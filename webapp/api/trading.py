"""
Trading API - Positions, Orders, Balance, Order Placement
"""
import os
import sys
import time
import json
import hmac
import hashlib
import logging
import aiohttp
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import db
from hl_adapter import HLAdapter

router = APIRouter()

# Import auth dependencies
from webapp.api.auth import get_current_user

# Bybit API URLs
BYBIT_DEMO_URL = "https://api-demo.bybit.com"
BYBIT_REAL_URL = "https://api.bybit.com"


class ClosePositionRequest(BaseModel):
    symbol: str
    exchange: str = "bybit"
    account_type: str = "demo"  # 'demo' or 'real'


class CloseAllRequest(BaseModel):
    exchange: str = "bybit"
    account_type: str = "demo"


class PlaceOrderRequest(BaseModel):
    symbol: str
    side: str  # 'buy' or 'sell' -> will be converted to 'Buy'/'Sell'
    order_type: Optional[str] = "market"  # 'market' or 'limit'
    type: Optional[str] = None  # Alias for order_type from frontend
    size: float
    price: Optional[float] = None
    leverage: int = 10
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    tp: Optional[float] = None  # Alias for take_profit from frontend
    sl: Optional[float] = None  # Alias for stop_loss from frontend
    exchange: str = "bybit"  # 'bybit' or 'hyperliquid'
    account_type: str = "demo"  # 'demo' or 'real'
    reduceOnly: bool = False
    postOnly: bool = False
    timeInForce: str = "GTC"
    
    def get_order_type(self) -> str:
        """Get order type from either order_type or type field"""
        return self.type or self.order_type or "market"
    
    def get_take_profit(self) -> Optional[float]:
        """Get take profit from either field"""
        return self.tp or self.take_profit
    
    def get_stop_loss(self) -> Optional[float]:
        """Get stop loss from either field"""
        return self.sl or self.stop_loss


class SetLeverageRequest(BaseModel):
    symbol: str
    leverage: int
    exchange: str = "bybit"
    account_type: str = "demo"


class CancelOrderRequest(BaseModel):
    symbol: str
    order_id: str
    exchange: str = "bybit"
    account_type: str = "demo"


# --- Bybit API Helper ---
def _sign_bybit(ts: str, api_key: str, api_secret: str, recv_window: str, body_json: str, query: str) -> str:
    """Sign Bybit request"""
    pre_sign = ts + api_key + recv_window + (query or body_json or "")
    return hmac.new(api_secret.encode(), pre_sign.encode(), hashlib.sha256).hexdigest()


async def bybit_request(
    user_id: int,
    method: str,
    path: str,
    params: dict = None,
    body: dict = None,
    account_type: str = "demo"
) -> dict:
    """Make authenticated Bybit API request"""
    creds = db.get_all_user_credentials(user_id)
    
    if account_type == "real":
        api_key = creds.get("real_api_key")
        api_secret = creds.get("real_api_secret")
        base_url = BYBIT_REAL_URL
    else:
        api_key = creds.get("demo_api_key")
        api_secret = creds.get("demo_api_secret")
        base_url = BYBIT_DEMO_URL
    
    if not api_key or not api_secret:
        raise HTTPException(status_code=400, detail=f"Bybit {account_type} API keys not configured")
    
    ts = str(int(time.time() * 1000))
    recv = "60000"
    
    # Build query string
    query = ""
    if params:
        from urllib.parse import quote
        query = "&".join(f"{quote(str(k), safe='~')}={quote(str(v), safe='~')}" for k, v in sorted(params.items()))
    
    body_json = json.dumps(body, separators=(",", ":")) if body else ""
    sign = _sign_bybit(ts, api_key, api_secret, recv, body_json, query)
    
    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": ts,
        "X-BAPI-RECV-WINDOW": recv,
        "X-BAPI-SIGN": sign,
        "X-BAPI-SIGN-TYPE": "2",
        "Content-Type": "application/json",
    }
    
    url = base_url + path + (f"?{query}" if method == "GET" and query else "")
    
    async with aiohttp.ClientSession() as session:
        if method == "GET":
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
        else:
            async with session.post(url, headers=headers, data=body_json) as resp:
                data = await resp.json()
    
    if data.get("retCode") != 0:
        raise HTTPException(status_code=400, detail=data.get("retMsg", "Bybit API error"))
    
    return data


@router.get("/balance")
async def get_balance(
    exchange: str = Query("bybit"),
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
):
    """Get account balance for specified exchange."""
    user_id = user["user_id"]
    
    if exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        if not hl_creds.get("hl_private_key"):
            return {"equity": 0, "available": 0, "unrealized_pnl": 0, "error": "HL not configured"}
        
        try:
            adapter = HLAdapter(
                private_key=hl_creds["hl_private_key"],
                testnet=hl_creds.get("hl_testnet", False)
            )
            result = await adapter.get_balance()
            await adapter.close()
            
            if result.get("success"):
                return result["data"]
            return {"equity": 0, "available": 0, "unrealized_pnl": 0, "error": result.get("error")}
        except Exception as e:
            return {"equity": 0, "available": 0, "unrealized_pnl": 0, "error": str(e)}
    
    else:
        # Bybit balance
        creds = db.get_all_user_credentials(user_id)
        
        # Use account_type from query param
        if account_type == "real":
            api_key = creds.get("real_api_key")
            api_secret = creds.get("real_api_secret")
            base_url = BYBIT_REAL_URL
        else:
            api_key = creds.get("demo_api_key")
            api_secret = creds.get("demo_api_secret")
            base_url = BYBIT_DEMO_URL
        
        if not api_key or not api_secret:
            return {"equity": 0, "available": 0, "unrealized_pnl": 0, "error": f"Bybit {account_type} not configured"}
        
        try:
            # Call Bybit wallet balance API
            data = await bybit_request(
                user_id, "GET", "/v5/account/wallet-balance",
                params={"accountType": "UNIFIED"},
                account_type=account_type
            )
            
            coins = data.get("result", {}).get("list", [{}])[0]
            return {
                "equity": float(coins.get("totalEquity", 0)),
                "available": float(coins.get("totalAvailableBalance", 0)),
                "unrealized_pnl": float(coins.get("totalPerpUPL", 0)),
                "margin_balance": float(coins.get("totalMarginBalance", 0)),
                "account_type": account_type
            }
        except HTTPException as e:
            return {"equity": 0, "available": 0, "unrealized_pnl": 0, "error": e.detail}
        except Exception as e:
            return {"equity": 0, "available": 0, "unrealized_pnl": 0, "error": str(e)}


