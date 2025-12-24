"""
Unified Trading Functions - Drop-in replacements for bot.py

These functions use the new unified architecture:
- models/unified.py for data models
- core/exchange_client.py for exchange routing
- Proper error handling and logging

Replace old bot.py functions with these.
"""
import logging
from typing import Optional, List, Dict, Any
from models import Position, Order, Balance, OrderResult, OrderSide, OrderType, normalize_symbol
from core import get_exchange_client, track_latency, count_errors
import db

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# 1. GET BALANCE
# ═══════════════════════════════════════════════════════════════

@track_latency(name='bot.get_balance')
async def get_balance_unified(user_id: int, exchange: str = 'bybit', account_type: str = 'demo') -> Optional[Balance]:
    """
    Get user balance using unified client
    
    Args:
        user_id: Telegram user ID
        exchange: 'bybit' or 'hyperliquid'
        account_type: 'demo', 'real', or 'testnet'
    
    Returns:
        Balance object or None if error
    """
    try:
        from core.exchange_client import get_exchange_client
        client = await get_exchange_client(user_id, exchange_type=exchange, account_type=account_type)
        
        result = await client.get_balance()
        
        # Handle different return types - could be Balance object directly or dict
        if isinstance(result, Balance):
            return result
        elif isinstance(result, dict):
            if not result.get('success'):
                logger.error(f"Balance fetch failed: {result.get('error')}")
                return None
            
            data = result.get('data', result)
            return Balance(
                total_equity=data.get('total_equity', 0),
                available_balance=data.get('available_balance', 0),
                margin_used=data.get('margin_used', 0),
                unrealized_pnl=data.get('unrealized_pnl', 0),
                currency=data.get('currency', 'USDT')
            )
        else:
            logger.error(f"Unexpected result type from get_balance: {type(result)}")
            return None
    except Exception as e:
        logger.error(f"get_balance_unified error for user {user_id}: {e}")
        count_errors('bot.get_balance')
        return None


# ═══════════════════════════════════════════════════════════════
# 2. GET POSITIONS
# ═══════════════════════════════════════════════════════════════

@track_latency(name='bot.get_positions')
async def get_positions_unified(user_id: int, symbol: Optional[str] = None, exchange: str = 'bybit', account_type: str = 'demo') -> List[Position]:
    """
    Get user positions using unified client
    
    Args:
        user_id: Telegram user ID
        symbol: Optional symbol filter
        exchange: 'bybit' or 'hyperliquid'
        account_type: 'demo', 'real', or 'testnet'
    
    Returns:
        List of Position objects
    """
    try:
        from core.exchange_client import get_exchange_client
        client = await get_exchange_client(user_id, exchange_type=exchange, account_type=account_type)
        
        result = await client.get_positions(symbol=symbol)
        
        # Handle different return types - could be list directly or dict with 'data' key
        if isinstance(result, list):
            # Result is already a list of Position objects or dicts
            raw_positions = result
        elif isinstance(result, dict):
            if not result.get('success'):
                logger.error(f"Positions fetch failed: {result.get('error')}")
                return []
            raw_positions = result.get('data', [])
        else:
            logger.error(f"Unexpected result type from get_positions: {type(result)}")
            return []
        
        positions = []
        for pos_dict in raw_positions:
            # If already Position objects, use them
            if isinstance(pos_dict, Position):
                positions.append(pos_dict)
            else:
                # Convert dict to Position
                positions.append(Position(
                    symbol=pos_dict['symbol'],
                    side=pos_dict['side'],
                    size=float(pos_dict['size']),
                    entry_price=float(pos_dict['entry_price']),
                    mark_price=float(pos_dict.get('mark_price', pos_dict['entry_price'])),
                    unrealized_pnl=float(pos_dict.get('unrealized_pnl', 0)),
                    leverage=int(pos_dict.get('leverage', 1)),
                    margin_mode=pos_dict.get('margin_mode', 'cross'),
                    margin_used=float(pos_dict.get('margin_used', 0)),
                    liquidation_price=float(pos_dict['liquidation_price']) if pos_dict.get('liquidation_price') else None
                ))
        
        return positions
    except Exception as e:
        logger.error(f"get_positions_unified error for user {user_id}: {e}")
        count_errors('bot.get_positions')
        return []


# ═══════════════════════════════════════════════════════════════
# 3. PLACE ORDER
# ═══════════════════════════════════════════════════════════════

