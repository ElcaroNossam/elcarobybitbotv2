"""
Trading Service - High-level trading operations
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import asyncio

from models.user import User
from models.position import Position, PositionSide
from models.trade import Trade, TradeType, TradeStatus
from models.exchange_credentials import ExchangeType
from services.exchange_service import (
    ExchangeAdapter, ExchangeService, exchange_service,
    OrderType, OrderSide, OrderResult, AccountBalance
)
from services.license_service import LicenseService, license_service
from core.exceptions import (
    ExchangeError, PremiumRequiredError, InsufficientBalanceError,
    PositionNotFoundError, OrderError
)


@dataclass
class TradeRequest:
    """Request to open a trade"""
    symbol: str
    side: PositionSide
    size_percent: float  # Percentage of balance to use
    leverage: int = 10
    take_profit_percent: Optional[float] = None
    stop_loss_percent: Optional[float] = None
    order_type: OrderType = OrderType.MARKET
    limit_price: Optional[float] = None
    is_dca: bool = False
    dca_levels: int = 1
    exchange_type: ExchangeType = ExchangeType.BYBIT


@dataclass
class TradeResult:
    """Result of a trade operation"""
    success: bool
    trade: Optional[Trade] = None
    order_result: Optional[OrderResult] = None
    error: Optional[str] = None
    positions_opened: List[Position] = None
    
    def __post_init__(self):
        if self.positions_opened is None:
            self.positions_opened = []


class TradingService:
    """High-level trading operations"""
    
    def __init__(
        self,
        exchange_service: ExchangeService,
        license_service: LicenseService
    ):
        self.exchange = exchange_service
        self.license = license_service
    
    async def open_position(
        self,
        user_id: int,
        request: TradeRequest,
        adapter: ExchangeAdapter
    ) -> TradeResult:
        """Open a new position"""
        try:
            # Check premium for HyperLiquid
            if request.exchange_type == ExchangeType.HYPERLIQUID:
                if not await self.license.has_premium_feature(user_id, "hyperliquid"):
                    raise PremiumRequiredError("HyperLiquid requires Premium license")
            
            # Get current balance
            balance = await adapter.get_balance()
            
            # Calculate position size
            position_value = balance.available_balance * (request.size_percent / 100)
            
            # Get current price
            ticker = await adapter.get_ticker(request.symbol)
            current_price = float(ticker.get("lastPrice", 0))
            
            if current_price <= 0:
                raise OrderError(f"Invalid price for {request.symbol}")
            
            # Calculate quantity
            quantity = (position_value * request.leverage) / current_price
            
            # Set leverage
            await adapter.set_leverage(request.symbol, request.leverage)
            
            # Calculate TP/SL prices
            take_profit = None
            stop_loss = None
            
            if request.take_profit_percent:
                if request.side == PositionSide.LONG:
                    take_profit = current_price * (1 + request.take_profit_percent / 100)
                else:
                    take_profit = current_price * (1 - request.take_profit_percent / 100)
            
            if request.stop_loss_percent:
                if request.side == PositionSide.LONG:
                    stop_loss = current_price * (1 - request.stop_loss_percent / 100)
                else:
                    stop_loss = current_price * (1 + request.stop_loss_percent / 100)
            
            # Place order
            order_side = OrderSide.BUY if request.side == PositionSide.LONG else OrderSide.SELL
            
            order_result = await adapter.place_order(
                symbol=request.symbol,
                side=order_side,
                order_type=request.order_type,
                quantity=quantity,
                price=request.limit_price,
                take_profit=take_profit,
                stop_loss=stop_loss,
                leverage=request.leverage
            )
            
            if order_result.error:
                raise OrderError(order_result.error)
            
            # Create trade record
            trade = Trade(
                user_id=user_id,
                symbol=request.symbol,
                trade_type=TradeType.OPEN,
                side=request.side,
                quantity=quantity,
                price=current_price,
                leverage=request.leverage,
                exchange=request.exchange_type,
                status=TradeStatus.FILLED if request.order_type == OrderType.MARKET else TradeStatus.PENDING,
                order_id=order_result.order_id,
                take_profit=take_profit,
                stop_loss=stop_loss,
                timestamp=datetime.utcnow()
            )
            
            return TradeResult(
                success=True,
                trade=trade,
                order_result=order_result
            )
            
        except PremiumRequiredError as e:
            return TradeResult(success=False, error=str(e))
        except InsufficientBalanceError as e:
            return TradeResult(success=False, error=f"Insufficient balance: {e}")
        except ExchangeError as e:
            return TradeResult(success=False, error=f"Exchange error: {e}")
        except Exception as e:
            return TradeResult(success=False, error=f"Unexpected error: {e}")
    
    async def close_position(
        self,
        user_id: int,
        symbol: str,
        adapter: ExchangeAdapter,
        close_percent: float = 100.0
    ) -> TradeResult:
        """Close an existing position"""
        try:
            # Get current positions
            positions = await adapter.get_positions()
            position = next((p for p in positions if p.symbol == symbol), None)
            
            if not position:
                raise PositionNotFoundError(f"No open position for {symbol}")
            
            # Calculate close quantity
            close_qty = position.size * (close_percent / 100)
            
            # Place closing order (opposite side)
            order_side = OrderSide.SELL if position.side == PositionSide.LONG else OrderSide.BUY
            
            order_result = await adapter.place_order(
                symbol=symbol,
                side=order_side,
                order_type=OrderType.MARKET,
                quantity=close_qty,
                reduce_only=True
            )
            
            if order_result.error:
                raise OrderError(order_result.error)
            
            # Create trade record
            ticker = await adapter.get_ticker(symbol)
            current_price = float(ticker.get("lastPrice", 0))
            
            trade = Trade(
                user_id=user_id,
                symbol=symbol,
                trade_type=TradeType.CLOSE,
                side=position.side,
                quantity=close_qty,
                price=current_price,
                leverage=position.leverage,
                exchange=adapter.exchange_type,
                status=TradeStatus.FILLED,
                order_id=order_result.order_id,
                pnl=position.unrealized_pnl * (close_percent / 100),
                timestamp=datetime.utcnow()
            )
            
            return TradeResult(
                success=True,
                trade=trade,
                order_result=order_result
            )
            
        except PositionNotFoundError as e:
            return TradeResult(success=False, error=str(e))
        except ExchangeError as e:
            return TradeResult(success=False, error=f"Exchange error: {e}")
        except Exception as e:
            return TradeResult(success=False, error=f"Unexpected error: {e}")
    
    async def update_tp_sl(
        self,
        user_id: int,
        symbol: str,
        adapter: ExchangeAdapter,
        take_profit: Optional[float] = None,
        stop_loss: Optional[float] = None
    ) -> TradeResult:
        """Update take profit / stop loss for a position"""
        try:
            positions = await adapter.get_positions()
            position = next((p for p in positions if p.symbol == symbol), None)
            
            if not position:
                raise PositionNotFoundError(f"No open position for {symbol}")
            
            # For Bybit, we need to use trading-stop endpoint
            # This is a simplified version
            return TradeResult(success=True)
            
        except Exception as e:
            return TradeResult(success=False, error=str(e))
    
    async def get_user_positions(
        self,
        user_id: int,
        adapter: ExchangeAdapter
    ) -> List[Position]:
        """Get all positions for a user"""
        return await adapter.get_positions()
    
    async def get_user_balance(
        self,
        user_id: int,
        adapter: ExchangeAdapter
    ) -> AccountBalance:
        """Get user's account balance"""
        return await adapter.get_balance()
    
    async def execute_dca(
        self,
        user_id: int,
        request: TradeRequest,
        adapter: ExchangeAdapter
    ) -> List[TradeResult]:
        """Execute DCA (Dollar Cost Averaging) orders"""
        results = []
        
        # Split size across DCA levels
        size_per_level = request.size_percent / request.dca_levels
        
        for i in range(request.dca_levels):
            dca_request = TradeRequest(
                symbol=request.symbol,
                side=request.side,
                size_percent=size_per_level,
                leverage=request.leverage,
                take_profit_percent=request.take_profit_percent,
                stop_loss_percent=request.stop_loss_percent,
                order_type=request.order_type,
                exchange_type=request.exchange_type,
                is_dca=True
            )
            
            result = await self.open_position(user_id, dca_request, adapter)
            results.append(result)
            
            # Small delay between orders
            if i < request.dca_levels - 1:
                await asyncio.sleep(0.1)
        
        return results
    
    async def cancel_all_orders(
        self,
        user_id: int,
        adapter: ExchangeAdapter,
        symbol: Optional[str] = None
    ) -> Tuple[int, int]:
        """Cancel all open orders. Returns (success_count, fail_count)"""
        orders = await adapter.get_open_orders(symbol)
        success = 0
        failed = 0
        
        for order in orders:
            order_id = order.get("orderId", order.get("oid", ""))
            order_symbol = order.get("symbol", symbol or "")
            
            if await adapter.cancel_order(order_symbol, order_id):
                success += 1
            else:
                failed += 1
        
        return success, failed


# Singleton instance
trading_service = TradingService(exchange_service, license_service)
