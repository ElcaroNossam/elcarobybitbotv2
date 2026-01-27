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
    AsyncLRUCache,
    UserPartitionedCache,
    cached,
    async_cached,
    async_cached_with_lock,
    user_cached,
    user_config_cache,
    price_cache,
    symbol_info_cache,
    api_response_cache,
    balance_cache,
    position_cache,
    order_cache,
    market_data_cache,
    credentials_cache,
    async_balance_cache,
    async_position_cache,
    user_strategy_cache,
    user_context_cache,
    invalidate_user_caches,
    invalidate_position_cache,
    invalidate_balance_cache,
    invalidate_on_trade_async,
    get_all_cache_stats,
    periodic_cache_cleanup,
)

# Pool Manager (unified connection pooling)
from .pool_manager import (
    UnifiedPoolManager,
    CircuitBreaker,
    CircuitState,
    RetryConfig,
    PoolMetrics,
    get_pool_manager,
)

# User Context (thread/async-safe multitenancy)
from .user_context import (
    TradingContext,
    user_context,
    get_trading_context,
    require_trading_context,
    current_user_id,
    current_exchange,
    current_account_type,
    with_user_context,
    ContextLoggerAdapter,
)

# Batch Operations (high-performance bulk queries)
from .batch_operations import (
    BatchResult,
    BatchSummary,
    batch_fetch_positions,
    batch_fetch_user_settings,
    batch_fetch_active_users,
    parallel_process_users,
    chunked_process,
    MonitoringCycleStats,
    MonitoringStats,
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

# Blockchain and ELC token
# Task management
from .tasks import (
    safe_create_task,
    create_task_safe,
    fire_and_forget,
    gather_with_exceptions,
    get_active_background_tasks,
    cancel_all_background_tasks,
)

# Optimizations (added Jan 27, 2026)
from .optimizations import (
    BoundedDict,
    TTLBoundedDict,
    run_in_executor,
    sync_to_async,
    log_exceptions,
    CacheCleanupScheduler,
    cache_cleanup_scheduler,
    metrics as opt_metrics,
    batch_query,
    retry_with_backoff,
)

from .blockchain import (
    # Core
    EnlikoBlockchain,
    ELCWallet,
    ELCTransaction,
    TransactionType,
    CryptoNetwork,
    
    # Config
    SOVEREIGN_OWNER_ID,
    SOVEREIGN_OWNER_NAME,
    CHAIN_ID,
    CHAIN_NAME,
    ELC_SYMBOL,
    ELC_NAME,
    ELC_TOTAL_SUPPLY,
    ELC_INITIAL_CIRCULATION,
    BASE_STAKING_APY,
    LICENSE_PRICES_ELC,
    NETWORK_CONFIG,
    GLOBAL_USD_RATES,
    
    # Price functions
    calculate_global_usd_index,
    get_elc_usd_rate,
    get_elc_price_info,
    
    # Wallet functions
    get_elc_wallet,
    get_elc_balance,
    deposit_elc,
    pay_with_elc,
    reward_elc,
    pay_license,
    get_license_price_elc,
    
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
    "AsyncLRUCache",
    "UserPartitionedCache",
    "cached",
    "async_cached",
    "async_cached_with_lock",
    "user_cached",
    "user_config_cache",
    "price_cache",
    "symbol_info_cache",
    "api_response_cache",
    "balance_cache",
    "position_cache",
    "order_cache",
    "market_data_cache",
    "credentials_cache",
    "async_balance_cache",
    "async_position_cache",
    "user_strategy_cache",
    "user_context_cache",
    "invalidate_user_caches",
    "invalidate_position_cache",
    "invalidate_balance_cache",
    "invalidate_on_trade_async",
    "get_all_cache_stats",
    "periodic_cache_cleanup",
    
    # Pool Manager
    "UnifiedPoolManager",
    "CircuitBreaker",
    "CircuitState",
    "RetryConfig",
    "PoolMetrics",
    "get_pool_manager",
    
    # User Context
    "TradingContext",
    "user_context",
    "get_trading_context",
    "require_trading_context",
    "current_user_id",
    "current_exchange",
    "current_account_type",
    "with_user_context",
    "ContextLoggerAdapter",
    
    # Batch Operations
    "BatchResult",
    "BatchSummary",
    "batch_fetch_positions",
    "batch_fetch_user_settings",
    "batch_fetch_active_users",
    "parallel_process_users",
    "chunked_process",
    "MonitoringCycleStats",
    "MonitoringStats",
    
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
    
    # Blockchain and ELC
    "EnlikoBlockchain",
    "ELCWallet",
    "ELCTransaction",
    "TransactionType",
    "CryptoNetwork",
    "SOVEREIGN_OWNER_ID",
    "SOVEREIGN_OWNER_NAME",
    "CHAIN_ID",
    "CHAIN_NAME",
    "ELC_SYMBOL",
    "ELC_NAME",
    "ELC_TOTAL_SUPPLY",
    "ELC_INITIAL_CIRCULATION",
    "BASE_STAKING_APY",
    "LICENSE_PRICES_ELC",
    "NETWORK_CONFIG",
    "GLOBAL_USD_RATES",
    "calculate_global_usd_index",
    "get_elc_usd_rate",
    "get_elc_price_info",
    "get_elc_wallet",
    "get_elc_balance",
    "deposit_elc",
    "pay_with_elc",
    "reward_elc",
    "pay_license",
    "get_license_price_elc",
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
    
    # Task management
    "safe_create_task",
    "create_task_safe",
    "fire_and_forget",
    "gather_with_exceptions",
    "get_active_background_tasks",
    "cancel_all_background_tasks",
    
    # Optimizations (added Jan 27, 2026)
    "BoundedDict",
    "TTLBoundedDict",
    "run_in_executor",
    "sync_to_async",
    "log_exceptions",
    "CacheCleanupScheduler",
    "cache_cleanup_scheduler",
    "opt_metrics",
    "batch_query",
    "retry_with_backoff",
]
