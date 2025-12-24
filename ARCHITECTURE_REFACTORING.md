# ElCaro Trading Bot - Архитектурный Рефакторинг

**Дата:** 23 декабря 2025  
**Статус:** В разработке  
**Цель:** Интеграция и гармонизация всех модулей проекта

---

## 🔍 Текущие Проблемы

### 1. Дублирование Функционала

#### 1.1 Размещение Ордеров (5 реализаций!)
```python
# 1. bot.py:3519 - Прямой вызов Bybit API
async def place_order(user_id, symbol, side, orderType, qty, price, account_type):
    # 250+ строк кода с ручной обработкой

# 2. exchange_router.py:16 - Роутинг Bybit/HyperLiquid
async def place_order_universal(user_id, symbol, side, orderType, qty, ...):
    if exchange == "hyperliquid":
        adapter = HLAdapter(...)
    else:
        return await bybit_place_order_func(...)

# 3. services/trading_service.py:66 - Business logic layer
class TradingService:
    async def open_position(self, user_id, request, adapter):
        # Использует ExchangeService

# 4. services/exchange_service.py:234 - Exchange abstraction
class BybitAdapter:
    async def place_order(self, symbol, side, size, ...):
        # Оборачивает exchanges/bybit.py

# 5. exchanges/bybit.py:290 - Низкоуровневый API wrapper
class BybitExchange:
    async def place_order(self, symbol, side, size, ...):
        # Прямой HTTP запрос к Bybit
```

**Проблема:** Каждая реализация имеет свою логику обработки ошибок, кэширования, логирования. При добавлении новой биржи нужно обновлять 5 мест!

#### 1.2 Получение Позиций (4 реализации)
- `bot.py:6212` - `get_positions_bybit_single()`
- `exchange_router.py:93` - `fetch_positions_universal()`
- `services/exchange_service.py:169` - `BybitAdapter.get_positions()`
- `exchanges/bybit.py:220` - `BybitExchange.get_positions()`

#### 1.3 Получение Баланса (4 реализации)
- `bot.py` → прямой вызов `/v5/account/wallet-balance`
- `exchange_router.py:161` - `get_balance_universal()`
- `services/exchange_service.py:130` - `BybitAdapter.get_balance()`
- `exchanges/bybit.py:210` - `BybitExchange.get_balance()`

### 2. Несогласованность Форматов Данных

#### 2.1 Модель Позиции (3 разных схемы)
```python
# 1. exchanges/base.py:45
@dataclass
class Position:
    symbol: str
    side: PositionSide
    size: float
    entry_price: float
    unrealized_pnl: float
    leverage: int

# 2. bot.py - словарь Bybit API
position = {
    "symbol": "BTCUSDT",
    "side": "Buy",  # строка!
    "size": "0.1",
    "avgPrice": "45000",  # другое имя поля!
    "unrealisedPnl": "100"  # другое имя!
}

# 3. services/exchange_service.py - промежуточный формат
{
    "symbol": str,
    "side": str,
    "size": float,  # уже преобразовано в float
    "entry_price": float,  # переименовано
    "pnl": float  # переименовано
}
```

**Проблема:** Нужно 3 раза преобразовывать один и тот же объект!

#### 2.2 Стороны Ордера (3 разных формата)
- `bot.py`: `"Buy"` / `"Sell"` (строки)
- `exchanges/base.py`: `OrderSide.BUY` / `OrderSide.SELL` (enum)
- `services/exchange_service.py`: `"LONG"` / `"SHORT"` (строки)

### 3. Нарушение Архитектуры

#### 3.1 bot.py Импортирует ВСЁ
```python
# bot.py строки 1-100
import db  # ❌ Прямой доступ к БД
from hl_adapter import HLAdapter  # ❌ Прямой доступ к API клиенту
from exchange_router import place_order_universal  # ❌ Bypass services

# Правильно было бы:
from services import trading_service, exchange_service
```

