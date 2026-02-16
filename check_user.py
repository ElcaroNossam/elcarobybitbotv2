#!/usr/bin/env python3
"""Check user routing settings."""
from core.db_postgres import get_conn

uid = 6536903257

with get_conn() as conn:
    cur = conn.cursor()
    cur.execute("""SELECT user_id, exchange_type, trading_mode, routing_policy, hl_enabled, hl_testnet,
                          demo_api_key IS NOT NULL AND demo_api_key != '' as has_demo,
                          real_api_key IS NOT NULL AND real_api_key != '' as has_real,
                          hl_testnet_private_key IS NOT NULL AND hl_testnet_private_key != '' as has_hl_testnet,
                          hl_mainnet_private_key IS NOT NULL AND hl_mainnet_private_key != '' as has_hl_mainnet,
                          live_enabled, bybit_enabled
                   FROM users WHERE user_id = %s""", (uid,))
    row = cur.fetchone()
    if row:
        cols = [d[0] for d in cur.description]
        for c, v in zip(cols, row):
            print(f"{c}: {v}")
    else:
        print("User not found")
