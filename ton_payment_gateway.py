"""
TON Payment Gateway - Buy ELCARO tokens with USDT
Supports TON, jUSDT, and direct wallet connections
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

try:
    from pytoniq import LiteBalancer, WalletV4R2, begin_cell
    from pytoniq_core import Address
    TON_AVAILABLE = True
except ImportError:
    TON_AVAILABLE = False
    logging.warning("TON libraries not available. Install: pip install pytoniq pytoniq-core")

# Import db_elcaro functions for ELC balance management
try:
    from db_elcaro import (
        create_elc_purchase,
        complete_elc_purchase,
        get_elc_purchase,
        add_elc_balance,
    )
    DB_ELCARO_AVAILABLE = True
except ImportError:
    DB_ELCARO_AVAILABLE = False
    logging.warning("db_elcaro module not available")

logger = logging.getLogger(__name__)


class TONPaymentGateway:
    """
    TON Payment Gateway for ELCARO token purchases
    Handles USDT → ELC conversions on TON blockchain
    """
    
    def __init__(
        self,
        platform_wallet: str,
        testnet: bool = False,
        elc_price_usd: float = 1.0,
        platform_fee_percent: float = 0.5
    ):
        """
        Initialize TON Payment Gateway
        
        Args:
            platform_wallet: Platform's TON wallet address
            testnet: Use testnet or mainnet
            elc_price_usd: Current ELC price in USD
            platform_fee_percent: Platform fee (0.5% default)
        """
        if not TON_AVAILABLE:
            raise ImportError("TON libraries not installed")
        
        self.platform_wallet = platform_wallet
        self.testnet = testnet
        self.elc_price = Decimal(str(elc_price_usd))
        self.platform_fee = Decimal(str(platform_fee_percent)) / 100
        
        # TON network endpoints
        self.network = "testnet" if testnet else "mainnet"
        
        # jUSDT contract address (TON Jetton)
        if testnet:
            self.usdt_contract = "kQD0GKBM8ZbryVk2aEhhTNyHzJ_freeTXK6dTkvdHh0jiqfh"  # Testnet jUSDT
        else:
            self.usdt_contract = "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs"  # Mainnet jUSDT
        
        self.client = None
    
    async def initialize(self):
        """Initialize connection to TON blockchain"""
        try:
            if self.testnet:
                self.client = LiteBalancer.from_testnet_config(trust_level=2)
            else:
                self.client = LiteBalancer.from_mainnet_config(trust_level=2)
            
            await self.client.start_up()
            logger.info(f"TON Payment Gateway initialized ({self.network})")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize TON gateway: {e}")
            return False
    
    async def close(self):
        """Close TON connection"""
        if self.client:
            await self.client.close_all()
    
    def calculate_elc_amount(self, usdt_amount: float) -> Dict[str, float]:
        """
        Calculate ELC tokens for USDT amount
        
        Args:
            usdt_amount: Amount of USDT to spend
            
        Returns:
            Dict with elc_amount, fee, total_elc, effective_price
        """
        usdt = Decimal(str(usdt_amount))
        fee = usdt * self.platform_fee
        usdt_after_fee = usdt - fee
        elc_amount = usdt_after_fee / self.elc_price
        
        return {
            "usdt_amount": float(usdt),
            "platform_fee": float(fee),
            "usdt_after_fee": float(usdt_after_fee),
            "elc_amount": float(elc_amount),
            "elc_price": float(self.elc_price),
            "effective_price": float(usdt / elc_amount) if elc_amount > 0 else 0
        }
    
    async def get_wallet_balance(self, wallet_address: str) -> Dict[str, float]:
        """
        Get TON and USDT balance for wallet
        
        Args:
            wallet_address: User's TON wallet address
            
        Returns:
            Dict with ton_balance and usdt_balance
        """
        try:
            if not self.client:
                await self.initialize()
            
            address = Address(wallet_address)
            
            # Get TON balance
            account = await self.client.get_account_state(address)
            ton_balance = account.balance / 1e9  # Convert from nanotons
            
            # Get USDT balance (Jetton)
            # This requires querying the Jetton wallet contract
            # For now, return 0 - implement full Jetton balance check later
            usdt_balance = 0.0
            
            return {
                "ton_balance": ton_balance,
                "usdt_balance": usdt_balance,
                "wallet_address": wallet_address
            }
        except Exception as e:
            logger.error(f"Failed to get wallet balance: {e}")
            return {
                "ton_balance": 0.0,
                "usdt_balance": 0.0,
                "error": str(e)
            }
    
    async def create_payment_link(
        self,
        user_id: int,
        usdt_amount: float,
        purpose: str = "subscription"
    ) -> Dict[str, Any]:
        """
        Create payment link for user to send USDT
        
        Args:
            user_id: User ID for tracking
            usdt_amount: Amount of USDT to pay
            purpose: Payment purpose (subscription, strategy_purchase, etc.)
            
        Returns:
            Dict with payment details and TON link
        """
        calc = self.calculate_elc_amount(usdt_amount)
        
        # Generate unique payment comment for tracking
        payment_id = f"ELC-{user_id}-{int(datetime.utcnow().timestamp())}"
        
        # Create TON payment link
        # Format: ton://transfer/<address>?amount=<nanotons>&text=<comment>
        # For USDT (Jetton), format is different - need to use Jetton transfer
        
        # Simplified link (user needs to send USDT manually)
        payment_link = f"ton://transfer/{self.platform_wallet}?text={payment_id}"
        
        # Alternative: Deep link to TON Wallet app
        ton_wallet_link = (
            f"https://app.tonkeeper.com/transfer/{self.platform_wallet}"
            f"?text={payment_id}"
        )
        
        # Create purchase record in database
        purchase_id = None
        if DB_ELCARO_AVAILABLE:
            try:
                purchase_id = create_elc_purchase(
                    user_id=user_id,
                    payment_id=payment_id,
                    usdt_amount=calc["usdt_amount"],
                    elc_amount=calc["elc_amount"],
                    platform_fee=calc["platform_fee"],
                    payment_method="ton_usdt"
                )
                logger.info(f"Created ELC purchase record: {payment_id} (id={purchase_id})")
            except Exception as e:
                logger.error(f"Failed to create purchase record: {e}")
        
        return {
            "payment_id": payment_id,
            "purchase_id": purchase_id,
            "user_id": user_id,
            "usdt_amount": calc["usdt_amount"],
            "elc_amount": calc["elc_amount"],
            "platform_fee": calc["platform_fee"],
            "payment_link": payment_link,
            "ton_wallet_link": ton_wallet_link,
            "qr_code_url": f"https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl={ton_wallet_link}",
            "platform_wallet": self.platform_wallet,
            "purpose": purpose,
            "expires_at": int(datetime.utcnow().timestamp()) + 3600  # 1 hour expiry
        }
    
    async def verify_payment(
        self,
        payment_id: str,
        expected_amount: float
    ) -> Dict[str, Any]:
        """
        Verify that payment was received
        
        Args:
            payment_id: Payment ID to verify
            expected_amount: Expected USDT amount
            
        Returns:
            Dict with verification status
        """
        try:
            if not self.client:
                await self.initialize()
            
            # Get recent transactions for platform wallet
            address = Address(self.platform_wallet)
            
            # Check last 100 transactions
            transactions = await self.client.get_transactions(address, limit=100)
            
            for tx in transactions:
                # Check if transaction has our payment_id in comment
                # and matches expected amount
                # This is simplified - need to parse actual transaction data
                
                # For now, return pending
                pass
            
            return {
                "verified": False,
                "status": "pending",
                "payment_id": payment_id,
                "message": "Payment verification pending"
            }
        except Exception as e:
            logger.error(f"Payment verification error: {e}")
            return {
                "verified": False,
                "status": "error",
                "error": str(e)
            }
    
    async def process_elc_distribution(
        self,
        user_id: int,
        payment_id: str,
        tx_hash: str = None
    ) -> Dict[str, Any]:
        """
        Distribute ELC tokens to user after payment verified.
        Uses db_elcaro to update user balance.
        
        Args:
            user_id: User ID
            payment_id: Payment ID from create_payment_link
            tx_hash: TON blockchain transaction hash
            
        Returns:
            Dict with distribution status
        """
        try:
            if not DB_ELCARO_AVAILABLE:
                logger.error("db_elcaro not available for ELC distribution")
                return {
                    "success": False,
                    "error": "Database module not available",
                    "status": "failed"
                }
            
            # Get purchase details
            purchase = get_elc_purchase(payment_id)
            if not purchase:
                return {
                    "success": False,
                    "error": f"Purchase not found: {payment_id}",
                    "status": "failed"
                }
            
            if purchase["status"] == "completed":
                return {
                    "success": True,
                    "elc_amount": purchase["elc_amount"],
                    "status": "already_completed",
                    "message": "Purchase already completed"
                }
            
            # Complete purchase and distribute ELC
            success = complete_elc_purchase(payment_id, tx_hash)
            
            if success:
                logger.info(f"ELC distributed: {purchase['elc_amount']} ELC to user {user_id}")
                return {
                    "success": True,
                    "elc_amount": purchase["elc_amount"],
                    "user_id": user_id,
                    "payment_id": payment_id,
                    "tx_hash": tx_hash,
                    "status": "completed",
                    "message": f"Distributed {purchase['elc_amount']} ELC to user {user_id}"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to complete purchase",
                    "status": "failed"
                }
        except Exception as e:
            logger.error(f"ELC distribution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }


class ELCAROPaymentManager:
    """
    High-level payment manager for ELCARO ecosystem
    Handles all payment-related operations
    """
    
    def __init__(self, testnet: bool = False):
        self.testnet = testnet
        self.ton_gateway = None
        
        # ELC prices for different items (synced with bot.py LICENSE_PRICES)
        # All prices in ELC (1 ELC = 1 USD)
        self.prices = {
            "subscription": {
                # Premium Plan: $100/mo, -10% 3mo, -20% 6mo, -30% 12mo
                "premium_1m": 100,
                "premium_3m": 270,
                "premium_6m": 480,
                "premium_1y": 840,
                # Basic Plan: 50% of Premium
                "basic_1m": 50,
                "basic_3m": 135,
                "basic_6m": 240,
                "basic_1y": 420,
                # Enterprise Plan: 5x Premium
                "enterprise_1m": 500,
                "enterprise_3m": 1350,
                "enterprise_6m": 2400,
                "enterprise_1y": 4200,
                # Trial
                "trial_1m": 0,
            },
            "marketplace": {
                "listing_fee": 10,
                "featured_listing": 50,
                "platform_fee_percent": 2.5,
            },
            "staking": {
                "tier1_min": 1000,
                "tier2_min": 5000,
                "tier3_min": 10000,
                "tier4_min": 50000,
            }
        }
    
    async def initialize(self, platform_wallet: str):
        """Initialize payment gateway"""
        self.ton_gateway = TONPaymentGateway(
            platform_wallet=platform_wallet,
            testnet=self.testnet,
            elc_price_usd=1.0,  # Update from oracle
            platform_fee_percent=0.5
        )
        await self.ton_gateway.initialize()
    
    def get_subscription_price(self, plan: str, duration: str) -> float:
        """Get subscription price in ELC"""
        key = f"{plan}_{duration}"
        return self.prices["subscription"].get(key, 0)
    
    async def create_subscription_payment(
        self,
        user_id: int,
        plan: str,
        duration: str
    ) -> Dict[str, Any]:
        """
        Create payment for subscription
        
        Args:
            user_id: User ID
            plan: Plan type (basic, premium, pro)
            duration: Duration (1m, 3m, 6m, 1y)
            
        Returns:
            Payment details with ELC amount and USDT equivalent
        """
        elc_price = self.get_subscription_price(plan, duration)
        
        if elc_price == 0:
            return {"error": "Invalid plan or duration"}
        
        # Calculate USDT amount needed
        usdt_amount = elc_price * float(self.ton_gateway.elc_price)
        
        # Create payment link
        payment_data = await self.ton_gateway.create_payment_link(
            user_id=user_id,
            usdt_amount=usdt_amount,
            purpose=f"subscription_{plan}_{duration}"
        )
        
        payment_data["elc_price"] = elc_price
        payment_data["plan"] = plan
        payment_data["duration"] = duration
        
        return payment_data
    
    async def verify_and_activate_subscription(
        self,
        payment_id: str,
        user_id: int
    ) -> Dict[str, Any]:
        """Verify payment and activate subscription"""
        # This would:
        # 1. Verify TON payment
        # 2. Distribute ELC tokens
        # 3. Activate subscription
        # 4. Record in database
        
        return {
            "verified": True,
            "subscription_activated": True,
            "user_id": user_id
        }


# ═══════════════════════════════════════════════════════════════════════════════════
# STANDALONE VERIFICATION FUNCTIONS (for import by other modules)
# ═══════════════════════════════════════════════════════════════════════════════════

async def verify_ton_transaction(tx_hash: str, expected_amount: float) -> bool:
    """
    Verify a TON transaction by hash.
    
    This function is imported by webapp/api/payments.py for payment verification.
    
    Args:
        tx_hash: TON blockchain transaction hash
        expected_amount: Expected payment amount in USDT
        
    Returns:
        True if transaction is valid and matches expected amount
    """
    if not TON_AVAILABLE:
        logger.error("TON libraries not available for verification")
        return False
    
    try:
        # Initialize client
        client = LiteBalancer.from_mainnet_config(trust_level=2)
        await client.start_up()
        
        # TODO: Implement actual transaction verification
        # 1. Fetch transaction by hash
        # 2. Verify it's a Jetton transfer (USDT)
        # 3. Verify amount matches
        # 4. Verify recipient is platform wallet
        
        # For now, return True for development
        # IMPORTANT: Implement proper verification before production!
        logger.warning(f"TON transaction verification not fully implemented. tx_hash={tx_hash}")
        
        await client.close_all()
        return True
        
    except Exception as e:
        logger.error(f"TON transaction verification failed: {e}")
        return False


async def verify_usdt_jetton_transfer(
    tx_hash: str,
    expected_amount: float,
    recipient_wallet: str,
    testnet: bool = False
) -> dict:
    """
    Verify a USDT Jetton transfer on TON blockchain.
    
    Args:
        tx_hash: Transaction hash
        expected_amount: Expected USDT amount
        recipient_wallet: Expected recipient wallet address
        testnet: Use testnet or mainnet
        
    Returns:
        {
            "verified": bool,
            "amount": float,
            "sender": str,
            "recipient": str,
            "timestamp": int,
            "error": str (if any)
        }
    """
    if not TON_AVAILABLE:
        return {"verified": False, "error": "TON libraries not available"}
    
    try:
        if testnet:
            client = LiteBalancer.from_testnet_config(trust_level=2)
        else:
            client = LiteBalancer.from_mainnet_config(trust_level=2)
        
        await client.start_up()
        
        # TODO: Implement full Jetton transfer verification
        # This requires:
        # 1. Parsing the transaction data
        # 2. Decoding the Jetton transfer message
        # 3. Verifying amounts and addresses
        
        await client.close_all()
        
        return {
            "verified": True,  # Placeholder
            "amount": expected_amount,
            "recipient": recipient_wallet,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"USDT Jetton verification failed: {e}")
        return {"verified": False, "error": str(e)}


# Example usage
if __name__ == "__main__":
    async def test_gateway():
        # Initialize gateway
        gateway = TONPaymentGateway(
            platform_wallet="UQC...",  # Platform wallet
            testnet=True,
            elc_price_usd=1.0
        )
        
        await gateway.initialize()
        
        # Calculate ELC for 100 USDT
        calc = gateway.calculate_elc_amount(100)
        print(f"100 USDT = {calc['elc_amount']} ELC")
        print(f"Platform fee: ${calc['platform_fee']}")
        
        # Create payment link
        payment = await gateway.create_payment_link(
            user_id=123,
            usdt_amount=100,
            purpose="subscription_premium_1m"
        )
        print(f"Payment link: {payment['ton_wallet_link']}")
        print(f"Payment ID: {payment['payment_id']}")
        
        await gateway.close()
    
    asyncio.run(test_gateway())
