# 🔧 Быстрые Исправления - 23 декабря 2025

## Текущие Проблемы и Решения

### 1. ❌ Скринер - Нет Переключения Бирж

**Файл:** `webapp/templates/screener.html` (строка ~488)

**Проблема:** Есть только Futures/Spot, нет выбора биржи

**Решение:** Добавить после market-type-toggle:

```html
<!-- ДОБАВИТЬ ПОСЛЕ строки 493 (после market-type-toggle) -->
<div class="exchange-selector" id="exchangeFilter">
    <button class="exchange-btn active" data-exchange="binance">
        <i class="fab fa-bitcoin"></i> Binance
    </button>
    <button class="exchange-btn" data-exchange="bybit">
        <span class="exchange-icon">⚡</span> Bybit
    </button>
    <button class="exchange-btn" data-exchange="okx">
        <span class="exchange-icon">🔷</span> OKX
    </button>
</div>
```

**CSS (добавить в <style>):**
```css
.exchange-selector {
    display: flex;
    gap: 10px;
}
.exchange-btn {
    padding: 8px 16px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
}
.exchange-btn:hover {
    background: var(--bg-hover);
    border-color: var(--accent);
}
.exchange-btn.active {
    background: linear-gradient(135deg, var(--green), #00cc6a);
    border-color: transparent;
    color: #000;
    font-weight: 600;
}
.exchange-icon {
    font-size: 16px;
}
```

**JavaScript (добавить в <script>):**
```javascript
let activeExchange = 'binance';

document.querySelectorAll('.exchange-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log('Switching exchange:', btn.dataset.exchange);
        document.querySelectorAll('.exchange-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeExchange = btn.dataset.exchange;
        
        // Reconnect WebSocket with new exchange
        if (ws) {
            ws.close();
            connectWS();
        }
    });
});

// Modify connectWS() to include exchange
function connectWS() {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${location.host}/ws/screener/${activeExchange}`);
    // ... rest of code
}
```

---

### 2. ❌ Стратегии - Стили Выпадающих Меню

**Файл:** `webapp/templates/strategies.html`

**Проблема:** Базовые `<select>` dropdown'ы

**Найти все `<select>` и заменить на:**

```html
<!-- Пример для Entry Conditions -->
<div class="custom-select" data-name="entry-indicator">
    <div class="select-trigger">
        <span class="select-value">RSI</span>
        <i class="fas fa-chevron-down"></i>
    </div>
    <div class="select-options">
        <div class="select-option" data-value="rsi">RSI</div>
        <div class="select-option" data-value="bb_upper">BB Upper</div>
        <div class="select-option" data-value="bb_lower">BB Lower</div>
        <div class="select-option" data-value="macd">MACD Signal</div>
        <div class="select-option" data-value="price">Price</div>
    </div>
</div>
```

**CSS (добавить в <style>):**
```css
.custom-select {
    position: relative;
    width: 100%;
}
.select-trigger {
    padding: 10px 15px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    transition: all 0.3s;
}
.select-trigger:hover {
    border-color: var(--accent);
    background: var(--bg-hover);
}
.custom-select.open .select-trigger {
    border-color: var(--accent-green);
}
.select-options {
    position: absolute;
    top: calc(100% + 5px);
    left: 0;
    right: 0;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    max-height: 250px;
    overflow-y: auto;
    z-index: 100;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all 0.3s;
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
}
.custom-select.open .select-options {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}
.select-option {
    padding: 10px 15px;
    cursor: pointer;
    transition: background 0.2s;
}
.select-option:hover {
    background: var(--bg-hover);
}
.select-option.selected {
    background: rgba(34, 197, 94, 0.1);
    color: var(--green);
}
```

**JavaScript:**
```javascript
// Custom Select Handler
document.querySelectorAll('.custom-select').forEach(select => {
    const trigger = select.querySelector('.select-trigger');
    const options = select.querySelectorAll('.select-option');
    
    trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        // Close all other selects
        document.querySelectorAll('.custom-select').forEach(s => {
            if (s !== select) s.classList.remove('open');
        });
        select.classList.toggle('open');
    });
    
    options.forEach(option => {
        option.addEventListener('click', (e) => {
            e.stopPropagation();
            const value = option.dataset.value;
            const text = option.textContent;
            
            // Update trigger
            trigger.querySelector('.select-value').textContent = text;
            
            // Update selected state
            options.forEach(opt => opt.classList.remove('selected'));
            option.classList.add('selected');
            
            // Close dropdown
            select.classList.remove('open');
            
            // Trigger change event
            select.dispatchEvent(new CustomEvent('change', {
                detail: { value, text }
            }));
        });
    });
});

