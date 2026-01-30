"""
Push Notifications API
======================
Endpoints for managing push notifications and device tokens.
Supports iOS (APNs) and WebApp (WebSocket).

Author: Enliko Team
Created: 2026-01-30
"""

import json
import logging
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from webapp.api.auth import get_current_user
from core.db_postgres import execute, execute_one, get_conn

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notifications", tags=["notifications"])


# ============================================================================
# Models
# ============================================================================

class DeviceTokenRequest(BaseModel):
    """Request to register device token"""
    device_token: str = Field(..., min_length=10, max_length=500)
    platform: str = Field(..., pattern="^(ios|android|web)$")
    device_name: Optional[str] = None
    app_version: Optional[str] = None
    os_version: Optional[str] = None


class NotificationPreferences(BaseModel):
    """User notification preferences"""
    trades_enabled: bool = True
    signals_enabled: bool = True
    price_alerts_enabled: bool = True
    daily_report_enabled: bool = True
    sound_enabled: bool = True
    vibration_enabled: bool = True
    
    # Specific notification types
    trade_opened: bool = True
    trade_closed: bool = True
    break_even: bool = True
    partial_tp: bool = True
    margin_warning: bool = True


class NotificationItem(BaseModel):
    """Notification item for list"""
    id: int
    type: str
    title: str
    message: str
    data: Optional[dict] = None
    is_read: bool = False
    created_at: datetime


class MarkReadRequest(BaseModel):
    """Request to mark notifications as read"""
    notification_ids: List[int]


# ============================================================================
# Device Token Management
# ============================================================================

@router.post("/devices/register")
async def register_device(request: DeviceTokenRequest, user: dict = Depends(get_current_user)):
    """
    Register device token for push notifications.
    Call this on app launch and when token refreshes.
    """
    user_id = user.get("user_id") or user.get("id")
    
    try:
        # Check if token already exists
        existing = execute_one("""
            SELECT id FROM user_devices 
            WHERE device_token = %s AND user_id = %s
        """, (request.device_token, user_id))
        
        if existing:
            # Update existing
            execute_one("""
                UPDATE user_devices 
                SET device_name = %s, app_version = %s, os_version = %s,
                    is_active = TRUE, updated_at = NOW()
                WHERE id = %s
            """, (request.device_name, request.app_version, request.os_version, existing["id"]))
        else:
            # Deactivate old tokens for this platform
            execute_one("""
                UPDATE user_devices 
                SET is_active = FALSE 
                WHERE user_id = %s AND platform = %s
            """, (user_id, request.platform))
            
            # Insert new token
            execute_one("""
                INSERT INTO user_devices 
                (user_id, device_token, platform, device_name, app_version, os_version, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, TRUE)
            """, (
                user_id, request.device_token, request.platform,
                request.device_name, request.app_version, request.os_version
            ))
        
        return {"status": "success", "message": "Device registered"}
    except Exception as e:
        logger.error(f"Failed to register device: {e}")
        raise HTTPException(status_code=500, detail="Failed to register device")


@router.delete("/devices/{device_token}")
async def unregister_device(device_token: str, user: dict = Depends(get_current_user)):
    """Unregister device token (on logout)"""
    user_id = user.get("user_id") or user.get("id")
    
    execute_one("""
        UPDATE user_devices SET is_active = FALSE 
        WHERE user_id = %s AND device_token = %s
    """, (user_id, device_token))
    
    return {"status": "success"}


@router.get("/devices")
async def get_devices(user: dict = Depends(get_current_user)):
    """Get list of registered devices"""
    user_id = user.get("user_id") or user.get("id")
    
    devices = execute("""
        SELECT id, platform, device_name, app_version, is_active, created_at, updated_at
        FROM user_devices 
        WHERE user_id = %s
        ORDER BY updated_at DESC
    """, (user_id,))
    
    return {"devices": devices or []}


# ============================================================================
# Notification Preferences
# ============================================================================

