# © 2025 Illia Teslenko. All rights reserved. Proprietary license. Unauthorized use prohibited.
from __future__ import annotations

import json
import time
import threading
import os
import logging
from pathlib import Path
from typing import Any, Optional

from coin_params import DEFAULT_TP_PCT, DEFAULT_SL_PCT, DEFAULT_LANG

# ═══════════════════════════════════════════════════════════════════════════════════
# DATABASE: PostgreSQL ONLY (Full Migration - January 2026)
# ═══════════════════════════════════════════════════════════════════════════════════
_logger = logging.getLogger(__name__)
_logger.info("🐘 Using PostgreSQL database (FULL MIGRATION)")

# Import ALL PostgreSQL functions from core module
from core.db_postgres import (
    get_pool, get_conn, execute, execute_one, execute_scalar, execute_write,
    pg_init_db,  # PostgreSQL schema initialization
    pg_get_user, pg_ensure_user, pg_set_user_field, pg_get_user_field,
    pg_get_all_users, pg_get_active_users, pg_get_allowed_users,
    pg_add_active_position, pg_get_active_positions, pg_get_active_position,
    pg_remove_active_position, pg_update_position_field,
    pg_add_trade_log, pg_get_trade_logs, pg_get_pnl_stats,
    pg_add_signal, pg_get_signals,
    pg_get_user_strategy_settings, pg_set_user_strategy_settings,
    pg_get_trading_mode, pg_get_active_trading_users,
    pg_get_user_config,
    pg_get_user_credentials, pg_get_all_user_credentials,
    pg_get_exchange_type, pg_get_hl_credentials, pg_is_hl_enabled,
    pg_is_bybit_enabled, pg_set_bybit_enabled,
    pg_get_routing_policy, pg_set_routing_policy,
    pg_get_user_trading_context, pg_get_active_account_types,
    pg_get_strategy_account_types,
    pg_get_strategy_settings_db, pg_get_strategy_settings,
    pg_set_strategy_setting, pg_get_effective_settings,
    pg_get_hl_strategy_settings, pg_set_hl_strategy_setting,
    pg_get_hl_effective_settings, pg_should_show_account_switcher,
    pg_update_user_info, pg_set_trading_mode, pg_set_hl_enabled,
    pg_delete_user, pg_sync_position_entry_price, pg_set_user_credentials,
    pg_set_pending_input, pg_get_pending_input, pg_clear_pending_input,
)

# Legacy compatibility - no longer used but kept for imports
DB_FILE = Path("bot.db")

# ------------------------------------------------------------------------------------
# JSON PARSING HELPER (PostgreSQL returns JSON as dict, not string)
# ------------------------------------------------------------------------------------
def _safe_json_loads(value, default=None):
    """Safely parse JSON - handles both string and already-parsed dict/list from PostgreSQL."""
    if value is None:
        return default if default is not None else {}
    if isinstance(value, (dict, list)):
        return value  # Already parsed by psycopg2
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return default if default is not None else {}
    return default if default is not None else {}

# ------------------------------------------------------------------------------------
# In-memory caches for frequently accessed data
# ------------------------------------------------------------------------------------
_user_config_cache: dict[int, tuple[float, dict]] = {}  # user_id -> (timestamp, config)
_all_users_cache: tuple[float, list[int]] = (0.0, [])  # (timestamp, user_ids)
_active_users_cache: tuple[float, list[int]] = (0.0, [])  # users with API keys
CACHE_TTL = 30.0  # seconds
_cache_lock = threading.RLock()  # SECURITY: Lock for thread-safe cache access

def invalidate_user_cache(user_id: int = None):
    """Invalidate cache for a user or all users."""
    global _all_users_cache, _active_users_cache
    with _cache_lock:
        if user_id:
            _user_config_cache.pop(user_id, None)
        else:
            _user_config_cache.clear()
        _all_users_cache = (0.0, [])
        _active_users_cache = (0.0, [])

# --- Полезные константы/whitelist'ы -------------------------------------------------
USER_FIELDS_WHITELIST = {
    "username",  # telegram username
    "first_name", "last_name",  # telegram names
    "api_key", "api_secret",
    # Demo/Real API keys
    "demo_api_key", "demo_api_secret",
    "real_api_key", "real_api_secret",
    "trading_mode",  # 'demo', 'real', 'both'
    "percent", "coins", "limit_enabled",
    "trade_oi", "trade_rsi_bb",
    "tp_percent", "sl_percent", "tp_pct", "sl_pct",  # aliases
    "leverage",  # global leverage
    "use_atr", "lang",
    # ATR settings (global) - fallback when strategy setting is NULL
    "atr_periods",       # candles for ATR calculation (default 7)
    "atr_multiplier_sl", # ATR multiplier for SL distance (default 1.0)
    "atr_trigger_pct",   # % profit to activate ATR trailing (default 2.0)
    "atr_step_pct",      # % step to move SL (default 0.5)
    "direction",         # 'all', 'long', 'short' - global direction filter
    "global_order_type",  # 'market', 'limit' - global default order type
    "exchange_type",  # 'bybit', 'hyperliquid'
    # стратегии/пороги (опционально)
    "strategies_enabled", "strategies_order",
    "rsi_lo", "rsi_hi", "bb_touch_k",
    "oi_min_pct", "price_min_pct", "limit_only_default",
    "trade_scryptomera",
    "trade_scalper",
    "trade_elcaro",
    "trade_fibonacci",
    "trade_manual",  # 0/1 - monitor and manage manual positions (set SL/TP/ATR)
    # Enable flags (webapp format - aliases for trade_* fields)
    "enable_scryptomera", "enable_elcaro", "enable_scalper",
    "enable_fibonacci", "enable_rsi_bb", "enable_oi", "enable_wyckoff",
    # настройки по стратегиям (JSON)
    "strategy_settings",
    # DCA настройки
    "dca_enabled",  # 0/1 - включён ли DCA добор для фьючерсов (по умолчанию 0)
    "dca_pct_1", "dca_pct_2",
    # Spot trading
    "spot_enabled",  # 0/1 - включена ли спот торговля
    "spot_settings",  # JSON с настройками спот DCA
    # Limit ladder (лимитные доборы)
    "limit_ladder_enabled",  # 0/1 - включены ли лимитные доборы
    "limit_ladder_count",    # количество лимиток (1-5)
    "limit_ladder_settings", # JSON: [{"pct_from_entry": 2, "pct_of_deposit": 10}, ...]
    # доступ/согласие
    "is_allowed", "is_banned", "terms_accepted", "disclaimer_accepted",
    "guide_sent",  # 0/1 - отправлен ли PDF гайд
    "live_enabled",  # 0/1 - разрешена ли торговля на Real/Mainnet
    # License info (добавлено для admin API)
    "license_type", "license_expires", "current_license", "is_lifetime",
    # для совместимости с текущим кодом бота
    "first_seen_ts", "last_seen_ts",
    # Last viewed account type (for UI persistence)
    "last_viewed_account",  # 'demo', 'real', 'testnet', 'mainnet' - persists across views
    # HyperLiquid settings
    "hl_testnet",  # 0/1 - testnet or mainnet (legacy, for active context)
    "hl_enabled",  # 0/1 - HL trading enabled
    "hl_private_key",  # HyperLiquid private key (legacy, will migrate to testnet/mainnet)
    "hl_wallet_address",  # HyperLiquid wallet address (legacy)
    "hl_vault_address",  # HyperLiquid vault address
    # Separate HL testnet/mainnet credentials
    "hl_testnet_private_key",  # HL testnet private key
    "hl_testnet_wallet_address",  # HL testnet wallet address
    "hl_mainnet_private_key",  # HL mainnet private key
    "hl_mainnet_wallet_address",  # HL mainnet wallet address
    # Margin mode settings
    "bybit_enabled",  # 0/1 - is Bybit trading enabled
    "bybit_margin_mode",  # 'cross' or 'isolated' for Bybit
    "hl_margin_mode",  # 'cross' or 'isolated' for HyperLiquid
    # Routing policy
    "routing_policy",  # NULL=use trading_mode, 'all_enabled'=trade on all configured exchanges
    # Coins group per exchange (simplified settings - Feb 10, 2026)
    "bybit_coins_group",  # 'ALL', 'TOP', 'VOLATILE' for Bybit
    "hl_coins_group",  # 'ALL', 'TOP', 'VOLATILE' for HyperLiquid
    # Per-exchange trading settings (Feb 10, 2026)
    "bybit_leverage",  # Global leverage for Bybit (default 10)
    "bybit_order_type",  # 'market' or 'limit' for Bybit
    "bybit_coins_filter",  # 'ALL', 'TOP', 'VOLATILE' for Bybit
    "hl_leverage",  # Global leverage for HyperLiquid (default 10)
    "hl_order_type",  # 'market' or 'limit' for HyperLiquid
    "hl_coins_filter",  # 'ALL', 'TOP', 'VOLATILE' for HyperLiquid
    # Admin controls
    "trading_paused",  # 0/1 - admin can pause trading for user
    # Auto-close settings per exchange (Feb 21, 2026)
    "bybit_auto_close_enabled",  # 0/1 - auto-close all Bybit positions at specific time
    "bybit_auto_close_time",  # HH:MM format (UTC)
    "bybit_auto_close_timezone",  # Timezone for auto-close (default UTC)
    "hl_auto_close_enabled",  # 0/1 - auto-close all HL positions at specific time
    "hl_auto_close_time",  # HH:MM format (UTC)
    "hl_auto_close_timezone",  # Timezone for auto-close (default UTC)
}


def _normalize_both_account_type(account_type: str | None, exchange: str = 'bybit') -> str | None:
    """
    Normalize account_type for API and DB queries.
    
    Handles:
    - 'both' → default safe type per exchange
    - Cross-exchange mapping: demo→testnet, real→mainnet for HL (and vice versa)
    
    Args:
        account_type: 'demo', 'real', 'both', 'testnet', 'mainnet', or None
        exchange: 'bybit' or 'hyperliquid'
    
    Returns:
        Normalized account_type or None (if input was None)
    """
    if account_type is None:
        return None
    if exchange == 'hyperliquid':
        mapping = {'both': 'testnet', 'demo': 'testnet', 'real': 'mainnet'}
        return mapping.get(account_type, account_type)
    else:
        mapping = {'both': 'demo', 'testnet': 'demo', 'mainnet': 'real'}
        return mapping.get(account_type, account_type)


# ------------------------------------------------------------------------------------
# PostgreSQL connection helpers (re-exported from core.db_postgres)
# ------------------------------------------------------------------------------------
# get_conn() and release_conn() are now PostgreSQL-based from core.db_postgres

def release_conn(conn):
    """Release connection back to pool (compatibility wrapper)."""
    # In PostgreSQL mode, connections are managed via context manager
    # This is kept for API compatibility
    pass


# PERFORMANCE: Cache for schema introspection (columns rarely change)
_schema_cache: dict[str, set[str]] = {}  # table_name -> set of column names
_schema_cache_ts: float = 0.0
SCHEMA_CACHE_TTL = 300.0  # 5 minutes - balance between performance and freshness after migrations


def invalidate_schema_cache():
    """Force refresh schema cache - call after migrations."""
    global _schema_cache, _schema_cache_ts
    _schema_cache = {}
    _schema_cache_ts = 0.0
    _logger.info("Schema cache invalidated")


def _refresh_schema_cache():
    """Refresh the schema cache for all tables."""
    global _schema_cache, _schema_cache_ts
    _schema_cache = {}
    rows = execute("""
        SELECT table_name, column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public'
    """)
    for row in rows:
        # Handle both dict (RealDictCursor) and tuple formats
        if isinstance(row, dict):
            table = row.get('table_name')
            col = row.get('column_name')
        else:
            table = row[0]
            col = row[1]
        if table and col:
            if table not in _schema_cache:
                _schema_cache[table] = set()
            _schema_cache[table].add(col)
    _schema_cache_ts = time.time()
    _logger.info(f"Schema cache refreshed: {len(_schema_cache)} tables, users has {len(_schema_cache.get('users', set()))} columns")


def _col_exists_pg(table: str, col: str) -> bool:
    """Check if column exists in PostgreSQL table. CACHED for performance."""
    global _schema_cache_ts
    now = time.time()
    if now - _schema_cache_ts > SCHEMA_CACHE_TTL or not _schema_cache:
        _refresh_schema_cache()
    return col in _schema_cache.get(table, set())


def _table_exists_pg(table: str) -> bool:
    """Check if table exists in PostgreSQL."""
    result = execute_one("""
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = %s
    """, (table,))
    return result is not None


# Legacy aliases for compatibility
def _col_exists(conn, table: str, col: str) -> bool:
    """Legacy wrapper - conn parameter ignored in PostgreSQL."""
    return _col_exists_pg(table, col)


def _table_exists(conn, table: str) -> bool:
    """Legacy wrapper - conn parameter ignored in PostgreSQL."""
    return _table_exists_pg(table)


# ------------------------------------------------------------------------------------
# Schema & Migrations (PostgreSQL)
# ------------------------------------------------------------------------------------
def init_db():
    """Initialize PostgreSQL database schema.
    
    Delegates to pg_init_db() from core.db_postgres which contains
    the complete PostgreSQL schema with proper syntax (SERIAL, TEXT, etc.).
    """
    _logger.info("🐘 Initializing PostgreSQL database via pg_init_db()...")
    pg_init_db()
    _logger.info("✅ PostgreSQL database initialized successfully")



# ------------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------------
def ensure_user(user_id: int):
    """Гарантирует наличие записи пользователя. Нужен перед любыми UPDATE."""
    execute_write(
        "INSERT INTO users(user_id) VALUES(%s) ON CONFLICT (user_id) DO NOTHING",
        (user_id,),
    )

def update_user_info(user_id: int, username: str = None, first_name: str = None):
    """Updates user info (username, first_name) if provided"""
    ensure_user(user_id)
    updates = []
    params = []
    
    if username is not None:
        updates.append("username = %s")
        params.append(username)
        # Also update telegram_username for 2FA login
        updates.append("telegram_username = %s")
        params.append(username)
    
    if first_name is not None:
        updates.append("first_name = %s")
        params.append(first_name)
    
    if updates:
        params.append(user_id)
        execute_write(
            f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s",
            tuple(params)
        )

def delete_user(user_id: int):
    """
    Полностью удаляет пользователя.
    Связанные записи чистятся каскадом (active_positions, trade_logs, pyramids, pending_limit_orders).
    """
    execute_write("DELETE FROM users WHERE user_id=%s", (user_id,))

def ban_user(user_id: int):
    """Блокировка пользователя: бан + снятие одобрения."""
    ensure_user(user_id)
    execute_write("UPDATE users SET is_banned=1, is_allowed=0 WHERE user_id=%s", (user_id,))

def allow_user(user_id: int):
    """Одобрение пользователя: снимаем бан и ставим флаг допуска."""
    ensure_user(user_id)
    execute_write("UPDATE users SET is_allowed=1, is_banned=0 WHERE user_id=%s", (user_id,))

# ------------------------------------------------------------------------------------
# Users
# ------------------------------------------------------------------------------------
def set_user_credentials(user_id: int, api_key: str, api_secret: str, account_type: str = "demo"):
    """Set API credentials for demo or real account.
    
    Args:
        user_id: Telegram user ID
        api_key: Bybit API key
        api_secret: Bybit API secret
        account_type: 'demo' or 'real'
    """
    ensure_user(user_id)
    if account_type == "real":
        key_col, secret_col = "real_api_key", "real_api_secret"
    else:
        key_col, secret_col = "demo_api_key", "demo_api_secret"
    
    with get_conn() as conn:
        conn.execute(
            f"UPDATE users SET {key_col}=?, {secret_col}=? WHERE user_id=?",
            (api_key, api_secret, user_id),
        )
        conn.commit()
    
    # Clear expired API keys cache for this user (they updated their keys)
    try:
        from core import invalidate_client
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(invalidate_client(user_id, account_type=account_type))
    except Exception as e:
        _logger.debug(f"Could not invalidate client cache: {e}")  # Expected if core not fully loaded

def get_user_credentials(user_id: int, account_type: str = None) -> tuple[str | None, str | None]:
    """Get API credentials for specified account type.
    
    Args:
        user_id: Telegram user ID
        account_type: 'demo', 'real', or None (auto-detect from trading_mode)
    
    Returns:
        Tuple of (api_key, api_secret)
    """
    with get_conn() as conn:
        row = conn.execute(
            "SELECT demo_api_key, demo_api_secret, real_api_key, real_api_secret, trading_mode FROM users WHERE user_id=?",
            (user_id,),
        ).fetchone()
    
    if not row:
        return (None, None)
    
    demo_key, demo_secret, real_key, real_secret, trading_mode = row
    
    # CRITICAL FIX: Normalize 'both' mode to 'demo' since API needs specific mode
    if account_type == 'both':
        account_type = 'demo'
    
    # If account_type specified, use that
    if account_type == "real":
        return (real_key, real_secret)
    elif account_type == "demo":
        return (demo_key, demo_secret)
    
    # Auto-detect based on trading_mode
    if trading_mode == "real":
        return (real_key, real_secret)
    else:
        return (demo_key, demo_secret)

def get_all_user_credentials(user_id: int) -> dict:
    """Get all API credentials, trading mode and exchange type for a user.
    
    Returns:
        Dict with demo_api_key, demo_api_secret, real_api_key, real_api_secret, 
        trading_mode, exchange_type, last_viewed_account, lang
    """
    with get_conn() as conn:
        row = conn.execute(
            "SELECT demo_api_key, demo_api_secret, real_api_key, real_api_secret, trading_mode, exchange_type, last_viewed_account, lang FROM users WHERE user_id=?",
            (user_id,),
        ).fetchone()
    
    if not row:
        return {
            "demo_api_key": None, "demo_api_secret": None,
            "real_api_key": None, "real_api_secret": None,
            "trading_mode": "demo",
            "exchange_type": "bybit",
            "last_viewed_account": None,
            "lang": "en"
        }
    
    return {
        "demo_api_key": row[0],
        "demo_api_secret": row[1],
        "real_api_key": row[2],
        "real_api_secret": row[3],
        "trading_mode": row[4] or "demo",
        "exchange_type": row[5] or "bybit",
        "last_viewed_account": row[6],
        "lang": row[7] or "en"
    }

def set_trading_mode(user_id: int, mode: str):
    """Set trading mode: 'demo', 'real', or 'both'."""
    if mode not in ("demo", "real", "both"):
        raise ValueError(f"Invalid trading mode: {mode}")
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute("UPDATE users SET trading_mode=? WHERE user_id=?", (mode, user_id))
        conn.commit()

def get_trading_mode(user_id: int) -> str:
    """Get current trading mode."""
    with get_conn() as conn:
        row = conn.execute("SELECT trading_mode FROM users WHERE user_id=?", (user_id,)).fetchone()
    return row[0] if row and row[0] else "demo"


def get_last_viewed_account(user_id: int, exchange: str = 'bybit') -> str:
    """Get last viewed account type for UI persistence.
    
    This is separate from trading_mode - it's just for UI display.
    User can VIEW demo positions while TRADING on real.
    
    Returns:
        'demo' or 'real' for Bybit
        'testnet' or 'mainnet' for HyperLiquid
    """
    with get_conn() as conn:
        row = conn.execute(
            "SELECT last_viewed_account, trading_mode, hl_testnet FROM users WHERE user_id=?", 
            (user_id,)
        ).fetchone()
    
    if not row:
        return "demo" if exchange == "bybit" else "testnet"
    
    last_viewed = row[0]
    trading_mode = row[1] or "demo"
    hl_testnet = row[2]
    
    # If last_viewed is set and matches exchange, use it
    if last_viewed:
        if exchange == "bybit" and last_viewed in ("demo", "real"):
            return last_viewed
        if exchange == "hyperliquid" and last_viewed in ("testnet", "mainnet"):
            return last_viewed
    
    # Default based on trading mode, API keys availability, or hl_testnet
    if exchange == "bybit":
        if trading_mode == "both":
            # FIX: Prefer 'real' if user has real API keys configured
            creds = get_all_user_credentials(user_id)
            if creds.get("real_api_key") and creds.get("real_api_secret"):
                return "real"
            return "demo"
        return trading_mode if trading_mode in ("demo", "real") else "demo"
    else:
        return "testnet" if hl_testnet else "mainnet"


def set_last_viewed_account(user_id: int, account_type: str):
    """Save last viewed account type for UI persistence."""
    if account_type not in ("demo", "real", "testnet", "mainnet"):
        return
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET last_viewed_account=? WHERE user_id=?", 
            (account_type, user_id)
        )
        conn.commit()
    invalidate_user_cache(user_id)


def should_show_account_switcher(user_id: int) -> bool:
    """Check if user should see Demo/Real switcher.
    
    Returns True if user has BOTH demo AND real API keys configured.
    This allows viewing balances/positions/orders on both accounts
    regardless of which account they trade on.
    """
    creds = get_all_user_credentials(user_id)
    
    # Check if both API keys exist
    has_demo = bool(creds.get("demo_api_key") and creds.get("demo_api_secret"))
    has_real = bool(creds.get("real_api_key") and creds.get("real_api_secret"))
    
    return has_demo and has_real


def should_show_hl_network_switcher(user_id: int) -> bool:
    """Check if user should see Testnet/Mainnet switcher for HyperLiquid.
    
    Returns True if user has BOTH testnet AND mainnet keys configured.
    """
    hl_creds = get_hl_credentials(user_id)
    
    has_testnet = bool(hl_creds.get("hl_testnet_private_key"))
    has_mainnet = bool(hl_creds.get("hl_mainnet_private_key"))
    
    # Also check legacy key as fallback
    if not has_testnet and not has_mainnet:
        return False
    
    return has_testnet and has_mainnet


def get_effective_trading_mode(user_id: int) -> str:
    """
    Get effective trading mode based on enabled strategies' settings.
    
    Uses get_strategy_account_types() to get actual account types each strategy trades on,
    then determines what to display in positions.
    
    Returns:
    - 'demo' if all enabled strategies trade only on demo
    - 'real' if all enabled strategies trade only on real
    - 'both' if strategies trade on mixed accounts
    
    Falls back to global trading_mode if no strategies are enabled.
    """
    with get_conn() as conn:
        row = conn.execute("""
            SELECT trading_mode,
                   trade_scryptomera, trade_scalper, trade_elcaro, 
                   trade_fibonacci, trade_oi, trade_rsi_bb
            FROM users WHERE user_id=?
        """, (user_id,)).fetchone()
    
    if not row:
        return "demo"
    
    global_mode = row[0] or "demo"
    
    # Check which strategies are enabled
    enabled_strategies = []
    if row[1]:  # trade_scryptomera
        enabled_strategies.append("scryptomera")
    if row[2]:  # trade_scalper
        enabled_strategies.append("scalper")
    if row[3]:  # trade_elcaro
        enabled_strategies.append("elcaro")
    if row[4]:  # trade_fibonacci
        enabled_strategies.append("fibonacci")
    if row[5]:  # trade_oi
        enabled_strategies.append("oi")
    if row[6]:  # trade_rsi_bb
        enabled_strategies.append("rsi_bb")
    
    # If no strategies enabled, use global mode
    if not enabled_strategies:
        return global_mode
    
    # Collect all account types from enabled strategies
    all_accounts = set()
    for strat in enabled_strategies:
        accounts = get_strategy_account_types(user_id, strat)
        all_accounts.update(accounts)
    
    # Normalize to demo/real (handle testnet/mainnet for HyperLiquid)
    normalized = set()
    for acc in all_accounts:
        if acc in ("demo", "testnet"):
            normalized.add("demo")
        elif acc in ("real", "mainnet"):
            normalized.add("real")
    
    # Determine effective mode
    if not normalized:
        return global_mode
    elif normalized == {"demo"}:
        return "demo"
    elif normalized == {"real"}:
        return "real"
    else:
        return "both"


def get_user_trading_context(user_id: int) -> dict:
    """
    Get current trading context for user: exchange and primary account_type.
    
    For Bybit: account_type is demo/real based on trading_mode
    For HyperLiquid: account_type is testnet/mainnet based on hl_testnet setting
    
    Returns:
        {
            "exchange": "bybit" | "hyperliquid",
            "account_type": "demo" | "real" | "testnet" | "mainnet",
            "trading_mode": "demo" | "real" | "both"
        }
    """
    with get_conn() as conn:
        row = conn.execute("""
            SELECT exchange_type, trading_mode, hl_testnet
            FROM users WHERE user_id = ?
        """, (user_id,)).fetchone()
    
    if not row:
        return {"exchange": "bybit", "account_type": "demo", "trading_mode": "demo"}
    
    exchange = row[0] or "bybit"
    trading_mode = row[1] or "demo"
    hl_testnet = bool(row[2]) if row[2] is not None else False
    
    if exchange == "hyperliquid":
        # For HL: testnet/mainnet based on hl_testnet setting
        account_type = "testnet" if hl_testnet else "mainnet"
    else:
        # For Bybit: demo/real based on trading_mode
        # If "both", prefer "real" as primary for settings display
        if trading_mode == "both":
            account_type = "real"  # Primary account when both enabled
        else:
            account_type = trading_mode
    
    return {
        "exchange": exchange,
        "account_type": account_type,
        "trading_mode": trading_mode
    }


def normalize_account_type(account_type: str, exchange: str = "bybit") -> str:
    """
    Normalize account type between exchanges.
    demo <-> testnet, real <-> mainnet
    """
    if exchange == "hyperliquid":
        # Normalize bybit modes to HL modes
        if account_type == "demo":
            return "testnet"
        elif account_type == "real":
            return "mainnet"
    else:
        # Normalize HL modes to Bybit modes
        if account_type == "testnet":
            return "demo"
        elif account_type == "mainnet":
            return "real"
    return account_type


def get_active_account_types(user_id: int) -> list[str]:
    """
    Get list of account types to trade on based on trading_mode and active exchange.
    
    Returns for Bybit: ['demo'], ['real'], or ['demo', 'real']
    Returns for HyperLiquid: ['testnet'], ['mainnet'], or ['testnet', 'mainnet']
    
    For HL: checks separate testnet/mainnet credentials.
    """
    exchange = get_exchange_type(user_id)
    
    if exchange == "hyperliquid":
        # For HyperLiquid, check separate testnet/mainnet credentials
        hl_creds = get_hl_credentials(user_id)
        
        # Check each credential separately
        has_testnet = bool(hl_creds.get("hl_testnet_private_key"))
        has_mainnet = bool(hl_creds.get("hl_mainnet_private_key"))
        
        # Fallback to legacy key
        if not has_testnet and not has_mainnet and hl_creds.get("hl_private_key"):
            if hl_creds.get("hl_testnet"):
                has_testnet = True
            else:
                has_mainnet = True
        
        if not has_testnet and not has_mainnet:
            return []
        
        # Get trading_mode preference
        with get_conn() as conn:
            row = conn.execute("SELECT trading_mode FROM users WHERE user_id=?", (user_id,)).fetchone()
        
        trading_mode = row[0] if row else "demo"
        trading_mode = trading_mode or "demo"
        
        result = []
        # Map trading_mode to HL account types
        if trading_mode == "both":
            if has_testnet:
                result.append("testnet")
            if has_mainnet:
                result.append("mainnet")
        elif trading_mode in ("demo", "testnet"):
            if has_testnet:
                result.append("testnet")
        else:  # real, mainnet
            if has_mainnet:
                result.append("mainnet")
        
        return result
    else:
        # For Bybit
        with get_conn() as conn:
            row = conn.execute(
                "SELECT demo_api_key, demo_api_secret, real_api_key, real_api_secret, trading_mode FROM users WHERE user_id=?",
                (user_id,),
            ).fetchone()
        
        if not row:
            return []
        
        demo_key, demo_secret, real_key, real_secret, trading_mode = row
        trading_mode = trading_mode or "demo"
        
        result = []
        
        if trading_mode == "both":
            if demo_key and demo_secret:
                result.append("demo")
            if real_key and real_secret:
                result.append("real")
        elif trading_mode == "real":
            if real_key and real_secret:
                result.append("real")
        else:  # demo
            if demo_key and demo_secret:
                result.append("demo")
        
        return result


def get_strategy_account_types(user_id: int, strategy: str) -> list[str]:
    """Get list of account types to trade on for a specific strategy.
    
    Strategy can have its own trading_mode setting:
    - 'global': use user's global trading_mode
    - 'demo'/'testnet': trade only on demo/testnet account
    - 'real'/'mainnet': trade only on real/mainnet account  
    - 'both': trade on both accounts
    
    Returns for Bybit: ['demo'], ['real'], or ['demo', 'real']
    Returns for HyperLiquid: ['testnet'], ['mainnet'], or ['testnet', 'mainnet']
    """
    # Get user's active exchange
    exchange = get_exchange_type(user_id)
    
    # Get strategy settings for current exchange context
    context = get_user_trading_context(user_id)
    strat_settings = get_strategy_settings(user_id, strategy, exchange, context["account_type"])
    strat_mode = strat_settings.get("trading_mode", "global")
    
    # If strategy uses global mode, delegate to global function
    if strat_mode == "global":
        return get_active_account_types(user_id)
    
    # Normalize mode for the active exchange
    strat_mode = normalize_account_type(strat_mode, exchange)
    
    if exchange == "hyperliquid":
        # For HyperLiquid, check separate testnet/mainnet credentials
        hl_creds = get_hl_credentials(user_id)
        has_testnet = bool(hl_creds.get("hl_testnet_private_key"))
        has_mainnet = bool(hl_creds.get("hl_mainnet_private_key"))
        
        # Fallback to legacy key
        if not has_testnet and not has_mainnet and hl_creds.get("hl_private_key"):
            if hl_creds.get("hl_testnet"):
                has_testnet = True
            else:
                has_mainnet = True
        
        if not has_testnet and not has_mainnet:
            return []
        
        result = []
        if strat_mode == "both":
            if has_testnet:
                result.append("testnet")
            if has_mainnet:
                result.append("mainnet")
        elif strat_mode in ("mainnet", "real"):
            if has_mainnet:
                result.append("mainnet")
        elif strat_mode in ("testnet", "demo"):
            if has_testnet:
                result.append("testnet")
        
        return result if result else (["mainnet"] if has_mainnet else ["testnet"])
    else:
        # For Bybit
        with get_conn() as conn:
            row = conn.execute(
                "SELECT demo_api_key, demo_api_secret, real_api_key, real_api_secret FROM users WHERE user_id=?",
                (user_id,),
            ).fetchone()
        
        if not row:
            return []
        
        demo_key, demo_secret, real_key, real_secret = row
        result = []
        
        if strat_mode == "both":
            if demo_key and demo_secret:
                result.append("demo")
            if real_key and real_secret:
                result.append("real")
        elif strat_mode in ("real", "mainnet"):
            if real_key and real_secret:
                result.append("real")
        elif strat_mode in ("demo", "testnet"):
            if demo_key and demo_secret:
                result.append("demo")
        
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTING POLICY & EXECUTION TARGETS
# ═══════════════════════════════════════════════════════════════════════════════

class RoutingPolicy:
    """Routing policy values for signal execution"""
    ACTIVE_ONLY = "active_only"                    # Only the currently selected target (UI)
    SAME_EXCHANGE_ALL_ENVS = "same_exchange_all_envs"  # Current exchange, all enabled envs
    ALL_ENABLED = "all_enabled"                    # All enabled targets (up to 4)
    CUSTOM = "custom"                              # Explicit target list from strategy


def get_routing_policy(user_id: int) -> str:
    """Get user's global routing policy."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT routing_policy FROM users WHERE user_id=?", 
            (user_id,)
        ).fetchone()
    return row[0] if row and row[0] else RoutingPolicy.SAME_EXCHANGE_ALL_ENVS


def set_routing_policy(user_id: int, policy: str):
    """Set user's global routing policy."""
    valid_policies = [
        RoutingPolicy.ACTIVE_ONLY,
        RoutingPolicy.SAME_EXCHANGE_ALL_ENVS,
        RoutingPolicy.ALL_ENABLED,
        RoutingPolicy.CUSTOM,
    ]
    if policy not in valid_policies:
        raise ValueError(f"Invalid routing policy: {policy}")
    
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET routing_policy=? WHERE user_id=?",
            (policy, user_id)
        )
        conn.commit()
    invalidate_user_cache(user_id)


