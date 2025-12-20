"""
Validation utilities
"""
import re
from typing import Tuple, Optional


def validate_symbol(symbol: str) -> Tuple[bool, Optional[str]]:
    """Validate trading symbol format"""
    if not symbol:
        return False, "Symbol is required"
    
    symbol = symbol.upper().strip()
    
    # Must be alphanumeric and end with USDT
    if not re.match(r"^[A-Z0-9]{2,20}USDT$", symbol):
        return False, "Invalid symbol format. Must end with USDT"
    
    # Check minimum length
    if len(symbol) < 5:  # Minimum: XUSDT
        return False, "Symbol too short"
    
    return True, None


def validate_leverage(leverage: int, max_leverage: int = 100) -> Tuple[bool, Optional[str]]:
    """Validate leverage value"""
    if not isinstance(leverage, int):
        try:
            leverage = int(leverage)
        except (ValueError, TypeError):
            return False, "Leverage must be an integer"
    
    if leverage < 1:
        return False, "Leverage must be at least 1"
    
    if leverage > max_leverage:
        return False, f"Leverage cannot exceed {max_leverage}"
    
    return True, None


def validate_percent(
    value: float,
    min_val: float = 0.1,
    max_val: float = 100.0,
    field_name: str = "Percentage"
) -> Tuple[bool, Optional[str]]:
    """Validate percentage value"""
    try:
        v = float(value)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a number"
    
    if v < min_val:
        return False, f"{field_name} must be at least {min_val}%"
    
    if v > max_val:
        return False, f"{field_name} cannot exceed {max_val}%"
    
    return True, None


def validate_price(
    price: float,
    min_price: float = 0.0,
    field_name: str = "Price"
) -> Tuple[bool, Optional[str]]:
    """Validate price value"""
    try:
        p = float(price)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a number"
    
    if p <= min_price:
        return False, f"{field_name} must be greater than {min_price}"
    
    return True, None


def validate_api_key(key: str) -> Tuple[bool, Optional[str]]:
    """Validate API key format"""
    if not key:
        return False, "API key is required"
    
    key = key.strip()
    
    if len(key) < 10:
        return False, "API key is too short"
    
    if len(key) > 100:
        return False, "API key is too long"
    
    # Basic alphanumeric check
    if not re.match(r"^[A-Za-z0-9_-]+$", key):
        return False, "API key contains invalid characters"
    
    return True, None


def validate_wallet_address(address: str) -> Tuple[bool, Optional[str]]:
    """Validate Ethereum wallet address (for HyperLiquid)"""
    if not address:
        return False, "Wallet address is required"
    
    address = address.strip()
    
    # Check Ethereum address format
    if not re.match(r"^0x[a-fA-F0-9]{40}$", address):
        return False, "Invalid Ethereum wallet address"
    
    return True, None
