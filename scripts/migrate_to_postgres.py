#!/usr/bin/env python3
"""
SQLite to PostgreSQL Migration Script
=====================================
Migrates all data from SQLite (bot.db) to PostgreSQL.

Usage:
    python scripts/migrate_to_postgres.py --dry-run  # Preview changes
    python scripts/migrate_to_postgres.py            # Execute migration
"""

import sqlite3
import asyncio
import asyncpg
import os
import sys
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Default paths
SQLITE_PATH = os.path.join(os.path.dirname(__file__), '..', 'bot.db')
POSTGRES_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://elcaro:elcaro@localhost:5432/elcaro'
)


# ═══════════════════════════════════════════════════════════════════════
# SCHEMA DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════

POSTGRES_SCHEMA = """
-- Drop existing tables (careful in production!)
-- DROP TABLE IF EXISTS trade_logs CASCADE;
-- DROP TABLE IF EXISTS active_positions CASCADE;
-- DROP TABLE IF EXISTS signals CASCADE;
-- DROP TABLE IF EXISTS user_licenses CASCADE;
-- DROP TABLE IF EXISTS pending_limit_orders CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;

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
    raw_json TEXT,
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

-- Pending limit orders
CREATE TABLE IF NOT EXISTS pending_limit_orders (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    price REAL NOT NULL,
    qty REAL,
    strategy TEXT,
    account_type TEXT DEFAULT 'demo',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Pyramid tracking
CREATE TABLE IF NOT EXISTS pyramid_state (
    user_id BIGINT NOT NULL,
    symbol TEXT NOT NULL,
    count INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, symbol)
);

-- Config storage
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_allowed ON users(is_allowed) WHERE is_allowed = TRUE;
CREATE INDEX IF NOT EXISTS idx_positions_user ON active_positions(user_id);
CREATE INDEX IF NOT EXISTS idx_positions_symbol ON active_positions(symbol);
CREATE INDEX IF NOT EXISTS idx_trade_logs_user_ts ON trade_logs(user_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_trade_logs_strategy ON trade_logs(strategy, ts DESC);
CREATE INDEX IF NOT EXISTS idx_trade_logs_account ON trade_logs(account_type, ts DESC);
CREATE INDEX IF NOT EXISTS idx_signals_symbol_ts ON signals(symbol, ts DESC);
CREATE INDEX IF NOT EXISTS idx_signals_strategy ON signals(strategy, ts DESC);
CREATE INDEX IF NOT EXISTS idx_licenses_user ON user_licenses(user_id, expires_at DESC);
"""