@router.get("/preferences")
async def get_notification_preferences(user: dict = Depends(get_current_user)):
    """Get user's notification preferences"""
    user_id = user.get("user_id") or user.get("id")
    
    prefs = execute_one("""
        SELECT * FROM notification_preferences WHERE user_id = %s
    """, (user_id,))
    
    if not prefs:
        # Return defaults
        return NotificationPreferences().dict()
    
    return {
        "trades_enabled": prefs.get("trades_enabled", True),
        "signals_enabled": prefs.get("signals_enabled", True),
        "price_alerts_enabled": prefs.get("price_alerts_enabled", True),
        "daily_report_enabled": prefs.get("daily_report_enabled", True),
        "sound_enabled": prefs.get("sound_enabled", True),
        "vibration_enabled": prefs.get("vibration_enabled", True),
        "trade_opened": prefs.get("trade_opened", True),
        "trade_closed": prefs.get("trade_closed", True),
        "break_even": prefs.get("break_even", True),
        "partial_tp": prefs.get("partial_tp", True),
        "margin_warning": prefs.get("margin_warning", True),
    }


@router.put("/preferences")
async def update_notification_preferences(
    prefs: NotificationPreferences, 
    user: dict = Depends(get_current_user)
):
    """Update notification preferences"""
    user_id = user.get("user_id") or user.get("id")
    
    execute_one("""
        INSERT INTO notification_preferences 
        (user_id, trades_enabled, signals_enabled, price_alerts_enabled, 
         daily_report_enabled, sound_enabled, vibration_enabled,
         trade_opened, trade_closed, break_even, partial_tp, margin_warning)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
            trades_enabled = EXCLUDED.trades_enabled,
            signals_enabled = EXCLUDED.signals_enabled,
            price_alerts_enabled = EXCLUDED.price_alerts_enabled,
            daily_report_enabled = EXCLUDED.daily_report_enabled,
            sound_enabled = EXCLUDED.sound_enabled,
            vibration_enabled = EXCLUDED.vibration_enabled,
            trade_opened = EXCLUDED.trade_opened,
            trade_closed = EXCLUDED.trade_closed,
            break_even = EXCLUDED.break_even,
            partial_tp = EXCLUDED.partial_tp,
            margin_warning = EXCLUDED.margin_warning,
            updated_at = NOW()
    """, (
        user_id,
        prefs.trades_enabled, prefs.signals_enabled, prefs.price_alerts_enabled,
        prefs.daily_report_enabled, prefs.sound_enabled, prefs.vibration_enabled,
        prefs.trade_opened, prefs.trade_closed, prefs.break_even,
        prefs.partial_tp, prefs.margin_warning
    ))
    
    return {"status": "success"}


# ============================================================================
# Notification History
# ============================================================================

