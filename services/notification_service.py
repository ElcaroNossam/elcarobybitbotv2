"""
Advanced Notification Service for Enliko Bot
PostgreSQL Multitenancy Architecture
Sends personalized notifications about:
- Position closed/opened
- Daily PnL reports
- Market news from CoinMarketCap
- Large liquidations (>100k)
- Significant market movements

Also sends to:
- iOS/Android via APNs Push Notifications (device locked)
- iOS/Android via WebSocket (real-time in-app banners)
- WebApp via WebSocket
- Telegram Bot
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Import PostgreSQL connection from core
from core.db_postgres import get_conn, execute, execute_one

# Import APNs service for iOS push notifications
try:
    from services.apns_service import (
        send_trade_opened_push,
        send_trade_closed_push,
        send_daily_digest_push,
        send_break_even_push,
        send_partial_tp_push,
        send_signal_push,
        calculate_daily_digest,
        send_daily_digests_to_all_users,
    )
    APNS_AVAILABLE = True
except ImportError:
    APNS_AVAILABLE = False

logger = logging.getLogger(__name__)


async def _send_to_websocket(user_id: int, notification: dict):
    """Helper to send notification via WebSocket to iOS/WebApp"""
    try:
        from webapp.api.push_notifications import send_notification_to_user
        await send_notification_to_user(user_id, notification)
    except Exception as e:
        logger.debug(f"WebSocket send failed (user may be offline): {e}")


async def _save_notification_to_db(user_id: int, notification_type: str, title: str, message: str, data: dict = None):
    """Save notification to database for history"""
    try:
        execute("""
            INSERT INTO notification_queue (user_id, notification_type, title, message, data, status)
            VALUES (%s, %s, %s, %s, %s, 'sent')
        """, (user_id, notification_type, title, message, json.dumps(data) if data else None))
    except Exception as e:
        logger.error(f"Failed to save notification to DB: {e}")

class NotificationService:
    def __init__(self, bot, db=None):
        """
        Initialize notification service.
        
        Args:
            bot: Telegram bot instance
            db: Legacy db module (optional, for backward compatibility)
        """
        self.bot = bot
        self.db = db  # Keep for backward compatibility
        self.news_cache = []
        self.last_news_update = None
        self.liquidations_sent = set()  # Track sent liquidations
        self.last_daily_report_date = None  # Track last daily report date to prevent duplicates
        
    async def send_position_closed_notification(self, user_id: int, position_data: dict, t: dict):
        """
        Send beautiful notification when position is closed.
        Sends to: Telegram, iOS Push (APNs), WebSocket
        """
        try:
            symbol = position_data.get('symbol', 'UNKNOWN')
            side = position_data.get('side', 'LONG')
            entry_price = float(position_data.get('entry_price', 0))
            exit_price = float(position_data.get('exit_price', 0))
            quantity = float(position_data.get('quantity', 0))
            pnl = float(position_data.get('pnl', 0))
            pnl_percent = float(position_data.get('pnl_percent', 0))
            exit_reason = position_data.get('exit_reason', '')
            
            # Emoji based on PnL
            emoji = "🎉" if pnl > 0 else "😔" if pnl < 0 else "🤷"
            status = "PROFIT" if pnl > 0 else "LOSS" if pnl < 0 else "BREAKEVEN"
            
            message = f"""
{emoji} <b>Position Closed</b>

📊 <b>{symbol}</b> • {side}
━━━━━━━━━━━━━━━━
📈 Entry: <code>\${entry_price:.2f}</code>
📉 Exit: <code>\${exit_price:.2f}</code>
💰 Size: <code>{quantity}</code>

<b>{status}</b>
💵 PnL: <b>\${pnl:+.2f}</b> ({pnl_percent:+.2f}%)

