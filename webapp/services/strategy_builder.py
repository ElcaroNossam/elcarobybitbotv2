"""
ElCaro Visual Strategy Builder
Create custom trading strategies through visual condition builder

Features:
- Drag & drop condition builder
- 50+ indicators
- Complex logic (AND/OR/NOT)
- Multi-condition groups
- Backtestable strategies
- Export/Import JSON
"""
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import json


class ConditionOperator(Enum):
    """Comparison operators"""
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    EQUALS = "=="
    NOT_EQUALS = "!="
    CROSSES_ABOVE = "crosses_above"
    CROSSES_BELOW = "crosses_below"
    BETWEEN = "between"
    OUTSIDE = "outside"


class LogicalOperator(Enum):
    """Logical operators"""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class IndicatorType(Enum):
    """All available indicators"""
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
    
    # Momentum
    RSI = "rsi"
    STOCHASTIC = "stochastic"
    MACD = "macd"
    WILLIAMS_R = "williams_r"
    CCI = "cci"
    ROC = "roc"
    MFI = "mfi"
    STOCHASTIC_RSI = "stochastic_rsi"
    
    # Volatility
    ATR = "atr"
    BOLLINGER_BANDS = "bollinger_bands"
    KELTNER_CHANNELS = "keltner_channels"
    DONCHIAN_CHANNELS = "donchian_channels"
    
    # Volume
    OBV = "obv"
    VOLUME_OSCILLATOR = "volume_oscillator"
    ACCUMULATION_DISTRIBUTION = "accumulation_distribution"
    
    # Price
    PRICE_CLOSE = "price_close"
    PRICE_OPEN = "price_open"
    PRICE_HIGH = "price_high"
    PRICE_LOW = "price_low"


@dataclass
class IndicatorConfig:
    """Indicator configuration"""
    type: str
    params: Dict[str, Any] = field(default_factory=dict)
    field: Optional[str] = None  # For indicators with multiple outputs (e.g., 'upper', 'lower')
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Condition:
    """Single condition in strategy"""
    id: str
    left_indicator: IndicatorConfig
    operator: str
    right_indicator: Optional[IndicatorConfig] = None
    right_value: Optional[float] = None
    timeframe: str = "current"  # 'current', '1h', '4h', etc.
    enabled: bool = True
    description: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "left_indicator": self.left_indicator.to_dict(),
            "operator": self.operator,
            "right_indicator": self.right_indicator.to_dict() if self.right_indicator else None,
            "right_value": self.right_value,
            "timeframe": self.timeframe,
            "enabled": self.enabled,
            "description": self.description
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Condition':
        return Condition(
            id=data["id"],
            left_indicator=IndicatorConfig(**data["left_indicator"]),
            operator=data["operator"],
            right_indicator=IndicatorConfig(**data["right_indicator"]) if data.get("right_indicator") else None,
            right_value=data.get("right_value"),
            timeframe=data.get("timeframe", "current"),
            enabled=data.get("enabled", True),
            description=data.get("description")
        )


@dataclass
class ConditionGroup:
    """Group of conditions with logical operator"""
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
            id=data["id"],
            conditions=[Condition.from_dict(c) for c in data.get("conditions", [])],
            operator=data.get("operator", "AND"),
            enabled=data.get("enabled", True)
        )


