"""
Strategy Marketplace API
- Custom strategies CRUD
- Marketplace listing & purchasing
- Strategy ratings & rankings
- Market data integration
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sqlite3
import json
import time
import asyncio
from pathlib import Path

router = APIRouter()
DB_FILE = Path("bot.db")


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class IndicatorConfig(BaseModel):
    """Configuration for a single indicator"""
    name: str
    enabled: bool = True
    params: Dict[str, Any] = {}


class StrategyConfig(BaseModel):
    """Full strategy configuration"""
    name: str
    description: Optional[str] = None
    base_strategy: str = "custom"
    indicators: List[IndicatorConfig] = []
    entry_conditions: Dict[str, Any] = {}
    exit_conditions: Dict[str, Any] = {}
    risk_management: Dict[str, Any] = {"sl_percent": 2.0, "tp_percent": 4.0, "risk_per_trade": 1.0}
    timeframe: str = "1h"
    symbols: List[str] = ["BTCUSDT"]


class CreateStrategyRequest(BaseModel):
    config: StrategyConfig


class ListStrategyRequest(BaseModel):
    strategy_id: int
    price_ton: float = 0
    price_trc: int = 0


class PurchaseRequest(BaseModel):
    marketplace_id: int
    currency: str  # 'ton' or 'trc'


class RatingRequest(BaseModel):
    marketplace_id: int
    rating: int  # 1-5
    review: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# AVAILABLE INDICATORS (from our strategies)
# ═══════════════════════════════════════════════════════════════════════════════

AVAILABLE_INDICATORS = {
    "momentum": [
        {"id": "rsi", "name": "RSI", "params": {"period": 14, "overbought": 70, "oversold": 30}},
        {"id": "stoch_rsi", "name": "Stochastic RSI", "params": {"period": 14, "k_smooth": 3, "d_smooth": 3}},
        {"id": "macd", "name": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9}},
        {"id": "momentum", "name": "Momentum", "params": {"period": 10}},
        {"id": "roc", "name": "Rate of Change", "params": {"period": 12}},
    ],
    "trend": [
        {"id": "ema", "name": "EMA", "params": {"period": 20}},
        {"id": "sma", "name": "SMA", "params": {"period": 50}},
        {"id": "supertrend", "name": "SuperTrend", "params": {"period": 10, "multiplier": 3}},
        {"id": "adx", "name": "ADX", "params": {"period": 14, "threshold": 25}},
        {"id": "ichimoku", "name": "Ichimoku Cloud", "params": {"tenkan": 9, "kijun": 26, "senkou": 52}},
    ],
    "volatility": [
        {"id": "bb", "name": "Bollinger Bands", "params": {"period": 20, "std_dev": 2}},
        {"id": "atr", "name": "ATR", "params": {"period": 14}},
        {"id": "keltner", "name": "Keltner Channel", "params": {"period": 20, "multiplier": 2}},
        {"id": "donchian", "name": "Donchian Channel", "params": {"period": 20}},
    ],
    "volume": [
        {"id": "volume_profile", "name": "Volume Profile", "params": {"bins": 50}},
        {"id": "vwap", "name": "VWAP", "params": {}},
        {"id": "obv", "name": "OBV", "params": {}},
        {"id": "mfi", "name": "Money Flow Index", "params": {"period": 14}},
        {"id": "cvd", "name": "Cumulative Volume Delta", "params": {}},
    ],
    "orderflow": [
        {"id": "oi", "name": "Open Interest", "params": {"min_change_pct": 3}},
        {"id": "funding_rate", "name": "Funding Rate", "params": {"threshold": 0.01}},
        {"id": "liquidations", "name": "Liquidation Heatmap", "params": {}},
        {"id": "long_short_ratio", "name": "Long/Short Ratio", "params": {}},
    ],
    "smc": [  # Smart Money Concepts
        {"id": "fvg", "name": "Fair Value Gaps", "params": {"min_gap_pct": 0.3}},
        {"id": "order_blocks", "name": "Order Blocks", "params": {"lookback": 50}},
        {"id": "liquidity_zones", "name": "Liquidity Zones", "params": {}},
        {"id": "bos", "name": "Break of Structure", "params": {}},
        {"id": "choch", "name": "Change of Character", "params": {}},
        {"id": "fibo_zones", "name": "Fibonacci 141-161%", "params": {"zone_141": 1.41, "zone_161": 1.61}},
    ],
}


@router.get("/indicators")
async def get_available_indicators():
    """Get all available indicators grouped by category"""
    return {
        "success": True,
        "indicators": AVAILABLE_INDICATORS,
        "total": sum(len(v) for v in AVAILABLE_INDICATORS.values())
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM STRATEGIES CRUD
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/strategies/create")
async def create_strategy(user_id: int, request: CreateStrategyRequest):
    """Create a new custom strategy"""
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO custom_strategies 
            (user_id, name, description, config_json, base_strategy, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            request.config.name,
            request.config.description,
            json.dumps(request.config.dict()),
            request.config.base_strategy,
            int(time.time())
        ))
        conn.commit()
        strategy_id = cur.lastrowid
        
        return {
            "success": True,
            "strategy_id": strategy_id,
            "message": "Strategy created successfully"
        }
    finally:
        conn.close()


@router.get("/strategies/my")
async def get_my_strategies(user_id: int):
    """Get all strategies for a user"""
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT s.*, 
                   m.id as marketplace_id, m.price_ton, m.price_trc, m.total_sales, m.rating
            FROM custom_strategies s
            LEFT JOIN strategy_marketplace m ON s.id = m.strategy_id
            WHERE s.user_id = ?
            ORDER BY s.created_at DESC
        """, (user_id,))
        
        strategies = []
        for row in cur.fetchall():
            strategy = dict(row)
            strategy["config"] = json.loads(strategy.get("config_json", "{}"))
            strategies.append(strategy)
        
        return {"success": True, "strategies": strategies}
    finally:
        conn.close()


