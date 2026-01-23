"""
Migration: Strategy Marketplace Tables
Version: 017
Created: 2026-01-25

Creates all marketplace-related tables:
- strategy_marketplace: Published strategies for sale
- strategy_purchases: Purchase records
- strategy_ratings: User ratings for strategies
- seller_payouts: Payout requests from sellers
"""


def upgrade(cur):
    """Apply migration"""
    
    # Add missing columns to custom_strategies if needed
    try:
        cur.execute("ALTER TABLE custom_strategies ADD COLUMN IF NOT EXISTS config_json TEXT")
        cur.execute("ALTER TABLE custom_strategies ADD COLUMN IF NOT EXISTS base_strategy TEXT DEFAULT 'custom'")
        cur.execute("ALTER TABLE custom_strategies ADD COLUMN IF NOT EXISTS backtest_results_json TEXT")
        cur.execute("ALTER TABLE custom_strategies ADD COLUMN IF NOT EXISTS visibility TEXT DEFAULT 'private'")
        cur.execute("ALTER TABLE custom_strategies ADD COLUMN IF NOT EXISTS price REAL DEFAULT 0")
        cur.execute("ALTER TABLE custom_strategies ADD COLUMN IF NOT EXISTS performance_stats TEXT")
    except Exception:
        pass  # Columns may already exist
    
    # Strategy Marketplace listings
    cur.execute("""
        CREATE TABLE IF NOT EXISTS strategy_marketplace (
            id              SERIAL PRIMARY KEY,
            strategy_id     INTEGER NOT NULL REFERENCES custom_strategies(id) ON DELETE CASCADE,
            seller_id       BIGINT NOT NULL,
            
            -- Pricing (multiple currencies)
            price_ton       REAL DEFAULT 0,
            price_elc       REAL DEFAULT 0,
            price_usdt      REAL DEFAULT 0,
            
            -- Stats
            total_sales     INTEGER DEFAULT 0,
            rating          REAL DEFAULT 0,
            rating_count    INTEGER DEFAULT 0,
            
            -- Status
            is_active       BOOLEAN DEFAULT TRUE,
            is_featured     BOOLEAN DEFAULT FALSE,
            
            created_at      TIMESTAMP DEFAULT NOW(),
            updated_at      TIMESTAMP DEFAULT NOW(),
            
            UNIQUE(strategy_id)
        )
    """)
    
    # Purchase records
    cur.execute("""
        CREATE TABLE IF NOT EXISTS strategy_purchases (
            id              SERIAL PRIMARY KEY,
            marketplace_id  INTEGER REFERENCES strategy_marketplace(id),
            strategy_id     INTEGER NOT NULL REFERENCES custom_strategies(id),
            buyer_id        BIGINT NOT NULL,
            seller_id       BIGINT NOT NULL,
            
            -- Transaction
            amount_paid     REAL NOT NULL,
            currency        TEXT DEFAULT 'USDT',
            seller_share    REAL,
            platform_share  REAL,
            tx_hash         TEXT,
            
            -- Status
            is_active       BOOLEAN DEFAULT TRUE,
            
            purchased_at    BIGINT,
            
            UNIQUE(strategy_id, buyer_id)
        )
    """)
    
    # Strategy ratings
    cur.execute("""
        CREATE TABLE IF NOT EXISTS strategy_ratings (
            id              SERIAL PRIMARY KEY,
            strategy_id     INTEGER NOT NULL REFERENCES custom_strategies(id) ON DELETE CASCADE,
            marketplace_id  INTEGER REFERENCES strategy_marketplace(id),
            user_id         BIGINT NOT NULL,
            
            rating          INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            review          TEXT,
            
            created_at      BIGINT,
            updated_at      TIMESTAMP DEFAULT NOW(),
            
            UNIQUE(strategy_id, user_id),
            UNIQUE(marketplace_id, user_id)
        )
    """)
    
    # Seller payouts
    cur.execute("""
        CREATE TABLE IF NOT EXISTS seller_payouts (
            id              SERIAL PRIMARY KEY,
            seller_id       BIGINT NOT NULL,
            
            amount          REAL NOT NULL,
            currency        TEXT DEFAULT 'USDT',
            
            -- Payout details
            wallet_address  TEXT,
            tx_hash         TEXT,
            
            -- Status: pending, completed, failed
            status          TEXT DEFAULT 'pending',
            
            requested_at    TIMESTAMP DEFAULT NOW(),
            processed_at    TIMESTAMP
        )
    """)
    
    # Licenses table for admin
    cur.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
            id              SERIAL PRIMARY KEY,
            license_key     TEXT UNIQUE NOT NULL,
            license_type    TEXT DEFAULT 'premium',
            user_id         BIGINT,
            
            days            INTEGER DEFAULT 30,
            is_active       BOOLEAN DEFAULT TRUE,
            
            created_at      TIMESTAMP DEFAULT NOW(),
            expires_at      TIMESTAMP
        )
    """)
    
    # Strategy deployments (for live trading)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS strategy_deployments (
            id                      SERIAL PRIMARY KEY,
            strategy_name           TEXT NOT NULL,
            strategy_id             INTEGER REFERENCES custom_strategies(id),
            user_id                 BIGINT,
            
            params_json             TEXT,
            backtest_results_json   TEXT,
            
            is_active               BOOLEAN DEFAULT TRUE,
            deployed_at             TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Live deployments
    cur.execute("""
        CREATE TABLE IF NOT EXISTS live_deployments (
            id              SERIAL PRIMARY KEY,
            strategy_id     INTEGER NOT NULL REFERENCES custom_strategies(id) ON DELETE CASCADE,
            user_id         BIGINT NOT NULL,
            strategy_name   TEXT,
            
            -- Settings
            symbols         TEXT DEFAULT 'ALL',
            exchange        TEXT DEFAULT 'bybit',
            account_type    TEXT DEFAULT 'demo',
            leverage        INTEGER DEFAULT 10,
            config_json     TEXT,
            
            -- Status: active, paused, stopped
            status          TEXT DEFAULT 'active',
            
            -- Stats
            trades_count    INTEGER DEFAULT 0,
            pnl_usd         REAL DEFAULT 0,
            win_rate        REAL DEFAULT 0,
            backtest_pnl    REAL DEFAULT 0,
            total_trades    INTEGER DEFAULT 0,
            total_pnl       REAL DEFAULT 0,
            
            started_at      TIMESTAMP DEFAULT NOW(),
            stopped_at      TIMESTAMP,
            
            UNIQUE(user_id, strategy_id)
        )
    """)
    
    # Indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_marketplace_seller ON strategy_marketplace(seller_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_marketplace_active ON strategy_marketplace(is_active)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_marketplace_featured ON strategy_marketplace(is_featured)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_purchases_buyer ON strategy_purchases(buyer_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_purchases_seller ON strategy_purchases(seller_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ratings_strategy ON strategy_ratings(strategy_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_payouts_seller ON seller_payouts(seller_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_payouts_status ON seller_payouts(status)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_deployments_user ON live_deployments(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_deployments_status ON live_deployments(status)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS live_deployments CASCADE")
    cur.execute("DROP TABLE IF EXISTS strategy_deployments CASCADE")
    cur.execute("DROP TABLE IF EXISTS licenses CASCADE")
    cur.execute("DROP TABLE IF EXISTS seller_payouts CASCADE")
    cur.execute("DROP TABLE IF EXISTS strategy_ratings CASCADE")
    cur.execute("DROP TABLE IF EXISTS strategy_purchases CASCADE")
    cur.execute("DROP TABLE IF EXISTS strategy_marketplace CASCADE")
