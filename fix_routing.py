#!/usr/bin/env python3
"""Fix routing for user 6536903257.

User wants: Bybit Real + HL Testnet only.
Current: routing_policy='all_enabled' → opens on all 4 accounts.
Fix: routing_policy=NULL (uses trading_mode), trading_mode='real', hl_testnet=True
"""
from core.db_postgres import get_conn

uid = 6536903257

with get_conn() as conn:
    cur = conn.cursor()
    
    # Fix routing: NULL = uses trading_mode
    # trading_mode='real' → Bybit Real
    # hl_testnet=True → HL Testnet  
    cur.execute("""UPDATE users 
                   SET routing_policy = NULL,
                       trading_mode = 'real',
                       hl_testnet = 1
                   WHERE user_id = %s""", (uid,))
    conn.commit()
    print(f"Updated {cur.rowcount} row(s)")
    
    # Verify
    cur.execute("""SELECT routing_policy, trading_mode, hl_testnet, exchange_type
                   FROM users WHERE user_id = %s""", (uid,))
    row = cur.fetchone()
    cols = [d[0] for d in cur.description]
    for c, v in zip(cols, row):
        print(f"  {c}: {v}")
    
    print("\nResult: Bybit Real + HL Testnet only")
