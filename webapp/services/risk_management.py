"""
Lyxen Advanced Risk Management & Position Sizing
Professional risk management tools for backtesting

Features:
- Kelly Criterion
- Optimal F
- Fixed fractional
- Volatility-based sizing
- Maximum drawdown protection
- Portfolio heat management
- Risk-adjusted metrics (Sharpe, Sortino, Calmar, Omega)
"""
import math
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class PositionSizingMethod(Enum):
    """Position sizing methods"""
    FIXED_PERCENT = "fixed_percent"
    FIXED_AMOUNT = "fixed_amount"
    KELLY_CRITERION = "kelly_criterion"
    OPTIMAL_F = "optimal_f"
    VOLATILITY_BASED = "volatility_based"
    ATR_BASED = "atr_based"
    RISK_PARITY = "risk_parity"


@dataclass
class TradeResult:
    """Single trade result for analysis"""
    pnl: float
    pnl_percent: float
    win: bool
    holding_bars: int
    max_drawdown: float = 0.0


@dataclass
class RiskMetrics:
    """Complete risk metrics"""
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    omega_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    avg_drawdown: float
    recovery_factor: float
    profit_factor: float
    expectancy: float
    sqn: float  # System Quality Number


class KellyCriterion:
    """Kelly Criterion for optimal position sizing"""
    
    @staticmethod
    def calculate(win_rate: float, avg_win: float, avg_loss: float, max_kelly: float = 0.25) -> float:
        """
        Calculate Kelly percentage
        
        Args:
            win_rate: Probability of winning (0-1)
            avg_win: Average winning trade return
            avg_loss: Average losing trade return (positive)
            max_kelly: Maximum Kelly to use (cap for safety)
        
        Returns:
            Optimal position size as fraction of capital
        """
        if win_rate <= 0 or win_rate >= 1:
            return 0.0
        
        if avg_loss == 0:
            return 0.0
        
        # Kelly formula: f* = (p*b - q) / b
        # where p = win rate, q = 1-p, b = avg_win/avg_loss
        b = avg_win / avg_loss
        q = 1 - win_rate
        
        kelly = (win_rate * b - q) / b
        
        # Apply safety factor (half Kelly or quarter Kelly)
        kelly = max(0, min(kelly, max_kelly))
        
        return kelly
    
    @staticmethod
    def calculate_from_trades(trades: List[TradeResult], max_kelly: float = 0.25) -> float:
        """Calculate Kelly from trade history"""
        if not trades:
            return 0.0
        
        wins = [t for t in trades if t.win]
        losses = [t for t in trades if not t.win]
        
        if not wins or not losses:
            return 0.0
        
        win_rate = len(wins) / len(trades)
        avg_win = sum(t.pnl_percent for t in wins) / len(wins)
        avg_loss = abs(sum(t.pnl_percent for t in losses) / len(losses))
        
        return KellyCriterion.calculate(win_rate, avg_win, avg_loss, max_kelly)


class OptimalF:
    """Optimal F (Ralph Vince) - Maximum geometric growth"""
    
    @staticmethod
    def calculate(trades_pnl: List[float], starting_capital: float = 10000, 
                  iterations: int = 100) -> Tuple[float, float]:
        """
        Calculate Optimal F
        
        Returns:
            (optimal_f, terminal_wealth_ratio)
        """
        if not trades_pnl or len(trades_pnl) < 10:
            return 0.01, 1.0
        
        # Find largest loss
        largest_loss = abs(min(trades_pnl))
        if largest_loss == 0:
            return 0.01, 1.0
        
        best_f = 0.01
        best_twr = 1.0
        
        # Search for optimal f from 0.01 to 1.0
        for i in range(1, iterations + 1):
            f = i / iterations
            
            # Calculate terminal wealth ratio
            twr = 1.0
            for pnl in trades_pnl:
                # HPR = 1 + (f * pnl / largest_loss)
                hpr = 1 + (f * pnl / largest_loss)
                twr *= hpr
                
                if twr <= 0:
                    break
            
            if twr > best_twr:
                best_twr = twr
                best_f = f
        
        # Apply safety factor (typically use 50% of optimal F)
        safe_f = best_f * 0.5
        
        return safe_f, best_twr


