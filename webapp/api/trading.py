"""
Trading API - Positions, Orders, Balance, Order Placement
"""
import os
import sys
import time
import json
import hmac
import asyncio
import hashlib
import logging
import aiohttp
from typing import Optional, List, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import db
from hl_adapter import HLAdapter

# Bug #3 Fix: Use centralized account utilities
from core.account_utils import (
    normalize_account_type as _normalize_both_account_type,
    get_hl_credentials_for_account as _get_hl_credentials_for_account
)

# CROSS-PLATFORM: Import sync service for activity logging
try:
    from services.sync_service import sync_service
    SYNC_SERVICE_AVAILABLE = True
except ImportError:
    sync_service = None
    SYNC_SERVICE_AVAILABLE = False

# NEW: Use services integration layer
get_positions_service: Any = None
get_balance_service: Any = None
place_order_service: Any = None
close_position_service: Any = None
set_leverage_service: Any = None
try:
    from webapp.services_integration import (
        get_positions_service, get_balance_service,
        place_order_service, close_position_service, set_leverage_service
    )
    SERVICES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Services integration not available: {e}")
    SERVICES_AVAILABLE = False

# Import position calculator
position_calculator: Any = None
try:
    from webapp.services.position_calculator import position_calculator
    POSITION_CALCULATOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Position calculator not available: {e}")
    POSITION_CALCULATOR_AVAILABLE = False

router = APIRouter()

# Import auth dependencies
from webapp.api.auth import get_current_user

# Bybit API URLs
BYBIT_DEMO_URL = "https://api-demo.bybit.com"
BYBIT_REAL_URL = "https://api.bybit.com"


# ==================== LICENSE CHECK DEPENDENCY ====================

async def require_trading_license(user: dict = Depends(get_current_user)):
    """
    Check if user has a valid license for trading features.
    Returns user if has license, raises HTTPException if not.
    
    Free users can:
    - View balance, positions, orders
    - Access stats and market data
    - View screener and signals
    
    Trading requires at least basic license:
    - Place orders, close positions
    - Set leverage, DCA operations
    - Modify TP/SL
    """
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Check is_allowed flag (basic access)
    is_allowed = user.get("is_allowed", False)
    if is_allowed:
        return user
    
    # Check license_type in database
    try:
        license_type = db.get_user_field(user_id, "license_type") or "free"
        license_expires = db.get_user_field(user_id, "license_expires")
        
        # Free users can't trade
        if license_type == "free":
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "LICENSE_REQUIRED",
                    "message": "Trading features require a subscription",
                    "upgrade_url": "/subscription"
                }
            )
        
        # Check if license expired
        if license_expires:
            from datetime import datetime
            try:
                expires_at = datetime.fromisoformat(license_expires.replace("Z", "+00:00"))
                if datetime.utcnow() > expires_at:
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "code": "LICENSE_EXPIRED",
                            "message": "Your subscription has expired",
                            "upgrade_url": "/subscription"
                        }
                    )
            except (ValueError, TypeError):
                pass
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"License check error: {e}")
        # Allow on error to not block trading
        return user


# ==================== POSITION CALCULATOR MODELS ====================

class CalculatePositionRequest(BaseModel):
    """Request for position size calculation"""
    account_balance: float
    entry_price: float
    stop_loss_price: Optional[float] = None
    stop_loss_percent: Optional[float] = None
    risk_percent: float = 1.0
    leverage: int = 10
    side: str = "Buy"  # 'Buy' or 'Sell'
    take_profit_price: Optional[float] = None
    take_profit_percent: Optional[float] = None
    
    # Exchange limits (optional)
    min_order_size: Optional[float] = None
    max_order_size: Optional[float] = None
    qty_step: Optional[float] = None


class PositionCalculationResponse(BaseModel):
    """Response from position calculator"""
    position_size: float
    position_value_usd: float
    margin_required: float
    risk_amount_usd: float
    stop_loss_price: float
    stop_loss_percent: float
    take_profit_price: Optional[float] = None
    take_profit_percent: Optional[float] = None
    potential_profit_usd: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    max_loss_usd: float
    margin_ratio: float
    is_valid: bool = True
    warnings: List[str] = []


# ==================== OTHER MODELS ====================

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
    strategy: Optional[str] = None  # Strategy name (oi, scalper, fibonacci, etc.)
    use_atr: bool = False  # Use ATR trailing stop
    atr_periods: int = 14
    atr_multiplier_sl: float = 1.5
    atr_trigger_pct: float = 2.0
    
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
    params: Optional[dict] = None,
    body: Optional[dict] = None,
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
    
    # Normalize 'both' -> 'demo'/'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange) or account_type or "demo"
    
    # NEW: Use services integration if available
    if SERVICES_AVAILABLE:
        try:
            result = await get_balance_service(user_id, exchange, account_type)
            if result.get("success"):
                data = result["data"]
                # Add Android compatibility aliases if missing
                if "total_equity" not in data:
                    data["total_equity"] = data.get("equity", 0)
                if "available_balance" not in data:
                    data["available_balance"] = data.get("available", 0)
                return data
            return {"equity": 0, "available": 0, "unrealized_pnl": 0, "total_equity": 0, "available_balance": 0, "error": result.get("error")}
        except Exception as e:
            logger.error(f"Services balance error: {e}")
            # Fall through to old code
    
    # OLD CODE (fallback)
    if exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        
        # Determine which private key to use based on account_type
        private_key = None
        is_testnet = False
        
        if account_type in ("testnet", "demo"):
            # Try testnet key first, then legacy
            private_key = hl_creds.get("hl_testnet_private_key")
            if not private_key and hl_creds.get("hl_testnet"):
                private_key = hl_creds.get("hl_private_key")
            is_testnet = True
        else:  # mainnet/real
            # Try mainnet key first, then legacy
            private_key = hl_creds.get("hl_mainnet_private_key")
            if not private_key and not hl_creds.get("hl_testnet"):
                private_key = hl_creds.get("hl_private_key")
            is_testnet = False
        
        if not private_key:
            return {"equity": 0, "available": 0, "unrealized_pnl": 0, "total_equity": 0, "available_balance": 0, "error": f"HL {account_type} not configured"}
        
        # Get wallet address to skip auto-discovery (avoids rate limits)
        wallet_address = None
        if is_testnet:
            wallet_address = hl_creds.get("hl_testnet_wallet_address") or hl_creds.get("hl_wallet_address")
        else:
            wallet_address = hl_creds.get("hl_mainnet_wallet_address") or hl_creds.get("hl_wallet_address")
        
        adapter = None
        try:
            adapter = HLAdapter(
                private_key=private_key,
                testnet=is_testnet
            )
            await adapter.initialize()  # Auto-discover main wallet
            result = await adapter.get_balance()
            
            if result.get("success"):
                data = result["data"]
                # Add Android compatibility aliases
                data["total_equity"] = data.get("equity", 0)
                data["available_balance"] = data.get("available", 0)
                if "currency" not in data:
                    data["currency"] = "USDC"  # HL uses USDC
                return data
            return {"equity": 0, "available": 0, "unrealized_pnl": 0, "total_equity": 0, "available_balance": 0, "error": result.get("error")}
        except Exception as e:
            return {"equity": 0, "available": 0, "unrealized_pnl": 0, "total_equity": 0, "available_balance": 0, "error": str(e)}
        finally:
            if adapter:
                await adapter.close()
    
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
            return {"equity": 0, "available": 0, "unrealized_pnl": 0, "total_equity": 0, "available_balance": 0, "error": f"Bybit {account_type} not configured"}
        
        try:
            # Call Bybit wallet balance API
            data = await bybit_request(
                user_id, "GET", "/v5/account/wallet-balance",
                params={"accountType": "UNIFIED"},
                account_type=account_type
            )
            
            coins = data.get("result", {}).get("list", [{}])[0]
            
            # Calculate position margin (used margin for positions)
            equity = float(coins.get("totalEquity", 0))
            available = float(coins.get("totalAvailableBalance", 0))
            position_im = float(coins.get("totalPositionIM", 0))  # Initial Margin for positions
            unrealized_pnl = float(coins.get("totalPerpUPL", 0))
            margin_balance = float(coins.get("totalMarginBalance", 0))
            
            return {
                # Primary fields (iOS uses these)
                "equity": equity,
                "available": available,
                "unrealized_pnl": unrealized_pnl,
                # Android compatibility aliases
                "total_equity": equity,
                "available_balance": available,
                # Additional fields
                "margin_balance": margin_balance,
                "margin_used": margin_balance,
                "position_margin": position_im if position_im > 0 else (equity - available),  # Fallback
                "account_type": account_type,
                "currency": "USDT"
            }
        except HTTPException as e:
            return {"equity": 0, "available": 0, "unrealized_pnl": 0, "total_equity": 0, "available_balance": 0, "error": e.detail}
        except Exception as e:
            return {"equity": 0, "available": 0, "unrealized_pnl": 0, "total_equity": 0, "available_balance": 0, "error": str(e)}


@router.get("/balance/spot")
async def get_spot_balance(
    account_type: str = Query("mainnet"),
    user: dict = Depends(get_current_user)
):
    """Get HyperLiquid SPOT balance (separate from Perp)."""
    user_id = user["user_id"]
    
    hl_creds = db.get_hl_credentials(user_id)
    
    # Determine which private key to use based on account_type
    private_key = None
    is_testnet = False
    wallet_address = None
    
    if account_type in ("testnet", "demo"):
        private_key = hl_creds.get("hl_testnet_private_key") or hl_creds.get("hl_private_key")
        wallet_address = hl_creds.get("hl_testnet_wallet_address") or hl_creds.get("hl_wallet_address")
        is_testnet = True
    else:  # mainnet/real
        private_key = hl_creds.get("hl_mainnet_private_key") or hl_creds.get("hl_private_key")
        wallet_address = hl_creds.get("hl_mainnet_wallet_address") or hl_creds.get("hl_wallet_address")
        is_testnet = False
    
    if not private_key:
        return {"tokens": [], "total_usd_value": 0, "num_tokens": 0, "error": f"HL {account_type} not configured"}
    
    adapter = None
    try:
        adapter = HLAdapter(
            private_key=private_key,
            testnet=is_testnet
        )
        await adapter.initialize()  # Auto-discover main wallet
        result = await adapter.get_spot_balance()
        
        if result.get("success"):
            return result["data"]
        return {"tokens": [], "total_usd_value": 0, "num_tokens": 0, "error": result.get("error")}
    except Exception as e:
        return {"tokens": [], "total_usd_value": 0, "num_tokens": 0, "error": str(e)}
    finally:
        if adapter:
            await adapter.close()


