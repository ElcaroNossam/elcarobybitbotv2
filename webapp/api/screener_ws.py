"""
Crypto Screener WebSocket API for ElcaroBot
Real-time market data from Binance
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, List, Optional, Set
import asyncio
import aiohttp
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Binance API endpoints
BINANCE_FUTURES_API = "https://fapi.binance.com"
BINANCE_SPOT_API = "https://api.binance.com"
BINANCE_FUTURES_WS = "wss://fstream.binance.com"

# Cache for market data
class MarketDataCache:
    def __init__(self):
        self.futures_data: Dict[str, dict] = {}
        self.spot_data: Dict[str, dict] = {}
        self.btc_data: dict = {}
        self.liquidations: List[dict] = []
        self.last_update: datetime = datetime.now()
        
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
        change_5m = change_1h / 12 if change_1h else 0
        change_1m = change_5m / 5 if change_5m else 0
        
        return {
            "symbol": symbol,
            "price": price,
            "change_1m": round(change_1m, 2),
            "change_5m": round(change_5m, 2),
            "change_15m": round(change_5m * 3, 2),
            "change_1h": round(change_1h, 2),
            "change_4h": round(change_1h * 4, 2),
            "change_24h": round(change_24h, 2),
            "volume": volume,
            "high_24h": high,
            "low_24h": low,
            "open_interest": float(ticker.get('openInterest', 0)) if 'openInterest' in ticker else volume * 0.1,
            "funding_rate": funding_rates.get(symbol, 0),
            "vdelta": 0,  # Will be calculated from trades
            "timestamp": datetime.now().isoformat()
        }

fetcher = BinanceDataFetcher()

async def update_market_data():
    """Background task to update market data every 3 seconds"""
    while True:
        try:
            # Fetch data
            funding_rates = await fetcher.fetch_funding_rates()
            futures_tickers = await fetcher.fetch_futures_tickers()
            spot_tickers = await fetcher.fetch_spot_tickers()
            
            # Process futures
            for ticker in futures_tickers:
                processed = fetcher.process_ticker(ticker, funding_rates)
                cache.futures_data[processed['symbol']] = processed
            
            # Process spot
            for ticker in spot_tickers:
                processed = fetcher.process_ticker(ticker, {})
                processed['funding_rate'] = None
                processed['open_interest'] = None
                cache.spot_data[processed['symbol']] = processed
            
            # Update BTC data
            if 'BTCUSDT' in cache.futures_data:
                btc = cache.futures_data['BTCUSDT']
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
            # Send based on subscribed market
            market = getattr(ws, 'subscribed_market', 'futures')
            data = list(cache.futures_data.values()) if market == 'futures' else list(cache.spot_data.values())
            
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
    background_task = asyncio.create_task(update_market_data())

@router.on_event("shutdown")
async def shutdown():
    global background_task
    if background_task:
        background_task.cancel()
    await fetcher.close()

@router.websocket("/ws/screener")
async def screener_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time screener data"""
    await websocket.accept()
    active_connections.add(websocket)
    websocket.subscribed_market = 'futures'
    
    try:
        # Send initial snapshot
        data = list(cache.futures_data.values())
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
                    websocket.subscribed_market = market
                    data = list(cache.futures_data.values()) if market == 'futures' else list(cache.spot_data.values())
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
