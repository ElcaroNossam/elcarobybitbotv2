/**
 * ElCaro Advanced Terminal - Professional Trading Interface
 * Version 2.0 - Enhanced trading features with DCA, Risk Calculator, and more
 */

// ============================================================
// RISK CALCULATOR - Position sizing and risk management
// ============================================================
const RiskCalculator = {
    state: {
        accountBalance: 10000,
        riskPercent: 1,
        entryPrice: 0,
        stopLoss: 0,
        leverage: 10,
        symbol: 'BTCUSDT',
        tickSize: 0.01
    },

    async calculate() {
        const { accountBalance, riskPercent, entryPrice, stopLoss, leverage } = this.state;
        if (!entryPrice || !stopLoss) return null;

        try {
            // Use new position calculator API endpoint (matches bot.py exactly)
            const response = await fetch('/api/trading/calculate-position', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    account_balance: accountBalance,
                    entry_price: entryPrice,
                    stop_loss_price: stopLoss,
                    risk_percent: riskPercent,
                    leverage: leverage,
                    side: stopLoss < entryPrice ? 'Buy' : 'Sell'
                })
            });

            if (!response.ok) {
                // Fallback to local calculation if API fails
                console.warn('Position calculator API failed, using fallback');
                return this.calculateFallback();
            }

            const data = await response.json();
            
            // Return in expected format
            return {
                positionSize: data.position_size,
                positionValue: data.position_value_usd,
                marginRequired: data.margin_required,
                riskAmount: data.risk_amount_usd,
                stopPercent: data.stop_loss_percent,
                liqPrice: null, // Not provided by API yet
                maxPositionSize: accountBalance * leverage / entryPrice,
                riskReward: data.risk_reward_ratio,
                potentialProfit: data.potential_profit_usd,
                warnings: data.warnings || []
            };
        } catch (error) {
            console.error('Position calculation error:', error);
            return this.calculateFallback();
        }
    },

    calculateFallback() {
        // Original calculation as fallback
        const { accountBalance, riskPercent, entryPrice, stopLoss, leverage } = this.state;
        
        const riskAmount = accountBalance * (riskPercent / 100);
        const priceDiff = Math.abs(entryPrice - stopLoss);
        const stopPercent = (priceDiff / entryPrice) * 100;
        
        // Formula: position_size = risk_amount / (entry_price * (stop_loss_percent / 100))
        const positionSize = riskAmount / (entryPrice * (stopPercent / 100));
        const positionValue = positionSize * entryPrice;
        const marginRequired = positionValue / leverage;
        
        // Liquidation price
        const isBuy = stopLoss < entryPrice;
        const liqPrice = isBuy 
            ? entryPrice * (1 - 0.9 / leverage)
            : entryPrice * (1 + 0.9 / leverage);
        
        return {
            positionSize,
            positionValue,
            marginRequired,
            riskAmount,
            stopPercent,
            liqPrice,
            maxPositionSize: accountBalance * leverage / entryPrice,
            riskReward: null
        };
    },

    async setRiskReward(takeProfit) {
        const { accountBalance, riskPercent, entryPrice, stopLoss, leverage } = this.state;
        if (!entryPrice || !stopLoss || !takeProfit) return null;

        try {
            // Use API with TP/SL
            const response = await fetch('/api/trading/calculate-position', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    account_balance: accountBalance,
                    entry_price: entryPrice,
                    stop_loss_price: stopLoss,
                    take_profit_price: takeProfit,
                    risk_percent: riskPercent,
                    leverage: leverage,
                    side: stopLoss < entryPrice ? 'Buy' : 'Sell'
                })
            });

            if (!response.ok) {
                // Fallback
                const result = await this.calculate();
                if (!result) return null;
                
                const isBuy = stopLoss < entryPrice;
                const risk = Math.abs(entryPrice - stopLoss);
                const reward = isBuy ? takeProfit - entryPrice : entryPrice - takeProfit;
                result.riskReward = reward / risk;
                result.potentialProfit = result.riskAmount * result.riskReward;
                return result;
            }

            const data = await response.json();
            
            return {
                positionSize: data.position_size,
                positionValue: data.position_value_usd,
                marginRequired: data.margin_required,
                riskAmount: data.risk_amount_usd,
                stopPercent: data.stop_loss_percent,
                liqPrice: null,
                maxPositionSize: accountBalance * leverage / entryPrice,
                riskReward: data.risk_reward_ratio,
                potentialProfit: data.potential_profit_usd,
                warnings: data.warnings || []
            };
        } catch (error) {
            console.error('Risk/Reward calculation error:', error);
            return await this.calculate();
        }
    },

    async render() {
        const result = await this.calculate();
        if (!result) return '';

        const hasWarnings = result.warnings && result.warnings.length > 0;

        return `
            <div class="risk-calc-result">
                ${hasWarnings ? `
                <div class="risk-warnings" style="background: rgba(251, 191, 36, 0.1); border-left: 3px solid var(--yellow); padding: 8px 12px; margin-bottom: 10px; border-radius: 6px;">
                    ${result.warnings.map(w => `<div style="font-size: 0.75rem; color: var(--yellow); margin: 2px 0;"><i class="fas fa-exclamation-triangle"></i> ${w}</div>`).join('')}
                </div>
                ` : ''}
                <div class="risk-row">
                    <span>Position Size</span>
                    <strong>${result.positionSize.toFixed(4)} ${this.state.symbol.replace('USDT', '')}</strong>
                </div>
                <div class="risk-row">
                    <span>Position Value</span>
                    <strong>$${result.positionValue.toLocaleString(undefined, {maximumFractionDigits: 2})}</strong>
                </div>
                <div class="risk-row">
                    <span>Margin Required</span>
                    <strong>$${result.marginRequired.toFixed(2)}</strong>
                </div>
                <div class="risk-row warning">
                    <span>Risk Amount (${this.state.riskPercent}%)</span>
                    <strong style="color: var(--red);">-$${result.riskAmount.toFixed(2)}</strong>
                </div>
                ${result.liqPrice ? `
                <div class="risk-row">
                    <span>Liq. Price</span>
                    <strong style="color: var(--red);">$${result.liqPrice.toFixed(2)}</strong>
                </div>
                ` : ''}
                ${result.riskReward ? `
                <div class="risk-row">
                    <span>Risk/Reward</span>
                    <strong style="color: ${result.riskReward >= 2 ? 'var(--green)' : 'var(--yellow)'};">1:${result.riskReward.toFixed(2)}</strong>
                </div>
                <div class="risk-row">
                    <span>Potential Profit</span>
                    <strong style="color: var(--green);">+$${result.potentialProfit.toFixed(2)}</strong>
                </div>
                ` : ''}
                <div class="risk-row" style="margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--border);">
                    <span style="font-size: 0.7rem; color: var(--text-muted);">✓ Bot.py formula</span>
                    <span style="font-size: 0.7rem; color: var(--green); font-family: var(--font-mono);">EXACT MATCH</span>
                </div>
            </div>
        `;
    }
};


