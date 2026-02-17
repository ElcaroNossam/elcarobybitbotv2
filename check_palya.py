#!/usr/bin/env python3
"""Check user Palya's routing configuration."""
import db

uid = 6536903257
print("=== USER STATE ===")
print("exchange_type:", db.get_exchange_type(uid))
print("trading_mode:", db.get_trading_mode(uid))
print("routing_policy:", db.get_routing_policy(uid))
print("hl_enabled:", db.is_hl_enabled(uid))
print("bybit_enabled:", db.is_bybit_enabled(uid))
print("live_enabled:", db.get_live_enabled(uid))
print()

hl_creds = db.get_hl_credentials(uid)
print("=== HL CREDENTIALS ===")
print("hl_testnet_private_key:", bool(hl_creds.get("hl_testnet_private_key")))
print("hl_mainnet_private_key:", bool(hl_creds.get("hl_mainnet_private_key")))
print("hl_private_key:", bool(hl_creds.get("hl_private_key")))
print("hl_testnet_flag:", hl_creds.get("hl_testnet"))
print("hl_enabled_flag:", hl_creds.get("hl_enabled"))
print()

print("=== EXECUTION TARGETS ===")
for strat in ["oi", "scryptomera", "scalper", "elcaro", "fibonacci", "rsi_bb"]:
    targets = db.get_execution_targets(uid, strat)
    print(f"  {strat}: {targets}")
print()

print("=== STRATEGY TRADING MODES ===")
for strat in ["oi", "scryptomera", "scalper", "elcaro", "fibonacci", "rsi_bb"]:
    mode = db.get_strategy_trading_mode(uid, strat)
    print(f"  {strat}: {mode}")
print()

print("=== STRATEGY SETTINGS (raw) ===")
for strat in ["oi", "scryptomera"]:
    settings = db.get_strategy_settings(uid, strat)
    tm = settings.get("trading_mode") if settings else None
    enabled_l = settings.get("long_enabled") if settings else None
    enabled_s = settings.get("short_enabled") if settings else None
    print(f"  {strat}: trading_mode={tm}, long_enabled={enabled_l}, short_enabled={enabled_s}")
print()

print("=== ACTIVE POSITIONS ===")
from core.db_postgres import execute
rows = execute("SELECT symbol, side, strategy, account_type, exchange FROM active_positions WHERE user_id = %s", (uid,))
for r in rows:
    print(f"  {r}")
