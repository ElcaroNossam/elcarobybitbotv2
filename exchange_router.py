"""
Exchange Router - Unified trading execution layer for Bybit and HyperLiquid

P0.2: This module is the SINGLE point of order execution for both bot.py and webapp.
No direct exchange API calls should happen outside this module.

Key features:
- Execution targets model: orders execute on specified targets only
- Per-account qty calculation (P0.6)
- Risk validation (P0.7)
- Consistent response format
- ATR state persistence (P0.4)
- Manual SL/TP override support (P0.8)

Architecture (as of Dec 30, 2025):
- Target = (exchange, env) where env = paper|live
- Monitoring iterates ALL user targets
- active_positions filled ONLY by reconcile (monitor)
- Bot/WebApp write order_intent, reconcile creates positions
"""
import logging
import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum

import db
from hl_adapter import HLAdapter

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# HL CREDENTIALS HELPER
# ═══════════════════════════════════════════════════════════════════════════════

def _get_hl_credentials_for_env(hl_creds: dict, env: str) -> tuple:
    """
    Get the correct HyperLiquid credentials based on env (paper/live).
    Supports both new architecture and legacy format with fallback.
    
    HyperLiquid API Wallet Architecture:
    - private_key: API wallet key (used for signing)
    - wallet_address: Main wallet address (where funds are, for balance queries)
    - vault_address: Only needed for trading on behalf of a VAULT/SUBACCOUNT.
                     When API wallet is authorized on main wallet via UI (app.hyperliquid.xyz/API),
                     vault_address should be None - orders automatically go to main wallet.
    
    Returns: (private_key, is_testnet, wallet_address, vault_address)
    """
    is_testnet = env == "paper"
    
    # Try new architecture first
    if is_testnet:
        private_key = hl_creds.get("hl_testnet_private_key")
        wallet_address = hl_creds.get("hl_testnet_wallet_address")
    else:
        private_key = hl_creds.get("hl_mainnet_private_key")
        wallet_address = hl_creds.get("hl_mainnet_wallet_address")
    
    # Fallback to legacy format
    if not private_key:
        private_key = hl_creds.get("hl_private_key")
        wallet_address = hl_creds.get("hl_wallet_address")
        if private_key:
            is_testnet = hl_creds.get("hl_testnet", False)
    
    # IMPORTANT: When API wallet is authorized via UI (Authorize API Wallet button),
    # vault_address should be None. Orders signed by API wallet automatically
    # execute on the main wallet that authorized it.
    # vault_address is ONLY needed for vault/subaccount trading.
    vault_address = None
    
    return private_key, is_testnet, wallet_address, vault_address


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS AND DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

class Exchange(str, Enum):
    BYBIT = "bybit"
    HYPERLIQUID = "hyperliquid"


class Env(str, Enum):
    """
    Unified environment type across all exchanges.
    paper = demo/testnet (no real money)
    live = real/mainnet (real money)
    """
    PAPER = "paper"
    LIVE = "live"


# Legacy compatibility - maps to Env
class AccountType(str, Enum):
    DEMO = "demo"
    REAL = "real"
    TESTNET = "testnet"
    MAINNET = "mainnet"


# Mapping functions for env normalization
def normalize_env(account_type: str) -> str:
    """Convert account_type to unified env (paper/live)."""
    mapping = {
        "demo": Env.PAPER.value,
        "testnet": Env.PAPER.value,
        "real": Env.LIVE.value,
        "mainnet": Env.LIVE.value,
        "paper": Env.PAPER.value,
        "live": Env.LIVE.value,
    }
    return mapping.get(account_type.lower(), Env.PAPER.value)


def denormalize_env(env: str, exchange: str) -> str:
    """Convert unified env back to exchange-specific account_type."""
    if exchange == Exchange.BYBIT.value:
        return "demo" if env == Env.PAPER.value else "real"
    elif exchange == Exchange.HYPERLIQUID.value:
        return "testnet" if env == Env.PAPER.value else "mainnet"
    return env


class OrderSide(str, Enum):
    BUY = "Buy"
    SELL = "Sell"


class OrderType(str, Enum):
    MARKET = "Market"
    LIMIT = "Limit"


