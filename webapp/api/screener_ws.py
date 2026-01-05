"""
Crypto Screener WebSocket API for ElcaroBot
Real-time market data from multiple exchanges
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, List, Optional, Set
import asyncio
import aiohttp
import json
from datetime import datetime
import logging
from .exchange_fetchers import BybitDataFetcher, OKXDataFetcher, HyperLiquidDataFetcher
from core.tasks import safe_create_task

logger = logging.getLogger(__name__)
router = APIRouter()

# Exchange API endpoints
BINANCE_FUTURES_API = "https://fapi.binance.com"
BINANCE_SPOT_API = "https://api.binance.com"
BINANCE_FUTURES_WS = "wss://fstream.binance.com"

BYBIT_API = "https://api.bybit.com"
OKX_API = "https://www.okx.com"
HYPERLIQUID_API = "https://api.hyperliquid.xyz"

# Cache for market data (per exchange)
class MarketDataCache:
    def __init__(self):
        # Binance data
        self.binance_futures_data: Dict[str, dict] = {}
        self.binance_spot_data: Dict[str, dict] = {}
        # Bybit data
        self.bybit_futures_data: Dict[str, dict] = {}
        self.bybit_spot_data: Dict[str, dict] = {}
        # OKX data
        self.okx_futures_data: Dict[str, dict] = {}
        self.okx_spot_data: Dict[str, dict] = {}
        # HyperLiquid data (perps only)
        self.hyperliquid_futures_data: Dict[str, dict] = {}
        # Common data
        self.btc_data: dict = {}
        self.liquidations: List[dict] = []
        self.last_update: datetime = datetime.now()
    
    def get_futures_data(self, exchange: str = 'binance') -> Dict[str, dict]:
        """Get futures data for specific exchange"""
        if exchange == 'bybit':
            return self.bybit_futures_data
        elif exchange == 'okx':
            return self.okx_futures_data
        elif exchange == 'hyperliquid':
            return self.hyperliquid_futures_data
        return self.binance_futures_data
    
    def get_spot_data(self, exchange: str = 'binance') -> Dict[str, dict]:
        """Get spot data for specific exchange"""
        if exchange == 'bybit':
            return self.bybit_spot_data
        elif exchange == 'okx':
            return self.okx_spot_data
        elif exchange == 'hyperliquid':
            return {}  # HyperLiquid is perps only
        return self.binance_spot_data
        
cache = MarketDataCache()

# Active WebSocket connections
active_connections: Set[WebSocket] = set()

class BinanceDataFetcher:
    """Fetches data from Binance REST API"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - ensures session is closed"""
        await self.close()
        return False
    
    async def fetch_futures_tickers(self) -> List[dict]:
        """Fetch futures 24hr ticker data"""
        session = await self.get_session()
        try:
            async with session.get(f"{BINANCE_FUTURES_API}/fapi/v1/ticker/24hr") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Filter USDT pairs and sort by volume
                    usdt_pairs = [d for d in data if d['symbol'].endswith('USDT') and not d['symbol'].endswith('_PERP')]
                    usdt_pairs.sort(key=lambda x: float(x.get('quoteVolume', 0)), reverse=True)
                    return usdt_pairs[:50]  # Top 50 by volume
                return []
        except Exception as e:
            logger.error(f"Error fetching futures tickers: {e}")
            return []
    
    async def fetch_spot_tickers(self) -> List[dict]:
        """Fetch spot 24hr ticker data"""
        session = await self.get_session()
        try:
            async with session.get(f"{BINANCE_SPOT_API}/api/v3/ticker/24hr") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    usdt_pairs = [d for d in data if d['symbol'].endswith('USDT')]
                    usdt_pairs.sort(key=lambda x: float(x.get('quoteVolume', 0)), reverse=True)
                    return usdt_pairs[:50]
                return []
        except Exception as e:
            logger.error(f"Error fetching spot tickers: {e}")
            return []
    
    async def fetch_funding_rates(self) -> Dict[str, float]:
        """Fetch current funding rates"""
        session = await self.get_session()
        try:
            async with session.get(f"{BINANCE_FUTURES_API}/fapi/v1/premiumIndex") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {d['symbol']: float(d.get('lastFundingRate', 0)) for d in data}
                return {}
        except Exception as e:
            logger.error(f"Error fetching funding rates: {e}")
            return {}
    
    async def fetch_open_interest(self) -> Dict[str, float]:
        """Fetch open interest for symbols"""
        session = await self.get_session()
        try:
            async with session.get(f"{BINANCE_FUTURES_API}/fapi/v1/openInterest", params={"symbol": "BTCUSDT"}) as resp:
                # For multiple symbols, we need separate calls or use different endpoint
                pass
            # Use ticker for OI value (notional)
            async with session.get(f"{BINANCE_FUTURES_API}/futures/data/openInterestHist",
                                   params={"symbol": "BTCUSDT", "period": "5m", "limit": 1}) as resp:
                pass
            return {}
        except Exception as e:
            return {}
    
    def process_ticker(self, ticker: dict, funding_rates: Dict[str, float]) -> dict:
        """Process raw ticker to our format"""
        symbol = ticker.get('symbol', '')
        price = float(ticker.get('lastPrice', 0))
        open_price = float(ticker.get('openPrice', 0))
        high = float(ticker.get('highPrice', 0))
        low = float(ticker.get('lowPrice', 0))
        volume = float(ticker.get('quoteVolume', 0))
        
        # Calculate changes
        change_24h = float(ticker.get('priceChangePercent', 0))
        
        # Approximate shorter timeframe changes (we'll improve this with klines)
        change_1h = change_24h / 24 if change_24h else 0
        change_15m = change_1h / 4 if change_1h else 0
        change_5m = change_15m / 3 if change_15m else 0
        change_1m = change_5m / 5 if change_5m else 0
        change_30m = change_15m * 2 if change_15m else 0
        change_4h = change_1h * 4 if change_1h else 0
        change_8h = change_4h * 2 if change_4h else 0
        
        # OI changes (approximation)
        oi_base = float(ticker.get('openInterest', 0)) if 'openInterest' in ticker else volume * 0.1
        oi_change_1m = change_1m * 0.8  # OI changes slower than price
        oi_change_5m = change_5m * 0.8
        oi_change_15m = change_15m * 0.8
        oi_change_30m = change_30m * 0.8
        oi_change_1h = change_1h * 0.8
        oi_change_4h = change_4h * 0.8
        oi_change_8h = change_8h * 0.8
        oi_change_1d = change_24h * 0.8
        
        # Volatility (simplified calculation)
        volatility_base = ((high - low) / price * 100) if price > 0 else 0
        volatility_1m = volatility_base / 24 / 60
        volatility_5m = volatility_base / 24 / 12
        volatility_15m = volatility_base / 24 / 4
        volatility_30m = volatility_base / 24 / 2
        volatility_1h = volatility_base / 24
        
        # Volumes (approximation based on 24h volume)
        volume_1m = volume / 24 / 60
        volume_5m = volume / 24 / 12
        volume_15m = volume / 24 / 4
        volume_30m = volume / 24 / 2
        volume_1h = volume / 24
        volume_4h = volume / 6
        volume_8h = volume / 3
        
        return {
            "symbol": symbol,
            "price": price,
            "change_1m": round(change_1m, 2),
            "change_5m": round(change_5m, 2),
            "change_15m": round(change_15m, 2),
            "change_30m": round(change_30m, 2),
            "change_1h": round(change_1h, 2),
            "change_4h": round(change_4h, 2),
            "change_8h": round(change_8h, 2),
            "change_24h": round(change_24h, 2),
            "volume_1m": volume_1m,
            "volume_5m": volume_5m,
            "volume_15m": volume_15m,
            "volume_30m": volume_30m,
            "volume_1h": volume_1h,
            "volume_4h": volume_4h,
            "volume_8h": volume_8h,
            "volume": volume,
            "volume24h": volume,
            "high_24h": high,
            "low_24h": low,
            "open_interest": oi_base,
            "oi_change_1m": round(oi_change_1m, 2),
            "oi_change_5m": round(oi_change_5m, 2),
            "oi_change_15m": round(oi_change_15m, 2),
            "oi_change_30m": round(oi_change_30m, 2),
            "oi_change_1h": round(oi_change_1h, 2),
            "oi_change_4h": round(oi_change_4h, 2),
            "oi_change_8h": round(oi_change_8h, 2),
            "oi_change_1d": round(oi_change_1d, 2),
            "funding_rate": funding_rates.get(symbol, 0),
            "volatility_1m": round(volatility_1m, 4),
            "volatility_5m": round(volatility_5m, 4),
            "volatility_15m": round(volatility_15m, 4),
            "volatility_30m": round(volatility_30m, 4),
            "volatility_1h": round(volatility_1h, 4),
            "vdelta": 0,  # Will be calculated from trades
            "timestamp": datetime.now().isoformat()
        }

