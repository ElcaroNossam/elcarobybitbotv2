"""
Strategy Deployment Service
Manages deploying backtested strategies to live trading
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

# PostgreSQL imports
from webapp.api.db_helper import get_db

logger = logging.getLogger(__name__)


@dataclass
class Deployment:
    """Deployment record"""
    id: int
    user_id: int
    strategy: str
    params: Dict
    backtest_results: Dict
    deployed_at: str
    is_active: bool
    live_stats: Dict = field(default_factory=dict)


class StrategyDeployer:
    """Manages strategy deployments from backtest to live trading"""
    
    # Strategy field mapping in database
    STRATEGY_FIELDS = {
        "elcaro": "trade_elcaro",
        "rsibboi": "trade_rsi_bb",
        "rsi_bb": "trade_rsi_bb",
        "wyckoff": "trade_wyckoff",
        "scryptomera": "trade_scryptomera",
        "scalper": "trade_scalper",
        "oi": "trade_oi",
    }
    
    # Default parameter mapping
    PARAM_FIELDS = {
        "stop_loss_percent": "sl_pct",
        "take_profit_percent": "tp_pct",
        "leverage": "leverage",
        "position_size": "position_pct",
        "max_positions": "max_pos",
    }
    
    def __init__(self):
        # Tables are created via migrations - no runtime init needed
        pass
    
    def _init_db(self):
        """DEPRECATED: Tables are now created via migrations"""
        pass
    
    async def deploy(
        self,
        user_id: int,
        strategy: str,
        params: Dict[str, Any],
        backtest_results: Dict[str, Any],
        validation_rules: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Deploy a backtested strategy to live trading.
        
        Args:
            user_id: User ID
            strategy: Strategy name
            params: Optimized parameters
            backtest_results: Backtest results for validation
            validation_rules: Custom validation rules
        
        Returns:
            Deployment result dict
        """
        # Default validation rules
        rules = validation_rules or {
            "min_win_rate": 45.0,
            "min_profit_factor": 1.1,
            "min_trades": 10,
            "max_drawdown": 30.0,
            "min_sharpe": 0.5
        }
        
        # Validate backtest results
        validation = self._validate_results(backtest_results, rules)
        if not validation["passed"]:
            return {
                "success": False,
                "error": "Validation failed",
                "details": validation["issues"]
            }
        
        # Deactivate previous deployment for same strategy
        await self._deactivate_existing(user_id, strategy)
        
        # Save deployment
        deployment_id = await self._save_deployment(
            user_id, strategy, params, backtest_results
        )
        
        # Apply settings to user
        await self._apply_to_user(user_id, strategy, params)
        
        # Log event
        await self._log_event(deployment_id, "deployed", {
            "params": params,
            "validation": validation
        })
        
        return {
            "success": True,
            "deployment_id": deployment_id,
            "strategy": strategy,
            "params": params,
            "validation": validation,
            "message": f"Strategy '{strategy}' deployed successfully"
        }
    
    def _validate_results(
        self, 
        results: Dict[str, Any], 
        rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate backtest results against rules"""
        issues = []
        
        win_rate = results.get("win_rate", 0)
        profit_factor = results.get("profit_factor", 0)
        total_trades = results.get("total_trades", 0)
        max_drawdown = results.get("max_drawdown", 100)
        sharpe = results.get("sharpe_ratio", 0)
        
        if win_rate < rules.get("min_win_rate", 0):
            issues.append(f"Win rate {win_rate:.1f}% < {rules['min_win_rate']}%")
        
        if profit_factor < rules.get("min_profit_factor", 0):
            issues.append(f"Profit factor {profit_factor:.2f} < {rules['min_profit_factor']}")
        
        if total_trades < rules.get("min_trades", 0):
            issues.append(f"Only {total_trades} trades < {rules['min_trades']} minimum")
        
        if max_drawdown > rules.get("max_drawdown", 100):
            issues.append(f"Max drawdown {max_drawdown:.1f}% > {rules['max_drawdown']}%")
        
        if sharpe < rules.get("min_sharpe", 0):
            issues.append(f"Sharpe ratio {sharpe:.2f} < {rules['min_sharpe']}")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "scores": {
                "win_rate": win_rate,
                "profit_factor": profit_factor,
                "trades": total_trades,
                "max_drawdown": max_drawdown,
                "sharpe": sharpe
            }
        }
    
    async def _deactivate_existing(self, user_id: int, strategy: str):
        """Deactivate existing deployments for same strategy"""
        try:
            conn = get_db()
            try:
                cur = conn.cursor()
                
                cur.execute("""
                    UPDATE strategy_deployments 
                    SET is_active = FALSE, updated_at = %s
                    WHERE user_id = %s AND strategy_name = %s AND is_active = TRUE
                """, (datetime.now().isoformat(), user_id, strategy))
                
                conn.commit()
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Failed to deactivate existing: {e}")
    
    async def _save_deployment(
        self,
        user_id: int,
        strategy: str,
        params: Dict,
        backtest_results: Dict
    ) -> int:
        """Save deployment to database"""
        try:
            conn = get_db()
            try:
                cur = conn.cursor()
                
                cur.execute("""
                    INSERT INTO strategy_deployments 
                    (user_id, strategy_name, params_json, backtest_results_json, deployed_at, is_active)
                    VALUES (?, ?, ?, ?, ?, 1)
                    RETURNING id
                """, (
                    user_id,
                    strategy,
                    json.dumps(params),
                    json.dumps(backtest_results),
                    datetime.now().isoformat()
                ))
                
                row = cur.fetchone()
                deployment_id = row["id"] if row else -1
                conn.commit()
            finally:
                conn.close()
            
            return deployment_id
        except Exception as e:
            logger.error(f"Failed to save deployment: {e}")
            return -1
    
    async def _apply_to_user(
        self,
        user_id: int,
        strategy: str,
        params: Dict
    ):
        """Apply deployment settings to user configuration"""
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from db import set_user_field
            
            # Enable the strategy
            strategy_field = self.STRATEGY_FIELDS.get(strategy.lower())
            if strategy_field:
                set_user_field(user_id, strategy_field, 1)
            
            # Apply parameters
            for param_name, value in params.items():
                field_name = self.PARAM_FIELDS.get(param_name, param_name)
                try:
                    set_user_field(user_id, field_name, value)
                except Exception:
                    pass  # Field might not exist
            
            logger.info(f"Applied strategy {strategy} params to user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to apply to user: {e}")
    
    async def _log_event(
        self,
        deployment_id: int,
        event_type: str,
        event_data: Dict
    ):
        """Log deployment event"""
        try:
            conn = get_db()
            try:
                cur = conn.cursor()
                
                cur.execute("""
                    INSERT INTO deployment_history 
                    (deployment_id, event_type, event_data)
                    VALUES (%s, %s, %s)
                """, (deployment_id, event_type, json.dumps(event_data)))
                
                conn.commit()
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Failed to log event: {e}")
    
    async def undeploy(self, user_id: int, strategy: str) -> Dict[str, Any]:
        """Undeploy a strategy (stop it from trading)"""
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from db import set_user_field
            
            # Disable the strategy
            strategy_field = self.STRATEGY_FIELDS.get(strategy.lower())
            if strategy_field:
                set_user_field(user_id, strategy_field, 0)
            
            # Deactivate deployment record
            await self._deactivate_existing(user_id, strategy)
            
            return {
                "success": True,
                "message": f"Strategy '{strategy}' undeployed"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_active_deployments(self, user_id: int) -> List[Dict]:
        """Get all active deployments for a user"""
        try:
            conn = get_db()
            try:
                cur = conn.cursor()
                
                cur.execute("""
                    SELECT * FROM strategy_deployments 
                    WHERE user_id = %s AND is_active = TRUE
                    ORDER BY deployed_at DESC
                """, (user_id,))
                
                rows = cur.fetchall()
            finally:
                conn.close()
            
            return [
                {
                    "id": row["id"],
                    "strategy": row["strategy_name"],
                    "params": json.loads(row["params_json"]) if row["params_json"] else {},
                    "backtest_results": json.loads(row["backtest_results_json"]) if row["backtest_results_json"] else {},
                    "deployed_at": row["deployed_at"],
                    "live_stats": json.loads(row["live_stats_json"]) if row["live_stats_json"] else {}
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Failed to get deployments: {e}")
            return []
    
    async def get_deployment_history(
        self, 
        user_id: int = None, 
        limit: int = 50
    ) -> List[Dict]:
        """Get deployment history"""
        try:
            conn = get_db()
            try:
                cur = conn.cursor()
                
                if user_id:
                    cur.execute("""
                        SELECT d.*, h.event_type, h.event_data, h.created_at as event_time
                        FROM strategy_deployments d
                        LEFT JOIN deployment_history h ON d.id = h.deployment_id
                        WHERE d.user_id = ?
                        ORDER BY d.deployed_at DESC
                        LIMIT ?
                    """, (user_id, limit))
                else:
                    cur.execute("""
                        SELECT d.*, h.event_type, h.event_data, h.created_at as event_time
                        FROM strategy_deployments d
                        LEFT JOIN deployment_history h ON d.id = h.deployment_id
                        ORDER BY d.deployed_at DESC
                        LIMIT ?
                    """, (limit,))
                
                rows = cur.fetchall()
            finally:
                conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return []
    
    async def update_live_stats(
        self, 
        deployment_id: int, 
        stats: Dict
    ):
        """Update live trading stats for a deployment"""
        try:
            conn = get_db()
            try:
                cur = conn.cursor()
                
                cur.execute("""
                    UPDATE strategy_deployments 
                    SET live_stats_json = ?, updated_at = ?
                    WHERE id = ?
                """, (json.dumps(stats), datetime.now().isoformat(), deployment_id))
                
                conn.commit()
            finally:
                conn.close()
            
            # Log stats update
            await self._log_event(deployment_id, "stats_update", stats)
            
        except Exception as e:
            logger.error(f"Failed to update live stats: {e}")
    
    async def compare_backtest_vs_live(
        self, 
        user_id: int, 
        strategy: str
    ) -> Dict[str, Any]:
        """Compare backtest results vs live performance"""
        deployments = await self.get_active_deployments(user_id)
        
        for dep in deployments:
            if dep["strategy"] == strategy:
                bt = dep.get("backtest_results", {})
                live = dep.get("live_stats", {})
                
                if not live:
                    return {
                        "success": False,
                        "error": "No live stats available yet"
                    }
                
                return {
                    "success": True,
                    "comparison": {
                        "backtest": {
                            "win_rate": bt.get("win_rate", 0),
                            "profit_factor": bt.get("profit_factor", 0),
                            "total_pnl_pct": bt.get("total_pnl_pct", 0)
                        },
                        "live": {
                            "win_rate": live.get("win_rate", 0),
                            "profit_factor": live.get("profit_factor", 0),
                            "total_pnl_pct": live.get("total_pnl_pct", 0)
                        },
                        "differences": {
                            "win_rate_diff": live.get("win_rate", 0) - bt.get("win_rate", 0),
                            "pf_diff": live.get("profit_factor", 0) - bt.get("profit_factor", 0)
                        }
                    }
                }
        
        return {
            "success": False,
            "error": f"No active deployment for strategy '{strategy}'"
        }


# Global deployer instance
strategy_deployer = StrategyDeployer()


# Convenience functions
async def deploy_strategy(
    user_id: int,
    strategy: str,
    params: Dict,
    backtest_results: Dict,
    **kwargs
) -> Dict:
    """Deploy a strategy"""
    return await strategy_deployer.deploy(user_id, strategy, params, backtest_results, **kwargs)


async def undeploy_strategy(user_id: int, strategy: str) -> Dict:
    """Undeploy a strategy"""
    return await strategy_deployer.undeploy(user_id, strategy)


async def get_user_deployments(user_id: int) -> List[Dict]:
    """Get user's active deployments"""
    return await strategy_deployer.get_active_deployments(user_id)