@router.get("/positions")
async def get_positions(
    exchange: str = Query("bybit"),
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
) -> List[dict]:
    """Get open positions for specified exchange."""
    user_id = user["user_id"]
    
    if exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        if not hl_creds.get("hl_private_key"):
            return []
        
        try:
            adapter = HLAdapter(
                private_key=hl_creds["hl_private_key"],
                testnet=hl_creds.get("hl_testnet", False)
            )
            result = await adapter.fetch_positions()
            await adapter.close()
            
            positions = result.get("result", {}).get("list", [])
            return [
                {
                    "symbol": p.get("symbol"),
                    "side": p.get("side"),
                    "size": float(p.get("size", 0)),
                    "entry_price": float(p.get("entryPrice", 0)),
                    "mark_price": float(p.get("markPrice", 0)),
                    "pnl": float(p.get("unrealisedPnl", 0)),
                    "leverage": p.get("leverage"),
                    "exchange": "hyperliquid"
                }
                for p in positions if float(p.get("size", 0)) != 0
            ]
        except Exception as e:
            logger.error(f"HL positions error: {e}")
            return []
    
    else:
        # Bybit positions
        try:
            data = await bybit_request(
                user_id, "GET", "/v5/position/list",
                params={"category": "linear", "settleCoin": "USDT"},
                account_type=account_type
            )
            
            positions = data.get("result", {}).get("list", [])
            return [
                {
                    "symbol": p.get("symbol"),
                    "side": "long" if p.get("side") == "Buy" else "short",
                    "size": float(p.get("size", 0)),
                    "entry_price": float(p.get("avgPrice", 0)),
                    "mark_price": float(p.get("markPrice", 0)),
                    "liq_price": float(p.get("liqPrice", 0)) if p.get("liqPrice") else None,
                    "pnl": float(p.get("unrealisedPnl", 0)),
                    "roe": float(p.get("unrealisedPnl", 0)) / float(p.get("positionIM", 1)) * 100 if float(p.get("positionIM", 0)) > 0 else 0,
                    "leverage": p.get("leverage"),
                    "margin": float(p.get("positionIM", 0)),
                    "exchange": "bybit",
                    "account_type": account_type
                }
                for p in positions if float(p.get("size", 0)) != 0
            ]
        except Exception as e:
            logger.error(f"Bybit positions error: {e}")
            return []


@router.get("/orders")
async def get_orders(
    exchange: str = Query("bybit"),
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
) -> List[dict]:
    """Get open orders for specified exchange."""
    user_id = user["user_id"]
    
    if exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        if not hl_creds.get("hl_private_key"):
            return []
        
        try:
            adapter = HLAdapter(
                private_key=hl_creds["hl_private_key"],
                testnet=hl_creds.get("hl_testnet", False)
            )
            result = await adapter.fetch_open_orders()
            await adapter.close()
            
            if result.get("success"):
                return result["data"]
            return []
        except Exception as e:
            logger.error(f"HL orders error: {e}")
            return []
    
    else:
        # Bybit orders
        try:
            data = await bybit_request(
                user_id, "GET", "/v5/order/realtime",
                params={"category": "linear", "settleCoin": "USDT"},
                account_type=account_type
            )
            
            orders = data.get("result", {}).get("list", [])
            return [
                {
                    "id": o.get("orderId"),
                    "symbol": o.get("symbol"),
                    "side": o.get("side").lower() if o.get("side") else "buy",
                    "type": o.get("orderType", "Limit"),
                    "price": float(o.get("price", 0)),
                    "size": float(o.get("qty", 0)),
                    "filled": float(o.get("cumExecQty", 0)),
                    "remaining": float(o.get("leavesQty", 0)),
                    "status": o.get("orderStatus"),
                    "time": int(o.get("createdTime", 0)),
                    "reduceOnly": o.get("reduceOnly", False),
                    "exchange": "bybit",
                    "account_type": account_type
                }
                for o in orders if o.get("orderStatus") in ["New", "PartiallyFilled", "Untriggered"]
            ]
        except Exception as e:
            logger.error(f"Bybit orders error: {e}")
            return []


