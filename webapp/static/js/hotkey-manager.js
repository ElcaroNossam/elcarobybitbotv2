/**
 * Enliko Trading Platform - Customizable Hotkey Manager
 * Version 1.0.0 - February 2026
 * 
 * Full-featured hotkey system with user customization and persistence.
 */

const HotkeyManager = {
    // ============================================================
    // STATE & CONFIG
    // ============================================================
    bindings: new Map(),
    enabled: true,
    settingsOpen: false,
    editingKey: null,
    
    // Default hotkey configuration
    defaultHotkeys: {
        // Trading Actions
        'buy_long': { keys: 'b', description: '📈 Buy / Long', category: 'trading', action: 'setSide("buy")' },
        'sell_short': { keys: 's', description: '📉 Sell / Short', category: 'trading', action: 'setSide("sell")' },
        'submit_order': { keys: 'Enter', description: '✅ Submit Order', category: 'trading', action: 'submitOrder()' },
        'quick_buy_25': { keys: 'Ctrl+B', description: '⚡ Quick Buy 25%', category: 'trading', action: 'quickPercentOrder("buy", 25)' },
        'quick_sell_25': { keys: 'Ctrl+S', description: '⚡ Quick Sell 25%', category: 'trading', action: 'quickPercentOrder("sell", 25)' },
        'quick_buy_50': { keys: 'Ctrl+Shift+B', description: '💥 Quick Buy 50%', category: 'trading', action: 'quickPercentOrder("buy", 50)' },
        'quick_sell_50': { keys: 'Ctrl+Shift+S', description: '💥 Quick Sell 50%', category: 'trading', action: 'quickPercentOrder("sell", 50)' },
        'quick_buy_100': { keys: 'Alt+B', description: '🔥 Quick Buy 100%', category: 'trading', action: 'quickPercentOrder("buy", 100)' },
        'quick_sell_100': { keys: 'Alt+S', description: '🔥 Quick Sell 100%', category: 'trading', action: 'quickPercentOrder("sell", 100)' },
        'close_all_positions': { keys: 'Ctrl+Shift+X', description: '❌ Close All Positions', category: 'trading', action: 'closeAllPositions()' },
        
        // Order Types
        'order_limit': { keys: '1', description: '📋 Limit Order', category: 'orders', action: 'setOrderType("limit")' },
        'order_market': { keys: '2', description: '⚡ Market Order', category: 'orders', action: 'setOrderType("market")' },
        'order_conditional': { keys: '3', description: '🎯 Conditional Order', category: 'orders', action: 'setOrderType("conditional")' },
        'toggle_reduce_only': { keys: 'R', description: '🔄 Toggle Reduce Only', category: 'orders', action: 'toggleReduceOnly()' },
        
        // Size Presets
        'size_25': { keys: 'Shift+1', description: '25% Size', category: 'size', action: 'setPercentSize(25)' },
        'size_50': { keys: 'Shift+2', description: '50% Size', category: 'size', action: 'setPercentSize(50)' },
        'size_75': { keys: 'Shift+3', description: '75% Size', category: 'size', action: 'setPercentSize(75)' },
        'size_100': { keys: 'Shift+4', description: '100% Size', category: 'size', action: 'setPercentSize(100)' },
        
        // Navigation & UI
        'clear_form': { keys: 'Escape', description: '🗑️ Clear Form', category: 'navigation', action: 'clearOrderForm()' },
        'toggle_tpsl': { keys: 'T', description: '🎯 Toggle TP/SL Panel', category: 'navigation', action: 'toggleTPSLPanel()' },
        'focus_price': { keys: 'P', description: '💰 Focus Price Input', category: 'navigation', action: 'focusPriceInput()' },
        'focus_size': { keys: 'Q', description: '📊 Focus Size Input', category: 'navigation', action: 'focusSizeInput()' },
        'open_calculator': { keys: 'C', description: '🔢 Risk Calculator', category: 'navigation', action: 'showRiskCalc()' },
        'open_dca': { keys: 'D', description: '📊 DCA Builder', category: 'navigation', action: 'showDCABuilder()' },
        'show_hotkeys': { keys: '?', description: '⌨️ Show Hotkeys Help', category: 'navigation', action: 'HotkeyManager.showHelp()' },
        'open_settings': { keys: 'Ctrl+,', description: '⚙️ Hotkey Settings', category: 'navigation', action: 'HotkeyManager.showSettings()' },
        
        // Chart Controls
        'chart_timeframe_1m': { keys: 'Alt+1', description: '📈 1m Timeframe', category: 'chart', action: 'changeTimeframe("1")' },
        'chart_timeframe_5m': { keys: 'Alt+2', description: '📈 5m Timeframe', category: 'chart', action: 'changeTimeframe("5")' },
        'chart_timeframe_15m': { keys: 'Alt+3', description: '📈 15m Timeframe', category: 'chart', action: 'changeTimeframe("15")' },
        'chart_timeframe_1h': { keys: 'Alt+4', description: '📈 1H Timeframe', category: 'chart', action: 'changeTimeframe("60")' },
        'chart_timeframe_4h': { keys: 'Alt+5', description: '📈 4H Timeframe', category: 'chart', action: 'changeTimeframe("240")' },
        'chart_timeframe_1d': { keys: 'Alt+6', description: '📈 1D Timeframe', category: 'chart', action: 'changeTimeframe("D")' },
        
        // Leverage Presets
        'leverage_1x': { keys: 'Ctrl+1', description: '1x Leverage', category: 'leverage', action: 'setLeverage(1)' },
        'leverage_5x': { keys: 'Ctrl+2', description: '5x Leverage', category: 'leverage', action: 'setLeverage(5)' },
        'leverage_10x': { keys: 'Ctrl+3', description: '10x Leverage', category: 'leverage', action: 'setLeverage(10)' },
        'leverage_25x': { keys: 'Ctrl+4', description: '25x Leverage', category: 'leverage', action: 'setLeverage(25)' },
        'leverage_50x': { keys: 'Ctrl+5', description: '50x Leverage', category: 'leverage', action: 'setLeverage(50)' },
    },
    
    // User's custom hotkeys (loaded from storage)
    userHotkeys: {},
    
    // ============================================================
    // INITIALIZATION
    // ============================================================
    init() {
        this.loadUserHotkeys();
        this.applyHotkeys();
        this.bindKeyboardEvents();
        console.log('🎹 HotkeyManager initialized with', this.bindings.size, 'hotkeys');
    },
    
    bindKeyboardEvents() {
        document.addEventListener('keydown', (e) => {
            if (!this.enabled || this.settingsOpen) return;
            
            // Skip if typing in input fields
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) {
                if (e.key === 'Escape') {
                    e.target.blur();
                }
                return;
            }
            
            const keyCombo = this.getKeyCombo(e);
            const binding = this.bindings.get(keyCombo.toLowerCase());
            
            if (binding) {
                e.preventDefault();
                e.stopPropagation();
                this.executeAction(binding.action);
            }
        });
    },
    
    // ============================================================
    // HOTKEY MANAGEMENT
    // ============================================================
    getKeyCombo(e) {
        const parts = [];
        if (e.ctrlKey || e.metaKey) parts.push('Ctrl');
        if (e.altKey) parts.push('Alt');
        if (e.shiftKey) parts.push('Shift');
        
        // Normalize key names
        let key = e.key;
        if (key === ' ') key = 'Space';
        else if (key.length === 1) key = key.toUpperCase();
        
        parts.push(key);
        return parts.join('+');
    },
    
    parseKeyCombo(combo) {
        return combo.split('+').map(k => k.trim()).join('+');
    },
    
    applyHotkeys() {
        this.bindings.clear();
        
        // Merge defaults with user customizations
        const allHotkeys = { ...this.defaultHotkeys };
        for (const [id, config] of Object.entries(this.userHotkeys)) {
            if (allHotkeys[id]) {
                allHotkeys[id] = { ...allHotkeys[id], ...config };
            }
        }
        
        // Register all hotkeys
        for (const [id, config] of Object.entries(allHotkeys)) {
            if (config.enabled === false) continue; // Skip disabled hotkeys
            
            const keyCombo = this.parseKeyCombo(config.keys);
            this.bindings.set(keyCombo.toLowerCase(), {
                id,
                action: config.action,
                description: config.description,
                category: config.category
            });
        }
    },
    
    executeAction(actionStr) {
        try {
            // Execute the action in global scope
            const fn = new Function(actionStr);
            fn();
        } catch (err) {
            console.error('Hotkey action error:', err, actionStr);
        }
    },
    
    // ============================================================
    // PERSISTENCE (localStorage + API)
    // ============================================================
    loadUserHotkeys() {
        try {
            // First try localStorage
            const stored = localStorage.getItem('enliko_hotkeys');
            if (stored) {
                this.userHotkeys = JSON.parse(stored);
            }
            
            // Then try to sync from server (async)
            this.syncFromServer();
        } catch (err) {
            console.error('Failed to load hotkeys:', err);
            this.userHotkeys = {};
        }
    },
    
    saveUserHotkeys() {
        try {
            // Save to localStorage immediately
            localStorage.setItem('enliko_hotkeys', JSON.stringify(this.userHotkeys));
            
            // Sync to server (async)
            this.syncToServer();
            
            // Re-apply hotkeys
            this.applyHotkeys();
        } catch (err) {
            console.error('Failed to save hotkeys:', err);
        }
    },
    
    async syncFromServer() {
        const token = localStorage.getItem('enliko_token');
        if (!token) return;
        
        try {
            const res = await fetch('/api/users/preferences/hotkeys', {
                headers: { 'Authorization': 'Bearer ' + token }
            });
            
            if (res.ok) {
                const data = await res.json();
                if (data.hotkeys && Object.keys(data.hotkeys).length > 0) {
                    this.userHotkeys = data.hotkeys;
                    localStorage.setItem('enliko_hotkeys', JSON.stringify(this.userHotkeys));
                    this.applyHotkeys();
                }
            }
        } catch (err) {
            console.log('Could not sync hotkeys from server, using local');
        }
    },
    
    async syncToServer() {
        const token = localStorage.getItem('enliko_token');
        if (!token) return;
        
        try {
            await fetch('/api/users/preferences/hotkeys', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + token
                },
                body: JSON.stringify({ hotkeys: this.userHotkeys })
            });
        } catch (err) {
            console.log('Could not sync hotkeys to server');
        }
    },
    
    // ============================================================
    // SETTINGS UI
    // ============================================================
    showSettings() {
        this.settingsOpen = true;
        
        const categories = this.getCategories();
        const modal = document.createElement('div');
        modal.className = 'hotkey-settings-overlay';
        modal.id = 'hotkeySettingsModal';
        modal.innerHTML = `
            <div class="hotkey-settings-modal">
                <div class="hotkey-settings-header">
                    <h2><i class="fas fa-keyboard"></i> Keyboard Shortcuts Settings</h2>
                    <div class="hotkey-header-actions">
                        <button class="hotkey-btn-secondary" onclick="HotkeyManager.resetToDefaults()">
                            <i class="fas fa-undo"></i> Reset All
                        </button>
                        <button class="hotkey-btn-close" onclick="HotkeyManager.closeSettings()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                
                <div class="hotkey-settings-body">
                    <div class="hotkey-search-bar">
                        <i class="fas fa-search"></i>
                        <input type="text" id="hotkeySearch" placeholder="Search shortcuts..." oninput="HotkeyManager.filterHotkeys(this.value)">
                    </div>
                    
                    <div class="hotkey-categories-tabs">
                        <button class="hotkey-tab active" data-category="all" onclick="HotkeyManager.switchCategory('all')">
                            <i class="fas fa-th"></i> All
                        </button>
                        ${categories.map(cat => `
                            <button class="hotkey-tab" data-category="${cat.id}" onclick="HotkeyManager.switchCategory('${cat.id}')">
                                ${cat.icon} ${cat.name}
                            </button>
                        `).join('')}
                    </div>
                    
                    <div class="hotkey-list" id="hotkeyList">
                        ${this.renderHotkeyList()}
                    </div>
                </div>
                
                <div class="hotkey-settings-footer">
                    <span class="hotkey-tip">
                        <i class="fas fa-lightbulb"></i>
                        Click on a shortcut to customize it. Press <kbd>Esc</kbd> to cancel editing.
                    </span>
                    <button class="hotkey-btn-primary" onclick="HotkeyManager.closeSettings()">
                        <i class="fas fa-check"></i> Done
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Animate in
        requestAnimationFrame(() => modal.classList.add('active'));
        
        // Bind edit key capture
        this.bindEditKeyCapture();
    },
    
    getCategories() {
        return [
            { id: 'trading', name: 'Trading', icon: '💹' },
            { id: 'orders', name: 'Orders', icon: '📋' },
            { id: 'size', name: 'Size', icon: '📊' },
            { id: 'leverage', name: 'Leverage', icon: '⚖️' },
            { id: 'chart', name: 'Chart', icon: '📈' },
            { id: 'navigation', name: 'Navigation', icon: '🧭' }
        ];
    },
    
    renderHotkeyList(filter = '', category = 'all') {
        const allHotkeys = { ...this.defaultHotkeys };
        for (const [id, config] of Object.entries(this.userHotkeys)) {
            if (allHotkeys[id]) {
                allHotkeys[id] = { ...allHotkeys[id], ...config };
            }
        }
        
        const entries = Object.entries(allHotkeys)
            .filter(([id, config]) => {
                const matchesFilter = !filter || 
                    config.description.toLowerCase().includes(filter.toLowerCase()) ||
                    config.keys.toLowerCase().includes(filter.toLowerCase());
                const matchesCategory = category === 'all' || config.category === category;
                return matchesFilter && matchesCategory;
            });
        
        if (entries.length === 0) {
            return `<div class="hotkey-empty"><i class="fas fa-search"></i> No shortcuts found</div>`;
        }
        
        return entries.map(([id, config]) => {
            const isEnabled = config.enabled !== false;
            const isCustom = this.userHotkeys[id]?.keys && this.userHotkeys[id].keys !== this.defaultHotkeys[id]?.keys;
            
            return `
                <div class="hotkey-item ${isEnabled ? '' : 'disabled'}" data-id="${id}" data-category="${config.category}">
                    <div class="hotkey-item-info">
                        <span class="hotkey-description">${config.description}</span>
                        ${isCustom ? '<span class="hotkey-badge custom">Custom</span>' : ''}
                    </div>
                    <div class="hotkey-item-controls">
                        <button class="hotkey-key-btn" onclick="HotkeyManager.startEdit('${id}')" title="Click to change">
                            ${this.renderKeyCombo(config.keys)}
                        </button>
                        <button class="hotkey-toggle ${isEnabled ? 'on' : ''}" onclick="HotkeyManager.toggleHotkey('${id}')" title="${isEnabled ? 'Disable' : 'Enable'}">
                            <i class="fas ${isEnabled ? 'fa-toggle-on' : 'fa-toggle-off'}"></i>
                        </button>
                        ${isCustom ? `
                            <button class="hotkey-reset-btn" onclick="HotkeyManager.resetHotkey('${id}')" title="Reset to default">
                                <i class="fas fa-undo"></i>
                            </button>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');
    },
    
    renderKeyCombo(keys) {
        return keys.split('+').map(k => `<kbd>${k}</kbd>`).join(' + ');
    },
    
    switchCategory(category) {
        document.querySelectorAll('.hotkey-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.category === category);
        });
        document.getElementById('hotkeyList').innerHTML = this.renderHotkeyList(
            document.getElementById('hotkeySearch')?.value || '',
            category
        );
    },
    
    filterHotkeys(filter) {
        const activeCategory = document.querySelector('.hotkey-tab.active')?.dataset.category || 'all';
        document.getElementById('hotkeyList').innerHTML = this.renderHotkeyList(filter, activeCategory);
    },
    
    // ============================================================
    // HOTKEY EDITING
    // ============================================================
    startEdit(hotkeyId) {
        this.editingKey = hotkeyId;
        
        const item = document.querySelector(`.hotkey-item[data-id="${hotkeyId}"]`);
        const keyBtn = item?.querySelector('.hotkey-key-btn');
        
        if (keyBtn) {
            keyBtn.innerHTML = '<span class="hotkey-recording"><i class="fas fa-keyboard"></i> Press keys...</span>';
            keyBtn.classList.add('recording');
        }
        
        // Show instruction toast
        this.showToast('Press the key combination you want to assign, or Escape to cancel', 'info');
    },
    
    bindEditKeyCapture() {
        const handler = (e) => {
            if (!this.editingKey) return;
            
            e.preventDefault();
            e.stopPropagation();
            
            if (e.key === 'Escape') {
                this.cancelEdit();
                return;
            }
            
            // Ignore modifier-only presses
            if (['Control', 'Alt', 'Shift', 'Meta'].includes(e.key)) {
                return;
            }
            
            const newKeyCombo = this.getKeyCombo(e);
            
            // Check for conflicts
            const conflict = this.checkConflict(newKeyCombo, this.editingKey);
            if (conflict) {
                this.showToast(`"${newKeyCombo}" is already used by "${conflict.description}"`, 'warning');
                return;
            }
            
            // Apply the new key combo
            this.setHotkeyKeys(this.editingKey, newKeyCombo);
            this.finishEdit();
            this.showToast(`Shortcut updated to ${newKeyCombo}`, 'success');
        };
        
        document.addEventListener('keydown', handler, { capture: true });
        
        // Store handler for cleanup
        this._editHandler = handler;
    },
    
    cancelEdit() {
        if (!this.editingKey) return;
        
        // Restore display
        const item = document.querySelector(`.hotkey-item[data-id="${this.editingKey}"]`);
        const keyBtn = item?.querySelector('.hotkey-key-btn');
        
        if (keyBtn) {
            const config = this.userHotkeys[this.editingKey] || this.defaultHotkeys[this.editingKey];
            keyBtn.innerHTML = this.renderKeyCombo(config.keys);
            keyBtn.classList.remove('recording');
        }
        
        this.editingKey = null;
    },
    
    finishEdit() {
        this.editingKey = null;
        
        // Re-render the list
        const activeCategory = document.querySelector('.hotkey-tab.active')?.dataset.category || 'all';
        document.getElementById('hotkeyList').innerHTML = this.renderHotkeyList(
            document.getElementById('hotkeySearch')?.value || '',
            activeCategory
        );
    },
    
    checkConflict(keyCombo, excludeId) {
        const keyLower = keyCombo.toLowerCase();
        
        for (const [k, binding] of this.bindings.entries()) {
            if (k === keyLower && binding.id !== excludeId) {
                return binding;
            }
        }
        
        return null;
    },
    
    setHotkeyKeys(hotkeyId, keys) {
        if (!this.userHotkeys[hotkeyId]) {
            this.userHotkeys[hotkeyId] = {};
        }
        this.userHotkeys[hotkeyId].keys = keys;
        this.saveUserHotkeys();
    },
    
    toggleHotkey(hotkeyId) {
        if (!this.userHotkeys[hotkeyId]) {
            this.userHotkeys[hotkeyId] = {};
        }
        
        const current = this.userHotkeys[hotkeyId].enabled !== false;
        this.userHotkeys[hotkeyId].enabled = !current;
        this.saveUserHotkeys();
        
        // Update UI
        const activeCategory = document.querySelector('.hotkey-tab.active')?.dataset.category || 'all';
        document.getElementById('hotkeyList').innerHTML = this.renderHotkeyList(
            document.getElementById('hotkeySearch')?.value || '',
            activeCategory
        );
        
        this.showToast(`Shortcut ${current ? 'disabled' : 'enabled'}`, 'info');
    },
    
    resetHotkey(hotkeyId) {
        delete this.userHotkeys[hotkeyId];
        this.saveUserHotkeys();
        
        // Update UI
        const activeCategory = document.querySelector('.hotkey-tab.active')?.dataset.category || 'all';
        document.getElementById('hotkeyList').innerHTML = this.renderHotkeyList(
            document.getElementById('hotkeySearch')?.value || '',
            activeCategory
        );
        
        this.showToast('Shortcut reset to default', 'success');
    },
    
    resetToDefaults() {
        if (!confirm('Reset all keyboard shortcuts to their default values?')) {
            return;
        }
        
        this.userHotkeys = {};
        this.saveUserHotkeys();
        
        // Update UI
        document.getElementById('hotkeyList').innerHTML = this.renderHotkeyList();
        this.showToast('All shortcuts reset to defaults', 'success');
    },
    
    closeSettings() {
        this.cancelEdit();
        this.settingsOpen = false;
        
        const modal = document.getElementById('hotkeySettingsModal');
        if (modal) {
            modal.classList.remove('active');
            setTimeout(() => modal.remove(), 300);
        }
        
        // Cleanup handler
        if (this._editHandler) {
            document.removeEventListener('keydown', this._editHandler, { capture: true });
            this._editHandler = null;
        }
    },
    
    // ============================================================
    // HELP MODAL
    // ============================================================
    showHelp() {
        const categories = this.getCategories();
        const allHotkeys = { ...this.defaultHotkeys };
        for (const [id, config] of Object.entries(this.userHotkeys)) {
            if (allHotkeys[id]) {
                allHotkeys[id] = { ...allHotkeys[id], ...config };
            }
        }
        
        const modal = document.createElement('div');
        modal.className = 'hotkey-help-overlay';
        modal.innerHTML = `
            <div class="hotkey-help-modal">
                <div class="hotkey-help-header">
                    <h2><i class="fas fa-keyboard"></i> Keyboard Shortcuts</h2>
                    <button class="hotkey-btn-close" onclick="this.closest('.hotkey-help-overlay').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="hotkey-help-body">
                    ${categories.map(cat => {
                        const items = Object.entries(allHotkeys)
                            .filter(([id, config]) => config.category === cat.id && config.enabled !== false);
                        
                        if (items.length === 0) return '';
                        
                        return `
                            <div class="hotkey-help-category">
                                <h3>${cat.icon} ${cat.name}</h3>
                                <div class="hotkey-help-grid">
                                    ${items.map(([id, config]) => `
                                        <div class="hotkey-help-item">
                                            <span class="hotkey-help-desc">${config.description.replace(/^[^\s]+\s/, '')}</span>
                                            <span class="hotkey-help-keys">${this.renderKeyCombo(config.keys)}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
                <div class="hotkey-help-footer">
                    <button class="hotkey-btn-secondary" onclick="this.closest('.hotkey-help-overlay').remove(); HotkeyManager.showSettings();">
                        <i class="fas fa-cog"></i> Customize Shortcuts
                    </button>
                </div>
            </div>
        `;
        
        modal.onclick = (e) => {
            if (e.target === modal) modal.remove();
        };
        
        document.body.appendChild(modal);
        requestAnimationFrame(() => modal.classList.add('active'));
    },
    
    // ============================================================
    // UTILITY
    // ============================================================
    showToast(message, type = 'info') {
        if (typeof showNotification === 'function') {
            showNotification(message, type);
        } else if (typeof Notifications !== 'undefined') {
            Notifications.show(message, type);
        } else {
            console.log(`[${type}] ${message}`);
        }
    },
    
    // Export current config for debugging
    exportConfig() {
        return {
            defaults: this.defaultHotkeys,
            user: this.userHotkeys,
            active: Object.fromEntries(this.bindings)
        };
    }
};

// ============================================================
// ACTION FUNCTIONS (used by hotkeys)
// ============================================================

// Quick percent order functions
function quickPercentOrder(side, percent) {
    if (typeof window.state === 'undefined') return;
    
    // Calculate size based on balance and percent
    const balance = parseFloat(document.getElementById('availableBalance')?.textContent?.replace(/[$,]/g, '')) || 0;
    const price = window.state.lastPrice || parseFloat(document.getElementById('symbolPrice')?.textContent?.replace(/[$,]/g, '')) || 0;
    const leverage = window.state.leverage || 10;
    
    if (!balance || !price) {
        HotkeyManager.showToast('Cannot calculate order size - missing balance or price', 'warning');
        return;
    }
    
    const marginToUse = balance * (percent / 100);
    const size = (marginToUse * leverage) / price;
    
    // Set the values
    if (typeof setSide === 'function') setSide(side);
    if (typeof setOrderType === 'function') setOrderType('market');
    
    const sizeInput = document.getElementById('sizeInput');
    if (sizeInput) {
        sizeInput.value = size.toFixed(6);
        sizeInput.dispatchEvent(new Event('input'));
    }
    
    // Submit if one-click trading is enabled
    if (typeof OneClickTrading !== 'undefined' && OneClickTrading.state?.enabled) {
        if (typeof submitOrder === 'function') submitOrder();
    }
}

function clearOrderForm() {
    const sizeInput = document.getElementById('sizeInput');
    const priceInput = document.getElementById('priceInput');
    const tpInput = document.getElementById('tpInput');
    const slInput = document.getElementById('slInput');
    
    if (sizeInput) sizeInput.value = '';
    if (priceInput) priceInput.value = '';
    if (tpInput) tpInput.value = '';
    if (slInput) slInput.value = '';
}

function toggleTPSLPanel() {
    const tpslSection = document.querySelector('.tpsl-section');
    if (tpslSection) {
        tpslSection.classList.toggle('collapsed');
    }
}

function focusPriceInput() {
    const input = document.getElementById('priceInput');
    if (input) input.focus();
}

function focusSizeInput() {
    const input = document.getElementById('sizeInput');
    if (input) input.focus();
}

function toggleReduceOnly() {
    const checkbox = document.getElementById('reduceOnly');
    if (checkbox) {
        checkbox.checked = !checkbox.checked;
        HotkeyManager.showToast(`Reduce Only: ${checkbox.checked ? 'ON' : 'OFF'}`, 'info');
    }
}

function setPercentSize(percent) {
    const balance = parseFloat(document.getElementById('availableBalance')?.textContent?.replace(/[$,]/g, '')) || 0;
    const price = window.state?.lastPrice || parseFloat(document.getElementById('symbolPrice')?.textContent?.replace(/[$,]/g, '')) || 0;
    const leverage = window.state?.leverage || 10;
    
    if (!balance || !price) return;
    
    const marginToUse = balance * (percent / 100);
    const size = (marginToUse * leverage) / price;
    
    const sizeInput = document.getElementById('sizeInput');
    if (sizeInput) {
        sizeInput.value = size.toFixed(6);
        sizeInput.dispatchEvent(new Event('input'));
    }
    
    HotkeyManager.showToast(`Size set to ${percent}%`, 'info');
}

function closeAllPositions() {
    if (!confirm('Close ALL open positions?')) return;
    
    const token = localStorage.getItem('enliko_token');
    if (!token) {
        HotkeyManager.showToast('Please log in first', 'error');
        return;
    }
    
    fetch('/api/trading/close-all', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({
            exchange: window.state?.exchange || 'bybit',
            account_type: window.state?.accountType || 'demo'
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            HotkeyManager.showToast('All positions closed', 'success');
            if (typeof loadPositions === 'function') loadPositions();
        } else {
            HotkeyManager.showToast(data.error || 'Failed to close positions', 'error');
        }
    })
    .catch(err => {
        HotkeyManager.showToast('Error closing positions', 'error');
    });
}

function changeTimeframe(tf) {
    const select = document.getElementById('timeframeSelect');
    if (select) {
        select.value = tf;
        select.dispatchEvent(new Event('change'));
    }
}

// ============================================================
// CSS STYLES (injected on load)
// ============================================================
const hotkeyStyles = document.createElement('style');
hotkeyStyles.textContent = `
/* Hotkey Settings Modal */
.hotkey-settings-overlay,
.hotkey-help-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(8px);
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.hotkey-settings-overlay.active,
.hotkey-help-overlay.active {
    opacity: 1;
}

.hotkey-settings-modal {
    background: var(--bg-card, #1a1a2e);
    border: 1px solid var(--border, #333);
    border-radius: 16px;
    width: 90%;
    max-width: 700px;
    max-height: 85vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    transform: scale(0.95);
    transition: transform 0.3s ease;
}

.hotkey-settings-overlay.active .hotkey-settings-modal,
.hotkey-help-overlay.active .hotkey-help-modal {
    transform: scale(1);
}

.hotkey-settings-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid var(--border, #333);
}

.hotkey-settings-header h2 {
    font-size: 1.25rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 0;
    color: var(--text, #fff);
}

.hotkey-header-actions {
    display: flex;
    gap: 8px;
}

.hotkey-btn-secondary {
    background: var(--bg-secondary, #252540);
    border: 1px solid var(--border, #333);
    color: var(--text-muted, #888);
    padding: 8px 12px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.8rem;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.2s;
}

.hotkey-btn-secondary:hover {
    background: var(--bg-hover, #303050);
    color: var(--text, #fff);
}

.hotkey-btn-close {
    background: transparent;
    border: none;
    color: var(--text-muted, #888);
    width: 32px;
    height: 32px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.2s;
}

.hotkey-btn-close:hover {
    background: var(--bg-secondary, #252540);
    color: var(--text, #fff);
}

.hotkey-settings-body {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    padding: 16px 0;
}

.hotkey-search-bar {
    display: flex;
    align-items: center;
    background: var(--bg-secondary, #252540);
    border: 1px solid var(--border, #333);
    border-radius: 8px;
    margin: 0 24px 16px;
    padding: 10px 14px;
}

.hotkey-search-bar i {
    color: var(--text-muted, #888);
    margin-right: 10px;
}

.hotkey-search-bar input {
    flex: 1;
    background: none;
    border: none;
    outline: none;
    color: var(--text, #fff);
    font-size: 0.9rem;
}

.hotkey-search-bar input::placeholder {
    color: var(--text-muted, #666);
}

.hotkey-categories-tabs {
    display: flex;
    gap: 6px;
    padding: 0 24px 16px;
    overflow-x: auto;
    flex-wrap: nowrap;
}

.hotkey-tab {
    background: var(--bg-secondary, #252540);
    border: 1px solid var(--border, #333);
    color: var(--text-muted, #888);
    padding: 8px 14px;
    border-radius: 20px;
    cursor: pointer;
    font-size: 0.8rem;
    white-space: nowrap;
    transition: all 0.2s;
}

.hotkey-tab:hover {
    background: var(--bg-hover, #303050);
}

.hotkey-tab.active {
    background: var(--accent, #6366f1);
    border-color: var(--accent, #6366f1);
    color: #fff;
}

.hotkey-list {
    flex: 1;
    overflow-y: auto;
    padding: 0 24px;
}

.hotkey-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: var(--bg-secondary, #252540);
    border: 1px solid var(--border, #333);
    border-radius: 10px;
    margin-bottom: 8px;
    transition: all 0.2s;
}

.hotkey-item:hover {
    border-color: var(--accent, #6366f1);
}

.hotkey-item.disabled {
    opacity: 0.5;
}

.hotkey-item-info {
    display: flex;
    align-items: center;
    gap: 8px;
}

.hotkey-description {
    font-size: 0.9rem;
    color: var(--text, #fff);
}

.hotkey-badge {
    font-size: 0.65rem;
    padding: 2px 6px;
    border-radius: 4px;
    text-transform: uppercase;
    font-weight: 600;
}

.hotkey-badge.custom {
    background: var(--accent, #6366f1);
    color: #fff;
}

.hotkey-item-controls {
    display: flex;
    align-items: center;
    gap: 8px;
}

.hotkey-key-btn {
    background: var(--bg-card, #1a1a2e);
    border: 1px solid var(--border, #333);
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 4px;
    transition: all 0.2s;
    min-width: 80px;
    justify-content: center;
}

.hotkey-key-btn:hover {
    border-color: var(--accent, #6366f1);
}

.hotkey-key-btn.recording {
    border-color: var(--yellow, #fbbf24);
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

.hotkey-key-btn kbd {
    background: var(--bg-secondary, #252540);
    padding: 3px 7px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-family: var(--font-mono, monospace);
    color: var(--text, #fff);
    border: 1px solid var(--border, #444);
}

.hotkey-recording {
    color: var(--yellow, #fbbf24);
    font-size: 0.75rem;
    display: flex;
    align-items: center;
    gap: 6px;
}

.hotkey-toggle {
    background: transparent;
    border: none;
    color: var(--text-muted, #666);
    font-size: 1.2rem;
    cursor: pointer;
    transition: color 0.2s;
    padding: 4px;
}

.hotkey-toggle.on {
    color: var(--green, #10b981);
}

.hotkey-reset-btn {
    background: transparent;
    border: none;
    color: var(--text-muted, #666);
    cursor: pointer;
    padding: 4px 8px;
    font-size: 0.8rem;
    transition: color 0.2s;
}

.hotkey-reset-btn:hover {
    color: var(--red, #ef4444);
}

.hotkey-empty {
    text-align: center;
    padding: 40px;
    color: var(--text-muted, #666);
}

.hotkey-settings-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    border-top: 1px solid var(--border, #333);
}

.hotkey-tip {
    font-size: 0.8rem;
    color: var(--text-muted, #888);
    display: flex;
    align-items: center;
    gap: 8px;
}

.hotkey-tip kbd {
    background: var(--bg-secondary, #252540);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.7rem;
}

.hotkey-btn-primary {
    background: var(--accent, #6366f1);
    border: none;
    color: #fff;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.2s;
}

.hotkey-btn-primary:hover {
    filter: brightness(1.1);
}

/* Help Modal */
.hotkey-help-modal {
    background: var(--bg-card, #1a1a2e);
    border: 1px solid var(--border, #333);
    border-radius: 16px;
    width: 90%;
    max-width: 600px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    transform: scale(0.95);
    transition: transform 0.3s ease;
}

.hotkey-help-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border, #333);
}

.hotkey-help-header h2 {
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text, #fff);
}

.hotkey-help-body {
    flex: 1;
    overflow-y: auto;
    padding: 16px 20px;
}

.hotkey-help-category {
    margin-bottom: 20px;
}

.hotkey-help-category h3 {
    font-size: 0.9rem;
    font-weight: 600;
    margin: 0 0 10px;
    color: var(--accent, #6366f1);
    display: flex;
    align-items: center;
    gap: 6px;
}

.hotkey-help-grid {
    display: grid;
    gap: 6px;
}

.hotkey-help-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: var(--bg-secondary, #252540);
    border-radius: 6px;
}

.hotkey-help-desc {
    font-size: 0.85rem;
    color: var(--text, #fff);
}

.hotkey-help-keys {
    display: flex;
    gap: 4px;
}

.hotkey-help-keys kbd {
    background: var(--bg-card, #1a1a2e);
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-family: var(--font-mono, monospace);
    color: var(--text, #fff);
    border: 1px solid var(--border, #444);
}

.hotkey-help-footer {
    padding: 12px 20px;
    border-top: 1px solid var(--border, #333);
    display: flex;
    justify-content: center;
}
`;
document.head.appendChild(hotkeyStyles);

// ============================================================
// AUTO-INITIALIZE
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    HotkeyManager.init();
});

// Export for global access
window.HotkeyManager = HotkeyManager;
