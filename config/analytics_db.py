"""
ElCaro Analytics Database
Отдельная база для аналитических данных: свечи, индикаторы, рыночные данные
Оптимизирована для time-series и быстрого чтения
"""
import sqlite3
import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from queue import Queue
import threading

try:
    from config.settings import settings
    ANALYTICS_DB = settings.db.analytics_db
except ImportError:
    ANALYTICS_DB = Path(__file__).parent.parent / "data" / "analytics.db"

# Connection pool
_pool: Queue = Queue(maxsize=5)
_pool_lock = threading.Lock()


def _create_connection() -> sqlite3.Connection:
    """Create optimized connection for analytics"""
    ANALYTICS_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(ANALYTICS_DB), timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-128000")  # 128MB cache for analytics
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.execute("PRAGMA mmap_size=536870912")  # 512MB mmap
    return conn


@contextmanager
def get_analytics_conn():
    """Get connection from pool"""
    conn = None
    try:
        with _pool_lock:
            if not _pool.empty():
                conn = _pool.get_nowait()
        if conn is None:
            conn = _create_connection()
        yield conn
    finally:
        if conn:
            try:
                with _pool_lock:
                    if _pool.qsize() < 5:
                        _pool.put_nowait(conn)
                    else:
                        conn.close()
            except Exception:
                conn.close()


def init_analytics_db():
    """Initialize analytics database schema"""
    with get_analytics_conn() as conn:
        cursor = conn.cursor()
        
        # Candle data (OHLCV)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                open_time INTEGER NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                close_time INTEGER,
                quote_volume REAL,
                trades_count INTEGER,
                created_at REAL DEFAULT (strftime('%s', 'now')),
                UNIQUE(symbol, timeframe, open_time)
            )
        """)
        
        # Indicator cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS indicator_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                indicator_type TEXT NOT NULL,
                params TEXT,
                data TEXT NOT NULL,
                calculated_at REAL NOT NULL,
                expires_at REAL NOT NULL,
                UNIQUE(symbol, timeframe, indicator_type, params)
            )
        """)
        
        # Market snapshots (screener data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                price_change_24h REAL,
                volume_24h REAL,
                high_24h REAL,
                low_24h REAL,
                open_interest REAL,
                funding_rate REAL,
                long_short_ratio REAL,
                top_trader_ratio REAL,
                snapshot_time REAL NOT NULL,
                UNIQUE(symbol, snapshot_time)
            )
        """)
        
        # Liquidations history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS liquidations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                price REAL NOT NULL,
                qty REAL NOT NULL,
                usd_value REAL NOT NULL,
                timestamp REAL NOT NULL
            )
        """)
        
        # Top movers cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS top_movers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                data TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        
        # Strategy performance tracking (for leaderboard)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                period TEXT NOT NULL,
                total_pnl REAL NOT NULL,
                win_rate REAL NOT NULL,
                total_trades INTEGER NOT NULL,
                max_drawdown REAL,
                sharpe_ratio REAL,
                calculated_at REAL NOT NULL,
                UNIQUE(strategy_id, period)
            )
        """)
        
        # Create indexes for fast queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_candles_symbol_tf ON candles(symbol, timeframe, open_time DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_symbol ON market_snapshots(symbol, snapshot_time DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_liquidations_time ON liquidations(timestamp DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_indicator_expires ON indicator_cache(expires_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_strategy_perf ON strategy_performance(period, total_pnl DESC)")
        
        conn.commit()
        print(f"✅ Analytics DB initialized: {ANALYTICS_DB}")


# =============================================================================
# Candle Operations
# =============================================================================

def save_candles(symbol: str, timeframe: str, candles: List[Dict]) -> int:
    """Save candles to database (upsert)"""
    if not candles:
        return 0
    
    with get_analytics_conn() as conn:
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT OR REPLACE INTO candles 
            (symbol, timeframe, open_time, open, high, low, close, volume, close_time, quote_volume, trades_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (symbol, timeframe, c['open_time'], c['open'], c['high'], c['low'], 
             c['close'], c['volume'], c.get('close_time'), c.get('quote_volume'), c.get('trades_count'))
            for c in candles
        ])
        conn.commit()
        return cursor.rowcount


def get_candles(symbol: str, timeframe: str, limit: int = 500, since: int = None) -> List[Dict]:
    """Get candles from database"""
    with get_analytics_conn() as conn:
        cursor = conn.cursor()
        if since:
            cursor.execute("""
                SELECT * FROM candles 
                WHERE symbol = ? AND timeframe = ? AND open_time >= ?
                ORDER BY open_time ASC LIMIT ?
            """, (symbol, timeframe, since, limit))
        else:
            cursor.execute("""
                SELECT * FROM candles 
                WHERE symbol = ? AND timeframe = ?
                ORDER BY open_time DESC LIMIT ?
            """, (symbol, timeframe, limit))
        
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


# =============================================================================
# Indicator Cache
# =============================================================================

def cache_indicator(symbol: str, timeframe: str, indicator_type: str, 
                    params: dict, data: Any, ttl_minutes: int = 5):
    """Cache calculated indicator"""
    now = time.time()
    with get_analytics_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO indicator_cache 
            (symbol, timeframe, indicator_type, params, data, calculated_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (symbol, timeframe, indicator_type, json.dumps(params), 
              json.dumps(data), now, now + ttl_minutes * 60))
        conn.commit()


def get_cached_indicator(symbol: str, timeframe: str, indicator_type: str, 
                         params: dict) -> Optional[Any]:
    """Get cached indicator if not expired"""
    with get_analytics_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT data FROM indicator_cache 
            WHERE symbol = ? AND timeframe = ? AND indicator_type = ? 
            AND params = ? AND expires_at > ?
        """, (symbol, timeframe, indicator_type, json.dumps(params), time.time()))
        row = cursor.fetchone()
        return json.loads(row['data']) if row else None


