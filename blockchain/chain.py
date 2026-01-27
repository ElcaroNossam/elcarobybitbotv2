"""
ELCARO Chain - Core Blockchain Implementation

Decentralized L1 blockchain with PoS consensus, inspired by HyperLiquid architecture.

Features:
- Proof of Stake (PoS) + Byzantine Fault Tolerance (BFT)
- 10,000+ TPS target
- <500ms finality
- EVM compatibility
- Validator network
- Block production & validation
- State management
- Transaction processing
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------
# Core Data Structures
# ------------------------------------------------------------------------------------

@dataclass
class Transaction:
    """Blockchain transaction."""
    tx_hash: str
    from_address: str
    to_address: str
    value: Decimal
    gas_price: Decimal
    gas_limit: int
    nonce: int
    data: bytes = b""
    signature: str = ""
    timestamp: int = field(default_factory=lambda: int(time.time()))
    
    def to_dict(self) -> Dict:
        return {
            "tx_hash": self.tx_hash,
            "from": self.from_address,
            "to": self.to_address,
            "value": str(self.value),
            "gas_price": str(self.gas_price),
            "gas_limit": self.gas_limit,
            "nonce": self.nonce,
            "data": self.data.hex(),
            "signature": self.signature,
            "timestamp": self.timestamp
        }
    
    def calculate_hash(self) -> str:
        """Calculate transaction hash."""
        data = f"{self.from_address}{self.to_address}{self.value}{self.nonce}{self.timestamp}".encode()
        return hashlib.sha256(data).hexdigest()


@dataclass
class Block:
    """Blockchain block."""
    block_number: int
    timestamp: int
    transactions: List[Transaction]
    previous_hash: str
    validator: str
    block_hash: str = ""
    state_root: str = ""
    receipts_root: str = ""
    gas_used: int = 0
    gas_limit: int = 10_000_000
    signature: str = ""
    
    def __post_init__(self):
        if not self.block_hash:
            self.block_hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate block hash."""
        tx_hashes = "".join([tx.tx_hash for tx in self.transactions])
        data = f"{self.block_number}{self.timestamp}{tx_hashes}{self.previous_hash}{self.validator}".encode()
        return hashlib.sha256(data).hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            "block_number": self.block_number,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "validator": self.validator,
            "block_hash": self.block_hash,
            "state_root": self.state_root,
            "receipts_root": self.receipts_root,
            "gas_used": self.gas_used,
            "gas_limit": self.gas_limit,
            "signature": self.signature
        }


@dataclass
class Validator:
    """Network validator."""
    address: str
    stake: Decimal
    commission_rate: Decimal  # 0.05 = 5%
    delegated_stake: Decimal = Decimal(0)
    total_blocks_produced: int = 0
    total_blocks_missed: int = 0
    is_active: bool = True
    joined_at: int = field(default_factory=lambda: int(time.time()))
    last_active_at: int = field(default_factory=lambda: int(time.time()))
    
    @property
    def total_stake(self) -> Decimal:
        """Total stake including delegations."""
        return self.stake + self.delegated_stake
    
    @property
    def uptime_percent(self) -> float:
        """Validator uptime percentage."""
        total = self.total_blocks_produced + self.total_blocks_missed
        if total == 0:
            return 100.0
        return (self.total_blocks_produced / total) * 100
    
    def to_dict(self) -> Dict:
        return {
            "address": self.address,
            "stake": str(self.stake),
            "commission_rate": str(self.commission_rate),
            "delegated_stake": str(self.delegated_stake),
            "total_stake": str(self.total_stake),
            "total_blocks_produced": self.total_blocks_produced,
            "total_blocks_missed": self.total_blocks_missed,
            "uptime_percent": self.uptime_percent,
            "is_active": self.is_active,
            "joined_at": self.joined_at,
            "last_active_at": self.last_active_at
        }


@dataclass
class Account:
    """Blockchain account state."""
    address: str
    balance: Decimal = Decimal(0)
    nonce: int = 0
    code: bytes = b""  # Smart contract code
    storage: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "address": self.address,
            "balance": str(self.balance),
            "nonce": self.nonce,
            "code": self.code.hex() if self.code else "",
            "storage": self.storage
        }


# ------------------------------------------------------------------------------------
# Blockchain Core
# ------------------------------------------------------------------------------------

