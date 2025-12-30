# ElCaro Trading Platform - Senior Developer Guide

> **Последнее обновление:** 30 декабря 2025  
> **Версия:** 2.2.0  
> **Кодовая база:** ~50,000 строк Python

## 📋 Executive Summary

ElCaro - это асинхронный Telegram торговый бот с FastAPI веб-приложением для торговли криптовалютными фьючерсами на Bybit и HyperLiquid.

### Ключевые метрики
- **593 тестов** (все проходят)
- **16,595 строк** в bot.py (монолит)
- **5,724 строк** в db.py (SQLite с WAL)
- **15 языков** интерфейса (полная синхронизация)
- **4 target'а** для торговли (Bybit demo/real + HL testnet/mainnet)

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                     TELEGRAM USERS                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                     bot.py (~16.6K lines)                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │   Handlers  │ │   Signals   │ │  monitor_positions_loop ││
│  │ (Commands)  │ │  (Parsing)  │ │  (Background Task)      ││
│  └──────┬──────┘ └──────┬──────┘ └───────────┬─────────────┘│
│         │               │                     │              │
│         └───────────────┼─────────────────────┘              │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────────┤
│  │         place_order_for_targets() / place_order()        │
│  │                    (Order Execution)                     │
│  └──────────────────────────────────────────────────────────┘
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  exchange_router.py (1.1K lines)            │
│        Target Model: (exchange, env) → paper/live           │
│           - place_order_universal()                         │
│           - get_execution_targets()                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
   │ exchanges/   │ │ hl_adapter.py│ │   db.py      │
   │ bybit.py     │ │ (706 lines)  │ │ (5.7K lines) │
   │ (34 методов) │ │ (41 методов) │ │ SQLite+WAL   │
   └──────┬───────┘ └──────┬───────┘ └──────────────┘
          │                │
          ▼                ▼
   ┌──────────────┐ ┌──────────────┐
   │  Bybit API   │ │  HL API      │
   │  REST + WS   │ │  REST + WS   │
   └──────────────┘ └──────────────┘
```

---

## 📁 Структура модулей

### Ядро (Core)

| Файл | Строк | Описание |
|------|-------|----------|
| `bot.py` | 16,595 | Главный монолит - все Telegram хендлеры, обработка сигналов, мониторинг позиций |
| `db.py` | 5,724 | SQLite ORM с WAL, пул из 10 соединений, кеширование конфигов (30с) |
| `exchange_router.py` | 1,140 | Target Model, роутинг ордеров, унифицированные функции `*_universal()` |
| `hl_adapter.py` | 706 | Асинхронный адаптер для HyperLiquid API |
| `coin_params.py` | ~200 | Константы: `ADMIN_ID`, `DEFAULT_TP_PCT`, `BLACKLIST` |

### core/ - Инфраструктура

| Модуль | Назначение |
|--------|------------|
| `cache.py` | LRU кеши: `user_config_cache`, `price_cache`, `symbol_info_cache` |
| `rate_limiter.py` | Token bucket для API: `bybit_limiter`, `hl_limiter` |
| `connection_pool.py` | Пул HTTP соединений, переиспользование сессий |
| `metrics.py` | Prometheus-совместимые метрики, `track_latency()` |
| `exceptions.py` | Иерархия исключений: `ExchangeError`, `OrderError`, `LicenseError` |
| `exchange_client.py` | `UnifiedExchangeClient` - единый интерфейс для бирж |

### services/ - Бизнес-логика

| Сервис | Назначение |
|--------|------------|
| `trading_service.py` | `TradeRequest`, `TradeResult`, открытие/закрытие позиций |
| `signal_service.py` | Парсинг сигналов из каналов, `TradingSignal` |
| `exchange_service.py` | Адаптеры `BybitAdapter`, `HyperLiquidAdapter` |
| `license_service.py` | Управление подписками: premium, basic, trial |
| `notification_service.py` | Очередь уведомлений пользователям |
| `strategy_marketplace.py` | Маркетплейс пользовательских стратегий |
| `settings_sync.py` | Синхронизация настроек Bot ↔ WebApp |

### exchanges/ - Биржевые клиенты

| Модуль | Методов | Описание |
|--------|---------|----------|
| `bybit.py` | 34 | `BybitExchange` - полный CCXT-подобный клиент |
| `hyperliquid.py` | 41 | `HyperLiquidExchange` - обёртка над hl_adapter |
| `base.py` | - | Базовые dataclasses: `Position`, `Balance`, `Order`, `OrderResult` |
| `registry.py` | - | Реестр активных клиентов |

### models/ - Унифицированные модели

| Модуль | Назначение |
|--------|------------|
| `unified.py` | `Position.from_bybit()`, `Position.from_hyperliquid()` - конвертеры |
| `position.py` | Расширенная модель позиции |
| `trade.py` | История сделок |
| `user.py` | Модель пользователя |

### webapp/ - FastAPI приложение

| Путь | Описание |
|------|----------|
| `app.py` | Главное приложение, порт 8765 |
| `api/auth.py` | JWT аутентификация, Telegram OAuth |
| `api/trading.py` | REST API для торговли |
| `api/websocket.py` | WebSocket для real-time обновлений |
| `api/backtest*.py` | Модуль бэктестинга |
| `api/screener_ws.py` | Скринер с Binance WebSocket |
| `api/ai.py` | AI торговый агент (GPT-4) |
| `realtime/` | Real-time workers для Bybit/HL |
| `templates/` | Jinja2 HTML шаблоны |
| `static/` | CSS/JS ассеты |

### translations/ - Локализация

15 языков (651 ключ каждый):
`ar`, `cs`, `de`, `en`, `es`, `fr`, `he`, `it`, `ja`, `lt`, `pl`, `ru`, `sq`, `uk`, `zh`

---

## 🔄 Routing Policy System (NEW!)

### 4-Target Matrix

| Exchange | Env | account_type | Описание |
|----------|-----|--------------|----------|
| bybit | paper | demo | Демо счёт Bybit |
| bybit | live | real | Реальный счёт Bybit |
| hyperliquid | paper | testnet | Тестнет HyperLiquid |
| hyperliquid | live | mainnet | Mainnet HyperLiquid |

### Routing Policies

```python
class RoutingPolicy:
    ACTIVE_ONLY = "active_only"           # Только текущий target из UI
    SAME_EXCHANGE_ALL_ENVS = "same_exchange_all_envs"  # Текущая биржа, все envs
    ALL_ENABLED = "all_enabled"           # Все 4 target'а (если включены)
    CUSTOM = "custom"                     # Кастомный список из targets_json
