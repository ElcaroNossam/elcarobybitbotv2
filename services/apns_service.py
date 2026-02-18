"""
Apple Push Notification Service (APNs) Integration
==================================================
JWT-based authentication for sending push notifications to iOS devices.

Features:
- Trade opened/closed notifications with rich content
- Daily trading digest with beautiful formatting
- Break-even and partial TP alerts
- Signal notifications

Author: Enliko Team
Created: 2026-02-01
"""

import asyncio
import json
import jwt
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import aiohttp
from dataclasses import dataclass

from core.db_postgres import execute, execute_one

logger = logging.getLogger(__name__)

# ============================================================================
# APNs Configuration
# ============================================================================

import os

# APNs Configuration — from environment or defaults
APNS_KEY_ID = os.environ.get("APNS_KEY_ID", "DAJ5RF8F46")
APNS_TEAM_ID = os.environ.get("APNS_TEAM_ID", "NDGY75Y29A")
APNS_BUNDLE_ID = "io.enliko.trading"

# Auth key path — search multiple locations
_AUTH_KEY_FILENAME = f"AuthKey_{APNS_KEY_ID}.p8"
_possible_paths = [
    os.environ.get("APNS_AUTH_KEY_PATH", ""),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), _AUTH_KEY_FILENAME),
    f"/home/ubuntu/project/elcarobybitbotv2/{_AUTH_KEY_FILENAME}",
]
APNS_AUTH_KEY_PATH = next((p for p in _possible_paths if p and os.path.exists(p)), _possible_paths[1])

# APNs endpoints
APNS_PRODUCTION = "https://api.push.apple.com"
APNS_SANDBOX = "https://api.sandbox.push.apple.com"

# Use production for TestFlight/App Store builds, sandbox only for Xcode debug
APNS_HOST = os.environ.get("APNS_HOST", APNS_PRODUCTION)


@dataclass
class PushPayload:
    """APNs push notification payload"""
    title: str
    body: str
    subtitle: Optional[str] = None
    badge: Optional[int] = None
    sound: str = "default"
    category: Optional[str] = None
    thread_id: Optional[str] = None
    custom_data: Optional[Dict] = None
    mutable_content: bool = True  # For Notification Service Extension
    content_available: bool = False  # For silent push


