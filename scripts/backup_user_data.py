#!/usr/bin/env python3
"""
Backup user data before database migration.

Saves:
- users table (API keys, settings)
- user_strategy_settings table
- active_positions table
- trade_logs table (last 30 days)

Output: user_data_backup_YYYYMMDD_HHMMSS.json
"""

import json
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_postgres import get_conn, execute


def backup_users():
    """Backup users table with API keys and settings."""
    print("📦 Backing up users table...")
    
    rows = execute("""
        SELECT user_id, lang, trading_mode, exchange_type, percent, tp_percent, sl_percent,
               leverage, use_atr, atr_trigger_pct, atr_step_pct, coins, dca_enabled,
               dca_pct_1, dca_pct_2, is_allowed, is_banned, live_enabled,
               demo_api_key, demo_api_secret, real_api_key, real_api_secret,
               hl_enabled, hl_testnet, hl_testnet_private_key, hl_testnet_wallet_address,
               hl_mainnet_private_key, hl_mainnet_wallet_address, hl_private_key, hl_wallet_address,
               elc_balance, elc_staked, elc_locked, email, updated_at
        FROM users
        WHERE is_allowed = 1 OR demo_api_key IS NOT NULL OR real_api_key IS NOT NULL
    """)
    
    users = []
    for row in rows:
        users.append(dict(row))
    
    print(f"  ✅ Found {len(users)} users with data")
    return users


def backup_strategy_settings():
    """Backup strategy settings."""
    print("📦 Backing up strategy settings...")
    
    rows = execute("""
        SELECT user_id, strategy, side, exchange, account_type, enabled,
               percent, tp_percent, sl_percent, leverage, use_atr,
               atr_trigger_pct, atr_step_pct, order_type, limit_offset_pct,
               direction, dca_enabled, dca_pct_1, dca_pct_2,
               max_positions, coins_group, trading_mode, updated_at
        FROM user_strategy_settings
    """)
    
    settings = []
    for row in rows:
        settings.append(dict(row))
    
    print(f"  ✅ Found {len(settings)} strategy settings records")
    return settings


def backup_active_positions():
    """Backup active positions."""
    print("📦 Backing up active positions...")
    
    rows = execute("""
        SELECT user_id, symbol, account_type, exchange, side, entry_price,
               size, qty, strategy, leverage, sl_price, tp_price,
               dca_10_done, dca_25_done, open_ts, source
        FROM active_positions
    """)
    
    positions = []
    for row in rows:
        data = dict(row)
        # Convert datetime to string
        if data.get('open_ts'):
            data['open_ts'] = str(data['open_ts'])
        positions.append(data)
    
    print(f"  ✅ Found {len(positions)} active positions")
    return positions


def backup_trade_logs():
    """Backup trade logs (last 30 days)."""
    print("📦 Backing up trade logs (last 30 days)...")
    
    rows = execute("""
        SELECT user_id, symbol, side, qty, entry_price, exit_price,
               pnl, pnl_pct, strategy, account_type, exchange,
               exit_reason, sl_pct, tp_pct, leverage, ts
        FROM trade_logs
        WHERE ts > NOW() - INTERVAL '30 days'
        ORDER BY ts DESC
    """)
    
    trades = []
    for row in rows:
        data = dict(row)
        if data.get('ts'):
            data['ts'] = str(data['ts'])
        trades.append(data)
    
    print(f"  ✅ Found {len(trades)} trades from last 30 days")
    return trades


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"user_data_backup_{timestamp}.json"
    
    print("=" * 60)
    print("🗄️  DATABASE BACKUP SCRIPT")
    print("=" * 60)
    
    backup_data = {
        "backup_timestamp": datetime.now().isoformat(),
        "users": backup_users(),
        "strategy_settings": backup_strategy_settings(),
        "active_positions": backup_active_positions(),
        "trade_logs": backup_trade_logs()
    }
    
    # Save to file
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
    
    print("=" * 60)
    print(f"✅ Backup saved to: {filepath}")
    print(f"   Users: {len(backup_data['users'])}")
    print(f"   Strategy Settings: {len(backup_data['strategy_settings'])}")
    print(f"   Active Positions: {len(backup_data['active_positions'])}")
    print(f"   Trade Logs: {len(backup_data['trade_logs'])}")
    print("=" * 60)
    
    return filepath


if __name__ == "__main__":
    main()
