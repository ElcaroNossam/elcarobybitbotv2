"""
Binance WebSocket Workers для получения рыночных данных.

Воркеры подписываются на Binance WebSocket streams, хранят состояние в памяти
и каждые 0.3 секунды собирают snapshot для отправки через Django Channels group.
"""
import asyncio
import copy
import json
import logging
import websockets
import aiohttp
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional
from channels.layers import get_channel_layer
from decimal import Decimal

logger = logging.getLogger(__name__)

# НОВАЯ АРХИТЕКТУРА: единая модель агрегации
from .aggregation_model import (
    aggregate_trade_to_1m_bar,
    aggregate_1m_bars_to_tf,
    get_bars_stats,
    restore_bars_from_redis,
    get_bars_count,
    add_kline_to_bars,
    fill_missing_bars_from_klines,
)

# Server-side formatters for performance optimization  
try:
    from screener.formatters import format_price, format_volume, format_vdelta, format_percentage, format_integer
    _formatters_available = True
except ImportError:
    _formatters_available = False
    logger.warning("Formatters module not available - server-side formatting disabled")

# Django ORM helpers (used to persist aggregated snapshots)
try:
    from asgiref.sync import sync_to_async
    from screener.models import Symbol, ScreenerSnapshot
except Exception:
    # Running outside Django runtime (tests/static analysis) — imports may fail
    sync_to_async = None
    Symbol = None
    ScreenerSnapshot = None


# Глобальное хранилище данных для spot и futures
_spot_data: Dict[str, Dict] = {}
_futures_data: Dict[str, Dict] = {}

# Интервалы для kline
KLINE_INTERVALS = ['1m', '3m', '5m', '15m', '30m', '1h', '4h', '8h', '1d']

# Default maximum streams per WebSocket connection. Binance combined stream URLs and policy
# may cause 1008 (policy violation) if too many streams per connection or URL is too long.
# Reduce this value if you see 1008 events.
DEFAULT_MAX_STREAMS_PER_CONN = 120

# Количество минут для каждого таймфрейма (для расчёта из 1m баров)
TF_TO_MINUTES = {
    '1m': 1,
    '3m': 3,
    '5m': 5,
    '15m': 15,
    '30m': 30,
    '1h': 60,
    '4h': 240,
    '8h': 480,
    '1d': 1440,
}

# Максимальное количество 1m баров на символ (24 часа + запас)
MAX_BARS_PER_SYMBOL = 1500


# Глобальный connection pool для HTTP запросов (оптимизация)
_http_session = None
_session_lock = asyncio.Lock()

# Metrics / diagnostics for WebSocket stability
_ws_disconnects = 0
_ws_1008_count = 0
_fallback_klines_count = 0

# Синхронизация snapshot отправки (простой throttle без lock, так как async single-threaded)
_last_snapshot_time = {'spot': 0.0, 'futures': 0.0}
# ОПТИМИЗАЦИЯ: Зменшено до 0.2с (5 раз на секунду) для real-time vDelta
_min_snapshot_interval = 0.2

# Throttle DB writes: don't save snapshots to DB more often than this (seconds)
# Установлен 1 секунда - сервер может больше (16GB RAM, 8 cores)
_min_db_write_interval = 1.0
_last_db_write_time = {'spot': 0.0, 'futures': 0.0}


def _format_snapshot_for_client(snapshot_data: dict, market_type: str = 'spot') -> dict:
    """
    Format snapshot data on server side for immediate display in browser.
    This dramatically improves browser performance by moving formatting logic to the server.
    
    Returns dict with:
    - Original raw values (for sorting/filtering)
    - Formatted display values (ready to render)
    """
    if not _formatters_available:
        # If formatters not available, return original data
        return snapshot_data
    
    formatted = snapshot_data.copy()
    
    # Format price
    if 'price' in formatted:
        formatted['price_formatted'] = format_price(formatted['price'])
    
    # Format all timeframes
    timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
    
    for tf in timeframes:
        # Volume
        vol_key = f'volume_{tf}'
        if vol_key in formatted:
            formatted[f'{vol_key}_formatted'] = format_volume(formatted[vol_key], market_type)
        
        # Vdelta
        vd_key = f'vdelta_{tf}'
        if vd_key in formatted:
            formatted[f'{vd_key}_formatted'] = format_vdelta(formatted[vd_key], market_type)
        
        # Change (percentage)
        chg_key = f'change_{tf}'
        if chg_key in formatted:
            formatted[f'{chg_key}_formatted'] = format_percentage(formatted[chg_key])
        
        # OI Change (percentage) - all TFs
        oi_key = f'oi_change_{tf}'
        if oi_key in formatted:
            formatted[f'{oi_key}_formatted'] = format_percentage(formatted[oi_key])
    
    # Volatility - only relevant TFs
    for tf in ['1m', '3m', '5m', '15m', '30m', '1h']:
        vol_key = f'volatility_{tf}'
        if vol_key in formatted:
            formatted[f'{vol_key}_formatted'] = format_percentage(formatted[vol_key])
    
    # Ticks - only relevant TFs
    for tf in ['1m', '5m', '15m']:
        ticks_key = f'ticks_{tf}'
        if ticks_key in formatted:
            formatted[f'{ticks_key}_formatted'] = format_integer(formatted[ticks_key])
    
    # Funding rate and Open Interest (futures only)
    if market_type == 'futures':
        if 'funding_rate' in formatted:
            formatted['funding_rate_formatted'] = format_percentage(formatted['funding_rate'])
        if 'open_interest' in formatted:
            formatted['open_interest_formatted'] = format_volume(formatted['open_interest'], market_type)
    
    return formatted


def _project_row_for_client(row_data: dict, market_type: str = 'spot') -> dict:
    """Project snapshot row to raw fields only (no *_formatted) to keep payload small.
    Keeps all TF metrics (change/volume/vdelta/oi_change/volatility) plus base price/OI/funding.
    market_type is accepted for call-site symmetry but not used for filtering.
    """
    if not row_data:
        return row_data

    allowed_prefixes = (
        'change_', 'volume_', 'vdelta_', 'oi_change_', 'volatility_', 'ticks_'
    )

    allowed_keys = {
        'symbol', 'market_type', 'price', 'open_interest', 'funding_rate',
        'mark_price', 'timestamp', 'ts'
    }

    projected = {}
    for k, v in row_data.items():
        if k.endswith('_formatted'):
            continue
        if k in allowed_keys or any(k.startswith(p) for p in allowed_prefixes):
            projected[k] = v
    return projected


async def _persist_snapshot_to_db(snapshot: list, market_type: str = 'spot'):
    """Persist aggregated snapshot rows to DB using Django ORM in a thread.

    This function is scheduled as an asyncio task and delegates heavy DB work
    to a synchronous helper wrapped with `sync_to_async` to avoid blocking
    the event loop.
    """
    if sync_to_async is None or ScreenerSnapshot is None or Symbol is None:
        logger.debug("DB persistence skipped: Django ORM not available in this runtime")
        return

    def _sync_persist(rows, mtype):
        from django.utils.dateparse import parse_datetime
        objs = []
        now = datetime.now(timezone.utc)
        
        for r in rows:
            sym = r.get('symbol')
            if not sym:
                continue
            # ensure Symbol exists - use both symbol AND market_type to get correct symbol
            try:
                symbol_obj, _ = Symbol.objects.get_or_create(symbol=sym, market_type=mtype)
            except Exception:
                # Fallback: try to find by symbol and market_type
                try:
                    symbol_obj = Symbol.objects.filter(symbol=sym, market_type=mtype).first()
                    if not symbol_obj:
                        symbol_obj = Symbol.objects.create(symbol=sym, market_type=mtype)
                except Exception:
                    continue

            # parse timestamp
            ts_val = r.get('timestamp')
            if isinstance(ts_val, str):
                try:
                    ts_dt = parse_datetime(ts_val)
                    if ts_dt is None:
                        ts_dt = now
                except Exception:
                    ts_dt = now
            else:
                ts_dt = now

            # Helper to to_decimal
            def d(x):
                try:
                    return Decimal(str(x))
                except Exception:
                    return Decimal('0')

            snapshot_obj = ScreenerSnapshot(
                symbol=symbol_obj,
                ts=ts_dt,
                price=d(r.get('price', 0)),
                open_interest=float(r.get('open_interest', 0)) if r.get('open_interest') is not None else 0.0,
                funding_rate=float(r.get('funding_rate', 0)) if r.get('funding_rate') is not None else 0.0,
                change_1m=d(r.get('change_1m', 0)),
                change_2m=d(r.get('change_2m', 0)),
                change_3m=d(r.get('change_3m', 0)),
                change_5m=d(r.get('change_5m', 0)),
                change_15m=d(r.get('change_15m', 0)),
                change_30m=d(r.get('change_30m', 0)),
                change_1h=d(r.get('change_1h', 0)),
                change_8h=d(r.get('change_8h', 0)),
                change_1d=d(r.get('change_1d', 0)),
                oi_change_1m=d(r.get('oi_change_1m', 0)),
                oi_change_2m=d(r.get('oi_change_2m', 0)),
                oi_change_3m=d(r.get('oi_change_3m', 0)),
                oi_change_5m=d(r.get('oi_change_5m', 0)),
                oi_change_15m=d(r.get('oi_change_15m', 0)),
                oi_change_30m=d(r.get('oi_change_30m', 0)),
                oi_change_1h=d(r.get('oi_change_1h', 0)),
                oi_change_8h=d(r.get('oi_change_8h', 0)),
                oi_change_1d=d(r.get('oi_change_1d', 0)),
                volatility_1m=float(r.get('volatility_1m', 0)),
                volatility_2m=float(r.get('volatility_2m', 0)),
                volatility_3m=float(r.get('volatility_3m', 0)),
                volatility_5m=float(r.get('volatility_5m', 0)),
                volatility_15m=float(r.get('volatility_15m', 0)),
                volatility_30m=float(r.get('volatility_30m', 0)),
                volatility_1h=float(r.get('volatility_1h', 0)),
                ticks_1m=int(r.get('ticks_1m', 0)),
                ticks_2m=int(r.get('ticks_2m', 0)),
                ticks_3m=int(r.get('ticks_3m', 0)),
                ticks_5m=int(r.get('ticks_5m', 0)),
                ticks_15m=int(r.get('ticks_15m', 0)),
                ticks_30m=int(r.get('ticks_30m', 0)),
                ticks_1h=int(r.get('ticks_1h', 0)),
                vdelta_1m=d(r.get('vdelta_1m', 0)),
                vdelta_2m=d(r.get('vdelta_2m', 0)),
                vdelta_3m=d(r.get('vdelta_3m', 0)),
                vdelta_5m=d(r.get('vdelta_5m', 0)),
                vdelta_15m=d(r.get('vdelta_15m', 0)),
                vdelta_30m=d(r.get('vdelta_30m', 0)),
                vdelta_1h=d(r.get('vdelta_1h', 0)),
                vdelta_8h=d(r.get('vdelta_8h', 0)),
                vdelta_1d=d(r.get('vdelta_1d', 0)),
                volume_1m=d(r.get('volume_1m', 0)),
                volume_2m=d(r.get('volume_2m', 0)),
                volume_3m=d(r.get('volume_3m', 0)),
                volume_5m=d(r.get('volume_5m', 0)),
                volume_15m=d(r.get('volume_15m', 0)),
                volume_30m=d(r.get('volume_30m', 0)),
                volume_1h=d(r.get('volume_1h', 0)),
                volume_8h=d(r.get('volume_8h', 0)),
                volume_1d=d(r.get('volume_1d', 0)),
            )
            
            objs.append(snapshot_obj)

        # Bulk create in batches (увеличен batch size для оптимизации)
        # PostgreSQL эффективно обрабатывает батчи до 1000 записей
        batch = 500
        created_count = 0
        
        for i in range(0, len(objs), batch):
            batch_objs = objs[i:i+batch]
            try:
                # NOTE: Removed ignore_conflicts - there shouldn't be conflicts anyway
                # since each snapshot has unique (symbol, ts)
                result = ScreenerSnapshot.objects.bulk_create(batch_objs)
                created_count += len(result)
            except Exception as e:
                logger.error(f"_sync_persist bulk_create ERROR: {e}")

    try:
        await sync_to_async(_sync_persist, thread_sensitive=True)(snapshot, market_type)
        logger.debug(f"Persisted {len(snapshot)} snapshot rows to DB for {market_type}")
    except Exception as e:
        logger.exception(f"Error persisting snapshot to DB: {e}")


