// Main application JavaScript

// Global app state
function app() {
    return {
        isLoggedIn: !!localStorage.getItem('enliko_token'),
        isAdmin: false,
        user: null,

        async init() {
            if (this.isLoggedIn) {
                await this.checkAuth();
            }
        },

        async checkAuth() {
            try {
                const res = await fetch('/api/auth/me', {
                    headers: {
                        'Authorization': 'Bearer ' + localStorage.getItem('enliko_token')
                    }
                });
                
                if (res.ok) {
                    this.user = await res.json();
                    this.isAdmin = this.user.is_admin;
                } else {
                    this.logout();
                }
            } catch (e) {
                console.error('Auth check failed:', e);
            }
        },

        logout() {
            localStorage.removeItem('enliko_token');
            this.isLoggedIn = false;
            this.user = null;
            window.location.href = '/';
        }
    };
}

// Toast notification system
const Toast = {
    show(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s ease-out reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },
    
    success(message) {
        this.show(message, 'success');
    },
    
    error(message) {
        this.show(message, 'error');
    }
};

// API helper
async function api(url, options = {}) {
    const token = localStorage.getItem('enliko_token');
    
    const res = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': 'Bearer ' + token }),
            ...options.headers
        }
    });
    
    if (res.status === 401) {
        localStorage.removeItem('enliko_token');
        window.location.href = '/login';
        throw new Error('Unauthorized');
    }
    
    const data = await res.json();
    
    if (!res.ok) {
        throw new Error(data.detail || 'API Error');
    }
    
    return data;
}

// Utility functions
function formatMoney(value) {
    return '$' + (value || 0).toLocaleString('en-US', { 
        minimumFractionDigits: 2,
        maximumFractionDigits: 2 
    });
}

function formatPnl(value) {
    const sign = value >= 0 ? '+' : '';
    return sign + formatMoney(value);
}

function formatPercent(value) {
    const sign = value >= 0 ? '+' : '';
    return sign + (value || 0).toFixed(2) + '%';
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString();
}

// WebSocket connection for real-time updates
class WSConnection {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.handlers = {};
        this.reconnectAttempts = 0;
    }
    
    connect() {
        const token = localStorage.getItem('enliko_token');
        this.ws = new WebSocket(`${this.url}?token=${token}`);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const handler = this.handlers[data.type];
            if (handler) handler(data.payload);
        };
        
        this.ws.onclose = () => {
            if (this.reconnectAttempts < 5) {
                setTimeout(() => {
                    this.reconnectAttempts++;
                    this.connect();
                }, 2000 * this.reconnectAttempts);
            }
        };
    }
    
    on(event, handler) {
        this.handlers[event] = handler;
    }
    
    send(type, payload) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type, payload }));
        }
    }
}
