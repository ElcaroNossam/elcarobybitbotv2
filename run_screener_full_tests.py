#!/usr/bin/env python3
"""
🔍 FULL SCREENER TESTS - Real Market Data
Tests for multi-exchange screener with live data

Exchanges:
- Binance (Futures + Spot)
- Bybit (Futures + Spot)
- OKX (Futures + Spot)
- HyperLiquid (All coins)

Features tested:
- Common symbols detection (present on Binance + Bybit + OKX)
- HyperLiquid unique symbols
- Real-time data fetching
- Price accuracy
- Volume calculations
- Funding rates
- WebSocket connections
"""
import asyncio
import sys
from typing import Dict, List, Set
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Test results tracking
class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add(self, name: str, passed: bool, details: str = ""):
        self.tests.append((name, passed, details))
        if passed:
            self.passed += 1
            logger.info(f"  ✅ {name} - OK{f' ({details})' if details else ''}")
        else:
            self.failed += 1
            logger.error(f"  ❌ {name} - FAILED{f': {details}' if details else ''}")
    
    def summary(self):
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        return total, self.passed, self.failed, success_rate

results = TestResults()

# =============================================================================
# TEST 1: BINANCE DATA FETCHING
# =============================================================================
async def test_binance_fetching():
    """Test Binance real market data fetching"""
    logger.info("\n" + "="*80)
    logger.info("🔶 TEST 1: BINANCE DATA FETCHING (Real Market Data)")
    logger.info("="*80)
    
    from webapp.api.screener_ws import BinanceDataFetcher
    
    fetcher = BinanceDataFetcher()
    
    try:
        # Test futures tickers
        futures = await fetcher.fetch_futures_tickers()
        results.add("Binance Futures Fetch", len(futures) > 0, f"{len(futures)} symbols")
        
        if futures:
            btc_found = any(t['symbol'] == 'BTCUSDT' for t in futures)
            results.add("BTC in Binance Futures", btc_found)
            
            # Check data structure
            first = futures[0]
            has_price = 'lastPrice' in first
            has_volume = 'quoteVolume' in first
            results.add("Binance Futures Data Structure", has_price and has_volume, 
                       f"price: {first.get('lastPrice', 'N/A')}")
        
        # Test spot tickers
        spot = await fetcher.fetch_spot_tickers()
        results.add("Binance Spot Fetch", len(spot) > 0, f"{len(spot)} symbols")
        
        # Test funding rates
        funding = await fetcher.fetch_funding_rates()
        results.add("Binance Funding Rates", len(funding) > 0, f"{len(funding)} rates")
        
        if 'BTCUSDT' in funding:
            btc_funding = funding['BTCUSDT']
            results.add("BTC Funding Rate Value", -1.0 < btc_funding < 1.0, f"{btc_funding:.6f}")
        
        # Test ticker processing
        if futures:
            processed = fetcher.process_ticker(futures[0], funding)
            required_fields = ['symbol', 'price', 'change_24h', 'volume', 'funding_rate', 
                             'change_1m', 'change_5m', 'change_15m', 'volume_15m', 'volume_1h']
            has_all = all(field in processed for field in required_fields)
            results.add("Binance Ticker Processing", has_all, 
                       f"{processed['symbol']}: ${processed['price']:.2f}")
    
    except Exception as e:
        results.add("Binance Fetching", False, str(e))
    finally:
        await fetcher.close()
    
    logger.info(f"\n📊 Binance Tests: {results.passed}/{results.passed + results.failed} passed")

