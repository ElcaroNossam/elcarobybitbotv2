"""
Position models
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class PositionSide(Enum):
    """Position side/direction"""
    LONG = "Buy"
    SHORT = "Sell"
    
    @classmethod
    def from_string(cls, value: str) -> "PositionSide":
        value = value.upper()
        if value in ("BUY", "LONG", "L"):
            return cls.LONG
        elif value in ("SELL", "SHORT", "S"):
            return cls.SHORT
        raise ValueError(f"Invalid position side: {value}")


@dataclass
class Position:
    """Trading position model"""
    id: Optional[str] = None
    user_id: int = 0
    symbol: str = ""
    exchange: str = "bybit"
    side: PositionSide = PositionSide.LONG
    size: float = 0.0
    entry_price: float = 0.0
    leverage: int = 1
    margin_mode: str = "cross"
    mark_price: float = 0.0
    liquidation_price: float = 0.0
    margin: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_percent: float = 0.0
    realized_pnl: float = 0.0
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    trailing_stop: Optional[float] = None
    signal_source: Optional[str] = None
    order_link_id: Optional[str] = None
    opened_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_long(self) -> bool:
        return self.side == PositionSide.LONG
    
    @property
    def is_short(self) -> bool:
        return self.side == PositionSide.SHORT
    
    @property
    def position_value(self) -> float:
        return self.size * self.entry_price
    
    @property
    def current_value(self) -> float:
        return self.size * self.mark_price
    
    @property
    def pnl_percent(self) -> float:
        if self.position_value == 0:
            return 0.0
        return (self.unrealized_pnl / self.margin) * 100 if self.margin else 0.0
    
    def calculate_pnl(self, current_price: float) -> float:
        if self.is_long:
            return (current_price - self.entry_price) * self.size
        else:
            return (self.entry_price - current_price) * self.size
    
    def should_take_profit(self, current_price: float) -> bool:
        if not self.take_profit:
            return False
        if self.is_long:
            return current_price >= self.take_profit
        else:
            return current_price <= self.take_profit
    
    def should_stop_loss(self, current_price: float) -> bool:
        if not self.stop_loss:
            return False
        if self.is_long:
            return current_price <= self.stop_loss
        else:
            return current_price >= self.stop_loss
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "symbol": self.symbol,
            "exchange": self.exchange,
            "side": self.side.value,
            "size": self.size,
            "entry_price": self.entry_price,
            "leverage": self.leverage,
            "margin_mode": self.margin_mode,
            "mark_price": self.mark_price,
            "liquidation_price": self.liquidation_price,
            "margin": self.margin,
            "unrealized_pnl": self.unrealized_pnl,
            "unrealized_pnl_percent": self.pnl_percent,
            "realized_pnl": self.realized_pnl,
            "take_profit": self.take_profit,
            "stop_loss": self.stop_loss,
            "trailing_stop": self.trailing_stop,
            "signal_source": self.signal_source,
            "order_link_id": self.order_link_id,
            "opened_at": self.opened_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_long": self.is_long,
            "position_value": self.position_value,
        }
    
    @classmethod
    def from_bybit(cls, data: Dict[str, Any], user_id: int = 0) -> "Position":
        return cls(
            id=data.get("positionIdx"),
            user_id=user_id,
            symbol=data.get("symbol", ""),
            exchange="bybit",
            side=PositionSide.from_string(data.get("side", "Buy")),
            size=float(data.get("size", 0)),
            entry_price=float(data.get("avgPrice", 0)),
            leverage=int(float(data.get("leverage", 1))),
            margin_mode="isolated" if data.get("tradeMode") == 1 else "cross",
            mark_price=float(data.get("markPrice", 0)),
            liquidation_price=float(data.get("liqPrice", 0)) if data.get("liqPrice") else 0,
            margin=float(data.get("positionMM", 0)),
            unrealized_pnl=float(data.get("unrealisedPnl", 0)),
            realized_pnl=float(data.get("cumRealisedPnl", 0)),
            take_profit=float(data["takeProfit"]) if data.get("takeProfit") else None,
            stop_loss=float(data["stopLoss"]) if data.get("stopLoss") else None,
            trailing_stop=float(data["trailingStop"]) if data.get("trailingStop") else None,
        )
    
    @classmethod
    def from_hyperliquid(cls, data: Dict[str, Any], user_id: int = 0) -> "Position":
        position = data.get("position", data)
        size = float(position.get("szi", 0))
        side = PositionSide.LONG if size > 0 else PositionSide.SHORT
        return cls(
            user_id=user_id,
            symbol=position.get("coin", "") + "USDT",
            exchange="hyperliquid",
            side=side,
            size=abs(size),
            entry_price=float(position.get("entryPx", 0)),
            leverage=int(float(position.get("leverage", {}).get("value", 1))),
            mark_price=float(position.get("markPx", 0)),
            liquidation_price=float(position.get("liquidationPx", 0)) if position.get("liquidationPx") else 0,
            margin=float(position.get("marginUsed", 0)),
            unrealized_pnl=float(position.get("unrealizedPnl", 0)),
        )
