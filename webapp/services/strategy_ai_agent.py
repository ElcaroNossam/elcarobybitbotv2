"""
Strategy AI Agent - GPT-4 Integration for Strategy Generation

Converts natural language descriptions into valid StrategySpec configurations.
Uses OpenAI GPT-4 with structured output for reliable JSON generation.
"""
import os
import json
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not installed. AI strategy generation will use fallback templates.")


@dataclass
class AIGenerationResult:
    """Result of AI strategy generation"""
    success: bool
    strategy: Optional[Dict[str, Any]]
    error: Optional[str] = None
    model_used: str = "fallback"
    tokens_used: int = 0


# System prompt for GPT-4
STRATEGY_SYSTEM_PROMPT = """You are an expert crypto trading strategy architect. Your task is to convert natural language trading strategy descriptions into valid JSON configurations.

You MUST output a valid JSON object following this EXACT structure:

{
    "name": "Strategy Name",
    "description": "Brief description",
    "version": "1.0.0",
    "primary_timeframe": "15m",  // Options: 1m, 5m, 15m, 30m, 1h, 4h, 1d
    "higher_timeframes": ["1h", "4h"],  // For confirmation
    "long_entry": {  // null if no long trades
        "direction": "LONG",
        "groups": [{
            "id": "main",
            "conditions": [
                {
                    "id": "cond1",
                    "left": {"type": "rsi", "params": {"period": 14}},
                    "operator": "<",  // <, >, <=, >=, ==, !=, crosses_above, crosses_below, between
                    "right": null,  // Use for comparing two indicators
                    "value": 30,  // Use for comparing indicator to fixed value
                    "enabled": true,
                    "description": "RSI oversold"
                }
            ],
            "operator": "AND",  // AND or OR within group
            "enabled": true
        }],
        "group_operator": "AND",  // AND or OR between groups
        "enabled": true
    },
    "short_entry": null,  // Similar structure to long_entry, or null
    "exit_rules": [
        {"type": "take_profit", "value": 4.0, "enabled": true},
        {"type": "stop_loss", "value": 2.0, "enabled": true},
        {"type": "trailing_stop", "value": 1.5, "params": {"activation_percent": 2.0}, "enabled": true}
    ],
    "risk": {
        "position_size_percent": 10.0,  // % of balance per trade
        "max_positions": 5,
        "max_daily_trades": 20,
        "max_daily_loss_percent": 10.0,
        "leverage": 10
    },
    "filters": {
        "min_volume_usdt": null,
        "excluded_symbols": [],
        "required_symbols": [],
        "time_filters": []
    },
    "pyramiding": 1,  // Max entries per symbol
    "allow_reverse": false
}

AVAILABLE INDICATOR TYPES (for "left" or "right" fields):
- Trend: ema, sma, wma, vwma, vwap, supertrend, ichimoku
- Oscillators: rsi, stoch, stoch_rsi, cci, williams_r, mfi, ao, roc, momentum
- Volatility: bb (Bollinger), atr, keltner, donchian
- Volume: volume, obv, cvd, vwap
- Price: price_close, price_open, price_high, price_low, price_hl2, price_hlc3
- Other: macd (use field: "macd", "signal", or "histogram"), adx, aroon, psar

INDICATOR PARAMS (include in "params" object):
- period: int (default 14 for most oscillators, 20 for BB)
- fast: int (for MACD, default 12)
- slow: int (for MACD, default 26)
- signal: int (for MACD, default 9)
- field: str (for MACD: "macd", "signal", "histogram")
- std_dev: float (for BB, default 2.0)

EXIT RULE TYPES:
- take_profit: Fixed % above entry
- stop_loss: Fixed % below entry
- trailing_stop: Trails price (params: activation_percent)
- breakeven: Move SL to entry (params: activation_percent, offset)
- time_based: Exit after N bars (params: bars)
- indicator: Exit on indicator condition (conditions: [...])

OPERATORS:
- Comparison: <, >, <=, >=, ==, !=
- Crossing: crosses_above, crosses_below
- Range: between (uses value and value2)

IMPORTANT RULES:
1. Output ONLY valid JSON, no markdown code blocks
2. All indicator periods should be realistic (5-200 typically)
3. TP should be greater than SL for proper risk/reward
4. Use appropriate operators for each indicator type
5. Be creative but realistic based on the user's description
"""


