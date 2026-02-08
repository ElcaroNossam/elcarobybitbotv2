#!/usr/bin/env python3
"""
Test HyperLiquid Spot Order placement through Agent wallet.

Tests:
1. Spot balance check (from main wallet)
2. Spot limit order placement (very low price, should rest)
3. Order cancel
"""

import asyncio
import sys
sys.path.insert(0, '/Users/elcarosam/project/elcarobybitbotv2')

from hyperliquid.client import HyperLiquidClient

# Testnet credentials
TESTNET_PRIVATE_KEY = "0x13371337133713371337133713371337133713371337133713371337deadc0de"
TESTNET_API_WALLET = "0x5a1928289D14c9AF8D1c5557B8756E552b6D67ec"
TESTNET_MAIN_WALLET = "0xf38498bfec6dcd4a27809e5d70a8989df73d0c6c"


async def test_spot_order():
    print("=" * 60)
    print("HyperLiquid Spot Order Test (Agent Wallet)")
    print("=" * 60)
    
    # Initialize client
    print("\n1. Initializing client...")
    client = HyperLiquidClient(
        private_key=TESTNET_PRIVATE_KEY,
        testnet=True
    )
    
    # Discover main wallet
    print("\n2. Discovering main wallet...")
    main_wallet = await client.discover_main_wallet()
    print(f"   API Wallet: {client._address}")
    print(f"   Main Wallet: {main_wallet}")
    print(f"   Vault Address: {client._vault_address}")  # Should be None for agents
    
    # Check spot balance
    print("\n3. Getting spot balance (from MAIN wallet)...")
    try:
        spot_state = await client.spot_state(address=main_wallet)
        balances = spot_state.get("balances", [])
        print(f"   Spot balances on {main_wallet}:")
        for bal in balances:
            coin = bal.get("coin", "?")
            total = bal.get("total", "0")
            hold = bal.get("hold", "0")
            print(f"     {coin}: {total} (hold: {hold})")
    except Exception as e:
        print(f"   Error getting spot balance: {e}")
        return
    
    # Get available spot pairs
    print("\n4. Getting spot pairs...")
    try:
        spot_data = await client.spot_meta_and_asset_contexts()
        spot_meta = spot_data[0]
        spot_ctxs = spot_data[1]
        universe = spot_meta.get("universe", [])
        tokens = spot_meta.get("tokens", [])
        
        print(f"   Found {len(universe)} spot pairs:")
        for idx, pair in enumerate(universe):
            token_indices = pair.get("tokens", [])
            if len(token_indices) >= 2:
                base_idx = token_indices[0]
                quote_idx = token_indices[1]
                base_name = tokens[base_idx].get("name") if base_idx < len(tokens) else "?"
                quote_name = tokens[quote_idx].get("name") if quote_idx < len(tokens) else "?"
                
                mid_px = spot_ctxs[idx].get("midPx", "?") if idx < len(spot_ctxs) else "?"
                print(f"     @{idx}: {base_name}/{quote_name} - Mid: {mid_px}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Try to place a LIMIT order for PURR at very low price (should rest, not execute)
    print("\n5. Placing LIMIT order: BUY 1 PURR @ 0.000001 (should rest)...")
    try:
        result = await client.spot_order(
            base_token="PURR",
            is_buy=True,
            sz=1.0,
            limit_px=0.000001,  # Very low price - order should rest
            order_type={"limit": {"tif": "Gtc"}}
        )
        print(f"   Result: {result}")
        
        if result.get("status") == "ok":
            statuses = result.get("response", {}).get("data", {}).get("statuses", [])
            for status in statuses:
                if "resting" in status:
                    oid = status["resting"]["oid"]
                    print(f"   SUCCESS! Order resting with oid={oid}")
                    
                    # Cancel the order
                    print(f"\n6. Canceling order {oid}...")
                    cancel_result = await client.cancel_order(10000, oid)  # 10000 = PURR spot asset ID
                    print(f"   Cancel result: {cancel_result}")
                elif "error" in status:
                    print(f"   ERROR: {status['error']}")
        else:
            print(f"   Order failed: {result}")
    except Exception as e:
        print(f"   Error placing order: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_spot_order())
