"""
ElCaro Pro Backtest Engine V2
Professional-grade backtesting with advanced features:
- Commission & slippage modeling
- Trailing stops
- Position pyramiding
- Kelly Criterion position sizing
- Regime detection
- Correlation analysis
- Portfolio optimization
- Advanced metrics (Sortino, Calmar, Omega, SQN)
"""
import asyncio
import aiohttp
import math
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json


# =============================================================================
# ENUMS & DATA CLASSES
# =============================================================================

class PositionSide(Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


class ExitReason(Enum):
    TP = "TP"
    SL = "SL"
    TRAILING_STOP = "TRAILING_STOP"
    SIGNAL = "SIGNAL"
    TIME_EXIT = "TIME_EXIT"
    EOB = "EOB"  # End of backtest


class MarketRegime(Enum):
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"


@dataclass
class Candle:
    timestamp: int
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "time": self.time,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }


@dataclass
class Position:
    entry_time: str
    entry_price: float
    side: PositionSide
    size: float
    stop_loss: float
    take_profit: float
    trailing_stop: bool = False
    trailing_stop_distance: float = 0.0
    trailing_stop_activation: float = 0.0
    trailing_stop_triggered: bool = False
    highest_price: float = 0.0  # For trailing stop
    lowest_price: float = 0.0   # For trailing stop
    max_bars: int = 0  # Time-based exit (0 = disabled)
    bars_held: int = 0
    pyramiding_level: int = 1
    
    def update_trailing(self, current_price: float) -> float:
        """Update trailing stop and return current stop level"""
        if not self.trailing_stop:
            return self.stop_loss
        
        if self.side == PositionSide.LONG:
            # Track highest price
            if current_price > self.highest_price:
                self.highest_price = current_price
            
            # Activate trailing stop
            profit_pct = (current_price - self.entry_price) / self.entry_price * 100
            if profit_pct >= self.trailing_stop_activation and not self.trailing_stop_triggered:
                self.trailing_stop_triggered = True
            
            if self.trailing_stop_triggered:
                new_stop = self.highest_price * (1 - self.trailing_stop_distance / 100)
                self.stop_loss = max(self.stop_loss, new_stop)
        else:
            # Track lowest price
            if current_price < self.lowest_price or self.lowest_price == 0:
                self.lowest_price = current_price
            
            # Activate trailing stop
            profit_pct = (self.entry_price - current_price) / self.entry_price * 100
            if profit_pct >= self.trailing_stop_activation and not self.trailing_stop_triggered:
                self.trailing_stop_triggered = True
            
            if self.trailing_stop_triggered:
                new_stop = self.lowest_price * (1 + self.trailing_stop_distance / 100)
                self.stop_loss = min(self.stop_loss, new_stop)
        
        return self.stop_loss


@dataclass
class Trade:
    entry_time: str
    exit_time: str
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    pnl_percent: float
    commission: float
    slippage: float
    reason: str
    duration_bars: int
    max_favorable: float = 0.0  # MAE/MFE
    max_adverse: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "entry_time": self.entry_time,
            "exit_time": self.exit_time,
            "symbol": self.symbol,
            "direction": self.side,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "size": self.size,
            "pnl": self.pnl,
            "pnl_percent": self.pnl_percent,
            "commission": self.commission,
            "slippage": self.slippage,
            "reason": self.reason,
            "duration_bars": self.duration_bars,
            "max_favorable": self.max_favorable,
            "max_adverse": self.max_adverse
        }


@dataclass
class BacktestConfig:
    """Complete backtest configuration"""
    symbol: str = "BTCUSDT"
    timeframe: str = "1h"
    days: int = 30
    initial_balance: float = 10000
    
    # Risk management
    stop_loss_percent: float = 2.0
    take_profit_percent: float = 4.0
    risk_per_trade: float = 1.0
    max_positions: int = 1
    max_drawdown_percent: float = 20.0  # Stop trading if exceeded
    
    # Position sizing
    position_sizing: str = "fixed_percent"  # fixed_percent, kelly, volatility_adjusted
    kelly_fraction: float = 0.5  # Half-Kelly for safety
    
    # Trailing stop
    trailing_stop: bool = False
    trailing_stop_activation: float = 2.0  # Activate after X% profit
    trailing_stop_distance: float = 1.0    # Trail by X%
    
    # Transaction costs
    commission_percent: float = 0.1  # 0.1% per trade
    slippage_percent: float = 0.05   # 0.05% slippage
    
    # Leverage
    leverage: int = 1
    
    # Time filters
    max_bars_in_trade: int = 0  # 0 = disabled
    
    # Pyramiding
    pyramiding_enabled: bool = False
    max_pyramiding_positions: int = 3
    pyramiding_scale_factor: float = 0.5  # Each add is 50% of previous
    
    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "days": self.days,
            "initial_balance": self.initial_balance,
            "stop_loss_percent": self.stop_loss_percent,
            "take_profit_percent": self.take_profit_percent,
            "risk_per_trade": self.risk_per_trade,
            "max_positions": self.max_positions,
            "trailing_stop": self.trailing_stop,
            "commission_percent": self.commission_percent,
            "slippage_percent": self.slippage_percent,
            "leverage": self.leverage
        }


