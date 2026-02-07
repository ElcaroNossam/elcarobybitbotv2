#!/usr/bin/env python3
"""
Check extra agents registration on testnet and mainnet.
"""
import asyncio
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2


def get_hl_credentials(user_id: int):
    """Get HL credentials from production database."""
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        database="elcaro",
        user="elcaro",
        password="elcaro_prod_2026"
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT hl_testnet_private_key, hl_testnet_wallet_address,
               hl_mainnet_private_key, hl_mainnet_wallet_address
        FROM users WHERE user_id = %s
    """, (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if not row:
        return None
    
    return {
        "testnet_key": row[0],
        "testnet_wallet": row[1],
        "mainnet_key": row[2],
        "mainnet_wallet": row[3],
    }


async def check_agents():
    """Check agent registrations."""
    from hyperliquid.client import HyperLiquidClient
    from hyperliquid.signer import get_address_from_private_key
    from hyperliquid.constants import TESTNET_API_URL, MAINNET_API_URL
    import aiohttp
    
    user_id = 511692487
    creds = get_hl_credentials(user_id)
    
    if not creds:
        print("No credentials found!")
        return
    
    testnet_api_wallet = get_address_from_private_key(creds['testnet_key'])
    mainnet_api_wallet = get_address_from_private_key(creds['mainnet_key'])
    main_wallet = creds['mainnet_wallet']  # Same for both networks
    
    print("=== WALLET ADDRESSES ===")
    print(f"Main Wallet: {main_wallet}")
    print(f"Testnet API Wallet: {testnet_api_wallet}")
    print(f"Mainnet API Wallet: {mainnet_api_wallet}")
    
    async with aiohttp.ClientSession() as session:
        # Check TESTNET - main wallet's agents
        print("\n=== TESTNET: Main wallet's extraAgents ===")
        async with session.post(
            f"{TESTNET_API_URL}/info",
            json={"type": "extraAgents", "user": main_wallet}
        ) as resp:
            text = await resp.text()
            data = json.loads(text)
            print(f"Agents registered FOR main wallet on testnet:")
            for agent in data:
                print(f"  - {agent.get('address', agent.get('agentAddress', 'N/A'))} (name: {agent.get('name', 'N/A')})")
            if not data:
                print("  (none)")
        
        # Check TESTNET - testnet API wallet's agents (what vaults does it trade for?)
        print("\n=== TESTNET: Testnet API wallet is agent for... ===")
        # There's no direct API for this, but we can check clearinghouseState
        async with session.post(
            f"{TESTNET_API_URL}/info",
            json={"type": "clearinghouseState", "user": testnet_api_wallet}
        ) as resp:
            text = await resp.text()
            data = json.loads(text)
            print(f"Testnet API wallet own balance: ${data.get('marginSummary', {}).get('accountValue', 0)}")
        
        # Check MAINNET - main wallet's agents
        print("\n=== MAINNET: Main wallet's extraAgents ===")
        async with session.post(
            f"{MAINNET_API_URL}/info",
            json={"type": "extraAgents", "user": main_wallet}
        ) as resp:
            text = await resp.text()
            data = json.loads(text)
            print(f"Agents registered FOR main wallet on mainnet:")
            for agent in data:
                print(f"  - {agent.get('address', agent.get('agentAddress', 'N/A'))} (name: {agent.get('name', 'N/A')})")
            if not data:
                print("  (none)")
        
        # Check testnet API wallet's registration
        print("\n=== TESTNET: What is testnet API wallet registered for? ===")
        # Check if it's self-registered (trading for itself)
        async with session.post(
            f"{TESTNET_API_URL}/info",
            json={"type": "extraAgents", "user": testnet_api_wallet}
        ) as resp:
            text = await resp.text()
            data = json.loads(text)
            print(f"Agents FOR testnet API wallet (self):")
            for agent in data:
                print(f"  - {agent.get('address', agent.get('agentAddress', 'N/A'))} (name: {agent.get('name', 'N/A')})")
            if not data:
                print("  (none - it trades for itself)")


if __name__ == "__main__":
    asyncio.run(check_agents())