@dataclass
class Target:
    """
    Execution target = specific place where orders execute.
    This is the PRIMARY key for positions: (user_id, exchange, env, symbol)
    """
    exchange: str  # "bybit" | "hyperliquid"
    env: str  # "paper" | "live"
    
    # Configuration
    is_enabled: bool = True
    max_positions: int = 10
    max_leverage: int = 100
    risk_limit_pct: float = 30.0
    priority: int = 0
    label: str = ""
    
    @property
    def key(self) -> str:
        """Unique key for this target."""
        return f"{self.exchange}:{self.env}"
    
    @property
    def account_type(self) -> str:
        """Legacy account_type for backward compatibility."""
        return denormalize_env(self.env, self.exchange)
    
    def __hash__(self):
        return hash(self.key)
    
    def __eq__(self, other):
        if isinstance(other, Target):
            return self.key == other.key
        return False


# Alias for backward compatibility
ExecutionTarget = Target


def get_user_targets(user_id: int) -> list[Target]:
    """
    Get all enabled targets for user.
    This is the single source of truth for "where can this user trade".
    
    Returns up to 4 targets:
    - Bybit paper (demo)
    - Bybit live (real)
    - HyperLiquid paper (testnet)
    - HyperLiquid live (mainnet)
    """
    targets = []
    
    # Check Bybit credentials
    try:
        creds = db.get_all_user_credentials(user_id)
        trading_mode = db.get_trading_mode(user_id) or "demo"
        
        # Bybit demo/paper
        if creds.get("demo_api_key") and trading_mode in ("demo", "both"):
            targets.append(Target(
                exchange=Exchange.BYBIT.value,
                env=Env.PAPER.value,
                is_enabled=True,
                label="Bybit Demo"
            ))
        
        # Bybit real/live
        if creds.get("real_api_key") and trading_mode in ("real", "both"):
            targets.append(Target(
                exchange=Exchange.BYBIT.value,
                env=Env.LIVE.value,
                is_enabled=True,
                label="Bybit Real"
            ))
    except Exception as e:
        logger.warning(f"Failed to get Bybit credentials for {user_id}: {e}")
    
    # Check HyperLiquid credentials
    try:
        hl_creds = db.get_hl_credentials(user_id)
        # Check all possible keys (new architecture + legacy)
        has_hl_key = (hl_creds.get("hl_testnet_private_key") or 
                      hl_creds.get("hl_mainnet_private_key") or
                      hl_creds.get("hl_private_key"))
        hl_enabled = hl_creds.get("hl_enabled")
        if has_hl_key and hl_enabled:
            env = Env.PAPER.value if hl_creds.get("hl_testnet") else Env.LIVE.value
            targets.append(Target(
                exchange=Exchange.HYPERLIQUID.value,
                env=env,
                is_enabled=True,
                label=f"HyperLiquid {'Testnet' if env == Env.PAPER.value else 'Mainnet'}"
            ))
    except Exception as e:
        logger.warning(f"Failed to get HL credentials for {user_id}: {e}")
    
    return targets


@dataclass
class OrderIntent:
    """
    Order intent - what user wants to do.
    This is converted to execution on each target.
    """
    user_id: int
    symbol: str
    side: str  # "Buy" or "Sell"
    order_type: str = "Market"
    
    # Size specification (one of these)
    qty: float | None = None  # Fixed qty
    notional_pct: float | None = None  # % of balance (will calculate qty per target)
    notional_usd: float | None = None  # Fixed USD amount
    
    # Risk parameters
    leverage: int | None = None
    sl_percent: float | None = None
    tp_percent: float | None = None
    sl_price: float | None = None
    tp_price: float | None = None
    
    # Limit order
    price: float | None = None
    
    # Metadata
    strategy: str | None = None
    signal_id: int | None = None
    timeframe: str = "24h"
    reduce_only: bool = False
    
    # Execution control
    targets: list[ExecutionTarget] = field(default_factory=list)
    source: str = "bot"  # "bot", "webapp", "signal"
    client_order_id: str | None = None


@dataclass
class ExecutionResult:
    """Result of order execution on one target"""
    target: ExecutionTarget
    success: bool
    order_id: str | None = None
    filled_qty: float = 0.0
    filled_price: float = 0.0
    error: str | None = None
    raw_response: dict = field(default_factory=dict)


@dataclass
class OrderResult:
    """Aggregated result of order intent execution"""
    intent: OrderIntent
    results: list[ExecutionResult] = field(default_factory=list)
    
    @property
    def any_success(self) -> bool:
        return any(r.success for r in self.results)
    
    @property
    def all_success(self) -> bool:
        return all(r.success for r in self.results) if self.results else False
    
    @property
    def errors(self) -> list[str]:
        return [r.error for r in self.results if r.error]