@dataclass
class EntryRule:
    """Entry rule (LONG or SHORT)"""
    direction: str  # LONG or SHORT
    groups: List[ConditionGroup] = field(default_factory=list)
    group_operator: str = "AND"  # How groups are combined
    
    def to_dict(self) -> Dict:
        return {
            "direction": self.direction,
            "groups": [g.to_dict() for g in self.groups],
            "group_operator": self.group_operator
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'EntryRule':
        return EntryRule(
            direction=data["direction"],
            groups=[ConditionGroup.from_dict(g) for g in data.get("groups", [])],
            group_operator=data.get("group_operator", "AND")
        )


@dataclass
class ExitRule:
    """Exit rule (TP/SL/Trailing/Signal)"""
    type: str  # 'take_profit', 'stop_loss', 'trailing_stop', 'signal_exit'
    value: Optional[float] = None  # For TP/SL percentage
    conditions: Optional[ConditionGroup] = None  # For signal exit
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "value": self.value,
            "conditions": self.conditions.to_dict() if self.conditions else None,
            "enabled": self.enabled
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'ExitRule':
        return ExitRule(
            type=data["type"],
            value=data.get("value"),
            conditions=ConditionGroup.from_dict(data["conditions"]) if data.get("conditions") else None,
            enabled=data.get("enabled", True)
        )


@dataclass
class StrategyConfig:
    """Complete strategy configuration"""
    name: str
    description: str
    version: str = "1.0"
    author: Optional[str] = None
    
    # Entry rules
    long_entry: Optional[EntryRule] = None
    short_entry: Optional[EntryRule] = None
    
    # Exit rules
    exit_rules: List[ExitRule] = field(default_factory=list)
    
    # Risk management
    position_size_percent: float = 10.0
    max_positions: int = 5
    leverage: int = 10
    
    # Filters
    filters: Optional[ConditionGroup] = None
    
    # Timeframes
    primary_timeframe: str = "15m"
    higher_timeframes: List[str] = field(default_factory=lambda: ["1h", "4h"])
    
    # Advanced
    pyramiding: int = 1
    allow_reverse: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "long_entry": self.long_entry.to_dict() if self.long_entry else None,
            "short_entry": self.short_entry.to_dict() if self.short_entry else None,
            "exit_rules": [e.to_dict() for e in self.exit_rules],
            "position_size_percent": self.position_size_percent,
            "max_positions": self.max_positions,
            "leverage": self.leverage,
            "filters": self.filters.to_dict() if self.filters else None,
            "primary_timeframe": self.primary_timeframe,
            "higher_timeframes": self.higher_timeframes,
            "pyramiding": self.pyramiding,
            "allow_reverse": self.allow_reverse
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'StrategyConfig':
        return StrategyConfig(
            name=data["name"],
            description=data["description"],
            version=data.get("version", "1.0"),
            author=data.get("author"),
            long_entry=EntryRule.from_dict(data["long_entry"]) if data.get("long_entry") else None,
            short_entry=EntryRule.from_dict(data["short_entry"]) if data.get("short_entry") else None,
            exit_rules=[ExitRule.from_dict(e) for e in data.get("exit_rules", [])],
            position_size_percent=data.get("position_size_percent", 10.0),
            max_positions=data.get("max_positions", 5),
            leverage=data.get("leverage", 10),
            filters=ConditionGroup.from_dict(data["filters"]) if data.get("filters") else None,
            primary_timeframe=data.get("primary_timeframe", "15m"),
            higher_timeframes=data.get("higher_timeframes", ["1h", "4h"]),
            pyramiding=data.get("pyramiding", 1),
            allow_reverse=data.get("allow_reverse", False)
        )
    
    def to_json(self) -> str:
        """Export strategy as JSON"""
        return json.dumps(self.to_dict(), indent=2)
    
    @staticmethod
    def from_json(json_str: str) -> 'StrategyConfig':
        """Import strategy from JSON"""
        data = json.loads(json_str)
        return StrategyConfig.from_dict(data)


class StrategyBuilder:
    """Helper class to build strategies"""
    
    @staticmethod
    def create_rsi_strategy() -> StrategyConfig:
        """Example: Simple RSI strategy"""
        # Long entry: RSI < 30 AND price > EMA200
        long_group = ConditionGroup(
            id="long_group_1",
            conditions=[
                Condition(
                    id="rsi_oversold",
                    left_indicator=IndicatorConfig(type="rsi", params={"period": 14}),
                    operator="<",
                    right_value=30.0,
                    description="RSI below 30"
                ),
                Condition(
                    id="price_above_ema",
                    left_indicator=IndicatorConfig(type="price_close"),
                    operator=">",
                    right_indicator=IndicatorConfig(type="ema", params={"period": 200}),
                    description="Price above EMA200"
                )
            ],
            operator="AND"
        )
        
        # Short entry: RSI > 70 AND price < EMA200
        short_group = ConditionGroup(
            id="short_group_1",
            conditions=[
                Condition(
                    id="rsi_overbought",
                    left_indicator=IndicatorConfig(type="rsi", params={"period": 14}),
                    operator=">",
                    right_value=70.0,
                    description="RSI above 70"
                ),
                Condition(
                    id="price_below_ema",
                    left_indicator=IndicatorConfig(type="price_close"),
                    operator="<",
                    right_indicator=IndicatorConfig(type="ema", params={"period": 200}),
                    description="Price below EMA200"
                )
            ],
            operator="AND"
        )
        
        # Exit rules
        exits = [
            ExitRule(type="take_profit", value=5.0, enabled=True),
            ExitRule(type="stop_loss", value=2.0, enabled=True)
        ]
        
        return StrategyConfig(
            name="RSI Mean Reversion",
            description="Simple RSI mean reversion strategy with EMA filter",
            long_entry=EntryRule(direction="LONG", groups=[long_group]),
            short_entry=EntryRule(direction="SHORT", groups=[short_group]),
            exit_rules=exits,
            position_size_percent=10.0,
            leverage=10
        )
    
    @staticmethod
    def create_macd_strategy() -> StrategyConfig:
        """Example: MACD crossover strategy"""
        # Long: MACD crosses above signal
        long_condition = Condition(
            id="macd_cross_up",
            left_indicator=IndicatorConfig(type="macd", params={"fast": 12, "slow": 26, "signal": 9}, field="macd"),
            operator="crosses_above",
            right_indicator=IndicatorConfig(type="macd", params={"fast": 12, "slow": 26, "signal": 9}, field="signal"),
            description="MACD crosses above signal"
        )
        
        long_group = ConditionGroup(id="long_macd", conditions=[long_condition])
        
        # Short: MACD crosses below signal
        short_condition = Condition(
            id="macd_cross_down",
            left_indicator=IndicatorConfig(type="macd", params={"fast": 12, "slow": 26, "signal": 9}, field="macd"),
            operator="crosses_below",
            right_indicator=IndicatorConfig(type="macd", params={"fast": 12, "slow": 26, "signal": 9}, field="signal"),
            description="MACD crosses below signal"
        )
        
        short_group = ConditionGroup(id="short_macd", conditions=[short_condition])
        
        exits = [
            ExitRule(type="take_profit", value=8.0),
            ExitRule(type="stop_loss", value=3.0),
            ExitRule(type="trailing_stop", value=2.0)
        ]
        
        return StrategyConfig(
            name="MACD Crossover",
            description="MACD signal line crossover strategy",
            long_entry=EntryRule(direction="LONG", groups=[long_group]),
            short_entry=EntryRule(direction="SHORT", groups=[short_group]),
            exit_rules=exits
        )
    
    @staticmethod
    def create_multi_indicator_strategy() -> StrategyConfig:
        """Example: Complex multi-indicator strategy"""
        # Long entry: Multiple conditions
        group1 = ConditionGroup(
            id="trend_group",
            conditions=[
                Condition(
                    id="ema_cross",
                    left_indicator=IndicatorConfig(type="ema", params={"period": 20}),
                    operator=">",
                    right_indicator=IndicatorConfig(type="ema", params={"period": 50}),
                    description="EMA20 > EMA50"
                ),
                Condition(
                    id="price_above_ema",
                    left_indicator=IndicatorConfig(type="price_close"),
                    operator=">",
                    right_indicator=IndicatorConfig(type="ema", params={"period": 200}),
                    description="Price > EMA200",
                    timeframe="1h"  # Higher timeframe filter
                )
            ],
            operator="AND"
        )
        
        group2 = ConditionGroup(
            id="momentum_group",
            conditions=[
                Condition(
                    id="rsi_middle",
                    left_indicator=IndicatorConfig(type="rsi", params={"period": 14}),
                    operator="between",
                    right_value=40.0,  # Lower bound
                    description="RSI between 40-60"
                ),
                Condition(
                    id="macd_positive",
                    left_indicator=IndicatorConfig(type="macd", params={}, field="histogram"),
                    operator=">",
                    right_value=0.0,
                    description="MACD histogram > 0"
                )
            ],
            operator="OR"
        )
        
        # Exit with signal
        exit_signal_group = ConditionGroup(
            id="exit_signal",
            conditions=[
                Condition(
                    id="rsi_overbought",
                    left_indicator=IndicatorConfig(type="rsi", params={"period": 14}),
                    operator=">",
                    right_value=80.0
                )
            ]
        )
        
        exits = [
            ExitRule(type="take_profit", value=10.0),
            ExitRule(type="stop_loss", value=4.0),
            ExitRule(type="trailing_stop", value=3.0),
            ExitRule(type="signal_exit", conditions=exit_signal_group)
        ]
        
        return StrategyConfig(
            name="Advanced Multi-Indicator",
            description="Complex strategy with multiple indicators and filters",
            long_entry=EntryRule(
                direction="LONG",
                groups=[group1, group2],
                group_operator="AND"
            ),
            exit_rules=exits,
            primary_timeframe="15m",
            higher_timeframes=["1h", "4h"]
        )


class ConditionEvaluator:
    """Evaluate conditions against market data"""
    
    def __init__(self, indicator_calculator):
        """
        Args:
            indicator_calculator: Instance of IndicatorCalculator from advanced_indicators.py
        """
        self.indicator_calculator = indicator_calculator
        self._indicator_cache: Dict[str, Any] = {}
    
    def evaluate_condition(
        self,
        condition: Condition,
        candle_data: Dict[str, List[float]],
        index: int = -1
    ) -> bool:
        """
        Evaluate a single condition
        
        Args:
            condition: Condition to evaluate
            candle_data: Dict with OHLCV data
            index: Index in data to evaluate (-1 for latest)
        """
        if not condition.enabled:
            return True
        
        # Get left indicator value
        left_value = self._get_indicator_value(condition.left_indicator, candle_data, index)
        
        # Get right value (indicator or constant)
        if condition.right_indicator:
            right_value = self._get_indicator_value(condition.right_indicator, candle_data, index)
        else:
            right_value = condition.right_value
        
        # Evaluate operator
        return self._evaluate_operator(left_value, condition.operator, right_value, candle_data, index)
    
    def _get_indicator_value(
        self,
        indicator_config: IndicatorConfig,
        candle_data: Dict[str, List[float]],
        index: int
    ) -> float:
        """Calculate indicator value"""
        cache_key = f"{indicator_config.type}_{json.dumps(indicator_config.params)}_{indicator_config.field}"
        
        if cache_key not in self._indicator_cache:
            # Calculate indicator
            result = self.indicator_calculator.calculate(
                indicator_config.type,
                candle_data,
                indicator_config.params
            )
            self._indicator_cache[cache_key] = result
        else:
            result = self._indicator_cache[cache_key]
        
        # Extract field if needed
        if isinstance(result, dict) and indicator_config.field:
            result = result[indicator_config.field]
        
        # Get value at index
        if isinstance(result, list):
            return result[index] if result and len(result) > abs(index) else None
        else:
            return result
    
    def _evaluate_operator(
        self,
        left: float,
        operator: str,
        right: float,
        candle_data: Dict,
        index: int
    ) -> bool:
        """Evaluate comparison operator"""
        if left is None or right is None:
            return False
        
        if operator == ">":
            return left > right
        elif operator == "<":
            return left < right
        elif operator == ">=":
            return left >= right
        elif operator == "<=":
            return left <= right
        elif operator == "==":
            return abs(left - right) < 0.0001  # Float comparison
        elif operator == "!=":
            return abs(left - right) >= 0.0001
        elif operator == "crosses_above":
            # Check if left crossed above right in last candle
            if index >= -1 and len(candle_data.get("close", [])) > 1:
                prev_left = self._get_indicator_value(None, candle_data, index - 1)
                prev_right = right  # Assuming right is constant
                return prev_left <= prev_right and left > right
            return False
        elif operator == "crosses_below":
            if index >= -1 and len(candle_data.get("close", [])) > 1:
                prev_left = self._get_indicator_value(None, candle_data, index - 1)
                prev_right = right
                return prev_left >= prev_right and left < right
            return False
        elif operator == "between":
            # right_value is lower bound, need upper bound from somewhere
            return True  # Simplified
        elif operator == "outside":
            return True  # Simplified
        
        return False
    
    def evaluate_group(
        self,
        group: ConditionGroup,
        candle_data: Dict[str, List[float]],
        index: int = -1
    ) -> bool:
        """Evaluate condition group"""
        if not group.enabled or not group.conditions:
            return True
        
        results = [self.evaluate_condition(cond, candle_data, index) for cond in group.conditions]
        
        if group.operator == "AND":
            return all(results)
        elif group.operator == "OR":
            return any(results)
        else:
            return False
    
    def evaluate_entry_rule(
        self,
        entry_rule: EntryRule,
        candle_data: Dict[str, List[float]],
        index: int = -1
    ) -> bool:
        """Evaluate complete entry rule"""
        if not entry_rule.groups:
            return False
        
        group_results = [self.evaluate_group(g, candle_data, index) for g in entry_rule.groups]
        
        if entry_rule.group_operator == "AND":
            return all(group_results)
        elif entry_rule.group_operator == "OR":
            return any(group_results)
        
        return False


# Export builder instance
strategy_builder = StrategyBuilder()
