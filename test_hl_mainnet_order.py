#!/usr/bin/env python3
"""Test HyperLiquid mainnet order placement API"""
import asyncio
from hl_adapter import HLAdapter

async def test_order_api():
    private_key = "0x211a5a4bfb4d86b3ceeb9081410513cf9502058c7503e8ea7b7126b604714f9e"
    
    print("=" * 60)
    print("  HYPERLIQUID MAINNET ORDER API TEST")
    print("=" * 60)
    
    adapter = HLAdapter(
        private_key=private_key,
        testnet=False,
        vault_address=None
    )
    
    try:
        await adapter.initialize()
        print(f"\nAddress: {adapter.address}")
        
        # 1. Test placing a LIMIT order
        print("\n--- Testing LIMIT order API (BTC) ---")
        
        result = await adapter.place_order(
            symbol="BTCUSDT",
            side="Buy",
            order_type="Limit",
            qty=0.001,
            price=50000.0,
            reduce_only=False
        )
        
        print(f"Order Result: {result}")
        
        ret_code = result.get("retCode", -1)
        ret_msg = result.get("retMsg", str(result))
        
        if ret_code == 0:
            print("✅ Order API working! Order placed successfully.")
            order_id = result.get("result", {}).get("orderId")
            if order_id:
                print(f"   Order ID: {order_id}")
                # Cancel it
                print("\n--- Cancelling order ---")
                cancel_result = await adapter.cancel_order("BTCUSDT", order_id)
                print(f"Cancel result: {cancel_result}")
        else:
            # Check if it's expected error due to no balance
            if any(x in ret_msg.lower() for x in ["insufficient", "margin", "balance", "not enough"]):
                print(f"✅ Order API working! (Expected error - no balance)")
                print(f"   Message: {ret_msg}")
            else:
                print(f"Order response: {ret_msg}")
        
        # 2. Test leverage setting
        print("\n--- Testing LEVERAGE API ---")
        lev_result = await adapter.set_leverage("BTCUSDT", 10)
        print(f"Leverage result: {lev_result}")
        
        if lev_result.get("retCode") == 0:
            print("✅ Leverage API working!")
        else:
            print(f"Leverage message: {lev_result.get('retMsg', lev_result)}")
        
        print("\n" + "=" * 60)
        print("  TEST COMPLETE")
        print("=" * 60)
        
    finally:
        await adapter.close()

if __name__ == "__main__":
    asyncio.run(test_order_api())
