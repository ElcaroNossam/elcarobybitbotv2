# Enliko Trading Platform - Scalable Architecture for 10K+ Users
# ===============================================================
# Version: 1.0.0 | Created: January 15, 2026
# ===============================================================

## 📊 Масштабирование: Текущее vs Целевое

| Метрика | Текущее | Целевое (10K+) |
|---------|---------|----------------|
| Пользователей | 5 | 10,000+ |
| Позиций одновременно | 50 | 100,000+ |
| API запросов/сек | 10 | 5,000+ |
| Сигналов/день | 100 | 50,000+ |
| Latency | 1-5 сек | <500ms |
| Доступность | 95% | 99.9% |

---

## 🏗️ ЦЕЛЕВАЯ АРХИТЕКТУРА

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LOAD BALANCER (nginx/HAProxy)                      │
│                                    │                                         │
├────────────────────────────────────┼────────────────────────────────────────┤
│                                    ▼                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  API Server  │  │  API Server  │  │  API Server  │  │  API Server  │    │
│  │   (FastAPI)  │  │   (FastAPI)  │  │   (FastAPI)  │  │   (FastAPI)  │    │
│  │   Port 8765  │  │   Port 8766  │  │   Port 8767  │  │   Port 8768  │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │             │
├─────────┴─────────────────┴─────────────────┴─────────────────┴─────────────┤
│                                    │                                         │
│                          ┌─────────▼─────────┐                              │
│                          │   MESSAGE BROKER   │                              │
│                          │  (Redis Streams /  │                              │
│                          │    RabbitMQ)       │                              │
│                          └─────────┬─────────┘                              │
│                                    │                                         │
├────────────────────────────────────┼────────────────────────────────────────┤
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    CELERY WORKER POOL                                │   │
│  │                                                                      │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │  Signal    │  │  Position  │  │  Position  │  │  Position  │    │   │
│  │  │  Processor │  │  Monitor   │  │  Monitor   │  │  Monitor   │    │   │
│  │  │            │  │  Shard 1   │  │  Shard 2   │  │  Shard N   │    │   │
│  │  │ (signals)  │  │ (users 1-  │  │(users 1K-  │  │(users NK-  │    │   │
│  │  │            │  │    1000)   │  │   2000)    │  │  10000)    │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘    │   │
│  │                                                                      │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                    │   │
│  │  │   Trade    │  │    DCA     │  │   ATR      │                    │   │
│  │  │  Executor  │  │  Processor │  │  Trailing  │                    │   │
│  │  └────────────┘  └────────────┘  └────────────┘                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
├────────────────────────────────────┼────────────────────────────────────────┤
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         DATA LAYER                                   │   │
│  │                                                                      │   │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │   │
│  │  │   PostgreSQL     │  │      Redis       │  │   TimescaleDB    │  │   │
│  │  │   (Primary DB)   │  │   (Cache/Queue)  │  │  (Time Series)   │  │   │
│  │  │                  │  │                  │  │                  │  │   │
│  │  │  • users         │  │  • session cache │  │  • price_history │  │   │
│  │  │  • positions     │  │  • rate limiting │  │  • trade_metrics │  │   │
│  │  │  • trade_logs    │  │  • user_cache    │  │  • pnl_timeseries│  │   │
│  │  │  • signals       │  │  • price_cache   │  │                  │  │   │
│  │  │  • licenses      │  │  • pub/sub       │  │                  │  │   │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                         TELEGRAM BOT CLUSTER                                 │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Bot Pod 1  │  │   Bot Pod 2  │  │   Bot Pod 3  │  │   Bot Pod N  │   │
│  │  (Webhook)   │  │  (Webhook)   │  │  (Webhook)   │  │  (Webhook)   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 КЛЮЧЕВЫЕ КОМПОНЕНТЫ

### 1. PostgreSQL (Primary Database)

**Почему не SQLite:**
- SQLite: 1 writer at a time → bottleneck при 10K юзерах
- PostgreSQL: Connection pooling, concurrent writes, ACID

**Схема миграции:**
```sql
-- Users partitioned by user_id range
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    -- ... all existing fields
) PARTITION BY RANGE (user_id);

CREATE TABLE users_0_10k PARTITION OF users 
    FOR VALUES FROM (0) TO (10000);
CREATE TABLE users_10k_20k PARTITION OF users 
    FOR VALUES FROM (10000) TO (20000);

-- Indexes for hot queries
CREATE INDEX idx_users_active ON users(is_allowed) WHERE is_allowed = 1;
CREATE INDEX idx_positions_user_symbol ON active_positions(user_id, symbol);
CREATE INDEX idx_trade_logs_user_ts ON trade_logs(user_id, ts DESC);
```

### 2. Redis (Cache + Message Broker)

