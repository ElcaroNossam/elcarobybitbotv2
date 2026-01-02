/**
 * Statistics Dashboard
 * Comprehensive trading statistics visualization
 */

class StatsDashboard {
    constructor() {
        this.data = null;
        this.filters = {
            exchange: 'all',
            strategy: 'all',
            period: '30d',
            symbol: 'all'
        };
    }

    async init() {
        await this.loadData();
        this.bindEvents();
        this.render();
    }

    async loadData() {
        try {
            const params = new URLSearchParams(this.filters);
            const response = await fetch(`/api/stats/dashboard?${params}`);
            const json = await response.json();
            
            if (json.success) {
                this.data = json.data;
            }
        } catch (e) {
            console.error('Failed to load stats:', e);
        }
    }

    bindEvents() {
        // Filter changes
        document.querySelectorAll('.stats-filter').forEach(el => {
            el.addEventListener('change', async () => {
                this.filters[el.name] = el.value;
                await this.loadData();
                this.render();
            });
        });

        // Period buttons
        document.querySelectorAll('.period-btn').forEach(el => {
            el.addEventListener('click', async () => {
                document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
                el.classList.add('active');
                this.filters.period = el.dataset.period;
                await this.loadData();
                this.render();
            });
        });
    }

    render() {
        if (!this.data) return;

        this.renderSummary();
        this.renderPnLChart();
        this.renderWinRateChart();
        this.renderByStrategy();
        this.renderByExchange();
        this.renderBySymbol();
        this.renderCalendar();
        this.renderTopTrades();
    }

    renderSummary() {
        const container = document.getElementById('stats-summary');
        if (!container) return;

        const s = this.data.summary;

        container.innerHTML = `
            <div class="summary-grid">
                <div class="summary-card main ${s.totalPnL >= 0 ? 'profit' : 'loss'}">
                    <div class="card-icon">
                        <i class="fas fa-wallet"></i>
                    </div>
                    <div class="card-content">
                        <span class="label">Total P&L</span>
                        <span class="value">${s.totalPnL >= 0 ? '+' : ''}$${s.totalPnL.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                        <span class="change ${s.pnlChange >= 0 ? 'up' : 'down'}">
                            <i class="fas fa-arrow-${s.pnlChange >= 0 ? 'up' : 'down'}"></i>
                            ${Math.abs(s.pnlChange).toFixed(2)}% vs prev period
                        </span>
                    </div>
                </div>
                
                <div class="summary-card">
                    <div class="card-icon trades">
                        <i class="fas fa-exchange-alt"></i>
                    </div>
                    <div class="card-content">
                        <span class="label">Total Trades</span>
                        <span class="value">${s.totalTrades}</span>
                        <div class="mini-bar">
                            <span class="wins" style="width: ${s.winRate}%">${s.wins} wins</span>
                            <span class="losses" style="width: ${100 - s.winRate}%">${s.losses} losses</span>
                        </div>
                    </div>
                </div>
                
                <div class="summary-card">
                    <div class="card-icon winrate">
                        <i class="fas fa-trophy"></i>
                    </div>
                    <div class="card-content">
                        <span class="label">Win Rate</span>
                        <span class="value">${s.winRate.toFixed(1)}%</span>
                        <div class="gauge">
                            <div class="gauge-fill" style="width: ${s.winRate}%"></div>
                        </div>
                    </div>
                </div>
                
                <div class="summary-card">
                    <div class="card-icon pf">
                        <i class="fas fa-balance-scale"></i>
                    </div>
                    <div class="card-content">
                        <span class="label">Profit Factor</span>
                        <span class="value">${s.profitFactor.toFixed(2)}</span>
                        <span class="hint">${s.profitFactor >= 1.5 ? '✅ Good' : s.profitFactor >= 1 ? '⚠️ Marginal' : '❌ Poor'}</span>
                    </div>
                </div>
                
                <div class="summary-card">
                    <div class="card-icon avg">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <div class="card-content">
                        <span class="label">Avg Win / Loss</span>
                        <div class="avg-values">
                            <span class="text-success">+$${s.avgWin.toFixed(2)}</span>
                            <span>/</span>
                            <span class="text-danger">-$${Math.abs(s.avgLoss).toFixed(2)}</span>
                        </div>
                    </div>
                </div>
                
                <div class="summary-card">
                    <div class="card-icon dd">
                        <i class="fas fa-arrow-down"></i>
                    </div>
                    <div class="card-content">
                        <span class="label">Max Drawdown</span>
                        <span class="value text-danger">${s.maxDrawdown.toFixed(2)}%</span>
                        <span class="hint">$${s.maxDrawdownAbs.toFixed(2)}</span>
                    </div>
                </div>
                
                <div class="summary-card">
                    <div class="card-icon streak">
                        <i class="fas fa-fire"></i>
                    </div>
                    <div class="card-content">
                        <span class="label">Best Streak</span>
                        <span class="value text-success">${s.bestStreak} wins</span>
                        <span class="hint">Worst: ${s.worstStreak} losses</span>
                    </div>
                </div>
                
                <div class="summary-card">
                    <div class="card-icon time">
                        <i class="fas fa-clock"></i>
                    </div>
                    <div class="card-content">
                        <span class="label">Avg Duration</span>
                        <span class="value">${s.avgDuration}</span>
                        <span class="hint">${s.tradesPerDay.toFixed(1)} trades/day</span>
                    </div>
                </div>
            </div>
        `;
    }