# Initialize all fetchers
binance_fetcher = BinanceDataFetcher()
bybit_fetcher = BybitDataFetcher()
okx_fetcher = OKXDataFetcher()
hyperliquid_fetcher = HyperLiquidDataFetcher()

async def update_market_data():
    """Background task to update market data every 3 seconds for all exchanges"""
    while True:
        try:
            # Update Binance data
            try:
                funding_rates = await binance_fetcher.fetch_funding_rates()
                futures_tickers = await binance_fetcher.fetch_futures_tickers()
                spot_tickers = await binance_fetcher.fetch_spot_tickers()
                
                for ticker in futures_tickers:
                    processed = binance_fetcher.process_ticker(ticker, funding_rates)
                    cache.binance_futures_data[processed['symbol']] = processed
                
                for ticker in spot_tickers:
                    processed = binance_fetcher.process_ticker(ticker, {})
                    processed['funding_rate'] = None
                    processed['open_interest'] = None
                    cache.binance_spot_data[processed['symbol']] = processed
            except Exception as e:
                logger.error(f"Error updating Binance data: {e}")
            
            # Update Bybit data
            try:
                funding_rates = await bybit_fetcher.fetch_funding_rates()
                futures_tickers = await bybit_fetcher.fetch_futures_tickers()
                spot_tickers = await bybit_fetcher.fetch_spot_tickers()
                
                for ticker in futures_tickers:
                    processed = bybit_fetcher.process_ticker(ticker, funding_rates)
                    cache.bybit_futures_data[processed['symbol']] = processed
                
                for ticker in spot_tickers:
                    processed = bybit_fetcher.process_ticker(ticker, {})
                    processed['funding_rate'] = None
                    processed['open_interest'] = None
                    cache.bybit_spot_data[processed['symbol']] = processed
            except Exception as e:
                logger.error(f"Error updating Bybit data: {e}")
            
            # Update OKX data
            try:
                funding_rates = await okx_fetcher.fetch_funding_rates()
                futures_tickers = await okx_fetcher.fetch_futures_tickers()
                spot_tickers = await okx_fetcher.fetch_spot_tickers()
                
                for ticker in futures_tickers:
                    processed = okx_fetcher.process_ticker(ticker, funding_rates)
                    cache.okx_futures_data[processed['symbol']] = processed
                
                for ticker in spot_tickers:
                    processed = okx_fetcher.process_ticker(ticker, {})
                    processed['funding_rate'] = None
                    processed['open_interest'] = None
                    cache.okx_spot_data[processed['symbol']] = processed
            except Exception as e:
                logger.error(f"Error updating OKX data: {e}")
            
            # Update HyperLiquid data (perps only)
            try:
                funding_rates = await hyperliquid_fetcher.fetch_funding_rates()
                futures_tickers = await hyperliquid_fetcher.fetch_futures_tickers()
                
                for ticker in futures_tickers:
                    processed = hyperliquid_fetcher.process_ticker(ticker, funding_rates)
                    cache.hyperliquid_futures_data[processed['symbol']] = processed
            except Exception as e:
                logger.error(f"Error updating HyperLiquid data: {e}")
            
            # Update BTC data (from Binance as primary)
            if 'BTCUSDT' in cache.binance_futures_data:
                btc = cache.binance_futures_data['BTCUSDT']
                cache.btc_data = {
                    "price": btc['price'],
                    "change": btc['change_24h']
                }
            
            cache.last_update = datetime.now()
            
            # Broadcast to connected clients
            await broadcast_update()
            
        except Exception as e:
            logger.error(f"Error updating market data: {e}")
        
        await asyncio.sleep(3)  # Update every 3 seconds

