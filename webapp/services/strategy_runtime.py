"""
Strategy Runtime Orchestrator
Runs custom strategies in live trading mode via WebApp (not bot)

Features:
- Start/stop/pause strategies per user
- Real-time signal generation
- Order execution via exchange APIs
- Position tracking
- Daily limits enforcement
- WebSocket updates
"""
import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import aiohttp

# Setup logging
logger = logging.getLogger(__name__)

# Import database functions
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import db
from models.strategy_spec import StrategySpec
from webapp.services.backtest_engine import CustomStrategyAnalyzer


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

RUNTIME_CONFIG = {
    "update_interval_seconds": 60,      # Check strategies every 60s
    "price_cache_ttl": 5,               # Price cache TTL in seconds
    "max_strategies_per_user": 10,      # Max concurrent strategies
    "daily_reset_hour_utc": 0,          # When to reset daily counters
}

# Price cache
_price_cache: Dict[str, tuple] = {}  # symbol -> (price, timestamp)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RunningStrategy:
    """State for a running strategy"""
    user_id: int
    strategy_id: int
    spec: StrategySpec
    exchange: str
    account_type: str
    analyzer: CustomStrategyAnalyzer
    
    # Runtime state
    is_paused: bool = False
    last_check: Optional[datetime] = None
    last_signal: Optional[Dict] = None
    
    # Positions managed by this strategy
    open_positions: List[Dict] = field(default_factory=list)
    pending_orders: List[Dict] = field(default_factory=list)
    
    # Session stats
    session_trades: int = 0
    session_pnl: float = 0.0
    
    # Daily limits
    daily_trades: int = 0
    daily_pnl: float = 0.0
    daily_reset_at: Optional[datetime] = None


# ═══════════════════════════════════════════════════════════════════════════════
# RUNTIME ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════

