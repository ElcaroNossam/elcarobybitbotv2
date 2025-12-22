# ElCaro Trading Platform - AI Coding Guidelines

> **CRITICAL:** Do NOT run `git push` - all changes are local only!

## ⚠️ Golden Rules (ОБЯЗАТЕЛЬНО!)

1. **НЕ УДАЛЯТЬ** критический код — только оптимизация и улучшения
2. **НЕ УПРОЩАТЬ** логику — сохранять всю существующую функциональность
3. **Production сервер:** `/home/ubuntu/project/elcarobybitbotv2/` (systemd service: `elcaro-bot`)
4. **На сервере есть другой проект `noetdat`** — НЕ трогать его, работать ТОЛЬКО с `elcarobybitbotv2`
5. При изменениях сначала тестировать локально, затем деплоить

## 🚀 Deployment Workflow

**Credentials:** `.server_credentials` (локально, НЕ в git)

### 1. Локальная разработка и тест
```bash
# Тестирование с локальным .env
./start.sh --bot        # Запустить бота
./start.sh --status     # Проверить статус
```

### 2. Деплой на сервер (после одобрения)
```bash
# SSH подключение
ssh -i rita.pem ubuntu@46.62.211.0

# На сервере:
cd /home/ubuntu/project/elcarobybitbotv2

# Pull изменений
git pull origin main

# Рестарт Cloudflare tunnel
sudo systemctl restart cloudflared

# Рестарт бота
sudo systemctl restart elcaro-bot

# Проверка статуса
sudo systemctl status elcaro-bot
journalctl -u elcaro-bot -f --no-pager -n 50
```

### 3. Откат при проблемах
```bash
git checkout HEAD~1 -- <file>
sudo systemctl restart elcaro-bot
```

## 🔧 Recent Fixes (December 2024)

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

## Architecture

Async Telegram trading bot + FastAPI webapp for dual-exchange (Bybit/HyperLiquid) crypto futures.

| Layer | Location | Purpose |
|-------|----------|---------|
| **Bot** | `bot.py` (~14K lines) | Telegram handlers, signal processing, Bybit API |
| **Services** | `services/` | Business logic: `ExchangeService`, `TradingService`, `SignalService` |
| **Core** | `core/` | Infrastructure: caching, rate limiting, connection pooling, metrics |
| **Database** | `db.py` | SQLite WAL with 10-conn pool, 30s config cache |
| **WebApp** | `webapp/` | FastAPI (port 8765): terminal, backtesting, AI agent |
| **Translations** | `translations/*.py` | 15 languages - **must sync all on changes** |
| **Screener** | `scan/` | Separate Django app for real-time crypto screener |
| **HyperLiquid** | `hl_adapter.py`, `hyperliquid/` | HL async client wrapper |
| **Router** | `exchange_router.py` | Universal order/position routing (Bybit ↔ HL) |

## Critical Patterns

### Bot Handler Decorators (ORDER MATTERS!)
```python
@log_calls        # Exception logging only (no entry/exit spam) - defined at bot.py:375
@require_access   # Checks banned/allowed + internally calls @with_texts - defined at bot.py:491
async def cmd_something(update, ctx):
    t = ctx.t     # Translation dict injected by @with_texts
    uid = update.effective_user.id
```
⚠️ **`@require_access` internally wraps with `@with_texts`** - don't stack both decorators

### Core Infrastructure Usage
```python
from core import (
    async_cached, user_config_cache, invalidate_user_caches,  # Caching
    bybit_limiter, hl_limiter,                                 # Rate limiting
    get_cached_client, on_credentials_changed,                 # Connection pool
    track_latency, count_errors, metrics                       # Metrics
)

@async_cached(user_config_cache, ttl=60)
async def get_settings(uid): ...

await bybit_limiter.acquire(user_id, "order")  # Before API calls
on_credentials_changed(user_id)                 # After credential updates
```

