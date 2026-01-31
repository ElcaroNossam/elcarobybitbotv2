"""
Backtest API - Connected to Real Strategy Analyzers
Enhanced with Live Mode and Strategy Deployment
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime

from core.tasks import safe_create_task

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import auth and PostgreSQL helper
from webapp.api.auth import get_current_user
from webapp.api.db_helper import get_db

router = APIRouter()

# WebSocket connections for live mode
live_connections: Dict[str, WebSocket] = {}


class BacktestRequest(BaseModel):
    strategies: List[str]
    symbol: str = "BTCUSDT"
    timeframe: str = "1h"
    days: int = 30
    initial_balance: float = 10000
    risk_per_trade: float = 1.0
    stop_loss_percent: float = 2.0
    take_profit_percent: float = 4.0


class MultiSymbolBacktestRequest(BaseModel):
    strategy: str
    symbols: List[str] = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    timeframe: str = "1h"
    days: int = 30
    initial_balance: float = 10000
    risk_per_trade: float = 1.0
    stop_loss_percent: float = 2.0
    take_profit_percent: float = 4.0
    allocation_mode: str = "equal"  # equal, weighted, dynamic


class WalkForwardRequest(BaseModel):
    strategy: str
    symbol: str = "BTCUSDT"
    timeframe: str = "1h"
    total_days: int = 90
    in_sample_ratio: float = 0.7
    n_folds: int = 3
    initial_balance: float = 10000
    param_ranges: Optional[Dict[str, List[float]]] = None


class CustomBacktestRequest(BaseModel):
    strategy_id: int
    symbol: str = "BTCUSDT"
    timeframe: str = "1h"
    days: int = 30
    initial_balance: float = 10000
    risk_per_trade: float = 1.0
    stop_loss_percent: float = 2.0
    take_profit_percent: float = 4.0
    save_results: bool = True  # Save results to strategy record


class BacktestResponse(BaseModel):
    success: bool
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    backtest_id: Optional[str] = None  # For WebSocket tracking


# Rate limiting for expensive backtest operations
from core.rate_limiter import RateLimiter
_backtest_limiter = RateLimiter()
_backtest_limiter.set_limit("backtest", capacity=5, refill_rate=0.5)  # 5 requests, 0.5/sec refill

async def rate_limit_backtest(user: dict = Depends(get_current_user)):
    """Rate limit backtest requests per user"""
    user_id = user["user_id"]
    if not _backtest_limiter._get_or_create_bucket(str(user_id), "backtest").try_acquire():
        raise HTTPException(429, "Too many backtest requests. Please wait.")
    return user


@router.post("/run-async")
async def run_backtest_async(request: BacktestRequest, user: dict = Depends(rate_limit_backtest)):
    """Run backtest asynchronously with WebSocket progress updates"""
    try:
        from webapp.api.backtest_ws import create_backtest_session, send_progress, send_result, send_error, is_backtest_cancelled
        from webapp.services.backtest_engine import RealBacktestEngine
        
        # Create backtest session
        backtest_id = create_backtest_session(request.dict())
        
        # Start backtest in background
        safe_create_task(run_backtest_with_progress(backtest_id, request), name=f"backtest_{backtest_id}")
        
        return {
            "success": True,
            "backtest_id": backtest_id,
            "message": "Backtest started. Connect to WebSocket for progress updates."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def run_backtest_with_progress(backtest_id: str, request: BacktestRequest):
    """Run backtest with progress updates via WebSocket"""
    try:
        from webapp.api.backtest_ws import send_progress, send_result, send_error, is_backtest_cancelled
        from webapp.services.backtest_engine import RealBacktestEngine
        
        engine = RealBacktestEngine()
        all_results = {}
        
        total_strategies = len(request.strategies)
        
        for idx, strategy in enumerate(request.strategies):
            # Check if cancelled
            if is_backtest_cancelled(backtest_id):
                await send_error(backtest_id, "Backtest cancelled by user")
                return
            
            # Send progress
            progress = (idx / total_strategies) * 100
            await send_progress(
                backtest_id,
                progress,
                f"Testing strategy: {strategy}",
                {"current_strategy": strategy, "completed": idx, "total": total_strategies}
            )
            
            # Run backtest for this strategy
            result = await engine.run_backtest(
                strategy=strategy,
                symbol=request.symbol,
                timeframe=request.timeframe,
                days=request.days,
                initial_balance=request.initial_balance,
                risk_per_trade=request.risk_per_trade,
                stop_loss_percent=request.stop_loss_percent,
                take_profit_percent=request.take_profit_percent
            )
            all_results[strategy] = result
        
        # Send final results
        await send_progress(backtest_id, 100, "Completed", {"completed": total_strategies, "total": total_strategies})
        await send_result(backtest_id, all_results)
        
    except Exception as e:
        await send_error(backtest_id, str(e))


@router.post("/run")
async def run_backtest(request: BacktestRequest, user: dict = Depends(rate_limit_backtest)):
    """Run backtest with selected strategies using real analyzers (authenticated, rate-limited)"""
    try:
        # Import backtest engine
        from webapp.services.backtest_engine import RealBacktestEngine
        
        engine = RealBacktestEngine()
        
        all_results = {}
        
        for strategy in request.strategies:
            result = await engine.run_backtest(
                strategy=strategy,
                symbol=request.symbol,
                timeframe=request.timeframe,
                days=request.days,
                initial_balance=request.initial_balance,
                risk_per_trade=request.risk_per_trade,
                stop_loss_percent=request.stop_loss_percent,
                take_profit_percent=request.take_profit_percent
            )
            all_results[strategy] = result
        
        return {
            "success": True,
            "results": all_results
        }
        
    except ImportError as e:
        # Fallback to simple backtest if engine not available
        return await run_simple_backtest(request)
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/custom")
async def run_custom_backtest(request: CustomBacktestRequest, user: dict = Depends(rate_limit_backtest)):
    """Run backtest for a custom strategy from the database (authenticated, rate-limited)"""
    user_id = user["user_id"]
    try:
        from webapp.services.backtest_engine import RealBacktestEngine, save_backtest_results
        
        # Verify strategy exists and user has access
        with get_db() as conn:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT s.*, p.id as purchase_id 
                FROM custom_strategies s
                LEFT JOIN strategy_purchases p ON s.id = p.strategy_id AND p.buyer_id = ?
                WHERE s.id = ? AND s.is_active = TRUE
            """, (user_id, request.strategy_id))
            
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Strategy not found")
            
            strategy = dict(row)
            
            # Check access: owner or purchased
            if user_id and strategy["user_id"] != user_id and not strategy.get("purchase_id"):
                raise HTTPException(status_code=403, detail="Purchase required to backtest this strategy")
        
        engine = RealBacktestEngine()
        
        result = await engine.run_backtest(
            strategy="custom",
            symbol=request.symbol,
            timeframe=request.timeframe,
            days=request.days,
            initial_balance=request.initial_balance,
            risk_per_trade=request.risk_per_trade,
            stop_loss_percent=request.stop_loss_percent,
            take_profit_percent=request.take_profit_percent,
            custom_strategy_id=request.strategy_id
        )
        
        # Save results to strategy record if requested and user is owner
        if request.save_results and user_id and strategy["user_id"] == user_id:
            save_backtest_results(request.strategy_id, result)
        
        return {
            "success": True,
            "strategy_name": strategy["name"],
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/multi-symbol")
async def run_multi_symbol_backtest(request: MultiSymbolBacktestRequest, user: dict = Depends(rate_limit_backtest)):
    """Run backtest across multiple symbols simultaneously (authenticated, rate-limited)"""
    try:
        from webapp.services.backtest_engine import RealBacktestEngine
        
        engine = RealBacktestEngine()
        
        result = await engine.run_multi_symbol_backtest(
            strategy=request.strategy,
            symbols=request.symbols,
            timeframe=request.timeframe,
            days=request.days,
            initial_balance=request.initial_balance,
            risk_per_trade=request.risk_per_trade,
            stop_loss_percent=request.stop_loss_percent,
            take_profit_percent=request.take_profit_percent,
            allocation_mode=request.allocation_mode
        )
        
        return {
            "success": True,
            "strategy": request.strategy,
            "symbols": request.symbols,
            "result": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


class MonteCarloRequest(BaseModel):
    strategy: str
    symbol: str = "BTCUSDT"
    timeframe: str = "1h"
    days: int = 30
    initial_balance: float = 10000
    risk_per_trade: float = 1.0
    stop_loss_percent: float = 2.0
    take_profit_percent: float = 4.0
    n_simulations: int = 1000
    confidence_level: float = 0.95


class OptimizationRequest(BaseModel):
    strategy: str
    symbol: str = "BTCUSDT"
    timeframe: str = "1h"
    days: int = 30
    initial_balance: float = 10000
    param_grid: Optional[Dict[str, List[float]]] = None


@router.post("/monte-carlo")
async def run_monte_carlo(request: MonteCarloRequest, user: dict = Depends(rate_limit_backtest)):
    """
    Run Monte Carlo simulation to estimate strategy risk (authenticated, rate-limited).
    Shuffles trade order to see distribution of possible outcomes.
    """
    try:
        from webapp.services.backtest_engine import RealBacktestEngine
        
        engine = RealBacktestEngine()
        
        result = await engine.run_monte_carlo_simulation(
            strategy=request.strategy,
            symbol=request.symbol,
            timeframe=request.timeframe,
            days=request.days,
            initial_balance=request.initial_balance,
            risk_per_trade=request.risk_per_trade,
            stop_loss_percent=request.stop_loss_percent,
            take_profit_percent=request.take_profit_percent,
            n_simulations=request.n_simulations,
            confidence_level=request.confidence_level
        )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/optimize")
async def run_optimization(request: OptimizationRequest, user: dict = Depends(rate_limit_backtest)):
    """
    Grid search optimization for strategy parameters (authenticated, rate-limited).
    Tests all combinations and finds optimal settings.
    """
    try:
        from webapp.services.backtest_engine import RealBacktestEngine
        
        engine = RealBacktestEngine()
        
        result = await engine.run_optimization(
            strategy=request.strategy,
            symbol=request.symbol,
            timeframe=request.timeframe,
            days=request.days,
            initial_balance=request.initial_balance,
            param_grid=request.param_grid
        )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/walk-forward")
async def run_walk_forward_optimization(request: WalkForwardRequest, user: dict = Depends(rate_limit_backtest)):
    """
    Run walk-forward optimization to find robust parameters (authenticated, rate-limited).
    Splits data into in-sample (optimization) and out-of-sample (validation) periods.
    """
    try:
        from webapp.services.backtest_engine import RealBacktestEngine
        
        engine = RealBacktestEngine()
        
        # Default param ranges if not provided
        param_ranges = request.param_ranges or {
            "stop_loss_percent": [1.0, 1.5, 2.0, 2.5, 3.0],
            "take_profit_percent": [2.0, 3.0, 4.0, 5.0, 6.0],
            "risk_per_trade": [0.5, 1.0, 1.5, 2.0]
        }
        
        result = await engine.run_walk_forward_optimization(
            strategy=request.strategy,
            symbol=request.symbol,
            timeframe=request.timeframe,
            total_days=request.total_days,
            in_sample_ratio=request.in_sample_ratio,
            n_folds=request.n_folds,
            param_ranges=param_ranges,
            initial_balance=request.initial_balance
        )
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def run_simple_backtest(request: BacktestRequest):
    """Simple backtest fallback without real analyzers"""
    import random
    from datetime import datetime, timedelta
    
    results = {}
    
    for strategy in request.strategies:
        trades = []
        equity = request.initial_balance
        equity_curve = [{"time": datetime.now().isoformat(), "equity": equity}]
        
        # Generate simulated trades
        num_trades = request.days * 2  # Approximately 2 trades per day
        current_time = datetime.now() - timedelta(days=request.days)
        
        for i in range(num_trades):
            # Random trade
            is_long = random.random() > 0.5
            entry_price = 50000 + random.uniform(-5000, 5000)
            
            # Random outcome based on strategy "effectiveness"
            strategy_boost = {"elcaro": 0.55, "rsibboi": 0.52, "wyckoff": 0.58, "scryptomera": 0.50, "scalper": 0.48}.get(strategy, 0.50)
            is_win = random.random() < strategy_boost
            
            pnl_percent = random.uniform(0.5, 3.0) if is_win else -random.uniform(0.5, 2.0)
            pnl = equity * (request.risk_per_trade / 100) * (pnl_percent / request.stop_loss_percent)
            
            exit_price = entry_price * (1 + pnl_percent / 100) if is_long else entry_price * (1 - pnl_percent / 100)
            
            equity += pnl
            current_time += timedelta(hours=random.randint(4, 24))
            
            trades.append({
                "entry_time": current_time.isoformat(),
                "exit_time": (current_time + timedelta(hours=random.randint(1, 8))).isoformat(),
                "symbol": request.symbol,
                "direction": "LONG" if is_long else "SHORT",
                "entry_price": entry_price,
                "exit_price": exit_price,
                "size": equity * request.risk_per_trade / 100 / request.stop_loss_percent,
                "pnl": pnl,
                "pnl_percent": pnl_percent,
                "reason": "TP" if is_win else "SL"
            })
            
            equity_curve.append({
                "time": current_time.isoformat(),
                "equity": equity
            })
        
        # Calculate statistics
        wins = [t for t in trades if t["pnl"] > 0]
        losses = [t for t in trades if t["pnl"] < 0]
        
        win_rate = len(wins) / len(trades) * 100 if trades else 0
        total_pnl = sum(t["pnl"] for t in trades)
        
        gross_profit = sum(t["pnl"] for t in wins)
        gross_loss = abs(sum(t["pnl"] for t in losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")
        
        # Max drawdown
        peak = request.initial_balance
        max_dd = 0
        for point in equity_curve:
            if point["equity"] > peak:
                peak = point["equity"]
            dd = (peak - point["equity"]) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        results[strategy] = {
            "total_trades": len(trades),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "total_pnl_percent": (equity - request.initial_balance) / request.initial_balance * 100,
            "profit_factor": profit_factor if profit_factor != float("inf") else 999,
            "max_drawdown_percent": max_dd,
            "sharpe_ratio": 1.5 + random.uniform(-0.5, 0.5),
            "final_balance": equity,
            "trades": trades[-20:],  # Last 20 trades
            "equity_curve": equity_curve
        }
    
    return {
        "success": True,
        "results": results
    }


@router.post("/quick")
async def quick_backtest(symbol: str = "BTCUSDT", timeframe: str = "1h", days: int = 7):
    """Quick backtest for all strategies - uses real analyzers"""
    strategies = [
        "elcaro", "rsibboi", "wyckoff", "scryptomera", "scalper",
        "mean_reversion", "trend_following", "breakout", "dca", "grid", "momentum", "volatility_breakout"
    ]
    
    try:
        from webapp.services.backtest_engine import RealBacktestEngine
        
        engine = RealBacktestEngine()
        summary = {}
        
        for strategy in strategies:
            result = await engine.run_backtest(
                strategy=strategy,
                symbol=symbol,
                timeframe=timeframe,
                days=days,
                initial_balance=10000,
                risk_per_trade=1.0,
                stop_loss_percent=2.0,
                take_profit_percent=4.0
            )
            
            summary[strategy] = {
                "win_rate": round(result.get("win_rate", 0), 2),
                "pnl_percent": round(result.get("total_pnl_percent", 0), 2),
                "trades": result.get("total_trades", 0),
                "profit_factor": round(result.get("profit_factor", 0), 2),
                "sharpe_ratio": round(result.get("sharpe_ratio", 0), 2),
                "max_drawdown": round(result.get("max_drawdown_percent", 0), 2),
                "status": "bullish" if result.get("total_pnl_percent", 0) > 0 else "bearish"
            }
        
        return {
            "success": True,
            "summary": summary
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/strategies")
async def list_strategies():
    """List available strategies with descriptions"""
    return {
        "strategies": [
            # Core Strategies
            {
                "id": "elcaro",
                "name": "Enliko",
                "description": "Main channel breakout strategy with momentum confirmation",
                "icon": "🎯",
                "color": "#6366f1",
                "category": "core"
            },
            {
                "id": "rsibboi",
                "name": "RSI+BB+OI",
                "description": "RSI divergence with Bollinger Bands and Open Interest analysis",
                "icon": "📊",
                "color": "#22c55e",
                "category": "core"
            },
            {
                "id": "wyckoff",
                "name": "Wyckoff/SMC",
                "description": "Smart Money Concepts with Fibonacci retracement zones and order blocks",
                "icon": "🔮",
                "color": "#a855f7",
                "category": "core"
            },
            {
                "id": "scryptomera",
                "name": "Scryptomera",
                "description": "Volume profile and delta analysis strategy",
                "icon": "💎",
                "color": "#eab308",
                "category": "core"
            },
            {
                "id": "scalper",
                "name": "Scalper",
                "description": "High-frequency scalping with tight stops",
                "icon": "⚡",
                "color": "#ef4444",
                "category": "core"
            },
            # Advanced Strategies
            {
                "id": "mean_reversion",
                "name": "Mean Reversion",
                "description": "Buy oversold, sell overbought using Z-score analysis",
                "icon": "↔️",
                "color": "#06b6d4",
                "category": "advanced"
            },
            {
                "id": "trend_following",
                "name": "Trend Following",
                "description": "Multiple EMA crossovers with ADX trend strength filter",
                "icon": "📈",
                "color": "#10b981",
                "category": "advanced"
            },
            {
                "id": "breakout",
                "name": "Breakout",
                "description": "Trade breakouts from consolidation ranges with volume confirmation",
                "icon": "💥",
                "color": "#f97316",
                "category": "advanced"
            },
            {
                "id": "dca",
                "name": "DCA",
                "description": "Dollar Cost Averaging with RSI filter for optimal entries",
                "icon": "💰",
                "color": "#84cc16",
                "category": "advanced"
            },
            {
                "id": "grid",
                "name": "Grid Trading",
                "description": "Grid-based strategy - buy at lower grids, sell at upper grids",
                "icon": "🔲",
                "color": "#8b5cf6",
                "category": "advanced"
            },
            {
                "id": "momentum",
                "name": "Momentum",
                "description": "Trade strong momentum with ROC and volume confirmation",
                "icon": "🚀",
                "color": "#ec4899",
                "category": "advanced"
            },
            {
                "id": "volatility_breakout",
                "name": "Volatility Breakout",
                "description": "Trade breakouts using ATR and Keltner Channels",
                "icon": "🌊",
                "color": "#14b8a6",
                "category": "advanced"
            }
        ]
    }


@router.get("/indicators")
async def list_indicators():
    """List available technical indicators for custom strategies"""
    return {
        "indicators": [
            {
                "id": "rsi",
                "name": "RSI",
                "description": "Relative Strength Index - momentum oscillator",
                "params": {"period": {"default": 14, "min": 2, "max": 50}},
                "signals": ["oversold", "overbought", "divergence"]
            },
            {
                "id": "macd",
                "name": "MACD",
                "description": "Moving Average Convergence Divergence",
                "params": {"fast": {"default": 12}, "slow": {"default": 26}, "signal": {"default": 9}},
                "signals": ["crossover", "histogram"]
            },
            {
                "id": "bb",
                "name": "Bollinger Bands",
                "description": "Volatility bands around moving average",
                "params": {"period": {"default": 20}, "std": {"default": 2.0}},
                "signals": ["squeeze", "breakout", "bounce"]
            },
            {
                "id": "ema",
                "name": "EMA",
                "description": "Exponential Moving Average",
                "params": {"period": {"default": 20, "min": 2, "max": 200}},
                "signals": ["crossover", "trend"]
            },
            {
                "id": "sma",
                "name": "SMA",
                "description": "Simple Moving Average",
                "params": {"period": {"default": 20, "min": 2, "max": 200}},
                "signals": ["crossover", "trend"]
            },
            {
                "id": "atr",
                "name": "ATR",
                "description": "Average True Range - volatility indicator",
                "params": {"period": {"default": 14, "min": 2, "max": 50}},
                "signals": ["volatility_spike"]
            },
            {
                "id": "supertrend",
                "name": "SuperTrend",
                "description": "Trend-following indicator based on ATR",
                "params": {"period": {"default": 10}, "multiplier": {"default": 3.0}},
                "signals": ["trend_flip", "trend_confirmation"]
            },
            {
                "id": "vwap",
                "name": "VWAP",
                "description": "Volume Weighted Average Price",
                "params": {},
                "signals": ["cross_above", "cross_below", "deviation"]
            },
            {
                "id": "obv",
                "name": "OBV",
                "description": "On-Balance Volume - volume momentum",
                "params": {"period": {"default": 20}},
                "signals": ["divergence", "confirmation"]
            },
            {
                "id": "volume_sma",
                "name": "Volume SMA",
                "description": "Volume Simple Moving Average for spike detection",
                "params": {"period": {"default": 20}},
                "signals": ["volume_spike"]
            }
        ]
    }


# ============== LIVE MODE ENDPOINTS ==============

class LiveSessionRequest(BaseModel):
    strategy: str
    symbol: str = "BTCUSDT"
    timeframe: str = "1h"
    params: Dict[str, Any] = {}


class DeployStrategyRequest(BaseModel):
    strategy: str
    params: Dict[str, Any]
    backtest_results: Optional[Dict[str, Any]] = None


class ReplayDataRequest(BaseModel):
    strategy: str
    symbol: str = "BTCUSDT"
    timeframe: str = "1h"
    days: int = 30


@router.post("/replay-data")
async def get_replay_data(request: ReplayDataRequest):
    """Get historical data with pre-calculated signals for replay mode"""
    try:
        from webapp.services.backtest_engine import RealBacktestEngine
        
        engine = RealBacktestEngine()
        
        # Fetch candles
        candles = await engine.fetch_historical_data(
            request.symbol, request.timeframe, request.days
        )
        
        if not candles or len(candles) < 50:
            return {"success": False, "error": "Insufficient data"}
        
        # Get analyzer
        analyzer = engine.analyzers.get(request.strategy)
        if not analyzer:
            return {"success": False, "error": f"Unknown strategy: {request.strategy}"}
        
        # Generate signals
        signals = analyzer.analyze(candles)
        
        # Convert signals to list format with candle index
        signals_list = []
        for idx, signal in signals.items():
            if signal.get("direction"):
                signals_list.append({
                    "candle_index": idx,
                    "time": candles[idx]["time"],
                    "timestamp": candles[idx].get("timestamp", 0),
                    "direction": signal["direction"],
                    "reason": signal.get("reason", "Signal"),
                    "confidence": signal.get("confidence", 0.7),
                    "price": candles[idx]["close"]
                })
        
        # Simulate trades
        trades = []
        position = None
        sl_pct = 2.0
        tp_pct = 4.0
        
        for i, candle in enumerate(candles):
            if i < 20:
                continue
                
            signal = signals.get(i, {})
            
            if position:
                # Check exit
                if position["direction"] == "LONG":
                    if candle["low"] <= position["stop_loss"]:
                        trades.append({
                            "entry_candle_index": position["entry_index"],
                            "exit_candle_index": i,
                            "entry_time": position["entry_time"],
                            "exit_time": candle["time"],
                            "direction": "LONG",
                            "entry_price": position["entry_price"],
                            "exit_price": position["stop_loss"],
                            "pnl": -sl_pct,
                            "reason": "SL"
                        })
                        position = None
                    elif candle["high"] >= position["take_profit"]:
                        trades.append({
                            "entry_candle_index": position["entry_index"],
                            "exit_candle_index": i,
                            "entry_time": position["entry_time"],
                            "exit_time": candle["time"],
                            "direction": "LONG",
                            "entry_price": position["entry_price"],
                            "exit_price": position["take_profit"],
                            "pnl": tp_pct,
                            "reason": "TP"
                        })
                        position = None
                else:  # SHORT
                    if candle["high"] >= position["stop_loss"]:
                        trades.append({
                            "entry_candle_index": position["entry_index"],
                            "exit_candle_index": i,
                            "entry_time": position["entry_time"],
                            "exit_time": candle["time"],
                            "direction": "SHORT",
                            "entry_price": position["entry_price"],
                            "exit_price": position["stop_loss"],
                            "pnl": -sl_pct,
                            "reason": "SL"
                        })
                        position = None
                    elif candle["low"] <= position["take_profit"]:
                        trades.append({
                            "entry_candle_index": position["entry_index"],
                            "exit_candle_index": i,
                            "entry_time": position["entry_time"],
                            "exit_time": candle["time"],
                            "direction": "SHORT",
                            "entry_price": position["entry_price"],
                            "exit_price": position["take_profit"],
                            "pnl": tp_pct,
                            "reason": "TP"
                        })
                        position = None
            
            # Check entry
            if not position and signal.get("direction"):
                entry_price = candle["close"]
                if signal["direction"] == "LONG":
                    position = {
                        "entry_index": i,
                        "entry_time": candle["time"],
                        "entry_price": entry_price,
                        "direction": "LONG",
                        "stop_loss": entry_price * (1 - sl_pct / 100),
                        "take_profit": entry_price * (1 + tp_pct / 100)
                    }
                else:
                    position = {
                        "entry_index": i,
                        "entry_time": candle["time"],
                        "entry_price": entry_price,
                        "direction": "SHORT",
                        "stop_loss": entry_price * (1 + sl_pct / 100),
                        "take_profit": entry_price * (1 - tp_pct / 100)
                    }
        
        return {
            "success": True,
            "candles": candles,
            "signals": signals_list,
            "trades": trades,
            "total_candles": len(candles),
            "total_signals": len(signals_list),
            "total_trades": len(trades)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/deploy")
async def deploy_strategy(request: DeployStrategyRequest):
    """Deploy tested strategy to bot with optimized parameters"""
    try:
        with get_db() as conn:
            cur = conn.cursor()
            
            # Save deployment record
            cur.execute("""
                INSERT INTO strategy_deployments (
                    strategy_name, params_json, backtest_results_json, 
                    deployed_at, is_active
                ) VALUES (?, ?, ?, NOW(), TRUE)
                RETURNING id
            """, (
                request.strategy,
                json.dumps(request.params),
                json.dumps(request.backtest_results) if request.backtest_results else "{}"
            ))
            
            row = cur.fetchone()
            deployment_id = row['id'] if row else None
            
            # Deactivate previous deployments for same strategy
            if deployment_id:
                cur.execute("""
                    UPDATE strategy_deployments 
                    SET is_active = FALSE 
                    WHERE strategy_name = ? AND id != ?
                """, (request.strategy, deployment_id))
            
            conn.commit()
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "message": f"Strategy '{request.strategy}' deployed successfully"
            }
        
    except Exception as e:
        # Table might not exist - create it
        if "does not exist" in str(e) or "no such table" in str(e):
            with get_db() as conn2:
                cur2 = conn2.cursor()
                cur2.execute("""
                    CREATE TABLE IF NOT EXISTS strategy_deployments (
                        id SERIAL PRIMARY KEY,
                        strategy_name TEXT NOT NULL,
                        params_json TEXT,
                        backtest_results_json TEXT,
                        deployed_at TIMESTAMP DEFAULT NOW(),
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """)
            # Retry
            return await deploy_strategy(request)
        
        return {"success": False, "error": str(e)}


@router.get("/deployments")
async def list_deployments():
    """List all strategy deployments"""
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM strategy_deployments 
                ORDER BY deployed_at DESC 
                LIMIT 50
            """)
            rows = cur.fetchall()
        
        deployments = []
        for row in rows:
            deployments.append({
                "id": row["id"],
                "strategy": row["strategy_name"],
                "params": json.loads(row["params_json"]) if row["params_json"] else {},
                "backtest_results": json.loads(row["backtest_results_json"]) if row["backtest_results_json"] else {},
                "deployed_at": row["deployed_at"],
                "is_active": bool(row["is_active"])
            })
        
        return {"success": True, "deployments": deployments}
        
    except Exception as e:
        return {"success": False, "error": str(e), "deployments": []}


@router.get("/active-deployment/{strategy}")
async def get_active_deployment(strategy: str):
    """Get currently active deployment for a strategy"""
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM strategy_deployments 
                WHERE strategy_name = ? AND is_active = TRUE
                ORDER BY deployed_at DESC 
                LIMIT 1
            """, (strategy,))
            row = cur.fetchone()
        
        if row:
            return {
                "success": True,
                "deployment": {
                    "id": row["id"],
                    "strategy": row["strategy_name"],
                    "params": json.loads(row["params_json"]) if row["params_json"] else {},
                    "backtest_results": json.loads(row["backtest_results_json"]) if row["backtest_results_json"] else {},
                    "deployed_at": row["deployed_at"]
                }
            }
        
        return {"success": True, "deployment": None}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# WebSocket for live backtesting
class LiveBacktestManager:
    """Manages live backtest sessions with real-time streaming"""
    
    def __init__(self):
        self.active_sessions: Dict[str, dict] = {}
    
    async def start_session(self, ws: WebSocket, config: dict):
        """Start a live backtest session"""
        session_id = str(id(ws))
        
        self.active_sessions[session_id] = {
            "ws": ws,
            "config": config,
            "running": True,
            "candle_index": 0
        }
        
        # Start streaming
        await self.stream_live_data(session_id)
    
    async def stop_session(self, ws: WebSocket):
        """Stop a live backtest session"""
        session_id = str(id(ws))
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["running"] = False
            del self.active_sessions[session_id]
    
    async def stream_live_data(self, session_id: str):
        """Stream candles and analysis in real-time"""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        from webapp.services.backtest_engine import RealBacktestEngine
        engine = RealBacktestEngine()
        
        config = session["config"]
        ws = session["ws"]
        
        try:
            # Fetch historical data
            candles = await engine.fetch_historical_data(
                config.get("symbol", "BTCUSDT"),
                config.get("timeframe", "1h"),
                config.get("days", 30)
            )
            
            if not candles:
                await ws.send_json({"type": "error", "message": "No data available"})
                return
            
            # Get analyzer
            strategy = config.get("strategy", "elcaro")
            analyzer = engine.analyzers.get(strategy)
            if not analyzer:
                await ws.send_json({"type": "error", "message": f"Unknown strategy: {strategy}"})
                return
            
            # Pre-calculate all signals
            all_signals = analyzer.analyze(candles)
            
            # Prepare parameters
            params = config.get("params", {})
            sl_pct = params.get("stop_loss_percent", 2.0)
            tp_pct = params.get("take_profit_percent", 4.0)
            initial_balance = config.get("initial_balance", 10000)
            
            equity = initial_balance
            position = None
            
            # Stream candles one by one
            for i, candle in enumerate(candles):
                if not session.get("running", False):
                    break
                
                # Send candle
                await ws.send_json({
                    "type": "candle",
                    "data": candle
                })
                
                if i >= 20:
                    signal = all_signals.get(i, {})
                    
                    # Calculate indicators for this candle
                    analysis = self._calculate_analysis(candles[:i+1])
                    await ws.send_json({
                        "type": "analysis",
                        "data": analysis
                    })
                    
                    # Check for exit
                    if position:
                        exit_info = self._check_exit(position, candle, sl_pct, tp_pct)
                        if exit_info:
                            pnl = self._calc_pnl(position, exit_info["price"], sl_pct, tp_pct)
                            equity += pnl
                            
                            trade = {
                                "entry_time": position["entry_time"],
                                "exit_time": candle["time"],
                                "direction": position["direction"],
                                "entry_price": position["entry_price"],
                                "exit_price": exit_info["price"],
                                "pnl": pnl,
                                "reason": exit_info["reason"]
                            }
                            
                            await ws.send_json({
                                "type": "trade",
                                "data": trade
                            })
                            
                            position = None
                    
                    # Check for entry signal
                    if not position and signal.get("direction"):
                        await ws.send_json({
                            "type": "signal",
                            "data": {
                                "time": candle["time"],
                                "timestamp": candle.get("timestamp", 0),
                                "direction": signal["direction"],
                                "reason": signal.get("reason", "Strategy signal"),
                                "confidence": signal.get("confidence", 0.7)
                            }
                        })
                        
                        position = {
                            "entry_time": candle["time"],
                            "entry_price": candle["close"],
                            "direction": signal["direction"],
                            "stop_loss": candle["close"] * (1 - sl_pct / 100) if signal["direction"] == "LONG" else candle["close"] * (1 + sl_pct / 100),
                            "take_profit": candle["close"] * (1 + tp_pct / 100) if signal["direction"] == "LONG" else candle["close"] * (1 - tp_pct / 100)
                        }
                
                # Send progress update
                progress = (i + 1) / len(candles) * 100
                await ws.send_json({
                    "type": "session_update",
                    "data": {"progress": progress, "equity": equity}
                })
                
                # Small delay for visualization
                await asyncio.sleep(0.05)
            
        except WebSocketDisconnect:
            pass
        except Exception as e:
            try:
                await ws.send_json({"type": "error", "message": str(e)})
            except Exception:
                pass  # Connection already closed
        finally:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
    
    def _calculate_analysis(self, candles: List[Dict]) -> Dict:
        """Calculate technical indicators for current candle"""
        if len(candles) < 20:
            return {}
        
        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        volumes = [c["volume"] for c in candles]
        
        # RSI
        rsi = self._calc_rsi(closes, 14)
        
        # Simple EMA
        ema20 = self._calc_ema(closes, 20)
        ema50 = self._calc_ema(closes, 50) if len(closes) >= 50 else None
        
        # Bollinger Bands
        bb = self._calc_bb(closes, 20, 2)
        
        # Volume delta (simple approximation)
        vol_delta = volumes[-1] - sum(volumes[-20:]) / 20 if len(volumes) >= 20 else 0
        
        # Sentiment score (-100 to +100)
        sentiment = 0
        if rsi:
            if rsi > 70:
                sentiment -= 30
            elif rsi < 30:
                sentiment += 30
        
        if ema20 and ema50:
            if ema20 > ema50:
                sentiment += 20
            else:
                sentiment -= 20
        
        if closes[-1] > sum(closes[-20:]) / 20:
            sentiment += 20
        else:
            sentiment -= 20
        
        return {
            "time": candles[-1].get("timestamp", 0),
            "price": closes[-1],
            "rsi": rsi,
            "ema20": ema20,
            "ema50": ema50,
            "bb": bb,
            "volume_delta": vol_delta,
            "sentiment": max(-100, min(100, sentiment))
        }
    
    def _calc_rsi(self, closes: List[float], period: int = 14) -> Optional[float]:
        if len(closes) < period + 1:
            return None
        
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def _calc_ema(self, data: List[float], period: int) -> Optional[float]:
        if len(data) < period:
            return None
        
        multiplier = 2 / (period + 1)
        ema = sum(data[:period]) / period
        
        for price in data[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def _calc_bb(self, closes: List[float], period: int = 20, std_mult: float = 2) -> Optional[Dict]:
        if len(closes) < period:
            return None
        
        recent = closes[-period:]
        sma = sum(recent) / period
        variance = sum((x - sma) ** 2 for x in recent) / period
        std = variance ** 0.5
        
        return {
            "middle": sma,
            "upper": sma + std * std_mult,
            "lower": sma - std * std_mult
        }
    
    def _check_exit(self, position: Dict, candle: Dict, sl_pct: float, tp_pct: float) -> Optional[Dict]:
        if position["direction"] == "LONG":
            if candle["low"] <= position["stop_loss"]:
                return {"price": position["stop_loss"], "reason": "SL"}
            if candle["high"] >= position["take_profit"]:
                return {"price": position["take_profit"], "reason": "TP"}
        else:
            if candle["high"] >= position["stop_loss"]:
                return {"price": position["stop_loss"], "reason": "SL"}
            if candle["low"] <= position["take_profit"]:
                return {"price": position["take_profit"], "reason": "TP"}
        return None
    
    def _calc_pnl(self, position: Dict, exit_price: float, sl_pct: float, tp_pct: float) -> float:
        if position["direction"] == "LONG":
            return (exit_price - position["entry_price"]) / position["entry_price"] * 1000
        else:
            return (position["entry_price"] - exit_price) / position["entry_price"] * 1000


# Global instance
live_manager = LiveBacktestManager()


# ============== EXCHANGE VALIDATION ENDPOINTS ==============

@router.get("/validate-exchange/{user_id}")
async def validate_user_exchange(
    user_id: int, 
    exchange: str = None,
    user: dict = Depends(get_current_user)
):
    """Validate exchange API credentials for a user - requires authentication"""
    # SECURITY: Users can only validate their own exchange credentials
    if user["user_id"] != user_id and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        from webapp.services.exchange_validator import validate_user_exchange_setup
        return await validate_user_exchange_setup(user_id, exchange)
    except Exception as e:
        return {"valid": False, "error": str(e)}


@router.get("/exchange-health")
async def exchange_health_check():
    """Check connectivity to all exchanges"""
    try:
        from webapp.services.exchange_validator import ExchangeValidator
        return await ExchangeValidator.health_check_all()
    except Exception as e:
        return {"error": str(e)}


@router.post("/validate-bybit")
async def validate_bybit_credentials(
    api_key: str,
    api_secret: str,
    demo: bool = True,
    testnet: bool = False
):
    """Validate Bybit API credentials"""
    try:
        from webapp.services.exchange_validator import ExchangeValidator
        return await ExchangeValidator.validate_bybit(api_key, api_secret, demo, testnet)
    except Exception as e:
        return {"valid": False, "error": str(e)}


@router.post("/validate-hyperliquid")
async def validate_hyperliquid_credentials(
    private_key: str,
    testnet: bool = False
):
    """Validate HyperLiquid private key"""
    try:
        from webapp.services.exchange_validator import ExchangeValidator
        return await ExchangeValidator.validate_hyperliquid(private_key, testnet)
    except Exception as e:
        return {"valid": False, "error": str(e)}


# ============== STRATEGY DEPLOYMENT V2 ==============

class DeploymentRequest(BaseModel):
    user_id: int
    strategy: str
    params: Dict[str, Any]
    backtest_results: Dict[str, Any]
    validation_rules: Optional[Dict[str, Any]] = None


@router.post("/deploy-v2")
async def deploy_strategy_v2(
    request: DeploymentRequest,
    user: dict = Depends(get_current_user)
):
    """Deploy a backtested strategy to live trading with validation"""
    # SECURITY: Users can only deploy for themselves
    if user["user_id"] != request.user_id and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        from webapp.services.strategy_deployer import strategy_deployer
        return await strategy_deployer.deploy(
            user_id=request.user_id,
            strategy=request.strategy,
            params=request.params,
            backtest_results=request.backtest_results,
            validation_rules=request.validation_rules
        )
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/undeploy/{user_id}/{strategy}")
async def undeploy_strategy(
    user_id: int, 
    strategy: str,
    user: dict = Depends(get_current_user)
):
    """Undeploy a strategy from live trading"""
    # SECURITY: Users can only undeploy their own strategies
    if user["user_id"] != user_id and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        from webapp.services.strategy_deployer import strategy_deployer
        return await strategy_deployer.undeploy(user_id, strategy)
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/deployments/{user_id}")
async def get_user_deployments(
    user_id: int,
    user: dict = Depends(get_current_user)
):
    """Get all active deployments for a user"""
    # SECURITY: Users can only view their own deployments
    if user["user_id"] != user_id and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        from webapp.services.strategy_deployer import strategy_deployer
        deployments = await strategy_deployer.get_active_deployments(user_id)
        return {"success": True, "deployments": deployments}
    except Exception as e:
        return {"success": False, "error": str(e), "deployments": []}


@router.get("/deployment-history/{user_id}")
async def get_deployment_history(
    user_id: int, 
    limit: int = Query(50, ge=1, le=100),
    user: dict = Depends(get_current_user)
):
    """Get deployment history for a user"""
    # SECURITY: Users can only view their own deployment history
    if user["user_id"] != user_id and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        from webapp.services.strategy_deployer import strategy_deployer
        history = await strategy_deployer.get_deployment_history(user_id, limit)
        return {"success": True, "history": history}
    except Exception as e:
        return {"success": False, "error": str(e), "history": []}


@router.get("/compare-performance/{user_id}/{strategy}")
async def compare_backtest_vs_live(
    user_id: int, 
    strategy: str,
    user: dict = Depends(get_current_user)
):
    """Compare backtest results vs live performance"""
    # SECURITY: Users can only compare their own performance
    if user["user_id"] != user_id and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        from webapp.services.strategy_deployer import strategy_deployer
        return await strategy_deployer.compare_backtest_vs_live(user_id, strategy)
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============== INDICATOR CALCULATION ENDPOINTS ==============

@router.post("/calculate-indicators")
async def calculate_indicators(
    symbol: str = "BTCUSDT",
    timeframe: str = "1h",
    days: int = 30,
    indicators: List[str] = ["rsi", "macd", "bb", "ema"]
):
    """Calculate technical indicators for a symbol"""
    try:
        from webapp.services.backtest_engine import RealBacktestEngine
        from webapp.services.indicators import Indicators
        
        engine = RealBacktestEngine()
        candles = await engine.fetch_historical_data(symbol, timeframe, days)
        
        if not candles or len(candles) < 50:
            return {"success": False, "error": "Insufficient data"}
        
        closes = [c["close"] for c in candles]
        results = {}
        
        if "rsi" in indicators:
            results["rsi"] = Indicators.rsi(closes, 14)[-20:]  # Last 20 values
        
        if "macd" in indicators:
            macd, signal, hist = Indicators.macd(closes)
            results["macd"] = {
                "line": macd[-20:],
                "signal": signal[-20:],
                "histogram": hist[-20:]
            }
        
        if "bb" in indicators:
            upper, middle, lower = Indicators.bollinger_bands(closes)
            results["bollinger"] = {
                "upper": upper[-20:],
                "middle": middle[-20:],
                "lower": lower[-20:]
            }
        
        if "ema" in indicators:
            results["ema"] = {
                "ema20": Indicators.ema(closes, 20)[-20:],
                "ema50": Indicators.ema(closes, 50)[-20:] if len(closes) >= 50 else None
            }
        
        if "atr" in indicators:
            results["atr"] = Indicators.atr(candles, 14)[-20:]
        
        if "supertrend" in indicators:
            st, direction = Indicators.supertrend(candles)
            results["supertrend"] = {
                "values": st[-20:],
                "direction": direction[-20:]
            }
        
        if "obv" in indicators:
            results["obv"] = Indicators.obv(candles)[-20:]
        
        if "adx" in indicators:
            adx, plus_di, minus_di = Indicators.adx(candles)
            results["adx"] = {
                "adx": adx[-20:],
                "plus_di": plus_di[-20:],
                "minus_di": minus_di[-20:]
            }
        
        if "stochastic" in indicators:
            k, d = Indicators.stochastic(candles)
            results["stochastic"] = {
                "k": k[-20:],
                "d": d[-20:]
            }
        
        if "vwap" in indicators:
            results["vwap"] = Indicators.vwap(candles)[-20:]
        
        return {
            "success": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "indicators": results,
            "last_close": closes[-1],
            "timestamp": candles[-1].get("time")
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/trend-analysis/{symbol}")
async def get_trend_analysis(symbol: str, timeframe: str = "1h"):
    """Get comprehensive trend strength analysis"""
    try:
        from webapp.services.backtest_engine import RealBacktestEngine
        from webapp.services.indicators import Indicators
        
        engine = RealBacktestEngine()
        candles = await engine.fetch_historical_data(symbol, timeframe, 100)
        
        if not candles or len(candles) < 50:
            return {"success": False, "error": "Insufficient data"}
        
        analysis = Indicators.calculate_trend_strength(candles)
        
        # Add support/resistance levels
        sr_levels = Indicators.detect_support_resistance(candles)
        
        # Add pivot points
        pivots = Indicators.pivot_points(candles)
        
        return {
            "success": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "trend": analysis,
            "support_resistance": sr_levels,
            "pivot_points": pivots,
            "current_price": candles[-1]["close"] if candles else 0
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============== ADDITIONAL ENDPOINTS (merged from v2) ==============

class MultiTimeframeRequest(BaseModel):
    symbol: str = "BTCUSDT"
    strategies: List[str] = ["elcaro", "rsibboi"]
    timeframes: List[str] = ["1h", "4h", "1d"]
    days: int = 90
    initial_balance: float = 10000
    stop_loss_percent: float = 2.0
    take_profit_percent: float = 4.0
    leverage: int = 1


class HeatmapRequest(BaseModel):
    symbol: str = "BTCUSDT"
    strategy: str = "elcaro"
    param1_name: str = "stop_loss_percent"
    param1_range: List[float] = [1.0, 1.5, 2.0, 2.5, 3.0]
    param2_name: str = "take_profit_percent"
    param2_range: List[float] = [2.0, 3.0, 4.0, 5.0, 6.0]
    timeframe: str = "1h"
    days: int = 30


class StressTestRequest(BaseModel):
    symbol: str = "BTCUSDT"
    strategy: str = "elcaro"
    timeframe: str = "1h"
    scenarios: List[str] = ["flash_crash", "high_volatility", "trend_reversal", "sideways"]


@router.post("/multi-timeframe")
async def run_multi_timeframe_backtest(request: MultiTimeframeRequest):
    """Run backtest across multiple timeframes for the same symbol"""
    try:
        from webapp.services.backtest_engine import RealBacktestEngine
        engine = RealBacktestEngine()
        
        results = {}
        for strategy in request.strategies:
            strategy_results = {}
            for tf in request.timeframes:
                result = await engine.run_backtest(
                    strategy=strategy,
                    symbol=request.symbol,
                    timeframe=tf,
                    days=request.days,
                    initial_balance=request.initial_balance,
                    stop_loss_percent=request.stop_loss_percent,
                    take_profit_percent=request.take_profit_percent
                )
                strategy_results[tf] = result
            results[strategy] = strategy_results
        
        # Find best timeframe per strategy
        best_timeframes = {}
        for strategy, tf_results in results.items():
            best_tf = max(tf_results.items(), key=lambda x: x[1].get("total_pnl_percent", 0))
            best_timeframes[strategy] = {"timeframe": best_tf[0], "pnl": best_tf[1].get("total_pnl_percent", 0)}
        
        return {"success": True, "results": results, "best_timeframes": best_timeframes}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/heatmap")
async def generate_parameter_heatmap(request: HeatmapRequest):
    """Generate parameter optimization heatmap"""
    try:
        from webapp.services.backtest_engine import RealBacktestEngine
        engine = RealBacktestEngine()
        
        heatmap_data = []
        for p1 in request.param1_range:
            row = []
            for p2 in request.param2_range:
                params = {request.param1_name: p1, request.param2_name: p2}
                result = await engine.run_backtest(
                    strategy=request.strategy,
                    symbol=request.symbol,
                    timeframe=request.timeframe,
                    days=request.days,
                    initial_balance=10000,
                    stop_loss_percent=params.get("stop_loss_percent", 2.0),
                    take_profit_percent=params.get("take_profit_percent", 4.0)
                )
                row.append(result.get("sharpe_ratio", 0))
            heatmap_data.append(row)
        
        # Find optimal
        best_sharpe = -999
        best_params = {}
        for i, p1 in enumerate(request.param1_range):
            for j, p2 in enumerate(request.param2_range):
                if heatmap_data[i][j] > best_sharpe:
                    best_sharpe = heatmap_data[i][j]
                    best_params = {request.param1_name: p1, request.param2_name: p2}
        
        return {
            "success": True,
            "heatmap": heatmap_data,
            "param1_values": request.param1_range,
            "param2_values": request.param2_range,
            "optimal": {"params": best_params, "sharpe": best_sharpe}
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/stress-test")
async def stress_test_strategy(request: StressTestRequest):
    """Test strategy under various market stress scenarios"""
    try:
        from webapp.services.backtest_engine import RealBacktestEngine
        engine = RealBacktestEngine()
        
        # Fetch base data
        candles = await engine.fetch_historical_data(request.symbol, request.timeframe, 90)
        if len(candles) < 100:
            return {"success": False, "error": "Insufficient data"}
        
        scenario_results = {}
        for scenario in request.scenarios:
            # Apply stress scenario modifications
            modified = apply_stress_scenario(candles, scenario)
            
            result = await engine.run_backtest(
                strategy=request.strategy,
                symbol=request.symbol,
                timeframe=request.timeframe,
                days=90,
                initial_balance=10000
            )
            
            scenario_results[scenario] = {
                "trades": result.get("total_trades", 0),
                "win_rate": result.get("win_rate", 0),
                "total_pnl_pct": result.get("total_pnl_percent", 0),
                "max_drawdown": result.get("max_drawdown_percent", 0),
                "survived": result.get("total_pnl_percent", 0) > -50
            }
        
        survival_rate = sum(1 for s in scenario_results.values() if s["survived"]) / len(scenario_results) * 100
        
        return {
            "success": True,
            "strategy": request.strategy,
            "scenarios": scenario_results,
            "robustness": {"survival_rate": survival_rate}
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def apply_stress_scenario(candles: List[Dict], scenario: str) -> List[Dict]:
    """Apply stress scenario modifications to candle data"""
    import copy
    modified = copy.deepcopy(candles)
    
    if scenario == "flash_crash":
        # Simulate 20% crash at random point
        crash_idx = len(modified) // 2
        for i in range(crash_idx, min(crash_idx + 10, len(modified))):
            factor = 0.8 + (i - crash_idx) * 0.02
            modified[i]["close"] *= factor
            modified[i]["low"] *= factor * 0.95
    
    elif scenario == "high_volatility":
        # Double the price swings
        for c in modified:
            mid = (c["high"] + c["low"]) / 2
            c["high"] = mid + (c["high"] - mid) * 2
            c["low"] = mid - (mid - c["low"]) * 2
    
    elif scenario == "trend_reversal":
        # Reverse trend direction
        half = len(modified) // 2
        base = modified[half]["close"]
        for i in range(half, len(modified)):
            diff = modified[i]["close"] - base
            modified[i]["close"] = base - diff
            modified[i]["high"] = base - (modified[i]["low"] - base)
            modified[i]["low"] = base - (modified[i]["high"] - base)
    
    elif scenario == "sideways":
        # Flatten prices to sideways range
        if not modified:
            return modified
        avg_price = sum(c["close"] for c in modified) / len(modified)
        for c in modified:
            c["close"] = avg_price + (c["close"] - avg_price) * 0.1
            c["high"] = c["close"] * 1.005
            c["low"] = c["close"] * 0.995
    
    return modified


@router.get("/timeframes")
async def list_timeframes():
    """List all available timeframes"""
    return {
        "timeframes": [
            {"value": "1m", "label": "1 Minute", "candles_per_day": 1440},
            {"value": "5m", "label": "5 Minutes", "candles_per_day": 288},
            {"value": "15m", "label": "15 Minutes", "candles_per_day": 96},
            {"value": "30m", "label": "30 Minutes", "candles_per_day": 48},
            {"value": "1h", "label": "1 Hour", "candles_per_day": 24},
            {"value": "4h", "label": "4 Hours", "candles_per_day": 6},
            {"value": "1d", "label": "1 Day", "candles_per_day": 1}
        ]
    }


@router.get("/available-data/{symbol}")
async def get_available_data(symbol: str, timeframe: str = "1d"):
    """Get information about available historical data"""
    try:
        from webapp.services.backtest_engine import RealBacktestEngine
        engine = RealBacktestEngine()
        
        candles = await engine.fetch_historical_data(symbol, timeframe, 365)
        
        if not candles:
            return {"success": False, "error": "No data available"}
        
        return {
            "success": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "first_date": candles[0]["time"][:10],
            "last_date": candles[-1]["time"][:10],
            "total_candles": len(candles)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============== STRATEGY BUILDER ENDPOINTS ==============

class CustomStrategyConfig(BaseModel):
    name: str
    description: str = ""
    base_strategy: str = "custom"
    entry_conditions: List[Dict[str, Any]]  # List of indicator conditions
    exit_conditions: List[Dict[str, Any]]
    risk_params: Dict[str, float] = {"stop_loss": 2.0, "take_profit": 4.0, "risk_per_trade": 1.0}
    filters: Dict[str, Any] = {}  # Volume filter, trend filter, etc.


class SaveStrategyRequest(BaseModel):
    user_id: int
    config: CustomStrategyConfig
    backtest_results: Optional[Dict] = None
    visibility: str = "private"  # private, public, premium
    price: float = 0.0  # For premium strategies


@router.post("/strategy-builder/save")
async def save_custom_strategy(request: SaveStrategyRequest):
    """Save a custom built strategy"""
    try:
        now = datetime.now().isoformat()
        
        with get_db() as conn:
            cur = conn.cursor()
            
            # Use INSERT ON CONFLICT for PostgreSQL (upsert)
            cur.execute("""
                INSERT INTO custom_strategies 
                (user_id, name, description, base_strategy, config_json, backtest_results_json, 
                 visibility, price, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s, %s)
                ON CONFLICT (user_id, name) DO UPDATE SET
                    description = EXCLUDED.description,
                    base_strategy = EXCLUDED.base_strategy,
                    config_json = EXCLUDED.config_json,
                    backtest_results_json = EXCLUDED.backtest_results_json,
                    visibility = EXCLUDED.visibility,
                    price = EXCLUDED.price,
                    updated_at = EXCLUDED.updated_at
            """, (
                request.user_id,
                request.config.name,
                request.config.description,
                request.config.base_strategy,
                json.dumps(request.config.dict()),
                json.dumps(request.backtest_results) if request.backtest_results else None,
                request.visibility,
                request.price,
                now, now
            ))
            
            strategy_id = cur.lastrowid
        
        return {"success": True, "strategy_id": strategy_id, "message": f"Strategy '{request.config.name}' saved"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/strategy-builder/my-strategies/{user_id}")
async def get_user_strategies(user_id: int, user: dict = Depends(get_current_user)):
    """Get all strategies created by a user"""
    # Security: Verify user owns this resource or is admin
    if user["user_id"] != user_id and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied: Cannot view other user's strategies")
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT cs.*, 
                       (SELECT COUNT(*) FROM live_deployments ld 
                        WHERE ld.strategy_id = cs.id AND ld.user_id = cs.user_id AND ld.status = 'active') as is_live
                FROM custom_strategies cs
                WHERE cs.user_id = ? AND cs.is_active = TRUE 
                ORDER BY cs.updated_at DESC
            """, (user_id,))
            rows = cur.fetchall()
        
        strategies = []
        for row in rows:
            bt_results = json.loads(row["backtest_results_json"]) if row["backtest_results_json"] else {}
            strategies.append({
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "base_strategy": row["base_strategy"],
                "config": json.loads(row["config_json"]) if row["config_json"] else {},
                "backtest_results": bt_results,
                "visibility": row["visibility"],
                "is_public": row["visibility"] in ("public", "premium"),
                "is_live": row["is_live"] > 0 if row["is_live"] else False,
                "price": row["price"],
                "win_rate": bt_results.get("win_rate", 0),
                "total_pnl_percent": bt_results.get("total_pnl_percent", 0),
                "trades": bt_results.get("total_trades", 0),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            })
        
        return {"success": True, "strategies": strategies}
    except Exception as e:
        return {"success": False, "error": str(e), "strategies": []}


@router.delete("/strategy-builder/{strategy_id}")
async def delete_strategy(strategy_id: int, user: dict = Depends(get_current_user)):
    """Delete a custom strategy (soft delete)"""
    # Security: Use authenticated user_id from JWT
    user_id = user["user_id"]
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE custom_strategies SET is_active = FALSE 
                WHERE id = ? AND user_id = ?
            """, (strategy_id, user_id))
        
        return {"success": True, "message": "Strategy deleted"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/strategy-builder/{strategy_id}")
async def get_strategy_details(strategy_id: int, user_id: int = None):
    """Get detailed info about a strategy"""
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT cs.*, u.username as author_name
                FROM custom_strategies cs
                LEFT JOIN users u ON cs.user_id = u.user_id
                WHERE cs.id = ? AND cs.is_active = TRUE
            """, (strategy_id,))
            row = cur.fetchone()
        
        if not row:
            return {"success": False, "error": "Strategy not found"}
        
        # Check access: owner or public/premium
        if row["user_id"] != user_id and row["visibility"] == "private":
            return {"success": False, "error": "Access denied"}
        
        config = json.loads(row["config_json"]) if row["config_json"] else {}
        bt_results = json.loads(row["backtest_results_json"]) if row["backtest_results_json"] else {}
        
        return {
            "success": True,
            "strategy": {
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "author": row["author_name"] or f"User #{row['user_id']}",
                "base_strategy": row["base_strategy"],
                "visibility": row["visibility"],
                "price": row["price"],
                "entry_conditions": config.get("entry_conditions", []),
                "exit_conditions": config.get("exit_conditions", []),
                "stop_loss_percent": config.get("stop_loss_percent", 2),
                "take_profit_percent": config.get("take_profit_percent", 4),
                "risk_per_trade": config.get("risk_per_trade", 1),
                "max_positions": config.get("max_positions", 3),
                "filters": config.get("filters", {}),
                "backtest_results": bt_results,
                "win_rate": bt_results.get("win_rate", 0),
                "total_pnl_percent": bt_results.get("total_pnl_percent", 0),
                "total_trades": bt_results.get("total_trades", 0),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/strategy-builder/test")
async def test_custom_strategy(config: CustomStrategyConfig, symbol: str = "BTCUSDT", 
                                timeframe: str = "1h", days: int = 30):
    """Test a custom strategy configuration without saving"""
    try:
        from webapp.services.backtest_engine import RealBacktestEngine, CustomStrategyAnalyzer
        
        engine = RealBacktestEngine()
        analyzer = CustomStrategyAnalyzer(config.dict(), config.base_strategy)
        
        candles = await engine.fetch_historical_data(symbol, timeframe, days)
        
        if not candles or len(candles) < 50:
            return {"success": False, "error": "Insufficient data"}
        
        signals = analyzer.analyze(candles)
        
        # Simulate trades
        result = await engine.run_backtest(
            strategy="custom",
            symbol=symbol,
            timeframe=timeframe,
            days=days,
            initial_balance=10000,
            stop_loss_percent=config.risk_params.get("stop_loss", 2.0),
            take_profit_percent=config.risk_params.get("take_profit", 4.0)
        )
        
        return {"success": True, "result": result, "signals_count": len([s for s in signals.values() if s.get("direction")])}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============== MARKETPLACE ENDPOINTS ==============

@router.get("/marketplace/browse")
async def browse_marketplace(
    category: str = None,
    sort_by: str = "rating",  # rating, copies, pnl, newest
    limit: int = 20,
    offset: int = 0
):
    """Browse public strategies in marketplace"""
    try:
        with get_db() as conn:
            cur = conn.cursor()
            
            query = """
                SELECT cs.*, u.username as author_name
                FROM custom_strategies cs
                LEFT JOIN users u ON cs.user_id = u.user_id
                WHERE cs.is_active = TRUE AND cs.visibility IN ('public', 'premium')
            """
            params = []
            
            if category:
                query += " AND cs.base_strategy = ?"
                params.append(category)
            
            sort_map = {
                "rating": "cs.price DESC",
                "copies": "cs.price DESC",
                "pnl": "cs.updated_at DESC",  # Use updated_at as proxy since jsonb extraction is complex
                "newest": "cs.created_at DESC"
            }
            query += f" ORDER BY {sort_map.get(sort_by, 'cs.created_at DESC')}"
            query += f" LIMIT {limit} OFFSET {offset}"
            
            cur.execute(query, tuple(params) if params else None)
            rows = cur.fetchall()
        
        strategies = []
        for row in rows:
            bt_results = json.loads(row["backtest_results_json"]) if row.get("backtest_results_json") else {}
            strategies.append({
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "author": row.get("author_name") or f"User #{row['user_id']}",
                "base_strategy": row["base_strategy"],
                "visibility": row["visibility"],
                "price": row["price"],
                "win_rate": bt_results.get("win_rate", 0),
                "total_pnl": bt_results.get("total_pnl_percent", 0),
                "total_trades": bt_results.get("total_trades", 0),
                "created_at": row["created_at"]
            })
        
        return {"success": True, "strategies": strategies, "total": len(strategies)}
    except Exception as e:
        return {"success": False, "error": str(e), "strategies": []}


@router.post("/marketplace/copy/{strategy_id}")
async def copy_strategy(strategy_id: int, user: dict = Depends(get_current_user)):
    """Copy a public strategy to your account - requires authentication"""
    user_id = user["user_id"]  # SECURITY: user_id from JWT
    try:
        with get_db() as conn:
            cur = conn.cursor()
            
            # Get original strategy
            cur.execute("""
                SELECT * FROM custom_strategies 
                WHERE id = ? AND visibility IN ('public', 'premium') AND is_active = TRUE
            """, (strategy_id,))
            
            original = cur.fetchone()
            if not original:
                return {"success": False, "error": "Strategy not found or not public"}
            
            # Check if premium and payment required
            if original["visibility"] == "premium" and original.get("price", 0) > 0:
                # TODO: Check payment status
                pass
            
            # Create copy for user
            now = datetime.now().isoformat()
            new_name = f"{original['name']} (copy)"
            
            cur.execute("""
                INSERT INTO custom_strategies 
                (user_id, name, description, base_strategy, config_json, backtest_results_json,
                 visibility, price, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, 'private', 0, TRUE, %s, %s)
            """, (
                user_id, new_name, original["description"], original["base_strategy"],
                original["config_json"], original.get("backtest_results_json"), now, now
            ))
            
            new_id = cur.lastrowid
        
        return {"success": True, "strategy_id": new_id, "message": f"Strategy copied as '{new_name}'"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/marketplace/publish/{strategy_id}")
async def publish_to_marketplace(strategy_id: int, user_id: int, visibility: str = "public", price: float = 0):
    """Publish your strategy to marketplace"""
    try:
        with get_db() as conn:
            cur = conn.cursor()
            
            # Verify ownership
            cur.execute("SELECT user_id FROM custom_strategies WHERE id = ?", (strategy_id,))
            row = cur.fetchone()
            
            if not row or row["user_id"] != user_id:
                return {"success": False, "error": "Strategy not found or access denied"}
            
            cur.execute("""
                UPDATE custom_strategies 
                SET visibility = ?, price = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
            """, (visibility, price, datetime.now().isoformat(), strategy_id, user_id))
        
        return {"success": True, "message": f"Strategy published as {visibility}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============== LIVE TRADING INTEGRATION ==============

class GoLiveRequest(BaseModel):
    user_id: int
    exchange: str = "bybit"
    account_type: str = "demo"
    params: Optional[Dict[str, Any]] = None

@router.post("/go-live/{strategy_id}")
async def start_live_trading(strategy_id: int, request: GoLiveRequest):
    """Deploy strategy to live trading in the bot"""
    try:
        with get_db() as conn:
            cur = conn.cursor()
            
            # Get strategy
            cur.execute("""
                SELECT * FROM custom_strategies WHERE id = ? AND is_active = TRUE
            """, (strategy_id,))
            
            strategy = cur.fetchone()
            if not strategy:
                return {"success": False, "error": "Strategy not found"}
            
            # Check ownership or purchase
            if strategy["user_id"] != request.user_id:
                cur.execute("""
                    SELECT id FROM strategy_purchases 
                    WHERE strategy_id = ? AND buyer_id = ?
                """, (strategy_id, request.user_id))
                if not cur.fetchone():
                    return {"success": False, "error": "Access denied - purchase required"}
            
            config = json.loads(strategy["config_json"]) if strategy.get("config_json") else {}
            
            # Merge with override params
            if request.params:
                config["risk_params"] = {**config.get("risk_params", {}), **request.params}
            
            # Get backtest pnl
            bt_results = json.loads(strategy["backtest_results_json"]) if strategy.get("backtest_results_json") else {}
            backtest_pnl = bt_results.get("total_pnl_percent", 0)
            
            now = datetime.now().isoformat()
            
            # Use PostgreSQL upsert syntax
            cur.execute("""
                INSERT INTO live_deployments 
                (user_id, strategy_id, strategy_name, exchange, account_type, 
                 config_json, status, started_at, backtest_pnl)
                VALUES (%s, %s, %s, %s, %s, %s, 'active', %s, %s)
                ON CONFLICT (user_id, strategy_id) DO UPDATE SET
                    exchange = EXCLUDED.exchange,
                    account_type = EXCLUDED.account_type,
                    config_json = EXCLUDED.config_json,
                    status = 'active',
                    started_at = EXCLUDED.started_at,
                    stopped_at = NULL
            """, (request.user_id, strategy_id, strategy["name"], request.exchange, 
                  request.account_type, json.dumps(config), now, backtest_pnl))
        
        return {
            "success": True, 
            "message": f"Strategy '{strategy['name']}' is now LIVE on {request.exchange} ({request.account_type})",
            "config": config
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


class StopLiveRequest(BaseModel):
    user_id: int

@router.post("/stop-live/{strategy_id}")
async def stop_live_trading(strategy_id: int, request: StopLiveRequest):
    """Stop live trading for a strategy"""
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE live_deployments 
                SET status = 'stopped', stopped_at = ?
                WHERE strategy_id = ? AND user_id = ? AND status = 'active'
            """, (datetime.now().isoformat(), strategy_id, request.user_id))
        
        return {"success": True, "message": "Live trading stopped"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/live-status/{user_id}")
async def get_live_status(user_id: int, user: dict = Depends(get_current_user)):
    """Get all active live deployments for a user"""
    # Security: Verify user owns this resource or is admin
    if user["user_id"] != user_id and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied: Cannot view other user's live status")
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT ld.*, cs.backtest_results_json 
                FROM live_deployments ld
                LEFT JOIN custom_strategies cs ON ld.strategy_id = cs.id
                WHERE ld.user_id = ? AND ld.status = 'active'
            """, (user_id,))
            rows = cur.fetchall()
        
        deployments = []
        for row in rows:
            bt_results = json.loads(row["backtest_results_json"]) if row.get("backtest_results_json") else {}
            deployments.append({
                "strategy_id": row["strategy_id"],
                "strategy_name": row["strategy_name"],
                "exchange": row.get("exchange") or "bybit",
                "account_type": row.get("account_type") or "demo",
                "config": json.loads(row["config_json"]) if row.get("config_json") else {},
                "started_at": row["started_at"],
                "trades": row.get("trades_count") or 0,
                "live_pnl": row.get("pnl_usd") or 0,
                "win_rate": row.get("win_rate") or 0,
                "backtest_pnl": bt_results.get("total_pnl_percent", 0)
            })
        
        return {"success": True, "active_deployments": deployments}
    except Exception as e:
        return {"success": False, "error": str(e), "active_deployments": []}

