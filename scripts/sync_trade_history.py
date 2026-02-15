#!/usr/bin/env python3
"""
Sync Trade History Script
=========================
Синхронизирует историю закрытых сделок с Bybit API в trade_logs.

Использование:
    python3 sync_trade_history.py --user USER_ID --days 30 --account real
    python3 sync_trade_history.py --user USER_ID --days 30 --account both
    python3 sync_trade_history.py --all --days 7  # Для всех активных пользователей
"""

import asyncio
import argparse
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Optional

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import db
from db import add_trade_log, get_user_config, get_active_positions

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bybit API URLs
BYBIT_DEMO_URL = "https://api-demo.bybit.com"
BYBIT_REAL_URL = "https://api.bybit.com"


async def fetch_closed_pnl_history(
    user_id: int, 
    days: int = 30, 
    account_type: str = "demo",
    symbol: str = None
) -> list:
    """
    Fetch closed PnL history from Bybit API.
    
    Args:
        user_id: Telegram user ID
        days: Number of days to fetch
        account_type: 'demo' or 'real'
        symbol: Optional symbol filter
        
    Returns:
        List of closed position records
    """
    # Import bot module for API access
    try:
        from bot import _bybit_request, get_user_credentials, MissingAPICredentials
    except ImportError:
        logger.error("Cannot import bot module")
        return []
    
    # Check credentials
    api_key, api_secret = get_user_credentials(user_id, account_type)
    if not api_key or not api_secret:
        logger.warning(f"[{user_id}] No {account_type} API credentials")
        return []
    
    end_ts = int(datetime.now().timestamp() * 1000)
    start_ts = end_ts - days * 24 * 60 * 60 * 1000
    
    all_records = []
    
    # Bybit API limits to 7 days per request
    chunk_days = 7
    chunk_end = end_ts
    
    while chunk_end > start_ts:
        chunk_start = max(chunk_end - chunk_days * 24 * 60 * 60 * 1000, start_ts)
        
        cursor = None
        while True:
            params = {
                "category": "linear",
                "startTime": chunk_start,
                "endTime": chunk_end,
                "limit": 100,
            }
            if symbol:
                params["symbol"] = symbol
            if cursor:
                params["cursor"] = cursor
            
            try:
                res = await _bybit_request(
                    user_id, "GET", "/v5/position/closed-pnl", 
                    params=params, account_type=account_type
                )
                
                records = res.get("list", [])
                all_records.extend(records)
                
                cursor = res.get("nextPageCursor")
                if not cursor or len(records) < 100:
                    break
                    
            except MissingAPICredentials:
                logger.warning(f"[{user_id}] Missing API credentials for {account_type}")
                return all_records
            except Exception as e:
                logger.error(f"[{user_id}] API error: {e}")
                break
        
        chunk_end = chunk_start
    
    logger.info(f"[{user_id}] Fetched {len(all_records)} closed PnL records for {account_type}")
    return all_records


def detect_strategy_from_symbol_and_time(user_id: int, symbol: str, entry_ts: int) -> Optional[str]:
    """
    Try to detect strategy from signals table based on symbol and time.
    """
    try:
        from db import get_conn
        with get_conn() as conn:
            # Look for signal within 5 minutes of entry
            row = conn.execute("""
                SELECT source, raw_message FROM signals 
                WHERE user_id = ? AND symbol = ? 
                AND ABS(ts - ?) < 300
                ORDER BY ABS(ts - ?) ASC
                LIMIT 1
            """, (user_id, symbol, entry_ts, entry_ts)).fetchone()
            
            if row:
                source = row[0] or ""
                raw_msg = row[1] or ""
                
                # Detect strategy from signal
                raw_upper = (source + raw_msg).upper()
                if "SCRYPTOMERA" in raw_upper or "DROP CATCH" in raw_msg or "DROPSBOT" in raw_upper or "TIGHTBTC" in raw_upper:
                    return "scryptomera"
                elif "SCALPER" in raw_upper and "⚡" in raw_msg:
                    return "scalper"
                elif "ELCARO" in raw_upper or "🔥 ELCARO" in raw_msg:
                    return "elcaro"
                elif "FIBONACCI" in raw_upper:
                    return "fibonacci"
                elif "OI" in raw_upper or "OPEN INTEREST" in raw_upper:
                    return "oi"
                elif "RSI" in raw_upper or "BB" in raw_upper or "BOLLINGER" in raw_upper:
                    return "rsi_bb"
    except Exception as e:
        logger.debug(f"Strategy detection error: {e}")
    
    return None


