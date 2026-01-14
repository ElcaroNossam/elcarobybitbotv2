"""
ELCARO Token Payment API
Complete payment system using ELCARO token only
Buy ELC with USDT on TON, use for all platform services
"""
import os
import sys
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from webapp.api.auth import get_current_user
from ton_payment_gateway import ELCAROPaymentManager
from cold_wallet_trading import (
    connect_metamask,
    place_order_with_metamask,
    submit_signed_hl_order,
    get_wallet_info,
    disconnect_metamask
)
import db

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize payment manager
payment_manager = ELCAROPaymentManager(testnet=True)  # Set False for production


# ============================================================
# REQUEST MODELS
# ============================================================

class BuyELCRequest(BaseModel):
    usdt_amount: float
    payment_method: str = "ton"  # ton, polygon, bsc


class CreateSubscriptionRequest(BaseModel):
    plan: str  # basic, premium, pro
    duration: str  # 1m, 3m, 6m, 1y
    payment_method: str = "elc"  # Always ELC now


class WalletConnectRequest(BaseModel):
    wallet_address: str
    signature: str
    message: str
    wallet_type: str = "metamask"  # metamask, walletconnect, tonkeeper


class PlaceOrderRequest(BaseModel):
    symbol: str
    side: str
    size: float
    order_type: str = "market"
    price: Optional[float] = None
    reduce_only: bool = False
    use_cold_wallet: bool = False  # If True, use MetaMask signing


class SubmitSignedOrderRequest(BaseModel):
    order_data: dict
    signature: str


# ============================================================
# ELCARO TOKEN ENDPOINTS
# ============================================================

@router.get("/elc/info")
async def get_elc_info():
    """Get ELCARO token information and current price
    
    NOTE: Token contracts not yet deployed. Values are placeholders.
    DO NOT use contract_addresses in production until real addresses are set.
    """
    return {
        "token_name": "ELCARO Token",
        "ticker": "ELC",
        "total_supply": 1_000_000_000,
        "circulating_supply": 450_000_000,
        "current_price_usd": 1.0,
        "market_cap": 450_000_000,
        "networks": ["TON", "Polygon", "BSC"],
        "primary_network": "TON",
        "contract_addresses": {
            # PLACEHOLDER: Replace with real contract addresses before launch
            "ton": None,  # TODO: Deploy and add TON contract
            "polygon": None,  # TODO: Deploy and add Polygon contract
            "bsc": None  # TODO: Deploy and add BSC contract
        },
        "dex_pairs": {
            "ton": ["ELC/TON", "ELC/USDT"],
            "polygon": ["ELC/USDC", "ELC/MATIC"],
            "bsc": ["ELC/BUSD", "ELC/BNB"]
        },
        "features": [
            "Platform subscriptions",
            "Strategy marketplace",
            "Staking rewards (5-15% APY)",
            "Governance voting",
            "Trading fee discounts"
        ]
    }


@router.post("/elc/calculate")
async def calculate_elc_purchase(request: BuyELCRequest):
    """Calculate how much ELC user gets for USDT"""
    try:
        if request.usdt_amount <= 0:
            raise HTTPException(400, "USDT amount must be positive")
        
        # Initialize if needed
        if not payment_manager.ton_gateway:
            await payment_manager.initialize(
                platform_wallet="UQC..."  # Add real platform wallet
            )
        
        calculation = payment_manager.ton_gateway.calculate_elc_amount(request.usdt_amount)
        
        return {
            "success": True,
            **calculation,
            "payment_method": request.payment_method,
            "steps": [
                "1. Send USDT to platform address",
                "2. Wait for confirmation (1-2 minutes)",
                "3. Receive ELC in your wallet",
                "4. Start using ELC for subscriptions"
            ]
        }
    except Exception as e:
        logger.error(f"ELC calculation error: {e}")
        raise HTTPException(500, str(e))


