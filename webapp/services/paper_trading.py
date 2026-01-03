"""
ElCaro Paper Trading Module
Simulates real trading without risking actual capital:
- Virtual balance tracking
- Position management
- P&L calculation
- Performance metrics
- Trade history
- Session management
"""
import asyncio
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import logging
import json
import uuid

from core.tasks import safe_create_task


logger = logging.getLogger(__name__)


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class PositionSide(Enum):
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass
class PaperOrder:
    """Paper trading order"""
    id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float]
    trigger_price: Optional[float]
    status: OrderStatus
    created_at: datetime
    filled_at: Optional[datetime] = None
    filled_price: Optional[float] = None
    filled_quantity: Optional[float] = None
    reduce_only: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "side": self.side.value,
            "order_type": self.order_type.value,
            "quantity": self.quantity,
            "price": self.price,
            "trigger_price": self.trigger_price,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "filled_at": self.filled_at.isoformat() if self.filled_at else None,
            "filled_price": self.filled_price,
            "filled_quantity": self.filled_quantity,
            "reduce_only": self.reduce_only
        }


@dataclass
class PaperPosition:
    """Paper trading position"""
    symbol: str
    side: PositionSide
    quantity: float
    entry_price: float
    current_price: float
    leverage: int
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    trailing_stop: Optional[float] = None
    trailing_stop_activation: Optional[float] = None
    opened_at: datetime = field(default_factory=datetime.now)
    
    @property
    def unrealized_pnl(self) -> float:
        if self.side == PositionSide.LONG:
            return (self.current_price - self.entry_price) / self.entry_price * 100 * self.leverage
        else:
            return (self.entry_price - self.current_price) / self.entry_price * 100 * self.leverage
    
    @property
    def unrealized_pnl_usd(self) -> float:
        notional = self.quantity * self.entry_price
        if self.side == PositionSide.LONG:
            return (self.current_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - self.current_price) * self.quantity
    
    @property
    def margin_used(self) -> float:
        return (self.quantity * self.entry_price) / self.leverage
    
    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "side": self.side.value,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "leverage": self.leverage,
            "unrealized_pnl": self.unrealized_pnl,
            "unrealized_pnl_usd": self.unrealized_pnl_usd,
            "margin_used": self.margin_used,
            "take_profit": self.take_profit,
            "stop_loss": self.stop_loss,
            "trailing_stop": self.trailing_stop,
            "opened_at": self.opened_at.isoformat()
        }


@dataclass
class PaperTrade:
    """Closed paper trade"""
    id: str
    symbol: str
    side: PositionSide
    quantity: float
    entry_price: float
    exit_price: float
    leverage: int
    pnl_percent: float
    pnl_usd: float
    opened_at: datetime
    closed_at: datetime
    exit_reason: str
    strategy: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "side": self.side.value,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "leverage": self.leverage,
            "pnl_percent": self.pnl_percent,
            "pnl_usd": self.pnl_usd,
            "opened_at": self.opened_at.isoformat(),
            "closed_at": self.closed_at.isoformat(),
            "exit_reason": self.exit_reason,
            "strategy": self.strategy
        }


