"""
Admin API - Users and Licenses management
"""
import os
import sys
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
import secrets

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import db
from coin_params import ADMIN_ID

# Use PostgreSQL via centralized helper (NOT sqlite3!)
from webapp.api.db_helper import get_db

router = APIRouter()

from webapp.api.auth import get_current_user, require_admin


class LicenseCreate(BaseModel):
    license_type: str = "premium"
    days: int = 30
    user_id: Optional[int] = None


class UserAction(BaseModel):
    user_id: int


@router.get("/users")
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    admin: dict = Depends(require_admin)
):
    """Get all users with stats."""
    
    with get_db() as conn:
        cur = conn.cursor()
        
        # Get counts (with safe None handling)
        cur.execute("SELECT COUNT(*) as cnt FROM users")
        row = cur.fetchone()
        total = row['cnt'] if row else 0
        
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE is_allowed = TRUE AND is_banned = FALSE")
        row = cur.fetchone()
        active = row['cnt'] if row else 0
        
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE license_type = 'premium' OR is_lifetime = TRUE")
        row = cur.fetchone()
        premium = row['cnt'] if row else 0
        
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE is_banned = TRUE")
        row = cur.fetchone()
        banned = row['cnt'] if row else 0
        
        # Get users list
        offset = (page - 1) * limit
        
        if search:
            cur.execute("""
                SELECT user_id, first_name, username, is_allowed, is_banned, 
                       license_type, is_lifetime, exchange_type, lang,
                       created_at
                FROM users 
                WHERE CAST(user_id AS TEXT) LIKE ? OR username LIKE ? OR first_name LIKE ?
                ORDER BY user_id DESC 
                LIMIT ? OFFSET ?
            """, (f"%{search}%", f"%{search}%", f"%{search}%", limit, offset))
        else:
            cur.execute("""
                SELECT user_id, first_name, username, is_allowed, is_banned, 
                       license_type, is_lifetime, exchange_type, lang,
                       created_at
                FROM users 
                ORDER BY user_id DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset))
        
        users = []
        for row in cur.fetchall():
            users.append({
                "user_id": row["user_id"],
                "first_name": row["first_name"],
                "username": row["username"],
                "is_allowed": bool(row["is_allowed"]),
                "is_banned": bool(row["is_banned"]),
                "license_type": row["license_type"] or ("lifetime" if row["is_lifetime"] else "free"),
                "exchange_type": row["exchange_type"] or "bybit",
                "lang": row["lang"] or "en",
                "created_at": row["created_at"],
            })
        
        return {
            "total": total,
            "active": active,
            "premium": premium,
            "banned": banned,
            "page": page,
            "limit": limit,
            "list": users
        }


@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    admin: dict = Depends(require_admin)
):
    """Get detailed user info."""
    
    creds = db.get_all_user_credentials(user_id)
    if not creds:
        raise HTTPException(status_code=404, detail="User not found")
    
    exchange_status = db.get_exchange_status(user_id)
    hl_creds = db.get_hl_credentials(user_id)
    
    return {
        "user_id": user_id,
        "first_name": creds.get("first_name"),
        "username": creds.get("username"),
        "lang": creds.get("lang", "en"),
        "is_allowed": creds.get("is_allowed", False),
        "is_banned": creds.get("is_banned", False),
        "license_type": creds.get("license_type"),
        "license_expires": creds.get("license_expires"),
        "is_lifetime": creds.get("is_lifetime", False),
        
        # Trading settings
        "percent": creds.get("percent", 5),
        "leverage": creds.get("leverage", 10),
        "tp_percent": creds.get("tp_percent", 2),
        "sl_percent": creds.get("sl_percent", 1),
        
        # Exchange info
        "exchange_status": exchange_status,
        "bybit_configured": bool(creds.get("demo_api_key") or creds.get("real_api_key")),
        "hl_configured": bool(
            hl_creds.get("hl_testnet_private_key") or 
            hl_creds.get("hl_mainnet_private_key") or 
            hl_creds.get("hl_private_key")
        ),
        
        # Strategies
        "enable_scryptomera": creds.get("enable_scryptomera", False),
        "enable_elcaro": creds.get("enable_elcaro", False),
        "enable_wyckoff": creds.get("enable_wyckoff", False),
        "enable_scalper": creds.get("enable_scalper", False),
    }


@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    admin: dict = Depends(require_admin)
):
    """Ban a user."""
    if user_id == ADMIN_ID:
        raise HTTPException(status_code=400, detail="Cannot ban admin")
    
    db.set_user_field(user_id, "is_banned", 1)
    db.set_user_field(user_id, "is_allowed", 0)
    
    return {"success": True, "message": f"User {user_id} banned"}


@router.post("/users/{user_id}/unban")
async def unban_user(
    user_id: int,
    admin: dict = Depends(require_admin)
):
    """Unban a user."""
    db.set_user_field(user_id, "is_banned", 0)
    db.set_user_field(user_id, "is_allowed", 1)
    
    return {"success": True, "message": f"User {user_id} unbanned"}


@router.post("/users/{user_id}/approve")
async def approve_user(
    user_id: int,
    admin: dict = Depends(require_admin)
):
    """Approve a user."""
    db.set_user_field(user_id, "is_allowed", 1)
    db.set_user_field(user_id, "is_banned", 0)
    
    return {"success": True, "message": f"User {user_id} approved"}


@router.get("/licenses")
async def get_licenses(
    admin: dict = Depends(require_admin)
):
    """Get all licenses."""
    
    with get_db() as conn:
        cur = conn.cursor()
        
        # Check if licenses table exists (PostgreSQL uses information_schema)
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_name='licenses'")
        if not cur.fetchone():
            # Create licenses table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS licenses (
                    id SERIAL PRIMARY KEY,
                    license_key TEXT UNIQUE NOT NULL,
                    license_type TEXT DEFAULT 'premium',
                    user_id BIGINT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    days INTEGER DEFAULT 30
                )
            """)
            conn.commit()
        
        cur.execute("""
            SELECT license_key, license_type, user_id, created_at, expires_at, is_active, days
            FROM licenses
            ORDER BY created_at DESC
            LIMIT 100
        """)
        
        licenses = []
        for row in cur.fetchall():
            licenses.append({
                "key": row["license_key"],
                "type": row["license_type"],
                "user_id": row["user_id"],
                "created_at": str(row["created_at"]) if row["created_at"] else None,
                "expires_at": str(row["expires_at"]) if row["expires_at"] else None,
                "is_active": bool(row["is_active"]),
                "days": row["days"],
            })
        
        return {"list": licenses}