### Exchange Routing
```python
# User's active exchange - db.py:3339
db.get_exchange_type(uid)  # 'bybit' or 'hyperliquid'

# Bybit demo/real modes
db.get_trading_mode(uid)   # 'demo', 'real', or 'both'

# Universal order placement via exchange_router.py
await place_order_universal(uid, symbol, side, order_type, qty, ...)
```

### Services Layer Pattern
Services follow singleton pattern with lowercase instance exports:
```python
from services import trading_service, signal_service, exchange_service  # singletons
from services import TradingService, TradeRequest, TradeResult          # classes
```

## Developer Workflows

### Service Management
```bash
./start.sh --install     # First-time setup (install deps)
./start.sh               # Run all foreground (bot + webapp + screener)
./start.sh --daemon      # Background mode
./start.sh --status      # Check running services
./start.sh --restart     # Restart all
./start.sh --stop        # Stop all services
./start.sh --bot         # Start only bot
./start.sh --webapp      # Start only webapp
./start.sh --clean       # Clean caches and temp files
```

### Adding Bot Commands
1. Add handler in `bot.py` with `@log_calls @require_access`
2. Register: `app.add_handler(CommandHandler("cmd", handler))`
3. Add translation keys to ALL 15 `translations/*.py` files
4. Verify: `python -m utils.translation_sync --check`
5. Auto-fix missing: `python -m utils.translation_sync --fix`

### Adding Database Fields
1. Add `ALTER TABLE` migration to `init_db()` in `db.py`
2. Add field name to `USER_FIELDS_WHITELIST` (db.py:53)
3. Invalidate cache: `db.invalidate_user_cache(uid)`

### WebApp Development
- API routers in `webapp/api/` → mounted at `/api/{router_name}` (see `webapp/app.py:37-44`)
- Available routers: `auth`, `users`, `trading`, `admin`, `stats`, `backtest`, `ai`, `websocket`
- Templates in `webapp/templates/`, static in `webapp/static/`
- WebSockets in `webapp/api/websocket.py` → `/ws/*`
- Docs at `/api/docs` (Swagger), `/api/redoc`

## Key Files Reference

| File | Key Exports |
|------|-------------|
| `coin_params.py` | `ADMIN_ID`, `COIN_PARAMS`, `BLACKLIST`, `DEFAULT_TP_PCT`, `DEFAULT_SL_PCT` |
| `db.py` | `get_user_config`, `set_user_value`, `USER_FIELDS_WHITELIST`, `invalidate_user_cache` |
| `exchange_router.py` | `place_order_universal`, `fetch_positions_universal`, `set_leverage_universal`, `close_position_universal`, `get_balance_universal` |
| `hl_adapter.py` | `HLAdapter` (41 methods) - HyperLiquid async client wrapper |
| `exchanges/bybit.py` | `BybitExchange` (34 methods) - Bybit async client |
| `exchanges/base.py` | `BaseExchange`, `Balance`, `Position`, `Order`, `OrderResult`, `OrderSide`, `OrderType`, `PositionSide` |
| `services/exchange_service.py` | `ExchangeAdapter`, `BybitAdapter`, `HyperLiquidAdapter`, `OrderType`, `OrderSide` |
| `core/__init__.py` | All infrastructure exports: caching, rate limiting, metrics, exceptions |
| `core/exchange_client.py` | `UnifiedExchangeClient`, `ExchangeCredentials`, `ExchangeType`, `AccountMode` |

## After Code Changes
```bash
rm -rf __pycache__ */__pycache__ && ./start.sh --restart
```

## Translation Sync
```bash
python -m utils.translation_sync --report  # Status report
python -m utils.translation_sync --check   # CI validation
python -m utils.translation_sync --fix     # Add missing with English fallback
```
Languages: `ar, cs, de, en, es, fr, he, it, ja, lt, pl, ru, sq, uk, zh` (English is reference)

## Screener (scan/)
Separate Django app - see `scan/README.md`. Use `scan/install.sh` for setup.

---

# 📚 DETAILED PROJECT KNOWLEDGE BASE

## 🏗️ Project Structure Deep Dive

