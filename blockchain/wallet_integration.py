"""
Web3 Wallet Integration - MetaMask, WalletConnect, etc.
Browser-side wallet connection for WebApp
"""
import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import hashlib
import secrets

logger = logging.getLogger(__name__)


@dataclass
class WalletConnection:
    """Wallet connection information"""
    user_id: int
    wallet_address: str
    network: str
    connected_at: datetime
    signature: str  # Message signature for verification
    is_verified: bool = False


class WalletAuth:
    """
    Web3 Wallet Authentication.
    
    Flow:
    1. User clicks "Connect Wallet" in WebApp
    2. MetaMask/WalletConnect popup appears
    3. User signs message to prove ownership
    4. Backend verifies signature
    5. Wallet linked to user account
    """
    
    @staticmethod
    def generate_signin_message(wallet_address: str, nonce: str) -> str:
        """
        Generate message for user to sign.
        
        Args:
            wallet_address: User's wallet address
            nonce: Random nonce for security
        
        Returns:
            Message to sign
        """
        timestamp = int(datetime.now().timestamp())
        
        message = f"""Welcome to Enliko Platform!

Sign this message to prove you own this wallet.

Wallet: {wallet_address}
Nonce: {nonce}
Timestamp: {timestamp}

This won't cost any gas or funds.
"""
        return message
    
    @staticmethod
    def verify_signature(
        message: str,
        signature: str,
        expected_address: str
    ) -> bool:
        """
        Verify wallet signature.
        
        Args:
            message: Original message
            signature: Signed message
            expected_address: Expected wallet address
        
        Returns:
            True if signature is valid
        """
        try:
            from eth_account.messages import encode_defunct
            from web3 import Web3
            from eth_account import Account
            
            # Create message hash
            message_hash = encode_defunct(text=message)
            
            # Recover address from signature
            recovered_address = Account.recover_message(message_hash, signature=signature)
            
            # Compare addresses (case-insensitive)
            return recovered_address.lower() == expected_address.lower()
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    @staticmethod
    def generate_nonce() -> str:
        """Generate random nonce for signing"""
        return secrets.token_hex(16)


