"""
AI Agent API endpoints
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import aiohttp
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from .auth import get_current_user

router = APIRouter(tags=["ai-agent"])


class ChatRequest(BaseModel):
    message: str
    question: Optional[str] = None  # Alias for message (iOS sends 'question')
    language: Optional[str] = "en"  # User's preferred language
    context: Optional[Dict[str, Any]] = None
    
    @property
    def text(self) -> str:
        """Get the actual question text"""
        return self.question or self.message


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Language names for system prompt
LANGUAGE_NAMES = {
    "en": "English",
    "ru": "Russian",
    "uk": "Ukrainian", 
    "de": "German",
    "es": "Spanish",
    "fr": "French",
    "it": "Italian",
    "ja": "Japanese",
    "zh": "Chinese",
    "ar": "Arabic",
    "he": "Hebrew",
    "pl": "Polish",
    "cs": "Czech",
    "lt": "Lithuanian",
    "sq": "Albanian"
}


SYSTEM_PROMPT = """You are an expert AI Trading Assistant for a cryptocurrency trading bot. You analyze markets, provide trading signals, and help users make informed decisions.

Your capabilities:
1. Technical Analysis - RSI, MACD, Bollinger Bands, Moving Averages, Volume analysis
2. Market Sentiment - Fear & Greed index, social sentiment, funding rates
3. Trading Signals - Entry/exit points with TP/SL levels
4. Risk Management - Position sizing, R:R ratios, portfolio risk
5. Strategy Advice - Optimize trading strategies

When providing trading signals:
- Always include Entry, Take Profit, and Stop Loss levels
- Calculate Risk:Reward ratio
- Provide confidence percentage (0-100%)
- Explain the reasoning behind the signal

Format responses with:
- Use **bold** for important terms
- Use bullet points for lists
- Be concise but informative
- Include specific price levels when relevant

Available commands:
/analyze [COIN] - Full technical analysis
/signal [PAIR] - Trading signal with entry/TP/SL
/market - Market overview
/risk - Portfolio risk assessment
/sentiment - Market sentiment analysis

Current context will be provided about user's positions and market data.

IMPORTANT: You MUST respond in the language specified by the user. If user speaks Russian, respond in Russian. If user speaks German, respond in German, etc."""


async def call_openai(message: str, context: Dict = None, language: str = "en") -> Dict:
    """Call OpenAI API for chat completion"""
    if not OPENAI_API_KEY:
        # Return mock response if no API key
        return generate_mock_response(message, language)
    
    lang_name = LANGUAGE_NAMES.get(language, "English")
    system_context = SYSTEM_PROMPT + f"\n\nIMPORTANT: Respond in {lang_name}."
    
    if context:
        if context.get("positions"):
            system_context += f"\n\nUser's current positions: {context['positions']}"
        if context.get("market"):
            system_context += f"\n\nCurrent market data: {context['market']}"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    "success": True,
                    "response": data["choices"][0]["message"]["content"]
                }
            else:
                return {"success": False, "error": f"API error: {resp.status}"}


def generate_mock_response(message: str, language: str = "en") -> Dict:
    """Generate mock AI response for demo purposes - with language support"""
    msg = message.lower()
    
    # Localized templates
    if language == "ru":
        templates = {
            "analyze_title": "📊 **Технический анализ {coin}**",
            "current_price": "**Текущая цена:**",
            "trend": "**Тренд:**",
            "bullish": "🟢 Бычий (Краткосрочный)",
            "key_levels": "**Ключевые уровни:**",
            "resistance": "Сопротивление",
            "support": "Поддержка",
            "indicators": "**Индикаторы:**",
            "volume_analysis": "**Анализ объема:**",
            "recommendation": "**Рекомендация:**",
            "signal_title": "🎯 **Торговый сигнал - BTC/USDT**",
            "direction": "**Направление:**",
            "long": "🟢 ЛОНГ",
            "confidence": "**Уверенность:**",
            "entry_zone": "**Зона входа:**",
            "take_profit": "**Тейк профит",
            "stop_loss": "**Стоп лосс:**",
            "risk_reward": "**Риск:Награда:**",
            "reasoning": "**Обоснование:**",
            "not_advice": "⚠️ *Это не финансовый совет. Проводите собственный анализ.*",
            "market_title": "🌍 **Обзор рынка**",
            "sentiment_title": "📊 **Настроение рынка**",
            "fear_greed": "Индекс страха и жадности",
            "greed": "Жадность",
        }
    elif language == "uk":
        templates = {
            "analyze_title": "📊 **Технічний аналіз {coin}**",
            "current_price": "**Поточна ціна:**",
            "trend": "**Тренд:**",
            "bullish": "🟢 Бичачий (Короткостроковий)",
            "key_levels": "**Ключові рівні:**",
            "resistance": "Опір",
            "support": "Підтримка",
            "indicators": "**Індикатори:**",
            "volume_analysis": "**Аналіз об'єму:**",
            "recommendation": "**Рекомендація:**",
            "signal_title": "🎯 **Торговий сигнал - BTC/USDT**",
            "direction": "**Напрямок:**",
            "long": "🟢 ЛОНГ",
            "confidence": "**Впевненість:**",
            "entry_zone": "**Зона входу:**",
            "take_profit": "**Тейк профіт",
            "stop_loss": "**Стоп лос:**",
            "risk_reward": "**Ризик:Нагорода:**",
            "reasoning": "**Обґрунтування:**",
            "not_advice": "⚠️ *Це не фінансова порада. Проводьте власний аналіз.*",
            "market_title": "🌍 **Огляд ринку**",
            "sentiment_title": "📊 **Настрій ринку**",
            "fear_greed": "Індекс страху та жадібності",
            "greed": "Жадібність",
        }
    else:
        templates = {
            "analyze_title": "📊 **{coin} Technical Analysis**",
            "current_price": "**Current Price:**",
            "trend": "**Trend:**",
            "bullish": "🟢 Bullish (Short-term)",
            "key_levels": "**Key Levels:**",
            "resistance": "Resistance",
            "support": "Support",
            "indicators": "**Indicators:**",
            "volume_analysis": "**Volume Analysis:**",
            "recommendation": "**Recommendation:**",
            "signal_title": "🎯 **Trading Signal - BTC/USDT**",
            "direction": "**Direction:**",
            "long": "🟢 LONG",
            "confidence": "**Confidence:**",
            "entry_zone": "**Entry Zone:**",
            "take_profit": "**Take Profit",
            "stop_loss": "**Stop Loss:**",
            "risk_reward": "**Risk:Reward:**",
            "reasoning": "**Reasoning:**",
            "not_advice": "⚠️ *This is not financial advice. Always DYOR.*",
            "market_title": "🌍 **Market Overview**",
            "sentiment_title": "📊 **Market Sentiment**",
            "fear_greed": "Fear & Greed Index",
            "greed": "Greed",
        }
    
    if "/analyze" in msg or "analyze" in msg:
        coin = "BTC" if "btc" in msg or "bitcoin" in msg else "ETH" if "eth" in msg else "BTC"
        return {
            "success": True,
            "response": f"""📊 **{coin} Technical Analysis**

