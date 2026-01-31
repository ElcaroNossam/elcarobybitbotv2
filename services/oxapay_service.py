"""
OxaPay Payment Gateway Integration
==================================
Full integration with OxaPay for crypto payments (USDT, BTC, ETH, etc.)
Auto-approve subscriptions on successful payment via webhook.

Features:
- Create payment invoices
- White-label payment pages
- Static wallet addresses
- Webhook verification
- Auto-convert to USDT
- Multiple cryptocurrencies

API Docs: https://docs.oxapay.com/
"""

import os
import hmac
import hashlib
import logging
import secrets
import aiohttp
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================

OXAPAY_API_URL = "https://api.oxapay.com"
OXAPAY_MERCHANT_API_KEY = os.getenv("OXAPAY_MERCHANT_API_KEY", "")
OXAPAY_PAYOUT_API_KEY = os.getenv("OXAPAY_PAYOUT_API_KEY", "")
OXAPAY_WEBHOOK_SECRET = os.getenv("OXAPAY_WEBHOOK_SECRET", "")

# Callback URL for webhooks
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://enliko.com")
PAYMENT_CALLBACK_URL = f"{WEBAPP_URL}/api/payments/oxapay/webhook"

# ============================================
# PRICING CONFIGURATION (USD)
# ============================================

class LicensePlan(Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    TRIAL = "trial"


class LicenseDuration(Enum):
    MONTH_1 = "1m"
    MONTH_3 = "3m"
    MONTH_6 = "6m"
    YEAR_1 = "1y"


class PaymentStatus(Enum):
    """OxaPay payment statuses."""
    PENDING = "pending"           # Waiting for payment
    CONFIRMING = "confirming"     # Payment detected, waiting for confirmations
    CONFIRMED = "confirmed"       # Payment confirmed and processed
    EXPIRED = "expired"           # Payment expired (30 min timeout)
    FAILED = "failed"             # Payment failed
    REFUNDED = "refunded"         # Payment refunded


# Pricing in USD (same as ELC which is 1:1 with USD)
LICENSE_PRICES_USD = {
    "basic": {
        "1m": 50.0,
        "3m": 135.0,    # $45/mo - 10% discount
        "6m": 240.0,    # $40/mo - 20% discount
        "1y": 420.0,    # $35/mo - 30% discount
    },
    "premium": {
        "1m": 100.0,
        "3m": 270.0,    # $90/mo - 10% discount
        "6m": 480.0,    # $80/mo - 20% discount
        "1y": 840.0,    # $70/mo - 30% discount
    },
    "enterprise": {
        "1m": 500.0,
        "3m": 1350.0,   # $450/mo - 10% discount
        "6m": 2400.0,   # $400/mo - 20% discount
        "1y": 4200.0,   # $350/mo - 30% discount
    },
    "trial": {
        "1m": 0.0,
    }
}

# Duration in months
DURATION_MONTHS = {
    "1m": 1,
    "3m": 3,
    "6m": 6,
    "1y": 12,
}

# Plan features
PLAN_FEATURES = {
    "trial": {
        "name": "Free Trial",
        "description": "7 days free access",
        "features": [
            "Bybit Demo trading",
            "3 open positions max",
            "Basic strategies (OI, Scalper)",
            "Manual trading",
        ],
        "duration_days": 7,
        "is_trial": True,
    },
    "basic": {
        "name": "Basic",
        "description": "Essential trading features",
        "features": [
            "Bybit Demo + Real trading",
            "10 open positions max",
            "All basic strategies",
            "DCA support",
            "Email support",
        ],
        "max_positions": 10,
    },
    "premium": {
        "name": "Premium",
        "description": "Full access for serious traders",
        "features": [
            "Everything in Basic",
            "HyperLiquid access",
            "25 open positions max",
            "Advanced signals",
            "ATR Trailing Stop",
            "Break-Even automation",
            "Partial Take Profit",
            "Priority support",
            "Telegram notifications",
        ],
        "max_positions": 25,
        "recommended": True,
    },
    "enterprise": {
        "name": "Enterprise",
        "description": "Unlimited power for professionals",
        "features": [
            "Everything in Premium",
            "Unlimited positions",
            "Multi-exchange simultaneous",
            "Custom strategies",
            "Webhooks integration",
            "API access",
            "Dedicated account manager",
            "White-glove onboarding",
        ],
        "max_positions": 999,
    },
}


# ============================================
# DATA MODELS
# ============================================

@dataclass
class PaymentInvoice:
    """OxaPay payment invoice"""
    payment_id: str
    track_id: str
    pay_url: str
    amount_usd: float
    amount_crypto: Optional[float]
    currency: str
    address: Optional[str]
    status: str
    expires_at: datetime
    user_id: int
    plan: str
    duration: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "payment_id": self.payment_id,
            "track_id": self.track_id,
            "pay_url": self.pay_url,
            "amount_usd": self.amount_usd,
            "amount_crypto": self.amount_crypto,
            "currency": self.currency,
            "address": self.address,
            "status": self.status,
            "expires_at": self.expires_at.isoformat(),
            "user_id": self.user_id,
            "plan": self.plan,
            "duration": self.duration,
        }


