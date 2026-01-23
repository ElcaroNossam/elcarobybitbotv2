"""
Finance & Accounting API
========================
Full financial reporting for accountants and admins.
Includes revenue tracking, subscription analytics, transaction history,
and export capabilities for tax/accounting purposes.

Designed for multitenancy with mobile app support.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timedelta, date
from decimal import Decimal
import logging
import csv
import io

from webapp.api.auth import get_current_user, require_admin

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================
# MODELS
# ============================================

class FinancialSummary(BaseModel):
    """Financial summary for a period"""
    period_start: datetime
    period_end: datetime
    total_revenue_usd: float
    total_revenue_trc: float
    subscriptions_count: int
    new_subscriptions: int
    renewals: int
    cancellations: int
    refunds_usd: float
    net_revenue_usd: float
    average_transaction_usd: float


class TransactionRecord(BaseModel):
    """Single financial transaction"""
    id: str
    timestamp: datetime
    user_id: int
    username: Optional[str]
    transaction_type: str  # 'subscription', 'token_purchase', 'refund', 'payout'
    payment_method: str  # 'trc', 'ton', 'usdt', 'crypto'
    amount_usd: float
    amount_crypto: float
    crypto_currency: str
    status: str  # 'completed', 'pending', 'failed', 'refunded'
    reference: Optional[str]
    notes: Optional[str]


class SubscriptionAnalytics(BaseModel):
    """Subscription analytics data"""
    total_active: int
    by_plan: Dict[str, int]
    by_period: Dict[str, int]  # monthly, quarterly, yearly
    mrr: float  # Monthly Recurring Revenue
    arr: float  # Annual Recurring Revenue
    churn_rate: float
    ltv: float  # Customer Lifetime Value
    new_this_month: int
    cancelled_this_month: int


class RevenueByPeriod(BaseModel):
    """Revenue breakdown by time period"""
    period: str  # 'daily', 'weekly', 'monthly'
    data: List[Dict[str, Any]]


class ExportRequest(BaseModel):
    """Request for financial data export"""
    start_date: date
    end_date: date
    export_type: Literal['transactions', 'subscriptions', 'revenue', 'full']
    format: Literal['csv', 'json'] = 'csv'


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_db_connection():
    """Get PostgreSQL connection"""
    try:
        from core.db_postgres import get_conn
        return get_conn()
    except Exception as e:
        logger.error(f"DB connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")


def calculate_mrr(subscriptions: List[Dict]) -> float:
    """Calculate Monthly Recurring Revenue"""
    mrr = 0.0
    for sub in subscriptions:
        if sub.get('status') != 'active':
            continue
        period = sub.get('period', 'monthly')
        amount = sub.get('amount_usd', 0)
        if period == 'yearly':
            mrr += amount / 12
        elif period == 'quarterly':
            mrr += amount / 3
        else:
            mrr += amount
    return round(mrr, 2)


# ============================================
# ENDPOINTS - FINANCIAL DASHBOARD
# ============================================

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_finance_dashboard(
    period: str = Query("month", pattern="^(day|week|month|quarter|year)$"),
    admin: dict = Depends(require_admin)
):
    """
    Get comprehensive financial dashboard data.
    
    Returns:
    - Revenue summary
    - Subscription metrics
    - Transaction stats
    - Payment method breakdown
    """
    try:
        now = datetime.utcnow()
        
        # Calculate period start
        if period == "day":
            period_start = now - timedelta(days=1)
        elif period == "week":
            period_start = now - timedelta(weeks=1)
        elif period == "month":
            period_start = now - timedelta(days=30)
        elif period == "quarter":
            period_start = now - timedelta(days=90)
        else:  # year
            period_start = now - timedelta(days=365)
        
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Get total revenue from payment_history
            cur.execute("""
                SELECT 
                    COALESCE(SUM(amount_usd), 0) as total_revenue,
                    COUNT(*) as transaction_count,
                    COALESCE(AVG(amount_usd), 0) as avg_transaction
                FROM payment_history 
                WHERE status = 'completed' 
                AND created_at >= %s
            """, (period_start,))
            revenue_row = cur.fetchone()
            
            # Get subscription counts
            cur.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE license_type = 'premium') as premium,
                    COUNT(*) FILTER (WHERE license_type = 'basic') as basic,
                    COUNT(*) FILTER (WHERE license_type = 'trial') as trial,
                    COUNT(*) FILTER (WHERE is_lifetime = TRUE) as lifetime
                FROM users 
                WHERE is_allowed = TRUE AND is_banned = FALSE
            """)
            sub_row = cur.fetchone()
            
            # Get payment method breakdown
            cur.execute("""
                SELECT 
                    payment_method,
                    COUNT(*) as count,
                    COALESCE(SUM(amount_usd), 0) as total
                FROM payment_history 
                WHERE status = 'completed' 
                AND created_at >= %s
                GROUP BY payment_method
            """, (period_start,))
            payment_methods = {}
            for row in cur.fetchall():
                payment_methods[row[0] or 'unknown'] = {
                    'count': row[1],
                    'total_usd': float(row[2])
                }
            
            # Get TRC token stats
            cur.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN tx_type = 'purchase' THEN amount ELSE 0 END), 0) as purchased,
                    COALESCE(SUM(CASE WHEN tx_type = 'payment' THEN amount ELSE 0 END), 0) as spent,
                    COALESCE(SUM(CASE WHEN tx_type = 'reward' THEN amount ELSE 0 END), 0) as rewarded
                FROM elc_transactions 
                WHERE ts >= %s
            """, (period_start,))
            trc_row = cur.fetchone()
            
            # Get new users this period
            cur.execute("""
                SELECT COUNT(*) FROM users 
                WHERE created_at >= %s
            """, (period_start,))
            row = cur.fetchone()
            new_users = (row[0] if row else 0) or 0
            
            # Calculate MRR from active subscriptions
            cur.execute("""
                SELECT license_type, COUNT(*) 
                FROM users 
                WHERE is_allowed = TRUE AND is_banned = FALSE 
                AND license_type IS NOT NULL
                GROUP BY license_type
            """)
            
            # Estimate MRR based on subscription counts
            mrr = 0.0
            plan_prices = {'trial': 0, 'basic': 29, 'premium': 99}
            for row in cur.fetchall():
                plan = row[0] or 'trial'
                count = row[1]
                mrr += plan_prices.get(plan, 0) * count
            
        return {
            "success": True,
            "period": period,
            "period_start": period_start.isoformat(),
            "period_end": now.isoformat(),
            "revenue": {
                "total_usd": float(revenue_row[0]) if revenue_row else 0,
                "transactions": revenue_row[1] if revenue_row else 0,
                "average_transaction": float(revenue_row[2]) if revenue_row else 0,
                "mrr": mrr,
                "arr": mrr * 12
            },
            "subscriptions": {
                "premium": sub_row[0] if sub_row else 0,
                "basic": sub_row[1] if sub_row else 0,
                "trial": sub_row[2] if sub_row else 0,
                "lifetime": sub_row[3] if sub_row else 0,
                "total_active": sum(sub_row) if sub_row else 0
            },
            "trc_tokens": {
                "purchased": float(trc_row[0]) if trc_row else 0,
                "spent_on_subscriptions": float(trc_row[1]) if trc_row else 0,
                "rewarded": float(trc_row[2]) if trc_row else 0
            },
            "payment_methods": payment_methods,
            "new_users": new_users
        }
        
    except Exception as e:
        logger.exception(f"Finance dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions", response_model=Dict[str, Any])
async def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    user_id: Optional[int] = Query(None),
    admin: dict = Depends(require_admin)
):
    """
    Get paginated list of all financial transactions.
    Supports filtering by status, payment method, date range, and user.
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Build query
            where_clauses = []
            params = []
            
            if status:
                where_clauses.append("ph.status = %s")
                params.append(status)
            
            if payment_method:
                where_clauses.append("ph.payment_method = %s")
                params.append(payment_method)
            
            if start_date:
                where_clauses.append("ph.created_at >= %s")
                params.append(start_date)
            
            if end_date:
                where_clauses.append("ph.created_at <= %s")
                params.append(end_date + timedelta(days=1))
            
            if user_id:
                where_clauses.append("ph.user_id = %s")
                params.append(user_id)
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            # Get total count
            cur.execute(f"""
                SELECT COUNT(*) FROM payment_history ph WHERE {where_sql}
            """, params)
            row = cur.fetchone()
            total = row[0] if row else 0
            
            # Get transactions
            offset = (page - 1) * limit
            cur.execute(f"""
                SELECT 
                    ph.id, ph.user_id, ph.payment_type, ph.payment_method,
                    ph.amount_usd, ph.amount_crypto, ph.crypto_currency,
                    ph.status, ph.tx_hash, ph.created_at, ph.notes,
                    u.username, u.first_name
                FROM payment_history ph
                LEFT JOIN users u ON ph.user_id = u.user_id
                WHERE {where_sql}
                ORDER BY ph.created_at DESC
                LIMIT %s OFFSET %s
            """, params + [limit, offset])
            
            transactions = []
            for row in cur.fetchall():
                transactions.append({
                    "id": row[0],
                    "user_id": row[1],
                    "username": row[11] or row[12] or f"User #{row[1]}",
                    "type": row[2],
                    "payment_method": row[3],
                    "amount_usd": float(row[4]) if row[4] else 0,
                    "amount_crypto": float(row[5]) if row[5] else 0,
                    "crypto_currency": row[6] or "TRC",
                    "status": row[7],
                    "tx_hash": row[8],
                    "timestamp": row[9].isoformat() if row[9] else None,
                    "notes": row[10]
                })
            
        return {
            "success": True,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
            "transactions": transactions
        }
        
    except Exception as e:
        logger.exception(f"Transactions list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscriptions/analytics", response_model=Dict[str, Any])