@dataclass
class BacktestMetrics:
    """Comprehensive backtest metrics"""
    # Core metrics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    
    # Returns
    total_return: float = 0.0
    total_return_percent: float = 0.0
    annualized_return: float = 0.0
    
    # Risk metrics
    max_drawdown_percent: float = 0.0
    max_drawdown_duration_days: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    omega_ratio: float = 0.0
    
    # Trade metrics
    avg_win: float = 0.0
    avg_loss: float = 0.0
    avg_trade: float = 0.0
    profit_factor: float = 0.0
    payoff_ratio: float = 0.0
    
    # Time metrics
    avg_bars_in_trade: float = 0.0
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    
    # Advanced
    recovery_factor: float = 0.0
    expectancy: float = 0.0
    sqn: float = 0.0  # System Quality Number
    
    # Costs
    total_commission: float = 0.0
    total_slippage: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": round(self.win_rate, 2),
            "total_return": round(self.total_return, 2),
            "total_return_percent": round(self.total_return_percent, 2),
            "annualized_return": round(self.annualized_return, 2),
            "max_drawdown_percent": round(self.max_drawdown_percent, 2),
            "max_drawdown_duration_days": round(self.max_drawdown_duration_days, 2),
            "sharpe_ratio": round(self.sharpe_ratio, 3),
            "sortino_ratio": round(self.sortino_ratio, 3),
            "calmar_ratio": round(self.calmar_ratio, 3),
            "omega_ratio": round(self.omega_ratio, 3),
            "avg_win": round(self.avg_win, 2),
            "avg_loss": round(self.avg_loss, 2),
            "avg_trade": round(self.avg_trade, 2),
            "profit_factor": round(self.profit_factor, 3),
            "payoff_ratio": round(self.payoff_ratio, 3),
            "avg_bars_in_trade": round(self.avg_bars_in_trade, 1),
            "max_consecutive_wins": self.max_consecutive_wins,
            "max_consecutive_losses": self.max_consecutive_losses,
            "recovery_factor": round(self.recovery_factor, 3),
            "expectancy": round(self.expectancy, 4),
            "sqn": round(self.sqn, 3),
            "total_commission": round(self.total_commission, 2),
            "total_slippage": round(self.total_slippage, 2)
        }


# =============================================================================
# DATA FETCHER
# =============================================================================

class DataFetcher:
    """Async data fetcher with caching"""
    
    _cache: Dict[str, Tuple[List[Dict], float]] = {}
    _cache_ttl = 300  # 5 minutes
    
    @classmethod
    async def fetch_candles(cls, symbol: str, timeframe: str, days: int) -> List[Dict]:
        """Fetch OHLCV data from Binance with pagination for unlimited history"""
        cache_key = f"{symbol}_{timeframe}_{days}"
        now = datetime.now().timestamp()
        
        # Check cache
        if cache_key in cls._cache:
            data, cached_time = cls._cache[cache_key]
            if now - cached_time < cls._cache_ttl:
                return data
        
        tf_map = {"1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m", 
                  "1h": "1h", "4h": "4h", "1d": "1d", "1w": "1w"}
        interval = tf_map.get(timeframe, "1h")
        
        # Calculate candles needed
        candles_per_day = {"1m": 1440, "5m": 288, "15m": 96, "30m": 48,
                          "1h": 24, "4h": 6, "1d": 1, "1w": 1/7}
        total_needed = int(days * candles_per_day.get(interval, 24))
        
        all_candles = []
        end_time = int(datetime.now().timestamp() * 1000)
        
        async with aiohttp.ClientSession() as session:
            while len(all_candles) < total_needed:
                limit = min(1000, total_needed - len(all_candles))
                url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}&endTime={end_time}"
                
                try:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                        if resp.status != 200:
                            break
                        
                        data = await resp.json()
                        if not data:
                            break
                        
                        batch = [
                            {
                                "timestamp": k[0],
                                "time": datetime.fromtimestamp(k[0] / 1000).isoformat(),
                                "open": float(k[1]),
                                "high": float(k[2]),
                                "low": float(k[3]),
                                "close": float(k[4]),
                                "volume": float(k[5])
                            }
                            for k in data
                        ]
                        
                        all_candles = batch + all_candles
                        end_time = data[0][0] - 1
                        
                        if len(data) < limit:
                            break
                except Exception:
                    break
        
        if all_candles:
            cls._cache[cache_key] = (all_candles, now)
        
        return all_candles


# =============================================================================
# REGIME DETECTOR
# =============================================================================

