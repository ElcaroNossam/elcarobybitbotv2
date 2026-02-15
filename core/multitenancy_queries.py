"""
Multitenancy Queries - Optimized Database Queries for Multi-tenant Trading System

This module provides:
- Prepared statements for frequently executed queries
- Optimized indexes for 4D multitenancy (user_id, strategy, exchange, account_type)
- Query builders with proper isolation
- Batch query execution for high-performance scenarios

Best Practices Applied:
1. Prepared statements reduce query parsing overhead
2. Covering indexes for common query patterns
3. Parameterized queries prevent SQL injection
4. Query result caching integration
5. Connection pool integration

Usage:
    from core.multitenancy_queries import (
        get_user_settings_optimized,
        get_positions_for_monitoring,
        upsert_user_settings,
        MultitenantQueryBuilder,
    )
    
    # Fast settings lookup with caching
    settings = await get_user_settings_optimized(uid, strategy, exchange, account_type)
    
    # Batch position fetch for monitoring
    positions = await get_positions_for_monitoring(user_ids)
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# INDEX DEFINITIONS (для применения через миграцию)
# =============================================================================

RECOMMENDED_INDEXES = """
-- Multitenancy composite indexes for user_strategy_settings
-- PRIMARY KEY: (user_id, strategy, side) - SIMPLIFIED schema (Jan 2026)
-- NOTE: exchange/account_type columns exist but NOT in PRIMARY KEY

-- Index for strategy listing per user
CREATE INDEX IF NOT EXISTS idx_uss_user_enabled 
ON user_strategy_settings(user_id, enabled) 
WHERE enabled = TRUE;

-- Index for finding all users with specific strategy enabled
CREATE INDEX IF NOT EXISTS idx_uss_strategy_enabled 
ON user_strategy_settings(strategy, enabled) 
WHERE enabled = TRUE;

-- Covering index for settings lookup (simplified - no exchange/account_type)
CREATE INDEX IF NOT EXISTS idx_uss_covering 
ON user_strategy_settings(user_id, strategy, side) 
INCLUDE (enabled, percent, sl_percent, tp_percent, leverage, use_atr);

-- Indexes for active_positions
-- PRIMARY KEY: (user_id, symbol, account_type) - still 3D
-- Composite for user position lookup
CREATE INDEX IF NOT EXISTS idx_ap_user_account 
ON active_positions(user_id, account_type);

-- Index for symbol-based lookups (monitoring)
CREATE INDEX IF NOT EXISTS idx_ap_symbol_account 
ON active_positions(symbol, account_type);

-- Covering index for position monitoring
CREATE INDEX IF NOT EXISTS idx_ap_monitoring 
ON active_positions(user_id, account_type) 
INCLUDE (symbol, side, entry_price, size, sl_price, tp_price, strategy);

-- Indexes for trade_logs
-- Time-series index for recent trades
CREATE INDEX IF NOT EXISTS idx_tl_user_time 
ON trade_logs(user_id, ts DESC);

-- Strategy performance analysis
CREATE INDEX IF NOT EXISTS idx_tl_strategy_time 
ON trade_logs(strategy, ts DESC);

-- Account type filtering
CREATE INDEX IF NOT EXISTS idx_tl_account_time 
ON trade_logs(account_type, ts DESC);

-- Composite for detailed analysis
CREATE INDEX IF NOT EXISTS idx_tl_analysis 
ON trade_logs(user_id, strategy, account_type, ts DESC);

-- Indexes for users table
-- Active users lookup
CREATE INDEX IF NOT EXISTS idx_users_allowed 
ON users(is_allowed) 
WHERE is_allowed = 1;