async def get_subscription_analytics(
    admin: dict = Depends(require_admin)
):
    """
    Get detailed subscription analytics.
    Includes MRR, churn rate, LTV, and trends.
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Active subscriptions by plan
            cur.execute("""
                SELECT 
                    COALESCE(license_type, 'free') as plan,
                    COUNT(*) as count
                FROM users 
                WHERE is_allowed = TRUE AND is_banned = FALSE
                GROUP BY license_type
            """)
            by_plan = {row[0]: row[1] for row in cur.fetchall()}
            
            # Monthly subscription trends (last 6 months)
            cur.execute("""
                SELECT 
                    DATE_TRUNC('month', created_at) as month,
                    COUNT(*) as new_users,
                    COUNT(*) FILTER (WHERE license_type = 'premium') as premium,
                    COUNT(*) FILTER (WHERE license_type = 'basic') as basic
                FROM users
                WHERE created_at >= NOW() - INTERVAL '6 months'
                GROUP BY DATE_TRUNC('month', created_at)
                ORDER BY month DESC
            """)
            monthly_trends = []
            for row in cur.fetchall():
                monthly_trends.append({
                    "month": row[0].strftime("%Y-%m") if row[0] else None,
                    "new_users": row[1],
                    "premium": row[2],
                    "basic": row[3]
                })
            
            # Calculate churn (users who stopped being active)
            cur.execute("""
                SELECT COUNT(*) FROM users 
                WHERE is_allowed = FALSE 
                AND created_at >= NOW() - INTERVAL '30 days'
            """)
            row = cur.fetchone()
            churned = (row[0] if row else 0) or 0
            
            total_active = sum(by_plan.values())
            churn_rate = (churned / (total_active + churned) * 100) if (total_active + churned) > 0 else 0
            
            # Calculate MRR
            plan_prices = {'trial': 0, 'free': 0, 'basic': 29, 'premium': 99}
            mrr = sum(plan_prices.get(plan, 0) * count for plan, count in by_plan.items())
            
            # Estimate LTV (simplified: MRR / churn_rate * 100)
            ltv = (mrr / churn_rate * 100) if churn_rate > 0 else mrr * 12
            
        return {
            "success": True,
            "analytics": {
                "total_active": total_active,
                "by_plan": by_plan,
                "mrr": mrr,
                "arr": mrr * 12,
                "churn_rate_percent": round(churn_rate, 2),
                "estimated_ltv": round(ltv, 2),
                "monthly_trends": monthly_trends
            }
        }
        
    except Exception as e:
        logger.exception(f"Subscription analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/revenue/chart", response_model=Dict[str, Any])
async def get_revenue_chart(
    period: str = Query("month", pattern="^(week|month|quarter|year)$"),
    group_by: str = Query("day", pattern="^(day|week|month)$"),
    admin: dict = Depends(require_admin)
):
    """
    Get revenue chart data for visualization.
    """
    try:
        now = datetime.utcnow()
        
        if period == "week":
            period_start = now - timedelta(weeks=1)
        elif period == "month":
            period_start = now - timedelta(days=30)
        elif period == "quarter":
            period_start = now - timedelta(days=90)
        else:
            period_start = now - timedelta(days=365)
        
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            if group_by == "day":
                trunc = "day"
            elif group_by == "week":
                trunc = "week"
            else:
                trunc = "month"
            
            cur.execute(f"""
                SELECT 
                    DATE_TRUNC(%s, created_at) as period,
                    COALESCE(SUM(amount_usd), 0) as revenue,
                    COUNT(*) as transactions
                FROM payment_history 
                WHERE status = 'completed'
                AND created_at >= %s
                GROUP BY DATE_TRUNC(%s, created_at)
                ORDER BY period ASC
            """, (trunc, period_start, trunc))
            
            chart_data = []
            for row in cur.fetchall():
                chart_data.append({
                    "date": row[0].strftime("%Y-%m-%d") if row[0] else None,
                    "revenue": float(row[1]),
                    "transactions": row[2]
                })
        
        return {
            "success": True,
            "period": period,
            "group_by": group_by,
            "data": chart_data
        }
        
    except Exception as e:
        logger.exception(f"Revenue chart error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_financial_data(
    request: ExportRequest,
    admin: dict = Depends(require_admin)
):
    """
    Export financial data for accounting purposes.
    Supports CSV and JSON formats.
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Get transactions in date range
            cur.execute("""
                SELECT 
                    ph.id, ph.user_id, u.username, u.first_name,
                    ph.payment_type, ph.payment_method,
                    ph.amount_usd, ph.amount_crypto, ph.crypto_currency,
                    ph.status, ph.tx_hash, ph.created_at, ph.notes
                FROM payment_history ph
                LEFT JOIN users u ON ph.user_id = u.user_id
                WHERE ph.created_at >= %s AND ph.created_at <= %s
                ORDER BY ph.created_at ASC
            """, (request.start_date, request.end_date + timedelta(days=1)))
            
            transactions = []
            for row in cur.fetchall():
                transactions.append({
                    "id": row[0],
                    "user_id": row[1],
                    "username": row[2] or row[3] or f"User #{row[1]}",
                    "type": row[4],
                    "payment_method": row[5],
                    "amount_usd": float(row[6]) if row[6] else 0,
                    "amount_crypto": float(row[7]) if row[7] else 0,
                    "crypto_currency": row[8],
                    "status": row[9],
                    "tx_hash": row[10],
                    "date": row[11].strftime("%Y-%m-%d %H:%M:%S") if row[11] else None,
                    "notes": row[12]
                })
            
            # Calculate totals
            totals = {
                "total_transactions": len(transactions),
                "total_revenue_usd": sum(t["amount_usd"] for t in transactions if t["status"] == "completed"),
                "completed_transactions": len([t for t in transactions if t["status"] == "completed"]),
                "pending_transactions": len([t for t in transactions if t["status"] == "pending"]),
                "failed_transactions": len([t for t in transactions if t["status"] == "failed"])
            }
        
        if request.format == "json":
            return {
                "success": True,
                "export_date": datetime.utcnow().isoformat(),
                "period": {
                    "start": request.start_date.isoformat(),
                    "end": request.end_date.isoformat()
                },
                "totals": totals,
                "transactions": transactions
            }
        else:
            # Generate CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                "ID", "Date", "User ID", "Username", "Type", "Payment Method",
                "Amount USD", "Amount Crypto", "Currency", "Status", "TX Hash", "Notes"
            ])
            
            # Data rows
            for t in transactions:
                writer.writerow([
                    t["id"], t["date"], t["user_id"], t["username"],
                    t["type"], t["payment_method"], t["amount_usd"],
                    t["amount_crypto"], t["crypto_currency"], t["status"],
                    t["tx_hash"], t["notes"]
                ])
            
            # Summary row
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Transactions", totals["total_transactions"]])
            writer.writerow(["Total Revenue USD", totals["total_revenue_usd"]])
            writer.writerow(["Completed", totals["completed_transactions"]])
            writer.writerow(["Pending", totals["pending_transactions"]])
            writer.writerow(["Failed", totals["failed_transactions"]])
            
            csv_content = output.getvalue()
            
            return {
                "success": True,
                "format": "csv",
                "filename": f"financial_export_{request.start_date}_{request.end_date}.csv",
                "content": csv_content
            }
            
    except Exception as e:
        logger.exception(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS - PAYMENT MANAGEMENT
# ============================================

@router.post("/payments/{payment_id}/refund")
async def refund_payment(
    payment_id: int,
    reason: str = Query(..., min_length=5),
    admin: dict = Depends(require_admin)
):
    """
    Process a refund for a payment.
    Updates payment status and logs the refund.
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Check payment exists
            cur.execute("""
                SELECT user_id, amount_usd, status 
                FROM payment_history 
                WHERE id = %s
            """, (payment_id,))
            payment = cur.fetchone()
            
            if not payment:
                raise HTTPException(status_code=404, detail="Payment not found")
            
            if payment[2] != 'completed':
                raise HTTPException(status_code=400, detail="Can only refund completed payments")
            
            # Update payment status
            cur.execute("""
                UPDATE payment_history 
                SET status = 'refunded', 
                    notes = COALESCE(notes, '') || %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (f" | Refunded: {reason}", payment_id))
            
            # Log refund transaction
            cur.execute("""
                INSERT INTO payment_history 
                (user_id, payment_type, amount_usd, status, notes, created_at)
                VALUES (%s, 'refund', %s, 'completed', %s, NOW())
            """, (payment[0], -payment[1], f"Refund for payment #{payment_id}: {reason}"))
            
            conn.commit()
        
        return {
            "success": True,
            "message": f"Payment #{payment_id} refunded",
            "refund_amount": float(payment[1])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Refund error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending-payments")
async def get_pending_payments(
    admin: dict = Depends(require_admin)
):
    """
    Get all pending payments that need admin action.
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    ph.id, ph.user_id, u.username, u.first_name,
                    ph.payment_type, ph.payment_method,
                    ph.amount_usd, ph.tx_hash, ph.created_at
                FROM payment_history ph
                LEFT JOIN users u ON ph.user_id = u.user_id
                WHERE ph.status = 'pending'
                ORDER BY ph.created_at ASC
            """)
            
            pending = []
            for row in cur.fetchall():
                pending.append({
                    "id": row[0],
                    "user_id": row[1],
                    "username": row[2] or row[3] or f"User #{row[1]}",
                    "type": row[4],
                    "payment_method": row[5],
                    "amount_usd": float(row[6]) if row[6] else 0,
                    "tx_hash": row[7],
                    "created_at": row[8].isoformat() if row[8] else None
                })
        
        return {
            "success": True,
            "count": len(pending),
            "payments": pending
        }
        
    except Exception as e:
        logger.exception(f"Pending payments error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payments/{payment_id}/approve")
