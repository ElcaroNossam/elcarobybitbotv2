/**
 * Enliko Market Heatmap v1.0
 * Interactive cryptocurrency market visualization
 */

class MarketHeatmap {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.coins = [];
        this.sortBy = 'market_cap';
        this.timeframe = '24h';
    }

    async init() {
        if (!this.container) return;
        
        this.createHeader();
        this.createHeatmapContainer();
        await this.fetchData();
        this.startAutoRefresh();
    }

    createHeader() {
        const header = document.createElement('div');
        header.className = 'heatmap-header';
        header.innerHTML = `
            <div class="heatmap-title">
                <span class="heatmap-icon">🔥</span>
                <h3>Market Heatmap</h3>
                <span class="live-indicator">LIVE</span>
            </div>
            <div class="heatmap-controls">
                <select id="heatmapTimeframe" onchange="Heatmap.setTimeframe(this.value)">
                    <option value="1h">1 Hour</option>
                    <option value="24h" selected>24 Hours</option>
                    <option value="7d">7 Days</option>
                </select>
                <select id="heatmapSort" onchange="Heatmap.setSort(this.value)">
                    <option value="market_cap" selected>Market Cap</option>
                    <option value="volume">Volume</option>
                    <option value="change">% Change</option>
                </select>
            </div>
        `;
        this.container.appendChild(header);
    }

    createHeatmapContainer() {
        const grid = document.createElement('div');
        grid.className = 'heatmap-grid';
        grid.id = 'heatmapGrid';
        this.container.appendChild(grid);
    }

    async fetchData() {
        try {
            const response = await fetch('/api/screener/coins?limit=50');
            if (response.ok) {
                const data = await response.json();
                this.coins = data.coins || data || [];
                this.render();
            } else {
                // Use mock data
                this.coins = this.getMockData();
                this.render();
            }
        } catch (e) {
            console.warn('Failed to fetch heatmap data:', e);
            this.coins = this.getMockData();
            this.render();
        }
    }

    getMockData() {
        const symbols = [
            { symbol: 'BTC', name: 'Bitcoin', market_cap: 1900000000000 },
            { symbol: 'ETH', name: 'Ethereum', market_cap: 400000000000 },
            { symbol: 'BNB', name: 'BNB', market_cap: 90000000000 },
            { symbol: 'SOL', name: 'Solana', market_cap: 80000000000 },
            { symbol: 'XRP', name: 'Ripple', market_cap: 70000000000 },
            { symbol: 'DOGE', name: 'Dogecoin', market_cap: 40000000000 },
            { symbol: 'ADA', name: 'Cardano', market_cap: 35000000000 },
            { symbol: 'AVAX', name: 'Avalanche', market_cap: 30000000000 },
            { symbol: 'DOT', name: 'Polkadot', market_cap: 25000000000 },
            { symbol: 'LINK', name: 'Chainlink', market_cap: 20000000000 },
            { symbol: 'MATIC', name: 'Polygon', market_cap: 18000000000 },
            { symbol: 'UNI', name: 'Uniswap', market_cap: 15000000000 },
            { symbol: 'ATOM', name: 'Cosmos', market_cap: 12000000000 },
            { symbol: 'LTC', name: 'Litecoin', market_cap: 10000000000 },
            { symbol: 'FIL', name: 'Filecoin', market_cap: 8000000000 },
            { symbol: 'APT', name: 'Aptos', market_cap: 7000000000 },
            { symbol: 'ARB', name: 'Arbitrum', market_cap: 6000000000 },
            { symbol: 'OP', name: 'Optimism', market_cap: 5000000000 },
            { symbol: 'SUI', name: 'Sui', market_cap: 4500000000 },
            { symbol: 'INJ', name: 'Injective', market_cap: 4000000000 },
        ];

        return symbols.map(s => ({
            ...s,
            price: Math.random() * 50000 + 1,
            change_24h: (Math.random() - 0.5) * 20,
            volume_24h: s.market_cap * (Math.random() * 0.1 + 0.02)
        }));
    }

    render() {
        const grid = document.getElementById('heatmapGrid');
        if (!grid) return;

        // Sort coins
        let sorted = [...this.coins];
        switch (this.sortBy) {
            case 'volume':
                sorted.sort((a, b) => (b.volume_24h || 0) - (a.volume_24h || 0));
                break;
            case 'change':
                sorted.sort((a, b) => Math.abs(b.change_24h || 0) - Math.abs(a.change_24h || 0));
                break;
            default:
                sorted.sort((a, b) => (b.market_cap || 0) - (a.market_cap || 0));
        }

        // Calculate sizes based on market cap
        const maxCap = Math.max(...sorted.map(c => c.market_cap || 1));
        
        grid.innerHTML = sorted.map((coin, index) => {
            const change = coin.change_24h || 0;
            const intensity = Math.min(Math.abs(change) / 10, 1);
            const isPositive = change >= 0;
            const size = this.calculateSize(coin.market_cap || 1, maxCap, index);
            
            const bgColor = isPositive 
                ? `rgba(34, 197, 94, ${0.2 + intensity * 0.6})`
                : `rgba(239, 68, 68, ${0.2 + intensity * 0.6})`;
            
            const borderColor = isPositive 
                ? `rgba(34, 197, 94, ${0.5 + intensity * 0.5})`
                : `rgba(239, 68, 68, ${0.5 + intensity * 0.5})`;

            return `
                <div class="heatmap-tile ${isPositive ? 'positive' : 'negative'}" 
                     style="--size: ${size}; background: ${bgColor}; border-color: ${borderColor};"
                     onclick="Heatmap.selectCoin('${coin.symbol}')"
                     data-symbol="${coin.symbol}">
                    <div class="tile-symbol">${coin.symbol}</div>
                    <div class="tile-change ${isPositive ? 'up' : 'down'}">
                        ${isPositive ? '+' : ''}${change.toFixed(2)}%
                    </div>
                    <div class="tile-price">$${this.formatPrice(coin.price)}</div>
                </div>
            `;
        }).join('');
    }

    calculateSize(cap, maxCap, index) {
        // Logarithmic scaling for better distribution
        const logScale = Math.log10(cap + 1) / Math.log10(maxCap + 1);
        const baseSize = 80 + logScale * 120;
        
        // Top coins get extra size
        if (index < 3) return baseSize * 1.5;
        if (index < 10) return baseSize * 1.2;
        return baseSize;
    }

    formatPrice(price) {
        if (!price) return '0.00';
        if (price >= 1000) return price.toLocaleString('en-US', { maximumFractionDigits: 0 });
        if (price >= 1) return price.toFixed(2);
        return price.toFixed(4);
    }

    setTimeframe(tf) {
        this.timeframe = tf;
        this.fetchData();
    }

    setSort(sort) {
        this.sortBy = sort;
        this.render();
    }

    selectCoin(symbol) {
        // Update terminal symbol
        if (window.terminal) {
            window.terminal.currentSymbol = symbol + 'USDT';
            window.terminal.updateChart();
        }
        
        // Highlight selected
        document.querySelectorAll('.heatmap-tile').forEach(el => {
            el.classList.remove('selected');
            if (el.dataset.symbol === symbol) {
                el.classList.add('selected');
            }
        });

        HapticFeedback?.selection();
        SoundEffects?.play('click');
    }

    startAutoRefresh() {
        setInterval(() => this.fetchData(), 30000);
    }
}

