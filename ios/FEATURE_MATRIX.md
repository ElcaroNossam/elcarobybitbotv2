# Lyxen Trading - Feature Matrix
## WebApp vs iOS App Comparison

**Last Updated:** January 24, 2026  
**iOS Build Status:** ✅ BUILD SUCCEEDED (0 errors, 0 warnings)

---

## 📊 Summary

| Platform | Screens | API Endpoints | Status |
|----------|---------|---------------|--------|
| **WebApp** | 17 pages | 85+ endpoints | Production |
| **iOS App** | 12 screens | 45+ endpoints | Ready for Testing |

---

## 🎯 Feature Comparison

### 1️⃣ Authentication

| Feature | WebApp | iOS | Status |
|---------|--------|-----|--------|
| Telegram Login | ✅ | ✅ | ✅ |
| Email Registration | ✅ | ✅ | ✅ |
| Email Verification | ✅ | ✅ | ✅ |
| Password Login | ✅ | ✅ | ✅ |
| JWT Token Refresh | ✅ | ✅ | ✅ |
| Logout | ✅ | ✅ | ✅ |

**iOS Files:**
- `Services/AuthManager.swift` - Authentication logic
- `Views/Auth/LoginView.swift` - Login/Register UI

---

### 2️⃣ Portfolio & Dashboard

| Feature | WebApp | iOS | Status |
|---------|--------|-----|--------|
| Total Balance | ✅ | ✅ | ✅ |
| Equity/Available | ✅ | ✅ | ✅ |
| Today PnL | ✅ | ✅ | ✅ |
| Week PnL | ✅ | ✅ | ✅ |
| Month PnL | ✅ | ✅ | ✅ |
| PnL Chart | ✅ | ⚠️ Placeholder | Need real data |
| Active Positions Count | ✅ | ✅ | ✅ |
| Open Orders Count | ✅ | ✅ | ✅ |
| Trading Stats | ✅ | ✅ | ✅ |
| Exchange Switcher | ✅ | ✅ | ✅ |
| Account Type Switcher | ✅ | ✅ | ✅ |

**iOS Files:**
- `Views/Portfolio/PortfolioView.swift` - Dashboard UI

---

### 3️⃣ Positions Management

| Feature | WebApp | iOS | Status |
|---------|--------|-----|--------|
| View All Positions | ✅ | ✅ | ✅ |
| Position Details (symbol, side, entry, size) | ✅ | ✅ | ✅ |
| Unrealized PnL | ✅ | ✅ | ✅ |
| TP/SL Display | ✅ | ✅ | ✅ |
| Modify TP/SL | ✅ | ✅ | ✅ |
| Close Single Position | ✅ | ✅ | ✅ |
| Close All Positions | ✅ | ✅ | ✅ |
| Leverage Display | ✅ | ✅ | ✅ |

**iOS Files:**
- `Views/Portfolio/PositionsView.swift` - Positions list

---

### 4️⃣ Trade History

| Feature | WebApp | iOS | Status |
|---------|--------|-----|--------|
| Trade List | ✅ | ✅ | ✅ |
| Exit Reason | ✅ | ✅ | ✅ |
| Realized PnL | ✅ | ✅ | ✅ |
| Strategy Tag | ✅ | ✅ | ✅ |
| Date Filter | ✅ | ✅ | ✅ |
| Export CSV | ✅ | ❌ | TODO |

**iOS Files:**
- `Views/Portfolio/TradeHistoryView.swift` - History list

---

### 5️⃣ Trading Terminal

| Feature | WebApp | iOS | Status |
|---------|--------|-----|--------|
| Symbol Picker | ✅ | ✅ | ✅ |
| Symbol Search | ✅ | ✅ | ✅ |
| Market/Limit Order | ✅ | ✅ | ✅ |
| Long/Short | ✅ | ✅ | ✅ |
| Set Leverage | ✅ | ✅ | ✅ |
| Set TP% | ✅ | ✅ | ✅ |
| Set SL% | ✅ | ✅ | ✅ |
| Entry % | ✅ | ✅ | ✅ |
| Position Calculator | ✅ | ✅ | ✅ |
| Quick Trade Buttons | ✅ | ✅ | ✅ |
| Orderbook | ✅ | ❌ | TODO |
| Price Chart | ✅ (TradingView) | ❌ | TODO |
| Recent Trades | ✅ | ❌ | TODO |

**iOS Files:**
- `Views/Trading/TradingView.swift` - Trading interface
- `Views/Trading/SymbolPickerView.swift` - Symbol selection

---

### 6️⃣ Orders Management

