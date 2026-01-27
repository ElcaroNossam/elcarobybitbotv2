"""
Enliko Monte Carlo Simulation & Stress Testing
Advanced statistical analysis for backtesting robustness

Features:
- Monte Carlo resampling
- Trade sequence randomization
- Drawdown probability distribution
- Confidence intervals
- Stress testing (market crashes, volatility spikes)
- Robustness score
"""
import random
import numpy as np
import math
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor
import multiprocessing


@dataclass
class MonteCarloResult:
    """Result of Monte Carlo simulation"""
    simulations: int
    mean_return: float
    median_return: float
    std_dev: float
    confidence_95_lower: float
    confidence_95_upper: float
    confidence_99_lower: float
    confidence_99_upper: float
    max_drawdown_mean: float
    max_drawdown_worst: float
    max_drawdown_best: float
    probability_profit: float
    probability_10_percent: float
    probability_20_percent: float
    probability_50_percent: float
    risk_of_ruin: float
    expected_value: float
    value_at_risk_95: float
    conditional_var_95: float
    
    def to_dict(self) -> Dict:
        return {
            "simulations": self.simulations,
            "mean_return": self.mean_return,
            "median_return": self.median_return,
            "std_dev": self.std_dev,
            "confidence_intervals": {
                "95": {
                    "lower": self.confidence_95_lower,
                    "upper": self.confidence_95_upper
                },
                "99": {
                    "lower": self.confidence_99_lower,
                    "upper": self.confidence_99_upper
                }
            },
            "max_drawdown": {
                "mean": self.max_drawdown_mean,
                "worst": self.max_drawdown_worst,
                "best": self.max_drawdown_best
            },
            "probabilities": {
                "profit": self.probability_profit,
                "10_percent": self.probability_10_percent,
                "20_percent": self.probability_20_percent,
                "50_percent": self.probability_50_percent
            },
            "risk_metrics": {
                "risk_of_ruin": self.risk_of_ruin,
                "expected_value": self.expected_value,
                "var_95": self.value_at_risk_95,
                "cvar_95": self.conditional_var_95
            }
        }


@dataclass
class StressTestResult:
    """Result of stress test"""
    scenario: str
    description: str
    final_return: float
    max_drawdown: float
    recovery_time: int
    survived: bool
    details: Dict[str, Any]


