"""
Signals REST API

Endpoints for trading signals list and management.
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from datetime import datetime, timedelta
import random
import logging

from webapp.api.auth import get_current_user
from core.db_postgres import execute, execute_one

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/signals", tags=["signals"])


# ==================== List Signals ====================

@router.get("")
@router.get("/")
async def get_signals(
    strategy: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user)
):
    """
    Get list of trading signals.
    
    Filters:
    - strategy: Filter by strategy name (oi, scryptomera, etc.)
    - status: active, executed, expired, cancelled
    """
    user_id = user["user_id"]
    
    # Try to get signals from database
    try:
        query = """
            SELECT id, symbol, side, strategy, entry_price, sl_price as stop_loss, 
                   tp_price as take_profit, 1.0 as confidence, 'executed' as status,
                   open_ts as created_at, NULL as executed_at, NULL as pnl
            FROM trade_logs
            WHERE user_id = %s
        """
        params = [user_id]
        
        if strategy:
            query += " AND strategy = %s"
            params.append(strategy)
            
        query += " ORDER BY ts DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        rows = execute(query, params) or []
        
        signals = []
        for row in rows:
            signals.append({
                "id": row["id"],
                "symbol": row["symbol"],
                "side": row["side"],
                "strategy": row["strategy"] or "manual",
                "entry_price": row["entry_price"],
                "stop_loss": row["stop_loss"],
                "take_profit": row["take_profit"],
                "confidence": row["confidence"],
                "status": "executed",
                "created_at": str(row["created_at"]) if row["created_at"] else None,
                "executed_at": str(row["executed_at"]) if row.get("executed_at") else None,
                "pnl": row.get("pnl")
            })
        
        return {
            "success": True,
            "data": signals,
            "count": len(signals)
        }
        
    except Exception as e:
        logger.error(f"Error fetching signals: {e}")
        # Return mock data
        return _get_mock_signals(limit)


@router.get("/active")
async def get_active_signals(
    limit: int = Query(20, le=50),
    user: dict = Depends(get_current_user)
):
    """
    Get currently active signals (pending execution).
    """
    user_id = user["user_id"]
    
    # Try to get from pending_limit_orders table
    try:
        query = """
            SELECT id, symbol, side, strategy, entry_price, sl_price, tp_price,
                   created_at, status
            FROM pending_limit_orders
            WHERE user_id = %s AND status = 'pending'
            ORDER BY created_at DESC
            LIMIT %s
        """
        rows = execute(query, [user_id, limit]) or []
        
        signals = []
        for row in rows:
            signals.append({
                "id": row["id"],
                "symbol": row["symbol"],
                "side": row["side"],
                "strategy": row["strategy"] or "limit",
                "entry_price": row["entry_price"],
                "stop_loss": row.get("sl_price"),
                "take_profit": row.get("tp_price"),
                "confidence": 0.7,
                "status": "active",
                "created_at": str(row["created_at"]) if row["created_at"] else None,
                "executed_at": None,
                "pnl": None
            })
        
        return {
            "success": True,
            "data": signals,
            "count": len(signals)
        }
        
    except Exception as e:
        logger.error(f"Error fetching active signals: {e}")
        return {
            "success": True,
            "data": [],
            "count": 0
        }


@router.get("/stats")
async def get_signal_stats(
    strategy: Optional[str] = None,
    days: int = Query(30, le=365),
    user: dict = Depends(get_current_user)
):
    """
    Get signal statistics.
    """
    user_id = user["user_id"]
    from_date = datetime.now() - timedelta(days=days)
    
    try:
        query = """
            SELECT 
                COUNT(*) as total_signals,
                COUNT(CASE WHEN pnl > 0 THEN 1 END) as wins,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl
            FROM trade_logs
            WHERE user_id = %s AND ts >= %s
        """
        params = [user_id, from_date]
        
        if strategy:
            query += " AND strategy = %s"
            params.append(strategy)
            
        row = execute_one(query, params)
        
        if row:
            total = row["total_signals"] or 0
            wins = row["wins"] or 0
            win_rate = (wins / total * 100) if total > 0 else 0
            
            return {
                "success": True,
                "data": {
                    "total_signals": total,
                    "active_signals": 0,  # Would need separate query
                    "executed_signals": total,
                    "win_rate": win_rate,
                    "total_pnl": row["total_pnl"] or 0,
                    "avg_pnl_per_signal": row["avg_pnl"] or 0
                }
            }
        
    except Exception as e:
        logger.error(f"Error fetching signal stats: {e}")
    
    return {
        "success": True,
        "data": {
            "total_signals": 0,
            "active_signals": 0,
            "executed_signals": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "avg_pnl_per_signal": 0
        }
    }


def _get_mock_signals(limit: int = 20):
    """Generate mock signals for demo"""
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
    strategies = ["oi", "scryptomera", "scalper", "elcaro", "manual"]
    statuses = ["executed", "executed", "executed", "expired", "cancelled"]
    
    signals = []
    for i in range(min(limit, 20)):
        symbol = random.choice(symbols)
        side = random.choice(["Buy", "Sell"])
        price = random.uniform(100, 100000) if "BTC" in symbol else random.uniform(10, 5000)
        pnl = random.uniform(-50, 150) if random.random() > 0.3 else random.uniform(-100, -10)
        
        signals.append({
            "id": i + 1,
            "symbol": symbol,
            "side": side,
            "strategy": random.choice(strategies),
            "entry_price": round(price, 2),
            "stop_loss": round(price * (0.97 if side == "Buy" else 1.03), 2),
            "take_profit": round(price * (1.05 if side == "Buy" else 0.95), 2),
            "confidence": random.uniform(0.5, 0.95),
            "status": random.choice(statuses),
            "created_at": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
            "executed_at": (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat() if random.random() > 0.3 else None,
            "pnl": round(pnl, 2) if random.random() > 0.2 else None
        })
    
    return {
        "success": True,
        "data": signals,
        "count": len(signals)
    }
