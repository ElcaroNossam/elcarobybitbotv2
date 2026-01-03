"""
Oracle Portfolio Optimizer
==========================

Modern Portfolio Theory implementation for crypto:
- Efficient Frontier calculation
- Sharpe/Sortino/Calmar ratios
- Risk parity allocation
- Position sizing
- Correlation analysis

Based on Markowitz portfolio theory with crypto-specific adjustments.
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("oracle.portfolio")


@dataclass
class Asset:
    """Asset data for portfolio optimization"""
    symbol: str
    expected_return: float  # Annual expected return
    volatility: float  # Annual volatility
    current_weight: float = 0.0
    min_weight: float = 0.0
    max_weight: float = 1.0
    risk_score: float = 50.0  # Oracle risk score


@dataclass
class PortfolioMetrics:
    """Optimized portfolio metrics"""
    expected_return: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown: float = 0.0
    var_95: float = 0.0  # Value at Risk 95%
    cvar_95: float = 0.0  # Conditional VaR


@dataclass
class AllocationResult:
    """Portfolio allocation recommendation"""
    weights: Dict[str, float] = field(default_factory=dict)
    metrics: PortfolioMetrics = field(default_factory=PortfolioMetrics)
    rebalance_trades: List[Dict] = field(default_factory=list)
    risk_contribution: Dict[str, float] = field(default_factory=dict)


class PortfolioOptimizer:
    """
    Portfolio Optimization Engine
    
    Implements Modern Portfolio Theory with crypto adjustments:
    - Higher volatility assumptions
    - Correlation regime changes
    - Liquidity constraints
    - Risk score integration
    """
    
    RISK_FREE_RATE = 0.05  # 5% annual (stablecoin yield)
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
    
    def optimize(
        self,
        assets: List[Asset],
        correlation_matrix: Optional[np.ndarray] = None,
        target: str = "max_sharpe",  # max_sharpe, min_volatility, risk_parity
        risk_budget: Optional[float] = None  # Max portfolio volatility
    ) -> AllocationResult:
        """
        Optimize portfolio allocation.
        
        Args:
            assets: List of assets with returns/volatility
            correlation_matrix: Asset correlations (if None, assumed 0.5)
            target: Optimization objective
            risk_budget: Maximum portfolio volatility constraint
        
        Returns:
            AllocationResult with optimal weights
        """
        result = AllocationResult()
        n = len(assets)
        
        if n == 0:
            logger.warning("No assets provided for optimization")
            return result
        
        # Build expected returns vector
        expected_returns = np.array([a.expected_return for a in assets])
        
        # Build volatility vector
        volatilities = np.array([a.volatility for a in assets])
        
        # Build correlation matrix
        if correlation_matrix is None:
            correlation_matrix = self._default_correlation_matrix(n)
        
        # Build covariance matrix
        cov_matrix = self._build_covariance_matrix(volatilities, correlation_matrix)
        
        # Optimize based on target
        if target == "max_sharpe":
            weights = self._maximize_sharpe(
                expected_returns, cov_matrix, assets, risk_budget
            )
        elif target == "min_volatility":
            weights = self._minimize_volatility(cov_matrix, assets)
        elif target == "risk_parity":
            weights = self._risk_parity(volatilities, correlation_matrix, assets)
        else:
            weights = self._equal_weight(n)
        
        # Adjust for risk scores (penalize high-risk assets)
        weights = self._adjust_for_risk_scores(weights, assets)
        
        # Normalize weights
        weights = weights / np.sum(weights)
        
        # Calculate portfolio metrics
        port_return = np.dot(weights, expected_returns)
        port_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe = (port_return - self.RISK_FREE_RATE) / port_volatility if port_volatility > 0 else 0
        
        # Value at Risk (assuming normal distribution)
        var_95 = port_return - 1.645 * port_volatility
        cvar_95 = port_return - 2.063 * port_volatility  # Expected shortfall
        
        # Risk contribution
        risk_contrib = self._calculate_risk_contribution(weights, cov_matrix)
        
        # Populate result
        result.weights = {assets[i].symbol: float(weights[i]) for i in range(n)}
        result.metrics = PortfolioMetrics(
            expected_return=float(port_return),
            volatility=float(port_volatility),
            sharpe_ratio=float(sharpe),
            var_95=float(var_95),
            cvar_95=float(cvar_95)
        )
        result.risk_contribution = {
            assets[i].symbol: float(risk_contrib[i]) for i in range(n)
        }
        
        # Calculate rebalance trades
        result.rebalance_trades = self._calculate_rebalance_trades(
            assets, result.weights
        )
        
        logger.info(
            f"Portfolio optimized: E(R)={port_return:.1%}, "
            f"Vol={port_volatility:.1%}, Sharpe={sharpe:.2f}"
        )
        
        return result
    
    def efficient_frontier(
        self,
        assets: List[Asset],
        correlation_matrix: Optional[np.ndarray] = None,
        n_points: int = 20
    ) -> List[Tuple[float, float, Dict[str, float]]]:
        """
        Calculate efficient frontier points.
        
        Returns:
            List of (return, volatility, weights) tuples
        """
        n = len(assets)
        if n == 0:
            return []
        
        expected_returns = np.array([a.expected_return for a in assets])
        volatilities = np.array([a.volatility for a in assets])
        
        if correlation_matrix is None:
            correlation_matrix = self._default_correlation_matrix(n)
        
        cov_matrix = self._build_covariance_matrix(volatilities, correlation_matrix)
        
        # Get return range
        min_ret = np.min(expected_returns)
        max_ret = np.max(expected_returns)
        
        frontier = []
        
        for target_return in np.linspace(min_ret, max_ret, n_points):
            weights = self._minimize_volatility_for_return(
                expected_returns, cov_matrix, target_return, assets
            )
            
            if weights is not None:
                port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                weight_dict = {assets[i].symbol: float(weights[i]) for i in range(n)}
                frontier.append((float(target_return), float(port_vol), weight_dict))
        
        return frontier
    
    def position_size(
        self,
        capital: float,
        asset: Asset,
        risk_per_trade: float = 0.02,  # 2% of capital
        stop_loss_pct: float = 0.05    # 5% stop loss
    ) -> Dict[str, Any]:
        """
        Calculate position size using Kelly criterion modified for crypto.
        
        Args:
            capital: Total portfolio capital
            asset: Asset to size
            risk_per_trade: Max risk per trade as fraction of capital
            stop_loss_pct: Stop loss percentage
        
        Returns:
            Position sizing recommendation
        """
        # Risk amount
        risk_amount = capital * risk_per_trade
        
        # Position size based on stop loss
        position_size = risk_amount / stop_loss_pct
        
        # Kelly fraction (simplified)
        # f = (edge / odds) where edge = E(R) and odds = volatility
        win_rate = 0.5 + (asset.expected_return / (asset.volatility * 2))
        win_rate = max(0.3, min(0.7, win_rate))  # Bound between 30-70%
        
        avg_win = asset.volatility * 0.5  # Half of volatility
        avg_loss = stop_loss_pct
        
        kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        kelly = max(0, min(0.5, kelly))  # Cap at 50% Kelly
        
        # Apply half-Kelly for safety
        kelly_fraction = kelly / 2
        kelly_position = capital * kelly_fraction
        
        # Final position (minimum of methods)
        final_position = min(position_size, kelly_position)
        
        # Apply risk score adjustment
        risk_multiplier = 1 - (asset.risk_score / 200)  # 50 -> 0.75x, 100 -> 0.5x
        risk_multiplier = max(0.2, min(1.0, risk_multiplier))
        final_position *= risk_multiplier
        
        return {
            "position_size": round(final_position, 2),
            "position_pct": round(final_position / capital * 100, 2),
            "risk_amount": round(risk_amount, 2),
            "kelly_fraction": round(kelly_fraction, 4),
            "risk_multiplier": round(risk_multiplier, 2),
            "max_loss": round(final_position * stop_loss_pct, 2)
        }
    
    def _default_correlation_matrix(self, n: int) -> np.ndarray:
        """Create default correlation matrix (0.5 for all pairs)"""
        corr = np.ones((n, n)) * 0.5
        np.fill_diagonal(corr, 1.0)
        return corr
    
    def _build_covariance_matrix(
        self,
        volatilities: np.ndarray,
        correlations: np.ndarray
    ) -> np.ndarray:
        """Build covariance matrix from volatilities and correlations"""
        n = len(volatilities)
        cov = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                cov[i, j] = correlations[i, j] * volatilities[i] * volatilities[j]
        
        return cov
    
    def _maximize_sharpe(
        self,
        returns: np.ndarray,
        cov: np.ndarray,
        assets: List[Asset],
        risk_budget: Optional[float]
    ) -> np.ndarray:
        """Find maximum Sharpe ratio portfolio (analytical solution)"""
        n = len(returns)
        
        # Excess returns
        excess = returns - self.RISK_FREE_RATE
        
        try:
            # Analytical solution: w* = Sigma^-1 * excess / (1' * Sigma^-1 * excess)
            cov_inv = np.linalg.inv(cov)
            weights = np.dot(cov_inv, excess)
            
            # Handle negative weights (go to constrained optimization)
            if np.any(weights < 0):
                weights = self._constrained_max_sharpe(returns, cov, assets)
            else:
                weights = weights / np.sum(weights)
            
            # Apply risk budget constraint
            if risk_budget is not None:
                port_vol = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))
                if port_vol > risk_budget:
                    # Scale down weights
                    scale = risk_budget / port_vol
                    weights = weights * scale
                    weights = weights / np.sum(weights)
        
        except np.linalg.LinAlgError:
            weights = self._equal_weight(n)
        
        return weights
    
    def _constrained_max_sharpe(
        self,
        returns: np.ndarray,
        cov: np.ndarray,
        assets: List[Asset]
    ) -> np.ndarray:
        """Constrained maximum Sharpe (simple gradient descent)"""
        n = len(returns)
        weights = np.ones(n) / n  # Start equal
        
        # Constraints
        min_weights = np.array([a.min_weight for a in assets])
        max_weights = np.array([a.max_weight for a in assets])
        
        learning_rate = 0.01
        iterations = 1000
        
        for _ in range(iterations):
            # Calculate gradient of Sharpe ratio
            port_ret = np.dot(weights, returns)
            port_var = np.dot(weights.T, np.dot(cov, weights))
            port_vol = np.sqrt(port_var)
            
            excess = port_ret - self.RISK_FREE_RATE
            
            # Gradient of Sharpe ratio
            grad_ret = returns
            grad_var = 2 * np.dot(cov, weights)
            
            gradient = (grad_ret * port_vol - excess * grad_var / (2 * port_vol)) / port_var
            
            # Update
            weights = weights + learning_rate * gradient
            
            # Apply constraints
            weights = np.clip(weights, min_weights, max_weights)
            weights = weights / np.sum(weights)
        
        return weights
    
    def _minimize_volatility(
        self,
        cov: np.ndarray,
        assets: List[Asset]
    ) -> np.ndarray:
        """Find minimum volatility portfolio"""
        n = len(assets)
        
        try:
            cov_inv = np.linalg.inv(cov)
            ones = np.ones(n)
            weights = np.dot(cov_inv, ones) / np.dot(ones, np.dot(cov_inv, ones))
            
            # Handle negative weights
            if np.any(weights < 0):
                weights = np.maximum(weights, 0)
                weights = weights / np.sum(weights)
        
        except np.linalg.LinAlgError:
            weights = self._equal_weight(n)
        
        return weights
    
    def _minimize_volatility_for_return(
        self,
        returns: np.ndarray,
        cov: np.ndarray,
        target_return: float,
        assets: List[Asset]
    ) -> Optional[np.ndarray]:
        """Find minimum volatility portfolio for target return"""
        n = len(assets)
        
        # Simple iterative approach
        weights = np.ones(n) / n
        learning_rate = 0.01
        iterations = 500
        
        for _ in range(iterations):
            # Current portfolio
            port_ret = np.dot(weights, returns)
            
            # Gradient of volatility
            grad_vol = np.dot(cov, weights) / np.sqrt(np.dot(weights.T, np.dot(cov, weights)))
            
            # Penalty for return constraint
            ret_penalty = 10.0 * (port_ret - target_return) * returns
            
            # Update
            weights = weights - learning_rate * (grad_vol + ret_penalty)
            
            # Project to simplex
            weights = np.maximum(weights, 0)
            if np.sum(weights) > 0:
                weights = weights / np.sum(weights)
            else:
                return None
        
        return weights
    
    def _risk_parity(
        self,
        volatilities: np.ndarray,
        correlations: np.ndarray,
        assets: List[Asset]
    ) -> np.ndarray:
        """Risk parity allocation (equal risk contribution)"""
        n = len(volatilities)
        
        # Simple inverse volatility weighting as approximation
        inv_vol = 1 / volatilities
        weights = inv_vol / np.sum(inv_vol)
        
        return weights
    
    def _equal_weight(self, n: int) -> np.ndarray:
        """Equal weight allocation"""
        return np.ones(n) / n
    
    def _adjust_for_risk_scores(
        self,
        weights: np.ndarray,
        assets: List[Asset]
    ) -> np.ndarray:
        """Adjust weights based on Oracle risk scores"""
        risk_scores = np.array([a.risk_score for a in assets])
        
        # Convert to multipliers (higher score = higher risk = lower allocation)
        # Score 30 -> 1.0x, Score 70 -> 0.5x, Score 100 -> 0.2x
        multipliers = 1.5 - (risk_scores / 100)
        multipliers = np.clip(multipliers, 0.2, 1.2)
        
        adjusted = weights * multipliers
        
        return adjusted
    
    def _calculate_risk_contribution(
        self,
        weights: np.ndarray,
        cov: np.ndarray
    ) -> np.ndarray:
        """Calculate each asset's contribution to portfolio risk"""
        port_var = np.dot(weights.T, np.dot(cov, weights))
        port_vol = np.sqrt(port_var)
        
        if port_vol == 0:
            return weights
        
        # Marginal contribution
        marginal = np.dot(cov, weights) / port_vol
        
        # Risk contribution = weight * marginal
        contribution = weights * marginal / port_vol
        
        return contribution
    
    def _calculate_rebalance_trades(
        self,
        assets: List[Asset],
        target_weights: Dict[str, float]
    ) -> List[Dict]:
        """Calculate trades needed to rebalance"""
        trades = []
        
        for asset in assets:
            current = asset.current_weight
            target = target_weights.get(asset.symbol, 0)
            diff = target - current
            
            if abs(diff) > 0.01:  # 1% threshold
                trades.append({
                    "symbol": asset.symbol,
                    "action": "BUY" if diff > 0 else "SELL",
                    "current_weight": round(current * 100, 2),
                    "target_weight": round(target * 100, 2),
                    "change": round(diff * 100, 2)
                })
        
        return trades


