"""
Mobile API Layer
================
API layer specifically designed for mobile applications (Android/iOS).
Includes multitenancy support, device management, and mobile-specific endpoints.

Headers for multitenancy:
- X-Platform: 'android' | 'ios' | 'web'
- X-Device-ID: Unique device identifier
- X-App-Version: App version string
- Authorization: Bearer JWT token
"""
from fastapi import APIRouter, HTTPException, Depends, Header, Query, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timedelta
import logging
import hashlib
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================
# MODELS
# ============================================

class DeviceInfo(BaseModel):
    """Device registration info"""
    device_id: str
    platform: Literal['android', 'ios', 'web']
    device_model: Optional[str] = None
    os_version: Optional[str] = None
    app_version: str
    push_token: Optional[str] = None  # FCM/APNS token
    language: str = 'en'
    timezone: str = 'UTC'


class MobileLoginRequest(BaseModel):
    """Mobile login request"""
    user_id: int
    device_info: DeviceInfo
    auth_token: Optional[str] = None  # Telegram auth token if available


class MobileLoginResponse(BaseModel):
    """Mobile login response"""
    success: bool
    access_token: str
    refresh_token: str
    user: Dict[str, Any]
    device_registered: bool


class PushNotificationSettings(BaseModel):
    """Push notification preferences"""
    enabled: bool = True
    trade_signals: bool = True
    position_updates: bool = True
    price_alerts: bool = True
    news: bool = False
    marketing: bool = False


# ============================================
# DEPENDENCIES
# ============================================

def get_mobile_context(
    x_platform: str = Header(None, alias="X-Platform"),
    x_device_id: str = Header(None, alias="X-Device-ID"),
    x_app_version: str = Header(None, alias="X-App-Version"),
    authorization: str = Header(None)
):
    """
    Extract mobile context from headers.
    Returns dict with platform, device_id, app_version, and user_id (if authenticated).
    """
    context = {
        "platform": x_platform or "web",
        "device_id": x_device_id,
        "app_version": x_app_version,
        "user_id": None,
        "is_mobile": x_platform in ['android', 'ios']
    }
    
    # Extract user_id from JWT if present
    if authorization and authorization.startswith('Bearer '):
        try:
            from webapp.api.auth import decode_token
            token = authorization.replace('Bearer ', '')
            payload = decode_token(token)
            context["user_id"] = payload.get("user_id")
        except Exception:
            pass
    
    return context


def require_mobile_auth(
    context: dict = Depends(get_mobile_context)
):
    """Require authenticated mobile user"""
    if not context.get("user_id"):
        raise HTTPException(status_code=401, detail="Authentication required")
    return context


# ============================================
# DATABASE HELPERS
# ============================================

def get_db_connection():
    """Get PostgreSQL connection"""
    try:
        from core.db_postgres import get_conn
        return get_conn()
    except Exception as e:
        logger.error(f"DB connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")


def register_device(user_id: int, device_info: DeviceInfo) -> bool:
    """Register or update a device for push notifications"""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Upsert device
            cur.execute("""
                INSERT INTO user_devices 
                (user_id, device_id, platform, device_model, os_version, app_version, 
                 push_token, language, timezone, last_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (user_id, device_id) 
                DO UPDATE SET 
                    platform = EXCLUDED.platform,
                    device_model = EXCLUDED.device_model,
                    os_version = EXCLUDED.os_version,
                    app_version = EXCLUDED.app_version,
                    push_token = EXCLUDED.push_token,
                    language = EXCLUDED.language,
                    timezone = EXCLUDED.timezone,
                    last_active = NOW()
            """, (
                user_id, device_info.device_id, device_info.platform,
                device_info.device_model, device_info.os_version, device_info.app_version,
                device_info.push_token, device_info.language, device_info.timezone
            ))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Device registration error: {e}")
        return False


# ============================================
# ENDPOINTS - AUTH
# ============================================

