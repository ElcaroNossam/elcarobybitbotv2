"""
Activity Log API

Endpoints for:
- Getting user activity history
- Cross-platform sync status
- Real-time activity WebSocket
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from datetime import datetime, timedelta
from typing import Optional, List
import logging

from webapp.api.auth import get_current_user
from services.sync_service import sync_service, get_user_activity

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/activity", tags=["activity"])


# ==================== Activity History ====================

@router.get("/history")
async def get_activity_history(
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    action_type: Optional[str] = None,
    source: Optional[str] = None,
    days: int = Query(30, le=90),
    user: dict = Depends(get_current_user)
):
    """
    Get user's activity history across all platforms.
    
    Tracks:
    - Settings changes (iOS, WebApp, Telegram)
    - Exchange switches
    - Trade actions
    - Logins
    """
    user_id = user["user_id"]
    
    from_date = datetime.now() - timedelta(days=days)
    
    activities = await sync_service.get_activity_history(
        user_id=user_id,
        limit=limit,
        offset=offset,
        action_type=action_type,
        source=source,
        from_date=from_date
    )
    
    return {
        "success": True,
        "activities": activities,
        "count": len(activities),
        "filters": {
            "action_type": action_type,
            "source": source,
            "days": days
        }
    }


@router.get("/recent")
async def get_recent_activity(
    limit: int = Query(10, le=50),
    user: dict = Depends(get_current_user)
):
    """Get most recent activity for quick sync check"""
    user_id = user["user_id"]
    
    activities = await sync_service.get_activity_history(
        user_id=user_id,
        limit=limit
    )
    
    return {
        "success": True,
        "activities": activities
    }


@router.get("/by-source/{source}")
async def get_activity_by_source(
    source: str,
    limit: int = Query(20, le=100),
    user: dict = Depends(get_current_user)
):
    """Get activity from specific source (ios, webapp, telegram)"""
    
    if source not in ["ios", "webapp", "telegram", "api"]:
        raise HTTPException(status_code=400, detail="Invalid source. Use: ios, webapp, telegram, api")
    
    user_id = user["user_id"]
    
    activities = await sync_service.get_activity_history(
        user_id=user_id,
        limit=limit,
        source=source
    )
    
    return {
        "success": True,
        "source": source,
        "activities": activities
    }


@router.get("/settings-changes")
async def get_settings_changes(
    limit: int = Query(20, le=100),
    user: dict = Depends(get_current_user)
):
    """Get history of settings changes only"""
    user_id = user["user_id"]
    
    activities = await sync_service.get_activity_history(
        user_id=user_id,
        limit=limit,
        action_type="settings_change"
    )
    
    return {
        "success": True,
        "settings_changes": activities
    }


# ==================== Sync Status ====================

@router.get("/sync-status")
async def get_sync_status(
    user: dict = Depends(get_current_user)
):
    """
    Get synchronization status across platforms.
    Shows which platforms have received latest updates.
    """
    user_id = user["user_id"]
    
    # Get last 5 activities to check sync status
    activities = await sync_service.get_activity_history(
        user_id=user_id,
        limit=5
    )
    
    # Calculate sync status
    platforms_synced = {
        "telegram": True,
        "webapp": True,
        "ios": True
    }
    
    pending_sync = []
    
    for activity in activities:
        if not activity.get("telegram_notified"):
            platforms_synced["telegram"] = False
            pending_sync.append({
                "platform": "telegram",
                "activity_id": activity["id"],
                "action": activity["action_type"]
            })
        if not activity.get("webapp_notified"):
            platforms_synced["webapp"] = False
            pending_sync.append({
                "platform": "webapp",
                "activity_id": activity["id"],
                "action": activity["action_type"]
            })
        if not activity.get("ios_notified"):
            platforms_synced["ios"] = False
            pending_sync.append({
                "platform": "ios",
                "activity_id": activity["id"],
                "action": activity["action_type"]
            })
    
    return {
        "success": True,
        "all_synced": all(platforms_synced.values()),
        "platforms": platforms_synced,
        "pending_sync": pending_sync[:10],  # Max 10 pending items
        "last_activity": activities[0] if activities else None
    }


# ==================== Manual Sync Trigger ====================

@router.post("/trigger-sync")
async def trigger_sync(
    request: Request,
    user: dict = Depends(get_current_user)
):
    """
    Trigger manual sync to all platforms.
    Useful when iOS/WebApp needs to refresh data.
    """
    user_id = user["user_id"]
    
    # Determine source
    user_agent = request.headers.get("user-agent", "").lower()
    if "lyxentrading" in user_agent or "ios" in user_agent:
        source = "ios"
    else:
        source = "webapp"
    
    # Log sync request
    await sync_service.log_activity(
        user_id=user_id,
        action_type="sync_request",
        action_category="system",
        source=source,
        entity_type="manual_sync",
        new_value={"requested_from": source},
        notify=True
    )
    
    return {
        "success": True,
        "message": "Sync triggered to all platforms"
    }


# ==================== Activity Stats ====================

@router.get("/stats")
async def get_activity_stats(
    days: int = Query(7, le=30),
    user: dict = Depends(get_current_user)
):
    """Get activity statistics for the user"""
    user_id = user["user_id"]
    
    from_date = datetime.now() - timedelta(days=days)
    
    # Get all activities for period
    activities = await sync_service.get_activity_history(
        user_id=user_id,
        limit=500,
        from_date=from_date
    )
    
    # Calculate stats
    stats = {
        "total_activities": len(activities),
        "by_source": {"ios": 0, "webapp": 0, "telegram": 0, "api": 0},
        "by_type": {},
        "by_day": {}
    }
    
    for activity in activities:
        # Count by source
        source = activity.get("source", "unknown")
        if source in stats["by_source"]:
            stats["by_source"][source] += 1
        
        # Count by type
        action_type = activity.get("action_type", "unknown")
        stats["by_type"][action_type] = stats["by_type"].get(action_type, 0) + 1
        
        # Count by day
        if activity.get("created_at"):
            day = activity["created_at"][:10]
            stats["by_day"][day] = stats["by_day"].get(day, 0) + 1
    
    return {
        "success": True,
        "period_days": days,
        "stats": stats
    }
