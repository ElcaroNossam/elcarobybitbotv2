"""
Strategy Marketplace - Share and trade strategies between users
"""
import json
import sqlite3
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

DB_FILE = Path(__file__).parent.parent / "bot.db"


class StrategyVisibility(Enum):
    PRIVATE = "private"       # Only owner can see
    PUBLIC = "public"         # Anyone can see and copy
    PREMIUM = "premium"       # Requires payment/subscription


class StrategyCategory(Enum):
    SCALPING = "scalping"
    SWING = "swing"
    DAY_TRADING = "day_trading"
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    DCA = "dca"
    CUSTOM = "custom"


@dataclass
class SharedStrategy:
    """A strategy configuration that can be shared"""
    id: int
    owner_id: int
    owner_name: str
    name: str
    description: str
    base_strategy: str  # elcaro, wyckoff, etc
    category: StrategyCategory
    visibility: StrategyVisibility
    
    # Configuration
    params: Dict[str, Any]
    symbols: List[str]
    timeframe: str
    
    # Performance (from backtest or live)
    win_rate: float
    profit_factor: float
    total_pnl_percent: float
    max_drawdown: float
    total_trades: int
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    copies_count: int = 0
    rating: float = 0.0
    ratings_count: int = 0
    
    # Optional
    tags: List[str] = field(default_factory=list)
    backtest_results: Dict = field(default_factory=dict)


@dataclass 
class StrategyPreset:
    """User's saved strategy preset (personal settings snapshot)"""
    id: int
    user_id: int
    name: str
    description: str
    
    # All strategy settings at time of save
    settings: Dict[str, Any]
    
    created_at: datetime
    is_active: bool = False


