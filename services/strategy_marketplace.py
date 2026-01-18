"""
Strategy Marketplace - Share and trade strategies between users

PostgreSQL ONLY - No SQLite support
"""
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# PostgreSQL imports
from core.db_postgres import get_pool, get_conn, execute, execute_one, execute_write

logger = logging.getLogger(__name__)


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


class StrategyMarketplace:
    """
    Marketplace for sharing, copying, and rating strategies.
    PostgreSQL only.
    """
    
    def __init__(self):
        try:
            self._init_tables()
        except Exception as e:
            logger.warning(f"Could not init marketplace tables: {e}")
    
    def _init_tables(self):
        """Initialize marketplace tables"""
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Shared strategies table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS shared_strategies (
                        id SERIAL PRIMARY KEY,
                        owner_id BIGINT NOT NULL,
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
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(owner_id, name)
                    )
                """)
                
                # Strategy copies tracking
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS strategy_copies (
                        id SERIAL PRIMARY KEY,
                        strategy_id INTEGER NOT NULL,
                        user_id BIGINT NOT NULL,
                        copied_at TIMESTAMP DEFAULT NOW(),
                        is_active BOOLEAN DEFAULT TRUE,
                        UNIQUE(strategy_id, user_id)
                    )
                """)
                
                # Strategy ratings
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS strategy_ratings (
                        id SERIAL PRIMARY KEY,
                        strategy_id INTEGER NOT NULL,
                        user_id BIGINT NOT NULL,
                        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                        comment TEXT,
                        rated_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(strategy_id, user_id)
                    )
                """)
                
                # User presets (personal settings snapshots)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_presets (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        name TEXT NOT NULL,
                        description TEXT,
                        settings_json TEXT,
                        created_at TIMESTAMP DEFAULT NOW(),
                        is_active BOOLEAN DEFAULT FALSE,
                        UNIQUE(user_id, name)
                    )
                """)
                
                # Strategy deployments (from backtest to live)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS strategy_deployments (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        strategy TEXT NOT NULL,
                        params TEXT,
                        backtest_results TEXT,
                        deployed_at TIMESTAMP DEFAULT NOW(),
                        is_active BOOLEAN DEFAULT TRUE,
                        live_pnl REAL DEFAULT 0,
                        live_trades INTEGER DEFAULT 0,
                        UNIQUE(user_id, strategy)
                    )
                """)
                
        logger.info("Marketplace tables initialized")
    
    def _row_to_strategy(self, row: Dict) -> SharedStrategy:
        """Convert database row to SharedStrategy object"""
        return SharedStrategy(
            id=row["id"],
            owner_id=row["owner_id"],
            owner_name=row.get("owner_name") or "Unknown",
            name=row["name"],
            description=row.get("description") or "",
            base_strategy=row["base_strategy"],
            category=StrategyCategory(row.get("category") or "custom"),
            visibility=StrategyVisibility(row.get("visibility") or "public"),
            params=json.loads(row.get("params_json") or "{}"),
            symbols=json.loads(row.get("symbols_json") or "[]"),
            timeframe=row.get("timeframe") or "15m",
            win_rate=row.get("win_rate") or 0,
            profit_factor=row.get("profit_factor") or 0,
            total_pnl_percent=row.get("total_pnl_percent") or 0,
            max_drawdown=row.get("max_drawdown") or 0,
            total_trades=row.get("total_trades") or 0,
            created_at=row.get("created_at") or datetime.now(),
            updated_at=row.get("updated_at") or datetime.now(),
            copies_count=row.get("copies_count") or 0,
            rating=row.get("rating") or 0,
            ratings_count=row.get("ratings_count") or 0,
            tags=json.loads(row.get("tags_json") or "[]"),
            backtest_results=json.loads(row.get("backtest_results_json") or "{}")
        )
    
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
        conn = _get_conn()
        try:
            cur = conn.cursor()
            
            # Extract performance from backtest results
            win_rate = backtest_results.get("win_rate", 0) if backtest_results else 0
            profit_factor = backtest_results.get("profit_factor", 0) if backtest_results else 0
            total_pnl = backtest_results.get("total_pnl_percent", 0) if backtest_results else 0
            max_dd = backtest_results.get("max_drawdown_percent", 0) if backtest_results else 0
            total_trades = backtest_results.get("total_trades", 0) if backtest_results else 0
            
            cur.execute("""
                INSERT INTO shared_strategies 
                (owner_id, owner_name, name, description, base_strategy, category, visibility,
                 params_json, symbols_json, timeframe, win_rate, profit_factor, total_pnl_percent,
                 max_drawdown, total_trades, tags_json, backtest_results_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (owner_id, name) DO UPDATE SET
                    description = EXCLUDED.description,
                    params_json = EXCLUDED.params_json,
                    symbols_json = EXCLUDED.symbols_json,
                    win_rate = EXCLUDED.win_rate,
                    profit_factor = EXCLUDED.profit_factor,
                    total_pnl_percent = EXCLUDED.total_pnl_percent,
                    max_drawdown = EXCLUDED.max_drawdown,
                    total_trades = EXCLUDED.total_trades,
                    backtest_results_json = EXCLUDED.backtest_results_json,
                    updated_at = NOW()
                RETURNING id
            """, (
                owner_id, owner_name, name, description, base_strategy, category, visibility,
                json.dumps(params), json.dumps(symbols), timeframe,
                win_rate, profit_factor, total_pnl, max_dd, total_trades,
                json.dumps(tags or []), json.dumps(backtest_results or {})
            ))
            
            row = cur.fetchone()
            conn.commit()
            strategy_id = row[0] if row else None
            
            logger.info(f"Strategy '{name}' shared by user {owner_id}, id={strategy_id}")
            return strategy_id
            
        except Exception as e:
            logger.error(f"Failed to share strategy: {e}")
            conn.rollback()
            return None
        finally:
            _release_conn(conn)
    
    def get_strategy(self, strategy_id: int) -> Optional[SharedStrategy]:
        """Get a shared strategy by ID"""
        row = execute_one("SELECT * FROM shared_strategies WHERE id = %s", (strategy_id,))
        if row:
            return self._row_to_strategy(row)
        return None
    
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
        conditions = ["visibility = %s"]
        params = [visibility]
        
        if query:
            conditions.append("(name ILIKE %s OR description ILIKE %s OR tags_json ILIKE %s)")
            q = f"%{query}%"
            params.extend([q, q, q])
        
        if category:
            conditions.append("category = %s")
            params.append(category)
        
        if base_strategy:
            conditions.append("base_strategy = %s")
            params.append(base_strategy)
        
        if min_win_rate is not None:
            conditions.append("win_rate >= %s")
            params.append(min_win_rate)
        
        if min_profit_factor is not None:
            conditions.append("profit_factor >= %s")
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
        
        where_clause = " AND ".join(conditions)
        params.extend([limit, offset])
        
        rows = execute(f"""
            SELECT * FROM shared_strategies 
            WHERE {where_clause}
            ORDER BY {order_by}
            LIMIT %s OFFSET %s
        """, tuple(params))
        
        return [self._row_to_strategy(row) for row in rows]
    
    def get_top_strategies(self, limit: int = 10) -> List[SharedStrategy]:
        """Get top rated public strategies"""
        return self.search_strategies(visibility="public", sort_by="rating", limit=limit)
    
    def get_user_strategies(self, user_id: int) -> List[SharedStrategy]:
        """Get all strategies owned by a user"""
        rows = execute("""
            SELECT * FROM shared_strategies 
            WHERE owner_id = %s
            ORDER BY updated_at DESC
        """, (user_id,))
        
        return [self._row_to_strategy(row) for row in rows]
    
    def delete_strategy(self, strategy_id: int, owner_id: int) -> bool:
        """Delete a strategy (only owner can delete)"""
        count = execute_write("""
            DELETE FROM shared_strategies 
            WHERE id = %s AND owner_id = %s
        """, (strategy_id, owner_id))
        return count > 0
    
    # =========================================================================
    # STRATEGY COPYING
    # =========================================================================
    
    def copy_strategy(self, strategy_id: int, user_id: int) -> bool:
        """Copy a strategy to user's collection"""
        conn = _get_conn()
        try:
            cur = conn.cursor()
            
            # Insert copy record
            cur.execute("""
                INSERT INTO strategy_copies (strategy_id, user_id)
                VALUES (%s, %s)
                ON CONFLICT (strategy_id, user_id) DO UPDATE SET is_active = TRUE
            """, (strategy_id, user_id))
            
            # Increment copies count
            cur.execute("""
                UPDATE shared_strategies 
                SET copies_count = copies_count + 1
                WHERE id = %s
            """, (strategy_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy strategy: {e}")
            conn.rollback()
            return False
        finally:
            _release_conn(conn)
    
    def get_copied_strategies(self, user_id: int) -> List[SharedStrategy]:
        """Get all strategies copied by a user"""
        rows = execute("""
            SELECT s.* FROM shared_strategies s
            JOIN strategy_copies c ON s.id = c.strategy_id
            WHERE c.user_id = %s AND c.is_active = TRUE
            ORDER BY c.copied_at DESC
        """, (user_id,))
        
        return [self._row_to_strategy(row) for row in rows]
    
    # =========================================================================
    # STRATEGY RATINGS
    # =========================================================================
    
    def rate_strategy(self, strategy_id: int, user_id: int, rating: int, comment: str = None) -> bool:
        """Rate a strategy (1-5 stars)"""
        if not 1 <= rating <= 5:
            return False
        
        conn = _get_conn()
        try:
            cur = conn.cursor()
            
            # Insert or update rating
            cur.execute("""
                INSERT INTO strategy_ratings (strategy_id, user_id, rating, comment)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (strategy_id, user_id) DO UPDATE SET 
                    rating = EXCLUDED.rating,
                    comment = EXCLUDED.comment,
                    rated_at = NOW()
            """, (strategy_id, user_id, rating, comment))
            
            # Update average rating in strategy
            cur.execute("""
                UPDATE shared_strategies 
                SET rating = (SELECT AVG(rating) FROM strategy_ratings WHERE strategy_id = %s),
                    ratings_count = (SELECT COUNT(*) FROM strategy_ratings WHERE strategy_id = %s)
                WHERE id = %s
            """, (strategy_id, strategy_id, strategy_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to rate strategy: {e}")
            conn.rollback()
            return False
        finally:
            _release_conn(conn)
    
    def get_strategy_ratings(self, strategy_id: int, limit: int = 50) -> List[Dict]:
        """Get ratings for a strategy"""
        return execute("""
            SELECT user_id, rating, comment, rated_at
            FROM strategy_ratings
            WHERE strategy_id = %s
            ORDER BY rated_at DESC
            LIMIT %s
        """, (strategy_id, limit))
    
    # =========================================================================
    # USER PRESETS
    # =========================================================================
    
    def save_preset(
        self, 
        user_id: int, 
        name: str, 
        settings: Dict,
        description: str = None
    ) -> Optional[int]:
        """Save current settings as a preset"""
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO user_presets (user_id, name, description, settings_json)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, name) DO UPDATE SET
                    description = EXCLUDED.description,
                    settings_json = EXCLUDED.settings_json
                RETURNING id
            """, (user_id, name, description, json.dumps(settings)))
            
            row = cur.fetchone()
            conn.commit()
            return row[0] if row else None
            
        except Exception as e:
            logger.error(f"Failed to save preset: {e}")
            conn.rollback()
            return None
        finally:
            _release_conn(conn)
    
    def get_presets(self, user_id: int) -> List[Dict]:
        """Get all presets for a user"""
        return execute("""
            SELECT id, name, description, settings_json, created_at, is_active
            FROM user_presets
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
    
    def load_preset(self, user_id: int, preset_id: int) -> Optional[Dict]:
        """Load a preset's settings"""
        row = execute_one("""
            SELECT settings_json FROM user_presets
            WHERE id = %s AND user_id = %s
        """, (preset_id, user_id))
        
        if row:
            return json.loads(row.get("settings_json") or "{}")
        return None
    
    def delete_preset(self, user_id: int, preset_id: int) -> bool:
        """Delete a preset"""
        count = execute_write("""
            DELETE FROM user_presets
            WHERE id = %s AND user_id = %s
        """, (preset_id, user_id))
        return count > 0


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_marketplace_instance: Optional[StrategyMarketplace] = None

def get_marketplace() -> StrategyMarketplace:
    """Get singleton marketplace instance"""
    global _marketplace_instance
    if _marketplace_instance is None:
        _marketplace_instance = StrategyMarketplace()
    return _marketplace_instance


# Alias for backward compatibility
marketplace = get_marketplace()


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def share_strategy(owner_id: int, name: str, **kwargs) -> Optional[int]:
    """Share a strategy to marketplace"""
    return get_marketplace().share_strategy(owner_id=owner_id, name=name, **kwargs)

def search_strategies(query: str = None, **kwargs) -> List[SharedStrategy]:
    """Search strategies in marketplace"""
    return get_marketplace().search_strategies(query=query, **kwargs)

def copy_strategy(strategy_id: int, user_id: int) -> bool:
    """Copy a strategy"""
    return get_marketplace().copy_strategy(strategy_id, user_id)

def rate_strategy(strategy_id: int, user_id: int, rating: int, comment: str = None) -> bool:
    """Rate a strategy"""
    return get_marketplace().rate_strategy(strategy_id, user_id, rating, comment)
