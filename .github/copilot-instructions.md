# Bybit Demo Trading Bot - AI Coding Guidelines

## Architecture Overview

This is an **async Telegram trading bot** for Bybit cryptocurrency futures trading. Built with `python-telegram-bot` (v20+) and `aiohttp` for API calls.

**Core Components:**
- `bot.py` - Main bot logic (~3800 lines): command handlers, Bybit API wrapper, signal processing, DCA/pyramid logic
- `db.py` - SQLite database layer with WAL mode, user config, positions, trade logs
- `coin_params.py` - Trading configuration: TP/SL defaults, ATR params, keyword sentiment lists, symbol filters
- `translations/` - Multi-language support (15 languages), each file exports `TEXTS` dict

**Data Flow:**
```
Telegram Channel Signal → on_channel_post() → parse signal → 
→ filter by user config (coins, OI, RSI/BB) → create order via _bybit_request() →
→ store in active_positions → monitor for TP/SL/exit → log to trade_logs
```

## Key Patterns

### Bybit API Calls
All Bybit requests go through `_bybit_request()` which handles:
- HMAC signing with user credentials from DB
- Retry logic with exponential backoff
- Demo vs production endpoint (`BYBIT_BASE`)

```python
# Pattern for API calls
await _bybit_request(user_id, "POST", "/v5/order/create", body={...})
await _bybit_request(user_id, "GET", "/v5/position/list", params={...})
```

### Handler Decorators
- `@require_access` - Checks user approval, ban status, terms acceptance
- `@with_texts` - Injects `ctx.t` dict with localized strings
- `@log_calls` - Debug logging for function entry/exit

Always stack decorators in this order:
```python
@with_texts
@log_calls
async def cmd_something(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
```

### Database Operations
- Use `get_user_config(uid)` for reading user settings (returns normalized dict)
- Use `set_user_field(uid, field, value)` for updates (field must be in `USER_FIELDS_WHITELIST`)
- Use `ensure_user(uid)` before any UPDATE if user might not exist

### Localization
Access translations via `ctx.t[key]` after using `@with_texts`. Add new keys to ALL files in `translations/`.

## Environment & Configuration

**Required `.env` variables:**
- `TELEGRAM_TOKEN` - Bot token
- `SIGNAL_CHANNEL_IDS` - Comma-separated Telegram channel IDs for signals
- Bybit credentials stored per-user in SQLite, not env

**Key constants in `coin_params.py`:**
- `ADMIN_ID` - Telegram user ID with admin privileges
- `MAX_OPEN_POSITIONS`, `MAX_LIMIT_ORDERS` - Trading limits
- `BLACKLIST` - Symbols to never trade
- `TIMEFRAME_PARAMS` - ATR/TP/SL settings per timeframe

## Running the Bot

```bash
# Ensure .env exists with TELEGRAM_TOKEN
python bot.py
```

The bot uses `run_polling()` and initializes the aiohttp session + SQLite on startup via `init_session()` and `db.init_db()`.

## Common Tasks

**Adding a new command:**
1. Create handler function with `@require_access`, `@with_texts` decorators
2. Register in `main()` with `app.add_handler(CommandHandler("name", handler))`
3. Add button text to all translation files if needed

**Adding a user config field:**
1. Add to `USER_FIELDS_WHITELIST` in `db.py`
2. Add column migration in `init_db()` with `_col_exists()` check
3. Add to `get_user_config()` return dict
