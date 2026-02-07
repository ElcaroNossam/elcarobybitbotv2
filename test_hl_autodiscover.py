#!/usr/bin/env python3
"""Test HyperLiquid auto-discovery of main wallet from agent"""
import asyncio
import sys
sys.path.insert(0, "/Users/elcarosam/project/elcarobybitbotv2")

from hl_adapter import HLAdapter


async def test_auto_discovery():
    print("=" * 60)
    print("HyperLiquid Auto-Discovery Test")
    print("=" * 60)
    
    # Use a private key that IS registered as agent
    # The registered agent is: 0x64a64f20b1d5124c0249c313903ac8df3646214a
    # Main wallet is: 0xF38498bFec6DCD4A27809e5d70A8989Df73d0C6c
    
    # But we only have this private key which gives 0xf1E2cC78...
    # This is NOT the registered agent!
    TEST_PRIVATE_KEY = "0xcd4c1fcb7af13bc6d48a227b2a7e9e4db680c32c9f23e04a6aa83e35e29fed80"
    
    print(f"\nTesting with private key: {TEST_PRIVATE_KEY[:15]}...")
    print("-" * 60)
    
    async with HLAdapter(private_key=TEST_PRIVATE_KEY, testnet=False) as adapter:
        print(f"\nAPI Wallet Address: {adapter.address}")
        print(f"Main Wallet (discovered): {adapter.main_wallet_address}")
        print(f"Vault Address (client): {adapter._client._vault_address}")
        
        # Try to get balance
        print("\n" + "-" * 60)
        print("Trying to get balance...")
        balance = await adapter.get_balance(use_cache=False)
        print(f"Balance result: {balance}")
        
        if adapter.main_wallet_address != adapter.address:
            print("\n✅ SUCCESS: Main wallet was auto-discovered!")
        else:
            print("\n❌ FAILED: Main wallet NOT discovered (wallet is not a registered agent)")
            print("   You need to use a private key for a registered API wallet")


if __name__ == "__main__":
    asyncio.run(test_auto_discovery())