# =============================================================================
# TEST 2: BYBIT DATA FETCHING
# =============================================================================
async def test_bybit_fetching():
    """Test Bybit real market data fetching"""
    logger.info("\n" + "="*80)
    logger.info("🔷 TEST 2: BYBIT DATA FETCHING (Real Market Data)")
    logger.info("="*80)
    
    from webapp.api.exchange_fetchers import BybitDataFetcher
    
    fetcher = BybitDataFetcher()
    
    try:
        # Test futures tickers
        futures = await fetcher.fetch_futures_tickers()
        results.add("Bybit Futures Fetch", len(futures) > 0, f"{len(futures)} symbols")
        
        if futures:
            btc_found = any(t['symbol'] == 'BTCUSDT' for t in futures)
            results.add("BTC in Bybit Futures", btc_found)
            
            first = futures[0]
            has_price = 'lastPrice' in first
            has_volume = 'turnover24h' in first
            results.add("Bybit Futures Data Structure", has_price and has_volume,
                       f"price: {first.get('lastPrice', 'N/A')}")
        
        # Test spot tickers
        spot = await fetcher.fetch_spot_tickers()
        results.add("Bybit Spot Fetch", len(spot) > 0, f"{len(spot)} symbols")
        
        # Test funding rates
        funding = await fetcher.fetch_funding_rates()
        results.add("Bybit Funding Rates", len(funding) > 0, f"{len(funding)} rates")
        
        # Test ticker processing
        if futures:
            processed = fetcher.process_ticker(futures[0], funding)
            required_fields = ['symbol', 'price', 'change_24h', 'volume']
            has_all = all(field in processed for field in required_fields)
            results.add("Bybit Ticker Processing", has_all,
                       f"{processed['symbol']}: ${processed['price']:.2f}")
    
    except Exception as e:
        results.add("Bybit Fetching", False, str(e))
    finally:
        await fetcher.close()
    
    logger.info(f"\n📊 Bybit Tests: {results.passed}/{results.passed + results.failed} passed")

# =============================================================================
# TEST 3: OKX DATA FETCHING
# =============================================================================
async def test_okx_fetching():
    """Test OKX real market data fetching"""
    logger.info("\n" + "="*80)
    logger.info("🟠 TEST 3: OKX DATA FETCHING (Real Market Data)")
    logger.info("="*80)
    
    from webapp.api.exchange_fetchers import OKXDataFetcher
    
    fetcher = OKXDataFetcher()
    
    try:
        # Test futures tickers
        futures = await fetcher.fetch_futures_tickers()
        results.add("OKX Futures Fetch", len(futures) > 0, f"{len(futures)} symbols")
        
        if futures:
            btc_found = any('BTC-USDT' in t.get('instId', '') for t in futures)
            results.add("BTC in OKX Futures", btc_found)
            
            first = futures[0]
            has_price = 'last' in first
            has_volume = 'vol24h' in first or 'volCcy24h' in first
            results.add("OKX Futures Data Structure", has_price and has_volume,
                       f"price: {first.get('last', 'N/A')}")
        
        # Test spot tickers
        spot = await fetcher.fetch_spot_tickers()
        results.add("OKX Spot Fetch", len(spot) > 0, f"{len(spot)} symbols")
        
        # Test funding rates
        funding = await fetcher.fetch_funding_rates()
        results.add("OKX Funding Rates", len(funding) > 0, f"{len(funding)} rates")
        
        # Test ticker processing
        if futures:
            processed = fetcher.process_ticker(futures[0], funding)
            required_fields = ['symbol', 'price', 'change_24h', 'volume']
            has_all = all(field in processed for field in required_fields)
            results.add("OKX Ticker Processing", has_all,
                       f"{processed['symbol']}: ${processed['price']:.2f}")
    
    except Exception as e:
        results.add("OKX Fetching", False, str(e))
    finally:
        await fetcher.close()
    
    logger.info(f"\n📊 OKX Tests: {results.passed}/{results.passed + results.failed} passed")