class StrategyAIAgent:
    """AI Agent for converting text to StrategySpec"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = "gpt-4o"  # Using GPT-4o for best JSON output
        self.fallback_model = "gpt-3.5-turbo"
        
        if OPENAI_AVAILABLE and self.api_key:
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    async def generate(self, prompt: str, max_retries: int = 2) -> AIGenerationResult:
        """
        Generate strategy from natural language prompt.
        
        Args:
            prompt: Natural language description of the strategy
            max_retries: Number of retries on failure
            
        Returns:
            AIGenerationResult with strategy dict or error
        """
        if not self.client:
            # Fallback to pattern matching
            return self._fallback_generate(prompt)
        
        # Try GPT-4 first, fallback to GPT-3.5
        for model in [self.model, self.fallback_model]:
            for attempt in range(max_retries):
                try:
                    result = await self._call_openai(prompt, model)
                    if result.success:
                        return result
                except Exception as e:
                    logger.warning(f"OpenAI call failed (model={model}, attempt={attempt+1}): {e}")
                    continue
        
        # All retries failed, use fallback
        logger.warning("All OpenAI attempts failed, using fallback template")
        return self._fallback_generate(prompt)
    
    async def _call_openai(self, prompt: str, model: str) -> AIGenerationResult:
        """Make OpenAI API call"""
        import asyncio
        
        user_message = f"""Create a trading strategy based on this description:

"{prompt}"

Remember:
- Output ONLY valid JSON (no code blocks, no explanation)
- Include both long_entry and short_entry if appropriate, or set one to null
- Set realistic parameters based on the description
- If the user mentions specific indicators, use them
- If the user mentions timeframes, use them
"""
        
        # Run in thread pool since openai client is sync
        loop = asyncio.get_event_loop()
        
        try:
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": STRATEGY_SYSTEM_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=2000,
                    response_format={"type": "json_object"} if model == "gpt-4o" else None
                )
            )
            
            content = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            # Parse JSON
            # Clean up any markdown code blocks
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            strategy_dict = json.loads(content)
            
            # Validate required fields
            required = ["name", "long_entry", "exit_rules", "risk"]
            for field in required:
                if field not in strategy_dict:
                    if field == "long_entry" and strategy_dict.get("short_entry"):
                        continue  # OK if short_entry exists
                    return AIGenerationResult(
                        success=False,
                        strategy=None,
                        error=f"Missing required field: {field}",
                        model_used=model
                    )
            
            # Add defaults if missing
            strategy_dict.setdefault("version", "1.0.0")
            strategy_dict.setdefault("primary_timeframe", "15m")
            strategy_dict.setdefault("higher_timeframes", ["1h", "4h"])
            strategy_dict.setdefault("pyramiding", 1)
            strategy_dict.setdefault("allow_reverse", False)
            strategy_dict.setdefault("filters", {
                "min_volume_usdt": None,
                "excluded_symbols": [],
                "required_symbols": []
            })
            
            return AIGenerationResult(
                success=True,
                strategy=strategy_dict,
                model_used=model,
                tokens_used=tokens_used
            )
            
        except json.JSONDecodeError as e:
            return AIGenerationResult(
                success=False,
                strategy=None,
                error=f"Invalid JSON from AI: {str(e)}",
                model_used=model
            )
        except Exception as e:
            return AIGenerationResult(
                success=False,
                strategy=None,
                error=str(e),
                model_used=model
            )
    
    def _fallback_generate(self, prompt: str) -> AIGenerationResult:
        """Fallback template-based generation when OpenAI is not available"""
        from models.strategy_spec import StrategyTemplates
        
        prompt_lower = prompt.lower()
        
        # Pattern matching for common strategy types
        if "rsi" in prompt_lower and ("oversold" in prompt_lower or "overbought" in prompt_lower or "below 30" in prompt_lower or "above 70" in prompt_lower):
            spec = StrategyTemplates.rsi_mean_reversion()
            
            # Customize based on prompt
            if "5m" in prompt_lower or "5 min" in prompt_lower:
                spec.primary_timeframe = "5m"
            elif "1h" in prompt_lower or "hourly" in prompt_lower:
                spec.primary_timeframe = "1h"
            
            spec.name = "AI Generated: RSI Mean Reversion"
            
        elif "macd" in prompt_lower and ("cross" in prompt_lower or "crossover" in prompt_lower):
            spec = StrategyTemplates.macd_crossover()
            spec.name = "AI Generated: MACD Crossover"
            
        elif "bollinger" in prompt_lower or "bb" in prompt_lower:
            spec = StrategyTemplates.bollinger_breakout()
            spec.name = "AI Generated: Bollinger Breakout"
            
        elif "scalp" in prompt_lower:
            # Scalping strategy with tight parameters
            spec = StrategyTemplates.multi_indicator()
            spec.name = "AI Generated: Scalping Strategy"
            spec.primary_timeframe = "5m"
            spec.risk.leverage = 20
            spec.risk.max_positions = 3
            # Adjust exit rules for scalping
            for rule in spec.exit_rules:
                if rule.type == "take_profit":
                    rule.value = 1.5
                elif rule.type == "stop_loss":
                    rule.value = 0.75
                    
        elif "trend" in prompt_lower or "ema" in prompt_lower or "moving average" in prompt_lower:
            spec = StrategyTemplates.multi_indicator()
            spec.name = "AI Generated: Trend Following"
            
        elif "momentum" in prompt_lower:
            spec = StrategyTemplates.multi_indicator()
            spec.name = "AI Generated: Momentum Strategy"
            
        else:
            # Default multi-indicator
            spec = StrategyTemplates.multi_indicator()
            spec.name = "AI Generated: Multi-Indicator Strategy"
        
        spec.description = f"Generated from: {prompt[:100]}..."
        
        return AIGenerationResult(
            success=True,
            strategy=spec.to_dict(),
            model_used="fallback-template",
            tokens_used=0
        )
    
    async def enhance_strategy(self, strategy: Dict[str, Any], feedback: str) -> AIGenerationResult:
        """
        Enhance an existing strategy based on user feedback.
        
        Args:
            strategy: Current strategy configuration
            feedback: User's feedback or enhancement request
            
        Returns:
            AIGenerationResult with enhanced strategy
        """
        if not self.client:
            return AIGenerationResult(
                success=False,
                strategy=strategy,
                error="OpenAI not available for enhancement",
                model_used="none"
            )
        
        prompt = f"""Enhance this trading strategy based on the user's feedback.

