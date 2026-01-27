#!/usr/bin/env python3
"""
Database Audit Script - проверка соответствия данных реальности
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['DATABASE_URL'] = 'postgresql://elcaro:elcaro_prod_2026@127.0.0.1:5432/elcaro'

from core.db_postgres import execute, execute_one
from datetime import datetime, timedelta

def main():
    print("=" * 70)
    print("📊 DATABASE AUDIT REPORT")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 1. Общая статистика
    print("\n📈 GENERAL STATISTICS")
    print("-" * 40)
    
    users = execute("SELECT COUNT(*) as cnt FROM users WHERE is_allowed = 1")
    print(f"👥 Active users: {users[0]['cnt']}")
    
    positions = execute("SELECT COUNT(*) as cnt FROM active_positions")
    print(f"📈 Active positions in DB: {positions[0]['cnt']}")
    
    trades = execute("SELECT COUNT(*) as cnt FROM trade_logs")
    print(f"📜 Trade logs total: {trades[0]['cnt']}")
    
    recent = execute("""
        SELECT COUNT(*) as cnt FROM trade_logs 
        WHERE ts > NOW() - INTERVAL '7 days'
    """)
    print(f"📊 Trades last 7 days: {recent[0]['cnt']}")

    # 2. Позиции по юзерам
    print("\n" + "=" * 70)
    print("📈 ACTIVE POSITIONS BY USER")
    print("=" * 70)
    
    positions_by_user = execute("""
        SELECT 
            ap.user_id,
            u.username,
            u.first_name,
            ap.exchange,
            ap.account_type,
            COUNT(*) as pos_count,
            STRING_AGG(ap.symbol, ', ') as symbols
        FROM active_positions ap
        LEFT JOIN users u ON ap.user_id = u.user_id
        GROUP BY ap.user_id, u.username, u.first_name, ap.exchange, ap.account_type
        ORDER BY pos_count DESC
    """)
    
    if not positions_by_user:
        print("✅ No active positions in DB")
    else:
        for row in positions_by_user:
            name = row['username'] or row['first_name'] or str(row['user_id'])
            symbols = row['symbols'] or ""
            print(f"\n👤 {name} ({row['user_id']})")
            print(f"   Exchange: {row['exchange']} | Account: {row['account_type']}")
            print(f"   Positions: {row['pos_count']}")
            if len(symbols) > 80:
                print(f"   Symbols: {symbols[:80]}...")
            else:
                print(f"   Symbols: {symbols}")

    # 3. Детали активных позиций
    print("\n" + "=" * 70)
    print("📋 ACTIVE POSITIONS DETAILS")
    print("=" * 70)
    
    all_positions = execute("""
        SELECT 
            ap.*,
            u.username,
            u.first_name
        FROM active_positions ap
        LEFT JOIN users u ON ap.user_id = u.user_id
        ORDER BY ap.open_ts DESC
        LIMIT 20
    """)
    
    for pos in all_positions:
        name = pos.get('username') or pos.get('first_name') or str(pos['user_id'])
        side = pos.get('side', '?')
        symbol = pos.get('symbol', '?')
        entry = pos.get('entry_price', 0)
        size = pos.get('size', 0)
        leverage = pos.get('leverage', 0)
        strategy = pos.get('strategy', 'unknown')
        exchange = pos.get('exchange', 'bybit')
        acc_type = pos.get('account_type', 'demo')
        open_ts = pos.get('open_ts')
        
        print(f"\n📊 {symbol} | {side} | {name}")
        print(f"   Entry: ${entry:.6f} | Size: {size:.4f} | Lev: {leverage}x")
        print(f"   Strategy: {strategy} | {exchange}/{acc_type}")
        if open_ts:
            print(f"   Opened: {open_ts}")

    # 4. Последние сделки
    print("\n" + "=" * 70)
    print("📜 RECENT TRADES (last 20)")
    print("=" * 70)
    
    recent_trades = execute("""
        SELECT 
            tl.*,
            u.username,
            u.first_name
        FROM trade_logs tl
        LEFT JOIN users u ON tl.user_id = u.user_id
        ORDER BY tl.ts DESC
        LIMIT 20
    """)
    
    for trade in recent_trades:
        name = trade.get('username') or trade.get('first_name') or str(trade['user_id'])
        symbol = trade.get('symbol', '?')
        side = trade.get('side', '?')
        pnl = trade.get('pnl', 0) or 0
        pnl_pct = trade.get('pnl_pct', 0) or 0
        exit_reason = trade.get('exit_reason', '?')
        strategy = trade.get('strategy', 'unknown')
        ts = trade.get('ts')
        account_type = trade.get('account_type', 'demo')
        
        pnl_emoji = "🟢" if pnl >= 0 else "🔴"
        print(f"\n{pnl_emoji} {symbol} | {side} | {name}")
        print(f"   PnL: ${pnl:.2f} ({pnl_pct:.2f}%) | Exit: {exit_reason}")
        print(f"   Strategy: {strategy} | {account_type}")
        if ts:
            print(f"   Time: {ts}")

    # 5. Статистика по стратегиям
    print("\n" + "=" * 70)
    print("📊 TRADE STATS BY STRATEGY (last 30 days)")
    print("=" * 70)
    
    strategy_stats = execute("""
        SELECT 
            strategy,
            account_type,
            COUNT(*) as trades,
            SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses,
            ROUND(SUM(pnl)::numeric, 2) as total_pnl,
            ROUND(AVG(pnl)::numeric, 2) as avg_pnl,
            ROUND(AVG(pnl_pct)::numeric, 2) as avg_pnl_pct
        FROM trade_logs
        WHERE ts > NOW() - INTERVAL '30 days'
        GROUP BY strategy, account_type
        ORDER BY total_pnl DESC
    """)
    
    for stat in strategy_stats:
        strategy = stat['strategy'] or 'unknown'
        account = stat['account_type'] or 'demo'
        trades = stat['trades']
        wins = stat['wins'] or 0
        losses = stat['losses'] or 0
        total_pnl = float(stat['total_pnl'] or 0)
        avg_pnl = float(stat['avg_pnl'] or 0)
        avg_pnl_pct = float(stat['avg_pnl_pct'] or 0)
        winrate = (wins / trades * 100) if trades > 0 else 0
        
        pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
        print(f"\n{pnl_emoji} {strategy} ({account})")
        print(f"   Trades: {trades} | Wins: {wins} | Losses: {losses} | WR: {winrate:.1f}%")
        print(f"   Total PnL: ${total_pnl:.2f} | Avg: ${avg_pnl:.2f} ({avg_pnl_pct:.2f}%)")

    # 6. PnL по юзерам
    print("\n" + "=" * 70)
    print("💰 PNL BY USER (last 30 days)")
    print("=" * 70)
    
    user_pnl = execute("""
        SELECT 
            tl.user_id,
            u.username,
            u.first_name,
            tl.account_type,
            COUNT(*) as trades,
            SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
            ROUND(SUM(pnl)::numeric, 2) as total_pnl,
            ROUND(AVG(pnl_pct)::numeric, 2) as avg_pnl_pct
        FROM trade_logs tl
        LEFT JOIN users u ON tl.user_id = u.user_id
        WHERE tl.ts > NOW() - INTERVAL '30 days'
        GROUP BY tl.user_id, u.username, u.first_name, tl.account_type
        ORDER BY total_pnl DESC
    """)
    
    for row in user_pnl:
        name = row['username'] or row['first_name'] or str(row['user_id'])
        account = row['account_type'] or 'demo'
        trades = row['trades']
        wins = row['wins'] or 0
        total_pnl = float(row['total_pnl'] or 0)
        avg_pnl_pct = float(row['avg_pnl_pct'] or 0)
        winrate = (wins / trades * 100) if trades > 0 else 0
        
        pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
        print(f"\n{pnl_emoji} {name} ({account})")
        print(f"   Trades: {trades} | WR: {winrate:.1f}%")
        print(f"   Total PnL: ${total_pnl:.2f} | Avg %: {avg_pnl_pct:.2f}%")

    # 7. Проверка дубликатов
    print("\n" + "=" * 70)
    print("🔍 DATA INTEGRITY CHECK")
    print("=" * 70)
    
    # Дубликаты в trade_logs
    duplicates = execute("""
        SELECT 
            user_id, symbol, side, entry_price, pnl,
            COUNT(*) as cnt
        FROM trade_logs
        WHERE ts > NOW() - INTERVAL '7 days'
        GROUP BY user_id, symbol, side, entry_price, pnl
        HAVING COUNT(*) > 1
        LIMIT 10
    """)
    
    if duplicates:
        print(f"\n⚠️ Found {len(duplicates)} potential duplicates in trade_logs:")
        for dup in duplicates:
            print(f"   {dup['symbol']} | {dup['side']} | Entry: {dup['entry_price']} | Count: {dup['cnt']}")
    else:
        print("\n✅ No duplicates found in recent trade_logs")
    
    # Orphaned positions (старше 7 дней без активности)
    old_positions = execute("""
        SELECT COUNT(*) as cnt 
        FROM active_positions 
        WHERE open_ts < NOW() - INTERVAL '7 days'
    """)
    
    if old_positions[0]['cnt'] > 0:
        print(f"\n⚠️ {old_positions[0]['cnt']} positions older than 7 days - may need cleanup")
    else:
        print("✅ No stale positions found")

    # Trades с нулевым PnL
    zero_pnl = execute("""
        SELECT COUNT(*) as cnt 
        FROM trade_logs 
        WHERE pnl = 0 AND ts > NOW() - INTERVAL '7 days'
    """)
    print(f"ℹ️ Trades with zero PnL (last 7 days): {zero_pnl[0]['cnt']}")

    print("\n" + "=" * 70)
    print("✅ AUDIT COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
