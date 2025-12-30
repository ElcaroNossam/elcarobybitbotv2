# 🎯 Шаблон добавления новой стратегии

> **Для AI:** При добавлении новой стратегии следовать этому чек-листу пошагово.

## 📋 Чек-лист (в порядке выполнения)

### 1. ✅ База данных (db.py)

**Файл:** `db.py`

```python
# 1.1 Добавить в USER_FIELDS_WHITELIST (~line 72-75):
"trade_newstrategy",

# 1.2 Добавить колонку в CREATE TABLE users (~line 212):
trade_newstrategy  INTEGER NOT NULL DEFAULT 0,

# 1.3 Добавить миграцию (~line 251):
("trade_newstrategy",  "ALTER TABLE users ADD COLUMN trade_newstrategy  INTEGER NOT NULL DEFAULT 0"),
```

---

### 2. ✅ Конфигурация стратегии (bot.py)

**Файл:** `bot.py`

```python
# 2.1 Добавить в STRATEGY_NAMES_MAP (~line 4563):
STRATEGY_NAMES_MAP = {
    ...
    "newstrategy": "NewStrategy",  # Отображаемое имя
}

# 2.2 Добавить в STRATEGY_FEATURES (~line 4660):
STRATEGY_FEATURES = {
    ...
    "newstrategy": {
        "order_type": True,      # Market/Limit toggle
        "coins_group": True,     # Coins filter (ALL/TOP100/VOLATILE)
        "leverage": True,        # Leverage setting
        "use_atr": True,         # ATR trailing toggle
        "direction": True,       # LONG/SHORT/ALL filter
        "side_settings": True,   # Separate LONG/SHORT settings
        "percent": True,         # Position size %
        "sl_tp": True,           # SL/TP settings
        "atr_params": True,      # ATR params
        "hl_settings": True,     # HyperLiquid support
        "min_quality": False,    # Quality filter (if needed)
    },
}
```

---

### 3. ✅ Парсер сигналов (bot.py)

**Файл:** `bot.py` (~после line 9475)

```python
# 3.1 Regex для парсинга сигналов:
NEWSTRATEGY_RE_HDR = re.compile(r'NewStrategy Signal', re.I)
NEWSTRATEGY_RE_SYMBOL = re.compile(r'\[([A-Z0-9]+USDT)\]')
NEWSTRATEGY_RE_SIDE = re.compile(r'\b(LONG|SHORT)\b', re.I)
NEWSTRATEGY_RE_PRICE = re.compile(r'\bPrice\s*[:=]\s*' + NUM, re.I)

# 3.2 Функция проверки:
def is_newstrategy_signal(text: str) -> bool:
    """Check if message is NewStrategy signal."""
    return bool(NEWSTRATEGY_RE_HDR.search(text))

# 3.3 Функция парсинга:
def parse_newstrategy_signal(text: str) -> dict | None:
    """Parse NewStrategy signal.
    
    Format:
        NewStrategy Signal
        [BTCUSDT] LONG
        Price: 50000
    
    Returns dict with parsed data or None.
    """
    if not is_newstrategy_signal(text):
        return None
    
    m_sym = NEWSTRATEGY_RE_SYMBOL.search(text)
    m_side = NEWSTRATEGY_RE_SIDE.search(text)
    m_px = NEWSTRATEGY_RE_PRICE.search(text)
    
    if not (m_sym and m_side and m_px):
        return None
    
    symbol = m_sym.group(1).upper()
    side = "Buy" if m_side.group(1).upper() == "LONG" else "Sell"
    price = _tof(m_px.group(1))
    
    return {"symbol": symbol, "side": side, "price": price}
```

---

### 4. ✅ Обработка сигналов (bot.py)

**Файл:** `bot.py`

```python
# 4.1 В on_channel_post (~line 9840):
# Добавить парсинг:
parsed_newstrategy = parse_newstrategy_signal(txt)
is_newstrategy = parsed_newstrategy is not None

# 4.2 Добавить проверку стратегии для юзера (~line 9940+):
newstrategy_trigger = is_newstrategy and bool(cfg.get('trade_newstrategy', 0))

# 4.3 Добавить coins filter check (~line 10028):
if newstrategy_trigger and not check_coins_filter("newstrategy"):
    newstrategy_trigger = False

# 4.4 Добавить direction filter (~line 10055):
if newstrategy_trigger:
    ns_settings = db.get_strategy_settings(uid, "newstrategy", ctx_exchange, ctx_account_type)
    ns_direction = ns_settings.get("direction", "all")
    signal_direction = "long" if side == "Buy" else "short"
    if ns_direction != "all" and ns_direction != signal_direction:
        newstrategy_trigger = False

# 4.5 В process_signal (~line 10130+):
# Добавить обработку в место где триггеры -> торговля:
if newstrategy_trigger:
    detected_strategy = "newstrategy"
    # ... торговая логика ...
```

