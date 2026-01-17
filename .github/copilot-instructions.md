# ElCaro Trading Platform - AI Coding Guidelines
# =============================================
# Версия: 3.9.0 | Обновлено: 17 января 2026
# =============================================

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

## Статистика проекта (актуально на 15.01.2026)

| Метрика | Значение |
|---------|----------|
| Python файлов | 273 |
| HTML шаблонов | 36 |
| CSS файлов | 9 |
| JS файлов | 18 |
| Тестов | 664 |
| Языков перевода | 15 |
| Ключей перевода | 679 |
| База данных | PostgreSQL 14 (ONLY) |
| Users | 12 |
| Active positions | 30 |
| Trade logs | 11,691 |

## Структура проекта

```
ElCaro Trading Platform
├── bot.py                 # 🔥 Главный бот (21748 строк, 250+ функций)
├── db.py                  # 💾 Database layer (PostgreSQL-ONLY, 6K строк)
├── bot_unified.py         # 🔗 Unified API Bybit/HyperLiquid (530 строк)
├── exchange_router.py     # 🔀 Роутинг между биржами (1140 строк)
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
│
├── models/                # Data models
│   ├── unified.py         # Position, Balance, Order
│   ├── user.py            # User model
│   ├── trade.py           # Trade model
│   └── strategy_spec.py   # Strategy specifications
│
├── services/              # Бизнес-логика
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
├── translations/          # 15 языков (679 ключей каждый)
│   └── en.py              # REFERENCE файл
│
├── tests/                 # 664 теста (pytest)
└── logs/                  # Логи
```

---

# 💾 БАЗА ДАННЫХ (PostgreSQL 14 - ONLY)

> **⚠️ КРИТИЧНО:** SQLite полностью удалён! PostgreSQL - единственная БД.
> Флаг `USE_POSTGRES` больше не существует - PostgreSQL используется всегда.

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

Система поддерживает полную изоляцию настроек по 4 измерениям:

| Измерение | Значения | Описание |
|-----------|----------|----------|
| `user_id` | Telegram ID | Уникальный пользователь |
| `strategy` | OI, Scryptomera, Scalper, ElCaro, Fibonacci | Торговая стратегия |
| `exchange` | bybit, hyperliquid | Биржа |
| `account_type` | demo, real, testnet, mainnet | Тип аккаунта |

**Комбинации:**
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

### user_strategy_settings (настройки по стратегиям) ⭐ MULTITENANCY
```sql
-- PRIMARY KEY: (user_id, strategy, exchange, account_type)
user_id             BIGINT NOT NULL
strategy            TEXT NOT NULL         -- 'OI', 'Scryptomera', etc.
exchange            TEXT DEFAULT 'bybit'  -- 'bybit' | 'hyperliquid'
account_type        TEXT DEFAULT 'demo'   -- 'demo' | 'real' | 'testnet' | 'mainnet'
enabled             BOOLEAN DEFAULT FALSE
percent             REAL                  -- Entry % для этой стратегии
sl_percent          REAL
tp_percent          REAL
leverage            REAL
use_atr             INTEGER
atr_periods         INTEGER
atr_multiplier_sl   REAL
atr_trigger_pct     REAL
order_type          TEXT DEFAULT 'market'
direction           TEXT DEFAULT 'all'    -- 'all' | 'long' | 'short'
-- Side-specific settings (Long/Short)
long_percent        REAL
long_sl_percent     REAL
long_tp_percent     REAL
short_percent       REAL
short_sl_percent    REAL
short_tp_percent    REAL
-- Metadata
created_at          TIMESTAMP DEFAULT NOW()
updated_at          TIMESTAMP DEFAULT NOW()
```

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
| elc_transactions | ELCARO token транзакции |

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
    pg_get_strategy_settings,     # Настройки с 4D fallback
    pg_get_effective_settings,    # Эффективные настройки с side-specific
    pg_set_strategy_setting,      # UPSERT настройки
)

# Получить контекст пользователя
ctx = pg_get_user_trading_context(uid)
# {'exchange': 'bybit', 'account_type': 'demo', 'trading_mode': 'demo'}

# Получить настройки стратегии с fallback
settings = pg_get_strategy_settings(uid, 'oi', exchange='bybit', account_type='demo')
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

## Cloudflare Tunnel

WebApp доступен через Cloudflare Quick Tunnel (URL меняется при рестарте!):

```bash
# Получить текущий URL
tail -20 /home/ubuntu/project/elcarobybitbotv2/logs/cloudflared.log | grep trycloudflare

# Обновить .env (БЕЗ рестарта бота!)
sed -i 's|WEBAPP_URL=.*|WEBAPP_URL=https://NEW-URL.trycloudflare.com|' .env
```

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

## Database Cache Invalidation

```python
# ВСЕГДА после изменения данных пользователя:
db.set_user_field(uid, "some_field", value)
db.invalidate_user_cache(uid)  # Обязательно!
```

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

---

# 🔧 RECENT FIXES (Январь 2026)

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

# 🔒 SECURITY FIXES (Январь 2026)

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
# Все тесты (664 теста)
python3 -m pytest tests/ -v

# Конкретный файл
python3 -m pytest tests/test_webapp.py -v

# С покрытием
python3 -m pytest tests/ --cov=. --cov-report=html
```

**Текущий статус: 664/664 tests passing ✅**

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

# 💎 TON PAYMENT INTEGRATION (IN PROGRESS)

## Текущий статус: ЗАГЛУШКИ

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

*Last updated: 17 января 2026*
*Version: 3.10.0*
*Database: PostgreSQL 14 (SQLite removed)*
*Multitenancy: 4D isolation (user_id, strategy, exchange, account_type)*
*Security Audit: 14 vulnerabilities fixed*
*Tests: 664/664 passing*
*TON Integration: In Progress (stubs)*