class APNsService:
    """
    Apple Push Notification Service client.
    Uses JWT authentication (token-based).
    """
    
    def __init__(self):
        self._token: Optional[str] = None
        self._token_expires: float = 0
        self._auth_key: Optional[str] = None
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,
                enable_cleanup_closed=True
            )
            self._session = aiohttp.ClientSession(connector=connector)
        return self._session
        
    def _load_auth_key(self) -> str:
        """Load APNs authentication key from file"""
        if self._auth_key is None:
            try:
                with open(APNS_AUTH_KEY_PATH, 'r') as f:
                    self._auth_key = f.read()
            except FileNotFoundError:
                logger.error(f"APNs auth key not found: {APNS_AUTH_KEY_PATH}")
                raise
        return self._auth_key
        
    def _generate_token(self) -> str:
        """Generate JWT token for APNs authentication"""
        now = time.time()
        
        # Reuse token if not expired (refresh every 45 minutes, valid for 1 hour)
        if self._token and now < self._token_expires:
            return self._token
            
        try:
            auth_key = self._load_auth_key()
            
            headers = {
                "alg": "ES256",
                "kid": APNS_KEY_ID
            }
            
            payload = {
                "iss": APNS_TEAM_ID,
                "iat": int(now)
            }
            
            self._token = jwt.encode(payload, auth_key, algorithm="ES256", headers=headers)
            self._token_expires = now + 2700  # 45 minutes
            
            return self._token
        except Exception as e:
            logger.error(f"Failed to generate APNs token: {e}")
            raise
            
    async def send_push(
        self,
        device_token: str,
        payload: PushPayload,
        priority: int = 10,
        expiration: int = 0
    ) -> bool:
        """
        Send push notification to device.
        
        Args:
            device_token: APNs device token
            payload: Push notification payload
            priority: 10 for immediate, 5 for power considerations
            expiration: Unix timestamp when notification expires (0 = immediate)
            
        Returns:
            True if sent successfully
        """
        try:
            session = await self._get_session()
            token = self._generate_token()
            
            url = f"{APNS_HOST}/3/device/{device_token}"
            
            headers = {
                "authorization": f"bearer {token}",
                "apns-topic": APNS_BUNDLE_ID,
                "apns-push-type": "alert",
                "apns-priority": str(priority),
                "apns-expiration": str(expiration),
            }
            
            # Build APNs payload
            aps = {
                "alert": {
                    "title": payload.title,
                    "body": payload.body,
                },
                "sound": payload.sound,
            }
            
            if payload.subtitle:
                aps["alert"]["subtitle"] = payload.subtitle
            if payload.badge is not None:
                aps["badge"] = payload.badge
            if payload.category:
                aps["category"] = payload.category
            if payload.thread_id:
                aps["thread-id"] = payload.thread_id
            if payload.mutable_content:
                aps["mutable-content"] = 1
            if payload.content_available:
                aps["content-available"] = 1
                
            body = {"aps": aps}
            
            if payload.custom_data:
                body.update(payload.custom_data)
                
            async with session.post(url, json=body, headers=headers) as resp:
                if resp.status == 200:
                    logger.debug(f"Push sent to {device_token[:20]}...")
                    return True
                else:
                    error = await resp.text()
                    logger.error(f"APNs error {resp.status}: {error}")
                    
                    # Handle specific errors
                    if resp.status == 410:  # Unregistered
                        await self._deactivate_device(device_token)
                    elif resp.status == 400:  # Bad request
                        try:
                            error_data = json.loads(error)
                            if error_data.get("reason") == "BadDeviceToken":
                                await self._deactivate_device(device_token)
                        except (json.JSONDecodeError, TypeError):
                            pass
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to send push: {e}")
            return False
            
    async def _deactivate_device(self, device_token: str):
        """Deactivate invalid device token"""
        try:
            execute("""
                UPDATE user_devices SET is_active = FALSE 
                WHERE device_token = %s
            """, (device_token,))
            logger.info(f"Deactivated device token: {device_token[:20]}...")
        except Exception as e:
            logger.error(f"Failed to deactivate device: {e}")
            
    async def send_to_user(self, user_id: int, payload: PushPayload) -> int:
        """
        Send push to all active devices of user.
        Checks user's notification preferences before sending.
        
        Returns:
            Number of successful sends
        """
        # Check user notification preferences
        try:
            prefs = execute_one("""
                SELECT trades_enabled, signals_enabled, price_alerts_enabled,
                       daily_report_enabled, trade_opened, trade_closed,
                       break_even, partial_tp, margin_warning
                FROM notification_preferences WHERE user_id = %s
            """, (user_id,))
            
            if prefs:
                category = payload.category or ""
                p = prefs if isinstance(prefs, dict) else {}
                
                # Map APNs categories to preference keys
                if category == "TRADE_CLOSED" and not p.get("trade_closed", True):
                    logger.debug(f"User {user_id} disabled trade_closed notifications")
                    return 0
                if category == "TRADE_OPENED" and not p.get("trade_opened", True):
                    logger.debug(f"User {user_id} disabled trade_opened notifications")
                    return 0
                if category == "BREAK_EVEN" and not p.get("break_even", True):
                    logger.debug(f"User {user_id} disabled break_even notifications")
                    return 0
                if category == "PARTIAL_TP" and not p.get("partial_tp", True):
                    logger.debug(f"User {user_id} disabled partial_tp notifications")
                    return 0
                if category == "SIGNAL" and not p.get("signals_enabled", True):
                    logger.debug(f"User {user_id} disabled signal notifications")
                    return 0
                if category == "MARGIN_WARNING" and not p.get("margin_warning", True):
                    logger.debug(f"User {user_id} disabled margin_warning notifications")
                    return 0
                if category in ("TRADE_CLOSED", "TRADE_OPENED") and not p.get("trades_enabled", True):
                    logger.debug(f"User {user_id} disabled all trade notifications")
                    return 0
        except Exception as e:
            logger.debug(f"Could not check preferences for user {user_id}: {e}")
            # If preferences can't be loaded, send notification anyway
        
        devices = execute("""
            SELECT device_token FROM user_devices
            WHERE user_id = %s AND device_type = 'ios' AND is_active = TRUE
        """, (user_id,))
        
        if not devices:
            logger.debug(f"No iOS devices for user {user_id}")
            return 0
            
        success_count = 0
        for device in devices:
            token = device["device_token"] if isinstance(device, dict) else device[0]
            if await self.send_push(token, payload):
                success_count += 1
                
        return success_count
        
    async def close(self):
        """Close the session"""
        if self._session and not self._session.closed:
            await self._session.close()


