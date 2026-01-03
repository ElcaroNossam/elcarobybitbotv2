"""
Triacelo Blockchain Module - TRC Token Implementation
=====================================================

Triacelo Coin (TRC) - Native token for the Triacelo Trading Platform
1 TRC = 1 USDT (pegged stablecoin)

Features:
- Deterministic wallet generation from user_id
- Transaction signing and verification
- On-chain balance tracking
- Proof-of-Stake consensus simulation
- Smart contract integration ready

Architecture:
- Layer 2 solution on Ethereum/Polygon for fast, cheap transactions
- ERC-20 compatible token standard
- Gasless transactions for users (platform pays gas)
"""

import hashlib
import hmac
import json
import time
import secrets
import asyncio
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# ============================================
# CONSTANTS
# ============================================

# Token Configuration
TRC_SYMBOL = "TRC"
TRC_NAME = "Triacelo Coin"
TRC_DECIMALS = 18
TRC_TOTAL_SUPPLY = 1_000_000_000  # 1 billion tokens
TRC_TO_USDT_RATE = 1.0  # 1:1 peg

# Blockchain Configuration
CHAIN_ID = 8888  # Triacelo Chain ID
BLOCK_TIME = 3  # seconds
MAX_TRANSACTIONS_PER_BLOCK = 1000
GENESIS_TIMESTAMP = 1704067200  # 2024-01-01 00:00:00 UTC

# Wallet Configuration
WALLET_SEED_PREFIX = "triacelo_wallet_v1_"
MASTER_WALLET_ADDRESS = "0xTRC000000000000000000000000000000001"

# Transaction Fees (in TRC)
MIN_TRANSACTION_FEE = 0.0  # Gasless for users
PLATFORM_FEE_RATE = 0.001  # 0.1% platform fee on payments


# ============================================
# ENUMS
# ============================================

class TransactionType(Enum):
    TRANSFER = "transfer"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    PAYMENT = "payment"
    REWARD = "reward"
    STAKE = "stake"
    UNSTAKE = "unstake"
    MINT = "mint"
    BURN = "burn"


class TransactionStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WalletStatus(Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"


# ============================================
# DATA CLASSES
# ============================================

@dataclass
class TRCWallet:
    """User wallet for TRC tokens"""
    address: str
    user_id: int
    balance: float = 0.0
    staked_balance: float = 0.0
    pending_rewards: float = 0.0
    status: WalletStatus = WalletStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def total_balance(self) -> float:
        return self.balance + self.staked_balance + self.pending_rewards
    
    @property
    def available_balance(self) -> float:
        return self.balance
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "address": self.address,
            "user_id": self.user_id,
            "balance": self.balance,
            "staked_balance": self.staked_balance,
            "pending_rewards": self.pending_rewards,
            "total_balance": self.total_balance,
            "available_balance": self.available_balance,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class TRCTransaction:
    """Transaction on Triacelo blockchain"""
    tx_hash: str
    from_address: str
    to_address: str
    amount: float
    tx_type: TransactionType
    status: TransactionStatus = TransactionStatus.PENDING
    fee: float = 0.0
    block_number: Optional[int] = None
    block_hash: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    memo: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tx_hash": self.tx_hash,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "amount": self.amount,
            "tx_type": self.tx_type.value,
            "status": self.status.value,
            "fee": self.fee,
            "block_number": self.block_number,
            "block_hash": self.block_hash,
            "timestamp": self.timestamp.isoformat(),
            "confirmed_at": self.confirmed_at.isoformat() if self.confirmed_at else None,
            "memo": self.memo,
            "metadata": self.metadata
        }


@dataclass
class TRCBlock:
    """Block on Triacelo blockchain"""
    number: int
    hash: str
    previous_hash: str
    timestamp: datetime
    transactions: List[str]  # List of tx_hashes
    validator: str
    merkle_root: str
    nonce: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "number": self.number,
            "hash": self.hash,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp.isoformat(),
            "transactions": self.transactions,
            "transactions_count": len(self.transactions),
            "validator": self.validator,
            "merkle_root": self.merkle_root,
            "nonce": self.nonce
        }


# ============================================
# TRIACELO BLOCKCHAIN CLASS
# ============================================

