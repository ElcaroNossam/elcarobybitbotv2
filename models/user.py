"""
User-related models
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


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


@dataclass
class UserLicense:
    """User license information"""
    type: LicenseType = LicenseType.FREE
    expires_at: Optional[datetime] = None
    promo_code: Optional[str] = None
    features: List[str] = field(default_factory=list)
    
    @property
    def is_active(self) -> bool:
        if self.type == LicenseType.FREE:
            return True
        if self.expires_at is None:
            return True
        return datetime.utcnow() < self.expires_at
    
    @property
    def is_premium(self) -> bool:
        return self.is_active and self.type.level >= LicenseType.PREMIUM.level
    
    def can_access(self, feature: str) -> bool:
        if not self.is_active:
            return False
        if self.type == LicenseType.ENTERPRISE:
            return True
        return feature.lower() in self.features
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "features": self.features
        }


@dataclass
class UserConfig:
    """User trading configuration"""
    exchange_mode: str = "bybit"
    risk_percent: float = 1.0
    max_positions: int = 5
    max_leverage: int = 20
    default_order_type: str = "market"
    default_margin_mode: str = "cross"
    auto_tp: bool = True
    auto_sl: bool = True
    tp_percent: float = 3.0
    sl_percent: float = 2.0
    trailing_stop: bool = False
    trailing_percent: float = 1.0
    dca_enabled: bool = False
    dca_levels: int = 3
    dca_multiplier: float = 1.5
    pyramid_enabled: bool = False
    pyramid_levels: int = 3
    pyramid_distance: float = 1.0
    min_oi_change: float = 0.0
    max_oi_change: float = 100.0
    use_rsi_filter: bool = False
    use_bb_filter: bool = False
    notify_trades: bool = True
    notify_signals: bool = True
    notify_errors: bool = True
    allowed_coins: List[str] = field(default_factory=list)
    blocked_coins: List[str] = field(default_factory=list)
    language: str = "en"
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserConfig":
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


@dataclass
class User:
    """User model"""
    id: int
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    is_approved: bool = False
    is_banned: bool = False
    has_accepted_terms: bool = False
    license: UserLicense = field(default_factory=UserLicense)
    config: UserConfig = field(default_factory=UserConfig)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_active_at: Optional[datetime] = None
    referral_code: Optional[str] = None
    referred_by: Optional[int] = None
    
    @property
    def display_name(self) -> str:
        if self.first_name:
            name = self.first_name
            if self.last_name:
                name += f" {self.last_name}"
            return name
        return self.username or f"User {self.telegram_id}"
    
    @property
    def can_trade(self) -> bool:
        return self.is_active and self.is_approved and not self.is_banned
    
    @property
    def is_premium(self) -> bool:
        return self.license.is_premium
    
    def can_access_exchange(self, exchange: str) -> bool:
        if exchange.lower() == "bybit":
            return True
        if exchange.lower() == "hyperliquid":
            return self.is_premium
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "display_name": self.display_name,
            "is_active": self.is_active,
            "is_approved": self.is_approved,
            "is_banned": self.is_banned,
            "license": self.license.to_dict(),
            "config": self.config.to_dict(),
            "can_trade": self.can_trade,
            "is_premium": self.is_premium,
        }
