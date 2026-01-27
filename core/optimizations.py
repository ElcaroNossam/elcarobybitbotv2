"""
Core Optimizations Module
=========================
Centralized optimization utilities discovered during full project audit (Jan 27, 2026).

Contains:
- Cache cleanup scheduler
- Memory-bounded caches
- Async-safe connection helpers
- Batch operation utilities
- Performance monitoring
"""
from __future__ import annotations

import asyncio
import time
import logging
import threading
import functools
from typing import Any, Callable, Dict, Optional, TypeVar, Generic
from collections import OrderedDict
from dataclasses import dataclass, field
from contextlib import asynccontextmanager, contextmanager

logger = logging.getLogger(__name__)

T = TypeVar('T')


# ═══════════════════════════════════════════════════════════════════════════════
# BOUNDED DICT CACHE - Prevents unbounded memory growth
# ═══════════════════════════════════════════════════════════════════════════════

class BoundedDict(Generic[T]):
    """
    Thread-safe dictionary with max size limit.
    Evicts oldest entries when limit is reached (FIFO).
    
    Use instead of plain dict for caches that might grow unbounded.
    
    Example:
        cache = BoundedDict[str](max_size=1000)
        cache["key"] = "value"
        value = cache.get("key")
    """
    
    def __init__(self, max_size: int = 1000):
        self._data: OrderedDict[str, T] = OrderedDict()
        self._max_size = max_size
        self._lock = threading.RLock()
        self._eviction_count = 0
    
    def __setitem__(self, key: str, value: T) -> None:
        with self._lock:
            if key in self._data:
                self._data.move_to_end(key)
            else:
                while len(self._data) >= self._max_size:
                    self._data.popitem(last=False)
                    self._eviction_count += 1
            self._data[key] = value
    
    def __getitem__(self, key: str) -> T:
        with self._lock:
            return self._data[key]
    
    def get(self, key: str, default: T = None) -> T:
        with self._lock:
            return self._data.get(key, default)
    
    def __contains__(self, key: str) -> bool:
        with self._lock:
            return key in self._data
    
    def pop(self, key: str, default: T = None) -> T:
        with self._lock:
            return self._data.pop(key, default)
    
    def clear(self) -> None:
        with self._lock:
            self._data.clear()
    
    def __len__(self) -> int:
        return len(self._data)
    
    @property
    def stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "size": len(self._data),
                "max_size": self._max_size,
                "evictions": self._eviction_count
            }


# ═══════════════════════════════════════════════════════════════════════════════
# TTL BOUNDED DICT - Auto-expiring entries with size limit
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TTLEntry(Generic[T]):
    value: T
    expires_at: float
    
    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class TTLBoundedDict(Generic[T]):
    """
    Thread-safe dictionary with TTL and max size.
    Entries expire after TTL seconds and oldest are evicted at max_size.
    
    Example:
        cache = TTLBoundedDict[dict](max_size=500, ttl=60.0)
        cache.set("user:123", {"balance": 1000})
        data = cache.get("user:123")  # Returns None if expired
    """
    
    def __init__(self, max_size: int = 500, ttl: float = 60.0):
        self._data: OrderedDict[str, TTLEntry[T]] = OrderedDict()
        self._max_size = max_size
        self._default_ttl = ttl
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
    
    def set(self, key: str, value: T, ttl: float = None) -> None:
        ttl = ttl if ttl is not None else self._default_ttl
        with self._lock:
            if key in self._data:
                self._data.move_to_end(key)
            else:
                while len(self._data) >= self._max_size:
                    self._data.popitem(last=False)
            self._data[key] = TTLEntry(value=value, expires_at=time.time() + ttl)
    
    def get(self, key: str, default: T = None) -> T:
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                self._misses += 1
                return default
            if entry.is_expired:
                del self._data[key]
                self._misses += 1
                return default
            self._hits += 1
            return entry.value
    
    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._data:
                del self._data[key]
                return True
            return False
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries. Returns count removed."""
        with self._lock:
            expired = [k for k, v in self._data.items() if v.is_expired]
            for k in expired:
                del self._data[k]
            return len(expired)
    
    def clear(self) -> None:
        with self._lock:
            self._data.clear()
    
    @property
    def stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self._hits + self._misses
            return {
                "size": len(self._data),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": self._hits / total if total > 0 else 0.0
            }


# ═══════════════════════════════════════════════════════════════════════════════
# ASYNC CONNECTION HELPER - Safe async context for sync DB operations
# ═══════════════════════════════════════════════════════════════════════════════

_db_executor_lock = asyncio.Lock() if asyncio.get_event_loop().is_running() else None


async def run_in_executor(func: Callable, *args, **kwargs) -> Any:
    """
    Run synchronous function in thread pool executor.
    Use for DB operations in async context to avoid blocking event loop.
    
    Example:
        result = await run_in_executor(db.get_user, user_id)
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,  # Use default ThreadPoolExecutor
        functools.partial(func, *args, **kwargs)
    )


