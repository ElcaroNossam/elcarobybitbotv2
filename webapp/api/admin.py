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
        
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE is_allowed = 1 AND is_banned = 0")
        row = cur.fetchone()
        active = row['cnt'] if row else 0
        
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE license_type = 'premium' OR is_lifetime = 1")
        row = cur.fetchone()
        premium = row['cnt'] if row else 0
        
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE is_banned = 1")
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
    expires_ts = int((datetime.utcnow() + timedelta(days=data.days)).timestamp())
    
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
            VALUES (%s, %s, %s, %s, %s)
        """, (license_key, data.license_type, data.user_id, expires_at, data.days))
        
        conn.commit()
    
    # If user_id provided, activate license for user
    if data.user_id:
        db.set_user_field(data.user_id, "license_type", data.license_type)
        db.set_user_field(data.user_id, "license_expires", expires_ts)
    
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
        
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE is_allowed = 1 AND is_banned = 0")
        row = cur.fetchone()
        active_users = row['cnt'] if row else 0
        
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE license_type = 'premium' OR is_lifetime = 1")
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


# ============ PAYMENTS & SUBSCRIPTIONS MANAGEMENT ============

@router.get("/payments")
async def get_all_payments(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    admin: dict = Depends(require_admin)
):
    """Get all payment history with filters."""
    
    with get_db() as conn:
        cur = conn.cursor()
        offset = (page - 1) * limit
        
        # Build query based on filters
        where_clause = ""
        params = []
        if status:
            where_clause = "WHERE p.status = %s"
            params.append(status)
        
        cur.execute(f"""
            SELECT p.*, u.username, u.first_name
            FROM payment_history p
            LEFT JOIN users u ON p.user_id = u.user_id
            {where_clause}
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        
        payments = []
        for row in cur.fetchall():
            payments.append({
                "id": row["id"],
                "user_id": row["user_id"],
                "username": row.get("username"),
                "first_name": row.get("first_name"),
                "amount": float(row["amount"]) if row["amount"] else 0,
                "currency": row["currency"],
                "payment_type": row["payment_type"],
                "status": row["status"],
                "tx_hash": row.get("tx_hash"),
                "license_type": row.get("license_type"),
                "license_days": row.get("license_days"),
                "created_at": str(row["created_at"]) if row["created_at"] else None,
                "confirmed_at": str(row["confirmed_at"]) if row.get("confirmed_at") else None,
            })
        
        # Get totals
        cur.execute("SELECT COUNT(*) as cnt FROM payment_history")
        row = cur.fetchone()
        total = row['cnt'] if row else 0
        
        cur.execute("SELECT COUNT(*) as cnt FROM payment_history WHERE status = 'pending'")
        row = cur.fetchone()
        pending = row['cnt'] if row else 0
        
        cur.execute("SELECT COALESCE(SUM(amount), 0) as total FROM payment_history WHERE status = 'confirmed'")
        row = cur.fetchone()
        total_revenue = float(row['total']) if row else 0
        
        return {
            "total": total,
            "pending": pending,
            "total_revenue": total_revenue,
            "page": page,
            "pages": (total + limit - 1) // limit,
            "list": payments
        }


@router.post("/payments/{payment_id}/approve")
async def approve_payment(
    payment_id: int,
    admin: dict = Depends(require_admin)
):
    """Approve a pending payment and activate subscription."""
    
    with get_db() as conn:
        cur = conn.cursor()
        
        # Get payment details
        cur.execute("SELECT * FROM payment_history WHERE id = %s", (payment_id,))
        payment = cur.fetchone()
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        if payment["status"] != "pending":
            raise HTTPException(status_code=400, detail="Payment is not pending")
        
        # Update payment status
        cur.execute("""
            UPDATE payment_history 
            SET status = 'confirmed', confirmed_at = NOW()
            WHERE id = %s
        """, (payment_id,))
        
        # Activate user subscription
        user_id = payment["user_id"]
        license_type = payment.get("license_type") or "premium"
        license_days = payment.get("license_days") or 30
        
        expires_at = (datetime.utcnow() + timedelta(days=license_days)).isoformat()
        expires_ts = int((datetime.utcnow() + timedelta(days=license_days)).timestamp())
        
        db.set_user_field(user_id, "license_type", license_type)
        db.set_user_field(user_id, "license_expires", expires_ts)
        db.set_user_field(user_id, "is_allowed", 1)
        
        conn.commit()
        
        return {
            "success": True,
            "message": f"Payment approved. User {user_id} now has {license_type} until {expires_at}",
            "expires": expires_at
        }


