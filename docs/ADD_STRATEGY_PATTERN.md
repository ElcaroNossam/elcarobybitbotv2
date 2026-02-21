# 🎯 ПАТТЕРН ДОБАВЛЕНИЯ НОВОЙ СТРАТЕГИИ

## Быстрый чек-лист (5 шагов)

При добавлении новой стратегии (например, `wyckoff`) нужно:

1. **Парсер сигналов** → bot.py
2. **STRATEGY_FEATURES** → bot.py
3. **UI клавиатура** → bot.py
4. **Trigger + direction check** → bot.py (on_channel_post)
5. **Настройки по умолчанию** → db.py

---

## Шаг 1: Парсер сигналов (bot.py ~line 19700)

```python
# Regex для детекции сигнала
WYCKOFF_RE_MAIN = re.compile(r'📊\s*WYCKOFF\s*(LONG|SHORT)\s*([A-Z0-9]+USDT)', re.I)
WYCKOFF_RE_ENTRY = re.compile(r'Entry\s*[:：]\s*' + NUM, re.I)

def is_wyckoff_signal(text: str) -> bool:
    """Check if message is Wyckoff signal."""
    return bool(WYCKOFF_RE_MAIN.search(text))

def parse_wyckoff_signal(text: str) -> dict | None:
    """Parse Wyckoff signal format.
    
    Format:
        📊 WYCKOFF LONG BTCUSDT
        Entry: 95000.00
        SL: 94000.00 (1.05%)
        TP: 97000.00 (2.10%)
    """
    if not is_wyckoff_signal(text):
        return None
    
    m = WYCKOFF_RE_MAIN.search(text)
    if not m:
        return None
    
    side = "Buy" if m.group(1).upper() == "LONG" else "Sell"
    symbol = m.group(2).upper()
    
    entry_m = WYCKOFF_RE_ENTRY.search(text)
    price = _tof(entry_m.group(1)) if entry_m else None
    
    return {
        "symbol": symbol,
        "side": side,
        "price": price,
    }
```

---

## Шаг 2: STRATEGY_FEATURES (bot.py ~line 9465)

```python
STRATEGY_FEATURES = {
    # ... existing strategies ...
    "wyckoff": {
        "order_type": False,     # Order type is per-side
        "coins_group": False,    # Uses exchange-level filter
        "leverage": True,
        "use_atr": True,
        "direction": True,       # LONG/SHORT/ALL filter
        "side_settings": True,   # Separate LONG/SHORT settings
        "percent": True,         # Entry %
        "sl_tp": True,           # SL/TP %
        "atr_params": True,
        "min_quality": False,    # Has quality filter? (optional)
    },
}
```

---

## Шаг 3: UI клавиатура (bot.py ~line 9600)

В функции `get_strategy_settings_keyboard()` найти список `strategies`:

```python
strategies = [
    ("trade_scryptomera", "Scryptomera"),
    ("trade_scalper", "Scalper"),
    ("trade_elcaro", "Enliko"),
    ("trade_fibonacci", "Fibonacci"),
    ("trade_oi", "OI Strategy"),
    ("trade_rsi_bb", "RSI BB"),
    ("trade_wyckoff", "Wyckoff"),  # <-- ДОБАВИТЬ
]
```

---

## Шаг 4: Trigger + direction check (bot.py on_channel_post ~line 20400)

### 4.1 Добавить парсинг:

```python
# В начале on_channel_post, после остальных парсеров:
parsed_wyckoff = parse_wyckoff_signal(txt)
is_wyckoff = parsed_wyckoff is not None
```

### 4.2 Добавить override parsed data:

```python
elif is_wyckoff and parsed_wyckoff:
    parsed["symbol"] = parsed_wyckoff.get("symbol")
    parsed["side"] = parsed_wyckoff.get("side")
    parsed["price"] = parsed_wyckoff.get("price")
```

### 4.3 Добавить триггер:

```python
wyckoff_trigger = (cfg.get("trade_wyckoff", 0) and is_wyckoff)
```

