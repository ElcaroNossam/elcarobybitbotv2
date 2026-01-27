#!/usr/bin/env python3
"""
Position Verification Script - сверка позиций в БД с реальными на бирже
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_postgres import execute
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
                    return []
    except Exception as e:
        print(f"   Request Error: {e}")
        return []

async def verify_user_positions(user_id: int, username: str, exchange: str, account_type: str):
    """Verify positions for a single user"""
    print(f"\n{'='*60}")
    print(f"👤 {username} ({user_id}) - {exchange}/{account_type}")
    print("=" * 60)
    
    # Get DB positions
    db_positions = execute("""
        SELECT symbol, side, entry_price, size, leverage, strategy, open_ts
        FROM active_positions
        WHERE user_id = %s AND exchange = %s AND account_type = %s
        ORDER BY symbol
    """, (user_id, exchange, account_type))
    
    print(f"\n📊 DB Positions: {len(db_positions)}")
    
    if exchange != 'bybit':
        print("   ⚠️ HyperLiquid verification not implemented yet")
        return
    
    # Get API credentials
    user = execute("""
        SELECT demo_api_key, demo_api_secret, real_api_key, real_api_secret
        FROM users WHERE user_id = %s
    """, (user_id,))
    
    if not user:
        print("   ❌ User not found in DB")
        return
    
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
        print(f"   ⚠️ No API credentials for {account_type}")
        return
    
    # Get Bybit positions
    print(f"\n🔄 Fetching from Bybit {'Demo' if is_demo else 'Real'}...")
    api_positions = await get_bybit_positions(api_key, api_secret, is_demo)
    
    # Filter only positions with size > 0
    api_positions = [p for p in api_positions if float(p.get('size', 0)) > 0]
    print(f"📈 Bybit Positions: {len(api_positions)}")
    
    # Create lookup sets
    db_symbols = {p['symbol'] for p in db_positions}
    api_symbols = {p['symbol'] for p in api_positions}
    
    # Find discrepancies
    missing_in_api = db_symbols - api_symbols
    missing_in_db = api_symbols - db_symbols
    common = db_symbols & api_symbols
    
    if missing_in_api:
        print(f"\n⚠️ In DB but NOT on Bybit ({len(missing_in_api)}):")
        for sym in sorted(missing_in_api):
            db_pos = next(p for p in db_positions if p['symbol'] == sym)
            print(f"   🔴 {sym} | {db_pos['side']} | Entry: ${db_pos['entry_price']:.6f} | Strategy: {db_pos['strategy']}")
    
    if missing_in_db:
        print(f"\n⚠️ On Bybit but NOT in DB ({len(missing_in_db)}):")
        for sym in sorted(missing_in_db):
            api_pos = next(p for p in api_positions if p['symbol'] == sym)
            side = api_pos.get('side', '?')
            entry = float(api_pos.get('avgPrice', 0))
            size = float(api_pos.get('size', 0))
            print(f"   🟡 {sym} | {side} | Entry: ${entry:.6f} | Size: {size}")
    
    # Check common positions for data mismatch
    mismatches = []
    for sym in common:
        db_pos = next(p for p in db_positions if p['symbol'] == sym)
        api_pos = next(p for p in api_positions if p['symbol'] == sym)
        
        db_side = db_pos['side']
        api_side = api_pos.get('side', '')
        
        # Normalize sides
        db_side_norm = 'Buy' if db_side.lower() in ('buy', 'long') else 'Sell'
        api_side_norm = api_side
        
        db_size = float(db_pos['size'])
        api_size = float(api_pos.get('size', 0))
        
        if db_side_norm != api_side_norm:
            mismatches.append((sym, 'side', db_side, api_side))
        
        if abs(db_size - api_size) > 0.001:
            mismatches.append((sym, 'size', db_size, api_size))
    
    if mismatches:
        print(f"\n⚠️ Data Mismatches ({len(mismatches)}):")
        for sym, field, db_val, api_val in mismatches:
            print(f"   ⚡ {sym} - {field}: DB={db_val} vs API={api_val}")
    
    if not missing_in_api and not missing_in_db and not mismatches:
        print(f"\n✅ All {len(common)} positions match!")
    
    return {
        'user_id': user_id,
        'db_count': len(db_positions),
        'api_count': len(api_positions),
        'missing_in_api': list(missing_in_api),
        'missing_in_db': list(missing_in_db),
        'mismatches': mismatches
    }

async def main():
    print("=" * 70)
    print("🔍 POSITION VERIFICATION REPORT")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
    
    print(f"\n📊 Found {len(users_with_positions)} user/account combinations with positions")
    
    results = []
    for row in users_with_positions:
        username = row['username'] or row['first_name'] or str(row['user_id'])
        result = await verify_user_positions(
            row['user_id'],
            username,
            row['exchange'],
            row['account_type']
        )
        if result:
            results.append(result)
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 SUMMARY")
    print("=" * 70)
    
    total_db = sum(r['db_count'] for r in results)
    total_api = sum(r['api_count'] for r in results)
    total_missing_api = sum(len(r['missing_in_api']) for r in results)
    total_missing_db = sum(len(r['missing_in_db']) for r in results)
    total_mismatches = sum(len(r['mismatches']) for r in results)
    
    print(f"\n📊 Total DB Positions: {total_db}")
    print(f"📈 Total API Positions: {total_api}")
    print(f"🔴 Missing on Exchange: {total_missing_api}")
    print(f"🟡 Missing in DB: {total_missing_db}")
    print(f"⚡ Data Mismatches: {total_mismatches}")
    
    if total_missing_api > 0:
        print(f"\n⚠️ ATTENTION: {total_missing_api} positions in DB but closed on exchange!")
        print("   Consider running position cleanup to remove stale records")
    
    if total_missing_db > 0:
        print(f"\n⚠️ ATTENTION: {total_missing_db} positions on exchange but not tracked!")
        print("   These may be manually opened positions")
    
    print("\n" + "=" * 70)
    print("✅ VERIFICATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
