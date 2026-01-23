"""
Migration: Trade Logs Table
Version: 003
Created: 2026-01-22
Updated: 2026-01-24 - Added all signal analytics columns

Creates trade_logs table for completed trades history.
"""


def upgrade(cur):
    """Apply migration"""
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trade_logs (
            id            SERIAL PRIMARY KEY,
            user_id       BIGINT NOT NULL,
            signal_id     INTEGER,
            symbol        TEXT NOT NULL,
            side          TEXT NOT NULL,
            qty           REAL NOT NULL,
            entry_price   REAL,
            exit_price    REAL,
            pnl           REAL,
            pnl_pct       REAL,
            ts            TIMESTAMP DEFAULT NOW(),
            closed_at     TIMESTAMP,
            status        TEXT DEFAULT 'open',
            order_id      TEXT,
            strategy      TEXT,
            account_type  TEXT DEFAULT 'demo',
            exchange      TEXT DEFAULT 'bybit',
            fee           REAL DEFAULT 0,
            notes         TEXT,
            exit_reason   TEXT,
            sl_pct        REAL,
            tp_pct        REAL,
            timeframe     TEXT,
            source        TEXT DEFAULT 'api',
            leverage      REAL,
            signal_source TEXT,
            sl_price      REAL,
            tp_price      REAL,
            entry_ts      BIGINT,
            exit_ts       BIGINT,
            exit_order_type TEXT,
            rsi           REAL,
            bb_hi         REAL,
            bb_lo         REAL,
            vol_delta     REAL,
            oi_prev       REAL,
            oi_now        REAL,
            oi_chg        REAL,
            vol_from      REAL,
            vol_to        REAL,
            price_chg     REAL
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trade_logs_user ON trade_logs(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trade_logs_symbol ON trade_logs(symbol)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trade_logs_ts ON trade_logs(ts)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trade_logs_status ON trade_logs(status)")
    # Performance indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trade_logs_user_ts ON trade_logs(user_id, ts DESC)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trade_logs_user_acc ON trade_logs(user_id, account_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trade_logs_user_strat ON trade_logs(user_id, strategy)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_trade_logs_user_acc_ts ON trade_logs(user_id, account_type, ts DESC)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS trade_logs CASCADE")
