"""
Advanced Caching System for Trading Bot
=========================================
Provides multi-level caching with TTL, LRU eviction, and async support.

Best Practices Applied:
1. Thread-safe with RLock for sync code
2. AsyncLock for async code paths
3. Per-user cache partitioning for multitenancy
4. Automatic cleanup of expired entries
5. Hit/miss metrics for monitoring
6. Cache stampede prevention with async_cached_with_lock
"""
from __future__ import annotations

import asyncio
import time
import hashlib
import json
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, Generic, Set
from dataclasses import dataclass, field
from collections import OrderedDict
import threading
import weakref


T = TypeVar('T')


@dataclass
class CacheEntry(Generic[T]):
    """Single cache entry with metadata"""
    value: T
    created_at: float
    ttl: float
    hits: int = 0
    
    @property
    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.ttl
    
    def touch(self) -> None:
        self.hits += 1


class LRUCache(Generic[T]):
    """
    Thread-safe LRU cache with TTL support.
    Evicts least recently used items when max_size is reached.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 300.0):
        self._cache: OrderedDict[str, CacheEntry[T]] = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[T]:
        """Get value from cache, returns None if not found or expired"""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None
            
            if entry.is_expired:
                del self._cache[key]
                self._misses += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.touch()
            self._hits += 1
            return entry.value
    
    def set(self, key: str, value: T, ttl: Optional[float] = None) -> None:
        """Set value in cache with optional custom TTL"""
        with self._lock:
            ttl = ttl if ttl is not None else self._default_ttl
            
            # Remove oldest if at capacity
            while len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)
            
            self._cache[key] = CacheEntry(
                value=value,
                created_at=time.time(),
                ttl=ttl
            )
            self._cache.move_to_end(key)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache, returns True if key existed"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern prefix"""
        with self._lock:
            keys_to_delete = [k for k in self._cache if k.startswith(pattern)]
            for key in keys_to_delete:
                del self._cache[key]
            return len(keys_to_delete)
    
    def clear(self) -> None:
        """Clear entire cache"""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries, returns count removed"""
        with self._lock:
            expired = [k for k, v in self._cache.items() if v.is_expired]
            for key in expired:
                del self._cache[key]
            return len(expired)
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total = self._hits + self._misses
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": self._hits / total if total > 0 else 0,
            }


# ═══════════════════════════════════════════════════════════════
# ASYNC-SAFE LRU CACHE
# ═══════════════════════════════════════════════════════════════

class AsyncLRUCache(Generic[T]):
    """
    Async-safe LRU cache with stampede prevention.
    
    Uses asyncio.Lock to prevent cache stampede (thundering herd)
    when multiple async tasks try to populate the same cache key.
    
    Features:
    - Async-safe with asyncio.Lock
    - Cache stampede prevention
    - Per-key locks for fine-grained concurrency
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 300.0):
        self._cache: OrderedDict[str, CacheEntry[T]] = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()
        self._key_locks: Dict[str, asyncio.Lock] = {}
        self._key_locks_lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0
    
    async def _get_key_lock(self, key: str) -> asyncio.Lock:
        """Get or create lock for specific key"""
        async with self._key_locks_lock:
            if key not in self._key_locks:
                self._key_locks[key] = asyncio.Lock()
            return self._key_locks[key]
    
    async def get(self, key: str) -> Optional[T]:
        """Get value from cache"""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None
            
            if entry.is_expired:
                del self._cache[key]
                self._misses += 1
                return None
            
            self._cache.move_to_end(key)
            entry.touch()
            self._hits += 1
            return entry.value
    
    async def set(self, key: str, value: T, ttl: Optional[float] = None) -> None:
        """Set value in cache"""
        async with self._lock:
            ttl = ttl if ttl is not None else self._default_ttl
            
            while len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)
            
            self._cache[key] = CacheEntry(
                value=value,
                created_at=time.time(),
                ttl=ttl
            )
            self._cache.move_to_end(key)
    
    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], T],
        ttl: Optional[float] = None
    ) -> T:
        """
        Get value from cache or compute and store it.
        
        Uses per-key locking to prevent cache stampede - only one
        task will compute the value, others will wait.
        """
        # Fast path - check cache first
        value = await self.get(key)
        if value is not None:
            return value
        
        # Slow path - acquire key-specific lock
        key_lock = await self._get_key_lock(key)
        async with key_lock:
            # Double check after acquiring lock
            value = await self.get(key)
            if value is not None:
                return value
            
            # Compute value
            if asyncio.iscoroutinefunction(factory):
                value = await factory()
            else:
                value = factory()
            
            if value is not None:
                await self.set(key, value, ttl)
            
            return value
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern prefix"""
        async with self._lock:
            keys_to_delete = [k for k in self._cache if k.startswith(pattern)]
            for key in keys_to_delete:
                del self._cache[key]
            return len(keys_to_delete)
    
    async def clear(self) -> None:
        """Clear entire cache"""
        async with self._lock:
            self._cache.clear()
    
    async def cleanup_expired(self) -> int:
        """Remove all expired entries"""
        async with self._lock:
            expired = [k for k, v in self._cache.items() if v.is_expired]
            for key in expired:
                del self._cache[key]
            return len(expired)
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics (sync for monitoring)"""
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0,
            "key_locks": len(self._key_locks),
        }


