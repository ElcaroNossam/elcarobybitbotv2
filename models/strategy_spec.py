"""
Unified Strategy Specification (StrategySpec)
Single source of truth for: Builder → Backtest → Runtime → Live Trading

This replaces the duplicate StrategyConfig classes in:
- webapp/services/strategy_builder.py
- webapp/services/strategy_parameters.py
"""
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import uuid
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class IndicatorType(Enum):
    """All 50+ available indicators"""
    # Trend
    SMA = "sma"
    EMA = "ema"
    WMA = "wma"
    HULL_MA = "hull_ma"
    KAMA = "kama"
    SUPERTREND = "supertrend"
    PARABOLIC_SAR = "parabolic_sar"
    VWAP = "vwap"
    ICHIMOKU = "ichimoku"
    ADX = "adx"
    
    # Momentum
    RSI = "rsi"
    STOCHASTIC = "stochastic"
    STOCHASTIC_RSI = "stochastic_rsi"
    MACD = "macd"
    WILLIAMS_R = "williams_r"
    CCI = "cci"
    ROC = "roc"
    MFI = "mfi"
    MOMENTUM = "momentum"
    
    # Volatility
    ATR = "atr"
    BOLLINGER_BANDS = "bb"
    KELTNER_CHANNELS = "keltner"
    DONCHIAN_CHANNELS = "donchian"
    
    # Volume
    OBV = "obv"
    VOLUME_OSCILLATOR = "volume_oscillator"
    ACCUMULATION_DISTRIBUTION = "ad"
    CVD = "cvd"  # Cumulative Volume Delta
    
    # Order Flow
    OPEN_INTEREST = "oi"
    FUNDING_RATE = "funding"
    LIQUIDATIONS = "liquidations"
    LONG_SHORT_RATIO = "lsr"
    
    # Smart Money Concepts
    FVG = "fvg"  # Fair Value Gaps
    ORDER_BLOCKS = "order_blocks"
    LIQUIDITY_ZONES = "liquidity_zones"
    BOS = "bos"  # Break of Structure
    CHOCH = "choch"  # Change of Character
    FIBONACCI = "fibonacci"
    
    # Price
    PRICE_CLOSE = "price_close"
    PRICE_OPEN = "price_open"
    PRICE_HIGH = "price_high"
    PRICE_LOW = "price_low"
    PRICE_HL2 = "price_hl2"
    PRICE_HLC3 = "price_hlc3"
    
    # Support/Resistance
    SUPPORT_RESISTANCE = "sr"
    PIVOT_POINTS = "pivot"


class ConditionOperator(Enum):
    """Comparison operators for conditions"""
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="
    EQ = "=="
    NEQ = "!="
    CROSSES_ABOVE = "crosses_above"
    CROSSES_BELOW = "crosses_below"
    BETWEEN = "between"
    OUTSIDE = "outside"
    IS_RISING = "is_rising"
    IS_FALLING = "is_falling"


class LogicalOperator(Enum):
    """Logical operators for combining conditions"""
    AND = "AND"
    OR = "OR"


class ExitType(Enum):
    """Exit rule types"""
    TAKE_PROFIT = "take_profit"
    STOP_LOSS = "stop_loss"
    TRAILING_STOP = "trailing_stop"
    SIGNAL_EXIT = "signal_exit"
    TIME_EXIT = "time_exit"
    BREAKEVEN = "breakeven"


class TimeFrame(Enum):
    """Trading timeframes"""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"


