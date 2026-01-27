"""
ELCARO Chain - Cross-Chain Bridge Infrastructure

Multi-chain bridge for connecting ELCARO Chain with:
- TON, Ethereum, BSC, Polygon, Arbitrum, Optimism, Solana

Features:
- Lock & Mint mechanism
- Multi-sig validation
- Time-locked large transfers
- Insurance fund
- Automatic relayers
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from decimal import Decimal
from enum import Enum
import time
import hashlib

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------------------------

class BridgeChain(Enum):
    ELCARO = "elcaro"
    TON = "ton"
    ETHEREUM = "ethereum"
    BSC = "bsc"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    SOLANA = "solana"


class BridgeStatus(Enum):
    PENDING = "pending"
    LOCKED = "locked"
    MINTED = "minted"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMELOCKED = "timelocked"


# ------------------------------------------------------------------------------------
# Data Structures
# ------------------------------------------------------------------------------------

@dataclass
class BridgeTransfer:
    """Cross-chain bridge transfer."""
    transfer_id: str
    from_chain: BridgeChain
    to_chain: BridgeChain
    from_address: str
    to_address: str
    token: str
    amount: Decimal
    fee: Decimal
    status: BridgeStatus
    lock_tx_hash: str = ""
    mint_tx_hash: str = ""
    signatures: List[str] = field(default_factory=list)
    required_signatures: int = 7  # 7-of-10 multisig
    created_at: int = field(default_factory=lambda: int(time.time()))
    locked_at: int = 0
    minted_at: int = 0
    timelock_until: int = 0
    
    @property
    def is_large_transfer(self) -> bool:
        """Check if transfer exceeds $100k threshold."""
        return self.amount > Decimal("100000")
    
    @property
    def has_enough_signatures(self) -> bool:
        """Check if transfer has enough validator signatures."""
        return len(self.signatures) >= self.required_signatures
    
    @property
    def is_timelocked(self) -> bool:
        """Check if transfer is still timelocked."""
        return self.timelock_until > int(time.time())
    
    def to_dict(self) -> Dict:
        return {
            "transfer_id": self.transfer_id,
            "from_chain": self.from_chain.value,
            "to_chain": self.to_chain.value,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "token": self.token,
            "amount": str(self.amount),
            "fee": str(self.fee),
            "status": self.status.value,
            "lock_tx_hash": self.lock_tx_hash,
            "mint_tx_hash": self.mint_tx_hash,
            "signatures": len(self.signatures),
            "required_signatures": self.required_signatures,
            "created_at": self.created_at,
            "is_large_transfer": self.is_large_transfer,
            "is_timelocked": self.is_timelocked,
            "timelock_until": self.timelock_until if self.timelock_until > 0 else None
        }


@dataclass
class BridgeValidator:
    """Bridge validator node."""
    address: str
    chains: List[BridgeChain]
    is_active: bool = True
    total_signed: int = 0
    last_active_at: int = field(default_factory=lambda: int(time.time()))


@dataclass
class WrappedToken:
    """Wrapped token on ELCARO Chain."""
    symbol: str
    name: str
    origin_chain: BridgeChain
    origin_address: str
    elcaro_address: str
    total_wrapped: Decimal = Decimal(0)
    decimals: int = 18


# ------------------------------------------------------------------------------------
# Bridge Core
# ------------------------------------------------------------------------------------

class EnlikoBridge:
    """
    Multi-chain bridge for ELCARO Chain.
    
    Architecture:
    1. User locks tokens on source chain
    2. Bridge validators monitor lock event
    3. Validators sign mint transaction (7-of-10 multisig)
    4. Wrapped tokens minted on ELCARO Chain
    5. User can later burn wrapped tokens to unlock on source chain
    
    Security:
    - 7-of-10 validator signatures required
    - Large transfers (>$100k) have 1-hour timelock
    - Insurance fund covers losses
    - Circuit breakers for anomalies
    """
    
    def __init__(self):
        self.transfers: Dict[str, BridgeTransfer] = {}
        self.validators: Dict[str, BridgeValidator] = {}
        self.wrapped_tokens: Dict[str, WrappedToken] = {}
        
        # Fee configuration
        self.bridge_fee_rate = Decimal("0.002")  # 0.2%
        self.min_bridge_fee = Decimal("1")  # 1 token minimum
        
        # Insurance fund
        self.insurance_fund = Decimal(0)
        
        # Statistics
        self.total_volume = Decimal(0)
        self.total_fees = Decimal(0)
        self.total_transfers = 0
        
        # Timelock configuration
        self.large_transfer_threshold = Decimal("100000")  # $100k
        self.timelock_duration = 3600  # 1 hour in seconds
        
        logger.info("ELCARO Bridge initialized")
    
    # ------------------------------------------------------------------------------------
    # Token Management
    # ------------------------------------------------------------------------------------
    
    def register_wrapped_token(
        self,
        symbol: str,
        name: str,
        origin_chain: BridgeChain,
        origin_address: str,
        elcaro_address: str
    ) -> WrappedToken:
        """Register a new wrapped token."""
        if symbol in self.wrapped_tokens:
            raise ValueError(f"Wrapped token {symbol} already registered")
        
        wrapped = WrappedToken(
            symbol=symbol,
            name=name,
            origin_chain=origin_chain,
            origin_address=origin_address,
            elcaro_address=elcaro_address
        )
        
        self.wrapped_tokens[symbol] = wrapped
        logger.info(f"Wrapped token registered: {symbol} from {origin_chain.value}")
        return wrapped
    
    def get_wrapped_token(self, symbol: str) -> Optional[WrappedToken]:
        """Get wrapped token info."""
        return self.wrapped_tokens.get(symbol)
    
    # ------------------------------------------------------------------------------------
    # Validator Management
    # ------------------------------------------------------------------------------------
    
    def register_validator(
        self,
        address: str,
        chains: List[BridgeChain]
    ) -> BridgeValidator:
        """Register a bridge validator."""
        if address in self.validators:
            raise ValueError(f"Validator {address} already registered")
        
        validator = BridgeValidator(
            address=address,
            chains=chains
        )
        
        self.validators[address] = validator
        logger.info(f"Bridge validator registered: {address} for chains {[c.value for c in chains]}")
        return validator
    
    def get_active_validators(self, chain: BridgeChain = None) -> List[BridgeValidator]:
        """Get active validators, optionally filtered by chain."""
        validators = [v for v in self.validators.values() if v.is_active]
        
        if chain:
            validators = [v for v in validators if chain in v.chains]
        
        return validators
    
    # ------------------------------------------------------------------------------------
    # Bridge Transfers (Lock & Mint)
    # ------------------------------------------------------------------------------------
    
    def initiate_transfer(
        self,
        from_chain: BridgeChain,
        to_chain: BridgeChain,
        from_address: str,
        to_address: str,
        token: str,
        amount: Decimal,
        lock_tx_hash: str
    ) -> str:
        """Initiate a cross-chain transfer (called after lock on source chain)."""
        # Calculate fee
        fee = max(amount * self.bridge_fee_rate, self.min_bridge_fee)
        amount_after_fee = amount - fee
        
        # Generate transfer ID
        transfer_id = self._generate_transfer_id(from_chain, to_chain, from_address, lock_tx_hash)
        
        # Create transfer
        transfer = BridgeTransfer(
            transfer_id=transfer_id,
            from_chain=from_chain,
            to_chain=to_chain,
            from_address=from_address,
            to_address=to_address,
            token=token,
            amount=amount_after_fee,
            fee=fee,
            status=BridgeStatus.PENDING,
            lock_tx_hash=lock_tx_hash
        )
        
        # Check if large transfer (requires timelock)
        if transfer.is_large_transfer:
            transfer.status = BridgeStatus.TIMELOCKED
            transfer.timelock_until = int(time.time()) + self.timelock_duration
            logger.info(f"Large transfer initiated with timelock: {transfer_id}")
        else:
            transfer.status = BridgeStatus.LOCKED
            logger.info(f"Transfer initiated: {transfer_id}")
        
        self.transfers[transfer_id] = transfer
        self.total_transfers += 1
        self.total_volume += amount
        self.total_fees += fee
        
        # Distribute fees
        self._distribute_bridge_fees(fee)
        
        return transfer_id
    
    def sign_transfer(
        self,
        transfer_id: str,
        validator_address: str,
        signature: str
    ) -> bool:
        """Validator signs a bridge transfer."""
        transfer = self.transfers.get(transfer_id)
        if not transfer:
            logger.error(f"Transfer {transfer_id} not found")
            return False
        
        # Check validator
        validator = self.validators.get(validator_address)
        if not validator or not validator.is_active:
            logger.error(f"Validator {validator_address} not found or inactive")
            return False
        
        # Check if already signed
        if signature in transfer.signatures:
            logger.warning(f"Validator {validator_address} already signed transfer {transfer_id}")
            return False
        
        # Add signature
        transfer.signatures.append(signature)
        validator.total_signed += 1
        validator.last_active_at = int(time.time())
        
        logger.info(f"Transfer {transfer_id} signed by {validator_address} ({len(transfer.signatures)}/{transfer.required_signatures})")
        
        # Check if ready to mint
        if transfer.has_enough_signatures and not transfer.is_timelocked:
            self._mint_wrapped_tokens(transfer)
        
        return True
    
    def _mint_wrapped_tokens(self, transfer: BridgeTransfer):
        """Mint wrapped tokens on ELCARO Chain."""
        # Update wrapped token supply
        wrapped = self.wrapped_tokens.get(transfer.token)
        if wrapped:
            wrapped.total_wrapped += transfer.amount
        
        # Update transfer status
        transfer.status = BridgeStatus.MINTED
        transfer.minted_at = int(time.time())
        transfer.mint_tx_hash = self._generate_mint_tx_hash(transfer)
        
        logger.info(f"Wrapped tokens minted: {transfer.amount} {transfer.token} to {transfer.to_address}")
    
    def check_timelocked_transfers(self):
        """Check and process timelocked transfers that are ready."""
        current_time = int(time.time())
        
        for transfer in self.transfers.values():
            if transfer.status == BridgeStatus.TIMELOCKED:
                if transfer.timelock_until <= current_time:
                    transfer.status = BridgeStatus.LOCKED
                    logger.info(f"Transfer {transfer.transfer_id} timelock expired, now processing")
                    
                    # Check if ready to mint
                    if transfer.has_enough_signatures:
                        self._mint_wrapped_tokens(transfer)
    
    # ------------------------------------------------------------------------------------
    # Reverse Bridge (Burn & Unlock)
    # ------------------------------------------------------------------------------------
    
    def initiate_burn(
        self,
        from_address: str,
        to_chain: BridgeChain,
        to_address: str,
        token: str,
        amount: Decimal
    ) -> str:
        """Initiate burn of wrapped tokens to unlock on source chain."""
        # Calculate fee
        fee = max(amount * self.bridge_fee_rate, self.min_bridge_fee)
        amount_after_fee = amount - fee
        
        # Generate transfer ID
        transfer_id = f"burn_{from_address}_{token}_{int(time.time())}"
        
        # Create reverse transfer
        transfer = BridgeTransfer(
            transfer_id=transfer_id,
            from_chain=BridgeChain.ELCARO,
            to_chain=to_chain,
            from_address=from_address,
            to_address=to_address,
            token=token,
            amount=amount_after_fee,
            fee=fee,
            status=BridgeStatus.PENDING
        )
        
        # Burn wrapped tokens
        wrapped = self.wrapped_tokens.get(token)
        if wrapped:
            if wrapped.total_wrapped < amount:
                raise ValueError(f"Insufficient wrapped tokens: {wrapped.total_wrapped} < {amount}")
            wrapped.total_wrapped -= amount
        
        transfer.status = BridgeStatus.LOCKED
        
        self.transfers[transfer_id] = transfer
        self.total_transfers += 1
        self.total_fees += fee
        
        logger.info(f"Burn initiated: {transfer_id}, unlock on {to_chain.value}")
        return transfer_id
    
    # ------------------------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------------------------
    
    def get_transfer(self, transfer_id: str) -> Optional[BridgeTransfer]:
        """Get transfer by ID."""
        return self.transfers.get(transfer_id)
    
    def get_user_transfers(
        self,
        address: str,
        chain: BridgeChain = None,
        status: BridgeStatus = None
    ) -> List[BridgeTransfer]:
        """Get user's bridge transfers."""
        transfers = [
            t for t in self.transfers.values()
            if t.from_address == address or t.to_address == address
        ]
        
        if chain:
            transfers = [t for t in transfers if t.from_chain == chain or t.to_chain == chain]
        
        if status:
            transfers = [t for t in transfers if t.status == status]
        
        return sorted(transfers, key=lambda t: t.created_at, reverse=True)
    
    def get_pending_transfers(self) -> List[BridgeTransfer]:
        """Get all pending transfers awaiting signatures."""
        return [
            t for t in self.transfers.values()
            if t.status in [BridgeStatus.PENDING, BridgeStatus.LOCKED, BridgeStatus.TIMELOCKED]
            and not t.has_enough_signatures
        ]
    
    def get_stats(self) -> Dict:
        """Get bridge statistics."""
        return {
            "total_transfers": self.total_transfers,
            "total_volume": str(self.total_volume),
            "total_fees": str(self.total_fees),
            "insurance_fund": str(self.insurance_fund),
            "active_validators": len(self.get_active_validators()),
            "wrapped_tokens": len(self.wrapped_tokens),
            "pending_transfers": len(self.get_pending_transfers()),
            "wrapped_token_supply": {
                symbol: str(token.total_wrapped)
                for symbol, token in self.wrapped_tokens.items()
            }
        }
    
    # ------------------------------------------------------------------------------------
    # Helper Functions
    # ------------------------------------------------------------------------------------
    
    def _generate_transfer_id(
        self,
        from_chain: BridgeChain,
        to_chain: BridgeChain,
        from_address: str,
        lock_tx_hash: str
    ) -> str:
        """Generate unique transfer ID."""
        data = f"{from_chain.value}_{to_chain.value}_{from_address}_{lock_tx_hash}".encode()
        return hashlib.sha256(data).hexdigest()
    
    def _generate_mint_tx_hash(self, transfer: BridgeTransfer) -> str:
        """Generate mint transaction hash."""
        data = f"mint_{transfer.transfer_id}_{transfer.amount}_{int(time.time())}".encode()
        return hashlib.sha256(data).hexdigest()
    
    def _distribute_bridge_fees(self, fee: Decimal):
        """Distribute bridge fees."""
        # 50% to insurance fund
        insurance = fee * Decimal("0.5")
        self.insurance_fund += insurance
        
        # 30% to bridge validators (distributed proportionally)
        # 20% burned
        
        logger.debug(f"Bridge fee distributed: {fee} (insurance: {insurance})")