@router.post("/close")
async def close_position(
    req: ClosePositionRequest,
    user: dict = Depends(get_current_user)
):
    """Close a specific position."""
    user_id = user["user_id"]
    
    if req.exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        if not hl_creds.get("hl_private_key"):
            raise HTTPException(status_code=400, detail="HL not configured")
        
        try:
            adapter = HLAdapter(
                private_key=hl_creds["hl_private_key"],
                testnet=hl_creds.get("hl_testnet", False)
            )
            result = await adapter.close_position(req.symbol)
            await adapter.close()
            
            if result.get("retCode") == 0:
                return {"success": True, "message": f"Closed {req.symbol}"}
            return {"success": False, "error": result.get("retMsg")}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    else:
        # Bybit close position
        try:
            # First get the position to know side and size
            pos_data = await bybit_request(
                user_id, "GET", "/v5/position/list",
                params={"category": "linear", "symbol": req.symbol},
                account_type=req.account_type
            )
            
            positions = pos_data.get("result", {}).get("list", [])
            if not positions:
                raise HTTPException(status_code=404, detail="Position not found")
            
            pos = positions[0]
            size = float(pos.get("size", 0))
            if size == 0:
                raise HTTPException(status_code=404, detail="No open position")
            
            # Close position by placing opposite order
            close_side = "Sell" if pos.get("side") == "Buy" else "Buy"
            
            import uuid
            result = await bybit_request(
                user_id, "POST", "/v5/order/create",
                body={
                    "category": "linear",
                    "symbol": req.symbol,
                    "side": close_side,
                    "orderType": "Market",
                    "qty": str(size),
                    "reduceOnly": True,
                    "orderLinkId": f"close_{uuid.uuid4().hex[:12]}",
                    "timeInForce": "IOC"
                },
                account_type=req.account_type
            )
            
            return {
                "success": True,
                "message": f"Closed {req.symbol} position",
                "order_id": result.get("result", {}).get("orderId")
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/close-all")
async def close_all_positions(
    req: CloseAllRequest,
    user: dict = Depends(get_current_user)
):
    """Close all positions."""
    user_id = user["user_id"]
    
    if req.exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        if not hl_creds.get("hl_private_key"):
            raise HTTPException(status_code=400, detail="HL not configured")
        
        try:
            adapter = HLAdapter(
                private_key=hl_creds["hl_private_key"],
                testnet=hl_creds.get("hl_testnet", False)
            )
            
            # Get all positions
            positions_result = await adapter.fetch_positions()
            positions = positions_result.get("result", {}).get("list", [])
            
            closed = 0
            for pos in positions:
                symbol = pos.get("symbol")
                if symbol:
                    result = await adapter.close_position(symbol)
                    if result.get("retCode") == 0:
                        closed += 1
            
            await adapter.close()
            return {"success": True, "closed": closed}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    else:
        # Bybit close all positions
        import uuid
        try:
            # Get all open positions
            pos_data = await bybit_request(
                user_id, "GET", "/v5/position/list",
                params={"category": "linear", "settleCoin": "USDT"},
                account_type=req.account_type
            )
            
            positions = pos_data.get("result", {}).get("list", [])
            closed = 0
            errors = []
            
            for pos in positions:
                size = float(pos.get("size", 0))
                if size == 0:
                    continue
                    
                symbol = pos.get("symbol")
                close_side = "Sell" if pos.get("side") == "Buy" else "Buy"
                
                try:
                    await bybit_request(
                        user_id, "POST", "/v5/order/create",
                        body={
                            "category": "linear",
                            "symbol": symbol,
                            "side": close_side,
                            "orderType": "Market",
                            "qty": str(size),
                            "reduceOnly": True,
                            "orderLinkId": f"closeall_{uuid.uuid4().hex[:10]}",
                            "timeInForce": "IOC"
                        },
                        account_type=req.account_type
                    )
                    closed += 1
                except Exception as e:
                    errors.append(f"{symbol}: {str(e)}")
            
            return {
                "success": closed > 0 or len(positions) == 0,
                "closed": closed,
                "total": len([p for p in positions if float(p.get("size", 0)) > 0]),
                "errors": errors if errors else None
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/execution-history")
async def get_execution_history(
    exchange: str = Query("bybit"),
    account_type: str = Query("demo"),
    symbol: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    user: dict = Depends(get_current_user)
) -> dict:
    """Get execution history from exchange API (fills/executions)."""
    user_id = user["user_id"]
    
    if exchange == "hyperliquid":
        # HyperLiquid execution history
        hl_creds = db.get_hl_credentials(user_id)
        if not hl_creds.get("hl_private_key"):
            return {"executions": [], "error": "HL not configured"}
        
        try:
            adapter = HLAdapter(
                private_key=hl_creds["hl_private_key"],
                testnet=hl_creds.get("hl_testnet", False)
            )
            # Note: HyperLiquid fill history would require separate implementation
            await adapter.close()
            return {"executions": [], "message": "HL execution history not yet implemented"}
        except Exception as e:
            return {"executions": [], "error": str(e)}
    
    else:
        # Bybit execution history (closed PnL)
        try:
            params = {"category": "linear", "limit": str(limit)}
            if symbol:
                params["symbol"] = symbol
            
            data = await bybit_request(
                user_id, "GET", "/v5/position/closed-pnl",
                params=params,
                account_type=account_type
            )
            
            executions = []
            for e in data.get("result", {}).get("list", []):
                executions.append({
                    "id": e.get("orderId"),
                    "symbol": e.get("symbol"),
                    "side": e.get("side", "").lower(),
                    "entry_price": float(e.get("avgEntryPrice", 0)),
                    "exit_price": float(e.get("avgExitPrice", 0)),
                    "size": float(e.get("qty", 0)),
                    "pnl": float(e.get("closedPnl", 0)),
                    "leverage": e.get("leverage"),
                    "order_type": e.get("orderType"),
                    "exec_type": e.get("execType"),
                    "created_at": int(e.get("createdTime", 0)),
                    "updated_at": int(e.get("updatedTime", 0)),
                    "exchange": "bybit",
                    "account_type": account_type
                })
            
            return {"executions": executions, "total": len(executions)}
        except HTTPException as e:
            return {"executions": [], "error": e.detail}
        except Exception as e:
            return {"executions": [], "error": str(e)}


@router.get("/trades")
async def get_trades(
    exchange: str = Query("bybit"),
    limit: int = Query(20, ge=1, le=100),
    user: dict = Depends(get_current_user)
) -> dict:
    """Get recent trades history."""
    user_id = user["user_id"]
    import sqlite3
    
    try:
        conn = sqlite3.connect(db.DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get trades from trades table if exists
        cur.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='trades'
        """)
        if not cur.fetchone():
            # Create trades table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    symbol TEXT,
                    side TEXT,
                    entry_price REAL,
                    exit_price REAL,
                    size REAL,
                    pnl REAL,
                    pnl_percent REAL,
                    exchange TEXT DEFAULT 'bybit',
                    strategy TEXT,
                    created_at INTEGER,
                    closed_at INTEGER
                )
            """)
            conn.commit()
            conn.close()
            return {"trades": [], "total": 0}
        
        cur.execute("""
            SELECT * FROM trades 
            WHERE user_id = ? AND (exchange = ? OR ? = 'all')
            ORDER BY created_at DESC 
            LIMIT ?
        """, (user_id, exchange, exchange, limit))
        
        trades = []
        for row in cur.fetchall():
            trades.append({
                "id": row["id"],
                "symbol": row["symbol"],
                "side": row["side"],
                "entry_price": row["entry_price"],
                "exit_price": row["exit_price"],
                "size": row["size"],
                "pnl": row["pnl"],
                "pnl_percent": row["pnl_percent"],
                "exchange": row["exchange"],
                "strategy": row["strategy"],
                "created_at": row["created_at"],
                "closed_at": row["closed_at"]
            })
        
        # Get total count
        cur.execute("""
            SELECT COUNT(*) FROM trades 
            WHERE user_id = ? AND (exchange = ? OR ? = 'all')
        """, (user_id, exchange, exchange))
        total = cur.fetchone()[0]
        
        conn.close()
        return {"trades": trades, "total": total}
        
    except Exception as e:
        logger.error(f"Trades fetch error: {e}")
        return {"trades": [], "total": 0, "error": str(e)}


@router.get("/stats")
async def get_trading_stats(
    exchange: str = Query("bybit"),
    period: str = Query("all"),  # all, day, week, month
    user: dict = Depends(get_current_user)
) -> dict:
    """Get trading statistics."""
    user_id = user["user_id"]
    import sqlite3
    import time
    
    try:
        conn = sqlite3.connect(db.DB_FILE)
        cur = conn.cursor()
        
        # Period filter
        now = int(time.time())
        period_filter = ""
        if period == "day":
            period_filter = f" AND created_at >= {now - 86400}"
        elif period == "week":
            period_filter = f" AND created_at >= {now - 604800}"
        elif period == "month":
            period_filter = f" AND created_at >= {now - 2592000}"
        
        # Check if trades table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trades'")
        if not cur.fetchone():
            conn.close()
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "avg_pnl": 0,
                "best_trade": 0,
                "worst_trade": 0
            }
        
        # Total trades
        cur.execute(f"""
            SELECT COUNT(*) FROM trades 
            WHERE user_id = ? AND (exchange = ? OR ? = 'all') {period_filter}
        """, (user_id, exchange, exchange))
        total_trades = cur.fetchone()[0]
        
        if total_trades == 0:
            conn.close()
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "avg_pnl": 0,
                "best_trade": 0,
                "worst_trade": 0
            }
        
        # Win/loss counts
        cur.execute(f"""
            SELECT COUNT(*) FROM trades 
            WHERE user_id = ? AND (exchange = ? OR ? = 'all') AND pnl > 0 {period_filter}
        """, (user_id, exchange, exchange))
        winning = cur.fetchone()[0]
        
        cur.execute(f"""
            SELECT COUNT(*) FROM trades 
            WHERE user_id = ? AND (exchange = ? OR ? = 'all') AND pnl < 0 {period_filter}
        """, (user_id, exchange, exchange))
        losing = cur.fetchone()[0]
        
        # PnL stats
        cur.execute(f"""
            SELECT SUM(pnl), AVG(pnl), MAX(pnl), MIN(pnl) FROM trades 
            WHERE user_id = ? AND (exchange = ? OR ? = 'all') {period_filter}
        """, (user_id, exchange, exchange))
        row = cur.fetchone()
        total_pnl = row[0] or 0
        avg_pnl = row[1] or 0
        best_trade = row[2] or 0
        worst_trade = row[3] or 0
        
        conn.close()
        
        return {
            "total_trades": total_trades,
            "winning_trades": winning,
            "losing_trades": losing,
            "win_rate": (winning / total_trades * 100) if total_trades > 0 else 0,
            "total_pnl": round(total_pnl, 2),
            "avg_pnl": round(avg_pnl, 2),
            "best_trade": round(best_trade, 2),
            "worst_trade": round(worst_trade, 2)
        }
        
    except Exception as e:
        logger.error(f"Stats fetch error: {e}")
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "avg_pnl": 0,
            "best_trade": 0,
            "worst_trade": 0,
            "error": str(e)
        }

