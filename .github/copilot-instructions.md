# ElCaro Trading Platform - AI Coding Guidelines

> **CRITICAL:** Do NOT run `git push` - all changes are local only!

## Architecture Overview

Async Telegram trading bot with FastAPI webapp for dual-exchange crypto futures trading.

**Stack:** Python 3.10+, `python-telegram-bot` v20+, `aiohttp`, `FastAPI`, `SQLite WAL`

| Component | Files | Purpose |
|-----------|-------|---------|
| **Bot** | `bot.py` (~14K lines) | Telegram handlers, Bybit API, signal processing |
| **Core** | `core/` | Caching, rate limiting, connection pooling, metrics |
| **Database** | `db.py` | SQLite WAL, connection pooling (10 conns), 30s config cache |
| **Trading Config** | `coin_params.py` | `ADMIN_ID`, TP/SL defaults, `BLACKLIST`, thresholds |
| **Exchange Router** | `exchange_router.py` | Routes orders to Bybit or HyperLiquid per user |
| **HyperLiquid** | `hl_adapter.py`, `hyperliquid/` | Custom async SDK with EIP-712 signing |
| **WebApp** | `webapp/` | FastAPI terminal, AI agent, backtesting (port 8765) |
| **Translations** | `translations/*.py` | 15 languages - **must sync all on changes** |
| **Screener** | `scan/` | Separate Django app for real-time crypto screener |

## Core Infrastructure (`core/`)

### Caching (`core/cache.py`)
```python
from core import cached, async_cached, user_config_cache, invalidate_user_caches

# Sync function caching
@cached(user_config_cache, ttl=60)
def get_user_settings(user_id: int) -> dict: ...

# Async function caching
@async_cached(price_cache, ttl=5)
async def fetch_price(symbol: str) -> dict: ...

# Invalidate on updates
invalidate_user_caches(user_id)
```

### Rate Limiting (`core/rate_limiter.py`)
```python
from core import bybit_limiter, hl_limiter

await bybit_limiter.acquire(user_id, "order")  # Before placing order
await hl_limiter.acquire(user_id, "balance")   # Before balance check
```

### Connection Pooling (`core/connection_pool.py`)
```python
from core import get_cached_client, on_credentials_changed

async with await get_cached_client(user_id) as client:
    balance = await client.get_balance()

# After credential changes:
on_credentials_changed(user_id)
```

### Metrics (`core/metrics.py`)
```python
from core import metrics, track_latency, count_errors

@track_latency(name="api_request")
@count_errors()
async def make_api_call(): ...

# Manual metrics
metrics.orders_placed.inc(exchange="bybit")
metrics.request_latency.observe(elapsed_ms)
```

## Handler Decorator Stack (ORDER MATTERS!)
```python
@with_texts      # 1st: Injects ctx.t dict from user's language
@log_calls       # 2nd: Exception logging (no entry/exit spam)  
@require_access  # 3rd: Checks is_banned, is_allowed, terms_accepted
async def cmd_something(update, ctx):
    t = ctx.t  # Translation dict
    uid = update.effective_user.id
```
**Note:** `require_access` internally calls `@with_texts`, so just `@log_calls @require_access` works.

## Exchange System
```python
# User exchange type (active)
db.get_exchange_type(uid)       # Returns 'bybit' or 'hyperliquid'
db.set_exchange_type(uid, type) # Switch active exchange

# Bybit supports demo/real accounts
db.get_trading_mode(uid)        # 'demo', 'real', or 'both'
db.get_active_account_types(uid) # Returns ['demo'] or ['demo', 'real']

# HyperLiquid credentials
db.get_hl_credentials(uid)      # Dict: hl_private_key, hl_wallet_address, hl_testnet
```

## Developer Workflows

### Service Management
```bash
./start.sh              # All services foreground
./start.sh --daemon     # Background mode
./start.sh --status     # Check running services
./start.sh --stop       # Stop all
./start.sh --restart    # Restart all
./start.sh --bot        # Bot only
./start.sh --webapp     # WebApp only (port 8765)
./start.sh --install    # Install dependencies
```

### Database (`bot.db`)
SQLite WAL mode, 64MB cache, connection pool. Soft migrations in `init_db()`.
```python
# Adding new user column:
# 1. Add ALTER TABLE to init_db() migrations in db.py
# 2. Add field name to USER_FIELDS_WHITELIST in db.py
# 3. Invalidate cache: db.invalidate_user_cache(uid) or core.invalidate_user_caches(uid)
```

### Adding Bot Commands
1. Create handler in `bot.py`:
   ```python
   @log_calls
   @require_access
   async def cmd_newfeature(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
       await update.message.reply_text(ctx.t['new_feature_text'])
   ```
2. Register: `app.add_handler(CommandHandler("newfeature", cmd_newfeature))`
3. Add keys to ALL 15 `translations/*.py` files
4. Verify: `python -m utils.translation_sync --check`
5. Auto-fix: `python -m utils.translation_sync --fix`

### WebApp API Structure
```
webapp/api/
├── auth.py         # /api/auth - Telegram auth
├── trading.py      # /api/trading - Order execution, DCA, risk calculator
├── admin.py        # /api/admin - Admin functions
├── stats.py        # /api/stats - Analytics
├── backtest.py     # /api/backtest - Strategy testing
├── ai.py           # /api/ai - AI agent queries
├── websocket.py    # /ws - Live orderbook, trades, signals
└── strategy_sync.py # /api/sync - Bot<->webapp sync
```

### Trading Terminal v2.0 (`webapp/templates/terminal.html`)
Advanced trading interface with professional features:

**Core Trading:**
- TradingView chart integration
- Real-time orderbook with whale detection
- Quick market buy/sell with hotkeys
- Cross/Isolated margin modes
- Leverage slider (1-100x)