@router.get("/history")
async def get_notification_history(
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False,
    user: dict = Depends(get_current_user)
):
    """Get notification history"""
    user_id = user.get("user_id") or user.get("id")
    
    where_clause = "WHERE user_id = %s"
    params = [user_id]
    
    if unread_only:
        where_clause += " AND is_read = FALSE"
    
    notifications = execute(f"""
        SELECT id, notification_type as type, title, message, data, 
               is_read, created_at
        FROM notification_queue
        {where_clause}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (*params, limit, offset))
    
    # Get unread count
    unread_count = execute_one(f"""
        SELECT COUNT(*) as count FROM notification_queue
        WHERE user_id = %s AND is_read = FALSE
    """, (user_id,))
    
    return {
        "notifications": notifications or [],
        "unread_count": unread_count.get("count", 0) if unread_count else 0
    }


@router.post("/mark-read")
async def mark_notifications_read(
    request: MarkReadRequest,
    user: dict = Depends(get_current_user)
):
    """Mark notifications as read"""
    user_id = user.get("user_id") or user.get("id")
    
    if not request.notification_ids:
        return {"status": "success", "marked": 0}
    
    placeholders = ",".join(["%s"] * len(request.notification_ids))
    execute_one(f"""
        UPDATE notification_queue 
        SET is_read = TRUE, read_at = NOW()
        WHERE id IN ({placeholders}) AND user_id = %s
    """, (*request.notification_ids, user_id))
    
    return {"status": "success", "marked": len(request.notification_ids)}


@router.post("/mark-all-read")
async def mark_all_read(user: dict = Depends(get_current_user)):
    """Mark all notifications as read"""
    user_id = user.get("user_id") or user.get("id")
    
    result = execute_one("""
        UPDATE notification_queue 
        SET is_read = TRUE, read_at = NOW()
        WHERE user_id = %s AND is_read = FALSE
    """, (user_id,))
    
    return {"status": "success"}


@router.delete("/clear")
async def clear_notifications(
    older_than_days: int = 30,
    user: dict = Depends(get_current_user)
):
    """Clear old notifications"""
    user_id = user.get("user_id") or user.get("id")
    
    execute_one("""
        DELETE FROM notification_queue 
        WHERE user_id = %s AND created_at < NOW() - INTERVAL '%s days'
    """, (user_id, older_than_days))
    
    return {"status": "success"}


# ============================================================================
# WebSocket for Real-Time Notifications
# ============================================================================

# Store active WebSocket connections
_ws_connections: dict = {}  # user_id -> list of websockets


@router.websocket("/ws/{token}")
async def notification_websocket(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for real-time notifications.
    Connect with JWT token in path.
    
    Messages from server:
    - {"type": "notification", "payload": {...}}
    - {"type": "ping"}
    
    Messages from client:
    - {"type": "pong"}
    - {"type": "mark_read", "ids": [1, 2, 3]}
    """
    from webapp.api.auth import decode_token
    
    # Verify token
    try:
        payload = decode_token(token)
        user_id = payload.get("user_id") or payload.get("sub")
        if not user_id:
            await websocket.close(code=4001, reason="Invalid token")
            return
    except Exception as e:
        logger.error(f"WebSocket auth failed: {e}")
        await websocket.close(code=4001, reason="Authentication failed")
        return
    
    await websocket.accept()
    
    # Register connection
    if user_id not in _ws_connections:
        _ws_connections[user_id] = []
    _ws_connections[user_id].append(websocket)
    
    logger.info(f"WebSocket connected for user {user_id}")
    
    try:
        # Send unread count on connect
        unread = execute_one("""
            SELECT COUNT(*) as count FROM notification_queue
            WHERE user_id = %s AND is_read = FALSE
        """, (user_id,))
        
        await websocket.send_json({
            "type": "connected",
            "unread_count": unread.get("count", 0) if unread else 0
        })
        
        # Keep connection alive
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=60.0  # 60 second timeout
                )
                
                if data.get("type") == "pong":
                    continue
                elif data.get("type") == "mark_read":
                    ids = data.get("ids", [])
                    if ids:
                        placeholders = ",".join(["%s"] * len(ids))
                        execute_one(f"""
                            UPDATE notification_queue 
                            SET is_read = TRUE 
                            WHERE id IN ({placeholders}) AND user_id = %s
                        """, (*ids, user_id))
                        
            except asyncio.TimeoutError:
                # Send ping
                await websocket.send_json({"type": "ping"})
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Unregister connection
        if user_id in _ws_connections:
            try:
                _ws_connections[user_id].remove(websocket)
                if not _ws_connections[user_id]:
                    del _ws_connections[user_id]
            except ValueError:
                pass
        logger.info(f"WebSocket disconnected for user {user_id}")


async def send_notification_to_user(user_id: int, notification: dict):
    """
    Send notification to user via WebSocket.
    Called from notification_service.
    """
    if user_id not in _ws_connections:
        return False
    
    ws_list = _ws_connections[user_id]
    sent = False
    
    for ws in ws_list[:]:  # Copy list to avoid modification during iteration
        try:
            await ws.send_json({
                "type": "notification",
                "payload": notification
            })
            sent = True
        except Exception as e:
            logger.error(f"Failed to send to WebSocket: {e}")
            try:
                ws_list.remove(ws)
            except ValueError:
                pass
    
    return sent


def get_connected_user_ids() -> List[int]:
    """Get list of user IDs with active WebSocket connections"""
    return list(_ws_connections.keys())


# Import for async
import asyncio
