"""
Real Backtest Engine - Connected to Actual Bot Strategy Logic
Based on analyzers from: elcaro, aiboll, spain_rsibb_oi, fibo_bot, pazzle, damp
"""
import aiohttp
import asyncio
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import math

# Setup logging
logger = logging.getLogger(__name__)

# Error handling decorator for strategy analyzers
def safe_analyze(func):
    """Decorator to safely execute analyzer with error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ZeroDivisionError, ValueError, IndexError, KeyError, TypeError) as e:
            logger.error(f"Analyzer {func.__name__} failed: {e}")
            return {}  # Return empty signals on error
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            return {}
    return wrapper

# In-memory cache for historical data (5 min TTL)
_data_cache: Dict[str, tuple] = {}
_cache_ttl = 300  # 5 minutes

DB_FILE = Path(__file__).parent.parent.parent / "bot.db"

# Trading costs configuration
class TradingCosts:
    """Realistic trading costs for backtesting"""
    BYBIT_MAKER_FEE = 0.00055  # 0.055% maker fee
    BYBIT_TAKER_FEE = 0.00075  # 0.075% taker fee
    SLIPPAGE = 0.0005          # 0.05% slippage
    
    @classmethod
    def calculate(cls, entry_value: float, exit_value: float, is_maker: bool = False) -> float:
        """Calculate total trading costs (commissions + slippage)"""
        entry_fee = entry_value * (cls.BYBIT_MAKER_FEE if is_maker else cls.BYBIT_TAKER_FEE)
        exit_fee = exit_value * cls.BYBIT_TAKER_FEE  # Exit usually market order
        slippage = entry_value * cls.SLIPPAGE
        return entry_fee + exit_fee + slippage


@dataclass
class Trade:
    entry_time: str
    exit_time: str
    symbol: str
    direction: str  # LONG or SHORT
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    pnl_percent: float
    reason: str  # TP, SL, SIGNAL


@dataclass
class BacktestResult:
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    total_pnl_percent: float
    profit_factor: float
    max_drawdown_percent: float
    sharpe_ratio: float
    final_balance: float
    trades: List[Dict]
    equity_curve: List[Dict]


class RealBacktestEngine:
    """Backtest engine using real strategy logic from bot analyzers"""
    
    def __init__(self):
        self.analyzers = {
            # Core strategies
            "rsibboi": RSIBBOIAnalyzer(),
            "wyckoff": WyckoffAnalyzer(),
            "elcaro": ElCaroAnalyzer(),
            "scryptomera": ScryptomeraAnalyzer(),
            "scalper": ScalperAnalyzer(),
            # Advanced strategies
            "mean_reversion": MeanReversionAnalyzer(),
            "trend_following": TrendFollowingAnalyzer(),
            "breakout": BreakoutAnalyzer(),
            "dca": DCAAnalyzer(),
            "grid": GridAnalyzer(),
            "momentum": MomentumAnalyzer(),
            "volatility_breakout": VolatilityBreakoutAnalyzer(),
        }
    
    async def fetch_historical_data(self, symbol: str, timeframe: str, days: int) -> List[Dict]:
        """Fetch OHLCV data from Binance with caching - UNLIMITED data via pagination"""
        cache_key = f"{symbol}_{timeframe}_{days}"
        now = datetime.now().timestamp()
        
        # Check cache
        if cache_key in _data_cache:
            cached_data, cached_time = _data_cache[cache_key]
            if now - cached_time < _cache_ttl:
                return cached_data
        
        tf_map = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d"}
        interval = tf_map.get(timeframe, "1h")
        
        # Calculate total candles needed
        candles_per_day = {"1m": 1440, "5m": 288, "15m": 96, "1h": 24, "4h": 6, "1d": 1}
        total_candles_needed = days * candles_per_day.get(interval, 24)
        
        # Binance API limit is 1000, so we paginate
        all_candles = []
        end_time = int(datetime.now().timestamp() * 1000)
        
        async with aiohttp.ClientSession() as session:
            while len(all_candles) < total_candles_needed:
                limit = min(1000, total_candles_needed - len(all_candles))
                url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}&endTime={end_time}"
                
                async with session.get(url) as resp:
                    if resp.status != 200:
                        logger.error(f"Binance API error: {resp.status}")
                        break
                    
                    data = await resp.json()
                    if not data:
                        break
                    
                    # Validate and parse candles
                    batch = []
                    for k in data:
                        try:
                            candle = {
                                "time": datetime.fromtimestamp(k[0] / 1000).isoformat(),
                                "timestamp": k[0],
                                "open": float(k[1]),
                                "high": float(k[2]),
                                "low": float(k[3]),
                                "close": float(k[4]),
                                "volume": float(k[5])
                            }
                            # Data validation
                            if candle["high"] < candle["low"]:
                                logger.warning(f"Invalid candle: high < low")
                                continue
                            if any(candle[x] <= 0 for x in ["open", "high", "low", "close"]):
                                logger.warning(f"Invalid candle: price <= 0")
                                continue
                            if candle["volume"] < 0:
                                logger.warning(f"Invalid candle: negative volume")
                                continue
                            batch.append(candle)
                        except (ValueError, IndexError, TypeError, KeyError) as e:
                            logger.error(f"Failed to parse candle: {e}")
                            continue
                    
                    all_candles = batch + all_candles  # Prepend older candles
                    
                    # Set end_time for next batch (1ms before oldest candle)
                    end_time = data[0][0] - 1
                    
                    # Safety: avoid infinite loop
                    if len(data) < limit:
                        break
        
        # Cache the data
        if all_candles:
            _data_cache[cache_key] = (all_candles, now)
        
        return all_candles
    
    def get_custom_strategy_analyzer(self, strategy_id: int) -> Optional["CustomStrategyAnalyzer"]:
        """Load a custom strategy from database and create analyzer"""
        try:
            conn = sqlite3.connect(str(DB_FILE))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM custom_strategies WHERE id = ? AND is_active = 1", (strategy_id,))
            row = cur.fetchone()
            conn.close()
            
            if row:
                config = json.loads(row["config_json"])
                return CustomStrategyAnalyzer(config, row["base_strategy"])
            return None
        except Exception:
            return None
    
    async def run_backtest_with_config(
        self,
        strategy_config: 'StrategyConfig',
        symbol: str,
        timeframe: str,
        days: int,
        initial_balance: float
    ) -> Dict[str, Any]:
        """
        Run backtest using StrategyConfig object with custom parameters
        Allows full customization of indicators and parameters
        """
        # Import here to avoid circular dependency
        from webapp.services.strategy_parameters import StrategyConfig
        
        # Fetch historical data
        candles = await self.fetch_historical_data(symbol, timeframe, days)
        
        if not candles or len(candles) < 50:
            return self._empty_result(initial_balance)
        
        # Get analyzer based on base strategy
        analyzer = self.analyzers.get(strategy_config.base_strategy)
        if not analyzer:
            return self._empty_result(initial_balance)
        
        # Apply custom parameters to analyzer
        analyzer = self._create_custom_analyzer(strategy_config, analyzer)
        
        # Run strategy analysis
        signals = analyzer.analyze(candles)
        
        # Use strategy config parameters for risk management
        risk_per_trade = strategy_config.risk_per_trade
        stop_loss_percent = strategy_config.stop_loss_percent
        take_profit_percent = strategy_config.take_profit_percent
        
        # Simulate trades
        trades = []
        equity = initial_balance
        equity_curve = [{"time": candles[0]["time"], "equity": equity}]
        
        position = None
        
        for i, candle in enumerate(candles):
            if i < 20:  # Skip first candles for indicator warmup
                continue
            
            signal = signals.get(i, {})
            
            # Check for exit
            if position:
                exit_signal = self._check_exit(position, candle, stop_loss_percent, take_profit_percent, signal)
                if exit_signal:
                    pnl = self._calculate_pnl(position, candle["close"])
                    equity += pnl
                    
                    trades.append({
                        "entry_time": position["entry_time"],
                        "exit_time": candle["time"],
                        "symbol": symbol,
                        "direction": position["direction"],
                        "entry_price": position["entry_price"],
                        "exit_price": candle["close"],
                        "size": position["size"],
                        "pnl": pnl,
                        "pnl_percent": (pnl / position["size"]) * 100,
                        "reason": exit_signal
                    })
                    
                    equity_curve.append({"time": candle["time"], "equity": equity})
                    position = None
            
            # Check for entry
            if not position and signal.get("direction"):
                size = equity * (risk_per_trade / 100) / (stop_loss_percent / 100)
                position = {
                    "entry_time": candle["time"],
                    "entry_price": candle["close"],
                    "direction": signal["direction"],
                    "size": size,
                    "stop_loss": candle["close"] * (1 - stop_loss_percent / 100) if signal["direction"] == "LONG" else candle["close"] * (1 + stop_loss_percent / 100),
                    "take_profit": candle["close"] * (1 + take_profit_percent / 100) if signal["direction"] == "LONG" else candle["close"] * (1 - take_profit_percent / 100)
                }
        
        # Close any remaining position
        if position:
            pnl = self._calculate_pnl(position, candles[-1]["close"])
            equity += pnl
            trades.append({
                "entry_time": position["entry_time"],
                "exit_time": candles[-1]["time"],
                "symbol": symbol,
                "direction": position["direction"],
                "entry_price": position["entry_price"],
                "exit_price": candles[-1]["close"],
                "size": position["size"],
                "pnl": pnl,
                "pnl_percent": (pnl / position["size"]) * 100,
                "reason": "EOB"
            })
            equity_curve.append({"time": candles[-1]["time"], "equity": equity})
        
        # Calculate statistics
        return self._calculate_statistics(trades, equity_curve, initial_balance, equity)
    
    def _create_custom_analyzer(self, strategy_config: 'StrategyConfig', base_analyzer):
        """
        Create custom analyzer with modified parameters based on StrategyConfig
        """
        # Clone the analyzer
        import copy
        custom_analyzer = copy.deepcopy(base_analyzer)
        
        # Apply custom indicator parameters
        for ind_name, indicator in strategy_config.indicators.items():
            if not indicator.enabled:
                continue
            
            # Update analyzer parameters based on indicator type
            if hasattr(custom_analyzer, '_apply_custom_params'):
                custom_analyzer._apply_custom_params(ind_name, indicator.params)
        
        return custom_analyzer
    
    async def run_backtest(
        self,
        strategy: str,
        symbol: str,
        timeframe: str,
        days: int,
        initial_balance: float,
        risk_per_trade: float = 1.0,
        stop_loss_percent: float = 2.0,
        take_profit_percent: float = 4.0,
        custom_strategy_id: int = None
    ) -> Dict[str, Any]:
        """Run backtest for a specific strategy or custom strategy"""
        
        # Fetch historical data
        candles = await self.fetch_historical_data(symbol, timeframe, days)
        
        if not candles or len(candles) < 50:
            return self._empty_result(initial_balance)
        
        # Get analyzer - either built-in or custom
        if custom_strategy_id:
            analyzer = self.get_custom_strategy_analyzer(custom_strategy_id)
            if not analyzer:
                return self._empty_result(initial_balance)
        else:
            analyzer = self.analyzers.get(strategy)
            if not analyzer:
                return self._empty_result(initial_balance)
        
        # Run strategy analysis
        signals = analyzer.analyze(candles)
        
        # Simulate trades
        trades = []
        equity = initial_balance
        equity_curve = [{"time": candles[0]["time"], "equity": equity}]
        
        position = None
        
        for i, candle in enumerate(candles):
            if i < 20:  # Skip first candles for indicator warmup
                continue
            
            signal = signals.get(i, {})
            
            # Check for exit
            if position:
                exit_signal = self._check_exit(position, candle, stop_loss_percent, take_profit_percent, signal)
                if exit_signal:
                    pnl = self._calculate_pnl(position, candle["close"])
                    equity += pnl
                    
                    trades.append({
                        "entry_time": position["entry_time"],
                        "exit_time": candle["time"],
                        "symbol": symbol,
                        "direction": position["direction"],
                        "entry_price": position["entry_price"],
                        "exit_price": candle["close"],
                        "size": position["size"],
                        "pnl": pnl,
                        "pnl_percent": (pnl / position["size"]) * 100,
                        "reason": exit_signal
                    })
                    
                    equity_curve.append({"time": candle["time"], "equity": equity})
                    position = None
            
            # Check for entry
            if not position and signal.get("direction"):
                size = equity * (risk_per_trade / 100) / (stop_loss_percent / 100)
                position = {
                    "entry_time": candle["time"],
                    "entry_price": candle["close"],
                    "direction": signal["direction"],
                    "size": size,
                    "stop_loss": candle["close"] * (1 - stop_loss_percent / 100) if signal["direction"] == "LONG" else candle["close"] * (1 + stop_loss_percent / 100),
                    "take_profit": candle["close"] * (1 + take_profit_percent / 100) if signal["direction"] == "LONG" else candle["close"] * (1 - take_profit_percent / 100)
                }
        
        # Close any remaining position
        if position:
            pnl = self._calculate_pnl(position, candles[-1]["close"])
            equity += pnl
            trades.append({
                "entry_time": position["entry_time"],
                "exit_time": candles[-1]["time"],
                "symbol": symbol,
                "direction": position["direction"],
                "entry_price": position["entry_price"],
                "exit_price": candles[-1]["close"],
                "size": position["size"],
                "pnl": pnl,
                "pnl_percent": (pnl / position["size"]) * 100,
                "reason": "EOB"  # End of backtest
            })
            equity_curve.append({"time": candles[-1]["time"], "equity": equity})
        
        return self._calculate_statistics(trades, equity_curve, initial_balance, equity)
    
    async def run_multi_symbol_backtest(
        self,
        strategy: str,
        symbols: List[str],
        timeframe: str,
        days: int,
        initial_balance: float,
        risk_per_trade: float = 1.0,
        stop_loss_percent: float = 2.0,
        take_profit_percent: float = 4.0,
        allocation_mode: str = "equal"  # "equal", "weighted", "dynamic"
    ) -> Dict[str, Any]:
        """Run backtest across multiple symbols simultaneously"""
        
        if not symbols:
            return self._empty_result(initial_balance)
        
        # Fetch all symbol data concurrently
        data_tasks = [self.fetch_historical_data(s, timeframe, days) for s in symbols]
        all_candles = await asyncio.gather(*data_tasks)
        
        symbol_candles = {s: c for s, c in zip(symbols, all_candles) if c and len(c) >= 50}
        
        if not symbol_candles:
            return self._empty_result(initial_balance)
        
        # Get analyzer
        analyzer = self.analyzers.get(strategy)
        if not analyzer:
            return self._empty_result(initial_balance)
        
        # Calculate signals for all symbols
        symbol_signals = {}
        for symbol, candles in symbol_candles.items():
            symbol_signals[symbol] = analyzer.analyze(candles)
        
        # Determine allocation per symbol
        n_symbols = len(symbol_candles)
        if allocation_mode == "equal":
            allocations = {s: 1.0 / n_symbols for s in symbol_candles}
        else:
            allocations = {s: 1.0 / n_symbols for s in symbol_candles}  # Default to equal
        
        # Aggregate all trades across symbols
        all_trades = []
        positions = {}  # symbol -> position
        equity = initial_balance
        equity_curve = []
        
        # Find common time range
        min_len = min(len(c) for c in symbol_candles.values())
        
        for i in range(20, min_len):
            timestamp = None
            
            for symbol, candles in symbol_candles.items():
                candle = candles[i]
                if not timestamp:
                    timestamp = candle["time"]
                
                signal = symbol_signals[symbol].get(i, {})
                
                # Check for exit
                if symbol in positions:
                    pos = positions[symbol]
                    exit_signal = self._check_exit(pos, candle, stop_loss_percent, take_profit_percent, signal)
                    if exit_signal:
                        pnl = self._calculate_pnl(pos, candle["close"])
                        equity += pnl
                        
                        all_trades.append({
                            "entry_time": pos["entry_time"],
                            "exit_time": candle["time"],
                            "symbol": symbol,
                            "direction": pos["direction"],
                            "entry_price": pos["entry_price"],
                            "exit_price": candle["close"],
                            "size": pos["size"],
                            "pnl": pnl,
                            "pnl_percent": (pnl / pos["size"]) * 100,
                            "reason": exit_signal
                        })
                        del positions[symbol]
                
                # Check for entry
                if symbol not in positions and signal.get("direction"):
                    symbol_equity = equity * allocations[symbol]
                    size = symbol_equity * (risk_per_trade / 100) / (stop_loss_percent / 100)
                    
                    positions[symbol] = {
                        "entry_time": candle["time"],
                        "entry_price": candle["close"],
                        "direction": signal["direction"],
                        "size": size,
                        "stop_loss": candle["close"] * (1 - stop_loss_percent / 100) if signal["direction"] == "LONG" else candle["close"] * (1 + stop_loss_percent / 100),
                        "take_profit": candle["close"] * (1 + take_profit_percent / 100) if signal["direction"] == "LONG" else candle["close"] * (1 - take_profit_percent / 100)
                    }
            
            if timestamp:
                equity_curve.append({"time": timestamp, "equity": equity})
        
        # Close remaining positions
        for symbol, pos in positions.items():
            candles = symbol_candles[symbol]
            final_candle = candles[-1]
            pnl = self._calculate_pnl(pos, final_candle["close"])
            equity += pnl
            all_trades.append({
                "entry_time": pos["entry_time"],
                "exit_time": final_candle["time"],
                "symbol": symbol,
                "direction": pos["direction"],
                "entry_price": pos["entry_price"],
                "exit_price": final_candle["close"],
                "size": pos["size"],
                "pnl": pnl,
                "pnl_percent": (pnl / pos["size"]) * 100,
                "reason": "EOB"
            })
        
        result = self._calculate_statistics(all_trades, equity_curve, initial_balance, equity)
        result["symbols_tested"] = list(symbol_candles.keys())
        result["trades_by_symbol"] = {s: len([t for t in all_trades if t["symbol"] == s]) for s in symbol_candles}
        
        return result
    
    async def run_walk_forward_optimization(
        self,
        strategy: str,
        symbol: str,
        timeframe: str,
        total_days: int,
        in_sample_ratio: float = 0.7,  # 70% for optimization
        n_folds: int = 3,  # Number of walk-forward folds
        param_ranges: Dict[str, List] = None,
        initial_balance: float = 10000
    ) -> Dict[str, Any]:
        """
        Walk-forward optimization to prevent overfitting.
        Splits data into in-sample (IS) for optimization and out-of-sample (OOS) for validation.
        """
        
        candles = await self.fetch_historical_data(symbol, timeframe, total_days)
        if not candles or len(candles) < 100:
            return {"error": "Insufficient data", "results": []}
        
        total_candles = len(candles)
        fold_size = total_candles // n_folds
        
        # Default parameter ranges
        if not param_ranges:
            param_ranges = {
                "stop_loss_percent": [1.0, 1.5, 2.0, 2.5, 3.0],
                "take_profit_percent": [2.0, 3.0, 4.0, 5.0, 6.0],
                "risk_per_trade": [0.5, 1.0, 1.5, 2.0]
            }
        
        fold_results = []
        best_params_history = []
        oos_trades = []
        oos_equity_curve = []
        running_balance = initial_balance
        
        for fold in range(n_folds):
            fold_start = fold * fold_size
            fold_end = min((fold + 1) * fold_size, total_candles)
            fold_candles = candles[fold_start:fold_end]
            
            is_size = int(len(fold_candles) * in_sample_ratio)
            is_candles = fold_candles[:is_size]
            oos_candles = fold_candles[is_size:]
            
            if len(is_candles) < 50 or len(oos_candles) < 20:
                continue
            
            # Optimize on in-sample
            best_params = {"stop_loss_percent": 2.0, "take_profit_percent": 4.0, "risk_per_trade": 1.0}
            best_sharpe = -999
            
            analyzer = self.analyzers.get(strategy)
            if not analyzer:
                continue
            
            # Grid search on IS data
            for sl in param_ranges.get("stop_loss_percent", [2.0]):
                for tp in param_ranges.get("take_profit_percent", [4.0]):
                    for risk in param_ranges.get("risk_per_trade", [1.0]):
                        signals = analyzer.analyze(is_candles)
                        trades, equity, eq_curve = self._simulate_trades(
                            is_candles, signals, symbol, initial_balance, risk, sl, tp
                        )
                        
                        if trades:
                            sharpe = self._calculate_sharpe(trades)
                            if sharpe > best_sharpe:
                                best_sharpe = sharpe
                                best_params = {"stop_loss_percent": sl, "take_profit_percent": tp, "risk_per_trade": risk}
            
            best_params_history.append(best_params)
            
            # Validate on out-of-sample with best params
            oos_signals = analyzer.analyze(oos_candles)
            oos_fold_trades, oos_equity, oos_eq_curve = self._simulate_trades(
                oos_candles, oos_signals, symbol, running_balance,
                best_params["risk_per_trade"], best_params["stop_loss_percent"], best_params["take_profit_percent"]
            )
            
            running_balance = oos_equity
            oos_trades.extend(oos_fold_trades)
            oos_equity_curve.extend(oos_eq_curve)
            
            fold_results.append({
                "fold": fold + 1,
                "is_candles": len(is_candles),
                "oos_candles": len(oos_candles),
                "best_params": best_params,
                "is_sharpe": best_sharpe,
                "oos_trades": len(oos_fold_trades),
                "oos_pnl": oos_equity - initial_balance if fold == 0 else oos_equity - fold_results[-1].get("running_balance", initial_balance) if len(fold_results) > 1 else oos_equity - initial_balance,
                "running_balance": running_balance
            })
        
        # Calculate overall OOS statistics
        oos_stats = self._calculate_statistics(oos_trades, oos_equity_curve, initial_balance, running_balance)
        
        return {
            "strategy": strategy,
            "symbol": symbol,
            "total_folds": n_folds,
            "fold_results": fold_results,
            "best_params_history": best_params_history,
            "oos_performance": oos_stats,
            "robustness_score": self._calculate_robustness(fold_results),
            "recommended_params": self._get_consensus_params(best_params_history)
        }
    
    def _simulate_trades(
        self, candles: List[Dict], signals: Dict, symbol: str,
        initial: float, risk: float, sl: float, tp: float
    ) -> tuple:
        """Simulate trades and return trades list, final equity, and equity curve"""
        trades = []
        equity = initial
        equity_curve = [{"time": candles[0]["time"] if candles else "", "equity": equity}]
        position = None
        
        for i, candle in enumerate(candles):
            if i < 20:
                continue
            
            signal = signals.get(i, {})
            
            if position:
                exit_signal = self._check_exit(position, candle, sl, tp, signal)
                if exit_signal:
                    pnl = self._calculate_pnl(position, candle["close"])
                    equity += pnl
                    trades.append({
                        "entry_time": position["entry_time"],
                        "exit_time": candle["time"],
                        "symbol": symbol,
                        "direction": position["direction"],
                        "entry_price": position["entry_price"],
                        "exit_price": candle["close"],
                        "size": position["size"],
                        "pnl": pnl,
                        "pnl_percent": (pnl / position["size"]) * 100,
                        "reason": exit_signal
                    })
                    equity_curve.append({"time": candle["time"], "equity": equity})
                    position = None
            
            if not position and signal.get("direction"):
                size = equity * (risk / 100) / (sl / 100)
                position = {
                    "entry_time": candle["time"],
                    "entry_price": candle["close"],
                    "direction": signal["direction"],
                    "size": size,
                    "stop_loss": candle["close"] * (1 - sl / 100) if signal["direction"] == "LONG" else candle["close"] * (1 + sl / 100),
                    "take_profit": candle["close"] * (1 + tp / 100) if signal["direction"] == "LONG" else candle["close"] * (1 - tp / 100)
                }
        
        return trades, equity, equity_curve
    
    def _calculate_robustness(self, fold_results: List[Dict]) -> float:
        """Calculate robustness score based on consistency across folds"""
        if not fold_results:
            return 0
        
        # Check parameter stability
        params_list = [f["best_params"] for f in fold_results]
        sl_values = [p["stop_loss_percent"] for p in params_list]
        tp_values = [p["take_profit_percent"] for p in params_list]
        
        # Calculate coefficient of variation (lower is better)
        sl_cv = (max(sl_values) - min(sl_values)) / (sum(sl_values) / len(sl_values)) if sl_values else 1
        tp_cv = (max(tp_values) - min(tp_values)) / (sum(tp_values) / len(tp_values)) if tp_values else 1
        
        # Check profitability consistency
        profitable_folds = sum(1 for f in fold_results if f.get("oos_pnl", 0) > 0)
        profit_ratio = profitable_folds / len(fold_results)
        
        # Robustness = param stability * profit consistency
        robustness = (1 - (sl_cv + tp_cv) / 4) * profit_ratio * 100
        return max(0, min(100, robustness))
    
    def _get_consensus_params(self, params_history: List[Dict]) -> Dict:
        """Get consensus parameters from walk-forward optimization"""
        if not params_history:
            return {"stop_loss_percent": 2.0, "take_profit_percent": 4.0, "risk_per_trade": 1.0}
        
        # Use median for robustness
        sl_values = sorted([p["stop_loss_percent"] for p in params_history])
        tp_values = sorted([p["take_profit_percent"] for p in params_history])
        risk_values = sorted([p["risk_per_trade"] for p in params_history])
        
        mid = len(params_history) // 2
        return {
            "stop_loss_percent": sl_values[mid],
            "take_profit_percent": tp_values[mid],
            "risk_per_trade": risk_values[mid]
        }
    
    def _check_exit(self, position: Dict, candle: Dict, sl_pct: float, tp_pct: float, signal: Dict) -> Optional[str]:
        """Check if position should be closed"""
        if position["direction"] == "LONG":
            if candle["low"] <= position["stop_loss"]:
                return "SL"
            if candle["high"] >= position["take_profit"]:
                return "TP"
            if signal.get("direction") == "SHORT":
                return "SIGNAL"
        else:
            if candle["high"] >= position["stop_loss"]:
                return "SL"
            if candle["low"] <= position["take_profit"]:
                return "TP"
            if signal.get("direction") == "LONG":
                return "SIGNAL"
        return None
    
    def _calculate_pnl(self, position: Dict, exit_price: float) -> float:
        """Calculate PnL for a position with realistic costs (commissions + slippage)"""
        entry_value = position["size"]
        exit_value = position["size"]
        
        # Calculate gross P&L
        if position["direction"] == "LONG":
            gross_pnl = position["size"] * (exit_price - position["entry_price"]) / position["entry_price"]
        else:
            gross_pnl = position["size"] * (position["entry_price"] - exit_price) / position["entry_price"]
        
        # Deduct trading costs
        costs = TradingCosts.calculate(
            entry_value=entry_value,
            exit_value=exit_value,
            is_maker=False  # Conservative: assume taker fees
        )
        
        net_pnl = gross_pnl - costs
        return net_pnl
    
    def _calculate_statistics(self, trades: List[Dict], equity_curve: List[Dict], initial: float, final: float) -> Dict:
        """Calculate backtest statistics"""
        if not trades:
            return self._empty_result(initial)
        
        wins = [t for t in trades if t["pnl"] > 0]
        losses = [t for t in trades if t["pnl"] <= 0]
        
        gross_profit = sum(t["pnl"] for t in wins)
        gross_loss = abs(sum(t["pnl"] for t in losses))
        
        # Max drawdown
        peak = initial
        max_dd = 0
        for point in equity_curve:
            if point["equity"] > peak:
                peak = point["equity"]
            dd = (peak - point["equity"]) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        total_return = (final - initial) / initial * 100
        
        return {
            "total_trades": len(trades),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate": len(wins) / len(trades) * 100 if trades else 0,
            "total_pnl": final - initial,
            "total_pnl_percent": total_return,
            "profit_factor": gross_profit / gross_loss if gross_loss > 0 else 999,
            "max_drawdown_percent": max_dd,
            "sharpe_ratio": self._calculate_sharpe(trades),
            "sortino_ratio": self._calculate_sortino(trades),
            "calmar_ratio": self._calculate_calmar(total_return, max_dd),
            "expectancy": self._calculate_expectancy(trades),
            "avg_win": gross_profit / len(wins) if wins else 0,
            "avg_loss": gross_loss / len(losses) if losses else 0,
            "final_balance": final,
            "trades": trades[-50:],  # Last 50 trades
            "equity_curve": equity_curve
        }
    
    def _calculate_sharpe(self, trades: List[Dict]) -> float:
        """Calculate Sharpe ratio (annualized)"""
        if len(trades) < 2:
            return 0
        returns = [t["pnl_percent"] for t in trades]
        mean = sum(returns) / len(returns)
        std = math.sqrt(sum((r - mean) ** 2 for r in returns) / len(returns))
        return (mean / std) * math.sqrt(252) if std > 0 else 0
    
    def _calculate_sortino(self, trades: List[Dict]) -> float:
        """Calculate Sortino ratio (downside deviation only)"""
        if len(trades) < 2:
            return 0
        returns = [t["pnl_percent"] for t in trades]
        mean = sum(returns) / len(returns)
        # Only consider negative returns for downside deviation
        downside_returns = [r for r in returns if r < 0]
        if not downside_returns:
            return 999  # No losses
        downside_std = math.sqrt(sum(r ** 2 for r in downside_returns) / len(downside_returns))
        return (mean / downside_std) * math.sqrt(252) if downside_std > 0 else 0
    
    def _calculate_calmar(self, total_return: float, max_dd: float) -> float:
        """Calculate Calmar ratio (return / max drawdown)"""
        if max_dd == 0:
            return 999
        return total_return / max_dd if max_dd > 0 else 0
    
    def _calculate_expectancy(self, trades: List[Dict]) -> float:
        """Calculate trade expectancy (average win * win_rate - average loss * loss_rate)"""
        if not trades:
            return 0
        wins = [t["pnl"] for t in trades if t["pnl"] > 0]
        losses = [abs(t["pnl"]) for t in trades if t["pnl"] <= 0]
        
        win_rate = len(wins) / len(trades) if trades else 0
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        return (avg_win * win_rate) - (avg_loss * (1 - win_rate))
    
    async def run_monte_carlo_simulation(
        self,
        strategy: str,
        symbol: str,
        timeframe: str,
        days: int,
        initial_balance: float = 10000,
        risk_per_trade: float = 1.0,
        stop_loss_percent: float = 2.0,
        take_profit_percent: float = 4.0,
        n_simulations: int = 1000,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Monte Carlo simulation to estimate strategy risk and expected outcomes.
        Randomly shuffles trade order to see distribution of possible results.
        """
        import random
        
        # First run normal backtest to get trades
        result = await self.run_backtest(
            strategy=strategy,
            symbol=symbol,
            timeframe=timeframe,
            days=days,
            initial_balance=initial_balance,
            risk_per_trade=risk_per_trade,
            stop_loss_percent=stop_loss_percent,
            take_profit_percent=take_profit_percent
        )
        
        trades = result.get("trades", [])
        if len(trades) < 10:
            return {
                "error": "Insufficient trades for Monte Carlo simulation (min 10)",
                "original_result": result
            }
        
        # Extract trade returns
        trade_returns = [t["pnl_percent"] for t in trades]
        
        # Run simulations
        final_balances = []
        max_drawdowns = []
        
        for _ in range(n_simulations):
            # Shuffle trade order
            shuffled = trade_returns.copy()
            random.shuffle(shuffled)
            
            # Simulate equity curve
            equity = initial_balance
            peak = equity
            max_dd = 0
            
            for ret in shuffled:
                equity *= (1 + ret / 100)
                if equity > peak:
                    peak = equity
                dd = (peak - equity) / peak * 100
                if dd > max_dd:
                    max_dd = dd
            
            final_balances.append(equity)
            max_drawdowns.append(max_dd)
        
        # Calculate statistics
        final_balances.sort()
        max_drawdowns.sort()
        
        n = len(final_balances)
        lower_idx = int((1 - confidence_level) / 2 * n)
        upper_idx = int((1 + confidence_level) / 2 * n)
        
        # VaR (Value at Risk) at confidence level
        var_idx = int((1 - confidence_level) * n)
        
        return {
            "success": True,
            "n_simulations": n_simulations,
            "confidence_level": confidence_level,
            "original_result": {
                "total_trades": result["total_trades"],
                "win_rate": result["win_rate"],
                "total_pnl_percent": result["total_pnl_percent"],
                "max_drawdown": result["max_drawdown_percent"]
            },
            "monte_carlo": {
                "final_balance": {
                    "mean": sum(final_balances) / n,
                    "median": final_balances[n // 2],
                    "min": final_balances[0],
                    "max": final_balances[-1],
                    "percentile_5": final_balances[int(n * 0.05)],
                    "percentile_25": final_balances[int(n * 0.25)],
                    "percentile_75": final_balances[int(n * 0.75)],
                    "percentile_95": final_balances[int(n * 0.95)],
                    "confidence_interval": [final_balances[lower_idx], final_balances[upper_idx]]
                },
                "max_drawdown": {
                    "mean": sum(max_drawdowns) / n,
                    "median": max_drawdowns[n // 2],
                    "worst_case": max_drawdowns[-1],
                    "percentile_95": max_drawdowns[int(n * 0.95)]
                },
                "var": {
                    "value": initial_balance - final_balances[var_idx],
                    "percent": (initial_balance - final_balances[var_idx]) / initial_balance * 100
                },
                "probability_of_profit": sum(1 for b in final_balances if b > initial_balance) / n * 100,
                "probability_of_ruin": sum(1 for b in final_balances if b < initial_balance * 0.5) / n * 100
            },
            "distribution": {
                "balances_histogram": self._create_histogram(final_balances, 20),
                "drawdown_histogram": self._create_histogram(max_drawdowns, 20)
            }
        }
    
    def _create_histogram(self, data: List[float], bins: int = 20) -> List[Dict]:
        """Create histogram data for charting"""
        if not data:
            return []
        
        min_val = min(data)
        max_val = max(data)
        bin_size = (max_val - min_val) / bins if max_val > min_val else 1
        
        histogram = []
        for i in range(bins):
            bin_start = min_val + i * bin_size
            bin_end = bin_start + bin_size
            count = sum(1 for d in data if bin_start <= d < bin_end)
            histogram.append({
                "range": f"{bin_start:.2f}-{bin_end:.2f}",
                "start": bin_start,
                "end": bin_end,
                "count": count,
                "percent": count / len(data) * 100
            })
        
        return histogram
    
    async def run_optimization(
        self,
        strategy: str,
        symbol: str,
        timeframe: str,
        days: int,
        initial_balance: float = 10000,
        param_grid: Dict[str, List] = None
    ) -> Dict[str, Any]:
        """
        Grid search optimization for strategy parameters.
        Tests all combinations and finds optimal settings.
        """
        if not param_grid:
            param_grid = {
                "stop_loss_percent": [1.0, 1.5, 2.0, 2.5, 3.0],
                "take_profit_percent": [2.0, 3.0, 4.0, 5.0, 6.0],
                "risk_per_trade": [0.5, 1.0, 1.5, 2.0]
            }
        
        results = []
        best_result = None
        best_sharpe = -999
        
        # Generate all parameter combinations
        from itertools import product
        param_names = list(param_grid.keys())
        param_values = [param_grid[p] for p in param_names]
        
        for combo in product(*param_values):
            params = dict(zip(param_names, combo))
            
            result = await self.run_backtest(
                strategy=strategy,
                symbol=symbol,
                timeframe=timeframe,
                days=days,
                initial_balance=initial_balance,
                risk_per_trade=params.get("risk_per_trade", 1.0),
                stop_loss_percent=params.get("stop_loss_percent", 2.0),
                take_profit_percent=params.get("take_profit_percent", 4.0)
            )
            
            result_summary = {
                "params": params,
                "total_trades": result["total_trades"],
                "win_rate": result["win_rate"],
                "total_pnl_percent": result["total_pnl_percent"],
                "profit_factor": result["profit_factor"],
                "max_drawdown": result["max_drawdown_percent"],
                "sharpe_ratio": result["sharpe_ratio"]
            }
            results.append(result_summary)
            
            if result["sharpe_ratio"] > best_sharpe:
                best_sharpe = result["sharpe_ratio"]
                best_result = result_summary
        
        # Sort by Sharpe ratio
        results.sort(key=lambda x: x["sharpe_ratio"], reverse=True)
        
        return {
            "success": True,
            "total_combinations": len(results),
            "best_params": best_result["params"] if best_result else None,
            "best_result": best_result,
            "top_10_results": results[:10],
            "all_results": results
        }
    
    def _empty_result(self, initial: float) -> Dict:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "total_pnl_percent": 0,
            "profit_factor": 0,
            "max_drawdown_percent": 0,
            "sharpe_ratio": 0,
            "final_balance": initial,
            "trades": [],
            "equity_curve": [{"time": datetime.now().isoformat(), "equity": initial}]
        }


# Strategy Analyzers based on real bot logic

class RSIBBOIAnalyzer:
    """Based on aiboll/aiboll.py and spain_rsibb_oi/oi.py"""
    
    @safe_analyze
    def analyze(self, candles: List[Dict]) -> Dict[int, Dict]:
        signals = {}
        closes = [c["close"] for c in candles]
        
        for i in range(30, len(candles)):
            rsi = self._calculate_rsi(closes[:i+1], 14)
            bb_upper, bb_lower, bb_mid = self._bollinger_bands(closes[:i+1], 20, 2)
            
            close = closes[i]
            signal = {}
            
            # RSI + BB logic
            if rsi < 30 and close < bb_lower:
                signal = {"direction": "LONG", "score": 80 + (30 - rsi)}
            elif rsi > 70 and close > bb_upper:
                signal = {"direction": "SHORT", "score": 80 + (rsi - 70)}
            
            if signal:
                signals[i] = signal
        
        return signals
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        if len(prices) < period + 1:
            return 50
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def _bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2) -> tuple:
        if len(prices) < period:
            return prices[-1], prices[-1], prices[-1]
        window = prices[-period:]
        mid = sum(window) / period
        std = math.sqrt(sum((p - mid) ** 2 for p in window) / period)
        return mid + std_dev * std, mid - std_dev * std, mid


