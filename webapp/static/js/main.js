/**
 * Trading Bot WebApp - Main Application
 * Elite Graphite Edition
 */

// ═══════════════════════════════════════════════════════════════
// STATE MANAGEMENT
// ═══════════════════════════════════════════════════════════════
const AppState = {
    user: null,
    exchange: 'bybit',
    language: 'en',
    theme: 'dark',
    isAdmin: false,
    isLoading: true,
    positions: [],
    orders: [],
    settings: {}
};

// ═══════════════════════════════════════════════════════════════
// API CLIENT
// ═══════════════════════════════════════════════════════════════
const API = {
    baseUrl: '/api',
    token: null,

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (response.status === 401) {
                this.logout();
                return null;
            }

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            Toast.error(error.message);
            throw error;
        }
    },

    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },

    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    },

    loadToken() {
        this.token = localStorage.getItem('auth_token');
        return this.token;
    },

    logout() {
        this.token = null;
        localStorage.removeItem('auth_token');
        AppState.user = null;
        Router.navigate('/login');
    }
};

// ═══════════════════════════════════════════════════════════════
// TELEGRAM AUTH
// ═══════════════════════════════════════════════════════════════
const TelegramAuth = {
    async init() {
        // Check if opened from Telegram WebApp
        if (window.Telegram?.WebApp) {
            const tg = window.Telegram.WebApp;
            tg.ready();
            tg.expand();
            
            // Set theme colors from Telegram
            if (tg.themeParams) {
                document.documentElement.style.setProperty('--bg-primary', tg.themeParams.bg_color || '#0d0d0f');
                document.documentElement.style.setProperty('--text-primary', tg.themeParams.text_color || '#f1f1f4');
            }

            // Auto-login with Telegram data
            if (tg.initData) {
                await this.loginWithTelegram(tg.initData);
            }
        }
    },

    async loginWithTelegram(initData) {
        try {
            const response = await API.post('/auth/telegram', { init_data: initData });
            
            if (response.token) {
                API.setToken(response.token);
                AppState.user = response.user;
                AppState.isAdmin = response.user?.is_admin || false;
                
                Toast.success('Successfully logged in!');
                Router.navigate('/dashboard');
                return true;
            }
        } catch (error) {
            console.error('Telegram auth failed:', error);
            return false;
        }
    },

    // For desktop - show QR or login button
    showLoginWidget(container) {
        const botUsername = 'elcaro_bybit_bot'; // Your bot username
        const widget = document.createElement('div');
        widget.innerHTML = `
            <div class="login-card">
                <div class="login-logo">🤖</div>
                <h2 class="login-title">Trading Bot</h2>
                <p class="login-subtitle">Sign in with your Telegram account</p>
                <button class="telegram-login-btn" onclick="TelegramAuth.openTelegramLogin()">
                    <i class="fab fa-telegram"></i>
                    Continue with Telegram
                </button>
                <p style="margin-top: 24px; font-size: 0.875rem; color: var(--text-muted);">
                    Open this link in Telegram for auto-login
                </p>
            </div>
        `;
        container.appendChild(widget);
    },

    openTelegramLogin() {
        const botUsername = 'elcaro_bybit_bot';
        const callbackUrl = encodeURIComponent(window.location.origin + '/auth/callback');
        window.location.href = `https://t.me/${botUsername}?start=webapp_${callbackUrl}`;
    }
};

// ═══════════════════════════════════════════════════════════════
// ROUTER
// ═══════════════════════════════════════════════════════════════
const Router = {
    routes: {},
    currentRoute: null,

    register(path, handler) {
        this.routes[path] = handler;
    },

    async navigate(path) {
        // Check auth for protected routes
        if (path !== '/login' && !API.token) {
            return this.navigate('/login');
        }

        // Check admin for admin routes
        if (path.startsWith('/admin') && !AppState.isAdmin) {
            Toast.error('Access denied');
            return this.navigate('/dashboard');
        }

        this.currentRoute = path;
        window.history.pushState({}, '', path);
        
        const handler = this.routes[path] || this.routes['/404'];
        if (handler) {
            await handler();
        }
    },

    init() {
        window.addEventListener('popstate', () => {
            this.navigate(window.location.pathname);
        });

        // Handle initial route
        const path = window.location.pathname;
        this.navigate(path === '/' ? '/dashboard' : path);
    }
};