### 4.4 Добавить direction check (после остальных):

```python
# Check Wyckoff enabled + direction filter
if wyckoff_trigger:
    wyckoff_settings = db.get_strategy_settings(uid, "wyckoff", ctx_exchange, ctx_account_type)
    signal_direction = "long" if side == "Buy" else "short"
    
    # CRITICAL: Check if this side is enabled
    side_enabled_key = f"{signal_direction}_enabled"
    side_enabled = wyckoff_settings.get(side_enabled_key, True)
    
    if not side_enabled:
        logger.info(f"[{uid}] {symbol}: Wyckoff {signal_direction.upper()} disabled → skip")
        wyckoff_trigger = False
    else:
        # Check direction filter
        wyckoff_direction = wyckoff_settings.get("direction", "all")
        
        if wyckoff_direction != "all" and wyckoff_direction != signal_direction:
            logger.info(f"[{uid}] {symbol}: Wyckoff direction filter → skip")
            wyckoff_trigger = False
```

### 4.5 Добавить в условие продолжения:

```python
if not (rsi_bb_trigger or bitk_trigger or scalper_trigger or elcaro_trigger or fibonacci_trigger or oi_trigger or wyckoff_trigger or dynamic_trigger):
    continue
```

### 4.6 Добавить вызов place_order:

В конце on_channel_post, где вызывается `place_order_for_targets`:

```python
if wyckoff_trigger:
    trade_params = get_strategy_trade_params(uid, "wyckoff", side, ctx_exchange, ctx_account_type)
    # ... place_order_for_targets call ...
```

---

## Шаг 5: Настройки по умолчанию (db.py)

### 5.1 STRATEGY_SETTINGS_DEFAULTS (~line 120):

```python
STRATEGY_SETTINGS_DEFAULTS = {
    # ... existing ...
    "wyckoff": {
        "long_enabled": True,
        "short_enabled": True,
        "long_percent": 1.0,
        "short_percent": 1.0,
        "long_sl_percent": 30.0,
        "short_sl_percent": 30.0,
        "long_tp_percent": 10.0,
        "short_tp_percent": 10.0,
        "leverage": 10,
        "direction": "all",
        "use_atr": False,
    },
}
```

### 5.2 DEFAULT_HL_STRATEGY_SETTINGS (если отличается для HyperLiquid):

```python
DEFAULT_HL_STRATEGY_SETTINGS = {
    # ... existing ...
    "wyckoff": {
        # Same as above
    },
}
```

---

## Проверка

После добавления:

1. **Проверить синтаксис:**
   ```bash
   python -m py_compile bot.py db.py
   ```

2. **Тест парсера:**
   ```python
   from bot import parse_wyckoff_signal
   result = parse_wyckoff_signal("📊 WYCKOFF LONG BTCUSDT\nEntry: 95000.00")
   print(result)  # {'symbol': 'BTCUSDT', 'side': 'Buy', 'price': 95000.0}
   ```

3. **Деплой:**
   ```bash
   git add -A && git commit -m "feat: Add Wyckoff strategy"
   git push && ssh server "cd project && git pull && sudo systemctl restart elcaro-bot"
   ```

---

## Файлы для изменения

| Файл | Что добавить |
|------|--------------|
| bot.py | Парсер, STRATEGY_FEATURES, UI keyboard, trigger, direction check |
| db.py | STRATEGY_SETTINGS_DEFAULTS |
| translations/*.py | Ключи перевода (опционально) |

---

## Архитектура стратегий

```
Сигнал из Telegram-канала
          ↓
    on_channel_post()
          ↓
    parse_*_signal() → распознает формат
          ↓
    get_strategy_settings() → читает настройки юзера
          ↓
    direction check → фильтр LONG/SHORT/ALL
          ↓
    get_strategy_trade_params() → параметры сделки
          ↓
    place_order_for_targets() → открытие позиции
          ↓
    set_trading_stop() → установка SL/TP
```

---

*Last updated: 21 February 2026*