async def approve_payment(
    payment_id: int,
    admin: dict = Depends(require_admin)
):
    """
    Manually approve a pending payment.
    Activates the associated subscription.
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Get payment details
            cur.execute("""
                SELECT user_id, payment_type, amount_usd, license_type, license_days
                FROM payment_history 
                WHERE id = %s AND status = 'pending'
            """, (payment_id,))
            payment = cur.fetchone()
            
            if not payment:
                raise HTTPException(status_code=404, detail="Pending payment not found")
            
            user_id = payment[0]
            license_type = payment[3] or 'premium'
            license_days = payment[4] or 30
            
            # Update payment status
            cur.execute("""
                UPDATE payment_history 
                SET status = 'completed', 
                    updated_at = NOW()
                WHERE id = %s
            """, (payment_id,))
            
            # Activate subscription
            expires = datetime.utcnow() + timedelta(days=license_days)
            cur.execute("""
                UPDATE users 
                SET license_type = %s,
                    license_expires = %s,
                    is_allowed = TRUE
                WHERE user_id = %s
            """, (license_type, expires, user_id))
            
            conn.commit()
        
        return {
            "success": True,
            "message": f"Payment #{payment_id} approved, subscription activated",
            "user_id": user_id,
            "license_type": license_type,
            "expires": expires.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Approve payment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS - MOBILE APP API (Multitenancy ready)
# ============================================

@router.get("/user/subscription")
async def get_user_subscription(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user's subscription info.
    Mobile-friendly endpoint for apps.
    """
    user_id = current_user['user_id']
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    license_type, license_expires, is_lifetime,
                    is_allowed, created_at
                FROM users 
                WHERE user_id = %s
            """, (user_id,))
            user = cur.fetchone()
            
            if not user:
                return {
                    "success": True,
                    "subscription": None,
                    "is_active": False
                }
            
            license_type = user[0] or 'free'
            expires = user[1]
            is_lifetime = bool(user[2])
            is_allowed = bool(user[3])
            
            # Check if expired
            is_active = is_lifetime or (expires and expires > datetime.utcnow())
            days_left = None
            if expires and not is_lifetime:
                days_left = max(0, (expires - datetime.utcnow()).days)
            
            return {
                "success": True,
                "subscription": {
                    "plan": license_type,
                    "is_lifetime": is_lifetime,
                    "expires": expires.isoformat() if expires else None,
                    "days_left": days_left,
                    "is_active": is_active and is_allowed
                },
                "features": get_plan_features(license_type)
            }
            
    except Exception as e:
        logger.exception(f"User subscription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_plan_features(plan: str) -> Dict[str, Any]:
    """Get features available for a subscription plan"""
    features = {
        "free": {
            "ai_signals_per_day": 3,
            "backtests_per_day": 1,
            "copy_traders": 0,
            "custom_strategies": False,
            "priority_support": False,
            "advanced_terminal": False
        },
        "trial": {
            "ai_signals_per_day": 10,
            "backtests_per_day": 5,
            "copy_traders": 1,
            "custom_strategies": False,
            "priority_support": False,
            "advanced_terminal": True
        },
        "basic": {
            "ai_signals_per_day": 20,
            "backtests_per_day": 10,
            "copy_traders": 2,
            "custom_strategies": True,
            "priority_support": False,
            "advanced_terminal": True
        },
        "premium": {
            "ai_signals_per_day": -1,  # Unlimited
            "backtests_per_day": -1,  # Unlimited
            "copy_traders": 5,
            "custom_strategies": True,
            "priority_support": True,
            "advanced_terminal": True
        }
    }
    return features.get(plan, features["free"])


@router.get("/user/payment-history")
async def get_user_payment_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user's payment history.
    Mobile-friendly endpoint.
    """
    user_id = current_user['user_id']
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    id, payment_type, payment_method,
                    amount_usd, status, created_at
                FROM payment_history 
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (user_id, limit))
            
            history = []
            for row in cur.fetchall():
                history.append({
                    "id": row[0],
                    "type": row[1],
                    "method": row[2],
                    "amount_usd": float(row[3]) if row[3] else 0,
                    "status": row[4],
                    "date": row[5].isoformat() if row[5] else None
                })
        
        return {
            "success": True,
            "history": history
        }
        
    except Exception as e:
        logger.exception(f"User payment history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
