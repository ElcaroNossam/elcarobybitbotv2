#!/usr/bin/env python3
"""Get wallet address from private key"""
import sys
sys.path.insert(0, "/home/illiateslenko/UpdateProject/project-bybit/bybitv1/bybit_demo")

from eth_account import Account
from db import get_hl_credentials

uid = 511692487
creds = get_hl_credentials(uid)

if creds.get("hl_private_key"):
    pk = creds["hl_private_key"]
    
    # Get wallet address from private key
    account = Account.from_key(pk)
    address = account.address
    
    print(f"\n{'='*60}")
    print(f"HyperLiquid Wallet Info")
    print(f"{'='*60}\n")
    print(f"Private Key: {pk[:10]}...")
    print(f"Wallet Address: {address}")
    print(f"\n{'='*60}")
    print(f"Check balance at:")
    print(f"🧪 Testnet: https://app.hyperliquid-testnet.xyz/explorer")
    print(f"🌐 Mainnet: https://app.hyperliquid.xyz/explorer")
    print(f"{'='*60}\n")
else:
    print("No private key found!")
