# Руководство по Миграции - Unified Models

**Дата:** 23 декабря 2025  
**Статус:** ✅ Phase 1 Complete  

---

## 📦 Что Создано

### 1. Unified Data Models (`models/unified.py`)

Единые модели данных для всех слоев проекта:

```python
from models import (
    # Enums
    OrderSide, OrderType, OrderStatus, PositionSide,
    # Core Models
    Position, Order, Balance, OrderResult,
    # Helpers
    normalize_symbol, convert_side
)
```

#### Ключевые Особенности

✅ **Единый Формат** - одна модель `Position` вместо 3 разных  
✅ **Автоматическая Конвертация** - `Position.from_bybit()`, `Position.from_hyperliquid()`  
✅ **Type Safety** - строгая типизация с dataclasses  
✅ **Exchange Agnostic** - работает с любой биржей  
✅ **JSON Serialization** - `.to_dict()` для API responses  

---

## 🔄 Как Мигрировать Существующий Код

### Пример 1: Получение Позиций

#### ❌ Старый Код (bot.py)
```python
async def get_positions_bybit(user_id):
    # Прямой API запрос
    resp = await _bybit_request(user_id, "GET", "/v5/position/list", {})
    if resp.get("retCode") != 0:
        return []
    
    # Возвращаем raw dict
    positions = resp.get("result", {}).get("list", [])
    return positions

# Использование - работа с dict
positions = await get_positions_bybit(uid)
for pos in positions:
    symbol = pos['symbol']  # dict access
    side = pos['side']      # строка "Buy" или "Sell"
    pnl = float(pos.get('unrealisedPnl', 0))  # ручное преобразование
```

#### ✅ Новый Код (с unified models)
```python
from models import Position
from core import get_exchange_client

async def get_positions(user_id: int) -> list[Position]:
    """Получить позиции - автоматически роутинг Bybit/HL"""
    client = get_exchange_client(user_id)
    return await client.get_positions()

# Использование - работа с объектами
positions = await get_positions(uid)
for pos in positions:
    symbol = pos.symbol              # typed attribute
    side = pos.side                  # PositionSide enum
    pnl = pos.unrealized_pnl         # уже float
    
    # Удобные свойства
    if pos.is_long:
        print(f"Long {pos.symbol}: {pos.pnl_percent:.2f}%")
    
    # JSON для WebApp
    return pos.to_dict()  # готов для FastAPI
```

### Пример 2: Размещение Ордера

#### ❌ Старый Код
```python
async def place_order(user_id, symbol, side, orderType, qty, price, account_type):
    # 250+ строк кода
    
    # Получаем credentials
    creds = db.get_user_credentials(user_id, account_type)
    
    # Формируем параметры
    params = {
        "category": "linear",
        "symbol": symbol,
        "side": side,  # "Buy" или "Sell" строка
        "orderType": orderType,
        "qty": str(qty),
        "price": str(price) if price else "",
    }
    
    # Подпись
    signature = generate_signature(params, creds['api_secret'])
    
    # HTTP запрос
    async with aiohttp.ClientSession() as session:
        headers = {"X-BAPI-API-KEY": creds['api_key'], ...}
        async with session.post(url, json=params, headers=headers) as resp:
            data = await resp.json()
    
    # Обработка ответа (raw dict)
    if data.get("retCode") != 0:
        raise Exception(data.get("retMsg"))
    
    result = data.get("result", {})
    return result  # dict
```

#### ✅ Новый Код
```python
from models import OrderSide, OrderType, Order
from core import get_exchange_client

async def place_order(
    user_id: int,
    symbol: str,
    side: OrderSide,
    order_type: OrderType,
    size: float,
    price: Optional[float] = None,
    leverage: int = 10
) -> Order:
    """Разместить ордер - автоматически роутинг Bybit/HL"""
    client = get_exchange_client(user_id)
    
    return await client.place_order(
        symbol=symbol,
        side=side,
        size=size,
        order_type=order_type,
        price=price,
        leverage=leverage
    )

# Использование
order = await place_order(
    user_id=123,
    symbol="BTCUSDT",
    side=OrderSide.BUY,
    order_type=OrderType.MARKET,
    size=0.1,
    leverage=10
)

print(f"Order placed: {order.order_id}")
print(f"Fill: {order.fill_percent:.1f}%")
```