### Bot Core (bot.py ~14,200 lines)
Main Telegram bot with ALL trading logic, signals, and handlers.

**Key Function Groups:**
- **Lines 375-520**: Decorators (`log_calls`, `with_texts`, `require_access`)
- **Lines 791-1200**: API Settings handlers (Demo/Real keys management)
- **Lines 2247-2600**: Bybit API interactions (`set_leverage`, `_bybit_request`)
- **Lines 3016-3300**: Order placement logic (`split_market_plus_one_limit`)
- **Lines 3485-3790**: Core `place_order()` function
- **Lines 3682-3786**: HyperLiquid order placement
- **Lines 3888-5480**: Strategy settings handlers
- **Lines 5497-5650**: `/start` command and user onboarding

**Trading Strategies:**
- `scryptomera` - Crypto news sentiment
- `scalper` - Quick scalp trades
- `elcaro` - Main strategy
- `wyckoff` - Wyckoff methodology

### Database Layer (db.py ~3,880 lines)
SQLite with WAL mode, connection pooling, comprehensive user management.

**Connection Pool (lines 17-120):**
```python
_pool: Queue = Queue(maxsize=10)
get_conn()      # Get connection from pool
release_conn()  # Return to pool
```

**Core Tables:**
- `users` - All user settings, API keys, strategies
- `signals` - Trading signal history
- `active_positions` - Current open positions
- `pending_limit_orders` - Limit orders awaiting execution
- `trade_logs` - Complete trade history
- `user_licenses` - Premium subscription management
- `promo_codes` - Promotional codes
- `custom_strategies` - User-created strategies

**Key Functions by Category:**

*User Management (737-1260):*
```python
ensure_user(user_id)
get_user_config(user_id)     # Returns dict with ALL user settings (cached 30s)
set_user_field(user_id, field, value)
invalidate_user_cache(user_id)
```

*Credentials (772-965):*
```python
set_user_credentials(uid, key, secret, account_type)  # 'demo'|'real'
get_user_credentials(uid, account_type)
get_trading_mode(uid)  # 'demo', 'real', 'both'
set_trading_mode(uid, mode)
```

*Strategy Settings (1260-1510):*
```python
get_strategy_settings(uid, strategy)     # Get strategy-specific TP/SL/percent
set_strategy_setting(uid, strategy, field, value)
get_effective_settings(uid, strategy)    # Merged with global defaults
is_strategy_enabled_v2(uid, strategy, exchange, account_type)
```

*Positions & Trades (1736-2280):*
```python
add_active_position(uid, symbol, side, entry, qty, ...)
get_active_positions(uid)
remove_active_position(uid, symbol)
add_trade_log(uid, symbol, side, entry, exit, pnl, ...)
get_trade_stats(uid, strategy, period)
```

*License System (2275-2845):*
```python
get_user_license(uid)        # Returns: type, expires, is_active
set_user_license(uid, license_type, days, ...)
extend_license(uid, days)
check_license_access(uid, feature)
can_trade_strategy(uid, strategy)  # License check
```

*HyperLiquid (3280-3475):*
```python
set_hl_credentials(uid, private_key, vault_address, testnet)
get_hl_credentials(uid)
get_exchange_type(uid)       # 'bybit' | 'hyperliquid'
set_exchange_type(uid, type)
```

### Services Layer (services/)

**ExchangeService** (services/exchange_service.py):
- Abstract adapter pattern for multi-exchange
- `BybitAdapter`, `HyperLiquidAdapter` classes
- `OrderType`, `OrderSide`, `OrderResult`, `AccountBalance` dataclasses

**TradingService** (services/trading_service.py):
```python
@dataclass
class TradeRequest:
    symbol: str
    side: PositionSide
    size_percent: float
    leverage: int = 10
    take_profit_percent: Optional[float]
    stop_loss_percent: Optional[float]

trading_service.open_position(uid, request, adapter)
trading_service.close_position(uid, symbol, adapter)
```

