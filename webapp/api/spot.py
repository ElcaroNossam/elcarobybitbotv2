"""
Spot Trading API for WebApp/iOS
================================

Endpoints for spot trading operations:
- GET /spot/balance - Get spot balances for all coins
- GET /spot/holdings - Get portfolio breakdown with USD values
- GET /spot/ticker/{symbol} - Get current price for a symbol
- POST /spot/buy - Place spot buy order
- POST /spot/sell - Place spot sell order
- GET /spot/history - Get spot trading history
- GET /spot/settings - Get spot DCA settings
- PUT /spot/settings - Update spot DCA settings
"""
import os
import sys
import json
import logging
import aiohttp
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import db

router = APIRouter()

# Import auth dependencies
from webapp.api.auth import get_current_user

# Bybit API URLs
BYBIT_DEMO_URL = "https://api-demo.bybit.com"
BYBIT_REAL_URL = "https://api.bybit.com"


# ==================== MODELS ====================

class SpotOrderRequest(BaseModel):
    symbol: str  # e.g., "BTCUSDT"
    side: str    # "buy" or "sell"
    quantity: Optional[float] = None  # In base coin (e.g., BTC)
    quote_amount: Optional[float] = None  # In quote coin (e.g., USDT)
    order_type: str = "market"  # "market" or "limit"
    price: Optional[float] = None  # Required for limit orders


class SpotSettingsRequest(BaseModel):
    spot_enabled: bool = False
    dca_enabled: bool = False
    dca_frequency: str = "daily"  # daily, weekly, monthly
    dca_amount: float = 100.0
    dca_coins: List[str] = ["BTC", "ETH"]
    dca_strategy: str = "fixed"  # fixed, value_avg, fear_greed, dip_buy


# ==================== HELPER FUNCTIONS ====================