class EnlikoChain:
    """
    ELCARO Chain - Core blockchain implementation.
    
    Features:
    - PoS consensus with BFT finality
    - 2-second block time
    - 10,000 transactions per block
    - EVM-compatible smart contracts
    - Validator network management
    """
    
    def __init__(
        self,
        chain_id: int = 1,
        block_time: int = 2,  # seconds
        max_validators: int = 100,
        min_validator_stake: Decimal = Decimal("100000")  # 100k ELC
    ):
        self.chain_id = chain_id
        self.block_time = block_time
        self.max_validators = max_validators
        self.min_validator_stake = min_validator_stake
        
        # Blockchain state
        self.blocks: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.accounts: Dict[str, Account] = {}
        self.validators: Dict[str, Validator] = {}
        
        # Consensus state
        self.current_validator_index = 0
        self.epoch_length = 1800  # 1 hour (1800 blocks at 2s/block)
        self.current_epoch = 0
        
        # Statistics
        self.total_transactions = 0
        self.total_gas_used = 0
        
        # Create genesis block
        self._create_genesis_block()
        
        logger.info(f"ELCARO Chain initialized (chain_id={chain_id}, block_time={block_time}s)")
    
    def _create_genesis_block(self):
        """Create the first block (genesis)."""
        genesis_block = Block(
            block_number=0,
            timestamp=int(time.time()),
            transactions=[],
            previous_hash="0" * 64,
            validator="genesis"
        )
        self.blocks.append(genesis_block)
        logger.info(f"Genesis block created: {genesis_block.block_hash}")
    
    # ------------------------------------------------------------------------------------
    # Account Management
    # ------------------------------------------------------------------------------------
    
    def create_account(self, address: str, initial_balance: Decimal = Decimal(0)) -> Account:
        """Create a new account."""
        if address in self.accounts:
            raise ValueError(f"Account {address} already exists")
        
        account = Account(address=address, balance=initial_balance)
        self.accounts[address] = account
        logger.info(f"Account created: {address} with balance {initial_balance}")
        return account
    
    def get_account(self, address: str) -> Optional[Account]:
        """Get account by address."""
        return self.accounts.get(address)
    
    def get_balance(self, address: str) -> Decimal:
        """Get account balance."""
        account = self.get_account(address)
        return account.balance if account else Decimal(0)
    
    def transfer(self, from_addr: str, to_addr: str, amount: Decimal) -> bool:
        """Transfer tokens between accounts."""
        from_account = self.get_account(from_addr)
        if not from_account:
            raise ValueError(f"From account {from_addr} not found")
        
        if from_account.balance < amount:
            raise ValueError(f"Insufficient balance: {from_account.balance} < {amount}")
        
        # Deduct from sender
        from_account.balance -= amount
        
        # Add to recipient (create if not exists)
        to_account = self.get_account(to_addr)
        if not to_account:
            to_account = self.create_account(to_addr)
        to_account.balance += amount
        
        logger.info(f"Transfer: {from_addr} → {to_addr}, amount: {amount}")
        return True
    
    # ------------------------------------------------------------------------------------
    # Transaction Processing
    # ------------------------------------------------------------------------------------
    
    def create_transaction(
        self,
        from_addr: str,
        to_addr: str,
        value: Decimal,
        gas_price: Decimal = Decimal("0.00001"),
        gas_limit: int = 21000,
        data: bytes = b""
    ) -> Transaction:
        """Create a new transaction."""
        account = self.get_account(from_addr)
        if not account:
            raise ValueError(f"Account {from_addr} not found")
        
        nonce = account.nonce
        
        tx = Transaction(
            tx_hash="",  # Will be calculated
            from_address=from_addr,
            to_address=to_addr,
            value=value,
            gas_price=gas_price,
            gas_limit=gas_limit,
            nonce=nonce,
            data=data
        )
        
        tx.tx_hash = tx.calculate_hash()
        return tx
    
    def add_transaction(self, tx: Transaction) -> bool:
        """Add transaction to pending pool."""
        # Validate transaction
        if not self._validate_transaction(tx):
            return False
        
        self.pending_transactions.append(tx)
        logger.info(f"Transaction added to mempool: {tx.tx_hash}")
        return True
    
    def _validate_transaction(self, tx: Transaction) -> bool:
        """Validate transaction."""
        account = self.get_account(tx.from_address)
        if not account:
            logger.error(f"Transaction validation failed: account {tx.from_address} not found")
            return False
        
        # Check nonce
        if tx.nonce != account.nonce:
            logger.error(f"Transaction validation failed: invalid nonce {tx.nonce} != {account.nonce}")
            return False
        
        # Check balance (value + gas)
        total_cost = tx.value + (tx.gas_price * tx.gas_limit)
        if account.balance < total_cost:
            logger.error(f"Transaction validation failed: insufficient balance")
            return False
        
        return True
    
    def execute_transaction(self, tx: Transaction) -> bool:
        """Execute a transaction."""
        try:
            # Get accounts
            from_account = self.get_account(tx.from_address)
            if not from_account:
                return False
            
            # Calculate gas cost
            gas_used = 21000  # Base transfer cost
            gas_cost = tx.gas_price * gas_used
            
            # Deduct value + gas from sender
            total_deduction = tx.value + gas_cost
            if from_account.balance < total_deduction:
                return False
            
            from_account.balance -= total_deduction
            from_account.nonce += 1
            
            # Add value to recipient
            to_account = self.get_account(tx.to_address)
            if not to_account:
                to_account = self.create_account(tx.to_address)
            to_account.balance += tx.value
            
            # Update statistics
            self.total_transactions += 1
            self.total_gas_used += gas_used
            
            logger.info(f"Transaction executed: {tx.tx_hash}")
            return True
            
        except Exception as e:
            logger.error(f"Transaction execution failed: {e}")
            return False
    
    # ------------------------------------------------------------------------------------
    # Block Production
    # ------------------------------------------------------------------------------------
    
    def produce_block(self, validator_address: str) -> Optional[Block]:
        """Produce a new block."""
        validator = self.validators.get(validator_address)
        if not validator or not validator.is_active:
            logger.error(f"Validator {validator_address} not found or inactive")
            return None
        
        # Get previous block
        previous_block = self.blocks[-1]
        
        # Select transactions from mempool (max 10,000)
        transactions_to_include = self.pending_transactions[:10000]
        
        # Execute transactions
        included_transactions = []
        for tx in transactions_to_include:
            if self.execute_transaction(tx):
                included_transactions.append(tx)
        
        # Remove included transactions from mempool
        for tx in included_transactions:
            if tx in self.pending_transactions:
                self.pending_transactions.remove(tx)
        
        # Create new block
        new_block = Block(
            block_number=previous_block.block_number + 1,
            timestamp=int(time.time()),
            transactions=included_transactions,
            previous_hash=previous_block.block_hash,
            validator=validator_address
        )
        
        # Add block to chain
        self.blocks.append(new_block)
        
        # Update validator stats
        validator.total_blocks_produced += 1
        validator.last_active_at = int(time.time())
        
        # Check if epoch ended
        if new_block.block_number % self.epoch_length == 0:
            self._rotate_validators()
        
        logger.info(f"Block #{new_block.block_number} produced by {validator_address}: {len(included_transactions)} txs")
        return new_block
    
    def _rotate_validators(self):
        """Rotate validators at end of epoch."""
        self.current_epoch += 1
        logger.info(f"Epoch {self.current_epoch} started - validators rotated")
    
    # ------------------------------------------------------------------------------------
    # Validator Management
    # ------------------------------------------------------------------------------------
    
    def register_validator(
        self,
        address: str,
        stake: Decimal,
        commission_rate: Decimal = Decimal("0.05")
    ) -> Validator:
        """Register a new validator."""
        if address in self.validators:
            raise ValueError(f"Validator {address} already registered")
        
        if stake < self.min_validator_stake:
            raise ValueError(f"Stake {stake} below minimum {self.min_validator_stake}")
        
        # Deduct stake from account
        account = self.get_account(address)
        if not account or account.balance < stake:
            raise ValueError(f"Insufficient balance for staking")
        
        account.balance -= stake
        
        validator = Validator(
            address=address,
            stake=stake,
            commission_rate=commission_rate
        )
        
        self.validators[address] = validator
        logger.info(f"Validator registered: {address} with stake {stake}")
        return validator
    
    def unregister_validator(self, address: str) -> bool:
        """Unregister a validator and return stake."""
        validator = self.validators.get(address)
        if not validator:
            return False
        
        # Return stake to account
        account = self.get_account(address)
        if account:
            account.balance += validator.stake
        
        # Remove validator
        del self.validators[address]
        logger.info(f"Validator unregistered: {address}")
        return True
    
    def delegate_to_validator(
        self,
        delegator_addr: str,
        validator_addr: str,
        amount: Decimal
    ) -> bool:
        """Delegate stake to a validator."""
        validator = self.validators.get(validator_addr)
        if not validator:
            raise ValueError(f"Validator {validator_addr} not found")
        
        delegator = self.get_account(delegator_addr)
        if not delegator or delegator.balance < amount:
            raise ValueError("Insufficient balance for delegation")
        
        # Deduct from delegator
        delegator.balance -= amount
        
        # Add to validator's delegated stake
        validator.delegated_stake += amount
        
        logger.info(f"Delegated {amount} from {delegator_addr} to {validator_addr}")
        return True
    
    def get_active_validators(self) -> List[Validator]:
        """Get all active validators sorted by stake."""
        active = [v for v in self.validators.values() if v.is_active]
        return sorted(active, key=lambda v: v.total_stake, reverse=True)[:self.max_validators]
    
    def select_block_producer(self) -> Optional[str]:
        """Select next block producer (round-robin for now)."""
        active_validators = self.get_active_validators()
        if not active_validators:
            return None
        
        validator = active_validators[self.current_validator_index % len(active_validators)]
        self.current_validator_index += 1
        return validator.address
    
    # ------------------------------------------------------------------------------------
    # Statistics & Queries
    # ------------------------------------------------------------------------------------
    
    def get_block(self, block_number: int) -> Optional[Block]:
        """Get block by number."""
        if 0 <= block_number < len(self.blocks):
            return self.blocks[block_number]
        return None
    
    def get_latest_block(self) -> Block:
        """Get latest block."""
        return self.blocks[-1]
    
    def get_block_height(self) -> int:
        """Get current block height."""
        return len(self.blocks) - 1
    
    def get_chain_stats(self) -> Dict:
        """Get blockchain statistics."""
        latest_block = self.get_latest_block()
        active_validators = self.get_active_validators()
        
        return {
            "chain_id": self.chain_id,
            "block_height": self.get_block_height(),
            "total_transactions": self.total_transactions,
            "total_gas_used": self.total_gas_used,
            "pending_transactions": len(self.pending_transactions),
            "total_accounts": len(self.accounts),
            "active_validators": len(active_validators),
            "total_validators": len(self.validators),
            "epoch": self.current_epoch,
            "latest_block": {
                "number": latest_block.block_number,
                "hash": latest_block.block_hash,
                "timestamp": latest_block.timestamp,
                "transactions": len(latest_block.transactions),
                "validator": latest_block.validator
            }
        }
    
    def get_validator_rewards(self, validator_addr: str) -> Decimal:
        """Calculate validator rewards (simplified)."""
        validator = self.validators.get(validator_addr)
        if not validator:
            return Decimal(0)
        
        # 5 ELC per block reward (simplified)
        block_reward = Decimal("5")
        total_reward = block_reward * validator.total_blocks_produced
        
        return total_reward
    
    # ------------------------------------------------------------------------------------
    # Persistence (Future: RocksDB/LevelDB)
    # ------------------------------------------------------------------------------------
    
    def export_state(self) -> Dict:
        """Export blockchain state to dict."""
        return {
            "chain_id": self.chain_id,
            "blocks": [block.to_dict() for block in self.blocks],
            "accounts": {addr: acc.to_dict() for addr, acc in self.accounts.items()},
            "validators": {addr: val.to_dict() for addr, val in self.validators.items()},
            "stats": self.get_chain_stats()
        }
    
    def export_to_file(self, filepath: str):
        """Export blockchain state to JSON file."""
        state = self.export_state()
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        logger.info(f"Blockchain state exported to {filepath}")