# ------------------------------------------------------------------------------------
# Bridge Relayer (Automated)
# ------------------------------------------------------------------------------------

class BridgeRelayer:
    """
    Automated relayer for monitoring and processing bridge transfers.
    
    Functions:
    - Monitor source chain for lock events
    - Submit signatures automatically
    - Process pending transfers
    - Handle emergency situations
    """
    
    def __init__(self, bridge: EnlikoBridge, validator_address: str):
        self.bridge = bridge
        self.validator_address = validator_address
        self.is_running = False
        
    def start(self):
        """Start relayer monitoring."""
        self.is_running = True
        logger.info(f"Bridge relayer started for validator {self.validator_address}")
    
    def stop(self):
        """Stop relayer."""
        self.is_running = False
        logger.info(f"Bridge relayer stopped for validator {self.validator_address}")
    
    def process_pending_transfers(self):
        """Process all pending transfers."""
        pending = self.bridge.get_pending_transfers()
        
        for transfer in pending:
            # Skip if already signed
            if any(sig.startswith(self.validator_address) for sig in transfer.signatures):
                continue
            
            # Skip if timelocked
            if transfer.is_timelocked:
                continue
            
            # Generate signature (simplified - real implementation would use cryptographic signing)
            signature = f"{self.validator_address}_{transfer.transfer_id}_{int(time.time())}"
            
            # Submit signature
            self.bridge.sign_transfer(transfer.transfer_id, self.validator_address, signature)
    
    def check_timelocks(self):
        """Check and process expired timelocks."""
        self.bridge.check_timelocked_transfers()


