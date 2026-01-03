"""
ELCARO Token (ERC-20) - Smart Contract Interface
Native token for ElCaro trading platform
"""
import logging
from decimal import Decimal, ROUND_DOWN
from typing import Dict, Any, Optional
from dataclasses import dataclass
from .web3_client import Web3Client

logger = logging.getLogger(__name__)


# ELCARO Token Smart Contract ABI
ELCARO_TOKEN_ABI = [
    # ERC-20 Standard
    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "_from", "type": "address"}, {"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transferFrom", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}, {"name": "_spender", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    
    # Events
    {"anonymous": False, "inputs": [{"indexed": True, "name": "from", "type": "address"}, {"indexed": True, "name": "to", "type": "address"}, {"indexed": False, "name": "value", "type": "uint256"}], "name": "Transfer", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "name": "owner", "type": "address"}, {"indexed": True, "name": "spender", "type": "address"}, {"indexed": False, "name": "value", "type": "uint256"}], "name": "Approval", "type": "event"},
    
    # Extended functions (ElCaro specific)
    {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_amount", "type": "uint256"}], "name": "mint", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "_amount", "type": "uint256"}], "name": "burn", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "owner", "outputs": [{"name": "", "type": "address"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "_account", "type": "address"}], "name": "pause", "outputs": [], "type": "function"},
    {"constant": False, "inputs": [{"name": "_account", "type": "address"}], "name": "unpause", "outputs": [], "type": "function"},
    {"constant": True, "inputs": [{"name": "_account", "type": "address"}], "name": "isPaused", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
]


@dataclass
class TokenInfo:
    """Token information"""
    name: str
    symbol: str
    decimals: int
    total_supply: float
    contract_address: str


class ElcaroToken:
    """
    ELCARO Token - ERC-20 token for ElCaro platform.
    
    Features:
    - Standard ERC-20 functionality
    - Minting/burning capabilities (owner only)
    - Pause mechanism for security
    - Used for all platform payments (subscriptions, strategies, etc.)
    
    Tokenomics:
    - Symbol: ELCARO
    - Decimals: 18
    - Initial Supply: 100,000,000 ELCARO
    - Max Supply: 1,000,000,000 ELCARO
    """
    
    # Token contract addresses per network
    CONTRACT_ADDRESSES = {
        'polygon': '0x0000000000000000000000000000000000000000',  # Deploy address
        'bsc': '0x0000000000000000000000000000000000000000',
        'polygon_mumbai': '0x0000000000000000000000000000000000000000',  # Testnet
    }
    
    def __init__(self, web3_client: Web3Client, contract_address: Optional[str] = None):
        """
        Initialize ELCARO token interface.
        
        Args:
            web3_client: Web3Client instance
            contract_address: Token contract address (auto-detect if None)
        """
        self.client = web3_client
        
        # Get contract address for current network
        if not contract_address:
            network_key = web3_client.network.value
            contract_address = self.CONTRACT_ADDRESSES.get(network_key)
            
            if not contract_address or contract_address == '0x0000000000000000000000000000000000000000':
                raise ValueError(f"ELCARO token not deployed on {network_key}")
        
        self.contract_address = contract_address
        self.contract = web3_client.get_contract(contract_address, ELCARO_TOKEN_ABI)
        
        logger.info(f"ElcaroToken initialized at {contract_address}")
    
    async def get_info(self) -> TokenInfo:
        """Get token information"""
        name = await self.client.read_contract_function(
            self.contract_address, ELCARO_TOKEN_ABI, "name"
        )
        symbol = await self.client.read_contract_function(
            self.contract_address, ELCARO_TOKEN_ABI, "symbol"
        )
        decimals = await self.client.read_contract_function(
            self.contract_address, ELCARO_TOKEN_ABI, "decimals"
        )
        total_supply_raw = await self.client.read_contract_function(
            self.contract_address, ELCARO_TOKEN_ABI, "totalSupply"
        )
        
        total_supply = total_supply_raw / (10 ** decimals)
        
        return TokenInfo(
            name=name,
            symbol=symbol,
            decimals=decimals,
            total_supply=total_supply,
            contract_address=self.contract_address
        )
    
    async def balance_of(self, address: str) -> float:
        """
        Get token balance for address.
        
        Args:
            address: Wallet address
        
        Returns:
            Token balance
        """
        balance = await self.client.get_token_balance(self.contract_address, address)
        return balance
    
    async def transfer(self, to_address: str, amount: float) -> Dict[str, Any]:
        """
        Transfer tokens to address.
        
        Args:
            to_address: Recipient address
            amount: Amount in ELCARO tokens
        
        Returns:
            Transaction receipt
        """
        # Convert to wei (considering decimals) - use Decimal for precision
        decimals = await self.client.read_contract_function(
            self.contract_address, ELCARO_TOKEN_ABI, "decimals"
        )
        # SECURITY: Use Decimal to avoid floating point precision loss
        amount_decimal = Decimal(str(amount))
        multiplier = Decimal(10) ** decimals
        amount_wei = int((amount_decimal * multiplier).to_integral_value(rounding=ROUND_DOWN))
        
        return await self.client.call_contract_function(
            self.contract_address,
            ELCARO_TOKEN_ABI,
            "transfer",
            to_address,
            amount_wei
        )
    
    async def approve(self, spender_address: str, amount: float) -> Dict[str, Any]:
        """
        Approve spender to use tokens.
        
        Args:
            spender_address: Spender address (e.g., marketplace contract)
            amount: Amount to approve
        
        Returns:
            Transaction receipt
        """
        decimals = await self.client.read_contract_function(
            self.contract_address, ELCARO_TOKEN_ABI, "decimals"
        )
        # SECURITY: Use Decimal to avoid floating point precision loss
        amount_decimal = Decimal(str(amount))
        multiplier = Decimal(10) ** decimals
        amount_wei = int((amount_decimal * multiplier).to_integral_value(rounding=ROUND_DOWN))
        
        return await self.client.call_contract_function(
            self.contract_address,
            ELCARO_TOKEN_ABI,
            "approve",
            spender_address,
            amount_wei
        )
    
    async def allowance(self, owner_address: str, spender_address: str) -> float:
        """
        Get allowance amount.
        
        Args:
            owner_address: Token owner
            spender_address: Spender
        
        Returns:
            Approved amount
        """
        allowance_wei = await self.client.read_contract_function(
            self.contract_address,
            ELCARO_TOKEN_ABI,
            "allowance",
            owner_address,
            spender_address
        )
        
        decimals = await self.client.read_contract_function(
            self.contract_address, ELCARO_TOKEN_ABI, "decimals"
        )
        
        return allowance_wei / (10 ** decimals)
    
    async def mint(self, to_address: str, amount: float) -> Dict[str, Any]:
        """
        Mint new tokens (owner only).
        
        Args:
            to_address: Recipient
            amount: Amount to mint
        
        Returns:
            Transaction receipt
        """
        decimals = await self.client.read_contract_function(
            self.contract_address, ELCARO_TOKEN_ABI, "decimals"
        )
        # SECURITY: Use Decimal to avoid floating point precision loss
        amount_decimal = Decimal(str(amount))
        multiplier = Decimal(10) ** decimals
        amount_wei = int((amount_decimal * multiplier).to_integral_value(rounding=ROUND_DOWN))
        
        return await self.client.call_contract_function(
            self.contract_address,
            ELCARO_TOKEN_ABI,
            "mint",
            to_address,
            amount_wei
        )
    
    async def burn(self, amount: float) -> Dict[str, Any]:
        """
        Burn tokens from own balance.
        
        Args:
            amount: Amount to burn
        
        Returns:
            Transaction receipt
        """
        decimals = await self.client.read_contract_function(
            self.contract_address, ELCARO_TOKEN_ABI, "decimals"
        )
        # SECURITY: Use Decimal to avoid floating point precision loss
        amount_decimal = Decimal(str(amount))
        multiplier = Decimal(10) ** decimals
        amount_wei = int((amount_decimal * multiplier).to_integral_value(rounding=ROUND_DOWN))
        
        return await self.client.call_contract_function(
            self.contract_address,
            ELCARO_TOKEN_ABI,
            "burn",
            amount_wei
        )
    
    def get_explorer_url(self) -> str:
        """Get token explorer URL"""
        return self.client.get_explorer_url(address=self.contract_address)


# Utility functions for token conversions
def usd_to_elcaro(usd_amount: float, elcaro_price_usd: float = 1.0) -> float:
    """
    Convert USD to ELCARO tokens.
    
    Args:
        usd_amount: Amount in USD
        elcaro_price_usd: Current ELCARO price in USD
    
    Returns:
        Amount in ELCARO
    """
    return usd_amount / elcaro_price_usd


def elcaro_to_usd(elcaro_amount: float, elcaro_price_usd: float = 1.0) -> float:
    """
    Convert ELCARO to USD.
    
    Args:
        elcaro_amount: Amount in ELCARO
        elcaro_price_usd: Current ELCARO price in USD
    
    Returns:
        Amount in USD
    """
    return elcaro_amount * elcaro_price_usd


# Price oracle (simple version - in production use Chainlink or similar)
class TokenPriceOracle:
    """Simple price oracle for ELCARO token"""
    
    # Initial price: 1 ELCARO = $1 USD
    BASE_PRICE_USD = 1.0
    
    @classmethod
    async def get_price(cls) -> float:
        """
        Get current ELCARO price in USD.
        
        Returns:
            Price in USD
        """
        # TODO: In production, fetch from DEX (Uniswap, PancakeSwap)
        # or price oracle (Chainlink)
        return cls.BASE_PRICE_USD
    
    @classmethod
    async def convert_subscription_price(cls, plan: str, period_months: int) -> float:
        """
        Convert subscription price to ELCARO.
        
        Args:
            plan: 'free', 'basic', 'premium'
            period_months: 1, 3, 6, 12
        
        Returns:
            Price in ELCARO tokens
        """
        # Subscription prices in USD
        prices = {
            'basic': {1: 50, 3: 135, 6: 240, 12: 420},
            'premium': {1: 100, 3: 270, 6: 480, 12: 840},
        }
        
        if plan not in prices:
            return 0
        
        usd_price = prices[plan].get(period_months, 0)
        elcaro_price = await cls.get_price()
        
        return usd_to_elcaro(usd_price, elcaro_price)
