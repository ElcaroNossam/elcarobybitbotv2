"""
Trade Execution Tasks
=====================
Distributed trade execution with rate limiting and retries.
"""

from celery import shared_task
from typing import Dict, Any, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=2,
    rate_limit='10/s',  # Max 10 trades per second globally
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=30
)
def execute_trade(
    self, 
    user_id: int, 
    signal_id: int, 
    signal: Dict[str, Any]
):
    """
    Execute trade for user based on signal.
    
    Args:
        user_id: User ID
        signal_id: Signal ID from DB
        signal: Signal data
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _async_execute_trade(user_id, signal_id, signal)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Trade execution failed for user {user_id}: {exc}")
        raise self.retry(exc=exc)


async def _async_execute_trade(
    user_id: int, 
    signal_id: int, 
    signal: Dict[str, Any]
) -> Dict[str, Any]:
    """Async trade execution"""
    from core.db_async import get_user_config, get_trading_mode, add_active_position
    from core.redis_client import get_redis
    
    symbol = signal.get("symbol")
    side = signal.get("side")
    strategy = signal.get("strategy")
    
    logger.info(f"Executing trade for user {user_id}: {symbol} {side}")
    
    # Get user config
    config = await get_user_config(user_id)
    if not config:
        return {"success": False, "error": "User not found"}
    
    # Check rate limit
    redis = await get_redis()
    if not await redis.rate_limit(user_id, action="trade", limit=10, window=60):
        return {"success": False, "error": "Rate limited"}
    
    # Get trading mode
    mode = await get_trading_mode(user_id)
    account_types = ["demo"] if mode == "demo" else ["real"] if mode == "real" else ["demo", "real"]
    
    results = []
    
    for account_type in account_types:
        try:
            # Acquire distributed lock to prevent duplicate trades
            lock_key = f"trade:{user_id}:{symbol}:{account_type}"
            if not await redis.acquire_lock(lock_key, timeout=10, blocking=False):
                logger.warning(f"Trade lock held for {user_id}:{symbol}:{account_type}")
                continue
            
            try:
                result = await _execute_single_trade(
                    user_id, 
                    symbol, 
                    side, 
                    strategy,
                    account_type,
                    config,
                    signal
                )
                results.append(result)
            finally:
                await redis.release_lock(lock_key)
                
        except Exception as e:
            logger.error(f"Trade failed for {user_id}:{symbol}:{account_type}: {e}")
            results.append({
                "account_type": account_type,
                "success": False,
                "error": str(e)
            })
    
    return {
        "user_id": user_id,
        "symbol": symbol,
        "results": results
    }


async def _execute_single_trade(
    user_id: int,
    symbol: str,
    side: str,
    strategy: str,
    account_type: str,
    config: Dict,
    signal: Dict
) -> Dict[str, Any]:
    """Execute a single trade on one account"""
    from bot_unified import place_order_unified, set_leverage_unified
    from core.db_async import add_active_position, get_user_credentials
    from models import OrderType, OrderSide
    
    # Get credentials
    creds = await get_user_credentials(user_id, account_type)
    if not creds:
        return {
            "account_type": account_type,
            "success": False,
            "error": "No credentials"
        }
    
    # Get user settings
    entry_pct = config.get("percent", 1.0)
    sl_pct = config.get("sl_percent", 3.0)
    tp_pct = config.get("tp_percent", 8.0)
    
    # Strategy-specific settings
    strategy_settings = config.get("strategy_settings") or {}
    if strategy in strategy_settings:
        strat_cfg = strategy_settings[strategy]
        entry_pct = strat_cfg.get("entry_pct", entry_pct)
        sl_pct = strat_cfg.get("sl_pct", sl_pct)
        tp_pct = strat_cfg.get("tp_pct", tp_pct)
    
    # Set leverage
    leverage = 50  # Default, will fallback automatically
    try:
        await set_leverage_unified(user_id, symbol, leverage, account_type)
    except Exception as e:
        logger.warning(f"Leverage set failed, will use default: {e}")
    
    # Calculate position size
    from core.redis_client import get_redis
    redis = await get_redis()
    current_price = await redis.get_price(symbol) or signal.get("entry_price", 0)
    
    if not current_price:
        return {
            "account_type": account_type,
            "success": False,
            "error": "Could not get current price"
        }
    
    # Get balance for position sizing
    from bot_unified import get_balance_unified
    balance = await get_balance_unified(user_id, account_type=account_type)
    
    if not balance or balance.equity <= 0:
        return {
            "account_type": account_type,
            "success": False,
            "error": "No balance"
        }
    
    # Calculate qty using risk-based sizing
    risk_usdt = balance.equity * (entry_pct / 100)
    price_move = current_price * (sl_pct / 100)
    qty = risk_usdt / price_move if price_move > 0 else 0
    
    if qty <= 0:
        return {
            "account_type": account_type,
            "success": False,
            "error": "Invalid quantity calculated"
        }
    
    # Normalize side
    order_side = OrderSide.BUY if side in ["Buy", "Long"] else OrderSide.SELL
    
    # Place order
    try:
        order_result = await place_order_unified(
            user_id=user_id,
            symbol=symbol,
            side=order_side,
            order_type=OrderType.MARKET,
            qty=qty,
            account_type=account_type
        )
        
        if not order_result:
            return {
                "account_type": account_type,
                "success": False,
                "error": "Order placement returned None"
            }
        
        # Calculate SL/TP prices
        if order_side == OrderSide.BUY:
            sl_price = current_price * (1 - sl_pct / 100)
            tp_price = current_price * (1 + tp_pct / 100)
        else:
            sl_price = current_price * (1 + sl_pct / 100)
            tp_price = current_price * (1 - tp_pct / 100)
        
        # Save position to DB
        await add_active_position(
            user_id=user_id,
            symbol=symbol,
            side=side,
            entry_price=current_price,
            size=qty,
            strategy=strategy,
            account_type=account_type,
            leverage=leverage,
            sl_price=sl_price,
            tp_price=tp_price,
            exchange="bybit"  # tasks/trades.py is Bybit-only for now
        )
        
        return {
            "account_type": account_type,
            "success": True,
            "order_id": getattr(order_result, 'order_id', None),
            "entry_price": current_price,
            "qty": qty,
            "sl_price": sl_price,
            "tp_price": tp_price
        }
        
    except Exception as e:
        logger.error(f"Order placement failed: {e}")
        return {
            "account_type": account_type,
            "success": False,
            "error": str(e)
        }


@shared_task(
    bind=True,
    max_retries=3,
    rate_limit='10/s'
)
def execute_close_position(
    self,
    user_id: int,
    symbol: str,
    account_type: str,
    reason: str,
    exit_price: float
):
    """Close position and log trade"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _async_close_position(user_id, symbol, account_type, reason, exit_price)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Close position failed: {exc}")
        raise self.retry(exc=exc)


