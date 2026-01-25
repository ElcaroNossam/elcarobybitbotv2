"""
Position Monitoring Tasks
=========================
Distributed position monitoring with user sharding.

Sharding Strategy:
- Users are divided into N shards based on user_id % SHARD_COUNT
- Each shard is processed by a separate Celery worker
- This allows parallel monitoring of 10K+ users
"""

from celery import shared_task
from typing import List, Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

# Number of shards (workers)
SHARD_COUNT = 10


def get_user_shard(user_id: int) -> int:
    """Get shard ID for user"""
    return user_id % SHARD_COUNT


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    autoretry_for=(Exception,),
    retry_backoff=True
)
def monitor_user_positions(self, user_ids: List[int]):
    """
    Monitor positions for a list of users (one shard).
    
    Args:
        user_ids: List of user IDs to monitor
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_async_monitor_positions(user_ids))
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Position monitoring failed for {len(user_ids)} users: {exc}")
        raise self.retry(exc=exc)


async def _async_monitor_positions(user_ids: List[int]) -> Dict[str, Any]:
    """Async position monitoring implementation"""
    from core.db_async import get_active_positions
    from core.redis_client import get_redis
    
    redis = await get_redis()
    
    results = {
        "users_processed": 0,
        "positions_checked": 0,
        "sl_triggered": 0,
        "tp_triggered": 0,
        "atr_updated": 0,
        "errors": []
    }
    
    for user_id in user_ids:
        try:
            # Get positions from DB - get all positions across exchanges
            # In monitoring, we process ALL positions regardless of exchange
            positions = await get_active_positions(user_id)
            
            for pos in positions:
                symbol = pos["symbol"]
                entry_price = pos["entry_price"]
                side = pos["side"]
                sl_price = pos.get("sl_price")
                tp_price = pos.get("tp_price")
                
                # Get current price from Redis cache
                current_price = await redis.get_price(symbol)
                
                if not current_price:
                    continue
                
                results["positions_checked"] += 1
                
                # Check SL/TP triggers
                if side == "Buy":
                    if sl_price and current_price <= sl_price:
                        await _trigger_close(user_id, symbol, pos, "SL", current_price)
                        results["sl_triggered"] += 1
                    elif tp_price and current_price >= tp_price:
                        await _trigger_close(user_id, symbol, pos, "TP", current_price)
                        results["tp_triggered"] += 1
                else:  # Sell
                    if sl_price and current_price >= sl_price:
                        await _trigger_close(user_id, symbol, pos, "SL", current_price)
                        results["sl_triggered"] += 1
                    elif tp_price and current_price <= tp_price:
                        await _trigger_close(user_id, symbol, pos, "TP", current_price)
                        results["tp_triggered"] += 1
                
                # ATR trailing update
                await _check_atr_trailing(user_id, pos, current_price)
            
            results["users_processed"] += 1
            
        except Exception as e:
            results["errors"].append(f"User {user_id}: {str(e)}")
            logger.error(f"Error monitoring user {user_id}: {e}")
    
    return results


async def _trigger_close(
    user_id: int, 
    symbol: str, 
    position: Dict, 
    reason: str,
    current_price: float
):
    """Trigger position close via trade task"""
    from tasks.trades import execute_close_position
    
    # Queue the close trade
    execute_close_position.apply_async(
        args=[user_id, symbol, position["account_type"], reason, current_price],
        queue='trades'
    )


async def _check_atr_trailing(user_id: int, position: Dict, current_price: float):
    """Check and update ATR trailing stop"""
    # Import here to avoid circular imports
    from core.db_async import set_user_field
    
    entry_price = position["entry_price"]
    side = position["side"]
    current_sl = position.get("sl_price")
    
    if not current_sl:
        return
    
    # Calculate move percentage
    if side == "Buy":
        move_pct = (current_price - entry_price) / entry_price * 100
        # Update trailing stop if price moved favorably
        if move_pct > 3.0:  # Trigger threshold
            new_sl = current_price * 0.97  # 3% below current
            if new_sl > current_sl:
                await _update_trailing_stop(user_id, position, new_sl)
    else:
        move_pct = (entry_price - current_price) / entry_price * 100
        if move_pct > 3.0:
            new_sl = current_price * 1.03  # 3% above current
            if new_sl < current_sl:
                await _update_trailing_stop(user_id, position, new_sl)


async def _update_trailing_stop(user_id: int, position: Dict, new_sl: float):
    """Update trailing stop on exchange"""
    from tasks.trades import update_stop_loss
    
    update_stop_loss.apply_async(
        args=[
            user_id, 
            position["symbol"], 
            new_sl,
            position["account_type"]
        ],
        queue='trades'
    )


@shared_task(bind=True)
def monitor_all_positions(self):
    """
    Distribute position monitoring across shards.
    Called periodically by Celery Beat.
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_distribute_monitoring())
            return result
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Failed to distribute monitoring: {e}")
        raise


