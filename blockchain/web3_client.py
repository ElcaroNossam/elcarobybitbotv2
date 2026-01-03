"""
Web3 Client - Universal blockchain connection manager
Supports: Polygon, BSC, Ethereum, Base, Arbitrum
"""
import os
import logging
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import aiohttp

logger = logging.getLogger(__name__)


class NetworkType(Enum):
    """Supported blockchain networks"""
    # Mainnets
    POLYGON = "polygon"
    BSC = "bsc"
    ETHEREUM = "ethereum"
    BASE = "base"
    ARBITRUM = "arbitrum"
    
    # Testnets
    POLYGON_MUMBAI = "polygon_mumbai"
    BSC_TESTNET = "bsc_testnet"
    SEPOLIA = "sepolia"
    BASE_SEPOLIA = "base_sepolia"


@dataclass
class NetworkConfig:
    """Network configuration"""
    name: str
    chain_id: int
    rpc_url: str
    explorer_url: str
    native_token: str
    is_testnet: bool = False


class NetworkRegistry:
    """Registry of all supported networks"""
    
    NETWORKS = {
        NetworkType.POLYGON: NetworkConfig(
            name="Polygon Mainnet",
            chain_id=137,
            rpc_url="https://polygon-rpc.com",
            explorer_url="https://polygonscan.com",
            native_token="MATIC",
            is_testnet=False
        ),
        NetworkType.BSC: NetworkConfig(
            name="BSC Mainnet",
            chain_id=56,
            rpc_url="https://bsc-dataseed.binance.org",
            explorer_url="https://bscscan.com",
            native_token="BNB",
            is_testnet=False
        ),
        NetworkType.ETHEREUM: NetworkConfig(
            name="Ethereum Mainnet",
            chain_id=1,
            rpc_url=os.getenv("ETHEREUM_RPC_URL", "https://eth.llamarpc.com"),
            explorer_url="https://etherscan.io",
            native_token="ETH",
            is_testnet=False
        ),
        NetworkType.BASE: NetworkConfig(
            name="Base Mainnet",
            chain_id=8453,
            rpc_url="https://mainnet.base.org",
            explorer_url="https://basescan.org",
            native_token="ETH",
            is_testnet=False
        ),
        NetworkType.ARBITRUM: NetworkConfig(
            name="Arbitrum One",
            chain_id=42161,
            rpc_url="https://arb1.arbitrum.io/rpc",
            explorer_url="https://arbiscan.io",
            native_token="ETH",
            is_testnet=False
        ),
        # Testnets
        NetworkType.POLYGON_MUMBAI: NetworkConfig(
            name="Polygon Mumbai",
            chain_id=80001,
            rpc_url="https://rpc-mumbai.maticvigil.com",
            explorer_url="https://mumbai.polygonscan.com",
            native_token="MATIC",
            is_testnet=True
        ),
        NetworkType.BSC_TESTNET: NetworkConfig(
            name="BSC Testnet",
            chain_id=97,
            rpc_url="https://data-seed-prebsc-1-s1.binance.org:8545",
            explorer_url="https://testnet.bscscan.com",
            native_token="BNB",
            is_testnet=True
        ),
        NetworkType.SEPOLIA: NetworkConfig(
            name="Sepolia Testnet",
            chain_id=11155111,
            rpc_url="https://rpc.sepolia.org",
            explorer_url="https://sepolia.etherscan.io",
            native_token="ETH",
            is_testnet=True
        ),
    }
    
    @classmethod
    def get_config(cls, network: NetworkType) -> NetworkConfig:
        """Get network configuration"""
        return cls.NETWORKS[network]


