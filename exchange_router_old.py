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
            
            async with adapter:
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
                
                # HLAdapter returns Bybit-like format with retCode
                if result.get("retCode") == 0:
                    logger.info(f"HL Order placed: {result}")
                    return result.get("result", {})
                else:
                    raise ValueError(f"HyperLiquid order failed: {result.get('retMsg', 'Unknown error')}")
                
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
            
            # HLAdapter returns Bybit-like format with retCode
            if result.get("retCode") == 0:
                positions = result.get("result", {}).get("list", [])
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
            # HLAdapter returns Bybit-like format with retCode
            return result.get("retCode") == 0
            
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
            
            async with adapter:
                result = await adapter.close_position(symbol, size)
                
                # HLAdapter returns Bybit-like format with retCode
                if result.get("retCode") == 0:
                    logger.info(f"HL Position closed: {result}")
                    return result.get("result", {})
                else:
                    raise ValueError(f"HyperLiquid close failed: {result.get('retMsg', 'Unknown error')}")
                
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
            
            async with adapter:
                result = await adapter.get_balance()
                
                # get_balance returns {"success": True, "data": {...}}
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


# ===========================
# Utility Functions
# ===========================

def normalize_symbol_for_hl(symbol: str) -> str:
    """
    Normalize symbol for HyperLiquid format.
    Bybit: BTCUSDT -> HyperLiquid: BTC
    """
    if symbol.endswith("USDT"):
        return symbol[:-4]
    if symbol.endswith("USDC"):
        return symbol[:-4]
    return symbol


def convert_side_for_hl(side: str) -> str:
    """
    Convert Bybit side format to HyperLiquid format.
    Bybit: Buy/Sell -> HyperLiquid: BUY/SELL
    """
    side_map = {
        "Buy": "BUY",
        "Sell": "SELL",
        "buy": "BUY",
        "sell": "SELL",
    }
    return side_map.get(side, side.upper())


def convert_order_type_for_hl(order_type: str) -> str:
    """
    Convert Bybit order type to HyperLiquid format.
    Bybit: Market/Limit -> HyperLiquid: MARKET/LIMIT
    """
    type_map = {
        "Market": "MARKET",
        "Limit": "LIMIT",
        "market": "MARKET",
        "limit": "LIMIT",
    }
    if order_type not in type_map:
        raise ValueError(f"Invalid order type: {order_type}")
    return type_map[order_type]


def normalize_response(response: dict, exchange: str) -> dict:
    """
    Normalize exchange response to unified format.
    
    Args:
        response: Raw exchange API response
        exchange: 'bybit' or 'hyperliquid'
    
    Returns:
        Normalized dict with 'success', 'data', 'error' keys
    """
    if exchange == "bybit":
        # Bybit format: {"retCode": 0, "retMsg": "OK", "result": {...}}
        return {
            "success": response.get("retCode") == 0,
            "data": response.get("result", {}),
            "error": response.get("retMsg") if response.get("retCode") != 0 else None
        }
    
    elif exchange == "hyperliquid":
        # HyperLiquid format: {"status": "ok", "response": {...}}
        return {
            "success": response.get("status") == "ok",
            "data": response.get("response", {}),
            "error": response.get("error") if response.get("status") != "ok" else None
        }
    
    else:
        # Unknown exchange - pass through
        return {
            "success": response.get("success", False),
            "data": response.get("data", response),
            "error": response.get("error")
        }

