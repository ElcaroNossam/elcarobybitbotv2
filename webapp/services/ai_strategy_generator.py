"""
ElCaro AI Strategy Generator
Uses AI/ML techniques to generate and optimize trading strategies:
- GPT-powered strategy generation (if API key available)
- Rule-based intelligent generation
- Market regime adaptation
- Multi-indicator combinations
- Automatic parameter tuning
"""
import random
import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import asyncio
import os


@dataclass
class GeneratedStrategy:
    """AI-generated strategy configuration"""
    name: str
    description: str
    indicators: List[Dict[str, Any]]
    entry_rules: List[Dict[str, Any]]
    exit_rules: List[Dict[str, Any]]
    risk_management: Dict[str, Any]
    expected_win_rate: float
    expected_sharpe: float
    complexity: str  # beginner, intermediate, advanced
    market_regime: str  # trending, ranging, volatile
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "indicators": self.indicators,
            "entry_rules": self.entry_rules,
            "exit_rules": self.exit_rules,
            "risk_management": self.risk_management,
            "expected_win_rate": self.expected_win_rate,
            "expected_sharpe": self.expected_sharpe,
            "complexity": self.complexity,
            "market_regime": self.market_regime
        }


class AIStrategyGenerator:
    """AI-powered trading strategy generator"""
    
    # Indicator configurations by category
    TREND_INDICATORS = [
        {"type": "ema", "params": {"period": 20}, "alias": "ema_20"},
        {"type": "ema", "params": {"period": 50}, "alias": "ema_50"},
        {"type": "ema", "params": {"period": 200}, "alias": "ema_200"},
        {"type": "sma", "params": {"period": 50}, "alias": "sma_50"},
        {"type": "supertrend", "params": {"period": 10, "multiplier": 3.0}},
        {"type": "parabolic_sar", "params": {"af_start": 0.02, "af_max": 0.2}},
        {"type": "adx", "params": {"period": 14}, "alias": "adx"},
    ]
    
    MOMENTUM_INDICATORS = [
        {"type": "rsi", "params": {"period": 14}, "alias": "rsi"},
        {"type": "rsi", "params": {"period": 7}, "alias": "rsi_7"},
        {"type": "stochastic", "params": {"k_period": 14, "d_period": 3}},
        {"type": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}},
        {"type": "roc", "params": {"period": 10}, "alias": "roc"},
        {"type": "cci", "params": {"period": 20}, "alias": "cci"},
        {"type": "williams_r", "params": {"period": 14}, "alias": "williams_r"},
    ]
    
    VOLATILITY_INDICATORS = [
        {"type": "bollinger_bands", "params": {"period": 20, "std_dev": 2.0}},
        {"type": "keltner_channels", "params": {"ema_period": 20, "atr_period": 10, "multiplier": 2.0}},
        {"type": "atr", "params": {"period": 14}, "alias": "atr"},
        {"type": "donchian_channels", "params": {"period": 20}},
    ]
    
    VOLUME_INDICATORS = [
        {"type": "obv", "params": {}},
        {"type": "vwap", "params": {}},
        {"type": "mfi", "params": {"period": 14}, "alias": "mfi"},
        {"type": "volume_sma", "params": {"period": 20}, "alias": "volume_sma"},
    ]
    
    # Strategy templates for different market conditions
    STRATEGY_TEMPLATES = {
        "trending": {
            "indicators": ["trend", "momentum"],
            "entry_logic": "trend_confirmation",
            "exit_logic": "trend_reversal",
            "risk_reward": 3.0
        },
        "ranging": {
            "indicators": ["momentum", "volatility"],
            "entry_logic": "mean_reversion",
            "exit_logic": "overbought_oversold",
            "risk_reward": 1.5
        },
        "volatile": {
            "indicators": ["volatility", "volume"],
            "entry_logic": "breakout",
            "exit_logic": "volatility_contraction",
            "risk_reward": 2.0
        }
    }
    
    def __init__(self):
        self.reasoning: List[str] = []
        self.openai_key = os.environ.get("OPENAI_API_KEY")
    
    def get_reasoning(self) -> List[str]:
        """Get the AI reasoning for generated strategies"""
        return self.reasoning
    
    async def generate(
        self,
        target_market: str = "crypto_volatile",
        risk_profile: str = "moderate",
        preferred_timeframes: List[str] = ["1h", "4h"],
        indicators_to_use: Optional[List[str]] = None,
        avoid_indicators: Optional[List[str]] = None,
        min_win_rate: float = 50,
        max_drawdown: float = 20,
        symbols_to_test: List[str] = ["BTCUSDT", "ETHUSDT"],
        n_strategies: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate optimized trading strategies based on requirements.
        """
        self.reasoning = []
        strategies = []
        
        # Determine market regime focus
        regime = self._determine_regime(target_market)
        self.reasoning.append(f"Target market '{target_market}' mapped to regime: {regime}")
        
        # Determine risk parameters
        risk_params = self._get_risk_params(risk_profile, max_drawdown)
        self.reasoning.append(f"Risk profile '{risk_profile}' configured: SL={risk_params['stop_loss']}%, TP={risk_params['take_profit']}%")
        
        # Generate multiple strategy variations
        for i in range(n_strategies):
            strategy = await self._generate_single_strategy(
                regime=regime,
                risk_params=risk_params,
                timeframe=preferred_timeframes[0] if preferred_timeframes else "1h",
                indicators_to_use=indicators_to_use,
                avoid_indicators=avoid_indicators,
                min_win_rate=min_win_rate,
                strategy_num=i + 1
            )
            
            if strategy:
                # Backtest to get expected performance
                perf = await self._quick_backtest(
                    strategy, symbols_to_test[0], preferred_timeframes[0]
                )
                strategy["expected_win_rate"] = perf.get("win_rate", min_win_rate)
                strategy["expected_sharpe"] = perf.get("sharpe_ratio", 0.5)
                strategy["backtest_pnl"] = perf.get("total_pnl_percent", 0)
                
                strategies.append(strategy)
        
        # Sort by expected performance
        strategies.sort(key=lambda x: x.get("expected_sharpe", 0), reverse=True)
        
        self.reasoning.append(f"Generated {len(strategies)} strategies, best Sharpe: {strategies[0].get('expected_sharpe', 0):.2f}" if strategies else "No strategies generated")
        
        return strategies
    
    def _determine_regime(self, target_market: str) -> str:
        """Map target market to regime"""
        regime_map = {
            "crypto_volatile": "volatile",
            "crypto_trending": "trending",
            "crypto_ranging": "ranging",
            "forex_range": "ranging",
            "forex_trend": "trending",
            "stocks_volatile": "volatile",
            "stocks_momentum": "trending"
        }
        return regime_map.get(target_market, "volatile")
    
    def _get_risk_params(self, risk_profile: str, max_dd: float) -> Dict[str, float]:
        """Get risk parameters based on profile"""
        profiles = {
            "conservative": {
                "stop_loss": 1.5,
                "take_profit": 2.5,
                "risk_per_trade": 0.5,
                "max_positions": 2,
                "trailing_stop": True,
                "trailing_activation": 1.5,
                "trailing_distance": 1.0
            },
            "moderate": {
                "stop_loss": 2.5,
                "take_profit": 5.0,
                "risk_per_trade": 1.0,
                "max_positions": 3,
                "trailing_stop": True,
                "trailing_activation": 3.0,
                "trailing_distance": 1.5
            },
            "aggressive": {
                "stop_loss": 4.0,
                "take_profit": 10.0,
                "risk_per_trade": 2.0,
                "max_positions": 5,
                "trailing_stop": True,
                "trailing_activation": 5.0,
                "trailing_distance": 2.0
            }
        }
        
        params = profiles.get(risk_profile, profiles["moderate"])
        
        # Adjust for max drawdown constraint
        if max_dd < 15:
            params["risk_per_trade"] *= 0.7
            params["max_positions"] = min(params["max_positions"], 2)
        
        return params
    
    async def _generate_single_strategy(
        self,
        regime: str,
        risk_params: Dict[str, float],
        timeframe: str,
        indicators_to_use: Optional[List[str]],
        avoid_indicators: Optional[List[str]],
        min_win_rate: float,
        strategy_num: int
    ) -> Dict[str, Any]:
        """Generate a single strategy configuration"""
        
        # Select indicators based on regime
        template = self.STRATEGY_TEMPLATES.get(regime, self.STRATEGY_TEMPLATES["volatile"])
        
        selected_indicators = []
        
        # Add trend indicators
        if "trend" in template["indicators"]:
            trend_ind = random.choice(self.TREND_INDICATORS)
            if not self._is_avoided(trend_ind, avoid_indicators):
                selected_indicators.append(trend_ind)
        
        # Add momentum indicators
        if "momentum" in template["indicators"]:
            momentum_inds = random.sample(self.MOMENTUM_INDICATORS, 
                                         min(2, len(self.MOMENTUM_INDICATORS)))
            for ind in momentum_inds:
                if not self._is_avoided(ind, avoid_indicators):
                    selected_indicators.append(ind)
        
        # Add volatility indicators
        if "volatility" in template["indicators"]:
            vol_ind = random.choice(self.VOLATILITY_INDICATORS)
            if not self._is_avoided(vol_ind, avoid_indicators):
                selected_indicators.append(vol_ind)
        
        # Add volume indicator
        if regime == "volatile" or random.random() > 0.5:
            vol_ind = random.choice(self.VOLUME_INDICATORS)
            if not self._is_avoided(vol_ind, avoid_indicators):
                selected_indicators.append(vol_ind)
        
        # Add user-requested indicators
        if indicators_to_use:
            for ind_type in indicators_to_use:
                if not any(i.get("type") == ind_type for i in selected_indicators):
                    ind = self._create_indicator(ind_type)
                    if ind:
                        selected_indicators.append(ind)
        
        # Generate entry rules based on template logic
        entry_rules = self._generate_entry_rules(
            selected_indicators, template["entry_logic"], regime
        )
        
        # Generate exit rules
        exit_rules = self._generate_exit_rules(
            selected_indicators, template["exit_logic"], regime
        )
        
        # Strategy name
        indicator_names = [i.get("type", i.get("alias", "unknown")) for i in selected_indicators[:2]]
        strategy_name = f"AI_{regime.capitalize()}_{'+'.join(indicator_names).upper()}_{strategy_num}"
        
        # Complexity assessment
        complexity = "beginner" if len(selected_indicators) <= 2 else "intermediate" if len(selected_indicators) <= 4 else "advanced"
        
        # Description
        description = self._generate_description(
            selected_indicators, regime, template["entry_logic"], risk_params
        )
        
        return {
            "name": strategy_name,
            "description": description,
            "indicators": selected_indicators,
            "entry_rules": entry_rules,
            "exit_rules": exit_rules,
            "risk_management": {
                "stop_loss_percent": risk_params["stop_loss"],
                "take_profit_percent": risk_params["take_profit"],
                "risk_per_trade": risk_params["risk_per_trade"],
                "max_positions": risk_params["max_positions"],
                "trailing_stop": risk_params.get("trailing_stop", False),
                "trailing_stop_activation": risk_params.get("trailing_activation", 2.0),
                "trailing_stop_distance": risk_params.get("trailing_distance", 1.0)
            },
            "complexity": complexity,
            "market_regime": regime,
            "timeframe": timeframe
        }
    
    def _is_avoided(self, indicator: Dict, avoid_list: Optional[List[str]]) -> bool:
        """Check if indicator should be avoided"""
        if not avoid_list:
            return False
        ind_type = indicator.get("type", "")
        return ind_type in avoid_list
    
    def _create_indicator(self, ind_type: str) -> Optional[Dict]:
        """Create indicator config by type"""
        all_indicators = (
            self.TREND_INDICATORS + 
            self.MOMENTUM_INDICATORS + 
            self.VOLATILITY_INDICATORS + 
            self.VOLUME_INDICATORS
        )
        
        for ind in all_indicators:
            if ind.get("type") == ind_type:
                return ind.copy()
        
        return None
    
    def _generate_entry_rules(
        self, 
        indicators: List[Dict], 
        logic: str,
        regime: str
    ) -> List[Dict[str, Any]]:
        """Generate entry rules based on indicators and logic"""
        
        entry_rules = []
        
        if logic == "trend_confirmation":
            # Trend-following entry
            long_conditions = []
            short_conditions = []
            
            for ind in indicators:
                ind_type = ind.get("type", "")
                alias = ind.get("alias", ind_type)
                
                if ind_type == "rsi":
                    long_conditions.append({
                        "left_operand": alias,
                        "operator": ">",
                        "right_operand": "40"
                    })
                    long_conditions.append({
                        "left_operand": alias,
                        "operator": "<",
                        "right_operand": "70"
                    })
                    short_conditions.append({
                        "left_operand": alias,
                        "operator": "<",
                        "right_operand": "60"
                    })
                    short_conditions.append({
                        "left_operand": alias,
                        "operator": ">",
                        "right_operand": "30"
                    })
                
                elif ind_type in ["ema", "sma"]:
                    period = ind.get("params", {}).get("period", 20)
                    long_conditions.append({
                        "left_operand": "close",
                        "operator": ">",
                        "right_operand": alias
                    })
                    short_conditions.append({
                        "left_operand": "close",
                        "operator": "<",
                        "right_operand": alias
                    })
                
                elif ind_type == "macd":
                    long_conditions.append({
                        "left_operand": "macd",
                        "operator": "crosses_above",
                        "right_operand": "macd_signal"
                    })
                    short_conditions.append({
                        "left_operand": "macd",
                        "operator": "crosses_below",
                        "right_operand": "macd_signal"
                    })
                
                elif ind_type == "supertrend":
                    long_conditions.append({
                        "left_operand": "supertrend_dir",
                        "operator": "==",
                        "right_operand": "1"
                    })
                    short_conditions.append({
                        "left_operand": "supertrend_dir",
                        "operator": "==",
                        "right_operand": "-1"
                    })
                
                elif ind_type == "adx":
                    long_conditions.append({
                        "left_operand": alias,
                        "operator": ">",
                        "right_operand": "25"
                    })
                    short_conditions.append({
                        "left_operand": alias,
                        "operator": ">",
                        "right_operand": "25"
                    })
            
            if long_conditions:
                entry_rules.append({
                    "direction": "LONG",
                    "condition_groups": [{
                        "conditions": long_conditions[:3],  # Limit conditions
                        "logic": "AND"
                    }],
                    "score_weight": 1.0
                })
            
            if short_conditions:
                entry_rules.append({
                    "direction": "SHORT",
                    "condition_groups": [{
                        "conditions": short_conditions[:3],
                        "logic": "AND"
                    }],
                    "score_weight": 1.0
                })
        
        elif logic == "mean_reversion":
            # Mean reversion entry
            long_conditions = []
            short_conditions = []
            
            for ind in indicators:
                ind_type = ind.get("type", "")
                alias = ind.get("alias", ind_type)
                
                if ind_type == "rsi":
                    long_conditions.append({
                        "left_operand": alias,
                        "operator": "<",
                        "right_operand": "30"
                    })
                    short_conditions.append({
                        "left_operand": alias,
                        "operator": ">",
                        "right_operand": "70"
                    })
                
                elif ind_type == "bollinger_bands":
                    long_conditions.append({
                        "left_operand": "close",
                        "operator": "<",
                        "right_operand": "bb_lower"
                    })
                    short_conditions.append({
                        "left_operand": "close",
                        "operator": ">",
                        "right_operand": "bb_upper"
                    })
                
                elif ind_type == "stochastic":
                    long_conditions.append({
                        "left_operand": "stoch_k",
                        "operator": "<",
                        "right_operand": "20"
                    })
                    short_conditions.append({
                        "left_operand": "stoch_k",
                        "operator": ">",
                        "right_operand": "80"
                    })
                
                elif ind_type == "cci":
                    long_conditions.append({
                        "left_operand": alias,
                        "operator": "<",
                        "right_operand": "-100"
                    })
                    short_conditions.append({
                        "left_operand": alias,
                        "operator": ">",
                        "right_operand": "100"
                    })
            
            if long_conditions:
                entry_rules.append({
                    "direction": "LONG",
                    "condition_groups": [{
                        "conditions": long_conditions[:2],
                        "logic": "AND"
                    }]
                })
            
            if short_conditions:
                entry_rules.append({
                    "direction": "SHORT",
                    "condition_groups": [{
                        "conditions": short_conditions[:2],
                        "logic": "AND"
                    }]
                })
        
        elif logic == "breakout":
            # Breakout entry
            long_conditions = [
                {"left_operand": "close", "operator": ">", "right_operand": "bb_upper"}
            ]
            short_conditions = [
                {"left_operand": "close", "operator": "<", "right_operand": "bb_lower"}
            ]
            
            # Add volume confirmation
            for ind in indicators:
                if ind.get("type") in ["volume_sma", "obv"]:
                    long_conditions.append({
                        "left_operand": "volume",
                        "operator": ">",
                        "right_operand": "volume_sma"
                    })
                    short_conditions.append({
                        "left_operand": "volume",
                        "operator": ">",
                        "right_operand": "volume_sma"
                    })
                    break
            
            entry_rules.append({
                "direction": "LONG",
                "condition_groups": [{"conditions": long_conditions, "logic": "AND"}]
            })
            entry_rules.append({
                "direction": "SHORT",
                "condition_groups": [{"conditions": short_conditions, "logic": "AND"}]
            })
        
        return entry_rules
    
    def _generate_exit_rules(
        self, 
        indicators: List[Dict], 
        logic: str,
        regime: str
    ) -> List[Dict[str, Any]]:
        """Generate exit rules based on indicators and logic"""
        
        exit_rules = []
        
        if logic == "trend_reversal":
            conditions = []
            
            for ind in indicators:
                ind_type = ind.get("type", "")
                
                if ind_type == "macd":
                    conditions.append({
                        "left_operand": "macd",
                        "operator": "crosses_below",
                        "right_operand": "macd_signal"
                    })
                elif ind_type == "supertrend":
                    conditions.append({
                        "left_operand": "supertrend_dir",
                        "operator": "==",
                        "right_operand": "-1"
                    })
            
            if conditions:
                exit_rules.append({
                    "condition_groups": [{
                        "conditions": conditions[:1],
                        "logic": "OR"
                    }],
                    "exit_type": "signal"
                })
        
        elif logic == "overbought_oversold":
            exit_rules.append({
                "condition_groups": [{
                    "conditions": [
                        {"left_operand": "rsi", "operator": ">", "right_operand": "50"}
                    ],
                    "logic": "AND"
                }],
                "exit_type": "signal"
            })
        
        elif logic == "volatility_contraction":
            exit_rules.append({
                "condition_groups": [{
                    "conditions": [
                        {"left_operand": "close", "operator": "<", "right_operand": "bb_upper"},
                        {"left_operand": "close", "operator": ">", "right_operand": "bb_lower"}
                    ],
                    "logic": "AND"
                }],
                "exit_type": "signal"
            })
        
        return exit_rules
    
    def _generate_description(
        self, 
        indicators: List[Dict], 
        regime: str, 
        logic: str,
        risk_params: Dict
    ) -> str:
        """Generate human-readable strategy description"""
        
        ind_names = [i.get("type", "").upper() for i in indicators]
        
        logic_desc = {
            "trend_confirmation": "follows trends with confirmation from multiple indicators",
            "mean_reversion": "trades reversals at extreme levels",
            "breakout": "captures breakouts from consolidation"
        }
        
        regime_desc = {
            "trending": "trending markets",
            "ranging": "ranging/sideways markets",
            "volatile": "high volatility conditions"
        }
        
        return f"AI-generated strategy optimized for {regime_desc.get(regime, 'various conditions')}. " \
               f"Uses {', '.join(ind_names[:3])} and {logic_desc.get(logic, 'proprietary logic')}. " \
               f"Risk management: {risk_params['stop_loss']}% SL, {risk_params['take_profit']}% TP, " \
               f"{risk_params['risk_per_trade']}% risk per trade."
    
    async def _quick_backtest(
        self, 
        strategy: Dict, 
        symbol: str, 
        timeframe: str,
        days: int = 30
    ) -> Dict[str, float]:
        """Run quick backtest to estimate strategy performance"""
        try:
            from webapp.services.backtest_engine_pro import ProBacktestEngine
            
            engine = ProBacktestEngine()
            
            risk = strategy.get("risk_management", {})
            
            result = await engine.run(
                custom_strategy=strategy,
                symbols=[symbol],
                timeframe=timeframe,
                days=days,
                initial_balance=10000,
                stop_loss_percent=risk.get("stop_loss_percent", 2.0),
                take_profit_percent=risk.get("take_profit_percent", 4.0),
                trailing_stop=risk.get("trailing_stop", False),
                trailing_stop_activation=risk.get("trailing_stop_activation", 2.0),
                trailing_stop_distance=risk.get("trailing_stop_distance", 1.0)
            )
            
            return result.get("metrics", {})
        except Exception as e:
            self.reasoning.append(f"Backtest error: {str(e)}")
            return {"win_rate": 50, "sharpe_ratio": 0.5, "total_pnl_percent": 0}
    
    async def generate_with_gpt(
        self,
        requirements: str,
        risk_profile: str = "moderate",
        symbol: str = "BTCUSDT",
        timeframe: str = "1h"
    ) -> Optional[Dict[str, Any]]:
        """
        Use GPT-4 to generate strategy based on natural language requirements.
        Requires OPENAI_API_KEY environment variable.
        """
        if not self.openai_key:
            self.reasoning.append("OpenAI API key not found, using rule-based generation")
            return None
        
        try:
            import aiohttp
            
            prompt = f"""You are an expert algorithmic trading strategy designer.
            
Based on these requirements: {requirements}
Risk profile: {risk_profile}
Trading pair: {symbol}
Timeframe: {timeframe}

Generate a complete trading strategy configuration in JSON format with:
1. name: Strategy name
2. description: Brief description
3. indicators: List of technical indicators with parameters
4. entry_rules: Entry conditions for LONG and SHORT
5. exit_rules: Exit conditions
6. risk_management: Stop loss, take profit, position sizing

Use these indicator types: rsi, macd, ema, sma, bollinger_bands, supertrend, atr, adx, stochastic, vwap

Respond ONLY with valid JSON, no explanation."""

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 2000
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        content = data["choices"][0]["message"]["content"]
                        
                        # Parse JSON from response
                        import json
                        strategy = json.loads(content)
                        
                        self.reasoning.append(f"GPT-4 generated strategy: {strategy.get('name', 'Unknown')}")
                        
                        return strategy
                    else:
                        self.reasoning.append(f"GPT API error: {resp.status}")
                        return None
        except Exception as e:
            self.reasoning.append(f"GPT generation error: {str(e)}")
            return None
    
    async def auto_improve(
        self,
        strategy: Dict[str, Any],
        symbol: str = "BTCUSDT",
        timeframe: str = "1h",
        days: int = 60,
        iterations: int = 10
    ) -> Dict[str, Any]:
        """
        Automatically improve a strategy through iteration.
        Uses feedback from backtests to adjust parameters.
        """
        from webapp.services.strategy_optimizer import StrategyOptimizer
        
        optimizer = StrategyOptimizer()
        
        # Define parameter ranges based on current strategy
        risk = strategy.get("risk_management", {})
        
        param_ranges = {
            "stop_loss_percent": {
                "min": max(0.5, risk.get("stop_loss_percent", 2) * 0.5),
                "max": min(10, risk.get("stop_loss_percent", 2) * 2),
                "step": 0.5
            },
            "take_profit_percent": {
                "min": max(1, risk.get("take_profit_percent", 4) * 0.5),
                "max": min(20, risk.get("take_profit_percent", 4) * 2),
                "step": 1.0
            },
            "risk_per_trade": {
                "min": 0.5,
                "max": 3.0,
                "step": 0.5
            }
        }
        
        # Run optimization
        result = await optimizer.random_search(
            base_strategy=strategy,
            param_ranges=param_ranges,
            target="sharpe_ratio",
            n_iterations=iterations,
            symbol=symbol,
            timeframe=timeframe,
            days=days
        )
        
        # Apply best parameters to strategy
        best_params = result.get("best_params", {})
        improved_strategy = strategy.copy()
        
        if "risk_management" not in improved_strategy:
            improved_strategy["risk_management"] = {}
        
        for key, value in best_params.items():
            improved_strategy["risk_management"][key] = value
        
        improved_strategy["name"] = f"{strategy.get('name', 'Strategy')}_improved"
        improved_strategy["description"] = f"Optimized version. Best Sharpe: {result.get('best_score', 0):.2f}"
        
        self.reasoning.append(f"Improved strategy Sharpe: {result.get('best_score', 0):.2f}")
        
        return {
            "original": strategy,
            "improved": improved_strategy,
            "improvement": result.get("best_score", 0),
            "optimization_details": result
        }


# Singleton instance
ai_strategy_generator = AIStrategyGenerator()
