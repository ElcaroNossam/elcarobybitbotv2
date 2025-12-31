"""
Unified Data Models - Single Source of Truth

These models are used across ALL layers:
- bot.py (Telegram handlers)
- services/ (Business logic)
- core/ (Infrastructure)
- exchanges/ (Exchange API wrappers)
- webapp/ (FastAPI endpoints)

ALL exchange API responses MUST be converted to these standardized models.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from decimal import Decimal


# ============================================================================
# ENUMS - Standard values across all exchanges
# ============================================================================

class OrderSide(str, Enum):
    """Order/Position side - standardized to Bybit format"""
    BUY = "Buy"
    SELL = "Sell"
    
    @classmethod
    def from_string(cls, value: str) -> "OrderSide":
        """Convert various formats to standard OrderSide"""
        value = str(value).upper()
        if value in ("BUY", "LONG", "L", "B"):
            return cls.BUY
        elif value in ("SELL", "SHORT", "S"):
            return cls.SELL
        raise ValueError(f"Invalid order side: {value}")


class PositionSide(str, Enum):
    """Position direction"""
    LONG = "Buy"
    SHORT = "Sell"
    NONE = "None"
    
    @classmethod
    def from_string(cls, value: str) -> "PositionSide":
        value = str(value).upper()
        if value in ("BUY", "LONG", "L"):
            return cls.LONG
        elif value in ("SELL", "SHORT", "S"):
            return cls.SHORT
        return cls.NONE


class OrderType(str, Enum):
    """Order type"""
    MARKET = "Market"
    LIMIT = "Limit"
    
    @classmethod
    def from_string(cls, value: str) -> "OrderType":
        value = str(value).upper()
        if value in ("MARKET", "M"):
            return cls.MARKET
        elif value in ("LIMIT", "L"):
            return cls.LIMIT
        raise ValueError(f"Invalid order type: {value}")


class OrderStatus(str, Enum):
    """Order status"""
    NEW = "New"
    FILLED = "Filled"
    PARTIALLY_FILLED = "PartiallyFilled"
    CANCELLED = "Cancelled"
    REJECTED = "Rejected"
    UNTRIGGERED = "Untriggered"


# ============================================================================
# CORE DATA MODELS
# ============================================================================

@dataclass
class Position:
    """
    Unified Position Model
    
    Used by:
    - Bybit positions
    - HyperLiquid positions
    - WebApp display
    - Bot position tracking
    """
    symbol: str
    side: PositionSide
    size: float
    entry_price: float
    mark_price: float = 0.0
    unrealized_pnl: float = 0.0
    leverage: int = 1
    margin_mode: str = "cross"
    margin_used: float = 0.0
    liquidation_price: Optional[float] = None
    
    # Optional fields
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    trailing_stop: Optional[float] = None
    
    # Metadata
    exchange: str = "bybit"
    user_id: Optional[int] = None
    strategy: Optional[str] = None
    opened_at: Optional[datetime] = None
    
    @property
    def is_long(self) -> bool:
        return self.side == PositionSide.LONG
    
    @property
    def is_short(self) -> bool:
        return self.side == PositionSide.SHORT
    
    @property
    def position_value(self) -> float:
        """Total position value in quote currency"""
        return self.size * self.entry_price
    
    @property
    def current_value(self) -> float:
        """Current position value at mark price"""
        return self.size * self.mark_price
    
    @property
    def pnl_percent(self) -> float:
        """PNL percentage based on margin used"""
        if self.margin_used == 0:
            return 0.0
        return (self.unrealized_pnl / self.margin_used) * 100
    
    @property
    def roi_percent(self) -> float:
        """ROI percentage on entry value"""
        if self.position_value == 0:
            return 0.0
        return (self.unrealized_pnl / self.position_value) * 100
    
    @classmethod
    def from_bybit(cls, data: Dict[str, Any]) -> 'Position':
        """Convert Bybit API response to Position"""
        # Support both snake_case (from exchange_client) and camelCase (from raw Bybit API)
        entry_price = float(data.get('entry_price') or data.get('avgPrice', 0))
        mark_price_raw = data.get('mark_price') or data.get('markPrice')
        mark_price = float(mark_price_raw) if mark_price_raw else entry_price
        
        # Handle stop_loss - support both formats
        sl_raw = data.get('stop_loss') or data.get('stopLoss')
        stop_loss = float(sl_raw) if sl_raw else None
        
        # Handle take_profit - support both formats
        tp_raw = data.get('take_profit') or data.get('takeProfit')
        take_profit = float(tp_raw) if tp_raw else None
        
        return cls(
            symbol=data['symbol'],
            side=PositionSide.from_string(data['side']),
            size=float(data['size']),
            entry_price=entry_price,
            mark_price=mark_price,
            unrealized_pnl=float(data.get('unrealized_pnl') or data.get('unrealisedPnl', 0)),
            leverage=int(data.get('leverage', 1)),
            margin_mode=data.get('tradeMode', 'cross').lower(),
            margin_used=float(data.get('positionIM', 0)),
            liquidation_price=float(data.get('liqPrice') or data.get('liquidation_price', 0)) if data.get('liqPrice') or data.get('liquidation_price') else None,
            take_profit=take_profit,
            stop_loss=stop_loss,
            exchange='bybit'
        )
    
    @classmethod
    def from_hyperliquid(cls, data: Dict[str, Any]) -> 'Position':
        """Convert HyperLiquid API response to Position"""
        position_data = data.get('position', {})
        coin = position_data.get('coin', '')
        szi = float(position_data.get('szi', 0))
        
        return cls(
            symbol=f"{coin}USD",  # HL format
            side=PositionSide.LONG if szi > 0 else PositionSide.SHORT if szi < 0 else PositionSide.NONE,
            size=abs(szi),
            entry_price=float(position_data.get('entryPx', 0)),
            mark_price=float(data.get('markPx', position_data.get('entryPx', 0))),
            unrealized_pnl=float(position_data.get('unrealizedPnl', 0)),
            leverage=int(position_data.get('leverage', {}).get('value', 1)),
            margin_mode='cross',  # HL default
            margin_used=float(position_data.get('marginUsed', 0)),
            liquidation_price=float(position_data.get('liquidationPx')) if position_data.get('liquidationPx') else None,
            exchange='hyperliquid'
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization"""
        # Handle side - could be enum or string
        side_value = self.side.value if hasattr(self.side, 'value') else str(self.side)
        return {
            'symbol': self.symbol,
            'side': side_value,
            'size': self.size,
            'entry_price': self.entry_price,
            'mark_price': self.mark_price,
            'unrealized_pnl': self.unrealized_pnl,
            'leverage': self.leverage,
            'margin_mode': self.margin_mode,
            'margin_used': self.margin_used,
            'liquidation_price': self.liquidation_price,
            'take_profit': self.take_profit,
            'stop_loss': self.stop_loss,
            'pnl_percent': self.pnl_percent,
            'roi_percent': self.roi_percent,
            'exchange': self.exchange,
        }