-- Exchange type filtering
CREATE INDEX IF NOT EXISTS idx_users_exchange 
ON users(exchange_type, is_allowed) 
WHERE is_allowed = 1;
"""


# =============================================================================
# PREPARED STATEMENTS
# =============================================================================

@dataclass
class PreparedStatement:
    """Represents a prepared statement with its name and query"""
    name: str
    query: str
    param_types: Tuple[str, ...] = field(default_factory=tuple)


# Frequently used queries as prepared statements
PREPARED_STATEMENTS = {
    # User settings lookup - SIMPLIFIED to (user_id, strategy, side)
    # NOTE: exchange/account_type not used in simplified schema
    'get_user_settings': PreparedStatement(
        name='get_user_settings',
        query="""
            SELECT 
                enabled, percent, sl_percent, tp_percent, leverage,
                use_atr, atr_trigger_pct, atr_step_pct,
                order_type
            FROM user_strategy_settings
            WHERE user_id = $1 
              AND strategy = $2 
              AND side = $3
        """,
        param_types=('bigint', 'text', 'text')
    ),
    
    # All enabled strategies for a user
    'get_user_enabled_strategies': PreparedStatement(
        name='get_user_enabled_strategies',
        query="""
            SELECT strategy, exchange, account_type, percent, leverage
            FROM user_strategy_settings
            WHERE user_id = $1 AND enabled = TRUE
            ORDER BY strategy
        """,
        param_types=('bigint',)
    ),
    
    # User positions for specific account
    'get_user_positions': PreparedStatement(
        name='get_user_positions',
        query="""
            SELECT 
                symbol, side, entry_price, size, strategy,
                leverage, sl_price, tp_price, dca_10_done, dca_25_done, open_ts
            FROM active_positions
            WHERE user_id = $1 AND account_type = $2
            ORDER BY open_ts DESC
        """,
        param_types=('bigint', 'text')
    ),
    
    # Single position lookup
    'get_position': PreparedStatement(
        name='get_position',
        query="""
            SELECT 
                symbol, side, entry_price, size, strategy,
                leverage, sl_price, tp_price, dca_10_done, dca_25_done, open_ts, exchange
            FROM active_positions
            WHERE user_id = $1 AND symbol = $2 AND account_type = $3 AND exchange = $4
        """,
        param_types=('bigint', 'text', 'text', 'text')
    ),
    
    # User global settings fallback
    'get_user_global_settings': PreparedStatement(
        name='get_user_global_settings',
        query="""
            SELECT 
                percent, tp_percent, sl_percent, use_atr, leverage,
                dca_enabled, dca_pct_1, dca_pct_2,
                exchange_type, trading_mode
            FROM users
            WHERE user_id = $1
        """,
        param_types=('bigint',)
    ),
    
    # Active users for monitoring
    'get_active_users': PreparedStatement(
        name='get_active_users',
        query="""
            SELECT DISTINCT user_id, exchange_type, trading_mode
            FROM users
            WHERE is_allowed = 1 AND is_banned = 0
        """,
        param_types=()
    ),
    
    # Users with positions
    'get_users_with_positions': PreparedStatement(
        name='get_users_with_positions',
        query="""
            SELECT DISTINCT ap.user_id, u.exchange_type, u.trading_mode
            FROM active_positions ap
            JOIN users u ON ap.user_id = u.user_id
            WHERE u.is_allowed = 1 AND u.is_banned = 0
        """,
        param_types=()
    ),
    
    # Upsert user settings - 4D schema (user_id, strategy, side, exchange)
    'upsert_user_settings': PreparedStatement(
        name='upsert_user_settings',
        query="""
            INSERT INTO user_strategy_settings 
                (user_id, strategy, side, exchange, enabled, percent, sl_percent, tp_percent, leverage, use_atr, atr_trigger_pct, atr_step_pct, order_type)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            ON CONFLICT (user_id, strategy, side, exchange) 
            DO UPDATE SET
                enabled = EXCLUDED.enabled,
                percent = COALESCE(EXCLUDED.percent, user_strategy_settings.percent),
                sl_percent = COALESCE(EXCLUDED.sl_percent, user_strategy_settings.sl_percent),
                tp_percent = COALESCE(EXCLUDED.tp_percent, user_strategy_settings.tp_percent),
                leverage = COALESCE(EXCLUDED.leverage, user_strategy_settings.leverage),
                use_atr = COALESCE(EXCLUDED.use_atr, user_strategy_settings.use_atr),
                atr_trigger_pct = COALESCE(EXCLUDED.atr_trigger_pct, user_strategy_settings.atr_trigger_pct),
                atr_step_pct = COALESCE(EXCLUDED.atr_step_pct, user_strategy_settings.atr_step_pct),
                order_type = COALESCE(EXCLUDED.order_type, user_strategy_settings.order_type),
                updated_at = NOW()
            RETURNING *
        """,
        param_types=('bigint', 'text', 'text', 'text', 'boolean', 'real', 'real', 'real', 'integer', 'boolean', 'real', 'real', 'text')
    ),
    
    # Add position
    'add_position': PreparedStatement(
        name='add_position',
        query="""
            INSERT INTO active_positions
                (user_id, symbol, account_type, exchange, side, entry_price, size, strategy, leverage, sl_price, tp_price)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (user_id, symbol, account_type, exchange)
            DO UPDATE SET
                side = EXCLUDED.side,
                entry_price = EXCLUDED.entry_price,
                size = EXCLUDED.size,
                strategy = EXCLUDED.strategy,
                leverage = EXCLUDED.leverage,
                sl_price = EXCLUDED.sl_price,
                tp_price = EXCLUDED.tp_price
            RETURNING *
        """,
        param_types=('bigint', 'text', 'text', 'text', 'text', 'real', 'real', 'text', 'real', 'real', 'real')
    ),
    
    # Remove position
    'remove_position': PreparedStatement(
        name='remove_position',
        query="""
            DELETE FROM active_positions
            WHERE user_id = $1 AND symbol = $2 AND account_type = $3 AND exchange = $4
            RETURNING *
        """,
        param_types=('bigint', 'text', 'text', 'text')
    ),
    
    # Add trade log
    'add_trade_log': PreparedStatement(
        name='add_trade_log',
        query="""
            INSERT INTO trade_logs
                (user_id, symbol, side, entry_price, exit_price, exit_reason, 
                 pnl, pnl_pct, strategy, account_type, sl_pct, tp_pct, exchange)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            RETURNING id
        """,
        param_types=('bigint', 'text', 'text', 'real', 'real', 'text', 
                     'real', 'real', 'text', 'text', 'real', 'real', 'text')
    ),
}


# =============================================================================
# ASYNC PREPARED STATEMENT MANAGER
# =============================================================================

class PreparedStatementManager:
    """
    Manages prepared statements for asyncpg connections.
    
    Prepared statements are cached per-connection to avoid re-preparation overhead.
    Uses connection's prepare() method which is automatically cached by asyncpg.
    """
    
    def __init__(self):
        self._prepared: Dict[int, Set[str]] = {}  # conn_id -> set of prepared names
        self._lock = asyncio.Lock()
    
    async def get_prepared(self, conn, stmt_name: str):
        """
        Get or create a prepared statement for the connection.
        
        Args:
            conn: asyncpg connection
            stmt_name: Name of the prepared statement from PREPARED_STATEMENTS
            
        Returns:
            Prepared statement object
        """
        if stmt_name not in PREPARED_STATEMENTS:
            raise ValueError(f"Unknown prepared statement: {stmt_name}")
        
        stmt = PREPARED_STATEMENTS[stmt_name]
        conn_id = id(conn)
        
        # Check if already prepared for this connection
        if conn_id in self._prepared and stmt_name in self._prepared[conn_id]:
            # asyncpg caches prepared statements internally
            return await conn.prepare(stmt.query)
        
        # Prepare the statement
        async with self._lock:
            if conn_id not in self._prepared:
                self._prepared[conn_id] = set()
            
            prepared = await conn.prepare(stmt.query)
            self._prepared[conn_id].add(stmt_name)
            
            return prepared
    
    def on_connection_close(self, conn):
        """Called when a connection is closed to cleanup tracking"""
        conn_id = id(conn)
        self._prepared.pop(conn_id, None)


# Singleton instance
_stmt_manager = PreparedStatementManager()


# =============================================================================
# OPTIMIZED QUERY FUNCTIONS
# =============================================================================

async def get_user_settings_optimized(
    pool,
    user_id: int,
    strategy: str,
    exchange: str = 'bybit',
    account_type: str = 'demo',
    use_cache: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Get user strategy settings with optimized prepared statement.
    
    Uses prepared statement for minimal parsing overhead and
    integrates with cache layer for repeated lookups.
    
    Args:
        pool: asyncpg connection pool
        user_id: User's Telegram ID
        strategy: Strategy name (e.g., 'OI', 'Scryptomera')
        exchange: Exchange name ('bybit' or 'hyperliquid')
        account_type: Account type ('demo', 'real', 'testnet', 'mainnet')
        use_cache: Whether to use cache (default True)
        
    Returns:
        Settings dict or None if not found
    """
    # Try cache first
    if use_cache:
        from .cache import user_strategy_cache
        cache_key = f"{user_id}:{strategy}:{exchange}:{account_type}"
        cached = user_strategy_cache.get(cache_key)
        if cached is not None:
            return cached
    
    async with pool.acquire() as conn:
        prepared = await _stmt_manager.get_prepared(conn, 'get_user_settings')
        row = await prepared.fetchrow(user_id, strategy.lower(), exchange, account_type)
        
        if row:
            result = dict(row)
            # Cache the result
            if use_cache:
                from .cache import user_strategy_cache
                user_strategy_cache.set(cache_key, result)
            return result
        
        return None