def sync_to_async(func: Callable) -> Callable:
    """
    Decorator to convert sync function to async.
    Runs in thread pool executor.
    
    Example:
        @sync_to_async
        def get_user(user_id):
            return db.get_user(user_id)
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))
    return wrapper


# ═══════════════════════════════════════════════════════════════════════════════
# EXCEPTION LOGGING DECORATOR - Ensures all exceptions are logged
# ═══════════════════════════════════════════════════════════════════════════════

def log_exceptions(func: Callable) -> Callable:
    """
    Decorator that logs exceptions before re-raising.
    Use on functions where bare 'except:' was used before.
    
    Example:
        @log_exceptions
        def process_trade(trade_data):
            ...
    """
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"{func.__name__} failed: {e}")
            raise
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"{func.__name__} failed: {e}")
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


# ═══════════════════════════════════════════════════════════════════════════════
# CACHE CLEANUP SCHEDULER - Periodic cache maintenance
# ═══════════════════════════════════════════════════════════════════════════════

class CacheCleanupScheduler:
    """
    Schedules periodic cleanup of caches.
    Should be started once at application startup.
    
    Example:
        scheduler = CacheCleanupScheduler()
        scheduler.register(my_cache, cleanup_interval=300)
        await scheduler.start()
    """
    
    def __init__(self):
        self._caches: list[tuple[Any, float]] = []
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    def register(self, cache: Any, cleanup_interval: float = 300.0) -> None:
        """Register a cache for periodic cleanup."""
        if hasattr(cache, 'cleanup_expired'):
            self._caches.append((cache, cleanup_interval))
    
    async def start(self) -> None:
        """Start the cleanup scheduler."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._cleanup_loop())
        logger.info("Cache cleanup scheduler started")
    
    async def stop(self) -> None:
        """Stop the cleanup scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _cleanup_loop(self) -> None:
        """Main cleanup loop."""
        last_cleanup: Dict[int, float] = {}
        
        while self._running:
            try:
                now = time.time()
                for i, (cache, interval) in enumerate(self._caches):
                    last = last_cleanup.get(i, 0)
                    if now - last >= interval:
                        try:
                            removed = cache.cleanup_expired()
                            if removed > 0:
                                logger.debug(f"Cache cleanup: removed {removed} entries")
                            last_cleanup[i] = now
                        except Exception as e:
                            logger.warning(f"Cache cleanup failed: {e}")
                
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Cache cleanup loop error: {e}")
                await asyncio.sleep(60)


# Global scheduler instance
cache_cleanup_scheduler = CacheCleanupScheduler()


# ═══════════════════════════════════════════════════════════════════════════════
# PERFORMANCE METRICS COLLECTOR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class OperationMetrics:
    """Tracks performance metrics for an operation type."""
    name: str
    total_calls: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0.0
    errors: int = 0
    
    def record(self, duration_ms: float, is_error: bool = False) -> None:
        self.total_calls += 1
        self.total_time_ms += duration_ms
        self.min_time_ms = min(self.min_time_ms, duration_ms)
        self.max_time_ms = max(self.max_time_ms, duration_ms)
        if is_error:
            self.errors += 1
    
    @property
    def avg_time_ms(self) -> float:
        return self.total_time_ms / self.total_calls if self.total_calls > 0 else 0.0
    
    @property
    def error_rate(self) -> float:
        return self.errors / self.total_calls if self.total_calls > 0 else 0.0


class MetricsCollector:
    """
    Collects performance metrics for operations.
    
    Example:
        metrics = MetricsCollector()
        
        with metrics.measure("db_query"):
            result = db.execute(query)
        
        print(metrics.get_stats())
    """
    
    def __init__(self):
        self._metrics: Dict[str, OperationMetrics] = {}
        self._lock = threading.RLock()
    
    @contextmanager
    def measure(self, operation: str):
        """Context manager to measure operation duration."""
        start = time.perf_counter()
        is_error = False
        try:
            yield
        except Exception:
            is_error = True
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            with self._lock:
                if operation not in self._metrics:
                    self._metrics[operation] = OperationMetrics(name=operation)
                self._metrics[operation].record(duration_ms, is_error)
    
    @asynccontextmanager
    async def measure_async(self, operation: str):
        """Async context manager to measure operation duration."""
        start = time.perf_counter()
        is_error = False
        try:
            yield
        except Exception:
            is_error = True
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            with self._lock:
                if operation not in self._metrics:
                    self._metrics[operation] = OperationMetrics(name=operation)
                self._metrics[operation].record(duration_ms, is_error)
    
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get all metrics."""
        with self._lock:
            return {
                name: {
                    "calls": m.total_calls,
                    "avg_ms": round(m.avg_time_ms, 2),
                    "min_ms": round(m.min_time_ms, 2) if m.min_time_ms != float('inf') else 0,
                    "max_ms": round(m.max_time_ms, 2),
                    "errors": m.errors,
                    "error_rate": round(m.error_rate * 100, 2)
                }
                for name, m in self._metrics.items()
            }
    
    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._metrics.clear()


