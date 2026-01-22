"""
Migration: User Pending Inputs Table
Version: 012
Created: 2026-01-22

Creates user_pending_inputs table for conversation state persistence.
"""


def upgrade(cur):
    """Apply migration"""
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_pending_inputs (
            user_id       BIGINT PRIMARY KEY,
            input_type    TEXT NOT NULL,
            input_data    TEXT,
            created_at    TIMESTAMP DEFAULT NOW()
        )
    """)


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS user_pending_inputs CASCADE")