def check_trade_exists(user_id: int, symbol: str, side: str, entry_price: float, exit_price: float) -> bool:
    """Check if trade already exists in trade_logs."""
    try:
        from db import get_conn
        with get_conn() as conn:
            row = conn.execute("""
                SELECT id FROM trade_logs 
                WHERE user_id = ? AND symbol = ? AND side = ?
                AND ABS(entry_price - ?) < 0.0001
                AND ABS(exit_price - ?) < 0.0001
                LIMIT 1
            """, (user_id, symbol, side, entry_price, exit_price)).fetchone()
            return row is not None
    except Exception:
        return False


async def sync_user_trades(
    user_id: int, 
    days: int = 30, 
    account_type: str = "demo",
    dry_run: bool = False
) -> dict:
    """
    Sync trades for a specific user from Bybit API to trade_logs.
    
    Returns:
        dict with sync statistics
    """
    stats = {
        "fetched": 0,
        "imported": 0,
        "skipped_exists": 0,
        "skipped_error": 0,
        "strategies_detected": {}
    }
    
    records = await fetch_closed_pnl_history(user_id, days, account_type)
    stats["fetched"] = len(records)
    
    for rec in records:
        try:
            symbol = rec.get("symbol", "")
            side = rec.get("side", "")  # "Buy" or "Sell"
            entry_price = float(rec.get("avgEntryPrice", 0))
            exit_price = float(rec.get("avgExitPrice", 0))
            closed_size = float(rec.get("closedSize", 0))
            closed_pnl = float(rec.get("closedPnl", 0))
            leverage = int(float(rec.get("leverage", 1)))
            created_time = int(rec.get("createdTime", 0))
            updated_time = int(rec.get("updatedTime", 0))
            
            # Skip if already exists
            if check_trade_exists(user_id, symbol, side, entry_price, exit_price):
                stats["skipped_exists"] += 1
                continue
            
            # Calculate PnL percentage (price change, not ROE)
            if entry_price > 0:
                if side == "Buy":
                    pnl_pct = (exit_price / entry_price - 1) * 100
                else:
                    pnl_pct = (1 - exit_price / entry_price) * 100
            else:
                pnl_pct = 0.0
            
            # Try to detect strategy
            entry_ts = created_time // 1000 if created_time else 0
            strategy = detect_strategy_from_symbol_and_time(user_id, symbol, entry_ts)
            
            if not strategy:
                # Check active_positions for strategy (Bybit sync only)
                positions = get_active_positions(user_id, account_type=account_type, exchange="bybit")
                for pos in positions:
                    if pos.get("symbol") == symbol:
                        strategy = pos.get("strategy")
                        break
            
            # Default to "unknown" if no strategy detected
            if not strategy:
                strategy = "unknown"
            
            # Track detected strategies
            stats["strategies_detected"][strategy] = stats["strategies_detected"].get(strategy, 0) + 1
            
            # Determine exit reason from PnL and price movement
            cfg = get_user_config(user_id) or {}
            default_sl = float(cfg.get("sl_percent", 30.0))
            default_tp = float(cfg.get("tp_percent", 25.0))
            
            if closed_pnl > 0:
                exit_reason = "TP" if pnl_pct >= default_tp * 0.8 else "TRAILING"
            elif closed_pnl < 0:
                exit_reason = "SL" if abs(pnl_pct) >= default_sl * 0.8 else "MANUAL"
            else:
                exit_reason = "MANUAL"
            
            if dry_run:
                logger.info(f"[DRY RUN] Would import: {symbol} {side} PnL={closed_pnl:.2f} strategy={strategy}")
                stats["imported"] += 1
                continue
            
            # Add to trade_logs
            add_trade_log(
                user_id=user_id,
                signal_id=None,
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                exit_price=exit_price,
                exit_reason=exit_reason,
                pnl=closed_pnl,
                pnl_pct=pnl_pct,
                strategy=strategy,
                account_type=account_type,
                exchange="bybit",
                entry_ts=created_time,
                exit_ts=updated_time,
            )
            
            stats["imported"] += 1
            logger.debug(f"[{user_id}] Imported: {symbol} {side} PnL={closed_pnl:.2f} strategy={strategy}")
            
        except Exception as e:
            logger.error(f"[{user_id}] Error processing record: {e}")
            stats["skipped_error"] += 1
    
    return stats


