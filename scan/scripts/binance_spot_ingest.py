"""
Binance Spot ingest script for continuous updates.

Fetches spot symbols and metrics from Binance Spot API and writes them into
the PostgreSQL database via Django ORM.

This version runs continuously, updating data every second.

Run from the project root:

    python scripts/binance_spot_ingest.py
"""

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List

import django
import requests


def setup_django() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()


BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")


# Global session for connection pooling
_http_session = None

def get_session():
    """Get or create a global HTTP session for connection pooling."""
    global _http_session
    if _http_session is None:
        _http_session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=500,  # МАКСИМУМ для 8 CPU - максимальная параллельность
            pool_maxsize=2000,    # МАКСИМУМ для 8 CPU - максимальный размер пула
            max_retries=2
        )
        _http_session.mount('https://', adapter)
    return _http_session


def fetch_tickers(retries: int = 10) -> List[Dict[str, Any]]:
    """Fetch all tickers with retry logic for rate limit errors.
    Only returns tickers for symbols that are traded on all three exchanges (Binance, Bybit, OKX).
    
    Args:
        retries: Number of retry attempts for rate limit errors (increased to 10 for better success)
    
    Returns:
        List of ticker dictionaries (filtered to allowed symbols only)
        Returns empty list if all retries fail (doesn't crash)
    """
    # REMOVED: Symbol filtering - show all USDT symbols
    # Користувач попросив показувати всі символи без фільтрації
    allowed_symbols = None
    
    for attempt in range(retries):
        try:
            resp = requests.get(f"{BINANCE_BASE_URL}/api/v3/ticker/24hr", timeout=10)
            
            # Handle rate limit errors (418, 429)
            if resp.status_code == 418 or resp.status_code == 429:
                # Check for Retry-After header (server tells us how long to wait)
                retry_after = resp.headers.get('Retry-After')
                if retry_after:
                    try:
                        wait_time = float(retry_after)
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Rate limit (418/429) - server says wait {wait_time:.1f}s (Retry-After header)")
                    except (ValueError, TypeError):
                        wait_time = None
                else:
                    wait_time = None
                
                # If no Retry-After header, calculate wait time based on attempt
                if wait_time is None:
                    # Binance rate limit resets every minute (1200 weight/min)
                    # First attempt: wait 70 seconds (to ensure we're past the minute boundary)
                    # Subsequent attempts: wait longer (2-3 minutes for repeated violations)
                    if attempt == 0:
                        wait_time = 70.0  # Wait for minute boundary + 10s buffer
                    elif attempt < 3:
                        wait_time = 120.0  # 2 minutes for repeated violations
                    else:
                        wait_time = 180.0  # 3 minutes for persistent violations
                
                if attempt < retries - 1:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Rate limit (418/429) on tickers, waiting {wait_time:.1f}s for limit reset... (attempt {attempt + 1}/{retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    # Last attempt failed - return empty list instead of crashing
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Failed to fetch tickers after {retries} attempts, using empty list")
                    return []
            
            resp.raise_for_status()
            data = resp.json()
            
            # Filter to only USDT symbols
            tickers = [item for item in data if item.get("symbol", "").endswith("USDT")]
            
            # Filter to only allowed symbols (if list is available)
            if allowed_symbols:
                tickers = [item for item in tickers if item.get("symbol") in allowed_symbols]
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Filtered to {len(tickers)} allowed symbols (from {len(data)} total)")
            
            return tickers
            
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                # Wait before retry (exponential backoff with longer delays)
                wait_time = (2 ** attempt) * 2.0
                wait_time = min(wait_time, 60.0)  # Cap at 60 seconds
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetching tickers, retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{retries})")
                time.sleep(wait_time)
                continue
            else:
                # Last attempt failed - return empty list instead of crashing
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Failed to fetch tickers after {retries} attempts: {e}, using empty list")
                return []


def fetch_klines(symbol: str, interval: str = "1m", limit: int = 1440, session: requests.Session = None, retries: int = 5) -> List[List]:
    """Fetch klines (candlestick) data for a symbol with retry logic.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')
        interval: Kline interval (1m, 5m, 15m, 1h, etc.)
        limit: Number of klines to fetch (max 1500, default 1440 for 1 day of 1m candles)
        session: Optional requests session for connection pooling
        retries: Number of retry attempts for rate limit errors (increased to 5 for better success rate)
    
    Returns:
        List of klines, where each kline is:
        [open_time, open, high, low, close, volume, close_time, quote_volume, trades, ...]
        Returns empty list [] only if ALL retries fail
    """
    client = session if session else requests
    
    for attempt in range(retries):
        try:
            url = f"{BINANCE_BASE_URL}/api/v3/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            resp = client.get(url, params=params, timeout=3)
            
            # Handle rate limit errors (418, 429)
            if resp.status_code == 418 or resp.status_code == 429:
                # Check for Retry-After header (server tells us how long to wait)
                retry_after = resp.headers.get('Retry-After')
                if retry_after:
                    try:
                        wait_time = float(retry_after)
                    except (ValueError, TypeError):
                        wait_time = None
                else:
                    wait_time = None
                
                # If no Retry-After header, calculate wait time based on attempt
                if wait_time is None:
                    # Binance rate limit resets every minute (1200 weight/min)
                    # First attempt: wait 70 seconds (to ensure we're past the minute boundary)
                    # Subsequent attempts: wait longer (2-3 minutes for repeated violations)
                    if attempt == 0:
                        wait_time = 70.0  # Wait for minute boundary + 10s buffer
                    elif attempt < 3:
                        wait_time = 120.0  # 2 minutes for repeated violations
                    else:
                        wait_time = 180.0  # 3 minutes for persistent violations
                
                if attempt < retries - 1:
                    time.sleep(wait_time)
                    continue
                else:
                    # Last attempt failed, return empty
                    return []
            
            resp.raise_for_status()
            return resp.json()  # ✅ DATA ARRIVES HERE on successful request
            
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                # Wait before retry (exponential backoff with longer delays)
                wait_time = (2 ** attempt) * 1.0  # 1s, 2s, 4s, 8s, 16s
                time.sleep(wait_time)
                continue
            else:
                # Last attempt failed
                return []
        except Exception as e:
            # Other errors - don't retry
            return []
    
    return []


def aggregate_klines_to_timeframe(klines_1m: List[List], minutes: int) -> Dict[str, Any]:
    """Aggregate 1m klines to a larger timeframe.
    
    Args:
        klines_1m: List of 1m klines
        minutes: Target timeframe in minutes (e.g., 5 for 5m, 15 for 15m)
    
    Returns:
        Dictionary with aggregated data
    """
    if not klines_1m or len(klines_1m) < minutes:
        return None
    
    # Take last N minutes of 1m candles
    relevant_klines = klines_1m[-minutes:]
    
    # Aggregate data
    open_price = Decimal(str(relevant_klines[0][1]))  # First open
    close_price = Decimal(str(relevant_klines[-1][4]))  # Last close
    high_price = max(Decimal(str(k[2])) for k in relevant_klines)  # Max high
    low_price = min(Decimal(str(k[3])) for k in relevant_klines)  # Min low
    volume = sum(Decimal(str(k[5])) for k in relevant_klines)  # Sum of volumes (base)
    quote_volume = sum(Decimal(str(k[7])) for k in relevant_klines)  # Sum of quote volumes (USDT)
    trades = sum(int(k[8]) for k in relevant_klines)  # Sum of trades
    
    # Calculate percentage change
    if open_price > 0:
        change_pct = ((close_price - open_price) / open_price) * Decimal("100")
    else:
        change_pct = Decimal("0")
    
    return {
        'open': open_price,
        'close': close_price,
        'high': high_price,
        'low': low_price,
        'volume': volume,
        'quote_volume': quote_volume,
        'trades': trades,
        'change_pct': change_pct
    }


def calculate_timeframe_data_from_klines(klines_1m: List[List]) -> Dict[str, Dict[str, Any]]:
    """Calculate all timeframe data from 1m klines.
    
    Args:
        klines_1m: List of 1m klines (should have at least 480 for 8h, 1d uses approximation)
    
    Returns:
        Dictionary with data for each timeframe
    """
    timeframes = {
        '1m': 1,
        '2m': 2,
        '3m': 3,
        '5m': 5,
        '15m': 15,
        '30m': 30,
        '1h': 60,
        '8h': 480,
        '1d': 1440
    }
    
    result = {}
    for tf_name, minutes in timeframes.items():
        aggregated = aggregate_klines_to_timeframe(klines_1m, minutes)
        if aggregated:
            result[tf_name] = aggregated
        else:
            # Fallback to zero values if not enough data
            result[tf_name] = {
                'open': Decimal("0"),
                'close': Decimal("0"),
                'high': Decimal("0"),
                'low': Decimal("0"),
                'volume': Decimal("0"),
                'quote_volume': Decimal("0"),
                'trades': 0,
                'change_pct': Decimal("0")
            }
    
    return result


def ingest_snapshot() -> int:
    """Ingest one snapshot of all spot symbols. Returns count of symbols processed."""
    from screener.models import ScreenerSnapshot, Symbol
    
    tickers = fetch_tickers()
    
    # If tickers fetch failed (empty list), skip this update cycle
    if not tickers:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ No tickers available, skipping this update cycle")
        return 0
    
    now = datetime.now(timezone.utc)
    processed = 0
    snapshots_to_create = []  # Collect snapshots for bulk insert

    # Get symbol codes
    symbol_codes = [t["symbol"] for t in tickers if Decimal(t.get("lastPrice", "0")) > 0]
    
    # Fetch klines for all symbols with SMART BATCHING to avoid rate limits
    # УМНЫЙ БАТЧИНГ: распределяем запросы равномерно по времени
    # Rate limit: 1200 weight/min = 20 weight/sec
    # 178 символов = 178 weight, нужно распределить на ~9 секунд
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching klines for {len(symbol_codes)} spot symbols with smart batching...")
    session = get_session()
    klines_data = {}
    
    cpu_count = os.cpu_count() or 8
    klines_limit = 480  # 8 hours of 1m candles
    
    # УМНЫЙ БАТЧИНГ: распределяем запросы равномерно
    rate_limit_per_second = 20.0  # weight/sec
    max_workers = min(50, cpu_count * 6)  # Умеренный параллелизм (50 потоков)
    
    # Разбиваем на батчи по 20 символов для равномерного распределения
    batch_size = 20
    batches = [symbol_codes[i:i + batch_size] for i in range(0, len(symbol_codes), batch_size)]
    
    start_time = time.time()
    total_requests = 0
    
    for batch_idx, batch in enumerate(batches):
        batch_start = time.time()
        
        # Отправляем запросы для батча параллельно
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {
                executor.submit(fetch_klines, symbol, "1m", klines_limit, session): symbol
                for symbol in batch
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    klines = future.result()
                    if klines:
                        klines_data[symbol] = klines
                    total_requests += 1
                except Exception as e:
                    if symbol not in klines_data:
                        klines_data[symbol] = []
                    total_requests += 1
        
        # Задержка между батчами для соблюдения rate limit
        if batch_idx < len(batches) - 1:
            required_time = batch_size / rate_limit_per_second
            elapsed = time.time() - batch_start
            sleep_time = max(0, required_time - elapsed)
            
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    elapsed_total = time.time() - start_time
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetched klines for {len(klines_data)} symbols in {elapsed_total:.2f}s ({total_requests} requests)")
    
    # NO DELAY - all symbols processed in one batch, rate limit handled by retry logic
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetched klines for {len(klines_data)} spot symbols")
    
    # Bulk get or create all symbols at once
    existing_symbols = {
        s.symbol: s for s in Symbol.objects.filter(
            symbol__in=symbol_codes,
            market_type="spot"
        )
    }
    
    # Create missing symbols
    symbols_to_create = [
        Symbol(symbol=code, market_type="spot", name=code)
        for code in symbol_codes if code not in existing_symbols
    ]
    if symbols_to_create:
        Symbol.objects.bulk_create(symbols_to_create, ignore_conflicts=True)
        # Refresh existing_symbols dict
        for s in Symbol.objects.filter(symbol__in=symbol_codes, market_type="spot"):
            existing_symbols[s.symbol] = s

    for t in tickers:
        try:
            symbol_code = t["symbol"]

            last_price = Decimal(t.get("lastPrice", "0"))
            
            # Skip coins with zero or invalid price
            if last_price <= 0:
                continue
            
            # Convert to Decimal for precise calculations (no rounding errors)
            price_change_percent_24h = Decimal(str(t.get("priceChangePercent", 0.0)))
            # Use quoteVolume (volume in USDT) for spot
            volume_24h = Decimal(str(t.get("quoteVolume", t.get("volume", 0.0))))

            # Get klines data for this symbol (real data instead of approximation)
            klines_1m = klines_data.get(symbol_code, [])
            
            # Calculate real data from klines if available, otherwise fallback to approximation
            # We request 480 candles (8 hours), which covers all timeframes up to 8h
            # For 1d timeframe, we use approximation from 24h ticker data
            if klines_1m and len(klines_1m) >= 60:  # At least 60 candles (1 hour) for 1h timeframe
                # Use real klines data for all timeframes
                tf_data = calculate_timeframe_data_from_klines(klines_1m)
                
                # Extract change, volume, and calculate vdelta from real data
                change_1m = tf_data['1m']['change_pct']
                change_2m = tf_data['2m']['change_pct']
                change_3m = tf_data['3m']['change_pct']
                change_5m = tf_data['5m']['change_pct']
                change_15m = tf_data['15m']['change_pct']
                change_30m = tf_data['30m']['change_pct']
                change_1h = tf_data['1h']['change_pct']
                change_8h = tf_data['8h']['change_pct'] if len(klines_1m) >= 480 else price_change_percent_24h / Decimal("3")
                # For 1d, use approximation from 24h ticker data (we only have 8h of klines)
                change_1d = price_change_percent_24h
                
                volume_1m = tf_data['1m']['quote_volume']
                volume_2m = tf_data['2m']['quote_volume']
                volume_3m = tf_data['3m']['quote_volume']
                volume_5m = tf_data['5m']['quote_volume']
                volume_15m = tf_data['15m']['quote_volume']
                volume_30m = tf_data['30m']['quote_volume']
                volume_1h = tf_data['1h']['quote_volume']
                volume_8h = tf_data['8h']['quote_volume'] if len(klines_1m) >= 480 else volume_24h / Decimal("3")
                # For 1d, use approximation from 24h ticker data
                volume_1d = volume_24h
                
                # Calculate ticks from real trades data
                ticks_1m = tf_data['1m']['trades']
                ticks_2m = tf_data['2m']['trades']
                ticks_3m = tf_data['3m']['trades']
                ticks_5m = tf_data['5m']['trades']
                ticks_15m = tf_data['15m']['trades']
                ticks_30m = tf_data['30m']['trades']
                ticks_1h = tf_data['1h']['trades']
                
                # Calculate volatility from high-low range (more accurate than just change)
                volatility_1m = abs(float((tf_data['1m']['high'] - tf_data['1m']['low']) / tf_data['1m']['open'] * Decimal("100"))) if tf_data['1m']['open'] > 0 else abs(float(change_1m))
                volatility_2m = abs(float((tf_data['2m']['high'] - tf_data['2m']['low']) / tf_data['2m']['open'] * Decimal("100"))) if tf_data['2m']['open'] > 0 else abs(float(change_2m))
                volatility_3m = abs(float((tf_data['3m']['high'] - tf_data['3m']['low']) / tf_data['3m']['open'] * Decimal("100"))) if tf_data['3m']['open'] > 0 else abs(float(change_3m))
                volatility_5m = abs(float((tf_data['5m']['high'] - tf_data['5m']['low']) / tf_data['5m']['open'] * Decimal("100"))) if tf_data['5m']['open'] > 0 else abs(float(change_5m))
                volatility_15m = abs(float((tf_data['15m']['high'] - tf_data['15m']['low']) / tf_data['15m']['open'] * Decimal("100"))) if tf_data['15m']['open'] > 0 else abs(float(change_15m))
                volatility_30m = abs(float((tf_data['30m']['high'] - tf_data['30m']['low']) / tf_data['30m']['open'] * Decimal("100"))) if tf_data['30m']['open'] > 0 else abs(float(change_30m))
                volatility_1h = abs(float((tf_data['1h']['high'] - tf_data['1h']['low']) / tf_data['1h']['open'] * Decimal("100"))) if tf_data['1h']['open'] > 0 else abs(float(change_1h))
            else:
                # Fallback to approximation if klines not available
                # Timeframe ratios: 1m=1/1440, 2m=1/720, 3m=1/480, 5m=1/288, 15m=1/96, 30m=1/48, 1h=1/24, 8h=1/3, 1d=1
                change_1m = price_change_percent_24h / Decimal("1440")
                change_2m = price_change_percent_24h / Decimal("720")
                change_3m = price_change_percent_24h / Decimal("480")
                change_5m = price_change_percent_24h / Decimal("288")
                change_15m = price_change_percent_24h / Decimal("96")
                change_30m = price_change_percent_24h / Decimal("48")
                change_1h = price_change_percent_24h / Decimal("24")
                change_8h = price_change_percent_24h / Decimal("3")
                change_1d = price_change_percent_24h

                volume_1m = volume_24h / Decimal("1440")
                volume_2m = volume_24h / Decimal("720")
                volume_3m = volume_24h / Decimal("480")
                volume_5m = volume_24h / Decimal("288")
                volume_15m = volume_24h / Decimal("96")
                volume_30m = volume_24h / Decimal("48")
                volume_1h = volume_24h / Decimal("24")
                volume_8h = volume_24h / Decimal("3")
                volume_1d = volume_24h

                # Approximate volatility as absolute change
                volatility_1m = abs(float(change_1m))
                volatility_2m = abs(float(change_2m))
                volatility_3m = abs(float(change_3m))
                volatility_5m = abs(float(change_5m))
                volatility_15m = abs(float(change_15m))
                volatility_30m = abs(float(change_30m))
                volatility_1h = abs(float(change_1h))

                # Approximate ticks based on volume
                ticks_1m = int(float(volume_1m) / 1000.0)
                ticks_2m = int(float(volume_2m) / 1000.0)
                ticks_3m = int(float(volume_3m) / 1000.0)
                ticks_5m = int(float(volume_5m) / 1000.0)
                ticks_15m = int(float(volume_15m) / 1000.0)
                ticks_30m = int(float(volume_30m) / 1000.0)
                ticks_1h = int(float(volume_1h) / 1000.0)

            # Vdelta: volume-weighted price change for each timeframe
            # Formula: vdelta_tf = (volume_tf * change_tf) / 100.0
            # Using Decimal for precise calculations without rounding errors
            # Now using REAL data from klines instead of approximation!
            vdelta_1m = (volume_1m * change_1m) / Decimal("100")
            vdelta_2m = (volume_2m * change_2m) / Decimal("100")
            vdelta_3m = (volume_3m * change_3m) / Decimal("100")
            vdelta_5m = (volume_5m * change_5m) / Decimal("100")
            vdelta_15m = (volume_15m * change_15m) / Decimal("100")
            vdelta_30m = (volume_30m * change_30m) / Decimal("100")
            vdelta_1h = (volume_1h * change_1h) / Decimal("100")
            vdelta_8h = (volume_8h * change_8h) / Decimal("100")
            vdelta_1d = (volume_1d * change_1d) / Decimal("100")

            # Spot doesn't have open interest or funding rate, but we'll get it from futures
            # Get OI from futures for the same symbol (for reference, even though Spot doesn't have OI)
            futures_symbol = Symbol.objects.filter(
                symbol=symbol_code, market_type="futures"
            ).first()
            
            # Initialize OI and funding rate
            oi = 0.0
            funding_rate = 0.0
            oi_change_1m = Decimal("0")
            oi_change_2m = Decimal("0")
            oi_change_3m = Decimal("0")
            oi_change_5m = Decimal("0")
            oi_change_15m = Decimal("0")
            oi_change_30m = Decimal("0")
            oi_change_1h = Decimal("0")
            oi_change_8h = Decimal("0")
            oi_change_1d = Decimal("0")
            
            futures_snapshot = None
            if futures_symbol:
                # Get latest futures snapshot to get OI, funding rate, and OI changes
                futures_snapshot = (
                    ScreenerSnapshot.objects.filter(symbol=futures_symbol)
                    .order_by("-ts")
                    .first()
                )
                if futures_snapshot:
                    oi = float(futures_snapshot.open_interest) if futures_snapshot.open_interest else 0.0
                    funding_rate = float(futures_snapshot.funding_rate) if futures_snapshot.funding_rate else 0.0
                    # Get OI changes directly from futures snapshot (now DecimalField)
                    oi_change_1m = futures_snapshot.oi_change_1m if futures_snapshot.oi_change_1m else Decimal("0")
                    oi_change_2m = futures_snapshot.oi_change_2m if futures_snapshot.oi_change_2m else Decimal("0")
                    oi_change_3m = futures_snapshot.oi_change_3m if futures_snapshot.oi_change_3m else Decimal("0")
                    oi_change_5m = futures_snapshot.oi_change_5m if futures_snapshot.oi_change_5m else Decimal("0")
                    oi_change_15m = futures_snapshot.oi_change_15m if futures_snapshot.oi_change_15m else Decimal("0")
                    oi_change_30m = futures_snapshot.oi_change_30m if futures_snapshot.oi_change_30m else Decimal("0")
                    oi_change_1h = futures_snapshot.oi_change_1h if futures_snapshot.oi_change_1h else Decimal("0")
                    oi_change_8h = futures_snapshot.oi_change_8h if futures_snapshot.oi_change_8h else Decimal("0")
                    oi_change_1d = futures_snapshot.oi_change_1d if futures_snapshot.oi_change_1d else Decimal("0")

            # Get symbol from pre-fetched dict
            symbol_obj = existing_symbols.get(symbol_code)
            if not symbol_obj:
                continue  # Skip if symbol wasn't created (shouldn't happen)

            # Prepare snapshot data for bulk insert
            snapshot_data = {
                "symbol": symbol_obj,
                "ts": now,
                "price": last_price,
                "open_interest": oi,
                "funding_rate": funding_rate,
                "change_1m": change_1m,
                "change_2m": change_2m,
                "change_3m": change_3m,
                "change_5m": change_5m,
                "change_15m": change_15m,
                "change_30m": change_30m,
                "change_1h": change_1h,
                "change_8h": change_8h,
                "change_1d": change_1d,
                "oi_change_1m": oi_change_1m,
                "oi_change_2m": oi_change_2m,
                "oi_change_3m": oi_change_3m,
                "oi_change_5m": oi_change_5m,
                "oi_change_15m": oi_change_15m,
                "oi_change_30m": oi_change_30m,
                "oi_change_1h": oi_change_1h,
                "oi_change_8h": oi_change_8h,
                "oi_change_1d": oi_change_1d,
                "volatility_1m": volatility_1m,
                "volatility_2m": volatility_2m,
                "volatility_3m": volatility_3m,
                "volatility_5m": volatility_5m,
                "volatility_15m": volatility_15m,
                "volatility_30m": volatility_30m,
                "volatility_1h": volatility_1h,
                "ticks_1m": ticks_1m,
                "ticks_2m": ticks_2m,
                "ticks_3m": ticks_3m,
                "ticks_5m": ticks_5m,
                "ticks_15m": ticks_15m,
                "ticks_30m": ticks_30m,
                "ticks_1h": ticks_1h,
                "vdelta_1m": vdelta_1m,
                "vdelta_2m": vdelta_2m,
                "vdelta_3m": vdelta_3m,
                "vdelta_5m": vdelta_5m,
                "vdelta_15m": vdelta_15m,
                "vdelta_30m": vdelta_30m,
                "vdelta_1h": vdelta_1h,
                "vdelta_8h": vdelta_8h,
                "vdelta_1d": vdelta_1d,
                "volume_1m": volume_1m,
                "volume_2m": volume_2m,
                "volume_3m": volume_3m,
                "volume_5m": volume_5m,
                "volume_15m": volume_15m,
                "volume_30m": volume_30m,
                "volume_1h": volume_1h,
                "volume_8h": volume_8h,
                "volume_1d": volume_1d,
            }
            snapshots_to_create.append(ScreenerSnapshot(**snapshot_data))
            processed += 1
        except Exception as e:
            print(f"Error processing {t.get('symbol', 'unknown')}: {e}")
            continue

    # Bulk insert all snapshots at once (much faster than individual creates)
    if snapshots_to_create:
        ScreenerSnapshot.objects.bulk_create(
            snapshots_to_create,
            batch_size=100,
            ignore_conflicts=True
        )
    
    return processed


def main() -> None:
    setup_django()
    
    print("Starting Binance Spot ingest loop (OPTIMIZED FOR 178 SYMBOLS)...")
    print("Using REAL klines data for vdelta calculation!")
    print("Ticker + Klines: every 12s (optimized)")
    print("Press Ctrl+C to stop.")
    
    try:
        # Optimized with SMART BATCHING - теперь можно обновлять чаще!
        # УМНЫЙ БАТЧИНГ распределяет запросы равномерно, не превышая лимиты
        # Klines: 178 символов распределены на ~9 секунд (батчи по 20)
        # Ticker: 40 weight (быстро)
        # Можно обновлять каждые 3-4 секунды
        UPDATE_INTERVAL = 3.0  # УСКОРЕНИЕ - обновление каждые 3 секунды (умный батчинг позволяет!)
        
        while True:
            start_time = time.time()
            count = ingest_snapshot()
            elapsed = time.time() - start_time
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ingested {count} spot symbols in {elapsed:.2f}s")
            
            # Sleep to maintain 4 second interval between updates
            # If processing takes longer than 4s, start immediately (no delay)
            sleep_time = max(0, UPDATE_INTERVAL - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
    except KeyboardInterrupt:
        print("\nStopped by user.")


if __name__ == "__main__":
    main()

