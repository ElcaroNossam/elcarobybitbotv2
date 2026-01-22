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
            order_id      TEXT NOT NULL,
            symbol        TEXT NOT NULL,
            side          TEXT NOT NULL,
            qty           REAL NOT NULL,
            price         REAL NOT NULL,
            signal_id     INTEGER,
            created_ts    BIGINT NOT NULL,
            time_in_force TEXT NOT NULL DEFAULT 'GTC',
            strategy      TEXT,
            account_type  TEXT DEFAULT 'demo',
            exchange      TEXT DEFAULT 'bybit',
            status        TEXT DEFAULT 'pending',
            expires_at    TIMESTAMP,
            
            PRIMARY KEY (user_id, order_id)
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pending_orders_user ON pending_limit_orders(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pending_orders_status ON pending_limit_orders(status)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pending_user_created ON pending_limit_orders(user_id, created_ts DESC)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS pending_limit_orders CASCADE")