class VolatilityBasedSizing:
    """Position sizing based on volatility"""
    
    @staticmethod
    def calculate_size(
        target_risk_percent: float,
        atr: float,
        current_price: float,
        account_balance: float,
        atr_multiplier: float = 2.0
    ) -> float:
        """
        Calculate position size based on ATR volatility
        
        Args:
            target_risk_percent: Target risk per trade (e.g., 1.0 for 1%)
            atr: Average True Range value
            current_price: Current asset price
            account_balance: Trading account balance
            atr_multiplier: Stop loss distance in ATR units
        
        Returns:
            Position size in base currency
        """
        if atr == 0 or current_price == 0:
            return 0.0
        
        # Risk amount in dollars
        risk_amount = account_balance * (target_risk_percent / 100)
        
        # Stop distance
        stop_distance = atr * atr_multiplier
        
        # Position size
        position_size = risk_amount / stop_distance
        
        return position_size


class AdvancedRiskMetrics:
    """Calculate advanced risk-adjusted performance metrics"""
    
    @staticmethod
    def sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
        """
        Calculate Sharpe Ratio
        
        Args:
            returns: List of period returns
            risk_free_rate: Annual risk-free rate (e.g., 0.02 for 2%)
            periods_per_year: Number of periods per year (252 for daily, 52 for weekly)
        """
        if not returns or len(returns) < 2:
            return 0.0
        
        returns_array = np.array(returns)
        
        # Excess returns
        period_rf = risk_free_rate / periods_per_year
        excess_returns = returns_array - period_rf
        
        if np.std(excess_returns) == 0:
            return 0.0
        
        sharpe = (np.mean(excess_returns) / np.std(excess_returns)) * np.sqrt(periods_per_year)
        
        return sharpe
    
    @staticmethod
    def sortino_ratio(returns: List[float], target_return: float = 0.0, periods_per_year: int = 252) -> float:
        """
        Calculate Sortino Ratio (penalizes only downside volatility)
        """
        if not returns or len(returns) < 2:
            return 0.0
        
        returns_array = np.array(returns)
        
        # Downside returns (below target)
        downside_returns = returns_array[returns_array < target_return] - target_return
        
        if len(downside_returns) == 0:
            return 0.0
        
        downside_deviation = np.sqrt(np.mean(downside_returns ** 2))
        
        if downside_deviation == 0:
            return 0.0
        
        sortino = (np.mean(returns_array) - target_return) / downside_deviation * np.sqrt(periods_per_year)
        
        return sortino
    
    @staticmethod
    def calmar_ratio(returns: List[float], max_drawdown: float) -> float:
        """
        Calculate Calmar Ratio (return / max drawdown)
        """
        if not returns or max_drawdown == 0:
            return 0.0
        
        annual_return = sum(returns) * 252 / len(returns)  # Annualized
        
        calmar = annual_return / abs(max_drawdown)
        
        return calmar
    
    @staticmethod
    def omega_ratio(returns: List[float], threshold: float = 0.0) -> float:
        """
        Calculate Omega Ratio (probability-weighted ratio of gains vs losses)
        """
        if not returns:
            return 1.0
        
        returns_array = np.array(returns)
        
        gains = returns_array[returns_array > threshold] - threshold
        losses = threshold - returns_array[returns_array < threshold]
        
        if len(losses) == 0 or np.sum(losses) == 0:
            return 999.0 if len(gains) > 0 else 1.0
        
        omega = np.sum(gains) / np.sum(losses)
        
        return omega
    
    @staticmethod
    def calculate_drawdown_series(equity_curve: List[float]) -> List[float]:
        """Calculate drawdown at each point"""
        if not equity_curve:
            return []
        
        drawdowns = []
        peak = equity_curve[0]
        
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            
            if peak == 0:
                drawdown = 0
            else:
                drawdown = (equity - peak) / peak * 100
            
            drawdowns.append(drawdown)
        
        return drawdowns
    
    @staticmethod
    def max_drawdown(equity_curve: List[float]) -> Tuple[float, int, int]:
        """
        Calculate maximum drawdown and duration
        
        Returns:
            (max_dd_percent, start_index, duration_bars)
        """
        if not equity_curve:
            return 0.0, 0, 0
        
        drawdowns = AdvancedRiskMetrics.calculate_drawdown_series(equity_curve)
        
        max_dd = min(drawdowns)
        max_dd_idx = drawdowns.index(max_dd)
        
        # Find duration
        duration = 0
        for i in range(max_dd_idx, len(drawdowns)):
            if drawdowns[i] >= 0:
                break
            duration += 1
        
        return max_dd, max_dd_idx, duration
    
    @staticmethod
    def system_quality_number(trades: List[TradeResult]) -> float:
        """
        Calculate SQN (System Quality Number) by Van Tharp
        
        SQN = sqrt(N) * mean(R) / stdev(R)
        where R = R-multiples (profit/initial risk)
        """
        if not trades or len(trades) < 10:
            return 0.0
        
        r_multiples = [t.pnl_percent for t in trades]
        
        n = len(r_multiples)
        mean_r = np.mean(r_multiples)
        std_r = np.std(r_multiples)
        
        if std_r == 0:
            return 0.0
        
        sqn = math.sqrt(n) * mean_r / std_r
        
        return sqn
    
    @staticmethod
    def profit_factor(trades: List[TradeResult]) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        if not trades:
            return 0.0
        
        gross_profit = sum(t.pnl for t in trades if t.pnl > 0)
        gross_loss = abs(sum(t.pnl for t in trades if t.pnl < 0))
        
        if gross_loss == 0:
            return 999.0 if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss
    
    @staticmethod
    def expectancy(trades: List[TradeResult]) -> float:
        """Calculate expectancy (average $ per trade)"""
        if not trades:
            return 0.0
        
        return sum(t.pnl for t in trades) / len(trades)
    
    @staticmethod
    def recovery_factor(total_profit: float, max_drawdown: float) -> float:
        """Calculate recovery factor (net profit / max drawdown)"""
        if max_drawdown == 0:
            return 999.0 if total_profit > 0 else 0.0
        
        return total_profit / abs(max_drawdown)


