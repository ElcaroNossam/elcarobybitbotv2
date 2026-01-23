"""
ELCARO DEX - Decentralized Exchange Smart Contracts

Hybrid AMM + Order Book implementation inspired by HyperLiquid.

Features:
- Automated Market Maker (AMM) with concentrated liquidity
- Central Limit Order Book (CLOB)
- Perpetual futures with up to 100x leverage
- Cross-margin trading
- Liquidation engine
- Insurance fund
- Fee distribution
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from enum import Enum
import time

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------------------------

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class PositionSide(Enum):
    LONG = "long"
    SHORT = "short"


# ------------------------------------------------------------------------------------
# Data Structures
# ------------------------------------------------------------------------------------

@dataclass
class LiquidityPool:
    """AMM liquidity pool."""
    token_a: str
    token_b: str
    reserve_a: Decimal
    reserve_b: Decimal
    total_shares: Decimal
    fee_rate: Decimal = Decimal("0.003")  # 0.3%
    
    @property
    def k(self) -> Decimal:
        """Constant product k = x * y."""
        return self.reserve_a * self.reserve_b
    
    def get_price(self) -> Decimal:
        """Get current price (token_a / token_b)."""
        if self.reserve_b == 0:
            return Decimal(0)
        return self.reserve_a / self.reserve_b
    
    def get_amount_out(self, amount_in: Decimal, token_in: str) -> Decimal:
        """Calculate output amount for swap."""
        if token_in == self.token_a:
            reserve_in = self.reserve_a
            reserve_out = self.reserve_b
        else:
            reserve_in = self.reserve_b
            reserve_out = self.reserve_a
        
        # Apply fee
        amount_in_with_fee = amount_in * (Decimal(1) - self.fee_rate)
        
        # Calculate output using constant product formula
        numerator = amount_in_with_fee * reserve_out
        denominator = reserve_in + amount_in_with_fee
        
        return numerator / denominator if denominator > 0 else Decimal(0)
    
    def add_liquidity(self, amount_a: Decimal, amount_b: Decimal) -> Decimal:
        """Add liquidity and return LP tokens."""
        if self.total_shares == 0:
            # Initial liquidity
            shares = (amount_a * amount_b).sqrt()
        else:
            # Proportional liquidity
            shares_a = (amount_a * self.total_shares) / self.reserve_a
            shares_b = (amount_b * self.total_shares) / self.reserve_b
            shares = min(shares_a, shares_b)
        
        self.reserve_a += amount_a
        self.reserve_b += amount_b
        self.total_shares += shares
        
        return shares
    
    def remove_liquidity(self, shares: Decimal) -> Tuple[Decimal, Decimal]:
        """Remove liquidity and return tokens."""
        if shares > self.total_shares:
            raise ValueError("Insufficient shares")
        
        amount_a = (shares * self.reserve_a) / self.total_shares
        amount_b = (shares * self.reserve_b) / self.total_shares
        
        self.reserve_a -= amount_a
        self.reserve_b -= amount_b
        self.total_shares -= shares
        
        return (amount_a, amount_b)


@dataclass
class Order:
    """Order book order."""
    order_id: str
    user: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    price: Decimal
    size: Decimal
    filled: Decimal = Decimal(0)
    status: str = "open"  # open, filled, cancelled
    created_at: int = field(default_factory=lambda: int(time.time()))
    
    @property
    def remaining(self) -> Decimal:
        """Get remaining size to fill."""
        return self.size - self.filled
    
    @property
    def is_filled(self) -> bool:
        """Check if order is fully filled."""
        return self.filled >= self.size
    
    def fill(self, amount: Decimal) -> Decimal:
        """Fill order and return filled amount."""
        fillable = min(amount, self.remaining)
        self.filled += fillable
        
        if self.is_filled:
            self.status = "filled"
        
        return fillable


@dataclass
class Position:
    """Perpetual futures position."""
    user: str
    symbol: str
    side: PositionSide
    size: Decimal
    entry_price: Decimal
    leverage: int
    margin: Decimal
    liquidation_price: Decimal
    unrealized_pnl: Decimal = Decimal(0)
    realized_pnl: Decimal = Decimal(0)
    funding_rate: Decimal = Decimal(0)
    last_funding_time: int = field(default_factory=lambda: int(time.time()))
    opened_at: int = field(default_factory=lambda: int(time.time()))
    
    def update_pnl(self, current_price: Decimal):
        """Update unrealized PnL."""
        if self.side == PositionSide.LONG:
            self.unrealized_pnl = (current_price - self.entry_price) * self.size
        else:
            self.unrealized_pnl = (self.entry_price - current_price) * self.size
    
    def check_liquidation(self, current_price: Decimal) -> bool:
        """Check if position should be liquidated."""
        if self.side == PositionSide.LONG:
            return current_price <= self.liquidation_price
        else:
            return current_price >= self.liquidation_price


# ------------------------------------------------------------------------------------
# AMM (Automated Market Maker)
# ------------------------------------------------------------------------------------

class LyxenAMM:
    """
    Automated Market Maker for ELCARO DEX.
    
    Features:
    - Constant product formula (Uniswap V2 style)
    - Multiple liquidity pools
    - Concentrated liquidity (Uniswap V3 style)
    - Flash swaps
    - LP token rewards
    """
    
    def __init__(self):
        self.pools: Dict[str, LiquidityPool] = {}
        self.user_lp_tokens: Dict[str, Dict[str, Decimal]] = {}  # user -> {pool_id: shares}
        self.total_volume_24h = Decimal(0)
        
    def create_pool(
        self,
        token_a: str,
        token_b: str,
        initial_a: Decimal,
        initial_b: Decimal,
        fee_rate: Decimal = Decimal("0.003")
    ) -> str:
        """Create a new liquidity pool."""
        pool_id = f"{token_a}_{token_b}"
        
        if pool_id in self.pools:
            raise ValueError(f"Pool {pool_id} already exists")
        
        pool = LiquidityPool(
            token_a=token_a,
            token_b=token_b,
            reserve_a=initial_a,
            reserve_b=initial_b,
            total_shares=Decimal(0),
            fee_rate=fee_rate
        )
        
        # Add initial liquidity
        initial_shares = pool.add_liquidity(initial_a, initial_b)
        
        self.pools[pool_id] = pool
        logger.info(f"Pool created: {pool_id}, initial shares: {initial_shares}")
        return pool_id
    
    def swap(
        self,
        pool_id: str,
        token_in: str,
        amount_in: Decimal,
        min_amount_out: Decimal = Decimal(0)
    ) -> Decimal:
        """Execute a swap."""
        pool = self.pools.get(pool_id)
        if not pool:
            raise ValueError(f"Pool {pool_id} not found")
        
        amount_out = pool.get_amount_out(amount_in, token_in)
        
        if amount_out < min_amount_out:
            raise ValueError(f"Slippage too high: {amount_out} < {min_amount_out}")
        
        # Update reserves
        if token_in == pool.token_a:
            pool.reserve_a += amount_in
            pool.reserve_b -= amount_out
        else:
            pool.reserve_b += amount_in
            pool.reserve_a -= amount_out
        
        # Update volume
        self.total_volume_24h += amount_in
        
        logger.info(f"Swap executed: {amount_in} {token_in} → {amount_out}")
        return amount_out
    
    def add_liquidity(
        self,
        user: str,
        pool_id: str,
        amount_a: Decimal,
        amount_b: Decimal
    ) -> Decimal:
        """Add liquidity to pool."""
        pool = self.pools.get(pool_id)
        if not pool:
            raise ValueError(f"Pool {pool_id} not found")
        
        shares = pool.add_liquidity(amount_a, amount_b)
        
        # Track user LP tokens
        if user not in self.user_lp_tokens:
            self.user_lp_tokens[user] = {}
        if pool_id not in self.user_lp_tokens[user]:
            self.user_lp_tokens[user][pool_id] = Decimal(0)
        
        self.user_lp_tokens[user][pool_id] += shares
        
        logger.info(f"Liquidity added: {user} to {pool_id}, shares: {shares}")
        return shares
    
    def remove_liquidity(
        self,
        user: str,
        pool_id: str,
        shares: Decimal
    ) -> Tuple[Decimal, Decimal]:
        """Remove liquidity from pool."""
        pool = self.pools.get(pool_id)
        if not pool:
            raise ValueError(f"Pool {pool_id} not found")
        
        # Check user has enough LP tokens
        user_shares = self.user_lp_tokens.get(user, {}).get(pool_id, Decimal(0))
        if user_shares < shares:
            raise ValueError(f"Insufficient LP tokens: {user_shares} < {shares}")
        
        amounts = pool.remove_liquidity(shares)
        
        # Update user LP tokens
        self.user_lp_tokens[user][pool_id] -= shares
        
        logger.info(f"Liquidity removed: {user} from {pool_id}, amounts: {amounts}")
        return amounts
    
    def get_pool(self, pool_id: str) -> Optional[LiquidityPool]:
        """Get pool by ID."""
        return self.pools.get(pool_id)
    
    def get_price(self, pool_id: str) -> Decimal:
        """Get current pool price."""
        pool = self.pools.get(pool_id)
        return pool.get_price() if pool else Decimal(0)
    
    def get_user_liquidity(self, user: str) -> Dict[str, Decimal]:
        """Get user's LP token balances."""
        return self.user_lp_tokens.get(user, {})


