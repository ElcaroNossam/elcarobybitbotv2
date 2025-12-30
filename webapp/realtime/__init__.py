"""
Real-time market data workers for Bybit and HyperLiquid.

Architecture (inspired by scan/api/binance_workers.py):
1. WebSocket workers connect to exchange streams
2. Data stored in memory (_bybit_data, _hyperliquid_data)  
3. Every 0.2s, aggregated snapshot broadcasted via asyncio events
4. WebSocket endpoint streams to connected clients
"""
import asyncio
import json
import logging
import time
import aiohttp
from datetime import datetime, timezone
from typing import Dict, List, Optional
from decimal import Decimal
from collections import defaultdict

logger = logging.getLogger(__name__)


def safe_float(value, default: float = 0.0) -> float:
    """Safely convert value to float, handling empty strings and None."""
    if value is None or value == '':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


# In-memory storage for real-time data
_bybit_data: Dict[str, Dict] = {}
_hyperliquid_data: Dict[str, Dict] = {}
_last_snapshot_time = {'bybit': 0.0, 'hyperliquid': 0.0}
_min_snapshot_interval = 0.2  # 5 updates/second

# Active WebSocket connections (clients)
_active_connections: Dict[str, set] = {
    'bybit': set(),
    'hyperliquid': set()
}

# HTTP session for REST API calls
_http_session: Optional[aiohttp.ClientSession] = None
_session_lock = asyncio.Lock()

# Worker status
_workers_running = False
_worker_tasks = []


async def get_http_session() -> aiohttp.ClientSession:
    """Get or create HTTP session with connection pooling."""
    global _http_session
    async with _session_lock:
        if _http_session is None or _http_session.closed:
            timeout = aiohttp.ClientTimeout(total=10, connect=5)
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            _http_session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            )
    return _http_session


async def close_http_session():
    """Close HTTP session."""
    global _http_session
    if _http_session and not _http_session.closed:
        await _http_session.close()
        _http_session = None