def get_live_enabled(user_id: int) -> bool:
    """Check if user has explicitly enabled live/mainnet trading."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT live_enabled FROM users WHERE user_id=?",
            (user_id,)
        ).fetchone()
    return bool(row[0]) if row else False


def set_live_enabled(user_id: int, enabled: bool):
    """Set live/mainnet trading permission."""
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET live_enabled=? WHERE user_id=?",
            (bool(enabled), user_id)
        )
        conn.commit()
    invalidate_user_cache(user_id)


def get_execution_targets(
    user_id: int,
    strategy: str = None,
    override_policy: str = None
) -> list[dict]:
    """
    Get list of execution targets based on routing_policy and strategy's trading_mode.
    
    Returns list of dicts with keys: exchange, env, account_type
    
    Logic:
    1. Resolve strategy's trading_mode first (demo/real/both)
    
    2. Check routing_policy:
       - ALL_ENABLED: trade on BOTH exchanges, filtered by trading_mode:
         • demo → Bybit Demo + HL Testnet
         • real → Bybit Real + HL Mainnet
         • both → All 4 targets
       - SAME_EXCHANGE_ALL_ENVS: all account types on current exchange
       - ACTIVE_ONLY: only currently selected target
    
    3. If no special policy, use strategy's trading_mode on CURRENT exchange:
       - demo: Bybit Demo OR HL Testnet
       - real: Bybit Real OR HL Mainnet
       - both: BOTH account types on ONE exchange (Demo+Real OR Testnet+Mainnet)
    
    Safety: Filters out live targets if live_enabled=False
    """
    targets = []
    live_enabled = get_live_enabled(user_id)
    
    bybit_enabled = is_bybit_enabled(user_id)
    hl_enabled = is_hl_enabled(user_id)
    
    # Get user's current active exchange
    current_exchange = get_exchange_type(user_id)  # 'bybit' or 'hyperliquid'
    
    # FALLBACK: If exchange_type not set, auto-detect based on which exchange is enabled
    if not current_exchange:
        if hl_enabled and not bybit_enabled:
            current_exchange = "hyperliquid"
        elif bybit_enabled:
            current_exchange = "bybit"
    
    # Check routing policy (can be overridden)
    routing_policy = override_policy or get_routing_policy(user_id)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Resolve strategy's trading_mode FIRST (used by ALL routing paths)
    # ═══════════════════════════════════════════════════════════════════════════
    strat_mode = "demo"  # Default
    if strategy:
        strat_mode = get_strategy_trading_mode(user_id, strategy)
    
    # If strategy uses global, get user's global mode
    if strat_mode == "global":
        strat_mode = get_trading_mode(user_id) or "demo"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ALL_ENABLED: Trade on BOTH exchanges, but RESPECT trading_mode!
    # demo  → Bybit Demo + HL Testnet (paper accounts only)
    # real  → Bybit Real + HL Mainnet (live accounts only)
    # both  → All 4 targets: Bybit Demo + Real + HL Testnet + Mainnet
    # ═══════════════════════════════════════════════════════════════════════════
    if routing_policy == RoutingPolicy.ALL_ENABLED:
        # Determine allowed account types per exchange based on strat_mode
        if strat_mode == "both":
            bybit_allowed = {"demo", "real"}
            hl_allowed = {"testnet", "mainnet"}
        elif strat_mode in ("real", "mainnet"):
            bybit_allowed = {"real"}
            hl_allowed = {"mainnet"}
        else:  # demo/testnet (default)
            bybit_allowed = {"demo"}
            hl_allowed = {"testnet"}
        
        # Add Bybit targets filtered by strat_mode
        if bybit_enabled:
            bybit_types = _get_bybit_account_types(user_id)
            for acc_type in bybit_types:
                if acc_type not in bybit_allowed:
                    continue
                env = "paper" if acc_type == "demo" else "live"
                if env == "live" and not live_enabled:
                    continue
                targets.append({
                    "exchange": "bybit",
                    "env": env,
                    "account_type": acc_type
                })
        
        # Add HyperLiquid targets filtered by strat_mode
        if hl_enabled:
            hl_types = _get_hl_account_types(user_id)
            for acc_type in hl_types:
                if acc_type not in hl_allowed:
                    continue
                env = "paper" if acc_type == "testnet" else "live"
                if env == "live" and not live_enabled:
                    continue
                targets.append({
                    "exchange": "hyperliquid",
                    "env": env,
                    "account_type": acc_type
                })
        
        return targets
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SAME_EXCHANGE_ALL_ENVS or trading_mode based routing (default)
    # strat_mode already resolved above
    # ═══════════════════════════════════════════════════════════════════════════
    # Determine which account types to use based on mode
    # demo → demo for Bybit, testnet for HL
    # real → real for Bybit, mainnet for HL  
    # both → all configured accounts ON CURRENT ACTIVE EXCHANGE (not all exchanges!)
    
    if strat_mode == "both":
        # FIX: "both" means BOTH account types (demo+real or testnet+mainnet)
        # on the CURRENT active exchange, NOT both exchanges!
        
        if current_exchange == "bybit" and bybit_enabled:
            bybit_types = _get_bybit_account_types(user_id)
            for acc_type in bybit_types:
                env = "paper" if acc_type == "demo" else "live"
                if env == "live" and not live_enabled:
                    continue
                targets.append({
                    "exchange": "bybit",
                    "env": env,
                    "account_type": acc_type
                })
        
        elif current_exchange == "hyperliquid" and hl_enabled:
            hl_types = _get_hl_account_types(user_id)
            for acc_type in hl_types:
                env = "paper" if acc_type == "testnet" else "live"
                if env == "live" and not live_enabled:
                    continue
                targets.append({
                    "exchange": "hyperliquid",
                    "env": env,
                    "account_type": acc_type
                })
    
    elif strat_mode in ("real", "mainnet"):
        # Real/Mainnet mode - use CURRENT active exchange only
        if current_exchange == "bybit" and bybit_enabled:
            # Check if real credentials exist
            creds = get_all_user_credentials(user_id)
            if creds.get("real_api_key") and creds.get("real_api_secret"):
                if live_enabled:  # Only add if live trading is enabled
                    targets.append({
                        "exchange": "bybit",
                        "env": "live",
                        "account_type": "real"
                    })
        
        elif current_exchange == "hyperliquid" and hl_enabled:
            hl_creds = get_hl_credentials(user_id)
            has_mainnet = bool(hl_creds.get("hl_mainnet_private_key"))
            if not has_mainnet and hl_creds.get("hl_private_key") and not hl_creds.get("hl_testnet"):
                has_mainnet = True
            if has_mainnet and live_enabled:
                targets.append({
                    "exchange": "hyperliquid",
                    "env": "live",
                    "account_type": "mainnet"
                })
    
    else:  # demo/testnet mode (default) - use CURRENT active exchange only
        if current_exchange == "bybit" and bybit_enabled:
            # Check if demo credentials exist
            creds = get_all_user_credentials(user_id)
            if creds.get("demo_api_key") and creds.get("demo_api_secret"):
                targets.append({
                    "exchange": "bybit",
                    "env": "paper",
                    "account_type": "demo"
                })
        
        elif current_exchange == "hyperliquid" and hl_enabled:
            hl_creds = get_hl_credentials(user_id)
            has_testnet = bool(hl_creds.get("hl_testnet_private_key"))
            if not has_testnet and hl_creds.get("hl_private_key") and hl_creds.get("hl_testnet"):
                has_testnet = True
            if has_testnet:
                targets.append({
                    "exchange": "hyperliquid",
                    "env": "paper",
                    "account_type": "testnet"
                })
    
    return targets


def _env_to_account_type(exchange: str, env: str) -> str:
    """Convert env (paper/live) to account_type for specific exchange."""
    if exchange == "hyperliquid":
        return "testnet" if env == "paper" else "mainnet"
    else:
        return "demo" if env == "paper" else "real"


def _get_bybit_account_types(user_id: int) -> list[str]:
    """Get all configured Bybit account types."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT demo_api_key, demo_api_secret, real_api_key, real_api_secret, trading_mode FROM users WHERE user_id=?",
            (user_id,)
        ).fetchone()
    
    if not row:
        return []
    
    demo_key, demo_secret, real_key, real_secret, trading_mode = row
    result = []
    
    if demo_key and demo_secret:
        result.append("demo")
    if real_key and real_secret:
        result.append("real")
    
    return result


def _get_hl_account_types(user_id: int) -> list[str]:
    """
    Get all configured HyperLiquid account types.
    
    New architecture: checks for separate testnet/mainnet credentials.
    Returns list of account types that have valid credentials configured.
    """
    hl_creds = get_hl_credentials(user_id)
    
    result = []
    
    # Check testnet credentials
    has_testnet = bool(hl_creds.get("hl_testnet_private_key"))
    # Fallback to legacy key if hl_testnet flag is set
    if not has_testnet and hl_creds.get("hl_private_key") and hl_creds.get("hl_testnet"):
        has_testnet = True
    
    # Check mainnet credentials
    has_mainnet = bool(hl_creds.get("hl_mainnet_private_key"))
    # Fallback to legacy key if hl_testnet flag is NOT set
    if not has_mainnet and hl_creds.get("hl_private_key") and not hl_creds.get("hl_testnet"):
        has_mainnet = True
    
    if has_testnet:
        result.append("testnet")
    if has_mainnet:
        result.append("mainnet")
    
    return result


def delete_user_credentials(user_id: int, account_type: str):
    """Delete API credentials for demo or real account."""
    ensure_user(user_id)
    if account_type == "real":
        key_col, secret_col = "real_api_key", "real_api_secret"
    else:
        key_col, secret_col = "demo_api_key", "demo_api_secret"
    
    with get_conn() as conn:
        conn.execute(f"UPDATE users SET {key_col}=NULL, {secret_col}=NULL WHERE user_id=?", (user_id,))
        conn.commit()
    invalidate_user_cache(user_id)

def set_user_field(user_id: int, field: str, value: Any):
    if field not in USER_FIELDS_WHITELIST:
        raise ValueError(f"Unsupported field: {field}")
    
    # NOTE: DB has mixed types after migrations!
    # BOOLEAN columns: terms_accepted, disclaimer_accepted, dca_enabled, bybit_enabled
    # INTEGER columns: is_allowed, is_banned, hl_enabled, use_atr, etc.
    
    # Columns that ARE BOOLEAN in PostgreSQL - convert int to bool
    BOOLEAN_COLUMNS = {
        "terms_accepted", "disclaimer_accepted", "dca_enabled", "bybit_enabled",
        # All trade_* columns are BOOLEAN in production DB
        "trade_oi", "trade_rsi_bb", "trade_manual", "trade_elcaro",
        "trade_fibonacci", "trade_scalper", "trade_scryptomera"
    }
    
    # Columns that ARE INTEGER in PostgreSQL - convert bool to int
    INTEGER_FLAG_COLUMNS = {
        "is_allowed", "is_banned", "hl_enabled", "use_atr", "be_enabled",
        "hl_testnet", "live_enabled", "limit_enabled", "spot_enabled"
    }
    
    if field in BOOLEAN_COLUMNS and isinstance(value, int):
        value = bool(value)
    elif field in INTEGER_FLAG_COLUMNS and isinstance(value, bool):
        value = 1 if value else 0
    
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, user_id))
        conn.commit()
    invalidate_user_cache(user_id)


def get_user_field(user_id: int, field: str, default: Any = None) -> Any:
    """Get a single field from user record."""
    if field not in USER_FIELDS_WHITELIST:
        raise ValueError(f"Unsupported field: {field}")
    ensure_user(user_id)
    with get_conn() as conn:
        cur = conn.execute(f"SELECT {field} FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        if row:
            return row[0] if row[0] is not None else default
        return default


def get_user_lang(user_id: int) -> str:
    """Get user's language preference."""
    return get_user_field(user_id, "lang", "en")


def get_user_config(user_id: int) -> dict:
    # Check cache first
    now = time.time()
    if user_id in _user_config_cache:
        ts, cfg = _user_config_cache[user_id]
        if now - ts < CACHE_TTL:
            return cfg.copy()  # Return copy to prevent mutation
    
    ensure_user(user_id)
    with get_conn() as conn:
        cols = [
            # торговые настройки
            "percent", "coins", "limit_enabled",
            "trade_oi", "trade_rsi_bb", "trade_manual",
            "tp_percent", "sl_percent",
            "use_atr", "lang",
            # стратегии/пороги
            "strategies_enabled", "strategies_order",
            "rsi_lo", "rsi_hi", "bb_touch_k",
            "oi_min_pct", "price_min_pct", "limit_only_default",
            # доступ/согласие
            "is_allowed", "is_banned", "terms_accepted", "disclaimer_accepted",
            # совместимость
            "first_seen_ts", "last_seen_ts",
            # exchange settings (IMPORTANT for routing!)
            "exchange_type", "trading_mode", "live_enabled",
        ]
        if _col_exists(conn, "users", "trade_scryptomera"):
            cols.append("trade_scryptomera")
        # backward compatibility with old DB
        elif _col_exists(conn, "users", "trade_bitkonovich"):
            cols.append("trade_bitkonovich")
        if _col_exists(conn, "users", "trade_scalper"):
            cols.append("trade_scalper")
        if _col_exists(conn, "users", "trade_elcaro"):
            cols.append("trade_elcaro")
        if _col_exists(conn, "users", "trade_fibonacci"):
            cols.append("trade_fibonacci")
        # Also check for old column name for backward compatibility
        elif _col_exists(conn, "users", "trade_wyckoff"):
            cols.append("trade_wyckoff")
        # trade_manual is now in base cols list
        if _col_exists(conn, "users", "strategy_settings"):
            cols.append("strategy_settings")
        if _col_exists(conn, "users", "dca_enabled"):
            cols.append("dca_enabled")
        if _col_exists(conn, "users", "dca_pct_1"):
            cols.append("dca_pct_1")
        if _col_exists(conn, "users", "dca_pct_2"):
            cols.append("dca_pct_2")
        # Spot trading
        if _col_exists(conn, "users", "spot_enabled"):
            cols.append("spot_enabled")
        if _col_exists(conn, "users", "spot_settings"):
            cols.append("spot_settings")
        # Guide sent flag
        if _col_exists(conn, "users", "guide_sent"):
            cols.append("guide_sent")
        # Global leverage
        if _col_exists(conn, "users", "leverage"):
            cols.append("leverage")
        # Limit ladder (DCA entries)
        if _col_exists(conn, "users", "limit_ladder_enabled"):
            cols.append("limit_ladder_enabled")
        if _col_exists(conn, "users", "limit_ladder_count"):
            cols.append("limit_ladder_count")
        if _col_exists(conn, "users", "limit_ladder_settings"):
            cols.append("limit_ladder_settings")
        # Global order type
        if _col_exists(conn, "users", "global_order_type"):
            cols.append("global_order_type")
        # Global ATR settings
        if _col_exists(conn, "users", "atr_periods"):
            cols.append("atr_periods")
        if _col_exists(conn, "users", "atr_multiplier_sl"):
            cols.append("atr_multiplier_sl")
        if _col_exists(conn, "users", "atr_trigger_pct"):
            cols.append("atr_trigger_pct")
        if _col_exists(conn, "users", "atr_step_pct"):
            cols.append("atr_step_pct")
        # Global direction
        if _col_exists(conn, "users", "direction"):
            cols.append("direction")
        # Per-exchange settings (leverage, order_type, coins_group)
        for _exc_col in (
            "bybit_leverage", "hl_leverage",
            "bybit_order_type", "hl_order_type",
            "bybit_coins_group", "hl_coins_group",
        ):
            if _col_exists(conn, "users", _exc_col):
                cols.append(_exc_col)
        # Auto-close settings (per exchange)
        for _ac_col in (
            "bybit_auto_close_enabled", "bybit_auto_close_time", "bybit_auto_close_timezone",
            "hl_auto_close_enabled", "hl_auto_close_time", "hl_auto_close_timezone",
        ):
            if _col_exists(conn, "users", _ac_col):
                cols.append(_ac_col)

        row = conn.execute(f"SELECT {', '.join(cols)} FROM users WHERE user_id=?",
                           (user_id,)).fetchone()

    if not row:
        # дефолтная конфигурация
        return {
            "percent": 1.0,
            "coins": "ALL",
            "limit_enabled": False,  # Market by default
            "trade_oi": True,
            "trade_rsi_bb": True,
            "tp_percent": DEFAULT_TP_PCT,
            "sl_percent": DEFAULT_SL_PCT,
            "use_atr": False,  # ATR trailing disabled by default
            "lang": DEFAULT_LANG,
            "strategies_enabled": [],
            "strategies_order": [],
            "rsi_lo": None,
            "rsi_hi": None,
            "bb_touch_k": None,
            "oi_min_pct": None,
            "price_min_pct": None,
            "limit_only_default": False,
            "is_allowed": 0,
            "is_banned": 0,
            "terms_accepted": 0,
            "first_seen_ts": None,
            "last_seen_ts": None,
            "trade_scryptomera": 0,
            "trade_scalper": 0,
            "trade_elcaro": 0,
            "trade_fibonacci": 0,
            "trade_manual": 1,  # Manual monitoring enabled by default
            "strategy_settings": {},
            "dca_enabled": 0,
            "dca_pct_1": 10.0,
            "dca_pct_2": 25.0,
            "spot_enabled": 0,
            "spot_settings": {},
            "guide_sent": 0,
            "leverage": 10,
            "limit_ladder_enabled": 0,
            "limit_ladder_count": 3,
            "limit_ladder_settings": [],
            "global_order_type": "market",
            "atr_periods": 7,
            "atr_multiplier_sl": 1.0,
            "atr_trigger_pct": 2.0,
            "atr_step_pct": 0.5,
            "direction": "all",
            # Exchange settings
            "exchange_type": "bybit",
            "trading_mode": "demo",
            "live_enabled": False,
        }

    data = dict(zip(cols, row))

    def parse_csv(s: str | None) -> list[str]:
        return [x for x in (s or "").split(",") if x]

    cfg = {
        "percent": float(data.get("percent") or 1.0),
        "coins": (data.get("coins") or "ALL").upper(),
        "limit_enabled": bool(data.get("limit_enabled") or 0),
        "trade_oi": bool(data.get("trade_oi") or 0),
        "trade_rsi_bb": bool(data.get("trade_rsi_bb") or 0),
        "tp_percent": float(data.get("tp_percent") or DEFAULT_TP_PCT),
        "sl_percent": float(data.get("sl_percent") or DEFAULT_SL_PCT),
        "use_atr": bool(data.get("use_atr") or 0),
        "lang": (data.get("lang") or DEFAULT_LANG),
        "strategies_enabled": parse_csv(data.get("strategies_enabled")),
        "strategies_order": parse_csv(data.get("strategies_order")),
        "rsi_lo": data.get("rsi_lo"),
        "rsi_hi": data.get("rsi_hi"),
        "bb_touch_k": data.get("bb_touch_k"),
        "oi_min_pct": data.get("oi_min_pct"),
        "price_min_pct": data.get("price_min_pct"),
        "limit_only_default": bool(data.get("limit_only_default") or 0),
        "is_allowed": int(data.get("is_allowed") or 0),
        "is_banned": int(data.get("is_banned") or 0),
        "terms_accepted": int(data.get("terms_accepted") or 0),
        "first_seen_ts": data.get("first_seen_ts"),
        "last_seen_ts": data.get("last_seen_ts"),
        "trade_scryptomera": int(data.get("trade_scryptomera") or data.get("trade_bitkonovich") or 0)
        if "trade_scryptomera" in data or "trade_bitkonovich" in data
        else 0,
        "trade_scalper": int(data.get("trade_scalper") or 0)
        if "trade_scalper" in data
        else 0,
        "trade_elcaro": int(data.get("trade_elcaro") or 0)
        if "trade_elcaro" in data
        else 0,
        "trade_fibonacci": int(data.get("trade_fibonacci") or data.get("trade_wyckoff") or 0)
        if "trade_fibonacci" in data or "trade_wyckoff" in data
        else 0,
        "trade_manual": int(data.get("trade_manual") if data.get("trade_manual") is not None else 1),
        "strategy_settings": _safe_json_loads(data.get("strategy_settings"), {})
        if data.get("strategy_settings")
        else {},
        "dca_enabled": int(data.get("dca_enabled") or 0)
        if "dca_enabled" in data
        else 0,
        "dca_pct_1": float(data.get("dca_pct_1") or 10.0)
        if "dca_pct_1" in data
        else 10.0,
        "dca_pct_2": float(data.get("dca_pct_2") or 25.0)
        if "dca_pct_2" in data
        else 25.0,
        # Spot trading
        "spot_enabled": int(data.get("spot_enabled") or 0)
        if "spot_enabled" in data
        else 0,
        "spot_settings": _safe_json_loads(data.get("spot_settings"), {})
        if data.get("spot_settings")
        else {},
        # Global leverage
        "leverage": int(data.get("leverage") or 10)
        if "leverage" in data
        else 10,
        # Limit ladder
        "limit_ladder_enabled": int(data.get("limit_ladder_enabled") or 0)
        if "limit_ladder_enabled" in data
        else 0,
        "limit_ladder_count": int(data.get("limit_ladder_count") or 3)
        if "limit_ladder_count" in data
        else 3,
        "limit_ladder_settings": _safe_json_loads(data.get("limit_ladder_settings"), [])
        if data.get("limit_ladder_settings")
        else [],
        # Global order type
        "global_order_type": data.get("global_order_type", "market")
        if "global_order_type" in data
        else "market",
        # Global ATR settings
        "atr_periods": int(data.get("atr_periods") or 7)
        if "atr_periods" in data
        else 7,
        "atr_multiplier_sl": float(data.get("atr_multiplier_sl") or 1.0)
        if "atr_multiplier_sl" in data
        else 1.0,
        "atr_trigger_pct": float(data.get("atr_trigger_pct") or 2.0)
        if "atr_trigger_pct" in data
        else 2.0,
        "atr_step_pct": float(data.get("atr_step_pct") or 0.5)
        if "atr_step_pct" in data
        else 0.5,
        # Global direction
        "direction": data.get("direction", "all")
        if "direction" in data
        else "all",
        # Exchange settings (IMPORTANT for routing!)
        "exchange_type": data.get("exchange_type") or "bybit",
        "trading_mode": data.get("trading_mode") or "demo",
        "live_enabled": bool(data.get("live_enabled") or 0),
        # Per-exchange settings
        "bybit_leverage": int(data.get("bybit_leverage") or 0) if data.get("bybit_leverage") else None,
        "hl_leverage": int(data.get("hl_leverage") or 0) if data.get("hl_leverage") else None,
        "bybit_order_type": data.get("bybit_order_type") or None,
        "hl_order_type": data.get("hl_order_type") or None,
        "bybit_coins_group": data.get("bybit_coins_group") or None,
        "hl_coins_group": data.get("hl_coins_group") or None,
    }
    # Store in cache
    _user_config_cache[user_id] = (time.time(), cfg)
    return cfg


# ------------------------------------------------------------------------------------
# Strategy Settings Helpers
# ------------------------------------------------------------------------------------
# Default settings per strategy (used as fallback if user hasn't customized)
# Extended with ATR settings: atr_periods, atr_multiplier_sl, atr_trigger_pct
# use_atr: None = use global, 0 = Fixed SL/TP, 1 = ATR Trailing
DEFAULT_STRATEGY_SETTINGS = {
    "oi": {
        "percent": None, "sl_percent": None, "tp_percent": None,
        "atr_periods": None, "atr_multiplier_sl": None, "atr_trigger_pct": None,
        "use_atr": None,  # None = use global, 0 = Fixed SL/TP, 1 = ATR Trailing
        "order_type": "market",  # "market" or "limit"
        "coins_group": None,  # "ALL", "TOP", "VOLATILE" or None for global
        "leverage": None,  # None = use current, or 1-100
        "trading_mode": "global",  # "global", "demo", "real", "both"
    },
    "rsi_bb": {
        "percent": None, "sl_percent": None, "tp_percent": None,
        "atr_periods": None, "atr_multiplier_sl": None, "atr_trigger_pct": None,
        "use_atr": None,  # None = use global, 0 = Fixed SL/TP, 1 = ATR Trailing
        "order_type": "market",
        "coins_group": None,
        "leverage": None,
        "trading_mode": "global",  # "global", "demo", "real", "both"
    },
    "scryptomera": {
        "percent": None, "sl_percent": None, "tp_percent": None,
        "atr_periods": None, "atr_multiplier_sl": None, "atr_trigger_pct": None,
        "use_atr": None,  # None = use global, 0 = Fixed SL/TP, 1 = ATR Trailing
        "order_type": "market",
        "coins_group": None,
        "leverage": None,
        "trading_mode": "global",  # "global", "demo", "real", "both"
        # Direction filter: "all", "long", "short"
        "direction": "all",
        # Separate settings for LONG
        "long_percent": None, "long_sl_percent": None, "long_tp_percent": None,
        "long_atr_periods": None, "long_atr_multiplier_sl": None, "long_atr_trigger_pct": None,
        # Separate settings for SHORT
        "short_percent": None, "short_sl_percent": None, "short_tp_percent": None,
        "short_atr_periods": None, "short_atr_multiplier_sl": None, "short_atr_trigger_pct": None,
    },
    "scalper": {
        "percent": None, "sl_percent": None, "tp_percent": None,
        "atr_periods": None, "atr_multiplier_sl": None, "atr_trigger_pct": None,
        "use_atr": None,  # None = use global, 0 = Fixed SL/TP, 1 = ATR Trailing
        "order_type": "market",
        "coins_group": None,
        "leverage": None,
        "trading_mode": "global",  # "global", "demo", "real", "both"
        # Direction filter: "all", "long", "short"
        "direction": "all",
        # Separate settings for LONG
        "long_percent": None, "long_sl_percent": None, "long_tp_percent": None,
        "long_atr_periods": None, "long_atr_multiplier_sl": None, "long_atr_trigger_pct": None,
        # Separate settings for SHORT
        "short_percent": None, "short_sl_percent": None, "short_tp_percent": None,
        "short_atr_periods": None, "short_atr_multiplier_sl": None, "short_atr_trigger_pct": None,
    },
    "elcaro": {
        "percent": None, "sl_percent": None, "tp_percent": None,
        "atr_periods": None, "atr_multiplier_sl": None, "atr_trigger_pct": None,
        "use_atr": None,  # None = use global, 0 = Fixed SL/TP, 1 = ATR Trailing
        "order_type": "market",
        "coins_group": None,
        "trading_mode": "global",  # "global", "demo", "real", "both"
        # leverage for elcaro comes from signal, not settings
    },
    "fibonacci": {
        "percent": None, "sl_percent": None, "tp_percent": None,
        "atr_periods": None, "atr_multiplier_sl": None, "atr_trigger_pct": None,
        "use_atr": None,  # None = use global, 0 = Fixed SL/TP, 1 = ATR Trailing
        "order_type": "market",
        "coins_group": None,
        "leverage": 10,  # Default leverage
        "min_quality": 50,  # Minimum quality score (0-100) to trade
        "direction": "all",  # "all", "long", "short"
        "trading_mode": "global",  # "global", "demo", "real", "both"
    },
    "manual": {
        "percent": None, "sl_percent": None, "tp_percent": None,
        "atr_periods": None, "atr_multiplier_sl": None, "atr_trigger_pct": None,
        "use_atr": None,  # None = use global, 0 = Fixed SL/TP, 1 = ATR Trailing
        "order_type": "market",
        "coins_group": None,
        "leverage": 10,
        "direction": "all",
        "trading_mode": "demo",  # Manual trades default to demo
    },
}

STRATEGY_NAMES = ["oi", "rsi_bb", "scryptomera", "scalper", "elcaro", "fibonacci", "manual", "wyckoff"]
STRATEGY_SETTING_FIELDS = [
    "percent", "sl_percent", "tp_percent",
    "tp_pct", "sl_pct",  # Aliases for compatibility
    "atr_periods", "atr_multiplier_sl", "atr_trigger_pct",
    "use_atr",  # 0 or 1 - use ATR trailing or fixed SL/TP
    "order_type",  # "market" or "limit"
    "coins_group",  # "ALL", "TOP", "VOLATILE" or None
    "leverage",  # 1-100 or None
    "trading_mode",  # "demo", "real", "both", or "global" (use user's global setting)
    "enabled",  # True/False - enable this strategy
    "account_types",  # "demo", "real", "both" - which accounts to use
    # Scryptomera-specific fields
    "direction", "long_percent", "long_sl_percent", "long_tp_percent",
    "long_atr_periods", "long_atr_multiplier_sl", "long_atr_trigger_pct",
    "short_percent", "short_sl_percent", "short_tp_percent",
    "short_atr_periods", "short_atr_multiplier_sl", "short_atr_trigger_pct",
    # HyperLiquid-specific fields  
    "hl_enabled",  # 0 or 1 - enable trading on HyperLiquid for this strategy
    "hl_percent", "hl_sl_percent", "hl_tp_percent",
    "hl_leverage",  # 1-100 or None (use strategy default)
]

# Default HL strategy settings (same structure as Bybit but for HL)
DEFAULT_HL_STRATEGY_SETTINGS = {
    "oi": {"hl_enabled": False, "hl_percent": None, "hl_sl_percent": None, "hl_tp_percent": None, "hl_leverage": None},
    "rsi_bb": {"hl_enabled": False, "hl_percent": None, "hl_sl_percent": None, "hl_tp_percent": None, "hl_leverage": None},
    "scryptomera": {"hl_enabled": False, "hl_percent": None, "hl_sl_percent": None, "hl_tp_percent": None, "hl_leverage": None},
    "scalper": {"hl_enabled": False, "hl_percent": None, "hl_sl_percent": None, "hl_tp_percent": None, "hl_leverage": None},
    "elcaro": {"hl_enabled": False, "hl_percent": None, "hl_sl_percent": None, "hl_tp_percent": None, "hl_leverage": None},
    "fibonacci": {"hl_enabled": False, "hl_percent": None, "hl_sl_percent": None, "hl_tp_percent": None, "hl_leverage": None},
    "manual": {"hl_enabled": False, "hl_percent": None, "hl_sl_percent": None, "hl_tp_percent": None, "hl_leverage": None},
    "wyckoff": {"hl_enabled": False, "hl_percent": None, "hl_sl_percent": None, "hl_tp_percent": None, "hl_leverage": None},
}


# ------------------------------------------------------------------------------------
# NEW: Database-based Strategy Settings Functions
# ------------------------------------------------------------------------------------

# Columns in user_strategy_settings table that can be read/written
_STRATEGY_DB_COLUMNS = [
    "enabled", "percent", "sl_percent", "tp_percent", "leverage",
    "use_atr", "atr_periods", "atr_multiplier_sl", "atr_trigger_pct", "atr_step_pct",
    "be_enabled", "be_trigger_pct", "be_offset_pct",  # Break-Even settings
    # Partial Take Profit settings (срез маржи в 2 шага)
    "partial_tp_enabled", 
    "partial_tp_1_trigger_pct", "partial_tp_1_close_pct",
    "partial_tp_2_trigger_pct", "partial_tp_2_close_pct",
    "order_type", "coins_group", "direction", "trading_mode",
    # LONG settings
    "long_percent", "long_sl_percent", "long_tp_percent", "long_leverage", "long_use_atr",
    "long_atr_periods", "long_atr_multiplier_sl", "long_atr_trigger_pct", "long_atr_step_pct",
    "long_be_enabled", "long_be_trigger_pct", "long_be_offset_pct",  # Long-specific BE
    "long_partial_tp_enabled",
    "long_partial_tp_1_trigger_pct", "long_partial_tp_1_close_pct",
    "long_partial_tp_2_trigger_pct", "long_partial_tp_2_close_pct",
    # SHORT settings
    "short_percent", "short_sl_percent", "short_tp_percent", "short_leverage", "short_use_atr",
    "short_atr_periods", "short_atr_multiplier_sl", "short_atr_trigger_pct", "short_atr_step_pct",
    "short_be_enabled", "short_be_trigger_pct", "short_be_offset_pct",  # Short-specific BE
    "short_partial_tp_enabled",
    "short_partial_tp_1_trigger_pct", "short_partial_tp_1_close_pct",
    "short_partial_tp_2_trigger_pct", "short_partial_tp_2_close_pct",
    "min_quality"
]


def _migrate_single_strategy(user_id: int, strategy: str, strat_json: dict, 
                              exchange: str, account_type: str, cur) -> bool:
    """
    Helper to migrate a single strategy's settings from JSON dict to DB.
    Uses provided cursor for transaction.
    With 3D schema, inserts separate rows for 'long' and 'short' sides.
    """
    # Filter only valid columns
    valid_settings = {k: v for k, v in strat_json.items() if k in _STRATEGY_DB_COLUMNS and v is not None}
    if not valid_settings:
        return False
    
    # Insert for both sides
    for side in ['long', 'short']:
        # Extract side-specific settings (e.g., 'long_percent' -> 'percent')
        side_settings = {}
        for key, val in valid_settings.items():
            if key.startswith(f"{side}_"):
                # Remove side prefix for DB column
                db_key = key[len(side) + 1:]  # Remove 'long_' or 'short_'
                side_settings[db_key] = val
            elif not key.startswith("long_") and not key.startswith("short_"):
                # Non-side-specific setting, apply to both
                side_settings[key] = val
        
        if not side_settings:
            continue
        
        columns = ["user_id", "strategy", "side", "exchange", "account_type"] + list(side_settings.keys())
        placeholders = ["%s"] * len(columns)
        values = [user_id, strategy, side, exchange, account_type] + list(side_settings.values())
        
        # Build UPDATE SET clause for all columns except primary key
        update_cols = list(side_settings.keys())
        update_set = ", ".join([f"{col} = EXCLUDED.{col}" for col in update_cols])
        
        try:
            cur.execute(f"""
                INSERT INTO user_strategy_settings ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                ON CONFLICT (user_id, strategy, side, exchange) DO UPDATE SET {update_set}
            """, values)
        except Exception as e:
            _logger.exception(f"Failed to save strategy settings for user {user_id}: {e}")
            return False
    
    return True


def get_strategy_settings_db(user_id: int, strategy: str, exchange: str = "bybit", account_type: str = "demo") -> dict:
    """
    Get strategy settings from user_strategy_settings table.
    
    WEBAPP WRAPPER: Delegates to get_strategy_settings() with full fallback logic.
    
    For direct DB access without fallback, use _get_strategy_settings_raw().
    """
    return get_strategy_settings(user_id, strategy, exchange, account_type)


def _get_strategy_settings_raw(user_id: int, strategy: str, exchange: str, account_type: str) -> dict:
    """
    LOW-LEVEL: Read strategy settings directly from DB without fallback logic.
    
    Returns raw dict from database or empty dict with defaults if not found.
    Used internally by get_strategy_settings() for each fallback level.
    
    DO NOT use directly - use get_strategy_settings() for proper fallback handling.
    """
    if strategy not in STRATEGY_NAMES:
        return {}
    
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM user_strategy_settings
                WHERE user_id = ? AND strategy = ? AND exchange = ? AND account_type = ?
            """, (user_id, strategy, exchange, account_type))
            row = cur.fetchone()
            
            if row:
                # Get column names from cursor
                columns = [desc[0] for desc in cur.description]
                result = dict(zip(columns, row))
                # Remove metadata columns
                for key in ["user_id", "strategy", "exchange", "account_type", "created_at", "updated_at"]:
                    result.pop(key, None)
                return result
            
            # Not found - return empty dict (caller will handle defaults)
            return {}
    except Exception as e:
        _logger.warning(f"Error reading strategy settings: {e}")
        return {}


def set_strategy_setting_db(user_id: int, strategy: str, field: str, value, 
                            exchange: str = "bybit", account_type: str = "default") -> bool:
    """
    Set a single field for a strategy in user_strategy_settings table.
    
    Low-level function that directly writes to DB.
    For smart fallback logic use set_strategy_setting() wrapper.
    """
    # Call the PostgreSQL function directly (NOT the wrapper to avoid recursion!)
    return pg_set_strategy_setting(user_id, strategy, field, value, exchange, account_type)


def set_strategy_settings_db(user_id: int, strategy: str, settings: dict,
                             exchange: str = "bybit", account_type: str = "demo") -> bool:
    """
    Set multiple fields for a strategy at once.
    
    WEBAPP WRAPPER: Uses new set_strategy_setting() with 'default' fallback logic.
    """
    if strategy not in STRATEGY_NAMES:
        return False
    
    # Filter only valid columns
    valid_settings = {k: v for k, v in settings.items() if k in _STRATEGY_DB_COLUMNS}
    if not valid_settings:
        return False
    
    try:
        # Use the new function for each field
        for field, value in valid_settings.items():
            set_strategy_setting(user_id, strategy, field, value, exchange, account_type)
        return True
    except Exception as e:
        print(f"[DB ERROR] set_strategy_settings_db: {e}")
        return False


def get_all_strategy_settings_db(user_id: int, exchange: str = "bybit", account_type: str = "demo") -> dict:
    """
    Get all strategy settings for a user/exchange/account_type combination.
    Returns dict: { "scryptomera": {...}, "scalper": {...}, ... }
    """
    result = {}
    for strategy in STRATEGY_NAMES:
        result[strategy] = get_strategy_settings_db(user_id, strategy, exchange, account_type)
    return result


def get_strategy_trading_mode(user_id: int, strategy: str) -> str:
    """Get trading mode for a specific strategy.
    
    Returns 'demo', 'real', or 'both'. Default is 'demo'.
    """
    strategy_normalized = strategy.lower().replace("-", "_").replace(" ", "_")
    if strategy_normalized == "rsi_bb":
        strategy_normalized = "rsi_bb"
    
    # Use PostgreSQL function directly
    from core.db_postgres import pg_get_strategy_settings
    settings = pg_get_strategy_settings(user_id, strategy_normalized)
    return settings.get("trading_mode") or "demo"


def set_strategy_trading_mode(user_id: int, strategy: str, mode: str, exchange: str = None) -> bool:
    """Set trading mode for a specific strategy.
    
    Args:
        user_id: User's Telegram ID
        strategy: Strategy name (oi, scryptomera, etc.)
        mode: 'demo', 'real', or 'both'
        exchange: Exchange name. If None, uses user's active exchange.
    
    Returns True if successful.
    """
    if mode not in ("demo", "real", "both"):
        return False
    
    strategy_normalized = strategy.lower().replace("-", "_").replace(" ", "_")
    if strategy_normalized == "rsi_bb":
        strategy_normalized = "rsi_bb"
    
    # Get user's active exchange if not specified
    if not exchange:
        exchange = get_exchange_type(user_id) or "bybit"
    
    # Set in DB - trading_mode is saved per exchange
    return set_strategy_setting_db(user_id, strategy_normalized, "trading_mode", mode, exchange=exchange)


def migrate_json_to_db_settings(user_id: int) -> bool:
    """
    Migrate user's JSON strategy_settings to new database table.
    Call this once per user to migrate existing settings.
    """
    cfg = get_user_config(user_id)
    json_settings = cfg.get("strategy_settings", {})
    
    if not json_settings:
        return True  # Nothing to migrate
    
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            
            # Check for new format (with exchange keys) or legacy format
            if any(k in json_settings for k in ["bybit", "hyperliquid"]):
                # New format: { "bybit": { "demo": { "scryptomera": {...} } } }
                for exchange, exchange_data in json_settings.items():
                    if not isinstance(exchange_data, dict):
                        continue
                    for account_type, account_data in exchange_data.items():
                        if not isinstance(account_data, dict):
                            continue
                        for strategy, strat_settings in account_data.items():
                            if strategy in STRATEGY_NAMES and isinstance(strat_settings, dict):
                                set_strategy_settings_db(user_id, strategy, strat_settings, exchange, account_type)
            else:
                # Legacy format: { "scryptomera": {...}, "scalper": {...} }
                # Migrate to bybit/demo by default
                for strategy, strat_settings in json_settings.items():
                    if strategy in STRATEGY_NAMES and isinstance(strat_settings, dict):
                        set_strategy_settings_db(user_id, strategy, strat_settings, "bybit", "demo")
            
            # Clear the JSON field after migration
            cur.execute("UPDATE users SET strategy_settings = NULL WHERE user_id = ?", (user_id,))
            conn.commit()
            invalidate_user_cache(user_id)
            return True
    except Exception as e:
        print(f"[DB ERROR] migrate_json_to_db_settings for user {user_id}: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# SIMPLIFIED STRATEGY SETTINGS API
# Only LONG/SHORT per strategy, no complex fallbacks
# ═══════════════════════════════════════════════════════════════════════════════

def get_strategy_settings(user_id: int, strategy: str, exchange: str = None, account_type: str = None) -> dict:
    """
    Get settings for a specific strategy for a specific exchange.
    
    4D SCHEMA: Uses (user_id, strategy, side, exchange) as key.
    If exchange is None, uses user's current exchange from get_exchange_type().
    Returns settings with long_* and short_* fields.
    """
    from core.db_postgres import pg_get_strategy_settings
    
    # If exchange not provided, get user's current exchange
    if exchange is None:
        exchange = get_exchange_type(user_id) or "bybit"
    
    return pg_get_strategy_settings(user_id, strategy, exchange)


def set_strategy_setting(user_id: int, strategy: str, field: str, value,
                         exchange: str = None, account_type: str = None,
                         sync_all_accounts: bool = True) -> bool:
    """
    Set a specific field for a strategy on a specific exchange.
    
    4D SCHEMA: Uses (user_id, strategy, side, exchange) as key.
    If exchange is None, uses user's current exchange from get_exchange_type().
    """
    # If exchange not provided, get user's current exchange
    if exchange is None:
        exchange = get_exchange_type(user_id) or "bybit"
    
    return pg_set_strategy_setting(user_id, strategy, field, value, exchange)


def get_effective_settings(user_id: int, strategy: str, exchange: str = None, 
                          account_type: str = None, timeframe: str = "24h", 
                          side: str = None) -> dict:
    """
    Get effective settings for a strategy on a specific exchange.
    
    4D SCHEMA: Reads side-specific settings from DB with exchange context.
    Falls back to STRATEGY_DEFAULTS from coin_params.py.
    
    Args:
        user_id: User ID
        strategy: Strategy name (oi, scalper, scryptomera, etc.)
        exchange: Exchange name ('bybit' or 'hyperliquid'). If None, uses user's current.
        side: Trade side ('Buy'/'LONG' or 'Sell'/'SHORT'). REQUIRED for trading!
    
    Returns dict with: enabled, percent, sl_percent, tp_percent, leverage, 
                       use_atr, atr_trigger_pct, atr_step_pct, order_type
    """
    from coin_params import STRATEGY_DEFAULTS
    
    # Get settings for this exchange (or user's current if not specified)
    strat_settings = get_strategy_settings(user_id, strategy, exchange)
    
    # Determine side prefix
    side_prefix = "long"  # default
    if side:
        side_upper = str(side).upper()
        if side_upper in ("SELL", "SHORT"):
            side_prefix = "short"
    
    # Get defaults for this side
    defaults = STRATEGY_DEFAULTS.get(side_prefix, STRATEGY_DEFAULTS["long"])
    
    def _get(key):
        """Get value: DB side-specific → default"""
        side_key = f"{side_prefix}_{key}"
        val = strat_settings.get(side_key)
        if val is not None:
            return val
        return defaults.get(key)
    
    return {
        "enabled": bool(strat_settings.get(f"{side_prefix}_enabled", defaults.get("enabled", True))),
        "percent": _get("percent"),
        "sl_percent": _get("sl_percent"),
        "tp_percent": _get("tp_percent"),
        "leverage": _get("leverage"),
        "use_atr": bool(_get("use_atr")),
        "atr_trigger_pct": _get("atr_trigger_pct"),
        "atr_step_pct": _get("atr_step_pct"),
        "order_type": strat_settings.get("order_type") or defaults.get("order_type", "market"),
        # Extra fields for compatibility
        "direction": strat_settings.get("direction", "all"),
        "coins_group": strat_settings.get("coins_group", "TOP"),
        "side": side_prefix,
    }


def get_hl_strategy_settings(user_id: int, strategy: str) -> dict:
    """
    Get HyperLiquid-specific settings for a strategy.
    Returns dict with hl_enabled, hl_percent, hl_sl_percent, hl_tp_percent, hl_leverage
    """
    if strategy not in STRATEGY_NAMES:
        return DEFAULT_HL_STRATEGY_SETTINGS.get("oi", {}).copy()
    
    cfg = get_user_config(user_id)
    hl_settings = cfg.get("hl_strategy_settings", {})
    strat_settings = hl_settings.get(strategy, {})
    
    # Merge with defaults
    result = DEFAULT_HL_STRATEGY_SETTINGS.get(strategy, {}).copy()
    result.update(strat_settings)
    return result


def set_hl_strategy_setting(user_id: int, strategy: str, field: str, value) -> bool:
    """
    Set a specific HL field for a strategy.
    field must be one of: hl_enabled, hl_percent, hl_sl_percent, hl_tp_percent, hl_leverage
    """
    if strategy not in STRATEGY_NAMES:
        return False
    valid_fields = ["hl_enabled", "hl_percent", "hl_sl_percent", "hl_tp_percent", "hl_leverage"]
    if field not in valid_fields:
        return False
    
    cfg = get_user_config(user_id)
    hl_settings = cfg.get("hl_strategy_settings", {})
    
    if strategy not in hl_settings:
        hl_settings[strategy] = {}
    
    if value is None:
        hl_settings[strategy].pop(field, None)
    else:
        hl_settings[strategy][field] = value
    
    # Clean up empty strategy dicts
    if not hl_settings[strategy]:
        del hl_settings[strategy]
    
    set_user_field(user_id, "hl_strategy_settings", json.dumps(hl_settings))
    return True


def get_hl_effective_settings(user_id: int, strategy: str) -> dict:
    """
    Get effective HL settings for a strategy.
    Falls back to Bybit strategy settings if HL-specific not set.
    """
    hl_settings = get_hl_strategy_settings(user_id, strategy)
    bybit_settings = get_effective_settings(user_id, strategy)
    
    return {
        "enabled": hl_settings.get("hl_enabled", False),
        "percent": hl_settings.get("hl_percent") if hl_settings.get("hl_percent") is not None else bybit_settings.get("percent", 1.0),
        "sl_percent": hl_settings.get("hl_sl_percent") if hl_settings.get("hl_sl_percent") is not None else bybit_settings.get("sl_percent", 2.0),
        "tp_percent": hl_settings.get("hl_tp_percent") if hl_settings.get("hl_tp_percent") is not None else bybit_settings.get("tp_percent", 3.0),
        "leverage": hl_settings.get("hl_leverage") if hl_settings.get("hl_leverage") is not None else bybit_settings.get("leverage", 10),
    }


def get_all_users() -> list[int]:
    """Get all user IDs with caching."""
    global _all_users_cache
    now = time.time()
    ts, users = _all_users_cache
    if now - ts < CACHE_TTL:
        return users.copy()
    
    with get_conn() as conn:
        rows = conn.execute("SELECT user_id FROM users").fetchall()
    users = [r[0] for r in rows]
    _all_users_cache = (now, users)
    return users

def get_active_trading_users() -> list[int]:
    """
    Get users with API keys configured - optimized for monitoring loop.
    
    P0.10: Now includes users with HyperLiquid credentials too.
    Supports both legacy (hl_private_key) and new multitenancy (hl_testnet/mainnet_private_key).
    """
    global _active_users_cache
    now = time.time()
    ts, users = _active_users_cache
    if now - ts < CACHE_TTL:
        return users.copy()
    
    with get_conn() as conn:
        # P0.10: Include HL users in the query (both legacy and new multitenancy architecture)
        rows = conn.execute("""
            SELECT user_id FROM users 
            WHERE is_banned = 0 
            AND (
                demo_api_key IS NOT NULL 
                OR real_api_key IS NOT NULL
                OR (hl_private_key IS NOT NULL AND hl_enabled = 1)
                OR (hl_testnet_private_key IS NOT NULL AND hl_enabled = 1)
                OR (hl_mainnet_private_key IS NOT NULL AND hl_enabled = 1)
            )
        """).fetchall()
    users = [r[0] for r in rows]
    _active_users_cache = (now, users)
    return users

def get_subscribed_users() -> list[int]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT user_id FROM users WHERE limit_enabled=1"
        ).fetchall()
    return [r[0] for r in rows]

# ------------------------------------------------------------------------------------
# Market / News / Meta
# ------------------------------------------------------------------------------------
def _now_ms() -> int:
    return int(time.time() * 1000)

def save_market_snapshot(dom: float, price: float, change: float, alt_signal: str):
    # PostgreSQL: use datetime instead of Unix timestamp (bigint)
    from datetime import datetime
    ts = datetime.now()
    with get_conn() as conn:
        conn.execute(
            """
          INSERT INTO market_snapshots(ts, btc_dom, btc_price, btc_change, alt_signal)
          VALUES (?, ?, ?, ?, ?)
        """,
            (ts, dom, price, change, alt_signal),
        )
        conn.commit()

def store_news(
    title: str,
    link: str,
    description: str,
    image_url: str,
    signal: str,
    sentiment: str,
):
    with get_conn() as conn:
        conn.execute(
            """
          INSERT INTO news(link, title, description, image_url, signal, sentiment)
          VALUES (?, ?, ?, ?, ?, ?)
          ON CONFLICT (link) DO NOTHING
        """,
            (link, title, description, image_url, signal, sentiment),
        )
        conn.commit()

def get_prev_btc_dom() -> float | None:
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM meta WHERE key='btc_dom'").fetchone()
    return float(row[0]) if row else None

def store_prev_btc_dom(dom: float):
    with get_conn() as conn:
        conn.execute(
            """
          INSERT INTO meta(key, value) VALUES('btc_dom', ?)
          ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """,
            (str(dom),),
        )
        conn.commit()

# ------------------------------------------------------------------------------------
# Pyramids
# ------------------------------------------------------------------------------------
def get_pyramid(user_id: int, symbol: str, exchange: str = "bybit") -> dict:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT side, count FROM pyramids WHERE user_id=? AND symbol=? AND exchange=?",
            (user_id, symbol, exchange),
        ).fetchone()
    return {"side": row[0], "count": row[1]} if row else {"side": None, "count": 0}

def inc_pyramid(user_id: int, symbol: str, new_side: str, exchange: str = "bybit"):
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO pyramids(user_id, symbol, side, count, exchange)
            VALUES (?, ?, ?, 1, ?)
            ON CONFLICT(user_id, symbol, exchange) DO UPDATE SET
              side  = excluded.side,
              count = CASE
                        WHEN pyramids.side <> excluded.side THEN 1
                        ELSE pyramids.count + 1
                      END
        """,
            (user_id, symbol, new_side, exchange),
        )
        conn.commit()

