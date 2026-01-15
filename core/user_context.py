"""
User Context Management for Multitenancy
=========================================
Thread-safe and async-safe user context using contextvars.

Best Practices Applied:
1. contextvars for proper async context isolation
2. No global state pollution
3. Automatic context propagation in TaskGroups
4. Type-safe tenant data access

Usage:
    from core.user_context import user_context, current_user_id, with_user_context

    # Set context for current async task
    async with user_context(user_id=123, exchange="bybit", account_type="demo"):
        user = current_user_id()  # Returns 123
        ctx = get_trading_context()  # Returns full context
        ...

    # Decorator usage
    @with_user_context
    async def process_signal(user_id: int, ...):
        # user context automatically set
        ...
"""

from __future__ import annotations

import asyncio
import contextvars
import threading
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Callable, TypeVar
from functools import wraps
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


# ═══════════════════════════════════════════════════════════════════════════════════
# CONTEXT VARIABLES (Thread-safe and Async-safe)
# ═══════════════════════════════════════════════════════════════════════════════════

# Primary user identifier
_user_id: contextvars.ContextVar[Optional[int]] = contextvars.ContextVar(
    'user_id', default=None
)

# Exchange context
_exchange: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'exchange', default=None
)

# Account type (demo/real/testnet/mainnet)
_account_type: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'account_type', default=None
)

# Strategy being processed
_strategy: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'strategy', default=None
)

# Request/operation ID for tracing
_request_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'request_id', default=None
)

# Additional metadata
_metadata: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar(
    'metadata', default={}
)


# ═══════════════════════════════════════════════════════════════════════════════════
# TRADING CONTEXT DATA CLASS
# ═══════════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TradingContext:
    """
    Immutable trading context for the current operation.
    
    Contains all tenant-specific information needed for:
    - Database queries (user_id, exchange, account_type)
    - API calls (exchange credentials selection)
    - Logging (request_id, strategy)
    """
    user_id: int
    exchange: str = "bybit"
    account_type: str = "demo"
    strategy: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Validate required fields
        if not self.user_id:
            raise ValueError("user_id is required for TradingContext")
    
    @property
    def is_demo(self) -> bool:
        return self.account_type in ("demo", "testnet")
    
    @property
    def is_real(self) -> bool:
        return self.account_type in ("real", "mainnet")
    
    @property
    def is_bybit(self) -> bool:
        return self.exchange == "bybit"
    
    @property
    def is_hyperliquid(self) -> bool:
        return self.exchange == "hyperliquid"
    
    def with_strategy(self, strategy: str) -> 'TradingContext':
        """Create new context with different strategy"""
        return TradingContext(
            user_id=self.user_id,
            exchange=self.exchange,
            account_type=self.account_type,
            strategy=strategy,
            request_id=self.request_id,
            metadata=self.metadata,
        )
    
    def with_account_type(self, account_type: str) -> 'TradingContext':
        """Create new context with different account type"""
        return TradingContext(
            user_id=self.user_id,
            exchange=self.exchange,
            account_type=account_type,
            strategy=self.strategy,
            request_id=self.request_id,
            metadata=self.metadata,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "exchange": self.exchange,
            "account_type": self.account_type,
            "strategy": self.strategy,
            "request_id": self.request_id,
            "metadata": self.metadata,
        }


# ═══════════════════════════════════════════════════════════════════════════════════
# CONTEXT GETTERS (Safe access)
# ═══════════════════════════════════════════════════════════════════════════════════

def current_user_id() -> Optional[int]:
    """Get current user ID from context"""
    return _user_id.get()


def current_exchange() -> Optional[str]:
    """Get current exchange from context"""
    return _exchange.get()


def current_account_type() -> Optional[str]:
    """Get current account type from context"""
    return _account_type.get()


def current_strategy() -> Optional[str]:
    """Get current strategy from context"""
    return _strategy.get()


def current_request_id() -> Optional[str]:
    """Get current request ID from context"""
    return _request_id.get()