async def sync_all_users(days: int = 7, dry_run: bool = False):
    """Sync trades for all active users."""
    try:
        from bot import get_active_trading_users
        users = get_active_trading_users()
    except Exception:
        # Fallback: get users from database
        from db import get_conn
        with get_conn() as conn:
            rows = conn.execute("""
                SELECT DISTINCT user_id FROM users 
                WHERE (demo_api_key IS NOT NULL OR real_api_key IS NOT NULL)
                AND is_banned = 0
            """).fetchall()
            users = [row[0] for row in rows]
    
    logger.info(f"Syncing trades for {len(users)} users...")
    
    total_stats = {
        "users_processed": 0,
        "total_fetched": 0,
        "total_imported": 0,
        "total_skipped": 0,
    }
    
    for uid in users:
        try:
            # Check trading mode
            trading_mode = db.get_trading_mode(uid) or "demo"
            
            if trading_mode == "both":
                account_types = ["demo", "real"]
            else:
                account_types = [trading_mode]
            
            for acc_type in account_types:
                stats = await sync_user_trades(uid, days, acc_type, dry_run)
                total_stats["total_fetched"] += stats["fetched"]
                total_stats["total_imported"] += stats["imported"]
                total_stats["total_skipped"] += stats["skipped_exists"] + stats["skipped_error"]
            
            total_stats["users_processed"] += 1
            
        except Exception as e:
            logger.error(f"Error syncing user {uid}: {e}")
    
    return total_stats


async def main():
    parser = argparse.ArgumentParser(description="Sync trade history from Bybit API")
    parser.add_argument("--user", type=int, help="User ID to sync")
    parser.add_argument("--all", action="store_true", help="Sync all active users")
    parser.add_argument("--days", type=int, default=30, help="Number of days to sync (default: 30)")
    parser.add_argument("--account", choices=["demo", "real", "both"], default="both", 
                        help="Account type to sync (default: both)")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually import, just show what would be imported")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.all:
        stats = await sync_all_users(args.days, args.dry_run)
        print(f"\n{'='*50}")
        print(f"SYNC COMPLETE")
        print(f"{'='*50}")
        print(f"Users processed: {stats['users_processed']}")
        print(f"Total fetched: {stats['total_fetched']}")
        print(f"Total imported: {stats['total_imported']}")
        print(f"Total skipped: {stats['total_skipped']}")
        
    elif args.user:
        if args.account == "both":
            account_types = ["demo", "real"]
        else:
            account_types = [args.account]
        
        for acc_type in account_types:
            print(f"\nSyncing {acc_type} account for user {args.user}...")
            stats = await sync_user_trades(args.user, args.days, acc_type, args.dry_run)
            
            print(f"\n{'='*50}")
            print(f"SYNC RESULTS ({acc_type.upper()})")
            print(f"{'='*50}")
            print(f"Fetched from API: {stats['fetched']}")
            print(f"Imported to DB: {stats['imported']}")
            print(f"Skipped (exists): {stats['skipped_exists']}")
            print(f"Skipped (error): {stats['skipped_error']}")
            print(f"\nStrategies detected:")
            for strat, count in stats['strategies_detected'].items():
                print(f"  - {strat}: {count}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
