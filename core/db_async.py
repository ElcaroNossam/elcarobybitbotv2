"""
Async PostgreSQL Database Layer for Enliko Trading Platform
============================================================
Designed for 10K+ concurrent users with connection pooling.

Features:
- asyncpg connection pooling (100 connections)
- Automatic reconnection
- Query timeout handling  
- Transaction support
- Prepared statements caching

Migration from SQLite:
- Same API as db.py where possible
- All operations are async
- Connection pool instead of single connection
"""

import asyncpg
from asyncpg import Pool, Connection
from typing import Optional, List, Dict, Any, Tuple
import logging
import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Singleton pool
_pool: Optional[Pool] = None
_pool_lock = asyncio.Lock()


async def get_pool() -> Pool:
    """Get or create connection pool"""
    global _pool
    
    if _pool is not None:
        return _pool
    
    async with _pool_lock:
        if _pool is not None:
            return _pool
        
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://elcaro:elcaro@localhost:5432/elcaro"
        )
        
        try:
            _pool = await asyncpg.create_pool(
                database_url,
                min_size=10,
                max_size=100,
                max_inactive_connection_lifetime=300,
                command_timeout=30,
            )
            logger.info(f"✅ PostgreSQL pool created: {_pool.get_size()} connections")
            return _pool
            
        except Exception as e:
            logger.error(f"❌ Failed to create PostgreSQL pool: {e}")
            raise


async def close_pool():
    """Close connection pool"""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("PostgreSQL pool closed")


@asynccontextmanager
async def get_connection():
    """Get connection from pool with automatic release"""
    pool = await get_pool()
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)


@asynccontextmanager
async def transaction():
    """Transaction context manager"""
    async with get_connection() as conn:
        async with conn.transaction():
            yield conn


# ═══════════════════════════════════════════════════════════════════════
# USER OPERATIONS
# ═══════════════════════════════════════════════════════════════════════