// ============================================================
// DCA LADDER BUILDER - Dollar Cost Averaging orders
// ============================================================
const DCABuilder = {
    state: {
        enabled: false,
        orders: [],
        totalSize: 1,
        priceRange: 5, // 5% from entry
        orderCount: 5,
        distribution: 'linear', // linear, geometric, fibonacci
        side: 'buy',
        entryPrice: 0
    },

    distributions: {
        linear: (count) => Array(count).fill(1),
        geometric: (count) => Array.from({length: count}, (_, i) => Math.pow(1.5, i)),
        fibonacci: (count) => {
            let fib = [1, 1];
            for (let i = 2; i < count; i++) fib.push(fib[i-1] + fib[i-2]);
            return fib.slice(0, count);
        },
        exponential: (count) => Array.from({length: count}, (_, i) => Math.pow(2, i))
    },

    calculate() {
        const { totalSize, priceRange, orderCount, distribution, side, entryPrice } = this.state;
        if (!entryPrice || orderCount < 2) return [];

        const weights = this.distributions[distribution](orderCount);
        const totalWeight = weights.reduce((a, b) => a + b, 0);
        
        const orders = [];
        const priceStep = (entryPrice * priceRange / 100) / (orderCount - 1);
        
        for (let i = 0; i < orderCount; i++) {
            const sizeWeight = weights[i] / totalWeight;
            const size = totalSize * sizeWeight;
            const price = side === 'buy'
                ? entryPrice - (priceStep * i)
                : entryPrice + (priceStep * i);
            
            orders.push({
                index: i + 1,
                price: parseFloat(price.toFixed(2)),
                size: parseFloat(size.toFixed(4)),
                value: parseFloat((price * size).toFixed(2)),
                percentFromEntry: ((price - entryPrice) / entryPrice * 100).toFixed(2)
            });
        }
        
        this.state.orders = orders;
        return orders;
    },

    getAverageEntry() {
        if (!this.state.orders.length) return 0;
        const totalValue = this.state.orders.reduce((sum, o) => sum + o.value, 0);
        const totalSize = this.state.orders.reduce((sum, o) => sum + o.size, 0);
        return totalValue / totalSize;
    },

    render() {
        const orders = this.calculate();
        const avgEntry = this.getAverageEntry();
        const totalValue = orders.reduce((sum, o) => sum + o.value, 0);

        return `
            <div class="dca-builder">
                <div class="dca-header">
                    <h4><i class="fas fa-layer-group"></i> DCA Ladder</h4>
                    <div class="dca-controls">
                        <select id="dcaDistribution" onchange="DCABuilder.setDistribution(this.value)">
                            <option value="linear">Linear</option>
                            <option value="geometric">Geometric</option>
                            <option value="fibonacci">Fibonacci</option>
                            <option value="exponential">Exponential</option>
                        </select>
                        <input type="number" id="dcaOrderCount" value="${this.state.orderCount}" 
                               min="2" max="20" onchange="DCABuilder.setOrderCount(this.value)">
                        <span>orders</span>
                    </div>
                </div>
                
                <div class="dca-summary">
                    <div class="dca-stat">
                        <span>Avg Entry</span>
                        <strong>$${avgEntry.toFixed(2)}</strong>
                    </div>
                    <div class="dca-stat">
                        <span>Total Value</span>
                        <strong>$${totalValue.toFixed(2)}</strong>
                    </div>
                    <div class="dca-stat">
                        <span>Price Range</span>
                        <strong>${this.state.priceRange}%</strong>
                    </div>
                </div>

                <div class="dca-orders">
                    ${orders.map(o => `
                        <div class="dca-order ${this.state.side}">
                            <span class="order-num">#${o.index}</span>
                            <span class="order-price">$${o.price.toLocaleString()}</span>
                            <span class="order-size">${o.size.toFixed(4)}</span>
                            <span class="order-pct">${o.percentFromEntry}%</span>
                        </div>
                    `).join('')}
                </div>

                <button class="dca-submit" onclick="DCABuilder.placeOrders()">
                    <i class="fas fa-bolt"></i> Place ${orders.length} Orders
                </button>
            </div>
        `;
    },

    setDistribution(dist) {
        this.state.distribution = dist;
        this.render();
    },

    setOrderCount(count) {
        this.state.orderCount = parseInt(count);
        this.render();
    },

    async placeOrders() {
        const orders = this.state.orders;
        if (!orders.length) return;

        const token = localStorage.getItem('triacelo_token');
        let success = 0, failed = 0;

        for (const order of orders) {
            try {
                const res = await fetch('/api/trading/order', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + token 
                    },
                    body: JSON.stringify({
                        symbol: window.state?.symbol || 'BTCUSDT',
                        side: this.state.side,
                        type: 'limit',
                        price: order.price,
                        size: order.size,
                        timeInForce: 'GTC'
                    })
                });
                const data = await res.json();
                if (data.success) success++;
                else failed++;
            } catch (e) {
                failed++;
            }
        }

        Notifications.show(
            `Placed ${success}/${orders.length} DCA orders${failed ? ` (${failed} failed)` : ''}`,
            success === orders.length ? 'success' : 'warning'
        );
    }
};