| Feature | WebApp | iOS | Status |
|---------|--------|-----|--------|
| View Open Orders | ✅ | ✅ | ✅ |
| Cancel Single Order | ✅ | ✅ | ✅ |
| Cancel All Orders | ✅ | ✅ | ✅ |

**iOS Files:**
- Part of `Views/Portfolio/PositionsView.swift`

---

### 7️⃣ Market Overview

| Feature | WebApp | iOS | Status |
|---------|--------|-----|--------|
| Symbol List | ✅ | ✅ | ✅ |
| Real-time Prices | ✅ (WebSocket) | ✅ (WebSocket) | ✅ |
| 24h Change % | ✅ | ✅ | ✅ |
| Volume | ✅ | ⚠️ | Need format |
| Search/Filter | ✅ | ✅ | ✅ |
| Symbol Details | ✅ | ❌ | TODO |

**iOS Files:**
- `Views/Trading/MarketView.swift` - Market list
- `Services/WebSocketService.swift` - Real-time data

---

### 8️⃣ Strategies

| Feature | WebApp | iOS | Status |
|---------|--------|-----|--------|
| My Strategies List | ✅ | ✅ | ✅ |
| Strategy Settings | ✅ | ⚠️ | Basic UI |
| Enable/Disable | ✅ | ✅ | ✅ |
| Per-side Settings (Long/Short) | ✅ | ❌ | TODO |
| DCA Settings | ✅ | ❌ | TODO |
| ATR Settings | ✅ | ❌ | TODO |

**iOS Files:**
- `Views/Strategies/StrategiesView.swift` - Strategy list
- `Services/StrategyService.swift` - Strategy API

---

### 9️⃣ Marketplace

| Feature | WebApp | iOS | Status |
|---------|--------|-----|--------|
| Browse Strategies | ✅ | ✅ | ✅ |
| Strategy Details | ✅ | ⚠️ | Basic |
| Purchase Strategy | ✅ | ❌ | TODO |
| Rate Strategy | ✅ | ❌ | TODO |
| Seller Stats | ✅ | ❌ | TODO |
| Top Performers | ✅ | ❌ | TODO |

**iOS Files:**
- Part of `Views/Strategies/StrategiesView.swift`

---

### 🔟 Backtesting

| Feature | WebApp | iOS | Status |
|---------|--------|-----|--------|
| Run Backtest | ✅ | ✅ | ✅ |
| Strategy Selection | ✅ | ✅ | ✅ |
| Symbol Selection | ✅ | ✅ | ✅ |
| Timeframe Selection | ✅ | ✅ | ✅ |
| Period (Days) | ✅ | ✅ | ✅ |
| Initial Balance | ✅ | ✅ | ✅ |
| Risk per Trade | ✅ | ✅ | ✅ |
| SL/TP % | ✅ | ✅ | ✅ |
| Results Display | ✅ | ✅ | ✅ |
| Equity Curve | ✅ | ❌ | TODO |
| Trade List | ✅ | ⚠️ | Basic |
| Compare Strategies | ✅ | ❌ | TODO |
| AI Optimization | ✅ | ❌ | TODO |

**iOS Files:**
- `Views/Strategies/BacktestView.swift` - Backtest UI
- `Services/StrategyService.swift` - runBacktest()

---

### 1️⃣1️⃣ Settings

| Feature | WebApp | iOS | Status |
|---------|--------|-----|--------|
| User Profile | ✅ | ✅ | ✅ |
| Exchange Selection | ✅ | ✅ | ✅ |
| Default Leverage | ✅ | ✅ | ✅ |
| Default TP/SL | ✅ | ✅ | ✅ |
| Max Positions | ✅ | ✅ | ✅ |
| API Keys (Bybit) | ✅ | ✅ | ✅ |
| API Keys (HyperLiquid) | ✅ | ✅ | ✅ |
| Trade Notifications | ✅ | ✅ | ✅ |
| Signal Notifications | ✅ | ✅ | ✅ |
| Language Selection | ✅ | ⚠️ | System |
| Theme (Dark/Light) | ✅ | ⚠️ | Dark only |
| About/Version | ✅ | ✅ | ✅ |
| Logout | ✅ | ✅ | ✅ |

**iOS Files:**
- `Views/Settings/SettingsView.swift` - Main settings
- `Views/Settings/SubSettingsViews.swift` - Sub-pages

---

### 1️⃣2️⃣ Screener (Advanced)

| Feature | WebApp | iOS | Status |
|---------|--------|-----|--------|
| Multi-Exchange Data | ✅ | ❌ | TODO |
| OI Changes | ✅ | ❌ | TODO |
| Volume Spikes | ✅ | ❌ | TODO |
| Custom Filters | ✅ | ❌ | TODO |
| Real-time Updates | ✅ (WebSocket) | ❌ | TODO |

---