@router.get("/strategies/{strategy_id}")
async def get_strategy(strategy_id: int, user_id: int = None):
    """Get strategy details (only owner can see full config)"""
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT s.*, m.id as marketplace_id, m.price_ton, m.price_trc, 
                   m.total_sales, m.rating, m.rating_count
            FROM custom_strategies s
            LEFT JOIN strategy_marketplace m ON s.id = m.strategy_id
            WHERE s.id = ?
        """, (strategy_id,))
        
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        strategy = dict(row)
        
        # Only show full config to owner or buyer
        is_owner = user_id == strategy["user_id"]
        has_purchased = False
        
        if user_id and not is_owner and strategy.get("marketplace_id"):
            cur.execute("""
                SELECT 1 FROM strategy_purchases 
                WHERE buyer_id = ? AND marketplace_id = ? AND is_active = 1
            """, (user_id, strategy["marketplace_id"]))
            has_purchased = cur.fetchone() is not None
        
        if is_owner or has_purchased:
            strategy["config"] = json.loads(strategy.get("config_json", "{}"))
        else:
            # Hide config for non-owners
            strategy["config"] = {"hidden": True, "message": "Purchase to see full configuration"}
            del strategy["config_json"]
        
        return {"success": True, "strategy": strategy, "is_owner": is_owner, "has_purchased": has_purchased}
    finally:
        conn.close()


@router.put("/strategies/{strategy_id}")
async def update_strategy(strategy_id: int, user_id: int, request: CreateStrategyRequest):
    """Update a custom strategy (owner only)"""
    conn = get_db()
    try:
        cur = conn.cursor()
        
        # Verify ownership
        cur.execute("SELECT user_id FROM custom_strategies WHERE id = ?", (strategy_id,))
        row = cur.fetchone()
        if not row or row["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        cur.execute("""
            UPDATE custom_strategies 
            SET name = ?, description = ?, config_json = ?, updated_at = ?
            WHERE id = ?
        """, (
            request.config.name,
            request.config.description,
            json.dumps(request.config.dict()),
            int(time.time()),
            strategy_id
        ))
        conn.commit()
        
        return {"success": True, "message": "Strategy updated"}
    finally:
        conn.close()


@router.delete("/strategies/{strategy_id}")
async def delete_strategy(strategy_id: int, user_id: int):
    """Delete a custom strategy (owner only)"""
    conn = get_db()
    try:
        cur = conn.cursor()
        
        # Verify ownership
        cur.execute("SELECT user_id FROM custom_strategies WHERE id = ?", (strategy_id,))
        row = cur.fetchone()
        if not row or row["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        cur.execute("DELETE FROM custom_strategies WHERE id = ?", (strategy_id,))
        conn.commit()
        
        return {"success": True, "message": "Strategy deleted"}
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# MARKETPLACE
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/marketplace/list")
async def list_on_marketplace(user_id: int, request: ListStrategyRequest):
    """List a strategy on the marketplace (50/50 revenue share)"""
    conn = get_db()
    try:
        cur = conn.cursor()
        
        # Verify ownership
        cur.execute("SELECT user_id, name FROM custom_strategies WHERE id = ?", (request.strategy_id,))
        row = cur.fetchone()
        if not row or row["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Check if already listed
        cur.execute("SELECT id FROM strategy_marketplace WHERE strategy_id = ?", (request.strategy_id,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Strategy already listed")
        
        # Create marketplace listing
        cur.execute("""
            INSERT INTO strategy_marketplace 
            (strategy_id, seller_id, price_ton, price_trc, revenue_share, created_at)
            VALUES (?, ?, ?, ?, 0.5, ?)
        """, (request.strategy_id, user_id, request.price_ton, request.price_trc, int(time.time())))
        
        # Mark strategy as public
        cur.execute("UPDATE custom_strategies SET is_public = 1 WHERE id = ?", (request.strategy_id,))
        
        conn.commit()
        
        return {
            "success": True,
            "message": "Strategy listed on marketplace! Revenue will be split 50/50 with platform.",
            "marketplace_id": cur.lastrowid,
            "revenue_share": "50% goes to you, 50% to platform"
        }
    finally:
        conn.close()


@router.get("/marketplace")
async def get_marketplace(
    page: int = 1,
    limit: int = 20,
    sort_by: str = "rating",  # rating, sales, newest, price
    min_rating: float = 0,
    base_strategy: str = None
):
    """Browse marketplace listings"""
    conn = get_db()
    try:
        cur = conn.cursor()
        
        order_map = {
            "rating": "m.rating DESC",
            "sales": "m.total_sales DESC",
            "newest": "m.created_at DESC",
            "price_low": "m.price_ton ASC",
            "price_high": "m.price_ton DESC"
        }
        order = order_map.get(sort_by, "m.rating DESC")
        
        query = """
            SELECT m.*, s.name, s.description, s.base_strategy, s.win_rate, s.total_pnl,
                   u.user_id as seller_user_id
            FROM strategy_marketplace m
            JOIN custom_strategies s ON m.strategy_id = s.id
            JOIN users u ON m.seller_id = u.user_id
            WHERE m.is_active = 1 AND m.rating >= ?
        """
        params = [min_rating]
        
        if base_strategy:
            query += " AND s.base_strategy = ?"
            params.append(base_strategy)
        
        query += f" ORDER BY {order} LIMIT ? OFFSET ?"
        params.extend([limit, (page - 1) * limit])
        
        cur.execute(query, params)
        
        listings = []
        for row in cur.fetchall():
            listing = dict(row)
            listing["revenue_share_info"] = "50% creator / 50% platform"
            listings.append(listing)
        
        # Get total count
        cur.execute("SELECT COUNT(*) FROM strategy_marketplace WHERE is_active = 1")
        row = cur.fetchone()
        total = row[0] if row else 0
        
        return {
            "success": True,
            "listings": listings,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
    finally:
        conn.close()


@router.post("/marketplace/purchase")
async def purchase_strategy(user_id: int, request: PurchaseRequest):
    """Purchase a strategy from marketplace"""
    conn = get_db()
    try:
        cur = conn.cursor()
        
        # Get marketplace listing
        cur.execute("""
            SELECT m.*, s.name, s.user_id as creator_id
            FROM strategy_marketplace m
            JOIN custom_strategies s ON m.strategy_id = s.id
            WHERE m.id = ? AND m.is_active = 1
        """, (request.marketplace_id,))
        
        listing = cur.fetchone()
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")
        
        listing = dict(listing)
        
        # Check if already purchased
        cur.execute("""
            SELECT id FROM strategy_purchases 
            WHERE buyer_id = ? AND marketplace_id = ? AND is_active = 1
        """, (user_id, request.marketplace_id))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Already purchased")
        
        # Cannot buy own strategy
        if listing["creator_id"] == user_id:
            raise HTTPException(status_code=400, detail="Cannot purchase your own strategy")
        
        # Get price
        price = listing["price_ton"] if request.currency == "ton" else listing["price_trc"]
        seller_share = price * 0.5
        platform_share = price * 0.5
        
        # TODO: Integrate with TRC payment system (blockchain.py)
        # For now, record the purchase (payment verification should happen separately)
        
        cur.execute("""
            INSERT INTO strategy_purchases 
            (buyer_id, marketplace_id, strategy_id, seller_id, amount_paid, currency, seller_share, platform_share, purchased_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, request.marketplace_id, listing["strategy_id"], listing["seller_id"],
            price, request.currency, seller_share, platform_share, int(time.time())
        ))
        
        # Update sales count
        cur.execute("""
            UPDATE strategy_marketplace 
            SET total_sales = total_sales + 1, total_revenue = total_revenue + ?
            WHERE id = ?
        """, (price, request.marketplace_id))
        
        conn.commit()
        
        return {
            "success": True,
            "message": f"Strategy '{listing['name']}' purchased successfully!",
            "amount_paid": price,
            "currency": request.currency,
            "seller_gets": seller_share,
            "access_granted": True
        }
    finally:
        conn.close()