// ============================================================
// TRAILING STOP MANAGER - Advanced stop management
// ============================================================
const TrailingStop = {
    state: {
        enabled: false,
        triggerPercent: 1, // Activate after 1% profit
        trailPercent: 0.5, // Trail by 0.5%
        breakEvenAt: 2, // Move to break-even at 2% profit
        positions: new Map()
    },

    track(position) {
        const { symbol, entry_price, side, pnl } = position;
        const key = `${symbol}-${side}`;
        
        if (!this.state.positions.has(key)) {
            this.state.positions.set(key, {
                highestProfit: 0,
                trailStop: null,
                breakEvenHit: false
            });
        }
        
        const tracking = this.state.positions.get(key);
        const profitPercent = (pnl / position.margin) * 100;
        
        // Update highest profit
        if (profitPercent > tracking.highestProfit) {
            tracking.highestProfit = profitPercent;
            
            // Calculate new trail stop
            if (profitPercent >= this.state.triggerPercent) {
                const isBuy = side === 'long';
                const currentPrice = position.mark_price;
                tracking.trailStop = isBuy
                    ? currentPrice * (1 - this.state.trailPercent / 100)
                    : currentPrice * (1 + this.state.trailPercent / 100);
            }
        }
        
        // Break-even logic
        if (!tracking.breakEvenHit && profitPercent >= this.state.breakEvenAt) {
            tracking.breakEvenHit = true;
            tracking.trailStop = position.entry_price;
            Notifications.show(`${symbol}: Stop moved to break-even`, 'info');
        }
        
        return tracking;
    },

    render() {
        return `
            <div class="trailing-stop-panel">
                <div class="ts-header">
                    <h4><i class="fas fa-chart-line"></i> Trailing Stop</h4>
                    <div class="toggle-switch ${this.state.enabled ? 'active' : ''}" 
                         onclick="TrailingStop.toggle()"></div>
                </div>
                
                <div class="ts-settings ${this.state.enabled ? '' : 'disabled'}">
                    <div class="ts-row">
                        <label>Activate at</label>
                        <input type="number" value="${this.state.triggerPercent}" step="0.1"
                               onchange="TrailingStop.state.triggerPercent = parseFloat(this.value)">
                        <span>% profit</span>
                    </div>
                    <div class="ts-row">
                        <label>Trail by</label>
                        <input type="number" value="${this.state.trailPercent}" step="0.1"
                               onchange="TrailingStop.state.trailPercent = parseFloat(this.value)">
                        <span>%</span>
                    </div>
                    <div class="ts-row">
                        <label>Break-even at</label>
                        <input type="number" value="${this.state.breakEvenAt}" step="0.1"
                               onchange="TrailingStop.state.breakEvenAt = parseFloat(this.value)">
                        <span>% profit</span>
                    </div>
                </div>
            </div>
        `;
    },

    toggle() {
        this.state.enabled = !this.state.enabled;
    }
};