# ═══════════════════════════════════════════════════════════════════════════════
# INDICATOR CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class IndicatorConfig:
    """Configuration for a single indicator"""
    type: str
    params: Dict[str, Any] = field(default_factory=dict)
    field: Optional[str] = None  # For multi-output indicators (bb.upper, macd.signal)
    timeframe: Optional[str] = None  # Override strategy timeframe
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "params": self.params,
            "field": self.field,
            "timeframe": self.timeframe
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'IndicatorConfig':
        return IndicatorConfig(
            type=data.get("type", ""),
            params=data.get("params", {}),
            field=data.get("field"),
            timeframe=data.get("timeframe")
        )
    
    # Convenient factory methods
    @staticmethod
    def rsi(period: int = 14) -> 'IndicatorConfig':
        return IndicatorConfig(type="rsi", params={"period": period})
    
    @staticmethod
    def ema(period: int = 20) -> 'IndicatorConfig':
        return IndicatorConfig(type="ema", params={"period": period})
    
    @staticmethod
    def bb(period: int = 20, std_dev: float = 2.0, field: str = None) -> 'IndicatorConfig':
        return IndicatorConfig(type="bb", params={"period": period, "std_dev": std_dev}, field=field)
    
    @staticmethod
    def macd(fast: int = 12, slow: int = 26, signal: int = 9, field: str = None) -> 'IndicatorConfig':
        return IndicatorConfig(type="macd", params={"fast": fast, "slow": slow, "signal": signal}, field=field)
    
    @staticmethod
    def atr(period: int = 14) -> 'IndicatorConfig':
        return IndicatorConfig(type="atr", params={"period": period})
    
    @staticmethod
    def price(field: str = "close") -> 'IndicatorConfig':
        return IndicatorConfig(type=f"price_{field}")


# ═══════════════════════════════════════════════════════════════════════════════
# CONDITIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Condition:
    """Single condition: left_indicator OPERATOR right_indicator/value"""
    id: str
    left: IndicatorConfig
    operator: str
    right: Optional[IndicatorConfig] = None  # Compare to another indicator
    value: Optional[float] = None  # Compare to static value
    value2: Optional[float] = None  # For BETWEEN operator (upper bound)
    enabled: bool = True
    description: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "left": self.left.to_dict(),
            "operator": self.operator,
            "right": self.right.to_dict() if self.right else None,
            "value": self.value,
            "value2": self.value2,
            "enabled": self.enabled,
            "description": self.description
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Condition':
        return Condition(
            id=data.get("id", str(uuid.uuid4())[:8]),
            left=IndicatorConfig.from_dict(data["left"]),
            operator=data.get("operator", ">"),
            right=IndicatorConfig.from_dict(data["right"]) if data.get("right") else None,
            value=data.get("value"),
            value2=data.get("value2"),
            enabled=data.get("enabled", True),
            description=data.get("description")
        )
    
    def __str__(self) -> str:
        left_str = f"{self.left.type}"
        if self.left.params:
            left_str += f"({self.left.params.get('period', '')})"
        
        if self.right:
            right_str = f"{self.right.type}"
            if self.right.params:
                right_str += f"({self.right.params.get('period', '')})"
        else:
            right_str = str(self.value)
        
        return f"{left_str} {self.operator} {right_str}"


@dataclass
class ConditionGroup:
    """Group of conditions combined with AND/OR"""
    id: str
    conditions: List[Condition] = field(default_factory=list)
    operator: str = "AND"  # AND or OR
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "conditions": [c.to_dict() for c in self.conditions],
            "operator": self.operator,
            "enabled": self.enabled
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'ConditionGroup':
        return ConditionGroup(
            id=data.get("id", str(uuid.uuid4())[:8]),
            conditions=[Condition.from_dict(c) for c in data.get("conditions", [])],
            operator=data.get("operator", "AND"),
            enabled=data.get("enabled", True)
        )
    
    def add(self, condition: Condition) -> 'ConditionGroup':
        """Fluent API: add condition and return self"""
        self.conditions.append(condition)
        return self


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY & EXIT RULES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EntryRule:
    """Entry rule for LONG or SHORT"""
    direction: str  # "LONG" or "SHORT"
    groups: List[ConditionGroup] = field(default_factory=list)
    group_operator: str = "AND"  # How groups combine
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "direction": self.direction,
            "groups": [g.to_dict() for g in self.groups],
            "group_operator": self.group_operator,
            "enabled": self.enabled
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'EntryRule':
        return EntryRule(
            direction=data.get("direction", "LONG"),
            groups=[ConditionGroup.from_dict(g) for g in data.get("groups", [])],
            group_operator=data.get("group_operator", "AND"),
            enabled=data.get("enabled", True)
        )