CURRENT STRATEGY:
{json.dumps(strategy, indent=2)}

USER FEEDBACK:
{feedback}

Output the complete enhanced strategy as valid JSON.
"""
        
        return await self.generate(prompt)
    
    async def explain_strategy(self, strategy: Dict[str, Any]) -> str:
        """Generate human-readable explanation of a strategy"""
        if not self.client:
            return self._fallback_explain(strategy)
        
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a trading strategy expert. Explain trading strategies in simple terms."},
                        {"role": "user", "content": f"Explain this trading strategy in simple terms:\n\n{json.dumps(strategy, indent=2)}"}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.warning(f"Explain strategy failed: {e}")
            return self._fallback_explain(strategy)
    
    def _fallback_explain(self, strategy: Dict[str, Any]) -> str:
        """Fallback explanation generator"""
        lines = [f"**{strategy.get('name', 'Strategy')}**", ""]
        
        if strategy.get("description"):
            lines.append(strategy["description"])
            lines.append("")
        
        # Entry conditions
        long_entry = strategy.get("long_entry")
        short_entry = strategy.get("short_entry")
        
        if long_entry and long_entry.get("enabled"):
            lines.append("**Long Entry:**")
            for group in long_entry.get("groups", []):
                for cond in group.get("conditions", []):
                    desc = cond.get("description", "")
                    if desc:
                        lines.append(f"- {desc}")
            lines.append("")
        
        if short_entry and short_entry.get("enabled"):
            lines.append("**Short Entry:**")
            for group in short_entry.get("groups", []):
                for cond in group.get("conditions", []):
                    desc = cond.get("description", "")
                    if desc:
                        lines.append(f"- {desc}")
            lines.append("")
        
        # Exit rules
        lines.append("**Exit Rules:**")
        for rule in strategy.get("exit_rules", []):
            if rule.get("enabled"):
                rule_type = rule.get("type", "unknown")
                value = rule.get("value")
                if value:
                    lines.append(f"- {rule_type.replace('_', ' ').title()}: {value}%")
                else:
                    lines.append(f"- {rule_type.replace('_', ' ').title()}")
        
        # Risk
        risk = strategy.get("risk", {})
        lines.append("")
        lines.append("**Risk Management:**")
        lines.append(f"- Position size: {risk.get('position_size_percent', 10)}% of balance")
        lines.append(f"- Max positions: {risk.get('max_positions', 5)}")
        lines.append(f"- Leverage: {risk.get('leverage', 10)}x")
        
        return "\n".join(lines)


# Singleton instance
_agent_instance: Optional[StrategyAIAgent] = None


def get_ai_agent() -> StrategyAIAgent:
    """Get or create singleton AI agent"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = StrategyAIAgent()
    return _agent_instance