```

### Safety Control

```python
# live_enabled = False (по умолчанию) блокирует live торговлю
db.set_live_enabled(user_id, True)  # Разблокировать
```

---

## 🗃️ База данных (db.py)

### Ключевые таблицы

| Таблица | Назначение |
|---------|------------|
| `users` | Конфигурация пользователей, API ключи |
| `user_strategy_settings` | Настройки стратегий per exchange/env |
| `active_positions` | Открытые позиции |
| `trade_logs` | История сделок |
| `signals` | Входящие сигналы |
| `pending_limit_orders` | Ожидающие лимитные ордера |
| `user_licenses` | Подписки пользователей |
| `exchange_accounts` | Конфигурация аккаунтов (новая) |

### Ключевые функции

```python
# Пользователи
get_user_config(uid)           # Получить все настройки (кешируется 30с)
set_user_field(uid, field, val)  # Установить поле
invalidate_user_cache(uid)     # Сбросить кеш

# Credentials
get_user_credentials(uid, account_type)  # 'demo' | 'real'
set_user_credentials(uid, key, secret, account_type)
get_hl_credentials(uid)
set_hl_credentials(uid, private_key, vault, testnet)

# Trading Context
get_user_trading_context(uid)  # → {exchange, account_type, env}
get_execution_targets(uid, strategy, override_policy)  # → [targets]

# Strategy Settings (с fallback!)
get_strategy_settings(uid, strategy, exchange, account_type)
# Fallback: exact → exchange-level → global → defaults

# Positions
add_active_position(uid, symbol, side, entry, size, ...)
get_active_positions(uid)
remove_active_position(uid, symbol)

# Routing Policy
get_routing_policy(uid)        # → 'active_only' | 'same_exchange_all_envs' | ...
set_routing_policy(uid, policy)
get_live_enabled(uid)          # → bool
set_live_enabled(uid, enabled)
```

---

## 🤖 Bot.py - Главные компоненты

### Декораторы (порядок важен!)

```python
@log_calls        # Логирование исключений (line 375)
@require_access   # Проверка banned/allowed + инъекция ctx.t (line 491)
async def handler(update, ctx):
    t = ctx.t     # Словарь переводов
```

⚠️ **`@require_access` уже включает `@with_texts`** - не дублировать!

### Background Tasks

1. **`monitor_positions_loop`** (line ~10500)
   - Мониторинг TP/SL/ATR trailing
   - Проверка позиций на бирже vs БД
   - Reconciliation расхождений

2. **`spot_auto_dca_loop`**
   - Автоматический DCA для spot

3. **`notification_service_loop`**
   - Отправка отложенных уведомлений

### Order Execution

```python
# Новый способ (multi-target)
await place_order_for_targets(
    user_id, symbol, side, order_type, qty,
    strategy="elcaro",
    use_legacy_routing=False  # Использовать routing_policy
)

