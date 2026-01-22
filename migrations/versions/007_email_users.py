"""
Migration: Email Users Table
Version: 007
Created: 2026-01-22

Creates email_users table for web login authentication.
"""


def upgrade(cur):
    """Apply migration"""
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS email_users (
            id              SERIAL PRIMARY KEY,
            user_id         BIGINT UNIQUE NOT NULL,
            email           TEXT UNIQUE NOT NULL,
            password_hash   TEXT NOT NULL,
            password_salt   TEXT NOT NULL,
            name            TEXT,
            is_verified     BOOLEAN DEFAULT FALSE,
            verification_code TEXT,
            verification_expires TIMESTAMP,
            last_login      TIMESTAMP,
            created_at      TIMESTAMP DEFAULT NOW(),
            updated_at      TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_email_users_email ON email_users(email)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_email_users_user_id ON email_users(user_id)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS email_users CASCADE")
