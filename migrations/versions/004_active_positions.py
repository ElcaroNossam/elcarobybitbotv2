"""
Migration: Active Positions Table
Version: 004
Created: 2026-01-22

Creates active_positions table for tracking open positions.
"""


def upgrade(cur):
    """Apply migration"""
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS active_positions (
            user_id       BIGINT NOT NULL,
            symbol        TEXT NOT NULL,
            account_type  TEXT NOT NULL DEFAULT 'demo',
            
            side          TEXT,
            qty           REAL,
            entry_price   REAL,
            current_price REAL,
            pnl           REAL,
            pnl_pct       REAL,
            
            tp_price      REAL,
            sl_price      REAL,
            leverage      INTEGER,
            
            strategy      TEXT,
            signal_id     INTEGER,
            exchange      TEXT DEFAULT 'bybit',
            
            -- Trailing stop
            trailing_active    BOOLEAN DEFAULT FALSE,
            trailing_trigger   REAL,
            trailing_distance  REAL,
            highest_pnl        REAL,
            
            -- DCA
            dca_count     INTEGER DEFAULT 0,
            avg_entry     REAL,
            
            opened_at     TIMESTAMP DEFAULT NOW(),
            updated_at    TIMESTAMP DEFAULT NOW(),
            
            PRIMARY KEY (user_id, symbol, account_type)
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_positions_user ON active_positions(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_positions_symbol ON active_positions(symbol)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS active_positions CASCADE")
