# 🧪 ElCaro Backtest Module - Complete Guide

**Last Updated:** December 24, 2025  
**Status:** ✅ Fully Integrated  
**URL:** `https://YOUR-DOMAIN/backtest`

---

## 🎯 Overview

Полноценный модуль для **динамического виртуального безграничного тестирования** торговых стратегий с визуальным конструктором, оптимизацией параметров и реалтайм симуляцией.

### 🌟 Key Features

1. **📊 Visual Strategy Builder** - Drag & drop конструктор стратегий
2. **⚡ Real-time Backtesting** - Мгновенное тестирование на исторических данных
3. **🎲 Monte Carlo Simulation** - Анализ рисков и стабильности (1000+ симуляций)
4. **🔧 Parameter Optimization** - Автоматический поиск лучших параметров
5. **📈 Walk-Forward Analysis** - Защита от overfitting
6. **🎬 Strategy Replay** - Визуализация сделок по таймлайну
7. **🔴 Live Mode** - Реалтайм тестирование на текущем рынке
8. **📦 Strategy Marketplace** - Импорт/экспорт готовых стратегий

---

## 🗺️ Navigation

### Доступ к модулю:

1. **С главной страницы:** `/` → Features → "Strategy Backtesting" → "Open Backtester"
2. **Из терминала:** `/terminal` → Header → <i class="fas fa-chart-line"></i> (кнопка Backtest)
3. **Из скринера:** `/screener` → Header → "Backtest"
4. **Прямой URL:** `/backtest`

### Обновленная навигация:

```
Terminal Header:
┌──────────────────────────────────────────────────────────┐
│ [ElCaro Logo] ... [Backtest] [Screener] [Dashboard] [⚙] │
└──────────────────────────────────────────────────────────┘

Backtest Header:
┌──────────────────────────────────────────────────────────┐
│ [ElCaro] [Terminal] [Strategies] [Backtester*] [Market] │
└──────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

### Frontend (backtest.html)
```
📁 /webapp/templates/backtest.html (3610 lines)
├── Header Navigation
├── Sidebar (Strategy Selector)
│   ├── Pre-built Strategies
│   │   ├── ElCaro AI Strategy
│   │   ├── RSI + Bollinger Bands
│   │   ├── Trend Following
│   │   ├── Mean Reversion
│   │   ├── Breakout Hunter
│   │   └── MACD Crossover
│   └── Custom Strategies
├── Main Content Area
│   ├── Configuration Panel
│   │   ├── Symbol Selection
│   │   ├── Timeframe (1m → 1d)
│   │   ├── Period (Days)
│   │   ├── Initial Balance
│   │   ├── Risk per Trade
│   │   ├── Stop Loss / Take Profit
│   │   └── Advanced Options
│   ├── Action Buttons
│   │   ├── Run Backtest
│   │   ├── Monte Carlo
│   │   ├── Optimize
│   │   ├── Quick Compare
│   │   └── Live Mode
│   ├── Results Panel
│   │   ├── Summary Stats
│   │   ├── Performance Metrics
│   │   ├── Equity Curve Chart
│   │   └── Trade History Table
│   ├── Strategy Builder
│   │   ├── Entry Conditions (Visual)
│   │   ├── Exit Conditions (Visual)
│   │   ├── Risk Management
│   │   └── Filters & Timeframes
│   └── Advanced Tools
│       ├── Walk-Forward Analysis
│       ├── Parameter Optimization
│       └── Correlation Matrix
└── WebSocket Connection (Live Updates)
```

### Backend APIs

```python
# Backtest API Endpoints
/api/backtest/run                # POST - Run backtest
/api/backtest/optimize            # POST - Optimize parameters
/api/backtest/monte-carlo         # POST - Monte Carlo simulation
/api/backtest/quick-compare       # POST - Quick strategy comparison