# ═══════════════════════════════════════════════════════════════════════
# MIGRATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def get_sqlite_connection(db_path: str) -> sqlite3.Connection:
    """Get SQLite connection"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_sqlite_tables(conn: sqlite3.Connection) -> List[str]:
    """Get list of tables in SQLite"""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    return [row[0] for row in cursor.fetchall()]


def get_table_data(conn: sqlite3.Connection, table: str) -> List[Dict]:
    """Get all data from a SQLite table"""
    cursor = conn.execute(f"SELECT * FROM {table}")
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_table_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    """Get column names for a table"""
    cursor = conn.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cursor.fetchall()]


async def create_postgres_schema(pool: asyncpg.Pool):
    """Create PostgreSQL schema"""
    async with pool.acquire() as conn:
        await conn.execute(POSTGRES_SCHEMA)
    logger.info("✅ PostgreSQL schema created")


async def migrate_table(
    pool: asyncpg.Pool,
    table: str,
    data: List[Dict],
    column_mapping: Optional[Dict[str, str]] = None
) -> int:
    """Migrate data from SQLite table to PostgreSQL"""
    if not data:
        logger.info(f"  ⏭️  {table}: No data to migrate")
        return 0
    
    # Get columns from first row
    columns = list(data[0].keys())
    
    # Apply column mapping if provided
    if column_mapping:
        columns = [column_mapping.get(c, c) for c in columns]
    
    # Filter out columns that don't exist in PostgreSQL
    # (will be handled per-table below)
    
    async with pool.acquire() as conn:
        migrated = 0
        
        for row in data:
            try:
                # Build INSERT statement
                values = list(row.values())
                placeholders = ", ".join(f"${i+1}" for i in range(len(values)))
                cols = ", ".join(columns)
                
                # Handle conflicts
                if table == "users":
                    query = f"""
                        INSERT INTO {table} ({cols}) VALUES ({placeholders})
                        ON CONFLICT (user_id) DO UPDATE SET updated_at = NOW()
                    """
                elif table == "active_positions":
                    query = f"""
                        INSERT INTO {table} ({cols}) VALUES ({placeholders})
                        ON CONFLICT (user_id, symbol, account_type) DO NOTHING
                    """
                elif table == "config":
                    query = f"""
                        INSERT INTO {table} ({cols}) VALUES ({placeholders})
                        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                    """
                else:
                    query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
                
                await conn.execute(query, *values)
                migrated += 1
                
            except Exception as e:
                logger.warning(f"  ⚠️  Row error in {table}: {e}")
                continue
        
        return migrated


async def migrate_users(pool: asyncpg.Pool, sqlite_conn: sqlite3.Connection) -> int:
    """Migrate users table with column filtering"""
    cursor = sqlite_conn.execute("SELECT * FROM users")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    # PostgreSQL users table columns
    pg_columns = [
        'user_id', 'demo_api_key', 'demo_api_secret', 'real_api_key', 'real_api_secret',
        'trading_mode', 'exchange_type', 'hl_address', 'hl_private_key', 'hl_testnet',
        'hl_enabled', 'percent', 'tp_percent', 'sl_percent', 'use_atr', 'coins',
        'trade_scryptomera', 'trade_scalper', 'trade_elcaro', 'trade_fibonacci',
        'trade_oi', 'strategy_settings', 'dca_enabled', 'dca_pct_1', 'dca_pct_2',
        'is_allowed', 'is_banned', 'lang'
    ]
    
    # Boolean columns that need conversion from INTEGER (0/1) to bool
    boolean_columns = {'hl_testnet', 'hl_enabled'}
    
    # Map SQLite columns to PostgreSQL columns
    col_indices = {}
    for i, col in enumerate(columns):
        if col in pg_columns:
            col_indices[col] = i
    
    migrated = 0
    async with pool.acquire() as conn:
        for row in rows:
            try:
                # Build data dict with only matching columns
                data = {}
                for col in pg_columns:
                    if col in col_indices:
                        value = row[col_indices[col]]
                        # Convert INTEGER to boolean for boolean columns
                        if col in boolean_columns:
                            value = bool(value) if value is not None else False
                        data[col] = value
                
                if 'user_id' not in data:
                    continue
                
                cols = list(data.keys())
                values = list(data.values())
                placeholders = ", ".join(f"${i+1}" for i in range(len(values)))
                
                query = f"""
                    INSERT INTO users ({', '.join(cols)}) VALUES ({placeholders})
                    ON CONFLICT (user_id) DO UPDATE SET updated_at = NOW()
                """
                
                await conn.execute(query, *values)
                migrated += 1
                
            except Exception as e:
                logger.warning(f"  ⚠️  User migration error: {e}")
                continue
    
    return migrated


async def migrate_trade_logs(pool: asyncpg.Pool, sqlite_conn: sqlite3.Connection) -> int:
    """Migrate trade_logs table"""
    try:
        cursor = sqlite_conn.execute("SELECT * FROM trade_logs")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        logger.info("  ⏭️  trade_logs: Table does not exist in SQLite")
        return 0
    
    pg_columns = [
        'user_id', 'symbol', 'side', 'entry_price', 'exit_price', 'exit_reason',
        'pnl', 'pnl_pct', 'strategy', 'account_type', 'sl_pct', 'tp_pct', 'timeframe', 'ts'
    ]
    
    # Datetime columns that need conversion from string
    datetime_columns = {'ts'}
    
    col_indices = {col: i for i, col in enumerate(columns) if col in pg_columns}
    logger.info(f"  📋 trade_logs: mapping {len(col_indices)} columns from SQLite")
    
    migrated = 0
    errors = 0
    async with pool.acquire() as conn:
        for row in rows:
            try:
                data = {}
                for col, idx in col_indices.items():
                    value = row[idx]
                    # Convert string timestamp to datetime
                    if col in datetime_columns and value and isinstance(value, str):
                        try:
                            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
                            except ValueError:
                                value = datetime.now()
                    data[col] = value
                
                if 'user_id' not in data:
                    continue
                
                cols = list(data.keys())
                values = list(data.values())
                placeholders = ", ".join(f"${i+1}" for i in range(len(values)))
                
                query = f"INSERT INTO trade_logs ({', '.join(cols)}) VALUES ({placeholders})"
                await conn.execute(query, *values)
                migrated += 1
                
            except Exception as e:
                errors += 1
                if errors <= 5:
                    logger.warning(f"  ⚠️  trade_logs error #{errors}: {e}")
                continue
    
    if errors > 5:
        logger.warning(f"  ⚠️  trade_logs: {errors} total errors (showing first 5)")
    
    return migrated


async def migrate_active_positions(pool: asyncpg.Pool, sqlite_conn: sqlite3.Connection) -> int:
    """Migrate active_positions table"""
    try:
        cursor = sqlite_conn.execute("SELECT * FROM active_positions")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        logger.info("  ⏭️  active_positions: Table does not exist in SQLite")
        return 0
    
    pg_columns = [
        'user_id', 'symbol', 'account_type', 'side', 'entry_price', 'size',
        'strategy', 'leverage', 'sl_price', 'tp_price', 'dca_10_done', 'dca_25_done', 'open_ts'
    ]
    
    # Datetime columns that need conversion
    datetime_columns = {'open_ts'}
    
    col_indices = {col: i for i, col in enumerate(columns) if col in pg_columns}
    logger.info(f"  📋 active_positions: mapping {len(col_indices)} columns from SQLite")
    
    migrated = 0
    errors = 0
    async with pool.acquire() as conn:
        for row in rows:
            try:
                data = {}
                for col, idx in col_indices.items():
                    value = row[idx]
                    # Convert string timestamp to datetime
                    if col in datetime_columns and value and isinstance(value, str):
                        try:
                            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
                            except ValueError:
                                value = datetime.now()
                    data[col] = value
                
                if 'user_id' not in data or 'symbol' not in data:
                    continue
                
                # Default account_type
                if 'account_type' not in data:
                    data['account_type'] = 'demo'
                
                cols = list(data.keys())
                values = list(data.values())
                placeholders = ", ".join(f"${i+1}" for i in range(len(values)))
                
                query = f"""
                    INSERT INTO active_positions ({', '.join(cols)}) VALUES ({placeholders})
                    ON CONFLICT (user_id, symbol, account_type) DO NOTHING
                """
                await conn.execute(query, *values)
                migrated += 1
                
            except Exception as e:
                errors += 1
                if errors <= 5:
                    logger.warning(f"  ⚠️  active_positions error #{errors}: {e}")
                continue
    
    if errors > 5:
        logger.warning(f"  ⚠️  active_positions: {errors} total errors (showing first 5)")
    
    return migrated


async def migrate_signals(pool: asyncpg.Pool, sqlite_conn: sqlite3.Connection) -> int:
    """Migrate signals table"""
    try:
        cursor = sqlite_conn.execute("SELECT * FROM signals")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        logger.info("  ⏭️  signals: Table does not exist in SQLite")
        return 0
    
    pg_columns = ['symbol', 'side', 'strategy', 'entry_price', 'sl_price', 'tp_price', 'timeframe', 'raw_json', 'ts']
    
    # Datetime columns that need conversion
    datetime_columns = {'ts'}
    
    col_indices = {col: i for i, col in enumerate(columns) if col in pg_columns}
    logger.info(f"  📋 signals: mapping {len(col_indices)} columns from SQLite")
    
    migrated = 0
    errors = 0
    async with pool.acquire() as conn:
        for row in rows:
            try:
                data = {}
                for col, idx in col_indices.items():
                    value = row[idx]
                    # Convert string timestamp to datetime
                    if col in datetime_columns and value and isinstance(value, str):
                        try:
                            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
                            except ValueError:
                                value = datetime.now()
                    data[col] = value
                
                if 'symbol' not in data or 'side' not in data:
                    continue
                
                if 'strategy' not in data:
                    data['strategy'] = 'unknown'
                
                cols = list(data.keys())
                values = list(data.values())
                placeholders = ", ".join(f"${i+1}" for i in range(len(values)))
                
                query = f"INSERT INTO signals ({', '.join(cols)}) VALUES ({placeholders})"
                await conn.execute(query, *values)
                migrated += 1
                
            except Exception as e:
                errors += 1
                if errors <= 5:
                    logger.warning(f"  ⚠️  signals error #{errors}: {e}")
                continue
    
    if errors > 5:
        logger.warning(f"  ⚠️  signals: {errors} total errors (showing first 5)")
    
    return migrated


async def run_migration(sqlite_path: str, postgres_url: str, dry_run: bool = False):
    """Run the full migration"""
    logger.info("=" * 60)
    logger.info("SQLite to PostgreSQL Migration")
    logger.info("=" * 60)
    logger.info(f"SQLite: {sqlite_path}")
    logger.info(f"PostgreSQL: {postgres_url.split('@')[1] if '@' in postgres_url else postgres_url}")
    logger.info(f"Dry Run: {dry_run}")
    logger.info("=" * 60)
    
    # Connect to SQLite
    if not os.path.exists(sqlite_path):
        logger.error(f"❌ SQLite database not found: {sqlite_path}")
        return False
    
    sqlite_conn = get_sqlite_connection(sqlite_path)
    tables = get_sqlite_tables(sqlite_conn)
    logger.info(f"📂 SQLite tables: {tables}")
    
    # Get row counts
    for table in tables:
        try:
            cursor = sqlite_conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            logger.info(f"  📊 {table}: {count} rows")
        except Exception as e:
            logger.warning(f"  ⚠️  {table}: {e}")
    
    if dry_run:
        logger.info("\n🔍 DRY RUN - No changes made")
        sqlite_conn.close()
        return True
    
    # Connect to PostgreSQL
    logger.info("\n📡 Connecting to PostgreSQL...")
    try:
        pool = await asyncpg.create_pool(postgres_url, min_size=2, max_size=10)
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        sqlite_conn.close()
        return False
    
    logger.info("✅ PostgreSQL connected")
    
    # Create schema
    logger.info("\n📝 Creating PostgreSQL schema...")
    await create_postgres_schema(pool)
    
    # Migrate tables
    logger.info("\n📦 Migrating data...")
    
    results = {}
    
    # Users
    logger.info("  🔄 Migrating users...")
    results['users'] = await migrate_users(pool, sqlite_conn)
    logger.info(f"  ✅ users: {results['users']} rows")
    
    # Trade logs
    logger.info("  🔄 Migrating trade_logs...")
    results['trade_logs'] = await migrate_trade_logs(pool, sqlite_conn)
    logger.info(f"  ✅ trade_logs: {results['trade_logs']} rows")
    
    # Active positions
    logger.info("  🔄 Migrating active_positions...")
    results['active_positions'] = await migrate_active_positions(pool, sqlite_conn)
    logger.info(f"  ✅ active_positions: {results['active_positions']} rows")
    
    # Signals
    logger.info("  🔄 Migrating signals...")
    results['signals'] = await migrate_signals(pool, sqlite_conn)
    logger.info(f"  ✅ signals: {results['signals']} rows")
    
    # Verify migration
    logger.info("\n🔍 Verifying migration...")
    async with pool.acquire() as conn:
        for table in ['users', 'trade_logs', 'active_positions', 'signals']:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            logger.info(f"  📊 PostgreSQL {table}: {count} rows")
    
    # Cleanup
    await pool.close()
    sqlite_conn.close()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ MIGRATION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total migrated:")
    for table, count in results.items():
        logger.info(f"  • {table}: {count} rows")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Migrate SQLite to PostgreSQL')
    parser.add_argument('--sqlite', default=SQLITE_PATH, help='SQLite database path')
    parser.add_argument('--postgres', default=POSTGRES_URL, help='PostgreSQL connection URL')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    
    args = parser.parse_args()
    
    success = asyncio.run(run_migration(
        sqlite_path=args.sqlite,
        postgres_url=args.postgres,
        dry_run=args.dry_run
    ))
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
