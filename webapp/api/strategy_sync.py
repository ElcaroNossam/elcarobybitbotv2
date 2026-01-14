"""
Strategy Sync API - Bidirectional sync between WebApp and Bot
Live visualization, real-time backtest updates, and strategy rankings
"""
import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import db

# Import services with error handling
try:
    from services.strategy_service import StrategySyncService
    STRATEGY_SERVICE_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Strategy service not available: {e}")
    STRATEGY_SERVICE_AVAILABLE = False
    StrategySyncService = None

router = APIRouter()

# Import auth
from webapp.api.auth import get_current_user


# ============ REQUEST/RESPONSE MODELS ============

class StrategySyncRequest(BaseModel):
    """Request to sync strategies between webapp and bot."""
    direction: str = "webapp_to_bot"  # or "bot_to_webapp"
    strategy_ids: Optional[List[int]] = None


class StrategyActivationRequest(BaseModel):
    """Request to activate/deactivate a strategy for trading."""
    strategy_id: int
    active: bool
    exchange: str = "bybit"  # or "hyperliquid"


class BacktestVisualizationRequest(BaseModel):
    """Request for live backtest visualization data."""
    strategy_id: int
    symbol: str = "BTCUSDT"
    timeframe: str = "1h"
    days: int = 30


class RankingRequest(BaseModel):
    """Request for strategy rankings."""
    period: str = "30d"  # 7d, 30d, 90d, all
    limit: int = 20
    category: Optional[str] = None


# ============ SYNC ENDPOINTS ============