# ===================== ORDER PLACEMENT =====================

@router.post("/order")
async def place_order(
    req: PlaceOrderRequest,
    user: dict = Depends(get_current_user)
):
    """Place a new order on Bybit or HyperLiquid"""
    user_id = user["user_id"]
    
    # Normalize side
    side = "Buy" if req.side.lower() in ["buy", "long"] else "Sell"
    order_type_str = req.get_order_type()
    order_type = "Market" if order_type_str.lower() == "market" else "Limit"
    
    # Update req with resolved values
    req.take_profit = req.get_take_profit()
    req.stop_loss = req.get_stop_loss()
    
    if req.exchange == "hyperliquid":
        return await _place_order_hyperliquid(user_id, req, side, order_type)
    else:
        return await _place_order_bybit(user_id, req, side, order_type)


async def _place_order_bybit(user_id: int, req: PlaceOrderRequest, side: str, order_type: str):
    """Place order on Bybit"""
    import uuid
    
    # Set leverage first
    try:
        await bybit_request(
            user_id, "POST", "/v5/position/set-leverage",
            body={
                "category": "linear",
                "symbol": req.symbol,
                "buyLeverage": str(req.leverage),
                "sellLeverage": str(req.leverage)
            },
            account_type=req.account_type
        )
    except:
        pass  # Leverage might already be set
    
    # Build order body
    order_link_id = f"web_{uuid.uuid4().hex[:16]}"
    body = {
        "category": "linear",
        "symbol": req.symbol,
        "side": side,
        "orderType": order_type,
        "qty": str(req.size),
        "orderLinkId": order_link_id,
        "timeInForce": "IOC" if order_type == "Market" else "GTC"
    }
    
    if order_type == "Limit" and req.price:
        body["price"] = str(req.price)
    
    if req.take_profit:
        body["takeProfit"] = str(req.take_profit)
    if req.stop_loss:
        body["stopLoss"] = str(req.stop_loss)
    
    try:
        result = await bybit_request(
            user_id, "POST", "/v5/order/create",
            body=body,
            account_type=req.account_type
        )
        
        order_id = result.get("result", {}).get("orderId", "")
        return {
            "success": True,
            "order_id": order_id,
            "exchange": "bybit",
            "account_type": req.account_type,
            "symbol": req.symbol,
            "side": side,
            "size": req.size,
            "message": f"Order placed on Bybit ({req.account_type})"
        }
    except HTTPException as e:
        return {"success": False, "error": e.detail, "exchange": "bybit"}
    except Exception as e:
        return {"success": False, "error": str(e), "exchange": "bybit"}


async def _place_order_hyperliquid(user_id: int, req: PlaceOrderRequest, side: str, order_type: str):
    """Place order on HyperLiquid"""
    hl_creds = db.get_hl_credentials(user_id)
    if not hl_creds.get("hl_private_key"):
        return {"success": False, "error": "HyperLiquid not configured", "exchange": "hyperliquid"}
    
    # Use testnet from saved credentials (set via settings or account type switch)
    testnet = hl_creds.get("hl_testnet", False)
    
    try:
        adapter = HLAdapter(
            private_key=hl_creds["hl_private_key"],
            testnet=testnet,
            vault_address=hl_creds.get("hl_vault_address")
        )
        
        # Set leverage
        await adapter.set_leverage(req.symbol.replace("USDT", "").replace("USDC", ""), req.leverage)
        
        # Place order
        result = await adapter.place_order(
            symbol=req.symbol,
            side=side,
            qty=req.size,
            order_type=order_type,
            price=req.price if order_type == "Limit" else None
        )
        await adapter.close()
        
        if result.get("retCode") == 0:
            return {
                "success": True,
                "order_id": result.get("result", {}).get("orderId", ""),
                "exchange": "hyperliquid",
                "account_type": "testnet" if testnet else "mainnet",
                "symbol": req.symbol,
                "side": side,
                "size": req.size,
                "message": f"Order placed on HyperLiquid ({'testnet' if testnet else 'mainnet'})"
            }
        else:
            return {"success": False, "error": result.get("retMsg"), "exchange": "hyperliquid"}
    except Exception as e:
        return {"success": False, "error": str(e), "exchange": "hyperliquid"}