async def get_user_enabled_strategies(
    pool,
    user_id: int
) -> List[Dict[str, Any]]:
    """
    Get all enabled strategies for a user.
    
    Args:
        pool: asyncpg connection pool
        user_id: User's Telegram ID
        
    Returns:
        List of enabled strategy configs
    """
    async with pool.acquire() as conn:
        prepared = await _stmt_manager.get_prepared(conn, 'get_user_enabled_strategies')
        rows = await prepared.fetch(user_id)
        return [dict(row) for row in rows]


async def get_positions_for_monitoring(
    pool,
    user_ids: Optional[List[int]] = None,
    account_type: Optional[str] = None
) -> Dict[int, List[Dict[str, Any]]]:
    """
    Batch fetch positions for monitoring loop.
    
    Optimized for bulk retrieval with optional filtering.
    
    Args:
        pool: asyncpg connection pool
        user_ids: Optional list of user IDs to filter
        account_type: Optional account type filter
        
    Returns:
        Dict mapping user_id to list of positions
    """
    async with pool.acquire() as conn:
        # Build query dynamically based on filters
        query = """
            SELECT 
                user_id, symbol, account_type, side, entry_price, 
                size, strategy, leverage, sl_price, tp_price,
                dca_10_done, dca_25_done, open_ts
            FROM active_positions
            WHERE 1=1
        """
        params = []
        param_idx = 1
        
        if user_ids:
            query += f" AND user_id = ANY(${param_idx})"
            params.append(user_ids)
            param_idx += 1
        
        if account_type:
            query += f" AND account_type = ${param_idx}"
            params.append(account_type)
            param_idx += 1
        
        query += " ORDER BY user_id, open_ts DESC"
        
        rows = await conn.fetch(query, *params)
        
        # Group by user_id
        result: Dict[int, List[Dict[str, Any]]] = {}
        for row in rows:
            uid = row['user_id']
            if uid not in result:
                result[uid] = []
            result[uid].append(dict(row))
        
        return result


