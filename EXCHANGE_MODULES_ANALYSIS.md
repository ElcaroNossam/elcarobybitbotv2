# 🔍 АНАЛИЗ МОДУЛЕЙ ТОРГОВЛИ ПО БИРЖАМ

## Дата проверки: December 23, 2025

---

## ✅ ОБНАРУЖЕННЫЕ ПРОБЛЕМЫ

### 1. **bot_unified.py - НЕ ПЕРЕДАЕТСЯ account_type**

**Проблема:**
```python
# bot_unified.py line 34
client = get_exchange_client(user_id)  # ❌ account_type не передается!
```

**Решение:**
```python
# Нужно добавить параметр account_type и передать в get_exchange_client
client = get_exchange_client(user_id, account_type=account_type)
```

**Где используется:**
- `get_balance_unified()` - line 21
- `get_positions_unified()` - line 52
- `place_order_unified()` - line 104
- `close_position_unified()` - line 207
- `set_leverage_unified()` - line 308

---

### 2. **core/exchange_client.py - get_exchange_client НЕ ПРИНИМАЕТ account_type**

**Текущая сигнатура:**
```python
# line 353
async def get_exchange_client(user_id: int, exchange_type: Optional[str] = None) -> UnifiedExchangeClient:
```

**Проблема:**
- Функция использует `db.get_trading_mode(user_id)` для определения demo/real
- Но не позволяет явно указать account_type

**Решение:**
```python
async def get_exchange_client(
    user_id: int, 
    exchange_type: Optional[str] = None,
    account_type: Optional[str] = None  # ✅ Добавить этот параметр
) -> UnifiedExchangeClient:
    """
    Create an exchange client for a user.
    
    Args:
        user_id: Telegram user ID
        exchange_type: Force specific exchange ('bybit' or 'hyperliquid')
        account_type: Force account type ('demo', 'real', 'testnet')
    """
    import db
    
    # Get user's exchange preference
    if exchange_type is None:
        exchange_type = db.get_exchange_type(user_id)
    
    exchange = ExchangeType(exchange_type) if exchange_type else ExchangeType.BYBIT
    
    if exchange == ExchangeType.HYPERLIQUID:
        hl_creds = db.get_hl_credentials(user_id)
        credentials = ExchangeCredentials(
            exchange=ExchangeType.HYPERLIQUID,
            private_key=hl_creds.get("hl_private_key"),
            wallet_address=hl_creds.get("hl_wallet_address"),
            vault_address=hl_creds.get("hl_vault_address"),
            mode=AccountMode.TESTNET if hl_creds.get("hl_testnet") else AccountMode.REAL
        )
    else:
        # ✅ Use explicit account_type if provided
        if account_type is None:
            trading_mode = db.get_trading_mode(user_id)
            account_type = "real" if trading_mode == "real" else "demo"
        
        api_key, api_secret = db.get_user_credentials(user_id, account_type)
        
        # ✅ Support testnet mode
        if account_type == "testnet":
            mode = AccountMode.TESTNET
        elif account_type == "real":
            mode = AccountMode.REAL
        else:
            mode = AccountMode.DEMO
        
        credentials = ExchangeCredentials(
            exchange=ExchangeType.BYBIT,
            api_key=api_key,
            api_secret=api_secret,
            mode=mode
        )
    
    client = UnifiedExchangeClient(credentials)
    await client.initialize()
    return client
```

---

### 3. **bot.py - fetch_open_positions НЕ ИСПОЛЬЗУЕТ UNIFIED**

**Текущая реализация:**
```python
# line 6236
async def fetch_open_positions(user_id, *args, **kwargs) -> list:
    # ❌ Использует прямой вызов _bybit_request
    res = await _bybit_request(
        uid, "GET", "/v5/position/list",
        params={"category": "linear", "settleCoin": "USDT"}
    )
    return [p for p in (res.get("list") or []) if float(p.get("size") or 0) != 0.0]
```

**Проблемы:**
1. Только Bybit (нет поддержки HyperLiquid)
2. Не использует unified architecture
3. Возвращает dict вместо Position objects
4. Не учитывает account_type (demo/real)

**Решение:**
```python
async def fetch_open_positions(user_id, *args, **kwargs) -> list:
    """
    Fetch open positions using unified architecture
    Returns list of Position objects (unified format)
    """
    if USE_UNIFIED_ARCHITECTURE and UNIFIED_AVAILABLE:
        try:
            # ✅ Use unified function
            account_type = kwargs.get('account_type', 'demo')
            positions = await get_positions_unified(user_id, account_type=account_type)
            
            # Convert Position objects to dicts for backward compatibility
            return [pos.to_dict() for pos in positions]
        except Exception as e:
            logger.error(f"Unified fetch_open_positions error: {e}")
            # Fall through to old code
    
    # OLD CODE (fallback)
    try:
        uid = None
        if isinstance(user_id, int):
            uid = user_id
        else:
            update = user_id
            uid = getattr(getattr(update, "effective_user", None), "id", None)

        if uid is None:
            uid = kwargs.get("user_id")

        if uid is None:
            raise RuntimeError("fetch_open_positions: не удалось определить user_id")

        res = await _bybit_request(
            uid, "GET", "/v5/position/list",
            params={"category": "linear", "settleCoin": "USDT"}
        )
        return [p for p in (res.get("list") or []) if float(p.get("size") or 0) != 0.0]
    except MissingAPICredentials:
        return []
```

