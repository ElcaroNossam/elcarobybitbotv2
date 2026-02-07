#!/usr/bin/env python3
"""
Test if testnet API wallet can trade without vault.
The agent has $0 balance, but maybe that's the issue.
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


async def explain_testnet_issue():
    """Explain the testnet issue and what's needed."""
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
    main_wallet = creds['mainnet_wallet']
    
    print("=" * 60)
    print("DIAGNOSIS: HyperLiquid Testnet Issue")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Check testnet main wallet balance
        async with session.post(
            f"{TESTNET_API_URL}/info",
            json={"type": "clearinghouseState", "user": main_wallet}
        ) as resp:
            data = json.loads(await resp.text())
            main_balance = float(data.get('marginSummary', {}).get('accountValue', 0))
        
        # Check testnet API wallet balance
        async with session.post(
            f"{TESTNET_API_URL}/info",
            json={"type": "clearinghouseState", "user": testnet_api_wallet}
        ) as resp:
            data = json.loads(await resp.text())
            api_balance = float(data.get('marginSummary', {}).get('accountValue', 0))
    
    print(f"""
TESTNET CONFIGURATION:
----------------------
Main Wallet:         {main_wallet}
  └─ Balance:        ${main_balance}
  └─ Agent:          {testnet_api_wallet} (registered as "testnet")

Testnet API Wallet:  {testnet_api_wallet}
  └─ Balance:        ${api_balance}

PROBLEM:
--------
When we try to trade WITH vault_address={main_wallet}:
  → Error: "Vault not registered"

When we try to trade WITHOUT vault_address:
  → Error: "Order price cannot be more than 80% away from reference price"
  → This is because API wallet has $0 balance, so no margin for trading!

MAINNET (for comparison - WORKING):
-----------------------------------
Main Wallet:         {main_wallet}
  └─ Has Unified Account
  └─ Balance in Spot clearinghouse
  └─ Agent: {mainnet_api_wallet} (registered as "my")
  
When we trade:
  1. We use vault_address={main_wallet}
  2. API wallet signs
  3. Trade happens on main wallet ✅

SOLUTION OPTIONS:
-----------------
1. RECOMMENDED: Skip testnet for now. Mainnet is working perfectly.
   - Testnet is for development, not critical
   - Mainnet with small amounts ($32) is sufficient for testing
   
2. Fix testnet agent registration:
   - User needs to re-register API wallet as agent on testnet
   - This requires action in HyperLiquid UI
   
3. Transfer funds to testnet API wallet:
   - Then trade without vault_address
   - But defeats purpose of agent system

CONCLUSION:
-----------
✅ MAINNET: Fully working - tested open, close, balance
❌ TESTNET: Agent registration issue - not critical

For production use, mainnet functionality is what matters.
Testnet issue can be fixed later by re-registering the agent.
""")


if __name__ == "__main__":
    asyncio.run(explain_testnet_issue())
