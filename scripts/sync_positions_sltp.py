#!/usr/bin/env python3
"""
Скрипт синхронизации SL/TP цен в БД с актуальными значениями с биржи.
Исправляет исторические позиции где SL/TP = NULL.

Запуск: python3 scripts/sync_positions_sltp.py
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_postgres import execute, get_conn
import db


async def get_bybit_positions(user_id: int, account_type: str) -> dict:
    """Получить позиции с Bybit для пользователя."""
    import aiohttp
    import time
    import hashlib
    import hmac
    
    creds = db.get_all_user_credentials(user_id)
    if not creds:
        return {}
    
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
        return {}
    
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
                        positions = {}
                        for pos in data.get('result', {}).get('list', []):
                            size = float(pos.get('size') or 0)
                            if size > 0:
                                symbol = pos.get('symbol')
                                # Handle empty strings from Bybit API
                                sl_val = pos.get('stopLoss', '')
                                tp_val = pos.get('takeProfit', '')
                                positions[symbol] = {
                                    'sl_price': float(sl_val) if sl_val else None,
                                    'tp_price': float(tp_val) if tp_val else None,
                                    'side': pos.get('side'),
                                    'size': size,
                                    'entry_price': float(pos.get('avgPrice') or 0),
                                    'leverage': float(pos.get('leverage') or 1),
                                }
                        return positions
    except Exception as e:
        print(f"  ⚠️ Ошибка API для user {user_id}: {e}")
    
    return {}


async def sync_positions():
    """Синхронизировать SL/TP для всех позиций."""
    print("=" * 70)
    print("🔄 СИНХРОНИЗАЦИЯ SL/TP ЦЕН С БИРЖИ")
    print("=" * 70)
    
    # Получаем все позиции без SL/TP
    positions = execute("""
        SELECT user_id, symbol, account_type, exchange, side, entry_price, 
               sl_price, tp_price, strategy
        FROM active_positions
        ORDER BY user_id, symbol
    """)
    
    print(f"\n📊 Найдено {len(positions)} активных позиций в БД")
    
    # Группируем по user_id и account_type
    user_positions = {}
    for pos in positions:
        key = (pos['user_id'], pos['account_type'], pos['exchange'])
        if key not in user_positions:
            user_positions[key] = []
        user_positions[key].append(pos)
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for (user_id, account_type, exchange), user_pos_list in user_positions.items():
        print(f"\n👤 User {user_id} ({exchange}/{account_type}): {len(user_pos_list)} позиций")
        
        if exchange != 'bybit':
            print(f"   ⏭️ Пропуск - HyperLiquid (пока не поддерживается)")
            skipped_count += len(user_pos_list)
            continue
        
        # Получаем актуальные позиции с биржи
        exchange_positions = await get_bybit_positions(user_id, account_type)
        
        if not exchange_positions:
            print(f"   ⚠️ Не удалось получить позиции с биржи (нет ключей или ошибка)")
            skipped_count += len(user_pos_list)
            continue
        
        print(f"   📡 Получено {len(exchange_positions)} позиций с биржи")
        
        for db_pos in user_pos_list:
            symbol = db_pos['symbol']
            
            if symbol not in exchange_positions:
                print(f"   ❓ {symbol}: не найдена на бирже (возможно закрыта)")
                continue
            
            ex_pos = exchange_positions[symbol]
            old_sl = db_pos['sl_price']
            old_tp = db_pos['tp_price']
            new_sl = ex_pos['sl_price']
            new_tp = ex_pos['tp_price']
            
            # Проверяем нужно ли обновлять
            need_update = False
            changes = []
            
            if old_sl != new_sl:
                need_update = True
                changes.append(f"SL: {old_sl} → {new_sl}")
            
            if old_tp != new_tp:
                need_update = True
                changes.append(f"TP: {old_tp} → {new_tp}")
            
            if need_update:
                try:
                    db.update_position_sltp(
                        user_id=user_id,
                        symbol=symbol,
                        account_type=account_type,
                        sl_price=new_sl,
                        tp_price=new_tp
                    )
                    updated_count += 1
                    print(f"   ✅ {symbol}: {', '.join(changes)}")
                except Exception as e:
                    error_count += 1
                    print(f"   ❌ {symbol}: ошибка обновления - {e}")
            else:
                print(f"   ✓ {symbol}: уже актуально (SL={new_sl}, TP={new_tp})")
    
    print("\n" + "=" * 70)
    print(f"📊 РЕЗУЛЬТАТ:")
    print(f"   ✅ Обновлено: {updated_count}")
    print(f"   ⏭️ Пропущено: {skipped_count}")
    print(f"   ❌ Ошибок: {error_count}")
    print("=" * 70)
    
    # Проверяем результат
    after_check = execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(sl_price) as with_sl,
            COUNT(tp_price) as with_tp
        FROM active_positions
    """)
    
    row = after_check[0]
    print(f"\n📈 СОСТОЯНИЕ БД ПОСЛЕ СИНХРОНИЗАЦИИ:")
    print(f"   Всего позиций: {row['total']}")
    print(f"   С SL ценой: {row['with_sl']}")
    print(f"   С TP ценой: {row['with_tp']}")


if __name__ == "__main__":
    asyncio.run(sync_positions())