def reset_pyramid(user_id: int, symbol: str, exchange: str = "bybit"):
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM pyramids WHERE user_id=? AND symbol=? AND exchange=?", (user_id, symbol, exchange)
        )
        conn.commit()

def get_all_pyramided_symbols(user_id: int, exchange: str = "bybit") -> list[str]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT symbol FROM pyramids WHERE user_id=? AND exchange=?", (user_id, exchange)
        ).fetchall()
    return [r[0] for r in rows]

# ------------------------------------------------------------------------------------
# Signals
# ------------------------------------------------------------------------------------
def add_signal(
    raw_data: str,  # Column is 'raw_data' in DB
    timeframe: str | None,  # Column is 'timeframe' in DB
    side: str | None,
    symbol: str | None,
    price: float | None,
    oi_prev: float | None,
    oi_now: float | None,
    oi_chg: float | None,
    vol_from: float | None,
    vol_to: float | None,
    price_chg: float | None,
    vol_delta: float | None,
    rsi: float | None,
    bb_hi: float | None,
    bb_lo: float | None,
) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """
          INSERT INTO signals(
            raw_data, timeframe, side, symbol, price,
            oi_prev, oi_now, oi_chg, vol_from, vol_to, price_chg,
            vol_delta, rsi, bb_hi, bb_lo
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                raw_data,
                timeframe,
                side,
                symbol,
                price,
                oi_prev,
                oi_now,
                oi_chg,
                vol_from,
                vol_to,
                price_chg,
                vol_delta,
                rsi,
                bb_hi,
                bb_lo,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)

def fetch_signal_by_id(signal_id: int) -> dict | None:
    cols = [
        "raw_data",  # Column is 'raw_data' in DB
        "timeframe",  # Column is 'timeframe' in DB
        "side",
        "symbol",
        "price",
        "oi_prev",
        "oi_now",
        "oi_chg",
        "vol_from",
        "vol_to",
        "price_chg",
        "vol_delta",
        "rsi",
        "bb_hi",
        "bb_lo",
    ]
    with get_conn() as conn:
        row = conn.execute(
            f"""
          SELECT {",".join(cols)}
            FROM signals
           WHERE id = ?
        """,
            (signal_id,),
        ).fetchone()
    return dict(zip(cols, row)) if row else None

def get_last_signal_id(user_id: int, symbol: str, timeframe: str) -> int | None:
    # Сигналы — глобальные; user_id здесь для совместимости с интерфейсом
    with get_conn() as conn:
        # First try exact match by symbol column
        row = conn.execute(
            """
          SELECT id FROM signals WHERE symbol=? AND (timeframe=? OR timeframe IS NULL)
          ORDER BY ts DESC LIMIT 1
        """,
            (symbol, timeframe),
        ).fetchone()
        if row:
            return int(row[0])
        
        # Fallback: search by symbol in raw_data (for signals with symbol=NULL)
        # Look for patterns like [SYMBOL] or "SYMBOL" or "🔔 SYMBOL"
        row = conn.execute(
            """
          SELECT id FROM signals 
          WHERE (raw_data LIKE ? OR raw_data LIKE ? OR raw_data LIKE ?)
          ORDER BY ts DESC LIMIT 1
        """,
            (f'%[{symbol}]%', f'%🔔 {symbol}%', f'%🔔{symbol}%'),
        ).fetchone()
        return int(row[0]) if row else None


def get_last_signal_by_symbol_in_raw(symbol: str) -> dict | None:
    """
    Search for most recent signal containing symbol in raw_data.
    Searches all known signal formats:
    - [SYMBOL] - legacy format
    - 🔔 SYMBOL - Enliko format  
    - 🪙 SYMBOL - Fibonacci format
    - SHORT/LONG SYMBOL - Scryptomera format
    - @ SYMBOL - OI/Scalper format with price
    - Just SYMBOL anywhere in message
    """
    cols = ["id", "raw_data", "ts", "timeframe", "side", "symbol", "price"]
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, raw_data, ts, timeframe, side, symbol, price 
            FROM signals 
            WHERE raw_data LIKE %s 
               OR raw_data LIKE %s 
               OR raw_data LIKE %s
               OR raw_data LIKE %s
               OR raw_data LIKE %s
               OR raw_data LIKE %s
               OR raw_data LIKE %s
            ORDER BY ts DESC LIMIT 1
            """,
            (
                f'%[{symbol}]%',           # [SYMBOL]
                f'%🔔 {symbol}%',          # 🔔 SYMBOL (Enliko)
                f'%🔔{symbol}%',           # 🔔SYMBOL (Enliko no space)
                f'%🪙 {symbol}%',          # 🪙 SYMBOL (Fibonacci)
                f'%SHORT {symbol}%',       # SHORT SYMBOL (Scryptomera)
                f'%LONG {symbol}%',        # LONG SYMBOL (Scryptomera)
                f'%{symbol} @%',           # SYMBOL @ price (OI)
            ),
        ).fetchone()
    return dict(zip(cols, row)) if row else None


def get_recent_signal_for_position(symbol: str, side: str, within_seconds: int = 180) -> dict | None:
    """
    Find a recent signal for this symbol+side within the last N seconds.
    
    This is used when bot detects an existing position on exchange to determine
    which strategy opened it. The signal must:
    1. Be for the same symbol
    2. Be for the same direction (Buy/Sell)
    3. Be within the time window (default 3 minutes)
    
    Returns signal dict or None.
    
    IMPORTANT: This function is safe to use for position detection because:
    - It checks BOTH symbol AND side match
    - It only looks back a short time window (not all signals)
    - It's used after confirming the position is new (not in active_positions)
    """
    cols = ["id", "raw_data", "ts", "timeframe", "side", "symbol", "price"]
    
    # Normalize side for comparison
    if side == "Buy":
        side_patterns = ("Buy", "LONG", "Long", "long")
    else:
        side_patterns = ("Sell", "SHORT", "Short", "short")
    
    with get_conn() as conn:
        # Search for signals within time window for this symbol
        row = conn.execute(
            """
            SELECT id, raw_data, ts, timeframe, side, symbol, price 
            FROM signals 
            WHERE symbol = %s
            AND ts > NOW() - make_interval(secs => %s)
            ORDER BY ts DESC LIMIT 1
            """,
            (symbol, within_seconds),
        ).fetchone()
        
        if row:
            sig = dict(zip(cols, row))
            # Verify side matches (signal side may be Buy/Sell or Long/Short)
            sig_side = (sig.get("side") or "").upper()
            raw_msg = (sig.get("raw_data") or "").upper()
            
            if side == "Buy":
                if sig_side in ("BUY", "LONG") or "LONG" in raw_msg[:50]:
                    return sig
            else:
                if sig_side in ("SELL", "SHORT") or "SHORT" in raw_msg[:50]:
                    return sig
            # Side doesn't match - this signal is for opposite direction
            return None
        
        return None


# ------------------------------------------------------------------------------------
# Active positions
# ------------------------------------------------------------------------------------

def _normalize_env(account_type: str) -> str:
    """Convert account_type to unified env (paper/live)."""
    mapping = {
        "demo": "paper",
        "testnet": "paper",
        "real": "live",
        "mainnet": "live",
        "paper": "paper",
        "live": "live",
    }
    return mapping.get(account_type.lower() if account_type else "demo", "paper")


def add_active_position(
    user_id: int,
    symbol: str,
    side: str,
    entry_price: float,
    size: float,
    timeframe: str = "24h",
    signal_id: int | None = None,
    strategy: str | None = None,
    account_type: str = "demo",
    # P0.3: New fields for proper tracking
    source: str = "bot",  # 'bot', 'webapp', 'monitor'
    opened_by: str = "bot",
    exchange: str = "bybit",
    sl_price: float | None = None,
    tp_price: float | None = None,
    leverage: int | None = None,
    client_order_id: str | None = None,
    exchange_order_id: str | None = None,
    env: str | None = None,  # Unified env (paper/live)
    use_atr: bool = False,  # P0.5: ATR trailing enabled for this position
    # P1: Save applied SL/TP percentages at position open time
    applied_sl_pct: float | None = None,
    applied_tp_pct: float | None = None,
):
    """
    UPSERT с обновлением ключевых полей.
    PRIMARY KEY включает account_type - позволяет иметь одновременно Demo и Real позиции.
    
    P0.3 ВАЖНО: 
    - НЕ перезаписываем strategy на NULL (COALESCE)
    - НЕ перезаписываем sl_price/tp_price если уже есть и manual_sltp_override=1
    - source указывает откуда создана позиция
    
    env автоматически вычисляется из account_type если не указан.
    """
    ensure_user(user_id)
    
    # Auto-calculate env from account_type if not provided
    if env is None:
        env = _normalize_env(account_type)
    
    # Convert use_atr bool to int for SQLite
    use_atr_int = 1 if use_atr else 0
    
    with get_conn() as conn:
        conn.execute(
            """
          INSERT INTO active_positions
            (user_id, symbol, account_type, side, entry_price, size, timeframe, signal_id, 
             dca_10_done, dca_25_done, strategy, source, opened_by, exchange,
             sl_price, tp_price, leverage, client_order_id, exchange_order_id, env, use_atr,
             applied_sl_pct, applied_tp_pct)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
          ON CONFLICT(user_id, symbol, account_type, exchange) DO UPDATE SET
            side             = excluded.side,
            entry_price      = excluded.entry_price,
            size             = excluded.size,
            timeframe        = COALESCE(excluded.timeframe, active_positions.timeframe),
            signal_id        = COALESCE(excluded.signal_id, active_positions.signal_id),
            -- P0.3: НЕ перезаписываем strategy если уже есть реальная стратегия
            -- Не позволяем 'manual'/'unknown' перезаписать реальную стратегию
            strategy         = CASE
                                 WHEN excluded.strategy IS NOT NULL 
                                      AND excluded.strategy NOT IN ('manual', 'unknown')
                                 THEN excluded.strategy
                                 WHEN active_positions.strategy IS NOT NULL
                                      AND active_positions.strategy NOT IN ('manual', 'unknown')
                                 THEN active_positions.strategy
                                 ELSE COALESCE(
                                   NULLIF(NULLIF(excluded.strategy, 'manual'), 'unknown'),
                                   NULLIF(NULLIF(active_positions.strategy, 'manual'), 'unknown')
                                 )
                               END,
            -- P0.3: Обновляем source/exchange только если они пустые
            source           = COALESCE(active_positions.source, excluded.source),
            exchange         = COALESCE(excluded.exchange, active_positions.exchange),
            -- P0.8: Не перезаписываем SL/TP если manual_sltp_override=1
            sl_price         = CASE 
                                 WHEN active_positions.manual_sltp_override = 1 THEN active_positions.sl_price 
                                 ELSE COALESCE(excluded.sl_price, active_positions.sl_price) 
                               END,
            tp_price         = CASE 
                                 WHEN active_positions.manual_sltp_override = 1 THEN active_positions.tp_price 
                                 ELSE COALESCE(excluded.tp_price, active_positions.tp_price) 
                               END,
            leverage         = COALESCE(excluded.leverage, active_positions.leverage),
            client_order_id  = COALESCE(excluded.client_order_id, active_positions.client_order_id),
            exchange_order_id = COALESCE(excluded.exchange_order_id, active_positions.exchange_order_id),
            env              = COALESCE(excluded.env, active_positions.env),
            use_atr          = excluded.use_atr,
            applied_sl_pct   = COALESCE(excluded.applied_sl_pct, active_positions.applied_sl_pct),
            applied_tp_pct   = COALESCE(excluded.applied_tp_pct, active_positions.applied_tp_pct)
        """,
            (user_id, symbol, account_type, side, entry_price, size, timeframe, signal_id, 
             strategy, source, opened_by, exchange, sl_price, tp_price, leverage, 
             client_order_id, exchange_order_id, env, use_atr_int, applied_sl_pct, applied_tp_pct),
        )
        conn.commit()