    renderPnLChart() {
        const container = document.getElementById('pnl-chart');
        if (!container || !window.LightweightCharts || !this.data.pnlHistory) return;

        container.innerHTML = '';
        
        const chart = LightweightCharts.createChart(container, {
            layout: { background: { color: 'transparent' }, textColor: '#a1a1aa' },
            grid: { vertLines: { color: '#27272a' }, horzLines: { color: '#27272a' } },
            rightPriceScale: { borderColor: '#27272a' },
            timeScale: { borderColor: '#27272a' }
        });

        // Cumulative PnL
        const areaSeries = chart.addAreaSeries({
            topColor: 'rgba(220, 38, 38, 0.4)',
            bottomColor: 'rgba(220, 38, 38, 0.0)',
            lineColor: '#dc2626',
            lineWidth: 2
        });

        areaSeries.setData(this.data.pnlHistory.map(p => ({
            time: p.date,
            value: p.cumulative
        })));

        // Daily PnL bars
        const histogramSeries = chart.addHistogramSeries({
            color: '#dc2626',
            priceFormat: { type: 'price' },
            priceScaleId: 'daily'
        });

        chart.priceScale('daily').applyOptions({
            scaleMargins: { top: 0.8, bottom: 0 }
        });

        histogramSeries.setData(this.data.pnlHistory.map(p => ({
            time: p.date,
            value: p.daily,
            color: p.daily >= 0 ? '#10b981' : '#ef4444'
        })));

        chart.timeScale().fitContent();
    }

    renderWinRateChart() {
        const container = document.getElementById('winrate-chart');
        if (!container || !this.data.winRateHistory) return;

        // Create donut chart with Chart.js or custom SVG
        const current = this.data.summary.winRate;
        
        container.innerHTML = `
            <div class="donut-chart">
                <svg viewBox="0 0 36 36">
                    <path class="bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    <path class="fill" stroke-dasharray="${current}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    <text x="18" y="20.35" class="percentage">${current.toFixed(0)}%</text>
                </svg>
                <div class="legend">
                    <div class="legend-item wins">
                        <span class="dot"></span>
                        <span>Wins: ${this.data.summary.wins}</span>
                    </div>
                    <div class="legend-item losses">
                        <span class="dot"></span>
                        <span>Losses: ${this.data.summary.losses}</span>
                    </div>
                </div>
            </div>
        `;
    }

    renderByStrategy() {
        const container = document.getElementById('stats-by-strategy');
        if (!container || !this.data.byStrategy) return;

        container.innerHTML = Object.entries(this.data.byStrategy).map(([name, stats]) => `
            <div class="strategy-row">
                <div class="strategy-name">
                    <span class="icon" style="background: ${this.getStrategyColor(name)}">
                        ${name.charAt(0).toUpperCase()}
                    </span>
                    <span>${name}</span>
                </div>
                <div class="strategy-trades">${stats.trades} trades</div>
                <div class="strategy-winrate">
                    <div class="mini-gauge">
                        <div class="fill" style="width: ${stats.winRate}%"></div>
                    </div>
                    <span>${stats.winRate.toFixed(0)}%</span>
                </div>
                <div class="strategy-pnl ${stats.pnl >= 0 ? 'profit' : 'loss'}">
                    ${stats.pnl >= 0 ? '+' : ''}$${stats.pnl.toFixed(2)}
                </div>
            </div>
        `).join('');
    }