#### 3.2 WebApp API Bypass Services
```python
# webapp/api/trading.py:19
import db  # ❌ Прямой доступ к БД

# webapp/api/admin.py:14
import db  # ❌ Прямой доступ к БД

# webapp/api/auth.py:20
import db  # ❌ Прямой доступ к БД
```

**14 файлов в webapp/** импортируют `db` напрямую вместо использования `services`!

#### 3.3 Двойная База Данных
```python
# db.py - основная БД
- users (50+ колонок)
- active_positions
- trade_logs
- signals

# db_elcaro.py - блокчейн БД
- elcaro_wallets
- elcaro_balances
- elcaro_transactions
- elcaro_mining_stats
```

**Проблема:** `user_id` не связан foreign key, нет транзакций между базами, дублирование балансов!

### 4. Неиспользуемые Модули

#### 4.1 services/ Слой Игнорируется
```bash
# bot.py имеет НОЛЬ импортов из services/
grep "from services" bot.py
# Пусто!

# Все services созданы но не используются:
- services/trading_service.py (354 строки)
- services/exchange_service.py (726 строк)
- services/signal_service.py (389 строк)
- services/user_service.py (172 строки)
```

#### 4.2 core/exchange_client.py vs exchange_router.py
Оба делают одно и то же - роутинг между биржами!

```python
# core/exchange_client.py:369
class UnifiedExchangeClient:
    async def place_order(...)
    async def get_positions(...)
    
# exchange_router.py:16
async def place_order_universal(...)
async def fetch_positions_universal(...)
```

---

## ✅ Целевая Архитектура

### Иерархия Зависимостей
```
┌─────────────────────────────────────────────────────────────┐
│                          bot.py                              │
│              (Telegram UI + Signal Parsing)                  │
│                      ~2000 строк                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                       services/                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │   trading    │ │   signal     │ │    user      │        │
│  │   _service   │ │   _service   │ │   _service   │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│         Business Logic Layer                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                         core/                                │
│  ┌────────────┐ ┌────────────┐ ┌─────────────┐            │
│  │   cache    │ │   rate     │ │  exchange   │            │
│  │            │ │  _limiter  │ │  _client    │            │
│  └────────────┘ └────────────┘ └─────────────┘            │
│      Infrastructure: Pool, Cache, Metrics                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      exchanges/                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │    bybit     │ │  hyperliquid │ │   binance    │        │
│  │   Exchange   │ │   Exchange   │ │   Exchange   │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│         Exchange-Specific API Wrappers                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
                  External APIs
           (Bybit, HyperLiquid, Binance...)
```

### Принципы

1. **Единая Точка Входа**: `bot.py` только через `services/`
2. **Единый Формат Данных**: Используем `exchanges/base.py` dataclass везде
3. **Нет Прямого Доступа**: WebApp API → `services/` → `core/` → `exchanges/`
4. **Одна База**: Merge `db_elcaro.py` → `db.py`
5. **Роутинг в Core**: `core/exchange_client.py` - единственный роутер

---

## 🛠️ План Рефакторинга

### Phase 1: Стандартизация Моделей Данных (1-2 дня)

#### 1.1 Единые Dataclasses
**Файл:** `models/__init__.py`
```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Literal

class OrderSide(str, Enum):
    BUY = "Buy"
    SELL = "Sell"

class PositionSide(str, Enum):
    LONG = "Buy"
    SHORT = "Sell"

class OrderType(str, Enum):
    MARKET = "Market"
    LIMIT = "Limit"

@dataclass
class Position:
    symbol: str
    side: PositionSide
    size: float
    entry_price: float
    mark_price: float
    unrealized_pnl: float
    leverage: int
    margin: float
    liquidation_price: Optional[float] = None
    
    @classmethod
    def from_bybit(cls, data: dict) -> 'Position':
        """Преобразование из Bybit API формата"""
        return cls(
            symbol=data['symbol'],
            side=PositionSide(data['side']),
            size=float(data['size']),
            entry_price=float(data['avgPrice']),
            mark_price=float(data['markPrice']),
            unrealized_pnl=float(data['unrealisedPnl']),
            leverage=int(data['leverage']),
            margin=float(data['positionIM']),
            liquidation_price=float(data.get('liqPrice', 0))
        )

@dataclass
class Order:
    order_id: str
    symbol: str
    side: OrderSide
    type: OrderType
    size: float
    price: Optional[float]
    status: str
    created_at: int
    
@dataclass
class Balance:
    total: float
    available: float
    margin_used: float
    currency: str = "USDT"
```

**Задачи:**
- [ ] Создать `models/__init__.py` с унифицированными моделями
- [ ] Добавить `from_bybit()`, `from_hyperliquid()` методы
- [ ] Обновить `exchanges/base.py` использовать эти модели
- [ ] Добавить валидацию через pydantic (опционально)

#### 1.2 Обновить exchanges/
```python
# exchanges/bybit.py
from models import Position, Order, Balance, OrderSide, OrderType

class BybitExchange(BaseExchange):
    async def get_positions(self) -> list[Position]:
        resp = await self._request('GET', '/v5/position/list')
        return [Position.from_bybit(p) for p in resp['result']['list']]
```

**Задачи:**
- [ ] Обновить `exchanges/bybit.py` возвращать `Position` вместо dict
- [ ] Обновить `exchanges/hyperliquid.py` возвращать `Position`
- [ ] Обновить `hl_adapter.py` использовать единые модели

### Phase 2: Unified Exchange Client (2-3 дня)

#### 2.1 Усилить core/exchange_client.py
**Файл:** `core/exchange_client.py`

```python
from exchanges import BybitExchange, HyperLiquidExchange
from models import Position, Order, Balance
from typing import Protocol

class ExchangeProtocol(Protocol):
    async def place_order(...) -> Order: ...
    async def get_positions(...) -> list[Position]: ...
    async def get_balance(...) -> Balance: ...

class UnifiedExchangeClient:
    """
    Единый клиент для всех бирж с:
    - Connection pooling
    - Rate limiting
    - Caching
    - Retry logic
    - Metrics
    """
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self._exchange: Optional[ExchangeProtocol] = None
        
    async def _get_exchange(self) -> ExchangeProtocol:
        """Получить exchange client из pool или создать новый"""
        if self._exchange:
            return self._exchange
            
        # Get from connection pool
        from core import get_cached_client, bybit_limiter, hl_limiter
        exchange_type = db.get_exchange_type(self.user_id)
        
        if exchange_type == "hyperliquid":
            creds = db.get_hl_credentials(self.user_id)
            self._exchange = HyperLiquidExchange(
                private_key=creds['hl_private_key'],
                testnet=creds.get('hl_testnet', False)
            )
            self._limiter = hl_limiter
        else:
            creds = db.get_user_credentials(self.user_id, 'real')
            self._exchange = BybitExchange(
                api_key=creds['api_key'],
                api_secret=creds['api_secret'],
                testnet=False
            )
            self._limiter = bybit_limiter
            
        await self._exchange.initialize()
        return self._exchange
    
    @track_latency('exchange.place_order')
    @async_cached(ttl=0)  # No cache for orders
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        size: float,
        order_type: OrderType = OrderType.MARKET,
        price: Optional[float] = None,
        leverage: Optional[int] = None
    ) -> Order:
        """Единый метод размещения ордера"""
        await self._limiter.acquire(self.user_id, 'order')
        
        exchange = await self._get_exchange()
        
        # Set leverage if needed
        if leverage:
            await self.set_leverage(symbol, leverage)
        
        return await exchange.place_order(
            symbol=symbol,
            side=side,
            size=size,
            order_type=order_type,
            price=price
        )
    
    @track_latency('exchange.get_positions')
    @async_cached(balance_cache, ttl=5)
    async def get_positions(self, symbol: Optional[str] = None) -> list[Position]:
        """Единый метод получения позиций"""
        await self._limiter.acquire(self.user_id, 'position')
        
        exchange = await self._get_exchange()
        positions = await exchange.get_positions()
        
        if symbol:
            positions = [p for p in positions if p.symbol == symbol]
        
        return positions
```

**Задачи:**
- [ ] Удалить `exchange_router.py` (функционал → `core/exchange_client.py`)
- [ ] Добавить connection pooling в `UnifiedExchangeClient`
- [ ] Интегрировать rate limiting из `core/rate_limiter.py`
- [ ] Добавить caching из `core/cache.py`
- [ ] Добавить metrics tracking из `core/metrics.py`

#### 2.2 Создать Factory
```python
# core/__init__.py
from .exchange_client import UnifiedExchangeClient

def get_exchange_client(user_id: int) -> UnifiedExchangeClient:
    """Factory для создания exchange client"""
    return UnifiedExchangeClient(user_id)
```

### Phase 3: Обновить services/ (3-4 дня)

#### 3.1 Упростить TradingService
**Файл:** `services/trading_service.py`

```python
from core import get_exchange_client
from models import Position, Order, OrderSide, OrderType
import db

class TradingService:
    async def open_position(
        self,
        user_id: int,
        symbol: str,
        side: OrderSide,
        size_percent: float,
        leverage: int = 10,
        take_profit_percent: Optional[float] = None,
        stop_loss_percent: Optional[float] = None
    ) -> Order:
        """Открыть позицию"""
        
        # 1. Get exchange client
        client = get_exchange_client(user_id)
        
        # 2. Get balance
        balance = await client.get_balance()
        
        # 3. Calculate size
        size = self._calculate_position_size(
            balance.available, 
            size_percent,
            leverage
        )
        
        # 4. Place order
        order = await client.place_order(
            symbol=symbol,
            side=side,
            size=size,
            leverage=leverage
        )
        
        # 5. Set TP/SL if needed
        if take_profit_percent:
            await self._set_take_profit(client, order, take_profit_percent)
        
        if stop_loss_percent:
            await self._set_stop_loss(client, order, stop_loss_percent)
        
        # 6. Save to DB
        db.add_active_position(
            user_id=user_id,
            symbol=order.symbol,
            side=order.side.value,
            entry=order.price,
            qty=order.size,
            leverage=leverage,
            strategy='manual'
        )
        
        return order
```

**Задачи:**
- [ ] Переписать `TradingService` использовать `UnifiedExchangeClient`
- [ ] Удалить `ExchangeService.BybitAdapter` (дубликат)
- [ ] Переписать `SignalService` использовать `TradingService`

### Phase 4: Мигрировать bot.py (5-7 дней) ⚠️ **Критично**

#### 4.1 Убрать Прямые API Вызовы
**Было (bot.py:3519):**
```python
async def place_order(user_id, symbol, side, orderType, qty, price, account_type):
    # 250+ строк прямых HTTP запросов к Bybit
    url = "https://api.bybit.com/v5/order/create"
    params = {...}
    signature = generate_signature(params)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=params) as resp:
            ...
```

**Стало:**
```python
from services import trading_service
from models import OrderSide, OrderType

async def place_order(user_id, symbol, side, orderType, qty, price, account_type):
    # Всё делегируем в trading_service
    order = await trading_service.open_position(
        user_id=user_id,
        symbol=symbol,
        side=OrderSide(side),
        size_percent=None,  # Fixed size
        leverage=db.get_user_config(user_id).get('leverage', 10)
    )
    return order
```

#### 4.2 Обработка Сигналов
**Файл:** `bot.py:8680-9500` (signal handlers)

```python
# Было
async def handle_scryptomera_signal(msg_text, channel_id):
    # 200+ строк парсинга и прямых API вызовов
    users = db.get_subscribed_users()
    for uid in users:
        if not db.get_user_config(uid).get('trade_scryptomera'):
            continue
        # Прямой вызов place_order
        await place_order(uid, symbol, side, ...)

# Стало
from services import signal_service, trading_service

async def handle_signal(msg_text, channel_id):
    # 1. Parse signal
    signal = signal_service.parse(msg_text, channel_id)
    if not signal:
        return
    
    # 2. Get subscribed users
    users = signal_service.get_subscribed_users(signal.source)
    
    # 3. Execute for each user
    for uid in users:
        try:
            await trading_service.execute_signal(uid, signal)
        except Exception as e:
            logger.error(f"Failed to execute signal for {uid}: {e}")
```

**Задачи:**
- [ ] Создать `trading_service.execute_signal()` метод
- [ ] Переписать signal handlers использовать `signal_service`
- [ ] Удалить дублированную логику парсинга из `bot.py`
- [ ] Удалить прямые вызовы `place_order()` из signal handlers

#### 4.3 Telegram Handlers
```python
# bot.py:791-1200 (API settings handlers)
@log_calls
@require_access
async def cmd_api_demo(update, ctx):
    t = ctx.t
    uid = update.effective_user.id
    
    # Было: прямой db.set_user_field
    db.set_user_field(uid, 'demo_api_key', api_key)
    
    # Стало: через user_service
    from services import user_service
    await user_service.set_credentials(
        uid, 
        exchange='bybit',
        mode='demo',
        api_key=api_key,
        api_secret=api_secret
    )
```

**Задачи:**
- [ ] Обновить все команды использовать `user_service`
- [ ] Обновить position handlers использовать `trading_service`
- [ ] Обновить stats commands использовать `license_service`

### Phase 5: WebApp Рефакторинг (3-4 дня)

#### 5.1 Убрать Прямые db Импорты
**Было (webapp/api/trading.py):**
```python
import db

@router.get("/positions")
async def get_positions(user_id: int):
    positions = db.get_active_positions(user_id)
    return positions
```

**Стало:**
```python
from services import trading_service

@router.get("/positions")
async def get_positions(user_id: int):
    positions = await trading_service.get_positions(user_id)
    return [p.dict() for p in positions]
```

**Задачи:**
- [ ] Обновить `webapp/api/trading.py` → `trading_service`
- [ ] Обновить `webapp/api/admin.py` → `user_service`, `license_service`
- [ ] Обновить `webapp/api/auth.py` → `user_service`
- [ ] Обновить `webapp/api/users.py` → `user_service`
- [ ] Обновить `webapp/api/stats.py` → `trading_service`

### Phase 6: Консолидация БД (2-3 дня)

#### 6.1 Merge db_elcaro.py → db.py
```sql
-- Добавить в db.py init_db()

-- ELCaro Blockchain tables
CREATE TABLE IF NOT EXISTS elcaro_wallets (
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id),
    address TEXT NOT NULL UNIQUE,
    private_key_encrypted TEXT NOT NULL,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS elcaro_balances (
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id),
    elc_balance REAL NOT NULL DEFAULT 0,
    usdt_balance REAL NOT NULL DEFAULT 0,
    locked_balance REAL NOT NULL DEFAULT 0,
    last_updated INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS elcaro_transactions (
    tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    tx_hash TEXT NOT NULL UNIQUE,
    tx_type TEXT NOT NULL, -- 'mining', 'reward', 'trade', 'transfer'
    amount REAL NOT NULL,
    currency TEXT NOT NULL, -- 'ELC' or 'USDT'
    status TEXT NOT NULL, -- 'pending', 'confirmed', 'failed'
    created_at INTEGER NOT NULL,
    confirmed_at INTEGER
);

-- Mining stats
CREATE TABLE IF NOT EXISTS elcaro_mining_stats (
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id),
    total_mined REAL NOT NULL DEFAULT 0,
    mining_power INTEGER NOT NULL DEFAULT 1,
    last_claim_time INTEGER,
    referral_count INTEGER NOT NULL DEFAULT 0,
    referral_rewards REAL NOT NULL DEFAULT 0
);
```

**Задачи:**
- [ ] Добавить ELCaro таблицы в `db.py`
- [ ] Создать миграцию для существующих данных
- [ ] Обновить `blockchain/db_integration.py` использовать `db.py`
- [ ] Удалить `db_elcaro.py`
- [ ] Обновить `elcaro_bot_commands.py` использовать `db.py`

### Phase 7: Тестирование (3-5 дней)

#### 7.1 Unit Tests
```python
# tests/test_trading_service.py
import pytest
from services import trading_service
from models import OrderSide
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_open_position():
    with patch('core.get_exchange_client') as mock_client:
        mock_client.return_value.place_order = AsyncMock(return_value=Order(...))
        
        order = await trading_service.open_position(
            user_id=123,
            symbol='BTCUSDT',
            side=OrderSide.BUY,
            size_percent=1.0,
            leverage=10
        )
        
        assert order.symbol == 'BTCUSDT'
        assert order.side == OrderSide.BUY
```

**Задачи:**
- [ ] Написать unit tests для всех services
- [ ] Написать integration tests для bot.py → services
- [ ] Написать tests для WebApp API → services
- [ ] Smoke tests для всех критичных путей

---

## 📊 Метрики Успеха

### Количественные
- **Строк кода:** bot.py с 14,442 → ~2,000 строк ✅
- **Дублирование:** 5 реализаций place_order → 1 ✅
- **Покрытие тестами:** 0% → 70%+ ✅
- **Время отклика API:** -30% (благодаря connection pooling) ✅

### Качественные
- ✅ Все модули используют единый формат данных
- ✅ Нет прямых импортов `db` вне `services/`
- ✅ Все exchanges через единый `UnifiedExchangeClient`
- ✅ WebApp API использует только `services/`
- ✅ Одна база данных с proper foreign keys

---

## 🚀 Порядок Выполнения

### Неделя 1: Подготовка (безопасно)
1. ✅ Создать `models/__init__.py` с едиными dataclass
2. ✅ Обновить `exchanges/` использовать новые модели
3. ✅ Написать тесты для `exchanges/`
4. ✅ Обновить `core/exchange_client.py`

### Неделя 2: Services (средний риск)
5. ✅ Переписать `services/trading_service.py`
6. ✅ Переписать `services/signal_service.py`
7. ✅ Написать тесты для services
8. ✅ Провести integration tests

### Неделя 3: Bot Migration (высокий риск!) ⚠️
9. ⚠️ Обновить команды bot.py → user_service
10. ⚠️ Обновить signal handlers → signal_service + trading_service
11. ⚠️ Удалить прямые API вызовы из bot.py
12. ⚠️ **Полное тестирование на demo перед деплоем!**

### Неделя 4: WebApp + DB (средний риск)
13. ✅ Обновить WebApp API → services
14. ✅ Консолидировать db_elcaro.py → db.py
15. ✅ Финальное интеграционное тестирование
16. ✅ Деплой на production

---

## ⚠️ Риски и Митигация

### Риск 1: Поломка bot.py во время рефакторинга
**Митигация:**
- Создать feature branch
- Тестировать каждое изменение локально
- Не деплоить на production до полного тестирования
- Держать возможность быстрого rollback

### Риск 2: Потеря данных при миграции БД
**Митигация:**
- Сделать backup bot.db перед миграцией
- Тестировать миграцию на копии БД
- Создать rollback скрипт
- Проверить все foreign keys

### Риск 3: Ломающие изменения API для WebApp
**Митигация:**
- Версионирование API (/api/v1, /api/v2)
- Документировать breaking changes
- Поддерживать старый API параллельно 1-2 недели
- Использовать feature flags

---

## 📝 Чеклист Перед Каждым Деплоем

- [ ] Все тесты green
- [ ] Локальное тестирование с demo API
- [ ] Проверка логов на ошибки
- [ ] Backup базы данных
- [ ] Проверка всех критичных путей (place order, close position, get balance)
- [ ] Мониторинг метрик после деплоя 30 минут

---

## 🎯 Долгосрочные Улучшения (После Рефакторинга)

1. **Type Safety:** Добавить type hints везде, использовать mypy
2. **Async Optimization:** Batch operations, parallel requests
3. **Monitoring:** Grafana dashboards для metrics
4. **Documentation:** Автогенерация API docs из docstrings
5. **CI/CD:** GitHub Actions для автоматического тестирования
6. **Error Handling:** Централизованная обработка ошибок

---

**Статус:** 🟡 В разработке  
**Следующий шаг:** Phase 1 - Стандартизация моделей данных
