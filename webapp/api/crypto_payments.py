"""
Crypto Payments API - OxaPay Integration
=========================================
REST API endpoints for crypto payments via OxaPay.
Supports USDT (TRC20, BEP20, ERC20), BTC, ETH, TON, SOL and more.

Endpoints:
- POST /api/payments/create - Create payment invoice
- GET /api/payments/status/{payment_id} - Check payment status
- POST /api/payments/webhook - OxaPay webhook callback
- GET /api/payments/plans - Get available subscription plans
- GET /api/payments/currencies - Get supported currencies
- GET /api/payments/history - User payment history
- POST /api/payments/apply-promo - Apply promo code
"""

import logging
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request, Header, Depends
from pydantic import BaseModel, Field

from services.oxapay_service import (
    oxapay_service,
    LicensePlan,
    LicenseDuration,
    LICENSE_PRICES_USD,
    PLAN_FEATURES,
    PaymentStatus,
)
from webapp.api.auth import get_current_user
from core.db_postgres import get_conn, execute, execute_one

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crypto", tags=["Crypto Payments"])


# =============================================================================
# Request/Response Models
# =============================================================================

class CreatePaymentRequest(BaseModel):
    """Request to create a payment invoice."""
    plan: str = Field(..., description="Plan: basic, premium, enterprise")
    duration: str = Field(..., description="Duration: 1m, 3m, 6m, 1y")
    currency: str = Field(default="USDT", description="Crypto currency")
    network: Optional[str] = Field(default="TRC20", description="Network for currency")
    promo_code: Optional[str] = Field(default=None, description="Promo code for discount")


class PaymentResponse(BaseModel):
    """Payment invoice response."""
    payment_id: str
    address: str
    amount_usd: float
    amount_crypto: float
    currency: str
    network: str
    expires_at: str
    status: str
    qr_code_url: Optional[str] = None
    discount_percent: Optional[float] = None
    original_amount: Optional[float] = None


class PaymentStatusResponse(BaseModel):
    """Payment status response."""
    payment_id: str
    status: str
    amount_usd: float
    amount_crypto: float
    currency: str
    tx_hash: Optional[str] = None
    confirmed_at: Optional[str] = None
    plan: str
    duration: str


class PlanInfo(BaseModel):
    """Subscription plan information."""
    name: str
    display_name: str
    features: List[str]
    prices: dict


class CurrencyInfo(BaseModel):
    """Supported currency information."""
    symbol: str
    name: str
    networks: List[str]
    min_amount: float


class PromoCodeRequest(BaseModel):
    """Request to apply promo code."""
    code: str
    plan: str
    duration: str


class PromoCodeResponse(BaseModel):
    """Promo code validation response."""
    valid: bool
    discount_percent: Optional[float] = None
    final_amount: Optional[float] = None
    original_amount: Optional[float] = None
    message: str


class PaymentHistoryItem(BaseModel):
    """Payment history item."""
    payment_id: str
    amount_usd: float
    currency: str
    status: str
    plan: str
    duration: str
    created_at: str
    confirmed_at: Optional[str] = None


# =============================================================================
# Helper Functions
# =============================================================================

def validate_plan(plan: str) -> LicensePlan:
    """Validate and convert plan string to enum."""
    try:
        return LicensePlan(plan.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid plan: {plan}. Valid options: basic, premium, enterprise"
        )


def validate_duration(duration: str) -> LicenseDuration:
    """Validate and convert duration string to enum."""
    duration_map = {
        "1m": LicenseDuration.MONTH_1,
        "3m": LicenseDuration.MONTHS_3,
        "6m": LicenseDuration.MONTHS_6,
        "1y": LicenseDuration.YEAR_1,
        "month": LicenseDuration.MONTH_1,
        "quarter": LicenseDuration.MONTHS_3,
        "half_year": LicenseDuration.MONTHS_6,
        "year": LicenseDuration.YEAR_1,
    }
    
    if duration.lower() not in duration_map:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid duration: {duration}. Valid options: 1m, 3m, 6m, 1y"
        )
    
    return duration_map[duration.lower()]