**SignalService** (services/signal_service.py):
```python
signal_service.parse(text, channel_id)  # Returns TradingSignal
SignalSource: SCRYPTOMERA, SCALPER, ELCARO, WYCKOFF, MANUAL
SignalType: ENTRY, EXIT, UPDATE_TP, UPDATE_SL, ADD_POSITION
```

### Core Infrastructure (core/)

**Caching (core/cache.py):**
```python
user_config_cache   # max=5000, ttl=30s
price_cache         # max=500, ttl=5s
symbol_info_cache   # max=1000, ttl=1h
balance_cache       # max=1000, ttl=15s

@async_cached(cache, ttl=60)
async def expensive_call(): ...
```

**Rate Limiting (core/rate_limiter.py):**
```python
bybit_limiter.acquire(uid, "order")    # Token bucket algorithm
hl_limiter.acquire(uid, "order")

# Limits: user=20/5s, order=10/5s, balance=10/2s
```

**Exceptions (core/exceptions.py):**
```python
BotException           # Base
├── ExchangeError
│   ├── AuthenticationError
│   ├── RateLimitError
│   ├── InsufficientBalanceError
│   ├── PositionNotFoundError
│   └── OrderError
├── LicenseError
│   └── PremiumRequiredError
├── ConfigurationError
├── DatabaseError
└── SignalParseError
```

### WebApp (webapp/)

**FastAPI App (webapp/app.py):**
- Port: 8765
- Swagger: `/api/docs`
- Health: `/health`, `/health/detailed`, `/metrics`

**API Routers:**
| Router | Prefix | Purpose |
|--------|--------|---------|
| auth | `/api/auth` | JWT authentication |
| users | `/api/users` | User profile management |
| trading | `/api/trading` | Positions, orders, balance |
| admin | `/api/admin` | Admin panel API |
| stats | `/api/stats` | Trading statistics |
| backtest | `/api/backtest` | Strategy backtesting |
| ai | `/api/ai` | AI trading assistant (GPT-4) |
| websocket | `/ws` | Live trade updates |
| marketplace | `/api/marketplace` | Strategy marketplace |
| strategy_sync | `/api/sync` | Bot ↔ WebApp sync |

**Pages:**
- `/` - Landing page
- `/terminal` - Trading terminal
- `/dashboard` - User dashboard
- `/admin` - Admin panel
- `/backtest` - Backtesting interface
- `/screener` - Market screener

### HyperLiquid Integration (hl_adapter.py, hyperliquid/)

**HLAdapter** - Wrapper for HyperLiquid API (41 методов):
```python
adapter = HLAdapter(private_key, testnet=False, vault_address=None)
await adapter.initialize()
await adapter.place_order(symbol, side, qty, order_type, price)
await adapter.fetch_positions()
await adapter.set_leverage(symbol, leverage)
await adapter.close()
```

