"""
Unified Trading Functions - Drop-in replacements for bot.py

These functions use the new unified architecture:
- models/unified.py for data models
- core/exchange_client.py for exchange routing
- Proper error handling and logging

Replace old bot.py functions with these.
"""
import logging
import time
from typing import Optional, List, Dict, Any, Tuple
from models import Position, Order, Balance, OrderResult, OrderSide, OrderType, PositionSide, normalize_symbol
from core import get_exchange_client, track_latency, count_errors
import db

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# HYPERLIQUID CACHE - Prevent rate limiting (429 errors)
# HyperLiquid has strict rate limits: 1200 weight/minute, info requests = 20 weight
# This means ~60 info requests/minute MAX
# Cache positions/balance for 60 seconds to avoid rate limits
# CHECK_INTERVAL = 15s, so with 180s cache we only make 1 API call per 3 minutes per user
# ═══════════════════════════════════════════════════════════════
_hl_cache: Dict[str, Tuple[Any, float, float]] = {}  # key -> (data, timestamp, ttl)
HL_CACHE_TTL = 180  # seconds - cache HyperLiquid data for 180 seconds (3 minutes to avoid rate limits)
HL_CACHE_ERROR_TTL = 30  # seconds - shorter cache for error results to allow recovery


def _get_hl_cache(key: str) -> Optional[Any]:
    """Get cached HyperLiquid data if not expired"""
    if key in _hl_cache:
        entry = _hl_cache[key]
        # Support both old (data, ts) and new (data, ts, ttl) format
        if len(entry) == 3:
            data, ts, ttl = entry
        else:
            data, ts = entry
            ttl = HL_CACHE_TTL
        age = time.time() - ts
        if age < ttl:
            logger.debug(f"HL_CACHE HIT: {key} (age={age:.1f}s, ttl={ttl}s)")
            return data
        else:
            logger.debug(f"HL_CACHE EXPIRED: {key} (age={age:.1f}s > TTL={ttl}s)")
    else:
        logger.debug(f"HL_CACHE MISS: {key} (key not in cache)")
    return None


def _set_hl_cache(key: str, data: Any, ttl: float = None):
    """Set HyperLiquid cache with current timestamp and optional TTL"""
    cache_ttl = ttl if ttl is not None else HL_CACHE_TTL
    _hl_cache[key] = (data, time.time(), cache_ttl)
    logger.debug(f"HL_CACHE SET: {key} (items={len(data) if isinstance(data, list) else 'N/A'}, ttl={cache_ttl}s)")


def invalidate_hl_cache(user_id: int, account_type: str = None):
    """
    Invalidate HyperLiquid cache for a user.
    Call this after placing/closing orders to refresh data.
    """
    keys_to_remove = []
    prefix = f"positions:{user_id}:" if account_type is None else f"positions:{user_id}:{account_type}"
    balance_prefix = f"balance:{user_id}:" if account_type is None else f"balance:{user_id}:{account_type}"
    
    for key in _hl_cache.keys():
        if key.startswith(prefix) or key.startswith(balance_prefix):
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del _hl_cache[key]
    
    if keys_to_remove:
        logger.debug(f"[HL-CACHE] Invalidated cache for user {user_id}: {keys_to_remove}")


from core.account_utils import normalize_account_type as _normalize_both_account_type


# ═══════════════════════════════════════════════════════════════
# 1. GET BALANCE
# ═══════════════════════════════════════════════════════════════

