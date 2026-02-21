"""
Migration 025: Add auto-close settings per exchange
Created: Feb 21, 2026

Adds columns for scheduled auto-close of positions:
- bybit_auto_close_enabled, bybit_auto_close_time, bybit_auto_close_timezone
- hl_auto_close_enabled, hl_auto_close_time, hl_auto_close_timezone

Default behavior: OFF (auto-close disabled)
Time format: HH:MM in UTC (or specified timezone)
"""


def upgrade(cur):
    """Apply migration - add auto-close columns to users table."""
    
    # Bybit auto-close settings
    cur.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS bybit_auto_close_enabled BOOLEAN DEFAULT FALSE
    """)
    cur.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS bybit_auto_close_time TEXT
    """)
    cur.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS bybit_auto_close_timezone TEXT DEFAULT 'UTC'
    """)
    
    # HyperLiquid auto-close settings
    cur.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS hl_auto_close_enabled BOOLEAN DEFAULT FALSE
    """)
    cur.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS hl_auto_close_time TEXT
    """)
    cur.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS hl_auto_close_timezone TEXT DEFAULT 'UTC'
    """)
    
    print("✅ Added auto-close columns to users table")


def downgrade(cur):
    """Rollback migration - remove auto-close columns."""
    
    cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS bybit_auto_close_enabled")
    cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS bybit_auto_close_time")
    cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS bybit_auto_close_timezone")
    cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS hl_auto_close_enabled")
    cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS hl_auto_close_time")
    cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS hl_auto_close_timezone")
    
    print("✅ Removed auto-close columns from users table")
