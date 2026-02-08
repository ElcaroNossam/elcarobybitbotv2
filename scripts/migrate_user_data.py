#!/usr/bin/env python3
"""
Script to export all user data from current database before migration.
Run this BEFORE applying the unified schema migration.
"""
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

DATABASE_URL = "postgresql://elcaro:elcaro_prod_2026@127.0.0.1:5432/elcaro"


def export_users():
    """Export all user data to JSON"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Export users
    cur.execute("SELECT * FROM users")
    users = [dict(row) for row in cur.fetchall()]
    
    # Export strategy settings
    cur.execute("SELECT * FROM user_strategy_settings")
    strategy_settings = [dict(row) for row in cur.fetchall()]
    
    # Export active positions
    cur.execute("SELECT * FROM active_positions")
    positions = [dict(row) for row in cur.fetchall()]
    
    # Export trade logs (last 1000)
    cur.execute("SELECT * FROM trade_logs ORDER BY ts DESC LIMIT 1000")
    trade_logs = [dict(row) for row in cur.fetchall()]
    
    conn.close()
    
    # Convert datetime to string
    def convert_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj
    
    def process_row(row):
        return {k: convert_datetime(v) for k, v in row.items()}
    
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "users": [process_row(u) for u in users],
        "strategy_settings": [process_row(s) for s in strategy_settings],
        "active_positions": [process_row(p) for p in positions],
        "trade_logs_sample": [process_row(t) for t in trade_logs[:100]],
    }
    
    # Save to file
    with open("user_data_export_before_migration.json", "w") as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"Exported {len(users)} users")
    print(f"Exported {len(strategy_settings)} strategy settings")
    print(f"Exported {len(positions)} active positions")
    print(f"Exported {len(trade_logs)} trade logs")
    print(f"Saved to user_data_export_before_migration.json")
    
    return export_data


def import_users(data):
    """Import user data after migration"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Import users
    for user in data["users"]:
        # Map old field names to new
        values = {
            "user_id": user.get("user_id"),
            "username": user.get("username"),
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "email": user.get("email"),
            "lang": user.get("lang", "en"),
            "is_allowed": user.get("is_allowed", False),
            "is_banned": user.get("is_banned", False),
            "current_license": user.get("current_license", "none"),
            
            # Bybit credentials
            "bybit_enabled": user.get("bybit_enabled", True),
            "demo_api_key": user.get("demo_api_key"),
            "demo_api_secret": user.get("demo_api_secret"),
            "real_api_key": user.get("real_api_key"),
            "real_api_secret": user.get("real_api_secret"),
            
            # HyperLiquid credentials
            "hl_enabled": user.get("hl_enabled", False),
            "hl_testnet_private_key": user.get("hl_testnet_private_key"),
            "hl_testnet_wallet_address": user.get("hl_testnet_wallet_address"),
            "hl_mainnet_private_key": user.get("hl_mainnet_private_key"),
            "hl_mainnet_wallet_address": user.get("hl_mainnet_wallet_address"),
            
            # Exchange routing
            "exchange_type": user.get("exchange_type", "bybit"),
            "trading_mode": user.get("trading_mode", "demo"),
            "routing_policy": user.get("routing_policy"),
            "live_enabled": user.get("live_enabled", False),
            
            # Trading settings
            "percent": user.get("percent", 3.0),
            "tp_percent": user.get("tp_percent", 10.0),
            "sl_percent": user.get("sl_percent", 30.0),
            "leverage": user.get("leverage", 10),
            "use_atr": user.get("use_atr", True),
            "atr_trigger_pct": user.get("atr_trigger_pct", 3.0),
            
            # Coins groups
            "bybit_coins_group": user.get("bybit_coins_group") or user.get("coins", "ALL"),
            "hl_coins_group": user.get("hl_coins_group") or "ALL",
        }
        
        fields = [k for k, v in values.items() if v is not None]
        placeholders = ["%s"] * len(fields)
        vals = [values[k] for k in fields]
        
        sql = f"""
            INSERT INTO users ({", ".join(fields)})
            VALUES ({", ".join(placeholders)})
            ON CONFLICT (user_id) DO UPDATE SET {", ".join(f"{f} = EXCLUDED.{f}" for f in fields if f != "user_id")}
        """
        cur.execute(sql, vals)
        print(f"  Imported user {user.get('user_id')} ({user.get('username')})")
    
    # Import active positions
    for pos in data.get("active_positions", []):
        if not pos.get("user_id") or not pos.get("symbol"):
            continue
            
        cur.execute("""
            INSERT INTO active_positions (user_id, symbol, account_type, exchange, side, entry_price, size, leverage, strategy)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, symbol, account_type, exchange) DO NOTHING
        """, (
            pos.get("user_id"),
            pos.get("symbol"),
            pos.get("account_type", "demo"),
            pos.get("exchange", "bybit"),
            pos.get("side"),
            pos.get("entry_price"),
            pos.get("size"),
            pos.get("leverage"),
            pos.get("strategy"),
        ))
    
    conn.commit()
    conn.close()
    print(f"Import complete!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "import":
        with open("user_data_export_before_migration.json") as f:
            data = json.load(f)
        import_users(data)
    else:
        export_users()
