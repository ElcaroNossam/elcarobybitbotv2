# © 2025 Illia Teslenko. All rights reserved. Proprietary license. Unauthorized use prohibited.
from __future__ import annotations

import json
import sqlite3
import time
import threading
from pathlib import Path
from typing import Any
from queue import Queue

from coin_params import DEFAULT_TP_PCT, DEFAULT_SL_PCT, DEFAULT_LANG

DB_FILE = Path("bot.db")

# ------------------------------------------------------------------------------------
# Connection Pool for multi-user optimization
# ------------------------------------------------------------------------------------
_pool: Queue = Queue(maxsize=10)
_pool_lock = threading.Lock()

def _create_connection() -> sqlite3.Connection:
    """Create a new connection with optimal settings."""
    conn = sqlite3.connect(DB_FILE, timeout=30.0, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
    conn.execute("PRAGMA mmap_size=268435456")  # 256MB mmap
    return conn

# ------------------------------------------------------------------------------------
# In-memory caches for frequently accessed data
# ------------------------------------------------------------------------------------
_user_config_cache: dict[int, tuple[float, dict]] = {}  # user_id -> (timestamp, config)
_all_users_cache: tuple[float, list[int]] = (0.0, [])  # (timestamp, user_ids)
_active_users_cache: tuple[float, list[int]] = (0.0, [])  # users with API keys
CACHE_TTL = 30.0  # seconds

def invalidate_user_cache(user_id: int = None):
    """Invalidate cache for a user or all users."""
    global _all_users_cache, _active_users_cache
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
    # ATR settings (global)
    "atr_trigger_pct",   # % profit to activate ATR trailing (default 1.0)
    "atr_step_pct",      # min % move to trail SL (default 0.5)
    "atr_period",        # candles for ATR calculation (default 14)
    "atr_multiplier",    # ATR multiplier for SL distance (default 1.5)
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
    "is_allowed", "is_banned", "terms_accepted",
    "guide_sent",  # 0/1 - отправлен ли PDF гайд
    # License info (добавлено для admin API)
    "license_type", "license_expires", "current_license",
    # для совместимости с текущим кодом бота
    "first_seen_ts", "last_seen_ts",
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
}

# ------------------------------------------------------------------------------------
# База / подключение с Connection Pool
# ------------------------------------------------------------------------------------
def get_conn() -> sqlite3.Connection:
    """
    Получает соединение из пула или создаёт новое.
    Оптимизировано для многопользовательской работы.
    """
    try:
        conn = _pool.get_nowait()
        # Проверяем, что соединение живое
        try:
            conn.execute("SELECT 1")
            return conn
        except:
            pass  # Соединение мёртвое, создаём новое
    except:
        pass  # Пул пустой
    return _create_connection()

def release_conn(conn: sqlite3.Connection):
    """Возвращает соединение в пул для переиспользования."""
    try:
        _pool.put_nowait(conn)
    except:
        # Пул полный - закрываем соединение
        try:
            conn.close()
        except:
            pass


def _col_exists(conn: sqlite3.Connection, table: str, col: str) -> bool:
    """Check if column exists in table - SAFE from SQL injection"""
    # Security: Validate table and column names against whitelists
    if table not in {'users', 'signals', 'active_positions', 'pending_limit_orders',
                      'trade_logs', 'user_licenses', 'promo_codes', 'custom_strategies',
                      'market_snapshots', 'payment_history', 'user_achievements',
                      'user_strategy_settings', 'exchange_accounts', 'strategy_ratings',
                      'strategy_marketplace', 'strategy_purchases', 'seller_payouts',
                      'top_strategies', 'elc_purchases', 'elc_transactions', 'elc_stats'}:
        raise ValueError(f"Invalid table name: {table}")
    
    if not col.replace('_', '').isalnum():
        raise ValueError(f"Invalid column name: {col}")
    
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == col for r in rows)


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return bool(row)