# Global instance
apns_service = APNsService()


# ============================================================================
# Trade Notification Helpers
# ============================================================================

async def send_trade_opened_push(user_id: int, trade_data: dict):
    """
    Send beautiful push notification when trade is opened.
    
    trade_data should contain:
    - symbol: str (e.g., "BTCUSDT")
    - side: str (e.g., "LONG" or "SHORT")
    - entry_price: float
    - quantity: float
    - leverage: int
    - take_profit: float (optional)
    - stop_loss: float (optional)
    """
    symbol = trade_data.get("symbol", "UNKNOWN")
    side = trade_data.get("side", "LONG").upper()
    entry_price = trade_data.get("entry_price", 0)
    leverage = trade_data.get("leverage", 1)
    
    # Emoji based on side
    emoji = "🟢" if side == "LONG" else "🔴"
    
    payload = PushPayload(
        title=f"{emoji} {symbol} {side}",
        subtitle=f"{leverage}x Leverage",
        body=f"Entry: ${entry_price:,.2f}",
        category="TRADE_OPENED",
        thread_id=f"trade_{symbol}",
        sound="trade_open.wav",
        custom_data={
            "type": "trade_opened",
            "symbol": symbol,
            "side": side,
            "entry_price": entry_price,
            "leverage": leverage,
        }
    )
    
    return await apns_service.send_to_user(user_id, payload)


async def send_trade_closed_push(user_id: int, trade_data: dict):
    """
    Send beautiful push notification when trade is closed.
    
    trade_data should contain:
    - symbol: str
    - side: str
    - entry_price: float
    - exit_price: float
    - pnl: float
    - pnl_percent: float
    - exit_reason: str (optional)
    """
    symbol = trade_data.get("symbol", "UNKNOWN")
    side = trade_data.get("side", "LONG").upper()
    pnl = trade_data.get("pnl", 0)
    pnl_percent = trade_data.get("pnl_percent", 0)
    exit_reason = trade_data.get("exit_reason", "")
    
    # Emoji based on profit/loss
    if pnl > 0:
        emoji = "🎉"
        result = "PROFIT"
    elif pnl < 0:
        emoji = "📉"
        result = "LOSS"
    else:
        emoji = "➖"
        result = "BREAKEVEN"
        
    # Sound based on result
    sound = "trade_profit.wav" if pnl > 0 else "trade_loss.wav"
    
    payload = PushPayload(
        title=f"{emoji} {symbol} Closed • {result}",
        subtitle=f"{side} • {exit_reason}" if exit_reason else side,
        body=f"PnL: ${pnl:+,.2f} ({pnl_percent:+.2f}%)",
        category="TRADE_CLOSED",
        thread_id=f"trade_{symbol}",
        sound=sound,
        custom_data={
            "type": "trade_closed",
            "symbol": symbol,
            "side": side,
            "pnl": pnl,
            "pnl_percent": pnl_percent,
        }
    )
    
    return await apns_service.send_to_user(user_id, payload)