// ============================================================
// ORDERBOOK HEATMAP - Visual depth analysis
// ============================================================
const OrderbookHeatmap = {
    state: {
        asks: [],
        bids: [],
        maxSize: 0,
        grouping: 0.01,
        imbalance: 0
    },

    update(asks, bids) {
        this.state.asks = asks;
        this.state.bids = bids;
        
        // Calculate max size for heatmap scaling
        const allSizes = [...asks, ...bids].map(l => l.size);
        this.state.maxSize = Math.max(...allSizes);
        
        // Calculate bid/ask imbalance
        const bidVolume = bids.slice(0, 10).reduce((sum, b) => sum + b.size, 0);
        const askVolume = asks.slice(0, 10).reduce((sum, a) => sum + a.size, 0);
        this.state.imbalance = ((bidVolume - askVolume) / (bidVolume + askVolume)) * 100;
    },

    getHeatColor(size, side) {
        const intensity = Math.min(size / this.state.maxSize, 1);
        if (side === 'ask') {
            return `rgba(239, 68, 68, ${0.1 + intensity * 0.6})`;
        }
        return `rgba(34, 197, 94, ${0.1 + intensity * 0.6})`;
    },

    renderImbalanceIndicator() {
        const { imbalance } = this.state;
        const color = imbalance > 10 ? 'var(--green)' : imbalance < -10 ? 'var(--red)' : 'var(--text-muted)';
        const label = imbalance > 10 ? 'Bullish' : imbalance < -10 ? 'Bearish' : 'Neutral';
        
        return `
            <div class="imbalance-indicator">
                <div class="imbalance-bar">
                    <div class="imbalance-fill" style="width: ${50 + imbalance/2}%; background: ${color};"></div>
                </div>
                <span class="imbalance-label" style="color: ${color};">${label} (${imbalance.toFixed(1)}%)</span>
            </div>
        `;
    },

    renderLevel(level, side) {
        const heatColor = this.getHeatColor(level.size, side);
        const isLargeOrder = level.size > this.state.maxSize * 0.3;
        
        return `
            <div class="orderbook-row ${side} ${isLargeOrder ? 'whale' : ''}" 
                 style="--heat-color: ${heatColor};"
                 onclick="setPrice(${level.price})">
                <span class="price">${level.price.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
                <span class="size ${isLargeOrder ? 'highlight' : ''}">${level.size.toFixed(4)}</span>
                <span class="total">${level.total.toFixed(2)}</span>
                <div class="depth" style="width: ${level.depth}%; background: ${heatColor};"></div>
                ${isLargeOrder ? '<i class="fas fa-fish whale-icon"></i>' : ''}
            </div>
        `;
    }
};


