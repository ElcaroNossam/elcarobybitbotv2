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
    dca_strategy: str = "fixed"  # fixed, value_avg, fear_greed, dip_buy, crash_boost, momentum, rsi_based
    portfolio: str = "custom"  # Portfolio preset name
    tp_enabled: bool = False
    tp_profile: str = "balanced"  # TP profile name
    trailing_tp_enabled: bool = False
    trailing_activation_pct: float = 15.0
    trailing_trail_pct: float = 5.0
    profit_lock_enabled: bool = False
    profit_lock_trigger_pct: float = 30.0
    profit_lock_pct: float = 50.0
    smart_rebalance_enabled: bool = False
    rebalance_threshold_pct: float = 10.0


class SpotDCAExecuteRequest(BaseModel):
    coin: str
    amount: float
    strategy: str = "fixed"


class SpotPortfolioRebalanceRequest(BaseModel):
    portfolio: str = "blue_chip"
    total_investment: float = 100.0


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


# ==================== ADVANCED SPOT FEATURES ====================

# Portfolio presets (imported from bot.py constants)
SPOT_PORTFOLIOS = {
    "blue_chip": {"name": "Blue Chips", "emoji": "💎", "coins": {"BTC": 50, "ETH": 30, "BNB": 10, "SOL": 10}, "risk_level": "low"},
    "defi": {"name": "DeFi", "emoji": "🏦", "coins": {"UNI": 25, "AAVE": 25, "MKR": 20, "LINK": 15, "SNX": 15}, "risk_level": "medium"},
    "layer2": {"name": "Layer 2", "emoji": "⚡", "coins": {"MATIC": 30, "ARB": 25, "OP": 25, "IMX": 20}, "risk_level": "medium"},
    "ai_narrative": {"name": "AI & Data", "emoji": "🤖", "coins": {"FET": 25, "RNDR": 25, "TAO": 20, "NEAR": 15, "GRT": 15}, "risk_level": "high"},
    "gaming": {"name": "Gaming", "emoji": "🎮", "coins": {"AXS": 25, "SAND": 20, "MANA": 20, "GALA": 20, "ENJ": 15}, "risk_level": "high"},
    "meme": {"name": "Memecoins", "emoji": "🐕", "coins": {"DOGE": 35, "SHIB": 25, "PEPE": 20, "FLOKI": 10, "WIF": 10}, "risk_level": "very_high"},
    "l1_killers": {"name": "L1 Killers", "emoji": "⚔️", "coins": {"SOL": 30, "AVAX": 25, "NEAR": 20, "SUI": 15, "APT": 10}, "risk_level": "medium"},
    "rwa": {"name": "RWA", "emoji": "🏛️", "coins": {"ONDO": 30, "MKR": 25, "SNX": 20, "LINK": 15, "GRT": 10}, "risk_level": "medium"},
    "infrastructure": {"name": "Infra", "emoji": "🔧", "coins": {"LINK": 30, "GRT": 25, "FIL": 20, "AR": 15, "ATOM": 10}, "risk_level": "medium"},
    "btc_only": {"name": "BTC Only", "emoji": "₿", "coins": {"BTC": 100}, "risk_level": "low"},
    "eth_btc": {"name": "ETH+BTC", "emoji": "💰", "coins": {"BTC": 60, "ETH": 40}, "risk_level": "low"},
    "custom": {"name": "Custom", "emoji": "⚙️", "coins": {}, "risk_level": "custom"},
}

SMART_DCA_STRATEGIES = {
    "fixed": {"name": "Fixed DCA", "emoji": "📊", "description": "Same amount at regular intervals"},
    "value_avg": {"name": "Value Averaging", "emoji": "📈", "description": "Buy more when price drops, less when rises"},
    "fear_greed": {"name": "Fear & Greed", "emoji": "😱", "description": "Buy more during extreme fear"},
    "dip_buy": {"name": "Dip Buying", "emoji": "📉", "description": "Only buy on significant dips"},
    "crash_boost": {"name": "Crash Boost", "emoji": "🚨", "description": "3x buy when price drops >15% in 24h"},
    "momentum": {"name": "Momentum", "emoji": "🚀", "description": "Buy more in uptrends, less in downtrends"},
    "rsi_based": {"name": "RSI Smart", "emoji": "📐", "description": "Buy more when RSI < 30 (oversold)"},
}

