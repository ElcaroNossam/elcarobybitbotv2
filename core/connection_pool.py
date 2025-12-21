"""
Connection Pool Manager for Exchange Clients
Reduces connection overhead by reusing clients across requests
"""
from __future__ import annotations

import asyncio
import time
import logging
from typing import Dict, Optional, Any, TypeVar
from dataclasses import dataclass, field
from collections import OrderedDict
import threading
from weakref import WeakValueDictionary

from core.cache import invalidate_user_caches


logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class PooledConnection:
    """Wrapper for a pooled connection"""
    client: Any
    user_id: int
    exchange: str
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    use_count: int = 0
    is_healthy: bool = True
    
    def touch(self) -> None:
        self.last_used = time.time()
        self.use_count += 1
    
    @property
    def age(self) -> float:
        return time.time() - self.created_at
    
    @property
    def idle_time(self) -> float:
        return time.time() - self.last_used


class ConnectionPool:
    """
    Connection pool for exchange clients.
    
    - Maintains a pool of initialized exchange clients per user
    - Automatically closes idle connections
    - Limits max connections per user
    - Health checks on borrow
    
    Usage:
        pool = ConnectionPool(max_per_user=3, max_idle_seconds=300)
        
        async with pool.acquire(user_id, exchange_type) as client:
            balance = await client.get_balance()
    """
    
    def __init__(
        self,
        max_per_user: int = 2,
        max_total: int = 100,
        max_idle_seconds: float = 300.0,
        max_age_seconds: float = 3600.0
    ):
        self.max_per_user = max_per_user
        self.max_total = max_total
        self.max_idle_seconds = max_idle_seconds
        self.max_age_seconds = max_age_seconds
        
        # Pool structure: {(user_id, exchange): [PooledConnection, ...]}
        self._pool: Dict[tuple, list[PooledConnection]] = {}
        self._in_use: Dict[tuple, int] = {}  # Count of connections currently in use
        self._lock = asyncio.Lock()
        
        # Stats
        self._hits = 0
        self._misses = 0
        self._evictions = 0
    
    async def acquire(self, user_id: int, exchange: str = "bybit"):
        """
        Acquire a connection from the pool.
        Returns a context manager that returns the connection to pool on exit.
        
        Usage:
            async with pool.acquire(user_id, "bybit") as client:
                await client.get_balance()
        """
        return _PooledConnectionContext(self, user_id, exchange)
    
    async def _get_connection(self, user_id: int, exchange: str) -> PooledConnection:
        """Get or create a connection"""
        key = (user_id, exchange)
        
        async with self._lock:
            # Try to get from pool
            if key in self._pool and self._pool[key]:
                # Find a healthy, non-expired connection
                for conn in self._pool[key]:
                    if conn.is_healthy and conn.age < self.max_age_seconds:
                        self._pool[key].remove(conn)
                        conn.touch()
                        self._hits += 1
                        return conn
                
                # No healthy connection, clean up unhealthy ones
                self._pool[key] = [
                    c for c in self._pool[key] 
                    if c.is_healthy and c.age < self.max_age_seconds
                ]
            
            # Need to create new connection
            self._misses += 1
        
        # Create outside lock to avoid blocking
        client = await self._create_client(user_id, exchange)
        return PooledConnection(
            client=client,
            user_id=user_id,
            exchange=exchange
        )
    
    async def _return_connection(self, conn: PooledConnection) -> None:
        """Return a connection to the pool"""
        key = (conn.user_id, conn.exchange)
        
        async with self._lock:
            # Don't return unhealthy or expired connections
            if not conn.is_healthy or conn.age >= self.max_age_seconds:
                await self._close_connection(conn)
                return
            
            # Initialize pool list if needed
            if key not in self._pool:
                self._pool[key] = []
            
            # Check if we're at capacity
            if len(self._pool[key]) >= self.max_per_user:
                # Remove oldest
                oldest = min(self._pool[key], key=lambda c: c.last_used)
                self._pool[key].remove(oldest)
                await self._close_connection(oldest)
                self._evictions += 1
            
            # Check total pool size
            total = sum(len(conns) for conns in self._pool.values())
            if total >= self.max_total:
                # Evict least recently used globally
                all_conns = [(k, c) for k, conns in self._pool.items() for c in conns]
                if all_conns:
                    oldest_key, oldest_conn = min(all_conns, key=lambda x: x[1].last_used)
                    self._pool[oldest_key].remove(oldest_conn)
                    await self._close_connection(oldest_conn)
                    self._evictions += 1
            
            self._pool[key].append(conn)
    
    async def _create_client(self, user_id: int, exchange: str) -> Any:
        """Create a new exchange client"""
        from core.exchange_client import get_exchange_client
        return await get_exchange_client(user_id, exchange)
    
    async def _close_connection(self, conn: PooledConnection) -> None:
        """Close a connection"""
        try:
            if hasattr(conn.client, 'close'):
                await conn.client.close()
        except Exception as e:
            logger.warning(f"Error closing connection: {e}")
    
    async def cleanup(self) -> int:
        """Remove idle and expired connections"""
        cleaned = 0
        now = time.time()
        
        async with self._lock:
            for key in list(self._pool.keys()):
                connections = self._pool[key]
                to_remove = []
                
                for conn in connections:
                    if conn.idle_time > self.max_idle_seconds or conn.age > self.max_age_seconds:
                        to_remove.append(conn)
                
                for conn in to_remove:
                    connections.remove(conn)
                    await self._close_connection(conn)
                    cleaned += 1
                
                if not connections:
                    del self._pool[key]
        
        if cleaned:
            logger.info(f"Pool cleanup: removed {cleaned} idle connections")
        
        return cleaned
    
    async def close_all(self) -> None:
        """Close all connections in the pool"""
        async with self._lock:
            for key, connections in self._pool.items():
                for conn in connections:
                    await self._close_connection(conn)
            self._pool.clear()
        
        logger.info("Connection pool closed")
    
    def invalidate_user(self, user_id: int) -> None:
        """Invalidate all connections for a user (after credential change)"""
        keys_to_remove = [k for k in self._pool.keys() if k[0] == user_id]
        
        for key in keys_to_remove:
            for conn in self._pool.get(key, []):
                conn.is_healthy = False
            self._pool.pop(key, None)
        
        # Also invalidate user caches
        invalidate_user_caches(user_id)
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        total_connections = sum(len(conns) for conns in self._pool.values())
        total_users = len(set(k[0] for k in self._pool.keys()))
        
        return {
            "total_connections": total_connections,
            "unique_users": total_users,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / (self._hits + self._misses) if (self._hits + self._misses) > 0 else 0,
            "evictions": self._evictions,
            "max_per_user": self.max_per_user,
            "max_total": self.max_total,
        }