@router.post("/elc/buy")
async def buy_elc_tokens(
    request: BuyELCRequest,
    user: dict = Depends(get_current_user)
):
    """Create payment link to buy ELC with USDT"""
    user_id = user["user_id"]
    
    try:
        if not payment_manager.ton_gateway:
            await payment_manager.initialize(
                platform_wallet="UQC..."  # Add real platform wallet
            )
        
        # Create payment link
        payment_data = await payment_manager.ton_gateway.create_payment_link(
            user_id=user_id,
            usdt_amount=request.usdt_amount,
            purpose="buy_elc"
        )
        
        # Save to database
        db.execute(
            """INSERT INTO elc_purchases 
               (user_id, payment_id, usdt_amount, elc_amount, status, payment_method, created_at)
               VALUES (?, ?, ?, ?, 'pending', ?, datetime('now'))""",
            (user_id, payment_data["payment_id"], request.usdt_amount, 
             payment_data["elc_amount"], request.payment_method)
        )
        
        return {
            "success": True,
            **payment_data,
            "instructions": [
                f"Send {request.usdt_amount} USDT to the address below",
                f"Include payment ID in transaction comment",
                "Your ELC will arrive in 1-5 minutes",
                "Check 'My Wallet' to see your ELC balance"
            ]
        }
    except Exception as e:
        logger.error(f"Buy ELC error: {e}")
        raise HTTPException(500, str(e))


@router.get("/elc/balance")
async def get_elc_balance(user: dict = Depends(get_current_user)):
    """Get user's ELC token balance"""
    user_id = user["user_id"]
    
    try:
        # Get balance from database
        result = db.execute(
            "SELECT elc_balance, elc_staked, elc_locked FROM users WHERE user_id = ?",
            (user_id,)
        )
        row = result.fetchone()
        
        if not row:
            return {
                "elc_balance": 0,
                "elc_staked": 0,
                "elc_locked": 0,
                "total_elc": 0,
                "usd_value": 0
            }
        
        elc_balance = row[0] or 0
        elc_staked = row[1] or 0
        elc_locked = row[2] or 0
        total = elc_balance + elc_staked + elc_locked
        
        return {
            "elc_balance": elc_balance,
            "elc_staked": elc_staked,
            "elc_locked": elc_locked,
            "total_elc": total,
            "usd_value": total * 1.0,  # $1 per ELC
            "available_for_trading": elc_balance,
            "staking_rewards_pending": 0  # Calculate actual rewards
        }
    except Exception as e:
        logger.error(f"Get ELC balance error: {e}")
        raise HTTPException(500, str(e))


@router.get("/elc/transactions")
async def get_elc_transactions(
    limit: int = 50,
    user: dict = Depends(get_current_user)
):
    """Get user's ELC transaction history"""
    user_id = user["user_id"]
    
    try:
        result = db.execute(
            """SELECT transaction_type, amount, balance_after, description, created_at
               FROM elc_transactions 
               WHERE user_id = ?
               ORDER BY created_at DESC
               LIMIT ?""",
            (user_id, limit)
        )
        
        transactions = []
        for row in result.fetchall():
            transactions.append({
                "type": row[0],
                "amount": row[1],
                "balance_after": row[2],
                "description": row[3],
                "timestamp": row[4]
            })
        
        return {
            "success": True,
            "transactions": transactions,
            "count": len(transactions)
        }
    except Exception as e:
        logger.error(f"Get transactions error: {e}")
        raise HTTPException(500, str(e))


# ============================================================
# SUBSCRIPTION ENDPOINTS (ELC Only)
# ============================================================