def _prune_window(window_data, cutoff_ms):
    """Return pruned window entries keeping those with ts >= cutoff_ms.

    Accepts window entries in two formats:
      - (ts, vdelta)
      - (ts, vdelta, volume)

    Normalizes output to tuples of (ts, vdelta, volume_or_none).
    Uses inclusive boundary (>=) so items with ts == cutoff_ms are kept.
    """
    pruned = []
    if not window_data:
        return pruned

    for entry in window_data:
        try:
            if len(entry) == 3:
                ts, vd, vol = entry
            elif len(entry) == 2:
                ts, vd = entry
                vol = abs(vd) if vd is not None else None
            else:
                # Unexpected shape: try to unpack first two values
                ts = entry[0]
                vd = entry[1] if len(entry) > 1 else 0
                vol = entry[2] if len(entry) > 2 else (abs(vd) if vd is not None else None)
        except Exception:
            # Skip malformed entries
            continue

        try:
            if ts is None:
                continue
            # ensure numeric comparison
            ts_val = int(ts)
        except Exception:
            continue

        if ts_val >= cutoff_ms:
            pruned.append((ts_val, vd, vol))

    return pruned


# Кеш для символов (чтобы не запрашивать БД каждый раз)
_symbols_cache: Dict[str, List[str]] = {}
_symbols_cache_time: Dict[str, float] = {}
_SYMBOLS_CACHE_TTL = 300  # 5 минут

def load_symbols_from_file() -> List[str]:
    """Загружает символы из файла symbols.txt"""
    import os
    symbols_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'symbols.txt')
    try:
        with open(symbols_file, 'r') as f:
            symbols = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        logger.info(f"Loaded {len(symbols)} symbols from {symbols_file}")
        return symbols
    except Exception as e:
        logger.error(f"Failed to load symbols from file: {e}")
        return []

async def get_symbols_from_db(market_type: str) -> List[str]:
    """Получает список символов из файла symbols.txt (одинаковый для spot и futures)."""
    import time
    
    # Проверяем кеш
    current_time = time.time()
    if market_type in _symbols_cache:
        cache_time = _symbols_cache_time.get(market_type, 0)
        if current_time - cache_time < _SYMBOLS_CACHE_TTL:
            logger.debug(f"Using cached symbols for {market_type} ({len(_symbols_cache[market_type])} symbols)")
            return _symbols_cache[market_type]
    
    # Загружаем из файла
    symbol_list = load_symbols_from_file()
    
    if symbol_list:
        # Сохраняем в кеш
        _symbols_cache[market_type] = symbol_list
        _symbols_cache_time[market_type] = current_time
        logger.info(f"Loaded {len(symbol_list)} symbols from file for {market_type} (cached)")
        return symbol_list
    
    # Fallback на базовый список
    fallback = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT', 'DOGEUSDT',
        'AVAXUSDT', 'TRXUSDT', 'LINKUSDT', 'DOTUSDT', 'MATICUSDT', 'SHIBUSDT',
        'LTCUSDT', 'UNIUSDT', 'ATOMUSDT', 'ETCUSDT', 'XLMUSDT', 'BCHUSDT', 'ALGOUSDT',
    ]
    logger.info(f"Using fallback list with {len(fallback)} symbols for {market_type}")
    return fallback


