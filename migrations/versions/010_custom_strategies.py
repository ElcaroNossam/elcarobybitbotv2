"""
Migration: Custom Strategies Table
Version: 010
Created: 2026-01-22

Creates custom_strategies table for user-defined strategies.
"""


def upgrade(cur):
    """Apply migration"""
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS custom_strategies (
            id            SERIAL PRIMARY KEY,
            user_id       BIGINT NOT NULL,
            name          TEXT NOT NULL,
            description   TEXT,
            
            -- Strategy logic
            entry_conditions   JSONB DEFAULT '[]',
            exit_conditions    JSONB DEFAULT '[]',
            indicators         JSONB DEFAULT '[]',
            
            -- Settings
            timeframe     TEXT DEFAULT '15m',
            symbols       TEXT DEFAULT 'ALL',
            tp_percent    REAL DEFAULT 8.0,
            sl_percent    REAL DEFAULT 3.0,
            leverage      INTEGER DEFAULT 10,
            
            -- Status
            is_active     BOOLEAN DEFAULT FALSE,
            is_public     BOOLEAN DEFAULT FALSE,
            
            -- Stats
            total_trades  INTEGER DEFAULT 0,
            win_rate      REAL,
            total_pnl     REAL DEFAULT 0,
            
            created_at    TIMESTAMP DEFAULT NOW(),
            updated_at    TIMESTAMP DEFAULT NOW(),
            
            UNIQUE(user_id, name)
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_custom_strategies_user ON custom_strategies(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_custom_strategies_public ON custom_strategies(is_public)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS custom_strategies CASCADE")
