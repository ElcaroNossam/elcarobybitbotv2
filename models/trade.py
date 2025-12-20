"""
Trade models
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List


class TradeType(Enum):
    """Type of trade"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT = "take_profit"
    STOP_LOSS = "stop_loss"
    TRAILING_STOP = "trailing_stop"


class TradeStatus(Enum):
    """Trade status"""
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partial"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CLOSED = "closed"


class TradeSide(Enum):
    """Trade side"""
    BUY = "Buy"
    SELL = "Sell"


@dataclass
class Trade:
    """Trade/order model"""
    id: Optional[str] = None
    order_id: Optional[str] = None
    order_link_id: Optional[str] = None
    user_id: int = 0
    symbol: str = ""
    exchange: str = "bybit"
    side: TradeSide = TradeSide.BUY
    type: TradeType = TradeType.MARKET
    status: TradeStatus = TradeStatus.PENDING
    qty: float = 0.0
    filled_qty: float = 0.0
    remaining_qty: float = 0.0
    price: float = 0.0
    avg_price: float = 0.0
    trigger_price: Optional[float] = None
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    leverage: int = 1
    margin_mode: str = "cross"
    reduce_only: bool = False
    close_on_trigger: bool = False
    pnl: float = 0.0
    pnl_percent: float = 0.0
    fee: float = 0.0
    signal_source: Optional[str] = None
    signal_text: Optional[str] = None
    comment: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    filled_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    @property
    def is_buy(self) -> bool:
        return self.side == TradeSide.BUY
    
    @property
    def is_sell(self) -> bool:
        return self.side == TradeSide.SELL
    
    @property
    def is_market(self) -> bool:
        return self.type == TradeType.MARKET
    
    @property
    def is_limit(self) -> bool:
        return self.type == TradeType.LIMIT
    
    @property
    def is_open(self) -> bool:
        return self.status in (TradeStatus.OPEN, TradeStatus.PARTIALLY_FILLED, TradeStatus.PENDING)
    
    @property
    def is_filled(self) -> bool:
        return self.status == TradeStatus.FILLED
    
    @property
    def is_closed(self) -> bool:
        return self.status in (TradeStatus.CLOSED, TradeStatus.CANCELLED, TradeStatus.REJECTED, TradeStatus.EXPIRED)
    
    @property
    def fill_percent(self) -> float:
        if self.qty == 0:
            return 0.0
        return (self.filled_qty / self.qty) * 100
    
    @property
    def trade_value(self) -> float:
        return self.qty * (self.avg_price or self.price)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "order_link_id": self.order_link_id,
            "user_id": self.user_id,
            "symbol": self.symbol,
            "exchange": self.exchange,
            "side": self.side.value,
            "type": self.type.value,
            "status": self.status.value,
            "qty": self.qty,
            "filled_qty": self.filled_qty,
            "remaining_qty": self.remaining_qty,
            "price": self.price,
            "avg_price": self.avg_price,
            "trigger_price": self.trigger_price,
            "take_profit": self.take_profit,
            "stop_loss": self.stop_loss,
            "leverage": self.leverage,
            "pnl": self.pnl,
            "pnl_percent": self.pnl_percent,
            "fee": self.fee,
            "signal_source": self.signal_source,
            "is_open": self.is_open,
            "is_filled": self.is_filled,
            "fill_percent": self.fill_percent,
            "trade_value": self.trade_value,
        }
    
    @classmethod
    def from_bybit_order(cls, data: Dict[str, Any], user_id: int = 0) -> "Trade":
        status_map = {
            "New": TradeStatus.OPEN,
            "PartiallyFilled": TradeStatus.PARTIALLY_FILLED,
            "Filled": TradeStatus.FILLED,
            "Cancelled": TradeStatus.CANCELLED,
            "Rejected": TradeStatus.REJECTED,
            "Expired": TradeStatus.EXPIRED,
        }
        type_map = {
            "Market": TradeType.MARKET,
            "Limit": TradeType.LIMIT,
            "Stop": TradeType.STOP,
        }
        return cls(
            order_id=data.get("orderId"),
            order_link_id=data.get("orderLinkId"),
            user_id=user_id,
            symbol=data.get("symbol", ""),
            exchange="bybit",
            side=TradeSide.BUY if data.get("side") == "Buy" else TradeSide.SELL,
            type=type_map.get(data.get("orderType"), TradeType.MARKET),
            status=status_map.get(data.get("orderStatus"), TradeStatus.PENDING),
            qty=float(data.get("qty", 0)),
            filled_qty=float(data.get("cumExecQty", 0)),
            remaining_qty=float(data.get("leavesQty", 0)),
            price=float(data.get("price", 0)),
            avg_price=float(data.get("avgPrice", 0)),
            trigger_price=float(data["triggerPrice"]) if data.get("triggerPrice") else None,
            take_profit=float(data["takeProfit"]) if data.get("takeProfit") else None,
            stop_loss=float(data["stopLoss"]) if data.get("stopLoss") else None,
            reduce_only=data.get("reduceOnly", False),
            close_on_trigger=data.get("closeOnTrigger", False),
            fee=float(data.get("cumExecFee", 0)),
        )