**HLAdapter Full Method List:**
| Category | Method | Description |
|----------|--------|-------------|
| **Core** | `initialize()` | Initialize client connection |
| | `close()` | Close connection |
| | `is_supported_symbol(symbol)` | Check if symbol is tradable |
| **Account** | `get_balance()` | Get account balance |
| | `fetch_balance()` | Alias for get_balance |
| | `get_portfolio()` | Get full portfolio details |
| | `get_user_fees()` | Get user fee rates |
| | `get_referral_info()` | Get referral stats |
| | `get_subaccounts()` | Get subaccounts list |
| | `get_rate_limits()` | Get current rate limits |
| **Positions** | `fetch_positions()` | Get all open positions |
| | `close_position(symbol, size)` | Close position |
| | `update_isolated_margin(symbol, delta)` | Adjust isolated margin |
| **Orders** | `place_order(...)` | Place new order |
| | `modify_order(order_id, ...)` | Modify existing order |
| | `cancel_order(symbol, order_id)` | Cancel order |
| | `cancel_all_orders(symbol)` | Cancel all orders |
| | `schedule_cancel(time)` | Schedule future cancel |
| | `place_twap_order(...)` | Place TWAP order |
| | `cancel_twap(twap_id)` | Cancel TWAP order |
| | `fetch_open_orders()` | Get open orders |
| | `fetch_orders()` | Get order history |
| | `get_order_status(order_id)` | Get order status |
| | `get_historical_orders(...)` | Get historical orders |
| **Market Data** | `get_price(symbol)` | Get current price |
| | `get_all_prices()` | Get all prices |
| | `get_ticker(symbol)` | Get ticker with bid/ask |
| | `get_orderbook(symbol, depth)` | Get orderbook |
| | `get_candles(symbol, interval, limit)` | Get candlestick data |
| | `get_symbols()` | Get all tradable symbols |
| | `get_all_coins_info()` | Get coins metadata |
| | `get_meta()` | Get exchange metadata |
| **History** | `fetch_trade_history(limit)` | Get trade fills |
| | `get_fills_by_time(start, end)` | Get fills by time range |
| | `get_funding_history(...)` | Get funding payments |
| | `get_predicted_funding(symbol)` | Get predicted funding |
| **Settings** | `set_leverage(symbol, leverage)` | Set leverage |
| | `set_take_profit(symbol, price)` | Set TP |
| | `set_stop_loss(symbol, price)` | Set SL |
| **Transfers** | `transfer_usdc(amount, dest)` | Transfer USDC |
| | `spot_transfer(coin, amount)` | Spot to perp transfer |

### Bybit Integration (exchanges/bybit.py)

**BybitExchange** - Bybit API Adapter (34 методов):
```python
from exchanges.bybit import BybitExchange

bybit = BybitExchange(
    api_key=api_key,
    api_secret=api_secret,
    testnet=False,  # Use testnet
    demo=True       # Use demo account
)
await bybit.initialize()
await bybit.place_order(symbol, side, size, order_type=OrderType.MARKET)
await bybit.get_positions()
await bybit.close()
```

**BybitExchange Full Method List:**
| Category | Method | Description |
|----------|--------|-------------|
| **Core** | `initialize()` | Initialize client connection |
| | `close()` | Close connection |
| | `normalize_symbol(symbol)` | Normalize to USDT pair |
| **Account** | `get_balance()` | Get account balance (Balance dataclass) |
| | `get_wallet_balance()` | Get detailed wallet per-coin |
| | `get_account_info()` | Get account config |
| | `get_fee_rates(symbol)` | Get maker/taker fees |
| **Positions** | `get_positions()` | Get all open positions |
| | `get_position(symbol)` | Get specific position |
| | `close_position(symbol, size)` | Close position |
| **Orders** | `place_order(...)` | Place new order (OrderResult) |
| | `modify_order(symbol, order_id, ...)` | Amend order |
| | `cancel_order(symbol, order_id)` | Cancel order |
| | `cancel_all_orders(symbol)` | Cancel all orders |
| | `get_open_orders(symbol)` | Get open orders |
| | `get_order_history(...)` | Get historical orders |
| **Market Data** | `get_price(symbol)` | Get last price |
| | `get_ticker(symbol)` | Get ticker with 24h stats |
| | `get_orderbook(symbol, depth)` | Get orderbook |
| | `get_candles(symbol, interval, limit)` | Get OHLCV data |
| | `get_symbols()` | Get all tradable symbols |
| | `get_instrument_info(symbol)` | Get symbol specs |
| | `get_server_time()` | Get server timestamp |
| | `get_open_interest(symbol)` | Get open interest |
| | `get_risk_limit(symbol)` | Get risk limit tiers |
| **History** | `get_trade_history(...)` | Get trade fills |
| | `get_pnl_history(...)` | Get closed P&L |
| | `get_funding_history(...)` | Get funding payments |
| | `get_current_funding_rate(symbol)` | Get current funding |
| **Settings** | `set_leverage(symbol, leverage)` | Set leverage |
| | `set_take_profit(symbol, price)` | Set TP |
| | `set_stop_loss(symbol, price)` | Set SL |
| | `set_margin_mode(symbol, mode)` | Set ISOLATED/CROSS |
| | `set_position_mode(mode)` | Set hedge/one-way |

