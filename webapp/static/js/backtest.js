/**
 * Strategy Backtesting Engine
 * Test strategies on historical data
 */

class BacktestEngine {
    constructor() {
        this.strategies = [
            { id: 'elcaro', name: 'Elcaro Strategy', description: 'AI-powered signals' },
            { id: 'scryptomera', name: 'Scryptomera', description: 'Volume analysis' },
            { id: 'scalper', name: 'Scalper', description: 'Quick scalping' },
            { id: 'wyckoff', name: 'Wyckoff', description: 'Wyckoff accumulation/distribution' },
            { id: 'rsi_bb', name: 'RSI + BB', description: 'RSI with Bollinger Bands' }
        ];
        
        this.results = null;
        this.isRunning = false;
    }

    async init() {
        this.renderStrategySelector();
        this.bindEvents();
    }

    renderStrategySelector() {
        const container = document.getElementById('strategy-selector');
        if (!container) return;

        container.innerHTML = this.strategies.map(s => `
            <div class="strategy-option" data-id="${s.id}">
                <div class="strategy-icon">
                    <i class="fas fa-chart-line"></i>
                </div>
                <div class="strategy-info">
                    <h4>${s.name}</h4>
                    <p>${s.description}</p>
                </div>
                <div class="strategy-check">
                    <input type="checkbox" id="strat-${s.id}" name="strategies" value="${s.id}">
                </div>
            </div>
        `).join('');
    }

    bindEvents() {
        const runBtn = document.getElementById('run-backtest');
        if (runBtn) {
            runBtn.addEventListener('click', () => this.runBacktest());
        }

        // Strategy option click
        document.querySelectorAll('.strategy-option').forEach(el => {
            el.addEventListener('click', () => {
                const checkbox = el.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;
                el.classList.toggle('selected', checkbox.checked);
            });
        });
    }