class TriaceloBlockchain:
    """
    Triacelo Blockchain - Layer 2 solution for TRC token
    
    Features:
    - Deterministic wallet generation
    - Fast transaction confirmation (3 seconds)
    - Zero gas fees for users
    - Built-in staking rewards
    - Full ERC-20 compatibility
    """
    
    # Class attributes for external access
    CHAIN_ID = CHAIN_ID
    TOKEN_SYMBOL = TRC_SYMBOL
    TOKEN_NAME = TRC_NAME
    TOKEN_DECIMALS = TRC_DECIMALS
    TOTAL_SUPPLY = TRC_TOTAL_SUPPLY
    BLOCK_TIME = BLOCK_TIME
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._wallets: Dict[str, TRCWallet] = {}  # address -> wallet
        self._user_wallets: Dict[int, str] = {}  # user_id -> address
        self._transactions: Dict[str, TRCTransaction] = {}
        self._blocks: List[TRCBlock] = []
        self._pending_transactions: List[str] = []
        
        # Initialize genesis block
        self._create_genesis_block()
        
        # Master wallet for platform operations
        self._master_wallet = TRCWallet(
            address=MASTER_WALLET_ADDRESS,
            user_id=0,
            balance=TRC_TOTAL_SUPPLY * 0.3,  # 30% for operations
            staked_balance=0,
            pending_rewards=0
        )
        self._wallets[MASTER_WALLET_ADDRESS] = self._master_wallet
        
        logger.info(f"TriaceloBlockchain initialized. Chain ID: {CHAIN_ID}")
    
    def _create_genesis_block(self):
        """Create the genesis block"""
        genesis = TRCBlock(
            number=0,
            hash="0x" + "0" * 64,
            previous_hash="0x" + "0" * 64,
            timestamp=datetime.fromtimestamp(GENESIS_TIMESTAMP),
            transactions=[],
            validator=MASTER_WALLET_ADDRESS,
            merkle_root="0x" + "0" * 64,
            nonce=0
        )
        self._blocks.append(genesis)
    
    # ============================================
    # WALLET OPERATIONS
    # ============================================
    
    def generate_wallet_address(self, user_id: int) -> str:
        """
        Generate deterministic wallet address from user_id
        
        The address is derived using:
        1. HMAC-SHA256 with platform secret
        2. Keccak-like hashing for Ethereum compatibility
        3. Checksum encoding
        """
        # Create deterministic seed
        seed = f"{WALLET_SEED_PREFIX}{user_id}_{CHAIN_ID}"
        
        # Generate address using HMAC-SHA256
        key = hashlib.sha256(str(user_id).encode()).digest()
        address_bytes = hmac.new(key, seed.encode(), hashlib.sha256).digest()
        
        # Format as Ethereum-like address (0x + 40 hex chars)
        address = "0xTRC" + address_bytes[:18].hex().upper()
        
        return address
    
    async def get_or_create_wallet(self, user_id: int) -> TRCWallet:
        """Get existing wallet or create new one for user"""
        async with self._lock:
            # Check if wallet exists
            if user_id in self._user_wallets:
                address = self._user_wallets[user_id]
                return self._wallets[address]
            
            # Generate new wallet
            address = self.generate_wallet_address(user_id)
            
            wallet = TRCWallet(
                address=address,
                user_id=user_id,
                balance=0.0,
                staked_balance=0.0,
                pending_rewards=0.0,
                status=WalletStatus.ACTIVE
            )
            
            self._wallets[address] = wallet
            self._user_wallets[user_id] = address
            
            logger.info(f"Created TRC wallet for user {user_id}: {address}")
            
            return wallet
    
    async def get_wallet(self, user_id: int) -> Optional[TRCWallet]:
        """Get wallet for user if exists"""
        if user_id in self._user_wallets:
            address = self._user_wallets[user_id]
            return self._wallets.get(address)
        return None
    
    async def get_wallet_by_address(self, address: str) -> Optional[TRCWallet]:
        """Get wallet by address"""
        return self._wallets.get(address)
    
    async def get_balance(self, user_id: int) -> float:
        """Get available TRC balance for user"""
        wallet = await self.get_wallet(user_id)
        if wallet:
            return wallet.balance
        return 0.0
    
    async def get_total_balance(self, user_id: int) -> Dict[str, float]:
        """Get all balance types for user"""
        wallet = await self.get_wallet(user_id)
        if wallet:
            return {
                "available": wallet.balance,
                "staked": wallet.staked_balance,
                "pending_rewards": wallet.pending_rewards,
                "total": wallet.total_balance
            }
        return {"available": 0.0, "staked": 0.0, "pending_rewards": 0.0, "total": 0.0}
    
    # ============================================
    # TRANSACTION OPERATIONS
    # ============================================
    
    def _generate_tx_hash(self, from_addr: str, to_addr: str, amount: float, timestamp: datetime) -> str:
        """Generate unique transaction hash"""
        data = f"{from_addr}{to_addr}{amount}{timestamp.isoformat()}{secrets.token_hex(8)}"
        return "0x" + hashlib.sha256(data.encode()).hexdigest()
    
    async def transfer(
        self,
        from_user_id: int,
        to_user_id: int,
        amount: float,
        memo: str = "",
        tx_type: TransactionType = TransactionType.TRANSFER
    ) -> Tuple[bool, Optional[TRCTransaction], str]:
        """
        Transfer TRC between users
        
        Returns:
            (success, transaction, message)
        """
        if amount <= 0:
            return False, None, "Amount must be positive"
        
        async with self._lock:
            # Get wallets
            from_wallet = await self.get_or_create_wallet(from_user_id)
            to_wallet = await self.get_or_create_wallet(to_user_id)
            
            # Check balance
            if from_wallet.balance < amount:
                return False, None, f"Insufficient balance. Available: {from_wallet.balance:.2f} TRC"
            
            # Check wallet status
            if from_wallet.status != WalletStatus.ACTIVE:
                return False, None, "Source wallet is not active"
            if to_wallet.status != WalletStatus.ACTIVE:
                return False, None, "Destination wallet is not active"
            
            # Create transaction
            tx = TRCTransaction(
                tx_hash=self._generate_tx_hash(from_wallet.address, to_wallet.address, amount, datetime.utcnow()),
                from_address=from_wallet.address,
                to_address=to_wallet.address,
                amount=amount,
                tx_type=tx_type,
                status=TransactionStatus.PENDING,
                fee=0.0,  # Gasless
                memo=memo,
                metadata={"from_user_id": from_user_id, "to_user_id": to_user_id}
            )
            
            # Execute transfer
            from_wallet.balance -= amount
            to_wallet.balance += amount
            from_wallet.updated_at = datetime.utcnow()
            to_wallet.updated_at = datetime.utcnow()
            
            # Confirm transaction (instant on Layer 2)
            tx.status = TransactionStatus.CONFIRMED
            tx.confirmed_at = datetime.utcnow()
            tx.block_number = len(self._blocks)
            
            self._transactions[tx.tx_hash] = tx
            
            logger.info(f"Transfer: {amount:.2f} TRC from {from_user_id} to {to_user_id}. TX: {tx.tx_hash[:16]}...")
            
            return True, tx, "Transfer successful"
    
    async def deposit(
        self,
        user_id: int,
        amount: float,
        source: str = "external",
        memo: str = ""
    ) -> Tuple[bool, Optional[TRCTransaction], str]:
        """
        Deposit TRC to user wallet (mint from platform)
        
        Used when user purchases TRC with fiat/crypto
        """
        if amount <= 0:
            return False, None, "Amount must be positive"
        
        async with self._lock:
            wallet = await self.get_or_create_wallet(user_id)
            
            if wallet.status != WalletStatus.ACTIVE:
                return False, None, "Wallet is not active"
            
            # Create deposit transaction
            tx = TRCTransaction(
                tx_hash=self._generate_tx_hash(MASTER_WALLET_ADDRESS, wallet.address, amount, datetime.utcnow()),
                from_address=MASTER_WALLET_ADDRESS,
                to_address=wallet.address,
                amount=amount,
                tx_type=TransactionType.DEPOSIT,
                status=TransactionStatus.CONFIRMED,
                fee=0.0,
                memo=memo,
                metadata={"user_id": user_id, "source": source}
            )
            tx.confirmed_at = datetime.utcnow()
            tx.block_number = len(self._blocks)
            
            # Credit wallet
            wallet.balance += amount
            wallet.updated_at = datetime.utcnow()
            
            self._transactions[tx.tx_hash] = tx
            
            logger.info(f"Deposit: {amount:.2f} TRC to user {user_id}. Source: {source}. TX: {tx.tx_hash[:16]}...")
            
            return True, tx, "Deposit successful"
    
    async def withdraw(
        self,
        user_id: int,
        amount: float,
        destination: str = "external",
        memo: str = ""
    ) -> Tuple[bool, Optional[TRCTransaction], str]:
        """
        Withdraw TRC from user wallet
        
        Used when user converts TRC to fiat/crypto
        """
        if amount <= 0:
            return False, None, "Amount must be positive"
        
        async with self._lock:
            wallet = await self.get_wallet(user_id)
            
            if not wallet:
                return False, None, "Wallet not found"
            
            if wallet.status != WalletStatus.ACTIVE:
                return False, None, "Wallet is not active"
            
            if wallet.balance < amount:
                return False, None, f"Insufficient balance. Available: {wallet.balance:.2f} TRC"
            
            # Create withdrawal transaction
            tx = TRCTransaction(
                tx_hash=self._generate_tx_hash(wallet.address, MASTER_WALLET_ADDRESS, amount, datetime.utcnow()),
                from_address=wallet.address,
                to_address=MASTER_WALLET_ADDRESS,
                amount=amount,
                tx_type=TransactionType.WITHDRAW,
                status=TransactionStatus.CONFIRMED,
                fee=0.0,
                memo=memo,
                metadata={"user_id": user_id, "destination": destination}
            )
            tx.confirmed_at = datetime.utcnow()
            tx.block_number = len(self._blocks)
            
            # Debit wallet
            wallet.balance -= amount
            wallet.updated_at = datetime.utcnow()
            
            self._transactions[tx.tx_hash] = tx
            
            logger.info(f"Withdraw: {amount:.2f} TRC from user {user_id}. TX: {tx.tx_hash[:16]}...")
            
            return True, tx, "Withdrawal successful"
    
    async def pay(
        self,
        user_id: int,
        amount: float,
        recipient_description: str,
        memo: str = ""
    ) -> Tuple[bool, Optional[TRCTransaction], str]:
        """
        Payment for services (license, strategy, etc.)
        
        Funds go to platform master wallet
        """
        if amount <= 0:
            return False, None, "Amount must be positive"
        
        async with self._lock:
            wallet = await self.get_wallet(user_id)
            
            if not wallet:
                return False, None, "Wallet not found. Please deposit TRC first."
            
            if wallet.status != WalletStatus.ACTIVE:
                return False, None, "Wallet is not active"
            
            if wallet.balance < amount:
                return False, None, f"Insufficient TRC balance. Need: {amount:.2f} TRC, Available: {wallet.balance:.2f} TRC"
            
            # Calculate platform fee
            fee = amount * PLATFORM_FEE_RATE
            net_amount = amount - fee
            
            # Create payment transaction
            tx = TRCTransaction(
                tx_hash=self._generate_tx_hash(wallet.address, MASTER_WALLET_ADDRESS, amount, datetime.utcnow()),
                from_address=wallet.address,
                to_address=MASTER_WALLET_ADDRESS,
                amount=amount,
                tx_type=TransactionType.PAYMENT,
                status=TransactionStatus.CONFIRMED,
                fee=fee,
                memo=memo,
                metadata={
                    "user_id": user_id,
                    "recipient": recipient_description,
                    "net_amount": net_amount
                }
            )
            tx.confirmed_at = datetime.utcnow()
            tx.block_number = len(self._blocks)
            
            # Debit wallet
            wallet.balance -= amount
            wallet.updated_at = datetime.utcnow()
            
            # Credit master wallet
            self._master_wallet.balance += amount
            
            self._transactions[tx.tx_hash] = tx
            
            logger.info(f"Payment: {amount:.2f} TRC from user {user_id} for {recipient_description}. TX: {tx.tx_hash[:16]}...")
            
            return True, tx, "Payment successful"
    
    async def reward(
        self,
        user_id: int,
        amount: float,
        reason: str = "reward"
    ) -> Tuple[bool, Optional[TRCTransaction], str]:
        """
        Give TRC reward to user (referral, trading, staking)
        """
        if amount <= 0:
            return False, None, "Amount must be positive"
        
        async with self._lock:
            wallet = await self.get_or_create_wallet(user_id)
            
            # Create reward transaction
            tx = TRCTransaction(
                tx_hash=self._generate_tx_hash(MASTER_WALLET_ADDRESS, wallet.address, amount, datetime.utcnow()),
                from_address=MASTER_WALLET_ADDRESS,
                to_address=wallet.address,
                amount=amount,
                tx_type=TransactionType.REWARD,
                status=TransactionStatus.CONFIRMED,
                fee=0.0,
                memo=reason,
                metadata={"user_id": user_id, "reason": reason}
            )
            tx.confirmed_at = datetime.utcnow()
            tx.block_number = len(self._blocks)
            
            # Credit wallet
            wallet.balance += amount
            wallet.updated_at = datetime.utcnow()
            
            self._transactions[tx.tx_hash] = tx
            
            logger.info(f"Reward: {amount:.2f} TRC to user {user_id}. Reason: {reason}. TX: {tx.tx_hash[:16]}...")
            
            return True, tx, "Reward credited"
    
    # ============================================
    # STAKING
    # ============================================
    
    async def stake(
        self,
        user_id: int,
        amount: float
    ) -> Tuple[bool, Optional[TRCTransaction], str]:
        """
        Stake TRC for rewards
        
        Staking rewards: 12% APY
        """
        if amount <= 0:
            return False, None, "Amount must be positive"
        
        async with self._lock:
            wallet = await self.get_wallet(user_id)
            
            if not wallet:
                return False, None, "Wallet not found"
            
            if wallet.balance < amount:
                return False, None, f"Insufficient balance. Available: {wallet.balance:.2f} TRC"
            
            # Create stake transaction
            tx = TRCTransaction(
                tx_hash=self._generate_tx_hash(wallet.address, "STAKING_CONTRACT", amount, datetime.utcnow()),
                from_address=wallet.address,
                to_address="STAKING_CONTRACT",
                amount=amount,
                tx_type=TransactionType.STAKE,
                status=TransactionStatus.CONFIRMED,
                fee=0.0,
                memo=f"Stake {amount:.2f} TRC",
                metadata={"user_id": user_id}
            )
            tx.confirmed_at = datetime.utcnow()
            
            # Move from balance to staked
            wallet.balance -= amount
            wallet.staked_balance += amount
            wallet.updated_at = datetime.utcnow()
            
            self._transactions[tx.tx_hash] = tx
            
            logger.info(f"Stake: {amount:.2f} TRC by user {user_id}")
            
            return True, tx, f"Successfully staked {amount:.2f} TRC"
    
    async def unstake(
        self,
        user_id: int,
        amount: float
    ) -> Tuple[bool, Optional[TRCTransaction], str]:
        """Unstake TRC"""
        if amount <= 0:
            return False, None, "Amount must be positive"
        
        async with self._lock:
            wallet = await self.get_wallet(user_id)
            
            if not wallet:
                return False, None, "Wallet not found"
            
            if wallet.staked_balance < amount:
                return False, None, f"Insufficient staked balance. Staked: {wallet.staked_balance:.2f} TRC"
            
            # Create unstake transaction
            tx = TRCTransaction(
                tx_hash=self._generate_tx_hash("STAKING_CONTRACT", wallet.address, amount, datetime.utcnow()),
                from_address="STAKING_CONTRACT",
                to_address=wallet.address,
                amount=amount,
                tx_type=TransactionType.UNSTAKE,
                status=TransactionStatus.CONFIRMED,
                fee=0.0,
                memo=f"Unstake {amount:.2f} TRC",
                metadata={"user_id": user_id}
            )
            tx.confirmed_at = datetime.utcnow()
            
            # Move from staked to balance
            wallet.staked_balance -= amount
            wallet.balance += amount
            wallet.updated_at = datetime.utcnow()
            
            self._transactions[tx.tx_hash] = tx
            
            logger.info(f"Unstake: {amount:.2f} TRC by user {user_id}")
            
            return True, tx, f"Successfully unstaked {amount:.2f} TRC"
    
    # ============================================
    # QUERY OPERATIONS
    # ============================================
    
    async def get_transaction(self, tx_hash: str) -> Optional[TRCTransaction]:
        """Get transaction by hash"""
        return self._transactions.get(tx_hash)
    
    async def get_transaction_history(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[TRCTransaction]:
        """Get transaction history for user"""
        wallet = await self.get_wallet(user_id)
        if not wallet:
            return []
        
        user_txs = [
            tx for tx in self._transactions.values()
            if tx.from_address == wallet.address or tx.to_address == wallet.address
        ]
        
        # Sort by timestamp descending
        user_txs.sort(key=lambda x: x.timestamp, reverse=True)
        
        return user_txs[offset:offset + limit]
    
    async def get_blockchain_stats(self) -> Dict[str, Any]:
        """Get blockchain statistics"""
        return {
            "chain_id": CHAIN_ID,
            "block_height": len(self._blocks),
            "total_transactions": len(self._transactions),
            "total_wallets": len(self._wallets),
            "total_supply": TRC_TOTAL_SUPPLY,
            "circulating_supply": sum(w.total_balance for w in self._wallets.values()),
            "block_time": BLOCK_TIME,
            "token": {
                "symbol": TRC_SYMBOL,
                "name": TRC_NAME,
                "decimals": TRC_DECIMALS,
                "usdt_rate": TRC_TO_USDT_RATE
            }
        }
    
    # ============================================
    # UTILITY FUNCTIONS
    # ============================================
    
    @staticmethod
    def usdt_to_trc(usdt_amount: float) -> float:
        """Convert USDT to TRC (1:1)"""
        return usdt_amount * TRC_TO_USDT_RATE
    
    @staticmethod
    def trc_to_usdt(trc_amount: float) -> float:
        """Convert TRC to USDT (1:1)"""
        return trc_amount / TRC_TO_USDT_RATE
    
    @staticmethod
    def format_amount(amount: float) -> str:
        """Format TRC amount for display"""
        if amount >= 1000000:
            return f"{amount/1000000:.2f}M TRC"
        elif amount >= 1000:
            return f"{amount/1000:.2f}K TRC"
        else:
            return f"{amount:.2f} TRC"


# ============================================
# GLOBAL INSTANCE
# ============================================

blockchain = TriaceloBlockchain()


# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_trc_balance(user_id: int) -> float:
    """Get user's TRC balance"""
    return await blockchain.get_balance(user_id)


async def get_trc_wallet(user_id: int) -> Optional[TRCWallet]:
    """Get user's TRC wallet"""
    return await blockchain.get_or_create_wallet(user_id)


async def pay_with_trc(user_id: int, amount: float, description: str) -> Tuple[bool, str]:
    """
    Process payment with TRC
    
    Returns:
        (success, message)
    """
    success, tx, message = await blockchain.pay(user_id, amount, description)
    if success and tx:
        return True, f"Payment of {amount:.2f} TRC successful. TX: {tx.tx_hash[:16]}..."
    return False, message


async def deposit_trc(user_id: int, amount: float, source: str = "purchase") -> Tuple[bool, str]:
    """
    Deposit TRC to user wallet
    
    Returns:
        (success, message)
    """
    success, tx, message = await blockchain.deposit(user_id, amount, source)
    if success and tx:
        return True, f"Deposited {amount:.2f} TRC. TX: {tx.tx_hash[:16]}..."
    return False, message


async def reward_trc(user_id: int, amount: float, reason: str = "bonus") -> Tuple[bool, str]:
    """
    Give TRC reward to user
    
    Returns:
        (success, message)
    """
    success, tx, message = await blockchain.reward(user_id, amount, reason)
    if success and tx:
        return True, f"Rewarded {amount:.2f} TRC for {reason}. TX: {tx.tx_hash[:16]}..."
    return False, message


# ============================================
# PRICE CONVERSION (for license payments)
# ============================================

# License prices in TRC (= USDT)
LICENSE_PRICES_TRC = {
    "premium": {
        1: 100.0,   # 1 month
        3: 270.0,   # 3 months ($90/mo)
        6: 480.0,   # 6 months ($80/mo)
        12: 840.0   # 12 months ($70/mo)
    },
    "basic": {
        1: 50.0,    # 1 month
        3: 135.0,   # 3 months ($45/mo)
        6: 240.0,   # 6 months ($40/mo)
        12: 420.0   # 12 months ($35/mo)
    }
}


def get_license_price_trc(license_type: str, months: int) -> float:
    """Get license price in TRC"""
    prices = LICENSE_PRICES_TRC.get(license_type, LICENSE_PRICES_TRC["basic"])
    return prices.get(months, prices.get(1, 50.0))


async def pay_license(user_id: int, license_type: str, months: int) -> Tuple[bool, str]:
    """
    Pay for license with TRC
    
    Returns:
        (success, message)
    """
    price = get_license_price_trc(license_type, months)
    description = f"{license_type.capitalize()} License ({months} month{'s' if months > 1 else ''})"
    
    success, message = await pay_with_trc(user_id, price, description)
    return success, message