@router.post("/payments/{payment_id}/reject")
async def reject_payment(
    payment_id: int,
    reason: str = "Payment rejected by admin",
    admin: dict = Depends(require_admin)
):
    """Reject a payment."""
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE payment_history 
            SET status = 'rejected'
            WHERE id = %s
        """, (payment_id,))
        conn.commit()
        
        return {"success": True, "message": "Payment rejected", "reason": reason}


# ============ USER BALANCE & PNL ============

@router.get("/users/{user_id}/balance")
async def get_user_balance_details(
    user_id: int,
    admin: dict = Depends(require_admin)
):
    """Get detailed balance and PnL info for a user."""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    creds = db.get_all_user_credentials(user_id)
    if not creds:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get positions count
    with get_db() as conn:
        cur = conn.cursor()
        
        # Active positions
        cur.execute("""
            SELECT COUNT(*) as cnt, account_type, exchange
            FROM active_positions 
            WHERE user_id = %s
            GROUP BY account_type, exchange
        """, (user_id,))
        positions_by_account = {}
        for row in cur.fetchall():
            key = f"{row.get('exchange', 'bybit')}:{row['account_type']}"
            positions_by_account[key] = row['cnt']
        
        # Trade stats
        cur.execute("""
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses,
                COALESCE(SUM(pnl), 0) as total_pnl,
                COALESCE(AVG(pnl), 0) as avg_pnl
            FROM trade_logs
            WHERE user_id = %s
        """, (user_id,))
        
        stats_row = cur.fetchone()
        trade_stats = {
            "total_trades": stats_row["total_trades"] or 0,
            "wins": stats_row["wins"] or 0,
            "losses": stats_row["losses"] or 0,
            "total_pnl": float(stats_row["total_pnl"] or 0),
            "avg_pnl": float(stats_row["avg_pnl"] or 0),
            "winrate": round((stats_row["wins"] or 0) / max(stats_row["total_trades"] or 1, 1) * 100, 1)
        }
        
        # Recent trades
        cur.execute("""
            SELECT symbol, side, pnl, pnl_pct, exit_reason, ts, account_type
            FROM trade_logs
            WHERE user_id = %s
            ORDER BY ts DESC
            LIMIT 20
        """, (user_id,))
        
        recent_trades = []
        for row in cur.fetchall():
            recent_trades.append({
                "symbol": row["symbol"],
                "side": row["side"],
                "pnl": float(row["pnl"]) if row["pnl"] else 0,
                "pnl_pct": float(row["pnl_pct"]) if row.get("pnl_pct") else 0,
                "exit_reason": row.get("exit_reason"),
                "ts": str(row["ts"]) if row["ts"] else None,
                "account_type": row.get("account_type", "demo")
            })
        
        # Payment history
        cur.execute("""
            SELECT * FROM payment_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 10
        """, (user_id,))
        
        payments = []
        for row in cur.fetchall():
            payments.append({
                "id": row["id"],
                "amount": float(row["amount"]) if row["amount"] else 0,
                "currency": row["currency"],
                "payment_type": row["payment_type"],
                "status": row["status"],
                "created_at": str(row["created_at"]) if row["created_at"] else None
            })
    
    return {
        "user_id": user_id,
        "username": creds.get("username"),
        "first_name": creds.get("first_name"),
        "license_type": creds.get("license_type"),
        "license_expires": creds.get("license_expires"),
        "is_lifetime": creds.get("is_lifetime", False),
        "exchange_type": creds.get("exchange_type", "bybit"),
        "trading_mode": creds.get("trading_mode", "demo"),
        "positions_by_account": positions_by_account,
        "trade_stats": trade_stats,
        "recent_trades": recent_trades,
        "payments": payments
    }


@router.post("/users/{user_id}/subscription")
async def update_user_subscription(
    user_id: int,
    license_type: str = "premium",
    days: int = 30,
    admin: dict = Depends(require_admin)
):
    """Manually set user subscription."""
    
    expires_at = (datetime.utcnow() + timedelta(days=days)).isoformat()
    expires_ts = int((datetime.utcnow() + timedelta(days=days)).timestamp())
    
    db.set_user_field(user_id, "license_type", license_type)
    db.set_user_field(user_id, "license_expires", expires_ts)
    db.set_user_field(user_id, "is_allowed", 1)
    
    return {
        "success": True,
        "message": f"Subscription set to {license_type} for {days} days",
        "expires": expires_at
    }


@router.post("/users/{user_id}/lifetime")
async def grant_lifetime(
    user_id: int,
    admin: dict = Depends(require_admin)
):
    """Grant lifetime subscription."""
    
    db.set_user_field(user_id, "is_lifetime", 1)
    db.set_user_field(user_id, "license_type", "lifetime")
    db.set_user_field(user_id, "is_allowed", 1)
    
    return {"success": True, "message": f"User {user_id} now has lifetime access"}


@router.delete("/users/{user_id}/subscription")
async def revoke_subscription(
    user_id: int,
    admin: dict = Depends(require_admin)
):
    """Revoke user subscription."""
    
    db.set_user_field(user_id, "license_type", None)
    db.set_user_field(user_id, "license_expires", None)
    db.set_user_field(user_id, "is_lifetime", 0)
    
    return {"success": True, "message": f"Subscription revoked for user {user_id}"}


@router.post("/users/{user_id}/settings")
async def update_user_settings(
    user_id: int,
    percent: Optional[float] = None,
    leverage: Optional[int] = None,
    tp_percent: Optional[float] = None,
    sl_percent: Optional[float] = None,
    admin: dict = Depends(require_admin)
):
    """Update user trading settings."""
    
    if percent is not None:
        db.set_user_field(user_id, "percent", percent)
    if leverage is not None:
        db.set_user_field(user_id, "leverage", leverage)
    if tp_percent is not None:
        db.set_user_field(user_id, "tp_percent", tp_percent)
    if sl_percent is not None:
        db.set_user_field(user_id, "sl_percent", sl_percent)
    
    return {"success": True, "message": "Settings updated"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: dict = Depends(require_admin)
):
    """Delete a user and all their data."""
    
    if user_id == ADMIN_ID:
        raise HTTPException(status_code=400, detail="Cannot delete admin")
    
    with get_db() as conn:
        cur = conn.cursor()
        
        # Delete related data first
        cur.execute("DELETE FROM active_positions WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM trade_logs WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM payment_history WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM user_strategy_settings WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM custom_strategies WHERE user_id = %s", (user_id,))
        
        # Delete user
        cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        
        conn.commit()
        affected = cur.rowcount
        
        return {"success": affected > 0, "message": f"User {user_id} deleted"}


# ============ DASHBOARD SUMMARY ============

@router.get("/dashboard")
async def get_dashboard(
    admin: dict = Depends(require_admin)
):
    """Get comprehensive admin dashboard data."""
    
    with get_db() as conn:
        cur = conn.cursor()
        
        # Users stats
        cur.execute("SELECT COUNT(*) as cnt FROM users")
        total_users = cur.fetchone()['cnt'] or 0
        
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE is_allowed = 1 AND is_banned = 0")
        active_users = cur.fetchone()['cnt'] or 0
        
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE license_type = 'premium' OR is_lifetime = 1")
        premium_users = cur.fetchone()['cnt'] or 0
        
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE DATE(created_at) = CURRENT_DATE")
        new_today = cur.fetchone()['cnt'] or 0
        
        # Revenue stats
        cur.execute("""
            SELECT 
                COALESCE(SUM(amount), 0) as total_revenue,
                COUNT(*) as total_payments
            FROM payment_history 
            WHERE status = 'confirmed'
        """)
        rev_row = cur.fetchone()
        total_revenue = float(rev_row['total_revenue']) if rev_row else 0
        total_payments = rev_row['total_payments'] or 0
        
        # This month revenue
        cur.execute("""
            SELECT COALESCE(SUM(amount), 0) as revenue
            FROM payment_history 
            WHERE status = 'confirmed' 
            AND created_at >= DATE_TRUNC('month', CURRENT_DATE)
        """)
        row = cur.fetchone()
        month_revenue = float(row['revenue']) if row else 0
        
        # Pending payments
        cur.execute("SELECT COUNT(*) as cnt FROM payment_history WHERE status = 'pending'")
        pending_payments = cur.fetchone()['cnt'] or 0
        
        # Positions stats
        cur.execute("SELECT COUNT(*) as cnt FROM active_positions")
        total_positions = cur.fetchone()['cnt'] or 0
        
        # Trades stats
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                COALESCE(SUM(pnl), 0) as total_pnl
            FROM trade_logs
        """)
        trades_row = cur.fetchone()
        
        # Today's trades
        cur.execute("""
            SELECT COUNT(*) as cnt, COALESCE(SUM(pnl), 0) as pnl
            FROM trade_logs
            WHERE DATE(ts) = CURRENT_DATE
        """)
        today_row = cur.fetchone()
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "premium": premium_users,
                "new_today": new_today
            },
            "revenue": {
                "total": total_revenue,
                "this_month": month_revenue,
                "total_payments": total_payments,
                "pending": pending_payments
            },
            "trading": {
                "active_positions": total_positions,
                "total_trades": trades_row['total'] or 0,
                "wins": trades_row['wins'] or 0,
                "total_pnl": float(trades_row['total_pnl'] or 0),
                "today_trades": today_row['cnt'] or 0,
                "today_pnl": float(today_row['pnl'] or 0)
            }
        }


