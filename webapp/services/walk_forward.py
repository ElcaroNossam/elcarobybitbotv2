"""
ElCaro Walk-Forward Analysis & Parameter Optimization
Prevent overfitting with rolling optimization and validation

Features:
- Walk-forward optimization
- Anchored vs Rolling window
- Parameter grid search
- Genetic algorithm optimization
- Overfitting detection
- Efficiency metrics
- Out-of-sample validation
"""
import asyncio
import ast
import numpy as np
from typing import List, Dict, Any, Tuple, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from itertools import product
import random


@dataclass
class OptimizationPeriod:
    """Single optimization period"""
    train_start: datetime
    train_end: datetime
    test_start: datetime
    test_end: datetime
    train_candles: List[Dict]
    test_candles: List[Dict]


@dataclass
class ParameterSet:
    """Set of strategy parameters"""
    params: Dict[str, Any]
    train_return: float = 0.0
    test_return: float = 0.0
    train_sharpe: float = 0.0
    test_sharpe: float = 0.0
    train_max_dd: float = 0.0
    test_max_dd: float = 0.0
    efficiency_ratio: float = 0.0  # test_return / train_return
    robustness_score: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "params": self.params,
            "train_metrics": {
                "return": self.train_return,
                "sharpe": self.train_sharpe,
                "max_drawdown": self.train_max_dd
            },
            "test_metrics": {
                "return": self.test_return,
                "sharpe": self.test_sharpe,
                "max_drawdown": self.test_max_dd
            },
            "efficiency_ratio": self.efficiency_ratio,
            "robustness_score": self.robustness_score
        }


@dataclass
class WalkForwardResult:
    """Complete walk-forward analysis result"""
    periods: int
    best_params: Dict[str, Any]
    avg_train_return: float
    avg_test_return: float
    total_test_return: float
    efficiency_ratio: float
    overfitting_detected: bool
    stability_score: float
    period_results: List[ParameterSet]
    
    def to_dict(self) -> Dict:
        return {
            "periods": self.periods,
            "best_params": self.best_params,
            "performance": {
                "avg_train_return": self.avg_train_return,
                "avg_test_return": self.avg_test_return,
                "total_test_return": self.total_test_return,
                "efficiency_ratio": self.efficiency_ratio
            },
            "analysis": {
                "overfitting_detected": self.overfitting_detected,
                "stability_score": self.stability_score
            },
            "period_results": [p.to_dict() for p in self.period_results]
        }


