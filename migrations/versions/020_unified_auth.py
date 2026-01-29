"""
Migration 020: Unified Auth Schema
==================================
Adds email/password fields to main users table for unified authentication.
This allows users to login via Telegram OR Email with the same account.

Key changes:
- Add email, password_hash, password_salt to users table
- Add telegram_username for display purposes
- Add auth_provider to track how user registered

After migration, email_users table becomes legacy (data migrated to users).
"""

def upgrade(cur):
    """Apply migration - add unified auth fields to users table."""
    
    # Add email auth fields to main users table
    cur.execute("""
        ALTER TABLE users ADD COLUMN IF NOT EXISTS email TEXT UNIQUE;
    """)
    
    cur.execute("""
        ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash TEXT;
    """)
    
    cur.execute("""
        ALTER TABLE users ADD COLUMN IF NOT EXISTS password_salt TEXT;
    """)
    
    cur.execute("""
        ALTER TABLE users ADD COLUMN IF NOT EXISTS telegram_username TEXT;
    """)
    
    # auth_provider: 'telegram', 'email', 'both' (when linked)
    cur.execute("""
        ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider TEXT DEFAULT 'telegram';
    """)
    
    # email_verified flag
    cur.execute("""
        ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
    """)
    
    # last_login timestamp
    cur.execute("""
        ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;
    """)
    
    # Create index for email lookup
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email) WHERE email IS NOT NULL;
    """)
    
    # Create index for telegram_username lookup
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_telegram_username ON users(telegram_username) WHERE telegram_username IS NOT NULL;
    """)
    
    # Create telegram_user_mapping for linking email accounts to Telegram
    # This is needed when email-registered user (negative user_id) links their Telegram
    cur.execute("""
        CREATE TABLE IF NOT EXISTS telegram_user_mapping (
            telegram_id BIGINT PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES users(user_id),
            linked_at TIMESTAMP DEFAULT NOW()
        );
    """)
    
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_telegram_mapping_user ON telegram_user_mapping(user_id);
    """)
    
    # Migrate data from email_users to users (for existing email registrations)
    # This links email accounts with their generated user_id
    cur.execute("""
        UPDATE users u
        SET 
            email = eu.email,
            password_hash = eu.password_hash,
            password_salt = eu.password_salt,
            auth_provider = 'email',
            email_verified = eu.is_verified,
            last_login = eu.last_login
        FROM email_users eu
        WHERE u.user_id = eu.user_id
          AND u.email IS NULL;
    """)
    
    print("✅ Migration 020: Unified auth fields added to users table")


def downgrade(cur):
    """Rollback migration - remove unified auth fields."""
    cur.execute("DROP TABLE IF EXISTS telegram_user_mapping CASCADE;")
    cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS email;")
    cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS password_hash;")
    cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS password_salt;")
    cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS telegram_username;")
    cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS auth_provider;")
    cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS email_verified;")
    cur.execute("ALTER TABLE users DROP COLUMN IF EXISTS last_login;")
    cur.execute("DROP INDEX IF EXISTS idx_users_email;")
    cur.execute("DROP INDEX IF EXISTS idx_users_telegram_username;")
    cur.execute("DROP INDEX IF EXISTS idx_telegram_mapping_user;")
    
    print("✅ Migration 020: Rolled back unified auth fields")
