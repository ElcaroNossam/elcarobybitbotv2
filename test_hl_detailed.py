#!/usr/bin/env python3
"""Detailed HyperLiquid API test"""
import asyncio
import sys
import json
sys.path.insert(0, "/home/illiateslenko/UpdateProject/project-bybit/bybitv1/bybit_demo")

from db import get_hl_credentials
from hl_adapter import HLAdapter

async def detailed_test(uid):
    print(f"\n{'='*70}")
    print(f"DETAILED HYPERLIQUID API TEST - User {uid}")
    print(f"{'='*70}\n")
    
    creds = get_hl_credentials(uid)
    if not creds.get("hl_private_key"):
        print("❌ No private key!")
        return
    
    print(f"🔑 Private Key: ***REDACTED*** (length: {len(creds['hl_private_key'])})")
    print(f"📍 Vault Address: {creds.get('hl_vault_address')}")
    
    # Test TESTNET
    print(f"\n{'='*70}")
    print(f"🧪 TESTNET TEST")
    print(f"{'='*70}\n")
    
    adapter = HLAdapter(
        private_key=creds["hl_private_key"],
        testnet=True,
        vault_address=creds.get("hl_vault_address")
    )
    
    print(f"1️⃣ Testing get_balance()...")
    balance_result = await adapter.get_balance()
    print(f"   Raw response: {json.dumps(balance_result, indent=2)}\n")
    
    print(f"2️⃣ Testing fetch_balance()...")
    fetch_result = await adapter.fetch_balance()
    print(f"   Raw response: {json.dumps(fetch_result, indent=2)}\n")
    
    print(f"3️⃣ Testing get_portfolio()...")
    try:
        portfolio_result = await adapter.get_portfolio()
        print(f"   Raw response: {json.dumps(portfolio_result, indent=2)}\n")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    print(f"4️⃣ Testing fetch_positions()...")
    try:
        positions = await adapter.fetch_positions()
        print(f"   Positions count: {len(positions)}")
        print(f"   Raw response: {json.dumps(positions, indent=2)}\n")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    await adapter.close()
    
    print(f"\n{'='*70}")
    print(f"✅ Test completed!")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    asyncio.run(detailed_test(511692487))
