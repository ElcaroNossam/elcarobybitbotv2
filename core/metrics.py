"""
Performance Metrics and Monitoring System
Tracks key metrics for bot health and performance optimization
"""
from __future__ import annotations

import time
import logging
import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict, deque
from functools import wraps
import threading
import statistics


logger = logging.getLogger(__name__)


@dataclass
class MetricSample:
    """Single metric measurement"""
    value: float
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)


class Counter:
    """Thread-safe counter metric"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self._value = 0.0
        self._lock = threading.Lock()
        self._by_label: Dict[str, float] = defaultdict(float)
    
    def inc(self, value: float = 1.0, **labels) -> None:
        with self._lock:
            self._value += value
            if labels:
                key = ":".join(f"{k}={v}" for k, v in sorted(labels.items()))
                self._by_label[key] += value
    
    @property
    def value(self) -> float:
        return self._value
    
    def get_by_labels(self) -> Dict[str, float]:
        return dict(self._by_label)


class Gauge:
    """Thread-safe gauge metric (can go up or down)"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self._value = 0.0
        self._lock = threading.Lock()
    
    def set(self, value: float) -> None:
        with self._lock:
            self._value = value
    
    def inc(self, value: float = 1.0) -> None:
        with self._lock:
            self._value += value
    
    def dec(self, value: float = 1.0) -> None:
        with self._lock:
            self._value -= value
    
    @property
    def value(self) -> float:
        return self._value


