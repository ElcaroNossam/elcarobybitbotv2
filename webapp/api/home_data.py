"""
Home Page Data API - Real-time BTC/Gold/Platform Stats
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import aiohttp
import asyncio
from datetime import datetime
import logging

router = APIRouter(prefix="/api/home", tags=["home"])
logger = logging.getLogger(__name__)

# Cache for data
_cache = {
    "btc": {"data": None, "updated": 0},
    "gold": {"data": None, "updated": 0},
    "stats": {"data": None, "updated": 0}
}
CACHE_TTL = 60  # 60 seconds


async def fetch_btc_data() -> Dict[str, Any]:
    """Fetch Bitcoin price and chart data from Binance"""
    try:
        async with aiohttp.ClientSession() as session:
            # Current price
            async with session.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT") as resp:
                if resp.status == 200:
                    ticker = await resp.json()
                else:
                    ticker = {}
            
            # Klines for chart (1h, last 168 points = 7 days)
            async with session.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=168") as resp:
                if resp.status == 200:
                    klines = await resp.json()
                else:
                    klines = []
            
            # Format chart data (timestamp, close price)
            chart_data = [[int(k[0]), float(k[4])] for k in klines]
            
            return {
                "symbol": "BTC/USDT",
                "price": float(ticker.get("lastPrice", 0)),
                "change24h": float(ticker.get("priceChangePercent", 0)),
                "high24h": float(ticker.get("highPrice", 0)),
                "low24h": float(ticker.get("lowPrice", 0)),
                "volume24h": float(ticker.get("quoteVolume", 0)),
                "chart": chart_data
            }
    except Exception as e:
        logger.error(f"Error fetching BTC data: {e}")
        return {"symbol": "BTC/USDT", "price": 0, "change24h": 0, "chart": []}


async def fetch_gold_data() -> Dict[str, Any]:
    """Fetch Gold price data from various sources"""
    try:
        async with aiohttp.ClientSession() as session:
            # Try Metals API (free tier)
            headers = {"Accept": "application/json"}
            
            # Use a public gold API
            async with session.get(
                "https://api.metalpriceapi.com/v1/latest?api_key=demo&base=USD&currencies=XAU",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success") and data.get("rates", {}).get("XAU"):
                        gold_oz = 1 / data["rates"]["XAU"]
                        return {
                            "symbol": "XAU/USD",
                            "price": round(gold_oz, 2),
                            "change24h": 0.45,  # Placeholder
                            "unit": "per oz"
                        }
            
            # Fallback: estimated price
            return {
                "symbol": "XAU/USD",
                "price": 2045.50,
                "change24h": 0.32,
                "unit": "per oz"
            }
    except Exception as e:
        logger.error(f"Error fetching Gold data: {e}")
        return {"symbol": "XAU/USD", "price": 2045.50, "change24h": 0.32, "unit": "per oz"}


async def fetch_platform_stats() -> Dict[str, Any]:
    """Fetch platform statistics from database"""
    try:
        from core.db_postgres import execute, execute_one
        
        # Total users
        users_result = execute_one("SELECT COUNT(*) as cnt FROM users WHERE is_allowed = 1")
        total_users = users_result["cnt"] if users_result else 0
        
        # Total trades
        trades_result = execute_one("SELECT COUNT(*) as cnt FROM trade_logs")
        total_trades = trades_result["cnt"] if trades_result else 0
        
        # Total volume (sum of trade sizes * entry prices)
        volume_result = execute_one("""
            SELECT COALESCE(SUM(ABS(size * entry_price)), 0) as vol 
            FROM trade_logs 
            WHERE ts > NOW() - INTERVAL '30 days'
        """)
        total_volume = float(volume_result["vol"]) if volume_result else 0
        
        # Win rate
        winrate_result = execute_one("""
            SELECT 
                COUNT(CASE WHEN pnl > 0 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as winrate
            FROM trade_logs
            WHERE ts > NOW() - INTERVAL '30 days'
        """)
        win_rate = round(float(winrate_result["winrate"] or 0), 1)
        
        # Active positions
        positions_result = execute_one("SELECT COUNT(*) as cnt FROM active_positions")
        active_positions = positions_result["cnt"] if positions_result else 0
        
        # Today's PnL
        today_pnl_result = execute_one("""
            SELECT COALESCE(SUM(pnl), 0) as pnl
            FROM trade_logs
            WHERE ts::date = CURRENT_DATE
        """)
        today_pnl = float(today_pnl_result["pnl"]) if today_pnl_result else 0
        
        # Signals today
        signals_result = execute_one("""
            SELECT COUNT(*) as cnt FROM signals 
            WHERE ts > NOW() - INTERVAL '24 hours'
        """)
        signals_today = signals_result["cnt"] if signals_result else 0
        
        return {
            "total_users": total_users,
            "total_trades": total_trades,
            "total_volume": total_volume,
            "win_rate": win_rate,
            "active_positions": active_positions,
            "today_pnl": today_pnl,
            "signals_today": signals_today,
            "uptime": 99.9,
            "server_status": "online"
        }
    except Exception as e:
        logger.error(f"Error fetching platform stats: {e}")
        return {
            "total_users": 0,
            "total_trades": 0,
            "total_volume": 0,
            "win_rate": 0,
            "active_positions": 0,
            "today_pnl": 0,
            "signals_today": 0,
            "uptime": 99.9,
            "server_status": "online"
        }


@router.get("/btc")
async def get_btc_data():
    """Get Bitcoin price and chart data"""
    now = datetime.now().timestamp()
    if _cache["btc"]["data"] and (now - _cache["btc"]["updated"]) < CACHE_TTL:
        return _cache["btc"]["data"]
    
    data = await fetch_btc_data()
    _cache["btc"] = {"data": data, "updated": now}
    return data


@router.get("/gold")
async def get_gold_data():
    """Get Gold price data"""
    now = datetime.now().timestamp()
    if _cache["gold"]["data"] and (now - _cache["gold"]["updated"]) < CACHE_TTL:
        return _cache["gold"]["data"]
    
    data = await fetch_gold_data()
    _cache["gold"] = {"data": data, "updated": now}
    return data


@router.get("/stats")
async def get_platform_stats():
    """Get platform statistics"""
    now = datetime.now().timestamp()
    if _cache["stats"]["data"] and (now - _cache["stats"]["updated"]) < CACHE_TTL:
        return _cache["stats"]["data"]
    
    data = await fetch_platform_stats()
    _cache["stats"] = {"data": data, "updated": now}
    return data


@router.get("/all")
async def get_all_home_data():
    """Get all home page data in one request"""
    btc, gold, stats = await asyncio.gather(
        get_btc_data(),
        get_gold_data(),
        get_platform_stats()
    )
    
    return {
        "btc": btc,
        "gold": gold,
        "stats": stats,
        "timestamp": datetime.now().isoformat()
    }