async def broadcast_update():
    """Send updates to all connected WebSocket clients"""
    if not active_connections:
        return
    
    disconnected = set()
    for ws in active_connections:
        try:
            # Send based on subscribed market and exchange
            market = getattr(ws, 'subscribed_market', 'futures')
            exchange = getattr(ws, 'subscribed_exchange', 'binance')
            
            futures_data = cache.get_futures_data(exchange)
            spot_data = cache.get_spot_data(exchange)
            data = list(futures_data.values()) if market == 'futures' else list(spot_data.values())
            
            await ws.send_json({
                "type": "update",
                "data": data,
                "btc": cache.btc_data,
                "timestamp": cache.last_update.isoformat()
            })
        except Exception as e:
            logger.error(f"Error sending to websocket: {e}")
            disconnected.add(ws)
    
    # Remove disconnected clients
    for ws in disconnected:
        active_connections.discard(ws)

# Start background task
background_task = None

@router.on_event("startup")
async def startup():
    global background_task
    background_task = safe_create_task(update_market_data(), name="screener_market_data")

@router.on_event("shutdown")
async def shutdown():
    global background_task
    if background_task:
        background_task.cancel()
    await binance_fetcher.close()
    await bybit_fetcher.close()
    await okx_fetcher.close()
    await hyperliquid_fetcher.close()