@dataclass
class Order:
    """
    Unified Order Model
    
    Represents an order across all exchanges
    """
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    size: float
    price: Optional[float] = None
    filled_size: float = 0.0
    avg_fill_price: Optional[float] = None
    status: OrderStatus = OrderStatus.NEW
    reduce_only: bool = False
    
    # Optional fields
    client_order_id: Optional[str] = None
    leverage: Optional[int] = None
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    
    # Metadata
    exchange: str = "bybit"
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def is_filled(self) -> bool:
        return self.status == OrderStatus.FILLED
    
    @property
    def is_open(self) -> bool:
        return self.status in (OrderStatus.NEW, OrderStatus.PARTIALLY_FILLED, OrderStatus.UNTRIGGERED)
    
    @property
    def fill_percent(self) -> float:
        if self.size == 0:
            return 0.0
        return (self.filled_size / self.size) * 100
    
    @classmethod
    def from_bybit(cls, data: Dict[str, Any]) -> 'Order':
        """Convert Bybit API response to Order"""
        return cls(
            order_id=data['orderId'],
            symbol=data['symbol'],
            side=OrderSide.from_string(data['side']),
            order_type=OrderType.from_string(data['orderType']),
            size=float(data['qty']),
            price=float(data.get('price', 0)) if data.get('price') else None,
            filled_size=float(data.get('cumExecQty', 0)),
            avg_fill_price=float(data.get('avgPrice', 0)) if data.get('avgPrice') else None,
            status=OrderStatus(data.get('orderStatus', 'New')),
            reduce_only=data.get('reduceOnly', False),
            client_order_id=data.get('orderLinkId'),
            take_profit=float(data.get('takeProfit', 0)) if data.get('takeProfit') else None,
            stop_loss=float(data.get('stopLoss', 0)) if data.get('stopLoss') else None,
            exchange='bybit',
            created_at=datetime.fromtimestamp(int(data.get('createdTime', 0)) / 1000) if data.get('createdTime') else None
        )
    
    @classmethod
    def from_hyperliquid(cls, data: Dict[str, Any]) -> 'Order':
        """Convert HyperLiquid API response to Order"""
        order_data = data.get('order', data)
        
        return cls(
            order_id=str(order_data.get('oid', '')),
            symbol=order_data.get('coin', '') + 'USD',
            side=OrderSide.BUY if float(order_data.get('sz', 0)) > 0 else OrderSide.SELL,
            order_type=OrderType.LIMIT if order_data.get('limitPx') else OrderType.MARKET,
            size=abs(float(order_data.get('sz', 0))),
            price=float(order_data.get('limitPx', 0)) if order_data.get('limitPx') else None,
            filled_size=abs(float(order_data.get('szFilled', 0))),
            status=OrderStatus.FILLED if order_data.get('filled') else OrderStatus.NEW,
            exchange='hyperliquid',
            created_at=datetime.fromtimestamp(int(order_data.get('timestamp', 0)) / 1000) if order_data.get('timestamp') else None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization"""
        # Handle enums that might be strings
        side_val = self.side.value if hasattr(self.side, 'value') else str(self.side)
        type_val = self.order_type.value if hasattr(self.order_type, 'value') else str(self.order_type)
        status_val = self.status.value if hasattr(self.status, 'value') else str(self.status)
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': side_val,
            'order_type': type_val,
            'size': self.size,
            'price': self.price,
            'filled_size': self.filled_size,
            'avg_fill_price': self.avg_fill_price,
            'status': status_val,
            'reduce_only': self.reduce_only,
            'fill_percent': self.fill_percent,
            'exchange': self.exchange,
        }


@dataclass
class Balance:
    """
    Unified Balance Model
    
    Represents account balance across all exchanges
    """
    total_equity: float
    available_balance: float
    margin_used: float
    unrealized_pnl: float
    currency: str = "USDT"
    
    # Optional fields
    wallet_balance: Optional[float] = None
    position_value: Optional[float] = None
    order_margin: Optional[float] = None
    
    # Metadata
    exchange: str = "bybit"
    account_type: str = "unified"
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def used_margin(self) -> float:
        """Alias for margin_used"""
        return self.margin_used
    
    @property
    def free_margin(self) -> float:
        """Available margin for new positions"""
        return self.available_balance
    
    @property
    def margin_level(self) -> float:
        """Margin level percentage"""
        if self.margin_used == 0:
            return 100.0
        return (self.total_equity / self.margin_used) * 100
    
    @classmethod
    def from_bybit(cls, data: Dict[str, Any]) -> 'Balance':
        """Convert Bybit API response to Balance"""
        coin_data = data.get('coin', [{}])[0] if isinstance(data.get('coin'), list) else data.get('coin', {})
        
        return cls(
            total_equity=float(data.get('totalEquity', 0)),
            available_balance=float(data.get('totalAvailableBalance', 0)),
            margin_used=float(data.get('totalMarginBalance', 0)) - float(data.get('totalAvailableBalance', 0)),
            unrealized_pnl=float(data.get('totalPerpUPL', 0)),
            wallet_balance=float(data.get('totalWalletBalance', 0)),
            currency=coin_data.get('coin', 'USDT') if coin_data else 'USDT',
            exchange='bybit',
            account_type=data.get('accountType', 'unified').lower()
        )
    
    @classmethod
    def from_hyperliquid(cls, data: Dict[str, Any]) -> 'Balance':
        """Convert HyperLiquid API response to Balance"""
        margin_summary = data.get('marginSummary', data)
        
        return cls(
            total_equity=float(margin_summary.get('accountValue', 0)),
            available_balance=float(margin_summary.get('withdrawable', 0)),
            margin_used=float(margin_summary.get('totalMarginUsed', 0)),
            unrealized_pnl=float(margin_summary.get('totalNtlPos', 0)),
            currency='USDC',  # HL uses USDC
            exchange='hyperliquid',
            account_type='cross'
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization"""
        return {
            'total_equity': self.total_equity,
            'available_balance': self.available_balance,
            'margin_used': self.margin_used,
            'unrealized_pnl': self.unrealized_pnl,
            'currency': self.currency,
            'wallet_balance': self.wallet_balance,
            'margin_level': self.margin_level,
            'exchange': self.exchange,
            'account_type': self.account_type,
        }


@dataclass
class OrderResult:
    """
    Result of order placement operation
    
    Standardized response for all order operations
    """
    success: bool
    order_id: Optional[str] = None
    order: Optional[Order] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    filled_size: float = 0.0
    avg_price: Optional[float] = None
    
    # Metadata
    exchange: str = "bybit"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def success_result(cls, order: Order, exchange: str = "bybit") -> 'OrderResult':
        """Create successful result"""
        return cls(
            success=True,
            order_id=order.order_id,
            order=order,
            filled_size=order.filled_size,
            avg_price=order.avg_fill_price,
            exchange=exchange
        )
    
    @classmethod
    def error_result(cls, error: str, error_code: Optional[str] = None, exchange: str = "bybit") -> 'OrderResult':
        """Create error result"""
        return cls(
            success=False,
            error=error,
            error_code=error_code,
            exchange=exchange
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization"""
        return {
            'success': self.success,
            'order_id': self.order_id,
            'order': self.order.to_dict() if self.order else None,
            'error': self.error,
            'error_code': self.error_code,
            'filled_size': self.filled_size,
            'avg_price': self.avg_price,
            'exchange': self.exchange,
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def normalize_symbol(symbol: str, exchange: str = "bybit") -> str:
    """
    Normalize symbol format across exchanges
    
    Bybit: BTCUSDT
    HyperLiquid: BTCUSD
    """
    symbol = symbol.upper().replace(" ", "").replace("-", "").replace("_", "")
    
    if exchange == "hyperliquid":
        # HL uses USD suffix
        if symbol.endswith("USDT"):
            return symbol.replace("USDT", "USD")
        elif not symbol.endswith("USD"):
            return symbol + "USD"
    else:
        # Bybit uses USDT suffix
        if symbol.endswith("USD") and not symbol.endswith("USDT"):
            return symbol + "T"
        elif not symbol.endswith("USDT"):
            return symbol + "USDT"
    
    return symbol


def convert_side(side: str, from_format: str = "standard", to_format: str = "standard") -> str:
    """
    Convert side between different formats
    
    standard: Buy/Sell
    long_short: Long/Short
    numeric: 1/-1
    """
    side = str(side).upper()
    
    # Normalize to Buy/Sell first
    if side in ("BUY", "LONG", "L", "1"):
        normalized = "Buy"
    elif side in ("SELL", "SHORT", "S", "-1"):
        normalized = "Sell"
    else:
        normalized = side
    
    if to_format == "long_short":
        return "Long" if normalized == "Buy" else "Short"
    elif to_format == "numeric":
        return "1" if normalized == "Buy" else "-1"
    
    return normalized
