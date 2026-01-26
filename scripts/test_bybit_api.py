#!/usr/bin/env python3
"""
Test script for Bybit API v5 endpoints
Tests all major endpoints against the demo account
"""
import asyncio
import sys
sys.path.insert(0, "/home/ubuntu/project/elcarobybitbotv2")

from exchanges.bybit import BybitExchange
import db

async def run_tests():
    uid = 511692487
    
    # Get credentials - returns tuple (api_key, api_secret)
    api_key, api_secret = db.get_user_credentials(uid, account_type="demo")
    if not api_key or not api_secret:
        print("ERROR: No credentials found")
        return False
    
    exchange = BybitExchange(
        api_key=api_key,
        api_secret=api_secret,
        testnet=True
    )
    
    tests_passed = 0
    tests_total = 8
    
    try:
        await exchange.initialize()
        print("=" * 60)
        print("BYBIT API v5 ENDPOINT TESTS")
        print("=" * 60)
        
        # Test 1: Balance
        print("\n[1/8] GET Balance (/v5/account/wallet-balance)...")
        try:
            balance = await exchange.get_balance()
            print(f"      Total Equity: {balance.total_equity:.2f} USDT")
            print(f"      Available: {balance.available_balance:.2f} USDT")
            print(f"      Margin Used: {balance.margin_used:.2f} USDT")
            print("      PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"      FAILED: {e}")
        
        # Test 2: Positions
        print("\n[2/8] GET Positions (/v5/position/list)...")
        try:
            positions = await exchange.get_positions()
            print(f"      Open positions: {len(positions)}")
            print("      PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"      FAILED: {e}")
        
        # Test 3: Open Orders
        print("\n[3/8] GET Open Orders (/v5/order/realtime)...")
        try:
            orders = await exchange.get_open_orders()
            print(f"      Open orders: {len(orders)}")
            print("      PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"      FAILED: {e}")
        
        # Test 4: Account Info
        print("\n[4/8] GET Account Info (/v5/account/info)...")
        try:
            info = await exchange._request("GET", "/v5/account/info")
            if info:
                margin_mode = info.get("marginMode", "UNKNOWN")
                unified_status = info.get("unifiedMarginStatus", "UNKNOWN")
                print(f"      Margin Mode: {margin_mode}")
                print(f"      Unified Status: {unified_status}")
            print("      PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"      FAILED: {e}")
        
        # Test 5: Order History
        print("\n[5/8] GET Order History (/v5/order/history)...")
        try:
            history = await exchange.get_order_history(limit=5)
            print(f"      Orders in history: {len(history)}")
            print("      PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"      FAILED: {e}")
        
        # Test 6: Trade History (Execution List)
        print("\n[6/8] GET Trade History (/v5/execution/list)...")
        try:
            trades = await exchange.get_trade_history(limit=5)
            print(f"      Trades in history: {len(trades)}")
            print("      PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"      FAILED: {e}")
        
        # Test 7: Set Margin Mode (account-level)
        print("\n[7/8] SET Margin Mode (/v5/account/set-margin-mode)...")
        try:
            success = await exchange.set_margin_mode("ISOLATED_MARGIN")
            if success:
                print("      Successfully set to ISOLATED_MARGIN")
                print("      PASSED")
                tests_passed += 1
            else:
                print("      FAILED: set_margin_mode returned False")
        except Exception as e:
            print(f"      FAILED: {e}")
        
        # Test 8: Get Price
        print("\n[8/8] GET Price (/v5/market/tickers)...")
        try:
            price = await exchange.get_price("BTCUSDT")
            if price:
                print(f"      BTC Price: ${price:,.2f}")
                print("      PASSED")
                tests_passed += 1
            else:
                print("      FAILED: No price returned")
        except Exception as e:
            print(f"      FAILED: {e}")
        
        print("\n" + "=" * 60)
        print(f"RESULTS: {tests_passed}/{tests_total} tests passed")
        if tests_passed == tests_total:
            print("ALL TESTS PASSED!")
        else:
            print(f"SOME TESTS FAILED ({tests_total - tests_passed} failures)")
        print("=" * 60)
        
        return tests_passed == tests_total
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await exchange.close()


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
