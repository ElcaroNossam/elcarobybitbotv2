"""
Unified Exchange Client Factory
Provides a clean interface for creating exchange clients with proper configuration
"""
from __future__ import annotations

import logging
from typing import Optional, Dict, Any, TypedDict
from enum import Enum
from dataclasses import dataclass

from core.cache import balance_cache, async_cached
from core.rate_limiter import bybit_limiter, hl_limiter


logger = logging.getLogger(__name__)


class ExchangeType(str, Enum):
    BYBIT = "bybit"
    HYPERLIQUID = "hyperliquid"


class AccountMode(str, Enum):
    DEMO = "demo"
    REAL = "real"
    TESTNET = "testnet"


@dataclass
class ExchangeCredentials:
    """Credentials for exchange connection"""
    exchange: ExchangeType
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    private_key: Optional[str] = None  # For HyperLiquid
    wallet_address: Optional[str] = None
    vault_address: Optional[str] = None
    mode: AccountMode = AccountMode.DEMO
    
    @property
    def is_valid(self) -> bool:
        if self.exchange == ExchangeType.BYBIT:
            return bool(self.api_key and self.api_secret)
        elif self.exchange == ExchangeType.HYPERLIQUID:
            return bool(self.private_key)
        return False


class ExchangeResult(TypedDict, total=False):
    """Standard result format for exchange operations"""
    success: bool
    data: Any
    error: Optional[str]
    exchange: str