**Exchange Router (exchange_router.py):**
```python
# Unified order placement - routes based on user's exchange setting
await place_order_universal(
    user_id, symbol, side, orderType, qty,
    price=None, leverage=None, reduce_only=False,
    bybit_place_order_func=place_order
)

# Other universal functions
await fetch_positions_universal(user_id, symbol, bybit_fetch_positions_func)
await set_leverage_universal(user_id, symbol, leverage, bybit_set_leverage_func)
await close_position_universal(user_id, symbol, size, side, bybit_place_order_func)
await get_balance_universal(user_id, bybit_get_balance_func)
```

## 📊 Trading Strategies

### Strategy Settings Structure
Each strategy can have per-user settings:
```python
{
    "percent": 1.0,     # % of balance per trade
    "tp_pct": 8.0,      # Take profit %
    "sl_pct": 3.0,      # Stop loss %
    "leverage": 10,
    "enabled": True,
    "account_types": ["demo", "real"],
    "side": "both"      # 'long', 'short', 'both'
}
```

### Strategy Toggle Handlers
- `cmd_toggle_scryptomera` (bot.py:3804)
- `cmd_toggle_scalper` (bot.py:3822)
- `cmd_toggle_elcaro` (bot.py:3841)
- `cmd_toggle_wyckoff` (bot.py:3860)

## 🔐 License System

**License Types:**
```python
LICENSE_TYPES = {
    "free": {"name": "Free", "max_strategies": 1, "features": []},
    "basic": {"name": "Basic", "max_strategies": 3, "features": ["basic_strategies"]},
    "premium": {"name": "Premium", "max_strategies": -1, "features": ["all_strategies", "hyperliquid", "ai_agent"]},
    "enterprise": {"name": "Enterprise", "max_strategies": -1, "features": ["*"]}
}
```

**Premium Features:**
- HyperLiquid exchange
- AI Trading Agent
- Unlimited strategies
- Advanced backtesting

## 🌐 Translations

**15 Languages:** ar, cs, de, en, es, fr, he, it, ja, lt, pl, ru, sq, uk, zh

**Reference:** `translations/en.py` (940+ keys)

**Pattern:**
```python
# translations/en.py
TEXTS = {
    'welcome': '👋 Hello!',
    'button_api': '🔑 API',
    ...
}
```

**Sync Commands:**
```bash
python -m utils.translation_sync --check   # Verify all keys
python -m utils.translation_sync --fix     # Add missing (English fallback)
python -m utils.translation_sync --report  # Full status
```

## 🛠️ Configuration Files

**Environment (.env):**
```
TELEGRAM_TOKEN=xxx
SIGNAL_CHANNEL_IDS=-1001234567890,-1009876543210
OPENAI_API_KEY=sk-xxx  # For AI agent
```

**Coin Parameters (coin_params.py):**
```python
ADMIN_ID = 511692487
DEFAULT_TP_PCT = 8.0
DEFAULT_SL_PCT = 3.0
MAX_OPEN_POSITIONS = 50
MAX_LIMIT_ORDERS = 50
BLACKLIST = {"FUSDT", "SKLUSDT", "BNBUSDT"}
```

## 🔧 Common Development Tasks

### Add New Telegram Command
```python
# 1. In bot.py
@log_calls
@require_access
async def cmd_newfeature(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    t = ctx.t
    uid = update.effective_user.id
    await update.message.reply_text(t['new_feature_text'])

# 2. Register handler (near end of bot.py)
app.add_handler(CommandHandler("newfeature", cmd_newfeature))

# 3. Add translations to ALL 15 files
# translations/en.py: 'new_feature_text': 'New feature description'
```

### Add New Database Column
```python
# In db.py init_db():
if not _col_exists(conn, "users", "new_column"):
    cur.execute("ALTER TABLE users ADD COLUMN new_column TEXT")

# Add to whitelist:
USER_FIELDS_WHITELIST = {
    ...
    "new_column",
}
```

