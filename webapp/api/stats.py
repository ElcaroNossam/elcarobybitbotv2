"""
Statistics API endpoints
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
import sys
import os
import logging

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from .auth import get_current_user

router = APIRouter(tags=["statistics"])


@router.get("/dashboard")
async def get_dashboard_stats(
    user = Depends(get_current_user),
    exchange: str = Query("all"),
    strategy: str = Query("all"),
    period: str = Query("30d")
):
    """Get comprehensive trading statistics for dashboard"""
    try:
        import db
        uid = user["user_id"]
        logger.debug(f"Dashboard stats: user_id={uid}, exchange={exchange}, strategy={strategy}, period={period}")
        
        # Parse period
        days = {"7d": 7, "30d": 30, "90d": 90, "all": 365}.get(period, 30)
        start_date = datetime.now() - timedelta(days=days)
        
        # Get trades from trade_logs table (where bot saves trades)
        # Note: exchange column may not exist in all rows - filter in Python
        trades = db.get_trade_logs_list(uid, limit=1000, 
                                        strategy=strategy if strategy != "all" else None,
                                        exchange=None) or []
        logger.debug(f"Trades returned: {len(trades)}")
        
        # Filter by exchange if specified
        if exchange and exchange != "all":
            trades = [t for t in trades if t.get("exchange", "bybit") == exchange]
            logger.debug(f"Trades after exchange filter: {len(trades)}")
        
        # Filter by period
        filtered_trades = []
        for t in trades:
            trade_time_str = t.get("time", "2024-01-01")
            try:
                if isinstance(trade_time_str, str):
                    trade_time = datetime.fromisoformat(trade_time_str.replace("Z", "+00:00"))
                else:
                    trade_time = datetime.now()
            except (ValueError, TypeError) as e:
                logger.debug(f"Failed to parse trade time '{trade_time_str}': {e}")
                trade_time = datetime.now()
            
            if trade_time >= start_date:
                filtered_trades.append(t)
        
        logger.debug(f"Filtered trades: {len(filtered_trades)} (period={days}d, start={start_date})")
        
        # Calculate summary statistics
        if not filtered_trades:
            return {
                "success": True,
                "data": {
                    "summary": {
                        "totalPnL": 0, "returnPct": 0, "totalTrades": 0,
                        "winRate": 0, "profitFactor": 0, "maxDrawdown": 0,
                        "avgWin": 0, "avgLoss": 0, "bestStreak": 0, "worstStreak": 0,
                        "avgDuration": "0h", "tradesPerDay": 0, "pnlChange": 0,
                        "wins": 0, "losses": 0, "maxDrawdownAbs": 0
                    },
                    "pnlHistory": [],
                    "byStrategy": {},
                    "byExchange": {},
                    "bySymbol": {},
                    "dailyPnL": {},
                    "topTrades": {"best": [], "worst": []}
                }
            }
        
        # Calculate stats
        wins = [t for t in filtered_trades if float(t.get("pnl", 0)) > 0]
        losses = [t for t in filtered_trades if float(t.get("pnl", 0)) < 0]
        
        total_pnl = sum(float(t.get("pnl", 0)) for t in filtered_trades)
        total_wins = sum(float(t.get("pnl", 0)) for t in wins)
        total_losses = abs(sum(float(t.get("pnl", 0)) for t in losses))
        
        win_rate = (len(wins) / len(filtered_trades) * 100) if filtered_trades else 0
        profit_factor = (total_wins / total_losses) if total_losses > 0 else total_wins
        avg_win = (total_wins / len(wins)) if wins else 0
        avg_loss = (total_losses / len(losses)) if losses else 0
        
        # Build PnL history (cumulative)
        pnl_history = []
        cumulative = 0
        daily_pnl = {}
        
        for t in sorted(filtered_trades, key=lambda x: x.get("time", "")):
            pnl = float(t.get("pnl", 0))
            cumulative += pnl
            date_str = t.get("time", "")[:10]
            
            pnl_history.append({
                "time": date_str,
                "daily": pnl,
                "cumulative": cumulative
            })
            
            if date_str in daily_pnl:
                daily_pnl[date_str] += pnl
            else:
                daily_pnl[date_str] = pnl
        
        # By strategy
        by_strategy = {}
        for t in filtered_trades:
            strat = t.get("strategy", "manual")
            if strat not in by_strategy:
                by_strategy[strat] = {"trades": 0, "wins": 0, "pnl": 0}
            by_strategy[strat]["trades"] += 1
            by_strategy[strat]["pnl"] += float(t.get("pnl", 0))
            if float(t.get("pnl", 0)) > 0:
                by_strategy[strat]["wins"] += 1
        
        for strat in by_strategy:
            by_strategy[strat]["winRate"] = (by_strategy[strat]["wins"] / by_strategy[strat]["trades"] * 100) if by_strategy[strat]["trades"] else 0
            by_strategy[strat]["avgPnl"] = by_strategy[strat]["pnl"] / by_strategy[strat]["trades"] if by_strategy[strat]["trades"] else 0
        
        # By exchange
        by_exchange = {}
        for t in filtered_trades:
            ex = t.get("exchange", "bybit")
            if ex not in by_exchange:
                by_exchange[ex] = {"trades": 0, "wins": 0, "pnl": 0}
            by_exchange[ex]["trades"] += 1
            by_exchange[ex]["pnl"] += float(t.get("pnl", 0))
            if float(t.get("pnl", 0)) > 0:
                by_exchange[ex]["wins"] += 1
        
        for ex in by_exchange:
            by_exchange[ex]["winRate"] = (by_exchange[ex]["wins"] / by_exchange[ex]["trades"] * 100) if by_exchange[ex]["trades"] else 0
            by_exchange[ex]["avgPnl"] = by_exchange[ex]["pnl"] / by_exchange[ex]["trades"] if by_exchange[ex]["trades"] else 0
        
        # By symbol
        by_symbol = {}
        for t in filtered_trades:
            sym = t.get("symbol", "UNKNOWN")
            if sym not in by_symbol:
                by_symbol[sym] = {"trades": 0, "wins": 0, "pnl": 0}
            by_symbol[sym]["trades"] += 1
            by_symbol[sym]["pnl"] += float(t.get("pnl", 0))
            if float(t.get("pnl", 0)) > 0:
                by_symbol[sym]["wins"] += 1
        
        for sym in by_symbol:
            by_symbol[sym]["winRate"] = (by_symbol[sym]["wins"] / by_symbol[sym]["trades"] * 100) if by_symbol[sym]["trades"] else 0
        
        # Top trades
        sorted_by_pnl = sorted(filtered_trades, key=lambda x: float(x.get("pnl", 0)), reverse=True)
        top_trades = {
            "best": sorted_by_pnl[:5],
            "worst": sorted_by_pnl[-5:][::-1]
        }
        
        # Calculate maxDrawdown and streaks properly
        max_drawdown = 0.0
        max_drawdown_abs = 0.0
        if pnl_history:
            # Extract cumulative values for drawdown calculation
            cumulative_values = [h["cumulative"] for h in pnl_history]
            peak = cumulative_values[0]
            for val in cumulative_values:
                if val > peak:
                    peak = val
                drawdown = peak - val
                if drawdown > max_drawdown_abs:
                    max_drawdown_abs = drawdown
                if peak > 0:
                    dd_pct = (drawdown / peak) * 100
                    if dd_pct > max_drawdown:
                        max_drawdown = dd_pct
        
        # Calculate best/worst streak
        best_streak = 0
        worst_streak = 0
        current_win_streak = 0
        current_loss_streak = 0
        for trade in sorted(filtered_trades, key=lambda x: x.get("time", x.get("created_at", ""))):
            pnl = float(trade.get("pnl", 0))
            if pnl > 0:
                current_win_streak += 1
                current_loss_streak = 0
                if current_win_streak > best_streak:
                    best_streak = current_win_streak
            elif pnl < 0:
                current_loss_streak += 1
                current_win_streak = 0
                if current_loss_streak > worst_streak:
                    worst_streak = current_loss_streak
        
        # Calculate returnPct: Use average trade size as base instead of hardcoded 10k
        # This gives a more realistic percentage return based on actual trading volume
        avg_trade_size = sum(abs(float(t.get("pnl", 0)) / max(abs(float(t.get("pnl_pct", 0.01) / 100)), 0.001)) 
                             for t in filtered_trades if float(t.get("pnl_pct", 0)) != 0) / max(len(filtered_trades), 1)
        estimated_capital = max(avg_trade_size * 10, 1000)  # Assume 10x leverage, minimum 1000
        return_pct = (total_pnl / estimated_capital) * 100 if estimated_capital > 0 else 0
        
        return {
            "success": True,
            "data": {
                "summary": {
                    "totalPnL": total_pnl,
                    "returnPct": round(return_pct, 2),
                    "totalTrades": len(filtered_trades),
                    "winRate": win_rate,
                    "profitFactor": profit_factor,
                    "maxDrawdown": round(max_drawdown, 2),
                    "avgWin": avg_win,
                    "avgLoss": avg_loss,
                    "bestStreak": best_streak,
                    "worstStreak": worst_streak,
                    "avgDuration": "2h",
                    "tradesPerDay": len(filtered_trades) / max(days, 1),
                    "pnlChange": 12.5,
                    "wins": len(wins),
                    "losses": len(losses),
                    "maxDrawdownAbs": round(max_drawdown_abs, 2)
                },
                "pnlHistory": pnl_history,
                "byStrategy": by_strategy,
                "byExchange": by_exchange,
                "bySymbol": by_symbol,
                "dailyPnL": daily_pnl,
                "topTrades": top_trades
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/pnl-history")
async def get_pnl_history(
    user = Depends(get_current_user),
    exchange: str = Query("bybit"),
    period: str = Query("7d")
):
    """Get PnL history for chart display"""
    try:
        import db
        uid = user["user_id"]
        logger.info(f"[PnL-API] Request from user {uid}, exchange={exchange}, period={period}")
        
        # Parse period
        days_map = {"24h": 1, "7d": 7, "30d": 30, "90d": 90, "all": 365}
        days = days_map.get(period, 7)
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Get trades from trade_logs table
        # Fix #9: Apply exchange filter if provided and column exists
        trades = db.get_trade_logs_list(uid, limit=500, exchange=exchange if exchange != "all" else None) or []
        logger.info(f"[PnL-API] User {uid}: fetched {len(trades)} trades (exchange filter: {exchange})")
        
        # Group by date
        daily_pnl = {}
        for t in trades:
            trade_time_str = t.get("time", "")
            if not trade_time_str:
                continue
            
            try:
                if isinstance(trade_time_str, (int, float)):
                    trade_time = datetime.fromtimestamp(trade_time_str)
                else:
                    trade_time = datetime.fromisoformat(str(trade_time_str).replace("Z", "+00:00"))
            except (ValueError, TypeError, OSError) as e:
                logger.debug(f"Failed to parse trade time '{trade_time_str}': {e}")
                continue
            
            if trade_time < start_date:
                continue
            
            date_key = trade_time.strftime("%Y-%m-%d")
            pnl = float(t.get("pnl", 0))
            
            if date_key not in daily_pnl:
                daily_pnl[date_key] = 0
            daily_pnl[date_key] += pnl
        
        # Sort by date and create arrays
        sorted_dates = sorted(daily_pnl.keys())
        
        # If no data, generate empty days
        if not sorted_dates:
            labels = []
            values = []
            for i in range(days):
                date = datetime.now() - timedelta(days=days - i - 1)
                labels.append(date.strftime("%b %d"))
                values.append(0)
        else:
            labels = [datetime.strptime(d, "%Y-%m-%d").strftime("%b %d") for d in sorted_dates]
            
            # Calculate cumulative PnL
            cumulative = 0
            values = []
            for d in sorted_dates:
                cumulative += daily_pnl[d]
                values.append(round(cumulative, 2))
        
        logger.info(f"[PnL-API] User {uid}: returning {len(labels)} data points, cumulative={cumulative if 'cumulative' in dir() else 0}")
        return {
            "labels": labels,
            "values": values,
            "period": period
        }
    except Exception as e:
        logger.error(f"[PnL-API] Error: {e}")
        return {"labels": [], "values": [], "error": str(e)}


@router.get("/strategy-report")
async def get_strategy_report(
    user = Depends(get_current_user),
    exchange: str = Query("all"),
    period: str = Query("30d")
):
    """Get detailed strategy performance report."""
    try:
        import db
        uid = user["user_id"]
        
        # Parse period
        days = {"7d": 7, "30d": 30, "90d": 90, "all": 365}.get(period, 30)
        start_date = datetime.now() - timedelta(days=days)
        
        # Get trades
        trades = db.get_trade_history(uid, limit=1000) or []
        
        # Filter by period and exchange
        filtered_trades = []
        for t in trades:
            try:
                trade_time = datetime.fromisoformat(t.get("time", "2024-01-01").replace("Z", ""))
            except (ValueError, TypeError) as e:
                logger.debug(f"Failed to parse trade time: {e}")
                continue
            if trade_time >= start_date:
                if exchange != "all" and t.get("exchange", "bybit") != exchange:
                    continue
                filtered_trades.append(t)
        
        # Build strategy report
        strategies = {}
        for t in filtered_trades:
            strat = t.get("strategy") or "manual"
            if strat not in strategies:
                strategies[strat] = {
                    "name": strat,
                    "trades": 0,
                    "wins": 0,
                    "losses": 0,
                    "pnl": 0,
                    "total_volume": 0,
                    "best_trade": None,
                    "worst_trade": None,
                    "avg_duration": 0,
                    "symbols": {},
                    "daily_pnl": {},
                    "current_streak": 0,
                    "max_win_streak": 0,
                    "max_loss_streak": 0
                }
            
            pnl = float(t.get("pnl", 0))
            size = float(t.get("size", 0))
            entry = float(t.get("entry_price", 0))
            
            strategies[strat]["trades"] += 1
            strategies[strat]["pnl"] += pnl
            strategies[strat]["total_volume"] += size * entry
            
            if pnl > 0:
                strategies[strat]["wins"] += 1
            elif pnl < 0:
                strategies[strat]["losses"] += 1
            
            # Best/worst trade
            if strategies[strat]["best_trade"] is None or pnl > strategies[strat]["best_trade"]["pnl"]:
                strategies[strat]["best_trade"] = {
                    "symbol": t.get("symbol"),
                    "pnl": pnl,
                    "time": t.get("time")
                }
            if strategies[strat]["worst_trade"] is None or pnl < strategies[strat]["worst_trade"]["pnl"]:
                strategies[strat]["worst_trade"] = {
                    "symbol": t.get("symbol"),
                    "pnl": pnl,
                    "time": t.get("time")
                }
            
            # Symbols
            symbol = t.get("symbol", "UNKNOWN")
            if symbol not in strategies[strat]["symbols"]:
                strategies[strat]["symbols"][symbol] = {"trades": 0, "pnl": 0}
            strategies[strat]["symbols"][symbol]["trades"] += 1
            strategies[strat]["symbols"][symbol]["pnl"] += pnl
            
            # Daily PnL
            date = t.get("time", "")[:10]
            if date not in strategies[strat]["daily_pnl"]:
                strategies[strat]["daily_pnl"][date] = 0
            strategies[strat]["daily_pnl"][date] += pnl
        
        # Calculate derived metrics
        result = []
        for strat_name, data in strategies.items():
            total = data["trades"]
            wins = data["wins"]
            losses = data["losses"]
            pnl = data["pnl"]
            
            win_rate = (wins / total * 100) if total > 0 else 0
            avg_pnl = pnl / total if total > 0 else 0
            
            # Calculate profit factor
            win_pnl = sum(t.get("pnl", 0) for t in filtered_trades 
                         if t.get("strategy") == strat_name and t.get("pnl", 0) > 0)
            loss_pnl = abs(sum(t.get("pnl", 0) for t in filtered_trades 
                              if t.get("strategy") == strat_name and t.get("pnl", 0) < 0))
            profit_factor = win_pnl / loss_pnl if loss_pnl > 0 else win_pnl
            
            # Top 3 symbols
            top_symbols = sorted(data["symbols"].items(), key=lambda x: x[1]["pnl"], reverse=True)[:3]
            
            result.append({
                "name": strat_name,
                "display_name": strat_name.replace("_", " ").title(),
                "trades": total,
                "wins": wins,
                "losses": losses,
                "win_rate": round(win_rate, 1),
                "pnl": round(pnl, 2),
                "avg_pnl": round(avg_pnl, 2),
                "profit_factor": round(profit_factor, 2),
                "total_volume": round(data["total_volume"], 2),
                "best_trade": data["best_trade"],
                "worst_trade": data["worst_trade"],
                "top_symbols": [{"symbol": s[0], "trades": s[1]["trades"], "pnl": round(s[1]["pnl"], 2)} for s in top_symbols],
                "daily_pnl": data["daily_pnl"]
            })
        
        # Sort by PnL
        result.sort(key=lambda x: x["pnl"], reverse=True)
        
        # Calculate totals
        totals = {
            "total_trades": sum(s["trades"] for s in result),
            "total_wins": sum(s["wins"] for s in result),
            "total_losses": sum(s["losses"] for s in result),
            "total_pnl": round(sum(s["pnl"] for s in result), 2),
            "overall_win_rate": 0,
            "best_strategy": result[0]["name"] if result else None,
            "worst_strategy": result[-1]["name"] if result else None
        }
        if totals["total_trades"] > 0:
            totals["overall_win_rate"] = round(totals["total_wins"] / totals["total_trades"] * 100, 1)
        
        return {
            "success": True,
            "strategies": result,
            "totals": totals,
            "period": period,
            "exchange": exchange
        }
    except Exception as e:
        logger.error(f"Strategy report error: {e}")
        return {"success": False, "error": str(e), "strategies": []}


@router.get("/positions-summary")
async def get_positions_summary(
    user = Depends(get_current_user),
    exchange: str = Query("all")
):
    """Get summary of current positions across exchanges."""
    try:
        import db
        uid = user["user_id"]
        
        # Get active positions from database
        positions = db.get_active_positions(uid)
        
        if not positions:
            return {
                "success": True,
                "positions": [],
                "summary": {
                    "total_positions": 0,
                    "total_pnl": 0,
                    "long_count": 0,
                    "short_count": 0,
                    "by_exchange": {},
                    "by_account_type": {}
                }
            }
        
        # Filter by exchange if needed
        if exchange != "all":
            positions = [p for p in positions if p.get("exchange", "bybit") == exchange]
        
        # Calculate summary
        summary = {
            "total_positions": len(positions),
            "total_pnl": sum(float(p.get("pnl", 0)) for p in positions),
            "long_count": sum(1 for p in positions if p.get("side") == "long"),
            "short_count": sum(1 for p in positions if p.get("side") == "short"),
            "by_exchange": {},
            "by_account_type": {},
            "by_symbol": {}
        }
        
        for p in positions:
            ex = p.get("exchange", "bybit")
            acc = p.get("account_type", "demo")
            sym = p.get("symbol", "")
            pnl = float(p.get("pnl", 0))
            
            if ex not in summary["by_exchange"]:
                summary["by_exchange"][ex] = {"count": 0, "pnl": 0}
            summary["by_exchange"][ex]["count"] += 1
            summary["by_exchange"][ex]["pnl"] += pnl
            
            if acc not in summary["by_account_type"]:
                summary["by_account_type"][acc] = {"count": 0, "pnl": 0}
            summary["by_account_type"][acc]["count"] += 1
            summary["by_account_type"][acc]["pnl"] += pnl
            
            if sym not in summary["by_symbol"]:
                summary["by_symbol"][sym] = {"count": 0, "pnl": 0}
            summary["by_symbol"][sym]["count"] += 1
            summary["by_symbol"][sym]["pnl"] += pnl
        
        return {
            "success": True,
            "positions": positions,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Positions summary error: {e}")
        return {"success": False, "error": str(e), "positions": [], "summary": {}}

