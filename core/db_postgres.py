"""
PostgreSQL Sync Database Layer for Enliko Trading Platform
==========================================================
Drop-in replacement for SQLite db.py functions using psycopg2.

Usage:
    Set USE_POSTGRES=1 in environment to switch from SQLite.
"""

import os
import psycopg2
import psycopg2.extras
import psycopg2.pool
import threading
import logging
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)

# Connection pool
_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
_pool_lock = threading.Lock()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://elcaro:elcaro_prod_2026@127.0.0.1:5432/elcaro"
)


def get_pool() -> psycopg2.pool.ThreadedConnectionPool:
    """Get or create PostgreSQL connection pool"""
    global _pool
    
    if _pool is not None:
        return _pool
    
    with _pool_lock:
        if _pool is not None:
            return _pool
        
        logger.info(f"Creating PostgreSQL connection pool...")
        _pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=5,
            maxconn=50,
            dsn=DATABASE_URL
        )
        logger.info("PostgreSQL connection pool created")
        return _pool


def _sqlite_to_pg(query: str) -> str:
    """Convert SQLite query syntax to PostgreSQL.
    
    Conversions:
    - ? placeholders → %s
    - INSERT OR IGNORE → INSERT ... ON CONFLICT DO NOTHING
    - INSERT OR REPLACE → INSERT ... ON CONFLICT DO UPDATE
    - datetime('now') → NOW()
    - AUTOINCREMENT → SERIAL (handled in schema)
    """
    import re
    
    # Convert ? placeholders to %s
    query = query.replace('?', '%s')
    
    # Convert INSERT OR IGNORE to PostgreSQL syntax
    # Pattern: INSERT OR IGNORE INTO table(cols) VALUES(vals)
    if 'INSERT OR IGNORE' in query.upper():
        query = re.sub(
            r'INSERT\s+OR\s+IGNORE\s+INTO\s+(\w+)',
            r'INSERT INTO \1',
            query,
            flags=re.IGNORECASE
        )
        # Add ON CONFLICT DO NOTHING before the end
        if 'ON CONFLICT' not in query.upper():
            # Find the right place to add ON CONFLICT
            query = query.rstrip().rstrip(';') + ' ON CONFLICT DO NOTHING'
    
    # Convert INSERT OR REPLACE to PostgreSQL UPSERT
    if 'INSERT OR REPLACE' in query.upper():
        query = re.sub(
            r'INSERT\s+OR\s+REPLACE\s+INTO',
            r'INSERT INTO',
            query,
            flags=re.IGNORECASE
        )
        # Note: Full UPSERT requires knowing the conflict target
        # For now, handled case by case in specific functions
    
    # Convert datetime functions - handle both single and double quotes
    query = re.sub(r"datetime\s*\(\s*['\"]now['\"]\s*\)", 'NOW()', query, flags=re.IGNORECASE)
    query = re.sub(r"CURRENT_TIMESTAMP", 'NOW()', query, flags=re.IGNORECASE)
    
    # Convert strftime to PostgreSQL extract
    # strftime('%s', col) → EXTRACT(EPOCH FROM col)::INTEGER
    query = re.sub(
        r"CAST\s*\(\s*strftime\s*\(\s*'%s'\s*,\s*(\w+)\s*\)\s*AS\s+INTEGER\s*\)",
        r"EXTRACT(EPOCH FROM \1)::INTEGER",
        query,
        flags=re.IGNORECASE
    )
    
    return query


class SQLiteCompatCursor:
    """Cursor wrapper that provides SQLite-compatible interface for PostgreSQL."""
    
    def __init__(self, pg_cursor):
        self._cursor = pg_cursor
        self.lastrowid = None
        self.rowcount = 0
        self.description = None
    
    def execute(self, query: str, params: tuple = None):
        """Execute query with automatic SQLite→PostgreSQL conversion."""
        pg_query = _sqlite_to_pg(query)
        
        # Handle RETURNING id for INSERT statements - but only for tables with 'id' column
        # Skip for tables with composite primary keys: active_positions, user_strategy_settings
        tables_without_id = ['active_positions', 'user_strategy_settings', 'pending_limit_orders']
        has_id_column = True
        for table in tables_without_id:
            if table.lower() in pg_query.lower():
                has_id_column = False
                break
        
        if has_id_column and 'INSERT' in pg_query.upper() and 'RETURNING' not in pg_query.upper():
            # Check if it's not ON CONFLICT DO NOTHING (which might not insert)
            if 'ON CONFLICT DO NOTHING' not in pg_query.upper():
                pg_query = pg_query.rstrip().rstrip(';') + ' RETURNING id'
        
        try:
            self._cursor.execute(pg_query, params)
            self.rowcount = self._cursor.rowcount
            self.description = self._cursor.description
            
            # Get lastrowid for INSERT
            if 'RETURNING' in pg_query.upper() and self._cursor.description:
                row = self._cursor.fetchone()
                if row:
                    self.lastrowid = row[0]
        except Exception as e:
            # Retry without RETURNING if it fails (rollback current transaction first)
            if 'RETURNING' in pg_query:
                try:
                    self._cursor.connection.rollback()
                except Exception as rollback_err:
                    logger.warning(f"Rollback failed during RETURNING retry: {rollback_err}")
                pg_query_no_returning = pg_query.replace(' RETURNING id', '')
                self._cursor.execute(pg_query_no_returning, params)
                self.rowcount = self._cursor.rowcount
                self.description = self._cursor.description
            else:
                raise
        
        return self
    
    def executemany(self, query: str, params_list):
        """Execute query multiple times with different params."""
        pg_query = _sqlite_to_pg(query)
        self._cursor.executemany(pg_query, params_list)
        self.rowcount = self._cursor.rowcount
        return self
    
    def fetchone(self):
        """Fetch one row."""
        return self._cursor.fetchone()
    
    def fetchall(self):
        """Fetch all rows."""
        return self._cursor.fetchall()
    
    def fetchmany(self, size=None):
        """Fetch many rows."""
        if size:
            return self._cursor.fetchmany(size)
        return self._cursor.fetchmany()
    
    def close(self):
        """Close cursor."""
        self._cursor.close()
    
    def __iter__(self):
        return iter(self._cursor)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


class SQLiteCompatConnection:
    """Connection wrapper that provides SQLite-compatible interface for PostgreSQL.
    
    This allows existing SQLite code to work with PostgreSQL without changes.
    Usage: conn.execute("SELECT * FROM users WHERE id=?", (uid,))
    """
    
    def __init__(self, pg_conn):
        self._conn = pg_conn
        self._cursor = None
    
    def cursor(self, *args, **kwargs):
        """Get a cursor."""
        pg_cursor = self._conn.cursor(*args, **kwargs)
        return SQLiteCompatCursor(pg_cursor)
    
    def execute(self, query: str, params: tuple = None):
        """Execute query directly on connection (SQLite style)."""
        if self._cursor is None:
            self._cursor = SQLiteCompatCursor(self._conn.cursor())
        return self._cursor.execute(query, params)
    
    def executemany(self, query: str, params_list):
        """Execute query multiple times."""
        if self._cursor is None:
            self._cursor = SQLiteCompatCursor(self._conn.cursor())
        return self._cursor.executemany(query, params_list)
    
    def commit(self):
        """Commit transaction."""
        self._conn.commit()
    
    def rollback(self):
        """Rollback transaction."""
        self._conn.rollback()
    
    def close(self):
        """Close connection - returns to pool if pool reference exists."""
        if self._cursor:
            self._cursor.close()
        # If we have a pool reference, return connection to pool instead of closing
        if hasattr(self, '_pool') and self._pool:
            self._pool.putconn(self._conn)
        else:
            self._conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()


@contextmanager
def get_conn():
    """Get connection from pool with automatic return.
    
    Returns SQLiteCompatConnection for backward compatibility with
    existing db.py code that uses conn.execute("...?...", (param,))
    """
    pool = get_pool()
    pg_conn = pool.getconn()
    conn = SQLiteCompatConnection(pg_conn)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(pg_conn)


def execute(query: str, params: tuple = None) -> List[Dict]:
    """Execute query and return results as list of dicts.
    
    ВАЖНО: Автоматически делает commit для INSERT/UPDATE/DELETE запросов!
    """
    pool = get_pool()
    pg_conn = pool.getconn()
    try:
        with pg_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Convert SQLite style query to PostgreSQL
            pg_query = _sqlite_to_pg(query)
            cur.execute(pg_query, params)
            
            # Check if this is a write operation that needs commit
            query_upper = query.strip().upper()
            if query_upper.startswith(('INSERT', 'UPDATE', 'DELETE', 'UPSERT')):
                pg_conn.commit()
                logger.debug(f"execute() committed write operation: {query[:50]}...")
            
            if cur.description:
                return [dict(row) for row in cur.fetchall()]
            return []
    except Exception as e:
        pg_conn.rollback()
        logger.error(f"execute() error: {e}, query: {query[:100]}")
        raise
    finally:
        pool.putconn(pg_conn)


def execute_one(query: str, params: tuple = None) -> Optional[Dict]:
    """Execute query and return single result"""
    results = execute(query, params)
    return results[0] if results else None


def execute_scalar(query: str, params: tuple = None) -> Any:
    """Execute query and return single value"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            row = cur.fetchone()
            return row[0] if row else None


def execute_write(query: str, params: tuple = None) -> int:
    """Execute INSERT/UPDATE/DELETE and return affected rows"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.rowcount


