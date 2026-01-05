# ElCaro Trading Platform - AI Coding Guidelines
# =============================================
# Версия: 3.0.0 | Обновлено: 6 января 2025
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

**Как обновлять:**
1. Добавить в секцию "Recent Fixes" с датой
2. Обновить номера строк если изменились
3. Добавить новые паттерны если появились

---

# 📊 АРХИТЕКТУРА ПРОЕКТА

## Общая структура

```
ElCaro Trading Platform
├── bot.py              # Главный бот (20000+ строк) - ВСЯ логика торговли
├── bot_unified.py      # Unified API для Bybit/HyperLiquid (5 функций)
├── db.py               # SQLite database (3800+ строк)
├── exchange_router.py  # Роутинг между биржами
├── hl_adapter.py       # HyperLiquid адаптер (41 метод)
├── coin_params.py      # Параметры монет, ADMIN_ID, лимиты
│
├── webapp/             # FastAPI веб-приложение
│   ├── app.py          # Main FastAPI app (port 8765)
│   ├── api/            # API роутеры (trading, stats, backtest...)
│   ├── templates/      # HTML шаблоны (dashboard, terminal...)
│   └── static/         # CSS/JS/Images
│
├── core/               # Инфраструктура
│   ├── cache.py        # Кеширование (TTL 30s)
│   ├── rate_limiter.py # Rate limiting для бирж
│   └── exceptions.py   # Кастомные исключения
│
├── services/           # Бизнес-логика (новый код)
│   ├── trading_service.py
│   └── signal_service.py
│
├── exchanges/          # Адаптеры бирж
│   ├── bybit.py        # BybitExchange (34 метода)
│   └── base.py         # Базовые классы
│
├── translations/       # 15 языков (651 ключ каждый)
│   └── en.py           # REFERENCE файл
│
├── models/             # Data models
│   └── unified.py      # Position, Balance, Order
│
├── tests/              # Тесты (pytest)
└── logs/               # Логи
```

## Ключевые файлы (номера строк актуальны на 06.01.2025)

### bot.py (~20000 строк)
| Секция | Строки | Описание |
|--------|--------|----------|
| Decorators | 375-520 | `@log_calls`, `@with_texts`, `@require_access` |
| API Settings | 791-1200 | Demo/Real ключи |
| set_leverage | 3321-3380 | Установка плеча с fallback 50→25→10→5→3→2→1 |
| place_order | 4850-5100 | Основная функция ордеров |
| Signal Parsing | 6000-7500 | Парсинг сигналов (scryptomera, scalper, elcaro) |
| Monitor Loop | 10893-11800 | Мониторинг позиций (TP/SL/ATR) |
| Handlers | 12000-20000 | Telegram handlers |

### db.py (~3880 строк)
| Секция | Строки | Описание |
|--------|--------|----------|
| Connection Pool | 17-120 | SQLite pool (10 connections) |
| User Management | 737-1260 | `get_user_config`, `set_user_field` |
| Credentials | 772-965 | API keys management |
| Positions | 1736-2280 | `add_active_position`, `get_active_positions` |
| Trade Logs | 2280-2500 | История сделок |

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

## SSH и деплой

```bash
# 1. Подключение
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com

# 2. На сервере
cd /home/ubuntu/project/elcarobybitbotv2
git pull origin main
sudo systemctl restart elcaro-bot

# 3. Проверка логов
journalctl -u elcaro-bot -f --no-pager -n 100
```

## Cloudflare Tunnel (WebApp)

WebApp доступен через Cloudflare Quick Tunnel:
- uvicorn на порту 8765
- cloudflared создаёт туннель
- URL в `.env` как `WEBAPP_URL`

### Обновление Cloudflare URL
```bash
# 1. Получить актуальный URL
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com \
  "cat /home/ubuntu/project/elcarobybitbotv2/logs/cloudflared.log | grep -oE 'https://[^[:space:]]+\.trycloudflare\.com' | tail -1"

# 2. Обновить .env и перезапустить
ssh -i noet-dat.pem ubuntu@ec2-3-66-84-33.eu-central-1.compute.amazonaws.com \
  "sed -i 's|WEBAPP_URL=.*|WEBAPP_URL=https://NEW-URL.trycloudflare.com|' /home/ubuntu/project/elcarobybitbotv2/.env && \
   sudo systemctl restart elcaro-bot"
```

---

# 🔧 RECENT FIXES (Январь 2025)