    renderByExchange() {
        const container = document.getElementById('stats-by-exchange');
        if (!container || !this.data.byExchange) return;

        const exchangeColors = {
            bybit: '#f7931a',
            hyperliquid: '#00d4ff'
        };

        container.innerHTML = Object.entries(this.data.byExchange).map(([name, stats]) => `
            <div class="exchange-card" style="border-color: ${exchangeColors[name] || '#dc2626'}">
                <div class="exchange-header">
                    <span class="exchange-name" style="color: ${exchangeColors[name] || '#dc2626'}">
                        ${name === 'bybit' ? '🟠' : '🔷'} ${name.charAt(0).toUpperCase() + name.slice(1)}
                    </span>
                </div>
                <div class="exchange-stats">
                    <div class="stat">
                        <span class="label">Trades</span>
                        <span class="value">${stats.trades}</span>
                    </div>
                    <div class="stat">
                        <span class="label">Win Rate</span>
                        <span class="value">${stats.winRate.toFixed(0)}%</span>
                    </div>
                    <div class="stat">
                        <span class="label">P&L</span>
                        <span class="value ${stats.pnl >= 0 ? 'text-success' : 'text-danger'}">
                            ${stats.pnl >= 0 ? '+' : ''}$${stats.pnl.toFixed(2)}
                        </span>
                    </div>
                    <div class="stat">
                        <span class="label">Avg Trade</span>
                        <span class="value ${stats.avgPnl >= 0 ? 'text-success' : 'text-danger'}">
                            $${stats.avgPnl.toFixed(2)}
                        </span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderBySymbol() {
        const container = document.getElementById('stats-by-symbol');
        if (!container || !this.data.bySymbol) return;

        const sorted = Object.entries(this.data.bySymbol)
            .sort((a, b) => b[1].pnl - a[1].pnl);

        container.innerHTML = `
            <div class="symbols-grid">
                ${sorted.slice(0, 10).map(([symbol, stats]) => `
                    <div class="symbol-card ${stats.pnl >= 0 ? 'profit' : 'loss'}">
                        <div class="symbol-name">${symbol}</div>
                        <div class="symbol-pnl">${stats.pnl >= 0 ? '+' : ''}$${stats.pnl.toFixed(2)}</div>
                        <div class="symbol-meta">
                            <span>${stats.trades} trades</span>
                            <span>${stats.winRate.toFixed(0)}% WR</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderCalendar() {
        const container = document.getElementById('pnl-calendar');
        if (!container || !this.data.dailyPnL) return;

        const today = new Date();
        const daysInMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1).getDay();

        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        
        let calendarHTML = `
            <div class="calendar-header">
                ${days.map(d => `<div class="day-name">${d}</div>`).join('')}
            </div>
            <div class="calendar-grid">
        `;

        // Empty cells for days before month starts
        for (let i = 0; i < firstDay; i++) {
            calendarHTML += '<div class="calendar-day empty"></div>';
        }

        // Days of month
        for (let day = 1; day <= daysInMonth; day++) {
            const dateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const pnl = this.data.dailyPnL[dateStr] || 0;
            const intensity = Math.min(Math.abs(pnl) / 100, 1);
            const colorClass = pnl > 0 ? 'profit' : pnl < 0 ? 'loss' : '';
            
            calendarHTML += `
                <div class="calendar-day ${colorClass}" style="--intensity: ${intensity}" title="${dateStr}: $${pnl.toFixed(2)}">
                    <span class="day-num">${day}</span>
                    ${pnl !== 0 ? `<span class="day-pnl">${pnl > 0 ? '+' : ''}${pnl.toFixed(0)}</span>` : ''}
                </div>
            `;
        }

        calendarHTML += '</div>';
        container.innerHTML = calendarHTML;
    }

    renderTopTrades() {
        const container = document.getElementById('top-trades');
        if (!container || !this.data.topTrades) return;

        container.innerHTML = `
            <div class="top-trades-section">
                <h4>🏆 Best Trades</h4>
                <div class="trades-list">
                    ${this.data.topTrades.best.slice(0, 5).map(t => `
                        <div class="trade-item profit">
                            <span class="symbol">${t.symbol}</span>
                            <span class="pnl">+$${t.pnl.toFixed(2)}</span>
                            <span class="strategy">${t.strategy}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div class="top-trades-section">
                <h4>💀 Worst Trades</h4>
                <div class="trades-list">
                    ${this.data.topTrades.worst.slice(0, 5).map(t => `
                        <div class="trade-item loss">
                            <span class="symbol">${t.symbol}</span>
                            <span class="pnl">-$${Math.abs(t.pnl).toFixed(2)}</span>
                            <span class="strategy">${t.strategy}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    getStrategyColor(name) {
        const colors = {
            elcaro: '#dc2626',
            scryptomera: '#991b1b',
            scalper: '#d4a017',
            wyckoff: '#f59e0b',
            rsi_bb: '#10b981'
        };
        return colors[name.toLowerCase()] || '#71717a';
    }
}

// Export
window.StatsDashboard = StatsDashboard;
const statsDashboard = new StatsDashboard();