### 1️⃣3️⃣ Admin Panel

| Feature | WebApp | iOS | Status |
|---------|--------|-----|--------|
| User Management | ✅ | ❌ | N/A (Web only) |
| System Stats | ✅ | ❌ | N/A |
| License Management | ✅ | ❌ | N/A |

---

### 1️⃣4️⃣ Payments & LYXEN Token

| Feature | WebApp | iOS | Status |
|---------|--------|-----|--------|
| LYXEN Balance | ✅ | ❌ | TODO |
| Purchase LYXEN | ✅ | ❌ | TODO |
| TON Payments | ✅ | ❌ | TODO |
| Transaction History | ✅ | ❌ | TODO |

---

## 📁 iOS Project Structure

```
ios/LyxenTrading/
├── App/
│   ├── LyxenTradingApp.swift    # App entry point
│   ├── AppState.swift           # Global state
│   └── Config.swift             # API endpoints
├── Models/
│   └── Models.swift             # All data models
├── Services/
│   ├── AuthManager.swift        # Authentication
│   ├── NetworkService.swift     # HTTP client
│   ├── TradingService.swift     # Trading API
│   ├── StrategyService.swift    # Strategy API
│   └── WebSocketService.swift   # Real-time data
├── ViewModels/
│   └── ViewModels.swift         # View models
├── Views/
│   ├── Auth/LoginView.swift
│   ├── MainTabView.swift
│   ├── Portfolio/
│   │   ├── PortfolioView.swift
│   │   ├── PositionsView.swift
│   │   └── TradeHistoryView.swift
│   ├── Trading/
│   │   ├── TradingView.swift
│   │   ├── MarketView.swift
│   │   └── SymbolPickerView.swift
│   ├── Strategies/
│   │   ├── StrategiesView.swift
│   │   └── BacktestView.swift
│   ├── Settings/
│   │   ├── SettingsView.swift
│   │   └── SubSettingsViews.swift
│   └── Components/
│       └── LoadingView.swift
└── Utils/
    ├── Utilities.swift
    └── Colors.swift
```

---

## ✅ What Works in iOS App

1. **Authentication** - Email/Telegram login, JWT tokens
2. **Portfolio** - Balance, PnL, stats
3. **Positions** - View, close, modify TP/SL
4. **Trading** - Place orders, set leverage
5. **Market** - Real-time prices via WebSocket
6. **Strategies** - View, basic settings
7. **Backtest** - Run backtests with all parameters
8. **Settings** - API keys, preferences

---

## ❌ TODO for iOS App (Priority)

### High Priority
1. **Price Chart** - Integrate TradingView or native charts
2. **Orderbook** - Real-time order book display
3. **Per-side Strategy Settings** - Long/Short separate configs
4. **DCA Settings** - Dollar-cost averaging config

### Medium Priority
5. **Screener** - Market screener with filters
6. **LYXEN Token** - Balance and purchase
7. **Marketplace Purchase** - Buy strategies
8. **Export CSV** - Trade history export

### Low Priority
9. **AI Optimization** - Backtest optimization
10. **Light Theme** - Optional light mode
11. **Localization** - Multi-language support

---

## 🔧 Build Instructions

```bash
# 1. Generate Xcode project
cd ios/LyxenTrading
xcodegen generate

# 2. Build
xcodebuild -project LyxenTrading.xcodeproj \
  -scheme LyxenTrading \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  build

# 3. Run in Xcode
open LyxenTrading.xcodeproj
# Press Cmd+R to run
```

---

## 🌐 API Endpoints Used by iOS

### Auth
- POST `/auth/email/login`
- POST `/auth/email/register`
- POST `/auth/email/verify`
- POST `/auth/telegram`
- POST `/auth/refresh`

### Users
- GET `/users/me`
- GET/PUT `/users/settings`
- POST `/users/exchange`
- POST `/users/switch-account-type`
- GET/POST `/users/api-keys`
- GET/PUT `/users/strategy-settings`

### Trading
- GET `/trading/balance`
- GET `/trading/positions`
- GET `/trading/orders`
- GET `/trading/symbols`
- POST `/trading/order`
- POST `/trading/close`
- POST `/trading/close-all`
- POST `/trading/leverage`
- POST `/trading/modify-tpsl`
- POST `/trading/cancel`
- POST `/trading/cancel-all-orders`
- GET `/trading/trades`
- GET `/trading/stats`

### Backtest
- POST `/backtest/run`
- GET `/backtest/strategies`

### Marketplace
- GET `/marketplace/strategies`
- GET `/marketplace/purchased`

### WebSocket
- `/ws/market` - Real-time ticker data

---

*Generated by Lyxen iOS Audit - January 24, 2026*