### ✅ Leverage Fallback для низколиквидных монет (Jan 6, 2025)
- **Проблема:** PONKEUSDT (max 5x) не торговался - "cannot set leverage [1000] gt maxLeverage [500]"
- **Файл:** `bot.py` lines 3321-3380
- **Fix:** `set_leverage()` теперь пробует: 50→25→10→5→3→2→1
- **Commit:** aae2aa2

### ✅ PnL Chart Race Condition (Jan 6, 2025)
- **Проблема:** График PnL не отображался, кнопки периодов не работали
- **Файл:** `webapp/templates/user/dashboard.html` line 1069
- **Fix:** `setTimeout(() => loadPnLData('30d'), 100)` + `let pnlChart`
- **Commit:** a7c954e

### ✅ Spot DCA PnL Calculation (Jan 5, 2025)
- **Проблема:** Spot DCA показывал unrealized_pnl = 0
- **Файл:** `bot.py` lines 11150-11200
- **Fix:** Расчёт PnL на основе avg_entry и current_price

### ✅ Rolling 24h Stats (Jan 5, 2025)
- **Проблема:** Статистика обновлялась только раз в день
- **Файлы:** `db.py`, `bot.py`, `webapp/api/stats.py`
- **Fix:** Теперь считает за последние 24 часа rolling

---

# 📋 ПАТТЕРНЫ РАЗРАБОТКИ

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

## Translations

**15 языков:** ar, cs, de, en, es, fr, he, it, ja, lt, pl, ru, sq, uk, zh

```python
# Добавить новый текст:
# 1. translations/en.py (reference)
# 2. Проверить sync:
python3 utils/translation_sync.py --report
```

---

# 🧪 ТЕСТИРОВАНИЕ

```bash
# Запуск тестов
python3 -m pytest tests/ -v

# Конкретный тест
python3 -m pytest tests/test_screener.py -v

# С покрытием
python3 -m pytest tests/ --cov=. --cov-report=html
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
sudo systemctl status nginx
```

## Бот не запускается
```bash
journalctl -u elcaro-bot -n 100 --no-pager
```

---

# 📊 СТРУКТУРА БАЗЫ ДАННЫХ

## Основные таблицы
- `users` - Все настройки пользователей, API ключи
- `active_positions` - Текущие открытые позиции
- `trade_logs` - История сделок с PnL
- `signals` - История сигналов
- `pending_limit_orders` - Лимитные ордера

## Ключевые поля users
- `api_key_demo`, `api_secret_demo` - Demo ключи Bybit
- `api_key_real`, `api_secret_real` - Real ключи Bybit
- `hl_private_key`, `hl_vault_address` - HyperLiquid
- `trading_mode` - 'demo' | 'real' | 'both'
- `exchange_type` - 'bybit' | 'hyperliquid'

---

# 📁 ИГНОРИРУЕМЫЕ ФАЙЛЫ

В корне проекта много старых MD файлов документации.
**Актуальная документация:**
- Этот файл (.github/copilot-instructions.md)
- README.md (базовый)
- TARGET_MODEL_ARCHITECTURE.md (модель Target)

**Можно игнорировать:** Все остальные *_COMPLETE.md, *_REPORT.md, *_FIXED.md файлы.

---

*Last updated: 6 января 2025*
*Version: 3.0.0*

### ✅ WebApp API Enrichment Fix (Dec 30, 2025)
- **Problem:** API returning `strategy: null`, `pnl: null` for positions
- **File:** `webapp/services_integration.py`
- **Fix:** `get_positions_service()` now enriches exchange data with DB data
- **Added Fields:**
  - `strategy` - from `db.get_active_positions()`
  - `account_type`, `env` - from request params
  - `tp_price`, `sl_price` - from DB or exchange
  - `use_atr`, `atr_activated` - ATR trailing stop state
- **Balance Fix:** Mapped `total_equity`→`equity`, `available_balance`→`available`

### ✅ Monitor Loop Multi-Exchange Fix (Dec 30, 2025)
- **Problem:** Stale positions not cleaned for demo accounts (only testnet)
- **File:** `bot.py` lines 10893-11799
- **Fix:** Critical indentation bug - cleanup code was OUTSIDE the account_type loop
- **Added:** `current_exchange` tracking alongside `current_account_type`
- **Notifications:** Now include exchange and market_type in open/close messages

