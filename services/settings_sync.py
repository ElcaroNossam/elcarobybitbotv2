"""
Settings Sync Service - Real-time settings synchronization between bot and webapp
Handles dynamic exchange switching, credential changes, strategy updates
"""
import asyncio
import logging
import json
from typing import Dict, Set, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SettingChangeType(Enum):
    """Types of setting changes that trigger actions"""
    EXCHANGE_SWITCH = "exchange_switch"
    API_CREDENTIALS = "api_credentials"
    TRADING_MODE = "trading_mode"
    STRATEGY_TOGGLE = "strategy_toggle"
    STRATEGY_PARAMS = "strategy_params"
    RISK_SETTINGS = "risk_settings"
    DEPLOYED_STRATEGY = "deployed_strategy"


@dataclass
class SettingChange:
    """Represents a setting change event"""
    user_id: int
    change_type: SettingChangeType
    old_value: Any
    new_value: Any
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


class SettingsSyncManager:
    """
    Central manager for settings synchronization.
    Notifies subscribers when settings change and handles reconnection logic.
    """
    
    def __init__(self):
        self._subscribers: Dict[SettingChangeType, Set[Callable]] = {t: set() for t in SettingChangeType}
        self._user_sessions: Dict[int, Dict] = {}  # user_id -> active session info
        self._pending_reconnects: Dict[int, asyncio.Task] = {}
        self._change_history: Dict[int, list] = {}  # user_id -> recent changes
        self._lock = asyncio.Lock()
    
    def subscribe(self, change_type: SettingChangeType, callback: Callable):
        """Subscribe to specific setting change type"""
        self._subscribers[change_type].add(callback)
        logger.debug(f"Subscribed to {change_type.value}: {callback.__name__}")
    
    def unsubscribe(self, change_type: SettingChangeType, callback: Callable):
        """Unsubscribe from setting change type"""
        self._subscribers[change_type].discard(callback)
    
    async def notify_change(self, change: SettingChange):
        """Notify all subscribers of a setting change"""
        async with self._lock:
            # Store in history
            if change.user_id not in self._change_history:
                self._change_history[change.user_id] = []
            self._change_history[change.user_id].append(change)
            # Keep only last 50 changes per user
            self._change_history[change.user_id] = self._change_history[change.user_id][-50:]
        
        # Notify subscribers
        for callback in self._subscribers[change.change_type]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(change)
                else:
                    callback(change)
            except Exception as e:
                logger.error(f"Error in setting change handler {callback.__name__}: {e}")
        
        logger.info(f"Setting change notified: user={change.user_id}, type={change.change_type.value}")
    
    async def on_exchange_switch(self, user_id: int, old_exchange: str, new_exchange: str, credentials: Dict):
        """Handle exchange switch with proper reconnection"""
        change = SettingChange(
            user_id=user_id,
            change_type=SettingChangeType.EXCHANGE_SWITCH,
            old_value=old_exchange,
            new_value=new_exchange,
            metadata={"has_credentials": bool(credentials)}
        )
        
        # Cancel any pending reconnect for this user
        if user_id in self._pending_reconnects:
            self._pending_reconnects[user_id].cancel()
        
        # Update user session
        self._user_sessions[user_id] = {
            "exchange": new_exchange,
            "connected": False,
            "last_switch": datetime.now()
        }
        
        await self.notify_change(change)
        
        # Schedule reconnection
        self._pending_reconnects[user_id] = asyncio.create_task(
            self._reconnect_exchange(user_id, new_exchange, credentials)
        )
    
    async def _reconnect_exchange(self, user_id: int, exchange: str, credentials: Dict):
        """Reconnect to new exchange with retry logic"""
        from core import get_cached_client, on_credentials_changed
        
        # Invalidate old connections
        on_credentials_changed(user_id)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await asyncio.sleep(0.5 * (attempt + 1))  # Backoff
                
                # Test new connection
                async with await get_cached_client(user_id) as client:
                    balance = await client.get_balance()
                    
                    self._user_sessions[user_id]["connected"] = True
                    self._user_sessions[user_id]["balance"] = balance
                    
                    logger.info(f"User {user_id} reconnected to {exchange}")
                    
                    # Notify success
                    await self.notify_change(SettingChange(
                        user_id=user_id,
                        change_type=SettingChangeType.EXCHANGE_SWITCH,
                        old_value=None,
                        new_value={"status": "connected", "exchange": exchange},
                        metadata={"balance": balance}
                    ))
                    return True
                    
            except Exception as e:
                logger.warning(f"Reconnect attempt {attempt + 1} failed for user {user_id}: {e}")
        
        logger.error(f"Failed to reconnect user {user_id} to {exchange} after {max_retries} attempts")
        return False
    
    async def on_credentials_update(self, user_id: int, exchange: str, account_type: str = None):
        """Handle API credential update"""
        from core import on_credentials_changed
        
        # Invalidate cached connections
        on_credentials_changed(user_id)
        
        change = SettingChange(
            user_id=user_id,
            change_type=SettingChangeType.API_CREDENTIALS,
            old_value=None,
            new_value={"exchange": exchange, "account_type": account_type}
        )
        
        await self.notify_change(change)
        
        # Test new credentials
        return await self._reconnect_exchange(user_id, exchange, {})
    
    async def on_strategy_deployed(self, user_id: int, strategy: str, params: Dict, backtest_results: Dict):
        """Handle strategy deployment from backtest to live"""
        change = SettingChange(
            user_id=user_id,
            change_type=SettingChangeType.DEPLOYED_STRATEGY,
            old_value=None,
            new_value={
                "strategy": strategy,
                "params": params,
                "backtest_results": backtest_results
            }
        )
        
        await self.notify_change(change)
    
    def get_user_session(self, user_id: int) -> Optional[Dict]:
        """Get current session info for user"""
        return self._user_sessions.get(user_id)
    
    def get_recent_changes(self, user_id: int, limit: int = 10) -> list:
        """Get recent setting changes for user"""
        changes = self._change_history.get(user_id, [])
        return changes[-limit:]