@track_latency(name='bot.place_order')
async def place_order_unified(
    user_id: int,
    symbol: str,
    side: str,  # 'Buy' or 'Sell'
    order_type: str,  # 'Market' or 'Limit'
    qty: float,
    price: Optional[float] = None,
    leverage: int = 10,
    take_profit: Optional[float] = None,
    stop_loss: Optional[float] = None,
    exchange: str = 'bybit',
    account_type: str = 'demo',
    strategy: str = 'manual'
) -> Dict[str, Any]:
    """
    Place order using unified client
    
    Args:
        user_id: Telegram user ID
        symbol: Trading pair (e.g. 'BTCUSDT')
        side: 'Buy' or 'Sell'
        order_type: 'Market' or 'Limit'
        qty: Order quantity
        price: Limit price (required for Limit orders)
        leverage: Position leverage
        take_profit: TP price (optional)
        stop_loss: SL price (optional)
        exchange: 'bybit' or 'hyperliquid'
        account_type: 'demo', 'real', or 'testnet'
        strategy: Strategy name for tracking
    
    Returns:
        Dict with success status and order details
    """
    try:
        from core.exchange_client import get_exchange_client
        
        # Normalize inputs
        symbol = normalize_symbol(symbol)
        order_side = OrderSide.from_string(side)
        order_type_enum = OrderType.from_string(order_type)
        
        # Get exchange client
        client = await get_exchange_client(user_id, exchange_type=exchange, account_type=account_type)
        
        # Set leverage first
        await client.set_leverage(symbol, leverage)
        
        # Place order
        result = await client.place_order(
            symbol=symbol,
            side=order_side,
            order_type=order_type_enum,
            quantity=qty,
            price=price
        )
        
        # Handle different return types - OrderResult object or dict
        if isinstance(result, OrderResult):
            if not result.success:
                logger.error(f"Order placement failed: {result.error}")
                return {
                    'success': False,
                    'error': result.error
                }
            order_id = result.order_id
            order_data = {
                'order_id': result.order_id,
                'avg_price': result.avg_price
            }
        elif isinstance(result, dict):
            if not result.get('success'):
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Order placement failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }
            order_data = result.get('data', {})
            order_id = order_data.get('order_id')
        else:
            logger.error(f"Unexpected result type from place_order: {type(result)}")
            return {
                'success': False,
                'error': 'Unexpected response type'
            }
        
        # Set TP/SL if provided
        if take_profit or stop_loss:
            try:
                await client.set_tp_sl(
                    symbol=symbol,
                    take_profit=take_profit,
                    stop_loss=stop_loss
                )
            except Exception as e:
                logger.warning(f"Failed to set TP/SL: {e}")
        
        # Save to database
        db.add_active_position(
            user_id=user_id,
            symbol=symbol,
            side=side,
            entry_price=price or order_data.get('avg_price', 0),
            size=qty,
            strategy=strategy,
            account_type=account_type
        )
        
        return {
            'success': True,
            'order_id': order_id,
            'symbol': symbol,
            'side': side,
            'qty': qty,
            'price': order_data.get('avg_price'),
            'data': order_data
        }
        
    except Exception as e:
        logger.error(f"place_order_unified error for user {user_id}: {e}")
        count_errors('bot.place_order')
        return {
            'success': False,
            'error': str(e)
        }


# ═══════════════════════════════════════════════════════════════
# 4. CLOSE POSITION
# ═══════════════════════════════════════════════════════════════

