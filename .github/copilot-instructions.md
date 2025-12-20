# Bybit + HyperLiquid Trading Bot - AI Coding Guidelines

> **CRITICAL:** Do NOT run `git push` - all changes are local only!

## Architecture Overview

Async Telegram trading bot supporting dual-exchange futures trading:
- **Bybit** (CEX) - primary exchange
- **HyperLiquid** (DEX) - Premium users only

**Stack:** `python-telegram-bot` v20+, `aiohttp`, `FastAPI`, `SQLite WAL`

### Core Files
| File | Purpose |
|------|---------|
| `bot.py` | Main bot (~14K lines) - all handlers, Bybit API, signal processing |
| `db.py` | SQLite layer with connection pooling, user config caching |
| `coin_params.py` | Trading config: `ADMIN_ID`, `DEFAULT_TP_PCT/SL_PCT`, `BLACKLIST` |
| `exchange_router.py` | Routes orders to Bybit or HyperLiquid based on user settings |
| `hl_adapter.py` | HyperLiquid adapter wrapping the custom SDK |
| `hyperliquid/client.py` | Custom async HyperLiquid SDK with EIP-712 signing |
| `translations/*.py` | 15 languages - all must stay in sync |

### Key Patterns

**Handler Decorators (order matters!):**
```python
@with_texts      # Injects ctx.t dict with translations
@log_calls       # Exception logging (no entry/exit spam)
@require_access  # Checks ban, approval, terms acceptance
async def cmd_something(update, ctx):
    text = ctx.t['some_key']  # Use translation
```

**Exchange Mode System:**
```python
db.get_exchange_type(uid)       # 'bybit' or 'hyperliquid' - active exchange
db.set_exchange_mode(uid, mode) # 'bybit', 'hyperliquid', 'both' - allowed modes
db.get_hl_credentials(uid)      # Returns dict with hl_private_key, hl_wallet_address, etc.
```

**HyperLiquid Client:**
```python
from hyperliquid import HyperLiquidClient
# Full access (trading)
client = HyperLiquidClient(private_key="0x...", testnet=True)
# Read-only (balance/positions only)
client = HyperLiquidClient(wallet_address="0x...", testnet=True)
```

## Developer Workflows

### Running Services
```bash
./start.sh              # All services foreground
./start.sh --daemon     # All services background
./start.sh --status     # Check what's running
./start.sh --stop       # Stop everything
./start.sh --bot        # Bot only
./start.sh --webapp     # WebApp only (port 8765)
```

### Database: `bot.db` (not `bybit_users.db`!)
SQLite with WAL mode. User config uses in-memory cache (30s TTL).
```python
# Add new column:
conn = sqlite3.connect("bot.db")
conn.execute("ALTER TABLE users ADD COLUMN new_col TEXT")
conn.commit()
```

### Adding Bot Commands
1. Write handler in `bot.py` with `@with_texts`, `@require_access` decorators
2. Register: `app.add_handler(CommandHandler("cmd", handler))`
3. Add translation keys to ALL 15 files in `translations/*.py`
```python
# Check missing translations:
from translations import en, ru
missing = set(en.TEXTS.keys()) - set(ru.TEXTS.keys())
```

### After Code Changes
```bash
rm -rf __pycache__ */__pycache__  # Clear Python cache
./start.sh --restart               # Restart services
```

## Project-Specific Notes

- **Port 8000** is reserved (system process) - use **8765** for webapp
- **ngrok API** runs on port 4040 for tunnel URLs
- Database columns for HyperLiquid: `hl_wallet_address`, `hl_private_key`, `hl_vault_address`, `hl_testnet`, `exchange_mode`, `exchange_type`
- User whitelist field: `USER_FIELDS_WHITELIST` in `db.py` controls allowed config updates
- Trading parameters in `coin_params.py`: `COIN_PARAMS`, `TIMEFRAME_PARAMS`, `THRESHOLD_MAP`

## WebApp (FastAPI)

Located in `webapp/` with Jinja2 templates. API routes:
- `/api/auth` - Authentication
- `/api/trading` - Order placement
- `/api/admin` - Admin functions
- `/ws` - WebSocket for live trades

## Current HyperLiquid Commands
`/hl`, `/hl_balance`, `/hl_positions`, `/hl_switch`, `/hl_clear`

---
*Updated: December 2025*
