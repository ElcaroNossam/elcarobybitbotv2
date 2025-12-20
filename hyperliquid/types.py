"""
HyperLiquid Type Definitions
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class OrderRequest:
    """Order request structure"""
    coin: str
    is_buy: bool
    sz: float
    limit_px: float
    reduce_only: bool = False
    order_type: Optional[Dict[str, Any]] = None
    cloid: Optional[str] = None


@dataclass
class OrderWire:
    """Wire format for orders"""
    a: int
    b: bool
    p: str
    s: str
    r: bool
    t: Dict[str, Any]
    c: Optional[str] = None


@dataclass
class CancelRequest:
    """Cancel request structure"""
    coin: str
    oid: int


@dataclass
class PositionData:
    """Position data from user state"""
    coin: str
    szi: float
    entry_px: Optional[float] = None
    position_value: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    return_on_equity: Optional[float] = None
    liquidation_px: Optional[float] = None
    leverage: Optional[Dict[str, Any]] = None
    margin_used: Optional[float] = None


@dataclass
class UserState:
    """User account state"""
    margin_summary: Dict[str, Any]
    cross_margin_summary: Dict[str, Any]
    asset_positions: List[Dict[str, Any]]
    withdrawable: float


@dataclass
class OpenOrder:
    """Open order data"""
    coin: str
    oid: int
    is_buy: bool
    limit_px: float
    sz: float
    order_type: str
    reduce_only: bool
    timestamp: int
    cloid: Optional[str] = None


@dataclass
class Fill:
    """Trade fill data"""
    coin: str
    px: float
    sz: float
    side: str
    time: int
    start_position: float
    dir: str
    closed_pnl: float
    hash: str
    oid: int
    fee: float


@dataclass
class Meta:
    """Market metadata"""
    universe: List[Dict[str, Any]]