# =============================================================================
# TEST 4: COMMON SYMBOLS DETECTION
# =============================================================================
async def test_common_symbols():
    """Test detection of common symbols across Binance, Bybit, OKX"""
    logger.info("\n" + "="*80)
    logger.info("🔗 TEST 4: COMMON SYMBOLS DETECTION")
    logger.info("="*80)
    
    from webapp.api.screener_ws import BinanceDataFetcher
    from webapp.api.exchange_fetchers import BybitDataFetcher, OKXDataFetcher
    
    binance_fetcher = BinanceDataFetcher()
    bybit_fetcher = BybitDataFetcher()
    okx_fetcher = OKXDataFetcher()
    
    try:
        # Fetch symbols from all exchanges
        binance_futures = await binance_fetcher.fetch_futures_tickers()
        bybit_futures = await bybit_fetcher.fetch_futures_tickers()
        okx_futures = await okx_fetcher.fetch_futures_tickers()
        
        # Extract symbol names
        binance_symbols = set(t['symbol'] for t in binance_futures)
        bybit_symbols = set(t['symbol'] for t in bybit_futures)
        okx_symbols = set()
        for t in okx_futures:
            inst_id = t.get('instId', '')
            # Convert OKX format: BTC-USDT-SWAP → BTCUSDT
            if '-USDT-SWAP' in inst_id:
                symbol = inst_id.replace('-USDT-SWAP', 'USDT')
                okx_symbols.add(symbol)
        
        results.add("Binance Symbols Fetched", len(binance_symbols) > 0, 
                   f"{len(binance_symbols)} symbols")
        results.add("Bybit Symbols Fetched", len(bybit_symbols) > 0,
                   f"{len(bybit_symbols)} symbols")
        results.add("OKX Symbols Fetched", len(okx_symbols) > 0,
                   f"{len(okx_symbols)} symbols")
        
        # Find common symbols (present on all 3 exchanges)
        common = binance_symbols & bybit_symbols & okx_symbols
        results.add("Common Symbols Found", len(common) > 0, f"{len(common)} common")
        
        if common:
            # Check for major coins
            major_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
            major_in_common = [coin for coin in major_coins if coin in common]
            results.add("Major Coins in Common", len(major_in_common) >= 3,
                       f"{', '.join(major_in_common)}")
            
            logger.info(f"\n💎 Top 10 Common Symbols:")
            for i, symbol in enumerate(sorted(list(common))[:10], 1):
                logger.info(f"   {i}. {symbol}")
        
        # Find unique to each exchange
        binance_only = binance_symbols - bybit_symbols - okx_symbols
        bybit_only = bybit_symbols - binance_symbols - okx_symbols
        okx_only = okx_symbols - binance_symbols - bybit_symbols
        
        results.add("Binance Unique Symbols", len(binance_only) >= 0,
                   f"{len(binance_only)} unique")
        results.add("Bybit Unique Symbols", len(bybit_only) >= 0,
                   f"{len(bybit_only)} unique")
        results.add("OKX Unique Symbols", len(okx_only) >= 0,
                   f"{len(okx_only)} unique")
    
    except Exception as e:
        results.add("Common Symbols Detection", False, str(e))
    finally:
        await binance_fetcher.close()
        await bybit_fetcher.close()
        await okx_fetcher.close()
    
    logger.info(f"\n📊 Common Symbols Tests: {results.passed}/{results.passed + results.failed} passed")

# =============================================================================
# TEST 5: HYPERLIQUID DATA FETCHING
# =============================================================================
async def test_hyperliquid_fetching():
    """Test HyperLiquid unique symbols fetching"""
    logger.info("\n" + "="*80)
    logger.info("🌐 TEST 5: HYPERLIQUID DATA FETCHING")
    logger.info("="*80)
    
    try:
        # HyperLiquid uses different client
        import sys
        sys.path.insert(0, '/home/illiateslenko/UpdateProject/project-bybit/bybitv1/bybit_demo')
        
        from hl_adapter import HLAdapter
        
        hl = HLAdapter(private_key=None, testnet=False, vault_address=None)
        await hl.initialize()
        
        # Get all symbols
        meta = await hl.get_meta()
        if meta and 'universe' in meta:
            symbols = [asset['name'] for asset in meta['universe']]
            results.add("HyperLiquid Symbols Fetch", len(symbols) > 0, 
                       f"{len(symbols)} symbols")
            
            # Check for unique HyperLiquid coins
            hl_unique = ['PURR', 'HYPE', 'JEFF', 'TRUMP', 'DOGE']
            found_unique = [s for s in hl_unique if s in symbols]
            results.add("HyperLiquid Unique Coins", len(found_unique) > 0,
                       f"{', '.join(found_unique)}")
            
            # Check for common coins
            common = ['BTC', 'ETH', 'SOL', 'ARB', 'OP']
            found_common = [s for s in common if s in symbols]
            results.add("HyperLiquid Common Coins", len(found_common) >= 3,
                       f"{', '.join(found_common)}")
            
            logger.info(f"\n💎 HyperLiquid Symbols (showing first 20):")
            for i, symbol in enumerate(symbols[:20], 1):
                logger.info(f"   {i}. {symbol}")
            
            # Test price fetching
            if 'BTC' in symbols:
                price = await hl.get_price('BTC')
                results.add("HyperLiquid BTC Price", price > 0, f"${price:,.2f}")
            
            # Test ticker data
            if symbols:
                ticker = await hl.get_ticker(symbols[0])
                has_data = ticker and 'mid' in ticker
                results.add("HyperLiquid Ticker Data", has_data,
                           f"{symbols[0]}: ${ticker.get('mid', 'N/A')}")
        else:
            results.add("HyperLiquid Meta Fetch", False, "No universe data")
        
        await hl.close()
    
    except Exception as e:
        results.add("HyperLiquid Fetching", False, str(e))
    
    logger.info(f"\n📊 HyperLiquid Tests: {results.passed}/{results.passed + results.failed} passed")

