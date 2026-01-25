"""
User service for managing users
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management operations"""
    
    def __init__(self, db_module):
        self.db = db_module
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by Telegram ID"""
        try:
            return self.db.get_user_config(user_id)
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            return None
    
    async def get_or_create_user(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """Get existing user or create new one"""
        user = await self.get_user(user_id)
        if user:
            return user
        return await self.create_user(user_id, **kwargs)
    
    async def create_user(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """Create new user"""
        try:
            self.db.ensure_user(user_id)
            for field, value in kwargs.items():
                if hasattr(self.db, "USER_FIELDS_WHITELIST"):
                    if field in self.db.USER_FIELDS_WHITELIST:
                        self.db.set_user_field(user_id, field, value)
            return await self.get_user(user_id)
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {e}")
            raise
    
    async def update_user(self, user_id: int, **fields) -> Dict[str, Any]:
        """Update user fields"""
        try:
            self.db.ensure_user(user_id)
            for field, value in fields.items():
                if hasattr(self.db, "USER_FIELDS_WHITELIST"):
                    if field in self.db.USER_FIELDS_WHITELIST:
                        self.db.set_user_field(user_id, field, value)
            return await self.get_user(user_id)
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise
    
    async def get_user_config(self, user_id: int) -> Dict[str, Any]:
        """Get user trading configuration"""
        return self.db.get_user_config(user_id)
    
    async def update_user_config(self, user_id: int, **fields) -> Dict[str, Any]:
        """Update user configuration"""
        for field, value in fields.items():
            if hasattr(self.db, "USER_FIELDS_WHITELIST"):
                if field in self.db.USER_FIELDS_WHITELIST:
                    self.db.set_user_field(user_id, field, value)
        return await self.get_user_config(user_id)
    
    async def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users with pagination"""
        try:
            if hasattr(self.db, "get_all_users"):
                return self.db.get_all_users(limit=limit, offset=offset)
            return []
        except Exception as e:
            logger.error(f"Error fetching all users: {e}")
            return []
    
    async def get_active_users(self) -> List[Dict[str, Any]]:
        """Get all active (approved, not banned) users"""
        try:
            if hasattr(self.db, "get_approved_users"):
                rows = self.db.get_approved_users()
                return [r for r in rows if not r.get("banned")]
            return []
        except Exception as e:
            logger.error(f"Error fetching active users: {e}")
            return []
    
    async def approve_user(self, user_id: int) -> Dict[str, Any]:
        """Approve user for trading"""
        return await self.update_user(user_id, approved=True)
    
    async def ban_user(self, user_id: int, reason: str = None) -> Dict[str, Any]:
        """Ban user from trading"""
        return await self.update_user(user_id, banned=True, ban_reason=reason)
    
    async def unban_user(self, user_id: int) -> Dict[str, Any]:
        """Unban user"""
        return await self.update_user(user_id, banned=False, ban_reason=None)
    
    async def accept_terms(self, user_id: int) -> Dict[str, Any]:
        """Mark user as having accepted terms"""
        return await self.update_user(user_id, terms_accepted=True)
    
    async def set_language(self, user_id: int, language: str) -> Dict[str, Any]:
        """Set user language preference"""
        return await self.update_user(user_id, language=language)
    
    async def set_exchange_mode(self, user_id: int, mode: str) -> Dict[str, Any]:
        """Set user exchange mode"""
        if mode not in ("bybit", "hyperliquid", "both"):
            raise ValueError(f"Invalid exchange mode: {mode}")
        return await self.update_user(user_id, exchange_mode=mode)
    
    async def get_user_stats(self, user_id: int, exchange: str = None, account_type: str = None) -> Dict[str, Any]:
        """Get user trading statistics with multitenancy support"""
        try:
            if hasattr(self.db, "get_trade_logs_list"):
                # Use correct function name and pass exchange for multitenancy
                trades = self.db.get_trade_logs_list(
                    user_id, 
                    limit=1000, 
                    exchange=exchange,
                    account_type=account_type
                )
            else:
                trades = []
            
            total_trades = len(trades)
            winning_trades = sum(1 for t in trades if t.get("pnl", 0) > 0)
            losing_trades = sum(1 for t in trades if t.get("pnl", 0) < 0)
            total_pnl = sum(t.get("pnl", 0) for t in trades)
            
            return {
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": (winning_trades / total_trades * 100) if total_trades > 0 else 0,
                "total_pnl": total_pnl,
                "avg_pnl": total_pnl / total_trades if total_trades > 0 else 0,
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "avg_pnl": 0,
            }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

# Lazy singleton - initialized when db module is available
_user_service_instance = None

def get_user_service():
    """Get or create UserService singleton"""
    global _user_service_instance
    if _user_service_instance is None:
        try:
            import db
            _user_service_instance = UserService(db)
        except ImportError:
            logger.warning("db module not available, UserService not initialized")
            return None
    return _user_service_instance

# Create singleton on module load (if db available)
try:
    import db as _db_module
    user_service = UserService(_db_module)
except ImportError:
    user_service = None
    logger.warning("db module not available at import time")
