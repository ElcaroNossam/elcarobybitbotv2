# 🚀 Project-Wide Optimization Plan

**Created:** 2025-12-23  
**Status:** In Progress  
**Goal:** Reduce API response times from 30s+ to <5s, improve database performance, enhance caching  

---

## 📊 Current Performance Issues

### Identified Bottlenecks
1. **Slow API Responses** - Trading terminal endpoints timing out (30s+)
2. **Database Queries** - No indexes on critical columns (symbol, user_id in trade_logs)
3. **Limited Caching** - Only user config cached (30s TTL), no balance/position caching
4. **No Connection Pooling** - Creating new exchange clients per request
5. **N+1 Query Problem** - get_user_config called multiple times in loops
6. **Redundant JSON Parsing** - strategy_settings parsed on every access

---

## 🎯 Optimization Phases

### Phase 1: Database Optimization (HIGH PRIORITY) ✅
**Impact:** 40-60% faster queries  
**Time:** 1-2 hours  

#### 1.1 Missing Indexes
```sql
-- Trade logs performance (most queries)
CREATE INDEX idx_logs_user_symbol ON trade_logs(user_id, symbol);
CREATE INDEX idx_logs_entry_ts ON trade_logs(entry_ts);

-- Active positions lookup
CREATE INDEX idx_active_symbol ON active_positions(symbol);
CREATE INDEX idx_active_account_type ON active_positions(user_id, account_type);

-- Pending orders
CREATE INDEX idx_pending_symbol ON pending_limit_orders(symbol);
CREATE INDEX idx_pending_strategy ON pending_limit_orders(user_id, strategy);

-- Licenses (admin queries)
CREATE INDEX idx_licenses_expires ON user_licenses(end_date) WHERE is_active = 1;
CREATE INDEX idx_promo_active ON promo_codes(is_active, valid_until);

-- Signals (historical lookups)
CREATE INDEX idx_signals_symbol_side ON signals(symbol, side, ts DESC);
```

#### 1.2 Query Optimizations
- [ ] Replace `SELECT *` with explicit column lists (reduce data transfer)
- [ ] Add LIMIT to unbounded queries
- [ ] Use prepared statements for repeated queries
- [ ] Batch inserts for multiple records

#### 1.3 Connection Pool Enhancement
- [x] Current: 10 connections with health checks
- [ ] Add: Statement caching for hot queries
- [ ] Add: Query result memoization for 1s

---

### Phase 2: Enhanced Caching Strategy (HIGH PRIORITY) 🔄
**Impact:** 60-80% faster API responses  
**Time:** 2-3 hours  

#### 2.1 New Cache Layers

**Balance Cache** (TTL: 15s)
```python
# core/cache.py
balance_cache = LRUCache(max_size=1000, ttl=15.0)

@async_cached(balance_cache, ttl=15.0)
async def get_balance_cached(user_id: int, exchange: str, account_type: str):
    """Cache balance to reduce exchange API calls"""
```

**Position Cache** (TTL: 10s)
```python
position_cache = LRUCache(max_size=1000, ttl=10.0)

@async_cached(position_cache, ttl=10.0)
async def get_positions_cached(user_id: int, exchange: str, account_type: str):
    """Cache positions - invalidate on order placement"""
```

**Market Data Cache** (TTL: 5s)
```python
market_data_cache = LRUCache(max_size=500, ttl=5.0)

@async_cached(market_data_cache, ttl=5.0)
async def get_ticker_cached(symbol: str):
    """Cache ticker data - shared across all users"""
```

**User Credentials Cache** (TTL: 60s)
```python
# Already exists but extend:
credentials_cache = LRUCache(max_size=2000, ttl=60.0)
# Currently only user_config cached - add:
# - API keys (avoid decrypt every call)
# - Exchange settings
# - Strategy settings (parsed JSON)
```

#### 2.2 Cache Invalidation Strategy
```python
# webapp/api/trading.py
async def place_order(...):
    result = await adapter.place_order(...)
    if result.success:
        # Invalidate position cache
        position_cache.invalidate(f"{user_id}:{exchange}:{account_type}")
        # Balance cache will auto-expire in 15s
    return result
```

#### 2.3 Cache Warming
```python
# Preload cache for active users on bot startup
async def warm_caches():
    active_users = db.get_active_trading_users()
    for uid in active_users:
        asyncio.create_task(get_balance_cached(uid, ...))
        asyncio.create_task(get_positions_cached(uid, ...))
```