@router.post("/auth/login", response_model=Dict[str, Any])
async def mobile_login(
    request: MobileLoginRequest,
    req: Request
):
    """
    Mobile app login endpoint.
    Registers device and returns tokens.
    """
    try:
        from webapp.api.auth import create_access_token
        
        user_id = request.user_id
        device_info = request.device_info
        
        # Verify user exists
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT user_id, username, first_name, license_type, 
                       exchange_type, lang, is_allowed, is_banned
                FROM users WHERE user_id = %s
            """, (user_id,))
            user_row = cur.fetchone()
            
            if not user_row:
                raise HTTPException(status_code=404, detail="User not found")
            
            if user_row[7]:  # is_banned
                raise HTTPException(status_code=403, detail="Account suspended")
        
        # Register device
        device_registered = register_device(user_id, device_info)
        
        # Create tokens (using existing create_access_token)
        is_admin = user_id == 511692487  # ADMIN_ID
        access_token = create_access_token(user_id, is_admin)
        
        # Generate simple refresh token (hash of user_id + device_id + secret)
        refresh_token = hashlib.sha256(f"{user_id}:{device_info.device_id}:refresh_secret_2026".encode()).hexdigest()
        
        # Log login
        client_ip = req.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not client_ip:
            client_ip = req.client.host if req.client else "unknown"
        
        logger.info(f"Mobile login: user={user_id}, platform={device_info.platform}, ip={client_ip}")
        
        return {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 24 * 3600,  # 24 hours (default JWT expiry)
            "user": {
                "user_id": user_row[0],
                "username": user_row[1],
                "first_name": user_row[2],
                "license_type": user_row[3] or "free",
                "exchange_type": user_row[4] or "bybit",
                "language": user_row[5] or "en",
                "is_allowed": bool(user_row[6])
            },
            "device_registered": device_registered
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Mobile login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/refresh")
async def refresh_token_endpoint(
    refresh_token: str,
    context: dict = Depends(get_mobile_context)
):
    """Refresh access token"""
    try:
        from webapp.api.auth import create_access_token
        
        # For now, just require user to be logged in via context
        # In production, implement proper refresh token validation
        user_id = context.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        is_admin = user_id == 511692487  # ADMIN_ID
        new_access_token = create_access_token(user_id, is_admin)
        
        return {
            "success": True,
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 24 * 3600
        }
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/auth/logout")
async def mobile_logout(
    context: dict = Depends(require_mobile_auth)
):
    """Logout and invalidate device session"""
    try:
        user_id = context["user_id"]
        device_id = context.get("device_id")
        
        if device_id:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE user_devices 
                    SET push_token = NULL, last_active = NOW()
                    WHERE user_id = %s AND device_id = %s
                """, (user_id, device_id))
                conn.commit()
        
        return {"success": True, "message": "Logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"success": True, "message": "Logged out"}


# ============================================
# ENDPOINTS - USER PROFILE
# ============================================

@router.get("/user/profile")
async def get_user_profile(
    context: dict = Depends(require_mobile_auth)
):
    """Get full user profile for mobile app"""
    user_id = context["user_id"]
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Get user info
            cur.execute("""
                SELECT 
                    user_id, username, first_name, last_name,
                    license_type, license_expires, is_lifetime,
                    exchange_type, trading_mode, lang,
                    percent, sl_percent, tp_percent, leverage,
                    created_at, is_allowed, is_banned,
                    hl_enabled
                FROM users WHERE user_id = %s
            """, (user_id,))
            user = cur.fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get active positions count
            cur.execute("""
                SELECT COUNT(*) FROM active_positions WHERE user_id = %s
            """, (user_id,))
            row = cur.fetchone()
            positions_count = (row[0] if row else 0) or 0
            
            # Get TRC balance
            cur.execute("""
                SELECT COALESCE(SUM(CASE WHEN tx_type IN ('purchase', 'reward', 'deposit') THEN amount 
                                         WHEN tx_type IN ('payment', 'withdrawal') THEN -amount 
                                         ELSE 0 END), 0)
                FROM elc_transactions WHERE user_id = %s
            """, (user_id,))
            row = cur.fetchone()
            trc_balance = (row[0] if row else 0) or 0
        
        # Subscription status
        license_type = user[4] or "free"
        license_expires = user[5]
        is_lifetime = bool(user[6])
        
        days_left = None
        if license_expires and not is_lifetime:
            days_left = max(0, (license_expires - datetime.utcnow()).days)
        
        is_premium = license_type in ['premium', 'pro'] or is_lifetime
        
        return {
            "success": True,
            "profile": {
                "user_id": user[0],
                "username": user[1],
                "first_name": user[2],
                "last_name": user[3],
                "language": user[9] or "en"
            },
            "subscription": {
                "plan": license_type,
                "is_lifetime": is_lifetime,
                "expires": license_expires.isoformat() if license_expires else None,
                "days_left": days_left,
                "is_active": bool(user[15]) and not bool(user[16]),
                "is_premium": is_premium
            },
            "trading": {
                "exchange": user[7] or "bybit",
                "mode": user[8] or "demo",
                "hyperliquid_enabled": bool(user[17]),
                "active_positions": positions_count,
                "default_settings": {
                    "entry_percent": user[10],
                    "sl_percent": user[11],
                    "tp_percent": user[12],
                    "leverage": user[13]
                }
            },
            "wallet": {
                "trc_balance": float(trc_balance)
            },
            "member_since": user[14].isoformat() if user[14] else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/user/settings")
async def update_user_settings(
    settings: Dict[str, Any],
    context: dict = Depends(require_mobile_auth)
):
    """Update user settings from mobile app"""
    user_id = context["user_id"]
    
    # Allowed settings to update
    allowed_fields = {
        'lang', 'percent', 'sl_percent', 'tp_percent', 'leverage',
        'trading_mode', 'exchange_type'
    }
    
    try:
        updates = {k: v for k, v in settings.items() if k in allowed_fields}
        
        if not updates:
            return {"success": True, "message": "No valid settings to update"}
        
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            set_clauses = ", ".join([f"{k} = %s" for k in updates.keys()])
            values = list(updates.values()) + [user_id]
            
            cur.execute(f"""
                UPDATE users SET {set_clauses}, updated_at = NOW()
                WHERE user_id = %s
            """, values)
            conn.commit()
        
        return {"success": True, "updated": list(updates.keys())}
        
    except Exception as e:
        logger.exception(f"Settings update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS - PUSH NOTIFICATIONS
# ============================================

@router.post("/notifications/register")
async def register_push_token(
    push_token: str,
    context: dict = Depends(require_mobile_auth)
):
    """Register FCM/APNS push token"""
    user_id = context["user_id"]
    device_id = context.get("device_id")
    platform = context.get("platform", "android")
    
    if not device_id:
        device_id = hashlib.sha256(f"{user_id}:{push_token}".encode()).hexdigest()[:32]
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO user_devices (user_id, device_id, platform, push_token, last_active, created_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (user_id, device_id) 
                DO UPDATE SET push_token = %s, last_active = NOW()
            """, (user_id, device_id, platform, push_token, push_token))
            conn.commit()
        
        return {"success": True, "message": "Push token registered"}
        
    except Exception as e:
        logger.exception(f"Push token registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications/settings")
async def get_notification_settings(
    context: dict = Depends(require_mobile_auth)
):
    """Get push notification preferences"""
    user_id = context["user_id"]
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT notification_settings FROM users WHERE user_id = %s
            """, (user_id,))
            row = cur.fetchone()
        
        settings = row[0] if row and row[0] else {}
        
        return {
            "success": True,
            "settings": {
                "enabled": settings.get("enabled", True),
                "trade_signals": settings.get("trade_signals", True),
                "position_updates": settings.get("position_updates", True),
                "price_alerts": settings.get("price_alerts", True),
                "news": settings.get("news", False),
                "marketing": settings.get("marketing", False)
            }
        }
        
    except Exception as e:
        logger.exception(f"Get notification settings error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/notifications/settings")
async def update_notification_settings(
    settings: PushNotificationSettings,
    context: dict = Depends(require_mobile_auth)
):
    """Update push notification preferences"""
    user_id = context["user_id"]
    
    try:
        import json
        
        settings_dict = settings.model_dump()
        
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE users 
                SET notification_settings = %s::jsonb
                WHERE user_id = %s
            """, (json.dumps(settings_dict), user_id))
            conn.commit()
        
        return {"success": True, "settings": settings_dict}
        
    except Exception as e:
        logger.exception(f"Update notification settings error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS - QUICK ACTIONS (Mobile-specific)
# ============================================

@router.get("/dashboard/quick")
async def get_quick_dashboard(
    context: dict = Depends(require_mobile_auth)
):
    """
    Quick dashboard data optimized for mobile.
    Returns essential data in a single call.
    """
    user_id = context["user_id"]
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Get user basics
            cur.execute("""
                SELECT exchange_type, trading_mode, license_type
                FROM users WHERE user_id = %s
            """, (user_id,))
            user = cur.fetchone()
            
            # Get active positions
            cur.execute("""
                SELECT symbol, side, entry_price, size, pnl, strategy
                FROM active_positions 
                WHERE user_id = %s
                ORDER BY open_ts DESC
                LIMIT 10
            """, (user_id,))
            positions = []
            for row in cur.fetchall():
                positions.append({
                    "symbol": row[0],
                    "side": row[1],
                    "entry_price": float(row[2]) if row[2] else 0,
                    "size": float(row[3]) if row[3] else 0,
                    "pnl": float(row[4]) if row[4] else 0,
                    "strategy": row[5]
                })
            
            # Get today's stats
            cur.execute("""
                SELECT 
                    COUNT(*) as trades,
                    COALESCE(SUM(pnl), 0) as total_pnl,
                    COUNT(*) FILTER (WHERE pnl > 0) as wins
                FROM trade_logs 
                WHERE user_id = %s 
                AND ts >= NOW() - INTERVAL '24 hours'
            """, (user_id,))
            stats = cur.fetchone()
        
        total_pnl = float(stats[1]) if stats else 0
        trades = stats[0] if stats else 0
        wins = stats[2] if stats else 0
        
        return {
            "success": True,
            "exchange": user[0] if user else "bybit",
            "mode": user[1] if user else "demo",
            "plan": user[2] if user else "free",
            "positions": positions,
            "stats_24h": {
                "trades": trades,
                "pnl": total_pnl,
                "wins": wins,
                "win_rate": (wins / trades * 100) if trades > 0 else 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.exception(f"Quick dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/app/config")
async def get_app_config(
    context: dict = Depends(get_mobile_context)
):
    """
    Get app configuration and feature flags.
    Useful for remote config without app update.
    """
    platform = context.get("platform", "web")
    app_version = context.get("app_version", "1.0.0")
    
    return {
        "success": True,
        "config": {
            "api_version": "2.0",
            "min_supported_version": "1.0.0",
            "force_update": False,
            "maintenance_mode": False,
            "features": {
                "copy_trading": True,
                "backtesting": True,
                "ai_signals": True,
                "hyperliquid": True,
                "trc_payments": True,
                "push_notifications": True
            },
            "links": {
                "support": "https://t.me/triacelo_support",
                "telegram_bot": "https://t.me/triacelo_bybit_bot",
                "website": "https://triacelo.com",
                "terms": "https://triacelo.com/terms",
                "privacy": "https://triacelo.com/privacy"
            },
            "rate_limits": {
                "api_calls_per_minute": 60,
                "signals_per_day_free": 3,
                "backtests_per_day_free": 1
            }
        }
    }