def get_active_positions(user_id: int, account_type: str | None = None, exchange: str | None = None, env: str | None = None) -> list[dict]:
    """
    Получает активные позиции пользователя.
    Фильтры:
    - account_type: 'demo', 'real', 'testnet', 'mainnet'
    - exchange: 'bybit', 'hyperliquid'  
    - env: 'paper', 'live' (unified env)
    """
    # Normalize 'both' -> 'demo' or 'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange=exchange or 'bybit')
    
    with get_conn() as conn:
        # Build query based on filters
        base_query = """
            SELECT symbol, side, entry_price, size, open_ts, timeframe, signal_id, 
                   COALESCE(dca_10_done, 0), COALESCE(dca_25_done, 0), strategy, account_type,
                   source, opened_by, exchange, sl_price, tp_price, 
                   manual_sltp_override, manual_sltp_ts,
                   atr_activated, atr_activation_price, atr_last_stop_price, atr_last_update_ts,
                   leverage, client_order_id, exchange_order_id, env, COALESCE(use_atr, 0) as use_atr,
                   applied_sl_pct, applied_tp_pct
            FROM active_positions
            WHERE user_id=?
        """
        params = [user_id]
        
        if account_type:
            base_query += " AND account_type=?"
            params.append(account_type)
        
        if exchange:
            base_query += " AND exchange=?"
            params.append(exchange)
        
        if env:
            base_query += " AND env=?"
            params.append(env)
        
        rows = conn.execute(base_query, params).fetchall()
        
        return [
            {
                "symbol": r[0],
                "side": r[1],
                "entry_price": r[2],
                "size": r[3],
                "open_ts": r[4],
                "timeframe": r[5],
                "signal_id": r[6],
                "dca_10_done": bool(r[7]),
                "dca_25_done": bool(r[8]),
                "strategy": r[9],
                "account_type": r[10] or "demo",
                # New fields
                "source": r[11] or "bot",
                "opened_by": r[12] or "bot",
                "exchange": r[13] or "bybit",
                "sl_price": r[14],
                "tp_price": r[15],
                "manual_sltp_override": bool(r[16]) if r[16] else False,
                "manual_sltp_ts": r[17],
                # ATR state (P0.4)
                "atr_activated": bool(r[18]) if r[18] else False,
                "atr_activation_price": r[19],
                "atr_last_stop_price": r[20],
                "atr_last_update_ts": r[21],
                # Other
                "leverage": r[22],
                "client_order_id": r[23],
                "exchange_order_id": r[24],
                # Unified env
                "env": r[25] or _normalize_env(r[10] or "demo"),
                # P0.5: ATR enabled flag
                "use_atr": bool(r[26]) if len(r) > 26 else False,
                # Applied SL/TP percentages at open time (Fix #2)
                "applied_sl_pct": r[27] if len(r) > 27 else None,
                "applied_tp_pct": r[28] if len(r) > 28 else None,
            }
            for r in rows
        ]


def remove_active_position(user_id: int, symbol: str, account_type: str | None = None, entry_price: float | None = None, entry_price_tolerance: float = 0.001, exchange: str = "bybit"):
    """
    Удаляет активную позицию с поддержкой multitenancy.
    Если account_type указан - удаляет только для этого типа.
    Если не указан - удаляет все позиции по символу (для обратной совместимости).
    
    IMPORTANT: If entry_price is provided, only deletes if the position's entry_price matches
    (within tolerance). This prevents race condition where a NEW position opened by signal handler
    gets deleted by monitor loop closing the OLD position.
    
    Args:
        user_id: User ID
        symbol: Trading symbol
        account_type: demo/real/testnet (optional)
        entry_price: Expected entry price to match (optional, for race condition protection)
        entry_price_tolerance: Relative tolerance for price matching (default 0.1% = 0.001)
        exchange: 'bybit' or 'hyperliquid' (default 'bybit')
    """
    import logging
    logger = logging.getLogger(__name__)
    
    with get_conn() as conn:
        # If entry_price is provided, verify it matches before deleting
        if entry_price is not None:
            # First check current entry_price in DB
            if account_type:
                cur = conn.execute(
                    "SELECT entry_price FROM active_positions WHERE user_id=? AND symbol=? AND account_type=? AND exchange=?",
                    (user_id, symbol, account_type, exchange),
                )
            else:
                cur = conn.execute(
                    "SELECT entry_price FROM active_positions WHERE user_id=? AND symbol=? AND exchange=?",
                    (user_id, symbol, exchange),
                )
            row = cur.fetchone()
            
            if row:
                db_entry_price = row[0]
                if db_entry_price and entry_price:
                    # Check if prices match within tolerance
                    price_diff = abs(db_entry_price - entry_price) / entry_price
                    if price_diff > entry_price_tolerance:
                        logger.warning(
                            f"[{user_id}] {symbol}: Skipping position removal - entry_price mismatch! "
                            f"Expected={entry_price:.6f}, DB has={db_entry_price:.6f}, diff={price_diff*100:.2f}%. "
                            f"This may indicate a new position was opened while closing old one."
                        )
                        return  # Don't delete - this is a different position!
        
        # Proceed with deletion with exchange filter
        if account_type:
            conn.execute(
                "DELETE FROM active_positions WHERE user_id=? AND symbol=? AND account_type=? AND exchange=?",
                (user_id, symbol, account_type, exchange),
            )
        else:
            conn.execute(
                "DELETE FROM active_positions WHERE user_id=? AND symbol=? AND exchange=?",
                (user_id, symbol, exchange),
            )
        conn.commit()


def set_dca_flag(user_id: int, symbol: str, level: int, value: bool = True, account_type: str = "demo", exchange: str = "bybit"):
    """
    Устанавливает флаг DCA для позиции.
    level: 10 или 25 (процент)
    """
    col = f"dca_{level}_done"
    if col not in ("dca_10_done", "dca_25_done"):
        raise ValueError(f"Invalid DCA level: {level}")
    with get_conn() as conn:
        conn.execute(
            f"UPDATE active_positions SET {col}=? WHERE user_id=? AND symbol=? AND account_type=? AND exchange=?",
            (1 if value else 0, user_id, symbol, account_type, exchange),
        )
        conn.commit()


def get_dca_flag(user_id: int, symbol: str, level: int, account_type: str = "demo", exchange: str = "bybit") -> bool:
    """
    Проверяет, был ли выполнен DCA на данном уровне.
    level: 10 или 25 (процент)
    """
    col = f"dca_{level}_done"
    if col not in ("dca_10_done", "dca_25_done"):
        raise ValueError(f"Invalid DCA level: {level}")
    with get_conn() as conn:
        row = conn.execute(
            f"SELECT {col} FROM active_positions WHERE user_id=? AND symbol=? AND account_type=? AND exchange=?",
            (user_id, symbol, account_type, exchange),
        ).fetchone()
    return bool(row[0]) if row else False


def set_ptp_flag(user_id: int, symbol: str, step: int, value: bool = True, account_type: str = "demo", exchange: str = "bybit"):
    """
    Sets Partial Take Profit step done flag for a position.
    step: 1 or 2
    """
    col = f"ptp_step_{step}_done"
    if col not in ("ptp_step_1_done", "ptp_step_2_done"):
        raise ValueError(f"Invalid PTP step: {step}")
    with get_conn() as conn:
        conn.execute(
            f"UPDATE active_positions SET {col}=? WHERE user_id=? AND symbol=? AND account_type=? AND exchange=?",
            (1 if value else 0, user_id, symbol, account_type, exchange),
        )
        conn.commit()


def get_ptp_flag(user_id: int, symbol: str, step: int, account_type: str = "demo", exchange: str = "bybit") -> bool:
    """
    Checks if Partial TP step was already executed for position.
    step: 1 or 2
    """
    col = f"ptp_step_{step}_done"
    if col not in ("ptp_step_1_done", "ptp_step_2_done"):
        raise ValueError(f"Invalid PTP step: {step}")
    with get_conn() as conn:
        row = conn.execute(
            f"SELECT {col} FROM active_positions WHERE user_id=? AND symbol=? AND account_type=? AND exchange=?",
            (user_id, symbol, account_type, exchange),
        ).fetchone()
    return bool(row[0]) if row else False


def sync_position_entry_price(user_id: int, symbol: str, new_entry_price: float, account_type: str = "demo", exchange: str = "bybit") -> bool:
    """
    Синхронизирует entry_price позиции с биржей.
    
    Вызывается когда ATR монитор обнаруживает что entry на бирже != entry в БД.
    Это происходит когда юзер делает DCA/добор и средняя цена меняется.
    
    Returns:
        True если была произведена синхронизация, False если не нужна
    """
    with get_conn() as conn:
        row = conn.execute(
            "SELECT entry_price FROM active_positions WHERE user_id=? AND symbol=? AND account_type=? AND exchange=?",
            (user_id, symbol, account_type, exchange),
        ).fetchone()
        
        if not row:
            return False
        
        db_entry = float(row[0]) if row[0] else 0
        if db_entry == 0:
            return False
        
        # Check if entry changed significantly (>0.1%)
        diff_pct = abs(new_entry_price - db_entry) / db_entry * 100
        if diff_pct < 0.1:
            return False
        
        # Update entry_price
        conn.execute(
            "UPDATE active_positions SET entry_price=? WHERE user_id=? AND symbol=? AND account_type=? AND exchange=?",
            (new_entry_price, user_id, symbol, account_type, exchange),
        )
        conn.commit()
        return True


def get_positions_by_target(user_id: int, exchange: str, env: str) -> list[dict]:
    """
    Получает позиции по target (exchange + env).
    
    Это основная функция для мониторинга - итерирует по всем target'ам пользователя.
    
    Args:
        user_id: ID пользователя
        exchange: 'bybit' или 'hyperliquid'
        env: 'paper' или 'live'
    
    Returns:
        Список позиций для данного target
    """
    return get_active_positions(user_id, exchange=exchange, env=env)


def get_all_positions_by_targets(user_id: int, targets: list[dict]) -> dict[str, list[dict]]:
    """
    Получает позиции для всех target'ов пользователя.
    
    Args:
        user_id: ID пользователя
        targets: Список target'ов [{exchange, env}, ...]
    
    Returns:
        Dict: {target_key: [positions]}
        где target_key = "exchange:env" (например "bybit:paper")
    """
    result = {}
    for target in targets:
        exchange = target.get("exchange") or target.exchange if hasattr(target, 'exchange') else "bybit"
        env = target.get("env") or target.env if hasattr(target, 'env') else "paper"
        key = f"{exchange}:{env}"
        result[key] = get_positions_by_target(user_id, exchange, env)
    return result


def update_position_strategy(user_id: int, symbol: str, strategy: str, account_type: str = "demo", exchange: str = "bybit") -> bool:
    """
    Обновляет strategy для существующей позиции с поддержкой multitenancy.
    Возвращает True если позиция была обновлена, False если не найдена.
    """
    with get_conn() as conn:
        cursor = conn.execute(
            "UPDATE active_positions SET strategy=? WHERE user_id=? AND symbol=? AND account_type=? AND exchange=?",
            (strategy, user_id, symbol, account_type, exchange),
        )
        conn.commit()
        return cursor.rowcount > 0


# ------------------------------------------------------------------------------------
# P0.4: ATR trailing stop state persistence
# ------------------------------------------------------------------------------------
def update_atr_state(
    user_id: int, 
    symbol: str, 
    account_type: str = "demo",
    atr_activated: bool = False,
    atr_activation_price: float | None = None,
    atr_last_stop_price: float | None = None,
    exchange: str = "bybit",
) -> bool:
    """
    Обновляет ATR trailing stop state для позиции.
    Возвращает True если позиция была обновлена.
    """
    import time
    with get_conn() as conn:
        cursor = conn.execute(
            """UPDATE active_positions SET 
                atr_activated = ?,
                atr_activation_price = ?,
                atr_last_stop_price = ?,
                atr_last_update_ts = ?
            WHERE user_id=? AND symbol=? AND account_type=? AND exchange=?""",
            (1 if atr_activated else 0, atr_activation_price, atr_last_stop_price,
             int(time.time()), user_id, symbol, account_type, exchange),
        )
        conn.commit()
        return cursor.rowcount > 0


def get_atr_state(user_id: int, symbol: str, account_type: str = "demo", exchange: str = "bybit") -> dict | None:
    """
    Получает ATR trailing stop state для позиции.
    Возвращает dict с полями: atr_activated, atr_activation_price, atr_last_stop_price, atr_last_update_ts
    или None если позиция не найдена.
    """
    with get_conn() as conn:
        row = conn.execute(
            """SELECT atr_activated, atr_activation_price, atr_last_stop_price, atr_last_update_ts
            FROM active_positions WHERE user_id=? AND symbol=? AND account_type=? AND exchange=?""",
            (user_id, symbol, account_type, exchange),
        ).fetchone()
        
        if row:
            return {
                "atr_activated": bool(row[0]) if row[0] else False,
                "atr_activation_price": row[1],
                "atr_last_stop_price": row[2],
                "atr_last_update_ts": row[3],
            }
        return None


def clear_atr_state(user_id: int, symbol: str, account_type: str = "demo", exchange: str = "bybit") -> bool:
    """
    Сбрасывает ATR state для позиции.
    Вызывается при закрытии позиции.
    """
    with get_conn() as conn:
        cursor = conn.execute(
            """UPDATE active_positions SET 
                atr_activated = 0,
                atr_activation_price = NULL,
                atr_last_stop_price = NULL,
                atr_last_update_ts = NULL
            WHERE user_id=? AND symbol=? AND account_type=? AND exchange=?""",
            (user_id, symbol, account_type, exchange),
        )
        conn.commit()
        return cursor.rowcount > 0


# ------------------------------------------------------------------------------------
# P0.8: Manual SL/TP override - prevents bot from overwriting manual changes
# ------------------------------------------------------------------------------------
def set_manual_sltp_override(
    user_id: int, 
    symbol: str, 
    account_type: str = "demo",
    sl_price: float | None = None,
    tp_price: float | None = None,
    exchange: str = "bybit",
) -> bool:
    """
    Устанавливает manual_sltp_override=1 и обновляет SL/TP цены.
    После этого бот не будет перезаписывать SL/TP в мониторинге.
    Поддержка multitenancy через exchange параметр.
    """
    import time
    with get_conn() as conn:
        cursor = conn.execute(
            """UPDATE active_positions SET 
                manual_sltp_override = 1,
                manual_sltp_ts = ?,
                sl_price = COALESCE(?, sl_price),
                tp_price = COALESCE(?, tp_price)
            WHERE user_id=? AND symbol=? AND account_type=? AND exchange=?""",
            (int(time.time()), sl_price, tp_price, user_id, symbol, account_type, exchange),
        )
        conn.commit()
        return cursor.rowcount > 0


def clear_manual_sltp_override(user_id: int, symbol: str, account_type: str = "demo", exchange: str = "bybit") -> bool:
    """
    Сбрасывает manual_sltp_override - бот снова может управлять SL/TP.
    Поддержка multitenancy через exchange параметр.
    """
    with get_conn() as conn:
        cursor = conn.execute(
            """UPDATE active_positions SET 
                manual_sltp_override = 0,
                manual_sltp_ts = NULL
            WHERE user_id=? AND symbol=? AND account_type=? AND exchange=?""",
            (user_id, symbol, account_type, exchange),
        )
        conn.commit()
        return cursor.rowcount > 0


def is_manual_sltp_override(user_id: int, symbol: str, account_type: str = "demo", exchange: str = "bybit") -> bool:
    """
    Проверяет, установлен ли manual_sltp_override для позиции.
    Возвращает True если бот не должен трогать SL/TP.
    Поддержка multitenancy через exchange параметр.
    """
    with get_conn() as conn:
        row = conn.execute(
            "SELECT manual_sltp_override FROM active_positions WHERE user_id=? AND symbol=? AND account_type=? AND exchange=?",
            (user_id, symbol, account_type, exchange),
        ).fetchone()
        return bool(row[0]) if row and row[0] else False


def update_position_sltp(
    user_id: int,
    symbol: str,
    account_type: str = "demo",
    sl_price: float | None = None,
    tp_price: float | None = None,
    respect_manual_override: bool = True,
    exchange: str = "bybit",
) -> bool:
    """
    Обновляет SL/TP цены для позиции с поддержкой multitenancy.
    Если respect_manual_override=True и manual_sltp_override=1, ничего не делает.
    """
    if respect_manual_override and is_manual_sltp_override(user_id, symbol, account_type, exchange=exchange):
        return False
    
    with get_conn() as conn:
        updates = []
        params = []
        
        if sl_price is not None:
            updates.append("sl_price = ?")
            params.append(sl_price)
        if tp_price is not None:
            updates.append("tp_price = ?")
            params.append(tp_price)
        
        if not updates:
            return False
        
        params.extend([user_id, symbol, account_type, exchange])
        cursor = conn.execute(
            f"UPDATE active_positions SET {', '.join(updates)} WHERE user_id=? AND symbol=? AND account_type=? AND exchange=?",
            params,
        )
        conn.commit()
        return cursor.rowcount > 0


def update_position_applied_sltp(
    user_id: int,
    symbol: str,
    account_type: str = "demo",
    applied_sl_pct: float | None = None,
    applied_tp_pct: float | None = None,
    sl_price: float | None = None,
    tp_price: float | None = None,
    exchange: str = "bybit",
) -> bool:
    """
    Обновляет applied_sl_pct, applied_tp_pct, sl_price, tp_price для позиции.
    Эти поля сохраняют SL/TP% и цены которые были использованы при установке,
    чтобы последующие циклы мониторинга не пересчитывали SL/TP.
    """
    with get_conn() as conn:
        updates = []
        params = []
        
        if applied_sl_pct is not None:
            updates.append("applied_sl_pct = ?")
            params.append(applied_sl_pct)
        if applied_tp_pct is not None:
            updates.append("applied_tp_pct = ?")
            params.append(applied_tp_pct)
        if sl_price is not None:
            updates.append("sl_price = ?")
            params.append(sl_price)
        if tp_price is not None:
            updates.append("tp_price = ?")
            params.append(tp_price)
        
        if not updates:
            return False
        
        params.extend([user_id, symbol, account_type, exchange])
        cursor = conn.execute(
            f"UPDATE active_positions SET {', '.join(updates)} WHERE user_id=? AND symbol=? AND account_type=? AND exchange=?",
            params,
        )
        conn.commit()
        return cursor.rowcount > 0


# ------------------------------------------------------------------------------------
# P0.1: Exchange Accounts (execution_targets support) - LEGACY
# NOTE: Main get_execution_targets is defined earlier in file (~line 1533) with routing_policy
# This function is kept for backward compatibility with exchange_accounts table
# ------------------------------------------------------------------------------------
def _get_execution_targets_from_exchange_accounts(user_id: int, strategy: str | None = None) -> list[dict]:
    """
    LEGACY: Получает targets из таблицы exchange_accounts.
    Используется как fallback когда нет routing_policy настроек.
    
    Returns list of dicts with env field for compatibility with new system.
    """
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT id, exchange, account_type, label, is_enabled, is_default,
                      max_positions, max_leverage, risk_limit_pct, priority
               FROM exchange_accounts
               WHERE user_id=? AND is_enabled=1
               ORDER BY priority, exchange, account_type""",
            (user_id,),
        ).fetchall()
        
        targets = []
        for r in rows:
            exchange = r[1]
            account_type = r[2]
            # Map account_type to env
            if account_type in ("demo", "testnet"):
                env = "paper"
            else:
                env = "live"
            
            targets.append({
                "id": r[0],
                "exchange": exchange,
                "account_type": account_type,
                "env": env,  # Added for compatibility
                "label": r[3],
                "is_enabled": bool(r[4]),
                "is_default": bool(r[5]),
                "max_positions": r[6] or 10,
                "max_leverage": r[7] or 100,
                "risk_limit_pct": r[8] or 30.0,
                "priority": r[9] or 0,
            })
        
        # Fallback: если нет записей в exchange_accounts, используем старую логику
        if not targets:
            targets = _get_legacy_execution_targets_from_users(user_id)
        
        return targets


def _get_legacy_execution_targets_from_users(user_id: int) -> list[dict]:
    """
    Fallback для старых пользователей без exchange_accounts записей.
    Использует trading_mode и hl_enabled из users.
    Returns targets with env field for compatibility with new system.
    """
    with get_conn() as conn:
        row = conn.execute(
            """SELECT trading_mode, demo_api_key, real_api_key, 
                      hl_private_key, hl_enabled, exchange_type
               FROM users WHERE user_id=?""",
            (user_id,),
        ).fetchone()
        
        if not row:
            return []
        
        trading_mode = row[0] or "demo"
        has_demo = bool(row[1])
        has_real = bool(row[2])
        has_hl = bool(row[3])
        hl_enabled = bool(row[4])
        exchange_type = row[5] or "bybit"
        
        targets = []
        
        # Bybit targets based on trading_mode
        if exchange_type == "bybit" or exchange_type == "both":
            if trading_mode in ("demo", "both") and has_demo:
                targets.append({
                    "exchange": "bybit",
                    "account_type": "demo",
                    "env": "paper",  # Added for compatibility
                    "is_enabled": True,
                    "is_default": trading_mode == "demo",
                    "max_positions": 10,
                    "max_leverage": 100,
                    "risk_limit_pct": 30.0,
                    "priority": 0,
                })
            if trading_mode in ("real", "both") and has_real:
                targets.append({
                    "exchange": "bybit",
                    "account_type": "real",
                    "env": "live",  # Added for compatibility
                    "is_enabled": True,
                    "is_default": trading_mode == "real",
                    "max_positions": 10,
                    "max_leverage": 100,
                    "risk_limit_pct": 30.0,
                    "priority": 1,
                })
        
        # HyperLiquid target
        if (exchange_type == "hyperliquid" or exchange_type == "both") and has_hl and hl_enabled:
            targets.append({
                "exchange": "hyperliquid",
                "account_type": "mainnet",  # or testnet based on hl_testnet
                "env": "live",  # Added for compatibility
                "is_enabled": True,
                "is_default": exchange_type == "hyperliquid",
                "max_positions": 10,
                "max_leverage": 50,
                "risk_limit_pct": 30.0,
                "priority": 2,
            })
        
        return targets


def add_exchange_account(
    user_id: int,
    exchange: str,
    account_type: str,
    api_key: str | None = None,
    api_secret: str | None = None,
    extra_json: str | None = None,
    label: str | None = None,
    is_enabled: bool = True,
    is_default: bool = False,
    max_positions: int = 10,
    max_leverage: int = 100,
    risk_limit_pct: float = 30.0,
    priority: int = 0,
) -> int | None:
    """
    Добавляет exchange account. Возвращает ID или None при ошибке.
    """
    ensure_user(user_id)
    import time
    with get_conn() as conn:
        try:
            cur = conn.execute(
                """INSERT INTO exchange_accounts
                    (user_id, exchange, account_type, api_key, api_secret, extra_json,
                     label, is_enabled, is_default, max_positions, max_leverage,
                     risk_limit_pct, priority, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(user_id, exchange, account_type) DO UPDATE SET
                     api_key = excluded.api_key,
                     api_secret = excluded.api_secret,
                     extra_json = COALESCE(excluded.extra_json, exchange_accounts.extra_json),
                     label = COALESCE(excluded.label, exchange_accounts.label),
                     is_enabled = excluded.is_enabled,
                     is_default = excluded.is_default,
                     max_positions = excluded.max_positions,
                     max_leverage = excluded.max_leverage,
                     risk_limit_pct = excluded.risk_limit_pct,
                     priority = excluded.priority,
                     updated_at = excluded.updated_at
                """,
                (user_id, exchange, account_type, api_key, api_secret, extra_json,
                 label, 1 if is_enabled else 0, 1 if is_default else 0,
                 max_positions, max_leverage, risk_limit_pct, priority,
                 int(time.time()), int(time.time())),
            )
            conn.commit()
            return cur.lastrowid
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"add_exchange_account error: {e}")
            return None


def get_exchange_account(user_id: int, exchange: str, account_type: str) -> dict | None:
    """
    Получает конкретный exchange account.
    """
    with get_conn() as conn:
        row = conn.execute(
            """SELECT id, exchange, account_type, api_key, api_secret, extra_json,
                      label, is_enabled, is_default, max_positions, max_leverage,
                      risk_limit_pct, priority
               FROM exchange_accounts
               WHERE user_id=? AND exchange=? AND account_type=?""",
            (user_id, exchange, account_type),
        ).fetchone()
        
        if row:
            return {
                "id": row[0],
                "exchange": row[1],
                "account_type": row[2],
                "api_key": row[3],
                "api_secret": row[4],
                "extra_json": row[5],
                "label": row[6],
                "is_enabled": bool(row[7]),
                "is_default": bool(row[8]),
                "max_positions": row[9] or 10,
                "max_leverage": row[10] or 100,
                "risk_limit_pct": row[11] or 30.0,
                "priority": row[12] or 0,
            }
        return None


def set_exchange_account_enabled(user_id: int, exchange: str, account_type: str, enabled: bool) -> bool:
    """
    Включает/выключает exchange account.
    """
    with get_conn() as conn:
        cursor = conn.execute(
            "UPDATE exchange_accounts SET is_enabled=? WHERE user_id=? AND exchange=? AND account_type=?",
            (1 if enabled else 0, user_id, exchange, account_type),
        )
        conn.commit()
        return cursor.rowcount > 0

# ------------------------------------------------------------------------------------
# Pending limit orders
# ------------------------------------------------------------------------------------
def add_pending_limit_order(
    user_id: int,
    order_id: str,
    symbol: str,
    side: str,
    qty: float,
    price: float,
    signal_id: int,
    created_ts: int,
    time_in_force: str = "GTC",
    strategy: str | None = None,
    account_type: str = "demo",
    exchange: str = "bybit",
):
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute(
            """
          INSERT INTO pending_limit_orders
            (user_id, order_id, symbol, side, qty, price, signal_id, created_ts, time_in_force, strategy, account_type, exchange)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
          ON CONFLICT (user_id, order_id, exchange) DO NOTHING
        """,
            (user_id, order_id, symbol, side, qty, price, signal_id, created_ts, time_in_force, strategy, account_type, exchange),
        )
        conn.commit()

def get_pending_limit_orders(user_id: int, exchange: str = "bybit") -> list[dict]:
    """
    Возвращает список отложенных лимитных ордеров пользователя для указанной биржи,
    отсортированных от новых к старым. Гарантирует наличие ключа
    `time_in_force`, `strategy` и `account_type` (если колонок нет в БД — подставит дефолты).
    
    Args:
        user_id: ID пользователя
        exchange: Биржа ('bybit' или 'hyperliquid')
    """
    with get_conn() as conn:
        # На всякий случай держим совместимость со старыми схемами
        has_tif = _col_exists(conn, "pending_limit_orders", "time_in_force")
        has_strategy = _col_exists(conn, "pending_limit_orders", "strategy")
        has_account_type = _col_exists(conn, "pending_limit_orders", "account_type")

        if has_tif and has_strategy and has_account_type:
            rows = conn.execute(
                """
                SELECT order_id, symbol, side, qty, price, signal_id, created_ts, time_in_force, strategy, account_type
                  FROM pending_limit_orders
                 WHERE user_id=? AND exchange=?
                 ORDER BY created_ts DESC
                """,
                (user_id, exchange),
            ).fetchall()
        elif has_tif and has_strategy:
            rows = conn.execute(
                """
                SELECT order_id, symbol, side, qty, price, signal_id, created_ts, time_in_force, strategy
                  FROM pending_limit_orders
                 WHERE user_id=? AND exchange=?
                 ORDER BY created_ts DESC
                """,
                (user_id, exchange),
            ).fetchall()
        elif has_tif:
            rows = conn.execute(
                """
                SELECT order_id, symbol, side, qty, price, signal_id, created_ts, time_in_force
                  FROM pending_limit_orders
                 WHERE user_id=? AND exchange=?
                 ORDER BY created_ts DESC
                """,
                (user_id, exchange),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT order_id, symbol, side, qty, price, signal_id, created_ts
                  FROM pending_limit_orders
                 WHERE user_id=? AND exchange=?
                 ORDER BY created_ts DESC
                """,
                (user_id, exchange),
            ).fetchall()

    result: list[dict] = []
    for r in rows:
        # распаковка с учётом наличия колонок
        if has_tif and has_strategy and has_account_type:
            order_id, symbol, side, qty, price, signal_id, created_ts, tif, strategy, account_type = r
        elif has_tif and has_strategy:
            order_id, symbol, side, qty, price, signal_id, created_ts, tif, strategy = r
            account_type = "demo"
        elif has_tif:
            order_id, symbol, side, qty, price, signal_id, created_ts, tif = r
            strategy = None
            account_type = "demo"
        else:
            order_id, symbol, side, qty, price, signal_id, created_ts = r
            tif = "GTC"
            strategy = None
            account_type = "demo"

        result.append(
            {
                "order_id": str(order_id),
                "symbol": str(symbol),
                "side": str(side),
                "qty": float(qty) if qty is not None else 0.0,
                "price": float(price) if price is not None else 0.0,
                "signal_id": int(signal_id) if signal_id is not None else 0,
                "created_ts": int(created_ts) if created_ts is not None else 0,
                "time_in_force": str(tif) if tif is not None else "GTC",
                "strategy": strategy,
                "account_type": account_type or "demo",
            }
        )
    return result

def remove_pending_limit_order(user_id: int, order_id: str, exchange: str = "bybit"):
    with get_conn() as conn:
        conn.execute(
            """
          DELETE FROM pending_limit_orders
           WHERE user_id=? AND order_id=? AND exchange=?
        """,
            (user_id, order_id, exchange),
        )
        conn.commit()

# ------------------------------------------------------------------------------------
# Trade logs
# ------------------------------------------------------------------------------------

def was_position_recently_closed(user_id: int, symbol: str, entry_price: float, seconds: int = 120, exchange: str = "bybit") -> bool:
    """
    Check if a position with the same symbol and entry price was closed recently.
    This helps detect Bybit API sync delays where closed positions still appear as open.
    
    Args:
        user_id: User ID
        symbol: Trading pair symbol
        entry_price: Entry price to match (rounded to 4 decimals)
        seconds: Time window to check (default 2 minutes)
        exchange: Exchange to filter by ('bybit' or 'hyperliquid')
    
    Returns:
        True if a matching trade was closed within the time window
    """
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(seconds=seconds)
    cutoff_str = cutoff.strftime('%Y-%m-%d %H:%M:%S')
    
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM trade_logs
            WHERE user_id = ?
              AND symbol = ?
              AND exchange = ?
              AND ABS(entry_price - ?) < 0.0001
              AND ts > ?
        """, (user_id, symbol, exchange, entry_price, cutoff_str))
        row = cur.fetchone()
        count = row[0] if row else 0
        return count > 0


def add_trade_log(
    user_id: int,
    signal_id: int | None,
    symbol: str,
    side: str,
    entry_price: float,
    exit_price: float,
    exit_reason: str,
    pnl: float,
    pnl_pct: float,
    signal_source: str | None = None,
    rsi: float | None = None,
    bb_hi: float | None = None,
    bb_lo: float | None = None,
    oi_prev: float | None = None,
    oi_now: float | None = None,
    oi_chg: float | None = None,
    vol_from: float | None = None,
    vol_to: float | None = None,
    price_chg: float | None = None,
    vol_delta: float | None = None,
    sl_pct: float | None = None,
    tp_pct: float | None = None,
    sl_price: float | None = None,
    tp_price: float | None = None,
    timeframe: str | None = None,
    entry_ts: int | None = None,
    exit_ts: int | None = None,
    exit_order_type: str | None = None,
    strategy: str | None = None,
    account_type: str = "demo",
    exchange: str = "bybit",
    fee: float = 0.0,  # Trading fee (commission) from exchange
):
    ensure_user(user_id)
    
    # Fix #7: Ensure SL/TP never go to DB as NULL/0 - use defaults
    if sl_pct is None or sl_pct <= 0:
        sl_pct = DEFAULT_SL_PCT
    if tp_pct is None or tp_pct <= 0:
        tp_pct = DEFAULT_TP_PCT
    
    with get_conn() as conn:
        # CRITICAL: Check for duplicate trade before inserting
        # A trade is considered duplicate if same user+symbol+side+entry_price+exit_price within last 24 hours
        # This prevents the monitoring loop from logging the same closed position multiple times
        # NOTE: We check entry_price AND exit_price instead of pnl for more reliable matching
        existing = conn.execute(
            """
            SELECT id FROM trade_logs 
            WHERE user_id = ? AND symbol = ? AND side = ? 
              AND ABS(entry_price - ?) < 0.0001 
              AND ABS(exit_price - ?) < 0.0001
              AND (exchange = ? OR (exchange IS NULL AND ? = 'bybit'))
              AND (account_type = ? OR account_type IS NULL)
              AND ts > NOW() - INTERVAL '24 hours'
            LIMIT 1
            """,
            (user_id, symbol, side, entry_price, exit_price, exchange, exchange, account_type)
        ).fetchone()
        
        if existing:
            # Duplicate detected, skip insert
            import logging
            logging.getLogger(__name__).debug(
                f"[{user_id}] Skipping duplicate trade log: {symbol} {side} pnl={pnl}"
            )
            return
        
        conn.execute(
            """
          INSERT INTO trade_logs(
            user_id, signal_id, symbol, side,
            entry_price, exit_price, exit_reason,
            pnl, pnl_pct, signal_source,
            rsi, bb_hi, bb_lo,
            oi_prev, oi_now, oi_chg, vol_from, vol_to, price_chg,
            vol_delta, sl_pct, tp_pct, sl_price, tp_price,
            timeframe, entry_ts, exit_ts, exit_order_type, strategy, account_type, exchange, fee
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                user_id,
                signal_id,
                symbol,
                side,
                entry_price,
                exit_price,
                exit_reason,
                pnl,
                pnl_pct,
                signal_source,
                rsi,
                bb_hi,
                bb_lo,
                oi_prev,
                oi_now,
                oi_chg,
                vol_from,
                vol_to,
                price_chg,
                vol_delta,
                sl_pct,
                tp_pct,
                sl_price,
                tp_price,
                timeframe,
                entry_ts,
                exit_ts,
                exit_order_type,
                strategy,
                account_type,
                exchange,
                fee,
            ),
        )
        conn.commit()