@router.get("/marketplace/purchased")
async def get_purchased_strategies(user_id: int):
    """Get strategies purchased by user"""
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.*, s.name, s.description, s.config_json, s.win_rate, s.total_pnl
            FROM strategy_purchases p
            JOIN custom_strategies s ON p.strategy_id = s.id
            WHERE p.buyer_id = ? AND p.is_active = 1
            ORDER BY p.purchased_at DESC
        """, (user_id,))
        
        purchases = []
        for row in cur.fetchall():
            purchase = dict(row)
            purchase["config"] = json.loads(purchase.get("config_json", "{}"))
            del purchase["config_json"]
            purchases.append(purchase)
        
        return {"success": True, "purchases": purchases, "strategies": purchases}
    finally:
        conn.close()


# Alias for frontend compatibility
@router.get("/purchases")
async def get_purchases_alias(user_id: int):
    """Alias for /marketplace/purchased"""
    return await get_purchased_strategies(user_id)


# ═══════════════════════════════════════════════════════════════════════════════
# RATINGS & RANKINGS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/marketplace/rate")
async def rate_strategy(user_id: int, request: RatingRequest):
    """Rate a purchased strategy"""
    if not 1 <= request.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")
    
    conn = get_db()
    try:
        cur = conn.cursor()
        
        # Verify purchase
        cur.execute("""
            SELECT id FROM strategy_purchases 
            WHERE buyer_id = ? AND marketplace_id = ? AND is_active = 1
        """, (user_id, request.marketplace_id))
        if not cur.fetchone():
            raise HTTPException(status_code=403, detail="Must purchase strategy to rate")
        
        # Insert or update rating
        cur.execute("""
            INSERT OR REPLACE INTO strategy_ratings 
            (marketplace_id, user_id, rating, review, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (request.marketplace_id, user_id, request.rating, request.review, int(time.time())))
        
        # Update average rating
        cur.execute("""
            UPDATE strategy_marketplace 
            SET rating = (SELECT AVG(rating) FROM strategy_ratings WHERE marketplace_id = ?),
                rating_count = (SELECT COUNT(*) FROM strategy_ratings WHERE marketplace_id = ?)
            WHERE id = ?
        """, (request.marketplace_id, request.marketplace_id, request.marketplace_id))
        
        conn.commit()
        
        return {"success": True, "message": "Rating submitted"}
    finally:
        conn.close()