async def upsert_user_settings(
    pool,
    user_id: int,
    strategy: str,
    exchange: str,
    account_type: str,
    settings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Insert or update user strategy settings atomically.
    
    Uses ON CONFLICT DO UPDATE for atomic upsert.
    
    Args:
        pool: asyncpg connection pool
        user_id: User's Telegram ID
        strategy: Strategy name
        exchange: Exchange name
        account_type: Account type
        settings: Dict with settings to update
        
    Returns:
        Updated settings dict
    """
    async with pool.acquire() as conn:
        prepared = await _stmt_manager.get_prepared(conn, 'upsert_user_settings')
        row = await prepared.fetchrow(
            user_id,
            strategy.lower(),
            exchange,
            account_type,
            settings.get('enabled', False),
            settings.get('percent'),
            settings.get('sl_percent'),
            settings.get('tp_percent'),
            settings.get('leverage')
        )
        
        result = dict(row) if row else {}
        
        # Invalidate cache
        from .cache import user_strategy_cache
        cache_key = f"{user_id}:{strategy.lower()}:{exchange}:{account_type}"
        user_strategy_cache.delete(cache_key)
        
        return result


async def get_user_global_settings(
    pool,
    user_id: int
) -> Optional[Dict[str, Any]]:
    """
    Get user's global settings (fallback when strategy-specific not found).
    
    Args:
        pool: asyncpg connection pool
        user_id: User's Telegram ID
        
    Returns:
        Global settings dict or None
    """
    async with pool.acquire() as conn:
        prepared = await _stmt_manager.get_prepared(conn, 'get_user_global_settings')
        row = await prepared.fetchrow(user_id)
        return dict(row) if row else None


async def get_effective_settings(
    pool,
    user_id: int,
    strategy: str,
    exchange: str = 'bybit',
    account_type: str = 'demo',
    side: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get effective settings with proper fallback chain:
    1. Side-specific (long_percent, short_percent)
    2. Strategy-specific (percent, sl_percent, tp_percent)
    3. Global user settings (from users table)
    
    Args:
        pool: asyncpg connection pool
        user_id: User's Telegram ID
        strategy: Strategy name
        exchange: Exchange name
        account_type: Account type
        side: Optional side ('Buy'/'Sell' or 'long'/'short') for side-specific settings
        
    Returns:
        Effective settings dict with all values resolved
    """
    # Get strategy-specific settings
    strategy_settings = await get_user_settings_optimized(
        pool, user_id, strategy, exchange, account_type
    )
    
    # Get global settings for fallback
    global_settings = await get_user_global_settings(pool, user_id)
    
    if not global_settings:
        global_settings = {
            'percent': 1.0,
            'tp_percent': 25.0,
            'sl_percent': 30.0,
            'leverage': 10.0,
            'use_atr': 1,
        }
    
    # Start with global settings as base
    result = {
        'percent': global_settings.get('percent', 1.0),
        'sl_percent': global_settings.get('sl_percent', 30.0),
        'tp_percent': global_settings.get('tp_percent', 25.0),
        'leverage': global_settings.get('leverage', 10.0),
        'use_atr': global_settings.get('use_atr', 1),
    }
    
    # Override with strategy-specific settings if present
    if strategy_settings:
        for key in ['percent', 'sl_percent', 'tp_percent', 'leverage', 'use_atr', 
                    'atr_periods', 'atr_multiplier_sl', 'atr_trigger_pct', 
                    'order_type', 'direction']:
            if strategy_settings.get(key) is not None:
                result[key] = strategy_settings[key]
        
        # Apply side-specific settings if requested
        if side:
            side_lower = side.lower()
            is_long = side_lower in ('buy', 'long')
            
            if is_long:
                if strategy_settings.get('long_percent') is not None:
                    result['percent'] = strategy_settings['long_percent']
                if strategy_settings.get('long_sl_percent') is not None:
                    result['sl_percent'] = strategy_settings['long_sl_percent']
                if strategy_settings.get('long_tp_percent') is not None:
                    result['tp_percent'] = strategy_settings['long_tp_percent']
            else:
                if strategy_settings.get('short_percent') is not None:
                    result['percent'] = strategy_settings['short_percent']
                if strategy_settings.get('short_sl_percent') is not None:
                    result['sl_percent'] = strategy_settings['short_sl_percent']
                if strategy_settings.get('short_tp_percent') is not None:
                    result['tp_percent'] = strategy_settings['short_tp_percent']
        
        result['enabled'] = strategy_settings.get('enabled', False)
    else:
        result['enabled'] = False
    
    return result


# =============================================================================
# QUERY BUILDER FOR COMPLEX QUERIES
# =============================================================================

class MultitenantQueryBuilder:
    """
    Fluent query builder for multitenant queries.
    
    Provides type-safe query construction with proper parameterization.
    
    Usage:
        builder = MultitenantQueryBuilder('user_strategy_settings')
        query, params = (builder
            .select('strategy', 'enabled', 'percent')
            .where_user(user_id)
            .where_exchange('bybit')
            .where_enabled()
            .build())
    """
    
    def __init__(self, table: str):
        self.table = table
        self._select_cols: List[str] = ['*']
        self._where_clauses: List[str] = []
        self._params: List[Any] = []
        self._order_by: Optional[str] = None
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
    
    def select(self, *columns: str) -> 'MultitenantQueryBuilder':
        """Select specific columns"""
        self._select_cols = list(columns)
        return self
    
    def where_user(self, user_id: int) -> 'MultitenantQueryBuilder':
        """Filter by user_id"""
        self._params.append(user_id)
        self._where_clauses.append(f"user_id = ${len(self._params)}")
        return self
    
    def where_strategy(self, strategy: str) -> 'MultitenantQueryBuilder':
        """Filter by strategy"""
        self._params.append(strategy.lower())
        self._where_clauses.append(f"strategy = ${len(self._params)}")
        return self
    
    def where_exchange(self, exchange: str) -> 'MultitenantQueryBuilder':
        """Filter by exchange"""
        self._params.append(exchange)
        self._where_clauses.append(f"exchange = ${len(self._params)}")
        return self
    
    def where_account_type(self, account_type: str) -> 'MultitenantQueryBuilder':
        """Filter by account_type"""
        self._params.append(account_type)
        self._where_clauses.append(f"account_type = ${len(self._params)}")
        return self
    
    def where_enabled(self, enabled: bool = True) -> 'MultitenantQueryBuilder':
        """Filter by enabled status"""
        self._params.append(enabled)
        self._where_clauses.append(f"enabled = ${len(self._params)}")
        return self
    
    def where_in_users(self, user_ids: List[int]) -> 'MultitenantQueryBuilder':
        """Filter by list of user IDs"""
        self._params.append(user_ids)
        self._where_clauses.append(f"user_id = ANY(${len(self._params)})")
        return self
    
    def where_raw(self, clause: str, *params: Any) -> 'MultitenantQueryBuilder':
        """Add raw WHERE clause with parameters"""
        for param in params:
            self._params.append(param)
        # Replace ? with $N placeholders
        adjusted_clause = clause
        for i, _ in enumerate(params):
            adjusted_clause = adjusted_clause.replace('?', f'${len(self._params) - len(params) + i + 1}', 1)
        self._where_clauses.append(adjusted_clause)
        return self
    
    def order_by(self, column: str, desc: bool = False) -> 'MultitenantQueryBuilder':
        """Set ORDER BY clause"""
        direction = 'DESC' if desc else 'ASC'
        self._order_by = f"{column} {direction}"
        return self
    
    def limit(self, limit: int) -> 'MultitenantQueryBuilder':
        """Set LIMIT"""
        self._limit = limit
        return self
    
    def offset(self, offset: int) -> 'MultitenantQueryBuilder':
        """Set OFFSET"""
        self._offset = offset
        return self
    
    def build(self) -> Tuple[str, List[Any]]:
        """Build the final query and parameters"""
        cols = ', '.join(self._select_cols)
        query = f"SELECT {cols} FROM {self.table}"
        
        if self._where_clauses:
            query += " WHERE " + " AND ".join(self._where_clauses)
        
        if self._order_by:
            query += f" ORDER BY {self._order_by}"
        
        if self._limit is not None:
            query += f" LIMIT {self._limit}"
        
        if self._offset is not None:
            query += f" OFFSET {self._offset}"
        
        return query, self._params


# =============================================================================
# INDEX MANAGEMENT
# =============================================================================

async def ensure_indexes(pool) -> List[str]:
    """
    Ensure all recommended indexes exist.
    
    Returns list of created indexes.
    """
    created = []
    
    async with pool.acquire() as conn:
        # Split indexes into individual statements
        statements = [s.strip() for s in RECOMMENDED_INDEXES.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for stmt in statements:
            if not stmt:
                continue
            try:
                # Extract index name from CREATE INDEX statement
                if 'CREATE INDEX' in stmt.upper():
                    # Parse: CREATE INDEX IF NOT EXISTS idx_name ON ...
                    parts = stmt.split()
                    idx_name = None
                    for i, part in enumerate(parts):
                        if part.upper() == 'EXISTS':
                            idx_name = parts[i + 1]
                            break
                        elif part.upper() == 'INDEX' and parts[i + 1].upper() != 'IF':
                            idx_name = parts[i + 1]
                            break
                    
                    await conn.execute(stmt)
                    if idx_name:
                        created.append(idx_name)
                        logger.info(f"Created index: {idx_name}")
            except Exception as e:
                # Index might already exist or other issue
                logger.debug(f"Index creation skipped: {e}")
    
    return created


async def analyze_tables(pool, tables: List[str] = None) -> None:
    """
    Run ANALYZE on tables to update statistics for query planner.
    
    Should be run periodically or after significant data changes.
    """
    if tables is None:
        tables = ['users', 'user_strategy_settings', 'active_positions', 'trade_logs', 'signals']
    
    async with pool.acquire() as conn:
        for table in tables:
            try:
                await conn.execute(f"ANALYZE {table}")
                logger.info(f"Analyzed table: {table}")
            except Exception as e:
                logger.warning(f"Failed to analyze {table}: {e}")


# =============================================================================
# QUERY STATISTICS
# =============================================================================

@dataclass
class QueryStats:
    """Statistics for query execution"""
    query_name: str
    execution_count: int = 0
    total_time_ms: float = 0.0
    avg_time_ms: float = 0.0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0.0
    
    def record(self, time_ms: float):
        """Record a query execution time"""
        self.execution_count += 1
        self.total_time_ms += time_ms
        self.avg_time_ms = self.total_time_ms / self.execution_count
        self.min_time_ms = min(self.min_time_ms, time_ms)
        self.max_time_ms = max(self.max_time_ms, time_ms)


class QueryStatsCollector:
    """Collects query execution statistics for monitoring"""
    
    def __init__(self):
        self._stats: Dict[str, QueryStats] = {}
        self._lock = asyncio.Lock()
    
    async def record(self, query_name: str, time_ms: float):
        """Record query execution time"""
        async with self._lock:
            if query_name not in self._stats:
                self._stats[query_name] = QueryStats(query_name)
            self._stats[query_name].record(time_ms)
    
    def get_stats(self) -> Dict[str, QueryStats]:
        """Get all query statistics"""
        return dict(self._stats)
    
    def get_slow_queries(self, threshold_ms: float = 100.0) -> List[QueryStats]:
        """Get queries with average time above threshold"""
        return [s for s in self._stats.values() if s.avg_time_ms > threshold_ms]


# Global stats collector
_query_stats = QueryStatsCollector()


async def get_query_stats() -> Dict[str, QueryStats]:
    """Get global query statistics"""
    return _query_stats.get_stats()


async def get_slow_queries(threshold_ms: float = 100.0) -> List[QueryStats]:
    """Get slow queries above threshold"""
    return _query_stats.get_slow_queries(threshold_ms)
