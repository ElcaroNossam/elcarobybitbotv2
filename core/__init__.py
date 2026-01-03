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

# Blockchain and TRC token
from .blockchain import (
    # Core
    TriaceloBlockchain,
    TRCWallet,
    TRCTransaction,
    TransactionType,
    CryptoNetwork,
    
    # Config
    SOVEREIGN_OWNER_ID,
    SOVEREIGN_OWNER_NAME,
    CHAIN_ID,
    CHAIN_NAME,
    TRC_SYMBOL,
    TRC_NAME,
    TRC_TOTAL_SUPPLY,
    TRC_INITIAL_CIRCULATION,
    BASE_STAKING_APY,
    LICENSE_PRICES_TRC,
    NETWORK_CONFIG,
    
    # Wallet functions
    get_trc_wallet,
    get_trc_balance,
    deposit_trc,
    pay_with_trc,
    reward_trc,
    pay_license,
    get_license_price_trc,
    
    # Currency conversion
    usdt_to_trc,
    trc_to_usdt,
    
    # Sovereign operations
    is_sovereign_owner,
    emit_tokens,
    burn_tokens,
    set_monetary_policy,
    freeze_wallet,
    unfreeze_wallet,
    distribute_staking_rewards,
    get_treasury_stats,
    transfer_from_treasury,
    get_global_stats,
    get_owner_dashboard,
    
    # Network operations
    get_supported_networks,
    get_network_config,
    get_deposit_address,
    request_withdrawal,
    confirm_deposit,
    get_withdrawal_fees,
    get_network_status,
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
    
    # Blockchain and TRC
    "TriaceloBlockchain",
    "TRCWallet",
    "TRCTransaction",
    "TransactionType",
    "CryptoNetwork",
    "SOVEREIGN_OWNER_ID",
    "SOVEREIGN_OWNER_NAME",
    "CHAIN_ID",
    "CHAIN_NAME",
    "TRC_SYMBOL",
    "TRC_NAME",
    "TRC_TOTAL_SUPPLY",
    "TRC_INITIAL_CIRCULATION",
    "BASE_STAKING_APY",
    "LICENSE_PRICES_TRC",
    "NETWORK_CONFIG",
    "get_trc_wallet",
    "get_trc_balance",
    "deposit_trc",
    "pay_with_trc",
    "reward_trc",
    "pay_license",
    "get_license_price_trc",
    "usdt_to_trc",
    "trc_to_usdt",
    "is_sovereign_owner",
    "emit_tokens",
    "burn_tokens",
    "set_monetary_policy",
    "freeze_wallet",
    "unfreeze_wallet",
    "distribute_staking_rewards",
    "get_treasury_stats",
    "transfer_from_treasury",
    "get_global_stats",
    "get_owner_dashboard",
    "get_supported_networks",
    "get_network_config",
    "get_deposit_address",
    "request_withdrawal",
    "confirm_deposit",
    "get_withdrawal_fees",
    "get_network_status",
]