@router.post("/leverage")
async def set_leverage(
    req: SetLeverageRequest,
    user: dict = Depends(get_current_user)
):
    """Set leverage for a symbol"""
    user_id = user["user_id"]
    
    if req.exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        if not hl_creds.get("hl_private_key"):
            return {"success": False, "error": "HyperLiquid not configured"}
        
        try:
            adapter = HLAdapter(
                private_key=hl_creds["hl_private_key"],
                testnet=hl_creds.get("hl_testnet", False)
            )
            await adapter.set_leverage(req.symbol.replace("USDT", "").replace("USDC", ""), req.leverage)
            await adapter.close()
            return {"success": True, "leverage": req.leverage}
        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        # Bybit
        try:
            await bybit_request(
                user_id, "POST", "/v5/position/set-leverage",
                body={
                    "category": "linear",
                    "symbol": req.symbol,
                    "buyLeverage": str(req.leverage),
                    "sellLeverage": str(req.leverage)
                },
                account_type=req.account_type
            )
            return {"success": True, "leverage": req.leverage}
        except HTTPException as e:
            return {"success": False, "error": e.detail}


@router.delete("/order")
async def cancel_order(
    req: CancelOrderRequest,
    user: dict = Depends(get_current_user)
):
    """Cancel an open order"""
    user_id = user["user_id"]
    
    if req.exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        if not hl_creds.get("hl_private_key"):
            return {"success": False, "error": "HyperLiquid not configured"}
        
        try:
            adapter = HLAdapter(
                private_key=hl_creds["hl_private_key"],
                testnet=hl_creds.get("hl_testnet", False)
            )
            result = await adapter.cancel_order(req.symbol, req.order_id)
            await adapter.close()
            return {"success": result.get("retCode") == 0}
        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        try:
            await bybit_request(
                user_id, "POST", "/v5/order/cancel",
                body={
                    "category": "linear",
                    "symbol": req.symbol,
                    "orderId": req.order_id
                },
                account_type=req.account_type
            )
            return {"success": True}
        except HTTPException as e:
            return {"success": False, "error": e.detail}


@router.get("/account-info")
async def get_account_info(
    exchange: str = Query("bybit"),
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
):
    """Get account info (configured exchanges, modes, etc.)"""
    user_id = user["user_id"]
    
    creds = db.get_all_user_credentials(user_id)
    hl_creds = db.get_hl_credentials(user_id)
    
    return {
        "bybit": {
            "demo_configured": bool(creds.get("demo_api_key")),
            "real_configured": bool(creds.get("real_api_key")),
            "trading_mode": creds.get("trading_mode", "demo")
        },
        "hyperliquid": {
            "configured": bool(hl_creds.get("hl_private_key")),
            "testnet": hl_creds.get("hl_testnet", True),
            "wallet_address": hl_creds.get("hl_wallet_address", "")[:10] + "..." if hl_creds.get("hl_wallet_address") else None
        },
        "active_exchange": db.get_exchange_type(user_id)
    }


class ModifyTPSLRequest(BaseModel):
    """Request model for modifying TP/SL on an existing position"""
    symbol: str
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    tp_trigger_by: str = "LastPrice"  # MarkPrice, LastPrice, IndexPrice
    sl_trigger_by: str = "LastPrice"
    position_idx: int = 0  # 0 for one-way, 1 for Buy hedge, 2 for Sell hedge
    exchange: str = "bybit"
    account_type: str = "demo"


@router.post("/modify-tpsl")
async def modify_position_tpsl(
    req: ModifyTPSLRequest,
    user: dict = Depends(get_current_user)
):
    """Modify Take Profit / Stop Loss for an existing position"""
    user_id = user["user_id"]
    
    if req.exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        if not hl_creds.get("hl_private_key"):
            return {"success": False, "error": "HyperLiquid not configured"}
        
        try:
            adapter = HLAdapter(
                private_key=hl_creds["hl_private_key"],
                testnet=hl_creds.get("hl_testnet", False)
            )
            
            # Get position to determine side
            pos_result = await adapter.fetch_positions()
            positions = pos_result.get("result", {}).get("list", [])
            pos = next((p for p in positions if p.get("symbol") == req.symbol), None)
            
            if not pos:
                await adapter.close()
                return {"success": False, "error": "Position not found"}
            
            is_long = pos.get("side", "").lower() == "buy" or pos.get("side", "").lower() == "long"
            
            # Set TP/SL via trigger orders
            result = await adapter.set_tp_sl(
                symbol=req.symbol,
                is_long=is_long,
                take_profit=req.take_profit,
                stop_loss=req.stop_loss
            )
            await adapter.close()
            
            return {"success": True, "message": "TP/SL updated", "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    else:
        # Bybit TP/SL modification
        try:
            body = {
                "category": "linear",
                "symbol": req.symbol,
                "positionIdx": req.position_idx
            }
            
            if req.take_profit is not None:
                body["takeProfit"] = str(req.take_profit)
                body["tpTriggerBy"] = req.tp_trigger_by
            
            if req.stop_loss is not None:
                body["stopLoss"] = str(req.stop_loss)
                body["slTriggerBy"] = req.sl_trigger_by
            
            result = await bybit_request(
                user_id, "POST", "/v5/position/trading-stop",
                body=body,
                account_type=req.account_type
            )
            
            return {
                "success": True,
                "message": "TP/SL updated successfully",
                "take_profit": req.take_profit,
                "stop_loss": req.stop_loss
            }
        except HTTPException as e:
            return {"success": False, "error": e.detail}
        except Exception as e:
            return {"success": False, "error": str(e)}


@router.post("/cancel-all-orders")
async def cancel_all_orders(
    exchange: str = Query("bybit"),
    account_type: str = Query("demo"),
    symbol: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)
):
    """Cancel all open orders"""
    user_id = user["user_id"]
    
    if exchange == "hyperliquid":
        # HyperLiquid cancel all - would need implementation
        return {"success": False, "error": "Not implemented for HyperLiquid yet"}
    
    else:
        try:
            body = {"category": "linear"}
            if symbol:
                body["symbol"] = symbol
            else:
                body["settleCoin"] = "USDT"
            
            result = await bybit_request(
                user_id, "POST", "/v5/order/cancel-all",
                body=body,
                account_type=account_type
            )
            
            cancelled = result.get("result", {}).get("list", [])
            return {
                "success": True,
                "cancelled": len(cancelled),
                "orders": cancelled
            }
        except HTTPException as e:
            return {"success": False, "error": e.detail}
        except Exception as e:
            return {"success": False, "error": str(e)}


