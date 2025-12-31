"""
Unified Exchange Client Factory
Provides a clean interface for creating exchange clients with proper configuration
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Optional, Dict, Any, TypedDict, Tuple
from enum import Enum
from dataclasses import dataclass
from weakref import WeakValueDictionary

from core.cache import balance_cache, async_cached
from core.rate_limiter import bybit_limiter, hl_limiter


logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# CLIENT CONNECTION POOL - Prevent session leaks!
# ═══════════════════════════════════════════════════════════════
# Cache for exchange clients to prevent creating new sessions every request
# Key: (user_id, exchange_type, account_type), Value: (client, last_used_timestamp)
_client_pool: Dict[Tuple[int, str, str], Tuple[Any, float]] = {}
_client_pool_lock = asyncio.Lock()
_CLIENT_POOL_TTL = 300  # 5 minutes - unused clients will be closed
_CLIENT_POOL_CLEANUP_INTERVAL = 60  # Check for stale clients every minute
_last_cleanup_time = 0.0

# Cache for auth errors - don't create clients for users with expired keys
# Key: (user_id, exchange_type, account_type), Value: timestamp
_auth_error_cache: Dict[Tuple[int, str, str], float] = {}
_AUTH_ERROR_CACHE_TTL = 3600  # 1 hour


def _safe_float(val, default=0.0):
    """Safely convert value to float, handling empty strings and None"""
    if val is None or val == '':
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


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
    user_id: Optional[int] = None  # For auth error caching
    
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
    
    # Auth error codes for Bybit
    AUTH_ERROR_CODES = {"33004", "10003", "10004", "10005"}
    
    def __init__(self, credentials: ExchangeCredentials):
        self.credentials = credentials
        self._client = None
        self._initialized = False
        
        # Select rate limiter based on exchange
        if credentials.exchange == ExchangeType.HYPERLIQUID:
            self._limiter = hl_limiter
        else:
            self._limiter = bybit_limiter
    
    def _cache_auth_error(self) -> None:
        """Cache auth error for this user to prevent repeated failed requests"""
        if not self.credentials.user_id:
            return
        
        pool_key = (
            self.credentials.user_id,
            self.credentials.exchange.value,
            self.credentials.mode.value
        )
        _auth_error_cache[pool_key] = time.time()
        logger.warning(f"Auth error cached for user {self.credentials.user_id} "
                      f"({self.credentials.exchange.value}/{self.credentials.mode.value}) - "
                      f"will skip requests for {_AUTH_ERROR_CACHE_TTL}s")
    
    def _is_auth_error(self, error: Exception) -> bool:
        """Check if error is an authentication error that should be cached"""
        error_str = str(error).lower()
        # Check for Bybit auth error codes
        for code in self.AUTH_ERROR_CODES:
            if code in error_str:
                return True
        # Check for common auth error messages
        if any(x in error_str for x in ["expired", "invalid key", "authentication"]):
            return True
        return False
    
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
            # Validate HyperLiquid credentials
            if not self.credentials.private_key:
                raise ValueError("HyperLiquid private_key is required")
            
            from hl_adapter import HLAdapter
            self._client = HLAdapter(
                private_key=self.credentials.private_key,
                testnet=(self.credentials.mode == AccountMode.TESTNET),
                vault_address=self.credentials.vault_address
            )
            await self._client.initialize()
        else:
            # Validate Bybit credentials
            if not self.credentials.api_key or not self.credentials.api_secret:
                raise ValueError("Bybit api_key and api_secret are required")
            
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
        if self._client:
            try:
                await self._client.close()
            except Exception as e:
                logger.debug(f"Error closing exchange client: {e}")
        self._client = None
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
                    "total_equity": _safe_float(result.get("accountValue")),
                    "available_balance": _safe_float(result.get("withdrawable")),
                    "margin_used": _safe_float(result.get("marginUsed")),
                    "unrealized_pnl": _safe_float(result.get("unrealizedPnl")),
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
            # Check if this is an auth error and cache it
            if self._is_auth_error(e):
                self._cache_auth_error()
            else:
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
                        "mark_price": pos.mark_price or pos.entry_price,  # Fallback to entry if no mark
                        "unrealized_pnl": pos.unrealized_pnl,
                        "leverage": pos.leverage,
                        "liquidation_price": pos.liquidation_price,
                        "stop_loss": pos.stop_loss,
                        "take_profit": pos.take_profit
                    })
            
            return ExchangeResult(
                success=True,
                data=positions,
                exchange=self.credentials.exchange.value
            )
            
        except Exception as e:
            # Check if this is an auth error and cache it
            if self._is_auth_error(e):
                self._cache_auth_error()
            else:
                logger.error(f"get_positions error: {e}", exc_info=True)
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
            # Check if this is an auth error and cache it
            if self._is_auth_error(e):
                self._cache_auth_error()
            else:
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
            # Check if this is an auth error and cache it
            if self._is_auth_error(e):
                self._cache_auth_error()
            else:
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
            # Check if this is an auth error and cache it
            if self._is_auth_error(e):
                self._cache_auth_error()
            else:
                logger.error(f"close_position error: {e}")
            return ExchangeResult(success=False, error=str(e), exchange=self.credentials.exchange.value)


# ═══════════════════════════════════════════════════════════════
# FACTORY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

async def _cleanup_stale_clients():
    """Close clients that haven't been used for a while"""
    global _last_cleanup_time
    
    now = time.time()
    if now - _last_cleanup_time < _CLIENT_POOL_CLEANUP_INTERVAL:
        return
    
    _last_cleanup_time = now
    
    async with _client_pool_lock:
        stale_keys = []
        for key, (client, last_used) in _client_pool.items():
            if now - last_used > _CLIENT_POOL_TTL:
                stale_keys.append(key)
        
        for key in stale_keys:
            client, _ = _client_pool.pop(key, (None, 0))
            if client:
                try:
                    await client.close()
                    logger.debug(f"Closed stale client for {key}")
                except Exception as e:
                    logger.debug(f"Error closing stale client: {e}")


