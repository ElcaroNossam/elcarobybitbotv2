"""
Real Backtest Engine - Connected to Actual Bot Strategy Logic
Based on analyzers from: elcaro, aiboll, spain_rsibb_oi, fibo_bot, pazzle, damp
"""
import aiohttp
import asyncio
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import math

# In-memory cache for historical data (5 min TTL)
_data_cache: Dict[str, tuple] = {}
_cache_ttl = 300  # 5 minutes

DB_FILE = Path(__file__).parent.parent.parent / "bot.db"


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
            "rsibboi": RSIBBOIAnalyzer(),
            "wyckoff": WyckoffAnalyzer(),
            "elcaro": ElCaroAnalyzer(),
            "scryptomera": ScryptomeraAnalyzer(),
            "scalper": ScalperAnalyzer()
        }
    
    async def fetch_historical_data(self, symbol: str, timeframe: str, days: int) -> List[Dict]:
        """Fetch OHLCV data from Binance with caching"""
        cache_key = f"{symbol}_{timeframe}_{days}"
        now = datetime.now().timestamp()
        
        # Check cache
        if cache_key in _data_cache:
            cached_data, cached_time = _data_cache[cache_key]
            if now - cached_time < _cache_ttl:
                return cached_data
        
        tf_map = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d"}
        interval = tf_map.get(timeframe, "1h")
        
        # Calculate limit based on timeframe
        candles_per_day = {"1m": 1440, "5m": 288, "15m": 96, "1h": 24, "4h": 6, "1d": 1}
        limit = min(days * candles_per_day.get(interval, 24), 1000)
        
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    candles = [
                        {
                            "time": datetime.fromtimestamp(k[0] / 1000).isoformat(),
                            "timestamp": k[0],
                            "open": float(k[1]),
                            "high": float(k[2]),
                            "low": float(k[3]),
                            "close": float(k[4]),
                            "volume": float(k[5])
                        }
                        for k in data
                    ]
                    # Cache the data
                    _data_cache[cache_key] = (candles, now)
                    return candles
                return []
    
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
        """Calculate PnL for a position"""
        if position["direction"] == "LONG":
            return position["size"] * (exit_price - position["entry_price"]) / position["entry_price"]
        else:
            return position["size"] * (position["entry_price"] - exit_price) / position["entry_price"]
    
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
        
        return {
            "total_trades": len(trades),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate": len(wins) / len(trades) * 100 if trades else 0,
            "total_pnl": final - initial,
            "total_pnl_percent": (final - initial) / initial * 100,
            "profit_factor": gross_profit / gross_loss if gross_loss > 0 else 999,
            "max_drawdown_percent": max_dd,
            "sharpe_ratio": self._calculate_sharpe(trades),
            "final_balance": final,
            "trades": trades[-50:],  # Last 50 trades
            "equity_curve": equity_curve
        }
    
    def _calculate_sharpe(self, trades: List[Dict]) -> float:
        """Calculate Sharpe ratio"""
        if len(trades) < 2:
            return 0
        returns = [t["pnl_percent"] for t in trades]
        mean = sum(returns) / len(returns)
        std = math.sqrt(sum((r - mean) ** 2 for r in returns) / len(returns))
        return (mean / std) * math.sqrt(252) if std > 0 else 0
    
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


class CustomStrategyAnalyzer:
    """Analyzer for user-created custom strategies"""
    
    def __init__(self, config: Dict, base_strategy: str = "custom"):
        self.config = config
        self.base_strategy = base_strategy
        self.indicators = config.get("indicators", [])
        self.entry_conditions = config.get("entry_conditions", {})
        self.exit_conditions = config.get("exit_conditions", {})
        self.risk_management = config.get("risk_management", {})
    
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