async def get_user_config(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user configuration"""
    async with get_connection() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM users WHERE user_id = $1",
            user_id
        )
        return dict(row) if row else None


async def set_user_field(user_id: int, field: str, value: Any):
    """Update single user field"""
    async with get_connection() as conn:
        await conn.execute(
            f"UPDATE users SET {field} = $1 WHERE user_id = $2",
            value, user_id
        )


async def get_user_lang(user_id: int) -> str:
    """Get user language"""
    async with get_connection() as conn:
        lang = await conn.fetchval(
            "SELECT lang FROM users WHERE user_id = $1",
            user_id
        )
        return lang or "en"


async def upsert_user(user_id: int, defaults: Dict[str, Any] = None):
    """Create user if not exists"""
    defaults = defaults or {}
    
    async with get_connection() as conn:
        exists = await conn.fetchval(
            "SELECT 1 FROM users WHERE user_id = $1",
            user_id
        )
        
        if not exists:
            columns = ["user_id"] + list(defaults.keys())
            placeholders = ", ".join(f"${i+1}" for i in range(len(columns)))
            values = [user_id] + list(defaults.values())
            
            await conn.execute(
                f"INSERT INTO users ({', '.join(columns)}) VALUES ({placeholders})",
                *values
            )
            logger.info(f"Created new user: {user_id}")


async def get_subscribed_users() -> List[int]:
    """Get all users with active strategies"""
    async with get_connection() as conn:
        rows = await conn.fetch("""
            SELECT user_id FROM users 
            WHERE is_allowed = 1 
            AND is_banned = 0
            AND (
                trade_scryptomera = TRUE OR 
                trade_scalper = TRUE OR 
                trade_elcaro = TRUE OR 
                trade_fibonacci = TRUE OR 
                trade_oi = TRUE
            )
        """)
        return [row["user_id"] for row in rows]


async def get_active_trading_users() -> List[int]:
    """Get users with API keys configured"""
    async with get_connection() as conn:
        rows = await conn.fetch("""
            SELECT user_id FROM users 
            WHERE is_allowed = 1 
            AND is_banned = 0
            AND (
                (demo_api_key IS NOT NULL AND demo_api_key != '') OR
                (real_api_key IS NOT NULL AND real_api_key != '')
            )
        """)
        return [row["user_id"] for row in rows]


async def get_all_users() -> List[Dict[str, Any]]:
    """Get all users"""
    async with get_connection() as conn:
        rows = await conn.fetch("SELECT * FROM users")
        return [dict(row) for row in rows]


# ═══════════════════════════════════════════════════════════════════════
# POSITION OPERATIONS
# ═══════════════════════════════════════════════════════════════════════

async def add_active_position(
    user_id: int,
    symbol: str,
    side: str,
    entry_price: float,
    size: float,
    strategy: str,
    account_type: str = "demo",
    leverage: float = None,
    sl_price: float = None,
    tp_price: float = None,
    exchange: str = "bybit"
):
    """Add or update active position with multitenancy support"""
    async with get_connection() as conn:
        await conn.execute("""
            INSERT INTO active_positions 
            (user_id, symbol, side, entry_price, size, strategy, account_type, 
             leverage, sl_price, tp_price, open_ts, exchange)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), $11)
            ON CONFLICT (user_id, symbol, account_type, exchange) 
            DO UPDATE SET 
                side = EXCLUDED.side,
                entry_price = EXCLUDED.entry_price,
                size = EXCLUDED.size,
                strategy = EXCLUDED.strategy,
                leverage = EXCLUDED.leverage,
                sl_price = EXCLUDED.sl_price,
                tp_price = EXCLUDED.tp_price
        """, user_id, symbol, side, entry_price, size, strategy, account_type,
            leverage, sl_price, tp_price, exchange)


async def remove_active_position(user_id: int, symbol: str, account_type: str = "demo", exchange: str = "bybit"):
    """Remove active position with multitenancy support"""
    async with get_connection() as conn:
        await conn.execute("""
            DELETE FROM active_positions 
            WHERE user_id = $1 AND symbol = $2 AND account_type = $3 AND exchange = $4
        """, user_id, symbol, account_type, exchange)


async def get_active_positions(user_id: int, account_type: str = None, exchange: str = None) -> List[Dict[str, Any]]:
    """Get active positions for user with multitenancy support.
    
    Args:
        user_id: User's Telegram ID
        account_type: 'demo', 'real', 'testnet', 'mainnet'
        exchange: 'bybit', 'hyperliquid' - for 4D schema filtering
    """
    async with get_connection() as conn:
        query = "SELECT * FROM active_positions WHERE user_id = $1"
        params = [user_id]
        param_idx = 2
        
        if account_type:
            query += f" AND account_type = ${param_idx}"
            params.append(account_type)
            param_idx += 1
        
        if exchange:
            query += f" AND exchange = ${param_idx}"
            params.append(exchange)
            param_idx += 1
        
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]


async def get_all_active_positions() -> List[Dict[str, Any]]:
    """Get all active positions across all users"""
    async with get_connection() as conn:
        rows = await conn.fetch("SELECT * FROM active_positions")
        return [dict(row) for row in rows]


async def get_all_active_symbols() -> List[str]:
    """Get unique symbols with active positions"""
    async with get_connection() as conn:
        rows = await conn.fetch("""
            SELECT DISTINCT symbol FROM active_positions
        """)
        return [row["symbol"] for row in rows]


# ═══════════════════════════════════════════════════════════════════════
# TRADE LOG OPERATIONS
# ═══════════════════════════════════════════════════════════════════════

async def add_trade_log(
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
    exchange: str = "bybit"
) -> bool:
    """
    Add trade log with duplicate prevention and multitenancy support.
    Returns True if inserted, False if duplicate.
    """
    async with get_connection() as conn:
        # Check for duplicate (same trade within 24 hours)
        existing = await conn.fetchval("""
            SELECT 1 FROM trade_logs 
            WHERE user_id = $1 
            AND symbol = $2 
            AND side = $3
            AND ABS(entry_price - $4) < 0.0001
            AND ABS(pnl - $5) < 0.01
            AND ts > NOW() - INTERVAL '24 hours'
            AND exchange = $6
            LIMIT 1
        """, user_id, symbol, side, entry_price, pnl, exchange)
        
        if existing:
            logger.debug(f"Duplicate trade log skipped: {user_id} {symbol}")
            return False
        
        await conn.execute("""
            INSERT INTO trade_logs 
            (user_id, symbol, side, entry_price, exit_price, exit_reason, 
             pnl, pnl_pct, strategy, account_type, sl_pct, tp_pct, timeframe, exchange, ts)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, NOW())
        """, user_id, symbol, side, entry_price, exit_price, exit_reason,
            pnl, pnl_pct, strategy, account_type, sl_pct, tp_pct, timeframe, exchange)
        
        return True


async def get_trade_stats(
    user_id: int, 
    days: int = 30, 
    account_type: str = None,
    strategy: str = None,
    exchange: str = None
) -> Dict[str, Any]:
    """Get trading statistics for user with multitenancy support"""
    async with get_connection() as conn:
        conditions = ["user_id = $1", "ts > NOW() - $2::interval"]
        params = [user_id, f"{days} days"]
        
        if account_type:
            conditions.append(f"account_type = ${len(params) + 1}")
            params.append(account_type)
        
        if strategy:
            conditions.append(f"strategy = ${len(params) + 1}")
            params.append(strategy)
        
        if exchange:
            conditions.append(f"exchange = ${len(params) + 1}")
            params.append(exchange)
        
        where_clause = " AND ".join(conditions)
        
        row = await conn.fetchrow(f"""
            SELECT 
                COUNT(*) as total_trades,
                COUNT(*) FILTER (WHERE pnl > 0) as winning_trades,
                COUNT(*) FILTER (WHERE pnl < 0) as losing_trades,
                COALESCE(SUM(pnl), 0) as total_pnl,
                COALESCE(AVG(pnl), 0) as avg_pnl,
                COALESCE(MAX(pnl), 0) as best_trade,
                COALESCE(MIN(pnl), 0) as worst_trade,
                COALESCE(AVG(pnl_pct), 0) as avg_pnl_pct
            FROM trade_logs
            WHERE {where_clause}
        """, *params)
        
        result = dict(row)
        total = result["total_trades"]
        result["win_rate"] = (result["winning_trades"] / total * 100) if total > 0 else 0
        
        return result


async def get_stats_by_strategy(user_id: int, days: int = 30, account_type: str = None, exchange: str = None) -> Dict[str, Dict]:
    """Get stats grouped by strategy"""
    async with get_connection() as conn:
        conditions = ["user_id = $1", "ts > NOW() - $2::interval"]
        params = [user_id, f"{days} days"]
        
        if account_type:
            conditions.append(f"account_type = ${len(params) + 1}")
            params.append(account_type)
        
        if exchange:
            conditions.append(f"exchange = ${len(params) + 1}")
            params.append(exchange)
        
        where_clause = " AND ".join(conditions)
        
        rows = await conn.fetch(f"""
            SELECT 
                strategy,
                COUNT(*) as total_trades,
                COUNT(*) FILTER (WHERE pnl > 0) as winning_trades,
                COALESCE(SUM(pnl), 0) as total_pnl,
                COALESCE(AVG(pnl), 0) as avg_pnl
            FROM trade_logs
            WHERE {where_clause}
            GROUP BY strategy
        """, *params)
        
        result = {}
        for row in rows:
            strategy = row["strategy"] or "unknown"
            total = row["total_trades"]
            result[strategy] = {
                "total_trades": total,
                "winning_trades": row["winning_trades"],
                "total_pnl": float(row["total_pnl"]),
                "avg_pnl": float(row["avg_pnl"]),
                "win_rate": (row["winning_trades"] / total * 100) if total > 0 else 0
            }
        
        return result


# ═══════════════════════════════════════════════════════════════════════
# SIGNAL OPERATIONS
# ═══════════════════════════════════════════════════════════════════════

async def add_signal(
    symbol: str,
    side: str,
    strategy: str,
    entry_price: float = None,
    sl_price: float = None,
    tp_price: float = None,
    timeframe: str = None,
    metadata: Dict = None
) -> int:
    """Add new signal, returns signal_id"""
    async with get_connection() as conn:
        signal_id = await conn.fetchval("""
            INSERT INTO signals 
            (symbol, side, strategy, entry_price, sl_price, tp_price, timeframe, metadata, ts)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
            RETURNING id
        """, symbol, side, strategy, entry_price, sl_price, tp_price, 
            timeframe, metadata)
        return signal_id


async def get_last_signal_by_symbol(symbol: str, strategy: str = None) -> Optional[Dict]:
    """Get last signal for symbol"""
    async with get_connection() as conn:
        if strategy:
            row = await conn.fetchrow("""
                SELECT * FROM signals 
                WHERE symbol = $1 AND strategy = $2
                ORDER BY ts DESC LIMIT 1
            """, symbol, strategy)
        else:
            row = await conn.fetchrow("""
                SELECT * FROM signals 
                WHERE symbol = $1
                ORDER BY ts DESC LIMIT 1
            """, symbol)
        return dict(row) if row else None


# ═══════════════════════════════════════════════════════════════════════
# CREDENTIALS OPERATIONS
# ═══════════════════════════════════════════════════════════════════════

async def get_user_credentials(user_id: int, account_type: str = "demo") -> Optional[Tuple[str, str]]:
    """Get API credentials for user"""
    async with get_connection() as conn:
        if account_type == "demo":
            row = await conn.fetchrow("""
                SELECT demo_api_key, demo_api_secret FROM users WHERE user_id = $1
            """, user_id)
            if row and row["demo_api_key"]:
                return (row["demo_api_key"], row["demo_api_secret"])
        else:
            row = await conn.fetchrow("""
                SELECT real_api_key, real_api_secret FROM users WHERE user_id = $1
            """, user_id)
            if row and row["real_api_key"]:
                return (row["real_api_key"], row["real_api_secret"])
        return None


async def set_user_credentials(
    user_id: int, 
    api_key: str, 
    api_secret: str, 
    account_type: str = "demo"
):
    """Set API credentials for user"""
    async with get_connection() as conn:
        if account_type == "demo":
            await conn.execute("""
                UPDATE users SET demo_api_key = $1, demo_api_secret = $2 
                WHERE user_id = $3
            """, api_key, api_secret, user_id)
        else:
            await conn.execute("""
                UPDATE users SET real_api_key = $1, real_api_secret = $2 
                WHERE user_id = $3
            """, api_key, api_secret, user_id)


# ═══════════════════════════════════════════════════════════════════════
# HYPERLIQUID CREDENTIALS
# ═══════════════════════════════════════════════════════════════════════

async def get_hl_credentials(user_id: int) -> Dict[str, Any]:
    """Get HyperLiquid credentials"""
    async with get_connection() as conn:
        row = await conn.fetchrow("""
            SELECT hl_address, hl_private_key, hl_testnet, hl_enabled
            FROM users WHERE user_id = $1
        """, user_id)
        
        if row:
            return {
                "hl_address": row["hl_address"],
                "hl_private_key": row["hl_private_key"],
                "hl_testnet": row["hl_testnet"] or False,
                "hl_enabled": row["hl_enabled"] or False
            }
        return {}


async def set_hl_credentials(
    user_id: int,
    address: str,
    private_key: str,
    testnet: bool = False
):
    """Set HyperLiquid credentials"""
    async with get_connection() as conn:
        await conn.execute("""
            UPDATE users SET 
                hl_address = $1, 
                hl_private_key = $2, 
                hl_testnet = $3,
                hl_enabled = true
            WHERE user_id = $4
        """, address, private_key, testnet, user_id)


# ═══════════════════════════════════════════════════════════════════════
# LICENSE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════

async def get_user_license(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user license info"""
    async with get_connection() as conn:
        row = await conn.fetchrow("""
            SELECT * FROM user_licenses 
            WHERE user_id = $1 AND expires_at > NOW()
            ORDER BY expires_at DESC LIMIT 1
        """, user_id)
        return dict(row) if row else None