### ✅ Position Notifications Enhanced (Dec 30, 2025)
- **Feature:** Exchange + market type in position notifications
- **Files:** `bot.py`, all 15 `translations/*.py`
- **Format:**
  ```
  🚀 New position BTCUSDT @ 94000, size=0.001
  📍 BYBIT • Demo
  
  🔔 Position BTCUSDT closed by *TP*:
  ...
  📍 BYBIT • Demo
  ```

### ✅ Screener Full Refactoring (Dec 23, 2025)
- **Feature:** Complete screener redesign with WebSocket real-time updates
- **Files:** `webapp/templates/screener.html`, `webapp/api/screener_ws.py`
- **What's New:**
  - Real-time market data from Binance (Futures + Spot)
  - 14 columns: Symbol, Price, 1m/5m/15m/1h/24h %, Vol 15m/1h, OI, OI Δ 15m, Funding, Volatility
  - Dynamic Futures/Spot switching with gradient buttons
  - WebSocket updates every 3 seconds
  - Improved `process_ticker()` with full timeframe calculations
  - Top Gainers/Losers sidebar
  - Beautiful gradient UI matching ElCaro design system
- **Tests:** `tests/test_screener.py` created with cache and fetcher tests
- **Status:** ✅ All CSS errors fixed, 102 core tests passing

### ✅ CSS Design System Fixed (Dec 23, 2025)
- **Problem:** CSS variables outside `:root` block causing 30+ errors
- **File:** `webapp/static/css/elcaro-design-system.css`
- **Fix:** All CSS variables moved inside `:root { }` block
- **Variables Added:**
  - Gradients: `--gradient-primary`, `--gradient-purple`, `--gradient-green`
  - Glow effects: `--glow-green`, `--glow-blue`, `--glow-purple`
  - Exchange colors: `--bybit-color`, `--hl-color`, `--binance-color`
  - Spacing, radius, shadows, transitions
- **Result:** 0 CSS errors, perfect syntax

### ✅ Unified Architecture Integration (Dec 23, 2024)
- **Feature:** Complete unified architecture for multi-exchange support
- **Files:** `models/unified.py`, `bot_unified.py`, `core/exchange_client.py`
- **What's New:**
  - Unified `Position`, `Balance`, `Order` models with `.from_bybit()` and `.from_hyperliquid()` converters
  - 5 main functions: `get_balance_unified()`, `get_positions_unified()`, `place_order_unified()`, `close_position_unified()`, `set_leverage_unified()`
  - All functions accept `exchange='bybit'` and `account_type='demo'` parameters
  - `fetch_open_positions()` in bot.py now uses unified architecture with field mapping
  - Proper `account_type` propagation through entire call chain
  - Full support for demo/real/testnet modes on both Bybit and HyperLiquid
- **Tests:** 13/13 passing in `tests/test_unified_models.py`
- **Feature Flag:** `USE_UNIFIED_ARCHITECTURE = True` in bot.py to enable (line ~120)

### ✅ Translation Sync (Dec 23, 2024)
- **Status:** All 15 languages perfectly synchronized (651 keys each)
- **Cleaned:** Removed obsolete keys (`elcaro_ai_note`, `elcaro_ai_params_*`, `lang_XX`)
- **Languages:** ar, cs, de, en, es, fr, he, it, ja, lt, pl, ru, sq, uk, zh
- **Command:** Use `python3 utils/translation_sync.py --report` to check status

### Position Close Strategy Detection
- **Problem:** "Position closed by UNKNOWN: Strategy: Unknown"
- **Fix:** Enhanced `detect_exit_reason()` at bot.py:2291 with fallback checks
- **Fix:** Added strategy parameter to `split_market_plus_one_limit()` and its `add_active_position()` call

### Elcaro Signal Parsing  
- **Problem:** Signals not being detected
- **Fix:** Made `ELCARO_RE_MAIN` regex more flexible (supports USDC, extra emojis)
- **Fix:** `is_elcaro_signal()` now requires core match + one additional indicator (more lenient)

### Positions Pagination
- **Change:** Now shows 10 positions per page instead of 1
- **New constant:** `POSITIONS_PER_PAGE = 10` at bot.py:6335
- **New functions:** `get_positions_list_keyboard()`, `format_positions_list_header()`
- **Handler:** `pos:list:{page}` for page navigation

### HyperLiquid Backend
- **Fix:** `place_order_hyperliquid()` now properly sets leverage BEFORE placing order
- **Fix:** TP/SL are set after successful order via `set_tp_sl()`
- **Fix:** `exchange_router.py` now uses correct response format (`retCode` for Bybit-like responses)
