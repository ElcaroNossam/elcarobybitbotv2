"""
Strategy Marketplace Smart Contract Interface
Buy, sell, and trade strategy NFTs using ELCARO tokens
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from .web3_client import Web3Client

logger = logging.getLogger(__name__)


# Marketplace Smart Contract ABI
MARKETPLACE_ABI = [
    # Listing management
    {"constant": False, "inputs": [{"name": "_tokenId", "type": "uint256"}, {"name": "_price", "type": "uint256"}, {"name": "_royaltyPercent", "type": "uint256"}], "name": "listStrategy", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "_listingId", "type": "uint256"}], "name": "cancelListing", "outputs": [], "type": "function"},
    {"constant": False, "inputs": [{"name": "_listingId", "type": "uint256"}], "name": "buyStrategy", "outputs": [], "type": "function"},
    
    # View functions
    {"constant": True, "inputs": [{"name": "_listingId", "type": "uint256"}], "name": "getListing", "outputs": [{"name": "seller", "type": "address"}, {"name": "tokenId", "type": "uint256"}, {"name": "price", "type": "uint256"}, {"name": "isActive", "type": "bool"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "getActiveListings", "outputs": [{"name": "", "type": "uint256[]"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "_seller", "type": "address"}], "name": "getSellerListings", "outputs": [{"name": "", "type": "uint256[]"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "_tokenId", "type": "uint256"}], "name": "getRoyaltyInfo", "outputs": [{"name": "creator", "type": "address"}, {"name": "royaltyPercent", "type": "uint256"}], "type": "function"},
    
    # Admin functions
    {"constant": False, "inputs": [{"name": "_feePercent", "type": "uint256"}], "name": "setMarketplaceFee", "outputs": [], "type": "function"},
    {"constant": True, "inputs": [], "name": "getMarketplaceFee", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": False, "inputs": [], "name": "withdrawFees", "outputs": [], "type": "function"},
    
    # Subscription with tokens
    {"constant": False, "inputs": [{"name": "_plan", "type": "string"}, {"name": "_months", "type": "uint256"}], "name": "purchaseSubscription", "outputs": [], "type": "function"},
    {"constant": True, "inputs": [{"name": "_user", "type": "address"}], "name": "getSubscription", "outputs": [{"name": "plan", "type": "string"}, {"name": "expiresAt", "type": "uint256"}], "type": "function"},
    
    # Events
    {"anonymous": False, "inputs": [{"indexed": True, "name": "listingId", "type": "uint256"}, {"indexed": True, "name": "seller", "type": "address"}, {"indexed": True, "name": "tokenId", "type": "uint256"}, {"indexed": False, "name": "price", "type": "uint256"}], "name": "StrategyListed", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "name": "listingId", "type": "uint256"}, {"indexed": True, "name": "buyer", "type": "address"}, {"indexed": True, "name": "seller", "type": "address"}, {"indexed": False, "name": "tokenId", "type": "uint256"}, {"indexed": False, "name": "price", "type": "uint256"}], "name": "StrategySold", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "name": "user", "type": "address"}, {"indexed": False, "name": "plan", "type": "string"}, {"indexed": False, "name": "months", "type": "uint256"}, {"indexed": False, "name": "amount", "type": "uint256"}], "name": "SubscriptionPurchased", "type": "event"},
]


@dataclass
class StrategyListing:
    """Strategy listing on marketplace"""
    listing_id: int
    seller: str
    token_id: int
    price: float
    royalty_percent: float
    is_active: bool
    created_at: datetime


@dataclass
class RoyaltyInfo:
    """Creator royalty information"""
    creator: str
    royalty_percent: float


class StrategyMarketplace:
    """
    Strategy Marketplace Smart Contract.
    
    Features:
    - List strategies for sale
    - Buy strategies with ELCARO tokens
    - Creator royalties on resales (5-10%)
    - Platform fee (2.5%)
    - Subscription payments with tokens
    - On-chain ownership verification
    
    Flow:
    1. User creates strategy → gets NFT
    2. List NFT on marketplace with price
    3. Buyer approves ELCARO tokens
    4. Buyer purchases → tokens transferred
    5. Creator gets royalty, seller gets payment
    6. Buyer receives NFT + strategy access
    """
    
    CONTRACT_ADDRESSES = {
        'polygon': '0x0000000000000000000000000000000000000002',  # Deploy address
        'bsc': '0x0000000000000000000000000000000000000002',
        'polygon_mumbai': '0x0000000000000000000000000000000000000002',  # Testnet
    }
    
    def __init__(self, web3_client: Web3Client, contract_address: Optional[str] = None):
        """
        Initialize Marketplace interface.
        
        Args:
            web3_client: Web3Client instance
            contract_address: Marketplace contract address
        """
        self.client = web3_client
        
        if not contract_address:
            network_key = web3_client.network.value
            contract_address = self.CONTRACT_ADDRESSES.get(network_key)
            
            if not contract_address or contract_address == '0x0000000000000000000000000000000000000002':
                raise ValueError(f"Marketplace not deployed on {network_key}")
        
        self.contract_address = contract_address
        self.contract = web3_client.get_contract(contract_address, MARKETPLACE_ABI)
        
        logger.info(f"StrategyMarketplace initialized at {contract_address}")
    
    async def list_strategy(
        self,
        token_id: int,
        price: float,
        royalty_percent: float = 5.0
    ) -> Dict[str, Any]:
        """
        List strategy for sale.
        
        Args:
            token_id: Strategy NFT token ID
            price: Price in ELCARO tokens
            royalty_percent: Creator royalty (default 5%)
        
        Returns:
            Transaction receipt with listing_id
        """
        # Convert price to wei
        price_wei = int(price * 1e18)
        royalty_bps = int(royalty_percent * 100)  # Basis points (5% = 500)
        
        result = await self.client.call_contract_function(
            self.contract_address,
            MARKETPLACE_ABI,
            "listStrategy",
            token_id,
            price_wei,
            royalty_bps
        )
        
        logger.info(f"Listed strategy NFT {token_id} for {price} ELCARO")
        return result
    
    async def cancel_listing(self, listing_id: int) -> Dict[str, Any]:
        """
        Cancel active listing.
        
        Args:
            listing_id: Listing ID
        
        Returns:
            Transaction receipt
        """
        return await self.client.call_contract_function(
            self.contract_address,
            MARKETPLACE_ABI,
            "cancelListing",
            listing_id
        )
    
    async def buy_strategy(self, listing_id: int) -> Dict[str, Any]:
        """
        Buy strategy from marketplace.
        
        Args:
            listing_id: Listing ID to purchase
        
        Returns:
            Transaction receipt
        """
        # Note: Buyer must approve ELCARO tokens BEFORE calling this
        return await self.client.call_contract_function(
            self.contract_address,
            MARKETPLACE_ABI,
            "buyStrategy",
            listing_id
        )
    
    async def get_listing(self, listing_id: int) -> Optional[StrategyListing]:
        """
        Get listing details.
        
        Args:
            listing_id: Listing ID
        
        Returns:
            StrategyListing or None
        """
        data = await self.client.read_contract_function(
            self.contract_address,
            MARKETPLACE_ABI,
            "getListing",
            listing_id
        )
        
        if not data[3]:  # is_active
            return None
        
        return StrategyListing(
            listing_id=listing_id,
            seller=data[0],
            token_id=data[1],
            price=data[2] / 1e18,
            royalty_percent=0,  # Get from getRoyaltyInfo
            is_active=data[3],
            created_at=datetime.now()
        )
    
    async def get_active_listings(self) -> List[int]:
        """
        Get all active listing IDs.
        
        Returns:
            List of listing IDs
        """
        return await self.client.read_contract_function(
            self.contract_address,
            MARKETPLACE_ABI,
            "getActiveListings"
        )
    
    async def get_seller_listings(self, seller_address: str) -> List[int]:
        """
        Get all listings by seller.
        
        Args:
            seller_address: Seller wallet address
        
        Returns:
            List of listing IDs
        """
        return await self.client.read_contract_function(
            self.contract_address,
            MARKETPLACE_ABI,
            "getSellerListings",
            seller_address
        )
    
    async def get_royalty_info(self, token_id: int) -> RoyaltyInfo:
        """
        Get creator royalty information.
        
        Args:
            token_id: Strategy NFT token ID
        
        Returns:
            RoyaltyInfo
        """
        data = await self.client.read_contract_function(
            self.contract_address,
            MARKETPLACE_ABI,
            "getRoyaltyInfo",
            token_id
        )
        
        return RoyaltyInfo(
            creator=data[0],
            royalty_percent=data[1] / 100  # Convert from basis points
        )
    
    async def purchase_subscription(
        self,
        plan: str,
        months: int
    ) -> Dict[str, Any]:
        """
        Purchase subscription with ELCARO tokens.
        
        Args:
            plan: 'basic' or 'premium'
            months: 1, 3, 6, or 12
        
        Returns:
            Transaction receipt
        """
        # Note: User must approve ELCARO tokens BEFORE calling this
        return await self.client.call_contract_function(
            self.contract_address,
            MARKETPLACE_ABI,
            "purchaseSubscription",
            plan,
            months
        )
    
    async def get_subscription(self, user_address: str) -> Dict[str, Any]:
        """
        Get user's subscription status.
        
        Args:
            user_address: User wallet address
        
        Returns:
            Subscription info
        """
        data = await self.client.read_contract_function(
            self.contract_address,
            MARKETPLACE_ABI,
            "getSubscription",
            user_address
        )
        
        return {
            'plan': data[0],
            'expires_at': datetime.fromtimestamp(data[1]) if data[1] > 0 else None,
            'is_active': data[1] > datetime.now().timestamp() if data[1] > 0 else False
        }
    
    async def get_marketplace_fee(self) -> float:
        """
        Get current marketplace fee percentage.
        
        Returns:
            Fee percentage (e.g., 2.5)
        """
        fee_bps = await self.client.read_contract_function(
            self.contract_address,
            MARKETPLACE_ABI,
            "getMarketplaceFee"
        )
        return fee_bps / 100
    
    async def set_marketplace_fee(self, fee_percent: float) -> Dict[str, Any]:
        """
        Set marketplace fee (admin only).
        
        Args:
            fee_percent: Fee percentage (e.g., 2.5)
        
        Returns:
            Transaction receipt
        """
        fee_bps = int(fee_percent * 100)
        return await self.client.call_contract_function(
            self.contract_address,
            MARKETPLACE_ABI,
            "setMarketplaceFee",
            fee_bps
        )
    
    async def withdraw_fees(self) -> Dict[str, Any]:
        """
        Withdraw accumulated marketplace fees (admin only).
        
        Returns:
            Transaction receipt
        """
        return await self.client.call_contract_function(
            self.contract_address,
            MARKETPLACE_ABI,
            "withdrawFees"
        )
    
    def get_explorer_url(self) -> str:
        """Get marketplace explorer URL"""
        return self.client.get_explorer_url(address=self.contract_address)


# Helper functions
def calculate_sale_breakdown(
    price: float,
    royalty_percent: float = 5.0,
    marketplace_fee_percent: float = 2.5
) -> Dict[str, float]:
    """
    Calculate payment breakdown for strategy sale.
    
    Args:
        price: Sale price in ELCARO
        royalty_percent: Creator royalty percentage
        marketplace_fee_percent: Platform fee percentage
    
    Returns:
        Payment breakdown
    """
    marketplace_fee = price * (marketplace_fee_percent / 100)
    royalty = price * (royalty_percent / 100)
    seller_amount = price - marketplace_fee - royalty
    
    return {
        'total_price': price,
        'seller_receives': seller_amount,
        'creator_royalty': royalty,
        'marketplace_fee': marketplace_fee,
        'royalty_percent': royalty_percent,
        'fee_percent': marketplace_fee_percent
    }
