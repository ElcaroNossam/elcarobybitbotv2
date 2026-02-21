"""
Migration: Marketplace Integration for User Strategy Deployments
Version: 026
Created: 2026-02-21

Adds marketplace columns to user_strategy_deployments for:
- Listing personal strategies on marketplace
- Tracking purchased strategies
"""


def upgrade(cur):
    """Apply migration"""
    
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
    cur.execute("CREATE INDEX IF NOT EXISTS idx_usd_marketplace ON user_strategy_deployments(marketplace_listing_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_usd_purchase ON user_strategy_deployments(purchase_id)")


def downgrade(cur):
    """Rollback migration"""
    # Remove added columns from user_strategy_deployments
    try:
        cur.execute("ALTER TABLE user_strategy_deployments DROP COLUMN IF EXISTS marketplace_listing_id")
        cur.execute("ALTER TABLE user_strategy_deployments DROP COLUMN IF EXISTS custom_strategy_id")
        cur.execute("ALTER TABLE user_strategy_deployments DROP COLUMN IF EXISTS purchase_id")
        cur.execute("ALTER TABLE user_strategy_deployments DROP COLUMN IF EXISTS is_public")
        cur.execute("ALTER TABLE user_strategy_deployments DROP COLUMN IF EXISTS price_elc")
    except Exception:
        pass
