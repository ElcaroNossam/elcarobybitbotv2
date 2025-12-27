#!/usr/bin/env python3
"""Test HyperLiquid API with user's credentials"""
import asyncio
import sys
sys.path.insert(0, "/home/illiateslenko/UpdateProject/project-bybit/bybitv1/bybit_demo")

from db import get_hl_credentials
from hl_adapter import HLAdapter

async def test_balance(uid, testnet=True):
    """Test balance fetch for both testnet and mainnet"""
    print(f"\n{'='*60}")
    print(f"Testing HyperLiquid Balance for User {uid}")
    print(f"{'='*60}\n")
    
    # Get credentials
    creds = get_hl_credentials(uid)
    if not creds.get("hl_private_key"):
        print("❌ No HL private key found!")
        return
    
    print(f"✅ Private Key: {creds['hl_private_key'][:10]}...")
    print(f"   Vault Address: {creds.get('hl_vault_address')}")
    print(f"   DB Testnet Flag: {creds.get('hl_testnet')}")
    print()
    
    # Test both testnet and mainnet
    for test_mode in [True, False]:
        network = "🧪 TESTNET" if test_mode else "🌐 MAINNET"
        print(f"\n{'-'*60}")
        print(f"Testing {network}")
        print(f"{'-'*60}")
        
        try:
            adapter = HLAdapter(
                private_key=creds["hl_private_key"],
                testnet=test_mode,
                vault_address=creds.get("hl_vault_address")
            )
            
            print(f"✅ Adapter created (testnet={test_mode})")
            
            # Try to get balance
            result = await adapter.get_balance()
            
            print(f"\n📊 API Response:")
            print(f"   Success: {result.get('success')}")
            
            if result.get("success"):
                data = result.get("data", {})
                print(f"\n💰 Balance Data:")
                print(f"   Equity: ${data.get('equity', 0):,.2f}")
                print(f"   Available: ${data.get('available', 0):,.2f}")
                print(f"   Margin Used: ${data.get('margin_used', 0):,.2f}")
                print(f"   Unrealized PnL: ${data.get('unrealized_pnl', 0):,.2f}")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                print(f"   Full response: {result}")
            
            await adapter.close()
            
        except Exception as e:
            print(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_balance(511692487))
