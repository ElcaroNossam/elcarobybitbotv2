"""
Protected Strategy Backtest & Custom Strategy Builder API

Key Features:
1. Backtest built-in strategies WITHOUT revealing indicator logic
2. Allow users to create custom strategies from public indicators  
3. Beautiful configuration interface for all timeframes and coins
4. Strategy marketplace integration

**SECURITY:** All endpoints require JWT authentication

(c) Lyxen Trading Platform 2024
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import hashlib
import json
import logging

from webapp.api.auth import get_current_user
from core.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/strategy", tags=["strategy"])

# Rate limiter: 5 backtests per hour per user
_backtest_limiter = RateLimiter()
_backtest_limiter.set_limit("backtest", capacity=5, refill_rate=5/3600)


# ======================= ENUMS =======================

class TimeFrame(str, Enum):
    M1 = "1m"
    M3 = "3m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H2 = "2h"
    H4 = "4h"
    H6 = "6h"
    H12 = "12h"
    D1 = "1d"
    W1 = "1w"


class BuiltInStrategy(str, Enum):
    """Built-in strategies with HIDDEN indicator logic"""
    ELCARO = "elcaro"
    WYCKOFF = "wyckoff"
    SCALPER = "scalper"
    SCRYPTOMERA = "scryptomera"
    MEAN_REVERSION = "mean_reversion"
    TREND_FOLLOWING = "trend_following"
    BREAKOUT = "breakout"
    DCA = "dca"
    GRID = "grid"
    MOMENTUM = "momentum"
    VOLATILITY_BREAKOUT = "volatility_breakout"


class ConditionOperator(str, Enum):
    CROSSES_ABOVE = "crosses_above"
    CROSSES_BELOW = "crosses_below"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EQUALS = "equals"
    BETWEEN = "between"
    INCREASING = "increasing"
    DECREASING = "decreasing"


class LogicGate(str, Enum):
    AND = "and"
    OR = "or"


# ======================= REQUEST MODELS =======================

class StrategySettings(BaseModel):
    """Common settings for all strategies"""
    take_profit_percent: float = Field(default=5.0, ge=0.1, le=100, description="TP %")
    stop_loss_percent: float = Field(default=2.0, ge=0.1, le=50, description="SL %")
    position_size_percent: float = Field(default=10.0, ge=1, le=100, description="% баланса на сделку")
    leverage: int = Field(default=10, ge=1, le=125)
    trailing_stop: bool = Field(default=False)
    trailing_stop_percent: Optional[float] = Field(default=1.0, ge=0.1, le=50)
    max_positions: int = Field(default=5, ge=1, le=50)
    

class BacktestRequest(BaseModel):
    """Request for backtesting a BUILT-IN strategy (hidden logic)"""
    strategy: BuiltInStrategy
    symbols: List[str] = Field(..., min_items=1, max_items=50)
    timeframe: TimeFrame
    start_date: Optional[datetime] = None  # Default: 30 days ago
    end_date: Optional[datetime] = None    # Default: now
    initial_balance: float = Field(default=10000, ge=100, le=10000000)
    settings: StrategySettings = Field(default_factory=StrategySettings)
    
    @validator('start_date', pre=True, always=True)
    def set_start_date(cls, v):
        return v or datetime.utcnow() - timedelta(days=30)
    
    @validator('end_date', pre=True, always=True) 
    def set_end_date(cls, v):
        return v or datetime.utcnow()


class IndicatorCondition(BaseModel):
    """Single indicator condition for custom strategy"""
    indicator: str = Field(..., description="Indicator type (e.g. 'rsi', 'macd')")
    params: Dict[str, Any] = Field(default_factory=dict, description="Indicator parameters")
    output_key: Optional[str] = Field(None, description="For multi-output indicators (e.g. 'k' for stochastic)")
    operator: ConditionOperator
    value: Optional[float] = None  # For comparison operators
    value2: Optional[float] = None  # For BETWEEN operator
    compare_indicator: Optional[str] = None  # Compare with another indicator
    compare_params: Optional[Dict[str, Any]] = None


class ConditionGroup(BaseModel):
    """Group of conditions with logic gate"""
    conditions: List[IndicatorCondition]
    logic: LogicGate = LogicGate.AND


class CustomStrategyDefinition(BaseModel):
    """User-defined strategy from public indicators"""
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    
    # Entry conditions
    long_entry: List[ConditionGroup] = Field(default_factory=list)
    short_entry: List[ConditionGroup] = Field(default_factory=list)
    
    # Exit conditions (optional - can use TP/SL only)
    long_exit: List[ConditionGroup] = Field(default_factory=list)
    short_exit: List[ConditionGroup] = Field(default_factory=list)
    
    # Settings
    settings: StrategySettings = Field(default_factory=StrategySettings)
    
    # Filters
    min_volume_usd: Optional[float] = None
    trade_hours: Optional[List[int]] = None  # UTC hours to trade
    avoid_weekends: bool = False


class CustomBacktestRequest(BaseModel):
    """Request for backtesting a USER-DEFINED strategy"""
    strategy: CustomStrategyDefinition
    symbols: List[str] = Field(..., min_items=1, max_items=50)
    timeframe: TimeFrame
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    initial_balance: float = Field(default=10000, ge=100, le=10000000)


class SaveStrategyRequest(BaseModel):
    """Save custom strategy to DB"""
    strategy: CustomStrategyDefinition
    is_public: bool = Field(default=False, description="List on marketplace")
    price_usd: Optional[float] = Field(None, ge=0, le=10000, description="Price if public")
    tags: List[str] = Field(default_factory=list, max_items=10)


# ======================= RESPONSE MODELS =======================

class TradeResult(BaseModel):
    """Single trade result"""
    symbol: str
    side: str  # 'long' or 'short'
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    pnl_percent: float
    exit_reason: str


class SymbolMetrics(BaseModel):
    """Metrics for single symbol"""
    symbol: str
    total_trades: int
    win_rate: float
    profit_factor: float
    total_pnl: float
    total_pnl_percent: float
    max_drawdown: float
    avg_trade_duration: str
    best_trade: float
    worst_trade: float
    sharpe_ratio: float


class BacktestResult(BaseModel):
    """Comprehensive backtest result"""
    # Strategy info (NO indicator details for built-in)
    strategy_name: str
    strategy_type: str  # 'built_in' or 'custom'
    timeframe: str
    
    # Period
    start_date: datetime
    end_date: datetime
    
    # Overall metrics
    initial_balance: float
    final_balance: float
    total_return: float
    total_return_percent: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    max_drawdown: float
    max_drawdown_percent: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    
    # Per-symbol breakdown
    symbol_metrics: List[SymbolMetrics]
    
    # Equity curve (for charting)
    equity_curve: List[Dict[str, Any]]
    
    # Trade log (limited for performance)
    trades: List[TradeResult]
    
    # Monthly returns
    monthly_returns: Dict[str, float]
    
    # Comparison with buy-and-hold
    buy_hold_return: float
    alpha: float  # Strategy return - Buy&Hold return
    
    # Risk metrics
    var_95: float  # Value at Risk 95%
    cvar_95: float  # Conditional VaR


class AvailableIndicator(BaseModel):
    """Info about available indicator for custom strategies"""
    type: str
    name: str
    category: str
    params: Dict[str, Any]
    output: Any
    description: str


class StrategyInfo(BaseModel):
    """Built-in strategy info (NO indicator details)"""
    name: str
    display_name: str
    description: str
    suitable_timeframes: List[str]
    risk_level: str  # 'low', 'medium', 'high'
    expected_trades_per_day: str
    best_market_conditions: List[str]


# ======================= BUILT-IN STRATEGIES METADATA =======================

STRATEGY_METADATA = {
    BuiltInStrategy.ELCARO: {
        "display_name": "Lyxen Pro",
        "description": "Proprietary multi-indicator trend-following system with dynamic risk management",
        "suitable_timeframes": ["15m", "1h", "4h"],
        "risk_level": "medium",
        "expected_trades_per_day": "3-8",
        "best_market_conditions": ["trending", "breakouts"]
    },
    BuiltInStrategy.WYCKOFF: {
        "display_name": "Wyckoff Analysis",
        "description": "Based on Wyckoff methodology - accumulation/distribution phase detection",
        "suitable_timeframes": ["1h", "4h", "1d"],
        "risk_level": "low",
        "expected_trades_per_day": "1-3",
        "best_market_conditions": ["ranging", "accumulation"]
    },
    BuiltInStrategy.SCALPER: {
        "display_name": "Quick Scalper",
        "description": "High-frequency scalping for quick profits on small moves",
        "suitable_timeframes": ["1m", "3m", "5m"],
        "risk_level": "high",
        "expected_trades_per_day": "20-50",
        "best_market_conditions": ["volatile", "liquid"]
    },
    BuiltInStrategy.SCRYPTOMERA: {
        "display_name": "Scryptomera Signals",
        "description": "Crypto news and sentiment-based signal generation",
        "suitable_timeframes": ["5m", "15m", "1h"],
        "risk_level": "medium",
        "expected_trades_per_day": "5-15",
        "best_market_conditions": ["news-driven", "volatile"]
    },
    BuiltInStrategy.MEAN_REVERSION: {
        "display_name": "Mean Reversion",
        "description": "Trades price returning to statistical mean after extremes",
        "suitable_timeframes": ["15m", "1h", "4h"],
        "risk_level": "medium",
        "expected_trades_per_day": "2-5",
        "best_market_conditions": ["ranging", "oversold/overbought"]
    },
    BuiltInStrategy.TREND_FOLLOWING: {
        "display_name": "Trend Following",
        "description": "Classic trend following with trend confirmation filters",
        "suitable_timeframes": ["1h", "4h", "1d"],
        "risk_level": "low",
        "expected_trades_per_day": "1-3",
        "best_market_conditions": ["trending", "momentum"]
    },
    BuiltInStrategy.BREAKOUT: {
        "display_name": "Breakout Hunter",
        "description": "Detects and trades key support/resistance breakouts",
        "suitable_timeframes": ["15m", "1h", "4h"],
        "risk_level": "high",
        "expected_trades_per_day": "3-8",
        "best_market_conditions": ["consolidation breakouts", "volatile"]
    },
    BuiltInStrategy.DCA: {
        "display_name": "Smart DCA",
        "description": "Dollar cost averaging with smart entry timing",
        "suitable_timeframes": ["1h", "4h", "1d"],
        "risk_level": "low",
        "expected_trades_per_day": "1-2",
        "best_market_conditions": ["any", "long-term accumulation"]
    },
    BuiltInStrategy.GRID: {
        "display_name": "Grid Trading",
        "description": "Grid-based trading for ranging markets",
        "suitable_timeframes": ["5m", "15m", "1h"],
        "risk_level": "medium",
        "expected_trades_per_day": "10-30",
        "best_market_conditions": ["ranging", "sideways"]
    },
    BuiltInStrategy.MOMENTUM: {
        "display_name": "Momentum Rider",
        "description": "Captures strong momentum moves with multiple confirmations",
        "suitable_timeframes": ["5m", "15m", "1h"],
        "risk_level": "medium",
        "expected_trades_per_day": "5-12",
        "best_market_conditions": ["trending", "breakouts"]
    },
    BuiltInStrategy.VOLATILITY_BREAKOUT: {
        "display_name": "Volatility Breakout",
        "description": "Trades volatility expansion after low volatility periods",
        "suitable_timeframes": ["15m", "1h", "4h"],
        "risk_level": "high",
        "expected_trades_per_day": "2-6",
        "best_market_conditions": ["post-consolidation", "news events"]
    }
}


# ======================= ENDPOINTS =======================

@router.get("/built-in")
async def get_built_in_strategies() -> List[StrategyInfo]:
    """
    Get list of all built-in strategies with metadata.
    NOTE: Indicator logic is completely HIDDEN.
    """
    result = []
    for strategy, meta in STRATEGY_METADATA.items():
        result.append(StrategyInfo(
            name=strategy.value,
            display_name=meta["display_name"],
            description=meta["description"],
            suitable_timeframes=meta["suitable_timeframes"],
            risk_level=meta["risk_level"],
            expected_trades_per_day=meta["expected_trades_per_day"],
            best_market_conditions=meta["best_market_conditions"]
        ))
    return result


@router.get("/indicators")
async def get_available_indicators() -> Dict[str, List[AvailableIndicator]]:
    """
    Get all available indicators for custom strategy building.
    Grouped by category with full parameter info.
    """
    from webapp.services.indicators import IndicatorCalculator
    
    calc = IndicatorCalculator()
    categories = calc.get_available_indicators()
    
    result = {}
    for category, indicators in categories.items():
        result[category] = []
        for ind_type in indicators:
            info = calc.get_indicator_info(ind_type)
            result[category].append(AvailableIndicator(
                type=ind_type,
                name=info.get('name', ind_type),
                category=info.get('category', category),
                params=info.get('params', {}),
                output=info.get('output', 'single'),
                description=info.get('description', '')
            ))
    
    return result


@router.get("/timeframes")
async def get_available_timeframes() -> List[Dict[str, str]]:
    """Get all available timeframes with display names"""
    return [
        {"value": tf.value, "label": tf.value, "minutes": _tf_to_minutes(tf.value)}
        for tf in TimeFrame
    ]


@router.get("/symbols")
async def get_available_symbols(
    exchange: str = Query("binance", pattern="^(binance|bybit)$"),
    quote: str = Query("USDT", pattern="^(USDT|USDC|BUSD)$")
) -> List[Dict[str, Any]]:
    """Get all tradeable symbols with metadata"""
    # Mock data - in production, fetch from exchange
    popular = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
        "ADAUSDT", "DOGEUSDT", "DOTUSDT", "MATICUSDT", "LTCUSDT",
        "LINKUSDT", "AVAXUSDT", "UNIUSDT", "ATOMUSDT", "NEARUSDT"
    ]
    
    all_symbols = popular + [
        "AAVEUSDT", "ALGOUSDT", "APEUSDT", "APTUSDT", "ARBUSDT",
        "AXSUSDT", "BCHUSDT", "COMPUSDT", "CRVUSDT", "DYDXUSDT",
        "EGLDUSDT", "ETCUSDT", "FILUSDT", "FLOWUSDT", "FTMUSDT",
        "GALAUSDT", "GMXUSDT", "GRTUSDT", "HBARUSDT", "ICPUSDT",
        "IMXUSDT", "INJUSDT", "KAVAUSDT", "KLAYUSDT", "LDOUSDT",
        "LRCUSDT", "MANAUSDT", "MKRUSDT", "NEOUSDT", "OPUSDT",
        "PEPEUSDT", "QNTUSDT", "RNDRUSDT", "RUNEUSDT", "SANDUSDT",
        "SHIBUSDT", "SNXUSDT", "STXUSDT", "SUIUSDT", "SUSHIUSDT",
        "THETAUSDT", "TONUSDT", "TRXUSDT", "VETUSDT", "WLDUSDT",
        "XLMUSDT", "XMRUSDT", "YFIUSDT", "ZECUSDT", "ZILUSDT"
    ]
    
    return [
        {
            "symbol": s,
            "base": s.replace(quote, ""),
            "quote": quote,
            "popular": s in popular,
            "category": _get_crypto_category(s)
        }
        for s in sorted(set(all_symbols))
    ]


@router.post("/backtest/built-in")
async def backtest_built_in_strategy(
    request: BacktestRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
) -> BacktestResult:
    """
    Backtest a BUILT-IN strategy.
    
    ⚠️ IMPORTANT: Strategy indicator logic is completely HIDDEN.
    Only backtest results and metrics are returned.
    
    **REQUIRES:** JWT Authentication
    **RATE LIMIT:** 5 backtests per hour
    """
    user_id = current_user['user_id']
    
    # Rate limiting check
    if not await _backtest_limiter.acquire(user_id, "backtest"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Max 5 backtests per hour.")
    from webapp.services.backtest_engine_pro import ProBacktestEngine
    
    engine = ProBacktestEngine()
    
    # Map strategy name to internal analyzer
    strategy_map = {
        BuiltInStrategy.ELCARO: "elcaro",
        BuiltInStrategy.WYCKOFF: "wyckoff", 
        BuiltInStrategy.SCALPER: "scalper",
        BuiltInStrategy.SCRYPTOMERA: "scryptomera",
        BuiltInStrategy.MEAN_REVERSION: "mean_reversion",
        BuiltInStrategy.TREND_FOLLOWING: "trend_following",
        BuiltInStrategy.BREAKOUT: "breakout",
        BuiltInStrategy.DCA: "dca",
        BuiltInStrategy.GRID: "grid",
        BuiltInStrategy.MOMENTUM: "momentum",
        BuiltInStrategy.VOLATILITY_BREAKOUT: "volatility_breakout"
    }
    
    analyzer_name = strategy_map.get(request.strategy, "trend_following")
    
    # Run backtest
    result = await engine.run_backtest(
        symbols=request.symbols,
        timeframe=request.timeframe.value,
        start_date=request.start_date,
        end_date=request.end_date,
        analyzer_name=analyzer_name,
        initial_balance=request.initial_balance,
        tp_percent=request.settings.take_profit_percent,
        sl_percent=request.settings.stop_loss_percent,
        position_size_percent=request.settings.position_size_percent,
        leverage=request.settings.leverage,
        trailing_stop=request.settings.trailing_stop,
        trailing_percent=request.settings.trailing_stop_percent
    )
    
    # Convert to response format (strip any indicator info)
    return _format_backtest_result(
        result,
        strategy_name=STRATEGY_METADATA[request.strategy]["display_name"],
        strategy_type="built_in",
        timeframe=request.timeframe.value,
        request=request
    )


@router.post("/backtest/custom")
async def backtest_custom_strategy(
    request: CustomBacktestRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
) -> BacktestResult:
    """
    Backtest a USER-DEFINED custom strategy.
    
    Users can create strategies from available public indicators
    and backtest them across any symbols and timeframes.
    
    **REQUIRES:** JWT Authentication
    **RATE LIMIT:** 5 backtests per hour
    """
    user_id = current_user['user_id']
    
    # Rate limiting check
    if not await _backtest_limiter.acquire(user_id, "backtest"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Max 5 backtests per hour.")
    from webapp.services.backtest_engine_pro import ProBacktestEngine
    from webapp.services.indicators import IndicatorCalculator
    
    engine = ProBacktestEngine()
    calculator = IndicatorCalculator()
    
    # Build custom analyzer function from strategy definition
    async def custom_analyzer(candles: List[Dict], config: Dict) -> Dict:
        strategy = request.strategy
        
        # Calculate all required indicators
        indicators = {}
        all_conditions = (
            strategy.long_entry + strategy.short_entry + 
            strategy.long_exit + strategy.short_exit
        )
        
        for group in all_conditions:
            for cond in group.conditions:
                key = f"{cond.indicator}_{hash(json.dumps(cond.params, sort_keys=True))}"
                if key not in indicators:
                    indicators[key] = calculator.calculate(
                        cond.indicator, candles, **cond.params
                    )
        
        # Evaluate conditions for each candle
        signals = []
        
        for i in range(1, len(candles)):
            # Check long entry
            long_signal = _evaluate_condition_groups(
                strategy.long_entry, indicators, i
            )
            
            # Check short entry
            short_signal = _evaluate_condition_groups(
                strategy.short_entry, indicators, i
            )
            
            # Check exits
            long_exit = _evaluate_condition_groups(
                strategy.long_exit, indicators, i
            ) if strategy.long_exit else False
            
            short_exit = _evaluate_condition_groups(
                strategy.short_exit, indicators, i
            ) if strategy.short_exit else False
            
            if long_signal:
                signals.append({
                    "index": i,
                    "action": "long",
                    "price": candles[i]["close"]
                })
            elif short_signal:
                signals.append({
                    "index": i,
                    "action": "short", 
                    "price": candles[i]["close"]
                })
            elif long_exit:
                signals.append({
                    "index": i,
                    "action": "exit_long",
                    "price": candles[i]["close"]
                })
            elif short_exit:
                signals.append({
                    "index": i,
                    "action": "exit_short",
                    "price": candles[i]["close"]
                })
        
        return {"signals": signals}
    
    # Run backtest with custom analyzer
    result = await engine.run_backtest_with_custom_analyzer(
        symbols=request.symbols,
        timeframe=request.timeframe.value,
        start_date=request.start_date,
        end_date=request.end_date,
        analyzer_func=custom_analyzer,
        initial_balance=request.initial_balance,
        tp_percent=request.strategy.settings.take_profit_percent,
        sl_percent=request.strategy.settings.stop_loss_percent,
        position_size_percent=request.strategy.settings.position_size_percent,
        leverage=request.strategy.settings.leverage
    )
    
    return _format_backtest_result(
        result,
        strategy_name=request.strategy.name,
        strategy_type="custom",
        timeframe=request.timeframe.value,
        request=request
    )


@router.post("/save")
async def save_custom_strategy(
    request: SaveStrategyRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Save a custom strategy to database.
    Can optionally list on marketplace for sale.
    
    **REQUIRES:** JWT Authentication
    """
    user_id = current_user['user_id']
    strategy_hash = hashlib.sha256(
        json.dumps(request.strategy.dict(), sort_keys=True).encode()
    ).hexdigest()[:16]
    
    # TODO: Save to database
    result = {
        "strategy_id": strategy_hash,
        "name": request.strategy.name,
        "owner_id": user_id,
        "is_public": request.is_public,
        "price_usd": request.price_usd if request.is_public else None,
        "tags": request.tags,
        "created_at": datetime.utcnow().isoformat(),
        "status": "active" if not request.is_public else "pending_review"
    }
    
    return result


