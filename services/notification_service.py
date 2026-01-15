"""
Advanced Notification Service for ElCaro Bot
PostgreSQL Multitenancy Architecture
Sends personalized notifications about:
- Position closed/opened
- Daily PnL reports
- Market news from CoinMarketCap
- Large liquidations (>100k)
- Significant market movements
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Import PostgreSQL connection from core
from core.db_postgres import get_conn, execute, execute_one

logger = logging.getLogger(__name__)

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
        
    async def send_position_closed_notification(self, user_id: int, position_data: dict, t: dict):
        """
        Send beautiful notification when position is closed
        """
        try:
            symbol = position_data.get('symbol', 'UNKNOWN')
            side = position_data.get('side', 'LONG')
            entry_price = float(position_data.get('entry_price', 0))
            exit_price = float(position_data.get('exit_price', 0))
            quantity = float(position_data.get('quantity', 0))
            pnl = float(position_data.get('pnl', 0))
            pnl_percent = float(position_data.get('pnl_percent', 0))
            
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
            
        except Exception as e:
            logger.error(f"Error sending position closed notification: {e}")
            
    async def send_position_opened_notification(self, user_id: int, position_data: dict, t: dict):
        """
        Send notification when position is opened
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
            
        except Exception as e:
            logger.error(f"Error sending position opened notification: {e}")
            
    async def send_daily_pnl_report(self, user_id: int, t: dict):
        """
        Send daily PnL summary report
        Uses PostgreSQL via context manager
        """
        try:
            today = datetime.now().date()
            
            # Use PostgreSQL with context manager
            with get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT COUNT(*), COALESCE(SUM(pnl), 0), COALESCE(AVG(pnl), 0)
                    FROM trade_logs
                    WHERE user_id = %s AND DATE(ts) = %s
                """, (user_id, today.isoformat()))
                row = cur.fetchone()
            
            if not row or row[0] == 0:
                return  # No trades today
                
            trades_count = row[0]
            total_pnl = row[1] or 0
            avg_pnl = row[2] or 0
            
            emoji = "🎉" if total_pnl > 0 else "😔" if total_pnl < 0 else "💤"
            
            message = f"""
{emoji} <b>Daily Trading Report</b>

📅 {today.strftime('%d %B %Y')}
━━━━━━━━━━━━━━━━
📊 Trades: <b>{trades_count}</b>
💰 Total PnL: <b>\${total_pnl:+.2f}</b>
📈 Avg PnL: <b>\${avg_pnl:+.2f}</b>

Keep it up! 💪
"""
            
            await self.bot.send_message(user_id, message, parse_mode='HTML')
            
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
                if now.hour == 20 and now.minute == 0:  # 8 PM daily report
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


# Global instance
notification_service = None

def init_notification_service(bot, db=None):
    """Initialize global notification service"""
    global notification_service
    notification_service = NotificationService(bot, db)
    return notification_service
