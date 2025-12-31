# Strategy Builder API Documentation

**Version:** 1.0.0  
**Base URL:** `/api/builder/strategies`  
**Authentication:** JWT Bearer Token

## Overview

The Strategy Builder API provides complete CRUD operations, backtesting, and live trading management for custom trading strategies. It features AI-powered strategy generation using OpenAI GPT-4.

## Authentication

All endpoints (except templates and indicators) require JWT authentication:

```
Authorization: Bearer <your_jwt_token>
```

---

## Endpoints

### Public Endpoints (No Auth Required)

#### `GET /templates`
Get preset strategy templates.

**Response:**
```json
{
  "templates": {
    "rsi_mean_reversion": { ... },
    "macd_crossover": { ... },
    "bollinger_breakout": { ... },
    "multi_indicator": { ... }
  }
}
```

#### `GET /indicators`
Get available indicators and their parameters.

**Response:**
```json
{
  "indicators": {
    "trend": [
      {"id": "ema", "name": "EMA", "params": {"period": "int"}},
      {"id": "sma", "name": "SMA", "params": {"period": "int"}}
    ],
    "oscillators": [...],
    "volatility": [...],
    "volume": [...],
    "price": [...]
  },
  "operators": ["<", ">", "<=", ">=", "==", "!=", "crosses_above", "crosses_below", "between"],
  "exit_types": [...],
  "timeframes": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
}
```

---

### AI Generation

#### `POST /generate`
Generate strategy from natural language description using AI.

**Request:**
```json
{
  "description": "RSI strategy that buys when RSI is below 30 and price is above EMA200"
}
```

**Response:**
```json
{
  "success": true,
  "generated": true,
  "strategy": {
    "name": "AI Generated: RSI Mean Reversion",
    "description": "...",
    "version": "1.0.0",
    "long_entry": {...},
    "exit_rules": [...],
    "risk": {...}
  },
  "model_used": "gpt-4o",
  "tokens_used": 1234,
  "message": "Strategy generated from description. Review and customize before saving."
}
```

#### `POST /enhance`
Enhance an existing strategy based on feedback.

**Request:**
```json
{
  "strategy": { ... current strategy config ... },
  "feedback": "Make it more aggressive with higher leverage"
}
```

**Response:**
```json
{
  "success": true,
  "enhanced": true,
  "strategy": { ... enhanced config ... },
  "model_used": "gpt-4o",
  "tokens_used": 1500
}
```

#### `POST /explain`
Get human-readable explanation of a strategy.

**Request:**
```json
{
  "strategy": { ... strategy config ... }
}
```

**Response:**
```json
{
  "success": true,
  "explanation": "**RSI Mean Reversion Strategy**\n\n**Long Entry:**\n- RSI below 30 (oversold)\n- Price above EMA200 (uptrend)...",
  "strategy_name": "RSI Mean Reversion"
}
```

---

### Strategy CRUD

#### `POST /` (Create)
Create a new custom strategy.

**Request:**
```json
{
  "name": "My RSI Strategy",
  "description": "RSI mean reversion with EMA filter",
  "long_entry": {
    "direction": "LONG",
    "groups": [{
      "id": "main",
      "conditions": [
        {
          "id": "rsi_oversold",
          "left": {"type": "rsi", "params": {"period": 14}},
          "operator": "<",
          "value": 30,
          "enabled": true,
          "description": "RSI oversold"
        }
      ],
      "operator": "AND",
      "enabled": true
    }],
    "group_operator": "AND",
    "enabled": true
  },
  "short_entry": null,
  "exit_rules": [
    {"type": "take_profit", "value": 4.0, "enabled": true},
    {"type": "stop_loss", "value": 2.0, "enabled": true}
  ],
  "risk": {
    "position_size_percent": 10.0,
    "max_positions": 5,
    "max_daily_trades": 20,
    "max_daily_loss_percent": 10.0,
    "leverage": 10
  },
  "filters": {
    "min_volume_usdt": null,
    "excluded_symbols": [],
    "required_symbols": []
  },
  "primary_timeframe": "15m",
  "higher_timeframes": ["1h", "4h"],
  "pyramiding": 1,
  "allow_reverse": false
}
```

**Response:**
```json
{
  "success": true,
  "strategy_id": 1,
  "name": "My RSI Strategy",
  "version": "1.0.0"
}
```

#### `GET /` (List)
List all strategies owned or purchased by user.

**Query Parameters:**
- `include_purchased` (bool, default: true): Include purchased strategies

**Response:**
```json
{
  "owned": [
    {
      "id": 1,
      "name": "My RSI Strategy",
      "description": "...",
      "is_active": true,
      "is_public": false,
      "created_at": "2024-12-30T10:00:00Z"
    }
  ],
  "purchased": []
}
```

