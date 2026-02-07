"""Check API wallet authorization on both networks"""
import asyncio
import aiohttp

async def check_extra_agents():
    """Check if API wallet is registered as agent for main wallet"""
    api_wallet = "0x64a64F20b1D5124C0249c313903aC8dF3646214A"
    main_wallet = "0xF38498bFec6DCD4A27809e5d70A8989Df73d0C6c"
    
    async with aiohttp.ClientSession() as session:
        # Check TESTNET extra agents for main wallet
        print("=== TESTNET: Checking extra agents for main wallet ===")
        print(f"Main wallet: {main_wallet}")
        print(f"API wallet:  {api_wallet}")
        async with session.post(
            "https://api.hyperliquid-testnet.xyz/info",
            json={"type": "extraAgents", "user": main_wallet}
        ) as resp:
            testnet_agents = await resp.json()
            print(f"Testnet agents: {testnet_agents}")
            if testnet_agents:
                for agent in testnet_agents:
                    print(f"  - {agent.get('address', 'unknown')} ({agent.get('name', 'unnamed')})")
                    if agent.get('address', '').lower() == api_wallet.lower():
                        print("    ✅ API wallet is registered!")
            else:
                print("  ❌ No agents registered on testnet!")
        
        # Check MAINNET extra agents for main wallet
        print("\n=== MAINNET: Checking extra agents for main wallet ===")
        async with session.post(
            "https://api.hyperliquid.xyz/info",
            json={"type": "extraAgents", "user": main_wallet}
        ) as resp:
            mainnet_agents = await resp.json()
            print(f"Mainnet agents: {mainnet_agents}")
            if mainnet_agents:
                for agent in mainnet_agents:
                    print(f"  - {agent.get('address', 'unknown')} ({agent.get('name', 'unnamed')})")
                    if agent.get('address', '').lower() == api_wallet.lower():
                        print("    ✅ API wallet is registered!")
            else:
                print("  ❌ No agents registered on mainnet!")

if __name__ == "__main__":
    asyncio.run(check_extra_agents())