def pg_init_db():
    """Initialize PostgreSQL database schema.
    
    NOTE: If unified migration (100_unified_schema.py) was applied, this function 
    just verifies the schema exists and doesn't try to create/modify tables.
    """
    logger.info("🐘 Initializing PostgreSQL database schema...")
    
    with get_conn() as conn:
        cur = conn.cursor()
        
        # Check if unified migration was applied
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM _migrations WHERE version = '100'
            )
        """)
        unified_migration_applied = cur.fetchone()[0]
        
        if unified_migration_applied:
            logger.info("✅ Unified migration already applied - skipping schema creation")
            # Just verify core tables exist
            cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'users'")
            if cur.fetchone()[0] > 0:
                logger.info("✅ Database schema verified")
                conn.commit()
                return
            else:
                logger.error("❌ Unified migration applied but users table missing!")
        
        logger.info("📝 Creating database schema (no unified migration found)...")
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # USERS TABLE
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id            BIGINT PRIMARY KEY,
                api_key            TEXT,
                api_secret         TEXT,
                
                -- Demo/Real API keys
                demo_api_key       TEXT,
                demo_api_secret    TEXT,
                real_api_key       TEXT,
                real_api_secret    TEXT,
                trading_mode       TEXT NOT NULL DEFAULT 'demo',
                
                -- Trading settings (NEW DEFAULTS: SL 30%, TP 10%, ATR enabled)
                percent            REAL NOT NULL DEFAULT 1.0,
                coins              TEXT NOT NULL DEFAULT 'ALL',
                limit_enabled      INTEGER NOT NULL DEFAULT 1,
                trade_oi           INTEGER NOT NULL DEFAULT 1,
                trade_rsi_bb       INTEGER NOT NULL DEFAULT 1,
                tp_percent         REAL NOT NULL DEFAULT 10.0,
                sl_percent         REAL NOT NULL DEFAULT 30.0,
                use_atr            INTEGER NOT NULL DEFAULT 1,
                lang               TEXT NOT NULL DEFAULT 'en',
                leverage           INTEGER NOT NULL DEFAULT 10,
                
                -- Strategies
                trade_scryptomera  INTEGER NOT NULL DEFAULT 0,
                trade_scalper      INTEGER NOT NULL DEFAULT 0,
                trade_elcaro       INTEGER NOT NULL DEFAULT 0,
                trade_fibonacci    INTEGER NOT NULL DEFAULT 0,
                trade_manual       INTEGER NOT NULL DEFAULT 1,
                strategy_settings  TEXT,
                strategies_enabled TEXT,  -- CSV list of enabled strategies
                strategies_order   TEXT,  -- CSV list of strategy execution order
                
                -- Strategy thresholds
                rsi_lo             REAL,
                rsi_hi             REAL,
                bb_touch_k         REAL,
                oi_min_pct         REAL,
                price_min_pct      REAL,
                limit_only_default INTEGER NOT NULL DEFAULT 0,
                
                -- DCA settings
                dca_enabled        INTEGER NOT NULL DEFAULT 0,
                dca_pct_1          REAL NOT NULL DEFAULT 10.0,
                dca_pct_2          REAL NOT NULL DEFAULT 25.0,
                
                -- Access control
                is_allowed         INTEGER NOT NULL DEFAULT 0,
                is_banned          INTEGER NOT NULL DEFAULT 0,
                terms_accepted     INTEGER NOT NULL DEFAULT 0,
                guide_sent         INTEGER NOT NULL DEFAULT 0,
                
                -- HyperLiquid
                hl_enabled         BOOLEAN DEFAULT FALSE,
                hl_testnet         BOOLEAN DEFAULT FALSE,
                hl_private_key     TEXT,
                hl_wallet_address  TEXT,
                hl_vault_address   TEXT,
                hl_testnet_private_key     TEXT,
                hl_testnet_wallet_address  TEXT,
                hl_mainnet_private_key     TEXT,
                hl_mainnet_wallet_address  TEXT,
                
                -- Bybit
                bybit_enabled      INTEGER NOT NULL DEFAULT 1,
                exchange_type      TEXT NOT NULL DEFAULT 'bybit',
                exchange_mode      TEXT NOT NULL DEFAULT 'bybit',
                
                -- ATR settings
                atr_periods        INTEGER NOT NULL DEFAULT 7,
                atr_multiplier_sl  REAL NOT NULL DEFAULT 1.0,
                atr_trigger_pct    REAL NOT NULL DEFAULT 2.0,
                atr_step_pct       REAL NOT NULL DEFAULT 0.5,
                direction          TEXT NOT NULL DEFAULT 'all',
                global_order_type  TEXT NOT NULL DEFAULT 'market',
                
                -- Routing
                routing_policy     TEXT DEFAULT 'same_exchange_all_envs',
                live_enabled       INTEGER DEFAULT 0,
                
                -- License
                current_license    TEXT DEFAULT 'none',
                license_expires    BIGINT,
                license_type       TEXT,  -- Type of license (trial, basic, pro, etc.)
                
                -- ELC Token
                elc_balance        REAL NOT NULL DEFAULT 0.0,
                elc_staked         REAL NOT NULL DEFAULT 0.0,
                elc_locked         REAL NOT NULL DEFAULT 0.0,
                
                -- User info
                username           TEXT,
                first_name         TEXT,
                last_name          TEXT,
                referral_code      TEXT,
                referred_by        BIGINT,
                
                -- Spot trading
                spot_enabled       INTEGER NOT NULL DEFAULT 0,
                spot_settings      TEXT,
                
                -- Limit ladder
                limit_ladder_enabled  INTEGER NOT NULL DEFAULT 0,
                limit_ladder_count    INTEGER NOT NULL DEFAULT 3,
                limit_ladder_settings TEXT,
                
                -- Timestamps
                first_seen_ts      BIGINT,
                last_seen_ts       BIGINT,
                updated_at         TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # SIGNALS TABLE
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id          SERIAL PRIMARY KEY,
                raw_message TEXT,
                ts          TIMESTAMP NOT NULL DEFAULT NOW(),
                tf          TEXT,
                side        TEXT,
                symbol      TEXT,
                price       REAL,
                strategy    TEXT,
                entry_price REAL,
                sl_price    REAL,
                tp_price    REAL,
                timeframe   TEXT,
                raw_json    TEXT,
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
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_signals_symbol_ts ON signals(symbol, ts DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_signals_tf_ts ON signals(tf, ts DESC)")
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # ACTIVE POSITIONS TABLE
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS active_positions (
                user_id      BIGINT NOT NULL,
                symbol       TEXT NOT NULL,
                account_type TEXT NOT NULL DEFAULT 'demo',
                side         TEXT,
                entry_price  REAL,
                size         REAL,
                open_ts      TIMESTAMP NOT NULL DEFAULT NOW(),
                timeframe    TEXT,
                signal_id    INTEGER,
                dca_10_done  INTEGER NOT NULL DEFAULT 0,
                dca_25_done  INTEGER NOT NULL DEFAULT 0,
                strategy     TEXT,
                leverage     INTEGER,
                sl_price     REAL,
                tp_price     REAL,
                exchange     TEXT DEFAULT 'bybit',
                env          TEXT,
                source       TEXT DEFAULT 'bot',
                opened_by    TEXT DEFAULT 'bot',
                manual_sltp_override INTEGER DEFAULT 0,
                manual_sltp_ts       BIGINT,
                atr_activated        INTEGER DEFAULT 0,
                atr_activation_price REAL,
                atr_last_stop_price  REAL,
                atr_last_update_ts   BIGINT,
                use_atr              INTEGER DEFAULT 0,
                applied_sl_pct       REAL,
                applied_tp_pct       REAL,
                client_order_id      TEXT,
                exchange_order_id    TEXT,
                ptp_step_1_done      INTEGER NOT NULL DEFAULT 0,
                ptp_step_2_done      INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(user_id, symbol, account_type)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_active_user ON active_positions(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_active_account ON active_positions(user_id, account_type)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_active_exchange ON active_positions(user_id, exchange, account_type)")
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # TRADE LOGS TABLE
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS trade_logs (
                id              SERIAL PRIMARY KEY,
                user_id         BIGINT NOT NULL,
                signal_id       INTEGER,
                symbol          TEXT,
                side            TEXT,
                entry_price     REAL,
                exit_price      REAL,
                exit_reason     TEXT,
                pnl             REAL,
                pnl_pct         REAL,
                ts              TIMESTAMP NOT NULL DEFAULT NOW(),
                signal_source   TEXT,
                strategy        TEXT,
                account_type    TEXT DEFAULT 'demo',
                exchange        TEXT DEFAULT 'bybit',
                sl_pct          REAL,
                tp_pct          REAL,
                sl_price        REAL,
                tp_price        REAL,
                timeframe       TEXT,
                entry_ts        BIGINT,
                exit_ts         BIGINT,
                exit_order_type TEXT,
                fee             REAL DEFAULT 0
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_logs_user_ts ON trade_logs(user_id, ts DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_logs_symbol_ts ON trade_logs(symbol, ts DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_logs_strategy ON trade_logs(user_id, strategy)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_logs_account_type ON trade_logs(user_id, account_type)")
        
        # Add fee column to existing trade_logs if missing
        cur.execute("ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS fee REAL DEFAULT 0")
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # USER STRATEGY SETTINGS TABLE (SIMPLIFIED - Only LONG/SHORT per strategy)
        # ═══════════════════════════════════════════════════════════════════════════════════
        # Each strategy has LONG and SHORT settings independently
        # No complex fallback - settings are stored with defaults from ENV
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_strategy_settings (
                user_id         BIGINT NOT NULL,
                strategy        TEXT NOT NULL,
                side            TEXT NOT NULL,  -- 'long' or 'short'
                
                -- Strategy enabled
                enabled         BOOLEAN DEFAULT TRUE,
                
                -- Trading parameters
                percent         REAL NOT NULL,          -- Entry % (risk per trade)
                sl_percent      REAL NOT NULL,          -- Stop-Loss %
                tp_percent      REAL NOT NULL,          -- Take-Profit %
                leverage        INTEGER NOT NULL,       -- Leverage
                
                -- ATR Trailing parameters
                use_atr         BOOLEAN DEFAULT FALSE,  -- ATR Trailing disabled by default
                atr_trigger_pct REAL NOT NULL,          -- Trigger % (profit to activate)
                atr_step_pct    REAL NOT NULL,          -- Step % (SL distance from price)
                
                -- Order type and limit offset
                order_type      TEXT DEFAULT 'market',  -- 'market' or 'limit'
                limit_offset_pct REAL DEFAULT 0.1,      -- Limit order offset %
                
                -- DCA settings
                dca_enabled     BOOLEAN DEFAULT FALSE,  -- DCA disabled by default
                dca_pct_1       REAL DEFAULT 10.0,      -- First DCA level %
                dca_pct_2       REAL DEFAULT 25.0,      -- Second DCA level %
                
                -- Position limits and coins filter
                max_positions   INTEGER DEFAULT 0,      -- 0 = unlimited
                coins_group     TEXT DEFAULT 'ALL',     -- ALL, TOP100, VOLATILE
                
                -- Timestamps
                created_at      TIMESTAMP DEFAULT NOW(),
                updated_at      TIMESTAMP DEFAULT NOW(),
                
                PRIMARY KEY(user_id, strategy, side)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_uss_user ON user_strategy_settings(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_uss_strategy ON user_strategy_settings(strategy)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_uss_user_strategy ON user_strategy_settings(user_id, strategy)")
        
        # Add new columns to existing table (for migration)
        for col, col_def in [
            ("limit_offset_pct", "REAL DEFAULT 0.1"),
            ("dca_enabled", "BOOLEAN DEFAULT FALSE"),
            ("dca_pct_1", "REAL DEFAULT 10.0"),
            ("dca_pct_2", "REAL DEFAULT 25.0"),
            ("max_positions", "INTEGER DEFAULT 0"),
            ("coins_group", "TEXT DEFAULT 'ALL'"),
            ("trading_mode", "TEXT DEFAULT 'demo'"),  # Strategy-level trading mode
            ("exchange", "TEXT DEFAULT 'bybit'"),     # Multitenancy: bybit or hyperliquid
            ("account_type", "TEXT DEFAULT 'demo'"),  # Multitenancy: demo/real/testnet/mainnet
            ("direction", "TEXT DEFAULT 'all'"),      # Direction filter: all/long/short
        ]:
            try:
                cur.execute(f"ALTER TABLE user_strategy_settings ADD COLUMN IF NOT EXISTS {col} {col_def}")
            except Exception:
                pass  # Column already exists
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # PENDING LIMIT ORDERS TABLE
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pending_limit_orders (
                user_id       BIGINT NOT NULL,
                order_id      TEXT NOT NULL,
                symbol        TEXT NOT NULL,
                side          TEXT NOT NULL,
                qty           REAL NOT NULL,
                price         REAL NOT NULL,
                signal_id     INTEGER NOT NULL,
                created_ts    BIGINT NOT NULL,
                time_in_force TEXT NOT NULL DEFAULT 'GTC',
                strategy      TEXT,
                account_type  TEXT DEFAULT 'demo',
                PRIMARY KEY(user_id, order_id)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pending_user_created ON pending_limit_orders(user_id, created_ts DESC)")
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # USER LICENSES TABLE
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_licenses (
                id              SERIAL PRIMARY KEY,
                user_id         BIGINT NOT NULL,
                license_type    TEXT NOT NULL,
                start_date      BIGINT NOT NULL,
                end_date        BIGINT NOT NULL,
                is_active       INTEGER NOT NULL DEFAULT 1,
                created_at      BIGINT NOT NULL,
                updated_at      BIGINT,
                created_by      BIGINT,
                notes           TEXT
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_licenses_user ON user_licenses(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_licenses_active ON user_licenses(is_active, end_date)")
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # PROMO CODES TABLE
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS promo_codes (
                id              SERIAL PRIMARY KEY,
                code            TEXT NOT NULL UNIQUE,
                license_type    TEXT NOT NULL,
                period_days     INTEGER NOT NULL,
                max_uses        INTEGER DEFAULT 1,
                current_uses    INTEGER NOT NULL DEFAULT 0,
                is_active       INTEGER NOT NULL DEFAULT 1,
                valid_until     BIGINT,
                created_at      BIGINT NOT NULL,
                created_by      BIGINT,
                notes           TEXT
            )
        """)
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # EXCHANGE ACCOUNTS TABLE
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS exchange_accounts (
                id              SERIAL PRIMARY KEY,
                user_id         BIGINT NOT NULL,
                exchange        TEXT NOT NULL,
                account_type    TEXT NOT NULL,
                label           TEXT,
                is_enabled      INTEGER DEFAULT 1,
                is_default      INTEGER DEFAULT 0,
                api_key         TEXT,
                api_secret      TEXT,
                extra_json      TEXT,
                max_positions   INTEGER DEFAULT 10,
                max_leverage    INTEGER DEFAULT 100,
                risk_limit_pct  REAL DEFAULT 30.0,
                priority        INTEGER DEFAULT 0,
                created_at      TIMESTAMP DEFAULT NOW(),
                updated_at      TIMESTAMP DEFAULT NOW(),
                last_sync_at    TIMESTAMP,
                UNIQUE(user_id, exchange, account_type)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_exch_accounts_user ON exchange_accounts(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_exch_accounts_enabled ON exchange_accounts(user_id, is_enabled)")
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # CUSTOM STRATEGIES TABLE
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS custom_strategies (
                id              SERIAL PRIMARY KEY,
                user_id         BIGINT NOT NULL,
                name            TEXT NOT NULL,
                description     TEXT,
                base_strategy   TEXT DEFAULT 'custom',
                config_json     TEXT NOT NULL,
                is_public       INTEGER DEFAULT 0,
                is_active       INTEGER DEFAULT 1,
                win_rate        REAL DEFAULT 0,
                total_pnl       REAL DEFAULT 0,
                total_trades    INTEGER DEFAULT 0,
                backtest_score  REAL DEFAULT 0,
                performance_stats TEXT,
                created_at      BIGINT NOT NULL,
                updated_at      BIGINT
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_strategies_user ON custom_strategies(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_strategies_public ON custom_strategies(is_public, is_active)")
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # META TABLE (key-value storage)
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS meta (
                key   TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # PYRAMIDS TABLE
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pyramids (
                user_id   BIGINT NOT NULL,
                symbol    TEXT NOT NULL,
                side      TEXT,
                count     INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(user_id, symbol)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pyramids_user ON pyramids(user_id)")
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # ELC TRANSACTIONS TABLE
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS elc_transactions (
                id                SERIAL PRIMARY KEY,
                user_id           BIGINT NOT NULL,
                transaction_type  TEXT NOT NULL,
                amount            REAL NOT NULL,
                balance_after     REAL NOT NULL,
                description       TEXT,
                metadata          TEXT,
                created_at        TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_elc_txs_user ON elc_transactions(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_elc_txs_type ON elc_transactions(transaction_type)")
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # PAYMENT HISTORY TABLE
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS payment_history (
                id              SERIAL PRIMARY KEY,
                user_id         BIGINT NOT NULL,
                license_id      INTEGER,
                payment_type    TEXT NOT NULL,
                amount          REAL NOT NULL,
                currency        TEXT NOT NULL,
                license_type    TEXT NOT NULL,
                period_days     INTEGER NOT NULL,
                telegram_charge_id TEXT,
                status          TEXT NOT NULL DEFAULT 'completed',
                created_at      BIGINT NOT NULL,
                metadata        TEXT
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_payments_user ON payment_history(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_payments_status ON payment_history(status)")
        
        # Add tx_hash column to payment_history if not exists
        cur.execute("ALTER TABLE payment_history ADD COLUMN IF NOT EXISTS tx_hash TEXT")
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # TON PAYMENTS TABLE (TON blockchain subscription purchases)
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ton_payments (
                id              SERIAL PRIMARY KEY,
                user_id         BIGINT NOT NULL,
                payment_id      TEXT UNIQUE NOT NULL,
                plan_id         TEXT NOT NULL,
                amount_usdt     REAL NOT NULL,
                amount_ton      REAL,
                status          TEXT DEFAULT 'pending',
                platform_wallet TEXT NOT NULL,
                from_wallet     TEXT,
                tx_hash         TEXT,
                created_at      TIMESTAMP DEFAULT NOW(),
                expires_at      TIMESTAMP,
                confirmed_at    TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ton_payments_user ON ton_payments(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ton_payments_status ON ton_payments(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ton_payments_payment_id ON ton_payments(payment_id)")
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # LICENSE REQUESTS TABLE (Admin Approval System)
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS license_requests (
                id              SERIAL PRIMARY KEY,
                user_id         BIGINT NOT NULL,
                license_type    TEXT NOT NULL,
                period_months   INTEGER NOT NULL DEFAULT 1,
                payment_method  TEXT NOT NULL DEFAULT 'pending',
                amount          REAL NOT NULL DEFAULT 0,
                currency        TEXT NOT NULL DEFAULT 'ELC',
                status          TEXT NOT NULL DEFAULT 'pending',
                notes           TEXT,
                created_at      BIGINT NOT NULL,
                approved_at     BIGINT,
                approved_by     BIGINT,
                rejection_reason TEXT
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_lic_requests_user ON license_requests(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_lic_requests_status ON license_requests(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_lic_requests_pending ON license_requests(status, created_at) WHERE status = 'pending'")
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # PROMO USAGE TABLE (Track promo code usage)
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS promo_usage (
                id              SERIAL PRIMARY KEY,
                promo_id        INTEGER NOT NULL,
                user_id         BIGINT NOT NULL,
                used_at         BIGINT NOT NULL,
                UNIQUE(promo_id, user_id)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_promo_usage_user ON promo_usage(user_id)")
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # USER DEVICES TABLE (Mobile app multitenancy - Android/iOS)
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_devices (
                id              SERIAL PRIMARY KEY,
                user_id         BIGINT NOT NULL,
                device_token    TEXT,
                device_type     TEXT DEFAULT 'android',
                device_name     TEXT,
                is_active       BOOLEAN DEFAULT TRUE,
                created_at      TIMESTAMP DEFAULT NOW(),
                last_seen       TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_user_devices_user ON user_devices(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_user_devices_token ON user_devices(device_token) WHERE device_token IS NOT NULL")
        
        # Add notification_settings column to users if not exists
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name = 'users' AND column_name = 'notification_settings') THEN
                    ALTER TABLE users ADD COLUMN notification_settings JSONB DEFAULT '{}';
                END IF;
            END
            $$
        """)
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # EMAIL USERS TABLE (Alternative auth method without Telegram)
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS email_users (
                id              SERIAL PRIMARY KEY,
                user_id         BIGINT UNIQUE NOT NULL,
                email           TEXT UNIQUE NOT NULL,
                password_hash   TEXT NOT NULL,
                password_salt   TEXT NOT NULL,
                name            TEXT,
                is_verified     BOOLEAN DEFAULT FALSE,
                verification_code TEXT,
                verification_expires TIMESTAMP,
                last_login      TIMESTAMP,
                created_at      TIMESTAMP DEFAULT NOW(),
                updated_at      TIMESTAMP DEFAULT NOW()
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_email_users_email ON email_users(email)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_email_users_user_id ON email_users(user_id)")
        
        # Add email column to users table if not exists
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name = 'users' AND column_name = 'email') THEN
                    ALTER TABLE users ADD COLUMN email TEXT;
                END IF;
            END
            $$
        """)
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # USER PENDING INPUTS TABLE (for persistence across bot restarts)
        # ═══════════════════════════════════════════════════════════════════════════════════
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_pending_inputs (
                user_id         BIGINT PRIMARY KEY,
                input_type      TEXT NOT NULL,
                input_data      TEXT,
                created_at      TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # ═══════════════════════════════════════════════════════════════════════════════════
        # MIGRATIONS: Add missing columns to existing tables
        # ═══════════════════════════════════════════════════════════════════════════════════
        migration_columns = [
            ("strategies_enabled", "TEXT"),
            ("strategies_order", "TEXT"),
            ("rsi_lo", "REAL"),
            ("rsi_hi", "REAL"),
            ("bb_touch_k", "REAL"),
            ("oi_min_pct", "REAL"),
            ("price_min_pct", "REAL"),
            ("limit_only_default", "INTEGER DEFAULT 0"),
            ("license_type", "TEXT"),
        ]
        for col_name, col_def in migration_columns:
            cur.execute(f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name = 'users' AND column_name = '{col_name}') THEN
                        ALTER TABLE users ADD COLUMN {col_name} {col_def};
                    END IF;
                END
                $$
            """)
        
        logger.info("✅ PostgreSQL schema initialized successfully")


# ═══════════════════════════════════════════════════════════════════════════════════
# USER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def pg_get_user(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    return execute_one("SELECT * FROM users WHERE user_id = %s", (user_id,))


def pg_ensure_user(user_id: int) -> Dict:
    """Ensure user exists, create if not"""
    user = pg_get_user(user_id)
    if user:
        return user
    
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO users (user_id, trading_mode, lang)
                VALUES (%s, 'demo', 'en')
                ON CONFLICT (user_id) DO UPDATE SET updated_at = NOW()
                RETURNING *
            """, (user_id,))
            return dict(cur.fetchone())


def pg_set_user_field(user_id: int, field: str, value: Any):
    """Set single user field"""
    # Ensure user exists first
    pg_ensure_user(user_id)
    
    # Safe field whitelist - must match db.py USER_FIELDS_WHITELIST
    allowed_fields = {
        'username', 'first_name', 'last_name',
        'demo_api_key', 'demo_api_secret', 'real_api_key', 'real_api_secret',
        'trading_mode', 'exchange_type', 'percent', 'tp_percent', 'sl_percent',
        'tp_pct', 'sl_pct',  # aliases
        'use_atr', 'coins', 'leverage', 'lang', 'is_allowed', 'is_banned',
        'trade_scryptomera', 'trade_scalper', 'trade_elcaro', 'trade_fibonacci',
        'trade_oi', 'trade_rsi_bb', 'trade_manual',
        'dca_enabled', 'dca_pct_1', 'dca_pct_2', 'strategy_settings',
        'hl_enabled', 'hl_testnet', 'hl_private_key', 'hl_wallet_address',
        'hl_vault_address',
        'hl_testnet_private_key', 'hl_testnet_wallet_address',
        'hl_mainnet_private_key', 'hl_mainnet_wallet_address',
        'atr_periods', 'atr_multiplier_sl', 'atr_trigger_pct', 'atr_step_pct',
        'direction', 'global_order_type', 'spot_enabled', 'spot_settings',
        'limit_ladder_enabled', 'limit_ladder_count', 'limit_ladder_settings',
        'terms_accepted', 'disclaimer_accepted', 'guide_sent',
        'live_enabled', 'limit_enabled',
        'license_type', 'license_expires', 'current_license', 'is_lifetime',
        'first_seen_ts', 'last_seen_ts', 'last_viewed_account',
        'strategies_enabled', 'strategies_order',
        'rsi_lo', 'rsi_hi', 'bb_touch_k',
        'oi_min_pct', 'price_min_pct', 'limit_only_default',
        'bybit_margin_mode', 'hl_margin_mode',
        'routing_policy',
        'bybit_coins_group', 'hl_coins_group',
        'bybit_leverage', 'bybit_order_type', 'bybit_coins_filter',
        'hl_leverage', 'hl_order_type', 'hl_coins_filter',
        'api_key', 'api_secret',
        'referral_code', 'referred_by',
        'trading_paused',
    }
    
    if field not in allowed_fields:
        logger.warning(f"pg_set_user_field: field '{field}' not in whitelist")
        return
    
    query = f"UPDATE users SET {field} = %s, updated_at = NOW() WHERE user_id = %s"
    execute_write(query, (value, user_id))


def pg_get_user_field(user_id: int, field: str, default: Any = None) -> Any:
    """Get single user field"""
    user = pg_get_user(user_id)
    if user:
        return user.get(field, default)
    return default


def pg_get_all_users() -> List[int]:
    """Get all user IDs"""
    rows = execute("SELECT user_id FROM users")
    return [r['user_id'] for r in rows]


def pg_get_active_users() -> List[int]:
    """Get users with API keys"""
    rows = execute("""
        SELECT user_id FROM users 
        WHERE (demo_api_key IS NOT NULL OR real_api_key IS NOT NULL)
        AND is_banned = 0
    """)
    return [r['user_id'] for r in rows]


def pg_get_allowed_users() -> List[int]:
    """Get users with is_allowed=1"""
    rows = execute("SELECT user_id FROM users WHERE is_allowed = 1")
    return [r['user_id'] for r in rows]


def pg_get_trading_mode(user_id: int) -> str:
    """Get user's current trading mode"""
    result = execute_one("SELECT trading_mode FROM users WHERE user_id = %s", (user_id,))
    if result and result.get('trading_mode'):
        return result['trading_mode']
    return "demo"


def pg_get_active_trading_users() -> List[int]:
    """
    Get users with API keys configured - optimized for monitoring loop.
    Includes users with HyperLiquid credentials too.
    """
    rows = execute("""
        SELECT user_id FROM users 
        WHERE is_banned = 0 
        AND (
            demo_api_key IS NOT NULL 
            OR real_api_key IS NOT NULL
            OR (hl_private_key IS NOT NULL AND hl_enabled = 1)
        )
    """)
    return [r['user_id'] for r in rows]


def pg_get_user_credentials(user_id: int, account_type: str = None) -> tuple:
    """Get API credentials for specified account type."""
    user = pg_get_user(user_id)
    if not user:
        return (None, None)
    
    demo_key = user.get('demo_api_key')
    demo_secret = user.get('demo_api_secret')
    real_key = user.get('real_api_key')
    real_secret = user.get('real_api_secret')
    trading_mode = user.get('trading_mode', 'demo')
    
    if account_type == "real":
        return (real_key, real_secret)
    elif account_type == "demo":
        return (demo_key, demo_secret)
    
    if trading_mode == "real":
        return (real_key, real_secret)
    return (demo_key, demo_secret)


def pg_get_all_user_credentials(user_id: int) -> Dict:
    """Get all API credentials and trading mode for a user."""
    user = pg_get_user(user_id)
    if not user:
        return {
            "demo_api_key": None, "demo_api_secret": None,
            "real_api_key": None, "real_api_secret": None,
            "trading_mode": "demo"
        }
    
    return {
        "demo_api_key": user.get('demo_api_key'),
        "demo_api_secret": user.get('demo_api_secret'),
        "real_api_key": user.get('real_api_key'),
        "real_api_secret": user.get('real_api_secret'),
        "trading_mode": user.get('trading_mode') or "demo"
    }


def pg_get_exchange_type(user_id: int) -> str:
    """Get user's exchange type: 'bybit' or 'hyperliquid'"""
    user = pg_get_user(user_id)
    if user and user.get('exchange_type'):
        return user['exchange_type']
    return "bybit"


def pg_get_hl_credentials(user_id: int, account_type: str = None) -> Dict:
    """Get HyperLiquid credentials as dict (matching original SQLite function)."""
    user = pg_get_user(user_id)
    
    if not user:
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
    
    # Extract fields
    legacy_key = user.get('hl_private_key')
    legacy_addr = user.get('hl_wallet_address')
    vault_addr = user.get('hl_vault_address')
    is_testnet = bool(user.get('hl_testnet'))
    is_enabled = bool(user.get('hl_enabled'))
    testnet_key = user.get('hl_testnet_private_key')
    testnet_addr = user.get('hl_testnet_wallet_address')
    mainnet_key = user.get('hl_mainnet_private_key')
    mainnet_addr = user.get('hl_mainnet_wallet_address')
    
    # Determine primary key based on account_type or testnet flag
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
        "hl_testnet_private_key": testnet_key,
        "hl_testnet_wallet_address": testnet_addr,
        "hl_mainnet_private_key": mainnet_key,
        "hl_mainnet_wallet_address": mainnet_addr,
    }


def pg_is_hl_enabled(user_id: int) -> bool:
    """Check if HyperLiquid is enabled for user"""
    user = pg_get_user(user_id)
    if user:
        return bool(user.get('hl_enabled'))
    return False


# ═══════════════════════════════════════════════════════════════════════════════════
# POSITION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def pg_add_active_position(
    user_id: int,
    symbol: str,
    side: str,
    entry_price: float,
    size: float,
    strategy: str = None,
    account_type: str = "demo",
    leverage: float = None,
    sl_price: float = None,
    tp_price: float = None,
    exchange: str = "bybit",
    env: str = None
):
    """Add or update active position with full 4D multitenancy support"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO active_positions 
                    (user_id, symbol, account_type, exchange, side, entry_price, size, 
                     strategy, leverage, sl_price, tp_price, open_ts)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (user_id, symbol, account_type, exchange) 
                DO UPDATE SET 
                    side = EXCLUDED.side,
                    entry_price = EXCLUDED.entry_price,
                    size = EXCLUDED.size,
                    strategy = EXCLUDED.strategy,
                    leverage = EXCLUDED.leverage,
                    sl_price = EXCLUDED.sl_price,
                    tp_price = EXCLUDED.tp_price
            """, (user_id, symbol, account_type, exchange, side, entry_price, size,
                  strategy, leverage, sl_price, tp_price))


def pg_get_active_positions(
    user_id: int, 
    account_type: str = None,
    exchange: str = None,
    env: str = None
) -> List[Dict]:
    """Get active positions for user with full 4D multitenancy support"""
    conditions = ["user_id = %s"]
    params = [user_id]
    
    if account_type:
        conditions.append("account_type = %s")
        params.append(account_type)
    
    if exchange:
        conditions.append("exchange = %s")
        params.append(exchange)
    
    if env:
        conditions.append("env = %s")
        params.append(env)
    
    query = f"SELECT * FROM active_positions WHERE {' AND '.join(conditions)}"
    return execute(query, tuple(params))


def pg_get_active_position(
    user_id: int,
    symbol: str,
    account_type: str = "demo",
    exchange: str = "bybit"
) -> Optional[Dict]:
    """Get single active position"""
    return execute_one(
        "SELECT * FROM active_positions WHERE user_id = %s AND symbol = %s AND account_type = %s AND exchange = %s",
        (user_id, symbol, account_type, exchange)
    )


def pg_remove_active_position(
    user_id: int,
    symbol: str,
    account_type: str = "demo",
    exchange: str = "bybit"
):
    """Remove active position"""
    execute_write(
        "DELETE FROM active_positions WHERE user_id = %s AND symbol = %s AND account_type = %s AND exchange = %s",
        (user_id, symbol, account_type, exchange)
    )


def pg_update_position_field(
    user_id: int,
    symbol: str,
    field: str,
    value: Any,
    account_type: str = "demo",
    exchange: str = "bybit"
):
    """Update single position field"""
    allowed_fields = {'sl_price', 'tp_price', 'size', 'leverage', 'dca_10_done', 'dca_25_done',
                      'ptp_step_1_done', 'ptp_step_2_done', 'entry_price', 'strategy'}
    if field not in allowed_fields:
        return
    
    query = f"""
        UPDATE active_positions 
        SET {field} = %s 
        WHERE user_id = %s AND symbol = %s AND account_type = %s AND exchange = %s
    """
    execute_write(query, (value, user_id, symbol, account_type, exchange))


# ═══════════════════════════════════════════════════════════════════════════════════
# TRADE LOG FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def pg_add_trade_log(
    user_id: int,
    symbol: str,
    side: str,
    entry_price: float,
    exit_price: float,
    exit_reason: str,
    pnl: float,
    pnl_pct: float,
    strategy: str = None,
    account_type: str = "demo",
    sl_pct: float = None,
    tp_pct: float = None,
    timeframe: str = None,
    fee: float = 0.0,
    exchange: str = "bybit"
) -> bool:
    """Add trade log entry with duplicate protection and multitenancy support"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Check for recent duplicate with exchange filter
            cur.execute("""
                SELECT 1 FROM trade_logs 
                WHERE user_id = %s AND symbol = %s AND side = %s 
                AND entry_price = %s AND ABS(pnl - %s) < 0.01
                AND ts > NOW() - INTERVAL '24 hours'
                AND exchange = %s
                LIMIT 1
            """, (user_id, symbol, side, entry_price, pnl, exchange))
            
            if cur.fetchone():
                return False  # Duplicate
            
            cur.execute("""
                INSERT INTO trade_logs 
                    (user_id, symbol, side, entry_price, exit_price, exit_reason,
                     pnl, pnl_pct, strategy, account_type, sl_pct, tp_pct, timeframe, fee, exchange, ts)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (user_id, symbol, side, entry_price, exit_price, exit_reason,
                  pnl, pnl_pct, strategy, account_type, sl_pct, tp_pct, timeframe, fee, exchange))
            return True


def pg_get_trade_logs(
    user_id: int,
    account_type: str = None,
    strategy: str = None,
    limit: int = 100,
    days: int = None,
    exchange: str = None
) -> List[Dict]:
    """Get trade logs for user with multitenancy support"""
    conditions = ["user_id = %s"]
    params = [user_id]
    
    if account_type:
        conditions.append("account_type = %s")
        params.append(account_type)
    
    if strategy:
        conditions.append("strategy = %s")
        params.append(strategy)
    
    if days:
        conditions.append("ts > NOW() - INTERVAL '%s days'")
        params.append(days)
    
    if exchange:
        conditions.append("exchange = %s")
        params.append(exchange)
    
    query = f"""
        SELECT * FROM trade_logs 
        WHERE {' AND '.join(conditions)}
        ORDER BY ts DESC
        LIMIT %s
    """
    params.append(limit)
    
    return execute(query, tuple(params))


def pg_get_pnl_stats(
    user_id: int,
    account_type: str = None,
    days: int = None,
    exchange: str = None
) -> Dict:
    """Get PnL statistics with multitenancy support"""
    conditions = ["user_id = %s"]
    params = [user_id]
    
    if account_type:
        conditions.append("account_type = %s")
        params.append(account_type)
    
    if days:
        conditions.append("ts > NOW() - INTERVAL '%s days'")
        params.append(days)
    
    if exchange:
        conditions.append("exchange = %s")
        params.append(exchange)
    
    query = f"""
        SELECT 
            COUNT(*) as total_trades,
            COALESCE(SUM(pnl), 0) as total_pnl,
            COALESCE(AVG(pnl_pct), 0) as avg_pnl_pct,
            COUNT(CASE WHEN pnl > 0 THEN 1 END) as wins,
            COUNT(CASE WHEN pnl < 0 THEN 1 END) as losses
        FROM trade_logs 
        WHERE {' AND '.join(conditions)}
    """
    
    return execute_one(query, tuple(params)) or {
        'total_trades': 0, 'total_pnl': 0, 'avg_pnl_pct': 0, 'wins': 0, 'losses': 0
    }


# ═══════════════════════════════════════════════════════════════════════════════════
# SIGNAL FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def pg_add_signal(
    symbol: str,
    side: str,
    strategy: str,
    entry_price: float = None,
    sl_price: float = None,
    tp_price: float = None,
    timeframe: str = None,
    raw_json: str = None
):
    """Add signal entry"""
    execute_write("""
        INSERT INTO signals (symbol, side, strategy, entry_price, sl_price, tp_price, timeframe, raw_json, ts)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
    """, (symbol, side, strategy, entry_price, sl_price, tp_price, timeframe, raw_json))


def pg_get_signals(limit: int = 100, strategy: str = None) -> List[Dict]:
    """Get recent signals"""
    if strategy:
        return execute(
            "SELECT * FROM signals WHERE strategy = %s ORDER BY ts DESC LIMIT %s",
            (strategy, limit)
        )
    return execute(
        "SELECT * FROM signals ORDER BY ts DESC LIMIT %s",
        (limit,)
    )


# ═══════════════════════════════════════════════════════════════════════════════════
# USER CONFIG (full user data as dict)
# ═══════════════════════════════════════════════════════════════════════════════════

def pg_get_user_config(user_id: int) -> Dict:
    """Get full user configuration as dict"""
    user = pg_get_user(user_id)
    
    if not user:
        # Default config
        return {
            "percent": 1.0,
            "coins": "ALL",
            "limit_enabled": False,
            "trade_oi": 1,
            "trade_rsi_bb": 1,
            "tp_percent": 8.0,
            "sl_percent": 3.0,
            "use_atr": 1,
            "lang": "en",
            "is_allowed": 0,
            "is_banned": 0,
            "trade_scryptomera": 0,
            "trade_scalper": 0,
            "trade_elcaro": 0,
            "trade_fibonacci": 0,
            "strategy_settings": {},
            "dca_enabled": 0,
            "dca_pct_1": 10.0,
            "dca_pct_2": 25.0,
            "leverage": 10,
        }
    
    # Convert to dict with proper types
    config = dict(user)
    
    # Parse JSON fields
    if config.get('strategy_settings') and isinstance(config['strategy_settings'], str):
        import json
        try:
            config['strategy_settings'] = json.loads(config['strategy_settings'])
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse strategy_settings for user {user_id}: {e}")
            config['strategy_settings'] = {}
    
    return config


# ═══════════════════════════════════════════════════════════════════════════════════
# USER STRATEGY SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════════

def pg_get_user_strategy_settings(user_id: int, strategy: str, exchange: str = "bybit") -> Optional[Dict]:
    """Get user's settings for a specific strategy (both sides) with multitenancy support"""
    rows = execute(
        "SELECT * FROM user_strategy_settings WHERE user_id = %s AND strategy = %s AND exchange = %s",
        (user_id, strategy, exchange)
    )
    return rows if rows else []


def pg_set_user_strategy_settings(user_id: int, strategy: str, settings: Dict, side: str = None, exchange: str = "bybit"):
    """Set user's settings for a specific strategy with multitenancy support.
    
    With 4D schema, if side is provided, updates that specific side.
    If side is None and settings contains 'long'/'short' keys, updates both sides.
    """
    import json
    
    # Determine which sides to update
    sides_to_update = []
    if side:
        sides_to_update = [side]
    elif 'long' in settings or 'short' in settings:
        sides_to_update = [s for s in ['long', 'short'] if s in settings]
    else:
        # Apply same settings to both sides
        sides_to_update = ['long', 'short']
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            for s in sides_to_update:
                side_settings = settings.get(s, settings) if s in settings else settings
                settings_json = json.dumps(side_settings)
                
                cur.execute("""
                    INSERT INTO user_strategy_settings (user_id, strategy, side, exchange, settings)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, strategy, side, exchange) 
                    DO UPDATE SET settings = EXCLUDED.settings, updated_at = NOW()
                """, (user_id, strategy, s, exchange, settings_json))


# ═══════════════════════════════════════════════════════════════════════════════════
# HELPER: Create user_strategy_settings table if needed
# ═══════════════════════════════════════════════════════════════════════════════════

def ensure_tables():
    """Ensure all required tables exist with 3D schema (user_id, strategy, side)"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            # user_strategy_settings with 3D PRIMARY KEY (user_id, strategy, side)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_strategy_settings (
                    user_id       BIGINT NOT NULL,
                    strategy      TEXT NOT NULL,
                    side          TEXT NOT NULL DEFAULT 'long',
                    settings      JSONB DEFAULT '{}',
                    
                    -- Per-side trading settings
                    percent       REAL,
                    tp_percent    REAL,
                    sl_percent    REAL,
                    leverage      INTEGER,
                    use_atr       BOOLEAN DEFAULT FALSE,
                    
                    -- ATR settings per strategy/side
                    atr_periods       INTEGER,
                    atr_multiplier_sl REAL,
                    atr_trigger_pct   REAL,
                    atr_step_pct      REAL,
                    
                    -- Order settings
                    order_type        TEXT DEFAULT 'market',
                    limit_offset_pct  REAL DEFAULT 0.1,
                    direction         TEXT DEFAULT 'all',
                    
                    -- DCA settings
                    dca_enabled   BOOLEAN DEFAULT FALSE,
                    dca_pct_1     REAL DEFAULT 10.0,
                    dca_pct_2     REAL DEFAULT 25.0,
                    
                    -- Position limits
                    max_positions INTEGER DEFAULT 0,
                    coins_group   TEXT DEFAULT 'ALL',
                    
                    -- Context columns (for future extension)
                    trading_mode  TEXT DEFAULT 'demo',
                    exchange      TEXT DEFAULT 'bybit',
                    account_type  TEXT DEFAULT 'demo',
                    
                    enabled       BOOLEAN DEFAULT TRUE,
                    updated_at    TIMESTAMP DEFAULT NOW(),
                    
                    PRIMARY KEY (user_id, strategy, side)
                )
            """)
            
            # Indexes for efficient querying
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_strategy_settings_user 
                ON user_strategy_settings(user_id)
            """)
            
            # Add any missing columns to users
            cur.execute("""
                DO $$ 
                BEGIN
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS is_banned INTEGER DEFAULT 0;
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS trade_manual INTEGER DEFAULT 1;
                EXCEPTION WHEN OTHERS THEN
                    NULL;
                END $$;
            """)


# Initialize on module load
try:
    ensure_tables()
except Exception as e:
    logger.warning(f"Could not ensure PostgreSQL tables: {e}")


# ═══════════════════════════════════════════════════════════════════════════════════
# ADDITIONAL CRITICAL FUNCTIONS (Jan 15, 2026)
# ═══════════════════════════════════════════════════════════════════════════════════

def pg_is_bybit_enabled(user_id: int) -> bool:
    """Check if Bybit trading is enabled AND configured for user.
    
    Returns True only if:
    1. bybit_enabled flag is True (or None for backward compat)
    2. User has at least demo OR real credentials configured
    """
    row = execute_one(
        "SELECT bybit_enabled, demo_api_key, demo_api_secret, real_api_key, real_api_secret FROM users WHERE user_id = %s",
        (user_id,)
    )
    
    if not row:
        return False
    
    bybit_enabled = row.get('bybit_enabled')
    # If explicitly disabled, return False
    if bybit_enabled == 0 or bybit_enabled is False:
        return False
    
    # Check if any credentials exist
    has_demo = bool(row.get('demo_api_key') and row.get('demo_api_secret'))
    has_real = bool(row.get('real_api_key') and row.get('real_api_secret'))
    
    return has_demo or has_real


def pg_set_bybit_enabled(user_id: int, enabled: bool):
    """Enable or disable Bybit trading for user."""
    pg_ensure_user(user_id)
    execute_write(
        "UPDATE users SET bybit_enabled = %s WHERE user_id = %s",
        (enabled, user_id)
    )


def pg_get_routing_policy(user_id: int) -> str:
    """Get user's global routing policy."""
    row = execute_one(
        "SELECT routing_policy FROM users WHERE user_id = %s",
        (user_id,)
    )
    return row.get('routing_policy') if row and row.get('routing_policy') else 'same_exchange_all_envs'


def pg_set_routing_policy(user_id: int, policy: str):
    """Set user's global routing policy."""
    pg_ensure_user(user_id)
    execute_write(
        "UPDATE users SET routing_policy = %s WHERE user_id = %s",
        (policy, user_id)
    )


def pg_get_user_trading_context(user_id: int) -> Dict:
    """Get current trading context for user."""
    row = execute_one(
        "SELECT exchange_type, trading_mode, hl_testnet FROM users WHERE user_id = %s",
        (user_id,)
    )
    
    if not row:
        return {"exchange": "bybit", "account_type": "demo", "trading_mode": "demo"}
    
    exchange = row.get('exchange_type') or "bybit"
    trading_mode = row.get('trading_mode') or "demo"
    hl_testnet = bool(row.get('hl_testnet')) if row.get('hl_testnet') is not None else False
    
    if exchange == "hyperliquid":
        account_type = "testnet" if hl_testnet else "mainnet"
    else:
        if trading_mode == "both":
            account_type = "real"
        else:
            account_type = trading_mode
    
    return {
        "exchange": exchange,
        "account_type": account_type,
        "trading_mode": trading_mode
    }


def pg_get_active_account_types(user_id: int) -> List[str]:
    """Get list of account types to trade on based on trading_mode."""
    row = execute_one(
        "SELECT exchange_type, trading_mode FROM users WHERE user_id = %s",
        (user_id,)
    )
    
    if not row:
        return ["demo"]
    
    exchange = row.get('exchange_type') or "bybit"
    trading_mode = row.get('trading_mode') or "demo"
    
    if exchange == "hyperliquid":
        return ["mainnet"]  # HL only has mainnet for now
    
    if trading_mode == "both":
        return ["demo", "real"]
    return [trading_mode]


def pg_get_strategy_account_types(user_id: int, strategy: str) -> List[str]:
    """Get account types that a specific strategy is enabled for."""
    # Check user_strategy_settings for strategy-specific settings
    rows = execute(
        """SELECT account_type, enabled FROM user_strategy_settings 
           WHERE user_id = %s AND strategy = %s AND enabled = TRUE""",
        (user_id, strategy)
    )
    
    if rows:
        return [r['account_type'] for r in rows if r.get('account_type')]
    
    # Fallback to user's global trading mode
    return pg_get_active_account_types(user_id)


# Default strategy settings (fallback values)
DEFAULT_STRATEGY_SETTINGS = {
    "oi": {"percent": 1.0, "sl_percent": 3.0, "tp_percent": 8.0, "leverage": 10, "use_atr": 1},
    "scalper": {"percent": 1.0, "sl_percent": 2.0, "tp_percent": 4.0, "leverage": 10, "use_atr": 1},
    "scryptomera": {"percent": 1.0, "sl_percent": 3.0, "tp_percent": 6.0, "leverage": 10, "use_atr": 1},
    "elcaro": {"percent": 1.0, "sl_percent": 3.0, "tp_percent": 8.0, "leverage": 10, "use_atr": 1},
    "fibonacci": {"percent": 1.0, "sl_percent": 2.5, "tp_percent": 5.0, "leverage": 10, "use_atr": 1},
    "rsi_bb": {"percent": 1.0, "sl_percent": 3.0, "tp_percent": 8.0, "leverage": 10, "use_atr": 1},
}

DEFAULT_HL_STRATEGY_SETTINGS = {
    "oi": {"hl_enabled": False, "hl_percent": 1.0, "hl_sl_percent": 3.0, "hl_tp_percent": 8.0, "hl_leverage": 5},
}


def pg_get_strategy_settings_db(user_id: int, strategy: str, exchange: str = "bybit", account_type: str = "demo") -> Dict:
    """Get strategy settings from user_strategy_settings table.
    
    NOTE: With simplified schema (PRIMARY KEY: user_id, strategy, side),
    exchange and account_type parameters are kept for API compatibility but NOT used.
    Settings are shared across all exchanges/accounts for the same strategy.
    """
    # SIMPLIFIED: Query by (user_id, strategy) only, return combined long/short settings
    # The exchange and account_type params are ignored in simplified schema
    return pg_get_strategy_settings(user_id, strategy)


def pg_get_strategy_settings(user_id: int, strategy: str, exchange: str = None, account_type: str = None) -> Dict:
    """
    Get settings for a specific strategy.
    4D SCHEMA: PRIMARY KEY is (user_id, strategy, side, exchange).
    Each side (long/short) and exchange has its own row with independent settings.
    Returns both LONG and SHORT settings as long_* and short_* fields.
    
    Args:
        user_id: User ID
        strategy: Strategy name
        exchange: Exchange name ('bybit' or 'hyperliquid'). If None, uses user's active exchange.
        account_type: Kept for API compatibility
    """
    from coin_params import STRATEGY_DEFAULTS
    
    # Get user's active exchange if not specified
    if not exchange:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT exchange_type FROM users WHERE user_id = %s", (user_id,))
                row = cur.fetchone()
                exchange = row[0] if row and row[0] else "bybit"
    
    result = {}
    trading_mode = "demo"  # Default trading mode
    direction = "all"  # Default direction
    coins_group = "ALL"  # Default coins group
    
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # 4D SCHEMA: Query for both long and short rows for specific exchange
            cur.execute("""
                SELECT * FROM user_strategy_settings 
                WHERE user_id = %s AND strategy = %s AND exchange = %s
            """, (user_id, strategy, exchange))
            rows = cur.fetchall()
            
            # If no rows found for this exchange, try to copy from default exchange
            if not rows and exchange != "bybit":
                # Try to get settings from bybit as fallback
                cur.execute("""
                    SELECT * FROM user_strategy_settings 
                    WHERE user_id = %s AND strategy = %s AND exchange = 'bybit'
                """, (user_id, strategy))
                bybit_rows = cur.fetchall()
                
                # Copy bybit settings to this exchange
                if bybit_rows:
                    for row in bybit_rows:
                        side = row.get('side', 'long')
                        _pg_copy_settings_to_exchange(cur, user_id, strategy, side, row, exchange)
                    
                    # Re-fetch for this exchange
                    cur.execute("""
                        SELECT * FROM user_strategy_settings 
                        WHERE user_id = %s AND strategy = %s AND exchange = %s
                    """, (user_id, strategy, exchange))
                    rows = cur.fetchall()
            
            # Group rows by side
            rows_by_side = {}
            for row in rows:
                side = row.get('side', 'long')
                rows_by_side[side] = row
                
                # Get strategy-level settings from any row (they should be same)
                if row.get('trading_mode'):
                    trading_mode = row.get('trading_mode')
                if row.get('direction'):
                    direction = row.get('direction')
                if row.get('coins_group'):
                    coins_group = row.get('coins_group')
            
            # Build result from each side's row
            for side in ["long", "short"]:
                prefix = f"{side}_"
                row = rows_by_side.get(side)
                
                if row:
                    result[f"{prefix}enabled"] = row.get('enabled', True)
                    result[f"{prefix}percent"] = row.get('percent')
                    result[f"{prefix}sl_percent"] = row.get('sl_percent')
                    result[f"{prefix}tp_percent"] = row.get('tp_percent')
                    result[f"{prefix}leverage"] = row.get('leverage')
                    result[f"{prefix}use_atr"] = row.get('use_atr')
                    result[f"{prefix}atr_periods"] = row.get('atr_periods')
                    result[f"{prefix}atr_multiplier_sl"] = row.get('atr_multiplier_sl')
                    result[f"{prefix}atr_trigger_pct"] = row.get('atr_trigger_pct')
                    result[f"{prefix}atr_step_pct"] = row.get('atr_step_pct')
                    result[f"{prefix}order_type"] = row.get('order_type', 'market')
                    result[f"{prefix}limit_offset_pct"] = row.get('limit_offset_pct', 0.1)
                    result[f"{prefix}dca_enabled"] = row.get('dca_enabled', False)
                    result[f"{prefix}dca_pct_1"] = row.get('dca_pct_1', 10.0)
                    result[f"{prefix}dca_pct_2"] = row.get('dca_pct_2', 25.0)
                    result[f"{prefix}max_positions"] = row.get('max_positions', 0)
                    result[f"{prefix}coins_group"] = row.get('coins_group', 'ALL')
                    # Break-Even settings
                    result[f"{prefix}be_enabled"] = row.get('be_enabled', False)
                    result[f"{prefix}be_trigger_pct"] = row.get('be_trigger_pct', 1.0)
                    # Partial Take Profit settings (срез маржи в 2 шага)
                    result[f"{prefix}partial_tp_enabled"] = row.get('partial_tp_enabled', False)
                    result[f"{prefix}partial_tp_1_trigger_pct"] = row.get('partial_tp_1_trigger_pct', 2.0)
                    result[f"{prefix}partial_tp_1_close_pct"] = row.get('partial_tp_1_close_pct', 30.0)
                    result[f"{prefix}partial_tp_2_trigger_pct"] = row.get('partial_tp_2_trigger_pct', 5.0)
                    result[f"{prefix}partial_tp_2_close_pct"] = row.get('partial_tp_2_close_pct', 30.0)
    
    # Add strategy-level settings to result
    result["trading_mode"] = trading_mode
    result["direction"] = direction
    result["coins_group"] = coins_group
    result["exchange"] = exchange  # Include current exchange in result
    
    # Fill missing sides with defaults
    # CRITICAL FIX (Feb 2026): For trading params that have user-global equivalents
    # (percent, sl_percent, tp_percent, leverage, use_atr, dca_*, be_*),
    # set to None so get_strategy_trade_params() falls through to user globals.
    # Only fill structural defaults that have NO user-global equivalents.
    for side in ["long", "short"]:
        prefix = f"{side}_"
        defaults = STRATEGY_DEFAULTS.get(side, STRATEGY_DEFAULTS["long"])
        
        # Only fill defaults if this side has NO DB row at all
        # (NOT based on percent being None — a row may exist with percent=NULL but other values set)
        if side not in rows_by_side:
            # Only set enabled if it wasn't already set from DB
            if f"{prefix}enabled" not in result:
                result[f"{prefix}enabled"] = defaults.get("enabled", True)
            # Trading params → None (will fall through to user globals in get_strategy_trade_params)
            result[f"{prefix}percent"] = None
            result[f"{prefix}sl_percent"] = None
            result[f"{prefix}tp_percent"] = None
            result[f"{prefix}leverage"] = None
            result[f"{prefix}use_atr"] = None
            # ATR calculation params → atr_periods/atr_multiplier_sl keep defaults (no user-global equivalents)
            # But atr_trigger_pct/atr_step_pct → None (DO have user-global equivalents!)
            result[f"{prefix}atr_periods"] = defaults.get("atr_periods", 14)
            result[f"{prefix}atr_multiplier_sl"] = defaults.get("atr_multiplier_sl", 1.5)
            result[f"{prefix}atr_trigger_pct"] = None  # Fall through to user globals
            result[f"{prefix}atr_step_pct"] = None      # Fall through to user globals
            result[f"{prefix}order_type"] = defaults.get("order_type", "market")
            result[f"{prefix}limit_offset_pct"] = defaults.get("limit_offset_pct", 0.1)
            # DCA → None (will fall through to user globals)
            result[f"{prefix}dca_enabled"] = None
            result[f"{prefix}dca_pct_1"] = None
            result[f"{prefix}dca_pct_2"] = None
            result[f"{prefix}max_positions"] = defaults.get("max_positions", 0)
            result[f"{prefix}coins_group"] = defaults.get("coins_group", "ALL")
            # Break-Even → None (will fall through to user globals)
            result[f"{prefix}be_enabled"] = None
            result[f"{prefix}be_trigger_pct"] = None
            # Partial Take Profit → keep defaults (no user-global equivalents)
            result[f"{prefix}partial_tp_enabled"] = defaults.get("partial_tp_enabled", False)
            result[f"{prefix}partial_tp_1_trigger_pct"] = defaults.get("partial_tp_1_trigger_pct", 2.0)
            result[f"{prefix}partial_tp_1_close_pct"] = defaults.get("partial_tp_1_close_pct", 30.0)
            result[f"{prefix}partial_tp_2_trigger_pct"] = defaults.get("partial_tp_2_trigger_pct", 5.0)
            result[f"{prefix}partial_tp_2_close_pct"] = defaults.get("partial_tp_2_close_pct", 30.0)
    
    return result


def _pg_copy_settings_to_exchange(cur, user_id: int, strategy: str, side: str, 
                                   source_row: dict, target_exchange: str):
    """Copy settings from source row to target exchange."""
    cur.execute("""
        INSERT INTO user_strategy_settings 
        (user_id, strategy, side, exchange, settings, percent, tp_percent, sl_percent,
         leverage, use_atr, atr_periods, atr_multiplier_sl, atr_trigger_pct, atr_step_pct,
         order_type, limit_offset_pct, direction, dca_enabled, dca_pct_1, dca_pct_2,
         max_positions, coins_group, trading_mode, account_type, enabled, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (user_id, strategy, side, exchange) DO NOTHING
    """, (
        user_id, strategy, side, target_exchange,
        source_row.get('settings', '{}'),
        source_row.get('percent'),
        source_row.get('tp_percent'),
        source_row.get('sl_percent'),
        source_row.get('leverage'),
        source_row.get('use_atr', False),
        source_row.get('atr_periods'),
        source_row.get('atr_multiplier_sl'),
        source_row.get('atr_trigger_pct'),
        source_row.get('atr_step_pct'),
        source_row.get('order_type', 'market'),
        source_row.get('limit_offset_pct', 0.1),
        source_row.get('direction', 'all'),
        source_row.get('dca_enabled', False),
        source_row.get('dca_pct_1', 10.0),
        source_row.get('dca_pct_2', 25.0),
        source_row.get('max_positions', 0),
        source_row.get('coins_group', 'ALL'),
        source_row.get('trading_mode', 'demo'),
        source_row.get('account_type', 'demo'),
        source_row.get('enabled', True)
    ))


def pg_set_strategy_setting(user_id: int, strategy: str, field: str, value, 
                            exchange: str = None, account_type: str = "demo") -> bool:
    """
    Set a single field for a strategy in user_strategy_settings table.
    
    4D SCHEMA: Field name determines side (long_* or short_*)
    If field starts with 'long_' or 'short_', extracts side and stores in correct row.
    
    Args:
        user_id: User ID
        strategy: Strategy name
        field: Field name (e.g., 'long_percent', 'short_sl_percent', 'direction')
        value: Value to set
        exchange: Exchange name. If None, uses user's active exchange.
        account_type: Kept for API compatibility
    """
    from coin_params import STRATEGY_DEFAULTS
    
    # Get user's active exchange if not specified
    if not exchange:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT exchange_type FROM users WHERE user_id = %s", (user_id,))
                row = cur.fetchone()
                exchange = row[0] if row and row[0] else "bybit"
    
    # Determine side from field name
    if field.startswith("long_"):

        side = "long"
        db_field = field[5:]  # Remove 'long_' prefix
    elif field.startswith("short_"):
        side = "short"
        db_field = field[6:]  # Remove 'short_' prefix
    else:
        # Non-side field like 'direction', 'order_type', 'coins_group'
        # Apply to both sides for this exchange
        for s in ["long", "short"]:
            _pg_set_side_setting(user_id, strategy, s, field, value, exchange)
        return True
    
    return _pg_set_side_setting(user_id, strategy, side, db_field, value, exchange)


def _pg_set_side_setting(user_id: int, strategy: str, side: str, field: str, value, 
                         exchange: str = "bybit") -> bool:
    """Set a field for a specific side (long/short) and exchange.
    
    4D SCHEMA: Uses (user_id, strategy, side, exchange) as key.
    """
    from coin_params import STRATEGY_DEFAULTS
    
    ALLOWED_FIELDS = {
        'enabled', 'percent', 'sl_percent', 'tp_percent', 'leverage',
        'use_atr', 'atr_periods', 'atr_multiplier_sl', 'atr_trigger_pct', 'atr_step_pct', 'order_type',
        'limit_offset_pct', 'dca_enabled', 'dca_pct_1', 'dca_pct_2',
        'max_positions', 'coins_group', 'trading_mode', 'direction',
        'account_type', 'be_enabled', 'be_trigger_pct',  # Break-Even
        # Partial Take Profit (срез маржи)
        'partial_tp_enabled', 'partial_tp_1_trigger_pct', 'partial_tp_1_close_pct',
        'partial_tp_2_trigger_pct', 'partial_tp_2_close_pct'
    }
    
    # Boolean fields that need conversion from int to bool for PostgreSQL
    BOOLEAN_FIELDS = {'enabled', 'use_atr', 'dca_enabled', 'be_enabled', 'partial_tp_enabled'}
    
    if field not in ALLOWED_FIELDS:
        logger.warning(f"Field '{field}' not in allowed fields for _pg_set_side_setting")
        return False
    
    # Convert int to bool for boolean columns
    if field in BOOLEAN_FIELDS and value is not None:
        value = bool(value)
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            # 4D SCHEMA: Check if row exists for this exchange
            cur.execute("""
                SELECT 1 FROM user_strategy_settings 
                WHERE user_id = %s AND strategy = %s AND side = %s AND exchange = %s
            """, (user_id, strategy, side, exchange))
            
            if cur.fetchone():
                # UPDATE existing
                cur.execute(f"""
                    UPDATE user_strategy_settings SET {field} = %s, updated_at = NOW()
                    WHERE user_id = %s AND strategy = %s AND side = %s AND exchange = %s
                """, (value, user_id, strategy, side, exchange))
            else:
                # INSERT new row with NULL for trading params that have user-global equivalents
                # This ensures get_strategy_trade_params() falls through to user globals
                # Only set structural fields that have NO user-global equivalents
                cur.execute("""
                    INSERT INTO user_strategy_settings 
                    (user_id, strategy, side, exchange, enabled, percent, sl_percent, tp_percent, 
                     leverage, use_atr, atr_trigger_pct, atr_step_pct, order_type,
                     limit_offset_pct, dca_enabled, dca_pct_1, dca_pct_2, max_positions, 
                     coins_group, trading_mode, account_type, direction,
                     be_enabled, be_trigger_pct)
                    VALUES (%s, %s, %s, %s, 
                            TRUE,           -- enabled (structural, no global equivalent)
                            NULL, NULL, NULL, NULL, NULL, NULL, NULL,  -- trading params → NULL (fall through to user globals)
                            'market', 0.1,  -- order_type, limit_offset_pct (structural defaults)
                            NULL, NULL, NULL,  -- DCA params → NULL (fall through to user globals)
                            0, 'ALL',       -- max_positions, coins_group (structural defaults)
                            'demo', 'demo', 'all',  -- trading_mode, account_type, direction
                            NULL, NULL)     -- BE params → NULL (fall through to user globals)
                """, (user_id, strategy, side, exchange))
                # Now update the specific field
                cur.execute(f"""
                    UPDATE user_strategy_settings SET {field} = %s
                    WHERE user_id = %s AND strategy = %s AND side = %s AND exchange = %s
                """, (value, user_id, strategy, side, exchange))
    
    return True



def pg_reset_strategy_to_defaults(user_id: int, strategy: str, side: str = None, 
                                   exchange: str = None) -> bool:
    """Reset strategy settings to defaults. 
    
    If side is None, resets both long and short.
    If exchange is None, resets both bybit and hyperliquid.
    
    4D SCHEMA: Uses (user_id, strategy, side, exchange) as key.
    """
    from coin_params import STRATEGY_DEFAULTS
    
    sides = [side] if side else ["long", "short"]
    exchanges = [exchange] if exchange else ["bybit", "hyperliquid"]
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            for ex in exchanges:
                for s in sides:
                    defaults = STRATEGY_DEFAULTS.get(s, STRATEGY_DEFAULTS["long"])
                    cur.execute("""
                        INSERT INTO user_strategy_settings 
                        (user_id, strategy, side, exchange, enabled, percent, sl_percent, tp_percent, 
                         leverage, use_atr, atr_trigger_pct, atr_step_pct, order_type,
                         limit_offset_pct, dca_enabled, dca_pct_1, dca_pct_2, max_positions, 
                         coins_group, trading_mode, account_type, direction)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (user_id, strategy, side, exchange) DO UPDATE SET
                            enabled = EXCLUDED.enabled,
                            percent = EXCLUDED.percent,
                            sl_percent = EXCLUDED.sl_percent,
                            tp_percent = EXCLUDED.tp_percent,
                            leverage = EXCLUDED.leverage,
                            use_atr = EXCLUDED.use_atr,
                            atr_trigger_pct = EXCLUDED.atr_trigger_pct,
                            atr_step_pct = EXCLUDED.atr_step_pct,
                            order_type = EXCLUDED.order_type,
                            limit_offset_pct = EXCLUDED.limit_offset_pct,
                            dca_enabled = EXCLUDED.dca_enabled,
                            dca_pct_1 = EXCLUDED.dca_pct_1,
                            dca_pct_2 = EXCLUDED.dca_pct_2,
                            max_positions = EXCLUDED.max_positions,
                            coins_group = EXCLUDED.coins_group,
                            trading_mode = EXCLUDED.trading_mode,
                            account_type = EXCLUDED.account_type,
                            direction = EXCLUDED.direction,
                            updated_at = NOW()
                    """, (
                        user_id, strategy, s, ex,
                        bool(defaults.get("enabled", True)),
                        defaults.get("percent"),
                        defaults.get("sl_percent"),
                        defaults.get("tp_percent"),
                        defaults.get("leverage"),
                        bool(defaults.get("use_atr", False)),
                        defaults.get("atr_trigger_pct"),
                        defaults.get("atr_step_pct"),
                        defaults.get("order_type", "market"),
                        defaults.get("limit_offset_pct", 0.1),
                        bool(defaults.get("dca_enabled", False)),
                        defaults.get("dca_pct_1", 10.0),
                        defaults.get("dca_pct_2", 25.0),
                        defaults.get("max_positions", 0),
                        defaults.get("coins_group", "ALL"),
                        "demo",   # Reset trading_mode to demo
                        "demo",   # Default account_type
                        "all"     # Default direction
                    ))
    return True


# ATR defaults by timeframe (kept for compatibility)
ATR_DEFAULTS = {
    "24h": {"atr_trigger_pct": 0.5, "atr_step_pct": 0.3},
    "4h": {"atr_trigger_pct": 0.4, "atr_step_pct": 0.25},
    "1h": {"atr_trigger_pct": 0.3, "atr_step_pct": 0.2},
}


def pg_get_effective_settings(user_id: int, strategy: str, exchange: str = None, 
                             account_type: str = None, timeframe: str = "24h", 
                             side: str = None) -> Dict:
    """
    Get effective settings for a strategy.
    SIMPLIFIED: Read side-specific settings from DB, fallback to STRATEGY_DEFAULTS.
    """
    from coin_params import STRATEGY_DEFAULTS
    
    settings = pg_get_strategy_settings(user_id, strategy)
    
    # Determine side prefix
    side_prefix = "long"
    if side:
        side_upper = str(side).upper()
        if side_upper in ("SELL", "SHORT"):
            side_prefix = "short"
    
    defaults = STRATEGY_DEFAULTS.get(side_prefix, STRATEGY_DEFAULTS["long"])
    
    def _get(key):
        val = settings.get(f"{side_prefix}_{key}")
        return val if val is not None else defaults.get(key)
    
    return {
        "enabled": bool(settings.get(f"{side_prefix}_enabled", defaults.get("enabled", True))),
        "percent": _get("percent"),
        "sl_percent": _get("sl_percent"),
        "tp_percent": _get("tp_percent"),
        "leverage": _get("leverage"),
        "use_atr": bool(_get("use_atr")),
        "atr_trigger_pct": _get("atr_trigger_pct"),
        "atr_step_pct": _get("atr_step_pct"),
        "order_type": settings.get("order_type") or defaults.get("order_type", "market"),
        "direction": "all",
        "side": side_prefix,
    }


def pg_get_hl_strategy_settings(user_id: int, strategy: str) -> Dict:
    """Get HyperLiquid-specific settings for a strategy."""
    config = pg_get_user_config(user_id)
    hl_settings = config.get("hl_strategy_settings", {})
    strat_settings = hl_settings.get(strategy, {}) if isinstance(hl_settings, dict) else {}
    
    # Merge with defaults
    defaults = DEFAULT_HL_STRATEGY_SETTINGS.get(strategy, DEFAULT_HL_STRATEGY_SETTINGS.get("oi", {}))
    result = defaults.copy()
    if isinstance(strat_settings, dict):
        result.update(strat_settings)
    
    return result


def pg_set_hl_strategy_setting(user_id: int, strategy: str, field: str, value) -> bool:
    """Set a HyperLiquid-specific setting for a strategy."""
    import json
    
    config = pg_get_user_config(user_id)
    hl_settings = config.get("hl_strategy_settings", {})
    if not isinstance(hl_settings, dict):
        hl_settings = {}
    
    if strategy not in hl_settings:
        hl_settings[strategy] = {}
    
    if value is None:
        hl_settings[strategy].pop(field, None)
    else:
        hl_settings[strategy][field] = value
    
    # Save back to user
    pg_set_user_field(user_id, "hl_strategy_settings", json.dumps(hl_settings))
    return True


def pg_get_hl_effective_settings(user_id: int, strategy: str) -> Dict:
    """Get effective HyperLiquid settings with fallback."""
    hl_settings = pg_get_hl_strategy_settings(user_id, strategy)
    
    # Get global config for fallback
    config = pg_get_user_config(user_id)
    
    return {
        "hl_enabled": hl_settings.get("hl_enabled", False),
        "hl_percent": hl_settings.get("hl_percent") or config.get("percent") or 1.0,
        "hl_sl_percent": hl_settings.get("hl_sl_percent") or config.get("sl_percent") or 3.0,
        "hl_tp_percent": hl_settings.get("hl_tp_percent") or config.get("tp_percent") or 8.0,
        "hl_leverage": hl_settings.get("hl_leverage") or 5,
    }


def pg_should_show_account_switcher(user_id: int) -> bool:
    """Check if user should see Demo/Real switcher."""
    creds = pg_get_all_user_credentials(user_id)
    
    has_demo = bool(creds.get("demo_api_key") and creds.get("demo_api_secret"))
    has_real = bool(creds.get("real_api_key") and creds.get("real_api_secret"))
    
    if not (has_demo and has_real):
        return False
    
    # Check effective mode
    mode = pg_get_trading_mode(user_id)
    return mode == "both"


def pg_update_user_info(user_id: int, username: str = None, first_name: str = None):
    """Updates user info (username, first_name) if provided."""
    pg_ensure_user(user_id)
    
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


def pg_set_trading_mode(user_id: int, mode: str):
    """Set trading mode (demo/real/both)."""
    pg_ensure_user(user_id)
    execute_write(
        "UPDATE users SET trading_mode = %s WHERE user_id = %s",
        (mode, user_id)
    )


def pg_set_hl_enabled(user_id: int, enabled: bool):
    """Enable or disable HyperLiquid trading."""
    pg_ensure_user(user_id)
    execute_write(
        "UPDATE users SET hl_enabled = %s WHERE user_id = %s",
        (enabled, user_id)
    )


def pg_delete_user(user_id: int):
    """Delete user and all related data."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM active_positions WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM trade_logs WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM user_strategy_settings WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))


def pg_sync_position_entry_price(user_id: int, symbol: str, new_entry_price: float, account_type: str = "demo", exchange: str = "bybit") -> bool:
    """Update position entry price (used after DCA)."""
    result = execute_write(
        """UPDATE active_positions SET entry_price = %s 
           WHERE user_id = %s AND symbol = %s AND account_type = %s AND exchange = %s""",
        (new_entry_price, user_id, symbol, account_type, exchange)
    )
    return result > 0


def pg_set_user_credentials(user_id: int, api_key: str, api_secret: str, account_type: str = "demo"):
    """Set API credentials for user."""
    pg_ensure_user(user_id)
    
    if account_type == "demo":
        execute_write(
            "UPDATE users SET demo_api_key = %s, demo_api_secret = %s WHERE user_id = %s",
            (api_key, api_secret, user_id)
        )
    elif account_type == "real":
        execute_write(
            "UPDATE users SET real_api_key = %s, real_api_secret = %s WHERE user_id = %s",
            (api_key, api_secret, user_id)
        )


# ═══════════════════════════════════════════════════════════════════════════════════
# USER PENDING INPUTS (for persistence across bot restarts)
# ═══════════════════════════════════════════════════════════════════════════════════

def pg_set_pending_input(user_id: int, input_type: str, input_data: str = None):
    """Set pending input for user (survives bot restarts)."""
    execute_write("""
        INSERT INTO user_pending_inputs (user_id, input_type, input_data, created_at)
        VALUES (%s, %s, %s, NOW())
        ON CONFLICT (user_id) DO UPDATE SET 
            input_type = EXCLUDED.input_type,
            input_data = EXCLUDED.input_data,
            created_at = NOW()
    """, (user_id, input_type, input_data))


def pg_get_pending_input(user_id: int) -> Optional[Dict]:
    """Get pending input for user."""
    return execute_one(
        "SELECT input_type, input_data, created_at FROM user_pending_inputs WHERE user_id = %s",
        (user_id,)
    )


def pg_clear_pending_input(user_id: int):
    """Clear pending input for user."""
    execute_write("DELETE FROM user_pending_inputs WHERE user_id = %s", (user_id,))


# ═══════════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test connection
    print("Testing PostgreSQL connection...")
    users = pg_get_all_users()
    print(f"Users: {len(users)}")
    
    if users:
        uid = users[0]
        user = pg_get_user(uid)
        print(f"User {uid}: trading_mode={user.get('trading_mode')}, lang={user.get('lang')}")
        
        positions = pg_get_active_positions(uid)
        print(f"Positions: {len(positions)}")
        
        stats = pg_get_pnl_stats(uid)
        print(f"Stats: {stats}")
    
    print("PostgreSQL OK!")
