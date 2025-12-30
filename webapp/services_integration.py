"""
Unified WebApp API Services Integration

Drop-in replacements for webapp/api/ routers to use services layer
instead of direct db imports.
"""
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


async def get_positions_service(user_id: int, exchange: str = 'bybit', account_type: str = 'demo', symbol: Optional[str] = None) -> Dict[str, Any]:
    """
    Get positions using services layer
    
    Replace:
        positions = db.get_active_positions(user_id)
    
    With:
        from webapp.services_integration import get_positions_service
        positions = await get_positions_service(user_id, exchange='bybit', account_type='demo')
    
    Returns:
        Dict with {"success": bool, "data": List[dict]}
    """
    try:
        import db
        from bot_unified import get_positions_unified
        
        # Get positions from exchange API
        positions = await get_positions_unified(user_id, symbol=symbol, exchange=exchange, account_type=account_type)
        
        # Get DB positions for enrichment (strategy, etc.)
        db_positions = {}
        try:
            active_pos = db.get_active_positions(
                user_id,
                account_type=account_type,
                exchange=exchange
            )
            for ap in active_pos:
                db_positions[ap.get("symbol", "")] = ap
        except Exception as db_err:
            logger.warning(f"Could not get DB positions for enrichment: {db_err}")
        
        # Convert to dict and enrich with DB data
        result_data = []
        for pos in positions:
            pos_dict = pos.to_dict()
            sym = pos_dict.get("symbol", "")
            db_pos = db_positions.get(sym, {})
            
            # Enrich with DB data
            pos_dict["strategy"] = db_pos.get("strategy")
            pos_dict["account_type"] = account_type
            pos_dict["env"] = db_pos.get("env") or ("paper" if account_type in ("demo", "testnet") else "live")
            pos_dict["tp_price"] = db_pos.get("tp_price") or pos_dict.get("take_profit")
            pos_dict["sl_price"] = db_pos.get("sl_price") or pos_dict.get("stop_loss")
            pos_dict["use_atr"] = bool(db_pos.get("atr_activated", 0))
            pos_dict["atr_activated"] = bool(db_pos.get("atr_activated", 0))
            
            result_data.append(pos_dict)
        
        return {
            "success": True,
            "data": result_data
        }
    except Exception as e:
        logger.error(f"get_positions_service error: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": []
        }


async def get_balance_service(user_id: int, exchange: str = 'bybit', account_type: str = 'demo') -> Dict[str, Any]:
    """
    Get balance using services layer
    
    Replace:
        balance = await bybit_request(user_id, 'GET', '/v5/account/wallet-balance', ...)
    
    With:
        from webapp.services_integration import get_balance_service
        balance = await get_balance_service(user_id, exchange='bybit', account_type='demo')
    
    Returns:
        Dict with {"success": bool, "data": dict}
    """
    try:
        from bot_unified import get_balance_unified
        
        balance = await get_balance_unified(user_id, exchange=exchange, account_type=account_type)
        if not balance:
            return {
                "success": False,
                "error": "Failed to fetch balance",
                "data": {
                    "equity": 0,
                    "available": 0,
                    "unrealized_pnl": 0,
                    "account_type": account_type
                }
            }
        
        # Map to API-expected field names
        balance_dict = balance.to_dict()
        return {
            "success": True,
            "data": {
                "equity": balance_dict.get("total_equity", 0),
                "available": balance_dict.get("available_balance", 0),
                "unrealized_pnl": balance_dict.get("unrealized_pnl", 0),
                "margin_balance": balance_dict.get("margin_used", 0),
                "wallet_balance": balance_dict.get("wallet_balance"),
                "account_type": account_type,
                "currency": balance_dict.get("currency", "USDT"),
                # Also include original fields for backward compatibility
                "total_equity": balance_dict.get("total_equity", 0),
                "available_balance": balance_dict.get("available_balance", 0),
            }
        }
    except Exception as e:
        logger.error(f"get_balance_service error: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": {
                "equity": 0,
                "available": 0,
                "unrealized_pnl": 0,
                "account_type": account_type
            }
        }