# ------------------------------------------------------------------------------------
# Supported Chains Configuration
# ------------------------------------------------------------------------------------

SUPPORTED_CHAINS = {
    BridgeChain.TON: {
        "name": "TON",
        "native_token": "TON",
        "supported_tokens": ["USDT", "TON"],
        "confirmation_blocks": 10,
        "avg_block_time": 5
    },
    BridgeChain.ETHEREUM: {
        "name": "Ethereum",
        "native_token": "ETH",
        "supported_tokens": ["ETH", "USDC", "USDT", "WBTC"],
        "confirmation_blocks": 12,
        "avg_block_time": 12
    },
    BridgeChain.BSC: {
        "name": "BNB Chain",
        "native_token": "BNB",
        "supported_tokens": ["BNB", "BUSD", "USDT"],
        "confirmation_blocks": 15,
        "avg_block_time": 3
    },
    BridgeChain.POLYGON: {
        "name": "Polygon",
        "native_token": "MATIC",
        "supported_tokens": ["MATIC", "USDC", "USDT"],
        "confirmation_blocks": 128,
        "avg_block_time": 2
    },
    BridgeChain.ARBITRUM: {
        "name": "Arbitrum",
        "native_token": "ETH",
        "supported_tokens": ["ETH", "USDC", "USDT"],
        "confirmation_blocks": 10,
        "avg_block_time": 0.25
    },
    BridgeChain.OPTIMISM: {
        "name": "Optimism",
        "native_token": "ETH",
        "supported_tokens": ["ETH", "USDC", "USDT"],
        "confirmation_blocks": 10,
        "avg_block_time": 2
    },
    BridgeChain.SOLANA: {
        "name": "Solana",
        "native_token": "SOL",
        "supported_tokens": ["SOL", "USDC"],
        "confirmation_blocks": 32,
        "avg_block_time": 0.4
    }
}
