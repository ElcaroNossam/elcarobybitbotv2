# ElCaro Trading Platform - AI Coding Guidelines
# =============================================
# Версия: 3.3.0 | Обновлено: 7 января 2026
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

## Статистика проекта (актуально на 06.01.2026)

| Метрика | Значение |
|---------|----------|
| Python файлов | 273 |
| HTML шаблонов | 36 |
| CSS файлов | 9 |
| JS файлов | 18 |
| Тестов | 664 |
| Языков перевода | 15 |
| Ключей перевода | 679 |

## Структура проекта

```
ElCaro Trading Platform
├── bot.py                 # 🔥 Главный бот (20218 строк, 241 функция)
├── db.py                  # 💾 SQLite database (6379 строк, 165 функций)
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

# 💾 БАЗА ДАННЫХ (SQLite)

## Основные таблицы

### users (главная таблица пользователей)
```sql
user_id            INTEGER PRIMARY KEY   -- Telegram ID
-- API ключи
demo_api_key       TEXT                  -- Bybit Demo API key
demo_api_secret    TEXT                  -- Bybit Demo API secret
real_api_key       TEXT                  -- Bybit Real API key
real_api_secret    TEXT                  -- Bybit Real API secret
trading_mode       TEXT DEFAULT 'demo'   -- 'demo' | 'real' | 'both'
-- Торговые настройки
percent            REAL DEFAULT 1.0      -- Entry % от баланса
tp_percent         REAL DEFAULT 8.0      -- Take Profit %
sl_percent         REAL DEFAULT 3.0      -- Stop Loss %
use_atr            INTEGER DEFAULT 1     -- 1=ATR trailing, 0=fixed
coins              TEXT DEFAULT 'ALL'    -- Разрешённые монеты
-- Стратегии
trade_scryptomera  INTEGER DEFAULT 0     -- Scryptomera вкл/выкл
trade_scalper      INTEGER DEFAULT 0     -- Scalper вкл/выкл
trade_elcaro       INTEGER DEFAULT 0     -- ElCaro AI вкл/выкл
trade_fibonacci    INTEGER DEFAULT 0     -- Fibonacci вкл/выкл
trade_oi           INTEGER DEFAULT 1     -- OI Strategy вкл/выкл
strategy_settings  TEXT                  -- JSON с настройками по стратегиям
-- DCA
dca_enabled        INTEGER DEFAULT 0     -- DCA вкл/выкл
dca_pct_1          REAL DEFAULT 10.0     -- 1й добор при -10%
dca_pct_2          REAL DEFAULT 25.0     -- 2й добор при -25%
-- Доступ
is_allowed         INTEGER DEFAULT 0     -- 1=одобрен админом
is_banned          INTEGER DEFAULT 0     -- 1=забанен
lang               TEXT DEFAULT 'en'     -- Язык интерфейса
```

### active_positions (открытые позиции)
```sql
user_id       INTEGER NOT NULL
symbol        TEXT NOT NULL
account_type  TEXT DEFAULT 'demo'    -- 'demo' | 'real'
side          TEXT                   -- 'Buy' | 'Sell'
entry_price   REAL
size          REAL
open_ts       DATETIME
strategy      TEXT                   -- Название стратегии
leverage      REAL                   -- Плечо (добавлено Jan 6, 2026)
sl_price      REAL                   -- Стоп-лосс
tp_price      REAL                   -- Тейк-профит
dca_10_done   INTEGER DEFAULT 0      -- 1й добор выполнен
dca_25_done   INTEGER DEFAULT 0      -- 2й добор выполнен
PRIMARY KEY(user_id, symbol, account_type)
```

### trade_logs (история сделок)
```sql
id              INTEGER PRIMARY KEY AUTOINCREMENT
user_id         INTEGER NOT NULL
symbol          TEXT
side            TEXT
entry_price     REAL
exit_price      REAL
exit_reason     TEXT              -- 'TP', 'SL', 'MANUAL', 'ATR'
pnl             REAL              -- Profit/Loss в USDT
pnl_pct         REAL              -- Profit/Loss в %
ts              DATETIME          -- Timestamp закрытия
strategy        TEXT              -- Название стратегии
sl_pct          REAL
tp_pct          REAL
timeframe       TEXT
```

### Другие таблицы
| Таблица | Описание |
|---------|----------|
| signals | История сигналов |
| pending_limit_orders | Лимитные ордера |
| user_licenses | Лицензии пользователей |
| custom_strategies | Кастомные стратегии |
| strategy_marketplace | Маркетплейс стратегий |
| user_strategy_settings | Настройки стратегий по юзерам |
| exchange_accounts | Подключённые биржи |
| connected_wallets | Крипто кошельки (для ELC) |

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

---

*Last updated: 6 января 2026*
*Version: 3.2.0*
*Tests: 664/664 passing*