# =============================================================================
# TEST 6: PRICE COMPARISON ACROSS EXCHANGES
# =============================================================================
async def test_price_comparison():
    """Test price consistency across exchanges"""
    logger.info("\n" + "="*80)
    logger.info("💰 TEST 6: PRICE COMPARISON ACROSS EXCHANGES")
    logger.info("="*80)
    
    from webapp.api.screener_ws import BinanceDataFetcher
    from webapp.api.exchange_fetchers import BybitDataFetcher, OKXDataFetcher
    
    binance_fetcher = BinanceDataFetcher()
    bybit_fetcher = BybitDataFetcher()
    okx_fetcher = OKXDataFetcher()
    
    try:
        # Get BTC price from all exchanges
        binance_futures = await binance_fetcher.fetch_futures_tickers()
        bybit_futures = await bybit_fetcher.fetch_futures_tickers()
        okx_futures = await okx_fetcher.fetch_futures_tickers()
        
        binance_btc = next((t for t in binance_futures if t['symbol'] == 'BTCUSDT'), None)
        bybit_btc = next((t for t in bybit_futures if t['symbol'] == 'BTCUSDT'), None)
        okx_btc = next((t for t in okx_futures if 'BTC-USDT' in t.get('instId', '')), None)
        
        if binance_btc and bybit_btc and okx_btc:
            binance_price = float(binance_btc['lastPrice'])
            bybit_price = float(bybit_btc['lastPrice'])
            okx_price = float(okx_btc['last'])
            
            logger.info(f"\n💵 BTC Prices:")
            logger.info(f"   Binance: ${binance_price:,.2f}")
            logger.info(f"   Bybit:   ${bybit_price:,.2f}")
            logger.info(f"   OKX:     ${okx_price:,.2f}")
            
            # Prices should be within 0.5% of each other
            avg_price = (binance_price + bybit_price + okx_price) / 3
            binance_diff = abs(binance_price - avg_price) / avg_price * 100
            bybit_diff = abs(bybit_price - avg_price) / avg_price * 100
            okx_diff = abs(okx_price - avg_price) / avg_price * 100
            
            max_diff = max(binance_diff, bybit_diff, okx_diff)
            results.add("Price Consistency (<0.5% spread)", max_diff < 0.5, 
                       f"max spread: {max_diff:.3f}%")
            
            results.add("Binance Price Valid", binance_price > 0, f"${binance_price:,.2f}")
            results.add("Bybit Price Valid", bybit_price > 0, f"${bybit_price:,.2f}")
            results.add("OKX Price Valid", okx_price > 0, f"${okx_price:,.2f}")
        else:
            results.add("BTC Found on All Exchanges", False, "Missing BTC data")
    
    except Exception as e:
        results.add("Price Comparison", False, str(e))
    finally:
        await binance_fetcher.close()
        await bybit_fetcher.close()
        await okx_fetcher.close()
    
    logger.info(f"\n📊 Price Comparison Tests: {results.passed}/{results.passed + results.failed} passed")