### Пример 3: Конвертация из Bybit API

#### В Exchange Wrapper
```python
# exchanges/bybit.py

from models import Position, Order, Balance

class BybitExchange:
    async def get_positions(self) -> list[Position]:
        """Получить позиции Bybit"""
        resp = await self._request("GET", "/v5/position/list", {})
        
        if resp.get("retCode") != 0:
            raise ExchangeError(resp.get("retMsg"))
        
        # Конвертируем каждую позицию
        raw_positions = resp.get("result", {}).get("list", [])
        return [Position.from_bybit(p) for p in raw_positions]
    
    async def place_order(
        self, 
        symbol: str, 
        side: OrderSide,
        size: float,
        order_type: OrderType = OrderType.MARKET,
        price: Optional[float] = None
    ) -> Order:
        """Разместить ордер Bybit"""
        
        params = {
            "category": "linear",
            "symbol": symbol,
            "side": side.value,  # "Buy" или "Sell"
            "orderType": order_type.value,
            "qty": str(size),
        }
        
        if price:
            params["price"] = str(price)
        
        resp = await self._request("POST", "/v5/order/create", params)
        
        if resp.get("retCode") != 0:
            raise ExchangeError(resp.get("retMsg"))
        
        # Конвертируем результат
        order_data = resp.get("result", {})
        return Order.from_bybit(order_data)
```

---

## 🔧 Пошаговая Миграция

### Шаг 1: Обновить exchanges/ (БЕЗОПАСНО)

Уже используют базовые модели, просто обновить импорты:

```python
# exchanges/bybit.py
# Было:
from exchanges.base import Position, Order, Balance

# Стало:
from models import Position, Order, Balance
```

**Коммиты:**
```bash
git add exchanges/
git commit -m "refactor: use unified models in exchanges layer"
```

### Шаг 2: Обновить services/ (БЕЗОПАСНО)

Services пока мало используются, можно смело обновлять:

```python
# services/trading_service.py
from models import Position, Order, OrderSide, OrderType, OrderResult

class TradingService:
    async def open_position(self, user_id: int, ...) -> Order:
        # Используем типизированные модели
        client = get_exchange_client(user_id)
        return await client.place_order(...)
```

**Коммиты:**
```bash
git add services/
git commit -m "refactor: migrate services to unified models"
```

### Шаг 3: Обновить core/ (СРЕДНИЙ РИСК)

Обновить `core/exchange_client.py`:

```python
# core/exchange_client.py
from models import Position, Order, Balance, OrderSide, OrderType

class UnifiedExchangeClient:
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,  # используем enum
        size: float,
        order_type: OrderType = OrderType.MARKET,
        ...
    ) -> Order:  # возвращаем типизированный Order
        ...
```

**Тестирование:**
```bash
# Юнит тесты для core
pytest tests/test_core/ -v

# Интеграционные тесты
pytest tests/test_integration/ -v -k exchange_client
```

**Коммиты:**
```bash
git add core/
git commit -m "refactor: unified models in core layer"
```

### Шаг 4: Постепенно Обновлять bot.py (ВЫСОКИЙ РИСК!) ⚠️

**НЕ обновлять всё сразу!** Постепенно по функциям.

#### Подход: Feature Flags

```python
# bot.py
USE_UNIFIED_MODELS = os.getenv("USE_UNIFIED_MODELS", "false").lower() == "true"

if USE_UNIFIED_MODELS:
    from models import Position, Order, OrderSide
    # Новый код
else:
    # Старый код (fallback)
```

#### Порядок Миграции bot.py

1. **Команды API настроек** (низкий риск)
   - `/api`, `/api_demo`, `/api_real`
   - Используют только `db`, не затрагивают торговлю

2. **Команды статистики** (низкий риск)
   - `/stats`, `/positions`, `/balance`
   - Только чтение, не изменяют состояние

3. **Ручные команды торговли** (средний риск)
   - `/close`, `/closeall`
   - Тестировать на demo аккаунте

