"""
Exchange data fetchers for ElCaro Screener
Supports: Binance, Bybit, OKX
"""
import aiohttp
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Exchange API endpoints
BYBIT_API = "https://api.bybit.com"
OKX_API = "https://www.okx.com"


class BybitDataFetcher:
    """Fetches data from Bybit REST API"""
    
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
        """Fetch Bybit futures 24hr ticker data"""
        session = await self.get_session()
        try:
            async with session.get(f"{BYBIT_API}/v5/market/tickers", params={"category": "linear"}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('retCode') == 0:
                        tickers = data.get('result', {}).get('list', [])
                        # Filter USDT pairs and sort by volume
                        usdt_pairs = [t for t in tickers if t.get('symbol', '').endswith('USDT')]
                        usdt_pairs.sort(key=lambda x: float(x.get('turnover24h', 0)), reverse=True)
                        return usdt_pairs[:50]
                return []
        except Exception as e:
            logger.error(f"Error fetching Bybit futures tickers: {e}")
            return []
    
    async def fetch_spot_tickers(self) -> List[dict]:
        """Fetch Bybit spot 24hr ticker data"""
        session = await self.get_session()
        try:
            async with session.get(f"{BYBIT_API}/v5/market/tickers", params={"category": "spot"}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('retCode') == 0:
                        tickers = data.get('result', {}).get('list', [])
                        usdt_pairs = [t for t in tickers if t.get('symbol', '').endswith('USDT')]
                        usdt_pairs.sort(key=lambda x: float(x.get('turnover24h', 0)), reverse=True)
                        return usdt_pairs[:50]
                return []
        except Exception as e:
            logger.error(f"Error fetching Bybit spot tickers: {e}")
            return []
    
    async def fetch_funding_rates(self) -> Dict[str, float]:
        """Fetch Bybit funding rates"""
        session = await self.get_session()
        try:
            async with session.get(f"{BYBIT_API}/v5/market/tickers", params={"category": "linear"}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('retCode') == 0:
                        tickers = data.get('result', {}).get('list', [])
                        return {t['symbol']: float(t.get('fundingRate', 0)) for t in tickers if t.get('fundingRate')}
                return {}
        except Exception as e:
            logger.error(f"Error fetching Bybit funding rates: {e}")
            return {}
    
    def process_ticker(self, ticker: dict, funding_rates: Dict[str, float]) -> dict:
        """Process Bybit ticker to unified format"""
        from datetime import datetime
        
        symbol = ticker.get('symbol', '')
        price = float(ticker.get('lastPrice', 0))
        high = float(ticker.get('highPrice24h', 0))
        low = float(ticker.get('lowPrice24h', 0))
        volume = float(ticker.get('turnover24h', 0))
        change_24h = float(ticker.get('price24hPcnt', 0)) * 100
        
        # Approximate shorter timeframes
        change_1h = change_24h / 24
        change_15m = change_1h / 4
        change_5m = change_15m / 3
        change_1m = change_5m / 5
        change_30m = change_15m * 2
        change_4h = change_1h * 4
        change_8h = change_4h * 2
        
        # OI and volatility
        oi_base = float(ticker.get('openInterest', 0)) if 'openInterest' in ticker else volume * 0.1
        oi_change_1m = change_1m * 0.8
        oi_change_5m = change_5m * 0.8
        oi_change_15m = change_15m * 0.8
        oi_change_30m = change_30m * 0.8
        oi_change_1h = change_1h * 0.8
        oi_change_4h = change_4h * 0.8
        oi_change_8h = change_8h * 0.8
        oi_change_1d = change_24h * 0.8
        
        volatility_base = ((high - low) / price * 100) if price > 0 else 0
        volatility_1m = volatility_base / 24 / 60
        volatility_5m = volatility_base / 24 / 12
        volatility_15m = volatility_base / 24 / 4
        volatility_30m = volatility_base / 24 / 2
        volatility_1h = volatility_base / 24
        
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
            "vdelta": 0,
            "timestamp": datetime.now().isoformat()
        }


class OKXDataFetcher:
    """Fetches data from OKX REST API"""
    
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
        """Fetch OKX futures 24hr ticker data"""
        session = await self.get_session()
        try:
            async with session.get(f"{OKX_API}/api/v5/market/tickers", params={"instType": "SWAP"}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('code') == '0':
                        tickers = data.get('data', [])
                        # Filter USDT pairs
                        usdt_pairs = [t for t in tickers if t.get('instId', '').endswith('-USDT-SWAP')]
                        usdt_pairs.sort(key=lambda x: float(x.get('volCcy24h', 0)), reverse=True)
                        return usdt_pairs[:50]
                return []
        except Exception as e:
            logger.error(f"Error fetching OKX futures tickers: {e}")
            return []
    
    async def fetch_spot_tickers(self) -> List[dict]:
        """Fetch OKX spot 24hr ticker data"""
        session = await self.get_session()
        try:
            async with session.get(f"{OKX_API}/api/v5/market/tickers", params={"instType": "SPOT"}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('code') == '0':
                        tickers = data.get('data', [])
                        usdt_pairs = [t for t in tickers if t.get('instId', '').endswith('-USDT')]
                        usdt_pairs.sort(key=lambda x: float(x.get('volCcy24h', 0)), reverse=True)
                        return usdt_pairs[:50]
                return []
        except Exception as e:
            logger.error(f"Error fetching OKX spot tickers: {e}")
            return []
    
    async def fetch_funding_rates(self) -> Dict[str, float]:
        """Fetch OKX funding rates"""
        session = await self.get_session()
        try:
            async with session.get(f"{OKX_API}/api/v5/public/funding-rate", params={"instType": "SWAP"}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('code') == '0':
                        rates = data.get('data', [])
                        return {r['instId']: float(r.get('fundingRate', 0)) for r in rates}
                return {}
        except Exception as e:
            logger.error(f"Error fetching OKX funding rates: {e}")
            return {}
    
    def process_ticker(self, ticker: dict, funding_rates: Dict[str, float]) -> dict:
        """Process OKX ticker to unified format"""
        from datetime import datetime
        
        inst_id = ticker.get('instId', '')
        # Convert OKX format to our format: BTC-USDT-SWAP -> BTCUSDT
        symbol = inst_id.replace('-USDT-SWAP', 'USDT').replace('-USDT', 'USDT')
        
        price = float(ticker.get('last', 0))
        high = float(ticker.get('high24h', 0))
        low = float(ticker.get('low24h', 0))
        volume = float(ticker.get('volCcy24h', 0))
        open_price = float(ticker.get('open24h', 0))
        change_24h = ((price - open_price) / open_price * 100) if open_price > 0 else 0
        
        # Approximate shorter timeframes
        change_1h = change_24h / 24
        change_15m = change_1h / 4
        change_5m = change_15m / 3
        change_1m = change_5m / 5
        change_30m = change_15m * 2
        change_4h = change_1h * 4
        change_8h = change_4h * 2
        
        # OI and volatility
        oi_base = float(ticker.get('openInterest', 0)) if 'openInterest' in ticker else volume * 0.1
        oi_change_1m = change_1m * 0.8
        oi_change_5m = change_5m * 0.8
        oi_change_15m = change_15m * 0.8
        oi_change_30m = change_30m * 0.8
        oi_change_1h = change_1h * 0.8
        oi_change_4h = change_4h * 0.8
        oi_change_8h = change_8h * 0.8
        oi_change_1d = change_24h * 0.8
        
        volatility_base = ((high - low) / price * 100) if price > 0 else 0
        volatility_1m = volatility_base / 24 / 60
        volatility_5m = volatility_base / 24 / 12
        volatility_15m = volatility_base / 24 / 4
        volatility_30m = volatility_base / 24 / 2
        volatility_1h = volatility_base / 24
        
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
            "funding_rate": funding_rates.get(inst_id, 0),
            "volatility_1m": round(volatility_1m, 4),
            "volatility_5m": round(volatility_5m, 4),
            "volatility_15m": round(volatility_15m, 4),
            "volatility_30m": round(volatility_30m, 4),
            "volatility_1h": round(volatility_1h, 4),
            "vdelta": 0,
            "timestamp": datetime.now().isoformat()
        }


def get_fetcher(exchange: str):
    """Factory function to get appropriate fetcher"""
    if exchange == 'bybit':
        return BybitDataFetcher()
    elif exchange == 'okx':
        return OKXDataFetcher()
    else:
        # Return Binance fetcher (imported in screener_ws.py)
        return None  # Will use BinanceDataFetcher from screener_ws
