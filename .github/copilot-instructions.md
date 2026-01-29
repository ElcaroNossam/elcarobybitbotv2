# Enliko Trading Platform - AI Coding Guidelines
# =============================================
# Версия: 3.38.0 | Обновлено: 28 января 2026
# =============================================
# Production Domain: https://enliko.com (nginx + SSL)
# Cross-Platform Sync: iOS ↔ WebApp ↔ Telegram Bot ↔ Android
# iOS Full Localization: 15 languages + RTL support
# Android App: Kotlin + Jetpack Compose
# Modern Features: Biometrics, Haptics, Animations, Offline-First
# 4D Schema: (user_id, strategy, side, exchange)
# Break-Even (BE): Move SL to entry when profit >= trigger%
# Partial Take Profit: Close X% at +Y% profit in 2 steps
# Translations: 15 languages × 690 keys = Full sync (Jan 28, 2026)

---

# 📚 КЛЮЧЕВАЯ ДОКУМЕНТАЦИЯ

| Документ | Путь | Описание |
|----------|------|----------|
| **Trading Streams** | `docs/TRADING_STREAMS_ARCHITECTURE.md` | Полная карта 60 торговых потоков |
| **Copilot Instructions** | Этот файл | Правила для AI |
| **Keyboard Helpers** | `keyboard_helpers.py` | Централизованный factory для кнопок |
| **Sync Service** | `services/sync_service.py` | Кросс-платформенная синхронизация |
| **Activity API** | `webapp/api/activity.py` | История активности пользователей |

---

# 🚨🚨🚨 КРИТИЧЕСКИЕ ПРАВИЛА (ЧИТАТЬ ПЕРВЫМ!) 🚨🚨🚨

## ⛔ АБСОЛЮТНЫЕ ЗАПРЕТЫ

1. **НИКОГДА НЕ УДАЛЯТЬ СУЩЕСТВУЮЩИЙ КОД** без прямого запроса
   - Только добавление нового функционала
   - Только исправление багов в существующем коде
   - ЗАПРЕЩЕНО: "упрощать", "рефакторить", "удалять неиспользуемое"

2. **НИКОГДА НЕ УПРОЩАТЬ ЛОГИКУ**
   - Все условия, проверки, fallback'и - важны
   - Если кажется "лишним" - спроси пользователя

3. **НИКОГДА НЕ ЗАПУСКАТЬ `git push`**
   - Все изменения - только локально
   - Пользователь сам решает когда пушить

4. **НИКОГДА НЕ УДАЛЯТЬ ФАЙЛЫ** без явного запроса
   - Особенно: `.py`, `.html`, `.css`, `.js`
   - Даже если файл выглядит неиспользуемым

---

## 🧠 ОБЯЗАТЕЛЬНЫЙ АНАЛИЗ ПЕРЕД КАЖДЫМ ЗАПРОСОМ

**Перед любым изменением кода ОБЯЗАТЕЛЬНО:**

1. **Прочитать текущий код** в контексте изменения (read_file)
2. **Понять архитектуру** - как этот код связан с другими модулями
3. **Найти все использования** (grep_search, list_code_usages)
4. **Проверить зависимости** - что сломается при изменении
5. **Спланировать минимальное изменение** - изменить только то, что нужно

**❌ ЗАПРЕЩЕНО:**
- Делать изменения "наугад"
- Удалять код который "выглядит неиспользуемым"
- Рефакторить без запроса

## 🔴 НЕМЕДЛЕННОЕ ИСПРАВЛЕНИЕ ОШИБОК

**При обнаружении ошибок во время выполнения запроса:**

1. **НЕМЕДЛЕННО исправить** - не откладывать на "потом"
2. **Найти причинно-следственную связь** - почему ошибка возникла
3. **Проверить все связанные места** - где ещё может быть аналогичная проблема
4. **Исправить комплексно** - все найденные места, не только первое
5. **Проверить результат** - убедиться что исправление работает

## 🚀 ОБЯЗАТЕЛЬНЫЙ DEPLOYMENT ПОСЛЕ КАЖДОЙ ЗАДАЧИ

**После ЛЮБЫХ изменений в коде ОБЯЗАТЕЛЬНО:**

1. **Commit изменения локально:**
   ```bash
   git add -A && git commit -m "fix/feat: краткое описание"
   ```

2. **Push на GitHub:**
   ```bash
   git push origin main
   ```

3. **Deploy на сервер и перезапуск:**
   ```bash
   ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com \
     'cd /home/ubuntu/project/elcarobybitbotv2 && git pull origin main && sudo systemctl restart elcaro-bot'
   ```

4. **Проверить логи (обязательно!):**
   ```bash
   ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com \
     'journalctl -u elcaro-bot -n 50 --no-pager'
   ```

5. **Убедиться что нет ошибок** - искать `ERROR`, `Exception`, `Traceback`

**❌ ЗАПРЕЩЕНО:**
- Заканчивать задачу без деплоя
- Деплоить без проверки логов
- Игнорировать ошибки в логах после деплоя

**Паттерн исправления:**
```
1. Увидел ошибку → Читаю код → Нахожу причину
2. Ищу аналогичные места → grep_search / list_code_usages
3. Исправляю ВСЕ места → Проверяю get_errors
4. Тестирую если возможно
```

**❌ ЗАПРЕЩЕНО:**
- Игнорировать ошибки "это потом"
- Исправлять только симптом, не причину
- Исправлять одно место, когда проблема в нескольких

---

## 📝 САМООБНОВЛЕНИЕ ИНСТРУКЦИЙ

