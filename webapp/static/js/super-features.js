/**
 * Enliko Super Features v1.0
 * Premium trading experience enhancements
 * 
 * Features:
 * - 🎉 Confetti on profit trades
 * - 🔔 Sound notifications
 * - ⌨️ Keyboard shortcuts
 * - 📊 Animated counters
 * - 📳 Haptic feedback
 * - 🎨 Theme animations
 * - 💀 Skeleton loading
 * - 🚀 Performance optimizations
 */

// ===== CONFETTI CELEBRATION =====
class ConfettiCelebration {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.particles = [];
        this.animating = false;
    }

    init() {
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'confetti-canvas';
        this.canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 99999;
        `;
        document.body.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');
        this.resize();
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    celebrate(pnl = 0) {
        if (!this.canvas) this.init();
        
        // Create particles based on profit size
        const particleCount = Math.min(150, 50 + Math.floor(pnl / 10));
        const colors = ['#22c55e', '#10b981', '#fbbf24', '#f59e0b', '#3b82f6', '#8b5cf6'];
        
        for (let i = 0; i < particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: -10,
                size: Math.random() * 8 + 4,
                speedX: Math.random() * 6 - 3,
                speedY: Math.random() * 8 + 4,
                color: colors[Math.floor(Math.random() * colors.length)],
                rotation: Math.random() * 360,
                rotationSpeed: Math.random() * 10 - 5,
                shape: Math.random() > 0.5 ? 'rect' : 'circle'
            });
        }

        if (!this.animating) {
            this.animating = true;
            this.animate();
        }

        // Play celebration sound
        SoundEffects.play('success');
        
        // Haptic feedback
        HapticFeedback.success();
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.particles = this.particles.filter(p => {
            p.x += p.speedX;
            p.y += p.speedY;
            p.speedY += 0.2; // Gravity
            p.rotation += p.rotationSpeed;

            this.ctx.save();
            this.ctx.translate(p.x, p.y);
            this.ctx.rotate((p.rotation * Math.PI) / 180);
            this.ctx.fillStyle = p.color;
            
            if (p.shape === 'rect') {
                this.ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
            } else {
                this.ctx.beginPath();
                this.ctx.arc(0, 0, p.size / 2, 0, Math.PI * 2);
                this.ctx.fill();
            }
            
            this.ctx.restore();

            return p.y < this.canvas.height + 20;
        });

        if (this.particles.length > 0) {
            requestAnimationFrame(() => this.animate());
        } else {
            this.animating = false;
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }
    }
}

// ===== SOUND EFFECTS =====
const SoundEffects = {
    enabled: localStorage.getItem('enliko_sounds') !== 'false',
    volume: parseFloat(localStorage.getItem('enliko_volume') || '0.5'),
    
    sounds: {
        success: { frequency: 800, duration: 150, type: 'sine' },
        error: { frequency: 200, duration: 300, type: 'square' },
        notification: { frequency: 600, duration: 100, type: 'sine' },
        click: { frequency: 1000, duration: 50, type: 'sine' },
        trade: { frequency: [523, 659, 784], duration: 100, type: 'sine' }, // C-E-G chord
        alert: { frequency: 440, duration: 200, type: 'triangle' }
    },

    audioContext: null,

    getContext() {
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        return this.audioContext;
    },

    play(soundName) {
        if (!this.enabled) return;
        
        const sound = this.sounds[soundName];
        if (!sound) return;

        try {
            const ctx = this.getContext();
            const frequencies = Array.isArray(sound.frequency) ? sound.frequency : [sound.frequency];
            
            frequencies.forEach((freq, i) => {
                const oscillator = ctx.createOscillator();
                const gainNode = ctx.createGain();
                
                oscillator.type = sound.type;
                oscillator.frequency.setValueAtTime(freq, ctx.currentTime);
                
                gainNode.gain.setValueAtTime(this.volume * 0.3, ctx.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + sound.duration / 1000);
                
                oscillator.connect(gainNode);
                gainNode.connect(ctx.destination);
                
                oscillator.start(ctx.currentTime + (i * 0.05));
                oscillator.stop(ctx.currentTime + sound.duration / 1000 + (i * 0.05));
            });
        } catch (e) {
            console.warn('Sound playback failed:', e);
        }
    },

    toggle() {
        this.enabled = !this.enabled;
        localStorage.setItem('enliko_sounds', this.enabled);
        return this.enabled;
    },

    setVolume(vol) {
        this.volume = Math.max(0, Math.min(1, vol));
        localStorage.setItem('enliko_volume', this.volume);
    }
};

// ===== HAPTIC FEEDBACK =====
const HapticFeedback = {
    enabled: 'vibrate' in navigator,

    light() {
        if (this.enabled) navigator.vibrate(10);
    },

    medium() {
        if (this.enabled) navigator.vibrate(25);
    },

    heavy() {
        if (this.enabled) navigator.vibrate(50);
    },

    success() {
        if (this.enabled) navigator.vibrate([50, 50, 100]);
    },

    error() {
        if (this.enabled) navigator.vibrate([100, 50, 100, 50, 100]);
    },

    selection() {
        if (this.enabled) navigator.vibrate(5);
    }
};

// ===== KEYBOARD SHORTCUTS =====
class KeyboardShortcuts {
    constructor() {
        this.shortcuts = new Map();
        this.enabled = true;
        this.modalOpen = false;
    }

    init() {
        // Trading shortcuts
        this.register('b', () => this.quickOrder('long'), 'Quick Long');
        this.register('s', () => this.quickOrder('short'), 'Quick Short');
        this.register('c', () => this.closeAllPositions(), 'Close All Positions');
        this.register('Escape', () => this.cancelAction(), 'Cancel / Close Modal');
        
        // Navigation shortcuts
        this.register('1', () => this.switchTab('positions'), 'Positions Tab');
        this.register('2', () => this.switchTab('orders'), 'Orders Tab');
        this.register('3', () => this.switchTab('trades'), 'Trades Tab');
        this.register('4', () => this.switchTab('signals'), 'Signals Tab');
        
        // Chart shortcuts
        this.register('ArrowUp', () => this.adjustLeverage(1), 'Increase Leverage');
        this.register('ArrowDown', () => this.adjustLeverage(-1), 'Decrease Leverage');
        this.register('m', () => this.toggleOrderType(), 'Toggle Market/Limit');
        
        // UI shortcuts
        this.register('/', () => this.openSearch(), 'Search Symbol');
        this.register('?', () => this.showShortcutsModal(), 'Show Shortcuts');
        this.register('t', () => this.toggleTheme(), 'Toggle Theme');
        this.register('n', () => SoundEffects.toggle(), 'Toggle Sounds');

        document.addEventListener('keydown', (e) => this.handleKeydown(e));
    }

    register(key, action, description) {
        this.shortcuts.set(key.toLowerCase(), { action, description, key });
    }

    handleKeydown(e) {
        // Ignore if typing in input
        if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;
        if (!this.enabled) return;

        const key = e.key.toLowerCase();
        const shortcut = this.shortcuts.get(key);
        
        if (shortcut) {
            e.preventDefault();
            HapticFeedback.selection();
            shortcut.action();
        }
    }

    quickOrder(side) {
        const orderBtn = document.querySelector(`.order-btn.${side}, [data-side="${side}"]`);
        if (orderBtn) {
            orderBtn.click();
            SoundEffects.play('click');
        }
    }

    closeAllPositions() {
        if (confirm('Close all positions?')) {
            document.querySelector('[onclick*="closeAll"], .close-all-btn')?.click();
        }
    }

    cancelAction() {
        document.querySelector('.modal.show .close-btn, .modal-close')?.click();
    }

    switchTab(tabName) {
        document.querySelector(`[data-tab="${tabName}"], .tab-btn[onclick*="${tabName}"]`)?.click();
    }

    adjustLeverage(delta) {
        const leverageInput = document.querySelector('#leverageSlider, input[name="leverage"]');
        if (leverageInput) {
            leverageInput.value = Math.max(1, Math.min(100, parseInt(leverageInput.value) + delta));
            leverageInput.dispatchEvent(new Event('input'));
        }
    }

    toggleOrderType() {
        document.querySelector('.order-type-toggle, [onclick*="toggleOrderType"]')?.click();
    }

    openSearch() {
        document.querySelector('.symbol-selector, [onclick*="openSymbol"]')?.click();
    }

    toggleTheme() {
        ThemeAnimator.toggle();
    }

    showShortcutsModal() {
        const shortcuts = Array.from(this.shortcuts.entries())
            .map(([key, { description }]) => `
                <div class="shortcut-item">
                    <kbd>${key.toUpperCase()}</kbd>
                    <span>${description}</span>
                </div>
            `).join('');

        const modal = document.createElement('div');
        modal.className = 'shortcuts-modal';
        modal.innerHTML = `
            <div class="shortcuts-content">
                <div class="shortcuts-header">
                    <h3>⌨️ Keyboard Shortcuts</h3>
                    <button onclick="this.closest('.shortcuts-modal').remove()">✕</button>
                </div>
                <div class="shortcuts-grid">${shortcuts}</div>
            </div>
        `;
        document.body.appendChild(modal);
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    }
}

// ===== ANIMATED COUNTER =====
class AnimatedCounter {
    static animate(element, endValue, options = {}) {
        const {
            duration = 1000,
            prefix = '',
            suffix = '',
            decimals = 2,
            colorize = true
        } = options;

        const startValue = parseFloat(element.dataset.value) || 0;
        const startTime = performance.now();
        
        element.dataset.value = endValue;

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function (ease-out-expo)
            const eased = 1 - Math.pow(2, -10 * progress);
            const currentValue = startValue + (endValue - startValue) * eased;
            
            element.textContent = prefix + currentValue.toFixed(decimals) + suffix;
            
            if (colorize) {
                element.classList.remove('positive', 'negative');
                element.classList.add(currentValue >= 0 ? 'positive' : 'negative');
            }

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    static formatCurrency(value, animate = true) {
        const formatted = new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(value);
        return formatted;
    }
}

// ===== THEME ANIMATOR =====
const ThemeAnimator = {
    current: localStorage.getItem('enliko_theme') || 'dark',

    init() {
        document.documentElement.setAttribute('data-theme', this.current);
        this.createToggleButton();
    },

    createToggleButton() {
        const existing = document.querySelector('.theme-toggle-btn');
        if (existing) return;

        const btn = document.createElement('button');
        btn.className = 'theme-toggle-btn';
        btn.innerHTML = this.current === 'dark' ? '🌙' : '☀️';
        btn.title = 'Toggle Theme (T)';
        btn.onclick = () => this.toggle();
        
        const header = document.querySelector('.header-right, .header-actions');
        if (header) header.prepend(btn);
    },

    toggle() {
        this.current = this.current === 'dark' ? 'light' : 'dark';
        localStorage.setItem('enliko_theme', this.current);
        
        // Animate transition
        document.body.style.transition = 'background-color 0.3s, color 0.3s';
        document.documentElement.setAttribute('data-theme', this.current);
        
        // Update button
        const btn = document.querySelector('.theme-toggle-btn');
        if (btn) {
            btn.innerHTML = this.current === 'dark' ? '🌙' : '☀️';
            btn.classList.add('theme-switching');
            setTimeout(() => btn.classList.remove('theme-switching'), 300);
        }

        SoundEffects.play('click');
        HapticFeedback.light();
    }
};

// ===== SKELETON LOADING =====
const SkeletonLoader = {
    create(type = 'card') {
        const templates = {
            card: `
                <div class="skeleton-card">
                    <div class="skeleton-line w-60"></div>
                    <div class="skeleton-line w-40"></div>
                    <div class="skeleton-line w-80"></div>
                </div>
            `,
            table: `
                <div class="skeleton-table">
                    ${Array(5).fill('<div class="skeleton-row"><div class="skeleton-cell"></div><div class="skeleton-cell"></div><div class="skeleton-cell"></div></div>').join('')}
                </div>
            `,
            position: `
                <div class="skeleton-position">
                    <div class="skeleton-header">
                        <div class="skeleton-line w-30"></div>
                        <div class="skeleton-badge"></div>
                    </div>
                    <div class="skeleton-stats">
                        <div class="skeleton-stat"></div>
                        <div class="skeleton-stat"></div>
                        <div class="skeleton-stat"></div>
                    </div>
                </div>
            `
        };
        
        const wrapper = document.createElement('div');
        wrapper.className = 'skeleton-wrapper';
        wrapper.innerHTML = templates[type] || templates.card;
        return wrapper;
    },

    show(container, type = 'card', count = 3) {
        container.innerHTML = '';
        for (let i = 0; i < count; i++) {
            container.appendChild(this.create(type));
        }
    },

    hide(container) {
        container.querySelectorAll('.skeleton-wrapper').forEach(el => el.remove());
    }
};

// ===== PRICE FLASH ANIMATION =====
const PriceFlash = {
    animate(element, newPrice, oldPrice) {
        if (!element) return;
        
        element.textContent = this.formatPrice(newPrice);
        
        if (newPrice > oldPrice) {
            element.classList.remove('flash-down');
            element.classList.add('flash-up');
        } else if (newPrice < oldPrice) {
            element.classList.remove('flash-up');
            element.classList.add('flash-down');
        }

        setTimeout(() => {
            element.classList.remove('flash-up', 'flash-down');
        }, 500);
    },

    formatPrice(price) {
        if (price >= 1000) return '$' + price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        if (price >= 1) return '$' + price.toFixed(4);
        return '$' + price.toFixed(6);
    }
};

// ===== TOAST NOTIFICATIONS (Enhanced) =====
const SuperToast = {
    container: null,

    init() {
        this.container = document.createElement('div');
        this.container.className = 'super-toast-container';
        document.body.appendChild(this.container);
    },

    show(message, type = 'info', duration = 4000) {
        if (!this.container) this.init();

        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️',
            trade: '📈',
            profit: '💰',
            loss: '📉'
        };

        const toast = document.createElement('div');
        toast.className = `super-toast ${type}`;
        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
        `;

        this.container.appendChild(toast);
        
        // Trigger animation
        requestAnimationFrame(() => toast.classList.add('show'));

        // Play sound based on type
        if (type === 'success' || type === 'profit') {
            SoundEffects.play('success');
            HapticFeedback.success();
        } else if (type === 'error' || type === 'loss') {
            SoundEffects.play('error');
            HapticFeedback.error();
        } else {
            SoundEffects.play('notification');
            HapticFeedback.light();
        }

        // Auto remove
        setTimeout(() => {
            toast.classList.add('hiding');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    profit(pnl, symbol) {
        this.show(`${symbol}: +$${pnl.toFixed(2)} profit! 🎉`, 'profit', 5000);
        window.Confetti?.celebrate(pnl);
    },

    loss(pnl, symbol) {
        this.show(`${symbol}: -$${Math.abs(pnl).toFixed(2)} loss`, 'loss', 4000);
    }
};

// ===== QUICK TRADE PANEL =====
class QuickTradePanel {
    constructor() {
        this.panel = null;
        this.symbol = 'BTCUSDT';
        this.leverage = 10;
        this.amount = 100;
    }

    init() {
        this.createPanel();
        this.bindEvents();
    }

    createPanel() {
        this.panel = document.createElement('div');
        this.panel.className = 'quick-trade-panel';
        this.panel.innerHTML = `
            <div class="quick-trade-header">
                <span class="quick-symbol">${this.symbol}</span>
                <span class="quick-price" id="quickPrice">$0.00</span>
            </div>
            <div class="quick-trade-inputs">
                <div class="quick-input-group">
                    <label>Amount ($)</label>
                    <input type="number" id="quickAmount" value="${this.amount}" min="10" step="10">
                </div>
                <div class="quick-input-group">
                    <label>Leverage</label>
                    <input type="range" id="quickLeverage" value="${this.leverage}" min="1" max="100">
                    <span id="quickLeverageValue">${this.leverage}x</span>
                </div>
            </div>
            <div class="quick-trade-buttons">
                <button class="quick-btn long" onclick="QuickTrade.executeTrade('long')">
                    <span class="btn-icon">📈</span>
                    <span>LONG</span>
                    <kbd>B</kbd>
                </button>
                <button class="quick-btn short" onclick="QuickTrade.executeTrade('short')">
                    <span class="btn-icon">📉</span>
                    <span>SHORT</span>
                    <kbd>S</kbd>
                </button>
            </div>
        `;
        
        const sidebar = document.querySelector('.sidebar-right, .trade-panel');
        if (sidebar) {
            sidebar.prepend(this.panel);
        }
    }

    bindEvents() {
        const leverageInput = this.panel?.querySelector('#quickLeverage');
        const leverageValue = this.panel?.querySelector('#quickLeverageValue');
        
        if (leverageInput && leverageValue) {
            leverageInput.addEventListener('input', (e) => {
                this.leverage = parseInt(e.target.value);
                leverageValue.textContent = `${this.leverage}x`;
                HapticFeedback.selection();
            });
        }
    }

    async executeTrade(side) {
        const amount = parseFloat(document.getElementById('quickAmount')?.value) || this.amount;
        
        HapticFeedback.medium();
        SoundEffects.play('trade');
        
        try {
            const response = await fetch('/api/trading/order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('enliko_token')}`
                },
                body: JSON.stringify({
                    symbol: this.symbol,
                    side: side === 'long' ? 'Buy' : 'Sell',
                    type: 'market',
                    size: amount / this.leverage,
                    leverage: this.leverage,
                    exchange: window.state?.exchange || 'bybit',
                    account_type: window.state?.accountType || 'demo'
                })
            });

            const result = await response.json();
            
            if (result.success) {
                SuperToast.show(`${side.toUpperCase()} order placed for ${this.symbol}`, 'trade');
            } else {
                SuperToast.show(result.error || 'Order failed', 'error');
            }
        } catch (e) {
            SuperToast.show('Failed to place order', 'error');
        }
    }
}

