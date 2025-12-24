"""
ELCARO Chain - Layer 1 Blockchain
Complete blockchain infrastructure with PoS consensus, DEX, bridge, and governance
"""
# Core blockchain components
from .chain import ElcaroChain, ConsensusEngine, Transaction, Block, Validator, Account
from .chain import generate_address, elc_to_wei, wei_to_elc

# DEX components
from .dex import ElcaroDEX, ElcaroAMM, OrderBook, PerpetualFutures
from .dex import LiquidityPool, Order, Position, OrderSide, OrderType, PositionSide

# Bridge components
from .bridge import ElcaroBridge, BridgeRelayer, BridgeTransfer, BridgeValidator, WrappedToken
from .bridge import BridgeChain, BridgeStatus

# Governance components
from .governance import ElcaroDAO, Proposal, Vote
from .governance import ProposalType, ProposalStatus, VoteOption

# Legacy Web3 components (if needed for compatibility)
try:
    from .web3_client import Web3Client, NetworkType
    from .token_contract import ElcaroToken
    from .nft_contract import StrategyNFT
    from .marketplace_contract import StrategyMarketplace
    
    __all__ = [
        # Core blockchain
        'ElcaroChain', 'ConsensusEngine', 'Transaction', 'Block', 'Validator', 'Account',
        'generate_address', 'elc_to_wei', 'wei_to_elc',
        # DEX
        'ElcaroDEX', 'ElcaroAMM', 'OrderBook', 'PerpetualFutures',
        'LiquidityPool', 'Order', 'Position', 'OrderSide', 'OrderType', 'PositionSide',
        # Bridge
        'ElcaroBridge', 'BridgeRelayer', 'BridgeTransfer', 'BridgeValidator', 'WrappedToken',
        'BridgeChain', 'BridgeStatus',
        # Governance
        'ElcaroDAO', 'Proposal', 'Vote',
        'ProposalType', 'ProposalStatus', 'VoteOption',
        # Legacy
        'Web3Client', 'NetworkType', 'ElcaroToken', 'StrategyNFT', 'StrategyMarketplace'
    ]
except ImportError:
    # Web3 not available, only blockchain components
    __all__ = [
        # Core blockchain
        'ElcaroChain', 'ConsensusEngine', 'Transaction', 'Block', 'Validator', 'Account',
        'generate_address', 'elc_to_wei', 'wei_to_elc',
        # DEX
        'ElcaroDEX', 'ElcaroAMM', 'OrderBook', 'PerpetualFutures',
        'LiquidityPool', 'Order', 'Position', 'OrderSide', 'OrderType', 'PositionSide',
        # Bridge
        'ElcaroBridge', 'BridgeRelayer', 'BridgeTransfer', 'BridgeValidator', 'WrappedToken',
        'BridgeChain', 'BridgeStatus',
        # Governance
        'ElcaroDAO', 'Proposal', 'Vote',
        'ProposalType', 'ProposalStatus', 'VoteOption',
    ]