**Current Price:** $97,500

**Trend:** 🟢 Bullish (Short-term)

**Key Levels:**
• Resistance: $98,500, $100,000, $102,500
• Support: $95,000, $93,500, $91,000

**Indicators:**
• **RSI (14):** 58.5 - Neutral, room for upside
• **MACD:** Bullish crossover on 4H
• **BB:** Price near upper band, slight overbought
• **EMA 20/50:** Bullish cross confirmed

**Volume Analysis:**
• 24h Volume: $45.2B (+15% vs avg)
• Buy pressure dominant

**Recommendation:** 
Consider LONG entries on pullbacks to $95,000-$96,000 zone with SL below $93,500.""",
            "analysis": {
                "indicators": {
                    "RSI": {"value": "58.5", "signal": "neutral"},
                    "MACD": {"value": "Bullish", "signal": "bullish"},
                    "BB": {"value": "Upper", "signal": "neutral"},
                    "Volume": {"value": "+15%", "signal": "bullish"}
                }
            }
        }
    
    elif "/signal" in msg or "signal" in msg:
        return {
            "success": True,
            "response": """🎯 **Trading Signal - BTC/USDT**

**Direction:** 🟢 LONG
**Confidence:** 75%

**Entry Zone:** $96,500 - $97,000
**Take Profit 1:** $99,000 (+2.5%)
**Take Profit 2:** $101,500 (+4.9%)
**Stop Loss:** $94,500 (-2.6%)

**Risk:Reward:** 1:1.9

**Reasoning:**
• Bullish structure on 4H
• Support holding at $96,000
• RSI oversold bounce setup
• Volume confirmation on support

**Position Size:** Risk 2% of portfolio

⚠️ *This is not financial advice. Always DYOR.*""",
            "analysis": {
                "signal": {
                    "direction": "long",
                    "confidence": 75
                },
                "levels": {
                    "entry": "97,000",
                    "takeProfit": "99,000",
                    "stopLoss": "94,500",
                    "riskReward": "1:1.9"
                }
            }
        }
    
    elif "/market" in msg or "market" in msg:
        return {
            "success": True,
            "response": """🌍 **Market Overview**

**BTC Dominance:** 54.2% (+0.3%)
**Total Market Cap:** $3.45T (+1.2%)
**24h Volume:** $185B

**Top Movers:**
• 🟢 SOL +8.5%
• 🟢 AVAX +6.2%
• 🟢 LINK +5.8%
• 🔴 DOGE -2.1%

**Market Sentiment:**
• Fear & Greed: 72 (Greed)
• Funding Rates: Slightly positive
• Open Interest: $45.5B (+5%)

**Key Events:**
• FOMC Meeting in 5 days
• ETH upgrade scheduled
• BTC options expiry Friday

**Summary:** Market is bullish but approaching resistance. Watch for potential consolidation before next leg up."""
        }
    
    elif "/risk" in msg or "risk" in msg:
        return {
            "success": True,
            "response": """⚠️ **Risk Assessment**

