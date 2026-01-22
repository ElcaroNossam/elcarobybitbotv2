"""
Migration: User Devices Table
Version: 011
Created: 2026-01-22

Creates user_devices table for push notifications.
"""


def upgrade(cur):
    """Apply migration"""
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_devices (
            id            SERIAL PRIMARY KEY,
            user_id       BIGINT NOT NULL,
            device_id     TEXT NOT NULL,
            device_type   TEXT,
            push_token    TEXT,
            app_version   TEXT,
            os_version    TEXT,
            last_active   TIMESTAMP DEFAULT NOW(),
            created_at    TIMESTAMP DEFAULT NOW(),
            
            UNIQUE(user_id, device_id)
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_user_devices_user ON user_devices(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_user_devices_push ON user_devices(push_token) WHERE push_token IS NOT NULL")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS user_devices CASCADE")
