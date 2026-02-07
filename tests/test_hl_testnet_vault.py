#!/usr/bin/env python3
"""
Test HyperLiquid testnet WITH vault_address (main wallet).
The API wallet signs, but trades on behalf of main wallet.
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
        "testnet_wallet": row[1],  # This is the MAIN wallet
        "mainnet_key": row[2],
        "mainnet_wallet": row[3],
    }


async def test_with_vault():
    """Test with vault_address = main wallet."""
    from hyperliquid.client import HyperLiquidClient, round_price
    from hyperliquid.signer import (
        sign_l1_action, order_request_to_order_wire, order_wire_to_action,
        get_timestamp_ms, get_address_from_private_key
    )
    from hyperliquid.constants import coin_to_asset_id, TESTNET_API_URL
    import aiohttp
    
    user_id = 511692487
    creds = get_hl_credentials(user_id)
    
    if not creds:
        print("No credentials found!")
        return
    
    print("=== TESTNET WITH VAULT_ADDRESS ===")
    
    api_wallet = get_address_from_private_key(creds['testnet_key'])
    main_wallet = creds['testnet_wallet']  # Main wallet where funds are
    
    print(f"API Wallet (signs): {api_wallet}")
    print(f"Main Wallet (funds): {main_wallet}")
    
    # Create client
    client = HyperLiquidClient(
        private_key=creds['testnet_key'],
        testnet=True,
        vault_address=main_wallet  # Trade on behalf of main wallet!
    )
    
    try:
        await client.initialize()
        
        # Check balance on MAIN wallet
        state = await client.user_state(address=main_wallet)
        print(f"\nMain wallet balance: ${state.get('marginSummary', {}).get('accountValue', 0)}")
        
        # Get price
        mids = await client.get_all_mids()
        mid = float(mids.get('ETH', 2000))
        print(f"Mid price: {mid}")
        
        # Build order
        coin = "ETH"
        is_buy = True
        sz = 0.01
        slippage = 0.01
        
        limit_px = mid * (1 + slippage)
        limit_px = round_price(limit_px, coin)
        
        print(f"Order: BUY {sz} {coin} @ {limit_px}")
        
        asset = coin_to_asset_id(coin)
        
        order_req = {
            "coin": coin,
            "is_buy": is_buy,
            "sz": sz,
            "limit_px": limit_px,
            "reduce_only": False,
            "order_type": {"limit": {"tif": "Ioc"}}
        }
        
        order_wire = order_request_to_order_wire(order_req, asset)
        action = order_wire_to_action([order_wire], grouping="na")
        nonce = get_timestamp_ms()
        
        # Sign with vault_address = main_wallet!
        signed_payload = sign_l1_action(
            creds['testnet_key'],
            action,
            vault_address=main_wallet,  # THIS IS THE KEY DIFFERENCE!
            nonce=nonce,
            is_mainnet=False
        )
        
        print(f"\nPayload has vaultAddress: {signed_payload.get('vaultAddress')}")
        
        # Send
        print("\n=== Sending request... ===")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{TESTNET_API_URL}/exchange",
                json=signed_payload,
                headers={"Content-Type": "application/json"}
            ) as resp:
                text = await resp.text()
                print(f"Status: {resp.status}")
                print(f"Response: {text}")
                
                # Parse response
                try:
                    data = json.loads(text)
                    if data.get("status") == "ok":
                        statuses = data.get("response", {}).get("data", {}).get("statuses", [])
                        for st in statuses:
                            if "filled" in st:
                                print(f"\n✅ FILLED: {st['filled']}")
                            elif "error" in st:
                                print(f"\n❌ Error: {st['error']}")
                            elif "resting" in st:
                                print(f"\n⏳ Resting: {st['resting']}")
                except:
                    pass
        
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_with_vault())
