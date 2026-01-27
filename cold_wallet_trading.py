"""
MetaMask/WalletConnect Integration for HyperLiquid Trading
Allows users to trade on HL using their cold wallet (MetaMask, WalletConnect)
"""
import logging
from typing import Optional, Dict, Any
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3

logger = logging.getLogger(__name__)


class ColdWalletTrading:
    """
    Trade on HyperLiquid using cold wallet (MetaMask, WalletConnect)
    Users sign transactions locally, never expose private keys
    """
    
    def __init__(self):
        self.w3 = Web3()
        self.connected_wallets = {}  # user_id -> wallet_address
    
    async def connect_wallet(
        self,
        user_id: int,
        wallet_address: str,
        signature: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Verify wallet connection via signature
        
        Args:
            user_id: User ID
            wallet_address: Ethereum wallet address
            signature: Signed message from wallet
            message: Original message that was signed
            
        Returns:
            Connection status and session info
        """
        try:
            # Verify signature
            message_hash = encode_defunct(text=message)
            recovered_address = Account.recover_message(message_hash, signature=signature)
            
            if recovered_address.lower() != wallet_address.lower():
                return {
                    "success": False,
                    "error": "Signature verification failed"
                }
            
            # Store connected wallet
            self.connected_wallets[user_id] = {
                "address": wallet_address,
                "connected_at": None,  # Add timestamp
                "verified": True
            }
            
            logger.info(f"Wallet connected: {wallet_address} for user {user_id}")
            
            return {
                "success": True,
                "wallet_address": wallet_address,
                "user_id": user_id,
                "trading_enabled": True,
                "message": "Wallet connected successfully"
            }
        except Exception as e:
            logger.error(f"Wallet connection error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_connected_wallet(self, user_id: int) -> Optional[str]:
        """Get connected wallet address for user"""
        wallet_data = self.connected_wallets.get(user_id)
        if wallet_data and wallet_data.get("verified"):
            return wallet_data["address"]
        return None
    
    async def prepare_hl_order(
        self,
        user_id: int,
        symbol: str,
        side: str,
        size: float,
        order_type: str = "market",
        price: Optional[float] = None,
        reduce_only: bool = False
    ) -> Dict[str, Any]:
        """
        Prepare HyperLiquid order for signing
        
        User will sign this locally in their wallet
        Then we submit signed order to HL
        
        Args:
            user_id: User ID
            symbol: Trading pair
            side: buy/sell
            size: Position size
            order_type: market/limit
            price: Limit price (for limit orders)
            reduce_only: Close position only
            
        Returns:
            Order data to be signed by wallet
        """
        wallet_address = self.get_connected_wallet(user_id)
        
        if not wallet_address:
            return {
                "success": False,
                "error": "No wallet connected. Please connect MetaMask first."
            }
        
        # Prepare HyperLiquid order message
        # This follows HL's EIP-712 signature format
        order_data = {
            "asset": symbol,
            "is_buy": side.lower() in ["buy", "long"],
            "limit_px": str(price) if price else "0",
            "sz": str(size),
            "reduce_only": reduce_only,
            "order_type": order_type.upper()
        }
        
        # EIP-712 typed data for HyperLiquid
        typed_data = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"}
                ],
                "Order": [
                    {"name": "asset", "type": "string"},
                    {"name": "isBuy", "type": "bool"},
                    {"name": "limitPx", "type": "string"},
                    {"name": "sz", "type": "string"},
                    {"name": "reduceOnly", "type": "bool"},
                    {"name": "orderType", "type": "string"}
                ]
            },
            "domain": {
                "name": "HyperLiquid",
                "version": "1",
                "chainId": 1,  # Ethereum mainnet
                "verifyingContract": "0x0000000000000000000000000000000000000000"
            },
            "primaryType": "Order",
            "message": order_data
        }
        
        return {
            "success": True,
            "order_data": order_data,
            "typed_data": typed_data,
            "wallet_address": wallet_address,
            "user_id": user_id,
            "requires_signature": True,
            "signing_instructions": "Sign this message in MetaMask to execute order on HyperLiquid"
        }
    
    async def submit_signed_order(
        self,
        user_id: int,
        order_data: Dict,
        signature: str
    ) -> Dict[str, Any]:
        """
        Submit signed order to HyperLiquid
        
        Args:
            user_id: User ID
            order_data: Order details
            signature: User's signature from MetaMask
            
        Returns:
            Order execution result
        """
        try:
            wallet_address = self.get_connected_wallet(user_id)
            
            if not wallet_address:
                return {
                    "success": False,
                    "error": "Wallet not connected"
                }
            
            # Import HL adapter
            from hl_adapter import HLAdapter
            
            # Create HL adapter with wallet address
            # Note: HL adapter needs modification to accept signed orders
            adapter = HLAdapter(
                private_key=None,  # Not needed for signed orders
                wallet_address=wallet_address,
                testnet=False
            )
            
            # Submit signed order to HyperLiquid using their agent API
            # HyperLiquid requires orders signed with private key or via approved agent
            # This endpoint is for users who sign via MetaMask
            
            # For now, cold wallet trading is not fully implemented
            # Users should use private key trading via hl_adapter.py
            logger.warning(f"Cold wallet trading is experimental. User {user_id} attempted order submission.")
            
            return {
                "success": False,
                "error": "Cold wallet trading is not yet available. Please configure your private key in API Settings for trading.",
                "order_id": None,
                "status": "not_implemented",
                "wallet_address": wallet_address
            }
        except Exception as e:
            logger.error(f"Order submission error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def disconnect_wallet(self, user_id: int) -> bool:
        """Disconnect wallet for user"""
        if user_id in self.connected_wallets:
            del self.connected_wallets[user_id]
            logger.info(f"Wallet disconnected for user {user_id}")
            return True
        return False
    
    def get_wallet_status(self, user_id: int) -> Dict[str, Any]:
        """Get wallet connection status"""
        wallet_data = self.connected_wallets.get(user_id)
        
        if wallet_data:
            return {
                "connected": True,
                "wallet_address": wallet_data["address"],
                "trading_enabled": True
            }
        
        return {
            "connected": False,
            "wallet_address": None,
            "trading_enabled": False
        }


# Global instance
cold_wallet_trading = ColdWalletTrading()


# Helper functions for easy integration
async def connect_metamask(user_id: int, wallet_address: str, signature: str, message: str):
    """Connect MetaMask wallet"""
    return await cold_wallet_trading.connect_wallet(user_id, wallet_address, signature, message)


async def place_order_with_metamask(user_id: int, symbol: str, side: str, size: float, **kwargs):
    """Place order using connected MetaMask wallet"""
    # Prepare order for signing
    order_prep = await cold_wallet_trading.prepare_hl_order(
        user_id, symbol, side, size, **kwargs
    )
    
    if not order_prep.get("success"):
        return order_prep
    
    # Return order data for frontend to sign
    return {
        "success": True,
        "action": "sign_order",
        "typed_data": order_prep["typed_data"],
        "instructions": "Please sign this order in MetaMask"
    }


async def submit_signed_hl_order(user_id: int, order_data: Dict, signature: str):
    """Submit signed order to HyperLiquid"""
    return await cold_wallet_trading.submit_signed_order(user_id, order_data, signature)


def get_wallet_info(user_id: int):
    """Get wallet connection info"""
    return cold_wallet_trading.get_wallet_status(user_id)


def disconnect_metamask(user_id: int):
    """Disconnect MetaMask"""
    return cold_wallet_trading.disconnect_wallet(user_id)