// Close on outside click
document.addEventListener('click', () => {
    document.querySelectorAll('.custom-select.open').forEach(s => {
        s.classList.remove('open');
    });
});
```

---

### 3. ❌ Кнопка "New Strategy" Не Работает

**Файл:** `webapp/templates/strategies.html`

**Найти кнопку (примерно строка 145-155):**
```html
<button class="btn-create">
    <i class="fas fa-plus"></i> New Strategy
</button>
```

**Добавить обработчик:**
```javascript
document.querySelector('.btn-create')?.addEventListener('click', () => {
    console.log('Opening new strategy modal');
    openNewStrategyModal();
});

function openNewStrategyModal() {
    // Сбросить форму
    document.getElementById('strategyName').value = '';
    document.getElementById('strategyDesc').value = '';
    document.querySelectorAll('.indicator-card').forEach(card => {
        card.classList.remove('active');
    });
    activeIndicators.clear();
    
    // Показать модал
    const modal = document.getElementById('newStrategyModal');
    if (modal) {
        modal.style.display = 'flex';
        setTimeout(() => modal.classList.add('active'), 10);
    } else {
        console.error('Modal not found!');
    }
}

function closeNewStrategyModal() {
    const modal = document.getElementById('newStrategyModal');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => modal.style.display = 'none', 300);
    }
}
```

**Проверить что модал существует (если нет - добавить):**
```html
<!-- В конце body, перед закрывающим </body> -->
<div id="newStrategyModal" class="modal">
    <div class="modal-overlay" onclick="closeNewStrategyModal()"></div>
    <div class="modal-content modal-large">
        <div class="modal-header">
            <h2><i class="fas fa-plus-circle"></i> Create New Strategy</h2>
            <button class="modal-close" onclick="closeNewStrategyModal()">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="modal-body">
            <div class="form-group">
                <label>Strategy Name</label>
                <input type="text" id="strategyName" placeholder="My Awesome Strategy">
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea id="strategyDesc" rows="4" placeholder="Describe your strategy..."></textarea>
            </div>
            <!-- Добавить остальные поля -->
        </div>
        <div class="modal-footer">
            <button class="btn btn-outline" onclick="closeNewStrategyModal()">Cancel</button>
            <button class="btn btn-primary" onclick="saveNewStrategy()">
                <i class="fas fa-save"></i> Save Strategy
            </button>
        </div>
    </div>