class Histogram:
    """
    Histogram for measuring distributions (latency, sizes, etc.)
    Keeps recent samples for percentile calculations.
    """
    
    def __init__(self, name: str, description: str = "", max_samples: int = 10000):
        self.name = name
        self.description = description
        self._samples: deque = deque(maxlen=max_samples)
        self._lock = threading.Lock()
        self._total_count = 0
        self._total_sum = 0.0
    
    def observe(self, value: float, **labels) -> None:
        with self._lock:
            self._samples.append(MetricSample(value=value, labels=labels))
            self._total_count += 1
            self._total_sum += value
    
    @property
    def count(self) -> int:
        return self._total_count
    
    @property
    def sum(self) -> float:
        return self._total_sum
    
    @property
    def avg(self) -> float:
        if self._total_count == 0:
            return 0.0
        return self._total_sum / self._total_count
    
    def percentile(self, p: float) -> float:
        """Get percentile value (p between 0 and 100)"""
        with self._lock:
            if not self._samples:
                return 0.0
            values = sorted(s.value for s in self._samples)
            idx = int(len(values) * p / 100)
            return values[min(idx, len(values) - 1)]
    
    def get_stats(self) -> Dict[str, float]:
        """Get common statistics"""
        with self._lock:
            if not self._samples:
                return {"count": 0, "avg": 0, "p50": 0, "p95": 0, "p99": 0, "max": 0}
            
            values = [s.value for s in self._samples]
            sorted_values = sorted(values)
            
            return {
                "count": len(values),
                "avg": statistics.mean(values),
                "p50": sorted_values[len(sorted_values) // 2],
                "p95": sorted_values[int(len(sorted_values) * 0.95)],
                "p99": sorted_values[int(len(sorted_values) * 0.99)],
                "max": max(values),
                "min": min(values),
            }


class Timer:
    """Context manager for measuring execution time"""
    
    def __init__(self, histogram: Histogram, **labels):
        self.histogram = histogram
        self.labels = labels
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (time.perf_counter() - self.start_time) * 1000  # ms
        self.histogram.observe(elapsed, **self.labels)


class AsyncTimer:
    """Async context manager for measuring execution time"""
    
    def __init__(self, histogram: Histogram, **labels):
        self.histogram = histogram
        self.labels = labels
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = time.perf_counter()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        elapsed = (time.perf_counter() - self.start_time) * 1000  # ms
        self.histogram.observe(elapsed, **self.labels)


# ═══════════════════════════════════════════════════════════════
# GLOBAL METRICS REGISTRY
# ═══════════════════════════════════════════════════════════════

class MetricsRegistry:
    """Central registry for all metrics"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self._counters: Dict[str, Counter] = {}
        self._gauges: Dict[str, Gauge] = {}
        self._histograms: Dict[str, Histogram] = {}
        
        # Pre-create common metrics
        
        # Counters
        self.requests_total = self.counter(
            "requests_total",
            "Total number of API requests"
        )
        self.errors_total = self.counter(
            "errors_total",
            "Total number of errors"
        )
        self.orders_placed = self.counter(
            "orders_placed_total",
            "Total orders placed"
        )
        self.signals_processed = self.counter(
            "signals_processed_total",
            "Total trading signals processed"
        )
        self.messages_sent = self.counter(
            "messages_sent_total",
            "Total Telegram messages sent"
        )
        
        # Gauges
        self.active_users = self.gauge(
            "active_users",
            "Number of currently active users"
        )
        self.open_positions = self.gauge(
            "open_positions",
            "Number of open positions across all users"
        )
        self.pending_orders = self.gauge(
            "pending_orders",
            "Number of pending limit orders"
        )
        self.memory_usage_mb = self.gauge(
            "memory_usage_mb",
            "Memory usage in MB"
        )
        
        # Histograms
        self.request_latency = self.histogram(
            "request_latency_ms",
            "API request latency in milliseconds"
        )
        self.order_latency = self.histogram(
            "order_latency_ms",
            "Order placement latency in milliseconds"
        )
        self.db_query_latency = self.histogram(
            "db_query_latency_ms",
            "Database query latency in milliseconds"
        )
        self.handler_latency = self.histogram(
            "handler_latency_ms",
            "Telegram handler execution time in milliseconds"
        )
    
    def counter(self, name: str, description: str = "") -> Counter:
        if name not in self._counters:
            self._counters[name] = Counter(name, description)
        return self._counters[name]
    
    def gauge(self, name: str, description: str = "") -> Gauge:
        if name not in self._gauges:
            self._gauges[name] = Gauge(name, description)
        return self._gauges[name]
    
    def histogram(self, name: str, description: str = "") -> Histogram:
        if name not in self._histograms:
            self._histograms[name] = Histogram(name, description)
        return self._histograms[name]
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics in a single dict for monitoring/export"""
        result = {
            "counters": {
                name: {"value": c.value, "by_label": c.get_by_labels()}
                for name, c in self._counters.items()
            },
            "gauges": {
                name: {"value": g.value}
                for name, g in self._gauges.items()
            },
            "histograms": {
                name: h.get_stats()
                for name, h in self._histograms.items()
            },
            "timestamp": time.time()
        }
        return result


# Global registry instance
metrics = MetricsRegistry()


# ═══════════════════════════════════════════════════════════════
# DECORATORS FOR AUTOMATIC METRICS
# ═══════════════════════════════════════════════════════════════

def track_latency(histogram: Histogram = None, name: str = None):
    """
    Decorator to track function execution time.
    
    Example:
        @track_latency(name="my_function")
        async def my_function():
            ...
    """
    def decorator(func):
        hist = histogram or metrics.histogram(name or func.__name__)
        
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    return await func(*args, **kwargs)
                finally:
                    elapsed = (time.perf_counter() - start) * 1000
                    hist.observe(elapsed, function=func.__name__)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    return func(*args, **kwargs)
                finally:
                    elapsed = (time.perf_counter() - start) * 1000
                    hist.observe(elapsed, function=func.__name__)
            return sync_wrapper
    
    return decorator


def count_calls(counter: Counter = None, name: str = None):
    """
    Decorator to count function calls.
    
    Example:
        @count_calls(name="api_requests")
        async def make_request():
            ...
    """
    def decorator(func):
        cnt = counter or metrics.counter(name or f"{func.__name__}_calls")
        
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                cnt.inc(function=func.__name__)
                return await func(*args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                cnt.inc(function=func.__name__)
                return func(*args, **kwargs)
            return sync_wrapper
    
    return decorator


def count_errors(counter: Counter = None, name: str = None):
    """
    Decorator to count errors/exceptions.
    
    Example:
        @count_errors()
        async def risky_operation():
            ...
    """
    def decorator(func):
        cnt = counter or metrics.counter(name or "errors_total")
        
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    cnt.inc(function=func.__name__, error_type=type(e).__name__)
                    raise
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    cnt.inc(function=func.__name__, error_type=type(e).__name__)
                    raise
            return sync_wrapper
    
    return decorator


# ═══════════════════════════════════════════════════════════════
# HEALTH CHECK ENDPOINT
# ═══════════════════════════════════════════════════════════════

async def get_health_status() -> Dict[str, Any]:
    """Get system health status for monitoring"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    # Update memory gauge
    metrics.memory_usage_mb.set(memory_info.rss / 1024 / 1024)
    
    # Get cache stats
    from core.cache import get_all_cache_stats
    cache_stats = get_all_cache_stats()
    
    return {
        "status": "healthy",
        "uptime_seconds": time.time() - process.create_time(),
        "memory": {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
        },
        "cpu_percent": process.cpu_percent(),
        "open_files": len(process.open_files()),
        "threads": process.num_threads(),
        "cache": cache_stats,
        "metrics": metrics.get_all_metrics()
    }


async def periodic_health_check(interval: float = 60.0, callback: Optional[Callable] = None):
    """Background task for periodic health monitoring"""
    while True:
        try:
            health = await get_health_status()
            
            # Log warnings for concerning metrics
            if health["memory"]["rss_mb"] > 1000:
                logger.warning(f"High memory usage: {health['memory']['rss_mb']:.0f}MB")
            
            if callback:
                await callback(health)
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
        
        await asyncio.sleep(interval)