// ═══════════════════════════════════════════════════════════════
// TOAST NOTIFICATIONS
// ═══════════════════════════════════════════════════════════════
const Toast = {
    container: null,

    init() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        document.body.appendChild(this.container);
    },

    show(message, type = 'info', duration = 4000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()" style="background:none;border:none;color:var(--text-muted);cursor:pointer;">&times;</button>
        `;
        this.container.appendChild(toast);

        setTimeout(() => toast.remove(), duration);
    },

    success(message) { this.show(message, 'success'); },
    error(message) { this.show(message, 'error'); },
    warning(message) { this.show(message, 'warning'); },
    info(message) { this.show(message, 'info'); }
};

// ═══════════════════════════════════════════════════════════════
// COMPONENTS
// ═══════════════════════════════════════════════════════════════
const Components = {
    // Sidebar component
    sidebar() {
        const isAdmin = AppState.isAdmin;
        const exchange = AppState.exchange;
        
        return `
            <aside class="sidebar" id="sidebar">
                <div class="sidebar-header">
                    <div class="sidebar-logo">
                        <div style="width:40px;height:40px;background:var(--gradient-primary);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.5rem;">🤖</div>
                        <h1>TradingBot</h1>
                    </div>
                </div>
                
                <nav class="sidebar-nav">
                    <div class="nav-section">
                        <div class="nav-section-title">Trading</div>
                        <div class="nav-item ${Router.currentRoute === '/dashboard' ? 'active' : ''}" onclick="Router.navigate('/dashboard')">
                            <i class="fas fa-chart-line"></i>
                            <span>Dashboard</span>
                        </div>
                        <div class="nav-item ${Router.currentRoute === '/positions' ? 'active' : ''}" onclick="Router.navigate('/positions')">
                            <i class="fas fa-layer-group"></i>
                            <span>Positions</span>
                        </div>
                        <div class="nav-item ${Router.currentRoute === '/orders' ? 'active' : ''}" onclick="Router.navigate('/orders')">
                            <i class="fas fa-list-alt"></i>
                            <span>Orders</span>
                        </div>
                        <div class="nav-item ${Router.currentRoute === '/history' ? 'active' : ''}" onclick="Router.navigate('/history')">
                            <i class="fas fa-history"></i>
                            <span>History</span>
                        </div>
                    </div>
                    
                    <div class="nav-section">
                        <div class="nav-section-title">Settings</div>
                        <div class="nav-item ${Router.currentRoute === '/settings' ? 'active' : ''}" onclick="Router.navigate('/settings')">
                            <i class="fas fa-cog"></i>
                            <span>Bot Settings</span>
                        </div>
                        <div class="nav-item ${Router.currentRoute === '/api-keys' ? 'active' : ''}" onclick="Router.navigate('/api-keys')">
                            <i class="fas fa-key"></i>
                            <span>API Keys</span>
                        </div>
                        <div class="nav-item ${Router.currentRoute === '/strategies' ? 'active' : ''}" onclick="Router.navigate('/strategies')">
                            <i class="fas fa-robot"></i>
                            <span>Strategies</span>
                        </div>
                    </div>
                    
                    ${isAdmin ? `
                    <div class="nav-section">
                        <div class="nav-section-title">Admin</div>
                        <div class="nav-item ${Router.currentRoute === '/admin/users' ? 'active' : ''}" onclick="Router.navigate('/admin/users')">
                            <i class="fas fa-users"></i>
                            <span>Users</span>
                        </div>
                        <div class="nav-item ${Router.currentRoute === '/admin/licenses' ? 'active' : ''}" onclick="Router.navigate('/admin/licenses')">
                            <i class="fas fa-id-card"></i>
                            <span>Licenses</span>
                        </div>
                        <div class="nav-item ${Router.currentRoute === '/admin/stats' ? 'active' : ''}" onclick="Router.navigate('/admin/stats')">
                            <i class="fas fa-chart-bar"></i>
                            <span>Statistics</span>
                        </div>
                    </div>
                    ` : ''}
                </nav>
            </aside>
        `;
    },

    // Header component
    header() {
        const user = AppState.user || {};
        const exchange = AppState.exchange;
        
        return `
            <header class="header">
                <div class="header-left">
                    <button class="btn btn-secondary btn-sm" onclick="toggleSidebar()" style="display:none;" id="menu-toggle">
                        <i class="fas fa-bars"></i>
                    </button>
                    
                    <div class="exchange-switcher">
                        <button class="exchange-btn bybit ${exchange === 'bybit' ? 'active' : ''}" onclick="switchExchange('bybit')">
                            🟠 Bybit
                        </button>
                        <button class="exchange-btn hyperliquid ${exchange === 'hyperliquid' ? 'active' : ''}" onclick="switchExchange('hyperliquid')">
                            🔷 HyperLiquid
                        </button>
                    </div>
                </div>
                
                <div class="header-right">
                    <button class="btn btn-secondary btn-sm" onclick="Router.navigate('/settings')">
                        <i class="fas fa-cog"></i>
                    </button>
                    
                    <div class="user-menu" onclick="toggleUserMenu()">
                        <div class="user-avatar">${(user.first_name || 'U')[0]}</div>
                        <div class="user-info">
                            <span class="user-name">${user.first_name || 'User'}</span>
                            <span class="user-status">${user.is_premium ? '💎 Premium' : 'Free'}</span>
                        </div>
                    </div>
                </div>
            </header>
        `;
    },

    // Stats cards
    statsGrid(stats) {
        return `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon primary"><i class="fas fa-wallet"></i></div>
                    <div class="stat-value">$${formatNumber(stats.balance || 0)}</div>
                    <div class="stat-label">Total Balance</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon ${stats.pnl >= 0 ? 'success' : 'danger'}">
                        <i class="fas fa-${stats.pnl >= 0 ? 'arrow-up' : 'arrow-down'}"></i>
                    </div>
                    <div class="stat-value">${stats.pnl >= 0 ? '+' : ''}$${formatNumber(stats.pnl || 0)}</div>
                    <div class="stat-label">Unrealized PnL</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon info"><i class="fas fa-layer-group"></i></div>
                    <div class="stat-value">${stats.positions || 0}</div>
                    <div class="stat-label">Open Positions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon warning"><i class="fas fa-clock"></i></div>
                    <div class="stat-value">${stats.orders || 0}</div>
                    <div class="stat-label">Pending Orders</div>
                </div>
            </div>
        `;
    },

    // Positions table
    positionsTable(positions) {
        if (!positions || positions.length === 0) {
            return `
                <div class="card">
                    <div class="card-body" style="text-align:center;padding:48px;">
                        <i class="fas fa-inbox" style="font-size:3rem;color:var(--text-muted);margin-bottom:16px;"></i>
                        <p style="color:var(--text-muted);">No open positions</p>
                    </div>
                </div>
            `;
        }

        return `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Open Positions</h3>
                    <button class="btn btn-danger btn-sm" onclick="closeAllPositions()">
                        <i class="fas fa-times"></i> Close All
                    </button>
                </div>
                <div class="table-container">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Side</th>
                                <th>Size</th>
                                <th>Entry Price</th>
                                <th>Mark Price</th>
                                <th>PnL</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${positions.map(pos => `
                                <tr>
                                    <td><strong>${pos.symbol}</strong></td>
                                    <td>
                                        <span class="position-side ${pos.side === 'Buy' ? 'long' : 'short'}">
                                            ${pos.side === 'Buy' ? '🟢 LONG' : '🔴 SHORT'}
                                        </span>
                                    </td>
                                    <td>${pos.size}</td>
                                    <td>$${formatNumber(pos.entry_price)}</td>
                                    <td>$${formatNumber(pos.mark_price)}</td>
                                    <td class="position-pnl ${pos.pnl >= 0 ? 'positive' : 'negative'}">
                                        ${pos.pnl >= 0 ? '+' : ''}$${formatNumber(pos.pnl)}
                                    </td>
                                    <td>
                                        <button class="btn btn-secondary btn-sm" onclick="editPosition('${pos.symbol}')">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <button class="btn btn-danger btn-sm" onclick="closePosition('${pos.symbol}')">
                                            <i class="fas fa-times"></i>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    },

    // Settings form
    settingsForm(settings, exchange) {
        const isHL = exchange === 'hyperliquid';
        
        return `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">${isHL ? '🔷 HyperLiquid' : '🟠 Bybit'} Settings</h3>
                </div>
                <div class="card-body">
                    <div class="settings-section">
                        <h4 class="settings-section-title">Trading Parameters</h4>
                        
                        <div class="settings-row">
                            <div class="settings-label">
                                <span>Trade Size (%)</span>
                                <small>Percentage of balance per trade</small>
                            </div>
                            <input type="number" class="form-input" style="width:120px;" 
                                value="${settings.percent || 5}" 
                                onchange="updateSetting('percent', this.value)">
                        </div>
                        
                        <div class="settings-row">
                            <div class="settings-label">
                                <span>Leverage</span>
                                <small>Default leverage for trades</small>
                            </div>
                            <input type="number" class="form-input" style="width:120px;" 
                                value="${settings.leverage || 10}" 
                                onchange="updateSetting('leverage', this.value)">
                        </div>
                        
                        <div class="settings-row">
                            <div class="settings-label">
                                <span>Take Profit (%)</span>
                                <small>Default TP percentage</small>
                            </div>
                            <input type="number" class="form-input" style="width:120px;" 
                                value="${settings.tp_percent || 2}" step="0.1"
                                onchange="updateSetting('tp_percent', this.value)">
                        </div>
                        
                        <div class="settings-row">
                            <div class="settings-label">
                                <span>Stop Loss (%)</span>
                                <small>Default SL percentage</small>
                            </div>
                            <input type="number" class="form-input" style="width:120px;" 
                                value="${settings.sl_percent || 1}" step="0.1"
                                onchange="updateSetting('sl_percent', this.value)">
                        </div>
                    </div>
                    
                    ${!isHL ? `
                    <div class="settings-section">
                        <h4 class="settings-section-title">Strategies</h4>
                        
                        <div class="settings-row">
                            <div class="settings-label">
                                <span>Scryptomera</span>
                                <small>Enable Scryptomera signals</small>
                            </div>
                            <label class="toggle">
                                <input type="checkbox" ${settings.enable_scryptomera ? 'checked' : ''} 
                                    onchange="updateSetting('enable_scryptomera', this.checked)">
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                        
                        <div class="settings-row">
                            <div class="settings-label">
                                <span>Elcaro</span>
                                <small>Enable Elcaro strategy</small>
                            </div>
                            <label class="toggle">
                                <input type="checkbox" ${settings.enable_elcaro ? 'checked' : ''} 
                                    onchange="updateSetting('enable_elcaro', this.checked)">
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                        
                        <div class="settings-row">
                            <div class="settings-label">
                                <span>Wyckoff</span>
                                <small>Enable Wyckoff analysis</small>
                            </div>
                            <label class="toggle">
                                <input type="checkbox" ${settings.enable_wyckoff ? 'checked' : ''} 
                                    onchange="updateSetting('enable_wyckoff', this.checked)">
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                        
                        <div class="settings-row">
                            <div class="settings-label">
                                <span>Scalper</span>
                                <small>Enable scalping mode</small>
                            </div>
                            <label class="toggle">
                                <input type="checkbox" ${settings.enable_scalper ? 'checked' : ''} 
                                    onchange="updateSetting('enable_scalper', this.checked)">
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                    </div>
                    ` : ''}
                </div>
                <div class="card-footer">
                    <button class="btn btn-primary" onclick="saveSettings()">
                        <i class="fas fa-save"></i> Save Settings
                    </button>
                </div>
            </div>
        `;
    }
};

// ═══════════════════════════════════════════════════════════════
// PAGES
// ═══════════════════════════════════════════════════════════════
const Pages = {
    async login() {
        document.getElementById('app').innerHTML = `
            <div class="login-container">
                <div class="login-card">
                    <div class="login-logo">🤖</div>
                    <h2 class="login-title">Trading Bot</h2>
                    <p class="login-subtitle">Sign in to manage your trading bot</p>
                    <button class="telegram-login-btn" onclick="TelegramAuth.openTelegramLogin()">
                        <i class="fab fa-telegram"></i>
                        Continue with Telegram
                    </button>
                </div>
            </div>
        `;
    },

    async dashboard() {
        showLoading();
        
        try {
            const [balance, positions, orders] = await Promise.all([
                API.get(`/trading/balance?exchange=${AppState.exchange}`),
                API.get(`/trading/positions?exchange=${AppState.exchange}`),
                API.get(`/trading/orders?exchange=${AppState.exchange}`)
            ]);

            const stats = {
                balance: balance?.equity || 0,
                pnl: balance?.unrealized_pnl || 0,
                positions: positions?.length || 0,
                orders: orders?.length || 0
            };

            AppState.positions = positions || [];
            AppState.orders = orders || [];

            renderLayout(`
                <div class="page-content fade-in">
                    <div class="page-header">
                        <h1 class="page-title">Dashboard</h1>
                        <p class="page-subtitle">Overview of your trading activity</p>
                    </div>
                    
                    ${Components.statsGrid(stats)}
                    ${Components.positionsTable(positions)}
                </div>
            `);
        } catch (error) {
            renderLayout(`
                <div class="page-content">
                    <div class="card">
                        <div class="card-body" style="text-align:center;padding:48px;">
                            <i class="fas fa-exclamation-triangle" style="font-size:3rem;color:var(--accent-warning);margin-bottom:16px;"></i>
                            <h3>Failed to load dashboard</h3>
                            <p style="color:var(--text-muted);">${error.message}</p>
                            <button class="btn btn-primary" onclick="Router.navigate('/dashboard')" style="margin-top:16px;">
                                <i class="fas fa-redo"></i> Retry
                            </button>
                        </div>
                    </div>
                </div>
            `);
        }
        
        hideLoading();
    },

    async positions() {
        showLoading();
        
        try {
            const positions = await API.get(`/trading/positions?exchange=${AppState.exchange}`);
            AppState.positions = positions || [];

            renderLayout(`
                <div class="page-content fade-in">
                    <div class="page-header">
                        <h1 class="page-title">Positions</h1>
                        <p class="page-subtitle">Manage your open positions</p>
                    </div>
                    ${Components.positionsTable(positions)}
                </div>
            `);
        } catch (error) {
            Toast.error('Failed to load positions');
        }
        
        hideLoading();
    },

    async settings() {
        showLoading();
        
        try {
            const settings = await API.get(`/users/settings?exchange=${AppState.exchange}`);
            AppState.settings = settings || {};

            renderLayout(`
                <div class="page-content fade-in">
                    <div class="page-header">
                        <h1 class="page-title">Settings</h1>
                        <p class="page-subtitle">Configure your trading bot</p>
                    </div>
                    
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">
                        ${Components.settingsForm(settings, AppState.exchange)}
                        
                        <div class="card">
                            <div class="card-header">
                                <h3 class="card-title">🌐 Language</h3>
                            </div>
                            <div class="card-body">
                                <div class="language-grid">
                                    ${['en', 'ru', 'uk', 'de', 'fr', 'es', 'it', 'pl', 'zh', 'ja', 'ar', 'he', 'cs', 'lt', 'sq'].map(lang => `
                                        <div class="language-option ${AppState.language === lang ? 'active' : ''}" 
                                            onclick="changeLanguage('${lang}')">
                                            <div class="language-flag">${getLanguageFlag(lang)}</div>
                                            <div>${getLanguageName(lang)}</div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `);
        } catch (error) {
            Toast.error('Failed to load settings');
        }
        
        hideLoading();
    },

    async adminUsers() {
        if (!AppState.isAdmin) {
            return Router.navigate('/dashboard');
        }
        
        showLoading();
        
        try {
            const users = await API.get('/admin/users');

            renderLayout(`
                <div class="page-content fade-in">
                    <div class="page-header">
                        <h1 class="page-title">👥 Users Management</h1>
                        <p class="page-subtitle">Manage bot users and permissions</p>
                    </div>
                    
                    <div class="admin-stats">
                        <div class="stat-card">
                            <div class="stat-icon primary"><i class="fas fa-users"></i></div>
                            <div class="stat-value">${users?.total || 0}</div>
                            <div class="stat-label">Total Users</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon success"><i class="fas fa-check-circle"></i></div>
                            <div class="stat-value">${users?.active || 0}</div>
                            <div class="stat-label">Active</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon warning"><i class="fas fa-crown"></i></div>
                            <div class="stat-value">${users?.premium || 0}</div>
                            <div class="stat-label">Premium</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon danger"><i class="fas fa-ban"></i></div>
                            <div class="stat-value">${users?.banned || 0}</div>
                            <div class="stat-label">Banned</div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">All Users</h3>
                            <input type="text" class="form-input" placeholder="Search users..." 
                                style="width:300px;" onkeyup="searchUsers(this.value)">
                        </div>
                        <div class="table-container">
                            <table class="table" id="users-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>User</th>
                                        <th>Status</th>
                                        <th>License</th>
                                        <th>Exchange</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${(users?.list || []).map(user => `
                                        <tr>
                                            <td><code>${user.user_id}</code></td>
                                            <td>
                                                <strong>${user.first_name || 'Unknown'}</strong>
                                                ${user.username ? `<br><small>@${user.username}</small>` : ''}
                                            </td>
                                            <td>
                                                ${user.is_banned ? '<span class="badge badge-danger">Banned</span>' : 
                                                  user.is_allowed ? '<span class="badge badge-success">Active</span>' : 
                                                  '<span class="badge badge-warning">Pending</span>'}
                                            </td>
                                            <td>
                                                ${user.license_type === 'premium' ? '<span class="badge license-badge premium">💎 Premium</span>' :
                                                  user.license_type === 'trial' ? '<span class="badge license-badge trial">⏳ Trial</span>' :
                                                  '<span class="badge badge-secondary">Free</span>'}
                                            </td>
                                            <td>${user.exchange_type === 'hyperliquid' ? '🔷 HL' : '🟠 Bybit'}</td>
                                            <td class="user-table-actions">
                                                <button class="btn btn-sm btn-secondary" onclick="viewUser(${user.user_id})">
                                                    <i class="fas fa-eye"></i>
                                                </button>
                                                ${user.is_banned ? 
                                                    `<button class="btn btn-sm btn-success" onclick="unbanUser(${user.user_id})"><i class="fas fa-check"></i></button>` :
                                                    `<button class="btn btn-sm btn-danger" onclick="banUser(${user.user_id})"><i class="fas fa-ban"></i></button>`
                                                }
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `);
        } catch (error) {
            Toast.error('Failed to load users');
        }
        
        hideLoading();
    },

    async adminLicenses() {
        if (!AppState.isAdmin) {
            return Router.navigate('/dashboard');
        }
        
        showLoading();
        
        try {
            const licenses = await API.get('/admin/licenses');

            renderLayout(`
                <div class="page-content fade-in">
                    <div class="page-header" style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <h1 class="page-title">🔑 Licenses</h1>
                            <p class="page-subtitle">Manage premium licenses</p>
                        </div>
                        <button class="btn btn-primary" onclick="showCreateLicenseModal()">
                            <i class="fas fa-plus"></i> Create License
                        </button>
                    </div>
                    
                    <div class="card">
                        <div class="table-container">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>License Key</th>
                                        <th>Type</th>
                                        <th>User</th>
                                        <th>Created</th>
                                        <th>Expires</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${(licenses?.list || []).map(lic => `
                                        <tr>
                                            <td><code>${lic.key}</code></td>
                                            <td><span class="badge badge-primary">${lic.type}</span></td>
                                            <td>${lic.user_id || '<span style="color:var(--text-muted)">Not used</span>'}</td>
                                            <td>${formatDate(lic.created_at)}</td>
                                            <td>${formatDate(lic.expires_at)}</td>
                                            <td>
                                                ${lic.is_active ? '<span class="badge badge-success">Active</span>' : 
                                                  '<span class="badge badge-danger">Expired</span>'}
                                            </td>
                                            <td>
                                                <button class="btn btn-sm btn-danger" onclick="revokeLicense('${lic.key}')">
                                                    <i class="fas fa-trash"></i>
                                                </button>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `);
        } catch (error) {
            Toast.error('Failed to load licenses');
        }
        
        hideLoading();
    }
};

// ═══════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════
function formatNumber(num) {
    return new Intl.NumberFormat('en-US', { 
        minimumFractionDigits: 2, 
        maximumFractionDigits: 2 
    }).format(num);
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString();
}

function getLanguageFlag(lang) {
    const flags = {
        en: '🇬🇧', ru: '🇷🇺', uk: '🇺🇦', de: '🇩🇪', fr: '🇫🇷',
        es: '🇪🇸', it: '🇮🇹', pl: '🇵🇱', zh: '🇨🇳', ja: '🇯🇵',
        ar: '🇸🇦', he: '🇮🇱', cs: '🇨🇿', lt: '🇱🇹', sq: '🇦🇱'
    };
    return flags[lang] || '🌐';
}

function getLanguageName(lang) {
    const names = {
        en: 'English', ru: 'Русский', uk: 'Українська', de: 'Deutsch', fr: 'Français',
        es: 'Español', it: 'Italiano', pl: 'Polski', zh: '中文', ja: '日本語',
        ar: 'العربية', he: 'עברית', cs: 'Čeština', lt: 'Lietuvių', sq: 'Shqip'
    };
    return names[lang] || lang;
}

function renderLayout(content) {
    document.getElementById('app').innerHTML = `
        <div class="app-layout">
            ${Components.sidebar()}
            <div class="main-content">
                ${Components.header()}
                ${content}
            </div>
        </div>
    `;
}

function showLoading() {
    const loader = document.getElementById('loading');
    if (loader) loader.style.display = 'flex';
}

function hideLoading() {
    const loader = document.getElementById('loading');
    if (loader) loader.style.display = 'none';
}

function toggleSidebar() {
    document.getElementById('sidebar')?.classList.toggle('open');
}

async function switchExchange(exchange) {
    AppState.exchange = exchange;
    await API.post('/users/exchange', { exchange });
    Router.navigate(Router.currentRoute);
}

async function updateSetting(key, value) {
    AppState.settings[key] = value;
}

async function saveSettings() {
    try {
        await API.put('/users/settings', {
            exchange: AppState.exchange,
            settings: AppState.settings
        });
        Toast.success('Settings saved!');
    } catch (error) {
        Toast.error('Failed to save settings');
    }
}

async function changeLanguage(lang) {
    AppState.language = lang;
    await API.post('/users/language', { language: lang });
    Router.navigate(Router.currentRoute);
}

async function closePosition(symbol) {
    if (!confirm(`Close position ${symbol}?`)) return;
    
    try {
        await API.post('/trading/close', { symbol, exchange: AppState.exchange });
        Toast.success('Position closed');
        Router.navigate(Router.currentRoute);
    } catch (error) {
        Toast.error('Failed to close position');
    }
}

async function closeAllPositions() {
    if (!confirm('Close ALL positions?')) return;
    
    try {
        await API.post('/trading/close-all', { exchange: AppState.exchange });
        Toast.success('All positions closed');
        Router.navigate(Router.currentRoute);
    } catch (error) {
        Toast.error('Failed to close positions');
    }
}

async function banUser(userId) {
    if (!confirm(`Ban user ${userId}?`)) return;
    
    try {
        await API.post(`/admin/users/${userId}/ban`);
        Toast.success('User banned');
        Router.navigate('/admin/users');
    } catch (error) {
        Toast.error('Failed to ban user');
    }
}

async function unbanUser(userId) {
    try {
        await API.post(`/admin/users/${userId}/unban`);
        Toast.success('User unbanned');
        Router.navigate('/admin/users');
    } catch (error) {
        Toast.error('Failed to unban user');
    }
}

// ═══════════════════════════════════════════════════════════════
// TERMINAL INTEGRATION
// ═══════════════════════════════════════════════════════════════
const TerminalPage = {
    terminal: null,
    stats: null,
    backtest: null,
    aiAgent: null,

    async init() {
        // Initialize terminal components if on terminal page
        if (typeof TradingTerminal !== 'undefined' && !this.terminal) {
            this.terminal = new TradingTerminal('chart-container');
        }
        if (typeof StatsDashboard !== 'undefined' && !this.stats) {
            this.stats = new StatsDashboard();
        }
        if (typeof BacktestEngine !== 'undefined' && !this.backtest) {
            this.backtest = new BacktestEngine();
        }
        if (typeof AIAgent !== 'undefined' && !this.aiAgent) {
            this.aiAgent = new AIAgent();
        }
    },

    async show(section = 'terminal') {
        await this.init();
        
        // Hide all sections
        document.querySelectorAll('.terminal-section').forEach(el => {
            el.classList.add('hidden');
        });
        
        // Show requested section
        const sectionEl = document.getElementById(`section-${section}`);
        if (sectionEl) {
            sectionEl.classList.remove('hidden');
        }
        
        // Update sidebar active state
        document.querySelectorAll('.sidebar-nav .nav-item').forEach(el => {
            el.classList.remove('active');
        });
        const navItem = document.querySelector(`[data-section="${section}"]`);
        if (navItem) {
            navItem.classList.add('active');
        }
        
        // Initialize specific section
        switch(section) {
            case 'terminal':
                if (this.terminal) {
                    this.terminal.loadChart(AppState.currentSymbol || 'BTCUSDT');
                }
                break;
            case 'statistics':
                if (this.stats) {
                    this.stats.loadStats();
                }
                break;
            case 'backtest':
                // Already initialized
                break;
            case 'ai-agent':
                if (this.aiAgent) {
                    this.aiAgent.loadHistory();
                }
                break;
        }
    }
};

// Global function to navigate terminal sections
function navigateTerminal(section) {
    TerminalPage.show(section);
}

// ═══════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', async () => {
    // Init toast system
    Toast.init();
    
    // Load saved token
    API.loadToken();
    
    // Try Telegram auto-login
    await TelegramAuth.init();
    
    // If we have a token, fetch user info
    if (API.token) {
        try {
            const user = await API.get('/auth/me');
            AppState.user = user;
            AppState.isAdmin = user?.is_admin || false;
            AppState.exchange = user?.exchange_type || 'bybit';
            AppState.language = user?.language || 'en';
        } catch (error) {
            API.logout();
        }
    }
    
    // Register routes
    Router.register('/login', Pages.login);
    Router.register('/dashboard', Pages.dashboard);
    Router.register('/positions', Pages.positions);
    Router.register('/settings', Pages.settings);
    Router.register('/admin/users', Pages.adminUsers);
    Router.register('/admin/licenses', Pages.adminLicenses);
    Router.register('/terminal', () => TerminalPage.show('terminal'));
    Router.register('/terminal/trade', () => TerminalPage.show('terminal'));
    Router.register('/terminal/history', () => TerminalPage.show('history'));
    Router.register('/terminal/backtest', () => TerminalPage.show('backtest'));
    Router.register('/terminal/statistics', () => TerminalPage.show('statistics'));
    Router.register('/terminal/ai', () => TerminalPage.show('ai-agent'));
    Router.register('/terminal/settings', () => TerminalPage.show('settings'));
    Router.register('/terminal/admin', () => TerminalPage.show('admin'));
    Router.register('/404', () => {
        renderLayout('<div class="page-content"><h1>404 - Not Found</h1></div>');
    });
    
    // Init router
    Router.init();
    
    // Check if on terminal page and init terminal components
    if (window.location.pathname.startsWith('/terminal')) {
        await TerminalPage.init();
        const section = window.location.pathname.split('/').pop() || 'terminal';
        TerminalPage.show(section === 'terminal' ? 'terminal' : section);
    }
    
    hideLoading();
});