SPOT_TP_PROFILES = {
    "conservative": {"name": "Conservative", "emoji": "🐢", "levels": [{"gain_pct": 10, "sell_pct": 25}, {"gain_pct": 20, "sell_pct": 25}, {"gain_pct": 35, "sell_pct": 25}, {"gain_pct": 50, "sell_pct": 25}]},
    "balanced": {"name": "Balanced", "emoji": "⚖️", "levels": [{"gain_pct": 20, "sell_pct": 20}, {"gain_pct": 50, "sell_pct": 25}, {"gain_pct": 100, "sell_pct": 30}, {"gain_pct": 200, "sell_pct": 25}]},
    "aggressive": {"name": "Aggressive", "emoji": "🦁", "levels": [{"gain_pct": 50, "sell_pct": 15}, {"gain_pct": 100, "sell_pct": 20}, {"gain_pct": 200, "sell_pct": 25}, {"gain_pct": 500, "sell_pct": 40}]},
    "moonbag": {"name": "Moonbag", "emoji": "🌙", "levels": [{"gain_pct": 100, "sell_pct": 50}, {"gain_pct": 500, "sell_pct": 25}]},
}


@router.get("/portfolios")
async def get_portfolios(
    user: dict = Depends(get_current_user)
):
    """Get available portfolio presets with coin allocations."""
    return {
        "success": True,
        "portfolios": SPOT_PORTFOLIOS,
        "count": len(SPOT_PORTFOLIOS)
    }


@router.get("/strategies")
async def get_strategies(
    user: dict = Depends(get_current_user)
):
    """Get available DCA strategies with descriptions."""
    return {
        "success": True,
        "strategies": SMART_DCA_STRATEGIES,
        "count": len(SMART_DCA_STRATEGIES)
    }


@router.get("/tp-profiles")
async def get_tp_profiles(
    user: dict = Depends(get_current_user)
):
    """Get available Take Profit profiles."""
    return {
        "success": True,
        "profiles": SPOT_TP_PROFILES,
        "count": len(SPOT_TP_PROFILES)
    }


