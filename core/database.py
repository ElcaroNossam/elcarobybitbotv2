"""
Base database manager with optimized connection pooling
"""
import sqlite3
import threading
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Thread-safe SQLite database manager with connection pooling.
    Optimized for multi-user concurrent access.
    """
    
    _instance: Optional["DatabaseManager"] = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: str = None):
        """Singleton pattern for database manager"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: str = None):
        if self._initialized:
            return
            
        self.db_path = db_path or str(Path(__file__).parent.parent / "bot.db")
        self._local = threading.local()
        self._initialized = True
        
        # Initialize database schema
        self._init_schema()
        
        logger.info(f"DatabaseManager initialized: {self.db_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self._local.connection.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrency
            self._local.connection.execute("PRAGMA journal_mode=WAL")
            self._local.connection.execute("PRAGMA synchronous=NORMAL")
            self._local.connection.execute("PRAGMA cache_size=10000")
            self._local.connection.execute("PRAGMA busy_timeout=30000")
        return self._local.connection
    
    @contextmanager
    def connection(self):
        """Context manager for database connection with automatic commit/rollback"""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
    
    @contextmanager
    def cursor(self):
        """Context manager for database cursor"""
        with self.connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()
    
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute SQL with automatic connection management"""
        with self.cursor() as cur:
            return cur.execute(sql, params)
    
    def execute_many(self, sql: str, params_list: List[tuple]) -> None:
        """Execute SQL for multiple parameter sets"""
        with self.cursor() as cur:
            cur.executemany(sql, params_list)
    
    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch single row as dict"""
        with self.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None
    
    def fetch_all(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows as list of dicts"""
        with self.cursor() as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
    
    def fetch_value(self, sql: str, params: tuple = (), default=None):
        """Fetch single value"""
        row = self.fetch_one(sql, params)
        if row:
            return list(row.values())[0]
        return default
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        result = self.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return result is not None
    
    def column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if column exists in table"""
        with self.cursor() as cur:
            cur.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cur.fetchall()]
            return column_name in columns
    
    def add_column(self, table_name: str, column_name: str, column_type: str, default=None) -> bool:
        """Add column to table if not exists"""
        if self.column_exists(table_name, column_name):
            return False
        
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        if default is not None:
            if isinstance(default, str):
                sql += f" DEFAULT '{default}'"
            else:
                sql += f" DEFAULT {default}"
        
        with self.cursor() as cur:
            cur.execute(sql)
        
        logger.info(f"Added column {column_name} to {table_name}")
        return True
    
    def _init_schema(self):
        """Initialize database schema with all tables"""
        with self.cursor() as cur:
            # Users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    language TEXT DEFAULT 'en',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Access control
                    approved INTEGER DEFAULT 0,
                    banned INTEGER DEFAULT 0,
                    ban_reason TEXT,
                    terms_accepted INTEGER DEFAULT 0,
                    
                    -- License
                    license_type TEXT DEFAULT 'free',
                    license_expires_at TIMESTAMP,
                    promo_code TEXT,
                    
                    -- Exchange mode
                    exchange_mode TEXT DEFAULT 'bybit',
                    trading_mode TEXT DEFAULT 'demo',
                    
                    -- Bybit credentials (demo)
                    demo_api_key TEXT,
                    demo_api_secret TEXT,
                    
                    -- Bybit credentials (real)
                    real_api_key TEXT,
                    real_api_secret TEXT,
                    
                    -- HyperLiquid credentials
                    hl_private_key TEXT,
                    hl_address TEXT,
                    hl_vault_address TEXT,
                    hl_testnet INTEGER DEFAULT 0,
                    hl_enabled INTEGER DEFAULT 0,
                    
                    -- Trading settings
                    risk_percent REAL DEFAULT 1.0,
                    max_positions INTEGER DEFAULT 5,
                    leverage INTEGER DEFAULT 10,
                    order_type TEXT DEFAULT 'market',
                    margin_mode TEXT DEFAULT 'cross',
                    
                    -- TP/SL settings
                    auto_tp INTEGER DEFAULT 1,
                    auto_sl INTEGER DEFAULT 1,
                    tp_percent REAL DEFAULT 3.0,
                    sl_percent REAL DEFAULT 2.0,
                    trailing_stop INTEGER DEFAULT 0,
                    trailing_percent REAL DEFAULT 1.0,
                    
                    -- DCA settings
                    dca_enabled INTEGER DEFAULT 0,
                    dca_levels INTEGER DEFAULT 3,
                    dca_multiplier REAL DEFAULT 1.5,
                    
                    -- Pyramid settings
                    pyramid_enabled INTEGER DEFAULT 0,
                    pyramid_levels INTEGER DEFAULT 3,
                    pyramid_distance REAL DEFAULT 1.0,
                    
                    -- Filters
                    min_oi_change REAL DEFAULT 0,
                    max_oi_change REAL DEFAULT 100,
                    use_rsi_filter INTEGER DEFAULT 0,
                    use_bb_filter INTEGER DEFAULT 0,
                    
                    -- Notifications
                    notify_trades INTEGER DEFAULT 1,
                    notify_signals INTEGER DEFAULT 1,
                    notify_errors INTEGER DEFAULT 1,
                    
                    -- Coin filters (JSON arrays)
                    allowed_coins TEXT DEFAULT '[]',
                    blocked_coins TEXT DEFAULT '[]'
                )
            """)
            
            # Positions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    exchange TEXT NOT NULL DEFAULT 'bybit',
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    size REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    leverage INTEGER DEFAULT 10,
                    margin_mode TEXT DEFAULT 'cross',
                    take_profit REAL,
                    stop_loss REAL,
                    trailing_stop REAL,
                    signal_source TEXT,
                    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    closed_at TIMESTAMP,
                    close_price REAL,
                    realized_pnl REAL,
                    status TEXT DEFAULT 'open',
                    metadata TEXT DEFAULT '{}',
                    
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Trade logs table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS trade_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    exchange TEXT NOT NULL DEFAULT 'bybit',
                    position_id INTEGER,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    action TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    pnl REAL,
                    pnl_percent REAL,
                    fee REAL DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    signal_source TEXT,
                    order_id TEXT,
                    metadata TEXT DEFAULT '{}',
                    
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (position_id) REFERENCES positions(id)
                )
            """)
            
            # Orders table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    exchange TEXT NOT NULL DEFAULT 'bybit',
                    order_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    order_type TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL,
                    trigger_price REAL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP,
                    filled_at TIMESTAMP,
                    filled_qty REAL DEFAULT 0,
                    avg_fill_price REAL,
                    metadata TEXT DEFAULT '{}',
                    
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    UNIQUE(exchange, order_id)
                )
            """)
            
            # Signals table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price REAL,
                    take_profits TEXT DEFAULT '[]',
                    stop_loss REAL,
                    leverage INTEGER,
                    timeframe TEXT,
                    confidence REAL,
                    raw_text TEXT,
                    parsed_data TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # Signal executions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS signal_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    exchange TEXT NOT NULL,
                    position_id INTEGER,
                    status TEXT DEFAULT 'pending',
                    error_message TEXT,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (signal_id) REFERENCES signals(id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (position_id) REFERENCES positions(id)
                )
            """)
            
            # Statistics table (daily aggregates)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    exchange TEXT NOT NULL,
                    date DATE NOT NULL,
                    trades_count INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    losing_trades INTEGER DEFAULT 0,
                    total_pnl REAL DEFAULT 0,
                    total_volume REAL DEFAULT 0,
                    total_fees REAL DEFAULT 0,
                    max_drawdown REAL DEFAULT 0,
                    
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    UNIQUE(user_id, exchange, date)
                )
            """)
            
            # Create indexes for performance
            cur.execute("CREATE INDEX IF NOT EXISTS idx_users_license ON users(license_type)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_users_approved ON users(approved, banned)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_positions_user ON positions(user_id, status)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol, status)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_trades_user ON trade_logs(user_id, timestamp)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trade_logs(symbol, timestamp)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id, status)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status, created_at)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_stats_user_date ON daily_stats(user_id, date)")
            
        logger.info("Database schema initialized")
    
    def migrate(self):
        """Run database migrations"""
        # Add new columns if they don't exist
        migrations = [
            ("users", "exchange_mode", "TEXT", "bybit"),
            ("users", "hl_private_key", "TEXT", None),
            ("users", "hl_address", "TEXT", None),
            ("users", "hl_vault_address", "TEXT", None),
            ("users", "hl_testnet", "INTEGER", 0),
            ("users", "hl_enabled", "INTEGER", 0),
            ("users", "license_expires_at", "TIMESTAMP", None),
            ("users", "trading_mode", "TEXT", "demo"),
            ("positions", "exchange", "TEXT", "bybit"),
            ("trade_logs", "exchange", "TEXT", "bybit"),
            ("orders", "exchange", "TEXT", "bybit"),
        ]
        
        for table, column, col_type, default in migrations:
            self.add_column(table, column, col_type, default)
        
        logger.info("Database migrations completed")


# Global instance
_db_manager: Optional[DatabaseManager] = None


def get_db() -> DatabaseManager:
    """Get or create database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def init_db(db_path: str = None) -> DatabaseManager:
    """Initialize database with optional path"""
    global _db_manager
    _db_manager = DatabaseManager(db_path)
    _db_manager.migrate()
    return _db_manager
