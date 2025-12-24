#!/usr/bin/env python3
import json
import sys

data = json.load(sys.stdin)
r = data['results']['elcaro']

print('📊 BACKTEST RESULTS (with new metrics):\n')
print(f'Total Trades: {r["total_trades"]}')
print(f'Win Rate: {r["win_rate"]:.1f}%')
print(f'Total P&L: ${r["total_pnl"]:.2f} ({r["total_pnl_percent"]:.2f}%)')
print(f'\nRISK METRICS:')
print(f'  Sharpe Ratio: {r["sharpe_ratio"]:.2f}')
print(f'  Sortino Ratio: {r.get("sortino_ratio", "N/A")}')
print(f'  Calmar Ratio: {r.get("calmar_ratio", "N/A")}')
print(f'  Expectancy: {r.get("expectancy", "N/A")}')
print(f'  Avg Win: ${r.get("avg_win", "N/A")}')
print(f'  Avg Loss: ${r.get("avg_loss", "N/A")}')
print(f'\nMAX DD: {r["max_drawdown_percent"]:.2f}%')
print(f'Final Balance: ${r["final_balance"]:.2f}')