// ===== PERFORMANCE MONITOR =====
const PerformanceMonitor = {
    fps: 0,
    lastTime: performance.now(),
    frameCount: 0,

    init() {
        this.createDisplay();
        this.measure();
    },

    createDisplay() {
        if (localStorage.getItem('enliko_debug') !== 'true') return;
        
        const display = document.createElement('div');
        display.id = 'perf-monitor';
        display.style.cssText = `
            position: fixed;
            bottom: 10px;
            left: 10px;
            background: rgba(0,0,0,0.8);
            color: #0f0;
            font-family: monospace;
            font-size: 12px;
            padding: 5px 10px;
            border-radius: 4px;
            z-index: 99999;
        `;
        document.body.appendChild(display);
    },

    measure() {
        this.frameCount++;
        const now = performance.now();
        
        if (now - this.lastTime >= 1000) {
            this.fps = this.frameCount;
            this.frameCount = 0;
            this.lastTime = now;
            
            const display = document.getElementById('perf-monitor');
            if (display) {
                const memory = performance.memory?.usedJSHeapSize 
                    ? (performance.memory.usedJSHeapSize / 1048576).toFixed(1) + 'MB'
                    : 'N/A';
                display.textContent = `FPS: ${this.fps} | Memory: ${memory}`;
            }
        }
        
        requestAnimationFrame(() => this.measure());
    }
};

// ===== INITIALIZATION =====
const Confetti = new ConfettiCelebration();
const Shortcuts = new KeyboardShortcuts();
const QuickTrade = new QuickTradePanel();

document.addEventListener('DOMContentLoaded', () => {
    // Initialize all super features
    Shortcuts.init();
    ThemeAnimator.init();
    SuperToast.init();
    PerformanceMonitor.init();
    
    console.log('🚀 Enliko Super Features loaded!');
    console.log('Press ? for keyboard shortcuts');
});

// Export for global access
window.Confetti = Confetti;
window.SoundEffects = SoundEffects;
window.HapticFeedback = HapticFeedback;
window.Shortcuts = Shortcuts;
window.AnimatedCounter = AnimatedCounter;
window.ThemeAnimator = ThemeAnimator;
window.SkeletonLoader = SkeletonLoader;
window.PriceFlash = PriceFlash;
window.SuperToast = SuperToast;
window.QuickTrade = QuickTrade;
