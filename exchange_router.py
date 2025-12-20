"""
Exchange Router - Universal trading functions that route to Bybit or HyperLiquid
"""
import logging
from db import get_exchange_type, get_hl_credentials
from hl_adapter import HLAdapter

logger = logging.getLogger(__name__)


async def place_order_universal(
    user_id: int,
    symbol: str,
    side: str,
    orderType: str,
    qty: float,
    price: float = None,
    leverage: int = None,
    reduce_only: bool = False,
    account_type: str = None,
    bybit_place_order_func=None,
):
    """
    Universal order placement - routes to Bybit or HyperLiquid based on user settings.
    Returns result in unified format.
    
    Args:
        bybit_place_order_func: The Bybit place_order function to use for Bybit orders
    """
    exchange = get_exchange_type(user_id)
    
    if exchange == "hyperliquid":
        hl_creds = get_hl_credentials(user_id)
        if not hl_creds.get("hl_private_key"):
            raise ValueError("HyperLiquid not configured. Use /hl to set up.")
        
        try:
            adapter = HLAdapter(
                private_key=hl_creds["hl_private_key"],
                testnet=hl_creds.get("hl_testnet", False),
                vault_address=hl_creds.get("hl_vault_address")
            )
            
            # Set leverage if specified
            if leverage:
                await adapter.set_leverage(symbol, leverage)
            
            # Place order
            result = await adapter.place_order(
                symbol=symbol,
                side=side,
                qty=qty,
                order_type=orderType,
                price=price,
                reduce_only=reduce_only
            )
            
            if result.get("success"):
                logger.info(f"HL Order placed: {result}")
                return result.get("data", {})
            else:
                raise ValueError(f"HyperLiquid order failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"HyperLiquid order error: {e}")
            raise
    
    else:
        # Default: Bybit
        if bybit_place_order_func is None:
            raise ValueError("bybit_place_order_func is required for Bybit orders")
        return await bybit_place_order_func(
            user_id=user_id,
            symbol=symbol,
            side=side,
            orderType=orderType,
            qty=qty,
            price=price,
            account_type=account_type
        )


async def fetch_positions_universal(
    user_id: int, 
    symbol: str = None,
    bybit_fetch_positions_func=None,
) -> list:
    """
    Universal position fetching - routes to Bybit or HyperLiquid.
    Returns list in unified format.
    """
    exchange = get_exchange_type(user_id)
    
    if exchange == "hyperliquid":
        hl_creds = get_hl_credentials(user_id)
        if not hl_creds.get("hl_private_key"):
            return []
        
        try:
            adapter = HLAdapter(
                private_key=hl_creds["hl_private_key"],
                testnet=hl_creds.get("hl_testnet", False),
                vault_address=hl_creds.get("hl_vault_address")
            )
            
            result = await adapter.fetch_positions()
            
            if result.get("success"):
                positions = result.get("data", [])
                if symbol:
                    positions = [p for p in positions if p.get("symbol") == symbol]
                return positions
            return []
            
        except Exception as e:
            logger.error(f"HL fetch positions error: {e}")
            return []
    
    else:
        # Default: Bybit
        if bybit_fetch_positions_func is None:
            raise ValueError("bybit_fetch_positions_func is required for Bybit")
        positions = await bybit_fetch_positions_func(user_id)
        if symbol:
            positions = [p for p in positions if p.get("symbol") == symbol]
        return positions


async def set_leverage_universal(
    user_id: int,
    symbol: str,
    leverage: int = 10,
    account_type: str = None,
    bybit_set_leverage_func=None,
) -> bool:
    """
    Universal leverage setting - routes to Bybit or HyperLiquid.
    Returns True if successful.
    """
    exchange = get_exchange_type(user_id)
    
    if exchange == "hyperliquid":
        hl_creds = get_hl_credentials(user_id)
        if not hl_creds.get("hl_private_key"):
            raise ValueError("HyperLiquid not configured")
        
        try:
            adapter = HLAdapter(
                private_key=hl_creds["hl_private_key"],
                testnet=hl_creds.get("hl_testnet", False),
                vault_address=hl_creds.get("hl_vault_address")
            )
            
            result = await adapter.set_leverage(symbol, leverage)
            return result.get("success", False)
            
        except Exception as e:
            logger.error(f"HL set leverage error: {e}")
            raise
    
    else:
        # Default: Bybit
        if bybit_set_leverage_func is None:
            raise ValueError("bybit_set_leverage_func is required for Bybit")
        return await bybit_set_leverage_func(user_id, symbol, leverage, account_type)


async def close_position_universal(
    user_id: int,
    symbol: str,
    size: float,
    side: str,  # Current position side
    account_type: str = None,
    bybit_place_order_func=None,
):
    """
    Universal position closing - routes to Bybit or HyperLiquid.
    """
    exchange = get_exchange_type(user_id)
    close_side = "Sell" if side == "Buy" else "Buy"
    
    if exchange == "hyperliquid":
        hl_creds = get_hl_credentials(user_id)
        if not hl_creds.get("hl_private_key"):
            raise ValueError("HyperLiquid not configured")
        
        try:
            adapter = HLAdapter(
                private_key=hl_creds["hl_private_key"],
                testnet=hl_creds.get("hl_testnet", False),
                vault_address=hl_creds.get("hl_vault_address")
            )
            
            result = await adapter.close_position(symbol, size, side)
            
            if result.get("success"):
                logger.info(f"HL Position closed: {result}")
                return result.get("data", {})
            else:
                raise ValueError(f"HyperLiquid close failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"HyperLiquid close error: {e}")
            raise
    
    else:
        # Default: Bybit - close via market order
        if bybit_place_order_func is None:
            raise ValueError("bybit_place_order_func is required for Bybit")
        return await bybit_place_order_func(
            user_id=user_id,
            symbol=symbol,
            side=close_side,
            orderType="Market",
            qty=size,
            account_type=account_type
        )


async def get_balance_universal(user_id: int, bybit_get_balance_func=None) -> dict:
    """
    Universal balance fetching - routes to Bybit or HyperLiquid.
    Returns dict with equity, available, margin_used, unrealized_pnl.
    """
    exchange = get_exchange_type(user_id)
    
    if exchange == "hyperliquid":
        hl_creds = get_hl_credentials(user_id)
        if not hl_creds.get("hl_private_key"):
            return {"equity": 0, "available": 0, "margin_used": 0, "unrealized_pnl": 0}
        
        try:
            adapter = HLAdapter(
                private_key=hl_creds["hl_private_key"],
                testnet=hl_creds.get("hl_testnet", False),
                vault_address=hl_creds.get("hl_vault_address")
            )
            
            result = await adapter.get_balance()
            
            if result.get("success"):
                return result.get("data", {})
            return {"equity": 0, "available": 0, "margin_used": 0, "unrealized_pnl": 0}
            
        except Exception as e:
            logger.error(f"HL get balance error: {e}")
            return {"equity": 0, "available": 0, "margin_used": 0, "unrealized_pnl": 0}
    
    else:
        # Default: Bybit
        if bybit_get_balance_func:
            return await bybit_get_balance_func(user_id)
        return {"equity": 0, "available": 0, "margin_used": 0, "unrealized_pnl": 0}
