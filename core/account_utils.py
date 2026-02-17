"""
Account Type Utilities
======================
Centralized utilities for account type normalization and handling.
Bug #3 Fix: Single source of truth instead of duplicated functions.
"""

from typing import Optional, Tuple


def normalize_account_type(account_type: Optional[str], exchange: str = 'bybit') -> Optional[str]:
    """
    Normalize account_type for API and DB queries.
    
    Handles:
    - 'both' → default safe type per exchange
    - Cross-exchange mapping: demo→testnet, real→mainnet for HL (and vice versa for Bybit)
    
    Args:
        account_type: 'demo', 'real', 'both', 'testnet', 'mainnet', or None
        exchange: 'bybit' or 'hyperliquid'
    
    Returns:
        Normalized account_type or None (if input was None)
    """
    if account_type is None:
        return None
    if exchange == 'hyperliquid':
        # Map Bybit types to HL types
        mapping = {'both': 'testnet', 'demo': 'testnet', 'real': 'mainnet'}
        return mapping.get(account_type, account_type)
    else:
        # Map HL types to Bybit types
        mapping = {'both': 'demo', 'testnet': 'demo', 'mainnet': 'real'}
        return mapping.get(account_type, account_type)


def get_hl_credentials_for_account(hl_creds: dict, account_type: str) -> Tuple[Optional[str], bool, Optional[str]]:
    """
    Get HyperLiquid credentials for specified account type.
    
    Supports both new architecture (testnet/mainnet separate keys)
    and legacy format (single key with hl_testnet flag).
    
    For Unified Account architecture:
    - API wallet signs orders
    - Main wallet holds funds/positions
    - wallet_address should be passed to HLAdapter for balance queries
    
    Args:
        hl_creds: Dictionary with HL credentials from db.get_hl_credentials()
        account_type: 'testnet', 'mainnet', 'demo', or 'real'
    
    Returns:
        Tuple of (private_key, is_testnet, wallet_address)
    """
    is_testnet = account_type in ("testnet", "demo")
    
    # Try new architecture first
    if is_testnet:
        private_key = hl_creds.get("hl_testnet_private_key")
        wallet_address = hl_creds.get("hl_testnet_wallet_address")
        if not private_key:
            # Fallback to legacy format
            private_key = hl_creds.get("hl_private_key")
            wallet_address = hl_creds.get("hl_wallet_address")
            if private_key and not hl_creds.get("hl_testnet", False):
                # Legacy key is for mainnet, not testnet
                private_key = None
                wallet_address = None
    else:
        private_key = hl_creds.get("hl_mainnet_private_key")
        wallet_address = hl_creds.get("hl_mainnet_wallet_address")
        if not private_key:
            # Fallback to legacy format
            private_key = hl_creds.get("hl_private_key")
            wallet_address = hl_creds.get("hl_wallet_address")
            if private_key and hl_creds.get("hl_testnet", False):
                # Legacy key is for testnet, not mainnet
                private_key = None
                wallet_address = None
    
    return private_key, is_testnet, wallet_address


def is_live_account(account_type: str, exchange: str = 'bybit') -> bool:
    """
    Check if account type is a live/production account.
    
    Args:
        account_type: Account type string
        exchange: Exchange name
    
    Returns:
        True if this is a real money account
    """
    if exchange == 'hyperliquid':
        return account_type == 'mainnet'
    return account_type == 'real'


def get_default_account_type(exchange: str = 'bybit', trading_mode: str = 'demo') -> str:
    """
    Get default account type for exchange based on trading mode.
    
    Args:
        exchange: 'bybit' or 'hyperliquid'
        trading_mode: 'demo', 'real', or 'both'
    
    Returns:
        Default account type string
    """
    if exchange == 'hyperliquid':
        if trading_mode == 'real':
            return 'mainnet'
        return 'testnet'
    else:
        if trading_mode == 'real':
            return 'real'
        return 'demo'


# Alias for backward compatibility
_normalize_both_account_type = normalize_account_type
