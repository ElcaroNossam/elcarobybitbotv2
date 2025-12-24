"""
Strategy NFT (ERC-721) - Smart Contract Interface
Each trading strategy is represented as unique NFT
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from .web3_client import Web3Client

logger = logging.getLogger(__name__)


# ERC-721 + Metadata ABI
STRATEGY_NFT_ABI = [
    # ERC-721 Standard
    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "_tokenId", "type": "uint256"}], "name": "ownerOf", "outputs": [{"name": "", "type": "address"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_tokenId", "type": "uint256"}], "name": "transferFrom", "outputs": [], "type": "function"},
    {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_approved", "type": "bool"}], "name": "setApprovalForAll", "outputs": [], "type": "function"},
    {"constant": True, "inputs": [{"name": "_tokenId", "type": "uint256"}], "name": "tokenURI", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    
    # Custom functions
    {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_strategyId", "type": "uint256"}, {"name": "_metadata", "type": "string"}], "name": "mint", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "_tokenId", "type": "uint256"}], "name": "burn", "outputs": [], "type": "function"},
    {"constant": True, "inputs": [{"name": "_tokenId", "type": "uint256"}], "name": "getStrategyData", "outputs": [{"name": "strategyId", "type": "uint256"}, {"name": "creator", "type": "address"}, {"name": "price", "type": "uint256"}, {"name": "totalOwners", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "tokensOfOwner", "outputs": [{"name": "", "type": "uint256[]"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "_tokenId", "type": "uint256"}, {"name": "_performance", "type": "string"}], "name": "updatePerformance", "outputs": [], "type": "function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    
    # Events
    {"anonymous": False, "inputs": [{"indexed": True, "name": "from", "type": "address"}, {"indexed": True, "name": "to", "type": "address"}, {"indexed": True, "name": "tokenId", "type": "uint256"}], "name": "Transfer", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "name": "owner", "type": "address"}, {"indexed": True, "name": "approved", "type": "address"}, {"indexed": True, "name": "tokenId", "type": "uint256"}], "name": "Approval", "type": "event"},
]


@dataclass
class StrategyNFTData:
    """Strategy NFT metadata"""
    token_id: int
    strategy_id: int
    name: str
    description: str
    creator: str
    owner: str
    price: float
    total_owners: int
    performance_stats: Dict
    metadata_uri: str
    minted_at: datetime


class StrategyNFT:
    """
    Strategy NFT Contract - ERC-721 for trading strategies.
    
    Features:
    - Each strategy is a unique NFT
    - Ownership tracking
    - Performance updates on-chain
    - Royalties for creators
    - Transferable/tradable
    
    Use cases:
    - User buys strategy → gets NFT
    - NFT proves ownership
    - Can resell NFT on marketplace
    - Creator gets royalty on each resale
    """
    
    CONTRACT_ADDRESSES = {
        'polygon': '0x0000000000000000000000000000000000000001',  # Deploy address
        'bsc': '0x0000000000000000000000000000000000000001',
        'polygon_mumbai': '0x0000000000000000000000000000000000000001',  # Testnet
    }
    
    def __init__(self, web3_client: Web3Client, contract_address: Optional[str] = None):
        """
        Initialize Strategy NFT interface.
        
        Args:
            web3_client: Web3Client instance
            contract_address: NFT contract address
        """
        self.client = web3_client
        
        if not contract_address:
            network_key = web3_client.network.value
            contract_address = self.CONTRACT_ADDRESSES.get(network_key)
            
            if not contract_address or contract_address == '0x0000000000000000000000000000000000000001':
                raise ValueError(f"Strategy NFT not deployed on {network_key}")
        
        self.contract_address = contract_address
        self.contract = web3_client.get_contract(contract_address, STRATEGY_NFT_ABI)
        
        logger.info(f"StrategyNFT initialized at {contract_address}")
    
    async def mint_strategy_nft(
        self,
        to_address: str,
        strategy_id: int,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mint new strategy NFT.
        
        Args:
            to_address: NFT recipient
            strategy_id: Strategy ID from database
            metadata: Strategy metadata (name, description, etc.)
        
        Returns:
            Transaction receipt with token_id
        """
        import json
        metadata_json = json.dumps(metadata)
        
        result = await self.client.call_contract_function(
            self.contract_address,
            STRATEGY_NFT_ABI,
            "mint",
            to_address,
            strategy_id,
            metadata_json
        )
        
        # Get token ID from receipt logs
        # In real implementation, parse Transfer event
        logger.info(f"Minted strategy NFT for strategy {strategy_id} to {to_address}")
        
        return result
    
    async def get_owner(self, token_id: int) -> str:
        """Get NFT owner address"""
        return await self.client.read_contract_function(
            self.contract_address,
            STRATEGY_NFT_ABI,
            "ownerOf",
            token_id
        )
    
    async def get_balance(self, address: str) -> int:
        """Get number of strategy NFTs owned"""
        return await self.client.read_contract_function(
            self.contract_address,
            STRATEGY_NFT_ABI,
            "balanceOf",
            address
        )
    
    async def get_tokens_of_owner(self, address: str) -> List[int]:
        """
        Get all strategy NFT token IDs owned by address.
        
        Args:
            address: Wallet address
        
        Returns:
            List of token IDs
        """
        return await self.client.read_contract_function(
            self.contract_address,
            STRATEGY_NFT_ABI,
            "tokensOfOwner",
            address
        )
    
    async def get_strategy_data(self, token_id: int) -> Dict[str, Any]:
        """
        Get strategy data from NFT.
        
        Args:
            token_id: NFT token ID
        
        Returns:
            Strategy data
        """
        data = await self.client.read_contract_function(
            self.contract_address,
            STRATEGY_NFT_ABI,
            "getStrategyData",
            token_id
        )
        
        return {
            'strategy_id': data[0],
            'creator': data[1],
            'price': data[2] / 1e18,  # Convert from wei
            'total_owners': data[3]
        }
    
    async def transfer_nft(
        self,
        to_address: str,
        token_id: int
    ) -> Dict[str, Any]:
        """
        Transfer NFT to another address.
        
        Args:
            to_address: Recipient
            token_id: Token ID to transfer
        
        Returns:
            Transaction receipt
        """
        from_address = self.client.address
        
        return await self.client.call_contract_function(
            self.contract_address,
            STRATEGY_NFT_ABI,
            "transferFrom",
            from_address,
            to_address,
            token_id
        )
    
    async def burn_nft(self, token_id: int) -> Dict[str, Any]:
        """
        Burn (destroy) NFT.
        
        Args:
            token_id: Token ID to burn
        
        Returns:
            Transaction receipt
        """
        return await self.client.call_contract_function(
            self.contract_address,
            STRATEGY_NFT_ABI,
            "burn",
            token_id
        )
    
    async def update_performance(
        self,
        token_id: int,
        performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update strategy performance data on-chain.
        
        Args:
            token_id: NFT token ID
            performance: Performance stats
        
        Returns:
            Transaction receipt
        """
        import json
        performance_json = json.dumps(performance)
        
        return await self.client.call_contract_function(
            self.contract_address,
            STRATEGY_NFT_ABI,
            "updatePerformance",
            token_id,
            performance_json
        )
    
    async def get_total_supply(self) -> int:
        """Get total number of minted strategy NFTs"""
        return await self.client.read_contract_function(
            self.contract_address,
            STRATEGY_NFT_ABI,
            "totalSupply"
        )
    
    async def get_token_uri(self, token_id: int) -> str:
        """Get metadata URI for NFT"""
        return await self.client.read_contract_function(
            self.contract_address,
            STRATEGY_NFT_ABI,
            "tokenURI",
            token_id
        )
    
    def get_explorer_url(self, token_id: Optional[int] = None) -> str:
        """Get NFT explorer URL"""
        url = self.client.get_explorer_url(address=self.contract_address)
        if token_id is not None:
            url += f"?a={token_id}"
        return url


# Helper functions
def create_strategy_metadata(
    strategy_id: int,
    name: str,
    description: str,
    creator: str,
    base_strategy: str,
    performance: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create strategy NFT metadata following OpenSea standard.
    
    Args:
        strategy_id: Strategy ID
        name: Strategy name
        description: Strategy description
        creator: Creator username
        base_strategy: Base strategy type
        performance: Performance stats
    
    Returns:
        Metadata dict
    """
    return {
        "name": name,
        "description": description,
        "image": f"https://elcaro.com/api/strategy/{strategy_id}/image",
        "external_url": f"https://elcaro.com/strategy/{strategy_id}",
        "attributes": [
            {"trait_type": "Creator", "value": creator},
            {"trait_type": "Base Strategy", "value": base_strategy},
            {"trait_type": "Win Rate", "value": f"{performance.get('win_rate', 0):.1f}%"},
            {"trait_type": "Profit Factor", "value": f"{performance.get('profit_factor', 0):.2f}"},
            {"trait_type": "Total PnL", "value": f"{performance.get('total_pnl_percent', 0):.1f}%"},
            {"trait_type": "Total Trades", "value": performance.get('total_trades', 0)},
            {"display_type": "date", "trait_type": "Created", "value": int(datetime.now().timestamp())}
        ],
        "properties": {
            "strategy_id": strategy_id,
            "version": "1.0"
        }
    }