# ═══════════════════════════════════════════════════════════════════════════════
# RISK VALIDATION (P0.7)
# ═══════════════════════════════════════════════════════════════════════════════

def validate_risk(
    sl_percent: float | None,
    leverage: int | None,
    max_risk_pct: float = 30.0,
) -> tuple[bool, str | None]:
    """
    Validate that effective risk is acceptable.
    
    P0.7: effective_risk = sl_pct * leverage <= max_risk_pct
    
    Returns:
        (is_valid, error_message)
    """
    if sl_percent is None or leverage is None:
        return True, None
    
    effective_risk = sl_percent * leverage
    
    if effective_risk > max_risk_pct:
        # Option 1: Reject
        # return False, f"Effective risk {effective_risk:.1f}% exceeds limit {max_risk_pct}%. SL={sl_percent}% × Leverage={leverage}x"
        
        # Option 2: Auto-adjust SL (preferred)
        suggested_sl = max_risk_pct / leverage
        return False, f"Risk too high: SL={sl_percent}%×{leverage}x = {effective_risk:.1f}% (max {max_risk_pct}%). Suggested SL: {suggested_sl:.2f}%"
    
    return True, None


def auto_adjust_sl_for_risk(
    sl_percent: float,
    leverage: int,
    max_risk_pct: float = 30.0,
) -> float:
    """
    Auto-adjust SL to meet risk limit.
    
    Returns adjusted SL percent.
    """
    effective_risk = sl_percent * leverage
    if effective_risk <= max_risk_pct:
        return sl_percent
    
    adjusted_sl = max_risk_pct / leverage
    logger.warning(f"Auto-adjusted SL from {sl_percent}% to {adjusted_sl:.2f}% for leverage {leverage}x")
    return adjusted_sl


# ═══════════════════════════════════════════════════════════════════════════════
# SYMBOL NORMALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

def normalize_symbol(symbol: str, exchange: str) -> str:
    """
    Normalize symbol for specific exchange.
    Bybit: BTCUSDT
    HyperLiquid: BTC
    """
    if exchange == Exchange.HYPERLIQUID.value:
        # Remove USDT/USDC suffix for HL
        if symbol.endswith("USDT"):
            return symbol[:-4]
        if symbol.endswith("USDC"):
            return symbol[:-4]
    return symbol


def denormalize_symbol(symbol: str, exchange: str) -> str:
    """
    Convert exchange-specific symbol back to unified format (BTCUSDT).
    """
    if exchange == Exchange.HYPERLIQUID.value:
        if not symbol.endswith("USDT") and not symbol.endswith("USDC"):
            return f"{symbol}USDT"
    return symbol


