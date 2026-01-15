"""
Notification Tasks
==================
Async notifications via Telegram, email, webhooks.
"""

from celery import shared_task
from typing import Dict, Any, List, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    rate_limit='50/s'
)
def send_close_notification(
    self,
    user_id: int,
    symbol: str,
    side: str,
    entry_price: float,
    exit_price: float,
    pnl: float,
    reason: str
):
    """Send trade close notification to user"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _async_send_close_notification(
                    user_id, symbol, side, entry_price, exit_price, pnl, reason
                )
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Notification failed for user {user_id}: {exc}")
        raise self.retry(exc=exc)


async def _async_send_close_notification(
    user_id: int,
    symbol: str,
    side: str,
    entry_price: float,
    exit_price: float,
    pnl: float,
    reason: str
) -> Dict[str, Any]:
    """Send notification via Telegram"""
    import os
    import aiohttp
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN not set")
        return {"success": False, "error": "No bot token"}
    
    # Format message
    pnl_emoji = "🟢" if pnl >= 0 else "🔴"
    pnl_formatted = f"+${pnl:.2f}" if pnl >= 0 else f"-${abs(pnl):.2f}"
    
    pnl_pct = (exit_price - entry_price) / entry_price * 100
    if side == "Sell":
        pnl_pct = -pnl_pct
    
    message = f"""
{pnl_emoji} <b>Position Closed</b>

📊 <b>{symbol}</b>
📍 Side: {side}
💰 Entry: ${entry_price:.4f}
🎯 Exit: ${exit_price:.4f}
📈 PnL: <b>{pnl_formatted}</b> ({pnl_pct:+.2f}%)
📝 Reason: {reason}
"""
    
    # Send via Telegram API
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={
            "chat_id": user_id,
            "text": message.strip(),
            "parse_mode": "HTML"
        }) as resp:
            result = await resp.json()
            
            if result.get("ok"):
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": result.get("description", "Unknown error")
                }


@shared_task(bind=True, rate_limit='50/s')
def send_signal_notification(
    self,
    user_id: int,
    signal: Dict[str, Any]
):
    """Send new signal notification"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _async_send_signal_notification(user_id, signal)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Signal notification failed: {exc}")
        raise self.retry(exc=exc)


async def _async_send_signal_notification(
    user_id: int,
    signal: Dict[str, Any]
) -> Dict[str, Any]:
    """Send signal notification"""
    import os
    import aiohttp
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        return {"success": False, "error": "No bot token"}
    
    symbol = signal.get("symbol")
    side = signal.get("side")
    strategy = signal.get("strategy")
    entry_price = signal.get("entry_price")
    
    side_emoji = "🟢" if side in ["Buy", "Long"] else "🔴"
    
    message = f"""
{side_emoji} <b>New Signal</b>

📊 <b>{symbol}</b>
📍 Side: {side}
🤖 Strategy: {strategy}
💰 Entry: ${entry_price:.4f} (approx)
"""
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={
            "chat_id": user_id,
            "text": message.strip(),
            "parse_mode": "HTML"
        }) as resp:
            result = await resp.json()
            return {"success": result.get("ok", False)}


@shared_task(bind=True)
def send_bulk_notification(
    self,
    user_ids: List[int],
    message: str,
    parse_mode: str = "HTML"
):
    """Send notification to multiple users"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _async_send_bulk(user_ids, message, parse_mode)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Bulk notification failed: {exc}")
        raise self.retry(exc=exc)


async def _async_send_bulk(
    user_ids: List[int],
    message: str,
    parse_mode: str
) -> Dict[str, Any]:
    """Send to multiple users with rate limiting"""
    import os
    import aiohttp
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        return {"success": False, "error": "No bot token"}
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    sent = 0
    failed = 0
    
    async with aiohttp.ClientSession() as session:
        for user_id in user_ids:
            try:
                async with session.post(url, json={
                    "chat_id": user_id,
                    "text": message,
                    "parse_mode": parse_mode
                }) as resp:
                    result = await resp.json()
                    if result.get("ok"):
                        sent += 1
                    else:
                        failed += 1
                
                # Rate limit: 30 messages per second
                await asyncio.sleep(0.035)
                
            except Exception as e:
                logger.error(f"Failed to send to {user_id}: {e}")
                failed += 1
    
    return {
        "sent": sent,
        "failed": failed,
        "total": len(user_ids)
    }


@shared_task(bind=True)
def send_admin_alert(self, message: str, level: str = "info"):
    """Send alert to admin"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            import os
            admin_id = int(os.getenv("ADMIN_ID", "511692487"))
            
            level_emoji = {
                "info": "ℹ️",
                "warning": "⚠️",
                "error": "🚨",
                "critical": "🔥"
            }.get(level, "ℹ️")
            
            full_message = f"{level_emoji} <b>Admin Alert</b>\n\n{message}"
            
            result = loop.run_until_complete(
                _async_send_bulk([admin_id], full_message, "HTML")
            )
            return result
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Admin alert failed: {e}")
        return {"success": False, "error": str(e)}


@shared_task(bind=True)
def send_webhook(
    self,
    url: str,
    payload: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None
):
    """Send webhook notification"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                _async_send_webhook(url, payload, headers)
            )
            return result
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Webhook failed: {exc}")
        raise self.retry(exc=exc)


async def _async_send_webhook(
    url: str,
    payload: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Send webhook"""
    import aiohttp
    
    headers = headers or {"Content-Type": "application/json"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            return {
                "success": resp.status < 400,
                "status_code": resp.status,
                "response": await resp.text()
            }