#### `GET /{strategy_id}` (Get)
Get strategy details including version history.

**Response:**
```json
{
  "id": 1,
  "name": "My RSI Strategy",
  "description": "...",
  "config": { ... full strategy config ... },
  "is_active": true,
  "is_public": false,
  "performance_stats": {},
  "created_at": "2024-12-30T10:00:00Z",
  "updated_at": "2024-12-30T10:00:00Z",
  "versions": [
    {
      "id": 1,
      "version": "1.0.0",
      "change_log": "Initial version",
      "created_at": "2024-12-30T10:00:00Z"
    }
  ]
}
```

#### `PUT /{strategy_id}` (Update)
Update strategy configuration.

**Request:**
```json
{
  "name": "My RSI Strategy v2",
  "description": "Updated description",
  "config": { ... updated config ... },
  "change_log": "Added volume filter"
}
```

**Response:**
```json
{
  "success": true,
  "strategy_id": 1,
  "new_version": "1.0.1"
}
```

#### `DELETE /{strategy_id}` (Delete)
Delete a strategy.

**Response:**
```json
{
  "success": true,
  "deleted_id": 1
}
```

---

### Backtesting

#### `POST /{strategy_id}/backtest`
Run backtest on historical data.

**Request:**
```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "start_date": "2024-01-01",
  "end_date": "2024-06-01",
  "initial_balance": 10000
}
```

**Response:**
```json
{
  "success": true,
  "strategy_id": 1,
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "days": 152,
  "stats": {
    "total_trades": 45,
    "winning_trades": 28,
    "losing_trades": 17,
    "win_rate": 62.22,
    "total_pnl": 2500.50,
    "total_pnl_percent": 25.01,
    "profit_factor": 1.85,
    "max_drawdown_percent": 8.5,
    "sharpe_ratio": 1.42,
    "sortino_ratio": 2.10
  },
  "trades": [...],
  "equity_curve": [...]
}
```

---

### Version Control

#### `GET /{strategy_id}/versions`
Get version history.

**Response:**
```json
{
  "strategy_id": 1,
  "versions": [
    {
      "id": 2,
      "version": "1.0.1",
      "change_log": "Added volume filter",
      "backtest_results": {...},
      "created_at": "2024-12-30T12:00:00Z",
      "created_by": 511692487
    },
    {
      "id": 1,
      "version": "1.0.0",
      "change_log": "Initial version",
      "created_at": "2024-12-30T10:00:00Z"
    }
  ]
}
```

#### `POST /{strategy_id}/versions/{version_id}/rollback`
Rollback to a previous version.

**Response:**
```json
{
  "success": true,
  "strategy_id": 1,
  "rolled_back_to_version": "1.0.0",
  "new_version": "1.0.2"
}
```

---

### Live Trading

#### `POST /{strategy_id}/start`
Start live trading for a strategy.

**Request:**
```json
{
  "symbols": ["BTCUSDT", "ETHUSDT"],
  "exchange": "bybit",
  "account_type": "demo"
}
```

**Response:**
```json
{
  "success": true,
  "key": "511692487:1:bybit:demo",
  "strategy_name": "My RSI Strategy",
  "exchange": "bybit",
  "account_type": "demo",
  "symbols": ["BTCUSDT", "ETHUSDT"]
}
```

#### `POST /{strategy_id}/stop`
Stop live trading.

**Request:**
```json
{
  "exchange": "bybit",
  "account_type": "demo",
  "close_positions": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Strategy stopped successfully"
}
```

#### `POST /{strategy_id}/pause`
Pause live trading (keeps positions, stops new signals).

**Request:**
```json
{
  "exchange": "bybit",
  "account_type": "demo"
}
```

#### `POST /{strategy_id}/resume`
Resume paused strategy.

**Request:**
```json
{
  "exchange": "bybit",
  "account_type": "demo"
}
```

#### `GET /{strategy_id}/status`
Get live trading status.

**Response:**
```json
{
  "strategy_id": 1,
  "exchange": "bybit",
  "account_type": "demo",
  "status": "running",
  "started_at": "2024-12-30T10:00:00Z",
  "symbols": ["BTCUSDT", "ETHUSDT"],
  "open_positions": 2,
  "total_trades": 15,
  "total_pnl": 150.50
}
```

#### `GET /running`
Get all running strategies for current user.

**Response:**
```json
{
  "running": [
    {
      "strategy_id": 1,
      "strategy_name": "My RSI Strategy",
      "exchange": "bybit",
      "account_type": "demo",
      "status": "running",
      "symbols": ["BTCUSDT", "ETHUSDT"]
    }
  ],
  "count": 1
}
```