def get_trading_context() -> Optional[TradingContext]:
    """
    Get full trading context from current contextvars.
    Returns None if no user_id is set.
    """
    user_id = _user_id.get()
    if user_id is None:
        return None
    
    return TradingContext(
        user_id=user_id,
        exchange=_exchange.get() or "bybit",
        account_type=_account_type.get() or "demo",
        strategy=_strategy.get(),
        request_id=_request_id.get(),
        metadata=_metadata.get().copy(),
    )


def require_trading_context() -> TradingContext:
    """
    Get trading context, raise error if not set.
    Use in functions that require user context.
    """
    ctx = get_trading_context()
    if ctx is None:
        raise RuntimeError("Trading context not set. Use user_context() or @with_user_context")
    return ctx


# ═══════════════════════════════════════════════════════════════════════════════════
# CONTEXT SETTERS
# ═══════════════════════════════════════════════════════════════════════════════════

def set_user_id(user_id: int) -> contextvars.Token:
    """Set user ID in context, returns token for reset"""
    return _user_id.set(user_id)


def set_exchange(exchange: str) -> contextvars.Token:
    """Set exchange in context"""
    return _exchange.set(exchange)


def set_account_type(account_type: str) -> contextvars.Token:
    """Set account type in context"""
    return _account_type.set(account_type)


def set_strategy(strategy: str) -> contextvars.Token:
    """Set strategy in context"""
    return _strategy.set(strategy)


def set_request_id(request_id: str) -> contextvars.Token:
    """Set request ID in context"""
    return _request_id.set(request_id)


def set_metadata(key: str, value: Any) -> None:
    """Set metadata value in context"""
    current = _metadata.get().copy()
    current[key] = value
    _metadata.set(current)


# ═══════════════════════════════════════════════════════════════════════════════════
# ASYNC CONTEXT MANAGER
# ═══════════════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def user_context(
    user_id: int,
    exchange: str = None,
    account_type: str = None,
    strategy: str = None,
    request_id: str = None,
    **metadata
):
    """
    Async context manager for setting user context.
    
    Context is automatically propagated to child tasks created with
    asyncio.create_task() and TaskGroup.
    
    Usage:
        async with user_context(user_id=123, exchange="bybit", account_type="demo"):
            # All database queries and API calls use this context
            await process_user_data()
    """
    # Store tokens for cleanup
    tokens = []
    
    try:
        tokens.append(_user_id.set(user_id))
        
        if exchange is not None:
            tokens.append(_exchange.set(exchange))
        
        if account_type is not None:
            tokens.append(_account_type.set(account_type))
        
        if strategy is not None:
            tokens.append(_strategy.set(strategy))
        
        if request_id is not None:
            tokens.append(_request_id.set(request_id))
        
        if metadata:
            current_meta = _metadata.get().copy()
            current_meta.update(metadata)
            tokens.append(_metadata.set(current_meta))
        
        yield get_trading_context()
        
    finally:
        # Reset all context vars to previous values
        for token in reversed(tokens):
            token.var.reset(token)


@contextmanager
def user_context_sync(
    user_id: int,
    exchange: str = None,
    account_type: str = None,
    strategy: str = None,
    request_id: str = None,
    **metadata
):
    """Sync version of user_context for non-async code"""
    tokens = []
    
    try:
        tokens.append(_user_id.set(user_id))
        
        if exchange is not None:
            tokens.append(_exchange.set(exchange))
        
        if account_type is not None:
            tokens.append(_account_type.set(account_type))
        
        if strategy is not None:
            tokens.append(_strategy.set(strategy))
        
        if request_id is not None:
            tokens.append(_request_id.set(request_id))
        
        if metadata:
            current_meta = _metadata.get().copy()
            current_meta.update(metadata)
            tokens.append(_metadata.set(current_meta))
        
        yield get_trading_context()
        
    finally:
        for token in reversed(tokens):
            token.var.reset(token)


# ═══════════════════════════════════════════════════════════════════════════════════
# DECORATORS
# ═══════════════════════════════════════════════════════════════════════════════════