# JavaScript code for WebApp (to be included in templates)
WALLET_CONNECT_JS = """
// Enliko Web3 Wallet Integration
// Add to webapp/static/js/wallet.js

class EnlikoWallet {
    constructor() {
        this.provider = null;
        this.account = null;
        this.chainId = null;
        this.isConnected = false;
    }
    
    // Detect wallet provider
    async detectProvider() {
        if (window.ethereum) {
            this.provider = window.ethereum;
            return true;
        }
        
        // Check for other providers
        if (window.web3) {
            this.provider = window.web3.currentProvider;
            return true;
        }
        
        alert('Please install MetaMask or another Web3 wallet!');
        return false;
    }
    
    // Connect wallet
    async connect() {
        if (!await this.detectProvider()) {
            return null;
        }
        
        try {
            // Request account access
            const accounts = await this.provider.request({
                method: 'eth_requestAccounts'
            });
            
            this.account = accounts[0];
            
            // Get chain ID
            this.chainId = await this.provider.request({
                method: 'eth_chainId'
            });
            
            this.isConnected = true;
            
            // Listen for account changes
            this.provider.on('accountsChanged', (accounts) => {
                this.account = accounts[0];
                this.onAccountChanged(accounts[0]);
            });
            
            // Listen for chain changes
            this.provider.on('chainChanged', (chainId) => {
                this.chainId = chainId;
                this.onChainChanged(chainId);
            });
            
            return this.account;
            
        } catch (error) {
            console.error('Failed to connect wallet:', error);
            return null;
        }
    }
    
    // Sign message
    async signMessage(message) {
        if (!this.account) {
            throw new Error('Wallet not connected');
        }
        
        try {
            const signature = await this.provider.request({
                method: 'personal_sign',
                params: [message, this.account]
            });
            
            return signature;
            
        } catch (error) {
            console.error('Failed to sign message:', error);
            throw error;
        }
    }
    
    // Switch network
    async switchNetwork(chainId) {
        try {
            await this.provider.request({
                method: 'wallet_switchEthereumChain',
                params: [{ chainId: `0x${chainId.toString(16)}` }]
            });
            
            return true;
            
        } catch (error) {
            // Network not added, try to add it
            if (error.code === 4902) {
                return await this.addNetwork(chainId);
            }
            
            console.error('Failed to switch network:', error);
            return false;
        }
    }
    
    // Add network
    async addNetwork(chainId) {
        const networks = {
            137: {  // Polygon
                chainId: '0x89',
                chainName: 'Polygon Mainnet',
                nativeCurrency: {
                    name: 'MATIC',
                    symbol: 'MATIC',
                    decimals: 18
                },
                rpcUrls: ['https://polygon-rpc.com'],
                blockExplorerUrls: ['https://polygonscan.com']
            },
            56: {  // BSC
                chainId: '0x38',
                chainName: 'BNB Smart Chain',
                nativeCurrency: {
                    name: 'BNB',
                    symbol: 'BNB',
                    decimals: 18
                },
                rpcUrls: ['https://bsc-dataseed.binance.org'],
                blockExplorerUrls: ['https://bscscan.com']
            }
        };
        
        const network = networks[chainId];
        if (!network) {
            throw new Error('Unsupported network');
        }
        
        try {
            await this.provider.request({
                method: 'wallet_addEthereumChain',
                params: [network]
            });
            
            return true;
            
        } catch (error) {
            console.error('Failed to add network:', error);
            return false;
        }
    }
    
    // Get ENLIKO token balance
    async getTokenBalance(tokenAddress) {
        if (!this.account) {
            return 0;
        }
        
        const Web3 = window.Web3;
        const web3 = new Web3(this.provider);
        
        // ERC-20 ABI (balanceOf + decimals)
        const abi = [
            {
                "constant": true,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": true,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ];
        
        const contract = new web3.eth.Contract(abi, tokenAddress);
        
        const balance = await contract.methods.balanceOf(this.account).call();
        const decimals = await contract.methods.decimals().call();
        
        return balance / (10 ** decimals);
    }
    
    // Approve token spending
    async approveToken(tokenAddress, spenderAddress, amount) {
        const Web3 = window.Web3;
        const web3 = new Web3(this.provider);
        
        const abi = [{
            "constant": false,
            "inputs": [
                {"name": "_spender", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "approve",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        }];
        
        const contract = new web3.eth.Contract(abi, tokenAddress);
        
        // Convert amount to wei (18 decimals)
        const amountWei = web3.utils.toWei(amount.toString(), 'ether');
        
        const tx = await contract.methods.approve(spenderAddress, amountWei).send({
            from: this.account
        });
        
        return tx;
    }
    
    // Callbacks (override these)
    onAccountChanged(account) {
        console.log('Account changed:', account);
    }
    
    onChainChanged(chainId) {
        console.log('Chain changed:', chainId);
        window.location.reload();
    }
    
    // Disconnect
    disconnect() {
        this.account = null;
        this.isConnected = false;
    }
    
    // Get network name
    getNetworkName() {
        const names = {
            '0x1': 'Ethereum',
            '0x89': 'Polygon',
            '0x38': 'BSC',
            '0x2105': 'Base'
        };
        return names[this.chainId] || 'Unknown';
    }
}

// Initialize global wallet instance
window.elcaroWallet = new EnlikoWallet();

// Helper functions
async function connectWallet() {
    const address = await window.elcaroWallet.connect();
    if (address) {
        console.log('Connected:', address);
        
        // Get nonce from backend
        const response = await fetch('/api/wallet/nonce', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({wallet_address: address})
        });
        
        const data = await response.json();
        const message = data.message;
        
        // Sign message
        const signature = await window.elcaroWallet.signMessage(message);
        
        // Verify with backend
        const verifyResponse = await fetch('/api/wallet/verify', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                wallet_address: address,
                signature: signature,
                message: message
            })
        });
        
        const verifyData = await verifyResponse.json();
        
        if (verifyData.success) {
            alert('Wallet connected successfully!');
            updateWalletUI(address);
        } else {
            alert('Failed to verify wallet signature');
        }
    }
}

function updateWalletUI(address) {
    const short = `${address.slice(0, 6)}...${address.slice(-4)}`;
    document.getElementById('walletAddress').textContent = short;
    document.getElementById('connectBtn').style.display = 'none';
    document.getElementById('walletInfo').style.display = 'block';
}
"""


def save_wallet_js():
    """Save wallet JavaScript to webapp/static/js/"""
    js_dir = os.path.join("webapp", "static", "js")
    os.makedirs(js_dir, exist_ok=True)
    
    js_file = os.path.join(js_dir, "wallet.js")
    with open(js_file, "w") as f:
        f.write(WALLET_CONNECT_JS)
    
    logger.info(f"Saved wallet.js to {js_file}")