```python
# redis_client.py
import redis.asyncio as redis
from typing import Optional, Any
import json

class RedisCache:
    def __init__(self, url: str = "redis://localhost:6379"):
        self.pool = redis.ConnectionPool.from_url(url, max_connections=100)
        self.client = redis.Redis(connection_pool=self.pool)
    
    async def get_user_cache(self, user_id: int) -> Optional[dict]:
        key = f"user:{user_id}"
        data = await self.client.get(key)
        return json.loads(data) if data else None
    
    async def set_user_cache(self, user_id: int, data: dict, ttl: int = 30):
        key = f"user:{user_id}"
        await self.client.setex(key, ttl, json.dumps(data))
    
    async def rate_limit(self, user_id: int, limit: int = 60, window: int = 60) -> bool:
        """Distributed rate limiting"""
        key = f"ratelimit:{user_id}"
        current = await self.client.incr(key)
        if current == 1:
            await self.client.expire(key, window)
        return current <= limit
    
    async def publish_signal(self, signal: dict):
        """Publish signal to all workers"""
        await self.client.publish("signals", json.dumps(signal))
    
    async def get_price(self, symbol: str) -> Optional[float]:
        """Get cached price (updated by WebSocket worker)"""
        price = await self.client.hget("prices", symbol)
        return float(price) if price else None
```

### 3. Celery Task Queue

```python
# tasks/celery_app.py
from celery import Celery

app = Celery(
    'elcaro',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1',
    include=['tasks.signals', 'tasks.positions', 'tasks.trades']
)

app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_concurrency=8,
    # Task routing
    task_routes={
        'tasks.signals.*': {'queue': 'signals'},
        'tasks.positions.*': {'queue': 'positions'},
        'tasks.trades.*': {'queue': 'trades'},
    }
)
```

```python
# tasks/positions.py
from celery import shared_task
from typing import List
import asyncio

@shared_task(bind=True, max_retries=3)
def monitor_user_positions(self, user_ids: List[int]):
    """Monitor positions for a shard of users"""
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_async_monitor(user_ids))
    except Exception as exc:
        self.retry(exc=exc, countdown=5)

async def _async_monitor(user_ids: List[int]):
    """Async position monitoring for user shard"""
    from bot import monitor_positions_for_users
    await monitor_positions_for_users(user_ids)
```

### 4. User Sharding Strategy

```python
# sharding/user_shards.py
import hashlib
from typing import List, Tuple

SHARD_COUNT = 10  # 10 shards = 1000 users per shard for 10K users

def get_user_shard(user_id: int) -> int:
    """Consistent hashing for user → shard mapping"""
    return user_id % SHARD_COUNT

def get_shard_users(shard_id: int, all_users: List[int]) -> List[int]:
    """Get all users belonging to a shard"""
    return [uid for uid in all_users if get_user_shard(uid) == shard_id]

def distribute_monitoring_tasks():
    """Distribute position monitoring across workers"""
    from db import get_active_trading_users
    from tasks.positions import monitor_user_positions
    
    users = get_active_trading_users()
    
    # Group users by shard
    shards = {}
    for uid in users:
        shard = get_user_shard(uid)
        if shard not in shards:
            shards[shard] = []
        shards[shard].append(uid)
    
    # Dispatch tasks to Celery
    for shard_id, shard_users in shards.items():
        monitor_user_positions.apply_async(
            args=[shard_users],
            queue=f'positions_shard_{shard_id}'
        )
```

### 5. WebSocket Price Feed

```python
# services/price_feed.py
import asyncio
import websockets
import json
from typing import Dict, Set
from redis_client import RedisCache

class PriceFeedService:
    """WebSocket price feed with Redis broadcasting"""
    
    def __init__(self):
        self.redis = RedisCache()
        self.subscribed_symbols: Set[str] = set()
        self.prices: Dict[str, float] = {}
    
    async def connect_bybit_ws(self):
        """Connect to Bybit WebSocket for real-time prices"""
        uri = "wss://stream.bybit.com/v5/public/linear"
        
        async with websockets.connect(uri) as ws:
            # Subscribe to tickers
            symbols = await self._get_active_symbols()
            subscribe_msg = {
                "op": "subscribe",
                "args": [f"tickers.{s}" for s in symbols]
            }
            await ws.send(json.dumps(subscribe_msg))
            
            async for message in ws:
                data = json.loads(message)
                if data.get("topic", "").startswith("tickers."):
                    await self._handle_ticker(data)
    
    async def _handle_ticker(self, data: dict):
        """Process ticker update and broadcast to Redis"""
        topic = data.get("topic", "")
        symbol = topic.replace("tickers.", "")
        ticker_data = data.get("data", {})
        
        price = float(ticker_data.get("lastPrice", 0))
        if price > 0:
            self.prices[symbol] = price
            
            # Update Redis (all workers see this instantly)
            await self.redis.client.hset("prices", symbol, str(price))
            
            # Publish price update event
            await self.redis.client.publish(
                "price_updates",
                json.dumps({"symbol": symbol, "price": price})
            )
    
    async def _get_active_symbols(self) -> Set[str]:
        """Get all symbols with open positions"""
        from db_async import get_all_active_symbols
        return await get_all_active_symbols()
```

