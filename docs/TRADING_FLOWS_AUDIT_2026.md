# Trading Flows Audit - January 2026

## 📊 Обзор

Этот документ содержит результаты полного аудита торговой логики проекта Enliko Trading Platform.

**Дата аудита:** 31 января 2026  
**Автор:** Copilot Agent  

---

## 🔄 Полный Путь Пользователя

### 1. Старт → Настройка API ключей

```
/start
  ↓
Проверка is_allowed (регистрация/ожидание доступа)
  ↓
Main Menu (bot.py: main_menu_keyboard)
  ↓
🔗 API Keys (callback: settings:api)
  ↓
Bybit / HyperLiquid selection
  ↓
Demo/Real ключи (шифруются перед сохранением)
  ↓
Валидация API ключей (testnet/mainnet проверка)
```

### 2. Торговля по Стратегиям

#### 2.1 Получение Сигнала

```
Signal Source (Channel/API)
  ↓
parse_signal() - распознавание формата
  ↓
Validation: symbol в symbols.txt, licensed strategy
  ↓
get_strategy_trade_params(uid, strategy, side) - bot.py:3920
  ↓
Returns: percent, sl_pct, tp_pct, use_atr, be_enabled, be_trigger_pct,
         partial_tp settings, dca settings, atr_trigger_pct, atr_mult_sl
```

#### 2.2 Открытие Позиции

```
calc_qty(equity, entry_pct, sl_pct, price)
  ↓
set_leverage() с fallback: 50→25→10→5→3→2→1
  ↓
place_order() - market/limit
  ↓
add_active_position() - db.py:2217
  PRIMARY KEY: (user_id, symbol, account_type, exchange)
  ↓
set_trading_stop() - SL/TP установка
```

#### 2.3 4D Schema для Настроек

```sql
-- user_strategy_settings
PRIMARY KEY: (user_id, strategy, side, exchange)

-- Каждая комбинация имеет независимые настройки:
- sl_pct, tp_pct, percent
- use_atr, atr_trigger_pct, atr_mult_sl
- be_enabled, be_trigger_pct
- partial_tp_enabled, partial_tp_1_trigger_pct, partial_tp_1_close_pct
- dca_enabled, dca_pct_1, dca_pct_2
```

---

## 🔍 Monitor Loop (bot.py:17250)

### Цикл Мониторинга Позиций

```
monitor_positions_loop()
  ↓
For each active user:
  ↓
  For each enabled exchange/account_type:
    ↓
    1. Fetch positions from exchange API
    2. Detect new positions (external/manual)
    3. Check closed positions → log trade
    4. Run SL/TP/ATR/BE/PTP logic
```

### Обнаружение Новых Позиций (Manual Strategy)

```python
# bot.py:17518
if sym not in existing_db_symbols:
    detected_strategy = await detect_signal_strategy(uid, sym, side)
    final_strategy = detected_strategy or "manual"  # Default to manual
    
    add_active_position(uid, sym, side, entry, size, 
                        strategy=final_strategy,
                        exchange=current_exchange)
```

### Проверка trade_manual Toggle

```python
# bot.py:17605-17607
if strategy == "manual" and not cfg.get("trade_manual", 1):
    logger.debug(f"[{uid}] {sym}: Manual position - trade_manual disabled, skipping SL/TP")
    continue  # Не устанавливаем SL/TP для manual позиций
```

---

## 📈 Фичи Мониторинга

### 1. ATR Trailing Stop

```python
# bot.py:18700-18800
if pos_use_atr:
    atr_val = await calc_atr(sym, interval="60", periods=atr_periods)
    
    # Pre-trigger phase (move_pct < trigger_pct)
    if move_pct < trigger_pct and not _atr_triggered.get(key):
        # Set initial SL based on sl_pct
        base_sl = entry * (1 - sl_pct/100)  # for Long
        await set_trading_stop(uid, sym, sl_price=base_sl)
    
    # Trailing phase (move_pct >= trigger_pct)
    else:
        _atr_triggered[key] = True
        # Calculate trailing SL
        new_sl = mark - atr_val * atr_mult_sl  # for Long
        if new_sl > current_sl:
            await set_trading_stop(uid, sym, sl_price=new_sl)
```

### 2. Break-Even (BE)

```python
# bot.py:18401-18442
if be_enabled and move_pct >= be_trigger_pct and not _be_triggered.get(key):
    be_sl = entry  # SL = Entry price
    
    should_move_to_be = (
        current_sl is None or
        (side == "Buy" and current_sl < entry) or
        (side == "Sell" and current_sl > entry)
    )
    
    if should_move_to_be:
        await set_trading_stop(uid, sym, sl_price=be_sl)
        _be_triggered[key] = True
        # Notification: "🔄 Break-Even: {symbol} SL → entry @ {price}"
```

### 3. Partial Take Profit

```python
# bot.py:18447-18560
if ptp_enabled and move_pct > 0:
    # Step 1
    if move_pct >= ptp_1_trigger and not step_1_done:
        qty_to_close = current_size * (ptp_1_close / 100)
        await close_position_partial(uid, sym, qty_to_close)
        mark_ptp_step_done(ap, step=1)
    
    # Step 2
    if move_pct >= ptp_2_trigger and step_1_done and not step_2_done:
        qty_to_close = current_size * (ptp_2_close / 100)
        await close_position_partial(uid, sym, qty_to_close)
        mark_ptp_step_done(ap, step=2)
```

### 4. DCA (Dollar Cost Averaging)

