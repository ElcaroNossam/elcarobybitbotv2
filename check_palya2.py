#!/usr/bin/env python3
"""Check HL position timestamps for user Palya."""
from core.db_postgres import execute

uid = 6536903257

print("=== HL POSITIONS WITH TIMESTAMPS ===")
rows = execute(
    """SELECT symbol, side, strategy, account_type, exchange, open_ts, entry_price
       FROM active_positions 
       WHERE user_id = %s AND exchange = 'hyperliquid' 
       ORDER BY open_ts DESC""",
    (uid,)
)
for r in rows:
    print(f"  {r['symbol']:20s} {r['side']:5s} {r['strategy']:15s} {r['account_type']:10s} {r.get('open_ts', 'N/A')}")

print()
print("=== BYBIT DEMO POSITIONS WITH TIMESTAMPS ===")
rows2 = execute(
    """SELECT symbol, side, strategy, account_type, exchange, open_ts, entry_price
       FROM active_positions 
       WHERE user_id = %s AND exchange = 'bybit' AND account_type = 'demo'
       ORDER BY open_ts DESC""",
    (uid,)
)
for r in rows2:
    print(f"  {r['symbol']:20s} {r['side']:5s} {r['strategy']:15s} {r['account_type']:10s} {r.get('open_ts', 'N/A')}")

print()
print("=== MOST RECENT BYBIT REAL POSITIONS (last 5) ===")
rows3 = execute(
    """SELECT symbol, side, strategy, account_type, exchange, open_ts, entry_price
       FROM active_positions 
       WHERE user_id = %s AND exchange = 'bybit' AND account_type = 'real'
       ORDER BY open_ts DESC LIMIT 5""",
    (uid,)
)
for r in rows3:
    print(f"  {r['symbol']:20s} {r['side']:5s} {r['strategy']:15s} {r['account_type']:10s} {r.get('open_ts', 'N/A')}")

print()
print("=== TRADE LOGS (last 10 HL entries) ===")
rows4 = execute(
    """SELECT symbol, side, strategy, account_type, exchange, ts, entry_price, exit_price, pnl, exit_reason
       FROM trade_logs 
       WHERE user_id = %s AND exchange = 'hyperliquid'
       ORDER BY ts DESC LIMIT 10""",
    (uid,)
)
for r in rows4:
    print(f"  {r['symbol']:20s} {r['side']:5s} {r['strategy'] or 'N/A':15s} {r['account_type']:10s} {r.get('ts', 'N/A')} pnl={r.get('pnl', 'N/A')}")

print()
print("=== USER SETTINGS HISTORY (routing_policy changes) ===")
rows5 = execute(
    """SELECT action_type, old_value, new_value, source, created_at
       FROM user_activity_log 
       WHERE user_id = %s AND (action_type LIKE '%%routing%%' OR action_type LIKE '%%exchange%%' OR action_type LIKE '%%trading_mode%%')
       ORDER BY created_at DESC LIMIT 20""",
    (uid,)
)
if rows5:
    for r in rows5:
        print(f"  {r['action_type']:30s} old={r.get('old_value')} → new={r.get('new_value')} source={r.get('source')} at={r.get('created_at')}")
else:
    print("  No activity log entries found")
