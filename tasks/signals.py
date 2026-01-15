"""
Signal Processing Tasks
=======================
Distributed signal processing with parallel execution.
"""

from celery import shared_task, group, chain
from typing import Dict, Any, List
import asyncio
import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=2,
    rate_limit='100/s'
)
def process_signal(self, signal: Dict[str, Any]):
    """
    Process a trading signal for all subscribed users.
    
    Args:
        signal: Signal data with symbol, side, strategy, etc.
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_async_process_signal(signal))
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Signal processing failed: {exc}")
        raise self.retry(exc=exc)


async def _async_process_signal(signal: Dict[str, Any]) -> Dict[str, Any]:
    """Async signal processing implementation"""
    from core.db_async import get_subscribed_users, get_user_config
    from core.db_async import add_signal
    from core.redis_client import get_redis
    
    symbol = signal.get("symbol")
    side = signal.get("side")
    strategy = signal.get("strategy")
    entry_price = signal.get("entry_price")
    
    logger.info(f"Processing signal: {symbol} {side} {strategy}")
    
    # Save signal to DB
    signal_id = await add_signal(
        symbol=symbol,
        side=side,
        strategy=strategy,
        entry_price=entry_price,
        sl_price=signal.get("sl_price"),
        tp_price=signal.get("tp_price"),
        timeframe=signal.get("timeframe"),
        metadata=signal.get("metadata")
    )
    
    # Get users subscribed to this strategy
    users = await get_subscribed_users()
    
    # Filter users who have this strategy enabled
    eligible_users = []
    for user_id in users:
        config = await get_user_config(user_id)
        if not config:
            continue
        
        # Check if strategy is enabled
        strategy_field = f"trade_{strategy.lower()}"
        if config.get(strategy_field, 0) != 1:
            continue
        
        # Check coin filter
        coins = config.get("coins", "ALL")
        if coins != "ALL" and symbol.replace("USDT", "") not in coins:
            continue
        
        eligible_users.append(user_id)
    
    # Dispatch trade tasks for eligible users
    from tasks.trades import execute_trade
    
    trades_dispatched = 0
    for user_id in eligible_users:
        execute_trade.apply_async(
            args=[user_id, signal_id, signal],
            queue='trades'
        )
        trades_dispatched += 1
    
    # Publish to Redis for real-time subscribers
    redis = await get_redis()
    await redis.publish_signal({
        **signal,
        "signal_id": signal_id,
        "users_count": len(eligible_users)
    })
    
    return {
        "signal_id": signal_id,
        "users_eligible": len(eligible_users),
        "trades_dispatched": trades_dispatched
    }


@shared_task(bind=True)
def broadcast_signal(self, signal: Dict[str, Any]):
    """
    Broadcast signal to all workers via Redis pub/sub.
    Used for high-priority signals that need immediate processing.
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            from core.redis_client import get_redis
            redis = loop.run_until_complete(get_redis())
            loop.run_until_complete(redis.publish_signal(signal))
            return {"broadcasted": True}
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Failed to broadcast signal: {e}")
        return {"broadcasted": False, "error": str(e)}


@shared_task(bind=True)
def process_signal_batch(self, signals: List[Dict[str, Any]]):
    """
    Process a batch of signals.
    Used for bulk signal ingestion.
    """
    results = []
    
    # Create a group of signal processing tasks
    signal_tasks = group([
        process_signal.s(signal) for signal in signals
    ])
    
    # Execute all in parallel
    result = signal_tasks.apply_async()
    
    return {
        "signals_count": len(signals),
        "task_id": result.id
    }


@shared_task(bind=True)
def validate_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate signal before processing.
    Checks symbol validity, risk parameters, etc.
    """
    errors = []
    warnings = []
    
    # Required fields
    required = ["symbol", "side", "strategy"]
    for field in required:
        if field not in signal:
            errors.append(f"Missing required field: {field}")
    
    # Validate symbol
    symbol = signal.get("symbol", "")
    if symbol and not symbol.endswith("USDT"):
        warnings.append(f"Non-USDT symbol: {symbol}")
    
    # Validate side
    side = signal.get("side", "")
    if side not in ["Buy", "Sell", "Long", "Short"]:
        errors.append(f"Invalid side: {side}")
    
    # Validate strategy
    valid_strategies = ["scryptomera", "scalper", "elcaro", "fibonacci", "oi", "rsi_bb"]
    strategy = signal.get("strategy", "").lower()
    if strategy and strategy not in valid_strategies:
        errors.append(f"Unknown strategy: {strategy}")
    
    # Check entry price
    entry_price = signal.get("entry_price")
    if entry_price and entry_price <= 0:
        errors.append(f"Invalid entry price: {entry_price}")
    
    # Check SL/TP
    sl_price = signal.get("sl_price")
    tp_price = signal.get("tp_price")
    
    if entry_price and sl_price:
        sl_pct = abs(entry_price - sl_price) / entry_price * 100
        if sl_pct > 50:
            warnings.append(f"Large SL: {sl_pct:.1f}%")
    
    if entry_price and tp_price:
        tp_pct = abs(tp_price - entry_price) / entry_price * 100
        if tp_pct > 100:
            warnings.append(f"Large TP: {tp_pct:.1f}%")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "signal": signal
    }


@shared_task(bind=True)
def enrich_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich signal with additional data.
    Adds current price, ATR, volume, etc.
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(_async_enrich_signal(signal))
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Failed to enrich signal: {e}")
        return signal


async def _async_enrich_signal(signal: Dict[str, Any]) -> Dict[str, Any]:
    """Async signal enrichment"""
    from core.redis_client import get_redis
    
    symbol = signal.get("symbol")
    if not symbol:
        return signal
    
    enriched = signal.copy()
    
    # Get current price from Redis cache
    redis = await get_redis()
    current_price = await redis.get_price(symbol)
    
    if current_price:
        enriched["current_price"] = current_price
        
        # Calculate deviation from entry price
        entry_price = signal.get("entry_price")
        if entry_price:
            deviation = (current_price - entry_price) / entry_price * 100
            enriched["price_deviation_pct"] = round(deviation, 2)
    
    # Add timestamp
    import datetime
    enriched["enriched_at"] = datetime.datetime.utcnow().isoformat()
    
    return enriched
