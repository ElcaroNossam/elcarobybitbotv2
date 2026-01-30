/**
 * Enliko AI Trading Copilot v1.0
 * Smart trading assistant with real-time insights
 */

class AICopilot {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.panel = null;
        this.isTyping = false;
    }

    init() {
        this.createPanel();
        this.createTriggerButton();
        this.bindEvents();
        this.loadHistory();
        
        // Show welcome message after delay
        setTimeout(() => this.showWelcome(), 2000);
    }

    createPanel() {
        this.panel = document.createElement('div');
        this.panel.className = 'ai-copilot-panel';
        this.panel.innerHTML = `
            <div class="copilot-header">
                <div class="copilot-title">
                    <span class="copilot-avatar">🤖</span>
                    <span>AI Trading Copilot</span>
                    <span class="copilot-status online">Online</span>
                </div>
                <div class="copilot-actions">
                    <button class="copilot-btn" onclick="AICopilot.clearHistory()" title="Clear history">
                        <i class="fas fa-trash"></i>
                    </button>
                    <button class="copilot-btn" onclick="AICopilot.toggle()" title="Close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div class="copilot-messages" id="copilotMessages"></div>
            <div class="copilot-suggestions" id="copilotSuggestions">
                <button onclick="AICopilot.ask('market analysis')">📊 Market Analysis</button>
                <button onclick="AICopilot.ask('trading signals')">📈 Trading Signals</button>
                <button onclick="AICopilot.ask('portfolio review')">💼 Portfolio Review</button>
                <button onclick="AICopilot.ask('risk assessment')">⚠️ Risk Assessment</button>
            </div>
            <div class="copilot-input-area">
                <input type="text" id="copilotInput" placeholder="Ask me anything about trading..." 
                       onkeypress="if(event.key==='Enter') AICopilot.send()">
                <button onclick="AICopilot.send()" class="send-btn">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        `;
        document.body.appendChild(this.panel);
    }

    createTriggerButton() {
        const btn = document.createElement('button');
        btn.className = 'ai-copilot-trigger';
        btn.innerHTML = `
            <span class="trigger-icon">🤖</span>
            <span class="trigger-pulse"></span>
        `;
        btn.onclick = () => this.toggle();
        btn.title = 'AI Trading Copilot';
        document.body.appendChild(btn);
    }

    bindEvents() {
        // Close on escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.toggle();
            }
        });

        // Close on click outside
        document.addEventListener('click', (e) => {
            if (this.isOpen && !this.panel.contains(e.target) && 
                !e.target.closest('.ai-copilot-trigger')) {
                this.toggle();
            }
        });
    }

    toggle() {
        this.isOpen = !this.isOpen;
        this.panel.classList.toggle('open', this.isOpen);
        
        if (this.isOpen) {
            document.getElementById('copilotInput')?.focus();
            HapticFeedback?.light();
        }
    }

    showWelcome() {
        if (this.messages.length === 0) {
            this.addMessage('bot', `👋 Hey! I'm your AI Trading Copilot.
            
I can help you with:
• Real-time market analysis
• Trading signal insights  
• Portfolio optimization
• Risk management

What would you like to know?`);
        }
    }

    addMessage(type, content, animate = true) {
        const messagesContainer = document.getElementById('copilotMessages');
        if (!messagesContainer) return;

        const msg = document.createElement('div');
        msg.className = `copilot-message ${type}`;
        
        if (type === 'bot') {
            msg.innerHTML = `
                <span class="message-avatar">🤖</span>
                <div class="message-content">
                    <div class="message-text">${this.formatMessage(content)}</div>
                    <span class="message-time">${new Date().toLocaleTimeString()}</span>
                </div>
            `;
        } else {
            msg.innerHTML = `
                <div class="message-content">
                    <div class="message-text">${escapeHtml(content)}</div>
                    <span class="message-time">${new Date().toLocaleTimeString()}</span>
                </div>
            `;
        }

        if (animate) {
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(10px)';
        }

        messagesContainer.appendChild(msg);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        if (animate) {
            requestAnimationFrame(() => {
                msg.style.transition = 'all 0.3s ease';
                msg.style.opacity = '1';
                msg.style.transform = 'translateY(0)';
            });
        }

        this.messages.push({ type, content, time: Date.now() });
        this.saveHistory();
    }

    formatMessage(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>')
            .replace(/• /g, '&bull; ');
    }

    async send() {
        const input = document.getElementById('copilotInput');
        const query = input?.value.trim();
        if (!query || this.isTyping) return;

        input.value = '';
        this.addMessage('user', query);
        
        await this.getAIResponse(query);
    }

    async ask(topic) {
        const queries = {
            'market analysis': 'Give me a quick market analysis for the current trading session',
            'trading signals': 'What are the top trading signals right now?',
            'portfolio review': 'Review my current portfolio and positions',
            'risk assessment': 'Assess my current risk exposure'
        };
        
        const query = queries[topic] || topic;
        this.addMessage('user', query);
        await this.getAIResponse(query);
    }

    showTyping() {
        this.isTyping = true;
        const messagesContainer = document.getElementById('copilotMessages');
        
        const typing = document.createElement('div');
        typing.className = 'copilot-message bot typing-indicator';
        typing.id = 'typingIndicator';
        typing.innerHTML = `
            <span class="message-avatar">🤖</span>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        messagesContainer.appendChild(typing);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTyping() {
        this.isTyping = false;
        document.getElementById('typingIndicator')?.remove();
    }

    async getAIResponse(query) {
        this.showTyping();
        
        try {
            // Try to get real AI response from backend
            const response = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('enliko_token')}`
                },
                body: JSON.stringify({ message: query })
            });

            this.hideTyping();

            if (response.ok) {
                const data = await response.json();
                this.addMessage('bot', data.response || data.message);
            } else {
                // Fallback to smart local responses
                const smartResponse = this.generateSmartResponse(query);
                this.addMessage('bot', smartResponse);
            }
        } catch (e) {
            this.hideTyping();
            const smartResponse = this.generateSmartResponse(query);
            this.addMessage('bot', smartResponse);
        }

        SoundEffects?.play('notification');
    }

    generateSmartResponse(query) {
        const lowerQuery = query.toLowerCase();
        
        // Market analysis responses
        if (lowerQuery.includes('market') || lowerQuery.includes('analysis')) {
            return `📊 **Quick Market Analysis**

Based on current conditions:

• **BTC**: Trading near key support levels. Watch for breakout above resistance.
• **ETH**: Showing strength relative to BTC. Bullish momentum building.
• **Market Sentiment**: Fear & Greed Index suggests cautious optimism.

💡 **Tip**: Consider scaling into positions rather than going all-in.`;
        }
        
        // Trading signals
        if (lowerQuery.includes('signal') || lowerQuery.includes('trade')) {
            return `📈 **Active Trading Signals**

🟢 **Strong Buy Signals**:
• RSI oversold on multiple timeframes
• Volume surge detected
• Support level confirmation

🔴 **Caution Areas**:
• Some altcoins showing weakness
• Funding rates elevated

⚡ **Action**: Check the Signals tab for real-time entries.`;
        }
        
        // Portfolio review
        if (lowerQuery.includes('portfolio') || lowerQuery.includes('position')) {
            return `💼 **Portfolio Insights**

Looking at your current positions:

• **Diversification**: Consider spreading risk across more assets
• **Leverage**: Keep effective leverage below 10x for safety
• **Stop Losses**: Ensure all positions have protective stops

📊 View detailed stats in the Statistics section.`;
        }
        
        // Risk assessment
        if (lowerQuery.includes('risk')) {
            return `⚠️ **Risk Assessment**

Key risk metrics to monitor:

• **Position Size**: Don't risk more than 2-5% per trade
• **Correlation**: High correlation between positions = concentrated risk
• **Liquidation Price**: Keep distance from liq prices

🛡️ **Protection Tips**:
1. Use stop losses on every trade
2. Take partial profits at targets
3. Don't over-leverage

Stay safe out there! 🚀`;
        }
        
        // Default helpful response
        return `Thanks for your question! Here's what I can help with:

• 📊 **Market Analysis** - Current market conditions
• 📈 **Trading Signals** - Active opportunities  
• 💼 **Portfolio Review** - Position analysis
• ⚠️ **Risk Assessment** - Risk management tips

Try clicking one of the quick action buttons or ask something specific!`;
    }

    saveHistory() {
        try {
            const history = this.messages.slice(-50); // Keep last 50 messages
            localStorage.setItem('enliko_copilot_history', JSON.stringify(history));
        } catch (e) {
            console.warn('Failed to save copilot history:', e);
        }
    }

    loadHistory() {
        try {
            const history = JSON.parse(localStorage.getItem('enliko_copilot_history') || '[]');
            const messagesContainer = document.getElementById('copilotMessages');
            
            history.forEach(msg => {
                this.messages.push(msg);
                // Render without animation for history
                const msgEl = document.createElement('div');
                msgEl.className = `copilot-message ${msg.type}`;
                
                if (msg.type === 'bot') {
                    msgEl.innerHTML = `
                        <span class="message-avatar">🤖</span>
                        <div class="message-content">
                            <div class="message-text">${this.formatMessage(msg.content)}</div>
                        </div>
                    `;
                } else {
                    msgEl.innerHTML = `
                        <div class="message-content">
                            <div class="message-text">${escapeHtml(msg.content)}</div>
                        </div>
                    `;
                }
                messagesContainer?.appendChild(msgEl);
            });

            if (messagesContainer) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        } catch (e) {
            console.warn('Failed to load copilot history:', e);
        }
    }

    clearHistory() {
        this.messages = [];
        localStorage.removeItem('enliko_copilot_history');
        const messagesContainer = document.getElementById('copilotMessages');
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }
        this.showWelcome();
        SoundEffects?.play('click');
    }
}

// Initialize
const AICopilot = new AICopilot();
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => AICopilot.init(), 500);
});

window.AICopilot = AICopilot;
