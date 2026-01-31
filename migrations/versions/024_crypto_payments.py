"""
Migration: Crypto Payments Table (OxaPay)
Version: 024
Created: 2026-01-31

Creates crypto_payments table for OxaPay payment tracking.
Supports multiple cryptocurrencies, auto-approval, webhooks.
"""


def upgrade(cur):
    """Apply migration"""
    
    # Main crypto payments table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS crypto_payments (
            id              SERIAL PRIMARY KEY,
            payment_id      TEXT UNIQUE NOT NULL,
            user_id         BIGINT NOT NULL,
            track_id        TEXT,
            
            -- Amount info
            amount_usd      DECIMAL(12, 2) NOT NULL,
            amount_crypto   DECIMAL(18, 8),
            paid_amount     DECIMAL(18, 8),
            
            -- Crypto details
            currency        TEXT DEFAULT 'USDT',
            network         TEXT DEFAULT 'TRC20',
            address         TEXT,
            tx_hash         TEXT,
            
            -- Subscription info
            plan            TEXT NOT NULL,
            duration        TEXT NOT NULL,
            
            -- Status tracking
            status          TEXT DEFAULT 'pending',
            webhook_data    TEXT,
            
            -- Timestamps
            created_at      TIMESTAMP DEFAULT NOW(),
            updated_at      TIMESTAMP DEFAULT NOW(),
            expires_at      TIMESTAMP,
            confirmed_at    TIMESTAMP,
            
            -- Payment provider
            provider        TEXT DEFAULT 'oxapay'
        )
    """)
    
    # Indexes for fast lookups
    cur.execute("CREATE INDEX IF NOT EXISTS idx_crypto_payments_user ON crypto_payments(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_crypto_payments_status ON crypto_payments(status)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_crypto_payments_track ON crypto_payments(track_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_crypto_payments_created ON crypto_payments(created_at DESC)")
    
    # Promo codes table (for discount codes)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS promo_codes (
            id              SERIAL PRIMARY KEY,
            code            TEXT UNIQUE NOT NULL,
            discount_pct    INTEGER DEFAULT 0,
            discount_amount DECIMAL(10, 2) DEFAULT 0,
            plan_type       TEXT,
            max_uses        INTEGER DEFAULT 1,
            used_count      INTEGER DEFAULT 0,
            valid_from      TIMESTAMP DEFAULT NOW(),
            valid_until     TIMESTAMP,
            is_active       BOOLEAN DEFAULT TRUE,
            created_by      BIGINT,
            created_at      TIMESTAMP DEFAULT NOW(),
            notes           TEXT
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_promo_codes_code ON promo_codes(code)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_promo_codes_active ON promo_codes(is_active, valid_until)")
    
    # Promo code usage tracking
    cur.execute("""
        CREATE TABLE IF NOT EXISTS promo_code_usage (
            id              SERIAL PRIMARY KEY,
            code_id         INTEGER REFERENCES promo_codes(id),
            user_id         BIGINT NOT NULL,
            payment_id      TEXT,
            discount_applied DECIMAL(10, 2),
            used_at         TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_promo_usage_user ON promo_code_usage(user_id)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS promo_code_usage CASCADE")
    cur.execute("DROP TABLE IF EXISTS promo_codes CASCADE")
    cur.execute("DROP TABLE IF EXISTS crypto_payments CASCADE")