async def send_daily_digest_push(user_id: int, digest_data: dict):
    """
    Send beautiful daily trading digest push notification.
    
    digest_data should contain:
    - date: str (e.g., "Feb 1, 2026")
    - trades_count: int
    - wins: int
    - losses: int
    - total_pnl: float
    - best_trade_pnl: float
    - best_trade_symbol: str
    - worst_trade_pnl: float
    - worst_trade_symbol: str
    - win_rate: float (0-100)
    """
    total_pnl = digest_data.get("total_pnl", 0)
    trades_count = digest_data.get("trades_count", 0)
    wins = digest_data.get("wins", 0)
    losses = digest_data.get("losses", 0)
    win_rate = digest_data.get("win_rate", 0)
    date = digest_data.get("date", datetime.now().strftime("%b %d, %Y"))
    best_pnl = digest_data.get("best_trade_pnl", 0)
    best_symbol = digest_data.get("best_trade_symbol", "")
    
    # Emoji based on daily PnL
    if total_pnl > 100:
        emoji = "🚀"
        vibe = "Amazing day!"
    elif total_pnl > 0:
        emoji = "✅"
        vibe = "Nice work!"
    elif total_pnl == 0:
        emoji = "➖"
        vibe = "Breakeven day"
    elif total_pnl > -100:
        emoji = "📉"
        vibe = "Small loss"
    else:
        emoji = "😔"
        vibe = "Tough day"
    
    # Build body with stats
    body_parts = [f"PnL: ${total_pnl:+,.2f}"]
    if trades_count > 0:
        body_parts.append(f"{wins}W/{losses}L ({win_rate:.0f}%)")
    if best_pnl > 0 and best_symbol:
        body_parts.append(f"Best: {best_symbol} +${best_pnl:.0f}")
        
    body = " • ".join(body_parts)
    
    payload = PushPayload(
        title=f"{emoji} Daily Digest • {vibe}",
        subtitle=date,
        body=body,
        category="DAILY_DIGEST",
        thread_id="daily_digest",
        sound="digest.wav",
        custom_data={
            "type": "daily_digest",
            "date": date,
            "total_pnl": total_pnl,
            "trades_count": trades_count,
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
        }
    )
    
    return await apns_service.send_to_user(user_id, payload)


async def send_break_even_push(user_id: int, symbol: str, side: str, entry_price: float):
    """Send push when break-even is triggered"""
    payload = PushPayload(
        title=f"🛡 {symbol} • Break-Even",
        subtitle=f"{side} position protected",
        body=f"Stop-loss moved to ${entry_price:,.2f}",
        category="BREAK_EVEN",
        thread_id=f"trade_{symbol}",
        sound="be_triggered.wav",
        custom_data={
            "type": "break_even",
            "symbol": symbol,
            "side": side,
            "entry_price": entry_price,
        }
    )
    
    return await apns_service.send_to_user(user_id, payload)


async def send_partial_tp_push(
    user_id: int, 
    symbol: str, 
    side: str, 
    step: int,
    close_pct: float,
    profit_pct: float,
    pnl: float
):
    """Send push when partial take profit is triggered"""
    payload = PushPayload(
        title=f"💰 {symbol} • Partial TP Step {step}",
        subtitle=f"Closed {close_pct:.0f}% at +{profit_pct:.1f}%",
        body=f"Locked in ${pnl:+,.2f} profit",
        category="PARTIAL_TP",
        thread_id=f"trade_{symbol}",
        sound="partial_tp.wav",
        custom_data={
            "type": "partial_tp",
            "symbol": symbol,
            "side": side,
            "step": step,
            "pnl": pnl,
        }
    )
    
    return await apns_service.send_to_user(user_id, payload)


