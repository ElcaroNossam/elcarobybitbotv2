#!/usr/bin/env python3
"""
Скрипт очистки закрытых позиций из БД.
Удаляет позиции которые уже не существуют на бирже.

Запуск: python3 scripts/cleanup_closed_positions.py
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_postgres import execute, get_conn
import db


async def get_bybit_positions(user_id: int, account_type: str) -> set:
    """Получить список символов с открытыми позициями на Bybit."""
    import aiohttp
    import time
    import hashlib
    import hmac
    
    creds = db.get_all_user_credentials(user_id)
    if not creds:
        return set()
    
    # Выбираем ключи в зависимости от account_type
    if account_type in ('demo', 'testnet'):
        api_key = creds.get('demo_api_key') or ''
        api_secret = creds.get('demo_api_secret') or ''
        base_url = "https://api-demo.bybit.com"
    else:
        api_key = creds.get('real_api_key') or ''
        api_secret = creds.get('real_api_secret') or ''
        base_url = "https://api.bybit.com"
    
    # Проверяем что ключи не пустые
    if not api_key.strip() or not api_secret.strip():
        return set()
    
    # Формируем запрос
    timestamp = str(int(time.time() * 1000))
    params = f"category=linear&settleCoin=USDT"
    sign_str = f"{timestamp}{api_key}5000{params}"
    signature = hmac.new(api_secret.encode(), sign_str.encode(), hashlib.sha256).hexdigest()
    
    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-SIGN": signature,
        "X-BAPI-RECV-WINDOW": "5000",
    }
    
    url = f"{base_url}/v5/position/list?{params}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('retCode') == 0:
                        symbols = set()
                        for pos in data.get('result', {}).get('list', []):
                            size = float(pos.get('size') or 0)
                            if size > 0:
                                symbols.add(pos.get('symbol'))
                        return symbols
    except Exception as e:
        print(f"  ⚠️ Ошибка API для user {user_id}: {e}")
    
    return set()


async def cleanup_positions():
    """Удалить закрытые позиции из БД."""
    print("=" * 70)
    print("🧹 ОЧИСТКА ЗАКРЫТЫХ ПОЗИЦИЙ ИЗ БД")
    print("=" * 70)
    
    # Получаем все позиции из БД
    positions = execute("""
        SELECT user_id, symbol, account_type, exchange, side, entry_price
        FROM active_positions
        ORDER BY user_id, symbol
    """)
    
    print(f"\n📊 Найдено {len(positions)} позиций в БД")
    
    # Группируем по user_id и account_type
    user_positions = {}
    for pos in positions:
        key = (pos['user_id'], pos['account_type'], pos['exchange'])
        if key not in user_positions:
            user_positions[key] = []
        user_positions[key].append(pos)
    
    deleted_count = 0
    skipped_count = 0
    kept_count = 0
    
    for (user_id, account_type, exchange), user_pos_list in user_positions.items():
        print(f"\n👤 User {user_id} ({exchange}/{account_type}): {len(user_pos_list)} позиций в БД")
        
        if exchange != 'bybit':
            print(f"   ⏭️ Пропуск - HyperLiquid (пока не поддерживается)")
            skipped_count += len(user_pos_list)
            continue
        
        # Получаем актуальные позиции с биржи
        exchange_symbols = await get_bybit_positions(user_id, account_type)
        
        if not exchange_symbols and len(user_pos_list) > 0:
            # Проверяем есть ли API ключи
            creds = db.get_all_user_credentials(user_id)
            api_key = creds.get('demo_api_key' if account_type == 'demo' else 'real_api_key', '')
            if not api_key.strip():
                print(f"   ⚠️ Нет API ключей - пропускаем")
                skipped_count += len(user_pos_list)
                continue
        
        print(f"   📡 Активных позиций на бирже: {len(exchange_symbols)}")
        
        for db_pos in user_pos_list:
            symbol = db_pos['symbol']
            
            if symbol in exchange_symbols:
                kept_count += 1
                print(f"   ✓ {symbol}: активна на бирже")
            else:
                # Позиция закрыта - удаляем из БД
                try:
                    with get_conn() as conn:
                        cur = conn.cursor()
                        cur.execute("""
                            DELETE FROM active_positions 
                            WHERE user_id = %s AND symbol = %s AND account_type = %s
                        """, (user_id, symbol, account_type))
                        conn.commit()
                    deleted_count += 1
                    print(f"   🗑️ {symbol}: удалена (закрыта на бирже)")
                except Exception as e:
                    print(f"   ❌ {symbol}: ошибка удаления - {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 РЕЗУЛЬТАТ:")
    print(f"   🗑️ Удалено: {deleted_count}")
    print(f"   ✓ Сохранено: {kept_count}")
    print(f"   ⏭️ Пропущено: {skipped_count}")
    print("=" * 70)
    
    # Проверяем результат
    after_check = execute("SELECT COUNT(*) as total FROM active_positions")
    print(f"\n📈 Позиций в БД после очистки: {after_check[0]['total']}")


if __name__ == "__main__":
    asyncio.run(cleanup_positions())