# ═══════════════════════════════════════════════════════════════
# USER-PARTITIONED CACHE
# ═══════════════════════════════════════════════════════════════

class UserPartitionedCache(Generic[T]):
    """
    Cache partitioned by user_id for multitenancy.
    
    Provides:
    - Per-user cache isolation
    - Efficient user-specific invalidation
    - Shared LRU eviction across all users
    
    Usage:
        cache = UserPartitionedCache[Dict](max_per_user=100)
        cache.set(user_id=123, key="balance", value={"usdt": 1000})
        balance = cache.get(user_id=123, key="balance")
        cache.invalidate_user(user_id=123)  # Clear all user's cache
    """
    
    def __init__(
        self,
        max_per_user: int = 100,
        max_total: int = 10000,
        default_ttl: float = 60.0
    ):
        self._max_per_user = max_per_user
        self._max_total = max_total
        self._default_ttl = default_ttl
        
        # Main cache storage: {(user_id, key): CacheEntry}
        self._cache: OrderedDict[tuple, CacheEntry[T]] = OrderedDict()
        # Per-user key tracking for efficient invalidation
        self._user_keys: Dict[int, Set[str]] = {}
        
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
    
    def _make_key(self, user_id: int, key: str) -> tuple:
        return (user_id, key)
    
    def get(self, user_id: int, key: str) -> Optional[T]:
        """Get value for user"""
        with self._lock:
            cache_key = self._make_key(user_id, key)
            entry = self._cache.get(cache_key)
            
            if entry is None:
                self._misses += 1
                return None
            
            if entry.is_expired:
                del self._cache[cache_key]
                self._user_keys.get(user_id, set()).discard(key)
                self._misses += 1
                return None
            
            self._cache.move_to_end(cache_key)
            entry.touch()
            self._hits += 1
            return entry.value
    
    def set(self, user_id: int, key: str, value: T, ttl: Optional[float] = None) -> None:
        """Set value for user"""
        with self._lock:
            ttl = ttl if ttl is not None else self._default_ttl
            cache_key = self._make_key(user_id, key)
            
            # Check user's cache size
            user_keys = self._user_keys.setdefault(user_id, set())
            if len(user_keys) >= self._max_per_user and key not in user_keys:
                # Evict oldest entry for this user
                for old_key in list(self._cache.keys()):
                    if old_key[0] == user_id:
                        del self._cache[old_key]
                        user_keys.discard(old_key[1])
                        break
            
            # Check total cache size
            while len(self._cache) >= self._max_total:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._user_keys.get(oldest_key[0], set()).discard(oldest_key[1])
            
            # Add new entry
            self._cache[cache_key] = CacheEntry(
                value=value,
                created_at=time.time(),
                ttl=ttl
            )
            user_keys.add(key)
            self._cache.move_to_end(cache_key)
    
    def delete(self, user_id: int, key: str) -> bool:
        """Delete specific key for user"""
        with self._lock:
            cache_key = self._make_key(user_id, key)
            if cache_key in self._cache:
                del self._cache[cache_key]
                self._user_keys.get(user_id, set()).discard(key)
                return True
            return False
    
    def invalidate_user(self, user_id: int) -> int:
        """Invalidate all cached data for a user"""
        with self._lock:
            user_keys = self._user_keys.pop(user_id, set())
            count = 0
            for key in user_keys:
                cache_key = self._make_key(user_id, key)
                if cache_key in self._cache:
                    del self._cache[cache_key]
                    count += 1
            return count
    
    def get_user_keys(self, user_id: int) -> Set[str]:
        """Get all cached keys for a user"""
        with self._lock:
            return self._user_keys.get(user_id, set()).copy()
    
    @property
    def stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self._hits + self._misses
            return {
                "size": len(self._cache),
                "max_total": self._max_total,
                "unique_users": len(self._user_keys),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": self._hits / total if total > 0 else 0,
            }


