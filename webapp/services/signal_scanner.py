"""
Enliko Real-Time Signal Scanner
Scans multiple symbols and strategies for trading signals:
- Multi-symbol parallel scanning
- Multi-strategy detection
- Real-time signal streaming via WebSocket
- Signal ranking and filtering
- Alert system integration
"""
import asyncio
from typing import List, Dict, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

from core.tasks import safe_create_task


logger = logging.getLogger(__name__)


class SignalType(Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    EXIT_LONG = "EXIT_LONG"
    EXIT_SHORT = "EXIT_SHORT"
    NEUTRAL = "NEUTRAL"


class SignalStrength(Enum):
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    VERY_STRONG = 4


@dataclass
class Signal:
    """Trading signal with metadata"""
    symbol: str
    signal_type: SignalType
    strength: SignalStrength
    strategy: str
    price: float
    timestamp: datetime
    indicators: Dict[str, float]
    reasoning: List[str]
    score: float  # 0-100
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    timeframe: str = "1h"
    confidence: float = 0.0  # 0-1
    
    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "signal_type": self.signal_type.value,
            "strength": self.strength.name,
            "strategy": self.strategy,
            "price": self.price,
            "timestamp": self.timestamp.isoformat(),
            "indicators": self.indicators,
            "reasoning": self.reasoning,
            "score": self.score,
            "take_profit": self.take_profit,
            "stop_loss": self.stop_loss,
            "timeframe": self.timeframe,
            "confidence": self.confidence
        }


@dataclass
class ScannerConfig:
    """Scanner configuration"""
    symbols: List[str]
    strategies: List[str]
    timeframes: List[str] = field(default_factory=lambda: ["1h"])
    min_score: float = 50.0
    min_strength: SignalStrength = SignalStrength.MODERATE
    scan_interval: int = 60  # seconds
    max_signals_per_symbol: int = 3
    include_exit_signals: bool = True