# ===================== ADVANCED TRADING ENDPOINTS =====================

class DCAOrderRequest(BaseModel):
    """Request model for DCA ladder orders"""
    symbol: str
    side: str  # 'buy' or 'sell'
    total_size: float
    order_count: int = 5  # Number of orders in ladder
    price_range_percent: float = 5.0  # Range from entry price
    distribution: str = "linear"  # linear, geometric, fibonacci, exponential
    entry_price: Optional[float] = None  # Current price if None
    exchange: str = "bybit"
    account_type: str = "demo"
    leverage: int = 10


class RiskCalcRequest(BaseModel):
    """Request model for position sizing calculation"""
    account_balance: float
    risk_percent: float = 1.0  # Risk 1% of account
    entry_price: float
    stop_loss_price: float
    take_profit_price: Optional[float] = None
    leverage: int = 10


class TrailingStopRequest(BaseModel):
    """Request model for trailing stop setup"""
    symbol: str
    position_side: str  # 'long' or 'short'
    trigger_percent: float = 1.0  # Activate after 1% profit
    trail_percent: float = 0.5  # Trail by 0.5%
    exchange: str = "bybit"
    account_type: str = "demo"


@router.post("/dca-ladder")
async def place_dca_ladder(
    req: DCAOrderRequest,
    user: dict = Depends(get_current_user)
):
    """Place a DCA ladder of orders"""
    user_id = user["user_id"]
    
    # Get current price if not provided
    if not req.entry_price:
        price_data = await _fetch_price(req.symbol)
        req.entry_price = price_data.get("price", 0)
        if not req.entry_price:
            return {"success": False, "error": "Could not fetch current price"}
    
    # Calculate distribution weights
    distributions = {
        "linear": lambda n: [1] * n,
        "geometric": lambda n: [1.5 ** i for i in range(n)],
        "fibonacci": lambda n: _fib_sequence(n),
        "exponential": lambda n: [2 ** i for i in range(n)]
    }
    
    weights = distributions.get(req.distribution, distributions["linear"])(req.order_count)
    total_weight = sum(weights)
    
    # Calculate order sizes and prices
    orders = []
    price_step = (req.entry_price * req.price_range_percent / 100) / (req.order_count - 1) if req.order_count > 1 else 0
    
    is_buy = req.side.lower() in ["buy", "long"]
    
    for i in range(req.order_count):
        size = req.total_size * (weights[i] / total_weight)
        price = req.entry_price - (price_step * i) if is_buy else req.entry_price + (price_step * i)
        orders.append({
            "index": i + 1,
            "price": round(price, 2),
            "size": round(size, 4)
        })
    
    # Set leverage first
    try:
        await _set_leverage_for_symbol(user_id, req.symbol, req.leverage, req.exchange, req.account_type)
    except:
        pass
    
    # Place orders
    results = []
    success_count = 0
    
    for order in orders:
        try:
            if req.exchange == "hyperliquid":
                result = await _place_single_order_hl(
                    user_id, req.symbol, req.side, "Limit", order["size"], order["price"], req.account_type
                )
            else:
                result = await _place_single_order_bybit(
                    user_id, req.symbol, req.side, "Limit", order["size"], order["price"], req.account_type
                )
            
            results.append({**order, "success": result.get("success", False), "order_id": result.get("order_id")})
            if result.get("success"):
                success_count += 1
        except Exception as e:
            results.append({**order, "success": False, "error": str(e)})
    
    return {
        "success": success_count > 0,
        "placed": success_count,
        "total": req.order_count,
        "average_entry": sum(o["price"] * o["size"] for o in orders) / req.total_size if req.total_size > 0 else 0,
        "orders": results,
        "message": f"Placed {success_count}/{req.order_count} DCA orders"
    }


