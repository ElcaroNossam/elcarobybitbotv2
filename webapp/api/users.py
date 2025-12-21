"""
Users API - Settings, Profile, Exchange switching, API Keys
"""
import os
import sys
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import db

router = APIRouter()
logger = logging.getLogger(__name__)

from webapp.api.auth import get_current_user


class ExchangeSwitch(BaseModel):
    exchange: str


class LanguageChange(BaseModel):
    language: str


class SettingsUpdate(BaseModel):
    exchange: str = "bybit"
    settings: dict


class BybitApiKeys(BaseModel):
    account_type: str  # 'demo' or 'real'
    api_key: str
    api_secret: str


class HLApiKeys(BaseModel):
    wallet_address: str
    private_key: Optional[str] = None
    vault_address: Optional[str] = None
    testnet: bool = False


@router.get("/settings")
async def get_settings(
    exchange: str = Query("bybit"),
    user: dict = Depends(get_current_user)
):
    """Get user settings for specified exchange."""
    user_id = user["user_id"]
    creds = db.get_all_user_credentials(user_id)
    
    if exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        return {
            "percent": creds.get("hl_percent", 5),
            "leverage": creds.get("hl_leverage", 10),
            "tp_percent": creds.get("hl_tp_percent", 2),
            "sl_percent": creds.get("hl_sl_percent", 1),
            "testnet": hl_creds.get("hl_testnet", False),
            "has_key": bool(hl_creds.get("hl_private_key")),
            "wallet": hl_creds.get("hl_wallet_address", "")[:10] + "..." if hl_creds.get("hl_wallet_address") else None,
        }
    else:
        return {
            "percent": creds.get("percent", 5),
            "leverage": creds.get("leverage", 10),
            "tp_percent": creds.get("tp_percent", 2),
            "sl_percent": creds.get("sl_percent", 1),
            "trading_mode": creds.get("trading_mode", "demo"),
            "enable_scryptomera": creds.get("enable_scryptomera", False),
            "enable_elcaro": creds.get("enable_elcaro", False),
            "enable_wyckoff": creds.get("enable_wyckoff", False),
            "enable_scalper": creds.get("enable_scalper", False),
            "limit_only": creds.get("limit_only", False),
            "use_oi": creds.get("use_oi", False),
            "use_rsi_bb": creds.get("use_rsi_bb", False),
            "use_atr": creds.get("use_atr", False),
            "has_demo_key": bool(creds.get("demo_api_key")),
            "has_real_key": bool(creds.get("real_api_key")),
        }


@router.put("/settings")
async def update_settings(
    data: SettingsUpdate,
    user: dict = Depends(get_current_user)
):
    """Update user settings."""
    user_id = user["user_id"]
    
    for key, value in data.settings.items():
        if data.exchange == "hyperliquid":
            # HL specific settings
            if key in ["percent", "leverage", "tp_percent", "sl_percent"]:
                db.set_user_field(user_id, f"hl_{key}", value)
        else:
            # Bybit settings
            if key in ["percent", "leverage", "tp_percent", "sl_percent", 
                       "enable_scryptomera", "enable_elcaro", "enable_wyckoff", 
                       "enable_scalper", "limit_only", "use_oi", "use_rsi_bb", "use_atr"]:
                db.set_user_field(user_id, key, value)
    
    return {"success": True}


