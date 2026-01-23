#!/usr/bin/env python3
"""Script to rename ElCaro to Lyxen across the codebase - Phase 2."""

import os

def replace_in_file(filepath, replacements):
    """Replace display text in a file."""
    if not os.path.exists(filepath):
        return 0
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading {filepath}: {e}")
        return 0
    
    original = content
    count = 0
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            count += 1
    
    if content != original:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"  Error writing {filepath}: {e}")
            return 0
        return count
    return 0

# Display text replacements (NOT code identifiers)
REPLACEMENTS = [
    ("Lyxen Trading Platform", "Lyxen Trading Platform"),
    ("ElCaro Trading Terminal", "Lyxen Trading Terminal"),
    ("ElCaro Trading", "Lyxen Trading"),
    ("Lyxen Team", "Lyxen Team"),
    ("ElCaro Oracle Team", "Lyxen Oracle Team"),
    ("ElCaro Development Team", "Lyxen Development Team"),
    ("Lyxen Pro Backtest", "Lyxen Pro Backtest"),
    ("Lyxen Pro", "Lyxen Pro"),
    ("Lyxen Backtester", "Lyxen Backtester"),
    ("Lyxen Screener", "Lyxen Screener"),
    ("Lyxen Analytics", "Lyxen Analytics"),
    ("ElCaro Orderbook", "Lyxen Orderbook"),
    ("ElCaro Paper Trading", "Lyxen Paper Trading"),
    ("ElCaro Advanced Risk", "Lyxen Advanced Risk"),
    ("ElCaro Position Size", "Lyxen Position Size"),
    ("Lyxen Channel Breakout", "Lyxen Channel Breakout"),
    ("ElCaro Trade Stream", "Lyxen Trade Stream"),
    ("ElCaro design system", "Lyxen design system"),
    ("LYXEN BACKTESTER", "LYXEN BACKTESTER"),
    ("LYXEN payment system", "LYXEN payment system"),
    ("LYXEN Token Payment", "LYXEN Token Payment"),
    ("LYXEN token ecosystem", "LYXEN token ecosystem"),
    ("LYXEN token purchases", "LYXEN token purchases"),
    ("LYXEN tokens", "LYXEN tokens"),
    ("LYXEN token", "LYXEN token"),
    ("ElCaro Token", "Lyxen Token"),
    ("'ElCaro'", "'Lyxen'"),
    ('"Lyxen"', '"Lyxen"'),
    ("LyxenBot", "LyxenBot"),
    ("(c) 2024-2026 ElCaro", "(c) 2024-2026 Lyxen"),
    ("(c) Lyxen", "(c) Lyxen"),
    ("Lyxen ©", "Lyxen ©"),
    # Test signal parsers - keep Elcaro as the signal format header
]

FILES_TO_UPDATE = [
    "requirements.txt",
    "SECURITY_AUDIT_REPORT_2026.md",
    "config/analytics_db.py",
    "config/__init__.py",
    "config/settings.py",
    "run_tests_quick.sh",
    "run_terminal_full_tests.py",
    "run_backtest_tests.py",
    "oracle/__init__.py",
    "oracle/README.md",
    "webapp/app.py",
    "webapp/api/screener_ws.py",
    "webapp/api/ton_payments.py",
    "webapp/api/users.py",
    "webapp/api/strategy_backtest.py",
    "webapp/api/web3.py",
    "webapp/api/exchange_fetchers.py",
    "webapp/api/admin.py",
    "webapp/api/backtest_pro.py",
    "webapp/api/blockchain.py",
    "webapp/api/backtest.py",
    "webapp/api/websocket.py",
    "webapp/services/paper_trading.py",
    "webapp/services/risk_management.py",
    "webapp/services/position_calculator.py",
    "webapp/services/orderbook_analyzer.py",
]

def main():
    os.chdir('/Users/elcarosam/project/elcarobybitbotv2')
    
    total = 0
    for filepath in FILES_TO_UPDATE:
        count = replace_in_file(filepath, REPLACEMENTS)
        if count > 0:
            print(f"Updated: {filepath} ({count} replacements)")
            total += 1
    
    print(f"\nTotal files updated in Phase 2: {total}")

if __name__ == '__main__':
    main()
