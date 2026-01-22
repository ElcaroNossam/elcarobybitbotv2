"""
Migration: Strategy Settings Table
Version: 005
Created: 2026-01-22

Creates user_strategy_settings table for per-strategy user settings.
"""


def upgrade(cur):
    """Apply migration"""
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_strategy_settings (
            user_id       BIGINT NOT NULL,
            strategy      TEXT NOT NULL,
            settings      JSONB DEFAULT '{}',
            
            -- Override global settings
            tp_percent    REAL,
            sl_percent    REAL,
            leverage      INTEGER,
            use_atr       BOOLEAN,
            
            -- ATR settings per strategy
            atr_periods       INTEGER,
            atr_multiplier_sl REAL,
            atr_trigger_pct   REAL,
            atr_step_pct      REAL,
            
            -- Order settings
            order_type    TEXT DEFAULT 'market',
            direction     TEXT DEFAULT 'all',
            
            enabled       BOOLEAN DEFAULT TRUE,
            updated_at    TIMESTAMP DEFAULT NOW(),
            
            PRIMARY KEY (user_id, strategy)
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_strategy_settings_user ON user_strategy_settings(user_id)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS user_strategy_settings CASCADE")
