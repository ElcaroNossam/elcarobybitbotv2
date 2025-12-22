"""
ElCaro Trading Platform - Centralized Configuration
Единый конфиг для всех сервисов: Bot, WebApp, Screener, Analytics
"""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

# Load .env
BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

@dataclass
class DatabaseConfig:
    """Database paths and settings"""
    # Main user database (auth, settings, trades, licenses)
    main_db: Path = field(default_factory=lambda: BASE_DIR / "bot.db")
    
    # Analytics database (market data, candles, indicators cache)
    analytics_db: Path = field(default_factory=lambda: BASE_DIR / "data" / "analytics.db")
    
    # Screener database (real-time market snapshots)
    screener_db: Path = field(default_factory=lambda: BASE_DIR / "data" / "screener.db")
    
    # WAL mode settings
    journal_mode: str = "WAL"
    synchronous: str = "NORMAL"
    cache_size: int = -64000  # 64MB
    busy_timeout: int = 5000
    
    def ensure_dirs(self):
        """Create data directories if not exist"""
        self.analytics_db.parent.mkdir(parents=True, exist_ok=True)
        self.screener_db.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class TelegramConfig:
    """Telegram Bot settings"""
    token: str = field(default_factory=lambda: os.getenv("TELEGRAM_TOKEN", ""))
    admin_id: int = 511692487
    signal_channels: list = field(default_factory=lambda: [
        int(x.strip()) for x in os.getenv("SIGNAL_CHANNEL_IDS", "").split(",") if x.strip()
    ])
    webhook_url: Optional[str] = field(default_factory=lambda: os.getenv("WEBHOOK_URL"))


@dataclass
class WebAppConfig:
    """FastAPI WebApp settings"""
    host: str = "0.0.0.0"
    port: int = 8765
    reload: bool = field(default_factory=lambda: os.getenv("ENV", "dev") == "dev")
    workers: int = 1
    
    # CORS
    allow_origins: list = field(default_factory=lambda: ["*"])
    
    # Session - SECRET_KEY must be set in environment for production
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY") or os.urandom(32).hex())


@dataclass  
class ScreenerConfig:
    """Real-time Screener settings"""
    # Update intervals (seconds)
    ticker_interval: float = 3.0  # How often to update tickers
    liquidation_interval: float = 1.0  # Liquidations stream
    orderbook_interval: float = 2.0  # Order book updates
    
    # Binance WebSocket
    binance_ws_url: str = "wss://fstream.binance.com/ws"
    binance_api_url: str = "https://fapi.binance.com"
    
    # Limits
    max_symbols: int = 200
    top_symbols_count: int = 50
    
    # Thresholds for alerts
    price_change_alert: float = 5.0  # % change for notification
    volume_spike_multiplier: float = 3.0  # Volume spike detection
    large_liquidation_usd: float = 100000  # $100k+ liquidation alert


@dataclass
class AnalyticsConfig:
    """Analytics and indicator settings"""
    # Candle cache settings
    candle_cache_hours: int = 24 * 7  # Keep 1 week of candles
    indicator_cache_minutes: int = 5
    
    # Default indicator periods
    rsi_period: int = 14
    bb_period: int = 20
    bb_std: float = 2.0
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    atr_period: int = 14
    
    # Backtest settings
    default_initial_capital: float = 10000.0
    default_fee_percent: float = 0.04


@dataclass
class PaymentConfig:
    """Payment settings (TON, Stars)"""
    ton_wallet: str = field(default_factory=lambda: os.getenv("TON_WALLET", ""))
    ton_api_key: str = field(default_factory=lambda: os.getenv("TON_API_KEY", ""))
    
    # Revenue share
    marketplace_fee_percent: float = 50.0  # Platform takes 50%
    
    # Prices
    premium_price_ton: float = 50.0
    premium_price_stars: int = 2500


@dataclass
class Settings:
    """Main settings container"""
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    webapp: WebAppConfig = field(default_factory=WebAppConfig)
    screener: ScreenerConfig = field(default_factory=ScreenerConfig)
    analytics: AnalyticsConfig = field(default_factory=AnalyticsConfig)
    payment: PaymentConfig = field(default_factory=PaymentConfig)
    
    # Environment
    env: str = field(default_factory=lambda: os.getenv("ENV", "dev"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "0") == "1")
    
    def __post_init__(self):
        self.db.ensure_dirs()


# Singleton instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get or create settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Quick access
settings = get_settings()
