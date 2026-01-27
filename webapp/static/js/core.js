/**
 * Enliko - Core Application Logic
 * Единый JS файл для базового функционала всех страниц
 * v3.19.0
 */

// ===== SECURITY: HTML SANITIZATION =====
// Simple HTML escape function to prevent XSS
function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
}

// Sanitize object for safe HTML rendering
function sanitizeForHtml(obj) {
    if (typeof obj === 'string') return escapeHtml(obj);
    if (typeof obj !== 'object' || obj === null) return obj;
    const result = Array.isArray(obj) ? [] : {};
    for (const key in obj) {
        if (typeof obj[key] === 'string') {
            result[key] = escapeHtml(obj[key]);
        } else if (typeof obj[key] === 'object') {
            result[key] = sanitizeForHtml(obj[key]);
        } else {
            result[key] = obj[key];
        }
    }
    return result;
}

// Global sanitize function
window.escapeHtml = escapeHtml;
window.sanitizeForHtml = sanitizeForHtml;

// ===== CONFIGURATION =====
const CONFIG = {
    API_BASE: '',
    STORAGE_KEYS: {
        TOKEN: 'auth_token',
        USER: 'user_data',
        THEME: 'enliko_theme',
        LANG: 'enliko_lang',
        ACCOUNT_TYPE: 'account_type',
        EXCHANGE: 'exchange_type'
    },
    DEFAULT_THEME: 'dark',
    DEFAULT_LANG: 'en'
};

// ===== TELEGRAM WEBAPP INTEGRATION =====
const TG = window.Telegram?.WebApp;
const IS_TELEGRAM = !!TG?.initData;

function initTelegram() {
    if (!TG) return;
    
    TG.ready();
    TG.expand();
    TG.enableClosingConfirmation();
    
    // Set theme based on Telegram
    if (TG.colorScheme) {
        document.documentElement.setAttribute('data-theme', TG.colorScheme);
    }
    
    // Back button handling
    TG.BackButton.onClick(() => {
        if (window.history.length > 1) {
            window.history.back();
        } else {
            window.location.href = '/terminal';
        }
    });
}

// ===== AUTH =====
function getAuthToken() {
    // Priority: localStorage > Telegram initData
    let token = localStorage.getItem(CONFIG.STORAGE_KEYS.TOKEN);
    
    if (!token && IS_TELEGRAM && TG.initData) {
        token = TG.initData;
    }
    
    // Fallback: URL params
    if (!token) {
        const urlParams = new URLSearchParams(window.location.search);
        token = urlParams.get('token') || urlParams.get('auth');
    }
    
    return token;
}

function setAuthToken(token) {
    localStorage.setItem(CONFIG.STORAGE_KEYS.TOKEN, token);
}

function clearAuth() {
    localStorage.removeItem(CONFIG.STORAGE_KEYS.TOKEN);
    localStorage.removeItem(CONFIG.STORAGE_KEYS.USER);
}

function isAuthenticated() {
    return !!getAuthToken();
}