# ═══════════════════════════════════════════════════════════════════════════════
# EXCHANGE ROUTER CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class ExchangeRouter:
    """
    Unified execution router for all exchanges.
    
    This is the ONLY class that should place orders, fetch positions, etc.
    Both bot.py and webapp/api/trading.py must use this.
    """
    
    def __init__(self, bybit_client_factory=None, hl_client_factory=None):
        """
        Args:
            bybit_client_factory: async callable(user_id, account_type) -> BybitClient
            hl_client_factory: async callable(user_id) -> HLAdapter
        """
        self._bybit_factory = bybit_client_factory
        self._hl_factory = hl_client_factory
    
    # ─────────────────────────────────────────────────────────────────────────
    # EXECUTION TARGETS
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_execution_targets(self, user_id: int, strategy: str | None = None) -> list[Target]:
        """
        Get execution targets for user.
        
        P0.1: Uses db.get_execution_targets() which now has routing_policy logic
        or falls back to legacy trading_mode logic.
        
        Returns unified Target objects with env (paper/live).
        """
        raw_targets = db.get_execution_targets(user_id, strategy)
        return [
            Target(
                exchange=t["exchange"],
                env=t.get("env") or normalize_env(t.get("account_type", "demo")),  # Use env if present, else normalize account_type
                is_enabled=t.get("is_enabled", True),
                max_positions=t.get("max_positions", 10),
                max_leverage=t.get("max_leverage", 100),
                risk_limit_pct=t.get("risk_limit_pct", 30.0),
                priority=t.get("priority", 0),
                label=t.get("label", ""),
            )
            for t in raw_targets
        ]
    
    def get_all_user_targets(self, user_id: int) -> list[Target]:
        """
        Get ALL possible targets for user, not just enabled ones.
        
        This is used by monitoring to reconcile positions across ALL targets.
        """
        return get_user_targets(user_id)
    
    # ─────────────────────────────────────────────────────────────────────────
    # ORDER EXECUTION
    # ─────────────────────────────────────────────────────────────────────────
    
    async def execute(self, intent: OrderIntent) -> OrderResult:
        """
        Execute order intent on all targets.
        
        P0.1: Orders execute ONLY on specified targets.
        P0.6: Qty is calculated per-target based on balance.
        P0.7: Risk is validated before execution.
        """
        result = OrderResult(intent=intent)
        
        # Get targets if not specified
        targets = intent.targets
        if not targets:
            targets = self.get_execution_targets(intent.user_id, intent.strategy)
        
        if not targets:
            logger.warning(f"[{intent.user_id}] No execution targets found")
            return result
        
        # Execute on each target
        for target in targets:
            if not target.is_enabled:
                continue
            
            try:
                exec_result = await self._execute_on_target(intent, target)
                result.results.append(exec_result)
                
                # If successful, save position to DB
                if exec_result.success:
                    await self._save_position(intent, target, exec_result)
                    
            except Exception as e:
                logger.error(f"[{intent.user_id}] Execution error on {target.key}: {e}")
                result.results.append(ExecutionResult(
                    target=target,
                    success=False,
                    error=str(e),
                ))
        
        return result
    
    async def _execute_on_target(self, intent: OrderIntent, target: Target) -> ExecutionResult:
        """Execute order on single target."""
        
        # P0.7: Validate risk
        if intent.sl_percent and intent.leverage:
            is_valid, error = validate_risk(
                intent.sl_percent, 
                intent.leverage, 
                target.risk_limit_pct
            )
            if not is_valid:
                # Auto-adjust SL instead of rejecting
                intent.sl_percent = auto_adjust_sl_for_risk(
                    intent.sl_percent,
                    intent.leverage,
                    target.risk_limit_pct
                )
        
        # P0.6: Calculate qty if using percent
        qty = intent.qty
        if qty is None and intent.notional_pct:
            qty = await self._calculate_qty_for_target(intent, target)
            if qty is None or qty <= 0:
                return ExecutionResult(
                    target=target,
                    success=False,
                    error="Could not calculate quantity (zero balance or invalid params)",
                )
        
        # Route to exchange
        if target.exchange == Exchange.BYBIT.value:
            return await self._execute_bybit(intent, target, qty)
        elif target.exchange == Exchange.HYPERLIQUID.value:
            return await self._execute_hyperliquid(intent, target, qty)
        else:
            return ExecutionResult(
                target=target,
                success=False,
                error=f"Unknown exchange: {target.exchange}",
            )
    
    async def _calculate_qty_for_target(
        self, 
        intent: OrderIntent, 
        target: Target,
    ) -> float | None:
        """
        P0.6: Calculate qty based on target's balance.
        
        Each target gets qty proportional to its balance,
        not a fixed qty for all targets.
        """
        try:
            # Get balance for this target
            balance_info = await self.get_balance(intent.user_id, target)
            equity = balance_info.get("equity", 0) or balance_info.get("available", 0)
            
            if equity <= 0:
                logger.warning(f"[{intent.user_id}] Zero equity on {target.key}")
                return None
            
            # Get current price
            price = await self._get_price(intent.symbol, target.exchange)
            if not price or price <= 0:
                return None
            
            # Calculate position value based on percent
            notional_value = equity * (intent.notional_pct / 100)
            
            # Apply leverage if specified
            leverage = intent.leverage or 10
            position_value = notional_value * leverage
            
            # Calculate qty
            qty = position_value / price
            
            # Get symbol info for rounding
            min_qty, qty_step = await self._get_symbol_info(intent.symbol, target.exchange)
            
            # Round to step
            if qty_step and qty_step > 0:
                qty = round(qty / qty_step) * qty_step
            
            # Check min qty
            if min_qty and qty < min_qty:
                logger.warning(f"[{intent.user_id}] Qty {qty} below min {min_qty} on {target.key}")
                return None
            
            return round(qty, 8)
            
        except Exception as e:
            logger.error(f"[{intent.user_id}] Qty calculation error: {e}")
            return None
    
    async def _get_price(self, symbol: str, exchange: str) -> float | None:
        """Get current price for symbol."""
        # This should be implemented by the caller via factory
        # For now, return None and let caller handle
        return None
    
    async def _get_symbol_info(self, symbol: str, exchange: str) -> tuple[float, float]:
        """Get min qty and qty step for symbol."""
        # Default values
        return 0.001, 0.001
    
    async def _execute_bybit(
        self, 
        intent: OrderIntent, 
        target: Target,
        qty: float,
    ) -> ExecutionResult:
        """Execute order on Bybit."""
        if not self._bybit_factory:
            return ExecutionResult(
                target=target,
                success=False,
                error="Bybit client factory not configured",
            )
        
        try:
            # This will be called from bot.py with the actual place_order function
            # For now, return placeholder
            return ExecutionResult(
                target=target,
                success=False,
                error="Bybit execution via factory not implemented - use place_order callback",
            )
        except Exception as e:
            return ExecutionResult(
                target=target,
                success=False,
                error=str(e),
            )
    
    async def _execute_hyperliquid(
        self, 
        intent: OrderIntent, 
        target: Target,
        qty: float,
    ) -> ExecutionResult:
        """Execute order on HyperLiquid."""
        try:
            # Get HL credentials
            hl_creds = db.get_hl_credentials(intent.user_id)
            private_key, is_testnet, wallet_address, vault_address = _get_hl_credentials_for_env(hl_creds, target.env)
            
            if not private_key:
                return ExecutionResult(
                    target=target,
                    success=False,
                    error=f"HyperLiquid {target.env} not configured",
                )
            
            # Create adapter with main_wallet_address for Unified Account
            adapter = HLAdapter(
                private_key=private_key,
                testnet=is_testnet,
                vault_address=wallet_address,
                main_wallet_address=wallet_address,
            )
            
            async with adapter:
                # Normalize symbol for HL
                hl_symbol = normalize_symbol(intent.symbol, Exchange.HYPERLIQUID.value)
                
                # Set leverage
                if intent.leverage:
                    try:
                        await adapter.set_leverage(hl_symbol, intent.leverage)
                    except Exception as lev_err:
                        logger.warning(f"[{intent.user_id}] HL leverage error: {lev_err}")
                
                # Place order with TP/SL (same as Bybit parity)
                result = await adapter.place_order(
                    symbol=hl_symbol,
                    side=intent.side,
                    qty=qty,
                    order_type=intent.order_type,
                    price=intent.price,
                    reduce_only=intent.reduce_only,
                    take_profit=intent.tp_price,
                    stop_loss=intent.sl_price,
                )
                
                if result.get("retCode") == 0:
                    order_data = result.get("result", {})
                    return ExecutionResult(
                        target=target,
                        success=True,
                        order_id=order_data.get("orderId"),
                        filled_qty=qty,
                        raw_response=result,
                    )
                else:
                    return ExecutionResult(
                        target=target,
                        success=False,
                        error=result.get("retMsg", "Unknown HL error"),
                        raw_response=result,
                    )
                    
        except Exception as e:
            logger.error(f"[{intent.user_id}] HL execution error: {e}")
            return ExecutionResult(
                target=target,
                success=False,
                error=str(e),
            )
    
    async def _save_position(
        self, 
        intent: OrderIntent, 
        target: Target,
        exec_result: ExecutionResult,
    ):
        """Save position to database after successful execution."""
        try:
            # Get current price if not available
            price = exec_result.filled_price or intent.price
            if not price:
                price = await self._get_price(intent.symbol, target.exchange) or 0
            
            db.add_active_position(
                user_id=intent.user_id,
                symbol=intent.symbol,
                side=intent.side,
                entry_price=price,
                size=exec_result.filled_qty or intent.qty or 0,
                timeframe=intent.timeframe,
                signal_id=intent.signal_id,
                strategy=intent.strategy,
                account_type=target.account_type,
                # P0.3: New fields
                source=intent.source,
                opened_by=intent.source,
                exchange=target.exchange,
                sl_price=intent.sl_price,
                tp_price=intent.tp_price,
                leverage=intent.leverage,
                client_order_id=intent.client_order_id,
                exchange_order_id=exec_result.order_id,
            )
            
            logger.info(f"[{intent.user_id}] Position saved: {intent.symbol} {intent.side} on {target.key}")
            
        except Exception as e:
            logger.error(f"[{intent.user_id}] Failed to save position: {e}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # BALANCE AND POSITIONS
    # ─────────────────────────────────────────────────────────────────────────
    
    async def get_balance(self, user_id: int, target: Target) -> dict:
        """Get balance for specific target."""
        if target.exchange == Exchange.HYPERLIQUID.value:
            return await self._get_hl_balance(user_id)
        else:
            # Bybit balance should be fetched via factory
            return {"equity": 0, "available": 0}
    
    async def _get_hl_balance(self, user_id: int, target: Target = None) -> dict:
        """Get HyperLiquid balance."""
        try:
            hl_creds = db.get_hl_credentials(user_id)
            env = target.env if target else "paper"
            private_key, is_testnet, wallet_address, vault_address = _get_hl_credentials_for_env(hl_creds, env)
            
            if not private_key:
                return {"equity": 0, "available": 0}
            
            adapter = HLAdapter(
                private_key=private_key,
                testnet=is_testnet,
                vault_address=vault_address,
                main_wallet_address=wallet_address,  # Query balance from main wallet
            )
            
            async with adapter:
                result = await adapter.get_balance()
                if result.get("success"):
                    return result.get("data", {})
                return {"equity": 0, "available": 0}
                
        except Exception as e:
            logger.error(f"[{user_id}] HL balance error: {e}")
            return {"equity": 0, "available": 0}
    
    async def get_positions(
        self, 
        user_id: int, 
        target: Target | None = None,
        symbol: str | None = None,
    ) -> list[dict]:
        """Get positions from exchange."""
        if target:
            if target.exchange == Exchange.HYPERLIQUID.value:
                return await self._get_hl_positions(user_id, symbol)
            # Bybit positions via factory
            return []
        
        # Get from all targets
        all_positions = []
        targets = self.get_execution_targets(user_id)
        for t in targets:
            positions = await self.get_positions(user_id, t, symbol)
            for p in positions:
                p["exchange"] = t.exchange
                p["account_type"] = t.account_type
            all_positions.extend(positions)
        
        return all_positions
    
    async def _get_hl_positions(self, user_id: int, symbol: str | None = None, target: Target = None) -> list[dict]:
        """Get HyperLiquid positions."""
        try:
            hl_creds = db.get_hl_credentials(user_id)
            env = target.env if target else "paper"
            private_key, is_testnet, wallet_address, vault_address = _get_hl_credentials_for_env(hl_creds, env)
            
            if not private_key:
                return []
            
            adapter = HLAdapter(
                private_key=private_key,
                testnet=is_testnet,
                vault_address=vault_address,
                main_wallet_address=wallet_address,  # Query positions from main wallet
            )
            
            async with adapter:
                result = await adapter.fetch_positions()
                if result.get("retCode") == 0:
                    positions = result.get("result", {}).get("list", [])
                    if symbol:
                        hl_symbol = normalize_symbol(symbol, Exchange.HYPERLIQUID.value)
                        positions = [p for p in positions if p.get("symbol") == hl_symbol]
                    return positions
                return []
                
        except Exception as e:
            logger.error(f"[{user_id}] HL positions error: {e}")
            return []
    
    # ─────────────────────────────────────────────────────────────────────────
    # CLOSE POSITION
    # ─────────────────────────────────────────────────────────────────────────
    
    async def close_position(
        self,
        user_id: int,
        symbol: str,
        target: Target | None = None,
        size: float | None = None,
        side: str | None = None,
    ) -> OrderResult:
        """Close position on target(s)."""
        intent = OrderIntent(
            user_id=user_id,
            symbol=symbol,
            side="Sell" if side == "Buy" else "Buy",  # Opposite side
            order_type="Market",
            qty=size,
            reduce_only=True,
            source="close",
        )
        
        if target:
            intent.targets = [target]
        
        result = await self.execute(intent)
        
        # Remove from DB if successful
        for r in result.results:
            if r.success:
                db.remove_active_position(user_id, symbol, r.target.account_type, exchange=r.target.exchange)
                # P0.4: Clear ATR state
                db.clear_atr_state(user_id, symbol, r.target.account_type, exchange=r.target.exchange)
        
        return result
    
    # ─────────────────────────────────────────────────────────────────────────
    # LEVERAGE
    # ─────────────────────────────────────────────────────────────────────────
    
    async def set_leverage(
        self,
        user_id: int,
        symbol: str,
        leverage: int,
        target: Target | None = None,
    ) -> bool:
        """Set leverage on target(s)."""
        targets = [target] if target else self.get_execution_targets(user_id)
        
        success = False
        for t in targets:
            try:
                if t.exchange == Exchange.HYPERLIQUID.value:
                    hl_creds = db.get_hl_credentials(user_id)
                    private_key, is_testnet, wallet_address, _ = _get_hl_credentials_for_env(hl_creds, t.env)
                    if private_key:
                        adapter = HLAdapter(
                            private_key=private_key,
                            testnet=is_testnet,
                            vault_address=wallet_address,
                            main_wallet_address=wallet_address,
                        )
                        async with adapter:
                            hl_symbol = normalize_symbol(symbol, Exchange.HYPERLIQUID.value)
                            result = await adapter.set_leverage(hl_symbol, leverage)
                            if result.get("retCode") == 0:
                                success = True
                # Bybit via factory
            except Exception as e:
                logger.error(f"[{user_id}] Set leverage error on {t.key}: {e}")
        
        return success
    
    # ─────────────────────────────────────────────────────────────────────────
    # SL/TP MANAGEMENT (P0.8)
    # ─────────────────────────────────────────────────────────────────────────
    
    async def modify_sltp(
        self,
        user_id: int,
        symbol: str,
        account_type: str = "demo",
        sl_price: float | None = None,
        tp_price: float | None = None,
        set_manual_override: bool = True,
        exchange: str = "bybit",
    ) -> bool:
        """
        Modify SL/TP for position with multitenancy support.
        
        P0.8: If set_manual_override=True, sets the flag so bot won't overwrite.
        """
        try:
            # Update on exchange (to be implemented via factory)
            # ...
            
            # Update in DB with exchange parameter
            if set_manual_override:
                db.set_manual_sltp_override(user_id, symbol, account_type, sl_price, tp_price, exchange=exchange)
            else:
                db.update_position_sltp(user_id, symbol, account_type, sl_price, tp_price, exchange=exchange)
            
            logger.info(f"[{user_id}] SL/TP modified for {symbol}: SL={sl_price}, TP={tp_price}")
            return True
            
        except Exception as e:
            logger.error(f"[{user_id}] Modify SL/TP error: {e}")
            return False


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

# Global router instance - to be configured by bot.py
_router: ExchangeRouter | None = None


def get_router() -> ExchangeRouter:
    """Get or create the global router instance."""
    global _router
    if _router is None:
        _router = ExchangeRouter()
    return _router


def configure_router(bybit_factory=None, hl_factory=None):
    """Configure the global router with client factories."""
    global _router
    _router = ExchangeRouter(
        bybit_client_factory=bybit_factory,
        hl_client_factory=hl_factory,
    )
    return _router


# ═══════════════════════════════════════════════════════════════════════════════
# BACKWARD COMPATIBILITY FUNCTIONS
# (These mirror the old exchange_router.py API for gradual migration)
# ═══════════════════════════════════════════════════════════════════════════════

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
    strategy: str = None,
    sl_percent: float = None,
    tp_percent: float = None,
    bybit_place_order_func=None,
):
    """
    Universal order placement - backward compatible wrapper.
    
    P0.2: Routes through ExchangeRouter but supports old callback pattern.
    """
    router = get_router()
    
    # Create intent
    intent = OrderIntent(
        user_id=user_id,
        symbol=symbol,
        side=side,
        order_type=orderType,
        qty=qty,
        price=price,
        leverage=leverage,
        reduce_only=reduce_only,
        strategy=strategy,
        sl_percent=sl_percent,
        tp_percent=tp_percent,
    )
    
    # Get targets based on account_type
    if account_type:
        # Single target specified
        exchange = db.get_exchange_type(user_id)
        intent.targets = [ExecutionTarget(exchange=exchange, account_type=account_type)]
    
    # For Bybit, use the callback if provided
    if bybit_place_order_func:
        targets = intent.targets or router.get_execution_targets(user_id)
        results = []
        
        for target in targets:
            if target.exchange == Exchange.BYBIT.value:
                try:
                    result = await bybit_place_order_func(
                        user_id=user_id,
                        symbol=symbol,
                        side=side,
                        orderType=orderType,
                        qty=qty,
                        price=price,
                        account_type=target.account_type,
                    )
                    results.append({"success": True, "target": target.key, "result": result})
                except Exception as e:
                    results.append({"success": False, "target": target.key, "error": str(e)})
            
            elif target.exchange == Exchange.HYPERLIQUID.value:
                exec_result = await router._execute_hyperliquid(intent, target, qty)
                results.append({
                    "success": exec_result.success,
                    "target": target.key,
                    "result": exec_result.raw_response if exec_result.success else None,
                    "error": exec_result.error,
                })
        
        # Return first successful result or last error
        for r in results:
            if r["success"]:
                return r.get("result", {})
        
        if results:
            raise ValueError(results[-1].get("error", "All executions failed"))
        return {}
    
    # Use router directly
    result = await router.execute(intent)
    if result.any_success:
        for r in result.results:
            if r.success:
                return r.raw_response
    
    if result.errors:
        raise ValueError(result.errors[0])
    
    return {}


