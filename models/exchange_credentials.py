"""
Exchange credentials models
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import hashlib


class ExchangeType(Enum):
    """Supported exchanges"""
    BYBIT = "bybit"
    HYPERLIQUID = "hyperliquid"


class NetworkType(Enum):
    """Network types"""
    MAINNET = "mainnet"
    TESTNET = "testnet"
    DEMO = "demo"


@dataclass
class ExchangeCredentials:
    """Exchange API credentials model"""
    user_id: int = 0
    exchange: ExchangeType = ExchangeType.BYBIT
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    wallet_address: Optional[str] = None
    private_key: Optional[str] = None
    network: NetworkType = NetworkType.MAINNET
    is_testnet: bool = False
    is_demo: bool = False
    is_active: bool = True
    is_connected: bool = False
    last_connected_at: Optional[datetime] = None
    connection_error: Optional[str] = None
    label: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_bybit(self) -> bool:
        return self.exchange == ExchangeType.BYBIT
    
    @property
    def is_hyperliquid(self) -> bool:
        return self.exchange == ExchangeType.HYPERLIQUID
    
    @property
    def has_credentials(self) -> bool:
        if self.is_bybit:
            return bool(self.api_key and self.api_secret)
        elif self.is_hyperliquid:
            return bool(self.wallet_address and self.private_key)
        return False
    
    @property
    def masked_key(self) -> str:
        if self.is_bybit and self.api_key:
            if len(self.api_key) > 8:
                return f"{self.api_key[:4]}...{self.api_key[-4:]}"
            return "****"
        elif self.is_hyperliquid and self.wallet_address:
            if len(self.wallet_address) > 12:
                return f"{self.wallet_address[:6]}...{self.wallet_address[-4:]}"
            return "****"
        return ""
    
    @property
    def network_name(self) -> str:
        if self.is_demo:
            return "Demo"
        elif self.is_testnet:
            return "Testnet"
        return "Mainnet"
    
    def get_base_url(self) -> str:
        if self.is_bybit:
            if self.is_demo:
                return "https://api-demo.bybit.com"
            elif self.is_testnet:
                return "https://api-testnet.bybit.com"
            return "https://api.bybit.com"
        elif self.is_hyperliquid:
            if self.is_testnet:
                return "https://api.hyperliquid-testnet.xyz"
            return "https://api.hyperliquid.xyz"
        return ""
    
    def validate(self) -> tuple:
        if self.is_bybit:
            if not self.api_key:
                return False, "API key is required"
            if not self.api_secret:
                return False, "API secret is required"
            if len(self.api_key) < 10:
                return False, "Invalid API key format"
        elif self.is_hyperliquid:
            if not self.wallet_address:
                return False, "Wallet address is required"
            if not self.wallet_address.startswith("0x"):
                return False, "Invalid wallet address format"
            if len(self.wallet_address) != 42:
                return False, "Invalid wallet address length"
            if self.private_key and not self.private_key.startswith("0x"):
                return False, "Invalid private key format"
        return True, None
    
    def to_dict(self, include_secrets: bool = False) -> Dict[str, Any]:
        data = {
            "user_id": self.user_id,
            "exchange": self.exchange.value,
            "network": self.network.value,
            "is_testnet": self.is_testnet,
            "is_demo": self.is_demo,
            "is_active": self.is_active,
            "is_connected": self.is_connected,
            "has_credentials": self.has_credentials,
            "masked_key": self.masked_key,
            "network_name": self.network_name,
            "label": self.label,
            "last_connected_at": self.last_connected_at.isoformat() if self.last_connected_at else None,
            "connection_error": self.connection_error,
        }
        if include_secrets:
            if self.is_bybit:
                data["api_key"] = self.api_key
                data["api_secret"] = self.api_secret
            elif self.is_hyperliquid:
                data["wallet_address"] = self.wallet_address
                data["private_key"] = self.private_key
        return data
    
    def generate_signature(self, message: str) -> str:
        if not self.api_secret:
            raise ValueError("API secret not set")
        import hmac
        return hmac.new(
            self.api_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()


@dataclass
class ExchangeBalance:
    """Exchange account balance"""
    exchange: ExchangeType = ExchangeType.BYBIT
    total_equity: float = 0.0
    available_balance: float = 0.0
    used_margin: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    currency: str = "USDT"
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def margin_ratio(self) -> float:
        if self.total_equity == 0:
            return 0.0
        return (self.used_margin / self.total_equity) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "exchange": self.exchange.value,
            "total_equity": self.total_equity,
            "available_balance": self.available_balance,
            "used_margin": self.used_margin,
            "unrealized_pnl": self.unrealized_pnl,
            "realized_pnl": self.realized_pnl,
            "currency": self.currency,
            "margin_ratio": self.margin_ratio,
            "updated_at": self.updated_at.isoformat(),
        }
