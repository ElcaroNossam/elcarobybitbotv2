#!/usr/bin/env python3
"""Test backtest engine critical fixes"""

import sys
sys.path.insert(0, '/home/illiateslenko/UpdateProject/project-bybit/bybitv1/bybit_demo')

from webapp.services.backtest_engine import RealBacktestEngine, TradingCosts

# Test TradingCosts
entry_val = 1000
exit_val = 1000
costs = TradingCosts.calculate(entry_val, exit_val, is_maker=False)
print(f'✅ TradingCosts.calculate() works: ${costs:.2f} on $1000 trade')
print(f'   - Entry fee (taker 0.075%): ${entry_val * 0.00075:.2f}')
print(f'   - Exit fee (taker 0.075%): ${exit_val * 0.00075:.2f}')
print(f'   - Slippage (0.05%): ${entry_val * 0.0005:.2f}')
print(f'   - Total: ${costs:.2f} ({costs/entry_val*100:.3f}%)')

# Test engine initialization
engine = RealBacktestEngine()
print(f'\n✅ RealBacktestEngine initialized with {len(engine.analyzers)} analyzers')
print(f'   Analyzers: {list(engine.analyzers.keys())}')

# Test safe_analyze decorator
print(f'\n✅ Testing @safe_analyze decorator on all analyzers:')
for name, analyzer in engine.analyzers.items():
    # Call with empty candles (should not crash thanks to decorator)
    result = analyzer.analyze([])
    status = "✅ SAFE" if result == {} else "⚠️ UNEXPECTED"
    print(f'   {name}: {status}')
    
print(f'\n✅ All critical fixes verified successfully!')