async def fetch_positions_universal(
    user_id: int,
    symbol: str = None,
    bybit_fetch_positions_func=None,
) -> list:
    """Universal position fetching - backward compatible."""
    router = get_router()
    
    # Get from all targets
    all_positions = []
    
    targets = router.get_execution_targets(user_id)
    for target in targets:
        if target.exchange == Exchange.BYBIT.value and bybit_fetch_positions_func:
            try:
                positions = await bybit_fetch_positions_func(user_id)
                for p in positions:
                    p["exchange"] = "bybit"
                    p["account_type"] = target.account_type
                all_positions.extend(positions)
            except Exception as e:
                logger.error(f"Bybit positions error: {e}")
        
        elif target.exchange == Exchange.HYPERLIQUID.value:
            positions = await router._get_hl_positions(user_id, symbol)
            for p in positions:
                p["exchange"] = "hyperliquid"
                p["account_type"] = target.account_type
            all_positions.extend(positions)
    
    if symbol:
        all_positions = [p for p in all_positions if p.get("symbol") == symbol]
    
    return all_positions


async def set_leverage_universal(
    user_id: int,
    symbol: str,
    leverage: int = 10,
    account_type: str = None,
    bybit_set_leverage_func=None,
) -> bool:
    """Universal leverage setting - backward compatible."""
    router = get_router()
    
    targets = router.get_execution_targets(user_id)
    if account_type:
        targets = [t for t in targets if t.account_type == account_type]
    
    success = False
    for target in targets:
        if target.exchange == Exchange.BYBIT.value and bybit_set_leverage_func:
            try:
                await bybit_set_leverage_func(user_id, symbol, leverage, target.account_type)
                success = True
            except Exception as e:
                logger.error(f"Bybit leverage error: {e}")
        
        elif target.exchange == Exchange.HYPERLIQUID.value:
            result = await router.set_leverage(user_id, symbol, leverage, target)
            if result:
                success = True
    
    return success