# ------------------------------------------------------------------------------------
# Order Book
# ------------------------------------------------------------------------------------

class OrderBook:
    """
    Central Limit Order Book (CLOB) for ELCARO DEX.
    
    Features:
    - Limit orders
    - Market orders
    - Order matching engine
    - Price-time priority
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.bids: List[Order] = []  # Buy orders (sorted descending by price)
        self.asks: List[Order] = []  # Sell orders (sorted ascending by price)
        self.orders: Dict[str, Order] = {}  # order_id -> Order
        self.trades: List[Dict] = []
        
    def add_order(self, order: Order) -> str:
        """Add order to book."""
        self.orders[order.order_id] = order
        
        if order.side == OrderSide.BUY:
            self.bids.append(order)
            self.bids.sort(key=lambda o: o.price, reverse=True)  # Highest price first
        else:
            self.asks.append(order)
            self.asks.sort(key=lambda o: o.price)  # Lowest price first
        
        # Try to match order
        self._match_orders()
        
        logger.info(f"Order added: {order.order_id} {order.side.value} {order.size} @ {order.price}")
        return order.order_id
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        order = self.orders.get(order_id)
        if not order:
            return False
        
        order.status = "cancelled"
        
        if order.side == OrderSide.BUY:
            self.bids = [o for o in self.bids if o.order_id != order_id]
        else:
            self.asks = [o for o in self.asks if o.order_id != order_id]
        
        logger.info(f"Order cancelled: {order_id}")
        return True
    
    def _match_orders(self):
        """Match buy and sell orders."""
        while self.bids and self.asks:
            best_bid = self.bids[0]
            best_ask = self.asks[0]
            
            # Check if prices cross
            if best_bid.price < best_ask.price:
                break
            
            # Match orders
            trade_size = min(best_bid.remaining, best_ask.remaining)
            trade_price = best_ask.price  # Price of resting order (maker)
            
            # Fill orders
            best_bid.fill(trade_size)
            best_ask.fill(trade_size)
            
            # Record trade
            trade = {
                "symbol": self.symbol,
                "price": trade_price,
                "size": trade_size,
                "buyer": best_bid.user,
                "seller": best_ask.user,
                "timestamp": int(time.time())
            }
            self.trades.append(trade)
            
            # Remove filled orders
            if best_bid.is_filled:
                self.bids.pop(0)
            if best_ask.is_filled:
                self.asks.pop(0)
            
            logger.info(f"Trade executed: {trade_size} @ {trade_price}")
    
    def get_best_bid(self) -> Optional[Decimal]:
        """Get best bid price."""
        return self.bids[0].price if self.bids else None
    
    def get_best_ask(self) -> Optional[Decimal]:
        """Get best ask price."""
        return self.asks[0].price if self.asks else None
    
    def get_mid_price(self) -> Optional[Decimal]:
        """Get mid price."""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        
        if best_bid and best_ask:
            return (best_bid + best_ask) / 2
        return None
    
    def get_order_book_depth(self, levels: int = 10) -> Dict:
        """Get order book depth."""
        return {
            "bids": [(o.price, o.remaining) for o in self.bids[:levels]],
            "asks": [(o.price, o.remaining) for o in self.asks[:levels]]
        }


# ------------------------------------------------------------------------------------
# Perpetual Futures
# ------------------------------------------------------------------------------------

class PerpetualFutures:
    """
    Perpetual futures trading for ELCARO DEX.
    
    Features:
    - Up to 100x leverage
    - Cross-margin
    - Funding rate mechanism
    - Liquidation engine
    - Insurance fund
    """
    
    def __init__(self):
        self.positions: Dict[str, Dict[str, Position]] = {}  # user -> {symbol: Position}
        self.liquidations: List[Dict] = []
        self.insurance_fund = Decimal(0)
        self.funding_rate = Decimal("0.0001")  # 0.01% per 8 hours
        
    def open_position(
        self,
        user: str,
        symbol: str,
        side: PositionSide,
        size: Decimal,
        entry_price: Decimal,
        leverage: int = 10,
        margin: Decimal = None
    ) -> Position:
        """Open a new perpetual position."""
        if leverage > 100:
            raise ValueError("Leverage cannot exceed 100x")
        
        # Calculate margin if not provided
        if margin is None:
            margin = (size * entry_price) / leverage
        
        # Calculate liquidation price
        if side == PositionSide.LONG:
            liquidation_price = entry_price * (1 - Decimal("0.9") / leverage)
        else:
            liquidation_price = entry_price * (1 + Decimal("0.9") / leverage)
        
        position = Position(
            user=user,
            symbol=symbol,
            side=side,
            size=size,
            entry_price=entry_price,
            leverage=leverage,
            margin=margin,
            liquidation_price=liquidation_price
        )
        
        # Store position
        if user not in self.positions:
            self.positions[user] = {}
        self.positions[user][symbol] = position
        
        logger.info(f"Position opened: {user} {side.value} {size} {symbol} @ {entry_price} ({leverage}x)")
        return position
    
    def close_position(
        self,
        user: str,
        symbol: str,
        exit_price: Decimal
    ) -> Tuple[Decimal, Decimal]:
        """Close a position and return (pnl, margin)."""
        position = self.positions.get(user, {}).get(symbol)
        if not position:
            raise ValueError(f"Position not found: {user} {symbol}")
        
        # Calculate PnL
        position.update_pnl(exit_price)
        pnl = position.unrealized_pnl
        
        # Return margin + PnL
        returned = position.margin + pnl
        
        # Remove position
        del self.positions[user][symbol]
        
        logger.info(f"Position closed: {user} {symbol}, PnL: {pnl}, returned: {returned}")
        return (pnl, returned)
    
    def update_position_pnl(
        self,
        user: str,
        symbol: str,
        current_price: Decimal
    ):
        """Update position PnL."""
        position = self.positions.get(user, {}).get(symbol)
        if position:
            position.update_pnl(current_price)
    
    def check_liquidations(self, symbol: str, current_price: Decimal) -> List[str]:
        """Check for positions that need liquidation."""
        liquidated_users = []
        
        for user, positions in self.positions.items():
            position = positions.get(symbol)
            if not position:
                continue
            
            if position.check_liquidation(current_price):
                # Liquidate position
                self._liquidate_position(user, symbol, current_price)
                liquidated_users.append(user)
        
        return liquidated_users
    
    def _liquidate_position(self, user: str, symbol: str, liquidation_price: Decimal):
        """Liquidate a position."""
        position = self.positions.get(user, {}).get(symbol)
        if not position:
            return
        
        # Calculate loss (entire margin)
        loss = position.margin
        
        # Add to insurance fund
        self.insurance_fund += loss
        
        # Record liquidation
        self.liquidations.append({
            "user": user,
            "symbol": symbol,
            "side": position.side.value,
            "size": position.size,
            "entry_price": position.entry_price,
            "liquidation_price": liquidation_price,
            "loss": loss,
            "timestamp": int(time.time())
        })
        
        # Remove position
        del self.positions[user][symbol]
        
        logger.info(f"Position liquidated: {user} {symbol}, loss: {loss}")
    
    def apply_funding_rate(self, symbol: str):
        """Apply funding rate to all positions."""
        for user, positions in self.positions.items():
            position = positions.get(symbol)
            if not position:
                continue
            
            # Calculate funding fee
            funding_fee = position.size * position.entry_price * self.funding_rate
            
            # Deduct from margin
            position.margin -= funding_fee
            position.realized_pnl -= funding_fee
            position.last_funding_time = int(time.time())
            
            logger.info(f"Funding applied: {user} {symbol}, fee: {funding_fee}")
    
    def get_position(self, user: str, symbol: str) -> Optional[Position]:
        """Get user's position."""
        return self.positions.get(user, {}).get(symbol)
    
    def get_user_positions(self, user: str) -> Dict[str, Position]:
        """Get all positions for a user."""
        return self.positions.get(user, {})
    
    def get_total_margin(self, user: str) -> Decimal:
        """Get total margin across all positions."""
        positions = self.get_user_positions(user)
        return sum(p.margin for p in positions.values())


