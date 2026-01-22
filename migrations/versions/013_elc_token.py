"""
Migration: ELC Token Tables
Version: 013
Created: 2026-01-22

Creates ELC token related tables (purchases, staking, transactions).
"""


def upgrade(cur):
    """Apply migration"""
    
    # ELC Purchases
    cur.execute("""
        CREATE TABLE IF NOT EXISTS elc_purchases (
            id            SERIAL PRIMARY KEY,
            user_id       BIGINT NOT NULL,
            amount_usd    REAL NOT NULL,
            amount_elc    REAL NOT NULL,
            price_per_elc REAL NOT NULL,
            status        TEXT DEFAULT 'pending',
            payment_method TEXT,
            tx_hash       TEXT,
            created_at    TIMESTAMP DEFAULT NOW(),
            completed_at  TIMESTAMP
        )
    """)
    
    # ELC Staking
    cur.execute("""
        CREATE TABLE IF NOT EXISTS elc_staking (
            id            SERIAL PRIMARY KEY,
            user_id       BIGINT NOT NULL,
            amount        REAL NOT NULL,
            apy_rate      REAL NOT NULL,
            start_date    TIMESTAMP DEFAULT NOW(),
            unlock_date   TIMESTAMP,
            status        TEXT DEFAULT 'active',
            rewards_claimed REAL DEFAULT 0
        )
    """)
    
    # ELC Transactions (transfers, burns, etc.)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS elc_transactions (
            id            SERIAL PRIMARY KEY,
            user_id       BIGINT NOT NULL,
            tx_type       TEXT NOT NULL,
            amount        REAL NOT NULL,
            balance_after REAL,
            reference_id  INTEGER,
            description   TEXT,
            created_at    TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_elc_purchases_user ON elc_purchases(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_elc_staking_user ON elc_staking(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_elc_transactions_user ON elc_transactions(user_id)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS elc_transactions CASCADE")
    cur.execute("DROP TABLE IF EXISTS elc_staking CASCADE")
    cur.execute("DROP TABLE IF EXISTS elc_purchases CASCADE")