@router.get("/positions")
async def get_positions(
    exchange: str = Query("bybit"),
    account_type: str = Query("demo"),
    env: Optional[str] = Query(None, description="Unified env: 'paper' or 'live'. If provided, takes precedence over account_type"),
    user: dict = Depends(get_current_user)
) -> List[dict]:
    """Get open positions for specified exchange.
    
    Args:
        exchange: 'bybit' or 'hyperliquid'
        account_type: 'demo', 'real', 'testnet', 'mainnet' (legacy)
        env: 'paper' or 'live' (unified Target model, takes precedence)
    """
    user_id = user["user_id"]
    
    # Normalize env to account_type for backward compatibility
    if env:
        if env == "paper":
            account_type = "demo" if exchange == "bybit" else "testnet"
        elif env == "live":
            account_type = "real" if exchange == "bybit" else "mainnet"
    
    # Normalize 'both' -> 'demo'/'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange) or account_type or "demo"
    
    # NEW: Use services integration if available
    if SERVICES_AVAILABLE:
        try:
            result = await get_positions_service(user_id, exchange, account_type)
            if result.get("success"):
                return result["data"]
            return []
        except Exception as e:
            logger.error(f"Services positions error: {e}")
            # Fall through to old code
    
    # OLD CODE (fallback)
    if exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        account_type = _normalize_both_account_type(account_type, "hyperliquid") or "testnet"
        private_key, is_testnet, wallet_address = _get_hl_credentials_for_account(hl_creds, account_type)
        
        if not private_key:
            return []
        
        adapter = None
        try:
            adapter = HLAdapter(
                private_key=private_key,
                testnet=is_testnet
            )
            await adapter.initialize()  # Auto-discover main wallet
            result = await adapter.fetch_positions()
            
            positions = result.get("result", {}).get("list", [])
            
            # Determine env based on is_testnet
            hl_env = "paper" if is_testnet else "live"
            hl_account_type = "testnet" if is_testnet else "mainnet"
            
            return [
                {
                    "symbol": p.get("symbol"),
                    "side": p.get("side"),
                    "size": float(p.get("size", 0)),
                    "entry_price": float(p.get("entryPrice", 0)),
                    "mark_price": float(p.get("markPrice", 0)),
                    "pnl": float(p.get("unrealisedPnl", 0)),
                    "leverage": p.get("leverage"),
                    "exchange": "hyperliquid",
                    "account_type": hl_account_type,
                    "env": hl_env
                }
                for p in positions if float(p.get("size", 0)) != 0
            ]
        except Exception as e:
            logger.error(f"HL positions error: {e}")
            return []
        finally:
            if adapter:
                await adapter.close()
    
    else:
        # Bybit positions
        try:
            data = await bybit_request(
                user_id, "GET", "/v5/position/list",
                params={"category": "linear", "settleCoin": "USDT"},
                account_type=account_type
            )
            
            positions = data.get("result", {}).get("list", [])
            
            # Get active positions from our DB for strategy info
            # Filter by account_type and exchange for accurate matching
            db_positions = {}
            try:
                active_pos = db.get_active_positions(
                    user_id, 
                    account_type=account_type, 
                    exchange=exchange,
                    env=env
                )
                for ap in active_pos:
                    sym = ap.get("symbol", "")
                    db_positions[sym] = ap
            except Exception:
                pass
            
            result_positions = []
            for p in positions:
                if float(p.get("size", 0)) == 0:
                    continue
                    
                symbol = p.get("symbol")
                db_pos = db_positions.get(symbol, {})
                
                # Get TP/SL from Bybit position if set
                tp_price = None
                sl_price = None
                try:
                    tp_price = float(p.get("takeProfit")) if p.get("takeProfit") else None
                    sl_price = float(p.get("stopLoss")) if p.get("stopLoss") else None
                except (TypeError, ValueError):
                    pass
                
                # Fallback to DB values
                if not tp_price:
                    tp_price = db_pos.get("tp_price")
                if not sl_price:
                    sl_price = db_pos.get("sl_price")
                
                result_positions.append({
                    "symbol": symbol,
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
                    "account_type": account_type,
                    "env": env or ("paper" if account_type in ("demo", "testnet") else "live"),
                    # Additional info from our DB
                    "strategy": db_pos.get("strategy"),
                    "tp_price": tp_price,
                    "sl_price": sl_price,
                    "use_atr": bool(db_pos.get("use_atr", 0)),
                    "atr_activated": bool(db_pos.get("atr_activated", 0)),
                })
            
            return result_positions
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
    
    # Normalize 'both' -> 'demo'/'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange) or account_type or "demo"
    
    if exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        private_key, is_testnet, wallet_address = _get_hl_credentials_for_account(hl_creds, account_type)
        
        if not private_key:
            return []
        
        adapter = None
        try:
            adapter = HLAdapter(
                private_key=private_key,
                testnet=is_testnet
            )
            await adapter.initialize()  # Auto-discover main wallet
            result = await adapter.fetch_open_orders()
            
            if result.get("success"):
                return result["data"]
            return []
        except Exception as e:
            logger.error(f"HL orders error: {e}")
            return []
        finally:
            if adapter:
                await adapter.close()
    
    else:
        # Bybit orders
        try:
            data = await bybit_request(
                user_id, "GET", "/v5/order/realtime",
                params={"category": "linear", "settleCoin": "USDT"},
                account_type=account_type
            )
            
            orders = data.get("result", {}).get("list", [])
            result = []
            for o in orders:
                if o.get("orderStatus") not in ["New", "PartiallyFilled", "Untriggered"]:
                    continue
                created_time = int(o.get("createdTime", 0))
                created_at_str = ""
                if created_time > 0:
                    from datetime import datetime
                    try:
                        created_at_str = datetime.fromtimestamp(created_time / 1000).strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        created_at_str = ""
                result.append({
                    "id": o.get("orderId"),
                    "symbol": o.get("symbol"),
                    "side": (o.get("side") or "Buy").lower(),
                    "type": o.get("orderType", "Limit"),
                    "order_type": o.get("orderType", "Limit"),
                    "price": float(o.get("price", 0)),
                    "trigger_price": float(o.get("triggerPrice", 0)),
                    "qty": float(o.get("qty", 0)),
                    "size": float(o.get("qty", 0)),
                    "filled": float(o.get("cumExecQty", 0)),
                    "remaining": float(o.get("leavesQty", 0)),
                    "status": o.get("orderStatus"),
                    "time": created_time,
                    "created_at": created_at_str,
                    "reduceOnly": o.get("reduceOnly", False),
                    "exchange": "bybit",
                    "account_type": account_type
                })
            return result
        except Exception as e:
            logger.error(f"Bybit orders error: {e}")
            return []