@router.get("/my-strategies")
async def get_user_strategies(
    current_user: dict = Depends(get_current_user)
) -> List[Dict]:
    """
    Get user's saved custom strategies
    
    **REQUIRES:** JWT Authentication
    """
    user_id = current_user['user_id']
    # TODO: Fetch from database
    return []


@router.delete("/delete/{strategy_id}")
async def delete_strategy(
    strategy_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a custom strategy
    
    **REQUIRES:** JWT Authentication
    """
    user_id = current_user['user_id']
    # TODO: Delete from database
    return {"status": "deleted", "strategy_id": strategy_id}


# ======================= HELPER FUNCTIONS =======================

def _tf_to_minutes(tf: str) -> int:
    """Convert timeframe string to minutes"""
    mapping = {
        "1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30,
        "1h": 60, "2h": 120, "4h": 240, "6h": 360, "12h": 720,
        "1d": 1440, "1w": 10080
    }
    return mapping.get(tf, 60)


def _get_crypto_category(symbol: str) -> str:
    """Categorize crypto symbol"""
    base = symbol.replace("USDT", "").replace("USDC", "")
    
    layer1 = ["BTC", "ETH", "SOL", "ADA", "DOT", "AVAX", "NEAR", "APT", "SUI", "ATOM"]
    layer2 = ["MATIC", "ARB", "OP", "IMX", "LRC", "METIS"]
    defi = ["UNI", "AAVE", "COMP", "MKR", "CRV", "SNX", "SUSHI", "YFI", "LDO", "GMX", "DYDX"]
    gaming = ["AXS", "SAND", "MANA", "GALA", "ENJ", "IMX", "FLOW"]
    meme = ["DOGE", "SHIB", "PEPE", "FLOKI", "BONK"]
    ai = ["FET", "AGIX", "RNDR", "OCEAN"]
    
    if base in layer1:
        return "Layer 1"
    elif base in layer2:
        return "Layer 2"
    elif base in defi:
        return "DeFi"
    elif base in gaming:
        return "Gaming/NFT"
    elif base in meme:
        return "Meme"
    elif base in ai:
        return "AI"
    else:
        return "Other"


def _evaluate_condition_groups(
    groups: List[ConditionGroup],
    indicators: Dict[str, Any],
    index: int
) -> bool:
    """Evaluate all condition groups (OR logic between groups)"""
    if not groups:
        return False
    
    for group in groups:
        group_result = _evaluate_single_group(group, indicators, index)
        if group_result:
            return True  # OR between groups
    
    return False


def _evaluate_single_group(
    group: ConditionGroup,
    indicators: Dict[str, Any],
    index: int
) -> bool:
    """Evaluate single condition group (AND/OR within group)"""
    results = []
    
    for cond in group.conditions:
        result = _evaluate_condition(cond, indicators, index)
        results.append(result)
    
    if group.logic == LogicGate.AND:
        return all(results)
    else:
        return any(results)


def _evaluate_condition(
    cond: IndicatorCondition,
    indicators: Dict[str, Any],
    index: int
) -> bool:
    """Evaluate single indicator condition"""
    try:
        key = f"{cond.indicator}_{hash(json.dumps(cond.params, sort_keys=True))}"
        indicator_data = indicators.get(key)
        
        if indicator_data is None:
            return False
        
        # Get value at index
        if isinstance(indicator_data, dict) and cond.output_key:
            values = indicator_data.get(cond.output_key, [])
        elif isinstance(indicator_data, list):
            values = indicator_data
        else:
            return False
        
        if index >= len(values) or index < 1:
            return False
        
        current = values[index]
        previous = values[index - 1]
        
        if current is None or previous is None:
            return False
        
        # Evaluate operator
        if cond.operator == ConditionOperator.GREATER_THAN:
            return current > cond.value
        
        elif cond.operator == ConditionOperator.LESS_THAN:
            return current < cond.value
        
        elif cond.operator == ConditionOperator.EQUALS:
            return abs(current - cond.value) < 0.0001
        
        elif cond.operator == ConditionOperator.BETWEEN:
            return cond.value <= current <= cond.value2
        
        elif cond.operator == ConditionOperator.CROSSES_ABOVE:
            if cond.compare_indicator:
                # Compare with another indicator
                compare_key = f"{cond.compare_indicator}_{hash(json.dumps(cond.compare_params or {}, sort_keys=True))}"
                compare_data = indicators.get(compare_key, [])
                if isinstance(compare_data, dict):
                    compare_data = compare_data.get(cond.output_key, [])
                if index < len(compare_data):
                    compare_current = compare_data[index]
                    compare_previous = compare_data[index - 1]
                    return previous <= compare_previous and current > compare_current
                return False
            else:
                return previous <= cond.value and current > cond.value
        
        elif cond.operator == ConditionOperator.CROSSES_BELOW:
            if cond.compare_indicator:
                compare_key = f"{cond.compare_indicator}_{hash(json.dumps(cond.compare_params or {}, sort_keys=True))}"
                compare_data = indicators.get(compare_key, [])
                if isinstance(compare_data, dict):
                    compare_data = compare_data.get(cond.output_key, [])
                if index < len(compare_data):
                    compare_current = compare_data[index]
                    compare_previous = compare_data[index - 1]
                    return previous >= compare_previous and current < compare_current
                return False
            else:
                return previous >= cond.value and current < cond.value
        
        elif cond.operator == ConditionOperator.INCREASING:
            return current > previous
        
        elif cond.operator == ConditionOperator.DECREASING:
            return current < previous
        
        return False
        
    except Exception as e:
        logger.error(f"Error evaluating condition: {e}")
        return False


def _format_backtest_result(
    result: Dict,
    strategy_name: str,
    strategy_type: str,
    timeframe: str,
    request: Any
) -> BacktestResult:
    """Format backtest result to response model"""
    
    # Extract or calculate metrics
    metrics = result.get("metrics", {})
    trades = result.get("trades", [])
    equity = result.get("equity_curve", [])
    
    # Per-symbol metrics
    symbol_metrics = []
    symbols_data = result.get("per_symbol", {})
    for symbol, data in symbols_data.items():
        symbol_metrics.append(SymbolMetrics(
            symbol=symbol,
            total_trades=data.get("total_trades", 0),
            win_rate=data.get("win_rate", 0),
            profit_factor=data.get("profit_factor", 0),
            total_pnl=data.get("total_pnl", 0),
            total_pnl_percent=data.get("total_pnl_percent", 0),
            max_drawdown=data.get("max_drawdown", 0),
            avg_trade_duration=data.get("avg_duration", "0h"),
            best_trade=data.get("best_trade", 0),
            worst_trade=data.get("worst_trade", 0),
            sharpe_ratio=data.get("sharpe", 0)
        ))
    
    # Format trades
    trade_results = []
    for t in trades[:500]:  # Limit for response size
        trade_results.append(TradeResult(
            symbol=t.get("symbol", ""),
            side=t.get("side", ""),
            entry_time=t.get("entry_time", datetime.utcnow()),
            exit_time=t.get("exit_time", datetime.utcnow()),
            entry_price=t.get("entry_price", 0),
            exit_price=t.get("exit_price", 0),
            size=t.get("size", 0),
            pnl=t.get("pnl", 0),
            pnl_percent=t.get("pnl_percent", 0),
            exit_reason=t.get("exit_reason", "")
        ))
    
    return BacktestResult(
        strategy_name=strategy_name,
        strategy_type=strategy_type,
        timeframe=timeframe,
        start_date=result.get("start_date", datetime.utcnow() - timedelta(days=30)),
        end_date=result.get("end_date", datetime.utcnow()),
        initial_balance=result.get("initial_balance", 10000),
        final_balance=result.get("final_balance", 10000),
        total_return=metrics.get("total_return", 0),
        total_return_percent=metrics.get("total_return_percent", 0),
        total_trades=metrics.get("total_trades", 0),
        winning_trades=metrics.get("winning_trades", 0),
        losing_trades=metrics.get("losing_trades", 0),
        win_rate=metrics.get("win_rate", 0),
        profit_factor=metrics.get("profit_factor", 0),
        max_drawdown=metrics.get("max_drawdown", 0),
        max_drawdown_percent=metrics.get("max_drawdown_percent", 0),
        sharpe_ratio=metrics.get("sharpe_ratio", 0),
        sortino_ratio=metrics.get("sortino_ratio", 0),
        calmar_ratio=metrics.get("calmar_ratio", 0),
        symbol_metrics=symbol_metrics,
        equity_curve=equity[:1000],  # Limit points
        trades=trade_results,
        monthly_returns=result.get("monthly_returns", {}),
        buy_hold_return=metrics.get("buy_hold_return", 0),
        alpha=metrics.get("alpha", 0),
        var_95=metrics.get("var_95", 0),
        cvar_95=metrics.get("cvar_95", 0)
    )