# Enhanced Backtest API (V2)
/api/backtest-v2/run              # POST - Advanced backtest with more metrics
/api/backtest-v2/walk-forward     # POST - Walk-forward analysis
/api/backtest-v2/correlation      # POST - Strategy correlation matrix

# Strategy Builder API
/api/strategy-backtest/custom     # POST - Test custom strategy
/api/strategy-backtest/validate   # POST - Validate strategy logic
/api/strategy-backtest/export     # POST - Export strategy JSON
/api/strategy-backtest/import     # POST - Import strategy JSON

# WebSocket Real-time Updates
/ws/backtest/{user_id}            # WebSocket - Live backtest updates
```

---

## 🎨 Visual Strategy Builder

### Entry Conditions (Drag & Drop)

```javascript
// Example: RSI Oversold + Volume Spike
{
  "entry": [
    {
      "indicator": "rsi",
      "comparison": "lt",
      "value": 30,
      "period": 14
    },
    {
      "indicator": "volume",
      "comparison": "gt",
      "value": 150,  // % of average
      "period": 20
    }
  ]
}
```

### Exit Conditions

```javascript
{
  "exit": [
    {
      "indicator": "rsi",
      "comparison": "gt",
      "value": 70
    },
    {
      "type": "trailing_stop",
      "value": 2.0,  // %
      "activation": 1.5  // % profit to activate
    }
  ]
}
```

### Available Indicators (50+)

**Trend:**
- EMA (Exponential Moving Average)
- SMA (Simple Moving Average)
- MACD (Moving Average Convergence Divergence)
- ADX (Average Directional Index)
- SuperTrend
- Parabolic SAR
- Ichimoku Cloud

**Momentum:**
- RSI (Relative Strength Index)
- Stochastic
- CCI (Commodity Channel Index)
- Williams %R
- ROC (Rate of Change)
- MFI (Money Flow Index)

**Volatility:**
- Bollinger Bands
- ATR (Average True Range)
- Keltner Channels
- Donchian Channels

**Volume:**
- Volume Profile
- OBV (On Balance Volume)
- VWAP (Volume Weighted Average Price)
- Volume Spike Detection

**Custom:**
- Price Action Patterns
- Support/Resistance Levels
- Fibonacci Retracements
- Multi-timeframe Confluence

---

## 🚀 Quick Start

### 1. Simple Backtest

```javascript
// Frontend JavaScript
async function runSimpleBacktest() {
    const response = await fetch('/api/backtest/run', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            symbol: "BTCUSDT",
            strategy: "elcaro",
            timeframe: "1h",
            days: 30,
            initial_balance: 10000,
            risk_per_trade: 1.0,
            stop_loss: 2.0,
            take_profit: 4.0
        })
    });
    
    const result = await response.json();
    console.log(result);
    // {
    //   "total_pnl": 1250.50,
    //   "win_rate": 65.5,
    //   "total_trades": 42,
    //   "sharpe_ratio": 1.85,
    //   "max_drawdown": -8.5,
    //   "profit_factor": 2.15
    // }
}
```

### 2. Monte Carlo Simulation

```javascript
async function runMonteCarlo() {
    const response = await fetch('/api/backtest/monte-carlo', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            trades: backtest_trades,  // Array of trade results
            simulations: 1000,
            confidence_level: 95
        })
    });
    
    const result = await response.json();
    // {
    //   "expected_return": 12.5,
    //   "worst_case": -5.2,
    //   "best_case": 28.4,
    //   "probability_profit": 87.5,
    //   "var_95": -4.8
    // }
}
```

### 3. Parameter Optimization

```javascript
async function optimizeStrategy() {
    const response = await fetch('/api/backtest/optimize', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            symbol: "ETHUSDT",
            strategy: "rsibboi",
            parameter_grid: {
                rsi_period: [10, 14, 20],
                rsi_oversold: [25, 30, 35],
                rsi_overbought: [65, 70, 75],
                bb_period: [15, 20, 25],
                bb_std: [1.5, 2.0, 2.5]
            },
            metric: "sharpe_ratio"  // or "win_rate", "profit_factor"
        })
    });
    
    const result = await response.json();
    // {
    //   "best_params": {
    //     "rsi_period": 14,
    //     "rsi_oversold": 30,
    //     "rsi_overbought": 70,
    //     "bb_period": 20,
    //     "bb_std": 2.0
    //   },
    //   "best_score": 2.15,
    //   "all_results": [...]
    // }
}
```

---

## 📊 Performance Metrics

### Backtest Result Structure

```python
{
    # Основные метрики
    "total_pnl": 1250.50,           # Общий P&L в USD
    "total_pnl_pct": 12.5,          # P&L в %
    "win_rate": 65.5,               # % выигрышных сделок
    "total_trades": 42,             # Всего сделок
    "winning_trades": 28,           # Выигрышных
    "losing_trades": 14,            # Проигрышных
    
    # Риск-метрики
    "sharpe_ratio": 1.85,           # Sharpe Ratio
    "sortino_ratio": 2.42,          # Sortino Ratio
    "max_drawdown": -8.5,           # Максимальная просадка %
    "max_drawdown_duration": 5,     # Дней в просадке
    "calmar_ratio": 1.47,           # Calmar Ratio
    
    # Прибыльность
    "profit_factor": 2.15,          # Profit Factor
    "avg_win": 52.30,               # Средний выигрыш USD
    "avg_loss": -24.50,             # Средний проигрыш USD
    "avg_win_pct": 5.2,             # Средний выигрыш %
    "avg_loss_pct": -2.4,           # Средний проигрыш %
    "largest_win": 145.80,          # Самый большой выигрыш
    "largest_loss": -48.20,         # Самый большой проигрыш
    
    # Временные метрики
    "avg_trade_duration": 4.2,      # Средняя длительность (часы)
    "avg_bars_in_trade": 3.5,       # Средняя длительность (бары)
    
    # Последовательности
    "max_consecutive_wins": 7,      # Макс серия побед
    "max_consecutive_losses": 3,    # Макс серия потерь
    
    # Equity curve
    "equity_curve": [10000, 10150, 10280, ...],
    
    # Trade history
    "trades": [
        {
            "entry_time": "2024-01-15 10:30:00",
            "exit_time": "2024-01-15 14:30:00",
            "side": "LONG",
            "entry_price": 42150.50,
            "exit_price": 42580.20,
            "size": 0.5,
            "pnl": 214.85,
            "pnl_pct": 1.02,
            "exit_reason": "take_profit"
        },
        ...
    ]
}
```

---

## 🎲 Monte Carlo Analysis

### What is Monte Carlo?

Симуляция 1000+ случайных порядков сделок для оценки стабильности стратегии:

```python
# Пример: 
Original trades: [+5%, -2%, +3%, +7%, -1%, +4%]