# ═══════════════════════════════════════════════════════════════
# GLOBAL CACHE INSTANCES
# ═══════════════════════════════════════════════════════════════

# User config cache - frequently accessed, short TTL
user_config_cache = LRUCache[Dict[str, Any]](max_size=5000, default_ttl=30.0)

# Price/ticker cache - very short TTL, high traffic
price_cache = LRUCache[Dict[str, Any]](max_size=500, default_ttl=5.0)

# Symbol info cache - rarely changes, long TTL
symbol_info_cache = LRUCache[Dict[str, Any]](max_size=1000, default_ttl=3600.0)

# API response cache - for idempotent endpoints
api_response_cache = LRUCache[Dict[str, Any]](max_size=2000, default_ttl=60.0)

# Balance cache - medium TTL, per user+exchange
balance_cache = LRUCache[Dict[str, Any]](max_size=1000, default_ttl=15.0)

# Position cache - short TTL, invalidate on order placement
position_cache = LRUCache[Dict[str, Any]](max_size=2000, default_ttl=10.0)

# Order cache - very short TTL, high update frequency
order_cache = LRUCache[Dict[str, Any]](max_size=1500, default_ttl=5.0)

# Market data cache - ticker, orderbook, trades
market_data_cache = LRUCache[Dict[str, Any]](max_size=500, default_ttl=5.0)

# Credentials cache - avoid decrypt on every call
credentials_cache = LRUCache[Dict[str, Any]](max_size=2000, default_ttl=60.0)


def _make_cache_key(*args, **kwargs) -> str:
    """Create a cache key from function arguments"""
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    key_str = ":".join(key_parts)
    
    if len(key_str) > 200:
        return hashlib.sha256(key_str.encode()).hexdigest()[:32]
    return key_str


def cached(
    cache: LRUCache,
    ttl: Optional[float] = None,
    key_prefix: str = "",
    skip_if: Optional[Callable[..., bool]] = None
):
    """
    Decorator for caching function results.
    
    Args:
        cache: The LRUCache instance to use
        ttl: Optional custom TTL (uses cache default if None)
        key_prefix: Prefix for cache keys (default: function name)
        skip_if: Optional callable that returns True to skip caching
    
    Example:
        @cached(user_config_cache, ttl=60)
        def get_user_settings(user_id: int) -> dict:
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        prefix = key_prefix or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Check if caching should be skipped
            if skip_if and skip_if(*args, **kwargs):
                return func(*args, **kwargs)
            
            key = f"{prefix}:{_make_cache_key(*args, **kwargs)}"
            
            # Try cache first
            result = cache.get(key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache.set(key, result, ttl)
            
            return result
        
        # Add cache control methods to wrapper
        wrapper.cache_clear = lambda: cache.delete_pattern(prefix + ":")
        wrapper.cache_delete = lambda *a, **kw: cache.delete(
            f"{prefix}:{_make_cache_key(*a, **kw)}"
        )
        
        return wrapper
    return decorator


def async_cached(
    cache: LRUCache,
    ttl: Optional[float] = None,
    key_prefix: str = "",
    skip_if: Optional[Callable[..., bool]] = None
):
    """
    Async version of cached decorator.
    
    Example:
        @async_cached(price_cache, ttl=5)
        async def fetch_price(symbol: str) -> dict:
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        prefix = key_prefix or func.__name__
        
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Check if caching should be skipped
            if skip_if and skip_if(*args, **kwargs):
                return await func(*args, **kwargs)
            
            key = f"{prefix}:{_make_cache_key(*args, **kwargs)}"
            
            # Try cache first
            result = cache.get(key)
            if result is not None:
                return result
            
            # Call async function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                cache.set(key, result, ttl)
            
            return result
        
        # Add cache control methods
        wrapper.cache_clear = lambda: cache.delete_pattern(prefix + ":")
        wrapper.cache_delete = lambda *a, **kw: cache.delete(
            f"{prefix}:{_make_cache_key(*a, **kw)}"
        )
        
        return wrapper
    return decorator


