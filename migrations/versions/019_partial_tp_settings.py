"""
Migration: Partial Take Profit (срез маржи) settings
Version: 019
Created: 2026-01-26

Adds partial take profit columns to user_strategy_settings table.
This allows closing part of position at specific profit levels in 2 steps.
"""


def upgrade(cur):
    """Apply migration - add Partial TP columns"""
    
    # Check if columns already exist
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'user_strategy_settings' AND column_name = 'partial_tp_enabled'
    """)
    if cur.fetchone():
        print("  ⏭️ Partial TP columns already exist, skipping...")
        return
    
    # Add Partial TP columns
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        ADD COLUMN IF NOT EXISTS partial_tp_enabled BOOLEAN DEFAULT FALSE
    """)
    
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        ADD COLUMN IF NOT EXISTS partial_tp_1_trigger_pct REAL DEFAULT 2.0
    """)
    
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        ADD COLUMN IF NOT EXISTS partial_tp_1_close_pct REAL DEFAULT 30.0
    """)
    
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        ADD COLUMN IF NOT EXISTS partial_tp_2_trigger_pct REAL DEFAULT 5.0
    """)
    
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        ADD COLUMN IF NOT EXISTS partial_tp_2_close_pct REAL DEFAULT 30.0
    """)
    
    print("  ✅ Added Partial TP columns to user_strategy_settings")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("ALTER TABLE user_strategy_settings DROP COLUMN IF EXISTS partial_tp_enabled")
    cur.execute("ALTER TABLE user_strategy_settings DROP COLUMN IF EXISTS partial_tp_1_trigger_pct")
    cur.execute("ALTER TABLE user_strategy_settings DROP COLUMN IF EXISTS partial_tp_1_close_pct")
    cur.execute("ALTER TABLE user_strategy_settings DROP COLUMN IF EXISTS partial_tp_2_trigger_pct")
    cur.execute("ALTER TABLE user_strategy_settings DROP COLUMN IF EXISTS partial_tp_2_close_pct")
    print("  ✅ Removed Partial TP columns from user_strategy_settings")