---

### 5. ✅ Переключатель стратегии (bot.py)

**Файл:** `bot.py` (~line 4460)

```python
@log_calls
@require_access
async def cmd_toggle_newstrategy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Toggle NewStrategy trading on/off."""
    uid = update.effective_user.id
    cfg = get_user_config(uid)
    new_val = 0 if cfg.get('trade_newstrategy', 0) else 1
    set_user_field(uid, 'trade_newstrategy', new_val)
    status = ctx.t['status_enabled'] if new_val else ctx.t['status_disabled']
    await update.message.reply_text(
        f"🆕 NewStrategy: {status}",
        reply_markup=main_menu_keyboard(ctx, update=update)
    )
```

---

### 6. ✅ Регистрация handler'ов (bot.py)

**Файл:** `bot.py` (~line 16674)

```python
# 6.1 CommandHandler:
app.add_handler(CommandHandler("toggle_newstrategy", cmd_toggle_newstrategy))

# 6.2 В on_text (~line 13755):
if text == ctx.t.get("button_newstrategy"):
    return await cmd_toggle_newstrategy(update, ctx)
```

---

### 7. ✅ Переводы (translations/*.py)

**Файл:** `translations/en.py` (и все 14 других языков)

```python
# 7.1 Кнопка:
'button_newstrategy':          '🆕 NewStrategy',

# 7.2 Конфиг:
'config_trade_newstrategy':    '🆕 NewStrategy: {state}',

# 7.3 Уведомления об ордерах:
'newstrategy_limit_entry':     '🆕 *NewStrategy Limit Entry*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
'newstrategy_limit_error':     '❌ NewStrategy Limit error: {msg}',
'newstrategy_market_entry':    '🆕 *NewStrategy Market Entry*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
'newstrategy_market_error':    '❌ NewStrategy Market error: {msg}',
'newstrategy_market_ok':       '🆕 *NewStrategy: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%',
```

---

### 8. ✅ WebApp интеграция

**Файл:** `webapp/services/strategy_deployer.py` (~line 37)

```python
STRATEGY_FIELD_MAP = {
    ...
    "newstrategy": "trade_newstrategy",
}
```

**Файл:** `webapp/api/strategy_sync.py` (~line 131)

```python
STRATEGIES = [
    ...
    {"name": "newstrategy", "field": "trade_newstrategy"},
]
```

**Файл:** `webapp/api/users.py` (~line 627)

```python
STRATEGY_FEATURES = {
    ...
    "newstrategy": {
        # Скопировать структуру из bot.py
    },
}
```

---

### 9. ✅ Тесты

**Файл:** `tests/conftest.py` (~line 80)

```python
# В CREATE TABLE users:
trade_newstrategy INTEGER DEFAULT 0,
```

---

## 🚀 Команда добавления (для AI)

При запросе "Добавь стратегию X с каналом Y":

1. Определить формат сигналов канала (попросить пример если нужно)
2. Написать regex парсеры
3. Добавить во ВСЕ файлы по чек-листу выше
4. Запустить `python3 utils/translation_sync.py --report` для синхронизации переводов
5. Проверить синтаксис: `python3 -c "import ast; ast.parse(open('bot.py').read())"`
6. Запустить тесты: `python3 -m pytest tests/ -x -q`
7. Commit и deploy

---

## 📊 Текущие стратегии

| Strategy | DB Field | Emoji | Parser Function |
|----------|----------|-------|-----------------|
| OI | trade_oi | 📉 | (internal) |
| RSI+BB | trade_rsi_bb | 📊 | (internal) |
| Scryptomera | trade_scryptomera | 🔮 | parse_bitk_signal |
| Scalper | trade_scalper | 🎯 | parse_scalper_signal |
| Elcaro | trade_elcaro | 🔥 | parse_elcaro_signal |
| Fibonacci | trade_fibonacci | 📐 | parse_fibonacci_signal |

---

## 📁 Файлы для изменений

| Файл | Что менять |
|------|------------|
| `db.py` | USER_FIELDS_WHITELIST, CREATE TABLE, миграция |
| `bot.py` | STRATEGY_NAMES_MAP, STRATEGY_FEATURES, парсер, handler, on_channel_post |
| `translations/*.py` | button_, config_, _entry, _error ключи |
| `webapp/services/strategy_deployer.py` | STRATEGY_FIELD_MAP |
| `webapp/api/strategy_sync.py` | STRATEGIES list |
| `webapp/api/users.py` | STRATEGY_FEATURES |
| `tests/conftest.py` | trade_X в test schema |

---

*Последнее обновление: December 30, 2025*
