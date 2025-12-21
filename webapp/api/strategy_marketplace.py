"""
Marketplace API - Strategy sharing, presets, import/export
"""
import os
import sys
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from services.strategy_marketplace import marketplace, StrategyCategory, StrategyVisibility

router = APIRouter()
logger = logging.getLogger(__name__)

from webapp.api.auth import get_current_user


# ============================================================================
# MODELS
# ============================================================================

class ShareStrategyRequest(BaseModel):
    name: str
    description: str = ""
    base_strategy: str
    params: dict
    symbols: List[str] = []
    timeframe: str = "15m"
    category: str = "custom"
    visibility: str = "public"
    backtest_results: dict = None
    tags: List[str] = []


class CopyStrategyRequest(BaseModel):
    strategy_id: int


class RateStrategyRequest(BaseModel):
    strategy_id: int
    rating: int
    comment: str = None


class SavePresetRequest(BaseModel):
    name: str
    description: str = ""


class LoadPresetRequest(BaseModel):
    preset_id: int


class ImportSettingsRequest(BaseModel):
    settings: dict


# ============================================================================
# MARKETPLACE ENDPOINTS
# ============================================================================

@router.get("/search")
async def search_strategies(
    query: str = Query(None),
    category: str = Query(None),
    base_strategy: str = Query(None),
    min_win_rate: float = Query(None),
    min_profit_factor: float = Query(None),
    sort_by: str = Query("rating"),
    limit: int = Query(50),
    offset: int = Query(0),
    user: dict = Depends(get_current_user)
):
    """
    Search strategies in the marketplace.
    
    Filters:
    - query: Text search in name, description, tags
    - category: scalping, swing, day_trading, trend_following, etc.
    - base_strategy: elcaro, wyckoff, scryptomera, etc.
    - min_win_rate: Minimum win rate percentage
    - min_profit_factor: Minimum profit factor
    
    Sort options: rating, copies, win_rate, profit_factor, pnl, recent
    """
    strategies = marketplace.search_strategies(
        query=query,
        category=category,
        base_strategy=base_strategy,
        min_win_rate=min_win_rate,
        min_profit_factor=min_profit_factor,
        sort_by=sort_by,
        limit=limit,
        offset=offset
    )
    
    return {
        "strategies": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "owner_name": s.owner_name,
                "base_strategy": s.base_strategy,
                "category": s.category.value,
                "win_rate": s.win_rate,
                "profit_factor": s.profit_factor,
                "total_pnl_percent": s.total_pnl_percent,
                "max_drawdown": s.max_drawdown,
                "total_trades": s.total_trades,
                "copies_count": s.copies_count,
                "rating": s.rating,
                "ratings_count": s.ratings_count,
                "timeframe": s.timeframe,
                "symbols": s.symbols[:5],  # First 5 symbols
                "tags": s.tags,
                "created_at": s.created_at.isoformat()
            }
            for s in strategies
        ],
        "count": len(strategies),
        "offset": offset
    }


@router.get("/strategy/{strategy_id}")
async def get_strategy_details(
    strategy_id: int,
    user: dict = Depends(get_current_user)
):
    """Get full details of a strategy"""
    strategy = marketplace.get_strategy(strategy_id)
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return {
        "id": strategy.id,
        "name": strategy.name,
        "description": strategy.description,
        "owner_id": strategy.owner_id,
        "owner_name": strategy.owner_name,
        "base_strategy": strategy.base_strategy,
        "category": strategy.category.value,
        "visibility": strategy.visibility.value,
        "params": strategy.params,
        "symbols": strategy.symbols,
        "timeframe": strategy.timeframe,
        "win_rate": strategy.win_rate,
        "profit_factor": strategy.profit_factor,
        "total_pnl_percent": strategy.total_pnl_percent,
        "max_drawdown": strategy.max_drawdown,
        "total_trades": strategy.total_trades,
        "copies_count": strategy.copies_count,
        "rating": strategy.rating,
        "ratings_count": strategy.ratings_count,
        "tags": strategy.tags,
        "backtest_results": strategy.backtest_results,
        "created_at": strategy.created_at.isoformat(),
        "updated_at": strategy.updated_at.isoformat(),
        "is_owner": strategy.owner_id == user["user_id"]
    }