class WyckoffAnalyzer:
    """Wyckoff + SMC with Fibonacci zones and order blocks"""
    
    @safe_analyze
    def analyze(self, candles: List[Dict]) -> Dict[int, Dict]:
        signals = {}
        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        
        for i in range(30, len(candles)):
            # Use shorter window for more frequent signals
            window = candles[max(0, i-20):i+1]
            
            w_highs = [c["high"] for c in window]
            w_lows = [c["low"] for c in window]
            
            swing_high = max(w_highs)
            swing_low = min(w_lows)
            range_size = swing_high - swing_low
            
            if range_size == 0:
                continue
                
            close = candles[i]["close"]
            prev_close = candles[i-1]["close"]
            curr_open = candles[i]["open"]
            
            # Fibonacci retracement levels (more common price zones)
            fib_618 = swing_high - range_size * 0.618  # Golden ratio
            fib_786 = swing_high - range_size * 0.786  # Deep retracement
            fib_382 = swing_high - range_size * 0.382  # Shallow retracement
            fib_236 = swing_high - range_size * 0.236  # Very shallow
            
            # Volume analysis for confirmation
            avg_vol = sum(c["volume"] for c in candles[max(0,i-10):i]) / min(10, i)
            curr_vol = candles[i]["volume"]
            high_volume = curr_vol > avg_vol * 1.5
            
            # Bullish reversal patterns
            is_bullish_candle = close > curr_open
            is_bearish_candle = close < curr_open
            
            # Order block detection (last bearish candle before bullish move)
            bullish_engulf = (is_bullish_candle and 
                            candles[i-1]["close"] < candles[i-1]["open"] and
                            close > candles[i-1]["open"])
            bearish_engulf = (is_bearish_candle and 
                            candles[i-1]["close"] > candles[i-1]["open"] and
                            close < candles[i-1]["open"])
            
            signal = None
            
            # LONG signals - price in discount zone (lower Fib levels)
            if close <= fib_618 and close >= fib_786:
                if is_bullish_candle:
                    score = 70
                    if high_volume:
                        score += 15
                    if bullish_engulf:
                        score += 15
                    signal = {"direction": "LONG", "score": score}
            
            # Strong support bounce at 78.6%
            elif close <= fib_786 and prev_close < fib_786 and is_bullish_candle:
                score = 80
                if high_volume:
                    score += 10
                signal = {"direction": "LONG", "score": score}
            
            # Break of structure up
            elif close > swing_high and prev_close <= swing_high and is_bullish_candle:
                if high_volume:
                    signal = {"direction": "LONG", "score": 85}
            
            # SHORT signals - price in premium zone (upper Fib levels)
            if close >= fib_382 and close <= fib_236:
                if is_bearish_candle:
                    score = 70
                    if high_volume:
                        score += 15
                    if bearish_engulf:
                        score += 15
                    signal = {"direction": "SHORT", "score": score}
            
            # Strong resistance rejection at 23.6%
            elif close >= fib_236 and prev_close > fib_236 and is_bearish_candle:
                score = 80
                if high_volume:
                    score += 10
                signal = {"direction": "SHORT", "score": score}
            
            # Break of structure down
            elif close < swing_low and prev_close >= swing_low and is_bearish_candle:
                if high_volume:
                    signal = {"direction": "SHORT", "score": 85}
            
            if signal:
                signals[i] = signal
        
        return signals


