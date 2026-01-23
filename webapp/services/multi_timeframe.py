"""
Lyxen Multi-Timeframe Analysis System
Analyze multiple timeframes simultaneously for better trading decisions

Features:
- Automatic timeframe alignment
- Trend cascade detection
- Multi-TF indicator synchronization
- Higher timeframe filters
- Conflux zones (multiple TF confluence)
"""
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class TrendDirection(Enum):
    STRONG_BULLISH = "strong_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    STRONG_BEARISH = "strong_bearish"


@dataclass
class TimeframeData:
    """Data for a single timeframe"""
    timeframe: str
    candles: List[Dict]
    trend: TrendDirection
    indicators: Dict[str, Any]
    support_levels: List[float]
    resistance_levels: List[float]
    
    @property
    def current_price(self) -> float:
        return self.candles[-1]["close"] if self.candles else 0.0


@dataclass
class MultiTimeframeSignal:
    """Combined multi-timeframe signal"""
    primary_tf: str
    direction: str  # LONG, SHORT, NEUTRAL
    strength: float  # 0-100
    confluences: List[str]
    divergences: List[str]
    timeframe_alignment: Dict[str, str]  # TF -> trend
    entry_conditions_met: bool
    higher_tf_filter_passed: bool
    

class TimeframeConverter:
    """Convert between timeframe formats"""
    
    TIMEFRAME_MINUTES = {
        "1m": 1,
        "3m": 3,
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "1h": 60,
        "2h": 120,
        "4h": 240,
        "6h": 360,
        "12h": 720,
        "1d": 1440,
        "1w": 10080
    }
    
    @staticmethod
    def to_minutes(timeframe: str) -> int:
        """Convert timeframe string to minutes"""
        return TimeframeConverter.TIMEFRAME_MINUTES.get(timeframe, 60)
    
    @staticmethod
    def get_higher_timeframes(base_tf: str, count: int = 3) -> List[str]:
        """Get N higher timeframes from base"""
        all_tfs = list(TimeframeConverter.TIMEFRAME_MINUTES.keys())
        base_minutes = TimeframeConverter.to_minutes(base_tf)
        
        higher = [tf for tf in all_tfs if TimeframeConverter.to_minutes(tf) > base_minutes]
        return sorted(higher, key=lambda x: TimeframeConverter.to_minutes(x))[:count]
    
    @staticmethod
    def is_aligned(lower_tf: str, higher_tf: str) -> bool:
        """Check if timeframes are properly aligned (higher is multiple of lower)"""
        lower_min = TimeframeConverter.to_minutes(lower_tf)
        higher_min = TimeframeConverter.to_minutes(higher_tf)
        
        return higher_min % lower_min == 0


