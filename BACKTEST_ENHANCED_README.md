# 🚀 Улучшенный Модуль Бэктеста с AI и Настраиваемыми Параметрами

## 📋 Содержание
1. [Обзор](#обзор)
2. [Новые Возможности](#новые-возможности)
3. [Структура Проекта](#структура-проекта)
4. [API Endpoints](#api-endpoints)
5. [Примеры Использования](#примеры-использования)
6. [AI Функционал](#ai-функционал)
7. [Редактирование Параметров](#редактирование-параметров)

---

## 🎯 Обзор

Улучшенный модуль бэктеста позволяет:
- ✅ Редактировать **любые параметры** существующих стратегий (RSI, BB, MACD и т.д.)
- ✅ **Создавать кастомные стратегии** на основе шаблонов
- ✅ **Генерировать стратегии с помощью AI** из текстового описания
- ✅ **Оптимизировать параметры** на основе исторических данных
- ✅ **Сравнивать стратегии** side-by-side
- ✅ **Добавлять/удалять индикаторы** динамически
- ✅ Работать быстро - бэктест выполняется в браузере (client-side)

---

## 🆕 Новые Возможности

### 1. **Редактируемые Параметры Стратегий**

Каждая стратегия имеет полностью настраиваемые параметры:

```python
# Например, для RSIBBOI:
{
  "indicators": {
    "rsi": {
      "period": 14,        # Можно изменить на 7, 21, 50
      "overbought": 70,    # Можно изменить на 65, 75, 80
      "oversold": 30       # Можно изменить на 25, 35, 20
    },
    "bb": {
      "period": 20,        # Можно изменить на 10, 30, 50
      "std_dev": 2.0       # Можно изменить на 1.5, 2.5, 3.0
    }
  },
  "risk_per_trade": 1.0,   # % от депозита
  "stop_loss_percent": 2.0,
  "take_profit_percent": 4.0
}
```

### 2. **AI-Генерация Стратегий**

Создание стратегии из текстового описания:

```
"Создай агрессивную скальпинговую стратегию для 5-минутных графиков.
Используй RSI ниже 20 для входа и тейк-профит на 1%.
Добавь Bollinger Bands для подтверждения."
```

AI создаст полную конфигурацию с оптимальными параметрами!

### 3. **Оптимизация Параметров**

AI анализирует историческ��е результаты и предлагает оптимальные настройки:
- Лучший период для RSI
- Оптимальные std_dev для BB
- Идеальное соотношение TP/SL

---

## 📁 Структура Проекта

```
webapp/
├── api/
│   ├── backtest.py              # Старый API (базовый)
│   └── backtest_enhanced.py     # ⭐ Новый API с расширенными возможностями
├── services/
│   ├── backtest_engine.py       # Движок бэктеста
│   ├── strategy_parameters.py   # ⭐ Система параметров стратегий
│   └── ai_strategy_generator.py # ⭐ AI генератор и оптимизатор
└── templates/
    └── backtest.html            # UI бэктеста
```

---

## 🔌 API Endpoints

### 1. Получить Шаблоны Стратегий

```http
GET /api/backtest/strategies/templates
```

**Ответ:**
```json
{
  "success": true,
  "templates": {
    "rsibboi": {...},
    "wyckoff": {...},
    "elcaro": {...},
    "scalper": {...}
  }
}
```

### 2. Получить Конкретную Стратегию с Редактируемыми Параметрами

```http
GET /api/backtest/strategies/template/rsibboi
```

**Ответ:**
```json
{
  "success": true,
  "strategy": {
    "name": "RSI BB OI",
    "base_strategy": "rsibboi",
    "indicators": {...}
  },
  "editable_params": {
    "indicators": {
      "rsi": {
        "type": "rsi",
        "enabled": true,
        "weight": 1.0,
        "params": {
          "period": 14,
          "overbought": 70,
          "oversold": 30
        },
        "param_descriptions": {
          "period": "Number of periods for RSI calculation (typical: 14)",
          "overbought": "Level above which asset is considered overbought",
          "oversold": "Level below which asset is considered oversold"
        }
      }
    }
  }
}
```

### 3. Запустить Кастомный Бэктест

```http
POST /api/backtest/custom
Content-Type: application/json

{
  "base_strategy": "rsibboi",
  "custom_params": {
    "name": "My Custom RSI BB",
    "indicators": {
      "rsi": {
        "period": 21,
        "oversold": 25,
        "overbought": 75
      },
      "bb": {
        "period": 30,
        "std_dev": 2.5
      }
    },
    "risk_per_trade": 2.0,
    "stop_loss_percent": 1.5,
    "take_profit_percent": 3.0
  },
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "days": 30,
  "initial_balance": 10000
}
```

### 4. Генерация Стратегии с AI

```http
POST /api/backtest/strategies/ai/generate
Content-Type: application/json

{
  "description": "Create a scalping strategy using RSI and BB for 5m timeframe with aggressive TP",
  "market_conditions": "High volatility, trending market",
  "optimize_for": "win_rate"
}
```

### 5. Оптимизация Параметров с AI

```http
POST /api/backtest/strategies/ai/optimize
Content-Type: application/json

{
  "base_strategy": "rsibboi",
  "historical_results": [
    {
      "parameters": {...},
      "win_rate": 65,
      "total_pnl": 1500,
      "sharpe_ratio": 1.8
    }
  ]
}
```

### 6. Сравнение Стратегий

```http
POST /api/backtest/compare
Content-Type: application/json

{
  "strategies": [
    {"name": "RSI 14", "base_strategy": "rsibboi", ...},
    {"name": "RSI 21", "base_strategy": "rsibboi", ...}
  ],
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "days": 30
}
```

### 7. Доступные Индикаторы

```http
GET /api/backtest/indicators/available
```

---

## 💡 Примеры Использования

### Пример 1: Изменить RSI период с 14 на 21

```javascript
// Получить шаблон
const template = await fetch('/api/backtest/strategies/template/rsibboi').then(r => r.json());

// Изменить параметры
const customParams = {
  ...template.strategy,
  indicators: {
    ...template.strategy.indicators,
    rsi: {
      ...template.strategy.indicators.rsi,
      params: {
        ...template.strategy.indicators.rsi.params,
        period: 21  // ✅ Изменили!
      }
    }
  }
};

// Запустить бэктест
const result = await fetch('/api/backtest/custom', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    base_strategy: 'rsibboi',
    custom_params: customParams,
    symbol: 'BTCUSDT',
    timeframe: '1h',
    days: 30
  })
}).then(r => r.json());

console.log('Win Rate:', result.results.win_rate);
console.log('Total PnL:', result.results.total_pnl);
```

### Пример 2: Добавить новый индикатор (MACD)

```javascript
const customParams = {
  base_strategy: "rsibboi",
  custom_params: {
    indicators: {
      rsi: { /* existing params */ },
      bb: { /* existing params */ },
      macd: {  // ✅ Новый индикатор!
        type: "macd",
        enabled: true,
        weight: 1.0,
        params: {
          fast_period: 12,
          slow_period: 26,
          signal_period: 9
        }
      }
    }
  }
};
```

### Пример 3: A/B тестирование параметров

```javascript
const results = await fetch('/api/backtest/compare', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    strategies: [
      {
        name: "Conservative RSI",
        base_strategy: "rsibboi",
        indicators: {
          rsi: {params: {period: 14, oversold: 20, overbought: 80}}
        }
      },
      {
        name: "Aggressive RSI",
        base_strategy: "rsibboi",
        indicators: {
          rsi: {params: {period: 7, oversold: 25, overbought: 75}}
        }
      }
    ],
    symbol: "BTCUSDT",
    timeframe: "1h",
    days: 30
  })
}).then(r => r.json());

console.log('Winner:', results.winner);
console.log('Comparison:', results.comparison);
```

---

## 🤖 AI Функционал

### 1. Генерация Стратегии из Текста

```javascript
const strategy = await fetch('/api/backtest/strategies/ai/generate', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    description: `
      Создай стратегию для скальпинга на 5-минутках.
      - Использовать RSI < 25 для лонгов
      - BB с периодом 10 для волатильности
      - Тейк-профит 0.5%, стоп-лосс 0.3%
      - Подтверждение объемом (spike > 2x)
    `
  })
}).then(r => r.json());

// AI создаст полную конфигурацию
console.log(strategy.strategy);
```

### 2. Оптимизация Существующей Стратегии

```javascript
// Собрать историю бэктестов
const historical_results = [
  {parameters: {rsi: 14, bb: 20}, win_rate: 60, sharpe: 1.5},
  {parameters: {rsi: 21, bb: 20}, win_rate: 65, sharpe: 1.8},
  {parameters: {rsi: 14, bb: 30}, win_rate: 55, sharpe: 1.2}
];

// AI предложит оптимальные параметры
const optimized = await fetch('/api/backtest/strategies/ai/optimize', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    base_strategy: "rsibboi",
    historical_results: historical_results
  })
}).then(r => r.json());

console.log('Optimized RSI period:', optimized.optimized_strategy.indicators.rsi.params.period);
```

---

## ⚙️ Редактирование Параметров

### Доступные Индикаторы

| Индикатор | Параметры | Описание |
|-----------|-----------|----------|
| **RSI** | `period` (2-50)<br>`overbought` (50-100)<br>`oversold` (0-50) | Relative Strength Index |
| **BB** | `period` (5-100)<br>`std_dev` (1.0-4.0) | Bollinger Bands |
| **MACD** | `fast_period` (5-30)<br>`slow_period` (10-50)<br>`signal_period` (5-20) | Moving Average Convergence Divergence |
| **EMA** | `periods` (array) | Exponential Moving Averages |
| **Volume** | `ma_period` (5-50)<br>`spike_threshold` (1.0-5.0) | Volume Analysis |
| **ATR** | `period` (5-30) | Average True Range |
| **Fibonacci** | `levels` (array) | Fibonacci Retracement |

### Логика Входа/Выхода

```javascript
{
  "entry_logic": "AND" | "OR" | "WEIGHTED",
  "exit_logic": "TP_SL" | "SIGNAL" | "TRAILING"
}
```

- **AND**: Все индикаторы должны подтвердить
- **OR**: Хотя бы один индикатор
- **WEIGHTED**: Взвешенная сумма сигналов

---

## 🎨 UI Интеграция

### Слайдеры для Параметров

```html
<div class="param-control">
  <label>RSI Period: <span id="rsi-period-value">14</span></label>
  <input type="range" id="rsi-period" 
         min="2" max="50" value="14" step="1"
         oninput="document.getElementById('rsi-period-value').textContent = this.value">
</div>

<div class="param-control">
  <label>RSI Oversold: <span id="rsi-oversold-value">30</span></label>
  <input type="range" id="rsi-oversold" 
         min="0" max="50" value="30" step="1"
         oninput="document.getElementById('rsi-oversold-value').textContent = this.value">
</div>

<button onclick="runCustomBacktest()">Run Backtest</button>

<script>
async function runCustomBacktest() {
  const params = {
    base_strategy: 'rsibboi',
    custom_params: {
      indicators: {
        rsi: {
          params: {
            period: parseInt(document.getElementById('rsi-period').value),
            oversold: parseInt(document.getElementById('rsi-oversold').value),
            overbought: 70
          }
        }
      }
    },
    symbol: 'BTCUSDT',
    timeframe: '1h',
    days: 30
  };
  
  const result = await fetch('/api/backtest/custom', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(params)
  }).then(r => r.json());
  
  displayResults(result);
}
</script>
```

---

## 📊 Производительность

### Client-Side Бэктест

Бэктест выполняется **в браузере пользователя**, не нагружая сервер:

1. **Сервер** отдает исторические данные (candles) один раз
2. **Браузер** выполняет симуляцию локально
3. Можно запускать **100+ бэктестов параллельно**
4. Мгновенное обновление при изменении параметров

```javascript
// Загрузить данные один раз
const candles = await fetch(`/api/data/candles?symbol=BTCUSDT&days=30`).then(r => r.json());

// Запустить множество бэктестов локально
for (let period = 7; period <= 21; period++) {
  const result = runBacktestLocally(candles, {rsi: {period}});
  console.log(`RSI ${period}: Win Rate ${result.win_rate}%`);
}
```

---

## 🔥 Ключевые Преимущества

1. ✅ **Полная Гибкость** - крути любые параметры
2. ✅ **AI Помощник** - генерация и оптимизация стратегий
3. ✅ **Быстрота** - бэктест в браузере
4. ✅ **Визуализация** - сравнение результатов
5. ✅ **Расширяемость** - легко добавить новые индикаторы
6. ✅ **API-first** - всё через REST API

---

## 📝 TODO (Будущие Улучшения)

- [ ] Walk-Forward оптимизация
- [ ] Monte Carlo симуляции
- [ ] Multi-symbol portfolio backtest
- [ ] ML предсказание параметров
- [ ] Автоматическое re-balancing
- [ ] Экспорт/импорт стратегий

---

**Создано:** December 23, 2025  
**Версия:** 2.0.0  
**Статус:** ✅ Production Ready  
**AI Integration:** GPT-4o-mini  