class ElCaroAnalyzer:
    """Main ElCaro strategy - Channel breakout with momentum"""
    
    @safe_analyze
    def analyze(self, candles: List[Dict]) -> Dict[int, Dict]:
        signals = {}
        
        for i in range(20, len(candles)):
            window = candles[i-20:i]
            
            highs = [c["high"] for c in window]
            lows = [c["low"] for c in window]
            
            upper_channel = max(highs)
            lower_channel = min(lows)
            
            close = candles[i]["close"]
            prev_close = candles[i-1]["close"]
            
            # Breakout signals
            if close > upper_channel and prev_close <= upper_channel:
                signals[i] = {"direction": "LONG", "score": 90}
            elif close < lower_channel and prev_close >= lower_channel:
                signals[i] = {"direction": "SHORT", "score": 90}
        
        return signals


class ScryptomeraAnalyzer:
    """Based on pazzle/damp.py - Volume profile strategy"""
    
    @safe_analyze
    def analyze(self, candles: List[Dict]) -> Dict[int, Dict]:
        signals = {}
        
        for i in range(30, len(candles)):
            window = candles[i-30:i+1]
            
            volumes = [c["volume"] for c in window]
            avg_volume = sum(volumes[:-1]) / len(volumes[:-1])
            
            closes = [c["close"] for c in window]
            price_change = (closes[-1] - closes[0]) / closes[0] * 100
            
            current_volume = volumes[-1]
            volume_ratio = current_volume / avg_volume
            
            # High volume breakout
            if volume_ratio > 2:
                if price_change > 1:
                    signals[i] = {"direction": "LONG", "score": 75}
                elif price_change < -1:
                    signals[i] = {"direction": "SHORT", "score": 75}
        
        return signals


