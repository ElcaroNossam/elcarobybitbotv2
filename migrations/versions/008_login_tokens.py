"""
Migration: Login Tokens Table
Version: 008
Created: 2026-01-22

Creates login_tokens table for Telegram WebApp auto-login.
"""


def upgrade(cur):
    """Apply migration"""
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS login_tokens (
            id            SERIAL PRIMARY KEY,
            token         TEXT UNIQUE NOT NULL,
            user_id       BIGINT NOT NULL,
            created_at    TIMESTAMP DEFAULT NOW(),
            expires_at    TIMESTAMP NOT NULL,
            used          BOOLEAN DEFAULT FALSE,
            used_at       TIMESTAMP,
            ip_address    TEXT,
            user_agent    TEXT
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_login_tokens_token ON login_tokens(token)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_login_tokens_user ON login_tokens(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_login_tokens_expires ON login_tokens(expires_at)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS login_tokens CASCADE")