// ===== API HELPERS =====
async function apiRequest(endpoint, options = {}) {
    const token = getAuthToken();
    
    const defaultHeaders = {
        'Content-Type': 'application/json'
    };
    
    if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
        defaultHeaders['X-Auth-Token'] = token;
    }
    
    // Add Telegram data if available
    if (IS_TELEGRAM && TG.initData) {
        defaultHeaders['X-Telegram-Init-Data'] = TG.initData;
    }
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}${endpoint}`, {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers
            }
        });
        
        if (response.status === 401) {
            clearAuth();
            window.location.href = '/auth/login';
            return null;
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

async function apiGet(endpoint) {
    return apiRequest(endpoint, { method: 'GET' });
}

async function apiPost(endpoint, body) {
    return apiRequest(endpoint, {
        method: 'POST',
        body: JSON.stringify(body)
    });
}

// ===== THEME MANAGEMENT =====
function getTheme() {
    return localStorage.getItem(CONFIG.STORAGE_KEYS.THEME) || CONFIG.DEFAULT_THEME;
}

function setTheme(theme) {
    localStorage.setItem(CONFIG.STORAGE_KEYS.THEME, theme);
    
    if (theme === 'system') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    } else {
        document.documentElement.setAttribute('data-theme', theme);
    }
    
    // Update icon if exists
    const icon = document.getElementById('themeIcon');
    if (icon) {
        icon.className = theme === 'light' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

function toggleTheme() {
    const current = getTheme();
    const next = current === 'dark' ? 'light' : 'dark';
    setTheme(next);
}

// ===== LANGUAGE MANAGEMENT =====
function getLang() {
    return localStorage.getItem(CONFIG.STORAGE_KEYS.LANG) || 
           navigator.language?.split('-')[0] || 
           CONFIG.DEFAULT_LANG;
}

function setLang(lang) {
    localStorage.setItem(CONFIG.STORAGE_KEYS.LANG, lang);
    document.documentElement.setAttribute('lang', lang);
    
    // Reload translations if i18n is loaded
    if (window.loadTranslations) {
        window.loadTranslations(lang);
    }
}

// ===== ACCOUNT TYPE MANAGEMENT =====
function getAccountType() {
    return localStorage.getItem(CONFIG.STORAGE_KEYS.ACCOUNT_TYPE) || 'demo';
}

function setAccountType(type) {
    localStorage.setItem(CONFIG.STORAGE_KEYS.ACCOUNT_TYPE, type);
    
    // Update UI
    document.querySelectorAll('.account-btn').forEach(btn => {
        btn.classList.toggle('active', btn.classList.contains(type));
    });
    
    // Dispatch event for other components
    window.dispatchEvent(new CustomEvent('accountTypeChanged', { detail: { type } }));
}

function getExchangeType() {
    return localStorage.getItem(CONFIG.STORAGE_KEYS.EXCHANGE) || 'bybit';
}

function setExchangeType(exchange) {
    localStorage.setItem(CONFIG.STORAGE_KEYS.EXCHANGE, exchange);
    window.dispatchEvent(new CustomEvent('exchangeChanged', { detail: { exchange } }));
}

// ===== TOAST NOTIFICATIONS =====
function showToast(message, type = 'info', duration = 3000) {
    // Remove existing toast
    const existing = document.querySelector('.toast-notification');
    if (existing) existing.remove();
    
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${getToastIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add styles if not present
    if (!document.querySelector('#toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            .toast-notification {
                position: fixed;
                bottom: 24px;
                right: 24px;
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
                background: var(--bg-card);
                border: 1px solid var(--border);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-lg);
                z-index: 9999;
                animation: slideIn 0.3s ease;
            }
            .toast-content { display: flex; align-items: center; gap: 8px; }
            .toast-close { background: none; border: none; color: var(--text-muted); cursor: pointer; }
            .toast-success { border-color: var(--green); }
            .toast-success i { color: var(--green); }
            .toast-error { border-color: var(--red); }
            .toast-error i { color: var(--red); }
            .toast-warning { border-color: var(--accent-gold); }
            .toast-warning i { color: var(--accent-gold); }
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(toast);
    
    if (duration > 0) {
        setTimeout(() => toast.remove(), duration);
    }
}

function getToastIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || icons.info;
}

// ===== FORMATTING HELPERS =====
function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined) return '-';
    return Number(num).toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

function formatCurrency(num, currency = 'USDT') {
    if (num === null || num === undefined) return '-';
    return `${formatNumber(num)} ${currency}`;
}

function formatPercent(num, showSign = true) {
    if (num === null || num === undefined) return '-';
    const formatted = formatNumber(num, 2);
    if (showSign && num > 0) return `+${formatted}%`;
    return `${formatted}%`;
}

function formatPnl(num) {
    if (num === null || num === undefined) return '-';
    const formatted = formatNumber(Math.abs(num), 2);
    const sign = num >= 0 ? '+' : '-';
    return `${sign}$${formatted}`;
}

function formatDate(dateStr, options = {}) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        ...options
    });
}

// ===== DOM HELPERS =====
function $(selector) {
    return document.querySelector(selector);
}

function $$(selector) {
    return document.querySelectorAll(selector);
}

function createElement(tag, attrs = {}, children = []) {
    const el = document.createElement(tag);
    Object.entries(attrs).forEach(([key, value]) => {
        if (key === 'className') el.className = value;
        else if (key === 'innerHTML') el.innerHTML = value;
        else if (key.startsWith('on')) el.addEventListener(key.slice(2).toLowerCase(), value);
        else el.setAttribute(key, value);
    });
    children.forEach(child => {
        if (typeof child === 'string') el.appendChild(document.createTextNode(child));
        else el.appendChild(child);
    });
    return el;
}

// ===== INITIALIZATION =====
function initApp() {
    // Initialize Telegram
    initTelegram();
    
    // Apply saved theme
    setTheme(getTheme());
    
    // Apply saved language
    document.documentElement.setAttribute('lang', getLang());
    
    // Show back button in Telegram if not on main page
    if (IS_TELEGRAM && window.location.pathname !== '/terminal') {
        TG.BackButton.show();
    }
    
    console.log('🚀 Enliko App Initialized');
}

// Auto-init on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

// Export for global access
window.Enliko = {
    CONFIG,
    IS_TELEGRAM,
    TG,
    // Auth
    getAuthToken,
    setAuthToken,
    clearAuth,
    isAuthenticated,
    // API
    apiRequest,
    apiGet,
    apiPost,
    // Theme/Lang
    getTheme,
    setTheme,
    toggleTheme,
    getLang,
    setLang,
    // Account
    getAccountType,
    setAccountType,
    getExchangeType,
    setExchangeType,
    // UI
    showToast,
    // Format
    formatNumber,
    formatCurrency,
    formatPercent,
    formatPnl,
    formatDate,
    // DOM
    $,
    $$,
    createElement
};
