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

# Bug #3 Fix: Use centralized account utilities instead of local definition
from core.account_utils import normalize_account_type as _normalize_both_account_type

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
    hl_creds = db.get_hl_credentials(user_id)
    
    # Common global settings for all responses
    exchange_type = db.get_exchange_type(user_id) or "bybit"
    trading_mode = creds.get("trading_mode", "demo")
    hl_testnet = hl_creds.get("hl_testnet", False)
    user_lang = creds.get("lang", "en")
    last_viewed_account = creds.get("last_viewed_account", None)  # Bug #2 fix: for iOS sync
    
    if exchange == "hyperliquid":
        # Check both new architecture and legacy format
        has_key = bool(
            hl_creds.get("hl_testnet_private_key") or 
            hl_creds.get("hl_mainnet_private_key") or 
            hl_creds.get("hl_private_key")
        )
        return {
            # Global settings
            "exchange_type": exchange_type,
            "trading_mode": trading_mode,
            "hl_testnet": hl_testnet,
            "lang": user_lang,
            "last_viewed_account": last_viewed_account,
            # Exchange-specific settings
            "percent": creds.get("hl_percent", 5),
            "leverage": creds.get("hl_leverage", 10),
            "tp_percent": creds.get("hl_tp_percent", 2),
            "sl_percent": creds.get("hl_sl_percent", 1),
            "testnet": hl_testnet,
            "has_key": has_key,
            "wallet": hl_creds.get("hl_wallet_address", "")[:10] + "..." if hl_creds.get("hl_wallet_address") else None,
        }
    else:
        return {
            # Global settings
            "exchange_type": exchange_type,
            "trading_mode": trading_mode,
            "hl_testnet": hl_testnet,
            "lang": user_lang,
            "last_viewed_account": last_viewed_account,
            # Exchange-specific settings
            "percent": creds.get("percent", 5),
            "leverage": creds.get("leverage", 10),
            "tp_percent": creds.get("tp_percent", 2),
            "sl_percent": creds.get("sl_percent", 1),
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


@router.get("/me")
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """Get current authenticated user info for quick UI setup."""
    user_id = user["user_id"]
    creds = db.get_all_user_credentials(user_id)
    hl_creds = db.get_hl_credentials(user_id)
    
    # Get exchange type from correct field
    exchange_type = db.get_exchange_type(user_id) or "bybit"
    
    # Get additional user fields directly from database (including linked accounts)
    from core.db_postgres import execute_one
    user_row = execute_one("""
        SELECT first_name, last_name, is_allowed, leverage, lang, license_type,
               email, email_verified, telegram_id, telegram_username, auth_provider
        FROM users WHERE user_id = %s
    """, (user_id,))
    
    # Get email user info if available (legacy fallback)
    email_user = None
    if not user_row or not user_row.get("email"):
        try:
            from webapp.api.email_auth import get_email_user_by_id
            email_user = get_email_user_by_id(user_id)
        except:
            pass
    
    # Build linked accounts info
    email_from_row = user_row.get("email") if user_row else None
    email_address = email_from_row or (email_user.get("email") if email_user else None)
    
    # Determine Telegram ID - native TG users have positive user_id
    telegram_id = user_row.get("telegram_id") if user_row else None
    if telegram_id is None and user_id > 0:
        telegram_id = user_id  # Native Telegram user
    
    return {
        "user": {
            "id": user_id,  # Required for iOS Identifiable
            "user_id": user_id,
            "email": email_address,
            "name": (user_row.get("first_name") if user_row else None) or (email_user.get("name") if email_user else None),
            "first_name": user_row.get("first_name") if user_row else None,
            "last_name": user_row.get("last_name") if user_row else None,
            "exchange_type": exchange_type,
            "trading_mode": creds.get("trading_mode", "demo"),
            "hl_testnet": hl_creds.get("hl_testnet", False),
            "leverage": user_row.get("leverage", 10) if user_row else 10,
            "lang": user_row.get("lang", "en") if user_row else "en",
            "is_allowed": bool(user_row.get("is_allowed", 0)) if user_row else False,
            "is_premium": (user_row.get("license_type") if user_row else None) not in (None, "free"),
            "license_type": user_row.get("license_type", "free") if user_row else "free",
            # Linked accounts info
            "telegram_id": telegram_id,
            "telegram_username": user_row.get("telegram_username") if user_row else None,
            "email_verified": bool(user_row.get("email_verified")) if user_row else False,
            "auth_provider": user_row.get("auth_provider", "email" if user_id < 0 else "telegram") if user_row else None,
        }
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
        # Check both new architecture and legacy format
        has_testnet = hl_creds.get("hl_testnet_private_key")
        has_mainnet = hl_creds.get("hl_mainnet_private_key")
        has_legacy = hl_creds.get("hl_private_key")
        if not (has_testnet or has_mainnet or has_legacy):
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
    
    # Log activity for cross-platform sync
    try:
        from services.sync_service import sync_service
        import asyncio
        asyncio.create_task(sync_service.sync_exchange_switch(
            user_id=user_id,
            source="webapp",
            old_exchange=old_exchange,
            new_exchange=data.exchange
        ))
    except Exception as e:
        logger.warning(f"Failed to log exchange switch activity: {e}")
    
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
    
    # Update trading mode for both Bybit and HyperLiquid
    # Bug #9 Fix: Also update trading_mode for HL so iOS can sync correctly
    db.set_trading_mode(user_id, new_mode)
    
    # Also save last_viewed_account for iOS sync
    db.set_user_field(user_id, "last_viewed_account", data.account_type)
    
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
    
    # Save last viewed account for UI persistence across platforms
    db.set_last_viewed_account(user_id, new_mode)
    
    # Log activity for cross-platform sync
    try:
        from services.sync_service import sync_service
        import asyncio
        asyncio.create_task(sync_service.log_activity(
            user_id=user_id,
            action_type="account_type_switch",
            action_category="settings",
            source="webapp",
            entity_type="account",
            old_value=old_mode,
            new_value=new_mode,
            details={"exchange": exchange}
        ))
    except Exception as e:
        logger.warning(f"Failed to log account type switch activity: {e}")
    
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


class DisclaimerAcceptance(BaseModel):
    accepted: bool


@router.post("/disclaimer")
async def accept_disclaimer(
    data: DisclaimerAcceptance,
    user: dict = Depends(get_current_user)
):
    """Record user's disclaimer acceptance (for compliance tracking)."""
    user_id = user["user_id"]
    
    if data.accepted:
        # Store disclaimer acceptance in database
        try:
            db.set_user_field(user_id, "disclaimer_accepted", 1)
            db.set_user_field(user_id, "disclaimer_accepted_at", "NOW()")
            logger.info(f"User {user_id} accepted disclaimer")
        except Exception as e:
            logger.warning(f"Failed to save disclaimer acceptance: {e}")
    
    return {"success": True, "accepted": data.accepted}


@router.get("/disclaimer")
async def get_disclaimer_status(user: dict = Depends(get_current_user)):
    """Check if user has accepted the disclaimer."""
    user_id = user["user_id"]
    
    try:
        accepted = db.get_user_field(user_id, "disclaimer_accepted", 0)
        return {"accepted": bool(accepted)}
    except Exception:
        return {"accepted": False}


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
            "configured": bool(
                hl_creds.get("hl_testnet_private_key") or 
                hl_creds.get("hl_mainnet_private_key") or 
                hl_creds.get("hl_private_key")
            ),
            "testnet": hl_creds.get("hl_testnet", False),
            "wallet": hl_creds.get("hl_wallet_address", "")[:10] + "..." if hl_creds.get("hl_wallet_address") else None,
        }
    }


