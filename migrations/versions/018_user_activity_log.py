"""
Migration: User Activity Log Table
Version: 018
Created: 2026-01-25

Creates user_activity_log table for tracking all user actions
across iOS, WebApp, and Telegram Bot for full synchronization.
"""


def upgrade(cur):
    """Apply migration"""
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_activity_log (
            id              SERIAL PRIMARY KEY,
            user_id         BIGINT NOT NULL,
            
            -- Action details
            action_type     TEXT NOT NULL,       -- 'settings_change', 'trade', 'login', 'exchange_switch'
            action_category TEXT NOT NULL,       -- 'settings', 'trading', 'auth', 'exchange'
            
            -- Source of action
            source          TEXT NOT NULL,       -- 'ios', 'webapp', 'telegram', 'api'
            device_info     TEXT,                -- Device/browser info
            
            -- Change details
            entity_type     TEXT,                -- 'strategy_settings', 'user_settings', 'position', etc.
            entity_id       TEXT,                -- Specific entity identifier
            old_value       JSONB,               -- Previous value
            new_value       JSONB,               -- New value
            
            -- Metadata
            ip_address      TEXT,
            user_agent      TEXT,
            
            -- Notification status
            telegram_notified   BOOLEAN DEFAULT FALSE,
            webapp_notified     BOOLEAN DEFAULT FALSE,
            ios_notified        BOOLEAN DEFAULT FALSE,
            
            created_at      TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Indexes for efficient queries
    cur.execute("CREATE INDEX IF NOT EXISTS idx_activity_user ON user_activity_log(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_activity_type ON user_activity_log(action_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_activity_source ON user_activity_log(source)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_activity_created ON user_activity_log(created_at DESC)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_activity_user_date ON user_activity_log(user_id, created_at DESC)")
    
    # Create notification queue table for pending notifications
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notification_queue (
            id              SERIAL PRIMARY KEY,
            user_id         BIGINT NOT NULL,
            activity_id     INTEGER REFERENCES user_activity_log(id),
            
            -- Target
            target          TEXT NOT NULL,       -- 'telegram', 'webapp', 'ios'
            
            -- Content
            notification_type TEXT NOT NULL,     -- 'settings_changed', 'trade_executed', etc.
            title           TEXT,
            message         TEXT,
            data            JSONB,
            
            -- Status
            status          TEXT DEFAULT 'pending',  -- 'pending', 'sent', 'failed', 'skipped'
            attempts        INTEGER DEFAULT 0,
            last_attempt    TIMESTAMP,
            error_message   TEXT,
            
            created_at      TIMESTAMP DEFAULT NOW(),
            sent_at         TIMESTAMP
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_notif_user ON notification_queue(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_notif_status ON notification_queue(status)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_notif_target ON notification_queue(target)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS notification_queue CASCADE")
    cur.execute("DROP TABLE IF EXISTS user_activity_log CASCADE")