async def close_position_universal(
    user_id: int,
    symbol: str,
    size: float,
    side: str,
    account_type: str = None,
    bybit_place_order_func=None,
):
    """Universal position closing - backward compatible."""
    router = get_router()
    close_side = "Sell" if side == "Buy" else "Buy"
    
    targets = router.get_execution_targets(user_id)
    if account_type:
        targets = [t for t in targets if t.account_type == account_type]
    
    for target in targets:
        if target.exchange == Exchange.BYBIT.value and bybit_place_order_func:
            try:
                await bybit_place_order_func(
                    user_id=user_id,
                    symbol=symbol,
                    side=close_side,
                    orderType="Market",
                    qty=size,
                    account_type=target.account_type,
                )
                db.remove_active_position(user_id, symbol, target.account_type, exchange=target.exchange)
                db.clear_atr_state(user_id, symbol, target.account_type, exchange=target.exchange)
            except Exception as e:
                logger.error(f"Bybit close error: {e}")
        
        elif target.exchange == Exchange.HYPERLIQUID.value:
            await router.close_position(user_id, symbol, target, size, side)


async def get_balance_universal(user_id: int, bybit_get_balance_func=None) -> dict:
    """Universal balance fetching - backward compatible."""
    router = get_router()
    
    targets = router.get_execution_targets(user_id)
    
    # Return first available balance
    for target in targets:
        if target.exchange == Exchange.BYBIT.value and bybit_get_balance_func:
            try:
                return await bybit_get_balance_func(user_id)
            except Exception:
                continue
        
        elif target.exchange == Exchange.HYPERLIQUID.value:
            balance = await router._get_hl_balance(user_id)
            if balance.get("equity", 0) > 0:
                return balance
    
    return {"equity": 0, "available": 0, "margin_used": 0, "unrealized_pnl": 0}


# Keep old utility functions for compatibility
def normalize_symbol_for_hl(symbol: str) -> str:
    return normalize_symbol(symbol, Exchange.HYPERLIQUID.value)

def convert_side_for_hl(side: str) -> str:
    return side.upper()

def convert_order_type_for_hl(order_type: str) -> str:
    return order_type.upper()
