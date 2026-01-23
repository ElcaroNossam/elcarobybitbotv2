#!/usr/bin/env python3
"""
Database Optimization Script
Adds missing indexes and optimizes queries for performance

Run this after deploying to add all missing indexes.
Safe to run multiple times (uses IF NOT EXISTS).
"""
import sqlite3
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import DB_FILE, get_conn, release_conn

def measure_query_time(conn, query, params=None):
    """Measure query execution time"""
    start = time.time()
    if params:
        conn.execute(query, params).fetchall()
    else:
        conn.execute(query).fetchall()
    return time.time() - start

def analyze_table(conn, table_name):
    """Analyze table for query optimizer"""
    print(f"  Analyzing {table_name}...")
    conn.execute(f"ANALYZE {table_name}")

def create_indexes(conn):
    """Create all missing performance indexes"""
    indexes = [
        # Trade logs - most queries involve these columns
        ("idx_logs_user_symbol", "trade_logs", "user_id, symbol"),
        ("idx_logs_entry_ts", "trade_logs", "entry_ts DESC"),
        ("idx_logs_exit_ts", "trade_logs", "exit_ts DESC"),
        ("idx_logs_pnl", "trade_logs", "pnl DESC"),
        
        # Active positions - critical for monitoring
        ("idx_active_symbol", "active_positions", "symbol"),
        ("idx_active_account_type", "active_positions", "user_id, account_type"),
        ("idx_active_strategy", "active_positions", "user_id, strategy"),
        ("idx_active_side", "active_positions", "side, symbol"),
        
        # Pending limit orders - order matching
        ("idx_pending_symbol", "pending_limit_orders", "symbol"),
        ("idx_pending_strategy", "pending_limit_orders", "user_id, strategy"),
        ("idx_pending_account_type", "pending_limit_orders", "user_id, account_type"),
        ("idx_pending_price", "pending_limit_orders", "symbol, price"),
        
        # User licenses - admin queries and access checks
        ("idx_licenses_expires", "user_licenses", "end_date DESC"),
        ("idx_licenses_type", "user_licenses", "user_id, license_type"),
        ("idx_licenses_active_user", "user_licenses", "is_active, user_id"),
        
        # Promo codes - redemption checks
        ("idx_promo_active", "promo_codes", "is_active, valid_until"),
        ("idx_promo_type", "promo_codes", "license_type, is_active"),
        
        # Signals - historical lookups
        ("idx_signals_symbol_side", "signals", "symbol, side, ts DESC"),
        ("idx_signals_price", "signals", "symbol, price"),
        
        # Payment history - user billing
        ("idx_payments_created", "payment_history", "created_at DESC"),
        ("idx_payments_type", "payment_history", "payment_type, status"),
        
        # Promo usage - tracking
        ("idx_promo_usage_user", "promo_usage", "user_id, used_at DESC"),
        
        # Pyramids - position tracking
        ("idx_pyramids_symbol", "pyramids", "symbol"),
        
        # News - signal correlation
        ("idx_news_signal", "news", "signal, ts DESC"),
        ("idx_news_sentiment", "news", "sentiment, ts DESC"),
        
        # Market snapshots - technical analysis
        ("idx_ms_btc_dom", "market_snapshots", "btc_dom, ts DESC"),
        ("idx_ms_alt_signal", "market_snapshots", "alt_signal, ts DESC"),
        
        # Users - API key lookups (partial indexes for performance)
        ("idx_users_demo_keys", "users", "demo_api_key WHERE demo_api_key IS NOT NULL"),
        ("idx_users_real_keys", "users", "real_api_key WHERE real_api_key IS NOT NULL"),
        ("idx_users_mode", "users", "trading_mode, is_banned"),
    ]
    
    created = 0
    skipped = 0
    
    for idx_def in indexes:
        if len(idx_def) == 3:
            idx_name, table, columns = idx_def
            where_clause = ""
        else:
            idx_name, table, columns_and_where = idx_def
            if " WHERE " in columns_and_where:
                columns, where_clause = columns_and_where.split(" WHERE ")
            else:
                columns = columns_and_where
                where_clause = ""
        
        try:
            query = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({columns})"
            if where_clause:
                query += f" WHERE {where_clause}"
            
            print(f"  Creating index: {idx_name}...")
            conn.execute(query)
            created += 1
        except sqlite3.OperationalError as e:
            if "already exists" in str(e).lower():
                print(f"  ✓ Index {idx_name} already exists")
                skipped += 1
            else:
                print(f"  ✗ Error creating {idx_name}: {e}")
    
    return created, skipped

