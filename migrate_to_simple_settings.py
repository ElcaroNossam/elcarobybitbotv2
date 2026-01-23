#!/usr/bin/env python3
"""
Migration script: Create new simplified DB and sync user API keys

Run on server:
    cd /home/ubuntu/project/elcarobybitbotv2
    source venv/bin/activate
    python migrate_to_simple_settings.py

This will:
1. Backup current user_strategy_settings table (rename to _old)
2. Create new simplified table with PRIMARY KEY (user_id, strategy, side)
3. Keep all users with their API keys intact
4. Strategy settings will use ENV defaults until user customizes
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# Load env
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://elcaro:elcaro_prod_2026@127.0.0.1:5432/elcaro")


def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def migrate():
    print("=" * 60)
    print("MIGRATION: Simplified Strategy Settings")
    print("=" * 60)
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Step 1: Check if old table exists and backup
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'user_strategy_settings'
            )
        """)
        table_exists = cur.fetchone()['exists']
        
        if table_exists:
            print("\n[1/5] Backing up old user_strategy_settings...")
            
            # Check if backup already exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'user_strategy_settings_old_backup'
                )
            """)
            backup_exists = cur.fetchone()['exists']
            
            if backup_exists:
                print("  - Backup already exists, dropping it...")
                cur.execute("DROP TABLE user_strategy_settings_old_backup")
            
            cur.execute("ALTER TABLE user_strategy_settings RENAME TO user_strategy_settings_old_backup")
            print("  ✅ Renamed to user_strategy_settings_old_backup")
        else:
            print("\n[1/5] No old table found, skipping backup")
        
        # Step 2: Create new simplified table
        print("\n[2/5] Creating new simplified table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_strategy_settings (
                user_id         BIGINT NOT NULL,
                strategy        TEXT NOT NULL,
                side            TEXT NOT NULL,  -- 'long' or 'short'
                
                -- Strategy enabled
                enabled         BOOLEAN DEFAULT TRUE,
                
                -- Trading parameters
                percent         REAL NOT NULL,          -- Entry % (risk per trade)
                sl_percent      REAL NOT NULL,          -- Stop-Loss %
                tp_percent      REAL NOT NULL,          -- Take-Profit %
                leverage        INTEGER NOT NULL,       -- Leverage
                
                -- ATR Trailing parameters
                use_atr         BOOLEAN DEFAULT TRUE,   -- ATR Trailing enabled
                atr_trigger_pct REAL NOT NULL,          -- Trigger % (profit to activate)
                atr_step_pct    REAL NOT NULL,          -- Step % (SL distance from price)
                
                -- Order type
                order_type      TEXT DEFAULT 'market',  -- 'market' or 'limit'
                
                -- Timestamps
                created_at      TIMESTAMP DEFAULT NOW(),
                updated_at      TIMESTAMP DEFAULT NOW(),
                
                PRIMARY KEY(user_id, strategy, side)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_uss_user ON user_strategy_settings(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_uss_strategy ON user_strategy_settings(strategy)")
        print("  ✅ New table created with PRIMARY KEY (user_id, strategy, side)")
        
        # Step 3: Verify users table is intact
        print("\n[3/5] Verifying users table...")
        cur.execute("SELECT COUNT(*) as cnt FROM users WHERE is_allowed = TRUE")
        active_users = cur.fetchone()['cnt']
        print(f"  ✅ {active_users} active users found")
        
        # Step 4: Check API keys
        print("\n[4/5] Checking API keys...")
        cur.execute("""
            SELECT user_id, 
                   CASE WHEN demo_api_key IS NOT NULL THEN 1 ELSE 0 END as has_demo,
                   CASE WHEN real_api_key IS NOT NULL THEN 1 ELSE 0 END as has_real,
                   CASE WHEN hl_mainnet_private_key IS NOT NULL THEN 1 ELSE 0 END as has_hl
            FROM users 
            WHERE is_allowed = TRUE
        """)
        users_with_keys = cur.fetchall()
        
        demo_count = sum(1 for u in users_with_keys if u['has_demo'])
        real_count = sum(1 for u in users_with_keys if u['has_real'])
        hl_count = sum(1 for u in users_with_keys if u['has_hl'])
        
        print(f"  ✅ Demo API keys: {demo_count}")
        print(f"  ✅ Real API keys: {real_count}")
        print(f"  ✅ HyperLiquid keys: {hl_count}")
        
        # Step 5: Commit
        print("\n[5/5] Committing changes...")
        conn.commit()
        print("  ✅ Migration complete!")
        
        print("\n" + "=" * 60)
        print("SUMMARY:")
        print("=" * 60)
        print(f"  - Old table backed up to: user_strategy_settings_old_backup")
        print(f"  - New table created: user_strategy_settings")
        print(f"  - Active users: {active_users}")
        print(f"  - All API keys preserved")
        print(f"  - Strategy settings now use ENV defaults")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