async def get_promo_discount(code: str, user_id: int) -> Optional[dict]:
    """Get promo code discount if valid."""
    if not code:
        return None
    
    try:
        row = execute_one("""
            SELECT id, code, discount_percent, max_uses, current_uses, 
                   valid_from, valid_until, one_per_user
            FROM promo_codes
            WHERE code = %s AND is_active = TRUE
        """, (code.upper(),))
        
        if not row:
            return None
        
        # Check validity period
        now = datetime.utcnow()
        if row['valid_from'] and now < row['valid_from']:
            return None
        if row['valid_until'] and now > row['valid_until']:
            return None
        
        # Check max uses
        if row['max_uses'] and row['current_uses'] >= row['max_uses']:
            return None
        
        # Check one per user
        if row['one_per_user']:
            used = execute_one("""
                SELECT 1 FROM promo_code_usage 
                WHERE promo_code_id = %s AND user_id = %s
            """, (row['id'], user_id))
            if used:
                return None
        
        return {
            'id': row['id'],
            'discount_percent': float(row['discount_percent']),
        }
    except Exception as e:
        logger.warning(f"Error checking promo code: {e}")
        return None


async def record_promo_usage(promo_id: int, user_id: int, payment_id: str):
    """Record promo code usage."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            # Record usage
            cur.execute("""
                INSERT INTO promo_code_usage (promo_code_id, user_id, payment_id)
                VALUES (%s, %s, %s)
            """, (promo_id, user_id, payment_id))
            # Increment counter
            cur.execute("""
                UPDATE promo_codes SET current_uses = current_uses + 1 WHERE id = %s
            """, (promo_id,))
            conn.commit()
    except Exception as e:
        logger.error(f"Error recording promo usage: {e}")


# =============================================================================
# API Endpoints
# =============================================================================

@router.get("/plans", response_model=List[PlanInfo])
async def get_plans():
    """
    Get all available subscription plans with prices and features.
    
    Returns list of plans with:
    - Name and display name
    - Features included
    - Prices for each duration (1m, 3m, 6m, 1y)
    """
    plans = []
    
    for plan in LicensePlan:
        plan_prices = {}
        for duration in LicenseDuration:
            price = LICENSE_PRICES_USD.get(plan, {}).get(duration)
            if price:
                plan_prices[duration.value] = price
        
        plans.append(PlanInfo(
            name=plan.value,
            display_name=plan.value.capitalize(),
            features=PLAN_FEATURES.get(plan, []),
            prices=plan_prices,
        ))
    
    return plans


@router.get("/currencies", response_model=List[CurrencyInfo])
async def get_currencies():
    """
    Get list of supported cryptocurrencies for payment.
    
    Each currency has:
    - Symbol (USDT, BTC, ETH, etc.)
    - Full name
    - Supported networks
    - Minimum payment amount
    """
    currencies = [
        CurrencyInfo(
            symbol="USDT",
            name="Tether USD",
            networks=["TRC20", "BEP20", "ERC20", "Polygon", "Arbitrum", "TON"],
            min_amount=5.0,
        ),
        CurrencyInfo(
            symbol="BTC",
            name="Bitcoin",
            networks=["Bitcoin", "Lightning"],
            min_amount=10.0,
        ),
        CurrencyInfo(
            symbol="ETH",
            name="Ethereum",
            networks=["ERC20", "Arbitrum", "Optimism"],
            min_amount=10.0,
        ),
        CurrencyInfo(
            symbol="TON",
            name="Toncoin",
            networks=["TON"],
            min_amount=5.0,
        ),
        CurrencyInfo(
            symbol="SOL",
            name="Solana",
            networks=["Solana"],
            min_amount=5.0,
        ),
        CurrencyInfo(
            symbol="TRX",
            name="TRON",
            networks=["TRC20"],
            min_amount=10.0,
        ),
        CurrencyInfo(
            symbol="LTC",
            name="Litecoin",
            networks=["Litecoin"],
            min_amount=5.0,
        ),
    ]
    return currencies


@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    request: CreatePaymentRequest,
    user: dict = Depends(get_current_user)
):
    """
    Create a new payment invoice.
    
    User selects:
    - Plan (basic, premium, enterprise)
    - Duration (1m, 3m, 6m, 1y)
    - Currency (USDT, BTC, ETH, etc.)
    - Network (TRC20, BEP20, etc.)
    - Optional promo code
    
    Returns payment address and amount to send.
    """
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    # Validate inputs
    plan = validate_plan(request.plan)
    duration = validate_duration(request.duration)
    
    # Get base price
    base_price = LICENSE_PRICES_USD.get(plan, {}).get(duration)
    if not base_price:
        raise HTTPException(status_code=400, detail="Invalid plan/duration combination")
    
    # Check promo code
    discount_info = None
    discount_percent = 0.0
    if request.promo_code:
        discount_info = await get_promo_discount(request.promo_code, user_id)
        if discount_info:
            discount_percent = discount_info['discount_percent']
    
    # Calculate final amount
    if discount_percent > 0:
        final_amount = base_price * (1 - discount_percent / 100)
    else:
        final_amount = base_price
    
    try:
        # Create payment via OxaPay
        invoice = await oxapay_service.create_white_label_payment(
            user_id=user_id,
            plan=plan,
            duration=duration,
            currency=request.currency,
            network=request.network,
        )
        
        if not invoice:
            raise HTTPException(status_code=500, detail="Failed to create payment")
        
        # Record promo code usage if applied
        if discount_info:
            await record_promo_usage(
                discount_info['id'],
                user_id,
                invoice.payment_id
            )
            
            # Update payment amount in DB with discount
            with get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE crypto_payments 
                    SET amount_usd = %s, promo_code = %s, discount_percent = %s
                    WHERE payment_id = %s
                """, (final_amount, request.promo_code.upper(), discount_percent, invoice.payment_id))
                conn.commit()
        
        # Generate QR code URL
        qr_data = f"{invoice.currency.lower()}:{invoice.address}?amount={invoice.amount_crypto}"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={qr_data}"
        
        return PaymentResponse(
            payment_id=invoice.payment_id,
            address=invoice.address,
            amount_usd=final_amount if discount_percent > 0 else invoice.amount_usd,
            amount_crypto=invoice.amount_crypto * (1 - discount_percent / 100) if discount_percent > 0 else invoice.amount_crypto,
            currency=invoice.currency,
            network=invoice.network,
            expires_at=invoice.expires_at,
            status=invoice.status,
            qr_code_url=qr_url,
            discount_percent=discount_percent if discount_percent > 0 else None,
            original_amount=base_price if discount_percent > 0 else None,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment invoice")


@router.get("/status/{payment_id}", response_model=PaymentStatusResponse)
async def get_payment_status(
    payment_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Check status of a payment.
    
    Returns:
    - Current status (pending, confirming, confirmed, expired, failed)
    - Amount and currency
    - Transaction hash if confirmed
    - Confirmation timestamp
    """
    user_id = user.get("user_id")
    
    try:
        # Get from database
        row = execute_one("""
            SELECT payment_id, status, amount_usd, amount_crypto, currency,
                   tx_hash, confirmed_at, plan, duration
            FROM crypto_payments
            WHERE payment_id = %s AND user_id = %s
        """, (payment_id, user_id))
        
        if not row:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Also check with OxaPay for latest status
        oxapay_status = await oxapay_service.check_payment_status(payment_id)
        current_status = oxapay_status or row['status']
        
        return PaymentStatusResponse(
            payment_id=row['payment_id'],
            status=current_status,
            amount_usd=float(row['amount_usd']),
            amount_crypto=float(row['amount_crypto']) if row['amount_crypto'] else 0,
            currency=row['currency'],
            tx_hash=row['tx_hash'],
            confirmed_at=row['confirmed_at'].isoformat() if row['confirmed_at'] else None,
            plan=row['plan'],
            duration=row['duration'],
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get payment status")


@router.post("/webhook")
async def oxapay_webhook(request: Request):
    """
    OxaPay webhook endpoint.
    
    Called by OxaPay when payment status changes.
    Verifies signature and processes payment confirmation.
    Auto-activates license on successful payment.
    """
    try:
        # Get signature from header
        signature = request.headers.get("X-Oxapay-Signature", "")
        
        # Get raw body
        body = await request.body()
        body_str = body.decode("utf-8")
        
        # Verify signature
        if not oxapay_service.verify_webhook(body_str, signature):
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse JSON
        import json
        data = json.loads(body_str)
        
        # Process webhook
        result = await oxapay_service.process_webhook(data)
        
        if result:
            logger.info(f"Webhook processed successfully: {data.get('trackId')}")
            return {"status": "ok"}
        else:
            logger.warning(f"Webhook processing failed: {data}")
            return {"status": "error", "message": "Processing failed"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.post("/apply-promo", response_model=PromoCodeResponse)
async def apply_promo_code(
    request: PromoCodeRequest,
    user: dict = Depends(get_current_user)
):
    """
    Validate and apply a promo code.
    
    Returns:
    - Whether code is valid
    - Discount percentage
    - Final amount after discount
    """
    user_id = user.get("user_id")
    
    # Validate plan/duration
    plan = validate_plan(request.plan)
    duration = validate_duration(request.duration)
    
    # Get base price
    base_price = LICENSE_PRICES_USD.get(plan, {}).get(duration)
    if not base_price:
        raise HTTPException(status_code=400, detail="Invalid plan/duration")
    
    # Check promo code
    discount_info = await get_promo_discount(request.code, user_id)
    
    if not discount_info:
        return PromoCodeResponse(
            valid=False,
            message="Invalid or expired promo code"
        )
    
    discount = discount_info['discount_percent']
    final_amount = base_price * (1 - discount / 100)
    
    return PromoCodeResponse(
        valid=True,
        discount_percent=discount,
        final_amount=round(final_amount, 2),
        original_amount=base_price,
        message=f"{discount}% discount applied!"
    )


@router.get("/history", response_model=List[PaymentHistoryItem])
async def get_payment_history(
    user: dict = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """
    Get user's payment history.
    
    Returns list of past payments with status and details.
    """
    user_id = user.get("user_id")
    
    try:
        rows = execute("""
            SELECT payment_id, amount_usd, currency, status, plan, duration,
                   created_at, confirmed_at
            FROM crypto_payments
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (user_id, limit, offset))
        
        return [
            PaymentHistoryItem(
                payment_id=row['payment_id'],
                amount_usd=float(row['amount_usd']),
                currency=row['currency'],
                status=row['status'],
                plan=row['plan'],
                duration=row['duration'],
                created_at=row['created_at'].isoformat(),
                confirmed_at=row['confirmed_at'].isoformat() if row['confirmed_at'] else None,
            )
            for row in rows
        ]
        
    except Exception as e:
        logger.error(f"Error getting payment history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get payment history")


# =============================================================================
# Admin Endpoints (for promo code management)
# =============================================================================

class CreatePromoRequest(BaseModel):
    """Request to create promo code."""
    code: str
    discount_percent: float = Field(..., ge=1, le=100)
    max_uses: Optional[int] = None
    valid_days: Optional[int] = None
    one_per_user: bool = True


@router.post("/admin/promo", include_in_schema=False)
async def create_promo_code(
    request: CreatePromoRequest,
    user: dict = Depends(get_current_user)
):
    """Create a new promo code (admin only)."""
    from coin_params import ADMIN_ID
    
    user_id = user.get("user_id")
    if user_id != ADMIN_ID:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        valid_until = None
        if request.valid_days:
            from datetime import timedelta
            valid_until = datetime.utcnow() + timedelta(days=request.valid_days)
        
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO promo_codes (code, discount_percent, max_uses, valid_until, one_per_user)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                request.code.upper(),
                request.discount_percent,
                request.max_uses,
                valid_until,
                request.one_per_user,
            ))
            promo_id = cur.fetchone()[0]
            conn.commit()
        
        return {"id": promo_id, "code": request.code.upper(), "status": "created"}
        
    except Exception as e:
        logger.error(f"Error creating promo code: {e}")
        raise HTTPException(status_code=500, detail="Failed to create promo code")