class SignalScanner:
    """Real-time multi-symbol, multi-strategy signal scanner"""
    
    # Strategy analyzers mapping
    STRATEGY_ANALYZERS = {
        "rsi_oversold": "_analyze_rsi_oversold",
        "rsi_overbought": "_analyze_rsi_overbought",
        "macd_crossover": "_analyze_macd_crossover",
        "bollinger_squeeze": "_analyze_bollinger_squeeze",
        "supertrend": "_analyze_supertrend",
        "ema_crossover": "_analyze_ema_crossover",
        "wyckoff": "_analyze_wyckoff",
        "mean_reversion": "_analyze_mean_reversion",
        "momentum_burst": "_analyze_momentum_burst",
        "breakout": "_analyze_breakout",
        "divergence": "_analyze_divergence",
        "support_resistance": "_analyze_support_resistance"
    }
    
    def __init__(self):
        self.running = False
        self.callbacks: List[Callable[[Signal], None]] = []
        self.recent_signals: Dict[str, List[Signal]] = {}
        self._scan_task: Optional[asyncio.Task] = None
        self.config: Optional[ScannerConfig] = None
        self._data_cache: Dict[str, Any] = {}
    
    def add_callback(self, callback: Callable[[Signal], None]) -> None:
        """Add callback for new signals"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[Signal], None]) -> None:
        """Remove callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    async def scan(
        self,
        symbols: List[str],
        strategies: List[str],
        timeframe: str = "1h",
        min_score: float = 50.0,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Scan symbols for trading signals across multiple strategies.
        Returns top N signals sorted by score.
        """
        all_signals = []
        
        # Scan in parallel batches
        batch_size = 10
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            
            tasks = [
                self._scan_symbol(symbol, strategies, timeframe)
                for symbol in batch
            ]
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, list):
                    all_signals.extend(result)
        
        # Filter by minimum score
        filtered_signals = [s for s in all_signals if s.score >= min_score]
        
        # Sort by score descending
        sorted_signals = sorted(filtered_signals, key=lambda x: x.score, reverse=True)
        
        # Return top N
        top_signals = sorted_signals[:top_n]
        
        return [s.to_dict() for s in top_signals]
    
    async def _scan_symbol(
        self,
        symbol: str,
        strategies: List[str],
        timeframe: str
    ) -> List[Signal]:
        """Scan a single symbol for signals"""
        signals = []
        
        try:
            # Fetch market data
            data = await self._fetch_data(symbol, timeframe)
            if not data or len(data) < 50:
                return signals
            
            # Calculate indicators
            indicators = await self._calculate_indicators(data)
            
            # Current price and timestamp
            current_price = data[-1].get("close", 0)
            current_time = datetime.now()
            
            # Run each strategy analyzer
            for strategy in strategies:
                analyzer_method = self.STRATEGY_ANALYZERS.get(strategy)
                if analyzer_method:
                    try:
                        method = getattr(self, analyzer_method)
                        signal = await method(
                            symbol, data, indicators, current_price, current_time, timeframe
                        )
                        if signal:
                            signals.append(signal)
                    except Exception as e:
                        logger.error(f"Error in {strategy} analyzer for {symbol}: {e}")
        
        except Exception as e:
            logger.error(f"Error scanning {symbol}: {e}")
        
        return signals
    
    async def _fetch_data(self, symbol: str, timeframe: str, limit: int = 200) -> List[Dict]:
        """Fetch OHLCV data for symbol"""
        try:
            from webapp.services.backtest_engine_pro import DataFetcher
            
            fetcher = DataFetcher()
            data = await fetcher.fetch_historical(
                symbol=symbol,
                interval=timeframe,
                limit=limit
            )
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return []
    
    async def _calculate_indicators(self, data: List[Dict]) -> Dict[str, Any]:
        """Calculate all indicators for the data"""
        from webapp.services.indicators import IndicatorCalculator
        
        calc = IndicatorCalculator()
        
        # Calculate common indicators
        indicators = {
            "rsi_14": calc.calculate("rsi", data, period=14),
            "rsi_7": calc.calculate("rsi", data, period=7),
            "macd": calc.calculate("macd", data, fast=12, slow=26, signal=9),
            "ema_20": calc.calculate("ema", data, period=20),
            "ema_50": calc.calculate("ema", data, period=50),
            "ema_200": calc.calculate("ema", data, period=200),
            "bb": calc.calculate("bollinger_bands", data, period=20, std_dev=2.0),
            "atr": calc.calculate("atr", data, period=14),
            "adx": calc.calculate("adx", data, period=14),
            "supertrend": calc.calculate("supertrend", data, period=10, multiplier=3.0),
            "stochastic": calc.calculate("stochastic", data, k_period=14, d_period=3),
            "obv": calc.calculate("obv", data),
            "mfi": calc.calculate("mfi", data, period=14),
            "cci": calc.calculate("cci", data, period=20)
        }
        
        return indicators
    
    # Strategy analyzers
    async def _analyze_rsi_oversold(
        self, symbol: str, data: List[Dict], indicators: Dict, 
        price: float, time: datetime, timeframe: str
    ) -> Optional[Signal]:
        """RSI oversold signal (LONG)"""
        rsi_values = indicators.get("rsi_14", [])
        if len(rsi_values) < 2:
            return None
        
        current_rsi = rsi_values[-1]
        prev_rsi = rsi_values[-2]
        
        # RSI below 30 and rising
        if current_rsi < 30 and current_rsi > prev_rsi:
            atr = indicators.get("atr", [0])[-1] if indicators.get("atr") else price * 0.02
            
            # Score based on RSI level and momentum
            score = min(100, (30 - current_rsi) * 3 + (current_rsi - prev_rsi) * 5)
            
            return Signal(
                symbol=symbol,
                signal_type=SignalType.LONG,
                strength=SignalStrength.STRONG if current_rsi < 20 else SignalStrength.MODERATE,
                strategy="rsi_oversold",
                price=price,
                timestamp=time,
                indicators={"rsi": current_rsi, "rsi_prev": prev_rsi},
                reasoning=[
                    f"RSI at {current_rsi:.1f} (oversold < 30)",
                    f"RSI rising: {prev_rsi:.1f} → {current_rsi:.1f}"
                ],
                score=score,
                take_profit=price * (1 + 0.03),  # 3% TP
                stop_loss=price * (1 - 0.015),   # 1.5% SL
                timeframe=timeframe,
                confidence=min(1.0, (30 - current_rsi) / 30)
            )
        
        return None
    
    async def _analyze_rsi_overbought(
        self, symbol: str, data: List[Dict], indicators: Dict,
        price: float, time: datetime, timeframe: str
    ) -> Optional[Signal]:
        """RSI overbought signal (SHORT)"""
        rsi_values = indicators.get("rsi_14", [])
        if len(rsi_values) < 2:
            return None
        
        current_rsi = rsi_values[-1]
        prev_rsi = rsi_values[-2]
        
        # RSI above 70 and falling
        if current_rsi > 70 and current_rsi < prev_rsi:
            score = min(100, (current_rsi - 70) * 3 + (prev_rsi - current_rsi) * 5)
            
            return Signal(
                symbol=symbol,
                signal_type=SignalType.SHORT,
                strength=SignalStrength.STRONG if current_rsi > 80 else SignalStrength.MODERATE,
                strategy="rsi_overbought",
                price=price,
                timestamp=time,
                indicators={"rsi": current_rsi, "rsi_prev": prev_rsi},
                reasoning=[
                    f"RSI at {current_rsi:.1f} (overbought > 70)",
                    f"RSI falling: {prev_rsi:.1f} → {current_rsi:.1f}"
                ],
                score=score,
                take_profit=price * (1 - 0.03),
                stop_loss=price * (1 + 0.015),
                timeframe=timeframe,
                confidence=min(1.0, (current_rsi - 70) / 30)
            )
        
        return None
    
    async def _analyze_macd_crossover(
        self, symbol: str, data: List[Dict], indicators: Dict,
        price: float, time: datetime, timeframe: str
    ) -> Optional[Signal]:
        """MACD crossover signal"""
        macd_data = indicators.get("macd", {})
        if not macd_data:
            return None
        
        macd = macd_data.get("macd", [])
        signal = macd_data.get("signal", [])
        
        if len(macd) < 2 or len(signal) < 2:
            return None
        
        # Bullish crossover
        if macd[-1] > signal[-1] and macd[-2] <= signal[-2]:
            histogram = macd[-1] - signal[-1]
            score = min(100, abs(histogram) * 1000 + 50)
            
            return Signal(
                symbol=symbol,
                signal_type=SignalType.LONG,
                strength=SignalStrength.MODERATE if histogram > 0.001 else SignalStrength.WEAK,
                strategy="macd_crossover",
                price=price,
                timestamp=time,
                indicators={"macd": macd[-1], "signal": signal[-1], "histogram": histogram},
                reasoning=[
                    "MACD crossed above signal line",
                    f"Histogram: {histogram:.4f}"
                ],
                score=score,
                take_profit=price * 1.04,
                stop_loss=price * 0.98,
                timeframe=timeframe,
                confidence=min(1.0, abs(histogram) * 100)
            )
        
        # Bearish crossover
        if macd[-1] < signal[-1] and macd[-2] >= signal[-2]:
            histogram = macd[-1] - signal[-1]
            score = min(100, abs(histogram) * 1000 + 50)
            
            return Signal(
                symbol=symbol,
                signal_type=SignalType.SHORT,
                strength=SignalStrength.MODERATE if abs(histogram) > 0.001 else SignalStrength.WEAK,
                strategy="macd_crossover",
                price=price,
                timestamp=time,
                indicators={"macd": macd[-1], "signal": signal[-1], "histogram": histogram},
                reasoning=[
                    "MACD crossed below signal line",
                    f"Histogram: {histogram:.4f}"
                ],
                score=score,
                take_profit=price * 0.96,
                stop_loss=price * 1.02,
                timeframe=timeframe,
                confidence=min(1.0, abs(histogram) * 100)
            )
        
        return None
    
    async def _analyze_bollinger_squeeze(
        self, symbol: str, data: List[Dict], indicators: Dict,
        price: float, time: datetime, timeframe: str
    ) -> Optional[Signal]:
        """Bollinger Band squeeze breakout"""
        bb = indicators.get("bb", {})
        if not bb:
            return None
        
        upper = bb.get("upper", [])
        lower = bb.get("lower", [])
        middle = bb.get("middle", [])
        
        if len(upper) < 20:
            return None
        
        # Calculate band width
        current_width = (upper[-1] - lower[-1]) / middle[-1] if middle[-1] else 0
        avg_width = sum((upper[i] - lower[i]) / middle[i] if middle[i] else 0 
                       for i in range(-20, 0)) / 20
        
        # Squeeze detection: current width < 50% of average
        is_squeeze = current_width < avg_width * 0.5
        
        if not is_squeeze:
            return None
        
        # Breakout direction
        if price > upper[-1]:
            score = min(100, 70 + (1 - current_width / avg_width) * 30)
            
            return Signal(
                symbol=symbol,
                signal_type=SignalType.LONG,
                strength=SignalStrength.STRONG,
                strategy="bollinger_squeeze",
                price=price,
                timestamp=time,
                indicators={
                    "upper": upper[-1], "lower": lower[-1], "middle": middle[-1],
                    "band_width": current_width, "avg_width": avg_width
                },
                reasoning=[
                    "Bollinger Band squeeze detected",
                    f"Width: {current_width:.4f} vs avg: {avg_width:.4f}",
                    "Price breaking above upper band"
                ],
                score=score,
                take_profit=price * 1.05,
                stop_loss=middle[-1] * 0.99,
                timeframe=timeframe,
                confidence=0.75
            )
        
        elif price < lower[-1]:
            score = min(100, 70 + (1 - current_width / avg_width) * 30)
            
            return Signal(
                symbol=symbol,
                signal_type=SignalType.SHORT,
                strength=SignalStrength.STRONG,
                strategy="bollinger_squeeze",
                price=price,
                timestamp=time,
                indicators={
                    "upper": upper[-1], "lower": lower[-1], "middle": middle[-1],
                    "band_width": current_width, "avg_width": avg_width
                },
                reasoning=[
                    "Bollinger Band squeeze detected",
                    f"Width: {current_width:.4f} vs avg: {avg_width:.4f}",
                    "Price breaking below lower band"
                ],
                score=score,
                take_profit=price * 0.95,
                stop_loss=middle[-1] * 1.01,
                timeframe=timeframe,
                confidence=0.75
            )
        
        return None
    
    async def _analyze_supertrend(
        self, symbol: str, data: List[Dict], indicators: Dict,
        price: float, time: datetime, timeframe: str
    ) -> Optional[Signal]:
        """SuperTrend direction change"""
        supertrend = indicators.get("supertrend", {})
        if not supertrend:
            return None
        
        direction = supertrend.get("direction", [])
        value = supertrend.get("value", [])
        
        if len(direction) < 2:
            return None
        
        # Direction change from -1 to 1 (bullish)
        if direction[-1] == 1 and direction[-2] == -1:
            return Signal(
                symbol=symbol,
                signal_type=SignalType.LONG,
                strength=SignalStrength.STRONG,
                strategy="supertrend",
                price=price,
                timestamp=time,
                indicators={"supertrend": value[-1], "direction": direction[-1]},
                reasoning=[
                    "SuperTrend flipped to bullish",
                    f"SuperTrend level: {value[-1]:.2f}"
                ],
                score=75,
                take_profit=price * 1.05,
                stop_loss=value[-1] * 0.99,
                timeframe=timeframe,
                confidence=0.7
            )
        
        # Direction change from 1 to -1 (bearish)
        if direction[-1] == -1 and direction[-2] == 1:
            return Signal(
                symbol=symbol,
                signal_type=SignalType.SHORT,
                strength=SignalStrength.STRONG,
                strategy="supertrend",
                price=price,
                timestamp=time,
                indicators={"supertrend": value[-1], "direction": direction[-1]},
                reasoning=[
                    "SuperTrend flipped to bearish",
                    f"SuperTrend level: {value[-1]:.2f}"
                ],
                score=75,
                take_profit=price * 0.95,
                stop_loss=value[-1] * 1.01,
                timeframe=timeframe,
                confidence=0.7
            )
        
        return None
    
    async def _analyze_ema_crossover(
        self, symbol: str, data: List[Dict], indicators: Dict,
        price: float, time: datetime, timeframe: str
    ) -> Optional[Signal]:
        """EMA crossover signal"""
        ema_20 = indicators.get("ema_20", [])
        ema_50 = indicators.get("ema_50", [])
        
        if len(ema_20) < 2 or len(ema_50) < 2:
            return None
        
        # Golden cross (EMA20 crosses above EMA50)
        if ema_20[-1] > ema_50[-1] and ema_20[-2] <= ema_50[-2]:
            adx = indicators.get("adx", [25])[-1] if indicators.get("adx") else 25
            score = min(100, 50 + adx)
            
            return Signal(
                symbol=symbol,
                signal_type=SignalType.LONG,
                strength=SignalStrength.STRONG if adx > 25 else SignalStrength.MODERATE,
                strategy="ema_crossover",
                price=price,
                timestamp=time,
                indicators={"ema_20": ema_20[-1], "ema_50": ema_50[-1], "adx": adx},
                reasoning=[
                    "EMA 20 crossed above EMA 50 (Golden Cross)",
                    f"Trend strength ADX: {adx:.1f}"
                ],
                score=score,
                take_profit=price * 1.05,
                stop_loss=ema_50[-1] * 0.99,
                timeframe=timeframe,
                confidence=min(1.0, adx / 50)
            )
        
        # Death cross (EMA20 crosses below EMA50)
        if ema_20[-1] < ema_50[-1] and ema_20[-2] >= ema_50[-2]:
            adx = indicators.get("adx", [25])[-1] if indicators.get("adx") else 25
            score = min(100, 50 + adx)
            
            return Signal(
                symbol=symbol,
                signal_type=SignalType.SHORT,
                strength=SignalStrength.STRONG if adx > 25 else SignalStrength.MODERATE,
                strategy="ema_crossover",
                price=price,
                timestamp=time,
                indicators={"ema_20": ema_20[-1], "ema_50": ema_50[-1], "adx": adx},
                reasoning=[
                    "EMA 20 crossed below EMA 50 (Death Cross)",
                    f"Trend strength ADX: {adx:.1f}"
                ],
                score=score,
                take_profit=price * 0.95,
                stop_loss=ema_50[-1] * 1.01,
                timeframe=timeframe,
                confidence=min(1.0, adx / 50)
            )
        
        return None
    
    async def _analyze_wyckoff(
        self, symbol: str, data: List[Dict], indicators: Dict,
        price: float, time: datetime, timeframe: str
    ) -> Optional[Signal]:
        """Wyckoff accumulation/distribution detection"""
        # Simplified Wyckoff detection using volume and price action
        if len(data) < 50:
            return None
        
        # Look for accumulation (low volume at support, increasing on rally)
        volumes = [d.get("volume", 0) for d in data[-30:]]
        closes = [d.get("close", 0) for d in data[-30:]]
        
        avg_volume = sum(volumes) / len(volumes)
        recent_avg_volume = sum(volumes[-5:]) / 5
        
        # Price near local low with increasing volume
        local_min = min(closes[-20:])
        local_max = max(closes[-20:])
        price_range = local_max - local_min if local_max > local_min else 1
        
        price_position = (price - local_min) / price_range if price_range else 0.5
        
        # Accumulation: price near bottom, volume picking up
        if price_position < 0.3 and recent_avg_volume > avg_volume * 1.2:
            return Signal(
                symbol=symbol,
                signal_type=SignalType.LONG,
                strength=SignalStrength.MODERATE,
                strategy="wyckoff",
                price=price,
                timestamp=time,
                indicators={
                    "price_position": price_position,
                    "volume_ratio": recent_avg_volume / avg_volume
                },
                reasoning=[
                    "Wyckoff accumulation pattern detected",
                    f"Price near support (position: {price_position:.1%})",
                    f"Volume increasing: {recent_avg_volume/avg_volume:.1f}x avg"
                ],
                score=65,
                take_profit=local_max,
                stop_loss=local_min * 0.99,
                timeframe=timeframe,
                confidence=0.6
            )
        
        # Distribution: price near top, volume picking up
        if price_position > 0.7 and recent_avg_volume > avg_volume * 1.2:
            return Signal(
                symbol=symbol,
                signal_type=SignalType.SHORT,
                strength=SignalStrength.MODERATE,
                strategy="wyckoff",
                price=price,
                timestamp=time,
                indicators={
                    "price_position": price_position,
                    "volume_ratio": recent_avg_volume / avg_volume
                },
                reasoning=[
                    "Wyckoff distribution pattern detected",
                    f"Price near resistance (position: {price_position:.1%})",
                    f"Volume increasing: {recent_avg_volume/avg_volume:.1f}x avg"
                ],
                score=65,
                take_profit=local_min,
                stop_loss=local_max * 1.01,
                timeframe=timeframe,
                confidence=0.6
            )
        
        return None
    
    async def _analyze_mean_reversion(
        self, symbol: str, data: List[Dict], indicators: Dict,
        price: float, time: datetime, timeframe: str
    ) -> Optional[Signal]:
        """Mean reversion based on Bollinger Bands and RSI"""
        bb = indicators.get("bb", {})
        rsi = indicators.get("rsi_14", [])
        
        if not bb or len(rsi) < 1:
            return None
        
        upper = bb.get("upper", [])
        lower = bb.get("lower", [])
        middle = bb.get("middle", [])
        
        if not upper or not lower or not middle:
            return None
        
        current_rsi = rsi[-1]
        
        # Oversold + at lower BB = LONG
        if price <= lower[-1] and current_rsi < 35:
            score = min(100, (35 - current_rsi) * 2 + 40)
            
            return Signal(
                symbol=symbol,
                signal_type=SignalType.LONG,
                strength=SignalStrength.STRONG if current_rsi < 25 else SignalStrength.MODERATE,
                strategy="mean_reversion",
                price=price,
                timestamp=time,
                indicators={
                    "rsi": current_rsi,
                    "bb_lower": lower[-1],
                    "bb_middle": middle[-1]
                },
                reasoning=[
                    f"Price at lower Bollinger Band (${lower[-1]:.2f})",
                    f"RSI oversold at {current_rsi:.1f}",
                    "Expecting mean reversion to middle band"
                ],
                score=score,
                take_profit=middle[-1],
                stop_loss=lower[-1] * 0.98,
                timeframe=timeframe,
                confidence=min(1.0, (35 - current_rsi) / 35)
            )
        
        # Overbought + at upper BB = SHORT
        if price >= upper[-1] and current_rsi > 65:
            score = min(100, (current_rsi - 65) * 2 + 40)
            
            return Signal(
                symbol=symbol,
                signal_type=SignalType.SHORT,
                strength=SignalStrength.STRONG if current_rsi > 75 else SignalStrength.MODERATE,
                strategy="mean_reversion",
                price=price,
                timestamp=time,
                indicators={
                    "rsi": current_rsi,
                    "bb_upper": upper[-1],
                    "bb_middle": middle[-1]
                },
                reasoning=[
                    f"Price at upper Bollinger Band (${upper[-1]:.2f})",
                    f"RSI overbought at {current_rsi:.1f}",
                    "Expecting mean reversion to middle band"
                ],
                score=score,
                take_profit=middle[-1],
                stop_loss=upper[-1] * 1.02,
                timeframe=timeframe,
                confidence=min(1.0, (current_rsi - 65) / 35)
            )
        
        return None
    
    async def _analyze_momentum_burst(
        self, symbol: str, data: List[Dict], indicators: Dict,
        price: float, time: datetime, timeframe: str
    ) -> Optional[Signal]:
        """Momentum burst detection"""
        if len(data) < 10:
            return None
        
        # Calculate recent price change
        price_5 = data[-5].get("close", price)
        price_change = (price - price_5) / price_5 * 100
        
        # Volume surge
        volumes = [d.get("volume", 0) for d in data[-20:]]
        avg_volume = sum(volumes[:-5]) / 15 if len(volumes) >= 20 else sum(volumes) / len(volumes)
        recent_volume = sum(volumes[-5:]) / 5
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        
        adx = indicators.get("adx", [20])[-1] if indicators.get("adx") else 20
        
        # Strong momentum up
        if price_change > 3 and volume_ratio > 1.5 and adx > 25:
            score = min(100, price_change * 10 + volume_ratio * 10 + adx)
            
            return Signal(
                symbol=symbol,
                signal_type=SignalType.LONG,
                strength=SignalStrength.VERY_STRONG if price_change > 5 else SignalStrength.STRONG,
                strategy="momentum_burst",
                price=price,
                timestamp=time,
                indicators={
                    "price_change_5": price_change,
                    "volume_ratio": volume_ratio,
                    "adx": adx
                },
                reasoning=[
                    f"Strong momentum: +{price_change:.2f}% in 5 candles",
                    f"Volume surge: {volume_ratio:.1f}x average",
                    f"Trend strength ADX: {adx:.1f}"
                ],
                score=score,
                take_profit=price * (1 + price_change / 100),  # Match momentum
                stop_loss=price_5,
                timeframe=timeframe,
                confidence=min(1.0, volume_ratio / 3)
            )
        
        # Strong momentum down
        if price_change < -3 and volume_ratio > 1.5 and adx > 25:
            score = min(100, abs(price_change) * 10 + volume_ratio * 10 + adx)
            
            return Signal(
                symbol=symbol,
                signal_type=SignalType.SHORT,
                strength=SignalStrength.VERY_STRONG if price_change < -5 else SignalStrength.STRONG,
                strategy="momentum_burst",
                price=price,
                timestamp=time,
                indicators={
                    "price_change_5": price_change,
                    "volume_ratio": volume_ratio,
                    "adx": adx
                },
                reasoning=[
                    f"Strong momentum: {price_change:.2f}% in 5 candles",
                    f"Volume surge: {volume_ratio:.1f}x average",
                    f"Trend strength ADX: {adx:.1f}"
                ],
                score=score,
                take_profit=price * (1 + price_change / 100),
                stop_loss=price_5,
                timeframe=timeframe,
                confidence=min(1.0, volume_ratio / 3)
            )
        
        return None
    
    async def _analyze_breakout(
        self, symbol: str, data: List[Dict], indicators: Dict,
        price: float, time: datetime, timeframe: str
    ) -> Optional[Signal]:
        """Support/Resistance breakout"""
        if len(data) < 50:
            return None
        
        # Calculate recent highs and lows
        highs = [d.get("high", 0) for d in data[-50:-1]]
        lows = [d.get("low", 0) for d in data[-50:-1]]
        
        resistance = max(highs[-20:])
        support = min(lows[-20:])
        
        atr = indicators.get("atr", [0])[-1] if indicators.get("atr") else price * 0.02
        
        # Breakout above resistance
        if price > resistance * 1.005:  # 0.5% above resistance
            score = 75
            
            return Signal(
                symbol=symbol,
                signal_type=SignalType.LONG,
                strength=SignalStrength.STRONG,
                strategy="breakout",
                price=price,
                timestamp=time,
                indicators={
                    "resistance": resistance,
                    "support": support,
                    "atr": atr
                },
                reasoning=[
                    f"Breakout above resistance ${resistance:.2f}",
                    f"Current price: ${price:.2f}",
                    "Looking for continuation"
                ],
                score=score,
                take_profit=price + (resistance - support),  # Measure move
                stop_loss=resistance * 0.995,
                timeframe=timeframe,
                confidence=0.7
            )
        
        # Breakdown below support
        if price < support * 0.995:
            score = 75
            
            return Signal(
                symbol=symbol,
                signal_type=SignalType.SHORT,
                strategy="breakout",
                strength=SignalStrength.STRONG,
                price=price,
                timestamp=time,
                indicators={
                    "resistance": resistance,
                    "support": support,
                    "atr": atr
                },
                reasoning=[
                    f"Breakdown below support ${support:.2f}",
                    f"Current price: ${price:.2f}",
                    "Looking for continuation"
                ],
                score=score,
                take_profit=price - (resistance - support),
                stop_loss=support * 1.005,
                timeframe=timeframe,
                confidence=0.7
            )
        
        return None
    
    async def _analyze_divergence(
        self, symbol: str, data: List[Dict], indicators: Dict,
        price: float, time: datetime, timeframe: str
    ) -> Optional[Signal]:
        """RSI divergence detection"""
        rsi = indicators.get("rsi_14", [])
        if len(rsi) < 20 or len(data) < 20:
            return None
        
        # Look for price making new lows but RSI making higher lows (bullish)
        recent_prices = [d.get("close", 0) for d in data[-20:]]
        
        # Find recent swing lows
        price_low_1 = min(recent_prices[-10:])
        price_low_2 = min(recent_prices[-20:-10])
        
        rsi_at_low_1 = rsi[-5]  # Approximate
        rsi_at_low_2 = rsi[-15]  # Approximate
        
        # Bullish divergence: lower price low, higher RSI low
        if price_low_1 < price_low_2 * 0.99 and rsi_at_low_1 > rsi_at_low_2 + 5:
            return Signal(
                symbol=symbol,
                signal_type=SignalType.LONG,
                strength=SignalStrength.MODERATE,
                strategy="divergence",
                price=price,
                timestamp=time,
                indicators={
                    "rsi_current": rsi[-1],
                    "rsi_divergence": rsi_at_low_1 - rsi_at_low_2
                },
                reasoning=[
                    "Bullish RSI divergence detected",
                    f"Price made lower low but RSI made higher low",
                    "Momentum shifting bullish"
                ],
                score=65,
                take_profit=price * 1.04,
                stop_loss=price_low_1 * 0.99,
                timeframe=timeframe,
                confidence=0.6
            )
        
        # Find recent swing highs
        price_high_1 = max(recent_prices[-10:])
        price_high_2 = max(recent_prices[-20:-10])
        
        rsi_at_high_1 = rsi[-5]
        rsi_at_high_2 = rsi[-15]
        
        # Bearish divergence: higher price high, lower RSI high
        if price_high_1 > price_high_2 * 1.01 and rsi_at_high_1 < rsi_at_high_2 - 5:
            return Signal(
                symbol=symbol,
                signal_type=SignalType.SHORT,
                strength=SignalStrength.MODERATE,
                strategy="divergence",
                price=price,
                timestamp=time,
                indicators={
                    "rsi_current": rsi[-1],
                    "rsi_divergence": rsi_at_high_2 - rsi_at_high_1
                },
                reasoning=[
                    "Bearish RSI divergence detected",
                    f"Price made higher high but RSI made lower high",
                    "Momentum shifting bearish"
                ],
                score=65,
                take_profit=price * 0.96,
                stop_loss=price_high_1 * 1.01,
                timeframe=timeframe,
                confidence=0.6
            )
        
        return None
    
    async def _analyze_support_resistance(
        self, symbol: str, data: List[Dict], indicators: Dict,
        price: float, time: datetime, timeframe: str
    ) -> Optional[Signal]:
        """Support/Resistance bounce"""
        if len(data) < 100:
            return None
        
        # Calculate key levels
        highs = [d.get("high", 0) for d in data[-100:]]
        lows = [d.get("low", 0) for d in data[-100:]]
        
        # Simple pivot calculation
        pivot = (max(highs[-20:]) + min(lows[-20:]) + data[-1].get("close", 0)) / 3
        
        resistance = pivot + (max(highs[-20:]) - min(lows[-20:])) * 0.5
        support = pivot - (max(highs[-20:]) - min(lows[-20:])) * 0.5
        
        atr = indicators.get("atr", [0])[-1] if indicators.get("atr") else price * 0.02
        
        # Near support with bullish candle
        if abs(price - support) < atr and data[-1].get("close", 0) > data[-1].get("open", 0):
            return Signal(
                symbol=symbol,
                signal_type=SignalType.LONG,
                strength=SignalStrength.MODERATE,
                strategy="support_resistance",
                price=price,
                timestamp=time,
                indicators={
                    "support": support,
                    "resistance": resistance,
                    "pivot": pivot
                },
                reasoning=[
                    f"Price testing support at ${support:.2f}",
                    "Bullish candle formed at support",
                    "Looking for bounce"
                ],
                score=60,
                take_profit=pivot,
                stop_loss=support - atr,
                timeframe=timeframe,
                confidence=0.55
            )
        
        # Near resistance with bearish candle
        if abs(price - resistance) < atr and data[-1].get("close", 0) < data[-1].get("open", 0):
            return Signal(
                symbol=symbol,
                signal_type=SignalType.SHORT,
                strength=SignalStrength.MODERATE,
                strategy="support_resistance",
                price=price,
                timestamp=time,
                indicators={
                    "support": support,
                    "resistance": resistance,
                    "pivot": pivot
                },
                reasoning=[
                    f"Price testing resistance at ${resistance:.2f}",
                    "Bearish candle formed at resistance",
                    "Looking for rejection"
                ],
                score=60,
                take_profit=pivot,
                stop_loss=resistance + atr,
                timeframe=timeframe,
                confidence=0.55
            )
        
        return None
    
    # Live scanning methods
    async def start_live_scan(self, config: ScannerConfig) -> None:
        """Start continuous live scanning"""
        self.config = config
        self.running = True
        self._scan_task = safe_create_task(self._live_scan_loop(), name="signal_scanner_live")
    
    async def stop_live_scan(self) -> None:
        """Stop live scanning"""
        self.running = False
        if self._scan_task:
            self._scan_task.cancel()
            try:
                await self._scan_task
            except asyncio.CancelledError:
                pass
    
    async def _live_scan_loop(self) -> None:
        """Main live scanning loop"""
        while self.running and self.config:
            try:
                for timeframe in self.config.timeframes:
                    signals = await self.scan(
                        symbols=self.config.symbols,
                        strategies=self.config.strategies,
                        timeframe=timeframe,
                        min_score=self.config.min_score
                    )
                    
                    for signal_dict in signals:
                        # Convert back to Signal object for callbacks
                        signal = Signal(
                            symbol=signal_dict["symbol"],
                            signal_type=SignalType(signal_dict["signal_type"]),
                            strength=SignalStrength[signal_dict["strength"]],
                            strategy=signal_dict["strategy"],
                            price=signal_dict["price"],
                            timestamp=datetime.fromisoformat(signal_dict["timestamp"]),
                            indicators=signal_dict["indicators"],
                            reasoning=signal_dict["reasoning"],
                            score=signal_dict["score"],
                            take_profit=signal_dict["take_profit"],
                            stop_loss=signal_dict["stop_loss"],
                            timeframe=signal_dict["timeframe"],
                            confidence=signal_dict["confidence"]
                        )
                        
                        # Notify callbacks
                        for callback in self.callbacks:
                            try:
                                await callback(signal)
                            except Exception as e:
                                logger.error(f"Callback error: {e}")
                
                # Wait for next scan
                await asyncio.sleep(self.config.scan_interval)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Live scan error: {e}")
                await asyncio.sleep(5)
    
    def get_active_signals(self) -> Dict[str, List[Dict]]:
        """Get recent signals organized by symbol"""
        return {
            symbol: [s.to_dict() for s in signals]
            for symbol, signals in self.recent_signals.items()
        }


# Singleton instance
signal_scanner = SignalScanner()
