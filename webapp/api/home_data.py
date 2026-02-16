"""
Home Page Data API - Real-time BTC/Gold/Platform Stats + Market Overview
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import aiohttp
import asyncio
from datetime import datetime
import logging
import re

router = APIRouter(prefix="/api/home", tags=["home"])
logger = logging.getLogger(__name__)

# Cache for data
_cache = {
    "btc": {"data": None, "updated": 0},
    "gold": {"data": None, "updated": 0},
    "stats": {"data": None, "updated": 0},
    "market": {"data": None, "updated": 0},
}
CACHE_TTL = 60  # 60 seconds
MARKET_CACHE_TTL = 120  # 2 minutes for market data (heavier fetch)


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
        win_rate = round(float(winrate_result["winrate"] or 0), 1) if winrate_result else 0.0
        
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


async def fetch_market_data() -> Dict[str, Any]:
    """Fetch comprehensive market data: Fear & Greed, Dominance, S&P 500, Gold, Top Coins, Market Cap.
    Replicates bot.py fetch_market_status() logic."""
    btc_dom, eth_dom, usdt_dom = 0.0, 0.0, 0.0
    btc_price, btc_change = 0.0, 0.0
    sp500, sp500_change = 0.0, 0.0
    gold_price, gold_change = 0.0, 0.0
    total1, total2, total3 = 0.0, 0.0, 0.0
    fear_greed, fear_greed_label = 0, "N/A"
    altseason_index = 0
    top_coins = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    async with aiohttp.ClientSession() as session:
        # ===== CoinMarketCap: listing API for top coins, dominance, BTC price =====
        try:
            cmc_url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?start=1&limit=15&sortBy=market_cap&sortType=desc"
            async with session.get(cmc_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 200:
                    data = await r.json()
                    for crypto in data.get("data", {}).get("cryptoCurrencyList", []):
                        symbol = crypto.get("symbol")
                        usd_quote = None
                        for q in crypto.get("quotes", []):
                            if q.get("name") == "USD":
                                usd_quote = q
                                break
                        if not usd_quote and crypto.get("quotes"):
                            usd_quote = crypto.get("quotes", [{}])[-1]
                        if not usd_quote:
                            continue
                        dom = usd_quote.get("dominance", 0)
                        mcap = usd_quote.get("marketCap", 0)
                        mcap_b = mcap / 1e9 if mcap else 0
                        price = usd_quote.get("price", 0)
                        change_24h = usd_quote.get("percentChange24h", 0)
                        if symbol == "BTC":
                            btc_dom = float(dom)
                            btc_price = float(price)
                            btc_change = float(change_24h)
                        elif symbol == "ETH":
                            eth_dom = float(dom)
                        elif symbol == "USDT":
                            usdt_dom = float(dom)
                        if symbol not in ("BTC", "USDT", "USDC", "DAI", "BUSD", "TUSD", "FDUSD", "USDD", "CMC20", "CMC100"):
                            top_coins.append({"symbol": symbol, "mcap_b": round(mcap_b, 2), "dominance": round(float(dom), 2), "price": round(float(price), 2), "change_24h": round(float(change_24h), 2)})
        except Exception as e:
            logger.warning(f"CoinMarketCap listing fetch failed: {e}")

        # ===== CoinMarketCap: global metrics for Total Market Cap =====
        try:
            cmc_global_url = "https://api.coinmarketcap.com/data-api/v3/global-metrics/quotes/latest"
            async with session.get(cmc_global_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 200:
                    data = await r.json()
                    gdata = data.get("data", {})
                    if btc_dom == 0:
                        btc_dom = float(gdata.get("btcDominance", 0))
                    if eth_dom == 0:
                        eth_dom = float(gdata.get("ethDominance", 0))
                    quotes = gdata.get("quotes", [])
                    if quotes:
                        q = quotes[0]
                        total_mcap = q.get("totalMarketCap", 0)
                        altcoin_mcap = q.get("altcoinMarketCap", 0)
                        total1 = total_mcap / 1e12
                        total2 = altcoin_mcap / 1e12
                        eth_mcap = total_mcap * (eth_dom / 100) if eth_dom else 0
                        total3 = (altcoin_mcap - eth_mcap) / 1e12
        except Exception as e:
            logger.warning(f"CoinMarketCap global metrics failed: {e}")

        # ===== CoinMarketCap: Fear & Greed and Altcoin Season =====
        try:
            fg_url = "https://coinmarketcap.com/charts/fear-and-greed-index/"
            async with session.get(fg_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 200:
                    html = await r.text()
                    fg_match = re.search(r'"score":(\d+).*?"name":"([^"]+)"', html)
                    if fg_match:
                        fear_greed = int(fg_match.group(1))
                        fear_greed_label = fg_match.group(2)
                    alt_match = re.search(r'"altcoinIndex":(\d+)', html)
                    if alt_match:
                        altseason_index = int(alt_match.group(1))
        except Exception as e:
            logger.warning(f"CoinMarketCap Fear & Greed fetch failed: {e}")

        # ===== Yahoo Finance: S&P 500 =====
        try:
            sp500_url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?interval=1d&range=2d"
            async with session.get(sp500_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as r:
                data = await r.json()
                result = data.get("chart", {}).get("result", [])
                if result:
                    meta = result[0].get("meta", {})
                    sp500 = meta.get("regularMarketPrice", 0.0)
                    prev_close = meta.get("chartPreviousClose", meta.get("previousClose", sp500))
                    if prev_close and prev_close > 0:
                        sp500_change = ((sp500 - prev_close) / prev_close) * 100
        except Exception as e:
            logger.warning(f"Yahoo S&P500 fetch failed: {e}")

        # ===== Yahoo Finance: Gold =====
        try:
            gold_url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=1d&range=2d"
            async with session.get(gold_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as r:
                data = await r.json()
                result = data.get("chart", {}).get("result", [])
                if result:
                    meta = result[0].get("meta", {})
                    gold_price = meta.get("regularMarketPrice", 0.0)
                    prev_close = meta.get("chartPreviousClose", meta.get("previousClose", gold_price))
                    if prev_close and prev_close > 0:
                        gold_change = ((gold_price - prev_close) / prev_close) * 100
        except Exception as e:
            logger.warning(f"Yahoo Gold fetch failed: {e}")

    # Sort top coins by dominance
    top_coins = sorted(top_coins, key=lambda x: x["dominance"], reverse=True)[:5]

    # ALT Signal logic (same as cmd_market in bot.py)
    # Falling BTC dominance + BTC price up = LONG altcoins
    alt_signal = "NEUTRAL"
    # We don't store prev_dom in webapp, so base on altseason
    if altseason_index >= 75:
        alt_signal = "LONG"
    elif altseason_index <= 25:
        alt_signal = "SHORT"
    else:
        alt_signal = "NEUTRAL"

    return {
        "btc": {
            "price": round(btc_price, 2),
            "change_24h": round(btc_change, 2),
            "dominance": round(btc_dom, 2),
        },
        "usdt_dominance": round(usdt_dom, 2),
        "sp500": {
            "price": round(sp500, 2),
            "change": round(sp500_change, 2),
        },
        "gold": {
            "price": round(gold_price, 2),
            "change": round(gold_change, 2),
        },
        "fear_greed": {
            "value": fear_greed,
            "label": fear_greed_label,
        },
        "altseason_index": altseason_index,
        "alt_signal": alt_signal,
        "top_coins": top_coins,
        "total_market_cap": {
            "total1": round(total1, 2),
            "total2": round(total2, 2),
            "total3": round(total3, 2),
        },
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/market")
async def get_market_data():
    """Get comprehensive market overview data (Fear & Greed, Dominance, S&P 500, etc.)"""
    now = datetime.now().timestamp()
    if _cache["market"]["data"] and (now - _cache["market"]["updated"]) < MARKET_CACHE_TTL:
        return _cache["market"]["data"]

    data = await fetch_market_data()
    _cache["market"] = {"data": data, "updated": now}
    return data


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
    btc, gold, stats, market = await asyncio.gather(
        get_btc_data(),
        get_gold_data(),
        get_platform_stats(),
        get_market_data()
    )
    
    return {
        "btc": btc,
        "gold": gold,
        "stats": stats,
        "market": market,
        "timestamp": datetime.now().isoformat()
    }