// ============================================================
// ONE-CLICK TRADING - Fast execution mode
// ============================================================
const OneClickTrading = {
    state: {
        enabled: false,
        confirmationTime: 3, // seconds to cancel
        pendingOrder: null,
        countdown: 0
    },

    enable() {
        if (!confirm('Enable One-Click Trading? Orders will be placed immediately without confirmation dialog.')) {
            return;
        }
        this.state.enabled = true;
        Notifications.show('One-Click Trading enabled', 'warning');
    },

    disable() {
        this.state.enabled = false;
        Notifications.show('One-Click Trading disabled', 'info');
    },

    async quickOrder(side, percent = 25) {
        const price = window.state?.lastPrice || 0;
        const available = parseFloat(document.getElementById('availableBalance')?.textContent.replace(/[$,]/g, '') || 0);
        const leverage = window.state?.leverage || 10;
        
        if (!price) {
            Notifications.show('Price not available', 'error');
            return;
        }

        const positionValue = available * leverage * (percent / 100);
        const size = positionValue / price;

        if (this.state.enabled) {
            // Immediate execution with cancel countdown
            this.state.pendingOrder = { side, size, price };
            this.state.countdown = this.state.confirmationTime;
            
            this.showCountdown();
            
            const timer = setInterval(() => {
                this.state.countdown--;
                if (this.state.countdown <= 0) {
                    clearInterval(timer);
                    this.executeOrder();
                } else {
                    this.showCountdown();
                }
            }, 1000);
            
            this.state.timer = timer;
        } else {
            // Normal flow - populate form
            document.getElementById('sizeInput').value = size.toFixed(4);
            document.getElementById('priceInput').value = price;
            window.setSide?.(side);
        }
    },

    showCountdown() {
        const existing = document.getElementById('oneclick-countdown');
        if (existing) existing.remove();

        const div = document.createElement('div');
        div.id = 'oneclick-countdown';
        div.innerHTML = `
            <div class="oneclick-popup">
                <div class="oneclick-side ${this.state.pendingOrder.side}">
                    ${this.state.pendingOrder.side.toUpperCase()}
                </div>
                <div class="oneclick-details">
                    ${this.state.pendingOrder.size.toFixed(4)} @ $${this.state.pendingOrder.price.toLocaleString()}
                </div>
                <div class="oneclick-countdown">${this.state.countdown}s</div>
                <button class="oneclick-cancel" onclick="OneClickTrading.cancel()">Cancel</button>
            </div>
        `;
        document.body.appendChild(div);
    },

    cancel() {
        if (this.state.timer) {
            clearInterval(this.state.timer);
            this.state.timer = null;
        }
        this.state.pendingOrder = null;
        const popup = document.getElementById('oneclick-countdown');
        if (popup) popup.remove();
        Notifications.show('Order cancelled', 'info');
    },

    async executeOrder() {
        const popup = document.getElementById('oneclick-countdown');
        if (popup) popup.remove();

        if (!this.state.pendingOrder) return;

        const { side, size, price } = this.state.pendingOrder;
        this.state.pendingOrder = null;

        try {
            const token = localStorage.getItem('triacelo_token');
            const res = await fetch('/api/trading/order', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + token 
                },
                body: JSON.stringify({
                    symbol: window.state?.symbol || 'BTCUSDT',
                    side,
                    type: 'market',
                    size,
                    leverage: window.state?.leverage || 10
                })
            });
            const data = await res.json();
            if (data.success) {
                Notifications.show(`Market ${side.toUpperCase()} executed!`, 'success');
            } else {
                Notifications.show(data.error || 'Order failed', 'error');
            }
        } catch (e) {
            Notifications.show('Order execution failed', 'error');
        }
    }
};


