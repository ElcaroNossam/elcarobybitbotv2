"""
Migration: Add disclaimer_accepted column
Version: 020
Created: 2026-01-28

Adds disclaimer_accepted column to users table for legal compliance.
This is separate from terms_accepted (Terms of Service).
"""


def upgrade(cur):
    """Apply migration"""
    
    # Add disclaimer_accepted column
    cur.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS disclaimer_accepted INTEGER NOT NULL DEFAULT 0
    """)
    
    # Users who already accepted terms should also have disclaimer accepted
    # (they used the bot before disclaimer was added)
    cur.execute("""
        UPDATE users 
        SET disclaimer_accepted = 1 
        WHERE terms_accepted = 1
    """)


def downgrade(cur):
    """Rollback migration"""
    cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS disclaimer_accepted")
