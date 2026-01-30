"""
Migration 021: Login 2FA Requests Table
=======================================
Table to store 2FA login requests for iOS/Android/Web app authentication.

Used as fallback when Redis is unavailable. Primary storage is Redis with 5 min TTL.

Flow:
1. User enters @username in app
2. Server creates request (Redis primary, DB fallback)
3. Bot sends confirmation message to user's Telegram
4. User clicks Confirm/Reject
5. Bot updates status via API
6. App polls /check-2fa and gets JWT token if approved
"""


def upgrade(cur):
    """Create login_2fa_requests table."""
    cur.execute("""
        CREATE TABLE IF NOT EXISTS login_2fa_requests (
            id              SERIAL PRIMARY KEY,
            request_id      TEXT NOT NULL UNIQUE,
            telegram_id     BIGINT NOT NULL,
            username        TEXT,
            status          TEXT NOT NULL DEFAULT 'pending',  -- pending, approved, rejected
            created_at      TIMESTAMP DEFAULT NOW(),
            expires_at      TIMESTAMP NOT NULL,
            
            CONSTRAINT valid_status CHECK (status IN ('pending', 'approved', 'rejected'))
        )
    """)
    
    # Index for fast lookup by request_id
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_2fa_requests_request_id 
        ON login_2fa_requests(request_id)
    """)
    
    # Index for cleanup of expired requests
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_2fa_requests_expires_at 
        ON login_2fa_requests(expires_at)
    """)
    
    # Auto-cleanup of expired requests (optional trigger)
    # Note: Can also be done via cron job
    cur.execute("""
        CREATE OR REPLACE FUNCTION cleanup_expired_2fa_requests()
        RETURNS TRIGGER AS $$
        BEGIN
            DELETE FROM login_2fa_requests WHERE expires_at < NOW() - INTERVAL '1 hour';
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)
    
    # Trigger to cleanup on every insert (simple approach)
    cur.execute("""
        DROP TRIGGER IF EXISTS trg_cleanup_2fa ON login_2fa_requests
    """)
    
    cur.execute("""
        CREATE TRIGGER trg_cleanup_2fa
        AFTER INSERT ON login_2fa_requests
        FOR EACH STATEMENT
        EXECUTE FUNCTION cleanup_expired_2fa_requests()
    """)


def downgrade(cur):
    """Drop login_2fa_requests table and related objects."""
    cur.execute("DROP TRIGGER IF EXISTS trg_cleanup_2fa ON login_2fa_requests")
    cur.execute("DROP FUNCTION IF EXISTS cleanup_expired_2fa_requests()")
    cur.execute("DROP TABLE IF EXISTS login_2fa_requests CASCADE")