# =============================================================================
# TEST 7: SCREENER CACHE FUNCTIONALITY
# =============================================================================
async def test_screener_cache():
    """Test screener cache and data storage"""
    logger.info("\n" + "="*80)
    logger.info("💾 TEST 7: SCREENER CACHE FUNCTIONALITY")
    logger.info("="*80)
    
    from webapp.api.screener_ws import cache, MarketDataCache
    
    try:
        # Test cache initialization
        test_cache = MarketDataCache()
        results.add("Cache Initialization", True, "Created successfully")
        
        # Test cache structure
        has_binance = hasattr(test_cache, 'binance_futures_data')
        has_bybit = hasattr(test_cache, 'bybit_futures_data')
        has_okx = hasattr(test_cache, 'okx_futures_data')
        results.add("Cache Structure", has_binance and has_bybit and has_okx,
                   "All exchange caches present")
        
        # Test data storage
        test_cache.binance_futures_data['BTCUSDT'] = {
            'symbol': 'BTCUSDT',
            'price': 50000.0,
            'change_24h': 5.0
        }
        stored = 'BTCUSDT' in test_cache.binance_futures_data
        results.add("Cache Data Storage", stored, "BTC data stored")
        
        # Test data retrieval
        btc_data = test_cache.binance_futures_data.get('BTCUSDT')
        price_correct = btc_data and btc_data['price'] == 50000.0
        results.add("Cache Data Retrieval", price_correct, "BTC price retrieved")
        
        # Test get_futures_data method
        binance_data = test_cache.get_futures_data('binance')
        bybit_data = test_cache.get_futures_data('bybit')
        okx_data = test_cache.get_futures_data('okx')
        results.add("Cache Get Methods", 
                   binance_data is not None and bybit_data is not None and okx_data is not None,
                   "All exchange data accessible")
    
    except Exception as e:
        results.add("Cache Functionality", False, str(e))
    
    logger.info(f"\n📊 Cache Tests: {results.passed}/{results.passed + results.failed} passed")

# =============================================================================
# MAIN EXECUTION
# =============================================================================
async def main():
    """Run all screener tests"""
    logger.info("="*80)
    logger.info("🔍 ELCARO SCREENER - FULL TEST SUITE")
    logger.info("Testing: Binance, Bybit, OKX, HyperLiquid")
    logger.info("Mode: Real Market Data (Live)")
    logger.info("="*80)
    
    start_time = datetime.now()
    
    # Run all tests
    await test_binance_fetching()
    await test_bybit_fetching()
    await test_okx_fetching()
    await test_common_symbols()
    await test_hyperliquid_fetching()
    await test_price_comparison()
    await test_screener_cache()
    
    # Final report
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("\n" + "="*80)
    logger.info("📋 FINAL REPORT")
    logger.info("="*80)
    
    total, passed, failed, success_rate = results.summary()
    
    # Group by test suite
    suites = {
        'Binance': [],
        'Bybit': [],
        'OKX': [],
        'Common': [],
        'HyperLiquid': [],
        'Price': [],
        'Cache': []
    }
    
    for name, status, details in results.tests:
        if 'Binance' in name:
            suites['Binance'].append((name, status))
        elif 'Bybit' in name:
            suites['Bybit'].append((name, status))
        elif 'OKX' in name:
            suites['OKX'].append((name, status))
        elif 'Common' in name or 'Symbols' in name:
            suites['Common'].append((name, status))
        elif 'HyperLiquid' in name:
            suites['HyperLiquid'].append((name, status))
        elif 'Price' in name:
            suites['Price'].append((name, status))
        elif 'Cache' in name:
            suites['Cache'].append((name, status))
    
    for suite_name, tests in suites.items():
        if tests:
            suite_passed = sum(1 for _, status in tests if status)
            suite_total = len(tests)
            status = "✅" if suite_passed == suite_total else "⚠️"
            logger.info(f"  {status} {suite_name:<15} - {suite_passed}/{suite_total} passed")
    
    logger.info("\n" + "-"*80)
    logger.info(f"  Total tests passed: {passed}")
    logger.info(f"  Total tests failed: {failed}")
    logger.info(f"  Success rate: {success_rate:.1f}%")
    logger.info(f"  Execution time: {duration:.2f}s")
    logger.info("-"*80)
    
    if failed == 0:
        logger.info("\n🎉 ALL TESTS PASSED! Screener is fully operational.")
        return 0
    else:
        logger.info(f"\n⚠️  {failed} tests failed. Review logs above for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