# ------------------------------------------------------------------------------------
# Schema & Migrations
# ------------------------------------------------------------------------------------
def init_db():
    with get_conn() as conn:
        cur = conn.cursor()

        # USERS — дефолты выровнены под логику бота (limit/rsi/oi/atr включены)
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS users (
            user_id            INTEGER PRIMARY KEY,
            api_key            TEXT,
            api_secret         TEXT,

            -- Demo/Real API keys
            demo_api_key       TEXT,
            demo_api_secret    TEXT,
            real_api_key       TEXT,
            real_api_secret    TEXT,
            trading_mode       TEXT NOT NULL DEFAULT 'demo',  -- 'demo', 'real', 'both'

            -- торговые настройки
            percent            REAL    NOT NULL DEFAULT 1.0,
            coins              TEXT    NOT NULL DEFAULT 'ALL',
            limit_enabled      INTEGER NOT NULL DEFAULT 1,
            trade_oi           INTEGER NOT NULL DEFAULT 1,
            trade_rsi_bb       INTEGER NOT NULL DEFAULT 1,
            tp_percent         REAL    NOT NULL DEFAULT 8.0,
            sl_percent         REAL    NOT NULL DEFAULT 3.0,
            use_atr            INTEGER NOT NULL DEFAULT 1,   -- 1=ATR, 0=fixed
            lang               TEXT    NOT NULL DEFAULT 'en',

            -- стратегии/пороги (опц.)
            strategies_enabled TEXT,
            strategies_order   TEXT,
            rsi_lo             REAL,
            rsi_hi             REAL,
            bb_touch_k         REAL,
            oi_min_pct         REAL,
            price_min_pct      REAL,
            limit_only_default INTEGER,

            -- новая стратегия
            trade_scryptomera  INTEGER NOT NULL DEFAULT 0,
            trade_scalper      INTEGER NOT NULL DEFAULT 0,
            trade_elcaro       INTEGER NOT NULL DEFAULT 0,
            trade_fibonacci    INTEGER NOT NULL DEFAULT 0,

            -- настройки по стратегиям (JSON: {"oi": {"percent": 1, "sl": 3, "tp": 8}, ...})
            strategy_settings  TEXT,
            -- DCA настройки для доборов (фьючерсы)
            dca_enabled        INTEGER NOT NULL DEFAULT 0,   -- 0=выключено, 1=включено
            dca_pct_1          REAL    NOT NULL DEFAULT 10.0,
            dca_pct_2          REAL    NOT NULL DEFAULT 25.0,

            -- доступ/модерация/согласие
            is_allowed         INTEGER NOT NULL DEFAULT 0,   -- 1=одобрен админом
            is_banned          INTEGER NOT NULL DEFAULT 0,   -- 1=бан
            terms_accepted     INTEGER NOT NULL DEFAULT 0,   -- 1=принял правила
            guide_sent         INTEGER NOT NULL DEFAULT 0,   -- 1=отправлен PDF гайд

            -- совместимость с текущим кодом
            first_seen_ts      INTEGER,
            last_seen_ts       INTEGER
        )
        """
        )

        # Индексы для админ-листинга/фильтра/сортировки
        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_flags ON users(is_banned, is_allowed)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_last_seen ON users(last_seen_ts DESC)")

        # Мягкие миграции на случай старой БД
        for col, ddl in [
            ("strategies_enabled", "ALTER TABLE users ADD COLUMN strategies_enabled TEXT"),
            ("strategies_order",   "ALTER TABLE users ADD COLUMN strategies_order   TEXT"),
            ("rsi_lo",             "ALTER TABLE users ADD COLUMN rsi_lo REAL"),
            ("rsi_hi",             "ALTER TABLE users ADD COLUMN rsi_hi REAL"),
            ("bb_touch_k",         "ALTER TABLE users ADD COLUMN bb_touch_k REAL"),
            ("oi_min_pct",         "ALTER TABLE users ADD COLUMN oi_min_pct REAL"),
            ("price_min_pct",      "ALTER TABLE users ADD COLUMN price_min_pct REAL"),
            ("limit_only_default", "ALTER TABLE users ADD COLUMN limit_only_default INTEGER"),
            ("trade_scryptomera",  "ALTER TABLE users ADD COLUMN trade_scryptomera  INTEGER NOT NULL DEFAULT 0"),
            ("trade_scalper",      "ALTER TABLE users ADD COLUMN trade_scalper      INTEGER NOT NULL DEFAULT 0"),
            ("trade_elcaro",       "ALTER TABLE users ADD COLUMN trade_elcaro       INTEGER NOT NULL DEFAULT 0"),
            ("trade_fibonacci",    "ALTER TABLE users ADD COLUMN trade_fibonacci    INTEGER NOT NULL DEFAULT 0"),
            ("strategy_settings",  "ALTER TABLE users ADD COLUMN strategy_settings  TEXT"),
            ("dca_enabled",        "ALTER TABLE users ADD COLUMN dca_enabled        INTEGER NOT NULL DEFAULT 0"),
            ("dca_pct_1",          "ALTER TABLE users ADD COLUMN dca_pct_1          REAL NOT NULL DEFAULT 10.0"),
            ("dca_pct_2",          "ALTER TABLE users ADD COLUMN dca_pct_2          REAL NOT NULL DEFAULT 25.0"),
            ("is_allowed",         "ALTER TABLE users ADD COLUMN is_allowed         INTEGER NOT NULL DEFAULT 0"),
            ("is_banned",          "ALTER TABLE users ADD COLUMN is_banned          INTEGER NOT NULL DEFAULT 0"),
            ("terms_accepted",     "ALTER TABLE users ADD COLUMN terms_accepted     INTEGER NOT NULL DEFAULT 0"),
            ("first_seen_ts",      "ALTER TABLE users ADD COLUMN first_seen_ts      INTEGER"),
            ("last_seen_ts",       "ALTER TABLE users ADD COLUMN last_seen_ts       INTEGER"),
            # Demo/Real API keys migration
            ("demo_api_key",       "ALTER TABLE users ADD COLUMN demo_api_key       TEXT"),
            ("demo_api_secret",    "ALTER TABLE users ADD COLUMN demo_api_secret    TEXT"),
            ("real_api_key",       "ALTER TABLE users ADD COLUMN real_api_key       TEXT"),
            ("real_api_secret",    "ALTER TABLE users ADD COLUMN real_api_secret    TEXT"),
            ("trading_mode",       "ALTER TABLE users ADD COLUMN trading_mode       TEXT NOT NULL DEFAULT 'demo'"),
            # Global leverage
            ("leverage",           "ALTER TABLE users ADD COLUMN leverage           INTEGER NOT NULL DEFAULT 10"),
            # Spot trading
            ("spot_enabled",       "ALTER TABLE users ADD COLUMN spot_enabled       INTEGER NOT NULL DEFAULT 0"),
            ("spot_settings",      "ALTER TABLE users ADD COLUMN spot_settings      TEXT"),
            # Guide sent flag
            ("guide_sent",         "ALTER TABLE users ADD COLUMN guide_sent         INTEGER NOT NULL DEFAULT 0"),
            # Limit ladder settings (for DCA entries)
            ("limit_ladder_enabled",  "ALTER TABLE users ADD COLUMN limit_ladder_enabled  INTEGER NOT NULL DEFAULT 0"),
            ("limit_ladder_count",    "ALTER TABLE users ADD COLUMN limit_ladder_count    INTEGER NOT NULL DEFAULT 3"),
            ("limit_ladder_settings", "ALTER TABLE users ADD COLUMN limit_ladder_settings TEXT"),
            # Global order type (market/limit) 
            ("global_order_type",  "ALTER TABLE users ADD COLUMN global_order_type  TEXT NOT NULL DEFAULT 'market'"),
            # HyperLiquid DEX columns
            ("hl_private_key",     "ALTER TABLE users ADD COLUMN hl_private_key     TEXT"),
            ("hl_wallet_address",  "ALTER TABLE users ADD COLUMN hl_wallet_address  TEXT"),
            ("hl_vault_address",   "ALTER TABLE users ADD COLUMN hl_vault_address   TEXT"),
            ("hl_testnet",         "ALTER TABLE users ADD COLUMN hl_testnet         INTEGER NOT NULL DEFAULT 0"),
            ("hl_enabled",         "ALTER TABLE users ADD COLUMN hl_enabled         INTEGER NOT NULL DEFAULT 0"),
            # Separate HL testnet/mainnet credentials
            ("hl_testnet_private_key",     "ALTER TABLE users ADD COLUMN hl_testnet_private_key     TEXT"),
            ("hl_testnet_wallet_address",  "ALTER TABLE users ADD COLUMN hl_testnet_wallet_address  TEXT"),
            ("hl_mainnet_private_key",     "ALTER TABLE users ADD COLUMN hl_mainnet_private_key     TEXT"),
            ("hl_mainnet_wallet_address",  "ALTER TABLE users ADD COLUMN hl_mainnet_wallet_address  TEXT"),
            ("exchange_mode",      "ALTER TABLE users ADD COLUMN exchange_mode      TEXT NOT NULL DEFAULT 'bybit'"),
            ("exchange_type",      "ALTER TABLE users ADD COLUMN exchange_type      TEXT NOT NULL DEFAULT 'bybit'"),
            # ELCARO Token balances
            ("elc_balance",        "ALTER TABLE users ADD COLUMN elc_balance        REAL NOT NULL DEFAULT 0.0"),
            ("elc_staked",         "ALTER TABLE users ADD COLUMN elc_staked         REAL NOT NULL DEFAULT 0.0"),
            ("elc_locked",         "ALTER TABLE users ADD COLUMN elc_locked         REAL NOT NULL DEFAULT 0.0"),
            # User info for webapp login
            ("username",           "ALTER TABLE users ADD COLUMN username           TEXT"),
            ("first_name",         "ALTER TABLE users ADD COLUMN first_name         TEXT"),
        ]:
            if not _col_exists(conn, "users", col):
                cur.execute(ddl)
        
        # Migrate old api_key/api_secret to demo_api_key/demo_api_secret if not migrated
        cur.execute("""
            UPDATE users 
            SET demo_api_key = api_key, demo_api_secret = api_secret
            WHERE api_key IS NOT NULL AND demo_api_key IS NULL
        """)

        # Доп. выравнивание NULL → дефолтов
        cur.execute("UPDATE users SET trade_oi=1        WHERE trade_oi IS NULL")
        cur.execute("UPDATE users SET use_atr=1         WHERE use_atr IS NULL")
        cur.execute("UPDATE users SET trade_rsi_bb=1    WHERE trade_rsi_bb IS NULL")
        cur.execute("UPDATE users SET limit_enabled=1   WHERE limit_enabled IS NULL")
        cur.execute("UPDATE users SET is_allowed=0      WHERE is_allowed IS NULL")
        cur.execute("UPDATE users SET is_banned=0       WHERE is_banned  IS NULL")
        cur.execute("UPDATE users SET terms_accepted=0  WHERE terms_accepted IS NULL")

        # MARKET SNAPSHOTS
        if _table_exists(conn, "market_snapshots") and not _col_exists(
            conn, "market_snapshots", "id"
        ):
            cur.execute("ALTER TABLE market_snapshots RENAME TO market_snapshots__old")

        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS market_snapshots (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ts          INTEGER NOT NULL,       -- unix ms
            btc_dom     REAL,
            btc_price   REAL,
            btc_change  REAL,
            alt_signal  TEXT CHECK(alt_signal IN ('LONG','SHORT','NEUTRAL'))
        )
        """
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_ms_ts ON market_snapshots(ts DESC)"
        )

        if _table_exists(conn, "market_snapshots__old"):
            cur.execute(
                """
                INSERT INTO market_snapshots (ts, btc_dom, btc_price, btc_change, alt_signal)
                SELECT CAST(strftime('%s', ts) AS INTEGER)*1000, btc_dom, btc_price, btc_change, alt_signal
                  FROM market_snapshots__old
            """
            )
            cur.execute("DROP TABLE market_snapshots__old")

        # NEWS
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS news (
            link        TEXT PRIMARY KEY,
            title       TEXT,
            description TEXT,
            image_url   TEXT,
            ts          DATETIME DEFAULT (CURRENT_TIMESTAMP),
            signal      TEXT,
            sentiment   TEXT
        )
        """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_news_ts ON news(ts DESC)")

        # PYRAMIDS
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS pyramids (
            user_id   INTEGER NOT NULL,
            symbol    TEXT    NOT NULL,
            side      TEXT,
            count     INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY(user_id, symbol),
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pyramids_user ON pyramids(user_id)")

        # USER STRATEGY SETTINGS - per-user, per-strategy, per-exchange, per-account settings
        # Replaces JSON-based strategy_settings field
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS user_strategy_settings (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            strategy        TEXT NOT NULL,  -- oi, rsi_bb, scryptomera, scalper, elcaro, fibonacci, manual
            exchange        TEXT NOT NULL DEFAULT 'bybit',  -- bybit, hyperliquid
            account_type    TEXT NOT NULL DEFAULT 'demo',   -- demo, real, testnet, mainnet
            
            -- Trading parameters
            enabled         INTEGER DEFAULT 1,
            percent         REAL,  -- Position size % of balance
            sl_percent      REAL,  -- Stop loss %
            tp_percent      REAL,  -- Take profit %
            leverage        INTEGER,  -- 1-100 or NULL for default
            
            -- ATR parameters
            use_atr         INTEGER,  -- 0=Fixed SL/TP, 1=ATR Trailing, NULL=use global
            atr_periods     INTEGER,
            atr_multiplier_sl REAL,
            atr_trigger_pct REAL,
            
            -- Order settings
            order_type      TEXT DEFAULT 'market',  -- market, limit
            coins_group     TEXT,  -- ALL, TOP100, VOLATILE, or NULL for global
            direction       TEXT DEFAULT 'all',  -- all, long, short
            
            -- Side-specific settings (for scryptomera/scalper)
            long_percent    REAL,
            long_sl_percent REAL,
            long_tp_percent REAL,
            long_atr_periods INTEGER,
            long_atr_multiplier_sl REAL,
            long_atr_trigger_pct REAL,
            
            short_percent   REAL,
            short_sl_percent REAL,
            short_tp_percent REAL,
            short_atr_periods INTEGER,
            short_atr_multiplier_sl REAL,
            short_atr_trigger_pct REAL,
            
            -- Fibonacci-specific
            min_quality     INTEGER DEFAULT 50,
            
            -- Trading mode (per-strategy setting for this exchange/account)
            trading_mode    TEXT DEFAULT 'global',  -- global, demo, real, both, testnet, mainnet
            
            -- Timestamps
            created_at      DATETIME DEFAULT (CURRENT_TIMESTAMP),
            updated_at      DATETIME DEFAULT (CURRENT_TIMESTAMP),
            
            UNIQUE(user_id, strategy, exchange, account_type),
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_uss_user ON user_strategy_settings(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_uss_strategy ON user_strategy_settings(strategy)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_uss_user_strategy ON user_strategy_settings(user_id, strategy)")
        
        # Migration: add trading_mode column if not exists
        if _table_exists(conn, "user_strategy_settings") and not _col_exists(conn, "user_strategy_settings", "trading_mode"):
            cur.execute("ALTER TABLE user_strategy_settings ADD COLUMN trading_mode TEXT DEFAULT 'global'")

        # ELC PURCHASES - track USDT → ELC purchases on TON
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS elc_purchases (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            payment_id      TEXT UNIQUE NOT NULL,
            usdt_amount     REAL NOT NULL,
            elc_amount      REAL NOT NULL,
            platform_fee    REAL NOT NULL,
            status          TEXT NOT NULL DEFAULT 'pending',  -- pending, completed, failed
            payment_method  TEXT NOT NULL,  -- ton_usdt, direct_wallet
            tx_hash         TEXT,
            created_at      DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
            completed_at    DATETIME,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_elc_purchases_user ON elc_purchases(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_elc_purchases_status ON elc_purchases(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_elc_purchases_created ON elc_purchases(created_at DESC)")

        # ELC TRANSACTIONS - track all ELC balance changes
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS elc_transactions (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id           INTEGER NOT NULL,
            transaction_type  TEXT NOT NULL,  -- purchase, subscription, marketplace, burn, stake, unstake, withdraw
            amount            REAL NOT NULL,  -- negative for spending, positive for receiving
            balance_after     REAL NOT NULL,
            description       TEXT,
            metadata          TEXT,  -- JSON for additional data
            created_at        DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_elc_txs_user ON elc_transactions(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_elc_txs_type ON elc_transactions(transaction_type)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_elc_txs_created ON elc_transactions(created_at DESC)")

        # ELC STATS - global token statistics
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS elc_stats (
            id                  INTEGER PRIMARY KEY DEFAULT 1,
            total_burned        REAL NOT NULL DEFAULT 0.0,
            total_staked        REAL NOT NULL DEFAULT 0.0,
            circulating_supply  REAL NOT NULL DEFAULT 1000000000.0,  -- 1 billion initial
            total_purchases     REAL NOT NULL DEFAULT 0.0,
            total_subscriptions REAL NOT NULL DEFAULT 0.0,
            last_burn_at        DATETIME,
            last_update         DATETIME DEFAULT (CURRENT_TIMESTAMP)
        )
        """
        )
        # Insert initial row if not exists
        cur.execute("""
            INSERT OR IGNORE INTO elc_stats (id, total_burned, total_staked, circulating_supply) 
            VALUES (1, 0.0, 0.0, 1000000000.0)
        """)

        # CONNECTED WALLETS - for cold wallet trading (MetaMask, WalletConnect)
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS connected_wallets (
            user_id         INTEGER PRIMARY KEY,
            wallet_address  TEXT NOT NULL,
            wallet_type     TEXT NOT NULL,  -- metamask, walletconnect, tonkeeper
            chain           TEXT NOT NULL DEFAULT 'ethereum',  -- ethereum, ton, polygon, bsc
            connected_at    DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
            last_used_at    DATETIME,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_connected_wallets_address ON connected_wallets(wallet_address)")

        # META (k/v)
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS meta (
            key   TEXT PRIMARY KEY,
            value TEXT
        )
        """
        )

        # BTC DOM (исторический лог)
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS btc_dom (
            ts   INTEGER PRIMARY KEY,
            dom  REAL
        )
        """
        )

        # SIGNALS
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS signals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_message TEXT,
            ts          DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
            tf          TEXT,
            side        TEXT,
            symbol      TEXT,
            price       REAL,
            oi_prev     REAL,
            oi_now      REAL,
            oi_chg      REAL,
            vol_from    REAL,
            vol_to      REAL,
            price_chg   REAL,
            vol_delta   REAL,
            rsi         REAL,
            bb_hi       REAL,
            bb_lo       REAL
        )
        """
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_signals_symbol_ts ON signals(symbol, ts DESC)"
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_signals_tf_ts     ON signals(tf, ts DESC)"
        )

        # ACTIVE POSITIONS
        # Проверяем нужна ли миграция PRIMARY KEY (добавление account_type в PK)
        needs_pk_migration = False
        if _table_exists(conn, "active_positions"):
            # Проверяем текущий PRIMARY KEY - если account_type нет в PK, нужна миграция
            pk_info = cur.execute("PRAGMA table_info(active_positions)").fetchall()
            pk_cols = [col[1] for col in pk_info if col[5] > 0]  # col[5] = pk flag
            if "account_type" not in pk_cols:
                needs_pk_migration = True
        
        if needs_pk_migration:
            # Миграция: пересоздаём таблицу с новым PRIMARY KEY (user_id, symbol, account_type)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS active_positions_new (
                    user_id      INTEGER NOT NULL,
                    symbol       TEXT    NOT NULL,
                    account_type TEXT    NOT NULL DEFAULT 'demo',
                    side         TEXT,
                    entry_price  REAL,
                    size         REAL,
                    open_ts      DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
                    timeframe    TEXT,
                    signal_id    INTEGER,
                    dca_10_done  INTEGER NOT NULL DEFAULT 0,
                    dca_25_done  INTEGER NOT NULL DEFAULT 0,
                    strategy     TEXT,
                    PRIMARY KEY(user_id, symbol, account_type),
                    FOREIGN KEY(user_id)  REFERENCES users(user_id)   ON DELETE CASCADE,
                    FOREIGN KEY(signal_id) REFERENCES signals(id)     ON DELETE SET NULL
                )
            """)
            # Копируем данные из старой таблицы
            cur.execute("""
                INSERT OR IGNORE INTO active_positions_new 
                    (user_id, symbol, account_type, side, entry_price, size, open_ts, timeframe, signal_id, dca_10_done, dca_25_done, strategy)
                SELECT 
                    user_id, symbol, COALESCE(account_type, 'demo'), side, entry_price, size, open_ts, timeframe, signal_id,
                    COALESCE(dca_10_done, 0), COALESCE(dca_25_done, 0), strategy
                FROM active_positions
            """)
            cur.execute("DROP TABLE active_positions")
            cur.execute("ALTER TABLE active_positions_new RENAME TO active_positions")
        else:
            # Создание новой таблицы с правильным PRIMARY KEY
            cur.execute(
                """
            CREATE TABLE IF NOT EXISTS active_positions (
                user_id      INTEGER NOT NULL,
                symbol       TEXT    NOT NULL,
                account_type TEXT    NOT NULL DEFAULT 'demo',
                side         TEXT,
                entry_price  REAL,
                size         REAL,
                open_ts      DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
                timeframe    TEXT,
                signal_id    INTEGER,
                dca_10_done  INTEGER NOT NULL DEFAULT 0,
                dca_25_done  INTEGER NOT NULL DEFAULT 0,
                strategy     TEXT,
                PRIMARY KEY(user_id, symbol, account_type),
                FOREIGN KEY(user_id)  REFERENCES users(user_id)   ON DELETE CASCADE,
                FOREIGN KEY(signal_id) REFERENCES signals(id)     ON DELETE SET NULL
            )
            """
            )
        
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_active_user ON active_positions(user_id)"
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_active_sig  ON active_positions(signal_id)"
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_active_account ON active_positions(user_id, account_type)"
        )

        # TRADE LOGS
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS trade_logs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            signal_id       INTEGER,
            symbol          TEXT,
            side            TEXT,
            entry_price     REAL,
            exit_price      REAL,
            exit_reason     TEXT,
            pnl             REAL,
            pnl_pct         REAL,
            ts              DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
            signal_source   TEXT,
            rsi             REAL,
            bb_hi           REAL,
            bb_lo           REAL,
            oi_prev         REAL,
            oi_now          REAL,
            oi_chg          REAL,
            vol_from        REAL,
            vol_to          REAL,
            price_chg       REAL,
            vol_delta       REAL,
            sl_pct          REAL,
            tp_pct          REAL,
            sl_price        REAL,
            tp_price        REAL,
            timeframe       TEXT,
            entry_ts        INTEGER,
            exit_ts         INTEGER,
            exit_order_type TEXT,
            FOREIGN KEY(user_id)   REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY(signal_id) REFERENCES signals(id)    ON DELETE SET NULL
        )
        """
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_logs_user_ts   ON trade_logs(user_id, ts DESC)"
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_logs_symbol_ts ON trade_logs(symbol, ts DESC)"
        )
        # Миграция: добавляем strategy в trade_logs
        if _table_exists(conn, "trade_logs") and not _col_exists(conn, "trade_logs", "strategy"):
            cur.execute("ALTER TABLE trade_logs ADD COLUMN strategy TEXT DEFAULT NULL")
        # Миграция: добавляем account_type в trade_logs
        if _table_exists(conn, "trade_logs") and not _col_exists(conn, "trade_logs", "account_type"):
            cur.execute("ALTER TABLE trade_logs ADD COLUMN account_type TEXT DEFAULT 'demo'")
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_logs_strategy ON trade_logs(user_id, strategy)"
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_logs_account_type ON trade_logs(user_id, account_type)"
        )

        # PENDING LIMIT ORDERS (+ time_in_force)
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS pending_limit_orders (
            user_id       INTEGER NOT NULL,
            order_id      TEXT    NOT NULL,
            symbol        TEXT    NOT NULL,
            side          TEXT    NOT NULL,
            qty           REAL    NOT NULL,
            price         REAL    NOT NULL,
            signal_id     INTEGER NOT NULL,
            created_ts    INTEGER NOT NULL,
            time_in_force TEXT    NOT NULL DEFAULT 'GTC',
            PRIMARY KEY(user_id, order_id),
            FOREIGN KEY(user_id)   REFERENCES users(user_id)  ON DELETE CASCADE,
            FOREIGN KEY(signal_id) REFERENCES signals(id)     ON DELETE CASCADE
        )
        """
        )
        # Миграция для существующих таблиц без time_in_force
        if _table_exists(conn, "pending_limit_orders") and not _col_exists(conn, "pending_limit_orders", "time_in_force"):
            cur.execute("ALTER TABLE pending_limit_orders ADD COLUMN time_in_force TEXT NOT NULL DEFAULT 'GTC'")
        # Миграция: добавляем strategy в pending_limit_orders
        if _table_exists(conn, "pending_limit_orders") and not _col_exists(conn, "pending_limit_orders", "strategy"):
            cur.execute("ALTER TABLE pending_limit_orders ADD COLUMN strategy TEXT DEFAULT NULL")
        # Миграция: добавляем account_type в pending_limit_orders для поддержки demo/real режимов
        if _table_exists(conn, "pending_limit_orders") and not _col_exists(conn, "pending_limit_orders", "account_type"):
            cur.execute("ALTER TABLE pending_limit_orders ADD COLUMN account_type TEXT DEFAULT 'demo'")

        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_pending_user_created ON pending_limit_orders(user_id, created_ts DESC)"
        )

        # =====================================================
        # LICENSING SYSTEM TABLES
        # =====================================================
        
        # User licenses table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_licenses (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                license_type    TEXT NOT NULL,         -- 'premium', 'basic', 'trial'
                start_date      INTEGER NOT NULL,      -- Unix timestamp
                end_date        INTEGER NOT NULL,      -- Unix timestamp
                is_active       INTEGER NOT NULL DEFAULT 1,
                created_at      INTEGER NOT NULL,
                updated_at      INTEGER,
                created_by      INTEGER,               -- Admin who created/modified
                notes           TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_licenses_user ON user_licenses(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_licenses_active ON user_licenses(is_active, end_date)")
        
        # Payment history table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS payment_history (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                license_id      INTEGER,               -- Reference to user_licenses
                payment_type    TEXT NOT NULL,         -- 'stars', 'ton', 'admin_grant', 'promo'
                amount          REAL NOT NULL,         -- Amount paid (in stars or TON)
                currency        TEXT NOT NULL,         -- 'XTR' (stars), 'TON', 'FREE'
                license_type    TEXT NOT NULL,         -- 'premium', 'basic', 'trial'
                period_days     INTEGER NOT NULL,      -- Duration in days
                telegram_charge_id TEXT,               -- Telegram payment charge ID
                status          TEXT NOT NULL DEFAULT 'completed', -- 'pending', 'completed', 'failed', 'refunded'
                created_at      INTEGER NOT NULL,
                metadata        TEXT,                  -- JSON with additional data
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY(license_id) REFERENCES user_licenses(id) ON DELETE SET NULL
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_payments_user ON payment_history(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_payments_status ON payment_history(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_payments_charge ON payment_history(telegram_charge_id)")
        
        # Promo codes table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS promo_codes (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                code            TEXT NOT NULL UNIQUE,
                license_type    TEXT NOT NULL,         -- 'premium', 'basic', 'trial'
                period_days     INTEGER NOT NULL,
                max_uses        INTEGER DEFAULT 1,     -- NULL = unlimited
                current_uses    INTEGER NOT NULL DEFAULT 0,
                is_active       INTEGER NOT NULL DEFAULT 1,
                valid_until     INTEGER,               -- Unix timestamp, NULL = no expiry
                created_at      INTEGER NOT NULL,
                created_by      INTEGER,               -- Admin ID
                notes           TEXT
            )
        """)
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_promo_code ON promo_codes(code)")
        
        # Promo code usage tracking
        cur.execute("""
            CREATE TABLE IF NOT EXISTS promo_usage (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                promo_id        INTEGER NOT NULL,
                user_id         INTEGER NOT NULL,
                used_at         INTEGER NOT NULL,
                FOREIGN KEY(promo_id) REFERENCES promo_codes(id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE(promo_id, user_id)              -- Each user can use promo only once
            )
        """)
        
        # Add license_type column to users table if not exists (for quick access)
        if not _col_exists(conn, "users", "current_license"):
            cur.execute("ALTER TABLE users ADD COLUMN current_license TEXT DEFAULT 'none'")
        if not _col_exists(conn, "users", "license_expires"):
            cur.execute("ALTER TABLE users ADD COLUMN license_expires INTEGER")

        # ═══════════════════════════════════════════════════════════════════════════════
        # MARKETPLACE & CUSTOM STRATEGIES TABLES
        # ═══════════════════════════════════════════════════════════════════════════════
        
        # Custom strategies created by users
        cur.execute("""
            CREATE TABLE IF NOT EXISTS custom_strategies (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                name            TEXT NOT NULL,
                description     TEXT,
                base_strategy   TEXT DEFAULT 'custom',   -- 'elcaro', 'rsibboi', 'fibonacci', etc.
                config_json     TEXT NOT NULL,           -- Full strategy config as JSON
                is_public       INTEGER DEFAULT 0,       -- Listed on marketplace
                is_active       INTEGER DEFAULT 1,
                win_rate        REAL DEFAULT 0,          -- Backtest win rate %
                total_pnl       REAL DEFAULT 0,          -- Backtest total PnL %
                total_trades    INTEGER DEFAULT 0,       -- Backtest trade count
                backtest_score  REAL DEFAULT 0,          -- Composite score for ranking
                created_at      INTEGER NOT NULL,
                updated_at      INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_strategies_user ON custom_strategies(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_strategies_public ON custom_strategies(is_public, is_active)")
        
        # Add performance_stats column if not exists
        if not _col_exists(conn, "custom_strategies", "performance_stats"):
            cur.execute("ALTER TABLE custom_strategies ADD COLUMN performance_stats TEXT")
        
        # Marketplace listings (strategies for sale)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS strategy_marketplace (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_id     INTEGER NOT NULL UNIQUE,
                seller_id       INTEGER NOT NULL,
                price_ton       REAL DEFAULT 0,          -- Price in TON
                price_stars     INTEGER DEFAULT 0,       -- Price in Telegram Stars
                revenue_share   REAL DEFAULT 0.5,        -- Creator's share (0.5 = 50%)
                rating          REAL DEFAULT 0,          -- Average rating 1-5
                rating_count    INTEGER DEFAULT 0,
                total_sales     INTEGER DEFAULT 0,
                total_revenue   REAL DEFAULT 0,
                is_active       INTEGER DEFAULT 1,
                featured        INTEGER DEFAULT 0,       -- Featured on homepage
                created_at      INTEGER NOT NULL,
                FOREIGN KEY(strategy_id) REFERENCES custom_strategies(id) ON DELETE CASCADE,
                FOREIGN KEY(seller_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_marketplace_seller ON strategy_marketplace(seller_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_marketplace_rating ON strategy_marketplace(rating DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_marketplace_active ON strategy_marketplace(is_active)")
        
        # Strategy purchases
        cur.execute("""
            CREATE TABLE IF NOT EXISTS strategy_purchases (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                buyer_id        INTEGER NOT NULL,
                marketplace_id  INTEGER NOT NULL,
                strategy_id     INTEGER NOT NULL,
                seller_id       INTEGER NOT NULL,
                amount_paid     REAL NOT NULL,
                currency        TEXT NOT NULL,           -- 'ton' or 'stars'
                seller_share    REAL NOT NULL,
                platform_share  REAL NOT NULL,
                is_active       INTEGER DEFAULT 1,       -- Access still valid
                purchased_at    INTEGER NOT NULL,
                FOREIGN KEY(buyer_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY(marketplace_id) REFERENCES strategy_marketplace(id) ON DELETE CASCADE,
                FOREIGN KEY(strategy_id) REFERENCES custom_strategies(id) ON DELETE CASCADE,
                FOREIGN KEY(seller_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_purchases_buyer ON strategy_purchases(buyer_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_purchases_seller ON strategy_purchases(seller_id)")
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_purchases_unique ON strategy_purchases(buyer_id, marketplace_id)")
        
        # Strategy ratings
        cur.execute("""
            CREATE TABLE IF NOT EXISTS strategy_ratings (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                marketplace_id  INTEGER NOT NULL,
                user_id         INTEGER NOT NULL,
                rating          INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
                review          TEXT,
                created_at      INTEGER NOT NULL,
                FOREIGN KEY(marketplace_id) REFERENCES strategy_marketplace(id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE(marketplace_id, user_id)         -- One rating per user per strategy
            )
        """)
        # Only create index if marketplace_id column exists
        if _col_exists(conn, "strategy_ratings", "marketplace_id"):
            cur.execute("CREATE INDEX IF NOT EXISTS idx_ratings_marketplace ON strategy_ratings(marketplace_id)")
        
        # Seller payouts tracking
        cur.execute("""
            CREATE TABLE IF NOT EXISTS seller_payouts (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id       INTEGER NOT NULL,
                amount          REAL NOT NULL,
                currency        TEXT NOT NULL,
                status          TEXT DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed'
                tx_hash         TEXT,                    -- Blockchain transaction hash
                requested_at    INTEGER NOT NULL,
                processed_at    INTEGER,
                FOREIGN KEY(seller_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_payouts_seller ON seller_payouts(seller_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_payouts_status ON seller_payouts(status)")
        
        # Top strategies view/table for rankings
        cur.execute("""
            CREATE TABLE IF NOT EXISTS top_strategies (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_type   TEXT NOT NULL,           -- 'system' or 'custom'
                strategy_id     INTEGER,                 -- NULL for system strategies
                strategy_name   TEXT NOT NULL,
                win_rate        REAL DEFAULT 0,
                total_pnl       REAL DEFAULT 0,
                total_trades    INTEGER DEFAULT 0,
                sharpe_ratio    REAL DEFAULT 0,
                max_drawdown    REAL DEFAULT 0,
                rank            INTEGER,
                config_json     TEXT,
                updated_at      INTEGER NOT NULL
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_top_rank ON top_strategies(rank)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_top_type ON top_strategies(strategy_type)")

        # ═══════════════════════════════════════════════════════════════════════════════
        # STRATEGY VERSIONING - Track all versions of custom strategies
        # ═══════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS strategy_versions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_id     INTEGER NOT NULL,
                version         TEXT NOT NULL,           -- Semver: "1.0.0", "1.1.0", etc.
                config_json     TEXT NOT NULL,           -- Full strategy config snapshot
                change_log      TEXT,                    -- Description of changes
                backtest_result TEXT,                    -- Backtest stats at this version
                created_by      INTEGER NOT NULL,        -- User who created this version
                created_at      INTEGER NOT NULL,
                FOREIGN KEY(strategy_id) REFERENCES custom_strategies(id) ON DELETE CASCADE,
                FOREIGN KEY(created_by) REFERENCES users(user_id) ON DELETE SET NULL
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_versions_strategy ON strategy_versions(strategy_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_versions_version ON strategy_versions(strategy_id, version)")
        
        # ═══════════════════════════════════════════════════════════════════════════════
        # STRATEGY LIVE STATE - Runtime state for strategies in live trading
        # ═══════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS strategy_live_state (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                strategy_id     INTEGER NOT NULL,
                exchange        TEXT NOT NULL DEFAULT 'bybit',  -- 'bybit', 'hyperliquid'
                account_type    TEXT NOT NULL DEFAULT 'demo',   -- 'demo', 'real'
                
                -- State
                is_running      INTEGER DEFAULT 0,       -- Is strategy actively running?
                is_paused       INTEGER DEFAULT 0,       -- Temporarily paused
                
                -- Current positions for this strategy
                open_positions  TEXT,                    -- JSON: [{symbol, side, entry, size}]
                pending_orders  TEXT,                    -- JSON: [{symbol, side, price, size}]
                
                -- Runtime stats
                session_pnl     REAL DEFAULT 0,          -- PnL since last start
                session_trades  INTEGER DEFAULT 0,       -- Trades since last start
                total_pnl       REAL DEFAULT 0,          -- Lifetime PnL
                total_trades    INTEGER DEFAULT 0,       -- Lifetime trades
                win_rate        REAL DEFAULT 0,
                
                -- Daily limits tracking
                daily_trades    INTEGER DEFAULT 0,
                daily_pnl       REAL DEFAULT 0,
                daily_reset_at  INTEGER,                 -- Unix timestamp of last daily reset
                
                -- Timestamps
                started_at      INTEGER,                 -- When strategy was last started
                stopped_at      INTEGER,                 -- When strategy was last stopped
                last_signal_at  INTEGER,                 -- Last signal processed
                updated_at      INTEGER,
                
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY(strategy_id) REFERENCES custom_strategies(id) ON DELETE CASCADE,
                UNIQUE(user_id, strategy_id, exchange, account_type)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_live_user ON strategy_live_state(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_live_running ON strategy_live_state(is_running)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_live_strategy ON strategy_live_state(strategy_id)")

        # ═══════════════════════════════════════════════════════════════════════════════
        # P0.1: EXCHANGE ACCOUNTS TABLE - Multi-exchange support with execution_targets
        # ═══════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS exchange_accounts (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                exchange        TEXT NOT NULL,           -- 'bybit', 'hyperliquid'
                account_type    TEXT NOT NULL,           -- 'demo', 'real', 'testnet', 'mainnet'
                label           TEXT,                    -- User-friendly label
                is_enabled      INTEGER DEFAULT 1,       -- Is this account active for trading?
                is_default      INTEGER DEFAULT 0,       -- Default account for this exchange
                
                -- API credentials (encrypted or plain for now)
                api_key         TEXT,
                api_secret      TEXT,
                extra_json      TEXT,                    -- JSON for HL private_key, wallet, vault, etc.
                
                -- Account-specific settings
                max_positions   INTEGER DEFAULT 10,      -- Max concurrent positions
                max_leverage    INTEGER DEFAULT 100,     -- Max allowed leverage
                risk_limit_pct  REAL DEFAULT 30.0,       -- Max effective_risk (sl_pct * leverage)
                
                -- Execution targeting
                priority        INTEGER DEFAULT 0,       -- Order of execution (lower = first)
                
                -- Metadata
                created_at      DATETIME DEFAULT (CURRENT_TIMESTAMP),
                updated_at      DATETIME DEFAULT (CURRENT_TIMESTAMP),
                last_sync_at    DATETIME,
                
                UNIQUE(user_id, exchange, account_type),
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_exch_accounts_user ON exchange_accounts(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_exch_accounts_enabled ON exchange_accounts(user_id, is_enabled)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_exch_accounts_exchange ON exchange_accounts(user_id, exchange)")

        # ═══════════════════════════════════════════════════════════════════════════════
        # P0.3: ACTIVE POSITIONS EXTENSIONS - source, manual_sltp_override, ATR state
        # ═══════════════════════════════════════════════════════════════════════════════
        
        # Миграция: добавляем source (откуда создана позиция)
        if _table_exists(conn, "active_positions") and not _col_exists(conn, "active_positions", "source"):
            cur.execute("ALTER TABLE active_positions ADD COLUMN source TEXT DEFAULT 'bot'")
        
        # Миграция: добавляем opened_by (для WebApp интеграции)
        if _table_exists(conn, "active_positions") and not _col_exists(conn, "active_positions", "opened_by"):
            cur.execute("ALTER TABLE active_positions ADD COLUMN opened_by TEXT DEFAULT 'bot'")
        
        # Миграция: добавляем exchange (поддержка мульти-биржи)
        if _table_exists(conn, "active_positions") and not _col_exists(conn, "active_positions", "exchange"):
            cur.execute("ALTER TABLE active_positions ADD COLUMN exchange TEXT DEFAULT 'bybit'")
        
        # Миграция: SL/TP цены
        if _table_exists(conn, "active_positions") and not _col_exists(conn, "active_positions", "sl_price"):
            cur.execute("ALTER TABLE active_positions ADD COLUMN sl_price REAL")
        if _table_exists(conn, "active_positions") and not _col_exists(conn, "active_positions", "tp_price"):
            cur.execute("ALTER TABLE active_positions ADD COLUMN tp_price REAL")
        
        # Миграция: manual_sltp_override - бот не будет перезаписывать ручные изменения
        if _table_exists(conn, "active_positions") and not _col_exists(conn, "active_positions", "manual_sltp_override"):
            cur.execute("ALTER TABLE active_positions ADD COLUMN manual_sltp_override INTEGER DEFAULT 0")
        if _table_exists(conn, "active_positions") and not _col_exists(conn, "active_positions", "manual_sltp_ts"):
            cur.execute("ALTER TABLE active_positions ADD COLUMN manual_sltp_ts INTEGER")
        
        # P0.4: ATR trailing state - переживает рестарт бота
        if _table_exists(conn, "active_positions") and not _col_exists(conn, "active_positions", "atr_activated"):
            cur.execute("ALTER TABLE active_positions ADD COLUMN atr_activated INTEGER DEFAULT 0")
        if _table_exists(conn, "active_positions") and not _col_exists(conn, "active_positions", "atr_activation_price"):
            cur.execute("ALTER TABLE active_positions ADD COLUMN atr_activation_price REAL")
        if _table_exists(conn, "active_positions") and not _col_exists(conn, "active_positions", "atr_last_stop_price"):
            cur.execute("ALTER TABLE active_positions ADD COLUMN atr_last_stop_price REAL")
        if _table_exists(conn, "active_positions") and not _col_exists(conn, "active_positions", "atr_last_update_ts"):
            cur.execute("ALTER TABLE active_positions ADD COLUMN atr_last_update_ts INTEGER")
        # P0.5: use_atr - флаг включения ATR trailing для позиции
        if _table_exists(conn, "active_positions") and not _col_exists(conn, "active_positions", "use_atr"):
            cur.execute("ALTER TABLE active_positions ADD COLUMN use_atr INTEGER DEFAULT 0")
        
        # Миграция: leverage для позиции
        if _table_exists(conn, "active_positions") and not _col_exists(conn, "active_positions", "leverage"):
            cur.execute("ALTER TABLE active_positions ADD COLUMN leverage INTEGER")
        
        # Миграция: client_order_id для идемпотентности
        if _table_exists(conn, "active_positions") and not _col_exists(conn, "active_positions", "client_order_id"):
            cur.execute("ALTER TABLE active_positions ADD COLUMN client_order_id TEXT")
        
        # Миграция: exchange_order_id (ID ордера на бирже)
        if _table_exists(conn, "active_positions") and not _col_exists(conn, "active_positions", "exchange_order_id"):
            cur.execute("ALTER TABLE active_positions ADD COLUMN exchange_order_id TEXT")
        
        # Миграция: env (unified paper/live) для новой Target модели
        if _table_exists(conn, "active_positions") and not _col_exists(conn, "active_positions", "env"):
            cur.execute("ALTER TABLE active_positions ADD COLUMN env TEXT")
            # Заполняем env на основе account_type
            cur.execute("""
                UPDATE active_positions 
                SET env = CASE 
                    WHEN account_type IN ('demo', 'testnet') THEN 'paper'
                    WHEN account_type IN ('real', 'mainnet') THEN 'live'
                    ELSE 'paper'
                END
                WHERE env IS NULL
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_active_env ON active_positions(user_id, exchange, env)")

        # ═══════════════════════════════════════════════════════════════════════════════
        # ROUTING POLICY & MULTI-TARGET SUPPORT
        # ═══════════════════════════════════════════════════════════════════════════════
        
        # Миграция: routing_policy для users - определяет как маршрутизировать сигналы
        # Значения:
        #   - 'active_only': только на выбранном таргете (UI)
        #   - 'same_exchange_all_envs': текущая биржа, все включенные env (demo+real или testnet+mainnet)
        #   - 'all_enabled': все включенные таргеты (до 4)
        if not _col_exists(conn, "users", "routing_policy"):
            cur.execute("ALTER TABLE users ADD COLUMN routing_policy TEXT DEFAULT 'same_exchange_all_envs'")
        
        # Миграция: live_enabled - отдельное подтверждение для live/mainnet трейдинга
        # Пользователь должен явно подтвердить, что хочет торговать на реальные деньги
        if not _col_exists(conn, "users", "live_enabled"):
            cur.execute("ALTER TABLE users ADD COLUMN live_enabled INTEGER DEFAULT 0")
        
        # Миграция: добавляем env поле в user_strategy_settings для fallback логики
        if _table_exists(conn, "user_strategy_settings") and not _col_exists(conn, "user_strategy_settings", "env"):
            cur.execute("ALTER TABLE user_strategy_settings ADD COLUMN env TEXT")
            # Заполняем env на основе account_type
            cur.execute("""
                UPDATE user_strategy_settings 
                SET env = CASE 
                    WHEN account_type IN ('demo', 'testnet') THEN 'paper'
                    WHEN account_type IN ('real', 'mainnet') THEN 'live'
                    ELSE NULL
                END
                WHERE env IS NULL
            """)
        
        # Миграция: добавляем routing_policy в user_strategy_settings (per-strategy override)
        if _table_exists(conn, "user_strategy_settings") and not _col_exists(conn, "user_strategy_settings", "routing_policy"):
            cur.execute("ALTER TABLE user_strategy_settings ADD COLUMN routing_policy TEXT")
        
        # Миграция: добавляем explicit targets list (JSON) для CUSTOM_TARGET_LIST policy
        if _table_exists(conn, "user_strategy_settings") and not _col_exists(conn, "user_strategy_settings", "targets_json"):
            cur.execute("ALTER TABLE user_strategy_settings ADD COLUMN targets_json TEXT")

        conn.commit()

# ------------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------------
def ensure_user(user_id: int):
    """Гарантирует наличие записи пользователя. Нужен перед любыми UPDATE."""
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users(user_id) VALUES(?)",
            (user_id,),
        )
        conn.commit()

def update_user_info(user_id: int, username: str = None, first_name: str = None):
    """Updates user info (username, first_name) if provided"""
    ensure_user(user_id)
    updates = []
    params = []
    
    if username is not None:
        updates.append("username = ?")
        params.append(username)
    
    if first_name is not None:
        updates.append("first_name = ?")
        params.append(first_name)
    
    if updates:
        params.append(user_id)
        with get_conn() as conn:
            conn.execute(
                f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?",
                params
            )
            conn.commit()

def delete_user(user_id: int):
    """
    Полностью удаляет пользователя.
    Связанные записи чистятся каскадом (active_positions, trade_logs, pyramids, pending_limit_orders).
    """
    with get_conn() as conn:
        conn.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        conn.commit()

def ban_user(user_id: int):
    """Блокировка пользователя: бан + снятие одобрения."""
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute("UPDATE users SET is_banned=1, is_allowed=0 WHERE user_id=?", (user_id,))
        conn.commit()

def allow_user(user_id: int):
    """Одобрение пользователя: снимаем бан и ставим флаг допуска."""
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute("UPDATE users SET is_allowed=1, is_banned=0 WHERE user_id=?", (user_id,))
        conn.commit()

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
    except Exception:
        pass  # Ignore if core not available

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
    """Get all API credentials and trading mode for a user.
    
    Returns:
        Dict with demo_api_key, demo_api_secret, real_api_key, real_api_secret, trading_mode
    """
    with get_conn() as conn:
        row = conn.execute(
            "SELECT demo_api_key, demo_api_secret, real_api_key, real_api_secret, trading_mode FROM users WHERE user_id=?",
            (user_id,),
        ).fetchone()
    
    if not row:
        return {
            "demo_api_key": None, "demo_api_secret": None,
            "real_api_key": None, "real_api_secret": None,
            "trading_mode": "demo"
        }
    
    return {
        "demo_api_key": row[0],
        "demo_api_secret": row[1],
        "real_api_key": row[2],
        "real_api_secret": row[3],
        "trading_mode": row[4] or "demo"
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
            (1 if enabled else 0, user_id)
        )
        conn.commit()
    invalidate_user_cache(user_id)


def get_execution_targets(
    user_id: int,
    strategy: str = None,
    override_policy: str = None
) -> list[dict]:
    """
    Get list of execution targets based on routing policy.
    
    Returns list of dicts with keys: exchange, env, account_type
    
    Priority:
    1. Strategy's custom targets (if strategy has routing_policy='custom' and targets_json)
    2. Strategy's routing_policy (if set and != 'global')
    3. User's global routing_policy
    4. Default: SAME_EXCHANGE_ALL_ENVS
    
    Safety: Filters out live targets if live_enabled=False
    """
    # Determine effective routing policy
    policy = override_policy
    strategy_targets = None
    
    if not policy and strategy:
        # Check if strategy has explicit targets or routing_policy
        context = get_user_trading_context(user_id)
        strat_settings = get_strategy_settings(user_id, strategy, context["exchange"], context["account_type"])
        
        if strat_settings.get("routing_policy") == RoutingPolicy.CUSTOM:
            # Use explicit target list from strategy
            import json
            targets_json = strat_settings.get("targets_json")
            if targets_json:
                try:
                    strategy_targets = json.loads(targets_json)
                except:
                    pass
        elif strat_settings.get("routing_policy") and strat_settings.get("routing_policy") != "global":
            policy = strat_settings.get("routing_policy")
    
    if not policy:
        policy = get_routing_policy(user_id)
    
    # Get user context
    context = get_user_trading_context(user_id)
    live_enabled = get_live_enabled(user_id)
    
    targets = []
    
    # If strategy has explicit targets, use them
    if strategy_targets:
        for t in strategy_targets:
            env = t.get("env", "paper")
            # Safety check: skip live if not enabled
            if env == "live" and not live_enabled:
                continue
            targets.append({
                "exchange": t.get("exchange", "bybit"),
                "env": env,
                "account_type": _env_to_account_type(t.get("exchange", "bybit"), env)
            })
        return targets
    
    # Apply routing policy
    if policy == RoutingPolicy.ACTIVE_ONLY:
        # Only the currently selected target (from UI)
        env = "paper" if context["account_type"] in ("demo", "testnet") else "live"
        if env == "live" and not live_enabled:
            return []  # User hasn't enabled live trading
        return [{
            "exchange": context["exchange"],
            "env": env,
            "account_type": context["account_type"]
        }]
    
    elif policy == RoutingPolicy.SAME_EXCHANGE_ALL_ENVS:
        # Current exchange, all enabled envs (demo+real or testnet+mainnet)
        exchange = context["exchange"]
        account_types = get_active_account_types(user_id)
        
        for acc_type in account_types:
            env = "paper" if acc_type in ("demo", "testnet") else "live"
            # Safety check: skip live if not enabled
            if env == "live" and not live_enabled:
                continue
            targets.append({
                "exchange": exchange,
                "env": env,
                "account_type": acc_type
            })
        return targets
    
    elif policy == RoutingPolicy.ALL_ENABLED:
        # All enabled targets across all exchanges (up to 4)
        # Check Bybit
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
        
        # Check HyperLiquid
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
        
        return targets
    
    # Default fallback: same as SAME_EXCHANGE_ALL_ENVS
    exchange = context["exchange"]
    account_types = get_active_account_types(user_id)
    for acc_type in account_types:
        env = "paper" if acc_type in ("demo", "testnet") else "live"
        if env == "live" and not live_enabled:
            continue
        targets.append({
            "exchange": exchange,
            "env": env,
            "account_type": acc_type
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
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, user_id))
        conn.commit()
    invalidate_user_cache(user_id)

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
            "trade_oi", "trade_rsi_bb",
            "tp_percent", "sl_percent",
            "use_atr", "lang",
            # стратегии/пороги
            "strategies_enabled", "strategies_order",
            "rsi_lo", "rsi_hi", "bb_touch_k",
            "oi_min_pct", "price_min_pct", "limit_only_default",
            # доступ/согласие
            "is_allowed", "is_banned", "terms_accepted",
            # совместимость
            "first_seen_ts", "last_seen_ts",
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
            "use_atr": True,
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
        "strategy_settings": json.loads(data.get("strategy_settings") or "{}")
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
        "spot_settings": json.loads(data.get("spot_settings") or "{}")
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
        "limit_ladder_settings": json.loads(data.get("limit_ladder_settings") or "[]")
        if data.get("limit_ladder_settings")
        else [],
        # Global order type
        "global_order_type": data.get("global_order_type", "market")
        if "global_order_type" in data
        else "market",
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
        "coins_group": None,  # "ALL", "TOP100", "VOLATILE" or None for global
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
}

STRATEGY_NAMES = ["oi", "rsi_bb", "scryptomera", "scalper", "elcaro", "fibonacci", "manual", "wyckoff"]
STRATEGY_SETTING_FIELDS = [
    "percent", "sl_percent", "tp_percent",
    "tp_pct", "sl_pct",  # Aliases for compatibility
    "atr_periods", "atr_multiplier_sl", "atr_trigger_pct",
    "use_atr",  # 0 or 1 - use ATR trailing or fixed SL/TP
    "order_type",  # "market" or "limit"
    "coins_group",  # "ALL", "TOP100", "VOLATILE" or None
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
}


# ------------------------------------------------------------------------------------
# NEW: Database-based Strategy Settings Functions
# ------------------------------------------------------------------------------------

# Columns in user_strategy_settings table that can be read/written
_STRATEGY_DB_COLUMNS = [
    "enabled", "percent", "sl_percent", "tp_percent", "leverage",
    "use_atr", "atr_periods", "atr_multiplier_sl", "atr_trigger_pct",
    "order_type", "coins_group", "direction", "trading_mode",
    "long_percent", "long_sl_percent", "long_tp_percent",
    "long_atr_periods", "long_atr_multiplier_sl", "long_atr_trigger_pct",
    "short_percent", "short_sl_percent", "short_tp_percent",
    "short_atr_periods", "short_atr_multiplier_sl", "short_atr_trigger_pct",
    "min_quality"
]


def _migrate_single_strategy(user_id: int, strategy: str, strat_json: dict, 
                              exchange: str, account_type: str, cur) -> bool:
    """
    Helper to migrate a single strategy's settings from JSON dict to DB.
    Uses provided cursor for transaction.
    """
    # Filter only valid columns
    valid_settings = {k: v for k, v in strat_json.items() if k in _STRATEGY_DB_COLUMNS and v is not None}
    if not valid_settings:
        return False
    
    columns = ["user_id", "strategy", "exchange", "account_type"] + list(valid_settings.keys())
    placeholders = ["?"] * len(columns)
    values = [user_id, strategy, exchange, account_type] + list(valid_settings.values())
    
    try:
        cur.execute(f"""
            INSERT OR REPLACE INTO user_strategy_settings ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """, values)
        return True
    except Exception:
        return False


def get_strategy_settings_db(user_id: int, strategy: str, exchange: str = "bybit", account_type: str = "demo") -> dict:
    """
    Get strategy settings from user_strategy_settings table.
    Returns dict with all strategy parameters. NULL values are returned as None.
    Auto-migrates from JSON if DB is empty but JSON exists.
    """
    if strategy not in STRATEGY_NAMES:
        return DEFAULT_STRATEGY_SETTINGS.get(strategy, {}).copy()
    
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT enabled, percent, sl_percent, tp_percent, leverage,
                   use_atr, atr_periods, atr_multiplier_sl, atr_trigger_pct,
                   order_type, coins_group, direction, trading_mode,
                   long_percent, long_sl_percent, long_tp_percent,
                   long_atr_periods, long_atr_multiplier_sl, long_atr_trigger_pct,
                   short_percent, short_sl_percent, short_tp_percent,
                   short_atr_periods, short_atr_multiplier_sl, short_atr_trigger_pct,
                   min_quality
            FROM user_strategy_settings
            WHERE user_id = ? AND strategy = ? AND exchange = ? AND account_type = ?
        """, (user_id, strategy, exchange, account_type))
        row = cur.fetchone()
        
        if not row:
            # Check if user has JSON settings to migrate
            cur.execute("SELECT strategy_settings FROM users WHERE user_id = ?", (user_id,))
            json_row = cur.fetchone()
            if json_row and json_row[0]:
                try:
                    json_settings = json.loads(json_row[0])
                    if json_settings and strategy in json_settings:
                        # Migrate this strategy's settings from JSON to DB
                        strat_json = json_settings.get(strategy, {})
                        if isinstance(strat_json, dict) and strat_json:
                            # Insert into DB
                            _migrate_single_strategy(user_id, strategy, strat_json, exchange, account_type, cur)
                            conn.commit()
                            # Re-fetch from DB
                            cur.execute("""
                                SELECT enabled, percent, sl_percent, tp_percent, leverage,
                                       use_atr, atr_periods, atr_multiplier_sl, atr_trigger_pct,
                                       order_type, coins_group, direction, trading_mode,
                                       long_percent, long_sl_percent, long_tp_percent,
                                       long_atr_periods, long_atr_multiplier_sl, long_atr_trigger_pct,
                                       short_percent, short_sl_percent, short_tp_percent,
                                       short_atr_periods, short_atr_multiplier_sl, short_atr_trigger_pct,
                                       min_quality
                                FROM user_strategy_settings
                                WHERE user_id = ? AND strategy = ? AND exchange = ? AND account_type = ?
                            """, (user_id, strategy, exchange, account_type))
                            row = cur.fetchone()
                except (json.JSONDecodeError, Exception):
                    pass
        
        if not row:
            # Return defaults for this strategy
            return DEFAULT_STRATEGY_SETTINGS.get(strategy, {}).copy()
        
        # Map row to dict
        result = {
            "enabled": row[0],
            "percent": row[1],
            "sl_percent": row[2],
            "tp_percent": row[3],
            "leverage": row[4],
            "use_atr": row[5],
            "atr_periods": row[6],
            "atr_multiplier_sl": row[7],
            "atr_trigger_pct": row[8],
            "order_type": row[9] or "market",
            "coins_group": row[10],
            "direction": row[11] or "all",
            "trading_mode": row[12] or "global",
            "long_percent": row[13],
            "long_sl_percent": row[14],
            "long_tp_percent": row[15],
            "long_atr_periods": row[16],
            "long_atr_multiplier_sl": row[17],
            "long_atr_trigger_pct": row[18],
            "short_percent": row[19],
            "short_sl_percent": row[20],
            "short_tp_percent": row[21],
            "short_atr_periods": row[22],
            "short_atr_multiplier_sl": row[23],
            "short_atr_trigger_pct": row[24],
            "min_quality": row[25] if row[25] is not None else 50,
        }
        return result
    finally:
        release_conn(conn)


def set_strategy_setting_db(user_id: int, strategy: str, field: str, value, 
                            exchange: str = "bybit", account_type: str = "demo") -> bool:
    """
    Set a single field for a strategy in user_strategy_settings table.
    Creates row if not exists (UPSERT).
    """
    if strategy not in STRATEGY_NAMES:
        return False
    if field not in _STRATEGY_DB_COLUMNS:
        return False
    
    conn = get_conn()
    try:
        cur = conn.cursor()
        # Check if row exists
        cur.execute("""
            SELECT 1 FROM user_strategy_settings
            WHERE user_id = ? AND strategy = ? AND exchange = ? AND account_type = ?
        """, (user_id, strategy, exchange, account_type))
        exists = cur.fetchone()
        
        if exists:
            # Update existing row
            cur.execute(f"""
                UPDATE user_strategy_settings 
                SET {field} = ?
                WHERE user_id = ? AND strategy = ? AND exchange = ? AND account_type = ?
            """, (value, user_id, strategy, exchange, account_type))
        else:
            # Insert new row
            cur.execute(f"""
                INSERT INTO user_strategy_settings (user_id, strategy, exchange, account_type, {field})
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, strategy, exchange, account_type, value))
        
        conn.commit()
        invalidate_user_cache(user_id)
        return True
    except Exception as e:
        print(f"[DB ERROR] set_strategy_setting_db: {e}")
        return False
    finally:
        release_conn(conn)


def set_strategy_settings_db(user_id: int, strategy: str, settings: dict,
                             exchange: str = "bybit", account_type: str = "demo") -> bool:
    """
    Set multiple fields for a strategy at once (UPSERT).
    """
    if strategy not in STRATEGY_NAMES:
        return False
    
    # Filter only valid columns
    valid_settings = {k: v for k, v in settings.items() if k in _STRATEGY_DB_COLUMNS}
    if not valid_settings:
        return False
    
    conn = get_conn()
    try:
        cur = conn.cursor()
        # Check if row exists
        cur.execute("""
            SELECT id FROM user_strategy_settings
            WHERE user_id = ? AND strategy = ? AND exchange = ? AND account_type = ?
        """, (user_id, strategy, exchange, account_type))
        exists = cur.fetchone()
        
        if exists:
            # Build UPDATE query
            set_parts = [f"{k} = ?" for k in valid_settings.keys()]
            set_parts.append("updated_at = CURRENT_TIMESTAMP")
            values = list(valid_settings.values())
            values.extend([user_id, strategy, exchange, account_type])
            
            cur.execute(f"""
                UPDATE user_strategy_settings 
                SET {', '.join(set_parts)}
                WHERE user_id = ? AND strategy = ? AND exchange = ? AND account_type = ?
            """, values)
        else:
            # Build INSERT query
            columns = ["user_id", "strategy", "exchange", "account_type"] + list(valid_settings.keys())
            placeholders = ["?"] * len(columns)
            values = [user_id, strategy, exchange, account_type] + list(valid_settings.values())
            
            cur.execute(f"""
                INSERT INTO user_strategy_settings ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """, values)
        
        conn.commit()
        invalidate_user_cache(user_id)
        return True
    except Exception as e:
        print(f"[DB ERROR] set_strategy_settings_db: {e}")
        return False
    finally:
        release_conn(conn)


def get_all_strategy_settings_db(user_id: int, exchange: str = "bybit", account_type: str = "demo") -> dict:
    """
    Get all strategy settings for a user/exchange/account_type combination.
    Returns dict: { "scryptomera": {...}, "scalper": {...}, ... }
    """
    result = {}
    for strategy in STRATEGY_NAMES:
        result[strategy] = get_strategy_settings_db(user_id, strategy, exchange, account_type)
    return result


def migrate_json_to_db_settings(user_id: int) -> bool:
    """
    Migrate user's JSON strategy_settings to new database table.
    Call this once per user to migrate existing settings.
    """
    cfg = get_user_config(user_id)
    json_settings = cfg.get("strategy_settings", {})
    
    if not json_settings:
        return True  # Nothing to migrate
    
    conn = get_conn()
    try:
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
    finally:
        release_conn(conn)


def get_strategy_settings_v2(user_id: int, strategy: str, exchange: str = "bybit", account_type: str = "demo") -> dict:
    """
    Get settings for a specific strategy, exchange, and account type.
    NOW USES DATABASE TABLE instead of JSON.
    Returns dict with keys: enabled, percent, sl_percent, tp_percent, leverage, etc.
    """
    return get_strategy_settings_db(user_id, strategy, exchange, account_type)


def set_strategy_settings_v2(user_id: int, strategy: str, settings: dict, exchange: str = "bybit", account_type: str = "demo") -> bool:
    """
    Set settings for a specific strategy, exchange, and account type.
    NOW USES DATABASE TABLE instead of JSON.
    """
    return set_strategy_settings_db(user_id, strategy, settings, exchange, account_type)


def is_strategy_enabled_v2(user_id: int, strategy: str, exchange: str = "bybit", account_type: str = "demo") -> bool:
    """
    Check if a strategy is enabled for specific exchange and account type.
    """
    settings = get_strategy_settings_db(user_id, strategy, exchange, account_type)
    return bool(settings.get("enabled", False))


def get_strategy_settings(user_id: int, strategy: str, exchange: str = None, account_type: str = None) -> dict:
    """
    Get settings for a specific strategy with FALLBACK logic.
    
    Fallback priority (most specific → least specific):
    1. (exchange + account_type) - exact match
    2. (exchange + None) - exchange-level defaults  
    3. (None + None) - global strategy defaults
    
    If exchange and account_type are not provided, automatically detects from user's current context.
    
    Returns dict with keys: percent, sl_percent, tp_percent, atr_periods, atr_multiplier_sl, atr_trigger_pct, routing_policy, targets_json
    Values are None if not customized (use global defaults)
    """
    # Auto-detect context if not provided
    if exchange is None or account_type is None:
        context = get_user_trading_context(user_id)
        exchange = exchange or context["exchange"]
        account_type = account_type or context["account_type"]
    
    # 1. Try exact match (exchange + account_type)
    settings = get_strategy_settings_db(user_id, strategy, exchange, account_type)
    
    # 2. If settings are all None (no customization), try exchange-level fallback
    if _is_empty_settings(settings):
        # Try exchange + 'default' account_type (which we interpret as exchange-level)
        exchange_settings = get_strategy_settings_db(user_id, strategy, exchange, "default")
        if not _is_empty_settings(exchange_settings):
            settings = _merge_settings(settings, exchange_settings)
    
    # 3. Try global strategy defaults (exchange='global', account_type='default')
    if _is_empty_settings(settings):
        global_settings = get_strategy_settings_db(user_id, strategy, "global", "default")
        if not _is_empty_settings(global_settings):
            settings = _merge_settings(settings, global_settings)
    
    # 4. Merge with routing_policy and targets_json from extended query
    settings = _enrich_with_routing(user_id, strategy, exchange, account_type, settings)
    
    return settings


def _is_empty_settings(settings: dict) -> bool:
    """Check if all relevant settings are None/empty (no customization)."""
    key_fields = ["percent", "sl_percent", "tp_percent", "leverage"]
    return all(settings.get(k) is None for k in key_fields)


def _merge_settings(target: dict, source: dict) -> dict:
    """Merge source settings into target, only filling None values."""
    result = target.copy()
    for key, value in source.items():
        if result.get(key) is None and value is not None:
            result[key] = value
    return result


def _enrich_with_routing(user_id: int, strategy: str, exchange: str, account_type: str, settings: dict) -> dict:
    """Enrich settings with routing_policy and targets_json if available."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT routing_policy, targets_json
            FROM user_strategy_settings
            WHERE user_id = ? AND strategy = ? AND exchange = ? AND account_type = ?
        """, (user_id, strategy, exchange, account_type))
        row = cur.fetchone()
        if row:
            settings["routing_policy"] = row[0]
            settings["targets_json"] = row[1]
        else:
            settings["routing_policy"] = None
            settings["targets_json"] = None
        return settings
    except:
        settings["routing_policy"] = None
        settings["targets_json"] = None
        return settings
    finally:
        release_conn(conn)


def set_strategy_setting(user_id: int, strategy: str, field: str, value: float | None,
                         exchange: str = None, account_type: str = None) -> bool:
    """
    Set a specific field for a strategy.
    NOW USES DATABASE TABLE instead of JSON.
    
    If exchange and account_type are not provided, automatically detects from user's current context.
    
    field must be one of: percent, sl_percent, tp_percent, atr_mult, etc.
    value can be None to reset to global default
    """
    # Auto-detect context if not provided
    if exchange is None or account_type is None:
        context = get_user_trading_context(user_id)
        exchange = exchange or context["exchange"]
        account_type = account_type or context["account_type"]
    
    return set_strategy_setting_db(user_id, strategy, field, value, exchange, account_type)


def get_effective_settings(user_id: int, strategy: str, global_cfg: dict | None = None, timeframe: str = "24h") -> dict:
    """
    Get effective settings for a strategy, falling back to global config and timeframe defaults.
    Returns dict with percent, sl_percent, tp_percent, atr_periods, atr_multiplier_sl, atr_trigger_pct
    """
    from coin_params import TIMEFRAME_PARAMS
    
    if global_cfg is None:
        global_cfg = get_user_config(user_id)
    
    strat_settings = get_strategy_settings(user_id, strategy)
    tf_cfg = TIMEFRAME_PARAMS.get(timeframe, TIMEFRAME_PARAMS.get("24h", {}))
    
    return {
        "percent": strat_settings.get("percent") if strat_settings.get("percent") is not None else global_cfg.get("percent", 1.0),
        "sl_percent": strat_settings.get("sl_percent") if strat_settings.get("sl_percent") is not None else global_cfg.get("sl_percent", DEFAULT_SL_PCT),
        "tp_percent": strat_settings.get("tp_percent") if strat_settings.get("tp_percent") is not None else global_cfg.get("tp_percent", DEFAULT_TP_PCT),
        "atr_periods": strat_settings.get("atr_periods") if strat_settings.get("atr_periods") is not None else tf_cfg.get("atr_periods", 7),
        "atr_multiplier_sl": strat_settings.get("atr_multiplier_sl") if strat_settings.get("atr_multiplier_sl") is not None else tf_cfg.get("atr_multiplier_sl", 1.0),
        "atr_trigger_pct": strat_settings.get("atr_trigger_pct") if strat_settings.get("atr_trigger_pct") is not None else tf_cfg.get("atr_trigger_pct", 2.0),
    }


def get_effective_settings_v2(user_id: int, strategy: str, exchange: str = "bybit", account_type: str = "demo", timeframe: str = "24h") -> dict:
    """
    Get effective settings for a strategy, exchange, and account type.
    Falls back to global config and timeframe defaults.
    Returns dict with enabled, percent, sl_percent, tp_percent, leverage, atr_periods, atr_multiplier_sl, atr_trigger_pct
    """
    from coin_params import TIMEFRAME_PARAMS
    
    global_cfg = get_user_config(user_id)
    strat_settings = get_strategy_settings_v2(user_id, strategy, exchange, account_type)
    tf_cfg = TIMEFRAME_PARAMS.get(timeframe, TIMEFRAME_PARAMS.get("24h", {}))
    
    def _get(key, default):
        """Get value from strategy settings, fallback to global, then default"""
        val = strat_settings.get(key)
        if val is not None:
            return val
        global_val = global_cfg.get(key)
        if global_val is not None:
            return global_val
        return default
    
    def _get_tf(key, default):
        """Get value from strategy settings, fallback to timeframe config, then default"""
        val = strat_settings.get(key)
        if val is not None:
            return val
        tf_val = tf_cfg.get(key)
        if tf_val is not None:
            return tf_val
        return default
    
    return {
        "enabled": bool(strat_settings.get("enabled", False)),
        "percent": _get("percent", 5.0),
        "sl_percent": _get("sl_percent", DEFAULT_SL_PCT),
        "tp_percent": _get("tp_percent", DEFAULT_TP_PCT),
        "leverage": _get("leverage", 10),
        "atr_periods": _get_tf("atr_periods", 7),
        "atr_multiplier_sl": _get_tf("atr_multiplier_sl", 1.0),
        "atr_trigger_pct": _get_tf("atr_trigger_pct", 2.0),
        # Strategy-specific fields
        "direction": strat_settings.get("direction", "all"),
        "order_type": strat_settings.get("order_type", "market"),
        # Pass through any extra fields
        **{k: v for k, v in strat_settings.items() if k not in [
            "enabled", "percent", "sl_percent", "tp_percent", "leverage",
            "atr_periods", "atr_multiplier_sl", "atr_trigger_pct", "direction", "order_type"
        ]}
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
    """
    global _active_users_cache
    now = time.time()
    ts, users = _active_users_cache
    if now - ts < CACHE_TTL:
        return users.copy()
    
    with get_conn() as conn:
        # P0.10: Include HL users in the query
        rows = conn.execute("""
            SELECT user_id FROM users 
            WHERE is_banned = 0 
            AND (
                demo_api_key IS NOT NULL 
                OR real_api_key IS NOT NULL
                OR (hl_private_key IS NOT NULL AND hl_enabled = 1)
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
    ts = _now_ms()
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
          INSERT OR IGNORE INTO news(link, title, description, image_url, signal, sentiment)
          VALUES (?, ?, ?, ?, ?, ?)
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
def get_pyramid(user_id: int, symbol: str) -> dict:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT side, count FROM pyramids WHERE user_id=? AND symbol=?",
            (user_id, symbol),
        ).fetchone()
    return {"side": row[0], "count": row[1]} if row else {"side": None, "count": 0}

def inc_pyramid(user_id: int, symbol: str, new_side: str):
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO pyramids(user_id, symbol, side, count)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(user_id, symbol) DO UPDATE SET
              side  = excluded.side,
              count = CASE
                        WHEN pyramids.side <> excluded.side THEN 1
                        ELSE pyramids.count + 1
                      END
        """,
            (user_id, symbol, new_side),
        )
        conn.commit()

def reset_pyramid(user_id: int, symbol: str):
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM pyramids WHERE user_id=? AND symbol=?", (user_id, symbol)
        )
        conn.commit()

def get_all_pyramided_symbols(user_id: int) -> list[str]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT symbol FROM pyramids WHERE user_id=?", (user_id,)
        ).fetchall()
    return [r[0] for r in rows]

# ------------------------------------------------------------------------------------
# Signals
# ------------------------------------------------------------------------------------
def add_signal(
    raw_message: str,
    tf: str | None,
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
            raw_message, tf, side, symbol, price,
            oi_prev, oi_now, oi_chg, vol_from, vol_to, price_chg,
            vol_delta, rsi, bb_hi, bb_lo
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                raw_message,
                tf,
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
        "raw_message",
        "tf",
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
          SELECT id FROM signals WHERE symbol=? AND (tf=? OR tf IS NULL)
          ORDER BY ts DESC LIMIT 1
        """,
            (symbol, timeframe),
        ).fetchone()
        if row:
            return int(row[0])
        
        # Fallback: search by symbol in raw_message (for signals with symbol=NULL)
        # Look for patterns like [SYMBOL] or "SYMBOL" or "🔔 SYMBOL"
        row = conn.execute(
            """
          SELECT id FROM signals 
          WHERE (raw_message LIKE ? OR raw_message LIKE ? OR raw_message LIKE ?)
          ORDER BY ts DESC LIMIT 1
        """,
            (f'%[{symbol}]%', f'%🔔 {symbol}%', f'%🔔{symbol}%'),
        ).fetchone()
        return int(row[0]) if row else None


def get_last_signal_by_symbol_in_raw(symbol: str) -> dict | None:
    """
    Search for most recent signal containing symbol in raw_message.
    Useful when signal was saved without proper symbol parsing.
    """
    cols = ["id", "raw_message", "ts", "tf", "side", "symbol", "price"]
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, raw_message, ts, tf, side, symbol, price 
            FROM signals 
            WHERE raw_message LIKE ? OR raw_message LIKE ? OR raw_message LIKE ?
            ORDER BY ts DESC LIMIT 1
            """,
            (f'%[{symbol}]%', f'%🔔 {symbol}%', f'%🔔{symbol}%'),
        ).fetchone()
    return dict(zip(cols, row)) if row else None


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
             sl_price, tp_price, leverage, client_order_id, exchange_order_id, env, use_atr)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
          ON CONFLICT(user_id, symbol, account_type) DO UPDATE SET
            side             = excluded.side,
            entry_price      = excluded.entry_price,
            size             = excluded.size,
            timeframe        = COALESCE(excluded.timeframe, active_positions.timeframe),
            signal_id        = COALESCE(excluded.signal_id, active_positions.signal_id),
            -- P0.3: НЕ перезаписываем strategy на NULL
            strategy         = COALESCE(excluded.strategy, active_positions.strategy),
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
            use_atr          = excluded.use_atr
        """,
            (user_id, symbol, account_type, side, entry_price, size, timeframe, signal_id, 
             strategy, source, opened_by, exchange, sl_price, tp_price, leverage, 
             client_order_id, exchange_order_id, env, use_atr_int),
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
    with get_conn() as conn:
        # Build query based on filters
        base_query = """
            SELECT symbol, side, entry_price, size, open_ts, timeframe, signal_id, 
                   COALESCE(dca_10_done, 0), COALESCE(dca_25_done, 0), strategy, account_type,
                   source, opened_by, exchange, sl_price, tp_price, 
                   manual_sltp_override, manual_sltp_ts,
                   atr_activated, atr_activation_price, atr_last_stop_price, atr_last_update_ts,
                   leverage, client_order_id, exchange_order_id, env, COALESCE(use_atr, 0) as use_atr
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
            }
            for r in rows
        ]


def remove_active_position(user_id: int, symbol: str, account_type: str | None = None, entry_price: float | None = None, entry_price_tolerance: float = 0.001):
    """
    Удаляет активную позицию.
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
    """
    import logging
    logger = logging.getLogger(__name__)
    
    with get_conn() as conn:
        # If entry_price is provided, verify it matches before deleting
        if entry_price is not None:
            # First check current entry_price in DB
            if account_type:
                cur = conn.execute(
                    "SELECT entry_price FROM active_positions WHERE user_id=? AND symbol=? AND account_type=?",
                    (user_id, symbol, account_type),
                )
            else:
                cur = conn.execute(
                    "SELECT entry_price FROM active_positions WHERE user_id=? AND symbol=?",
                    (user_id, symbol),
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
        
        # Proceed with deletion
        if account_type:
            conn.execute(
                "DELETE FROM active_positions WHERE user_id=? AND symbol=? AND account_type=?",
                (user_id, symbol, account_type),
            )
        else:
            conn.execute(
                "DELETE FROM active_positions WHERE user_id=? AND symbol=?",
                (user_id, symbol),
            )
        conn.commit()


def set_dca_flag(user_id: int, symbol: str, level: int, value: bool = True, account_type: str = "demo"):
    """
    Устанавливает флаг DCA для позиции.
    level: 10 или 25 (процент)
    """
    col = f"dca_{level}_done"
    if col not in ("dca_10_done", "dca_25_done"):
        raise ValueError(f"Invalid DCA level: {level}")
    with get_conn() as conn:
        conn.execute(
            f"UPDATE active_positions SET {col}=? WHERE user_id=? AND symbol=? AND account_type=?",
            (1 if value else 0, user_id, symbol, account_type),
        )
        conn.commit()


def get_dca_flag(user_id: int, symbol: str, level: int, account_type: str = "demo") -> bool:
    """
    Проверяет, был ли выполнен DCA на данном уровне.
    level: 10 или 25 (процент)
    """
    col = f"dca_{level}_done"
    if col not in ("dca_10_done", "dca_25_done"):
        raise ValueError(f"Invalid DCA level: {level}")
    with get_conn() as conn:
        row = conn.execute(
            f"SELECT {col} FROM active_positions WHERE user_id=? AND symbol=? AND account_type=?",
            (user_id, symbol, account_type),
        ).fetchone()
    return bool(row[0]) if row else False


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


def update_position_strategy(user_id: int, symbol: str, strategy: str, account_type: str = "demo") -> bool:
    """
    Обновляет strategy для существующей позиции.
    Возвращает True если позиция была обновлена, False если не найдена.
    """
    with get_conn() as conn:
        cursor = conn.execute(
            "UPDATE active_positions SET strategy=? WHERE user_id=? AND symbol=? AND account_type=?",
            (strategy, user_id, symbol, account_type),
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
            WHERE user_id=? AND symbol=? AND account_type=?""",
            (1 if atr_activated else 0, atr_activation_price, atr_last_stop_price,
             int(time.time()), user_id, symbol, account_type),
        )
        conn.commit()
        return cursor.rowcount > 0


def get_atr_state(user_id: int, symbol: str, account_type: str = "demo") -> dict | None:
    """
    Получает ATR trailing stop state для позиции.
    Возвращает dict с полями: atr_activated, atr_activation_price, atr_last_stop_price, atr_last_update_ts
    или None если позиция не найдена.
    """
    with get_conn() as conn:
        row = conn.execute(
            """SELECT atr_activated, atr_activation_price, atr_last_stop_price, atr_last_update_ts
            FROM active_positions WHERE user_id=? AND symbol=? AND account_type=?""",
            (user_id, symbol, account_type),
        ).fetchone()
        
        if row:
            return {
                "atr_activated": bool(row[0]) if row[0] else False,
                "atr_activation_price": row[1],
                "atr_last_stop_price": row[2],
                "atr_last_update_ts": row[3],
            }
        return None


def clear_atr_state(user_id: int, symbol: str, account_type: str = "demo") -> bool:
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
            WHERE user_id=? AND symbol=? AND account_type=?""",
            (user_id, symbol, account_type),
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
) -> bool:
    """
    Устанавливает manual_sltp_override=1 и обновляет SL/TP цены.
    После этого бот не будет перезаписывать SL/TP в мониторинге.
    """
    import time
    with get_conn() as conn:
        cursor = conn.execute(
            """UPDATE active_positions SET 
                manual_sltp_override = 1,
                manual_sltp_ts = ?,
                sl_price = COALESCE(?, sl_price),
                tp_price = COALESCE(?, tp_price)
            WHERE user_id=? AND symbol=? AND account_type=?""",
            (int(time.time()), sl_price, tp_price, user_id, symbol, account_type),
        )
        conn.commit()
        return cursor.rowcount > 0


def clear_manual_sltp_override(user_id: int, symbol: str, account_type: str = "demo") -> bool:
    """
    Сбрасывает manual_sltp_override - бот снова может управлять SL/TP.
    """
    with get_conn() as conn:
        cursor = conn.execute(
            """UPDATE active_positions SET 
                manual_sltp_override = 0,
                manual_sltp_ts = NULL
            WHERE user_id=? AND symbol=? AND account_type=?""",
            (user_id, symbol, account_type),
        )
        conn.commit()
        return cursor.rowcount > 0


def is_manual_sltp_override(user_id: int, symbol: str, account_type: str = "demo") -> bool:
    """
    Проверяет, установлен ли manual_sltp_override для позиции.
    Возвращает True если бот не должен трогать SL/TP.
    """
    with get_conn() as conn:
        row = conn.execute(
            "SELECT manual_sltp_override FROM active_positions WHERE user_id=? AND symbol=? AND account_type=?",
            (user_id, symbol, account_type),
        ).fetchone()
        return bool(row[0]) if row and row[0] else False


def update_position_sltp(
    user_id: int,
    symbol: str,
    account_type: str = "demo",
    sl_price: float | None = None,
    tp_price: float | None = None,
    respect_manual_override: bool = True,
) -> bool:
    """
    Обновляет SL/TP цены для позиции.
    Если respect_manual_override=True и manual_sltp_override=1, ничего не делает.
    """
    if respect_manual_override and is_manual_sltp_override(user_id, symbol, account_type):
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
        
        params.extend([user_id, symbol, account_type])
        cursor = conn.execute(
            f"UPDATE active_positions SET {', '.join(updates)} WHERE user_id=? AND symbol=? AND account_type=?",
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
):
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute(
            """
          INSERT OR IGNORE INTO pending_limit_orders
            (user_id, order_id, symbol, side, qty, price, signal_id, created_ts, time_in_force, strategy, account_type)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (user_id, order_id, symbol, side, qty, price, signal_id, created_ts, time_in_force, strategy, account_type),
        )
        conn.commit()

def get_pending_limit_orders(user_id: int) -> list[dict]:
    """
    Возвращает список отложенных лимитных ордеров пользователя,
    отсортированных от новых к старым. Гарантирует наличие ключа
    `time_in_force`, `strategy` и `account_type` (если колонок нет в БД — подставит дефолты).
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
                 WHERE user_id=?
                 ORDER BY created_ts DESC
                """,
                (user_id,),
            ).fetchall()
        elif has_tif and has_strategy:
            rows = conn.execute(
                """
                SELECT order_id, symbol, side, qty, price, signal_id, created_ts, time_in_force, strategy
                  FROM pending_limit_orders
                 WHERE user_id=?
                 ORDER BY created_ts DESC
                """,
                (user_id,),
            ).fetchall()
        elif has_tif:
            rows = conn.execute(
                """
                SELECT order_id, symbol, side, qty, price, signal_id, created_ts, time_in_force
                  FROM pending_limit_orders
                 WHERE user_id=?
                 ORDER BY created_ts DESC
                """,
                (user_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT order_id, symbol, side, qty, price, signal_id, created_ts
                  FROM pending_limit_orders
                 WHERE user_id=?
                 ORDER BY created_ts DESC
                """,
                (user_id,),
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

def remove_pending_limit_order(user_id: int, order_id: str):
    with get_conn() as conn:
        conn.execute(
            """
          DELETE FROM pending_limit_orders
           WHERE user_id=? AND order_id=?
        """,
            (user_id, order_id),
        )
        conn.commit()

# ------------------------------------------------------------------------------------
# Trade logs
# ------------------------------------------------------------------------------------
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
):
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute(
            """
          INSERT INTO trade_logs(
            user_id, signal_id, symbol, side,
            entry_price, exit_price, exit_reason,
            pnl, pnl_pct, signal_source,
            rsi, bb_hi, bb_lo,
            oi_prev, oi_now, oi_chg, vol_from, vol_to, price_chg,
            vol_delta, sl_pct, tp_pct, sl_price, tp_price,
            timeframe, entry_ts, exit_ts, exit_order_type, strategy, account_type
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            ),
        )
        conn.commit()


def get_trade_stats(user_id: int, strategy: str | None = None, period: str = "all", account_type: str | None = None) -> dict:
    """
    Получает статистику сделок пользователя.
    period: 'today', 'week', 'month', 'all'
    strategy: None = все стратегии, иначе конкретная
    account_type: 'demo', 'real', or None = все
    """
    import datetime
    from zoneinfo import ZoneInfo
    
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
        
        # Фильтр по периоду - используем скользящие окна (rolling windows)
        # вместо жёсткой привязки к полуночи
        now = datetime.datetime.now(ZoneInfo("UTC"))
        if period == "today":
            # Последние 24 часа вместо "с полуночи"
            start = now - datetime.timedelta(hours=24)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        elif period == "week":
            # Последние 7 дней
            start = now - datetime.timedelta(days=7)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        elif period == "month":
            # Последние 30 дней
            start = now - datetime.timedelta(days=30)
            where_clauses.append("ts >= ?")
            params.append(start.strftime("%Y-%m-%d %H:%M:%S"))
        
        where_sql = " AND ".join(where_clauses)
        
        # Общая статистика
        # Note: webapp_close is added to EOD category as it's a manual close via webapp
        row = conn.execute(f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN exit_reason IN ('TP', 'TRAILING') OR (exit_reason = 'UNKNOWN' AND pnl > 0) THEN 1 ELSE 0 END) as tp_count,
                SUM(CASE WHEN exit_reason IN ('SL', 'LIQ', 'ADL') OR (exit_reason = 'UNKNOWN' AND pnl < 0) THEN 1 ELSE 0 END) as sl_count,
                SUM(CASE WHEN exit_reason IN ('EOD', 'MANUAL', 'webapp_close') THEN 1 ELSE 0 END) as eod_count,
                SUM(pnl) as total_pnl,
                AVG(pnl_pct) as avg_pnl_pct,
                SUM(CASE WHEN side = 'Buy' THEN 1 ELSE 0 END) as long_count,
                SUM(CASE WHEN side = 'Sell' THEN 1 ELSE 0 END) as short_count,
                SUM(CASE WHEN side = 'Buy' AND pnl > 0 THEN 1 ELSE 0 END) as long_wins,
                SUM(CASE WHEN side = 'Sell' AND pnl > 0 THEN 1 ELSE 0 END) as short_wins,
                SUM(CASE WHEN pnl > 0 THEN pnl ELSE 0 END) as gross_profit,
                SUM(CASE WHEN pnl < 0 THEN pnl ELSE 0 END) as gross_loss,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins
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
        
        open_row = conn.execute(f"""
            SELECT COUNT(*) FROM active_positions
            WHERE {" AND ".join(open_where)}
        """, open_params).fetchone()
        open_count = open_row[0] if open_row else 0
        
        return {
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
        }


def get_trade_logs_list(user_id: int, limit: int = 500, strategy: str = None, 
                        account_type: str = None, exchange: str = None) -> list:
    """
    Get list of trade logs for a user.
    Returns list of dicts with trade data from trade_logs table.
    Used by webapp stats API.
    """
    with get_conn() as conn:
        where_clauses = ["user_id = ?"]
        params = [user_id]
        
        if strategy:
            where_clauses.append("strategy = ?")
            params.append(strategy)
        
        if account_type:
            where_clauses.append("(account_type = ? OR account_type IS NULL)")
            params.append(account_type)
            
        # Exchange filter - check if exchange column exists
        if exchange and _col_exists(conn, "trade_logs", "exchange"):
            where_clauses.append("exchange = ?")
            params.append(exchange)
        
        where_sql = " AND ".join(where_clauses)
        params.append(limit)
        
        cur = conn.execute(f"""
            SELECT id, signal_id, symbol, side, entry_price, exit_price, 
                   exit_reason, pnl, pnl_pct, strategy, account_type, ts
            FROM trade_logs
            WHERE {where_sql}
            ORDER BY ts DESC
            LIMIT ?
        """, params)
        
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
                "strategy": row[9],
                "account_type": row[10],
                "time": row[11],
                "exchange": "bybit",  # Default, can be expanded later
            })
        return result


def get_trade_stats_unknown(user_id: int, period: str = "all", account_type: str | None = None) -> dict:
    """Get stats for trades with NULL/unknown strategy."""
    import datetime
    from zoneinfo import ZoneInfo
    
    with get_conn() as conn:
        where_clauses = ["user_id = ?", "strategy IS NULL"]
        params: list = [user_id]
        
        if account_type:
            where_clauses.append("(account_type = ? OR account_type IS NULL)")
            params.append(account_type)
        
        now = datetime.datetime.now(ZoneInfo("UTC"))
        if period == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
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


def get_stats_by_strategy(user_id: int, period: str = "all", account_type: str | None = None) -> dict[str, dict]:
    """Возвращает статистику по каждой стратегии отдельно."""
    strategies = ["oi", "rsi_bb", "scryptomera", "scalper", "elcaro", "fibonacci"]
    result = {}
    for strat in strategies:
        stats = get_trade_stats(user_id, strategy=strat, period=period, account_type=account_type)
        if stats["total"] > 0:
            result[strat] = stats
    
    # Add unknown/manual trades
    unknown_stats = get_trade_stats_unknown(user_id, period=period, account_type=account_type)
    if unknown_stats["total"] > 0:
        result["manual"] = unknown_stats
    
    # Общая статистика
    result["all"] = get_trade_stats(user_id, strategy=None, period=period, account_type=account_type)
    return result


# =====================================================
# LICENSING SYSTEM FUNCTIONS
# =====================================================

# License types and their capabilities
LICENSE_TYPES = {
    "premium": {
        "name": "Premium",
        "demo_access": True,
        "real_access": True,
        "all_strategies": True,
        "strategies": ["oi", "rsi_bb", "scryptomera", "scalper", "elcaro", "fibonacci", "spot"],
    },
    "basic": {
        "name": "Basic", 
        "demo_access": True,
        "real_access": True,
        "all_strategies": False,
        "strategies": ["oi", "rsi_bb", "scryptomera", "scalper"],  # No elcaro, fibonacci, spot
    },
    "trial": {
        "name": "Trial",
        "demo_access": True,
        "real_access": False,  # Demo only
        "all_strategies": True,
        "strategies": ["oi", "rsi_bb", "scryptomera", "scalper", "elcaro", "fibonacci", "spot"],
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
            # License expired, update to none
            conn.execute(
                "UPDATE users SET current_license = 'none', license_expires = NULL WHERE user_id = ?",
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'completed', ?)
        """, (user_id, license_id, payment_type, amount, currency, license_type, period_days, telegram_charge_id, now))
        
        # Update quick access columns
        conn.execute(
            "UPDATE users SET current_license = ?, license_expires = ? WHERE user_id = ?",
            (license_type, new_end, user_id)
        )
        
        conn.commit()
        invalidate_user_cache(user_id)
        
        return {
            "success": True,
            "license_id": license_id,
            "license_type": license_type,
            "expires": new_end,
            "days": period_days,
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
            VALUES (?, 'admin_grant', 0, 'FREE', ?, ?, 'completed', ?, ?)
        """, (user_id, current["license_type"], days, now, json.dumps({"action": "extend", "admin_id": admin_id, "notes": notes})))
        
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
            VALUES (?, 'admin_grant', 0, 'FREE', 'none', 0, 'completed', ?, ?)
        """, (user_id, now, json.dumps({"action": "revoke", "admin_id": admin_id, "reason": reason})))
        
        # Clear quick access
        conn.execute(
            "UPDATE users SET current_license = 'none', license_expires = NULL WHERE user_id = ?",
            (user_id,)
        )
        
        conn.commit()
        invalidate_user_cache(user_id)
    
    return {"success": True, "message": "License revoked"}


def check_license_access(user_id: int, feature: str, account_type: str = "demo") -> dict:
    """
    Check if user has access to a specific feature.
    
    Args:
        user_id: User ID
        feature: Feature name ('trading', 'strategy_oi', 'strategy_rsi_bb', etc.)
        account_type: 'demo' or 'real'
    
    Returns:
        {"allowed": bool, "reason": str}
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
    
    # Check strategy access
    if feature.startswith("strategy_"):
        strategy = feature.replace("strategy_", "")
        
        # On real account, Basic users are limited
        if account_type == "real" and license_type == "basic":
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
    """
    license_info = get_user_license(user_id)
    
    if not license_info["is_active"]:
        return []
    
    caps = license_info["capabilities"]
    
    # Check if user can trade on this account type
    if account_type == "real" and not caps["real_access"]:
        return []
    if account_type == "demo" and not caps["demo_access"]:
        return []
    
    # For Basic on real account, return limited strategies
    if account_type == "real" and license_info["license_type"] == "basic":
        return caps["strategies"]
    
    # For Premium, Trial on demo, or Basic on demo - all strategies
    return ["oi", "rsi_bb", "scryptomera", "scalper", "elcaro"]


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
        except sqlite3.IntegrityError:
            return {"error": "Promo code already exists"}


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
        positions_count = conn.execute(
            "SELECT COUNT(*) FROM active_positions WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]
        
        # Count trade logs
        trades_count = conn.execute(
            "SELECT COUNT(*) FROM trade_logs WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]
        
        # Calculate total PnL
        pnl_row = conn.execute(
            "SELECT SUM(pnl), COUNT(CASE WHEN pnl > 0 THEN 1 END) FROM trade_logs WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        total_pnl = pnl_row[0] or 0.0
        wins = pnl_row[1] or 0
        
        # Payment history count
        payments_count = conn.execute(
            "SELECT COUNT(*) FROM payment_history WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]
        
        # Total payments amount
        total_paid = conn.execute(
            "SELECT SUM(amount) FROM payment_history WHERE user_id = ? AND status = 'completed' AND currency = 'XTR'",
            (user_id,)
        ).fetchone()[0] or 0
        
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
        if filter_type == "active":
            where = "is_allowed = 1 AND is_banned = 0"
        elif filter_type == "banned":
            where = "is_banned = 1"
        elif filter_type == "premium":
            where = f"current_license = 'premium' AND license_expires > {now}"
        elif filter_type == "basic":
            where = f"current_license = 'basic' AND license_expires > {now}"
        elif filter_type == "trial":
            where = f"current_license = 'trial' AND license_expires > {now}"
        elif filter_type == "no_license":
            where = f"(current_license = 'none' OR current_license IS NULL OR license_expires <= {now})"
        
        # Get total count
        total = conn.execute(f"SELECT COUNT(*) FROM users WHERE {where}").fetchone()[0]
        
        # Get page data
        offset = page * per_page
        rows = conn.execute(f"""
            SELECT user_id, is_allowed, is_banned, current_license, license_expires, last_seen_ts
            FROM users
            WHERE {where}
            ORDER BY last_seen_ts DESC NULLS LAST
            LIMIT ? OFFSET ?
        """, (per_page, offset)).fetchall()
        
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
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
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
        
        total = conn.execute(f"SELECT COUNT(*) FROM payment_history WHERE {where}", params).fetchone()[0]
        
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
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
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


def get_user_usage_report(user_id: int) -> dict:
    """Get detailed usage report for a specific user."""
    with get_conn() as conn:
        # Trade stats by account type
        demo_stats = get_trade_stats(user_id, account_type="demo")
        real_stats = get_trade_stats(user_id, account_type="real")
        
        # Strategy breakdown
        strategies = ["oi", "rsi_bb", "scryptomera", "scalper", "elcaro", "fibonacci"]
        strategy_stats = {}
        for strat in strategies:
            stats = get_trade_stats(user_id, strategy=strat)
            if stats["total"] > 0:
                strategy_stats[strat] = stats
        
        # Demo by strategy
        demo_by_strat = {}
        for strat in strategies:
            stats = get_trade_stats(user_id, strategy=strat, account_type="demo")
            if stats["total"] > 0:
                demo_by_strat[strat] = stats
        
        # Real by strategy
        real_by_strat = {}
        for strat in strategies:
            stats = get_trade_stats(user_id, strategy=strat, account_type="real")
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
        private_key = creds.get("hl_private_key", private_key)
        vault_address = creds.get("hl_vault_address", vault_address)
        testnet = creds.get("hl_testnet", testnet)
        wallet_address = creds.get("hl_wallet_address")
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
                    hl_testnet = 1,
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
                    hl_testnet = 0,
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
            "UPDATE users SET hl_enabled = ? WHERE user_id = ?",
            (1 if enabled else 0, user_id)
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
                    hl_testnet = 0,
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
            "SELECT exchange_mode FROM users WHERE user_id = ?", 
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
            "UPDATE users SET exchange_mode = ? WHERE user_id = ?",
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
            "configured": bool(hl_creds.get("hl_private_key") or hl_creds.get("hl_wallet_address")),
            "testnet": hl_creds.get("hl_testnet", False),
            "wallet": hl_creds.get("hl_wallet_address"),
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


def get_active_trading_strategies(user_id: int) -> list:
    """
    Get all active strategies for live trading.
    Includes: system strategies (elcaro, fibonacci, etc.) and custom/purchased strategies.
    Used by bot to determine which strategies to process signals for.
    """
    import json
    
    active_strategies = []
    cfg = get_user_config(user_id)
    
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
            strat_settings = get_strategy_settings(user_id, strat_name)
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
                    except:
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
    Get trade history for a user from the trades table.
    Returns list of dicts with trade data.
    """
    with get_conn() as conn:
        # Check if trades table exists
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='trades'"
        )
        if not cur.fetchone():
            return []
        
        if exchange:
            cur = conn.execute(
                """SELECT id, symbol, side, entry_price, exit_price, size, 
                          pnl, pnl_percent, exchange, strategy, created_at, closed_at
                   FROM trades 
                   WHERE user_id = ? AND exchange = ?
                   ORDER BY created_at DESC LIMIT ?""",
                (user_id, exchange, limit)
            )
        else:
            cur = conn.execute(
                """SELECT id, symbol, side, entry_price, exit_price, size, 
                          pnl, pnl_percent, exchange, strategy, created_at, closed_at
                   FROM trades 
                   WHERE user_id = ?
                   ORDER BY created_at DESC LIMIT ?""",
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
                "size": row[5],
                "pnl": row[6],
                "pnl_percent": row[7],
                "exchange": row[8],
                "strategy": row[9],
                "time": row[10],  # created_at as "time" for compatibility
                "created_at": row[10],
                "closed_at": row[11]
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
        # Ensure table exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                symbol TEXT,
                side TEXT,
                entry_price REAL,
                exit_price REAL,
                size REAL,
                pnl REAL,
                pnl_percent REAL,
                exchange TEXT DEFAULT 'bybit',
                strategy TEXT,
                created_at INTEGER,
                closed_at INTEGER
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

def add_payment_record(
    user_id: int,
    plan: str,
    period: str,
    amount: float,
    payment_method: str,
    wallet_address: str = None,
    transaction_hash: str = None
):
    """Record a payment transaction"""
    import time
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO payment_history (
                user_id, amount, payment_method, plan_type, 
                transaction_id, created_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            amount,
            payment_method,
            f"{plan}_{period}",
            transaction_hash or f"manual_{int(time.time())}",
            int(time.time()),
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


def get_user_payments(user_id: int, limit: int = 50) -> list:
    """Get user's payment history"""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT 
                amount, payment_method, plan_type, 
                transaction_id, created_at, status
            FROM payment_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit)).fetchall()
        
        return [
            {
                "amount": r[0],
                "method": r[1],
                "plan": r[2],
                "transaction_id": r[3],
                "date": r[4],
                "status": r[5]
            }
            for r in rows
        ]


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

