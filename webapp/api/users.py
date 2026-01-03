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
    reconnect: bool = True


class AccountTypeSwitch(BaseModel):
    account_type: str  # 'demo', 'real', 'testnet', 'mainnet'
    exchange: str = None


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
        from core.tasks import safe_create_task
        
        creds = db.get_all_user_credentials(user_id) if data.exchange == "bybit" else db.get_hl_credentials(user_id)
        safe_create_task(settings_sync.on_exchange_switch(user_id, old_exchange, data.exchange, creds), name=f"exchange_switch_{user_id}")
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


@router.post("/switch-account-type")
async def switch_account_type(
    data: AccountTypeSwitch,
    user: dict = Depends(get_current_user)
):
    """
    Switch trading mode (demo/real for Bybit, testnet/mainnet for HyperLiquid).
    """
    user_id = user["user_id"]
    exchange = data.exchange or db.get_exchange_type(user_id)
    
    # Validate account type based on exchange
    if exchange == "bybit":
        if data.account_type not in ["demo", "real", "both"]:
            raise HTTPException(status_code=400, detail="Invalid account type for Bybit. Use: demo, real, both")
        # For Bybit, directly use trading_mode
        new_mode = data.account_type
    else:  # hyperliquid
        if data.account_type not in ["testnet", "mainnet"]:
            raise HTTPException(status_code=400, detail="Invalid account type for HyperLiquid. Use: testnet, mainnet")
        # Map HL account types to trading mode
        new_mode = data.account_type
        
        # Update HL testnet setting
        hl_testnet = data.account_type == "testnet"
        db.set_user_field(user_id, "hl_testnet", hl_testnet)
    
    # Get old mode for comparison
    old_mode = db.get_trading_mode(user_id)
    
    # Update trading mode
    if exchange == "bybit":
        db.set_trading_mode(user_id, new_mode)
    
    # Invalidate cached connections
    try:
        from core import on_credentials_changed
        on_credentials_changed(user_id)
    except ImportError:
        pass
    
    # Test connection with new account type
    connection_status = {"connected": False, "balance": None, "error": None}
    
    try:
        if exchange == "bybit":
            import aiohttp
            import time
            import hashlib
            import hmac
            
            creds = db.get_all_user_credentials(user_id)
            
            if new_mode in ["demo", "both"]:
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
                            available = result.get("result", {}).get("list", [{}])[0].get("totalAvailableBalance", "0")
                            connection_status["balance"] = {
                                "equity": float(equity),
                                "available": float(available)
                            }
        else:  # hyperliquid
            import aiohttp
            hl_creds = db.get_hl_credentials(user_id)
            wallet = hl_creds.get("hl_wallet_address")
            testnet = data.account_type == "testnet"
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
                        available = float(data_resp["marginSummary"].get("availableBalance", 0))
                        connection_status["balance"] = {
                            "equity": equity,
                            "available": available
                        }
                        
    except Exception as e:
        connection_status["error"] = str(e)
        logger.warning(f"Account type switch connection test failed: {e}")
    
    logger.info(f"User {user_id} switched account type from {old_mode} to {new_mode} ({exchange})")
    
    return {
        "success": True,
        "account_type": new_mode,
        "previous_account_type": old_mode,
        "exchange": exchange,
        "balance": connection_status.get("balance"),
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

# Strategy features - defines which settings are available for each strategy
# Synced with bot.py STRATEGY_FEATURES
STRATEGY_FEATURES = {
    "scryptomera": {
        "order_type": True,      # Market/Limit toggle
        "coins_group": True,     # Coins filter (ALL/TOP100/VOLATILE)
        "leverage": True,        # Leverage setting
        "use_atr": True,         # ATR trailing toggle
        "direction": True,       # LONG/SHORT/ALL filter
        "side_settings": True,   # Separate LONG/SHORT settings
        "percent": True,         # Global percent
        "sl_tp": True,           # SL/TP on main screen
        "atr_params": True,      # ATR params on main screen  
        "hl_settings": True,     # HyperLiquid support
        "min_quality": False,    # Scryptomera doesn't have quality filter
    },
    "scalper": {
        "order_type": True,
        "coins_group": True,
        "leverage": True,
        "use_atr": True,
        "direction": True,
        "side_settings": True,
        "percent": True,
        "sl_tp": True,
        "atr_params": True,
        "hl_settings": True,
        "min_quality": False,
    },
    "elcaro": {
        "order_type": False,     # Elcaro signals have their own order logic
        "coins_group": True,
        "leverage": False,       # From signal
        "use_atr": False,        # ATR managed by signal
        "direction": True,
        "side_settings": True,   # Only percent per side
        "percent": True,         # Global percent for this strategy
        "sl_tp": False,          # From signal
        "atr_params": False,     # From signal
        "hl_settings": True,
        "min_quality": False,
    },
    "fibonacci": {
        "order_type": True,      # Market/Limit toggle
        "coins_group": True,
        "leverage": True,
        "use_atr": True,         # ATR trailing option
        "direction": True,
        "side_settings": True,
        "percent": True,
        "sl_tp": True,           # Manual SL/TP override
        "atr_params": True,      # ATR params
        "hl_settings": True,
        "min_quality": True,     # Fibonacci-specific quality filter
    },
    "oi": {
        "order_type": True,
        "coins_group": True,
        "leverage": True,
        "use_atr": True,
        "direction": True,
        "side_settings": True,   # LONG/SHORT separate settings
        "percent": True,
        "sl_tp": True,           # Manual SL/TP
        "atr_params": True,      # Full ATR control
        "hl_settings": True,
        "min_quality": False,
    },
    "rsi_bb": {
        "order_type": True,
        "coins_group": True,
        "leverage": True,
        "use_atr": True,
        "direction": True,
        "side_settings": True,   # LONG/SHORT separate settings
        "percent": True,
        "sl_tp": True,
        "atr_params": True,
        "hl_settings": True,
        "min_quality": False,
    },
}

VALID_STRATEGIES = ["elcaro", "scryptomera", "scalper", "fibonacci", "rsi_bb", "oi"]


class StrategySettings(BaseModel):
    strategy_name: str
    enabled: bool = True
    settings: dict = {}
    exchange: str = "bybit"  # "bybit" or "hyperliquid"
    account_type: str = "demo"  # "demo"/"real" for bybit, "testnet"/"mainnet" for hyperliquid


def _build_strategy_params(strategy: str, db_settings: dict, features: dict) -> dict:
    """Build params dict for a strategy based on its features and DB settings."""
    params = {}
    
    # Basic params (always included)
    params["percent"] = db_settings.get("percent") if db_settings.get("percent") is not None else 5.0
    params["direction"] = db_settings.get("direction") or "all"
    
    # Enabled flag
    params["enabled"] = bool(db_settings.get("enabled", False))
    
    # Leverage (if strategy supports it)
    if features.get("leverage"):
        params["leverage"] = db_settings.get("leverage") if db_settings.get("leverage") is not None else 10
    
    # Order type (if strategy supports it)
    if features.get("order_type"):
        params["order_type"] = db_settings.get("order_type") or "market"
    
    # SL/TP (if strategy supports it)
    if features.get("sl_tp"):
        params["sl_percent"] = db_settings.get("sl_percent") if db_settings.get("sl_percent") is not None else 3.0
        params["tp_percent"] = db_settings.get("tp_percent") if db_settings.get("tp_percent") is not None else 8.0
    
    # ATR settings (if strategy supports it)
    if features.get("use_atr"):
        params["use_atr"] = bool(db_settings.get("use_atr", False))
    
    if features.get("atr_params"):
        params["atr_periods"] = db_settings.get("atr_periods") if db_settings.get("atr_periods") is not None else 7
        params["atr_multiplier_sl"] = db_settings.get("atr_multiplier_sl") if db_settings.get("atr_multiplier_sl") is not None else 1.0
        params["atr_trigger_pct"] = db_settings.get("atr_trigger_pct") if db_settings.get("atr_trigger_pct") is not None else 2.0
    
    # Min quality (Fibonacci only)
    if features.get("min_quality"):
        params["min_quality"] = db_settings.get("min_quality") if db_settings.get("min_quality") is not None else 50
    
    # Side-specific settings (LONG/SHORT)
    if features.get("side_settings"):
        # LONG side
        params["long_percent"] = db_settings.get("long_percent")
        if features.get("sl_tp"):
            params["long_sl_percent"] = db_settings.get("long_sl_percent")
            params["long_tp_percent"] = db_settings.get("long_tp_percent")
        if features.get("atr_params"):
            params["long_atr_periods"] = db_settings.get("long_atr_periods")
            params["long_atr_multiplier_sl"] = db_settings.get("long_atr_multiplier_sl")
            params["long_atr_trigger_pct"] = db_settings.get("long_atr_trigger_pct")
        
        # SHORT side
        params["short_percent"] = db_settings.get("short_percent")
        if features.get("sl_tp"):
            params["short_sl_percent"] = db_settings.get("short_sl_percent")
            params["short_tp_percent"] = db_settings.get("short_tp_percent")
        if features.get("atr_params"):
            params["short_atr_periods"] = db_settings.get("short_atr_periods")
            params["short_atr_multiplier_sl"] = db_settings.get("short_atr_multiplier_sl")
            params["short_atr_trigger_pct"] = db_settings.get("short_atr_trigger_pct")
    
    # Coins group
    if features.get("coins_group"):
        params["coins_group"] = db_settings.get("coins_group") or "all"
    
    return params


@router.get("/strategy-settings")
async def get_strategy_settings(
    exchange: str = Query("bybit"),
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
):
    """Get all strategy settings for user per exchange and account type.
    
    Uses db.get_strategy_settings_db() to get settings from user_strategy_settings table.
    Returns settings with features based on STRATEGY_FEATURES config.
    """
    user_id = user["user_id"]
    
    result = {}
    for strategy in VALID_STRATEGIES:
        features = STRATEGY_FEATURES.get(strategy, {})
        
        # Get settings from database (uses user_strategy_settings table)
        db_settings = db.get_strategy_settings_db(user_id, strategy, exchange, account_type)
        
        # Build params based on features
        params = _build_strategy_params(strategy, db_settings, features)
        
        result[strategy] = {
            "enabled": params.pop("enabled", False),
            "params": params,
            "features": features,  # Include features so frontend knows what to display
        }
    
    return {
        "exchange": exchange,
        "account_type": account_type,
        "strategies": result
    }


@router.put("/strategy-settings/{strategy_name}")
async def update_strategy_settings(
    strategy_name: str,
    data: StrategySettings,
    user: dict = Depends(get_current_user)
):
    """Update settings for a specific strategy per exchange and account type.
    
    Uses db.set_strategy_setting_db() to save to user_strategy_settings table.
    Only updates fields that are included in the request.
    """
    user_id = user["user_id"]
    
    if strategy_name not in VALID_STRATEGIES:
        raise HTTPException(status_code=400, detail=f"Invalid strategy name. Valid: {VALID_STRATEGIES}")
    
    valid_exchanges = ["bybit", "hyperliquid"]
    if data.exchange not in valid_exchanges:
        raise HTTPException(status_code=400, detail="Invalid exchange")
    
    valid_account_types = {
        "bybit": ["demo", "real"],
        "hyperliquid": ["testnet", "mainnet"]
    }
    if data.account_type not in valid_account_types.get(data.exchange, []):
        raise HTTPException(status_code=400, detail="Invalid account type for exchange")
    
    # Get strategy features to validate which fields can be updated
    features = STRATEGY_FEATURES.get(strategy_name, {})
    
    # Valid fields that can be updated
    valid_fields = {
        "enabled", "percent", "direction", "coins_group",
        # Leverage (if supported)
        "leverage",
        # Order type (if supported)
        "order_type",
        # SL/TP (if supported)
        "sl_percent", "tp_percent",
        # ATR settings (if supported)
        "use_atr", "atr_periods", "atr_multiplier_sl", "atr_trigger_pct",
        # Min quality (Fibonacci only)
        "min_quality",
        # Side-specific settings
        "long_percent", "long_sl_percent", "long_tp_percent",
        "long_atr_periods", "long_atr_multiplier_sl", "long_atr_trigger_pct",
        "short_percent", "short_sl_percent", "short_tp_percent",
        "short_atr_periods", "short_atr_multiplier_sl", "short_atr_trigger_pct",
    }
    
    # Update enabled flag
    db.set_strategy_setting_db(user_id, strategy_name, "enabled", data.enabled, data.exchange, data.account_type)
    
    # Update each setting from the request
    updated_fields = ["enabled"]
    for field, value in data.settings.items():
        if field not in valid_fields:
            logger.warning(f"Invalid field {field} for strategy {strategy_name}")
            continue
        
        # Convert value type if needed
        if field in ("enabled", "use_atr"):
            value = bool(value)
        elif field in ("leverage", "atr_periods", "long_atr_periods", "short_atr_periods", "min_quality"):
            value = int(value) if value is not None else None
        elif field in ("percent", "sl_percent", "tp_percent", "atr_multiplier_sl", "atr_trigger_pct",
                       "long_percent", "long_sl_percent", "long_tp_percent", "long_atr_multiplier_sl", "long_atr_trigger_pct",
                       "short_percent", "short_sl_percent", "short_tp_percent", "short_atr_multiplier_sl", "short_atr_trigger_pct"):
            value = float(value) if value is not None else None
        
        db.set_strategy_setting_db(user_id, strategy_name, field, value, data.exchange, data.account_type)
        updated_fields.append(field)
    
    logger.info(f"User {user_id} updated {strategy_name} settings for {data.exchange}/{data.account_type}: {updated_fields}")
    
    return {
        "success": True, 
        "strategy": strategy_name, 
        "exchange": data.exchange, 
        "account_type": data.account_type,
        "updated_fields": updated_fields
    }
