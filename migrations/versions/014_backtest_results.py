"""
Migration: Backtest Results Table
Version: 014
Created: 2026-01-22

Creates backtest_results table for saving backtest history.
"""


def upgrade(cur):
    """Apply migration"""
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS backtest_results (
            id            SERIAL PRIMARY KEY,
            user_id       BIGINT NOT NULL,
            name          TEXT,
            
            -- Config
            strategy      TEXT NOT NULL,
            symbol        TEXT NOT NULL,
            timeframe     TEXT NOT NULL,
            start_date    TIMESTAMP,
            end_date      TIMESTAMP,
            
            -- Settings
            initial_capital REAL DEFAULT 10000,
            leverage      INTEGER DEFAULT 10,
            tp_percent    REAL,
            sl_percent    REAL,
            
            -- Results
            total_trades  INTEGER,
            winning_trades INTEGER,
            losing_trades INTEGER,
            win_rate      REAL,
            total_pnl     REAL,
            max_drawdown  REAL,
            sharpe_ratio  REAL,
            profit_factor REAL,
            
            -- Trade log
            trades_json   JSONB,
            equity_curve  JSONB,
            
            created_at    TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_backtest_user ON backtest_results(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_backtest_strategy ON backtest_results(strategy)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS backtest_results CASCADE")
