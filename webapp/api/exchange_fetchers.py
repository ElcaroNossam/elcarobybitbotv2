"""
Exchange data fetchers for Lyxen Screener
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
        self._max_retries = 2
        
    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=15, connect=5)
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5, force_close=True)
            self.session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        return self.session
        
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    async def _fetch_with_retry(self, url: str, params: dict) -> Optional[dict]:
        """Fetch with retry logic for connection issues"""
        session = await self.get_session()
        for attempt in range(self._max_retries + 1):
            try:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    return None
            except (aiohttp.ClientError, ConnectionResetError, TimeoutError) as e:
                if attempt < self._max_retries:
                    logger.debug(f"OKX retry {attempt + 1}/{self._max_retries}: {e}")
                    await self.close()  # Reset session
                    continue
                logger.warning(f"OKX fetch failed after {self._max_retries + 1} attempts: {e}")
                return None
            except Exception as e:
                logger.error(f"OKX unexpected error: {e}")
                return None
        return None
    
    async def fetch_futures_tickers(self) -> List[dict]:
        """Fetch OKX futures 24hr ticker data"""
        data = await self._fetch_with_retry(f"{OKX_API}/api/v5/market/tickers", {"instType": "SWAP"})
        if data and data.get('code') == '0':
            tickers = data.get('data', [])
            # Filter USDT pairs
            usdt_pairs = [t for t in tickers if t.get('instId', '').endswith('-USDT-SWAP')]
            usdt_pairs.sort(key=lambda x: float(x.get('volCcy24h', 0)), reverse=True)
            return usdt_pairs[:50]
        return []
    
    async def fetch_spot_tickers(self) -> List[dict]:
        """Fetch OKX spot 24hr ticker data"""
        data = await self._fetch_with_retry(f"{OKX_API}/api/v5/market/tickers", {"instType": "SPOT"})
        if data and data.get('code') == '0':
            tickers = data.get('data', [])
            usdt_pairs = [t for t in tickers if t.get('instId', '').endswith('-USDT')]
            usdt_pairs.sort(key=lambda x: float(x.get('volCcy24h', 0)), reverse=True)
            return usdt_pairs[:50]
        return []
    
    async def fetch_funding_rates(self) -> Dict[str, float]:
        """Fetch OKX funding rates"""
        data = await self._fetch_with_retry(f"{OKX_API}/api/v5/public/funding-rate", {"instType": "SWAP"})
        if data and data.get('code') == '0':
            rates = data.get('data', [])
            return {r['instId']: float(r.get('fundingRate', 0)) for r in rates}
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


class HyperLiquidDataFetcher:
    """Fetches data from HyperLiquid REST API"""
    
    HYPERLIQUID_API = "https://api.hyperliquid.xyz"
    
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
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        return False
    
    async def fetch_futures_tickers(self) -> List[dict]:
        """Fetch HyperLiquid perpetual market data"""
        session = await self.get_session()
        try:
            # Get all mids (prices) and meta info
            async with session.post(f"{self.HYPERLIQUID_API}/info", json={"type": "allMids"}) as resp:
                if resp.status == 200:
                    mids = await resp.json()
                else:
                    return []
            
            # Get asset contexts (24h volume, funding, OI)
            async with session.post(f"{self.HYPERLIQUID_API}/info", json={"type": "metaAndAssetCtxs"}) as resp:
                if resp.status == 200:
                    meta_data = await resp.json()
                else:
                    return []
            
            # Parse meta and asset contexts
            meta = meta_data[0] if len(meta_data) > 0 else {}
            asset_ctxs = meta_data[1] if len(meta_data) > 1 else []
            universe = meta.get('universe', [])
            
            tickers = []
            for i, asset in enumerate(universe):
                symbol = asset.get('name', '')
                if not symbol:
                    continue
                    
                # Get price from mids
                price = float(mids.get(symbol, 0))
                
                # Get asset context data
                ctx = asset_ctxs[i] if i < len(asset_ctxs) else {}
                
                ticker = {
                    'symbol': f"{symbol}USDT",  # Normalize to USDT format
                    'lastPrice': price,
                    'dayNtlVlm': float(ctx.get('dayNtlVlm', 0)),  # 24h volume in USD
                    'funding': float(ctx.get('funding', 0)),
                    'openInterest': float(ctx.get('openInterest', 0)),
                    'prevDayPx': float(ctx.get('prevDayPx', 0)),
                    'markPx': float(ctx.get('markPx', price)),
                    'oraclePx': float(ctx.get('oraclePx', price)),
                }
                tickers.append(ticker)
            
            # Sort by volume
            tickers.sort(key=lambda x: x.get('dayNtlVlm', 0), reverse=True)
            return tickers[:50]
            
        except Exception as e:
            logger.error(f"Error fetching HyperLiquid tickers: {e}")
            return []
    
    async def fetch_spot_tickers(self) -> List[dict]:
        """HyperLiquid is perps only - return empty for spot"""
        return []
    
    async def fetch_funding_rates(self) -> Dict[str, float]:
        """Extract funding rates from meta data"""
        session = await self.get_session()
        try:
            async with session.post(f"{self.HYPERLIQUID_API}/info", json={"type": "metaAndAssetCtxs"}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    meta = data[0] if len(data) > 0 else {}
                    asset_ctxs = data[1] if len(data) > 1 else []
                    universe = meta.get('universe', [])
                    
                    rates = {}
                    for i, asset in enumerate(universe):
                        symbol = asset.get('name', '')
                        if i < len(asset_ctxs):
                            rates[f"{symbol}USDT"] = float(asset_ctxs[i].get('funding', 0))
                    return rates
                return {}
        except Exception as e:
            logger.error(f"Error fetching HyperLiquid funding rates: {e}")
            return {}
    
    def process_ticker(self, ticker: dict, funding_rates: Dict[str, float]) -> dict:
        """Process HyperLiquid ticker to unified format"""
        from datetime import datetime
        
        symbol = ticker.get('symbol', '')
        price = float(ticker.get('lastPrice', 0) or ticker.get('markPx', 0))
        prev_price = float(ticker.get('prevDayPx', 0))
        volume = float(ticker.get('dayNtlVlm', 0))
        oi = float(ticker.get('openInterest', 0))
        funding = float(ticker.get('funding', 0))
        
        # Calculate 24h change
        change_24h = ((price - prev_price) / prev_price * 100) if prev_price > 0 else 0
        
        # Approximate shorter timeframes
        change_1h = change_24h / 24 if change_24h else 0
        change_15m = change_1h / 4 if change_1h else 0
        change_5m = change_15m / 3 if change_15m else 0
        change_1m = change_5m / 5 if change_5m else 0
        change_30m = change_15m * 2 if change_15m else 0
        change_4h = change_1h * 4 if change_1h else 0
        change_8h = change_4h * 2 if change_4h else 0
        
        # Volume approximations
        volume_1m = volume / 24 / 60
        volume_5m = volume / 24 / 12
        volume_15m = volume / 24 / 4
        volume_30m = volume / 24 / 2
        volume_1h = volume / 24
        volume_4h = volume / 6
        volume_8h = volume / 3
        
        # OI changes approximation
        oi_change_1m = change_1m * 0.8
        oi_change_5m = change_5m * 0.8
        oi_change_15m = change_15m * 0.8
        oi_change_30m = change_30m * 0.8
        oi_change_1h = change_1h * 0.8
        oi_change_4h = change_4h * 0.8
        oi_change_8h = change_8h * 0.8
        oi_change_1d = change_24h * 0.8
        
        # Volatility approximation (simplified)
        volatility_base = abs(change_24h) * 0.1
        volatility_1m = volatility_base / 24 / 60
        volatility_5m = volatility_base / 24 / 12
        volatility_15m = volatility_base / 24 / 4
        volatility_30m = volatility_base / 24 / 2
        volatility_1h = volatility_base / 24
        
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
            "high_24h": price * 1.01,  # Approximation
            "low_24h": price * 0.99,
            "open_interest": oi,
            "oi_change_1m": round(oi_change_1m, 2),
            "oi_change_5m": round(oi_change_5m, 2),
            "oi_change_15m": round(oi_change_15m, 2),
            "oi_change_30m": round(oi_change_30m, 2),
            "oi_change_1h": round(oi_change_1h, 2),
            "oi_change_4h": round(oi_change_4h, 2),
            "oi_change_8h": round(oi_change_8h, 2),
            "oi_change_1d": round(oi_change_1d, 2),
            "funding_rate": funding,
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
    elif exchange == 'hyperliquid':
        return HyperLiquidDataFetcher()
    else:
        # Return Binance fetcher (imported in screener_ws.py)
        return None  # Will use BinanceDataFetcher from screener_ws