@router.post("/share")
async def share_strategy(
    data: ShareStrategyRequest,
    user: dict = Depends(get_current_user)
):
    """
    Share a strategy to the marketplace.
    Other users can copy it and use your optimized settings.
    """
    user_id = user["user_id"]
    
    # Validate
    valid_strategies = ["elcaro", "wyckoff", "scryptomera", "scalper", "rsibboi", "custom"]
    if data.base_strategy not in valid_strategies:
        raise HTTPException(status_code=400, detail=f"Invalid base strategy. Valid: {valid_strategies}")
    
    valid_categories = [c.value for c in StrategyCategory]
    if data.category not in valid_categories:
        data.category = "custom"
    
    valid_visibility = [v.value for v in StrategyVisibility]
    if data.visibility not in valid_visibility:
        data.visibility = "public"
    
    # Get username
    import db
    creds = db.get_all_user_credentials(user_id)
    username = creds.get("username", f"User_{user_id}")
    
    strategy_id = marketplace.share_strategy(
        owner_id=user_id,
        owner_name=username,
        name=data.name,
        description=data.description,
        base_strategy=data.base_strategy,
        params=data.params,
        symbols=data.symbols,
        timeframe=data.timeframe,
        category=data.category,
        visibility=data.visibility,
        backtest_results=data.backtest_results,
        tags=data.tags
    )
    
    if strategy_id:
        return {"success": True, "strategy_id": strategy_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to share strategy")


@router.post("/copy")
async def copy_strategy(
    data: CopyStrategyRequest,
    user: dict = Depends(get_current_user)
):
    """
    Copy a strategy to your account.
    This will apply the strategy's parameters to your settings.
    """
    user_id = user["user_id"]
    
    result = marketplace.copy_strategy(data.strategy_id, user_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Copy failed"))
    
    return result


@router.post("/rate")
async def rate_strategy(
    data: RateStrategyRequest,
    user: dict = Depends(get_current_user)
):
    """Rate a strategy (1-5 stars)"""
    user_id = user["user_id"]
    
    if data.rating < 1 or data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")
    
    success = marketplace.rate_strategy(
        data.strategy_id,
        user_id,
        data.rating,
        data.comment
    )
    
    if success:
        return {"success": True}
    else:
        raise HTTPException(status_code=400, detail="Failed to rate strategy")


@router.get("/my-strategies")
async def get_my_strategies(user: dict = Depends(get_current_user)):
    """Get strategies shared by the current user"""
    user_id = user["user_id"]
    
    strategies = marketplace.search_strategies(
        visibility="public"  # Will filter by owner in query
    )
    
    # Filter by owner (TODO: add owner filter to search)
    my_strategies = [s for s in strategies if s.owner_id == user_id]
    
    return {
        "strategies": [
            {
                "id": s.id,
                "name": s.name,
                "base_strategy": s.base_strategy,
                "win_rate": s.win_rate,
                "copies_count": s.copies_count,
                "rating": s.rating,
                "visibility": s.visibility.value,
                "created_at": s.created_at.isoformat()
            }
            for s in my_strategies
        ]
    }


# ============================================================================
# PRESETS ENDPOINTS
# ============================================================================

@router.get("/presets")
async def get_presets(user: dict = Depends(get_current_user)):
    """Get all user's saved presets"""
    user_id = user["user_id"]
    presets = marketplace.get_user_presets(user_id)
    return {"presets": presets}


@router.post("/presets")
async def save_preset(
    data: SavePresetRequest,
    user: dict = Depends(get_current_user)
):
    """
    Save current settings as a named preset.
    You can have multiple presets and switch between them quickly.
    """
    user_id = user["user_id"]
    
    preset_id = marketplace.save_preset(user_id, data.name, data.description)
    
    if preset_id:
        return {"success": True, "preset_id": preset_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to save preset")


@router.post("/presets/load")
async def load_preset(
    data: LoadPresetRequest,
    user: dict = Depends(get_current_user)
):
    """Load a saved preset and apply it to your settings"""
    user_id = user["user_id"]
    
    result = marketplace.load_preset(user_id, data.preset_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Load failed"))
    
    return result


@router.delete("/presets/{preset_id}")
async def delete_preset(
    preset_id: int,
    user: dict = Depends(get_current_user)
):
    """Delete a preset"""
    user_id = user["user_id"]
    
    success = marketplace.delete_preset(user_id, preset_id)
    
    if success:
        return {"success": True}
    else:
        raise HTTPException(status_code=404, detail="Preset not found")


# ============================================================================
# IMPORT/EXPORT ENDPOINTS
# ============================================================================

@router.get("/export")
async def export_settings(user: dict = Depends(get_current_user)):
    """
    Export all settings as JSON.
    Can be shared with others or used to backup/restore your settings.
    """
    user_id = user["user_id"]
    export_data = marketplace.export_settings(user_id)
    return export_data


@router.post("/import")
async def import_settings(
    data: ImportSettingsRequest,
    user: dict = Depends(get_current_user)
):
    """
    Import settings from exported JSON.
    Use this to apply settings shared by another user or restore from backup.
    """
    user_id = user["user_id"]
    
    result = marketplace.import_settings(user_id, data.settings)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Import failed"))
    
    return result


# ============================================================================
# TOP STRATEGIES
# ============================================================================

@router.get("/top")
async def get_top_strategies(
    category: str = Query(None),
    limit: int = Query(10),
    user: dict = Depends(get_current_user)
):
    """Get top rated strategies"""
    strategies = marketplace.search_strategies(
        category=category,
        sort_by="rating",
        limit=limit
    )
    
    return {
        "strategies": [
            {
                "id": s.id,
                "name": s.name,
                "owner_name": s.owner_name,
                "base_strategy": s.base_strategy,
                "win_rate": s.win_rate,
                "profit_factor": s.profit_factor,
                "rating": s.rating,
                "copies_count": s.copies_count
            }
            for s in strategies
        ]
    }


@router.get("/trending")
async def get_trending_strategies(
    limit: int = Query(10),
    user: dict = Depends(get_current_user)
):
    """Get most copied strategies (trending)"""
    strategies = marketplace.search_strategies(
        sort_by="copies",
        limit=limit
    )
    
    return {
        "strategies": [
            {
                "id": s.id,
                "name": s.name,
                "owner_name": s.owner_name,
                "base_strategy": s.base_strategy,
                "win_rate": s.win_rate,
                "copies_count": s.copies_count
            }
            for s in strategies
        ]
    }
