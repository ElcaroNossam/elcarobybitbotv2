"""
ElCaro Orderbook & Market Microstructure Analysis
Real-time orderbook data fetching and analysis for realistic backtesting

Features:
- Orderbook depth analysis
- Liquidity profiling
- Slippage calculation based on real market depth
- Market impact modeling
- Order flow imbalance
"""
import aiohttp
import asyncio
import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class OrderbookLevel:
    """Single orderbook level"""
    price: float
    quantity: float
    cumulative_quantity: float = 0.0
    
    @property
    def notional_value(self) -> float:
        return self.price * self.quantity


@dataclass
class OrderbookSnapshot:
    """Complete orderbook snapshot"""
    symbol: str
    timestamp: datetime
    bids: List[OrderbookLevel]
    asks: List[OrderbookLevel]
    
    @property
    def best_bid(self) -> Optional[OrderbookLevel]:
        return self.bids[0] if self.bids else None
    
    @property
    def best_ask(self) -> Optional[OrderbookLevel]:
        return self.asks[0] if self.asks else None
    
    @property
    def spread_percent(self) -> float:
        if self.best_bid and self.best_ask:
            return 100 * (self.best_ask.price - self.best_bid.price) / self.best_bid.price
        return 0.0
    
    @property
    def mid_price(self) -> float:
        if self.best_bid and self.best_ask:
            return (self.best_bid.price + self.best_ask.price) / 2
        return 0.0


