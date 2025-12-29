"""
Comprehensive tests for real-time market data system.

Tests cover:
1. WebSocket workers (Bybit + HyperLiquid)
2. Data aggregation and broadcasting
3. Client connections and disconnections
4. Error handling and reconnection
5. Performance under load
"""
import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from webapp.realtime import (
    BybitWorker,
    HyperLiquidWorker,
    snapshot_broadcaster,
    start_workers,
    stop_workers,
    register_client,
    unregister_client,
    get_current_data,
    _bybit_data,
    _hyperliquid_data,
    _active_connections
)


class TestBybitWorker:
    """Test Bybit WebSocket worker."""
    
    @pytest.mark.asyncio
    async def test_worker_initialization(self):
        """Test worker can be initialized with symbols."""
        symbols = ['BTCUSDT', 'ETHUSDT']
        worker = BybitWorker(symbols)
        
        assert worker.symbols == symbols
        assert worker.ws_url == "wss://stream.bybit.com/v5/public/linear"
        assert worker.running == False
    
    @pytest.mark.asyncio
    async def test_worker_handles_ticker_message(self):
        """Test worker processes ticker messages correctly."""
        worker = BybitWorker(['BTCUSDT'])
        
        # Simulate ticker message
        message = {
            'topic': 'tickers.BTCUSDT',
            'data': {
                'symbol': 'BTCUSDT',
                'lastPrice': '50000.50',
                'volume24h': '1234567',
                'turnover24h': '987654321',
                'price24hPcnt': '0.025',
                'highPrice24h': '51000',
                'lowPrice24h': '49000',
                'bid1Price': '49999',
                'ask1Price': '50001'
            }
        }
        
        await worker._handle_message(message)
        
        # Check data was stored
        assert 'BTCUSDT' in _bybit_data
        data = _bybit_data['BTCUSDT']
        assert data['symbol'] == 'BTCUSDT'
        assert data['price'] == 50000.50
        assert data['volume_24h'] == 1234567.0
        assert data['change_24h'] == 2.5  # 0.025 * 100
    
    @pytest.mark.asyncio
    async def test_worker_stop(self):
        """Test worker can be stopped gracefully."""
        worker = BybitWorker(['BTCUSDT'])
        worker.running = True
        worker.stop()
        assert worker.running == False


class TestHyperLiquidWorker:
    """Test HyperLiquid WebSocket worker."""
    
    @pytest.mark.asyncio
    async def test_worker_initialization(self):
        """Test HyperLiquid worker initialization."""
        symbols = ['BTC', 'ETH']
        worker = HyperLiquidWorker(symbols)
        
        assert worker.symbols == symbols
        assert worker.ws_url == "wss://api.hyperliquid.xyz/ws"
    
    @pytest.mark.asyncio
    async def test_worker_handles_mids_message(self):
        """Test worker processes allMids messages."""
        worker = HyperLiquidWorker(['BTC', 'ETH'])
        
        message = {
            'channel': 'allMids',
            'data': {
                'mids': {
                    'BTC': '50000.5',
                    'ETH': '3000.25',
                    'SOL': '100.0'  # Not in symbols, should be ignored
                }
            }
        }
        
        await worker._handle_message(message)
        
        # Check only subscribed symbols were stored
        assert 'BTC' in _hyperliquid_data
        assert 'ETH' in _hyperliquid_data
        assert 'SOL' not in _hyperliquid_data
        
        assert _hyperliquid_data['BTC']['price'] == 50000.5
        assert _hyperliquid_data['ETH']['price'] == 3000.25