# Legacy (backward compatible)
await place_order_all_accounts(uid, symbol, side, type, qty)
# Обёртка над place_order_for_targets(use_legacy_routing=True)
```

---

## 🌐 WebApp API

### Endpoints Structure

| Prefix | Router | Описание |
|--------|--------|----------|
| `/api/auth` | auth.py | JWT, Telegram OAuth |
| `/api/users` | users.py | Профиль, настройки |
| `/api/trading` | trading.py | Позиции, ордера, баланс |
| `/api/stats` | stats.py | Статистика, PnL |
| `/api/admin` | admin.py | Админ панель |
| `/api/backtest` | backtest*.py | Бэктестинг |
| `/api/marketplace` | marketplace.py | Маркетплейс стратегий |
| `/ws/terminal` | websocket.py | Real-time терминал |
| `/ws/realtime/{exchange}` | realtime.py | Market data stream |
| `/ws/screener` | screener_ws.py | Скринер данные |

### Health & Metrics

```bash
GET /health          # {"status": "healthy", ...}
GET /health/detailed # Детальная информация
GET /metrics         # Prometheus формат
```

---

## ⚠️ Найденные несоответствия логике

### 1. Дублирование функций в db.py ✅ ИСПРАВЛЕНО

**Было:** Две функции `get_execution_targets` на линиях 1533 и 3334
**Исправлено:** Старая переименована в `_get_execution_targets_from_exchange_accounts`

### 2. monitor_positions_loop не использует routing_policy

**Проблема:** Loop использует старый `trading_mode` вместо нового `get_execution_targets()`

**Рекомендация:**
```python
# Заменить:
if trading_mode in ("demo", "both"):
    positions = await fetch_positions("demo")
if trading_mode in ("real", "both"):
    positions = await fetch_positions("real")

# На:
targets = db.get_execution_targets(uid)
for target in targets:
    positions = await fetch_positions(target["account_type"])
```

### 3. Strategy settings fallback не покрывает все кейсы

**Текущий fallback:** `exact → exchange-level → global → defaults`

**Отсутствует:** env-level (paper vs live) без привязки к exchange

**Рекомендация:** Добавить промежуточный уровень:
```
exact(exchange+env) → env-level → exchange-level → global → defaults
```

### 4. HyperLiquid testnet credentials

**Проблема:** Отдельного поля `hl_testnet_private_key` нет - используется общий `hl_private_key` + флаг `hl_testnet`

**Рекомендация:** Добавить отдельные credentials для testnet/mainnet

### 5. Real-time worker float parsing ✅ ИСПРАВЛЕНО

**Было:** `float(data.get('value', 0))` падало на пустых строках
**Исправлено:** Добавлена функция `safe_float()` с обработкой `''` и `None`

### 6. Отсутствует rate limiting для WebSocket

**Проблема:** WebSocket connections не имеют rate limiting

**Рекомендация:** Добавить лимит на количество подключений per user

### 7. exchange_accounts vs legacy credentials

**Проблема:** Две параллельные системы хранения credentials:
- Старая: `demo_api_key`, `real_api_key` в `users`
- Новая: таблица `exchange_accounts`

**Рекомендация:** Мигрировать всех на `exchange_accounts`, оставить legacy только для обратной совместимости

---

## 🧪 Тестирование

```bash
# Запуск всех тестов
python3 -m pytest tests/ -v

# Конкретные модули
python3 -m pytest tests/test_routing_policy.py -v
python3 -m pytest tests/test_exchange_router.py -v
python3 -m pytest tests/test_unified_models.py -v

# С покрытием
python3 -m pytest tests/ --cov=. --cov-report=html
```

### Текущий статус: 593/593 passed ✅

---

## 🚀 Локальный запуск

```bash
# 1. Активация venv
source venv/bin/activate

# 2. Запуск бота
python3 bot.py

# 3. Запуск webapp
JWT_SECRET=your_secret python3 -m uvicorn webapp.app:app --host 0.0.0.0 --port 8765

# Или через start.sh
./start.sh --bot      # Только бот
./start.sh --webapp   # Только webapp
./start.sh            # Оба
```

---

## 📦 Production (AWS EC2)

```bash
# SSH
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com

# Деплой
cd /home/ubuntu/project/elcarobybitbotv2
git pull origin main
sudo systemctl restart elcaro-bot

# Логи
journalctl -u elcaro-bot -f --no-pager
```

---

## 📝 Контрольный список для изменений

- [ ] Добавить переводы в `translations/en.py` (reference)
- [ ] Проверить sync: `python3 utils/translation_sync.py --report`
- [ ] Добавить миграцию в `init_db()` если новые поля
- [ ] Добавить поле в `USER_FIELDS_WHITELIST` если нужно
- [ ] Сбросить кеш: `invalidate_user_cache(uid)` после записи
- [ ] Запустить тесты: `python3 -m pytest tests/`
- [ ] Проверить webapp: `curl localhost:8765/health`

---

*Документ сгенерирован автоматически. Актуален на 30 декабря 2025.*