**Advanced Features:**
- **Risk Calculator** - Position sizing based on account risk %
- **DCA Ladder Builder** - Multi-order entry with linear/geometric/fibonacci distribution
- **Orderbook Heatmap** - Visual depth with bid/ask imbalance indicator
- **One-Click Trading** - Fast execution mode with countdown cancel
- **Smart Alerts** - Price/PnL alerts with sound & browser notifications
- **Trailing Stop Manager** - Auto break-even and trailing logic

**Keyboard Shortcuts:**
- `B` - Buy/Long, `S` - Sell/Short
- `1` - Limit order, `2` - Market order
- `Enter` - Submit order
- `Ctrl+B` - Quick buy 25%, `Ctrl+Shift+B` - Quick buy 100%
- `?` - Show shortcuts help

**JavaScript Modules:**
- `webapp/static/js/terminal-advanced.js` - Core advanced features
- `webapp/static/css/terminal-advanced.css` - Styles for new components

### Trading API Endpoints
```python
# Basic trading
POST /api/trading/order           # Place single order
POST /api/trading/close           # Close position
GET  /api/trading/positions       # Get open positions
GET  /api/trading/orders          # Get open orders
GET  /api/trading/balance         # Get account balance

# Advanced trading
POST /api/trading/dca-ladder      # Place DCA ladder orders
POST /api/trading/calculate-position  # Risk-based position calculator
GET  /api/trading/symbol-info/{symbol}  # Tick size, lot size, max leverage
GET  /api/trading/orderbook/{symbol}    # Real orderbook with depth
GET  /api/trading/recent-trades/{symbol}  # Recent trades feed
```

### Backtest API Endpoints
```python
# Standard backtest
POST /api/backtest/run           # Run backtest with strategies
POST /api/backtest/quick         # Quick compare all strategies
POST /api/backtest/multi-symbol  # Multi-symbol backtest
POST /api/backtest/monte-carlo   # Monte Carlo risk simulation
POST /api/backtest/optimize      # Grid search optimization
POST /api/backtest/walk-forward  # Walk-forward validation

# Live Strategy Execution
POST /api/backtest/replay-data   # Historical data with signals for replay
POST /api/backtest/deploy        # Deploy tested strategy to bot
GET  /api/backtest/deployments   # List strategy deployments
WS   /ws/backtest-live           # Real-time strategy visualization
```

### Screener API Endpoints
```python
WS   /ws/screener                # Real-time market data (Binance)
GET  /api/screener/overview      # Market overview stats
GET  /api/screener/symbols       # List of symbols
GET  /api/screener/symbol/{sym}  # Symbol data
```

### Health & Metrics Endpoints
- `GET /health` - Basic health check
- `GET /health/detailed` - Full system health with memory, CPU
- `GET /metrics` - Cache stats, connection pool, counters

## Backtest System v2.0

### Live Strategy Execution Mode
Watch strategies execute on historical data with real-time visualization:
- Real-time candle streaming on chart
- Dynamic indicator calculation (RSI, EMA, BB)
- Signal detection with confidence levels
- Trade execution with PnL tracking
- Market sentiment gauge

**Files:**
- `webapp/static/js/backtest-advanced.js` - BacktestAdvanced, LiveTradingChart, StrategyReplay
- `webapp/static/css/backtest-advanced.css` - Live mode styles
- `webapp/api/backtest.py` - LiveBacktestManager WebSocket handler

### Deploy Strategy to Bot
After successful backtest, deploy optimized parameters:
```python
POST /api/backtest/deploy
{
    "strategy": "elcaro",
    "params": {"stop_loss_percent": 1.5, "take_profit_percent": 3},
    "backtest_results": {"win_rate": 65, "pnl": 1250}
}
```

## Key Patterns

### Trading Parameters (`coin_params.py`)
- `COIN_PARAMS` - Per-coin TP/SL overrides (default: TP 8%, SL 3%)
- `TIMEFRAME_PARAMS` - ATR settings per timeframe (5m, 15m, 1h, 24h)
- `BLACKLIST` - Excluded symbols: `{"FUSDT", "SKLUSDT", "BNBUSDT"}`
- `ADMIN_ID` - Your Telegram ID for admin bypass

### HyperLiquid Client
```python
from hyperliquid import HyperLiquidClient
async with HyperLiquidClient(private_key="0x...", testnet=True) as client:
    await client.place_order(...)
```

### Unified Exchange Client (New)
```python
from core import get_exchange_client

async with await get_exchange_client(user_id) as client:
    balance = await client.get_balance()
    await client.place_order(symbol="BTCUSDT", side="Buy", qty=0.01)
```

### User Config Fields (`USER_FIELDS_WHITELIST` in db.py)
- API: `demo_api_key`, `demo_api_secret`, `real_api_key`, `real_api_secret`
- Trading: `trading_mode`, `percent`, `leverage`, `tp_percent`, `sl_percent`
- Strategies: `trade_oi`, `trade_rsi_bb`, `trade_scryptomera`, `trade_scalper`, `trade_elcaro`, `trade_wyckoff`
- Access: `is_allowed`, `is_banned`, `terms_accepted`

### After Code Changes
```bash
rm -rf __pycache__ */__pycache__  # Clear cache
./start.sh --restart
```

## Translation Management
```bash
# Check translation status
python -m utils.translation_sync --report

# Validate (for CI)
python -m utils.translation_sync --check

# Add missing keys with English fallback
python -m utils.translation_sync --fix
```

Languages: `ar, cs, de, en, es, fr, he, it, ja, lt, pl, ru, sq, uk, zh`

## HyperLiquid Commands
`/hl`, `/hl_balance`, `/hl_positions`, `/hl_switch`, `/hl_clear`

---
*Updated: December 2025*
