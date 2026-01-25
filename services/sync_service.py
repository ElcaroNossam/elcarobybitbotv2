"""
Cross-Platform Sync Service

Handles synchronization of user data across:
- iOS App
- WebApp (Terminal)
- Telegram Bot

Features:
- Activity logging
- Real-time notifications via WebSocket
- Telegram push notifications
- Unified history across all platforms
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Import database functions
try:
    from core.db_postgres import get_conn, execute, execute_one
except ImportError:
    get_conn = None
    execute = None
    execute_one = None


class SyncService:
    """Central service for cross-platform synchronization"""
    
    _instance = None
    _telegram_bot = None
    _websocket_manager = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def set_telegram_bot(cls, bot):
        """Set reference to Telegram bot for sending notifications"""
        cls._telegram_bot = bot
    
    @classmethod
    def set_websocket_manager(cls, manager):
        """Set reference to WebSocket manager for real-time updates"""
        cls._websocket_manager = manager
    
    # ==================== Activity Logging ====================
    
    async def log_activity(
        self,
        user_id: int,
        action_type: str,
        action_category: str,
        source: str,
        entity_type: str = None,
        entity_id: str = None,
        old_value: Any = None,
        new_value: Any = None,
        device_info: str = None,
        ip_address: str = None,
        user_agent: str = None,
        notify: bool = True
    ) -> int:
        """
        Log user activity and trigger notifications.
        
        Args:
            user_id: User's Telegram ID
            action_type: Type of action (settings_change, trade, login, etc.)
            action_category: Category (settings, trading, auth, exchange)
            source: Source platform (ios, webapp, telegram, api)
            entity_type: What was changed (strategy_settings, user_settings, position)
            entity_id: Specific entity ID
            old_value: Previous value (will be JSON serialized)
            new_value: New value (will be JSON serialized)
            device_info: Device/browser info
            ip_address: Client IP
            user_agent: User agent string
            notify: Whether to send notifications
            
        Returns:
            Activity log ID
        """
        if not get_conn:
            logger.warning("Database not available for activity logging")
            return 0
        
        try:
            with get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO user_activity_log 
                    (user_id, action_type, action_category, source, entity_type, 
                     entity_id, old_value, new_value, device_info, ip_address, user_agent)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    user_id,
                    action_type,
                    action_category,
                    source,
                    entity_type,
                    entity_id,
                    json.dumps(old_value) if old_value else None,
                    json.dumps(new_value) if new_value else None,
                    device_info,
                    ip_address,
                    user_agent
                ))
                activity_id = cur.fetchone()[0]
                conn.commit()
                
            # Trigger notifications to other platforms
            if notify:
                asyncio.create_task(self._notify_all_platforms(
                    user_id, activity_id, action_type, action_category, 
                    source, entity_type, old_value, new_value
                ))
                
            return activity_id
            
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
            return 0
    
    async def _notify_all_platforms(
        self,
        user_id: int,
        activity_id: int,
        action_type: str,
        action_category: str,
        source: str,
        entity_type: str,
        old_value: Any,
        new_value: Any
    ):
        """Send notifications to all platforms except the source"""
        
        notification_data = {
            "type": "sync_update",
            "action_type": action_type,
            "category": action_category,
            "source": source,
            "entity_type": entity_type,
            "changes": new_value,
            "timestamp": datetime.now().isoformat()
        }
        
        # Notify WebSocket (WebApp + iOS)
        if source != "webapp":
            await self._notify_websocket(user_id, notification_data)
        
        # Notify Telegram (if change not from bot)
        if source != "telegram":
            await self._notify_telegram(user_id, action_type, entity_type, new_value, source)
        
        # Update notification status
        await self._update_notification_status(activity_id, source)
    
    async def _notify_websocket(self, user_id: int, data: dict):
        """Send WebSocket notification to all connected clients"""
        try:
            if self._websocket_manager:
                await self._websocket_manager.broadcast_to_user(user_id, data)
                logger.info(f"WebSocket notification sent to user {user_id}")
        except Exception as e:
            logger.error(f"WebSocket notification failed: {e}")
    
    async def _notify_telegram(
        self, 
        user_id: int, 
        action_type: str, 
        entity_type: str, 
        new_value: Any,
        source: str
    ):
        """Send Telegram notification about changes"""
        try:
            if not self._telegram_bot:
                logger.debug("Telegram bot not set for notifications")
                return
            
            # Build notification message
            message = self._build_telegram_message(action_type, entity_type, new_value, source)
            
            if message:
                await self._telegram_bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode="Markdown"
                )
                logger.info(f"Telegram notification sent to user {user_id}")
                
        except Exception as e:
            logger.error(f"Telegram notification failed: {e}")
    
    def _build_telegram_message(
        self, 
        action_type: str, 
        entity_type: str, 
        new_value: Any,
        source: str
    ) -> Optional[str]:
        """Build human-readable Telegram notification message"""
        
        source_emoji = {
            "ios": "📱",
            "webapp": "💻",
            "api": "🔌"
        }.get(source, "🔄")
        
        if action_type == "settings_change":
            if entity_type == "strategy_settings":
                return (
                    f"{source_emoji} *Settings Updated*\n\n"
                    f"Your strategy settings were changed from {source.upper()}.\n"
                    f"Changes will apply to new trades."
                )
            elif entity_type == "exchange_type":
                exchange = new_value if isinstance(new_value, str) else new_value.get("exchange", "unknown")
                return (
                    f"{source_emoji} *Exchange Switched*\n\n"
                    f"Active exchange changed to *{exchange.upper()}* from {source.upper()}."
                )
            elif entity_type == "trading_mode":
                mode = new_value if isinstance(new_value, str) else new_value.get("mode", "unknown")
                return (
                    f"{source_emoji} *Trading Mode Changed*\n\n"
                    f"Trading mode set to *{mode.upper()}* from {source.upper()}."
                )
        
        elif action_type == "trade":
            return None  # Trade notifications handled separately
        
        elif action_type == "login":
            return (
                f"{source_emoji} *New Login*\n\n"
                f"Login detected from {source.upper()}."
            )
        
        return None
    
    async def _update_notification_status(self, activity_id: int, source: str):
        """Update which platforms were notified"""
        try:
            with get_conn() as conn:
                cur = conn.cursor()
                
                # Mark platforms as notified (except source)
                updates = []
                if source != "telegram":
                    updates.append("telegram_notified = TRUE")
                if source != "webapp":
                    updates.append("webapp_notified = TRUE")
                if source != "ios":
                    updates.append("ios_notified = TRUE")
                
                if updates:
                    cur.execute(f"""
                        UPDATE user_activity_log 
                        SET {', '.join(updates)}
                        WHERE id = %s
                    """, (activity_id,))
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"Failed to update notification status: {e}")
    
    # ==================== Activity History ====================
    
    async def get_activity_history(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        action_type: str = None,
        source: str = None,
        from_date: datetime = None,
        to_date: datetime = None
    ) -> List[Dict]:
        """Get user's activity history"""
        
        if not execute:
            return []
        
        try:
            query = """
                SELECT id, action_type, action_category, source, entity_type,
                       entity_id, old_value, new_value, device_info, 
                       telegram_notified, webapp_notified, ios_notified,
                       created_at
                FROM user_activity_log
                WHERE user_id = %s
            """
            params = [user_id]
            
            if action_type:
                query += " AND action_type = %s"
                params.append(action_type)
            
            if source:
                query += " AND source = %s"
                params.append(source)
            
            if from_date:
                query += " AND created_at >= %s"
                params.append(from_date)
            
            if to_date:
                query += " AND created_at <= %s"
                params.append(to_date)
            
            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            rows = execute(query, tuple(params))
            
            return [
                {
                    "id": row[0],
                    "action_type": row[1],
                    "action_category": row[2],
                    "source": row[3],
                    "entity_type": row[4],
                    "entity_id": row[5],
                    "old_value": row[6],
                    "new_value": row[7],
                    "device_info": row[8],
                    "telegram_notified": row[9],
                    "webapp_notified": row[10],
                    "ios_notified": row[11],
                    "created_at": row[12].isoformat() if row[12] else None
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Failed to get activity history: {e}")
            return []
    
    # ==================== Settings Sync Helpers ====================
    
    async def sync_settings_change(
        self,
        user_id: int,
        source: str,
        setting_type: str,
        old_value: Any,
        new_value: Any,
        device_info: str = None
    ):
        """Convenience method for syncing settings changes"""
        
        await self.log_activity(
            user_id=user_id,
            action_type="settings_change",
            action_category="settings",
            source=source,
            entity_type=setting_type,
            old_value=old_value,
            new_value=new_value,
            device_info=device_info
        )
    
    async def sync_exchange_switch(
        self,
        user_id: int,
        source: str,
        old_exchange: str,
        new_exchange: str
    ):
        """Sync exchange switch across platforms"""
        
        await self.log_activity(
            user_id=user_id,
            action_type="exchange_switch",
            action_category="exchange",
            source=source,
            entity_type="exchange_type",
            old_value={"exchange": old_exchange},
            new_value={"exchange": new_exchange}
        )
    
    async def sync_trade_action(
        self,
        user_id: int,
        source: str,
        action: str,  # 'open', 'close', 'modify'
        trade_data: dict
    ):
        """Sync trade actions across platforms"""
        
        await self.log_activity(
            user_id=user_id,
            action_type="trade",
            action_category="trading",
            source=source,
            entity_type=f"trade_{action}",
            new_value=trade_data,
            notify=True
        )


# Global instance
sync_service = SyncService()


# ==================== Integration Functions ====================

async def log_settings_change(
    user_id: int,
    source: str,
    setting_type: str,
    old_value: Any = None,
    new_value: Any = None
):
    """Quick function to log settings changes"""
    await sync_service.sync_settings_change(
        user_id, source, setting_type, old_value, new_value
    )


async def log_exchange_switch(
    user_id: int,
    source: str,
    old_exchange: str,
    new_exchange: str
):
    """Quick function to log exchange switches"""
    await sync_service.sync_exchange_switch(
        user_id, source, old_exchange, new_exchange
    )


async def get_user_activity(
    user_id: int,
    limit: int = 50,
    source: str = None
) -> List[Dict]:
    """Quick function to get user activity history"""
    return await sync_service.get_activity_history(
        user_id, limit=limit, source=source
    )
