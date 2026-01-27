#!/usr/bin/env python3
"""
Position Cleanup Script - удаление stale позиций из БД которых нет на бирже
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_postgres import execute, get_conn
from datetime import datetime
import asyncio
import aiohttp
import hmac
import hashlib
import time

async def get_bybit_positions(api_key: str, api_secret: str, is_demo: bool = True):
    """Fetch positions from Bybit API"""
    base_url = "https://api-demo.bybit.com" if is_demo else "https://api.bybit.com"
    endpoint = "/v5/position/list"
    
    timestamp = str(int(time.time() * 1000))
    params = {
        "category": "linear",
        "settleCoin": "USDT"
    }
    
    param_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    sign_str = f"{timestamp}{api_key}{5000}{param_str}"
    signature = hmac.new(api_secret.encode(), sign_str.encode(), hashlib.sha256).hexdigest()
    
    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-SIGN-TYPE": "2",
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": "5000"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}{endpoint}?{param_str}", headers=headers, timeout=10) as resp:
                data = await resp.json()
                if data.get("retCode") == 0:
                    return data.get("result", {}).get("list", [])
                else:
                    print(f"   API Error: {data.get('retMsg')}")
                    return None
    except Exception as e:
        print(f"   Request Error: {e}")
        return None

async def cleanup_user_positions(user_id: int, username: str, exchange: str, account_type: str, dry_run: bool = True):
    """Cleanup stale positions for a single user"""
    print(f"\n{'='*60}")
    print(f"👤 {username} ({user_id}) - {exchange}/{account_type}")
    print("=" * 60)
    
    if exchange != 'bybit':
        print("   ⚠️ HyperLiquid cleanup not implemented yet")
        return 0
    
    # Get DB positions
    db_positions = execute("""
        SELECT symbol, side, entry_price, size, leverage, strategy
        FROM active_positions
        WHERE user_id = %s AND exchange = %s AND account_type = %s
    """, (user_id, exchange, account_type))
    
    print(f"📊 DB Positions: {len(db_positions)}")
    
    # Get API credentials
    user = execute("""
        SELECT demo_api_key, demo_api_secret, real_api_key, real_api_secret
        FROM users WHERE user_id = %s
    """, (user_id,))
    
    if not user:
        print("   ❌ User not found")
        return 0
    
    user = user[0]
    
    if account_type in ('demo', 'testnet'):
        api_key = user.get('demo_api_key')
        api_secret = user.get('demo_api_secret')
        is_demo = True
    else:
        api_key = user.get('real_api_key')
        api_secret = user.get('real_api_secret')
        is_demo = False
    
    if not api_key or not api_secret:
        print(f"   ⚠️ No API credentials")
        return 0
    
    # Get Bybit positions
    api_positions = await get_bybit_positions(api_key, api_secret, is_demo)
    
    if api_positions is None:
        print("   ❌ Could not fetch API positions")
        return 0
    
    api_positions = [p for p in api_positions if float(p.get('size', 0)) > 0]
    api_symbols = {p['symbol'] for p in api_positions}
    
    print(f"📈 Bybit Positions: {len(api_positions)}")
    
    # Find positions to remove (in DB but not on exchange)
    removed = 0
    for pos in db_positions:
        symbol = pos['symbol']
        if symbol not in api_symbols:
            print(f"   🗑️ Removing: {symbol} | {pos['side']} | Entry: ${pos['entry_price']:.6f}")
            
            if not dry_run:
                with get_conn() as conn:
                    cur = conn.cursor()
                    cur.execute("""
                        DELETE FROM active_positions 
                        WHERE user_id = %s AND symbol = %s AND exchange = %s AND account_type = %s
                    """, (user_id, symbol, exchange, account_type))
                    conn.commit()
            removed += 1
    
    # Update size mismatches
    for pos in db_positions:
        symbol = pos['symbol']
        if symbol in api_symbols:
            api_pos = next(p for p in api_positions if p['symbol'] == symbol)
            api_size = float(api_pos.get('size', 0))
            db_size = float(pos['size'])
            
            if abs(db_size - api_size) > 0.01:
                print(f"   📝 Updating size: {symbol} | DB: {db_size} → API: {api_size}")
                
                if not dry_run:
                    with get_conn() as conn:
                        cur = conn.cursor()
                        cur.execute("""
                            UPDATE active_positions 
                            SET size = %s
                            WHERE user_id = %s AND symbol = %s AND exchange = %s AND account_type = %s
                        """, (api_size, user_id, symbol, exchange, account_type))
                        conn.commit()
    
    if removed == 0:
        print("   ✅ No stale positions found")
    else:
        mode = "DRY RUN" if dry_run else "CLEANED"
        print(f"   {'🔍' if dry_run else '✅'} {mode}: {removed} positions")
    
    return removed

async def main():
    import argparse
    parser = argparse.ArgumentParser(description='Cleanup stale positions')
    parser.add_argument('--execute', action='store_true', help='Actually delete (default is dry-run)')
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    print("=" * 70)
    print("🧹 POSITION CLEANUP")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Mode: {'DRY RUN (add --execute to delete)' if dry_run else '⚠️ EXECUTE MODE'}")
    print("=" * 70)
    
    # Get all users with positions
    users_with_positions = execute("""
        SELECT DISTINCT 
            ap.user_id,
            u.username,
            u.first_name,
            ap.exchange,
            ap.account_type
        FROM active_positions ap
        LEFT JOIN users u ON ap.user_id = u.user_id
        ORDER BY ap.user_id
    """)
    
    total_removed = 0
    for row in users_with_positions:
        username = row['username'] or row['first_name'] or str(row['user_id'])
        removed = await cleanup_user_positions(
            row['user_id'],
            username,
            row['exchange'],
            row['account_type'],
            dry_run=dry_run
        )
        total_removed += removed
    
    print("\n" + "=" * 70)
    print(f"📋 TOTAL: {total_removed} stale positions {'found' if dry_run else 'removed'}")
    if dry_run and total_removed > 0:
        print("⚠️ Run with --execute to actually delete these positions")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
