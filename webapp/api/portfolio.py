"""
Portfolio API - Spot/Futures Balance, PnL Analytics, Chart Data with Cluster Analysis
"""
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import db
from webapp.api.auth import get_current_user

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


# ═══════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════

class AssetBalance(BaseModel):
    """Balance for a single asset (spot or futures)"""
    asset: str
    free: float
    locked: float
    total: float
    usd_value: float
    pnl_24h: float = 0.0
    pnl_24h_pct: float = 0.0


class SpotPortfolio(BaseModel):
    """Spot holdings summary"""
    total_usd: float
    pnl: float
    pnl_pct: float
    assets: List[AssetBalance]


class FuturesPortfolio(BaseModel):
    """Futures portfolio summary"""
    total_equity: float
    available: float
    position_margin: float
    unrealized_pnl: float
    realized_pnl: float
    position_count: int


class PnLDataPoint(BaseModel):
    """Single PnL data point for chart"""
    timestamp: str  # ISO format
    pnl: float
    cumulative_pnl: float
    trade_count: int


class CandleCluster(BaseModel):
    """Cluster analysis for a single candle"""
    timestamp: str
    open_pnl: float
    high_pnl: float
    low_pnl: float
    close_pnl: float
    volume: float  # Total traded volume
    trade_count: int
    # Cluster breakdown
    long_count: int
    short_count: int
    long_pnl: float
    short_pnl: float
    win_count: int
    loss_count: int
    avg_win: float
    avg_loss: float
    # Strategy breakdown
    strategies: Dict[str, Dict[str, Any]]  # strategy -> {count, pnl, win_rate}
    # Symbol breakdown
    symbols: Dict[str, Dict[str, Any]]  # symbol -> {count, pnl}
    trades: List[Dict[str, Any]]  # Individual trades in this candle


class PortfolioSummary(BaseModel):
    """Complete portfolio summary"""
    spot: Optional[SpotPortfolio] = None
    futures: Optional[FuturesPortfolio] = None
    total_usd: float
    pnl_period: float  # PnL for selected period
    pnl_period_pct: float
    period: str  # "1d", "1w", "1m", "custom"
    chart_data: List[PnLDataPoint]
    candles: List[CandleCluster] = []


# ═══════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def get_period_dates(period: str, custom_start: str = None, custom_end: str = None) -> tuple:
    """Get start/end dates for period"""
    now = datetime.utcnow()
    
    if period == "1d":
        start = now - timedelta(days=1)
    elif period == "1w":
        start = now - timedelta(weeks=1)
    elif period == "1m":
        start = now - timedelta(days=30)
    elif period == "3m":
        start = now - timedelta(days=90)
    elif period == "1y":
        start = now - timedelta(days=365)
    elif period == "custom" and custom_start:
        try:
            start = datetime.fromisoformat(custom_start.replace('Z', '+00:00'))
            now = datetime.fromisoformat(custom_end.replace('Z', '+00:00')) if custom_end else now
        except:
            start = now - timedelta(days=7)
    else:
        start = now - timedelta(days=7)
    
    return start, now