class MonteCarloSimulator:
    """Monte Carlo simulation for backtest results"""
    
    def __init__(self, num_simulations: int = 10000, random_seed: Optional[int] = None):
        """
        Initialize simulator
        
        Args:
            num_simulations: Number of Monte Carlo runs
            random_seed: Random seed for reproducibility
        """
        self.num_simulations = num_simulations
        if random_seed is not None:
            random.seed(random_seed)
            np.random.seed(random_seed)
    
    def run_trade_sequence_simulation(
        self,
        trades_pnl: List[float],
        initial_balance: float = 10000
    ) -> MonteCarloResult:
        """
        Simulate random trade sequences
        
        Randomly reorder trades and calculate statistics
        """
        if not trades_pnl or len(trades_pnl) < 10:
            return self._empty_result()
        
        simulation_results = []
        max_drawdowns = []
        
        for _ in range(self.num_simulations):
            # Randomly shuffle trades
            shuffled = random.sample(trades_pnl, len(trades_pnl))
            
            # Calculate equity curve
            equity = initial_balance
            equity_curve = [equity]
            peak = equity
            max_dd = 0
            
            for pnl in shuffled:
                equity += pnl
                equity_curve.append(equity)
                
                if equity > peak:
                    peak = equity
                
                dd = (peak - equity) / peak * 100 if peak > 0 else 0
                if dd > max_dd:
                    max_dd = dd
            
            final_return = (equity - initial_balance) / initial_balance * 100
            simulation_results.append(final_return)
            max_drawdowns.append(max_dd)
        
        return self._calculate_statistics(simulation_results, max_drawdowns, initial_balance)
    
    def run_bootstrap_simulation(
        self,
        trades_pnl: List[float],
        initial_balance: float = 10000
    ) -> MonteCarloResult:
        """
        Bootstrap resampling with replacement
        
        Sample trades with replacement and calculate statistics
        """
        if not trades_pnl or len(trades_pnl) < 10:
            return self._empty_result()
        
        simulation_results = []
        max_drawdowns = []
        
        num_trades = len(trades_pnl)
        
        for _ in range(self.num_simulations):
            # Sample with replacement
            sampled = [random.choice(trades_pnl) for _ in range(num_trades)]
            
            # Calculate equity
            equity = initial_balance
            peak = equity
            max_dd = 0
            
            for pnl in sampled:
                equity += pnl
                
                if equity > peak:
                    peak = equity
                
                dd = (peak - equity) / peak * 100 if peak > 0 else 0
                if dd > max_dd:
                    max_dd = dd
            
            final_return = (equity - initial_balance) / initial_balance * 100
            simulation_results.append(final_return)
            max_drawdowns.append(max_dd)
        
        return self._calculate_statistics(simulation_results, max_drawdowns, initial_balance)
    
    def run_parameter_perturbation(
        self,
        backtest_function: callable,
        base_params: Dict[str, Any],
        param_ranges: Dict[str, Tuple[float, float]],
        initial_balance: float = 10000
    ) -> MonteCarloResult:
        """
        Run simulation with random parameter variations
        
        Args:
            backtest_function: Function that runs backtest with params
            base_params: Base parameter set
            param_ranges: Dict of param_name -> (min, max)
        """
        simulation_results = []
        max_drawdowns = []
        
        for _ in range(self.num_simulations):
            # Perturb parameters
            perturbed_params = base_params.copy()
            for param, (min_val, max_val) in param_ranges.items():
                perturbed_params[param] = random.uniform(min_val, max_val)
            
            # Run backtest with perturbed params
            result = backtest_function(**perturbed_params)
            
            if result:
                final_return = (result["final_balance"] - initial_balance) / initial_balance * 100
                simulation_results.append(final_return)
                max_drawdowns.append(result.get("max_drawdown", 0))
        
        if not simulation_results:
            return self._empty_result()
        
        return self._calculate_statistics(simulation_results, max_drawdowns, initial_balance)
    
    def _calculate_statistics(
        self,
        returns: List[float],
        max_drawdowns: List[float],
        initial_balance: float
    ) -> MonteCarloResult:
        """Calculate statistics from simulation results"""
        returns_array = np.array(returns)
        dd_array = np.array(max_drawdowns)
        
        # Basic statistics
        mean_return = np.mean(returns_array)
        median_return = np.median(returns_array)
        std_dev = np.std(returns_array)
        
        # Confidence intervals
        conf_95_lower = np.percentile(returns_array, 2.5)
        conf_95_upper = np.percentile(returns_array, 97.5)
        conf_99_lower = np.percentile(returns_array, 0.5)
        conf_99_upper = np.percentile(returns_array, 99.5)
        
        # Drawdown statistics
        dd_mean = np.mean(dd_array)
        dd_worst = np.max(dd_array)
        dd_best = np.min(dd_array)
        
        # Probabilities
        prob_profit = np.sum(returns_array > 0) / len(returns_array)
        prob_10 = np.sum(returns_array > 10) / len(returns_array)
        prob_20 = np.sum(returns_array > 20) / len(returns_array)
        prob_50 = np.sum(returns_array > 50) / len(returns_array)
        
        # Risk of ruin (probability of losing 50% or more)
        risk_of_ruin = np.sum(returns_array < -50) / len(returns_array)
        
        # Expected value
        expected_value = mean_return
        
        # Value at Risk (95%)
        var_95 = np.percentile(returns_array, 5)
        
        # Conditional VaR (expected loss if in worst 5%)
        losses_in_tail = returns_array[returns_array <= var_95]
        cvar_95 = np.mean(losses_in_tail) if len(losses_in_tail) > 0 else var_95
        
        return MonteCarloResult(
            simulations=len(returns),
            mean_return=mean_return,
            median_return=median_return,
            std_dev=std_dev,
            confidence_95_lower=conf_95_lower,
            confidence_95_upper=conf_95_upper,
            confidence_99_lower=conf_99_lower,
            confidence_99_upper=conf_99_upper,
            max_drawdown_mean=dd_mean,
            max_drawdown_worst=dd_worst,
            max_drawdown_best=dd_best,
            probability_profit=prob_profit,
            probability_10_percent=prob_10,
            probability_20_percent=prob_20,
            probability_50_percent=prob_50,
            risk_of_ruin=risk_of_ruin,
            expected_value=expected_value,
            value_at_risk_95=var_95,
            conditional_var_95=cvar_95
        )
    
    def _empty_result(self) -> MonteCarloResult:
        """Return empty result"""
        return MonteCarloResult(
            simulations=0, mean_return=0, median_return=0, std_dev=0,
            confidence_95_lower=0, confidence_95_upper=0,
            confidence_99_lower=0, confidence_99_upper=0,
            max_drawdown_mean=0, max_drawdown_worst=0, max_drawdown_best=0,
            probability_profit=0, probability_10_percent=0,
            probability_20_percent=0, probability_50_percent=0,
            risk_of_ruin=0, expected_value=0,
            value_at_risk_95=0, conditional_var_95=0
        )