class ScalperAnalyzer:
    """High frequency scalping strategy"""
    
    @safe_analyze
    def analyze(self, candles: List[Dict]) -> Dict[int, Dict]:
        signals = {}
        
        for i in range(10, len(candles)):
            window = candles[i-10:i+1]
            
            closes = [c["close"] for c in window]
            
            # Simple momentum
            short_ma = sum(closes[-3:]) / 3
            long_ma = sum(closes[-10:]) / 10
            
            if short_ma > long_ma * 1.002:  # 0.2% above
                signals[i] = {"direction": "LONG", "score": 60}
            elif short_ma < long_ma * 0.998:  # 0.2% below
                signals[i] = {"direction": "SHORT", "score": 60}
        
        return signals


class MeanReversionAnalyzer:
    """Mean Reversion Strategy - Buy oversold, sell overbought with Z-score"""
    
    @safe_analyze
    def analyze(self, candles: List[Dict]) -> Dict[int, Dict]:
        signals = {}
        closes = [c["close"] for c in candles]
        
        for i in range(50, len(candles)):
            window = closes[i-50:i+1]
            mean = sum(window) / len(window)
            std = math.sqrt(sum((p - mean) ** 2 for p in window) / len(window))
            
            if std == 0:
                continue
            
            z_score = (closes[i] - mean) / std
            
            # Strong mean reversion signals
            if z_score < -2.0:  # Extremely oversold
                signals[i] = {"direction": "LONG", "score": 85}
            elif z_score < -1.5:
                signals[i] = {"direction": "LONG", "score": 70}
            elif z_score > 2.0:  # Extremely overbought
                signals[i] = {"direction": "SHORT", "score": 85}
            elif z_score > 1.5:
                signals[i] = {"direction": "SHORT", "score": 70}
        
        return signals