</div>
```

**CSS для модала:**
```css
.modal {
    position: fixed;
    inset: 0;
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    opacity: 0;
    transition: opacity 0.3s;
}
.modal.active {
    opacity: 1;
}
.modal-overlay {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(10px);
}
.modal-content {
    position: relative;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 20px;
    width: 90%;
    max-width: 800px;
    max-height: 90vh;
    overflow-y: auto;
    transform: scale(0.9);
    transition: transform 0.3s;
}
.modal.active .modal-content {
    transform: scale(1);
}
.modal-header {
    padding: 25px;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.modal-close {
    width: 40px;
    height: 40px;
    border: none;
    background: var(--bg-tertiary);
    border-radius: 10px;
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.3s;
}
.modal-close:hover {
    background: var(--red);
    transform: rotate(90deg);
}
.modal-body {
    padding: 25px;
}
.modal-footer {
    padding: 20px 25px;
    border-top: 1px solid var(--border);
    display: flex;
    gap: 15px;
    justify-content: flex-end;
}
```

---

### 4. ✅ Бэктест Модуль - Что Уже Работает

**Файл:** `webapp/templates/backtest.html` (3469 строк)

**УЖЕ РЕАЛИЗОВАНО:**
- ✅ Полный UI с Chart.js
- ✅ Выбор стратегии
- ✅ Настройки (TP, SL, leverage, timeframe)
- ✅ Кнопка запуска
- ✅ Результаты

**ЧТО НУЖНО ДОБАВИТЬ:**
1. **Права доступа (админ vs пользователь)**
2. **Real-time WebSocket прогресс**
3. **Сохранение результатов**

---

### 5. 🔐 Права Доступа

**Файл:** `webapp/api/backtest_pro.py`

**Добавить проверку admin:**

```python
from fastapi import Depends, HTTPException
from coin_params import ADMIN_ID

def get_current_user(authorization: str = Header(None)):
    # Parse JWT token
    if not authorization:
        raise HTTPException(401, "Not authenticated")
    token = authorization.replace('Bearer ', '')
    # Validate token and get user_id
    user_id = validate_jwt(token)  # Implement this
    return user_id

def is_admin(user_id: int = Depends(get_current_user)):
    if user_id != ADMIN_ID:
        raise HTTPException(403, "Admin only")
    return user_id

# Применить к эндпоинтам:
@router.post("/strategy/create")
async def create_strategy(
    strategy: CustomStrategyRequest,
    user_id: int = Depends(is_admin)  # Только админ
):
    # Create strategy logic
    pass

@router.get("/strategy/{id}/full")
async def get_strategy_full(
    id: str,
    user_id: int = Depends(get_current_user)
):
    # Полные данные только для админа
    strategy = get_strategy_from_db(id)
    
    if user_id != ADMIN_ID:
        # Скрыть код стратегии для обычных пользователей
        return {
            "id": strategy.id,
            "name": strategy.name,
            "description": strategy.description,
            "performance": strategy.performance,
            # НЕ возвращать indicators, entry_rules, exit_rules
        }
    
    # Админ видит всё
    return strategy
```

**Frontend (backtest.html):**
```javascript
const ADMIN_ID = 511692487;  // Из coin_params.py

async function loadStrategies() {
    const res = await fetch('/api/strategies/list', {
        headers: getAuthHeaders()
    });
    const data = await res.json();
    
    data.strategies.forEach(strategy => {
        const card = createStrategyCard(strategy);
        
        // Если не админ - скрыть кнопки редактирования
        if (USER_ID !== ADMIN_ID) {
            card.querySelectorAll('.btn-edit, .btn-delete').forEach(btn => {
                btn.style.display = 'none';
            });
        }
        
        container.appendChild(card);
    });
}
```

---

## ⚡ Приоритетные Действия

1. **СЕЙЧАС:** Добавить переключение бирж в скринер (15 мин)
2. **СЕЙЧАС:** Исправить стили select в стратегиях (20 мин)
3. **СЕЙЧАС:** Починить кнопку New Strategy (10 мин)
4. **ПОТОМ:** Добавить права доступа в API (30 мин)
5. **ПОТОМ:** WebSocket прогресс бэктеста (45 мин)

---

## 📝 Команды для Тестирования

```bash
# Перезапустить сервисы
./start.sh --restart

# Проверить статус
./start.sh --status

# Логи
tail -f logs/webapp.log
tail -f logs/bot.log

# Тест API
curl http://localhost:8765/api/strategies/list
curl http://localhost:8765/api/screener/overview?market=futures
```

---

**Статус:** Готово к применению  
**Время:** ~2 часа на все исправления  
**Приоритет:** HIGH - это критические баги UI