@track_latency(name='bot.get_balance')
async def get_balance_unified(user_id: int, exchange: str = 'bybit', account_type: str = 'demo', use_cache: bool = True) -> Optional[Balance]:
    """
    Get user balance using unified client
    
    Args:
        user_id: Telegram user ID
        exchange: 'bybit' or 'hyperliquid'
        account_type: 'demo', 'real', or 'testnet'
        use_cache: Use cache for HyperLiquid (default True to avoid rate limits)
    
    Returns:
        Balance object or None if error
    """
    # Normalize 'both' -> 'demo'/'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange)
    
    # Check HyperLiquid cache to avoid rate limits
    if exchange == 'hyperliquid' and use_cache:
        cache_key = f"balance:{user_id}:{account_type}"
        cached = _get_hl_cache(cache_key)
        if cached is not None:
            return cached
    
    client = None
    try:
        from core.exchange_client import get_exchange_client
        client = await get_exchange_client(user_id, exchange_type=exchange, account_type=account_type)
        
        result = await client.get_balance()
        
        # Handle different return types - could be Balance object directly or dict
        balance = None
        if isinstance(result, Balance):
            balance = result
        elif isinstance(result, dict):
            if not result.get('success'):
                logger.error(f"Balance fetch failed: {result.get('error')}")
                return None
            
            data = result.get('data', result)
            # HLAdapter returns 'equity'/'available', Bybit returns 'total_equity'/'available_balance'
            balance = Balance(
                total_equity=data.get('equity') or data.get('total_equity') or 0,
                available_balance=data.get('available') or data.get('available_balance') or 0,
                margin_used=data.get('margin_used', 0),
                unrealized_pnl=data.get('unrealized_pnl', 0),
                currency=data.get('currency', 'USDT')
            )
        else:
            logger.error(f"Unexpected result type from get_balance: {type(result)}")
            return None
        
        # Cache HyperLiquid result
        if exchange == 'hyperliquid' and balance is not None:
            cache_key = f"balance:{user_id}:{account_type}"
            _set_hl_cache(cache_key, balance)
        
        return balance
    except Exception as e:
        error_str = str(e)
        # Don't log cached auth errors at ERROR level - they are expected
        if "cached" in error_str.lower() or "retry in" in error_str:
            logger.debug(f"get_balance_unified skipped for user {user_id}: {e}")
        else:
            logger.error(f"get_balance_unified error for user {user_id}: {e}")
            count_errors('bot.get_balance')
        return None
    # NOTE: Client is pooled - do NOT close it manually!


# ═══════════════════════════════════════════════════════════════
# 2. GET POSITIONS
# ═══════════════════════════════════════════════════════════════

def _safe_float(value, default=0.0):
    """Safely convert value to float, handling empty strings and None"""
    if value is None or value == '' or value == '0':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def _safe_int(value, default=0):
    """Safely convert value to int, handling empty strings and None"""
    if value is None or value == '' or value == '0':
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