# ========== GLOBAL TRADING SETTINGS ==========

@router.get("/global-settings")
async def get_global_settings(user: dict = Depends(get_current_user)):
    """Get global trading settings (DCA, order type, spot, etc.)"""
    user_id = user["user_id"]
    cfg = db.get_user_config(user_id)
    
    # Parse spot_settings if it's a JSON string
    spot_settings = cfg.get("spot_settings", {})
    if isinstance(spot_settings, str):
        try:
            import json
            spot_settings = json.loads(spot_settings)
        except (json.JSONDecodeError, ValueError):
            spot_settings = {}
    
    return {
        # Order settings
        "global_order_type": cfg.get("global_order_type", "market"),
        "limit_offset_pct": cfg.get("limit_offset_pct", 0.1),
        
        # DCA settings (futures)
        "dca_enabled": bool(cfg.get("dca_enabled", 0)),
        "dca_pct_1": cfg.get("dca_pct_1", 10.0),
        "dca_pct_2": cfg.get("dca_pct_2", 25.0),
        
        # Spot DCA settings
        "spot_enabled": bool(cfg.get("spot_enabled", 0)),
        "spot_settings": {
            "trading_mode": spot_settings.get("trading_mode", "demo"),
            "strategy": spot_settings.get("strategy", "fixed"),
            "dca_amount": spot_settings.get("dca_amount", 10.0),
            "auto_dca": bool(spot_settings.get("auto_dca", False)),
            "tp_enabled": bool(spot_settings.get("tp_enabled", False)),
            "tp_percent": spot_settings.get("tp_percent", 10.0),
            "coins": spot_settings.get("coins", ["BTC", "ETH"]),
            "portfolio": spot_settings.get("portfolio", "custom"),
            "dip_threshold": spot_settings.get("dip_threshold", 5.0),
            "fear_threshold": spot_settings.get("fear_threshold", 25),
        },
        
        # ATR settings (global)
        "use_atr": bool(cfg.get("use_atr", 0)),
        "atr_periods": cfg.get("atr_periods", 7),
        "atr_multiplier_sl": cfg.get("atr_multiplier_sl", 1.0),
        "atr_trigger_pct": cfg.get("atr_trigger_pct", 2.0),
        "atr_step_pct": cfg.get("atr_step_pct", 0.5),
        
        # Live trading confirmation
        "live_enabled": bool(cfg.get("live_enabled", 0)),
    }