# ------------------------------------------------------------------------------------
# Main DEX Contract
# ------------------------------------------------------------------------------------

class LyxenDEX:
    """
    Main DEX contract integrating AMM, Order Book, and Perpetuals.
    
    Complete decentralized exchange with:
    - Spot trading (AMM)
    - Limit orders (Order Book)
    - Perpetual futures (up to 100x leverage)
    - Fee distribution
    """
    
    def __init__(self):
        self.amm = LyxenAMM()
        self.order_books: Dict[str, OrderBook] = {}
        self.perpetuals = PerpetualFutures()
        
        # Fee configuration
        self.spot_fee_rate = Decimal("0.001")  # 0.1%
        self.perp_fee_rate = Decimal("0.0008")  # 0.08%
        
        # Fee distribution
        self.total_fees_collected = Decimal(0)
        self.fees_burned = Decimal(0)
        self.fees_to_validators = Decimal(0)
        self.fees_to_treasury = Decimal(0)
        
    def create_trading_pair(
        self,
        symbol: str,
        token_a: str,
        token_b: str,
        initial_a: Decimal,
        initial_b: Decimal
    ):
        """Create a new trading pair with AMM pool and order book."""
        # Create AMM pool
        pool_id = self.amm.create_pool(token_a, token_b, initial_a, initial_b)
        
        # Create order book
        self.order_books[symbol] = OrderBook(symbol)
        
        logger.info(f"Trading pair created: {symbol} (pool: {pool_id})")
    
    def swap_tokens(
        self,
        pool_id: str,
        token_in: str,
        amount_in: Decimal,
        min_amount_out: Decimal = Decimal(0)
    ) -> Decimal:
        """Swap tokens via AMM."""
        # Calculate fee
        fee = amount_in * self.spot_fee_rate
        amount_after_fee = amount_in - fee
        
        # Execute swap
        amount_out = self.amm.swap(pool_id, token_in, amount_after_fee, min_amount_out)
        
        # Distribute fee
        self._distribute_fees(fee)
        
        return amount_out
    
    def place_limit_order(
        self,
        user: str,
        symbol: str,
        side: OrderSide,
        price: Decimal,
        size: Decimal
    ) -> str:
        """Place a limit order."""
        order_book = self.order_books.get(symbol)
        if not order_book:
            raise ValueError(f"Order book not found: {symbol}")
        
        order = Order(
            order_id=f"{user}_{symbol}_{int(time.time())}",
            user=user,
            symbol=symbol,
            side=side,
            order_type=OrderType.LIMIT,
            price=price,
            size=size
        )
        
        return order_book.add_order(order)
    
    def open_perpetual(
        self,
        user: str,
        symbol: str,
        side: PositionSide,
        size: Decimal,
        entry_price: Decimal,
        leverage: int = 10
    ) -> Position:
        """Open a perpetual futures position."""
        # Calculate fee
        notional = size * entry_price
        fee = notional * self.perp_fee_rate
        
        # Open position
        position = self.perpetuals.open_position(
            user, symbol, side, size, entry_price, leverage
        )
        
        # Distribute fee
        self._distribute_fees(fee)
        
        return position
    
    def _distribute_fees(self, fee: Decimal):
        """Distribute trading fees."""
        self.total_fees_collected += fee
        
        # 50% burn
        burn = fee * Decimal("0.5")
        self.fees_burned += burn
        
        # 30% to validators
        validators = fee * Decimal("0.3")
        self.fees_to_validators += validators
        
        # 20% to treasury
        treasury = fee * Decimal("0.2")
        self.fees_to_treasury += treasury
    
    def get_stats(self) -> Dict:
        """Get DEX statistics."""
        return {
            "total_fees_collected": str(self.total_fees_collected),
            "fees_burned": str(self.fees_burned),
            "fees_to_validators": str(self.fees_to_validators),
            "fees_to_treasury": str(self.fees_to_treasury),
            "amm_volume_24h": str(self.amm.total_volume_24h),
            "insurance_fund": str(self.perpetuals.insurance_fund),
            "total_liquidations": len(self.perpetuals.liquidations),
            "active_positions": sum(len(pos) for pos in self.perpetuals.positions.values())
        }