@router.get("/rankings/top")
async def get_top_strategies(
    strategy_type: str = "all",  # 'system', 'custom', 'all'
    limit: int = 20
):
    """Get top performing strategies (for display, hidden from marketplace)"""
    conn = get_db()
    try:
        cur = conn.cursor()
        
        query = """
            SELECT * FROM top_strategies
            WHERE 1=1
        """
        params = []
        
        if strategy_type != "all":
            query += " AND strategy_type = ?"
            params.append(strategy_type)
        
        query += " ORDER BY rank ASC, win_rate DESC LIMIT ?"
        params.append(limit)
        
        cur.execute(query, params)
        
        strategies = []
        for row in cur.fetchall():
            strategy = dict(row)
            if strategy.get("config_json"):
                strategy["config"] = json.loads(strategy["config_json"])
                del strategy["config_json"]
            strategies.append(strategy)
        
        return {"success": True, "rankings": strategies}
    finally:
        conn.close()


@router.get("/rankings/custom")
async def get_custom_strategy_rankings(page: int = 1, limit: int = 50):
    """Get rankings of all custom strategies by performance"""
    conn = get_db()
    try:
        cur = conn.cursor()
        
        cur.execute("""
            SELECT s.id, s.name, s.base_strategy, s.win_rate, s.total_pnl, 
                   s.total_trades, s.backtest_score, s.is_public,
                   m.rating, m.total_sales,
                   ROW_NUMBER() OVER (ORDER BY s.win_rate DESC, s.total_pnl DESC) as rank
            FROM custom_strategies s
            LEFT JOIN strategy_marketplace m ON s.id = m.strategy_id
            WHERE s.is_active = 1
            ORDER BY s.win_rate DESC, s.total_pnl DESC
            LIMIT ? OFFSET ?
        """, (limit, (page - 1) * limit))
        
        rankings = []
        for row in cur.fetchall():
            ranking = dict(row)
            # Mark private strategies
            ranking["visibility"] = "public" if ranking["is_public"] else "private"
            rankings.append(ranking)
        
        return {"success": True, "rankings": rankings, "page": page}
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# MARKET DATA
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/market/overview")
async def get_market_overview():
    """Get market overview with key metrics from exchanges"""
    import aiohttp
    
    try:
        data = {
            "btc": {},
            "eth": {},
            "top_movers": [],
            "funding_rates": [],
            "oi_changes": []
        }
        
        async with aiohttp.ClientSession() as session:
            # Parallel fetch: BTC, ETH, and all tickers
            async def fetch_btc():
                async with session.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT") as resp:
                    if resp.status == 200:
                        return await resp.json()
                return None
            
            async def fetch_eth():
                async with session.get("https://api.binance.com/api/v3/ticker/24hr?symbol=ETHUSDT") as resp:
                    if resp.status == 200:
                        return await resp.json()
                return None
            
            async def fetch_all_tickers():
                async with session.get("https://api.binance.com/api/v3/ticker/24hr") as resp:
                    if resp.status == 200:
                        return await resp.json()
                return None
            
            # Run all requests in parallel
            btc, eth, tickers = await asyncio.gather(
                fetch_btc(),
                fetch_eth(),
                fetch_all_tickers(),
                return_exceptions=True
            )
            
            # Process BTC
            if btc and not isinstance(btc, Exception):
                data["btc"] = {
                    "price": float(btc["lastPrice"]),
                    "change_24h": float(btc["priceChangePercent"]),
                    "volume_24h": float(btc["quoteVolume"]),
                    "high_24h": float(btc["highPrice"]),
                    "low_24h": float(btc["lowPrice"])
                }
            
            # Process ETH
            if eth and not isinstance(eth, Exception):
                data["eth"] = {
                    "price": float(eth["lastPrice"]),
                    "change_24h": float(eth["priceChangePercent"]),
                    "volume_24h": float(eth["quoteVolume"])
                }
            
            # Process top movers
            if tickers and not isinstance(tickers, Exception):
                usdt_pairs = [t for t in tickers if t["symbol"].endswith("USDT") and float(t["quoteVolume"]) > 10000000]
                sorted_gainers = sorted(usdt_pairs, key=lambda x: float(x["priceChangePercent"]), reverse=True)[:5]
                sorted_losers = sorted(usdt_pairs, key=lambda x: float(x["priceChangePercent"]))[:5]
                
                data["top_movers"] = {
                    "gainers": [{"symbol": t["symbol"], "change": float(t["priceChangePercent"])} for t in sorted_gainers],
                    "losers": [{"symbol": t["symbol"], "change": float(t["priceChangePercent"])} for t in sorted_losers]
                }
        
        return {"success": True, "data": data, "timestamp": int(time.time())}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/market/symbol/{symbol}")