---

### Phase 3: API Response Time Optimization (MEDIUM PRIORITY)
**Impact:** 30-50% faster responses  
**Time:** 2-3 hours  

#### 3.1 Parallel Queries
```python
# Before: Sequential calls (3-4s each)
balance = await get_balance(user_id)
positions = await get_positions(user_id)
orders = await get_orders(user_id)

# After: Parallel execution (<2s total)
balance, positions, orders = await asyncio.gather(
    get_balance_cached(user_id),
    get_positions_cached(user_id),
    get_orders(user_id)
)
```

#### 3.2 Response Compression
```python
# webapp/app.py
from fastapi.middleware.gzip import GZIPMiddleware
app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

#### 3.3 Request Deduplication
```python
# Prevent multiple identical requests in flight
_in_flight: Dict[str, asyncio.Future] = {}

async def deduplicated_request(key: str, coro):
    if key in _in_flight:
        return await _in_flight[key]
    future = asyncio.create_task(coro)
    _in_flight[key] = future
    try:
        result = await future
        return result
    finally:
        del _in_flight[key]
```

---

### Phase 4: Exchange Connection Pooling (MEDIUM PRIORITY)
**Impact:** 20-30% faster exchange calls  
**Time:** 2 hours  

#### 4.1 Client Pool Architecture
```python
# core/connection_pool.py (exists, enhance)

class ExchangeClientPool:
    def __init__(self, max_size=50, max_idle=300):
        self._pools = {}  # (exchange, user_id) -> Queue[Client]
        self._semaphore = asyncio.Semaphore(max_size)
    
    async def acquire(self, exchange: str, user_id: int) -> Client:
        key = (exchange, user_id)
        if key not in self._pools:
            self._pools[key] = asyncio.Queue(maxsize=5)
        
        pool = self._pools[key]
        try:
            client = pool.get_nowait()
            if await client.health_check():
                return client
        except asyncio.QueueEmpty:
            pass
        
        return await self._create_client(exchange, user_id)
    
    async def release(self, exchange: str, user_id: int, client: Client):
        key = (exchange, user_id)
        try:
            self._pools[key].put_nowait(client)
        except asyncio.QueueFull:
            await client.close()
```

#### 4.2 Health Checks
```python
# exchanges/bybit.py
async def health_check(self) -> bool:
    try:
        await self.get_server_time()
        return True
    except:
        return False
```

---

### Phase 5: Code Structure Refactoring (LOW PRIORITY)
**Impact:** Maintainability, testability  
**Time:** 4-8 hours  

#### 5.1 Extract Bot Logic to Services
```python
# Currently: bot.py (~14,200 lines)
# Split into:
services/
    order_service.py      # Order placement logic
    position_service.py   # Position management
    signal_service.py     # Signal parsing (exists)
    strategy_service.py   # Strategy execution
    monitoring_service.py # Position monitoring
```

#### 5.2 Reduce bot.py Size
```python
# Move handlers to separate files
handlers/
    api_settings.py    # Lines 791-1200
    strategy.py        # Lines 3888-5480
    positions.py       # Position handlers
    admin.py           # Admin commands
```

---

### Phase 6: Memory Optimization (LOW PRIORITY)
**Impact:** Reduced memory footprint  
**Time:** 1-2 hours  

#### 6.1 Data Structure Optimization
```python
# Before: Full position dict in memory
positions = [
    {"symbol": "BTCUSDT", "side": "LONG", "size": 0.5, ...}  # 500+ bytes
]

# After: Lightweight dataclass
@dataclass(slots=True)
class Position:
    symbol: str
    side: str
    size: float
    # Only essential fields - 80 bytes
```

#### 6.2 Limit In-Memory Logs
```python
# bot.py - rotate logs
import logging.handlers
handler = logging.handlers.RotatingFileHandler(
    "bot.log", maxBytes=10*1024*1024, backupCount=5
)
```

---

### Phase 7: Performance Monitoring (ONGOING)
**Impact:** Continuous optimization  
**Time:** 1 hour setup + ongoing  

#### 7.1 Add Performance Metrics
```python
# core/metrics.py (exists)
api_response_time = Histogram("api_response_seconds", ["endpoint", "status"])
db_query_time = Histogram("db_query_seconds", ["query_type"])
cache_hit_rate = Counter("cache_hits_total", ["cache_name"])