# Simple cache for trade stats (TTL 60 seconds)
_trade_stats_cache: dict = {}
_trade_stats_cache_ts: dict = {}
TRADE_STATS_CACHE_TTL = 60  # seconds


def get_trade_stats(user_id: int, strategy: str | None = None, period: str = "all", account_type: str | None = None, exchange: str | None = None) -> dict:
    """
    Получает статистику сделок пользователя.
    period: 'today', 'week', 'month', 'all'
    strategy: None = все стратегии, иначе конкретная
    account_type: 'demo', 'real', or None = все
    exchange: 'bybit', 'hyperliquid' or None = все
    """
    import datetime
    import time
    from zoneinfo import ZoneInfo
    
    # Check cache first
    cache_key = f"{user_id}:{strategy}:{period}:{account_type}:{exchange}"
    now = time.time()
    if cache_key in _trade_stats_cache:
        if now - _trade_stats_cache_ts.get(cache_key, 0) < TRADE_STATS_CACHE_TTL:
            return _trade_stats_cache[cache_key]
    
    # Normalize 'both' -> 'demo' or 'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange=exchange or 'bybit')
    
    with get_conn() as conn:
        # Базовый запрос
        where_clauses = ["user_id = ?"]
        params: list = [user_id]
        
        # Фильтр по стратегии
        if strategy:
            where_clauses.append("strategy = ?")
            params.append(strategy)
        
        # Фильтр по account_type
        if account_type:
            where_clauses.append("(account_type = ? OR account_type IS NULL)")
            params.append(account_type)
        
        # Фильтр по exchange (CRITICAL FIX: was missing!)
        if exchange:
            where_clauses.append("(exchange = ? OR exchange IS NULL)")
            params.append(exchange)
        
        # Фильтр по периоду - используем скользящие окна (rolling windows)
        # вместо жёсткой привязки к полуночи
        current_time = datetime.datetime.now(ZoneInfo("UTC"))
        if period == "today":
            # Последние 24 часа вместо "с полуночи"
            start = current_time - datetime.timedelta(hours=24)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        elif period == "week":
            # Последние 7 дней
            start = current_time - datetime.timedelta(days=7)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        elif period == "month":
            # Последние 30 дней
            start = current_time - datetime.timedelta(days=30)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        
        where_sql = " AND ".join(where_clauses)
        
        # Общая статистика
        # Note: webapp_close is added to EOD category as it's a manual close via webapp
        # Updated: ATR and PARTIAL_TP are now categorized based on PnL:
        #   - ATR/PARTIAL_TP with pnl > 0 → counted as TP (trailing win)
        #   - ATR/PARTIAL_TP with pnl < 0 → counted as SL (trailing loss)
        # NULL exit_reason: use PnL to determine win/loss
        row = conn.execute(f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE 
                    WHEN exit_reason IN ('TP', 'TRAILING', 'PARTIAL_TP') THEN 1
                    WHEN exit_reason = 'ATR' AND pnl > 0 THEN 1
                    WHEN exit_reason = 'UNKNOWN' AND pnl > 0 THEN 1
                    WHEN exit_reason IS NULL AND pnl > 0 THEN 1
                    ELSE 0 
                END) as tp_count,
                SUM(CASE 
                    WHEN exit_reason IN ('SL', 'LIQ', 'ADL') THEN 1
                    WHEN exit_reason = 'ATR' AND pnl <= 0 THEN 1
                    WHEN exit_reason = 'UNKNOWN' AND pnl < 0 THEN 1
                    WHEN exit_reason IS NULL AND pnl <= 0 THEN 1
                    ELSE 0 
                END) as sl_count,
                SUM(CASE WHEN exit_reason IN ('EOD', 'MANUAL', 'webapp_close') THEN 1 ELSE 0 END) as eod_count,
                COALESCE(SUM(pnl), 0) as total_pnl,
                COALESCE(AVG(pnl_pct), 0) as avg_pnl_pct,
                SUM(CASE WHEN side = 'Buy' THEN 1 ELSE 0 END) as long_count,
                SUM(CASE WHEN side = 'Sell' THEN 1 ELSE 0 END) as short_count,
                SUM(CASE WHEN side = 'Buy' AND pnl > 0 THEN 1 ELSE 0 END) as long_wins,
                SUM(CASE WHEN side = 'Sell' AND pnl > 0 THEN 1 ELSE 0 END) as short_wins,
                COALESCE(SUM(CASE WHEN pnl > 0 THEN pnl ELSE 0 END), 0) as gross_profit,
                COALESCE(SUM(CASE WHEN pnl < 0 THEN pnl ELSE 0 END), 0) as gross_loss,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                COALESCE(MAX(pnl), 0) as best_pnl,
                COALESCE(MIN(pnl), 0) as worst_pnl
            FROM trade_logs
            WHERE {where_sql}
        """, params).fetchone()
        
        total = row[0] or 0
        tp_count = row[1] or 0
        sl_count = row[2] or 0
        eod_count = row[3] or 0
        total_pnl = row[4] or 0.0
        avg_pnl_pct = row[5] or 0.0
        long_count = row[6] or 0
        short_count = row[7] or 0
        long_wins = row[8] or 0
        short_wins = row[9] or 0
        gross_profit = row[10] or 0.0
        gross_loss = row[11] or 0.0
        wins = row[12] or 0
        best_pnl = row[13] or 0.0
        worst_pnl = row[14] or 0.0
        
        # Винрейт - рассчитывается по победным сделкам (pnl > 0)
        winrate = (wins / total * 100) if total > 0 else 0.0
        long_winrate = (long_wins / long_count * 100) if long_count > 0 else 0.0
        short_winrate = (short_wins / short_count * 100) if short_count > 0 else 0.0
        
        # Profit Factor
        profit_factor = abs(gross_profit / gross_loss) if gross_loss != 0 else float('inf') if gross_profit > 0 else 0.0
        
        # Count open positions from active_positions table
        open_where = ["user_id = ?"]
        open_params: list = [user_id]
        if strategy:
            open_where.append("strategy = ?")
            open_params.append(strategy)
        if account_type:
            open_where.append("(account_type = ? OR account_type IS NULL)")
            open_params.append(account_type)
        # CRITICAL FIX: Add exchange filter
        if exchange:
            open_where.append("(exchange = ? OR exchange IS NULL)")
            open_params.append(exchange)
        
        open_row = conn.execute(f"""
            SELECT COUNT(*) FROM active_positions
            WHERE {" AND ".join(open_where)}
        """, open_params).fetchone()
        open_count = open_row[0] if open_row else 0
        
        result = {
            "total": total,
            "tp_count": tp_count,
            "sl_count": sl_count,
            "eod_count": eod_count,
            "total_pnl": total_pnl,
            "avg_pnl_pct": avg_pnl_pct,
            "winrate": winrate,
            "long_count": long_count,
            "short_count": short_count,
            "long_winrate": long_winrate,
            "short_winrate": short_winrate,
            "gross_profit": gross_profit,
            "gross_loss": gross_loss,
            "profit_factor": profit_factor,
            "open_count": open_count,
            "best_pnl": best_pnl,
            "worst_pnl": worst_pnl,
        }
        
        # Cache result
        _trade_stats_cache[cache_key] = result
        _trade_stats_cache_ts[cache_key] = now
        
        return result


def get_trade_logs_list(user_id: int, limit: int = 500, strategy: Optional[str] = None, 
                        account_type: Optional[str] = None, exchange: Optional[str] = None,
                        period: str = "all", offset: int = 0,
                        return_count: bool = False) -> list | tuple:
    """
    Get list of trade logs for a user with period filtering and pagination.
    
    Args:
        user_id: Telegram user ID
        limit: Max records to return
        strategy: Strategy filter (None = all)
        account_type: 'demo', 'real', 'testnet', 'mainnet'
        exchange: 'bybit', 'hyperliquid'
        period: 'today', 'week', 'month', 'all'
        offset: Pagination offset
        return_count: If True, returns (list, total_count) tuple
    
    Returns:
        List of trade dicts, or (list, total_count) tuple if return_count=True
    """
    import datetime
    from zoneinfo import ZoneInfo
    
    # Normalize 'both' -> 'demo'/'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange=exchange or 'bybit')
    
    with get_conn() as conn:
        where_clauses = ["user_id = ?"]
        params = [user_id]
        
        if strategy:
            if strategy == "manual_all":
                # Special case: include both manual and unknown strategies
                where_clauses.append("(strategy IS NULL OR strategy IN ('unknown', 'manual'))")
            else:
                where_clauses.append("strategy = ?")
                params.append(strategy)
        
        if account_type:
            where_clauses.append("(account_type = ? OR account_type IS NULL)")
            params.append(account_type)
            
        # Exchange filter
        if exchange and _col_exists(conn, "trade_logs", "exchange"):
            where_clauses.append("(exchange = ? OR exchange IS NULL)")
            params.append(exchange)
        
        # Period filter (rolling windows, same as get_trade_stats)
        current_time = datetime.datetime.now(ZoneInfo("UTC"))
        if period == "today":
            start = current_time - datetime.timedelta(hours=24)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        elif period == "week":
            start = current_time - datetime.timedelta(days=7)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        elif period == "month":
            start = current_time - datetime.timedelta(days=30)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        
        where_sql = " AND ".join(where_clauses)
        
        # Get total count if requested
        total_count = 0
        if return_count:
            count_row = conn.execute(f"""
                SELECT COUNT(*) FROM trade_logs WHERE {where_sql}
            """, params).fetchone()
            total_count = count_row[0] if count_row else 0
        
        # Get paginated results
        query_params = list(params) + [limit, offset]
        cur = conn.execute(f"""
            SELECT id, signal_id, symbol, side, entry_price, exit_price, 
                   exit_reason, pnl, pnl_pct, strategy, account_type, ts, exchange
            FROM trade_logs
            WHERE {where_sql}
            ORDER BY ts DESC
            LIMIT ? OFFSET ?
        """, query_params)
        
        rows = cur.fetchall()
        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "signal_id": row[1],
                "symbol": row[2],
                "side": row[3],
                "entry_price": row[4],
                "exit_price": row[5],
                "exit_reason": row[6],
                "pnl": row[7],
                "pnl_percent": row[8],
                "strategy": row[9] or "unknown",
                "account_type": row[10] or "demo",
                "time": row[11],
                "exchange": row[12] or "bybit",
            })
        
        if return_count:
            return result, total_count
        return result


def get_rolling_24h_pnl(user_id: int, account_type: str | None = None, exchange: str | None = None) -> float:
    """
    Get realized PnL for the last 24 hours (rolling window) from trade_logs.
    
    This is more accurate than Bybit API calendar-day PnL because:
    1. Uses rolling 24h window instead of calendar day (midnight reset)
    2. Works even after midnight when today's calendar day has no trades yet
    3. Includes all exchanges (Bybit + HyperLiquid)
    
    Args:
        user_id: Telegram user ID
        account_type: 'demo', 'real', 'testnet', 'mainnet', or None (all)
        exchange: 'bybit', 'hyperliquid', or None (all)
    
    Returns:
        Total realized PnL in USDT for last 24 hours
    """
    import datetime
    from zoneinfo import ZoneInfo
    
    # Normalize 'both' -> 'demo'/'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange=exchange or 'bybit')
    
    with get_conn() as conn:
        where_clauses = ["user_id = ?", "ts >= ?"]
        now = datetime.datetime.now(ZoneInfo("UTC"))
        start = now - datetime.timedelta(hours=24)
        params = [user_id, start.strftime("%Y-%m-%d %H:%M:%S")]
        
        if account_type:
            where_clauses.append("(account_type = ? OR account_type IS NULL)")
            params.append(account_type)
        
        if exchange and _col_exists(conn, "trade_logs", "exchange"):
            where_clauses.append("exchange = ?")
            params.append(exchange)
        
        where_sql = " AND ".join(where_clauses)
        
        row = conn.execute(f"""
            SELECT COALESCE(SUM(pnl), 0) as total_pnl, COUNT(*) as trade_count
            FROM trade_logs
            WHERE {where_sql}
        """, params).fetchone()
        
        total_pnl = float(row[0]) if row and row[0] else 0.0
        trade_count = row[1] if row else 0
        
        _logger.debug(f"[{user_id}] Rolling 24h PnL from DB: {total_pnl:+.2f} USDT ({trade_count} trades)")
        return total_pnl


def get_trade_stats_unknown(user_id: int, period: str = "all", account_type: str | None = None, exchange: str | None = None) -> dict:
    """Get stats for trades with NULL/unknown/manual strategy."""
    import datetime
    from zoneinfo import ZoneInfo
    
    # Normalize 'both' -> 'demo'/'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange=exchange or 'bybit')
    
    with get_conn() as conn:
        # Include NULL, 'unknown', and 'manual' strategies
        where_clauses = ["user_id = ?", "(strategy IS NULL OR strategy IN ('unknown', 'manual'))"]
        params: list = [user_id]
        
        if account_type:
            where_clauses.append("(account_type = ? OR account_type IS NULL)")
            params.append(account_type)
        
        # CRITICAL FIX: Add exchange filter (was missing!)
        if exchange:
            where_clauses.append("(exchange = ? OR exchange IS NULL)")
            params.append(exchange)
        
        now = datetime.datetime.now(ZoneInfo("UTC"))
        if period == "today":
            # Use rolling 24h for consistency with get_trade_stats
            start = now - datetime.timedelta(hours=24)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        elif period == "week":
            start = now - datetime.timedelta(days=7)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        elif period == "month":
            start = now - datetime.timedelta(days=30)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        
        where_sql = " AND ".join(where_clauses)
        
        row = conn.execute(f"""
            SELECT 
                COUNT(*) as total,
                SUM(pnl) as total_pnl,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins
            FROM trade_logs
            WHERE {where_sql}
        """, params).fetchone()
        
        total = row[0] or 0
        total_pnl = row[1] or 0.0
        wins = row[2] or 0
        winrate = (wins / total * 100) if total > 0 else 0.0
        
        return {
            "total": total,
            "total_pnl": total_pnl,
            "winrate": winrate,
        }


def get_stats_by_strategy(user_id: int, period: str = "all", account_type: str | None = None, exchange: str | None = None) -> dict[str, dict]:
    """Возвращает статистику по каждой стратегии отдельно."""
    strategies = ["oi", "rsi_bb", "scryptomera", "scalper", "elcaro", "fibonacci"]
    result = {}
    for strat in strategies:
        stats = get_trade_stats(user_id, strategy=strat, period=period, account_type=account_type, exchange=exchange)
        if stats["total"] > 0:
            result[strat] = stats
    
    # Add unknown/manual trades
    unknown_stats = get_trade_stats_unknown(user_id, period=period, account_type=account_type, exchange=exchange)
    if unknown_stats["total"] > 0:
        result["manual"] = unknown_stats
    
    # Общая статистика
    result["all"] = get_trade_stats(user_id, strategy=None, period=period, account_type=account_type, exchange=exchange)
    return result


# =====================================================
# LICENSE REQUEST SYSTEM (ADMIN APPROVAL)
# =====================================================

def create_license_request(
    user_id: int,
    license_type: str,
    period_months: int = 1,
    payment_method: str = "pending",
    amount: float = 0.0,
    currency: str = "ELC",
    notes: str = None
) -> dict:
    """
    Create a license request that needs admin approval.
    
    Returns:
        {"success": True, "request_id": int} or {"error": str}
    """
    import time
    now = int(time.time())
    
    ensure_user(user_id)
    
    with get_conn() as conn:
        # Check for existing pending request
        existing = conn.execute(
            "SELECT id FROM license_requests WHERE user_id = ? AND status = 'pending'",
            (user_id,)
        ).fetchone()
        
        if existing:
            return {"error": "pending_request_exists", "request_id": existing[0]}
        
        cur = conn.execute("""
            INSERT INTO license_requests 
            (user_id, license_type, period_months, payment_method, amount, currency, status, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)
        """, (user_id, license_type, period_months, payment_method, amount, currency, notes, now))
        
        request_id = cur.lastrowid
        conn.commit()
        
        return {"success": True, "request_id": request_id}


def get_pending_license_requests(limit: int = 50) -> list[dict]:
    """Get all pending license requests for admin review."""
    import time
    now = int(time.time())
    
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT lr.id, lr.user_id, lr.license_type, lr.period_months, lr.payment_method,
                   lr.amount, lr.currency, lr.status, lr.notes, lr.created_at,
                   u.username, u.first_name, u.current_license, u.license_expires
            FROM license_requests lr
            LEFT JOIN users u ON lr.user_id = u.user_id
            WHERE lr.status = 'pending'
            ORDER BY lr.created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        
        result = []
        for r in rows:
            days_ago = (now - r[9]) // 86400 if r[9] else 0
            result.append({
                "id": r[0],
                "user_id": r[1],
                "license_type": r[2],
                "period_months": r[3],
                "payment_method": r[4],
                "amount": r[5],
                "currency": r[6],
                "status": r[7],
                "notes": r[8],
                "created_at": r[9],
                "days_ago": days_ago,
                "username": r[10],
                "first_name": r[11],
                "current_license": r[12] or "none",
                "license_expires": r[13],
            })
        return result


def get_license_request(request_id: int) -> dict | None:
    """Get a specific license request."""
    with get_conn() as conn:
        row = conn.execute("""
            SELECT lr.id, lr.user_id, lr.license_type, lr.period_months, lr.payment_method,
                   lr.amount, lr.currency, lr.status, lr.notes, lr.created_at,
                   lr.approved_at, lr.approved_by, lr.rejection_reason,
                   u.username, u.first_name
            FROM license_requests lr
            LEFT JOIN users u ON lr.user_id = u.user_id
            WHERE lr.id = ?
        """, (request_id,)).fetchone()
        
        if not row:
            return None
        
        return {
            "id": row[0],
            "user_id": row[1],
            "license_type": row[2],
            "period_months": row[3],
            "payment_method": row[4],
            "amount": row[5],
            "currency": row[6],
            "status": row[7],
            "notes": row[8],
            "created_at": row[9],
            "approved_at": row[10],
            "approved_by": row[11],
            "rejection_reason": row[12],
            "username": row[13],
            "first_name": row[14],
        }


def approve_license_request(request_id: int, admin_id: int, notes: str = None) -> dict:
    """
    Approve a license request and grant the license.
    
    Returns:
        {"success": True, "license_info": dict} or {"error": str}
    """
    import time
    now = int(time.time())
    
    request = get_license_request(request_id)
    if not request:
        return {"error": "request_not_found"}
    
    if request["status"] != "pending":
        return {"error": f"request_already_{request['status']}"}
    
    # Grant the license
    license_result = set_user_license(
        user_id=request["user_id"],
        license_type=request["license_type"],
        period_months=request["period_months"],
        admin_id=admin_id,
        payment_type=request["payment_method"],
        amount=request["amount"],
        currency=request["currency"],
        notes=f"Approved from request #{request_id}. {notes or ''}"
    )
    
    if "error" in license_result:
        return license_result
    
    # Update request status
    with get_conn() as conn:
        conn.execute("""
            UPDATE license_requests 
            SET status = 'approved', approved_at = ?, approved_by = ?, notes = COALESCE(notes || ' | ', '') || ?
            WHERE id = ?
        """, (now, admin_id, f"Approved: {notes or ''}", request_id))
        conn.commit()
    
    return {"success": True, "license_info": license_result, "request": request}


def reject_license_request(request_id: int, admin_id: int, reason: str = None) -> dict:
    """Reject a license request."""
    import time
    now = int(time.time())
    
    request = get_license_request(request_id)
    if not request:
        return {"error": "request_not_found"}
    
    if request["status"] != "pending":
        return {"error": f"request_already_{request['status']}"}
    
    with get_conn() as conn:
        conn.execute("""
            UPDATE license_requests 
            SET status = 'rejected', approved_at = ?, approved_by = ?, rejection_reason = ?
            WHERE id = ?
        """, (now, admin_id, reason or "No reason provided", request_id))
        conn.commit()
    
    return {"success": True, "request": request}


def get_user_license_requests(user_id: int, limit: int = 10, status: str = None) -> list[dict]:
    """Get user's license request history."""
    with get_conn() as conn:
        if status:
            rows = conn.execute("""
                SELECT id, license_type, period_months, payment_method, amount, currency, 
                       status, notes, created_at, approved_at, rejection_reason
                FROM license_requests
                WHERE user_id = ? AND status = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, status, limit)).fetchall()
        else:
            rows = conn.execute("""
                SELECT id, license_type, period_months, payment_method, amount, currency, 
                       status, notes, created_at, approved_at, rejection_reason
                FROM license_requests
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit)).fetchall()
        
        return [
            {
                "id": r[0],
                "license_type": r[1],
                "period_months": r[2],
                "payment_method": r[3],
                "amount": r[4],
                "currency": r[5],
                "status": r[6],
                "notes": r[7],
                "created_at": r[8],
                "approved_at": r[9],
                "rejection_reason": r[10],
            }
            for r in rows
        ]


def get_license_request_stats() -> dict:
    """Get license request statistics for admin dashboard."""
    with get_conn() as conn:
        row = conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected,
                SUM(CASE WHEN status = 'approved' THEN amount ELSE 0 END) as total_approved_amount
            FROM license_requests
        """).fetchone()
        
        return {
            "total": row[0] or 0,
            "pending": row[1] or 0,
            "approved": row[2] or 0,
            "rejected": row[3] or 0,
            "total_approved_amount": row[4] or 0.0,
        }


# =====================================================
# LICENSING SYSTEM FUNCTIONS
# =====================================================

# License types and their capabilities
# Basic: Bybit only, OI + RSI_BB, demo + real
# Trial: Demo only, all strategies, 14 days
# Premium: Everything (all strategies, all exchanges, demo + real)
LICENSE_TYPES = {
    "premium": {
        "name": "Premium",
        "demo_access": True,
        "real_access": True,
        "all_strategies": True,
        "all_exchanges": True,  # Bybit + HyperLiquid
        "strategies": ["oi", "rsi_bb", "scryptomera", "scalper", "elcaro", "fibonacci", "spot", "manual"],
    },
    "enterprise": {
        "name": "Enterprise",
        "demo_access": True,
        "real_access": True,
        "all_strategies": True,
        "all_exchanges": True,
        "strategies": ["oi", "rsi_bb", "scryptomera", "scalper", "elcaro", "fibonacci", "spot", "manual"],
        "priority_support": True,
        "api_access": True,
        "white_label": True,
        "max_positions": 100,
    },
    "basic": {
        "name": "Basic", 
        "demo_access": True,
        "real_access": True,
        "all_strategies": False,
        "all_exchanges": False,  # Bybit ONLY
        "bybit_only": True,
        "strategies": ["oi", "rsi_bb"],  # Only OI and RSI+BB
    },
    "trial": {
        "name": "Trial",
        "demo_access": True,
        "real_access": False,  # Demo only, 14 days
        "all_strategies": True,
        "all_exchanges": True,  # Can see all in demo
        "strategies": ["oi", "rsi_bb", "scryptomera", "scalper", "elcaro", "fibonacci", "spot", "manual"],
    },
    "none": {
        "name": "No License",
        "demo_access": False,
        "real_access": False,
        "all_strategies": False,
        "strategies": [],
    }
}

# Period days mapping
LICENSE_PERIODS = {
    1: 30,    # 1 month
    3: 90,    # 3 months  
    6: 180,   # 6 months
    12: 365,  # 12 months
}


def get_user_license(user_id: int) -> dict:
    """
    Get user's current active license info.
    
    Returns dict with:
        - license_type: 'premium', 'basic', 'trial', 'none'
        - expires: Unix timestamp or None
        - days_left: int or None
        - is_active: bool
        - capabilities: dict from LICENSE_TYPES
    """
    import time
    
    with get_conn() as conn:
        # First check quick access columns in users table
        row = conn.execute(
            "SELECT current_license, license_expires FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        
        if not row:
            return {
                "license_type": "none",
                "expires": None,
                "days_left": None,
                "is_active": False,
                "capabilities": LICENSE_TYPES["none"],
            }
        
        current_license = row[0] or "none"
        license_expires = row[1]
        
        now = int(time.time())
        
        # Check if license expired
        if license_expires and license_expires < now:
            # License expired, update to none (sync BOTH columns)
            conn.execute(
                "UPDATE users SET current_license = 'none', license_type = 'none', license_expires = NULL WHERE user_id = ?",
                (user_id,)
            )
            # Deactivate old license records
            conn.execute(
                "UPDATE user_licenses SET is_active = 0, updated_at = ? WHERE user_id = ? AND is_active = 1",
                (now, user_id)
            )
            conn.commit()
            invalidate_user_cache(user_id)
            return {
                "license_type": "none",
                "expires": None,
                "days_left": None,
                "is_active": False,
                "capabilities": LICENSE_TYPES["none"],
            }
        
        # Calculate days left
        days_left = None
        if license_expires:
            days_left = max(0, (license_expires - now) // 86400)
        
        capabilities = LICENSE_TYPES.get(current_license, LICENSE_TYPES["none"])
        
        return {
            "license_type": current_license,
            "expires": license_expires,
            "days_left": days_left,
            "is_active": current_license != "none",
            "capabilities": capabilities,
        }


def set_user_license(
    user_id: int,
    license_type: str,
    period_months: int = 1,
    admin_id: int | None = None,
    payment_type: str = "admin_grant",
    amount: float = 0.0,
    currency: str = "FREE",
    telegram_charge_id: str | None = None,
    notes: str | None = None,
) -> dict:
    """
    Set or extend user's license.
    
    Returns dict with license info or error.
    """
    import time
    
    if license_type not in LICENSE_TYPES:
        return {"error": f"Invalid license type: {license_type}"}
    
    period_days = LICENSE_PERIODS.get(period_months, period_months * 30)
    now = int(time.time())
    
    ensure_user(user_id)
    
    with get_conn() as conn:
        # Check current license
        current = get_user_license(user_id)
        
        # Calculate new end date
        if current["is_active"] and current["expires"]:
            # Extend from current expiry if same or higher tier
            tier_order = {"premium": 3, "basic": 2, "trial": 1, "none": 0}
            if tier_order.get(license_type, 0) >= tier_order.get(current["license_type"], 0):
                new_end = current["expires"] + (period_days * 86400)
            else:
                # Downgrade starts from now
                new_end = now + (period_days * 86400)
        else:
            new_end = now + (period_days * 86400)
        
        # Deactivate old license
        conn.execute(
            "UPDATE user_licenses SET is_active = 0, updated_at = ? WHERE user_id = ? AND is_active = 1",
            (now, user_id)
        )
        
        # Create new license record
        cur = conn.execute("""
            INSERT INTO user_licenses (user_id, license_type, start_date, end_date, is_active, created_at, created_by, notes)
            VALUES (?, ?, ?, ?, 1, ?, ?, ?)
        """, (user_id, license_type, now, new_end, now, admin_id, notes))
        
        license_id = cur.lastrowid
        
        # Record payment
        conn.execute("""
            INSERT INTO payment_history (user_id, license_id, payment_type, amount, currency, license_type, period_days, telegram_charge_id, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'completed', NOW())
        """, (user_id, license_id, payment_type, amount, currency, license_type, period_days, telegram_charge_id))
        
        # Update quick access columns (sync BOTH current_license and license_type for webapp compat)
        conn.execute(
            "UPDATE users SET current_license = ?, license_type = ?, license_expires = ? WHERE user_id = ?",
            (license_type, license_type, new_end, user_id)
        )
        
        conn.commit()
        invalidate_user_cache(user_id)
        
        # Format end date for display
        from datetime import datetime
        end_date_str = datetime.fromtimestamp(new_end).strftime("%Y-%m-%d")
        
        return {
            "success": True,
            "license_id": license_id,
            "license_type": license_type,
            "expires": new_end,
            "days": period_days,
            "end_date": end_date_str,
        }


def extend_license(user_id: int, days: int, admin_id: int | None = None, notes: str | None = None) -> dict:
    """
    Extend user's current license by specified days.
    Admin-only function.
    """
    import time
    
    current = get_user_license(user_id)
    if not current["is_active"]:
        return {"error": "User has no active license to extend"}
    
    now = int(time.time())
    new_end = current["expires"] + (days * 86400)
    
    with get_conn() as conn:
        # Update active license
        conn.execute("""
            UPDATE user_licenses 
            SET end_date = ?, updated_at = ?, notes = COALESCE(notes || ' | ', '') || ?
            WHERE user_id = ? AND is_active = 1
        """, (new_end, now, f"Extended +{days}d by admin {admin_id}", user_id))
        
        # Record as admin grant
        conn.execute("""
            INSERT INTO payment_history (user_id, payment_type, amount, currency, license_type, period_days, status, created_at, metadata)
            VALUES (?, 'admin_grant', 0, 'FREE', ?, ?, 'completed', NOW(), ?)
        """, (user_id, current["license_type"], days, json.dumps({"action": "extend", "admin_id": admin_id, "notes": notes})))
        
        # Update quick access
        conn.execute(
            "UPDATE users SET license_expires = ? WHERE user_id = ?",
            (new_end, user_id)
        )
        
        conn.commit()
        invalidate_user_cache(user_id)
        
    return {
        "success": True,
        "new_expires": new_end,
        "days_added": days,
        "new_days_left": (new_end - now) // 86400,
    }


def revoke_license(user_id: int, admin_id: int | None = None, reason: str | None = None) -> dict:
    """
    Revoke user's license (admin function).
    """
    import time
    now = int(time.time())
    
    with get_conn() as conn:
        # Deactivate license
        conn.execute("""
            UPDATE user_licenses 
            SET is_active = 0, updated_at = ?, notes = COALESCE(notes || ' | ', '') || ?
            WHERE user_id = ? AND is_active = 1
        """, (now, f"Revoked by admin {admin_id}: {reason or 'No reason'}", user_id))
        
        # Record revocation
        conn.execute("""
            INSERT INTO payment_history (user_id, payment_type, amount, currency, license_type, period_days, status, created_at, metadata)
            VALUES (?, 'admin_grant', 0, 'FREE', 'none', 0, 'completed', NOW(), ?)
        """, (user_id, json.dumps({"action": "revoke", "admin_id": admin_id, "reason": reason})))
        
        # Clear quick access (sync BOTH columns)
        conn.execute(
            "UPDATE users SET current_license = 'none', license_type = 'none', license_expires = NULL WHERE user_id = ?",
            (user_id,)
        )
        
        conn.commit()
        invalidate_user_cache(user_id)
    
    return {"success": True, "message": "License revoked"}


def check_license_access(user_id: int, feature: str, account_type: str = "demo", exchange: str = "bybit") -> dict:
    """
    Check if user has access to a specific feature.
    
    Args:
        user_id: User ID
        feature: Feature name ('trading', 'strategy_oi', 'strategy_rsi_bb', 'exchange_hyperliquid', etc.)
        account_type: 'demo' or 'real'
        exchange: 'bybit' or 'hyperliquid'
    
    Returns:
        {"allowed": bool, "reason": str}
    
    License rules:
        - Trial: Demo only, all strategies, all exchanges in demo
        - Basic: Demo + Real, OI and RSI_BB only, Bybit only
        - Premium: Everything
    """
    license_info = get_user_license(user_id)
    
    if not license_info["is_active"]:
        return {"allowed": False, "reason": "no_license"}
    
    caps = license_info["capabilities"]
    license_type = license_info["license_type"]
    
    # Check demo/real access
    if account_type == "real" and not caps["real_access"]:
        return {"allowed": False, "reason": "trial_demo_only"}
    
    if account_type == "demo" and not caps["demo_access"]:
        return {"allowed": False, "reason": "no_demo_access"}
    
    # Check exchange access - Basic is Bybit only
    if license_type == "basic" and exchange == "hyperliquid":
        return {"allowed": False, "reason": "basic_bybit_only"}
    
    # Check strategy access
    if feature.startswith("strategy_"):
        strategy = feature.replace("strategy_", "")
        
        # Basic users are limited to OI and RSI_BB on both demo and real
        if license_type == "basic":
            if strategy not in caps["strategies"]:
                return {"allowed": False, "reason": "basic_strategy_limit", "allowed_strategies": caps["strategies"]}
        
        # Premium and Trial have all strategies
        if strategy not in caps["strategies"]:
            return {"allowed": False, "reason": "strategy_not_available"}
    
    return {"allowed": True, "reason": "ok"}


def can_trade_strategy(user_id: int, strategy: str, account_type: str = "demo") -> bool:
    """
    Quick check if user can trade a specific strategy.
    Convenience wrapper around check_license_access.
    """
    result = check_license_access(user_id, f"strategy_{strategy}", account_type)
    return result["allowed"]


def get_allowed_strategies(user_id: int, account_type: str = "demo") -> list[str]:
    """
    Get list of strategies user can trade on given account type.
    
    Basic: Only OI and RSI_BB on both demo and real (Bybit only)
    Trial: All strategies but demo only
    Premium: All strategies, all exchanges
    """
    license_info = get_user_license(user_id)
    
    if not license_info["is_active"]:
        return []
    
    caps = license_info["capabilities"]
    license_type = license_info["license_type"]
    
    # Check if user can trade on this account type
    if account_type == "real" and not caps["real_access"]:
        return []
    if account_type == "demo" and not caps["demo_access"]:
        return []
    
    # Basic: limited strategies (OI, RSI_BB only) on both demo and real
    if license_type == "basic":
        return ["oi", "rsi_bb"]
    
    # Premium, Enterprise, Trial - all strategies
    return ["oi", "rsi_bb", "scryptomera", "scalper", "elcaro", "fibonacci", "spot", "manual"]


# =====================================================
# PROMO CODE FUNCTIONS
# =====================================================

def create_promo_code(
    code: str,
    license_type: str,
    period_days: int,
    max_uses: int = 1,
    valid_days: int | None = None,
    admin_id: int | None = None,
    notes: str | None = None,
) -> dict:
    """
    Create a new promo code.
    """
    import time
    
    if license_type not in ["premium", "basic", "trial"]:
        return {"error": "Invalid license type"}
    
    now = int(time.time())
    valid_until = now + (valid_days * 86400) if valid_days else None
    
    with get_conn() as conn:
        try:
            conn.execute("""
                INSERT INTO promo_codes (code, license_type, period_days, max_uses, valid_until, created_at, created_by, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (code.upper(), license_type, period_days, max_uses, valid_until, now, admin_id, notes))
            conn.commit()
            return {"success": True, "code": code.upper()}
        except Exception as e:
            # Handle unique constraint violation (promo code already exists)
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                return {"error": "Promo code already exists"}
            raise