@dataclass
class ExitRule:
    """Exit rule (TP, SL, Trailing, Signal-based)"""
    type: str  # take_profit, stop_loss, trailing_stop, signal_exit, time_exit, breakeven
    value: Optional[float] = None  # Percentage for TP/SL/Trailing
    conditions: Optional[ConditionGroup] = None  # For signal_exit
    params: Dict[str, Any] = field(default_factory=dict)  # Additional params
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "value": self.value,
            "conditions": self.conditions.to_dict() if self.conditions else None,
            "params": self.params,
            "enabled": self.enabled
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'ExitRule':
        return ExitRule(
            type=data.get("type", "take_profit"),
            value=data.get("value"),
            conditions=ConditionGroup.from_dict(data["conditions"]) if data.get("conditions") else None,
            params=data.get("params", {}),
            enabled=data.get("enabled", True)
        )
    
    # Convenient factory methods
    @staticmethod
    def take_profit(percent: float) -> 'ExitRule':
        return ExitRule(type="take_profit", value=percent)
    
    @staticmethod
    def stop_loss(percent: float) -> 'ExitRule':
        return ExitRule(type="stop_loss", value=percent)
    
    @staticmethod
    def trailing_stop(percent: float, activation_percent: float = None) -> 'ExitRule':
        params = {}
        if activation_percent:
            params["activation_percent"] = activation_percent
        return ExitRule(type="trailing_stop", value=percent, params=params)
    
    @staticmethod
    def breakeven(activation_percent: float = 1.0, offset: float = 0.1) -> 'ExitRule':
        return ExitRule(type="breakeven", params={"activation_percent": activation_percent, "offset": offset})