@router.post("/close")
async def close_position(
    req: ClosePositionRequest,
    user: dict = Depends(require_trading_license),
    exchange: Optional[str] = Query(None),
    account_type: Optional[str] = Query(None),
):
    """Close a specific position. Requires trading license."""
    user_id = user["user_id"]
    # iOS sends exchange/account_type as query params - merge into request
    if exchange and req.exchange == "bybit":
        req.exchange = exchange
    if account_type and req.account_type == "demo":
        req.account_type = account_type
    
    # NEW: Use services integration if available
    if SERVICES_AVAILABLE:
        try:
            result = await close_position_service(
                user_id=user_id,
                symbol=req.symbol,
                qty=None,
                exchange=req.exchange,
                account_type=req.account_type
            )
            if result.get("success"):
                # CROSS-PLATFORM: Log activity for sync
                if SYNC_SERVICE_AVAILABLE and sync_service:
                    try:
                        asyncio.create_task(sync_service.sync_trade_action(
                            user_id=user_id,
                            source="webapp",
                            action="close",
                            trade_data={
                                "symbol": req.symbol,
                                "exchange": req.exchange,
                                "account_type": req.account_type,
                                "action": "close_position"
                            }
                        ))
                    except Exception:
                        pass
                return {"success": True, "message": result.get("message")}
            return {"success": False, "error": result.get("error")}
        except Exception as e:
            logger.error(f"Services close error: {e}")
            # Fall through to old code
    
    # OLD CODE (fallback)
    if req.exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        account_type = _normalize_both_account_type(req.account_type, "hyperliquid") or "testnet"
        private_key, is_testnet, wallet_address = _get_hl_credentials_for_account(hl_creds, account_type)
        
        if not private_key:
            raise HTTPException(status_code=400, detail=f"HL {account_type} not configured")
        
        adapter = None
        try:
            adapter = HLAdapter(
                private_key=private_key,
                testnet=is_testnet
            )
            await adapter.initialize()  # Auto-discover main wallet
            # Get position info before closing
            pos_result = await adapter.fetch_positions()
            positions = pos_result.get("result", {}).get("list", [])
            pos_info = next((p for p in positions if p.get("symbol") == req.symbol), None)
            
            result = await adapter.close_position(req.symbol)
            
            if result.get("retCode") == 0:
                # Sync: Log trade and remove position from DB
                hl_account_type = "testnet" if is_testnet else "mainnet"
                
                if pos_info:
                    import time
                    entry_price = float(pos_info.get("avgPrice", 0))
                    exit_price = float(pos_info.get("markPrice", entry_price))
                    size = float(pos_info.get("size", 0))
                    side = pos_info.get("side", "Buy")
                    
                    pnl_abs = (exit_price - entry_price) * size * (1 if side == "Buy" else -1)
                    pnl_pct = ((exit_price / entry_price) - 1) * 100 * (1 if side == "Buy" else -1) if entry_price > 0 else 0
                    
                    try:
                        db.add_trade_log(
                            user_id=user_id,
                            signal_id=None,
                            symbol=req.symbol,
                            side=side,
                            entry_price=entry_price,
                            exit_price=exit_price,
                            exit_reason="webapp_close",
                            pnl=pnl_abs,
                            pnl_pct=pnl_pct,
                            signal_source="webapp",
                            strategy="manual",
                            account_type=hl_account_type,
                            exit_order_type="Market",
                            exit_ts=int(time.time() * 1000),
                            exchange="hyperliquid",
                        )
                        logger.info(f"[{user_id}] WebApp HL: Trade logged for {req.symbol}")
                    except Exception as log_err:
                        logger.warning(f"[{user_id}] WebApp HL: Failed to log trade: {log_err}")
                
                try:
                    db.remove_active_position(user_id, req.symbol, account_type=hl_account_type, exchange="hyperliquid")
                    logger.info(f"[{user_id}] WebApp HL: Position removed from DB for {req.symbol}")
                except Exception as rm_err:
                    logger.warning(f"[{user_id}] WebApp HL: Failed to remove position: {rm_err}")
                
                return {"success": True, "message": f"Closed {req.symbol}"}
            return {"success": False, "error": result.get("retMsg")}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if adapter:
                await adapter.close()
    
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
            import time
            order_link_id = f"close_{uuid.uuid4().hex[:12]}"
            result = await bybit_request(
                user_id, "POST", "/v5/order/create",
                body={
                    "category": "linear",
                    "symbol": req.symbol,
                    "side": close_side,
                    "orderType": "Market",
                    "qty": str(size),
                    "reduceOnly": True,
                    "orderLinkId": order_link_id,
                    "timeInForce": "IOC"
                },
                account_type=req.account_type
            )
            
            # Get actual execution price from order result
            order_id = result.get("result", {}).get("orderId")
            entry_price = float(pos.get("avgPrice", 0))
            side_for_log = pos.get("side", "Buy")
            
            # Try to get actual fill price from order info
            exit_price = float(pos.get("markPrice", entry_price))  # Fallback
            if order_id:
                try:
                    await asyncio.sleep(0.3)  # Wait for order to fill
                    order_info = await bybit_request(
                        user_id, "GET", "/v5/order/history",
                        params={"category": "linear", "orderId": order_id},
                        account_type=req.account_type
                    )
                    order_list = order_info.get("result", {}).get("list", [])
                    if order_list:
                        filled_order = order_list[0]
                        avg_fill_price = float(filled_order.get("avgPrice", 0))
                        if avg_fill_price > 0:
                            exit_price = avg_fill_price
                            logger.info(f"[{user_id}] Got actual fill price: {exit_price} for {req.symbol}")
                except Exception as fill_err:
                    logger.warning(f"[{user_id}] Could not get fill price: {fill_err}, using markPrice")
            
            # Get DB position for strategy info
            db_pos = None
            try:
                db_positions = db.get_active_positions(user_id, account_type=req.account_type, exchange="bybit")
                db_pos = next((p for p in db_positions if p.get("symbol") == req.symbol), None)
            except Exception:
                pass
            
            # Calculate PnL
            pnl_abs = (exit_price - entry_price) * size * (1 if side_for_log == "Buy" else -1)
            pnl_pct = ((exit_price / entry_price) - 1) * 100 * (1 if side_for_log == "Buy" else -1) if entry_price > 0 else 0
            
            # Log trade
            try:
                db.add_trade_log(
                    user_id=user_id,
                    signal_id=db_pos.get("signal_id") if db_pos else None,
                    symbol=req.symbol,
                    side=side_for_log,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    exit_reason="webapp_close",
                    pnl=pnl_abs,
                    pnl_pct=pnl_pct,
                    signal_source="webapp",
                    strategy=db_pos.get("strategy") if db_pos else "manual",
                    account_type=req.account_type,
                    exit_order_type="Market",
                    exit_ts=int(time.time() * 1000),
                    exchange="bybit",
                )
                logger.info(f"[{user_id}] WebApp: Trade logged for {req.symbol} close")
            except Exception as log_err:
                logger.warning(f"[{user_id}] WebApp: Failed to log trade: {log_err}")
            
            # Remove position from DB
            try:
                db.remove_active_position(user_id, req.symbol, account_type=req.account_type, exchange="bybit")
                logger.info(f"[{user_id}] WebApp: Position removed from DB for {req.symbol}")
            except Exception as rm_err:
                logger.warning(f"[{user_id}] WebApp: Failed to remove position: {rm_err}")
            
            return {
                "success": True,
                "message": f"Closed {req.symbol} position",
                "order_id": result.get("result", {}).get("orderId"),
                "pnl": pnl_abs
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/close-all")
async def close_all_positions(
    req: Optional[CloseAllRequest] = None,
    user: dict = Depends(require_trading_license),
    exchange: Optional[str] = Query(None),
    account_type: Optional[str] = Query(None),
):
    """Close all positions. Requires trading license."""
    user_id = user["user_id"]
    import time
    # iOS may send no body - construct from query params
    if req is None:
        req = CloseAllRequest(
            exchange=exchange or "bybit",
            account_type=account_type or "demo"
        )
    else:
        # iOS sends exchange/account_type as query params - merge into request
        if exchange and req.exchange == "bybit":
            req.exchange = exchange
        if account_type and req.account_type == "demo":
            req.account_type = account_type
    
    if req.exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        account_type = _normalize_both_account_type(req.account_type, "hyperliquid") or "testnet"
        private_key, is_testnet, wallet_address = _get_hl_credentials_for_account(hl_creds, account_type)
        
        if not private_key:
            raise HTTPException(status_code=400, detail=f"HL {account_type} not configured")
        
        adapter = None
        try:
            adapter = HLAdapter(
                private_key=private_key,
                testnet=is_testnet
            )
            await adapter.initialize()  # Auto-discover main wallet
            
            hl_account_type = "testnet" if is_testnet else "mainnet"
            
            # Get all positions - create snapshot
            positions_result = await adapter.fetch_positions()
            positions = positions_result.get("result", {}).get("list", [])
            
            # Create snapshot (защита от race condition)
            positions_snapshot = []
            for pos in positions:
                size = float(pos.get("size", 0))
                if size > 0:
                    positions_snapshot.append({
                        "symbol": pos.get("symbol"),
                        "side": pos.get("side", "Buy"),
                        "size": size,
                        "entry_price": float(pos.get("avgPrice", 0)),
                        "mark_price": float(pos.get("markPrice", 0))
                    })
            
            if not positions_snapshot:
                return {"success": True, "closed": 0, "total": 0, "total_pnl": 0}
            
            closed = 0
            total_pnl = 0
            errors = []
            
            for snap in positions_snapshot:
                symbol = snap["symbol"]
                entry_price = snap["entry_price"]
                size = snap["size"]
                side = snap["side"]
                
                try:
                    result = await adapter.close_position(symbol, size)
                    
                    if result.get("retCode") == 0 or result.get("success"):
                        closed += 1
                        
                        # Try to get actual fill price from result
                        exit_price = snap["mark_price"]  # Fallback
                        if result.get("data", {}).get("avgPrice"):
                            exit_price = float(result["data"]["avgPrice"])
                        
                        pnl_abs = (exit_price - entry_price) * size * (1 if side == "Buy" else -1)
                        pnl_pct = ((exit_price / entry_price) - 1) * 100 * (1 if side == "Buy" else -1) if entry_price > 0 else 0
                        total_pnl += pnl_abs
                        
                        try:
                            db.add_trade_log(
                                user_id=user_id,
                                signal_id=None,
                                symbol=symbol,
                                side=side,
                                entry_price=entry_price,
                                exit_price=exit_price,
                                exit_reason="webapp_close_all",
                                pnl=pnl_abs,
                                pnl_pct=pnl_pct,
                                signal_source="webapp",
                                strategy="manual",
                                account_type=hl_account_type,
                                exit_order_type="Market",
                                exit_ts=int(time.time() * 1000),
                                exchange="hyperliquid",
                            )
                        except Exception:
                            pass
                        
                        try:
                            db.remove_active_position(user_id, symbol, account_type=hl_account_type, exchange="hyperliquid")
                        except Exception:
                            pass
                except Exception as e:
                    error_msg = str(e)
                    if "position" not in error_msg.lower():
                        errors.append(f"{symbol}: {error_msg}")
            
            logger.info(f"[{user_id}] WebApp HL: Closed {closed}/{len(positions_snapshot)} positions, PnL: {total_pnl:.2f}")
            return {
                "success": closed > 0 or len(positions_snapshot) == 0,
                "closed": closed,
                "total": len(positions_snapshot),
                "total_pnl": round(total_pnl, 2),
                "errors": errors if errors else None
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if adapter:
                await adapter.close()
    
    else:
        # Bybit close all positions
        import uuid
        try:
            # Get all open positions - create snapshot
            pos_data = await bybit_request(
                user_id, "GET", "/v5/position/list",
                params={"category": "linear", "settleCoin": "USDT"},
                account_type=req.account_type
            )
            
            # Get DB positions for strategy info
            db_positions = {}
            try:
                active_pos = db.get_active_positions(user_id, account_type=req.account_type, exchange="bybit")
                for ap in active_pos:
                    db_positions[ap.get("symbol", "")] = ap
            except Exception:
                pass
            
            positions = pos_data.get("result", {}).get("list", [])
            
            # Create snapshot of positions to close (защита от race condition)
            positions_snapshot = []
            for pos in positions:
                size = float(pos.get("size", 0))
                if size > 0:
                    positions_snapshot.append({
                        "symbol": pos.get("symbol"),
                        "side": pos.get("side", "Buy"),
                        "size": size,
                        "entry_price": float(pos.get("avgPrice", 0)),
                        "mark_price": float(pos.get("markPrice", 0))
                    })
            
            if not positions_snapshot:
                return {"success": True, "closed": 0, "total": 0, "total_pnl": 0}
            
            closed = 0
            errors = []
            total_pnl = 0
            
            for snap in positions_snapshot:
                symbol = snap["symbol"]
                side = snap["side"]
                snapshot_size = snap["size"]
                entry_price = snap["entry_price"]
                close_side = "Sell" if side == "Buy" else "Buy"
                
                try:
                    order_link_id = f"closeall_{uuid.uuid4().hex[:10]}"
                    result = await bybit_request(
                        user_id, "POST", "/v5/order/create",
                        body={
                            "category": "linear",
                            "symbol": symbol,
                            "side": close_side,
                            "orderType": "Market",
                            "qty": str(snapshot_size),
                            "reduceOnly": True,  # Критично! Не откроет обратную позицию
                            "orderLinkId": order_link_id,
                            "timeInForce": "IOC"
                        },
                        account_type=req.account_type
                    )
                    
                    # Get actual fill price
                    order_id = result.get("result", {}).get("orderId")
                    exit_price = snap["mark_price"]  # Fallback
                    actual_size = snapshot_size
                    
                    if order_id:
                        try:
                            await asyncio.sleep(0.2)
                            order_info = await bybit_request(
                                user_id, "GET", "/v5/order/history",
                                params={"category": "linear", "orderId": order_id},
                                account_type=req.account_type
                            )
                            order_list = order_info.get("result", {}).get("list", [])
                            if order_list:
                                filled_order = order_list[0]
                                avg_fill_price = float(filled_order.get("avgPrice", 0))
                                filled_qty = float(filled_order.get("cumExecQty", 0))
                                if avg_fill_price > 0:
                                    exit_price = avg_fill_price
                                if filled_qty > 0:
                                    actual_size = filled_qty
                        except Exception:
                            pass
                    
                    closed += 1
                    
                    # Calculate PnL with actual fill price
                    pnl_abs = (exit_price - entry_price) * actual_size * (1 if side == "Buy" else -1)
                    pnl_pct = ((exit_price / entry_price) - 1) * 100 * (1 if side == "Buy" else -1) if entry_price > 0 else 0
                    total_pnl += pnl_abs
                    
                    db_pos = db_positions.get(symbol, {})
                    
                    # Log trade
                    try:
                        db.add_trade_log(
                            user_id=user_id,
                            signal_id=db_pos.get("signal_id"),
                            symbol=symbol,
                            side=side,
                            entry_price=entry_price,
                            exit_price=exit_price,
                            exit_reason="webapp_close_all",
                            pnl=pnl_abs,
                            pnl_pct=pnl_pct,
                            signal_source="webapp",
                            strategy=db_pos.get("strategy", "manual"),
                            account_type=req.account_type,
                            exit_order_type="Market",
                            exit_ts=int(time.time() * 1000),
                            exchange="bybit",
                        )
                    except Exception:
                        pass
                    
                    # Remove from DB
                    try:
                        db.remove_active_position(user_id, symbol, account_type=req.account_type, exchange="bybit")
                    except Exception:
                        pass
                        
                except Exception as e:
                    error_msg = str(e)
                    # Если позиция уже закрыта - не считаем ошибкой
                    if "position not found" in error_msg.lower() or "reduce only" in error_msg.lower():
                        logger.info(f"[{user_id}] Position {symbol} already closed or changed")
                    else:
                        errors.append(f"{symbol}: {error_msg}")
            
            logger.info(f"[{user_id}] WebApp: Closed {closed}/{len(positions_snapshot)} positions, PnL: {total_pnl:.2f}")
            return {
                "success": closed > 0 or len(positions_snapshot) == 0,
                "closed": closed,
                "total": len(positions_snapshot),
                "total_pnl": round(total_pnl, 2),
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
    
    # Normalize 'both' -> 'demo'/'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange) or account_type or "demo"
    
    if exchange == "hyperliquid":
        # HyperLiquid execution history via user_fills API
        hl_creds = db.get_hl_credentials(user_id)
        private_key, is_testnet, wallet_address = _get_hl_credentials_for_account(hl_creds, account_type)
        
        if not private_key:
            return {"executions": [], "error": f"HL {account_type} not configured"}
        
        adapter = None
        try:
            adapter = HLAdapter(
                private_key=private_key,
                testnet=is_testnet
            )
            await adapter.initialize()  # Auto-discover main wallet
            
            # Fetch trade history using main_wallet_address for Unified Account support
            result = await adapter.fetch_trade_history(limit=limit)
            
            if result.get("success"):
                trades = result.get("data", [])
                executions = []
                for t in trades:
                    # HL fills: direction 'Open Long'/'Close Long'/'Open Short'/'Close Short'
                    direction = t.get("direction", "")
                    exec_type = "close" if "Close" in direction else "open"
                    executions.append({
                        "id": str(t.get("oid") or t.get("time", 0)),
                        "symbol": t.get("symbol", ""),
                        "side": t.get("side", "").lower(),
                        "entry_price": 0,  # HL fills don't include entry price
                        "exit_price": float(t.get("price", 0)),
                        "size": float(t.get("size", 0)),
                        "pnl": float(t.get("pnl", 0)),
                        "fee": float(t.get("fee", 0)),
                        "leverage": None,
                        "order_type": "limit" if not t.get("crossed", False) else "market",
                        "exec_type": exec_type,
                        "direction": direction,
                        "hash": t.get("hash", ""),
                        "liquidation": t.get("liquidation", False),
                        "created_at": int(t.get("time", 0)),
                        "updated_at": int(t.get("time", 0)),
                        "exchange": "hyperliquid",
                        "account_type": account_type
                    })
                return {"executions": executions, "total": len(executions)}
            else:
                return {"executions": [], "error": result.get("error", "Unknown error")}
        except Exception as e:
            return {"executions": [], "error": str(e)}
        finally:
            if adapter:
                await adapter.close()
    
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
    account_type: str = Query(None),  # 'demo', 'real', or None for all
    limit: int = Query(20, ge=1, le=100),
    user: dict = Depends(get_current_user)
) -> dict:
    """Get recent trades history from trade_logs table."""
    user_id = user["user_id"]
    
    # Normalize 'both' -> 'demo'/'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange) or account_type
    
    try:
        from core.db_postgres import execute, execute_scalar
        
        # Build query with account_type and exchange filters for multitenancy
        if account_type:
            trades_data = execute("""
                SELECT id, symbol, side, entry_price, exit_price, pnl, pnl_pct,
                       ts, strategy, account_type, exit_reason, exchange
                FROM trade_logs 
                WHERE user_id = %s AND account_type = %s AND exchange = %s
                ORDER BY ts DESC 
                LIMIT %s
            """, (user_id, account_type, exchange, limit))
            
            # Get total count with exchange filter
            total = execute_scalar(
                "SELECT COUNT(*) FROM trade_logs WHERE user_id = %s AND account_type = %s AND exchange = %s",
                (user_id, account_type, exchange)
            ) or 0
        else:
            trades_data = execute("""
                SELECT id, symbol, side, entry_price, exit_price, pnl, pnl_pct,
                       ts, strategy, account_type, exit_reason, exchange
                FROM trade_logs 
                WHERE user_id = %s AND exchange = %s
                ORDER BY ts DESC 
                LIMIT %s
            """, (user_id, exchange, limit))
            
            # Get total count with exchange filter
            total = execute_scalar(
                "SELECT COUNT(*) FROM trade_logs WHERE user_id = %s AND exchange = %s",
                (user_id, exchange)
            ) or 0
        
        trades = []
        for row in trades_data:
            ts_str = str(row.get("ts")) if row.get("ts") else None
            trades.append({
                "id": row.get("id"),
                "symbol": row.get("symbol"),
                "side": row.get("side"),
                "entry_price": row.get("entry_price"),
                "exit_price": row.get("exit_price"),
                "pnl": row.get("pnl"),
                "pnl_pct": row.get("pnl_pct"),  # iOS expects pnl_pct
                "pnl_percent": row.get("pnl_pct"),  # WebApp expects pnl_percent
                "exchange": row.get("exchange") or exchange,
                "strategy": row.get("strategy") or "unknown",
                "ts": ts_str,  # iOS expects ts
                "timestamp": ts_str,  # iOS fallback / Android expects this
                "created_at": ts_str,  # WebApp compatibility
                "closed_at": ts_str,  # WebApp compatibility
                "account_type": row.get("account_type") or "demo",
                "exit_reason": row.get("exit_reason"),
            })
        
        # Return both formats for compatibility: iOS expects "trades", Android expects "data"
        return {"success": True, "trades": trades, "data": trades, "total": total}
        
    except Exception as e:
        logger.error(f"Trades fetch error: {e}")
        return {"success": False, "trades": [], "data": [], "total": 0, "error": str(e)}


@router.get("/stats")
async def get_trading_stats(
    exchange: str = Query("bybit"),
    period: str = Query("all"),  # all, day, week, month
    account_type: str = Query(None),  # 'demo', 'real', or None for all
    user: dict = Depends(get_current_user)
) -> dict:
    """Get trading statistics from trade_logs table."""
    user_id = user["user_id"]
    
    # Normalize 'both' -> 'demo'/'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange) or account_type
    
    try:
        # Use db module's get_trade_stats which works with PostgreSQL
        stats = db.get_trade_stats(user_id, strategy=None, period=period, account_type=account_type, exchange=exchange)
        
        # Map database field names to API response field names
        total = stats.get("total", 0)
        tp_count = stats.get("tp_count", 0)
        sl_count = stats.get("sl_count", 0)
        eod_count = stats.get("eod_count", 0)
        winrate = stats.get("winrate", 0.0)
        total_pnl = stats.get("total_pnl", 0.0)
        avg_pnl_pct = stats.get("avg_pnl_pct", 0.0)
        gross_profit = stats.get("gross_profit", 0.0)
        gross_loss = stats.get("gross_loss", 0.0)
        
        # Calculate wins/losses based on TP/SL counts
        wins = tp_count
        losses = sl_count
        
        return {
            "total_trades": total,
            "winning_trades": wins,
            "losing_trades": losses,
            "eod_trades": eod_count,
            "win_rate": round(winrate, 1),
            "total_pnl": round(total_pnl, 2),
            "avg_pnl": round(avg_pnl_pct, 2),
            "gross_profit": round(gross_profit, 2),
            "gross_loss": round(abs(gross_loss), 2),
            "profit_factor": stats.get("profit_factor", 0.0),
            "long_count": stats.get("long_count", 0),
            "short_count": stats.get("short_count", 0),
            "long_winrate": stats.get("long_winrate", 0.0),
            "short_winrate": stats.get("short_winrate", 0.0),
            "open_count": stats.get("open_count", 0),
            "best_trade": stats.get("best_pnl", 0.0),
            "worst_trade": stats.get("worst_pnl", 0.0),
        }
        
    except Exception as e:
        logger.error(f"Stats fetch error: {e}")
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "eod_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "avg_pnl": 0,
            "gross_profit": 0,
            "gross_loss": 0,
            "profit_factor": 0,
            "long_count": 0,
            "short_count": 0,
            "long_winrate": 0,
            "short_winrate": 0,
            "open_count": 0,
            "best_trade": 0,
            "worst_trade": 0,
            "error": str(e)
        }


@router.get("/stats/by-strategy")
async def get_stats_by_strategy(
    strategy: str = Query("all"),  # all, rsi_bb, fibonacci, scryptomera, scalper, elcaro, oi, manual
    period: str = Query("week"),   # today, week, month, all
    exchange: str = Query("bybit"),
    account_type: str = Query(None),
    user: dict = Depends(get_current_user)
) -> dict:
    """
    Get trading statistics filtered by strategy.
    Returns summary stats + breakdown by strategy + recent trades.
    This endpoint powers the iOS StrategyStatsView.
    """
    user_id = user["user_id"]
    
    # Normalize account type
    account_type = _normalize_both_account_type(account_type, exchange) or account_type
    
    # Period to days mapping
    period_days = {
        "today": 1,
        "week": 7,
        "month": 30,
        "all": None
    }.get(period, 7)
    
    try:
        # If specific strategy selected, get stats for that strategy
        strategy_filter = None if strategy == "all" else strategy
        
        # Get main stats
        stats = db.get_trade_stats(
            user_id, 
            strategy=strategy_filter, 
            period=period,
            account_type=account_type,
            exchange=exchange
        )
        
        total = stats.get("total", 0)
        wins = stats.get("tp_count", 0)
        losses = stats.get("sl_count", 0)
        total_pnl = stats.get("total_pnl", 0.0)
        winrate = stats.get("winrate", 0.0) if total > 0 else 0.0
        gross_profit = stats.get("gross_profit", 0.0)
        gross_loss = abs(stats.get("gross_loss", 0.0))
        
        # Calculate averages
        avg_win = gross_profit / wins if wins > 0 else 0.0
        avg_loss = gross_loss / losses if losses > 0 else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else (gross_profit if gross_profit > 0 else 0.0)
        
        summary = {
            "total_pnl": round(total_pnl, 2),
            "total_trades": total,
            "win_rate": round(winrate, 1),
            "profit_factor": round(profit_factor, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "best_trade": round(stats.get("best_pnl", 0.0), 2),
            "worst_trade": round(stats.get("worst_pnl", 0.0), 2),
        }
        
        # Get breakdown by each strategy (if "all" selected)
        breakdown = []
        if strategy == "all":
            strategies = ["rsi_bb", "fibonacci", "scryptomera", "scalper", "elcaro", "oi", "manual"]
            for strat in strategies:
                strat_stats = db.get_trade_stats(
                    user_id,
                    strategy=strat,
                    period=period,
                    account_type=account_type,
                    exchange=exchange
                )
                strat_total = strat_stats.get("total", 0)
                if strat_total > 0:
                    strat_wins = strat_stats.get("tp_count", 0) or strat_stats.get("wins", 0) or 0
                    strat_losses = strat_stats.get("sl_count", 0) or strat_stats.get("losses", 0) or 0
                    breakdown.append({
                        "strategy": strat,
                        "pnl": round(strat_stats.get("total_pnl", 0.0), 2),
                        "trades": strat_total,
                        "wins": strat_wins,
                        "losses": strat_losses,
                        "win_rate": round(strat_stats.get("winrate", 0.0), 1)
                    })
            
            # Sort by PnL descending
            breakdown.sort(key=lambda x: x["pnl"], reverse=True)
        
        # Get recent trades
        recent_trades = []
        try:
            trades = db.get_trade_logs_list(
                user_id,
                strategy=strategy_filter or None,  # type: ignore[arg-type]
                limit=10,
                account_type=account_type,
                exchange=exchange
            )
            for trade in trades:
                recent_trades.append({
                    "id": trade.get("id", 0),
                    "symbol": trade.get("symbol", ""),
                    "side": "Long" if trade.get("side", "").lower() in ["buy", "long"] else "Short",
                    "pnl": round(trade.get("pnl", 0.0), 2),
                    "pnl_percent": round(trade.get("pnl_pct", 0.0) or 0.0, 2),
                    "entry_price": round(float(trade.get("entry_price", 0) or 0), 6),
                    "exit_price": round(float(trade.get("exit_price", 0) or 0), 6),
                    "size": float(trade.get("qty", 0) or trade.get("size", 0) or 0),
                    "strategy": trade.get("strategy", "manual"),
                    "exit_reason": trade.get("exit_reason", ""),
                    "closed_at": str(trade.get("ts", ""))[:16].replace("T", " ") if trade.get("ts") else ""
                })
        except Exception as e:
            logger.warning(f"Failed to get recent trades: {e}")
        
        return {
            "summary": summary,
            "breakdown": breakdown,
            "recent_trades": recent_trades
        }
        
    except Exception as e:
        logger.error(f"Strategy stats error: {e}")
        return {
            "summary": {
                "total_pnl": 0,
                "total_trades": 0,
                "win_rate": 0,
                "profit_factor": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "best_trade": 0,
                "worst_trade": 0
            },
            "breakdown": [],
            "recent_trades": [],
            "error": str(e)
        }


# ===================== ORDER PLACEMENT =====================

@router.post("/order")
async def place_order(
    req: PlaceOrderRequest,
    user: dict = Depends(require_trading_license),
    exchange: Optional[str] = Query(None),
    account_type: Optional[str] = Query(None),
):
    """Place a new order on Bybit or HyperLiquid. Requires trading license."""
    user_id = user["user_id"]
    # iOS sends exchange/account_type as query params - merge into request
    if exchange and req.exchange == "bybit":
        req.exchange = exchange
    if account_type and req.account_type == "demo":
        req.account_type = account_type
    
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
    except Exception as e:
        # Leverage might already be set - log at debug level
        logger.debug(f"Set leverage for {req.symbol}: {e}")
    
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
        
        # P0.5: Save position to database after successful order
        try:
            # Calculate SL/TP prices if percentages provided
            sl_price = None
            tp_price = None
            if req.stop_loss:
                sl_price = req.stop_loss
            if req.take_profit:
                tp_price = req.take_profit
            
            # Get current price for entry estimation (for market orders)
            entry_price = req.price
            if not entry_price:
                # Try to get from a quick price check (if available in result)
                entry_price = 0  # Will be updated by monitor
            
            db.add_active_position(
                user_id=user_id,
                symbol=req.symbol,
                side=side,
                entry_price=entry_price,
                size=req.size,
                timeframe="24h",
                signal_id=None,
                strategy=req.strategy if req.strategy else "webapp",  # Use 'webapp' for manual orders from web
                account_type=req.account_type,
                # P0.3: New fields
                source="webapp",
                opened_by="webapp",
                exchange="bybit",
                sl_price=sl_price,
                tp_price=tp_price,
                leverage=req.leverage,
                client_order_id=order_link_id,
                exchange_order_id=order_id,
            )
            logger.info(f"[{user_id}] WebApp: Position saved for {req.symbol} {side}")
        except Exception as pos_err:
            logger.warning(f"[{user_id}] WebApp: Failed to save position: {pos_err}")
        
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
    """Place order on HyperLiquid with TP/SL support (same as Bybit)"""
    hl_creds = db.get_hl_credentials(user_id)
    account_type = req.account_type if hasattr(req, 'account_type') else 'testnet'
    private_key, is_testnet, wallet_address = _get_hl_credentials_for_account(hl_creds, account_type)
    
    if not private_key:
        return {"success": False, "error": f"HyperLiquid {account_type} not configured", "exchange": "hyperliquid"}
    
    adapter = None
    try:
        adapter = HLAdapter(
            private_key=private_key,
            testnet=is_testnet
        )
        await adapter.initialize()  # Auto-discover main wallet
        
        # Normalize symbol for HL (remove USDT/USDC suffix)
        hl_symbol = req.symbol.replace("USDT", "").replace("USDC", "")
        
        # Set leverage first (same as Bybit)
        try:
            await adapter.set_leverage(hl_symbol, req.leverage)
        except Exception as lev_err:
            logger.warning(f"[{user_id}] HL leverage error: {lev_err}")
        
        # Place order with TP/SL (pass to adapter.place_order which handles it)
        result = await adapter.place_order(
            symbol=req.symbol,
            side=side,
            qty=req.size,
            order_type=order_type,
            price=req.price if order_type == "Limit" else None,
            take_profit=req.take_profit,
            stop_loss=req.stop_loss
        )
        
        if result.get("retCode") == 0:
            order_id = result.get("result", {}).get("orderId", "")
            hl_account_type = "testnet" if is_testnet else "mainnet"
            
            # P0.5: Save position to database after successful order
            try:
                db.add_active_position(
                    user_id=user_id,
                    symbol=req.symbol,
                    side=side,
                    entry_price=req.price or 0,  # Will be updated by monitor
                    size=req.size,
                    timeframe="24h",
                    signal_id=None,
                    strategy=req.strategy if req.strategy else "webapp",  # Use 'webapp' for manual orders from web
                    account_type=hl_account_type,
                    # P0.3: New fields
                    source="webapp",
                    opened_by="webapp",
                    exchange="hyperliquid",
                    sl_price=req.stop_loss,
                    tp_price=req.take_profit,
                    leverage=req.leverage,
                    exchange_order_id=order_id,
                )
                logger.info(f"[{user_id}] WebApp HL: Position saved for {req.symbol} {side}")
            except Exception as pos_err:
                logger.warning(f"[{user_id}] WebApp HL: Failed to save position: {pos_err}")
            
            return {
                "success": True,
                "order_id": order_id,
                "exchange": "hyperliquid",
                "account_type": hl_account_type,
                "symbol": req.symbol,
                "side": side,
                "size": req.size,
                "message": f"Order placed on HyperLiquid ({hl_account_type})"
            }
        else:
            return {"success": False, "error": result.get("retMsg"), "exchange": "hyperliquid"}
    except Exception as e:
        return {"success": False, "error": str(e), "exchange": "hyperliquid"}
    finally:
        if adapter:
            await adapter.close()


@router.post("/leverage")
async def set_leverage(
    req: SetLeverageRequest,
    user: dict = Depends(require_trading_license)
):
    """Set leverage for a symbol. Requires trading license."""
    user_id = user["user_id"]
    
    if req.exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        account_type = getattr(req, 'account_type', 'testnet')
        private_key, is_testnet, wallet_address = _get_hl_credentials_for_account(hl_creds, account_type)
        
        if not private_key:
            return {"success": False, "error": f"HL {account_type} not configured"}
        
        adapter = None
        try:
            adapter = HLAdapter(
                private_key=private_key,
                testnet=is_testnet
            )
            await adapter.initialize()  # Auto-discover main wallet
            await adapter.set_leverage(req.symbol.replace("USDT", "").replace("USDC", ""), req.leverage)
            return {"success": True, "leverage": req.leverage}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if adapter:
                await adapter.close()
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
        account_type = getattr(req, 'account_type', 'testnet')
        private_key, is_testnet, wallet_address = _get_hl_credentials_for_account(hl_creds, account_type)
        
        if not private_key:
            return {"success": False, "error": f"HL {account_type} not configured"}
        
        adapter = None
        try:
            adapter = HLAdapter(
                private_key=private_key,
                testnet=is_testnet
            )
            await adapter.initialize()  # Auto-discover main wallet
            result = await adapter.cancel_order(req.symbol, req.order_id)
            return {"success": result.get("retCode") == 0}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if adapter:
                await adapter.close()
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
            "configured": bool(
                hl_creds.get("hl_testnet_private_key") or 
                hl_creds.get("hl_mainnet_private_key") or 
                hl_creds.get("hl_private_key")
            ),
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
    user: dict = Depends(require_trading_license),
    exchange: Optional[str] = Query(None),
    account_type: Optional[str] = Query(None),
):
    """Modify Take Profit / Stop Loss for an existing position. Requires trading license."""
    user_id = user["user_id"]
    # iOS sends exchange/account_type as query params - merge into request
    if exchange and req.exchange == "bybit":
        req.exchange = exchange
    if account_type and req.account_type == "demo":
        req.account_type = account_type
    
    if req.exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        hl_account: str = getattr(req, 'account_type', 'testnet') or "testnet"
        private_key, is_testnet, wallet_address = _get_hl_credentials_for_account(hl_creds, hl_account)
        
        if not private_key:
            return {"success": False, "error": f"HL {hl_account} not configured"}
        
        adapter = None
        try:
            adapter = HLAdapter(
                private_key=private_key,
                testnet=is_testnet
            )
            await adapter.initialize()  # Auto-discover main wallet
            
            # Get position to determine side
            pos_result = await adapter.fetch_positions()
            positions = pos_result.get("result", {}).get("list", [])
            pos = next((p for p in positions if p.get("symbol") == req.symbol), None)
            
            if not pos:
                return {"success": False, "error": "Position not found"}
            
            is_long = pos.get("side", "").lower() == "buy" or pos.get("side", "").lower() == "long"
            
            # Normalize symbol for HyperLiquid (remove USDT suffix)
            coin = req.symbol.upper().replace("USDT", "").replace("USDC", "").replace("PERP", "")
            
            # Set TP/SL via adapter - it will use main_wallet_address for Unified Account
            result = await adapter.set_tp_sl(
                coin=coin,
                tp_price=req.take_profit,
                sl_price=req.stop_loss
            )
            
            # P0.8: Set manual_sltp_override in DB so bot won't overwrite
            try:
                # Use normalized account_type from request, not global hl_testnet flag
                hl_account_type = _normalize_both_account_type(req.account_type, "hyperliquid") or "testnet"
                db.set_manual_sltp_override(
                    user_id, req.symbol, hl_account_type, 
                    sl_price=req.stop_loss, tp_price=req.take_profit
                )
                logger.info(f"[{user_id}] WebApp: Set manual_sltp_override for {req.symbol}")
            except Exception as e:
                logger.warning(f"[{user_id}] WebApp: Failed to set manual override: {e}")
            
            return {"success": True, "message": "TP/SL updated", "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if adapter:
                await adapter.close()
    
    else:
        # Bybit TP/SL modification
        try:
            body = {
                "category": "linear",
                "symbol": req.symbol,
                "positionIdx": req.position_idx,
                "tpslMode": "Full",  # REQUIRED by Bybit v5 API!
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
            
            # P0.8: Set manual_sltp_override in DB so bot won't overwrite
            try:
                bybit_account_type = _normalize_both_account_type(req.account_type, "bybit") or "demo"
                db.set_manual_sltp_override(
                    user_id, req.symbol, bybit_account_type, 
                    sl_price=req.stop_loss, tp_price=req.take_profit
                )
                logger.info(f"[{user_id}] WebApp: Set manual_sltp_override for {req.symbol}")
            except Exception as e:
                logger.warning(f"[{user_id}] WebApp: Failed to set manual override: {e}")
            
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


@router.post("/cancel")
async def cancel_order_by_id(
    req: CancelOrderRequest,
    user: dict = Depends(require_trading_license)
):
    """Cancel a single order by ID. Requires trading license."""
    user_id = user["user_id"]
    
    if req.exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        account_type = getattr(req, 'account_type', 'testnet')
        private_key, is_testnet, wallet_address = _get_hl_credentials_for_account(hl_creds, account_type)
        
        if not private_key:
            return {"success": False, "error": f"HL {account_type} not configured"}
        
        adapter = None
        try:
            adapter = HLAdapter(
                private_key=private_key,
                testnet=is_testnet
            )
            await adapter.initialize()  # Auto-discover main wallet
            result = await adapter.cancel_order(req.symbol, req.order_id)
            
            if result.get("success"):
                return {"success": True, "message": f"Cancelled order {req.order_id}"}
            else:
                return {"success": False, "error": result.get("error", "Failed to cancel")}
        except Exception as e:
            logger.error(f"HL cancel order error: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if adapter:
                await adapter.close()
    
    else:
        # Bybit cancel
        try:
            result = await bybit_request(
                user_id, "POST", "/v5/order/cancel",
                body={
                    "category": "linear",
                    "symbol": req.symbol,
                    "orderId": req.order_id
                },
                account_type=req.account_type
            )
            
            if result.get("retCode") == 0:
                return {
                    "success": True,
                    "message": f"Cancelled order {req.order_id}",
                    "order_id": req.order_id
                }
            else:
                return {
                    "success": False,
                    "error": result.get("retMsg", "Cancel failed")
                }
        except HTTPException as e:
            return {"success": False, "error": e.detail}
        except Exception as e:
            logger.error(f"Bybit cancel order error: {e}")
            return {"success": False, "error": str(e)}


@router.post("/cancel-all-orders")
async def cancel_all_orders(
    exchange: str = Query("bybit"),
    account_type: str = Query("demo"),
    symbol: Optional[str] = Query(None),
    user: dict = Depends(require_trading_license)
):
    """Cancel all open orders. Requires trading license."""
    user_id = user["user_id"]
    
    # Normalize 'both' -> 'demo'/'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange) or account_type or "demo"
    
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
    user: dict = Depends(require_trading_license)
):
    """Place a DCA ladder of orders. Requires trading license."""
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
    except Exception:
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


def _fib_sequence(n: int) -> List[int]:
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
        # Use correct key based on account_type
        is_testnet = account_type in ("testnet", "demo")
        private_key = (
            hl_creds.get("hl_testnet_private_key") if is_testnet 
            else hl_creds.get("hl_mainnet_private_key")
        )
        # Fallback to legacy format
        if not private_key:
            private_key = hl_creds.get("hl_private_key")
            is_testnet = hl_creds.get("hl_testnet", False)
        
        if private_key:
            adapter = HLAdapter(private_key=private_key, testnet=is_testnet)
            try:
                await adapter.initialize()
                await adapter.set_leverage(symbol.replace("USDT", "").replace("USDC", ""), leverage)
            finally:
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
    
    # Use correct key based on account_type
    is_testnet = account_type in ("testnet", "demo")
    private_key = (
        hl_creds.get("hl_testnet_private_key") if is_testnet 
        else hl_creds.get("hl_mainnet_private_key")
    )
    # Fallback to legacy format
    if not private_key:
        private_key = hl_creds.get("hl_private_key")
        is_testnet = hl_creds.get("hl_testnet", False)
    
    if not private_key:
        return {"success": False, "error": f"HL {account_type} not configured"}
    
    side_formatted = "Buy" if side.lower() in ["buy", "long"] else "Sell"
    adapter = HLAdapter(private_key=private_key, testnet=is_testnet)
    try:
        await adapter.initialize()
        result = await adapter.place_order(symbol=symbol, side=side_formatted, qty=size, order_type=order_type, price=price)
        return {"success": result.get("retCode") == 0, "order_id": result.get("result", {}).get("orderId")}
    finally:
        await adapter.close()


@router.post("/calculate-position")
async def calculate_position_size(req: CalculatePositionRequest):
    """
    Calculate optimal position size based on risk parameters.
    Matches bot.py exact formulas for consistency.
    
    Args:
        req: Position calculation request with balance, entry, stop loss, risk%, leverage
        
    Returns:
        Complete position calculation with size, margin, risk/reward, warnings
    """
    if not POSITION_CALCULATOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Position calculator service unavailable")
    
    try:
        # Determine if using price or percent for stop loss
        if req.stop_loss_price is not None:
            # Calculate from price
            result = position_calculator.calculate(
                account_balance=req.account_balance,
                entry_price=req.entry_price,
                stop_loss_price=req.stop_loss_price,
                risk_percent=req.risk_percent,
                leverage=req.leverage,
                side=req.side,
                take_profit_price=req.take_profit_price
            )
        elif req.stop_loss_percent is not None:
            # Calculate from percent
            result = position_calculator.calculate_from_percent(
                account_balance=req.account_balance,
                entry_price=req.entry_price,
                stop_loss_percent=req.stop_loss_percent,
                risk_percent=req.risk_percent,
                leverage=req.leverage,
                side=req.side,
                take_profit_percent=req.take_profit_percent
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either stop_loss_price or stop_loss_percent must be provided"
            )
        
        # Validate against exchange limits if provided
        warnings = []
        if req.min_order_size and result.position_size < req.min_order_size:
            warnings.append(f"Position size {result.position_size} below minimum {req.min_order_size}")
        
        if req.max_order_size and result.position_size > req.max_order_size:
            warnings.append(f"Position size {result.position_size} exceeds maximum {req.max_order_size}")
        
        # Round to qty_step if provided
        final_size = result.position_size
        if req.qty_step:
            final_size = round(result.position_size / req.qty_step) * req.qty_step
            if abs(final_size - result.position_size) > 0.0001:
                warnings.append(f"Position size rounded from {result.position_size} to {final_size} (qty_step: {req.qty_step})")
        
        # Build response
        response = PositionCalculationResponse(
            position_size=final_size,
            position_value_usd=result.position_value_usd,
            margin_required=result.margin_required,
            risk_amount_usd=result.risk_amount_usd,
            stop_loss_price=result.stop_loss_price,
            stop_loss_percent=result.stop_loss_percent,
            take_profit_price=result.take_profit_price,
            take_profit_percent=result.take_profit_percent,
            potential_profit_usd=result.potential_profit_usd,
            risk_reward_ratio=result.risk_reward_ratio,
            max_loss_usd=result.risk_amount_usd,
            margin_ratio=round(result.margin_required / result.position_value_usd, 4) if result.position_value_usd > 0 else 0,
            is_valid=len(warnings) == 0,
            warnings=warnings
        )
        
        return response.dict()
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Position calculation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")


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
    except Exception:
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


@router.get("/price/{symbol}")
async def get_symbol_price(
    symbol: str,
    user: dict = Depends(get_current_user)
):
    """Get current price for a symbol."""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
            async with session.get(url) as resp:
                data = await resp.json()
                
                if data.get("retCode") != 0:
                    raise HTTPException(status_code=400, detail=data.get("retMsg"))
                
                tickers = data.get("result", {}).get("list", [])
                if not tickers:
                    raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
                
                t = tickers[0]
                return {
                    "symbol": t.get("symbol"),
                    "price": float(t.get("lastPrice", 0)),
                    "bid": float(t.get("bid1Price", 0)),
                    "ask": float(t.get("ask1Price", 0)),
                    "high_24h": float(t.get("highPrice24h", 0)),
                    "low_24h": float(t.get("lowPrice24h", 0)),
                    "change_24h": float(t.get("price24hPcnt", 0)) * 100,
                    "volume_24h": float(t.get("turnover24h", 0)),
                    "funding_rate": float(t.get("fundingRate", 0)) * 100 if t.get("fundingRate") else 0
                }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================== STRATEGY SETTINGS ENDPOINTS =====================

# Strategy names list (keep in sync with bot)
STRATEGY_NAMES = ["oi", "scryptomera", "scalper", "elcaro", "fibonacci", "rsi_bb", "manual"]

# Default strategy settings
DEFAULT_STRATEGY_SETTINGS = {
    "oi": {"enabled": False, "percent": 1.0, "sl_percent": 30.0, "tp_percent": 25.0, "leverage": 10, "use_atr": 0},
    "scryptomera": {"enabled": False, "percent": 1.0, "sl_percent": 30.0, "tp_percent": 25.0, "leverage": 10, "use_atr": 0},
    "scalper": {"enabled": False, "percent": 1.0, "sl_percent": 30.0, "tp_percent": 25.0, "leverage": 10, "use_atr": 0},
    "elcaro": {"enabled": False, "percent": 1.0, "sl_percent": 30.0, "tp_percent": 25.0, "leverage": 10, "use_atr": 0},
    "fibonacci": {"enabled": False, "percent": 1.0, "sl_percent": 30.0, "tp_percent": 25.0, "leverage": 10, "use_atr": 0},
    "rsi_bb": {"enabled": False, "percent": 1.0, "sl_percent": 30.0, "tp_percent": 25.0, "leverage": 10, "use_atr": 0},
    "manual": {"enabled": True, "percent": 1.0, "sl_percent": 30.0, "tp_percent": 25.0, "leverage": 10, "use_atr": 0},
}


@router.get("/strategy-settings")
async def get_all_strategy_settings(
    exchange: str = Query("bybit"),
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
):
    """
    Get all strategy settings for the user's current exchange and account type.
    Returns dict with all strategies and their settings.
    Used by terminal to show strategy-specific TP/SL values.
    """
    user_id = user["user_id"]
    
    # Normalize 'both' -> 'demo'/'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange) or account_type or "demo"
    
    try:
        # Get global user config for defaults
        user_cfg = db.get_user_config(user_id)
        global_sl = user_cfg.get("sl_percent", 30.0)
        global_tp = user_cfg.get("tp_percent", 25.0)
        global_leverage = user_cfg.get("leverage", 10)
        global_percent = user_cfg.get("percent", 1.0)
        global_use_atr = user_cfg.get("position_use_atr", 0)
        
        result = {
            "global": {
                "sl_percent": global_sl,
                "tp_percent": global_tp,
                "leverage": global_leverage,
                "percent": global_percent,
                "use_atr": bool(global_use_atr)
            },
            "strategies": {}
        }
        
        # Get each strategy's settings
        for strategy in STRATEGY_NAMES:
            try:
                settings = db.get_strategy_settings(user_id, strategy, exchange, account_type)
                defaults = DEFAULT_STRATEGY_SETTINGS.get(strategy, {})
                
                result["strategies"][strategy] = {
                    "enabled": bool(settings.get("enabled", defaults.get("enabled", False))),
                    "percent": settings.get("percent") if settings.get("percent") is not None else defaults.get("percent", global_percent),
                    "sl_percent": settings.get("sl_percent") if settings.get("sl_percent") is not None else defaults.get("sl_percent", global_sl),
                    "tp_percent": settings.get("tp_percent") if settings.get("tp_percent") is not None else defaults.get("tp_percent", global_tp),
                    "leverage": settings.get("leverage") if settings.get("leverage") is not None else defaults.get("leverage", global_leverage),
                    "use_atr": bool(settings.get("use_atr", 0)),
                    "atr_periods": settings.get("atr_periods") or 14,
                    "atr_multiplier_sl": settings.get("atr_multiplier_sl") or 1.5,
                    "atr_trigger_pct": settings.get("atr_trigger_pct") or 2.0,
                    "direction": settings.get("direction", "all"),
                    "order_type": settings.get("order_type", "market"),
                }
            except Exception as e:
                logger.warning(f"Failed to get settings for {strategy}: {e}")
                result["strategies"][strategy] = DEFAULT_STRATEGY_SETTINGS.get(strategy, {}).copy()
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get strategy settings: {e}")
        return {
            "global": {"sl_percent": 30.0, "tp_percent": 25.0, "leverage": 10, "percent": 1.0, "use_atr": False},
            "strategies": {s: DEFAULT_STRATEGY_SETTINGS.get(s, {}).copy() for s in STRATEGY_NAMES}
        }


@router.get("/strategy-settings/{strategy}")
async def get_single_strategy_settings(
    strategy: str,
    exchange: str = Query("bybit"),
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
):
    """Get settings for a specific strategy."""
    user_id = user["user_id"]
    
    # Normalize 'both' -> 'demo'/'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange) or account_type or "demo"
    
    if strategy not in STRATEGY_NAMES:
        raise HTTPException(status_code=400, detail=f"Unknown strategy: {strategy}")
    
    try:
        settings = db.get_strategy_settings(user_id, strategy, exchange, account_type)
        defaults = DEFAULT_STRATEGY_SETTINGS.get(strategy, {})
        user_cfg = db.get_user_config(user_id)
        
        return {
            "strategy": strategy,
            "enabled": bool(settings.get("enabled", defaults.get("enabled", False))),
            "percent": settings.get("percent") if settings.get("percent") is not None else defaults.get("percent", user_cfg.get("percent", 1.0)),
            "sl_percent": settings.get("sl_percent") if settings.get("sl_percent") is not None else defaults.get("sl_percent", user_cfg.get("sl_percent", 30.0)),
            "tp_percent": settings.get("tp_percent") if settings.get("tp_percent") is not None else defaults.get("tp_percent", user_cfg.get("tp_percent", 25.0)),
            "leverage": settings.get("leverage") if settings.get("leverage") is not None else defaults.get("leverage", user_cfg.get("leverage", 10)),
            "use_atr": bool(settings.get("use_atr", 0)),
            "atr_periods": settings.get("atr_periods") or 14,
            "atr_multiplier_sl": settings.get("atr_multiplier_sl") or 1.5,
            "atr_trigger_pct": settings.get("atr_trigger_pct") or 2.0,
            "direction": settings.get("direction", "all"),
            "order_type": settings.get("order_type", "market"),
        }
    except Exception as e:
        logger.error(f"Failed to get {strategy} settings: {e}")
        return DEFAULT_STRATEGY_SETTINGS.get(strategy, {}).copy()


class UpdateStrategySettingsRequest(BaseModel):
    """Request to update strategy settings"""
    strategy: str
    enabled: Optional[bool] = None
    percent: Optional[float] = None
    sl_percent: Optional[float] = None
    tp_percent: Optional[float] = None
    leverage: Optional[int] = None
    use_atr: Optional[bool] = None
    atr_periods: Optional[int] = None
    atr_multiplier_sl: Optional[float] = None
    atr_trigger_pct: Optional[float] = None
    direction: Optional[str] = None
    order_type: Optional[str] = None
    exchange: str = "bybit"
    account_type: str = "demo"


@router.post("/strategy-settings")
async def update_strategy_settings(
    req: UpdateStrategySettingsRequest,
    user: dict = Depends(get_current_user)
):
    """Update settings for a specific strategy or global settings."""
    user_id = user["user_id"]
    
    # Handle global settings update
    if req.strategy == "global":
        try:
            updated = False
            if req.sl_percent is not None:
                db.set_user_field(user_id, "sl_percent", req.sl_percent)
                updated = True
            if req.tp_percent is not None:
                db.set_user_field(user_id, "tp_percent", req.tp_percent)
                updated = True
            if req.leverage is not None:
                db.set_user_field(user_id, "leverage", req.leverage)
                updated = True
            if req.percent is not None:
                db.set_user_field(user_id, "percent", req.percent)
                updated = True
            if req.use_atr is not None:
                db.set_user_field(user_id, "position_use_atr", 1 if req.use_atr else 0)
                updated = True
            if req.atr_periods is not None:
                db.set_user_field(user_id, "atr_periods", req.atr_periods)
                updated = True
            if req.atr_multiplier_sl is not None:
                db.set_user_field(user_id, "atr_multiplier_sl", req.atr_multiplier_sl)
                updated = True
            if req.atr_trigger_pct is not None:
                db.set_user_field(user_id, "atr_trigger_pct", req.atr_trigger_pct)
                updated = True
            
            if updated:
                db.invalidate_user_cache(user_id)
                return {"success": True, "message": "Updated global settings"}
            else:
                return {"success": False, "error": "No settings to update"}
        except Exception as e:
            logger.error(f"Failed to update global settings: {e}")
            return {"success": False, "error": str(e)}
    
    if req.strategy not in STRATEGY_NAMES:
        raise HTTPException(status_code=400, detail=f"Unknown strategy: {req.strategy}")
    
    try:
        # Build settings dict from non-None fields
        settings = {}
        if req.enabled is not None:
            settings["enabled"] = 1 if req.enabled else 0
        if req.percent is not None:
            settings["percent"] = req.percent
        if req.sl_percent is not None:
            settings["sl_percent"] = req.sl_percent
        if req.tp_percent is not None:
            settings["tp_percent"] = req.tp_percent
        if req.leverage is not None:
            settings["leverage"] = req.leverage
        if req.use_atr is not None:
            settings["use_atr"] = 1 if req.use_atr else 0
        if req.atr_periods is not None:
            settings["atr_periods"] = req.atr_periods
        if req.atr_multiplier_sl is not None:
            settings["atr_multiplier_sl"] = req.atr_multiplier_sl
        if req.atr_trigger_pct is not None:
            settings["atr_trigger_pct"] = req.atr_trigger_pct
        if req.direction is not None:
            settings["direction"] = req.direction
        if req.order_type is not None:
            settings["order_type"] = req.order_type
        
        if not settings:
            return {"success": False, "error": "No settings to update"}
        
        # Use db function to update
        success = db.set_strategy_settings_db(user_id, req.strategy, settings, req.exchange, req.account_type)
        
        if success:
            # Notify via WebSocket if available
            return {"success": True, "message": f"Updated {req.strategy} settings"}
        else:
            return {"success": False, "error": "Failed to save settings"}
            
    except Exception as e:
        logger.error(f"Failed to update {req.strategy} settings: {e}")
        return {"success": False, "error": str(e)}


class ToggleStrategyRequest(BaseModel):
    """Request to toggle strategy enabled state"""
    long_enabled: Optional[bool] = None
    short_enabled: Optional[bool] = None
    enabled: Optional[bool] = None  # Sets both long and short
    exchange: str = "bybit"
    account_type: str = "demo"


@router.post("/strategy-settings/{strategy}/toggle")
async def toggle_strategy(
    strategy: str,
    req: ToggleStrategyRequest,
    user: dict = Depends(get_current_user)
):
    """
    Quick toggle for strategy enabled state.
    Used by iOS StrategiesHubView for quick on/off toggles.
    
    Can set:
    - enabled: sets both long_enabled and short_enabled
    - long_enabled / short_enabled: set individually
    """
    user_id = user["user_id"]
    
    if strategy not in STRATEGY_NAMES:
        raise HTTPException(status_code=400, detail=f"Unknown strategy: {strategy}")
    
    # Normalize account type
    account_type = _normalize_both_account_type(req.account_type, req.exchange)
    
    try:
        # Build settings to update
        settings = {}
        
        # If enabled is set, use it for both sides
        if req.enabled is not None:
            settings["long_enabled"] = 1 if req.enabled else 0
            settings["short_enabled"] = 1 if req.enabled else 0
        else:
            # Otherwise use individual side toggles
            if req.long_enabled is not None:
                settings["long_enabled"] = 1 if req.long_enabled else 0
            if req.short_enabled is not None:
                settings["short_enabled"] = 1 if req.short_enabled else 0
        
        if not settings:
            return {"success": False, "error": "No toggle values provided"}
        
        # Save each setting
        for field, value in settings.items():
            db.set_strategy_setting_db(user_id, strategy, field, value, req.exchange, account_type or "demo")
        
        logger.info(f"User {user_id} toggled {strategy}: {settings} (exchange={req.exchange}, account={account_type})")
        
        return {
            "success": True,
            "message": f"Toggled {strategy}",
            "settings": settings
        }
        
    except Exception as e:
        logger.error(f"Failed to toggle {strategy}: {e}")
        return {"success": False, "error": str(e)}


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


# ==================== CHART MARKERS API ====================

@router.get("/chart-markers/{symbol}")
async def get_chart_markers(
    symbol: str,
    days: int = Query(default=30, le=365),
    user: dict = Depends(get_current_user)
):
    """
    Get chart markers for TradingView visualization.
    Returns entries, exits, SL/TP levels for the specified symbol.
    
    Marker types:
    - entry_long: Green arrow up (▲)
    - entry_short: Red arrow down (▼)
    - exit_tp: Star (★) - Take Profit
    - exit_sl: Cross (✖) - Stop-Loss (fixed)
    - exit_atr_sl: Diamond (◆) - ATR Trailing Stop
    - exit_manual: Circle (●) - Manual close
    - exit_liq: Skull (💀) - Liquidation
    """
    try:
        user_id = user.get("user_id") or user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        markers = []
        
        # Get trade logs for this symbol
        from core.db_postgres import execute
        
        # Query trade_logs for this user and symbol
        query = """
            SELECT 
                id, symbol, side, entry_price, exit_price, exit_reason,
                pnl, pnl_pct, strategy, account_type, sl_pct, tp_pct,
                sl_price, tp_price, entry_ts, exit_ts, exit_order_type
            FROM trade_logs
            WHERE user_id = %s AND symbol = %s
            AND exit_ts >= EXTRACT(EPOCH FROM (NOW() - make_interval(days => %s))) * 1000
            ORDER BY exit_ts DESC
            LIMIT 500
        """
        
        trades = execute(query, (user_id, symbol.upper(), days))
        
        for trade in trades:
            trade_id = trade.get("id")
            side = trade.get("side", "Buy")
            entry_price = trade.get("entry_price")
            exit_price = trade.get("exit_price")
            exit_reason = trade.get("exit_reason", "UNKNOWN")
            pnl = trade.get("pnl", 0)
            pnl_pct = trade.get("pnl_pct", 0)
            strategy = trade.get("strategy", "")
            entry_ts = trade.get("entry_ts", 0)
            exit_ts = trade.get("exit_ts", 0)
            sl_price = trade.get("sl_price")
            tp_price = trade.get("tp_price")
            
            # Entry marker
            if entry_price and entry_ts:
                markers.append({
                    "id": f"entry_{trade_id}",
                    "time": int(entry_ts / 1000),  # TradingView uses seconds
                    "type": "entry_long" if side == "Buy" else "entry_short",
                    "price": float(entry_price),
                    "text": f"{'LONG' if side == 'Buy' else 'SHORT'} {strategy}",
                    "color": "#26a69a" if side == "Buy" else "#ef5350",
                    "shape": "arrowUp" if side == "Buy" else "arrowDown",
                    "size": "small",
                })
            
            # Exit marker
            if exit_price and exit_ts:
                # Determine marker style based on exit reason
                marker_configs = {
                    "TP": {"color": "#00c853", "shape": "star", "label": "TP"},
                    "SL": {"color": "#ff1744", "shape": "cross", "label": "SL"},
                    "ATR_SL": {"color": "#ff9800", "shape": "diamond", "label": "ATR"},
                    "TRAILING": {"color": "#ff9800", "shape": "diamond", "label": "TRAIL"},
                    "MANUAL": {"color": "#9c27b0", "shape": "circle", "label": "MAN"},
                    "LIQ": {"color": "#000000", "shape": "skull", "label": "LIQ"},
                    "ADL": {"color": "#607d8b", "shape": "cross", "label": "ADL"},
                    "UNKNOWN": {"color": "#9e9e9e", "shape": "circle", "label": "?"},
                }
                
                config = marker_configs.get(exit_reason, marker_configs["UNKNOWN"])
                
                markers.append({
                    "id": f"exit_{trade_id}",
                    "time": int(exit_ts / 1000),
                    "type": f"exit_{exit_reason.lower()}",
                    "price": float(exit_price),
                    "text": f"{config['label']} {pnl:+.2f}$",
                    "color": config["color"],
                    "shape": config["shape"],
                    "size": "small",
                    "pnl": float(pnl),
                    "pnl_pct": float(pnl_pct),
                })
            
            # SL/TP level lines (for open positions or last trade)
            if sl_price:
                markers.append({
                    "id": f"sl_level_{trade_id}",
                    "time": int(entry_ts / 1000) if entry_ts else int(time.time()),
                    "type": "sl_level",
                    "price": float(sl_price),
                    "text": "SL",
                    "color": "#ff1744",
                    "lineStyle": "dashed",
                })
            
            if tp_price:
                markers.append({
                    "id": f"tp_level_{trade_id}",
                    "time": int(entry_ts / 1000) if entry_ts else int(time.time()),
                    "type": "tp_level", 
                    "price": float(tp_price),
                    "text": "TP",
                    "color": "#00c853",
                    "lineStyle": "dashed",
                })
        
        # Also get active positions for current SL/TP levels
        from db import get_active_positions, get_trading_mode, get_exchange_type
        
        exchange = get_exchange_type(user_id) or "bybit"
        trading_mode = get_trading_mode(user_id)
        if exchange == "hyperliquid":
            account_types = ["testnet"] if trading_mode == "demo" else ["mainnet"] if trading_mode == "real" else ["testnet", "mainnet"]
        else:
            account_types = ["demo"] if trading_mode == "demo" else ["real"] if trading_mode == "real" else ["demo", "real"]
        
        for acc_type in account_types:
            positions = get_active_positions(user_id, account_type=acc_type, exchange=exchange)
            active_pos = next((p for p in positions if p.get("symbol", "").upper() == symbol.upper()), None)
            if active_pos:
                entry_price = active_pos.get("entry_price")
                sl_price = active_pos.get("sl_price")
                tp_price = active_pos.get("tp_price")
                side = active_pos.get("side", "Buy")
                strategy = active_pos.get("strategy", "")
                open_ts = active_pos.get("open_ts")
                
                # Parse timestamp if string
                if isinstance(open_ts, str):
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(open_ts.replace('Z', '+00:00'))
                        open_ts = int(dt.timestamp())
                    except (ValueError, TypeError, AttributeError):
                        open_ts = int(time.time())
                elif open_ts is None:
                    open_ts = int(time.time())
                
                # Active position entry
                if entry_price:
                    markers.append({
                        "id": f"active_entry_{acc_type}",
                        "time": int(open_ts),
                        "type": "active_entry",
                        "price": float(entry_price),
                        "text": f"{'LONG' if side == 'Buy' else 'SHORT'} {strategy} (active)",
                        "color": "#26a69a" if side == "Buy" else "#ef5350",
                        "shape": "arrowUp" if side == "Buy" else "arrowDown",
                        "size": "normal",
                        "isActive": True,
                    })
                
                # Active SL level
                if sl_price:
                    markers.append({
                        "id": f"active_sl_{acc_type}",
                        "time": int(open_ts),
                        "type": "active_sl",
                        "price": float(sl_price),
                        "text": "Active SL",
                        "color": "#ff1744",
                        "lineStyle": "solid",
                        "isActive": True,
                    })
                
                # Active TP level
                if tp_price:
                    markers.append({
                        "id": f"active_tp_{acc_type}",
                        "time": int(open_ts),
                        "type": "active_tp",
                        "price": float(tp_price),
                        "text": "Active TP",
                        "color": "#00c853",
                        "lineStyle": "solid",
                        "isActive": True,
                    })
        
        return {
            "symbol": symbol.upper(),
            "markers": markers,
            "count": len(markers),
            "timestamp": int(time.time() * 1000)
        }
        
    except Exception as e:
        logger.exception(f"Error getting chart markers for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))