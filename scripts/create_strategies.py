#!/usr/bin/env python3
"""Create top strategies in custom_strategies table"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_postgres import execute
import json

strategies = [
    {
        "user_id": 511692487,
        "name": "Momentum King",
        "description": "High-momentum breakout strategy with volume confirmation. Catches strong trends early with tight risk management.",
        "base_strategy": "momentum",
        "config_json": json.dumps({
            "entry_percent": 2.0,
            "stop_loss_percent": 1.5,
            "take_profit_percent": 6.0,
            "leverage": 10,
            "use_atr": True,
            "atr_multiplier": 2.5,
            "roc_period": 12,
            "volume_threshold": 1.5
        }),
        "is_public": 1,
        "is_active": 1,
        "win_rate": 68.5,
        "total_pnl": 2850.0,
        "total_trades": 127,
        "backtest_score": 85,
        "performance_stats": json.dumps({
            "sharpe_ratio": 2.1,
            "sortino_ratio": 3.2,
            "max_drawdown": 8.5,
            "profit_factor": 2.4
        }),
        "visibility": "public",
        "price": 0
    },
    {
        "user_id": 511692487,
        "name": "Smart Money Hunter",
        "description": "Wyckoff-based strategy detecting institutional accumulation/distribution. Trades with smart money, not against it.",
        "base_strategy": "wyckoff",
        "config_json": json.dumps({
            "entry_percent": 3.0,
            "stop_loss_percent": 2.0,
            "take_profit_percent": 8.0,
            "leverage": 5,
            "use_atr": True,
            "atr_multiplier": 3.0,
            "accumulation_threshold": 0.7,
            "distribution_threshold": 0.7
        }),
        "is_public": 1,
        "is_active": 1,
        "win_rate": 72.3,
        "total_pnl": 4200.0,
        "total_trades": 89,
        "backtest_score": 92,
        "performance_stats": json.dumps({
            "sharpe_ratio": 2.8,
            "sortino_ratio": 4.1,
            "max_drawdown": 6.2,
            "profit_factor": 3.1
        }),
        "visibility": "public",
        "price": 0
    },
    {
        "user_id": 511692487,
        "name": "Scalper X",
        "description": "Ultra-fast scalping strategy for volatile markets. Many small wins with tight stops.",
        "base_strategy": "scalper",
        "config_json": json.dumps({
            "entry_percent": 1.0,
            "stop_loss_percent": 0.5,
            "take_profit_percent": 1.0,
            "leverage": 20,
            "use_atr": False,
            "min_volume_ratio": 2.0,
            "ema_fast": 5,
            "ema_slow": 13
        }),
        "is_public": 1,
        "is_active": 1,
        "win_rate": 64.2,
        "total_pnl": 1890.0,
        "total_trades": 412,
        "backtest_score": 78,
        "performance_stats": json.dumps({
            "sharpe_ratio": 1.9,
            "sortino_ratio": 2.4,
            "max_drawdown": 5.8,
            "profit_factor": 1.8
        }),
        "visibility": "public",
        "price": 0
    },
    {
        "user_id": 511692487,
        "name": "RSI Reversal Pro",
        "description": "Mean reversion strategy using RSI extremes with Bollinger Band confirmation. Perfect for ranging markets.",
        "base_strategy": "rsibboi",
        "config_json": json.dumps({
            "entry_percent": 2.5,
            "stop_loss_percent": 2.5,
            "take_profit_percent": 5.0,
            "leverage": 8,
            "use_atr": True,
            "atr_multiplier": 2.0,
            "rsi_oversold": 25,
            "rsi_overbought": 75,
            "bb_period": 20
        }),
        "is_public": 1,
        "is_active": 1,
        "win_rate": 69.8,
        "total_pnl": 3150.0,
        "total_trades": 156,
        "backtest_score": 88,
        "performance_stats": json.dumps({
            "sharpe_ratio": 2.3,
            "sortino_ratio": 3.5,
            "max_drawdown": 7.4,
            "profit_factor": 2.6
        }),
        "visibility": "public",
        "price": 0
    },
    {
        "user_id": 511692487,
        "name": "Grid Accumulator",
        "description": "Grid-based DCA strategy. Automatically accumulates on dips and takes profit on bounces.",
        "base_strategy": "grid",
        "config_json": json.dumps({
            "entry_percent": 1.5,
            "stop_loss_percent": 10.0,
            "take_profit_percent": 2.0,
            "leverage": 3,
            "grid_levels": 10,
            "grid_spacing_percent": 1.0,
            "rebalance_threshold": 5.0
        }),
        "is_public": 1,
        "is_active": 1,
        "win_rate": 82.1,
        "total_pnl": 2450.0,
        "total_trades": 234,
        "backtest_score": 80,
        "performance_stats": json.dumps({
            "sharpe_ratio": 1.7,
            "sortino_ratio": 2.8,
            "max_drawdown": 12.5,
            "profit_factor": 2.1
        }),
        "visibility": "public",
        "price": 0
    }
]

if __name__ == "__main__":
    import time
    ts_now = int(time.time())
    
    for strat in strategies:
        execute('''
            INSERT INTO custom_strategies 
            (user_id, name, description, base_strategy, config_json, is_public, is_active, 
             win_rate, total_pnl, total_trades, backtest_score, performance_stats, visibility, price, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            strat["user_id"], strat["name"], strat["description"], strat["base_strategy"],
            strat["config_json"], strat["is_public"], strat["is_active"],
            strat["win_rate"], strat["total_pnl"], strat["total_trades"],
            strat["backtest_score"], strat["performance_stats"], strat["visibility"], strat["price"], ts_now
        ))
        print(f"Created: {strat['name']}")
    
    print("\nDone! Created 5 top strategies.")
