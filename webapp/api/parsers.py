"""
Dynamic Signal Parsers API

Endpoints for managing user subscriptions to admin-created signal parsers.
These parsers work like built-in strategies (OI, Scryptomera, etc.) but are
dynamically created by admins.

SECURITY: All endpoints require JWT authentication.
"""
import os
import sys
import json
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/parsers", tags=["Signal Parsers"])

# Import auth
from webapp.api.auth import get_current_user


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class SubscribeRequest(BaseModel):
    """Subscribe to a dynamic signal parser."""
    parser_id: int
    long_enabled: bool = True
    short_enabled: bool = True
    entry_percent: float = 1.0
    leverage: int = 10
    dca_enabled: bool = False


class UpdateSubscriptionRequest(BaseModel):
    """Update subscription settings."""
    long_enabled: Optional[bool] = None
    short_enabled: Optional[bool] = None
    entry_percent: Optional[float] = None
    leverage: Optional[int] = None
    dca_enabled: Optional[bool] = None


# ═══════════════════════════════════════════════════════════════════════════════
# LIST AVAILABLE PARSERS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/available")
async def list_available_parsers(user: dict = Depends(get_current_user)):
    """
    List all available admin-created signal parsers that users can subscribe to.
    
    These are parsers marked as is_system=TRUE or is_public=TRUE.
    """
    user_id = user["user_id"]
    
    try:
        from core.db_postgres import execute
        
        # Get all public/system parsers
        parsers = execute("""
            SELECT 
                id, name, description, strategy_type, signal_channel,
                is_system, is_active, total_signals, total_trades,
                created_at, updated_at
            FROM dynamic_signal_parsers
            WHERE (is_system = TRUE OR is_public = TRUE) AND is_active = TRUE
            ORDER BY total_signals DESC, name
        """)
        
        # Get user's subscriptions
        user_subscriptions = db.get_user_parser_subscriptions(user_id, active_only=True)
        subscribed_parser_ids = {s["parser_id"] for s in user_subscriptions}
        
        result = []
        for p in parsers:
            parser_data = dict(p)
            parser_data["is_subscribed"] = parser_data["id"] in subscribed_parser_ids
            
            # Get subscription details if subscribed
            if parser_data["is_subscribed"]:
                sub = next((s for s in user_subscriptions if s["parser_id"] == parser_data["id"]), None)
                if sub:
                    parser_data["subscription"] = {
                        "long_enabled": sub.get("long_enabled", True),
                        "short_enabled": sub.get("short_enabled", True),
                        "entry_percent": sub.get("entry_percent", 1.0),
                        "leverage": sub.get("leverage", 10),
                        "dca_enabled": sub.get("dca_enabled", False),
                        "total_trades": sub.get("total_trades", 0),
                        "total_pnl": sub.get("total_pnl", 0),
                    }
            
            result.append(parser_data)
        
        return {
            "success": True,
            "parsers": result,
            "total": len(result)
        }
        
    except Exception as e:
        logger.exception(f"Failed to list parsers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscriptions")
