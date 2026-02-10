"""
Migration: Payment History Table
Version: 006
Created: 2026-01-22

Creates payment_history table for subscription payments.
"""


def upgrade(cur):
    """Apply migration"""
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payment_history (
            id                  SERIAL PRIMARY KEY,
            user_id             BIGINT NOT NULL,
            amount              REAL NOT NULL,
            currency            TEXT DEFAULT 'USD',
            payment_type        TEXT,
            status              TEXT DEFAULT 'pending',
            
            license_type        TEXT,
            license_id          INTEGER,
            period_days         INTEGER,
            
            tx_hash             TEXT,
            transaction_id      TEXT,
            telegram_charge_id  TEXT,
            payment_method      TEXT,
            plan_type           TEXT,
            
            wallet_from         TEXT,
            wallet_to           TEXT,
            network             TEXT,
            
            created_at          TIMESTAMP DEFAULT NOW(),
            confirmed_at        TIMESTAMP,
            
            metadata            JSONB DEFAULT '{}'
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_payments_user ON payment_history(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_payments_status ON payment_history(status)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_payments_tx ON payment_history(tx_hash)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS payment_history CASCADE")
