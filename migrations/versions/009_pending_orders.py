"""
Migration: Pending Limit Orders Table
Version: 009
Created: 2026-01-22

Creates pending_limit_orders table for tracking limit orders.
"""


def upgrade(cur):
    """Apply migration"""
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pending_limit_orders (
            user_id       BIGINT NOT NULL,
            symbol        TEXT NOT NULL,
            account_type  TEXT NOT NULL DEFAULT 'demo',
            order_id      TEXT NOT NULL,
            
            side          TEXT NOT NULL,
            qty           REAL NOT NULL,
            price         REAL NOT NULL,
            order_type    TEXT DEFAULT 'limit',
            
            strategy      TEXT,
            signal_id     INTEGER,
            exchange      TEXT DEFAULT 'bybit',
            
            status        TEXT DEFAULT 'pending',
            created_at    TIMESTAMP DEFAULT NOW(),
            expires_at    TIMESTAMP,
            
            PRIMARY KEY (user_id, symbol, account_type, order_id)
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pending_orders_user ON pending_limit_orders(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pending_orders_status ON pending_limit_orders(status)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS pending_limit_orders CASCADE")