class TrendFollowingAnalyzer:
    """Trend Following Strategy - Multiple EMA crossovers with ADX filter"""
    
    @safe_analyze
    def analyze(self, candles: List[Dict]) -> Dict[int, Dict]:
        signals = {}
        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        
        # Calculate EMAs
        ema_fast = self._calc_ema(closes, 12)
        ema_mid = self._calc_ema(closes, 26)
        ema_slow = self._calc_ema(closes, 50)
        
        # Calculate ADX for trend strength
        adx = self._calc_adx(highs, lows, closes, 14)
        
        for i in range(55, len(candles)):
            # Trend alignment: fast > mid > slow = bullish, fast < mid < slow = bearish
            bullish_trend = ema_fast[i] > ema_mid[i] > ema_slow[i]
            bearish_trend = ema_fast[i] < ema_mid[i] < ema_slow[i]
            
            trend_strength = adx[i] if i < len(adx) else 20
            
            # Only trade in strong trends
            if trend_strength > 25:
                if bullish_trend:
                    # Check for pullback entry
                    if closes[i] <= ema_fast[i] * 1.005 and closes[i] > ema_mid[i]:
                        signals[i] = {"direction": "LONG", "score": 80 + min(trend_strength - 25, 15)}
                elif bearish_trend:
                    if closes[i] >= ema_fast[i] * 0.995 and closes[i] < ema_mid[i]:
                        signals[i] = {"direction": "SHORT", "score": 80 + min(trend_strength - 25, 15)}
        
        return signals
    
    def _calc_ema(self, data: List[float], period: int) -> List[float]:
        ema = []
        mult = 2 / (period + 1)
        for i in range(len(data)):
            if i == 0:
                ema.append(data[0])
            elif i < period:
                ema.append(sum(data[:i+1]) / (i+1))
            else:
                ema.append((data[i] - ema[-1]) * mult + ema[-1])
        return ema
    
    def _calc_adx(self, highs: List[float], lows: List[float], closes: List[float], period: int) -> List[float]:
        """Calculate ADX indicator"""
        adx = []
        tr_list = []
        plus_dm_list = []
        minus_dm_list = []
        
        for i in range(len(closes)):
            if i == 0:
                tr_list.append(highs[0] - lows[0])
                plus_dm_list.append(0)
                minus_dm_list.append(0)
                adx.append(20)
                continue
            
            # True Range
            tr = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
            tr_list.append(tr)
            
            # Directional Movement
            up_move = highs[i] - highs[i-1]
            down_move = lows[i-1] - lows[i]
            
            plus_dm = up_move if up_move > down_move and up_move > 0 else 0
            minus_dm = down_move if down_move > up_move and down_move > 0 else 0
            
            plus_dm_list.append(plus_dm)
            minus_dm_list.append(minus_dm)
            
            if i < period:
                adx.append(20)
                continue
            
            # Smoothed averages
            atr = sum(tr_list[i-period+1:i+1]) / period
            plus_di = 100 * sum(plus_dm_list[i-period+1:i+1]) / period / atr if atr > 0 else 0
            minus_di = 100 * sum(minus_dm_list[i-period+1:i+1]) / period / atr if atr > 0 else 0
            
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) > 0 else 0
            adx.append(dx)
        
        return adx


