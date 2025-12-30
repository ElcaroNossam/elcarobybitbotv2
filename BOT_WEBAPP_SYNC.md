# Bot ↔ WebApp Synchronization Architecture

> **Version:** 2.0  
> **Date:** December 28, 2025  
> **Status:** Implemented

## Overview

This document describes the synchronization pattern between the Telegram Bot and WebApp for managing trading positions across multiple exchanges and environments.

## Target Model

The unified **Target** model represents a trading account destination:

```python
@dataclass
class Target:
    exchange: str    # 'bybit' | 'hyperliquid'
    env: str         # 'paper' | 'live'
    
    @property
    def key(self) -> str:
        return f"{self.exchange}:{self.env}"
    
    @property
    def account_type(self) -> str:
        """Backward compatibility: returns demo/real/testnet/mainnet"""
        if self.exchange == "bybit":
            return "demo" if self.env == "paper" else "real"
        else:  # hyperliquid
            return "testnet" if self.env == "paper" else "mainnet"
```

### Environment Mapping

| Exchange | Env | account_type (legacy) |
|----------|-----|----------------------|
| Bybit | paper | demo |
| Bybit | live | real |
| HyperLiquid | paper | testnet |
| HyperLiquid | live | mainnet |

## Data Flow

### 1. Bot → Database (Source of Truth)

The Bot is the **primary writer** to `active_positions` table:

```
Signal Received → Bot Opens Position → Exchange API → add_active_position()
                                                      ↓
                                              DB (active_positions)
                                                      ↓
                                              monitor_positions_loop()
                                              detects close → remove_active_position()
```

### 2. WebApp → Database (Reader + Display)

WebApp **reads** positions from Exchange API and **enriches** with DB data:

```
User Opens Terminal → GET /api/trading/positions?exchange=bybit&account_type=demo
                      ↓
              1. Fetch from Exchange API (live positions)
              2. Get db.get_active_positions(user_id, account_type, exchange, env)
              3. Merge: Exchange data + DB strategy/TP/SL info
                      ↓
              Return enriched positions to UI
```

### 3. WebApp → Database (Controlled Writer)

When WebApp opens/modifies positions, it writes through reconciled flow:

```
User Places Order → POST /api/trading/order
                    ↓
            1. Place order via Exchange API
            2. On success: add_active_position() with source='webapp', opened_by='webapp'
            3. Bot's monitor_positions_loop() will detect and track
```

## Key Components

### 1. `monitor_positions_loop()` in bot.py

**Purpose:** Monitors all user positions across ALL their targets (not just active trading_mode).

**New Logic (Multi-Target Iteration):**
```python
for user_id in users:
    user_config = get_user_config(user_id)
    trading_mode = user_config.get("trading_mode", "demo")
    
    # Determine which account_types to check
    if trading_mode == "both":
        account_types_to_check = ["demo", "real"]
    else:
        account_types_to_check = [trading_mode]
    
    for current_account_type in account_types_to_check:
        # Fetch positions for this account_type
        open_positions = await fetch_open_positions(uid, sym=None, account_type=current_account_type)
        
        # Get active positions from DB
        active = get_active_positions(uid, account_type=current_account_type)
        
        # ... process positions ...
```

**Benefits:**
- Users with `trading_mode="both"` now get monitored on BOTH demo and real
- No positions are missed due to account_type mismatch
- Proper cleanup of closed positions on all accounts

### 2. `fetch_open_positions()` in bot.py

**Purpose:** Fetch positions from exchange and enrich with DB data.

**Key Enrichment Logic:**
```python
# Enrich with DB data if exchange didn't return TP/SL
db_positions = {p["symbol"]: p for p in db.get_active_positions(user_id, account_type)}

for pos in exchange_positions:
    symbol = pos["symbol"]
    db_pos = db_positions.get(symbol, {})
    
    # Map unified fields to Bybit-style fields
    if "takeProfit" not in pos or not pos["takeProfit"]:
        pos["takeProfit"] = db_pos.get("tp_price")
    if "stopLoss" not in pos or not pos["stopLoss"]:
        pos["stopLoss"] = db_pos.get("sl_price")
    
    # Copy strategy info
    pos["strategy"] = db_pos.get("strategy")
    pos["source"] = db_pos.get("source", "bot")
    pos["opened_by"] = db_pos.get("opened_by", "bot")
```

### 3. `/api/trading/positions` in webapp/api/trading.py

**Purpose:** WebApp endpoint for fetching positions.

