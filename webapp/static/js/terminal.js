/**
 * Elite Trading Terminal
 * Full-featured trading terminal with TradingView charts, AI analysis, and backtesting
 */

class TradingTerminal {
    constructor() {
        this.currentExchange = 'bybit';
        this.currentSymbol = 'BTCUSDT';
        this.currentTimeframe = '1h';
        this.positions = [];
        this.orders = [];
        this.trades = [];
        this.strategies = [];
        this.chart = null;
        this.ws = null;
        this.priceData = {};
    }

    async init() {
        await this.loadUserData();
        this.initTradingView();
        this.initWebSocket();
        this.bindEvents();
        this.startDataRefresh();
    }

    async loadUserData() {
        try {
            // Get current exchange and account from selectors
            const exchange = document.querySelector('.exchange-select')?.value || this.currentExchange;
            const accountType = document.querySelector('.account-select')?.value || 'demo';
            
            const [posRes, ordRes, tradesRes, statsRes, balRes] = await Promise.all([
                fetch(`/api/trading/positions?exchange=${exchange}&account_type=${accountType}`),
                fetch(`/api/trading/orders?exchange=${exchange}&account_type=${accountType}`),
                fetch(`/api/trading/trades?limit=100`),
                fetch(`/api/trading/stats`),
                fetch(`/api/trading/balance?exchange=${exchange}&account_type=${accountType}`)
            ]);
            
            if (posRes.ok) {
                const data = await posRes.json();
                this.positions = Array.isArray(data) ? data : (data.data || []);
                this.renderPositions();
            }
            if (ordRes.ok) {
                const data = await ordRes.json();
                this.orders = Array.isArray(data) ? data : (data.data || []);
                this.renderOrders();
            }
            if (tradesRes.ok) {
                const data = await tradesRes.json();
                this.trades = Array.isArray(data) ? data : (data.data || []);
                this.renderTrades();
            }
            if (statsRes.ok) {
                const data = await statsRes.json();
                this.stats = data.data || data || {};
            }
            if (balRes.ok) {
                const balance = await balRes.json();
                this.updateBalanceDisplay(balance);
            }
        } catch (e) {
            console.error('Failed to load user data:', e);
            if (window.Notifications) {
                window.Notifications.show('Failed to load trading data', 'error');
            }
        }
    }

    initTradingView() {
        const container = document.getElementById('tradingview-chart');
        if (!container) return;

        // TradingView Advanced Charts widget
        new TradingView.widget({
            "autosize": true,
            "symbol": `${this.currentExchange.toUpperCase()}:${this.currentSymbol}`,
            "interval": this.timeframeToTradingView(this.currentTimeframe),
            "timezone": "Etc/UTC",
            "theme": "dark",
            "style": "1",
            "locale": "en",
            "toolbar_bg": "#141418",
            "enable_publishing": false,
            "hide_side_toolbar": false,
            "allow_symbol_change": true,
            "container_id": "tradingview-chart",
            "studies": [
                "RSI@tv-basicstudies",
                "MACD@tv-basicstudies",
                "BB@tv-basicstudies"
            ],
            "overrides": {
                "paneProperties.background": "#0d0d0f",
                "paneProperties.backgroundType": "solid",
                "scalesProperties.backgroundColor": "#0d0d0f",
                "scalesProperties.lineColor": "#27272a",
                "scalesProperties.textColor": "#a1a1aa"
            }
        });
    }

    timeframeToTradingView(tf) {
        const map = {
            '1m': '1', '5m': '5', '15m': '15', '30m': '30',
            '1h': '60', '4h': '240', '1d': 'D', '1w': 'W'
        };
        return map[tf] || '60';
    }

    initWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.ws = new WebSocket(`${protocol}//${window.location.host}/ws/market`);
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWSMessage(data);
        };

        this.ws.onclose = () => {
            setTimeout(() => this.initWebSocket(), 5000);
        };
    }

    handleWSMessage(data) {
        switch(data.type) {
            case 'price':
                this.updatePrice(data);
                break;
            case 'position':
                this.updatePosition(data);
                break;
            case 'order':
                this.updateOrder(data);
                break;
            case 'trade':
                this.addTrade(data);
                break;
        }
    }

    bindEvents() {
        // Symbol selector
        document.querySelectorAll('.symbol-item').forEach(el => {
            el.addEventListener('click', () => {
                this.currentSymbol = el.dataset.symbol;
                this.updateChart();
            });
        });

        // Timeframe selector
        document.querySelectorAll('.tf-btn').forEach(el => {
            el.addEventListener('click', () => {
                this.currentTimeframe = el.dataset.tf;
                this.updateChart();
            });
        });

        // Exchange selector
        document.querySelectorAll('.exchange-tab').forEach(el => {
            el.addEventListener('click', () => {
                this.currentExchange = el.dataset.exchange;
                this.loadUserData();
                this.updateChart();
            });
        });
        
        // Exchange select dropdown (if exists)
        const exchangeSelect = document.querySelector('.exchange-select');
        if (exchangeSelect) {
            exchangeSelect.addEventListener('change', (e) => {
                this.currentExchange = e.target.value;
                this.loadUserData();
                this.updateChart();
            });
        }
        
        // Account type select dropdown (if exists)
        const accountSelect = document.querySelector('.account-select');
        if (accountSelect) {
            accountSelect.addEventListener('change', () => {
                this.loadUserData();
            });
        }
    }

    updateChart() {
        // Reinit TradingView with new symbol/timeframe
        this.initTradingView();
    }

    startDataRefresh() {
        setInterval(() => this.loadUserData(), 5000);
    }

    updatePrice(data) {
        const el = document.querySelector(`[data-symbol="${data.symbol}"] .price`);
        if (el) {
            el.textContent = `$${parseFloat(data.price).toLocaleString()}`;
            el.classList.add(data.change > 0 ? 'text-success' : 'text-danger');
        }
    }

    updatePosition(data) {
        const idx = this.positions.findIndex(p => p.id === data.id);
        if (idx >= 0) {
            this.positions[idx] = data;
        } else {
            this.positions.push(data);
        }
        this.renderPositions();
    }

    updateOrder(data) {
        const idx = this.orders.findIndex(o => o.id === data.id);
        if (data.status === 'cancelled' || data.status === 'filled') {
            if (idx >= 0) this.orders.splice(idx, 1);
        } else if (idx >= 0) {
            this.orders[idx] = data;
        } else {
            this.orders.push(data);
        }
        this.renderOrders();
    }

    addTrade(data) {
        this.trades.unshift(data);
        if (this.trades.length > 100) this.trades.pop();
        this.renderTrades();
    }
    
    updateBalanceDisplay(balance) {
        // Update equity
        const equityEl = document.querySelector('[data-balance="equity"]');
        if (equityEl) {
            equityEl.textContent = `$${parseFloat(balance.equity || 0).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }
        
        // Update available balance
        const availableEl = document.querySelector('[data-balance="available"]');
        if (availableEl) {
            availableEl.textContent = `$${parseFloat(balance.available || 0).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }
        
        // Update unrealized P&L
        const pnlEl = document.querySelector('[data-balance="pnl"]');
        if (pnlEl) {
            const pnl = parseFloat(balance.unrealized_pnl || 0);
            pnlEl.textContent = `${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)}`;
            pnlEl.className = pnl >= 0 ? 'balance-value positive' : 'balance-value negative';
        }
    }

    renderPositions() {
        const container = document.getElementById('positions-list');
        if (!container) return;

        if (this.positions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <p>No open positions</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.positions.map(pos => `
            <div class="position-card ${pos.side === 'Buy' ? 'long' : 'short'}" data-id="${pos.id}">
                <div class="position-header">
                    <span class="symbol">${pos.symbol}</span>
                    <span class="side ${pos.side === 'Buy' ? 'long' : 'short'}">${pos.side === 'Buy' ? 'LONG' : 'SHORT'}</span>
                    <span class="leverage">${pos.leverage}x</span>
                </div>
                <div class="position-body">
                    <div class="stat">
                        <span class="label">Size</span>
                        <span class="value">${pos.size}</span>
                    </div>
                    <div class="stat">
                        <span class="label">Entry</span>
                        <span class="value">$${parseFloat(pos.entryPrice).toLocaleString()}</span>
                    </div>
                    <div class="stat">
                        <span class="label">Mark</span>
                        <span class="value">$${parseFloat(pos.markPrice).toLocaleString()}</span>
                    </div>
                    <div class="stat pnl ${parseFloat(pos.unrealisedPnl) >= 0 ? 'profit' : 'loss'}">
                        <span class="label">PnL</span>
                        <span class="value">${parseFloat(pos.unrealisedPnl) >= 0 ? '+' : ''}$${parseFloat(pos.unrealisedPnl).toFixed(2)}</span>
                    </div>
                </div>
                <div class="position-tpsl">
                    <span class="tp">TP: ${pos.takeProfit || '-'}</span>
                    <span class="sl">SL: ${pos.stopLoss || '-'}</span>
                </div>
                <div class="position-actions">
                    <button class="btn btn-sm btn-success" onclick="terminal.modifyPosition('${pos.id}')">
                        <i class="fas fa-edit"></i> Modify
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="terminal.closePosition('${pos.id}')">
                        <i class="fas fa-times"></i> Close
                    </button>
                </div>
            </div>
        `).join('');
    }

    renderOrders() {
        const container = document.getElementById('orders-list');
        if (!container) return;

        if (this.orders.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-clipboard-list"></i>
                    <p>No open orders</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.orders.map(order => `
            <div class="order-row">
                <span class="symbol">${order.symbol}</span>
                <span class="side ${order.side === 'Buy' ? 'buy' : 'sell'}">${order.side}</span>
                <span class="type">${order.orderType}</span>
                <span class="qty">${order.qty}</span>
                <span class="price">$${parseFloat(order.price).toLocaleString()}</span>
                <span class="status">${order.status}</span>
                <button class="btn btn-xs btn-danger" onclick="terminal.cancelOrder('${order.orderId}')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
    }

    renderTrades() {
        const container = document.getElementById('trades-list');
        if (!container) return;

        container.innerHTML = this.trades.slice(0, 50).map(trade => `
            <div class="trade-row ${trade.pnl >= 0 ? 'profit' : 'loss'}">
                <span class="time">${new Date(trade.time).toLocaleString()}</span>
                <span class="symbol">${trade.symbol}</span>
                <span class="side ${trade.side === 'Buy' ? 'buy' : 'sell'}">${trade.side}</span>
                <span class="qty">${trade.qty}</span>
                <span class="price">$${parseFloat(trade.price).toLocaleString()}</span>
                <span class="pnl ${trade.pnl >= 0 ? 'profit' : 'loss'}">
                    ${trade.pnl >= 0 ? '+' : ''}$${parseFloat(trade.pnl || 0).toFixed(2)}
                </span>
                <span class="strategy">${trade.strategy || '-'}</span>
                <button class="btn btn-xs btn-ghost" onclick="terminal.showTradeOnChart('${trade.id}')">
                    <i class="fas fa-chart-line"></i>
                </button>
            </div>
        `).join('');
    }

    async closePosition(positionId) {
        if (!confirm('Close this position?')) return;
        
        try {
            const res = await fetch(`/api/trading/positions/${positionId}/close`, {
                method: 'POST'
            });
            if (res.ok) {
                showToast('Position closed', 'success');
                this.loadUserData();
            }
        } catch (e) {
            showToast('Failed to close position', 'error');
        }
    }

    async cancelOrder(orderId) {
        try {
            const res = await fetch(`/api/trading/orders/${orderId}`, {
                method: 'DELETE'
            });
            if (res.ok) {
                showToast('Order cancelled', 'success');
                this.loadUserData();
            }
        } catch (e) {
            showToast('Failed to cancel order', 'error');
        }
    }

    modifyPosition(positionId) {
        const pos = this.positions.find(p => p.id === positionId);
        if (!pos) return;

        showModal('modify-position', {
            title: `Modify ${pos.symbol} Position`,
            content: `
                <div class="form-group">
                    <label>Take Profit</label>
                    <input type="number" id="modify-tp" value="${pos.takeProfit || ''}" placeholder="TP Price">
                </div>
                <div class="form-group">
                    <label>Stop Loss</label>
                    <input type="number" id="modify-sl" value="${pos.stopLoss || ''}" placeholder="SL Price">
                </div>
            `,
            onConfirm: async () => {
                const tp = document.getElementById('modify-tp').value;
                const sl = document.getElementById('modify-sl').value;
                
                const res = await fetch(`/api/trading/positions/${positionId}/tpsl`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ takeProfit: tp, stopLoss: sl })
                });
                
                if (res.ok) {
                    showToast('Position modified', 'success');
                    this.loadUserData();
                }
            }
        });
    }

    showTradeOnChart(tradeId) {
        const trade = this.trades.find(t => t.id === tradeId);
        if (!trade) return;

        // Change symbol and show trade details
        this.currentSymbol = trade.symbol;
        this.updateChart();

        // Show trade details modal
        showModal('trade-details', {
            title: `Trade Details - ${trade.symbol}`,
            content: `
                <div class="trade-details-modal">
                    <div class="trade-chart-container" id="trade-mini-chart"></div>
                    <div class="trade-info">
                        <div class="info-row">
                            <span>Direction</span>
                            <span class="${trade.side === 'Buy' ? 'text-success' : 'text-danger'}">
                                ${trade.side === 'Buy' ? '🟢 LONG' : '🔴 SHORT'}
                            </span>
                        </div>
                        <div class="info-row">
                            <span>Entry Price</span>
                            <span>$${parseFloat(trade.entryPrice || trade.price).toLocaleString()}</span>
                        </div>
                        <div class="info-row">
                            <span>Exit Price</span>
                            <span>$${parseFloat(trade.exitPrice || trade.price).toLocaleString()}</span>
                        </div>
                        <div class="info-row">
                            <span>Take Profit</span>
                            <span class="text-success">${trade.takeProfit || '-'}</span>
                        </div>
                        <div class="info-row">
                            <span>Stop Loss</span>
                            <span class="text-danger">${trade.stopLoss || '-'}</span>
                        </div>
                        <div class="info-row">
                            <span>Size</span>
                            <span>${trade.qty}</span>
                        </div>
                        <div class="info-row pnl-row ${trade.pnl >= 0 ? 'profit' : 'loss'}">
                            <span>PnL</span>
                            <span>${trade.pnl >= 0 ? '+' : ''}$${parseFloat(trade.pnl || 0).toFixed(2)}</span>
                        </div>
                        <div class="info-row">
                            <span>Strategy</span>
                            <span class="strategy-badge">${trade.strategy || 'Manual'}</span>
                        </div>
                        <div class="info-row">
                            <span>Exchange</span>
                            <span>${trade.exchange || this.currentExchange}</span>
                        </div>
                        <div class="info-row">
                            <span>Time</span>
                            <span>${new Date(trade.time).toLocaleString()}</span>
                        </div>
                    </div>
                </div>
            `
        });
    }
}

// Initialize terminal
const terminal = new TradingTerminal();