class BreakoutAnalyzer:
    """Breakout Strategy - Trade breakouts from consolidation ranges"""
    
    @safe_analyze
    def analyze(self, candles: List[Dict]) -> Dict[int, Dict]:
        signals = {}
        
        for i in range(30, len(candles)):
            window = candles[i-20:i]
            
            highs = [c["high"] for c in window]
            lows = [c["low"] for c in window]
            
            range_high = max(highs)
            range_low = min(lows)
            range_size = range_high - range_low
            
            # Detect consolidation (low volatility)
            avg_candle_size = sum(c["high"] - c["low"] for c in window) / len(window)
            is_consolidating = avg_candle_size < range_size * 0.15
            
            close = candles[i]["close"]
            volume = candles[i]["volume"]
            avg_volume = sum(c["volume"] for c in window) / len(window)
            
            high_volume = volume > avg_volume * 1.5
            
            if is_consolidating:
                # Breakout above range
                if close > range_high:
                    score = 80 if high_volume else 65
                    signals[i] = {"direction": "LONG", "score": score}
                # Breakdown below range
                elif close < range_low:
                    score = 80 if high_volume else 65
                    signals[i] = {"direction": "SHORT", "score": score}
        
        return signals


class DCAAnalyzer:
    """Dollar Cost Averaging Strategy - Time-based entries with RSI filter"""
    
    @safe_analyze
    def analyze(self, candles: List[Dict]) -> Dict[int, Dict]:
        signals = {}
        closes = [c["close"] for c in candles]
        
        # DCA every N candles with RSI filter
        dca_interval = 24  # Every 24 candles (1 day for 1h timeframe)
        
        for i in range(30, len(candles)):
            # Calculate RSI for filter
            rsi = self._calc_rsi(closes[:i+1], 14)
            
            # DCA entry at intervals, filtered by RSI
            if i % dca_interval == 0:
                if rsi < 50:  # Only buy when RSI is below neutral
                    score = 60 + (50 - rsi)  # Higher score for lower RSI
                    signals[i] = {"direction": "LONG", "score": min(score, 90)}
        
        return signals
    
    def _calc_rsi(self, prices: List[float], period: int = 14) -> float:
        if len(prices) < period + 1:
            return 50
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))


class GridAnalyzer:
    """Grid Trading Strategy - Buy at lower grids, sell at upper grids"""
    
    @safe_analyze
    def analyze(self, candles: List[Dict]) -> Dict[int, Dict]:
        signals = {}
        
        for i in range(50, len(candles)):
            window = candles[i-50:i]
            
            # Define grid range based on recent price action
            highs = [c["high"] for c in window]
            lows = [c["low"] for c in window]
            
            range_high = max(highs)
            range_low = min(lows)
            grid_size = (range_high - range_low) / 10  # 10 grid levels
            
            close = candles[i]["close"]
            prev_close = candles[i-1]["close"]
            
            # Calculate grid level (0-10)
            if grid_size > 0:
                grid_level = (close - range_low) / grid_size
                prev_grid_level = (prev_close - range_low) / grid_size
                
                # Buy at lower grids (0-3), sell at upper grids (7-10)
                if grid_level < 3 and prev_grid_level >= 3:
                    signals[i] = {"direction": "LONG", "score": 75}
                elif grid_level > 7 and prev_grid_level <= 7:
                    signals[i] = {"direction": "SHORT", "score": 75}
        
        return signals


