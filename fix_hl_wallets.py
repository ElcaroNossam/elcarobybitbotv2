#!/usr/bin/env python3
"""Fix HL wallet addresses in DB"""
from core.db_postgres import execute, execute_one

# Update wallet addresses to API wallet addresses (derived from keys)
execute("""
UPDATE users SET 
  hl_testnet_wallet_address = %s,
  hl_mainnet_wallet_address = %s
WHERE user_id = 511692487
""", ("0x5a1928289d14c9af8d1c5557b8756e552b6d67ec", "0x157a40d254c174a8132d207251ba24514ccc6a2f"))
print("Updated wallet addresses to API wallets")

# Verify
r = execute_one("SELECT hl_testnet_wallet_address, hl_mainnet_wallet_address FROM users WHERE user_id = 511692487")
testnet = r.get("hl_testnet_wallet_address")
mainnet = r.get("hl_mainnet_wallet_address")
print(f"Testnet wallet: {testnet}")
print(f"Mainnet wallet: {mainnet}")
