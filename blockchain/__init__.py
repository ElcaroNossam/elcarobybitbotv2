"""
ELCARO Chain - Layer 1 Blockchain
Complete blockchain infrastructure with PoS consensus, DEX, bridge, and governance
"""
# Core blockchain components
from .chain import LyxenChain, ConsensusEngine, Transaction, Block, Validator, Account
from .chain import generate_address, elc_to_wei, wei_to_elc

# DEX components
from .dex import LyxenDEX, LyxenAMM, OrderBook, PerpetualFutures
from .dex import LiquidityPool, Order, Position, OrderSide, OrderType, PositionSide

# Bridge components
from .bridge import LyxenBridge, BridgeRelayer, BridgeTransfer, BridgeValidator, WrappedToken
from .bridge import BridgeChain, BridgeStatus

# Governance components
from .governance import LyxenDAO, Proposal, Vote
from .governance import ProposalType, ProposalStatus, VoteOption

# Legacy Web3 components (if needed for compatibility)
try:
    from .web3_client import Web3Client, NetworkType
    from .token_contract import LyxenToken
    from .nft_contract import StrategyNFT
    from .marketplace_contract import StrategyMarketplace
    
    __all__ = [
        # Core blockchain
        'LyxenChain', 'ConsensusEngine', 'Transaction', 'Block', 'Validator', 'Account',
        'generate_address', 'elc_to_wei', 'wei_to_elc',
        # DEX
        'LyxenDEX', 'LyxenAMM', 'OrderBook', 'PerpetualFutures',
        'LiquidityPool', 'Order', 'Position', 'OrderSide', 'OrderType', 'PositionSide',
        # Bridge
        'LyxenBridge', 'BridgeRelayer', 'BridgeTransfer', 'BridgeValidator', 'WrappedToken',
        'BridgeChain', 'BridgeStatus',
        # Governance
        'LyxenDAO', 'Proposal', 'Vote',
        'ProposalType', 'ProposalStatus', 'VoteOption',
        # Legacy
        'Web3Client', 'NetworkType', 'LyxenToken', 'StrategyNFT', 'StrategyMarketplace'
    ]
except ImportError:
    # Web3 not available, only blockchain components
    __all__ = [
        # Core blockchain
        'LyxenChain', 'ConsensusEngine', 'Transaction', 'Block', 'Validator', 'Account',
        'generate_address', 'elc_to_wei', 'wei_to_elc',
        # DEX
        'LyxenDEX', 'LyxenAMM', 'OrderBook', 'PerpetualFutures',
        'LiquidityPool', 'Order', 'Position', 'OrderSide', 'OrderType', 'PositionSide',
        # Bridge
        'LyxenBridge', 'BridgeRelayer', 'BridgeTransfer', 'BridgeValidator', 'WrappedToken',
        'BridgeChain', 'BridgeStatus',
        # Governance
        'LyxenDAO', 'Proposal', 'Vote',
        'ProposalType', 'ProposalStatus', 'VoteOption',
    ]
