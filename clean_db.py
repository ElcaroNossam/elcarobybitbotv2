import sqlite3
import sys

db_path = sys.argv[1] if len(sys.argv) > 1 else "elcaro.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("=== Tables in DB ===")
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t[0]}")
    count = cursor.fetchone()[0]
    print(f"{t[0]}: {count} rows")

print("\n=== Cleaning old data (keeping API keys) ===")

# Tables to clear completely
tables_to_clear = [
    'trade_logs',
    'signals', 
    'active_positions',
    'pending_limit_orders',
    'dca_history',
    'price_cache',
    'signal_history',
]

for table in tables_to_clear:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        before = cursor.fetchone()[0]
        cursor.execute(f"DELETE FROM {table}")
        print(f"Cleared {table}: {before} rows deleted")
    except Exception as e:
        print(f"Table {table} not found or error: {e}")

conn.commit()

print("\n=== After cleaning ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t[0]}")
    count = cursor.fetchone()[0]
    print(f"{t[0]}: {count} rows")

# Show users are preserved
print("\n=== Users preserved ===")
cursor.execute("SELECT user_id, demo_api_key IS NOT NULL as has_demo, real_api_key IS NOT NULL as has_real FROM users LIMIT 10")
for row in cursor.fetchall():
    print(f"User {row[0]}: demo_key={bool(row[1])}, real_key={bool(row[2])}")

conn.close()
print("\nDone! Restart bot to sync fresh positions from exchange.")
