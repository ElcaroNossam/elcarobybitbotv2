#!/usr/bin/env python3
"""Check if we can discover main wallet from API wallet"""
import asyncio
import aiohttp
import json

# The API wallet address derived from the private key you gave (0xcd4c...)
API_WALLET = "0xf1E2cC781A82B665B2eCf77242f3101b0Cf008e1"

# The registered agent for your main wallet
REGISTERED_AGENT = "0x64a64f20b1d5124c0249c313903ac8df3646214a"

# Your main wallet
MAIN_WALLET = "0xF38498bFec6DCD4A27809e5d70A8989Df73d0C6c"


async def main():
    print("=" * 60)
    print("HyperLiquid Agent Discovery Test")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # 1. Check userRole - can tell us if address is user/agent/vault
        print("\n1. Checking userRole for your API wallet private key...")
        payload = {"type": "userRole", "user": API_WALLET}
        async with session.post("https://api.hyperliquid.xyz/info", json=payload) as resp:
            result = await resp.json()
            print(f"   {API_WALLET[:20]}...")
            print(f"   Role: {json.dumps(result)}")
        
        # 2. Check the registered agent
        print("\n2. Checking userRole for registered agent...")
        payload = {"type": "userRole", "user": REGISTERED_AGENT}
        async with session.post("https://api.hyperliquid.xyz/info", json=payload) as resp:
            result = await resp.json()
            print(f"   {REGISTERED_AGENT[:20]}...")
            print(f"   Role: {json.dumps(result)}")
        
        # 3. If agent, does it tell us the parent?
        # The 'role' response for an agent should include 'parent' field
        print("\n3. Detailed agent info (if role=agent)...")
        for name, addr in [("API_WALLET", API_WALLET), ("REGISTERED", REGISTERED_AGENT)]:
            payload = {"type": "userRole", "user": addr}
            async with session.post("https://api.hyperliquid.xyz/info", json=payload) as resp:
                result = await resp.json()
                if result.get("role") == "agent":
                    print(f"   {name} is an AGENT!")
                    print(f"   Full response: {json.dumps(result, indent=4)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY:")
        print("=" * 60)
        print(f"\nYour private key (0xcd4c...) generates: {API_WALLET}")
        print(f"But your main wallet has approved: {REGISTERED_AGENT}")
        print(f"\nThese are DIFFERENT addresses!")
        print(f"\nTo fix this, you need either:")
        print(f"1. Find the private key for {REGISTERED_AGENT}")
        print(f"2. OR create a new agent on HyperLiquid UI and use THAT private key")


if __name__ == "__main__":
    asyncio.run(main())
