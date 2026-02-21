"""
Migration 026: Add be_offset_pct column to user_strategy_settings
Created: Feb 22, 2026

Adds configurable Break-Even offset % per strategy/side.
Instead of moving SL to exact entry price, moves it to entry + offset%.
Default: 0.15% (locks in small profit on BE activation).
"""


def upgrade(cur):
    """Apply migration - add be_offset_pct to user_strategy_settings."""
    
    cur.execute("""
        ALTER TABLE user_strategy_settings 
        ADD COLUMN IF NOT EXISTS be_offset_pct REAL DEFAULT 0.15
    """)
    
    print("✅ Added be_offset_pct column to user_strategy_settings")


def downgrade(cur):
    """Rollback migration - remove be_offset_pct column."""
    
    cur.execute("ALTER TABLE user_strategy_settings DROP COLUMN IF EXISTS be_offset_pct")
    
    print("✅ Removed be_offset_pct column from user_strategy_settings")
