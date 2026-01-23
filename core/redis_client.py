"""
Redis Client for Lyxen Trading Platform
=========================================
Distributed caching, rate limiting, pub/sub for 10K+ users

Features:
- Connection pooling (100 connections)
- User cache (TTL 30s)
- Price cache (real-time from WebSocket)
- Distributed rate limiting
- Signal pub/sub broadcasting
"""

import redis.asyncio as redis
from redis.asyncio import ConnectionPool
from typing import Optional, Any, Dict, List, Set
import json
import logging
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

# Singleton instance
_redis_client: Optional['RedisClient'] = None


class RedisClient:
    """
    Async Redis client with connection pooling.
    
    Usage:
        redis = await get_redis()
        await redis.set_user_cache(user_id, data)
        data = await redis.get_user_cache(user_id)
    """
    
    def __init__(self, url: str = "redis://localhost:6379"):
        self.url = url
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
        self._connected = False
        self._lock = asyncio.Lock()
    
    async def connect(self) -> bool:
        """Initialize connection pool"""
        if self._connected:
            return True
        
        async with self._lock:
            if self._connected:
                return True
            
            try:
                self.pool = ConnectionPool.from_url(
                    self.url,
                    max_connections=100,
                    decode_responses=True
                )
                self.client = redis.Redis(connection_pool=self.pool)
                
                # Test connection
                await self.client.ping()
                self._connected = True
                logger.info(f"✅ Redis connected: {self.url}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Redis connection failed: {e}")
                self._connected = False
                return False
    
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.disconnect()
            self._connected = False
            logger.info("Redis disconnected")
    
    # ═══════════════════════════════════════════════════════════════
    # USER CACHE
    # ═══════════════════════════════════════════════════════════════
    
    async def get_user_cache(self, user_id: int) -> Optional[dict]:
        """Get cached user config"""
        if not self._connected:
            return None
        
        try:
            key = f"user:{user_id}"
            data = await self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.warning(f"Redis get_user_cache error: {e}")
            return None
    
    async def set_user_cache(self, user_id: int, data: dict, ttl: int = 30):
        """Cache user config with TTL"""
        if not self._connected:
            return
        
        try:
            key = f"user:{user_id}"
            await self.client.setex(key, ttl, json.dumps(data))
        except Exception as e:
            logger.warning(f"Redis set_user_cache error: {e}")
    
    async def invalidate_user_cache(self, user_id: int):
        """Invalidate user cache"""
        if not self._connected:
            return
        
        try:
            key = f"user:{user_id}"
            await self.client.delete(key)
        except Exception as e:
            logger.warning(f"Redis invalidate_user_cache error: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # PRICE CACHE (Updated by WebSocket worker)
    # ═══════════════════════════════════════════════════════════════
    
    async def get_price(self, symbol: str) -> Optional[float]:
        """Get cached price for symbol"""
        if not self._connected:
            return None
        
        try:
            price = await self.client.hget("prices", symbol)
            return float(price) if price else None
        except Exception as e:
            logger.warning(f"Redis get_price error: {e}")
            return None
    
    async def set_price(self, symbol: str, price: float):
        """Set price (called by WebSocket worker)"""
        if not self._connected:
            return
        
        try:
            await self.client.hset("prices", symbol, str(price))
        except Exception as e:
            logger.warning(f"Redis set_price error: {e}")
    
    async def get_all_prices(self) -> Dict[str, float]:
        """Get all cached prices"""
        if not self._connected:
            return {}
        
        try:
            prices = await self.client.hgetall("prices")
            return {k: float(v) for k, v in prices.items()}
        except Exception as e:
            logger.warning(f"Redis get_all_prices error: {e}")
            return {}
    
    async def set_prices_bulk(self, prices: Dict[str, float]):
        """Bulk update prices"""
        if not self._connected or not prices:
            return
        
        try:
            await self.client.hset("prices", mapping={k: str(v) for k, v in prices.items()})
        except Exception as e:
            logger.warning(f"Redis set_prices_bulk error: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # RATE LIMITING
    # ═══════════════════════════════════════════════════════════════
    
    async def rate_limit(
        self, 
        user_id: int, 
        action: str = "api",
        limit: int = 60, 
        window: int = 60
    ) -> bool:
        """
        Distributed rate limiting using sliding window.
        
        Returns True if request is allowed, False if rate limited.
        """
        if not self._connected:
            return True  # Allow if Redis unavailable
        
        try:
            key = f"ratelimit:{action}:{user_id}"
            current = await self.client.incr(key)
            
            if current == 1:
                await self.client.expire(key, window)
            
            return current <= limit
            
        except Exception as e:
            logger.warning(f"Redis rate_limit error: {e}")
            return True  # Allow on error
    
    async def get_rate_limit_remaining(
        self, 
        user_id: int, 
        action: str = "api",
        limit: int = 60
    ) -> int:
        """Get remaining rate limit quota"""
        if not self._connected:
            return limit
        
        try:
            key = f"ratelimit:{action}:{user_id}"
            current = await self.client.get(key)
            if current is None:
                return limit
            return max(0, limit - int(current))
        except Exception:
            return limit
    
    # ═══════════════════════════════════════════════════════════════
    # PUB/SUB - Signal Broadcasting
    # ═══════════════════════════════════════════════════════════════
    
    async def publish_signal(self, signal: dict):
        """Publish signal to all workers"""
        if not self._connected:
            return
        
        try:
            await self.client.publish("signals", json.dumps(signal))
            logger.debug(f"Published signal: {signal.get('symbol')}")
        except Exception as e:
            logger.error(f"Redis publish_signal error: {e}")
    
    async def publish_price_update(self, symbol: str, price: float):
        """Publish price update event"""
        if not self._connected:
            return
        
        try:
            await self.client.publish(
                "price_updates",
                json.dumps({"symbol": symbol, "price": price})
            )
        except Exception as e:
            logger.warning(f"Redis publish_price_update error: {e}")
    
    async def subscribe_signals(self, callback):
        """Subscribe to signal channel"""
        if not self._connected:
            return
        
        try:
            pubsub = self.client.pubsub()
            await pubsub.subscribe("signals")
            
            async for message in pubsub.listen():
                if message["type"] == "message":
                    signal = json.loads(message["data"])
                    await callback(signal)
                    
        except Exception as e:
            logger.error(f"Redis subscribe_signals error: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # SESSION STORAGE
    # ═══════════════════════════════════════════════════════════════
    
    async def set_session(self, session_id: str, data: dict, ttl: int = 3600):
        """Store session data"""
        if not self._connected:
            return
        
        try:
            key = f"session:{session_id}"
            await self.client.setex(key, ttl, json.dumps(data))
        except Exception as e:
            logger.warning(f"Redis set_session error: {e}")
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        if not self._connected:
            return None
        
        try:
            key = f"session:{session_id}"
            data = await self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.warning(f"Redis get_session error: {e}")
            return None
    
    async def delete_session(self, session_id: str):
        """Delete session"""
        if not self._connected:
            return
        
        try:
            key = f"session:{session_id}"
            await self.client.delete(key)
        except Exception as e:
            logger.warning(f"Redis delete_session error: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # DISTRIBUTED LOCKS
    # ═══════════════════════════════════════════════════════════════
    
    async def acquire_lock(
        self, 
        lock_name: str, 
        timeout: int = 10,
        blocking: bool = True
    ) -> bool:
        """
        Acquire distributed lock.
        
        Usage:
            if await redis.acquire_lock(f"trade:{user_id}:{symbol}"):
                try:
                    # do work
                finally:
                    await redis.release_lock(f"trade:{user_id}:{symbol}")
        """
        if not self._connected:
            return True
        
        try:
            key = f"lock:{lock_name}"
            
            if blocking:
                # Try to acquire with retries
                for _ in range(timeout * 10):
                    if await self.client.set(key, "1", nx=True, ex=timeout):
                        return True
                    await asyncio.sleep(0.1)
                return False
            else:
                return await self.client.set(key, "1", nx=True, ex=timeout)
                
        except Exception as e:
            logger.warning(f"Redis acquire_lock error: {e}")
            return True
    
    async def release_lock(self, lock_name: str):
        """Release distributed lock"""
        if not self._connected:
            return
        
        try:
            key = f"lock:{lock_name}"
            await self.client.delete(key)
        except Exception as e:
            logger.warning(f"Redis release_lock error: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # POSITION TRACKING
    # ═══════════════════════════════════════════════════════════════
    
    async def add_active_position(
        self, 
        user_id: int, 
        symbol: str, 
        account_type: str,
        position_data: dict
    ):
        """Track active position in Redis for fast lookup"""
        if not self._connected:
            return
        
        try:
            key = f"positions:{user_id}"
            field = f"{symbol}:{account_type}"
            await self.client.hset(key, field, json.dumps(position_data))
        except Exception as e:
            logger.warning(f"Redis add_active_position error: {e}")
    
    async def remove_active_position(
        self, 
        user_id: int, 
        symbol: str, 
        account_type: str
    ):
        """Remove position from Redis tracking"""
        if not self._connected:
            return
        
        try:
            key = f"positions:{user_id}"
            field = f"{symbol}:{account_type}"
            await self.client.hdel(key, field)
        except Exception as e:
            logger.warning(f"Redis remove_active_position error: {e}")
    
    async def get_user_positions(self, user_id: int) -> Dict[str, dict]:
        """Get all positions for user from Redis"""
        if not self._connected:
            return {}
        
        try:
            key = f"positions:{user_id}"
            positions = await self.client.hgetall(key)
            return {k: json.loads(v) for k, v in positions.items()}
        except Exception as e:
            logger.warning(f"Redis get_user_positions error: {e}")
            return {}
    
    # ═══════════════════════════════════════════════════════════════
    # EMAIL VERIFICATION CODES (for multi-worker support)
    # ═══════════════════════════════════════════════════════════════
    
    async def set_verification_code(
        self, 
        email: str, 
        data: dict, 
        ttl: int = 900  # 15 minutes
    ):
        """Store email verification code with TTL"""
        if not self._connected:
            return False
        
        try:
            key = f"verify:{email.lower()}"
            await self.client.setex(key, ttl, json.dumps(data))
            return True
        except Exception as e:
            logger.warning(f"Redis set_verification_code error: {e}")
            return False
    
    async def get_verification_code(self, email: str) -> Optional[dict]:
        """Get pending verification data"""
        if not self._connected:
            return None
        
        try:
            key = f"verify:{email.lower()}"
            data = await self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.warning(f"Redis get_verification_code error: {e}")
            return None
    
    async def delete_verification_code(self, email: str):
        """Delete verification code after use"""
        if not self._connected:
            return
        
        try:
            key = f"verify:{email.lower()}"
            await self.client.delete(key)
        except Exception as e:
            logger.warning(f"Redis delete_verification_code error: {e}")
    
    async def set_password_reset_code(
        self, 
        email: str, 
        data: dict, 
        ttl: int = 3600  # 1 hour
    ):
        """Store password reset code with TTL"""
        if not self._connected:
            return False
        
        try:
            key = f"reset:{email.lower()}"
            await self.client.setex(key, ttl, json.dumps(data))
            return True
        except Exception as e:
            logger.warning(f"Redis set_password_reset_code error: {e}")
            return False
    
    async def get_password_reset_code(self, email: str) -> Optional[dict]:
        """Get password reset data"""
        if not self._connected:
            return None
        
        try:
            key = f"reset:{email.lower()}"
            data = await self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.warning(f"Redis get_password_reset_code error: {e}")
            return None
    
    async def delete_password_reset_code(self, email: str):
        """Delete password reset code after use"""
        if not self._connected:
            return
        
        try:
            key = f"reset:{email.lower()}"
            await self.client.delete(key)
        except Exception as e:
            logger.warning(f"Redis delete_password_reset_code error: {e}")
        except Exception as e:
            logger.warning(f"Redis get_user_positions error: {e}")
            return {}
    
    # ═══════════════════════════════════════════════════════════════
    # METRICS / STATS
    # ═══════════════════════════════════════════════════════════════
    
    async def increment_metric(self, metric: str, value: int = 1):
        """Increment a metric counter"""
        if not self._connected:
            return
        
        try:
            await self.client.hincrby("metrics", metric, value)
        except Exception as e:
            logger.warning(f"Redis increment_metric error: {e}")
    
    async def get_metrics(self) -> Dict[str, int]:
        """Get all metrics"""
        if not self._connected:
            return {}
        
        try:
            metrics = await self.client.hgetall("metrics")
            return {k: int(v) for k, v in metrics.items()}
        except Exception as e:
            logger.warning(f"Redis get_metrics error: {e}")
            return {}
    
    # ═══════════════════════════════════════════════════════════════
    # HEALTH CHECK
    # ═══════════════════════════════════════════════════════════════
    
    async def health_check(self) -> dict:
        """Check Redis health"""
        if not self._connected:
            return {"status": "disconnected", "latency_ms": None}
        
        try:
            import time
            start = time.time()
            await self.client.ping()
            latency = (time.time() - start) * 1000
            
            info = await self.client.info("memory")
            
            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients")
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════
# SINGLETON ACCESS
# ═══════════════════════════════════════════════════════════════════════

async def get_redis(url: str = None) -> RedisClient:
    """Get singleton Redis client"""
    global _redis_client
    
    if _redis_client is None:
        import os
        url = url or os.getenv("REDIS_URL", "redis://localhost:6379")
        _redis_client = RedisClient(url)
        await _redis_client.connect()
    
    return _redis_client


def redis_cached(ttl: int = 30, key_prefix: str = "cache"):
    """
    Decorator for caching function results in Redis.
    
    Usage:
        @redis_cached(ttl=60, key_prefix="balance")
        async def get_user_balance(user_id: int):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            redis = await get_redis()
            
            # Build cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(a) for a in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            try:
                cached = await redis.client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            
            try:
                await redis.client.setex(cache_key, ttl, json.dumps(result))
            except Exception:
                pass
            
            return result
        
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════════════
# FALLBACK IN-MEMORY CACHE (when Redis unavailable)
# ═══════════════════════════════════════════════════════════════════════

class InMemoryFallback:
    """Fallback cache when Redis is unavailable"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._expires: Dict[str, float] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        import time
        if key in self._expires and time.time() > self._expires[key]:
            del self._cache[key]
            del self._expires[key]
            return None
        return self._cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = 30):
        import time
        self._cache[key] = value
        self._expires[key] = time.time() + ttl
    
    async def delete(self, key: str):
        self._cache.pop(key, None)
        self._expires.pop(key, None)


# Global fallback
_fallback_cache = InMemoryFallback()


async def get_with_fallback(
    redis: RedisClient, 
    key: str, 
    fetch_func, 
    ttl: int = 30
) -> Any:
    """
    Get value from Redis with in-memory fallback.
    
    Usage:
        data = await get_with_fallback(
            redis, 
            f"user:{user_id}", 
            lambda: db.get_user_config(user_id),
            ttl=30
        )
    """
    # Try Redis first
    if redis._connected:
        try:
            cached = await redis.client.get(key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass
    
    # Try in-memory fallback
    cached = await _fallback_cache.get(key)
    if cached:
        return cached
    
    # Fetch fresh data
    data = await fetch_func() if asyncio.iscoroutinefunction(fetch_func) else fetch_func()
    
    # Cache in both
    if data is not None:
        try:
            if redis._connected:
                await redis.client.setex(key, ttl, json.dumps(data))
        except Exception:
            pass
        await _fallback_cache.set(key, data, ttl)
    
    return data