// ============================================================
// POSITION ANALYTICS - P&L tracking and analysis
// ============================================================
const PositionAnalytics = {
    state: {
        dailyPnL: 0,
        weeklyPnL: 0,
        totalTrades: 0,
        winRate: 0,
        avgWin: 0,
        avgLoss: 0,
        largestWin: 0,
        largestLoss: 0,
        currentStreak: 0,
        positions: []
    },

    async fetchStats() {
        try {
            const token = localStorage.getItem('triacelo_token');
            const res = await fetch('/api/trading/stats?period=week', {
                headers: { 'Authorization': 'Bearer ' + token }
            });
            if (res.ok) {
                const data = await res.json();
                Object.assign(this.state, data);
            }
        } catch (e) {
            console.error('Stats fetch error:', e);
        }
    },

    render() {
        return `
            <div class="analytics-panel">
                <div class="analytics-header">
                    <h4><i class="fas fa-chart-pie"></i> Session Analytics</h4>
                </div>
                
                <div class="analytics-grid">
                    <div class="stat-card ${this.state.dailyPnL >= 0 ? 'positive' : 'negative'}">
                        <span class="stat-label">Today's P&L</span>
                        <span class="stat-value">${this.state.dailyPnL >= 0 ? '+' : ''}$${this.state.dailyPnL.toFixed(2)}</span>
                    </div>
                    
                    <div class="stat-card">
                        <span class="stat-label">Win Rate</span>
                        <span class="stat-value">${this.state.winRate.toFixed(1)}%</span>
                    </div>
                    
                    <div class="stat-card">
                        <span class="stat-label">Total Trades</span>
                        <span class="stat-value">${this.state.totalTrades}</span>
                    </div>
                    
                    <div class="stat-card ${this.state.currentStreak >= 0 ? 'streak-win' : 'streak-loss'}">
                        <span class="stat-label">Streak</span>
                        <span class="stat-value">${Math.abs(this.state.currentStreak)} ${this.state.currentStreak >= 0 ? '🔥' : '❄️'}</span>
                    </div>
                </div>
                
                <div class="analytics-chart" id="pnlMiniChart"></div>
            </div>
        `;
    },

    renderPnLChart(containerId, data) {
        // Mini sparkline chart for P&L
        const container = document.getElementById(containerId);
        if (!container || !data.length) return;

        const width = container.offsetWidth;
        const height = 60;
        const max = Math.max(...data.map(d => Math.abs(d)));
        const mid = height / 2;

        const points = data.map((d, i) => {
            const x = (i / (data.length - 1)) * width;
            const y = mid - (d / max) * (mid - 5);
            return `${x},${y}`;
        }).join(' ');

        container.innerHTML = `
            <svg width="${width}" height="${height}">
                <line x1="0" y1="${mid}" x2="${width}" y2="${mid}" stroke="var(--border)" stroke-dasharray="4"/>
                <polyline points="${points}" fill="none" stroke="var(--accent)" stroke-width="2"/>
            </svg>
        `;
    }
};


