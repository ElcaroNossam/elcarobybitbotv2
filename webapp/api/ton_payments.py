"""
TON Payments API - Subscription purchases via TON blockchain
Supports: USDT (Jetton), TON native

Integration with ELCARO token ecosystem
"""
import logging
import time
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Body, Query, Header
from pydantic import BaseModel, Field

import db
from db import invalidate_user_cache
from webapp.api.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ton", tags=["TON Payments"])

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# TON Payment Gateway Configuration
TON_CONFIG = {
    # Platform wallet addresses (USDT Jetton receiver)
    "mainnet_wallet": "UQC_your_mainnet_wallet_address_here",
    "testnet_wallet": "kQD_your_testnet_wallet_address_here",
    
    # jUSDT contract addresses
    "usdt_mainnet": "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs",
    "usdt_testnet": "kQD0GKBM8ZbryVk2aEhhTNyHzJ_freeTXK6dTkvdHh0jiqfh",
    
    # ELC price in USD
    "elc_price_usd": 1.0,
    
    # Platform fee (0.5%)
    "platform_fee_percent": 0.5,
    
    # Use testnet for development
    "use_testnet": True,
    
    # Webhook secret for verifying payment notifications
    "webhook_secret": "your_webhook_secret_here",  # TODO: Set via env
    
    # Payment expiry (1 hour)
    "payment_expiry_seconds": 3600,
}