class MomentumAnalyzer:
    """Momentum Strategy - Trade strong momentum with ROC and volume confirmation"""
    
    @safe_analyze
    def analyze(self, candles: List[Dict]) -> Dict[int, Dict]:
        signals = {}
        closes = [c["close"] for c in candles]
        volumes = [c["volume"] for c in candles]
        
        for i in range(20, len(candles)):
            # Rate of Change (ROC)
            roc_10 = (closes[i] - closes[i-10]) / closes[i-10] * 100
            roc_5 = (closes[i] - closes[i-5]) / closes[i-5] * 100
            
            # Volume confirmation
            avg_volume = sum(volumes[i-10:i]) / 10
            volume_ratio = volumes[i] / avg_volume if avg_volume > 0 else 1
            
            # Strong bullish momentum
            if roc_10 > 3 and roc_5 > 1 and volume_ratio > 1.2:
                score = 70 + min(roc_10, 15)
                signals[i] = {"direction": "LONG", "score": min(score, 95)}
            # Strong bearish momentum
            elif roc_10 < -3 and roc_5 < -1 and volume_ratio > 1.2:
                score = 70 + min(abs(roc_10), 15)
                signals[i] = {"direction": "SHORT", "score": min(score, 95)}
        
        return signals


class VolatilityBreakoutAnalyzer:
    """Volatility Breakout Strategy - Trade breakouts using ATR and Keltner Channels"""
    
    @safe_analyze
    def analyze(self, candles: List[Dict]) -> Dict[int, Dict]:
        signals = {}
        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        
        # Calculate ATR
        atr = self._calc_atr(highs, lows, closes, 14)
        
        # Calculate EMA for Keltner center
        ema_20 = self._calc_ema(closes, 20)
        
        for i in range(25, len(candles)):
            atr_val = atr[i] if i < len(atr) else 0
            ema_val = ema_20[i] if i < len(ema_20) else closes[i]
            
            # Keltner Channel bands
            upper_band = ema_val + 2 * atr_val
            lower_band = ema_val - 2 * atr_val
            
            close = closes[i]
            prev_close = closes[i-1]
            
            # Breakout signals
            if close > upper_band and prev_close <= upper_band:
                signals[i] = {"direction": "LONG", "score": 85}
            elif close < lower_band and prev_close >= lower_band:
                signals[i] = {"direction": "SHORT", "score": 85}
        
        return signals
    
    def _calc_ema(self, data: List[float], period: int) -> List[float]:
        ema = []
        mult = 2 / (period + 1)
        for i in range(len(data)):
            if i == 0:
                ema.append(data[0])
            elif i < period:
                ema.append(sum(data[:i+1]) / (i+1))
            else:
                ema.append((data[i] - ema[-1]) * mult + ema[-1])
        return ema
    
    def _calc_atr(self, highs: List[float], lows: List[float], closes: List[float], period: int) -> List[float]:
        tr = []
        for i in range(len(highs)):
            if i == 0:
                tr.append(highs[0] - lows[0])
            else:
                tr.append(max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1])))
        
        atr = []
        for i in range(len(tr)):
            if i < period:
                atr.append(sum(tr[:i+1]) / (i+1))
            else:
                atr.append(sum(tr[i-period+1:i+1]) / period)
        return atr


