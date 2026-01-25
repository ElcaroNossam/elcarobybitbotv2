"""
Migration: Strategy Settings 4D Schema
Version: 018
Created: 2026-01-25

Adds exchange to PRIMARY KEY for per-exchange settings.
Schema changes from 3D (user_id, strategy, side) to 4D (user_id, strategy, side, exchange).

This allows users to have different settings for the same strategy on different exchanges.
"""


def upgrade(cur):
    """Apply migration"""
    
    # Step 1: Drop the old primary key constraint
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        DROP CONSTRAINT IF EXISTS user_strategy_settings_pkey
    """)
    
    # Step 2: Add new composite primary key with exchange
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        ADD PRIMARY KEY (user_id, strategy, side, exchange)
    """)
    
    # Step 3: Create index for faster lookups by user+strategy+exchange
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_uss_user_strat_exchange 
        ON user_strategy_settings(user_id, strategy, exchange)
    """)
    
    # Step 4: Duplicate existing rows for hyperliquid exchange
    # This ensures users have settings for both exchanges by default
    cur.execute("""
        INSERT INTO user_strategy_settings 
            (user_id, strategy, side, exchange, settings, percent, tp_percent, sl_percent,
             leverage, use_atr, atr_periods, atr_multiplier_sl, atr_trigger_pct, atr_step_pct,
             order_type, limit_offset_pct, direction, dca_enabled, dca_pct_1, dca_pct_2,
             max_positions, coins_group, trading_mode, account_type, enabled, updated_at)
        SELECT 
            user_id, strategy, side, 'hyperliquid', settings, percent, tp_percent, sl_percent,
            leverage, use_atr, atr_periods, atr_multiplier_sl, atr_trigger_pct, atr_step_pct,
            order_type, limit_offset_pct, direction, dca_enabled, dca_pct_1, dca_pct_2,
            max_positions, coins_group, trading_mode, account_type, enabled, NOW()
        FROM user_strategy_settings 
        WHERE exchange = 'bybit'
        ON CONFLICT (user_id, strategy, side, exchange) DO NOTHING
    """)
    
    print("  ✅ Migrated strategy settings to 4D schema (user_id, strategy, side, exchange)")


def downgrade(cur):
    """Rollback migration"""
    
    # Remove hyperliquid rows
    cur.execute("""
        DELETE FROM user_strategy_settings WHERE exchange = 'hyperliquid'
    """)
    
    # Drop new primary key
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        DROP CONSTRAINT IF EXISTS user_strategy_settings_pkey
    """)
    
    # Restore old primary key
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        ADD PRIMARY KEY (user_id, strategy, side)
    """)
    
    # Drop new index
    cur.execute("""
        DROP INDEX IF EXISTS idx_uss_user_strat_exchange
    """)
