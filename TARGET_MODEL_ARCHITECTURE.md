# Target Model Architecture (Dec 30, 2025)

## Overview

Новая унифицированная модель Target для multi-exchange/multi-env архитектуры.

### Ключевой принцип

**Target = (exchange, env)** где:
- `exchange`: "bybit" | "hyperliquid"
- `env`: "paper" | "live" (унифицированный)

### Mapping env ↔ account_type

| Exchange     | env=paper  | env=live   |
|--------------|------------|------------|
| Bybit        | demo       | real       |
| HyperLiquid  | testnet    | mainnet    |

## Реализация

### exchange_router.py

```python
from exchange_router import Target, Env, Exchange, normalize_env, denormalize_env

# Создание target
target = Target(exchange="bybit", env="paper")
print(target.key)           # "bybit:paper"
print(target.account_type)  # "demo" (обратная совместимость)

# Нормализация env
normalize_env("demo")     # -> "paper"
normalize_env("testnet")  # -> "paper"
normalize_env("real")     # -> "live"
normalize_env("mainnet")  # -> "live"

# Денормализация (для API вызовов)
denormalize_env("paper", "bybit")       # -> "demo"
denormalize_env("live", "hyperliquid")  # -> "mainnet"
```

### db.py

```python
import db

# Добавление позиции с автоматическим расчетом env
db.add_active_position(
    user_id=123,
    symbol="BTCUSDT",
    side="Buy",
    entry_price=50000,
    size=0.1,
    account_type="demo",  # legacy
    exchange="bybit",
    # env вычисляется автоматически: demo -> paper
)

# Получение позиций по target
positions = db.get_active_positions(
    user_id=123,
    exchange="bybit",
    env="paper"
)

# Получение позиций для всех target'ов
all_positions = db.get_all_positions_by_targets(
    user_id=123,
    targets=[
        {"exchange": "bybit", "env": "paper"},
        {"exchange": "bybit", "env": "live"},
        {"exchange": "hyperliquid", "env": "live"},
    ]
)
# Returns: {"bybit:paper": [...], "bybit:live": [...], "hyperliquid:live": [...]}
```

### get_user_targets()

```python
from exchange_router import get_user_targets

# Получить ВСЕ target'ы пользователя (для мониторинга)
targets = get_user_targets(user_id=123)
# Returns list of Target objects based on user's credentials

for target in targets:
    print(f"Monitoring {target.key}...")
    positions = db.get_positions_by_target(user_id, target.exchange, target.env)
```

## Миграции DB

### active_positions

Добавлена колонка `env`:
```sql
ALTER TABLE active_positions ADD COLUMN env TEXT

-- Заполнение на основе account_type
UPDATE active_positions 
SET env = CASE 
    WHEN account_type IN ('demo', 'testnet') THEN 'paper'
    WHEN account_type IN ('real', 'mainnet') THEN 'live'
    ELSE 'paper'
END
WHERE env IS NULL

CREATE INDEX idx_active_env ON active_positions(user_id, exchange, env)
```

## Мониторинг (Planned)

### Правильный паттерн мониторинга

```python
async def monitor_positions_loop(user_id: int):
    """
    Мониторинг должен итерировать ВСЕ target'ы пользователя,
    не только "активный" из trading_mode.
    """
    targets = get_user_targets(user_id)
    
    for target in targets:
        # 1. Получить позиции с биржи
        exchange_positions = await fetch_from_exchange(user_id, target)
        
        # 2. Получить позиции из DB
        db_positions = db.get_positions_by_target(user_id, target.exchange, target.env)
        
        # 3. Reconcile: обновить DB на основе биржи
        await reconcile_positions(
            user_id=user_id,
            target=target,
            exchange_positions=exchange_positions,
            db_positions=db_positions,
        )
```

### Reconcile Pattern

- **Bot/WebApp** пишут order_intent / метадату
- **Reconcile (monitor)** единственный кто пишет в `active_positions`
- `active_positions` = слепок биржи, а не "что бот открыл"

## Backward Compatibility

### ExecutionTarget alias

```python
# ExecutionTarget теперь alias для Target
ExecutionTarget = Target

# Старый код продолжит работать
target = ExecutionTarget(exchange="bybit", env="paper")
# target.account_type property возвращает legacy значение
```

### account_type в DB

- Колонка `account_type` остаётся PRIMARY KEY
- `env` вычисляется автоматически при вставке
- Фильтрация работает по обоим полям

## Tests

```bash
# Run all tests
pytest tests/test_exchange_router.py tests/test_database.py -v

# Expected: 55+ passed
```

## Changes Summary

### exchange_router.py
- ✅ Added `Env` enum (PAPER, LIVE)
- ✅ Added `Target` dataclass with `env` field
- ✅ Added `normalize_env()` and `denormalize_env()` functions
- ✅ Added `get_user_targets()` function
- ✅ `ExecutionTarget` is now alias for `Target`
- ✅ All type hints updated to use `Target`

### db.py
- ✅ Added `env` column to active_positions
- ✅ Migration populates env based on account_type
- ✅ `add_active_position()` accepts `env` parameter
- ✅ `get_active_positions()` accepts `env` filter
- ✅ Added `get_positions_by_target()` function
- ✅ Added `get_all_positions_by_targets()` function
- ✅ Added `_normalize_env()` helper

### tests/test_exchange_router.py
- ✅ Added `TestEnvNormalization` class with 8 tests
- ✅ Updated `test_execution_target` to use `Target` with `env`

## Next Steps

1. **Update monitor_positions_loop in bot.py**:
   - Use `get_user_targets()` instead of single trading_mode
   - Iterate all targets for reconcile

2. **Update WebApp terminal**:
   - Add target selector UI (exchange + env dropdown)
   - Filter positions by target

3. **Implement reconcile pattern**:
   - Move position writes to reconcile-only
   - Bot/WebApp write intents, not positions