class StrategyMarketplace:
    """
    Marketplace for sharing, copying, and rating strategies.
    """
    
    def __init__(self):
        self._init_tables()
    
    def _get_conn(self):
        conn = sqlite3.connect(str(DB_FILE), timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_tables(self):
        """Initialize marketplace tables"""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            
            # Shared strategies table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS shared_strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner_id INTEGER NOT NULL,
                    owner_name TEXT,
                    name TEXT NOT NULL,
                    description TEXT,
                    base_strategy TEXT NOT NULL,
                    category TEXT DEFAULT 'custom',
                    visibility TEXT DEFAULT 'public',
                    params_json TEXT,
                    symbols_json TEXT,
                    timeframe TEXT DEFAULT '15m',
                    win_rate REAL DEFAULT 0,
                    profit_factor REAL DEFAULT 0,
                    total_pnl_percent REAL DEFAULT 0,
                    max_drawdown REAL DEFAULT 0,
                    total_trades INTEGER DEFAULT 0,
                    copies_count INTEGER DEFAULT 0,
                    rating REAL DEFAULT 0,
                    ratings_count INTEGER DEFAULT 0,
                    tags_json TEXT,
                    backtest_results_json TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    UNIQUE(owner_id, name)
                )
            """)
            
            # Strategy copies tracking
            cur.execute("""
                CREATE TABLE IF NOT EXISTS strategy_copies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    copied_at TEXT,
                    is_active INTEGER DEFAULT 1,
                    UNIQUE(strategy_id, user_id),
                    FOREIGN KEY(strategy_id) REFERENCES shared_strategies(id)
                )
            """)
            
            # Strategy ratings
            cur.execute("""
                CREATE TABLE IF NOT EXISTS strategy_ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                    comment TEXT,
                    rated_at TEXT,
                    UNIQUE(strategy_id, user_id),
                    FOREIGN KEY(strategy_id) REFERENCES shared_strategies(id)
                )
            """)
            
            # User presets (personal settings snapshots)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_presets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    settings_json TEXT,
                    created_at TEXT,
                    is_active INTEGER DEFAULT 0,
                    UNIQUE(user_id, name)
                )
            """)
            
            # Strategy deployments (from backtest to live)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS strategy_deployments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    strategy TEXT NOT NULL,
                    params TEXT,
                    backtest_results TEXT,
                    deployed_at TEXT,
                    is_active INTEGER DEFAULT 1,
                    live_pnl REAL DEFAULT 0,
                    live_trades INTEGER DEFAULT 0,
                    UNIQUE(user_id, strategy)
                )
            """)
            
            conn.commit()
            logger.info("Marketplace tables initialized")
            
        except Exception as e:
            logger.error(f"Failed to init marketplace tables: {e}")
        finally:
            conn.close()
    
    # =========================================================================
    # STRATEGY SHARING
    # =========================================================================
    
    def share_strategy(
        self,
        owner_id: int,
        owner_name: str,
        name: str,
        description: str,
        base_strategy: str,
        params: Dict,
        symbols: List[str],
        timeframe: str = "15m",
        category: str = "custom",
        visibility: str = "public",
        backtest_results: Dict = None,
        tags: List[str] = None
    ) -> Optional[int]:
        """
        Share a strategy configuration to the marketplace.
        Returns strategy ID or None on error.
        """
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            
            now = datetime.now().isoformat()
            
            # Extract performance from backtest results
            win_rate = backtest_results.get("win_rate", 0) if backtest_results else 0
            profit_factor = backtest_results.get("profit_factor", 0) if backtest_results else 0
            total_pnl = backtest_results.get("total_pnl_percent", 0) if backtest_results else 0
            max_dd = backtest_results.get("max_drawdown_percent", 0) if backtest_results else 0
            total_trades = backtest_results.get("total_trades", 0) if backtest_results else 0
            
            cur.execute("""
                INSERT OR REPLACE INTO shared_strategies 
                (owner_id, owner_name, name, description, base_strategy, category, visibility,
                 params_json, symbols_json, timeframe, win_rate, profit_factor, total_pnl_percent,
                 max_drawdown, total_trades, tags_json, backtest_results_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                owner_id, owner_name, name, description, base_strategy, category, visibility,
                json.dumps(params), json.dumps(symbols), timeframe,
                win_rate, profit_factor, total_pnl, max_dd, total_trades,
                json.dumps(tags or []), json.dumps(backtest_results or {}),
                now, now
            ))
            
            conn.commit()
            strategy_id = cur.lastrowid
            
            logger.info(f"Strategy '{name}' shared by user {owner_id}, id={strategy_id}")
            return strategy_id
            
        except Exception as e:
            logger.error(f"Failed to share strategy: {e}")
            return None
        finally:
            conn.close()
    
    def get_strategy(self, strategy_id: int) -> Optional[SharedStrategy]:
        """Get a shared strategy by ID"""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM shared_strategies WHERE id = ?", (strategy_id,))
            row = cur.fetchone()
            
            if row:
                return self._row_to_strategy(row)
            return None
            
        finally:
            conn.close()
    
    def search_strategies(
        self,
        query: str = None,
        category: str = None,
        base_strategy: str = None,
        min_win_rate: float = None,
        min_profit_factor: float = None,
        visibility: str = "public",
        sort_by: str = "rating",  # rating, copies, win_rate, profit_factor, pnl, recent
        limit: int = 50,
        offset: int = 0
    ) -> List[SharedStrategy]:
        """Search and filter strategies in the marketplace"""
        conn = self._get_conn()
        try:
            conditions = ["visibility = ?"]
            params = [visibility]
            
            if query:
                conditions.append("(name LIKE ? OR description LIKE ? OR tags_json LIKE ?)")
                q = f"%{query}%"
                params.extend([q, q, q])
            
            if category:
                conditions.append("category = ?")
                params.append(category)
            
            if base_strategy:
                conditions.append("base_strategy = ?")
                params.append(base_strategy)
            
            if min_win_rate is not None:
                conditions.append("win_rate >= ?")
                params.append(min_win_rate)
            
            if min_profit_factor is not None:
                conditions.append("profit_factor >= ?")
                params.append(min_profit_factor)
            
            # Build ORDER BY
            order_map = {
                "rating": "rating DESC, ratings_count DESC",
                "copies": "copies_count DESC",
                "win_rate": "win_rate DESC",
                "profit_factor": "profit_factor DESC",
                "pnl": "total_pnl_percent DESC",
                "recent": "created_at DESC"
            }
            order_by = order_map.get(sort_by, "rating DESC")
            
            sql = f"""
                SELECT * FROM shared_strategies
                WHERE {' AND '.join(conditions)}
                ORDER BY {order_by}
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])
            
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
            
            return [self._row_to_strategy(r) for r in rows]
            
        finally:
            conn.close()
    
    def copy_strategy(self, strategy_id: int, user_id: int) -> Dict:
        """
        Copy a strategy to user's account.
        Returns the strategy params to apply.
        """
        import db
        
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            
            # Get strategy
            cur.execute("SELECT * FROM shared_strategies WHERE id = ?", (strategy_id,))
            row = cur.fetchone()
            
            if not row:
                return {"success": False, "error": "Strategy not found"}
            
            if row["visibility"] == "private" and row["owner_id"] != user_id:
                return {"success": False, "error": "Strategy is private"}
            
            # Record copy
            now = datetime.now().isoformat()
            cur.execute("""
                INSERT OR REPLACE INTO strategy_copies (strategy_id, user_id, copied_at, is_active)
                VALUES (?, ?, ?, 1)
            """, (strategy_id, user_id, now))
            
            # Increment copies count
            cur.execute("""
                UPDATE shared_strategies SET copies_count = copies_count + 1 WHERE id = ?
            """, (strategy_id,))
            
            conn.commit()
            
            # Parse params
            params = json.loads(row["params_json"]) if row["params_json"] else {}
            
            # Apply to user settings
            self._apply_strategy_to_user(user_id, row["base_strategy"], params)
            
            logger.info(f"User {user_id} copied strategy {strategy_id}")
            
            return {
                "success": True,
                "strategy": row["name"],
                "base_strategy": row["base_strategy"],
                "params": params
            }
            
        except Exception as e:
            logger.error(f"Failed to copy strategy: {e}")
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def _apply_strategy_to_user(self, user_id: int, base_strategy: str, params: Dict):
        """Apply strategy params to user's settings"""
        import db
        
        # Enable the base strategy
        strategy_field = f"trade_{base_strategy}"
        db.set_user_field(user_id, strategy_field, 1)
        
        # Apply params
        if "stop_loss_percent" in params:
            db.set_user_field(user_id, "sl_percent", params["stop_loss_percent"])
        if "take_profit_percent" in params:
            db.set_user_field(user_id, "tp_percent", params["take_profit_percent"])
        if "leverage" in params:
            db.set_user_field(user_id, "leverage", params["leverage"])
        if "percent" in params:
            db.set_user_field(user_id, "percent", params["percent"])
        
        # Save strategy-specific settings
        current = db.get_user_field(user_id, "strategy_settings")
        try:
            settings = json.loads(current) if current else {}
        except:
            settings = {}
        settings[base_strategy] = params
        db.set_user_field(user_id, "strategy_settings", json.dumps(settings))
    
    def rate_strategy(self, strategy_id: int, user_id: int, rating: int, comment: str = None) -> bool:
        """Rate a strategy (1-5 stars)"""
        if rating < 1 or rating > 5:
            return False
        
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            now = datetime.now().isoformat()
            
            # Save/update rating
            cur.execute("""
                INSERT OR REPLACE INTO strategy_ratings (strategy_id, user_id, rating, comment, rated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (strategy_id, user_id, rating, comment, now))
            
            # Recalculate average rating
            cur.execute("""
                SELECT AVG(rating) as avg_rating, COUNT(*) as count
                FROM strategy_ratings WHERE strategy_id = ?
            """, (strategy_id,))
            result = cur.fetchone()
            
            cur.execute("""
                UPDATE shared_strategies 
                SET rating = ?, ratings_count = ?
                WHERE id = ?
            """, (result["avg_rating"], result["count"], strategy_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to rate strategy: {e}")
            return False
        finally:
            conn.close()
    
    # =========================================================================
    # USER PRESETS (Personal Settings Snapshots)
    # =========================================================================
    
    def save_preset(self, user_id: int, name: str, description: str = None) -> Optional[int]:
        """
        Save current user settings as a named preset.
        User can have multiple presets and switch between them.
        """
        import db
        
        conn = self._get_conn()
        try:
            # Get current user settings
            creds = db.get_all_user_credentials(user_id)
            
            settings = {
                # Trading settings
                "percent": creds.get("percent", 5),
                "leverage": creds.get("leverage", 10),
                "tp_percent": creds.get("tp_percent", 2),
                "sl_percent": creds.get("sl_percent", 1),
                "trading_mode": creds.get("trading_mode", "demo"),
                
                # Strategy toggles
                "trade_oi": creds.get("trade_oi", 0),
                "trade_rsi_bb": creds.get("trade_rsi_bb", 0),
                "trade_scryptomera": creds.get("trade_scryptomera", 0),
                "trade_scalper": creds.get("trade_scalper", 0),
                "trade_elcaro": creds.get("trade_elcaro", 0),
                "trade_wyckoff": creds.get("trade_wyckoff", 0),
                
                # Strategy-specific settings
                "strategy_settings": creds.get("strategy_settings"),
                
                # Other
                "use_atr": creds.get("use_atr", 0),
                "dca_enabled": creds.get("dca_enabled", 0),
                "limit_ladder_enabled": creds.get("limit_ladder_enabled", 0),
            }
            
            now = datetime.now().isoformat()
            
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO user_presets (user_id, name, description, settings_json, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, name, description, json.dumps(settings), now))
            
            conn.commit()
            
            logger.info(f"User {user_id} saved preset '{name}'")
            return cur.lastrowid
            
        except Exception as e:
            logger.error(f"Failed to save preset: {e}")
            return None
        finally:
            conn.close()
    
    def load_preset(self, user_id: int, preset_id: int) -> Dict:
        """Load a saved preset and apply it to user settings"""
        import db
        
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM user_presets WHERE id = ? AND user_id = ?
            """, (preset_id, user_id))
            row = cur.fetchone()
            
            if not row:
                return {"success": False, "error": "Preset not found"}
            
            settings = json.loads(row["settings_json"]) if row["settings_json"] else {}
            
            # Apply settings
            for key, value in settings.items():
                if key in db.USER_FIELDS_WHITELIST:
                    db.set_user_field(user_id, key, value)
            
            # Mark as active preset
            cur.execute("UPDATE user_presets SET is_active = 0 WHERE user_id = ?", (user_id,))
            cur.execute("UPDATE user_presets SET is_active = 1 WHERE id = ?", (preset_id,))
            conn.commit()
            
            logger.info(f"User {user_id} loaded preset '{row['name']}'")
            
            return {
                "success": True,
                "preset": row["name"],
                "settings": settings
            }
            
        except Exception as e:
            logger.error(f"Failed to load preset: {e}")
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def get_user_presets(self, user_id: int) -> List[Dict]:
        """Get all presets for a user"""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, name, description, created_at, is_active
                FROM user_presets WHERE user_id = ?
                ORDER BY is_active DESC, created_at DESC
            """, (user_id,))
            
            return [dict(r) for r in cur.fetchall()]
            
        finally:
            conn.close()
    
    def delete_preset(self, user_id: int, preset_id: int) -> bool:
        """Delete a user preset"""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM user_presets WHERE id = ? AND user_id = ?", (preset_id, user_id))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()
    
    def export_settings(self, user_id: int) -> Dict:
        """
        Export all user settings as a shareable JSON.
        Can be used to transfer settings to another account or share with others.
        """
        import db
        
        creds = db.get_all_user_credentials(user_id)
        
        # Build export object (exclude sensitive data)
        export = {
            "version": "2.0",
            "exported_at": datetime.now().isoformat(),
            "settings": {
                "trading": {
                    "percent": creds.get("percent", 5),
                    "leverage": creds.get("leverage", 10),
                    "tp_percent": creds.get("tp_percent", 2),
                    "sl_percent": creds.get("sl_percent", 1),
                },
                "strategies": {
                    "oi": bool(creds.get("trade_oi")),
                    "rsi_bb": bool(creds.get("trade_rsi_bb")),
                    "scryptomera": bool(creds.get("trade_scryptomera")),
                    "scalper": bool(creds.get("trade_scalper")),
                    "elcaro": bool(creds.get("trade_elcaro")),
                    "wyckoff": bool(creds.get("trade_wyckoff")),
                },
                "strategy_params": json.loads(creds.get("strategy_settings", "{}")) if creds.get("strategy_settings") else {},
                "features": {
                    "use_atr": bool(creds.get("use_atr")),
                    "dca_enabled": bool(creds.get("dca_enabled")),
                    "limit_ladder_enabled": bool(creds.get("limit_ladder_enabled")),
                }
            }
        }
        
        # Generate checksum
        export["checksum"] = hashlib.sha256(json.dumps(export["settings"]).encode()).hexdigest()[:8]
        
        return export
    
    def import_settings(self, user_id: int, export_data: Dict) -> Dict:
        """Import settings from exported JSON"""
        import db
        
        try:
            if export_data.get("version") != "2.0":
                return {"success": False, "error": "Incompatible settings version"}
            
            settings = export_data.get("settings", {})
            
            # Apply trading settings
            trading = settings.get("trading", {})
            for key in ["percent", "leverage", "tp_percent", "sl_percent"]:
                if key in trading:
                    db.set_user_field(user_id, key, trading[key])
            
            # Apply strategy toggles
            strategies = settings.get("strategies", {})
            strategy_map = {
                "oi": "trade_oi",
                "rsi_bb": "trade_rsi_bb",
                "scryptomera": "trade_scryptomera",
                "scalper": "trade_scalper",
                "elcaro": "trade_elcaro",
                "wyckoff": "trade_wyckoff",
            }
            for key, field in strategy_map.items():
                if key in strategies:
                    db.set_user_field(user_id, field, 1 if strategies[key] else 0)
            
            # Apply strategy params
            params = settings.get("strategy_params", {})
            if params:
                db.set_user_field(user_id, "strategy_settings", json.dumps(params))
            
            # Apply features
            features = settings.get("features", {})
            for key in ["use_atr", "dca_enabled", "limit_ladder_enabled"]:
                if key in features:
                    db.set_user_field(user_id, key, 1 if features[key] else 0)
            
            logger.info(f"User {user_id} imported settings")
            
            return {"success": True, "imported": list(settings.keys())}
            
        except Exception as e:
            logger.error(f"Failed to import settings: {e}")
            return {"success": False, "error": str(e)}
    
    def _row_to_strategy(self, row) -> SharedStrategy:
        """Convert database row to SharedStrategy object"""
        return SharedStrategy(
            id=row["id"],
            owner_id=row["owner_id"],
            owner_name=row["owner_name"] or "Anonymous",
            name=row["name"],
            description=row["description"] or "",
            base_strategy=row["base_strategy"],
            category=StrategyCategory(row["category"]) if row["category"] else StrategyCategory.CUSTOM,
            visibility=StrategyVisibility(row["visibility"]) if row["visibility"] else StrategyVisibility.PUBLIC,
            params=json.loads(row["params_json"]) if row["params_json"] else {},
            symbols=json.loads(row["symbols_json"]) if row["symbols_json"] else [],
            timeframe=row["timeframe"] or "15m",
            win_rate=row["win_rate"] or 0,
            profit_factor=row["profit_factor"] or 0,
            total_pnl_percent=row["total_pnl_percent"] or 0,
            max_drawdown=row["max_drawdown"] or 0,
            total_trades=row["total_trades"] or 0,
            copies_count=row["copies_count"] or 0,
            rating=row["rating"] or 0,
            ratings_count=row["ratings_count"] or 0,
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.now(),
            tags=json.loads(row["tags_json"]) if row["tags_json"] else [],
            backtest_results=json.loads(row["backtest_results_json"]) if row["backtest_results_json"] else {}
        )


# Global instance
marketplace = StrategyMarketplace()
