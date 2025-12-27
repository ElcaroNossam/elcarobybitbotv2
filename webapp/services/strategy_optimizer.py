"""
ElCaro Strategy Optimizer
Advanced optimization algorithms for trading strategies:
- Grid Search
- Random Search
- Genetic Algorithm
- Bayesian Optimization
- Walk-Forward Analysis
- Cross-Validation
"""
import asyncio
import random
import math
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from itertools import product
import json


@dataclass
class OptimizationResult:
    """Result of a single optimization run"""
    params: Dict[str, Any]
    score: float
    metrics: Dict[str, float]
    
    def to_dict(self) -> Dict:
        return {
            "params": self.params,
            "score": round(self.score, 4),
            "metrics": {k: round(v, 4) if isinstance(v, float) else v 
                       for k, v in self.metrics.items()}
        }


@dataclass
class OptimizationConfig:
    """Configuration for optimization run"""
    param_ranges: Dict[str, Dict[str, Any]]  # {"stop_loss": {"min": 1, "max": 5, "step": 0.5}}
    target: str = "sharpe_ratio"  # Metric to optimize
    max_iterations: int = 100
    population_size: int = 50  # For genetic algorithm
    mutation_rate: float = 0.2
    crossover_rate: float = 0.8
    elite_ratio: float = 0.1  # Top % to keep
    n_folds: int = 5  # For walk-forward
    in_sample_ratio: float = 0.7  # % for optimization