# ============================================
# OXAPAY SERVICE
# ============================================

class OxaPayService:
    """OxaPay payment gateway service"""
    
    def __init__(self, merchant_api_key: str = None):
        self.merchant_api_key = merchant_api_key or OXAPAY_MERCHANT_API_KEY
        self.base_url = OXAPAY_API_URL
        
    async def _request(
        self,
        endpoint: str,
        method: str = "POST",
        data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Make API request to OxaPay"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
        }
        
        # Add merchant key to data for OxaPay API format
        if data is None:
            data = {}
        data["merchant"] = self.merchant_api_key
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    json=data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    result = await response.json()
                    
                    if response.status != 200:
                        logger.error(f"OxaPay API error: {response.status} - {result}")
                        raise Exception(f"OxaPay API error: {result.get('message', 'Unknown error')}")
                    
                    return result
        except aiohttp.ClientError as e:
            logger.error(f"OxaPay request failed: {e}")
            raise Exception(f"Payment service unavailable: {e}")
    
    def get_price(self, plan: str, duration: str) -> float:
        """Get price for plan and duration"""
        plan_prices = LICENSE_PRICES_USD.get(plan.lower())
        if not plan_prices:
            raise ValueError(f"Invalid plan: {plan}")
        
        price = plan_prices.get(duration)
        if price is None:
            raise ValueError(f"Invalid duration: {duration}")
        
        return price
    
    def get_duration_months(self, duration: str) -> int:
        """Get duration in months"""
        return DURATION_MONTHS.get(duration, 1)
    
    async def create_payment(
        self,
        user_id: int,
        plan: str,
        duration: str,
        currency: str = "USDT",
        return_url: str = None,
    ) -> PaymentInvoice:
        """
        Create payment invoice for subscription.
        
        Args:
            user_id: Telegram user ID
            plan: License plan (basic, premium, enterprise)
            duration: Duration (1m, 3m, 6m, 1y)
            currency: Payment currency (USDT, BTC, ETH, etc.)
            return_url: URL to redirect after payment
            
        Returns:
            PaymentInvoice with payment details
        """
        amount = self.get_price(plan, duration)
        
        if amount <= 0:
            raise ValueError("Cannot create payment for free plan")
        
        order_id = f"enliko_{user_id}_{plan}_{duration}_{secrets.token_hex(4)}"
        
        data = {
            "amount": amount,
            "currency": "USD",
            "payCurrency": currency,
            "lifeTime": 30,  # 30 minutes to pay
            "feePaidByPayer": 1,  # User pays network fee
            "underPaidCoverage": 2.5,  # Accept 2.5% underpayment
            "callbackUrl": PAYMENT_CALLBACK_URL,
            "returnUrl": return_url or f"{WEBAPP_URL}/subscription/success",
            "orderId": order_id,
            "description": f"Enliko {plan.title()} - {duration}",
        }
        
        result = await self._request("/merchants/request", data=data)
        
        if result.get("result") != 100:
            error_msg = result.get("message", "Failed to create payment")
            logger.error(f"OxaPay create payment failed: {error_msg}")
            raise Exception(error_msg)
        
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        
        invoice = PaymentInvoice(
            payment_id=order_id,
            track_id=result.get("trackId", ""),
            pay_url=result.get("payLink", ""),
            amount_usd=amount,
            amount_crypto=result.get("payAmount"),
            currency=currency,
            address=result.get("address"),
            status="pending",
            expires_at=expires_at,
            user_id=user_id,
            plan=plan,
            duration=duration,
        )
        
        # Save to database
        await self._save_payment(invoice)
        
        logger.info(f"Payment created: {order_id} for user {user_id}, ${amount}")
        return invoice
    
    async def create_white_label_payment(
        self,
        user_id: int,
        plan: str,
        duration: str,
        pay_currency: str = "USDT",
        network: str = "TRC20",
    ) -> Dict[str, Any]:
        """
        Create white-label payment (no redirect, show address directly).
        
        Better for bot integration - shows QR code and address directly.
        """
        amount = self.get_price(plan, duration)
        
        if amount <= 0:
            raise ValueError("Cannot create payment for free plan")
        
        order_id = f"enliko_{user_id}_{plan}_{duration}_{secrets.token_hex(4)}"
        
        data = {
            "amount": amount,
            "currency": "USD",
            "payCurrency": pay_currency,
            "network": network,
            "lifeTime": 30,
            "feePaidByPayer": 1,
            "underPaidCoverage": 2.5,
            "callbackUrl": PAYMENT_CALLBACK_URL,
            "orderId": order_id,
            "description": f"Enliko {plan.title()} - {duration}",
        }
        
        result = await self._request("/merchants/request", data=data)
        
        if result.get("result") != 100:
            error_msg = result.get("message", "Failed to create payment")
            raise Exception(error_msg)
        
        payment_data = {
            "payment_id": order_id,
            "track_id": result.get("trackId", ""),
            "pay_url": result.get("payLink", ""),
            "address": result.get("address", ""),
            "amount_usd": amount,
            "amount_crypto": result.get("payAmount"),
            "currency": pay_currency,
            "network": network,
            "expires_in_minutes": 30,
            "expires_at": (datetime.utcnow() + timedelta(minutes=30)).isoformat(),
            "qr_code": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={result.get('address', '')}",
            "status": "pending",
            "user_id": user_id,
            "plan": plan,
            "duration": duration,
        }
        
        # Save to database
        await self._save_payment_data(payment_data)
        
        logger.info(f"White-label payment created: {order_id}")
        return payment_data
    
    async def check_payment_status(self, track_id: str) -> Dict[str, Any]:
        """Check payment status by track ID"""
        data = {"trackId": track_id}
        result = await self._request("/payment/inquiry", data=data)
        
        return {
            "track_id": track_id,
            "status": result.get("status", "unknown"),
            "amount": result.get("amount"),
            "pay_amount": result.get("payAmount"),
            "paid_amount": result.get("paidAmount"),
            "currency": result.get("currency"),
            "order_id": result.get("orderId"),
        }
    
    def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """
        Verify webhook signature from OxaPay.
        
        OxaPay sends HMAC-SHA512 signature in header.
        """
        if not OXAPAY_WEBHOOK_SECRET:
            logger.warning("OXAPAY_WEBHOOK_SECRET not set, skipping verification")
            return True
        
        import json
        payload_str = json.dumps(payload, separators=(',', ':'))
        
        expected_sig = hmac.new(
            OXAPAY_WEBHOOK_SECRET.encode(),
            payload_str.encode(),
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(expected_sig, signature)
    
    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process webhook from OxaPay.
        
        Auto-approves subscription on successful payment.
        """
        status = payload.get("status")
        order_id = payload.get("orderId", "")
        track_id = payload.get("trackId", "")
        
        logger.info(f"OxaPay webhook: {status} for {order_id}")
        
        # Parse order_id: enliko_{user_id}_{plan}_{duration}_{random}
        parts = order_id.split("_")
        if len(parts) < 4 or parts[0] != "enliko":
            logger.error(f"Invalid order_id format: {order_id}")
            return {"success": False, "error": "Invalid order format"}
        
        try:
            user_id = int(parts[1])
            plan = parts[2]
            duration = parts[3]
        except (ValueError, IndexError) as e:
            logger.error(f"Failed to parse order_id: {order_id}, error: {e}")
            return {"success": False, "error": "Parse error"}
        
        # Update payment status in database
        await self._update_payment_status(order_id, status, payload)
        
        if status in ("Paid", "Confirmed"):
            # Auto-approve license!
            result = await self._activate_license(
                user_id=user_id,
                plan=plan,
                duration=duration,
                payment_id=order_id,
                tx_hash=payload.get("txID"),
                amount=payload.get("payAmount"),
            )
            
            if result.get("success"):
                # Send notification to user
                await self._notify_user(user_id, plan, duration)
                
            return result
        
        elif status == "Expired":
            logger.info(f"Payment expired: {order_id}")
            return {"success": True, "status": "expired"}
        
        elif status == "Failed":
            logger.warning(f"Payment failed: {order_id}")
            return {"success": True, "status": "failed"}
        
        return {"success": True, "status": status}
    
    async def _save_payment(self, invoice: PaymentInvoice):
        """Save payment to database"""
        await self._save_payment_data(invoice.to_dict())
    
    async def _save_payment_data(self, data: Dict[str, Any]):
        """Save payment data to crypto_payments table"""
        try:
            from core.db_postgres import execute_write
            
            execute_write("""
                INSERT INTO crypto_payments (
                    payment_id, user_id, track_id, amount_usd, amount_crypto,
                    currency, address, status, plan, duration, expires_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (payment_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    updated_at = NOW()
            """, (
                data.get("payment_id"),
                data.get("user_id"),
                data.get("track_id"),
                data.get("amount_usd"),
                data.get("amount_crypto"),
                data.get("currency"),
                data.get("address"),
                data.get("status", "pending"),
                data.get("plan"),
                data.get("duration"),
                data.get("expires_at"),
            ))
        except Exception as e:
            logger.error(f"Failed to save payment: {e}")
    
    async def _update_payment_status(
        self,
        payment_id: str,
        status: str,
        payload: Dict[str, Any]
    ):
        """Update payment status in database"""
        try:
            from core.db_postgres import execute_write
            
            execute_write("""
                UPDATE crypto_payments 
                SET status = %s, 
                    tx_hash = %s,
                    paid_amount = %s,
                    webhook_data = %s,
                    confirmed_at = CASE WHEN %s IN ('Paid', 'Confirmed') THEN NOW() ELSE confirmed_at END,
                    updated_at = NOW()
                WHERE payment_id = %s
            """, (
                status.lower(),
                payload.get("txID"),
                payload.get("paidAmount"),
                str(payload),
                status,
                payment_id,
            ))
        except Exception as e:
            logger.error(f"Failed to update payment status: {e}")
    
    async def _activate_license(
        self,
        user_id: int,
        plan: str,
        duration: str,
        payment_id: str,
        tx_hash: str = None,
        amount: float = None,
    ) -> Dict[str, Any]:
        """Activate user license after successful payment"""
        try:
            from db import set_user_license
            
            months = self.get_duration_months(duration)
            
            result = set_user_license(
                user_id=user_id,
                license_type=plan,
                period_months=months,
                admin_id=None,  # Auto-approved
                payment_type="oxapay",
                amount=amount or self.get_price(plan, duration),
                currency="USDT",
                telegram_charge_id=payment_id,
                notes=f"OxaPay payment: {tx_hash or payment_id}",
            )
            
            if result.get("success"):
                logger.info(f"License activated: {user_id} -> {plan} for {months} months")
                return {
                    "success": True,
                    "user_id": user_id,
                    "plan": plan,
                    "duration": duration,
                    "expires": result.get("expires"),
                }
            else:
                logger.error(f"License activation failed: {result}")
                return {"success": False, "error": result.get("error")}
                
        except Exception as e:
            logger.error(f"License activation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _notify_user(self, user_id: int, plan: str, duration: str):
        """Send notification to user about successful payment"""
        try:
            # Import bot and send message
            from telegram import Bot
            
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if not bot_token:
                logger.warning("No bot token for notification")
                return
            
            bot = Bot(token=bot_token)
            
            plan_name = PLAN_FEATURES.get(plan, {}).get("name", plan.title())
            duration_text = {
                "1m": "1 month",
                "3m": "3 months",
                "6m": "6 months",
                "1y": "1 year",
            }.get(duration, duration)
            
            message = f"""
✅ *Payment Successful!*

Your *{plan_name}* subscription has been activated for *{duration_text}*.

Thank you for choosing Enliko! 🚀

Use /menu to access all features.
"""
            await bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Failed to notify user {user_id}: {e}")
    
    def get_available_currencies(self) -> List[Dict[str, Any]]:
        """Get list of available payment currencies"""
        return [
            {"code": "USDT", "name": "Tether USD", "networks": ["TRC20", "BEP20", "ERC20", "Polygon"]},
            {"code": "BTC", "name": "Bitcoin", "networks": ["Bitcoin"]},
            {"code": "ETH", "name": "Ethereum", "networks": ["ERC20"]},
            {"code": "TRX", "name": "Tron", "networks": ["TRC20"]},
            {"code": "BNB", "name": "BNB", "networks": ["BEP20"]},
            {"code": "SOL", "name": "Solana", "networks": ["Solana"]},
            {"code": "TON", "name": "Toncoin", "networks": ["TON"]},
            {"code": "LTC", "name": "Litecoin", "networks": ["Litecoin"]},
            {"code": "DOGE", "name": "Dogecoin", "networks": ["Dogecoin"]},
            {"code": "XMR", "name": "Monero", "networks": ["Monero"]},
        ]
    
    def get_plans(self) -> Dict[str, Any]:
        """Get all subscription plans with features and pricing"""
        result = {}
        for plan_id, features in PLAN_FEATURES.items():
            result[plan_id] = {
                **features,
                "prices": LICENSE_PRICES_USD.get(plan_id, {}),
            }
        return result


# ============================================
# SINGLETON INSTANCE
# ============================================

oxapay_service = OxaPayService()


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

async def create_payment(
    user_id: int,
    plan: str,
    duration: str,
    currency: str = "USDT",
) -> Dict[str, Any]:
    """Create payment for subscription"""
    return await oxapay_service.create_white_label_payment(
        user_id=user_id,
        plan=plan,
        duration=duration,
        pay_currency=currency,
    )


async def process_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process OxaPay webhook"""
    return await oxapay_service.process_webhook(payload)


def get_plans() -> Dict[str, Any]:
    """Get subscription plans"""
    return oxapay_service.get_plans()


def get_price(plan: str, duration: str) -> float:
    """Get price for plan"""
    return oxapay_service.get_price(plan, duration)


def get_currencies() -> List[Dict[str, Any]]:
    """Get available currencies"""
    return oxapay_service.get_available_currencies()
