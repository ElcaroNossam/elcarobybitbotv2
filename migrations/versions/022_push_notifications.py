"""
Migration: Push Notifications Infrastructure
Version: 022
Created: 2026-01-30

Updates for push notifications:
- user_devices: Add missing columns (device_token as alias for push_token, is_active, device_name)
- notification_preferences: User notification settings
- Updates notification_queue: Adds is_read, read_at columns
"""


def upgrade(cur):
    """Apply migration"""
    
    # Check if user_devices table exists and update it
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'user_devices'
    """)
    existing_columns = [row[0] for row in cur.fetchall()]
    
    if not existing_columns:
        # Create new table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_devices (
                id              SERIAL PRIMARY KEY,
                user_id         BIGINT NOT NULL,
                device_token    TEXT NOT NULL,
                platform        TEXT NOT NULL,        -- 'ios', 'android', 'web'
                device_name     TEXT,
                app_version     TEXT,
                os_version      TEXT,
                is_active       BOOLEAN DEFAULT TRUE,
                created_at      TIMESTAMP DEFAULT NOW(),
                updated_at      TIMESTAMP DEFAULT NOW(),
                
                UNIQUE(device_token)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_devices_user ON user_devices(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_devices_token ON user_devices(device_token)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_devices_active ON user_devices(user_id, is_active)")
    else:
        # Add missing columns to existing table
        if 'device_token' not in existing_columns and 'push_token' in existing_columns:
            # Rename push_token to device_token for consistency
            cur.execute("ALTER TABLE user_devices RENAME COLUMN push_token TO device_token")
        
        if 'is_active' not in existing_columns:
            cur.execute("ALTER TABLE user_devices ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
        
        if 'device_name' not in existing_columns:
            cur.execute("ALTER TABLE user_devices ADD COLUMN device_name TEXT")
        
        if 'updated_at' not in existing_columns:
            cur.execute("ALTER TABLE user_devices ADD COLUMN updated_at TIMESTAMP DEFAULT NOW()")
        
        # Create indexes if they don't exist
        cur.execute("CREATE INDEX IF NOT EXISTS idx_devices_user ON user_devices(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_devices_active ON user_devices(user_id, is_active)")
    
    # Notification preferences table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notification_preferences (
            user_id                 BIGINT PRIMARY KEY,
            
            -- Main toggles
            trades_enabled          BOOLEAN DEFAULT TRUE,
            signals_enabled         BOOLEAN DEFAULT TRUE,
            price_alerts_enabled    BOOLEAN DEFAULT TRUE,
            daily_report_enabled    BOOLEAN DEFAULT TRUE,
            
            -- Sound & Vibration
            sound_enabled           BOOLEAN DEFAULT TRUE,
            vibration_enabled       BOOLEAN DEFAULT TRUE,
            
            -- Specific notification types
            trade_opened            BOOLEAN DEFAULT TRUE,
            trade_closed            BOOLEAN DEFAULT TRUE,
            break_even              BOOLEAN DEFAULT TRUE,
            partial_tp              BOOLEAN DEFAULT TRUE,
            margin_warning          BOOLEAN DEFAULT TRUE,
            
            created_at              TIMESTAMP DEFAULT NOW(),
            updated_at              TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Add is_read column to notification_queue if not exists
    cur.execute("""
        ALTER TABLE notification_queue 
        ADD COLUMN IF NOT EXISTS is_read BOOLEAN DEFAULT FALSE
    """)
    
    cur.execute("""
        ALTER TABLE notification_queue 
        ADD COLUMN IF NOT EXISTS read_at TIMESTAMP
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_notif_unread ON notification_queue(user_id, is_read)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS notification_preferences CASCADE")
    cur.execute("DROP TABLE IF EXISTS user_devices CASCADE")
    cur.execute("ALTER TABLE notification_queue DROP COLUMN IF EXISTS is_read")
    cur.execute("ALTER TABLE notification_queue DROP COLUMN IF EXISTS read_at")