def invalidate_user_caches(user_id: int) -> int:
    """
    Invalidate all caches for a specific user.
    Call this after user config changes.
    Returns count of deleted entries.
    """
    count = 0
    prefix = str(user_id)
    
    count += user_config_cache.delete_pattern(f"get_user_config:{prefix}")
    count += balance_cache.delete_pattern(f"balance:{prefix}")
    count += position_cache.delete_pattern(f"positions:{prefix}")
    count += order_cache.delete_pattern(f"orders:{prefix}")
    count += credentials_cache.delete_pattern(f"creds:{prefix}")
    count += api_response_cache.delete_pattern(f"user_{prefix}")
    
    return count


def invalidate_position_cache(user_id: int, exchange: str = None, account_type: str = None) -> int:
    """
    Invalidate position cache for a user. Call after order placement.
    If exchange/account_type provided, invalidates only that cache.
    """
    if exchange and account_type:
        key = f"positions:{user_id}:{exchange}:{account_type}"
        return 1 if position_cache.delete(key) else 0
    else:
        # Invalidate all position caches for user
        return position_cache.delete_pattern(f"positions:{user_id}")


def invalidate_balance_cache(user_id: int, exchange: str = None, account_type: str = None) -> int:
    """
    Invalidate balance cache for a user. Call after order placement/closure.
    """
    if exchange and account_type:
        key = f"balance:{user_id}:{exchange}:{account_type}"
        return 1 if balance_cache.delete(key) else 0
    else:
        return balance_cache.delete_pattern(f"balance:{user_id}")


async def periodic_cache_cleanup(interval: float = 300.0):
    """Background task to clean expired entries periodically"""
    while True:
        await asyncio.sleep(interval)
        
        total_cleaned = 0
        total_cleaned += user_config_cache.cleanup_expired()
        total_cleaned += price_cache.cleanup_expired()
        total_cleaned += symbol_info_cache.cleanup_expired()
        total_cleaned += api_response_cache.cleanup_expired()
        total_cleaned += balance_cache.cleanup_expired()
        total_cleaned += position_cache.cleanup_expired()
        total_cleaned += order_cache.cleanup_expired()
        total_cleaned += market_data_cache.cleanup_expired()
        total_cleaned += credentials_cache.cleanup_expired()
        
        if total_cleaned > 0:
            import logging
            logging.debug(f"Cache cleanup: removed {total_cleaned} expired entries")


def get_all_cache_stats() -> Dict[str, Dict[str, Any]]:
    """Get statistics for all cache instances"""
    return {
        "user_config": user_config_cache.stats,
        "price": price_cache.stats,
        "symbol_info": symbol_info_cache.stats,
        "api_response": api_response_cache.stats,
        "balance": balance_cache.stats,
        "position": position_cache.stats,
        "order": order_cache.stats,
        "market_data": market_data_cache.stats,
        "credentials": credentials_cache.stats,
    }

# ═══════════════════════════════════════════════════════════════
# ASYNC CACHE INSTANCES (for high-concurrency operations)
# ═══════════════════════════════════════════════════════════════

# Async balance cache with stampede prevention
async_balance_cache = AsyncLRUCache[Dict[str, Any]](max_size=1000, default_ttl=15.0)

# Async position cache with stampede prevention  
async_position_cache = AsyncLRUCache[Dict[str, Any]](max_size=2000, default_ttl=10.0)

# Async price cache
async_price_cache = AsyncLRUCache[Dict[str, Any]](max_size=500, default_ttl=5.0)


# ═══════════════════════════════════════════════════════════════
# MULTITENANCY CACHE INSTANCES
# ═══════════════════════════════════════════════════════════════

# User-partitioned strategy settings cache
user_strategy_cache = UserPartitionedCache[Dict[str, Any]](
    max_per_user=50,
    max_total=10000,
    default_ttl=60.0
)

# User-partitioned trading context cache
user_context_cache = UserPartitionedCache[Dict[str, Any]](
    max_per_user=20,
    max_total=5000,
    default_ttl=30.0
)


# ═══════════════════════════════════════════════════════════════
# ENHANCED DECORATORS
# ═══════════════════════════════════════════════════════════════

