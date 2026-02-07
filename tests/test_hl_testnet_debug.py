#!/usr/bin/env python3
"""
Full debug of HyperLiquid testnet order issue.
Execute on production server with real credentials.
"""
import asyncio
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add psycopg2 for database access
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


async def debug_testnet_order():
    """Debug testnet order with full request logging."""
    from hyperliquid.client import HyperLiquidClient, round_price
    from hyperliquid.signer import (
        sign_l1_action, order_request_to_order_wire, order_wire_to_action,
        get_timestamp_ms, get_address_from_private_key
    )
    from hyperliquid.constants import coin_to_asset_id
    
    user_id = 511692487
    creds = get_hl_credentials(user_id)
    
    if not creds:
        print("No credentials found!")
        return
    
    print("=== TESTNET DEBUG ===")
    print(f"\nTestnet Key: {creds['testnet_key'][:10]}...")
    print(f"Testnet Wallet: {creds['testnet_wallet']}")
    
    # Get API wallet address from key
    api_wallet = get_address_from_private_key(creds['testnet_key'])
    print(f"API Wallet (from key): {api_wallet}")
    
    # Create client
    client = HyperLiquidClient(
        private_key=creds['testnet_key'],
        testnet=True
    )
    
    try:
        await client.initialize()
        
        # Get price
        mids = await client.get_all_mids()
        mid = float(mids.get('ETH', 2000))
        print(f"\nMid price: {mid}")
        
        # Build order manually to see exact request
        coin = "ETH"
        is_buy = True
        sz = 0.01
        slippage = 0.01
        
        limit_px = mid * (1 + slippage)
        limit_px = round_price(limit_px, coin)
        
        print(f"Order: BUY {sz} {coin} @ {limit_px}")
        
        asset = coin_to_asset_id(coin)
        print(f"Asset ID: {asset}")
        
        order_req = {
            "coin": coin,
            "is_buy": is_buy,
            "sz": sz,
            "limit_px": limit_px,
            "reduce_only": False,
            "order_type": {"limit": {"tif": "Ioc"}}
        }
        
        order_wire = order_request_to_order_wire(order_req, asset)
        print(f"\nOrder wire: {json.dumps(order_wire, indent=2)}")
        
        action = order_wire_to_action([order_wire], grouping="na")
        print(f"\nAction: {json.dumps(action, indent=2)}")
        
        nonce = get_timestamp_ms()
        print(f"\nNonce: {nonce}")
        
        # Sign the action - no vault_address since we're trading on API wallet
        signed_payload = sign_l1_action(
            creds['testnet_key'],
            action,
            vault_address=None,  # No vault - trading directly
            nonce=nonce,
            is_mainnet=False  # TESTNET
        )
        
        print(f"\nSigned payload (without full signature):")
        payload_for_print = {k: v for k, v in signed_payload.items() if k != 'signature'}
        payload_for_print['signature'] = '...'
        print(json.dumps(payload_for_print, indent=2))
        
        # Send the request
        print("\n=== Sending request... ===")
        
        import aiohttp
        from hyperliquid.constants import TESTNET_API_URL
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{TESTNET_API_URL}/exchange",
                json=signed_payload,
                headers={"Content-Type": "application/json"}
            ) as resp:
                text = await resp.text()
                print(f"Status: {resp.status}")
                print(f"Response: {text}")
        
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(debug_testnet_order())