### Add New WebApp Endpoint
```python
# webapp/api/myrouter.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/endpoint")
async def my_endpoint():
    return {"status": "ok"}

# In webapp/app.py:
from webapp.api import myrouter
app.include_router(myrouter.router, prefix="/api/my", tags=["my"])
```

## 🚨 Error Handling Patterns

```python
# Always use custom exceptions from core
from core.exceptions import ExchangeError, OrderError

try:
    result = await place_order(...)
except InsufficientBalanceError:
    await msg.reply_text(t['insufficient_balance'])
except RateLimitError as e:
    await asyncio.sleep(e.retry_after or 5)
except ExchangeError as e:
    logger.error(f"Exchange error: {e}")
```

## 📝 Important Notes

1. **bot.py is monolithic** - most trading logic is there, not in services
2. **Services are for new code** - gradually migrate logic there
3. **Always invalidate cache** after DB writes: `db.invalidate_user_cache(uid)`
4. **Test locally first** - never push directly to production
5. **Translations must sync** - every UI text needs all 15 language files

---

# 🖥️ SERVER & DEPLOYMENT DETAILS

## Server Connection

| Parameter | Value |
|-----------|-------|
| **IP** | `46.62.211.0` |
| **User** | `ubuntu` |
| **SSH Key** | `rita.pem` (в корне проекта, НЕ в git) |
| **Bot Path** | `/home/ubuntu/project/elcarobybitbotv2/` |
| **Python venv** | `/home/ubuntu/project/elcarobybitbotv2/venv/` |

### SSH Подключение
```bash
# Локально (из папки проекта)
ssh -i rita.pem ubuntu@46.62.211.0

# Или с полным путём
ssh -i /path/to/bybit_demo/rita.pem ubuntu@46.62.211.0
```

### ⚠️ Другие проекты на сервере (НЕ ТРОГАТЬ!)
- `/home/ubuntu/project/noetdat/` - Django screener (порт 8000)
- `/home/ubuntu/project/spain/` - rita.py бот

---

## Cloudflare Tunnel (Argo Tunnel)

### Текущий URL
```
https://kevin-longitude-night-pro.trycloudflare.com
```

### Как работает
1. Cloudflare tunnel запускается локально или на сервере
2. Создаёт безопасный туннель до Cloudflare edge
3. URL вида `*.trycloudflare.com` (меняется при каждом перезапуске!)

### Запуск туннеля на сервере
```bash
# Подключиться к серверу
ssh -i rita.pem ubuntu@46.62.211.0

# Запустить туннель в фоне
nohup cloudflared tunnel --url http://localhost:8765 > /tmp/cloudflared.log 2>&1 &

# Получить URL туннеля
grep -o 'https://[a-z-]*\.trycloudflare\.com' /tmp/cloudflared.log | tail -1
```

### Обновление URL в боте
После получения нового URL туннеля:
```bash
# На сервере - обновить файл URL
echo "https://NEW-URL.trycloudflare.com" > /home/ubuntu/project/elcarobybitbotv2/run/ngrok_url.txt

# Перезапустить бота чтобы применить новый URL для Menu Button
sudo systemctl restart elcaro-bot
```

### Проверка работы туннеля
```bash
# Проверить что туннель работает
curl -s https://YOUR-URL.trycloudflare.com/health

# Должен вернуть:
# {"status":"healthy","version":"2.0.0",...}
```

---

## Systemd Services

### elcaro-bot.service (Telegram Bot)
```bash
# Статус
sudo systemctl status elcaro-bot

# Перезапуск
sudo systemctl restart elcaro-bot

# Логи (live)
journalctl -u elcaro-bot -f --no-pager

# Логи (последние 100 строк)
journalctl -u elcaro-bot -n 100 --no-pager

# Остановить (не рекомендуется)
sudo systemctl stop elcaro-bot
```

