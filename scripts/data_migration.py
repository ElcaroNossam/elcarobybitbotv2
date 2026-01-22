"""
Data Migration Script - Export/Import User Data
================================================

Usage:
    python scripts/data_migration.py export   # Export to JSON
    python scripts/data_migration.py import   # Import from JSON
"""
import os
import sys
import json
import logging
from datetime import datetime, date
from decimal import Decimal

import psycopg2
import psycopg2.extras

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://elcaro:elcaro_prod_2026@127.0.0.1:5432/elcaro"
)

BACKUP_FILE = "user_data_backup.json"

# Tables to export (in order of dependency)
TABLES_TO_EXPORT = [
    "users",
    "user_strategy_settings",
    "payment_history",
    "email_users",
]

# Critical user fields that MUST be preserved
CRITICAL_USER_FIELDS = [
    "user_id",
    "demo_api_key", "demo_api_secret",
    "real_api_key", "real_api_secret",
    "trading_mode",
    "hl_private_key", "hl_wallet_address",
    "hl_testnet_private_key", "hl_testnet_wallet_address",
    "hl_mainnet_private_key", "hl_mainnet_wallet_address",
    "current_license", "license_expires", "license_type",
    "is_allowed", "is_banned",
    "elc_balance", "elc_staked", "elc_locked",
    "referral_code", "referred_by",
    "percent", "leverage", "tp_percent", "sl_percent",
    "trade_scryptomera", "trade_scalper", "trade_elcaro", "trade_fibonacci",
    "strategy_settings",
    "username", "first_name", "last_name", "email",
]


class CustomEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime, Decimal, etc."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, bytes):
            return obj.decode('utf-8', errors='ignore')
        return super().default(obj)


def get_connection():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL)


def table_exists(cur, table_name: str) -> bool:
    """Check if table exists"""
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = %s
        )
    """, (table_name,))
    result = cur.fetchone()
    if result is None:
        return False
    # Handle both dict (RealDictCursor) and tuple
    if isinstance(result, dict):
        return result.get('exists', False)
    return result[0] if result else False


def export_data():
    """Export critical user data to JSON file"""
    logger.info("📦 Starting data export...")
    
    data = {
        "exported_at": datetime.now().isoformat(),
        "tables": {}
    }
    
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            for table in TABLES_TO_EXPORT:
                if not table_exists(cur, table):
                    logger.warning(f"⚠️ Table {table} does not exist, skipping")
                    continue
                
                cur.execute(f"SELECT * FROM {table}")
                rows = cur.fetchall()
                
                # Convert to list of dicts
                data["tables"][table] = [dict(row) for row in rows]
                logger.info(f"  ✅ Exported {len(rows)} rows from {table}")
    
    # Save to file
    with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, cls=CustomEncoder, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Data exported to {BACKUP_FILE}")
    logger.info(f"   File size: {os.path.getsize(BACKUP_FILE) / 1024:.1f} KB")
    
    return BACKUP_FILE


def import_data(backup_file: str = BACKUP_FILE):
    """Import user data from JSON file"""
    logger.info(f"📥 Importing data from {backup_file}...")
    
    if not os.path.exists(backup_file):
        logger.error(f"❌ Backup file not found: {backup_file}")
        return False
    
    with open(backup_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info(f"   Backup from: {data.get('exported_at', 'unknown')}")
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Import users first
            if "users" in data["tables"]:
                users = data["tables"]["users"]
                imported = 0
                
                for user in users:
                    user_id = user.get("user_id")
                    if not user_id:
                        continue
                    
                    # Check if user exists
                    cur.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
                    exists = cur.fetchone()
                    
                    if exists:
                        # Update existing user - preserve critical fields
                        update_fields = []
                        values = []
                        
                        for field in CRITICAL_USER_FIELDS:
                            if field in user and field != "user_id":
                                value = user[field]
                                if value is not None:
                                    update_fields.append(f"{field} = %s")
                                    values.append(value)
                        
                        if update_fields:
                            values.append(user_id)
                            cur.execute(
                                f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = %s",
                                values
                            )
                    else:
                        # Insert new user
                        fields = [k for k in user.keys() if user[k] is not None]
                        placeholders = ", ".join(["%s"] * len(fields))
                        values = [user[k] for k in fields]
                        
                        try:
                            cur.execute(
                                f"INSERT INTO users ({', '.join(fields)}) VALUES ({placeholders})",
                                values
                            )
                        except Exception as e:
                            logger.warning(f"⚠️ Could not insert user {user_id}: {e}")
                            continue
                    
                    imported += 1
                
                logger.info(f"  ✅ Imported/updated {imported} users")
            
            # Import user_strategy_settings
            if "user_strategy_settings" in data["tables"]:
                settings = data["tables"]["user_strategy_settings"]
                for s in settings:
                    try:
                        cur.execute("""
                            INSERT INTO user_strategy_settings (user_id, strategy, settings)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (user_id, strategy) DO UPDATE 
                            SET settings = EXCLUDED.settings
                        """, (s["user_id"], s["strategy"], json.dumps(s.get("settings", {}))))
                    except Exception as e:
                        logger.warning(f"⚠️ Could not import strategy setting: {e}")
                
                logger.info(f"  ✅ Imported {len(settings)} strategy settings")
            
            # Import payment_history
            if "payment_history" in data["tables"]:
                payments = data["tables"]["payment_history"]
                for p in payments:
                    try:
                        cur.execute("""
                            INSERT INTO payment_history 
                            (user_id, amount, currency, payment_type, status, tx_hash, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            p["user_id"], p.get("amount", 0), p.get("currency", "USDT"),
                            p.get("payment_type", "unknown"), p.get("status", "completed"),
                            p.get("tx_hash"), p.get("created_at")
                        ))
                    except Exception as e:
                        logger.warning(f"⚠️ Could not import payment: {e}")
                
                logger.info(f"  ✅ Imported {len(payments)} payment records")
            
            # Import email_users
            if "email_users" in data["tables"]:
                email_users = data["tables"]["email_users"]
                for eu in email_users:
                    try:
                        cur.execute("""
                            INSERT INTO email_users 
                            (user_id, email, password_hash, password_salt, name, is_verified)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (user_id) DO UPDATE 
                            SET email = EXCLUDED.email
                        """, (
                            eu["user_id"], eu["email"], eu["password_hash"],
                            eu["password_salt"], eu.get("name"), eu.get("is_verified", False)
                        ))
                    except Exception as e:
                        logger.warning(f"⚠️ Could not import email user: {e}")
                
                logger.info(f"  ✅ Imported {len(email_users)} email users")
            
            conn.commit()
    
    logger.info("✅ Data import complete!")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/data_migration.py [export|import]")
        return
    
    command = sys.argv[1]
    
    if command == "export":
        export_data()
    elif command == "import":
        backup_file = sys.argv[2] if len(sys.argv) > 2 else BACKUP_FILE
        import_data(backup_file)
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