# Global metrics collector
metrics = MetricsCollector()


# ═══════════════════════════════════════════════════════════════════════════════
# BATCH QUERY HELPER - Reduce N+1 queries
# ═══════════════════════════════════════════════════════════════════════════════

async def batch_query(
    items: list,
    fetch_func: Callable,
    batch_size: int = 50,
    delay_between_batches: float = 0.01
) -> list:
    """
    Execute queries in batches to reduce N+1 problem.
    
    Example:
        user_ids = [1, 2, 3, ..., 100]
        
        async def fetch_users(ids):
            return await db.get_users_by_ids(ids)
        
        results = await batch_query(user_ids, fetch_users, batch_size=20)
    """
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        try:
            batch_result = await fetch_func(batch)
            if isinstance(batch_result, list):
                results.extend(batch_result)
            else:
                results.append(batch_result)
        except Exception as e:
            logger.exception(f"Batch query failed for items {i}-{i+batch_size}: {e}")
        
        if delay_between_batches > 0 and i + batch_size < len(items):
            await asyncio.sleep(delay_between_batches)
    
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# RETRY WITH BACKOFF - For unreliable operations
# ═══════════════════════════════════════════════════════════════════════════════

async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 10.0,
    exceptions: tuple = (Exception,)
) -> Any:
    """
    Retry async function with exponential backoff.
    
    Example:
        result = await retry_with_backoff(
            lambda: api.fetch_balance(user_id),
            max_retries=3,
            base_delay=1.0
        )
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                delay = min(base_delay * (2 ** attempt), max_delay)
                logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
                await asyncio.sleep(delay)
    
    raise last_exception


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Bounded caches
    'BoundedDict',
    'TTLBoundedDict',
    # Async helpers
    'run_in_executor',
    'sync_to_async',
    # Decorators
    'log_exceptions',
    # Cleanup
    'CacheCleanupScheduler',
    'cache_cleanup_scheduler',
    # Metrics
    'MetricsCollector',
    'metrics',
    # Utilities
    'batch_query',
    'retry_with_backoff',
]