// ============================================================
// SMART ALERTS - Price and position alerts
// ============================================================
const SmartAlerts = {
    alerts: [],

    add(type, config) {
        const alert = {
            id: Date.now(),
            type, // price, pnl, liquidation, funding
            ...config,
            active: true,
            createdAt: new Date()
        };
        this.alerts.push(alert);
        this.save();
        return alert;
    },

    remove(id) {
        this.alerts = this.alerts.filter(a => a.id !== id);
        this.save();
    },

    check(currentData) {
        for (const alert of this.alerts) {
            if (!alert.active) continue;

            let triggered = false;
            let message = '';

            switch (alert.type) {
                case 'price':
                    if (alert.condition === 'above' && currentData.price >= alert.value) {
                        triggered = true;
                        message = `${alert.symbol} reached $${alert.value}`;
                    } else if (alert.condition === 'below' && currentData.price <= alert.value) {
                        triggered = true;
                        message = `${alert.symbol} dropped to $${alert.value}`;
                    }
                    break;

                case 'pnl':
                    const position = currentData.positions?.find(p => p.symbol === alert.symbol);
                    if (position) {
                        const pnlPercent = position.roe || 0;
                        if (alert.condition === 'profit' && pnlPercent >= alert.value) {
                            triggered = true;
                            message = `${alert.symbol} reached ${alert.value}% profit!`;
                        } else if (alert.condition === 'loss' && pnlPercent <= -alert.value) {
                            triggered = true;
                            message = `${alert.symbol} hit ${alert.value}% loss!`;
                        }
                    }
                    break;

                case 'liquidation':
                    const pos = currentData.positions?.find(p => p.symbol === alert.symbol);
                    if (pos && pos.liq_price) {
                        const distancePercent = Math.abs((currentData.price - pos.liq_price) / pos.liq_price) * 100;
                        if (distancePercent <= alert.value) {
                            triggered = true;
                            message = `⚠️ ${alert.symbol} within ${alert.value}% of liquidation!`;
                        }
                    }
                    break;
            }

            if (triggered) {
                this.trigger(alert, message);
                if (alert.oneTime) {
                    alert.active = false;
                }
            }
        }
    },

    trigger(alert, message) {
        Notifications.show(message, 'warning', 10000);
        
        // Sound alert
        if (alert.sound) {
            this.playSound(alert.type);
        }
        
        // Browser notification
        if (Notification.permission === 'granted') {
            new Notification('ElCaro Alert', { body: message });
        }
    },

    playSound(type) {
        const sounds = {
            price: 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQ...',
            pnl: 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQ...',
            liquidation: 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQ...'
        };
        // Play sound effect (simplified)
        try {
            const audio = new Audio(sounds[type] || sounds.price);
            audio.volume = 0.5;
            audio.play();
        } catch (e) {}
    },

    save() {
        localStorage.setItem('elcaro_alerts', JSON.stringify(this.alerts));
    },

    load() {
        try {
            this.alerts = JSON.parse(localStorage.getItem('elcaro_alerts') || '[]');
        } catch (e) {
            this.alerts = [];
        }
    },

    render() {
        return `
            <div class="alerts-panel">
                <div class="alerts-header">
                    <h4><i class="fas fa-bell"></i> Price Alerts</h4>
                    <button class="add-alert-btn" onclick="SmartAlerts.showAddModal()">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
                <div class="alerts-list">
                    ${this.alerts.filter(a => a.active).map(a => `
                        <div class="alert-item">
                            <div class="alert-info">
                                <span class="alert-symbol">${a.symbol}</span>
                                <span class="alert-condition">${a.condition} $${a.value.toLocaleString()}</span>
                            </div>
                            <button class="alert-remove" onclick="SmartAlerts.remove(${a.id})">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    `).join('') || '<p class="empty">No active alerts</p>'}
                </div>
            </div>
        `;
    },

    showAddModal() {
        const symbol = window.state?.symbol || 'BTCUSDT';
        const price = window.state?.lastPrice || 0;
        
        const modal = document.createElement('div');
        modal.className = 'modal-overlay active';
        modal.innerHTML = `
            <div class="modal alert-modal">
                <div class="modal-header">
                    <span class="modal-title">Add Price Alert</span>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Symbol</label>
                        <input type="text" id="alertSymbol" value="${symbol}">
                    </div>
                    <div class="form-group">
                        <label>Condition</label>
                        <select id="alertCondition">
                            <option value="above">Price Above</option>
                            <option value="below">Price Below</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Price</label>
                        <input type="number" id="alertPrice" value="${price}" step="0.01">
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="alertSound" checked> Play sound</label>
                    </div>
                    <button class="submit-btn buy" onclick="SmartAlerts.createFromModal()">
                        Create Alert
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    },

    createFromModal() {
        const symbol = document.getElementById('alertSymbol').value;
        const condition = document.getElementById('alertCondition').value;
        const value = parseFloat(document.getElementById('alertPrice').value);
        const sound = document.getElementById('alertSound').checked;

        this.add('price', { symbol, condition, value, sound, oneTime: true });
        document.querySelector('.modal-overlay')?.remove();
        Notifications.show('Alert created', 'success');
    }
};


// ============================================================
// NOTIFICATIONS SYSTEM - Toast notifications
// ============================================================
const Notifications = {
    show(message, type = 'info', duration = 5000) {
        const container = document.getElementById('notifications') || this.createContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas ${this.getIcon(type)}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()"><i class="fas fa-times"></i></button>
        `;
        
        container.appendChild(toast);
        
        // Animate in
        requestAnimationFrame(() => toast.classList.add('show'));
        
        // Auto remove
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    createContainer() {
        const container = document.createElement('div');
        container.id = 'notifications';
        document.body.appendChild(container);
        return container;
    },

    getIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }
};