class MultiTimeframeAnalyzer:
    """Analyze multiple timeframes simultaneously"""
    
    def __init__(self):
        self.converter = TimeframeConverter()
        self._cache: Dict[str, Tuple[List[Dict], float]] = {}
        self._cache_ttl = 60  # 1 minute
    
    async def fetch_multiple_timeframes(
        self,
        symbol: str,
        timeframes: List[str],
        exchange: str = "binance"
    ) -> Dict[str, List[Dict]]:
        """
        Fetch data for multiple timeframes in parallel
        
        Returns:
            Dict mapping timeframe -> candles
        """
        tasks = []
        for tf in timeframes:
            tasks.append(self._fetch_timeframe_data(symbol, tf, exchange))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        tf_data = {}
        for tf, data in zip(timeframes, results):
            if isinstance(data, list):
                tf_data[tf] = data
        
        return tf_data
    
    async def _fetch_timeframe_data(
        self,
        symbol: str,
        timeframe: str,
        exchange: str,
        limit: int = 500
    ) -> List[Dict]:
        """Fetch candles for single timeframe with caching"""
        cache_key = f"{exchange}:{symbol}:{timeframe}"
        
        # Check cache
        if cache_key in self._cache:
            data, cached_time = self._cache[cache_key]
            if (datetime.now().timestamp() - cached_time) < self._cache_ttl:
                return data
        
        # Fetch from API
        try:
            if exchange.lower() == "binance":
                url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={timeframe}&limit={limit}"
            else:
                return []
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return []
                    
                    raw_data = await resp.json()
                    
                    candles = [
                        {
                            "timestamp": k[0],
                            "time": datetime.fromtimestamp(k[0] / 1000).isoformat(),
                            "open": float(k[1]),
                            "high": float(k[2]),
                            "low": float(k[3]),
                            "close": float(k[4]),
                            "volume": float(k[5])
                        }
                        for k in raw_data
                    ]
                    
                    # Cache
                    self._cache[cache_key] = (candles, datetime.now().timestamp())
                    
                    return candles
        
        except Exception as e:
            print(f"Error fetching {timeframe} data for {symbol}: {e}")
            return []
    
    def detect_trend(self, candles: List[Dict], method: str = "ema") -> TrendDirection:
        """
        Detect trend direction on a timeframe
        
        Methods:
        - ema: EMA crossover (20/50/200)
        - swing: Swing highs/lows
        - adx: ADX strength
        """
        if not candles or len(candles) < 50:
            return TrendDirection.NEUTRAL
        
        closes = [c["close"] for c in candles]
        
        if method == "ema":
            # Simple EMA trend detection
            ema20 = self._calculate_ema(closes, 20)
            ema50 = self._calculate_ema(closes, 50)
            
            if not ema20 or not ema50:
                return TrendDirection.NEUTRAL
            
            current_price = closes[-1]
            
            if current_price > ema20[-1] > ema50[-1]:
                # Strong bullish
                return TrendDirection.STRONG_BULLISH if current_price > ema20[-1] * 1.02 else TrendDirection.BULLISH
            elif current_price < ema20[-1] < ema50[-1]:
                # Strong bearish
                return TrendDirection.STRONG_BEARISH if current_price < ema20[-1] * 0.98 else TrendDirection.BEARISH
            else:
                return TrendDirection.NEUTRAL
        
        return TrendDirection.NEUTRAL
    
    def _calculate_ema(self, data: List[float], period: int) -> List[float]:
        """Calculate EMA"""
        if len(data) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema = [sum(data[:period]) / period]
        
        for price in data[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        
        return [None] * (period - 1) + ema
    
    def find_support_resistance(self, candles: List[Dict], num_levels: int = 3) -> Tuple[List[float], List[float]]:
        """Find key support and resistance levels"""
        if not candles or len(candles) < 20:
            return [], []
        
        highs = [c["high"] for c in candles[-100:]]  # Last 100 candles
        lows = [c["low"] for c in candles[-100:]]
        
        # Find local peaks and valleys
        resistance_candidates = []
        support_candidates = []
        
        for i in range(2, len(highs) - 2):
            # Check for peaks
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                resistance_candidates.append(highs[i])
            
            # Check for valleys
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                support_candidates.append(lows[i])
        
        # Cluster nearby levels
        resistance_levels = self._cluster_levels(resistance_candidates, tolerance=0.005)
        support_levels = self._cluster_levels(support_candidates, tolerance=0.005)
        
        # Get top N
        resistance_levels = sorted(resistance_levels, reverse=True)[:num_levels]
        support_levels = sorted(support_levels, reverse=True)[:num_levels]
        
        return support_levels, resistance_levels
    
    def _cluster_levels(self, levels: List[float], tolerance: float = 0.005) -> List[float]:
        """Cluster price levels that are close together"""
        if not levels:
            return []
        
        sorted_levels = sorted(levels)
        clusters = []
        current_cluster = [sorted_levels[0]]
        
        for level in sorted_levels[1:]:
            if level - current_cluster[-1] <= current_cluster[-1] * tolerance:
                current_cluster.append(level)
            else:
                clusters.append(sum(current_cluster) / len(current_cluster))
                current_cluster = [level]
        
        clusters.append(sum(current_cluster) / len(current_cluster))
        
        return clusters
    
    async def analyze_all_timeframes(
        self,
        symbol: str,
        primary_tf: str,
        include_higher_tfs: int = 3
    ) -> Dict[str, TimeframeData]:
        """
        Analyze primary timeframe + higher timeframes
        
        Returns:
            Dict mapping timeframe -> TimeframeData
        """
        # Get timeframes to analyze
        timeframes = [primary_tf] + self.converter.get_higher_timeframes(primary_tf, include_higher_tfs)
        
        # Fetch all data in parallel
        tf_candles = await self.fetch_multiple_timeframes(symbol, timeframes)
        
        # Analyze each timeframe
        tf_data = {}
        
        for tf, candles in tf_candles.items():
            if not candles:
                continue
            
            trend = self.detect_trend(candles)
            support, resistance = self.find_support_resistance(candles)
            
            # Calculate key indicators
            closes = [c["close"] for c in candles]
            indicators = {
                "ema20": self._calculate_ema(closes, 20)[-1] if len(closes) >= 20 else None,
                "ema50": self._calculate_ema(closes, 50)[-1] if len(closes) >= 50 else None,
            }
            
            tf_data[tf] = TimeframeData(
                timeframe=tf,
                candles=candles,
                trend=trend,
                indicators=indicators,
                support_levels=support,
                resistance_levels=resistance
            )
        
        return tf_data
    
    def generate_signal(
        self,
        tf_data: Dict[str, TimeframeData],
        primary_tf: str
    ) -> MultiTimeframeSignal:
        """
        Generate trading signal from multi-timeframe analysis
        
        Logic:
        1. Primary TF generates entry signal
        2. Higher TFs act as filters
        3. All aligned = strong signal
        """
        if primary_tf not in tf_data:
            return MultiTimeframeSignal(
                primary_tf=primary_tf,
                direction="NEUTRAL",
                strength=0,
                confluences=[],
                divergences=[],
                timeframe_alignment={},
                entry_conditions_met=False,
                higher_tf_filter_passed=False
            )
        
        primary_data = tf_data[primary_tf]
        primary_trend = primary_data.trend
        
        # Check alignment with higher timeframes
        timeframe_alignment = {}
        for tf, data in tf_data.items():
            timeframe_alignment[tf] = data.trend.value
        
        # Count aligned timeframes
        confluences = []
        divergences = []
        
        for tf, trend in timeframe_alignment.items():
            if tf == primary_tf:
                continue
            
            if "bullish" in trend and "bullish" in primary_trend.value:
                confluences.append(f"{tf} aligned bullish")
            elif "bearish" in trend and "bearish" in primary_trend.value:
                confluences.append(f"{tf} aligned bearish")
            else:
                divergences.append(f"{tf} divergence ({trend})")
        
        # Calculate signal strength
        strength = len(confluences) / max(1, len(timeframe_alignment) - 1) * 100
        
        # Determine direction
        if "bullish" in primary_trend.value and len(confluences) >= len(divergences):
            direction = "LONG"
        elif "bearish" in primary_trend.value and len(confluences) >= len(divergences):
            direction = "SHORT"
        else:
            direction = "NEUTRAL"
        
        # Entry conditions
        entry_conditions_met = (
            direction != "NEUTRAL" and
            strength >= 60 and
            len(confluences) >= 2
        )
        
        # Higher TF filter
        higher_tfs = [tf for tf in timeframe_alignment.keys() 
                      if self.converter.to_minutes(tf) > self.converter.to_minutes(primary_tf)]
        
        higher_tf_filter_passed = True
        for tf in higher_tfs[:2]:  # Check top 2 higher TFs
            tf_trend = timeframe_alignment[tf]
            if direction == "LONG" and "bearish" in tf_trend:
                higher_tf_filter_passed = False
            elif direction == "SHORT" and "bullish" in tf_trend:
                higher_tf_filter_passed = False
        
        return MultiTimeframeSignal(
            primary_tf=primary_tf,
            direction=direction,
            strength=strength,
            confluences=confluences,
            divergences=divergences,
            timeframe_alignment=timeframe_alignment,
            entry_conditions_met=entry_conditions_met,
            higher_tf_filter_passed=higher_tf_filter_passed
        )
    
    def find_confluence_zones(
        self,
        tf_data: Dict[str, TimeframeData]
    ) -> List[Dict[str, Any]]:
        """
        Find price zones where multiple timeframes have support/resistance
        
        Returns:
            List of confluence zones with strength
        """
        all_levels = []
        
        # Collect all S/R levels from all timeframes
        for tf, data in tf_data.items():
            for level in data.support_levels + data.resistance_levels:
                all_levels.append({
                    "price": level,
                    "timeframe": tf,
                    "weight": 1.0 / self.converter.to_minutes(tf)  # Higher TF = more weight
                })
        
        if not all_levels:
            return []
        
        # Cluster levels (within 0.5%)
        tolerance = 0.005
        zones = []
        
        for level_data in all_levels:
            level = level_data["price"]
            
            # Find existing zone
            found = False
            for zone in zones:
                if abs(zone["price"] - level) / level <= tolerance:
                    zone["timeframes"].append(level_data["timeframe"])
                    zone["strength"] += level_data["weight"]
                    zone["price"] = (zone["price"] + level) / 2  # Average
                    found = True
                    break
            
            if not found:
                zones.append({
                    "price": level,
                    "timeframes": [level_data["timeframe"]],
                    "strength": level_data["weight"]
                })
        
        # Sort by strength
        zones = sorted(zones, key=lambda x: x["strength"], reverse=True)
        
        # Add confluence count
        for zone in zones:
            zone["confluence_count"] = len(zone["timeframes"])
        
        return zones[:10]  # Top 10 zones


# Global instance
multi_tf_analyzer = MultiTimeframeAnalyzer()
