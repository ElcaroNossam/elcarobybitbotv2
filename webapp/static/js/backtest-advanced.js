/**
 * ElCaro Advanced Backtest System v2.0
 * Live Strategy Execution with Real-time Chart Visualization
 */

class BacktestAdvanced {
    constructor() {
        this.ws = null;
        this.liveSession = null;
        this.chart = null;
        this.trades = [];
        this.signals = [];
        this.equityCurve = [];
        this.isLiveMode = false;
        this.currentStrategy = null;
        this.audioNotify = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1qYmlhX2RdXF1fY2VpbnN5f4WKjpCTlpaWlJGNiIODhH9+fHl4d3Z1dHR0dHZ3eXx/goaJjI6QkZGQjouIhYN+fHp4d3Z2dnZ3eHp8f4KFiIuNj5CQj42KhoOAfXp4dnV0dHR0dXZ4en2AhIeKjI6PkI+OjImGg398eXd2dXR0dHV2d3l7foGEh4qMjo+Pjo2KhoOAfXp4dnV0dHR0dXZ4');
        
        this.initWebSocket();
    }

    initWebSocket() {
        const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.ws = new WebSocket(`${proto}//${location.host}/ws/backtest-live`);
        
        this.ws.onopen = () => {
            console.log('[Backtest WS] Connected');
            this.updateConnectionStatus(true);
        };
        
        this.ws.onmessage = (e) => {
            const data = JSON.parse(e.data);
            this.handleMessage(data);
        };
        
        this.ws.onclose = () => {
            console.log('[Backtest WS] Disconnected');
            this.updateConnectionStatus(false);
            setTimeout(() => this.initWebSocket(), 3000);
        };
    }

    handleMessage(data) {
        switch (data.type) {
            case 'candle':
                this.onNewCandle(data.data);
                break;
            case 'signal':
                this.onSignal(data.data);
                break;
            case 'trade':
                this.onTrade(data.data);
                break;
            case 'analysis':
                this.onAnalysis(data.data);
                break;
            case 'session_update':
                this.onSessionUpdate(data.data);
                break;
            case 'error':
                this.showError(data.message);
                break;
        }
    }

