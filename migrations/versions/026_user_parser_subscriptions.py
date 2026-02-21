"""
Migration: User Parser Subscriptions & Marketplace Integration
Version: 026
Created: 2026-02-21

Creates:
- user_parser_subscriptions: Track which dynamic parsers each user has enabled
- Adds marketplace columns to user_strategy_deployments
"""


def upgrade(cur):
    """Apply migration"""
    
    # User Parser Subscriptions - which dynamic parsers each user has enabled for trading
    # CRITICAL: System parsers (is_system=TRUE) are like the built-in 6 strategies -
    # users enable/disable them per-user without needing a full deployment.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_parser_subscriptions (
            id              SERIAL PRIMARY KEY,
            user_id         BIGINT NOT NULL,
            parser_id       INTEGER NOT NULL REFERENCES dynamic_signal_parsers(id) ON DELETE CASCADE,
            
            -- Settings (override parser defaults)
            is_active       BOOLEAN DEFAULT TRUE,
            settings_json   JSONB DEFAULT '{}',
            
            -- Per-side settings
            long_enabled    BOOLEAN DEFAULT TRUE,
            short_enabled   BOOLEAN DEFAULT TRUE,
            entry_percent   REAL,
            stop_loss_pct   REAL,
            take_profit_pct REAL,
            leverage        INTEGER,
            use_atr         BOOLEAN DEFAULT FALSE,
            dca_enabled     BOOLEAN DEFAULT FALSE,
            
            -- Tracking
            created_at      TIMESTAMP DEFAULT NOW(),
            updated_at      TIMESTAMP DEFAULT NOW(),
            total_trades    INTEGER DEFAULT 0,
            total_pnl       REAL DEFAULT 0,
            
            UNIQUE(user_id, parser_id)
        )
    """)
    
    # Add marketplace columns to user_strategy_deployments
    try:
        # Link to marketplace listing (if sold)
        cur.execute("ALTER TABLE user_strategy_deployments ADD COLUMN IF NOT EXISTS marketplace_listing_id INTEGER REFERENCES strategy_marketplace(id)")
        # Link to custom_strategies (for marketplace integration)
        cur.execute("ALTER TABLE user_strategy_deployments ADD COLUMN IF NOT EXISTS custom_strategy_id INTEGER REFERENCES custom_strategies(id)")
        # Source purchase (if bought from marketplace)
        cur.execute("ALTER TABLE user_strategy_deployments ADD COLUMN IF NOT EXISTS purchase_id INTEGER REFERENCES strategy_purchases(id)")
        # Is this a public shareable strategy?
        cur.execute("ALTER TABLE user_strategy_deployments ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE")
        # Price if listed on marketplace
        cur.execute("ALTER TABLE user_strategy_deployments ADD COLUMN IF NOT EXISTS price_elc REAL DEFAULT 0")
    except Exception:
        pass  # Columns may already exist
    
    # Add total_revenue column to strategy_marketplace if missing
    try:
        cur.execute("ALTER TABLE strategy_marketplace ADD COLUMN IF NOT EXISTS total_revenue REAL DEFAULT 0")
    except Exception:
        pass
    
    # Add revenue_share column if missing
    try:
        cur.execute("ALTER TABLE strategy_marketplace ADD COLUMN IF NOT EXISTS revenue_share REAL DEFAULT 0.5")
    except Exception:
        pass
    
    # Create indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ups_user ON user_parser_subscriptions(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ups_active ON user_parser_subscriptions(user_id, is_active)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_usd_marketplace ON user_strategy_deployments(marketplace_listing_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_usd_purchase ON user_strategy_deployments(purchase_id)")


def downgrade(cur):
    """Rollback migration"""
    # Drop subscriptions table
    cur.execute("DROP TABLE IF EXISTS user_parser_subscriptions CASCADE")
    
    # Remove added columns from user_strategy_deployments
    try:
        cur.execute("ALTER TABLE user_strategy_deployments DROP COLUMN IF EXISTS marketplace_listing_id")
        cur.execute("ALTER TABLE user_strategy_deployments DROP COLUMN IF EXISTS custom_strategy_id")
        cur.execute("ALTER TABLE user_strategy_deployments DROP COLUMN IF EXISTS purchase_id")
        cur.execute("ALTER TABLE user_strategy_deployments DROP COLUMN IF EXISTS is_public")
        cur.execute("ALTER TABLE user_strategy_deployments DROP COLUMN IF EXISTS price_elc")
    except Exception:
        pass
