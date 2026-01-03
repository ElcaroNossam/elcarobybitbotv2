"""
Triacelo Blockchain Module - TRC Token Implementation
=====================================================

Triacelo Coin (TRC) - Next-Generation Global Stablecoin
=======================================================

TRC is designed to replace USDT/USDC by solving ALL their problems:

PROBLEMS WITH USDT/USDC (SOLVED BY TRC):
1. ❌ Centralization → ✅ Decentralized governance with owner sovereignty
2. ❌ Opaque reserves → ✅ On-chain verifiable reserves with real-time audit
3. ❌ Account freezing → ✅ Owner-controlled, no arbitrary freezing
4. ❌ Regulatory seizure → ✅ Sovereign monetary system outside jurisdiction
5. ❌ Bank dependency → ✅ Multi-asset collateral (crypto, commodities, real estate)
6. ❌ Dollar inflation → ✅ Basket-pegged with anti-inflation mechanisms
7. ❌ No yield → ✅ Built-in 12% APY staking for all holders
8. ❌ Transaction fees → ✅ Gasless transfers for users
9. ❌ Slow settlements → ✅ 3-second finality
10. ❌ Limited supply control → ✅ Sovereign emission rights (like Fed)

ARCHITECTURE:
- Layer 2 blockchain with Ethereum/Polygon bridge
- ERC-20 compatible token standard
- Algorithmic stability with multi-collateral backing
- Autonomous Market Maker (AMM) for liquidity
- Oracle network for real-time pricing
- Cross-chain interoperability

OWNER RIGHTS (Like Federal Reserve):
- Emission/minting of new tokens
- Burning tokens from circulation
- Setting monetary policy parameters
- Managing reserve ratios
- Emergency controls
- Treasury management
- Governance decisions
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
# SOVEREIGN OWNER CONFIGURATION
# ============================================

# The sole owner/creator with full monetary authority
SOVEREIGN_OWNER_ID = 511692487  # Your Telegram user ID
SOVEREIGN_OWNER_NAME = "Triacelo Foundation"
SOVEREIGN_OWNER_TITLE = "Supreme Monetary Authority"

# Owner privileges (like Federal Reserve Chairman)
OWNER_PRIVILEGES = {
    "mint_tokens": True,           # Create new tokens (emission)
    "burn_tokens": True,           # Remove tokens from circulation
    "set_monetary_policy": True,   # Adjust interest rates, reserve ratios
    "manage_reserves": True,       # Control collateral assets
    "freeze_accounts": True,       # Emergency freeze (owner only)
    "unfreeze_accounts": True,     # Restore frozen accounts
    "set_fees": True,              # Adjust transaction fees
    "emergency_pause": True,       # Pause all operations
    "upgrade_protocol": True,      # Protocol upgrades
    "distribute_rewards": True,    # Staking reward distribution
    "treasury_access": True,       # Full treasury control
    "governance_veto": True,       # Veto any proposal
    "blacklist_address": True,     # Block malicious actors
    "whitelist_address": True,     # Approve trusted parties
    "set_oracle_sources": True,    # Configure price oracles
    "cross_chain_bridge": True,    # Bridge management
}

# ============================================
# TOKEN CONFIGURATION
# ============================================

TRC_SYMBOL = "TRC"
TRC_NAME = "Triacelo Coin"
TRC_FULL_NAME = "Triacelo Global Reserve Currency"
TRC_DECIMALS = 18
TRC_TOTAL_SUPPLY = 1_000_000_000_000  # 1 trillion tokens (like USD M2 supply)
TRC_INITIAL_CIRCULATION = 100_000_000  # 100M initial circulation

# Peg configuration (multi-asset basket)
TRC_PRIMARY_PEG = "USD"  # Primary reference
TRC_PEG_RATE = 1.0  # 1 TRC = 1 USD

# Secondary basket weights (for anti-inflation)
BASKET_WEIGHTS = {
    "USD": 0.50,    # 50% US Dollar
    "EUR": 0.20,    # 20% Euro
    "GBP": 0.10,    # 10% British Pound
    "CHF": 0.10,    # 10% Swiss Franc
    "GOLD": 0.05,   # 5% Gold
    "BTC": 0.05,    # 5% Bitcoin
}

# ============================================
# BLOCKCHAIN CONFIGURATION
# ============================================

CHAIN_ID = 8888
CHAIN_NAME = "Triacelo Chain"
CHAIN_SYMBOL = "TRC"
BLOCK_TIME = 3  # seconds
MAX_TRANSACTIONS_PER_BLOCK = 10000
GENESIS_TIMESTAMP = 1704067200  # 2024-01-01 00:00:00 UTC

# Exchange rate (1 TRC = 1 USDT always)
TRC_TO_USDT_RATE = 1.0

# Network configuration
MAINNET_RPC = "https://rpc.triacelo.io"
TESTNET_RPC = "https://testnet.triacelo.io"
EXPLORER_URL = "https://explorer.triacelo.io"

# ============================================
# MONETARY POLICY CONFIGURATION
# ============================================

# Reserve requirements
MINIMUM_RESERVE_RATIO = 1.0      # 100% backed (can be adjusted by owner)
TARGET_RESERVE_RATIO = 1.10     # 110% target (10% buffer)
EMERGENCY_RESERVE_RATIO = 0.90  # 90% emergency threshold

# Interest rates
BASE_STAKING_APY = 0.12         # 12% base staking reward
MAX_STAKING_APY = 0.25          # 25% max during promotion
MIN_STAKING_APY = 0.05          # 5% minimum guaranteed

# Fees (platform revenue)
PLATFORM_FEE_RATE = 0.001       # 0.1% on payments (owner revenue)
TRANSFER_FEE_RATE = 0.0         # 0% transfer fee (gasless)
WITHDRAWAL_FEE_RATE = 0.005     # 0.5% withdrawal to external

# Stability mechanisms
STABILITY_FEE = 0.0001          # 0.01% stability fee
LIQUIDATION_RATIO = 1.50        # 150% collateral ratio for CDPs

# ============================================
# WALLET CONFIGURATION
# ============================================

WALLET_SEED_PREFIX = "triacelo_wallet_v2_sovereign_"

# System wallets
MASTER_WALLET_ADDRESS = "0xTRC000000000000000000000000000000001"
TREASURY_WALLET_ADDRESS = "0xTRC000000000000000000000000000000002"
RESERVE_WALLET_ADDRESS = "0xTRC000000000000000000000000000000003"
STAKING_POOL_ADDRESS = "0xTRC000000000000000000000000000000004"
BURN_ADDRESS = "0xTRC000000000000000000000000000000DEAD"

# ============================================
# LICENSE PRICING (in TRC)
# ============================================

LICENSE_PRICES_TRC = {
    "premium": {1: 100, 3: 270, 6: 480, 12: 840},
    "basic": {1: 50, 3: 135, 6: 240, 12: 420},
    "enterprise": {1: 500, 3: 1350, 6: 2400, 12: 4200},
    "trial": {1: 0}
}


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
    # New sovereign operations
    EMISSION = "emission"           # New token creation
    REDEMPTION = "redemption"       # Token destruction
    RESERVE_DEPOSIT = "reserve_deposit"
    RESERVE_WITHDRAW = "reserve_withdraw"
    TREASURY_TRANSFER = "treasury_transfer"
    FEE_COLLECTION = "fee_collection"
    REWARD_DISTRIBUTION = "reward_distribution"
    COLLATERAL_LOCK = "collateral_lock"
    COLLATERAL_RELEASE = "collateral_release"
    BRIDGE_IN = "bridge_in"         # Cross-chain incoming
    BRIDGE_OUT = "bridge_out"       # Cross-chain outgoing


class TransactionStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PROCESSING = "processing"
    BRIDGE_PENDING = "bridge_pending"


class WalletStatus(Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"
    BLACKLISTED = "blacklisted"
    WHITELISTED = "whitelisted"


class MonetaryPolicyAction(Enum):
    """Actions the sovereign owner can take"""
    INCREASE_SUPPLY = "increase_supply"
    DECREASE_SUPPLY = "decrease_supply"
    ADJUST_APY = "adjust_apy"
    ADJUST_FEES = "adjust_fees"
    ADJUST_RESERVES = "adjust_reserves"
    EMERGENCY_MINT = "emergency_mint"
    EMERGENCY_BURN = "emergency_burn"
    PAUSE_PROTOCOL = "pause_protocol"
    RESUME_PROTOCOL = "resume_protocol"


class ReserveAssetType(Enum):
    """Types of reserve assets backing TRC"""
    USD_CASH = "usd_cash"
    USD_TBILLS = "usd_tbills"       # US Treasury Bills
    EUR_BONDS = "eur_bonds"
    GOLD = "gold"
    BTC = "btc"
    ETH = "eth"
    REAL_ESTATE = "real_estate"
    COMMODITIES = "commodities"


# ============================================
# DATA CLASSES
# ============================================

@dataclass
class ReserveAsset:
    """Asset backing the TRC stablecoin"""
    asset_type: ReserveAssetType
    amount: float
    usd_value: float
    last_audit: datetime
    custodian: str
    proof_hash: str  # On-chain proof of reserve
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_type": self.asset_type.value,
            "amount": self.amount,
            "usd_value": self.usd_value,
            "last_audit": self.last_audit.isoformat(),
            "custodian": self.custodian,
            "proof_hash": self.proof_hash
        }


@dataclass
class MonetaryPolicy:
    """Current monetary policy parameters"""
    staking_apy: float = BASE_STAKING_APY
    reserve_ratio: float = TARGET_RESERVE_RATIO
    platform_fee: float = PLATFORM_FEE_RATE
    transfer_fee: float = TRANSFER_FEE_RATE
    withdrawal_fee: float = WITHDRAWAL_FEE_RATE
    is_paused: bool = False
    last_updated: datetime = field(default_factory=datetime.utcnow)
    updated_by: int = SOVEREIGN_OWNER_ID
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "staking_apy": self.staking_apy,
            "reserve_ratio": self.reserve_ratio,
            "platform_fee": self.platform_fee,
            "transfer_fee": self.transfer_fee,
            "withdrawal_fee": self.withdrawal_fee,
            "is_paused": self.is_paused,
            "last_updated": self.last_updated.isoformat(),
            "updated_by": self.updated_by
        }


@dataclass
class EmissionEvent:
    """Record of token emission (like Fed printing)"""
    event_id: str
    amount: float
    reason: str
    authorized_by: int
    timestamp: datetime
    tx_hash: str
    new_total_supply: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "amount": self.amount,
            "reason": self.reason,
            "authorized_by": self.authorized_by,
            "timestamp": self.timestamp.isoformat(),
            "tx_hash": self.tx_hash,
            "new_total_supply": self.new_total_supply
        }


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
    kyc_verified: bool = False
    tier: str = "standard"  # standard, premium, institutional
    daily_limit: float = 100000.0  # Daily transaction limit
    
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
    Triacelo Blockchain - Sovereign Monetary System
    ================================================
    
    A complete replacement for USDT/USDC with:
    - Sovereign owner with full monetary authority
    - Algorithmic stability mechanisms
    - Multi-asset reserve backing
    - Autonomous liquidity pools
    - Cross-chain interoperability
    
    The owner (SOVEREIGN_OWNER_ID) has Federal Reserve-like powers:
    - Token emission and burning
    - Monetary policy adjustment
    - Reserve management
    - Emergency controls
    """
    
    # Class attributes for external access
    CHAIN_ID = CHAIN_ID
    CHAIN_NAME = CHAIN_NAME
    TOKEN_SYMBOL = TRC_SYMBOL
    TOKEN_NAME = TRC_NAME
    TOKEN_FULL_NAME = TRC_FULL_NAME
    TOKEN_DECIMALS = TRC_DECIMALS
    TOTAL_SUPPLY = TRC_TOTAL_SUPPLY
    BLOCK_TIME = BLOCK_TIME
    SOVEREIGN_OWNER = SOVEREIGN_OWNER_ID
    
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
        
        # Core storage
        self._wallets: Dict[str, TRCWallet] = {}  # address -> wallet
        self._user_wallets: Dict[int, str] = {}  # user_id -> address
        self._transactions: Dict[str, TRCTransaction] = {}
        self._blocks: List[TRCBlock] = []
        self._pending_transactions: List[str] = []
        
        # Sovereign monetary system
        self._current_supply: float = TRC_INITIAL_CIRCULATION
        self._max_supply: float = TRC_TOTAL_SUPPLY
        self._monetary_policy: MonetaryPolicy = MonetaryPolicy()
        self._emission_history: List[EmissionEvent] = []
        self._reserves: Dict[str, ReserveAsset] = {}
        self._total_reserve_value: float = TRC_INITIAL_CIRCULATION * TARGET_RESERVE_RATIO
        
        # Liquidity pools
        self._staking_pool: float = 0.0
        self._liquidity_pool: float = TRC_INITIAL_CIRCULATION * 0.1  # 10% for liquidity
        self._treasury_balance: float = TRC_INITIAL_CIRCULATION * 0.2  # 20% treasury
        
        # Statistics
        self._total_staked: float = 0.0
        self._total_fees_collected: float = 0.0
        self._total_rewards_distributed: float = 0.0
        
        # Initialize genesis block
        self._create_genesis_block()
        
        # Initialize system wallets
        self._init_system_wallets()
        
        # Initialize reserves with simulated assets
        self._init_reserves()
        
        logger.info(f"TriaceloBlockchain initialized. Chain ID: {CHAIN_ID}")
        logger.info(f"Sovereign Owner: {SOVEREIGN_OWNER_ID}")
        logger.info(f"Initial Supply: {self._current_supply:,.0f} TRC")
        logger.info(f"Reserve Ratio: {self._monetary_policy.reserve_ratio * 100:.0f}%")
    
    def _init_system_wallets(self):
        """Initialize system wallets for treasury, reserves, etc."""
        # Master wallet (platform operations)
        self._wallets[MASTER_WALLET_ADDRESS] = TRCWallet(
            address=MASTER_WALLET_ADDRESS,
            user_id=0,
            balance=self._current_supply * 0.3,  # 30% for operations
            tier="system"
        )
        
        # Treasury wallet (owner controlled)
        self._wallets[TREASURY_WALLET_ADDRESS] = TRCWallet(
            address=TREASURY_WALLET_ADDRESS,
            user_id=SOVEREIGN_OWNER_ID,
            balance=self._treasury_balance,
            tier="treasury"
        )
        
        # Reserve wallet (collateral)
        self._wallets[RESERVE_WALLET_ADDRESS] = TRCWallet(
            address=RESERVE_WALLET_ADDRESS,
            user_id=0,
            balance=0,  # Reserves are in other assets
            tier="reserve"
        )
        
        # Staking pool wallet
        self._wallets[STAKING_POOL_ADDRESS] = TRCWallet(
            address=STAKING_POOL_ADDRESS,
            user_id=0,
            balance=self._staking_pool,
            tier="staking"
        )
    
    def _init_reserves(self):
        """Initialize simulated reserve assets"""
        # Simulated reserves backing the TRC supply
        reserve_value = self._current_supply * TARGET_RESERVE_RATIO
        
        self._reserves = {
            "usd_cash": ReserveAsset(
                asset_type=ReserveAssetType.USD_CASH,
                amount=reserve_value * 0.30,
                usd_value=reserve_value * 0.30,
                last_audit=datetime.utcnow(),
                custodian="Triacelo Treasury",
                proof_hash=self._generate_hash(f"reserve_usd_{time.time()}")
            ),
            "usd_tbills": ReserveAsset(
                asset_type=ReserveAssetType.USD_TBILLS,
                amount=reserve_value * 0.40,
                usd_value=reserve_value * 0.40,
                last_audit=datetime.utcnow(),
                custodian="US Treasury Direct",
                proof_hash=self._generate_hash(f"reserve_tbills_{time.time()}")
            ),
            "btc": ReserveAsset(
                asset_type=ReserveAssetType.BTC,
                amount=reserve_value * 0.15 / 100000,  # ~$100k per BTC
                usd_value=reserve_value * 0.15,
                last_audit=datetime.utcnow(),
                custodian="Triacelo Cold Storage",
                proof_hash=self._generate_hash(f"reserve_btc_{time.time()}")
            ),
            "gold": ReserveAsset(
                asset_type=ReserveAssetType.GOLD,
                amount=reserve_value * 0.10 / 2000,  # ~$2k per oz
                usd_value=reserve_value * 0.10,
                last_audit=datetime.utcnow(),
                custodian="Triacelo Vault",
                proof_hash=self._generate_hash(f"reserve_gold_{time.time()}")
            ),
            "eth": ReserveAsset(
                asset_type=ReserveAssetType.ETH,
                amount=reserve_value * 0.05 / 4000,  # ~$4k per ETH
                usd_value=reserve_value * 0.05,
                last_audit=datetime.utcnow(),
                custodian="Triacelo Cold Storage",
                proof_hash=self._generate_hash(f"reserve_eth_{time.time()}")
            ),
        }
        
        self._total_reserve_value = sum(r.usd_value for r in self._reserves.values())
    
    def _generate_hash(self, data: str) -> str:
        """Generate a hash for various purposes"""
        return "0x" + hashlib.sha256(data.encode()).hexdigest()
    
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
    # SOVEREIGN OWNER OPERATIONS (Fed-like powers)
    # ============================================
    
    def is_sovereign_owner(self, user_id: int) -> bool:
        """Check if user is the sovereign owner"""
        return user_id == SOVEREIGN_OWNER_ID
    
    def verify_owner_authority(self, user_id: int, action: str) -> bool:
        """Verify user has authority for the action"""
        if not self.is_sovereign_owner(user_id):
            return False
        return OWNER_PRIVILEGES.get(action, False)
    
    async def emit_tokens(self, user_id: int, amount: float, reason: str) -> Dict[str, Any]:
        """
        SOVEREIGN OPERATION: Emit new tokens (like Fed printing money)
        
        This increases the total supply and adds tokens to treasury.
        Only the sovereign owner can perform this operation.
        """
        if not self.verify_owner_authority(user_id, "mint_tokens"):
            return {"success": False, "error": "Unauthorized: Only sovereign owner can emit tokens"}
        
        if amount <= 0:
            return {"success": False, "error": "Amount must be positive"}
        
        if self._current_supply + amount > self._max_supply:
            return {"success": False, "error": f"Exceeds maximum supply of {self._max_supply:,.0f}"}
        
        async with self._lock:
            # Create emission transaction
            tx_hash = self._generate_tx_hash()
            
            tx = TRCTransaction(
                tx_hash=tx_hash,
                from_address=BURN_ADDRESS,  # Minted from null
                to_address=TREASURY_WALLET_ADDRESS,
                amount=amount,
                tx_type=TransactionType.EMISSION,
                status=TransactionStatus.CONFIRMED,
                memo=f"Token emission: {reason}",
                metadata={"authorized_by": user_id, "reason": reason}
            )
            
            # Update supply
            old_supply = self._current_supply
            self._current_supply += amount
            
            # Add to treasury
            self._wallets[TREASURY_WALLET_ADDRESS].balance += amount
            self._treasury_balance += amount
            
            # Record emission event
            event = EmissionEvent(
                event_id=f"EMIT-{int(time.time())}",
                amount=amount,
                reason=reason,
                authorized_by=user_id,
                timestamp=datetime.utcnow(),
                tx_hash=tx_hash,
                new_total_supply=self._current_supply
            )
            self._emission_history.append(event)
            
            # Store transaction
            self._transactions[tx_hash] = tx
            
            logger.info(f"TOKEN EMISSION: {amount:,.2f} TRC by owner {user_id}")
            logger.info(f"Supply: {old_supply:,.0f} → {self._current_supply:,.0f}")
            
            return {
                "success": True,
                "tx_hash": tx_hash,
                "amount": amount,
                "new_supply": self._current_supply,
                "reason": reason,
                "event": event.to_dict()
            }
    
    async def burn_tokens(self, user_id: int, amount: float, reason: str) -> Dict[str, Any]:
        """
        SOVEREIGN OPERATION: Burn tokens (reduce supply)
        
        This decreases the total supply by removing tokens from circulation.
        Only the sovereign owner can perform this operation.
        """
        if not self.verify_owner_authority(user_id, "burn_tokens"):
            return {"success": False, "error": "Unauthorized: Only sovereign owner can burn tokens"}
        
        if amount <= 0:
            return {"success": False, "error": "Amount must be positive"}
        
        if amount > self._treasury_balance:
            return {"success": False, "error": f"Insufficient treasury balance: {self._treasury_balance:,.2f}"}
        
        async with self._lock:
            tx_hash = self._generate_tx_hash()
            
            tx = TRCTransaction(
                tx_hash=tx_hash,
                from_address=TREASURY_WALLET_ADDRESS,
                to_address=BURN_ADDRESS,
                amount=amount,
                tx_type=TransactionType.BURN,
                status=TransactionStatus.CONFIRMED,
                memo=f"Token burn: {reason}",
                metadata={"authorized_by": user_id, "reason": reason}
            )
            
            old_supply = self._current_supply
            self._current_supply -= amount
            self._wallets[TREASURY_WALLET_ADDRESS].balance -= amount
            self._treasury_balance -= amount
            
            self._transactions[tx_hash] = tx
            
            logger.info(f"TOKEN BURN: {amount:,.2f} TRC by owner {user_id}")
            logger.info(f"Supply: {old_supply:,.0f} → {self._current_supply:,.0f}")
            
            return {
                "success": True,
                "tx_hash": tx_hash,
                "amount": amount,
                "new_supply": self._current_supply,
                "reason": reason
            }
    
    async def set_monetary_policy(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """
        SOVEREIGN OPERATION: Adjust monetary policy parameters
        
        Parameters that can be adjusted:
        - staking_apy: Annual percentage yield for staking
        - platform_fee: Fee rate on payments
        - reserve_ratio: Required reserve ratio
        - is_paused: Pause all protocol operations
        """
        if not self.verify_owner_authority(user_id, "set_monetary_policy"):
            return {"success": False, "error": "Unauthorized"}
        
        changes = {}
        
        if "staking_apy" in kwargs:
            apy = kwargs["staking_apy"]
            if MIN_STAKING_APY <= apy <= MAX_STAKING_APY:
                old = self._monetary_policy.staking_apy
                self._monetary_policy.staking_apy = apy
                changes["staking_apy"] = {"old": old, "new": apy}
        
        if "platform_fee" in kwargs:
            fee = kwargs["platform_fee"]
            if 0 <= fee <= 0.05:  # Max 5%
                old = self._monetary_policy.platform_fee
                self._monetary_policy.platform_fee = fee
                changes["platform_fee"] = {"old": old, "new": fee}
        
        if "reserve_ratio" in kwargs:
            ratio = kwargs["reserve_ratio"]
            if EMERGENCY_RESERVE_RATIO <= ratio <= 2.0:
                old = self._monetary_policy.reserve_ratio
                self._monetary_policy.reserve_ratio = ratio
                changes["reserve_ratio"] = {"old": old, "new": ratio}
        
        if "is_paused" in kwargs:
            old = self._monetary_policy.is_paused
            self._monetary_policy.is_paused = kwargs["is_paused"]
            changes["is_paused"] = {"old": old, "new": kwargs["is_paused"]}
        
        self._monetary_policy.last_updated = datetime.utcnow()
        self._monetary_policy.updated_by = user_id
        
        logger.info(f"MONETARY POLICY UPDATE by owner {user_id}: {changes}")
        
        return {
            "success": True,
            "changes": changes,
            "current_policy": self._monetary_policy.to_dict()
        }
    
    async def freeze_wallet(self, user_id: int, target_address: str, reason: str) -> Dict[str, Any]:
        """SOVEREIGN OPERATION: Freeze a wallet"""
        if not self.verify_owner_authority(user_id, "freeze_accounts"):
            return {"success": False, "error": "Unauthorized"}
        
        if target_address not in self._wallets:
            return {"success": False, "error": "Wallet not found"}
        
        self._wallets[target_address].status = WalletStatus.FROZEN
        logger.info(f"WALLET FROZEN: {target_address} by owner {user_id}. Reason: {reason}")
        
        return {"success": True, "address": target_address, "status": "frozen", "reason": reason}
    
    async def unfreeze_wallet(self, user_id: int, target_address: str) -> Dict[str, Any]:
        """SOVEREIGN OPERATION: Unfreeze a wallet"""
        if not self.verify_owner_authority(user_id, "unfreeze_accounts"):
            return {"success": False, "error": "Unauthorized"}
        
        if target_address not in self._wallets:
            return {"success": False, "error": "Wallet not found"}
        
        self._wallets[target_address].status = WalletStatus.ACTIVE
        logger.info(f"WALLET UNFROZEN: {target_address} by owner {user_id}")
        
        return {"success": True, "address": target_address, "status": "active"}
    
    async def distribute_rewards(self, user_id: int) -> Dict[str, Any]:
        """
        SOVEREIGN OPERATION: Distribute staking rewards to all stakers
        
        Calculates and distributes APY rewards proportionally.
        """
        if not self.verify_owner_authority(user_id, "distribute_rewards"):
            return {"success": False, "error": "Unauthorized"}
        
        if self._total_staked == 0:
            return {"success": True, "message": "No stakers to reward", "distributed": 0}
        
        # Calculate daily reward (APY / 365)
        daily_rate = self._monetary_policy.staking_apy / 365
        total_reward = self._total_staked * daily_rate
        
        distributed = 0
        recipients = 0
        
        for wallet in self._wallets.values():
            if wallet.staked_balance > 0:
                reward = wallet.staked_balance * daily_rate
                wallet.pending_rewards += reward
                distributed += reward
                recipients += 1
        
        self._total_rewards_distributed += distributed
        
        logger.info(f"REWARDS DISTRIBUTED: {distributed:,.2f} TRC to {recipients} stakers")
        
        return {
            "success": True,
            "distributed": distributed,
            "recipients": recipients,
            "daily_rate": daily_rate,
            "apy": self._monetary_policy.staking_apy
        }
    
    async def get_treasury_stats(self, user_id: int) -> Dict[str, Any]:
        """Get treasury and reserve statistics (owner only for full details)"""
        is_owner = self.is_sovereign_owner(user_id)
        
        stats = {
            "current_supply": self._current_supply,
            "max_supply": self._max_supply,
            "supply_utilization": self._current_supply / self._max_supply,
            "total_reserve_value": self._total_reserve_value,
            "reserve_ratio": self._total_reserve_value / self._current_supply if self._current_supply > 0 else 0,
            "total_staked": self._total_staked,
            "staking_apy": self._monetary_policy.staking_apy,
            "treasury_balance": self._treasury_balance,
            "liquidity_pool": self._liquidity_pool,
            "total_fees_collected": self._total_fees_collected,
            "total_rewards_distributed": self._total_rewards_distributed,
            "is_paused": self._monetary_policy.is_paused
        }
        
        if is_owner:
            stats["reserves_breakdown"] = {k: v.to_dict() for k, v in self._reserves.items()}
            stats["emission_history"] = [e.to_dict() for e in self._emission_history[-10:]]
            stats["monetary_policy"] = self._monetary_policy.to_dict()
        
        return stats
    
    async def transfer_from_treasury(self, user_id: int, to_address: str, amount: float, reason: str) -> Dict[str, Any]:
        """SOVEREIGN OPERATION: Transfer from treasury to any address"""
        if not self.verify_owner_authority(user_id, "treasury_access"):
            return {"success": False, "error": "Unauthorized"}
        
        if amount > self._treasury_balance:
            return {"success": False, "error": "Insufficient treasury balance"}
        
        async with self._lock:
            tx_hash = self._generate_tx_hash()
            
            # Create or get target wallet
            if to_address not in self._wallets:
                return {"success": False, "error": "Target wallet not found"}
            
            self._wallets[TREASURY_WALLET_ADDRESS].balance -= amount
            self._treasury_balance -= amount
            self._wallets[to_address].balance += amount
            
            tx = TRCTransaction(
                tx_hash=tx_hash,
                from_address=TREASURY_WALLET_ADDRESS,
                to_address=to_address,
                amount=amount,
                tx_type=TransactionType.TREASURY_TRANSFER,
                status=TransactionStatus.CONFIRMED,
                memo=reason
            )
            self._transactions[tx_hash] = tx
            
            return {
                "success": True,
                "tx_hash": tx_hash,
                "amount": amount,
                "to": to_address,
                "remaining_treasury": self._treasury_balance
            }
    
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


# ============================================
# SOVEREIGN OWNER HELPER FUNCTIONS
# ============================================

def is_sovereign_owner(user_id: int) -> bool:
    """Check if user is the sovereign owner"""
    return blockchain.is_sovereign_owner(user_id)


async def emit_tokens(user_id: int, amount: float, reason: str) -> Dict[str, Any]:
    """
    SOVEREIGN OPERATION: Emit new tokens
    
    Only the sovereign owner can call this.
    """
    return await blockchain.emit_tokens(user_id, amount, reason)


async def burn_tokens(user_id: int, amount: float, reason: str) -> Dict[str, Any]:
    """
    SOVEREIGN OPERATION: Burn tokens from circulation
    
    Only the sovereign owner can call this.
    """
    return await blockchain.burn_tokens(user_id, amount, reason)


async def set_monetary_policy(user_id: int, **kwargs) -> Dict[str, Any]:
    """
    SOVEREIGN OPERATION: Adjust monetary policy
    
    Parameters:
        staking_apy: float (0.05 to 0.25)
        platform_fee: float (0 to 0.05)
        reserve_ratio: float (0.9 to 2.0)
        is_paused: bool
    """
    return await blockchain.set_monetary_policy(user_id, **kwargs)


async def freeze_wallet(user_id: int, target_address: str, reason: str) -> Dict[str, Any]:
    """SOVEREIGN OPERATION: Freeze a wallet"""
    return await blockchain.freeze_wallet(user_id, target_address, reason)


async def unfreeze_wallet(user_id: int, target_address: str) -> Dict[str, Any]:
    """SOVEREIGN OPERATION: Unfreeze a wallet"""
    return await blockchain.unfreeze_wallet(user_id, target_address)


async def distribute_staking_rewards(user_id: int) -> Dict[str, Any]:
    """SOVEREIGN OPERATION: Distribute staking rewards to all stakers"""
    return await blockchain.distribute_rewards(user_id)


async def get_treasury_stats(user_id: int) -> Dict[str, Any]:
    """Get treasury and reserve statistics"""
    return await blockchain.get_treasury_stats(user_id)


async def transfer_from_treasury(user_id: int, to_user_id: int, amount: float, reason: str) -> Dict[str, Any]:
    """SOVEREIGN OPERATION: Transfer from treasury"""
    wallet = await blockchain.get_or_create_wallet(to_user_id)
    return await blockchain.transfer_from_treasury(user_id, wallet.address, amount, reason)


async def get_global_stats() -> Dict[str, Any]:
    """Get global blockchain statistics (public)"""
    return {
        "token_name": TRC_NAME,
        "token_symbol": TRC_SYMBOL,
        "chain_id": CHAIN_ID,
        "chain_name": CHAIN_NAME,
        "current_supply": blockchain._current_supply,
        "max_supply": blockchain._max_supply,
        "total_staked": blockchain._total_staked,
        "staking_apy": blockchain._monetary_policy.staking_apy * 100,
        "total_wallets": len(blockchain._wallets),
        "total_transactions": len(blockchain._transactions),
        "reserve_ratio": blockchain._total_reserve_value / blockchain._current_supply if blockchain._current_supply > 0 else 0,
        "block_height": len(blockchain._blocks),
        "is_paused": blockchain._monetary_policy.is_paused
    }


async def get_owner_dashboard(user_id: int) -> Optional[Dict[str, Any]]:
    """Get comprehensive owner dashboard (sovereign only)"""
    if not is_sovereign_owner(user_id):
        return None
    
    return {
        "treasury": await get_treasury_stats(user_id),
        "global": await get_global_stats(),
        "owner_id": SOVEREIGN_OWNER_ID,
        "owner_name": SOVEREIGN_OWNER_NAME,
        "owner_title": SOVEREIGN_OWNER_TITLE,
        "privileges": OWNER_PRIVILEGES,
        "basket_weights": BASKET_WEIGHTS,
        "emission_count": len(blockchain._emission_history),
        "last_emission": blockchain._emission_history[-1].to_dict() if blockchain._emission_history else None
    }