    // Start Live Strategy Execution
    async startLiveSession(config) {
        this.liveSession = {
            strategy: config.strategy,
            symbol: config.symbol,
            timeframe: config.timeframe,
            params: config.params,
            startTime: Date.now(),
            trades: [],
            signals: [],
            equity: config.initial_balance || 10000
        };
        
        this.isLiveMode = true;
        this.currentStrategy = config.strategy;
        
        // Request to start live stream
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'start_live',
                strategy: config.strategy,
                symbol: config.symbol,
                timeframe: config.timeframe,
                params: config.params
            }));
        }
        
        this.showLivePanel();
        this.updateLiveStatus('Running');
        
        // Initialize chart for live mode
        await this.initLiveChart(config.symbol, config.timeframe);
    }

    stopLiveSession() {
        this.isLiveMode = false;
        
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'stop_live' }));
        }
        
        this.updateLiveStatus('Stopped');
        this.generateSessionReport();
    }

    // Real-time candle update
    onNewCandle(candle) {
        if (!this.isLiveMode) return;
        
        // Add candle to chart
        if (this.chart) {
            this.chart.addCandle(candle);
        }
        
        // Update current price display
        this.updatePriceDisplay(candle);
    }

    // Strategy signal received
    onSignal(signal) {
        this.signals.push(signal);
        
        // Draw signal on chart
        if (this.chart) {
            this.chart.addSignal(signal);
        }
        
        // Show signal notification
        this.showSignalNotification(signal);
        
        // Update signals list
        this.updateSignalsList();
    }

    // Trade executed
    onTrade(trade) {
        this.trades.push(trade);
        
        // Update equity curve
        if (this.liveSession) {
            this.liveSession.equity += trade.pnl;
            this.equityCurve.push({
                time: Date.now(),
                equity: this.liveSession.equity
            });
        }
        
        // Draw trade on chart
        if (this.chart) {
            this.chart.addTrade(trade);
        }
        
        // Update stats
        this.updateLiveStats();
        
        // Add to trades table
        this.addTradeToTable(trade);
        
        // Play sound
        if (trade.pnl > 0) {
            this.playSound('win');
        } else {
            this.playSound('loss');
        }
    }

    // Real-time analysis data (indicators, patterns)
    onAnalysis(analysis) {
        // Update indicator values display
        this.updateIndicatorDisplay(analysis);
        
        // Draw indicators on chart
        if (this.chart && analysis.indicators) {
            this.chart.updateIndicators(analysis.indicators);
        }
        
        // Update pattern detection
        if (analysis.patterns) {
            this.updatePatternDisplay(analysis.patterns);
        }
        
        // Update sentiment
        if (analysis.sentiment) {
            this.updateSentimentGauge(analysis.sentiment);
        }
    }

    // Session progress update
    onSessionUpdate(update) {
        document.getElementById('liveProgress')?.style.setProperty('--progress', update.progress + '%');
        document.getElementById('liveProgressText')?.textContent = `${update.progress.toFixed(1)}%`;
    }

    // Initialize live chart with TradingView integration
    async initLiveChart(symbol, timeframe) {
        // Create TradingView widget if available
        const container = document.getElementById('liveChartContainer');
        if (!container) return;
        
        container.innerHTML = '';
        
        // Create lightweight chart for live updates
        const chartDiv = document.createElement('div');
        chartDiv.id = 'liveChart';
        chartDiv.style.cssText = 'width: 100%; height: 100%;';
        container.appendChild(chartDiv);
        
        // Load TradingView lightweight charts
        if (typeof LightweightCharts !== 'undefined') {
            this.chart = new LiveTradingChart('liveChart', symbol, timeframe);
        } else {
            // Fallback: Load library dynamically
            await this.loadChartLibrary();
            this.chart = new LiveTradingChart('liveChart', symbol, timeframe);
        }
    }

    async loadChartLibrary() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    // Update displays
    updatePriceDisplay(candle) {
        const el = document.getElementById('liveCurrentPrice');
        if (el) {
            el.textContent = '$' + candle.close.toFixed(2);
            el.className = candle.close >= candle.open ? 'price-up' : 'price-down';
        }
    }

    updateIndicatorDisplay(analysis) {
        const container = document.getElementById('liveIndicators');
        if (!container) return;
        
        let html = '';
        
        if (analysis.rsi) {
            const rsiClass = analysis.rsi > 70 ? 'overbought' : analysis.rsi < 30 ? 'oversold' : 'neutral';
            html += `<div class="indicator-item ${rsiClass}">
                <span class="indicator-label">RSI</span>
                <span class="indicator-value">${analysis.rsi.toFixed(1)}</span>
            </div>`;
        }
        
        if (analysis.macd) {
            const macdClass = analysis.macd.histogram > 0 ? 'bullish' : 'bearish';
            html += `<div class="indicator-item ${macdClass}">
                <span class="indicator-label">MACD</span>
                <span class="indicator-value">${analysis.macd.value.toFixed(2)}</span>
            </div>`;
        }
        
        if (analysis.bb) {
            const bbPos = ((analysis.price - analysis.bb.lower) / (analysis.bb.upper - analysis.bb.lower) * 100).toFixed(0);
            html += `<div class="indicator-item">
                <span class="indicator-label">BB %</span>
                <span class="indicator-value">${bbPos}%</span>
            </div>`;
        }
        
        if (analysis.volume_delta) {
            const vdClass = analysis.volume_delta > 0 ? 'bullish' : 'bearish';
            html += `<div class="indicator-item ${vdClass}">
                <span class="indicator-label">V.Delta</span>
                <span class="indicator-value">${analysis.volume_delta > 0 ? '+' : ''}${(analysis.volume_delta / 1000).toFixed(1)}K</span>
            </div>`;
        }
        
        if (analysis.oi_change) {
            const oiClass = analysis.oi_change > 0 ? 'bullish' : 'bearish';
            html += `<div class="indicator-item ${oiClass}">
                <span class="indicator-label">OI Δ</span>
                <span class="indicator-value">${analysis.oi_change > 0 ? '+' : ''}${analysis.oi_change.toFixed(2)}%</span>
            </div>`;
        }
        
        container.innerHTML = html;
    }

    updatePatternDisplay(patterns) {
        const container = document.getElementById('livePatterns');
        if (!container) return;
        
        container.innerHTML = patterns.map(p => `
            <div class="pattern-item ${p.direction}">
                <span class="pattern-icon">${p.direction === 'bullish' ? '🟢' : '🔴'}</span>
                <span class="pattern-name">${p.name}</span>
                <span class="pattern-confidence">${(p.confidence * 100).toFixed(0)}%</span>
            </div>
        `).join('');
    }

    updateSentimentGauge(sentiment) {
        const gauge = document.getElementById('sentimentGauge');
        if (!gauge) return;
        
        const needle = gauge.querySelector('.gauge-needle');
        const value = gauge.querySelector('.gauge-value');
        
        // Sentiment: -100 to +100
        const rotation = (sentiment / 100) * 90; // -90 to +90 degrees
        needle.style.transform = `rotate(${rotation}deg)`;
        
        value.textContent = sentiment > 0 ? `+${sentiment.toFixed(0)}` : sentiment.toFixed(0);
        value.className = 'gauge-value ' + (sentiment > 0 ? 'bullish' : sentiment < 0 ? 'bearish' : 'neutral');
    }

    updateLiveStats() {
        const trades = this.trades;
        if (!trades.length) return;
        
        const wins = trades.filter(t => t.pnl > 0);
        const losses = trades.filter(t => t.pnl < 0);
        const winRate = (wins.length / trades.length * 100).toFixed(1);
        const totalPnl = trades.reduce((s, t) => s + t.pnl, 0);
        const avgWin = wins.length ? wins.reduce((s, t) => s + t.pnl, 0) / wins.length : 0;
        const avgLoss = losses.length ? Math.abs(losses.reduce((s, t) => s + t.pnl, 0) / losses.length) : 0;
        const profitFactor = avgLoss ? avgWin / avgLoss : avgWin > 0 ? 999 : 0;
        
        this.setElementText('liveTotalTrades', trades.length);
        this.setElementText('liveWinRate', winRate + '%');
        this.setElementText('livePnL', (totalPnl >= 0 ? '+$' : '-$') + Math.abs(totalPnl).toFixed(2));
        this.setElementText('liveProfitFactor', profitFactor.toFixed(2));
        
        if (this.liveSession) {
            this.setElementText('liveEquity', '$' + this.liveSession.equity.toFixed(2));
        }
    }

    updateSignalsList() {
        const container = document.getElementById('liveSignalsList');
        if (!container) return;
        
        const recent = this.signals.slice(-10).reverse();
        
        container.innerHTML = recent.map(s => `
            <div class="signal-item ${s.direction.toLowerCase()}">
                <div class="signal-time">${new Date(s.time).toLocaleTimeString()}</div>
                <div class="signal-direction">${s.direction}</div>
                <div class="signal-reason">${s.reason}</div>
                <div class="signal-confidence">${(s.confidence * 100).toFixed(0)}%</div>
            </div>
        `).join('');
    }

    addTradeToTable(trade) {
        const tbody = document.getElementById('liveTradesTableBody');
        if (!tbody) return;
        
        const row = document.createElement('tr');
        row.className = trade.pnl >= 0 ? 'trade-win' : 'trade-loss';
        row.innerHTML = `
            <td>${new Date(trade.entry_time).toLocaleTimeString()}</td>
            <td><span class="badge ${trade.direction.toLowerCase()}">${trade.direction}</span></td>
            <td>$${trade.entry_price.toFixed(2)}</td>
            <td>$${trade.exit_price.toFixed(2)}</td>
            <td class="${trade.pnl >= 0 ? 'positive' : 'negative'}">
                ${trade.pnl >= 0 ? '+' : ''}$${trade.pnl.toFixed(2)}
            </td>
            <td>${trade.reason}</td>
        `;
        
        tbody.insertBefore(row, tbody.firstChild);
        
        // Keep only last 20 trades visible
        while (tbody.children.length > 20) {
            tbody.removeChild(tbody.lastChild);
        }
    }

    showSignalNotification(signal) {
        const container = document.getElementById('signalNotifications');
        if (!container) return;
        
        const notif = document.createElement('div');
        notif.className = `signal-notification ${signal.direction.toLowerCase()}`;
        notif.innerHTML = `
            <div class="signal-notif-icon">${signal.direction === 'LONG' ? '🚀' : '📉'}</div>
            <div class="signal-notif-content">
                <strong>${signal.direction} Signal</strong>
                <span>${signal.reason}</span>
            </div>
            <div class="signal-notif-confidence">${(signal.confidence * 100).toFixed(0)}%</div>
        `;
        
        container.appendChild(notif);
        
        // Auto-remove after 5 seconds
        setTimeout(() => notif.remove(), 5000);
        
        this.playSound('signal');
    }

    showLivePanel() {
        document.getElementById('backtestResults')?.style.setProperty('display', 'none');
        document.getElementById('livePanel')?.style.setProperty('display', 'block');
    }

    updateLiveStatus(status) {
        const el = document.getElementById('liveStatus');
        if (el) {
            el.textContent = status;
            el.className = 'live-status ' + status.toLowerCase();
        }
    }

    updateConnectionStatus(connected) {
        const el = document.getElementById('wsLiveStatus');
        if (el) {
            el.classList.toggle('connected', connected);
        }
    }

    generateSessionReport() {
        if (!this.liveSession) return;
        
        const report = {
            strategy: this.liveSession.strategy,
            symbol: this.liveSession.symbol,
            duration: Date.now() - this.liveSession.startTime,
            trades: this.trades,
            signals: this.signals,
            final_equity: this.liveSession.equity,
            equity_curve: this.equityCurve
        };
        
        // Show report modal
        this.showReportModal(report);
    }

    showReportModal(report) {
        const wins = report.trades.filter(t => t.pnl > 0);
        const losses = report.trades.filter(t => t.pnl < 0);
        const totalPnl = report.trades.reduce((s, t) => s + t.pnl, 0);
        const winRate = report.trades.length ? (wins.length / report.trades.length * 100) : 0;
        
        const modal = document.createElement('div');
        modal.className = 'report-modal-overlay';
        modal.innerHTML = `
            <div class="report-modal">
                <div class="report-header">
                    <h2>📊 Live Session Report</h2>
                    <button class="close-btn" onclick="this.closest('.report-modal-overlay').remove()">×</button>
                </div>
                <div class="report-body">
                    <div class="report-summary">
                        <div class="report-stat">
                            <span class="label">Strategy</span>
                            <span class="value">${report.strategy}</span>
                        </div>
                        <div class="report-stat">
                            <span class="label">Duration</span>
                            <span class="value">${this.formatDuration(report.duration)}</span>
                        </div>
                        <div class="report-stat">
                            <span class="label">Trades</span>
                            <span class="value">${report.trades.length}</span>
                        </div>
                        <div class="report-stat">
                            <span class="label">Win Rate</span>
                            <span class="value ${winRate >= 50 ? 'positive' : 'negative'}">${winRate.toFixed(1)}%</span>
                        </div>
                        <div class="report-stat">
                            <span class="label">Total P&L</span>
                            <span class="value ${totalPnl >= 0 ? 'positive' : 'negative'}">
                                ${totalPnl >= 0 ? '+' : ''}$${totalPnl.toFixed(2)}
                            </span>
                        </div>
                        <div class="report-stat">
                            <span class="label">Final Equity</span>
                            <span class="value">$${report.final_equity.toFixed(2)}</span>
                        </div>
                    </div>
                    <div class="report-actions">
                        <button class="btn btn-primary" onclick="backtestAdvanced.exportSession()">
                            <i class="fas fa-download"></i> Export
                        </button>
                        <button class="btn btn-success" onclick="backtestAdvanced.deployStrategy()">
                            <i class="fas fa-rocket"></i> Deploy to Bot
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    async deployStrategy() {
        if (!this.currentStrategy || !this.liveSession) {
            this.showError('No strategy to deploy');
            return;
        }
        
        try {
            const response = await fetch('/api/backtest/deploy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    strategy: this.currentStrategy,
                    params: this.liveSession.params,
                    backtest_results: {
                        trades: this.trades.length,
                        win_rate: this.trades.length ? 
                            (this.trades.filter(t => t.pnl > 0).length / this.trades.length * 100) : 0,
                        pnl: this.trades.reduce((s, t) => s + t.pnl, 0)
                    }
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Strategy deployed successfully! Bot will use these settings.');
            } else {
                this.showError(data.error || 'Failed to deploy strategy');
            }
        } catch (e) {
            this.showError('Deploy failed: ' + e.message);
        }
    }

    exportSession() {
        const data = {
            session: this.liveSession,
            trades: this.trades,
            signals: this.signals,
            equity_curve: this.equityCurve,
            exported_at: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `backtest_session_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    // Utilities
    setElementText(id, text) {
        const el = document.getElementById(id);
        if (el) el.textContent = text;
    }

    formatDuration(ms) {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        
        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    }

    playSound(type) {
        try {
            this.audioNotify.play();
        } catch (e) {
            // Ignore audio errors
        }
    }

    showError(msg) {
        console.error('[Backtest]', msg);
        // Use notification system if available
        if (typeof Notifications !== 'undefined') {
            Notifications.show(msg, 'error');
        } else {
            alert(msg);
        }
    }

    showSuccess(msg) {
        console.log('[Backtest]', msg);
        if (typeof Notifications !== 'undefined') {
            Notifications.show(msg, 'success');
        }
    }
}