@router.post("/licenses")
async def create_license(
    data: LicenseCreate,
    admin: dict = Depends(require_admin)
):
    """Create a new license."""
    
    license_key = f"LYXEN-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"
    expires_at = (datetime.utcnow() + timedelta(days=data.days)).isoformat()
    
    with get_db() as conn:
        cur = conn.cursor()
        
        # Ensure table exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS licenses (
                id SERIAL PRIMARY KEY,
                license_key TEXT UNIQUE NOT NULL,
                license_type TEXT DEFAULT 'premium',
                user_id BIGINT,
                created_at TIMESTAMP DEFAULT NOW(),
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                days INTEGER DEFAULT 30
            )
        """)
        
        cur.execute("""
            INSERT INTO licenses (license_key, license_type, user_id, expires_at, days)
            VALUES (?, ?, ?, ?, ?)
        """, (license_key, data.license_type, data.user_id, expires_at, data.days))
        
        conn.commit()
    
    # If user_id provided, activate license for user
    if data.user_id:
        db.set_user_field(data.user_id, "license_type", data.license_type)
        db.set_user_field(data.user_id, "license_expires", expires_at)
    
    return {
        "success": True,
        "license_key": license_key,
        "expires_at": expires_at
    }


@router.delete("/licenses/{license_key}")
async def revoke_license(
    license_key: str,
    admin: dict = Depends(require_admin)
):
    """Revoke a license."""
    
    with get_db() as conn:
        cur = conn.cursor()
        
        # Get user_id before deleting
        cur.execute("SELECT user_id FROM licenses WHERE license_key = ?", (license_key,))
        row = cur.fetchone()
        
        if row and row.get('user_id'):
            # Remove license from user
            db.set_user_field(row['user_id'], "license_type", None)
            db.set_user_field(row['user_id'], "license_expires", None)
        
        cur.execute("DELETE FROM licenses WHERE license_key = ?", (license_key,))
        conn.commit()
    
    return {"success": True, "message": f"License {license_key} revoked"}


@router.get("/stats")
async def get_stats(
    admin: dict = Depends(require_admin)
):
    """Get system statistics."""
    
    with get_db() as conn:
        cur = conn.cursor()
        
        # Users stats (with safe None handling)
        cur.execute("SELECT COUNT(*) as cnt FROM users")
        row = cur.fetchone()
        total_users = row['cnt'] if row else 0
        
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE is_allowed = TRUE AND is_banned = FALSE")
        row = cur.fetchone()
        active_users = row['cnt'] if row else 0
        
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE license_type = 'premium' OR is_lifetime = TRUE")
        row = cur.fetchone()
        premium_users = row['cnt'] if row else 0
        
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE exchange_type = 'hyperliquid'")
        row = cur.fetchone()
        hl_users = row['cnt'] if row else 0
        
        # Today's stats - use DATE() for proper PostgreSQL date comparison
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE DATE(created_at) = CURRENT_DATE")
        row = cur.fetchone()
        new_today = row['cnt'] if row else 0
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "premium": premium_users,
                "hyperliquid": hl_users,
                "new_today": new_today,
            },
            "system": {
                "bot_status": "running",
                "webapp_status": "running",
            }
        }


# ============ STRATEGY MANAGEMENT ============

@router.get("/strategies")
async def get_all_strategies(
    admin: dict = Depends(require_admin),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
):
    """Get all custom strategies for admin review."""
    
    with get_db() as conn:
        cur = conn.cursor()
        offset = (page - 1) * limit
        
        # Get strategies with user info
        cur.execute("""
            SELECT s.id, s.user_id, s.name, s.description, s.is_active, s.is_public,
                   s.performance_stats, s.created_at, s.updated_at,
                   u.username, u.first_name
            FROM custom_strategies s
            LEFT JOIN users u ON s.user_id = u.user_id
            ORDER BY s.created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        strategies = []
        for row in cur.fetchall():
            strategies.append({
                "id": row["id"],
                "user_id": row["user_id"],
                "username": row["username"],
                "first_name": row["first_name"],
                "name": row["name"],
                "description": row["description"],
                "is_active": bool(row["is_active"]),
                "is_public": bool(row["is_public"]),
                "performance_stats": row["performance_stats"],
                "created_at": str(row["created_at"]) if row["created_at"] else None,
                "updated_at": str(row["updated_at"]) if row["updated_at"] else None,
            })
        
        cur.execute("SELECT COUNT(*) as cnt FROM custom_strategies")
        row = cur.fetchone()
        total = row['cnt'] if row else 0
        
        cur.execute("SELECT COUNT(*) as cnt FROM custom_strategies WHERE is_public = TRUE")
        row = cur.fetchone()
        public = row['cnt'] if row else 0
        
        return {
            "total": total,
            "public": public,
            "page": page,
            "limit": limit,
            "list": strategies
        }


