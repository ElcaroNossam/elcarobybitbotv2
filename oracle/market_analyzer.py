"""
Oracle Market Analyzer
======================

Real-time and historical market data analysis:
- Price/Volume metrics
- Volatility analysis
- Correlation with BTC/ETH
- Liquidity depth
- Trading patterns

Data Sources:
- CoinGecko API
- CoinMarketCap API
- DEX aggregators
- CEX APIs
"""

import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import statistics

from oracle.core import MarketData

logger = logging.getLogger("oracle.market")


@dataclass
class OHLCV:
    """Candlestick data"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class LiquidityData:
    """DEX/CEX liquidity metrics"""
    total_liquidity_usd: float = 0.0
    dex_liquidity_usd: float = 0.0
    cex_liquidity_usd: float = 0.0
    bid_depth_2pct: float = 0.0  # Buy orders within 2%
    ask_depth_2pct: float = 0.0  # Sell orders within 2%
    slippage_1k_usd: float = 0.0  # Slippage for $1k trade
    slippage_10k_usd: float = 0.0  # Slippage for $10k trade
    slippage_100k_usd: float = 0.0  # Slippage for $100k trade


class MarketAnalyzer:
    """
    Market Data Analysis Engine
    
    Fetches and analyzes real-time market data for crypto assets.
    """
    
    COINGECKO_BASE = "https://api.coingecko.com/api/v3"
    CMC_BASE = "https://pro-api.coinmarketcap.com/v1"
    
    # Cache duration
    CACHE_TTL = 300  # 5 minutes
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.session: Optional[aiohttp.ClientSession] = None
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        
        # API keys
        self.cmc_api_key = self.config.get("cmc_api_key")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.CACHE_TTL):
                return value
        return None
    
    def _set_cached(self, key: str, value: Any):
        """Cache value"""
        self._cache[key] = (value, datetime.now())
    
    async def analyze(
        self,
        token_id: Optional[str] = None,
        contract_address: Optional[str] = None,
        chain: str = "ethereum"
    ) -> MarketData:
        """
        Analyze market data for a token.
        
        Args:
            token_id: CoinGecko token ID
            contract_address: Token contract address
            chain: Blockchain (ethereum, bsc, polygon, etc.)
        
        Returns:
            MarketData with analysis results
        """
        market = MarketData()
        
        if not token_id and not contract_address:
            logger.warning("No token_id or contract_address provided")
            return market
        
        try:
            # Get basic market data
            if token_id:
                basic_data = await self._fetch_coingecko_data(token_id)
            elif contract_address:
                basic_data = await self._fetch_coingecko_contract(contract_address, chain)
            else:
                basic_data = {}
            
            if basic_data:
                market.price_usd = basic_data.get("current_price", 0)
                market.market_cap_usd = basic_data.get("market_cap", 0)
                market.volume_24h_usd = basic_data.get("total_volume", 0)
                market.price_change_24h_pct = basic_data.get("price_change_percentage_24h", 0)
                market.price_change_7d_pct = basic_data.get("price_change_percentage_7d", 0)
                market.price_change_30d_pct = basic_data.get("price_change_percentage_30d", 0)
                market.ath_usd = basic_data.get("ath", 0)
                market.ath_date = basic_data.get("ath_date", "")
                market.atl_usd = basic_data.get("atl", 0)
                
                # Calculate drawdown from ATH
                if market.ath_usd > 0 and market.price_usd > 0:
                    market.ath_drawdown_pct = (
                        (market.ath_usd - market.price_usd) / market.ath_usd * 100
                    )
            
            # Get historical data for volatility calculation
            if token_id:
                historical = await self._fetch_historical_prices(token_id, days=30)
                if historical:
                    market.volatility_30d = self._calculate_volatility(historical)
                    market.sharpe_ratio_30d = self._calculate_sharpe(historical)
                
                # Get BTC correlation
                btc_historical = await self._fetch_historical_prices("bitcoin", days=30)
                if btc_historical and historical:
                    market.btc_correlation_30d = self._calculate_correlation(
                        historical, btc_historical
                    )
            
            # Calculate market cap rank
            if market.market_cap_usd > 0:
                market.mcap_rank = await self._get_mcap_rank(market.market_cap_usd)
            
            # Volume to MCap ratio
            if market.market_cap_usd > 0:
                market.volume_mcap_ratio = market.volume_24h_usd / market.market_cap_usd
            
            # Calculate scores
            market.liquidity_score = self._calculate_liquidity_score(market)
            market.momentum_score = self._calculate_momentum_score(market)
            
            logger.info(
                f"Market analysis complete: ${market.price_usd:.4f}, "
                f"MCap: ${market.market_cap_usd:,.0f}"
            )
            
        except Exception as e:
            logger.error(f"Market analysis error: {e}")
        
        return market
    
    async def _fetch_coingecko_data(self, token_id: str) -> Dict:
        """Fetch token data from CoinGecko"""
        cache_key = f"cg_{token_id}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        session = await self._get_session()
        
        try:
            url = f"{self.COINGECKO_BASE}/coins/markets"
            params = {
                "vs_currency": "usd",
                "ids": token_id,
                "order": "market_cap_desc",
                "sparkline": "false",
                "price_change_percentage": "24h,7d,30d"
            }
            
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and len(data) > 0:
                        self._set_cached(cache_key, data[0])
                        return data[0]
        except Exception as e:
            logger.error(f"CoinGecko API error: {e}")
        
        return {}
    
    async def _fetch_coingecko_contract(self, address: str, chain: str) -> Dict:
        """Fetch token data by contract address"""
        cache_key = f"cg_contract_{chain}_{address}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        session = await self._get_session()
        
        # Map chain names to CoinGecko platform IDs
        chain_map = {
            "ethereum": "ethereum",
            "eth": "ethereum",
            "bsc": "binance-smart-chain",
            "polygon": "polygon-pos",
            "arbitrum": "arbitrum-one",
            "optimism": "optimistic-ethereum",
            "avalanche": "avalanche",
            "solana": "solana",
        }
        
        platform = chain_map.get(chain.lower(), chain)
        
        try:
            url = f"{self.COINGECKO_BASE}/coins/{platform}/contract/{address.lower()}"
            
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    # Extract market data
                    market_data = data.get("market_data", {})
                    result = {
                        "current_price": market_data.get("current_price", {}).get("usd", 0),
                        "market_cap": market_data.get("market_cap", {}).get("usd", 0),
                        "total_volume": market_data.get("total_volume", {}).get("usd", 0),
                        "price_change_percentage_24h": market_data.get("price_change_percentage_24h", 0),
                        "price_change_percentage_7d": market_data.get("price_change_percentage_7d", 0),
                        "price_change_percentage_30d": market_data.get("price_change_percentage_30d", 0),
                        "ath": market_data.get("ath", {}).get("usd", 0),
                        "ath_date": market_data.get("ath_date", {}).get("usd", ""),
                        "atl": market_data.get("atl", {}).get("usd", 0),
                    }
                    self._set_cached(cache_key, result)
                    return result
        except Exception as e:
            logger.error(f"CoinGecko contract API error: {e}")
        
        return {}
    
    async def _fetch_historical_prices(
        self,
        token_id: str,
        days: int = 30
    ) -> List[float]:
        """Fetch historical prices for analysis"""
        cache_key = f"cg_history_{token_id}_{days}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        session = await self._get_session()
        
        try:
            url = f"{self.COINGECKO_BASE}/coins/{token_id}/market_chart"
            params = {
                "vs_currency": "usd",
                "days": days,
                "interval": "daily"
            }
            
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    prices = [p[1] for p in data.get("prices", [])]
                    self._set_cached(cache_key, prices)
                    return prices
        except Exception as e:
            logger.error(f"Historical prices error: {e}")
        
        return []
    
    async def _get_mcap_rank(self, market_cap: float) -> int:
        """Estimate market cap rank"""
        # Rough estimation based on market cap tiers
        if market_cap >= 100_000_000_000:  # $100B+
            return 1
        elif market_cap >= 50_000_000_000:  # $50B+
            return 5
        elif market_cap >= 10_000_000_000:  # $10B+
            return 20
        elif market_cap >= 1_000_000_000:  # $1B+
            return 50
        elif market_cap >= 500_000_000:  # $500M+
            return 100
        elif market_cap >= 100_000_000:  # $100M+
            return 200
        elif market_cap >= 50_000_000:  # $50M+
            return 300
        elif market_cap >= 10_000_000:  # $10M+
            return 500
        else:
            return 1000
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate 30-day volatility (annualized)"""
        if len(prices) < 2:
            return 0.0
        
        # Calculate daily returns
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                daily_return = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(daily_return)
        
        if not returns:
            return 0.0
        
        # Standard deviation of returns
        std_dev = statistics.stdev(returns) if len(returns) > 1 else 0
        
        # Annualize (sqrt(365) for daily data)
        annualized_vol = std_dev * (365 ** 0.5) * 100
        
        return round(annualized_vol, 2)
    
    def _calculate_sharpe(self, prices: List[float], risk_free_rate: float = 0.05) -> float:
        """Calculate Sharpe ratio (simplified)"""
        if len(prices) < 2:
            return 0.0
        
        # Calculate returns
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                daily_return = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(daily_return)
        
        if not returns:
            return 0.0
        
        mean_return = statistics.mean(returns)
        std_dev = statistics.stdev(returns) if len(returns) > 1 else 0.01
        
        # Annualize
        annualized_return = mean_return * 365
        annualized_std = std_dev * (365 ** 0.5)
        
        if annualized_std == 0:
            return 0.0
        
        sharpe = (annualized_return - risk_free_rate) / annualized_std
        
        return round(sharpe, 2)
    
    def _calculate_correlation(
        self,
        prices1: List[float],
        prices2: List[float]
    ) -> float:
        """Calculate price correlation between two assets"""
        if len(prices1) < 3 or len(prices2) < 3:
            return 0.0
        
        # Align lengths
        min_len = min(len(prices1), len(prices2))
        prices1 = prices1[:min_len]
        prices2 = prices2[:min_len]
        
        # Calculate returns
        returns1 = [
            (prices1[i] - prices1[i-1]) / prices1[i-1]
            for i in range(1, len(prices1))
            if prices1[i-1] > 0
        ]
        returns2 = [
            (prices2[i] - prices2[i-1]) / prices2[i-1]
            for i in range(1, len(prices2))
            if prices2[i-1] > 0
        ]
        
        if len(returns1) < 3 or len(returns2) < 3:
            return 0.0
        
        # Align again
        min_len = min(len(returns1), len(returns2))
        returns1 = returns1[:min_len]
        returns2 = returns2[:min_len]
        
        # Calculate correlation
        mean1 = statistics.mean(returns1)
        mean2 = statistics.mean(returns2)
        
        numerator = sum(
            (r1 - mean1) * (r2 - mean2)
            for r1, r2 in zip(returns1, returns2)
        )
        
        std1 = statistics.stdev(returns1)
        std2 = statistics.stdev(returns2)
        
        if std1 == 0 or std2 == 0:
            return 0.0
        
        denominator = (len(returns1) - 1) * std1 * std2
        
        correlation = numerator / denominator if denominator > 0 else 0
        
        return round(correlation, 2)
    
    def _calculate_liquidity_score(self, market: MarketData) -> float:
        """Score liquidity (0-100)"""
        score = 0.0
        
        # Volume to MCap ratio (higher = more liquid)
        ratio = market.volume_mcap_ratio
        if ratio >= 0.5:
            score += 40
        elif ratio >= 0.2:
            score += 30
        elif ratio >= 0.1:
            score += 20
        elif ratio >= 0.05:
            score += 10
        
        # Absolute volume
        vol = market.volume_24h_usd
        if vol >= 100_000_000:
            score += 40
        elif vol >= 10_000_000:
            score += 30
        elif vol >= 1_000_000:
            score += 20
        elif vol >= 100_000:
            score += 10
        
        # Market cap (larger = more stable liquidity)
        mcap = market.market_cap_usd
        if mcap >= 1_000_000_000:
            score += 20
        elif mcap >= 100_000_000:
            score += 15
        elif mcap >= 10_000_000:
            score += 10
        elif mcap >= 1_000_000:
            score += 5
        
        return min(100, score)
    
    def _calculate_momentum_score(self, market: MarketData) -> float:
        """Score price momentum (0-100, 50 = neutral)"""
        score = 50.0
        
        # 24h change
        change_24h = market.price_change_24h_pct
        if change_24h > 20:
            score += 15
        elif change_24h > 10:
            score += 10
        elif change_24h > 5:
            score += 5
        elif change_24h < -20:
            score -= 15
        elif change_24h < -10:
            score -= 10
        elif change_24h < -5:
            score -= 5
        
        # 7d change
        change_7d = market.price_change_7d_pct
        if change_7d > 30:
            score += 20
        elif change_7d > 15:
            score += 15
        elif change_7d > 5:
            score += 10
        elif change_7d < -30:
            score -= 20
        elif change_7d < -15:
            score -= 15
        elif change_7d < -5:
            score -= 10
        
        # 30d change
        change_30d = market.price_change_30d_pct
        if change_30d > 50:
            score += 15
        elif change_30d > 20:
            score += 10
        elif change_30d > 0:
            score += 5
        elif change_30d < -50:
            score -= 15
        elif change_30d < -20:
            score -= 10
        elif change_30d < 0:
            score -= 5
        
        return max(0, min(100, score))


async def test():
    """Test market analyzer"""
    analyzer = MarketAnalyzer()
    
    try:
        # Test with Bitcoin
        print("Analyzing Bitcoin...")
        result = await analyzer.analyze(token_id="bitcoin")
        
        print(f"Price: ${result.price_usd:,.2f}")
        print(f"Market Cap: ${result.market_cap_usd:,.0f}")
        print(f"24h Volume: ${result.volume_24h_usd:,.0f}")
        print(f"30d Volatility: {result.volatility_30d:.2f}%")
        print(f"BTC Correlation: {result.btc_correlation_30d}")
        print(f"Liquidity Score: {result.liquidity_score:.0f}")
        print(f"Momentum Score: {result.momentum_score:.0f}")
        
    finally:
        await analyzer.close()


if __name__ == "__main__":
    asyncio.run(test())