⏰ {datetime.now().strftime('%H:%M:%S')}
"""
            
            await self.bot.send_message(user_id, message, parse_mode='HTML')
            
            # Send iOS Push Notification (APNs)
            if APNS_AVAILABLE:
                asyncio.create_task(send_trade_closed_push(user_id, {
                    "symbol": symbol,
                    "side": side,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "pnl": pnl,
                    "pnl_percent": pnl_percent,
                    "exit_reason": exit_reason,
                }))
            
            # Also send to iOS/WebApp via WebSocket (for in-app banners)
            ws_notification = {
                "id": f"trade_{datetime.now().timestamp()}",
                "type": "trade_closed",
                "title": f"{symbol} Closed",
                "message": f"{side} • PnL: ${pnl:+.2f} ({pnl_percent:+.2f}%)",
                "data": {
                    "symbol": symbol,
                    "side": side,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "pnl": pnl,
                    "pnl_percent": pnl_percent,
                },
                "created_at": datetime.now().isoformat()
            }
            asyncio.create_task(_send_to_websocket(user_id, ws_notification))
            asyncio.create_task(_save_notification_to_db(
                user_id, "trade_closed", ws_notification["title"], ws_notification["message"], ws_notification["data"]
            ))
            
        except Exception as e:
            logger.error(f"Error sending position closed notification: {e}")
            
    async def send_position_opened_notification(self, user_id: int, position_data: dict, t: dict):
        """
        Send notification when position is opened.
        Sends to: Telegram, iOS Push (APNs), WebSocket
        """
        try:
            symbol = position_data.get('symbol', 'UNKNOWN')
            side = position_data.get('side', 'LONG')
            entry_price = float(position_data.get('entry_price', 0))
            quantity = float(position_data.get('quantity', 0))
            leverage = position_data.get('leverage', 10)
            tp = position_data.get('take_profit')
            sl = position_data.get('stop_loss')
            
            emoji = "🟢" if side.upper() == "LONG" else "🔴"
            
            message = f"""
{emoji} <b>Position Opened</b>

📊 <b>{symbol}</b> • {side} • {leverage}x
━━━━━━━━━━━━━━━━
📈 Entry: <code>\${entry_price:.2f}</code>
💰 Size: <code>{quantity}</code>
"""
            
            if tp:
                message += f"🎯 TP: <code>\${float(tp):.2f}</code>\n"
            if sl:
                message += f"🛡 SL: <code>\${float(sl):.2f}</code>\n"
                
            message += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
            
            await self.bot.send_message(user_id, message, parse_mode='HTML')
            
            # Send iOS Push Notification (APNs)
            if APNS_AVAILABLE:
                asyncio.create_task(send_trade_opened_push(user_id, {
                    "symbol": symbol,
                    "side": side,
                    "entry_price": entry_price,
                    "quantity": quantity,
                    "leverage": leverage,
                    "take_profit": tp,
                    "stop_loss": sl,
                }))
            
            # Also send to iOS/WebApp via WebSocket (for in-app banners)
            ws_notification = {
                "id": f"trade_{datetime.now().timestamp()}",
                "type": "trade_opened",
                "title": f"{symbol} Opened",
                "message": f"{side} • {leverage}x • Entry: ${entry_price:.2f}",
                "data": {
                    "symbol": symbol,
                    "side": side,
                    "entry_price": entry_price,
                    "quantity": quantity,
                    "leverage": leverage,
                    "take_profit": tp,
                    "stop_loss": sl,
                },
                "created_at": datetime.now().isoformat()
            }
            asyncio.create_task(_send_to_websocket(user_id, ws_notification))
            asyncio.create_task(_save_notification_to_db(
                user_id, "trade_opened", ws_notification["title"], ws_notification["message"], ws_notification["data"]
            ))
            
        except Exception as e:
            logger.error(f"Error sending position opened notification: {e}")
            
    async def send_daily_pnl_report(self, user_id: int, t: dict):
        """
        Send beautiful daily PnL summary report with detailed stats.
        Sends to: Telegram, iOS Push (APNs), WebSocket
        """
        try:
            today = datetime.now().date()
            
            # Get detailed stats using PostgreSQL
            with get_conn() as conn:
                cur = conn.cursor()
                
                # Get aggregated stats
                cur.execute("""
                    SELECT 
                        COUNT(*) as trades_count,
                        COALESCE(SUM(pnl), 0) as total_pnl,
                        COALESCE(AVG(pnl), 0) as avg_pnl,
                        COUNT(*) FILTER (WHERE pnl > 0) as wins,
                        COUNT(*) FILTER (WHERE pnl < 0) as losses,
                        MAX(pnl) as best_pnl,
                        MIN(pnl) as worst_pnl
                    FROM trade_logs
                    WHERE user_id = %s AND DATE(ts) = %s
                """, (user_id, today.isoformat()))
                row = cur.fetchone()
                
                # Get best trade symbol
                cur.execute("""
                    SELECT symbol, pnl FROM trade_logs
                    WHERE user_id = %s AND DATE(ts) = %s
                    ORDER BY pnl DESC LIMIT 1
                """, (user_id, today.isoformat()))
                best_trade = cur.fetchone()
                
                # Get worst trade symbol
                cur.execute("""
                    SELECT symbol, pnl FROM trade_logs
                    WHERE user_id = %s AND DATE(ts) = %s
                    ORDER BY pnl ASC LIMIT 1
                """, (user_id, today.isoformat()))
                worst_trade = cur.fetchone()
            
            if not row or row[0] == 0:
                return  # No trades today
                
            trades_count = row[0]
            total_pnl = row[1] or 0
            avg_pnl = row[2] or 0
            wins = row[3] or 0
            losses = row[4] or 0
            best_pnl = row[5] or 0
            worst_pnl = row[6] or 0
            win_rate = (wins / trades_count * 100) if trades_count > 0 else 0
            
            best_symbol = best_trade[0] if best_trade else "N/A"
            worst_symbol = worst_trade[0] if worst_trade else "N/A"
            
            # Choose emoji and vibe based on performance
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
            
            message = f"""
{emoji} <b>Daily Trading Report</b>