def async_cached_with_lock(
    cache: AsyncLRUCache,
    ttl: Optional[float] = None,
    key_prefix: str = "",
):
    """
    Async decorator with stampede prevention.
    
    Uses per-key locking to ensure only one coroutine computes
    the value while others wait for the result.
    
    Example:
        @async_cached_with_lock(async_balance_cache, ttl=15)
        async def fetch_balance(user_id: int, exchange: str) -> dict:
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        prefix = key_prefix or func.__name__
        
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            key = f"{prefix}:{_make_cache_key(*args, **kwargs)}"
            
            # Use get_or_set with factory for stampede prevention
            async def factory():
                return await func(*args, **kwargs)
            
            return await cache.get_or_set(key, factory, ttl)
        
        # Add cache control methods
        async def cache_clear():
            await cache.delete_pattern(prefix + ":")
        
        async def cache_delete(*a, **kw):
            await cache.delete(f"{prefix}:{_make_cache_key(*a, **kw)}")
        
        wrapper.cache_clear = cache_clear
        wrapper.cache_delete = cache_delete
        
        return wrapper
    return decorator


def user_cached(
    cache: UserPartitionedCache,
    ttl: Optional[float] = None,
    key_builder: Callable[..., str] = None,
):
    """
    Decorator for user-partitioned caching.
    
    Automatically extracts user_id from first argument or kwargs.
    
    Example:
        @user_cached(user_strategy_cache, ttl=60)
        def get_strategy_settings(user_id: int, strategy: str) -> dict:
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Extract user_id
            user_id = kwargs.get('user_id')
            if user_id is None and args:
                user_id = args[0]
            
            if user_id is None:
                # No user context, call directly
                return func(*args, **kwargs)
            
            # Build cache key
            if key_builder:
                key = key_builder(*args, **kwargs)
            else:
                key = f"{func.__name__}:{_make_cache_key(*args[1:], **{k:v for k,v in kwargs.items() if k != 'user_id'})}"
            
            # Try cache first
            result = cache.get(user_id, key)
            if result is not None:
                return result
            
            # Compute and cache
            result = func(*args, **kwargs)
            if result is not None:
                cache.set(user_id, key, result, ttl)
            
            return result
        
        wrapper.cache = cache
        wrapper.invalidate_user = cache.invalidate_user
        
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════
# ENHANCED INVALIDATION
# ═══════════════════════════════════════════════════════════════

async def invalidate_user_caches_async(user_id: int) -> int:
    """
    Async version of user cache invalidation.
    Invalidates both sync and async caches.
    """
    count = 0
    
    # Sync caches
    count += invalidate_user_caches(user_id)
    
    # Async caches
    count += await async_balance_cache.delete_pattern(f"balance:{user_id}")
    count += await async_position_cache.delete_pattern(f"positions:{user_id}")
    
    # User-partitioned caches
    count += user_strategy_cache.invalidate_user(user_id)
    count += user_context_cache.invalidate_user(user_id)
    
    return count


def invalidate_on_trade(user_id: int, exchange: str = None, account_type: str = None):
    """
    Invalidate all trade-related caches after order placement/closure.
    
    Usage:
        # After placing order
        invalidate_on_trade(user_id, "bybit", "demo")
    """
    invalidate_position_cache(user_id, exchange, account_type)
    invalidate_balance_cache(user_id, exchange, account_type)
    order_cache.delete_pattern(f"orders:{user_id}")


async def invalidate_on_trade_async(user_id: int, exchange: str = None, account_type: str = None):
    """Async version of trade cache invalidation"""
    invalidate_on_trade(user_id, exchange, account_type)
    
    # Also invalidate async caches
    if exchange and account_type:
        await async_balance_cache.delete(f"balance:{user_id}:{exchange}:{account_type}")
        await async_position_cache.delete(f"positions:{user_id}:{exchange}:{account_type}")
    else:
        await async_balance_cache.delete_pattern(f"balance:{user_id}")
        await async_position_cache.delete_pattern(f"positions:{user_id}")


# ═══════════════════════════════════════════════════════════════
# ENHANCED CACHE STATS
# ═══════════════════════════════════════════════════════════════

def get_all_cache_stats_extended() -> Dict[str, Dict[str, Any]]:
    """Get comprehensive statistics for all cache instances"""
    return {
        "sync": {
            "user_config": user_config_cache.stats,
            "price": price_cache.stats,
            "symbol_info": symbol_info_cache.stats,
            "api_response": api_response_cache.stats,
            "balance": balance_cache.stats,
            "position": position_cache.stats,
            "order": order_cache.stats,
            "market_data": market_data_cache.stats,
            "credentials": credentials_cache.stats,
        },
        "async": {
            "balance": async_balance_cache.stats,
            "position": async_position_cache.stats,
            "price": async_price_cache.stats,
        },
        "user_partitioned": {
            "strategy": user_strategy_cache.stats,
            "context": user_context_cache.stats,
        },
    }