class OrderbookAnalyzer:
    """Analyze orderbook data for realistic execution modeling"""
    
    def __init__(self, cache_ttl: int = 5):
        self._cache: Dict[str, Tuple[OrderbookSnapshot, float]] = {}
        self._cache_ttl = cache_ttl
    
    async def fetch_orderbook(self, symbol: str, exchange: str = "binance", depth: int = 100) -> Optional[OrderbookSnapshot]:
        """
        Fetch real-time orderbook from exchange
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            exchange: Exchange name (binance, bybit)
            depth: Number of levels to fetch
        """
        # Check cache
        cache_key = f"{exchange}:{symbol}"
        if cache_key in self._cache:
            snapshot, cached_time = self._cache[cache_key]
            if (datetime.now().timestamp() - cached_time) < self._cache_ttl:
                return snapshot
        
        try:
            if exchange.lower() == "binance":
                url = f"https://fapi.binance.com/fapi/v1/depth?symbol={symbol}&limit={depth}"
            elif exchange.lower() == "bybit":
                url = f"https://api.bybit.com/v5/market/orderbook?category=linear&symbol={symbol}&limit={depth}"
            else:
                return None
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return None
                    
                    data = await resp.json()
                    
                    if exchange.lower() == "binance":
                        bids_data = data.get("bids", [])
                        asks_data = data.get("asks", [])
                    else:  # bybit
                        result = data.get("result", {})
                        bids_data = result.get("b", [])
                        asks_data = result.get("a", [])
                    
                    # Parse bids
                    bids = []
                    cumulative_qty = 0.0
                    for price_str, qty_str in bids_data:
                        price = float(price_str)
                        qty = float(qty_str)
                        cumulative_qty += qty
                        bids.append(OrderbookLevel(price, qty, cumulative_qty))
                    
                    # Parse asks
                    asks = []
                    cumulative_qty = 0.0
                    for price_str, qty_str in asks_data:
                        price = float(price_str)
                        qty = float(qty_str)
                        cumulative_qty += qty
                        asks.append(OrderbookLevel(price, qty, cumulative_qty))
                    
                    snapshot = OrderbookSnapshot(
                        symbol=symbol,
                        timestamp=datetime.now(),
                        bids=bids,
                        asks=asks
                    )
                    
                    # Cache the snapshot
                    self._cache[cache_key] = (snapshot, datetime.now().timestamp())
                    
                    return snapshot
        
        except Exception as e:
            print(f"Error fetching orderbook for {symbol}: {e}")
            return None
    
    def calculate_slippage(self, snapshot: OrderbookSnapshot, side: str, size_usd: float) -> Dict[str, float]:
        """
        Calculate realistic slippage based on orderbook depth
        
        Args:
            snapshot: Orderbook snapshot
            side: 'buy' or 'sell'
            size_usd: Order size in USD
        
        Returns:
            Dict with slippage metrics
        """
        if not snapshot:
            return {"slippage_percent": 0.5, "avg_price": 0.0, "worst_price": 0.0}
        
        # Select appropriate side
        levels = snapshot.asks if side.lower() == "buy" else snapshot.bids
        
        if not levels:
            return {"slippage_percent": 0.5, "avg_price": 0.0, "worst_price": 0.0}
        
        reference_price = levels[0].price
        remaining_usd = size_usd
        total_qty = 0.0
        weighted_price_sum = 0.0
        worst_price = reference_price
        
        for level in levels:
            if remaining_usd <= 0:
                break
            
            # How much can we fill at this level
            level_value = level.price * level.quantity
            fillable_value = min(remaining_usd, level_value)
            fillable_qty = fillable_value / level.price
            
            weighted_price_sum += level.price * fillable_qty
            total_qty += fillable_qty
            worst_price = level.price
            remaining_usd -= fillable_value
        
        if total_qty == 0:
            return {"slippage_percent": 1.0, "avg_price": reference_price, "worst_price": reference_price}
        
        avg_price = weighted_price_sum / total_qty
        
        # Calculate slippage
        if side.lower() == "buy":
            slippage_percent = 100 * (avg_price - reference_price) / reference_price
        else:
            slippage_percent = 100 * (reference_price - avg_price) / reference_price
        
        return {
            "slippage_percent": abs(slippage_percent),
            "avg_price": avg_price,
            "worst_price": worst_price,
            "fully_filled": remaining_usd <= 0,
            "partial_fill_percent": 100 * (1 - remaining_usd / size_usd) if size_usd > 0 else 100
        }
    
    def calculate_liquidity_score(self, snapshot: OrderbookSnapshot, depth_levels: int = 20) -> Dict[str, float]:
        """
        Calculate liquidity score based on orderbook depth
        
        Returns:
            Liquidity metrics
        """
        if not snapshot or not snapshot.bids or not snapshot.asks:
            return {"score": 0.0, "bid_liquidity": 0.0, "ask_liquidity": 0.0, "imbalance": 0.0}
        
        # Calculate bid side liquidity (top N levels)
        bid_liquidity = sum(level.price * level.quantity for level in snapshot.bids[:depth_levels])
        
        # Calculate ask side liquidity
        ask_liquidity = sum(level.price * level.quantity for level in snapshot.asks[:depth_levels])
        
        # Total liquidity
        total_liquidity = bid_liquidity + ask_liquidity
        
        # Order book imbalance (positive = more buy pressure)
        if total_liquidity > 0:
            imbalance = (bid_liquidity - ask_liquidity) / total_liquidity
        else:
            imbalance = 0.0
        
        # Liquidity score (0-100)
        # Based on total liquidity and spread
        spread = snapshot.spread_percent
        
        # Higher liquidity = higher score, lower spread = higher score
        if spread > 0:
            score = min(100, (total_liquidity / 1000000) * 10 * (1 / (1 + spread)))
        else:
            score = 0
        
        return {
            "score": score,
            "bid_liquidity_usd": bid_liquidity,
            "ask_liquidity_usd": ask_liquidity,
            "total_liquidity_usd": total_liquidity,
            "imbalance": imbalance,
            "spread_percent": spread
        }
    
    def estimate_market_impact(self, snapshot: OrderbookSnapshot, side: str, size_usd: float) -> float:
        """
        Estimate market impact as percentage price movement
        
        Based on Kyle's lambda model simplified
        """
        liquidity_metrics = self.calculate_liquidity_score(snapshot)
        total_liquidity = liquidity_metrics["total_liquidity_usd"]
        
        if total_liquidity == 0:
            return 1.0  # 1% impact if no liquidity data
        
        # Market impact factor (empirical)
        # Impact increases non-linearly with order size relative to liquidity
        size_ratio = size_usd / total_liquidity
        
        # Kyle's lambda approximation: impact = lambda * sqrt(size)
        lambda_factor = 0.5  # Adjustable based on market
        impact_percent = lambda_factor * math.sqrt(size_ratio) * 100
        
        return min(impact_percent, 10.0)  # Cap at 10%
    
    def get_execution_price(
        self,
        snapshot: OrderbookSnapshot,
        side: str,
        size_usd: float,
        order_type: str = "market"
    ) -> Dict[str, Any]:
        """
        Get realistic execution price considering slippage and market impact
        
        Args:
            snapshot: Orderbook snapshot
            side: 'buy' or 'sell'
            size_usd: Order size in USD
            order_type: 'market' or 'limit'
        
        Returns:
            Complete execution analysis
        """
        if not snapshot:
            return {
                "execution_price": 0.0,
                "slippage_percent": 0.5,
                "market_impact_percent": 0.5,
                "total_cost_percent": 1.0,
                "liquidity_sufficient": False
            }
        
        slippage = self.calculate_slippage(snapshot, side, size_usd)
        market_impact = self.estimate_market_impact(snapshot, side, size_usd)
        
        # For market orders, use average filled price + impact
        if order_type.lower() == "market":
            base_price = slippage["avg_price"]
            
            # Apply market impact
            if side.lower() == "buy":
                execution_price = base_price * (1 + market_impact / 100)
            else:
                execution_price = base_price * (1 - market_impact / 100)
            
            total_cost = slippage["slippage_percent"] + market_impact
        else:
            # Limit orders get filled at limit price (if liquidity allows)
            execution_price = snapshot.best_bid.price if side.lower() == "sell" else snapshot.best_ask.price
            total_cost = 0.1  # Minimal cost for limit orders
        
        return {
            "execution_price": execution_price,
            "reference_price": snapshot.mid_price,
            "slippage_percent": slippage["slippage_percent"],
            "market_impact_percent": market_impact,
            "total_cost_percent": total_cost,
            "liquidity_sufficient": slippage["fully_filled"],
            "partial_fill_percent": slippage.get("partial_fill_percent", 100),
            "spread_percent": snapshot.spread_percent
        }


