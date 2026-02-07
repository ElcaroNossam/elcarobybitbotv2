#!/usr/bin/env python3
"""
Debug HyperLiquid testnet order issue.
Check what exactly is being sent to the API.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hyperliquid.client import HyperLiquidClient, round_price
from hyperliquid.constants import get_size_decimals
import json


async def debug_testnet():
    """Debug testnet order placement."""
    
    # This would need the real testnet key from production
    # For now, let's check what the API returns for ETH
    
    # Create read-only client
    client = HyperLiquidClient(
        wallet_address="0xF38498bFec6DCD4A27809e5d70A8989Df73d0C6c",
        testnet=True
    )
    
    try:
        await client.initialize()
        
        # Get meta info for ETH
        meta = await client.meta()
        print("\n=== ETH Meta Info ===")
        
        eth_info = None
        for universe in meta.get("universe", []):
            if universe.get("name") == "ETH":
                eth_info = universe
                break
        
        if eth_info:
            print(json.dumps(eth_info, indent=2))
        else:
            print("ETH not found in universe")
        
        # Check all mids
        mids = await client.get_all_mids()
        print(f"\n=== Mid Price ===")
        print(f"ETH mid: {mids.get('ETH')}")
        
        # Get user state
        state = await client.user_state()
        print(f"\n=== User State (Perp) ===")
        print(f"Margin Summary: {json.dumps(state.get('marginSummary', {}), indent=2)}")
        print(f"Positions: {json.dumps(state.get('assetPositions', []), indent=2)}")
        
        # Check spot state
        spot = await client.spot_state()
        print(f"\n=== Spot State ===")
        print(f"Balances: {json.dumps(spot.get('balances', []), indent=2)}")
        
        # Check price rounding
        mid = float(mids.get('ETH', 2000))
        sz_decimals = get_size_decimals("ETH")
        print(f"\n=== Price Rounding Check ===")
        print(f"Mid price: {mid}")
        print(f"Size decimals: {sz_decimals}")
        print(f"Max price decimals: {6 - sz_decimals}")
        
        # Test various prices
        test_prices = [
            mid * 1.01,  # +1%
            mid * 0.99,  # -1%
            mid * 1.05,  # +5%
            mid * 0.95,  # -5%
            mid * 1.001, # +0.1%
            mid * 0.999, # -0.1%
        ]
        
        for px in test_prices:
            rounded = round_price(px, "ETH")
            pct = (px / mid - 1) * 100
            print(f"  {px:.4f} ({pct:+.2f}%) -> {rounded}")
        
        # Check L2 book for reference prices
        print(f"\n=== L2 Book ===")
        l2 = await client.l2_snapshot("ETH")
        if l2.get("levels"):
            bids = l2["levels"][0][:3] if len(l2["levels"]) > 0 else []
            asks = l2["levels"][1][:3] if len(l2["levels"]) > 1 else []
            print(f"Best bids: {bids}")
            print(f"Best asks: {asks}")
            
            if bids and asks:
                best_bid = float(bids[0]["px"])
                best_ask = float(asks[0]["px"])
                print(f"\nBest bid: {best_bid}")
                print(f"Best ask: {best_ask}")
                print(f"Spread: {best_ask - best_bid:.2f} ({(best_ask / best_bid - 1) * 100:.4f}%)")
                
                # Check if 80% rule applies
                ref_price = (best_bid + best_ask) / 2
                print(f"\nReference price: {ref_price:.2f}")
                print(f"80% above: {ref_price * 1.8:.2f}")
                print(f"80% below: {ref_price * 0.2:.2f}")
                
                # Typical order prices
                buy_px = round_price(best_ask * 1.01, "ETH")
                sell_px = round_price(best_bid * 0.99, "ETH")
                print(f"\nTypical buy price (+1% slippage): {buy_px}")
                print(f"Typical sell price (-1% slippage): {sell_px}")
                
                # Check if these are within 80% rule
                buy_pct_from_ref = abs(buy_px / ref_price - 1) * 100
                sell_pct_from_ref = abs(sell_px / ref_price - 1) * 100
                print(f"\nBuy price is {buy_pct_from_ref:.2f}% from reference (limit 80%)")
                print(f"Sell price is {sell_pct_from_ref:.2f}% from reference (limit 80%)")
        
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(debug_testnet())