@router.post("/sync")
async def sync_strategies(
    request: StrategySyncRequest,
    user: dict = Depends(get_current_user)
):
    """Sync user strategies between webapp and bot."""
    user_id = user["user_id"]
    
    try:
        sync_service = StrategySyncService()
        
        if request.direction == "webapp_to_bot":
            result = await sync_service.sync_webapp_to_bot(
                user_id, 
                request.strategy_ids
            )
        else:
            result = await sync_service.sync_bot_to_webapp(user_id)
        
        return {
            "success": True,
            "direction": request.direction,
            "synced_count": result.get("synced_count", 0),
            "details": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_sync_status(user: dict = Depends(get_current_user)):
    """Get current sync status for user's strategies."""
    user_id = user["user_id"]
    
    # Get user config from bot
    config = db.get_user_config(user_id)
    
    # Get custom strategies
    strategies = db.get_user_strategies(user_id)
    
    # Parse strategy settings from bot
    strategy_settings = {}
    if config.get("strategy_settings"):
        try:
            strategy_settings = json.loads(config["strategy_settings"])
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse strategy_settings for user {user_id}: {e}")
            strategy_settings = {}
    
    # Build status for each strategy
    status = []
    for s in strategies:
        s_id = s["id"]
        bot_active = strategy_settings.get(str(s_id), {}).get("active", False)
        
        status.append({
            "id": s_id,
            "name": s["name"],
            "webapp_active": bool(s.get("is_active")),
            "bot_active": bot_active,
            "synced": bool(s.get("is_active")) == bot_active,
            "last_synced": s.get("updated_at")
        })
    
    # Also check built-in strategies
    builtin = [
        {"name": "el_caro", "field": "trade_elcaro"},
        {"name": "wyckoff", "field": "trade_wyckoff"},
        {"name": "scalper", "field": "trade_scalper"},
        {"name": "scryptomera", "field": "trade_scryptomera"}
    ]
    
    for b in builtin:
        status.append({
            "id": b["name"],
            "name": b["name"].replace("_", " ").title(),
            "type": "builtin",
            "bot_active": bool(config.get(b["field"])),
            "synced": True  # Built-in always synced via db
        })
    
    return {
        "user_id": user_id,
        "strategies": status,
        "last_config_update": config.get("updated_at")
    }


@router.post("/activate")
async def activate_strategy(
    request: StrategyActivationRequest,
    user: dict = Depends(get_current_user)
):
    """Activate or deactivate a strategy for live trading."""
    user_id = user["user_id"]
    
    try:
        sync_service = StrategySyncService()
        
        # Get current strategy settings
        config = db.get_user_config(user_id)
        strategy_settings = {}
        if config.get("strategy_settings"):
            try:
                strategy_settings = json.loads(config["strategy_settings"])
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Update strategy activation
        str_id = str(request.strategy_id)
        if str_id not in strategy_settings:
            strategy_settings[str_id] = {}
        
        strategy_settings[str_id]["active"] = request.active
        strategy_settings[str_id]["exchange"] = request.exchange
        strategy_settings[str_id]["updated_at"] = datetime.utcnow().isoformat()
        
        # Save to bot config
        db.set_user_field(user_id, "strategy_settings", json.dumps(strategy_settings))
        
        # Also update custom strategy in webapp
        db.execute_query(
            "UPDATE custom_strategies SET is_active = ? WHERE id = ? AND user_id = ?",
            (1 if request.active else 0, request.strategy_id, user_id)
        )
        
        return {
            "success": True,
            "strategy_id": request.strategy_id,
            "active": request.active,
            "exchange": request.exchange
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active")
async def get_active_strategies(user: dict = Depends(get_current_user)):
    """Get all currently active strategies for trading."""
    user_id = user["user_id"]
    
    sync_service = StrategySyncService()
    active = sync_service.get_user_active_strategies(user_id)
    
    return {
        "user_id": user_id,
        "active_strategies": active,
        "total": len(active)
    }


# ============ LIVE VISUALIZATION ENDPOINTS ============

@router.post("/visualization/generate")
async def generate_visualization(
    request: BacktestVisualizationRequest,
    user: dict = Depends(get_current_user)
):
    """Generate visualization data for terminal display."""
    user_id = user["user_id"]
    
    try:
        viz_service = LiveBacktestVisualization()
        
        # Get strategy config
        strategy = db.get_strategy_by_id(request.strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        if strategy["user_id"] != user_id:
            # Check if user purchased this strategy
            purchases = db.get_user_purchases(user_id)
            if not any(p["strategy_id"] == request.strategy_id for p in purchases):
                raise HTTPException(status_code=403, detail="No access to this strategy")
        
        # Generate visualization
        data = viz_service.generate_visualization_data(
            strategy_config=json.loads(strategy.get("config", "{}")),
            symbol=request.symbol,
            timeframe=request.timeframe,
            days=request.days
        )
        
        return data
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visualization/chart-data/{strategy_id}")
async def get_chart_data(
    strategy_id: int,
    symbol: str = Query("BTCUSDT"),
    timeframe: str = Query("1h"),
    days: int = Query(30),
    user: dict = Depends(get_current_user)
):
    """Get chart data with strategy signals for visualization."""
    user_id = user["user_id"]
    
    try:
        viz_service = LiveBacktestVisualization()
        
        # Get strategy
        strategy = db.get_strategy_by_id(strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        config = json.loads(strategy.get("config", "{}"))
        
        # Generate chart data
        chart_data = viz_service.generate_chart_data(
            strategy_config=config,
            symbol=symbol,
            timeframe=timeframe,
            days=days
        )
        
        return chart_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ RANKING ENDPOINTS ============

@router.get("/rankings/live")
async def get_live_rankings(
    period: str = Query("30d"),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None)
):
    """Get live strategy rankings based on real performance."""
    try:
        ranking_service = StrategyRankingService()
        
        rankings = ranking_service.get_top_performers(
            period=period,
            limit=limit,
            category=category
        )
        
        return {
            "period": period,
            "total": len(rankings),
            "rankings": rankings
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rankings/user/{target_user_id}")
async def get_user_ranking(
    target_user_id: int,
    user: dict = Depends(get_current_user)
):
    """Get ranking position for a specific user's strategies."""
    try:
        ranking_service = StrategyRankingService()
        
        # Get all user strategies
        strategies = db.get_user_strategies(target_user_id)
        
        rankings = []
        for s in strategies:
            if s.get("is_public"):
                rank = ranking_service.get_strategy_rank(s["id"])
                rankings.append({
                    "strategy_id": s["id"],
                    "name": s["name"],
                    **rank
                })
        
        return {
            "user_id": target_user_id,
            "strategies": rankings
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rankings/update")
async def update_rankings(user: dict = Depends(get_current_user)):
    """Force update all strategy rankings (admin only)."""
    user_id = user["user_id"]
    
    # Check admin
    from coin_params import ADMIN_ID
    if user_id != ADMIN_ID:
        raise HTTPException(status_code=403, detail="Admin only")
    
    try:
        ranking_service = StrategyRankingService()
        result = ranking_service.update_all_rankings()
        
        return {
            "success": True,
            "updated_count": result.get("updated", 0),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ WEBSOCKET FOR LIVE UPDATES ============

class ConnectionManager:
    """Manage WebSocket connections for live backtest updates."""
    
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
    
    async def send_personal(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except (RuntimeError, ConnectionResetError):
                    pass
    
    async def broadcast(self, message: dict):
        for user_id in self.active_connections:
            await self.send_personal(message, user_id)


manager = ConnectionManager()


@router.websocket("/ws/backtest/{user_id}")
async def websocket_backtest(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for live backtest updates."""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            action = data.get("action")
            
            if action == "start_backtest":
                # Start live backtest
                strategy_id = data.get("strategy_id")
                symbol = data.get("symbol", "BTCUSDT")
                timeframe = data.get("timeframe", "1h")
                
                # Send initial message
                await manager.send_personal({
                    "type": "backtest_started",
                    "strategy_id": strategy_id,
                    "symbol": symbol,
                    "timeframe": timeframe
                }, user_id)
                
                # Run backtest in background
                asyncio.create_task(
                    run_live_backtest(user_id, strategy_id, symbol, timeframe)
                )
            
            elif action == "stop_backtest":
                await manager.send_personal({
                    "type": "backtest_stopped"
                }, user_id)
            
            elif action == "ping":
                await manager.send_personal({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }, user_id)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


async def run_live_backtest(user_id: int, strategy_id: int, symbol: str, timeframe: str):
    """Run backtest and stream updates via WebSocket."""
    try:
        strategy = db.get_strategy_by_id(strategy_id)
        if not strategy:
            await manager.send_personal({
                "type": "error",
                "message": "Strategy not found"
            }, user_id)
            return
        
        config = json.loads(strategy.get("config", "{}"))
        viz_service = LiveBacktestVisualization()
        
        # Generate visualization data step by step
        # Simulate streaming updates
        for progress in range(0, 101, 10):
            await asyncio.sleep(0.5)
            
            await manager.send_personal({
                "type": "progress",
                "progress": progress,
                "message": f"Processing {progress}%..."
            }, user_id)
        
        # Final result
        data = viz_service.generate_visualization_data(
            strategy_config=config,
            symbol=symbol,
            timeframe=timeframe,
            days=30
        )
        
        await manager.send_personal({
            "type": "backtest_complete",
            "data": data
        }, user_id)
    
    except Exception as e:
        await manager.send_personal({
            "type": "error",
            "message": str(e)
        }, user_id)


# ============ STRATEGY PRESETS ============

@router.get("/presets")
async def get_strategy_presets():
    """Get available strategy presets for quick setup."""
    presets = [
        {
            "id": "trend_following",
            "name": "Trend Following",
            "description": "EMA crossover with ADX confirmation",
            "config": {
                "entry_conditions": [
                    {"indicator": "ema_cross", "params": {"fast": 9, "slow": 21}, "condition": "bullish"},
                    {"indicator": "adx", "params": {"period": 14}, "condition": "above", "value": 25}
                ],
                "exit_conditions": [
                    {"indicator": "ema_cross", "params": {"fast": 9, "slow": 21}, "condition": "bearish"}
                ],
                "tp_pct": 3.0,
                "sl_pct": 1.5,
                "risk_per_trade": 2.0
            }
        },
        {
            "id": "mean_reversion",
            "name": "Mean Reversion",
            "description": "RSI oversold with Bollinger Band bounce",
            "config": {
                "entry_conditions": [
                    {"indicator": "rsi", "params": {"period": 14}, "condition": "below", "value": 30},
                    {"indicator": "bb", "params": {"period": 20, "std": 2}, "condition": "below_lower"}
                ],
                "exit_conditions": [
                    {"indicator": "rsi", "params": {"period": 14}, "condition": "above", "value": 70}
                ],
                "tp_pct": 2.0,
                "sl_pct": 1.0,
                "risk_per_trade": 1.5
            }
        },
        {
            "id": "momentum",
            "name": "Momentum Breakout",
            "description": "Volume spike with MACD confirmation",
            "config": {
                "entry_conditions": [
                    {"indicator": "volume_spike", "params": {"multiplier": 2.0}, "condition": "true"},
                    {"indicator": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}, "condition": "bullish_cross"}
                ],
                "exit_conditions": [
                    {"indicator": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}, "condition": "bearish_cross"}
                ],
                "tp_pct": 4.0,
                "sl_pct": 2.0,
                "risk_per_trade": 2.5
            }
        },
        {
            "id": "scalping",
            "name": "Quick Scalp",
            "description": "SuperTrend with VWAP for quick trades",
            "config": {
                "entry_conditions": [
                    {"indicator": "supertrend", "params": {"period": 10, "multiplier": 3}, "condition": "bullish"},
                    {"indicator": "vwap", "params": {}, "condition": "price_above"}
                ],
                "exit_conditions": [
                    {"indicator": "supertrend", "params": {"period": 10, "multiplier": 3}, "condition": "bearish"}
                ],
                "tp_pct": 1.0,
                "sl_pct": 0.5,
                "risk_per_trade": 1.0
            }
        },
        {
            "id": "smc_wyckoff",
            "name": "Smart Money Wyckoff",
            "description": "Order blocks with FVG and Wyckoff accumulation",
            "config": {
                "entry_conditions": [
                    {"indicator": "order_block", "params": {}, "condition": "bullish"},
                    {"indicator": "fvg", "params": {}, "condition": "bullish_gap"},
                    {"indicator": "wyckoff", "params": {}, "condition": "accumulation"}
                ],
                "exit_conditions": [
                    {"indicator": "bos", "params": {}, "condition": "bearish"}
                ],
                "tp_pct": 5.0,
                "sl_pct": 2.0,
                "risk_per_trade": 3.0
            }
        }
    ]
    
    return {"presets": presets}


@router.post("/presets/apply/{preset_id}")
async def apply_preset(
    preset_id: str,
    user: dict = Depends(get_current_user)
):
    """Apply a strategy preset to create a new custom strategy."""
    user_id = user["user_id"]
    
    # Get preset
    presets = (await get_strategy_presets())["presets"]
    preset = next((p for p in presets if p["id"] == preset_id), None)
    
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    
    try:
        # Create new custom strategy from preset
        strategy_id = db.create_custom_strategy(
            user_id=user_id,
            name=f"My {preset['name']}",
            description=f"Based on {preset['name']} preset: {preset['description']}",
            config=preset["config"]
        )
        
        return {
            "success": True,
            "strategy_id": strategy_id,
            "name": f"My {preset['name']}",
            "config": preset["config"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