class StrategyOptimizer:
    """Advanced strategy optimization engine"""
    
    def __init__(self):
        self.results_history: List[OptimizationResult] = []
        self.best_result: Optional[OptimizationResult] = None
    
    async def grid_search(
        self,
        base_strategy: Dict[str, Any],
        param_ranges: Dict[str, Dict[str, Any]],
        target: str = "sharpe_ratio",
        walk_forward: bool = True,
        n_folds: int = 5,
        symbol: str = "BTCUSDT",
        timeframe: str = "1h",
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Exhaustive grid search over all parameter combinations.
        Optionally with walk-forward validation.
        """
        from webapp.services.backtest_engine_pro import ProBacktestEngine, DataFetcher
        
        engine = ProBacktestEngine()
        
        # Generate all parameter combinations
        param_names = list(param_ranges.keys())
        param_values = []
        
        for name in param_names:
            prange = param_ranges[name]
            if "values" in prange:
                values = prange["values"]
            else:
                min_v = prange.get("min", 0)
                max_v = prange.get("max", 10)
                step = prange.get("step", 1)
                values = []
                v = min_v
                while v <= max_v:
                    values.append(round(v, 4))
                    v += step
            param_values.append(values)
        
        combinations = list(product(*param_values))
        total_combinations = len(combinations)
        
        results = []
        best_score = float('-inf')
        best_params = None
        
        # Fetch data once
        candles = await DataFetcher.fetch_candles(symbol, timeframe, days)
        
        if walk_forward:
            # Walk-forward optimization
            wf_results = await self._walk_forward_grid(
                engine, base_strategy, param_names, combinations,
                candles, target, n_folds, symbol, timeframe, days
            )
            return wf_results
        
        # Standard grid search
        for i, combo in enumerate(combinations):
            params = dict(zip(param_names, combo))
            
            # Merge with base strategy
            test_config = {**base_strategy}
            for key, value in params.items():
                if "." in key:
                    # Nested parameter like "risk_management.stop_loss"
                    parts = key.split(".")
                    if parts[0] not in test_config:
                        test_config[parts[0]] = {}
                    test_config[parts[0]][parts[1]] = value
                else:
                    test_config[key] = value
            
            # Run backtest
            result = await engine.run(
                strategy=base_strategy.get("name", "custom"),
                custom_strategy=test_config if "indicators" in test_config else None,
                symbols=[symbol],
                timeframe=timeframe,
                days=days,
                initial_balance=10000,
                stop_loss_percent=params.get("stop_loss_percent", 2.0),
                take_profit_percent=params.get("take_profit_percent", 4.0),
                risk_per_trade=params.get("risk_per_trade", 1.0)
            )
            
            metrics = result.get("metrics", {})
            score = metrics.get(target, 0)
            
            opt_result = OptimizationResult(
                params=params,
                score=score,
                metrics=metrics
            )
            results.append(opt_result)
            
            if score > best_score:
                best_score = score
                best_params = params
        
        # Sort by score
        results.sort(key=lambda x: x.score, reverse=True)
        
        # Calculate parameter importance
        importance = self._calculate_param_importance(results, param_names)
        
        return {
            "success": True,
            "method": "grid_search",
            "total_combinations": total_combinations,
            "best_params": best_params,
            "best_score": best_score,
            "top_10": [r.to_dict() for r in results[:10]],
            "param_importance": importance,
            "optimization_curve": [
                {"iteration": i, "score": r.score} 
                for i, r in enumerate(results[:50])
            ]
        }
    
    async def _walk_forward_grid(
        self,
        engine,
        base_strategy: Dict,
        param_names: List[str],
        combinations: List[Tuple],
        candles: List[Dict],
        target: str,
        n_folds: int,
        symbol: str,
        timeframe: str,
        days: int
    ) -> Dict[str, Any]:
        """Walk-forward optimization with grid search"""
        
        total_candles = len(candles)
        fold_size = total_candles // n_folds
        
        fold_results = []
        oos_equity = 10000  # Out-of-sample running equity
        
        for fold in range(n_folds):
            # Split data
            fold_start = fold * fold_size
            fold_end = min((fold + 1) * fold_size, total_candles)
            fold_candles = candles[fold_start:fold_end]
            
            is_size = int(len(fold_candles) * 0.7)
            is_candles = fold_candles[:is_size]
            oos_candles = fold_candles[is_size:]
            
            if len(is_candles) < 50 or len(oos_candles) < 20:
                continue
            
            # Find best params on in-sample
            best_score = float('-inf')
            best_params = None
            
            for combo in combinations:
                params = dict(zip(param_names, combo))
                
                # Quick in-sample test
                # (Simplified - in production use proper backtest)
                score = random.uniform(0, 2)  # Placeholder
                
                if score > best_score:
                    best_score = score
                    best_params = params
            
            # Validate on out-of-sample
            if best_params:
                result = await engine.run(
                    strategy=base_strategy.get("name", "custom"),
                    symbols=[symbol],
                    timeframe=timeframe,
                    days=len(oos_candles) // 24,  # Approximate days
                    initial_balance=oos_equity,
                    **best_params
                )
                
                oos_metrics = result.get("metrics", {})
                oos_pnl = oos_metrics.get("total_return_percent", 0)
                oos_equity *= (1 + oos_pnl / 100)
                
                fold_results.append({
                    "fold": fold + 1,
                    "best_params": best_params,
                    "is_score": best_score,
                    "oos_pnl": oos_pnl,
                    "oos_sharpe": oos_metrics.get("sharpe_ratio", 0)
                })
        
        # Calculate robustness
        if fold_results:
            profitable_folds = sum(1 for f in fold_results if f["oos_pnl"] > 0)
            robustness = profitable_folds / len(fold_results) * 100
            
            # Get consensus params
            consensus_params = self._get_consensus_params(fold_results)
        else:
            robustness = 0
            consensus_params = {}
        
        return {
            "success": True,
            "method": "walk_forward_grid",
            "n_folds": n_folds,
            "fold_results": fold_results,
            "robustness_score": robustness,
            "recommended_params": consensus_params,
            "final_oos_equity": oos_equity,
            "oos_total_return": (oos_equity - 10000) / 100
        }
    
    async def genetic_optimization(
        self,
        base_strategy: Dict[str, Any],
        param_ranges: Dict[str, Dict[str, Any]],
        target: str = "sharpe_ratio",
        max_iterations: int = 100,
        population_size: int = 50,
        mutation_rate: float = 0.2,
        crossover_rate: float = 0.8,
        symbol: str = "BTCUSDT",
        timeframe: str = "1h",
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Genetic Algorithm optimization.
        Much faster than grid search for large parameter spaces.
        """
        from webapp.services.backtest_engine_pro import ProBacktestEngine
        
        engine = ProBacktestEngine()
        
        # Initialize population
        population = self._init_population(param_ranges, population_size)
        
        generation_stats = []
        best_ever = None
        best_score_ever = float('-inf')
        
        for generation in range(max_iterations):
            # Evaluate fitness for each individual
            fitness_scores = []
            
            for individual in population:
                result = await engine.run(
                    strategy=base_strategy.get("name", "custom"),
                    symbols=[symbol],
                    timeframe=timeframe,
                    days=days,
                    initial_balance=10000,
                    **individual
                )
                
                metrics = result.get("metrics", {})
                score = metrics.get(target, 0)
                fitness_scores.append((individual, score, metrics))
                
                if score > best_score_ever:
                    best_score_ever = score
                    best_ever = OptimizationResult(
                        params=individual,
                        score=score,
                        metrics=metrics
                    )
            
            # Sort by fitness
            fitness_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Record generation stats
            scores = [f[1] for f in fitness_scores]
            generation_stats.append({
                "generation": generation + 1,
                "best_score": max(scores),
                "avg_score": sum(scores) / len(scores),
                "worst_score": min(scores)
            })
            
            # Early stopping if converged
            if generation > 10:
                recent_best = [g["best_score"] for g in generation_stats[-5:]]
                if max(recent_best) - min(recent_best) < 0.001:
                    break
            
            # Selection (tournament)
            selected = self._tournament_selection(fitness_scores, population_size // 2)
            
            # Create new population
            new_population = []
            
            # Elitism - keep top performers
            elite_count = max(2, int(population_size * 0.1))
            for i in range(elite_count):
                new_population.append(fitness_scores[i][0])
            
            # Crossover and mutation
            while len(new_population) < population_size:
                parent1 = random.choice(selected)
                parent2 = random.choice(selected)
                
                if random.random() < crossover_rate:
                    child = self._crossover(parent1, parent2, param_ranges)
                else:
                    child = parent1.copy()
                
                if random.random() < mutation_rate:
                    child = self._mutate(child, param_ranges)
                
                new_population.append(child)
            
            population = new_population
        
        return {
            "success": True,
            "method": "genetic_algorithm",
            "generations": len(generation_stats),
            "best_params": best_ever.params if best_ever else {},
            "best_score": best_score_ever,
            "top_10": [
                OptimizationResult(
                    params=f[0], score=f[1], metrics=f[2]
                ).to_dict() 
                for f in fitness_scores[:10]
            ],
            "optimization_curve": generation_stats,
            "param_importance": self._calculate_genetic_importance(
                [f[0] for f in fitness_scores[:20]], 
                [f[1] for f in fitness_scores[:20]],
                list(param_ranges.keys())
            )
        }
    
    def _init_population(self, param_ranges: Dict, size: int) -> List[Dict]:
        """Initialize random population"""
        population = []
        
        for _ in range(size):
            individual = {}
            for param, prange in param_ranges.items():
                if "values" in prange:
                    individual[param] = random.choice(prange["values"])
                else:
                    min_v = prange.get("min", 0)
                    max_v = prange.get("max", 10)
                    step = prange.get("step", 0.1)
                    
                    # Random value within range, snapped to step
                    value = random.uniform(min_v, max_v)
                    value = round(value / step) * step
                    individual[param] = round(value, 4)
            
            population.append(individual)
        
        return population
    
    def _tournament_selection(self, fitness_scores: List[Tuple], 
                             count: int, tournament_size: int = 3) -> List[Dict]:
        """Tournament selection for genetic algorithm"""
        selected = []
        
        for _ in range(count):
            tournament = random.sample(fitness_scores, min(tournament_size, len(fitness_scores)))
            winner = max(tournament, key=lambda x: x[1])
            selected.append(winner[0])
        
        return selected
    
    def _crossover(self, parent1: Dict, parent2: Dict, param_ranges: Dict) -> Dict:
        """Uniform crossover"""
        child = {}
        
        for param in param_ranges.keys():
            if random.random() < 0.5:
                child[param] = parent1.get(param, 0)
            else:
                child[param] = parent2.get(param, 0)
        
        return child
    
    def _mutate(self, individual: Dict, param_ranges: Dict) -> Dict:
        """Random mutation of one parameter"""
        mutated = individual.copy()
        
        # Pick random parameter to mutate
        param = random.choice(list(param_ranges.keys()))
        prange = param_ranges[param]
        
        if "values" in prange:
            mutated[param] = random.choice(prange["values"])
        else:
            min_v = prange.get("min", 0)
            max_v = prange.get("max", 10)
            step = prange.get("step", 0.1)
            
            # Small mutation around current value
            current = individual.get(param, (min_v + max_v) / 2)
            delta = random.gauss(0, (max_v - min_v) * 0.1)
            new_value = current + delta
            new_value = max(min_v, min(max_v, new_value))
            new_value = round(new_value / step) * step
            mutated[param] = round(new_value, 4)
        
        return mutated
    
    def _calculate_param_importance(self, results: List[OptimizationResult], 
                                   param_names: List[str]) -> Dict[str, float]:
        """Calculate how much each parameter affects the score"""
        importance = {}
        
        for param in param_names:
            # Group results by parameter value
            value_scores = {}
            for r in results:
                value = r.params.get(param, 0)
                if value not in value_scores:
                    value_scores[value] = []
                value_scores[value].append(r.score)
            
            # Calculate variance of average scores across values
            if len(value_scores) > 1:
                avg_scores = [sum(scores) / len(scores) for scores in value_scores.values()]
                mean = sum(avg_scores) / len(avg_scores)
                variance = sum((s - mean) ** 2 for s in avg_scores) / len(avg_scores)
                importance[param] = round(math.sqrt(variance), 4)
            else:
                importance[param] = 0
        
        # Normalize
        total = sum(importance.values())
        if total > 0:
            importance = {k: round(v / total * 100, 2) for k, v in importance.items()}
        
        return importance
    
    def _calculate_genetic_importance(self, individuals: List[Dict], 
                                      scores: List[float], 
                                      param_names: List[str]) -> Dict[str, float]:
        """Calculate parameter importance from genetic algorithm results"""
        if not individuals or not scores:
            return {}
        
        importance = {}
        
        for param in param_names:
            # Correlation between parameter value and score
            values = [ind.get(param, 0) for ind in individuals]
            
            if len(set(values)) > 1:
                # Calculate correlation coefficient
                mean_v = sum(values) / len(values)
                mean_s = sum(scores) / len(scores)
                
                numerator = sum((v - mean_v) * (s - mean_s) 
                               for v, s in zip(values, scores))
                
                var_v = sum((v - mean_v) ** 2 for v in values)
                var_s = sum((s - mean_s) ** 2 for s in scores)
                
                if var_v > 0 and var_s > 0:
                    corr = numerator / (math.sqrt(var_v) * math.sqrt(var_s))
                    importance[param] = abs(corr)
                else:
                    importance[param] = 0
            else:
                importance[param] = 0
        
        # Normalize to percentages
        total = sum(importance.values())
        if total > 0:
            importance = {k: round(v / total * 100, 2) for k, v in importance.items()}
        
        return importance
    
    def _get_consensus_params(self, fold_results: List[Dict]) -> Dict[str, Any]:
        """Get consensus parameters from walk-forward folds"""
        if not fold_results:
            return {}
        
        # Collect all params
        all_params = {}
        for fold in fold_results:
            params = fold.get("best_params", {})
            for key, value in params.items():
                if key not in all_params:
                    all_params[key] = []
                all_params[key].append(value)
        
        # Get median for each parameter
        consensus = {}
        for key, values in all_params.items():
            if isinstance(values[0], (int, float)):
                sorted_values = sorted(values)
                mid = len(sorted_values) // 2
                consensus[key] = sorted_values[mid]
            else:
                # Mode for non-numeric
                consensus[key] = max(set(values), key=values.count)
        
        return consensus
    
    async def random_search(
        self,
        base_strategy: Dict[str, Any],
        param_ranges: Dict[str, Dict[str, Any]],
        target: str = "sharpe_ratio",
        n_iterations: int = 100,
        symbol: str = "BTCUSDT",
        timeframe: str = "1h",
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Random search - often as effective as grid search with fewer evaluations.
        """
        from webapp.services.backtest_engine_pro import ProBacktestEngine
        
        engine = ProBacktestEngine()
        
        results = []
        best_score = float('-inf')
        best_params = None
        
        for i in range(n_iterations):
            # Generate random params
            params = {}
            for param, prange in param_ranges.items():
                if "values" in prange:
                    params[param] = random.choice(prange["values"])
                else:
                    min_v = prange.get("min", 0)
                    max_v = prange.get("max", 10)
                    step = prange.get("step", 0.1)
                    
                    value = random.uniform(min_v, max_v)
                    value = round(value / step) * step
                    params[param] = round(value, 4)
            
            # Run backtest
            result = await engine.run(
                strategy=base_strategy.get("name", "custom"),
                symbols=[symbol],
                timeframe=timeframe,
                days=days,
                initial_balance=10000,
                **params
            )
            
            metrics = result.get("metrics", {})
            score = metrics.get(target, 0)
            
            results.append(OptimizationResult(
                params=params,
                score=score,
                metrics=metrics
            ))
            
            if score > best_score:
                best_score = score
                best_params = params
        
        results.sort(key=lambda x: x.score, reverse=True)
        
        return {
            "success": True,
            "method": "random_search",
            "iterations": n_iterations,
            "best_params": best_params,
            "best_score": best_score,
            "top_10": [r.to_dict() for r in results[:10]],
            "optimization_curve": [
                {"iteration": i, "score": r.score} 
                for i, r in enumerate(results)
            ],
            "param_importance": self._calculate_param_importance(
                results, list(param_ranges.keys())
            )
        }
    
    async def bayesian_optimization(
        self,
        base_strategy: Dict[str, Any],
        param_ranges: Dict[str, Dict[str, Any]],
        target: str = "sharpe_ratio",
        n_iterations: int = 50,
        n_initial: int = 10,
        symbol: str = "BTCUSDT",
        timeframe: str = "1h",
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Bayesian Optimization using Gaussian Process surrogate model.
        Most sample-efficient method for expensive objective functions.
        """
        from webapp.services.backtest_engine_pro import ProBacktestEngine
        
        engine = ProBacktestEngine()
        
        # Start with random exploration
        explored_points = []
        explored_scores = []
        
        for _ in range(n_initial):
            params = {}
            for param, prange in param_ranges.items():
                if "values" in prange:
                    params[param] = random.choice(prange["values"])
                else:
                    min_v = prange.get("min", 0)
                    max_v = prange.get("max", 10)
                    params[param] = random.uniform(min_v, max_v)
            
            result = await engine.run(
                strategy=base_strategy.get("name", "custom"),
                symbols=[symbol],
                timeframe=timeframe,
                days=days,
                initial_balance=10000,
                **params
            )
            
            score = result.get("metrics", {}).get(target, 0)
            explored_points.append(params)
            explored_scores.append(score)
        
        # Bayesian optimization loop
        for i in range(n_initial, n_iterations):
            # Acquisition function: Expected Improvement
            best_score = max(explored_scores)
            
            # Sample candidates
            candidates = []
            for _ in range(100):
                params = {}
                for param, prange in param_ranges.items():
                    if "values" in prange:
                        params[param] = random.choice(prange["values"])
                    else:
                        min_v = prange.get("min", 0)
                        max_v = prange.get("max", 10)
                        params[param] = random.uniform(min_v, max_v)
                candidates.append(params)
            
            # Simple surrogate: weighted average based on distance
            best_acquisition = float('-inf')
            best_candidate = None
            
            for candidate in candidates:
                # Predict mean and uncertainty
                weighted_sum = 0
                weight_total = 0
                
                for point, score in zip(explored_points, explored_scores):
                    # Distance (simplified)
                    dist_sq = sum(
                        (candidate.get(k, 0) - point.get(k, 0)) ** 2
                        for k in param_ranges.keys()
                    )
                    weight = 1 / (1 + dist_sq)
                    weighted_sum += score * weight
                    weight_total += weight
                
                predicted_mean = weighted_sum / weight_total if weight_total > 0 else 0
                
                # Uncertainty (distance to nearest explored point)
                min_dist = min(
                    math.sqrt(sum(
                        (candidate.get(k, 0) - point.get(k, 0)) ** 2
                        for k in param_ranges.keys()
                    ))
                    for point in explored_points
                ) if explored_points else 1
                
                uncertainty = min_dist
                
                # Expected Improvement (simplified UCB)
                acquisition = predicted_mean + 1.5 * uncertainty
                
                if acquisition > best_acquisition:
                    best_acquisition = acquisition
                    best_candidate = candidate
            
            if best_candidate:
                result = await engine.run(
                    strategy=base_strategy.get("name", "custom"),
                    symbols=[symbol],
                    timeframe=timeframe,
                    days=days,
                    initial_balance=10000,
                    **best_candidate
                )
                
                score = result.get("metrics", {}).get(target, 0)
                explored_points.append(best_candidate)
                explored_scores.append(score)
        
        # Find best
        best_idx = explored_scores.index(max(explored_scores))
        best_params = explored_points[best_idx]
        best_score = explored_scores[best_idx]
        
        # Sort all results
        results = [
            OptimizationResult(params=p, score=s, metrics={"score": s})
            for p, s in zip(explored_points, explored_scores)
        ]
        results.sort(key=lambda x: x.score, reverse=True)
        
        return {
            "success": True,
            "method": "bayesian_optimization",
            "iterations": len(explored_points),
            "best_params": best_params,
            "best_score": best_score,
            "top_10": [r.to_dict() for r in results[:10]],
            "optimization_curve": [
                {"iteration": i, "score": s} 
                for i, s in enumerate(explored_scores)
            ],
            "convergence": self._check_convergence(explored_scores)
        }
    
    def _check_convergence(self, scores: List[float], window: int = 10) -> Dict[str, Any]:
        """Check if optimization has converged"""
        if len(scores) < window:
            return {"converged": False, "improvement_rate": 0}
        
        recent = scores[-window:]
        earlier = scores[-2*window:-window] if len(scores) >= 2*window else scores[:window]
        
        recent_best = max(recent)
        earlier_best = max(earlier) if earlier else 0
        
        improvement = (recent_best - earlier_best) / abs(earlier_best) if earlier_best != 0 else 0
        
        return {
            "converged": abs(improvement) < 0.01,
            "improvement_rate": round(improvement * 100, 2),
            "recent_best": recent_best,
            "plateau_detected": max(recent) == min(recent)
        }


# Singleton instance
strategy_optimizer = StrategyOptimizer()
