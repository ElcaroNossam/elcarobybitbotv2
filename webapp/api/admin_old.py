"""
Admin API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from webapp.api.auth import verify_token

router = APIRouter()


class AdminUserInfo(BaseModel):
    user_id: int
    username: Optional[str]
    license_type: str
    license_expires: Optional[datetime]
    is_banned: bool
    is_approved: bool
    created_at: datetime
    total_trades: int
    total_pnl: float


class UserListResponse(BaseModel):
    users: List[AdminUserInfo]
    total: int
    page: int
    per_page: int


class GrantLicenseRequest(BaseModel):
    user_id: int
    license_type: str
    days: int


class BroadcastRequest(BaseModel):
    message: str
    user_ids: Optional[List[int]] = None  # None = all users


class GlobalStats(BaseModel):
    total_users: int
    active_users: int
    premium_users: int
    total_trades: int
    total_volume: float
    total_pnl: float


def require_admin(payload: dict = Depends(verify_token)):
    """Verify user is admin"""
    # TODO: Check admin status in database
    user_id = int(payload.get("sub", 0))
    # if user_id not in ADMIN_IDS:
    #     raise HTTPException(403, "Admin access required")
    return payload


@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None,
    license_type: Optional[str] = None,
    payload: dict = Depends(require_admin)
):
    """List all users (admin only)"""
    # TODO: Query users from database
    return UserListResponse(users=[], total=0, page=page, per_page=per_page)


@router.get("/users/{user_id}", response_model=AdminUserInfo)
async def get_user_details(
    user_id: int,
    payload: dict = Depends(require_admin)
):
    """Get user details (admin only)"""
    # TODO: Get user from database
    raise HTTPException(404, "User not found")


@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    payload: dict = Depends(require_admin)
):
    """Ban a user"""
    # TODO: Update user in database
    return {"success": True, "message": f"User {user_id} banned"}


@router.post("/users/{user_id}/unban")
async def unban_user(
    user_id: int,
    payload: dict = Depends(require_admin)
):
    """Unban a user"""
    # TODO: Update user in database
    return {"success": True, "message": f"User {user_id} unbanned"}


@router.post("/users/{user_id}/approve")
async def approve_user(
    user_id: int,
    payload: dict = Depends(require_admin)
):
    """Approve a user"""
    # TODO: Update user in database
    return {"success": True, "message": f"User {user_id} approved"}


@router.post("/license/grant")
async def grant_license(
    request: GrantLicenseRequest,
    payload: dict = Depends(require_admin)
):
    """Grant license to user"""
    # TODO: Update license in database
    return {
        "success": True,
        "message": f"Granted {request.license_type} for {request.days} days"
    }


@router.post("/license/{user_id}/revoke")
async def revoke_license(
    user_id: int,
    payload: dict = Depends(require_admin)
):
    """Revoke user license"""
    # TODO: Update license in database
    return {"success": True, "message": f"License revoked for user {user_id}"}


@router.get("/stats", response_model=GlobalStats)
async def get_global_stats(payload: dict = Depends(require_admin)):
    """Get global statistics"""
    # TODO: Calculate stats from database
    return GlobalStats(
        total_users=0,
        active_users=0,
        premium_users=0,
        total_trades=0,
        total_volume=0.0,
        total_pnl=0.0
    )


@router.post("/broadcast")
async def broadcast_message(
    request: BroadcastRequest,
    payload: dict = Depends(require_admin)
):
    """Send broadcast message to users"""
    # TODO: Send messages via Telegram bot
    return {
        "success": True,
        "message": f"Message sent to {len(request.user_ids or [])} users"
    }


@router.get("/logs")
async def get_system_logs(
    limit: int = 100,
    level: str = "all",
    payload: dict = Depends(require_admin)
):
    """Get system logs"""
    # TODO: Get logs from log file
    return {"logs": []}