@dataclass
class SessionMetrics:
    """Paper trading session metrics"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl_percent: float = 0.0
    total_pnl_usd: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    best_trade: float = 0.0
    worst_trade: float = 0.0
    avg_holding_time: float = 0.0  # minutes
    sharpe_ratio: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "total_pnl_percent": round(self.total_pnl_percent, 2),
            "total_pnl_usd": round(self.total_pnl_usd, 2),
            "max_drawdown": round(self.max_drawdown, 2),
            "win_rate": round(self.win_rate, 2),
            "avg_win": round(self.avg_win, 2),
            "avg_loss": round(self.avg_loss, 2),
            "profit_factor": round(self.profit_factor, 2),
            "best_trade": round(self.best_trade, 2),
            "worst_trade": round(self.worst_trade, 2),
            "avg_holding_time": round(self.avg_holding_time, 2),
            "sharpe_ratio": round(self.sharpe_ratio, 2)
        }


class PaperTradingSession:
    """Paper trading session manager"""
    
    def __init__(
        self,
        session_id: str,
        user_id: int,
        initial_balance: float = 10000.0,
        leverage_default: int = 10,
        commission_rate: float = 0.0006,  # 0.06% taker fee
        slippage_percent: float = 0.05
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.leverage_default = leverage_default
        self.commission_rate = commission_rate
        self.slippage_percent = slippage_percent
        
        self.positions: Dict[str, PaperPosition] = {}
        self.pending_orders: Dict[str, PaperOrder] = {}
        self.trades: List[PaperTrade] = []
        self.balance_history: List[Dict] = [
            {"timestamp": datetime.now().isoformat(), "balance": initial_balance}
        ]
        
        self.created_at = datetime.now()
        self.is_active = True
        self.price_feeds: Dict[str, float] = {}
        
        # Callbacks for events
        self.on_order_filled: Optional[Callable] = None
        self.on_position_closed: Optional[Callable] = None
        self.on_stop_triggered: Optional[Callable] = None
    
    @property
    def equity(self) -> float:
        """Total equity including unrealized P&L"""
        unrealized = sum(p.unrealized_pnl_usd for p in self.positions.values())
        return self.balance + unrealized
    
    @property
    def margin_used(self) -> float:
        """Total margin in use"""
        return sum(p.margin_used for p in self.positions.values())
    
    @property
    def available_margin(self) -> float:
        """Available margin for new positions"""
        return self.balance - self.margin_used
    
    def update_price(self, symbol: str, price: float) -> None:
        """Update price for a symbol and check stops/limits"""
        self.price_feeds[symbol] = price
        
        # Update position current price
        if symbol in self.positions:
            self.positions[symbol].current_price = price
            self._check_position_stops(symbol, price)
        
        # Check pending orders
        self._check_pending_orders(symbol, price)
    
    async def place_order(
        self,
        symbol: str,
        side: str,  # "BUY" or "SELL"
        order_type: str,  # "MARKET", "LIMIT", "STOP_LOSS", "TAKE_PROFIT"
        quantity: float,
        price: Optional[float] = None,
        trigger_price: Optional[float] = None,
        leverage: Optional[int] = None,
        take_profit: Optional[float] = None,
        stop_loss: Optional[float] = None,
        reduce_only: bool = False,
        strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        """Place a paper order"""
        order_id = str(uuid.uuid4())[:8]
        
        order_side = OrderSide[side]
        order_type_enum = OrderType[order_type]
        
        # Get current price
        current_price = self.price_feeds.get(symbol)
        if not current_price and order_type_enum == OrderType.MARKET:
            # Fetch current price
            try:
                from webapp.services.backtest_engine_pro import DataFetcher
                fetcher = DataFetcher()
                data = await fetcher.fetch_historical(symbol, "1m", 1)
                if data:
                    current_price = data[-1].get("close", 0)
                    self.price_feeds[symbol] = current_price
            except Exception as e:
                logger.error(f"Error fetching price for {symbol}: {e}")
                return {"success": False, "error": "Could not fetch current price"}
        
        # Calculate required margin
        lev = leverage or self.leverage_default
        notional = quantity * (price or current_price or 0)
        required_margin = notional / lev
        
        if not reduce_only and required_margin > self.available_margin:
            return {
                "success": False,
                "error": f"Insufficient margin. Required: ${required_margin:.2f}, Available: ${self.available_margin:.2f}"
            }
        
        order = PaperOrder(
            id=order_id,
            symbol=symbol,
            side=order_side,
            order_type=order_type_enum,
            quantity=quantity,
            price=price,
            trigger_price=trigger_price,
            status=OrderStatus.PENDING,
            created_at=datetime.now(),
            reduce_only=reduce_only
        )
        
        # Market orders fill immediately
        if order_type_enum == OrderType.MARKET:
            fill_price = self._apply_slippage(current_price, order_side)
            return await self._fill_order(order, fill_price, lev, take_profit, stop_loss, strategy)
        
        # Store pending order
        self.pending_orders[order_id] = order
        
        return {
            "success": True,
            "order_id": order_id,
            "status": "PENDING",
            "message": f"Order placed. Waiting for price to reach {price or trigger_price}"
        }
    
    async def _fill_order(
        self,
        order: PaperOrder,
        fill_price: float,
        leverage: int,
        take_profit: Optional[float],
        stop_loss: Optional[float],
        strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fill an order"""
        order.status = OrderStatus.FILLED
        order.filled_at = datetime.now()
        order.filled_price = fill_price
        order.filled_quantity = order.quantity
        
        # Calculate commission
        notional = order.quantity * fill_price
        commission = notional * self.commission_rate
        self.balance -= commission
        
        symbol = order.symbol
        
        # Check if closing existing position
        if symbol in self.positions:
            position = self.positions[symbol]
            
            # Determine if this closes the position
            closes_position = (
                (position.side == PositionSide.LONG and order.side == OrderSide.SELL) or
                (position.side == PositionSide.SHORT and order.side == OrderSide.BUY)
            )
            
            if closes_position:
                return await self._close_position(symbol, fill_price, "Signal", strategy)
        
        # Open new position
        position_side = PositionSide.LONG if order.side == OrderSide.BUY else PositionSide.SHORT
        
        position = PaperPosition(
            symbol=symbol,
            side=position_side,
            quantity=order.quantity,
            entry_price=fill_price,
            current_price=fill_price,
            leverage=leverage,
            take_profit=take_profit,
            stop_loss=stop_loss,
            opened_at=datetime.now()
        )
        
        self.positions[symbol] = position
        
        # Callback
        if self.on_order_filled:
            try:
                await self.on_order_filled(order, position)
            except Exception as e:
                logger.warning(f"on_order_filled callback failed: {e}")
        
        return {
            "success": True,
            "order_id": order.id,
            "status": "FILLED",
            "fill_price": fill_price,
            "commission": commission,
            "position": position.to_dict()
        }
    
    async def _close_position(
        self,
        symbol: str,
        exit_price: float,
        exit_reason: str,
        strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        """Close a position"""
        if symbol not in self.positions:
            return {"success": False, "error": "Position not found"}
        
        position = self.positions[symbol]
        
        # Calculate P&L
        if position.side == PositionSide.LONG:
            pnl_percent = (exit_price - position.entry_price) / position.entry_price * 100 * position.leverage
            pnl_usd = (exit_price - position.entry_price) * position.quantity
        else:
            pnl_percent = (position.entry_price - exit_price) / position.entry_price * 100 * position.leverage
            pnl_usd = (position.entry_price - exit_price) * position.quantity
        
        # Apply commission
        commission = position.quantity * exit_price * self.commission_rate
        pnl_usd -= commission
        
        # Update balance
        self.balance += pnl_usd
        
        # Record trade
        trade = PaperTrade(
            id=str(uuid.uuid4())[:8],
            symbol=symbol,
            side=position.side,
            quantity=position.quantity,
            entry_price=position.entry_price,
            exit_price=exit_price,
            leverage=position.leverage,
            pnl_percent=pnl_percent,
            pnl_usd=pnl_usd,
            opened_at=position.opened_at,
            closed_at=datetime.now(),
            exit_reason=exit_reason,
            strategy=strategy
        )
        self.trades.append(trade)
        
        # Remove position
        del self.positions[symbol]
        
        # Record balance history
        self.balance_history.append({
            "timestamp": datetime.now().isoformat(),
            "balance": self.balance
        })
        
        # Callback
        if self.on_position_closed:
            try:
                await self.on_position_closed(trade)
            except Exception as e:
                logger.warning(f"on_position_closed callback failed: {e}")
        
        return {
            "success": True,
            "trade": trade.to_dict(),
            "balance": self.balance,
            "pnl_percent": pnl_percent,
            "pnl_usd": pnl_usd
        }
    
    def _check_position_stops(self, symbol: str, price: float) -> None:
        """Check if position hits TP/SL"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        
        # Check Take Profit
        if position.take_profit:
            if position.side == PositionSide.LONG and price >= position.take_profit:
                safe_create_task(self._close_position(symbol, price, "Take Profit"), name=f"close_{symbol}_tp")
                if self.on_stop_triggered:
                    safe_create_task(self.on_stop_triggered(symbol, "TP", price), name=f"trigger_{symbol}_tp")
                return
            elif position.side == PositionSide.SHORT and price <= position.take_profit:
                safe_create_task(self._close_position(symbol, price, "Take Profit"), name=f"close_{symbol}_tp")
                if self.on_stop_triggered:
                    safe_create_task(self.on_stop_triggered(symbol, "TP", price), name=f"trigger_{symbol}_tp")
                return
        
        # Check Stop Loss
        if position.stop_loss:
            if position.side == PositionSide.LONG and price <= position.stop_loss:
                safe_create_task(self._close_position(symbol, price, "Stop Loss"), name=f"close_{symbol}_sl")
                if self.on_stop_triggered:
                    safe_create_task(self.on_stop_triggered(symbol, "SL", price), name=f"trigger_{symbol}_sl")
                return
            elif position.side == PositionSide.SHORT and price >= position.stop_loss:
                safe_create_task(self._close_position(symbol, price, "Stop Loss"), name=f"close_{symbol}_sl")
                if self.on_stop_triggered:
                    safe_create_task(self.on_stop_triggered(symbol, "SL", price), name=f"trigger_{symbol}_sl")
                return
        
        # Check Trailing Stop
        if position.trailing_stop and position.trailing_stop_activation:
            # Check if trailing is activated
            if position.side == PositionSide.LONG:
                if price >= position.entry_price * (1 + position.trailing_stop_activation / 100):
                    # Update trailing stop
                    new_stop = price * (1 - position.trailing_stop / 100)
                    if not position.stop_loss or new_stop > position.stop_loss:
                        position.stop_loss = new_stop
            else:
                if price <= position.entry_price * (1 - position.trailing_stop_activation / 100):
                    new_stop = price * (1 + position.trailing_stop / 100)
                    if not position.stop_loss or new_stop < position.stop_loss:
                        position.stop_loss = new_stop
    
    def _check_pending_orders(self, symbol: str, price: float) -> None:
        """Check pending orders for fills"""
        orders_to_fill = []
        
        for order_id, order in list(self.pending_orders.items()):
            if order.symbol != symbol:
                continue
            
            should_fill = False
            fill_price = price
            
            if order.order_type == OrderType.LIMIT:
                if order.side == OrderSide.BUY and price <= order.price:
                    should_fill = True
                    fill_price = order.price
                elif order.side == OrderSide.SELL and price >= order.price:
                    should_fill = True
                    fill_price = order.price
            
            elif order.order_type == OrderType.STOP_LOSS:
                if order.side == OrderSide.SELL and price <= order.trigger_price:
                    should_fill = True
                elif order.side == OrderSide.BUY and price >= order.trigger_price:
                    should_fill = True
            
            elif order.order_type == OrderType.TAKE_PROFIT:
                if order.side == OrderSide.SELL and price >= order.trigger_price:
                    should_fill = True
                elif order.side == OrderSide.BUY and price <= order.trigger_price:
                    should_fill = True
            
            if should_fill:
                orders_to_fill.append((order_id, order, fill_price))
        
        # Fill orders
        for order_id, order, fill_price in orders_to_fill:
            del self.pending_orders[order_id]
            safe_create_task(
                self._fill_order(order, fill_price, self.leverage_default, None, None),
                name=f"fill_order_{order_id}"
            )
    
    def _apply_slippage(self, price: float, side: OrderSide) -> float:
        """Apply slippage to price"""
        slippage = price * self.slippage_percent / 100
        if side == OrderSide.BUY:
            return price + slippage
        return price - slippage
    
    async def close_all_positions(self) -> Dict[str, Any]:
        """Close all open positions"""
        results = []
        
        for symbol in list(self.positions.keys()):
            price = self.price_feeds.get(symbol, self.positions[symbol].current_price)
            result = await self._close_position(symbol, price, "Close All")
            results.append(result)
        
        return {
            "success": True,
            "closed_positions": len(results),
            "results": results
        }
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel a pending order"""
        if order_id not in self.pending_orders:
            return {"success": False, "error": "Order not found"}
        
        order = self.pending_orders[order_id]
        order.status = OrderStatus.CANCELLED
        del self.pending_orders[order_id]
        
        return {"success": True, "order_id": order_id, "status": "CANCELLED"}
    
    def cancel_all_orders(self) -> Dict[str, Any]:
        """Cancel all pending orders"""
        count = len(self.pending_orders)
        self.pending_orders.clear()
        return {"success": True, "cancelled_count": count}
    
    def modify_position(
        self,
        symbol: str,
        take_profit: Optional[float] = None,
        stop_loss: Optional[float] = None,
        trailing_stop: Optional[float] = None,
        trailing_stop_activation: Optional[float] = None
    ) -> Dict[str, Any]:
        """Modify position TP/SL"""
        if symbol not in self.positions:
            return {"success": False, "error": "Position not found"}
        
        position = self.positions[symbol]
        
        if take_profit is not None:
            position.take_profit = take_profit
        if stop_loss is not None:
            position.stop_loss = stop_loss
        if trailing_stop is not None:
            position.trailing_stop = trailing_stop
        if trailing_stop_activation is not None:
            position.trailing_stop_activation = trailing_stop_activation
        
        return {"success": True, "position": position.to_dict()}
    
    def get_metrics(self) -> SessionMetrics:
        """Calculate session performance metrics"""
        metrics = SessionMetrics()
        
        if not self.trades:
            return metrics
        
        metrics.total_trades = len(self.trades)
        
        wins = [t for t in self.trades if t.pnl_percent > 0]
        losses = [t for t in self.trades if t.pnl_percent <= 0]
        
        metrics.winning_trades = len(wins)
        metrics.losing_trades = len(losses)
        
        metrics.total_pnl_percent = sum(t.pnl_percent for t in self.trades)
        metrics.total_pnl_usd = sum(t.pnl_usd for t in self.trades)
        
        if metrics.total_trades > 0:
            metrics.win_rate = (metrics.winning_trades / metrics.total_trades) * 100
        
        if wins:
            metrics.avg_win = sum(t.pnl_percent for t in wins) / len(wins)
            metrics.best_trade = max(t.pnl_percent for t in wins)
        
        if losses:
            metrics.avg_loss = sum(t.pnl_percent for t in losses) / len(losses)
            metrics.worst_trade = min(t.pnl_percent for t in losses)
        
        # Profit factor
        gross_profit = sum(t.pnl_usd for t in wins) if wins else 0
        gross_loss = abs(sum(t.pnl_usd for t in losses)) if losses else 0
        if gross_loss > 0:
            metrics.profit_factor = gross_profit / gross_loss
        
        # Max drawdown
        peak = self.initial_balance
        max_dd = 0
        for entry in self.balance_history:
            balance = entry["balance"]
            if balance > peak:
                peak = balance
            dd = (peak - balance) / peak * 100
            if dd > max_dd:
                max_dd = dd
        metrics.max_drawdown = max_dd
        
        # Average holding time
        holding_times = []
        for t in self.trades:
            duration = (t.closed_at - t.opened_at).total_seconds() / 60
            holding_times.append(duration)
        if holding_times:
            metrics.avg_holding_time = sum(holding_times) / len(holding_times)
        
        # Sharpe ratio (simplified)
        if len(self.trades) > 1:
            returns = [t.pnl_percent for t in self.trades]
            avg_return = sum(returns) / len(returns)
            variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
            std_dev = variance ** 0.5
            if std_dev > 0:
                metrics.sharpe_ratio = avg_return / std_dev
        
        return metrics
    
    def get_status(self) -> Dict[str, Any]:
        """Get current session status"""
        metrics = self.get_metrics()
        
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "initial_balance": self.initial_balance,
            "current_balance": self.balance,
            "equity": self.equity,
            "margin_used": self.margin_used,
            "available_margin": self.available_margin,
            "pnl_percent": ((self.equity - self.initial_balance) / self.initial_balance) * 100,
            "open_positions": len(self.positions),
            "pending_orders": len(self.pending_orders),
            "total_trades": len(self.trades),
            "positions": [p.to_dict() for p in self.positions.values()],
            "pending_orders_list": [o.to_dict() for o in self.pending_orders.values()],
            "metrics": metrics.to_dict()
        }
    
    def export_trades(self) -> List[Dict]:
        """Export trade history"""
        return [t.to_dict() for t in self.trades]
    
    def to_dict(self) -> Dict:
        """Serialize session for storage"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "initial_balance": self.initial_balance,
            "balance": self.balance,
            "leverage_default": self.leverage_default,
            "commission_rate": self.commission_rate,
            "slippage_percent": self.slippage_percent,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "positions": {k: v.to_dict() for k, v in self.positions.items()},
            "pending_orders": {k: v.to_dict() for k, v in self.pending_orders.items()},
            "trades": [t.to_dict() for t in self.trades],
            "balance_history": self.balance_history
        }


class PaperTradingManager:
    """Manages multiple paper trading sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, PaperTradingSession] = {}
        self.user_sessions: Dict[int, str] = {}  # user_id -> session_id
        self._price_update_task: Optional[asyncio.Task] = None
        self._running = False
    
    def create_session(
        self,
        user_id: int,
        initial_balance: float = 10000.0,
        leverage: int = 10,
        commission_rate: float = 0.0006,
        slippage_percent: float = 0.05
    ) -> PaperTradingSession:
        """Create a new paper trading session"""
        session_id = str(uuid.uuid4())[:8]
        
        # Close existing session for user
        if user_id in self.user_sessions:
            old_session_id = self.user_sessions[user_id]
            if old_session_id in self.sessions:
                self.sessions[old_session_id].is_active = False
        
        session = PaperTradingSession(
            session_id=session_id,
            user_id=user_id,
            initial_balance=initial_balance,
            leverage_default=leverage,
            commission_rate=commission_rate,
            slippage_percent=slippage_percent
        )
        
        self.sessions[session_id] = session
        self.user_sessions[user_id] = session_id
        
        return session
    
    def get_session(self, session_id: str) -> Optional[PaperTradingSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def get_user_session(self, user_id: int) -> Optional[PaperTradingSession]:
        """Get active session for user"""
        session_id = self.user_sessions.get(user_id)
        if session_id:
            return self.sessions.get(session_id)
        return None
    
    def close_session(self, session_id: str) -> bool:
        """Close and archive a session"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        session.is_active = False
        
        # Remove from active user sessions
        if session.user_id in self.user_sessions:
            if self.user_sessions[session.user_id] == session_id:
                del self.user_sessions[session.user_id]
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session completely"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # Remove from user sessions
        if session.user_id in self.user_sessions:
            if self.user_sessions[session.user_id] == session_id:
                del self.user_sessions[session.user_id]
        
        del self.sessions[session_id]
        return True
    
    def list_sessions(self, user_id: Optional[int] = None) -> List[Dict]:
        """List all sessions, optionally filtered by user"""
        sessions = []
        
        for session in self.sessions.values():
            if user_id is None or session.user_id == user_id:
                sessions.append({
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "is_active": session.is_active,
                    "created_at": session.created_at.isoformat(),
                    "initial_balance": session.initial_balance,
                    "current_balance": session.balance,
                    "equity": session.equity,
                    "total_trades": len(session.trades)
                })
        
        return sessions
    
    async def start_price_updates(self, symbols: List[str], interval: float = 5.0):
        """Start background price updates for all sessions"""
        self._running = True
        self._price_update_task = safe_create_task(
            self._price_update_loop(symbols, interval),
            name="paper_trading_price_updates"
        )
    
    async def stop_price_updates(self):
        """Stop background price updates"""
        self._running = False
        if self._price_update_task:
            self._price_update_task.cancel()
            try:
                await self._price_update_task
            except asyncio.CancelledError:
                pass
    
    async def _price_update_loop(self, symbols: List[str], interval: float):
        """Background task to update prices"""
        from webapp.services.backtest_engine_pro import DataFetcher
        fetcher = DataFetcher()
        
        while self._running:
            try:
                for symbol in symbols:
                    try:
                        data = await fetcher.fetch_historical(symbol, "1m", 1)
                        if data:
                            price = data[-1].get("close", 0)
                            
                            # Update all active sessions
                            for session in self.sessions.values():
                                if session.is_active:
                                    session.update_price(symbol, price)
                    except Exception as e:
                        logger.error(f"Price update error for {symbol}: {e}")
                
                await asyncio.sleep(interval)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Price update loop error: {e}")
                await asyncio.sleep(interval)
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top performing sessions"""
        ranked = []
        
        for session in self.sessions.values():
            if len(session.trades) >= 5:  # Minimum trades requirement
                pnl_percent = ((session.equity - session.initial_balance) / session.initial_balance) * 100
                metrics = session.get_metrics()
                
                ranked.append({
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "total_pnl_percent": pnl_percent,
                    "total_trades": len(session.trades),
                    "win_rate": metrics.win_rate,
                    "sharpe_ratio": metrics.sharpe_ratio,
                    "max_drawdown": metrics.max_drawdown
                })
        
        # Sort by PnL
        ranked.sort(key=lambda x: x["total_pnl_percent"], reverse=True)
        
        return ranked[:limit]


# Singleton instance
paper_trading_manager = PaperTradingManager()
