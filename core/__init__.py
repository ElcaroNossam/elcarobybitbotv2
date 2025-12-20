"""
Core module for Bybit Demo Trading Bot
"""

from .exceptions import (
    BotException,
    ExchangeError,
    AuthenticationError,
    RateLimitError,
    InsufficientBalanceError,
    PositionNotFoundError,
    OrderError,
    LicenseError,
    ConfigurationError,
    DatabaseError,
    SignalParseError,
)

from .config import Config, get_config

__all__ = [
    "BotException",
    "ExchangeError",
    "AuthenticationError",
    "RateLimitError",
    "InsufficientBalanceError",
    "PositionNotFoundError",
    "OrderError",
    "LicenseError",
    "ConfigurationError",
    "DatabaseError",
    "SignalParseError",
    "Config",
    "get_config",
]