def with_user_context(
    user_id_param: str = "user_id",
    exchange_param: str = "exchange",
    account_type_param: str = "account_type"
):
    """
    Decorator to automatically set user context from function parameters.
    
    Usage:
        @with_user_context()
        async def process_signal(user_id: int, symbol: str, ...):
            ctx = require_trading_context()  # Available here
            ...
        
        @with_user_context(user_id_param="uid")
        async def other_func(uid: int, ...):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Extract user_id from args/kwargs
                user_id = kwargs.get(user_id_param)
                exchange = kwargs.get(exchange_param)
                account_type = kwargs.get(account_type_param)
                
                # If user_id not in kwargs, try positional args
                if user_id is None:
                    import inspect
                    sig = inspect.signature(func)
                    params = list(sig.parameters.keys())
                    if user_id_param in params:
                        idx = params.index(user_id_param)
                        if idx < len(args):
                            user_id = args[idx]
                
                if user_id is None:
                    # No user context, call directly
                    return await func(*args, **kwargs)
                
                async with user_context(
                    user_id=user_id,
                    exchange=exchange,
                    account_type=account_type
                ):
                    return await func(*args, **kwargs)
            
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                user_id = kwargs.get(user_id_param)
                exchange = kwargs.get(exchange_param)
                account_type = kwargs.get(account_type_param)
                
                if user_id is None:
                    import inspect
                    sig = inspect.signature(func)
                    params = list(sig.parameters.keys())
                    if user_id_param in params:
                        idx = params.index(user_id_param)
                        if idx < len(args):
                            user_id = args[idx]
                
                if user_id is None:
                    return func(*args, **kwargs)
                
                with user_context_sync(
                    user_id=user_id,
                    exchange=exchange,
                    account_type=account_type
                ):
                    return func(*args, **kwargs)
            
            return sync_wrapper
    
    return decorator


# ═══════════════════════════════════════════════════════════════════════════════════
# LOGGING INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════════

class ContextLoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that automatically includes user context in log messages.
    
    Usage:
        logger = ContextLoggerAdapter(logging.getLogger(__name__))
        logger.info("Processing signal")
        # Output: "[user=123 exchange=bybit] Processing signal"
    """
    
    def process(self, msg, kwargs):
        ctx = get_trading_context()
        if ctx:
            prefix = f"[user={ctx.user_id}"
            if ctx.exchange:
                prefix += f" {ctx.exchange}"
            if ctx.account_type:
                prefix += f"/{ctx.account_type}"
            if ctx.strategy:
                prefix += f" {ctx.strategy}"
            if ctx.request_id:
                prefix += f" req={ctx.request_id[:8]}"
            prefix += "]"
            msg = f"{prefix} {msg}"
        return msg, kwargs


def get_context_logger(name: str) -> ContextLoggerAdapter:
    """Get logger with automatic context inclusion"""
    return ContextLoggerAdapter(logging.getLogger(name), {})


# ═══════════════════════════════════════════════════════════════════════════════════
# BATCH PROCESSING HELPERS
# ═══════════════════════════════════════════════════════════════════════════════════

async def run_for_users(
    user_ids: list[int],
    func: Callable,
    *args,
    max_concurrent: int = 10,
    **kwargs
):
    """
    Run async function for multiple users with proper context isolation.
    
    Uses semaphore to limit concurrent operations.
    Each user gets its own isolated context.
    
    Usage:
        async def process_user(user_id: int):
            ctx = require_trading_context()
            ...
        
        results = await run_for_users([1, 2, 3], process_user)
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def run_with_context(user_id: int):
        async with semaphore:
            async with user_context(user_id=user_id):
                return await func(user_id, *args, **kwargs)
    
    tasks = [run_with_context(uid) for uid in user_ids]
    return await asyncio.gather(*tasks, return_exceptions=True)


async def run_for_accounts(
    user_id: int,
    account_types: list[str],
    func: Callable,
    *args,
    exchange: str = "bybit",
    **kwargs
):
    """
    Run async function for multiple account types with context.
    
    Usage:
        async def sync_positions(account_type: str):
            ctx = require_trading_context()
            ...
        
        results = await run_for_accounts(123, ["demo", "real"], sync_positions)
    """
    async def run_with_context(acc_type: str):
        async with user_context(
            user_id=user_id,
            exchange=exchange,
            account_type=acc_type
        ):
            return await func(acc_type, *args, **kwargs)
    
    tasks = [run_with_context(acc) for acc in account_types]
    return await asyncio.gather(*tasks, return_exceptions=True)
