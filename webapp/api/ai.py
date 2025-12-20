"""
AI Agent API endpoints
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import aiohttp
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from .auth import get_current_user

router = APIRouter(tags=["ai-agent"])


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


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

Current context will be provided about user's positions and market data."""


async def call_openai(message: str, context: Dict = None) -> Dict:
    """Call OpenAI API for chat completion"""
    if not OPENAI_API_KEY:
        # Return mock response if no API key
        return generate_mock_response(message)
    
    system_context = SYSTEM_PROMPT
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


def generate_mock_response(message: str) -> Dict:
    """Generate mock AI response for demo purposes"""
    msg = message.lower()
    
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


@router.post("/chat")
async def chat_with_ai(
    request: ChatRequest,
    user = Depends(get_current_user)
):
    """Chat with AI trading assistant"""
    try:
        result = await call_openai(request.message, request.context)
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
            "fearGreedIndex": 72,
            "fearGreedLabel": "Greed",
            "btcDominance": 54.2,
            "totalMarketCap": 3.45e12,
            "volume24h": 185e9,
            "topGainers": [
                {"symbol": "SOL", "change": 8.5},
                {"symbol": "AVAX", "change": 6.2},
                {"symbol": "LINK", "change": 5.8}
            ],
            "topLosers": [
                {"symbol": "DOGE", "change": -2.1},
                {"symbol": "SHIB", "change": -1.8}
            ],
            "fundingRates": {
                "BTC": 0.01,
                "ETH": 0.008
            }
        }
    }
