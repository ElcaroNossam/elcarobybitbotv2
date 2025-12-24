"""
Enhanced Backtest API with Editable Strategy Parameters
Allows users to customize and test strategies with any parameter configuration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json

from webapp.services.strategy_parameters import (
    StrategyConfig, StrategyParametersManager, StrategyTemplates
)
from webapp.services.backtest_engine import RealBacktestEngine

router = APIRouter()
manager = StrategyParametersManager()


class StrategyParametersRequest(BaseModel):
    """Request to get or modify strategy parameters"""
    strategy_name: str


class CustomBacktestRequest(BaseModel):
    """Backtest with custom parameters"""
    base_strategy: str  # Template to start from
    custom_params: Dict[str, Any]  # Modified parameters
    symbol: str = "BTCUSDT"
    timeframe: str = "1h"
    days: int = 30
    initial_balance: float = 10000


class AIStrategyRequest(BaseModel):
    """Generate strategy using AI"""
    description: str  # Natural language description
    market_conditions: Optional[str] = None
    optimize_for: str = "sharpe_ratio"  # sharpe_ratio, win_rate, profit_factor


@router.get("/strategies/templates")
async def get_strategy_templates():
    """Get all available strategy templates with their default parameters"""
    templates = StrategyTemplates.get_all_templates()
    return {
        "success": True,
        "templates": {name: config.to_dict() for name, config in templates.items()}
    }


@router.get("/strategies/template/{strategy_name}")
async def get_strategy_template(strategy_name: str):
    """Get specific strategy template with editable parameters"""
    template = manager.get_strategy_template(strategy_name)
    
    if not template:
        raise HTTPException(status_code=404, detail=f"Strategy '{strategy_name}' not found")
    
    return {
        "success": True,
        "strategy": template.to_dict(),
        "editable_params": {
            "indicators": {
                ind_name: {
                    "type": ind.type,
                    "enabled": ind.enabled,
                    "weight": ind.weight,
                    "params": ind.params,
                    "param_descriptions": _get_param_descriptions(ind.type)
                }
                for ind_name, ind in template.indicators.items()
            },
            "risk_management": {
                "risk_per_trade": {
                    "current": template.risk_per_trade,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1,
                    "description": "Percentage of balance to risk per trade"
                },
                "stop_loss_percent": {
                    "current": template.stop_loss_percent,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1,
                    "description": "Stop loss percentage from entry"
                },
                "take_profit_percent": {
                    "current": template.take_profit_percent,
                    "min": 0.1,
                    "max": 20.0,
                    "step": 0.1,
                    "description": "Take profit percentage from entry"
                }
            },
            "logic": {
                "entry_logic": {
                    "current": template.entry_logic,
                    "options": ["AND", "OR", "WEIGHTED"],
                    "description": "How to combine indicator signals for entry"
                },
                "exit_logic": {
                    "current": template.exit_logic,
                    "options": ["TP_SL", "SIGNAL", "TRAILING"],
                    "description": "Exit strategy type"
                }
            }
        }
    }


@router.post("/strategies/validate")
async def validate_strategy(config: Dict):
    """Validate a strategy configuration"""
    try:
        strategy = StrategyConfig.from_dict(config)
        valid, errors = manager.validate_strategy(strategy)
        
        return {
            "success": True,
            "valid": valid,
            "errors": errors
        }
    except Exception as e:
        return {
            "success": False,
            "valid": False,
            "errors": [str(e)]
        }


@router.post("/backtest/custom")
async def run_custom_backtest(request: CustomBacktestRequest):
    """
    Run backtest with custom parameters
    User can modify any parameter from the base template
    """
    try:
        # Create custom strategy from template + modifications
        custom_strategy = manager.create_custom_strategy(
            request.base_strategy,
            request.custom_params
        )
        
        # Validate
        valid, errors = manager.validate_strategy(custom_strategy)
        if not valid:
            raise HTTPException(status_code=400, detail={"errors": errors})
        
        # Run backtest
        engine = RealBacktestEngine()
        result = await engine.run_backtest_with_config(
            strategy_config=custom_strategy,
            symbol=request.symbol,
            timeframe=request.timeframe,
            days=request.days,
            initial_balance=request.initial_balance
        )
        
        return {
            "success": True,
            "strategy": custom_strategy.to_dict(),
            "results": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategies/ai/generate")
async def generate_ai_strategy(request: AIStrategyRequest):
    """
    Generate a new strategy using AI based on natural language description
    Example: "Create a scalping strategy using RSI and BB for 5m timeframe"
    """
    try:
        from webapp.services.ai_strategy_generator import AIStrategyGenerator
        
        generator = AIStrategyGenerator()
        strategy = await generator.generate_custom_strategy(
            user_description=request.description,
            market_conditions=request.market_conditions
        )
        
        return {
            "success": True,
            "strategy": strategy.to_dict(),
            "message": "Strategy generated successfully. Review and adjust parameters as needed."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategies/ai/optimize")
async def optimize_strategy_parameters(base_strategy: str, historical_results: List[Dict]):
    """
    Use AI to optimize strategy parameters based on historical results
    """
    try:
        from webapp.services.ai_strategy_generator import AIStrategyGenerator
        
        generator = AIStrategyGenerator()
        optimized = await generator.optimize_strategy_parameters(
            base_strategy=base_strategy,
            historical_results=historical_results
        )
        
        return {
            "success": True,
            "optimized_strategy": optimized.to_dict(),
            "message": "Parameters optimized based on historical performance"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backtest/compare")
async def compare_strategies(
    strategies: List[Dict],
    symbol: str = "BTCUSDT",
    timeframe: str = "1h",
    days: int = 30,
    initial_balance: float = 10000
):
    """
    Compare multiple strategy configurations side-by-side
    Useful for A/B testing different parameters
    """
    try:
        engine = RealBacktestEngine()
        results = []
        
        for strategy_dict in strategies:
            strategy = StrategyConfig.from_dict(strategy_dict)
            
            result = await engine.run_backtest_with_config(
                strategy_config=strategy,
                symbol=symbol,
                timeframe=timeframe,
                days=days,
                initial_balance=initial_balance
            )
            
            results.append({
                "strategy_name": strategy.name,
                "params": strategy.to_dict(),
                "results": result
            })
        
        # Calculate comparison metrics
        comparison = _compare_results(results)
        
        return {
            "success": True,
            "strategies": results,
            "comparison": comparison,
            "winner": comparison["best_strategy"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indicators/available")
async def get_available_indicators():
    """Get list of all available indicators with their parameters"""
    from webapp.services.strategy_parameters import IndicatorType
    
    indicators = {
        "rsi": {
            "name": "Relative Strength Index",
            "params": {
                "period": {"type": "int", "min": 2, "max": 50, "default": 14},
                "overbought": {"type": "float", "min": 50, "max": 100, "default": 70},
                "oversold": {"type": "float", "min": 0, "max": 50, "default": 30}
            }
        },
        "bb": {
            "name": "Bollinger Bands",
            "params": {
                "period": {"type": "int", "min": 5, "max": 100, "default": 20},
                "std_dev": {"type": "float", "min": 1.0, "max": 4.0, "default": 2.0}
            }
        },
        "macd": {
            "name": "MACD",
            "params": {
                "fast_period": {"type": "int", "min": 5, "max": 30, "default": 12},
                "slow_period": {"type": "int", "min": 10, "max": 50, "default": 26},
                "signal_period": {"type": "int", "min": 5, "max": 20, "default": 9}
            }
        },
        "ema": {
            "name": "Exponential Moving Average",
            "params": {
                "periods": {"type": "array", "default": [9, 21, 50, 200]}
            }
        },
        "volume": {
            "name": "Volume Analysis",
            "params": {
                "ma_period": {"type": "int", "min": 5, "max": 50, "default": 20},
                "spike_threshold": {"type": "float", "min": 1.0, "max": 5.0, "default": 2.0}
            }
        },
        "atr": {
            "name": "Average True Range",
            "params": {
                "period": {"type": "int", "min": 5, "max": 30, "default": 14}
            }
        },
        "adx": {
            "name": "Average Directional Index",
            "params": {
                "period": {"type": "int", "min": 5, "max": 30, "default": 14},
                "threshold": {"type": "float", "min": 10, "max": 50, "default": 25}
            }
        },
        "fibonacci": {
            "name": "Fibonacci Retracement",
            "params": {
                "levels": {"type": "array", "default": [0.236, 0.382, 0.5, 0.618, 0.786]}
            }
        }
    }
    
    return {
        "success": True,
        "indicators": indicators
    }


def _get_param_descriptions(indicator_type: str) -> Dict[str, str]:
    """Get human-readable descriptions for indicator parameters"""
    descriptions = {
        "rsi": {
            "period": "Number of periods for RSI calculation (typical: 14)",
            "overbought": "Level above which asset is considered overbought (typical: 70)",
            "oversold": "Level below which asset is considered oversold (typical: 30)"
        },
        "bb": {
            "period": "Number of periods for moving average (typical: 20)",
            "std_dev": "Number of standard deviations for bands (typical: 2.0)"
        },
        "macd": {
            "fast_period": "Fast EMA period (typical: 12)",
            "slow_period": "Slow EMA period (typical: 26)",
            "signal_period": "Signal line period (typical: 9)"
        }
    }
    return descriptions.get(indicator_type, {})


def _compare_results(results: List[Dict]) -> Dict:
    """Compare backtest results and determine the best strategy"""
    if not results:
        return {}
    
    comparison = {
        "best_strategy": None,
        "metrics": {
            "win_rate": {},
            "total_pnl": {},
            "sharpe_ratio": {},
            "max_drawdown": {},
            "profit_factor": {}
        }
    }
    
    # Find best for each metric
    for metric in comparison["metrics"].keys():
        values = {}
        for result in results:
            strategy_name = result["strategy_name"]
            value = result["results"].get(metric, 0)
            values[strategy_name] = value
        
        # Sort by value (descending, except max_drawdown which is ascending)
        reverse = metric != "max_drawdown"
        sorted_strategies = sorted(values.items(), key=lambda x: x[1], reverse=reverse)
        
        comparison["metrics"][metric] = {
            "best": sorted_strategies[0][0] if sorted_strategies else None,
            "values": values
        }
    
    # Determine overall best (weighted score)
    scores = {}
    for result in results:
        strategy_name = result["strategy_name"]
        r = result["results"]
        
        # Weighted scoring
        score = (
            r.get("win_rate", 0) * 0.2 +
            min(r.get("total_pnl_percent", 0), 100) * 0.3 +
            r.get("sharpe_ratio", 0) * 10 * 0.3 +
            (100 - min(abs(r.get("max_drawdown_percent", 0)), 100)) * 0.2
        )
        scores[strategy_name] = score
    
    comparison["best_strategy"] = max(scores.items(), key=lambda x: x[1])[0] if scores else None
    comparison["scores"] = scores
    
    return comparison
