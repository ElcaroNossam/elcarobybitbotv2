#!/usr/bin/env python3
"""
Restore user data after database migration.

Reads from user_data_backup_*.json and restores:
- users table (API keys, settings)
- user_strategy_settings table

Usage:
    python scripts/restore_user_data.py user_data_backup_20260125_123456.json
"""

import json
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_postgres import get_conn, execute, execute_one


def restore_users(users_data):
    """Restore users table."""
    print("📦 Restoring users table...")
    
    if not users_data:
        print("  ⚠️ No users to restore")
        return
    
    restored = 0
    skipped = 0
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            for user in users_data:
                user_id = user.get('user_id')
                if not user_id:
                    continue
                
                # Check if user already exists
                cur.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
                if cur.fetchone():
                    # Update existing user
                    cur.execute("""
                        UPDATE users SET
                            lang = COALESCE(%s, lang),
                            trading_mode = COALESCE(%s, trading_mode),
                            exchange_type = COALESCE(%s, exchange_type),
                            percent = COALESCE(%s, percent),
                            tp_percent = COALESCE(%s, tp_percent),
                            sl_percent = COALESCE(%s, sl_percent),
                            leverage = COALESCE(%s, leverage),
                            use_atr = COALESCE(%s, use_atr),
                            demo_api_key = COALESCE(%s, demo_api_key),
                            demo_api_secret = COALESCE(%s, demo_api_secret),
                            real_api_key = COALESCE(%s, real_api_key),
                            real_api_secret = COALESCE(%s, real_api_secret),
                            hl_enabled = COALESCE(%s, hl_enabled),
                            hl_testnet = COALESCE(%s, hl_testnet),
                            hl_testnet_private_key = COALESCE(%s, hl_testnet_private_key),
                            hl_testnet_wallet_address = COALESCE(%s, hl_testnet_wallet_address),
                            hl_mainnet_private_key = COALESCE(%s, hl_mainnet_private_key),
                            hl_mainnet_wallet_address = COALESCE(%s, hl_mainnet_wallet_address),
                            is_allowed = COALESCE(%s, is_allowed),
                            live_enabled = COALESCE(%s, live_enabled),
                            elc_balance = COALESCE(%s, elc_balance),
                            updated_at = NOW()
                        WHERE user_id = %s
                    """, (
                        user.get('lang'),
                        user.get('trading_mode'),
                        user.get('exchange_type'),
                        user.get('percent'),
                        user.get('tp_percent'),
                        user.get('sl_percent'),
                        user.get('leverage'),
                        user.get('use_atr'),
                        user.get('demo_api_key'),
                        user.get('demo_api_secret'),
                        user.get('real_api_key'),
                        user.get('real_api_secret'),
                        user.get('hl_enabled'),
                        user.get('hl_testnet'),
                        user.get('hl_testnet_private_key'),
                        user.get('hl_testnet_wallet_address'),
                        user.get('hl_mainnet_private_key'),
                        user.get('hl_mainnet_wallet_address'),
                        user.get('is_allowed'),
                        user.get('live_enabled'),
                        user.get('elc_balance'),
                        user_id
                    ))
                    restored += 1
                else:
                    # Insert new user
                    cur.execute("""
                        INSERT INTO users (
                            user_id, lang, trading_mode, exchange_type,
                            percent, tp_percent, sl_percent, leverage, use_atr,
                            demo_api_key, demo_api_secret, real_api_key, real_api_secret,
                            hl_enabled, hl_testnet, hl_testnet_private_key, hl_testnet_wallet_address,
                            hl_mainnet_private_key, hl_mainnet_wallet_address,
                            is_allowed, live_enabled, elc_balance
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, (
                        user_id,
                        user.get('lang', 'en'),
                        user.get('trading_mode', 'demo'),
                        user.get('exchange_type', 'bybit'),
                        user.get('percent', 1.0),
                        user.get('tp_percent', 8.0),
                        user.get('sl_percent', 3.0),
                        user.get('leverage', 10),
                        user.get('use_atr', True),
                        user.get('demo_api_key'),
                        user.get('demo_api_secret'),
                        user.get('real_api_key'),
                        user.get('real_api_secret'),
                        user.get('hl_enabled', False),
                        user.get('hl_testnet', False),
                        user.get('hl_testnet_private_key'),
                        user.get('hl_testnet_wallet_address'),
                        user.get('hl_mainnet_private_key'),
                        user.get('hl_mainnet_wallet_address'),
                        user.get('is_allowed', False),
                        user.get('live_enabled', False),
                        user.get('elc_balance', 0)
                    ))
                    restored += 1
    
    print(f"  ✅ Restored {restored} users")


def restore_strategy_settings(settings_data):
    """Restore strategy settings with 4D schema."""
    print("📦 Restoring strategy settings...")
    
    if not settings_data:
        print("  ⚠️ No strategy settings to restore")
        return
    
    restored = 0
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            for setting in settings_data:
                user_id = setting.get('user_id')
                strategy = setting.get('strategy')
                side = setting.get('side', 'long')
                exchange = setting.get('exchange', 'bybit')
                
                if not user_id or not strategy:
                    continue
                
                # UPSERT with 4D key
                cur.execute("""
                    INSERT INTO user_strategy_settings (
                        user_id, strategy, side, exchange,
                        enabled, percent, tp_percent, sl_percent, leverage,
                        use_atr, atr_trigger_pct, atr_step_pct, order_type,
                        direction, dca_enabled, dca_pct_1, dca_pct_2,
                        max_positions, coins_group, trading_mode, account_type
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (user_id, strategy, side, exchange) DO UPDATE SET
                        enabled = EXCLUDED.enabled,
                        percent = EXCLUDED.percent,
                        tp_percent = EXCLUDED.tp_percent,
                        sl_percent = EXCLUDED.sl_percent,
                        leverage = EXCLUDED.leverage,
                        use_atr = EXCLUDED.use_atr,
                        atr_trigger_pct = EXCLUDED.atr_trigger_pct,
                        atr_step_pct = EXCLUDED.atr_step_pct,
                        order_type = EXCLUDED.order_type,
                        direction = EXCLUDED.direction,
                        dca_enabled = EXCLUDED.dca_enabled,
                        dca_pct_1 = EXCLUDED.dca_pct_1,
                        dca_pct_2 = EXCLUDED.dca_pct_2,
                        max_positions = EXCLUDED.max_positions,
                        coins_group = EXCLUDED.coins_group,
                        trading_mode = EXCLUDED.trading_mode,
                        account_type = EXCLUDED.account_type,
                        updated_at = NOW()
                """, (
                    user_id, strategy, side, exchange,
                    setting.get('enabled', True),
                    setting.get('percent'),
                    setting.get('tp_percent'),
                    setting.get('sl_percent'),
                    setting.get('leverage'),
                    setting.get('use_atr', False),
                    setting.get('atr_trigger_pct'),
                    setting.get('atr_step_pct'),
                    setting.get('order_type', 'market'),
                    setting.get('direction', 'all'),
                    setting.get('dca_enabled', False),
                    setting.get('dca_pct_1', 10.0),
                    setting.get('dca_pct_2', 25.0),
                    setting.get('max_positions', 0),
                    setting.get('coins_group', 'ALL'),
                    setting.get('trading_mode', 'demo'),
                    setting.get('account_type', 'demo')
                ))
                restored += 1
    
    print(f"  ✅ Restored {restored} strategy settings")


def main():
    if len(sys.argv) < 2:
        print("Usage: python restore_user_data.py <backup_file.json>")
        print("Example: python restore_user_data.py user_data_backup_20260125_123456.json")
        sys.exit(1)
    
    backup_file = sys.argv[1]
    
    # Find backup file
    if not os.path.isabs(backup_file):
        # Check in project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        backup_path = os.path.join(project_root, backup_file)
        if not os.path.exists(backup_path):
            print(f"❌ Backup file not found: {backup_file}")
            sys.exit(1)
        backup_file = backup_path
    
    print("=" * 60)
    print("🗄️  DATABASE RESTORE SCRIPT")
    print("=" * 60)
    print(f"📂 Loading backup from: {backup_file}")
    
    with open(backup_file, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
    
    print(f"   Backup timestamp: {backup_data.get('backup_timestamp')}")
    print(f"   Users: {len(backup_data.get('users', []))}")
    print(f"   Strategy Settings: {len(backup_data.get('strategy_settings', []))}")
    print()
    
    restore_users(backup_data.get('users', []))
    restore_strategy_settings(backup_data.get('strategy_settings', []))
    
    print("=" * 60)
    print("✅ Restore completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
