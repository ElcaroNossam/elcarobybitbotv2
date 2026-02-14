#!/usr/bin/env python3
"""Check trade distribution for a user."""
from core.db_postgres import execute

UID = 511692487

rows = execute("SELECT strategy, exchange, account_type, COUNT(*) as cnt FROM trade_logs WHERE user_id = %s GROUP BY strategy, exchange, account_type ORDER BY cnt DESC", (UID,))
print("=== STRATEGY / EXCHANGE DISTRIBUTION ===")
for r in rows:
    s = r["strategy"] or "NULL"
    e = r["exchange"] or "NULL"
    a = r["account_type"] or "NULL"
    print(f"  {s:20s} | {e:15s} | {a:10s} | count={r['cnt']}")

manual = execute("SELECT id, symbol, side, strategy, exchange, account_type, exit_reason, ts::text FROM trade_logs WHERE user_id = %s AND (strategy IS NULL OR strategy IN ('manual', 'unknown')) ORDER BY ts DESC LIMIT 20", (UID,))
print(f"\n=== MANUAL/UNKNOWN/NULL TRADES ({len(manual)} found) ===")
for r in manual:
    print(f"  id={r['id']} {(r['symbol'] or '?'):15s} {(r['side'] or '?'):5s} strat={r['strategy']} exch={r['exchange']} acc={r['account_type']} reason={r['exit_reason']} ts={r['ts']}")

# Check DOGE, ZK specifically
doge_zk = execute("SELECT id, symbol, side, strategy, exchange, account_type, exit_reason, pnl, ts::text FROM trade_logs WHERE user_id = %s AND (symbol LIKE '%%DOGE%%' OR symbol LIKE '%%ZK%%') ORDER BY ts DESC LIMIT 20", (UID,))
print(f"\n=== DOGE/ZK TRADES ({len(doge_zk)} found) ===")
for r in doge_zk:
    print(f"  id={r['id']} {(r['symbol'] or '?'):15s} {(r['side'] or '?'):5s} strat={r['strategy']} exch={r['exchange']} pnl={r['pnl']} ts={r['ts']}")

pos = execute("SELECT symbol, side, strategy, exchange, account_type FROM active_positions WHERE user_id = %s ORDER BY exchange, symbol", (UID,))
print(f"\n=== ACTIVE POSITIONS ({len(pos)}) ===")
for p in pos:
    print(f"  {(p['symbol'] or '?'):15s} {(p['side'] or '?'):5s} strat={p['strategy']} exch={p['exchange']} acc={p['account_type']}")

hl = execute("SELECT COUNT(*) as cnt FROM trade_logs WHERE user_id = %s AND exchange = 'hyperliquid'", (UID,))
print(f"\nHL trade_logs count: {hl[0]['cnt']}")
total = execute("SELECT COUNT(*) as cnt FROM trade_logs WHERE user_id = %s", (UID,))
print(f"Total trade_logs: {total[0]['cnt']}")

# Recent trades to see pattern
recent = execute("SELECT id, symbol, side, strategy, exchange, account_type, exit_reason, pnl, ts::text FROM trade_logs WHERE user_id = %s ORDER BY ts DESC LIMIT 15", (UID,))
print(f"\n=== LAST 15 TRADES ===")
for r in recent:
    print(f"  id={r['id']} {(r['symbol'] or '?'):15s} {(r['side'] or '?'):5s} strat={r['strategy']:15s} exch={r['exchange'] or 'NULL':12s} reason={r['exit_reason']} pnl={r['pnl']} ts={r['ts']}")
