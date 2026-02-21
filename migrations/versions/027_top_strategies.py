"""
Top strategies table for rankings display
"""

def upgrade(cur):
    """Apply migration"""
    
    # Top strategies for rankings
    cur.execute("""
        CREATE TABLE IF NOT EXISTS top_strategies (
            id              SERIAL PRIMARY KEY,
            strategy_type   TEXT NOT NULL,
            strategy_id     INTEGER,
            strategy_name   TEXT NOT NULL,
            win_rate        REAL DEFAULT 0,
            total_pnl       REAL DEFAULT 0,
            total_trades    INTEGER DEFAULT 0,
            sharpe_ratio    REAL DEFAULT 0,
            max_drawdown    REAL DEFAULT 0,
            rank            INTEGER,
            config_json     TEXT,
            updated_at      TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Index for fast rankings lookup
    cur.execute("CREATE INDEX IF NOT EXISTS idx_top_strategies_rank ON top_strategies(rank)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_top_strategies_type ON top_strategies(strategy_type)")
    

def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS top_strategies CASCADE")
