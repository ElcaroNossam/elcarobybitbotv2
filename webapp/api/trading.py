"""
Trading API - Positions, Orders, Balance
"""
import os
import sys
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import db
from hl_adapter import HLAdapter

router = APIRouter()

# Import auth dependencies
from webapp.api.auth import get_current_user


class ClosePositionRequest(BaseModel):
    symbol: str
    exchange: str = "bybit"


class CloseAllRequest(BaseModel):
    exchange: str = "bybit"


@router.get("/balance")
async def get_balance(
    exchange: str = Query("bybit"),
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
        trading_mode = creds.get("trading_mode", "demo")
        
        if trading_mode == "demo":
            api_key = creds.get("demo_api_key")
            api_secret = creds.get("demo_api_secret")
        else:
            api_key = creds.get("real_api_key")
            api_secret = creds.get("real_api_secret")
        
        if not api_key or not api_secret:
            return {"equity": 0, "available": 0, "unrealized_pnl": 0, "error": "Bybit not configured"}
        
        # TODO: Call Bybit API
        return {
            "equity": 0,
            "available": 0, 
            "unrealized_pnl": 0,
            "note": "Bybit balance fetch via WebApp coming soon"
        }


@router.get("/positions")
async def get_positions(
    exchange: str = Query("bybit"),
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
                }
                for p in positions
            ]
        except Exception as e:
            print(f"HL positions error: {e}")
            return []
    
    else:
        # Bybit positions - TODO
        return []


@router.get("/orders")
async def get_orders(
    exchange: str = Query("bybit"),
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
            print(f"HL orders error: {e}")
            return []
    
    else:
        # Bybit orders - TODO
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
        # Bybit close - TODO
        raise HTTPException(status_code=501, detail="Bybit close not implemented yet")


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
        # Bybit close all - TODO
        raise HTTPException(status_code=501, detail="Bybit close-all not implemented yet")


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
        print(f"Trades fetch error: {e}")
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
        print(f"Stats fetch error: {e}")
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