**Portfolio Health:** 🟡 Moderate Risk

**Current Exposure:**
• Total Position Value: $5,200
• Margin Used: 35%
• Unrealized PnL: +$320 (+6.5%)

**Risk Metrics:**
• Max Drawdown (30d): -8.5%
• Sharpe Ratio: 1.45
• Win Rate: 62%

**Recommendations:**
1. Consider reducing leverage on volatile pairs
2. Set stop losses on all positions
3. Diversify across uncorrelated assets
4. Keep 40% in reserve for opportunities

**Overall:** Your risk levels are acceptable but monitor positions closely during high volatility periods."""
        }
    
    else:
        return {
            "success": True,
            "response": f"""I can help you with market analysis and trading signals!

**Quick Commands:**
• `/analyze BTC` - Full BTC analysis
• `/signal ETHUSDT` - Trading signal
• `/market` - Market overview
• `/risk` - Risk assessment

Or ask me anything about:
• Technical analysis
• Trading strategies
• Risk management
• Market sentiment

What would you like to know?"""
        }


class AnalyzeRequest(BaseModel):
    symbol: str
    timeframe: str = "1h"


@router.post("/analyze")
async def analyze_symbol(
    request: AnalyzeRequest,
    user = Depends(get_current_user)
):
    """
    AI-powered symbol analysis.
    Returns signal (LONG/SHORT/NEUTRAL), confidence, and key factors.
    """
    symbol = request.symbol.upper()
    timeframe = request.timeframe
    
    # In production, this would call actual analysis service
    # For now, return intelligent mock based on symbol
    import random
    import hashlib
    
    # Deterministic but varying results based on symbol (using SHA256 instead of MD5)
    seed = int(hashlib.sha256(symbol.encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    confidence = random.randint(55, 92)
    is_bullish = random.random() > 0.4
    signal = "LONG" if is_bullish else "SHORT" if random.random() > 0.3 else "NEUTRAL"
    
    price = random.uniform(0.1, 100000)
    if "BTC" in symbol:
        price = random.uniform(95000, 102000)
    elif "ETH" in symbol:
        price = random.uniform(3200, 3800)
    elif "SOL" in symbol:
        price = random.uniform(180, 220)
    
    tp_pct = random.uniform(2, 8)
    sl_pct = random.uniform(1.5, 4)
    
    return {
        "success": True,
        "data": {
            "symbol": symbol,
            "signal": signal,
            "confidence": confidence / 100,
            "analysis": f"Based on {timeframe} chart analysis, {symbol} shows {'bullish momentum with support holding' if is_bullish else 'bearish pressure with resistance ahead'}. Volume {'confirms' if confidence > 70 else 'partially supports'} the setup.",
            "key_factors": [
                f"RSI at {random.randint(30, 70)} - {'oversold bounce' if is_bullish else 'overbought rejection'}",
                f"MACD {'bullish crossover' if is_bullish else 'bearish divergence'}",
                f"Volume {'above' if is_bullish else 'below'} 20-day average",
                f"Price {'above' if is_bullish else 'below'} EMA 50"
            ],
            "price_targets": {
                "entry": round(price, 4),
                "take_profit": round(price * (1 + tp_pct/100) if is_bullish else price * (1 - tp_pct/100), 4),
                "stop_loss": round(price * (1 - sl_pct/100) if is_bullish else price * (1 + sl_pct/100), 4),
                "support": round(price * 0.95, 4),
                "resistance": round(price * 1.05, 4)
            },
            "risk_level": "LOW" if confidence > 75 else "MEDIUM" if confidence > 60 else "HIGH",
            "timestamp": datetime.now().isoformat()
        }
    }


@router.post("/chat")
async def chat_with_ai(
    request: ChatRequest,
    user = Depends(get_current_user)
):
    """Chat with AI trading assistant - responds in user's language"""
    try:
        message = request.text  # Use the property that handles both 'question' and 'message'
        language = request.language or "en"
        result = await call_openai(message, request.context, language)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/market-sentiment")
async def get_market_sentiment(user = Depends(get_current_user)):
    """Get current market sentiment data"""
    # In production, this would fetch from various APIs
    return {
        "success": True,
        "data": {
            "overall": "BULLISH",
            "score": 35.5,
            "fear_greed_index": 72,
            "btc_dominance": 54.2,
            "top_signals": [
                {"symbol": "SOLUSDT", "direction": "LONG", "confidence": 0.78, "strategy": "momentum"},
                {"symbol": "ETHUSDT", "direction": "LONG", "confidence": 0.72, "strategy": "breakout"},
                {"symbol": "DOGEUSDT", "direction": "SHORT", "confidence": 0.65, "strategy": "reversal"}
            ],
            "market_conditions": {
                "volatility": "MEDIUM",
                "trend": "UPTREND",
                "volume": "HIGH",
                "open_interest": "INCREASING"
            },
            "last_updated": "2026-01-25T20:00:00Z"
        }
    }