# Monte Carlo создает 1000 случайных перестановок:
Sim 1: [+3%, +7%, -2%, +5%, +4%, -1%]  → Result: +16%
Sim 2: [-2%, -1%, +3%, +5%, +7%, +4%]  → Result: +16%
Sim 3: [+7%, +5%, +3%, -2%, +4%, -1%]  → Result: +16%
...
Sim 1000: [-1%, +4%, -2%, +5%, +3%, +7%] → Result: +16%

# Анализ всех 1000 симуляций:
- Best case: +28.4%
- Worst case: -5.2%
- Average: +12.5%
- Probability of profit: 87.5%
- 95% VaR: -4.8%
```

### Monte Carlo Metrics

```python
{
    "simulations": 1000,
    "confidence_level": 95,
    
    "expected_return": 12.5,        # Средний результат
    "median_return": 12.2,          # Медиана
    "std_deviation": 8.5,           # Стандартное отклонение
    
    "best_case": 28.4,              # Лучший сценарий
    "worst_case": -5.2,             # Худший сценарий
    
    "probability_profit": 87.5,     # Вероятность прибыли
    "probability_loss": 12.5,       # Вероятность убытка
    
    "var_95": -4.8,                 # Value at Risk (95%)
    "cvar_95": -3.2,                # Conditional VaR
    
    "percentiles": {
        "5": -4.8,
        "25": 6.2,
        "50": 12.2,
        "75": 18.5,
        "95": 24.8
    }
}
```

---

## 🔧 Walk-Forward Optimization

### What is Walk-Forward?

Защита от overfitting через разделение данных на Train/Test периоды:

```
Timeline: [=============== 365 days ===============]

