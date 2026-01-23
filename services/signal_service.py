"""
Signal Service - Parse and process trading signals from Telegram channels
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from enum import Enum
import re

from models.position import PositionSide
from models.exchange_credentials import ExchangeType
from core.exceptions import SignalParseError


class SignalSource(Enum):
    """Signal source identifiers"""
    SCRYPTOMERA = "scryptomera"
    SCALPER = "scalper"
    ELCARO = "elcaro"
    WYCKOFF = "wyckoff"
    MANUAL = "manual"
    UNKNOWN = "unknown"


class SignalType(Enum):
    """Types of trading signals"""
    ENTRY = "entry"
    EXIT = "exit"
    UPDATE_TP = "update_tp"
    UPDATE_SL = "update_sl"
    ADD_POSITION = "add"
    CLOSE_PARTIAL = "partial"


@dataclass
class TradingSignal:
    """Parsed trading signal"""
    source: SignalSource
    signal_type: SignalType
    symbol: str
    side: PositionSide
    entry_price: Optional[float] = None
    take_profits: List[float] = field(default_factory=list)
    stop_loss: Optional[float] = None
    leverage: int = 10
    timeframe: str = "15m"
    confidence: float = 1.0
    raw_text: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_long(self) -> bool:
        return self.side == PositionSide.LONG
    
    @property
    def primary_tp(self) -> Optional[float]:
        return self.take_profits[0] if self.take_profits else None
    
    def tp_percent(self, entry: float) -> Optional[float]:
        if not self.primary_tp or not entry:
            return None
        return abs((self.primary_tp - entry) / entry * 100)
    
    def sl_percent(self, entry: float) -> Optional[float]:
        if not self.stop_loss or not entry:
            return None
        return abs((self.stop_loss - entry) / entry * 100)


class SignalParser:
    """Parse trading signals from various sources"""
    
    # Common patterns
    SYMBOL_PATTERN = re.compile(r"\$?([A-Z]{2,10})(?:USDT|/USDT|\s)", re.IGNORECASE)
    PRICE_PATTERN = re.compile(r"(\d+\.?\d*)")
    LONG_KEYWORDS = ["long", "buy", "лонг", "покупка", "📈", "🟢", "⬆️"]
    SHORT_KEYWORDS = ["short", "sell", "шорт", "продажа", "📉", "🔴", "⬇️"]
    
    def __init__(self):
        self._source_parsers = {
            SignalSource.SCRYPTOMERA: self._parse_scryptomera,
            SignalSource.SCALPER: self._parse_scalper,
            SignalSource.ELCARO: self._parse_elcaro,
            SignalSource.WYCKOFF: self._parse_wyckoff,
        }
    
    def detect_source(self, text: str, channel_id: Optional[int] = None) -> SignalSource:
        """Detect signal source from text or channel ID"""
        text_lower = text.lower()
        
        if "scryptomera" in text_lower or "scrypto" in text_lower:
            return SignalSource.SCRYPTOMERA
        if "scalper" in text_lower or "скальпер" in text_lower:
            return SignalSource.SCALPER
        if "elcaro" in text_lower:
            return SignalSource.ELCARO
        if "wyckoff" in text_lower or "вайкофф" in text_lower:
            return SignalSource.WYCKOFF
        
        return SignalSource.UNKNOWN
    
    def parse(self, text: str, channel_id: Optional[int] = None) -> Optional[TradingSignal]:
        """Parse a trading signal from text"""
        source = self.detect_source(text, channel_id)
        
        if source in self._source_parsers:
            try:
                return self._source_parsers[source](text)
            except Exception as e:
                # Fall back to generic parser
                pass
        
        return self._parse_generic(text, source)
    
    def _detect_side(self, text: str) -> PositionSide:
        """Detect if signal is LONG or SHORT"""
        text_lower = text.lower()
        
        for keyword in self.LONG_KEYWORDS:
            if keyword in text_lower:
                return PositionSide.LONG
        
        for keyword in self.SHORT_KEYWORDS:
            if keyword in text_lower:
                return PositionSide.SHORT
        
        # Default to LONG if not detected
        return PositionSide.LONG
    
    def _extract_symbol(self, text: str) -> Optional[str]:
        """Extract trading symbol from text"""
        # Try standard pattern
        match = self.SYMBOL_PATTERN.search(text)
        if match:
            symbol = match.group(1).upper()
            if not symbol.endswith("USDT"):
                symbol += "USDT"
            return symbol
        
        # Try line-by-line
        for line in text.split("\n"):
            line = line.strip().upper()
            if line and len(line) <= 12 and line.isalpha():
                if not line.endswith("USDT"):
                    line += "USDT"
                return line
        
        return None
    
    def _extract_prices(self, text: str) -> Tuple[List[float], Optional[float]]:
        """Extract TP and SL prices from text"""
        take_profits = []
        stop_loss = None
        
        lines = text.split("\n")
        
        for line in lines:
            line_lower = line.lower()
            prices = self.PRICE_PATTERN.findall(line)
            
            if not prices:
                continue
            
            if any(kw in line_lower for kw in ["tp", "take", "profit", "тейк", "цель"]):
                for p in prices:
                    try:
                        take_profits.append(float(p))
                    except ValueError:
                        pass
            
            elif any(kw in line_lower for kw in ["sl", "stop", "стоп", "лосс"]):
                try:
                    stop_loss = float(prices[0])
                except (ValueError, IndexError):
                    pass
        
        return take_profits, stop_loss
    
    def _extract_leverage(self, text: str) -> int:
        """Extract leverage from text"""
        patterns = [
            r"(\d+)x",
            r"leverage[:\s]*(\d+)",
            r"плечо[:\s]*(\d+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    pass
        
        return 10  # Default leverage
    
    def _parse_generic(self, text: str, source: SignalSource) -> Optional[TradingSignal]:
        """Generic signal parser"""
        symbol = self._extract_symbol(text)
        if not symbol:
            return None
        
        side = self._detect_side(text)
        take_profits, stop_loss = self._extract_prices(text)
        leverage = self._extract_leverage(text)
        
        # Try to extract entry price
        entry_price = None
        entry_patterns = [
            r"entry[:\s]*([\d.]+)",
            r"вход[:\s]*([\d.]+)",
            r"price[:\s]*([\d.]+)",
            r"цена[:\s]*([\d.]+)",
        ]
        
        for pattern in entry_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    entry_price = float(match.group(1))
                    break
                except ValueError:
                    pass
        
        return TradingSignal(
            source=source,
            signal_type=SignalType.ENTRY,
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            take_profits=take_profits,
            stop_loss=stop_loss,
            leverage=leverage,
            raw_text=text
        )
    
    def _parse_scryptomera(self, text: str) -> Optional[TradingSignal]:
        """Parse Scryptomera signal format"""
        signal = self._parse_generic(text, SignalSource.SCRYPTOMERA)
        if signal:
            signal.metadata["parser"] = "scryptomera"
        return signal
    
    def _parse_scalper(self, text: str) -> Optional[TradingSignal]:
        """Parse Scalper signal format"""
        signal = self._parse_generic(text, SignalSource.SCALPER)
        if signal:
            signal.timeframe = "1m"  # Scalper typically uses short timeframes
            signal.metadata["parser"] = "scalper"
        return signal
    
    def _parse_elcaro(self, text: str) -> Optional[TradingSignal]:
        """Parse Lyxen signal format"""
        signal = self._parse_generic(text, SignalSource.ELCARO)
        if signal:
            signal.metadata["parser"] = "elcaro"
        return signal
    
    def _parse_wyckoff(self, text: str) -> Optional[TradingSignal]:
        """Parse Wyckoff signal format"""
        signal = self._parse_generic(text, SignalSource.WYCKOFF)
        if signal:
            signal.metadata["parser"] = "wyckoff"
        return signal


class SignalService:
    """Signal processing service"""
    
    def __init__(self):
        self.parser = SignalParser()
        self._signal_history: List[TradingSignal] = []
    
    def parse_signal(self, text: str, channel_id: Optional[int] = None) -> Optional[TradingSignal]:
        """Parse a trading signal"""
        return self.parser.parse(text, channel_id)
    
    def validate_signal(
        self,
        signal: TradingSignal,
        user_config: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """Validate signal against user configuration"""
        
        # Check if source is enabled
        source_key = f"trade_{signal.source.value}"
        if not user_config.get(source_key, True):
            return False, f"Signal source {signal.source.value} is disabled"
        
        # Check coin group filter
        allowed_coins = user_config.get("coin_group", [])
        if allowed_coins and signal.symbol not in allowed_coins:
            return False, f"Symbol {signal.symbol} not in allowed coins"
        
        # Check blacklist
        blacklist = user_config.get("blacklist", [])
        if signal.symbol in blacklist:
            return False, f"Symbol {signal.symbol} is blacklisted"
        
        return True, None
    
    def should_execute(
        self,
        signal: TradingSignal,
        user_config: Dict[str, Any],
        current_positions: int,
        pending_orders: int
    ) -> Tuple[bool, Optional[str]]:
        """Check if signal should be executed"""
        
        # Validate signal first
        is_valid, error = self.validate_signal(signal, user_config)
        if not is_valid:
            return False, error
        
        # Check position limits
        max_positions = user_config.get("max_positions", 10)
        if current_positions >= max_positions:
            return False, f"Max positions ({max_positions}) reached"
        
        # Check order limits
        max_orders = user_config.get("max_orders", 20)
        if pending_orders >= max_orders:
            return False, f"Max pending orders ({max_orders}) reached"
        
        return True, None
    
    def add_to_history(self, signal: TradingSignal) -> None:
        """Add signal to history"""
        self._signal_history.append(signal)
        
        # Keep only last 1000 signals
        if len(self._signal_history) > 1000:
            self._signal_history = self._signal_history[-1000:]
    
    def get_history(
        self,
        source: Optional[SignalSource] = None,
        symbol: Optional[str] = None,
        limit: int = 100
    ) -> List[TradingSignal]:
        """Get signal history with optional filters"""
        signals = self._signal_history
        
        if source:
            signals = [s for s in signals if s.source == source]
        
        if symbol:
            signals = [s for s in signals if s.symbol == symbol]
        
        return signals[-limit:]
    
    def get_user_active_strategies(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all active strategies for user (built-in + custom)"""
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        import db
        import json
        
        active = []
        config = db.get_user_config(user_id)
        
        # Built-in strategies
        builtin_map = {
            "elcaro": "trade_elcaro",
            "wyckoff": "trade_wyckoff",
            "scalper": "trade_scalper",
            "scryptomera": "trade_scryptomera",
        }
        
        for name, field in builtin_map.items():
            if config.get(field):
                active.append({
                    "type": "builtin",
                    "name": name,
                    "source": SignalSource[name.upper()] if name.upper() in SignalSource.__members__ else SignalSource.MANUAL,
                    "config": db.get_strategy_settings(user_id, name),
                })
        
        # Custom strategies from webapp
        strategy_settings = {}
        if config.get("strategy_settings"):
            try:
                strategy_settings = json.loads(config["strategy_settings"])
            except (json.JSONDecodeError, TypeError):
                pass
        
        for str_id, settings in strategy_settings.items():
            if settings.get("active"):
                custom = db.get_strategy_by_id(int(str_id))
                if custom:
                    active.append({
                        "type": "custom",
                        "id": int(str_id),
                        "name": custom["name"],
                        "source": SignalSource.MANUAL,
                        "config": json.loads(custom.get("config", "{}")) if custom.get("config") else {},
                        "exchange": settings.get("exchange", "bybit"),
                    })
        
        return active
    
    def evaluate_custom_strategy(
        self,
        strategy_config: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Optional[TradingSignal]:
        """Evaluate a custom strategy against market data and generate signal if conditions met"""
        
        entry_conditions = strategy_config.get("entry_conditions", [])
        if not entry_conditions:
            return None
        
        # Evaluate all entry conditions
        conditions_met = 0
        for cond in entry_conditions:
            if self._evaluate_condition(cond, market_data):
                conditions_met += 1
        
        # All conditions must be met
        if conditions_met != len(entry_conditions):
            return None
        
        # Determine direction from conditions
        side = self._determine_side(entry_conditions, market_data)
        
        # Build signal
        signal = TradingSignal(
            source=SignalSource.MANUAL,
            signal_type=SignalType.ENTRY,
            symbol=market_data.get("symbol", "BTCUSDT"),
            side=side,
            entry_price=market_data.get("close"),
            take_profits=[market_data.get("close") * (1 + strategy_config.get("tp_pct", 2) / 100)],
            stop_loss=market_data.get("close") * (1 - strategy_config.get("sl_pct", 1) / 100),
            leverage=strategy_config.get("leverage", 10),
            confidence=conditions_met / len(entry_conditions),
            metadata={"strategy_config": strategy_config},
        )
        
        return signal
    
    def _evaluate_condition(self, condition: Dict, market_data: Dict) -> bool:
        """Evaluate a single condition against market data"""
        indicator = condition.get("indicator")
        cond_type = condition.get("condition")
        value = condition.get("value")
        
        # Get indicator value from market data
        ind_value = market_data.get(indicator)
        if ind_value is None:
            return False
        
        # Evaluate condition
        if cond_type == "above":
            return ind_value > value
        elif cond_type == "below":
            return ind_value < value
        elif cond_type == "equals":
            return abs(ind_value - value) < 0.001
        elif cond_type == "bullish":
            return ind_value > 0 or ind_value == True
        elif cond_type == "bearish":
            return ind_value < 0 or ind_value == False
        elif cond_type == "bullish_cross":
            return market_data.get(f"{indicator}_cross") == "bullish"
        elif cond_type == "bearish_cross":
            return market_data.get(f"{indicator}_cross") == "bearish"
        elif cond_type == "true":
            return bool(ind_value)
        
        return False
    
    def _determine_side(self, conditions: List[Dict], market_data: Dict) -> PositionSide:
        """Determine trade side from conditions"""
        # Check for explicit side conditions
        for cond in conditions:
            if cond.get("condition") in ["bullish", "bullish_cross"]:
                return PositionSide.LONG
            if cond.get("condition") in ["bearish", "bearish_cross"]:
                return PositionSide.SHORT
        
        # Default based on price action
        if market_data.get("close", 0) > market_data.get("open", 0):
            return PositionSide.LONG
        return PositionSide.SHORT


# Singleton instance
signal_service = SignalService()
