/**
 * Real-time Market Data WebSocket Client
 * Based on scan/static/js/screener.js architecture
 * 
 * Usage:
 *   const client = new RealtimeClient('bybit');
 *   client.on('data', (data) => console.log(data));
 *   client.connect();
 */

class RealtimeClient {
    constructor(exchange = 'bybit', symbols = null) {
        this.exchange = exchange;
        this.symbols = symbols;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000;
        this.pingInterval = null;
        this.isConnected = false;
        this.listeners = {
            'data': [],
            'connected': [],
            'disconnected': [],
            'error': []
        };
        
        this.data = {}; // In-memory data store
    }
    
    /**
     * Register event listener
     * @param {string} event - Event name: 'data', 'connected', 'disconnected', 'error'
     * @param {function} callback - Callback function
     */
    on(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event].push(callback);
        }
    }
    
    /**
     * Emit event to all listeners
     */
    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(cb => cb(data));
        }
    }
    
    /**
     * Connect to WebSocket
     */
    connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            console.log('[RealtimeClient] Already connected');
            return;
        }
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        let url = `${protocol}//${host}/ws/realtime/${this.exchange}`;
        
        if (this.symbols && this.symbols.length > 0) {
            url += `?symbols=${this.symbols.join(',')}`;
        }
        
        console.log(`[RealtimeClient] Connecting to ${url}`);
        
        try {
            this.ws = new WebSocket(url);
            
            this.ws.onopen = () => {
                console.log(`[RealtimeClient] ✅ Connected to ${this.exchange}`);
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.startPingInterval();
                this.emit('connected', { exchange: this.exchange });
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                } catch (e) {
                    console.error('[RealtimeClient] Failed to parse message:', e);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error(`[RealtimeClient] WebSocket error:`, error);
                this.emit('error', error);
            };
            
            this.ws.onclose = (event) => {
                console.log(`[RealtimeClient] Disconnected (code: ${event.code})`);
                this.isConnected = false;
                this.stopPingInterval();
                this.emit('disconnected', { code: event.code });
                
                // Attempt reconnection
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    const delay = this.reconnectDelay * this.reconnectAttempts;
                    console.log(`[RealtimeClient] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
                    setTimeout(() => this.connect(), delay);
                }
            };
            
        } catch (error) {
            console.error('[RealtimeClient] Failed to create WebSocket:', error);
            this.emit('error', error);
        }
    }
    
    /**
     * Handle incoming WebSocket message
     */
    handleMessage(message) {
        const { type, data, exchange, timestamp } = message;
        
        switch (type) {
            case 'initial_data':
                console.log(`[RealtimeClient] Received initial data: ${data.length} symbols`);
                // Store data
                data.forEach(item => {
                    this.data[item.symbol] = item;
                });
                this.emit('data', { type: 'initial', data: this.data, timestamp });
                break;
                
            case 'market_data':
                // Update data
                data.forEach(item => {
                    this.data[item.symbol] = item;
                });
                this.emit('data', { type: 'update', data: this.data, timestamp });
                break;
                
            case 'pong':
                // Server response to ping
                break;
                
            case 'ping':
                // Server initiated ping
                this.sendPong();
                break;
                
            default:
                console.log('[RealtimeClient] Unknown message type:', type);
        }
    }
    
    /**
     * Send ping to server
     */
    sendPing() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'ping' }));
        }
    }
    
    /**
     * Send pong to server
     */
    sendPong() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'pong' }));
        }
    }
    
    /**
     * Start ping interval to keep connection alive
     */
    startPingInterval() {
        this.stopPingInterval();
        this.pingInterval = setInterval(() => {
            this.sendPing();
        }, 30000); // Ping every 30 seconds
    }
    
    /**
     * Stop ping interval
     */
    stopPingInterval() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
    }
    
    /**
     * Disconnect from WebSocket
     */
    disconnect() {
        this.stopPingInterval();
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
    }
    
    /**
     * Get current data for a symbol
     */
    getSymbol(symbol) {
        return this.data[symbol] || null;
    }
    
    /**
     * Get all current data
     */
    getAllData() {
        return this.data;
    }
    
    /**
     * Get sorted data by field
     */
    getSortedData(field = 'price', ascending = false) {
        const arr = Object.values(this.data);
        arr.sort((a, b) => {
            const aVal = a[field] || 0;
            const bVal = b[field] || 0;
            return ascending ? aVal - bVal : bVal - aVal;
        });
        return arr;
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RealtimeClient;
}

// Global namespace
window.RealtimeClient = RealtimeClient;