class StrategyRuntimeOrchestrator:
    """
    Manages live execution of custom strategies.
    
    Usage:
        orchestrator = StrategyRuntimeOrchestrator()
        await orchestrator.start()
        
        # Start a strategy
        await orchestrator.start_strategy(user_id=123, strategy_id=1, exchange="bybit", account_type="demo")
        
        # Stop
        await orchestrator.stop_strategy(user_id=123, strategy_id=1)
        
        # Shutdown
        await orchestrator.stop()
    """
    
    def __init__(self):
        self._running: bool = False
        self._strategies: Dict[str, RunningStrategy] = {}  # key = "user_id:strategy_id:exchange:account_type"
        self._task: Optional[asyncio.Task] = None
        self._subscribers: Dict[str, List] = {}  # WebSocket subscribers
        self._http_session: Optional[aiohttp.ClientSession] = None
    
    @staticmethod
    def _make_key(user_id: int, strategy_id: int, exchange: str, account_type: str) -> str:
        return f"{user_id}:{strategy_id}:{exchange}:{account_type}"
    
    async def start(self):
        """Start the orchestrator background loop"""
        if self._running:
            return
        
        self._running = True
        self._http_session = aiohttp.ClientSession()
        
        # Load all running strategies from database
        await self._load_running_strategies()
        
        # Start background loop
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Strategy Runtime Orchestrator started")
    
    async def stop(self):
        """Stop the orchestrator"""
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        if self._http_session:
            await self._http_session.close()
        
        self._strategies.clear()
        logger.info("Strategy Runtime Orchestrator stopped")
    
    async def _load_running_strategies(self):
        """Load all running strategies from database"""
        try:
            running = db.get_all_running_strategies()
            
            for row in running:
                try:
                    config = json.loads(row.get("config_json", "{}"))
                    spec = StrategySpec.from_dict(config)
                    analyzer = CustomStrategyAnalyzer(config)
                    
                    key = self._make_key(
                        row["user_id"],
                        row["strategy_id"],
                        row.get("exchange", "bybit"),
                        row.get("account_type", "demo")
                    )
                    
                    self._strategies[key] = RunningStrategy(
                        user_id=row["user_id"],
                        strategy_id=row["strategy_id"],
                        spec=spec,
                        exchange=row.get("exchange", "bybit"),
                        account_type=row.get("account_type", "demo"),
                        analyzer=analyzer,
                        is_paused=bool(row.get("is_paused", 0)),
                        session_trades=row.get("session_trades", 0),
                        session_pnl=row.get("session_pnl", 0),
                        daily_trades=row.get("daily_trades", 0),
                        daily_pnl=row.get("daily_pnl", 0),
                    )
                    
                    # Parse positions
                    if row.get("open_positions"):
                        try:
                            self._strategies[key].open_positions = json.loads(row["open_positions"])
                        except:
                            pass
                    
                    logger.info(f"Loaded running strategy: {key}")
                    
                except Exception as e:
                    logger.error(f"Failed to load strategy {row.get('strategy_id')}: {e}")
            
            logger.info(f"Loaded {len(self._strategies)} running strategies")
            
        except Exception as e:
            logger.error(f"Failed to load running strategies: {e}")
    
    async def start_strategy(
        self,
        user_id: int,
        strategy_id: int,
        exchange: str = "bybit",
        account_type: str = "demo"
    ) -> Dict[str, Any]:
        """Start a strategy in live trading mode"""
        key = self._make_key(user_id, strategy_id, exchange, account_type)
        
        # Check if already running
        if key in self._strategies:
            return {"success": False, "error": "Strategy already running"}
        
        # Check max strategies limit
        user_strategies = sum(1 for s in self._strategies.values() if s.user_id == user_id)
        if user_strategies >= RUNTIME_CONFIG["max_strategies_per_user"]:
            return {"success": False, "error": f"Maximum {RUNTIME_CONFIG['max_strategies_per_user']} strategies per user"}
        
        # Load strategy from database
        strategy_data = db.get_strategy_by_id(strategy_id)
        if not strategy_data:
            return {"success": False, "error": "Strategy not found"}
        
        # Check ownership or purchase
        if strategy_data["user_id"] != user_id:
            purchases = db.get_user_purchases(user_id)
            if not any(p["strategy_id"] == strategy_id for p in purchases):
                return {"success": False, "error": "No access to this strategy"}
        
        try:
            # Parse config
            config_json = strategy_data.get("config") or strategy_data.get("config_json", "{}")
            config = json.loads(config_json) if isinstance(config_json, str) else config_json
            
            # Validate
            spec = StrategySpec.from_dict(config)
            is_valid, errors = spec.validate()
            if not is_valid:
                return {"success": False, "error": f"Invalid strategy: {', '.join(errors)}"}
            
            # Create analyzer
            analyzer = CustomStrategyAnalyzer(config)
            
            # Create running strategy
            running = RunningStrategy(
                user_id=user_id,
                strategy_id=strategy_id,
                spec=spec,
                exchange=exchange,
                account_type=account_type,
                analyzer=analyzer,
            )
            
            # Save to database
            db.start_strategy_live(user_id, strategy_id, exchange, account_type)
            
            # Add to active strategies
            self._strategies[key] = running
            
            logger.info(f"Started strategy: {key}")
            
            return {
                "success": True,
                "key": key,
                "strategy_name": spec.name,
                "exchange": exchange,
                "account_type": account_type
            }
            
        except Exception as e:
            logger.error(f"Failed to start strategy: {e}")
            return {"success": False, "error": str(e)}
    
    async def stop_strategy(
        self,
        user_id: int,
        strategy_id: int,
        exchange: str = "bybit",
        account_type: str = "demo",
        close_positions: bool = False
    ) -> Dict[str, Any]:
        """Stop a running strategy"""
        key = self._make_key(user_id, strategy_id, exchange, account_type)
        
        if key not in self._strategies:
            return {"success": False, "error": "Strategy not running"}
        
        running = self._strategies[key]
        
        # Optionally close open positions
        if close_positions and running.open_positions:
            for pos in running.open_positions:
                try:
                    await self._close_position(running, pos)
                except Exception as e:
                    logger.error(f"Failed to close position {pos}: {e}")
        
        # Update database
        db.stop_strategy_live(user_id, strategy_id, exchange, account_type)
        
        # Remove from active strategies
        del self._strategies[key]
        
        logger.info(f"Stopped strategy: {key}")
        
        return {
            "success": True,
            "key": key,
            "positions_closed": len(running.open_positions) if close_positions else 0
        }
    
    async def pause_strategy(
        self,
        user_id: int,
        strategy_id: int,
        exchange: str = "bybit",
        account_type: str = "demo"
    ) -> Dict[str, Any]:
        """Pause a running strategy (keeps positions, stops new signals)"""
        key = self._make_key(user_id, strategy_id, exchange, account_type)
        
        if key not in self._strategies:
            return {"success": False, "error": "Strategy not running"}
        
        self._strategies[key].is_paused = True
        db.pause_strategy_live(user_id, strategy_id, exchange, account_type)
        
        return {"success": True, "key": key, "status": "paused"}
    
    async def resume_strategy(
        self,
        user_id: int,
        strategy_id: int,
        exchange: str = "bybit",
        account_type: str = "demo"
    ) -> Dict[str, Any]:
        """Resume a paused strategy"""
        key = self._make_key(user_id, strategy_id, exchange, account_type)
        
        if key not in self._strategies:
            return {"success": False, "error": "Strategy not running"}
        
        self._strategies[key].is_paused = False
        db.resume_strategy_live(user_id, strategy_id, exchange, account_type)
        
        return {"success": True, "key": key, "status": "running"}
    
    def get_strategy_status(
        self,
        user_id: int,
        strategy_id: int,
        exchange: str = "bybit",
        account_type: str = "demo"
    ) -> Dict[str, Any]:
        """Get current status of a strategy"""
        key = self._make_key(user_id, strategy_id, exchange, account_type)
        
        if key not in self._strategies:
            # Check database for stopped state
            state = db.get_strategy_live_state(user_id, strategy_id, exchange, account_type)
            if state:
                return {
                    "status": "stopped",
                    "total_trades": state.get("total_trades", 0),
                    "total_pnl": state.get("total_pnl", 0),
                    "win_rate": state.get("win_rate", 0),
                }
            return {"status": "never_started"}
        
        running = self._strategies[key]
        
        return {
            "status": "paused" if running.is_paused else "running",
            "strategy_name": running.spec.name,
            "exchange": running.exchange,
            "account_type": running.account_type,
            "open_positions": len(running.open_positions),
            "pending_orders": len(running.pending_orders),
            "session_trades": running.session_trades,
            "session_pnl": running.session_pnl,
            "daily_trades": running.daily_trades,
            "daily_pnl": running.daily_pnl,
            "last_check": running.last_check.isoformat() if running.last_check else None,
            "last_signal": running.last_signal,
        }
    
    def get_user_running_strategies(self, user_id: int) -> List[Dict]:
        """Get all running strategies for a user"""
        return [
            {
                "strategy_id": s.strategy_id,
                "strategy_name": s.spec.name,
                "exchange": s.exchange,
                "account_type": s.account_type,
                "status": "paused" if s.is_paused else "running",
                "open_positions": len(s.open_positions),
                "session_pnl": s.session_pnl,
            }
            for s in self._strategies.values()
            if s.user_id == user_id
        ]
    
    async def _run_loop(self):
        """Main background loop - check all strategies periodically"""
        logger.info("Strategy Runtime loop started")
        
        while self._running:
            try:
                await self._check_all_strategies()
                await asyncio.sleep(RUNTIME_CONFIG["update_interval_seconds"])
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in runtime loop: {e}")
                await asyncio.sleep(5)
        
        logger.info("Strategy Runtime loop ended")
    
    async def _check_all_strategies(self):
        """Check all running strategies for signals"""
        for key, running in list(self._strategies.items()):
            if running.is_paused:
                continue
            
            try:
                await self._check_strategy(running)
            except Exception as e:
                logger.error(f"Error checking strategy {key}: {e}")
    
    async def _check_strategy(self, running: RunningStrategy):
        """Check a single strategy for signals"""
        now = datetime.utcnow()
        running.last_check = now
        
        # Check daily reset
        await self._check_daily_reset(running)
        
        # Check daily limits
        if not self._check_limits(running):
            return
        
        # Get symbols to check
        symbols = running.spec.filters.required_symbols or ["BTCUSDT", "ETHUSDT"]
        
        for symbol in symbols:
            try:
                # Fetch recent candles
                candles = await self._fetch_candles(
                    symbol,
                    running.spec.primary_timeframe,
                    limit=100
                )
                
                if not candles or len(candles) < 50:
                    continue
                
                # Analyze for signals
                signals = running.analyzer.analyze(candles)
                
                # Check last candle for signal
                last_idx = len(candles) - 1
                if last_idx in signals:
                    signal = signals[last_idx]
                    running.last_signal = {
                        "symbol": symbol,
                        "direction": signal.get("direction"),
                        "time": now.isoformat(),
                        "price": candles[-1]["close"]
                    }
                    
                    # Check if we should trade
                    if await self._should_open_position(running, symbol, signal):
                        await self._open_position(running, symbol, signal, candles[-1]["close"])
                
                # Check existing positions for exit
                for pos in list(running.open_positions):
                    if pos["symbol"] == symbol:
                        await self._check_position_exit(running, pos, candles[-1], signals.get(last_idx))
                        
            except Exception as e:
                logger.error(f"Error checking {symbol} for strategy {running.strategy_id}: {e}")
        
        # Update database state
        self._update_db_state(running)
    
    async def _check_daily_reset(self, running: RunningStrategy):
        """Reset daily counters if new day"""
        now = datetime.utcnow()
        reset_hour = RUNTIME_CONFIG["daily_reset_hour_utc"]
        
        if running.daily_reset_at is None:
            running.daily_reset_at = now.replace(hour=reset_hour, minute=0, second=0, microsecond=0)
        
        # Check if we passed the reset time
        if now >= running.daily_reset_at + timedelta(days=1):
            running.daily_trades = 0
            running.daily_pnl = 0.0
            running.daily_reset_at = now.replace(hour=reset_hour, minute=0, second=0, microsecond=0)
            logger.info(f"Daily reset for strategy {running.strategy_id}")
    
    def _check_limits(self, running: RunningStrategy) -> bool:
        """Check if strategy is within limits"""
        spec = running.spec
        
        # Max daily trades
        if running.daily_trades >= spec.risk.max_daily_trades:
            logger.debug(f"Strategy {running.strategy_id}: daily trade limit reached")
            return False
        
        # Max daily loss
        if running.daily_pnl <= -spec.risk.max_daily_loss_percent:
            logger.debug(f"Strategy {running.strategy_id}: daily loss limit reached")
            return False
        
        # Max positions
        if len(running.open_positions) >= spec.risk.max_positions:
            logger.debug(f"Strategy {running.strategy_id}: max positions reached")
            return False
        
        return True
    
    async def _should_open_position(self, running: RunningStrategy, symbol: str, signal: Dict) -> bool:
        """Check if we should open a position based on signal"""
        spec = running.spec
        
        # Check if we already have position for this symbol
        if spec.only_one_position_per_symbol:
            if any(p["symbol"] == symbol for p in running.open_positions):
                return False
        
        # Check pyramiding limit
        same_direction = sum(
            1 for p in running.open_positions
            if p["symbol"] == symbol and p["side"].upper() == signal.get("direction", "").upper()
        )
        if same_direction >= spec.pyramiding:
            return False
        
        return True
    
    async def _open_position(self, running: RunningStrategy, symbol: str, signal: Dict, price: float):
        """Open a new position"""
        try:
            spec = running.spec
            direction = signal.get("direction", "LONG")
            
            # Calculate position size
            # For demo, we use a mock balance
            balance = await self._get_balance(running.user_id, running.exchange, running.account_type)
            position_value = balance * (spec.risk.position_size_percent / 100)
            
            # Get TP/SL from exit rules
            tp_pct, sl_pct = spec.get_tp_sl_percent()
            tp_pct = tp_pct or 4.0
            sl_pct = sl_pct or 2.0
            
            if direction == "LONG":
                tp_price = price * (1 + tp_pct / 100)
                sl_price = price * (1 - sl_pct / 100)
            else:
                tp_price = price * (1 - tp_pct / 100)
                sl_price = price * (1 + sl_pct / 100)
            
            # Place order (mock for now, real implementation would call exchange API)
            order_result = await self._place_order(
                user_id=running.user_id,
                exchange=running.exchange,
                account_type=running.account_type,
                symbol=symbol,
                side=direction,
                size=position_value / price,  # Convert to quantity
                price=price,
                leverage=spec.risk.leverage,
                tp_price=tp_price,
                sl_price=sl_price
            )
            
            if order_result.get("success"):
                position = {
                    "symbol": symbol,
                    "side": direction,
                    "entry_price": price,
                    "size": position_value / price,
                    "value": position_value,
                    "tp_price": tp_price,
                    "sl_price": sl_price,
                    "opened_at": datetime.utcnow().isoformat(),
                    "order_id": order_result.get("order_id")
                }
                running.open_positions.append(position)
                
                logger.info(f"Opened {direction} position for {symbol} @ {price}")
                
                # Broadcast to WebSocket subscribers
                await self._broadcast_update(running, "position_opened", position)
                
        except Exception as e:
            logger.error(f"Failed to open position: {e}")
    
    async def _check_position_exit(self, running: RunningStrategy, pos: Dict, candle: Dict, signal: Optional[Dict]):
        """Check if position should be closed"""
        symbol = pos["symbol"]
        side = pos["side"]
        entry = pos["entry_price"]
        tp = pos.get("tp_price")
        sl = pos.get("sl_price")
        
        close_reason = None
        exit_price = candle["close"]
        
        if side.upper() == "LONG":
            if tp and candle["high"] >= tp:
                close_reason = "TP"
                exit_price = tp
            elif sl and candle["low"] <= sl:
                close_reason = "SL"
                exit_price = sl
            elif signal and signal.get("direction") == "SHORT" and running.spec.allow_reverse:
                close_reason = "SIGNAL_REVERSE"
        else:  # SHORT
            if tp and candle["low"] <= tp:
                close_reason = "TP"
                exit_price = tp
            elif sl and candle["high"] >= sl:
                close_reason = "SL"
                exit_price = sl
            elif signal and signal.get("direction") == "LONG" and running.spec.allow_reverse:
                close_reason = "SIGNAL_REVERSE"
        
        if close_reason:
            await self._close_position(running, pos, exit_price, close_reason)
    
    async def _close_position(self, running: RunningStrategy, pos: Dict, exit_price: float = None, reason: str = "MANUAL"):
        """Close a position"""
        try:
            if exit_price is None:
                exit_price = await self._get_price(pos["symbol"])
            
            # Calculate PnL
            entry = pos["entry_price"]
            size = pos.get("value", pos.get("size", 0) * entry)
            
            if pos["side"].upper() == "LONG":
                pnl_pct = (exit_price - entry) / entry * 100
            else:
                pnl_pct = (entry - exit_price) / entry * 100
            
            pnl = size * (pnl_pct / 100)
            is_win = pnl > 0
            
            # Place close order
            close_result = await self._place_order(
                user_id=running.user_id,
                exchange=running.exchange,
                account_type=running.account_type,
                symbol=pos["symbol"],
                side="SHORT" if pos["side"].upper() == "LONG" else "LONG",
                size=pos.get("size", size / exit_price),
                price=exit_price,
                reduce_only=True
            )
            
            if close_result.get("success") or True:  # Always update local state
                # Update stats
                running.session_trades += 1
                running.session_pnl += pnl
                running.daily_trades += 1
                running.daily_pnl += pnl
                
                # Remove from open positions
                running.open_positions = [p for p in running.open_positions if p != pos]
                
                # Record in database
                db.record_strategy_trade(
                    running.user_id,
                    running.strategy_id,
                    pnl,
                    is_win,
                    running.exchange,
                    running.account_type
                )
                
                logger.info(f"Closed {pos['symbol']} {pos['side']} @ {exit_price}, PnL: {pnl:.2f} ({reason})")
                
                # Broadcast
                await self._broadcast_update(running, "position_closed", {
                    **pos,
                    "exit_price": exit_price,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                    "reason": reason
                })
                
        except Exception as e:
            logger.error(f"Failed to close position: {e}")
    
    async def _fetch_candles(self, symbol: str, timeframe: str, limit: int = 100) -> List[Dict]:
        """Fetch OHLCV candles from Binance"""
        try:
            tf_map = {"1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m", "1h": "1h", "4h": "4h", "1d": "1d"}
            interval = tf_map.get(timeframe, "1h")
            
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
            
            async with self._http_session.get(url) as resp:
                if resp.status != 200:
                    return []
                
                data = await resp.json()
                
                return [
                    {
                        "time": datetime.fromtimestamp(k[0] / 1000).isoformat(),
                        "open": float(k[1]),
                        "high": float(k[2]),
                        "low": float(k[3]),
                        "close": float(k[4]),
                        "volume": float(k[5])
                    }
                    for k in data
                ]
                
        except Exception as e:
            logger.error(f"Failed to fetch candles for {symbol}: {e}")
            return []
    
    async def _get_price(self, symbol: str) -> float:
        """Get current price for symbol"""
        cache_key = symbol
        now = time.time()
        
        # Check cache
        if cache_key in _price_cache:
            cached_price, cached_time = _price_cache[cache_key]
            if now - cached_time < RUNTIME_CONFIG["price_cache_ttl"]:
                return cached_price
        
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            async with self._http_session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    price = float(data["price"])
                    _price_cache[cache_key] = (price, now)
                    return price
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
        
        # Return cached price even if stale
        if cache_key in _price_cache:
            return _price_cache[cache_key][0]
        
        return 0.0
    
    async def _get_balance(self, user_id: int, exchange: str, account_type: str) -> float:
        """Get account balance"""
        # For now, return mock balance
        # Real implementation would call exchange API via bot_unified
        return 10000.0  # $10,000 mock balance
    
    async def _place_order(
        self,
        user_id: int,
        exchange: str,
        account_type: str,
        symbol: str,
        side: str,
        size: float,
        price: float,
        leverage: int = 10,
        tp_price: float = None,
        sl_price: float = None,
        reduce_only: bool = False
    ) -> Dict[str, Any]:
        """Place order via exchange API"""
        # For now, return mock success
        # Real implementation would call bot_unified.place_order_unified()
        
        logger.info(f"[MOCK ORDER] {side} {symbol} size={size:.6f} @ {price:.2f}")
        
        return {
            "success": True,
            "order_id": f"mock_{int(time.time())}",
            "symbol": symbol,
            "side": side,
            "size": size,
            "price": price
        }
    
    def _update_db_state(self, running: RunningStrategy):
        """Update strategy state in database"""
        try:
            db.update_strategy_live_state(
                running.user_id,
                running.strategy_id,
                running.exchange,
                running.account_type,
                open_positions=running.open_positions,
                pending_orders=running.pending_orders,
                session_pnl=running.session_pnl,
                session_trades=running.session_trades,
                daily_trades=running.daily_trades,
                daily_pnl=running.daily_pnl,
                last_signal_at=int(time.time()) if running.last_signal else None
            )
        except Exception as e:
            logger.error(f"Failed to update strategy state: {e}")
    
    async def _broadcast_update(self, running: RunningStrategy, event_type: str, data: Dict):
        """Broadcast update to WebSocket subscribers"""
        # This would integrate with WebSocket handler
        key = self._make_key(running.user_id, running.strategy_id, running.exchange, running.account_type)
        
        message = {
            "type": event_type,
            "strategy_id": running.strategy_id,
            "strategy_name": running.spec.name,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # TODO: Integrate with WebSocket broadcast
        logger.debug(f"Broadcast: {event_type} for {key}")


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_orchestrator: Optional[StrategyRuntimeOrchestrator] = None


def get_orchestrator() -> StrategyRuntimeOrchestrator:
    """Get the singleton orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = StrategyRuntimeOrchestrator()
    return _orchestrator


async def start_runtime():
    """Start the runtime orchestrator"""
    orchestrator = get_orchestrator()
    await orchestrator.start()


async def stop_runtime():
    """Stop the runtime orchestrator"""
    orchestrator = get_orchestrator()
    await orchestrator.stop()