📅 {today.strftime('%d %B %Y')} • {vibe}
━━━━━━━━━━━━━━━━━━━━━━

💰 <b>Total PnL: ${total_pnl:+,.2f}</b>

📊 <b>Statistics</b>
├ Trades: <code>{trades_count}</code>
├ Wins/Losses: <code>{wins}W / {losses}L</code>
├ Win Rate: <code>{win_rate:.1f}%</code>
└ Avg PnL: <code>${avg_pnl:+.2f}</code>

🏆 <b>Best Trade</b>
└ {best_symbol}: <code>${best_pnl:+.2f}</code>
"""
            if worst_pnl < 0:
                message += f"""
📉 <b>Worst Trade</b>
└ {worst_symbol}: <code>${worst_pnl:+.2f}</code>
"""
            
            message += "\nKeep improving! 💪"
            
            await self.bot.send_message(user_id, message, parse_mode='HTML')
            
            # Send iOS Push Notification with beautiful digest
            if APNS_AVAILABLE:
                digest_data = {
                    "date": today.strftime("%b %d, %Y"),
                    "trades_count": trades_count,
                    "wins": wins,
                    "losses": losses,
                    "total_pnl": total_pnl,
                    "win_rate": win_rate,
                    "best_trade_pnl": best_pnl,
                    "best_trade_symbol": best_symbol,
                    "worst_trade_pnl": worst_pnl,
                    "worst_trade_symbol": worst_symbol,
                }
                asyncio.create_task(send_daily_digest_push(user_id, digest_data))
            
            # Also send to WebSocket
            ws_notification = {
                "id": f"digest_{datetime.now().timestamp()}",
                "type": "daily_report",
                "title": f"Daily Report • {vibe}",
                "message": f"PnL: ${total_pnl:+.2f} • {wins}W/{losses}L ({win_rate:.0f}%)",
                "data": {
                    "date": today.isoformat(),
                    "trades_count": trades_count,
                    "total_pnl": total_pnl,
                    "wins": wins,
                    "losses": losses,
                    "win_rate": win_rate,
                },
                "created_at": datetime.now().isoformat()
            }
            asyncio.create_task(_send_to_websocket(user_id, ws_notification))
            asyncio.create_task(_save_notification_to_db(
                user_id, "daily_report", ws_notification["title"], ws_notification["message"], ws_notification["data"]
            ))
            
        except Exception as e:
            logger.error(f"Error sending daily PnL report: {e}")
            
    async def fetch_crypto_news(self) -> List[Dict]:
        """
        Fetch latest crypto news from CoinMarketCap
        """
        # Check cache (update every 10 minutes)
        if self.last_news_update and (datetime.now() - self.last_news_update).seconds < 600:
            return self.news_cache
            
        try:
            # Use free crypto news API
            async with aiohttp.ClientSession() as session:
                async with session.get('https://cryptopanic.com/api/v1/posts/?auth_token=free&public=true&kind=news') as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.news_cache = data.get('results', [])[:5]  # Top 5 news
                        self.last_news_update = datetime.now()
                        return self.news_cache
        except Exception as e:
            logger.error(f"Error fetching crypto news: {e}")
            
        return []
        
    async def send_market_news(self, user_id: int):
        """
        Send latest crypto news to user
        """
        try:
            news = await self.fetch_crypto_news()
            
            if not news:
                return
                
            message = "📰 <b>Crypto News</b>\n━━━━━━━━━━━━━━━━\n\n"
            
            for i, item in enumerate(news[:5], 1):
                title = item.get('title', 'No title')
                url = item.get('url', '')
                message += f"{i}. <a href='{url}'>{title}</a>\n\n"
                
            await self.bot.send_message(user_id, message, parse_mode='HTML', disable_web_page_preview=True)
            
        except Exception as e:
            logger.error(f"Error sending market news: {e}")
            
    async def check_large_liquidations(self):
        """
        Check for large liquidations (>100k) and notify users
        """
        try:
            # This would connect to liquidation feed (e.g., from Binance, Bybit API)
            liquidations = []  # Get from API
            
            for liq in liquidations:
                if liq['value'] > 100000:  # >100k
                    liq_id = f"{liq['symbol']}_{liq['timestamp']}"
                    
                    if liq_id not in self.liquidations_sent:
                        self.liquidations_sent.add(liq_id)
                        await self.broadcast_liquidation_alert(liq)
                        
        except Exception as e:
            logger.error(f"Error checking large liquidations: {e}")
            
    async def broadcast_liquidation_alert(self, liq_data: dict):
        """
        Broadcast large liquidation to all users
        Uses PostgreSQL via context manager
        """
        try:
            symbol = liq_data.get('symbol', 'UNKNOWN')
            side = liq_data.get('side', 'LONG')
            value = liq_data.get('value', 0)
            price = liq_data.get('price', 0)
            
            emoji = "🔥" if value > 1000000 else "⚠️"
            
            message = f"""
{emoji} <b>Large Liquidation Alert!</b>

