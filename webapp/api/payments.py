"""
Payments & Subscriptions API
Handles subscription purchases, upgrades, TON/Web3 payments
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime, timedelta
import logging
import re

import db
from webapp.api.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models
class PaymentRequest(BaseModel):
    plan: Literal['trial', 'basic', 'premium']
    period: Literal['monthly', 'quarterly', 'yearly']
    amount: float = Field(..., ge=0, le=10000, description="Payment amount in USD")
    payment_method: Literal['web3', 'ton', 'usdt']
    wallet_address: Optional[str] = Field(None, max_length=128)
    transaction_hash: Optional[str] = Field(None, min_length=64, max_length=128)
    
    @field_validator('wallet_address')
    @classmethod
    def validate_wallet_address(cls, v):
        if v is not None:
            # Basic validation for crypto wallet addresses
            if not re.match(r'^[a-zA-Z0-9_\-:]+$', v):
                raise ValueError('Invalid wallet address format')
        return v
    
    @field_validator('transaction_hash')
    @classmethod
    def validate_tx_hash(cls, v):
        if v is not None:
            # Transaction hash should be hex
            if not re.match(r'^[a-fA-F0-9]+$', v):
                raise ValueError('Invalid transaction hash format')
        return v


class SubscriptionInfo(BaseModel):
    user_id: int
    plan: str
    status: str
    expires_at: Optional[datetime]
    days_left: Optional[int]
    auto_renew: bool


# Pricing Configuration
PRICING = {
    'trial': {
        'monthly': 0,
        'quarterly': 0,
        'yearly': 0,
        'license_type': 'trial',
        'duration_days': 7
    },
    'basic': {
        'monthly': 29,
        'quarterly': 78,  # 10% discount
        'yearly': 261,    # 25% discount
        'license_type': 'basic',
        'duration_days': {'monthly': 30, 'quarterly': 90, 'yearly': 365}
    },
    'premium': {
        'monthly': 99,
        'quarterly': 267,  # 10% discount
        'yearly': 891,     # 25% discount
        'license_type': 'premium',
        'duration_days': {'monthly': 30, 'quarterly': 90, 'yearly': 365}
    }
}


@router.get("/plans")
async def get_pricing_plans():
    """Get all available pricing plans"""
    return {
        "success": True,
        "plans": PRICING
    }


@router.post("/create")
async def create_payment(
    payment: PaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new payment/subscription
    Validates payment and activates subscription
    
    **SECURITY:** Requires JWT authentication
    """
    user_id = current_user['user_id']
    
    try:
        # Check for duplicate transaction BEFORE processing
        if payment.transaction_hash:
            if db.check_duplicate_transaction(payment.transaction_hash):
                logger.warning(f"Duplicate transaction attempt: {payment.transaction_hash} by user {user_id}")
                raise HTTPException(status_code=409, detail="Transaction already processed")
        
        # Validate plan and period
        if payment.plan not in PRICING:
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        plan_config = PRICING[payment.plan]
        expected_amount = plan_config[payment.period]
        
        # Validate amount
        if abs(payment.amount - expected_amount) > 0.01:
            raise HTTPException(status_code=400, detail=f"Invalid amount. Expected ${expected_amount}")
        
        # Verify payment on blockchain
        if payment.payment_method == 'web3':
            if not payment.wallet_address or not payment.transaction_hash:
                raise HTTPException(status_code=400, detail="Wallet address and transaction hash required")
            
            # Import Web3 verification
            try:
                from blockchain.web3_client import verify_payment_transaction
                is_valid = await verify_payment_transaction(
                    tx_hash=payment.transaction_hash,
                    expected_amount=payment.amount,
                    from_address=payment.wallet_address
                )
                if not is_valid:
                    raise HTTPException(status_code=400, detail="Invalid Web3 transaction")
            except ImportError:
                logger.error("Web3 verification not available - PAYMENT BLOCKED")
                raise HTTPException(status_code=503, detail="Web3 payment verification unavailable")
                
        elif payment.payment_method == 'ton':
            # TON payments deprecated - use OxaPay crypto payments instead
            raise HTTPException(
                status_code=410,
                detail="TON payments deprecated. Please use /api/crypto/ endpoints for crypto payments"
            )
                
        elif payment.payment_method == 'usdt':
            if not payment.transaction_hash:
                raise HTTPException(status_code=400, detail="Transaction hash required")
            
            try:
                from blockchain.web3_client import verify_usdt_transaction
                is_valid = await verify_usdt_transaction(
                    tx_hash=payment.transaction_hash,
                    expected_amount=payment.amount
                )
                if not is_valid:
                    raise HTTPException(status_code=400, detail="Invalid USDT transaction")
            except ImportError:
                logger.error("USDT verification not available - PAYMENT BLOCKED")
                raise HTTPException(status_code=503, detail="USDT payment verification unavailable")
        
        # Calculate expiration
        if payment.plan == 'trial':
            duration_days = plan_config['duration_days']
        else:
            duration_days = plan_config['duration_days'][payment.period]
        
        # Activate subscription
        license_type = plan_config['license_type']
        db.set_user_license(
            user_id=user_id,
            license_type=license_type,
            days=duration_days,
            payment_amount=payment.amount,
            payment_method=payment.payment_method
        )
        
        # Record payment
        db.add_payment_record(
            user_id=user_id,
            plan=payment.plan,
            period=payment.period,
            amount=payment.amount,
            payment_method=payment.payment_method,
            wallet_address=payment.wallet_address,
            transaction_hash=payment.transaction_hash
        )
        
        return {
            "success": True,
            "message": "Subscription activated successfully",
            "subscription": {
                "plan": payment.plan,
                "license_type": license_type,
                "expires_in_days": duration_days
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscription")
async def get_subscription(current_user: dict = Depends(get_current_user)):
    """Get current user's subscription info"""
    user_id = current_user['user_id']
    
    try:
        license_info = db.get_user_license(user_id)
        
        return {
            "success": True,
            "subscription": {
                "license_type": license_info['license_type'],
                "is_active": license_info['is_active'],
                "expires": license_info['expires'],
                "days_left": license_info['days_left'],
                "capabilities": license_info['capabilities']
            }
        }
    except Exception as e:
        logger.error(f"Failed to get subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel")
async def cancel_subscription(current_user: dict = Depends(get_current_user)):
    """Cancel current user's subscription (turn off auto-renew)"""
    user_id = current_user['user_id']
    
    try:
        # In a real system, you'd disable auto-renew but keep access until expiration
        db.set_user_value(user_id, "auto_renew", False)
        
        return {
            "success": True,
            "message": "Auto-renewal disabled. Access continues until expiration."
        }
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upgrade")
async def upgrade_subscription(
    new_plan: str = Body(...),
    new_period: str = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Upgrade user's subscription"""
    user_id = current_user['user_id']
    try:
        if new_plan not in PRICING:
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        # Get current subscription
        current = db.get_user_license(user_id)
        
        # Calculate prorated amount (if upgrading mid-cycle)
        # Simplified: just upgrade and extend
        plan_config = PRICING[new_plan]
        duration_days = plan_config['duration_days'][new_period]
        
        db.set_user_license(
            user_id=user_id,
            license_type=plan_config['license_type'],
            days=duration_days
        )
        
        return {
            "success": True,
            "message": "Subscription upgraded successfully"
        }
    except Exception as e:
        logger.error(f"Failed to upgrade subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/me")
async def get_my_payment_history(
    limit: int = 50,
    user: dict = Depends(get_current_user)
):
    """Get current user's payment history"""
    try:
        user_id = user["user_id"]
        payments = db.get_user_payments(user_id, limit)
        return {
            "success": True,
            "payments": payments
        }
    except Exception as e:
        logger.error(f"Failed to get payment history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{user_id}")
async def get_payment_history(
    user_id: int, 
    limit: int = 50,
    user: dict = Depends(get_current_user)
):
    """Get user's payment history - requires authentication"""
    # SECURITY: Users can only access their own payment history
    if user["user_id"] != user_id and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied. You can only view your own payment history.")
    
    try:
        payments = db.get_user_payments(user_id, limit)
        return {
            "success": True,
            "payments": payments
        }
    except Exception as e:
        logger.error(f"Failed to get payment history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Referral System
@router.post("/referral/apply")
async def apply_referral_code(
    referral_code: str = Body(..., embed=True),
    user: dict = Depends(get_current_user)
):
    """Apply referral code for discount - requires authentication"""
    # SECURITY: Use authenticated user_id from JWT, not from request body
    user_id = user["user_id"]
    try:
        # Validate referral code
        referrer_id = db.get_user_by_referral_code(referral_code)
        if not referrer_id:
            raise HTTPException(status_code=404, detail="Invalid referral code")
        
        # Prevent self-referral
        if referrer_id == user_id:
            raise HTTPException(status_code=400, detail="Cannot use your own referral code")
        
        # Apply referral bonus
        db.add_referral_connection(user_id, referrer_id)
        
        return {
            "success": True,
            "message": "Referral code applied",
            "discount": "10%"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to apply referral: {e}")
        raise HTTPException(status_code=500, detail=str(e))