class UnifiedExchangeClient:
    """
    Unified client for interacting with any supported exchange.
    Handles rate limiting, caching, and error normalization.
    
    Usage:
        async with UnifiedExchangeClient(credentials) as client:
            balance = await client.get_balance()
            await client.place_order(symbol="BTCUSDT", side="Buy", qty=0.001)
    """
    
    def __init__(self, credentials: ExchangeCredentials):
        self.credentials = credentials
        self._client = None
        self._initialized = False
        
        # Select rate limiter based on exchange
        if credentials.exchange == ExchangeType.HYPERLIQUID:
            self._limiter = hl_limiter
        else:
            self._limiter = bybit_limiter
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def initialize(self) -> None:
        """Initialize the exchange client"""
        if self._initialized:
            return
        
        if self.credentials.exchange == ExchangeType.HYPERLIQUID:
            from hl_adapter import HLAdapter
            self._client = HLAdapter(
                private_key=self.credentials.private_key,
                testnet=(self.credentials.mode == AccountMode.TESTNET),
                vault_address=self.credentials.vault_address
            )
            await self._client.initialize()
        else:
            # Bybit client setup
            from exchanges.bybit import BybitExchange
            self._client = BybitExchange(
                api_key=self.credentials.api_key,
                api_secret=self.credentials.api_secret,
                demo=(self.credentials.mode == AccountMode.DEMO),
                testnet=(self.credentials.mode == AccountMode.TESTNET)
            )
            await self._client.initialize()
        
        self._initialized = True
    
    async def close(self) -> None:
        """Close the client connection"""
        if self._client and self._initialized:
            await self._client.close()
            self._initialized = False
    
    def _normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol for the exchange"""
        symbol = symbol.upper()
        
        if self.credentials.exchange == ExchangeType.HYPERLIQUID:
            # HyperLiquid uses base coin only (BTC, ETH)
            return symbol.replace("USDT", "").replace("USDC", "").replace("PERP", "")
        else:
            # Bybit uses full symbol (BTCUSDT)
            if not symbol.endswith("USDT"):
                symbol = symbol + "USDT"
            return symbol
    
    async def get_balance(self) -> ExchangeResult:
        """Get account balance with caching"""
        cache_key = f"balance:{self.credentials.exchange}:{self.credentials.mode}"
        
        cached = balance_cache.get(cache_key)
        if cached:
            return cached
        
        try:
            await self._limiter.acquire("balance", "balance")
            
            if self.credentials.exchange == ExchangeType.HYPERLIQUID:
                result = await self._client.get_balance()
                data = {
                    "total_equity": float(result.get("accountValue", 0)),
                    "available_balance": float(result.get("withdrawable", 0)),
                    "margin_used": float(result.get("marginUsed", 0)),
                    "unrealized_pnl": float(result.get("unrealizedPnl", 0)),
                    "currency": "USDC"
                }
            else:
                balance = await self._client.get_balance()
                data = {
                    "total_equity": balance.total_equity,
                    "available_balance": balance.available_balance,
                    "margin_used": balance.margin_used,
                    "unrealized_pnl": balance.unrealized_pnl,
                    "currency": balance.currency
                }
            
            result = ExchangeResult(
                success=True,
                data=data,
                exchange=self.credentials.exchange.value
            )
            balance_cache.set(cache_key, result, ttl=15.0)
            return result
            
        except Exception as e:
            logger.error(f"get_balance error: {e}")
            return ExchangeResult(
                success=False,
                error=str(e),
                exchange=self.credentials.exchange.value
            )
    
    async def get_positions(self, symbol: Optional[str] = None) -> ExchangeResult:
        """Get open positions"""
        try:
            await self._limiter.acquire("positions", "position")
            
            if self.credentials.exchange == ExchangeType.HYPERLIQUID:
                result = await self._client.fetch_positions(
                    symbol=self._normalize_symbol(symbol) if symbol else None
                )
                positions = result.get("result", {}).get("list", [])
            else:
                positions_raw = await self._client.get_positions()
                positions = []
                for pos in positions_raw:
                    if symbol and pos.symbol != self._normalize_symbol(symbol):
                        continue
                    positions.append({
                        "symbol": pos.symbol,
                        "side": "Long" if pos.is_long else "Short",
                        "size": pos.size,
                        "entry_price": pos.entry_price,
                        "unrealized_pnl": pos.unrealized_pnl,
                        "leverage": pos.leverage,
                        "liquidation_price": pos.liquidation_price
                    })
            
            return ExchangeResult(
                success=True,
                data=positions,
                exchange=self.credentials.exchange.value
            )
            
        except Exception as e:
            logger.error(f"get_positions error: {e}")
            return ExchangeResult(
                success=False,
                error=str(e),
                exchange=self.credentials.exchange.value
            )
    
    async def place_order(
        self,
        symbol: str,
        side: str,
        qty: float,
        order_type: str = "Market",
        price: Optional[float] = None,
        leverage: Optional[int] = None,
        take_profit: Optional[float] = None,
        stop_loss: Optional[float] = None,
        reduce_only: bool = False
    ) -> ExchangeResult:
        """Place an order on the exchange"""
        try:
            await self._limiter.acquire("order", "order")
            
            symbol = self._normalize_symbol(symbol)
            
            # Set leverage if specified
            if leverage:
                await self.set_leverage(symbol, leverage)
            
            if self.credentials.exchange == ExchangeType.HYPERLIQUID:
                result = await self._client.place_order(
                    symbol=symbol,
                    side=side,
                    qty=qty,
                    order_type=order_type,
                    price=price,
                    reduce_only=reduce_only,
                    take_profit=take_profit,
                    stop_loss=stop_loss
                )
                
                if result.get("success"):
                    return ExchangeResult(
                        success=True,
                        data=result.get("data", {}),
                        exchange=self.credentials.exchange.value
                    )
                else:
                    return ExchangeResult(
                        success=False,
                        error=result.get("error", "Unknown error"),
                        exchange=self.credentials.exchange.value
                    )
            else:
                from exchanges.base import OrderSide, OrderType as OT
                
                order_side = OrderSide.BUY if side.upper() in ("BUY", "LONG") else OrderSide.SELL
                ot = OT.MARKET if order_type.upper() == "MARKET" else OT.LIMIT
                
                result = await self._client.place_order(
                    symbol=symbol,
                    side=order_side,
                    size=qty,
                    price=price,
                    order_type=ot,
                    reduce_only=reduce_only
                )
                
                # Set TP/SL after market order
                if result.success and take_profit:
                    await self._client.set_take_profit(symbol, take_profit)
                if result.success and stop_loss:
                    await self._client.set_stop_loss(symbol, stop_loss)
                
                return ExchangeResult(
                    success=result.success,
                    data={
                        "order_id": result.order_id,
                        "filled_size": result.filled_size,
                        "avg_price": result.avg_price
                    } if result.success else None,
                    error=result.error,
                    exchange=self.credentials.exchange.value
                )
            
        except Exception as e:
            logger.error(f"place_order error: {e}")
            return ExchangeResult(
                success=False,
                error=str(e),
                exchange=self.credentials.exchange.value
            )
    
    async def set_leverage(self, symbol: str, leverage: int) -> ExchangeResult:
        """Set leverage for a symbol"""
        try:
            symbol = self._normalize_symbol(symbol)
            
            if self.credentials.exchange == ExchangeType.HYPERLIQUID:
                result = await self._client.set_leverage(symbol, leverage)
                return ExchangeResult(success=True, data=result, exchange=self.credentials.exchange.value)
            else:
                success = await self._client.set_leverage(symbol, leverage)
                return ExchangeResult(success=success, exchange=self.credentials.exchange.value)
            
        except Exception as e:
            logger.error(f"set_leverage error: {e}")
            return ExchangeResult(success=False, error=str(e), exchange=self.credentials.exchange.value)
    
    async def close_position(self, symbol: str, size: Optional[float] = None) -> ExchangeResult:
        """Close an open position"""
        try:
            await self._limiter.acquire("order", "order")
            
            symbol = self._normalize_symbol(symbol)
            
            if self.credentials.exchange == ExchangeType.HYPERLIQUID:
                result = await self._client.close_position(symbol, size)
                return ExchangeResult(
                    success=result.get("success", False),
                    data=result.get("data"),
                    error=result.get("error"),
                    exchange=self.credentials.exchange.value
                )
            else:
                result = await self._client.close_position(symbol, size)
                return ExchangeResult(
                    success=result.success,
                    data={"order_id": result.order_id} if result.success else None,
                    error=result.error,
                    exchange=self.credentials.exchange.value
                )
            
        except Exception as e:
            logger.error(f"close_position error: {e}")
            return ExchangeResult(success=False, error=str(e), exchange=self.credentials.exchange.value)


# ═══════════════════════════════════════════════════════════════
# FACTORY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

async def get_exchange_client(user_id: int, exchange_type: Optional[str] = None, account_type: Optional[str] = None) -> UnifiedExchangeClient:
    """
    Create an exchange client for a user.
    
    Args:
        user_id: Telegram user ID
        exchange_type: Force specific exchange ('bybit' or 'hyperliquid')
                      If None, uses user's preferred exchange
        account_type: Force account type ('demo', 'real', 'testnet')
                     If None, uses user's trading_mode setting
    
    Returns:
        UnifiedExchangeClient ready to use
    
    Example:
        async with await get_exchange_client(user_id, account_type='demo') as client:
            balance = await client.get_balance()
    """
    import db
    
    # Get user's exchange preference
    if exchange_type is None:
        exchange_type = db.get_exchange_type(user_id)
    
    exchange = ExchangeType(exchange_type) if exchange_type else ExchangeType.BYBIT
    
    if exchange == ExchangeType.HYPERLIQUID:
        hl_creds = db.get_hl_credentials(user_id)
        credentials = ExchangeCredentials(
            exchange=ExchangeType.HYPERLIQUID,
            private_key=hl_creds.get("hl_private_key"),
            wallet_address=hl_creds.get("hl_wallet_address"),
            vault_address=hl_creds.get("hl_vault_address"),
            mode=AccountMode.TESTNET if hl_creds.get("hl_testnet") else AccountMode.REAL
        )
    else:
        # Use explicit account_type if provided, otherwise get from user settings
        if account_type is None:
            trading_mode = db.get_trading_mode(user_id)
            account_type = "real" if trading_mode == "real" else "demo"
        
        api_key, api_secret = db.get_user_credentials(user_id, account_type)
        
        # Support testnet mode
        if account_type == "testnet":
            mode = AccountMode.TESTNET
        elif account_type == "real":
            mode = AccountMode.REAL
        else:
            mode = AccountMode.DEMO
        
        credentials = ExchangeCredentials(
            exchange=ExchangeType.BYBIT,
            api_key=api_key,
            api_secret=api_secret,
            mode=mode
        )
    
    client = UnifiedExchangeClient(credentials)
    await client.initialize()
    return client


def create_credentials_from_config(
    exchange: str,
    api_key: Optional[str] = None,
    api_secret: Optional[str] = None,
    private_key: Optional[str] = None,
    wallet_address: Optional[str] = None,
    mode: str = "demo"
) -> ExchangeCredentials:
    """Helper to create credentials from raw config values"""
    exchange_type = ExchangeType(exchange.lower())
    account_mode = AccountMode(mode.lower())
    
    return ExchangeCredentials(
        exchange=exchange_type,
        api_key=api_key,
        api_secret=api_secret,
        private_key=private_key,
        wallet_address=wallet_address,
        mode=account_mode
    )
