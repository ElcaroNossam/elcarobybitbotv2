"""
Migration 025: Add trade_manual flag for manual position monitoring

When enabled:
- Bot will monitor positions opened manually on exchange (without strategy)
- Set SL/TP based on "manual" strategy settings
- Apply ATR trailing if configured

When disabled:
- Bot ignores positions without detected strategy
- No SL/TP will be set for manual positions
"""

def upgrade(cur):
    """Add trade_manual column to users table."""
    cur.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS trade_manual INTEGER DEFAULT 1
    """)
    # Default to 1 (enabled) for backward compatibility


def downgrade(cur):
    """Remove trade_manual column."""
    cur.execute("""
        ALTER TABLE users DROP COLUMN IF EXISTS trade_manual
    """)