async def _async_close_position(
    user_id: int,
    symbol: str,
    account_type: str,
    reason: str,
    exit_price: float,
    exchange: str = "bybit"
) -> Dict[str, Any]:
    """Async position close with multitenancy support"""
    from core.db_async import get_active_positions, remove_active_position, add_trade_log
    from bot_unified import close_position_unified
    
    # Get position data with exchange filter
    positions = await get_active_positions(user_id, account_type, exchange=exchange)
    position = next((p for p in positions if p["symbol"] == symbol), None)
    
    if not position:
        return {"success": False, "error": "Position not found"}
    
    entry_price = position["entry_price"]
    size = position["size"]
    side = position["side"]
    strategy = position.get("strategy", "unknown")
    exchange = position.get("exchange", exchange)
    
    # Close on exchange
    try:
        await close_position_unified(user_id, symbol, account_type=account_type)
    except Exception as e:
        logger.error(f"Exchange close failed: {e}")
        # Continue to log the trade anyway
    
    # Calculate PnL
    if side == "Buy":
        pnl = (exit_price - entry_price) * size
        pnl_pct = (exit_price - entry_price) / entry_price * 100
    else:
        pnl = (entry_price - exit_price) * size
        pnl_pct = (entry_price - exit_price) / entry_price * 100
    
    # Log trade with exchange
    await add_trade_log(
        user_id=user_id,
        symbol=symbol,
        side=side,
        entry_price=entry_price,
        exit_price=exit_price,
        exit_reason=reason,
        pnl=pnl,
        pnl_pct=pnl_pct,
        strategy=strategy,
        account_type=account_type,
        exchange=exchange
    )
    
    # Remove from active positions with exchange
    await remove_active_position(user_id, symbol, account_type, exchange=exchange)
    
    # Send notification
    from tasks.notifications import send_close_notification
    send_close_notification.apply_async(
        args=[user_id, symbol, side, entry_price, exit_price, pnl, reason],
        queue='notifications'
    )
    
    return {
        "success": True,
        "symbol": symbol,
        "pnl": pnl,
        "pnl_pct": pnl_pct,
        "reason": reason
    }


@shared_task(bind=True, rate_limit='10/s')
def update_stop_loss(
    self,
    user_id: int,
    symbol: str,
    new_sl: float,
    account_type: str
):
    """Update stop loss on exchange"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Update on exchange
            # This would call the exchange API
            logger.info(f"Updating SL for {user_id}:{symbol} to {new_sl}")
            
            # Update in DB
            from core.db_async import get_pool
            # Determine exchange from account_type for multitenancy
            exchange_for_db = 'hyperliquid' if account_type in ('testnet', 'mainnet') else 'bybit'
            async def update_sl():
                async with (await get_pool()).acquire() as conn:
                    await conn.execute("""
                        UPDATE active_positions 
                        SET sl_price = $1 
                        WHERE user_id = $2 AND symbol = $3 AND account_type = $4 AND exchange = $5
                    """, new_sl, user_id, symbol, account_type, exchange_for_db)
            
            loop.run_until_complete(update_sl())
            
            return {"success": True, "new_sl": new_sl}
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Update SL failed: {e}")
        return {"success": False, "error": str(e)}


@shared_task(bind=True)
def cleanup_expired_orders(self):
    """Remove expired limit orders"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async def cleanup():
                from core.db_async import get_pool
                async with (await get_pool()).acquire() as conn:
                    result = await conn.execute("""
                        DELETE FROM pending_limit_orders 
                        WHERE created_at < NOW() - INTERVAL '24 hours'
                    """)
                    return result
            
            result = loop.run_until_complete(cleanup())
            logger.info(f"Cleaned up expired orders: {result}")
            return {"success": True}
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return {"success": False, "error": str(e)}