@router.put("/global-settings")
async def update_global_settings(
    data: dict,
    user: dict = Depends(get_current_user)
):
    """Update global trading settings."""
    user_id = user["user_id"]
    
    # Allowed fields for update
    allowed_fields = {
        "global_order_type", "limit_offset_pct",
        "dca_enabled", "dca_pct_1", "dca_pct_2",
        "spot_enabled",
        "use_atr", "atr_periods", "atr_multiplier_sl", "atr_trigger_pct", "atr_step_pct",
        "live_enabled"
    }
    
    updated = {}
    for key, value in data.items():
        if key in allowed_fields:
            # Convert booleans to int for SQLite compatibility
            if key in ("dca_enabled", "spot_enabled", "use_atr", "live_enabled"):
                value = 1 if value else 0
            db.set_user_field(user_id, key, value)
            updated[key] = value
    
    return {"success": True, "updated": updated}


@router.put("/spot-settings")
async def update_spot_settings(
    data: dict,
    user: dict = Depends(get_current_user)
):
    """Update spot DCA settings."""
    user_id = user["user_id"]
    
    # Get current spot_settings
    cfg = db.get_user_config(user_id)
    spot_settings = cfg.get("spot_settings", {})
    if isinstance(spot_settings, str):
        try:
            import json
            spot_settings = json.loads(spot_settings)
        except (json.JSONDecodeError, ValueError):
            spot_settings = {}
    
    # Allowed spot fields
    allowed_spot_fields = {
        "trading_mode", "strategy", "dca_amount", "auto_dca", "tp_enabled",
        "tp_percent", "coins", "portfolio", "dip_threshold", "fear_threshold"
    }
    
    # Update spot_settings
    for key, value in data.items():
        if key in allowed_spot_fields:
            spot_settings[key] = value
    
    # Save back as JSON
    import json
    db.set_user_field(user_id, "spot_settings", json.dumps(spot_settings))
    
    return {"success": True, "spot_settings": spot_settings}


@router.get("/exchange-trading-status")
async def get_exchange_trading_status(user: dict = Depends(get_current_user)):
    """Get trading enabled/disabled status for each exchange."""
    user_id = user["user_id"]
    
    bybit_enabled = db.is_bybit_enabled(user_id)
    hl_enabled = db.is_hl_enabled(user_id)
    exchange_type = db.get_exchange_type(user_id)
    
    # Check configured
    creds = db.get_all_user_credentials(user_id)
    hl_creds = db.get_hl_credentials(user_id)
    
    bybit_configured = bool(creds.get("demo_api_key") or creds.get("real_api_key"))
    hl_configured = bool(
        hl_creds.get("hl_testnet_private_key") or 
        hl_creds.get("hl_mainnet_private_key") or 
        hl_creds.get("hl_private_key")
    )
    
    return {
        "active_exchange": exchange_type,
        "bybit": {
            "enabled": bybit_enabled,
            "configured": bybit_configured,
        },
        "hyperliquid": {
            "enabled": hl_enabled,
            "configured": hl_configured,
        }
    }