async def get_spot_balance(user_id: int, account_type: str = "demo") -> SpotPortfolio:
    """Get spot balance for user"""
    try:
        # Get Bybit credentials
        creds = db.get_all_user_credentials(user_id)
        if not creds:
            return SpotPortfolio(total_usd=0, pnl=0, pnl_pct=0, assets=[])
        
        # Determine API keys
        if account_type in ("demo", "testnet"):
            api_key = creds.get("demo_api_key")
            api_secret = creds.get("demo_api_secret")
            base_url = "https://api-demo.bybit.com"
        else:
            api_key = creds.get("real_api_key")
            api_secret = creds.get("real_api_secret")
            base_url = "https://api.bybit.com"
        
        if not api_key or not api_secret:
            return SpotPortfolio(total_usd=0, pnl=0, pnl_pct=0, assets=[])
        
        import aiohttp
        import hmac
        import hashlib
        import time
        
        timestamp = str(int(time.time() * 1000))
        recv_window = "5000"
        params = "accountType=UNIFIED"
        
        sign_str = timestamp + api_key + recv_window + params
        signature = hmac.new(
            api_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            "X-BAPI-API-KEY": api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-SIGN": signature,
            "X-BAPI-RECV-WINDOW": recv_window,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{base_url}/v5/account/wallet-balance?{params}",
                headers=headers
            ) as resp:
                data = await resp.json()
        
        if data.get("retCode") != 0:
            logger.warning(f"Bybit spot balance error: {data}")
            return SpotPortfolio(total_usd=0, pnl=0, pnl_pct=0, assets=[])
        
        wallet_list = data.get("result", {}).get("list", [])
        if not wallet_list:
            return SpotPortfolio(total_usd=0, pnl=0, pnl_pct=0, assets=[])
        
        wallet = wallet_list[0]
        coins = wallet.get("coin", [])
        
        assets = []
        total_usd = 0.0
        
        for coin in coins:
            usd_value = float(coin.get("usdValue", 0))
            if usd_value < 1:  # Skip dust
                continue
            
            asset = AssetBalance(
                asset=coin.get("coin", ""),
                free=float(coin.get("availableToWithdraw", 0)),
                locked=float(coin.get("locked", 0)),
                total=float(coin.get("walletBalance", 0)),
                usd_value=usd_value,
                pnl_24h=float(coin.get("unrealisedPnl", 0)),
                pnl_24h_pct=0
            )
            assets.append(asset)
            total_usd += usd_value
        
        # Sort by USD value
        assets.sort(key=lambda x: x.usd_value, reverse=True)
        
        return SpotPortfolio(
            total_usd=total_usd,
            pnl=0,  # Would need historical data
            pnl_pct=0,
            assets=assets
        )
    except Exception as e:
        logger.error(f"Error getting spot balance: {e}")
        return SpotPortfolio(total_usd=0, pnl=0, pnl_pct=0, assets=[])


