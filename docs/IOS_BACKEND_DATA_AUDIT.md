# iOS ↔ Backend ↔ Database Data Flow Audit
**Date:** February 2026 | **Status:** COMPREHENSIVE AUDIT

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Portfolio / Balance Screen](#2-portfolio--balance-screen)
3. [Positions Screen](#3-positions-screen)
4. [Trade History Screen](#4-trade-history-screen)
5. [Trading Stats Screen](#5-trading-stats-screen)
6. [Strategy Performance (Stats)](#6-strategy-performance)
7. [Field Name Mismatches](#7-field-name-mismatches)
8. [Missing / Hardcoded Data](#8-missing--hardcoded-data)
9. [Critical Recommendations](#9-critical-recommendations)

---

## 1. Executive Summary

### Overall Status: ⚠️ MOSTLY FUNCTIONAL — 7 ISSUES FOUND

The iOS app has robust defensive decoding (dual CodingKeys, optionals with fallbacks), which masks many potential mismatches. However, several data fields are **hardcoded to 0** in the iOS layer, and a few field name inconsistencies exist between layers.

### Critical Findings

| # | Severity | Screen | Issue |
|---|----------|--------|-------|
| 1 | 🔴 HIGH | Stats | `todayPnl`, `weekPnl`, `monthPnl` hardcoded to **0** — displayed but never populated |
| 2 | 🔴 HIGH | Stats | `bestTrade`, `worstTrade` hardcoded to **0** — displayed but never populated |
| 3 | 🟡 MED | Portfolio | `/portfolio/summary` endpoint — only queries Bybit; ignores HyperLiquid exchange entirely for spot/futures balance |
| 4 | 🟡 MED | Portfolio | Spot `pnl` and `pnl_pct` always return **0** ("Would need historical data") |
| 5 | 🟡 MED | Portfolio | Futures `realized_pnl` always returns **0** ("Would need historical") |
| 6 | 🟢 LOW | Trade History | DB column `pnl_pct` vs query alias `pnl_percent` naming inconsistency (currently handled by iOS dual keys) |
| 7 | 🟢 LOW | Positions | Side format `"long"/"short"` (Bybit backend) vs `"Buy"/"Sell"` (iOS `isLong` checks) — iOS handles both |

---

## 2. Portfolio / Balance Screen

### iOS View: `PortfolioView.swift` (777 lines)

**Endpoint Called:** `GET /portfolio/summary?period=X&account_type=Y&exchange=Z`

**iOS Models (defined inline in PortfolioView.swift lines 57-200):**

#### `PortfolioSummary`
| iOS Field | CodingKey | Type | Backend Source |
|-----------|-----------|------|----------------|
| `spot` | `spot` | `PortfolioSpotData?` | `portfolio.py` → `get_spot_balance()` |
| `futures` | `futures` | `PortfolioFuturesData?` | `portfolio.py` → `get_futures_balance()` |
| `totalUsd` | `total_usd` | `Double` | `spot.total_usd + futures.total_equity` |
| `pnlPeriod` | `pnl_period` | `Double` | Sum of trade PnLs in period |
| `pnlPeriodPct` | `pnl_period_pct` | `Double` | `pnl / equity * 100` |
| `period` | `period` | `String` | Echo of query param |
| `chartData` | `chart_data` | `[PnLDataPoint]` | `build_chart_data()` from trade_logs |
| `candles` | `candles` | `[CandleCluster]` | `build_candle_clusters()` from trade_logs |

**Verdict: ✅ MATCH** — All fields align with the backend `PortfolioSummary` Pydantic model at `portfolio.py:87-97`.

#### `PortfolioSpotData`
| iOS Field | CodingKey | Type | Backend Value |
|-----------|-----------|------|---------------|
| `totalUsd` | `total_usd` | `Double` | ✅ Sum of coin usdValues |
| `pnl` | `pnl` | `Double` | ⚠️ **Always 0** — `portfolio.py:219` has comment "Would need historical data" |
| `pnlPct` | `pnl_pct` | `Double` | ⚠️ **Always 0** — same reason |
| `assets` | `assets` | `[AssetBalance]` | ✅ Array of coin balances from Bybit UNIFIED account |

#### `PortfolioFuturesData`
| iOS Field | CodingKey | Type | Backend Value |
|-----------|-----------|------|---------------|
| `totalEquity` | `total_equity` | `Double` | ✅ `wallet.totalEquity` |
| `available` | `available` | `Double` | ✅ `wallet.totalAvailableBalance` |
| `positionMargin` | `position_margin` | `Double` | ✅ `wallet.totalPositionIM` |
| `unrealizedPnl` | `unrealized_pnl` | `Double` | ✅ `wallet.totalUnrealisedPnl` |
| `realizedPnl` | `realized_pnl` | `Double` | ⚠️ **Always 0** — `portfolio.py:316` says "Would need historical" |
| `positionCount` | `position_count` | `Int` | ✅ Count of positions with size > 0 |

#### `PnLDataPoint`
| iOS Field | CodingKey | Type | Backend Value |
|-----------|-----------|------|---------------|
| `timestamp` | `timestamp` | `String` | ✅ ISO format bucket timestamp |
| `pnl` | `pnl` | `Double` | ✅ Sum of PnL in bucket |
| `cumulativePnl` | `cumulative_pnl` | `Double` | ✅ Running total |
| `tradeCount` | `trade_count` | `Int` | ✅ Count of trades in bucket |

#### `CandleCluster`
| iOS Field | CodingKey | Type | Backend Value |
|-----------|-----------|------|---------------|
| `timestamp` | `timestamp` | `String` | ✅ |
| `openPnl` | `open_pnl` | `Double` | ✅ Cumulative PnL at candle open |
| `highPnl` | `high_pnl` | `Double` | ✅ Max cumulative PnL in candle |
| `lowPnl` | `low_pnl` | `Double` | ✅ Min cumulative PnL in candle |
| `closePnl` | `close_pnl` | `Double` | ✅ Cumulative PnL at candle close |
| `volume` | `volume` | `Double` | ✅ (volume formula is questionable but schema matches) |
| `tradeCount` | `trade_count` | `Int` | ✅ |
| `longCount` | `long_count` | `Int` | ✅ |
| `shortCount` | `short_count` | `Int` | ✅ |
| `longPnl` | `long_pnl` | `Double` | ✅ |
| `shortPnl` | `short_pnl` | `Double` | ✅ |
| `winCount` | `win_count` | `Int` | ✅ |
| `lossCount` | `loss_count` | `Int` | ✅ |
| `avgWin` | `avg_win` | `Double` | ✅ |
| `avgLoss` | `avg_loss` | `Double` | ✅ |
| `strategies` | `strategies` | `[String: StrategyCluster]` | ✅ Backend returns `{name: {count, pnl, win_rate}}` |
| `symbols` | `symbols` | `[String: SymbolCluster]` | ✅ Backend returns `{symbol: {count, pnl}}` |
| `trades` | `trades` | `[ClusterTrade]` | ✅ Simplified trade array |

**iOS `StrategyCluster`** expects `{count, pnl, winRate(win_rate)}` — backend returns `{count, pnl, wins, win_rate}`. **Match** (extra `wins` field is safely ignored by iOS).

**iOS `SymbolCluster`** expects `{count, pnl}` — backend returns `{count, pnl}`. **✅ Exact match.**

**iOS `ClusterTrade`** expects `{id, symbol, side, pnl, pnlPct(pnl_pct), strategy, exitReason(exit_reason), ts}` — backend returns all of these. **✅ Match.**

### 🔴 ISSUE: Portfolio endpoint ignores HyperLiquid

`portfolio.py:get_spot_balance()` and `get_futures_balance()` **only query the Bybit API** — they use `demo_api_key`/`real_api_key` and hit `api-demo.bybit.com` or `api.bybit.com`. The `exchange` query parameter is only used for filtering `trade_logs` in `get_trades_for_period()`, not for balance.

**Impact:** When `exchange=hyperliquid`, the Portfolio screen shows **$0 spot and $0 futures** because no HyperLiquid adapter is used.

### Secondary Data Sources in PortfolioView

PortfolioView also uses data from `TradingService`:
- `tradingService.tradingStats` → `GET /trading/stats` (for quick stats grid)
- `tradingService.trades` → `GET /trading/trades` (for recent trades list)
- `tradingService.positions` → `GET /trading/positions` (for futures tab)
- `tradingService.hlSpotBalance` → `GET /trading/balance/spot` (for HL spot card)

These are well-aligned (see sections 3-5 below).

---

## 3. Positions Screen

### iOS View: `PositionsView.swift` (509 lines)

**Endpoints Called:**
- `GET /trading/positions?exchange=X&account_type=Y` → `[Position]`
- `GET /trading/orders?exchange=X&account_type=Y` → `[Order]`

### Position Model (Models.swift ~line 250-440)

| iOS Field | CodingKey(s) | Type | Backend `/trading/positions` response | Status |
|-----------|-------------|------|---------------------------------------|--------|
| `symbol` | `symbol` | `String` | `symbol` | ✅ |
| `side` | `side` | `String` | `"long"` / `"short"` (Bybit), raw (HL) | ✅ iOS `isLong` checks "buy"/"Buy"/"long" |
| `size` | `size` | `Double` | `float(pos.size)` | ✅ |
| `entryPrice` | `entry_price` | `Double` | `float(pos.avgPrice)` | ✅ |
| `markPrice` | `mark_price` | `Double` | `float(pos.markPrice)` | ✅ |
| `leverage` | `leverage` | `FlexibleInt` | `int(pos.leverage)` | ✅ (handles String↔Int) |
| `pnl` | `pnl` OR `unrealized_pnl` | `Double?` | `unrealisedPnl` | ✅ Dual key |
| `roe` | `roe` OR `pnl_percent` | `Double?` | `float(curRealisedPnl)` (NOTE: this is wrong — it should be ROE) | ⚠️ See below |
| `liqPrice` | `liq_price` OR `liquidation_price` | `Double?` | `liqPrice` | ✅ |
| `tpPrice` | `tp_price` OR `take_profit` | `Double?` | From `active_positions` DB | ✅ |
| `slPrice` | `sl_price` OR `stop_loss` | `Double?` | From `active_positions` DB | ✅ |
| `strategy` | `strategy` | `String?` | From `active_positions` DB | ✅ |
| `margin` | `margin` | `Double?` | `positionIM` (Bybit) | ✅ |
| `positionValue` | `position_value` | `Double?` | `positionValue` (Bybit) | ✅ |
| `exchange` | `exchange` | `String?` | `exchange` param or "bybit"/"hyperliquid" | ✅ |
| `accountType` | `account_type` | `String?` | `account_type` param | ✅ |
| `useAtr` | `use_atr` | `Bool?` | From `active_positions` DB | ✅ |
| `atrActivated` | `atr_activated` | `Bool?` | From `active_positions` DB | ✅ |

#### ⚠️ ROE Issue
Backend `trading.py:574` sets `"roe": float(pos.get("curRealisedPnl", 0))`. This is the **realized PnL**, NOT the return on equity (ROE). The iOS app displays this as ROE percentage. The correct Bybit field for ROE would be calculated as `unrealizedPnl / initialMargin * 100%`.

**Impact:** Position ROE displays incorrect values — shows realized PnL instead of percentage return.

### Order Model (Models.swift ~line 450-550)

| iOS Field | CodingKey(s) | Type | Backend `/trading/orders` | Status |
|-----------|-------------|------|---------------------------|--------|
| `orderId` | `order_id` / `orderId` / `id` | `String` | `orderId` | ✅ Triple fallback |
| `symbol` | `symbol` | `String` | `symbol` | ✅ |
| `side` | `side` | `String` | `side` | ✅ |
| `orderType` | `order_type` / `type` | `String?` | `orderType` | ✅ |
| `qty` | `qty` / `size` | `Double` | `qty` | ✅ |
| `price` | `price` | `Double?` | `price` | ✅ |
| `triggerPrice` | `trigger_price` | `Double?` | `triggerPrice` | ✅ |
| `status` | `status` | `String?` | `orderStatus` | ✅ |
| `createdAt` | `created_at` | `String?` | `createdTime` | ✅ |

**Verdict: ✅ MATCH** — iOS models handle all backend response variants.

---

## 4. Trade History Screen

### iOS View: `TradeHistoryView.swift` (242 lines)

**Endpoint Called:** `GET /trading/trades?exchange=X&account_type=Y&limit=N`

### Trade Model (Models.swift ~line 550-650)

| iOS Field | CodingKey(s) | Type | Backend Response | DB Column | Status |
|-----------|-------------|------|-----------------|-----------|--------|
| `symbol` | `symbol` | `String` | `symbol` | `symbol` | ✅ |
| `side` | `side` | `String` | `side` | `side` | ✅ |
| `entryPrice` | `entry_price` | `Double?` | `entry_price` | `entry_price` | ✅ |
| `exitPrice` | `exit_price` | `Double?` | `exit_price` | `exit_price` | ✅ |
| `exitReason` | `exit_reason` | `String?` | `exit_reason` | `exit_reason` | ✅ |
| `pnl` | `pnl` | `Double?` | `pnl` (float) | `pnl` | ✅ |
| `pnlPct` | `pnl_pct` / `pnl_percent` | `Double?` | ⚠️ See below | ⚠️ See below | ⚠️ |
| `strategy` | `strategy` | `String?` | `strategy` | `strategy` | ✅ |
| `timestamp` | `ts` / `timestamp` | `String` | `ts`, `timestamp` | `ts` | ✅ Dual key |

#### ⚠️ `pnl_pct` vs `pnl_percent` chain

The data flows through 3 layers with different field names:

1. **DB column:** `pnl_pct` (in `trade_logs` table)
2. **`db.py:get_trade_logs_list()`** at line ~3718: Returns it as `"pnl_percent"` (aliased in SELECT)
3. **`trading.py` `/trades` endpoint** at line ~1374: Copies `t.get("pnl_pct")` AND `t.get("pnl_percent")` — returns BOTH keys
4. **iOS** `Trade` model: Has dual CodingKeys `pnl_pct` and `pnl_percent`

**Current status:** ✅ Works due to iOS dual keys AND backend sending both keys. But the backend `stats.py:dashboard` endpoint at line ~162 accesses `t.get("pnl_pct")` which returns `None` because `get_trade_logs_list()` returns the field as `"pnl_percent"`. This causes `returnPct` in the dashboard to be **incorrect** (likely 0).

---

## 5. Trading Stats Screen

### iOS View: `StatsView.swift` (384 lines)

**Data Sources:**
- `StatsService.shared.dashboard` (from `GET /stats/dashboard`)
- `StatsService.shared.pnlHistory` (from `GET /stats/pnl-history`)
- `StatsService.shared.strategyReports` (from `GET /stats/strategy-report`)
- `TradingService.shared.tradingStats` (from `GET /trading/stats`)

### A. Dashboard (`GET /stats/dashboard`)

**Backend (stats.py line 52):** Returns `{"success": true, "data": {"summary": {...}, "pnlHistory": [...], ...}}`

**iOS `DashboardSummary` (StatsService.swift line 15):**

| iOS Field | Type | Backend `data.summary` field | Status |
|-----------|------|------------------------------|--------|
| `totalPnL` | `Double?` | `totalPnL` | ✅ camelCase match |
| `returnPct` | `Double?` | `returnPct` | ⚠️ Backend calculates from `pnl_pct` which may be `None` (see section 4) |
| `totalTrades` | `Int?` | `totalTrades` | ✅ |
| `winRate` | `Double?` | `winRate` | ✅ |
| `profitFactor` | `Double?` | `profitFactor` | ✅ |
| `maxDrawdown` | `Double?` | `maxDrawdown` | ✅ |
| `avgWin` | `Double?` | `avgWin` | ✅ |
| `avgLoss` | `Double?` | `avgLoss` | ✅ |
| `bestStreak` | `Int?` | `bestStreak` | ✅ |
| `worstStreak` | `Int?` | `worstStreak` | ✅ |
| `avgDuration` | `String?` | `avgDuration` | ✅ |
| `tradesPerDay` | `Double?` | `tradesPerDay` | ✅ |
| `pnlChange` | `Double?` | `pnlChange` | ✅ |
| `wins` | `Int?` | `wins` | ✅ |
| `losses` | `Int?` | `losses` | ✅ |
| `maxDrawdownAbs` | `Double?` | `maxDrawdownAbs` | ✅ |

**Verdict: ✅ MATCH on field names.** Backend uses camelCase in the summary dict.

### 🔴 DashboardStats Hardcoded Zeros (StatsService.swift line 62-82)

The `DashboardStats` convenience struct maps `DashboardSummary` but **hardcodes several fields:**

```swift
struct DashboardStats {
    let todayPnl: Double      // = 0  ← HARDCODED
    let weekPnl: Double       // = 0  ← HARDCODED
    let monthPnl: Double      // = 0  ← HARDCODED
    let bestTrade: Double     // = 0  ← HARDCODED
    let worstTrade: Double    // = 0  ← HARDCODED
    ...
}
```

**StatsView.swift displays these in the dashboard grid:**
- "Today" card → shows $0.00 always
- "Week" card → shows $0.00 always
- "Month" card → shows $0.00 always
- "Best Trade" card → shows $0.00 always
- "Worst Trade" card → shows $0.00 always

**Backend has the data:**
- `todayPnl` / `weekPnl` / `monthPnl` — NOT returned by `/stats/dashboard` endpoint. Would need separate queries (e.g., `get_rolling_24h_pnl()` for today, separate period queries for week/month).
- `bestTrade` / `worstTrade` — Available in `data.topTrades` from `/stats/dashboard` but NOT mapped in iOS.

### B. TradingStats (`GET /trading/stats`)

**iOS `TradingStats` (Models.swift ~line 650-760):**

| iOS Field | CodingKey(s) | Backend Field | Status |
|-----------|-------------|---------------|--------|
| `total` | `total` / `total_trades` | `total_trades` | ✅ Dual key |
| `wins` | `wins` / `winning_trades` | `winning_trades` | ✅ Dual key |
| `losses` | `losses` / `losing_trades` | `losing_trades` | ✅ Dual key |
| `winrate` | `winrate` / `win_rate` | `win_rate` | ✅ Dual key |
| `totalPnl` | `total_pnl` | `total_pnl` | ✅ |
| `avgPnl` | `avg_pnl` | `avg_pnl` | ✅ |
| `avgWin` | `avg_win` | NOT returned | ⚠️ Backend doesn't return `avg_win` from `/trading/stats` |
| `avgLoss` | `avg_loss` | NOT returned | ⚠️ Backend doesn't return `avg_loss` from `/trading/stats` |
| `grossProfit` | `gross_profit` | `gross_profit` | ✅ |
| `grossLoss` | `gross_loss` | `gross_loss` | ✅ |
| `profitFactor` | `profit_factor` | `profit_factor` | ✅ |
| `maxDrawdown` | `max_drawdown` | NOT returned | ⚠️ Not calculated in `get_trade_stats()` |
| `bestPnl` | `best_pnl` / `best_trade` | `best_trade` | ✅ Dual key |
| `worstPnl` | `worst_pnl` / `worst_trade` | `worst_trade` | ✅ Dual key |
| `longCount` | `long_count` | `long_count` | ✅ |
| `shortCount` | `short_count` | `short_count` | ✅ |
| `longWinrate` | `long_winrate` | `long_winrate` | ✅ |
| `shortWinrate` | `short_winrate` | `short_winrate` | ✅ |
| `openCount` | `open_count` | `open_count` | ✅ |

**Fields iOS expects but backend `/trading/stats` doesn't provide:**
- `avg_win` — iOS defaults to `0`
- `avg_loss` — iOS defaults to `0`
- `max_drawdown` — iOS defaults to `0`

These ARE available from the `/stats/dashboard` endpoint summary but not from `/trading/stats`.

### C. PnL History (`GET /stats/pnl-history`)

**Backend returns:** `{"labels": [...], "values": [...], "period": "7d"}`

**iOS `PnlHistoryResponse` (StatsService.swift ~line 102):**

| iOS Field | Type | Backend Field | Status |
|-----------|------|---------------|--------|
| `labels` | `[String]` | `labels` | ✅ |
| `values` | `[Double]` | `values` | ✅ |
| `period` | `String?` | `period` | ✅ |

**Verdict: ✅ EXACT MATCH**

### D. Strategy Report (`GET /stats/strategy-report`)

**Backend returns:** `{"success": true, "strategies": [...], "totals": {...}, "period": "...", "exchange": "..."}`

**iOS `StrategyReport` (StatsService.swift ~line 115):**

| iOS Field | CodingKey | Backend Field | Status |
|-----------|-----------|---------------|--------|
| `name` | `name` | `name` | ✅ |
| `displayName` | `display_name` | `display_name` | ✅ |
| `trades` | `trades` | `trades` | ✅ |
| `wins` | `wins` | `wins` | ✅ |
| `losses` | `losses` | `losses` | ✅ |
| `winRate` | `win_rate` | `win_rate` | ✅ |
| `pnl` | `pnl` | `pnl` | ✅ |
| `avgPnl` | `avg_pnl` | `avg_pnl` | ✅ |
| `profitFactor` | `profit_factor` | `profit_factor` | ✅ |
| `totalVolume` | `total_volume` | `total_volume` | ✅ |

**Verdict: ✅ EXACT MATCH**

Backend also returns `best_trade`, `worst_trade`, `top_symbols`, `daily_pnl` per strategy — iOS ignores them (safely, since they're not declared in the Codable struct).

### E. Positions Summary (`GET /stats/positions-summary`)

**Backend returns:** `{"success": true, "positions": [...], "summary": {...}}`

**iOS `PositionsSummary` (StatsService.swift ~line 149):**

| iOS Field | CodingKey | Backend Field | Status |
|-----------|-----------|---------------|--------|
| `totalPositions` | `total_positions` | `total_positions` | ✅ |
| `totalPnl` | `total_pnl` | `total_pnl` | ✅ |
| `longCount` | `long_count` | `long_count` | ✅ |
| `shortCount` | `short_count` | `short_count` | ✅ |

Backend also returns `by_exchange`, `by_account_type`, `by_symbol` — iOS ignores them.

**Verdict: ✅ MATCH**

---

## 6. Strategy Performance

Strategy performance data comes from two endpoints:

1. **`GET /stats/strategy-report`** → Used by `StatsView.swift` → ✅ Fully aligned (see section 5D)
2. **`GET /trading/stats`** → Used by `PortfolioView.swift` quick stats grid → ✅ Mostly aligned (see section 5B)

No additional issues beyond what's documented above.

---

## 7. Field Name Mismatches (Complete List)

| # | Layer | Field Name 1 | Field Name 2 | Where | Impact |
|---|-------|-------------|-------------|-------|--------|
| 1 | DB → db.py | `pnl_pct` (column) | `pnl_percent` (alias in SELECT) | `get_trade_logs_list()` line ~3718 | ⚠️ Some code using `t.get("pnl_pct")` gets `None` |
| 2 | Backend → iOS | `roe` set to `curRealisedPnl` | iOS expects ROE % | `trading.py:574` | ⚠️ Wrong value displayed as ROE |
| 3 | Backend → iOS | `winning_trades` | iOS also accepts `wins` | `trading.py` `/stats` | ✅ Handled by dual keys |
| 4 | Backend → iOS | `total_trades` | iOS also accepts `total` | `trading.py` `/stats` | ✅ Handled by dual keys |
| 5 | Backend → iOS | `win_rate` | iOS also accepts `winrate` | `trading.py` `/stats` | ✅ Handled by dual keys |
| 6 | Backend → iOS | `best_trade` | iOS also accepts `best_pnl` | `trading.py` `/stats` | ✅ Handled by dual keys |
| 7 | Backend → iOS | Position side `"long"/"short"` | iOS checks `"buy"/"Buy"/"long"` | `trading.py:564` | ✅ Handled |

---

## 8. Missing / Hardcoded Data

### 🔴 Data Displayed But Never Populated

| Field | Screen | iOS Location | Current Value | Fix Required |
|-------|--------|-------------|---------------|-------------|
| `todayPnl` | Stats dashboard | `StatsService.swift:67` | **0** (hardcoded) | Add `get_rolling_24h_pnl()` to `/stats/dashboard` response, or create separate endpoint |
| `weekPnl` | Stats dashboard | `StatsService.swift:68` | **0** (hardcoded) | Add 7-day PnL aggregation to `/stats/dashboard` |
| `monthPnl` | Stats dashboard | `StatsService.swift:69` | **0** (hardcoded) | Add 30-day PnL aggregation to `/stats/dashboard` |
| `bestTrade` | Stats dashboard | `StatsService.swift:73` | **0** (hardcoded) | Map from `data.topTrades` in dashboard response (data exists!) |
| `worstTrade` | Stats dashboard | `StatsService.swift:74` | **0** (hardcoded) | Map from `data.topTrades` in dashboard response (data exists!) |

### 🟡 Backend Returns 0 / Stub Data

| Field | Endpoint | Backend Location | Reason | Fix Required |
|-------|----------|-----------------|--------|-------------|
| `spot.pnl` | `/portfolio/summary` | `portfolio.py:219` | "Would need historical data" | Calculate from 24h price changes or trade_logs |
| `spot.pnl_pct` | `/portfolio/summary` | `portfolio.py:220` | Same | Same |
| `futures.realized_pnl` | `/portfolio/summary` | `portfolio.py:316` | "Would need historical" | Query `get_rolling_24h_pnl()` or trade_logs |

### 🟡 Fields iOS Expects But Backend Doesn't Return

| iOS Field | Endpoint | Default | Impact |
|-----------|----------|---------|--------|
| `avg_win` | `/trading/stats` | `0` | Quick stats show 0 avg win |
| `avg_loss` | `/trading/stats` | `0` | Quick stats show 0 avg loss |
| `max_drawdown` | `/trading/stats` | `0` | Not displayed prominently |

---

## 9. Critical Recommendations

### Priority 1: Fix Hardcoded Stats (🔴 HIGH — User-visible zeros)

**Problem:** Stats dashboard shows $0 for Today/Week/Month PnL and Best/Worst trade.

**Fix in `stats.py` `/dashboard` endpoint (line ~52):**

```python
# Add to summary dict:
summary = {
    ...existing fields...
    # ADD THESE:
    "todayPnl": db.get_rolling_24h_pnl(user_id, account_type, exchange),
    "weekPnl": sum(t.get("pnl", 0) for t in week_trades),
    "monthPnl": sum(t.get("pnl", 0) for t in month_trades),
    "bestTrade": max((t.get("pnl", 0) for t in all_trades), default=0),
    "worstTrade": min((t.get("pnl", 0) for t in all_trades), default=0),
}
```

**Fix in iOS `DashboardStats` init (StatsService.swift line 62):**

```swift
self.todayPnl = s?.todayPnl ?? 0    // was: 0
self.weekPnl = s?.weekPnl ?? 0      // was: 0  
self.monthPnl = s?.monthPnl ?? 0    // was: 0
self.bestTrade = s?.bestTrade ?? 0   // was: 0
self.worstTrade = s?.worstTrade ?? 0 // was: 0
```

**Also add these fields to `DashboardSummary`:**
```swift
let todayPnl: Double?      // ADD
let weekPnl: Double?       // ADD
let monthPnl: Double?      // ADD
let bestTrade: Double?     // ADD (already exists as topTrades in backend)
let worstTrade: Double?    // ADD
```

### Priority 2: Fix Portfolio HyperLiquid Support (🟡 MED)

**Problem:** `/portfolio/summary` only queries Bybit for balance.

**Fix in `portfolio.py`:** Add HyperLiquid branch to `get_spot_balance()` and `get_futures_balance()`:

```python
async def get_futures_balance(user_id, account_type, exchange="bybit"):
    if exchange == "hyperliquid":
        from hl_adapter import HLAdapter
        hl_creds = db.get_all_user_credentials(user_id)
        private_key, is_testnet = get_hl_credentials_for_account(hl_creds, account_type)
        if private_key:
            adapter = HLAdapter(private_key=private_key, testnet=is_testnet)
            await adapter.initialize()
            balance = await adapter.get_balance()
            return FuturesPortfolio(
                total_equity=balance.get("equity", 0),
                available=balance.get("available", 0),
                ...
            )
    # existing Bybit code...
```

### Priority 3: Fix ROE Display (🟡 MED)

**Problem:** Position ROE shows realized PnL instead of percentage return.

**Fix in `trading.py` line 574:**
```python
# BEFORE:
"roe": float(pos.get("curRealisedPnl", 0)),

# AFTER:
initial_margin = float(pos.get("positionIM", 0))
unrealized_pnl = float(pos.get("unrealisedPnl", 0))
"roe": (unrealized_pnl / initial_margin * 100) if initial_margin > 0 else 0,
```

### Priority 4: Fix pnl_pct Naming Chain (🟢 LOW)

**Problem:** `get_trade_logs_list()` returns `pnl_percent` but some callers expect `pnl_pct`.

**Fix in `db.py:get_trade_logs_list()`:**
```python
# Return BOTH aliases:
trade_dict["pnl_pct"] = trade_dict.get("pnl_percent", 0)
```

Or fix the SELECT to alias it as `pnl_pct`:
```sql
SELECT ..., pnl_pct AS pnl_pct, ...  -- instead of aliasing to pnl_percent
```

### Priority 5: Add Missing Fields to `/trading/stats` (🟢 LOW)

Add `avg_win`, `avg_loss` to the `/trading/stats` response in `trading.py`:

```python
# In get_trade_stats() or the endpoint:
stats["avg_win"] = stats["gross_profit"] / stats["wins"] if stats["wins"] > 0 else 0
stats["avg_loss"] = stats["gross_loss"] / stats["losses"] if stats["losses"] > 0 else 0
```

---

## Appendix: Complete Endpoint ↔ iOS Mapping

| iOS Service | iOS Method | Endpoint | Backend File | Line |
|-------------|-----------|----------|-------------|------|
| TradingService | `fetchBalance()` | `GET /trading/balance` | `trading.py` | 303 |
| TradingService | `fetchHLSpotBalance()` | `GET /trading/balance/spot` | `trading.py` | 442 |
| TradingService | `fetchPositions()` | `GET /trading/positions` | `trading.py` | 488 |
| TradingService | `fetchOrders()` | `GET /trading/orders` | `trading.py` | ~650 |
| TradingService | `fetchTrades()` | `GET /trading/trades` | `trading.py` | 1323 |
| TradingService | `fetchStats()` | `GET /trading/stats` | `trading.py` | 1401 |
| StatsService | `fetchDashboard()` | `GET /stats/dashboard` | `stats.py` | 52 |
| StatsService | `fetchPnlHistory()` | `GET /stats/pnl-history` | `stats.py` | 308 |
| StatsService | `fetchStrategyReport()` | `GET /stats/strategy-report` | `stats.py` | 389 |
| StatsService | `fetchPositionsSummary()` | `GET /stats/positions-summary` | `stats.py` | 549 |
| PortfolioView | `loadPortfolioData()` | `GET /portfolio/summary` | `portfolio.py` | 567 |

All endpoints are registered in `webapp/app.py` with `/api` prefix.
iOS `Config.swift` endpoint constants at lines 41-143 correctly map to all backend routes.

---

*Generated by comprehensive iOS ↔ Backend ↔ DB data flow audit*