@router.put("/exchange-trading-status/{exchange}")
async def toggle_exchange_trading(
    exchange: str,
    data: dict,
    user: dict = Depends(get_current_user)
):
    """Enable/disable trading on specific exchange."""
    user_id = user["user_id"]
    enabled = data.get("enabled", True)
    
    if exchange == "bybit":
        db.set_bybit_enabled(user_id, enabled)
    elif exchange == "hyperliquid":
        db.set_hl_enabled(user_id, enabled)
    else:
        return {"success": False, "error": f"Unknown exchange: {exchange}"}
    
    return {"success": True, "exchange": exchange, "enabled": enabled}


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
        "hl_has_key": bool(
            hl_creds.get("hl_testnet_private_key") or 
            hl_creds.get("hl_mainnet_private_key") or 
            hl_creds.get("hl_private_key")
        ),
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
    
    # Normalize 'both' -> 'demo' (this is bybit-specific endpoint)
    account_type = _normalize_both_account_type(account_type, 'bybit')
    
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
        "limit_offset": True,    # Limit order offset %
        "coins_group": True,     # Coins filter (ALL/TOP/VOLATILE)
        "leverage": True,        # Leverage setting
        "use_atr": True,         # ATR trailing toggle
        "direction": True,       # LONG/SHORT/ALL filter
        "side_settings": True,   # Separate LONG/SHORT settings
        "percent": True,         # Global percent
        "sl_tp": True,           # SL/TP on main screen
        "atr_params": True,      # ATR params on main screen  
        "hl_settings": True,     # HyperLiquid support
        "min_quality": False,    # Scryptomera doesn't have quality filter
        "dca": True,             # DCA averaging support
    },
    "scalper": {
        "order_type": True,
        "limit_offset": True,
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
        "dca": True,             # DCA averaging support
    },
    "elcaro": {
        "order_type": False,     # Order type is per-side now
        "limit_offset": False,
        "coins_group": True,
        "leverage": True,        # User-configured leverage (NOT from signal anymore!)
        "use_atr": True,         # ATR trailing toggle (user settings)
        "direction": True,
        "side_settings": True,   # LONG/SHORT separate settings
        "percent": True,         # Global percent for this strategy
        "sl_tp": True,           # User-configured SL/TP (NOT from signal anymore!)
        "atr_params": True,      # ATR params from user settings
        "hl_settings": True,
        "min_quality": False,
        "dca": False,            # No DCA for Enliko signals
    },
    "fibonacci": {
        "order_type": True,      # Market/Limit toggle
        "limit_offset": True,
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
        "dca": True,
    },
    "oi": {
        "order_type": True,
        "limit_offset": True,
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
        "dca": True,
    },
    "rsi_bb": {
        "order_type": True,
        "limit_offset": True,
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
        "dca": True,
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
    
    # Limit offset (if strategy supports it)
    if features.get("limit_offset"):
        params["limit_offset_pct"] = db_settings.get("limit_offset_pct") if db_settings.get("limit_offset_pct") is not None else 0.1
    
    # SL/TP (if strategy supports it)
    if features.get("sl_tp"):
        params["sl_percent"] = db_settings.get("sl_percent") if db_settings.get("sl_percent") is not None else 3.0
        params["tp_percent"] = db_settings.get("tp_percent") if db_settings.get("tp_percent") is not None else 8.0
    
    # DCA settings (if strategy supports it)
    if features.get("dca"):
        params["dca_enabled"] = bool(db_settings.get("dca_enabled", False))
        params["dca_pct_1"] = db_settings.get("dca_pct_1") if db_settings.get("dca_pct_1") is not None else 10.0
        params["dca_pct_2"] = db_settings.get("dca_pct_2") if db_settings.get("dca_pct_2") is not None else 25.0
    
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
    
    # Normalize 'both' -> 'demo'/'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange)
    
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
    
    # Log activity for cross-platform sync
    try:
        from services.sync_service import sync_service
        import asyncio
        asyncio.create_task(sync_service.sync_settings_change(
            user_id=user_id,
            source="webapp",
            setting_name=f"strategy_{strategy_name}",
            old_value=None,  # Not tracking old value for bulk updates
            new_value=str(data.settings),
            details={
                "strategy": strategy_name,
                "exchange": data.exchange,
                "account_type": data.account_type,
                "updated_fields": updated_fields
            }
        ))
    except Exception as e:
        logger.warning(f"Failed to log strategy settings activity: {e}")
    
    return {
        "success": True, 
        "strategy": strategy_name, 
        "exchange": data.exchange, 
        "account_type": data.account_type,
        "updated_fields": updated_fields
    }


# ═══════════════════════════════════════════════════════════════════════════════════
# iOS MOBILE API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════════

@router.get("/strategy-settings/mobile")
async def get_strategy_settings_mobile(
    strategy: str = Query(None, description="Filter by strategy name"),
    exchange: str = Query("bybit"),
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
):
    """Get strategy settings in iOS-compatible format.
    
    Returns flat array of StrategySettings objects for iOS app.
    Each side (long/short) is a separate object in the array.
    
    Query params:
        strategy: Optional filter by strategy name
        exchange: Exchange name (bybit/hyperliquid)
        account_type: Account type (demo/real/testnet/mainnet)
    
    Returns:
        List of StrategySettings objects: [
            {"strategy": "oi", "side": "long", "percent": 1.0, ...},
            {"strategy": "oi", "side": "short", "percent": 1.0, ...},
            ...
        ]
    """
    user_id = user["user_id"]
    
    # Normalize 'both' -> 'demo'/'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange)
    
    # Filter strategies if specified
    strategies_to_fetch = [strategy] if strategy and strategy in VALID_STRATEGIES else VALID_STRATEGIES
    
    result = []
    
    for strat_name in strategies_to_fetch:
        # Get settings from database
        db_settings = db.get_strategy_settings_db(user_id, strat_name, exchange, account_type)
        
        # Create separate objects for long and short sides
        for side in ["long", "short"]:
            prefix = f"{side}_"
            
            settings_obj = {
                "strategy": strat_name,
                "side": side,
                "exchange": exchange,
                "account_type": account_type,
                "enabled": bool(db_settings.get(f"{prefix}enabled", True)),
                "percent": db_settings.get(f"{prefix}percent") or 1.0,
                "tp_percent": db_settings.get(f"{prefix}tp_percent") or 8.0,
                "sl_percent": db_settings.get(f"{prefix}sl_percent") or 3.0,
                "leverage": db_settings.get(f"{prefix}leverage") or 10,
                "use_atr": bool(db_settings.get(f"{prefix}use_atr", False)),
                "atr_trigger_pct": db_settings.get(f"{prefix}atr_trigger_pct"),
                "atr_step_pct": db_settings.get(f"{prefix}atr_step_pct"),
                "dca_enabled": bool(db_settings.get(f"{prefix}dca_enabled", False)),
                "dca_pct_1": db_settings.get(f"{prefix}dca_pct_1") or 10.0,
                "dca_pct_2": db_settings.get(f"{prefix}dca_pct_2") or 25.0,
                "max_positions": db_settings.get(f"{prefix}max_positions") or 0,
                "coins_group": db_settings.get(f"{prefix}coins_group") or db_settings.get("coins_group") or "ALL",
                "direction": db_settings.get("direction") or "all",
                "order_type": db_settings.get("order_type") or "market",
                # Break-Even settings
                "be_enabled": bool(db_settings.get(f"{prefix}be_enabled", False)),
                "be_trigger_pct": db_settings.get(f"{prefix}be_trigger_pct") or 1.0,
                # Partial Take Profit settings (2-step margin cut)
                "partial_tp_enabled": bool(db_settings.get(f"{prefix}partial_tp_enabled", False)),
                "partial_tp_1_trigger_pct": db_settings.get(f"{prefix}partial_tp_1_trigger_pct") or 2.0,
                "partial_tp_1_close_pct": db_settings.get(f"{prefix}partial_tp_1_close_pct") or 30.0,
                "partial_tp_2_trigger_pct": db_settings.get(f"{prefix}partial_tp_2_trigger_pct") or 5.0,
                "partial_tp_2_close_pct": db_settings.get(f"{prefix}partial_tp_2_close_pct") or 50.0,
            }
            
            result.append(settings_obj)
    
    return result


@router.put("/strategy-settings/mobile/{strategy_name}")
async def update_strategy_settings_mobile(
    strategy_name: str,
    settings: dict,
    user: dict = Depends(get_current_user)
):
    """Update strategy settings from iOS app.
    
    Accepts flat StrategySettings object and updates the corresponding side.
    
    Body:
        {
            "side": "long",
            "exchange": "bybit",
            "account_type": "demo",
            "percent": 1.5,
            "sl_percent": 3.0,
            ...
        }
    """
    user_id = user["user_id"]
    
    if strategy_name not in VALID_STRATEGIES:
        raise HTTPException(status_code=400, detail=f"Invalid strategy: {strategy_name}")
    
    side = settings.get("side", "long")
    if side not in ["long", "short"]:
        raise HTTPException(status_code=400, detail="Invalid side. Must be 'long' or 'short'")
    
    exchange = settings.get("exchange", "bybit")
    account_type = settings.get("account_type", "demo")
    
    # Fields that can be updated (with side prefix)
    updatable_fields = [
        "enabled", "percent", "tp_percent", "sl_percent", "leverage",
        "use_atr", "atr_trigger_pct", "atr_step_pct", 
        "dca_enabled", "dca_pct_1", "dca_pct_2",
        "max_positions", "coins_group", "limit_offset_pct", "order_type",
        # Break-Even
        "be_enabled", "be_trigger_pct",
        # Partial Take Profit
        "partial_tp_enabled",
        "partial_tp_1_trigger_pct", "partial_tp_1_close_pct",
        "partial_tp_2_trigger_pct", "partial_tp_2_close_pct",
    ]
    
    updated = []
    for field in updatable_fields:
        if field in settings:
            value = settings[field]
            # Add side prefix for DB
            db_field = f"{side}_{field}"
            
            # Type conversion
            if field in ("enabled", "use_atr", "dca_enabled", "be_enabled", "partial_tp_enabled"):
                value = bool(value)
            elif field in ("leverage", "max_positions"):
                value = int(value) if value is not None else None
            elif field in ("percent", "tp_percent", "sl_percent", "atr_trigger_pct", "atr_step_pct", 
                           "dca_pct_1", "dca_pct_2", "be_trigger_pct",
                           "partial_tp_1_trigger_pct", "partial_tp_1_close_pct",
                           "partial_tp_2_trigger_pct", "partial_tp_2_close_pct"):
                value = float(value) if value is not None else None
            
            db.set_strategy_setting_db(user_id, strategy_name, db_field, value, exchange, account_type)
            updated.append(field)
    
    # Non-side fields
    if "direction" in settings:
        db.set_strategy_setting_db(user_id, strategy_name, "direction", settings["direction"], exchange, account_type)
        updated.append("direction")
    
    if "order_type" in settings:
        db.set_strategy_setting_db(user_id, strategy_name, "order_type", settings["order_type"], exchange, account_type)
        updated.append("order_type")
    
    logger.info(f"User {user_id} updated {strategy_name}/{side} via mobile: {updated}")
    
    # Log activity for cross-platform sync (from iOS)
    try:
        from services.sync_service import sync_service
        import asyncio
        asyncio.create_task(sync_service.sync_settings_change(
            user_id=user_id,
            source="ios",  # Mobile endpoint = iOS
            setting_name=f"strategy_{strategy_name}_{side}",
            old_value=None,
            new_value=str({k: settings.get(k) for k in updated}),
            details={
                "strategy": strategy_name,
                "side": side,
                "exchange": exchange,
                "account_type": account_type,
                "updated_fields": updated
            }
        ))
    except Exception as e:
        logger.warning(f"Failed to log mobile strategy settings activity: {e}")
    
    return {"success": True, "strategy": strategy_name, "side": side, "updated_fields": updated}