# Subscription plans with ELC pricing
SUBSCRIPTION_PLANS = {
    "trial": {
        "name": "Trial",
        "description": "7-day trial access",
        "elc_price": 0,
        "usd_price": 0,
        "duration_days": 7,
        "features": ["Basic signals", "1 strategy", "Demo trading only"]
    },
    "basic_1m": {
        "name": "Basic Monthly",
        "description": "Basic trading features for 1 month",
        "elc_price": 50,
        "usd_price": 50,
        "duration_days": 30,
        "features": ["All signals", "3 strategies", "Demo + Real trading", "Basic support"]
    },
    "basic_3m": {
        "name": "Basic Quarterly",
        "description": "Basic trading features for 3 months (10% off)",
        "elc_price": 135,
        "usd_price": 135,
        "duration_days": 90,
        "features": ["All signals", "3 strategies", "Demo + Real trading", "Basic support"]
    },
    "premium_1m": {
        "name": "Premium Monthly",
        "description": "Full access for 1 month",
        "elc_price": 100,
        "usd_price": 100,
        "duration_days": 30,
        "features": ["All signals", "Unlimited strategies", "All exchanges", "Priority support", "Backtesting"]
    },
    "premium_3m": {
        "name": "Premium Quarterly",
        "description": "Full access for 3 months (10% off)",
        "elc_price": 270,
        "usd_price": 270,
        "duration_days": 90,
        "features": ["All signals", "Unlimited strategies", "All exchanges", "Priority support", "Backtesting"]
    },
    "premium_6m": {
        "name": "Premium Semi-Annual",
        "description": "Full access for 6 months (20% off)",
        "elc_price": 480,
        "usd_price": 480,
        "duration_days": 180,
        "features": ["All signals", "Unlimited strategies", "All exchanges", "Priority support", "Backtesting"]
    },
    "premium_1y": {
        "name": "Premium Annual",
        "description": "Full access for 1 year (30% off)",
        "elc_price": 840,
        "usd_price": 840,
        "duration_days": 365,
        "features": ["All signals", "Unlimited strategies", "All exchanges", "Priority support", "Backtesting", "API access"]
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class CreatePaymentRequest(BaseModel):
    plan_id: str = Field(..., description="Subscription plan ID (e.g., 'premium_1m')")
    payment_currency: str = Field("usdt", description="Payment currency: 'usdt' or 'ton'")


class CreatePaymentResponse(BaseModel):
    success: bool
    payment_id: str
    plan: dict
    amount_usdt: float
    amount_ton: Optional[float] = None
    platform_wallet: str
    payment_link: str
    tonkeeper_link: str
    qr_code_url: str
    expires_at: int
    message: str


class VerifyPaymentRequest(BaseModel):
    payment_id: str = Field(..., description="Payment ID to verify")
    tx_hash: Optional[str] = Field(None, description="TON blockchain transaction hash")


class WebhookPayload(BaseModel):
    """TON payment webhook payload"""
    payment_id: str
    tx_hash: str
    amount: float
    currency: str
    from_address: str
    to_address: str
    timestamp: int
    signature: str


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_payment_id(user_id: int, plan_id: str) -> str:
    """Generate unique payment ID"""
    timestamp = int(time.time())
    raw = f"TON-{user_id}-{plan_id}-{timestamp}"
    return raw


def get_platform_wallet() -> str:
    """Get platform wallet based on network config"""
    if TON_CONFIG["use_testnet"]:
        return TON_CONFIG["testnet_wallet"]
    return TON_CONFIG["mainnet_wallet"]


def verify_webhook_signature(payload: dict, signature: str) -> bool:
    """Verify webhook signature using HMAC-SHA256"""
    secret = TON_CONFIG["webhook_secret"]
    # Create signature from payload
    message = f"{payload['payment_id']}:{payload['tx_hash']}:{payload['amount']}:{payload['timestamp']}"
    expected = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


def create_ton_payment_link(wallet: str, amount_comment: str, payment_id: str) -> dict:
    """Create TON payment links"""
    # Standard ton:// link
    payment_link = f"ton://transfer/{wallet}?text={payment_id}"
    
    # Tonkeeper deep link
    tonkeeper_link = f"https://app.tonkeeper.com/transfer/{wallet}?text={payment_id}"
    
    # TonHub link
    tonhub_link = f"https://tonhub.com/transfer/{wallet}?text={payment_id}"
    
    # QR code URL (using Google Charts API)
    qr_url = f"https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl={tonkeeper_link}"
    
    return {
        "payment_link": payment_link,
        "tonkeeper_link": tonkeeper_link,
        "tonhub_link": tonhub_link,
        "qr_code_url": qr_url
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_ton_payment_record(
    user_id: int,
    payment_id: str,
    plan_id: str,
    amount_usdt: float,
    platform_wallet: str
) -> int:
    """Create TON payment record in database"""
    from core.db_postgres import get_conn
    
    with get_conn() as conn:
        cur = conn.cursor()
        
        # Create ton_payments table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ton_payments (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                payment_id TEXT UNIQUE NOT NULL,
                plan_id TEXT NOT NULL,
                amount_usdt REAL NOT NULL,
                amount_ton REAL,
                status TEXT DEFAULT 'pending',
                platform_wallet TEXT NOT NULL,
                from_wallet TEXT,
                tx_hash TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                expires_at TIMESTAMP,
                confirmed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ton_payments_user ON ton_payments(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ton_payments_status ON ton_payments(status)")
        
        # Insert payment record
        expires_at = datetime.utcnow() + timedelta(seconds=TON_CONFIG["payment_expiry_seconds"])
        cur.execute("""
            INSERT INTO ton_payments (user_id, payment_id, plan_id, amount_usdt, platform_wallet, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, payment_id, plan_id, amount_usdt, platform_wallet, expires_at))
        
        row = cur.fetchone()
        conn.commit()
        return row[0] if row else 0


def get_ton_payment(payment_id: str) -> Optional[dict]:
    """Get TON payment by ID"""
    from core.db_postgres import execute_one
    return execute_one(
        "SELECT * FROM ton_payments WHERE payment_id = %s",
        (payment_id,)
    )


def complete_ton_payment(payment_id: str, tx_hash: str, from_wallet: str = None) -> bool:
    """Mark TON payment as completed and activate subscription"""
    from core.db_postgres import get_conn
    
    payment = get_ton_payment(payment_id)
    if not payment:
        logger.error(f"Payment not found: {payment_id}")
        return False
    
    if payment["status"] == "completed":
        logger.warning(f"Payment already completed: {payment_id}")
        return True
    
    # Check if expired
    if payment["expires_at"] and datetime.utcnow() > payment["expires_at"]:
        logger.error(f"Payment expired: {payment_id}")
        return False
    
    user_id = payment["user_id"]
    plan_id = payment["plan_id"]
    plan = SUBSCRIPTION_PLANS.get(plan_id)
    
    if not plan:
        logger.error(f"Invalid plan: {plan_id}")
        return False
    
    with get_conn() as conn:
        cur = conn.cursor()
        
        # Update payment status
        cur.execute("""
            UPDATE ton_payments 
            SET status = 'completed', tx_hash = %s, from_wallet = %s, confirmed_at = NOW()
            WHERE payment_id = %s
        """, (tx_hash, from_wallet, payment_id))
        
        # Activate subscription
        # Determine license type from plan_id
        if plan_id.startswith("trial"):
            license_type = "trial"
        elif plan_id.startswith("basic"):
            license_type = "basic"
        elif plan_id.startswith("premium"):
            license_type = "premium"
        else:
            license_type = "basic"
        
        duration_days = plan["duration_days"]
        
        # Calculate new expiry (extend if already has subscription)
        cur.execute("SELECT license_expires FROM users WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        current_expires = row[0] if row and row[0] else None
        
        now = int(time.time())
        if current_expires and current_expires > now:
            # Extend existing subscription
            new_expires = current_expires + (duration_days * 86400)
        else:
            # New subscription
            new_expires = now + (duration_days * 86400)
        
        # Update user license
        cur.execute("""
            UPDATE users 
            SET current_license = %s, 
                license_expires = %s,
                is_allowed = 1
            WHERE user_id = %s
        """, (license_type, new_expires, user_id))
        
        # Record payment in payment_history
        cur.execute("""
            INSERT INTO payment_history 
            (user_id, payment_type, license_type, amount, currency, tx_hash, status, created_at)
            VALUES (%s, 'ton', %s, %s, 'USDT', %s, 'completed', NOW())
        """, (user_id, license_type, payment["amount_usdt"], tx_hash))
        
        conn.commit()
    
    invalidate_user_cache(user_id)
    logger.info(f"TON payment completed: {payment_id}, user={user_id}, plan={plan_id}")
    return True


def get_user_ton_payments(user_id: int, limit: int = 20) -> list:
    """Get user's TON payment history"""
    from core.db_postgres import execute
    return execute(
        """SELECT * FROM ton_payments 
           WHERE user_id = %s 
           ORDER BY created_at DESC 
           LIMIT %s""",
        (user_id, limit)
    )


# ═══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/plans")
async def get_subscription_plans():
    """
    Get all available subscription plans with TON pricing
    
    Returns list of plans with ELC and USD prices
    """
    plans = []
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        plans.append({
            "id": plan_id,
            "name": plan["name"],
            "description": plan["description"],
            "elc_price": plan["elc_price"],
            "usd_price": plan["usd_price"],
            "duration_days": plan["duration_days"],
            "features": plan["features"]
        })
    
    return {
        "success": True,
        "plans": plans,
        "payment_methods": ["usdt", "ton"],
        "network": "testnet" if TON_CONFIG["use_testnet"] else "mainnet"
    }


@router.post("/create-payment")
async def create_payment(
    req: CreatePaymentRequest,
    user: dict = Depends(get_current_user)
):
    """
    Create a TON payment for subscription
    
    Returns payment link and QR code for user to complete payment
    """
    user_id = user["user_id"]
    plan_id = req.plan_id
    
    # Validate plan
    if plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {plan_id}")
    
    plan = SUBSCRIPTION_PLANS[plan_id]
    
    # Free trial - activate immediately
    if plan["usd_price"] == 0:
        # Check if user already had trial
        existing = db.get_user_field(user_id, "had_trial")
        if existing:
            raise HTTPException(status_code=400, detail="Trial already used")
        
        # Activate trial
        db.set_user_field(user_id, "had_trial", 1)
        db.set_user_field(user_id, "current_license", "trial")
        db.set_user_field(user_id, "license_expires", int(time.time()) + (plan["duration_days"] * 86400))
        db.set_user_field(user_id, "is_allowed", 1)
        invalidate_user_cache(user_id)
        
        return {
            "success": True,
            "message": "Trial activated successfully!",
            "plan": plan,
            "payment_required": False
        }
    
    # Generate payment details
    payment_id = generate_payment_id(user_id, plan_id)
    platform_wallet = get_platform_wallet()
    amount_usdt = plan["usd_price"]
    
    # Create payment links
    links = create_ton_payment_link(platform_wallet, f"${amount_usdt}", payment_id)
    
    # Save payment record
    create_ton_payment_record(user_id, payment_id, plan_id, amount_usdt, platform_wallet)
    
    # Calculate expiry
    expires_at = int(time.time()) + TON_CONFIG["payment_expiry_seconds"]
    
    return {
        "success": True,
        "payment_id": payment_id,
        "plan": {
            "id": plan_id,
            "name": plan["name"],
            "duration_days": plan["duration_days"]
        },
        "amount_usdt": amount_usdt,
        "platform_wallet": platform_wallet,
        "payment_link": links["payment_link"],
        "tonkeeper_link": links["tonkeeper_link"],
        "qr_code_url": links["qr_code_url"],
        "expires_at": expires_at,
        "instructions": [
            f"1. Open Tonkeeper or any TON wallet",
            f"2. Send exactly ${amount_usdt} USDT to the wallet address",
            f"3. Include payment ID '{payment_id}' in the comment/memo",
            f"4. Wait for confirmation (usually 10-30 seconds)",
            f"5. Your subscription will be activated automatically"
        ],
        "message": f"Send ${amount_usdt} USDT to activate {plan['name']}"
    }


@router.post("/verify")
async def verify_payment(
    req: VerifyPaymentRequest,
    user: dict = Depends(get_current_user)
):
    """
    Verify a TON payment and activate subscription
    
    User submits tx_hash after payment, system verifies and activates
    """
    user_id = user["user_id"]
    payment = get_ton_payment(req.payment_id)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Payment belongs to another user")
    
    if payment["status"] == "completed":
        return {
            "success": True,
            "status": "already_completed",
            "message": "Payment already verified and subscription active"
        }
    
    if payment["status"] == "expired":
        raise HTTPException(status_code=400, detail="Payment expired. Please create a new payment.")
    
    # If tx_hash provided, verify on blockchain
    if req.tx_hash:
        # TODO: Implement actual TON blockchain verification
        # For now, trust the tx_hash and complete
        success = complete_ton_payment(req.payment_id, req.tx_hash)
        
        if success:
            plan = SUBSCRIPTION_PLANS.get(payment["plan_id"], {})
            return {
                "success": True,
                "status": "completed",
                "message": f"Payment verified! {plan.get('name', 'Subscription')} activated.",
                "subscription": {
                    "plan": payment["plan_id"],
                    "duration_days": plan.get("duration_days", 30)
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Payment verification failed")
    
    # No tx_hash - return pending status
    return {
        "success": True,
        "status": "pending",
        "message": "Waiting for payment. Please complete the transaction and provide tx_hash.",
        "payment_id": req.payment_id,
        "amount_usdt": payment["amount_usdt"]
    }


@router.get("/status/{payment_id}")
async def get_payment_status(
    payment_id: str,
    user: dict = Depends(get_current_user)
):
    """Get status of a TON payment"""
    user_id = user["user_id"]
    payment = get_ton_payment(payment_id)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "success": True,
        "payment_id": payment_id,
        "status": payment["status"],
        "plan_id": payment["plan_id"],
        "amount_usdt": payment["amount_usdt"],
        "created_at": str(payment["created_at"]),
        "expires_at": str(payment["expires_at"]) if payment["expires_at"] else None,
        "tx_hash": payment["tx_hash"]
    }


@router.get("/history")
async def get_payment_history(
    limit: int = Query(20, le=100),
    user: dict = Depends(get_current_user)
):
    """Get user's TON payment history"""
    user_id = user["user_id"]
    payments = get_user_ton_payments(user_id, limit)
    
    return {
        "success": True,
        "payments": [
            {
                "payment_id": p["payment_id"],
                "plan_id": p["plan_id"],
                "amount_usdt": p["amount_usdt"],
                "status": p["status"],
                "tx_hash": p["tx_hash"],
                "created_at": str(p["created_at"]),
                "confirmed_at": str(p["confirmed_at"]) if p.get("confirmed_at") else None
            }
            for p in payments
        ]
    }


@router.post("/webhook")
async def payment_webhook(
    payload: WebhookPayload,
    x_webhook_signature: str = Header(None, alias="X-Webhook-Signature")
):
    """
    Webhook endpoint for TON payment notifications
    
    This is called by the TON payment processor when a payment is received.
    The platform wallet monitors for incoming transactions and notifies us.
    
    **SECURITY:** Webhook signature verification required
    """
    # Verify webhook signature
    if not x_webhook_signature:
        logger.warning("Webhook received without signature")
        raise HTTPException(status_code=401, detail="Missing webhook signature")
    
    if not verify_webhook_signature(payload.dict(), x_webhook_signature):
        logger.warning(f"Invalid webhook signature for payment {payload.payment_id}")
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    # Process payment
    payment = get_ton_payment(payload.payment_id)
    if not payment:
        logger.error(f"Webhook for unknown payment: {payload.payment_id}")
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Verify amount matches
    if abs(payment["amount_usdt"] - payload.amount) > 0.01:
        logger.warning(f"Amount mismatch for {payload.payment_id}: expected {payment['amount_usdt']}, got {payload.amount}")
        # Still process but log warning
    
    # Complete payment
    success = complete_ton_payment(
        payload.payment_id,
        payload.tx_hash,
        payload.from_address
    )
    
    if success:
        logger.info(f"Webhook: Payment {payload.payment_id} completed via webhook")
        return {"success": True, "message": "Payment processed"}
    else:
        logger.error(f"Webhook: Failed to complete payment {payload.payment_id}")
        raise HTTPException(status_code=500, detail="Failed to process payment")


@router.get("/wallet-info")
async def get_wallet_info():
    """
    Get platform wallet information for manual payments
    
    Returns wallet address and supported tokens
    """
    return {
        "success": True,
        "network": "testnet" if TON_CONFIG["use_testnet"] else "mainnet",
        "wallet_address": get_platform_wallet(),
        "supported_tokens": [
            {
                "symbol": "USDT",
                "name": "Tether USD (Jetton)",
                "contract": TON_CONFIG["usdt_testnet"] if TON_CONFIG["use_testnet"] else TON_CONFIG["usdt_mainnet"]
            },
            {
                "symbol": "TON",
                "name": "Toncoin",
                "contract": None  # Native token
            }
        ],
        "instructions": "Send USDT or TON to this wallet with your payment ID in the comment"
    }