async def _distribute_monitoring() -> Dict[str, int]:
    """Distribute users across shards and dispatch tasks"""
    from core.db_async import get_active_trading_users
    
    # Get all active users
    users = await get_active_trading_users()
    
    if not users:
        return {"users": 0, "shards": 0}
    
    # Group users by shard
    shards: Dict[int, List[int]] = {}
    for uid in users:
        shard_id = get_user_shard(uid)
        if shard_id not in shards:
            shards[shard_id] = []
        shards[shard_id].append(uid)
    
    # Dispatch tasks for each shard
    for shard_id, shard_users in shards.items():
        monitor_user_positions.apply_async(
            args=[shard_users],
            queue=f'positions',
            routing_key=f'positions.shard.{shard_id}'
        )
    
    logger.info(f"Distributed {len(users)} users across {len(shards)} shards")
    
    return {
        "users": len(users),
        "shards": len(shards)
    }


@shared_task(bind=True)
def sync_exchange_positions(self):
    """
    Sync positions from exchange to database.
    Detects positions opened/closed outside the bot.
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_sync_all_positions())
            return result
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Position sync failed: {e}")
        raise


async def _sync_all_positions() -> Dict[str, int]:
    """Sync positions for all users"""
    from core.db_async import get_active_trading_users, get_active_positions
    from core.db_async import add_active_position, remove_active_position
    
    users = await get_active_trading_users()
    
    synced = 0
    removed = 0
    errors = 0
    
    for user_id in users:
        try:
            # Get positions from exchange
            exchange_positions = await _fetch_exchange_positions(user_id)
            
            # Get positions from DB - get exchange from position data
            # Note: We process each exchange separately
            db_positions = await get_active_positions(user_id)
            db_keys = {(p["symbol"], p["account_type"], p.get("exchange", "bybit")) for p in db_positions}
            
            # Sync new positions from exchange
            for pos in exchange_positions:
                exchange = pos.get("exchange", "bybit")
                key = (pos["symbol"], pos["account_type"], exchange)
                if key not in db_keys:
                    await add_active_position(
                        user_id=user_id,
                        symbol=pos["symbol"],
                        side=pos["side"],
                        entry_price=pos["entry_price"],
                        size=pos["size"],
                        strategy="external",
                        account_type=pos["account_type"],
                        exchange=exchange
                    )
                    synced += 1
            
            # Remove positions that no longer exist on exchange
            exchange_keys = {(p["symbol"], p["account_type"], p.get("exchange", "bybit")) for p in exchange_positions}
            for db_pos in db_positions:
                key = (db_pos["symbol"], db_pos["account_type"], db_pos.get("exchange", "bybit"))
                if key not in exchange_keys:
                    await remove_active_position(
                        user_id, 
                        db_pos["symbol"], 
                        db_pos["account_type"],
                        exchange=db_pos.get("exchange", "bybit")
                    )
                    removed += 1
                    
        except Exception as e:
            logger.error(f"Sync failed for user {user_id}: {e}")
            errors += 1
    
    return {
        "synced": synced,
        "removed": removed,
        "errors": errors
    }


async def _fetch_exchange_positions(user_id: int) -> List[Dict]:
    """Fetch positions from exchange API"""
    # Import exchange client
    from core.db_async import get_trading_mode, get_user_credentials
    
    positions = []
    
    # Get trading mode
    mode = await get_trading_mode(user_id)
    account_types = ["demo"] if mode == "demo" else ["real"] if mode == "real" else ["demo", "real"]
    
    for account_type in account_types:
        creds = await get_user_credentials(user_id, account_type)
        if not creds:
            continue
        
        try:
            # Use unified fetch
            from bot_unified import get_positions_unified
            
            exchange_positions = await get_positions_unified(
                user_id, 
                account_type=account_type
            )
            
            for pos in exchange_positions:
                positions.append({
                    "symbol": pos.symbol,
                    "side": pos.side.value,
                    "entry_price": pos.entry_price,
                    "size": pos.size,
                    "account_type": account_type
                })
                
        except Exception as e:
            logger.error(f"Failed to fetch positions for {user_id} {account_type}: {e}")
    
    return positions