@track_latency(name='bot.close_position')
async def close_position_unified(
    user_id: int,
    symbol: str,
    qty: Optional[float] = None,
    exchange: str = 'bybit',
    account_type: str = 'demo'
) -> Dict[str, Any]:
    """
    Close position using unified client
    
    Args:
        user_id: Telegram user ID
        symbol: Trading pair
        qty: Quantity to close (None = close all)
        exchange: 'bybit' or 'hyperliquid'
        account_type: 'demo', 'real', or 'testnet'
    
    Returns:
        Dict with success status
    """
    try:
        from core.exchange_client import get_exchange_client
        
        symbol = normalize_symbol(symbol)
        client = await get_exchange_client(user_id, exchange_type=exchange, account_type=account_type)
        
        # Get current position
        positions = await get_positions_unified(user_id, symbol=symbol, exchange=exchange, account_type=account_type)
        if not positions:
            return {
                'success': False,
                'error': f'No open position for {symbol}'
            }
        
        position = positions[0]
        close_qty = qty if qty else position.size
        
        # Determine close side (opposite of position)
        close_side = OrderSide.SELL if position.is_long else OrderSide.BUY
        
        # Place closing order
        result = await client.place_order(
            symbol=symbol,
            side=close_side,
            order_type=OrderType.MARKET,
            quantity=close_qty,
            reduce_only=True
        )
        
        # Handle different return types
        success = False
        error = None
        if isinstance(result, OrderResult):
            success = result.success
            error = result.error if not success else None
        elif isinstance(result, dict):
            success = result.get('success', False)
            error = result.get('error', 'Failed to close position')
        elif isinstance(result, bool):
            success = result
        
        if not success:
            return {
                'success': False,
                'error': error or 'Failed to close position'
            }
        
        # Remove from database
        db.remove_active_position(user_id, symbol)
        
        # Log trade
        # Log trade
        pnl = position.unrealized_pnl * (close_qty / position.size)
        
        # Get strategy from active positions
        positions = db.get_active_positions(user_id)
        strategy = 'unknown'
        for pos in positions:
            if pos['symbol'] == symbol:
                strategy = pos.get('strategy', 'unknown')
                break
        
        db.add_trade_log(
            user_id=user_id,
            signal_id=None,
            symbol=symbol,
            side=position.side.value,
            entry_price=position.entry_price,
            exit_price=position.mark_price,
            exit_reason='manual_close',
            pnl=pnl,
            pnl_pct=(pnl / (position.entry_price * close_qty)) * 100 if position.entry_price > 0 else 0,
            strategy=strategy
        )
        
        return {
            'success': True,
            'symbol': symbol,
            'qty': close_qty,
            'pnl': pnl
        }
        
    except Exception as e:
        logger.error(f"close_position_unified error for user {user_id}: {e}")
        count_errors('bot.close_position')
        return {
            'success': False,
            'error': str(e)
        }


# ═══════════════════════════════════════════════════════════════
# 5. SET LEVERAGE
# ═══════════════════════════════════════════════════════════════

@track_latency(name='bot.set_leverage')
async def set_leverage_unified(
    user_id: int,
    symbol: str,
    leverage: int,
    exchange: str = 'bybit',
    account_type: str = 'demo'
) -> bool:
    """
    Set leverage using unified client
    
    Args:
        user_id: Telegram user ID
        symbol: Trading pair
        leverage: Leverage value (1-100)
        exchange: 'bybit' or 'hyperliquid'
        account_type: 'demo', 'real', or 'testnet'
    
    Returns:
        True if successful
    """
    try:
        from core.exchange_client import get_exchange_client
        
        symbol = normalize_symbol(symbol)
        client = await get_exchange_client(user_id, exchange_type=exchange, account_type=account_type)
        
        result = await client.set_leverage(symbol, leverage)
        
        # Handle different return types
        if isinstance(result, bool):
            return result
        elif isinstance(result, dict):
            return result.get('success', False)
        else:
            return False
        
    except Exception as e:
        logger.error(f"set_leverage_unified error for user {user_id}: {e}")
        count_errors('bot.set_leverage')
        return False


# Compatibility functions for gradual migration
async def get_balance(user_id: int, account_type: str = 'demo') -> Optional[Balance]:
    """Alias for backward compatibility"""
    return await get_balance_unified(user_id, account_type)


async def get_positions(user_id: int, symbol: Optional[str] = None) -> List[Position]:
    """Alias for backward compatibility"""
    return await get_positions_unified(user_id, symbol)


async def place_order(
    user_id: int,
    symbol: str,
    side: str,
    orderType: str,
    qty: float,
    price: Optional[float] = None,
    account_type: str = 'demo',
    **kwargs
) -> Dict[str, Any]:
    """Alias for backward compatibility with old bot.py signature"""
    return await place_order_unified(
        user_id=user_id,
        symbol=symbol,
        side=side,
        order_type=orderType,
        qty=qty,
        price=price,
        account_type=account_type,
        leverage=kwargs.get('leverage', 10),
        take_profit=kwargs.get('take_profit'),
        stop_loss=kwargs.get('stop_loss'),
        strategy=kwargs.get('strategy', 'manual')
    )
