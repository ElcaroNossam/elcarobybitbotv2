"""
Migration: Signals Table
Version: 002
Created: 2026-01-22

Creates signals table for trading signal history.
"""


def upgrade(cur):
    """Apply migration"""
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id          SERIAL PRIMARY KEY,
            raw_message TEXT,
            ts          TIMESTAMP NOT NULL DEFAULT NOW(),
            tf          TEXT,
            side        TEXT,
            symbol      TEXT,
            price       REAL,
            strategy    TEXT,
            entry_price REAL,
            sl_price    REAL,
            tp_price    REAL,
            timeframe   TEXT,
            raw_json    TEXT,
            oi_prev     REAL,
            oi_now      REAL,
            oi_chg      REAL,
            vol_from    REAL,
            vol_to      REAL,
            price_chg   REAL,
            vol_delta   REAL,
            rsi         REAL,
            bb_status   TEXT,
            atr_value   REAL,
            bb_hi       REAL,
            bb_lo       REAL
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_signals_ts ON signals(ts)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_signals_strategy ON signals(strategy)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS signals CASCADE")
