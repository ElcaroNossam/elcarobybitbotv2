"""
ElCaro Pro Backtest API v2.0
Advanced backtesting endpoints with strategy builder, AI optimization, and real-time paper trading
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import asyncio
import json
from datetime import datetime, timedelta
from enum import Enum

router = APIRouter()


# =====================================================
# ENUMS & MODELS
# =====================================================

class IndicatorType(str, Enum):
    # Trend
    SMA = "sma"
    EMA = "ema"
    WMA = "wma"
    DEMA = "dema"
    TEMA = "tema"
    KAMA = "kama"
    HMA = "hma"
    SUPERTREND = "supertrend"
    PARABOLIC_SAR = "parabolic_sar"
    ICHIMOKU = "ichimoku"
    
    # Momentum
    RSI = "rsi"
    STOCHASTIC = "stochastic"
    STOCHASTIC_RSI = "stochastic_rsi"
    MACD = "macd"
    ROC = "roc"
    MOMENTUM = "momentum"
    WILLIAMS_R = "williams_r"
    CCI = "cci"
    AWESOME_OSCILLATOR = "awesome_oscillator"
    ULTIMATE_OSCILLATOR = "ultimate_oscillator"
    
    # Volatility
    ATR = "atr"
    BOLLINGER_BANDS = "bollinger_bands"
    KELTNER_CHANNELS = "keltner_channels"
    DONCHIAN_CHANNELS = "donchian_channels"
    
    # Volume
    OBV = "obv"
    VWAP = "vwap"
    MFI = "mfi"
    CHAIKIN_MONEY_FLOW = "chaikin_money_flow"
    VOLUME_OSCILLATOR = "volume_oscillator"
    
    # Analysis
    ADX = "adx"
    AROON = "aroon"


class ComparisonOperator(str, Enum):
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    EQUALS = "=="
    CROSSES_ABOVE = "crosses_above"
    CROSSES_BELOW = "crosses_below"


class LogicalOperator(str, Enum):
    AND = "AND"
    OR = "OR"


class TimeframeType(str, Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"


# =====================================================
# REQUEST MODELS
# =====================================================

class IndicatorConfig(BaseModel):
    """Configuration for a single indicator"""
    type: IndicatorType
    params: Dict[str, Any] = Field(default_factory=dict)
    alias: Optional[str] = None  # Custom name for referencing


class Condition(BaseModel):
    """Single condition in a strategy rule"""
    left_operand: str  # "rsi" or "close" or "ema_20" or number
    operator: ComparisonOperator
    right_operand: str  # "30" or "sma_50" or "bb_lower"
    

class ConditionGroup(BaseModel):
    """Group of conditions with logical operator"""
    conditions: List[Condition]
    logic: LogicalOperator = LogicalOperator.AND


class EntryRule(BaseModel):
    """Entry rule configuration"""
    direction: str = "LONG"  # LONG or SHORT
    condition_groups: List[ConditionGroup]
    score_weight: float = 1.0  # For multi-rule scoring


class ExitRule(BaseModel):
    """Exit rule configuration"""
    condition_groups: List[ConditionGroup]
    exit_type: str = "signal"  # signal, trailing_stop, time_based


class RiskManagement(BaseModel):
    """Risk management configuration"""
    stop_loss_percent: float = 2.0
    take_profit_percent: float = 4.0
    trailing_stop: bool = False
    trailing_stop_activation: float = 2.0  # Activate after X% profit
    trailing_stop_distance: float = 1.0  # Trail by X%
    max_positions: int = 1
    position_sizing: str = "fixed_percent"  # fixed_percent, kelly, volatility_adjusted
    risk_per_trade: float = 1.0  # % of capital


class CustomStrategyRequest(BaseModel):
    """Complete custom strategy configuration"""
    name: str
    description: Optional[str] = None
    indicators: List[IndicatorConfig]
    entry_rules: List[EntryRule]
    exit_rules: List[ExitRule]
    risk_management: RiskManagement
    filters: Optional[Dict[str, Any]] = None  # Additional filters


class ProBacktestRequest(BaseModel):
    """Professional backtest request"""
    strategy: Optional[str] = None  # Preset strategy name
    custom_strategy: Optional[CustomStrategyRequest] = None  # Or custom config
    symbols: List[str] = ["BTCUSDT"]
    timeframe: TimeframeType = TimeframeType.H1
    start_date: Optional[str] = None  # YYYY-MM-DD
    end_date: Optional[str] = None
    days: int = 30  # If no dates specified
    initial_balance: float = 10000
    commission: float = 0.1  # 0.1%
    slippage: float = 0.05  # 0.05%
    use_leverage: bool = True
    max_leverage: int = 10


class PortfolioBacktestRequest(BaseModel):
    """Portfolio backtest with multiple strategies"""
    strategies: List[Dict[str, Any]]  # List of strategy configs
    symbols: List[str]
    timeframe: TimeframeType = TimeframeType.H1
    days: int = 30
    initial_balance: float = 10000
    rebalance_frequency: str = "daily"  # daily, weekly, monthly
    correlation_limit: float = 0.7  # Max correlation between positions


class OptimizationRequest(BaseModel):
    """Strategy optimization request"""
    base_strategy: CustomStrategyRequest
    param_ranges: Dict[str, Dict[str, Any]]  # {"indicator.param": {"min": 5, "max": 50, "step": 5}}
    optimization_target: str = "sharpe_ratio"  # sharpe_ratio, total_return, calmar_ratio, win_rate
    max_iterations: int = 100
    use_genetic_algorithm: bool = False
    walk_forward: bool = True
    walk_forward_folds: int = 5


class AIStrategyGeneratorRequest(BaseModel):
    """AI-powered strategy generation"""
    target_market: str = "crypto_volatile"  # crypto_volatile, crypto_trending, forex_range
    risk_profile: str = "moderate"  # conservative, moderate, aggressive
    preferred_timeframes: List[TimeframeType] = [TimeframeType.H1, TimeframeType.H4]
    indicators_to_use: Optional[List[IndicatorType]] = None
    avoid_indicators: Optional[List[IndicatorType]] = None
    min_win_rate: float = 50
    max_drawdown: float = 20
    symbols_to_test: List[str] = ["BTCUSDT", "ETHUSDT"]


class ReplayRequest(BaseModel):
    """Market replay request for visual backtesting"""
    symbol: str = "BTCUSDT"
    timeframe: TimeframeType = TimeframeType.H1
    start_date: str  # YYYY-MM-DD HH:MM
    end_date: str
    speed: float = 1.0  # 1x, 2x, 5x, etc.
    strategy: Optional[str] = None


class SignalScannerRequest(BaseModel):
    """Real-time signal scanner"""
    strategies: List[str]
    symbols: List[str]
    timeframes: List[TimeframeType]
    min_score: int = 70


# =====================================================
# RESPONSE MODELS  
# =====================================================

class TradeResult(BaseModel):
    entry_time: str
    exit_time: str
    symbol: str
    direction: str
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    pnl_percent: float
    commission: float
    reason: str
    duration_hours: float
    max_drawdown: float
    max_profit: float


class BacktestMetrics(BaseModel):
    # Core metrics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    # Returns
    total_return: float
    total_return_percent: float
    annualized_return: float
    
    # Risk metrics
    max_drawdown_percent: float
    max_drawdown_duration_days: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    
    # Trade metrics
    avg_win: float
    avg_loss: float
    avg_trade: float
    profit_factor: float
    payoff_ratio: float
    
    # Time metrics
    avg_trade_duration_hours: float
    max_consecutive_wins: int
    max_consecutive_losses: int
    
    # Advanced
    recovery_factor: float
    expectancy: float
    sqn: float  # System Quality Number


class ProBacktestResponse(BaseModel):
    success: bool
    metrics: Optional[BacktestMetrics] = None
    trades: Optional[List[TradeResult]] = None
    equity_curve: Optional[List[Dict[str, Any]]] = None
    drawdown_curve: Optional[List[Dict[str, Any]]] = None
    monthly_returns: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


# =====================================================
# ENDPOINTS
# =====================================================

@router.post("/pro/run", response_model=ProBacktestResponse)
async def run_pro_backtest(request: ProBacktestRequest):
    """
    Run professional backtest with advanced metrics and custom strategies
    """
    try:
        from webapp.services.backtest_engine_pro import ProBacktestEngine
        
        engine = ProBacktestEngine()
        result = await engine.run(
            strategy=request.strategy,
            custom_strategy=request.custom_strategy.dict() if request.custom_strategy else None,
            symbols=request.symbols,
            timeframe=request.timeframe.value,
            days=request.days,
            initial_balance=request.initial_balance,
            commission=request.commission,
            slippage=request.slippage
        )
        
        return ProBacktestResponse(
            success=True,
            metrics=BacktestMetrics(**result["metrics"]),
            trades=result["trades"],
            equity_curve=result["equity_curve"],
            drawdown_curve=result["drawdown_curve"],
            monthly_returns=result["monthly_returns"]
        )
        
    except Exception as e:
        return ProBacktestResponse(success=False, error=str(e))


@router.post("/portfolio")
async def run_portfolio_backtest(request: PortfolioBacktestRequest):
    """
    Run portfolio backtest with multiple strategies and correlation analysis
    """
    try:
        from webapp.services.backtest_engine_pro import ProBacktestEngine
        
        engine = ProBacktestEngine()
        result = await engine.run_portfolio(
            strategies=request.strategies,
            symbols=request.symbols,
            timeframe=request.timeframe.value,
            days=request.days,
            initial_balance=request.initial_balance,
            rebalance_frequency=request.rebalance_frequency,
            correlation_limit=request.correlation_limit
        )
        
        return {
            "success": True,
            "portfolio_metrics": result["portfolio_metrics"],
            "strategy_contributions": result["strategy_contributions"],
            "correlation_matrix": result["correlation_matrix"],
            "optimal_weights": result["optimal_weights"],
            "equity_curve": result["equity_curve"]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/optimize")
async def optimize_strategy(request: OptimizationRequest):
    """
    Optimize strategy parameters using grid search or genetic algorithm
    """
    try:
        from webapp.services.strategy_optimizer import StrategyOptimizer
        
        optimizer = StrategyOptimizer()
        
        if request.use_genetic_algorithm:
            result = await optimizer.genetic_optimization(
                base_strategy=request.base_strategy.dict(),
                param_ranges=request.param_ranges,
                target=request.optimization_target,
                max_iterations=request.max_iterations
            )
        else:
            result = await optimizer.grid_search(
                base_strategy=request.base_strategy.dict(),
                param_ranges=request.param_ranges,
                target=request.optimization_target,
                walk_forward=request.walk_forward,
                n_folds=request.walk_forward_folds
            )
        
        return {
            "success": True,
            "best_params": result["best_params"],
            "best_score": result["best_score"],
            "optimization_curve": result["optimization_curve"],
            "param_importance": result["param_importance"],
            "top_10_combinations": result["top_10"],
            "walk_forward_results": result.get("walk_forward_results")
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/ai/generate")
async def ai_generate_strategy(request: AIStrategyGeneratorRequest):
    """
    Use AI to generate optimized trading strategy based on market conditions
    """
    try:
        from webapp.services.ai_strategy_generator import AIStrategyGenerator
        
        generator = AIStrategyGenerator()
        strategies = await generator.generate(
            target_market=request.target_market,
            risk_profile=request.risk_profile,
            preferred_timeframes=[tf.value for tf in request.preferred_timeframes],
            indicators_to_use=[i.value for i in request.indicators_to_use] if request.indicators_to_use else None,
            avoid_indicators=[i.value for i in request.avoid_indicators] if request.avoid_indicators else None,
            min_win_rate=request.min_win_rate,
            max_drawdown=request.max_drawdown,
            symbols_to_test=request.symbols_to_test
        )
        
        return {
            "success": True,
            "generated_strategies": strategies,
            "recommendation": strategies[0] if strategies else None,
            "reasoning": generator.get_reasoning()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/compare")
async def compare_strategies(
    strategies: List[str],
    symbols: List[str] = Query(["BTCUSDT"]),
    timeframe: TimeframeType = TimeframeType.H1,
    days: int = 30,
    initial_balance: float = 10000
):
    """
    Compare multiple strategies side by side
    """
    try:
        from webapp.services.backtest_engine_pro import ProBacktestEngine
        
        engine = ProBacktestEngine()
        results = {}
        
        for strategy in strategies:
            result = await engine.run(
                strategy=strategy,
                symbols=symbols,
                timeframe=timeframe.value,
                days=days,
                initial_balance=initial_balance
            )
            results[strategy] = {
                "metrics": result["metrics"],
                "equity_curve": result["equity_curve"]
            }
        
        # Calculate rankings
        rankings = {}
        metrics_to_rank = ["sharpe_ratio", "total_return_percent", "win_rate", "profit_factor"]
        
        for metric in metrics_to_rank:
            sorted_strategies = sorted(
                results.items(),
                key=lambda x: x[1]["metrics"].get(metric, 0),
                reverse=True
            )
            rankings[metric] = [s[0] for s in sorted_strategies]
        
        return {
            "success": True,
            "results": results,
            "rankings": rankings,
            "best_overall": rankings["sharpe_ratio"][0] if rankings["sharpe_ratio"] else None
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/strategies")
async def list_available_strategies():
    """
    List all available preset strategies with their descriptions
    """
    strategies = [
        {
            "id": "rsibboi",
            "name": "RSI + Bollinger Bands + OI",
            "category": "mean_reversion",
            "description": "Combines RSI oversold/overbought with Bollinger Band touches and Open Interest divergence",
            "recommended_timeframes": ["1h", "4h"],
            "avg_win_rate": 58,
            "risk_level": "moderate"
        },
        {
            "id": "wyckoff",
            "name": "Wyckoff + SMC",
            "category": "price_action",
            "description": "Wyckoff accumulation/distribution with Smart Money Concepts order blocks",
            "recommended_timeframes": ["4h", "1d"],
            "avg_win_rate": 62,
            "risk_level": "moderate"
        },
        {
            "id": "elcaro",
            "name": "ElCaro Channel Breakout",
            "category": "breakout",
            "description": "Channel breakout with momentum confirmation and volume filter",
            "recommended_timeframes": ["1h", "4h"],
            "avg_win_rate": 55,
            "risk_level": "aggressive"
        },
        {
            "id": "scryptomera",
            "name": "Scryptomera Volume Profile",
            "category": "volume",
            "description": "Volume profile analysis with price action confirmation",
            "recommended_timeframes": ["15m", "1h"],
            "avg_win_rate": 52,
            "risk_level": "aggressive"
        },
        {
            "id": "scalper",
            "name": "Quick Scalper",
            "category": "scalping",
            "description": "Fast EMA crossover scalping with tight stops",
            "recommended_timeframes": ["5m", "15m"],
            "avg_win_rate": 48,
            "risk_level": "aggressive"
        },
        {
            "id": "mean_reversion",
            "name": "Mean Reversion Z-Score",
            "category": "mean_reversion",
            "description": "Statistical mean reversion using Z-score extremes",
            "recommended_timeframes": ["1h", "4h"],
            "avg_win_rate": 56,
            "risk_level": "conservative"
        },
        {
            "id": "trend_following",
            "name": "Triple EMA Trend",
            "category": "trend",
            "description": "Multiple EMA alignment with ADX trend strength filter",
            "recommended_timeframes": ["4h", "1d"],
            "avg_win_rate": 45,
            "risk_level": "moderate"
        },
        {
            "id": "breakout",
            "name": "Consolidation Breakout",
            "category": "breakout",
            "description": "Trades breakouts from low-volatility consolidation zones",
            "recommended_timeframes": ["1h", "4h"],
            "avg_win_rate": 42,
            "risk_level": "moderate"
        },
        {
            "id": "momentum",
            "name": "Momentum Surge",
            "category": "momentum",
            "description": "ROC-based momentum with volume confirmation",
            "recommended_timeframes": ["1h", "4h"],
            "avg_win_rate": 50,
            "risk_level": "aggressive"
        },
        {
            "id": "volatility_breakout",
            "name": "Keltner Volatility Breakout",
            "category": "volatility",
            "description": "ATR-based Keltner Channel breakouts",
            "recommended_timeframes": ["1h", "4h"],
            "avg_win_rate": 54,
            "risk_level": "moderate"
        },
        {
            "id": "grid",
            "name": "Grid Trading",
            "category": "range",
            "description": "Range-based grid trading in consolidation zones",
            "recommended_timeframes": ["15m", "1h"],
            "avg_win_rate": 65,
            "risk_level": "conservative"
        },
        {
            "id": "dca",
            "name": "Smart DCA",
            "category": "accumulation",
            "description": "RSI-filtered dollar cost averaging",
            "recommended_timeframes": ["4h", "1d"],
            "avg_win_rate": 70,
            "risk_level": "conservative"
        }
    ]
    
    return {
        "success": True,
        "strategies": strategies,
        "total": len(strategies)
    }


@router.get("/indicators")
async def list_available_indicators():
    """
    List all available technical indicators with parameters
    """
    indicators = {
        "trend": [
            {"id": "sma", "name": "Simple Moving Average", "params": {"period": {"type": "int", "default": 20, "min": 2, "max": 500}}},
            {"id": "ema", "name": "Exponential Moving Average", "params": {"period": {"type": "int", "default": 20, "min": 2, "max": 500}}},
            {"id": "wma", "name": "Weighted Moving Average", "params": {"period": {"type": "int", "default": 20, "min": 2, "max": 500}}},
            {"id": "dema", "name": "Double EMA", "params": {"period": {"type": "int", "default": 20, "min": 2, "max": 500}}},
            {"id": "tema", "name": "Triple EMA", "params": {"period": {"type": "int", "default": 20, "min": 2, "max": 500}}},
            {"id": "kama", "name": "Kaufman Adaptive MA", "params": {"period": {"type": "int", "default": 10}, "fast": {"type": "int", "default": 2}, "slow": {"type": "int", "default": 30}}},
            {"id": "hma", "name": "Hull Moving Average", "params": {"period": {"type": "int", "default": 20, "min": 2, "max": 500}}},
            {"id": "supertrend", "name": "SuperTrend", "params": {"period": {"type": "int", "default": 10}, "multiplier": {"type": "float", "default": 3.0, "min": 1.0, "max": 10.0}}},
            {"id": "parabolic_sar", "name": "Parabolic SAR", "params": {"af_start": {"type": "float", "default": 0.02}, "af_max": {"type": "float", "default": 0.2}}},
            {"id": "ichimoku", "name": "Ichimoku Cloud", "params": {"tenkan": {"type": "int", "default": 9}, "kijun": {"type": "int", "default": 26}, "senkou_b": {"type": "int", "default": 52}}}
        ],
        "momentum": [
            {"id": "rsi", "name": "RSI", "params": {"period": {"type": "int", "default": 14, "min": 2, "max": 100}}},
            {"id": "stochastic", "name": "Stochastic", "params": {"k_period": {"type": "int", "default": 14}, "d_period": {"type": "int", "default": 3}}},
            {"id": "stochastic_rsi", "name": "Stochastic RSI", "params": {"rsi_period": {"type": "int", "default": 14}, "stoch_period": {"type": "int", "default": 14}}},
            {"id": "macd", "name": "MACD", "params": {"fast": {"type": "int", "default": 12}, "slow": {"type": "int", "default": 26}, "signal": {"type": "int", "default": 9}}},
            {"id": "roc", "name": "Rate of Change", "params": {"period": {"type": "int", "default": 10}}},
            {"id": "momentum", "name": "Momentum", "params": {"period": {"type": "int", "default": 10}}},
            {"id": "williams_r", "name": "Williams %R", "params": {"period": {"type": "int", "default": 14}}},
            {"id": "cci", "name": "CCI", "params": {"period": {"type": "int", "default": 20}}},
            {"id": "awesome_oscillator", "name": "Awesome Oscillator", "params": {}},
            {"id": "ultimate_oscillator", "name": "Ultimate Oscillator", "params": {"p1": {"type": "int", "default": 7}, "p2": {"type": "int", "default": 14}, "p3": {"type": "int", "default": 28}}}
        ],
        "volatility": [
            {"id": "atr", "name": "Average True Range", "params": {"period": {"type": "int", "default": 14}}},
            {"id": "bollinger_bands", "name": "Bollinger Bands", "params": {"period": {"type": "int", "default": 20}, "std_dev": {"type": "float", "default": 2.0}}},
            {"id": "keltner_channels", "name": "Keltner Channels", "params": {"ema_period": {"type": "int", "default": 20}, "atr_period": {"type": "int", "default": 10}, "multiplier": {"type": "float", "default": 2.0}}},
            {"id": "donchian_channels", "name": "Donchian Channels", "params": {"period": {"type": "int", "default": 20}}}
        ],
        "volume": [
            {"id": "obv", "name": "On-Balance Volume", "params": {}},
            {"id": "vwap", "name": "VWAP", "params": {}},
            {"id": "mfi", "name": "Money Flow Index", "params": {"period": {"type": "int", "default": 14}}},
            {"id": "chaikin_money_flow", "name": "Chaikin Money Flow", "params": {"period": {"type": "int", "default": 20}}},
            {"id": "volume_oscillator", "name": "Volume Oscillator", "params": {"fast": {"type": "int", "default": 5}, "slow": {"type": "int", "default": 20}}},
            {"id": "force_index", "name": "Force Index", "params": {"period": {"type": "int", "default": 13}}}
        ],
        "analysis": [
            {"id": "adx", "name": "ADX", "params": {"period": {"type": "int", "default": 14}}},
            {"id": "aroon", "name": "Aroon", "params": {"period": {"type": "int", "default": 25}}}
        ]
    }
    
    return {
        "success": True,
        "indicators": indicators,
        "total": sum(len(v) for v in indicators.values())
    }


@router.get("/templates")
async def get_strategy_templates():
    """
    Get pre-built strategy templates for quick start
    """
    templates = [
        {
            "id": "golden_cross",
            "name": "Golden Cross",
            "description": "Classic EMA 50/200 crossover strategy",
            "difficulty": "beginner",
            "config": {
                "indicators": [
                    {"type": "ema", "params": {"period": 50}, "alias": "ema_50"},
                    {"type": "ema", "params": {"period": 200}, "alias": "ema_200"}
                ],
                "entry_rules": [
                    {
                        "direction": "LONG",
                        "condition_groups": [
                            {
                                "conditions": [
                                    {"left_operand": "ema_50", "operator": "crosses_above", "right_operand": "ema_200"}
                                ],
                                "logic": "AND"
                            }
                        ]
                    }
                ],
                "exit_rules": [
                    {
                        "condition_groups": [
                            {
                                "conditions": [
                                    {"left_operand": "ema_50", "operator": "crosses_below", "right_operand": "ema_200"}
                                ],
                                "logic": "AND"
                            }
                        ]
                    }
                ],
                "risk_management": {
                    "stop_loss_percent": 5.0,
                    "take_profit_percent": 15.0,
                    "risk_per_trade": 2.0
                }
            }
        },
        {
            "id": "rsi_mean_reversion",
            "name": "RSI Mean Reversion",
            "description": "Buy oversold, sell overbought using RSI extremes",
            "difficulty": "beginner",
            "config": {
                "indicators": [
                    {"type": "rsi", "params": {"period": 14}, "alias": "rsi"}
                ],
                "entry_rules": [
                    {
                        "direction": "LONG",
                        "condition_groups": [
                            {
                                "conditions": [
                                    {"left_operand": "rsi", "operator": "<", "right_operand": "30"}
                                ],
                                "logic": "AND"
                            }
                        ]
                    },
                    {
                        "direction": "SHORT",
                        "condition_groups": [
                            {
                                "conditions": [
                                    {"left_operand": "rsi", "operator": ">", "right_operand": "70"}
                                ],
                                "logic": "AND"
                            }
                        ]
                    }
                ],
                "exit_rules": [
                    {
                        "condition_groups": [
                            {
                                "conditions": [
                                    {"left_operand": "rsi", "operator": ">", "right_operand": "50"}
                                ],
                                "logic": "AND"
                            }
                        ]
                    }
                ],
                "risk_management": {
                    "stop_loss_percent": 2.0,
                    "take_profit_percent": 4.0,
                    "risk_per_trade": 1.0
                }
            }
        },
        {
            "id": "bollinger_squeeze",
            "name": "Bollinger Band Squeeze",
            "description": "Trade breakouts after low volatility periods",
            "difficulty": "intermediate",
            "config": {
                "indicators": [
                    {"type": "bollinger_bands", "params": {"period": 20, "std_dev": 2.0}},
                    {"type": "atr", "params": {"period": 14}, "alias": "atr"},
                    {"type": "rsi", "params": {"period": 14}, "alias": "rsi"}
                ],
                "entry_rules": [
                    {
                        "direction": "LONG",
                        "condition_groups": [
                            {
                                "conditions": [
                                    {"left_operand": "close", "operator": ">", "right_operand": "bb_upper"},
                                    {"left_operand": "rsi", "operator": ">", "right_operand": "50"}
                                ],
                                "logic": "AND"
                            }
                        ]
                    },
                    {
                        "direction": "SHORT",
                        "condition_groups": [
                            {
                                "conditions": [
                                    {"left_operand": "close", "operator": "<", "right_operand": "bb_lower"},
                                    {"left_operand": "rsi", "operator": "<", "right_operand": "50"}
                                ],
                                "logic": "AND"
                            }
                        ]
                    }
                ],
                "risk_management": {
                    "stop_loss_percent": 2.0,
                    "take_profit_percent": 6.0,
                    "risk_per_trade": 1.5
                }
            }
        },
        {
            "id": "supertrend_trend",
            "name": "SuperTrend Trend Rider",
            "description": "Follow trends using SuperTrend with MACD confirmation",
            "difficulty": "intermediate",
            "config": {
                "indicators": [
                    {"type": "supertrend", "params": {"period": 10, "multiplier": 3.0}},
                    {"type": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}},
                    {"type": "adx", "params": {"period": 14}, "alias": "adx"}
                ],
                "entry_rules": [
                    {
                        "direction": "LONG",
                        "condition_groups": [
                            {
                                "conditions": [
                                    {"left_operand": "supertrend_dir", "operator": "==", "right_operand": "1"},
                                    {"left_operand": "macd", "operator": ">", "right_operand": "macd_signal"},
                                    {"left_operand": "adx", "operator": ">", "right_operand": "25"}
                                ],
                                "logic": "AND"
                            }
                        ]
                    },
                    {
                        "direction": "SHORT",
                        "condition_groups": [
                            {
                                "conditions": [
                                    {"left_operand": "supertrend_dir", "operator": "==", "right_operand": "-1"},
                                    {"left_operand": "macd", "operator": "<", "right_operand": "macd_signal"},
                                    {"left_operand": "adx", "operator": ">", "right_operand": "25"}
                                ],
                                "logic": "AND"
                            }
                        ]
                    }
                ],
                "risk_management": {
                    "stop_loss_percent": 3.0,
                    "take_profit_percent": 9.0,
                    "trailing_stop": True,
                    "trailing_stop_activation": 3.0,
                    "trailing_stop_distance": 1.5,
                    "risk_per_trade": 1.5
                }
            }
        },
        {
            "id": "ichimoku_cloud",
            "name": "Ichimoku Cloud Breakout",
            "description": "Trade cloud breakouts with Tenkan/Kijun cross",
            "difficulty": "advanced",
            "config": {
                "indicators": [
                    {"type": "ichimoku", "params": {"tenkan": 9, "kijun": 26, "senkou_b": 52}}
                ],
                "entry_rules": [
                    {
                        "direction": "LONG",
                        "condition_groups": [
                            {
                                "conditions": [
                                    {"left_operand": "close", "operator": ">", "right_operand": "ichimoku_senkou_a"},
                                    {"left_operand": "close", "operator": ">", "right_operand": "ichimoku_senkou_b"},
                                    {"left_operand": "ichimoku_tenkan", "operator": "crosses_above", "right_operand": "ichimoku_kijun"}
                                ],
                                "logic": "AND"
                            }
                        ]
                    }
                ],
                "risk_management": {
                    "stop_loss_percent": 4.0,
                    "take_profit_percent": 12.0,
                    "risk_per_trade": 2.0
                }
            }
        },
        {
            "id": "multi_timeframe_momentum",
            "name": "Multi-Timeframe Momentum",
            "description": "Combine RSI, MACD, and ADX for high-probability entries",
            "difficulty": "advanced",
            "config": {
                "indicators": [
                    {"type": "rsi", "params": {"period": 14}, "alias": "rsi"},
                    {"type": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}},
                    {"type": "adx", "params": {"period": 14}, "alias": "adx"},
                    {"type": "ema", "params": {"period": 200}, "alias": "ema_200"},
                    {"type": "atr", "params": {"period": 14}, "alias": "atr"}
                ],
                "entry_rules": [
                    {
                        "direction": "LONG",
                        "condition_groups": [
                            {
                                "conditions": [
                                    {"left_operand": "close", "operator": ">", "right_operand": "ema_200"},
                                    {"left_operand": "rsi", "operator": ">", "right_operand": "50"},
                                    {"left_operand": "rsi", "operator": "<", "right_operand": "70"},
                                    {"left_operand": "macd", "operator": "crosses_above", "right_operand": "macd_signal"},
                                    {"left_operand": "adx", "operator": ">", "right_operand": "20"}
                                ],
                                "logic": "AND"
                            }
                        ]
                    }
                ],
                "risk_management": {
                    "stop_loss_percent": 2.5,
                    "take_profit_percent": 7.5,
                    "trailing_stop": True,
                    "trailing_stop_activation": 4.0,
                    "trailing_stop_distance": 2.0,
                    "risk_per_trade": 1.0
                }
            }
        }
    ]
    
    return {
        "success": True,
        "templates": templates,
        "total": len(templates)
    }


@router.websocket("/replay/{session_id}")
async def market_replay(websocket: WebSocket, session_id: str):
    """
    Real-time market replay for visual backtesting
    """
    await websocket.accept()
    
    try:
        # Receive configuration
        config = await websocket.receive_json()
        
        from webapp.services.backtest_engine_pro import MarketReplayEngine
        
        engine = MarketReplayEngine()
        await engine.initialize(
            symbol=config.get("symbol", "BTCUSDT"),
            timeframe=config.get("timeframe", "1h"),
            start_date=config.get("start_date"),
            end_date=config.get("end_date"),
            strategy=config.get("strategy")
        )
        
        speed = config.get("speed", 1.0)
        paused = False
        
        while True:
            try:
                # Check for control messages (non-blocking)
                try:
                    msg = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)
                    if msg.get("action") == "pause":
                        paused = True
                    elif msg.get("action") == "resume":
                        paused = False
                    elif msg.get("action") == "speed":
                        speed = max(0.1, float(msg.get("value", 1.0)))  # Prevent division by zero
                    elif msg.get("action") == "stop":
                        break
                except asyncio.TimeoutError:
                    pass
                
                if not paused:
                    # Get next candle
                    candle_data = await engine.next_candle()
                    
                    if candle_data is None:
                        # Replay finished
                        await websocket.send_json({
                            "type": "complete",
                            "final_equity": engine.get_final_equity(),
                            "total_trades": engine.get_total_trades()
                        })
                        break
                    
                    await websocket.send_json({
                        "type": "candle",
                        "data": candle_data
                    })
                    
                    await asyncio.sleep(1.0 / speed)
                else:
                    await asyncio.sleep(0.1)
                    
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        await websocket.close()


@router.websocket("/signals")
async def live_signal_scanner(websocket: WebSocket):
    """
    Real-time signal scanner across multiple strategies and symbols
    """
    await websocket.accept()
    
    try:
        # Receive configuration
        config = await websocket.receive_json()
        
        strategies = config.get("strategies", ["rsibboi", "wyckoff"])
        symbols = config.get("symbols", ["BTCUSDT", "ETHUSDT"])
        timeframes = config.get("timeframes", ["1h", "4h"])
        min_score = config.get("min_score", 70)
        
        from webapp.services.signal_scanner import SignalScanner
        
        scanner = SignalScanner()
        
        while True:
            try:
                # Scan for signals
                signals = await scanner.scan(
                    strategies=strategies,
                    symbols=symbols,
                    timeframes=timeframes,
                    min_score=min_score
                )
                
                if signals:
                    await websocket.send_json({
                        "type": "signals",
                        "data": signals,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Check for updates to config
                try:
                    msg = await asyncio.wait_for(websocket.receive_json(), timeout=30)
                    if msg.get("action") == "update_config":
                        strategies = msg.get("strategies", strategies)
                        symbols = msg.get("symbols", symbols)
                        timeframes = msg.get("timeframes", timeframes)
                        min_score = msg.get("min_score", min_score)
                    elif msg.get("action") == "stop":
                        break
                except asyncio.TimeoutError:
                    pass
                    
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        await websocket.close()


# Paper trading endpoints
@router.post("/paper-trading/start")
async def start_paper_trading(
    strategy: str,
    symbols: List[str] = Query(["BTCUSDT"]),
    initial_balance: float = 10000,
    user_id: Optional[int] = None
):
    """
    Start paper trading session with real-time data
    """
    try:
        from webapp.services.paper_trading import PaperTradingSession
        
        session = PaperTradingSession(
            strategy=strategy,
            symbols=symbols,
            initial_balance=initial_balance,
            user_id=user_id
        )
        
        session_id = await session.start()
        
        return {
            "success": True,
            "session_id": session_id,
            "message": f"Paper trading started with {strategy} strategy"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/paper-trading/{session_id}")
async def get_paper_trading_status(session_id: str):
    """
    Get current status of paper trading session
    """
    try:
        from webapp.services.paper_trading import get_session
        
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "status": session.get_status(),
            "equity": session.get_equity(),
            "positions": session.get_positions(),
            "trades": session.get_trades(),
            "metrics": session.get_metrics()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/paper-trading/{session_id}/stop")
async def stop_paper_trading(session_id: str):
    """
    Stop paper trading session
    """
    try:
        from webapp.services.paper_trading import get_session
        
        session = get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        result = await session.stop()
        
        return {
            "success": True,
            "final_equity": result["final_equity"],
            "total_return": result["total_return"],
            "total_trades": result["total_trades"],
            "win_rate": result["win_rate"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": str(e)}
