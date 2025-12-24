"""
Payments & Subscriptions API
Handles subscription purchases, upgrades, TON/Web3 payments
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime, timedelta
import logging

import db

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models
class PaymentRequest(BaseModel):
    plan: Literal['trial', 'basic', 'premium']
    period: Literal['monthly', 'quarterly', 'yearly']
    amount: float
    payment_method: Literal['web3', 'ton', 'usdt']
    wallet_address: Optional[str] = None
    transaction_hash: Optional[str] = None


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
async def create_payment(payment: PaymentRequest):
    """
    Create a new payment/subscription
    Validates payment and activates subscription
    """
    try:
        # Validate plan and period
        if payment.plan not in PRICING:
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        plan_config = PRICING[payment.plan]
        expected_amount = plan_config[payment.period]
        
        # Validate amount
        if abs(payment.amount - expected_amount) > 0.01:
            raise HTTPException(status_code=400, detail=f"Invalid amount. Expected ${expected_amount}")
        
        # Verify payment (simplified - in production, verify on-chain)
        if payment.payment_method == 'web3':
            if not payment.wallet_address:
                raise HTTPException(status_code=400, detail="Wallet address required")
            # TODO: Verify Web3 payment
        elif payment.payment_method == 'ton':
            # TODO: Verify TON payment
            pass
        elif payment.payment_method == 'usdt':
            # TODO: Verify USDT payment
            pass
        
        # For demo purposes, simulate user_id (in production, get from auth)
        user_id = 123456  # Replace with actual user ID from session/JWT
        
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


@router.get("/subscription/{user_id}")
async def get_subscription(user_id: int):
    """Get user's current subscription info"""
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


@router.post("/cancel/{user_id}")
async def cancel_subscription(user_id: int):
    """Cancel user's subscription (turn off auto-renew)"""
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
    user_id: int = Body(...),
    new_plan: str = Body(...),
    new_period: str = Body(...)
):
    """Upgrade user's subscription"""
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


@router.get("/history/{user_id}")
async def get_payment_history(user_id: int, limit: int = 50):
    """Get user's payment history"""
    try:
        # This would query a payments table
        # For now, return mock data
        return {
            "success": True,
            "payments": []
        }
    except Exception as e:
        logger.error(f"Failed to get payment history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Referral System
@router.post("/referral/apply")
async def apply_referral_code(
    user_id: int = Body(...),
    referral_code: str = Body(...)
):
    """Apply referral code for discount"""
    try:
        # Validate referral code
        referrer_id = db.get_user_by_referral_code(referral_code)
        if not referrer_id:
            raise HTTPException(status_code=404, detail="Invalid referral code")
        
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