class BinanceSpotWorker:
    """Воркер для Spot рынка."""
    
    def __init__(self):
        self.ws_url = 'wss://stream.binance.com:9443/ws/'
        self.ws = None
        self.running = False
        self.channel_layer = get_channel_layer()
        self.group_name = 'screener_spot'
        self.symbols: List[str] = []  # Будет загружено асинхронно в run()
        self.open_interest_cache: Dict[str, float] = {}
        self._warmup_done = False
    
    async def connect_chunk(self, chunk_idx: int, stream_chunk: List[str], total_chunks: int):
        """Подключается к одному chunk streams."""
        streams_str = '/'.join(stream_chunk)
        combined_url = f'wss://stream.binance.com:9443/stream?streams={streams_str}'
        
        reconnect_delay = 5
        max_reconnect_delay = 60
        # максимальное число попыток до увеличения паузы/логирования
        max_reconnect_attempts = 8

        while self.running:
            try:
                logger.info(f"Spot worker: Connecting to chunk {chunk_idx + 1}/{total_chunks} ({len(stream_chunk)} streams)")
                # Use explicit client-side keepalive. Binance sends server pings but enforcing
                # client-side pings detects stalled connections faster and lets us reconnect.
                async with websockets.connect(
                    combined_url,
                    ping_interval=20,   # send ping every 20s
                    ping_timeout=10,    # wait 10s for pong
                    close_timeout=10,
                    max_size=10 * 1024 * 1024,  # Максимальный размер сообщения 10MB
                ) as ws:
                    logger.info(f"Spot worker: Connected to Binance WebSocket chunk {chunk_idx + 1}")
                    reconnect_delay = 5  # Сбрасываем задержку при успешном подключении

                    message_count = 0

                    async for message in ws:
                        if not self.running:
                            break

                        try:
                            message_count += 1
                            # Логируем только первое сообщение для подтверждения подключения
                            if message_count == 1:
                                logger.info(f"Spot worker chunk {chunk_idx + 1}: First message received, connection confirmed")

                            # Пропускаем пустые сообщения
                            if not message or not message.strip():
                                continue

                            data = json.loads(message)
                            await self.process_message(data)

                            # Логируем каждые 1000 сообщений для мониторинга
                            if message_count % 1000 == 0:
                                logger.debug(f"Spot worker chunk {chunk_idx + 1}: Processed {message_count} messages")
                        except json.JSONDecodeError as e:
                            logger.error(f"Spot worker chunk {chunk_idx + 1}: Failed to parse JSON: {e}")
                        except Exception as e:
                            logger.error(f"Spot worker chunk {chunk_idx + 1}: Error processing message: {e}")
                            
            except websockets.exceptions.ConnectionClosed as e:
                # Глобальная метрика отключений
                global _ws_disconnects, _ws_1008_count
                _ws_disconnects += 1

                # Логируем и помечаем policy violation
                if e.code == 1008:
                    _ws_1008_count += 1
                    logger.warning(f"Spot worker chunk {chunk_idx + 1}: Connection closed with policy violation (1008). Total 1008 events: {_ws_1008_count}")
                    logger.warning("Policy violation (1008) can indicate too many streams per connection or subscription rate limits; consider reducing chunk size.")

                # Логируем только если это не обычное закрытие (код 1000)
                if e.code != 1000:
                    logger.warning(
                        f"Spot worker chunk {chunk_idx + 1}: Connection closed: code={e.code} reason={getattr(e, 'reason', None)}; reconnecting in {reconnect_delay}s... (disconnects={_ws_disconnects})"
                    )
                else:
                    logger.debug(f"Spot worker chunk {chunk_idx + 1}: Connection closed normally: {e}")
            except asyncio.TimeoutError as e:
                logger.warning(f"Spot worker chunk {chunk_idx + 1}: Connection timeout: {e}, reconnecting in {reconnect_delay}s...")
            except Exception as e:
                # Не логируем keepalive timeout как ошибку - это нормальное поведение при переподключении
                error_str = str(e).lower()
                if 'keepalive' in error_str or 'ping timeout' in error_str or 'pong' in error_str:
                    # Обычно возникает при проблемах сети — не считать как критическую ошибку
                    logger.debug(f"Spot worker chunk {chunk_idx + 1}: Keepalive/pong timeout (normal): {e}")
                else:
                    logger.error(f"Spot worker chunk {chunk_idx + 1}: Connection error: {e}", exc_info=True)
            
            if not self.running:
                break
            
            # Переподключение с экспоненциальной задержкой + небольшой джиттер
            jitter = random.uniform(0, max(1.0, reconnect_delay * 0.5))
            sleep_for = min(reconnect_delay + jitter, max_reconnect_delay)
            logger.info(f"Spot worker chunk {chunk_idx + 1}: Reconnecting in {sleep_for:.1f}s (next delay cap {max_reconnect_delay}s)")
            await asyncio.sleep(sleep_for)
            reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)
    
    async def connect(self):
        """Подключается к Binance WebSocket и подписывается на streams."""
        streams = []
        
        # Собираем streams для всех данных
        for symbol in self.symbols:
            symbol_lower = symbol.lower()
            # aggTrade для Vdelta
            streams.append(f'{symbol_lower}@aggTrade')
            # kline только для 1m (остальные TF аггрегируем из 1m для экономии connections)
            streams.append(f'{symbol_lower}@kline_1m')
            # ticker для price, change_24h
            streams.append(f'{symbol_lower}@ticker')
        
        logger.info(f"Spot worker: Total streams to subscribe: {len(streams)} (3 per symbol)")

        
        # Используем combined stream для подписки на все streams
        # Максимум 200 streams на соединение (ограничение длины URL ~2000 символов)
        # Каждый stream ~50-100 символов, так что 200 streams = ~10-20KB в URL
        max_streams = DEFAULT_MAX_STREAMS_PER_CONN
        stream_chunks = [streams[i:i + max_streams] for i in range(0, len(streams), max_streams)]
        
        logger.info(f"Spot worker: Split into {len(stream_chunks)} chunks")
        
        # Создаем отдельные задачи для каждого chunk

        chunk_tasks = []
        for chunk_idx, stream_chunk in enumerate(stream_chunks):
            task = asyncio.create_task(self.connect_chunk(chunk_idx, stream_chunk, len(stream_chunks)))
            chunk_tasks.append(task)
        
        # Ждем завершения всех задач (они будут работать пока self.running = True)
        try:
            await asyncio.gather(*chunk_tasks)
        except Exception as e:
            logger.error(f"Spot worker: Error in chunk tasks: {e}", exc_info=True)
    
    async def process_message(self, data: dict):
        """Обрабатывает сообщение от Binance."""
        if not isinstance(data, dict):
            logger.warning(f"Spot worker: Received non-dict data: {type(data)}")
            return
        
        if 'stream' not in data or 'data' not in data:
            logger.warning(f"Spot worker: Missing 'stream' or 'data' in message: {list(data.keys())}")
            return
        
        stream_name = data['stream']
        stream_data = data['data']
        
        # Обрабатываем глобальные потоки (!bookTicker)
        if stream_name == '!bookTicker':
            # Для !bookTicker данные приходят как массив или одиночный объект
            if isinstance(stream_data, list):
                for item in stream_data:
                    symbol = item.get('s', '').upper()
                    if symbol:
                        await self.process_book_ticker(symbol, item)
            elif isinstance(stream_data, dict) and 's' in stream_data:
                symbol = stream_data.get('s', '').upper()
                if symbol:
                    await self.process_book_ticker(symbol, stream_data)
            return
        
        # Парсим stream name: symbol@type или symbol@type_interval
        parts = stream_name.split('@')
        if len(parts) < 2:
            logger.warning(f"Spot worker: Invalid stream name format: {stream_name}")
            return
        
        symbol = parts[0].upper()
        stream_type = parts[1]
        
        # Обрабатываем разные типы streams
        if stream_type == 'aggTrade':
            await self.process_agg_trade(symbol, stream_data)
        elif stream_type.startswith('kline_'):
            interval = stream_type.split('_', 1)[1]
            await self.process_kline(symbol, interval, stream_data)
        elif stream_type == 'ticker':
            await self.process_ticker(symbol, stream_data)
        elif stream_type.startswith('ticker_'):
            # ticker_1h, ticker_4h, ticker_1d
            interval = stream_type.split('_', 1)[1]
            await self.process_ticker(symbol, stream_data, interval=interval)
        elif stream_type == 'bookTicker':
            await self.process_book_ticker(symbol, stream_data)
        elif stream_type == 'depth10':
            await self.process_depth(symbol, stream_data)
        elif stream_type == 'depth@500ms':
            await self.process_depth(symbol, stream_data)
        else:
            logger.debug(f"Spot worker: Unknown stream type: {stream_type} for {symbol}")
    
    async def process_agg_trade(self, symbol: str, data: dict, skip_logging: bool = False):
        """Обрабатывает aggTrade для Vdelta и ticks.
        
        Использует отдельные rolling windows для каждого таймфрейма.
        НОВАЯ АРХИТЕКТУРА: все данные агрегируются в 1m бары через aggregation_model.
        Rolling windows для сырых трейдов УДАЛЕНЫ для экономии CPU/памяти.
        
        Формула vDelta:
        - vDelta = (price * quantity) в USDT
        - Если is_buyer_maker == False (агрессивный покупатель) → положительный vDelta
        - Если is_buyer_maker == True (агрессивный продавец) → отрицательный vDelta
        
        Args:
            symbol: Символ
            data: Данные aggTrade
            skip_logging: Пропустить логирование (для инициализации из исторических данных)
        """
        global _spot_data
        
        if symbol not in _spot_data:
            _spot_data[symbol] = {}
        
        price = float(data.get('p', 0))
        quantity = float(data.get('q', 0))
        is_buyer_maker = data.get('m', False)  # True = продажа (maker), False = покупка (taker)
        
        # Vdelta: объем покупок - объем продаж (в USDT)
        quote_volume = quantity * price  # Объем в USDT (quote currency)
        is_buy = not is_buyer_maker  # True если агрессивная покупка
        
        # Используем реальное время события от Binance (T - trade time)
        event_time_raw = data.get('T') or data.get('E')
        if not event_time_raw:
            event_time_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        else:
            try:
                evt = float(event_time_raw)
                event_time_ms = int(evt * 1000) if evt < 1e12 else int(evt)
            except Exception:
                event_time_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        
        # ЕДИНСТВЕННОЕ МЕСТО АГРЕГАЦИИ: все данные идут в 1m бары
        # Все TF рассчитываются из этих баров в send_snapshot()
        aggregate_trade_to_1m_bar(
            symbol=symbol,
            ts_ms=event_time_ms,
            quote_volume=quote_volume,
            is_buy=is_buy,
            price=price,
            market_type='spot'
        )
        
        # Диагностика для BTCUSDT (один раз)
        if not skip_logging and symbol == "BTCUSDT" and not hasattr(self, '_time_diag_logged'):
            self._time_diag_logged = True
            event_dt = datetime.fromtimestamp(event_time_ms / 1000, tz=timezone.utc)
            now_dt = datetime.now(timezone.utc)
            logger.info(f"[TIME DIAG] {symbol} event_time_ms={event_time_ms}, event_dt={event_dt.isoformat()}, now_dt={now_dt.isoformat()}, diff_sec={(now_dt - event_dt).total_seconds()}")
        
        # Храним только базовую информацию для совместимости (ticks, last_price)
        if 'aggTrade' not in _spot_data[symbol]:
            _spot_data[symbol]['aggTrade'] = {
                'ticks': 0,
                'last_price': price,
            }
        
        _spot_data[symbol]['aggTrade']['ticks'] += 1
        _spot_data[symbol]['aggTrade']['last_price'] = price
        _spot_data[symbol]['aggTrade']['last_update'] = datetime.fromtimestamp(event_time_ms / 1000, tz=timezone.utc).isoformat()

    
    async def process_kline(self, symbol: str, interval: str, data: dict):
        """Обрабатывает kline для volatility, volume, ticks, change."""
        global _spot_data
        
        if symbol not in _spot_data:
            _spot_data[symbol] = {}
        
        if 'kline' not in _spot_data[symbol]:
            _spot_data[symbol]['kline'] = {}
        
        k = data.get('k', {})
        if not k:
            return
        
        is_closed = k.get('x', False)  # True якщо свічка закрита
        
        kline_entry = {
            'open': float(k.get('o', 0)),
            'high': float(k.get('h', 0)),
            'low': float(k.get('l', 0)),
            'close': float(k.get('c', 0)),
            'volume': float(k.get('v', 0)),
            'quote_volume': float(k.get('q', 0)),
            'trades': int(k.get('n', 0)),
            'is_closed': is_closed,
            'last_update': datetime.now(timezone.utc).isoformat(),
        }
        
        _spot_data[symbol]['kline'][interval] = kline_entry

    async def _fetch_recent_klines_spot(self, symbol: str, interval: str, limit: int = 3):
        """Fetch recent klines for spot market via REST as a fallback when windows are empty."""
        import aiohttp
        global _http_session, _session_lock, _fallback_klines_count

        base = 'https://api.binance.com'
        url = f"{base}/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"

        async with _session_lock:
            if _http_session is None or _http_session.closed:
                connector = aiohttp.TCPConnector(limit=60, limit_per_host=30, ttl_dns_cache=300)
                timeout = aiohttp.ClientTimeout(total=8, connect=4)
                _http_session = aiohttp.ClientSession(connector=connector, timeout=timeout)

        try:
            async with _http_session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    klines = []
                    for k in data:
                        open_price = float(k[1])
                        close_price = float(k[4])
                        quote_vol = float(k[7])
                        klines.append({'open': open_price, 'close': close_price, 'quote_volume': quote_vol})
                    _fallback_klines_count += 1
                    return klines
        except Exception as e:
            logger.debug(f"Spot worker: fetch_recent_klines_spot failed for {symbol} {interval}: {e}")
        return None
    
    async def process_ticker(self, symbol: str, data: dict, interval: str = None):
        """Обрабатывает ticker для price, change, volume.
        
        Args:
            symbol: Символ
            data: Данные ticker
            interval: Интервал для ticker_1h, ticker_4h, ticker_1d (None для обычного ticker)
        """
        global _spot_data
        
        if symbol not in _spot_data:
            _spot_data[symbol] = {}
        
        price = float(data.get('c', 0))
        if price > 0:  # Только если цена валидная
            ticker_key = 'ticker' if not interval else f'ticker_{interval}'
            # Для основного ticker сохраняем change_24h, для остальных - change
            change_key = 'change_24h' if not interval else 'change'
            _spot_data[symbol][ticker_key] = {
                'price': price,  # Last price (c)
                'open': float(data.get('o', 0)),  # Open price (o)
                'high': float(data.get('h', 0)),  # High price (h)
                'low': float(data.get('l', 0)),  # Low price (l)
                change_key: float(data.get('P', 0)),  # Price change percent (P)
                'change': float(data.get('P', 0)),  # Также сохраняем как change для совместимости
                'volume': float(data.get('v', 0)),  # Base asset volume (v)
                'quote_volume': float(data.get('q', 0)),  # Quote asset volume (q)
                'interval': interval,  # Сохраняем интервал для идентификации
                'last_update': datetime.now(timezone.utc).isoformat(),
            }
    
    async def process_book_ticker(self, symbol: str, data: dict):
        """Обрабатывает bookTicker для bid/ask, spread."""
        global _spot_data
        
        if symbol not in _spot_data:
            _spot_data[symbol] = {}
        
        bid_price = float(data.get('b', 0))
        ask_price = float(data.get('a', 0))
        spread = ask_price - bid_price if bid_price > 0 and ask_price > 0 else 0
        
        _spot_data[symbol]['bookTicker'] = {
            'bid_price': bid_price,
            'bid_qty': float(data.get('B', 0)),
            'ask_price': ask_price,
            'ask_qty': float(data.get('A', 0)),
            'spread': spread,
            'last_update': datetime.now(timezone.utc).isoformat(),
        }
    
    async def process_depth(self, symbol: str, data: dict):
        """Обрабатывает depth10 для стакана."""
        global _spot_data
        
        if symbol not in _spot_data:
            _spot_data[symbol] = {}
        
        bids = [[float(b[0]), float(b[1])] for b in data.get('bids', [])]
        asks = [[float(a[0]), float(a[1])] for a in data.get('asks', [])]
        
        _spot_data[symbol]['depth'] = {
            'bids': bids,
            'asks': asks,
            'last_update': datetime.now(timezone.utc).isoformat(),
        }
    
    async def send_snapshot(self):
        """Собирает snapshot и отправляет через Channels group."""
        global _spot_data
        
        # Ждем первого сообщения от Binance перед отправкой снапшотов
        if not self._warmup_done:
            has_ticker = any(data.get('ticker') for data in _spot_data.values())
            has_agg = any(data.get('aggTrade') for data in _spot_data.values())
            if not (has_ticker or has_agg):
                return
            self._warmup_done = True
            logger.info("Spot worker: Warmup done! Starting to send snapshots")
        
        # КРИТИЧНО: Створюємо КОПІЮ _spot_data перед ітерацією
        snapshot_data = dict(_spot_data)
        
        snapshot = []
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        
        for symbol in self.symbols:
            if symbol not in snapshot_data:
                continue
            
            symbol_data = snapshot_data[symbol]
            
            # Собираем данные для snapshot
            ticker = symbol_data.get('ticker', {})
            agg_trade = symbol_data.get('aggTrade', {})
            klines = symbol_data.get('kline', {})
            
            # Пропускаем символы без ticker данных (нет цены)
            if not ticker or ticker.get('price', 0) == 0:
                continue
            
            current_price = ticker.get('price', 0)
            
            # Формируем snapshot для символа
            row_data = {
                'symbol': symbol,
                'price': current_price,
                'change_24h': ticker.get('change_24h', ticker.get('change', 0)),
                'volume_24h': ticker.get('quote_volume', 0),
                'ticks_1m': agg_trade.get('ticks', 0) if agg_trade else 0,
            }
            
            # НОВАЯ АРХИТЕКТУРА: все TF данные из агрегированных 1m баров
            # Для каждого TF вызываем aggregate_1m_bars_to_tf()
            for interval in KLINE_INTERVALS:
                # Получаем агрегированные данные из 1m баров
                tf_data = aggregate_1m_bars_to_tf(symbol, now_ms, interval, market_type='spot')
                
                if tf_data and tf_data.get('bars_count', 0) > 0:
                    # Данные есть - используем их
                    row_data[f'vdelta_{interval}'] = tf_data['vdelta']
                    row_data[f'volume_{interval}'] = tf_data['volume']
                    row_data[f'change_{interval}'] = tf_data['change_pct']
                    row_data[f'ticks_{interval}'] = tf_data['trades']
                    
                    # Volatility из high/low 1m баров
                    # Для этого нужно дополнительно получить high/low
                    # Пока используем 0 (можно доработать в aggregation_model)
                    row_data[f'volatility_{interval}'] = 0.0
                else:
                    # Fallback на kline данные от Binance (если есть)
                    if interval in klines:
                        kline = klines[interval]
                        open_price = kline.get('open', 0)
                        close_price = kline.get('close', 0)
                        high = kline.get('high', 0)
                        low = kline.get('low', 0)
                        
                        if open_price > 0:
                            row_data[f'volatility_{interval}'] = ((high - low) / open_price) * 100
                            row_data[f'change_{interval}'] = ((close_price - open_price) / open_price) * 100
                        else:
                            row_data[f'volatility_{interval}'] = 0.0
                            row_data[f'change_{interval}'] = 0.0
                        
                        row_data[f'volume_{interval}'] = kline.get('quote_volume', 0)
                        row_data[f'ticks_{interval}'] = kline.get('trades', 0)
                        row_data[f'vdelta_{interval}'] = 0  # kline не имеет vdelta
                    else:
                        # Нет данных - нули
                        row_data[f'volatility_{interval}'] = 0.0
                        row_data[f'change_{interval}'] = 0.0
                        row_data[f'volume_{interval}'] = 0.0
                        row_data[f'ticks_{interval}'] = 0
                        row_data[f'vdelta_{interval}'] = 0
            
            # Spot рынки: используем 24h volume как метрику ликвидности
            spot_volume = ticker.get('quote_volume', 0)
            row_data['open_interest'] = spot_volume
            row_data['funding_rate'] = 0.0  # Spot не имеет funding rate
            
            # Volume change для всех таймфреймов
            prev_volume = symbol_data.get('volume_previous', spot_volume)
            if prev_volume > 0:
                volume_change = ((spot_volume - prev_volume) / prev_volume) * 100
            else:
                volume_change = 0.0
            
            symbol_data['volume_previous'] = spot_volume
            
            for interval in KLINE_INTERVALS:
                row_data[f'oi_change_{interval}'] = volume_change
            
            # Timestamp
            if agg_trade and 'last_update' in agg_trade:
                row_data['timestamp'] = agg_trade['last_update']
            else:
                row_data['timestamp'] = datetime.now(timezone.utc).isoformat()
            row_data['ts'] = row_data['timestamp']
            
            # Send only raw fields; formatting happens client-side to keep payload small
            projected = _project_row_for_client(row_data)
            
            snapshot.append(projected)

        # Persist aggregated snapshot to DB at a throttled interval
        # NOTE: Temporarily disabled for performance - DB writes are too slow
        # try:
        #     if sync_to_async and ScreenerSnapshot is not None and Symbol is not None:
        #         now = asyncio.get_event_loop().time()
        #         last = _last_db_write_time.get('spot', 0.0)
        #         if now - last >= _min_db_write_interval:
        #             snapshot_copy = copy.deepcopy(snapshot)
        #             asyncio.create_task(_persist_snapshot_to_db(snapshot_copy, market_type='spot'))
        #             _last_db_write_time['spot'] = now
        # except Exception:
        #     logger.exception("Failed to schedule DB persistence for spot snapshot")


        # Отправляем через Channels group (только если есть данные)
        if not snapshot:
            symbols_with_data = [s for s in self.symbols if s in snapshot_data]
            symbols_with_ticker = [s for s in symbols_with_data if snapshot_data[s].get('ticker')]
            logger.warning(f"Spot worker: Empty snapshot, skipping send. Total symbols: {len(self.symbols)}, in snapshot_data: {len(symbols_with_data)}, with ticker: {len(symbols_with_ticker)}")
            print(f"[PRINT DEBUG SPOT] send_snapshot(): ⚠️ EMPTY snapshot. _spot_data keys: {len(_spot_data)}, symbols: {len(self.symbols)}", flush=True)
            return  # Не отправляем пустые snapshot
        
        # Throttle отправки
        import time
        global _last_snapshot_time, _min_snapshot_interval
        
        current_time = time.time()
        time_since_last = current_time - _last_snapshot_time.get('spot', 0)
        if time_since_last < _min_snapshot_interval:
            return
        
        _last_snapshot_time['spot'] = current_time
        
        if self.channel_layer:
            try:
                # Limit snapshot size
                MAX_SNAPSHOT_SIZE = 200
                if len(snapshot) > MAX_SNAPSHOT_SIZE:
                    snapshot = snapshot[:MAX_SNAPSHOT_SIZE]
                
                await asyncio.wait_for(
                    self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'screener_data',
                            'data': snapshot,
                            'market_type': 'spot',
                            'timestamp': datetime.now(timezone.utc).isoformat(),
                        }
                    ),
                    timeout=5.0  # Збільшено до 5с для стабільності при високому навантаженні
                )
                # Log successful send (every 50th)
                if not hasattr(self, '_send_count'):
                    self._send_count = 0
                self._send_count += 1
                if self._send_count % 50 == 0:
                    logger.info(f"Spot worker: ✅ Sent snapshot #{self._send_count} with {len(snapshot)} symbols to {self.group_name}")
            except asyncio.TimeoutError:
                logger.warning(f"Spot worker: Timeout sending snapshot to {self.group_name}")
            except Exception as e:
                error_msg = str(e).lower()
                if 'over capacity' not in error_msg and 'full' not in error_msg:
                    logger.error(f"Spot worker: Error sending snapshot: {e}")
                    try:
                        self.channel_layer = get_channel_layer()
                    except Exception as reconnect_error:
                        logger.error(f"Spot worker: Failed to reconnect channel layer: {reconnect_error}")
        else:
            logger.warning(f"Spot worker: Channel layer is None, cannot send snapshot to {self.group_name}")
        # NOTE: DB persistence is handled above (throttled); do not block on DB here.
    
    def _calculate_volatility(self, kline: dict) -> float:
        """Вычисляет волатильность из kline данных.
        
        Volatility = (high - low) / open * 100 (процент)
        Это стандартная формула волатильности для криптовалютных рынков.
        """
        high = kline.get('high', 0)
        low = kline.get('low', 0)
        open_price = kline.get('open', 0)
        
        if open_price == 0:
            return 0.0
        
        # Волатильность: (high - low) / open * 100 (процент)
        return ((high - low) / open_price) * 100
    
    async def fetch_open_interest_bulk_from_db(self, symbols: List[str]):
        """Получает Open Interest из БД для всех символов одним запросом (оптимизация)."""
        from django.db import connection
        from django.utils import timezone
        from datetime import timedelta
        from asgiref.sync import sync_to_async
        
        if not symbols:
            return {}
        
        try:
            # Получаем последний snapshot из БД за последние 4 часа для всех символов сразу
            # Используем более длительный период для кеширования (4 часа вместо 2)
            recent_cutoff = timezone.now() - timedelta(hours=4)
            
            # Обертываем синхронный код в sync_to_async
            @sync_to_async
            def _fetch_oi():
                with connection.cursor() as cursor:
                    # Оптимизированный запрос с DISTINCT ON (быстрее для PostgreSQL)
                    # DISTINCT ON в сочетании с индексом (symbol_id, ts DESC) работает O(n)
                    cursor.execute("""
                        SELECT DISTINCT ON (sym.id)
                            sym.symbol,
                            s.open_interest
                        FROM screener_screenersnapshot s
                        INNER JOIN screener_symbol sym ON s.symbol_id = sym.id
                        WHERE sym.symbol = ANY(%s)
                          AND sym.market_type = 'futures'
                          AND s.ts >= %s
                        ORDER BY sym.id, s.ts DESC
                    """, [symbols, recent_cutoff])
                    
                    oi_data = {}
                    for row in cursor.fetchall():
                        symbol, oi = row
                        oi_data[symbol] = float(oi or 0)
                    return oi_data
            
            oi_data = await _fetch_oi()
            
            # Обновляем кеш и предыдущие значения
            global _spot_data
            for symbol in symbols:
                new_oi = oi_data.get(symbol, 0.0)
                
                if symbol not in _spot_data:
                    _spot_data[symbol] = {}
                
                old_oi = self.open_interest_cache.get(symbol, new_oi)
                _spot_data[symbol]['oi_previous'] = old_oi
                self.open_interest_cache[symbol] = new_oi
            
            return oi_data
        except Exception as e:
            logger.error(f"Spot worker: Error fetching OI bulk from DB: {e}", exc_info=True)
            return {}
    
    async def oi_update_loop(self):
        """Цикл обновления 24h volume из ticker (для spot рынков)."""
        while self.running:
            try:
                # Для spot обновляем 24h volume из ticker (уже обновляется в process_ticker)
                # Дополнительно загружаем OI из БД для информации (если есть futures данные)
                if self.symbols:
                    await self.fetch_open_interest_bulk_from_db(self.symbols)
                    logger.debug(f"Spot worker: Updated volume/OI cache for {len(self.symbols)} symbols")
                
                # Интервал 10 секунд (меньшая частота для spot, т.к. volume уже в ticker)
                await asyncio.sleep(10.0)
            except Exception as e:
                logger.error(f"Spot worker: Error in volume update loop: {e}", exc_info=True)
                await asyncio.sleep(10.0)
    
    async def run(self):
        """Запускает воркер."""
        self.running = True
        
        # Загружаем символы из БД асинхронно
        if not self.symbols:
            self.symbols = await get_symbols_from_db('spot')
            logger.info(f"Spot worker: Loaded {len(self.symbols)} symbols")
        
        # Восстанавливаем 1m бары из Redis для персистентности между перезапусками
        bars_restored = restore_bars_from_redis(market_type='spot')
        logger.info(f"Spot worker: Restored {bars_restored} 1m bars from Redis")
        
        # Если данных недостаточно, догружаем через Klines API
        if self.symbols and bars_restored < len(self.symbols) * 1440:  # Минимум 24 часа на символ
            logger.info(f"Spot worker: Not enough bars in Redis, fetching from Klines API...")
            filled = await fill_missing_bars_from_klines(self.symbols, market_type='spot')
            logger.info(f"Spot worker: Filled {filled} bars from Klines API")
        
        if not self.symbols:
            logger.error("Spot worker: No symbols loaded, cannot start")
            return
        
        # Запускаем задачи
        snapshot_task = asyncio.create_task(self.snapshot_loop())
        oi_update_task = asyncio.create_task(self.oi_update_loop())
        metrics_task = asyncio.create_task(self.metrics_loop())
        
        # Запускаем подключение к WebSocket
        await self.connect()
        
        snapshot_task.cancel()
        oi_update_task.cancel()
        metrics_task.cancel()

    async def metrics_loop(self):
        """Периодически логирует глобальные счетчики WS для диагностики."""
        global _ws_disconnects, _ws_1008_count, _fallback_klines_count
        while self.running:
            try:
                logger.info(f"Spot worker WS metrics: disconnects={_ws_disconnects}, 1008_events={_ws_1008_count}, fallback_klines={_fallback_klines_count}")
                await asyncio.sleep(60)
            except Exception as e:
                logger.debug(f"Spot worker: metrics_loop error: {e}")
                await asyncio.sleep(60)
    
    async def snapshot_loop(self):
        """Цикл отправки snapshot."""
        iteration = 0
        while self.running:
            try:
                iteration += 1
                start = asyncio.get_event_loop().time()
                await self.send_snapshot()
                elapsed = asyncio.get_event_loop().time() - start
                # Логируем каждую 200-ю итерацию для диагностики
                if iteration % 200 == 0:
                    logger.info(f"Spot worker: snapshot_loop iteration #{iteration}, send_snapshot took {elapsed:.3f}s")
                # ОПТИМИЗАЦИЯ: цільовий інтервал 0.2с (~5 разів на секунду) для real-time даних
                sleep_time = max(0.05, 0.2 - elapsed)
                await asyncio.sleep(sleep_time)
            except Exception as e:
                logger.error(f"Spot worker: Error in snapshot loop: {e}")
                await asyncio.sleep(0.2)