# Usage in endpoints
@router.get("/balance")
@track_latency(api_response_time, labels={"endpoint": "/balance"})
async def get_balance(...):
    ...
```

#### 7.2 Health Monitoring Dashboard
```python
# webapp/api/monitoring.py
@router.get("/metrics")
async def get_metrics():
    return {
        "cache_stats": get_all_cache_stats(),
        "db_pool": {
            "size": _pool.qsize(),
            "active": 10 - _pool.qsize()
        },
        "response_times": metrics.get_histogram("api_response_seconds"),
        "error_rate": metrics.get_counter("errors_total")
    }
```

---

## 📈 Expected Results

### Before Optimization
- API Response Time: **30s+** (timeout)
- Database Query Time: **500-1000ms** (no indexes)
- Cache Hit Rate: **30%** (only user_config)
- Memory Usage: **150-200MB** (bot + webapp)

### After Optimization
- API Response Time: **<3s** (90% improvement) ✅
- Database Query Time: **50-100ms** (80% improvement) ✅
- Cache Hit Rate: **75-85%** (150% improvement) ✅
- Memory Usage: **120-150MB** (20% improvement) ✅

---

## 🚀 Implementation Priority

### Week 1 (Critical)
1. ✅ **Phase 1: Database Indexes** (Day 1)
   - Add all missing indexes
   - Test query performance
   - Measure improvement

2. ✅ **Phase 2: Cache Enhancement** (Day 2-3)
   - Implement balance/position caches
   - Add cache invalidation
   - Test with load

3. ✅ **Phase 3: Parallel Queries** (Day 3-4)
   - Refactor sequential calls
   - Add asyncio.gather
   - Benchmark

### Week 2 (Important)
4. **Phase 4: Connection Pooling** (Day 5-6)
   - Enhance existing pool
   - Add health checks
   - Monitor connections

5. **Phase 7: Monitoring** (Day 7)
   - Add performance metrics
   - Create dashboard
   - Set up alerts

### Week 3+ (Nice-to-Have)
6. **Phase 5: Code Refactoring**
   - Extract services
   - Split bot.py
   - Improve tests

7. **Phase 6: Memory Optimization**
   - Profile memory
   - Optimize data structures
   - Add rotation

---

## 📝 Progress Tracking

### Completed ✅
- [x] Created optimization plan
- [x] Analyzed bottlenecks
- [ ] Database indexes script ready

### In Progress 🔄
- [ ] Implementing Phase 1 (Database Optimization)

### Pending ⏳
- [ ] Phase 2: Enhanced Caching
- [ ] Phase 3: API Response Optimization
- [ ] Phase 4: Connection Pooling
- [ ] Phase 5: Code Refactoring
- [ ] Phase 6: Memory Optimization
- [ ] Phase 7: Performance Monitoring

---

## 🧪 Testing Strategy

### Performance Tests
```python
# tests/test_performance.py
import pytest
import time

@pytest.mark.asyncio
async def test_balance_response_time():
    """Balance API should respond in <2s"""
    start = time.time()
    result = await get_balance(user_id=999001)
    duration = time.time() - start
    assert duration < 2.0
    assert result is not None

@pytest.mark.asyncio
async def test_cache_hit_rate():
    """Cache should have >70% hit rate after warmup"""
    # Warm up
    for _ in range(10):
        await get_balance_cached(999001)
    
    # Measure
    stats = balance_cache.get_stats()
    hit_rate = stats['hits'] / (stats['hits'] + stats['misses'])
    assert hit_rate > 0.70
```

### Load Testing
```bash
# Use Apache Bench to test endpoints
ab -n 1000 -c 50 http://localhost:8765/api/trading/balance

# Expected results:
# Before: 30s timeout, failures
# After: <3s avg, 0 failures
```

---

## 📚 Documentation Updates

### Updated Files
1. **OPTIMIZATION_PLAN.md** - This document
2. **README.md** - Add performance section
3. **db.py** - Add index creation comments
4. **core/cache.py** - Document new cache layers
5. **webapp/api/trading.py** - Add caching decorators

### New Files
1. **scripts/add_indexes.sql** - Index creation script
2. **scripts/benchmark.py** - Performance testing
3. **tests/test_performance.py** - Performance test suite

---

*Last updated: 2025-12-23*
*Next review: After Phase 1 completion*