**Когда обновлять этот файл:**
- После добавления нового критического функционала
- После исправления важных багов (с описанием fix'а)
- После изменения архитектуры
- После изменения deployment процедур
- После каждой сессии с важными изменениями

**Как обновлять:**
1. Добавить в секцию "Recent Fixes" с датой
2. Обновить номера строк если изменились
3. Добавить новые паттерны если появились
4. Обновить версию и дату в заголовке

---

# 📊 АРХИТЕКТУРА ПРОЕКТА

## Статистика проекта (актуально на 27.01.2026)

| Метрика | Значение |
|---------|----------|
| Python файлов | 325 |
| HTML шаблонов | 44 |
| CSS файлов | 15 |
| JS файлов | 26 |
| Swift файлов | 35+ |
| **Kotlin файлов** | **30+** (NEW Android app!) |
| **Тестов** | **708 (416 unit + 293 integration)** |
| Языков перевода | 15 |
| Ключей перевода | 1540+ |
| База данных | PostgreSQL 14 (ONLY) |
| API endpoints | 127+ |
| Migration files | 19 |
| iOS Bundle ID | io.enliko.EnlikoTrading |
| **Android Package** | io.enliko.trading |
| Xcode | 26.2 (17C52) |
| **Android SDK** | 35 (minSdk 26) |
| **Cross-Platform Sync** | iOS ↔ WebApp ↔ Telegram ↔ Android |
| **4D Schema** | (user_id, strategy, side, exchange) |

## Структура проекта

```
Enliko Trading Platform
├── bot.py                 # 🔥 Главный бот (25018 строк, 260+ функций)
├── db.py                  # 💾 Database layer (PostgreSQL-ONLY, 6K строк)
├── db_elcaro.py           # 💎 ELC Token functions (705 строк)
├── keyboard_helpers.py    # ⌨️ Centralized button factory (370 строк) ⭐NEW!
├── bot_unified.py         # 🔗 Unified API Bybit/HyperLiquid (530 строк)
├── exchange_router.py     # 🔀 Роутинг между биржами (1187 строк)
├── hl_adapter.py          # 🌐 HyperLiquid адаптер (716 строк)
├── coin_params.py         # ⚙️ Параметры, ADMIN_ID, лимиты (309 строк)
│
├── webapp/                # 🌐 FastAPI веб-приложение
│   ├── app.py             # Main FastAPI app (port 8765)
│   ├── api/               # 25 API роутеров
│   │   ├── auth.py        # Авторизация, JWT токены
│   │   ├── trading.py     # Торговые операции
│   │   ├── stats.py       # Статистика, PnL
│   │   ├── backtest.py    # Бэктестинг (85K строк!)
│   │   ├── admin.py       # Админ панель
│   │   ├── marketplace.py # Маркетплейс стратегий
│   │   ├── screener.py    # Скринер монет
│   │   └── ...            # И другие
│   ├── templates/         # 17 HTML шаблонов
│   │   ├── terminal.html  # Торговый терминал
│   │   ├── backtest.html  # Бэктестер
│   │   ├── screener.html  # Скринер
│   │   ├── marketplace.html
│   │   └── ...
│   └── static/            # CSS/JS/Images
│       ├── css/
│       │   ├── base.css           # ⭐ Unified design system
│       │   ├── terminal-layout.css # Terminal page styles
│       │   └── components/header.css
│       └── js/
│           └── core.js            # ⭐ Unified API/auth/theme
│
├── models/                # Data models
│   ├── unified.py         # Position, Balance, Order
│   ├── user.py            # User model
│   ├── trade.py           # Trade model
│   └── strategy_spec.py   # Strategy specifications
│
├── services/              # Бизнес-логика
│   ├── sync_service.py    # ⭐ Cross-platform sync (iOS↔WebApp↔Bot)
│   ├── trading_service.py
│   ├── signal_service.py
│   ├── strategy_service.py
│   ├── license_service.py
│   └── notification_service.py
│
├── core/                  # Инфраструктура
│   ├── db_postgres.py     # PostgreSQL layer (1.8K строк) ⭐ MAIN DB
│   ├── cache.py           # Кеширование (TTL 30s)
│   ├── rate_limiter.py    # Rate limiting
│   └── exceptions.py      # Кастомные исключения
│
├── utils/                 # Утилиты
│   ├── formatters.py      # Форматирование цен/процентов
│   ├── validators.py      # Валидация данных
│   ├── crypto.py          # HMAC подписи
│   └── translation_sync.py # Синхронизация переводов
│
├── ios/                   # 📱 iOS приложение (Swift)
│   └── EnlikoTrading/
│       ├── App/
│       │   ├── EnlikoTradingApp.swift
│       │   ├── AppState.swift     # ⭐ Server sync
│       │   └── Config.swift
│       ├── Services/
│       │   ├── WebSocketService.swift  # ⭐ Sync messages
│       │   ├── NetworkService.swift
│       │   └── AuthManager.swift
│       ├── Views/                 # 12 SwiftUI views
│       └── Extensions/
│           └── Notification+Extensions.swift
│
├── translations/          # 15 языков (679 ключей каждый)
│   └── en.py              # REFERENCE файл
│
├── tests/                 # 778 тестов (pytest)
└── logs/                  # Логи
```

---

# 💾 БАЗА ДАННЫХ (PostgreSQL 14 - ONLY)

> **⚠️ КРИТИЧНО:** SQLite полностью удалён! PostgreSQL - единственная БД.
> Флаг `USE_POSTGRES` больше не существует - PostgreSQL используется всегда.

## 📦 Система миграций (NEW! Jan 23, 2026)

Проект теперь использует версионированную систему миграций:

```
migrations/
├── __init__.py
├── runner.py              # CLI для управления миграциями
└── versions/              # 18 миграционных файлов
    ├── 001_initial_users.py
    ├── 002_signals.py
    ├── 003_trade_logs.py
    ├── 004_active_positions.py
    ├── 005_strategy_settings.py
    ├── 006_payment_history.py
    ├── 007_email_users.py
    ├── 008_login_tokens.py
    ├── 009_pending_orders.py
    ├── 010_custom_strategies.py
    ├── 011_user_devices.py
    ├── 012_pending_inputs.py
    ├── 013_elc_token.py
    ├── 014_backtest_results.py
    ├── 015_ton_payments.py
    ├── 016_session_tokens.py
    ├── 017_marketplace_tables.py
    └── 018_user_activity_log.py   # ⭐ Cross-platform sync
```

### Команды миграций

```bash
# Проверить статус
python -m migrations.runner status

# Применить все миграции
python -m migrations.runner upgrade

# Откатить до версии N
python -m migrations.runner downgrade N

# Сбросить все миграции
python -m migrations.runner reset
```

### Структура файла миграции

```python
# migrations/versions/XXX_name.py
def upgrade(cur):
    """Apply migration"""
    cur.execute("""CREATE TABLE IF NOT EXISTS ...""")
    
def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS ... CASCADE")
```

### Таблица миграций

```sql
-- _migrations (создаётся автоматически)
CREATE TABLE _migrations (
    id          SERIAL PRIMARY KEY,
    version     TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    applied_at  TIMESTAMP DEFAULT NOW(),
    checksum    TEXT
);
```

## Connection Pool

```python
# core/db_postgres.py
psycopg2.pool.ThreadedConnectionPool(minconn=5, maxconn=50)
DATABASE_URL = "postgresql://elcaro:elcaro_prod_2026@127.0.0.1:5432/elcaro"
```

## SQLite Compatibility Layer

Для backward compatibility существует layer который автоматически конвертирует SQLite синтаксис:

```python
# core/db_postgres.py
class SQLiteCompatCursor:  # Конвертирует ? → %s плейсхолдеры
class SQLiteCompatConnection:  # Wrapper для seamless миграции
def _sqlite_to_pg(query):  # Автоматическая конвертация синтаксиса
```

## Multitenancy Architecture

### Позиции и сделки - полная 4D изоляция
Таблицы `active_positions` и `trade_logs` используют полную 4D изоляцию:

| Измерение | Значения | Описание |
|-----------|----------|----------|
| `user_id` | Telegram ID | Уникальный пользователь |
| `symbol` | BTCUSDT, ETHUSDT, etc. | Торговый инструмент |
| `exchange` | bybit, hyperliquid | Биржа |
| `account_type` | demo, real, testnet, mainnet | Тип аккаунта |

### Настройки стратегий - 4D схема (Jan 2026)
Таблица `user_strategy_settings` использует полную 4D схему:

| Измерение | Значения | Описание |
|-----------|----------|----------|
| `user_id` | Telegram ID | Уникальный пользователь |
| `strategy` | oi, scryptomera, scalper, elcaro, fibonacci, rsi_bb | Торговая стратегия |
| `side` | long, short | Направление сделки |
| `exchange` | bybit, hyperliquid | Биржа |

> **⚠️ ВАЖНО:** Каждая комбинация (user, strategy, side, exchange) имеет независимые настройки!
> Это позволяет иметь разные SL/TP/leverage для Bybit и HyperLiquid.

**Комбинации для позиций:**
- **Bybit:** demo, real, both (торгует на обоих)
- **HyperLiquid:** testnet, mainnet

## Основные таблицы

### users (главная таблица)
```sql
user_id            BIGINT PRIMARY KEY    -- Telegram ID
-- API Bybit
demo_api_key       TEXT
demo_api_secret    TEXT
real_api_key       TEXT
real_api_secret    TEXT
trading_mode       TEXT DEFAULT 'demo'   -- 'demo' | 'real' | 'both'
-- API HyperLiquid
hl_enabled         BOOLEAN DEFAULT FALSE
hl_testnet         BOOLEAN DEFAULT FALSE -- TRUE=testnet, FALSE=mainnet
hl_testnet_private_key     TEXT
hl_testnet_wallet_address  TEXT
hl_mainnet_private_key     TEXT
hl_mainnet_wallet_address  TEXT
-- Торговые настройки (глобальные, fallback)
exchange_type      TEXT DEFAULT 'bybit'  -- 'bybit' | 'hyperliquid'
percent            REAL DEFAULT 1.0
tp_percent         REAL DEFAULT 8.0
sl_percent         REAL DEFAULT 3.0
use_atr            INTEGER DEFAULT 1
leverage           REAL DEFAULT 10.0
-- DCA
dca_enabled        INTEGER DEFAULT 0
dca_pct_1          REAL DEFAULT 10.0
dca_pct_2          REAL DEFAULT 25.0
-- Доступ
is_allowed         INTEGER DEFAULT 0
is_banned          INTEGER DEFAULT 0
lang               TEXT DEFAULT 'en'
updated_at         TIMESTAMP DEFAULT NOW()
```

### user_strategy_settings (настройки по стратегиям) ⭐ 4D SCHEMA
```sql
-- PRIMARY KEY: (user_id, strategy, side, exchange)
-- 4D SCHEMA: Each combination has independent settings
user_id             BIGINT NOT NULL
strategy            TEXT NOT NULL         -- 'oi', 'scryptomera', 'scalper', 'elcaro', 'fibonacci', 'rsi_bb'
side                TEXT NOT NULL         -- 'long' | 'short'
exchange            TEXT NOT NULL         -- 'bybit' | 'hyperliquid'
settings            JSONB DEFAULT '{}'    -- Optional: additional per-side data
-- Per-side trading settings
percent             REAL                  -- Entry % of equity
tp_percent          REAL
sl_percent          REAL
leverage            INTEGER
use_atr             BOOLEAN DEFAULT FALSE
atr_periods         INTEGER
atr_multiplier_sl   REAL
atr_trigger_pct     REAL
atr_step_pct        REAL
order_type          TEXT DEFAULT 'market'
limit_offset_pct    REAL DEFAULT 0.1
direction           TEXT DEFAULT 'all'
-- DCA settings
dca_enabled         BOOLEAN DEFAULT FALSE
dca_pct_1           REAL DEFAULT 10.0
dca_pct_2           REAL DEFAULT 25.0
-- Position limits
max_positions       INTEGER DEFAULT 0
coins_group         TEXT DEFAULT 'ALL'
-- Context columns
trading_mode        TEXT DEFAULT 'demo'
account_type        TEXT DEFAULT 'demo'
enabled             BOOLEAN DEFAULT TRUE
updated_at          TIMESTAMP DEFAULT NOW()
```

> **⚠️ ВАЖНО:** 4D схема (актуально Jan 2026):
> - PRIMARY KEY = `(user_id, strategy, side, exchange)` — 4 измерения
> - LONG и SHORT имеют **отдельные строки** с независимыми настройками
> - Каждый side может иметь свой TP%, SL%, leverage, DCA и т.д.
> - Колонки `exchange`, `account_type` сохранены для будущего 4D расширения

### active_positions (открытые позиции)
```sql
-- PRIMARY KEY: (user_id, symbol, account_type)
user_id       BIGINT NOT NULL
symbol        TEXT NOT NULL
account_type  TEXT DEFAULT 'demo'    -- 'demo' | 'real' | 'testnet' | 'mainnet'
side          TEXT                   -- 'Buy' | 'Sell'
entry_price   REAL
size          REAL
strategy      TEXT
leverage      REAL
sl_price      REAL
tp_price      REAL
dca_10_done   INTEGER DEFAULT 0
dca_25_done   INTEGER DEFAULT 0
open_ts       TIMESTAMP DEFAULT NOW()
-- Indexes
idx_positions_user   (user_id)
idx_positions_symbol (symbol)
```

### trade_logs (история сделок)
```sql
id            SERIAL PRIMARY KEY
user_id       BIGINT NOT NULL
symbol        TEXT
side          TEXT
entry_price   REAL
exit_price    REAL
exit_reason   TEXT              -- 'TP', 'SL', 'MANUAL', 'ATR'
pnl           REAL
pnl_pct       REAL
strategy      TEXT
account_type  TEXT DEFAULT 'demo'
sl_pct        REAL
tp_pct        REAL
timeframe     TEXT
ts            TIMESTAMP DEFAULT NOW()
source        TEXT DEFAULT 'api'
-- Indexes
idx_trade_logs_user_ts      (user_id, ts DESC)
idx_trade_logs_strategy     (strategy, ts DESC)
idx_trade_logs_account      (account_type, ts DESC)
```

### Другие таблицы
| Таблица | Описание |
|---------|----------|
| signals | История сигналов |
| pending_limit_orders | Лимитные ордера |
| user_licenses | Лицензии пользователей |
| custom_strategies | Кастомные стратегии |
| strategy_marketplace | Маркетплейс стратегий |
| exchange_accounts | Подключённые биржи |
| elc_transactions | LYXEN token транзакции |

## Использование в коде

```python
# Все функции из db.py теперь PostgreSQL-only:
from db import get_user_field, set_user_field, add_active_position
# Внутри вызываются pg_* функции из core/db_postgres.py

# Прямой доступ к PostgreSQL
from core.db_postgres import get_pool, get_conn, execute, execute_one

# Context manager (РЕКОМЕНДУЕТСЯ)
from core.db_postgres import get_conn
with get_conn() as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = %s", (uid,))

# Или через execute() helper
from core.db_postgres import execute, execute_one
rows = execute("SELECT * FROM users WHERE is_allowed = %s", (1,))
user = execute_one("SELECT * FROM users WHERE user_id = %s", (uid,))
```

## Функции мультитенантности

```python
from core.db_postgres import (
    pg_get_user_trading_context,  # Контекст: exchange + account_type
    pg_get_active_account_types,  # Список аккаунтов для торговли
    pg_get_strategy_settings,     # Настройки стратегии (SIMPLIFIED - only user_id, strategy)
    pg_get_effective_settings,    # Эффективные настройки с side-specific
    pg_set_strategy_setting,      # UPSERT настройки
)

# Получить контекст пользователя
ctx = pg_get_user_trading_context(uid)
# {'exchange': 'bybit', 'account_type': 'demo', 'trading_mode': 'demo'}

# Получить настройки стратегии (exchange/account_type игнорируются - упрощённая схема)
settings = pg_get_strategy_settings(uid, 'oi')
# Возвращает long_* и short_* настройки для стратегии
```

---

# 🚀 DEPLOYMENT

## Сервер

| Параметр | Значение |
|----------|----------|
| **Host** | `ec2-3-66-84-33.eu-central-1.compute.amazonaws.com` |
| **IP** | `3.66.84.33` |
| **User** | `ubuntu` |
| **SSH Key** | `noet-dat.pem` (в корне проекта, НЕ в git!) |
| **Path** | `/home/ubuntu/project/elcarobybitbotv2/` |
| **Python** | `/home/ubuntu/project/elcarobybitbotv2/venv/bin/python` |
| **Service** | `elcaro-bot` (systemd) |
| **WebApp Port** | `8765` |
| **Production URL** | `https://enliko.com` |
| **API URL** | `https://enliko.com/api` |
| **Nginx Config** | `/etc/nginx/sites-enabled/enliko.com` |

## Деплой команды

```bash
# 1. SSH подключение
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com

# 2. Деплой
cd /home/ubuntu/project/elcarobybitbotv2
git pull origin main
sudo systemctl restart elcaro-bot

# 3. Логи
journalctl -u elcaro-bot -f --no-pager -n 100

# 4. Статус
sudo systemctl status elcaro-bot
```

## Production Domain

WebApp доступен через собственный домен с nginx + SSL:

```
https://enliko.com          # Main WebApp
https://enliko.com/api      # API endpoints
https://enliko.com/terminal # Trading terminal
```

**Конфигурация:**
- Nginx reverse proxy → localhost:8765
- SSL сертификаты в `/etc/ssl/enliko.com/`
- Конфиг: `/etc/nginx/sites-enabled/enliko.com`

> ⚠️ Cloudflare Tunnel больше не используется! Теперь production domain.

---

# 📋 ПАТТЕРНЫ РАЗРАБОТКИ

## Position Sizing (КРИТИЧЕСКИ ВАЖНО!)

```python
# calc_qty использует EQUITY (walletBalance), НЕ available!
# Это обеспечивает стабильный размер позиций независимо от открытых сделок

equity = await fetch_usdt_balance(uid, account_type=acc, use_equity=True)  # walletBalance
available = await fetch_usdt_balance(uid, account_type=acc, use_equity=False)  # свободные средства

# Формула calc_qty (НЕ использует leverage!):
risk_usdt = equity * (entry_pct / 100)
price_move = price * (sl_pct / 100)
qty = risk_usdt / price_move
```

⚠️ **Entry% ВСЕГДА от equity, НЕ от available!**

## Bot Handler Decorators

```python
@log_calls        # Логирование ошибок
@require_access   # Проверка доступа + @with_texts
async def cmd_something(update, ctx):
    t = ctx.t     # Переводы
    uid = update.effective_user.id
```

⚠️ **НЕ ставить `@with_texts` вместе с `@require_access`** - дублирование!

## Exchange Routing

```python
# Получить биржу пользователя
exchange_type = db.get_exchange_type(uid)  # 'bybit' | 'hyperliquid'

# Режим торговли Bybit
trading_mode = db.get_trading_mode(uid)    # 'demo' | 'real' | 'both'

# Unified order placement
await place_order_universal(uid, symbol, side, order_type, qty, ...)
```

## Bybit API v5 Trading Stop (CRITICAL!)

```python
# Обязательные параметры для /v5/position/trading-stop:
body = {
    "category": "linear",
    "symbol": symbol,
    "positionIdx": position_idx,           # REQUIRED! 0=one-way, 1=buy, 2=sell
    "tpslMode": "Full",                    # REQUIRED by Bybit v5!
    "takeProfit": str(tp_price),
    "tpTriggerBy": "MarkPrice",            # More reliable than LastPrice
    "stopLoss": str(sl_price),
    "slTriggerBy": "MarkPrice",            # More reliable than LastPrice
}
```

⚠️ **Ошибки при неправильных параметрах:**
- Без `tpslMode` → API error 10001 "invalid parameters"
- `LastPrice` триггер → может не сработать при волатильности
- Без `positionIdx` → не установится на правильную позицию

## Database Cache Invalidation

```python
# ВСЕГДА после изменения данных пользователя:
db.set_user_field(uid, "some_field", value)
db.invalidate_user_cache(uid)  # Обязательно!
```

## Account Type Normalization (CRITICAL!)

```python
# Когда trading_mode='both', функции API и DB получают account_type='both'
# НО 'both' - это КОНФИГУРАЦИЯ торговли, не валидный тип аккаунта для API!

# ВСЕГДА нормализуй 'both' с учётом биржи:
from db import _normalize_both_account_type
account_type = _normalize_both_account_type(account_type, exchange='bybit')
# Bybit: 'both' → 'demo'
# HyperLiquid: 'both' → 'testnet'

# Уже применено в:
# - bot.py: _bybit_request(), show_balance_for_account(), show_positions_for_account()
# - db.py: get_trade_stats(), get_rolling_24h_pnl(), get_active_positions()
# - webapp/api/trading.py: все 9 endpoints
# - webapp/api/users.py: test_bybit_api, get_strategy_settings
# - webapp/services_integration.py: get_positions_service, get_balance_service
# - bot_unified.py: get_balance_unified, get_positions_unified
```

⚠️ **При `trading_mode='both'`:**
- **Bybit:** По умолчанию показывается Demo аккаунт
- **HyperLiquid:** По умолчанию показывается Testnet
- Юзер переключает через кнопки Demo/Real (или Testnet/Mainnet)
- API не поддерживает mode='both' - только конкретный account_type

## HyperLiquid Credentials Architecture (IMPORTANT!)

```python
# НОВАЯ архитектура (multitenancy):
# - hl_testnet_private_key + hl_testnet_wallet_address  # Для testnet
# - hl_mainnet_private_key + hl_mainnet_wallet_address  # Для mainnet

# LEGACY архитектура (fallback):
# - hl_private_key + hl_wallet_address + hl_testnet (boolean)

# Правильный паттерн получения credentials:
def get_hl_credentials_for_account(hl_creds: dict, account_type: str) -> tuple:
    is_testnet = account_type in ("testnet", "demo")
    
    # Try new architecture first
    private_key = hl_creds.get("hl_testnet_private_key" if is_testnet else "hl_mainnet_private_key")
    
    # Fallback to legacy format
    if not private_key:
        private_key = hl_creds.get("hl_private_key")
        is_testnet = hl_creds.get("hl_testnet", False)
    
    return private_key, is_testnet

# ИСПОЛЬЗОВАТЬ В:
# - webapp/api/trading.py - _get_hl_credentials_for_account()
# - core/exchange_client.py - get_exchange_client()
# - bot.py - все HL endpoints
```

⚠️ **При добавлении новых HL endpoints:**
- ВСЕГДА использовать `account_type` для выбора testnet/mainnet ключа
- ВСЕГДА проверять оба формата (new + legacy fallback)
- НИКОГДА не использовать только `hl_private_key` напрямую

## Leverage Fallback

```python
# set_leverage() пробует: 50 → 25 → 10 → 5 → 3 → 2 → 1
# Для низколиквидных монет (PONKEUSDT max 5x) автоматически подберёт
await set_leverage(uid, symbol, 50, account_type)  # автоматический fallback
```

## Translations

**15 языков:** ar, cs, de, en, es, fr, he, it, ja, lt, pl, ru, sq, uk, zh

```python
# Добавить новый текст:
# 1. Добавить в translations/en.py (reference)
# 2. Проверить sync:
python3 utils/translation_sync.py --report
```

**Common button keys (added Jan 23, 2026):**
```python
# Все 15 языков теперь имеют:
'btn_back', 'btn_close', 'btn_cancel', 'btn_confirm',
'btn_refresh', 'btn_settings', 'btn_delete', 'btn_yes',
'btn_no', 'btn_prev', 'btn_next'
```

---

# ⌨️ KEYBOARD HELPERS (NEW!)

Централизованный модуль для создания кнопок клавиатуры:

```python
from keyboard_helpers import (
    btn_back, btn_close, btn_confirm, btn_cancel,
    btn_refresh, btn_settings, btn_yes, btn_no,
    btn_prev, btn_next, build_keyboard
)

# Использование
keyboard = build_keyboard([
    [btn_back(t), btn_close(t)],
    [btn_confirm(t)]
], t)
```

**Файл:** `keyboard_helpers.py` (370 строк)

---

# � CROSS-PLATFORM SYNC SYSTEM (NEW! Jan 25, 2026)

## Архитектура синхронизации

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   iOS App       │      │   WebApp        │      │ Telegram Bot    │
│                 │      │                 │      │                 │
│ WebSocketService│      │  users.py API   │      │   bot.py        │
│   + AppState    │      │  + websocket.py │      │   handlers      │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                        │                        │
         │   WS: exchange_switched, account_switched, settings_changed
         │                        │                        │
         └────────────────────────┴────────────────────────┘
                                  │
                      ┌───────────┴───────────┐
                      │    PostgreSQL         │
                      │  -------------------- │
                      │  user_activity_log    │
                      │  notification_queue   │
                      │  users (settings)     │
                      └───────────────────────┘
```

## Ключевые файлы

| Файл | Описание |
|------|----------|
| `services/sync_service.py` | Центральный сервис синхронизации (450 строк) |
| `webapp/api/activity.py` | REST API для истории активности (275 строк) |
| `webapp/api/websocket.py` | WebSocket sync handlers |
| `ios/.../WebSocketService.swift` | iOS WebSocket + WSSyncMessage |
| `ios/.../Notification+Extensions.swift` | iOS sync notifications |
| `migrations/versions/018_user_activity_log.py` | Таблицы для activity log |

## Таблица user_activity_log

```sql
CREATE TABLE user_activity_log (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    action_type     TEXT NOT NULL,       -- 'settings_change', 'trade', 'exchange_switch'
    action_category TEXT NOT NULL,       -- 'settings', 'trading', 'auth', 'exchange'
    source          TEXT NOT NULL,       -- 'ios', 'webapp', 'telegram', 'api'
    entity_type     TEXT,                -- 'strategy_settings', 'user_settings', 'position'
    old_value       JSONB,
    new_value       JSONB,
    telegram_notified   BOOLEAN DEFAULT FALSE,
    webapp_notified     BOOLEAN DEFAULT FALSE,
    ios_notified        BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

## Использование SyncService

```python
from services.sync_service import sync_service

# Логирование смены биржи
await sync_service.sync_exchange_switch(
    user_id=uid,
    source="webapp",  # или "telegram", "ios"
    old_exchange="bybit",
    new_exchange="hyperliquid"
)

# Логирование изменения настроек
await sync_service.sync_settings_change(
    user_id=uid,
    source="ios",
    setting_name="strategy_oi",
    old_value=None,
    new_value=str(settings)
)
```

## Activity API Endpoints

| Endpoint | Описание |
|----------|----------|
| `GET /api/activity/history` | Полная история с фильтрами |
| `GET /api/activity/recent` | Последние 10 активностей |
| `GET /api/activity/by-source/{source}` | Фильтр по ios/webapp/telegram |
| `GET /api/activity/settings-changes` | Только изменения настроек |
| `GET /api/activity/sync-status` | Статус доставки уведомлений |
| `POST /api/activity/trigger-sync` | Ручной запрос синхронизации |
| `GET /api/activity/stats` | Статистика по source/type/day |

## WebSocket Sync Messages

```json
// iOS → Server (WebSocketService.swift)
{
    "type": "exchange_switched",
    "source": "ios",
    "data": {
        "exchange": "hyperliquid",
        "timestamp": "2026-01-25T20:00:00Z"
    }
}

// Server → iOS (handleSyncMessage)
{
    "type": "settings_changed",
    "source": "webapp",
    "data": {
        "strategy": "oi",
        "setting": "tp_percent",
        "old_value": "5.0",
        "new_value": "8.0"
    }
}
```

## iOS Notification Names

```swift
// ios/EnlikoTrading/Extensions/Notification+Extensions.swift
extension Notification.Name {
    static let exchangeSwitched = Notification.Name("exchangeSwitched")
    static let accountTypeSwitched = Notification.Name("accountTypeSwitched")
    static let settingsChanged = Notification.Name("settingsChanged")
    static let syncRequested = Notification.Name("syncRequested")
}
```

## Graceful Fallbacks (Модульная независимость)

Каждый модуль работает **автономно**:

| Модуль | Автономная работа | При синхронизации |
|--------|-------------------|-------------------|
| **iOS App** | UserDefaults сохраняет локально | WS + REST sync при подключении |
| **WebApp** | REST API работает без бота | Логирует в activity_log |
| **Telegram Bot** | Полная функциональность без WebApp | Отправляет sync при доступности |
| **SyncService** | try/except на все операции | Не ломает основной функционал |

```python
# services/sync_service.py - graceful fallback pattern
try:
    from services.sync_service import sync_service
    asyncio.create_task(sync_service.sync_exchange_switch(...))
except Exception as e:
    logger.warning(f"Sync logging failed: {e}")
    # Основная операция продолжается без синхронизации
```

---

# 🔧 RECENT FIXES (Январь 2026)

### ✅ CRITICAL: Full Auth Flow Fix (Jan 29, 2026)
- **Проблема:** После регистрации iOS пользователь не мог войти в приложение
- **Причины найдены и исправлены:**
  1. **SQLiteCompatCursor bug:** `execute()` с RETURNING потреблял результат в `lastrowid`, `fetchone()` возвращал None
  2. **create_email_user() не делал commit:** Записи не сохранялись в БД
  3. **/me endpoint:** Использовал `get_all_user_credentials()` который НЕ возвращает `is_allowed`, `first_name`
- **Исправления:**
  1. **webapp/api/email_auth.py → create_email_user():**
     - Использует raw psycopg2 вместо SQLiteCompatCursor
     - Явный `pg_conn.commit()` после INSERT
     - `ON CONFLICT (email) DO UPDATE` для обновления существующих
     - Устанавливает `is_allowed = 1` для новых email юзеров
  2. **core/db_postgres.py → execute():**
     - Добавлен автоматический commit для INSERT/UPDATE/DELETE
     - Добавлена обработка ошибок с rollback
  3. **webapp/api/users.py → /me endpoint:**
     - Прямой SQL запрос для `first_name`, `last_name`, `is_allowed`, `leverage`, `lang`
     - `bool(user_row.get("is_allowed", 0))` для корректной конвертации 0/1 → false/true
- **Тестирование:**
  - ✅ POST /register → success
  - ✅ POST /verify → token + full user object
  - ✅ POST /login → token + user with is_allowed=true
  - ✅ GET /me → email, name, is_allowed=true
- **Commits:** `3ebf289`, `c519659`, `1dc7d74`

### ✅ FIX: iOS Registration Decoding Error (Jan 29, 2026)
- **Проблема:** "Decoding error: The data couldn't be read because it is missing" при регистрации/верификации
- **Причина:** iOS `User` struct имел `id: Int` как обязательное поле, но сервер возвращал только `user_id`
- **Исправления:**
  1. **iOS Models/Models.swift:**
     - Изменён `id: Int` → `private let _id: Int?` (optional)
     - Добавлено computed property: `var id: Int { userId ?? _id ?? 0 }`
     - Добавлены поля `name`, `isAdmin` которые сервер возвращает
     - Улучшен `displayName` с fallback на email
  2. **iOS AuthModels.swift:**
     - Добавлен `UserResponse` wrapper для `/me` endpoint (сервер возвращает `{"user": {...}}`)
  3. **iOS AuthManager.swift:**
     - `fetchCurrentUser` использует `UserResponse` wrapper
  4. **Server webapp/api/email_auth.py:**
     - `/verify` и `/login` теперь возвращают полный user object с `id` полем
     - Добавлена функция `get_email_user_by_id()`
  5. **Server webapp/api/users.py:**
     - `/me` endpoint возвращает полный user object с `id` полем
- **Результат:** iOS регистрация и логин работают корректно

### ✅ iOS Full Audit - All 40+ Files Verified (Jan 28, 2026)
- **Аудит:** Полная проверка всех Swift файлов iOS приложения
- **Результат:** **BUILD SUCCEEDED** - все файлы компилируются без ошибок
- **Проверенные компоненты (40 файлов):**
  - **App/** (3): EnlikoTradingApp, AppState, Config
  - **Services/** (12): NetworkService, AuthManager, TradingService, WebSocketService, LocalizationManager, StrategyService, AIService, ActivityService, GlobalSettingsService, ScreenerService, SignalsService, StatsService
  - **Views/** (22): 6 директорий с view файлами
  - **Models/** (2): Models, AuthModels
  - **Extensions/** (2): Color+Extensions, Notification+Extensions
  - **Utils/** (2): Utilities, ModernFeatures
- **Исправления подтверждены:**
  - DisclaimerView.swift → closures вместо @Binding ✅
  - NetworkService.swift → postIgnoreResponse() добавлен ✅
- **Архитектура верифицирована:**
  - Entry flow: EnlikoTradingApp → RootView → Disclaimer → Login → MainTabView
  - Network flow: AuthManager → NetworkService → JWT → WebSocket
  - Localization: 15 языков с RTL поддержкой
- **Команда сборки:** `xcodebuild -project EnlikoTrading.xcodeproj -scheme EnlikoTrading -destination 'platform=iOS Simulator,name=iPhone 16 Pro' build`

### ✅ FEAT: Deep Localization Audit & Full Sync (Jan 28, 2026)
- **Проблема:** 12 языков (DE/ES/FR/IT/JA/ZH/AR/HE/PL/CS/LT/SQ) были частично синхронизированы - отсутствовало 64-88 ключей
- **Причина:** Новые ключи (API settings, balance, positions, orders, exchange, disclaimers) не были добавлены во все языки
- **Решение:** Создан скрипт `add_en_keys_to_all.py` для автоматической синхронизации
- **Результат:** 
  - **EN (reference):** 658 ключей
  - **RU/UK:** 658 ключей ✅ Perfect sync
  - **DE/ES/FR/IT/JA/ZH/AR/HE/PL/CS/LT/SQ:** 956 ключей ✅ All EN keys + 298 legacy keys
- **Добавленные ключи (88 для DE/ES/FR/IT, 64 для остальных):**
  - API: `api_bybit_demo`, `api_bybit_real`, `api_hl_testnet`, `api_hl_mainnet`, `api_key_missing`, `api_settings_header`, `api_settings_info`
  - Balance: `balance_title`, `balance_demo`, `balance_real`, `balance_testnet`, `balance_mainnet`, `balance_margin_used`, `balance_unrealized`, `balance_today_pnl`, `balance_week_pnl`, `balance_empty`, `balance_error`, `balance_display`
  - Positions: `position_long`, `position_short`, `position_card`, `positions_empty`, `positions_page`, `close_position_confirm`
  - Orders: `orders_header`, `orders_empty`, `orders_pending`, `orders_cancelled_all`, `order_card`, `order_cancelled`
  - Buttons: `btn_bybit_demo`, `btn_bybit_real`, `btn_hl_testnet`, `btn_hl_mainnet`, `btn_close_pos`, `btn_cancel_order`, `btn_cancel_all`, `btn_modify_tpsl`, `button_ai_bots`, `button_help`, `button_language`, `button_portfolio`, `button_premium`, `button_screener`
  - Exchange: `exchange_header`, `exchange_bybit`, `exchange_hyperliquid`, `exchange_selected`
  - Execution: `execution_header`, `execution_confirm`, `execution_success`, `execution_failed`
  - Manual: `manual_order_header`, `manual_long`, `manual_short`, `manual_order_confirm`, `manual_order_success`, `manual_order_failed`
  - Market: `market_header`, `market_btc`, `market_eth`, `market_total_cap`, `market_fear_greed`, `market_last_update`
  - Other: `signal_header`, `spot_header`, `spot_dca_enabled`, `spot_dca_disabled`, `strategy_info`, `stats_disclaimer`, `terms_title`, `welcome_back`
- **Утилиты созданы:**
  - `translations/deep_audit.py` - глубокий аудит всех языков
  - `translations/sync_translations.py` - проверка синхронизации
- **Файлы backup сохранены:** `de_old_backup.py`, `es_old_backup.py`, `fr_old_backup.py`, `it_old_backup.py`
- **Синтаксис проверен:** Все 15 файлов компилируются без ошибок ✅

### ✅ FEAT: Partial Take Profit (Срез маржи) in 2 Steps (Jan 27, 2026)
- **Функционал:** Частичное закрытие позиции при достижении % прибыли в 2 шага
- **Per-Strategy/Side настройки:**
  - `partial_tp_enabled` - включить/выключить (по умолчанию OFF)
  - `partial_tp_1_trigger_pct` - % прибыли для Step 1 (default 2.0%)
  - `partial_tp_1_close_pct` - % позиции для закрытия в Step 1 (default 30%)
  - `partial_tp_2_trigger_pct` - % прибыли для Step 2 (default 5.0%)
  - `partial_tp_2_close_pct` - % позиции для закрытия в Step 2 (default 50%)
- **UI:** Добавлено в Per-Strategy Long/Short меню:
  - Кнопка toggle Partial TP ON/OFF
  - Кнопки настройки Step 1 и Step 2 (показываются только когда enabled)
  - Формат: "📊 Step 1: 30% @ +2.0%" / "📊 Step 2: 50% @ +5.0%"
- **Изменённые файлы:**
  - `bot.py` - UI меню, handler `strat_side_ptp:`, prompts
  - `core/db_postgres.py` - Partial TP в pg_get_strategy_settings, ALLOWED_FIELDS, BOOLEAN_FIELDS
  - `db.py` - Partial TP columns в _STRATEGY_DB_COLUMNS
  - `translations/en.py`, `translations/ru.py` - 15+ ключей перевода
  - `migrations/versions/019_partial_tp_settings.py` - новая миграция

### ✅ FEAT: Break-Even in Per-Strategy Menus (Jan 27, 2026)
- **Расширение:** BE теперь настраивается отдельно для Long/Short каждой стратегии
- **UI изменения:**
  - Добавлена секция BE в `get_strategy_side_keyboard()`
  - Кнопка toggle BE + кнопка Trigger % (при включённом BE)
  - CallbackQueryHandler pattern добавлен `strat_side_be:`
- **Файлы:** bot.py (+100 строк)

### ✅ FEAT: Break-Even (BE) Feature for All Strategies (Jan 26, 2026)
- **Функционал:** Перевод SL в безубыток когда прибыль достигает trigger %
- **Глобальные настройки:**
  - `be_enabled` - включить/выключить BE (по умолчанию OFF)
  - `be_trigger_pct` - % прибыли для активации BE (по умолчанию 1.0%)
- **UI:** Добавлено в Global Settings меню:
  - Кнопка toggle BE ON/OFF
  - Кнопка настройки BE Settings
  - Отображение статуса BE в меню
- **Логика мониторинга:**
  - Проверяет move_pct >= be_trigger_pct
  - Если SL ещё не на уровне entry → перемещает SL на entry
  - Кэш `_be_triggered` предотвращает повторные попытки
  - Уведомление пользователю о переводе в БУ
- **Изменённые файлы:**
  - `bot.py` - UI меню, callback handlers, логика в мониторинге (+180 строк)
  - `db.py` - BE колонки в _STRATEGY_DB_COLUMNS
  - `coin_params.py` - DEFAULT_BE_ENABLED, DEFAULT_BE_TRIGGER_PCT
  - `translations/en.py`, `translations/ru.py` - переводы BE
  - `migrations/versions/001_initial_users.py` - BE колонки в users
  - `migrations/versions/005_strategy_settings.py` - BE колонки в strategy_settings
- **Commit:** 6a59dac

### ✅ FEAT: Comprehensive 4D Schema Tests (Jan 27, 2026)
- **Добавлено:** 33 новых теста для проверки 4D схемы `(user_id, strategy, side, exchange)`
- **Новые файлы:**
  - `tests/test_4d_schema_strategy_settings.py` (630 строк) - 17 тестов
    - Test4DSchemaStructure - проверка PRIMARY KEY
    - TestSideSpecificSettings - раздельные настройки long/short
    - TestExchangeSpecificSettings - изоляция Bybit/HyperLiquid
    - TestSettingsRetrievalFormat - формат возвращаемых данных
    - TestMultiUserIsolation - изоляция между пользователями
    - TestStrategyDefaultsFallback - fallback на дефолты
    - TestATRSettings - настройки ATR
    - TestDCASettings - настройки DCA
  - `tests/test_4d_strategy_settings_updated.py` (545 строк) - 16 тестов
    - TestFieldNameParsing - парсинг имён полей
    - TestSetStrategySetting - UPSERT операции
    - TestGetStrategySettings - получение настроек
    - TestGetEffectiveSettings - эффективные настройки с side
    - TestExchangeIsolation - изоляция по биржам
    - TestMultiUserIsolation4D - полная 4D изоляция
    - TestStrategyFeaturesIntegration - интеграция с STRATEGY_FEATURES
- **Обновлено:** `tests/conftest.py` - PRIMARY KEY обновлён на 4D
- **Commits:** 0e8386a, 8805374

### ✅ FIX: Auto-Skip PostgreSQL Tests (Jan 27, 2026)
- **Проблема:** Тесты падали с ошибкой "database elcaro_test does not exist"
- **Решение:** Автоматический пропуск PostgreSQL тестов при отсутствии БД
- **Обновлено:** `tests/conftest.py`:
  - Добавлена функция `_is_postgres_available()` для проверки подключения
  - Добавлен `pytest_collection_modifyitems()` для автопропуска
  - 12 файлов тестов автоматически пропускаются без PostgreSQL
- **Результат:** 416 passed, 293 skipped (вместо 88 failed)
- **Commit:** 10c883b

### ✅ FIX: Pandas ImportOrSkip (Jan 27, 2026)
- **Проблема:** `test_backtester_comprehensive.py` падал без pandas
- **Решение:** `pd = pytest.importorskip("pandas")` вместо прямого импорта
- **Commit:** 10c883b

### ✅ MAJOR: iOS Full Localization - 15 Languages + RTL (Jan 26, 2026)
- **Проблема:** iOS приложение имело только английский язык, все строки hardcoded
- **Причина:** iOS не использовал систему переводов, только server имел 15 языков
- **Решение:** Создана Swift-native система локализации с bundled переводами
- **Новые файлы:**
  - `ios/EnlikoTrading/Services/LocalizationManager.swift` (808 строк):
    - AppLanguage enum (15 языков)
    - Bundled translations для всех языков
    - RTL detection для Arabic (ar) и Hebrew (he)
    - Синхронизация с сервером через POST /users/language
    - String.localized extension
    - RTLModifier ViewModifier
  - `ios/EnlikoTrading/Views/Settings/LanguageSettingsView.swift` (177 строк):
    - LanguageRow с флагами
    - CompactLanguagePicker для LoginView
    - LanguageGrid для Settings
- **Локализованные Views:**
  - MainTabView - tabs Portfolio, Trading, Market, Settings
  - PortfolioView - Balance, Positions, PnL labels
  - PositionsView - Side, Entry, Size, Leverage labels
  - StatsView - Trading Statistics title
  - ScreenerView - Crypto Screener title, search placeholder
  - AIView - AI Assistant title
  - SignalsView - Signals, All, Long, Short tabs
  - ActivityView - Activity, Recent, Settings labels
  - LoginView - Email, Password, Login/Register buttons + CompactLanguagePicker
  - SettingsView - Language selection menu
- **RTL Support:**
  - .withRTLSupport() modifier на root WindowGroup
  - Автоматическое зеркалирование UI для Arabic/Hebrew
- **Языки (15):** EN, RU, UK, DE, ES, FR, IT, JA, ZH, AR, HE, PL, CS, LT, SQ
- **Commits:** 1a8c9d7, 6b04bca

### ✅ FIX: Production Domain Migration from Cloudflare (Jan 28, 2026)
- **Проблема:** Клавиатура бота и некоторые ссылки всё ещё использовали старые Cloudflare URLs (*.trycloudflare.com)
- **Причина:** После перехода на production domain (enliko.com) не все места были обновлены
- **Исправленные файлы:**
  - `bot.py`: 
    - Изменён дефолт `WEBAPP_URL` с `http://localhost:8765` на `https://enliko.com`
    - Удалена legacy логика fallback на ngrok_url.txt (3 места)
  - `.env` (сервер): `WEBAPP_URL=https://enliko.com`
  - `start_bot.sh`: Уже использовал `https://enliko.com` ✅
  - `.github/copilot-instructions.md`: Обновлена документация
- **Результат:** Menu Button теперь ведёт на `https://enliko.com/terminal`, все ссылки актуальны
- **Commit:** pending

### ✅ CRITICAL: Multitenancy Audit Round 15 - Missing Exchange Filters (Jan 25, 2026)
- **Проблема:** Функции `get_pending_limit_orders()` и `was_position_recently_closed()` не фильтровали по exchange
- **Причина:** При добавлении multitenancy эти функции были пропущены
- **Исправленные файлы:**
  - `db.py`:
    - `get_pending_limit_orders(user_id, exchange="bybit")` - добавлен exchange параметр + фильтр во все 4 SQL запроса
    - `was_position_recently_closed(user_id, symbol, entry_price, seconds, exchange="bybit")` - добавлен exchange параметр
  - `bot.py`:
    - Line 14813: `get_pending_limit_orders(uid)` → `get_pending_limit_orders(uid, exchange=user_exchange)`
    - Line 16121: `get_pending_limit_orders(uid)` → `get_pending_limit_orders(uid, exchange=current_exchange)`
    - Line 14803: `was_position_recently_closed(...)` → добавлен `exchange=user_exchange`
    - Line 16251: `was_position_recently_closed(...)` → добавлен `exchange=current_exchange`
  - `webapp/api/trading.py`:
    - Line 781: Исправлена лишняя скобка в logger.info()
- **Результат:** Все multitenancy функции теперь корректно фильтруют по exchange
- **Общий итог аудита:** ~115 багов исправлено за 15 раундов

### ✅ FEAT: Cross-Platform Sync System (Jan 25, 2026)
- **Добавлено:** Полная кросс-платформенная синхронизация iOS ↔ WebApp ↔ Telegram
- **Файлы:**
  - `services/sync_service.py` - центральный сервис (450 строк)
  - `webapp/api/activity.py` - REST API для истории (275 строк)
  - `migrations/versions/018_user_activity_log.py` - таблицы БД
  - `ios/.../WebSocketService.swift` - WSSyncMessage + handlers
  - `ios/.../Notification+Extensions.swift` - sync notifications
  - `webapp/api/websocket.py` - exchange_switched, settings_changed handlers
  - `webapp/api/users.py` - sync_service интеграция в endpoints
  - `bot.py` - sync logging при смене биржи
- **Результат:** Изменения на любой платформе синхронизируются с остальными
- **Commit:** a075891

### ✅ FEAT: iOS Exchange Switcher with Server Sync (Jan 25, 2026)
- **Проблема:** iOS приложение не синхронизировало exchange/accountType изменения с сервером
- **Причина:** AppState сохранял только в UserDefaults (локально)
- **Исправленные файлы:**
  - `ios/EnlikoTrading/App/AppState.swift`:
    - Добавлен `syncExchangeWithServer(exchange:)` - PUT /users/exchange
    - Добавлен `syncAccountTypeWithServer(accountType:)` - PUT /users/switch-account-type
    - Добавлен `syncFromServer()` - GET /users/settings для загрузки настроек при логине
    - Добавлены структуры `ServerSettings`, `EmptyResponse`
  - `ios/EnlikoTrading/Services/AuthManager.swift`:
    - Добавлен вызов `AppState.shared.syncFromServer()` после fetchCurrentUser()
  - `ios/EnlikoTrading/Models/Models.swift`:
    - Добавлено поле `hlTestnet: Bool?` в User model
  - `webapp/api/users.py`:
    - `/me` endpoint теперь использует `db.get_exchange_type()` вместо legacy полей
    - Добавлен `hl_testnet` в ответ `/me`
    - `/settings` endpoint теперь возвращает `exchange_type`, `trading_mode`, `hl_testnet`
  - `webapp/services/exchange_validator.py`:
    - Исправлен выбор ключа с учётом `hl_testnet` флага
- **Результат:** iOS теперь синхронизирует exchange preferences с сервером
- **Commit:** 6deff34

### ✅ VERIFIED: WebSocket Exchange Support (Jan 25, 2026)
- **Проверка:** webapp/realtime/__init__.py уже имеет полную поддержку exchange
- **Существующие компоненты:**
  - `BybitWorker` и `HyperliquidWorker` - отдельные workers для каждой биржи
  - `_bybit_data`, `_hyperliquid_data` - раздельное хранение данных
  - `_active_connections['bybit']`, `_active_connections['hyperliquid']` - раздельные подключения
  - `register_client(ws, exchange)` - регистрация клиента по бирже
  - `snapshot_broadcaster('bybit'|'hyperliquid')` - broadcaster по бирже
- **Статус:** Уже реализовано, не требует изменений

### ✅ CRITICAL: Full Multitenancy Exchange Parameter Propagation (Jan 25, 2026)
- **Проблема:** Многие вызовы `get_trade_stats()`, `get_active_positions()`, `get_trade_stats_unknown()` не передавали `exchange` параметр
- **Причина:** При аудите 4D схемы (user_id, strategy, side, exchange) обнаружено ~15 мест без передачи exchange
- **Исправленные файлы:**
  - `bot.py` - 12 вызовов get_active_positions() с добавлением exchange=current_exchange/user_exchange
  - `bot.py` - 3 вызова get_trade_stats() с добавлением exchange=user_exchange
  - `bot.py` - 1 вызов get_trade_stats_unknown() с добавлением exchange
  - `core/db_async.py` - добавлен exchange параметр в async get_active_positions()
  - `webapp/api/trading.py` - добавлен exchange в get_trade_stats() вызов
  - `webapp/services_integration.py` - добавлен exchange параметр в get_trade_stats_service()
  - `tests/test_integration.py` - добавлен exchange в 3 теста add_active_position()
- **Ключевые места:**
  - Monitor loops: все 5 вызовов get_active_positions() теперь передают current_exchange
  - Stats handlers: cmd_trade_stats + on_stats_callback передают user_exchange
  - Close handlers: manual close + close all передают user_exchange
  - Stale cleanup: передаёт current_exchange
- **Результат:** Все запросы к БД теперь корректно фильтруют по exchange для 4D multitenancy
- **Commit:** pending

### ✅ CRITICAL: SQLite → PostgreSQL Migration for WebApp API (Jan 25, 2026)
- **Проблема:** 3 API файла (marketplace.py, admin.py, backtest.py) использовали sqlite3.connect вместо PostgreSQL!
- **Причина:** При миграции на PostgreSQL эти файлы были пропущены
- **Решение:**
  - Создан `webapp/api/db_helper.py` - centralized PostgreSQL compatibility layer
  - `get_db()` возвращает connection с автоматической конверсией ? → %s
  - `dict(row)` работает через RealDictCursor
  - `lastrowid` поддерживается через RETURNING id
- **Исправленные файлы:**
  - `marketplace.py`: 8 sqlite3.connect → get_db(), is_active=1 → is_active=TRUE
  - `admin.py`: 14 sqlite3.connect → get_db(), добавлены try-finally блоки
  - `backtest.py`: 16+ sqlite3.connect → get_db(), убраны CREATE TABLE в коде
- **Новая миграция:** `017_marketplace_tables.py` создаёт все недостающие таблицы:
  - strategy_marketplace, strategy_purchases, strategy_ratings
  - seller_payouts, licenses, strategy_deployments, live_deployments
- **Файлы:** 6 файлов изменено, 2 новых файла создано
- **Commit:** ea69741

### ✅ CRITICAL: Multitenancy Exchange Field Fix (Jan 24, 2026)
- **Проблема:** Несколько мест в коде НЕ передавали `exchange` при сохранении позиций и trade logs
- **Причина:** При добавлении multitenancy не были обновлены все вызовы `add_active_position()` и `log_exit_and_remove_position()`
- **Исправленные места:**
  - `bot.py` line 4917: DCA handler - добавлен `exchange="bybit"`
  - `bot.py` line 16116: pending orders monitor - добавлен `exchange=current_exchange`
  - `bot.py` line 16279: position detection monitor - добавлен `exchange=current_exchange`
  - `bot.py` line 12564: manual close - добавлен `exchange=ap.get("exchange") or "bybit"`
  - `bot.py` line 12739: close all - добавлен `exchange=ap.get("exchange") or "bybit"`
- **Результат:** Все позиции и trade logs теперь корректно сохраняют биржу для multitenancy фильтрации
- **Файл:** bot.py (5 изменений)

### ✅ CRITICAL: HyperLiquid Multitenancy Credentials Fix (Jan 24, 2026)
- **Проблема:** HL функции использовали устаревший `hl_creds["hl_private_key"]` вместо multitenancy credentials
- **Причина:** При добавлении multitenancy (testnet/mainnet ключи) не были обновлены все HL функции
- **Исправленные функции:**
  - `cmd_hl_balance` - добавлен network switcher + multitenancy
  - `cmd_hl_positions` - исправлена проверка credentials
  - `cmd_hl_orders` - исправлена проверка credentials
  - `cmd_hl_history` - добавлен network switcher + multitenancy
  - `on_hl_balance_callback` - NEW: обработчик переключения сети баланса
  - `on_hl_history_callback` - NEW: обработчик переключения сети истории
  - Исправлено 7 мест с `hl_creds["hl_private_key"]` → multitenancy pattern
- **Multitenancy паттерн:**
  ```python
  if is_testnet:
      hl_private_key = hl_creds.get("hl_testnet_private_key") or hl_creds.get("hl_private_key")
  else:
      hl_private_key = hl_creds.get("hl_mainnet_private_key") or hl_creds.get("hl_private_key")
  ```
- **Файл:** bot.py (+374 lines)
- **Commit:** fcb0513

### ✅ FIX: Unknown Strategy → Manual for External Positions (Jan 24, 2026)
- **Проблема:** Позиции открытые вручную на бирже записывались со `strategy='unknown'`
- **Решение:** Изменён fallback с "unknown" на "manual"
- **Файлы:**
  - `bot.py` line 16236: `final_strategy = detected_strategy or "manual"`
  - `sync_trade_history.py`: skip trades without detected strategy
- **База:** Удалено 8079 trades с strategy='unknown', обновлено 38 позиций на 'manual'

### ✅ FIX: trade_logs.qty Made Nullable (Jan 24, 2026)
- **Проблема:** trade_logs.qty был NOT NULL, но API sync не всегда имеет qty
- **Решение:** `ALTER TABLE trade_logs ALTER COLUMN qty DROP NOT NULL`
- **Файл:** migrations/versions/003_trade_logs.py

### ✅ MAJOR: Triacelo → Enliko Full Rebrand (Jan 24, 2026)
- **Изменения:**
  - Все упоминания Triacelo/triacelo/TRIACELO заменены на Enliko/enliko/LYXEN
  - Затронуто 48 файлов: HTML, JS, CSS, SVG, Python, MD
  - core.js: `Triacelo.apiGet()` → `Enliko.apiGet()` etc.
  - Логотипы, заголовки, футеры - везде Enliko
- **Файлы:** 48 файлов во всём проекте
- **Commit:** pending

### ✅ FIX: trade_logs Missing Signal Analytics Columns (Jan 24, 2026)
- **Проблема:** Ошибка "column oi_prev of relation trade_logs does not exist"
- **Причина:** Таблица trade_logs не имела 10 колонок для аналитики сигналов
- **Fix SQL:**
  ```sql
  ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS rsi REAL;
  ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS bb_hi REAL;
  ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS bb_lo REAL;
  ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS vol_delta REAL;
  ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS oi_prev REAL;
  ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS oi_now REAL;
  ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS oi_chg REAL;
  ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS vol_from REAL;
  ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS vol_to REAL;
  ALTER TABLE trade_logs ADD COLUMN IF NOT EXISTS price_chg REAL;
  ```
- **Результат:** trade_logs теперь 41 колонка, миграция 003 обновлена

### ✅ FEAT: Automatic Log Cleanup (Jan 24, 2026)
- **Изменения:**
  - Создан `/scripts/cleanup_logs.sh` на сервере
  - Удаление логов старше 7 дней
  - Автообрезка логов больше 50MB
  - Cron job: `0 3 * * *` (каждый день в 3:00 AM)
- **Результат:** Логи очищены с 72MB до 16MB

### ✅ FIX: Daily Error Notification Keys (Jan 24, 2026)
- **Изменения:**
  - Добавлены ключи daily_zero_balance, daily_api_keys_invalid, daily_connection_error, daily_margin_exhausted
  - Добавлены во все 15 языков переводов
- **Файлы:** все translations/*.py

### ✅ MAJOR: Menu Restructure + Bybit API Optimization (Jan 23, 2026)
- **Изменения:**
  - MenuButton теперь "💻 Terminal" → ведёт на `/terminal` (было Dashboard → `/dashboard`)
  - Keyboard реорганизована: 4 строки, Dashboard убран
  - Новая структура клавиатуры:
    ```
    Row 1: Portfolio, Positions, Orders
    Row 2: AI Bots, Market, History
    Row 3: PREMIUM, Lang, API Keys
    Row 4: [Exchange Status]
    ```
  - Добавлен `tpslMode: "Full"` в `set_trading_stop()` (REQUIRED by Bybit v5 API!)
  - Изменён TP/SL триггер с LastPrice на MarkPrice (более надёжно)
  - Добавлен `positionIdx` в `exchanges/bybit.py` set_take_profit/set_stop_loss
- **Файлы:** `bot.py`, `exchanges/bybit.py`
- **Commit:** cf21950

### ✅ MAJOR: Keyboard Helpers + Translation Optimization (Jan 23, 2026)
- **Изменения:**
  - Создан `keyboard_helpers.py` (370 строк) - centralized button factory
  - Добавлены common button translation keys во все 15 языков
  - Добавлены aliases в `db_elcaro.py`: `get_elc_transactions`, `disconnect_wallet`, `get_connected_wallet`
  - Исправлены hardcoded Russian strings в `exchange_ui.py` и `elcaro_bot_commands.py`
- **Файлы:** `keyboard_helpers.py` (NEW), `translations/en.py`, `translations/ru.py`, `db_elcaro.py`
- **Commit:** 65963de

### ✅ MAJOR: TON Blockchain Verification (Jan 23, 2026)
- **Изменения:**
  - Добавлена реальная верификация USDT Jetton transfers через TONAPI
  - Функция `verify_usdt_jetton_transfer()` в `webapp/api/ton_payments.py`
  - Проверяет: destination wallet, USDT amount, USDT Jetton contract, confirmations
- **Файл:** `webapp/api/ton_payments.py`
- **Commit:** cf842c7

### ✅ MAJOR: Unified CSS Design System (Jan 23, 2026)
- **Проблема:** Каждая HTML страница дублировала ~840 строк inline CSS с CSS variables
- **Решение:** Создана унифицированная CSS система
- **Файлы:**
  - `webapp/static/css/base.css` - Unified design tokens, CSS reset, компоненты (~320 lines)
  - `webapp/static/css/components/header.css` - Unified header component (~250 lines)
  - `webapp/static/css/terminal-layout.css` - Terminal page styles (~1100 lines)
  - `webapp/static/js/core.js` - API helpers, auth, theme, toast, formatting (~340 lines)
- **Изменения:**
  - Все CSS variables централизованы в base.css
  - Компоненты: buttons, cards, inputs, badges, utilities
  - core.js: `Triacelo.apiGet()`, `Triacelo.showToast()`, `Triacelo.formatCurrency()` etc.
- **Как использовать:**
  ```html
  <link href="/static/css/base.css" rel="stylesheet">
  <link href="/static/css/components/header.css" rel="stylesheet">
  <script src="/static/js/core.js"></script>
  ```
- **Commit:** 39dab58

### ✅ MAJOR: Database Migration System Created (Jan 23, 2026)
- **Проблема:** Отсутствовала система управления миграциями БД, схема создавалась хаотично
- **Решение:** Создана полноценная система миграций с 14 версионированными файлами
- **Файлы:**
  - `migrations/runner.py` - CLI для upgrade/downgrade/status/reset
  - `migrations/versions/001-014` - Миграции для всех таблиц
  - `scripts/data_migration.py` - Экспорт/импорт данных пользователей
- **Изменения:**
  - Все таблицы синхронизированы с `core/db_postgres.py`
  - Добавлены недостающие колонки в `active_positions` (size, open_ts, env, и др.)
  - Добавлены недостающие колонки в `pending_limit_orders` (status, expires_at, exchange)
  - Миграции записываются в таблицу `_migrations`
- **Результат:** База пересоздана, 12 пользователей мигрированы, 61 позиция активна
- **Commits:** 690ae61, 5d4db8a

### ✅ FIX: get_trade_stats_unknown Query Fix (Jan 22, 2026)
- **Проблема:** Кнопка "✋ Manual" в статистике показывала 0 сделок, хотя было 4000+ trades
- **Причина:** Функция `get_trade_stats_unknown()` искала `strategy IS NULL`, но все trades имели `strategy='unknown'` (строка)
- **Анализ данных:**
  - 10815 trades с `strategy='unknown'` от 15.01 (миграция PostgreSQL)
  - Текущие trades записываются корректно с правильными стратегиями
- **Файл:** `db.py` line 3327
- **Fix:** 
  ```python
  # Было:
  WHERE strategy IS NULL
  # Стало:
  WHERE (strategy IS NULL OR strategy IN ('unknown', 'manual'))
  ```
- **Commit:** 7aff25d

### ✅ FIX: Main Menu Keyboard Simplification (Jan 22, 2026)
- **Проблема:** Клавиатура была перегружена кнопками переключения бирж (🔄 Bybit, 🔄 HL)
- **Причина:** Отдельные кнопки для переключения бирж занимали место
- **Файлы:**
  - `bot.py` - `main_menu_keyboard()` упрощена:
    - Убраны кнопки 🔄 Bybit и 🔄 HL
    - Кнопка биржи теперь toggle: нажатие переключает между Bybit/HL
    - 4 строки вместо 5
    - Row 4: `[🟠 Bybit 🎮] [🔗 API Keys]` или `[🔷 HyperLiquid] [🔗 API Keys]`
- **Новое поведение:**
  - Нажатие на "🟠 Bybit 🎮" → переключает на HyperLiquid
  - Нажатие на "🔷 HyperLiquid" → переключает на Bybit
- **Commits:** 90bf521, 9b48838

### ✅ FIX: Missing get_user_field Function (Jan 22, 2026)
- **Проблема:** `AttributeError: module 'db' has no attribute 'get_user_field'`
- **Причина:** Функция вызывалась в bot.py но не была определена в db.py
- **Файлы:**
  - `db.py` - добавлена функция `get_user_field(user_id, field, default=None)`:
    ```python
    USER_FIELDS_WHITELIST = {"lang", "exchange_type", "trading_mode", ...}
    def get_user_field(user_id, field, default=None):
        if field not in USER_FIELDS_WHITELIST:
            return default
        # PostgreSQL query
    ```
  - `bot.py` - добавлен import `get_user_field` из db
- **Commit:** a3ebae4

### ✅ FIX: HyperLiquid API Settings Enhancement (Jan 22, 2026)
- **Проблема:** В меню HL API не было возможности переключить сеть и установить ключ
- **Файлы:**
  - `bot.py` - добавлены handlers:
    - `hl_api:testnet` - переключение на testnet
    - `hl_api:mainnet` - переключение на mainnet  
    - `hl_api:set_key` - установка private key для текущей сети
    - `hl_api:back` - возврат в главное меню API Settings
  - `bot.py` - добавлена функция `_refresh_hl_settings_inline()` для обновления UI
- **Commit:** 384f970

### ✅ CRITICAL: Full HyperLiquid Multitenancy Credentials Fix (Jan 22, 2026)
- **Проблема:** Все компоненты системы использовали legacy `hl_private_key` вместо новой архитектуры `hl_testnet_private_key` / `hl_mainnet_private_key`
- **Причина:** При добавлении новых полей в БД не были обновлены все места использования
- **Исправленные файлы (ПОЛНЫЙ список):**
  1. **webapp/api/trading.py** (15+ endpoints):
     - Добавлена функция `_get_hl_credentials_for_account(hl_creds, account_type)`
     - Исправлены: `/balance`, `/positions`, `/orders`, `/close`, `/close-all`
     - Исправлены: `/execution-history`, `/set-leverage`, `/cancel-order`, `/modify-tpsl`
     - Исправлены: `/exchange-status`, `_place_order_hyperliquid()`, `_set_leverage_for_symbol()`, `_place_single_order_hl()`
  2. **exchange_router.py**:
     - Добавлена функция `_get_hl_credentials_for_env(hl_creds, env)`
     - Исправлены: `_execute_hyperliquid()`, `_get_hl_balance()`, `_get_hl_positions()`, `set_leverage()`
  3. **core/exchange_client.py**:
     - `get_exchange_client()` теперь выбирает testnet/mainnet ключ по account_type
  4. **webapp/api/users.py**:
     - `has_key` и `configured` проверяют все 3 поля
     - Проверка при переключении на HL биржу
  5. **webapp/api/admin.py**:
     - `hl_configured` проверяет все 3 поля
- **Паттерн исправления:**
  ```python
  # Новая архитектура с fallback на legacy
  is_testnet = account_type in ("testnet", "demo")
  private_key = hl_creds.get("hl_testnet_private_key" if is_testnet else "hl_mainnet_private_key")
  if not private_key:
      private_key = hl_creds.get("hl_private_key")  # Legacy fallback
      is_testnet = hl_creds.get("hl_testnet", False)
  ```

### ✅ FIX: Strategy Settings Defaults (Jan 21, 2026)
- **Проблема #1:** `DEFAULT_HL_STRATEGY_SETTINGS` в db.py не содержал `manual` и `wyckoff` стратегии
- **Проблема #2:** `STRATEGY_SETTINGS_DEFAULTS` в db.py не содержал `manual` стратегию
- **Проблема #3:** `pg_get_strategy_settings()` не возвращал `direction` и `coins_group` поля
- **Файлы:**
  - `db.py` - добавлены `manual` и `wyckoff` в оба словаря дефолтов
  - `core/db_postgres.py` - добавлены поля в SELECT запрос

### ✅ FIX: is_bybit_enabled / is_hl_enabled Credential Checks (Jan 21, 2026)
- **Проблема:** `is_bybit_enabled()` возвращал True если флаг установлен, даже если нет credentials
- **Причина:** Проверялся только флаг `bybit_enabled=1`, но не наличие API ключей
- **Файлы:**
  - `db.py` - `is_bybit_enabled()` теперь проверяет: `demo_api_key OR real_api_key`
  - `core/db_postgres.py` - `pg_is_bybit_enabled()` аналогично
- **Результат:** Биржа считается включённой только если есть хотя бы один настроенный аккаунт

### ✅ FIX: Legacy Routing Missing live_enabled Check (Jan 19, 2026)
- **Проблема:** При `trading_mode='both'` сделки открывались ТОЛЬКО на Demo, хотя Real был настроен
- **Причина:** 
  1. `place_order_all_accounts()` использует `use_legacy_routing=True`
  2. Legacy routing формировал targets БЕЗ проверки `live_enabled`
  3. Но даже с `live_enabled=1`, стратегии имели `trading_mode='demo'` в `user_strategy_settings`
- **Файлы:**
  - `bot.py` (line ~5170) - добавлена проверка `live_enabled` в legacy routing:
    ```python
    live_enabled = get_live_enabled(user_id)
    if env == "live" and not live_enabled:
        continue  # Skip Real targets
    ```
- **Данные:** Обновлено 19 записей в `user_strategy_settings`:
  ```sql
  UPDATE user_strategy_settings SET trading_mode='global' 
  WHERE trading_mode IN ('demo', 'real') AND user.trading_mode='both';
  ```
- **Fix:** Теперь legacy routing корректно проверяет `live_enabled` и стратегии используют глобальный `trading_mode`
- **Commit:** 3e5b53d

### ✅ DATA: live_enabled Flag for Users (Jan 19, 2026)
- **Проблема:** Юзеры 511692487, 1240338409 имели `live_enabled=0` → Real не торговался
- **Fix SQL:**
  ```sql
  UPDATE users SET live_enabled=1 WHERE user_id IN (511692487, 1240338409);
  ```

### ✅ FEAT: HyperLiquid 'both' Mode Support (Jan 18, 2026)
- **Проблема:** `_normalize_both_account_type()` не учитывал HyperLiquid (testnet/mainnet)
- **Причина:** Функция всегда нормализовала 'both' → 'demo', но HL использует 'testnet'/'mainnet'
- **Файлы:**
  - `db.py` - обновлена `_normalize_both_account_type(account_type, exchange)`:
    - Bybit: 'both' → 'demo'
    - HyperLiquid: 'both' → 'testnet'
  - Все 5 вызовов в db.py обновлены для передачи exchange
  - `webapp/api/trading.py` - добавлен helper, обновлены 9 endpoints
  - `webapp/api/users.py` - добавлен helper, обновлены 2 endpoints
  - `webapp/services_integration.py` - добавлен helper, обновлены 2 сервиса
  - `bot_unified.py` - добавлен helper, обновлены 2 функции
- **Fix:** Теперь 'both' корректно нормализуется с учётом биржи
- **Commit:** cc580fa

### ✅ CRITICAL: 'both' Account Type Normalization (Jan 18, 2026)
- **Проблема:** При `trading_mode='both'` баланс показывал "💎 Real" но с данными Demo аккаунта!
- **Причина:** 
  1. `get_effective_trading_mode()` возвращал `'both'`
  2. UI: `if account_type == "demo"` → FALSE → показывал "💎 Real"
  3. API: `if account_type == "real"` → FALSE → fallback на Demo URL
  4. Результат: Demo данные с Real label!
- **Файлы:**
  - `bot.py` - нормализация 'both' → 'demo' в:
    - `_bybit_request()` (line 3909)
    - `show_balance_for_account()` (line 11094)
    - `show_positions_for_account()` (line 10258)
    - `show_positions_direct()` (line 11222)
    - `show_orders_for_account()` (line 9910)
  - `db.py` - добавлена функция `_normalize_both_account_type()` и применена в:
    - `get_user_credentials()` (line 318)
    - `get_trade_stats()` (line 3260)
    - `get_trade_logs_list()` (line 3403)
    - `get_rolling_24h_pnl()` (line 3476)
    - `get_trade_stats_unknown()` (line 3513)
    - `get_active_positions()` (line 2328)
  - `webapp/api/trading.py` - нормализация 'both' → 'demo' в:
    - `/balance`, `/positions`, `/orders`, `/trades`, `/stats`
    - `/execution-history`, `/cancel-all-orders`, `/strategy-settings`
  - `webapp/api/users.py` - нормализация в `/api-keys/bybit/test`, `/strategy-settings`
  - `webapp/services_integration.py` - `get_positions_service()`, `get_balance_service()`
  - `bot_unified.py` - `get_balance_unified()`, `get_positions_unified()`
- **Fix:** Теперь при `trading_mode='both'` показывается Demo по умолчанию с корректным label
- **Commits:** e87c1d8, ee48fce, 431c61f

### ✅ FIX: NameError in get_rolling_24h_pnl (Jan 18, 2026)
- **Проблема:** Today PnL показывал +0.00 USDT при наличии сделок
- **Причина:** `logger` не был определён → NameError → exception → return 0
- **Файл:** `db.py` line 3470
- **Fix:** `logger` → `_logger`
- **Commit:** 4847bf7

### ✅ FIX: Signal Skip Logging + Missing Coins in TOP_LIST (Jan 18, 2026)
- **Проблема:** Пользователи жаловались что сделки не открываются, но не было видно причину в логах
- **Причина:** 
  1. Логирование фильтрации сигналов было на уровне DEBUG (не видно в production)
  2. Многие активно торгуемые монеты (IPUSDT, AXSUSDT, WLDUSDT) отсутствовали в `symbols.txt`
  3. `coins_group` в настройках стратегии переопределял глобальный `coins` фильтр
- **Файлы:**
  - `bot.py` - изменено логирование с DEBUG на INFO для:
    - already has open position
    - position was recently closed  
    - has active orders
    - pending limit order
    - pyramid count
    - coins_group filter
  - `symbols.txt` - добавлено 20+ монет: IPUSDT, AXSUSDT, WLDUSDT, ZKUSDT, FILUSDT, etc.
- **Fix:** Теперь в логах чётко видно почему сигнал пропущен
- **Commit:** da091eb

### ✅ CRITICAL: Duplicate get_user_payments Function Removed (Jan 17, 2026)
- **Проблема:** Кнопка "Моя подписка" не работала - ошибка `column "payment_method" does not exist`
- **Причина:** Дублирующая функция `get_user_payments` в db.py:
  - Line ~4244: Правильная версия с колонками `payment_type`, `license_type`
  - Line ~5913: **СЛОМАННАЯ** версия с колонками `payment_method`, `plan_type` (не существуют!)
  - Python использует последнее определение → вызывалась сломанная версия
- **Файл:** `db.py` - удалена дублирующая функция (lines 5913-5936)
- **Fix:** Оставлена только правильная версия функции на line ~4244
- **Commit:** 2da097f

### ✅ FIX: Trading Statistics API Field Mapping (Jan 17, 2026)
- **Проблема:** Статистика торговли в WebApp показывала некорректные данные
- **Причина:** API `/stats` endpoint использовал неправильные имена полей:
  - `total_trades` вместо `total`
  - `win_rate` вместо `winrate`
- **Файлы:**
  - `webapp/api/trading.py` - исправлен маппинг полей в `/stats` endpoint
  - `db.py` - добавлены `best_pnl` и `worst_pnl` в `get_trade_stats()`
  - `db.py` - исправлен `get_trade_logs_list()` для получения exchange из БД
- **Fix:** Корректный маппинг полей + добавлены недостающие поля статистики
- **Commit:** 6aa2367

### ✅ FIX: SQLite Fallback Code Removed from WebApp (Jan 17, 2026)
- **Проблема:** В `/trades` endpoint остался obsolete SQLite fallback код
- **Файл:** `webapp/api/trading.py`
- **Fix:** Удалён SQLite fallback, оставлен только PostgreSQL код
- **Commit:** 6aa2367

### ✅ FIX: Strategy Validation Fallback (Jan 17, 2026)
- **Проблема:** Стратегии использовали "manual" как fallback вместо "unknown"
- **Файл:** `webapp/api/stats.py`
- **Fix:** Изменён fallback с "manual" на "unknown" для консистентности
- **Commit:** 6aa2367

### ✅ FIX: SQLiteCompatCursor Context Manager (Jan 15, 2026)
- **Проблема:** `execute()` функция падала с `AttributeError: __enter__` при использовании `RealDictCursor`
- **Причина:** `SQLiteCompatCursor` не имел методов `__enter__`/`__exit__` для context manager
- **Файл:** `core/db_postgres.py` lines 171-180
- **Fix:** Добавлены методы в `SQLiteCompatCursor`:
  ```python
  def __enter__(self):
      return self
  def __exit__(self, exc_type, exc_val, exc_tb):
      self.close()
      return False
  ```
- **Дополнительно:** Функция `execute()` теперь использует прямой доступ к pool для `RealDictCursor`

### ✅ FIX: Missing DB Columns Migration (Jan 15, 2026)
- **Проблема:** Production база имела устаревшую схему - отсутствовали колонки
- **Результат:** Бот падал при запуске с `column "X" does not exist`
- **Добавленные колонки:**
  - `pending_limit_orders`: `order_id`, `signal_id`
  - `user_licenses`: `is_active`, `end_date`, `start_date`, `license_type`, `created_by`, `notes`
  - `signals`: 13 колонок
  - `active_positions`: 15 колонок  
  - `trade_logs`: 6 колонок
  - `users`: 17 колонок
- **Fix:** Инкрементальные миграции через `ALTER TABLE ADD COLUMN IF NOT EXISTS`

### ✅ CRITICAL: Complete PostgreSQL Migration - SQLite Removed (Jan 15, 2026)
- **Проблема:** Проект использовал SQLite с условным переключением на PostgreSQL
- **Результат:** Полное удаление SQLite, PostgreSQL-ONLY архитектура
- **Изменения:**
  - `db.py` - удалено 1008 строк SQLite кода, `init_db()` теперь вызывает `pg_init_db()`
  - `core/db_postgres.py` - добавлен **SQLite Compatibility Layer** для backward compatibility:
    - `SQLiteCompatCursor` - конвертирует `?` → `%s` плейсхолдеры
    - `SQLiteCompatConnection` - wrapper для seamless миграции
    - `_sqlite_to_pg()` - автоматическая конвертация синтаксиса
  - `blockchain/db_integration.py` - переведён на PostgreSQL (SERIAL вместо AUTOINCREMENT)
  - Удалён `USE_POSTGRES` флаг - PostgreSQL теперь единственная БД
- **Архитектура:**
  1. `db.py` использует `get_conn()` из `core.db_postgres` 
  2. Все SQLite-style запросы (`?` placeholders) автоматически конвертируются в PostgreSQL (`%s`)
  3. `init_db()` делегирует на `pg_init_db()` с полной PostgreSQL схемой
- **Environment:** PostgreSQL обязателен (SQLite больше не поддерживается)

### ✅ MAJOR: SQLite → PostgreSQL Full Schema Migration (Jan 15, 2026)
- **Проблема:** SQLite не поддерживает высокую конкурентность для 10K+ юзеров
- **Результат:** Полная миграция на PostgreSQL 14
- **Файлы:**
  - `core/db_postgres.py` - PostgreSQL layer (1.8K строк с compatibility layer)
  - `db.py` - PostgreSQL-only (удалён SQLite код)
  - `services/strategy_service.py` - PostgreSQL support
  - `services/strategy_marketplace.py` - PostgreSQL support
  - `webapp/api/trading.py` - PostgreSQL support
  - `db_elcaro.py` - PostgreSQL support
- **Fix:**
  1. `psycopg2.pool.ThreadedConnectionPool(minconn=5, maxconn=50)`
  2. SQLite Compatibility Layer для существующего кода
  3. Multitenancy: PRIMARY KEY `(user_id, strategy, exchange, account_type)`
- **Environment:** PostgreSQL обязателен (SQLite больше не поддерживается)

### ✅ Position Sizing: Equity vs Available (Jan 6, 2026)
- **Проблема:** calc_qty использовал available (свободные средства) вместо equity
- **Результат:** Размер позиций скакал от 282 до 4284 USDT при одинаковом entry%
- **Файл:** `bot.py` lines 7796-7840, 11959-12000
- **Fix:** `fetch_usdt_balance(use_equity=True)` возвращает walletBalance
- **Логика:** Entry% всегда считается от общего капитала
- **Commit:** d111612

### ✅ Leverage saved in add_active_position (Jan 6, 2026)
- **Проблема:** Leverage никогда не сохранялся в add_active_position
- **Файл:** `bot.py` - 4 места вызова add_active_position
- **Fix:** Добавлен параметр leverage во все вызовы
- **Commit:** 0af4baa

### ✅ PnL Display: Price Change vs ROE (Jan 6, 2026)
- **Проблема:** Показывался ROE (price_change * leverage) но calc_qty не использует leverage
- **Файл:** `bot.py` line ~14150
- **Fix:** Показываем price_change % (реальное изменение цены)
- **Commit:** 6d855a8

### ✅ Strategy Summary for Scryptomera/Scalper (Jan 6, 2026)
- **Проблема:** Scryptomera/Scalper не показывали общие настройки Entry/SL/TP%
- **Файл:** `bot.py` `_build_strategy_status_parts()` line ~5480
- **Fix:** Fallback на общие настройки если нет side-specific
- **Commit:** 3590005

### ✅ Leverage Fallback для низколиквидных монет (Jan 6, 2026)
- **Проблема:** PONKEUSDT (max 5x) не торговался
- **Fix:** `set_leverage()` пробует: 50→25→10→5→3→2→1
- **Commit:** aae2aa2

### ✅ КРИТИЧЕСКИЙ: Duplicate Trade Logs Fix (Jan 7, 2026)
- **Проблема:** 87.5% записей в trade_logs были дубликатами!
- **Причина:** Мониторинг цикл записывал одну закрытую позицию каждые ~25 секунд
- **Результат:** Статистика показывала PnL -$1.16M вместо реальных -$35K
- **Файлы:** 
  - `db.py` - добавлена проверка дубликатов в `add_trade_log()` (line ~3890)
  - `bot.py` - добавлен `_processed_closures` кэш в мониторинге (line ~13648)
- **Fix:** Двойная защита:
  1. БД: проверка дубликата перед INSERT (symbol+side+entry_price+pnl за 24ч)
  2. Мониторинг: `_processed_closures` кэш с 24ч cooldown
- **Дедупликация:** Удалено 50,153 дубликатов, осталось 6,426 реальных сделок
- **Commits:** b599281, a9cd4c3

### ✅ Bybit API 7-day Limit Fix (Jan 7, 2026)
- **Проблема:** `fetch_realized_pnl(days>7)` падал с ошибкой Bybit API
- **Причина:** Bybit ограничивает closed-pnl запрос максимум 7 днями
- **Файл:** `bot.py` line ~7500
- **Fix:** Разбиение запроса на 7-дневные чанки
- **Commit:** 5183a73

### ✅ Balance Loading Speed Optimization (Jan 8, 2026)
- **Проблема:** Кнопка "Баланс" грузилась 5-10 секунд (5 последовательных API запросов)
- **Причина:** `show_balance_for_account` делал запросы один за другим (sequential)
- **Файлы:** 
  - `bot.py` - `_fetch_balance_data_parallel()` (line ~10235)
  - `bot.py` - `fetch_account_balance()` (line ~7684)
  - `bot.py` - `handle_balance_callback()` (line ~10508)
- **Fix:** 
  1. `asyncio.gather()` для параллельного выполнения 5 запросов
  2. Убран дублирующий запрос USDT - извлекаем из основного ответа
  3. Добавлена спотовая статистика `fetch_spot_pnl()`
  4. Добавлен 5-минутный кеш для `week_pnl` (самый медленный запрос)
- **Результат:** Загрузка баланса **0.3-0.4 секунды** с кешем (было 6+ сек)

### ✅ Spot Trading Statistics Added (Jan 8, 2026)
- **Проблема:** В балансе показывался только фьючерсный PnL, спот игнорировался
- **Файл:** `bot.py` - новая функция `fetch_spot_pnl()` (line ~10170)
- **Fix:** Добавлена строка "🛒 Spot (7d): X trades, $Y volume" в балансе
- **API:** `/v5/execution/list` с `category: "spot"`

### ✅ Full Performance Optimization (Jan 8, 2026)
- **Проблема:** Множество функций делали последовательные API запросы
- **Паттерн оптимизации:** `asyncio.gather()` + кеширование медленных запросов
- **Оптимизированные функции (bot.py):**
  - `_fetch_balance_data_parallel()` - 5 запросов параллельно
  - `fetch_realized_pnl()` - 5-минутный кеш для days>=7 (было 5-6 сек → 0 сек)
  - `cmd_account()` - 4 fetch запроса параллельно
  - `get_unrealized_pnl()` - параллельно для demo/real
  - `cmd_wallet()` - параллельный fetch wallet/balance/transactions
  - `on_wallet_cb()` - параллельный refresh
  - `on_stats_callback()` - параллельный unrealized_pnl + api_pnl
- **Оптимизированные функции (webapp):**
  - `screener_ws.py: update_market_data()` - 4 биржи параллельно (Binance, Bybit, OKX, HyperLiquid)
  - `marketplace.py: get_market_overview()` - BTC/ETH/tickers параллельно
  - `marketplace.py: get_symbol_data()` - ticker + klines параллельно
- **Результат:** Ускорение загрузки баланса **17x** (6.15s → 0.37s с кешем)

---

# � PRODUCTION SCALABILITY (10k+ Users)

## Архитектура для высокой нагрузки (Jan 19, 2026)

### ✅ Готовые компоненты

| Компонент | Настройка | Описание |
|-----------|-----------|----------|
| **PostgreSQL Pool** | `minconn=5, maxconn=50` | ThreadedConnectionPool достаточно для 10k+ |
| **Redis** | `max_connections=100` | Распределённый кеш и rate limiting |
| **Rate Limiting** | Token Bucket | Per-IP и per-endpoint лимиты |
| **Security Middleware** | HackerDetection | XSS, SQL injection, path traversal защита |
| **HTTP Sessions** | aiohttp | Connection pooling (100/30 per host) |
| **WebSocket** | Bybit/HL workers | Real-time data broadcasting |

### Uvicorn Workers Configuration

```bash
# Авто-определение по CPU (config/settings.py, start_bot.sh)
WORKERS = min(2 * CPU_CORES + 1, 8)

# Явная настройка через environment:
WEBAPP_WORKERS=8 ./start.sh
```

### Redis для Verification Codes

```python
# webapp/api/email_auth.py теперь использует Redis:
from core.redis_client import get_redis

# Verification codes хранятся в Redis (TTL 15 мин)
await redis.set_verification_code(email, data, ttl=900)

# С fallback на in-memory для single-worker режима
```

### Production Checklist (10k+ users)

```bash
# 1. Redis обязателен
redis-server --daemonize yes

# 2. PostgreSQL connection pool
DATABASE_URL="postgresql://user:pass@host:5432/db?pool_size=50"

# 3. Environment переменные
export ENV=production
export WEBAPP_WORKERS=8
export CORS_ORIGINS="https://yourdomain.com"
export SECRET_KEY=$(openssl rand -hex 32)
export REDIS_URL="redis://localhost:6379"

# 4. Uvicorn с workers
uvicorn webapp.app:app --host 0.0.0.0 --port 8765 \
  --workers 8 --limit-concurrency 500 --timeout-keep-alive 60
```

### WebSocket Connections (multi-worker issue)

⚠️ **Важно:** При multiple workers каждый worker имеет свой набор WebSocket соединений.

**Решение для production:**
1. Использовать Redis Pub/Sub для синхронизации между workers
2. Или использовать отдельный сервис для WebSocket (например, socket.io)

```python
# webapp/realtime/__init__.py уже использует:
# - _active_connections в памяти каждого worker
# - Для full production нужен Redis broadcaster (TODO)
```

### Мониторинг производительности

```bash
# Health check
curl http://localhost:8765/health

# PostgreSQL connections
SELECT count(*) FROM pg_stat_activity WHERE datname='elcaro';

# Redis info
redis-cli INFO clients
```

---

# �🔒 SECURITY FIXES (Январь 2026)

### 🔐 Security Audit Round 1 (Jan 9, 2026)

#### ✅ Race Condition in DB Transactions
- **Проблема:** Конкурентные транзакции могли привести к некорректным данным
- **Файл:** `db.py`
- **Fix:** `isolation_level="DEFERRED"` при создании соединения + `BEGIN EXCLUSIVE` для критических операций

#### ✅ Bare Exception Handling
- **Проблема:** 17 мест с `except:` или `except Exception:` без логирования
- **Файл:** `bot.py`
- **Fix:** Все исключения теперь логируются с `logger.exception()` или специфичными типами

#### ✅ fetchone() None Checks  
- **Проблема:** 15+ мест где `cursor.fetchone()` использовался без проверки на None
- **Файлы:** `db.py`, `bot.py`
- **Fix:** Добавлены проверки `if row:` перед обращением к результатам

#### ✅ Cache Thread Safety
- **Проблема:** Доступ к кэшу без синхронизации в многопоточной среде
- **Файл:** `db.py`
- **Fix:** Добавлены `threading.RLock()` для _user_cache и _cfg_cache

#### ✅ TOCTOU in ELC Purchase
- **Проблема:** Time-of-check to time-of-use уязвимость при покупке ELC токенов
- **Файл:** `db.py`
- **Fix:** `BEGIN EXCLUSIVE` транзакция для атомарной проверки и обновления баланса

#### ✅ Unsafe Dict Access
- **Проблема:** Обращение к ключам словаря без проверки существования
- **Файл:** `exchanges/bybit.py`
- **Fix:** Использование `.get()` с дефолтными значениями

### 🔐 Security Audit Round 2 (Jan 9, 2026)

#### ✅ CRITICAL: Hardcoded JWT Secret
- **Проблема:** JWT секрет был захардкожен в `start.sh`
- **Файл:** `start.sh`
- **Fix:** Генерация случайного секрета при первом запуске через `openssl rand -hex 32`

#### ✅ Path Traversal in Oracle CLI
- **Проблема:** Возможность чтения произвольных файлов через `../` в пути
- **Файл:** `oracle/cli.py`
- **Fix:** Whitelist `ALLOWED_ANALYSIS_DIRS` + `os.path.realpath()` валидация

#### ✅ MD5 Usage (Weak Hashing)
- **Проблема:** MD5 использовался для генерации ID отчётов
- **Файл:** `oracle/core.py`
- **Fix:** Заменён на SHA256: `hashlib.sha256().hexdigest()[:16]`

#### ✅ CORS Wildcard Default
- **Проблема:** CORS по умолчанию разрешал все origins (`["*"]`)
- **Файл:** `core/config.py`
- **Fix:** Дефолт изменён на `[]`, требуется явная настройка через env

#### ✅ Open Redirect Vulnerability
- **Проблема:** Редирект без валидации URL позволял фишинг-атаки
- **Файл:** `scan/config/views.py`
- **Fix:** Проверка что URL начинается с `/` и не с `//`

#### ✅ Dynamic Import Injection
- **Проблема:** `importlib.import_module(f"translations.{lang}")` без валидации
- **Файл:** `bot.py`
- **Fix:** Regex whitelist `VALID_LANG_PATTERN = r'^[a-z]{2}$'`

### 🔐 Security Audit Round 3 (Jan 9, 2026)

#### ✅ CRITICAL: IDOR in Blockchain Admin API
- **Проблема:** Admin endpoints принимали `admin_id` из URL/request body вместо JWT
- **Файл:** `webapp/api/blockchain.py`
- **Fix:** 
  - Создан `require_admin` dependency с JWT валидацией
  - `admin_id` извлекается только из verified JWT токена
  - Все admin endpoints (`/admin/*`) используют dependency injection

#### ✅ DoS via Unlimited Pagination
- **Проблема:** `limit` параметры в API без верхней границы
- **Файлы:** `webapp/api/strategy_marketplace.py`, `webapp/api/strategy_sync.py`
- **Fix:** Добавлены ограничения `Query(le=100)`, `Query(le=50)`

---

# 🛡️ SECURITY PATTERNS

## Обязательные паттерны при написании кода:

### 1. Валидация входных данных
```python
# ❌ ПЛОХО
lang = user_input
module = importlib.import_module(f"translations.{lang}")

# ✅ ХОРОШО
VALID_LANG_PATTERN = re.compile(r'^[a-z]{2}$')
if not VALID_LANG_PATTERN.match(lang):
    lang = "en"
module = importlib.import_module(f"translations.{lang}")
```

### 2. Path Traversal Protection
```python
# ❌ ПЛОХО  
with open(f"./data/{user_path}") as f:
    data = f.read()

# ✅ ХОРОШО
ALLOWED_DIRS = ["/app/data", "/app/reports"]
real_path = os.path.realpath(os.path.join(base_dir, user_path))
if not any(real_path.startswith(d) for d in ALLOWED_DIRS):
    raise ValueError("Invalid path")
```

### 3. JWT-based Authorization
```python
# ❌ ПЛОХО - admin_id из request
@router.get("/admin/{admin_id}/data")
async def get_admin_data(admin_id: int):
    ...

# ✅ ХОРОШО - admin_id из JWT
async def require_admin(authorization: str = Header(...)) -> int:
    payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    if not payload.get("is_admin"):
        raise HTTPException(403, "Admin required")
    return payload["user_id"]

@router.get("/admin/data")
async def get_admin_data(admin_id: int = Depends(require_admin)):
    ...
```

### 4. Database Transaction Safety
```python
# ❌ ПЛОХО - race condition
balance = get_balance(user_id)
if balance >= amount:
    update_balance(user_id, balance - amount)

# ✅ ХОРОШО - atomic transaction
cursor.execute("BEGIN EXCLUSIVE")
cursor.execute("SELECT balance FROM users WHERE id=? FOR UPDATE", (user_id,))
balance = cursor.fetchone()[0]
if balance >= amount:
    cursor.execute("UPDATE users SET balance=balance-? WHERE id=?", (amount, user_id))
cursor.execute("COMMIT")
```

### 5. Exception Handling
```python
# ❌ ПЛОХО
try:
    do_something()
except:
    pass

# ✅ ХОРОШО
try:
    do_something()
except SpecificError as e:
    logger.exception(f"Failed to do_something: {e}")
    raise
```

---

# 🧪 ТЕСТИРОВАНИЕ

```bash
# Все тесты (708 тестов в коллекции)
python3 -m pytest tests/ -v

# Конкретный файл
python3 -m pytest tests/test_webapp.py -v

# С покрытием
python3 -m pytest tests/ --cov=. --cov-report=html

# Только unit тесты (без PostgreSQL)
SKIP_POSTGRES_TESTS=1 python3 -m pytest tests/ -v

# Полные интеграционные тесты (требует elcaro_test DB)
SKIP_POSTGRES_TESTS=0 python3 -m pytest tests/ -v
```

**Текущий статус (Jan 27, 2026):**
- **708 тестов** в коллекции
- **416 passed** (unit тесты без PostgreSQL)
- **293 skipped** (PostgreSQL интеграционные тесты)
- Автоматический пропуск PostgreSQL тестов если БД недоступна

**Тесты требующие PostgreSQL (автопропуск):**
```
test_webapp.py, test_autologin.py, test_full_strategy_trading.py,
test_routing_policy.py, test_strategy_settings.py, test_multi_user_integration.py,
test_multi_user_strategy_settings.py, test_positions_display.py,
test_strategy_settings_integration.py, test_integration.py, test_elcaro_parser.py
```

---

# 🔥 TROUBLESHOOTING

## "Conflict: terminated by other getUpdates"
```bash
pkill -9 -f 'python.*bot.py'
sleep 5
sudo systemctl restart elcaro-bot
```

## WebApp недоступен
```bash
curl localhost:8765/health
tail -20 logs/cloudflared.log
```

## Бот не запускается
```bash
journalctl -u elcaro-bot -n 100 --no-pager
```

## Позиции не закрываются
```bash
journalctl -u elcaro-bot | grep -i "ATR\|monitor" | tail -50
```

## Полезные команды для отладки
```bash
# Логи конкретного юзера
journalctl -u elcaro-bot | grep "USER_ID" | tail -50

# Ошибки в логах
journalctl -u elcaro-bot | grep -iE "error|exception|traceback" | tail -30

# calc_qty логи (размеры позиций)
journalctl -u elcaro-bot | grep "calc_qty" | tail -20

# ATR мониторинг
journalctl -u elcaro-bot | grep "ATR-CHECK\|ATR-TRAIL" | tail -30
```

---

# 📁 ИГНОРИРУЕМЫЕ ФАЙЛЫ

В корне проекта много старых MD файлов документации.

**Актуальная документация:**
- Этот файл (`.github/copilot-instructions.md`)
- `README.md` (базовый)

**Можно игнорировать:** Все `*_COMPLETE.md`, `*_REPORT.md`, `*_FIXED.md` файлы.

---

# 🔑 КЛЮЧЕВЫЕ КОНСТАНТЫ

| Константа | Файл | Значение |
|-----------|------|----------|
| `ADMIN_ID` | coin_params.py | 511692487 |
| `WEBAPP_PORT` | webapp/app.py | 8765 |
| `CACHE_TTL` | core/cache.py | 30 секунд |
| `POSITIONS_PER_PAGE` | bot.py | 10 |
| `LEVERAGE_FALLBACK` | bot.py | [50, 25, 10, 5, 3, 2, 1] |
| `VALID_LANG_PATTERN` | bot.py | `^[a-z]{2}$` |

---

# 🌐 MULTI-EXCHANGE SUPPORT

## Поддерживаемые биржи

| Биржа | Тип | Режимы | Файлы |
|-------|-----|--------|-------|
| **Bybit** | CEX | Demo, Real, Both | `exchanges/bybit.py`, `bot_unified.py` |
| **HyperLiquid** | DEX | Real only | `hl_adapter.py`, `hyperliquid/` |

## Роутинг между биржами
```python
# Получить активную биржу пользователя
exchange = db.get_exchange_type(uid)  # 'bybit' | 'hyperliquid'

# Роутинг через exchange_router.py
await place_order_universal(uid, symbol, side, ...)  # Автоматически выбирает биржу
```

## Cold Wallet Trading (HyperLiquid)
```python
# cold_wallet_trading.py
await connect_wallet(user_id, wallet_address, signature, message)
await prepare_hl_order(user_id, symbol, side, ...)  # Возвращает unsigned tx
await submit_signed_order(user_id, order_data, signature)  # Отправляет signed tx
```

---

# 💎 TON PAYMENT INTEGRATION (READY!)

## Текущий статус: ГОТОВО (Jan 23, 2026)

**Файлы:**
- `webapp/api/ton_payments.py` - API endpoints + verify_usdt_jetton_transfer()
- `ton_payment_gateway.py` - Gateway functions
- `bot.py` - UI кнопки оплаты
- `core/db_postgres.py` - таблица ton_payments

**Верификация:**
```python
async def verify_usdt_jetton_transfer(
    tx_hash: str,
    expected_amount: float,
    expected_destination: str,
    use_testnet: bool = False
) -> dict:
    # Реальная проверка через TONAPI
    # Проверяет: destination, amount, USDT contract, confirmations

**Файлы:**
- `webapp/api/ton_payments.py` - API endpoints (готово)
- `ton_payment_gateway.py` - verify функции (заглушки)
- `bot.py` - UI кнопки оплаты (готово)
- `core/db_postgres.py` - таблица ton_payments (готово)

## TODO (ожидаем ответ от разработчиков TON):

### 1. Настроить реальные кошельки
```python
# webapp/api/ton_payments.py, строка 32-33
"mainnet_wallet": "UQ_REAL_WALLET_HERE",  # <-- Заменить
"testnet_wallet": "kQ_TESTNET_WALLET_HERE",  # <-- Заменить
```

### 2. Реализовать verify_usdt_jetton_transfer()
```python
# ton_payment_gateway.py
async def verify_usdt_jetton_transfer(...)
    # TODO: Интеграция с TONAPI
    # Ждём от разработчиков: формат webhook, API ключ
```

### 3. Настроить webhook secret
```python
# webapp/api/ton_payments.py, строка 48
"webhook_secret": "your_webhook_secret_here",  # <-- Из .env
```

### 4. Переключить на mainnet
```python
# webapp/api/ton_payments.py, строка 45
"use_testnet": False,  # <-- Для продакшена
```

## Документация для разработчиков TON:
Файл: `docs/TON_INTEGRATION_ANSWERS.txt`

---

# 🚀 MODERN FEATURES (NEW: Jan 27, 2026)

## Топовые фичи мобильной разработки 2024-2026

Обе платформы (iOS + Android) теперь имеют следующие современные фичи:

### 1. Биометрическая аутентификация

| Платформа | Технология | Файл |
|-----------|------------|------|
| **iOS** | Face ID, Touch ID, Optic ID | `ios/.../Utils/ModernFeatures.swift` |
| **Android** | Fingerprint, Face, Iris | `android/.../util/BiometricAuth.kt` |

```swift
// iOS - BiometricAuthManager
let result = await BiometricAuthManager.shared.authenticate()
switch result {
case .success: grantAccess()
case .cancelled: showCancelMessage()
case .failed(let error): showError(error)
}
```

```kotlin
// Android - BiometricAuthManager
val result = biometricManager.authenticate(activity)
when (result) {
    is BiometricResult.Success -> grantAccess()
    is BiometricResult.Canceled -> showCancel()
    is BiometricResult.Error -> showError(result.errorMessage)
}
```

### 2. Haptic Feedback (Тактильная обратная связь)

| Тип | Использование |
|-----|---------------|
| `light` | Изменение цены |
| `medium` | Новый сигнал |
| `heavy` | Важное действие |
| `success` | Успешная сделка |
| `error` | Ошибка |
| `warning` | Предупреждение |
| `selection` | Выбор элемента |

```swift
// iOS
HapticManager.shared.tradeSuccess()
HapticManager.shared.priceChange()
```

```kotlin
// Android
hapticManager.tradeSuccess()
hapticManager.priceChange()
```

### 3. Advanced Animations

| Анимация | Описание |
|----------|----------|
| `PulsingAnimation` | Пульсирующий эффект для важных элементов |
| `SlideInFromBottom` | Появление модальных окон снизу |
| `ShakeAnimation` | Тряска для ошибок ввода |
| `AnimatedCounter` | Анимированный счётчик для PnL |
| `AnimatedPriceChange` | Цветовая анимация изменения цены |

### 4. Shimmer/Skeleton Loading

```swift
// iOS
PositionSkeletonCard()
ShimmerView(width: 100, height: 20)
```

```kotlin
// Android
ShimmerEffect(modifier = Modifier)
```

### 5. Offline-First Architecture

| Компонент | Описание |
|-----------|----------|
| `OfflineCache<T>` | Кеш данных с timestamp |
| `ConnectionState` | Состояние подключения |
| `isValid()` | Проверка актуальности кеша (5 мин) |

### 6. Adaptive Layout

| Тип устройства | Ширина (dp) |
|----------------|-------------|
| Phone Compact | < 360 |
| Phone Medium | 360 - 400 |
| Phone Expanded | 400 - 600 |
| Tablet | 600 - 840 |
| Desktop | > 840 |

### 7. Loading States

```kotlin
sealed class LoadingState<out T> {
    object Idle : LoadingState<Nothing>()
    object Loading : LoadingState<Nothing>()
    data class Success<T>(val data: T) : LoadingState<T>()
    data class Error(val message: String) : LoadingState<Nothing>()
    data class Progress(val percent: Int) : LoadingState<Nothing>()
}
```

### 8. Trading Celebration

Эффект празднования при закрытии профитной сделки:
- Анимация ✅ checkmark
- Haptic feedback (success)
- Auto-dismiss через 2 сек

### 9. Swipe Actions для позиций

| Направление | Действие |
|-------------|----------|
| Swipe Left | Закрыть позицию |
| Swipe Right | Добавить к позиции |

### 10. Pull-to-Refresh

Обновление данных свайпом вниз с анимацией загрузки.

## Файлы Modern Features

| Платформа | Файл | Строк |
|-----------|------|-------|
| **Android** | `util/ModernFeatures.kt` | ~350 |
| **Android** | `util/BiometricAuth.kt` | ~280 |
| **iOS** | `Utils/ModernFeatures.swift` | ~450 |

---

# 🤖 ANDROID РАЗРАБОТКА (Jan 27, 2026)

## Статистика Android приложения

| Метрика | Значение |
|---------|----------|
| Kotlin файлов | 30+ |
| Compose Screens | 9 (Portfolio, Trading, Signals, Market, Settings, AI, History, Auth, Main) |
| ViewModels | 8 |
| Languages | 15 (full parity with iOS/server) |
| RTL Support | Arabic (ar), Hebrew (he) |
| Android SDK | 35 (targetSdk) / 26 (minSdk) |
| Package | io.enliko.trading |
| Architecture | MVVM + Clean Architecture |
| DI | Hilt 2.53.1 |

## Структура Android проекта

```
android/EnlikoTrading/
├── settings.gradle.kts
├── build.gradle.kts
├── gradle/
│   ├── wrapper/gradle-wrapper.properties
│   └── libs.versions.toml          # Version catalog
├── gradlew, gradlew.bat
├── app/
│   ├── build.gradle.kts
│   ├── proguard-rules.pro
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── java/io/enliko/trading/
│       │   ├── EnlikoApplication.kt     # @HiltAndroidApp
│       │   ├── MainActivity.kt         # Entry point
│       │   ├── data/
│       │   │   ├── api/EnlikoApi.kt     # Retrofit API
│       │   │   ├── models/Models.kt    # Data classes
│       │   │   ├── repository/PreferencesRepository.kt
│       │   │   └── websocket/WebSocketService.kt
│       │   ├── di/NetworkModule.kt     # Hilt DI
│       │   ├── ui/
│       │   │   ├── components/CommonComponents.kt
│       │   │   ├── navigation/Navigation.kt
│       │   │   ├── screens/
│       │   │   │   ├── ai/             # AI Assistant
│       │   │   │   ├── auth/           # Login/Register
│       │   │   │   ├── history/        # Trade History
│       │   │   │   ├── main/           # Bottom Navigation
│       │   │   │   ├── market/         # Screener
│       │   │   │   ├── portfolio/      # Balance + Positions
│       │   │   │   ├── settings/       # Settings
│       │   │   │   ├── signals/        # Trading Signals
│       │   │   │   └── trading/        # Long/Short
│       │   │   └── theme/              # Material 3 Theme
│       │   └── util/Localization.kt    # 15 languages
│       └── res/
│           ├── values/strings.xml, colors.xml, themes.xml
│           ├── xml/backup_rules.xml, data_extraction_rules.xml
│           ├── drawable/               # Vector icons
│           └── mipmap-anydpi-v26/      # Adaptive icons
└── README.md
```

## Tech Stack

| Компонент | Версия |
|-----------|--------|
| Kotlin | 2.1.0 |
| Compose BOM | 2024.12.01 |
| Material 3 | Latest |
| Hilt | 2.53.1 |
| Retrofit | 2.11.0 |
| OkHttp | 4.12.0 |
| DataStore | 1.1.1 |
| Coil | 2.7.0 |
| Navigation Compose | 2.8.5 |

## Build Commands

```bash
# Debug build
cd android/EnlikoTrading
./gradlew assembleDebug

# Release AAB for Play Store
./gradlew bundleRelease

# Install on device
adb install app/build/outputs/apk/debug/app-debug.apk
```

## Screens Parity with iOS

| Screen | iOS | Android | Status |
|--------|-----|---------|--------|
| Portfolio | ✅ | ✅ | Full parity |
| Positions | ✅ | ✅ | Full parity |
| Trading | ✅ | ✅ | Full parity |
| Signals | ✅ | ✅ | Full parity |
| Market/Screener | ✅ | ✅ | Full parity |
| AI Assistant | ✅ | ✅ | Full parity |
| Settings | ✅ | ✅ | Full parity |
| History | ✅ | ✅ | Full parity |
| Login/Register | ✅ | ✅ | Full parity |

---

# � UNIFIED AUTH SYSTEM (NEW! Jan 29, 2026)

## Архитектура

Единая система аутентификации для всех 4 модулей:

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Telegram Bot    │    │    WebApp        │    │    iOS App       │    │   Android App    │
│   @EnlikoBot     │    │  enliko.com      │    │    SwiftUI       │    │  Jetpack Compose │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                       │                       │
         │    ┌──────────────────┴───────────────────────┴───────────────────────┘
         │    │
         ▼    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              PostgreSQL: users table                                    │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │ user_id | email | password_hash | telegram_username | auth_provider | is_allowed│   │
│  │ 511692  | NULL  | NULL          | @username         | telegram      | 1         │   │
│  │ -12345  | a@b.c | <hash>        | @linked_user      | both          | 1         │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────┐                                         │
│  │ telegram_user_mapping (for linked accts)  │                                         │
│  │ telegram_id → user_id                     │                                         │
│  └───────────────────────────────────────────┘                                         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

## Auth Providers

| Provider | Описание | user_id |
|----------|----------|---------|
| `telegram` | Пользователь из Telegram бота | Telegram ID (положительный) |
| `email` | Зарегистрирован через email | Сгенерированный (отрицательный) |
| `both` | Email юзер привязал Telegram | Сгенерированный (с маппингом) |

## Deep Link Login Flow

```
1. User in Telegram bot → /app_login
2. Bot generates one-time token → Redis (5 min TTL)
3. Bot sends deep link: enliko://login?token=XXX&tid=12345
4. User taps link → iOS/Android app opens
5. App calls POST /auth/telegram/deep-link
6. Server verifies token in Redis → deletes token (one-time use)
7. Server returns JWT token
8. User is logged in with same account as in bot
```

## API Endpoints

| Endpoint | Описание |
|----------|----------|
| `POST /auth/telegram/login` | Telegram Login Widget verification |
| `POST /auth/telegram/link` | Link Telegram to email account |
| `GET /auth/telegram/widget-params` | Get widget configuration |
| `POST /auth/telegram/deep-link` | Verify bot-generated one-time token |

## Ключевые файлы

| Файл | Описание |
|------|----------|
| `migrations/versions/020_unified_auth.py` | Миграция схемы |
| `webapp/api/telegram_auth.py` | API endpoints (415 строк) |
| `bot.py: cmd_app_login()` | /app_login command |
| `ios/.../AuthManager.swift` | handleURL(), loginWithDeepLink() |
| `ios/.../Info.plist` | URL scheme: enliko:// |

## URL Scheme (iOS)

```xml
<!-- Info.plist -->
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>enliko</string>
        </array>
    </dict>
</array>
```

## Bot Command

```
/app_login - Получить ссылку для входа в iOS/Android приложение
```

Генерирует inline keyboard с двумя кнопками:
- 📱 Открыть в приложении → `enliko://login?token=XXX&tid=12345`
- 🌐 Открыть в браузере → `https://enliko.com/auth/app-login?token=XXX&tid=12345`

---

# �📱 iOS РАЗРАБОТКА (UPDATED: Jan 28, 2026 - Full Audit)

## 🔍 iOS Full Audit Results (Jan 28, 2026)

### ✅ Build Status
- **Xcode Build:** SUCCESS ✅
- **Target:** iPhone 16 Pro Simulator
- **Configuration:** Debug
- **All 40+ Swift files compiled without errors**

### 🔧 Fixes Applied During Audit

| Issue | File | Fix |
|-------|------|-----|
| Generic type inference | DisclaimerView.swift | Changed `NetworkService.post()` → `postIgnoreResponse()` |
| Missing fire-and-forget POST | NetworkService.swift | Added `postIgnoreResponse()` method |
| Duplicate closing brace | DisclaimerView.swift | Removed extra `}` |
| Binding vs Closures mismatch | DisclaimerView.swift | Changed from `@Binding` to `onAccept`/`onDecline` closures |

### ✅ Verified Components (40 files)

| Category | Files | Status |
|----------|-------|--------|
| **App/** | EnlikoTradingApp, AppState, Config | ✅ All correct |
| **Services/** | NetworkService, AuthManager, TradingService, WebSocketService, LocalizationManager, StrategyService, AIService, ActivityService, GlobalSettingsService, ScreenerService, SignalsService, StatsService | ✅ All correct |
| **Views/Auth/** | LoginView, DisclaimerView | ✅ Fixed |
| **Views/Portfolio/** | PortfolioView, PositionsView, TradeHistoryView | ✅ All correct |
| **Views/Trading/** | TradingView, MarketView, SymbolPickerView | ✅ All correct |
| **Views/Settings/** | SettingsView, StrategySettingsView, TradingSettingsView, LanguageSettingsView, NotificationSettingsView, SubSettingsViews | ✅ All correct |
| **Views/Strategies/** | StrategiesView, BacktestView | ✅ All correct |
| **Views/** | MainTabView, AIView, ActivityView, ScreenerView, SignalsView, StatsView | ✅ All correct |
| **Models/** | Models, AuthModels | ✅ All correct |
| **ViewModels/** | ViewModels | ✅ All correct |
| **Extensions/** | Color+Extensions, Notification+Extensions | ✅ All correct |
| **Utils/** | Utilities, ModernFeatures | ✅ All correct |

### 🏗 Architecture Verified

```
Entry Flow:
EnlikoTradingApp (@main)
  └─ RootView
       ├─ DisclaimerView (if not accepted) → onAccept → onDecline
       ├─ LoginView (if not authenticated)
       └─ MainTabView (if authenticated)
              ├─ PortfolioView (Tab 0)
              ├─ TradingView (Tab 1)
              ├─ PositionsView (Tab 2)
              ├─ MoreView (Tab 3) → Strategies, Stats, Screener, AI, Signals, Activity
              └─ SettingsView (Tab 4)

Network Flow:
AuthManager → NetworkService → Config.apiURL (https://enliko.com/api)
           ↓
     JWT Token in Keychain
           ↓
     Auto-refresh on 401
           ↓
     WebSocketService.connectAll() on login

Localization Flow:
LocalizationManager.shared.currentLanguage
           ↓
     Bundled translations (15 languages)
           ↓
     String.localized extension
           ↓
     RTL auto-detection for ar/he
```

## Статистика iOS приложения

| Метрика | Значение |
|---------|----------|
| Swift файлов | 40+ |
| Views | 22 |
| Services | 12 |
| Languages | 15 (full parity with server) |
| RTL Support | Arabic (ar), Hebrew (he) |
| Xcode версия | 26.2 (17C52) |
| iOS Target | 26.2 |
| Bundle ID | io.enliko.EnlikoTrading |
| Team ID | NDGY75Y29A |
| Build Status | ✅ SUCCESS |

## Структура iOS проекта

```
ios/EnlikoTrading/
├── EnlikoTrading.xcodeproj
├── App/
│   ├── EnlikoTradingApp.swift       # @main entry + RTL support
│   ├── AppState.swift              # Global state + server sync
│   └── Config.swift                # API URLs (https://enliko.com)
├── Views/
│   ├── Auth/
│   │   ├── LoginView.swift         # Auth + CompactLanguagePicker
│   │   └── DisclaimerView.swift    # Legal disclaimer (closures) ✅FIXED
│   ├── Portfolio/
│   │   ├── PortfolioView.swift     # Balance, PnL (localized)
│   │   ├── PositionsView.swift     # Open positions (localized)
│   │   └── TradeHistoryView.swift  # Trade history
│   ├── Trading/
│   │   ├── TradingView.swift       # Order placement
│   │   ├── MarketView.swift        # Market data
│   │   └── SymbolPickerView.swift  # Symbol selection
│   ├── Settings/
│   │   ├── SettingsView.swift      # User settings + language picker
│   │   ├── StrategySettingsView.swift  # Long/Short per strategy
│   │   ├── TradingSettingsView.swift   # Trading preferences
│   │   ├── LanguageSettingsView.swift  # Full language selection UI
│   │   ├── NotificationSettingsView.swift
│   │   └── SubSettingsViews.swift
│   ├── Strategies/
│   │   ├── StrategiesView.swift
│   │   └── BacktestView.swift
│   ├── MainTabView.swift           # Tab navigation (5 tabs)
│   ├── StatsView.swift             # Trading statistics
│   ├── ScreenerView.swift          # Crypto screener
│   ├── AIView.swift                # AI assistant
│   ├── SignalsView.swift           # Trading signals
│   └── ActivityView.swift          # Cross-platform sync history
├── Services/
│   ├── NetworkService.swift        # HTTP + JWT auth + postIgnoreResponse ✅FIXED
│   ├── TradingService.swift        # Trading API calls
│   ├── WebSocketService.swift      # Real-time updates (market + sync)
│   ├── AuthManager.swift           # Auth state
│   ├── LocalizationManager.swift   # 15-language localization (1154 lines)
│   ├── StrategyService.swift       # Strategy settings API
│   ├── GlobalSettingsService.swift # Global settings API
│   ├── ScreenerService.swift       # Screener API
│   ├── AIService.swift             # AI chat API
│   ├── SignalsService.swift        # Signals API
│   ├── ActivityService.swift       # Activity sync API
│   └── StatsService.swift          # Statistics API
├── Models/
│   ├── Models.swift                # Position, Order, Balance, Trade, etc. (725 lines)
│   └── AuthModels.swift            # Login, Token, Register requests
├── ViewModels/
│   └── ViewModels.swift            # Observable objects
├── Extensions/
│   ├── Color+Extensions.swift      # Enliko color scheme
│   └── Notification+Extensions.swift # Sync notifications
├── Utils/
│   ├── Utilities.swift             # Formatters, helpers
│   └── ModernFeatures.swift        # Biometrics, Haptics, Animations
└── Assets.xcassets/
    └── AppIcon.appiconset/         # 1024x1024 icon
```

## 🌍 iOS Локализация (15 языков)

### Поддерживаемые языки

| Код | Язык | Флаг | RTL |
|-----|------|------|-----|
| en | English | 🇬🇧 | No |
| ru | Русский | 🇷🇺 | No |
| uk | Українська | 🇺🇦 | No |
| de | Deutsch | 🇩🇪 | No |
| es | Español | 🇪🇸 | No |
| fr | Français | 🇫🇷 | No |
| it | Italiano | 🇮🇹 | No |
| ja | 日本語 | 🇯🇵 | No |
| zh | 中文 | 🇨🇳 | No |
| ar | العربية | 🇸🇦 | **Yes** |
| he | עברית | 🇮🇱 | **Yes** |
| pl | Polski | 🇵🇱 | No |
| cs | Čeština | 🇨🇿 | No |
| lt | Lietuvių | 🇱🇹 | No |
| sq | Shqip | 🇦🇱 | No |

### Использование LocalizationManager

```swift
import SwiftUI

// Использование в View
Text("portfolio".localized)
Text("positions".localized)

// RTL поддержка (автоматически для ar/he)
.withRTLSupport()

// Смена языка
LocalizationManager.shared.currentLanguage = .arabic
// Автоматически синхронизируется с сервером через POST /users/language

// Доступ к языку
let lang = LocalizationManager.shared.currentLanguage  // AppLanguage enum
let isRTL = LocalizationManager.shared.isRTL          // Bool
```

### Добавление новых переводов

```swift
// LocalizationManager.swift
private static let translations: [AppLanguage: [String: String]] = [
    .english: [
        "portfolio": "Portfolio",
        "new_key": "New Text",  // <-- Добавить
    ],
    .russian: [
        "portfolio": "Портфель",
        "new_key": "Новый текст",  // <-- Добавить
    ],
    // ... для всех 15 языков
]
```

### RTL Modifier

```swift
// Автоматическое зеркалирование UI для Arabic/Hebrew
struct RTLModifier: ViewModifier {
    @ObservedObject var manager = LocalizationManager.shared
    
    func body(content: Content) -> some View {
        content
            .environment(\.layoutDirection, manager.isRTL ? .rightToLeft : .leftToRight)
    }
}

// Использование на root view (EnlikoTradingApp.swift)
WindowGroup {
    ContentView()
        .withRTLSupport()
}
```

### Синхронизация языка с сервером

```swift
// При смене языка автоматически вызывается:
private func syncLanguageWithServer(_ language: AppLanguage) {
    // POST /users/language { "language": "ru" }
    NetworkService.shared.post("/users/language", body: ["language": language.rawValue])
}
```

## iOS CLI команды

```bash
# Список доступных версий Xcode
xcodes list

# Установить Xcode
xcodes install "26.2"

# Проверить подключённые устройства
xcrun xctrace list devices

# Билд для устройства
cd ios/EnlikoTrading/EnlikoTrading
xcodebuild -project EnlikoTrading.xcodeproj \
  -scheme EnlikoTrading \
  -configuration Release \
  -destination generic/platform=iOS \
  build

# Создать архив для TestFlight
xcodebuild -project EnlikoTrading.xcodeproj \
  -scheme EnlikoTrading \
  -configuration Release \
  -destination generic/platform=iOS \
  -archivePath ./build/EnlikoTrading.xcarchive \
  archive

# Установить на iPhone через ios-deploy
ios-deploy --bundle /path/to/EnlikoTrading.app

# Открыть архив в Organizer
open ./build/EnlikoTrading.xcarchive
```

## Config.swift - API Endpoints

```swift
// Production domain - same for DEBUG and RELEASE
static let baseURL = "https://enliko.com"
static let apiURL = "\(baseURL)/api"
static let wsURL = "wss://enliko.com"
```

> ✅ **Production domain:** `https://enliko.com` - больше не меняется!

## Apple Developer Program

- **Цена:** $99/год
- **Возможности:** TestFlight, App Store, Push Notifications, In-App Purchases
- **Сертификаты:** Apple Development + Apple Distribution
- **Регистрация:** [developer.apple.com/programs/enroll](https://developer.apple.com/programs/enroll/)

## TestFlight Deployment

1. Создать App в App Store Connect (Bundle ID: io.enliko.EnlikoTrading)
2. Добавить аккаунт в Xcode → Settings → Accounts
3. Создать архив: `xcodebuild archive`
4. Открыть в Organizer: `open ./build/EnlikoTrading.xcarchive`
5. Distribute App → TestFlight & App Store → Upload

---

*Last updated: 29 января 2026*
*Version: 3.40.0*
*Database: PostgreSQL 14 (SQLite removed)*
*WebApp API: All files migrated to PostgreSQL (marketplace, admin, backtest)*
*Multitenancy: 4D isolation (user_id, strategy, side, exchange)*
*4D Schema Tests: 33 tests covering all dimensions*
*Security Audit: 14 vulnerabilities fixed*
*Tests: 750+ total (unit + integration + modern features + cross-platform)*
*TON Integration: READY (real verification)*
*HL Credentials: Multitenancy (testnet/mainnet separate keys)*
*Exchange Field: All add_active_position/log_exit calls pass exchange correctly*
*Main Menu: 4-row keyboard, Terminal button in MenuButton*
*Translations: 15 languages, 1540+ keys, common button keys*
*Branding: Enliko (renamed from Triacelo)*
*Log Cleanup: Cron daily at 3:00 AM, 7-day retention*
*Cross-Platform Sync: iOS ↔ WebApp ↔ Telegram Bot ↔ Android (user_activity_log table)*
*iOS SwiftUI: 40+ files, BUILD SUCCEEDED, full audit Jan 28 2026*
*iOS Features: Screener, Stats, AI, Signals, Activity, Strategies - full parity with WebApp*
*iOS Auth Flow: Full registration/login/verify tested Jan 29 2026 ✅*
*Android Kotlin: 30+ files, Jetpack Compose, Hilt DI, Material 3*
*Android Features: All 9 screens with ViewModels, WebSocketService, full iOS parity*
*Modern Features: Biometrics, Haptics, Animations, Shimmer, Offline-First, Adaptive Layout*
*Break-Even (BE): Per-strategy Long/Short settings*
*Partial Take Profit: Close X% at +Y% profit in 2 steps*
*Email Auth: register → verify → login → /me - all working correctly*
*Unified Auth: Telegram + Email + Deep Links - same account across all 4 modules (Bot, WebApp, iOS, Android)*
*Telegram Login: /app_login command generates one-time deep link for iOS/Android*
*URL Scheme: enliko://login?token=XXX&tid=12345 for native app login*
