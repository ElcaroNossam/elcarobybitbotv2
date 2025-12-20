"""
Trading API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from webapp.api.auth import verify_token

router = APIRouter()


class Position(BaseModel):
    symbol: str
    side: str  # long, short
    size: float
    entry_price: float
    current_price: float
    leverage: int
    unrealized_pnl: float
    pnl_percent: float
    margin: float
    liquidation_price: Optional[float] = None
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    exchange: str = "bybit"


class Order(BaseModel):
    order_id: str
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None
    status: str
    created_at: datetime
    exchange: str = "bybit"


class TradeLog(BaseModel):
    id: int
    symbol: str
    side: str
    trade_type: str
    quantity: float
    price: float
    pnl: Optional[float] = None
    timestamp: datetime
    exchange: str
    signal_source: Optional[str] = None


class PlaceOrderRequest(BaseModel):
    symbol: str
    side: str  # buy, sell
    order_type: str  # market, limit
    quantity: float
    price: Optional[float] = None
    leverage: int = 10
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    exchange: str = "bybit"


class ClosePositionRequest(BaseModel):
    symbol: str
    close_percent: float = 100.0
    exchange: str = "bybit"


@router.get("/positions", response_model=List[Position])
async def get_positions(
    exchange: str = "all",
    payload: dict = Depends(verify_token)
):
    """Get all open positions"""
    user_id = int(payload.get("sub", 0))
    
    # TODO: Get positions from exchange adapter
    return []


@router.get("/orders", response_model=List[Order])
async def get_open_orders(
    exchange: str = "all",
    symbol: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    """Get all open orders"""
    user_id = int(payload.get("sub", 0))
    
    # TODO: Get orders from exchange adapter
    return []


@router.post("/order")
async def place_order(
    request: PlaceOrderRequest,
    payload: dict = Depends(verify_token)
):
    """Place a new order"""
    user_id = int(payload.get("sub", 0))
    
    # Check premium for HyperLiquid
    if request.exchange == "hyperliquid":
        # TODO: Check premium
        pass
    
    # TODO: Place order via trading service
    return {"order_id": "xxx", "status": "created"}


@router.post("/close")
async def close_position(
    request: ClosePositionRequest,
    payload: dict = Depends(verify_token)
):
    """Close a position"""
    user_id = int(payload.get("sub", 0))
    
    # TODO: Close position via trading service
    return {"success": True, "message": "Position closed"}


@router.delete("/order/{order_id}")
async def cancel_order(
    order_id: str,
    exchange: str = "bybit",
    payload: dict = Depends(verify_token)
):
    """Cancel an order"""
    user_id = int(payload.get("sub", 0))
    
    # TODO: Cancel order via exchange adapter
    return {"success": True, "message": "Order cancelled"}


@router.get("/history", response_model=List[TradeLog])
async def get_trade_history(
    exchange: str = "all",
    limit: int = 100,
    offset: int = 0,
    payload: dict = Depends(verify_token)
):
    """Get trade history"""
    user_id = int(payload.get("sub", 0))
    
    # TODO: Get trade logs from database
    return []