class _PooledConnectionContext:
    """Context manager for pooled connections"""
    
    def __init__(self, pool: ConnectionPool, user_id: int, exchange: str):
        self.pool = pool
        self.user_id = user_id
        self.exchange = exchange
        self.conn: Optional[PooledConnection] = None
    
    async def __aenter__(self):
        self.conn = await self.pool._get_connection(self.user_id, self.exchange)
        return self.conn.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            # Mark as unhealthy if there was an exception
            if exc_type is not None:
                self.conn.is_healthy = False
            await self.pool._return_connection(self.conn)


# ═══════════════════════════════════════════════════════════════
# GLOBAL POOL INSTANCE
# ═══════════════════════════════════════════════════════════════

# Global connection pool with sensible defaults
connection_pool = ConnectionPool(
    max_per_user=2,
    max_total=100,
    max_idle_seconds=300.0,  # 5 minutes
    max_age_seconds=3600.0   # 1 hour
)


async def periodic_pool_cleanup(interval: float = 60.0):
    """Background task for periodic pool cleanup"""
    while True:
        await asyncio.sleep(interval)
        try:
            await connection_pool.cleanup()
        except Exception as e:
            logger.error(f"Pool cleanup error: {e}")


# ═══════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

async def get_cached_client(user_id: int, exchange: str = "bybit"):
    """
    Get a pooled exchange client.
    
    Example:
        async with get_cached_client(user_id) as client:
            balance = await client.get_balance()
    """
    return await connection_pool.acquire(user_id, exchange)


def on_credentials_changed(user_id: int) -> None:
    """
    Call this when user's exchange credentials change.
    Invalidates all cached connections for the user.
    """
    connection_pool.invalidate_user(user_id)
    logger.info(f"Invalidated connections for user {user_id}")
