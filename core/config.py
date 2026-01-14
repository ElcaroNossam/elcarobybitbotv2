"""
Configuration management for Bybit Demo Trading Bot
"""

import os
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class ExchangeConfig:
    """Configuration for an exchange"""
    name: str
    base_url: str
    demo_url: Optional[str] = None
    testnet_url: Optional[str] = None
    rate_limit: int = 10
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class DatabaseConfig:
    """Database configuration"""
    path: str = "bot.db"
    wal_mode: bool = True
    timeout: float = 30.0
    check_same_thread: bool = False


@dataclass
class TelegramConfig:
    """Telegram bot configuration"""
    token: str = ""
    admin_ids: List[int] = field(default_factory=list)
    signal_channel_ids: List[int] = field(default_factory=list)
    webhook_url: Optional[str] = None
    webhook_port: int = 8443


@dataclass
class WebAppConfig:
    """Web application configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    # SECURITY: Changed from ["*"] to empty list - must be configured explicitly
    # Wildcard CORS origins are dangerous as they allow any website to make requests
    cors_origins: List[str] = field(default_factory=list)


@dataclass
class TradingConfig:
    """Trading configuration"""
    max_open_positions: int = 10
    max_limit_orders: int = 20
    default_leverage: int = 10
    min_order_value: float = 5.0
    max_order_value: float = 10000.0
    default_tp_percent: float = 3.0
    default_sl_percent: float = 2.0


@dataclass
class Config:
    """Main application configuration"""
    
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    webapp: WebAppConfig = field(default_factory=WebAppConfig)
    trading: TradingConfig = field(default_factory=TradingConfig)
    exchanges: Dict[str, ExchangeConfig] = field(default_factory=dict)
    debug: bool = False
    log_level: str = "INFO"
    timezone: str = "UTC"
    premium_features: List[str] = field(default_factory=lambda: [
        "hyperliquid", "advanced_signals", "multi_exchange", "priority_support"
    ])
    
    def __post_init__(self):
        self._load_from_env()
        self._setup_exchanges()
    
    def _load_from_env(self):
        self.telegram.token = os.getenv("TELEGRAM_TOKEN", "")
        admin_ids = os.getenv("ADMIN_ID", "")
        if admin_ids:
            self.telegram.admin_ids = [int(x.strip()) for x in admin_ids.split(",") if x.strip()]
        signal_ids = os.getenv("SIGNAL_CHANNEL_IDS", "")
        if signal_ids:
            self.telegram.signal_channel_ids = [int(x.strip()) for x in signal_ids.split(",") if x.strip()]
        self.webapp.secret_key = os.getenv("SECRET_KEY", os.urandom(32).hex())
        self.webapp.port = int(os.getenv("WEBAPP_PORT", "8000"))
        self.webapp.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.database.path = os.getenv("DATABASE_PATH", "bot.db")
    
    def _setup_exchanges(self):
        self.exchanges = {
            "bybit": ExchangeConfig(
                name="bybit",
                base_url="https://api.bybit.com",
                demo_url="https://api-demo.bybit.com",
                testnet_url="https://api-testnet.bybit.com",
                rate_limit=10, timeout=30
            ),
            "hyperliquid": ExchangeConfig(
                name="hyperliquid",
                base_url="https://api.hyperliquid.xyz",
                testnet_url="https://api.hyperliquid-testnet.xyz",
                rate_limit=5, timeout=30
            )
        }
    
    def get_exchange_config(self, exchange: str) -> Optional[ExchangeConfig]:
        return self.exchanges.get(exchange.lower())
    
    def is_admin(self, user_id: int) -> bool:
        return user_id in self.telegram.admin_ids
    
    def is_premium_feature(self, feature: str) -> bool:
        return feature.lower() in self.premium_features


_config: Optional[Config] = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    global _config
    _config = Config()
    return _config


def get_env(key: str, default: Any = None, cast: type = str) -> Any:
    value = os.getenv(key, default)
    if value is None:
        return default
    if cast == bool:
        return str(value).lower() in ("true", "1", "yes", "on")
    return cast(value)


def get_env_list(key: str, default: List[str] = None, separator: str = ",") -> List[str]:
    value = os.getenv(key, "")
    if not value:
        return default or []
    return [x.strip() for x in value.split(separator) if x.strip()]


def get_env_int_list(key: str, default: List[int] = None, separator: str = ",") -> List[int]:
    str_list = get_env_list(key, separator=separator)
    if not str_list:
        return default or []
    return [int(x) for x in str_list]