async def get_futures_balance(user_id: int, account_type: str = "demo") -> FuturesPortfolio:
    """Get futures balance for user"""
    try:
        creds = db.get_all_user_credentials(user_id)
        if not creds:
            return FuturesPortfolio(
                total_equity=0, available=0, position_margin=0,
                unrealized_pnl=0, realized_pnl=0, position_count=0
            )
        
        # Determine API keys
        if account_type in ("demo", "testnet"):
            api_key = creds.get("demo_api_key")
            api_secret = creds.get("demo_api_secret")
            base_url = "https://api-demo.bybit.com"
        else:
            api_key = creds.get("real_api_key")
            api_secret = creds.get("real_api_secret")
            base_url = "https://api.bybit.com"
        
        if not api_key or not api_secret:
            return FuturesPortfolio(
                total_equity=0, available=0, position_margin=0,
                unrealized_pnl=0, realized_pnl=0, position_count=0
            )
        
        import aiohttp
        import hmac
        import hashlib
        import time
        
        timestamp = str(int(time.time() * 1000))
        recv_window = "5000"
        params = "accountType=UNIFIED"
        
        sign_str = timestamp + api_key + recv_window + params
        signature = hmac.new(
            api_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            "X-BAPI-API-KEY": api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-SIGN": signature,
            "X-BAPI-RECV-WINDOW": recv_window,
        }
        
        # Get balance
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{base_url}/v5/account/wallet-balance?{params}",
                headers=headers
            ) as resp:
                balance_data = await resp.json()
            
            # Get positions count
            params2 = "category=linear&settleCoin=USDT"
            sign_str2 = timestamp + api_key + recv_window + params2
            signature2 = hmac.new(
                api_secret.encode('utf-8'),
                sign_str2.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            headers["X-BAPI-SIGN"] = signature2
            
            async with session.get(
                f"{base_url}/v5/position/list?{params2}",
                headers=headers
            ) as resp:
                pos_data = await resp.json()
        
        if balance_data.get("retCode") != 0:
            logger.warning(f"Bybit futures balance error: {balance_data}")
            return FuturesPortfolio(
                total_equity=0, available=0, position_margin=0,
                unrealized_pnl=0, realized_pnl=0, position_count=0
            )
        
        wallet_list = balance_data.get("result", {}).get("list", [])
        if not wallet_list:
            return FuturesPortfolio(
                total_equity=0, available=0, position_margin=0,
                unrealized_pnl=0, realized_pnl=0, position_count=0
            )
        
        wallet = wallet_list[0]
        
        # Count active positions
        positions = pos_data.get("result", {}).get("list", [])
        position_count = sum(1 for p in positions if float(p.get("size", 0)) > 0)
        
        return FuturesPortfolio(
            total_equity=float(wallet.get("totalEquity", 0)),
            available=float(wallet.get("totalAvailableBalance", 0)),
            position_margin=float(wallet.get("totalPositionIM", 0)),
            unrealized_pnl=float(wallet.get("totalUnrealisedPnl", 0)),
            realized_pnl=0,  # Would need historical
            position_count=position_count
        )
    except Exception as e:
        logger.error(f"Error getting futures balance: {e}")
        return FuturesPortfolio(
            total_equity=0, available=0, position_margin=0,
            unrealized_pnl=0, realized_pnl=0, position_count=0
        )


def get_trades_for_period(user_id: int, start: datetime, end: datetime, 
                          account_type: str = "demo", exchange: str = "bybit") -> List[Dict]:
    """Get trade logs for period from database"""
    from core.db_postgres import execute
    
    query = """
        SELECT id, symbol, side, entry_price, exit_price, pnl, pnl_pct, 
               strategy, ts, exit_reason, timeframe, account_type
        FROM trade_logs 
        WHERE user_id = %s 
          AND account_type = %s
          AND ts >= %s 
          AND ts <= %s
        ORDER BY ts ASC
    """
    
    rows = execute(query, (user_id, account_type, start, end))
    return [dict(r) for r in rows] if rows else []


def build_chart_data(trades: List[Dict], period: str) -> List[PnLDataPoint]:
    """Build chart data points from trades"""
    if not trades:
        return []
    
    # Determine bucket size based on period
    if period == "1d":
        bucket_hours = 1
    elif period == "1w":
        bucket_hours = 6
    elif period == "1m":
        bucket_hours = 24
    else:
        bucket_hours = 12
    
    # Group trades by bucket
    buckets = {}
    for trade in trades:
        ts = trade.get("ts")
        if not ts:
            continue
        
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        
        # Round to bucket
        bucket_ts = ts.replace(
            minute=0, second=0, microsecond=0,
            hour=(ts.hour // bucket_hours) * bucket_hours
        )
        bucket_key = bucket_ts.isoformat()
        
        if bucket_key not in buckets:
            buckets[bucket_key] = {"pnl": 0, "count": 0}
        
        buckets[bucket_key]["pnl"] += float(trade.get("pnl") or 0)
        buckets[bucket_key]["count"] += 1
    
    # Build data points with cumulative PnL
    data_points = []
    cumulative = 0.0
    
    for ts_key in sorted(buckets.keys()):
        bucket = buckets[ts_key]
        cumulative += bucket["pnl"]
        
        data_points.append(PnLDataPoint(
            timestamp=ts_key,
            pnl=bucket["pnl"],
            cumulative_pnl=cumulative,
            trade_count=bucket["count"]
        ))
    
    return data_points


def build_candle_clusters(trades: List[Dict], period: str) -> List[CandleCluster]:
    """Build candle data with cluster analysis from trades"""
    if not trades:
        return []
    
    # Determine candle duration based on period
    if period == "1d":
        candle_hours = 2
    elif period == "1w":
        candle_hours = 12
    elif period == "1m":
        candle_hours = 24
    else:
        candle_hours = 6
    
    # Group trades by candle
    candles_data = {}
    
    for trade in trades:
        ts = trade.get("ts")
        if not ts:
            continue
        
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        
        # Round to candle period
        candle_ts = ts.replace(
            minute=0, second=0, microsecond=0,
            hour=(ts.hour // candle_hours) * candle_hours
        )
        candle_key = candle_ts.isoformat()
        
        if candle_key not in candles_data:
            candles_data[candle_key] = {
                "trades": [],
                "pnls": [],
            }
        
        pnl = float(trade.get("pnl") or 0)
        candles_data[candle_key]["trades"].append(trade)
        candles_data[candle_key]["pnls"].append(pnl)
    
    # Build candle clusters
    candles = []
    cumulative_pnl = 0.0
    
    for candle_key in sorted(candles_data.keys()):
        data = candles_data[candle_key]
        trades_in_candle = data["trades"]
        pnls = data["pnls"]
        
        if not pnls:
            continue
        
        # Calculate OHLC of PnL (cumulative within candle)
        running_pnl = 0
        pnl_progression = [0]
        for p in pnls:
            running_pnl += p
            pnl_progression.append(running_pnl)
        
        open_pnl = cumulative_pnl
        close_pnl = cumulative_pnl + running_pnl
        high_pnl = cumulative_pnl + max(pnl_progression)
        low_pnl = cumulative_pnl + min(pnl_progression)
        
        # Cluster analysis
        long_trades = [t for t in trades_in_candle if t.get("side", "").lower() in ("buy", "long")]
        short_trades = [t for t in trades_in_candle if t.get("side", "").lower() in ("sell", "short")]
        
        wins = [t for t in trades_in_candle if (t.get("pnl") or 0) > 0]
        losses = [t for t in trades_in_candle if (t.get("pnl") or 0) < 0]
        
        long_pnl = sum(float(t.get("pnl") or 0) for t in long_trades)
        short_pnl = sum(float(t.get("pnl") or 0) for t in short_trades)
        
        avg_win = sum(float(t.get("pnl") or 0) for t in wins) / len(wins) if wins else 0
        avg_loss = sum(float(t.get("pnl") or 0) for t in losses) / len(losses) if losses else 0
        
        # Strategy breakdown
        strategies = {}
        for t in trades_in_candle:
            strat = t.get("strategy") or "unknown"
            if strat not in strategies:
                strategies[strat] = {"count": 0, "pnl": 0, "wins": 0}
            strategies[strat]["count"] += 1
            strategies[strat]["pnl"] += float(t.get("pnl") or 0)
            if (t.get("pnl") or 0) > 0:
                strategies[strat]["wins"] += 1
        
        for strat in strategies:
            cnt = strategies[strat]["count"]
            strategies[strat]["win_rate"] = (strategies[strat]["wins"] / cnt * 100) if cnt > 0 else 0
        
        # Symbol breakdown
        symbols = {}
        for t in trades_in_candle:
            sym = t.get("symbol") or "unknown"
            if sym not in symbols:
                symbols[sym] = {"count": 0, "pnl": 0}
            symbols[sym]["count"] += 1
            symbols[sym]["pnl"] += float(t.get("pnl") or 0)
        
        # Calculate volume (sum of position sizes)
        volume = sum(
            abs(float(t.get("entry_price") or 0)) * abs(float(t.get("exit_price") or 0) - float(t.get("entry_price") or 1))
            for t in trades_in_candle
        )
        
        # Simplified trade data for response
        simplified_trades = [
            {
                "id": t.get("id"),
                "symbol": t.get("symbol"),
                "side": t.get("side"),
                "pnl": float(t.get("pnl") or 0),
                "pnl_pct": float(t.get("pnl_pct") or 0),
                "strategy": t.get("strategy"),
                "exit_reason": t.get("exit_reason"),
                "ts": t.get("ts").isoformat() if hasattr(t.get("ts"), 'isoformat') else str(t.get("ts"))
            }
            for t in trades_in_candle
        ]
        
        candle = CandleCluster(
            timestamp=candle_key,
            open_pnl=open_pnl,
            high_pnl=high_pnl,
            low_pnl=low_pnl,
            close_pnl=close_pnl,
            volume=volume,
            trade_count=len(trades_in_candle),
            long_count=len(long_trades),
            short_count=len(short_trades),
            long_pnl=long_pnl,
            short_pnl=short_pnl,
            win_count=len(wins),
            loss_count=len(losses),
            avg_win=avg_win,
            avg_loss=avg_loss,
            strategies=strategies,
            symbols=symbols,
            trades=simplified_trades
        )
        
        candles.append(candle)
        cumulative_pnl = close_pnl
    
    return candles


# ═══════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════

@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(
    period: str = Query("1w", regex="^(1d|1w|1m|3m|1y|custom)$"),
    custom_start: Optional[str] = None,
    custom_end: Optional[str] = None,
    account_type: str = Query("demo"),
    exchange: str = Query("bybit"),
    user: dict = Depends(get_current_user)
):
    """
    Get complete portfolio summary with spot/futures balance,
    PnL analytics, and chart data with cluster analysis.
    
    Periods: 1d (day), 1w (week), 1m (month), 3m (quarter), 1y (year), custom
    """
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Get date range
    start_date, end_date = get_period_dates(period, custom_start, custom_end)
    
    # Fetch balances
    spot = await get_spot_balance(user_id, account_type)
    futures = await get_futures_balance(user_id, account_type)
    
    # Get trades for period
    trades = get_trades_for_period(user_id, start_date, end_date, account_type, exchange)
    
    # Calculate period PnL
    period_pnl = sum(float(t.get("pnl") or 0) for t in trades)
    total_equity = futures.total_equity if futures else 0
    period_pnl_pct = (period_pnl / total_equity * 100) if total_equity > 0 else 0
    
    # Build chart data
    chart_data = build_chart_data(trades, period)
    
    # Build candle clusters for interactive chart
    candles = build_candle_clusters(trades, period)
    
    return PortfolioSummary(
        spot=spot,
        futures=futures,
        total_usd=spot.total_usd + (futures.total_equity if futures else 0),
        pnl_period=period_pnl,
        pnl_period_pct=period_pnl_pct,
        period=period,
        chart_data=chart_data,
        candles=candles
    )


@router.get("/spot")
async def get_spot_portfolio(
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
):
    """Get spot portfolio with all assets"""
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")
    
    return await get_spot_balance(user_id, account_type)


@router.get("/futures")
async def get_futures_portfolio(
    account_type: str = Query("demo"),
    user: dict = Depends(get_current_user)
):
    """Get futures portfolio summary"""
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")
    
    return await get_futures_balance(user_id, account_type)


@router.get("/chart")
async def get_pnl_chart(
    period: str = Query("1w", regex="^(1d|1w|1m|3m|1y|custom)$"),
    custom_start: Optional[str] = None,
    custom_end: Optional[str] = None,
    account_type: str = Query("demo"),
    exchange: str = Query("bybit"),
    user: dict = Depends(get_current_user)
):
    """Get PnL chart data with cluster analysis candles"""
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")
    
    start_date, end_date = get_period_dates(period, custom_start, custom_end)
    trades = get_trades_for_period(user_id, start_date, end_date, account_type, exchange)
    
    return {
        "period": period,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "trade_count": len(trades),
        "total_pnl": sum(float(t.get("pnl") or 0) for t in trades),
        "chart_data": build_chart_data(trades, period),
        "candles": build_candle_clusters(trades, period)
    }


@router.get("/candle/{timestamp}")
async def get_candle_details(
    timestamp: str,
    account_type: str = Query("demo"),
    exchange: str = Query("bybit"),
    user: dict = Depends(get_current_user)
):
    """Get detailed cluster analysis for a specific candle"""
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")
    
    try:
        candle_dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except:
        raise HTTPException(status_code=400, detail="Invalid timestamp format")
    
    # Get trades around this candle (6 hour window)
    start = candle_dt - timedelta(hours=3)
    end = candle_dt + timedelta(hours=3)
    
    trades = get_trades_for_period(user_id, start, end, account_type, exchange)
    
    if not trades:
        return {"trades": [], "summary": None}
    
    # Build detailed analysis
    strategies = {}
    symbols = {}
    
    for t in trades:
        strat = t.get("strategy") or "unknown"
        if strat not in strategies:
            strategies[strat] = {"count": 0, "pnl": 0, "wins": 0, "trades": []}
        strategies[strat]["count"] += 1
        strategies[strat]["pnl"] += float(t.get("pnl") or 0)
        if (t.get("pnl") or 0) > 0:
            strategies[strat]["wins"] += 1
        strategies[strat]["trades"].append({
            "symbol": t.get("symbol"),
            "side": t.get("side"),
            "pnl": float(t.get("pnl") or 0),
            "pnl_pct": float(t.get("pnl_pct") or 0),
        })
        
        sym = t.get("symbol") or "unknown"
        if sym not in symbols:
            symbols[sym] = {"count": 0, "pnl": 0, "long_count": 0, "short_count": 0}
        symbols[sym]["count"] += 1
        symbols[sym]["pnl"] += float(t.get("pnl") or 0)
        if t.get("side", "").lower() in ("buy", "long"):
            symbols[sym]["long_count"] += 1
        else:
            symbols[sym]["short_count"] += 1
    
    total_pnl = sum(float(t.get("pnl") or 0) for t in trades)
    wins = sum(1 for t in trades if (t.get("pnl") or 0) > 0)
    
    return {
        "timestamp": timestamp,
        "trade_count": len(trades),
        "total_pnl": total_pnl,
        "win_rate": (wins / len(trades) * 100) if trades else 0,
        "strategies": strategies,
        "symbols": symbols,
        "trades": [
            {
                "id": t.get("id"),
                "symbol": t.get("symbol"),
                "side": t.get("side"),
                "entry_price": t.get("entry_price"),
                "exit_price": t.get("exit_price"),
                "pnl": float(t.get("pnl") or 0),
                "pnl_pct": float(t.get("pnl_pct") or 0),
                "strategy": t.get("strategy"),
                "exit_reason": t.get("exit_reason"),
                "ts": t.get("ts").isoformat() if hasattr(t.get("ts"), 'isoformat') else str(t.get("ts"))
            }
            for t in trades
        ]
    }