async def check_license_access(user_id: int, strategy: str) -> bool:
    """Check if user has access to strategy"""
    license_info = await get_user_license(user_id)
    
    if not license_info:
        return False
    
    license_type = license_info.get("license_type", "free")
    
    # Define strategy access by license type
    access_map = {
        "free": ["oi"],
        "basic": ["oi", "rsi_bb", "scalper"],
        "pro": ["oi", "rsi_bb", "scalper", "scryptomera", "fibonacci"],
        "enterprise": ["oi", "rsi_bb", "scalper", "scryptomera", "fibonacci", "elcaro"]
    }
    
    allowed = access_map.get(license_type, [])
    return strategy.lower() in allowed


# ═══════════════════════════════════════════════════════════════════════
# EXCHANGE TYPE
# ═══════════════════════════════════════════════════════════════════════

async def get_exchange_type(user_id: int) -> str:
    """Get active exchange for user"""
    async with get_connection() as conn:
        exchange = await conn.fetchval("""
            SELECT exchange_type FROM users WHERE user_id = $1
        """, user_id)
        return exchange or "bybit"


async def set_exchange_type(user_id: int, exchange_type: str):
    """Set active exchange"""
    async with get_connection() as conn:
        await conn.execute("""
            UPDATE users SET exchange_type = $1 WHERE user_id = $2
        """, exchange_type, user_id)