class CustomStrategyAnalyzer:
    """Analyzer for user-created custom strategies"""
    
    def __init__(self, config: Dict, base_strategy: str = "custom"):
        self.config = config
        self.base_strategy = base_strategy
        self.indicators = config.get("indicators", [])
        self.entry_conditions = config.get("entry_conditions", {})
        self.exit_conditions = config.get("exit_conditions", {})
        self.risk_management = config.get("risk_management", {})
    
    @safe_analyze
    def analyze(self, candles: List[Dict]) -> Dict[int, Dict]:
        """Generate signals based on custom strategy configuration"""
        signals = {}
        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        volumes = [c["volume"] for c in candles]
        
        # Calculate all enabled indicators
        indicator_values = {}
        for ind in self.indicators:
            if ind.get("enabled", True):
                ind_name = ind["name"]
                params = ind.get("params", {})
                
                if ind_name == "rsi":
                    indicator_values["rsi"] = self._calc_rsi_series(closes, params.get("period", 14))
                elif ind_name == "ema":
                    period = params.get("period", 20)
                    indicator_values[f"ema_{period}"] = self._calc_ema_series(closes, period)
                elif ind_name == "sma":
                    period = params.get("period", 20)
                    indicator_values[f"sma_{period}"] = self._calc_sma_series(closes, period)
                elif ind_name == "bb":
                    bb_upper, bb_lower, bb_mid = self._calc_bb_series(closes, params.get("period", 20), params.get("std", 2))
                    indicator_values["bb_upper"] = bb_upper
                    indicator_values["bb_lower"] = bb_lower
                    indicator_values["bb_mid"] = bb_mid
                elif ind_name == "macd":
                    macd_line, signal_line = self._calc_macd_series(closes)
                    indicator_values["macd"] = macd_line
                    indicator_values["macd_signal"] = signal_line
                elif ind_name == "atr":
                    indicator_values["atr"] = self._calc_atr_series(highs, lows, closes, params.get("period", 14))
                elif ind_name == "volume_sma":
                    period = params.get("period", 20)
                    indicator_values["volume_sma"] = self._calc_sma_series(volumes, period)
                elif ind_name == "supertrend":
                    period = params.get("period", 10)
                    multiplier = params.get("multiplier", 3.0)
                    st_values, st_direction = self._calc_supertrend_series(highs, lows, closes, period, multiplier)
                    indicator_values["supertrend"] = st_values
                    indicator_values["supertrend_dir"] = st_direction
                elif ind_name == "vwap":
                    indicator_values["vwap"] = self._calc_vwap_series(highs, lows, closes, volumes)
                elif ind_name == "obv":
                    indicator_values["obv"] = self._calc_obv_series(closes, volumes)
                    indicator_values["obv_sma"] = self._calc_sma_series(indicator_values["obv"], params.get("period", 20))
        
        # Generate signals based on entry conditions
        for i in range(50, len(candles)):
            signal = self._evaluate_conditions(i, candles, indicator_values, closes, volumes)
            if signal:
                signals[i] = signal
        
        return signals
    
    def _evaluate_conditions(self, i: int, candles: List[Dict], indicators: Dict, closes: List[float], volumes: List[float]) -> Optional[Dict]:
        """Evaluate entry conditions at index i"""
        long_score = 0
        short_score = 0
        
        # Check each condition type
        conditions = self.entry_conditions
        
        # RSI conditions
        if "rsi" in indicators:
            rsi = indicators["rsi"][i] if i < len(indicators["rsi"]) else 50
            rsi_oversold = conditions.get("rsi_oversold", 30)
            rsi_overbought = conditions.get("rsi_overbought", 70)
            
            if rsi < rsi_oversold:
                long_score += 30
            elif rsi > rsi_overbought:
                short_score += 30
        
        # Bollinger Bands conditions
        if "bb_upper" in indicators and "bb_lower" in indicators:
            close = closes[i]
            bb_upper = indicators["bb_upper"][i] if i < len(indicators["bb_upper"]) else close
            bb_lower = indicators["bb_lower"][i] if i < len(indicators["bb_lower"]) else close
            
            if close < bb_lower:
                long_score += 25
            elif close > bb_upper:
                short_score += 25
        
        # MACD conditions
        if "macd" in indicators and "macd_signal" in indicators:
            macd = indicators["macd"][i] if i < len(indicators["macd"]) else 0
            signal = indicators["macd_signal"][i] if i < len(indicators["macd_signal"]) else 0
            prev_macd = indicators["macd"][i-1] if i > 0 and i-1 < len(indicators["macd"]) else 0
            prev_signal = indicators["macd_signal"][i-1] if i > 0 and i-1 < len(indicators["macd_signal"]) else 0
            
            # MACD crossover
            if prev_macd < prev_signal and macd > signal:
                long_score += 35
            elif prev_macd > prev_signal and macd < signal:
                short_score += 35
        
        # EMA conditions
        for key in indicators:
            if key.startswith("ema_"):
                ema = indicators[key][i] if i < len(indicators[key]) else closes[i]
                if closes[i] > ema * 1.005:
                    long_score += 15
                elif closes[i] < ema * 0.995:
                    short_score += 15
        
        # Volume spike
        if "volume_sma" in indicators:
            vol_sma = indicators["volume_sma"][i] if i < len(indicators["volume_sma"]) else volumes[i]
            if volumes[i] > vol_sma * 2:
                # High volume confirms the move
                long_score += 10
                short_score += 10
        
        # SuperTrend conditions
        if "supertrend_dir" in indicators:
            st_dir = indicators["supertrend_dir"][i] if i < len(indicators["supertrend_dir"]) else 0
            prev_st_dir = indicators["supertrend_dir"][i-1] if i > 0 and i-1 < len(indicators["supertrend_dir"]) else 0
            
            # SuperTrend flip signals
            if st_dir == 1 and prev_st_dir == -1:  # Bullish flip
                long_score += 40
            elif st_dir == -1 and prev_st_dir == 1:  # Bearish flip
                short_score += 40
            elif st_dir == 1:  # In bullish trend
                long_score += 15
            elif st_dir == -1:  # In bearish trend
                short_score += 15
        
        # VWAP conditions
        if "vwap" in indicators:
            vwap = indicators["vwap"][i] if i < len(indicators["vwap"]) else closes[i]
            close = closes[i]
            prev_close = closes[i-1] if i > 0 else close
            
            # Price crossing VWAP
            if close > vwap and prev_close <= vwap:
                long_score += 25
            elif close < vwap and prev_close >= vwap:
                short_score += 25
            # Price significantly above/below VWAP
            elif close > vwap * 1.01:
                long_score += 10
            elif close < vwap * 0.99:
                short_score += 10
        
        # OBV conditions (On-Balance Volume)
        if "obv" in indicators and "obv_sma" in indicators:
            obv = indicators["obv"][i] if i < len(indicators["obv"]) else 0
            obv_sma = indicators["obv_sma"][i] if i < len(indicators["obv_sma"]) else 0
            prev_obv = indicators["obv"][i-1] if i > 0 and i-1 < len(indicators["obv"]) else 0
            
            # OBV crossing its SMA (volume confirmation)
            if obv > obv_sma and prev_obv <= obv_sma:
                long_score += 20
            elif obv < obv_sma and prev_obv >= obv_sma:
                short_score += 20
        
        # Determine signal based on score threshold
        min_score = conditions.get("min_score", 50)
        
        if long_score >= min_score and long_score > short_score:
            return {"direction": "LONG", "score": long_score}
        elif short_score >= min_score and short_score > long_score:
            return {"direction": "SHORT", "score": short_score}
        
        return None
    
    def _calc_rsi_series(self, prices: List[float], period: int = 14) -> List[float]:
        """Calculate RSI series"""
        rsi = []
        for i in range(len(prices)):
            if i < period + 1:
                rsi.append(50)
                continue
            deltas = [prices[j] - prices[j-1] for j in range(i-period+1, i+1)]
            gains = [d if d > 0 else 0 for d in deltas]
            losses = [-d if d < 0 else 0 for d in deltas]
            avg_gain = sum(gains) / period
            avg_loss = sum(losses) / period
            if avg_loss == 0:
                rsi.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi.append(100 - (100 / (1 + rs)))
        return rsi
    
    def _calc_sma_series(self, data: List[float], period: int) -> List[float]:
        """Calculate SMA series"""
        sma = []
        for i in range(len(data)):
            if i < period:
                sma.append(sum(data[:i+1]) / (i+1))
            else:
                sma.append(sum(data[i-period+1:i+1]) / period)
        return sma
    
    def _calc_ema_series(self, data: List[float], period: int) -> List[float]:
        """Calculate EMA series"""
        ema = []
        multiplier = 2 / (period + 1)
        for i in range(len(data)):
            if i == 0:
                ema.append(data[0])
            elif i < period:
                ema.append(sum(data[:i+1]) / (i+1))
            else:
                ema.append((data[i] - ema[-1]) * multiplier + ema[-1])
        return ema
    
    def _calc_bb_series(self, prices: List[float], period: int = 20, std_mult: float = 2) -> tuple:
        """Calculate Bollinger Bands series"""
        upper, lower, mid = [], [], []
        for i in range(len(prices)):
            if i < period:
                window = prices[:i+1]
            else:
                window = prices[i-period+1:i+1]
            mean = sum(window) / len(window)
            std = math.sqrt(sum((p - mean) ** 2 for p in window) / len(window))
            mid.append(mean)
            upper.append(mean + std_mult * std)
            lower.append(mean - std_mult * std)
        return upper, lower, mid
    
    def _calc_macd_series(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """Calculate MACD line and signal line"""
        ema_fast = self._calc_ema_series(prices, fast)
        ema_slow = self._calc_ema_series(prices, slow)
        macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
        signal_line = self._calc_ema_series(macd_line, signal)
        return macd_line, signal_line
    
    def _calc_atr_series(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[float]:
        """Calculate ATR series"""
        tr = []
        for i in range(len(highs)):
            if i == 0:
                tr.append(highs[0] - lows[0])
            else:
                tr.append(max(
                    highs[i] - lows[i],
                    abs(highs[i] - closes[i-1]),
                    abs(lows[i] - closes[i-1])
                ))
        return self._calc_sma_series(tr, period)
    
    def _calc_supertrend_series(self, highs: List[float], lows: List[float], closes: List[float], 
                                  period: int = 10, multiplier: float = 3.0) -> tuple:
        """Calculate SuperTrend indicator series"""
        atr = self._calc_atr_series(highs, lows, closes, period)
        
        supertrend = []
        direction = []  # 1 for bullish, -1 for bearish
        
        upper_band = []
        lower_band = []
        
        for i in range(len(closes)):
            hl2 = (highs[i] + lows[i]) / 2
            atr_val = atr[i] if i < len(atr) else 0
            
            basic_upper = hl2 + multiplier * atr_val
            basic_lower = hl2 - multiplier * atr_val
            
            if i == 0:
                upper_band.append(basic_upper)
                lower_band.append(basic_lower)
                supertrend.append(basic_lower)
                direction.append(1)
            else:
                # Upper band
                if basic_upper < upper_band[-1] or closes[i-1] > upper_band[-1]:
                    upper_band.append(basic_upper)
                else:
                    upper_band.append(upper_band[-1])
                
                # Lower band
                if basic_lower > lower_band[-1] or closes[i-1] < lower_band[-1]:
                    lower_band.append(basic_lower)
                else:
                    lower_band.append(lower_band[-1])
                
                # Determine trend direction
                if direction[-1] == 1:  # Previous was bullish
                    if closes[i] < lower_band[-1]:
                        direction.append(-1)
                        supertrend.append(upper_band[-1])
                    else:
                        direction.append(1)
                        supertrend.append(lower_band[-1])
                else:  # Previous was bearish
                    if closes[i] > upper_band[-1]:
                        direction.append(1)
                        supertrend.append(lower_band[-1])
                    else:
                        direction.append(-1)
                        supertrend.append(upper_band[-1])
        
        return supertrend, direction
    
    def _calc_vwap_series(self, highs: List[float], lows: List[float], closes: List[float], 
                           volumes: List[float]) -> List[float]:
        """Calculate VWAP (Volume Weighted Average Price) series - daily reset"""
        vwap = []
        cum_vol = 0
        cum_tp_vol = 0
        
        for i in range(len(closes)):
            typical_price = (highs[i] + lows[i] + closes[i]) / 3
            cum_vol += volumes[i]
            cum_tp_vol += typical_price * volumes[i]
            
            if cum_vol > 0:
                vwap.append(cum_tp_vol / cum_vol)
            else:
                vwap.append(closes[i])
        
        return vwap
    
    def _calc_obv_series(self, closes: List[float], volumes: List[float]) -> List[float]:
        """Calculate OBV (On-Balance Volume) series"""
        obv = [0]
        
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                obv.append(obv[-1] + volumes[i])
            elif closes[i] < closes[i-1]:
                obv.append(obv[-1] - volumes[i])
            else:
                obv.append(obv[-1])
        
        return obv


def save_backtest_results(strategy_id: int, results: Dict) -> bool:
    """Save backtest results to custom_strategies table"""
    try:
        conn = sqlite3.connect(str(DB_FILE))
        cur = conn.cursor()
        
        win_rate = results.get("win_rate", 0)
        total_pnl = results.get("total_pnl_percent", 0)
        total_trades = results.get("total_trades", 0)
        
        # Calculate composite backtest score
        sharpe = results.get("sharpe_ratio", 0)
        max_dd = results.get("max_drawdown_percent", 0)
        profit_factor = results.get("profit_factor", 0)
        
        # Score formula: win_rate*0.3 + pnl*0.3 + sharpe*10 + profit_factor*5 - max_dd*0.5
        backtest_score = (
            win_rate * 0.3 +
            min(total_pnl, 100) * 0.3 +
            min(sharpe, 3) * 10 +
            min(profit_factor, 5) * 5 -
            max_dd * 0.5
        )
        
        cur.execute("""
            UPDATE custom_strategies
            SET win_rate = ?, total_pnl = ?, total_trades = ?, backtest_score = ?, updated_at = ?
            WHERE id = ?
        """, (win_rate, total_pnl, total_trades, backtest_score, int(datetime.now().timestamp()), strategy_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False
