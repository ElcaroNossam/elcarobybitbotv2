"""
Strategy Builder API
Complete CRUD + Backtest + Live Trading endpoints for custom strategies

Endpoints:
- POST /strategies - Create new strategy
- GET /strategies - List user's strategies
- GET /strategies/{id} - Get strategy details
- PUT /strategies/{id} - Update strategy
- DELETE /strategies/{id} - Delete strategy
- POST /strategies/{id}/backtest - Run backtest
- GET /strategies/{id}/versions - Get version history
- POST /strategies/{id}/versions/{version_id}/rollback - Rollback to version
- POST /strategies/{id}/start - Start live trading
- POST /strategies/{id}/stop - Stop live trading
- POST /strategies/{id}/pause - Pause trading
- POST /strategies/{id}/resume - Resume trading
- GET /strategies/{id}/status - Get live status
- GET /templates - Get strategy templates
- GET /indicators - Get available indicators
- POST /generate - AI: text → strategy
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import db
from models.strategy_spec import (
    StrategySpec, StrategyTemplates, IndicatorType, ConditionOperator,
    IndicatorConfig, Condition, ConditionGroup, EntryRule, ExitRule,
    RiskManagement, Filters, migrate_old_config
)
from webapp.services.backtest_engine import RealBacktestEngine, CustomStrategyAnalyzer
from webapp.services.strategy_runtime import get_orchestrator
from webapp.services.strategy_ai_agent import get_ai_agent, AIGenerationResult

# Try to import auth, fallback to mock if not available
try:
    from webapp.api.auth import get_current_user
except ImportError:
    async def get_current_user():
        return {"user_id": 511692487, "is_admin": True}

router = APIRouter(prefix="/strategies", tags=["strategy-builder"])


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class IndicatorConfigModel(BaseModel):
    type: str
    params: Dict[str, Any] = {}
    field: Optional[str] = None
    timeframe: Optional[str] = None


class ConditionModel(BaseModel):
    id: str
    left: IndicatorConfigModel
    operator: str
    right: Optional[IndicatorConfigModel] = None
    value: Optional[float] = None
    value2: Optional[float] = None
    enabled: bool = True
    description: Optional[str] = None


class ConditionGroupModel(BaseModel):
    id: str
    conditions: List[ConditionModel] = []
    operator: str = "AND"
    enabled: bool = True


class EntryRuleModel(BaseModel):
    direction: str
    groups: List[ConditionGroupModel] = []
    group_operator: str = "AND"
    enabled: bool = True


class ExitRuleModel(BaseModel):
    type: str
    value: Optional[float] = None
    conditions: Optional[ConditionGroupModel] = None
    params: Dict[str, Any] = {}
    enabled: bool = True


class RiskManagementModel(BaseModel):
    position_size_percent: float = 10.0
    max_positions: int = 5
    max_daily_trades: int = 20
    max_daily_loss_percent: float = 10.0
    leverage: int = 10


class FiltersModel(BaseModel):
    min_volume_usdt: Optional[float] = None
    min_volatility: Optional[float] = None
    max_volatility: Optional[float] = None
    time_filters: List[str] = []
    excluded_symbols: List[str] = []
    required_symbols: List[str] = []


class CreateStrategyRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = ""
    long_entry: Optional[EntryRuleModel] = None
    short_entry: Optional[EntryRuleModel] = None
    exit_rules: List[ExitRuleModel] = []
    risk: RiskManagementModel = RiskManagementModel()
    filters: FiltersModel = FiltersModel()
    primary_timeframe: str = "15m"
    higher_timeframes: List[str] = ["1h", "4h"]
    pyramiding: int = 1
    allow_reverse: bool = False


class UpdateStrategyRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    long_entry: Optional[EntryRuleModel] = None
    short_entry: Optional[EntryRuleModel] = None
    exit_rules: Optional[List[ExitRuleModel]] = None
    risk: Optional[RiskManagementModel] = None
    filters: Optional[FiltersModel] = None
    primary_timeframe: Optional[str] = None
    higher_timeframes: Optional[List[str]] = None
    change_log: Optional[str] = None


class BacktestRequest(BaseModel):
    symbol: str = "BTCUSDT"
    timeframe: str = "1h"
    days: int = 30
    initial_balance: float = 10000


class StartLiveRequest(BaseModel):
    exchange: str = "bybit"
    account_type: str = "demo"


class GenerateStrategyRequest(BaseModel):
    description: str = Field(..., min_length=10, description="Natural language description of the strategy")


# ═══════════════════════════════════════════════════════════════════════════════
# STATIC ROUTES (MUST COME BEFORE /{strategy_id} ROUTES)
# These routes use static paths that could be confused with strategy_id parameter
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/templates")
async def get_templates():
    """Get available strategy templates (public endpoint)"""
    templates = {
        "rsi_mean_reversion": {
            "name": "RSI Mean Reversion",
            "description": "Classic RSI oversold/overbought strategy with EMA200 trend filter",
            "config": StrategyTemplates.rsi_mean_reversion().to_dict()
        },
        "bollinger_breakout": {
            "name": "Bollinger Breakout",
            "description": "Breakout strategy using Bollinger Bands expansion",
            "config": StrategyTemplates.bollinger_breakout().to_dict()
        },
        "macd_crossover": {
            "name": "MACD Crossover",
            "description": "Classic MACD signal line crossover strategy",
            "config": StrategyTemplates.macd_crossover().to_dict()
        },
        "multi_indicator": {
            "name": "Multi-Indicator Trend",
            "description": "Complex strategy with EMA alignment, RSI, MACD, and volume confirmation",
            "config": StrategyTemplates.multi_indicator().to_dict()
        }
    }
    return {"templates": templates}


@router.get("/indicators")
async def get_indicators():
    """Get all available indicators with their parameters (public endpoint)"""
    indicators = {
        "trend": [
            {"id": "ema", "name": "EMA", "params": {"period": {"type": "int", "default": 20, "min": 5, "max": 500}}},
            {"id": "sma", "name": "SMA", "params": {"period": {"type": "int", "default": 20, "min": 5, "max": 500}}},
            {"id": "supertrend", "name": "SuperTrend", "params": {
                "period": {"type": "int", "default": 10, "min": 5, "max": 50},
                "multiplier": {"type": "float", "default": 3.0, "min": 1.0, "max": 10.0}
            }},
            {"id": "vwap", "name": "VWAP", "params": {}},
        ],
        "momentum": [
            {"id": "rsi", "name": "RSI", "params": {"period": {"type": "int", "default": 14, "min": 5, "max": 50}}},
            {"id": "macd", "name": "MACD", "params": {
                "fast": {"type": "int", "default": 12},
                "slow": {"type": "int", "default": 26},
                "signal": {"type": "int", "default": 9}
            }, "fields": ["macd", "signal", "histogram"]},
            {"id": "stochastic", "name": "Stochastic", "params": {
                "k_period": {"type": "int", "default": 14},
                "d_period": {"type": "int", "default": 3}
            }, "fields": ["k", "d"]},
        ],
        "volatility": [
            {"id": "bb", "name": "Bollinger Bands", "params": {
                "period": {"type": "int", "default": 20},
                "std_dev": {"type": "float", "default": 2.0}
            }, "fields": ["upper", "middle", "lower"]},
            {"id": "atr", "name": "ATR", "params": {"period": {"type": "int", "default": 14}}},
        ],
        "volume": [
            {"id": "obv", "name": "OBV", "params": {}},
            {"id": "volume", "name": "Volume", "params": {}},
        ],
        "price": [
            {"id": "price_close", "name": "Close Price", "params": {}},
            {"id": "price_high", "name": "High Price", "params": {}},
            {"id": "price_low", "name": "Low Price", "params": {}},
            {"id": "price_open", "name": "Open Price", "params": {}},
        ]
    }
    
    operators = [
        {"id": ">", "name": "Greater than", "description": "Left > Right"},
        {"id": "<", "name": "Less than", "description": "Left < Right"},
        {"id": ">=", "name": "Greater or equal", "description": "Left >= Right"},
        {"id": "<=", "name": "Less or equal", "description": "Left <= Right"},
        {"id": "==", "name": "Equals", "description": "Left == Right"},
        {"id": "crosses_above", "name": "Crosses above", "description": "Left crosses above Right"},
        {"id": "crosses_below", "name": "Crosses below", "description": "Left crosses below Right"},
        {"id": "between", "name": "Between", "description": "Value between two bounds"},
    ]
    
    exit_types = [
        {"id": "take_profit", "name": "Take Profit", "params": {"value": "percent"}},
        {"id": "stop_loss", "name": "Stop Loss", "params": {"value": "percent"}},
        {"id": "trailing_stop", "name": "Trailing Stop", "params": {"value": "percent", "activation_percent": "percent"}},
        {"id": "signal_exit", "name": "Signal Exit", "params": {"conditions": "condition_group"}},
        {"id": "breakeven", "name": "Breakeven", "params": {"activation_percent": "percent", "offset": "percent"}},
    ]
    
    return {
        "indicators": indicators,
        "operators": operators,
        "exit_types": exit_types,
        "timeframes": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
    }


@router.get("/running")
async def get_running_strategies(user = Depends(get_current_user)):
    """Get all running strategies for current user"""
    user_id = user.get("user_id") if isinstance(user, dict) else user
    orchestrator = get_orchestrator()
    running = orchestrator.get_user_running_strategies(user_id)
    return {"running": running, "count": len(running)}


@router.post("/generate")
async def generate_strategy_from_text(request: GenerateStrategyRequest, user = Depends(get_current_user)):
    """
    Generate strategy from natural language description using AI.
    
    Uses OpenAI GPT-4 when available, falls back to template matching.
    
    Examples:
    - "RSI strategy that buys when RSI is below 30 and price is above EMA200"
    - "MACD crossover with Bollinger Bands confirmation on 15m timeframe"
    - "Scalping strategy with tight stops and quick take profits"
    - "Trend following using EMA crossovers with ATR-based stops"
    """
    user_id = user.get("user_id") if isinstance(user, dict) else user
    
    # Get AI agent
    agent = get_ai_agent()
    
    # Generate strategy
    result = await agent.generate(request.description)
    
    if not result.success:
        return {
            "success": False,
            "generated": False,
            "error": result.error,
            "model_used": result.model_used
        }
    
    # Add author_id and update name
    strategy = result.strategy
    strategy["author_id"] = user_id
    
    return {
        "success": True,
        "generated": True,
        "strategy": strategy,
        "model_used": result.model_used,
        "tokens_used": result.tokens_used,
        "message": "Strategy generated from description. Review and customize before saving."
    }


class EnhanceStrategyRequest(BaseModel):
    """Request to enhance an existing strategy"""
    strategy: Dict[str, Any] = Field(..., description="Current strategy configuration")
    feedback: str = Field(..., description="Enhancement request or feedback")


class ExplainStrategyRequest(BaseModel):
    """Request to explain a strategy"""
    strategy: Dict[str, Any] = Field(..., description="Strategy configuration to explain")


@router.post("/enhance")
async def enhance_strategy(request: EnhanceStrategyRequest, user = Depends(get_current_user)):
    """
    Enhance an existing strategy based on user feedback using AI.
    
    Example feedback:
    - "Make it more aggressive with higher leverage"
    - "Add a volume filter to avoid low liquidity trades"
    - "Change to only trade during Asian session"
    """
    agent = get_ai_agent()
    result = await agent.enhance_strategy(request.strategy, request.feedback)
    
    if not result.success:
        return {
            "success": False,
            "enhanced": False,
            "error": result.error,
            "strategy": request.strategy  # Return original
        }
    
    return {
        "success": True,
        "enhanced": True,
        "strategy": result.strategy,
        "model_used": result.model_used,
        "tokens_used": result.tokens_used
    }


@router.post("/explain")
async def explain_strategy(request: ExplainStrategyRequest, user = Depends(get_current_user)):
    """
    Get a human-readable explanation of a strategy.
    Useful for understanding complex strategies.
    """
    agent = get_ai_agent()
    explanation = await agent.explain_strategy(request.strategy)
    
    return {
        "success": True,
        "explanation": explanation,
        "strategy_name": request.strategy.get("name", "Unnamed Strategy")
    }


# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGY CRUD
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("")
async def create_strategy(request: CreateStrategyRequest, user = Depends(get_current_user)):
    """Create a new custom strategy"""
    user_id = user.get("user_id") if isinstance(user, dict) else user
    
    # Build StrategySpec
    spec_dict = {
        "name": request.name,
        "description": request.description,
        "version": "1.0.0",
        "author_id": user_id,
        "long_entry": request.long_entry.dict() if request.long_entry else None,
        "short_entry": request.short_entry.dict() if request.short_entry else None,
        "exit_rules": [e.dict() for e in request.exit_rules] if request.exit_rules else [
            {"type": "take_profit", "value": 4.0, "enabled": True},
            {"type": "stop_loss", "value": 2.0, "enabled": True}
        ],
        "risk": request.risk.dict(),
        "filters": request.filters.dict(),
        "primary_timeframe": request.primary_timeframe,
        "higher_timeframes": request.higher_timeframes,
        "pyramiding": request.pyramiding,
        "allow_reverse": request.allow_reverse,
    }
    
    # Validate
    spec = StrategySpec.from_dict(spec_dict)
    is_valid, errors = spec.validate()
    if not is_valid:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # Create in database
    strategy_id = db.create_custom_strategy(
        user_id=user_id,
        name=request.name,
        description=request.description,
        config=spec_dict
    )
    
    # Create initial version
    db.create_strategy_version(
        strategy_id=strategy_id,
        version="1.0.0",
        config_json=json.dumps(spec_dict),
        created_by=user_id,
        change_log="Initial version"
    )
    
    return {
        "success": True,
        "strategy_id": strategy_id,
        "name": request.name,
        "version": "1.0.0"
    }


@router.get("")
async def list_strategies(
    user = Depends(get_current_user),
    include_purchased: bool = True
):
    """List all strategies owned or purchased by user"""
    user_id = user.get("user_id") if isinstance(user, dict) else user
    
    # Get owned strategies
    owned = db.get_user_strategies(user_id)
    
    # Get purchased strategies
    purchased = []
    if include_purchased:
        purchased = db.get_user_purchases(user_id)
    
    return {
        "owned": owned,
        "purchased": purchased,
        "total": len(owned) + len(purchased)
    }


@router.get("/{strategy_id}")
async def get_strategy(strategy_id: int, user = Depends(get_current_user)):
    """Get strategy details"""
    user_id = user.get("user_id") if isinstance(user, dict) else user
    
    strategy = db.get_strategy_by_id(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Check access
    if strategy["user_id"] != user_id:
        purchases = db.get_user_purchases(user_id)
        if not any(p["strategy_id"] == strategy_id for p in purchases):
            raise HTTPException(status_code=403, detail="No access to this strategy")
    
    # Parse config
    config_json = strategy.get("config") or strategy.get("config_json", "{}")
    config = json.loads(config_json) if isinstance(config_json, str) else config_json
    
    # Get versions
    versions = db.get_strategy_versions(strategy_id)
    
    # Get live status
    orchestrator = get_orchestrator()
    live_statuses = []
    for exchange in ["bybit", "hyperliquid"]:
        for account_type in ["demo", "real"]:
            status = orchestrator.get_strategy_status(user_id, strategy_id, exchange, account_type)
            if status.get("status") != "never_started":
                live_statuses.append({
                    "exchange": exchange,
                    "account_type": account_type,
                    **status
                })
    
    return {
        "id": strategy_id,
        "name": strategy.get("name"),
        "description": strategy.get("description"),
        "config": config,
        "is_active": strategy.get("is_active"),
        "is_public": strategy.get("is_public"),
        "performance_stats": json.loads(strategy.get("performance_stats", "{}")) if strategy.get("performance_stats") else {},
        "created_at": strategy.get("created_at"),
        "updated_at": strategy.get("updated_at"),
        "versions": versions[:5],  # Last 5 versions
        "live_statuses": live_statuses
    }


@router.put("/{strategy_id}")
async def update_strategy(strategy_id: int, request: UpdateStrategyRequest, user = Depends(get_current_user)):
    """Update strategy configuration"""
    user_id = user.get("user_id") if isinstance(user, dict) else user
    
    # Get existing strategy
    strategy = db.get_strategy_by_id(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if strategy["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Cannot update strategy you don't own")
    
    # Parse existing config
    config_json = strategy.get("config") or strategy.get("config_json", "{}")
    config = json.loads(config_json) if isinstance(config_json, str) else config_json
    
    # Update fields
    updates = {}
    if request.name:
        updates["name"] = request.name
        config["name"] = request.name
    if request.description is not None:
        updates["description"] = request.description
        config["description"] = request.description
    if request.long_entry:
        config["long_entry"] = request.long_entry.dict()
    if request.short_entry:
        config["short_entry"] = request.short_entry.dict()
    if request.exit_rules:
        config["exit_rules"] = [e.dict() for e in request.exit_rules]
    if request.risk:
        config["risk"] = request.risk.dict()
    if request.filters:
        config["filters"] = request.filters.dict()
    if request.primary_timeframe:
        config["primary_timeframe"] = request.primary_timeframe
    if request.higher_timeframes:
        config["higher_timeframes"] = request.higher_timeframes
    
    # Increment version
    current_version = config.get("version", "1.0.0")
    parts = current_version.split(".")
    try:
        parts[-1] = str(int(parts[-1]) + 1)
    except ValueError:
        parts[-1] = "1"  # Reset to 1 if not numeric
    new_version = ".".join(parts)
    config["version"] = new_version
    
    updates["config_json"] = config
    
    # Validate
    spec = StrategySpec.from_dict(config)
    is_valid, errors = spec.validate()
    if not is_valid:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # Update in database
    db.update_custom_strategy(strategy_id, user_id, **updates)
    
    # Create new version
    db.create_strategy_version(
        strategy_id=strategy_id,
        version=new_version,
        config_json=json.dumps(config),
        created_by=user_id,
        change_log=request.change_log or "Updated"
    )
    
    return {
        "success": True,
        "strategy_id": strategy_id,
        "version": new_version
    }


@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: int, user = Depends(get_current_user)):
    """Delete a strategy"""
    user_id = user.get("user_id") if isinstance(user, dict) else user
    
    # Check if strategy is running
    orchestrator = get_orchestrator()
    for exchange in ["bybit", "hyperliquid"]:
        for account_type in ["demo", "real"]:
            status = orchestrator.get_strategy_status(user_id, strategy_id, exchange, account_type)
            if status.get("status") == "running":
                raise HTTPException(status_code=400, detail="Cannot delete running strategy. Stop it first.")
    
    # Delete
    deleted = db.delete_custom_strategy(strategy_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Strategy not found or already deleted")
    
    return {"success": True, "deleted": strategy_id}


# ═══════════════════════════════════════════════════════════════════════════════
# BACKTEST
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/{strategy_id}/backtest")
async def backtest_strategy(strategy_id: int, request: BacktestRequest, user = Depends(get_current_user)):
    """Run backtest on a strategy"""
    user_id = user.get("user_id") if isinstance(user, dict) else user
    
    # Get strategy
    strategy = db.get_strategy_by_id(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Check access
    if strategy["user_id"] != user_id:
        purchases = db.get_user_purchases(user_id)
        if not any(p["strategy_id"] == strategy_id for p in purchases):
            raise HTTPException(status_code=403, detail="No access to this strategy")
    
    # Parse config
    config_json = strategy.get("config") or strategy.get("config_json", "{}")
    config = json.loads(config_json) if isinstance(config_json, str) else config_json
    
    # Create analyzer
    analyzer = CustomStrategyAnalyzer(config)
    
    # Run backtest
    engine = RealBacktestEngine()
    candles = await engine.fetch_historical_data(request.symbol, request.timeframe, request.days)
    
    if not candles or len(candles) < 50:
        raise HTTPException(status_code=400, detail="Insufficient historical data")
    
    # Get signals
    signals = analyzer.analyze(candles)
    
    # Get risk params from config
    risk = config.get("risk", {})
    exit_rules = config.get("exit_rules", [])
    
    sl_pct = next((e.get("value", 2.0) for e in exit_rules if e.get("type") == "stop_loss"), 2.0)
    tp_pct = next((e.get("value", 4.0) for e in exit_rules if e.get("type") == "take_profit"), 4.0)
    risk_per_trade = risk.get("position_size_percent", 10.0)
    
    # Simulate trades using engine's internal method
    trades, final_equity, equity_curve = engine._simulate_trades(
        candles=candles,
        signals=signals,
        symbol=request.symbol,
        initial=request.initial_balance,
        risk=risk_per_trade,
        sl=sl_pct,
        tp=tp_pct
    )
    
    # Calculate statistics
    stats = engine._calculate_statistics(trades, equity_curve, request.initial_balance, final_equity)
    
    # Update strategy with backtest results
    db.update_custom_strategy(strategy_id, user_id, performance_stats={
        "last_backtest": {
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "days": request.days,
            "timestamp": int(time.time()),
            **stats
        }
    })
    
    return {
        "success": True,
        "strategy_id": strategy_id,
        "symbol": request.symbol,
        "timeframe": request.timeframe,
        "days": request.days,
        "stats": stats,
        "trades": trades[:50],  # Last 50 trades
        "equity_curve": equity_curve[::max(1, len(equity_curve) // 100)]  # Downsample to ~100 points
    }


# ═══════════════════════════════════════════════════════════════════════════════
# VERSIONING
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/{strategy_id}/versions")
async def get_versions(strategy_id: int, user = Depends(get_current_user)):
    """Get all versions of a strategy"""
    user_id = user.get("user_id") if isinstance(user, dict) else user
    
    # Check access
    strategy = db.get_strategy_by_id(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if strategy["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="No access")
    
    versions = db.get_strategy_versions(strategy_id)
    
    return {
        "strategy_id": strategy_id,
        "current_version": strategy.get("version", "1.0.0"),
        "versions": versions
    }


@router.post("/{strategy_id}/versions/{version_id}/rollback")
async def rollback_version(strategy_id: int, version_id: int, user = Depends(get_current_user)):
    """Rollback strategy to a specific version"""
    user_id = user.get("user_id") if isinstance(user, dict) else user
    
    # Check ownership
    strategy = db.get_strategy_by_id(strategy_id)
    if not strategy or strategy["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Cannot rollback strategy you don't own")
    
    # Perform rollback
    success = db.rollback_to_version(strategy_id, version_id, user_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to rollback")
    
    # Get the version we rolled back to
    version = db.get_strategy_version(version_id)
    
    return {
        "success": True,
        "strategy_id": strategy_id,
        "rolled_back_to": version.get("version") if version else "unknown"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# LIVE TRADING
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/{strategy_id}/start")
async def start_live_trading(strategy_id: int, request: StartLiveRequest, user = Depends(get_current_user)):
    """Start strategy in live trading mode"""
    user_id = user.get("user_id") if isinstance(user, dict) else user
    
    orchestrator = get_orchestrator()
    result = await orchestrator.start_strategy(
        user_id=user_id,
        strategy_id=strategy_id,
        exchange=request.exchange,
        account_type=request.account_type
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/{strategy_id}/stop")
async def stop_live_trading(
    strategy_id: int,
    exchange: str = "bybit",
    account_type: str = "demo",
    close_positions: bool = False,
    user = Depends(get_current_user)
):
    """Stop live trading for a strategy"""
    user_id = user.get("user_id") if isinstance(user, dict) else user
    
    orchestrator = get_orchestrator()
    result = await orchestrator.stop_strategy(
        user_id=user_id,
        strategy_id=strategy_id,
        exchange=exchange,
        account_type=account_type,
        close_positions=close_positions
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/{strategy_id}/pause")
async def pause_live_trading(
    strategy_id: int,
    exchange: str = "bybit",
    account_type: str = "demo",
    user = Depends(get_current_user)
):
    """Pause live trading (keeps positions, stops new signals)"""
    user_id = user.get("user_id") if isinstance(user, dict) else user
    
    orchestrator = get_orchestrator()
    result = await orchestrator.pause_strategy(user_id, strategy_id, exchange, account_type)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/{strategy_id}/resume")
async def resume_live_trading(
    strategy_id: int,
    exchange: str = "bybit",
    account_type: str = "demo",
    user = Depends(get_current_user)
):
    """Resume paused strategy"""
    user_id = user.get("user_id") if isinstance(user, dict) else user
    
    orchestrator = get_orchestrator()
    result = await orchestrator.resume_strategy(user_id, strategy_id, exchange, account_type)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/{strategy_id}/status")
async def get_live_status(
    strategy_id: int,
    exchange: str = "bybit",
    account_type: str = "demo",
    user = Depends(get_current_user)
):
    """Get live trading status for a strategy"""
    user_id = user.get("user_id") if isinstance(user, dict) else user
    
    orchestrator = get_orchestrator()
    status = orchestrator.get_strategy_status(user_id, strategy_id, exchange, account_type)
    
    return {
        "strategy_id": strategy_id,
        "exchange": exchange,
        "account_type": account_type,
        **status
    }