class RegimeDetector:
    """Detect market regime for strategy adaptation"""
    
    @staticmethod
    def detect(candles: List[Dict], lookback: int = 50) -> MarketRegime:
        """Detect current market regime"""
        if len(candles) < lookback:
            return MarketRegime.RANGING
        
        window = candles[-lookback:]
        closes = [c["close"] for c in window]
        highs = [c["high"] for c in window]
        lows = [c["low"] for c in window]
        
        # Trend detection using linear regression slope
        n = len(closes)
        x_mean = (n - 1) / 2
        y_mean = sum(closes) / n
        
        numerator = sum((i - x_mean) * (closes[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        slope = numerator / denominator if denominator != 0 else 0
        
        # Normalize slope by price
        norm_slope = slope / y_mean * 100
        
        # Volatility using ATR ratio
        atr_sum = 0
        for i in range(1, len(window)):
            tr = max(
                window[i]["high"] - window[i]["low"],
                abs(window[i]["high"] - window[i-1]["close"]),
                abs(window[i]["low"] - window[i-1]["close"])
            )
            atr_sum += tr
        
        atr = atr_sum / (len(window) - 1)
        atr_percent = atr / y_mean * 100
        
        # Price range as % of average
        price_range = (max(highs) - min(lows)) / y_mean * 100
        
        # Classify regime
        if atr_percent > 3.0:  # High volatility
            return MarketRegime.HIGH_VOLATILITY
        elif atr_percent < 1.0:  # Low volatility
            return MarketRegime.LOW_VOLATILITY
        elif norm_slope > 0.1:  # Strong uptrend
            return MarketRegime.TRENDING_UP
        elif norm_slope < -0.1:  # Strong downtrend
            return MarketRegime.TRENDING_DOWN
        else:
            return MarketRegime.RANGING
    
    @staticmethod
    def get_regime_stats(candles: List[Dict], window_size: int = 50) -> List[Dict]:
        """Get regime for each candle"""
        regimes = []
        for i in range(len(candles)):
            if i < window_size:
                regimes.append({"time": candles[i]["time"], "regime": "unknown"})
            else:
                regime = RegimeDetector.detect(candles[:i+1], window_size)
                regimes.append({"time": candles[i]["time"], "regime": regime.value})
        return regimes


# =============================================================================
# POSITION SIZER
# =============================================================================

class PositionSizer:
    """Advanced position sizing algorithms"""
    
    @staticmethod
    def fixed_percent(equity: float, risk_percent: float, stop_loss_percent: float, 
                      leverage: int = 1) -> float:
        """Fixed percentage of equity"""
        risk_amount = equity * (risk_percent / 100)
        position_size = risk_amount / (stop_loss_percent / 100)
        return position_size * leverage
    
    @staticmethod
    def kelly_criterion(win_rate: float, payoff_ratio: float, 
                        kelly_fraction: float = 0.5) -> float:
        """Kelly Criterion for optimal position sizing"""
        if payoff_ratio <= 0:
            return 0
        
        # Kelly formula: f* = (p * b - q) / b
        # where p = win probability, q = lose probability, b = win/loss ratio
        p = win_rate / 100
        q = 1 - p
        b = payoff_ratio
        
        kelly = (p * b - q) / b if b > 0 else 0
        
        # Apply fraction for safety (half-Kelly or quarter-Kelly)
        return max(0, min(kelly * kelly_fraction, 0.25))  # Cap at 25%
    
    @staticmethod
    def volatility_adjusted(equity: float, risk_percent: float, atr: float, 
                           atr_multiplier: float = 2.0, leverage: int = 1) -> float:
        """Position size based on volatility (ATR)"""
        risk_amount = equity * (risk_percent / 100)
        dollar_risk = atr * atr_multiplier
        
        if dollar_risk <= 0:
            return 0
        
        position_size = risk_amount / dollar_risk
        return position_size * leverage
    
    @staticmethod
    def calculate_size(config: BacktestConfig, equity: float, win_rate: float = 50,
                       payoff_ratio: float = 2.0, atr: float = 0) -> float:
        """Calculate position size based on config method"""
        if config.position_sizing == "kelly":
            kelly_pct = PositionSizer.kelly_criterion(
                win_rate, payoff_ratio, config.kelly_fraction
            )
            return equity * kelly_pct * config.leverage
        elif config.position_sizing == "volatility_adjusted" and atr > 0:
            return PositionSizer.volatility_adjusted(
                equity, config.risk_per_trade, atr, 2.0, config.leverage
            )
        else:
            return PositionSizer.fixed_percent(
                equity, config.risk_per_trade, config.stop_loss_percent, config.leverage
            )


# =============================================================================
# METRICS CALCULATOR
# =============================================================================

class MetricsCalculator:
    """Calculate comprehensive backtest metrics"""
    
    @staticmethod
    def calculate(trades: List[Trade], equity_curve: List[Dict], 
                  initial_balance: float, final_balance: float,
                  days: int) -> BacktestMetrics:
        """Calculate all metrics from trades and equity curve"""
        metrics = BacktestMetrics()
        
        if not trades:
            return metrics
        
        # Basic counts
        metrics.total_trades = len(trades)
        wins = [t for t in trades if t.pnl > 0]
        losses = [t for t in trades if t.pnl <= 0]
        metrics.winning_trades = len(wins)
        metrics.losing_trades = len(losses)
        metrics.win_rate = len(wins) / len(trades) * 100 if trades else 0
        
        # Returns
        metrics.total_return = final_balance - initial_balance
        metrics.total_return_percent = (final_balance - initial_balance) / initial_balance * 100
        
        # Annualized return
        if days > 0:
            years = days / 365
            if years > 0 and final_balance > 0 and initial_balance > 0:
                metrics.annualized_return = ((final_balance / initial_balance) ** (1 / years) - 1) * 100
        
        # Trade metrics
        if wins:
            metrics.avg_win = sum(t.pnl_percent for t in wins) / len(wins)
        if losses:
            metrics.avg_loss = abs(sum(t.pnl_percent for t in losses) / len(losses))
        
        if trades:
            metrics.avg_trade = sum(t.pnl_percent for t in trades) / len(trades)
            metrics.avg_bars_in_trade = sum(t.duration_bars for t in trades) / len(trades)
        
        # Profit factor
        gross_profit = sum(t.pnl for t in wins)
        gross_loss = abs(sum(t.pnl for t in losses))
        metrics.profit_factor = gross_profit / gross_loss if gross_loss > 0 else 999
        
        # Payoff ratio
        metrics.payoff_ratio = metrics.avg_win / metrics.avg_loss if metrics.avg_loss > 0 else 0
        
        # Drawdown
        peak = initial_balance
        max_dd = 0
        max_dd_duration = 0
        current_dd_start = 0
        
        for i, point in enumerate(equity_curve):
            equity = point["equity"]
            if equity > peak:
                peak = equity
                if current_dd_start > 0:
                    dd_duration = i - current_dd_start
                    max_dd_duration = max(max_dd_duration, dd_duration)
                current_dd_start = 0
            else:
                if current_dd_start == 0:
                    current_dd_start = i
                dd = (peak - equity) / peak * 100
                max_dd = max(max_dd, dd)
        
        metrics.max_drawdown_percent = max_dd
        
        # Convert bars to days based on equity curve length and total days
        if len(equity_curve) > 0 and days > 0:
            bars_per_day = len(equity_curve) / days
            metrics.max_drawdown_duration_days = max_dd_duration / bars_per_day if bars_per_day > 0 else 0
        
        # Consecutive wins/losses
        current_streak = 0
        max_win_streak = 0
        max_loss_streak = 0
        
        for t in trades:
            if t.pnl > 0:
                if current_streak > 0:
                    current_streak += 1
                else:
                    current_streak = 1
                max_win_streak = max(max_win_streak, current_streak)
            else:
                if current_streak < 0:
                    current_streak -= 1
                else:
                    current_streak = -1
                max_loss_streak = max(max_loss_streak, abs(current_streak))
        
        metrics.max_consecutive_wins = max_win_streak
        metrics.max_consecutive_losses = max_loss_streak
        
        # Risk-adjusted returns
        returns = [t.pnl_percent for t in trades]
        
        if len(returns) >= 2:
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
            std_dev = math.sqrt(variance)
            
            # Sharpe Ratio (annualized)
            if std_dev > 0:
                daily_rf = 0  # Risk-free rate
                metrics.sharpe_ratio = (mean_return - daily_rf) / std_dev * math.sqrt(252)
            
            # Sortino Ratio (downside deviation only)
            negative_returns = [r for r in returns if r < 0]
            if negative_returns:
                downside_variance = sum(r ** 2 for r in negative_returns) / len(returns)
                downside_std = math.sqrt(downside_variance)
                if downside_std > 0:
                    metrics.sortino_ratio = mean_return / downside_std * math.sqrt(252)
        
        # Calmar Ratio
        if metrics.max_drawdown_percent > 0:
            metrics.calmar_ratio = metrics.annualized_return / metrics.max_drawdown_percent
        
        # Recovery Factor
        if metrics.max_drawdown_percent > 0:
            metrics.recovery_factor = metrics.total_return_percent / metrics.max_drawdown_percent
        
        # Expectancy
        if metrics.total_trades > 0:
            metrics.expectancy = (
                (metrics.win_rate / 100 * metrics.avg_win) - 
                ((100 - metrics.win_rate) / 100 * metrics.avg_loss)
            )
        
        # SQN (System Quality Number)
        if len(returns) >= 30:
            mean_r = sum(returns) / len(returns)
            std_r = math.sqrt(sum((r - mean_r) ** 2 for r in returns) / len(returns))
            if std_r > 0:
                metrics.sqn = (mean_r / std_r) * math.sqrt(len(returns))
        
        # Omega Ratio
        threshold = 0  # Minimum acceptable return
        gains_above = sum(r - threshold for r in returns if r > threshold)
        losses_below = sum(threshold - r for r in returns if r <= threshold)
        if losses_below > 0:
            metrics.omega_ratio = gains_above / losses_below
        else:
            metrics.omega_ratio = float('inf') if gains_above > 0 else 0
        
        # Costs
        metrics.total_commission = sum(t.commission for t in trades)
        metrics.total_slippage = sum(t.slippage for t in trades)
        
        return metrics


# =============================================================================
# PRO BACKTEST ENGINE
# =============================================================================

class ProBacktestEngine:
    """Professional-grade backtesting engine"""
    
    def __init__(self):
        self.analyzers = self._load_analyzers()
    
    def _load_analyzers(self) -> Dict:
        """Load strategy analyzers from backtest_engine"""
        try:
            from webapp.services.backtest_engine import (
                RSIBBOIAnalyzer, WyckoffAnalyzer, ElCaroAnalyzer,
                ScryptomeraAnalyzer, ScalperAnalyzer, MeanReversionAnalyzer,
                TrendFollowingAnalyzer, BreakoutAnalyzer, DCAAnalyzer,
                GridAnalyzer, MomentumAnalyzer, VolatilityBreakoutAnalyzer,
                CustomStrategyAnalyzer
            )
            return {
                "rsibboi": RSIBBOIAnalyzer(),
                "wyckoff": WyckoffAnalyzer(),
                "elcaro": ElCaroAnalyzer(),
                "scryptomera": ScryptomeraAnalyzer(),
                "scalper": ScalperAnalyzer(),
                "mean_reversion": MeanReversionAnalyzer(),
                "trend_following": TrendFollowingAnalyzer(),
                "breakout": BreakoutAnalyzer(),
                "dca": DCAAnalyzer(),
                "grid": GridAnalyzer(),
                "momentum": MomentumAnalyzer(),
                "volatility_breakout": VolatilityBreakoutAnalyzer()
            }
        except Exception:
            return {}
    
    async def run(
        self,
        strategy: Optional[str] = None,
        custom_strategy: Optional[Dict] = None,
        symbols: List[str] = ["BTCUSDT"],
        timeframe: str = "1h",
        days: int = 30,
        initial_balance: float = 10000,
        commission: float = 0.1,
        slippage: float = 0.05,
        **kwargs
    ) -> Dict[str, Any]:
        """Run professional backtest"""
        
        config = BacktestConfig(
            symbol=symbols[0],
            timeframe=timeframe,
            days=days,
            initial_balance=initial_balance,
            commission_percent=commission,
            slippage_percent=slippage,
            stop_loss_percent=kwargs.get("stop_loss_percent", 2.0),
            take_profit_percent=kwargs.get("take_profit_percent", 4.0),
            risk_per_trade=kwargs.get("risk_per_trade", 1.0),
            trailing_stop=kwargs.get("trailing_stop", False),
            trailing_stop_activation=kwargs.get("trailing_stop_activation", 2.0),
            trailing_stop_distance=kwargs.get("trailing_stop_distance", 1.0),
            leverage=kwargs.get("leverage", 1),
            position_sizing=kwargs.get("position_sizing", "fixed_percent")
        )
        
        # Multi-symbol support
        all_results = {}
        combined_trades = []
        combined_equity = [{"time": datetime.now().isoformat(), "equity": initial_balance}]
        
        for symbol in symbols:
            config.symbol = symbol
            
            # Fetch data
            candles = await DataFetcher.fetch_candles(symbol, timeframe, days)
            if not candles or len(candles) < 50:
                continue
            
            # Get analyzer
            if custom_strategy:
                from webapp.services.backtest_engine import CustomStrategyAnalyzer
                analyzer = CustomStrategyAnalyzer(custom_strategy, "custom")
            elif strategy and strategy in self.analyzers:
                analyzer = self.analyzers[strategy]
            else:
                continue
            
            # Run backtest for this symbol
            result = await self._run_single(config, candles, analyzer)
            all_results[symbol] = result
            
            if result.get("trades"):
                combined_trades.extend(result["trades"])
        
        if not all_results:
            return self._empty_result(initial_balance)
        
        # Combine results for single symbol case
        if len(symbols) == 1:
            return all_results[symbols[0]]
        
        # Aggregate multi-symbol results
        all_trades = []
        final_equity = initial_balance
        
        for symbol, result in all_results.items():
            trades = result.get("trades", [])
            for t in trades:
                all_trades.append(Trade(**t) if isinstance(t, dict) else t)
            
            pnl = result.get("metrics", {}).get("total_return", 0)
            final_equity += pnl / len(symbols)  # Proportional allocation
        
        # Recalculate metrics
        metrics = MetricsCalculator.calculate(
            all_trades, combined_equity, initial_balance, final_equity, days
        )
        
        return {
            "success": True,
            "metrics": metrics.to_dict(),
            "trades": [t.to_dict() if hasattr(t, 'to_dict') else t for t in all_trades[-100:]],
            "equity_curve": combined_equity,
            "drawdown_curve": [],
            "monthly_returns": [],
            "symbol_results": {s: r.get("metrics", {}) for s, r in all_results.items()}
        }
    
    async def _run_single(self, config: BacktestConfig, candles: List[Dict], 
                          analyzer) -> Dict[str, Any]:
        """Run backtest for a single symbol"""
        
        # Generate signals
        signals = analyzer.analyze(candles)
        
        # Simulation state
        equity = config.initial_balance
        position: Optional[Position] = None
        trades: List[Trade] = []
        equity_curve = [{"time": candles[0]["time"], "equity": equity}]
        drawdown_curve = []
        peak_equity = equity
        
        # Running stats for Kelly
        running_wins = 0
        running_losses = 0
        running_win_pnl = 0
        running_loss_pnl = 0
        
        for i, candle in enumerate(candles):
            if i < 20:  # Warmup period
                continue
            
            current_time = candle["time"]
            current_price = candle["close"]
            signal = signals.get(i, {})
            
            # Check for exit if in position
            if position:
                position.bars_held += 1
                
                # Update trailing stop
                if config.trailing_stop:
                    position.update_trailing(current_price)
                
                exit_reason = self._check_exit(position, candle, config, signal)
                
                if exit_reason:
                    # Calculate PnL
                    exit_price = self._get_exit_price(position, candle, exit_reason, config)
                    
                    # Apply slippage
                    slippage_amount = exit_price * (config.slippage_percent / 100)
                    if position.side == PositionSide.LONG:
                        exit_price -= slippage_amount
                    else:
                        exit_price += slippage_amount
                    
                    # Calculate raw PnL (absolute, not percentage)
                    # Leverage already applied in position size
                    if position.side == PositionSide.LONG:
                        raw_pnl = (exit_price - position.entry_price) * position.size
                    else:
                        raw_pnl = (position.entry_price - exit_price) * position.size
                    
                    # Deduct commission
                    commission = position.size * (config.commission_percent / 100) * 2  # Entry + exit
                    net_pnl = raw_pnl - commission
                    pnl_percent = net_pnl / position.size * 100
                    
                    # Create trade record
                    trade = Trade(
                        entry_time=position.entry_time,
                        exit_time=current_time,
                        symbol=config.symbol,
                        side=position.side.value,
                        entry_price=position.entry_price,
                        exit_price=exit_price,
                        size=position.size,
                        pnl=net_pnl,
                        pnl_percent=pnl_percent,
                        commission=commission,
                        slippage=slippage_amount * 2,
                        reason=exit_reason.value,
                        duration_bars=position.bars_held
                    )
                    trades.append(trade)
                    
                    # Update equity
                    equity += net_pnl
                    equity_curve.append({"time": current_time, "equity": equity})
                    
                    # Update running stats
                    if net_pnl > 0:
                        running_wins += 1
                        running_win_pnl += pnl_percent
                    else:
                        running_losses += 1
                        running_loss_pnl += abs(pnl_percent)
                    
                    # Drawdown
                    if equity > peak_equity:
                        peak_equity = equity
                    dd = (peak_equity - equity) / peak_equity * 100
                    drawdown_curve.append({"time": current_time, "drawdown": dd})
                    
                    # Check max drawdown stop
                    if dd >= config.max_drawdown_percent:
                        break  # Stop trading
                    
                    position = None
            
            # Check for entry if no position
            if not position and signal.get("direction"):
                direction = PositionSide.LONG if signal["direction"] == "LONG" else PositionSide.SHORT
                
                # Calculate position size
                win_rate = running_wins / (running_wins + running_losses) * 100 if (running_wins + running_losses) > 0 else 50
                payoff = (running_win_pnl / running_wins) / (running_loss_pnl / running_losses) if running_losses > 0 and running_wins > 0 else 2.0
                
                size = PositionSizer.calculate_size(config, equity, win_rate, payoff)
                
                if size <= 0:
                    continue
                
                # Apply entry slippage
                entry_price = current_price
                slippage_amount = entry_price * (config.slippage_percent / 100)
                if direction == PositionSide.LONG:
                    entry_price += slippage_amount
                else:
                    entry_price -= slippage_amount
                
                # Calculate stops
                if direction == PositionSide.LONG:
                    stop_loss = entry_price * (1 - config.stop_loss_percent / 100)
                    take_profit = entry_price * (1 + config.take_profit_percent / 100)
                else:
                    stop_loss = entry_price * (1 + config.stop_loss_percent / 100)
                    take_profit = entry_price * (1 - config.take_profit_percent / 100)
                
                position = Position(
                    entry_time=current_time,
                    entry_price=entry_price,
                    side=direction,
                    size=size,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    trailing_stop=config.trailing_stop,
                    trailing_stop_distance=config.trailing_stop_distance,
                    trailing_stop_activation=config.trailing_stop_activation,
                    highest_price=entry_price,
                    lowest_price=entry_price,
                    max_bars=config.max_bars_in_trade
                )
        
        # Close any remaining position at end
        if position:
            last_candle = candles[-1]
            exit_price = last_candle["close"]
            
            # Calculate raw PnL (absolute, not percentage)
            # Leverage already applied in position size
            if position.side == PositionSide.LONG:
                raw_pnl = (exit_price - position.entry_price) * position.size
            else:
                raw_pnl = (position.entry_price - exit_price) * position.size
            
            commission = position.size * (config.commission_percent / 100) * 2
            net_pnl = raw_pnl - commission
            
            trade = Trade(
                entry_time=position.entry_time,
                exit_time=last_candle["time"],
                symbol=config.symbol,
                side=position.side.value,
                entry_price=position.entry_price,
                exit_price=exit_price,
                size=position.size,
                pnl=net_pnl,
                pnl_percent=net_pnl / position.size * 100,
                commission=commission,
                slippage=0,
                reason=ExitReason.EOB.value,
                duration_bars=position.bars_held
            )
            trades.append(trade)
            equity += net_pnl
            equity_curve.append({"time": last_candle["time"], "equity": equity})
        
        # Calculate metrics
        metrics = MetricsCalculator.calculate(
            trades, equity_curve, config.initial_balance, equity, config.days
        )
        
        # Monthly returns
        monthly_returns = self._calculate_monthly_returns(trades)
        
        return {
            "success": True,
            "metrics": metrics.to_dict(),
            "trades": [t.to_dict() for t in trades[-100:]],  # Last 100 trades
            "equity_curve": equity_curve,
            "drawdown_curve": drawdown_curve,
            "monthly_returns": monthly_returns
        }
    
    def _check_exit(self, position: Position, candle: Dict, config: BacktestConfig,
                    signal: Dict) -> Optional[ExitReason]:
        """Check if position should be exited"""
        
        # Time-based exit
        if config.max_bars_in_trade > 0 and position.bars_held >= config.max_bars_in_trade:
            return ExitReason.TIME_EXIT
        
        if position.side == PositionSide.LONG:
            # Stop loss hit
            if candle["low"] <= position.stop_loss:
                if position.trailing_stop_triggered:
                    return ExitReason.TRAILING_STOP
                return ExitReason.SL
            
            # Take profit hit
            if candle["high"] >= position.take_profit:
                return ExitReason.TP
            
            # Signal exit
            if signal.get("direction") == "SHORT":
                return ExitReason.SIGNAL
        
        else:  # SHORT
            # Stop loss hit
            if candle["high"] >= position.stop_loss:
                if position.trailing_stop_triggered:
                    return ExitReason.TRAILING_STOP
                return ExitReason.SL
            
            # Take profit hit
            if candle["low"] <= position.take_profit:
                return ExitReason.TP
            
            # Signal exit
            if signal.get("direction") == "LONG":
                return ExitReason.SIGNAL
        
        return None
    
    def _get_exit_price(self, position: Position, candle: Dict, 
                        reason: ExitReason, config: BacktestConfig) -> float:
        """Get the exit price based on exit reason"""
        if reason in [ExitReason.SL, ExitReason.TRAILING_STOP]:
            return position.stop_loss
        elif reason == ExitReason.TP:
            return position.take_profit
        else:
            return candle["close"]
    
    def _calculate_monthly_returns(self, trades: List[Trade]) -> List[Dict]:
        """Calculate returns grouped by month"""
        if not trades:
            return []
        
        monthly = {}
        for t in trades:
            try:
                month = t.entry_time[:7]  # YYYY-MM
                if month not in monthly:
                    monthly[month] = {"month": month, "trades": 0, "pnl": 0, "win_rate": 0}
                monthly[month]["trades"] += 1
                monthly[month]["pnl"] += t.pnl_percent
                if t.pnl > 0:
                    monthly[month]["win_rate"] += 1
            except (TypeError, AttributeError, KeyError) as e:
                logger.debug(f"Failed to process trade for monthly breakdown: {e}")
                continue
        
        result = []
        for m, data in sorted(monthly.items()):
            if data["trades"] > 0:
                data["win_rate"] = data["win_rate"] / data["trades"] * 100
            result.append(data)
        
        return result
    
    def _empty_result(self, initial_balance: float) -> Dict:
        """Return empty result"""
        return {
            "success": True,
            "metrics": BacktestMetrics().to_dict(),
            "trades": [],
            "equity_curve": [{"time": datetime.now().isoformat(), "equity": initial_balance}],
            "drawdown_curve": [],
            "monthly_returns": []
        }
    
    async def run_portfolio(
        self,
        strategies: List[Dict],
        symbols: List[str],
        timeframe: str,
        days: int,
        initial_balance: float,
        rebalance_frequency: str = "daily",
        correlation_limit: float = 0.7
    ) -> Dict[str, Any]:
        """Run portfolio backtest with multiple strategies"""
        
        # Run each strategy independently
        strategy_results = {}
        for strat_config in strategies:
            strategy_name = strat_config.get("strategy", "elcaro")
            result = await self.run(
                strategy=strategy_name,
                symbols=symbols,
                timeframe=timeframe,
                days=days,
                initial_balance=initial_balance / len(strategies),
                **strat_config
            )
            strategy_results[strategy_name] = result
        
        # Calculate correlation matrix
        correlation_matrix = self._calculate_correlation(strategy_results)
        
        # Calculate optimal weights (simplified mean-variance)
        weights = self._calculate_weights(strategy_results, correlation_limit)
        
        # Aggregate metrics
        total_return = sum(
            r.get("metrics", {}).get("total_return_percent", 0) * weights.get(s, 1/len(strategies))
            for s, r in strategy_results.items()
        )
        
        return {
            "success": True,
            "portfolio_metrics": {
                "total_return_percent": total_return,
                "strategies_count": len(strategies),
                "symbols_count": len(symbols)
            },
            "strategy_contributions": {
                s: r.get("metrics", {}).get("total_return_percent", 0) * weights.get(s, 0)
                for s, r in strategy_results.items()
            },
            "correlation_matrix": correlation_matrix,
            "optimal_weights": weights,
            "equity_curve": []
        }
    
    def _calculate_correlation(self, results: Dict[str, Dict]) -> Dict[str, Dict[str, float]]:
        """Calculate correlation matrix between strategies"""
        # Simplified - in reality would use daily returns
        strategies = list(results.keys())
        matrix = {}
        
        for s1 in strategies:
            matrix[s1] = {}
            for s2 in strategies:
                if s1 == s2:
                    matrix[s1][s2] = 1.0
                else:
                    # Simplified correlation based on win rate similarity
                    wr1 = results[s1].get("metrics", {}).get("win_rate", 50)
                    wr2 = results[s2].get("metrics", {}).get("win_rate", 50)
                    matrix[s1][s2] = 1 - abs(wr1 - wr2) / 100
        
        return matrix
    
    def _calculate_weights(self, results: Dict[str, Dict], 
                          correlation_limit: float) -> Dict[str, float]:
        """Calculate optimal portfolio weights"""
        strategies = list(results.keys())
        n = len(strategies)
        
        if n == 0:
            return {}
        
        # Simple Sharpe-based weighting
        sharpes = {
            s: max(0.1, results[s].get("metrics", {}).get("sharpe_ratio", 0.1))
            for s in strategies
        }
        
        total_sharpe = sum(sharpes.values())
        weights = {s: sharpes[s] / total_sharpe for s in strategies}
        
        return weights
    
    # =========================================================================
    # API WRAPPER METHODS
    # =========================================================================
    
    async def run_backtest(
        self,
        symbols: List[str],
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
        analyzer_name: str,
        initial_balance: float = 10000,
        tp_percent: float = 5.0,
        sl_percent: float = 2.0,
        position_size_percent: float = 10.0,
        leverage: int = 10,
        trailing_stop: bool = False,
        trailing_percent: float = 1.0
    ) -> Dict[str, Any]:
        """
        Simplified API for running backtests on built-in strategies.
        Used by the strategy_backtest API.
        """
        # Calculate days from date range
        days = (end_date - start_date).days
        if days <= 0:
            days = 30
        
        # Run the backtest
        result = await self.run(
            strategy=analyzer_name,
            symbols=symbols,
            timeframe=timeframe,
            days=days,
            initial_balance=initial_balance,
            take_profit_percent=tp_percent,
            stop_loss_percent=sl_percent,
            risk_per_trade=position_size_percent / 10,  # Convert to risk %
            leverage=leverage,
            trailing_stop=trailing_stop,
            trailing_stop_distance=trailing_percent,
            trailing_stop_activation=1.0
        )
        
        # Add date info
        result["start_date"] = start_date
        result["end_date"] = end_date
        result["initial_balance"] = initial_balance
        result["final_balance"] = initial_balance + result.get("metrics", {}).get("total_return", 0)
        
        # Build per-symbol breakdown
        per_symbol = {}
        if "symbol_results" in result:
            for symbol, metrics in result["symbol_results"].items():
                per_symbol[symbol] = {
                    "total_trades": metrics.get("total_trades", 0),
                    "win_rate": metrics.get("win_rate", 0),
                    "profit_factor": metrics.get("profit_factor", 0),
                    "total_pnl": metrics.get("total_return", 0),
                    "total_pnl_percent": metrics.get("total_return_percent", 0),
                    "max_drawdown": metrics.get("max_drawdown_percent", 0),
                    "sharpe": metrics.get("sharpe_ratio", 0),
                    "avg_duration": "1h",
                    "best_trade": 0,
                    "worst_trade": 0
                }
        else:
            # Single symbol
            metrics = result.get("metrics", {})
            for symbol in symbols:
                per_symbol[symbol] = {
                    "total_trades": metrics.get("total_trades", 0),
                    "win_rate": metrics.get("win_rate", 0),
                    "profit_factor": metrics.get("profit_factor", 0),
                    "total_pnl": metrics.get("total_return", 0),
                    "total_pnl_percent": metrics.get("total_return_percent", 0),
                    "max_drawdown": metrics.get("max_drawdown_percent", 0),
                    "sharpe": metrics.get("sharpe_ratio", 0),
                    "avg_duration": "1h",
                    "best_trade": 0,
                    "worst_trade": 0
                }
        
        result["per_symbol"] = per_symbol
        
        return result
    
    async def run_backtest_with_custom_analyzer(
        self,
        symbols: List[str],
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
        analyzer_func,  # Callable that returns signals
        initial_balance: float = 10000,
        tp_percent: float = 5.0,
        sl_percent: float = 2.0,
        position_size_percent: float = 10.0,
        leverage: int = 10
    ) -> Dict[str, Any]:
        """
        Run backtest with a custom analyzer function.
        Used for user-defined strategies from the strategy builder.
        """
        days = (end_date - start_date).days
        if days <= 0:
            days = 30
        
        config = BacktestConfig(
            symbol=symbols[0],
            timeframe=timeframe,
            days=days,
            initial_balance=initial_balance,
            take_profit_percent=tp_percent,
            stop_loss_percent=sl_percent,
            risk_per_trade=position_size_percent / 10,
            leverage=leverage
        )
        
        all_results = {}
        all_trades = []
        
        for symbol in symbols:
            config.symbol = symbol
            
            # Fetch data
            candles = await DataFetcher.fetch_candles(symbol, timeframe, days)
            if not candles or len(candles) < 50:
                continue
            
            # Run custom analyzer
            try:
                analysis = await analyzer_func(candles, {"symbol": symbol})
                signals_list = analysis.get("signals", [])
                
                # Convert to index-based signals dict
                signals = {}
                for sig in signals_list:
                    idx = sig.get("index", 0)
                    action = sig.get("action", "")
                    
                    if action == "long":
                        signals[idx] = {"action": "BUY", "signal": 1}
                    elif action == "short":
                        signals[idx] = {"action": "SELL", "signal": -1}
                    elif action in ("exit_long", "exit_short"):
                        signals[idx] = {"action": "EXIT", "exit_signal": True}
                
                # Create wrapper analyzer
                class WrapperAnalyzer:
                    def __init__(self, signals_dict):
                        self._signals = signals_dict
                    
                    def analyze(self, candles):
                        return self._signals
                
                analyzer = WrapperAnalyzer(signals)
                
                # Run backtest for this symbol
                result = await self._run_single(config, candles, analyzer)
                all_results[symbol] = result
                
                if result.get("trades"):
                    all_trades.extend(result["trades"])
                    
            except Exception as e:
                continue
        
        if not all_results:
            return self._empty_result(initial_balance)
        
        # Aggregate results
        final_equity = initial_balance
        for symbol, result in all_results.items():
            pnl = result.get("metrics", {}).get("total_return", 0)
            final_equity += pnl / len(symbols)
        
        # Calculate combined metrics
        metrics = MetricsCalculator.calculate(
            [Trade(**t) if isinstance(t, dict) else t for t in all_trades],
            [], initial_balance, final_equity, days
        )
        
        # Build per-symbol breakdown
        per_symbol = {}
        for symbol, result in all_results.items():
            m = result.get("metrics", {})
            per_symbol[symbol] = {
                "total_trades": m.get("total_trades", 0),
                "win_rate": m.get("win_rate", 0),
                "profit_factor": m.get("profit_factor", 0),
                "total_pnl": m.get("total_return", 0),
                "total_pnl_percent": m.get("total_return_percent", 0),
                "max_drawdown": m.get("max_drawdown_percent", 0),
                "sharpe": m.get("sharpe_ratio", 0),
                "avg_duration": "1h",
                "best_trade": 0,
                "worst_trade": 0
            }
        
        return {
            "success": True,
            "start_date": start_date,
            "end_date": end_date,
            "initial_balance": initial_balance,
            "final_balance": final_equity,
            "metrics": metrics.to_dict(),
            "trades": all_trades[-500:],
            "equity_curve": [],
            "per_symbol": per_symbol,
            "monthly_returns": {}
        }


# =============================================================================
# MARKET REPLAY ENGINE
# =============================================================================

class MarketReplayEngine:
    """Engine for visual market replay backtesting"""
    
    def __init__(self):
        self.candles: List[Dict] = []
        self.current_index: int = 0
        self.strategy = None
        self.signals: Dict = {}
        self.equity: float = 10000
        self.trades: List[Dict] = []
        self.position = None
    
    async def initialize(self, symbol: str, timeframe: str, 
                        start_date: str = None, end_date: str = None,
                        strategy: str = None):
        """Initialize replay with data and strategy"""
        
        # Calculate days from dates
        if start_date and end_date:
            try:
                start = datetime.fromisoformat(start_date)
                end = datetime.fromisoformat(end_date)
                days = (end - start).days
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse replay dates: {e}")
                days = 30
        else:
            days = 30
        
        self.candles = await DataFetcher.fetch_candles(symbol, timeframe, days)
        self.current_index = 0
        
        if strategy:
            engine = ProBacktestEngine()
            if strategy in engine.analyzers:
                analyzer = engine.analyzers[strategy]
                self.signals = analyzer.analyze(self.candles)
    
    async def next_candle(self) -> Optional[Dict]:
        """Get next candle with analysis"""
        if self.current_index >= len(self.candles):
            return None
        
        candle = self.candles[self.current_index]
        signal = self.signals.get(self.current_index, {})
        
        result = {
            "candle": candle,
            "signal": signal,
            "index": self.current_index,
            "progress": (self.current_index + 1) / len(self.candles) * 100
        }
        
        self.current_index += 1
        return result
    
    def get_final_equity(self) -> float:
        return self.equity
    
    def get_total_trades(self) -> int:
        return len(self.trades)