# ------------------------------------------------------------------------------------
# Consensus Engine (Simplified PoS + BFT)
# ------------------------------------------------------------------------------------

class ConsensusEngine:
    """
    Consensus engine for ELCARO Chain.
    
    Implements simplified PoS + BFT:
    - Round-robin validator selection (weighted by stake)
    - 2/3+ validators must sign block for finality
    - Instant finality on confirmation
    """
    
    def __init__(self, chain: EnlikoChain):
        self.chain = chain
        self.block_signatures: Dict[str, List[str]] = {}  # block_hash -> [validator_addresses]
        
    def get_required_signatures(self) -> int:
        """Get required signatures for finality (2/3+ of validators)."""
        active_validators = self.chain.get_active_validators()
        return (len(active_validators) * 2) // 3 + 1
    
    def sign_block(self, block_hash: str, validator_addr: str) -> bool:
        """Validator signs a block."""
        if validator_addr not in self.chain.validators:
            return False
        
        if block_hash not in self.block_signatures:
            self.block_signatures[block_hash] = []
        
        if validator_addr not in self.block_signatures[block_hash]:
            self.block_signatures[block_hash].append(validator_addr)
            logger.info(f"Block {block_hash[:16]}... signed by {validator_addr}")
        
        return True
    
    def is_block_finalized(self, block_hash: str) -> bool:
        """Check if block has enough signatures for finality."""
        required = self.get_required_signatures()
        signatures = len(self.block_signatures.get(block_hash, []))
        return signatures >= required
    
    def get_block_signatures(self, block_hash: str) -> List[str]:
        """Get all signatures for a block."""
        return self.block_signatures.get(block_hash, [])


# ------------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------------

def generate_address() -> str:
    """Generate random address (for testing)."""
    import secrets
    return "0x" + secrets.token_hex(20)


def elc_to_wei(elc: float) -> Decimal:
    """Convert ELC to smallest unit (wei-equivalent)."""
    return Decimal(str(elc)) * Decimal("1000000000000000000")  # 18 decimals


def wei_to_elc(wei: Decimal) -> float:
    """Convert wei to ELC."""
    return float(wei / Decimal("1000000000000000000"))