    async runBacktest() {
        if (this.isRunning) return;

        // Get selected strategies
        const selectedStrategies = Array.from(document.querySelectorAll('input[name="strategies"]:checked'))
            .map(el => el.value);

        if (selectedStrategies.length === 0) {
            showToast('Please select at least one strategy', 'warning');
            return;
        }

        // Get parameters
        const params = {
            strategies: selectedStrategies,
            symbol: document.getElementById('bt-symbol')?.value || 'BTCUSDT',
            timeframe: document.getElementById('bt-timeframe')?.value || '1h',
            startDate: document.getElementById('bt-start')?.value || this.getDefaultStartDate(),
            endDate: document.getElementById('bt-end')?.value || new Date().toISOString().split('T')[0],
            initialBalance: parseFloat(document.getElementById('bt-balance')?.value || 10000),
            leverage: parseInt(document.getElementById('bt-leverage')?.value || 10),
            riskPerTrade: parseFloat(document.getElementById('bt-risk')?.value || 2)
        };

        this.isRunning = true;
        this.showProgress();

        try {
            const response = await fetch('/api/backtest/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(params)
            });

            const data = await response.json();

            if (data.success) {
                this.results = data.results;
                this.renderResults();
            } else {
                showToast(`Backtest failed: ${data.error}`, 'error');
            }
        } catch (e) {
            showToast('Failed to run backtest', 'error');
        } finally {
            this.isRunning = false;
            this.hideProgress();
        }
    }

    getDefaultStartDate() {
        const date = new Date();
        date.setMonth(date.getMonth() - 3);
        return date.toISOString().split('T')[0];
    }

    showProgress() {
        const container = document.getElementById('backtest-progress');
        if (container) {
            container.innerHTML = `
                <div class="progress-overlay">
                    <div class="progress-content">
                        <div class="spinner"></div>
                        <h3>Running Backtest...</h3>
                        <p>Analyzing historical data</p>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
            `;
            container.style.display = 'flex';
            
            // Animate progress
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 90) progress = 90;
                container.querySelector('.progress-fill').style.width = `${progress}%`;
                if (!this.isRunning) {
                    clearInterval(interval);
                    container.querySelector('.progress-fill').style.width = '100%';
                }
            }, 500);
        }
    }

    hideProgress() {
        const container = document.getElementById('backtest-progress');
        if (container) {
            container.style.display = 'none';
        }
    }

    renderResults() {
        if (!this.results) return;

        const container = document.getElementById('backtest-results');
        if (!container) return;

        const { summary, trades, equity } = this.results;

        container.innerHTML = `
            <div class="results-header">
                <h2>📊 Backtest Results</h2>
                <button class="btn btn-secondary" onclick="backtestEngine.exportResults()">
                    <i class="fas fa-download"></i> Export
                </button>
            </div>

            <!-- Summary Stats -->
            <div class="stats-grid">
                <div class="stat-card ${summary.totalPnL >= 0 ? 'profit' : 'loss'}">
                    <div class="stat-icon"><i class="fas fa-dollar-sign"></i></div>
                    <div class="stat-info">
                        <span class="stat-label">Total P&L</span>
                        <span class="stat-value">${summary.totalPnL >= 0 ? '+' : ''}$${summary.totalPnL.toFixed(2)}</span>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-percentage"></i></div>
                    <div class="stat-info">
                        <span class="stat-label">Return</span>
                        <span class="stat-value ${summary.returnPct >= 0 ? 'text-success' : 'text-danger'}">
                            ${summary.returnPct >= 0 ? '+' : ''}${summary.returnPct.toFixed(2)}%
                        </span>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-chart-bar"></i></div>
                    <div class="stat-info">
                        <span class="stat-label">Total Trades</span>
                        <span class="stat-value">${summary.totalTrades}</span>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-trophy"></i></div>
                    <div class="stat-info">
                        <span class="stat-label">Win Rate</span>
                        <span class="stat-value">${summary.winRate.toFixed(1)}%</span>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-balance-scale"></i></div>
                    <div class="stat-info">
                        <span class="stat-label">Profit Factor</span>
                        <span class="stat-value">${summary.profitFactor.toFixed(2)}</span>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-arrow-down"></i></div>
                    <div class="stat-info">
                        <span class="stat-label">Max Drawdown</span>
                        <span class="stat-value text-danger">${summary.maxDrawdown.toFixed(2)}%</span>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-fire"></i></div>
                    <div class="stat-info">
                        <span class="stat-label">Sharpe Ratio</span>
                        <span class="stat-value">${summary.sharpeRatio.toFixed(2)}</span>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-clock"></i></div>
                    <div class="stat-info">
                        <span class="stat-label">Avg Trade Duration</span>
                        <span class="stat-value">${summary.avgDuration}</span>
                    </div>
                </div>
            </div>

            <!-- Equity Curve -->
            <div class="results-section">
                <h3>📈 Equity Curve</h3>
                <div id="equity-chart" style="height: 400px;"></div>
            </div>

            <!-- Drawdown Chart -->
            <div class="results-section">
                <h3>📉 Drawdown</h3>
                <div id="drawdown-chart" style="height: 200px;"></div>
            </div>

            <!-- Monthly Returns -->
            <div class="results-section">
                <h3>📅 Monthly Returns</h3>
                <div class="monthly-grid" id="monthly-returns"></div>
            </div>

            <!-- Strategy Breakdown -->
            <div class="results-section">
                <h3>🎯 Strategy Performance</h3>
                <div class="strategy-breakdown">
                    ${this.renderStrategyBreakdown(summary.byStrategy)}
                </div>
            </div>

            <!-- Trade List -->
            <div class="results-section">
                <h3>📋 Trade History</h3>
                <div class="trades-table-container">
                    <table class="trades-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Time</th>
                                <th>Symbol</th>
                                <th>Side</th>
                                <th>Entry</th>
                                <th>Exit</th>
                                <th>Size</th>
                                <th>P&L</th>
                                <th>Strategy</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${trades.map((t, i) => `
                                <tr class="${t.pnl >= 0 ? 'profit' : 'loss'}">
                                    <td>${i + 1}</td>
                                    <td>${new Date(t.entryTime).toLocaleDateString()}</td>
                                    <td>${t.symbol}</td>
                                    <td class="${t.side === 'Long' ? 'text-success' : 'text-danger'}">
                                        ${t.side === 'Long' ? '🟢' : '🔴'} ${t.side}
                                    </td>
                                    <td>$${t.entryPrice.toLocaleString()}</td>
                                    <td>$${t.exitPrice.toLocaleString()}</td>
                                    <td>${t.size}</td>
                                    <td class="${t.pnl >= 0 ? 'text-success' : 'text-danger'}">
                                        ${t.pnl >= 0 ? '+' : ''}$${t.pnl.toFixed(2)}
                                    </td>
                                    <td><span class="strategy-tag">${t.strategy}</span></td>
                                    <td>
                                        <button class="btn btn-xs btn-ghost" onclick="backtestEngine.showTradeOnChart(${i})">
                                            <i class="fas fa-chart-line"></i>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        // Render charts
        this.renderEquityChart(equity);
        this.renderDrawdownChart(summary.drawdowns);
        this.renderMonthlyReturns(summary.monthlyReturns);
    }

    renderStrategyBreakdown(byStrategy) {
        if (!byStrategy) return '<p>No strategy data</p>';

        return Object.entries(byStrategy).map(([strategy, stats]) => `
            <div class="strategy-card">
                <div class="strategy-header">
                    <h4>${strategy}</h4>
                    <span class="${stats.pnl >= 0 ? 'text-success' : 'text-danger'}">
                        ${stats.pnl >= 0 ? '+' : ''}$${stats.pnl.toFixed(2)}
                    </span>
                </div>
                <div class="strategy-stats">
                    <div class="mini-stat">
                        <span>Trades</span>
                        <span>${stats.trades}</span>
                    </div>
                    <div class="mini-stat">
                        <span>Win Rate</span>
                        <span>${stats.winRate.toFixed(1)}%</span>
                    </div>
                    <div class="mini-stat">
                        <span>Avg PnL</span>
                        <span class="${stats.avgPnl >= 0 ? 'text-success' : 'text-danger'}">
                            $${stats.avgPnl.toFixed(2)}
                        </span>
                    </div>
                </div>
                <div class="win-loss-bar">
                    <div class="wins" style="width: ${stats.winRate}%"></div>
                    <div class="losses" style="width: ${100 - stats.winRate}%"></div>
                </div>
            </div>
        `).join('');
    }

    renderEquityChart(equity) {
        const container = document.getElementById('equity-chart');
        if (!container || !window.LightweightCharts) return;

        const chart = LightweightCharts.createChart(container, {
            layout: {
                background: { color: 'transparent' },
                textColor: '#a1a1aa'
            },
            grid: {
                vertLines: { color: '#27272a' },
                horzLines: { color: '#27272a' }
            },
            rightPriceScale: {
                borderColor: '#27272a'
            },
            timeScale: {
                borderColor: '#27272a'
            }
        });

        const areaSeries = chart.addAreaSeries({
            topColor: 'rgba(220, 38, 38, 0.4)',
            bottomColor: 'rgba(220, 38, 38, 0.0)',
            lineColor: '#dc2626',
            lineWidth: 2
        });

        areaSeries.setData(equity.map(e => ({
            time: e.time,
            value: e.value
        })));

        chart.timeScale().fitContent();
    }

    renderDrawdownChart(drawdowns) {
        const container = document.getElementById('drawdown-chart');
        if (!container || !window.LightweightCharts || !drawdowns) return;

        const chart = LightweightCharts.createChart(container, {
            layout: {
                background: { color: 'transparent' },
                textColor: '#a1a1aa'
            },
            grid: {
                vertLines: { color: '#27272a' },
                horzLines: { color: '#27272a' }
            }
        });

        const areaSeries = chart.addAreaSeries({
            topColor: 'rgba(239, 68, 68, 0.0)',
            bottomColor: 'rgba(239, 68, 68, 0.4)',
            lineColor: '#ef4444',
            lineWidth: 2
        });

        areaSeries.setData(drawdowns.map(d => ({
            time: d.time,
            value: -d.value
        })));

        chart.timeScale().fitContent();
    }

    renderMonthlyReturns(monthly) {
        const container = document.getElementById('monthly-returns');
        if (!container || !monthly) return;

        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const years = [...new Set(monthly.map(m => m.year))].sort();

        container.innerHTML = `
            <table class="monthly-table">
                <thead>
                    <tr>
                        <th>Year</th>
                        ${months.map(m => `<th>${m}</th>`).join('')}
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    ${years.map(year => {
                        const yearData = monthly.filter(m => m.year === year);
                        const total = yearData.reduce((sum, m) => sum + m.return, 0);
                        return `
                            <tr>
                                <td><strong>${year}</strong></td>
                                ${months.map((_, i) => {
                                    const monthData = yearData.find(m => m.month === i + 1);
                                    const ret = monthData?.return || 0;
                                    const color = ret > 0 ? 'profit' : ret < 0 ? 'loss' : '';
                                    return `<td class="${color}">${ret ? ret.toFixed(1) + '%' : '-'}</td>`;
                                }).join('')}
                                <td class="${total >= 0 ? 'profit' : 'loss'}">
                                    <strong>${total.toFixed(1)}%</strong>
                                </td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        `;
    }

    showTradeOnChart(tradeIndex) {
        const trade = this.results?.trades[tradeIndex];
        if (!trade) return;

        showModal('trade-chart', {
            title: `Trade #${tradeIndex + 1} - ${trade.symbol}`,
            size: 'large',
            content: `
                <div class="trade-chart-modal">
                    <div id="trade-detail-chart" style="height: 400px;"></div>
                    <div class="trade-detail-info">
                        <div class="info-grid">
                            <div class="info-item">
                                <label>Direction</label>
                                <span class="${trade.side === 'Long' ? 'text-success' : 'text-danger'}">
                                    ${trade.side === 'Long' ? '🟢 LONG' : '🔴 SHORT'}
                                </span>
                            </div>
                            <div class="info-item">
                                <label>Entry Price</label>
                                <span>$${trade.entryPrice.toLocaleString()}</span>
                            </div>
                            <div class="info-item">
                                <label>Exit Price</label>
                                <span>$${trade.exitPrice.toLocaleString()}</span>
                            </div>
                            <div class="info-item">
                                <label>Take Profit</label>
                                <span class="text-success">${trade.tp ? '$' + trade.tp.toLocaleString() : '-'}</span>
                            </div>
                            <div class="info-item">
                                <label>Stop Loss</label>
                                <span class="text-danger">${trade.sl ? '$' + trade.sl.toLocaleString() : '-'}</span>
                            </div>
                            <div class="info-item">
                                <label>P&L</label>
                                <span class="${trade.pnl >= 0 ? 'text-success' : 'text-danger'}">
                                    ${trade.pnl >= 0 ? '+' : ''}$${trade.pnl.toFixed(2)}
                                </span>
                            </div>
                            <div class="info-item">
                                <label>Duration</label>
                                <span>${trade.duration}</span>
                            </div>
                            <div class="info-item">
                                <label>Strategy</label>
                                <span class="strategy-tag">${trade.strategy}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `
        });

        // Render trade chart with entry/exit markers
        setTimeout(() => this.renderTradeChart(trade), 100);
    }

    renderTradeChart(trade) {
        const container = document.getElementById('trade-detail-chart');
        if (!container || !window.LightweightCharts) return;

        const chart = LightweightCharts.createChart(container, {
            layout: {
                background: { color: '#1a1a1a' },
                textColor: '#a1a1aa'
            },
            grid: {
                vertLines: { color: '#27272a' },
                horzLines: { color: '#27272a' }
            }
        });

        const candleSeries = chart.addCandlestickSeries();
        candleSeries.setData(trade.candles || []);

        // Add price lines
        candleSeries.createPriceLine({
            price: trade.entryPrice,
            color: '#dc2626',
            lineWidth: 2,
            lineStyle: 0,
            title: 'Entry'
        });

        candleSeries.createPriceLine({
            price: trade.exitPrice,
            color: trade.pnl >= 0 ? '#10b981' : '#ef4444',
            lineWidth: 2,
            lineStyle: 0,
            title: 'Exit'
        });

        if (trade.tp) {
            candleSeries.createPriceLine({
                price: trade.tp,
                color: '#10b981',
                lineWidth: 1,
                lineStyle: 2,
                title: 'TP'
            });
        }

        if (trade.sl) {
            candleSeries.createPriceLine({
                price: trade.sl,
                color: '#ef4444',
                lineWidth: 1,
                lineStyle: 2,
                title: 'SL'
            });
        }

        // Add markers
        candleSeries.setMarkers([
            {
                time: trade.entryTime,
                position: trade.side === 'Long' ? 'belowBar' : 'aboveBar',
                color: '#dc2626',
                shape: trade.side === 'Long' ? 'arrowUp' : 'arrowDown',
                text: 'Entry'
            },
            {
                time: trade.exitTime,
                position: trade.side === 'Long' ? 'aboveBar' : 'belowBar',
                color: trade.pnl >= 0 ? '#10b981' : '#ef4444',
                shape: trade.side === 'Long' ? 'arrowDown' : 'arrowUp',
                text: 'Exit'
            }
        ]);

        chart.timeScale().fitContent();
    }

    exportResults() {
        if (!this.results) return;

        const data = {
            summary: this.results.summary,
            trades: this.results.trades
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `backtest-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// Export
window.BacktestEngine = BacktestEngine;
const backtestEngine = new BacktestEngine();
