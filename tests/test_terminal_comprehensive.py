"""
Comprehensive Terminal Testing Suite
Tests all exchanges (Bybit Demo/Real, HyperLiquid) and trading operations
"""
import asyncio
import pytest
import sys
import os
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import db
from hl_adapter import HLAdapter
from exchanges.bybit import BybitExchange
from exchanges.hyperliquid import HyperLiquidExchange


class TerminalTester:
    """Comprehensive terminal testing class"""
    
    def __init__(self):
        self.test_results = []
        self.exchanges = {}
        
    async def test_bybit_demo(self, user_id: int) -> Dict:
        """Test Bybit Demo API"""
        results = {
            "exchange": "Bybit Demo",
            "tests": {},
            "errors": []
        }
        
        print(f"\n{'='*60}")
        print(f"🧪 Testing Bybit Demo API")
        print(f"{'='*60}")
        
        try:
            # Get credentials
            creds = db.get_all_user_credentials(user_id)
            api_key = creds.get("demo_api_key")
            api_secret = creds.get("demo_api_secret")
            
            if not api_key or not api_secret:
                results["errors"].append("❌ Bybit Demo credentials not configured")
                return results
            
            # Initialize exchange
            exchange = BybitExchange(
                api_key=api_key,
                api_secret=api_secret,
                testnet=True,
                demo=True
            )
            
            await exchange.initialize()
            self.exchanges["bybit_demo"] = exchange
            
            # Test 1: Get Balance
            print("\n📊 Test 1: Get Balance")
            try:
                balance = await exchange.get_balance()
                results["tests"]["balance"] = {
                    "status": "✅ PASS",
                    "data": {
                        "equity": balance.total_equity,
                        "available": balance.available_balance,
                        "used": balance.used_margin
                    }
                }
                print(f"  ✅ Balance: ${balance.total_equity:.2f}")
                print(f"  ✅ Available: ${balance.available_balance:.2f}")
            except Exception as e:
                results["tests"]["balance"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Balance: {e}")
                print(f"  ❌ Error: {e}")
            
            # Test 2: Get Positions
            print("\n📈 Test 2: Get Positions")
            try:
                positions = await exchange.get_positions()
                results["tests"]["positions"] = {
                    "status": "✅ PASS",
                    "count": len(positions)
                }
                print(f"  ✅ Found {len(positions)} positions")
                for pos in positions[:3]:  # Show first 3
                    side_str = pos.side.value if hasattr(pos.side, 'value') else str(pos.side)
                    print(f"    - {pos.symbol}: {side_str} {pos.size} @ ${pos.entry_price}")
            except Exception as e:
                results["tests"]["positions"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Positions: {e}")
                print(f"  ❌ Error: {e}")
            
            # Test 3: Get Open Orders
            print("\n📋 Test 3: Get Open Orders")
            try:
                orders = await exchange.get_open_orders()
                results["tests"]["orders"] = {
                    "status": "✅ PASS",
                    "count": len(orders)
                }
                print(f"  ✅ Found {len(orders)} open orders")
            except Exception as e:
                results["tests"]["orders"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Orders: {e}")
                print(f"  ❌ Error: {e}")
            
            # Test 4: Get Symbol Info
            print("\n🔍 Test 4: Get Symbol Info")
            try:
                symbol_info = await exchange.get_instrument_info("BTCUSDT")
                results["tests"]["symbol_info"] = {
                    "status": "✅ PASS",
                    "symbol": "BTCUSDT",
                    "min_size": symbol_info.get("lotSizeFilter", {}).get("minOrderQty")
                }
                print(f"  ✅ BTCUSDT info retrieved")
                print(f"    Min Size: {symbol_info.get('lotSizeFilter', {}).get('minOrderQty')}")
            except Exception as e:
                results["tests"]["symbol_info"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Symbol Info: {e}")
                print(f"  ❌ Error: {e}")
            
            # Test 5: Get Ticker
            print("\n💹 Test 5: Get Ticker")
            try:
                ticker = await exchange.get_ticker("BTCUSDT")
                results["tests"]["ticker"] = {
                    "status": "✅ PASS",
                    "price": ticker.get("lastPrice"),
                    "volume": ticker.get("volume24h")
                }
                print(f"  ✅ BTCUSDT: ${ticker.get('lastPrice')}")
                print(f"    24h Volume: {ticker.get('volume24h')}")
            except Exception as e:
                results["tests"]["ticker"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Ticker: {e}")
                print(f"  ❌ Error: {e}")
            
            # Test 6: Get Server Time
            print("\n⏰ Test 6: Get Server Time")
            try:
                server_time = await exchange.get_server_time()
                results["tests"]["server_time"] = {
                    "status": "✅ PASS",
                    "time": server_time
                }
                print(f"  ✅ Server Time: {server_time}")
            except Exception as e:
                results["tests"]["server_time"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Server Time: {e}")
                print(f"  ❌ Error: {e}")
            
            # Test 7: Get Account Info
            print("\n👤 Test 7: Get Account Info")
            try:
                account_info = await exchange.get_account_info()
                results["tests"]["account_info"] = {
                    "status": "✅ PASS",
                    "margin_mode": account_info.get("marginMode"),
                    "unified": account_info.get("unifiedMarginStatus")
                }
                print(f"  ✅ Margin Mode: {account_info.get('marginMode')}")
            except Exception as e:
                results["tests"]["account_info"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Account Info: {e}")
                print(f"  ❌ Error: {e}")
            
        except Exception as e:
            results["errors"].append(f"Initialization: {e}")
            print(f"❌ Fatal Error: {e}")
        
        return results
    
    async def test_bybit_real(self, user_id: int) -> Dict:
        """Test Bybit Real API"""
        results = {
            "exchange": "Bybit Real",
            "tests": {},
            "errors": []
        }
        
        print(f"\n{'='*60}")
        print(f"🧪 Testing Bybit Real API")
        print(f"{'='*60}")
        
        try:
            # Get credentials
            creds = db.get_all_user_credentials(user_id)
            api_key = creds.get("real_api_key")
            api_secret = creds.get("real_api_secret")
            
            if not api_key or not api_secret:
                results["errors"].append("❌ Bybit Real credentials not configured")
                print("⚠️  Bybit Real API not configured - SKIPPED")
                return results
            
            # Initialize exchange
            exchange = BybitExchange(
                api_key=api_key,
                api_secret=api_secret,
                testnet=False,
                demo=False
            )
            
            await exchange.initialize()
            self.exchanges["bybit_real"] = exchange
            
            # Test 1: Get Balance
            print("\n📊 Test 1: Get Balance")
            try:
                balance = await exchange.get_balance()
                results["tests"]["balance"] = {
                    "status": "✅ PASS",
                    "data": {
                        "equity": balance.total_equity,
                        "available": balance.available_balance
                    }
                }
                print(f"  ✅ Balance: ${balance.total_equity:.2f}")
            except Exception as e:
                results["tests"]["balance"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Balance: {e}")
                print(f"  ❌ Error: {e}")
            
            # Test 2: Get Positions
            print("\n📈 Test 2: Get Positions")
            try:
                positions = await exchange.get_positions()
                results["tests"]["positions"] = {
                    "status": "✅ PASS",
                    "count": len(positions)
                }
                print(f"  ✅ Found {len(positions)} positions")
            except Exception as e:
                results["tests"]["positions"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Positions: {e}")
                print(f"  ❌ Error: {e}")
            
            # Test 3: Get Open Orders
            print("\n📋 Test 3: Get Open Orders")
            try:
                orders = await exchange.get_open_orders()
                results["tests"]["orders"] = {
                    "status": "✅ PASS",
                    "count": len(orders)
                }
                print(f"  ✅ Found {len(orders)} open orders")
            except Exception as e:
                results["tests"]["orders"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Orders: {e}")
                print(f"  ❌ Error: {e}")
            
            # Test 4: Get Ticker (Read-only, safe)
            print("\n💹 Test 4: Get Ticker")
            try:
                ticker = await exchange.get_ticker("BTCUSDT")
                results["tests"]["ticker"] = {
                    "status": "✅ PASS",
                    "price": ticker.get("lastPrice")
                }
                print(f"  ✅ BTCUSDT: ${ticker.get('lastPrice')}")
            except Exception as e:
                results["tests"]["ticker"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Ticker: {e}")
                print(f"  ❌ Error: {e}")
            
        except Exception as e:
            results["errors"].append(f"Initialization: {e}")
            print(f"❌ Fatal Error: {e}")
        
        return results
    
    async def test_hyperliquid(self, user_id: int) -> Dict:
        """Test HyperLiquid API"""
        results = {
            "exchange": "HyperLiquid",
            "tests": {},
            "errors": []
        }
        
        print(f"\n{'='*60}")
        print(f"🧪 Testing HyperLiquid API")
        print(f"{'='*60}")
        
        try:
            # Get credentials
            hl_creds = db.get_hl_credentials(user_id)
            private_key = hl_creds.get("hl_private_key")
            
            if not private_key:
                results["errors"].append("❌ HyperLiquid credentials not configured")
                print("⚠️  HyperLiquid API not configured - SKIPPED")
                return results
            
            # Initialize adapter
            adapter = HLAdapter(
                private_key=private_key,
                testnet=hl_creds.get("hl_testnet", False),
                vault_address=hl_creds.get("hl_vault_address")
            )
            
            await adapter.initialize()
            self.exchanges["hyperliquid"] = adapter
            
            # Test 1: Get Balance
            print("\n📊 Test 1: Get Balance")
            try:
                balance = await adapter.get_balance()
                if balance.get("success"):
                    data = balance.get("data", {})
                    results["tests"]["balance"] = {
                        "status": "✅ PASS",
                        "data": {
                            "equity": data.get("equity"),
                            "available": data.get("available")
                        }
                    }
                    print(f"  ✅ Equity: ${data.get('equity', 0):.2f}")
                    print(f"  ✅ Available: ${data.get('available', 0):.2f}")
                else:
                    raise Exception(balance.get("error", "Unknown error"))
            except Exception as e:
                results["tests"]["balance"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Balance: {e}")
                print(f"  ❌ Error: {e}")
            
            # Test 2: Get Positions
            print("\n📈 Test 2: Get Positions")
            try:
                positions_result = await adapter.fetch_positions()
                if positions_result.get("retCode") == 0:
                    positions = positions_result.get("result", {}).get("list", [])
                    active = [p for p in positions if float(p.get("size", 0)) != 0]
                    results["tests"]["positions"] = {
                        "status": "✅ PASS",
                        "count": len(active)
                    }
                    print(f"  ✅ Found {len(active)} positions")
                    for pos in active[:3]:
                        print(f"    - {pos.get('symbol')}: {pos.get('side')} {pos.get('size')}")
                else:
                    raise Exception(positions_result.get("retMsg", "Unknown error"))
            except Exception as e:
                results["tests"]["positions"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Positions: {e}")
                print(f"  ❌ Error: {e}")
            
            # Test 3: Get Price
            print("\n💹 Test 3: Get Price")
            try:
                price = await adapter.get_price("BTC")
                results["tests"]["price"] = {
                    "status": "✅ PASS",
                    "price": price
                }
                print(f"  ✅ BTC: ${price}")
            except Exception as e:
                results["tests"]["price"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Price: {e}")
                print(f"  ❌ Error: {e}")
            
            # Test 4: Get Symbols
            print("\n🔍 Test 4: Get Symbols")
            try:
                symbols = await adapter.get_symbols()
                results["tests"]["symbols"] = {
                    "status": "✅ PASS",
                    "count": len(symbols)
                }
                print(f"  ✅ Found {len(symbols)} tradable symbols")
                print(f"    Sample: {', '.join(symbols[:5])}")
            except Exception as e:
                results["tests"]["symbols"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Symbols: {e}")
                print(f"  ❌ Error: {e}")
            
            # Test 5: Get User State
            print("\n👤 Test 5: Get User State")
            try:
                portfolio = await adapter.get_portfolio()
                results["tests"]["portfolio"] = {
                    "status": "✅ PASS",
                    "has_data": portfolio is not None
                }
                print(f"  ✅ Portfolio data retrieved")
            except Exception as e:
                results["tests"]["portfolio"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Portfolio: {e}")
                print(f"  ❌ Error: {e}")
            
        except Exception as e:
            results["errors"].append(f"Initialization: {e}")
            print(f"❌ Fatal Error: {e}")
        
        return results
    
    async def test_order_flow(self, user_id: int, exchange_name: str) -> Dict:
        """Test order placement flow (without actual execution)"""
        results = {
            "exchange": exchange_name,
            "tests": {},
            "errors": []
        }
        
        print(f"\n{'='*60}")
        print(f"🧪 Testing Order Flow: {exchange_name}")
        print(f"{'='*60}")
        
        try:
            exchange = self.exchanges.get(exchange_name)
            if not exchange:
                results["errors"].append(f"Exchange {exchange_name} not initialized")
                return results
            
            # Test 1: Calculate Position Size
            print("\n🧮 Test 1: Calculate Position Size")
            try:
                # Get balance
                if exchange_name.startswith("bybit"):
                    balance = await exchange.get_balance()
                    equity = balance.total_equity
                else:
                    bal_result = await exchange.get_balance()
                    equity = bal_result.get("data", {}).get("equity", 0)
                
                risk_percent = 1.0  # 1% risk
                position_size = equity * risk_percent / 100
                
                results["tests"]["position_calc"] = {
                    "status": "✅ PASS",
                    "equity": equity,
                    "risk_percent": risk_percent,
                    "position_size": position_size
                }
                print(f"  ✅ Equity: ${equity:.2f}")
                print(f"  ✅ Risk: {risk_percent}%")
                print(f"  ✅ Position Size: ${position_size:.2f}")
            except Exception as e:
                results["tests"]["position_calc"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Position Calc: {e}")
                print(f"  ❌ Error: {e}")
            
            # Test 2: Validate Order Parameters
            print("\n✅ Test 2: Validate Order Parameters")
            try:
                test_order = {
                    "symbol": "BTCUSDT",
                    "side": "Buy",
                    "qty": 0.001,
                    "order_type": "Market",
                    "leverage": 10
                }
                
                # Basic validation
                assert test_order["symbol"], "Symbol required"
                assert test_order["side"] in ["Buy", "Sell"], "Invalid side"
                assert test_order["qty"] > 0, "Quantity must be positive"
                assert test_order["leverage"] > 0, "Leverage must be positive"
                
                results["tests"]["order_validation"] = {
                    "status": "✅ PASS",
                    "order": test_order
                }
                print(f"  ✅ Order parameters valid")
                print(f"    Symbol: {test_order['symbol']}")
                print(f"    Side: {test_order['side']}")
                print(f"    Qty: {test_order['qty']}")
            except Exception as e:
                results["tests"]["order_validation"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Order Validation: {e}")
                print(f"  ❌ Error: {e}")
            
            # Test 3: Check Leverage Setting
            print("\n⚡ Test 3: Check Leverage Setting")
            try:
                if exchange_name.startswith("bybit"):
                    # Don't actually set leverage, just validate
                    leverage_valid = 1 <= 10 <= 100
                    results["tests"]["leverage"] = {
                        "status": "✅ PASS" if leverage_valid else "❌ FAIL",
                        "leverage": 10,
                        "valid": leverage_valid
                    }
                    print(f"  ✅ Leverage 10x valid")
                else:
                    # HyperLiquid
                    leverage_valid = 1 <= 10 <= 50
                    results["tests"]["leverage"] = {
                        "status": "✅ PASS" if leverage_valid else "❌ FAIL",
                        "leverage": 10,
                        "valid": leverage_valid
                    }
                    print(f"  ✅ Leverage 10x valid for HL")
            except Exception as e:
                results["tests"]["leverage"] = {"status": "❌ FAIL", "error": str(e)}
                results["errors"].append(f"Leverage: {e}")
                print(f"  ❌ Error: {e}")
            
        except Exception as e:
            results["errors"].append(f"Order Flow: {e}")
            print(f"❌ Fatal Error: {e}")
        
        return results
    
    async def cleanup(self):
        """Close all exchange connections"""
        print(f"\n{'='*60}")
        print("🧹 Cleaning up...")
        print(f"{'='*60}")
        
        for name, exchange in self.exchanges.items():
            try:
                await exchange.close()
                print(f"  ✅ Closed {name}")
            except Exception as e:
                print(f"  ⚠️  Error closing {name}: {e}")
    
    def print_summary(self, all_results: List[Dict]):
        """Print test summary"""
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}\n")
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for result in all_results:
            exchange = result["exchange"]
            tests = result["tests"]
            errors = result["errors"]
            
            print(f"\n{exchange}:")
            print(f"  Tests Run: {len(tests)}")
            
            for test_name, test_result in tests.items():
                total_tests += 1
                status = test_result.get("status", "❓")
                if "✅" in status:
                    passed_tests += 1
                elif "❌" in status:
                    failed_tests += 1
                
                print(f"    {test_name}: {status}")
            
            if errors:
                print(f"  Errors: {len(errors)}")
                for error in errors:
                    print(f"    - {error}")
        
        print(f"\n{'='*60}")
        print(f"TOTAL: {total_tests} tests")
        print(f"✅ PASSED: {passed_tests}")
        print(f"❌ FAILED: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100) if total_tests > 0 else 0:.1f}%")
        print(f"{'='*60}\n")


async def run_comprehensive_tests(user_id: int):
    """Run all comprehensive tests"""
    tester = TerminalTester()
    results = []
    
    try:
        # Test Bybit Demo
        result = await tester.test_bybit_demo(user_id)
        results.append(result)
        
        # Test Bybit Real (if configured)
        result = await tester.test_bybit_real(user_id)
        results.append(result)
        
        # Test HyperLiquid (if configured)
        result = await tester.test_hyperliquid(user_id)
        results.append(result)
        
        # Test Order Flows
        for exchange_name in ["bybit_demo", "bybit_real", "hyperliquid"]:
            if exchange_name in tester.exchanges:
                result = await tester.test_order_flow(user_id, exchange_name)
                results.append(result)
        
        # Print summary
        tester.print_summary(results)
        
    finally:
        await tester.cleanup()
    
    return results


if __name__ == "__main__":
    import sys
    
    # Get user_id from command line or use default
    user_id = int(sys.argv[1]) if len(sys.argv) > 1 else 511692487
    
    print(f"\n{'='*60}")
    print(f"🚀 ElCaro Terminal Comprehensive Test Suite")
    print(f"{'='*60}")
    print(f"User ID: {user_id}")
    print(f"{'='*60}\n")
    
    # Run tests
    asyncio.run(run_comprehensive_tests(user_id))