class WalkForwardOptimizer:
    """Walk-forward optimization engine"""
    
    def __init__(
        self,
        train_period_days: int = 90,
        test_period_days: int = 30,
        step_days: int = 30,
        window_type: str = "rolling"  # 'rolling' or 'anchored'
    ):
        """
        Initialize optimizer
        
        Args:
            train_period_days: Training period length
            test_period_days: Testing (out-of-sample) period length
            step_days: Days to step forward between periods
            window_type: 'rolling' (fixed window) or 'anchored' (expanding window)
        """
        self.train_period_days = train_period_days
        self.test_period_days = test_period_days
        self.step_days = step_days
        self.window_type = window_type
    
    def split_data(
        self,
        candles: List[Dict],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[OptimizationPeriod]:
        """
        Split data into train/test periods
        
        Returns:
            List of optimization periods
        """
        if not candles:
            return []
        
        # Parse dates
        first_date = datetime.fromisoformat(candles[0]["time"].replace('Z', '+00:00'))
        last_date = datetime.fromisoformat(candles[-1]["time"].replace('Z', '+00:00'))
        
        start = start_date if start_date else first_date
        end = end_date if end_date else last_date
        
        periods = []
        current_start = start
        anchor_start = start  # For anchored window
        
        while True:
            # Calculate period boundaries
            train_end = current_start + timedelta(days=self.train_period_days)
            test_start = train_end
            test_end = test_start + timedelta(days=self.test_period_days)
            
            if test_end > end:
                break
            
            # Use anchor start for anchored window
            if self.window_type == "anchored":
                train_start = anchor_start
            else:
                train_start = current_start
            
            # Extract candles for this period
            train_candles = [c for c in candles if train_start <= datetime.fromisoformat(c["time"].replace('Z', '+00:00')) < train_end]
            test_candles = [c for c in candles if test_start <= datetime.fromisoformat(c["time"].replace('Z', '+00:00')) < test_end]
            
            if len(train_candles) >= 50 and len(test_candles) >= 10:
                periods.append(OptimizationPeriod(
                    train_start=train_start,
                    train_end=train_end,
                    test_start=test_start,
                    test_end=test_end,
                    train_candles=train_candles,
                    test_candles=test_candles
                ))
            
            # Step forward
            current_start += timedelta(days=self.step_days)
        
        return periods
    
    async def optimize_period(
        self,
        period: OptimizationPeriod,
        param_grid: Dict[str, List[Any]],
        backtest_function: Callable
    ) -> ParameterSet:
        """
        Optimize parameters for a single period
        
        Args:
            period: Optimization period
            param_grid: Dict of param_name -> list of values to try
            backtest_function: Async function(candles, **params) -> backtest_result
        
        Returns:
            Best parameter set
        """
        # Generate all parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        all_combinations = list(product(*param_values))
        
        # Test each combination on training data
        best_params = None
        best_score = -np.inf
        best_train_result = None
        
        for combination in all_combinations:
            params = dict(zip(param_names, combination))
            
            # Run backtest on training data
            train_result = await backtest_function(period.train_candles, **params)
            
            if not train_result:
                continue
            
            # Score based on Sharpe ratio (or other metric)
            score = train_result.get("sharpe_ratio", 0)
            
            if score > best_score:
                best_score = score
                best_params = params
                best_train_result = train_result
        
        if not best_params:
            return ParameterSet(params={}, train_return=0, test_return=0)
        
        # Test best params on out-of-sample data
        test_result = await backtest_function(period.test_candles, **best_params)
        
        # Calculate efficiency ratio
        train_return = best_train_result.get("total_pnl_percent", 0)
        test_return = test_result.get("total_pnl_percent", 0) if test_result else 0
        
        efficiency = test_return / train_return if train_return != 0 else 0
        
        # Robustness score (penalize overfitting)
        if efficiency < 0.5:
            robustness = 0
        elif efficiency > 1.5:
            robustness = 50  # Test performed way better (lucky)
        else:
            robustness = 100 * efficiency
        
        return ParameterSet(
            params=best_params,
            train_return=train_return,
            test_return=test_return,
            train_sharpe=best_train_result.get("sharpe_ratio", 0),
            test_sharpe=test_result.get("sharpe_ratio", 0) if test_result else 0,
            train_max_dd=best_train_result.get("max_drawdown_percent", 0),
            test_max_dd=test_result.get("max_drawdown_percent", 0) if test_result else 0,
            efficiency_ratio=efficiency,
            robustness_score=robustness
        )
    
    async def run_walk_forward(
        self,
        candles: List[Dict],
        param_grid: Dict[str, List[Any]],
        backtest_function: Callable
    ) -> WalkForwardResult:
        """
        Run complete walk-forward analysis
        
        Returns:
            Walk-forward result with all periods
        """
        # Split data
        periods = self.split_data(candles)
        
        if not periods:
            return WalkForwardResult(
                periods=0,
                best_params={},
                avg_train_return=0,
                avg_test_return=0,
                total_test_return=0,
                efficiency_ratio=0,
                overfitting_detected=False,
                stability_score=0,
                period_results=[]
            )
        
        # Optimize each period
        period_results = []
        
        for period in periods:
            result = await self.optimize_period(period, param_grid, backtest_function)
            period_results.append(result)
        
        # Analyze results
        train_returns = [p.train_return for p in period_results]
        test_returns = [p.test_return for p in period_results]
        
        avg_train_return = np.mean(train_returns)
        avg_test_return = np.mean(test_returns)
        total_test_return = sum(test_returns)
        
        overall_efficiency = avg_test_return / avg_train_return if avg_train_return != 0 else 0
        
        # Overfitting detection
        overfitting_detected = overall_efficiency < 0.5
        
        # Stability score (consistency across periods)
        test_return_std = np.std(test_returns)
        stability_score = max(0, 100 - (test_return_std * 10))
        
        # Find most common best parameters
        param_frequency = {}
        for result in period_results:
            param_key = str(sorted(result.params.items()))
            param_frequency[param_key] = param_frequency.get(param_key, 0) + 1
        
        most_common_params = max(param_frequency.items(), key=lambda x: x[1])[0] if param_frequency else "[]"
        best_params = ast.literal_eval(most_common_params)  # Safe: only parses literals
        
        return WalkForwardResult(
            periods=len(periods),
            best_params=dict(best_params) if isinstance(best_params, list) else best_params,
            avg_train_return=avg_train_return,
            avg_test_return=avg_test_return,
            total_test_return=total_test_return,
            efficiency_ratio=overall_efficiency,
            overfitting_detected=overfitting_detected,
            stability_score=stability_score,
            period_results=period_results
        )


class GeneticOptimizer:
    """Genetic algorithm for parameter optimization"""
    
    def __init__(
        self,
        population_size: int = 50,
        generations: int = 20,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7
    ):
        """
        Initialize genetic optimizer
        
        Args:
            population_size: Number of individuals in population
            generations: Number of generations to evolve
            mutation_rate: Probability of mutation
            crossover_rate: Probability of crossover
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
    
    def generate_individual(self, param_ranges: Dict[str, Tuple[Any, Any]]) -> Dict[str, Any]:
        """Generate random parameter set"""
        individual = {}
        
        for param, (min_val, max_val) in param_ranges.items():
            if isinstance(min_val, int) and isinstance(max_val, int):
                individual[param] = random.randint(min_val, max_val)
            elif isinstance(min_val, float) and isinstance(max_val, float):
                individual[param] = random.uniform(min_val, max_val)
            else:
                # For discrete choices
                choices = list(range(min_val, max_val + 1)) if isinstance(min_val, int) else [min_val, max_val]
                individual[param] = random.choice(choices)
        
        return individual
    
    def crossover(
        self,
        parent1: Dict[str, Any],
        parent2: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Crossover two parents"""
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        
        # Single-point crossover
        params = list(parent1.keys())
        crossover_point = random.randint(1, len(params) - 1)
        
        child1 = {}
        child2 = {}
        
        for i, param in enumerate(params):
            if i < crossover_point:
                child1[param] = parent1[param]
                child2[param] = parent2[param]
            else:
                child1[param] = parent2[param]
                child2[param] = parent1[param]
        
        return child1, child2
    
    def mutate(
        self,
        individual: Dict[str, Any],
        param_ranges: Dict[str, Tuple[Any, Any]]
    ) -> Dict[str, Any]:
        """Mutate individual"""
        mutated = individual.copy()
        
        for param, value in mutated.items():
            if random.random() < self.mutation_rate:
                min_val, max_val = param_ranges[param]
                
                if isinstance(min_val, int) and isinstance(max_val, int):
                    mutated[param] = random.randint(min_val, max_val)
                elif isinstance(min_val, float) and isinstance(max_val, float):
                    # Gaussian mutation
                    sigma = (max_val - min_val) * 0.1
                    new_val = value + random.gauss(0, sigma)
                    mutated[param] = max(min_val, min(max_val, new_val))
        
        return mutated
    
    async def optimize(
        self,
        candles: List[Dict],
        param_ranges: Dict[str, Tuple[Any, Any]],
        fitness_function: Callable,
        maximize: bool = True
    ) -> Dict[str, Any]:
        """
        Run genetic algorithm optimization
        
        Args:
            candles: Historical data
            param_ranges: Dict of param -> (min, max) ranges
            fitness_function: Async function(candles, **params) -> fitness_score
            maximize: True to maximize fitness, False to minimize
        
        Returns:
            Best parameter set found
        """
        # Initialize population
        population = [self.generate_individual(param_ranges) for _ in range(self.population_size)]
        
        best_individual = None
        best_fitness = -np.inf if maximize else np.inf
        
        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = []
            
            for individual in population:
                score = await fitness_function(candles, **individual)
                fitness_scores.append(score)
                
                # Track best
                if maximize and score > best_fitness:
                    best_fitness = score
                    best_individual = individual.copy()
                elif not maximize and score < best_fitness:
                    best_fitness = score
                    best_individual = individual.copy()
            
            # Selection (tournament selection)
            selected = []
            for _ in range(self.population_size):
                tournament = random.sample(list(zip(population, fitness_scores)), k=3)
                if maximize:
                    winner = max(tournament, key=lambda x: x[1])[0]
                else:
                    winner = min(tournament, key=lambda x: x[1])[0]
                selected.append(winner)
            
            # Crossover and mutation
            next_generation = []
            
            for i in range(0, self.population_size, 2):
                parent1 = selected[i]
                parent2 = selected[i + 1] if i + 1 < len(selected) else selected[0]
                
                child1, child2 = self.crossover(parent1, parent2)
                child1 = self.mutate(child1, param_ranges)
                child2 = self.mutate(child2, param_ranges)
                
                next_generation.extend([child1, child2])
            
            population = next_generation[:self.population_size]
        
        return best_individual


# Global instances
walk_forward_optimizer = WalkForwardOptimizer()
genetic_optimizer = GeneticOptimizer()
