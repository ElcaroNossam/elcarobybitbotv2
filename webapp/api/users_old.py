"""
Users API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from webapp.api.auth import verify_token

router = APIRouter()


class UserConfig(BaseModel):
    trade_percent: float = 5.0
    leverage: int = 10
    coin_group: List[str] = []
    trade_scryptomera: bool = True
    trade_scalper: bool = True
    trade_elcaro: bool = True
    trade_wyckoff: bool = True
    use_oi_filter: bool = False
    use_rsi_bb_filter: bool = False
    limit_only: bool = False
    exchange_mode: str = "bybit"  # bybit, hyperliquid, both


class UserConfigUpdate(BaseModel):
    trade_percent: Optional[float] = None
    leverage: Optional[int] = None
    coin_group: Optional[List[str]] = None
    trade_scryptomera: Optional[bool] = None
    trade_scalper: Optional[bool] = None
    trade_elcaro: Optional[bool] = None
    trade_wyckoff: Optional[bool] = None
    use_oi_filter: Optional[bool] = None
    use_rsi_bb_filter: Optional[bool] = None
    limit_only: Optional[bool] = None
    exchange_mode: Optional[str] = None


class UserStats(BaseModel):
    total_trades: int = 0
    winning_trades: int = 0
    total_pnl: float = 0.0
    win_rate: float = 0.0
    avg_trade_pnl: float = 0.0


@router.get("/config", response_model=UserConfig)
async def get_user_config(payload: dict = Depends(verify_token)):
    """Get current user configuration"""
    user_id = int(payload.get("sub", 0))
    
    # TODO: Get config from database
    return UserConfig()


@router.patch("/config", response_model=UserConfig)
async def update_user_config(
    updates: UserConfigUpdate,
    payload: dict = Depends(verify_token)
):
    """Update user configuration"""
    user_id = int(payload.get("sub", 0))
    
    # Validate exchange_mode
    if updates.exchange_mode:
        if updates.exchange_mode not in ["bybit", "hyperliquid", "both"]:
            raise HTTPException(400, "Invalid exchange mode")
        
        # Check premium for hyperliquid
        if updates.exchange_mode in ["hyperliquid", "both"]:
            # TODO: Check premium license
            pass
    
    # TODO: Update config in database
    return UserConfig()


@router.get("/stats", response_model=UserStats)
async def get_user_stats(payload: dict = Depends(verify_token)):
    """Get user trading statistics"""
    user_id = int(payload.get("sub", 0))
    
    # TODO: Calculate stats from trade logs
    return UserStats()


@router.get("/balance")
async def get_user_balance(
    exchange: str = "bybit",
    account: str = "demo",
    payload: dict = Depends(verify_token)
):
    """Get user balance from exchange"""
    user_id = int(payload.get("sub", 0))
    
    # TODO: Get balance from exchange
    return {
        "exchange": exchange,
        "account": account,
        "equity": 10000.0,
        "available": 8500.0,
        "margin_used": 1500.0,
        "unrealized_pnl": 0.0
    }
