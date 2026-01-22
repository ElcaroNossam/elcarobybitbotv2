"""
Migration: Active Positions Table
Version: 004
Created: 2026-01-22

Creates active_positions table for tracking open positions.
Synchronized with core/db_postgres.py schema.
"""


def upgrade(cur):
    """Apply migration"""
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS active_positions (
            user_id      BIGINT NOT NULL,
            symbol       TEXT NOT NULL,
            account_type TEXT NOT NULL DEFAULT 'demo',
            side         TEXT,
            entry_price  REAL,
            size         REAL,
            qty          REAL,
            open_ts      TIMESTAMP NOT NULL DEFAULT NOW(),
            opened_at    TIMESTAMP DEFAULT NOW(),
            timeframe    TEXT,
            signal_id    INTEGER,
            dca_10_done  INTEGER NOT NULL DEFAULT 0,
            dca_25_done  INTEGER NOT NULL DEFAULT 0,
            dca_count    INTEGER DEFAULT 0,
            avg_entry    REAL,
            strategy     TEXT,
            leverage     INTEGER,
            sl_price     REAL,
            tp_price     REAL,
            current_price REAL,
            pnl          REAL,
            pnl_pct      REAL,
            exchange     TEXT DEFAULT 'bybit',
            env          TEXT,
            source       TEXT DEFAULT 'bot',
            opened_by    TEXT DEFAULT 'bot',
            manual_sltp_override INTEGER DEFAULT 0,
            manual_sltp_ts       BIGINT,
            atr_activated        INTEGER DEFAULT 0,
            atr_activation_price REAL,
            atr_last_stop_price  REAL,
            atr_last_update_ts   BIGINT,
            use_atr              INTEGER DEFAULT 0,
            applied_sl_pct       REAL,
            applied_tp_pct       REAL,
            client_order_id      TEXT,
            exchange_order_id    TEXT,
            trailing_active      BOOLEAN DEFAULT FALSE,
            trailing_trigger     REAL,
            trailing_distance    REAL,
            highest_pnl          REAL,
            updated_at           TIMESTAMP DEFAULT NOW(),
            PRIMARY KEY(user_id, symbol, account_type)
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_active_user ON active_positions(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_active_account ON active_positions(user_id, account_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_active_exchange ON active_positions(user_id, exchange, account_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_positions_user ON active_positions(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_positions_symbol ON active_positions(symbol)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS active_positions CASCADE")