@router.post("/exchange")
async def switch_exchange(
    data: ExchangeSwitch,
    user: dict = Depends(get_current_user)
):
    """
    Switch active exchange with dynamic reconnection.
    Invalidates cached connections and tests new exchange connectivity.
    """
    user_id = user["user_id"]
    
    if data.exchange not in ["bybit", "hyperliquid"]:
        raise HTTPException(status_code=400, detail="Invalid exchange")
    
    # Get current exchange for comparison
    old_exchange = db.get_exchange_type(user_id)
    
    # Check if HL is configured before switching
    if data.exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        if not hl_creds.get("hl_private_key"):
            raise HTTPException(status_code=400, detail="HyperLiquid not configured. Add your wallet and private key first.")
    
    # Check if Bybit is configured
    if data.exchange == "bybit":
        creds = db.get_all_user_credentials(user_id)
        if not creds.get("demo_api_key") and not creds.get("real_api_key"):
            raise HTTPException(status_code=400, detail="Bybit not configured. Add your API keys first.")
    
    # Update exchange type in database
    db.set_exchange_type(user_id, data.exchange)
    
    # Invalidate cached connections for this user
    try:
        from core import on_credentials_changed
        on_credentials_changed(user_id)
    except ImportError:
        pass  # Core module not available
    
    # Notify settings sync manager
    try:
        from services.settings_sync import settings_sync
        import asyncio
        
        creds = db.get_all_user_credentials(user_id) if data.exchange == "bybit" else db.get_hl_credentials(user_id)
        asyncio.create_task(settings_sync.on_exchange_switch(user_id, old_exchange, data.exchange, creds))
    except ImportError:
        pass
    
    # Test connection to new exchange
    connection_status = {"connected": False, "balance": None, "error": None}
    
    try:
        if data.exchange == "bybit":
            # Test Bybit connection
            import aiohttp
            import time
            import hashlib
            import hmac
            
            creds = db.get_all_user_credentials(user_id)
            trading_mode = creds.get("trading_mode", "demo")
            
            if trading_mode == "demo":
                api_key = creds.get("demo_api_key")
                api_secret = creds.get("demo_api_secret")
                base_url = "https://api-demo.bybit.com"
            else:
                api_key = creds.get("real_api_key")
                api_secret = creds.get("real_api_secret")
                base_url = "https://api.bybit.com"
            
            if api_key and api_secret:
                timestamp = str(int(time.time() * 1000))
                recv_window = "20000"
                params = "accountType=UNIFIED"
                param_str = f"{timestamp}{api_key}{recv_window}{params}"
                signature = hmac.new(api_secret.encode(), param_str.encode(), hashlib.sha256).hexdigest()
                
                headers = {
                    "X-BAPI-API-KEY": api_key,
                    "X-BAPI-TIMESTAMP": timestamp,
                    "X-BAPI-RECV-WINDOW": recv_window,
                    "X-BAPI-SIGN": signature
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{base_url}/v5/account/wallet-balance?{params}",
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as resp:
                        result = await resp.json()
                        if result.get("retCode") == 0:
                            connection_status["connected"] = True
                            equity = result.get("result", {}).get("list", [{}])[0].get("totalEquity", "0")
                            connection_status["balance"] = f"${float(equity):,.2f}"
        
        else:  # hyperliquid
            import aiohttp
            hl_creds = db.get_hl_credentials(user_id)
            wallet = hl_creds.get("hl_wallet_address")
            testnet = hl_creds.get("hl_testnet", False)
            base_url = "https://api.hyperliquid-testnet.xyz" if testnet else "https://api.hyperliquid.xyz"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/info",
                    json={"type": "clearinghouseState", "user": wallet},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    data_resp = await resp.json()
                    if "marginSummary" in data_resp:
                        connection_status["connected"] = True
                        equity = float(data_resp["marginSummary"].get("accountValue", 0))
                        connection_status["balance"] = f"${equity:,.2f}"
                        
    except Exception as e:
        connection_status["error"] = str(e)
        logger.warning(f"Exchange switch connection test failed: {e}")
    
    logger.info(f"User {user_id} switched from {old_exchange} to {data.exchange}")
    
    return {
        "success": True,
        "exchange": data.exchange,
        "previous_exchange": old_exchange,
        "connection": connection_status
    }


@router.post("/language")
async def change_language(
    data: LanguageChange,
    user: dict = Depends(get_current_user)
):
    """Change user language."""
    user_id = user["user_id"]
    
    valid_langs = ["en", "ru", "uk", "de", "fr", "es", "it", "pl", "zh", "ja", "ar", "he", "cs", "lt", "sq"]
    if data.language not in valid_langs:
        raise HTTPException(status_code=400, detail="Invalid language")
    
    db.set_user_field(user_id, "lang", data.language)
    
    return {"success": True, "language": data.language}


@router.get("/profile")
async def get_profile(user: dict = Depends(get_current_user)):
    """Get full user profile."""
    user_id = user["user_id"]
    
    creds = db.get_all_user_credentials(user_id)
    exchange_status = db.get_exchange_status(user_id)
    hl_creds = db.get_hl_credentials(user_id)
    
    return {
        "user_id": user_id,
        "language": creds.get("lang", "en"),
        "is_allowed": creds.get("is_allowed", False),
        "is_banned": creds.get("is_banned", False),
        "license_type": creds.get("license_type"),
        "license_expires": creds.get("license_expires"),
        "is_lifetime": creds.get("is_lifetime", False),
        
        # Exchange status
        "exchange_mode": exchange_status.get("exchange_mode", "bybit"),
        "active_exchange": exchange_status.get("active_exchange", "bybit"),
        
        # Bybit status
        "bybit": {
            "configured": bool(creds.get("demo_api_key") or creds.get("real_api_key")),
            "trading_mode": creds.get("trading_mode", "demo"),
            "has_demo": bool(creds.get("demo_api_key")),
            "has_real": bool(creds.get("real_api_key")),
        },
        
        # HyperLiquid status
        "hyperliquid": {
            "configured": bool(hl_creds.get("hl_private_key")),
            "testnet": hl_creds.get("hl_testnet", False),
            "wallet": hl_creds.get("hl_wallet_address", "")[:10] + "..." if hl_creds.get("hl_wallet_address") else None,
        }
    }


# ========== API KEYS MANAGEMENT ==========

@router.get("/api-keys")
async def get_api_keys(user: dict = Depends(get_current_user)):
    """Get masked API keys info."""
    user_id = user["user_id"]
    creds = db.get_all_user_credentials(user_id)
    hl_creds = db.get_hl_credentials(user_id)
    
    return {
        "demo_api_key": creds.get("demo_api_key", "")[-4:] if creds.get("demo_api_key") else None,
        "real_api_key": creds.get("real_api_key", "")[-4:] if creds.get("real_api_key") else None,
        "hl_wallet_address": hl_creds.get("hl_wallet_address"),
        "hl_vault_address": hl_creds.get("hl_vault_address"),
        "hl_testnet": hl_creds.get("hl_testnet", False),
        "hl_has_key": bool(hl_creds.get("hl_private_key")),
    }


@router.post("/api-keys/bybit")
async def save_bybit_api_keys(
    data: BybitApiKeys,
    user: dict = Depends(get_current_user)
):
    """Save Bybit API keys."""
    user_id = user["user_id"]
    
    if data.account_type not in ["demo", "real"]:
        raise HTTPException(status_code=400, detail="Invalid account type")
    
    if not data.api_key or not data.api_secret:
        raise HTTPException(status_code=400, detail="API key and secret required")
    
    # Save keys
    if data.account_type == "demo":
        db.set_user_field(user_id, "demo_api_key", data.api_key)
        db.set_user_field(user_id, "demo_api_secret", data.api_secret)
    else:
        db.set_user_field(user_id, "real_api_key", data.api_key)
        db.set_user_field(user_id, "real_api_secret", data.api_secret)
    
    logger.info(f"User {user_id} saved {data.account_type} Bybit API keys")
    
    return {"success": True, "account_type": data.account_type}


@router.get("/api-keys/bybit/test")
async def test_bybit_api(
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
):
    """Test Bybit API connection."""
    user_id = user["user_id"]
    
    creds = db.get_all_user_credentials(user_id)
    
    if account_type == "demo":
        api_key = creds.get("demo_api_key")
        api_secret = creds.get("demo_api_secret")
        testnet = True
    else:
        api_key = creds.get("real_api_key")
        api_secret = creds.get("real_api_secret")
        testnet = False
    
    if not api_key or not api_secret:
        return {"success": False, "error": "API keys not configured"}
    
    try:
        import aiohttp
        import time
        import hashlib
        import hmac
        
        base_url = "https://api-demo.bybit.com" if testnet else "https://api.bybit.com"
        
        timestamp = str(int(time.time() * 1000))
        recv_window = "20000"
        params = "accountType=UNIFIED"
        
        param_str = f"{timestamp}{api_key}{recv_window}{params}"
        signature = hmac.new(
            api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            "X-BAPI-API-KEY": api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": recv_window,
            "X-BAPI-SIGN": signature
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{base_url}/v5/account/wallet-balance?{params}",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                data = await resp.json()
                
                if data.get("retCode") == 0:
                    balance = "OK"
                    result = data.get("result", {}).get("list", [])
                    if result:
                        equity = result[0].get("totalEquity", "0")
                        balance = f"${float(equity):,.2f}"
                    return {"success": True, "balance": balance}
                else:
                    return {"success": False, "error": data.get("retMsg", "API error")}
                    
    except Exception as e:
        logger.error(f"Bybit API test failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/api-keys/hyperliquid")
async def save_hl_api_keys(
    data: HLApiKeys,
    user: dict = Depends(get_current_user)
):
    """Save HyperLiquid API keys."""
    user_id = user["user_id"]
    
    if not data.wallet_address:
        raise HTTPException(status_code=400, detail="Wallet address required")
    
    # Validate wallet address format
    if not data.wallet_address.startswith("0x") or len(data.wallet_address) != 42:
        raise HTTPException(status_code=400, detail="Invalid wallet address format")
    
    db.set_user_field(user_id, "hl_wallet_address", data.wallet_address)
    
    if data.private_key:
        # Validate private key format
        pk = data.private_key.strip()
        if not pk.startswith("0x"):
            pk = "0x" + pk
        if len(pk) != 66:
            raise HTTPException(status_code=400, detail="Invalid private key format")
        db.set_user_field(user_id, "hl_private_key", pk)
    
    if data.vault_address:
        if not data.vault_address.startswith("0x") or len(data.vault_address) != 42:
            raise HTTPException(status_code=400, detail="Invalid vault address format")
        db.set_user_field(user_id, "hl_vault_address", data.vault_address)
    
    db.set_user_field(user_id, "hl_testnet", data.testnet)
    
    logger.info(f"User {user_id} saved HyperLiquid API keys")
    
    return {"success": True}


@router.get("/api-keys/hyperliquid/test")
async def test_hl_api(user: dict = Depends(get_current_user)):
    """Test HyperLiquid API connection."""
    user_id = user["user_id"]
    
    hl_creds = db.get_hl_credentials(user_id)
    
    wallet = hl_creds.get("hl_wallet_address")
    if not wallet:
        return {"success": False, "error": "Wallet not configured"}
    
    try:
        import aiohttp
        
        testnet = hl_creds.get("hl_testnet", False)
        base_url = "https://api.hyperliquid-testnet.xyz" if testnet else "https://api.hyperliquid.xyz"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/info",
                json={"type": "clearinghouseState", "user": wallet},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                data = await resp.json()
                
                if "marginSummary" in data:
                    equity = float(data["marginSummary"].get("accountValue", 0))
                    return {"success": True, "balance": f"${equity:,.2f}"}
                else:
                    return {"success": False, "error": "Invalid response"}
                    
    except Exception as e:
        logger.error(f"HL API test failed: {e}")
        return {"success": False, "error": str(e)}


# ========== STRATEGY SETTINGS ==========

class StrategySettings(BaseModel):
    strategy_name: str
    enabled: bool = True
    settings: dict = {}
    exchange: str = "bybit"  # "bybit" or "hyperliquid"
    account_type: str = "demo"  # "demo"/"real" for bybit, "testnet"/"mainnet" for hyperliquid


@router.get("/strategy-settings")
async def get_strategy_settings(
    exchange: str = Query("bybit"),
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
):
    """Get all strategy settings for user per exchange and account type."""
    user_id = user["user_id"]
    creds = db.get_all_user_credentials(user_id)
    
    # Parse unified strategy_settings JSON with new structure
    import json
    strategy_settings_raw = creds.get("strategy_settings", "{}")
    try:
        all_strategy_settings = json.loads(strategy_settings_raw) if strategy_settings_raw else {}
    except:
        all_strategy_settings = {}
    
    # Get settings for specific exchange/account_type
    # Structure: { "bybit": { "demo": {...}, "real": {...} }, "hyperliquid": { "testnet": {...}, "mainnet": {...} } }
    exchange_settings = all_strategy_settings.get(exchange, {})
    account_settings = exchange_settings.get(account_type, {})
    
    # Get global enabled flags (legacy compatibility)
    global_enabled = {
        "elcaro": bool(creds.get("trade_elcaro")),
        "wyckoff": bool(creds.get("trade_wyckoff")),
        "scryptomera": bool(creds.get("trade_scryptomera")),
        "scalper": bool(creds.get("trade_scalper")),
        "rsi_bb": bool(creds.get("trade_rsi_bb")),
        "oi": bool(creds.get("trade_oi")),
    }
    
    # Default settings for each strategy
    default_settings = {
        "elcaro": {
            "enabled": account_settings.get("elcaro", {}).get("enabled", global_enabled.get("elcaro", False)),
            "params": {
                "tp_percent": account_settings.get("elcaro", {}).get("tp_percent", creds.get("tp_percent", 2)),
                "sl_percent": account_settings.get("elcaro", {}).get("sl_percent", creds.get("sl_percent", 1)),
                "percent": account_settings.get("elcaro", {}).get("percent", creds.get("percent", 5)),
                "leverage": account_settings.get("elcaro", {}).get("leverage", creds.get("leverage", 10)),
                "min_confidence": account_settings.get("elcaro", {}).get("min_confidence", 0.7),
                "timeframes": account_settings.get("elcaro", {}).get("timeframes", ["15m", "1h"]),
            }
        },
        "wyckoff": {
            "enabled": account_settings.get("wyckoff", {}).get("enabled", global_enabled.get("wyckoff", False)),
            "params": {
                "tp_percent": account_settings.get("wyckoff", {}).get("tp_percent", creds.get("tp_percent", 2)),
                "sl_percent": account_settings.get("wyckoff", {}).get("sl_percent", creds.get("sl_percent", 1)),
                "percent": account_settings.get("wyckoff", {}).get("percent", creds.get("percent", 5)),
                "leverage": account_settings.get("wyckoff", {}).get("leverage", creds.get("leverage", 10)),
                "min_quality": account_settings.get("wyckoff", {}).get("min_quality", 50),
                "direction": account_settings.get("wyckoff", {}).get("direction", "all"),
            }
        },
        "scryptomera": {
            "enabled": account_settings.get("scryptomera", {}).get("enabled", global_enabled.get("scryptomera", False)),
            "params": {
                "tp_percent": account_settings.get("scryptomera", {}).get("tp_percent", creds.get("tp_percent", 2)),
                "sl_percent": account_settings.get("scryptomera", {}).get("sl_percent", creds.get("sl_percent", 1)),
                "percent": account_settings.get("scryptomera", {}).get("percent", creds.get("percent", 5)),
                "leverage": account_settings.get("scryptomera", {}).get("leverage", creds.get("leverage", 10)),
                "min_vdelta": account_settings.get("scryptomera", {}).get("min_vdelta", 100),
                "timeframe": account_settings.get("scryptomera", {}).get("timeframe", "15m"),
                "direction": account_settings.get("scryptomera", {}).get("direction", "all"),
            }
        },
        "scalper": {
            "enabled": account_settings.get("scalper", {}).get("enabled", global_enabled.get("scalper", False)),
            "params": {
                "tp_percent": account_settings.get("scalper", {}).get("tp_percent", 0.5),
                "sl_percent": account_settings.get("scalper", {}).get("sl_percent", 0.3),
                "percent": account_settings.get("scalper", {}).get("percent", creds.get("percent", 5)),
                "leverage": account_settings.get("scalper", {}).get("leverage", creds.get("leverage", 10)),
                "momentum_threshold": account_settings.get("scalper", {}).get("momentum_threshold", 1.5),
                "max_trades_per_hour": account_settings.get("scalper", {}).get("max_trades_per_hour", 10),
            }
        },
        "rsi_bb": {
            "enabled": account_settings.get("rsi_bb", {}).get("enabled", global_enabled.get("rsi_bb", False)),
            "params": {
                "tp_percent": account_settings.get("rsi_bb", {}).get("tp_percent", creds.get("tp_percent", 2)),
                "sl_percent": account_settings.get("rsi_bb", {}).get("sl_percent", creds.get("sl_percent", 1)),
                "percent": account_settings.get("rsi_bb", {}).get("percent", creds.get("percent", 5)),
                "leverage": account_settings.get("rsi_bb", {}).get("leverage", creds.get("leverage", 10)),
                "rsi_oversold": account_settings.get("rsi_bb", {}).get("rsi_oversold", creds.get("rsi_lo", 30)),
                "rsi_overbought": account_settings.get("rsi_bb", {}).get("rsi_overbought", creds.get("rsi_hi", 70)),
                "bb_touch_k": account_settings.get("rsi_bb", {}).get("bb_touch_k", creds.get("bb_touch_k", 2.0)),
            }
        },
        "oi": {
            "enabled": account_settings.get("oi", {}).get("enabled", global_enabled.get("oi", False)),
            "params": {
                "tp_percent": account_settings.get("oi", {}).get("tp_percent", creds.get("tp_percent", 2)),
                "sl_percent": account_settings.get("oi", {}).get("sl_percent", creds.get("sl_percent", 1)),
                "percent": account_settings.get("oi", {}).get("percent", creds.get("percent", 5)),
                "leverage": account_settings.get("oi", {}).get("leverage", creds.get("leverage", 10)),
                "min_oi_change": account_settings.get("oi", {}).get("min_oi_change", creds.get("oi_min_pct", 5)),
                "min_price_change": account_settings.get("oi", {}).get("min_price_change", creds.get("price_min_pct", 1)),
            }
        }
    }
    
    return {
        "exchange": exchange,
        "account_type": account_type,
        "strategies": default_settings
    }


@router.put("/strategy-settings/{strategy_name}")
async def update_strategy_settings(
    strategy_name: str,
    data: StrategySettings,
    user: dict = Depends(get_current_user)
):
    """Update settings for a specific strategy per exchange and account type."""
    user_id = user["user_id"]
    
    valid_strategies = ["elcaro", "wyckoff", "scryptomera", "scalper", "rsi_bb", "oi"]
    if strategy_name not in valid_strategies:
        raise HTTPException(status_code=400, detail="Invalid strategy name")
    
    valid_exchanges = ["bybit", "hyperliquid"]
    if data.exchange not in valid_exchanges:
        raise HTTPException(status_code=400, detail="Invalid exchange")
    
    valid_account_types = {
        "bybit": ["demo", "real"],
        "hyperliquid": ["testnet", "mainnet"]
    }
    if data.account_type not in valid_account_types.get(data.exchange, []):
        raise HTTPException(status_code=400, detail="Invalid account type for exchange")
    
    import json
    
    # Get current settings
    creds = db.get_all_user_credentials(user_id)
    strategy_settings_raw = creds.get("strategy_settings", "{}")
    try:
        all_strategy_settings = json.loads(strategy_settings_raw) if strategy_settings_raw else {}
    except:
        all_strategy_settings = {}
    
    # Initialize structure if needed
    if data.exchange not in all_strategy_settings:
        all_strategy_settings[data.exchange] = {}
    if data.account_type not in all_strategy_settings[data.exchange]:
        all_strategy_settings[data.exchange][data.account_type] = {}
    
    # Update strategy settings
    strategy_data = data.settings.copy()
    strategy_data["enabled"] = data.enabled
    all_strategy_settings[data.exchange][data.account_type][strategy_name] = strategy_data
    
    # Save to database
    db.set_user_field(user_id, "strategy_settings", json.dumps(all_strategy_settings))
    
    logger.info(f"User {user_id} updated {strategy_name} settings for {data.exchange}/{data.account_type}")
    
    return {"success": True, "strategy": strategy_name, "exchange": data.exchange, "account_type": data.account_type}