async def get_trading_mode(user_id: int) -> str:
    """Get trading mode (demo/real/both)"""
    async with get_connection() as conn:
        mode = await conn.fetchval("""
            SELECT trading_mode FROM users WHERE user_id = $1
        """, user_id)
        return mode or "demo"


async def set_trading_mode(user_id: int, mode: str):
    """Set trading mode"""
    async with get_connection() as conn:
        await conn.execute("""
            UPDATE users SET trading_mode = $1 WHERE user_id = $2
        """, mode, user_id)


# ═══════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════

async def health_check() -> Dict[str, Any]:
    """Check database health"""
    try:
        pool = await get_pool()
        
        async with get_connection() as conn:
            import time
            start = time.time()
            await conn.fetchval("SELECT 1")
            latency = (time.time() - start) * 1000
            
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            position_count = await conn.fetchval("SELECT COUNT(*) FROM active_positions")
        
        return {
            "status": "healthy",
            "latency_ms": round(latency, 2),
            "pool_size": pool.get_size(),
            "pool_free": pool.get_idle_size(),
            "users": user_count,
            "active_positions": position_count
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# ═══════════════════════════════════════════════════════════════════════
# SCHEMA MIGRATION
# ═══════════════════════════════════════════════════════════════════════

SCHEMA_SQL = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    -- API Keys
    demo_api_key TEXT,
    demo_api_secret TEXT,
    real_api_key TEXT,
    real_api_secret TEXT,
    trading_mode TEXT DEFAULT 'demo',
    exchange_type TEXT DEFAULT 'bybit',
    -- HyperLiquid
    hl_address TEXT,
    hl_private_key TEXT,
    hl_testnet BOOLEAN DEFAULT FALSE,
    hl_enabled BOOLEAN DEFAULT FALSE,
    -- Trading Settings
    percent REAL DEFAULT 1.0,
    tp_percent REAL DEFAULT 8.0,
    sl_percent REAL DEFAULT 3.0,
    use_atr INTEGER DEFAULT 1,
    coins TEXT DEFAULT 'ALL',
    -- Strategies
    trade_scryptomera INTEGER DEFAULT 0,
    trade_scalper INTEGER DEFAULT 0,
    trade_elcaro INTEGER DEFAULT 0,
    trade_fibonacci INTEGER DEFAULT 0,
    trade_oi INTEGER DEFAULT 1,
    strategy_settings JSONB,
    -- DCA
    dca_enabled INTEGER DEFAULT 0,
    dca_pct_1 REAL DEFAULT 10.0,
    dca_pct_2 REAL DEFAULT 25.0,
    -- Access
    is_allowed INTEGER DEFAULT 0,
    is_banned INTEGER DEFAULT 0,
    lang TEXT DEFAULT 'en',
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Active positions
CREATE TABLE IF NOT EXISTS active_positions (
    user_id BIGINT NOT NULL,
    symbol TEXT NOT NULL,
    account_type TEXT DEFAULT 'demo',
    side TEXT,
    entry_price REAL,
    size REAL,
    strategy TEXT,
    leverage REAL,
    sl_price REAL,
    tp_price REAL,
    dca_10_done INTEGER DEFAULT 0,
    dca_25_done INTEGER DEFAULT 0,
    open_ts TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, symbol, account_type)
);