```python
# bot.py:18300-18395
if dca_enabled:
    # DCA Level 1: -dca_pct_1% (default 10%)
    if move_pct <= -dca_pct_1 and not dca_10_done:
        add_qty = calculate_dca_qty(current_size)
        await place_order(uid, sym, side, qty=add_qty)
        mark_dca_done(ap, level=1)
    
    # DCA Level 2: -dca_pct_2% (default 25%)
    if move_pct <= -dca_pct_2 and dca_10_done and not dca_25_done:
        add_qty = calculate_dca_qty(current_size)
        await place_order(uid, sym, side, qty=add_qty)
        mark_dca_done(ap, level=2)
```

---

## 📊 Статистика (ИСПРАВЛЕНО)

### get_trade_stats() - db.py:3295

**КРИТИЧЕСКИЙ БАГ ИСПРАВЛЕН (31 января 2026):**

```python
# БЫЛО: exchange параметр НЕ добавлялся в WHERE clause!
def get_trade_stats(user_id, strategy=None, period="all", account_type=None, exchange=None):
    where_clauses = ["user_id = ?"]
    if strategy: where_clauses.append("strategy = ?")
    if account_type: where_clauses.append("(account_type = ? OR account_type IS NULL)")
    # exchange был пропущен!

# ИСПРАВЛЕНО:
def get_trade_stats(user_id, strategy=None, period="all", account_type=None, exchange=None):
    where_clauses = ["user_id = ?"]
    if strategy: where_clauses.append("strategy = ?")
    if account_type: where_clauses.append("(account_type = ? OR account_type IS NULL)")
    if exchange: where_clauses.append("(exchange = ? OR exchange IS NULL)")  # ADDED!
```

**Также исправлено в:**
- `get_trade_stats_unknown()` - db.py:3580
- `open_positions count` query в `get_trade_stats()` - db.py:3430

### log_exit_and_remove_position() - bot.py:17173

Все 3 вызова корректно передают exchange:

```python
# bot.py:13720, 13883, 17939
log_exit_and_remove_position(
    user_id=uid,
    symbol=symbol,
    ...
    exchange=ap.get("exchange") or current_exchange or "bybit",  # ✅
)
```

---

## 🛒 Spot Trading

### spot_auto_dca_loop - bot.py:19101

```python
async def spot_auto_dca_loop(app):
    """Background loop for automatic spot DCA."""
    while True:
        await asyncio.sleep(3600)  # Check every hour
        
        for uid in get_all_users():
            cfg = get_user_config(uid)
            spot_settings = cfg.get("spot_settings") or {}
            
            if not cfg.get("spot_enabled"):
                continue
            if not spot_settings.get("auto_dca"):
                continue
            
            frequency = spot_settings.get("frequency", "manual")
            if frequency == "manual":
                continue
            
            # Check if enough time has passed
            interval = SPOT_DCA_INTERVALS.get(frequency)
            last_exec = spot_settings.get("last_dca_ts", 0)
            
            if now - last_exec >= interval:
                # Execute DCA for all configured coins
                for coin in coins:
                    adjusted_amount = await calculate_smart_dca_amount(...)
                    await place_spot_order(uid, coin, "Buy", adjusted_amount)
```

### spot_tp_rebalance_loop - bot.py:18819

```python
async def spot_tp_rebalance_loop(app):
    """Background loop for spot TP and portfolio rebalancing."""
    while True:
        await asyncio.sleep(300)  # Check every 5 minutes
        
        for uid in get_all_users():
            spot_settings = cfg.get("spot_settings") or {}
            
            if not cfg.get("spot_enabled"):
                continue
            
            # Check TP conditions for each holding
            for holding in spot_holdings:
                pnl_pct = calculate_spot_pnl(holding)
                
                if pnl_pct >= tp_percent:
                    # Execute TP - sell and rebalance
                    await execute_spot_tp(uid, holding)
```

---

## ✅ Итоги Аудита

### Исправленные Проблемы

| # | Проблема | Файл | Статус |
|---|----------|------|--------|
| 1 | exchange не в WHERE clause get_trade_stats | db.py:3330 | ✅ Fixed |
| 2 | exchange не в WHERE clause get_trade_stats_unknown | db.py:3595 | ✅ Fixed |
| 3 | exchange не в WHERE open_positions count | db.py:3430 | ✅ Fixed |

### Проверенные Компоненты

| Компонент | Статус | Комментарий |
|-----------|--------|-------------|
| 4D Schema (user, strategy, side, exchange) | ✅ | Работает корректно |
| ATR Trailing Stop | ✅ | trigger_pct + atr_mult_sl |
| Break-Even (BE) | ✅ | be_enabled + be_trigger_pct |
| Partial Take Profit | ✅ | 2 steps с настройками |
| DCA добор | ✅ | 2 уровня (-10%, -25%) |
| Manual Strategy | ✅ | trade_manual toggle |
| Spot Auto DCA | ✅ | Hourly loop |
| Spot TP/Rebalance | ✅ | 5-min loop |
| add_trade_log exchange | ✅ | Все 3 вызова корректны |
| log_exit_and_remove_position | ✅ | Все параметры передаются |

---

## 📋 Рекомендации

1. **Мониторинг:** Добавить алерты при резком росте trade_logs без exchange
2. **Тесты:** Добавить integration tests для 4D schema изоляции
3. **Документация:** Обновить API docs с описанием exchange filtering

---

*Аудит завершён: 31 января 2026*