def use_promo_code(user_id: int, code: str) -> dict:
    """
    Apply a promo code for the user.
    """
    import time
    now = int(time.time())
    
    with get_conn() as conn:
        # Find promo code
        promo = conn.execute("""
            SELECT id, license_type, period_days, max_uses, current_uses, is_active, valid_until
            FROM promo_codes WHERE code = ?
        """, (code.upper(),)).fetchone()
        
        if not promo:
            return {"error": "invalid_code"}
        
        promo_id, license_type, period_days, max_uses, current_uses, is_active, valid_until = promo
        
        if not is_active:
            return {"error": "code_inactive"}
        
        if valid_until and valid_until < now:
            return {"error": "code_expired"}
        
        if max_uses and current_uses >= max_uses:
            return {"error": "code_used_up"}
        
        # Check if user already used this code
        used = conn.execute(
            "SELECT 1 FROM promo_usage WHERE promo_id = ? AND user_id = ?",
            (promo_id, user_id)
        ).fetchone()
        
        if used:
            return {"error": "already_used"}
        
        # Apply promo
        result = set_user_license(
            user_id=user_id,
            license_type=license_type,
            period_months=1,  # Will be overridden by period_days
            payment_type="promo",
            amount=0,
            currency="FREE",
            notes=f"Promo code: {code.upper()}"
        )
        
        if "error" in result:
            return result
        
        # Update promo usage
        conn.execute(
            "INSERT INTO promo_usage (promo_id, user_id, used_at) VALUES (?, ?, ?)",
            (promo_id, user_id, now)
        )
        conn.execute(
            "UPDATE promo_codes SET current_uses = current_uses + 1 WHERE id = ?",
            (promo_id,)
        )
        conn.commit()
        
        return {
            "success": True,
            "license_type": license_type,
            "days": period_days,
            "expires": result["expires"],
        }


def get_promo_codes(active_only: bool = True) -> list[dict]:
    """Get all promo codes (admin function)."""
    with get_conn() as conn:
        where = "WHERE is_active = 1" if active_only else ""
        rows = conn.execute(f"""
            SELECT id, code, license_type, period_days, max_uses, current_uses, is_active, valid_until, created_at, notes
            FROM promo_codes {where}
            ORDER BY created_at DESC
        """).fetchall()
        
        return [
            {
                "id": r[0],
                "code": r[1],
                "license_type": r[2],
                "period_days": r[3],
                "max_uses": r[4],
                "current_uses": r[5],
                "is_active": bool(r[6]),
                "valid_until": r[7],
                "created_at": r[8],
                "notes": r[9],
            }
            for r in rows
        ]


def deactivate_promo_code(code: str) -> dict:
    """Deactivate a promo code."""
    with get_conn() as conn:
        conn.execute(
            "UPDATE promo_codes SET is_active = 0 WHERE code = ?",
            (code.upper(),)
        )
        conn.commit()
    return {"success": True}


# =====================================================
# PAYMENT HISTORY FUNCTIONS
# =====================================================

def get_user_payments(user_id: int, limit: int = 50) -> list[dict]:
    """Get user's payment history."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT id, payment_type, amount, currency, license_type, period_days, status, created_at, telegram_charge_id
            FROM payment_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit)).fetchall()
        
        return [
            {
                "id": r[0],
                "payment_type": r[1],
                "amount": r[2],
                "currency": r[3],
                "license_type": r[4],
                "period_days": r[5],
                "status": r[6],
                "created_at": r[7],
                "telegram_charge_id": r[8],
            }
            for r in rows
        ]


def get_license_history(user_id: int) -> list[dict]:
    """Get user's license history."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT id, license_type, start_date, end_date, is_active, created_at, notes
            FROM user_licenses
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,)).fetchall()
        
        return [
            {
                "id": r[0],
                "license_type": r[1],
                "start_date": r[2],
                "end_date": r[3],
                "is_active": bool(r[4]),
                "created_at": r[5],
                "notes": r[6],
            }
            for r in rows
        ]


def get_all_active_licenses(license_type: str | None = None) -> list[dict]:
    """Get all users with active licenses (admin function)."""
    import time
    now = int(time.time())
    
    with get_conn() as conn:
        where = "WHERE current_license != 'none' AND license_expires > ?"
        params: list = [now]
        
        if license_type:
            where += " AND current_license = ?"
            params.append(license_type)
        
        rows = conn.execute(f"""
            SELECT user_id, current_license, license_expires
            FROM users
            {where}
            ORDER BY license_expires ASC
        """, params).fetchall()
        
        return [
            {
                "user_id": r[0],
                "license_type": r[1],
                "expires": r[2],
                "days_left": (r[2] - now) // 86400,
            }
            for r in rows
        ]


def get_expiring_licenses(days: int = 3) -> list[dict]:
    """Get licenses expiring within specified days."""
    import time
    now = int(time.time())
    threshold = now + (days * 86400)
    
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT user_id, current_license, license_expires
            FROM users
            WHERE current_license != 'none' 
              AND license_expires > ?
              AND license_expires <= ?
            ORDER BY license_expires ASC
        """, (now, threshold)).fetchall()
        
        return [
            {
                "user_id": r[0],
                "license_type": r[1],
                "expires": r[2],
                "days_left": (r[2] - now) // 86400,
            }
            for r in rows
        ]


# =====================================================
# ADMIN USER CARD FUNCTIONS
# =====================================================

def get_user_full_info(user_id: int) -> dict | None:
    """
    Get comprehensive user information for admin panel.
    Returns all user data including config, licenses, payments, positions, etc.
    """
    import time
    now = int(time.time())
    
    with get_conn() as conn:
        # Basic user info
        row = conn.execute("""
            SELECT user_id, is_allowed, is_banned, terms_accepted,
                   trading_mode, percent, coins, lang,
                   trade_oi, trade_rsi_bb, trade_scryptomera, trade_scalper, trade_elcaro,
                   current_license, license_expires,
                   first_seen_ts, last_seen_ts,
                   demo_api_key, real_api_key
            FROM users WHERE user_id = ?
        """, (user_id,)).fetchone()
        
        if not row:
            return None
        
        # Count active positions
        pos_row = conn.execute(
            "SELECT COUNT(*) FROM active_positions WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        positions_count = pos_row[0] if pos_row else 0
        
        # Count trade logs
        trades_row = conn.execute(
            "SELECT COUNT(*) FROM trade_logs WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        trades_count = trades_row[0] if trades_row else 0
        
        # Calculate total PnL
        pnl_row = conn.execute(
            "SELECT SUM(pnl), COUNT(CASE WHEN pnl > 0 THEN 1 END) FROM trade_logs WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        total_pnl = pnl_row[0] or 0.0
        wins = pnl_row[1] or 0
        
        # Payment history count
        pay_row = conn.execute(
            "SELECT COUNT(*) FROM payment_history WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        payments_count = pay_row[0] if pay_row else 0
        
        # Total payments amount
        paid_row = conn.execute(
            "SELECT SUM(amount) FROM payment_history WHERE user_id = ? AND status = 'completed' AND currency = 'XTR'",
            (user_id,)
        ).fetchone()
        total_paid = (paid_row[0] or 0) if paid_row else 0
        
        # License days left
        license_expires = row[14]
        days_left = None
        if license_expires and license_expires > now:
            days_left = (license_expires - now) // 86400
        
        return {
            "user_id": row[0],
            "is_allowed": bool(row[1]),
            "is_banned": bool(row[2]),
            "terms_accepted": bool(row[3]),
            "trading_mode": row[4] or "demo",
            "percent": row[5] or 1.0,
            "coins": row[6] or "ALL",
            "lang": row[7] or "en",
            "trade_oi": bool(row[8]),
            "trade_rsi_bb": bool(row[9]),
            "trade_scryptomera": bool(row[10]),
            "trade_scalper": bool(row[11]),
            "trade_elcaro": bool(row[12]),
            "current_license": row[13] or "none",
            "license_expires": license_expires,
            "license_days_left": days_left,
            "first_seen_ts": row[15],
            "last_seen_ts": row[16],
            "has_demo_api": bool(row[17]),
            "has_real_api": bool(row[18]),
            "positions_count": positions_count,
            "trades_count": trades_count,
            "total_pnl": total_pnl,
            "winrate": (wins / trades_count * 100) if trades_count > 0 else 0,
            "payments_count": payments_count,
            "total_paid_stars": total_paid,
        }


def get_users_paginated(page: int = 0, per_page: int = 10, filter_type: str = "all") -> tuple[list[dict], int]:
    """
    Get paginated list of users for admin panel.
    
    filter_type: 'all', 'active', 'banned', 'premium', 'basic', 'trial', 'no_license'
    
    Returns: (list of users, total count)
    """
    import time
    now = int(time.time())
    
    with get_conn() as conn:
        # Build WHERE clause based on filter
        where = "1=1"
        params = []
        if filter_type == "active":
            where = "is_allowed = 1 AND is_banned = 0"
        elif filter_type == "banned":
            where = "is_banned = 1"
        elif filter_type == "premium":
            where = "current_license = %s AND license_expires > %s"
            params = ['premium', now]
        elif filter_type == "basic":
            where = "current_license = %s AND license_expires > %s"
            params = ['basic', now]
        elif filter_type == "trial":
            where = "current_license = %s AND license_expires > %s"
            params = ['trial', now]
        elif filter_type == "no_license":
            where = "(current_license = 'none' OR current_license IS NULL OR license_expires <= %s)"
            params = [now]
        
        # Get total count
        total_row = conn.execute(f"SELECT COUNT(*) FROM users WHERE {where}", params).fetchone()
        total = total_row[0] if total_row else 0
        
        # Get page data
        offset = page * per_page
        rows = conn.execute(f"""
            SELECT user_id, is_allowed, is_banned, current_license, license_expires, last_seen_ts
            FROM users
            WHERE {where}
            ORDER BY last_seen_ts DESC NULLS LAST
            LIMIT ? OFFSET ?
        """, params + [per_page, offset]).fetchall()
        
        users = []
        for r in rows:
            license_expires = r[4]
            days_left = None
            if license_expires and license_expires > now:
                days_left = (license_expires - now) // 86400
            
            users.append({
                "user_id": r[0],
                "is_allowed": bool(r[1]),
                "is_banned": bool(r[2]),
                "license_type": r[3] or "none",
                "license_days_left": days_left,
                "last_seen_ts": r[5],
            })
        
        return users, total


def search_user_by_id(user_id: int) -> dict | None:
    """Search for user by ID."""
    return get_user_full_info(user_id)


# =====================================================
# ADMIN STATISTICS & REPORTS
# =====================================================

def get_global_trade_stats(strategy: str | None = None, period: str = "all", account_type: str | None = None) -> dict:
    """
    Get aggregate trade stats across ALL users for admin panel.
    """
    import datetime
    from zoneinfo import ZoneInfo
    
    with get_conn() as conn:
        where_clauses = ["1=1"]
        params: list = []
        
        if strategy:
            where_clauses.append("strategy = ?")
            params.append(strategy)
        
        if account_type:
            where_clauses.append("(account_type = ? OR account_type IS NULL)")
            params.append(account_type)
        
        now = datetime.datetime.now(ZoneInfo("UTC"))
        if period == "today":
            # Use rolling 24h for consistency
            start = now - datetime.timedelta(hours=24)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        elif period == "week":
            start = now - datetime.timedelta(days=7)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        elif period == "month":
            start = now - datetime.timedelta(days=30)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        
        where_sql = " AND ".join(where_clauses)
        
        row = conn.execute(f"""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT user_id) as unique_users,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                SUM(pnl) as total_pnl,
                AVG(pnl_pct) as avg_pnl_pct,
                SUM(CASE WHEN side = 'Buy' THEN 1 ELSE 0 END) as long_count,
                SUM(CASE WHEN side = 'Sell' THEN 1 ELSE 0 END) as short_count,
                SUM(CASE WHEN pnl > 0 THEN pnl ELSE 0 END) as gross_profit,
                SUM(CASE WHEN pnl < 0 THEN pnl ELSE 0 END) as gross_loss
            FROM trade_logs
            WHERE {where_sql}
        """, params).fetchone()
        
        total = row[0] or 0
        unique_users = row[1] or 0
        wins = row[2] or 0
        total_pnl = row[3] or 0.0
        avg_pnl_pct = row[4] or 0.0
        long_count = row[5] or 0
        short_count = row[6] or 0
        gross_profit = row[7] or 0.0
        gross_loss = row[8] or 0.0
        
        winrate = (wins / total * 100) if total > 0 else 0.0
        profit_factor = abs(gross_profit / gross_loss) if gross_loss != 0 else float('inf') if gross_profit > 0 else 0.0
        
        # Count active positions
        open_where = ["1=1"]
        open_params: list = []
        if strategy:
            open_where.append("strategy = ?")
            open_params.append(strategy)
        if account_type:
            open_where.append("(account_type = ? OR account_type IS NULL)")
            open_params.append(account_type)
        
        open_row = conn.execute(f"""
            SELECT COUNT(*), COUNT(DISTINCT user_id) FROM active_positions
            WHERE {" AND ".join(open_where)}
        """, open_params).fetchone()
        open_count = open_row[0] if open_row else 0
        open_users = open_row[1] if open_row else 0
        
        return {
            "total_trades": total,
            "unique_users": unique_users,
            "wins": wins,
            "total_pnl": total_pnl,
            "avg_pnl_pct": avg_pnl_pct,
            "winrate": winrate,
            "long_count": long_count,
            "short_count": short_count,
            "gross_profit": gross_profit,
            "gross_loss": gross_loss,
            "profit_factor": profit_factor,
            "open_positions": open_count,
            "users_with_open": open_users,
        }


def get_global_stats_by_strategy(period: str = "all", account_type: str | None = None) -> dict[str, dict]:
    """Get global stats broken down by strategy."""
    strategies = ["oi", "rsi_bb", "scryptomera", "scalper", "elcaro", "fibonacci"]
    result = {}
    for strat in strategies:
        stats = get_global_trade_stats(strategy=strat, period=period, account_type=account_type)
        if stats["total_trades"] > 0:
            result[strat] = stats
    result["all"] = get_global_trade_stats(strategy=None, period=period, account_type=account_type)
    return result


def get_all_payments(status: str | None = None, limit: int = 50, offset: int = 0) -> tuple[list[dict], int]:
    """Get all payments for admin panel with pagination."""
    with get_conn() as conn:
        where = "1=1"
        params: list = []
        
        if status:
            where += " AND status = ?"
            params.append(status)
        
        total_row = conn.execute(f"SELECT COUNT(*) FROM payment_history WHERE {where}", params).fetchone()
        total = total_row[0] if total_row else 0
        
        rows = conn.execute(f"""
            SELECT id, user_id, payment_type, amount, currency, license_type, period_days, status, created_at, telegram_charge_id
            FROM payment_history
            WHERE {where}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, params + [limit, offset]).fetchall()
        
        return [
            {
                "id": r[0],
                "user_id": r[1],
                "payment_type": r[2],
                "amount": r[3],
                "currency": r[4],
                "license_type": r[5],
                "period_days": r[6],
                "status": r[7],
                "created_at": r[8],
                "telegram_charge_id": r[9],
            }
            for r in rows
        ], total


def get_payment_stats() -> dict:
    """Get aggregate payment statistics for admin."""
    with get_conn() as conn:
        row = conn.execute("""
            SELECT 
                COUNT(*) as total_payments,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status = 'completed' AND currency = 'XTR' THEN amount ELSE 0 END) as total_stars,
                SUM(CASE WHEN status = 'completed' AND currency = 'TON' THEN amount ELSE 0 END) as total_ton,
                COUNT(DISTINCT user_id) as unique_payers
            FROM payment_history
        """).fetchone()
        
        return {
            "total_payments": row[0] or 0,
            "completed": row[1] or 0,
            "pending": row[2] or 0,
            "failed": row[3] or 0,
            "total_stars": row[4] or 0,
            "total_ton": row[5] or 0.0,
            "unique_payers": row[6] or 0,
        }


def get_top_traders(period: str = "all", account_type: str = "demo", limit: int = 10) -> list[dict]:
    """Get top traders by PnL."""
    import datetime
    from zoneinfo import ZoneInfo
    
    with get_conn() as conn:
        where_clauses = ["1=1"]
        params: list = []
        
        if account_type:
            where_clauses.append("(account_type = ? OR account_type IS NULL)")
            params.append(account_type)
        
        now = datetime.datetime.now(ZoneInfo("UTC"))
        if period == "today":
            # Use rolling 24h for consistency
            start = now - datetime.timedelta(hours=24)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        elif period == "week":
            start = now - datetime.timedelta(days=7)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        elif period == "month":
            start = now - datetime.timedelta(days=30)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        
        where_sql = " AND ".join(where_clauses)
        
        rows = conn.execute(f"""
            SELECT 
                user_id,
                COUNT(*) as trades,
                SUM(pnl) as total_pnl,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins
            FROM trade_logs
            WHERE {where_sql}
            GROUP BY user_id
            ORDER BY total_pnl DESC
            LIMIT ?
        """, params + [limit]).fetchall()
        
        return [
            {
                "user_id": r[0],
                "trades": r[1],
                "total_pnl": r[2] or 0.0,
                "wins": r[3] or 0,
                "winrate": (r[3] / r[1] * 100) if r[1] > 0 else 0.0,
            }
            for r in rows
        ]


def get_user_usage_report(user_id: int, exchange: str = "bybit") -> dict:
    """Get detailed usage report for a specific user with multitenancy support."""
    with get_conn() as conn:
        # Trade stats by account type
        demo_stats = get_trade_stats(user_id, account_type="demo", exchange=exchange)
        real_stats = get_trade_stats(user_id, account_type="real", exchange=exchange)
        
        # Strategy breakdown
        strategies = ["oi", "rsi_bb", "scryptomera", "scalper", "elcaro", "fibonacci"]
        strategy_stats = {}
        for strat in strategies:
            stats = get_trade_stats(user_id, strategy=strat, exchange=exchange)
            if stats["total"] > 0:
                strategy_stats[strat] = stats
        
        # Demo by strategy
        demo_by_strat = {}
        for strat in strategies:
            stats = get_trade_stats(user_id, strategy=strat, account_type="demo", exchange=exchange)
            if stats["total"] > 0:
                demo_by_strat[strat] = stats
        
        # Real by strategy
        real_by_strat = {}
        for strat in strategies:
            stats = get_trade_stats(user_id, strategy=strat, account_type="real", exchange=exchange)
            if stats["total"] > 0:
                real_by_strat[strat] = stats
        
        # User info
        user_info = get_user_full_info(user_id)
        
        # Payments
        payments = get_user_payments(user_id, limit=20)
        
        return {
            "user_info": user_info,
            "demo_stats": demo_stats,
            "real_stats": real_stats,
            "strategy_stats": strategy_stats,
            "demo_by_strategy": demo_by_strat,
            "real_by_strategy": real_by_strat,
            "payments": payments,
        }




# =====================================
# HyperLiquid DEX Functions
# =====================================

def set_hl_credentials(user_id: int, creds: dict = None, private_key: str = None, 
                       vault_address: str = None, testnet: bool = False,
                       account_type: str = None):
    """
    Save HyperLiquid credentials for user.
    
    New architecture: separate credentials for testnet and mainnet.
    - account_type='testnet' -> saves to hl_testnet_private_key
    - account_type='mainnet' -> saves to hl_mainnet_private_key
    - If account_type is None, uses testnet param for backward compatibility
    
    Also updates legacy hl_private_key for backward compatibility.
    """
    ensure_user(user_id)
    
    # Support dict or individual params
    if creds:
        # Check for new multitenancy field names first, fallback to legacy
        private_key = (creds.get("hl_mainnet_private_key") or 
                      creds.get("hl_testnet_private_key") or 
                      creds.get("hl_private_key", private_key))
        wallet_address = (creds.get("hl_mainnet_wallet_address") or 
                         creds.get("hl_testnet_wallet_address") or 
                         creds.get("hl_wallet_address"))
        vault_address = creds.get("hl_vault_address", vault_address)
        testnet = creds.get("hl_testnet", testnet)
        account_type = creds.get("account_type", account_type)
    else:
        wallet_address = None
    
    # Determine target account type
    if account_type is None:
        account_type = "testnet" if testnet else "mainnet"
    
    # Derive address from private key if not provided
    if private_key and not wallet_address:
        try:
            from eth_account import Account
            account = Account.from_key(private_key)
            wallet_address = account.address
        except Exception:
            pass
    
    with get_conn() as conn:
        if account_type == "testnet":
            # Save to testnet columns
            conn.execute("""
                UPDATE users SET
                    hl_testnet_private_key = ?,
                    hl_testnet_wallet_address = ?,
                    hl_vault_address = ?,
                    hl_testnet = TRUE,
                    hl_private_key = ?,
                    hl_wallet_address = ?
                WHERE user_id = ?
            """, (private_key, wallet_address, vault_address, private_key, wallet_address, user_id))
        else:
            # Save to mainnet columns
            conn.execute("""
                UPDATE users SET
                    hl_mainnet_private_key = ?,
                    hl_mainnet_wallet_address = ?,
                    hl_vault_address = ?,
                    hl_testnet = FALSE,
                    hl_private_key = ?,
                    hl_wallet_address = ?
                WHERE user_id = ?
            """, (private_key, wallet_address, vault_address, private_key, wallet_address, user_id))
        conn.commit()
    invalidate_user_cache(user_id)


def get_hl_credentials(user_id: int, account_type: str = None) -> dict:
    """
    Get HyperLiquid credentials for user.
    
    Args:
        user_id: User ID
        account_type: 'testnet' or 'mainnet'. If None, returns based on hl_testnet flag.
    
    Returns:
        Dict with hl_private_key, hl_wallet_address, hl_vault_address, hl_testnet, hl_enabled
    """
    with get_conn() as conn:
        row = conn.execute("""
            SELECT hl_private_key, hl_wallet_address, hl_vault_address, hl_testnet, hl_enabled,
                   hl_testnet_private_key, hl_testnet_wallet_address,
                   hl_mainnet_private_key, hl_mainnet_wallet_address
            FROM users WHERE user_id = ?
        """, (user_id,)).fetchone()
        
        if not row:
            return {
                "hl_private_key": None,
                "hl_wallet_address": None,
                "hl_vault_address": None,
                "hl_testnet": False,
                "hl_enabled": False,
                "hl_testnet_private_key": None,
                "hl_testnet_wallet_address": None,
                "hl_mainnet_private_key": None,
                "hl_mainnet_wallet_address": None,
            }
        
        # Unpack all columns
        (legacy_key, legacy_addr, vault_addr, is_testnet, is_enabled,
         testnet_key, testnet_addr, mainnet_key, mainnet_addr) = row
        
        is_testnet = bool(is_testnet) if is_testnet is not None else False
        is_enabled = bool(is_enabled) if is_enabled is not None else False
        
        # Determine which key to return as primary
        if account_type == "testnet":
            primary_key = testnet_key or legacy_key
            primary_addr = testnet_addr or legacy_addr
        elif account_type == "mainnet":
            primary_key = mainnet_key or legacy_key
            primary_addr = mainnet_addr or legacy_addr
        elif is_testnet:
            primary_key = testnet_key or legacy_key
            primary_addr = testnet_addr or legacy_addr
        else:
            primary_key = mainnet_key or legacy_key
            primary_addr = mainnet_addr or legacy_addr
        
        return {
            "hl_private_key": primary_key,
            "hl_wallet_address": primary_addr,
            "hl_vault_address": vault_addr,
            "hl_testnet": is_testnet,
            "hl_enabled": is_enabled,
            # New fields for explicit access
            "hl_testnet_private_key": testnet_key,
            "hl_testnet_wallet_address": testnet_addr,
            "hl_mainnet_private_key": mainnet_key,
            "hl_mainnet_wallet_address": mainnet_addr,
        }


def get_exchange_type(user_id: int) -> str:
    """Get active exchange type for user. Returns 'bybit' or 'hyperliquid'."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT exchange_type FROM users WHERE user_id = ?", 
            (user_id,)
        ).fetchone()
        return row[0] if row and row[0] else "bybit"


def set_exchange_type(user_id: int, exchange_type: str):
    """Set active exchange type for user."""
    ensure_user(user_id)
    if exchange_type not in ("bybit", "hyperliquid"):
        raise ValueError(f"Invalid exchange type: {exchange_type}")
    
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET exchange_type = ? WHERE user_id = ?",
            (exchange_type, user_id)
        )
        conn.commit()


def is_hl_enabled(user_id: int) -> bool:
    """Check if HyperLiquid is enabled and configured for user."""
    creds = get_hl_credentials(user_id)
    # HL is enabled if user has ANY private key AND hl_enabled flag is set
    has_any_key = (
        creds.get("hl_testnet_private_key") or 
        creds.get("hl_mainnet_private_key") or 
        creds.get("hl_private_key")
    )
    return bool(creds.get("hl_enabled") and has_any_key)


def set_hl_enabled(user_id: int, enabled: bool):
    """Enable or disable HyperLiquid for user."""
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET hl_enabled = %s WHERE user_id = %s",
            (1 if enabled else 0, user_id)  # Convert to int for INTEGER column
        )
        conn.commit()
    invalidate_user_cache(user_id)


def is_bybit_enabled(user_id: int) -> bool:
    """Check if Bybit trading is enabled AND configured for user.
    
    Returns True only if:
    1. bybit_enabled flag is True (or None for backward compat)
    2. User has at least demo OR real credentials configured
    """
    with get_conn() as conn:
        row = conn.execute(
            "SELECT bybit_enabled, demo_api_key, demo_api_secret, real_api_key, real_api_secret FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()
    
    if not row:
        return False
    
    bybit_enabled = row[0]
    # If explicitly disabled, return False
    if bybit_enabled is False or bybit_enabled == 0:
        return False
    
    # Check if any credentials exist
    has_demo = bool(row[1] and row[2])
    has_real = bool(row[3] and row[4])
    
    return has_demo or has_real


def set_bybit_enabled(user_id: int, enabled: bool):
    """Enable or disable Bybit trading for user."""
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET bybit_enabled = ? WHERE user_id = ?",
            (bool(enabled), user_id)
        )
        conn.commit()
    invalidate_user_cache(user_id)


def clear_hl_credentials(user_id: int, account_type: str = None):
    """
    Clear HyperLiquid credentials for user.
    
    Args:
        user_id: User ID
        account_type: 'testnet', 'mainnet', or None (clear all)
    """
    with get_conn() as conn:
        if account_type == "testnet":
            conn.execute("""
                UPDATE users SET
                    hl_testnet_private_key = NULL,
                    hl_testnet_wallet_address = NULL
                WHERE user_id = ?
            """, (user_id,))
        elif account_type == "mainnet":
            conn.execute("""
                UPDATE users SET
                    hl_mainnet_private_key = NULL,
                    hl_mainnet_wallet_address = NULL
                WHERE user_id = ?
            """, (user_id,))
        else:
            # Clear all HL credentials
            conn.execute("""
                UPDATE users SET
                    hl_private_key = NULL,
                    hl_wallet_address = NULL,
                    hl_vault_address = NULL,
                    hl_testnet = FALSE,
                    hl_testnet_private_key = NULL,
                    hl_testnet_wallet_address = NULL,
                    hl_mainnet_private_key = NULL,
                    hl_mainnet_wallet_address = NULL,
                    exchange_type = 'bybit'
                WHERE user_id = ?
            """, (user_id,))
        conn.commit()
    invalidate_user_cache(user_id)


# =====================================
# Exchange Mode Functions (both exchanges support)
# =====================================

EXCHANGE_MODES = ("bybit", "hyperliquid", "both")

def get_exchange_mode(user_id: int) -> str:
    """Get trading mode: 'bybit', 'hyperliquid', or 'both'."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT exchange_type FROM users WHERE user_id = ?", 
            (user_id,)
        ).fetchone()
        return row[0] if row and row[0] else "bybit"


