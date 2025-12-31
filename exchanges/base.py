"""
Abstract base class for exchange implementations
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class OrderSide(Enum):
    BUY = "Buy"
    SELL = "Sell"


class OrderType(Enum):
    LIMIT = "Limit"
    MARKET = "Market"


class PositionSide(Enum):
    LONG = "Long"
    SHORT = "Short"
    NONE = "None"


@dataclass
class Position:
    symbol: str
    side: PositionSide
    size: float
    entry_price: float
    unrealized_pnl: float
    leverage: float
    margin_mode: str
    liquidation_price: Optional[float] = None
    margin_used: Optional[float] = None
    mark_price: Optional[float] = None  # Current market price for PNL calculation
    stop_loss: Optional[float] = None  # Current stop loss price
    take_profit: Optional[float] = None  # Current take profit price

    @property
    def is_long(self) -> bool:
        return self.side == PositionSide.LONG

    @property
    def is_short(self) -> bool:
        return self.side == PositionSide.SHORT


@dataclass
class Order:
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    size: float
    price: Optional[float]
    filled_size: float = 0
    status: str = "open"
    reduce_only: bool = False
    client_order_id: Optional[str] = None
    created_at: Optional[int] = None


@dataclass
class Balance:
    total_equity: float
    available_balance: float
    margin_used: float
    unrealized_pnl: float
    currency: str = "USDC"
    used_margin: Optional[float] = None  # Alias for margin_used
    
    def __post_init__(self):
        # Set used_margin from margin_used if not provided
        if self.used_margin is None:
            self.used_margin = self.margin_used


@dataclass
class OrderResult:
    success: bool
    order_id: Optional[str] = None
    error: Optional[str] = None
    filled_size: float = 0
    avg_price: Optional[float] = None


class BaseExchange(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def initialize(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def get_balance(self) -> Balance:
        pass

    @abstractmethod
    async def get_positions(self) -> List[Position]:
        pass

    @abstractmethod
    async def get_position(self, symbol: str) -> Optional[Position]:
        pass

    @abstractmethod
    async def place_order(self, symbol: str, side: OrderSide, size: float, price: Optional[float] = None, order_type: OrderType = OrderType.MARKET, reduce_only: bool = False, client_order_id: Optional[str] = None) -> OrderResult:
        pass

    @abstractmethod
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        pass

    @abstractmethod
    async def cancel_all_orders(self, symbol: Optional[str] = None) -> int:
        pass

    @abstractmethod
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        pass

    @abstractmethod
    async def set_leverage(self, symbol: str, leverage: int) -> bool:
        pass

    @abstractmethod
    async def set_take_profit(self, symbol: str, price: float, size: Optional[float] = None) -> OrderResult:
        pass

    @abstractmethod
    async def set_stop_loss(self, symbol: str, price: float, size: Optional[float] = None) -> OrderResult:
        pass

    @abstractmethod
    async def close_position(self, symbol: str, size: Optional[float] = None) -> OrderResult:
        pass

    @abstractmethod
    async def get_price(self, symbol: str) -> Optional[float]:
        pass

    @abstractmethod
    async def get_orderbook(self, symbol: str, depth: int = 10) -> Dict[str, Any]:
        pass

    def normalize_symbol(self, symbol: str) -> str:
        return symbol.upper().replace("USDT", "").replace("USDC", "").replace("PERP", "")