def optimize_pragma_settings(conn):
    """Apply optimal PRAGMA settings"""
    print("\n2. Optimizing PRAGMA settings...")
    
    settings = {
        "cache_size": -128000,      # 128MB cache (increased from 64MB)
        "mmap_size": 536870912,     # 512MB mmap (increased from 256MB)
        "temp_store": "MEMORY",
        "synchronous": "NORMAL",
        "journal_mode": "WAL",
        "busy_timeout": 10000,      # 10s timeout
        "page_size": 8192,          # Larger pages for better performance
        "auto_vacuum": "INCREMENTAL",
    }
    
    for pragma, value in settings.items():
        if isinstance(value, str):
            conn.execute(f"PRAGMA {pragma}={value}")
        else:
            conn.execute(f"PRAGMA {pragma}={value}")
        
        result = conn.execute(f"PRAGMA {pragma}").fetchone()
        print(f"  {pragma}: {result[0]}")

def analyze_all_tables(conn):
    """Run ANALYZE on all tables for query optimizer"""
    print("\n3. Analyzing tables for query optimizer...")
    
    tables = [
        "users", "signals", "active_positions", "pending_limit_orders",
        "trade_logs", "user_licenses", "payment_history", "promo_codes",
        "promo_usage", "pyramids", "news", "market_snapshots"
    ]
    
    for table in tables:
        analyze_table(conn, table)
    
    print("  Running global ANALYZE...")
    conn.execute("ANALYZE")

def vacuum_database(conn):
    """VACUUM to reclaim space and optimize layout"""
    print("\n4. Running VACUUM (may take a while)...")
    
    # Get database size before
    size_before = DB_FILE.stat().st_size / (1024 * 1024)
    print(f"  Database size before: {size_before:.2f} MB")
    
    conn.execute("VACUUM")
    
    # Get size after
    size_after = DB_FILE.stat().st_size / (1024 * 1024)
    print(f"  Database size after: {size_after:.2f} MB")
    print(f"  Space reclaimed: {size_before - size_after:.2f} MB")

def benchmark_queries(conn):
    """Benchmark critical queries before/after optimization"""
    print("\n5. Benchmarking critical queries...")
    
    queries = [
        ("User config lookup", 
         "SELECT * FROM users WHERE user_id = ?", (511692487,)),
        
        ("Active positions by user", 
         "SELECT * FROM active_positions WHERE user_id = ?", (511692487,)),
        
        ("Trade logs last 24h", 
         "SELECT * FROM trade_logs WHERE user_id = ? AND ts > NOW() - INTERVAL '1 day'", 
         (511692487,)),
        
        ("License check", 
         "SELECT * FROM user_licenses WHERE user_id = ? AND is_active = TRUE AND end_date > ?", 
         (511692487, int(time.time()))),
        
        ("Pending orders by symbol", 
         "SELECT * FROM pending_limit_orders WHERE user_id = ? AND symbol = ?", 
         (511692487, "BTCUSDT")),
        
        ("Recent signals", 
         "SELECT * FROM signals WHERE symbol = ? ORDER BY ts DESC LIMIT 10", 
         ("BTCUSDT",)),
    ]
    
    for query_name, query, params in queries:
        elapsed = measure_query_time(conn, query, params)
        print(f"  {query_name}: {elapsed*1000:.2f}ms")

def main():
    print("=" * 70)
    print("DATABASE OPTIMIZATION SCRIPT")
    print("=" * 70)
    
    if not DB_FILE.exists():
        print(f"\n✗ Database not found: {DB_FILE}")
        print("  Run the bot first to create the database.")
        sys.exit(1)
    
    print(f"\nDatabase: {DB_FILE}")
    
    conn = get_conn()
    
    try:
        # 1. Create indexes
        print("\n1. Creating performance indexes...")
        created, skipped = create_indexes(conn)
        print(f"\n  Results:")
        print(f"    Created: {created}")
        print(f"    Already existed: {skipped}")
        
        # 2. Optimize PRAGMA settings
        optimize_pragma_settings(conn)
        
        # 3. Analyze tables
        analyze_all_tables(conn)
        
        # 4. VACUUM (optional - can be slow on large DBs)
        vacuum_input = input("\nRun VACUUM? (y/N): ").lower().strip()
        if vacuum_input == 'y':
            vacuum_database(conn)
        else:
            print("  Skipping VACUUM")
        
        # 5. Benchmark
        benchmark_queries(conn)
        
        conn.commit()
        
        print("\n" + "=" * 70)
        print("✅ DATABASE OPTIMIZATION COMPLETE")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Restart bot/webapp to use new indexes")
        print("  2. Monitor query performance with run_terminal_full_tests.py")
        print("  3. Check logs for any slow queries (>100ms)")
        
    except Exception as e:
        print(f"\n✗ Error during optimization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        release_conn(conn)

if __name__ == "__main__":
    main()
