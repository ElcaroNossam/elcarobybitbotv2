"""
Migration: Market Snapshots and News Tables
Version: 015
Created: 2026-01-23

Creates market_snapshots and news tables for market data and news.
"""


def upgrade(cur):
    """Apply migration"""
    
    # Market snapshots table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS market_snapshots (
            id            SERIAL PRIMARY KEY,
            ts            TIMESTAMP DEFAULT NOW(),
            btc_dom       REAL,
            btc_price     REAL,
            btc_change    REAL,
            alt_signal    TEXT,
            symbol        TEXT,
            price         REAL,
            volume_24h    REAL,
            price_change_24h REAL,
            open_interest REAL,
            funding_rate  REAL,
            exchange      TEXT DEFAULT 'bybit'
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_market_snapshots_ts ON market_snapshots(ts DESC)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_market_snapshots_symbol ON market_snapshots(symbol, ts DESC)")
    
    # News table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id          SERIAL PRIMARY KEY,
            link        TEXT UNIQUE,
            title       TEXT,
            description TEXT,
            image_url   TEXT,
            signal      TEXT,
            sentiment   TEXT,
            created_at  TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_news_created ON news(created_at DESC)")


def downgrade(cur):
    """Rollback migration"""
    cur.execute("DROP TABLE IF EXISTS market_snapshots CASCADE")
    cur.execute("DROP TABLE IF EXISTS news CASCADE")