class BybitWorker:
    """WebSocket worker for Bybit real-time data."""
    
    def __init__(self, symbols: List[str], limit: int = 200):
        self.symbols = symbols[:limit]  # Limit to top N symbols
        self.ws_url = "wss://stream.bybit.com/v5/public/linear"
        self.running = False
        self.bars_1m = defaultdict(lambda: defaultdict(lambda: {
            'volume': 0.0,
            'vdelta': 0.0,
            'trades': 0,
            'high': 0.0,
            'low': float('inf'),
            'open': 0.0,
            'close': 0.0
        }))
        
    async def start(self):
        """Start WebSocket connection and listen for updates."""
        self.running = True
        retry_count = 0
        max_retries = 10
        
        # Get initial top 200 symbols by volume
        await self._fetch_top_symbols()
        
        while self.running and retry_count < max_retries:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(self.ws_url) as ws:
                        logger.info(f"✅ Bybit WebSocket connected for {len(self.symbols)} symbols")
                        retry_count = 0  # Reset on successful connection
                        
                        # Subscribe to ticker + trade streams
                        subscribe_msg = {
                            "op": "subscribe",
                            "args": [f"tickers.{s}" for s in self.symbols] + [f"publicTrade.{s}" for s in self.symbols]
                        }
                        await ws.send_json(subscribe_msg)
                        
                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                await self._handle_message(json.loads(msg.data))
                            elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                                logger.warning(f"Bybit WebSocket closed/error: {msg.type}")
                                break
                                
            except Exception as e:
                retry_count += 1
                logger.error(f"Bybit WebSocket error (attempt {retry_count}/{max_retries}): {e}")
                await asyncio.sleep(min(retry_count * 2, 30))  # Exponential backoff
        
        logger.warning("Bybit worker stopped after max retries")
    
    async def _fetch_top_symbols(self):
        """Fetch top 200 symbols by 24h volume from Bybit."""
        try:
            session = await get_http_session()
            url = "https://api.bybit.com/v5/market/tickers?category=linear"
            
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    tickers = data.get('result', {}).get('list', [])
                    
                    # Sort by 24h turnover and take top 200
                    tickers.sort(key=lambda x: safe_float(x.get('turnover24h')), reverse=True)
                    self.symbols = [t['symbol'] for t in tickers[:200] if 'USDT' in t['symbol']]
                    
                    logger.info(f"✅ Fetched top {len(self.symbols)} Bybit symbols by volume")
        except Exception as e:
            logger.error(f"Failed to fetch top symbols: {e}")
            # Fallback to default symbols
            self.symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT']
    
    async def _handle_message(self, data: dict):
        """Process incoming WebSocket message."""
        topic = data.get('topic', '')
        
        # Ticker data
        if topic.startswith('tickers.'):
            ticker_data = data.get('data', {})
            symbol = ticker_data.get('symbol')
            
            if symbol:
                # Update in-memory storage with all metrics
                _bybit_data[symbol] = {
                    'symbol': symbol,
                    'price': safe_float(ticker_data.get('lastPrice')),
                    'mark_price': safe_float(ticker_data.get('markPrice')),
                    'index_price': safe_float(ticker_data.get('indexPrice')),
                    'volume_24h': safe_float(ticker_data.get('volume24h')),
                    'turnover_24h': safe_float(ticker_data.get('turnover24h')),
                    'change_24h': safe_float(ticker_data.get('price24hPcnt')) * 100,
                    'high_24h': safe_float(ticker_data.get('highPrice24h')),
                    'low_24h': safe_float(ticker_data.get('lowPrice24h')),
                    'bid': safe_float(ticker_data.get('bid1Price')),
                    'ask': safe_float(ticker_data.get('ask1Price')),
                    'open_interest': safe_float(ticker_data.get('openInterest')),
                    'open_interest_value': safe_float(ticker_data.get('openInterestValue')),
                    'funding_rate': safe_float(ticker_data.get('fundingRate')),
                    'next_funding_time': ticker_data.get('nextFundingTime', ''),
                    'predicted_funding': safe_float(ticker_data.get('predictedDeliveryPrice')),
                    'timestamp': time.time()
                }
        
        # Trade data for vdelta calculation
        elif topic.startswith('publicTrade.'):
            trades = data.get('data', [])
            for trade in trades:
                symbol = trade.get('s')
                if symbol:
                    price = safe_float(trade.get('p'))
                    volume = safe_float(trade.get('v'))
                    side = trade.get('S')  # 'Buy' or 'Sell'
                    timestamp = int(trade.get('T', 0) or 0)
                    
                    # Calculate vdelta (buy volume - sell volume)
                    quote_volume = price * volume
                    vdelta = quote_volume if side == 'Buy' else -quote_volume
                    
                    # Aggregate to 1m bars
                    minute_ts = (timestamp // 60000) * 60000
                    bar = self.bars_1m[symbol][minute_ts]
                    bar['volume'] += quote_volume
                    bar['vdelta'] += vdelta
                    bar['trades'] += 1
                    bar['high'] = max(bar['high'], price)
                    bar['low'] = min(bar['low'], price)
                    if bar['open'] == 0:
                        bar['open'] = price
                    bar['close'] = price
                    
                    # Update current data with aggregated metrics
                    if symbol in _bybit_data:
                        _bybit_data[symbol]['vdelta_1m'] = bar['vdelta']
                        _bybit_data[symbol]['volume_1m'] = bar['volume']
                        _bybit_data[symbol]['trades_1m'] = bar['trades']
                        _bybit_data[symbol]['volatility_1m'] = self._calculate_volatility(symbol, '1m')
    
    def _calculate_volatility(self, symbol: str, timeframe: str = '1m') -> float:
        """Calculate volatility from 1m bars."""
        try:
            bars = sorted(self.bars_1m[symbol].items())[-60:]  # Last 60 bars
            if len(bars) < 2:
                return 0.0
            
            prices = [bar[1]['close'] for bar in bars if bar[1]['close'] > 0]
            if len(prices) < 2:
                return 0.0
            
            # Calculate standard deviation
            mean = sum(prices) / len(prices)
            variance = sum((p - mean) ** 2 for p in prices) / len(prices)
            std_dev = variance ** 0.5
            
            # Return as percentage
            return (std_dev / mean * 100) if mean > 0 else 0.0
        except Exception:
            return 0.0
    
    def stop(self):
        """Stop the worker."""
        self.running = False


class HyperLiquidWorker:
    """WebSocket worker for HyperLiquid real-time data."""
    
    def __init__(self, symbols: List[str] = None):
        self.symbols = symbols or []
        self.ws_url = "wss://api.hyperliquid.xyz/ws"
        self.running = False
        self.bars_1m = defaultdict(lambda: defaultdict(lambda: {
            'volume': 0.0,
            'vdelta': 0.0,
            'trades': 0,
            'high': 0.0,
            'low': float('inf'),
            'open': 0.0,
            'close': 0.0
        }))
        self._stats_cache = {}
        self._stats_cache_time = {}
        
    async def start(self):
        """Start WebSocket connection and listen for updates."""
        self.running = True
        retry_count = 0
        max_retries = 10
        
        # Fetch all available symbols
        await self._fetch_all_symbols()
        
        while self.running and retry_count < max_retries:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(self.ws_url) as ws:
                        logger.info(f"✅ HyperLiquid WebSocket connected for {len(self.symbols)} symbols")
                        retry_count = 0
                        
                        # Subscribe to all markets data
                        subscribe_msg = {
                            "method": "subscribe",
                            "subscription": {
                                "type": "allMids"
                            }
                        }
                        await ws.send_json(subscribe_msg)
                        
                        # Subscribe to trades for vdelta (limit to avoid rate limits)
                        for symbol in self.symbols[:50]:
                            trades_sub = {
                                "method": "subscribe",
                                "subscription": {
                                    "type": "trades",
                                    "coin": symbol
                                }
                            }
                            await ws.send_json(trades_sub)
                            await asyncio.sleep(0.1)
                        
                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                await self._handle_message(json.loads(msg.data))
                            elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                                logger.warning(f"HyperLiquid WebSocket closed/error: {msg.type}")
                                break
                                
            except Exception as e:
                retry_count += 1
                logger.error(f"HyperLiquid WebSocket error (attempt {retry_count}/{max_retries}): {e}")
                await asyncio.sleep(min(retry_count * 2, 30))
        
        logger.warning("HyperLiquid worker stopped after max retries")
    
    async def _fetch_all_symbols(self):
        """Fetch all available symbols from HyperLiquid."""
        try:
            session = await get_http_session()
            url = "https://api.hyperliquid.xyz/info"
            payload = {"type": "meta"}
            
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    universe = data.get('universe', [])
                    self.symbols = [coin['name'] for coin in universe]
                    
                    logger.info(f"✅ Fetched {len(self.symbols)} HyperLiquid symbols")
        except Exception as e:
            logger.error(f"Failed to fetch HyperLiquid symbols: {e}")
            # Fallback
            self.symbols = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP']
    
    async def _handle_message(self, data: dict):
        """Process incoming WebSocket message."""
        channel = data.get('channel', '')
        
        # All mids (prices) data
        if channel == 'allMids':
            mids = data.get('data', {}).get('mids', {})
            for symbol, price in mids.items():
                if symbol in self.symbols:
                    stats = await self._get_24h_stats(symbol)
                    
                    _hyperliquid_data[symbol] = {
                        'symbol': symbol,
                        'price': float(price),
                        'volume_24h': stats.get('volume_24h', 0),
                        'change_24h': stats.get('change_24h', 0),
                        'high_24h': stats.get('high_24h', 0),
                        'low_24h': stats.get('low_24h', 0),
                        'open_interest': stats.get('open_interest', 0),
                        'funding_rate': stats.get('funding_rate', 0),
                        'timestamp': time.time()
                    }
        
        # Trade data for vdelta
        elif channel == 'trades':
            trades = data.get('data', [])
            for trade in trades:
                coin = trade.get('coin')
                if coin and coin in self.symbols:
                    price = safe_float(trade.get('px'))
                    size = safe_float(trade.get('sz'))
                    side = trade.get('side')  # 'A' (ask/sell) or 'B' (bid/buy)
                    timestamp = int(trade.get('time', 0) or 0)
                    
                    # Calculate vdelta
                    quote_volume = price * size
                    vdelta = quote_volume if side == 'B' else -quote_volume
                    
                    # Aggregate to 1m bars
                    minute_ts = (timestamp // 60000) * 60000
                    bar = self.bars_1m[coin][minute_ts]
                    bar['volume'] += quote_volume
                    bar['vdelta'] += vdelta
                    bar['trades'] += 1
                    bar['high'] = max(bar['high'], price)
                    bar['low'] = min(bar['low'], price)
                    if bar['open'] == 0:
                        bar['open'] = price
                    bar['close'] = price
                    
                    # Update metrics
                    if coin in _hyperliquid_data:
                        _hyperliquid_data[coin]['vdelta_1m'] = bar['vdelta']
                        _hyperliquid_data[coin]['volume_1m'] = bar['volume']
                        _hyperliquid_data[coin]['trades_1m'] = bar['trades']
                        _hyperliquid_data[coin]['volatility_1m'] = self._calculate_volatility(coin, '1m')
    
    async def _get_24h_stats(self, symbol: str) -> dict:
        """Fetch 24h statistics from API (with caching)."""
        now = time.time()
        if symbol in self._stats_cache and (now - self._stats_cache_time.get(symbol, 0)) < 60:
            return self._stats_cache[symbol]
        
        try:
            session = await get_http_session()
            url = "https://api.hyperliquid.xyz/info"
            payload = {"type": "metaAndAssetCtxs"}
            
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for ctx in data[1]:
                        if ctx.get('coin') == symbol:
                            stats = {
                                'volume_24h': safe_float(ctx.get('dayNtlVlm')),
                                'change_24h': (safe_float(ctx.get('premium')) * 100),
                                'open_interest': safe_float(ctx.get('openInterest')),
                                'funding_rate': safe_float(ctx.get('funding')),
                                'high_24h': 0,
                                'low_24h': 0
                            }
                            self._stats_cache[symbol] = stats
                            self._stats_cache_time[symbol] = now
                            return stats
        except Exception:
            pass
        
        return {}
    
    def _calculate_volatility(self, symbol: str, timeframe: str = '1m') -> float:
        """Calculate volatility from 1m bars."""
        try:
            bars = sorted(self.bars_1m[symbol].items())[-60:]
            if len(bars) < 2:
                return 0.0
            
            prices = [bar[1]['close'] for bar in bars if bar[1]['close'] > 0]
            if len(prices) < 2:
                return 0.0
            
            mean = sum(prices) / len(prices)
            variance = sum((p - mean) ** 2 for p in prices) / len(prices)
            std_dev = variance ** 0.5
            
            return (std_dev / mean * 100) if mean > 0 else 0.0
        except Exception:
            return 0.0
    
    def stop(self):
        """Stop the worker."""
        self.running = False


async def snapshot_broadcaster(exchange: str, interval: float = 0.2):
    """
    Periodically broadcast snapshots to connected clients.
    
    Args:
        exchange: 'bybit' or 'hyperliquid'
        interval: seconds between broadcasts
    """
    logger.info(f"Started snapshot broadcaster for {exchange}")
    
    while True:
        try:
            await asyncio.sleep(interval)
            
            # Get data for this exchange
            data = _bybit_data if exchange == 'bybit' else _hyperliquid_data
            
            if not data or not _active_connections[exchange]:
                continue
            
            # Prepare snapshot
            snapshot = {
                'type': 'market_data',
                'exchange': exchange,
                'data': list(data.values()),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'count': len(data)
            }
            
            # Broadcast to all connected clients
            disconnected = set()
            for websocket in _active_connections[exchange].copy():
                try:
                    await websocket.send_json(snapshot)
                except Exception as e:
                    logger.debug(f"Failed to send to client: {e}")
                    disconnected.add(websocket)
            
            # Remove disconnected clients
            _active_connections[exchange] -= disconnected
            
        except asyncio.CancelledError:
            logger.info(f"Snapshot broadcaster for {exchange} cancelled")
            break
        except Exception as e:
            logger.error(f"Error in snapshot broadcaster for {exchange}: {e}", exc_info=True)
            await asyncio.sleep(1)


async def start_workers(bybit_symbols: List[str] = None, hl_symbols: List[str] = None):
    """
    Start all workers and broadcaster tasks.
    
    Args:
        bybit_symbols: List of Bybit symbols to monitor
        hl_symbols: List of HyperLiquid symbols to monitor
    """
    global _workers_running, _worker_tasks
    
    if _workers_running:
        logger.warning("Workers already running")
        return
    
    _workers_running = True
    _worker_tasks = []
    
    # Default symbols if not provided
    if bybit_symbols is None:
        bybit_symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT']
    
    if hl_symbols is None:
        hl_symbols = ['BTC', 'ETH', 'SOL']
    
    # Start Bybit worker
    if bybit_symbols:
        bybit_worker = BybitWorker(bybit_symbols)
        task = asyncio.create_task(bybit_worker.start(), name="bybit_worker")
        _worker_tasks.append(task)
        
        # Start Bybit broadcaster
        broadcaster_task = asyncio.create_task(
            snapshot_broadcaster('bybit', _min_snapshot_interval),
            name="bybit_broadcaster"
        )
        _worker_tasks.append(broadcaster_task)
    
    # Start HyperLiquid worker
    if hl_symbols:
        hl_worker = HyperLiquidWorker(hl_symbols)
        task = asyncio.create_task(hl_worker.start(), name="hyperliquid_worker")
        _worker_tasks.append(task)
        
        # Start HyperLiquid broadcaster
        broadcaster_task = asyncio.create_task(
            snapshot_broadcaster('hyperliquid', _min_snapshot_interval),
            name="hyperliquid_broadcaster"
        )
        _worker_tasks.append(broadcaster_task)
    
    logger.info(f"✅ Started {len(_worker_tasks)} worker tasks")


async def stop_workers():
    """Stop all workers and clean up."""
    global _workers_running, _worker_tasks
    
    _workers_running = False
    
    # Cancel all tasks
    for task in _worker_tasks:
        task.cancel()
    
    # Wait for cancellation
    if _worker_tasks:
        await asyncio.gather(*_worker_tasks, return_exceptions=True)
    
    _worker_tasks = []
    await close_http_session()
    
    logger.info("All workers stopped")


def register_client(websocket, exchange: str):
    """Register a WebSocket client for updates."""
    _active_connections[exchange].add(websocket)
    logger.debug(f"Client registered for {exchange}. Total: {len(_active_connections[exchange])}")


def unregister_client(websocket, exchange: str):
    """Unregister a WebSocket client."""
    _active_connections[exchange].discard(websocket)
    logger.debug(f"Client unregistered from {exchange}. Remaining: {len(_active_connections[exchange])}")


def get_current_data(exchange: str) -> Dict[str, Dict]:
    """Get current in-memory data for an exchange."""
    if exchange == 'bybit':
        return _bybit_data.copy()
    elif exchange == 'hyperliquid':
        return _hyperliquid_data.copy()
    return {}


def get_market_data(exchange: str) -> Dict[str, Dict]:
    """
    Get current market data for an exchange (alias for get_current_data).
    
    Args:
        exchange: 'bybit' or 'hyperliquid'
        
    Returns:
        Dictionary of symbol -> market data
    """
    return get_current_data(exchange)


def get_worker_status() -> dict:
    """Get status of all workers."""
    return {
        'running': _workers_running,
        'task_count': len(_worker_tasks),
        'bybit_symbols': len(_bybit_data),
        'hyperliquid_symbols': len(_hyperliquid_data),
        'bybit_clients': len(_active_connections['bybit']),
        'hyperliquid_clients': len(_active_connections['hyperliquid'])
    }
