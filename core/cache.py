"""
Advanced Caching System for Trading Bot
Provides multi-level caching with TTL, LRU eviction, and async support
"""
from __future__ import annotations

import asyncio
import time
import hashlib
import json
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, Generic
from dataclasses import dataclass, field
from collections import OrderedDict
import threading


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
