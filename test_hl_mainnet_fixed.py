#!/usr/bin/env python3
"""
Test HyperLiquid mainnet with fixed signing - matching official SDK
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hyperliquid.client import HyperLiquidClient
from hyperliquid.signer import get_address_from_private_key

# Mainnet private key
MAINNET_KEY = "0x211a5a4bfb4d86b3ceeb9081410513cf9502058c7503e8ea7b7126b604714f9e"


async def test_mainnet():
    """Test mainnet trading with fixed signing."""
    
    print("=" * 60)
    print("HyperLiquid Mainnet Test - Fixed Signing")
    print("=" * 60)
    
    # 1. Get address
    address = get_address_from_private_key(MAINNET_KEY)
    print(f"\n✅ Address from key: {address}")
    
    # 2. Create client
    client = HyperLiquidClient(
        private_key=MAINNET_KEY,
        testnet=False  # MAINNET
    )
    
    try:
        await client.initialize()
        print("✅ Client initialized")
        
        # 3. Check user state
        print("\n--- USER STATE ---")
        state = await client.user_state()
        margin_summary = state.get("marginSummary", {})
        account_value = float(margin_summary.get("accountValue", 0))
        withdrawable = float(state.get("withdrawable", 0))
        
        print(f"  Account Value: ${account_value:.2f}")
        print(f"  Withdrawable: ${withdrawable:.2f}")
        
        positions = state.get("assetPositions", [])
        print(f"  Open Positions: {len(positions)}")
        
        await asyncio.sleep(1)  # Rate limit protection
        
        # If no balance, remind about Perps transfer
        if account_value == 0:
            print("\n⚠️  ВАЖНО: Баланс = $0!")
            print("   Деньги должны быть на Perps, не на Spot!")
            print("   Перейдите на https://app.hyperliquid.xyz")
            print("   Portfolio → Transfer to Perps")
            
            # Still try to place order to see exact error
            print("\n--- TEST ORDER ANYWAY ---")
        
        # 4. Get prices
        print("\n--- PRICES ---")
        mids = await client.get_all_mids()
        eth_price = mids.get("ETH")
        btc_price = mids.get("BTC")
        hype_price = mids.get("HYPE")
        
        print(f"  ETH: ${eth_price}")
        print(f"  BTC: ${btc_price}")
        print(f"  HYPE: ${hype_price}")
        
        await asyncio.sleep(1)  # Rate limit protection
        
        # 5. Try leverage first
        print("\n--- SET LEVERAGE (ETH 5x) ---")
        try:
            lev_result = await client.update_leverage("ETH", 5, is_cross=True)
            print(f"  Result: {lev_result}")
        except Exception as e:
            print(f"  Error: {e}")
        
        await asyncio.sleep(1)  # Rate limit protection
        
        # 6. Try to place a small order
        print("\n--- PLACE TEST ORDER ---")
        if eth_price:
            # Far limit order that won't fill - ETH is more reliable
            # Tick size for ETH is 0.1, so round to 1 decimal
            limit_price = round(eth_price * 0.8, 1)  # 20% below market, tick size = 0.1
            size = 0.01  # Minimum ETH size
            print(f"  ETH limit BUY: {size} @ ${limit_price}")
            
            try:
                order_result = await client.order(
                    coin="ETH",
                    is_buy=True,
                    sz=size,
                    limit_px=limit_price,
                    order_type={"limit": {"tif": "Gtc"}}
                )
                print(f"  Order result: {order_result}")
                
                # Check status
                status = order_result.get("response", {}).get("data", {}).get("statuses", [])
                if status:
                    stat = status[0]
                    if "resting" in stat:
                        oid = stat["resting"]["oid"]
                        print(f"  ✅ Order placed! OID: {oid}")
                    elif "error" in stat:
                        print(f"  ❌ Error: {stat['error']}")
                    else:
                        print(f"  Status: {stat}")
                    
            except Exception as e:
                print(f"  Order error: {e}")
        
        # 7. Check open orders
        print("\n--- OPEN ORDERS ---")
        await asyncio.sleep(1)
        try:
            orders = await client.open_orders()
            print(f"  Count: {len(orders)}")
            for o in orders[:3]:
                print(f"    {o.get('coin')} {o.get('side')} {o.get('sz')} @ {o.get('limitPx')}")
            
            # If order was placed but not in open orders, it was probably cancelled
            # due to insufficient margin
            if len(orders) == 0:
                print("  Note: Order was placed but not visible - likely cancelled")
                print("        due to insufficient margin ($0 balance)")
        except Exception as e:
            print(f"  Error: {e}")
        
        # 8. Check fills/trades
        print("\n--- RECENT FILLS ---")
        await asyncio.sleep(1)
        try:
            fills = await client.user_fills()
            print(f"  Count: {len(fills)}")
            for f in fills[:3]:
                print(f"    {f.get('coin')} {f.get('side')} {f.get('sz')} @ {f.get('px')}")
        except Exception as e:
            print(f"  Error: {e}")
        
        print("\n" + "=" * 60)
        print("Test completed!")
        
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_mainnet())