---

## Strategy Specification (StrategySpec)

### Full Schema

```typescript
interface StrategySpec {
  // Metadata
  name: string;
  description: string;
  version: string;
  author_id?: number;
  
  // Entry rules
  long_entry?: EntryRule;
  short_entry?: EntryRule;
  
  // Exit rules
  exit_rules: ExitRule[];
  
  // Risk management
  risk: RiskManagement;
  
  // Filters
  filters: Filters;
  
  // Timeframe settings
  primary_timeframe: string;  // "1m" | "5m" | "15m" | "30m" | "1h" | "4h" | "1d"
  higher_timeframes: string[];
  
  // Position settings
  pyramiding: number;  // Max entries per symbol
  allow_reverse: boolean;  // Allow reversing position
}

interface EntryRule {
  direction: "LONG" | "SHORT";
  groups: ConditionGroup[];
  group_operator: "AND" | "OR";
  enabled: boolean;
}

interface ConditionGroup {
  id: string;
  conditions: Condition[];
  operator: "AND" | "OR";
  enabled: boolean;
}

interface Condition {
  id: string;
  left: IndicatorConfig;
  operator: string;  // "<" | ">" | "crosses_above" | "between" | etc.
  right?: IndicatorConfig;  // For comparing two indicators
  value?: number;  // For comparing indicator to fixed value
  value2?: number;  // For "between" operator
  enabled: boolean;
  description: string;
}

interface IndicatorConfig {
  type: string;  // "rsi" | "ema" | "macd" | "bb" | etc.
  params: Record<string, any>;
  field?: string;  // For MACD: "macd" | "signal" | "histogram"
  timeframe?: string;  // Override timeframe
}

interface ExitRule {
  type: string;  // "take_profit" | "stop_loss" | "trailing_stop" | "breakeven" | "time_based" | "indicator"
  value?: number;
  conditions?: Condition[];  // For indicator-based exits
  params: Record<string, any>;
  enabled: boolean;
}

interface RiskManagement {
  position_size_percent: number;  // % of balance per trade
  max_positions: number;
  max_daily_trades: number;
  max_daily_loss_percent: number;
  leverage: number;
}

interface Filters {
  min_volume_usdt?: number;
  min_volatility?: number;
  max_volatility?: number;
  time_filters: TimeFilter[];
  excluded_symbols: string[];
  required_symbols: string[];
}
```

### Available Indicators

| Category | Indicators |
|----------|------------|
| **Trend** | ema, sma, wma, vwma, vwap, supertrend, ichimoku |
| **Oscillators** | rsi, stoch, stoch_rsi, cci, williams_r, mfi, ao, roc, momentum |
| **Volatility** | bb (Bollinger), atr, keltner, donchian |
| **Volume** | volume, obv, cvd, vwap |
| **Price** | price_close, price_open, price_high, price_low, price_hl2, price_hlc3 |
| **Other** | macd, adx, aroon, psar |

### Indicator Parameters

| Indicator | Parameters |
|-----------|------------|
| **EMA/SMA** | `period` (int) |
| **RSI** | `period` (int, default: 14) |
| **MACD** | `fast` (12), `slow` (26), `signal` (9), `field` ("macd", "signal", "histogram") |
| **Bollinger** | `period` (20), `std_dev` (2.0), `field` ("upper", "middle", "lower") |
| **ATR** | `period` (14) |
| **Stochastic** | `k_period` (14), `d_period` (3), `field` ("k", "d") |

---

## Error Handling

All endpoints return errors in this format:

```json
{
  "detail": "Error message here"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (no permission)
- `404` - Not Found
- `422` - Unprocessable Entity (invalid request body)
- `500` - Internal Server Error

---

## Examples

### Create and Backtest a Strategy

```bash
# 1. Generate strategy with AI
curl -X POST "http://localhost:8765/api/builder/strategies/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "RSI strategy for 15m timeframe with 3% take profit"}'

# 2. Create the strategy
curl -X POST "http://localhost:8765/api/builder/strategies" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @strategy.json

# 3. Run backtest
curl -X POST "http://localhost:8765/api/builder/strategies/1/backtest" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "15m", "start_date": "2024-01-01", "end_date": "2024-06-01"}'

# 4. Start live trading
curl -X POST "http://localhost:8765/api/builder/strategies/1/start" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["BTCUSDT", "ETHUSDT"], "exchange": "bybit", "account_type": "demo"}'
```

---

## Rate Limits

- **AI Generation:** 10 requests/minute per user
- **Backtest:** 20 requests/minute per user
- **Other endpoints:** 60 requests/minute per user

---

*Last Updated: December 30, 2025*