async def bybit_spot_request(user_id: int, method: str, endpoint: str, 
                              params: dict = None, body: dict = None,
                              account_type: str = "demo") -> dict:
    """Make authenticated request to Bybit Spot API."""
    import hmac
    import hashlib
    import time
    
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
    
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    
    # Build signature
    if method == "GET":
        query_string = "&".join([f"{k}={v}" for k, v in (params or {}).items()])
        sign_payload = f"{timestamp}{api_key}{recv_window}{query_string}"
        url = f"{base_url}{endpoint}?{query_string}" if query_string else f"{base_url}{endpoint}"
        body_data = None
    else:
        sign_payload = f"{timestamp}{api_key}{recv_window}{json.dumps(body or {})}"
        url = f"{base_url}{endpoint}"
        body_data = json.dumps(body or {})
    
    signature = hmac.new(
        api_secret.encode('utf-8'),
        sign_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "X-BAPI-SIGN": signature,
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        if method == "GET":
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
        else:
            async with session.post(url, headers=headers, data=body_data) as resp:
                data = await resp.json()
    
    if data.get("retCode") != 0:
        raise HTTPException(status_code=400, detail=data.get("retMsg", "Bybit API error"))
    
    return data.get("result", {})


# ==================== ENDPOINTS ====================

@router.get("/balance")
async def get_spot_balance(
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
):
    """Get spot account balances for all coins with non-zero balance."""
    user_id = user["user_id"]
    
    try:
        result = await bybit_spot_request(
            user_id, "GET", "/v5/account/wallet-balance",
            params={"accountType": "UNIFIED"},
            account_type=account_type
        )
        
        balances = []
        for acct in result.get("list", []):
            for coin in acct.get("coin", []):
                coin_name = coin.get("coin", "")
                wallet_balance = float(coin.get("walletBalance") or 0)
                
                if wallet_balance > 0.00000001:  # Filter dust
                    balances.append({
                        "coin": coin_name,
                        "balance": wallet_balance,
                        "available": float(coin.get("availableToWithdraw") or 0),
                        "locked": float(coin.get("locked") or 0),
                        "usd_value": float(coin.get("usdValue") or 0),
                    })
        
        # Sort by USD value descending
        balances.sort(key=lambda x: x["usd_value"], reverse=True)
        
        return {
            "success": True,
            "balances": balances,
            "total_usd": sum(b["usd_value"] for b in balances)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_spot_balance error: {e}")
        return {"success": False, "error": str(e), "balances": []}


@router.get("/holdings")
async def get_spot_holdings(
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
):
    """Get portfolio holdings with allocation percentages."""
    user_id = user["user_id"]
    
    try:
        result = await bybit_spot_request(
            user_id, "GET", "/v5/account/wallet-balance",
            params={"accountType": "UNIFIED"},
            account_type=account_type
        )
        
        holdings = []
        total_usd = 0.0
        
        for acct in result.get("list", []):
            for coin in acct.get("coin", []):
                usd_value = float(coin.get("usdValue") or 0)
                if usd_value > 0.01:  # $0.01 minimum
                    total_usd += usd_value
                    holdings.append({
                        "coin": coin.get("coin", ""),
                        "balance": float(coin.get("walletBalance") or 0),
                        "usd_value": usd_value,
                    })
        
        # Calculate allocation percentages
        for h in holdings:
            h["allocation"] = (h["usd_value"] / total_usd * 100) if total_usd > 0 else 0
        
        # Sort by allocation descending
        holdings.sort(key=lambda x: x["allocation"], reverse=True)
        
        return {
            "success": True,
            "holdings": holdings,
            "total_usd": total_usd,
            "positions_count": len(holdings)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_spot_holdings error: {e}")
        return {"success": False, "error": str(e), "holdings": []}


@router.get("/ticker/{symbol}")
async def get_spot_ticker(
    symbol: str,
    user: dict = Depends(get_current_user)
):
    """Get current price for a spot symbol."""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{BYBIT_REAL_URL}/v5/market/tickers"
            params = {"category": "spot", "symbol": symbol.upper()}
            
            async with session.get(url, params=params) as resp:
                data = await resp.json()
        
        if data.get("retCode") != 0:
            return {"success": False, "error": data.get("retMsg")}
        
        tickers = data.get("result", {}).get("list", [])
        if not tickers:
            return {"success": False, "error": f"Symbol {symbol} not found"}
        
        t = tickers[0]
        return {
            "success": True,
            "symbol": t.get("symbol"),
            "last_price": float(t.get("lastPrice") or 0),
            "bid": float(t.get("bid1Price") or 0),
            "ask": float(t.get("ask1Price") or 0),
            "high_24h": float(t.get("highPrice24h") or 0),
            "low_24h": float(t.get("lowPrice24h") or 0),
            "volume_24h": float(t.get("volume24h") or 0),
            "change_24h": float(t.get("price24hPcnt") or 0) * 100,
        }
        
    except Exception as e:
        logger.error(f"get_spot_ticker error: {e}")
        return {"success": False, "error": str(e)}


@router.post("/buy")
async def spot_buy(
    request: SpotOrderRequest,
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
):
    """Place a spot buy order."""
    user_id = user["user_id"]
    
    if not request.quantity and not request.quote_amount:
        raise HTTPException(status_code=400, detail="Either quantity or quote_amount required")
    
    try:
        body = {
            "category": "spot",
            "symbol": request.symbol.upper(),
            "side": "Buy",
            "orderType": "Market" if request.order_type == "market" else "Limit",
        }
        
        # Quantity in base coin or quote coin
        if request.quantity:
            body["qty"] = str(request.quantity)
        elif request.quote_amount:
            body["marketUnit"] = "quoteCoin"
            body["qty"] = str(request.quote_amount)
        
        if request.order_type == "limit" and request.price:
            body["price"] = str(request.price)
        
        result = await bybit_spot_request(
            user_id, "POST", "/v5/order/create",
            body=body,
            account_type=account_type
        )
        
        return {
            "success": True,
            "order_id": result.get("orderId"),
            "order_link_id": result.get("orderLinkId"),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"spot_buy error: {e}")
        return {"success": False, "error": str(e)}


@router.post("/sell")
async def spot_sell(
    request: SpotOrderRequest,
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
):
    """Place a spot sell order."""
    user_id = user["user_id"]
    
    if not request.quantity:
        raise HTTPException(status_code=400, detail="Quantity required for sell orders")
    
    try:
        body = {
            "category": "spot",
            "symbol": request.symbol.upper(),
            "side": "Sell",
            "orderType": "Market" if request.order_type == "market" else "Limit",
            "qty": str(request.quantity),
        }
        
        if request.order_type == "limit" and request.price:
            body["price"] = str(request.price)
        
        result = await bybit_spot_request(
            user_id, "POST", "/v5/order/create",
            body=body,
            account_type=account_type
        )
        
        return {
            "success": True,
            "order_id": result.get("orderId"),
            "order_link_id": result.get("orderLinkId"),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"spot_sell error: {e}")
        return {"success": False, "error": str(e)}


@router.get("/history")
async def get_spot_history(
    account_type: str = Query("demo"),
    symbol: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    user: dict = Depends(get_current_user)
):
    """Get spot trading history."""
    user_id = user["user_id"]
    
    try:
        params = {
            "category": "spot",
            "limit": str(limit),
        }
        if symbol:
            params["symbol"] = symbol.upper()
        
        result = await bybit_spot_request(
            user_id, "GET", "/v5/execution/list",
            params=params,
            account_type=account_type
        )
        
        trades = []
        for exec in result.get("list", []):
            trades.append({
                "symbol": exec.get("symbol"),
                "side": exec.get("side"),
                "price": float(exec.get("execPrice") or 0),
                "qty": float(exec.get("execQty") or 0),
                "value": float(exec.get("execValue") or 0),
                "fee": float(exec.get("execFee") or 0),
                "fee_currency": exec.get("feeCurrency"),
                "order_id": exec.get("orderId"),
                "exec_time": exec.get("execTime"),
            })
        
        return {
            "success": True,
            "trades": trades,
            "count": len(trades)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_spot_history error: {e}")
        return {"success": False, "error": str(e), "trades": []}


@router.get("/settings")
async def get_spot_settings(
    user: dict = Depends(get_current_user)
):
    """Get spot DCA settings for user."""
    user_id = user["user_id"]
    
    try:
        cfg = db.get_user_config(user_id)
        
        # Parse spot_settings if it's a JSON string
        spot_settings = cfg.get("spot_settings", {})
        if isinstance(spot_settings, str):
            try:
                spot_settings = json.loads(spot_settings)
            except:
                spot_settings = {}
        
        return {
            "success": True,
            "spot_enabled": bool(cfg.get("spot_enabled", 0)),
            "dca_enabled": bool(spot_settings.get("dca_enabled", False)),
            "dca_frequency": spot_settings.get("dca_frequency", "daily"),
            "dca_amount": float(spot_settings.get("dca_amount", 100)),
            "dca_coins": spot_settings.get("dca_coins", ["BTC", "ETH"]),
            "dca_strategy": spot_settings.get("dca_strategy", "fixed"),
        }
        
    except Exception as e:
        logger.error(f"get_spot_settings error: {e}")
        return {"success": False, "error": str(e)}


@router.put("/settings")
async def update_spot_settings(
    settings: SpotSettingsRequest,
    user: dict = Depends(get_current_user)
):
    """Update spot DCA settings."""
    user_id = user["user_id"]
    
    try:
        # Save spot_enabled flag
        db.set_user_field(user_id, "spot_enabled", 1 if settings.spot_enabled else 0)
        
        # Save spot_settings as JSON
        spot_settings = {
            "dca_enabled": settings.dca_enabled,
            "dca_frequency": settings.dca_frequency,
            "dca_amount": settings.dca_amount,
            "dca_coins": settings.dca_coins,
            "dca_strategy": settings.dca_strategy,
        }
        db.set_user_field(user_id, "spot_settings", json.dumps(spot_settings))
        
        return {"success": True, "message": "Settings updated"}
        
    except Exception as e:
        logger.error(f"update_spot_settings error: {e}")
        return {"success": False, "error": str(e)}


@router.get("/symbols")
async def get_spot_symbols(
    user: dict = Depends(get_current_user)
):
    """Get list of tradeable spot symbols."""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{BYBIT_REAL_URL}/v5/market/instruments-info"
            params = {"category": "spot", "limit": "500"}
            
            async with session.get(url, params=params) as resp:
                data = await resp.json()
        
        if data.get("retCode") != 0:
            return {"success": False, "error": data.get("retMsg")}
        
        symbols = []
        for s in data.get("result", {}).get("list", []):
            if s.get("quoteCoin") == "USDT":  # Only USDT pairs
                symbols.append({
                    "symbol": s.get("symbol"),
                    "base_coin": s.get("baseCoin"),
                    "quote_coin": s.get("quoteCoin"),
                    "min_qty": float(s.get("lotSizeFilter", {}).get("minOrderQty") or 0),
                    "min_notional": float(s.get("lotSizeFilter", {}).get("minOrderAmt") or 0),
                })
        
        # Sort alphabetically
        symbols.sort(key=lambda x: x["symbol"])
        
        return {
            "success": True,
            "symbols": symbols,
            "count": len(symbols)
        }
        
    except Exception as e:
        logger.error(f"get_spot_symbols error: {e}")
        return {"success": False, "error": str(e), "symbols": []}