/**
 * Live Trading Chart with Signals
 */
class LiveTradingChart {
    constructor(containerId, symbol, timeframe) {
        this.container = document.getElementById(containerId);
        this.symbol = symbol;
        this.timeframe = timeframe;
        this.candles = [];
        this.trades = [];
        this.signals = [];
        this.indicators = {};
        
        this.initChart();
    }

    initChart() {
        if (typeof LightweightCharts === 'undefined') {
            console.error('LightweightCharts not loaded');
            return;
        }
        
        this.chart = LightweightCharts.createChart(this.container, {
            layout: {
                background: { color: 'transparent' },
                textColor: '#a0a0b0',
            },
            grid: {
                vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
                horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            timeScale: {
                timeVisible: true,
                secondsVisible: false,
            },
        });
        
        // Candlestick series
        this.candleSeries = this.chart.addCandlestickSeries({
            upColor: '#22c55e',
            downColor: '#ef4444',
            borderUpColor: '#22c55e',
            borderDownColor: '#ef4444',
            wickUpColor: '#22c55e',
            wickDownColor: '#ef4444',
        });
        
        // Volume series
        this.volumeSeries = this.chart.addHistogramSeries({
            color: '#6366f1',
            priceFormat: { type: 'volume' },
            priceScaleId: '',
            scaleMargins: { top: 0.8, bottom: 0 },
        });
        
        // Resize handler
        new ResizeObserver(() => {
            this.chart.applyOptions({ 
                width: this.container.clientWidth,
                height: this.container.clientHeight 
            });
        }).observe(this.container);
    }

    addCandle(candle) {
        const candleData = {
            time: candle.timestamp / 1000,
            open: candle.open,
            high: candle.high,
            low: candle.low,
            close: candle.close,
        };
        
        this.candleSeries.update(candleData);
        
        this.volumeSeries.update({
            time: candle.timestamp / 1000,
            value: candle.volume,
            color: candle.close >= candle.open ? 'rgba(34, 197, 94, 0.5)' : 'rgba(239, 68, 68, 0.5)',
        });
        
        this.candles.push(candle);
    }

    addSignal(signal) {
        const marker = {
            time: signal.timestamp / 1000,
            position: signal.direction === 'LONG' ? 'belowBar' : 'aboveBar',
            color: signal.direction === 'LONG' ? '#22c55e' : '#ef4444',
            shape: signal.direction === 'LONG' ? 'arrowUp' : 'arrowDown',
            text: signal.direction,
        };
        
        this.signals.push(marker);
        this.candleSeries.setMarkers(this.signals);
    }

    addTrade(trade) {
        // Add entry marker
        const entryMarker = {
            time: new Date(trade.entry_time).getTime() / 1000,
            position: trade.direction === 'LONG' ? 'belowBar' : 'aboveBar',
            color: '#6366f1',
            shape: 'circle',
            text: 'Entry',
        };
        
        // Add exit marker
        const exitMarker = {
            time: new Date(trade.exit_time).getTime() / 1000,
            position: trade.direction === 'LONG' ? 'aboveBar' : 'belowBar',
            color: trade.pnl >= 0 ? '#22c55e' : '#ef4444',
            shape: 'circle',
            text: trade.reason,
        };
        
        this.signals.push(entryMarker, exitMarker);
        this.candleSeries.setMarkers(this.signals);
        
        // Draw line between entry and exit
        this.addTradeLine(trade);
    }

    addTradeLine(trade) {
        // Create line series for this trade
        const lineSeries = this.chart.addLineSeries({
            color: trade.pnl >= 0 ? '#22c55e' : '#ef4444',
            lineWidth: 2,
            lineStyle: LightweightCharts.LineStyle.Dashed,
        });
        
        lineSeries.setData([
            { time: new Date(trade.entry_time).getTime() / 1000, value: trade.entry_price },
            { time: new Date(trade.exit_time).getTime() / 1000, value: trade.exit_price },
        ]);
    }

    updateIndicators(indicators) {
        // RSI line
        if (indicators.rsi && !this.indicators.rsi) {
            this.indicators.rsi = this.chart.addLineSeries({
                color: '#f59e0b',
                lineWidth: 1,
                priceScaleId: 'rsi',
            });
        }
        
        if (indicators.rsi && this.indicators.rsi) {
            this.indicators.rsi.update({
                time: indicators.time / 1000,
                value: indicators.rsi,
            });
        }
        
        // EMA lines
        if (indicators.ema20 && !this.indicators.ema20) {
            this.indicators.ema20 = this.chart.addLineSeries({
                color: '#3b82f6',
                lineWidth: 1,
            });
        }
        
        if (indicators.ema20 && this.indicators.ema20) {
            this.indicators.ema20.update({
                time: indicators.time / 1000,
                value: indicators.ema20,
            });
        }
        
        if (indicators.ema50 && !this.indicators.ema50) {
            this.indicators.ema50 = this.chart.addLineSeries({
                color: '#8b5cf6',
                lineWidth: 1,
            });
        }
        
        if (indicators.ema50 && this.indicators.ema50) {
            this.indicators.ema50.update({
                time: indicators.time / 1000,
                value: indicators.ema50,
            });
        }
    }
}

// Strategy Replay System - replay historical data with real-time visualization
class StrategyReplay {
    constructor(backtestAdvanced) {
        this.backtest = backtestAdvanced;
        this.isPlaying = false;
        this.speed = 1;
        this.currentIndex = 0;
        this.candles = [];
        this.signals = [];
    }