-- Trade logs
CREATE TABLE IF NOT EXISTS trade_logs (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    symbol TEXT,
    side TEXT,
    entry_price REAL,
    exit_price REAL,
    exit_reason TEXT,
    pnl REAL,
    pnl_pct REAL,
    strategy TEXT,
    account_type TEXT DEFAULT 'demo',
    sl_pct REAL,
    tp_pct REAL,
    timeframe TEXT,
    ts TIMESTAMP DEFAULT NOW()
);

-- Signals
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    strategy TEXT NOT NULL,
    entry_price REAL,
    sl_price REAL,
    tp_price REAL,
    timeframe TEXT,
    metadata JSONB,
    ts TIMESTAMP DEFAULT NOW()
);

-- User licenses
CREATE TABLE IF NOT EXISTS user_licenses (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    license_type TEXT NOT NULL,
    starts_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    payment_id TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_allowed ON users(is_allowed) WHERE is_allowed = 1;
CREATE INDEX IF NOT EXISTS idx_positions_user ON active_positions(user_id);
CREATE INDEX IF NOT EXISTS idx_trade_logs_user_ts ON trade_logs(user_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_trade_logs_strategy ON trade_logs(strategy, ts DESC);
CREATE INDEX IF NOT EXISTS idx_signals_symbol_ts ON signals(symbol, ts DESC);
CREATE INDEX IF NOT EXISTS idx_licenses_user ON user_licenses(user_id, expires_at DESC);
"""


async def init_schema():
    """Initialize database schema"""
    async with get_connection() as conn:
        await conn.execute(SCHEMA_SQL)
        logger.info("✅ PostgreSQL schema initialized")