@router.get("/performance")
async def get_spot_performance(
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
):
    """Get spot portfolio performance metrics."""
    user_id = user["user_id"]
    
    try:
        cfg = db.get_user_config(user_id)
        spot_settings = cfg.get("spot_settings", {})
        if isinstance(spot_settings, str):
            try:
                spot_settings = json.loads(spot_settings)
            except:
                spot_settings = {}
        
        purchase_history = spot_settings.get("purchase_history", {})
        total_invested = spot_settings.get("total_invested", 0.0)
        
        # Get current balances
        result = await bybit_spot_request(
            user_id, "GET", "/v5/account/wallet-balance",
            params={"accountType": "UNIFIED"},
            account_type=account_type
        )
        
        holdings = []
        total_current_value = 0.0
        total_unrealized_pnl = 0.0
        
        for acct in result.get("list", []):
            for coin in acct.get("coin", []):
                coin_name = coin.get("coin", "")
                wallet_balance = float(coin.get("walletBalance") or 0)
                usd_value = float(coin.get("usdValue") or 0)
                
                if wallet_balance > 0.00000001 and coin_name != "USDT":
                    # Get purchase history for this coin
                    coin_history = purchase_history.get(coin_name, {})
                    avg_price = coin_history.get("avg_price", 0)
                    total_cost = coin_history.get("total_cost", 0)
                    
                    # Calculate unrealized PnL
                    unrealized_pnl = usd_value - total_cost if total_cost > 0 else 0
                    pnl_pct = ((usd_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
                    
                    holdings.append({
                        "coin": coin_name,
                        "balance": wallet_balance,
                        "usd_value": usd_value,
                        "avg_price": avg_price,
                        "total_cost": total_cost,
                        "unrealized_pnl": unrealized_pnl,
                        "pnl_pct": pnl_pct,
                    })
                    
                    total_current_value += usd_value
                    total_unrealized_pnl += unrealized_pnl
        
        # Sort by USD value
        holdings.sort(key=lambda x: x["usd_value"], reverse=True)
        
        # Calculate overall ROI
        roi_pct = ((total_current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
        
        return {
            "success": True,
            "total_invested": total_invested,
            "total_current_value": total_current_value,
            "total_unrealized_pnl": total_unrealized_pnl,
            "roi_pct": roi_pct,
            "holdings": holdings,
            "holdings_count": len(holdings),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_spot_performance error: {e}")
        return {"success": False, "error": str(e)}


@router.post("/execute-dca")
async def execute_spot_dca(
    request: SpotDCAExecuteRequest,
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
):
    """Execute a single DCA buy with specified strategy."""
    user_id = user["user_id"]
    
    try:
        symbol = f"{request.coin}USDT"
        
        # Get ticker for execution
        async with aiohttp.ClientSession() as session:
            url = f"{BYBIT_REAL_URL}/v5/market/tickers"
            params = {"category": "spot", "symbol": symbol}
            
            async with session.get(url, params=params) as resp:
                data = await resp.json()
        
        if data.get("retCode") != 0:
            return {"success": False, "error": data.get("retMsg")}
        
        tickers = data.get("result", {}).get("list", [])
        if not tickers:
            return {"success": False, "error": f"Symbol {symbol} not found"}
        
        current_price = float(tickers[0].get("lastPrice", 0))
        
        # Calculate adjusted amount based on strategy
        amount = request.amount
        if request.strategy == "fear_greed":
            # Would need to fetch Fear & Greed index
            fg_index = 50  # Default neutral
            if fg_index < 25:
                amount *= 2.0
            elif fg_index > 75:
                amount *= 0.5
        elif request.strategy == "crash_boost":
            change_24h = float(tickers[0].get("price24hPcnt", 0)) * 100
            if change_24h <= -15:
                amount *= 3.0
            elif change_24h <= -10:
                amount *= 2.0
        
        # Place buy order
        body = {
            "category": "spot",
            "symbol": symbol,
            "side": "Buy",
            "orderType": "Market",
            "marketUnit": "quoteCoin",
            "qty": str(amount),
        }
        
        result = await bybit_spot_request(
            user_id, "POST", "/v5/order/create",
            body=body,
            account_type=account_type
        )
        
        qty_bought = amount / current_price
        
        # Update purchase history
        try:
            cfg = db.get_user_config(user_id)
            spot_settings = cfg.get("spot_settings", {})
            if isinstance(spot_settings, str):
                spot_settings = json.loads(spot_settings)
            
            purchase_history = spot_settings.get("purchase_history", {})
            if request.coin not in purchase_history:
                purchase_history[request.coin] = {"total_qty": 0, "total_cost": 0, "avg_price": 0}
            
            coin_history = purchase_history[request.coin]
            coin_history["total_qty"] = coin_history.get("total_qty", 0) + qty_bought
            coin_history["total_cost"] = coin_history.get("total_cost", 0) + amount
            coin_history["avg_price"] = coin_history["total_cost"] / coin_history["total_qty"] if coin_history["total_qty"] > 0 else 0
            
            purchase_history[request.coin] = coin_history
            spot_settings["purchase_history"] = purchase_history
            spot_settings["total_invested"] = spot_settings.get("total_invested", 0) + amount
            
            db.set_user_field(user_id, "spot_settings", json.dumps(spot_settings))
        except Exception as e:
            logger.warning(f"Failed to update purchase history: {e}")
        
        return {
            "success": True,
            "coin": request.coin,
            "amount_spent": amount,
            "qty_bought": qty_bought,
            "price": current_price,
            "strategy": request.strategy,
            "order_id": result.get("orderId"),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"execute_spot_dca error: {e}")
        return {"success": False, "error": str(e)}


@router.post("/rebalance")
async def rebalance_portfolio(
    request: SpotPortfolioRebalanceRequest,
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
):
    """Rebalance portfolio to match target allocation."""
    user_id = user["user_id"]
    
    try:
        portfolio = SPOT_PORTFOLIOS.get(request.portfolio)
        if not portfolio:
            return {"success": False, "error": f"Unknown portfolio: {request.portfolio}"}
        
        target_allocation = portfolio.get("coins", {})
        if not target_allocation:
            return {"success": False, "error": "Portfolio has no allocation defined"}
        
        # Get current holdings
        result = await bybit_spot_request(
            user_id, "GET", "/v5/account/wallet-balance",
            params={"accountType": "UNIFIED"},
            account_type=account_type
        )
        
        # Calculate current values
        current_holdings = {}
        usdt_balance = 0.0
        
        for acct in result.get("list", []):
            for coin in acct.get("coin", []):
                coin_name = coin.get("coin", "")
                usd_value = float(coin.get("usdValue") or 0)
                
                if coin_name == "USDT":
                    usdt_balance = usd_value
                elif usd_value > 0.01:
                    current_holdings[coin_name] = usd_value
        
        total_portfolio = sum(current_holdings.values()) + usdt_balance + request.total_investment
        
        # Calculate trades needed
        trades = []
        
        for coin, target_pct in target_allocation.items():
            target_value = total_portfolio * (target_pct / 100)
            current_value = current_holdings.get(coin, 0)
            diff = target_value - current_value
            
            if abs(diff) > 5:  # Minimum $5 trade
                if diff > 0:
                    trades.append({"coin": coin, "action": "buy", "amount": diff})
                else:
                    trades.append({"coin": coin, "action": "sell", "amount": abs(diff)})
        
        # Execute trades
        results = []
        for trade in trades:
            try:
                symbol = f"{trade['coin']}USDT"
                
                if trade["action"] == "buy":
                    body = {
                        "category": "spot",
                        "symbol": symbol,
                        "side": "Buy",
                        "orderType": "Market",
                        "marketUnit": "quoteCoin",
                        "qty": str(trade["amount"]),
                    }
                else:
                    # For sell, need to calculate quantity from value
                    async with aiohttp.ClientSession() as session:
                        url = f"{BYBIT_REAL_URL}/v5/market/tickers"
                        params = {"category": "spot", "symbol": symbol}
                        async with session.get(url, params=params) as resp:
                            ticker_data = await resp.json()
                    
                    tickers = ticker_data.get("result", {}).get("list", [])
                    if tickers:
                        price = float(tickers[0].get("lastPrice", 0))
                        qty = trade["amount"] / price if price > 0 else 0
                        
                        body = {
                            "category": "spot",
                            "symbol": symbol,
                            "side": "Sell",
                            "orderType": "Market",
                            "qty": str(qty),
                        }
                    else:
                        continue
                
                order_result = await bybit_spot_request(
                    user_id, "POST", "/v5/order/create",
                    body=body,
                    account_type=account_type
                )
                
                results.append({
                    "coin": trade["coin"],
                    "action": trade["action"],
                    "amount": trade["amount"],
                    "success": True,
                    "order_id": order_result.get("orderId"),
                })
                
            except Exception as e:
                results.append({
                    "coin": trade["coin"],
                    "action": trade["action"],
                    "amount": trade["amount"],
                    "success": False,
                    "error": str(e),
                })
        
        return {
            "success": True,
            "portfolio": request.portfolio,
            "trades_executed": len([r for r in results if r.get("success")]),
            "trades_failed": len([r for r in results if not r.get("success")]),
            "results": results,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"rebalance_portfolio error: {e}")
        return {"success": False, "error": str(e)}


@router.get("/fear-greed")
async def get_fear_greed_index(
    user: dict = Depends(get_current_user)
):
    """Get current Fear & Greed Index."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.alternative.me/fng/",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("data") and len(data["data"]) > 0:
                        item = data["data"][0]
                        return {
                            "success": True,
                            "value": int(item.get("value", 50)),
                            "classification": item.get("value_classification", "Neutral"),
                            "timestamp": item.get("timestamp"),
                        }
        
        return {"success": False, "error": "Could not fetch Fear & Greed Index"}
        
    except Exception as e:
        logger.error(f"get_fear_greed_index error: {e}")
        return {"success": False, "error": str(e)}

