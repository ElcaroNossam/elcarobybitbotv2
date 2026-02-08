"""
Migration: Exchange-level coins group settings
Version: 025
Created: 2026-02-10

Adds bybit_coins_group and hl_coins_group to users table.
This simplifies settings - coins filter is now per-exchange instead of per-strategy.
"""


def upgrade(cur):
    """Apply migration"""
    # Add coins_group columns for each exchange
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS bybit_coins_group TEXT DEFAULT 'ALL'")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS hl_coins_group TEXT DEFAULT 'ALL'")
    
    # Create index for quick lookups
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_bybit_coins ON users(bybit_coins_group)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_hl_coins ON users(hl_coins_group)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP INDEX IF EXISTS idx_users_bybit_coins")
    cur.execute("DROP INDEX IF EXISTS idx_users_hl_coins")
    cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS bybit_coins_group")
    cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS hl_coins_group")
