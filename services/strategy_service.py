"""
Strategy Sync Service
Bidirectional synchronization between WebApp and Telegram Bot
Handles custom strategies, rankings, and live updates

PostgreSQL ONLY - No SQLite support
"""
import json
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

# PostgreSQL imports
from core.db_postgres import get_pool, get_conn, execute, execute_one, execute_write

import db

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGY TYPES & MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class StrategyType(Enum):
    SYSTEM = "system"       # Built-in strategies (elcaro, rsibboi, etc.)
    CUSTOM = "custom"       # User-created strategies
    PURCHASED = "purchased"  # Bought from marketplace


@dataclass
class StrategySettings:
    """User's settings for a specific strategy"""
    enabled: bool = False
    leverage: int = 10
    tp_percent: float = 2.0
    sl_percent: float = 1.5
    risk_per_trade: float = 1.0
    max_positions: int = 3
    symbols: List[str] = None
    timeframe: str = "1h"
    custom_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.symbols is None:
            self.symbols = ["BTCUSDT", "ETHUSDT"]
        if self.custom_params is None:
            self.custom_params = {}


# Built-in system strategies
SYSTEM_STRATEGIES = {
    "elcaro": {
        "name": "ElCaro",
        "description": "Channel breakout with momentum confirmation",
        "icon": "🎯",
        "default_settings": {"tp_percent": 4.0, "sl_percent": 2.0, "risk_per_trade": 1.0}
    },
    "rsibboi": {
        "name": "RSI+BB+OI",
        "description": "RSI divergence with Bollinger Bands and Open Interest",
        "icon": "📊",
        "default_settings": {"tp_percent": 3.0, "sl_percent": 1.5, "risk_per_trade": 1.0}
    },
    "wyckoff": {
        "name": "Wyckoff/SMC",
        "description": "Smart Money Concepts with Fibonacci zones",
        "icon": "🔮",
        "default_settings": {"tp_percent": 4.0, "sl_percent": 2.0, "risk_per_trade": 1.0}
    },
    "scryptomera": {
        "name": "Scryptomera",
        "description": "Volume profile and delta analysis",
        "icon": "💎",
        "default_settings": {"tp_percent": 3.5, "sl_percent": 2.0, "risk_per_trade": 1.0}
    },
    "scalper": {
        "name": "Scalper",
        "description": "High-frequency scalping with tight stops",
        "icon": "⚡",
        "default_settings": {"tp_percent": 1.5, "sl_percent": 0.75, "risk_per_trade": 0.5}
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE HELPERS (PostgreSQL Only)
# ═══════════════════════════════════════════════════════════════════════════════

def _get_conn():
    """Get PostgreSQL connection from pool"""
    pool = get_pool()
    return pool.getconn()

def _release_conn(conn):
    """Release connection back to pool"""
    pool = get_pool()
    pool.putconn(conn)


# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGY SYNC SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class StrategySyncService:
    """
    Handles bidirectional sync between WebApp and Bot.
    All strategy changes in webapp are immediately available in bot and vice versa.
    """
    
    def __init__(self):
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure custom_strategies table exists"""
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS custom_strategies (
                            id SERIAL PRIMARY KEY,
                            user_id BIGINT NOT NULL,
                            strategy_key TEXT NOT NULL,
                            strategy_name TEXT NOT NULL,
                            strategy_type TEXT DEFAULT 'custom',
                            settings_json TEXT,
                            performance_stats TEXT,
                            is_active BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT NOW(),
                            updated_at TIMESTAMP DEFAULT NOW(),
                            UNIQUE(user_id, strategy_key)
                        )
                    """)
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_custom_strategies_user 
                        ON custom_strategies(user_id)
                    """)
        except Exception as e:
            logger.warning(f"Could not ensure custom_strategies table: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # USER STRATEGY CONFIG (reads/writes from main user record)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def get_user_strategies(self, user_id: int) -> Dict[str, Dict]:
        """
        Get all enabled strategies and their settings for a user.
        Returns dict of {strategy_key: settings}
        """
        result = {}
        
        # 1. Get system strategies status from user record
        cfg = db.get_user_config(user_id)
        
        for key in SYSTEM_STRATEGIES:
            flag_field = f"trade_{key}" if key != "rsibboi" else "trade_oi"
            enabled = bool(cfg.get(flag_field, 0))
            
            if enabled:
                settings = db.get_strategy_settings(user_id, key)
                result[key] = {
                    "type": "system",
                    "enabled": True,
                    "name": SYSTEM_STRATEGIES[key]["name"],
                    "icon": SYSTEM_STRATEGIES[key]["icon"],
                    **settings
                }
        
        # 2. Get custom strategies
        custom = self.get_custom_strategies(user_id)
        for strat in custom:
            if strat.get("is_active"):
                result[strat["strategy_key"]] = {
                    "type": "custom",
                    "enabled": True,
                    "name": strat["strategy_name"],
                    **json.loads(strat.get("settings_json") or "{}")
                }
        
        return result
    
    def enable_strategy(self, user_id: int, strategy_key: str, enabled: bool = True) -> bool:
        """Enable or disable a strategy for a user"""
        if strategy_key in SYSTEM_STRATEGIES or strategy_key == "rsibboi":
            # System strategy - update user flag
            flag_field = f"trade_{strategy_key}" if strategy_key != "rsibboi" else "trade_oi"
            db.set_user_field(user_id, flag_field, 1 if enabled else 0)
            return True
        
        # Custom strategy
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE custom_strategies 
                SET is_active = %s, updated_at = NOW()
                WHERE user_id = %s AND strategy_key = %s
            """, (enabled, user_id, strategy_key))
            conn.commit()
            return cur.rowcount > 0
        finally:
            _release_conn(conn)
    
    def update_strategy_settings(
        self, 
        user_id: int, 
        strategy_key: str, 
        settings: Dict[str, Any],
        exchange: str = None,
        account_type: str = None
    ) -> bool:
        """Update settings for a strategy"""
        if strategy_key in SYSTEM_STRATEGIES or strategy_key == "rsibboi":
            # System strategy - use main db functions
            for field, value in settings.items():
                db.set_strategy_setting(user_id, strategy_key, field, value, exchange, account_type)
            return True
        
        # Custom strategy
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE custom_strategies 
                SET settings_json = %s, updated_at = NOW()
                WHERE user_id = %s AND strategy_key = %s
            """, (json.dumps(settings), user_id, strategy_key))
            conn.commit()
            return cur.rowcount > 0
        finally:
            _release_conn(conn)
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # CUSTOM STRATEGIES CRUD
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def create_custom_strategy(
        self,
        user_id: int,
        name: str,
        base_strategy: str = "custom",
        settings: Dict = None
    ) -> Optional[Dict]:
        """Create a new custom strategy for user"""
        strategy_key = f"custom_{user_id}_{int(time.time())}"
        settings = settings or {}
        
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO custom_strategies 
                    (user_id, strategy_key, strategy_name, strategy_type, settings_json, is_active)
                VALUES (%s, %s, %s, %s, %s, FALSE)
                RETURNING id, strategy_key, strategy_name
            """, (user_id, strategy_key, name, base_strategy, json.dumps(settings)))
            
            row = cur.fetchone()
            conn.commit()
            
            if row:
                return {
                    "id": row[0],
                    "strategy_key": row[1],
                    "strategy_name": row[2],
                    "settings": settings
                }
            return None
        finally:
            _release_conn(conn)
    
    def get_custom_strategies(self, user_id: int) -> List[Dict]:
        """Get all custom strategies for a user"""
        return execute("""
            SELECT id, strategy_key, strategy_name, strategy_type, 
                   settings_json, performance_stats, is_active,
                   created_at, updated_at
            FROM custom_strategies 
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
    
    def delete_custom_strategy(self, user_id: int, strategy_key: str) -> bool:
        """Delete a custom strategy"""
        count = execute_write("""
            DELETE FROM custom_strategies 
            WHERE user_id = %s AND strategy_key = %s
        """, (user_id, strategy_key))
        return count > 0
    
    def update_performance_stats(
        self, 
        user_id: int, 
        strategy_key: str, 
        stats: Dict
    ) -> bool:
        """Update performance statistics for a strategy"""
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE custom_strategies 
                SET performance_stats = %s, updated_at = NOW()
                WHERE user_id = %s AND strategy_key = %s
            """, (json.dumps(stats), user_id, strategy_key))
            conn.commit()
            return cur.rowcount > 0
        finally:
            _release_conn(conn)
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # STRATEGY RANKINGS & LEADERBOARDS
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def get_strategy_leaderboard(
        self, 
        strategy_key: str = None,
        timeframe: str = "7d",
        limit: int = 50
    ) -> List[Dict]:
        """Get top performing users for a strategy"""
        # Calculate time range
        days_map = {"1d": 1, "7d": 7, "30d": 30, "all": 365}
        days = days_map.get(timeframe, 7)
        
        if strategy_key:
            return execute("""
                SELECT 
                    user_id,
                    strategy,
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(pnl) as total_pnl,
                    AVG(pnl_pct) as avg_pnl_pct
                FROM trade_logs
                WHERE strategy = %s
                AND ts >= NOW() - INTERVAL '%s days'
                GROUP BY user_id, strategy
                HAVING COUNT(*) >= 5
                ORDER BY total_pnl DESC
                LIMIT %s
            """, (strategy_key, days, limit))
        else:
            return execute("""
                SELECT 
                    user_id,
                    'all' as strategy,
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(pnl) as total_pnl,
                    AVG(pnl_pct) as avg_pnl_pct
                FROM trade_logs
                WHERE ts >= NOW() - INTERVAL '%s days'
                GROUP BY user_id
                HAVING COUNT(*) >= 10
                ORDER BY total_pnl DESC
                LIMIT %s
            """, (days, limit))
    
    def get_user_ranking(self, user_id: int, strategy_key: str = None) -> Dict:
        """Get user's ranking position"""
        result = execute_one("""
            WITH ranked AS (
                SELECT 
                    user_id,
                    SUM(pnl) as total_pnl,
                    RANK() OVER (ORDER BY SUM(pnl) DESC) as rank
                FROM trade_logs
                WHERE ts >= NOW() - INTERVAL '7 days'
                GROUP BY user_id
                HAVING COUNT(*) >= 5
            )
            SELECT rank, total_pnl
            FROM ranked
            WHERE user_id = %s
        """, (user_id,))
        
        if result:
            return {
                "rank": result["rank"],
                "total_pnl": result["total_pnl"]
            }
        return {"rank": None, "total_pnl": 0}


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_service_instance: Optional[StrategySyncService] = None

def get_strategy_service() -> StrategySyncService:
    """Get singleton instance of strategy service"""
    global _service_instance
    if _service_instance is None:
        _service_instance = StrategySyncService()
    return _service_instance


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_user_strategies(user_id: int) -> Dict:
    """Get all enabled strategies for a user"""
    return get_strategy_service().get_user_strategies(user_id)

def enable_strategy(user_id: int, strategy_key: str, enabled: bool = True) -> bool:
    """Enable/disable a strategy"""
    return get_strategy_service().enable_strategy(user_id, strategy_key, enabled)

def update_strategy_settings(user_id: int, strategy_key: str, settings: Dict) -> bool:
    """Update strategy settings"""
    return get_strategy_service().update_strategy_settings(user_id, strategy_key, settings)

def get_strategy_leaderboard(strategy_key: str = None, limit: int = 50) -> List[Dict]:
    """Get strategy leaderboard"""
    return get_strategy_service().get_strategy_leaderboard(strategy_key, limit=limit)
