"""
PostgreSQL Database Helper for WebApp API

Provides SQLite-compatible interface for existing code that uses:
- conn.execute("SELECT ... WHERE id=?", (param,))
- dict(row) for row access
- cur.lastrowid for INSERT

Usage:
    from webapp.api.db_helper import get_db
    
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
        rows = [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()
"""
from typing import Optional, Any
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.db_postgres import get_pool, _sqlite_to_pg
import psycopg2.extras


def get_db():
    """Get PostgreSQL connection with SQLite compatibility layer.
    
    Returns a connection that:
    - Auto-converts ? -> %s placeholders
    - Returns dicts from fetchall/fetchone (works with dict(row))
    - Supports cur.lastrowid for INSERT statements
    
    Caller MUST call conn.close() when done - this returns conn to pool.
    """
    pool = get_pool()
    pg_conn = pool.getconn()
    wrapper = _DictCompatConnection(pg_conn)
    wrapper._pool = pool
    return wrapper


class _DictCompatConnection:
    """Connection wrapper that returns dicts from cursor for dict(row) compatibility.
    
    Supports context manager usage:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(...)
    """
    
    def __init__(self, pg_conn):
        self._conn = pg_conn
        self._pool: Optional[Any] = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - always close connection."""
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.close()
        return False
    
    def cursor(self, *args, **kwargs):
        """Get a cursor wrapper that returns dicts and supports lastrowid."""
        return _DictCompatCursor(self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor))
    
    def execute(self, query: str, params: Optional[tuple] = None):
        """Execute query directly."""
        cur = self.cursor()
        cur.execute(query, params)
        return cur
    
    def commit(self):
        self._conn.commit()
    
    def rollback(self):
        self._conn.rollback()
    
    def close(self):
        """Close connection - returns to pool if pool reference exists."""
        if self._pool:
            try:
                self._conn.rollback()
            except Exception:
                pass
            self._pool.putconn(self._conn)
        else:
            self._conn.close()


class _DictCompatCursor:
    """Cursor wrapper that converts ? -> %s and supports lastrowid."""
    
    def __init__(self, pg_cursor):
        self._cursor = pg_cursor
        self.lastrowid = None
        self.rowcount = 0
        self.description = None
    
    def execute(self, query: str, params: Optional[tuple] = None):
        """Execute query with ? -> %s conversion and RETURNING id for INSERTs."""
        pg_query = _sqlite_to_pg(query)
        
        # Add RETURNING id for INSERT statements if not present
        if 'INSERT' in pg_query.upper() and 'RETURNING' not in pg_query.upper():
            # Skip for tables without id column (composite/non-id primary keys)
            tables_without_id = [
                'active_positions', 'user_strategy_settings', 'pending_limit_orders',
                'users', 'pyramids'  # users.user_id, pyramids.(user_id,symbol,exchange)
            ]
            has_id_column = True
            for table in tables_without_id:
                if table.lower() in pg_query.lower():
                    has_id_column = False
                    break
            if has_id_column and 'ON CONFLICT DO NOTHING' not in pg_query.upper():
                pg_query = pg_query.rstrip().rstrip(';') + ' RETURNING id'
        
        self._cursor.execute(pg_query, params)
        self.rowcount = self._cursor.rowcount
        self.description = self._cursor.description
        
        # Get lastrowid for INSERT with RETURNING
        if 'RETURNING' in pg_query.upper() and self._cursor.description:
            row = self._cursor.fetchone()
            if row:
                self.lastrowid = row.get('id') if isinstance(row, dict) else row[0]
        
        return self
    
    def fetchone(self):
        return self._cursor.fetchone()
    
    def fetchall(self):
        return self._cursor.fetchall()
    
    def fetchmany(self, size=None):
        if size:
            return self._cursor.fetchmany(size)
        return self._cursor.fetchmany()
    
    def close(self):
        self._cursor.close()
    
    def __iter__(self):
        return iter(self._cursor)