---

## 📦 DEPLOYMENT ARCHITECTURE

### Docker Compose (Development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: elcaro
      POSTGRES_USER: elcaro
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  api:
    build: .
    command: uvicorn webapp.app:app --host 0.0.0.0 --port 8765 --workers 4
    environment:
      - DATABASE_URL=postgresql://elcaro:${DB_PASSWORD}@postgres:5432/elcaro
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    ports:
      - "8765:8765"

  celery_signals:
    build: .
    command: celery -A tasks.celery_app worker -Q signals -c 4 --loglevel=info
    environment:
      - DATABASE_URL=postgresql://elcaro:${DB_PASSWORD}@postgres:5432/elcaro
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  celery_positions:
    build: .
    command: celery -A tasks.celery_app worker -Q positions -c 8 --loglevel=info
    environment:
      - DATABASE_URL=postgresql://elcaro:${DB_PASSWORD}@postgres:5432/elcaro
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    deploy:
      replicas: 10  # 10 workers for 10 shards

  price_feed:
    build: .
    command: python services/price_feed.py
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  telegram_bot:
    build: .
    command: python bot.py
    environment:
      - DATABASE_URL=postgresql://elcaro:${DB_PASSWORD}@postgres:5432/elcaro
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
      - api

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes (Production)

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: elcaro-api
spec:
  replicas: 4
  selector:
    matchLabels:
      app: elcaro-api
  template:
    spec:
      containers:
      - name: api
        image: elcaro/api:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: elcaro-secrets
              key: database-url
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: elcaro-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: elcaro-api
  minReplicas: 4
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## 🔄 MIGRATION PLAN

### Phase 1: Database Migration (Week 1-2)
1. ✅ Set up PostgreSQL
2. ✅ Create async db layer (`db_async.py`)
3. ✅ Migrate schema with data
4. ✅ Switch bot to PostgreSQL
5. ✅ Keep SQLite as backup

### Phase 2: Redis Integration (Week 2-3)
1. ✅ Deploy Redis
2. ✅ Implement `RedisCache` class
3. ✅ Replace in-memory caches
4. ✅ Add distributed rate limiting
5. ✅ Implement pub/sub for signals

### Phase 3: Celery Workers (Week 3-4)
1. ✅ Set up Celery with Redis broker
2. ✅ Extract signal processing to tasks
3. ✅ Extract position monitoring to tasks
4. ✅ Implement user sharding
5. ✅ Test with load

### Phase 4: WebSocket Price Feeds (Week 4-5)
1. ✅ Create PriceFeedService
2. ✅ Connect to Bybit/HL WebSockets
3. ✅ Broadcast prices via Redis pub/sub
4. ✅ Update ATR monitoring to use cached prices
5. ✅ Remove polling

### Phase 5: Horizontal Scaling (Week 5-6)
1. ✅ Dockerize all components
2. ✅ Set up Kubernetes cluster
3. ✅ Configure auto-scaling
4. ✅ Load testing (10K simulated users)
5. ✅ Production deployment

---

## 📈 PERFORMANCE TARGETS

| Metric | Current | Target | How |
|--------|---------|--------|-----|
| Position monitoring latency | 25s loop | <5s | Sharded workers + WebSocket |
| Signal processing | Sequential | <100ms | Celery parallel workers |
| Balance fetch | 0.4s | <100ms | Redis cache + connection pool |
| DB write throughput | 100/s | 10,000/s | PostgreSQL + connection pool |
| Concurrent users | 5 | 10,000+ | Horizontal scaling |

---

## 🛡️ RELIABILITY

### Circuit Breaker Pattern
```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=30)
async def call_bybit_api(endpoint: str, params: dict):
    """API call with circuit breaker"""
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint, params=params) as resp:
            return await resp.json()
```

### Health Checks
```python
@app.get("/health")
async def health_check():
    checks = await asyncio.gather(
        check_postgres(),
        check_redis(),
        check_celery(),
        return_exceptions=True
    )
    
    status = "healthy" if all(c is True for c in checks) else "degraded"
    return {"status": status, "checks": checks}
```

### Graceful Degradation
- If Redis down → fallback to in-memory cache
- If Celery down → fallback to async monitoring
- If PostgreSQL down → read from SQLite replica

---

*Document created: January 15, 2026*
*Target: 10,000+ concurrent users*
*Timeline: 6 weeks to production*