Window 1:
├─ Train: [===== 30 days =====]
└─ Test:                       [= 7 days =]

Window 2:
    ├─ Train:     [===== 30 days =====]
    └─ Test:                           [= 7 days =]

Window 3:
        ├─ Train:         [===== 30 days =====]
        └─ Test:                               [= 7 days =]

... (rolling windows)
```

### Walk-Forward Process

```javascript
{
    "train_period": 30,     // Дней для обучения
    "test_period": 7,       // Дней для теста
    "step": 7,              // Шаг сдвига окна
    
    "results": [
        {
            "period": 1,
            "train_sharpe": 2.15,
            "test_sharpe": 1.85,    // Должен быть близок к train
            "overfitting_score": 0.86  // < 0.7 = плохо
        },
        ...
    ],
    
    "summary": {
        "avg_train_sharpe": 2.10,
        "avg_test_sharpe": 1.75,
        "consistency_score": 0.83,  // > 0.80 = хорошо
        "is_overfit": false
    }
}
```

---

## 🎬 Strategy Replay Mode

### Real-time Visualization

```javascript
// Режим replay воспроизводит сделки по таймлайну
// с контролем скорости (0.5x, 1x, 2x, 5x)

const replay = {
    candles: historical_data,
    trades: backtest_trades,
    speed: 1.0,
    
    async play() {
        for (let i = 0; i < this.candles.length; i++) {
            // Update chart
            updateChart(this.candles[i]);
            
            // Check for trades
            const trade = this.trades.find(t => t.index === i);
            if (trade) {
                showTradeMarker(trade);
                animateTradeExecution(trade);
            }
            
            // Wait based on speed
            await sleep(1000 / this.speed);
        }
    }
};
```

---

## 🔴 Live Mode

### Real-time Strategy Execution

```javascript
// Live mode подключается к реальным рыночным данным
// и симулирует сделки в реальном времени