@router.get("/strategies/marketplace")
async def get_marketplace_stats(
    admin: dict = Depends(require_admin)
):
    """Get marketplace statistics."""
    
    with get_db() as conn:
        cur = conn.cursor()
        
        # Total listings
        cur.execute("SELECT COUNT(*) as cnt FROM strategy_marketplace WHERE is_active = TRUE")
        row = cur.fetchone()
        active_listings = row['cnt'] if row else 0
        
        # Total sales
        cur.execute("SELECT COUNT(*) as cnt, COALESCE(SUM(amount_paid), 0) as total FROM strategy_purchases")
        row = cur.fetchone()
        total_sales = row['cnt'] or 0
        total_revenue = float(row['total'] or 0)
        
        # Platform share (50%)
        platform_revenue = total_revenue * 0.5
        
        # Pending payouts
        cur.execute("SELECT COUNT(*) as cnt, COALESCE(SUM(amount), 0) as total FROM seller_payouts WHERE status = 'pending'")
        row = cur.fetchone()
        pending_count = row['cnt'] or 0
        pending_amount = float(row['total'] or 0)
        
        # Top sellers
        cur.execute("""
            SELECT seller_id, COUNT(*) as sales, SUM(amount_paid) as revenue
            FROM strategy_purchases
            GROUP BY seller_id
            ORDER BY revenue DESC
            LIMIT 10
        """)
        top_sellers = []
        for row in cur.fetchall():
            top_sellers.append({
                "seller_id": row["seller_id"],
                "sales": row["sales"],
                "revenue": float(row["revenue"] or 0),
            })
        
        return {
            "active_listings": active_listings,
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "platform_revenue": platform_revenue,
            "pending_payouts": pending_count,
            "pending_amount": pending_amount,
            "top_sellers": top_sellers,
        }