# ============ COMPREHENSIVE DASHBOARD ============

@router.get("/dashboard/full")
async def get_full_dashboard(
    admin: dict = Depends(require_admin)
):
    """Get comprehensive admin dashboard with all statistics."""
    return db.get_admin_dashboard()


# ============ ALL POSITIONS (ADMIN VIEW) ============

@router.get("/positions")
async def get_all_positions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    exchange: Optional[str] = None,
    account_type: Optional[str] = None,
    strategy: Optional[str] = None,
    admin: dict = Depends(require_admin)
):
    """Get all positions across all users."""
    offset = (page - 1) * limit
    positions, total = db.get_all_positions_admin(
        exchange=exchange,
        account_type=account_type,
        strategy=strategy,
        limit=limit,
        offset=offset
    )
    
    return {
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "list": positions
    }


@router.post("/positions/{user_id}/{symbol}/close")
async def admin_close_position(
    user_id: int,
    symbol: str,
    exchange: Optional[str] = Query(None, description="Exchange: bybit or hyperliquid"),
    account_type: Optional[str] = Query(None, description="Account type: demo, real, testnet, mainnet"),
    admin: dict = Depends(require_admin)
):
    """Force close a specific position for a user."""
    # MULTITENANCY: Get position with exchange filter
    positions = db.pg_get_active_positions(user_id, exchange=exchange)
    position = next((p for p in positions if p.get("symbol") == symbol), None)
    
    if not position:
        raise HTTPException(status_code=404, detail=f"Position {symbol} not found for user {user_id}")
    
    # MULTITENANCY: Use position's exchange and account_type for removal
    pos_exchange = position.get("exchange") or exchange or "bybit"
    pos_account_type = position.get("account_type") or account_type or "demo"
    
    # Remove from database with correct exchange/account_type
    db.pg_remove_active_position(user_id, symbol, exchange=pos_exchange, account_type=pos_account_type)
    
    return {
        "success": True,
        "message": f"Position {symbol} removed for user {user_id} on {pos_exchange}/{pos_account_type}",
        "note": "Position removed from tracking. Manual close on exchange may be required."
    }