async def send_signal_push(user_id: int, signal_data: dict):
    """Send push for new trading signal"""
    symbol = signal_data.get("symbol", "UNKNOWN")
    side = signal_data.get("side", "LONG").upper()
    strategy = signal_data.get("strategy", "Signal")
    price = signal_data.get("price", 0)
    
    emoji = "🟢" if side == "LONG" else "🔴"
    
    payload = PushPayload(
        title=f"{emoji} New Signal • {symbol}",
        subtitle=f"{side} • {strategy}",
        body=f"Price: ${price:,.2f}",
        category="SIGNAL",
        thread_id="signals",
        sound="signal.wav",
        custom_data={
            "type": "signal",
            "symbol": symbol,
            "side": side,
            "strategy": strategy,
            "price": price,
        }
    )
    
    return await apns_service.send_to_user(user_id, payload)


async def send_margin_warning_push(user_id: int, margin_ratio: float, exchange: str):
    """Send push for margin warning"""
    payload = PushPayload(
        title="⚠️ Margin Warning",
        subtitle=f"{exchange.capitalize()} Account",
        body=f"Margin ratio: {margin_ratio:.1f}% - Risk of liquidation!",
        category="MARGIN_WARNING",
        thread_id="warnings",
        sound="warning.wav",
        custom_data={
            "type": "margin_warning",
            "margin_ratio": margin_ratio,
            "exchange": exchange,
        }
    )
    
    return await apns_service.send_to_user(user_id, payload)


# ============================================================================
# Batch Operations for Daily Digest
# ============================================================================

async def calculate_daily_digest(user_id: int) -> Optional[dict]:
    """
    Calculate daily trading digest for user.
    
    Returns digest data or None if no trades today.
    """
    today = datetime.now().date()
    
    # Get today's trades
    trades = execute("""
        SELECT symbol, side, pnl, pnl_pct, exit_reason
        FROM trade_logs
        WHERE user_id = %s AND DATE(ts) = %s
        ORDER BY pnl DESC
    """, (user_id, today.isoformat()))
    
    if not trades:
        return None
        
    # Calculate stats
    wins = sum(1 for t in trades if (t.get("pnl") or t[2] or 0) > 0)
    losses = sum(1 for t in trades if (t.get("pnl") or t[2] or 0) < 0)
    total_pnl = sum((t.get("pnl") or t[2] or 0) for t in trades)
    
    trades_count = len(trades)
    win_rate = (wins / trades_count * 100) if trades_count > 0 else 0
    
    # Best and worst trades
    best_trade = trades[0] if trades else None
    worst_trade = trades[-1] if trades else None
    
    return {
        "date": today.strftime("%b %d, %Y"),
        "trades_count": trades_count,
        "wins": wins,
        "losses": losses,
        "total_pnl": total_pnl,
        "win_rate": win_rate,
        "best_trade_pnl": (best_trade.get("pnl") or best_trade[2] or 0) if best_trade else 0,
        "best_trade_symbol": (best_trade.get("symbol") or best_trade[0] or "") if best_trade else "",
        "worst_trade_pnl": (worst_trade.get("pnl") or worst_trade[2] or 0) if worst_trade else 0,
        "worst_trade_symbol": (worst_trade.get("symbol") or worst_trade[0] or "") if worst_trade else "",
    }


async def send_daily_digests_to_all_users():
    """
    Send daily digest to all active users who have trades today.
    Called at 8 PM daily.
    """
    logger.info("Starting daily digest push notifications...")
    
    # Get all users with daily report enabled
    users = execute("""
        SELECT u.user_id 
        FROM users u
        LEFT JOIN notification_preferences np ON u.user_id = np.user_id
        WHERE u.is_allowed = 1 
        AND COALESCE(np.daily_report_enabled, TRUE) = TRUE
    """)
    
    if not users:
        logger.info("No users for daily digest")
        return
        
    sent_count = 0
    for user_row in users:
        user_id = user_row.get("user_id") or user_row[0]
        
        try:
            digest = await calculate_daily_digest(user_id)
            if digest:
                result = await send_daily_digest_push(user_id, digest)
                if result > 0:
                    sent_count += 1
                await asyncio.sleep(0.1)  # Rate limiting
        except Exception as e:
            logger.error(f"Failed to send digest to {user_id}: {e}")
            
    logger.info(f"Daily digest sent to {sent_count} users")
