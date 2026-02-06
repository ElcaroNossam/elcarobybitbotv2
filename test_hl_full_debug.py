#!/usr/bin/env python3
"""Full HyperLiquid mainnet test with debug info"""
import asyncio
import json
from hyperliquid.client import HyperLiquidClient
from hyperliquid.signer import get_address_from_private_key

async def full_test():
    private_key = "0x211a5a4bfb4d86b3ceeb9081410513cf9502058c7503e8ea7b7126b604714f9e"
    
    print("="*60)
    print("  HYPERLIQUID FULL DEBUG TEST")
    print("="*60)
    
    # Get address from private key
    address = get_address_from_private_key(private_key)
    print(f"\n📍 Address from private key: {address}")
    
    client = HyperLiquidClient(
        private_key=private_key,
        testnet=False
    )
    
    try:
        await client.initialize()
        print(f"📍 Client address: {client.address}")
        
        # 1. Get user state (balance, positions)
        print("\n" + "="*60)
        print("  1. USER STATE (clearinghouseState)")
        print("="*60)
        try:
            state = await client.user_state()
            print(f"Raw response: {json.dumps(state, indent=2)[:1000]}")
            
            # Extract balance info
            margin_summary = state.get("marginSummary", {})
            acct_value = margin_summary.get("accountValue", "0")
            total_margin = margin_summary.get("totalMarginUsed", "0")
            
            print(f"\n💰 Account Value: ${float(acct_value):,.2f}")
            print(f"📊 Margin Used: ${float(total_margin):,.2f}")
            
            # Withdrawable
            withdrawable = state.get("withdrawable", "0")
            print(f"💵 Withdrawable: ${float(withdrawable):,.2f}")
            
        except Exception as e:
            print(f"❌ Error getting user state: {e}")
        
        # 2. Get open orders
        print("\n" + "="*60)
        print("  2. OPEN ORDERS")
        print("="*60)
        try:
            orders = await client.open_orders()
            print(f"Orders count: {len(orders)}")
            for order in orders[:5]:
                print(f"  - {order}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 3. Get meta (assets info)
        print("\n" + "="*60)
        print("  3. META (available assets)")
        print("="*60)
        try:
            meta = await client.meta()
            universe = meta.get("universe", [])
            print(f"Available assets: {len(universe)}")
            # Find HYPE
            for asset in universe:
                if asset.get("name") == "HYPE":
                    print(f"HYPE asset info: {asset}")
                    break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 4. Try to place a small LIMIT order on HYPE
        print("\n" + "="*60)
        print("  4. PLACE LIMIT ORDER (HYPE)")
        print("="*60)
        try:
            # Get current HYPE price
            mid = await client.get_mid_price("HYPE")
            print(f"HYPE mid price: ${mid}")
            
            # Place limit order at -5% from mid (won't execute)
            limit_price = round(mid * 0.95, 2)
            size = 0.1  # Minimum size
            
            print(f"Placing BUY order: {size} HYPE @ ${limit_price}")
            
            result = await client.order(
                coin="HYPE",
                is_buy=True,
                sz=size,
                limit_px=limit_price,
                reduce_only=False,
                order_type={"limit": {"tif": "Gtc"}}
            )
            
            print(f"Order result: {json.dumps(result, indent=2)}")
            
            if result.get("response", {}).get("type") == "order":
                statuses = result.get("response", {}).get("data", {}).get("statuses", [])
                if statuses:
                    status = statuses[0]
                    if "resting" in status:
                        print(f"✅ Order placed! OID: {status['resting']['oid']}")
                    elif "filled" in status:
                        print(f"✅ Order filled!")
                    elif "error" in status:
                        print(f"❌ Order error: {status['error']}")
            else:
                print(f"Response: {result}")
                
        except Exception as e:
            print(f"❌ Error placing order: {e}")
            import traceback
            traceback.print_exc()
        
        # 5. Test leverage
        print("\n" + "="*60)
        print("  5. SET LEVERAGE (HYPE 5x)")
        print("="*60)
        try:
            result = await client.update_leverage("HYPE", leverage=5, is_cross=True)
            print(f"Leverage result: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
    finally:
        await client.close()
    
    print("\n" + "="*60)
    print("  TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(full_test())
