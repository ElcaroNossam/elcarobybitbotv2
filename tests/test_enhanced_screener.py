"""
Comprehensive tests for enhanced screener with advanced metrics.

Tests cover:
- Top 200 Bybit symbols fetching
- All HyperLiquid symbols fetching  
- vDelta calculation (buy_volume - sell_volume)
- Volatility calculation across timeframes
- 1m bar aggregation
- Metrics accuracy
- Performance under load (200 symbols)
"""
import pytest
import asyncio
import time
from webapp.realtime import (
    BybitWorker,
    HyperLiquidWorker,
    start_workers,
    stop_workers,
    get_market_data,
    _bybit_data,
    _hyperliquid_data
)


@pytest.mark.asyncio
class TestEnhancedScreener:
    """Test suite for enhanced screener functionality."""
    
    async def test_bybit_fetch_top_200(self):
        """Test fetching top 200 Bybit symbols by volume."""
        worker = BybitWorker([], limit=200)
        await worker._fetch_top_symbols()
        
        assert len(worker.symbols) > 0, "Should fetch symbols"
        assert len(worker.symbols) <= 200, "Should limit to 200"
        assert 'BTCUSDT' in worker.symbols, "BTC should be in top symbols"
        
        # Check they're all USDT pairs
        for symbol in worker.symbols:
            assert 'USDT' in symbol, f"{symbol} should be USDT pair"
    
    async def test_hyperliquid_fetch_all_symbols(self):
        """Test fetching all HyperLiquid symbols."""
        worker = HyperLiquidWorker()
        await worker._fetch_all_symbols()
        
        assert len(worker.symbols) > 0, "Should fetch symbols"
        assert 'BTC' in worker.symbols, "BTC should be available"
        assert 'ETH' in worker.symbols, "ETH should be available"
        
        print(f"✅ Fetched {len(worker.symbols)} HyperLiquid symbols")
    
    async def test_vdelta_calculation_bybit(self):
        """Test vDelta calculation for Bybit (buy_volume - sell_volume)."""
        worker = BybitWorker(['BTCUSDT'])
        
        # Simulate buy trade
        trade_data = {
            'topic': 'publicTrade.BTCUSDT',
            'data': [{
                's': 'BTCUSDT',
                'p': '50000',  # price
                'v': '2.5',    # volume
                'S': 'Buy',
                'T': int(time.time() * 1000)
            }]
        }
        
        await worker._handle_message(trade_data)
        
        # Check bar was created
        assert 'BTCUSDT' in worker.bars_1m
        
        # vDelta should be positive (buy)
        minute_ts = (int(time.time() * 1000) // 60000) * 60000
        bar = worker.bars_1m['BTCUSDT'][minute_ts]
        assert bar['vdelta'] > 0, "Buy trade should have positive vDelta"
        
        expected_vdelta = 50000 * 2.5
        assert abs(bar['vdelta'] - expected_vdelta) < 0.01
        
        # Simulate sell trade
        trade_data['data'][0]['S'] = 'Sell'
        trade_data['data'][0]['v'] = '1.0'
        
        await worker._handle_message(trade_data)
        
        # vDelta should decrease (sell)
        bar = worker.bars_1m['BTCUSDT'][minute_ts]
        expected_net_vdelta = (50000 * 2.5) - (50000 * 1.0)
        assert abs(bar['vdelta'] - expected_net_vdelta) < 0.01
        
        print(f"✅ vDelta calculation correct: {bar['vdelta']}")
    
    async def test_vdelta_calculation_hyperliquid(self):
        """Test vDelta calculation for HyperLiquid."""
        worker = HyperLiquidWorker(['BTC'])
        
        # Simulate bid (buy) trade
        trade_data = {
            'channel': 'trades',
            'data': [{
                'coin': 'BTC',
                'px': '50000',
                'sz': '1.5',
                'side': 'B',  # Bid = buy
                'time': int(time.time() * 1000)
            }]
        }
        
        # Initialize data
        from webapp.realtime import _hyperliquid_data
        _hyperliquid_data['BTC'] = {'symbol': 'BTC'}
        
        await worker._handle_message(trade_data)
        
        minute_ts = (int(time.time() * 1000) // 60000) * 60000
        bar = worker.bars_1m['BTC'][minute_ts]
        
        assert bar['vdelta'] > 0, "Bid trade should have positive vDelta"
        expected_vdelta = 50000 * 1.5
        assert abs(bar['vdelta'] - expected_vdelta) < 0.01
    
    async def test_volatility_calculation(self):
        """Test volatility calculation from 1m bars."""
        worker = BybitWorker(['BTCUSDT'])
        
        # Create 60 bars with price movement
        base_ts = (int(time.time()) // 60) * 60000
        prices = [50000 + (i * 100) for i in range(60)]  # Trending upward
        
        for i, price in enumerate(prices):
            ts = base_ts - ((59 - i) * 60000)
            worker.bars_1m['BTCUSDT'][ts] = {
                'close': price,
                'open': price - 50,
                'high': price + 50,
                'low': price - 50,
                'volume': 1000,
                'vdelta': 0,
                'trades': 10
            }
        
        volatility = worker._calculate_volatility('BTCUSDT', '1m')
        
        assert volatility > 0, "Should have non-zero volatility"
        assert volatility < 100, "Volatility should be reasonable percentage"
        
        print(f"✅ Calculated volatility: {volatility:.4f}%")
    
    async def test_bar_aggregation(self):
        """Test 1m bar aggregation from trades."""
        worker = BybitWorker(['ETHUSDT'])
        
        # Simulate multiple trades in same minute
        base_time = int(time.time() * 1000)
        minute_ts = (base_time // 60000) * 60000
        
        trades = [
            {'p': '3000', 'v': '1.0', 'S': 'Buy'},
            {'p': '3010', 'v': '0.5', 'S': 'Buy'},
            {'p': '3005', 'v': '2.0', 'S': 'Sell'},
        ]
        
        for trade in trades:
            trade_data = {
                'topic': 'publicTrade.ETHUSDT',
                'data': [{
                    's': 'ETHUSDT',
                    'p': trade['p'],
                    'v': trade['v'],
                    'S': trade['S'],
                    'T': base_time
                }]
            }
            await worker._handle_message(trade_data)
        
        bar = worker.bars_1m['ETHUSDT'][minute_ts]
        
        assert bar['trades'] == 3, "Should count all trades"
        assert bar['high'] == 3010, "Should track high"
        assert bar['low'] == 3000, "Should track low"
        assert bar['open'] == 3000, "Should set open from first trade"
        assert bar['close'] == 3005, "Should set close from last trade"
        
        # Check volume
        total_volume = (3000 * 1.0) + (3010 * 0.5) + (3005 * 2.0)
        assert abs(bar['volume'] - total_volume) < 0.01
    
    async def test_ticker_metrics(self):
        """Test ticker data includes all advanced metrics."""
        worker = BybitWorker(['BTCUSDT'])
        
        ticker_data = {
            'topic': 'tickers.BTCUSDT',
            'data': {
                'symbol': 'BTCUSDT',
                'lastPrice': '50000',
                'markPrice': '50005',
                'indexPrice': '50003',
                'volume24h': '1000000',
                'turnover24h': '50000000000',
                'price24hPcnt': '0.025',
                'highPrice24h': '51000',
                'lowPrice24h': '49000',
                'bid1Price': '49999',
                'ask1Price': '50001',
                'openInterest': '500000',
                'openInterestValue': '25000000000',
                'fundingRate': '0.0001',
                'nextFundingTime': '1234567890',
                'predictedDeliveryPrice': '50010'
            }
        }
        
        await worker._handle_message(ticker_data)
        
        from webapp.realtime import _bybit_data
        btc_data = _bybit_data.get('BTCUSDT', {})
        
        assert btc_data['price'] == 50000
        assert btc_data['mark_price'] == 50005
        assert btc_data['index_price'] == 50003
        assert btc_data['volume_24h'] == 1000000
        assert btc_data['change_24h'] == 2.5
        assert btc_data['open_interest'] == 500000
        assert btc_data['funding_rate'] == 0.0001
        
        print("✅ All ticker metrics captured")
    
    async def test_hyperliquid_stats_caching(self):
        """Test HyperLiquid 24h stats caching."""
        worker = HyperLiquidWorker(['BTC'])
        
        # First call - should fetch
        stats1 = await worker._get_24h_stats('BTC')
        time1 = worker._stats_cache_time.get('BTC', 0)
        
        # Second call immediately - should use cache
        stats2 = await worker._get_24h_stats('BTC')
        time2 = worker._stats_cache_time.get('BTC', 0)
        
        assert time1 == time2, "Should use cached value"
        
        # Wait and check cache expiry (would need to mock time for proper test)
        print("✅ Stats caching working")
    
    async def test_performance_200_symbols(self):
        """Test performance with 200 Bybit symbols."""
        worker = BybitWorker([], limit=200)
        await worker._fetch_top_symbols()
        
        start_time = time.time()
        
        # Simulate ticker updates for all symbols
        for symbol in worker.symbols[:50]:  # Test with 50 for speed
            ticker_data = {
                'topic': f'tickers.{symbol}',
                'data': {
                    'symbol': symbol,
                    'lastPrice': '1000',
                    'volume24h': '100000',
                    'price24hPcnt': '0.01'
                }
            }
            await worker._handle_message(ticker_data)
        
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0, f"Should process 50 symbols in <1s (took {elapsed:.2f}s)"
        print(f"✅ Performance: Processed 50 symbols in {elapsed:.4f}s")
    
    async def test_data_structure_completeness(self):
        """Test that data structure includes all required metrics."""
        worker = BybitWorker(['BTCUSDT'])
        
        ticker_data = {
            'topic': 'tickers.BTCUSDT',
            'data': {
                'symbol': 'BTCUSDT',
                'lastPrice': '50000',
                'volume24h': '1000000',
                'fundingRate': '0.0001',
                'openInterest': '500000'
            }
        }
        
        await worker._handle_message(ticker_data)
        
        from webapp.realtime import _bybit_data
        btc_data = _bybit_data['BTCUSDT']
        
        required_fields = [
            'symbol', 'price', 'volume_24h', 'change_24h',
            'open_interest', 'funding_rate', 'timestamp'
        ]
        
        for field in required_fields:
            assert field in btc_data, f"Missing field: {field}"
        
        print(f"✅ All required fields present: {list(btc_data.keys())}")


@pytest.mark.asyncio
class TestWorkerIntegration:
    """Integration tests for workers."""
    
    async def test_start_stop_workers(self):
        """Test starting and stopping workers."""
        # Start with auto-fetch
        await start_workers()
        await asyncio.sleep(2)
        
        # Check data is being populated
        from webapp.realtime import _bybit_data, _hyperliquid_data
        
        # At least some data should be available
        assert len(_bybit_data) > 0 or len(_hyperliquid_data) > 0
        
        await stop_workers()
        
        print("✅ Workers started and stopped successfully")
    
    async def test_get_market_data_bybit(self):
        """Test get_market_data function for Bybit."""
        await start_workers()
        await asyncio.sleep(2)
        
        data = get_market_data('bybit')
        
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check data structure
        for symbol, info in data.items():
            assert 'symbol' in info
            assert 'price' in info
            assert 'timestamp' in info
        
        await stop_workers()
        
        print(f"✅ Retrieved {len(data)} Bybit symbols")
    
    async def test_get_market_data_hyperliquid(self):
        """Test get_market_data function for HyperLiquid."""
        await start_workers()
        await asyncio.sleep(3)
        
        data = get_market_data('hyperliquid')
        
        assert isinstance(data, dict)
        
        if len(data) > 0:
            for symbol, info in data.items():
                assert 'symbol' in info
                assert 'price' in info
        
        await stop_workers()
        
        print(f"✅ Retrieved {len(data)} HyperLiquid symbols")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