# Global instance
settings_sync = SettingsSyncManager()


# ============================================================================
# STRATEGY DEPLOYMENT SYSTEM
# ============================================================================

@dataclass
class StrategyDeployment:
    """Deployed strategy configuration"""
    user_id: int
    strategy_name: str
    params: Dict
    deployed_at: datetime
    backtest_results: Dict
    is_active: bool = True
    live_results: Dict = field(default_factory=dict)


class StrategyDeploymentManager:
    """Manages strategy deployments from backtest to live trading"""
    
    def __init__(self):
        self._deployments: Dict[int, Dict[str, StrategyDeployment]] = {}  # user_id -> {strategy -> deployment}
    
    async def deploy_strategy(
        self,
        user_id: int,
        strategy: str,
        params: Dict,
        backtest_results: Dict,
        min_win_rate: float = 50.0,
        min_profit_factor: float = 1.2
    ) -> Dict:
        """
        Deploy a strategy to live trading after backtest validation.
        
        Args:
            user_id: User ID
            strategy: Strategy name
            params: Optimized parameters
            backtest_results: Results from backtesting
            min_win_rate: Minimum required win rate (%)
            min_profit_factor: Minimum required profit factor
        
        Returns:
            Deployment status dict
        """
        import db
        
        # Validate backtest results
        win_rate = backtest_results.get("win_rate", 0)
        profit_factor = backtest_results.get("profit_factor", 0)
        
        if win_rate < min_win_rate:
            return {
                "success": False,
                "error": f"Win rate {win_rate:.1f}% below minimum {min_win_rate}%"
            }
        
        if profit_factor < min_profit_factor:
            return {
                "success": False,
                "error": f"Profit factor {profit_factor:.2f} below minimum {min_profit_factor}"
            }
        
        # Create deployment
        deployment = StrategyDeployment(
            user_id=user_id,
            strategy_name=strategy,
            params=params,
            deployed_at=datetime.now(),
            backtest_results=backtest_results,
            is_active=True
        )
        
        # Store deployment
        if user_id not in self._deployments:
            self._deployments[user_id] = {}
        self._deployments[user_id][strategy] = deployment
        
        # Apply parameters to user settings
        await self._apply_strategy_params(user_id, strategy, params)
        
        # Enable the strategy
        strategy_field = f"trade_{strategy}"
        db.set_user_field(user_id, strategy_field, 1)
        
        # Save to database
        self._save_deployment_to_db(deployment)
        
        # Notify sync manager
        await settings_sync.on_strategy_deployed(user_id, strategy, params, backtest_results)
        
        logger.info(f"Strategy {strategy} deployed for user {user_id} with params: {params}")
        
        return {
            "success": True,
            "deployment": {
                "strategy": strategy,
                "params": params,
                "win_rate": win_rate,
                "profit_factor": profit_factor,
                "deployed_at": deployment.deployed_at.isoformat()
            }
        }
    
    async def _apply_strategy_params(self, user_id: int, strategy: str, params: Dict):
        """Apply strategy parameters to user settings"""
        import db
        
        # Get current strategy settings
        current = db.get_user_field(user_id, "strategy_settings")
        if current:
            try:
                settings = json.loads(current)
            except:
                settings = {}
        else:
            settings = {}
        
        # Update with new params
        settings[strategy] = params
        
        # Save back
        db.set_user_field(user_id, "strategy_settings", json.dumps(settings))
        
        # Apply global params (TP/SL/Leverage)
        if "stop_loss_percent" in params:
            db.set_user_field(user_id, "sl_percent", params["stop_loss_percent"])
        if "take_profit_percent" in params:
            db.set_user_field(user_id, "tp_percent", params["take_profit_percent"])
        if "leverage" in params:
            db.set_user_field(user_id, "leverage", params["leverage"])
    
    def _save_deployment_to_db(self, deployment: StrategyDeployment):
        """Save deployment to database"""
        import db
        
        conn = db.get_conn()
        try:
            conn.execute("""
                INSERT OR REPLACE INTO strategy_deployments 
                (user_id, strategy, params, backtest_results, deployed_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                deployment.user_id,
                deployment.strategy_name,
                json.dumps(deployment.params),
                json.dumps(deployment.backtest_results),
                deployment.deployed_at.isoformat(),
                1 if deployment.is_active else 0
            ))
        finally:
            db.release_conn(conn)
    
    def get_active_deployment(self, user_id: int, strategy: str) -> Optional[StrategyDeployment]:
        """Get active deployment for user/strategy"""
        if user_id in self._deployments:
            return self._deployments[user_id].get(strategy)
        return None
    
    def get_all_deployments(self, user_id: int) -> Dict[str, StrategyDeployment]:
        """Get all deployments for user"""
        return self._deployments.get(user_id, {})
    
    async def deactivate_deployment(self, user_id: int, strategy: str) -> bool:
        """Deactivate a deployment"""
        import db
        
        if user_id in self._deployments and strategy in self._deployments[user_id]:
            self._deployments[user_id][strategy].is_active = False
            db.set_user_field(user_id, f"trade_{strategy}", 0)
            return True
        return False


# Global instance
deployment_manager = StrategyDeploymentManager()