def cleanup_expired_cache():
    """Remove expired cache entries"""
    with get_analytics_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM indicator_cache WHERE expires_at < ?", (time.time(),))
        deleted = cursor.rowcount
        conn.commit()
        return deleted


# =============================================================================
# Market Snapshots
# =============================================================================

def save_market_snapshot(data: Dict):
    """Save market snapshot"""
    with get_analytics_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO market_snapshots 
            (symbol, price, price_change_24h, volume_24h, high_24h, low_24h,
             open_interest, funding_rate, long_short_ratio, top_trader_ratio, snapshot_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['symbol'], data['price'], data.get('price_change_24h'),
            data.get('volume_24h'), data.get('high_24h'), data.get('low_24h'),
            data.get('open_interest'), data.get('funding_rate'),
            data.get('long_short_ratio'), data.get('top_trader_ratio'), time.time()
        ))
        conn.commit()


def get_latest_snapshots(limit: int = 50) -> List[Dict]:
    """Get latest market snapshots for all symbols"""
    with get_analytics_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM market_snapshots 
            WHERE id IN (
                SELECT MAX(id) FROM market_snapshots GROUP BY symbol
            )
            ORDER BY volume_24h DESC LIMIT ?
        """, (limit,))
        return [dict(r) for r in cursor.fetchall()]


# =============================================================================
# Liquidations
# =============================================================================

def save_liquidation(symbol: str, side: str, price: float, qty: float, usd_value: float):
    """Save liquidation event"""
    with get_analytics_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO liquidations (symbol, side, price, qty, usd_value, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (symbol, side, price, qty, usd_value, time.time()))
        conn.commit()


def get_recent_liquidations(limit: int = 100, min_usd: float = 0) -> List[Dict]:
    """Get recent liquidations"""
    with get_analytics_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM liquidations 
            WHERE usd_value >= ?
            ORDER BY timestamp DESC LIMIT ?
        """, (min_usd, limit))
        return [dict(r) for r in cursor.fetchall()]


def get_liquidation_stats(hours: int = 24) -> Dict:
    """Get liquidation statistics"""
    since = time.time() - hours * 3600
    with get_analytics_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                side,
                COUNT(*) as count,
                SUM(usd_value) as total_usd,
                AVG(usd_value) as avg_usd,
                MAX(usd_value) as max_usd
            FROM liquidations 
            WHERE timestamp >= ?
            GROUP BY side
        """, (since,))
        stats = {}
        for row in cursor.fetchall():
            stats[row['side']] = dict(row)
        return stats


# =============================================================================
# Strategy Performance
# =============================================================================

def update_strategy_performance(strategy_id: int, user_id: int, period: str, 
                                 stats: Dict):
    """Update strategy performance for leaderboard"""
    with get_analytics_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO strategy_performance 
            (strategy_id, user_id, period, total_pnl, win_rate, total_trades, 
             max_drawdown, sharpe_ratio, calculated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            strategy_id, user_id, period, stats['total_pnl'], stats['win_rate'],
            stats['total_trades'], stats.get('max_drawdown'), stats.get('sharpe_ratio'),
            time.time()
        ))
        conn.commit()


def get_strategy_leaderboard(period: str = '30d', limit: int = 50) -> List[Dict]:
    """Get strategy leaderboard"""
    with get_analytics_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM strategy_performance 
            WHERE period = ?
            ORDER BY total_pnl DESC
            LIMIT ?
        """, (period, limit))
        return [dict(r) for r in cursor.fetchall()]


# Initialize on import
if __name__ != "__main__":
    try:
        init_analytics_db()
    except Exception as e:
        print(f"Warning: Could not init analytics DB: {e}")