📊 <b>{symbol}</b>
━━━━━━━━━━━━━━━━
🔻 Side: <b>{side}</b>
💰 Value: <b>\${value:,.0f}</b>
📈 Price: <code>\${price:.2f}</code>

⚠️ Market volatility ahead!
"""
            
            # Get all users who want notifications using PostgreSQL
            with get_conn() as conn:
                cur = conn.cursor()
                cur.execute("SELECT user_id FROM users WHERE is_allowed = 1")
                users = cur.fetchall()
            
            for row in users:
                uid = row[0] if isinstance(row, (list, tuple)) else row.get('user_id')
                try:
                    await self.bot.send_message(uid, message, parse_mode='HTML')
                    await asyncio.sleep(0.05)  # Rate limiting
                except Exception as e:
                    logger.debug(f"Failed to send liquidation alert to {uid}: {e}")
                    
        except Exception as e:
            logger.error(f"Error broadcasting liquidation alert: {e}")
            
    async def check_market_movements(self):
        """
        Check for significant market movements and notify
        """
        try:
            # Monitor major pairs for >5% moves
            major_pairs = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
            pass  # Implement based on your price data source
            
        except Exception as e:
            logger.error(f"Error checking market movements: {e}")
            
    async def start_notification_loop(self):
        """
        Background task for periodic notifications
        """
        while True:
            try:
                await self.check_large_liquidations()
                await self.check_market_movements()
                
                now = datetime.now()
                today = now.date()
                # Send daily report at 8 PM, but only once per day
                if now.hour == 20 and now.minute == 0 and self.last_daily_report_date != today:
                    self.last_daily_report_date = today
                    await self.send_daily_reports_to_all_users()
                    
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in notification loop: {e}")
                await asyncio.sleep(60)
                
    async def send_daily_reports_to_all_users(self):
        """
        Send daily PnL reports to all active users
        Uses PostgreSQL via context manager
        """
        try:
            # Get all users using PostgreSQL
            with get_conn() as conn:
                cur = conn.cursor()
                cur.execute("SELECT user_id FROM users WHERE is_allowed = 1")
                users = cur.fetchall()
            
            for row in users:
                uid = row[0] if isinstance(row, (list, tuple)) else row.get('user_id')
                try:
                    t = {}  # Get translations
                    await self.send_daily_pnl_report(uid, t)
                    await asyncio.sleep(0.1)  # Rate limiting
                except Exception as e:
                    logger.debug(f"Failed to send daily report to {uid}: {e}")
                    
        except Exception as e:
            logger.error(f"Error sending daily reports: {e}")
            
    async def send_break_even_notification(self, user_id: int, symbol: str, side: str, entry_price: float):
        """
        Send notification when Break-Even is triggered.
        Sends to: Telegram, iOS Push (APNs), WebSocket
        """
        try:
            message = f"""
🛡 <b>Break-Even Activated</b>

📊 <b>{symbol}</b> • {side}
━━━━━━━━━━━━━━━━
🎯 Stop Loss moved to Entry: <code>${entry_price:.2f}</code>