**Parameters:**
- `exchange`: 'bybit' or 'hyperliquid'
- `account_type`: 'demo', 'real', 'testnet', 'mainnet' (legacy)
- `env`: 'paper' or 'live' (unified, takes precedence)

**Example Usage:**
```javascript
// Get demo positions
fetch('/api/trading/positions?exchange=bybit&account_type=demo')

// Or using unified env
fetch('/api/trading/positions?exchange=bybit&env=paper')
```

## Database Schema

### `active_positions` table

| Column | Type | Description |
|--------|------|-------------|
| user_id | INTEGER | User ID |
| symbol | TEXT | Trading pair (e.g., BTCUSDT) |
| side | TEXT | 'long' or 'short' |
| entry_price | REAL | Entry price |
| size | REAL | Position size |
| account_type | TEXT | 'demo', 'real', 'testnet', 'mainnet' |
| exchange | TEXT | 'bybit' or 'hyperliquid' |
| env | TEXT | 'paper' or 'live' (unified) |
| strategy | TEXT | Strategy name |
| source | TEXT | 'bot', 'webapp', 'manual' |
| opened_by | TEXT | 'bot', 'webapp', 'user' |
| sl_price | REAL | Stop loss price |
| tp_price | REAL | Take profit price |
| ... | | (other fields) |

### Query Patterns

```python
# Get all positions for a specific target
positions = db.get_active_positions(
    user_id, 
    account_type="demo",
    exchange="bybit",
    env="paper"
)

# Get positions for ALL targets (for monitoring)
targets = get_user_targets(user_id)
for target in targets:
    positions = db.get_positions_by_target(user_id, target.exchange, target.env)
```

## Reconciliation Rules

### 1. Position Opened by Bot
- Source: `bot`
- DB entry created immediately after exchange confirms order
- WebApp can display and modify (TP/SL)
- Only Bot's monitor loop removes on close

### 2. Position Opened by WebApp
- Source: `webapp`
- DB entry created after exchange confirms order
- Bot's monitor loop detects and tracks it
- Either Bot or WebApp can close

### 3. Orphan Detection
If exchange has position but DB doesn't:
- WebApp shows it as "untracked"
- Bot's monitor can optionally add to DB if configured

### 4. Ghost Detection
If DB has position but exchange doesn't:
- Detected by `monitor_positions_loop()`
- Cleaned up automatically (removed from DB)
- Logged as "Position closed externally"

## UI Target Selector

Terminal has two dropdowns:

```html
<!-- Exchange selector -->
<select id="exchangeSelect" onchange="changeExchange()">
    <option value="bybit">Bybit</option>
    <option value="hyperliquid">HyperLiquid</option>
</select>

<!-- Account type selector (dynamically updated) -->
<select id="accountSelect" onchange="changeAccountType()">
    <!-- For Bybit: -->
    <option value="demo">Demo</option>
    <option value="real">Real</option>
    <!-- For HyperLiquid: -->
    <option value="testnet">Testnet</option>
    <option value="mainnet">Mainnet</option>
</select>
```

When user switches:
1. `changeAccountType()` calls `/api/users/switch-account-type`
2. Reloads positions for new target
3. Updates UI badge (DEMO/REAL)

## API Responses

### Positions Response
```json
[
  {
    "symbol": "BTCUSDT",
    "side": "long",
    "size": 0.01,
    "entry_price": 50000,
    "mark_price": 51000,
    "pnl": 100.0,
    "exchange": "bybit",
    "account_type": "demo",
    "env": "paper",
    "strategy": "elcaro",
    "tp_price": 55000,
    "sl_price": 48000
  }
]
```

## Migration Notes

### From Old to New Architecture

1. **Old code** used `trading_mode` as single value
2. **New code** iterates through `account_types_to_check` list
3. **Backward compatible**: `trading_mode="demo"` still works
4. **New capability**: `trading_mode="both"` properly monitors both accounts

### Key Changes in bot.py

1. Added import: `from exchange_router import get_user_targets, Target, normalize_env`
2. Modified `monitor_positions_loop()` to iterate account types
3. Modified `fetch_open_positions()` to enrich from DB
4. All TP/SL display issues fixed

## Testing

```bash
# Run relevant tests
python3 -m pytest tests/test_exchange_router.py tests/test_bot_unified.py -v

# All 43 tests should pass
```

## Future Improvements

1. **Real-time sync via WebSocket** - Push position updates to WebApp
2. **Conflict resolution** - Handle simultaneous Bot/WebApp modifications
3. **order_intents table** - Pre-register orders before execution for better tracking
4. **Audit log** - Track all position changes with source attribution

---

*Last updated: December 28, 2025*
