"""
Core module for Bybit Demo Trading Bot

Provides:
- Exception hierarchy for consistent error handling
- Configuration management
- Caching system with LRU and TTL support
- Rate limiting with token bucket algorithm
- Connection pooling for exchange clients
- Metrics and monitoring
- Unified exchange client interface
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

# Caching
from .cache import (
    LRUCache,
    cached,
    async_cached,
    user_config_cache,
    price_cache,
    symbol_info_cache,
    api_response_cache,
    balance_cache,
    position_cache,
    order_cache,
    market_data_cache,
    credentials_cache,
    invalidate_user_caches,
    invalidate_position_cache,
    invalidate_balance_cache,
    get_all_cache_stats,
    periodic_cache_cleanup,
)

# Rate limiting
from .rate_limiter import (
    TokenBucket,
    RateLimiter,
    BybitRateLimiter,
    HyperLiquidRateLimiter,
    bybit_limiter,
    hl_limiter,
    rate_limited,
)

# Connection pooling
from .connection_pool import (
    ConnectionPool,
    connection_pool,
    get_cached_client,
    on_credentials_changed,
)

# Metrics
from .metrics import (
    metrics,
    Counter,
    Gauge,
    Histogram,
    Timer,
    AsyncTimer,
    track_latency,
    count_calls,
    count_errors,
    get_health_status,
)

# Unified exchange client
from .exchange_client import (
    ExchangeType,
    AccountMode,
    ExchangeCredentials,
    ExchangeResult,
    UnifiedExchangeClient,
    get_exchange_client,
    create_credentials_from_config,
    invalidate_client,
    clear_auth_error_cache,
)

__all__ = [
    # Exceptions
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
    
    # Config
    "Config",
    "get_config",
    
    # Caching
    "LRUCache",
    "cached",
    "async_cached",
    "user_config_cache",
    "price_cache",
    "symbol_info_cache",
    "api_response_cache",
    "balance_cache",
    "position_cache",
    "order_cache",
    "market_data_cache",
    "credentials_cache",
    "invalidate_user_caches",
    "invalidate_position_cache",
    "invalidate_balance_cache",
    "get_all_cache_stats",
    "periodic_cache_cleanup",
    
    # Rate limiting
    "TokenBucket",
    "RateLimiter",
    "BybitRateLimiter",
    "HyperLiquidRateLimiter",
    "bybit_limiter",
    "hl_limiter",
    "rate_limited",
    
    # Connection pooling
    "ConnectionPool",
    "connection_pool",
    "get_cached_client",
    "on_credentials_changed",
    
    # Metrics
    "metrics",
    "Counter",
    "Gauge",
    "Histogram",
    "Timer",
    "AsyncTimer",
    "track_latency",
    "count_calls",
    "count_errors",
    "get_health_status",
    
    # Unified exchange client
    "ExchangeType",
    "AccountMode",
    "ExchangeCredentials",
    "ExchangeResult",
    "UnifiedExchangeClient",
    "get_exchange_client",
    "create_credentials_from_config",
    "invalidate_client",
    "clear_auth_error_cache",
]
