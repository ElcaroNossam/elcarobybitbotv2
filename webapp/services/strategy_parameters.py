"""
Strategy Parameters System - Editable Strategy Configurations
Allows users to customize RSI, BB, and all other indicators for each strategy
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import json


class IndicatorType(Enum):
    """Available indicators for strategies"""
    RSI = "rsi"
    BOLLINGER_BANDS = "bb"
    MACD = "macd"
    EMA = "ema"
    SMA = "sma"
    ATR = "atr"
    STOCHASTIC = "stochastic"
    ADX = "adx"
    VOLUME = "volume"
    OI = "oi"  # Open Interest
    FIBONACCI = "fibonacci"
    SUPPORT_RESISTANCE = "support_resistance"
    PIVOT_POINTS = "pivot"
    VWAP = "vwap"
    ICHIMOKU = "ichimoku"


@dataclass
class IndicatorParams:
    """Base parameters for any indicator"""
    type: str
    enabled: bool = True
    weight: float = 1.0  # Weight in signal calculation (0-1)
    params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class RSIParams(IndicatorParams):
    """RSI Indicator Parameters"""
    def __init__(self, period: int = 14, overbought: float = 70, oversold: float = 30, 
                 smoothing: int = 1, enabled: bool = True, weight: float = 1.0):
        super().__init__(
            type=IndicatorType.RSI.value,
            enabled=enabled,
            weight=weight,
            params={
                "period": period,
                "overbought": overbought,
                "oversold": oversold,
                "smoothing": smoothing
            }
        )


@dataclass
class BollingerBandsParams(IndicatorParams):
    """Bollinger Bands Parameters"""
    def __init__(self, period: int = 20, std_dev: float = 2.0, ma_type: str = "sma",
                 enabled: bool = True, weight: float = 1.0):
        super().__init__(
            type=IndicatorType.BOLLINGER_BANDS.value,
            enabled=enabled,
            weight=weight,
            params={
                "period": period,
                "std_dev": std_dev,
                "ma_type": ma_type
            }
        )


@dataclass
class MACDParams(IndicatorParams):
    """MACD Parameters"""
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9,
                 enabled: bool = True, weight: float = 1.0):
        super().__init__(
            type=IndicatorType.MACD.value,
            enabled=enabled,
            weight=weight,
            params={
                "fast_period": fast_period,
                "slow_period": slow_period,
                "signal_period": signal_period
            }
        )


@dataclass
class EMAParams(IndicatorParams):
    """EMA Parameters"""
    def __init__(self, periods: List[int] = None, enabled: bool = True, weight: float = 1.0):
        if periods is None:
            periods = [9, 21, 50, 200]
        super().__init__(
            type=IndicatorType.EMA.value,
            enabled=enabled,
            weight=weight,
            params={"periods": periods}
        )


@dataclass
class VolumeParams(IndicatorParams):
    """Volume Analysis Parameters"""
    def __init__(self, ma_period: int = 20, spike_threshold: float = 2.0,
                 enabled: bool = True, weight: float = 1.0):
        super().__init__(
            type=IndicatorType.VOLUME.value,
            enabled=enabled,
            weight=weight,
            params={
                "ma_period": ma_period,
                "spike_threshold": spike_threshold
            }
        )


@dataclass
class StrategyConfig:
    """Complete strategy configuration with all indicators"""
    name: str
    base_strategy: str  # elcaro, rsibboi, wyckoff, etc.
    description: str = ""
    
    # Core indicators
    indicators: Dict[str, IndicatorParams] = field(default_factory=dict)
    
    # Trading parameters
    risk_per_trade: float = 1.0
    stop_loss_percent: float = 2.0
    take_profit_percent: float = 4.0
    max_positions: int = 3
    
    # Entry/Exit logic
    entry_logic: str = "AND"  # AND, OR, WEIGHTED
    exit_logic: str = "TP_SL"  # TP_SL, SIGNAL, TRAILING
    
    # Additional filters
    min_volume: Optional[float] = None
    min_volatility: Optional[float] = None
    time_filters: List[str] = field(default_factory=list)  # ["09:30-16:00"]
    
    # AI Enhancement
    ai_enhanced: bool = False
    ai_model: Optional[str] = None
    ai_prompt: Optional[str] = None
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['indicators'] = {k: v.to_dict() if hasattr(v, 'to_dict') else v 
                             for k, v in self.indicators.items()}
        return data
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StrategyConfig':
        """Create StrategyConfig from dictionary"""
        indicators = {}
        for key, ind_data in data.get('indicators', {}).items():
            indicators[key] = IndicatorParams(**ind_data) if isinstance(ind_data, dict) else ind_data
        
        return cls(
            name=data['name'],
            base_strategy=data['base_strategy'],
            description=data.get('description', ''),
            indicators=indicators,
            risk_per_trade=data.get('risk_per_trade', 1.0),
            stop_loss_percent=data.get('stop_loss_percent', 2.0),
            take_profit_percent=data.get('take_profit_percent', 4.0),
            max_positions=data.get('max_positions', 3),
            entry_logic=data.get('entry_logic', 'AND'),
            exit_logic=data.get('exit_logic', 'TP_SL'),
            min_volume=data.get('min_volume'),
            min_volatility=data.get('min_volatility'),
            time_filters=data.get('time_filters', []),
            ai_enhanced=data.get('ai_enhanced', False),
            ai_model=data.get('ai_model'),
            ai_prompt=data.get('ai_prompt')
        )


class StrategyTemplates:
    """Predefined strategy templates with default parameters"""
    
    @staticmethod
    def rsibboi() -> StrategyConfig:
        """RSI + Bollinger Bands + Open Interest strategy"""
        return StrategyConfig(
            name="RSI BB OI",
            base_strategy="rsibboi",
            description="Classic RSI + Bollinger Bands strategy with volume confirmation",
            indicators={
                "rsi": RSIParams(period=14, overbought=70, oversold=30),
                "bb": BollingerBandsParams(period=20, std_dev=2.0),
                "volume": VolumeParams(ma_period=20, spike_threshold=1.5)
            },
            risk_per_trade=1.0,
            stop_loss_percent=2.0,
            take_profit_percent=4.0
        )
    
    @staticmethod
    def wyckoff() -> StrategyConfig:
        """Wyckoff + Smart Money Concepts strategy"""
        return StrategyConfig(
            name="Wyckoff SMC",
            base_strategy="wyckoff",
            description="Wyckoff accumulation/distribution with Fibonacci levels",
            indicators={
                "fibonacci": IndicatorParams(
                    type="fibonacci",
                    params={"levels": [0.236, 0.382, 0.5, 0.618, 0.786]}
                ),
                "volume": VolumeParams(ma_period=20, spike_threshold=2.0),
                "support_resistance": IndicatorParams(
                    type="support_resistance",
                    params={"lookback": 50, "min_touches": 3}
                )
            },
            risk_per_trade=1.5,
            stop_loss_percent=3.0,
            take_profit_percent=6.0
        )
    
    @staticmethod
    def elcaro() -> StrategyConfig:
        """Lyxen Main Strategy"""
        return StrategyConfig(
            name="Lyxen",
            base_strategy="elcaro",
            description="Lyxen proprietary signal processing",
            indicators={
                "rsi": RSIParams(period=14, overbought=65, oversold=35),
                "ema": EMAParams(periods=[9, 21, 50]),
                "volume": VolumeParams(ma_period=20, spike_threshold=1.8)
            },
            risk_per_trade=2.0,
            stop_loss_percent=2.5,
            take_profit_percent=5.0
        )
    
    @staticmethod
    def scalper() -> StrategyConfig:
        """Fast scalping strategy"""
        return StrategyConfig(
            name="Scalper",
            base_strategy="scalper",
            description="Quick in-and-out scalping on 1m/5m timeframes",
            indicators={
                "rsi": RSIParams(period=7, overbought=75, oversold=25),
                "bb": BollingerBandsParams(period=10, std_dev=1.5),
                "ema": EMAParams(periods=[5, 13, 21])
            },
            risk_per_trade=0.5,
            stop_loss_percent=0.5,
            take_profit_percent=1.0
        )
    
    @staticmethod
    def mean_reversion() -> StrategyConfig:
        """Mean reversion strategy"""
        return StrategyConfig(
            name="Mean Reversion",
            base_strategy="mean_reversion",
            description="Buy low, sell high within range",
            indicators={
                "bb": BollingerBandsParams(period=20, std_dev=2.5),
                "rsi": RSIParams(period=14, overbought=80, oversold=20),
                "support_resistance": IndicatorParams(
                    type="support_resistance",
                    params={"lookback": 100}
                )
            },
            risk_per_trade=1.0,
            stop_loss_percent=1.5,
            take_profit_percent=3.0
        )
    
    @staticmethod
    def trend_following() -> StrategyConfig:
        """Trend following strategy"""
        return StrategyConfig(
            name="Trend Following",
            base_strategy="trend_following",
            description="Follow the trend with momentum confirmation",
            indicators={
                "ema": EMAParams(periods=[20, 50, 200]),
                "macd": MACDParams(fast_period=12, slow_period=26, signal_period=9),
                "adx": IndicatorParams(
                    type="adx",
                    params={"period": 14, "threshold": 25}
                )
            },
            risk_per_trade=1.5,
            stop_loss_percent=3.0,
            take_profit_percent=8.0
        )
    
    @staticmethod
    def get_all_templates() -> Dict[str, StrategyConfig]:
        """Get all available strategy templates"""
        return {
            "rsibboi": StrategyTemplates.rsibboi(),
            "wyckoff": StrategyTemplates.wyckoff(),
            "elcaro": StrategyTemplates.elcaro(),
            "scalper": StrategyTemplates.scalper(),
            "mean_reversion": StrategyTemplates.mean_reversion(),
            "trend_following": StrategyTemplates.trend_following()
        }


class StrategyParametersManager:
    """Manager for loading, saving, and modifying strategy parameters"""
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
    
    def get_strategy_template(self, strategy_name: str) -> Optional[StrategyConfig]:
        """Get a strategy template by name"""
        templates = StrategyTemplates.get_all_templates()
        return templates.get(strategy_name)
    
    def create_custom_strategy(self, base_strategy: str, modifications: Dict) -> StrategyConfig:
        """Create a custom strategy based on a template with modifications"""
        template = self.get_strategy_template(base_strategy)
        if not template:
            raise ValueError(f"Unknown base strategy: {base_strategy}")
        
        # Apply modifications
        for key, value in modifications.items():
            if key == "indicators":
                for ind_name, ind_params in value.items():
                    if ind_name in template.indicators:
                        # Update existing indicator
                        template.indicators[ind_name].params.update(ind_params)
                    else:
                        # Add new indicator
                        template.indicators[ind_name] = IndicatorParams(
                            type=ind_name,
                            params=ind_params
                        )
            else:
                setattr(template, key, value)
        
        return template
    
    def validate_strategy(self, config: StrategyConfig) -> tuple[bool, List[str]]:
        """Validate strategy configuration"""
        errors = []
        
        if not config.name:
            errors.append("Strategy name is required")
        
        if not config.base_strategy:
            errors.append("Base strategy is required")
        
        if config.risk_per_trade <= 0 or config.risk_per_trade > 100:
            errors.append("Risk per trade must be between 0 and 100")
        
        if config.stop_loss_percent <= 0:
            errors.append("Stop loss must be positive")
        
        if config.take_profit_percent <= 0:
            errors.append("Take profit must be positive")
        
        # Validate indicators
        for ind_name, indicator in config.indicators.items():
            if not indicator.enabled:
                continue
            
            if indicator.type == IndicatorType.RSI.value:
                params = indicator.params
                if params.get("period", 0) < 2:
                    errors.append(f"RSI period must be >= 2")
                if not (0 <= params.get("oversold", 30) <= 100):
                    errors.append(f"RSI oversold must be 0-100")
                if not (0 <= params.get("overbought", 70) <= 100):
                    errors.append(f"RSI overbought must be 0-100")
        
        return len(errors) == 0, errors


if __name__ == "__main__":
    # Example usage
    manager = StrategyParametersManager()
    
    # Get a template
    rsibboi = manager.get_strategy_template("rsibboi")
    print("RSIBBOI Template:")
    print(rsibboi.to_json())
    print()
    
    # Create custom strategy
    custom = manager.create_custom_strategy("rsibboi", {
        "name": "My Custom RSI BB",
        "indicators": {
            "rsi": {"period": 21, "oversold": 25, "overbought": 75},
            "bb": {"period": 30, "std_dev": 2.5}
        },
        "risk_per_trade": 2.0
    })
    print("Custom Strategy:")
    print(custom.to_json())
    print()
    
    # Validate
    valid, errors = manager.validate_strategy(custom)
    print(f"Valid: {valid}")
    if errors:
        print("Errors:", errors)
