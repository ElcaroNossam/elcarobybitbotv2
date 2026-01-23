"""
Migration: Strategy Settings Table with 3D Schema
Version: 005
Created: 2026-01-22
Updated: 2026-01-23 - Changed to 3D schema (user_id, strategy, side)

Creates user_strategy_settings table for per-strategy per-side user settings.
"""


def upgrade(cur):
    """Apply migration"""
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_strategy_settings (
            user_id       BIGINT NOT NULL,
            strategy      TEXT NOT NULL,
            side          TEXT NOT NULL DEFAULT 'long',
            settings      JSONB DEFAULT '{}',
            
            -- Per-side trading settings
            percent       REAL,
            tp_percent    REAL,
            sl_percent    REAL,
            leverage      INTEGER,
            use_atr       BOOLEAN DEFAULT FALSE,
            
            -- ATR settings per strategy/side
            atr_periods       INTEGER,
            atr_multiplier_sl REAL,
            atr_trigger_pct   REAL,
            atr_step_pct      REAL,
            
            -- Order settings
            order_type        TEXT DEFAULT 'market',
            limit_offset_pct  REAL DEFAULT 0.1,
            direction         TEXT DEFAULT 'all',
            
            -- DCA settings
            dca_enabled   BOOLEAN DEFAULT FALSE,
            dca_pct_1     REAL DEFAULT 10.0,
            dca_pct_2     REAL DEFAULT 25.0,
            
            -- Position limits
            max_positions INTEGER DEFAULT 0,
            coins_group   TEXT DEFAULT 'ALL',
            
            -- Context columns (for future extension)
            trading_mode  TEXT DEFAULT 'demo',
            exchange      TEXT DEFAULT 'bybit',
            account_type  TEXT DEFAULT 'demo',
            
            enabled       BOOLEAN DEFAULT TRUE,
            updated_at    TIMESTAMP DEFAULT NOW(),
            
            PRIMARY KEY (user_id, strategy, side)
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_strategy_settings_user ON user_strategy_settings(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_strategy_settings_strategy ON user_strategy_settings(strategy)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS user_strategy_settings CASCADE")