class Web3Client:
    """
    Universal Web3 client for blockchain interactions.
    Handles wallet connections, transactions, smart contract calls.
    """
    
    def __init__(
        self,
        network: NetworkType = NetworkType.POLYGON,
        private_key: Optional[str] = None,
        rpc_url: Optional[str] = None
    ):
        """
        Initialize Web3 client.
        
        Args:
            network: Target blockchain network
            private_key: Wallet private key (optional for read-only)
            rpc_url: Custom RPC URL (overrides default)
        """
        self.network = network
        self.config = NetworkRegistry.get_config(network)
        
        # Setup Web3 connection
        rpc = rpc_url or self.config.rpc_url
        self.w3 = Web3(Web3.HTTPProvider(rpc))
        
        # Add PoA middleware for networks like Polygon, BSC
        if network in [NetworkType.POLYGON, NetworkType.BSC, NetworkType.POLYGON_MUMBAI, NetworkType.BSC_TESTNET]:
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Setup wallet if private key provided
        self.account: Optional[Account] = None
        self.address: Optional[str] = None
        
        if private_key:
            self.set_wallet(private_key)
        
        logger.info(f"Web3Client initialized for {self.config.name}")
    
    def set_wallet(self, private_key: str):
        """Set wallet from private key"""
        if not private_key.startswith("0x"):
            private_key = f"0x{private_key}"
        
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        logger.info(f"Wallet set: {self.address[:10]}...{self.address[-6:]}")
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to blockchain"""
        try:
            return self.w3.is_connected()
        except Exception:
            return False
    
    async def get_balance(self, address: Optional[str] = None) -> float:
        """
        Get native token balance (ETH, MATIC, BNB).
        
        Args:
            address: Wallet address (uses own if not specified)
        
        Returns:
            Balance in native token (not wei)
        """
        addr = address or self.address
        if not addr:
            raise ValueError("No address specified")
        
        balance_wei = self.w3.eth.get_balance(addr)
        balance = self.w3.from_wei(balance_wei, 'ether')
        return float(balance)
    
    async def get_token_balance(self, token_address: str, wallet_address: Optional[str] = None) -> float:
        """
        Get ERC-20 token balance.
        
        Args:
            token_address: Token contract address
            wallet_address: Wallet to check (uses own if not specified)
        
        Returns:
            Token balance (accounting for decimals)
        """
        addr = wallet_address or self.address
        if not addr:
            raise ValueError("No wallet address")
        
        # ERC-20 ABI for balanceOf
        abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]
        
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=abi
        )
        
        balance = contract.functions.balanceOf(Web3.to_checksum_address(addr)).call()
        decimals = contract.functions.decimals().call()
        
        return balance / (10 ** decimals)
    
    async def send_transaction(
        self,
        to_address: str,
        value: float = 0,
        data: str = "0x",
        gas_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send transaction to blockchain.
        
        Args:
            to_address: Destination address
            value: Amount in native token (ETH/MATIC/BNB)
            data: Transaction data (for contract calls)
            gas_limit: Custom gas limit
        
        Returns:
            Transaction receipt
        """
        if not self.account:
            raise ValueError("Wallet not set")
        
        # Build transaction
        nonce = self.w3.eth.get_transaction_count(self.address)
        
        tx = {
            'from': self.address,
            'to': Web3.to_checksum_address(to_address),
            'value': self.w3.to_wei(value, 'ether'),
            'nonce': nonce,
            'data': data,
            'chainId': self.config.chain_id
        }
        
        # Estimate gas
        if gas_limit:
            tx['gas'] = gas_limit
        else:
            try:
                tx['gas'] = self.w3.eth.estimate_gas(tx)
            except Exception as e:
                logger.error(f"Gas estimation failed: {e}")
                tx['gas'] = 100000  # Fallback
        
        # Get gas price
        tx['gasPrice'] = self.w3.eth.gas_price
        
        # Sign transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
        
        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            'tx_hash': tx_hash.hex(),
            'status': receipt['status'],
            'gas_used': receipt['gasUsed'],
            'block_number': receipt['blockNumber'],
            'explorer_url': f"{self.config.explorer_url}/tx/{tx_hash.hex()}"
        }
    
    def get_contract(self, address: str, abi: List[Dict]) -> Any:
        """
        Get contract instance.
        
        Args:
            address: Contract address
            abi: Contract ABI
        
        Returns:
            Web3 contract instance
        """
        return self.w3.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=abi
        )
    
    async def call_contract_function(
        self,
        contract_address: str,
        abi: List[Dict],
        function_name: str,
        *args,
        value: float = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call smart contract function (write).
        
        Args:
            contract_address: Contract address
            abi: Contract ABI
            function_name: Function name
            *args: Function arguments
            value: ETH/MATIC to send
            **kwargs: Additional transaction params
        
        Returns:
            Transaction receipt
        """
        if not self.account:
            raise ValueError("Wallet not set")
        
        contract = self.get_contract(contract_address, abi)
        function = getattr(contract.functions, function_name)
        
        # Build transaction
        nonce = self.w3.eth.get_transaction_count(self.address)
        
        tx = function(*args).build_transaction({
            'from': self.address,
            'value': self.w3.to_wei(value, 'ether'),
            'nonce': nonce,
            'chainId': self.config.chain_id,
            'gasPrice': self.w3.eth.gas_price,
            **kwargs
        })
        
        # Estimate gas if not provided
        if 'gas' not in tx:
            try:
                tx['gas'] = self.w3.eth.estimate_gas(tx)
            except Exception as e:
                logger.error(f"Gas estimation failed: {e}")
                tx['gas'] = 200000
        
        # Sign and send
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            'tx_hash': tx_hash.hex(),
            'status': receipt['status'],
            'gas_used': receipt['gasUsed'],
            'block_number': receipt['blockNumber'],
            'explorer_url': f"{self.config.explorer_url}/tx/{tx_hash.hex()}"
        }
    
    async def read_contract_function(
        self,
        contract_address: str,
        abi: List[Dict],
        function_name: str,
        *args
    ) -> Any:
        """
        Read from smart contract (view/pure function).
        
        Args:
            contract_address: Contract address
            abi: Contract ABI
            function_name: Function name
            *args: Function arguments
        
        Returns:
            Function return value
        """
        contract = self.get_contract(contract_address, abi)
        function = getattr(contract.functions, function_name)
        return function(*args).call()
    
    def get_transaction_receipt(self, tx_hash: str) -> Dict:
        """Get transaction receipt"""
        return dict(self.w3.eth.get_transaction_receipt(tx_hash))
    
    def get_explorer_url(self, tx_hash: str = None, address: str = None, block: int = None) -> str:
        """Get block explorer URL"""
        if tx_hash:
            return f"{self.config.explorer_url}/tx/{tx_hash}"
        elif address:
            return f"{self.config.explorer_url}/address/{address}"
        elif block:
            return f"{self.config.explorer_url}/block/{block}"
        return self.config.explorer_url
    
    @staticmethod
    def generate_wallet() -> Dict[str, str]:
        """
        Generate new wallet.
        
        Returns:
            Dict with private_key and address
        """
        account = Account.create()
        return {
            'private_key': account.key.hex(),
            'address': account.address
        }
    
    @staticmethod
    def is_valid_address(address: str) -> bool:
        """Check if address is valid Ethereum address"""
        return Web3.is_address(address)