# ═══════════════════════════════════════════════════════════════════════════════
# RISK MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RiskManagement:
    """Risk management settings"""
    position_size_percent: float = 10.0  # % of balance per trade
    max_positions: int = 5
    max_daily_trades: int = 20
    max_daily_loss_percent: float = 10.0  # Stop trading if daily loss exceeds
    leverage: int = 10
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict) -> 'RiskManagement':
        return RiskManagement(
            position_size_percent=data.get("position_size_percent", 10.0),
            max_positions=data.get("max_positions", 5),
            max_daily_trades=data.get("max_daily_trades", 20),
            max_daily_loss_percent=data.get("max_daily_loss_percent", 10.0),
            leverage=data.get("leverage", 10)
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FILTERS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Filters:
    """Pre-trade filters"""
    min_volume_usdt: Optional[float] = None  # Minimum 24h volume
    min_volatility: Optional[float] = None  # Minimum ATR %
    max_volatility: Optional[float] = None  # Maximum ATR %
    time_filters: List[str] = field(default_factory=list)  # ["09:00-17:00"]
    excluded_symbols: List[str] = field(default_factory=list)
    required_symbols: List[str] = field(default_factory=list)  # If set, only these
    condition_filter: Optional[ConditionGroup] = None  # Advanced filter conditions
    
    def to_dict(self) -> Dict:
        return {
            "min_volume_usdt": self.min_volume_usdt,
            "min_volatility": self.min_volatility,
            "max_volatility": self.max_volatility,
            "time_filters": self.time_filters,
            "excluded_symbols": self.excluded_symbols,
            "required_symbols": self.required_symbols,
            "condition_filter": self.condition_filter.to_dict() if self.condition_filter else None
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Filters':
        return Filters(
            min_volume_usdt=data.get("min_volume_usdt"),
            min_volatility=data.get("min_volatility"),
            max_volatility=data.get("max_volatility"),
            time_filters=data.get("time_filters", []),
            excluded_symbols=data.get("excluded_symbols", []),
            required_symbols=data.get("required_symbols", []),
            condition_filter=ConditionGroup.from_dict(data["condition_filter"]) if data.get("condition_filter") else None
        )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN STRATEGY SPEC
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class StrategySpec:
    """
    Unified Strategy Specification
    
    Used by:
    - Builder: create/edit strategies
    - Backtest: test on historical data
    - Runtime: execute in live trading
    - AI Agent: generate from text
    """
    # Metadata
    id: Optional[int] = None  # DB id (None for new strategies)
    name: str = "Untitled Strategy"
    description: str = ""
    version: str = "1.0.0"
    author_id: Optional[int] = None
    
    # Entry rules
    long_entry: Optional[EntryRule] = None
    short_entry: Optional[EntryRule] = None
    
    # Exit rules
    exit_rules: List[ExitRule] = field(default_factory=lambda: [
        ExitRule.take_profit(4.0),
        ExitRule.stop_loss(2.0)
    ])
    
    # Risk management
    risk: RiskManagement = field(default_factory=RiskManagement)
    
    # Filters
    filters: Filters = field(default_factory=Filters)
    
    # Timeframes
    primary_timeframe: str = "15m"
    higher_timeframes: List[str] = field(default_factory=lambda: ["1h", "4h"])
    
    # Advanced settings
    pyramiding: int = 1  # Max entries in same direction
    allow_reverse: bool = False  # Close opposite position on signal
    only_one_position_per_symbol: bool = True
    
    # Runtime state (not persisted)
    is_active: bool = False
    last_signal_time: Optional[str] = None
    
    # Timestamps
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author_id": self.author_id,
            "long_entry": self.long_entry.to_dict() if self.long_entry else None,
            "short_entry": self.short_entry.to_dict() if self.short_entry else None,
            "exit_rules": [e.to_dict() for e in self.exit_rules],
            "risk": self.risk.to_dict(),
            "filters": self.filters.to_dict(),
            "primary_timeframe": self.primary_timeframe,
            "higher_timeframes": self.higher_timeframes,
            "pyramiding": self.pyramiding,
            "allow_reverse": self.allow_reverse,
            "only_one_position_per_symbol": self.only_one_position_per_symbol,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'StrategySpec':
        """Create from dictionary"""
        return StrategySpec(
            id=data.get("id"),
            name=data.get("name", "Untitled Strategy"),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            author_id=data.get("author_id"),
            long_entry=EntryRule.from_dict(data["long_entry"]) if data.get("long_entry") else None,
            short_entry=EntryRule.from_dict(data["short_entry"]) if data.get("short_entry") else None,
            exit_rules=[ExitRule.from_dict(e) for e in data.get("exit_rules", [])],
            risk=RiskManagement.from_dict(data.get("risk", {})),
            filters=Filters.from_dict(data.get("filters", {})),
            primary_timeframe=data.get("primary_timeframe", "15m"),
            higher_timeframes=data.get("higher_timeframes", ["1h", "4h"]),
            pyramiding=data.get("pyramiding", 1),
            allow_reverse=data.get("allow_reverse", False),
            only_one_position_per_symbol=data.get("only_one_position_per_symbol", True),
            is_active=data.get("is_active", False),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def to_json(self) -> str:
        """Export as JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @staticmethod
    def from_json(json_str: str) -> 'StrategySpec':
        """Import from JSON string"""
        return StrategySpec.from_dict(json.loads(json_str))
    
    def validate(self) -> tuple:
        """
        Validate strategy configuration
        Returns: (is_valid: bool, errors: List[str])
        """
        errors = []
        
        if not self.name or len(self.name) < 2:
            errors.append("Name must be at least 2 characters")
        
        if not self.long_entry and not self.short_entry:
            errors.append("At least one entry rule (long or short) is required")
        
        if not self.exit_rules:
            errors.append("At least one exit rule is required")
        
        # Validate exit rules
        has_tp = any(e.type == "take_profit" and e.enabled for e in self.exit_rules)
        has_sl = any(e.type == "stop_loss" and e.enabled for e in self.exit_rules)
        
        if not has_sl:
            errors.append("Stop loss is required for risk management")
        
        # Validate risk parameters
        if self.risk.position_size_percent <= 0 or self.risk.position_size_percent > 100:
            errors.append("Position size must be between 0 and 100%")
        
        if self.risk.leverage < 1 or self.risk.leverage > 125:
            errors.append("Leverage must be between 1 and 125")
        
        return len(errors) == 0, errors
    
    def get_tp_sl_percent(self) -> tuple:
        """Get TP and SL percentages from exit rules"""
        tp = next((e.value for e in self.exit_rules if e.type == "take_profit" and e.enabled), None)
        sl = next((e.value for e in self.exit_rules if e.type == "stop_loss" and e.enabled), None)
        return tp, sl
    
    def clone(self, new_name: str = None) -> 'StrategySpec':
        """Create a copy of the strategy"""
        data = self.to_dict()
        data["id"] = None
        data["name"] = new_name or f"{self.name} (Copy)"
        data["version"] = "1.0.0"
        data["created_at"] = None
        data["updated_at"] = None
        return StrategySpec.from_dict(data)


# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGY TEMPLATES (EXAMPLES)
# ═══════════════════════════════════════════════════════════════════════════════

class StrategyTemplates:
    """Pre-built strategy templates"""
    
    @staticmethod
    def rsi_mean_reversion() -> StrategySpec:
        """RSI mean reversion strategy"""
        # Long: RSI < 30 AND price > EMA200
        long_group = ConditionGroup(
            id="long_main",
            conditions=[
                Condition(
                    id="rsi_oversold",
                    left=IndicatorConfig.rsi(14),
                    operator="<",
                    value=30.0,
                    description="RSI oversold"
                ),
                Condition(
                    id="above_ema200",
                    left=IndicatorConfig.price("close"),
                    operator=">",
                    right=IndicatorConfig.ema(200),
                    description="Price above EMA200 (uptrend)"
                )
            ],
            operator="AND"
        )
        
        # Short: RSI > 70 AND price < EMA200
        short_group = ConditionGroup(
            id="short_main",
            conditions=[
                Condition(
                    id="rsi_overbought",
                    left=IndicatorConfig.rsi(14),
                    operator=">",
                    value=70.0,
                    description="RSI overbought"
                ),
                Condition(
                    id="below_ema200",
                    left=IndicatorConfig.price("close"),
                    operator="<",
                    right=IndicatorConfig.ema(200),
                    description="Price below EMA200 (downtrend)"
                )
            ],
            operator="AND"
        )
        
        return StrategySpec(
            name="RSI Mean Reversion",
            description="Classic RSI oversold/overbought strategy with trend filter",
            long_entry=EntryRule(direction="LONG", groups=[long_group]),
            short_entry=EntryRule(direction="SHORT", groups=[short_group]),
            exit_rules=[
                ExitRule.take_profit(4.0),
                ExitRule.stop_loss(2.0),
                ExitRule.trailing_stop(1.5, activation_percent=2.0)
            ],
            risk=RiskManagement(position_size_percent=10.0, leverage=10),
            primary_timeframe="15m"
        )
    
    @staticmethod
    def bollinger_breakout() -> StrategySpec:
        """Bollinger Bands breakout strategy"""
        # Long: Price crosses above upper BB
        long_group = ConditionGroup(
            id="long_main",
            conditions=[
                Condition(
                    id="bb_breakout_up",
                    left=IndicatorConfig.price("close"),
                    operator="crosses_above",
                    right=IndicatorConfig.bb(20, 2.0, field="upper"),
                    description="Price breaks above upper BB"
                )
            ]
        )
        
        # Short: Price crosses below lower BB
        short_group = ConditionGroup(
            id="short_main",
            conditions=[
                Condition(
                    id="bb_breakout_down",
                    left=IndicatorConfig.price("close"),
                    operator="crosses_below",
                    right=IndicatorConfig.bb(20, 2.0, field="lower"),
                    description="Price breaks below lower BB"
                )
            ]
        )
        
        return StrategySpec(
            name="Bollinger Breakout",
            description="Breakout strategy using Bollinger Bands expansion",
            long_entry=EntryRule(direction="LONG", groups=[long_group]),
            short_entry=EntryRule(direction="SHORT", groups=[short_group]),
            exit_rules=[
                ExitRule.take_profit(5.0),
                ExitRule.stop_loss(2.5),
                ExitRule.trailing_stop(2.0)
            ],
            primary_timeframe="1h"
        )
    
    @staticmethod
    def macd_crossover() -> StrategySpec:
        """MACD crossover strategy"""
        # Long: MACD crosses above signal
        long_group = ConditionGroup(
            id="long_main",
            conditions=[
                Condition(
                    id="macd_cross_up",
                    left=IndicatorConfig.macd(field="macd"),
                    operator="crosses_above",
                    right=IndicatorConfig.macd(field="signal"),
                    description="MACD crosses above signal line"
                ),
                Condition(
                    id="macd_positive",
                    left=IndicatorConfig.macd(field="histogram"),
                    operator=">",
                    value=0,
                    description="MACD histogram positive"
                )
            ],
            operator="AND"
        )
        
        # Short: MACD crosses below signal
        short_group = ConditionGroup(
            id="short_main",
            conditions=[
                Condition(
                    id="macd_cross_down",
                    left=IndicatorConfig.macd(field="macd"),
                    operator="crosses_below",
                    right=IndicatorConfig.macd(field="signal"),
                    description="MACD crosses below signal line"
                )
            ]
        )
        
        return StrategySpec(
            name="MACD Crossover",
            description="Classic MACD signal line crossover strategy",
            long_entry=EntryRule(direction="LONG", groups=[long_group]),
            short_entry=EntryRule(direction="SHORT", groups=[short_group]),
            exit_rules=[
                ExitRule.take_profit(6.0),
                ExitRule.stop_loss(3.0)
            ],
            primary_timeframe="4h"
        )
    
    @staticmethod
    def multi_indicator() -> StrategySpec:
        """Complex multi-indicator strategy"""
        # Trend group: EMA alignment
        trend_group = ConditionGroup(
            id="trend",
            conditions=[
                Condition(
                    id="ema_20_50",
                    left=IndicatorConfig.ema(20),
                    operator=">",
                    right=IndicatorConfig.ema(50),
                    description="EMA20 > EMA50"
                ),
                Condition(
                    id="ema_50_200",
                    left=IndicatorConfig.ema(50),
                    operator=">",
                    right=IndicatorConfig.ema(200),
                    description="EMA50 > EMA200"
                )
            ],
            operator="AND"
        )
        
        # Momentum group
        momentum_group = ConditionGroup(
            id="momentum",
            conditions=[
                Condition(
                    id="rsi_bullish",
                    left=IndicatorConfig.rsi(14),
                    operator="between",
                    value=40.0,
                    value2=70.0,
                    description="RSI in bullish zone"
                ),
                Condition(
                    id="macd_bullish",
                    left=IndicatorConfig.macd(field="histogram"),
                    operator=">",
                    value=0,
                    description="MACD histogram positive"
                )
            ],
            operator="AND"
        )
        
        # Volume filter
        volume_filter = ConditionGroup(
            id="volume_filter",
            conditions=[
                Condition(
                    id="volume_spike",
                    left=IndicatorConfig(type="volume"),
                    operator=">",
                    right=IndicatorConfig(type="sma", params={"period": 20, "source": "volume"}),
                    description="Volume above 20 SMA"
                )
            ]
        )
        
        return StrategySpec(
            name="Multi-Indicator Trend",
            description="Complex strategy with EMA alignment, RSI, MACD, and volume confirmation",
            long_entry=EntryRule(
                direction="LONG",
                groups=[trend_group, momentum_group],
                group_operator="AND"
            ),
            exit_rules=[
                ExitRule.take_profit(8.0),
                ExitRule.stop_loss(3.0),
                ExitRule.trailing_stop(2.0, activation_percent=4.0),
                ExitRule.breakeven(activation_percent=2.0)
            ],
            filters=Filters(condition_filter=volume_filter),
            primary_timeframe="1h",
            higher_timeframes=["4h", "1d"]
        )


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def migrate_old_config(old_config: Dict) -> StrategySpec:
    """
    Migrate old strategy configs from strategy_builder.py or strategy_parameters.py
    to the new unified StrategySpec format
    """
    # Detect format by checking for specific keys
    if "base_strategy" in old_config and "indicators" in old_config:
        # strategy_parameters.py format
        return _migrate_from_parameters(old_config)
    elif "long_entry" in old_config and "groups" in str(old_config.get("long_entry", {})):
        # strategy_builder.py format - already compatible
        return StrategySpec.from_dict(old_config)
    else:
        # Simple/unknown format
        return _migrate_from_simple(old_config)


def _migrate_from_parameters(old: Dict) -> StrategySpec:
    """Migrate from strategy_parameters.py format"""
    # Extract risk management
    risk = RiskManagement(
        position_size_percent=old.get("risk_per_trade", 10.0),
        max_positions=old.get("max_positions", 5),
        leverage=old.get("leverage", 10)
    )
    
    # Extract exit rules from risk_management
    risk_mgmt = old.get("risk_management", {})
    exit_rules = [
        ExitRule.take_profit(risk_mgmt.get("tp_percent", old.get("take_profit_percent", 4.0))),
        ExitRule.stop_loss(risk_mgmt.get("sl_percent", old.get("stop_loss_percent", 2.0)))
    ]
    
    # Convert indicators to conditions (simplified)
    conditions = []
    for ind_name, ind_config in old.get("indicators", {}).items():
        if isinstance(ind_config, dict) and ind_config.get("enabled", True):
            params = ind_config.get("params", {})
            # Create basic condition based on indicator type
            if ind_name == "rsi":
                conditions.append(Condition(
                    id=f"{ind_name}_cond",
                    left=IndicatorConfig(type="rsi", params=params),
                    operator="<",
                    value=params.get("oversold", 30),
                    description=f"RSI oversold"
                ))
    
    long_group = ConditionGroup(id="migrated", conditions=conditions, operator="AND") if conditions else None
    
    return StrategySpec(
        name=old.get("name", "Migrated Strategy"),
        description=old.get("description", ""),
        long_entry=EntryRule(direction="LONG", groups=[long_group]) if long_group else None,
        exit_rules=exit_rules,
        risk=risk,
        primary_timeframe=old.get("timeframe", "1h")
    )


def _migrate_from_simple(old: Dict) -> StrategySpec:
    """Migrate from simple config format"""
    return StrategySpec(
        name=old.get("name", "Migrated Strategy"),
        description=old.get("description", ""),
        exit_rules=[
            ExitRule.take_profit(old.get("tp_percent", old.get("take_profit_percent", 4.0))),
            ExitRule.stop_loss(old.get("sl_percent", old.get("stop_loss_percent", 2.0)))
        ],
        risk=RiskManagement(
            position_size_percent=old.get("risk_per_trade", old.get("position_size_percent", 10.0)),
            leverage=old.get("leverage", 10)
        ),
        primary_timeframe=old.get("timeframe", old.get("primary_timeframe", "1h"))
    )