    async load(strategy, symbol, timeframe, days) {
        try {
            const response = await fetch('/api/backtest/replay-data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ strategy, symbol, timeframe, days })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.candles = data.candles;
                this.signals = data.signals;
                this.trades = data.trades;
                this.currentIndex = 0;
                return true;
            }
            
            return false;
        } catch (e) {
            console.error('Failed to load replay data:', e);
            return false;
        }
    }

    play() {
        this.isPlaying = true;
        this.tick();
    }

    pause() {
        this.isPlaying = false;
    }

    setSpeed(speed) {
        this.speed = speed;
    }

    tick() {
        if (!this.isPlaying || this.currentIndex >= this.candles.length) {
            this.isPlaying = false;
            return;
        }
        
        const candle = this.candles[this.currentIndex];
        this.backtest.onNewCandle(candle);
        
        // Check for signals at this candle
        const signal = this.signals.find(s => s.candle_index === this.currentIndex);
        if (signal) {
            this.backtest.onSignal(signal);
        }
        
        // Check for trades at this candle
        const trade = this.trades.find(t => t.exit_candle_index === this.currentIndex);
        if (trade) {
            this.backtest.onTrade(trade);
        }
        
        this.currentIndex++;
        
        // Update progress
        const progress = (this.currentIndex / this.candles.length) * 100;
        document.getElementById('replayProgress')?.style.setProperty('--progress', progress + '%');
        
        // Schedule next tick based on speed
        setTimeout(() => this.tick(), 100 / this.speed);
    }

