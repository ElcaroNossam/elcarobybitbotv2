"""
Rate Limiter with Token Bucket Algorithm
Prevents API rate limit errors with intelligent request throttling
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, Optional
import threading
from collections import defaultdict


@dataclass
class TokenBucket:
    """
    Token bucket rate limiter.
    Allows burst traffic while limiting average rate.
    """
    capacity: float  # Maximum tokens (burst size)
    refill_rate: float  # Tokens per second
    tokens: float = field(default=None)
    last_update: float = field(default=None)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    
    def __post_init__(self):
        if self.tokens is None:
            self.tokens = self.capacity
        if self.last_update is None:
            self.last_update = time.time()
    
    def _refill(self) -> None:
        """Add tokens based on time elapsed"""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_update = now
    
    def try_acquire(self, tokens: float = 1.0) -> bool:
        """
        Try to acquire tokens without blocking.
        Returns True if successful, False if not enough tokens.
        """
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def acquire_wait_time(self, tokens: float = 1.0) -> float:
        """
        Calculate time to wait before tokens become available.
        Returns 0 if tokens are available now.
        """
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                return 0.0
            needed = tokens - self.tokens
            return needed / self.refill_rate
    
    async def acquire(self, tokens: float = 1.0) -> None:
        """Acquire tokens, waiting if necessary"""
        while True:
            wait_time = self.acquire_wait_time(tokens)
            if wait_time <= 0:
                with self._lock:
                    self._refill()
                    if self.tokens >= tokens:
                        self.tokens -= tokens
                        return
            await asyncio.sleep(min(wait_time, 0.1))
    
    @property
    def available_tokens(self) -> float:
        """Current available tokens"""
        with self._lock:
            self._refill()
            return self.tokens


class RateLimiter:
    """
    Multi-key rate limiter for per-user and per-endpoint limiting.
    
    Example:
        limiter = RateLimiter()
        
        # Limit user to 10 requests per second
        limiter.set_limit("user", capacity=10, refill_rate=10)
        
        # Limit specific endpoint to 5 requests per second
        limiter.set_limit("order", capacity=5, refill_rate=5)
        
        # Check before making request
        if await limiter.acquire("user:123", "order"):
            await make_api_request()
    """
    
    def __init__(self):
        self._buckets: Dict[str, TokenBucket] = {}
        self._limits: Dict[str, tuple[float, float]] = {}
        self._lock = threading.Lock()
        
        # Default limits
        self.set_limit("default", capacity=50, refill_rate=10)
        self.set_limit("user", capacity=20, refill_rate=5)
        self.set_limit("order", capacity=10, refill_rate=5)
        self.set_limit("balance", capacity=10, refill_rate=2)
        self.set_limit("positions", capacity=10, refill_rate=2)
    
    def set_limit(self, limit_type: str, capacity: float, refill_rate: float) -> None:
        """Define a rate limit type"""
        self._limits[limit_type] = (capacity, refill_rate)
    
    def _get_or_create_bucket(self, key: str, limit_type: str) -> TokenBucket:
        """Get or create a token bucket for the given key"""
        full_key = f"{limit_type}:{key}"
        
        with self._lock:
            if full_key not in self._buckets:
                capacity, refill_rate = self._limits.get(
                    limit_type, self._limits["default"]
                )
                self._buckets[full_key] = TokenBucket(
                    capacity=capacity,
                    refill_rate=refill_rate
                )
            return self._buckets[full_key]
    
    def try_acquire(self, key: str, limit_type: str = "default", tokens: float = 1.0) -> bool:
        """Try to acquire rate limit permission without blocking"""
        bucket = self._get_or_create_bucket(key, limit_type)
        return bucket.try_acquire(tokens)
    
    async def acquire(self, key: str, limit_type: str = "default", tokens: float = 1.0) -> None:
        """Acquire rate limit permission, waiting if necessary"""
        bucket = self._get_or_create_bucket(key, limit_type)
        await bucket.acquire(tokens)
    
    def wait_time(self, key: str, limit_type: str = "default", tokens: float = 1.0) -> float:
        """Get estimated wait time until tokens become available"""
        bucket = self._get_or_create_bucket(key, limit_type)
        return bucket.acquire_wait_time(tokens)
    
    def cleanup(self, max_idle_seconds: float = 3600) -> int:
        """Remove buckets that haven't been used recently"""
        now = time.time()
        removed = 0
        
        with self._lock:
            keys_to_remove = [
                key for key, bucket in self._buckets.items()
                if now - bucket.last_update > max_idle_seconds
            ]
            for key in keys_to_remove:
                del self._buckets[key]
                removed += 1
        
        return removed


# ═══════════════════════════════════════════════════════════════
# EXCHANGE-SPECIFIC RATE LIMITERS
# ═══════════════════════════════════════════════════════════════

class BybitRateLimiter(RateLimiter):
    """
    Rate limiter tuned for Bybit API limits.
    
    Bybit limits:
    - 120 requests per second overall
    - 10 orders per second per symbol
    - Different limits for different endpoints
    """
    
    def __init__(self):
        super().__init__()
        
        # Override with Bybit-specific limits
        self.set_limit("default", capacity=100, refill_rate=100)
        self.set_limit("order", capacity=10, refill_rate=10)
        self.set_limit("cancel", capacity=10, refill_rate=10)
        self.set_limit("position", capacity=50, refill_rate=50)
        self.set_limit("balance", capacity=50, refill_rate=50)
        self.set_limit("market_data", capacity=100, refill_rate=100)


class HyperLiquidRateLimiter(RateLimiter):
    """
    Rate limiter tuned for HyperLiquid API limits.
    
    HyperLiquid limits:
    - 1200 requests per minute (20 per second)
    - Order limits depend on tier
    """
    
    def __init__(self):
        super().__init__()
        
        # HyperLiquid-specific limits
        self.set_limit("default", capacity=20, refill_rate=20)
        self.set_limit("order", capacity=5, refill_rate=5)
        self.set_limit("info", capacity=20, refill_rate=20)


# Global instances
bybit_limiter = BybitRateLimiter()
hl_limiter = HyperLiquidRateLimiter()


def rate_limited(limit_type: str = "default", key_arg: int = 0):
    """
    Decorator to rate limit async functions.
    
    Args:
        limit_type: Type of limit to apply
        key_arg: Index of argument to use as rate limit key (e.g., user_id)
    
    Example:
        @rate_limited("order", key_arg=0)
        async def place_order(user_id: int, symbol: str, ...):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract key from arguments
            key = str(args[key_arg]) if len(args) > key_arg else "default"
            
            # Determine which limiter to use based on function module
            limiter = bybit_limiter  # Default
            
            await limiter.acquire(key, limit_type)
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


import functools  # Add import at top when integrating