4. **Signal Handlers** (высокий риск!) ⚠️
   - `handle_scryptomera_signal()`
   - `handle_elcaro_signal()`
   - **КРИТИЧНО: тестировать несколько дней на demo!**

**Коммиты каждого шага:**
```bash
# 1. API commands
git add bot.py
git commit -m "refactor(bot): migrate API commands to unified models"

# 2. Stats commands
git add bot.py
git commit -m "refactor(bot): migrate stats commands to unified models"

# 3. Manual trading
git add bot.py
git commit -m "refactor(bot): migrate manual trading to unified models"

# 4. Signal handlers (после тестирования!)
git add bot.py
git commit -m "refactor(bot): migrate signal handlers to unified models"
```

### Шаг 5: Обновить WebApp (СРЕДНИЙ РИСК)

WebApp использует FastAPI с Pydantic, легко интегрировать:

```python
# webapp/api/trading.py
from fastapi import APIRouter
from models import Position, Order

router = APIRouter()

@router.get("/positions", response_model=list[dict])
async def get_positions(user_id: int):
    from services import trading_service
    
    positions = await trading_service.get_positions(user_id)
    return [p.to_dict() for p in positions]  # автоматическая сериализация

@router.post("/orders", response_model=dict)
async def place_order(user_id: int, order_request: OrderRequest):
    from services import trading_service
    
    order = await trading_service.place_order(
        user_id=user_id,
        symbol=order_request.symbol,
        side=OrderSide(order_request.side),
        ...
    )
    return order.to_dict()
```

**Коммиты:**
```bash
git add webapp/api/
git commit -m "refactor(webapp): migrate API to unified models"
```

---

## ✅ Чеклист Миграции

### Phase 1: Подготовка ✅ DONE
- [x] Создать `models/unified.py`
- [x] Добавить конвертеры `from_bybit()`, `from_hyperliquid()`
- [x] Добавить `.to_dict()` для JSON serialization
- [x] Обновить `models/__init__.py`

### Phase 2: Infrastructure (Следующий шаг)
- [ ] Обновить `exchanges/bybit.py` использовать unified models
- [ ] Обновить `exchanges/hyperliquid.py` использовать unified models
- [ ] Обновить `hl_adapter.py` использовать unified models
- [ ] Написать unit tests для конвертеров
- [ ] Обновить `core/exchange_client.py` (типизация)

### Phase 3: Services Layer
- [ ] Обновить `services/trading_service.py`
- [ ] Обновить `services/exchange_service.py`
- [ ] Обновить `services/signal_service.py`
- [ ] Написать integration tests для services

### Phase 4: Bot Migration (Постепенно!)
- [ ] Обновить API commands (низкий риск)
- [ ] Обновить stats commands (низкий риск)
- [ ] Обновить manual trading commands (средний риск)
- [ ] **ТЕСТИРОВАТЬ каждый шаг на demo!**
- [ ] Обновить signal handlers (высокий риск!)
- [ ] **Полное тестирование 3-5 дней на demo**

### Phase 5: WebApp
- [ ] Обновить `webapp/api/trading.py`
- [ ] Обновить `webapp/api/admin.py`
- [ ] Обновить `webapp/api/users.py`
- [ ] Обновить `webapp/api/stats.py`

### Phase 6: Cleanup
- [ ] Удалить старые модели из `models/position.py` (если не используются)
- [ ] Удалить дублированный код из `exchange_router.py`
- [ ] Обновить документацию
- [ ] Финальное интеграционное тестирование

---

## 🧪 Тестирование

