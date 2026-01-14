"""
Strategy Sync Service
Bidirectional synchronization between WebApp and Telegram Bot
Handles custom strategies, rankings, and live updates
"""
import sqlite3
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

DB_FILE = Path(__file__).parent.parent / "bot.db"

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
# DATABASE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_FILE), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGY SYNC SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class StrategySyncService:
    """
    Handles bidirectional sync between WebApp and Bot.
    All strategy changes in webapp are immediately available in bot and vice versa.
    """
    
    @staticmethod
    def get_user_strategies(user_id: int) -> Dict[str, Any]:
        """
        Get all strategies available to user:
        - System strategies with user's settings
        - Custom strategies created by user
        - Purchased strategies from marketplace
        """
        conn = get_conn()
        try:
            cur = conn.cursor()
            
            # Get user's strategy settings JSON
            cur.execute("SELECT strategy_settings FROM users WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            user_settings = json.loads(row["strategy_settings"]) if row and row["strategy_settings"] else {}
            
            # Build system strategies with user settings
            system_strategies = {}
            for key, info in SYSTEM_STRATEGIES.items():
                settings = user_settings.get(key, info["default_settings"].copy())
                
                # Check bot-level enable flags
                cur.execute(f"SELECT trade_{key} FROM users WHERE user_id = ?", (user_id,))
                row = cur.fetchone()
                enabled = bool(row[f"trade_{key}"]) if row else False
                
                system_strategies[key] = {
                    "type": "system",
                    "id": key,
                    "name": info["name"],
                    "description": info["description"],
                    "icon": info["icon"],
                    "enabled": enabled,
                    "settings": settings
                }
            
            # Get custom strategies
            cur.execute("""
                SELECT id, name, description, base_strategy, config_json, 
                       win_rate, total_pnl, total_trades, backtest_score, is_public
                FROM custom_strategies 
                WHERE user_id = ? AND is_active = 1
                ORDER BY backtest_score DESC
            """, (user_id,))
            
            custom_strategies = []
            for row in cur.fetchall():
                strategy = dict(row)
                strategy["type"] = "custom"
                strategy["config"] = json.loads(strategy.get("config_json", "{}"))
                del strategy["config_json"]
                custom_strategies.append(strategy)
            
            # Get purchased strategies
            cur.execute("""
                SELECT s.id, s.name, s.description, s.base_strategy, s.config_json,
                       s.win_rate, s.total_pnl, s.total_trades,
                       p.purchased_at, m.seller_id, m.rating
                FROM strategy_purchases p
                JOIN custom_strategies s ON p.strategy_id = s.id
                JOIN strategy_marketplace m ON p.marketplace_id = m.id
                WHERE p.buyer_id = ? AND p.is_active = 1
                ORDER BY p.purchased_at DESC
            """, (user_id,))
            
            purchased_strategies = []
            for row in cur.fetchall():
                strategy = dict(row)
                strategy["type"] = "purchased"
                strategy["config"] = json.loads(strategy.get("config_json", "{}"))
                del strategy["config_json"]
                purchased_strategies.append(strategy)
            
            return {
                "system": system_strategies,
                "custom": custom_strategies,
                "purchased": purchased_strategies,
                "total_enabled": sum(1 for s in system_strategies.values() if s["enabled"])
            }
            
        finally:
            conn.close()
    
    @staticmethod
    def update_strategy_settings(user_id: int, strategy_id: str, settings: Dict[str, Any], 
                                  strategy_type: str = "system") -> bool:
        """
        Update settings for a strategy (syncs to both webapp and bot).
        For system strategies: updates both enable flags and custom params.
        For custom/purchased: updates the config_json.
        """
        conn = get_conn()
        try:
            cur = conn.cursor()
            
            if strategy_type == "system":
                # Update enable flag (bot-level)
                if "enabled" in settings:
                    enabled = 1 if settings["enabled"] else 0
                    cur.execute(f"UPDATE users SET trade_{strategy_id} = ? WHERE user_id = ?",
                               (enabled, user_id))
                
                # Update custom params in strategy_settings JSON
                cur.execute("SELECT strategy_settings FROM users WHERE user_id = ?", (user_id,))
                row = cur.fetchone()
                all_settings = json.loads(row["strategy_settings"]) if row and row["strategy_settings"] else {}
                
                # Merge new settings
                if strategy_id not in all_settings:
                    all_settings[strategy_id] = SYSTEM_STRATEGIES[strategy_id]["default_settings"].copy()
                
                for key, value in settings.items():
                    if key != "enabled":  # enabled is stored separately
                        all_settings[strategy_id][key] = value
                
                cur.execute("UPDATE users SET strategy_settings = ? WHERE user_id = ?",
                           (json.dumps(all_settings), user_id))
            
            elif strategy_type in ("custom", "purchased"):
                # For custom/purchased, verify ownership/purchase then update config
                if strategy_type == "custom":
                    cur.execute("SELECT config_json FROM custom_strategies WHERE id = ? AND user_id = ?",
                               (int(strategy_id), user_id))
                else:
                    cur.execute("""
                        SELECT s.config_json FROM custom_strategies s
                        JOIN strategy_purchases p ON s.id = p.strategy_id
                        WHERE s.id = ? AND p.buyer_id = ? AND p.is_active = 1
                    """, (int(strategy_id), user_id))
                
                row = cur.fetchone()
                if not row:
                    return False
                
                config = json.loads(row["config_json"])
                
                # Update config with new settings
                if "risk_management" not in config:
                    config["risk_management"] = {}
                for key, value in settings.items():
                    if key in ("tp_percent", "sl_percent", "risk_per_trade"):
                        config["risk_management"][key] = value
                    elif key in ("symbols", "timeframe"):
                        config[key] = value
                    elif key == "enabled":
                        # For custom strategies, track enable in a separate field
                        pass
                
                if strategy_type == "custom":
                    cur.execute("UPDATE custom_strategies SET config_json = ?, updated_at = ? WHERE id = ?",
                               (json.dumps(config), int(time.time()), int(strategy_id)))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error updating strategy settings: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_active_strategies_for_trading(user_id: int) -> List[Dict]:
        """
        Get list of enabled strategies ready for trading.
        Used by the bot to determine which strategies to run.
        Returns both system and custom strategies with their full configs.
        """
        conn = get_conn()
        try:
            cur = conn.cursor()
            
            active_strategies = []
            
            # Check system strategies
            for key in SYSTEM_STRATEGIES.keys():
                cur.execute(f"SELECT trade_{key}, strategy_settings FROM users WHERE user_id = ?", (user_id,))
                row = cur.fetchone()
                if row and row[f"trade_{key}"]:
                    settings_json = row["strategy_settings"]
                    all_settings = json.loads(settings_json) if settings_json else {}
                    strategy_settings = all_settings.get(key, SYSTEM_STRATEGIES[key]["default_settings"])
                    
                    active_strategies.append({
                        "type": "system",
                        "id": key,
                        "name": SYSTEM_STRATEGIES[key]["name"],
                        "settings": strategy_settings
                    })
            
            # Get enabled custom strategies (check if user has custom_strategies_enabled in config)
            cur.execute("""
                SELECT id, name, config_json, base_strategy
                FROM custom_strategies
                WHERE user_id = ? AND is_active = 1
            """, (user_id,))
            
            for row in cur.fetchall():
                config = json.loads(row["config_json"])
                # Check if strategy is enabled in config
                if config.get("enabled", True):
                    active_strategies.append({
                        "type": "custom",
                        "id": row["id"],
                        "name": row["name"],
                        "base_strategy": row["base_strategy"],
                        "config": config
                    })
            
            # Get purchased strategies
            cur.execute("""
                SELECT s.id, s.name, s.config_json, s.base_strategy
                FROM strategy_purchases p
                JOIN custom_strategies s ON p.strategy_id = s.id
                WHERE p.buyer_id = ? AND p.is_active = 1
            """, (user_id,))
            
            for row in cur.fetchall():
                config = json.loads(row["config_json"])
                if config.get("enabled", True):
                    active_strategies.append({
                        "type": "purchased",
                        "id": row["id"],
                        "name": row["name"],
                        "base_strategy": row["base_strategy"],
                        "config": config
                    })
            
            return active_strategies
            
        finally:
            conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# RANKING SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class RankingService:
    """
    Manages strategy rankings based on backtest performance.
    Auto-updates rankings when backtests complete.
    """
    
    @staticmethod
    def update_strategy_rank(strategy_id: int, backtest_result: Dict) -> int:
        """
        Update strategy's ranking metrics after backtest.
        Returns new rank position.
        """
        conn = get_conn()
        try:
            cur = conn.cursor()
            
            # Calculate composite score
            win_rate = backtest_result.get("win_rate", 0)
            total_pnl = backtest_result.get("total_pnl_percent", 0)
            sharpe = backtest_result.get("sharpe_ratio", 0)
            max_dd = backtest_result.get("max_drawdown_percent", 0)
            profit_factor = backtest_result.get("profit_factor", 0)
            total_trades = backtest_result.get("total_trades", 0)
            
            # Score formula: balanced between profitability, consistency, and risk
            # Higher is better
            backtest_score = (
                win_rate * 0.25 +                    # Win rate weight
                min(total_pnl, 100) * 0.25 +         # PnL weight (capped at 100%)
                min(sharpe, 3) * 10 +                # Sharpe weight (capped at 3)
                min(profit_factor, 5) * 5 -          # Profit factor weight
                max_dd * 0.5 +                       # Drawdown penalty
                min(total_trades, 50) * 0.1          # Activity bonus
            )
            
            # Update custom_strategies
            cur.execute("""
                UPDATE custom_strategies
                SET win_rate = ?, total_pnl = ?, total_trades = ?, backtest_score = ?, updated_at = ?
                WHERE id = ?
            """, (win_rate, total_pnl, total_trades, backtest_score, int(time.time()), strategy_id))
            
            # Get strategy info
            cur.execute("SELECT name, user_id FROM custom_strategies WHERE id = ?", (strategy_id,))
            row = cur.fetchone()
            if not row:
                return -1
            
            # Update/insert into top_strategies
            cur.execute("""
                INSERT OR REPLACE INTO top_strategies 
                (strategy_type, strategy_id, strategy_name, win_rate, total_pnl, total_trades, 
                 sharpe_ratio, max_drawdown, updated_at)
                VALUES ('custom', ?, ?, ?, ?, ?, ?, ?, ?)
            """, (strategy_id, row["name"], win_rate, total_pnl, total_trades, 
                  sharpe, max_dd, int(time.time())))
            
            conn.commit()
            
            # Recalculate ranks
            RankingService.recalculate_all_ranks()
            
            # Return new rank
            cur.execute("""
                SELECT rank FROM top_strategies WHERE strategy_id = ? AND strategy_type = 'custom'
            """, (strategy_id,))
            row = cur.fetchone()
            return row["rank"] if row else -1
            
        finally:
            conn.close()
    
    @staticmethod
    def recalculate_all_ranks():
        """Recalculate rank positions for all strategies."""
        conn = get_conn()
        try:
            cur = conn.cursor()
            
            # Calculate score and assign ranks
            cur.execute("""
                WITH ranked AS (
                    SELECT id,
                           ROW_NUMBER() OVER (
                               ORDER BY 
                                   (win_rate * 0.3 + total_pnl * 0.3 + sharpe_ratio * 10 - max_drawdown * 0.5) DESC
                           ) as new_rank
                    FROM top_strategies
                )
                UPDATE top_strategies SET rank = (
                    SELECT new_rank FROM ranked WHERE ranked.id = top_strategies.id
                )
            """)
            
            conn.commit()
            
        finally:
            conn.close()
    
    @staticmethod
    def get_global_leaderboard(limit: int = 100, include_private: bool = False) -> List[Dict]:
        """Get global strategy leaderboard."""
        conn = get_conn()
        try:
            cur = conn.cursor()
            
            query = """
                SELECT t.*, 
                       c.user_id as creator_id, c.is_public,
                       m.price_ton, m.price_stars, m.rating as marketplace_rating, m.total_sales
                FROM top_strategies t
                LEFT JOIN custom_strategies c ON t.strategy_id = c.id AND t.strategy_type = 'custom'
                LEFT JOIN strategy_marketplace m ON c.id = m.strategy_id
                WHERE t.strategy_type = 'system' OR c.is_public = 1
            """
            
            if include_private:
                query = query.replace("OR c.is_public = 1", "")
            
            query += " ORDER BY t.rank ASC LIMIT ?"
            
            cur.execute(query, (limit,))
            
            leaderboard = []
            for row in cur.fetchall():
                entry = dict(row)
                entry["is_purchasable"] = bool(entry.get("price_ton") or entry.get("price_stars"))
                leaderboard.append(entry)
            
            return leaderboard
            
        finally:
            conn.close()
    
    @staticmethod
    def get_user_rank(user_id: int) -> Dict:
        """Get user's best strategy rank and overall ranking."""
        conn = get_conn()
        try:
            cur = conn.cursor()
            
            # Get user's best ranked strategy
            cur.execute("""
                SELECT t.rank, t.strategy_name, c.id as strategy_id, t.win_rate, t.total_pnl
                FROM top_strategies t
                JOIN custom_strategies c ON t.strategy_id = c.id
                WHERE c.user_id = ? AND t.strategy_type = 'custom'
                ORDER BY t.rank ASC
                LIMIT 1
            """, (user_id,))
            
            best_strategy = cur.fetchone()
            
            # Get total strategies count for user
            cur.execute("SELECT COUNT(*) as count FROM custom_strategies WHERE user_id = ? AND is_active = 1", 
                       (user_id,))
            row = cur.fetchone()
            total = row["count"] if row else 0
            
            # Get total earnings from sales
            cur.execute("""
                SELECT SUM(seller_share) as total_earnings
                FROM strategy_purchases
                WHERE seller_id = ?
            """, (user_id,))
            row = cur.fetchone()
            earnings = row["total_earnings"] if row and row["total_earnings"] else 0
            
            return {
                "best_rank": best_strategy["rank"] if best_strategy else None,
                "best_strategy": dict(best_strategy) if best_strategy else None,
                "total_strategies": total,
                "total_earnings": earnings
            }
            
        finally:
            conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# LIVE BACKTEST TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

class BacktestTracker:
    """
    Tracks live backtest progress for visualization in terminal.
    Stores trades, equity curve, and signals for replay.
    """
    
    # In-memory cache for active backtests
    _active_backtests: Dict[str, Dict] = {}
    
    @classmethod
    def start_backtest(cls, backtest_id: str, strategy: str, symbol: str, 
                        timeframe: str, initial_balance: float) -> None:
        """Initialize a new backtest tracking session."""
        cls._active_backtests[backtest_id] = {
            "strategy": strategy,
            "symbol": symbol,
            "timeframe": timeframe,
            "initial_balance": initial_balance,
            "current_balance": initial_balance,
            "start_time": time.time(),
            "trades": [],
            "signals": [],
            "equity_curve": [{"time": time.time(), "equity": initial_balance}],
            "current_position": None,
            "status": "running"
        }
    
    @classmethod
    def add_signal(cls, backtest_id: str, signal: Dict) -> None:
        """Record a signal during backtest."""
        if backtest_id in cls._active_backtests:
            cls._active_backtests[backtest_id]["signals"].append({
                **signal,
                "timestamp": time.time()
            })
    
    @classmethod
    def add_trade(cls, backtest_id: str, trade: Dict) -> None:
        """Record a completed trade."""
        if backtest_id in cls._active_backtests:
            bt = cls._active_backtests[backtest_id]
            bt["trades"].append(trade)
            bt["current_balance"] += trade.get("pnl", 0)
            bt["equity_curve"].append({
                "time": time.time(),
                "equity": bt["current_balance"]
            })
    
    @classmethod
    def update_position(cls, backtest_id: str, position: Optional[Dict]) -> None:
        """Update current open position."""
        if backtest_id in cls._active_backtests:
            cls._active_backtests[backtest_id]["current_position"] = position
    
    @classmethod
    def complete_backtest(cls, backtest_id: str, result: Dict) -> None:
        """Mark backtest as complete and save full results."""
        if backtest_id in cls._active_backtests:
            bt = cls._active_backtests[backtest_id]
            bt["status"] = "completed"
            bt["result"] = result
            bt["end_time"] = time.time()
    
    @classmethod
    def get_backtest_state(cls, backtest_id: str) -> Optional[Dict]:
        """Get current state of a backtest for live visualization."""
        return cls._active_backtests.get(backtest_id)
    
    @classmethod
    def cleanup_old_backtests(cls, max_age: int = 3600) -> None:
        """Remove old completed backtests from memory."""
        now = time.time()
        to_remove = []
        for bid, bt in cls._active_backtests.items():
            if bt["status"] == "completed" and now - bt.get("end_time", now) > max_age:
                to_remove.append(bid)
        for bid in to_remove:
            del cls._active_backtests[bid]


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def sync_bot_settings_to_webapp(user_id: int) -> Dict:
    """
    Pull current bot settings and format for webapp.
    Called when user opens settings page.
    """
    return StrategySyncService.get_user_strategies(user_id)


def sync_webapp_settings_to_bot(user_id: int, strategy_id: str, 
                                  settings: Dict, strategy_type: str = "system") -> bool:
    """
    Push webapp settings changes to bot.
    Called when user saves settings in webapp.
    """
    return StrategySyncService.update_strategy_settings(
        user_id, strategy_id, settings, strategy_type
    )


def get_tradeable_strategies(user_id: int) -> List[Dict]:
    """
    Get all strategies that are enabled and ready for trading.
    Used by bot's signal processor.
    """
    return StrategySyncService.get_active_strategies_for_trading(user_id)


def update_rankings_after_backtest(strategy_id: int, result: Dict) -> int:
    """
    Update strategy rankings after backtest completes.
    Returns new rank position.
    """
    return RankingService.update_strategy_rank(strategy_id, result)


def get_leaderboard(limit: int = 100) -> List[Dict]:
    """Get global strategy leaderboard."""
    return RankingService.get_global_leaderboard(limit)