Your position is now protected! 💪
⏰ {datetime.now().strftime('%H:%M:%S')}
"""
            await self.bot.send_message(user_id, message, parse_mode='HTML')
            
            # Send iOS Push Notification (APNs)
            if APNS_AVAILABLE:
                asyncio.create_task(send_break_even_push(user_id, symbol, side, entry_price))
            
            # Also send to iOS/WebApp via WebSocket
            ws_notification = {
                "id": f"be_{datetime.now().timestamp()}",
                "type": "break_even_triggered",
                "title": f"{symbol} Break-Even",
                "message": f"SL moved to entry: ${entry_price:.2f}",
                "data": {
                    "symbol": symbol,
                    "side": side,
                    "entry_price": entry_price,
                },
                "created_at": datetime.now().isoformat()
            }
            asyncio.create_task(_send_to_websocket(user_id, ws_notification))
            asyncio.create_task(_save_notification_to_db(
                user_id, "break_even", ws_notification["title"], ws_notification["message"], ws_notification["data"]
            ))
            
        except Exception as e:
            logger.error(f"Error sending BE notification: {e}")
            
    async def send_partial_tp_notification(self, user_id: int, symbol: str, side: str, 
                                           step: int, close_pct: float, profit_pct: float, pnl: float):
        """
        Send notification when Partial Take Profit is triggered.
        Sends to: Telegram, iOS Push (APNs), WebSocket
        """
        try:
            message = f"""
💰 <b>Partial Take Profit Step {step}</b>

📊 <b>{symbol}</b> • {side}
━━━━━━━━━━━━━━━━
📉 Closed: <code>{close_pct:.0f}%</code> of position
📈 Profit: <code>+{profit_pct:.2f}%</code>
💵 PnL: <b>${pnl:+.2f}</b>

Locking in profits! 🎉
⏰ {datetime.now().strftime('%H:%M:%S')}
"""
            await self.bot.send_message(user_id, message, parse_mode='HTML')
            
            # Send iOS Push Notification (APNs)
            if APNS_AVAILABLE:
                asyncio.create_task(send_partial_tp_push(user_id, symbol, side, step, close_pct, profit_pct, pnl))
            
            # Also send to iOS/WebApp via WebSocket
            ws_notification = {
                "id": f"ptp_{datetime.now().timestamp()}",
                "type": "partial_tp_triggered",
                "title": f"{symbol} Partial TP Step {step}",
                "message": f"Closed {close_pct:.0f}% at +{profit_pct:.2f}% • ${pnl:+.2f}",
                "data": {
                    "symbol": symbol,
                    "side": side,
                    "step": step,
                    "close_pct": close_pct,
                    "profit_pct": profit_pct,
                    "pnl": pnl,
                },
                "created_at": datetime.now().isoformat()
            }
            asyncio.create_task(_send_to_websocket(user_id, ws_notification))
            asyncio.create_task(_save_notification_to_db(
                user_id, "partial_tp", ws_notification["title"], ws_notification["message"], ws_notification["data"]
            ))
            
        except Exception as e:
            logger.error(f"Error sending Partial TP notification: {e}")
            
    async def send_signal_notification(self, user_id: int, signal_data: dict):
        """
        Send notification when new signal is received.
        Sends to: Telegram, iOS Push (APNs), WebSocket
        """
        try:
            symbol = signal_data.get('symbol', 'UNKNOWN')
            side = signal_data.get('side', 'LONG')
            strategy = signal_data.get('strategy', 'Unknown')
            price = signal_data.get('price', 0)
            
            emoji = "🟢" if side.upper() == "LONG" else "🔴"
            
            message = f"""
{emoji} <b>New Signal</b>

📊 <b>{symbol}</b> • {side}
🧠 Strategy: {strategy}
💵 Price: ${price:.2f}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""
            await self.bot.send_message(user_id, message, parse_mode='HTML')
            
            # Send iOS Push Notification (APNs)
            if APNS_AVAILABLE:
                asyncio.create_task(send_signal_push(user_id, signal_data))
            
            # Also send to iOS/WebApp via WebSocket
            ws_notification = {
                "id": f"signal_{datetime.now().timestamp()}",
                "type": "signal_new",
                "title": f"{symbol} {side} Signal",
                "message": f"{strategy} • Price: ${price:.2f}",
                "data": signal_data,
                "created_at": datetime.now().isoformat()
            }
            asyncio.create_task(_send_to_websocket(user_id, ws_notification))
            asyncio.create_task(_save_notification_to_db(
                user_id, "signal", ws_notification["title"], ws_notification["message"], ws_notification["data"]
            ))
            
        except Exception as e:
            logger.error(f"Error sending signal notification: {e}")


# Global instance
notification_service = None

def init_notification_service(bot, db=None):
    """Initialize global notification service"""
    global notification_service
    notification_service = NotificationService(bot, db)
    return notification_service