@router.post("/strategies/{strategy_id}/feature")
async def feature_strategy(
    strategy_id: int,
    featured: bool = True,
    admin: dict = Depends(require_admin)
):
    """Feature or unfeature a strategy in marketplace."""
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE strategy_marketplace SET is_featured = ? WHERE strategy_id = ?
        """, (featured, strategy_id))
        
        conn.commit()
        return {"success": True, "strategy_id": strategy_id, "featured": featured}


@router.post("/strategies/{strategy_id}/approve")
async def approve_strategy(
    strategy_id: int,
    admin: dict = Depends(require_admin)
):
    """Approve a strategy for public listing."""
    
    with get_db() as conn:
        cur = conn.cursor()
        # Set strategy as public and active
        cur.execute("""
            UPDATE custom_strategies SET is_public = TRUE, is_active = TRUE WHERE id = ?
        """, (strategy_id,))
        
        conn.commit()
        return {"success": True, "strategy_id": strategy_id, "approved": True}


@router.post("/strategies/{strategy_id}/reject")
async def reject_strategy(
    strategy_id: int,
    reason: str = "Does not meet quality standards",
    admin: dict = Depends(require_admin)
):
    """Reject a strategy from public listing."""
    
    with get_db() as conn:
        cur = conn.cursor()
        # Remove from public
        cur.execute("""
            UPDATE custom_strategies SET is_public = FALSE WHERE id = ?
        """, (strategy_id,))
        
        # Remove from marketplace if listed
        cur.execute("""
            UPDATE strategy_marketplace SET is_active = FALSE WHERE strategy_id = ?
        """, (strategy_id,))
        
        conn.commit()
        return {"success": True, "strategy_id": strategy_id, "rejected": True, "reason": reason}


@router.delete("/strategies/{strategy_id}")
async def delete_strategy_admin(
    strategy_id: int,
    admin: dict = Depends(require_admin)
):
    """Delete a strategy (admin only)."""
    
    with get_db() as conn:
        cur = conn.cursor()
        # Delete from marketplace first
        cur.execute("DELETE FROM strategy_marketplace WHERE strategy_id = ?", (strategy_id,))
        
        # Delete strategy
        cur.execute("DELETE FROM custom_strategies WHERE id = ?", (strategy_id,))
        
        conn.commit()
        affected = cur.rowcount
        return {"success": affected > 0, "deleted": affected}


# ============ PAYOUTS MANAGEMENT ============

@router.get("/payouts")
async def get_payouts(
    status: str = Query(None),
    admin: dict = Depends(require_admin)
):
    """Get all payout requests."""
    
    with get_db() as conn:
        cur = conn.cursor()
        
        if status:
            cur.execute("""
                SELECT p.*, u.username, u.first_name
                FROM seller_payouts p
                LEFT JOIN users u ON p.seller_id = u.user_id
                WHERE p.status = ?
                ORDER BY p.requested_at DESC
            """, (status,))
        else:
            cur.execute("""
                SELECT p.*, u.username, u.first_name
                FROM seller_payouts p
                LEFT JOIN users u ON p.seller_id = u.user_id
                ORDER BY p.requested_at DESC
                LIMIT 100
            """)
        
        payouts = []
        for row in cur.fetchall():
            payouts.append({
                "id": row["id"],
                "seller_id": row["seller_id"],
                "username": row["username"],
                "first_name": row["first_name"],
                "amount": float(row["amount"]) if row["amount"] else 0,
                "currency": row["currency"],
                "status": row["status"],
                "tx_hash": row["tx_hash"],
                "requested_at": str(row["requested_at"]) if row["requested_at"] else None,
                "processed_at": str(row["processed_at"]) if row["processed_at"] else None,
            })
        
        return {"list": payouts}


@router.post("/payouts/{payout_id}/process")
async def process_payout(
    payout_id: int,
    tx_hash: str = None,
    admin: dict = Depends(require_admin)
):
    """Mark payout as processed."""
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE seller_payouts 
            SET status = 'completed', tx_hash = ?, processed_at = NOW()
            WHERE id = ?
        """, (tx_hash, payout_id))
        
        conn.commit()
        return {"success": True, "payout_id": payout_id, "status": "completed"}


@router.post("/payouts/{payout_id}/reject")
async def reject_payout(
    payout_id: int,
    reason: str = "Rejected by admin",
    admin: dict = Depends(require_admin)
):
    """Reject a payout request."""
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE seller_payouts SET status = 'failed' WHERE id = ?
        """, (payout_id,))
        
        conn.commit()
        return {"success": True, "payout_id": payout_id, "status": "failed", "reason": reason}


# ============ RANKINGS MANAGEMENT ============

@router.get("/rankings")
async def get_rankings(
    admin: dict = Depends(require_admin)
):
    """Get current strategy rankings."""
    
    rankings = db.get_top_strategies(limit=50)
    
    return {
        "total": len(rankings),
        "rankings": rankings
    }


@router.post("/rankings/refresh")
async def refresh_rankings(
    admin: dict = Depends(require_admin)
):
    """Force refresh all strategy rankings."""
    from services.strategy_service import StrategyRankingService
    
    try:
        ranking_service = StrategyRankingService()
        result = ranking_service.update_all_rankings()
        
        return {
            "success": True,
            "updated": result.get("updated", 0),
            "message": "Rankings refreshed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
