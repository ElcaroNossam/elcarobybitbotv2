#!/usr/bin/env python3
"""Test HyperLiquid Spot Order placement on server"""
import asyncio
import db
from hyperliquid.client import HyperLiquidClient

async def test():
    uid = 511692487
    creds = db.get_hl_credentials(uid)
    pk = creds.get("hl_testnet_private_key") or creds.get("hl_private_key")
    
    client = HyperLiquidClient(private_key=pk, testnet=True)
    main = await client.discover_main_wallet()
    
    print("=== HyperLiquid SPOT ORDER Test ===")
    print(f"API Wallet: {client._address}")
    print(f"Main Wallet: {main}")
    
    # Get PURR price
    ticker = await client.get_spot_ticker("PURR")
    mid_px = 4.70  # fallback
    if ticker and ticker.get("midPx"):
        mid_px = float(ticker["midPx"])
    print(f"PURR mid price: {mid_px}")
    
    # 5 PURR @ 70% = ~16.5 USDC (> 10 min)
    test_px = round(mid_px * 0.7, 5)
    sz = 5.0
    
    print(f"\nPlacing BUY order: {sz} PURR @ {test_px} (notional ~{sz * test_px:.2f} USDC)...")
    
    result = await client.spot_order(
        base_token="PURR",
        is_buy=True,
        sz=sz,
        limit_px=test_px,
        order_type={"limit": {"tif": "Gtc"}}
    )
    print(f"Result: {result}")
    
    if result.get("status") == "ok":
        statuses = result.get("response", {}).get("data", {}).get("statuses", [])
        for s in statuses:
            if "resting" in s:
                oid = s["resting"]["oid"]
                print(f"\n*** SUCCESS! SPOT ORDER PLACED! oid={oid}")
                
                # Cancel
                print(f"Cancelling order {oid}...")
                cancel = await client.cancel_order(10000, oid)
                print(f"Cancel result: {cancel}")
                
            elif s.get("error"):
                print(f"\n*** ERROR: {s.get('error')}")
            elif "filled" in s:
                print(f"\n*** Order FILLED: {s['filled']}")
    else:
        print(f"\n*** Request failed: {result}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(test())