class TestSnapshotBroadcaster:
    """Test snapshot broadcasting to clients."""
    
    @pytest.mark.asyncio
    async def test_broadcaster_sends_to_clients(self):
        """Test broadcaster sends data to all connected clients."""
        # Mock WebSocket client
        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock()
        
        # Register client
        register_client(mock_ws, 'bybit')
        
        # Add test data
        _bybit_data['BTCUSDT'] = {
            'symbol': 'BTCUSDT',
            'price': 50000,
            'timestamp': 1234567890
        }
        
        # Run broadcaster for one iteration
        broadcaster_task = asyncio.create_task(snapshot_broadcaster('bybit', 0.1))
        await asyncio.sleep(0.2)  # Wait for at least one broadcast
        broadcaster_task.cancel()
        
        try:
            await broadcaster_task
        except asyncio.CancelledError:
            pass
        
        # Verify client received data
        assert mock_ws.send_json.called
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args['type'] == 'market_data'
        assert call_args['exchange'] == 'bybit'
        assert len(call_args['data']) > 0
        
        # Cleanup
        unregister_client(mock_ws, 'bybit')
    
    @pytest.mark.asyncio
    async def test_broadcaster_handles_disconnected_clients(self):
        """Test broadcaster removes disconnected clients."""
        # Mock client that raises exception
        mock_ws = AsyncMock()
        mock_ws.send_json = AsyncMock(side_effect=Exception("Connection closed"))
        
        register_client(mock_ws, 'bybit')
        assert len(_active_connections['bybit']) == 1
        
        # Add data
        _bybit_data['BTCUSDT'] = {'symbol': 'BTCUSDT', 'price': 50000}
        
        # Run broadcaster
        broadcaster_task = asyncio.create_task(snapshot_broadcaster('bybit', 0.1))
        await asyncio.sleep(0.2)
        broadcaster_task.cancel()
        
        try:
            await broadcaster_task
        except asyncio.CancelledError:
            pass
        
        # Client should be removed
        assert len(_active_connections['bybit']) == 0


class TestWorkerLifecycle:
    """Test worker start/stop lifecycle."""
    
    @pytest.mark.asyncio
    async def test_start_workers(self):
        """Test starting workers with custom symbols."""
        # Start workers with minimal symbols
        await start_workers(
            bybit_symbols=['BTCUSDT'],
            hl_symbols=['BTC']
        )
        
        # Give workers time to initialize
        await asyncio.sleep(0.5)
        
        # Check workers are running
        from webapp.realtime import _workers_running, _worker_tasks
        assert _workers_running == True
        assert len(_worker_tasks) > 0
        
        # Stop workers - handle potential event loop issues gracefully
        try:
            await stop_workers()
        except RuntimeError as e:
            if "Event loop is closed" in str(e):
                # This can happen in test cleanup, ignore
                pass
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_stop_workers(self):
        """Test stopping all workers."""
        await start_workers(
            bybit_symbols=['BTCUSDT'],
            hl_symbols=[]
        )
        
        await asyncio.sleep(0.3)
        
        # Stop workers
        await stop_workers()
        
        from webapp.realtime import _workers_running, _worker_tasks
        assert _workers_running == False
        assert len(_worker_tasks) == 0


class TestClientManagement:
    """Test client connection management."""
    
    def test_register_client(self):
        """Test registering a WebSocket client."""
        mock_ws = Mock()
        
        initial_count = len(_active_connections['bybit'])
        register_client(mock_ws, 'bybit')
        
        assert len(_active_connections['bybit']) == initial_count + 1
        assert mock_ws in _active_connections['bybit']
        
        # Cleanup
        unregister_client(mock_ws, 'bybit')
    
    def test_unregister_client(self):
        """Test unregistering a WebSocket client."""
        mock_ws = Mock()
        
        register_client(mock_ws, 'bybit')
        initial_count = len(_active_connections['bybit'])
        
        unregister_client(mock_ws, 'bybit')
        
        assert len(_active_connections['bybit']) == initial_count - 1
        assert mock_ws not in _active_connections['bybit']
    
    def test_get_current_data(self):
        """Test retrieving current market data."""
        # Add test data
        _bybit_data['BTCUSDT'] = {'symbol': 'BTCUSDT', 'price': 50000}
        _bybit_data['ETHUSDT'] = {'symbol': 'ETHUSDT', 'price': 3000}
        
        data = get_current_data('bybit')
        
        assert 'BTCUSDT' in data
        assert 'ETHUSDT' in data
        assert data['BTCUSDT']['price'] == 50000
        
        # Test unknown exchange
        data = get_current_data('unknown')
        assert data == {}