    seekTo(percent) {
        this.currentIndex = Math.floor(this.candles.length * (percent / 100));
    }
}

// Initialize
let backtestAdvanced;
let strategyReplay;

document.addEventListener('DOMContentLoaded', () => {
    backtestAdvanced = new BacktestAdvanced();
    strategyReplay = new StrategyReplay(backtestAdvanced);
});

// Global functions for HTML onclick handlers
function startLiveMode() {
    const config = {
        strategy: document.getElementById('liveStrategy')?.value || 'elcaro',
        symbol: document.getElementById('symbol')?.value || 'BTCUSDT',
        timeframe: document.getElementById('timeframe')?.value || '1h',
        params: {
            stop_loss_percent: parseFloat(document.getElementById('stopLoss')?.value || 2),
            take_profit_percent: parseFloat(document.getElementById('takeProfit')?.value || 4),
            risk_per_trade: parseFloat(document.getElementById('riskPerTrade')?.value || 1),
        },
        initial_balance: parseFloat(document.getElementById('initialBalance')?.value || 10000)
    };
    
    backtestAdvanced.startLiveSession(config);
}

function stopLiveMode() {
    backtestAdvanced.stopLiveSession();
}

async function startReplayMode() {
    const strategy = document.getElementById('liveStrategy')?.value || 'elcaro';
    const symbol = document.getElementById('symbol')?.value || 'BTCUSDT';
    const timeframe = document.getElementById('timeframe')?.value || '1h';
    const days = parseInt(document.getElementById('days')?.value || 30);
    
    const loaded = await strategyReplay.load(strategy, symbol, timeframe, days);
    
    if (loaded) {
        strategyReplay.play();
    }
}

function setReplaySpeed(speed) {
    strategyReplay.setSpeed(speed);
    document.querySelectorAll('.speed-btn').forEach(btn => {
        btn.classList.toggle('active', parseFloat(btn.dataset.speed) === speed);
    });
}