async def get_my_subscriptions(user: dict = Depends(get_current_user)):
    """Get all parser subscriptions for the authenticated user."""
    user_id = user["user_id"]
    
    try:
        subscriptions = db.get_user_parser_subscriptions(user_id, active_only=False)
        
        return {
            "success": True,
            "subscriptions": subscriptions,
            "active_count": sum(1 for s in subscriptions if s.get("is_active", False))
        }
        
    except Exception as e:
        logger.exception(f"Failed to get subscriptions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# SUBSCRIBE TO PARSER
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/subscribe")
async def subscribe_to_parser(
    request: SubscribeRequest,
    user: dict = Depends(get_current_user)
):
    """
    Subscribe to a dynamic signal parser.
    
    This enables the parser for your account with your specified trading settings.
    When signals from this parser arrive, they will be processed using your settings.
    """
    user_id = user["user_id"]
    
    try:
        # Verify parser exists and is available
        from core.db_postgres import execute_one
        
        parser = execute_one("""
            SELECT id, name, is_system, is_public, is_active
            FROM dynamic_signal_parsers
            WHERE id = %s
        """, (request.parser_id,))
        
        if not parser:
            raise HTTPException(status_code=404, detail="Parser not found")
        
        parser = dict(parser)
        
        if not parser["is_active"]:
            raise HTTPException(status_code=400, detail="Parser is not active")
        
        if not (parser["is_system"] or parser["is_public"]):
            raise HTTPException(status_code=403, detail="Parser is not available for subscription")
        
        # Check if already subscribed
        existing = db.get_user_parser_subscription(user_id, parser_id=request.parser_id)
        if existing and existing.get("is_active"):
            raise HTTPException(status_code=400, detail="Already subscribed to this parser")
        
        # Create or reactivate subscription
        db.subscribe_to_parser(
            user_id=user_id,
            parser_id=request.parser_id,
            long_enabled=request.long_enabled,
            short_enabled=request.short_enabled,
            entry_percent=request.entry_percent,
            leverage=request.leverage,
            dca_enabled=request.dca_enabled
        )
        
        return {
            "success": True,
            "message": f"Subscribed to parser '{parser['name']}' successfully!",
            "parser_id": request.parser_id,
            "parser_name": parser["name"],
            "settings": {
                "long_enabled": request.long_enabled,
                "short_enabled": request.short_enabled,
                "entry_percent": request.entry_percent,
                "leverage": request.leverage,
                "dca_enabled": request.dca_enabled
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to subscribe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# UNSUBSCRIBE FROM PARSER
# ═══════════════════════════════════════════════════════════════════════════════

@router.delete("/subscribe/{parser_id}")
async def unsubscribe_from_parser(
    parser_id: int,
    user: dict = Depends(get_current_user)
):
    """Unsubscribe from a dynamic signal parser."""
    user_id = user["user_id"]
    
    try:
        # Check if subscribed
        existing = db.get_user_parser_subscription(user_id, parser_id=parser_id)
        if not existing or not existing.get("is_active"):
            raise HTTPException(status_code=404, detail="Not subscribed to this parser")
        
        db.unsubscribe_from_parser(user_id, parser_id)
        
        return {
            "success": True,
            "message": "Unsubscribed successfully",
            "parser_id": parser_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to unsubscribe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# UPDATE SUBSCRIPTION SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

@router.patch("/subscribe/{parser_id}")
async def update_subscription(
    parser_id: int,
    request: UpdateSubscriptionRequest,
    user: dict = Depends(get_current_user)
):
    """Update settings for a parser subscription."""
    user_id = user["user_id"]
    
    try:
        # Check if subscribed
        existing = db.get_user_parser_subscription(user_id, parser_id=parser_id)
        if not existing or not existing.get("is_active"):
            raise HTTPException(status_code=404, detail="Not subscribed to this parser")
        
        # Build update dict from non-None values
        updates = {}
        if request.long_enabled is not None:
            updates["long_enabled"] = request.long_enabled
        if request.short_enabled is not None:
            updates["short_enabled"] = request.short_enabled
        if request.entry_percent is not None:
            updates["entry_percent"] = request.entry_percent
        if request.leverage is not None:
            updates["leverage"] = request.leverage
        if request.dca_enabled is not None:
            updates["dca_enabled"] = request.dca_enabled
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        db.update_parser_subscription(user_id, parser_id, **updates)
        
        return {
            "success": True,
            "message": "Subscription updated",
            "parser_id": parser_id,
            "updated_fields": list(updates.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to update subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# PARSER STATS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/stats/{parser_id}")
async def get_parser_stats(
    parser_id: int,
    user: dict = Depends(get_current_user)
):
    """Get statistics for a specific parser (user's personal stats)."""
    user_id = user["user_id"]
    
    try:
        from core.db_postgres import execute_one
        
        # Get parser info
        parser = execute_one("""
            SELECT id, name, description, strategy_type, total_signals, total_trades
            FROM dynamic_signal_parsers
            WHERE id = %s AND ((is_system = TRUE OR is_public = TRUE) AND is_active = TRUE)
        """, (parser_id,))
        
        if not parser:
            raise HTTPException(status_code=404, detail="Parser not found")
        
        parser = dict(parser)
        
        # Get user's subscription stats
        subscription = db.get_user_parser_subscription(user_id, parser_id=parser_id)
        
        user_stats = {
            "is_subscribed": False,
            "total_trades": 0,
            "total_pnl": 0,
            "winning_trades": 0,
            "losing_trades": 0,
        }
        
        if subscription:
            user_stats = {
                "is_subscribed": subscription.get("is_active", False),
                "total_trades": subscription.get("total_trades", 0),
                "total_pnl": subscription.get("total_pnl", 0),
                "winning_trades": subscription.get("winning_trades", 0),
                "losing_trades": subscription.get("losing_trades", 0),
            }
        
        return {
            "success": True,
            "parser": parser,
            "user_stats": user_stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get parser stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