def _fib_sequence(n: int) -> List[float]:
    """Generate Fibonacci sequence"""
    if n <= 0:
        return []
    if n == 1:
        return [1]
    fib = [1, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib[:n]


async def _set_leverage_for_symbol(user_id: int, symbol: str, leverage: int, exchange: str, account_type: str):
    """Set leverage for a symbol"""
    if exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        if hl_creds.get("hl_private_key"):
            adapter = HLAdapter(private_key=hl_creds["hl_private_key"], testnet=hl_creds.get("hl_testnet", False))
            await adapter.set_leverage(symbol.replace("USDT", "").replace("USDC", ""), leverage)
            await adapter.close()
    else:
        await bybit_request(
            user_id, "POST", "/v5/position/set-leverage",
            body={"category": "linear", "symbol": symbol, "buyLeverage": str(leverage), "sellLeverage": str(leverage)},
            account_type=account_type
        )


async def _place_single_order_bybit(user_id: int, symbol: str, side: str, order_type: str, size: float, price: float, account_type: str):
    """Place single order on Bybit"""
    import uuid
    side_formatted = "Buy" if side.lower() in ["buy", "long"] else "Sell"
    
    body = {
        "category": "linear",
        "symbol": symbol,
        "side": side_formatted,
        "orderType": order_type,
        "qty": str(size),
        "price": str(price),
        "orderLinkId": f"dca_{uuid.uuid4().hex[:12]}",
        "timeInForce": "GTC"
    }
    
    result = await bybit_request(user_id, "POST", "/v5/order/create", body=body, account_type=account_type)
    return {"success": True, "order_id": result.get("result", {}).get("orderId")}


async def _place_single_order_hl(user_id: int, symbol: str, side: str, order_type: str, size: float, price: float, account_type: str):
    """Place single order on HyperLiquid"""
    hl_creds = db.get_hl_credentials(user_id)
    if not hl_creds.get("hl_private_key"):
        return {"success": False, "error": "HL not configured"}
    
    side_formatted = "Buy" if side.lower() in ["buy", "long"] else "Sell"
    adapter = HLAdapter(private_key=hl_creds["hl_private_key"], testnet=hl_creds.get("hl_testnet", False))
    result = await adapter.place_order(symbol=symbol, side=side_formatted, qty=size, order_type=order_type, price=price)
    await adapter.close()
    
    return {"success": result.get("retCode") == 0, "order_id": result.get("result", {}).get("orderId")}


@router.post("/calculate-position")
async def calculate_position_size(req: RiskCalcRequest):
    """Calculate optimal position size based on risk parameters"""
    
    # Calculate price difference for stop loss
    price_diff = abs(req.entry_price - req.stop_loss_price)
    stop_percent = (price_diff / req.entry_price) * 100
    
    if stop_percent <= 0:
        return {"error": "Invalid stop loss price"}
    
    # Risk amount in account currency
    risk_amount = req.account_balance * (req.risk_percent / 100)
    
    # Position value based on risk
    position_value = (risk_amount / stop_percent) * 100
    position_size = position_value / req.entry_price
    
    # With leverage
    margin_required = position_value / req.leverage
    max_position_value = req.account_balance * req.leverage
    max_position_size = max_position_value / req.entry_price
    
    # Limit to max if over-leveraged
    if position_value > max_position_value:
        position_value = max_position_value
        position_size = max_position_size
        margin_required = req.account_balance
    
    # Liquidation price (assuming 90% margin maintenance)
    is_long = req.stop_loss_price < req.entry_price
    liq_price = req.entry_price * (1 - 0.9 / req.leverage) if is_long else req.entry_price * (1 + 0.9 / req.leverage)
    
    result = {
        "position_size": round(position_size, 6),
        "position_value": round(position_value, 2),
        "margin_required": round(margin_required, 2),
        "risk_amount": round(risk_amount, 2),
        "stop_percent": round(stop_percent, 2),
        "liquidation_price": round(liq_price, 2),
        "max_position_size": round(max_position_size, 6),
        "side": "long" if is_long else "short"
    }
    
    # Calculate risk/reward if take profit provided
    if req.take_profit_price:
        reward_diff = abs(req.take_profit_price - req.entry_price)
        risk_reward_ratio = reward_diff / price_diff if price_diff > 0 else 0
        potential_profit = risk_amount * risk_reward_ratio
        
        result["risk_reward_ratio"] = round(risk_reward_ratio, 2)
        result["potential_profit"] = round(potential_profit, 2)
        result["expected_value"] = round(potential_profit - risk_amount, 2)  # Simplified
    
    return result


@router.get("/symbol-info/{symbol}")
async def get_symbol_info(symbol: str):
    """Get symbol trading info (tick size, lot size, etc.)"""
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.bybit.com/v5/market/instruments-info?category=linear&symbol={symbol}"
            async with session.get(url) as resp:
                data = await resp.json()
                
                if data.get("retCode") == 0:
                    instruments = data.get("result", {}).get("list", [])
                    if instruments:
                        inst = instruments[0]
                        lot_size = inst.get("lotSizeFilter", {})
                        price_filter = inst.get("priceFilter", {})
                        leverage_filter = inst.get("leverageFilter", {})
                        
                        return {
                            "symbol": symbol,
                            "base_coin": inst.get("baseCoin"),
                            "quote_coin": inst.get("quoteCoin"),
                            "min_qty": float(lot_size.get("minOrderQty", 0)),
                            "max_qty": float(lot_size.get("maxOrderQty", 0)),
                            "qty_step": float(lot_size.get("qtyStep", 0)),
                            "min_price": float(price_filter.get("minPrice", 0)),
                            "max_price": float(price_filter.get("maxPrice", 0)),
                            "tick_size": float(price_filter.get("tickSize", 0)),
                            "min_leverage": float(leverage_filter.get("minLeverage", 1)),
                            "max_leverage": float(leverage_filter.get("maxLeverage", 100)),
                            "funding_interval": inst.get("fundingInterval")
                        }
    except Exception as e:
        return {"error": str(e)}
    
    return {"error": "Symbol not found"}


async def _fetch_price(symbol: str) -> dict:
    """Fetch current price for symbol"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
            async with session.get(url) as resp:
                data = await resp.json()
                if data.get("retCode") == 0:
                    ticker = data.get("result", {}).get("list", [{}])[0]
                    return {
                        "price": float(ticker.get("lastPrice", 0)),
                        "change24h": float(ticker.get("price24hPcnt", 0)) * 100,
                        "high24h": float(ticker.get("highPrice24h", 0)),
                        "low24h": float(ticker.get("lowPrice24h", 0)),
                        "volume24h": float(ticker.get("turnover24h", 0)),
                    }
    except:
        pass
    return {"price": 0}


@router.get("/orderbook/{symbol}")
async def get_orderbook(symbol: str, depth: int = Query(25, ge=5, le=200)):
    """Get orderbook snapshot for symbol"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.bybit.com/v5/market/orderbook?category=linear&symbol={symbol}&limit={depth}"
            async with session.get(url) as resp:
                data = await resp.json()
                
                if data.get("retCode") == 0:
                    result = data.get("result", {})
                    asks = [[float(p), float(s)] for p, s in result.get("a", [])]
                    bids = [[float(p), float(s)] for p, s in result.get("b", [])]
                    
                    # Calculate totals and depth percentages
                    ask_total, bid_total = 0, 0
                    for a in asks:
                        ask_total += a[1]
                        a.append(ask_total)
                    for b in bids:
                        bid_total += b[1]
                        b.append(bid_total)
                    
                    max_total = max(ask_total, bid_total) if ask_total > 0 or bid_total > 0 else 1
                    for a in asks:
                        a.append(a[2] / max_total * 100)  # depth percent
                    for b in bids:
                        b.append(b[2] / max_total * 100)
                    
                    # Calculate spread
                    spread = asks[0][0] - bids[0][0] if asks and bids else 0
                    spread_pct = (spread / asks[0][0] * 100) if asks and asks[0][0] > 0 else 0
                    
                    # Calculate bid/ask imbalance
                    bid_vol_10 = sum(b[1] for b in bids[:10])
                    ask_vol_10 = sum(a[1] for a in asks[:10])
                    imbalance = ((bid_vol_10 - ask_vol_10) / (bid_vol_10 + ask_vol_10) * 100) if (bid_vol_10 + ask_vol_10) > 0 else 0
                    
                    return {
                        "symbol": symbol,
                        "asks": asks,
                        "bids": bids,
                        "spread": round(spread, 2),
                        "spread_percent": round(spread_pct, 4),
                        "imbalance": round(imbalance, 1),
                        "timestamp": result.get("ts", 0)
                    }
    except Exception as e:
        return {"error": str(e)}
    
    return {"error": "Failed to fetch orderbook"}


@router.get("/recent-trades/{symbol}")
async def get_recent_trades(symbol: str, limit: int = Query(50, ge=10, le=500)):
    """Get recent trades for symbol"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.bybit.com/v5/market/recent-trade?category=linear&symbol={symbol}&limit={limit}"
            async with session.get(url) as resp:
                data = await resp.json()
                
                if data.get("retCode") == 0:
                    trades = []
                    for t in data.get("result", {}).get("list", []):
                        trades.append({
                            "price": float(t.get("price", 0)),
                            "size": float(t.get("size", 0)),
                            "side": t.get("side"),
                            "time": int(t.get("time", 0)),
                            "is_buyer_maker": t.get("side") == "Sell"
                        })
                    return {"symbol": symbol, "trades": trades}
    except Exception as e:
        return {"error": str(e)}
    
    return {"error": "Failed to fetch trades"}


@router.get("/symbols")
async def search_symbols(
    query: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(50, ge=1, le=200)
):
    """Search and list available trading symbols with live prices"""
    try:
        async with aiohttp.ClientSession() as session:
            # Get tickers with prices
            url = "https://api.bybit.com/v5/market/tickers?category=linear"
            async with session.get(url) as resp:
                data = await resp.json()
                
                if data.get("retCode") != 0:
                    return {"symbols": [], "error": data.get("retMsg")}
                
                tickers = data.get("result", {}).get("list", [])
                
                # Filter and format
                symbols = []
                for t in tickers:
                    symbol = t.get("symbol", "")
                    
                    # Skip non-USDT pairs and illiquid
                    if not symbol.endswith("USDT"):
                        continue
                    
                    # Filter by query if provided
                    if query:
                        base = symbol.replace("USDT", "").lower()
                        if query.lower() not in base and query.lower() not in symbol.lower():
                            continue
                    
                    price = float(t.get("lastPrice", 0))
                    change = float(t.get("price24hPcnt", 0)) * 100
                    volume = float(t.get("turnover24h", 0))
                    
                    symbols.append({
                        "symbol": symbol,
                        "base": symbol.replace("USDT", ""),
                        "price": price,
                        "change_24h": round(change, 2),
                        "high_24h": float(t.get("highPrice24h", 0)),
                        "low_24h": float(t.get("lowPrice24h", 0)),
                        "volume_24h": volume,
                        "volume_formatted": _format_volume(volume),
                        "funding_rate": float(t.get("fundingRate", 0)) * 100 if t.get("fundingRate") else None,
                        "open_interest": float(t.get("openInterest", 0)) if t.get("openInterest") else None
                    })
                
                # Sort by volume (most liquid first)
                symbols.sort(key=lambda x: x["volume_24h"], reverse=True)
                
                return {
                    "symbols": symbols[:limit],
                    "total": len(symbols)
                }
                
    except Exception as e:
        return {"symbols": [], "error": str(e)}


def _format_volume(volume: float) -> str:
    """Format volume for display"""
    if volume >= 1_000_000_000:
        return f"${volume / 1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        return f"${volume / 1_000_000:.2f}M"
    elif volume >= 1_000:
        return f"${volume / 1_000:.2f}K"
    return f"${volume:.2f}"


@router.get("/funding-rates")
async def get_funding_rates(limit: int = Query(30, ge=1, le=100)):
    """Get funding rates for top symbols"""
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.bybit.com/v5/market/tickers?category=linear"
            async with session.get(url) as resp:
                data = await resp.json()
                
                if data.get("retCode") != 0:
                    return {"rates": [], "error": data.get("retMsg")}
                
                tickers = data.get("result", {}).get("list", [])
                
                rates = []
                for t in tickers:
                    symbol = t.get("symbol", "")
                    if not symbol.endswith("USDT"):
                        continue
                    
                    funding = t.get("fundingRate")
                    if funding is None:
                        continue
                    
                    rates.append({
                        "symbol": symbol,
                        "funding_rate": float(funding) * 100,
                        "price": float(t.get("lastPrice", 0)),
                        "open_interest": float(t.get("openInterest", 0)) if t.get("openInterest") else 0
                    })
                
                # Sort by absolute funding rate (highest first)
                rates.sort(key=lambda x: abs(x["funding_rate"]), reverse=True)
                
                return {"rates": rates[:limit]}
                
    except Exception as e:
        return {"rates": [], "error": str(e)}


@router.get("/market-overview")
async def get_market_overview():
    """Get market overview with top gainers/losers and volume leaders"""
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.bybit.com/v5/market/tickers?category=linear"
            async with session.get(url) as resp:
                data = await resp.json()
                
                if data.get("retCode") != 0:
                    return {"error": data.get("retMsg")}
                
                tickers = data.get("result", {}).get("list", [])
                
                # Filter USDT pairs only
                usdt_tickers = [
                    t for t in tickers 
                    if t.get("symbol", "").endswith("USDT")
                ]
                
                # Process tickers
                processed = []
                for t in usdt_tickers:
                    change = float(t.get("price24hPcnt", 0)) * 100
                    volume = float(t.get("turnover24h", 0))
                    
                    processed.append({
                        "symbol": t.get("symbol"),
                        "price": float(t.get("lastPrice", 0)),
                        "change_24h": round(change, 2),
                        "volume_24h": volume
                    })
                
                # Sort for different categories
                gainers = sorted(processed, key=lambda x: x["change_24h"], reverse=True)[:10]
                losers = sorted(processed, key=lambda x: x["change_24h"])[:10]
                volume_leaders = sorted(processed, key=lambda x: x["volume_24h"], reverse=True)[:10]
                
                # Calculate market sentiment
                positive = sum(1 for t in processed if t["change_24h"] > 0)
                negative = sum(1 for t in processed if t["change_24h"] < 0)
                total = len(processed)
                
                return {
                    "gainers": gainers,
                    "losers": losers,
                    "volume_leaders": volume_leaders,
                    "sentiment": {
                        "positive_count": positive,
                        "negative_count": negative,
                        "total": total,
                        "bullish_percent": round(positive / total * 100, 1) if total > 0 else 0
                    },
                    "timestamp": int(time.time() * 1000)
                }
                
    except Exception as e:
        return {"error": str(e)}