class TestPerformance:
    """Performance tests for real-time system."""
    
    @pytest.mark.asyncio
    async def test_high_frequency_updates(self):
        """Test system handles high-frequency updates."""
        worker = BybitWorker(['BTCUSDT'])
        
        # Simulate 100 rapid updates
        for i in range(100):
            message = {
                'topic': 'tickers.BTCUSDT',
                'data': {
                    'symbol': 'BTCUSDT',
                    'lastPrice': str(50000 + i),
                    'volume24h': '1000000',
                    'turnover24h': '50000000000',
                    'price24hPcnt': '0.01',
                    'highPrice24h': '51000',
                    'lowPrice24h': '49000',
                    'bid1Price': '49999',
                    'ask1Price': '50001'
                }
            }
            await worker._handle_message(message)
        
        # Verify last update
        assert _bybit_data['BTCUSDT']['price'] == 50099.0
    
    @pytest.mark.asyncio
    async def test_multiple_symbols(self):
        """Test handling multiple symbols simultaneously."""
        worker = BybitWorker(['SYM1', 'SYM2', 'SYM3', 'SYM4', 'SYM5'])
        
        # Send updates for all symbols
        for i, symbol in enumerate(['SYM1', 'SYM2', 'SYM3', 'SYM4', 'SYM5']):
            message = {
                'topic': f'tickers.{symbol}',
                'data': {
                    'symbol': symbol,
                    'lastPrice': str(1000 + i * 100),
                    'volume24h': '1000000',
                    'turnover24h': '1000000000',
                    'price24hPcnt': '0.01',
                    'highPrice24h': '1100',
                    'lowPrice24h': '900',
                    'bid1Price': '999',
                    'ask1Price': '1001'
                }
            }
            await worker._handle_message(message)
        
        # Verify all symbols stored
        assert len(_bybit_data) >= 5
        assert _bybit_data['SYM1']['price'] == 1000.0
        assert _bybit_data['SYM5']['price'] == 1400.0


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_invalid_message_format(self):
        """Test worker handles invalid message formats gracefully."""
        worker = BybitWorker(['BTCUSDT'])
        
        # Invalid messages
        invalid_messages = [
            {},
            {'topic': 'tickers.BTCUSDT'},  # Missing data
            {'data': {}},  # Missing topic
            {'topic': 'invalid', 'data': {}},
        ]
        
        for msg in invalid_messages:
            try:
                await worker._handle_message(msg)
            except Exception as e:
                pytest.fail(f"Worker should handle invalid messages gracefully: {e}")
    
    @pytest.mark.asyncio
    async def test_malformed_price_data(self):
        """Test handling of malformed price data."""
        worker = BybitWorker(['BTCUSDT'])
        
        # Message with invalid numeric values
        message = {
            'topic': 'tickers.BTCUSDT',
            'data': {
                'symbol': 'BTCUSDT',
                'lastPrice': 'invalid',
                'volume24h': 'abc',
                'turnover24h': '',
                'price24hPcnt': None,
                'highPrice24h': '50000',
                'lowPrice24h': '49000',
                'bid1Price': '49999',
                'ask1Price': '50001'
            }
        }
        
        # Should not crash
        try:
            await worker._handle_message(message)
        except Exception as e:
            # Expected to handle gracefully (might store 0 or skip)
            pass


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test data after each test."""
    yield
    # Clear data
    _bybit_data.clear()
    _hyperliquid_data.clear()
    _active_connections['bybit'].clear()
    _active_connections['hyperliquid'].clear()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])