async def place_order_service(
    user_id: int,
    symbol: str,
    side: str,
    order_type: str,
    size: float,
    price: Optional[float] = None,
    leverage: int = 10,
    take_profit: Optional[float] = None,
    stop_loss: Optional[float] = None,
    exchange: str = 'bybit',
    account_type: str = 'demo'
) -> Dict[str, Any]:
    """
    Place order using services layer
    
    Replace:
        result = await bybit_request(user_id, 'POST', '/v5/order/create', ...)
    
    With:
        from webapp.services_integration import place_order_service
        result = await place_order_service(user_id, symbol, side, ...)
    """
    try:
        from bot_unified import place_order_unified
        
        result = await place_order_unified(
            user_id=user_id,
            symbol=symbol,
            side=side.capitalize(),  # 'buy' -> 'Buy'
            order_type=order_type.capitalize(),  # 'market' -> 'Market'
            qty=size,
            price=price,
            leverage=leverage,
            take_profit=take_profit,
            stop_loss=stop_loss,
            exchange=exchange,
            account_type=account_type
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Order failed'))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"place_order_service error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def close_position_service(
    user_id: int,
    symbol: str,
    qty: Optional[float] = None,
    exchange: str = 'bybit',
    account_type: str = 'demo'
) -> Dict[str, Any]:
    """
    Close position using services layer
    
    Replace:
        result = await bybit_request(user_id, 'POST', '/v5/order/create', ..., reduceOnly=True)
    
    With:
        from webapp.services_integration import close_position_service
        result = await close_position_service(user_id, symbol, exchange='bybit', account_type='demo')
    """
    try:
        from bot_unified import close_position_unified
        
        result = await close_position_unified(
            user_id=user_id,
            symbol=symbol,
            qty=qty,
            exchange=exchange,
            account_type=account_type
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Close failed'))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"close_position_service error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def set_leverage_service(
    user_id: int,
    symbol: str,
    leverage: int,
    exchange: str = 'bybit',
    account_type: str = 'demo'
) -> bool:
    """
    Set leverage using services layer
    
    Replace:
        result = await bybit_request(user_id, 'POST', '/v5/position/set-leverage', ...)
    
    With:
        from webapp.services_integration import set_leverage_service
        await set_leverage_service(user_id, symbol, leverage, exchange='bybit', account_type='demo')
        from webapp.services_integration import set_leverage_service
        success = await set_leverage_service(user_id, symbol, leverage)
    """
    try:
        from bot_unified import set_leverage_unified
        
        return await set_leverage_unified(user_id, symbol, leverage, account_type)
    except Exception as e:
        logger.error(f"set_leverage_service error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# User management через services
def get_user_config_service(user_id: int) -> Dict[str, Any]:
    """
    Get user config using services
    
    Replace:
        config = db.get_user_config(user_id)
    
    With:
        from webapp.services_integration import get_user_config_service
        config = get_user_config_service(user_id)
    """
    try:
        import db
        return db.get_user_config(user_id)
    except Exception as e:
        logger.error(f"get_user_config_service error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def set_user_field_service(user_id: int, field: str, value: Any) -> None:
    """
    Set user field using services
    
    Replace:
        db.set_user_field(user_id, field, value)
    
    With:
        from webapp.services_integration import set_user_field_service
        set_user_field_service(user_id, field, value)
    """
    try:
        import db
        db.set_user_field(user_id, field, value)
    except Exception as e:
        logger.error(f"set_user_field_service error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Trade stats через services
def get_trade_stats_service(
    user_id: int,
    strategy: Optional[str] = None,
    period: int = 30
) -> Dict[str, Any]:
    """
    Get trade statistics using services
    
    Replace:
        stats = db.get_trade_stats(user_id, strategy, period)
    
    With:
        from webapp.services_integration import get_trade_stats_service
        stats = get_trade_stats_service(user_id, strategy, period)
    """
    try:
        import db
        return db.get_trade_stats(user_id, strategy, period)
    except Exception as e:
        logger.error(f"get_trade_stats_service error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


__all__ = [
    'get_positions_service',
    'get_balance_service',
    'place_order_service',
    'close_position_service',
    'set_leverage_service',
    'get_user_config_service',
    'set_user_field_service',
    'get_trade_stats_service',
]