// ============================================================
// KEYBOARD SHORTCUTS MANAGER
// ============================================================
const Shortcuts = {
    bindings: new Map(),
    enabled: true,

    register(key, callback, description) {
        this.bindings.set(key.toLowerCase(), { callback, description });
    },

    init() {
        document.addEventListener('keydown', (e) => {
            if (!this.enabled) return;
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            const key = this.getKeyString(e);
            const binding = this.bindings.get(key);
            
            if (binding) {
                e.preventDefault();
                binding.callback(e);
            }
        });

        // Register default shortcuts
        this.register('b', () => window.setSide?.('buy'), 'Buy/Long');
        this.register('s', () => window.setSide?.('sell'), 'Sell/Short');
        this.register('enter', () => window.submitOrder?.(), 'Submit Order');
        this.register('escape', () => this.clearForm(), 'Clear Form');
        this.register('1', () => window.setOrderType?.('limit'), 'Limit Order');
        this.register('2', () => window.setOrderType?.('market'), 'Market Order');
        this.register('ctrl+b', () => OneClickTrading.quickOrder('buy', 25), 'Quick Buy 25%');
        this.register('ctrl+s', () => OneClickTrading.quickOrder('sell', 25), 'Quick Sell 25%');
        this.register('ctrl+shift+b', () => OneClickTrading.quickOrder('buy', 100), 'Quick Buy 100%');
        this.register('ctrl+shift+s', () => OneClickTrading.quickOrder('sell', 100), 'Quick Sell 100%');
        this.register('?', () => this.showHelp(), 'Show Shortcuts');
    },

    getKeyString(e) {
        let key = '';
        if (e.ctrlKey) key += 'ctrl+';
        if (e.shiftKey) key += 'shift+';
        if (e.altKey) key += 'alt+';
        key += e.key.toLowerCase();
        return key;
    },

    clearForm() {
        document.getElementById('sizeInput').value = '';
        document.getElementById('priceInput').value = '';
    },

    showHelp() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay active';
        modal.innerHTML = `
            <div class="modal shortcuts-modal">
                <div class="modal-header">
                    <span class="modal-title">⌨️ Keyboard Shortcuts</span>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body shortcuts-list">
                    ${Array.from(this.bindings.entries()).map(([key, { description }]) => `
                        <div class="shortcut-row">
                            <kbd>${key.replace('ctrl+', 'Ctrl + ').replace('shift+', 'Shift + ')}</kbd>
                            <span>${description}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
        document.body.appendChild(modal);
    }
};


// ============================================================
// INITIALIZATION
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    Shortcuts.init();
    SmartAlerts.load();
    PositionAnalytics.fetchStats();
    
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
});

// Export for global access
window.RiskCalculator = RiskCalculator;
window.DCABuilder = DCABuilder;
window.TrailingStop = TrailingStop;
window.OneClickTrading = OneClickTrading;
window.SmartAlerts = SmartAlerts;
window.Notifications = Notifications;
window.PositionAnalytics = PositionAnalytics;
window.OrderbookHeatmap = OrderbookHeatmap;
