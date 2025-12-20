"""
Core constants for the trading bot
"""
from enum import Enum
from typing import Dict, Any


class ExchangeType(Enum):
    """Supported exchanges"""
    BYBIT = "bybit"
    HYPERLIQUID = "hyperliquid"
    
    @classmethod
    def from_string(cls, value: str) -> "ExchangeType":
        for member in cls:
            if member.value == value.lower():
                return member
        raise ValueError(f"Unknown exchange: {value}")


class OrderType(Enum):
    """Order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT = "take_profit"
    TAKE_PROFIT_LIMIT = "take_profit_limit"


class OrderSide(Enum):
    """Order sides"""
    BUY = "buy"
    SELL = "sell"
    LONG = "long"
    SHORT = "short"


class PositionSide(Enum):
    """Position sides"""
    LONG = "long"
    SHORT = "short"


class MarginMode(Enum):
    """Margin modes"""
    CROSS = "cross"
    ISOLATED = "isolated"


class LicenseType(Enum):
    """User license types"""
    FREE = "free"
    PREMIUM = "premium"
    VIP = "vip"
    ENTERPRISE = "enterprise"
    
    @property
    def level(self) -> int:
        levels = {
            LicenseType.FREE: 0,
            LicenseType.PREMIUM: 1,
            LicenseType.VIP: 2,
            LicenseType.ENTERPRISE: 3
        }
        return levels.get(self, 0)
    
    def has_access(self, required: "LicenseType") -> bool:
        return self.level >= required.level
    
    @classmethod
    def from_string(cls, value: str) -> "LicenseType":
        for member in cls:
            if member.value == value.lower():
                return member
        return cls.FREE


class ExchangeMode(Enum):
    """Exchange trading mode"""
    BYBIT_ONLY = "bybit"
    HYPERLIQUID_ONLY = "hyperliquid"
    BOTH = "both"
    
    @classmethod
    def from_string(cls, value: str) -> "ExchangeMode":
        for member in cls:
            if member.value == value.lower():
                return member
        return cls.BYBIT_ONLY


class TradingMode(Enum):
    """Trading mode (demo/real)"""
    DEMO = "demo"
    REAL = "real"
    TESTNET = "testnet"  # For HyperLiquid


# Feature flags that require premium
PREMIUM_FEATURES = {
    "hyperliquid": LicenseType.PREMIUM,
    "advanced_dca": LicenseType.PREMIUM,
    "advanced_pyramid": LicenseType.PREMIUM,
    "custom_indicators": LicenseType.VIP,
    "api_access": LicenseType.VIP,
    "multi_account": LicenseType.ENTERPRISE,
}


# Default trading parameters
DEFAULT_TRADING_CONFIG = {
    "risk_percent": 1.0,
    "max_positions": 5,
    "max_leverage": 20,
    "default_order_type": "market",
    "default_margin_mode": "cross",
    "auto_tp": True,
    "auto_sl": True,
    "tp_percent": 3.0,
    "sl_percent": 2.0,
    "trailing_stop": False,
    "trailing_percent": 1.0,
}


# Supported timeframes
TIMEFRAMES = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "1w"]


# API Rate limits
RATE_LIMITS = {
    "bybit": {
        "requests_per_second": 10,
        "requests_per_minute": 120,
    },
    "hyperliquid": {
        "requests_per_second": 5,
        "requests_per_minute": 60,
    }
}