class StressTester:
    """Stress test strategies against extreme market conditions"""
    
    @staticmethod
    def test_flash_crash(
        equity_curve: List[float],
        trades: List[Dict],
        crash_magnitude: float = 20.0
    ) -> StressTestResult:
        """
        Simulate flash crash scenario
        
        Args:
            equity_curve: Original equity curve
            trades: List of trades
            crash_magnitude: Percentage drop
        """
        # Find a random point to inject crash
        crash_point = len(equity_curve) // 2
        
        # Simulate impact
        impacted_equity = equity_curve.copy()
        for i in range(crash_point, len(impacted_equity)):
            impacted_equity[i] *= (1 - crash_magnitude / 100)
        
        final_return = (impacted_equity[-1] - equity_curve[0]) / equity_curve[0] * 100
        
        # Calculate max drawdown after crash
        peak = max(impacted_equity[:crash_point])
        trough = min(impacted_equity[crash_point:])
        max_dd = (peak - trough) / peak * 100
        
        # Recovery time
        recovery_time = 0
        for i in range(crash_point, len(impacted_equity)):
            if impacted_equity[i] >= peak:
                recovery_time = i - crash_point
                break
        
        survived = impacted_equity[-1] > equity_curve[0] * 0.5  # At least 50% of starting capital
        
        return StressTestResult(
            scenario="flash_crash",
            description=f"{crash_magnitude}% flash crash at mid-point",
            final_return=final_return,
            max_drawdown=max_dd,
            recovery_time=recovery_time,
            survived=survived,
            details={
                "crash_magnitude": crash_magnitude,
                "crash_point": crash_point,
                "equity_at_crash": impacted_equity[crash_point],
                "lowest_equity": trough
            }
        )
    
    @staticmethod
    def test_high_volatility(
        trades_pnl: List[float],
        initial_balance: float,
        volatility_multiplier: float = 2.0
    ) -> StressTestResult:
        """
        Simulate high volatility period
        
        Multiply trade results by volatility factor
        """
        stressed_pnl = [pnl * volatility_multiplier for pnl in trades_pnl]
        
        equity = initial_balance
        equity_curve = [equity]
        peak = equity
        max_dd = 0
        
        for pnl in stressed_pnl:
            equity += pnl
            equity_curve.append(equity)
            
            if equity > peak:
                peak = equity
            
            dd = (peak - equity) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        final_return = (equity - initial_balance) / initial_balance * 100
        survived = equity > initial_balance * 0.5
        
        return StressTestResult(
            scenario="high_volatility",
            description=f"{volatility_multiplier}x volatility increase",
            final_return=final_return,
            max_drawdown=max_dd,
            recovery_time=0,
            survived=survived,
            details={
                "volatility_multiplier": volatility_multiplier,
                "final_equity": equity
            }
        )
    
    @staticmethod
    def test_consecutive_losses(
        trades_pnl: List[float],
        initial_balance: float,
        max_consecutive_losses: int = 10
    ) -> StressTestResult:
        """
        Test worst-case consecutive losses
        
        Find worst consecutive loss streak and extend it
        """
        # Find consecutive losing trades
        losing_streaks = []
        current_streak = []
        
        for pnl in trades_pnl:
            if pnl < 0:
                current_streak.append(pnl)
            else:
                if current_streak:
                    losing_streaks.append(current_streak)
                    current_streak = []
        
        if not losing_streaks:
            return StressTestResult(
                scenario="consecutive_losses",
                description="No losing trades",
                final_return=0,
                max_drawdown=0,
                recovery_time=0,
                survived=True,
                details={}
            )
        
        # Find worst streak
        worst_streak = min(losing_streaks, key=lambda x: sum(x))
        
        # Extend to max consecutive
        extended_losses = worst_streak * (max_consecutive_losses // len(worst_streak) + 1)
        extended_losses = extended_losses[:max_consecutive_losses]
        
        # Calculate impact
        equity = initial_balance
        for loss in extended_losses:
            equity += loss
        
        total_loss = sum(extended_losses)
        drawdown = (initial_balance - equity) / initial_balance * 100
        
        return StressTestResult(
            scenario="consecutive_losses",
            description=f"{max_consecutive_losses} consecutive losses",
            final_return=(equity - initial_balance) / initial_balance * 100,
            max_drawdown=drawdown,
            recovery_time=0,
            survived=equity > 0,
            details={
                "consecutive_losses": max_consecutive_losses,
                "total_loss": total_loss,
                "remaining_capital": equity
            }
        )
    
    @staticmethod
    def test_commission_increase(
        trades_pnl: List[float],
        initial_balance: float,
        commission_increase_percent: float = 50.0
    ) -> StressTestResult:
        """
        Test impact of commission increase
        """
        # Assume average trade size
        avg_trade_size = initial_balance * 0.1
        base_commission = avg_trade_size * 0.001  # 0.1% commission
        increased_commission = base_commission * (1 + commission_increase_percent / 100)
        
        additional_cost_per_trade = increased_commission - base_commission
        
        # Apply to all trades
        stressed_pnl = [pnl - additional_cost_per_trade for pnl in trades_pnl]
        
        final_equity = initial_balance + sum(stressed_pnl)
        final_return = (final_equity - initial_balance) / initial_balance * 100
        
        return StressTestResult(
            scenario="commission_increase",
            description=f"{commission_increase_percent}% commission increase",
            final_return=final_return,
            max_drawdown=0,
            recovery_time=0,
            survived=final_equity > initial_balance * 0.5,
            details={
                "commission_increase": commission_increase_percent,
                "additional_cost_per_trade": additional_cost_per_trade,
                "total_additional_cost": additional_cost_per_trade * len(trades_pnl)
            }
        )
    
    @staticmethod
    def run_all_stress_tests(
        equity_curve: List[float],
        trades_pnl: List[float],
        initial_balance: float
    ) -> List[StressTestResult]:
        """Run all stress tests"""
        tests = []
        
        # Flash crash
        tests.append(StressTester.test_flash_crash(equity_curve, [], 20.0))
        tests.append(StressTester.test_flash_crash(equity_curve, [], 30.0))
        
        # High volatility
        tests.append(StressTester.test_high_volatility(trades_pnl, initial_balance, 2.0))
        tests.append(StressTester.test_high_volatility(trades_pnl, initial_balance, 3.0))
        
        # Consecutive losses
        tests.append(StressTester.test_consecutive_losses(trades_pnl, initial_balance, 10))
        tests.append(StressTester.test_consecutive_losses(trades_pnl, initial_balance, 15))
        
        # Commission increase
        tests.append(StressTester.test_commission_increase(trades_pnl, initial_balance, 50.0))
        tests.append(StressTester.test_commission_increase(trades_pnl, initial_balance, 100.0))
        
        return tests


class RobustnessAnalyzer:
    """Analyze strategy robustness"""
    
    @staticmethod
    def calculate_robustness_score(
        monte_carlo_result: MonteCarloResult,
        stress_test_results: List[StressTestResult]
    ) -> Dict[str, Any]:
        """
        Calculate overall robustness score (0-100)
        
        Factors:
        - Monte Carlo confidence
        - Stress test survival rate
        - Risk of ruin
        - Drawdown consistency
        """
        # Monte Carlo score (0-40 points)
        mc_score = 0
        
        # Probability of profit
        mc_score += monte_carlo_result.probability_profit * 15
        
        # Low risk of ruin
        mc_score += (1 - monte_carlo_result.risk_of_ruin) * 10
        
        # Positive expected value
        if monte_carlo_result.expected_value > 0:
            mc_score += 10
        
        # Low drawdown variance
        dd_consistency = 1 - (monte_carlo_result.max_drawdown_worst - monte_carlo_result.max_drawdown_best) / 100
        mc_score += max(0, dd_consistency) * 5
        
        # Stress test score (0-40 points)
        stress_score = 0
        
        if stress_test_results:
            survival_rate = sum(1 for t in stress_test_results if t.survived) / len(stress_test_results)
            stress_score = survival_rate * 40
        
        # Confidence interval width (0-20 points)
        ci_width = monte_carlo_result.confidence_95_upper - monte_carlo_result.confidence_95_lower
        ci_score = max(0, 20 - (ci_width / 10))  # Narrower CI = better
        
        total_score = min(100, mc_score + stress_score + ci_score)
        
        # Rating
        if total_score >= 80:
            rating = "Excellent"
        elif total_score >= 60:
            rating = "Good"
        elif total_score >= 40:
            rating = "Fair"
        else:
            rating = "Poor"
        
        return {
            "total_score": total_score,
            "rating": rating,
            "monte_carlo_score": mc_score,
            "stress_test_score": stress_score,
            "confidence_interval_score": ci_score,
            "components": {
                "probability_profit": monte_carlo_result.probability_profit,
                "risk_of_ruin": monte_carlo_result.risk_of_ruin,
                "expected_value": monte_carlo_result.expected_value,
                "survival_rate": sum(1 for t in stress_test_results if t.survived) / len(stress_test_results) if stress_test_results else 0
            }
        }


# Global instances
monte_carlo_simulator = MonteCarloSimulator()
stress_tester = StressTester()
robustness_analyzer = RobustnessAnalyzer()