def set_exchange_mode(user_id: int, mode: str):
    """Set trading mode: 'bybit', 'hyperliquid', or 'both'."""
    ensure_user(user_id)
    if mode not in EXCHANGE_MODES:
        raise ValueError(f"Invalid exchange mode: {mode}. Must be one of {EXCHANGE_MODES}")
    
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET exchange_type = ? WHERE user_id = ?",
            (mode, user_id)
        )
        conn.commit()


def get_exchange_status(user_id: int) -> dict:
    """Get comprehensive exchange status for user."""
    mode = get_exchange_mode(user_id)
    active_type = get_exchange_type(user_id)
    hl_creds = get_hl_credentials(user_id)
    bb_creds = get_all_user_credentials(user_id)
    
    return {
        "exchange_mode": mode,
        "active_exchange": active_type,
        "bybit": {
            "active": active_type == "bybit" or mode == "both",
            "demo": bool(bb_creds.get("demo_api_key")),
            "real": bool(bb_creds.get("real_api_key")),
            "configured": bool(bb_creds.get("demo_api_key") or bb_creds.get("real_api_key")),
        },
        "hyperliquid": {
            "active": active_type == "hyperliquid" or mode == "both",
            "configured": bool(
                hl_creds.get("hl_private_key") or 
                hl_creds.get("hl_wallet_address") or
                hl_creds.get("hl_mainnet_private_key") or
                hl_creds.get("hl_testnet_private_key")
            ),
            "testnet": hl_creds.get("hl_testnet", False),
            "wallet": hl_creds.get("hl_wallet_address") or hl_creds.get("hl_mainnet_wallet_address") or hl_creds.get("hl_testnet_wallet_address"),
        }
    }


def get_hl_trading_mode(user_id: int) -> str:
    """Get HyperLiquid trading mode: 'mainnet' or 'testnet'."""
    creds = get_hl_credentials(user_id)
    return "testnet" if creds.get("hl_testnet") else "mainnet"


def set_hl_trading_mode(user_id: int, mode: str):
    """Set HyperLiquid trading mode: 'mainnet' or 'testnet'."""
    if mode not in ("mainnet", "testnet"):
        raise ValueError(f"Invalid HL trading mode: {mode}")
    
    creds = get_hl_credentials(user_id)
    if creds.get("hl_private_key"):
        set_hl_credentials(
            user_id,
            creds["hl_private_key"],
            creds.get("hl_vault_address"),
            mode == "testnet"
        )


def get_user_exchanges_status(user_id: int) -> dict:
    """Get full status of both exchanges for user."""
    from db import get_user_credentials, get_trading_mode
    
    # Bybit status
    bybit_creds = get_user_credentials(user_id)
    bybit_demo = bool(bybit_creds.get("demo_api_key"))
    bybit_real = bool(bybit_creds.get("real_api_key"))
    bybit_mode = get_trading_mode(user_id) or "demo"
    
    # HyperLiquid status
    hl_creds = get_hl_credentials(user_id)
    hl_configured = bool(hl_creds.get("hl_private_key"))
    hl_testnet = hl_creds.get("hl_testnet", False)
    hl_enabled = hl_creds.get("hl_enabled", False)
    
    # Exchange mode
    exchange_mode = get_exchange_mode(user_id)
    
    return {
        "exchange_mode": exchange_mode,
        "bybit": {
            "demo_configured": bybit_demo,
            "real_configured": bybit_real,
            "trading_mode": bybit_mode,
            "active": exchange_mode in ("bybit", "both"),
        },
        "hyperliquid": {
            "configured": hl_configured,
            "address": hl_creds.get("hl_address"),
            "testnet": hl_testnet,
            "enabled": hl_enabled,
            "active": exchange_mode in ("hyperliquid", "both") and hl_configured,
        },
    }


# ============ CUSTOM STRATEGIES FUNCTIONS ============

def get_user_strategies(user_id: int) -> list:
    """Get all custom strategies for a user."""
    with get_conn() as conn:
        cur = conn.execute(
            """SELECT id, user_id, name, description, config_json, is_active, is_public, 
                      performance_stats, created_at, updated_at
               FROM custom_strategies WHERE user_id = ?
               ORDER BY created_at DESC""",
            (user_id,)
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows] if rows else []


def get_active_trading_strategies(user_id: int, exchange: str = None, account_type: str = None) -> list:
    """
    Get all active strategies for live trading.
    Includes: system strategies (elcaro, fibonacci, etc.) and custom/purchased strategies.
    Used by bot to determine which strategies to process signals for.
    
    Args:
        user_id: User ID
        exchange: Exchange type ('bybit', 'hyperliquid'). If None, uses user's default.
        account_type: Account type ('demo', 'real', 'testnet', 'mainnet'). If None, uses user's default.
    """
    import json
    
    active_strategies = []
    cfg = get_user_config(user_id)
    
    # Get user's trading context if exchange/account_type not provided
    if exchange is None or account_type is None:
        context = get_user_trading_context(user_id)
        exchange = exchange or context.get("exchange", "bybit")
        account_type = account_type or context.get("account_type", "demo")
    
    # System strategies
    system_strats = [
        ("elcaro", "trade_elcaro"),
        ("fibonacci", "trade_fibonacci"),
        ("scryptomera", "trade_scryptomera"),
        ("scalper", "trade_scalper"),
        ("oi", "trade_oi"),
        ("rsi_bb", "trade_rsi_bb"),
    ]
    
    for strat_name, field in system_strats:
        if cfg.get(field):
            strat_settings = get_strategy_settings(user_id, strat_name, exchange, account_type)
            active_strategies.append({
                "type": "system",
                "id": strat_name,
                "name": strat_name.replace("_", " ").title(),
                "settings": strat_settings
            })
    
    # Custom strategies
    with get_conn() as conn:
        cur = conn.execute(
            """SELECT id, name, config, base_strategy 
               FROM custom_strategies 
               WHERE user_id = ? AND is_active = 1""",
            (user_id,)
        )
        for row in cur.fetchall():
            config = json.loads(row["config"]) if row["config"] else {}
            active_strategies.append({
                "type": "custom",
                "id": row["id"],
                "name": row["name"],
                "base_strategy": row["base_strategy"],
                "config": config
            })
        
        # Purchased strategies
        cur = conn.execute(
            """SELECT s.id, s.name, s.config, s.base_strategy
               FROM strategy_purchases p
               JOIN custom_strategies s ON p.strategy_id = s.id
               WHERE p.buyer_id = ? AND p.is_active = 1""",
            (user_id,)
        )
        for row in cur.fetchall():
            config = json.loads(row["config"]) if row["config"] else {}
            active_strategies.append({
                "type": "purchased",
                "id": row["id"],
                "name": row["name"],
                "base_strategy": row["base_strategy"],
                "config": config
            })
    
    return active_strategies


def get_strategy_by_id(strategy_id: int) -> dict | None:
    """Get a custom strategy by ID."""
    with get_conn() as conn:
        cur = conn.execute(
            """SELECT id, user_id, name, description, config_json, is_active, 
                      is_public, performance_stats, created_at, updated_at
               FROM custom_strategies WHERE id = ?""",
            (strategy_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None


def create_custom_strategy(user_id: int, name: str, description: str, config: dict) -> int:
    """Create a new custom strategy and return its ID."""
    import json
    import time
    now = int(time.time())
    
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO custom_strategies 
               (user_id, name, description, config_json, is_active, is_public, created_at, updated_at)
               VALUES (?, ?, ?, ?, 0, 0, ?, ?)""",
            (user_id, name, description, json.dumps(config), now, now)
        )
        conn.commit()
        return cur.lastrowid


def update_custom_strategy(strategy_id: int, user_id: int, **updates) -> bool:
    """Update a custom strategy. Returns True if updated."""
    import json
    import time
    
    allowed_fields = {'name', 'description', 'config_json', 'is_active', 'is_public', 'performance_stats'}
    filtered = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if not filtered:
        return False
    
    # JSON encode dict fields
    for k in ['config_json', 'performance_stats']:
        if k in filtered and isinstance(filtered[k], dict):
            filtered[k] = json.dumps(filtered[k])
    
    filtered['updated_at'] = int(time.time())
    
    set_clause = ', '.join(f"{k} = ?" for k in filtered.keys())
    values = list(filtered.values()) + [strategy_id, user_id]
    
    with get_conn() as conn:
        cur = conn.execute(
            f"UPDATE custom_strategies SET {set_clause} WHERE id = ? AND user_id = ?",
            values
        )
        conn.commit()
        return cur.rowcount > 0


def delete_custom_strategy(strategy_id: int, user_id: int) -> bool:
    """Delete a custom strategy. Returns True if deleted."""
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM custom_strategies WHERE id = ? AND user_id = ?",
            (strategy_id, user_id)
        )
        conn.commit()
        return cur.rowcount > 0


# ============ DYNAMIC SIGNAL PARSERS FUNCTIONS ============

def get_dynamic_parsers(active_only: bool = True) -> list:
    """Get all dynamic signal parsers for signal routing."""
    import json
    query = """
        SELECT id, name, display_name, description, channel_ids, signal_pattern, 
               symbol_pattern, side_pattern, price_pattern, base_strategy, 
               default_settings, is_active, is_system
        FROM dynamic_signal_parsers
    """
    if active_only:
        query += " WHERE is_active = TRUE"
    query += " ORDER BY is_system DESC, name ASC"
    
    with get_conn() as conn:
        cur = conn.execute(query)
        rows = cur.fetchall()
        result = []
        for row in rows:
            r = dict(row)
            # Parse JSON fields
            if r.get("channel_ids"):
                r["channel_ids"] = json.loads(r["channel_ids"])
            if r.get("default_settings"):
                r["default_settings"] = json.loads(r["default_settings"])
            result.append(r)
        return result


def get_dynamic_parser_by_name(name: str) -> dict | None:
    """Get a specific dynamic parser by name."""
    import json
    with get_conn() as conn:
        cur = conn.execute(
            """SELECT * FROM dynamic_signal_parsers WHERE name = ?""",
            (name,)
        )
        row = cur.fetchone()
        if not row:
            return None
        r = dict(row)
        if r.get("channel_ids"):
            r["channel_ids"] = json.loads(r["channel_ids"])
        if r.get("default_settings"):
            r["default_settings"] = json.loads(r["default_settings"])
        return r


def create_dynamic_parser(
    name: str,
    display_name: str,
    channel_ids: list,
    signal_pattern: str,
    symbol_pattern: str,
    side_pattern: str,
    price_pattern: str = None,
    description: str = None,
    example_signal: str = None,
    base_strategy: str = "manual",
    default_settings: dict = None,
    created_by: int = None
) -> int:
    """Create a new dynamic signal parser (admin function). Returns parser ID."""
    import json
    
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO dynamic_signal_parsers 
               (name, display_name, description, channel_ids, signal_pattern, 
                symbol_pattern, side_pattern, price_pattern, example_signal,
                base_strategy, default_settings, is_active, is_system, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, TRUE, FALSE, ?)
               RETURNING id""",
            (name, display_name, description, json.dumps(channel_ids), signal_pattern,
             symbol_pattern, side_pattern, price_pattern, example_signal,
             base_strategy, json.dumps(default_settings or {}), created_by)
        )
        row = cur.fetchone()
        conn.commit()
        return row[0] if row else cur.lastrowid


def update_dynamic_parser(parser_id: int, **updates) -> bool:
    """Update a dynamic parser settings. Returns True if updated."""
    import json
    
    allowed = {'display_name', 'description', 'channel_ids', 'signal_pattern', 
               'symbol_pattern', 'side_pattern', 'price_pattern', 'example_signal',
               'base_strategy', 'default_settings', 'is_active'}
    filtered = {k: v for k, v in updates.items() if k in allowed}
    
    if not filtered:
        return False
    
    # JSON encode list/dict fields
    for k in ['channel_ids', 'default_settings']:
        if k in filtered and isinstance(filtered[k], (list, dict)):
            filtered[k] = json.dumps(filtered[k])
    
    set_clause = ', '.join(f"{k} = ?" for k in filtered.keys())
    values = list(filtered.values()) + [parser_id]
    
    with get_conn() as conn:
        cur = conn.execute(
            f"UPDATE dynamic_signal_parsers SET {set_clause} WHERE id = ? AND is_system = FALSE",
            values
        )
        conn.commit()
        return cur.rowcount > 0


def delete_dynamic_parser(parser_id: int) -> bool:
    """Delete a non-system dynamic parser. Returns True if deleted."""
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM dynamic_signal_parsers WHERE id = ? AND is_system = FALSE",
            (parser_id,)
        )
        conn.commit()
        return cur.rowcount > 0


def increment_parser_signals(parser_name: str) -> None:
    """Increment signals_parsed counter and update last_signal_at for a parser."""
    with get_conn() as conn:
        conn.execute(
            """UPDATE dynamic_signal_parsers 
               SET signals_parsed = signals_parsed + 1, last_signal_at = NOW()
               WHERE name = ?""",
            (parser_name,)
        )
        conn.commit()


# ============ USER STRATEGY DEPLOYMENTS FUNCTIONS ============

def get_user_deployments(user_id: int, active_only: bool = True) -> list:
    """Get all strategy deployments for a user."""
    import json
    
    query = """
        SELECT * FROM user_strategy_deployments
        WHERE user_id = ?
    """
    if active_only:
        query += " AND is_active = TRUE"
    query += " ORDER BY created_at DESC"
    
    with get_conn() as conn:
        cur = conn.execute(query, (user_id,))
        rows = cur.fetchall()
        result = []
        for row in rows:
            r = dict(row)
            if r.get("config_json"):
                r["config_json"] = json.loads(r["config_json"])
            if r.get("backtest_results"):
                r["backtest_results"] = json.loads(r["backtest_results"])
            result.append(r)
        return result


def get_user_deployment_by_id(deployment_id: int, user_id: int = None) -> dict | None:
    """Get a specific deployment by ID, optionally filtered by user."""
    import json
    
    query = "SELECT * FROM user_strategy_deployments WHERE id = ?"
    params = [deployment_id]
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
    
    with get_conn() as conn:
        cur = conn.execute(query, params)
        row = cur.fetchone()
        if not row:
            return None
        r = dict(row)
        if r.get("config_json"):
            r["config_json"] = json.loads(r["config_json"])
        if r.get("backtest_results"):
            r["backtest_results"] = json.loads(r["backtest_results"])
        return r


def create_user_deployment(
    user_id: int,
    name: str,
    source_type: str,  # 'backtest', 'copy', 'custom'
    source_id: int = None,
    base_strategy: str = "manual",
    config_json: dict = None,
    # Trading settings
    entry_percent: float = 1.0,
    stop_loss_percent: float = 30.0,
    take_profit_percent: float = 10.0,
    leverage: int = 10,
    use_atr: bool = False,
    atr_periods: int = 14,
    atr_multiplier: float = 2.0,
    atr_trigger_pct: float = 1.0,
    atr_step_pct: float = 0.5,
    dca_enabled: bool = False,
    dca_percent_1: float = 10.0,
    dca_percent_2: float = 25.0,
    be_enabled: bool = False,
    be_trigger_pct: float = 1.0,
    partial_tp_enabled: bool = False,
    ptp_step1_trigger: float = 2.0,
    ptp_step1_close: float = 30.0,
    ptp_step2_trigger: float = 5.0,
    ptp_step2_close: float = 50.0,
    exchange: str = "bybit",
    account_type: str = "demo",
    backtest_results: dict = None,
    is_live: bool = False
) -> int:
    """Create a new user strategy deployment. Returns deployment ID."""
    import json
    
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO user_strategy_deployments 
               (user_id, source_type, source_id, name, base_strategy, config_json,
                entry_percent, stop_loss_percent, take_profit_percent, leverage,
                use_atr, atr_periods, atr_multiplier, atr_trigger_pct, atr_step_pct,
                dca_enabled, dca_percent_1, dca_percent_2,
                be_enabled, be_trigger_pct,
                partial_tp_enabled, ptp_step1_trigger, ptp_step1_close, ptp_step2_trigger, ptp_step2_close,
                exchange, account_type, is_active, is_live, backtest_results)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, TRUE, ?, ?)
               RETURNING id""",
            (user_id, source_type, source_id, name, base_strategy, json.dumps(config_json or {}),
             entry_percent, stop_loss_percent, take_profit_percent, leverage,
             use_atr, atr_periods, atr_multiplier, atr_trigger_pct, atr_step_pct,
             dca_enabled, dca_percent_1, dca_percent_2,
             be_enabled, be_trigger_pct,
             partial_tp_enabled, ptp_step1_trigger, ptp_step1_close, ptp_step2_trigger, ptp_step2_close,
             exchange, account_type, is_live, json.dumps(backtest_results or {}))
        )
        row = cur.fetchone()
        conn.commit()
        return row[0] if row else cur.lastrowid


def update_user_deployment(deployment_id: int, user_id: int, **updates) -> bool:
    """Update a user's strategy deployment. Returns True if updated."""
    import json
    
    allowed = {'name', 'config_json', 'entry_percent', 'stop_loss_percent', 'take_profit_percent',
               'leverage', 'use_atr', 'atr_periods', 'atr_multiplier', 'atr_trigger_pct', 'atr_step_pct',
               'dca_enabled', 'dca_percent_1', 'dca_percent_2', 'be_enabled', 'be_trigger_pct',
               'partial_tp_enabled', 'ptp_step1_trigger', 'ptp_step1_close', 'ptp_step2_trigger', 'ptp_step2_close',
               'exchange', 'account_type', 'is_active', 'is_live'}
    filtered = {k: v for k, v in updates.items() if k in allowed}
    
    if not filtered:
        return False
    
    # JSON encode dict fields
    for k in ['config_json', 'backtest_results']:
        if k in filtered and isinstance(filtered[k], dict):
            filtered[k] = json.dumps(filtered[k])
    
    set_clause = ', '.join(f"{k} = ?" for k in filtered.keys())
    values = list(filtered.values()) + [deployment_id, user_id]
    
    with get_conn() as conn:
        cur = conn.execute(
            f"UPDATE user_strategy_deployments SET {set_clause} WHERE id = ? AND user_id = ?",
            values
        )
        conn.commit()
        return cur.rowcount > 0


def delete_user_deployment(deployment_id: int, user_id: int) -> bool:
    """Delete a user's deployment. Returns True if deleted."""
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM user_strategy_deployments WHERE id = ? AND user_id = ?",
            (deployment_id, user_id)
        )
        conn.commit()
        return cur.rowcount > 0


def update_deployment_performance(deployment_id: int, pnl_change: float, is_win: bool) -> None:
    """Update performance stats after a trade closes."""
    with get_conn() as conn:
        if is_win:
            conn.execute(
                """UPDATE user_strategy_deployments 
                   SET total_trades = total_trades + 1, 
                       wins = wins + 1, 
                       total_pnl = total_pnl + ?
                   WHERE id = ?""",
                (pnl_change, deployment_id)
            )
        else:
            conn.execute(
                """UPDATE user_strategy_deployments 
                   SET total_trades = total_trades + 1, 
                       losses = losses + 1, 
                       total_pnl = total_pnl + ?
                   WHERE id = ?""",
                (pnl_change, deployment_id)
            )
        conn.commit()


def get_active_user_deployments_for_trading(user_id: int, exchange: str = None, account_type: str = None) -> list:
    """Get all active LIVE deployments for a user for signal routing.
    Used in on_channel_post to check user's personal strategies."""
    import json
    
    query = """
        SELECT * FROM user_strategy_deployments
        WHERE user_id = ? AND is_active = TRUE AND is_live = TRUE
    """
    params = [user_id]
    
    if exchange:
        query += " AND exchange = ?"
        params.append(exchange)
    if account_type:
        query += " AND account_type = ?"
        params.append(account_type)
    
    with get_conn() as conn:
        cur = conn.execute(query, params)
        rows = cur.fetchall()
        result = []
        for row in rows:
            r = dict(row)
            if r.get("config_json"):
                r["config_json"] = json.loads(r["config_json"])
            result.append(r)
        return result


# ============ STRATEGY VERSIONING FUNCTIONS ============

def create_strategy_version(
    strategy_id: int, 
    version: str, 
    config_json: str, 
    created_by: int,
    change_log: str = None,
    backtest_result: str = None
) -> int:
    """Create a new version of a strategy. Returns version id."""
    import time
    now = int(time.time())
    
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO strategy_versions 
               (strategy_id, version, config_json, change_log, backtest_result, created_by, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (strategy_id, version, config_json, change_log, backtest_result, created_by, now)
        )
        conn.commit()
        return cur.lastrowid


def get_strategy_versions(strategy_id: int) -> list:
    """Get all versions of a strategy, ordered by creation date."""
    with get_conn() as conn:
        cur = conn.execute(
            """SELECT id, strategy_id, version, config_json, change_log, 
                      backtest_result, created_by, created_at
               FROM strategy_versions 
               WHERE strategy_id = ?
               ORDER BY created_at DESC""",
            (strategy_id,)
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows] if rows else []