### Unit Tests
```python
# tests/test_unified_models.py
import pytest
from models import Position, Order, Balance, OrderSide, PositionSide

def test_position_from_bybit():
    """Test Bybit position conversion"""
    bybit_data = {
        'symbol': 'BTCUSDT',
        'side': 'Buy',
        'size': '0.1',
        'avgPrice': '45000',
        'unrealisedPnl': '100',
        'leverage': '10',
        'positionIM': '450',
        'liqPrice': '40000'
    }
    
    pos = Position.from_bybit(bybit_data)
    
    assert pos.symbol == 'BTCUSDT'
    assert pos.side == PositionSide.LONG
    assert pos.size == 0.1
    assert pos.entry_price == 45000
    assert pos.unrealized_pnl == 100
    assert pos.leverage == 10
    assert pos.is_long is True

def test_position_properties():
    """Test calculated properties"""
    pos = Position(
        symbol='BTCUSDT',
        side=PositionSide.LONG,
        size=0.1,
        entry_price=45000,
        mark_price=46000,
        unrealized_pnl=100,
        margin_used=450,
        leverage=10
    )
    
    assert pos.position_value == 4500  # 0.1 * 45000
    assert pos.current_value == 4600   # 0.1 * 46000
    assert abs(pos.pnl_percent - 22.22) < 0.01  # 100/450 * 100
    assert abs(pos.roi_percent - 2.22) < 0.01   # 100/4500 * 100

def test_order_from_bybit():
    """Test Bybit order conversion"""
    bybit_data = {
        'orderId': '123456',
        'symbol': 'BTCUSDT',
        'side': 'Buy',
        'orderType': 'Market',
        'qty': '0.1',
        'cumExecQty': '0.1',
        'avgPrice': '45000',
        'orderStatus': 'Filled'
    }
    
    order = Order.from_bybit(bybit_data)
    
    assert order.order_id == '123456'
    assert order.side == OrderSide.BUY
    assert order.size == 0.1
    assert order.is_filled is True
```

### Integration Tests
```python
# tests/test_exchange_integration.py
import pytest
from models import Position, OrderSide, OrderType
from core import get_exchange_client

@pytest.mark.asyncio
async def test_place_order_returns_unified_model(test_user_id):
    """Test that exchange client returns unified Order"""
    client = get_exchange_client(test_user_id)
    
    order = await client.place_order(
        symbol='BTCUSDT',
        side=OrderSide.BUY,
        size=0.001,  # Минимальный размер для теста
        order_type=OrderType.MARKET
    )
    
    # Проверяем что вернулся типизированный Order
    assert isinstance(order, Order)
    assert order.symbol == 'BTCUSDT'
    assert order.side == OrderSide.BUY
    assert order.order_id is not None

@pytest.mark.asyncio
async def test_get_positions_returns_unified_models(test_user_id):
    """Test that positions are unified Position objects"""
    client = get_exchange_client(test_user_id)
    
    positions = await client.get_positions()
    
    for pos in positions:
        assert isinstance(pos, Position)
        assert hasattr(pos, 'symbol')
        assert hasattr(pos, 'pnl_percent')  # calculated property
        assert pos.to_dict()  # can serialize
```

---

## 📊 Метрики Успеха

### Текущий Статус (Phase 1 Complete)

✅ **Создано:**
- `models/unified.py` - 600+ строк
- Все основные модели: Position, Order, Balance, OrderResult
- Конвертеры для Bybit и HyperLiquid
- Helper функции

### Следующие Шаги (Phase 2)

🔄 **В процессе:**
- Миграция exchanges/ на unified models
- Unit tests для конвертеров
- Integration tests

### Долгосрочная Цель

🎯 **Полная миграция:**
- 0 импортов dict для positions/orders в bot.py
- 100% type safety
- Единый формат данных across all layers
- Упрощение кода на 30-40%

---

## 🚨 Важные Замечания

### 1. Обратная Совместимость
Старый код будет работать параллельно во время миграции. Не удаляем старые функции до полной миграции.

### 2. Тестирование на Demo
**КРИТИЧНО:** Каждое изменение bot.py тестировать на demo аккаунте минимум 1 день перед production.

### 3. Rollback Plan
Держать возможность быстрого отката через git:
```bash
# Откат последнего коммита
git revert HEAD

# Откат к конкретному коммиту
git revert abc123
```

### 4. Мониторинг После Деплоя
- Следить за логами 30 минут после деплоя
- Проверить все критичные пути (open position, close position)
- Мониторить метрики (latency, errors)

---

**Следующий документ:** [Phase 2 - Exchanges Migration](PHASE2_EXCHANGES.md)
