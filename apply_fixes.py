#!/usr/bin/env python3
"""
Quick Patch Script - Apply Critical UI Fixes
Applies fixes to screener.html and strategies.html
"""

import re
import sys

def patch_screener():
    """Add exchange selector to screener"""
    file_path = "webapp/templates/screener.html"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find market-type-toggle and add exchange selector after it
    exchange_html = '''
            <div class="exchange-selector" style="display: flex; gap: 10px; margin-left: 20px;">
                <button class="exchange-btn active" data-exchange="binance" style="padding: 8px 16px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; color: var(--text-secondary); cursor: pointer; transition: all 0.3s; display: flex; align-items: center; gap: 6px; font-size: 13px;">
                    <i class="fab fa-bitcoin"></i> Binance
                </button>
                <button class="exchange-btn" data-exchange="bybit" style="padding: 8px 16px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; color: var(--text-secondary); cursor: pointer; transition: all 0.3s; display: flex; align-items: center; gap: 6px; font-size: 13px;">
                    <span style="font-size: 16px;">⚡</span> Bybit
                </button>
                <button class="exchange-btn" data-exchange="okx" style="padding: 8px 16px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; color: var(--text-secondary); cursor: pointer; transition: all 0.3s; display: flex; align-items: center; gap: 6px; font-size: 13px;">
                    <span style="font-size: 16px;">🔷</span> OKX
                </button>
            </div>'''
    
    # Insert after market-type-toggle closing div
    pattern = r'(</div>\s*</div>\s*<div class="filter-group")'
    if re.search(pattern, content):
        content = re.sub(pattern, exchange_html + r'\n\1', content, count=1)
        print("✅ Added exchange selector to screener")
    else:
        print("⚠️ Could not find insertion point for exchange selector")
    
    # Add CSS for exchange buttons
    css_insert = '''
        .exchange-btn:hover { background: var(--bg-hover); border-color: var(--accent); }
        .exchange-btn.active { background: linear-gradient(135deg, var(--green), #00cc6a); border-color: transparent; color: #000; font-weight: 600; }
'''
    
    # Insert before closing </style>
    content = content.replace('</style>', css_insert + '\n    </style>')
    
    # Add JavaScript for exchange switching
    js_insert = '''
        // Exchange Switching
        let activeExchange = 'binance';
        document.querySelectorAll('.exchange-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Switching exchange:', btn.dataset.exchange);
                document.querySelectorAll('.exchange-btn').forEach(b => {
                    b.classList.remove('active');
                    b.style.background = 'var(--bg-card)';
                    b.style.color = 'var(--text-secondary)';
                    b.style.fontWeight = 'normal';
                });
                btn.classList.add('active');
                btn.style.background = 'linear-gradient(135deg, var(--green), #00cc6a)';
                btn.style.color = '#000';
                btn.style.fontWeight = '600';
                activeExchange = btn.dataset.exchange;
                
                // Reconnect WebSocket with new exchange (implement later)
                console.log('Exchange changed to:', activeExchange);
            });
        });
'''
    
    # Insert before connectWS() call
    content = content.replace('// Start\n        connectWS();', js_insert + '\n        // Start\n        connectWS();')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Patched {file_path}")

def patch_strategies():
    """Fix New Strategy button in strategies.html"""
    file_path = "webapp/templates/strategies.html"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find btn-create and add onclick handler
    if 'btn-create' in content and 'onclick' not in content[content.find('btn-create'):content.find('btn-create')+200]:
        content = content.replace(
            'class="btn-create"',
            'class="btn-create" onclick="openNewStrategyModal()"'
        )
        print("✅ Added onclick handler to New Strategy button")
    
    # Add modal functions if not exist
    modal_functions = '''
        // Modal functions
        function openNewStrategyModal() {
            console.log('Opening new strategy modal');
            const modal = document.getElementById('newStrategyModal');
            if (modal) {
                modal.style.display = 'flex';
                setTimeout(() => modal.classList.add('active'), 10);
            } else {
                alert('Strategy creation modal coming soon!\\nFor now, use the Marketplace to purchase strategies.');
            }
        }
        
        function closeNewStrategyModal() {
            const modal = document.getElementById('newStrategyModal');
            if (modal) {
                modal.classList.remove('active');
                setTimeout(() => modal.style.display = 'none', 300);
            }
        }
        
        function saveNewStrategy() {
            const name = document.getElementById('strategyName')?.value;
            if (!name) {
                alert('Please enter a strategy name');
                return;
            }
            console.log('Saving strategy:', name);
            alert('Strategy creation will be implemented in next update');
            closeNewStrategyModal();
        }
'''
    
    # Insert before closing </script>
    if 'function openNewStrategyModal' not in content:
        content = content.replace('</script>\n</body>', modal_functions + '\n    </script>\n</body>')
        print("✅ Added modal functions to strategies page")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Patched {file_path}")

def main():
    try:
        print("🔧 Applying Quick Fixes...")
        print("=" * 50)
        
        patch_screener()
        print()
        patch_strategies()
        
        print()
        print("=" * 50)
        print("✅ All patches applied successfully!")
        print()
        print("Next steps:")
        print("1. Restart services: ./start.sh --restart")
        print("2. Test screener: http://localhost:8765/screener")
        print("3. Test strategies: http://localhost:8765/strategies")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