@track_latency(name='bot.get_positions')
async def get_positions_unified(user_id: int, symbol: Optional[str] = None, exchange: str = 'bybit', account_type: str = 'demo', use_cache: bool = True) -> List[Position]:
    """
    Get user positions using unified client
    
    Args:
        user_id: Telegram user ID
        symbol: Optional symbol filter
        exchange: 'bybit' or 'hyperliquid'
        account_type: 'demo', 'real', or 'testnet'
        use_cache: Use cache for HyperLiquid (default True to avoid rate limits)
    
    Returns:
        List of Position objects
    """
    # Normalize 'both' -> 'demo'/'testnet' based on exchange
    account_type = _normalize_both_account_type(account_type, exchange)
    
    # Check HyperLiquid cache to avoid rate limits
    if exchange == 'hyperliquid' and use_cache and symbol is None:
        cache_key = f"positions:{user_id}:{account_type}"
        cached = _get_hl_cache(cache_key)
        if cached is not None:
            # "ERROR" sentinel means a recent API error — return None to signal error
            if cached == "ERROR":
                return None
            return cached  # Cache hit - no logging needed
    
    client = None
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
                # Convert dict to Position with safe parsing
                try:
                    # Convert side string to PositionSide enum
                    side_str = pos_dict.get('side', 'Buy')
                    if side_str in ('Buy', 'LONG', 'Long'):
                        side = PositionSide.LONG
                    elif side_str in ('Sell', 'SHORT', 'Short'):
                        side = PositionSide.SHORT
                    else:
                        side = PositionSide.NONE
                    
                    positions.append(Position(
                        symbol=pos_dict.get('symbol', ''),
                        side=side,
                        size=_safe_float(pos_dict.get('size')),
                        entry_price=_safe_float(pos_dict.get('entry_price')),
                        mark_price=_safe_float(pos_dict.get('mark_price', pos_dict.get('entry_price'))),
                        unrealized_pnl=_safe_float(pos_dict.get('unrealized_pnl')),
                        leverage=_safe_int(pos_dict.get('leverage'), 1),
                        margin_mode=pos_dict.get('margin_mode', 'cross'),
                        margin_used=_safe_float(pos_dict.get('margin_used')),
                        liquidation_price=_safe_float(pos_dict.get('liquidation_price')) if pos_dict.get('liquidation_price') else None,
                        stop_loss=_safe_float(pos_dict.get('stop_loss')) if pos_dict.get('stop_loss') else None,
                        take_profit=_safe_float(pos_dict.get('take_profit')) if pos_dict.get('take_profit') else None
                    ))
                except Exception as pos_err:
                    logger.warning(f"Skipping invalid position: {pos_err}, data: {pos_dict}")
                    continue
        
        # Cache HyperLiquid result (only if no symbol filter)
        # NOTE: Cache EMPTY lists too to avoid repeated API calls for users with no positions!
        if exchange == 'hyperliquid' and symbol is None:
            cache_key = f"positions:{user_id}:{account_type}"
            _set_hl_cache(cache_key, positions)
        
        return positions
    except Exception as e:
        error_str = str(e)
        # Don't log cached auth errors at ERROR level - they are expected
        if "cached" in error_str.lower() or "retry in" in error_str:
            logger.debug(f"get_positions_unified skipped for user {user_id}: {e}")
        else:
            logger.error(f"get_positions_unified error for user {user_id}: {e}")
            count_errors('bot.get_positions')
        
        # Cache error sentinel to avoid retry storm (429 causing more 429s)
        # Use shorter TTL for errors (30s) to allow recovery
        if exchange == 'hyperliquid' and symbol is None:
            cache_key = f"positions:{user_id}:{account_type}"
            _set_hl_cache(cache_key, "ERROR", ttl=HL_CACHE_ERROR_TTL)  # Cache error sentinel with short TTL
            logger.info(f"HL_CACHE SET (error fallback): {cache_key}")
        
        return None  # Return None to distinguish error from empty positions
    # NOTE: Client is pooled - do NOT close it manually!
    # The pool handles lifecycle automatically.


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
    client = None
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
            account_type=account_type,
            exchange=exchange
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
        error_str = str(e)
        # Don't log cached auth errors at ERROR level - they are expected
        if "cached" in error_str.lower() or "retry in" in error_str:
            logger.debug(f"place_order_unified skipped for user {user_id}: {e}")
        else:
            logger.error(f"place_order_unified error for user {user_id}: {e}")
            count_errors('bot.place_order')
        return {
            'success': False,
            'error': str(e)
        }
    # NOTE: Client is pooled - do NOT close it manually!


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
    client = None
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
        
        # Use the exchange parameter directly (already passed by caller)
        exchange_for_db = exchange or ('hyperliquid' if account_type in ('testnet', 'mainnet') else 'bybit')
        
        # CRITICAL: Read strategy from DB BEFORE removing the position!
        active_positions_for_strategy = db.get_active_positions(user_id, account_type=account_type, exchange=exchange_for_db)
        strategy = 'unknown'
        for pos in active_positions_for_strategy:
            if pos['symbol'] == symbol:
                strategy = pos.get('strategy', 'unknown')
                break
        
        # Now remove from database
        db.remove_active_position(user_id, symbol, account_type=account_type, exchange=exchange_for_db)
        
        # Log trade
        pnl = position.unrealized_pnl * (close_qty / position.size) if position.size > 0 else 0
        
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
            strategy=strategy,
            account_type=account_type,
            exchange=exchange_for_db
        )
        
        return {
            'success': True,
            'symbol': symbol,
            'qty': close_qty,
            'pnl': pnl
        }
        
    except Exception as e:
        error_str = str(e)
        # Don't log cached auth errors at ERROR level - they are expected
        if "cached" in error_str.lower() or "retry in" in error_str:
            logger.debug(f"close_position_unified skipped for user {user_id}: {e}")
        else:
            logger.error(f"close_position_unified error for user {user_id}: {e}")
            count_errors('bot.close_position')
        return {
            'success': False,
            'error': str(e)
        }
    # NOTE: Client is pooled - do NOT close it manually!


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
    client = None
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
        error_str = str(e)
        # Don't log cached auth errors at ERROR level - they are expected
        if "cached" in error_str.lower() or "retry in" in error_str:
            logger.debug(f"set_leverage_unified skipped for user {user_id}: {e}")
        else:
            logger.error(f"set_leverage_unified error for user {user_id}: {e}")
            count_errors('bot.set_leverage')
        return False
    # NOTE: Client is pooled - do NOT close it manually!


# Compatibility functions for gradual migration
async def get_balance(user_id: int, account_type: str = 'demo', exchange: str = 'bybit') -> Optional[Balance]:
    """Alias for backward compatibility"""
    return await get_balance_unified(user_id, exchange=exchange, account_type=account_type)


async def get_positions(user_id: int, symbol: Optional[str] = None, exchange: str = 'bybit', account_type: str = 'demo') -> List[Position]:
    """Alias for backward compatibility"""
    return await get_positions_unified(user_id, symbol, exchange=exchange, account_type=account_type)


async def place_order(
    user_id: int,
    symbol: str,
    side: str,
    orderType: str,
    qty: float,
    price: Optional[float] = None,
    account_type: str = 'demo',
    exchange: str = 'bybit',
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
        exchange=exchange,
        account_type=account_type,
        leverage=kwargs.get('leverage', 10),
        take_profit=kwargs.get('take_profit'),
        stop_loss=kwargs.get('stop_loss'),
        strategy=kwargs.get('strategy', 'manual')
    )