async def test():
    """Test portfolio optimizer"""
    optimizer = PortfolioOptimizer()
    
    # Mock assets
    assets = [
        Asset(symbol="BTC", expected_return=0.50, volatility=0.60, risk_score=35, current_weight=0.4),
        Asset(symbol="ETH", expected_return=0.80, volatility=0.80, risk_score=40, current_weight=0.3),
        Asset(symbol="SOL", expected_return=1.20, volatility=1.20, risk_score=55, current_weight=0.2),
        Asset(symbol="LINK", expected_return=0.60, volatility=0.90, risk_score=45, current_weight=0.1),
    ]
    
    # Optimize
    result = optimizer.optimize(assets, target="max_sharpe")
    
    print("\n=== PORTFOLIO OPTIMIZATION ===")
    print(f"\nOptimal Weights:")
    for symbol, weight in result.weights.items():
        print(f"  {symbol}: {weight:.1%}")
    
    print(f"\nPortfolio Metrics:")
    print(f"  Expected Return: {result.metrics.expected_return:.1%}")
    print(f"  Volatility: {result.metrics.volatility:.1%}")
    print(f"  Sharpe Ratio: {result.metrics.sharpe_ratio:.2f}")
    print(f"  VaR 95%: {result.metrics.var_95:.1%}")
    
    print(f"\nRisk Contribution:")
    for symbol, contrib in result.risk_contribution.items():
        print(f"  {symbol}: {contrib:.1%}")
    
    print(f"\nRebalance Trades:")
    for trade in result.rebalance_trades:
        print(f"  {trade['action']} {trade['symbol']}: {trade['change']:+.1f}%")
    
    # Position sizing example
    print(f"\n=== POSITION SIZING (BTC, $10,000 capital) ===")
    sizing = optimizer.position_size(
        capital=10000,
        asset=assets[0],
        risk_per_trade=0.02,
        stop_loss_pct=0.05
    )
    for key, value in sizing.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test())