### Конфигурация сервиса
Файл: `/etc/systemd/system/elcaro-bot.service`
```ini
[Unit]
Description=Elcaro Bybit Trading Bot v2
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/project/elcarobybitbotv2
ExecStart=/home/ubuntu/project/elcarobybitbotv2/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### WebApp (Uvicorn)
WebApp запускается отдельно (не через systemd):
```bash
# На сервере - запуск webapp
cd /home/ubuntu/project/elcarobybitbotv2
source venv/bin/activate
JWT_SECRET=elcaro_jwt_secret_key_2024_v2_secure python -m uvicorn webapp.app:app --host 0.0.0.0 --port 8765 &

# Проверка
curl localhost:8765/health
```

---

## Полный Workflow Деплоя

### 1. Локальные изменения
```bash
# Внести изменения в код
# Тестировать локально

# Закоммитить
git add -A
git commit -m "описание изменений"

# Запушить
git push origin webapp-screener-auth-2fa-dec21
```

### 2. Применить на сервере
```bash
# Подключиться
ssh -i rita.pem ubuntu@46.62.211.0

# Перейти в проект
cd /home/ubuntu/project/elcarobybitbotv2

# Получить изменения
git pull origin webapp-screener-auth-2fa-dec21

# Перезапустить бота
sudo systemctl restart elcaro-bot

# Проверить логи
journalctl -u elcaro-bot -f --no-pager
```

### 3. Если нужен новый туннель
```bash
# Убить старый туннель
pkill cloudflared

# Запустить новый
nohup cloudflared tunnel --url http://localhost:8765 > /tmp/cloudflared.log 2>&1 &

# Подождать 5 сек
sleep 5

# Получить URL
NEW_URL=$(grep -o 'https://[a-z-]*\.trycloudflare\.com' /tmp/cloudflared.log | tail -1)
echo $NEW_URL

# Обновить файл
echo $NEW_URL > /home/ubuntu/project/elcarobybitbotv2/run/ngrok_url.txt

# Перезапустить бота
sudo systemctl restart elcaro-bot
```

---

## Troubleshooting

### ❌ Ошибка "Conflict: terminated by other getUpdates request"
**Причина:** Запущено несколько экземпляров бота

**Решение:**
```bash
# Убить все процессы бота
pkill -9 -f 'python.*bot.py'

# Подождать
sleep 5

# Перезапустить через systemd (запустится один)
sudo systemctl restart elcaro-bot
```

### ❌ WebApp недоступен через туннель
**Проверить:**
```bash
# 1. WebApp работает?
curl localhost:8765/health

# 2. Туннель работает?
ps aux | grep cloudflared

# 3. Если нет - запустить
nohup cloudflared tunnel --url http://localhost:8765 > /tmp/cloudflared.log 2>&1 &
```

### ❌ Бот не запускается
**Проверить логи:**
```bash
journalctl -u elcaro-bot -n 50 --no-pager

# Или файл логов
tail -50 /home/ubuntu/project/elcarobybitbotv2/nohup.out
```

### ❌ Нужен sudo пароль
На сервере sudo работает без пароля для пользователя ubuntu

---

## Recent Fixes (December 22, 2025)

### SL Validation Skip
- **Problem:** `ValueError: SL (X) must be < current price (Y) for LONG` - ошибка когда SL уже сработал
- **File:** `bot.py` lines 2912-2922
- **Fix:** Вместо `raise ValueError` теперь `logger.warning()` + `sl_price = None` (пропуск SL)

### WebApp UI Improvements
- **Files:** `terminal.html`, `index.html`, `elcaro-theme.js`
- **Changes:**
  - Улучшены стили exchange-select/account-select (лучший фон, hover эффекты)
  - Добавлены стили для lang-menu dropdown с флагами
  - Расширен список языков до 12 (EN, RU, UK, ZH, ES, DE, FR, IT, JA, AR, HE, PL)
  - Добавлена RTL поддержка для иврита (he)

---

*Last updated: December 22, 2025*
*Version: 2.1.0*
*Current Tunnel: https://kevin-longitude-night-pro.trycloudflare.com*
*Exchange APIs: Bybit (34 methods), HyperLiquid (41 methods)*