@router.get("/subscriptions/prices")
async def get_subscription_prices():
    """Get all subscription prices in ELC"""
    return {
        "currency": "ELC",
        "note": "All prices in ELCARO tokens. 1 ELC ≈ $1 USD",
        "plans": {
            "basic": {
                "name": "Basic Plan",
                "features": ["1 strategy", "Basic signals", "Email support"],
                "prices": {
                    "1m": {"elc": 100, "usd_equivalent": 100, "discount": 0},
                    "3m": {"elc": 270, "usd_equivalent": 270, "discount": 10},
                    "6m": {"elc": 480, "usd_equivalent": 480, "discount": 20},
                    "1y": {"elc": 840, "usd_equivalent": 840, "discount": 30}
                }
            },
            "premium": {
                "name": "Premium Plan",
                "features": ["Unlimited strategies", "Premium signals", "Priority support", "AI Agent"],
                "prices": {
                    "1m": {"elc": 200, "usd_equivalent": 200, "discount": 0},
                    "3m": {"elc": 540, "usd_equivalent": 540, "discount": 10},
                    "6m": {"elc": 960, "usd_equivalent": 960, "discount": 20},
                    "1y": {"elc": 1680, "usd_equivalent": 1680, "discount": 30}
                }
            },
            "pro": {
                "name": "Pro Plan",
                "features": ["Everything", "HyperLiquid access", "API access", "VIP support"],
                "prices": {
                    "1m": {"elc": 500, "usd_equivalent": 500, "discount": 0},
                    "3m": {"elc": 1350, "usd_equivalent": 1350, "discount": 10},
                    "6m": {"elc": 2400, "usd_equivalent": 2400, "discount": 20},
                    "1y": {"elc": 4200, "usd_equivalent": 4200, "discount": 30}
                }
            }
        },
        "payment_methods": ["ELC Token"],
        "how_to_buy_elc": "/api/payments/elc/buy"
    }


@router.post("/subscriptions/create")
async def create_subscription_payment(
    request: CreateSubscriptionRequest,
    user: dict = Depends(get_current_user)
):
    """Create subscription payment in ELC"""
    user_id = user["user_id"]
    
    try:
        # Get price in ELC
        elc_price = payment_manager.get_subscription_price(request.plan, request.duration)
        
        if elc_price == 0:
            raise HTTPException(400, "Invalid plan or duration")
        
        # Check user's ELC balance
        user_balance_result = db.execute(
            "SELECT elc_balance FROM users WHERE user_id = ?",
            (user_id,)
        )
        row = user_balance_result.fetchone()
        user_balance = row[0] if row else 0
        
        if user_balance < elc_price:
            return {
                "success": False,
                "error": "insufficient_balance",
                "required": elc_price,
                "available": user_balance,
                "shortfall": elc_price - user_balance,
                "message": f"You need {elc_price - user_balance} more ELC. Buy ELC with USDT first.",
                "buy_elc_url": "/api/payments/elc/buy"
            }
        
        # Deduct ELC from user balance
        db.execute(
            "UPDATE users SET elc_balance = elc_balance - ? WHERE user_id = ?",
            (elc_price, user_id)
        )
        
        # Calculate subscription duration in days
        duration_days = {
            "1m": 30,
            "3m": 90,
            "6m": 180,
            "1y": 365
        }[request.duration]
        
        # Activate subscription
        db.set_user_license(user_id, request.plan, duration_days)
        
        # Record transaction
        db.execute(
            """INSERT INTO elc_transactions 
               (user_id, transaction_type, amount, balance_after, description, created_at)
               VALUES (?, 'subscription', ?, ?, ?, datetime('now'))""",
            (user_id, -elc_price, user_balance - elc_price, 
             f"Subscription: {request.plan} {request.duration}")
        )
        
        # Burn 10% of subscription fee (deflationary mechanism)
        burn_amount = elc_price * 0.1
        db.execute(
            "UPDATE elc_stats SET total_burned = total_burned + ?, last_burn_at = datetime('now')",
            (burn_amount,)
        )
        
        return {
            "success": True,
            "subscription_activated": True,
            "plan": request.plan,
            "duration": request.duration,
            "elc_paid": elc_price,
            "elc_burned": burn_amount,
            "new_balance": user_balance - elc_price,
            "expires_in_days": duration_days,
            "message": f"{request.plan.title()} subscription activated for {duration_days} days!"
        }
    except Exception as e:
        logger.error(f"Subscription creation error: {e}")
        raise HTTPException(500, str(e))