@router.websocket("/ws/screener")
async def screener_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time screener data"""
    await websocket.accept()
    active_connections.add(websocket)
    websocket.subscribed_market = 'futures'
    websocket.subscribed_exchange = 'binance'
    
    try:
        # Send initial snapshot
        futures_data = cache.get_futures_data('binance')
        data = list(futures_data.values())
        await websocket.send_json({
            "type": "snapshot",
            "data": data,
            "btc": cache.btc_data,
            "timestamp": datetime.now().isoformat()
        })
        
        # Listen for messages
        while True:
            try:
                message = await websocket.receive_json()
                msg_type = message.get('type')
                
                if msg_type == 'subscribe':
                    market = message.get('market', 'futures')
                    exchange = message.get('exchange', 'binance')
                    
                    websocket.subscribed_market = market
                    websocket.subscribed_exchange = exchange
                    
                    futures_data = cache.get_futures_data(exchange)
                    spot_data = cache.get_spot_data(exchange)
                    data = list(futures_data.values()) if market == 'futures' else list(spot_data.values())
                    
                    await websocket.send_json({
                        "type": "snapshot",
                        "data": data,
                        "btc": cache.btc_data,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
                
    finally:
        active_connections.discard(websocket)

@router.get("/api/screener/symbols")
async def get_symbols(market: str = "futures"):
    """Get list of symbols"""
    if market == "futures":
        return {"symbols": list(cache.futures_data.keys())}
    return {"symbols": list(cache.spot_data.keys())}

@router.get("/api/screener/overview")
async def get_overview(market: str = "futures"):
    """Get market overview"""
    data = cache.futures_data if market == "futures" else cache.spot_data
    values = list(data.values())
    
    gainers = len([s for s in values if s.get('change_24h', 0) > 0])
    losers = len([s for s in values if s.get('change_24h', 0) < 0])
    total_volume = sum(s.get('volume', 0) for s in values)
    
    return {
        "total": len(values),
        "gainers": gainers,
        "losers": losers,
        "total_volume": total_volume,
        "btc": cache.btc_data,
        "last_update": cache.last_update.isoformat()
    }

@router.get("/api/screener/symbol/{symbol}")
async def get_symbol_data(symbol: str, market: str = "futures"):
    """Get data for specific symbol"""
    data = cache.futures_data if market == "futures" else cache.spot_data
    if symbol not in data:
        raise HTTPException(status_code=404, detail="Symbol not found")
    return data[symbol]
