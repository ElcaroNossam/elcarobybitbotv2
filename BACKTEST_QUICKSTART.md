# 🚀 Бэктест - Быстрый Старт

## 📋 Основные Endpoints

```
Base URL: /api/backtest-v2
```

### 1. Получить Список Стратегий
```bash
GET /api/backtest-v2/strategies/templates
```

### 2. Получить Стратегию с Параметрами
```bash
GET /api/backtest-v2/strategies/template/rsibboi
```

### 3. Запустить Кастомный Бэктест
```bash
POST /api/backtest-v2/backtest/custom
Content-Type: application/json

{
  "base_strategy": "rsibboi",
  "custom_params": {
    "indicators": {
      "rsi": {"params": {"period": 21}}
    }
  },
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "days": 30
}
```

### 4. Генерация Стратегии с AI
```bash
POST /api/backtest-v2/strategies/ai/generate

{
  "description": "Создай скальпинг стратегию с RSI и BB"
}
```

### 5. Сравнение Стратегий
```bash
POST /api/backtest-v2/backtest/compare

{
  "strategies": [
    {"name": "RSI 14", ...},
    {"name": "RSI 21", ...}
  ],
  "symbol": "BTCUSDT",
  "days": 30
}
```

---

## 💡 Быстрые Примеры

### JavaScript: Изменить RSI период

```javascript
// 1. Получить шаблон
const template = await fetch('/api/backtest-v2/strategies/template/rsibboi')
  .then(r => r.json());

// 2. Изменить параметр
template.strategy.indicators.rsi.params.period = 21;

// 3. Запустить
const result = await fetch('/api/backtest-v2/backtest/custom', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    base_strategy: 'rsibboi',
    custom_params: template.strategy,
    symbol: 'BTCUSDT',
    timeframe: '1h',
    days: 30
  })
}).then(r => r.json());

console.log(result.results);
```

### Python: Создать и протестировать стратегию

```python
from webapp.services.strategy_parameters import StrategyParametersManager
from webapp.services.backtest_engine import RealBacktestEngine

# 1. Создать кастомную стратегию
manager = StrategyParametersManager()
custom = manager.create_custom_strategy("rsibboi", {
    "indicators": {
        "rsi": {"period": 21, "oversold": 25},
        "bb": {"std_dev": 2.5}
    },
    "risk_per_trade": 2.0
})

# 2. Запустить бэктест
engine = RealBacktestEngine()
result = await engine.run_backtest_with_config(
    strategy_config=custom,
    symbol="BTCUSDT",
    timeframe="1h",
    days=30,
    initial_balance=10000
)

print(f"Win Rate: {result['win_rate']}%")
print(f"Total PnL: ${result['total_pnl']}")
```

---

## 🎯 Доступные Стратегии

| Стратегия | Описание | Индикаторы |
|-----------|----------|------------|
| `rsibboi` | RSI + BB + Volume | RSI, BB, Volume |
| `wyckoff` | Wyckoff + Fibonacci | Fib, Volume, S/R |
| `elcaro` | ElCaro Main | RSI, EMA, Volume |
| `scalper` | Fast Scalping | RSI(7), BB(10), EMA |
| `mean_reversion` | Range Trading | BB, RSI, S/R |
| `trend_following` | Trend + Momentum | EMA, MACD, ADX |

---

## ⚙️ Настройки Индикаторов

### RSI
```json
{
  "period": 14,        // 2-50
  "overbought": 70,    // 50-100
  "oversold": 30       // 0-50
}
```

### Bollinger Bands
```json
{
  "period": 20,        // 5-100
  "std_dev": 2.0       // 1.0-4.0
}
```

### MACD
```json
{
  "fast_period": 12,   // 5-30
  "slow_period": 26,   // 10-50
  "signal_period": 9   // 5-20
}
```

---

## 🎨 UI Пример

```html
<div class="strategy-editor">
  <h3>Edit Strategy: RSIBBOI</h3>
  
  <!-- RSI Period -->
  <div>
    <label>RSI Period: <span id="rsi-period">14</span></label>
    <input type="range" id="rsi-period-slider" 
           min="2" max="50" value="14"
           oninput="updateRSI(this.value)">
  </div>
  
  <!-- Run Button -->
  <button onclick="runBacktest()">Run Backtest</button>
  
  <!-- Results -->
  <div id="results"></div>
</div>

<script>
let params = {
  base_strategy: 'rsibboi',
  custom_params: {
    indicators: {
      rsi: {params: {period: 14, oversold: 30, overbought: 70}}
    }
  }
};

function updateRSI(value) {
  params.custom_params.indicators.rsi.params.period = parseInt(value);
  document.getElementById('rsi-period').textContent = value;
}

async function runBacktest() {
  const result = await fetch('/api/backtest-v2/backtest/custom', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      ...params,
      symbol: 'BTCUSDT',
      timeframe: '1h',
      days: 30
    })
  }).then(r => r.json());
  
  document.getElementById('results').innerHTML = `
    <h4>Results</h4>
    <p>Win Rate: ${result.results.win_rate}%</p>
    <p>Total PnL: $${result.results.total_pnl}</p>
    <p>Sharpe Ratio: ${result.results.sharpe_ratio}</p>
  `;
}
</script>
```

---

## 📚 Полная Документация

- **Детальный гайд:** `BACKTEST_ENHANCED_README.md`
- **Swagger UI:** `/api/docs`