// CSS for heatmap
const heatmapStyles = document.createElement('style');
heatmapStyles.textContent = `
.heatmap-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0;
    margin-bottom: 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.heatmap-title {
    display: flex;
    align-items: center;
    gap: 10px;
}

.heatmap-title h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: #fff;
}

.heatmap-icon {
    font-size: 24px;
}

.heatmap-controls {
    display: flex;
    gap: 10px;
}

.heatmap-controls select {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 8px 12px;
    color: #fff;
    font-size: 13px;
    cursor: pointer;
}

.heatmap-controls select:hover {
    border-color: rgba(255, 255, 255, 0.3);
}

.heatmap-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 8px;
}

.heatmap-tile {
    flex: 0 0 auto;
    width: calc(var(--size) * 1px);
    height: calc(var(--size) * 0.7px);
    min-width: 80px;
    min-height: 60px;
    border-radius: 12px;
    border: 1px solid;
    padding: 10px;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 4px;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}

.heatmap-tile::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 50%);
    pointer-events: none;
}

.heatmap-tile:hover {
    transform: scale(1.05);
    z-index: 10;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

.heatmap-tile.selected {
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.5), 0 8px 30px rgba(139, 92, 246, 0.3);
}

.tile-symbol {
    font-size: 14px;
    font-weight: 700;
    color: #fff;
    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.tile-change {
    font-size: 16px;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}

.tile-change.up {
    color: #22c55e;
}

.tile-change.down {
    color: #ef4444;
}

.tile-price {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.7);
    font-family: 'JetBrains Mono', monospace;
}

@media (max-width: 768px) {
    .heatmap-header {
        flex-direction: column;
        gap: 12px;
        align-items: flex-start;
    }
    
    .heatmap-tile {
        min-width: 70px;
        min-height: 50px;
        padding: 8px;
    }
    
    .tile-symbol {
        font-size: 12px;
    }
    
    .tile-change {
        font-size: 14px;
    }
}
`;
document.head.appendChild(heatmapStyles);

// Initialize
const Heatmap = new MarketHeatmap('marketHeatmap');
window.Heatmap = Heatmap;

// Auto-init if container exists
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('marketHeatmap')) {
        Heatmap.init();
    }
});