class RiskManager:
    """Unified risk management system"""
    
    def __init__(
        self,
        max_risk_per_trade: float = 1.0,
        max_portfolio_risk: float = 5.0,
        max_drawdown_limit: float = 20.0,
        sizing_method: PositionSizingMethod = PositionSizingMethod.FIXED_PERCENT
    ):
        """
        Initialize risk manager
        
        Args:
            max_risk_per_trade: Maximum risk per trade (%)
            max_portfolio_risk: Maximum total portfolio risk (%)
            max_drawdown_limit: Stop trading if drawdown exceeds this (%)
            sizing_method: Position sizing method
        """
        self.max_risk_per_trade = max_risk_per_trade
        self.max_portfolio_risk = max_portfolio_risk
        self.max_drawdown_limit = max_drawdown_limit
        self.sizing_method = sizing_method
        
        self.current_drawdown = 0.0
        self.portfolio_heat = 0.0  # Total risk currently in market
    
    def calculate_position_size(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss_price: float,
        trades_history: Optional[List[TradeResult]] = None,
        atr: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate optimal position size based on selected method
        
        Returns:
            Dict with size, risk_amount, and sizing_details
        """
        # Risk per unit
        risk_per_unit = abs(entry_price - stop_loss_price)
        
        if risk_per_unit == 0:
            return {"size": 0, "risk_amount": 0, "method": "error", "details": "Invalid stop loss"}
        
        # Base risk amount
        base_risk_amount = account_balance * (self.max_risk_per_trade / 100)
        
        # Calculate size based on method
        if self.sizing_method == PositionSizingMethod.FIXED_PERCENT:
            risk_amount = base_risk_amount
            size = risk_amount / risk_per_unit
            details = f"Fixed {self.max_risk_per_trade}%"
        
        elif self.sizing_method == PositionSizingMethod.KELLY_CRITERION:
            if trades_history and len(trades_history) >= 20:
                kelly_pct = KellyCriterion.calculate_from_trades(trades_history, max_kelly=0.25)
                risk_amount = account_balance * kelly_pct
                size = risk_amount / risk_per_unit
                details = f"Kelly {kelly_pct*100:.1f}%"
            else:
                # Fall back to fixed percent
                risk_amount = base_risk_amount
                size = risk_amount / risk_per_unit
                details = "Kelly (insufficient data, using fixed %)"
        
        elif self.sizing_method == PositionSizingMethod.OPTIMAL_F:
            if trades_history and len(trades_history) >= 20:
                trades_pnl = [t.pnl for t in trades_history]
                optimal_f, twr = OptimalF.calculate(trades_pnl, account_balance)
                risk_amount = account_balance * optimal_f
                size = risk_amount / risk_per_unit
                details = f"Optimal F {optimal_f*100:.1f}% (TWR: {twr:.2f})"
            else:
                risk_amount = base_risk_amount
                size = risk_amount / risk_per_unit
                details = "Optimal F (insufficient data)"
        
        elif self.sizing_method == PositionSizingMethod.VOLATILITY_BASED:
            if atr and atr > 0:
                size = VolatilityBasedSizing.calculate_size(
                    self.max_risk_per_trade,
                    atr,
                    entry_price,
                    account_balance,
                    atr_multiplier=2.0
                )
                risk_amount = size * risk_per_unit
                details = f"ATR-based (ATR: {atr:.2f})"
            else:
                risk_amount = base_risk_amount
                size = risk_amount / risk_per_unit
                details = "Volatility (no ATR data)"
        
        else:
            # Default to fixed percent
            risk_amount = base_risk_amount
            size = risk_amount / risk_per_unit
            details = "Fixed percent (default)"
        
        # Check portfolio heat
        if self.portfolio_heat + (risk_amount / account_balance * 100) > self.max_portfolio_risk:
            size = 0
            details += " [BLOCKED: Portfolio heat limit]"
        
        # Check drawdown limit
        if abs(self.current_drawdown) > self.max_drawdown_limit:
            size = 0
            details += " [BLOCKED: Max drawdown exceeded]"
        
        return {
            "size": size,
            "risk_amount": risk_amount,
            "risk_percent": (risk_amount / account_balance) * 100,
            "method": self.sizing_method.value,
            "details": details,
            "portfolio_heat": self.portfolio_heat,
            "current_drawdown": self.current_drawdown
        }
    
    def update_portfolio_state(self, open_positions_risk: float, current_drawdown: float):
        """Update risk manager state"""
        self.portfolio_heat = open_positions_risk
        self.current_drawdown = current_drawdown
    
    def calculate_all_metrics(
        self,
        trades: List[TradeResult],
        equity_curve: List[float],
        initial_balance: float
    ) -> RiskMetrics:
        """Calculate complete risk metrics"""
        if not trades:
            return RiskMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        # Returns calculation
        returns = []
        for i in range(1, len(equity_curve)):
            ret = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
            returns.append(ret)
        
        # Calculate metrics
        sharpe = AdvancedRiskMetrics.sharpe_ratio(returns)
        sortino = AdvancedRiskMetrics.sortino_ratio(returns)
        
        max_dd, dd_idx, dd_duration = AdvancedRiskMetrics.max_drawdown(equity_curve)
        
        total_profit = equity_curve[-1] - initial_balance
        calmar = AdvancedRiskMetrics.calmar_ratio(returns, max_dd)
        omega = AdvancedRiskMetrics.omega_ratio(returns)
        
        drawdowns = AdvancedRiskMetrics.calculate_drawdown_series(equity_curve)
        avg_dd = sum(drawdowns) / len(drawdowns)
        
        recovery = AdvancedRiskMetrics.recovery_factor(total_profit, max_dd)
        profit_factor = AdvancedRiskMetrics.profit_factor(trades)
        expectancy = AdvancedRiskMetrics.expectancy(trades)
        sqn = AdvancedRiskMetrics.system_quality_number(trades)
        
        return RiskMetrics(
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            calmar_ratio=calmar,
            omega_ratio=omega,
            max_drawdown=max_dd,
            max_drawdown_duration=dd_duration,
            avg_drawdown=avg_dd,
            recovery_factor=recovery,
            profit_factor=profit_factor,
            expectancy=expectancy,
            sqn=sqn
        )


# Export instances
kelly_calculator = KellyCriterion()
optimal_f_calculator = OptimalF()
risk_metrics_calculator = AdvancedRiskMetrics()
