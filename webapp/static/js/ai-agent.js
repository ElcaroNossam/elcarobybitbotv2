/**
 * AI Market Analysis Agent
 * Uses GPT-4 API for real-time market analysis
 */

class AIAgent {
    constructor() {
        this.messages = [];
        this.isTyping = false;
        this.context = {
            positions: [],
            market: {},
            strategies: []
        };
    }

    async init() {
        await this.loadContext();
        this.bindEvents();
        this.addSystemMessage();
    }

    async loadContext() {
        try {
            const [posRes, marketRes] = await Promise.all([
                fetch('/api/trading/positions'),
                fetch('/api/market/overview')
            ]);
            
            if (posRes.ok) this.context.positions = (await posRes.json()).data || [];
            if (marketRes.ok) this.context.market = (await marketRes.json()).data || {};
        } catch (e) {
            console.error('Failed to load AI context:', e);
        }
    }

    addSystemMessage() {
        this.addMessage({
            role: 'assistant',
            content: `👋 **Hello! I'm your AI Trading Assistant.**

I can help you with:
• 📊 **Market Analysis** - Analyze any crypto pair
• 📈 **Technical Indicators** - RSI, MACD, Bollinger Bands, etc.
• 🎯 **Trade Signals** - Entry/exit points with TP/SL levels
• 🧠 **Strategy Advice** - Optimize your trading strategies
• 📉 **Risk Management** - Position sizing and risk assessment

**Quick Commands:**
\`/analyze BTC\` - Full BTC analysis
\`/signal ETHUSDT\` - Trading signal
\`/risk\` - Risk assessment
\`/market\` - Market overview

What would you like to know?`
        });
    }

    bindEvents() {
        const input = document.getElementById('ai-input');
        const sendBtn = document.getElementById('ai-send');

        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage(input.value);
                    input.value = '';
                }
            });
        }

        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                if (input) {
                    this.sendMessage(input.value);
                    input.value = '';
                }
            });
        }

        // Quick action buttons
        document.querySelectorAll('.ai-quick-action').forEach(btn => {
            btn.addEventListener('click', () => {
                this.sendMessage(btn.dataset.command);
            });
        });
    }

    async sendMessage(content) {
        if (!content.trim() || this.isTyping) return;

        // Add user message
        this.addMessage({ role: 'user', content });

        // Show typing indicator
        this.isTyping = true;
        this.showTypingIndicator();

        try {
            const response = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: content,
                    context: this.context
                })
            });

            const data = await response.json();
            
            this.hideTypingIndicator();
            this.isTyping = false;

            if (data.success) {
                this.addMessage({
                    role: 'assistant',
                    content: data.response,
                    analysis: data.analysis
                });

                // If there's a chart recommendation, show it
                if (data.chart) {
                    this.showAnalysisChart(data.chart);
                }
            } else {
                this.addMessage({
                    role: 'assistant',
                    content: `❌ Error: ${data.error || 'Failed to get response'}`
                });
            }
        } catch (e) {
            this.hideTypingIndicator();
            this.isTyping = false;
            this.addMessage({
                role: 'assistant',
                content: `❌ Connection error. Please try again.`
            });
        }
    }

    addMessage(msg) {
        this.messages.push(msg);
        this.renderMessages();
    }

    renderMessages() {
        const container = document.getElementById('ai-messages');
        if (!container) return;

        container.innerHTML = this.messages.map((msg, idx) => `
            <div class="ai-message ${msg.role}">
                <div class="message-avatar">
                    ${msg.role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>'}
                </div>
                <div class="message-content">
                    <div class="message-text">${this.formatMessage(msg.content)}</div>
                    ${msg.analysis ? this.renderAnalysis(msg.analysis) : ''}
                </div>
            </div>
        `).join('');

        container.scrollTop = container.scrollHeight;
    }

    formatMessage(content) {
        // Convert markdown to HTML
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>')
            .replace(/•/g, '<span class="bullet">•</span>');
    }

    renderAnalysis(analysis) {
        if (!analysis) return '';

        return `
            <div class="analysis-card">
                ${analysis.signal ? `
                    <div class="signal-box ${analysis.signal.direction}">
                        <span class="signal-icon">${analysis.signal.direction === 'long' ? '🟢' : '🔴'}</span>
                        <span class="signal-text">${analysis.signal.direction.toUpperCase()}</span>
                        <span class="signal-confidence">${analysis.signal.confidence}% confidence</span>
                    </div>
                ` : ''}
                
                ${analysis.levels ? `
                    <div class="levels-grid">
                        <div class="level entry">
                            <span class="label">Entry</span>
                            <span class="value">$${analysis.levels.entry}</span>
                        </div>
                        <div class="level tp">
                            <span class="label">Take Profit</span>
                            <span class="value">$${analysis.levels.takeProfit}</span>
                        </div>
                        <div class="level sl">
                            <span class="label">Stop Loss</span>
                            <span class="value">$${analysis.levels.stopLoss}</span>
                        </div>
                        <div class="level rr">
                            <span class="label">R:R Ratio</span>
                            <span class="value">${analysis.levels.riskReward}</span>
                        </div>
                    </div>
                ` : ''}

                ${analysis.indicators ? `
                    <div class="indicators-grid">
                        ${Object.entries(analysis.indicators).map(([key, value]) => `
                            <div class="indicator ${value.signal || ''}">
                                <span class="name">${key}</span>
                                <span class="value">${value.value}</span>
                                <span class="signal-dot ${value.signal}"></span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    showTypingIndicator() {
        const container = document.getElementById('ai-messages');
        if (!container) return;

        const indicator = document.createElement('div');
        indicator.id = 'typing-indicator';
        indicator.className = 'ai-message assistant typing';
        indicator.innerHTML = `
            <div class="message-avatar"><i class="fas fa-robot"></i></div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        container.appendChild(indicator);
        container.scrollTop = container.scrollHeight;
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) indicator.remove();
    }

    showAnalysisChart(chartData) {
        const container = document.getElementById('ai-chart-overlay');
        if (!container) return;

        // Show mini chart with analysis levels
        container.innerHTML = `
            <div class="analysis-chart">
                <div class="chart-header">
                    <span>${chartData.symbol}</span>
                    <button onclick="this.parentElement.parentElement.parentElement.style.display='none'">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div id="ai-mini-chart" style="height: 300px;"></div>
            </div>
        `;
        container.style.display = 'block';

        // Draw chart with Lightweight Charts
        if (window.LightweightCharts) {
            const chart = LightweightCharts.createChart(document.getElementById('ai-mini-chart'), {
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
            candleSeries.setData(chartData.candles);

            // Add analysis lines
            if (chartData.entry) {
                candleSeries.createPriceLine({ price: chartData.entry, color: '#2563eb', lineWidth: 2, title: 'Entry' });
            }
            if (chartData.takeProfit) {
                candleSeries.createPriceLine({ price: chartData.takeProfit, color: '#10b981', lineWidth: 2, title: 'TP' });
            }
            if (chartData.stopLoss) {
                candleSeries.createPriceLine({ price: chartData.stopLoss, color: '#ef4444', lineWidth: 2, title: 'SL' });
            }
        }
    }
}

// Export
window.AIAgent = AIAgent;
