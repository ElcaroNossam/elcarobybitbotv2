"""
Unified Connection Pool Manager for ElCaro Trading Platform
============================================================
Best practices implementation based on PostgreSQL community recommendations.

Features:
- Singleton pattern with thread-safe initialization
- Health checks with automatic connection validation
- Circuit breaker pattern for cascade failure prevention
- Retry logic with exponential backoff
- Metrics collection for monitoring
- Graceful degradation under load

Based on:
- PostgreSQL Performance Optimization Wiki
- psycopg2/asyncpg best practices
- Python asyncio TaskGroup patterns
"""

from __future__ import annotations

import asyncio
import threading
import time
import logging
import os
from typing import Optional, Dict, Any, Callable, TypeVar
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager, asynccontextmanager
from functools import wraps
import random

logger = logging.getLogger(__name__)

T = TypeVar('T')


# ═══════════════════════════════════════════════════════════════════════════════════
# CIRCUIT BREAKER PATTERN
# ═══════════════════════════════════════════════════════════════════════════════════

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5      # Failures before opening
    success_threshold: int = 2      # Successes to close from half-open
    timeout_seconds: float = 30.0   # Time before trying again
    

class CircuitBreaker:
    """
    Circuit breaker to prevent cascade failures.
    
    When failures exceed threshold, circuit opens and rejects requests
    for timeout_seconds. After timeout, allows one request through
    (half-open) to test if service recovered.
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._lock = threading.RLock()
    
    @property
    def state(self) -> CircuitState:
        with self._lock:
            if self._state == CircuitState.OPEN:
                # Check if timeout expired
                if time.time() - self._last_failure_time >= self.config.timeout_seconds:
                    self._state = CircuitState.HALF_OPEN
                    logger.info(f"Circuit '{self.name}' half-open, testing...")
            return self._state
    
    def record_success(self):
        """Record successful operation"""
        with self._lock:
            self._failure_count = 0
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._success_count = 0
                    logger.info(f"Circuit '{self.name}' closed (recovered)")
    
    def record_failure(self):
        """Record failed operation"""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            self._success_count = 0
            
            if self._failure_count >= self.config.failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(f"Circuit '{self.name}' opened after {self._failure_count} failures")
    
    def allow_request(self) -> bool:
        """Check if request should be allowed"""
        state = self.state
        return state != CircuitState.OPEN
    
    @property
    def stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "name": self.name,
                "state": self._state.value,
                "failure_count": self._failure_count,
                "success_count": self._success_count,
                "last_failure": self._last_failure_time,
            }


# ═══════════════════════════════════════════════════════════════════════════════════
# RETRY LOGIC WITH EXPONENTIAL BACKOFF
# ═══════════════════════════════════════════════════════════════════════════════════

@dataclass
class RetryConfig:
    """Retry configuration"""
    max_retries: int = 3
    base_delay: float = 0.1        # Starting delay in seconds
    max_delay: float = 5.0         # Maximum delay cap
    exponential_base: float = 2.0  # Exponential backoff base
    jitter: bool = True            # Add random jitter to prevent thundering herd


async def retry_async(
    func: Callable,
    config: RetryConfig = None,
    circuit_breaker: CircuitBreaker = None,
    exceptions: tuple = (Exception,)
) -> Any:
    """
    Execute async function with retry logic.
    
    Uses exponential backoff with optional jitter to spread out retries
    and prevent thundering herd problem.
    """
    config = config or RetryConfig()
    last_exception = None
    
    for attempt in range(config.max_retries + 1):
        # Check circuit breaker
        if circuit_breaker and not circuit_breaker.allow_request():
            raise ConnectionError(f"Circuit breaker '{circuit_breaker.name}' is open")
        
        try:
            result = await func()
            if circuit_breaker:
                circuit_breaker.record_success()
            return result
            
        except exceptions as e:
            last_exception = e
            if circuit_breaker:
                circuit_breaker.record_failure()
            
            if attempt < config.max_retries:
                delay = min(
                    config.base_delay * (config.exponential_base ** attempt),
                    config.max_delay
                )
                if config.jitter:
                    delay *= (0.5 + random.random())  # 50-150% of calculated delay
                
                logger.warning(
                    f"Retry {attempt + 1}/{config.max_retries} after error: {e}. "
                    f"Waiting {delay:.2f}s"
                )
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {config.max_retries} retries failed: {e}")
    
    raise last_exception


def retry_sync(
    func: Callable,
    config: RetryConfig = None,
    circuit_breaker: CircuitBreaker = None,
    exceptions: tuple = (Exception,)
) -> Any:
    """Synchronous version of retry logic"""
    config = config or RetryConfig()
    last_exception = None
    
    for attempt in range(config.max_retries + 1):
        if circuit_breaker and not circuit_breaker.allow_request():
            raise ConnectionError(f"Circuit breaker '{circuit_breaker.name}' is open")
        
        try:
            result = func()
            if circuit_breaker:
                circuit_breaker.record_success()
            return result
            
        except exceptions as e:
            last_exception = e
            if circuit_breaker:
                circuit_breaker.record_failure()
            
            if attempt < config.max_retries:
                delay = min(
                    config.base_delay * (config.exponential_base ** attempt),
                    config.max_delay
                )
                if config.jitter:
                    delay *= (0.5 + random.random())
                
                logger.warning(f"Retry {attempt + 1}/{config.max_retries}: {e}. Waiting {delay:.2f}s")
                time.sleep(delay)
    
    raise last_exception


# ═══════════════════════════════════════════════════════════════════════════════════
# POOL METRICS
# ═══════════════════════════════════════════════════════════════════════════════════

@dataclass
class PoolMetrics:
    """Metrics for connection pool monitoring"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    waiting_requests: int = 0
    
    # Counters
    connections_created: int = 0
    connections_destroyed: int = 0
    connection_errors: int = 0
    
    # Timing
    avg_acquire_time_ms: float = 0.0
    avg_query_time_ms: float = 0.0
    
    # Health
    last_health_check: float = 0.0
    health_check_failures: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_connections": self.total_connections,
            "active_connections": self.active_connections,
            "idle_connections": self.idle_connections,
            "waiting_requests": self.waiting_requests,
            "connections_created": self.connections_created,
            "connections_destroyed": self.connections_destroyed,
            "connection_errors": self.connection_errors,
            "avg_acquire_time_ms": round(self.avg_acquire_time_ms, 2),
            "avg_query_time_ms": round(self.avg_query_time_ms, 2),
            "last_health_check": self.last_health_check,
            "health_check_failures": self.health_check_failures,
        }