class BinanceFuturesWorker:
    """Воркер для Futures рынка."""
    
    def __init__(self):
        self.ws_url = 'wss://fstream.binance.com/ws/'
        self.ws = None
        self.running = False
        self.channel_layer = get_channel_layer()
        self.group_name = 'screener_futures'
        self.open_interest_cache: Dict[str, float] = {}
        # История OI по минутам: {symbol: [(ts_minute, oi_value), ...]}
        self.oi_history: Dict[str, List[tuple]] = {}
        self.symbols: List[str] = []  # Будет загружено асинхронно в run()
        self._warmup_done = False
    
    async def connect_chunk(self, chunk_idx: int, stream_chunk: List[str], total_chunks: int):
        """Подключается к одному chunk streams."""
        streams_str = '/'.join(stream_chunk)
        combined_url = f'wss://fstream.binance.com/stream?streams={streams_str}'
        
        reconnect_delay = 5
        max_reconnect_delay = 60
        max_reconnect_attempts = 8

        while self.running:
            try:
                logger.info(f"Futures worker: Connecting to chunk {chunk_idx + 1}/{total_chunks} ({len(stream_chunk)} streams)")

                async with websockets.connect(
                    combined_url,
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=10,
                    max_size=10 * 1024 * 1024,
                ) as ws:
                    logger.info(f"Futures worker: Connected to Binance WebSocket chunk {chunk_idx + 1}")
                    reconnect_delay = 5

                    message_count = 0
                    first_message_logged = False

                    async for message in ws:
                        if not self.running:
                            break

                        try:
                            message_count += 1
                            # Логируем первое сообщение для подтверждения подключения
                            if message_count == 1:
                                logger.info(f"Futures worker chunk {chunk_idx + 1}: First message received, connection confirmed")
                                # Логируем содержимое первого сообщения для диагностики
                                try:
                                    first_data = json.loads(message)
                                    logger.info(f"Futures worker chunk {chunk_idx + 1}: First message keys: {list(first_data.keys())}, "
                                               f"stream: {first_data.get('stream', 'N/A')}, "
                                               f"data type: {type(first_data.get('data', 'N/A'))}")
                                except Exception as parse_err:
                                    logger.warning(f"Futures worker chunk {chunk_idx + 1}: Could not parse first message: {parse_err}")

                            # Пропускаем пустые сообщения
                            if not message or not message.strip():
                                continue

                            data = json.loads(message)
                            await self.process_message(data)

                            # Логируем каждые 1000 сообщений для мониторинга
                            if message_count % 1000 == 0:
                                logger.debug(f"Futures worker chunk {chunk_idx + 1}: Processed {message_count} messages")
                        except json.JSONDecodeError as e:
                            logger.error(f"Futures worker chunk {chunk_idx + 1}: Failed to parse JSON: {e}")
                        except Exception as e:
                            logger.error(f"Futures worker chunk {chunk_idx + 1}: Error processing message: {e}")
                            
            except websockets.exceptions.ConnectionClosed as e:
                global _ws_disconnects, _ws_1008_count
                _ws_disconnects += 1
                if e.code == 1008:
                    _ws_1008_count += 1
                    logger.warning(f"Futures worker chunk {chunk_idx + 1}: Connection closed with policy violation (1008). Total 1008 events: {_ws_1008_count}")
                    logger.warning("Policy violation (1008) can indicate too many streams per connection or subscription rate limits; consider reducing chunk size.")

                if e.code != 1000:
                    logger.warning(f"Futures worker chunk {chunk_idx + 1}: Connection closed: code={e.code} reason={getattr(e, 'reason', None)}; reconnecting in {reconnect_delay}s... (disconnects={_ws_disconnects})")
                else:
                    logger.debug(f"Futures worker chunk {chunk_idx + 1}: Connection closed normally: {e}")
            except asyncio.TimeoutError as e:
                logger.warning(f"Futures worker chunk {chunk_idx + 1}: Connection timeout: {e}, reconnecting in {reconnect_delay}s...")
            except Exception as e:
                error_str = str(e).lower()
                if 'keepalive' in error_str or 'ping timeout' in error_str or 'pong' in error_str:
                    logger.debug(f"Futures worker chunk {chunk_idx + 1}: Keepalive/pong timeout (normal): {e}")
                else:
                    logger.error(f"Futures worker chunk {chunk_idx + 1}: Connection error: {e}", exc_info=True)

            if not self.running:
                break

            jitter = random.uniform(0, max(1.0, reconnect_delay * 0.5))
            sleep_for = min(reconnect_delay + jitter, max_reconnect_delay)
            logger.info(f"Futures worker chunk {chunk_idx + 1}: Reconnecting in {sleep_for:.1f}s (next delay cap {max_reconnect_delay}s)")
            await asyncio.sleep(sleep_for)
            reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)
    
    async def connect(self):
        """Подключается к Binance WebSocket и подписывается на streams."""
        logger.info(f"Futures worker: connect() called with {len(self.symbols)} symbols")
        
        if not self.symbols:
            logger.error("Futures worker: No symbols available for connection")
            return
        
        streams = []
        
        # Собираем streams для всех данных
        for symbol in self.symbols:
            symbol_lower = symbol.lower()
            # aggTrade для Vdelta
            streams.append(f'{symbol_lower}@aggTrade')
            # kline только для 1m (остальные TF аггрегируем из 1m для экономии connections)
            streams.append(f'{symbol_lower}@kline_1m')
            # ticker для price, change_24h
            streams.append(f'{symbol_lower}@ticker')
            # markPrice для mark price и funding rate
            streams.append(f'{symbol_lower}@markPrice')
        
        # Глобальные потоки (для ликвидаций)
        streams.append('!forceOrder@arr')
        
        logger.info(f"Futures worker: Total streams to subscribe: {len(streams)} (4 per symbol + liquidations)")
        
        # Используем combined stream
        # Максимум 200 streams на соединение (ограничение длины URL ~2000 символов)
        # Каждый stream ~50-100 символов, так что 200 streams = ~10-20KB в URL
        max_streams = DEFAULT_MAX_STREAMS_PER_CONN
        stream_chunks = [streams[i:i + max_streams] for i in range(0, len(streams), max_streams)]
        
        logger.info(f"Futures worker: Split into {len(stream_chunks)} chunks")
        
        if not stream_chunks:
            logger.error("Futures worker: No stream chunks to connect to!")

            return
        
        # Создаем отдельные задачи для каждого chunk
        chunk_tasks = []
        for chunk_idx, stream_chunk in enumerate(stream_chunks):
            logger.info(f"Futures worker: Creating task for chunk {chunk_idx + 1}/{len(stream_chunks)} with {len(stream_chunk)} streams")
            task = asyncio.create_task(self.connect_chunk(chunk_idx, stream_chunk, len(stream_chunks)))
            chunk_tasks.append(task)
        
        logger.info(f"Futures worker: Created {len(chunk_tasks)} chunk tasks, waiting for connections...")
        
        # Ждем завершения всех задач (они будут работать пока self.running = True)
        try:
            await asyncio.gather(*chunk_tasks)
        except Exception as e:
            logger.error(f"Futures worker: Error in chunk tasks: {e}", exc_info=True)
    
    async def process_message(self, data: dict):
        """Обрабатывает сообщение от Binance."""
        if not isinstance(data, dict):
            logger.debug(f"Futures worker: Received non-dict data: {type(data)}")
            return
        
        if 'stream' not in data or 'data' not in data:
            logger.debug(f"Futures worker: Missing 'stream' or 'data' in message: {list(data.keys())}")
            return
        
        stream_name = data['stream']
        stream_data = data['data']
        
        # Обрабатываем специальные глобальные потоки
        if stream_name == '!forceOrder@arr':
            await self.process_force_order(stream_data)
            return
        elif stream_name == '!ticker@arr':
            # Для !ticker@arr данные приходят как массив ticker объектов
            # Формат: {"stream": "!ticker@arr", "data": [{"s": "BTCUSDT", "c": "50000", ...}, ...]}
            if isinstance(stream_data, list):
                processed_count = 0
                for item in stream_data:
                    symbol = item.get('s', '').upper()
                    if symbol and symbol in self.symbols:  # Проверяем что символ в нашем списке
                        await self.process_ticker(symbol, item)
                        processed_count += 1
                if processed_count > 0 and not hasattr(self, '_ticker_arr_logged'):
                    logger.info(f"Futures worker: Processed !ticker@arr with {processed_count} symbols")
                    self._ticker_arr_logged = True
            elif isinstance(stream_data, dict) and 's' in stream_data:
                symbol = stream_data.get('s', '').upper()
                if symbol and symbol in self.symbols:
                    await self.process_ticker(symbol, stream_data)
            return
        elif stream_name == '!markPrice@arr':
            # Для !markPrice@arr данные приходят как массив или одиночный объект
            if isinstance(stream_data, list):
                for item in stream_data:
                    symbol = item.get('s', '').upper()
                    if symbol:
                        await self.process_mark_price(symbol, item)
            elif isinstance(stream_data, dict) and 's' in stream_data:
                symbol = stream_data.get('s', '').upper()
                if symbol:
                    await self.process_mark_price(symbol, stream_data)
            return
        elif stream_name == '!bookTicker':
            # Для !bookTicker данные приходят как массив или одиночный объект
            if isinstance(stream_data, list):
                for item in stream_data:
                    symbol = item.get('s', '').upper()
                    if symbol:
                        await self.process_book_ticker(symbol, item)
            elif isinstance(stream_data, dict) and 's' in stream_data:
                symbol = stream_data.get('s', '').upper()
                if symbol:
                    await self.process_book_ticker(symbol, stream_data)
            return
        
        parts = stream_name.split('@')
        if len(parts) < 2:
            logger.debug(f"Futures worker: Invalid stream name format: {stream_name}")
            return
        
        symbol = parts[0].upper()
        stream_type = parts[1]
        
        # Логируем обработку ticker для диагностики (только первые несколько раз)
        if not hasattr(self, '_ticker_log_count'):
            self._ticker_log_count = {}
        if stream_type == 'ticker':
            if symbol not in self._ticker_log_count:
                self._ticker_log_count[symbol] = 0
            self._ticker_log_count[symbol] += 1
            if self._ticker_log_count[symbol] <= 3:
                logger.info(f"Futures worker: Processing ticker for {symbol}, price: {stream_data.get('c', 'N/A')}")
        
        if stream_type == 'aggTrade':
            await self.process_agg_trade(symbol, stream_data)
        elif stream_type.startswith('kline_'):
            interval = stream_type.split('_', 1)[1]
            await self.process_kline(symbol, interval, stream_data)
        elif stream_type == 'ticker':
            await self.process_ticker(symbol, stream_data)
        elif stream_type == 'markPrice':
            await self.process_mark_price(symbol, stream_data)
        elif stream_type == 'bookTicker':
            await self.process_book_ticker(symbol, stream_data)
        elif stream_type == 'depth10':
            await self.process_depth(symbol, stream_data)
        elif stream_type == 'depth@500ms':
            await self.process_depth(symbol, stream_data)
        elif stream_type == 'forceOrder':
            # Обрабатываем ликвидации для конкретного символа
            await self.process_force_order(stream_data)
        else:
            logger.debug(f"Futures worker: Unknown stream type: {stream_type} for {symbol}")
    
    async def process_agg_trade(self, symbol: str, data: dict, skip_logging: bool = False):
        """Обрабатывает aggTrade для Vdelta и ticks.
        
        НОВАЯ АРХИТЕКТУРА: все данные агрегируются в 1m бары через aggregation_model.
        Rolling windows для сырых трейдов УДАЛЕНЫ для экономии CPU/памяти.
        
        Args:
            symbol: Символ
            data: Данные aggTrade
            skip_logging: Пропустить логирование (для инициализации из исторических данных)
        """
        global _futures_data
        
        if symbol not in _futures_data:
            _futures_data[symbol] = {}
        
        price = float(data.get('p', 0))
        quantity = float(data.get('q', 0))
        is_buyer_maker = data.get('m', False)  # True = продажа (maker), False = покупка (taker)
        
        # Vdelta: объем покупок - объем продаж (в USDT)
        quote_volume = quantity * price
        is_buy = not is_buyer_maker  # True если агрессивная покупка
        
        # Используем реальное время события от Binance (T - trade time)
        event_time_raw = data.get('T') or data.get('E')
        if not event_time_raw:
            event_time_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        else:
            event_time_ms = int(event_time_raw * 1000) if event_time_raw < 1e12 else int(event_time_raw)
        
        # ЕДИНСТВЕННОЕ МЕСТО АГРЕГАЦИИ: все данные идут в 1m бары
        aggregate_trade_to_1m_bar(
            symbol=symbol,
            ts_ms=event_time_ms,
            quote_volume=quote_volume,
            is_buy=is_buy,
            price=price,
            market_type='futures'
        )
        
        # Диагностика для BTCUSDT (один раз)
        if not skip_logging and symbol == "BTCUSDT" and not hasattr(self, '_time_diag_logged'):
            self._time_diag_logged = True
            event_dt = datetime.fromtimestamp(event_time_ms / 1000, tz=timezone.utc)
            now_dt = datetime.now(timezone.utc)
            logger.info(f"[TIME DIAG] {symbol} event_time_ms={event_time_ms}, event_dt={event_dt.isoformat()}, now_dt={now_dt.isoformat()}, diff_sec={(now_dt - event_dt).total_seconds()}")
        
        # Храним только базовую информацию (ticks, last_price)
        if 'aggTrade' not in _futures_data[symbol]:
            _futures_data[symbol]['aggTrade'] = {
                'ticks': 0,
                'last_price': price,
            }
        
        _futures_data[symbol]['aggTrade']['ticks'] += 1
        _futures_data[symbol]['aggTrade']['last_price'] = price
        _futures_data[symbol]['aggTrade']['last_update'] = datetime.fromtimestamp(event_time_ms / 1000, tz=timezone.utc).isoformat()
    
    async def process_kline(self, symbol: str, interval: str, data: dict):
        """Обрабатывает kline для volatility, volume, ticks."""


        global _futures_data
        
        if symbol not in _futures_data:
            _futures_data[symbol] = {}
        
        if 'kline' not in _futures_data[symbol]:
            _futures_data[symbol]['kline'] = {}
        
        k = data.get('k', {})
        if not k:
            return
        
        is_closed = k.get('x', False)
        
        if interval not in _futures_data[symbol]['kline']:
            _futures_data[symbol]['kline'][interval] = {
                'open': float(k.get('o', 0)),
                'high': float(k.get('h', 0)),
                'low': float(k.get('l', 0)),
                'close': float(k.get('c', 0)),
                'volume': float(k.get('v', 0)),
                'quote_volume': float(k.get('q', 0)),
                'trades': int(k.get('n', 0)),
                'is_closed': is_closed,
            }
        else:
            # Обновляем данные для открытой свечи
            # ВАЖНО: для открытых свечей volume и trades накапливаются, а не заменяются
            kline_data = _futures_data[symbol]['kline'][interval]
            kline_data['high'] = max(kline_data['high'], float(k.get('h', 0)))
            kline_data['low'] = min(kline_data['low'], float(k.get('l', 0)))
            kline_data['close'] = float(k.get('c', 0))
            
            # Для открытых свечей (is_closed=False) volume накапливается
            # Для закрытых свечей (is_closed=True) volume заменяется
            if is_closed:
                # Свеча закрыта - используем финальные значения
                kline_data['volume'] = float(k.get('v', 0))
                kline_data['quote_volume'] = float(k.get('q', 0))
                kline_data['trades'] = int(k.get('n', 0))
            else:
                # Свеча открыта - используем текущие значения (они уже накоплены Binance)
                kline_data['volume'] = float(k.get('v', 0))
                kline_data['quote_volume'] = float(k.get('q', 0))
                kline_data['trades'] = int(k.get('n', 0))
            
            kline_data['is_closed'] = is_closed
        
        _futures_data[symbol]['kline'][interval]['last_update'] = datetime.now(timezone.utc).isoformat()
    
    async def process_ticker(self, symbol: str, data: dict):
        """Обрабатывает ticker для price, change, volume."""
        global _futures_data
        
        if symbol not in _futures_data:
            _futures_data[symbol] = {}
        
        # Получаем цену из разных возможных полей (c = close/last price)
        price_str = data.get('c') or data.get('lastPrice') or data.get('p') or '0'
        try:
            price = float(price_str)
        except (ValueError, TypeError):
            price = 0.0
        
        if price > 0:  # Только если цена валидная
            _futures_data[symbol]['ticker'] = {
                'price': price,  # Last price
                'open': float(data.get('o', data.get('openPrice', 0))),  # Open price (24h)
                'high': float(data.get('h', data.get('highPrice', 0))),
                'low': float(data.get('l', data.get('lowPrice', 0))),
                'change_24h': float(data.get('P', data.get('priceChangePercent', 0))),  # Price change percent
                'volume': float(data.get('v', data.get('volume', 0))),  # Base asset volume
                'quote_volume': float(data.get('q', data.get('quoteVolume', 0))),  # Quote asset volume
                'last_update': datetime.now(timezone.utc).isoformat(),
            }
            
            # Логируем первые несколько обновлений для диагностики
            if not hasattr(self, '_ticker_process_count'):
                self._ticker_process_count = {}
            if symbol not in self._ticker_process_count:
                self._ticker_process_count[symbol] = 0
            self._ticker_process_count[symbol] += 1
            if self._ticker_process_count[symbol] <= 3:
                logger.info(f"Futures worker: Processed ticker for {symbol}, price: {price}, data keys: {list(data.keys())[:10]}")
        else:
            logger.warning(f"Futures worker: Invalid price for {symbol}: {price_str} (data keys: {list(data.keys())[:10]})")
    
    async def process_mark_price(self, symbol: str, data: dict):
        """Обрабатывает markPrice для mark price и funding rate."""
        global _futures_data
        
        if symbol not in _futures_data:
            _futures_data[symbol] = {}
        
        _futures_data[symbol]['markPrice'] = {
            'mark_price': float(data.get('p', 0)),
            'funding_rate': float(data.get('r', 0)),
            'next_funding_time': int(data.get('T', 0)),
            'last_update': datetime.now(timezone.utc).isoformat(),
        }
    
    async def process_book_ticker(self, symbol: str, data: dict):
        """Обрабатывает bookTicker для bid/ask, spread."""
        global _futures_data
        
        if symbol not in _futures_data:
            _futures_data[symbol] = {}
        
        bid_price = float(data.get('b', 0))
        ask_price = float(data.get('a', 0))
        spread = ask_price - bid_price if bid_price > 0 and ask_price > 0 else 0
        
        _futures_data[symbol]['bookTicker'] = {
            'bid_price': bid_price,
            'bid_qty': float(data.get('B', 0)),
            'ask_price': ask_price,
            'ask_qty': float(data.get('A', 0)),
            'spread': spread,
            'last_update': datetime.now(timezone.utc).isoformat(),
        }
    
    async def process_depth(self, symbol: str, data: dict):
        """Обрабатывает depth10 для стакана."""
        global _futures_data
        
        if symbol not in _futures_data:
            _futures_data[symbol] = {}
        
        bids = [[float(b[0]), float(b[1])] for b in data.get('bids', [])]
        asks = [[float(a[0]), float(a[1])] for a in data.get('asks', [])]
        
        _futures_data[symbol]['depth'] = {
            'bids': bids,
            'asks': asks,
            'last_update': datetime.now(timezone.utc).isoformat(),
        }
    
    async def process_force_order(self, data: dict):
        """Обрабатывает forceOrder (ликвидации) согласно документации Binance.
        
        Формат данных для !forceOrder@arr:
        {
            'e': 'forceOrder',  # Event type
            'E': 123456789,      # Event time
            'o': {               # Order data
                's': 'BTCUSDT',  # Symbol
                'S': 'SELL',     # Side: SELL = Long ликвидация, BUY = Short ликвидация
                'o': 'LIMIT',    # Order type
                'f': 'IOC',      # Time in force
                'q': '0.001',    # Original quantity
                'p': '50000',    # Price
                'ap': '50000',   # Average price
                'X': 'FILLED',   # Order status
                'l': '0.001',    # Last filled quantity
                'z': '0.001',    # Cumulative filled quantity
                'T': 123456789,  # Trade time
                'i': 12345       # Order ID
            }
        }
        """
        try:
            # Для !forceOrder@arr данные приходят в формате { 'o': {...} }
            # Для symbol@forceOrder данные приходят напрямую
            order_data = data.get('o', data)
            
            if not order_data or 's' not in order_data:
                logger.debug(f"Futures worker: Invalid forceOrder data: {data}")
                return
            
            symbol_str = order_data['s']
            side = order_data.get('S', '')  # SELL = Long, BUY = Short
            price = float(order_data.get('p', 0) or order_data.get('ap', 0))
            quantity = float(order_data.get('q', 0) or order_data.get('l', 0))
            notional = price * quantity
            event_time = data.get('E', order_data.get('T', int(datetime.now(timezone.utc).timestamp() * 1000)))
            timestamp = datetime.fromtimestamp(event_time / 1000.0, tz=timezone.utc)
            
            # Формируем данные ликвидации
            liquidation_data = {
                'symbol': symbol_str,
                'side': 'Long' if side == 'SELL' else 'Short',  # SELL = Long ликвидация
                'price': price,
                'quantity': quantity,
                'notional': notional,
                'orderId': str(order_data.get('i', '')),
                'eventTime': event_time,
                'tradeTime': order_data.get('T', event_time),
            }
            
            # 1️⃣ Сохраняем в PostgreSQL (асинхронно, через sync_to_async)
            try:
                from asgiref.sync import sync_to_async
                from screener.models import Symbol, Liquidation
                from decimal import Decimal
                
                @sync_to_async
                def save_liquidation_to_db():
                    try:
                        symbol_obj = Symbol.objects.get(symbol=symbol_str, market_type='futures')
                        Liquidation.objects.create(
                            symbol=symbol_obj,
                            side=side,  # BUY или SELL
                            price=Decimal(str(price)),
                            quantity=Decimal(str(quantity)),
                            notional_value=Decimal(str(notional)),
                            timestamp=timestamp
                        )
                    except Symbol.DoesNotExist:
                        logger.warning(f"Symbol {symbol_str} not found in DB for liquidation")
                    except Exception as e:
                        logger.error(f"Error saving liquidation to DB: {e}", exc_info=True)
                
                await save_liquidation_to_db()
            except Exception as e:
                logger.error(f"Error in save_liquidation_to_db: {e}", exc_info=True)
            
            # 2️⃣ Публикуем в Redis PubSub (для real-time WebSocket)
            try:
                import redis
                import json
                
                redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
                redis_client.publish('liquidations', json.dumps({
                    'symbol': symbol_str,
                    'side': liquidation_data['side'],
                    'price': price,
                    'quantity': quantity,
                    'notional': notional,
                    'timestamp': timestamp.isoformat(),
                    'market_type': 'futures'
                }))
            except Exception as e:
                logger.error(f"Error publishing to Redis PubSub: {e}", exc_info=True)
            
            # 3️⃣ Отправляем через Channels group (legacy, можно убрать если используем только Redis PubSub)
            if self.channel_layer:
                try:
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'liquidation_data',
                            'data': liquidation_data,
                            'market_type': 'futures',
                            'timestamp': timestamp.isoformat(),
                        }
                    )
                except Exception as e:
                    logger.error(f"Futures worker: Error sending liquidation to group {self.group_name}: {e}", exc_info=True)
            
            # Логируем первые 10 ликвидаций для диагностики
            if not hasattr(self, '_liquidation_count'):
                self._liquidation_count = 0
            self._liquidation_count += 1
            if self._liquidation_count <= 10:
                logger.info(f"Futures worker: ✅ Liquidation #{self._liquidation_count} for {symbol_str}: {liquidation_data['side']} ${notional:,.0f}")
            else:
                logger.debug(f"Futures worker: Liquidation for {symbol_str}: {liquidation_data['side']} ${notional:,.0f}")
                
        except Exception as e:
            logger.error(f"Futures worker: Error processing forceOrder: {e}", exc_info=True)
    
    async def fetch_open_interest(self, symbol: str):
        """Получает Open Interest через REST API."""
        import aiohttp
        
        url = f'https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}'
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.open_interest_cache[symbol] = float(data.get('openInterest', 0))
        except Exception as e:
            logger.error(f"Futures worker: Error fetching OI for {symbol}: {e}")
    
    async def fetch_open_interest_bulk(self, symbols: List[str]):
        """Получает Open Interest для всех символов параллельно через REST API с оптимизацией."""
        import aiohttp
        import time
        
        if not symbols:
            return
        
        # Получаем или создаем глобальный session (connection pooling)
        global _http_session, _session_lock
        async with _session_lock:
            if _http_session is None or _http_session.closed:
                connector = aiohttp.TCPConnector(
                    limit=100,  # Максимум 100 одновременных соединений
                    limit_per_host=50,  # Максимум 50 на хост
                    ttl_dns_cache=300,  # Кеш DNS на 5 минут
                    force_close=False,  # Переиспользование соединений
                )
                timeout = aiohttp.ClientTimeout(total=10, connect=5)
                _http_session = aiohttp.ClientSession(
                    connector=connector,
                    timeout=timeout,
                )
        
        try:
            # Батчинг запросов с учетом лимитов Binance
            # Binance Futures: 1200 weight/min = 20 weight/sec
            # openInterest: 1 weight per request
            # Максимум 20 запросов в секунду, но делаем батчи по 15 для безопасности
            batch_size = 15
            delay_between_batches = 0.8  # 0.8 сек между батчами (15 req / 0.8s = ~18.75 req/s < 20)
            
            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]
                tasks = []
                for symbol in batch:
                    url = f'https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}'
                    tasks.append(self._fetch_oi_single(_http_session, symbol, url))
                
                # Выполняем батч параллельно
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Задержка между батчами (кроме последнего)
                if i + batch_size < len(symbols):
                    await asyncio.sleep(delay_between_batches)
        except Exception as e:
            logger.error(f"Futures worker: Error in bulk OI fetch: {e}", exc_info=True)

    async def _fetch_recent_klines_futures(self, symbol: str, interval: str, limit: int = 3):
        """Fetch recent klines for futures market via REST as a fallback when windows are empty."""
        import aiohttp
        global _http_session, _session_lock, _fallback_klines_count

        base = 'https://fapi.binance.com'
        url = f"{base}/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"

        async with _session_lock:
            if _http_session is None or _http_session.closed:
                connector = aiohttp.TCPConnector(limit=60, limit_per_host=30, ttl_dns_cache=300)
                timeout = aiohttp.ClientTimeout(total=8, connect=4)
                _http_session = aiohttp.ClientSession(connector=connector, timeout=timeout)

        try:
            async with _http_session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    klines = []
                    for k in data:
                        open_price = float(k[1])
                        close_price = float(k[4])
                        quote_vol = float(k[7])
                        klines.append({'open': open_price, 'close': close_price, 'quote_volume': quote_vol})
                    _fallback_klines_count += 1
                    return klines
        except Exception as e:
            logger.debug(f"Futures worker: fetch_recent_klines_futures failed for {symbol} {interval}: {e}")
        return None
    
    async def _fetch_oi_single(self, session, symbol: str, url: str):
        """Вспомогательная функция для получения OI одного символа."""
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    old_oi = self.open_interest_cache.get(symbol, 0)
                    new_oi = float(data.get('openInterest', 0))
                    self.open_interest_cache[symbol] = new_oi
                    
                    # Обновляем историю OI (для расчёта изменений по TF)
                    self._update_oi_history(symbol, new_oi)
                    
                    # Сохраняем предыдущее значение для вычисления изменения
                    global _futures_data
                    if symbol not in _futures_data:
                        _futures_data[symbol] = {}
                    _futures_data[symbol]['oi_previous'] = old_oi
        except Exception as e:
            logger.debug(f"Futures worker: Error fetching OI for {symbol}: {e}")
    
    def _update_oi_history(self, symbol: str, oi_value: float):
        """Обновляет историю OI для символа (хранит последние 1440 минут = 24ч)."""
        import time
        ts_minute = int(time.time() // 60) * 60  # Округляем до минуты
        
        if symbol not in self.oi_history:
            self.oi_history[symbol] = []
        
        history = self.oi_history[symbol]
        
        # Добавляем новую точку только если минута изменилась
        if not history or history[-1][0] < ts_minute:
            history.append((ts_minute, oi_value))
        else:
            # Обновляем последнее значение
            history[-1] = (ts_minute, oi_value)
        
        # Оставляем только последние 1440 точек (24 часа)
        if len(history) > 1440:
            self.oi_history[symbol] = history[-1440:]
    
    def get_oi_change_by_tf(self, symbol: str, tf: str) -> float:
        """Рассчитывает изменение OI в % для заданного TF."""
        if symbol not in self.oi_history:
            return 0.0
        
        history = self.oi_history[symbol]
        if len(history) < 2:
            return 0.0
        
        # Определяем сколько минут назад смотреть
        tf_minutes = TF_TO_MINUTES.get(tf, 1)
        
        current_oi = history[-1][1]
        current_ts = history[-1][0]
        target_ts = current_ts - (tf_minutes * 60)
        
        # Ищем ближайшее значение к target_ts
        old_oi = None
        for ts, oi in history:
            if ts <= target_ts:
                old_oi = oi
            else:
                break
        
        # Если не нашли точное значение, берём самое старое
        if old_oi is None and history:
            old_oi = history[0][1]
        
        if old_oi and old_oi > 0:
            return ((current_oi - old_oi) / old_oi) * 100
        return 0.0
    
    async def oi_update_loop(self):
        """Цикл обновления Open Interest с учетом лимитов Binance."""
        while self.running:
            try:
                # Обновляем OI для всех символов с батчингом и rate limiting
                if self.symbols:
                    await self.fetch_open_interest_bulk(self.symbols)
                
                # Интервал увеличен до 3 секунд для соблюдения лимитов Binance
                # 529 символов / 15 (batch) = ~36 батчей
                # 36 батчей * 0.8 сек = ~29 секунд на полный цикл
                # Плюс запас для безопасности = 3 секунды между циклами
                await asyncio.sleep(3.0)
            except Exception as e:
                logger.error(f"Futures worker: Error in OI update loop: {e}", exc_info=True)
                await asyncio.sleep(3.0)
    
    async def send_snapshot(self):
        """Собирает snapshot и отправляет через Channels group."""
        global _futures_data
        
        # Ждем первого сообщения от Binance перед отправкой снапшотов
        if not self._warmup_done:
            has_ticker = any(data.get('ticker') for data in _futures_data.values())
            has_agg = any(data.get('aggTrade') for data in _futures_data.values())
            if not (has_ticker or has_agg):
                logger.debug("Futures worker: Warmup - waiting for first Binance messages before sending snapshots")
                return
            self._warmup_done = True
            logger.info("Futures worker: Warmup done! Starting to send snapshots")
        
        # КРИТИЧНО: Створюємо КОПІЮ _futures_data перед ітерацією
        # Це вирішує race condition коли aggTrade handler змінює dict одночасно з читанням
        snapshot_data = dict(_futures_data)
        
        snapshot = []
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        
        for symbol in self.symbols:
            if symbol not in snapshot_data:
                continue
            
            symbol_data = snapshot_data[symbol]
            
            ticker = symbol_data.get('ticker', {})
            mark_price = symbol_data.get('markPrice', {})
            agg_trade = symbol_data.get('aggTrade', {})
            klines = symbol_data.get('kline', {})
            
            # Пропускаем символы без ticker данных (нет цены)
            if not ticker or ticker.get('price', 0) == 0:
                continue
            
            current_price = ticker.get('price', 0)
            
            # Получаем OI из кеша (обновляется отдельной задачей каждую секунду)
            oi = self.open_interest_cache.get(symbol, 0)
            oi_prev = symbol_data.get('oi_previous', oi)
            
            # Вычисляем OI Change
            if oi_prev > 0:
                oi_change = ((oi - oi_prev) / oi_prev) * 100
            else:
                oi_change = 0.0
            
            row_data = {
                'symbol': symbol,
                'price': current_price,
                'mark_price': mark_price.get('mark_price', 0),
                'funding_rate': mark_price.get('funding_rate', 0),
                'open_interest': oi,
                'change_24h': ticker.get('change_24h', 0),
                'volume_24h': ticker.get('quote_volume', 0),
                'ticks_1m': agg_trade.get('ticks', 0) if agg_trade else 0,
            }
            
            # НОВАЯ АРХИТЕКТУРА: все TF данные из агрегированных 1m баров
            for interval in KLINE_INTERVALS:
                # Получаем агрегированные данные из 1m баров
                tf_data = aggregate_1m_bars_to_tf(symbol, now_ms, interval, market_type='futures')
                
                if tf_data and tf_data.get('bars_count', 0) > 0:
                    # Данные есть - используем их
                    row_data[f'vdelta_{interval}'] = tf_data['vdelta']
                    row_data[f'volume_{interval}'] = tf_data['volume']
                    row_data[f'change_{interval}'] = tf_data['change_pct']
                    row_data[f'ticks_{interval}'] = tf_data['trades']
                    row_data[f'volatility_{interval}'] = 0.0  # TODO: добавить в aggregation_model
                else:
                    # Fallback на kline данные от Binance
                    if interval in klines:
                        kline = klines[interval]
                        open_price = kline.get('open', 0)
                        close_price = kline.get('close', 0)
                        high = kline.get('high', 0)
                        low = kline.get('low', 0)
                        
                        if open_price > 0:
                            row_data[f'volatility_{interval}'] = ((high - low) / open_price) * 100
                            row_data[f'change_{interval}'] = ((close_price - open_price) / open_price) * 100
                        else:
                            row_data[f'volatility_{interval}'] = 0.0
                            row_data[f'change_{interval}'] = 0.0
                        
                        row_data[f'volume_{interval}'] = kline.get('quote_volume', 0)
                        row_data[f'ticks_{interval}'] = kline.get('trades', 0)
                        row_data[f'vdelta_{interval}'] = 0  # kline не имеет vdelta
                    else:
                        # Нет данных - нули
                        row_data[f'volatility_{interval}'] = 0.0
                        row_data[f'change_{interval}'] = 0.0
                        row_data[f'volume_{interval}'] = 0.0
                        row_data[f'ticks_{interval}'] = 0
                        row_data[f'vdelta_{interval}'] = 0
            
            # OI Change для каждого таймфрейма (из истории OI)
            for interval in KLINE_INTERVALS:
                row_data[f'oi_change_{interval}'] = self.get_oi_change_by_tf(symbol, interval)
            
            # Timestamp
            if agg_trade and 'last_update' in agg_trade:
                row_data['timestamp'] = agg_trade['last_update']
            else:
                row_data['timestamp'] = datetime.now(timezone.utc).isoformat()
            
            # Send only raw fields; formatting happens client-side to keep payload small
            snapshot.append(_project_row_for_client(row_data, market_type='futures'))
        
        # Persist aggregated snapshot to DB at a throttled interval
        # NOTE: Temporarily disabled for performance - DB writes are too slow
        # try:
        #     if sync_to_async and ScreenerSnapshot is not None and Symbol is not None:
        #         now = asyncio.get_event_loop().time()
        #         last = _last_db_write_time.get('futures', 0.0)
        #         if now - last >= _min_db_write_interval:
        #             snapshot_copy = copy.deepcopy(snapshot)
        #             asyncio.create_task(_persist_snapshot_to_db(snapshot_copy, market_type='futures'))
        #             _last_db_write_time['futures'] = now
        # except Exception:
        #     logger.exception("Failed to schedule DB persistence for futures snapshot")
        
        # Отправляем через Channels group (только если есть данные)
        if not snapshot:
            logger.warning(f"Futures worker: Empty snapshot, skipping send. Symbols in snapshot_data: {len([s for s in self.symbols if s in snapshot_data])}")
            return  # Не отправляем пустые snapshot
        
        # Синхронизация отправки snapshot - простая throttle без lock
        import time
        global _last_snapshot_time, _min_snapshot_interval
        
        current_time = time.time()
        
        # Проверяем, прошло ли достаточно времени с последней отправки
        time_since_last = current_time - _last_snapshot_time.get('futures', 0)
        if time_since_last < _min_snapshot_interval:
            return
        
        _last_snapshot_time['futures'] = current_time
        
        if self.channel_layer:
            try:
                # Limit snapshot size
                MAX_SNAPSHOT_SIZE = 200
                if len(snapshot) > MAX_SNAPSHOT_SIZE:
                    snapshot = snapshot[:MAX_SNAPSHOT_SIZE]
                
                await asyncio.wait_for(
                    self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'screener_data',
                            'data': snapshot,
                            'market_type': 'futures',
                            'timestamp': datetime.now(timezone.utc).isoformat(),
                        }
                    ),
                    timeout=5.0  # Збільшено до 5с для стабільності
                )
                # Log successful send (every 50th)
                if not hasattr(self, '_send_count'):
                    self._send_count = 0
                self._send_count += 1
                if self._send_count % 50 == 0:
                    logger.info(f"Futures worker: ✅ Sent snapshot #{self._send_count} with {len(snapshot)} symbols to {self.group_name}")
            except asyncio.TimeoutError:
                logger.warning(f"Futures worker: Timeout sending snapshot to {self.group_name}")
            except Exception as e:
                error_msg = str(e).lower()
                if 'over capacity' not in error_msg and 'full' not in error_msg:
                    logger.error(f"Futures worker: Error sending snapshot: {e}")
                    try:
                        self.channel_layer = get_channel_layer()
                    except Exception:
                        pass
        else:
            logger.warning(f"Futures worker: Channel layer is None, cannot send snapshot to {self.group_name}")
    
    def _calculate_volatility(self, kline: dict) -> float:
        """Вычисляет волатильность из kline данных.
        
        Volatility = (high - low) / open * 100 (процент)
        Это стандартная формула волатильности для криптовалютных рынков.
        """
        high = kline.get('high', 0)
        low = kline.get('low', 0)
        open_price = kline.get('open', 0)
        
        if open_price == 0:
            return 0.0
        
        # Волатильность: (high - low) / open * 100 (процент)
        return ((high - low) / open_price) * 100
    
    async def run(self):
        """Запускает воркер."""
        self.running = True
        
        # Загружаем символы из БД асинхронно
        if not self.symbols:
            self.symbols = await get_symbols_from_db('futures')
            logger.info(f"Futures worker: Loaded {len(self.symbols)} symbols")
        
        # Восстанавливаем 1m бары из Redis для персистентності між перезапусками
        bars_restored = restore_bars_from_redis(market_type='futures')
        logger.info(f"Futures worker: Restored {bars_restored} 1m bars from Redis")
        
        # Якщо даних недостатньо, догружаємо через Klines API
        if self.symbols and bars_restored < len(self.symbols) * 1440:  # Мінімум 24 години на символ
            logger.info(f"Futures worker: Not enough bars in Redis, fetching from Klines API...")
            filled = await fill_missing_bars_from_klines(self.symbols, market_type='futures')
            logger.info(f"Futures worker: Filled {filled} bars from Klines API")
        
        if not self.symbols:
            logger.error("Futures worker: No symbols loaded, cannot start")
            return
        
        # Запускаем задачи
        snapshot_task = asyncio.create_task(self.snapshot_loop())
        oi_update_task = asyncio.create_task(self.oi_update_loop())

        # Запускаем подключение к WebSocket
        try:
            await self.connect()
        finally:
            snapshot_task.cancel()
            oi_update_task.cancel()

            # Закрываем глобальный aiohttp session
            global _http_session, _session_lock
            try:
                async with _session_lock:
                    if _http_session is not None and not getattr(_http_session, 'closed', False):
                        await _http_session.close()
                        _http_session = None
            except Exception:
                pass
    
    async def snapshot_loop(self):
        """Цикл отправки snapshot."""
        iteration = 0
        while self.running:
            try:
                iteration += 1
                start = asyncio.get_event_loop().time()
                await self.send_snapshot()
                elapsed = asyncio.get_event_loop().time() - start
                # Логируем каждую 200-ю итерацию для диагностики
                if iteration % 200 == 0:
                    logger.info(f"Futures worker: snapshot_loop iteration #{iteration}, send_snapshot took {elapsed:.3f}s")
                # ОПТИМИЗАЦИЯ: цільовий інтервал 0.2с (~5 разів на секунду) для real-time даних
                sleep_time = max(0.05, 0.2 - elapsed)
                await asyncio.sleep(sleep_time)
            except Exception as e:
                logger.error(f"Futures worker: Error in snapshot loop: {e}")
                await asyncio.sleep(0.2)

