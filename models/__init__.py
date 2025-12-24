"""
Data models for Bybit Demo Trading Bot

Unified data models used across all layers:
- bot.py (Telegram handlers)
- services/ (Business logic)
- core/ (Infrastructure)
- exchanges/ (Exchange API wrappers)
- webapp/ (FastAPI endpoints)

All exchange responses MUST be converted to these models using:
- Position.from_bybit() / Position.from_hyperliquid()
- Order.from_bybit() / Order.from_hyperliquid()
- Balance.from_bybit() / Balance.from_hyperliquid()
"""

# User models (legacy - keep for compatibility)
from .user import User, UserConfig, UserLicense, LicenseType
from .trade import Trade, TradeType, TradeStatus
from .exchange_credentials import ExchangeCredentials, ExchangeType

# UNIFIED MODELS - Single Source of Truth
from .unified import (
    # Enums
    OrderSide, OrderType, OrderStatus, PositionSide,
    # Core Models
    Position, Order, Balance, OrderResult,
    # Helper Functions
    normalize_symbol, convert_side
)

__all__ = [
    # User models (legacy)
    "User", "UserConfig", "UserLicense", "LicenseType",
    "Trade", "TradeType", "TradeStatus",
    "ExchangeCredentials", "ExchangeType",
    
    # UNIFIED MODELS (use these for all new code!)
    # Enums
    "OrderSide", "OrderType", "OrderStatus", "PositionSide",
    # Core Models
    "Position", "Order", "Balance", "OrderResult",
    # Helper Functions
    "normalize_symbol", "convert_side",
]