async def get_exchange_client(user_id: int, exchange_type: Optional[str] = None, account_type: Optional[str] = None) -> UnifiedExchangeClient:
    """
    Get or create an exchange client for a user.
    Uses a connection pool to prevent creating new sessions every request.
    
    Args:
        user_id: Telegram user ID
        exchange_type: Force specific exchange ('bybit' or 'hyperliquid')
                      If None, uses user's preferred exchange
        account_type: Force account type ('demo', 'real', 'testnet')
                     If None, uses user's trading_mode setting
    
    Returns:
        UnifiedExchangeClient ready to use (pooled, do NOT close it manually!)
    
    NOTE: Clients are pooled and reused. Do NOT call client.close() - 
          the pool handles lifecycle automatically.
    """
    import db
    
    # Cleanup stale clients periodically
    await _cleanup_stale_clients()
    
    # Get user's exchange preference
    if exchange_type is None:
        exchange_type = db.get_exchange_type(user_id) or 'bybit'
    
    # Determine account_type
    if account_type is None:
        trading_mode = db.get_trading_mode(user_id)
        account_type = "real" if trading_mode == "real" else "demo"
    
    # Create pool key
    pool_key = (user_id, exchange_type, account_type)
    
    # Check if user has auth error cached - skip creating client
    now = time.time()
    if pool_key in _auth_error_cache:
        error_ts = _auth_error_cache[pool_key]
        if now - error_ts < _AUTH_ERROR_CACHE_TTL:
            raise ValueError(f"API key error cached for user {user_id} (retry in {int(_AUTH_ERROR_CACHE_TTL - (now - error_ts))}s)")
        else:
            del _auth_error_cache[pool_key]
    
    async with _client_pool_lock:
        # Check if we have a valid cached client
        if pool_key in _client_pool:
            client, _ = _client_pool[pool_key]
            if client._initialized and client._client is not None:
                # Update last used time
                _client_pool[pool_key] = (client, time.time())
                return client
            else:
                # Client is closed/invalid, remove from pool
                _client_pool.pop(pool_key, None)
        
        # Create new client
        exchange = ExchangeType(exchange_type) if exchange_type else ExchangeType.BYBIT
        
        if exchange == ExchangeType.HYPERLIQUID:
            hl_creds = db.get_hl_credentials(user_id)
            credentials = ExchangeCredentials(
                exchange=ExchangeType.HYPERLIQUID,
                private_key=hl_creds.get("hl_private_key"),
                wallet_address=hl_creds.get("hl_wallet_address"),
                vault_address=hl_creds.get("hl_vault_address"),
                mode=AccountMode.TESTNET if hl_creds.get("hl_testnet") else AccountMode.REAL,
                user_id=user_id
            )
        else:
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
                mode=mode,
                user_id=user_id
            )
        
        client = UnifiedExchangeClient(credentials)
        await client.initialize()
        
        # Store in pool
        _client_pool[pool_key] = (client, time.time())
        logger.debug(f"Created new pooled client for user {user_id}, {exchange_type}, {account_type}")
        
        return client


async def invalidate_client(user_id: int, exchange_type: Optional[str] = None, account_type: Optional[str] = None):
    """
    Force close and remove a client from the pool.
    Call this when user credentials change.
    """
    keys_to_remove = []
    
    async with _client_pool_lock:
        for key in list(_client_pool.keys()):
            uid, exch, acc = key
            if uid == user_id:
                if exchange_type is None or exch == exchange_type:
                    if account_type is None or acc == account_type:
                        keys_to_remove.append(key)
        
        for key in keys_to_remove:
            client, _ = _client_pool.pop(key, (None, 0))
            if client:
                try:
                    await client.close()
                    logger.debug(f"Invalidated client for {key}")
                except Exception as e:
                    logger.debug(f"Error closing invalidated client: {e}")
    
    # Also clear auth error cache for this user
    clear_auth_error_cache(user_id, exchange_type, account_type)


def clear_auth_error_cache(user_id: int, exchange_type: Optional[str] = None, account_type: Optional[str] = None):
    """
    Clear auth error cache for a user.
    Call this when user updates their API credentials.
    """
    keys_to_remove = []
    
    for key in list(_auth_error_cache.keys()):
        uid, exch, acc = key
        if uid == user_id:
            if exchange_type is None or exch == exchange_type:
                if account_type is None or acc == account_type:
                    keys_to_remove.append(key)
    
    for key in keys_to_remove:
        _auth_error_cache.pop(key, None)
        logger.debug(f"Cleared auth error cache for {key}")


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