# Глобальные задачи воркеров
_spot_worker_task: Optional[asyncio.Task] = None
_futures_worker_task: Optional[asyncio.Task] = None
_workers_started = False


async def start_workers():
    """Запускает воркеры для spot и futures."""
    global _spot_worker_task, _futures_worker_task, _workers_started
    
    # Проверяем, не запущены ли уже воркеры
    if _workers_started:
        logger.debug("Binance workers already started, skipping")
        return
    
    if _spot_worker_task and not _spot_worker_task.done():
        logger.debug("Spot worker task already running")
        return
    
    if _futures_worker_task and not _futures_worker_task.done():
        logger.debug("Futures worker task already running")
        return
    
    # Проверяем тип Channel Layer и подключение к Redis
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()
    if channel_layer:
        layer_class = channel_layer.__class__.__name__
        logger.info(f"Using Channel Layer: {layer_class}")
        
        if layer_class == "InMemoryChannelLayer":
            logger.warning("⚠️  WARNING: Using InMemoryChannelLayer! This only works within a single process.")
            logger.warning("⚠️  If you run multiple processes (workers), they won't share data.")
            logger.warning("⚠️  For production, use Redis: CHANNEL_LAYERS with channels_redis.core.RedisChannelLayer")
        elif layer_class == "RedisChannelLayer":
            # Проверяем подключение к Redis
            try:
                # Пробуем отправить тестовое сообщение для проверки подключения
                test_group = "test_connection"
                await channel_layer.group_send(
                    test_group,
                    {"type": "test", "data": "ping"}
                )
                logger.info("✅ Redis connection verified successfully")
            except Exception as e:
                logger.error(f"❌ Redis connection failed: {e}")
                logger.error("Please check that Redis is running: sudo systemctl status redis-server")
    else:
        logger.error("Channel layer is None! Workers cannot send data to consumers.")
    
    logger.info("Starting Binance workers...")
    
    spot_worker = BinanceSpotWorker()
    futures_worker = BinanceFuturesWorker()
    
    _spot_worker_task = asyncio.create_task(spot_worker.run())
    _futures_worker_task = asyncio.create_task(futures_worker.run())
    
    _workers_started = True
    logger.info("✅ Binance workers started successfully")
    logger.info(f"   Spot worker task: {_spot_worker_task}")
    logger.info(f"   Futures worker task: {_futures_worker_task}")
    
    # Ждём завершения workers (они работают бесконечно пока не будут отменены)
    try:
        await asyncio.gather(_spot_worker_task, _futures_worker_task)
    except asyncio.CancelledError:
        logger.info("Workers cancelled")
    except Exception as e:
        logger.error(f"Workers error: {e}", exc_info=True)


async def stop_workers():
    """Останавливает воркеры."""
    global _spot_worker_task, _futures_worker_task, _workers_started
    
    if _spot_worker_task:
        _spot_worker_task.cancel()
        try:
            await _spot_worker_task
        except asyncio.CancelledError:
            pass
    
    if _futures_worker_task:
        _futures_worker_task.cancel()
        try:
            await _futures_worker_task
        except asyncio.CancelledError:
            pass
    
    _workers_started = False
    logger.info("Binance workers stopped")