# ============ ALL TRADES (ADMIN VIEW) ============

@router.get("/trades")
async def get_all_trades(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    exchange: Optional[str] = None,
    account_type: Optional[str] = None,
    strategy: Optional[str] = None,
    pnl_filter: Optional[str] = Query(None, description="Filter: 'win' or 'loss'"),
    admin: dict = Depends(require_admin)
):
    """Get all trades across all users."""
    offset = (page - 1) * limit
    trades, total = db.get_all_trades_admin(
        exchange=exchange,
        account_type=account_type,
        strategy=strategy,
        pnl_filter=pnl_filter,
        limit=limit,
        offset=offset
    )
    
    return {
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "list": trades
    }


# ============ ALL SIGNALS (ADMIN VIEW) ============

@router.get("/signals")
async def get_all_signals(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    strategy: Optional[str] = None,
    symbol: Optional[str] = None,
    side: Optional[str] = None,
    admin: dict = Depends(require_admin)
):
    """Get all signals."""
    offset = (page - 1) * limit
    signals, total = db.get_all_signals_admin(
        strategy=strategy,
        symbol=symbol,
        side=side,
        limit=limit,
        offset=offset
    )
    
    return {
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "list": signals
    }


@router.delete("/signals/{signal_id}")
async def delete_signal(
    signal_id: int,
    admin: dict = Depends(require_admin)
):
    """Delete a signal."""
    success = db.delete_signal_admin(signal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Signal not found")
    return {"success": True, "message": f"Signal {signal_id} deleted"}


# ============ SYSTEM HEALTH ============

@router.get("/system/health")
async def get_system_health(
    admin: dict = Depends(require_admin)
):
    """Get system health metrics."""
    return db.get_system_health()


# ============ USER TRADING CONTROL ============

@router.post("/users/{user_id}/pause-trading")
async def pause_user_trading(
    user_id: int,
    admin: dict = Depends(require_admin)
):
    """Pause trading for a specific user."""
    success = db.pause_user_trading(user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to pause trading")
    return {"success": True, "message": f"Trading paused for user {user_id}"}


@router.post("/users/{user_id}/resume-trading")
async def resume_user_trading(
    user_id: int,
    admin: dict = Depends(require_admin)
):
    """Resume trading for a specific user."""
    success = db.resume_user_trading(user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to resume trading")
    return {"success": True, "message": f"Trading resumed for user {user_id}"}


# ============ BROADCASTS ============

class BroadcastRequest(BaseModel):
    message: str
    target: str = "all"  # 'all', 'premium', 'active', 'bybit', 'hyperliquid'


@router.post("/broadcast")
async def create_broadcast(
    request: BroadcastRequest,
    admin: dict = Depends(require_admin)
):
    """Create a broadcast message to send to users."""
    broadcast_id = db.add_broadcast_message(
        message=request.message,
        target=request.target,
        admin_id=admin.get("user_id")
    )
    
    if not broadcast_id:
        raise HTTPException(status_code=500, detail="Failed to create broadcast")
    
    return {
        "success": True,
        "broadcast_id": broadcast_id,
        "message": "Broadcast created. Use /send endpoint to send."
    }


@router.get("/broadcast/pending")
async def get_pending_broadcasts(
    admin: dict = Depends(require_admin)
):
    """Get pending broadcast messages."""
    broadcasts = db.get_pending_broadcasts()
    return {"list": broadcasts}


# ============ ERROR MANAGEMENT (API) ============

@router.get("/errors")
async def get_admin_errors(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    admin: dict = Depends(require_admin)
):
    """Get pending admin errors."""
    offset = (page - 1) * limit
    errors = db.get_pending_admin_errors(limit=limit + offset)
    page_errors = errors[offset:offset + limit]
    total = len(errors)
    
    return {
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "list": page_errors
    }


@router.get("/errors/stats")
async def get_error_stats(
    admin: dict = Depends(require_admin)
):
    """Get error statistics."""
    return db.get_error_stats()


@router.post("/errors/{error_id}/approve")
async def approve_error(
    error_id: int,
    admin: dict = Depends(require_admin)
):
    """Approve (silence) an error."""
    success = db.approve_admin_error(error_id)
    if not success:
        raise HTTPException(status_code=404, detail="Error not found")
    return {"success": True, "message": "Error approved"}


@router.post("/errors/approve-all")
async def approve_all_errors(
    admin: dict = Depends(require_admin)
):
    """Approve all pending errors."""
    errors = db.get_pending_admin_errors(limit=1000)
    count = 0
    for err in errors:
        if db.approve_admin_error(err["id"]):
            count += 1
    return {"success": True, "approved": count}


@router.post("/errors/user/{user_id}/approve")
async def approve_user_errors(
    user_id: int,
    admin: dict = Depends(require_admin)
):
    """Approve all errors for a specific user."""
    count = db.approve_all_user_errors(user_id)
    return {"success": True, "approved": count}
