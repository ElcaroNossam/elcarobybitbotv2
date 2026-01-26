"""
Migration: Strategy Settings Table with 4D Schema
Version: 005
Created: 2026-01-25
Updated: 2026-01-25 - Unified 4D schema (user_id, strategy, side, exchange)

Creates user_strategy_settings table for per-strategy per-side per-exchange user settings.

4D SCHEMA: PRIMARY KEY = (user_id, strategy, side, exchange)
- Each user can have different settings per strategy
- Each strategy can have different settings for long vs short
- Each side can have different settings per exchange (bybit/hyperliquid)
"""


def upgrade(cur):
    """Apply migration"""
    
    # Drop old table if exists (for clean migration)
    cur.execute("DROP TABLE IF EXISTS user_strategy_settings CASCADE")
    
    cur.execute("""
        CREATE TABLE user_strategy_settings (
            -- PRIMARY KEY: 4D multitenancy
            user_id       BIGINT NOT NULL,
            strategy      TEXT NOT NULL,
            side          TEXT NOT NULL DEFAULT 'long',
            exchange      TEXT NOT NULL DEFAULT 'bybit',
            
            -- JSON settings (for future flexibility)
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
            
            -- Break-Even settings (move SL to entry price)
            be_enabled        BOOLEAN DEFAULT FALSE,
            be_trigger_pct    REAL DEFAULT 1.0,
            
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
            
            -- Context columns
            trading_mode  TEXT DEFAULT 'demo',
            account_type  TEXT DEFAULT 'demo',
            
            enabled       BOOLEAN DEFAULT TRUE,
            updated_at    TIMESTAMP DEFAULT NOW(),
            
            -- 4D PRIMARY KEY
            PRIMARY KEY (user_id, strategy, side, exchange)
        )
    """)
    
    # Indexes for fast lookups
    cur.execute("CREATE INDEX IF NOT EXISTS idx_uss_user ON user_strategy_settings(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_uss_strategy ON user_strategy_settings(strategy)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_uss_user_strat ON user_strategy_settings(user_id, strategy)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_uss_user_strat_exchange ON user_strategy_settings(user_id, strategy, exchange)")
    
    print("  ✅ Created user_strategy_settings with 4D schema (user_id, strategy, side, exchange)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS user_strategy_settings CASCADE")
