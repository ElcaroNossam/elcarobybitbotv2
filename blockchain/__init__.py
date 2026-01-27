"""
ELCARO Chain - Layer 1 Blockchain
Complete blockchain infrastructure with PoS consensus, DEX, bridge, and governance
"""
# Core blockchain components
from .chain import EnlikoChain, ConsensusEngine, Transaction, Block, Validator, Account
from .chain import generate_address, elc_to_wei, wei_to_elc

# DEX components
from .dex import EnlikoDEX, EnlikoAMM, OrderBook, PerpetualFutures
from .dex import LiquidityPool, Order, Position, OrderSide, OrderType, PositionSide

# Bridge components
from .bridge import EnlikoBridge, BridgeRelayer, BridgeTransfer, BridgeValidator, WrappedToken
from .bridge import BridgeChain, BridgeStatus

# Governance components
from .governance import EnlikoDAO, Proposal, Vote
from .governance import ProposalType, ProposalStatus, VoteOption

# Legacy Web3 components (if needed for compatibility)
try:
    from .web3_client import Web3Client, NetworkType
    from .token_contract import EnlikoToken
    from .nft_contract import StrategyNFT
    from .marketplace_contract import StrategyMarketplace
    
    __all__ = [
        # Core blockchain
        'EnlikoChain', 'ConsensusEngine', 'Transaction', 'Block', 'Validator', 'Account',
        'generate_address', 'elc_to_wei', 'wei_to_elc',
        # DEX
        'EnlikoDEX', 'EnlikoAMM', 'OrderBook', 'PerpetualFutures',
        'LiquidityPool', 'Order', 'Position', 'OrderSide', 'OrderType', 'PositionSide',
        # Bridge
        'EnlikoBridge', 'BridgeRelayer', 'BridgeTransfer', 'BridgeValidator', 'WrappedToken',
        'BridgeChain', 'BridgeStatus',
        # Governance
        'EnlikoDAO', 'Proposal', 'Vote',
        'ProposalType', 'ProposalStatus', 'VoteOption',
        # Legacy
        'Web3Client', 'NetworkType', 'EnlikoToken', 'StrategyNFT', 'StrategyMarketplace'
    ]
except ImportError:
    # Web3 not available, only blockchain components
    __all__ = [
        # Core blockchain
        'EnlikoChain', 'ConsensusEngine', 'Transaction', 'Block', 'Validator', 'Account',
        'generate_address', 'elc_to_wei', 'wei_to_elc',
        # DEX
        'EnlikoDEX', 'EnlikoAMM', 'OrderBook', 'PerpetualFutures',
        'LiquidityPool', 'Order', 'Position', 'OrderSide', 'OrderType', 'PositionSide',
        # Bridge
        'EnlikoBridge', 'BridgeRelayer', 'BridgeTransfer', 'BridgeValidator', 'WrappedToken',
        'BridgeChain', 'BridgeStatus',
        # Governance
        'EnlikoDAO', 'Proposal', 'Vote',
        'ProposalType', 'ProposalStatus', 'VoteOption',
    ]