def get_strategy_version(version_id: int) -> dict | None:
    """Get a specific strategy version by ID."""
    with get_conn() as conn:
        cur = conn.execute(
            """SELECT id, strategy_id, version, config_json, change_log, 
                      backtest_result, created_by, created_at
               FROM strategy_versions WHERE id = ?""",
            (version_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None


def get_latest_strategy_version(strategy_id: int) -> dict | None:
    """Get the latest version of a strategy."""
    with get_conn() as conn:
        cur = conn.execute(
            """SELECT id, strategy_id, version, config_json, change_log, 
                      backtest_result, created_by, created_at
               FROM strategy_versions 
               WHERE strategy_id = ?
               ORDER BY created_at DESC LIMIT 1""",
            (strategy_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None


def rollback_to_version(strategy_id: int, version_id: int, user_id: int) -> bool:
    """Rollback strategy to a specific version. Returns True if successful."""
    import json
    import time
    
    version = get_strategy_version(version_id)
    if not version or version["strategy_id"] != strategy_id:
        return False
    
    # Update main strategy with version config
    now = int(time.time())
    with get_conn() as conn:
        cur = conn.execute(
            """UPDATE custom_strategies 
               SET config_json = ?, updated_at = ?
               WHERE id = ? AND user_id = ?""",
            (version["config_json"], now, strategy_id, user_id)
        )
        conn.commit()
        return cur.rowcount > 0


# ============ STRATEGY LIVE STATE FUNCTIONS ============

def get_strategy_live_state(user_id: int, strategy_id: int, exchange: str = "bybit", account_type: str = "demo") -> dict | None:
    """Get live trading state for a strategy."""
    with get_conn() as conn:
        cur = conn.execute(
            """SELECT * FROM strategy_live_state 
               WHERE user_id = ? AND strategy_id = ? AND exchange = ? AND account_type = ?""",
            (user_id, strategy_id, exchange, account_type)
        )
        row = cur.fetchone()
        if row:
            result = dict(row)
            # Parse JSON fields
            import json
            for field in ['open_positions', 'pending_orders']:
                if result.get(field):
                    try:
                        result[field] = json.loads(result[field])
                    except (json.JSONDecodeError, TypeError):
                        result[field] = []
            return result
        return None


def get_all_running_strategies(user_id: int = None) -> list:
    """Get all currently running strategies, optionally filtered by user."""
    with get_conn() as conn:
        if user_id:
            cur = conn.execute(
                """SELECT ls.*, s.name as strategy_name, s.config_json
                   FROM strategy_live_state ls
                   JOIN custom_strategies s ON ls.strategy_id = s.id
                   WHERE ls.user_id = ? AND ls.is_running = 1""",
                (user_id,)
            )
        else:
            cur = conn.execute(
                """SELECT ls.*, s.name as strategy_name, s.config_json
                   FROM strategy_live_state ls
                   JOIN custom_strategies s ON ls.strategy_id = s.id
                   WHERE ls.is_running = 1"""
            )
        rows = cur.fetchall()
        return [dict(r) for r in rows] if rows else []


def start_strategy_live(
    user_id: int, 
    strategy_id: int, 
    exchange: str = "bybit", 
    account_type: str = "demo"
) -> int:
    """Start a strategy in live trading mode. Returns state id."""
    import time
    now = int(time.time())
    
    with get_conn() as conn:
        # Check if state exists
        cur = conn.execute(
            """SELECT id FROM strategy_live_state 
               WHERE user_id = ? AND strategy_id = ? AND exchange = ? AND account_type = ?""",
            (user_id, strategy_id, exchange, account_type)
        )
        existing = cur.fetchone()
        
        if existing:
            # Update existing state
            conn.execute(
                """UPDATE strategy_live_state 
                   SET is_running = 1, is_paused = 0, started_at = ?, updated_at = ?,
                       session_pnl = 0, session_trades = 0
                   WHERE id = ?""",
                (now, now, existing[0])
            )
            conn.commit()
            return existing[0]
        else:
            # Create new state
            cur = conn.execute(
                """INSERT INTO strategy_live_state 
                   (user_id, strategy_id, exchange, account_type, is_running, started_at, updated_at)
                   VALUES (?, ?, ?, ?, 1, ?, ?)""",
                (user_id, strategy_id, exchange, account_type, now, now)
            )
            conn.commit()
            return cur.lastrowid


def stop_strategy_live(user_id: int, strategy_id: int, exchange: str = "bybit", account_type: str = "demo") -> bool:
    """Stop a running strategy. Returns True if stopped."""
    import time
    now = int(time.time())
    
    with get_conn() as conn:
        cur = conn.execute(
            """UPDATE strategy_live_state 
               SET is_running = 0, stopped_at = ?, updated_at = ?
               WHERE user_id = ? AND strategy_id = ? AND exchange = ? AND account_type = ?""",
            (now, now, user_id, strategy_id, exchange, account_type)
        )
        conn.commit()
        return cur.rowcount > 0


def pause_strategy_live(user_id: int, strategy_id: int, exchange: str = "bybit", account_type: str = "demo") -> bool:
    """Pause a running strategy (keeps state but stops processing). Returns True if paused."""
    import time
    now = int(time.time())
    
    with get_conn() as conn:
        cur = conn.execute(
            """UPDATE strategy_live_state 
               SET is_paused = 1, updated_at = ?
               WHERE user_id = ? AND strategy_id = ? AND exchange = ? AND account_type = ?""",
            (now, user_id, strategy_id, exchange, account_type)
        )
        conn.commit()
        return cur.rowcount > 0


def resume_strategy_live(user_id: int, strategy_id: int, exchange: str = "bybit", account_type: str = "demo") -> bool:
    """Resume a paused strategy. Returns True if resumed."""
    import time
    now = int(time.time())
    
    with get_conn() as conn:
        cur = conn.execute(
            """UPDATE strategy_live_state 
               SET is_paused = 0, updated_at = ?
               WHERE user_id = ? AND strategy_id = ? AND exchange = ? AND account_type = ?""",
            (now, user_id, strategy_id, exchange, account_type)
        )
        conn.commit()
        return cur.rowcount > 0


def update_strategy_live_state(
    user_id: int, 
    strategy_id: int, 
    exchange: str = "bybit", 
    account_type: str = "demo",
    **updates
) -> bool:
    """Update live state fields (positions, pnl, trades, etc.)."""
    import json
    import time
    
    allowed_fields = {
        'open_positions', 'pending_orders', 'session_pnl', 'session_trades',
        'total_pnl', 'total_trades', 'win_rate', 'daily_trades', 'daily_pnl',
        'daily_reset_at', 'last_signal_at'
    }
    filtered = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if not filtered:
        return False
    
    # JSON encode list/dict fields
    for k in ['open_positions', 'pending_orders']:
        if k in filtered and isinstance(filtered[k], (list, dict)):
            filtered[k] = json.dumps(filtered[k])
    
    filtered['updated_at'] = int(time.time())
    
    set_clause = ', '.join(f"{k} = ?" for k in filtered.keys())
    values = list(filtered.values()) + [user_id, strategy_id, exchange, account_type]
    
    with get_conn() as conn:
        cur = conn.execute(
            f"""UPDATE strategy_live_state SET {set_clause} 
                WHERE user_id = ? AND strategy_id = ? AND exchange = ? AND account_type = ?""",
            values
        )
        conn.commit()
        return cur.rowcount > 0


def record_strategy_trade(
    user_id: int,
    strategy_id: int,
    pnl: float,
    is_win: bool,
    exchange: str = "bybit",
    account_type: str = "demo"
) -> bool:
    """Record a completed trade for a strategy (updates stats)."""
    import time
    now = int(time.time())
    
    state = get_strategy_live_state(user_id, strategy_id, exchange, account_type)
    if not state:
        return False
    
    # Update counters
    session_trades = (state.get('session_trades') or 0) + 1
    session_pnl = (state.get('session_pnl') or 0) + pnl
    total_trades = (state.get('total_trades') or 0) + 1
    total_pnl = (state.get('total_pnl') or 0) + pnl
    daily_trades = (state.get('daily_trades') or 0) + 1
    daily_pnl = (state.get('daily_pnl') or 0) + pnl
    
    # Calculate win rate
    # Approximate: if win, increment wins count (stored in total trades - losses)
    # For simplicity, recalculate based on session for now
    wins = (state.get('win_rate', 0) / 100 * (total_trades - 1)) + (1 if is_win else 0)
    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
    
    return update_strategy_live_state(
        user_id, strategy_id, exchange, account_type,
        session_trades=session_trades,
        session_pnl=session_pnl,
        total_trades=total_trades,
        total_pnl=total_pnl,
        daily_trades=daily_trades,
        daily_pnl=daily_pnl,
        win_rate=win_rate,
        last_signal_at=now
    )


def get_public_strategies(limit: int = 50, offset: int = 0) -> list:
    """Get public strategies for marketplace."""
    with get_conn() as conn:
        cur = conn.execute(
            """SELECT s.id, s.user_id, s.name, s.description, s.config, 
                      s.performance_stats, s.created_at,
                      m.price, m.sales_count, m.average_rating
               FROM custom_strategies s
               LEFT JOIN strategy_marketplace m ON s.id = m.strategy_id
               WHERE s.is_public = 1 AND s.is_active = 1
               ORDER BY m.average_rating DESC, m.sales_count DESC
               LIMIT ? OFFSET ?""",
            (limit, offset)
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows] if rows else []


def get_user_purchases(user_id: int) -> list:
    """Get all strategies purchased by user."""
    with get_conn() as conn:
        cur = conn.execute(
            """SELECT p.id, p.marketplace_id, p.strategy_id, p.amount_paid as price_paid, 
                      p.purchased_at, s.name, s.description, s.config_json
               FROM strategy_purchases p
               JOIN custom_strategies s ON p.strategy_id = s.id
               WHERE p.buyer_id = ?
               ORDER BY p.purchased_at DESC""",
            (user_id,)
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows] if rows else []


def execute_query(query: str, params: tuple = ()) -> int:
    """Execute a query and return rowcount."""
    with get_conn() as conn:
        cur = conn.execute(query, params)
        conn.commit()
        return cur.rowcount


def get_top_strategies(limit: int = 20, strategy_type: str = None) -> list:
    """Get top performing strategies from rankings."""
    with get_conn() as conn:
        if strategy_type:
            cur = conn.execute(
                """SELECT * FROM top_strategies 
                   WHERE strategy_type = ?
                   ORDER BY rank ASC LIMIT ?""",
                (strategy_type, limit)
            )
        else:
            cur = conn.execute(
                "SELECT * FROM top_strategies ORDER BY rank ASC LIMIT ?",
                (limit,)
            )
        rows = cur.fetchall()
        return [dict(r) for r in rows] if rows else []


def update_strategy_ranking(
    strategy_type: str,
    strategy_id: int | None,
    strategy_name: str,
    win_rate: float,
    total_pnl: float,
    total_trades: int,
    sharpe_ratio: float,
    max_drawdown: float,
    rank: int,
    config_json: str = None
) -> int:
    """Update or insert strategy ranking."""
    import time
    now = int(time.time())
    
    with get_conn() as conn:
        # Try to update existing
        if strategy_id:
            cur = conn.execute(
                """UPDATE top_strategies SET
                   win_rate = ?, total_pnl = ?, total_trades = ?,
                   sharpe_ratio = ?, max_drawdown = ?, rank = ?,
                   config_json = ?, updated_at = ?
                   WHERE strategy_type = ? AND strategy_id = ?""",
                (win_rate, total_pnl, total_trades, sharpe_ratio, 
                 max_drawdown, rank, config_json, now, strategy_type, strategy_id)
            )
            if cur.rowcount > 0:
                conn.commit()
                return cur.lastrowid
        
        # Insert new
        cur = conn.execute(
            """INSERT INTO top_strategies
               (strategy_type, strategy_id, strategy_name, win_rate, total_pnl,
                total_trades, sharpe_ratio, max_drawdown, rank, config_json, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (strategy_type, strategy_id, strategy_name, win_rate, total_pnl,
             total_trades, sharpe_ratio, max_drawdown, rank, config_json, now)
        )
        conn.commit()
        return cur.lastrowid


# ------------------------------------------------------------------------------------
# Trade History
# ------------------------------------------------------------------------------------
def get_trade_history(user_id: int, limit: int = 100, exchange: str = None) -> list:
    """
    Get trade history for a user from the trade_logs table.
    Returns list of dicts with trade data.
    NOTE: Changed from 'trades' table to 'trade_logs' which is the actual table used by the bot.
    """
    with get_conn() as conn:
        if exchange:
            cur = conn.execute(
                """SELECT id, symbol, side, entry_price, exit_price, 
                          pnl, pnl_pct, strategy, ts, exit_reason, account_type
                   FROM trade_logs 
                   WHERE user_id = ? AND (exchange = ? OR exchange IS NULL)
                   ORDER BY ts DESC LIMIT ?""",
                (user_id, exchange, limit)
            )
        else:
            cur = conn.execute(
                """SELECT id, symbol, side, entry_price, exit_price, 
                          pnl, pnl_pct, strategy, ts, exit_reason, account_type
                   FROM trade_logs 
                   WHERE user_id = ?
                   ORDER BY ts DESC LIMIT ?""",
                (user_id, limit)
            )
        
        rows = cur.fetchall()
        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "symbol": row[1],
                "side": row[2],
                "entry_price": row[3],
                "exit_price": row[4],
                "size": 0,  # Not stored in trade_logs, but kept for compatibility
                "pnl": row[5],
                "pnl_percent": row[6],
                "exchange": exchange or "bybit",
                "strategy": row[7],
                "time": row[8],
                "created_at": row[8],
                "closed_at": row[8],  # trade_logs only has ts (exit time)
                "exit_reason": row[9],
                "account_type": row[10]
            })
        return result


def save_trade(user_id: int, symbol: str, side: str, entry_price: float,
               exit_price: float = None, size: float = 0, pnl: float = 0,
               pnl_percent: float = 0, exchange: str = "bybit", 
               strategy: str = None) -> int:
    """Save a trade to history."""
    import time
    now = int(time.time())
    
    with get_conn() as conn:
        # Ensure table exists (PostgreSQL syntax)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                symbol TEXT,
                side TEXT,
                entry_price REAL,
                exit_price REAL,
                size REAL,
                pnl REAL,
                pnl_percent REAL,
                exchange TEXT DEFAULT 'bybit',
                strategy TEXT,
                created_at BIGINT,
                closed_at BIGINT
            )
        """)
        
        cur = conn.execute(
            """INSERT INTO trades 
               (user_id, symbol, side, entry_price, exit_price, size, 
                pnl, pnl_percent, exchange, strategy, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, symbol, side, entry_price, exit_price, size,
             pnl, pnl_percent, exchange, strategy, now)
        )
        conn.commit()
        return cur.lastrowid


def close_trade(trade_id: int, exit_price: float, pnl: float, pnl_percent: float) -> bool:
    """Close an existing trade with exit price and PnL."""
    import time
    now = int(time.time())
    
    with get_conn() as conn:
        cur = conn.execute(
            """UPDATE trades SET exit_price = ?, pnl = ?, pnl_percent = ?, closed_at = ?
               WHERE id = ?""",
            (exit_price, pnl, pnl_percent, now, trade_id)
        )
        conn.commit()
        return cur.rowcount > 0



# =====================================================
# PAYMENT & SUBSCRIPTION FUNCTIONS
# =====================================================

def check_duplicate_transaction(transaction_hash: str) -> bool:
    """Check if transaction hash already exists in payment history.
    
    Returns True if duplicate found (payment should be rejected).
    """
    if not transaction_hash or transaction_hash.startswith("manual_"):
        return False
    
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM payment_history WHERE transaction_id = ?",
            (transaction_hash,)
        ).fetchone()
        return row is not None


def add_payment_record(
    user_id: int,
    plan: str,
    period: str,
    amount: float,
    payment_method: str,
    wallet_address: str = None,
    transaction_hash: str = None
):
    """Record a payment transaction.
    
    Raises ValueError if transaction_hash is duplicate.
    """
    import time
    
    # Check for duplicate transaction
    if transaction_hash and check_duplicate_transaction(transaction_hash):
        raise ValueError(f"Duplicate transaction: {transaction_hash}")
    
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO payment_history (
                user_id, amount, payment_method, plan_type, 
                transaction_id, created_at, status
            ) VALUES (?, ?, ?, ?, ?, NOW(), ?)
        """, (
            user_id,
            amount,
            payment_method,
            f"{plan}_{period}",
            transaction_hash or f"manual_{int(time.time())}",
            "completed"
        ))


def get_user_by_referral_code(referral_code: str) -> int:
    """Get user ID by referral code"""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT user_id FROM users WHERE referral_code = ?",
            (referral_code,)
        ).fetchone()
        return row[0] if row else None


def add_referral_connection(user_id: int, referrer_id: int):
    """Create referral connection between users"""
    with get_conn() as conn:
        # Add referral field if not exists
        if not _col_exists(conn, "users", "referred_by"):
            conn.execute("ALTER TABLE users ADD COLUMN referred_by INTEGER")
        
        conn.execute(
            "UPDATE users SET referred_by = ? WHERE user_id = ?",
            (referrer_id, user_id)
        )
        
        # Give bonus to referrer (e.g., 7 days premium)
        extend_license(referrer_id, 7)


# NOTE: get_user_payments is defined earlier in this file (line ~4244)
# with correct column names matching payment_history schema


def get_referral_stats(user_id: int) -> dict:
    """Get user's referral statistics"""
    with get_conn() as conn:
        # Count referrals
        row = conn.execute(
            "SELECT COUNT(*) FROM users WHERE referred_by = ?",
            (user_id,)
        ).fetchone()
        
        total_referrals = row[0] if row else 0
        
        # Get referral code
        row = conn.execute(
            "SELECT referral_code FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        
        referral_code = row[0] if row else None
        
        # Generate referral code if not exists
        if not referral_code:
            import secrets
            import string
            # SECURITY: Use cryptographically secure random for referral codes
            alphabet = string.ascii_uppercase + string.digits
            referral_code = ''.join(secrets.choice(alphabet) for _ in range(8))
            conn.execute(
                "UPDATE users SET referral_code = ? WHERE user_id = ?",
                (referral_code, user_id)
            )
        
        return {
            "referral_code": referral_code,
            "total_referrals": total_referrals,
            "earnings": total_referrals * 5  # $5 per referral
        }


# ═══════════════════════════════════════════════════════════════════════════════════
# USER PENDING INPUTS (Persistent across bot restarts)
# ═══════════════════════════════════════════════════════════════════════════════════

def set_pending_input(user_id: int, input_type: str, input_data: str = None):
    """Set pending input for user (survives bot restarts)."""
    return pg_set_pending_input(user_id, input_type, input_data)


def get_pending_input(user_id: int) -> dict | None:
    """Get pending input for user."""
    return pg_get_pending_input(user_id)


def clear_pending_input(user_id: int):
    """Clear pending input for user."""
    return pg_clear_pending_input(user_id)

# ═══════════════════════════════════════════════════════════════════════════════════
# SIMPLIFIED STRATEGY SETTINGS API (NEW - uses core/strategy_settings.py)
# ═══════════════════════════════════════════════════════════════════════════════════

from core.strategy_settings import (
    get_strategy_side_settings as _get_strategy_side_settings,
    set_strategy_side_setting as _set_strategy_side_setting,
    reset_strategy_side_to_defaults as _reset_strategy_side_to_defaults,
    get_effective_settings as _get_effective_settings_new,
    get_all_strategy_settings as _get_all_strategy_settings,
    get_strategy_enabled as _get_strategy_enabled,
    get_default_settings as _get_default_settings,
    STRATEGY_NAMES as STRATEGY_NAMES_NEW,
    STRATEGY_DISPLAY_NAMES,
)


def get_strategy_side_settings(user_id: int, strategy: str, side: str) -> dict:
    """Get settings for strategy + side (LONG/SHORT). Simple, no fallback."""
    return _get_strategy_side_settings(user_id, strategy, side)


def set_strategy_side_setting(user_id: int, strategy: str, side: str, field: str, value) -> bool:
    """Set a single field for strategy + side."""
    return _set_strategy_side_setting(user_id, strategy, side, field, value)


def reset_strategy_side(user_id: int, strategy: str, side: str) -> bool:
    """Reset strategy + side to ENV defaults."""
    return _reset_strategy_side_to_defaults(user_id, strategy, side)


def get_trade_settings(user_id: int, strategy: str, side: str) -> dict:
    """Get effective settings for trading. Direct, simple."""
    return _get_effective_settings_new(user_id, strategy, side)


def get_both_side_settings(user_id: int, strategy: str) -> dict:
    """Get LONG and SHORT settings for a strategy."""
    return _get_all_strategy_settings(user_id, strategy)


def is_strategy_enabled(user_id: int, strategy: str, exchange: str = "bybit") -> bool:
    """Check if strategy is enabled with multitenancy support."""
    return _get_strategy_enabled(user_id, strategy, exchange=exchange)


def get_defaults() -> dict:
    """Get default settings from ENV."""
    return _get_default_settings()


# ═══════════════════════════════════════════════════════════════════════════════════
# ADMIN ERROR LOG - For admin error management with approve/notify
# ═══════════════════════════════════════════════════════════════════════════════════

def log_admin_error(
    user_id: int,
    error_type: str,
    error_message: str,
    error_code: str = None,
    context: dict = None,
    exchange: str = "bybit",
    account_type: str = "demo"
) -> int | None:
    """
    Log error for admin review. If same error exists (not approved), increment counter.
    Returns error_id or None.
    """
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            
            # Try to find existing error (same user, type, code, exchange, account)
            cur.execute("""
                SELECT id, occurrence_count FROM admin_error_log 
                WHERE user_id = %s AND error_type = %s 
                  AND COALESCE(error_code, '') = COALESCE(%s, '')
                  AND exchange = %s AND account_type = %s
                  AND status != 'approved'
                LIMIT 1
            """, (user_id, error_type, error_code, exchange, account_type))
            
            existing = cur.fetchone()
            
            if existing:
                # Update existing error - increment counter
                error_id, count = existing[0], existing[1]
                cur.execute("""
                    UPDATE admin_error_log 
                    SET occurrence_count = %s,
                        last_seen = NOW(),
                        error_message = %s,
                        context = %s
                    WHERE id = %s
                """, (count + 1, error_message, json.dumps(context or {}), error_id))
                conn.commit()
                return error_id
            else:
                # Insert new error
                cur.execute("""
                    INSERT INTO admin_error_log 
                    (user_id, error_type, error_code, error_message, context, exchange, account_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (user_id, error_type, error_code, error_message, 
                      json.dumps(context or {}), exchange, account_type))
                result = cur.fetchone()
                conn.commit()
                return result[0] if result else None
                
    except Exception as e:
        _logger.error(f"Failed to log admin error: {e}")
        return None


def get_pending_admin_errors(limit: int = 50) -> list[dict]:
    """Get all pending (non-approved) errors for admin review."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    e.id, e.user_id, e.error_type, e.error_code, e.error_message,
                    e.context, e.exchange, e.account_type, e.status,
                    e.occurrence_count, e.first_seen, e.last_seen,
                    u.username, u.first_name
                FROM admin_error_log e
                LEFT JOIN users u ON e.user_id = u.user_id
                WHERE e.status NOT IN ('approved', 'resolved')
                ORDER BY e.last_seen DESC
                LIMIT %s
            """, (limit,))
            
            rows = cur.fetchall()
            errors = []
            for row in rows:
                errors.append({
                    "id": row[0],
                    "user_id": row[1],
                    "error_type": row[2],
                    "error_code": row[3],
                    "error_message": row[4],
                    "context": _safe_json_loads(row[5], {}),
                    "exchange": row[6],
                    "account_type": row[7],
                    "status": row[8],
                    "occurrence_count": row[9],
                    "first_seen": row[10],
                    "last_seen": row[11],
                    "username": row[12],
                    "first_name": row[13],
                })
            return errors
            
    except Exception as e:
        _logger.error(f"Failed to get pending admin errors: {e}")
        return []


def get_admin_errors_by_user(user_id: int, include_approved: bool = False) -> list[dict]:
    """Get errors for a specific user."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            if include_approved:
                cur.execute("""
                    SELECT id, error_type, error_code, error_message, context,
                           exchange, account_type, status, occurrence_count, 
                           first_seen, last_seen, admin_note
                    FROM admin_error_log 
                    WHERE user_id = %s
                    ORDER BY last_seen DESC
                    LIMIT 100
                """, (user_id,))
            else:
                cur.execute("""
                    SELECT id, error_type, error_code, error_message, context,
                           exchange, account_type, status, occurrence_count, 
                           first_seen, last_seen, admin_note
                    FROM admin_error_log 
                    WHERE user_id = %s AND status NOT IN ('approved', 'resolved')
                    ORDER BY last_seen DESC
                    LIMIT 100
                """, (user_id,))
            
            rows = cur.fetchall()
            return [{
                "id": r[0], "error_type": r[1], "error_code": r[2],
                "error_message": r[3], "context": _safe_json_loads(r[4], {}),
                "exchange": r[5], "account_type": r[6], "status": r[7],
                "occurrence_count": r[8], "first_seen": r[9], "last_seen": r[10],
                "admin_note": r[11]
            } for r in rows]
            
    except Exception as e:
        _logger.error(f"Failed to get errors for user {user_id}: {e}")
        return []


def approve_admin_error(error_id: int, admin_note: str = None) -> bool:
    """Approve (silence) an error - it won't be shown again."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE admin_error_log 
                SET status = 'approved', 
                    approved_at = NOW(),
                    admin_note = COALESCE(%s, admin_note)
                WHERE id = %s
            """, (admin_note, error_id))
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        _logger.error(f"Failed to approve error {error_id}: {e}")
        return False


def approve_all_user_errors(user_id: int, error_type: str = None) -> int:
    """Approve all errors for a user (optionally filtered by type)."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            if error_type:
                cur.execute("""
                    UPDATE admin_error_log 
                    SET status = 'approved', approved_at = NOW()
                    WHERE user_id = %s AND error_type = %s 
                      AND status NOT IN ('approved', 'resolved')
                """, (user_id, error_type))
            else:
                cur.execute("""
                    UPDATE admin_error_log 
                    SET status = 'approved', approved_at = NOW()
                    WHERE user_id = %s AND status NOT IN ('approved', 'resolved')
                """, (user_id,))
            conn.commit()
            return cur.rowcount
    except Exception as e:
        _logger.error(f"Failed to approve all errors for user {user_id}: {e}")
        return 0


def mark_error_notified(error_id: int) -> bool:
    """Mark that user was notified about this error."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE admin_error_log 
                SET status = 'notified', notified_at = NOW()
                WHERE id = %s
            """, (error_id,))
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        _logger.error(f"Failed to mark error {error_id} as notified: {e}")
        return False


def get_error_stats() -> dict:
    """Get error statistics for admin dashboard."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            
            # Total pending
            cur.execute("""
                SELECT COUNT(*) FROM admin_error_log 
                WHERE status NOT IN ('approved', 'resolved')
            """)
            pending = cur.fetchone()[0]
            
            # By error type
            cur.execute("""
                SELECT error_type, COUNT(*), SUM(occurrence_count)
                FROM admin_error_log 
                WHERE status NOT IN ('approved', 'resolved')
                GROUP BY error_type
                ORDER BY COUNT(*) DESC
            """)
            by_type = {r[0]: {"count": r[1], "total_occurrences": r[2]} for r in cur.fetchall()}
            
            # By user (top 10)
            cur.execute("""
                SELECT e.user_id, u.username, u.first_name, COUNT(*), SUM(e.occurrence_count)
                FROM admin_error_log e
                LEFT JOIN users u ON e.user_id = u.user_id
                WHERE e.status NOT IN ('approved', 'resolved')
                GROUP BY e.user_id, u.username, u.first_name
                ORDER BY SUM(e.occurrence_count) DESC
                LIMIT 10
            """)
            by_user = [{
                "user_id": r[0], 
                "username": r[1], 
                "first_name": r[2],
                "error_count": r[3], 
                "total_occurrences": r[4]
            } for r in cur.fetchall()]
            
            return {
                "pending": pending,
                "by_type": by_type,
                "top_users": by_user
            }
            
    except Exception as e:
        _logger.error(f"Failed to get error stats: {e}")
        return {"pending": 0, "by_type": {}, "top_users": []}


# ════════════════════════════════════════════════════════════════════════════════════════
# ADMIN: COMPREHENSIVE DASHBOARD & SYSTEM FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════════════════

def get_admin_dashboard() -> dict:
    """Get comprehensive admin dashboard with all statistics."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            
            # === USERS ===
            cur.execute("SELECT COUNT(*) FROM users")
            total_users = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM users WHERE is_allowed = 1 AND is_banned = 0")
            active_users = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM users WHERE current_license = 'premium' OR is_lifetime = 1")
            premium_users = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM users WHERE current_license = 'basic'")
            basic_users = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1")
            banned_users = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM users WHERE exchange_type = 'hyperliquid'")
            hl_users = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURRENT_DATE")
            new_today = cur.fetchone()[0]
            
            # === POSITIONS ===
            cur.execute("SELECT COUNT(*) FROM active_positions")
            total_positions = cur.fetchone()[0]
            
            cur.execute("""
                SELECT exchange, account_type, COUNT(*) 
                FROM active_positions 
                GROUP BY exchange, account_type
            """)
            positions_by_account = {f"{r[0]}:{r[1]}": r[2] for r in cur.fetchall()}
            
            cur.execute("""
                SELECT strategy, COUNT(*) 
                FROM active_positions 
                GROUP BY strategy 
                ORDER BY COUNT(*) DESC
                LIMIT 10
            """)
            positions_by_strategy = {r[0] or "unknown": r[1] for r in cur.fetchall()}
            
            # === TRADES ===
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                    COALESCE(SUM(pnl), 0) as total_pnl,
                    COALESCE(AVG(pnl), 0) as avg_pnl
                FROM trade_logs
            """)
            row = cur.fetchone()
            total_trades = row[0] or 0
            wins = row[1] or 0
            total_pnl = float(row[2] or 0)
            avg_pnl = float(row[3] or 0)
            winrate = round(wins / max(total_trades, 1) * 100, 1)
            
            cur.execute("""
                SELECT COUNT(*), COALESCE(SUM(pnl), 0)
                FROM trade_logs
                WHERE DATE(ts) = CURRENT_DATE
            """)
            row = cur.fetchone()
            today_trades = row[0] or 0
            today_pnl = float(row[1] or 0)
            
            cur.execute("""
                SELECT COUNT(*), COALESCE(SUM(pnl), 0)
                FROM trade_logs
                WHERE ts >= NOW() - INTERVAL '7 days'
            """)
            row = cur.fetchone()
            week_trades = row[0] or 0
            week_pnl = float(row[1] or 0)
            
            # === SIGNALS ===
            cur.execute("SELECT COUNT(*) FROM signals")
            total_signals = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM signals WHERE DATE(open_ts) = CURRENT_DATE")
            today_signals = cur.fetchone()[0]
            
            cur.execute("""
                SELECT strategy, COUNT(*) 
                FROM signals 
                GROUP BY strategy 
                ORDER BY COUNT(*) DESC
                LIMIT 5
            """)
            signals_by_strategy = {r[0] or "unknown": r[1] for r in cur.fetchall()}
            
            # === PAYMENTS ===
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                    COALESCE(SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END), 0) as revenue
                FROM payment_history
            """)
            row = cur.fetchone()
            payments = {
                "total": row[0] or 0,
                "completed": row[1] or 0,
                "pending": row[2] or 0,
                "revenue": float(row[3] or 0)
            }
            
            # === ERRORS ===
            cur.execute("""
                SELECT COUNT(*) FROM admin_error_log 
                WHERE status NOT IN ('approved', 'resolved')
            """)
            pending_errors = cur.fetchone()[0]
            
            cur.execute("""
                SELECT COUNT(*) FROM admin_error_log 
                WHERE last_seen >= NOW() - INTERVAL '1 hour'
            """)
            errors_last_hour = cur.fetchone()[0]
            
            return {
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "premium": premium_users,
                    "basic": basic_users,
                    "banned": banned_users,
                    "hyperliquid": hl_users,
                    "new_today": new_today
                },
                "positions": {
                    "total": total_positions,
                    "by_account": positions_by_account,
                    "by_strategy": positions_by_strategy
                },
                "trades": {
                    "total": total_trades,
                    "wins": wins,
                    "winrate": winrate,
                    "total_pnl": total_pnl,
                    "avg_pnl": avg_pnl,
                    "today": today_trades,
                    "today_pnl": today_pnl,
                    "week": week_trades,
                    "week_pnl": week_pnl
                },
                "signals": {
                    "total": total_signals,
                    "today": today_signals,
                    "by_strategy": signals_by_strategy
                },
                "payments": payments,
                "errors": {
                    "pending": pending_errors,
                    "last_hour": errors_last_hour
                }
            }
    except Exception as e:
        _logger.error(f"Failed to get admin dashboard: {e}")
        return {}


def get_all_positions_admin(
    exchange: str = None,
    account_type: str = None,
    strategy: str = None,
    limit: int = 100,
    offset: int = 0
) -> tuple[list, int]:
    """Get all positions across all users for admin view."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            
            # Build WHERE clause
            conditions = []
            params = []
            
            if exchange:
                conditions.append("p.exchange = %s")
                params.append(exchange)
            if account_type:
                conditions.append("p.account_type = %s")
                params.append(account_type)
            if strategy:
                conditions.append("p.strategy = %s")
                params.append(strategy)
            
            where = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            # Count total
            cur.execute(f"SELECT COUNT(*) FROM active_positions p {where}", params)
            total = cur.fetchone()[0]
            
            # Get positions with user info
            cur.execute(f"""
                SELECT 
                    p.user_id, p.symbol, p.side, p.entry_price, p.size,
                    p.leverage, p.sl_price, p.tp_price, p.strategy,
                    p.exchange, p.account_type, p.open_ts,
                    u.username, u.first_name
                FROM active_positions p
                LEFT JOIN users u ON p.user_id = u.user_id
                {where}
                ORDER BY p.open_ts DESC
                LIMIT %s OFFSET %s
            """, params + [limit, offset])
            
            positions = []
            for row in cur.fetchall():
                positions.append({
                    "user_id": row[0],
                    "symbol": row[1],
                    "side": row[2],
                    "entry_price": float(row[3]) if row[3] else 0,
                    "size": float(row[4]) if row[4] else 0,
                    "leverage": row[5],
                    "sl_price": float(row[6]) if row[6] else None,
                    "tp_price": float(row[7]) if row[7] else None,
                    "strategy": row[8],
                    "exchange": row[9] or "bybit",
                    "account_type": row[10] or "demo",
                    "open_ts": str(row[11]) if row[11] else None,
                    "username": row[12],
                    "first_name": row[13]
                })
            
            return positions, total
            
    except Exception as e:
        _logger.error(f"Failed to get all positions: {e}")
        return [], 0


def get_all_trades_admin(
    exchange: str = None,
    account_type: str = None,
    strategy: str = None,
    pnl_filter: str = None,  # 'win', 'loss'
    limit: int = 100,
    offset: int = 0
) -> tuple[list, int]:
    """Get all trades across all users for admin view."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            
            # Build WHERE clause
            conditions = []
            params = []
            
            if exchange:
                conditions.append("t.exchange = %s")
                params.append(exchange)
            if account_type:
                conditions.append("t.account_type = %s")
                params.append(account_type)
            if strategy:
                conditions.append("t.strategy = %s")
                params.append(strategy)
            if pnl_filter == 'win':
                conditions.append("t.pnl > 0")
            elif pnl_filter == 'loss':
                conditions.append("t.pnl < 0")
            
            where = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            # Count total
            cur.execute(f"SELECT COUNT(*) FROM trade_logs t {where}", params)
            total = cur.fetchone()[0]
            
            # Get trades with user info
            cur.execute(f"""
                SELECT 
                    t.id, t.user_id, t.symbol, t.side, t.entry_price, t.exit_price,
                    t.pnl, t.pnl_pct, t.exit_reason, t.strategy,
                    t.exchange, t.account_type, t.ts,
                    u.username, u.first_name
                FROM trade_logs t
                LEFT JOIN users u ON t.user_id = u.user_id
                {where}
                ORDER BY t.ts DESC
                LIMIT %s OFFSET %s
            """, params + [limit, offset])
            
            trades = []
            for row in cur.fetchall():
                trades.append({
                    "id": row[0],
                    "user_id": row[1],
                    "symbol": row[2],
                    "side": row[3],
                    "entry_price": float(row[4]) if row[4] else 0,
                    "exit_price": float(row[5]) if row[5] else 0,
                    "pnl": float(row[6]) if row[6] else 0,
                    "pnl_pct": float(row[7]) if row[7] else 0,
                    "exit_reason": row[8],
                    "strategy": row[9],
                    "exchange": row[10] or "bybit",
                    "account_type": row[11] or "demo",
                    "ts": str(row[12]) if row[12] else None,
                    "username": row[13],
                    "first_name": row[14]
                })
            
            return trades, total
            
    except Exception as e:
        _logger.error(f"Failed to get all trades: {e}")
        return [], 0


def get_all_signals_admin(
    strategy: str = None,
    symbol: str = None,
    side: str = None,
    limit: int = 100,
    offset: int = 0
) -> tuple[list, int]:
    """Get all signals for admin view."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            
            # Build WHERE clause
            conditions = []
            params = []
            
            if strategy:
                conditions.append("strategy = %s")
                params.append(strategy)
            if symbol:
                conditions.append("symbol ILIKE %s")
                params.append(f"%{symbol}%")
            if side:
                conditions.append("side = %s")
                params.append(side)
            
            where = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            # Count total
            cur.execute(f"SELECT COUNT(*) FROM signals {where}", params)
            total = cur.fetchone()[0]
            
            # Get signals
            cur.execute(f"""
                SELECT 
                    id, symbol, side, strategy, entry_price, sl_price, tp_price,
                    timeframe, open_ts, exchange
                FROM signals
                {where}
                ORDER BY open_ts DESC
                LIMIT %s OFFSET %s
            """, params + [limit, offset])
            
            signals = []
            for row in cur.fetchall():
                signals.append({
                    "id": row[0],
                    "symbol": row[1],
                    "side": row[2],
                    "strategy": row[3],
                    "entry_price": float(row[4]) if row[4] else 0,
                    "sl_price": float(row[5]) if row[5] else None,
                    "tp_price": float(row[6]) if row[6] else None,
                    "timeframe": row[7],
                    "open_ts": str(row[8]) if row[8] else None,
                    "exchange": row[9] or "bybit"
                })
            
            return signals, total
            
    except Exception as e:
        _logger.error(f"Failed to get all signals: {e}")
        return [], 0


def delete_signal_admin(signal_id: int) -> bool:
    """Delete a signal by ID."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM signals WHERE id = %s", (signal_id,))
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        _logger.error(f"Failed to delete signal {signal_id}: {e}")
        return False


def get_system_health() -> dict:
    """Get system health metrics."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            
            # Database status
            cur.execute("SELECT 1")
            db_healthy = cur.fetchone() is not None
            
            # Connection pool stats
            pool = get_pool()
            pool_stats = {
                "min_conn": pool.minconn if pool else 0,
                "max_conn": pool.maxconn if pool else 0
            }
            
            # Recent activity
            cur.execute("""
                SELECT COUNT(*) FROM trade_logs 
                WHERE ts >= NOW() - INTERVAL '1 hour'
            """)
            trades_last_hour = cur.fetchone()[0]
            
            cur.execute("""
                SELECT COUNT(*) FROM signals 
                WHERE open_ts >= NOW() - INTERVAL '1 hour'
            """)
            signals_last_hour = cur.fetchone()[0]
            
            cur.execute("""
                SELECT COUNT(*) FROM admin_error_log 
                WHERE last_seen >= NOW() - INTERVAL '1 hour'
            """)
            errors_last_hour = cur.fetchone()[0]
            
            # Users online (based on recent activity - simplified)
            cur.execute("""
                SELECT COUNT(DISTINCT user_id) FROM trade_logs 
                WHERE ts >= NOW() - INTERVAL '24 hours'
            """)
            active_users_24h = cur.fetchone()[0]
            
            return {
                "status": "healthy" if db_healthy else "unhealthy",
                "database": {
                    "connected": db_healthy,
                    "pool": pool_stats
                },
                "activity": {
                    "trades_last_hour": trades_last_hour,
                    "signals_last_hour": signals_last_hour,
                    "errors_last_hour": errors_last_hour,
                    "active_users_24h": active_users_24h
                },
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    except Exception as e:
        _logger.error(f"Failed to get system health: {e}")
        return {"status": "error", "error": str(e)}


def pause_user_trading(user_id: int) -> bool:
    """Pause trading for a specific user."""
    try:
        pg_set_user_field(user_id, "trading_paused", 1)
        invalidate_user_cache(user_id)
        return True
    except Exception as e:
        _logger.error(f"Failed to pause user {user_id}: {e}")
        return False


def resume_user_trading(user_id: int) -> bool:
    """Resume trading for a specific user."""
    try:
        pg_set_user_field(user_id, "trading_paused", 0)
        invalidate_user_cache(user_id)
        return True
    except Exception as e:
        _logger.error(f"Failed to resume user {user_id}: {e}")
        return False


def add_broadcast_message(message: str, target: str = "all", admin_id: int = None) -> int:
    """Add a broadcast message to queue."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO notification_queue 
                (target_type, message, created_by, status, created_at)
                VALUES (%s, %s, %s, 'pending', NOW())
                RETURNING id
            """, (target, message, admin_id))
            result = cur.fetchone()
            conn.commit()
            return result[0] if result else 0
    except Exception as e:
        _logger.error(f"Failed to add broadcast: {e}")
        return 0


def get_pending_broadcasts() -> list:
    """Get pending broadcast messages."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, target_type, message, created_at
                FROM notification_queue
                WHERE status = 'pending'
                ORDER BY created_at DESC
                LIMIT 50
            """)
            return [{
                "id": r[0],
                "target": r[1],
                "message": r[2],
                "created_at": str(r[3]) if r[3] else None
            } for r in cur.fetchall()]
    except Exception as e:
        _logger.error(f"Failed to get pending broadcasts: {e}")
        return []


def mark_broadcast_sent(broadcast_id: int, sent_count: int = 0) -> bool:
    """Mark broadcast as sent."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE notification_queue 
                SET status = 'sent', sent_count = %s, sent_at = NOW()
                WHERE id = %s
            """, (sent_count, broadcast_id))
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        _logger.error(f"Failed to mark broadcast sent: {e}")
        return False