async def get_symbol_data(symbol: str):
    """Get detailed data for a specific symbol"""
    import aiohttp
    
    try:
        data = {"symbol": symbol, "indicators": {}}
        
        async with aiohttp.ClientSession() as session:
            # Parallel fetch: ticker and klines
            async def fetch_ticker():
                async with session.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}") as resp:
                    if resp.status == 200:
                        return await resp.json()
                return None
            
            async def fetch_klines():
                async with session.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100") as resp:
                    if resp.status == 200:
                        return await resp.json()
                return None
            
            ticker, klines = await asyncio.gather(
                fetch_ticker(),
                fetch_klines(),
                return_exceptions=True
            )
            
            # Process ticker
            if ticker and not isinstance(ticker, Exception):
                data["ticker"] = {
                    "price": float(ticker["lastPrice"]),
                    "change_24h": float(ticker["priceChangePercent"]),
                    "volume_24h": float(ticker["quoteVolume"]),
                    "high_24h": float(ticker["highPrice"]),
                    "low_24h": float(ticker["lowPrice"]),
                    "trades_24h": int(ticker["count"])
                }
            
            # Process klines and calculate indicators
            if klines and not isinstance(klines, Exception):
                closes = [float(k[4]) for k in klines]
                
                # Calculate RSI
                if len(closes) >= 15:
                    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
                    gains = [d if d > 0 else 0 for d in deltas[-14:]]
                    losses = [-d if d < 0 else 0 for d in deltas[-14:]]
                    avg_gain = sum(gains) / 14
                    avg_loss = sum(losses) / 14
                    rs = avg_gain / avg_loss if avg_loss > 0 else 100
                    rsi = 100 - (100 / (1 + rs))
                    data["indicators"]["rsi"] = round(rsi, 2)
                
                # Calculate BB
                if len(closes) >= 20:
                    window = closes[-20:]
                    sma = sum(window) / 20
                    std = (sum((p - sma) ** 2 for p in window) / 20) ** 0.5
                    data["indicators"]["bb"] = {
                        "upper": round(sma + 2 * std, 2),
                        "middle": round(sma, 2),
                        "lower": round(sma - 2 * std, 2),
                        "position": round((closes[-1] - (sma - 2 * std)) / (4 * std) * 100, 1)  # 0-100%
                    }
        
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# SELLER DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/seller/stats")
async def get_seller_stats(user_id: int):
    """Get seller statistics and earnings"""
    conn = get_db()
    try:
        cur = conn.cursor()
        
        # Total earnings
        cur.execute("""
            SELECT SUM(seller_share) as total_earnings, currency
            FROM strategy_purchases
            WHERE seller_id = ?
            GROUP BY currency
        """, (user_id,))
        
        earnings = {}
        for row in cur.fetchall():
            earnings[row["currency"]] = row["total_earnings"]
        
        # Total sales
        cur.execute("""
            SELECT COUNT(*) as total_sales
            FROM strategy_purchases
            WHERE seller_id = ?
        """, (user_id,))
        row = cur.fetchone()
        total_sales = row["total_sales"] if row else 0
        
        # Listed strategies
        cur.execute("""
            SELECT m.*, s.name, s.win_rate
            FROM strategy_marketplace m
            JOIN custom_strategies s ON m.strategy_id = s.id
            WHERE m.seller_id = ?
        """, (user_id,))
        
        listings = [dict(row) for row in cur.fetchall()]
        
        # Pending payouts
        cur.execute("""
            SELECT SUM(amount) as pending, currency
            FROM seller_payouts
            WHERE seller_id = ? AND status = 'pending'
            GROUP BY currency
        """, (user_id,))
        
        pending = {}
        for row in cur.fetchall():
            pending[row["currency"]] = row["pending"]
        
        return {
            "success": True,
            "stats": {
                "total_earnings": earnings,
                "total_sales": total_sales,
                "active_listings": len(listings),
                "pending_payouts": pending,
                "listings": listings
            }
        }
    finally:
        conn.close()
