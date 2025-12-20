"""
Users API - Settings, Profile, Exchange switching
"""
import os
import sys
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import db

router = APIRouter()

from webapp.api.auth import get_current_user


class ExchangeSwitch(BaseModel):
    exchange: str


class LanguageChange(BaseModel):
    language: str


class SettingsUpdate(BaseModel):
    exchange: str = "bybit"
    settings: dict


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
    """Switch active exchange."""
    user_id = user["user_id"]
    
    if data.exchange not in ["bybit", "hyperliquid"]:
        raise HTTPException(status_code=400, detail="Invalid exchange")
    
    # Check if HL is configured before switching
    if data.exchange == "hyperliquid":
        hl_creds = db.get_hl_credentials(user_id)
        if not hl_creds.get("hl_private_key"):
            raise HTTPException(status_code=400, detail="HyperLiquid not configured")
    
    db.set_exchange_type(user_id, data.exchange)
    
    return {"success": True, "exchange": data.exchange}


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