class BacktestOrderbookSimulator:
    """
    Simulate orderbook for historical backtesting
    Uses statistical modeling when real orderbook data is unavailable
    """
    
    def __init__(self):
        self.analyzer = OrderbookAnalyzer()
    
    def generate_synthetic_orderbook(
        self,
        mid_price: float,
        volume_24h: float,
        volatility: float = 0.01
    ) -> OrderbookSnapshot:
        """
        Generate synthetic orderbook based on market conditions
        
        Args:
            mid_price: Current market price
            volume_24h: 24h trading volume
            volatility: Price volatility (as decimal)
        """
        # Estimate liquidity based on volume
        avg_order_size = volume_24h / 1000  # Assume 1000 orders per day
        
        # Generate spread based on volatility
        spread_bps = max(1, int(volatility * 10000))  # Basis points
        spread_percent = spread_bps / 10000
        
        bid_price = mid_price * (1 - spread_percent / 2)
        ask_price = mid_price * (1 + spread_percent / 2)
        
        # Generate orderbook levels with exponential decay
        bids = []
        asks = []
        
        num_levels = 50
        
        for i in range(num_levels):
            # Bids
            price_offset = (i * spread_percent * 2)
            bid_level_price = bid_price * (1 - price_offset)
            
            # Quantity decreases exponentially with distance from mid
            base_qty = avg_order_size / mid_price
            qty = base_qty * math.exp(-i * 0.1)
            
            cumulative_bid_qty = sum(level.quantity for level in bids) + qty
            bids.append(OrderbookLevel(bid_level_price, qty, cumulative_bid_qty))
            
            # Asks
            ask_level_price = ask_price * (1 + price_offset)
            cumulative_ask_qty = sum(level.quantity for level in asks) + qty
            asks.append(OrderbookLevel(ask_level_price, qty, cumulative_ask_qty))
        
        return OrderbookSnapshot(
            symbol="SYNTHETIC",
            timestamp=datetime.now(),
            bids=bids,
            asks=asks
        )
    
    async def get_orderbook_for_backtest(
        self,
        symbol: str,
        price: float,
        volume_24h: float,
        volatility: float,
        use_real_data: bool = False
    ) -> OrderbookSnapshot:
        """
        Get orderbook for backtest - real if available, synthetic otherwise
        """
        if use_real_data:
            # Try to fetch real data
            real_book = await self.analyzer.fetch_orderbook(symbol, "binance", 100)
            if real_book:
                return real_book
        
        # Fall back to synthetic
        return self.generate_synthetic_orderbook(price, volume_24h, volatility)
    
    def calculate_realistic_fill(
        self,
        orderbook: OrderbookSnapshot,
        side: str,
        size_usd: float,
        order_type: str = "market",
        limit_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate realistic order fill considering:
        - Slippage
        - Market impact
        - Partial fills
        - Order type
        """
        execution = self.analyzer.get_execution_price(orderbook, side, size_usd, order_type)
        
        # For limit orders, check if price reaches limit
        if order_type.lower() == "limit" and limit_price:
            if side.lower() == "buy":
                # Buy limit only fills if market goes to or below limit
                if orderbook.best_ask.price > limit_price:
                    execution["filled"] = False
                    execution["execution_price"] = limit_price
                else:
                    execution["filled"] = True
            else:
                # Sell limit only fills if market goes to or above limit
                if orderbook.best_bid.price < limit_price:
                    execution["filled"] = False
                    execution["execution_price"] = limit_price
                else:
                    execution["filled"] = True
        else:
            execution["filled"] = execution["liquidity_sufficient"]
        
        return execution


# Global instances
orderbook_analyzer = OrderbookAnalyzer()
backtest_orderbook_simulator = BacktestOrderbookSimulator()