const liveMode = {
    ws: null,
    strategy: selected_strategy,
    paper_balance: 10000,
    
    async start() {
        // Connect to market WebSocket
        this.ws = new WebSocket('/ws/market/BTCUSDT');
        
        this.ws.onmessage = (event) => {
            const candle = JSON.parse(event.data);
            
            // Run strategy on new candle
            const signal = this.strategy.evaluate(candle);
            
            if (signal === 'BUY') {
                this.executePaperTrade('LONG', candle.close);
            } else if (signal === 'SELL') {
                this.closePaperPosition(candle.close);
            }
            
            // Update UI
            this.updateLiveChart(candle);
            this.updatePaperBalance();
        };
    }
};
```

---

## 📦 Strategy Import/Export

### Export Strategy

```javascript
async function exportStrategy() {
    const strategy = {
        name: "My RSI Strategy",
        description: "RSI oversold/overbought with volume confirmation",
        version: "1.0.0",
        author: "User123",
        
        parameters: {
            rsi_period: 14,
            rsi_oversold: 30,
            rsi_overbought: 70,
            volume_threshold: 150
        },
        
        entry_conditions: [
            {indicator: "rsi", comparison: "lt", value: 30},
            {indicator: "volume", comparison: "gt", value: 150}
        ],
        
        exit_conditions: [
            {indicator: "rsi", comparison: "gt", value: 70}
        ],
        
        risk_management: {
            stop_loss: 2.0,
            take_profit: 4.0,
            risk_per_trade: 1.0,
            max_positions: 3
        },
        
        backtest_results: {
            sharpe_ratio: 1.85,
            win_rate: 65.5,
            total_trades: 42
        }
    };
    
    // Save to file
    const blob = new Blob([JSON.stringify(strategy, null, 2)], 
                          {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'my_strategy.json';
    a.click();
}
```

### Import Strategy

```javascript
async function importStrategy(file) {
    const text = await file.text();
    const strategy = JSON.parse(text);
    
    // Validate strategy
    if (!validateStrategy(strategy)) {
        throw new Error('Invalid strategy format');
    }
    
    // Load into builder
    loadStrategyIntoBuilder(strategy);
    
    // Run backtest
    const results = await testStrategy(strategy);
    
    return {strategy, results};
}
```

---

## 🎓 Advanced Features

### 1. Correlation Matrix

```javascript
// Тест нескольких стратегий одновременно
// и анализ их корреляции

{
    "strategies": ["elcaro", "rsibboi", "trend_following"],
    "correlation_matrix": [
        [1.00, 0.45, 0.62],  // elcaro
        [0.45, 1.00, 0.38],  // rsibboi
        [0.62, 0.38, 1.00]   // trend_following
    ],
    
    // Низкая корреляция = хорошая диверсификация
    "diversification_score": 0.72
}
```

### 2. Multi-Symbol Backtesting

```javascript
{
    "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
    "strategy": "elcaro",
    "results": {
        "BTCUSDT": {sharpe: 1.85, win_rate: 65.5},
        "ETHUSDT": {sharpe: 2.10, win_rate: 68.2},
        "SOLUSDT": {sharpe: 1.65, win_rate: 62.8}
    },
    "portfolio_sharpe": 2.25  // Diversified
}
```

### 3. Timeframe Analysis

```javascript
{
    "strategy": "trend_following",
    "timeframes": ["1m", "5m", "15m", "1h", "4h"],
    "results": {
        "1m": {sharpe: 1.20, trades: 520},
        "5m": {sharpe: 1.55, trades: 180},
        "15m": {sharpe: 1.85, trades: 85},   // Best
        "1h": {sharpe: 1.65, trades: 42},
        "4h": {sharpe: 1.40, trades: 18}
    }
}
```

---

## 🔌 WebSocket Integration

### Real-time Backtest Updates

```javascript
// Client-side
const ws = new WebSocket('/ws/backtest/12345');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch (data.type) {
        case 'progress':
            updateProgressBar(data.progress);
            break;
            
        case 'trade':
            addTradeToTable(data.trade);
            updateEquityCurve(data.equity);
            break;
            
        case 'complete':
            showResults(data.results);
            break;
            
        case 'error':
            showError(data.error);
            break;
    }
};

// Start backtest
ws.send(JSON.stringify({
    action: 'start_backtest',
    strategy_id: 'elcaro',
    symbol: 'BTCUSDT',
    timeframe: '1h'
}));
```

---

## 📝 Best Practices

### 1. Data Quality
- Используйте достаточно данных (минимум 30 дней)
- Проверяйте качество исторических данных
- Учитывайте проскальзывание (slippage) и комиссии

### 2. Overfitting Prevention
- Всегда используйте Walk-Forward Analysis
- Тестируйте на out-of-sample данных
- Не оптимизируйте под конкретный период

### 3. Risk Management
- Risk per trade ≤ 1-2% от депозита
- Max drawdown ≤ 20%
- Stop loss обязателен

### 4. Strategy Validation
- Win rate > 50% для long-only
- Sharpe Ratio > 1.0
- Profit Factor > 1.5
- Max consecutive losses < 5

### 5. Monte Carlo Analysis
- Всегда проверяйте стабильность через MC
- Probability of profit > 70%
- 95% VaR должен быть приемлем

---

## 🚨 Common Pitfalls

### ❌ Избегайте:

1. **Curve Fitting** - оптимизация под историю
2. **Look-Ahead Bias** - использование будущих данных
3. **Survivorship Bias** - тестирование только на "живых" монетах
4. **Small Sample Size** - < 30 сделок недостаточно
5. **Ignoring Costs** - комиссии и проскальзывание
6. **Over-Optimization** - слишком много параметров
7. **Single Timeframe** - тест только на одном TF
8. **No Walk-Forward** - нет проверки на overfitting

---

## 🎯 Success Metrics

### Минимальные требования:

```python
{
    "sharpe_ratio": > 1.0,
    "win_rate": > 50%,
    "profit_factor": > 1.5,
    "total_trades": > 30,
    "max_drawdown": < 20%,
    "monte_carlo_profit_prob": > 70%,
    "walk_forward_consistency": > 0.8
}
```

### Excellent Strategy:

```python
{
    "sharpe_ratio": > 2.0,
    "win_rate": > 60%,
    "profit_factor": > 2.0,
    "max_drawdown": < 15%,
    "monte_carlo_profit_prob": > 85%,
    "walk_forward_consistency": > 0.85
}
```

---

## 🔗 API Documentation

### Complete API Reference

```bash
# Swagger UI
https://YOUR-DOMAIN/api/docs

# ReDoc
https://YOUR-DOMAIN/api/redoc

# OpenAPI JSON
https://YOUR-DOMAIN/api/openapi.json
```

### Quick API Test

```bash
# Run simple backtest
curl -X POST https://YOUR-DOMAIN/api/backtest/run \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "strategy": "elcaro",
    "timeframe": "1h",
    "days": 30,
    "initial_balance": 10000
  }'
