#!/usr/bin/env python3
"""Quick test HyperLiquid API"""
import asyncio
import aiohttp
import json

MAIN_WALLET = "0xF38498bFec6DCD4A27809e5d70A8989Df73d0C6c"
API_WALLET = "0x64a64f20b1d5124c0249c313903ac8df3646214a"  # Registered agent


async def main():
    print("=" * 60)
    print("HyperLiquid Quick Test")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # 1. Check balance
        print("\n1. Checking Main Wallet Balance...")
        payload = {"type": "clearinghouseState", "user": MAIN_WALLET}
        async with session.post("https://api.hyperliquid.xyz/info", json=payload) as resp:
            result = await resp.json()
            
            margin = result.get("marginSummary", {})
            perp_value = float(margin.get("accountValue", 0))
            
            spot_state = result.get("spotClearinghouseState", {})
            spot_balances = spot_state.get("balances", [])
            
            print(f"   Perp accountValue: ${perp_value:.2f}")
            
            if perp_value == 0 and spot_balances:
                print("   ✅ UNIFIED ACCOUNT DETECTED!")
                for b in spot_balances:
                    coin = b.get("coin", "USDC")
                    total = float(b.get("total", 0))
                    print(f"      {coin}: ${total:.2f}")
            else:
                print(f"   Spot balances: {spot_balances}")
        
        # 2. Check registered agents
        print("\n2. Checking Registered Agents...")
        payload = {"type": "extraAgents", "user": MAIN_WALLET}
        async with session.post("https://api.hyperliquid.xyz/info", json=payload) as resp:
            result = await resp.json()
            print(f"   Registered agents: {json.dumps(result, indent=6)}")
        
        # 3. Summary
        print("\n" + "=" * 60)
        print("SUMMARY:")
        print("=" * 60)
        print(f"Main Wallet: {MAIN_WALLET}")
        print(f"Registered API Wallet: {API_WALLET}")
        print("\n⚠️  To trade, you need the PRIVATE KEY for the registered API wallet:")
        print(f"   {API_WALLET}")
        print("\nThis private key should generate that exact address when imported.")


if __name__ == "__main__":
    asyncio.run(main())
