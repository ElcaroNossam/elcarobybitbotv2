"""
LYXEN Token Payment API
Complete payment system using LYXEN token only
Buy ELC with USDT on TON, use for all platform services

Synchronized with bot.py LICENSE_PRICES
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
from db import set_user_license
from db_elcaro import (
    get_elc_balance as get_elc_balance_db,
    subtract_elc_balance,
    add_elc_balance,
    add_elc_transaction,
    create_elc_purchase,
    complete_elc_purchase,
    get_user_transactions as get_elc_transactions_db,
)
from core.blockchain import (
    get_license_price,
    get_subscription_options,
    LICENSE_PRICES_ELC,
)

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
    """Get LYXEN token information and current price
    
    NOTE: Token contracts not yet deployed. Values are placeholders.
    DO NOT use contract_addresses in production until real addresses are set.
    """
    return {
        "token_name": "LYXEN Token",
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
        
        # Create payment link (this also creates purchase record via db_elcaro)
        payment_data = await payment_manager.ton_gateway.create_payment_link(
            user_id=user_id,
            usdt_amount=request.usdt_amount,
            purpose="buy_elc"
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
        # Get balance using db_elcaro function
        balance = get_elc_balance_db(user_id)
        
        return {
            "elc_balance": balance.get("available", 0),
            "elc_staked": balance.get("staked", 0),
            "elc_locked": balance.get("locked", 0),
            "total_elc": balance.get("total", 0),
            "usd_value": balance.get("total", 0) * 1.0,  # $1 per ELC
            "available_for_trading": balance.get("available", 0),
            "staking_rewards_pending": 0  # TODO: Calculate actual rewards
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
        # Use db_elcaro function
        transactions = get_elc_transactions_db(user_id, limit=limit)
        
        return {
            "success": True,
            "transactions": [
                {
                    "type": tx.get("transaction_type"),
                    "amount": tx.get("amount"),
                    "balance_after": tx.get("balance_after"),
                    "description": tx.get("description"),
                    "timestamp": str(tx.get("created_at"))
                }
                for tx in transactions
            ],
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
    """Get all subscription prices in ELC - synced with bot.py LICENSE_PRICES"""
    # Use unified function from core.blockchain
    options = get_subscription_options()
    
    # Transform to API format
    plans_data = {}
    for plan_id, plan_info in options["plans"].items():
        plans_data[plan_id] = {
            "name": plan_info["name"],
            "description": plan_info["description"],
            "features": plan_info["features"],
            "prices": {
                "1m": {
                    "elc": plan_info["prices"][1]["elc"],
                    "usd_equivalent": plan_info["prices"][1]["usd"],
                    "discount": options["discounts"][1]
                },
                "3m": {
                    "elc": plan_info["prices"][3]["elc"],
                    "usd_equivalent": plan_info["prices"][3]["usd"],
                    "discount": options["discounts"][3]
                },
                "6m": {
                    "elc": plan_info["prices"][6]["elc"],
                    "usd_equivalent": plan_info["prices"][6]["usd"],
                    "discount": options["discounts"][6]
                },
                "1y": {
                    "elc": plan_info["prices"][12]["elc"],
                    "usd_equivalent": plan_info["prices"][12]["usd"],
                    "discount": options["discounts"][12]
                }
            }
        }
    
    return {
        "currency": "ELC",
        "note": "All prices in LYXEN tokens. 1 ELC = $1 USD",
        "plans": plans_data,
        "payment_methods": options["currencies"],
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
        # Map duration to months
        duration_months = {
            "1m": 1,
            "3m": 3,
            "6m": 6,
            "1y": 12
        }.get(request.duration, 1)
        
        # Get price using unified function
        elc_price = get_license_price(request.plan, duration_months, "elc")
        
        if elc_price == 0 and request.plan != "trial":
            raise HTTPException(400, "Invalid plan or duration")
        
        # Check user's ELC balance using db_elcaro function
        balance = get_elc_balance_db(user_id)
        user_balance = balance.get("available", 0)
        
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
        
        # Deduct ELC from user balance using db_elcaro function
        new_balance = subtract_elc_balance(
            user_id, 
            elc_price, 
            f"Subscription: {request.plan} {request.duration}"
        )
        
        # Calculate subscription duration in days
        duration_days = {
            "1m": 30,
            "3m": 90,
            "6m": 180,
            "1y": 365
        }[request.duration]
        
        # Activate subscription using db.py function
        result = set_user_license(
            user_id=user_id,
            license_type=request.plan,
            period_months=duration_months,
            payment_type="ELC",
            amount=elc_price,
            currency="ELC",
            notes=f"Paid with LYXEN token via webapp"
        )
        
        if not result.get("success"):
            # Refund on failure
            add_elc_balance(user_id, elc_price, "Subscription activation failed - refund")
            raise HTTPException(500, result.get("error", "License activation failed"))
        
        return {
            "success": True,
            "subscription_activated": True,
            "plan": request.plan,
            "duration": request.duration,
            "elc_paid": elc_price,
            "new_balance": new_balance.get("available", 0),
            "expires_in_days": duration_days,
            "message": f"{request.plan.title()} subscription activated for {duration_days} days!"
        }
    except HTTPException:
        raise
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
                """INSERT INTO connected_wallets 
                   (user_id, wallet_address, wallet_type, connected_at)
                   VALUES (?, ?, ?, NOW())
                   ON CONFLICT (user_id, wallet_address) DO UPDATE SET connected_at = NOW()""",
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