# ============================================================
# COLD WALLET TRADING ENDPOINTS
# ============================================================

@router.post("/wallet/connect")
async def connect_wallet(
    request: WalletConnectRequest,
    user: dict = Depends(get_current_user)
):
    """Connect MetaMask/WalletConnect/Tonkeeper for trading"""
    user_id = user["user_id"]
    
    try:
        result = await connect_metamask(
            user_id=user_id,
            wallet_address=request.wallet_address,
            signature=request.signature,
            message=request.message
        )
        
        if result.get("success"):
            # Save to database
            db.execute(
                """INSERT OR REPLACE INTO connected_wallets 
                   (user_id, wallet_address, wallet_type, connected_at)
                   VALUES (?, ?, ?, datetime('now'))""",
                (user_id, request.wallet_address, request.wallet_type)
            )
        
        return result
    except Exception as e:
        logger.error(f"Wallet connect error: {e}")
        raise HTTPException(500, str(e))


@router.get("/wallet/status")
async def get_wallet_status(user: dict = Depends(get_current_user)):
    """Get wallet connection status"""
    user_id = user["user_id"]
    
    try:
        result = db.execute(
            "SELECT wallet_address, wallet_type, connected_at FROM connected_wallets WHERE user_id = ?",
            (user_id,)
        )
        row = result.fetchone()
        
        if row:
            return {
                "connected": True,
                "wallet_address": row[0],
                "wallet_type": row[1],
                "connected_at": row[2],
                "trading_enabled": True
            }
        
        return {
            "connected": False,
            "wallet_address": None,
            "wallet_type": None,
            "trading_enabled": False
        }
    except Exception as e:
        logger.error(f"Wallet status error: {e}")
        raise HTTPException(500, str(e))


@router.post("/wallet/disconnect")
async def disconnect_wallet(user: dict = Depends(get_current_user)):
    """Disconnect wallet"""
    user_id = user["user_id"]
    
    try:
        disconnect_metamask(user_id)
        db.execute("DELETE FROM connected_wallets WHERE user_id = ?", (user_id,))
        
        return {
            "success": True,
            "message": "Wallet disconnected"
        }
    except Exception as e:
        logger.error(f"Wallet disconnect error: {e}")
        raise HTTPException(500, str(e))


@router.post("/trading/place-order-cold-wallet")
async def place_order_cold_wallet(
    request: PlaceOrderRequest,
    user: dict = Depends(get_current_user)
):
    """Place order using cold wallet (MetaMask) - returns data to sign"""
    user_id = user["user_id"]
    
    if not request.use_cold_wallet:
        raise HTTPException(400, "use_cold_wallet must be true for this endpoint")
    
    try:
        result = await place_order_with_metamask(
            user_id=user_id,
            symbol=request.symbol,
            side=request.side,
            size=request.size,
            order_type=request.order_type,
            price=request.price,
            reduce_only=request.reduce_only
        )
        
        return result
    except Exception as e:
        logger.error(f"Cold wallet order error: {e}")
        raise HTTPException(500, str(e))


@router.post("/trading/submit-signed-order")
async def submit_signed_order(
    request: SubmitSignedOrderRequest,
    user: dict = Depends(get_current_user)
):
    """Submit signed order to HyperLiquid"""
    user_id = user["user_id"]
    
    try:
        result = await submit_signed_hl_order(
            user_id=user_id,
            order_data=request.order_data,
            signature=request.signature
        )
        
        return result
    except Exception as e:
        logger.error(f"Submit signed order error: {e}")
        raise HTTPException(500, str(e))


# Initialize payment manager on startup
@router.on_event("startup")
async def startup_event():
    """Initialize payment gateway on startup"""
    try:
        platform_wallet = os.getenv("PLATFORM_TON_WALLET", "UQC...")
        await payment_manager.initialize(platform_wallet)
        logger.info("ELCARO Payment Manager initialized")
    except Exception as e:
        logger.error(f"Payment manager initialization error: {e}")