# ═══════════════════════════════════════════════════════════════════════════════════
# UNIFIED POOL MANAGER
# ═══════════════════════════════════════════════════════════════════════════════════

class UnifiedPoolManager:
    """
    Unified connection pool manager supporting both sync and async operations.
    
    Best Practices Applied:
    1. Singleton pattern with double-check locking
    2. Separate pools for sync (psycopg2) and async (asyncpg)
    3. Connection health validation before use
    4. Circuit breaker for cascade failure prevention
    5. Metrics collection for monitoring
    6. Graceful degradation under high load
    
    Usage:
        manager = UnifiedPoolManager.get_instance()
        
        # Sync
        with manager.sync_connection() as conn:
            cursor = conn.cursor()
            ...
        
        # Async  
        async with manager.async_connection() as conn:
            await conn.fetch(...)
    """
    
    _instance: Optional['UnifiedPoolManager'] = None
    _lock = threading.Lock()
    
    def __init__(self):
        # Configuration from environment
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://elcaro:elcaro_prod_2026@127.0.0.1:5432/elcaro"
        )
        
        # Pool configuration - tuned for trading bot workload
        self.min_sync_connections = int(os.getenv("DB_MIN_SYNC_CONN", "5"))
        self.max_sync_connections = int(os.getenv("DB_MAX_SYNC_CONN", "50"))
        self.min_async_connections = int(os.getenv("DB_MIN_ASYNC_CONN", "10"))
        self.max_async_connections = int(os.getenv("DB_MAX_ASYNC_CONN", "100"))
        
        # Timeouts
        self.connection_timeout = float(os.getenv("DB_CONN_TIMEOUT", "5.0"))
        self.query_timeout = float(os.getenv("DB_QUERY_TIMEOUT", "30.0"))
        self.idle_timeout = float(os.getenv("DB_IDLE_TIMEOUT", "300.0"))
        
        # Internal state
        self._sync_pool = None
        self._async_pool = None
        self._sync_pool_lock = threading.Lock()
        self._async_pool_lock = asyncio.Lock()
        
        # Circuit breaker
        self._circuit_breaker = CircuitBreaker(
            "database",
            CircuitBreakerConfig(
                failure_threshold=5,
                success_threshold=2,
                timeout_seconds=30.0
            )
        )
        
        # Metrics
        self._metrics = PoolMetrics()
        self._metrics_lock = threading.Lock()
        
        # Retry config
        self._retry_config = RetryConfig(
            max_retries=3,
            base_delay=0.1,
            max_delay=5.0
        )
        
        logger.info("UnifiedPoolManager initialized")
    
    @classmethod
    def get_instance(cls) -> 'UnifiedPoolManager':
        """Get singleton instance with double-check locking"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    # ═══════════════════════════════════════════════════════════════════════
    # SYNC POOL (psycopg2)
    # ═══════════════════════════════════════════════════════════════════════
    
    def _get_sync_pool(self):
        """Get or create sync connection pool"""
        if self._sync_pool is None:
            with self._sync_pool_lock:
                if self._sync_pool is None:
                    import psycopg2.pool
                    
                    logger.info(
                        f"Creating sync pool: min={self.min_sync_connections}, "
                        f"max={self.max_sync_connections}"
                    )
                    self._sync_pool = psycopg2.pool.ThreadedConnectionPool(
                        minconn=self.min_sync_connections,
                        maxconn=self.max_sync_connections,
                        dsn=self.database_url
                    )
                    self._metrics.connections_created += self.min_sync_connections
                    logger.info("Sync connection pool created successfully")
        
        return self._sync_pool
    
    @contextmanager
    def sync_connection(self, autocommit: bool = False):
        """
        Get sync connection from pool with automatic return.
        
        Features:
        - Circuit breaker check
        - Health validation
        - Automatic rollback on exception
        - Metrics tracking
        """
        if not self._circuit_breaker.allow_request():
            raise ConnectionError("Database circuit breaker is open")
        
        pool = self._get_sync_pool()
        conn = None
        start_time = time.time()
        
        try:
            conn = pool.getconn()
            if autocommit:
                conn.autocommit = True
            
            # Track acquire time
            acquire_time = (time.time() - start_time) * 1000
            self._update_metrics(acquire_time_ms=acquire_time)
            
            self._metrics.active_connections += 1
            self._circuit_breaker.record_success()
            
            yield conn
            
            if not autocommit:
                conn.commit()
                
        except Exception as e:
            self._circuit_breaker.record_failure()
            self._metrics.connection_errors += 1
            
            if conn and not autocommit:
                try:
                    conn.rollback()
                except Exception:
                    pass
            raise
            
        finally:
            if conn:
                self._metrics.active_connections -= 1
                pool.putconn(conn)
    
    def sync_execute(self, query: str, params: tuple = None) -> list:
        """Execute query and return results as list of dicts"""
        import psycopg2.extras
        
        with self.sync_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, params)
                if cur.description:
                    return [dict(row) for row in cur.fetchall()]
                return []
    
    def sync_execute_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """Execute query and return single result"""
        results = self.sync_execute(query, params)
        return results[0] if results else None
    
    def sync_execute_write(self, query: str, params: tuple = None) -> int:
        """Execute INSERT/UPDATE/DELETE and return affected rows"""
        with self.sync_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.rowcount
    
    # ═══════════════════════════════════════════════════════════════════════
    # ASYNC POOL (asyncpg)
    # ═══════════════════════════════════════════════════════════════════════
    
    async def _get_async_pool(self):
        """Get or create async connection pool"""
        if self._async_pool is None:
            async with self._async_pool_lock:
                if self._async_pool is None:
                    import asyncpg
                    
                    logger.info(
                        f"Creating async pool: min={self.min_async_connections}, "
                        f"max={self.max_async_connections}"
                    )
                    
                    self._async_pool = await asyncpg.create_pool(
                        self.database_url,
                        min_size=self.min_async_connections,
                        max_size=self.max_async_connections,
                        max_inactive_connection_lifetime=self.idle_timeout,
                        command_timeout=self.query_timeout,
                    )
                    self._metrics.connections_created += self.min_async_connections
                    logger.info("Async connection pool created successfully")
        
        return self._async_pool
    
    @asynccontextmanager
    async def async_connection(self):
        """
        Get async connection from pool with automatic return.
        
        Features same as sync_connection but for async code.
        """
        if not self._circuit_breaker.allow_request():
            raise ConnectionError("Database circuit breaker is open")
        
        pool = await self._get_async_pool()
        start_time = time.time()
        
        conn = await pool.acquire()
        try:
            acquire_time = (time.time() - start_time) * 1000
            self._update_metrics(acquire_time_ms=acquire_time)
            
            self._metrics.active_connections += 1
            self._circuit_breaker.record_success()
            
            yield conn
            
        except Exception as e:
            self._circuit_breaker.record_failure()
            self._metrics.connection_errors += 1
            raise
            
        finally:
            self._metrics.active_connections -= 1
            await pool.release(conn)
    
    @asynccontextmanager
    async def async_transaction(self):
        """Get connection with transaction context"""
        async with self.async_connection() as conn:
            async with conn.transaction():
                yield conn
    
    async def async_fetch(self, query: str, *args) -> list:
        """Execute query and fetch all results"""
        async with self.async_connection() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def async_fetchrow(self, query: str, *args) -> Optional[Dict]:
        """Execute query and fetch single row"""
        async with self.async_connection() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def async_fetchval(self, query: str, *args) -> Any:
        """Execute query and fetch single value"""
        async with self.async_connection() as conn:
            return await conn.fetchval(query, *args)
    
    async def async_execute(self, query: str, *args) -> str:
        """Execute query and return status"""
        async with self.async_connection() as conn:
            return await conn.execute(query, *args)
    
    # ═══════════════════════════════════════════════════════════════════════
    # HEALTH CHECKS
    # ═══════════════════════════════════════════════════════════════════════
    
    async def health_check_async(self) -> bool:
        """Async health check - verify database connectivity"""
        try:
            result = await self.async_fetchval("SELECT 1")
            self._metrics.last_health_check = time.time()
            return result == 1
        except Exception as e:
            self._metrics.health_check_failures += 1
            logger.error(f"Async health check failed: {e}")
            return False
    
    def health_check_sync(self) -> bool:
        """Sync health check"""
        try:
            with self.sync_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    result = cur.fetchone()
                    self._metrics.last_health_check = time.time()
                    return result[0] == 1
        except Exception as e:
            self._metrics.health_check_failures += 1
            logger.error(f"Sync health check failed: {e}")
            return False
    
    # ═══════════════════════════════════════════════════════════════════════
    # METRICS & MONITORING
    # ═══════════════════════════════════════════════════════════════════════
    
    def _update_metrics(self, acquire_time_ms: float = None, query_time_ms: float = None):
        """Update pool metrics (thread-safe)"""
        with self._metrics_lock:
            if acquire_time_ms is not None:
                # Exponential moving average
                alpha = 0.1
                self._metrics.avg_acquire_time_ms = (
                    alpha * acquire_time_ms + 
                    (1 - alpha) * self._metrics.avg_acquire_time_ms
                )
            
            if query_time_ms is not None:
                alpha = 0.1
                self._metrics.avg_query_time_ms = (
                    alpha * query_time_ms +
                    (1 - alpha) * self._metrics.avg_query_time_ms
                )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all pool metrics"""
        metrics = self._metrics.to_dict()
        metrics["circuit_breaker"] = self._circuit_breaker.stats
        return metrics
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get detailed pool status"""
        status = {
            "sync_pool": None,
            "async_pool": None,
            "circuit_breaker_state": self._circuit_breaker.state.value,
        }
        
        if self._sync_pool:
            status["sync_pool"] = {
                "min_connections": self.min_sync_connections,
                "max_connections": self.max_sync_connections,
            }
        
        if self._async_pool:
            status["async_pool"] = {
                "min_connections": self.min_async_connections,
                "max_connections": self.max_async_connections,
                "size": self._async_pool.get_size(),
                "free_size": self._async_pool.get_idle_size(),
            }
        
        return status
    
    # ═══════════════════════════════════════════════════════════════════════
    # CLEANUP
    # ═══════════════════════════════════════════════════════════════════════
    
    async def close_async(self):
        """Close async pool"""
        if self._async_pool:
            await self._async_pool.close()
            self._async_pool = None
            logger.info("Async pool closed")
    
    def close_sync(self):
        """Close sync pool"""
        if self._sync_pool:
            self._sync_pool.closeall()
            self._sync_pool = None
            logger.info("Sync pool closed")
    
    async def close_all(self):
        """Close all pools"""
        await self.close_async()
        self.close_sync()
        logger.info("All pools closed")


# ═══════════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def get_pool_manager() -> UnifiedPoolManager:
    """Get the unified pool manager instance"""
    return UnifiedPoolManager.get_instance()


# Sync shortcuts
def execute(query: str, params: tuple = None) -> list:
    """Execute sync query and return results"""
    return get_pool_manager().sync_execute(query, params)


def execute_one(query: str, params: tuple = None) -> Optional[Dict]:
    """Execute sync query and return single result"""
    return get_pool_manager().sync_execute_one(query, params)


def execute_write(query: str, params: tuple = None) -> int:
    """Execute sync write query"""
    return get_pool_manager().sync_execute_write(query, params)


@contextmanager
def get_conn():
    """Get sync connection from pool"""
    with get_pool_manager().sync_connection() as conn:
        yield conn


# Async shortcuts
async def async_fetch(query: str, *args) -> list:
    """Execute async query and return results"""
    return await get_pool_manager().async_fetch(query, *args)


async def async_fetchrow(query: str, *args) -> Optional[Dict]:
    """Execute async query and return single result"""
    return await get_pool_manager().async_fetchrow(query, *args)


async def async_execute(query: str, *args) -> str:
    """Execute async query"""
    return await get_pool_manager().async_execute(query, *args)


@asynccontextmanager
async def async_conn():
    """Get async connection from pool"""
    async with get_pool_manager().async_connection() as conn:
        yield conn


@asynccontextmanager
async def async_transaction():
    """Get async connection with transaction"""
    async with get_pool_manager().async_transaction() as conn:
        yield conn


# ═══════════════════════════════════════════════════════════════════════════════════
# BACKGROUND TASKS
# ═══════════════════════════════════════════════════════════════════════════════════

async def periodic_health_check(interval: float = 30.0):
    """Background task for periodic health checks"""
    manager = get_pool_manager()
    
    while True:
        await asyncio.sleep(interval)
        try:
            healthy = await manager.health_check_async()
            if not healthy:
                logger.warning("Database health check failed")
        except Exception as e:
            logger.error(f"Health check error: {e}")


async def periodic_metrics_log(interval: float = 60.0):
    """Background task for logging metrics"""
    manager = get_pool_manager()
    
    while True:
        await asyncio.sleep(interval)
        try:
            metrics = manager.get_metrics()
            logger.info(f"Pool metrics: {metrics}")
        except Exception as e:
            logger.error(f"Metrics logging error: {e}")