---

### 4. **Отображение позиций - НЕТ ПОДДЕРЖКИ HYPERLIQUID**

**Проблема в cmd_positions:**
```python
# line 6331
async def cmd_positions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    pos_list = await fetch_open_positions(uid)  # ❌ Только Bybit format
    
    # Работает только с Bybit полями:
    avg = float(p.get("avgPrice") or 0)  # ❌ HL использует другое название
    mark = float(p.get("markPrice") or 0)
    pnl_i = float(p.get("unrealisedPnl") or 0)
```

**Решение:**
Использовать unified Position objects с `.to_dict()`:
```python
async def cmd_positions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    if USE_UNIFIED_ARCHITECTURE:
        # ✅ Get unified Position objects
        positions_objs = await get_positions_unified(uid)
        pos_list = [pos.to_dict() for pos in positions_objs]  # Convert to dicts
    else:
        pos_list = await fetch_open_positions(uid)
    
    if not pos_list:
        return await update.message.reply_text(ctx.t['no_positions'])

    total_pnl = 0.0
    total_im = 0.0
    lines = [ctx.t['positions_header']]

    for idx, p in enumerate(pos_list, start=1):
        sym = p.get("symbol", "-")
        side = p.get("side", "-")
        lev = p.get("leverage", "-")
        
        # ✅ Unified fields работают с обеими биржами
        size = human_format(float(p.get("size", 0)))
        avg = float(p.get("entry_price", 0))  # ✅ unified field
        mark = float(p.get("mark_price", 0))   # ✅ unified field
        pnl_i = float(p.get("unrealized_pnl", 0))  # ✅ unified field
        im = float(p.get("margin_used", 0))    # ✅ unified field
        
        # ... rest of code
```

---

### 5. **WebApp trading.py - НЕТ УЧЕТА account_type В НЕКОТОРЫХ МЕСТАХ**

**Проблема:**
```python
# webapp/api/trading.py
@router.get("/positions")
async def get_positions(
    exchange: str = Query("bybit"),
    account_type: str = Query("demo"),  # ✅ Есть параметр
    user: dict = Depends(get_current_user)
):
    # ✅ Используется правильно в новом коде
    if SERVICES_AVAILABLE:
        result = await get_positions_service(user_id, exchange, account_type)
```

Здесь уже исправлено в предыдущей интеграции ✅

---

## 🏗️ АРХИТЕКТУРА ПО БИРЖАМ

### Bybit
```
Modes: DEMO, REAL, TESTNET
URLs:
  - DEMO: https://api-demo.bybit.com
  - REAL: https://api.bybit.com
  - TESTNET: https://api-testnet.bybit.com

Fields (API response):
  - symbol: "BTCUSDT"
  - side: "Buy" / "Sell"
  - size: "0.5"
  - avgPrice: "50000.0"
  - markPrice: "51000.0"
  - unrealisedPnl: "500.0"
  - positionIM: "5000.0"
  - leverage: "10"

Unified Conversion:
  Position.from_bybit(bybit_data)
```

### HyperLiquid
```
Modes: MAINNET, TESTNET
No API keys - uses private key signature

Fields (API response):
  - position.coin: "BTC"
  - position.szi: "0.5" (signed size, negative = short)
  - position.entryPx: "52000.0"
  - markPx: "53000.0"
  - position.unrealizedPnl: "300.0"
  - position.leverage.value: 5

Unified Conversion:
  Position.from_hyperliquid(hl_data)
```

---

## 📊 МАППИНГ ПОЛЕЙ

| Unified Field | Bybit API | HyperLiquid API |
|---------------|-----------|-----------------|
| `symbol` | `symbol` | `f"{coin}USD"` |
| `side` | `side` (Buy/Sell) | `szi > 0` → LONG, `< 0` → SHORT |
| `size` | `size` | `abs(szi)` |
| `entry_price` | `avgPrice` | `entryPx` |
| `mark_price` | `markPrice` | `markPx` |
| `unrealized_pnl` | `unrealisedPnl` | `unrealizedPnl` |
| `leverage` | `leverage` | `leverage.value` |
| `margin_used` | `positionIM` | `marginUsed` |
| `liquidation_price` | `liqPrice` | `liquidationPx` |

---

## ✅ ПЛАН ИСПРАВЛЕНИЙ

### Priority 1: Core Functions
1. ✅ Исправить `core/exchange_client.py::get_exchange_client()` - добавить `account_type` параметр
2. ✅ Исправить `bot_unified.py` - передавать `account_type` в `get_exchange_client()`
3. ✅ Добавить поддержку TESTNET mode для Bybit

### Priority 2: Bot Integration
4. ✅ Исправить `bot.py::fetch_open_positions()` - использовать unified architecture
5. ✅ Обновить `bot.py::cmd_positions()` - поддержка unified Position objects
6. ✅ Обновить форматирование позиций - использовать unified fields

### Priority 3: Testing
7. ✅ Создать тесты для всех режимов (demo/real/testnet)
8. ✅ Протестировать отображение позиций с обеих бирж
9. ✅ Проверить корректность данных в WebApp

---

## 🚀 СТАТУС РЕАЛИЗАЦИИ

- [x] Анализ завершен
- [ ] Исправления применены
- [ ] Тесты созданы
- [ ] Проверка на demo
- [ ] Готово к продакшну

---

**Следующий шаг:** Применить все исправления одним batch'ем через multi_replace_string_in_file