```

---

## 🎨 UI Components

### Style Guide

```css
/* ElCaro Design System для Backtest */
:root {
    --accent-purple: #8b5cf6;
    --accent-green: #22c55e;
    --accent-red: #ef4444;
    --gradient-purple: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
    --gradient-green: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

/* Buttons */
.btn-primary {
    background: var(--gradient-purple);
    box-shadow: 0 4px 20px rgba(139, 92, 246, 0.3);
}

/* Strategy Cards */
.strategy-card.selected {
    border-color: var(--accent-purple);
    background: rgba(139, 92, 246, 0.1);
}

/* Result Stats */
.stat-card.positive {
    color: var(--accent-green);
    background: var(--green-dim);
}
```

---

## 📚 Related Modules

1. **[Terminal](/terminal)** - Real trading interface
2. **[Screener](/screener)** - Market scanner
3. **[Strategies](/strategies)** - Strategy library
4. **[Marketplace](/marketplace)** - Strategy marketplace
5. **[Dashboard](/dashboard)** - Portfolio overview

---

## 🎓 Learning Resources

### Tutorials:
1. [Backtest Quickstart](BACKTEST_QUICKSTART.md)
2. [Strategy Builder Guide](STRATEGY_BUILDER.md)
3. [Advanced Analytics](BACKTEST_ENHANCED_README.md)

### Examples:
- `webapp/static/js/backtest.js` - Main frontend logic
- `webapp/services/backtest_engine_v2.py` - Backend engine
- `webapp/services/strategy_builder.py` - Visual builder

---

## 🎉 Summary

ElCaro Backtest Module - это **полноценная платформа** для:
- ✅ Визуального создания стратегий
- ✅ Тестирования на исторических данных
- ✅ Оптимизации параметров
- ✅ Анализа рисков через Monte Carlo
- ✅ Защиты от overfitting через Walk-Forward
- ✅ Реалтайм симуляции в Live Mode
- ✅ Экспорта/импорта стратегий

**Status:** ✅ Fully Operational  
**URL:** `https://dean-italic-maternity-instead.trycloudflare.com/backtest`  
**Documentation:** `/api/docs`  

---

*Last updated: December 24, 2025*  
*ElCaro Trading Platform v2.1.0*
