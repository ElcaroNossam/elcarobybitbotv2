"""
ЕДИНАЯ ПРАВИЛЬНАЯ МОДЕЛЬ АГРЕГАЦИИ С ПЕРСИСТЕНТНОСТЬЮ
======================================================

Базовый принцип:
1. aggTrade приходят с биржи → агрегируем в 1m бары
2. Все старшие TF строим КАК СУММУ 1m баров
3. Формула vDelta одинаковая для всех TF: Σ(buy_volume) - Σ(sell_volume)
4. Формула volume одинаковая: Σ(quote_volume всех сделок)

Архитектура:
- В памяти хранятся только 1m бары (последние 1440 штук = 24 часа)
- При создании snapshot берем нужное количество 1m баров и суммируем
- vDelta = разница между покупками и продажами
- **ВАЖНО**: 1m бары сохраняются в Redis для персистентности между перезапусками

Формула:
    vDelta_TF = Σ(vdelta_1m в этом TF) = Σ(buy_vol_1m) - Σ(sell_vol_1m)
    volume_TF = Σ(volume_1m в этом TF)

Дополнительная метрика:
    vdelta_ratio = vDelta / volume  # нормализованный vDelta в диапазоне [-1, 1]
"""

import logging
import json
import redis
from datetime import datetime, timezone
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Подключение к Redis
try:
    _redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)
    _redis_client.ping()
    logger.info("✅ Redis connection established for 1m bars persistence")
except Exception as e:
    logger.error(f"❌ Redis connection failed: {e}")
    _redis_client = None

# Глобальные хранилища 1m баров для каждого рынка (в памяти для скорости)
# Структура: {symbol: {ts_minute: {volume, vdelta, trades, price_open, price_close, price_high, price_low}}}
_spot_1m_bars = {}
_futures_1m_bars = {}

# Кеш результатов агрегации TF (обновляется при каждом новом 1m баре)
# Структура: {symbol: {tf: {cached_minute: ts_minute, data: {...}}}}
_spot_tf_cache = {}
_futures_tf_cache = {}

# Redis keys для персистентности
REDIS_KEY_PREFIX_SPOT = "bars:spot:"
REDIS_KEY_PREFIX_FUTURES = "bars:futures:"
REDIS_BARS_TTL = 86400 + 3600  # 25 часов (24ч данных + запас)

# Маппинг TF в количество минут
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


def _save_bar_to_redis(symbol: str, ts_minute: int, bar: dict, market_type: str = 'spot'):
    """Сохранить 1m бар в Redis для персистентности"""
    if not _redis_client:
        return
    
    try:
        key_prefix = REDIS_KEY_PREFIX_SPOT if market_type == 'spot' else REDIS_KEY_PREFIX_FUTURES
        redis_key = f"{key_prefix}{symbol}:{ts_minute}"
        
        # Сериализуем бар в JSON
        bar_json = json.dumps(bar)
        
        # Сохраняем с TTL
        _redis_client.setex(redis_key, REDIS_BARS_TTL, bar_json)
    except Exception as e:
        logger.error(f"Failed to save bar to Redis: {e}")


def _load_bars_from_redis(symbol: str, market_type: str = 'spot') -> Dict[int, dict]:
    """Загрузить все 1m бары символа из Redis"""
    if not _redis_client:
        return {}
    
    try:
        key_prefix = REDIS_KEY_PREFIX_SPOT if market_type == 'spot' else REDIS_KEY_PREFIX_FUTURES
        pattern = f"{key_prefix}{symbol}:*"
        
        bars = {}
        for key in _redis_client.scan_iter(match=pattern, count=1000):
            key_str = key.decode('utf-8') if isinstance(key, bytes) else key
            ts_minute = int(key_str.split(':')[-1])
            
            bar_json = _redis_client.get(key)
            if bar_json:
                bar_data = json.loads(bar_json)
                bars[ts_minute] = bar_data
        
        logger.info(f"✅ Loaded {len(bars)} 1m bars for {symbol} ({market_type}) from Redis")
        return bars
    except Exception as e:
        logger.error(f"Failed to load bars from Redis: {e}")
        return {}


def restore_bars_from_redis(market_type: str = 'spot') -> int:
    """Восстановить все бары из Redis при старте workers. Возвращает количество загруженных баров."""
    if not _redis_client:
        logger.warning("Redis not available, skipping bars restoration")
        return 0
    
    bars_dict = _spot_1m_bars if market_type == 'spot' else _futures_1m_bars
    
    try:
        key_prefix = REDIS_KEY_PREFIX_SPOT if market_type == 'spot' else REDIS_KEY_PREFIX_FUTURES
        pattern = f"{key_prefix}*"
        
        symbols_restored = set()
        total_bars = 0
        
        for key in _redis_client.scan_iter(match=pattern, count=1000):
            key_str = key.decode('utf-8') if isinstance(key, bytes) else key
            parts = key_str.split(':')
            symbol = parts[-2]
            ts_minute = int(parts[-1])
            
            bar_json = _redis_client.get(key)
            if bar_json:
                bar_data = json.loads(bar_json)
                
                if symbol not in bars_dict:
                    bars_dict[symbol] = {}
                
                bars_dict[symbol][ts_minute] = bar_data
                symbols_restored.add(symbol)
                total_bars += 1
        
        logger.info(f"✅ Restored {total_bars} 1m bars for {len(symbols_restored)} symbols ({market_type}) from Redis")
        return total_bars
    except Exception as e:
        logger.error(f"Failed to restore bars from Redis: {e}")
        return 0


def get_bars_count(symbol: str, market_type: str = 'spot') -> int:
    """Получить количество 1m баров для символа"""
    bars_dict = _spot_1m_bars if market_type == 'spot' else _futures_1m_bars
    if symbol not in bars_dict:
        return 0
    return len(bars_dict[symbol])


def add_kline_to_bars(symbol: str, kline_data: dict, market_type: str = 'spot'):
    """
    Добавить kline из REST API в хранилище баров.
    
    kline_data должен содержать:
    - open_time: timestamp начала свечи (ms)
    - open: цена открытия
    - high: максимальная цена
    - low: минимальная цена
    - close: цена закрытия
    - volume: объем в USDT (quote volume)
    - taker_buy_volume: объем покупок маркет-мейкерами
    """
    bars_dict = _spot_1m_bars if market_type == 'spot' else _futures_1m_bars
    
    ts_minute = kline_data.get('open_time', 0)
    if ts_minute == 0:
        return
    
    # Инициализируем символ если нужно
    if symbol not in bars_dict:
        bars_dict[symbol] = {}
    
    # Не перезаписываем существующие бары (они могут быть точнее из aggTrades)
    if ts_minute in bars_dict[symbol]:
        return
    
    volume = float(kline_data.get('volume', 0))
    taker_buy_volume = float(kline_data.get('taker_buy_volume', 0))
    
    # vdelta = taker_buy_volume - taker_sell_volume
    # taker_sell_volume = volume - taker_buy_volume
    vdelta = taker_buy_volume - (volume - taker_buy_volume)
    
    bar = {
        'volume': volume,
        'vdelta': vdelta,
        'trades': int(kline_data.get('trades', 0)),
        'price_open': float(kline_data.get('open', 0)),
        'price_close': float(kline_data.get('close', 0)),
        'price_high': float(kline_data.get('high', 0)),
        'price_low': float(kline_data.get('low', 0)),
    }
    
    bars_dict[symbol][ts_minute] = bar
    
    # Сохраняем в Redis
    _save_bar_to_redis(symbol, ts_minute, bar, market_type)


def aggregate_trade_to_1m_bar(symbol: str, ts_ms: int, quote_volume: float, is_buy: bool, price: float, market_type: str = 'spot'):
    """
    Агрегация одной сделки в базовый 1m бар.
    
    Это ЕДИНСТВЕННАЯ функция, которая обрабатывает сделки.
    Все остальные TF строятся из этих 1m баров.
    
    Args:
        symbol: торговая пара (BTCUSDT, ETHUSDT, ...)
        ts_ms: timestamp сделки в миллисекундах
        quote_volume: объем в котируемой валюте (USDT)
        is_buy: True если агрессивная покупка, False если агрессивная продажа
        price: цена сделки
        market_type: 'spot' или 'futures'
    
    Формула vDelta:
        vdelta += quote_volume  если is_buy
        vdelta -= quote_volume  если не is_buy
    """
    # Выбираем хранилище
    bars_dict = _spot_1m_bars if market_type == 'spot' else _futures_1m_bars
    
    # Округляем timestamp до начала минуты
    ts_minute = (ts_ms // 60000) * 60000
    
    # Инициализируем символ если нужно
    if symbol not in bars_dict:
        bars_dict[symbol] = {}
    
    # Инициализируем бар если нужно
    if ts_minute not in bars_dict[symbol]:
        bars_dict[symbol][ts_minute] = {
            'volume': 0.0,
            'vdelta': 0.0,
            'trades': 0,
            'price_open': price,
            'price_close': price,
            'price_high': price,
            'price_low': price,
        }
    
    bar = bars_dict[symbol][ts_minute]
    
    # Агрегируем данные
    bar['volume'] += quote_volume
    bar['vdelta'] += quote_volume if is_buy else -quote_volume  # ЕДИНАЯ ФОРМУЛА
    bar['trades'] += 1
    bar['price_close'] = price  # обновляем последнюю цену
    bar['price_high'] = max(bar['price_high'], price)
    bar['price_low'] = min(bar['price_low'], price)
    
    # Сохраняем в Redis для персистентности
    _save_bar_to_redis(symbol, ts_minute, bar, market_type)
    
    # Очистка старых баров (храним только последние 24 часа = 1440 минут)
    cutoff_minute = ts_minute - (1440 * 60000)
    old_minutes = [m for m in bars_dict[symbol] if m < cutoff_minute]
    for m in old_minutes:
        del bars_dict[symbol][m]
        # Удаляем из Redis тоже
        if _redis_client:
            try:
                key_prefix = REDIS_KEY_PREFIX_SPOT if market_type == 'spot' else REDIS_KEY_PREFIX_FUTURES
                redis_key = f"{key_prefix}{symbol}:{m}"
                _redis_client.delete(redis_key)
            except Exception:
                pass


def aggregate_1m_bars_to_tf(symbol: str, current_ts_ms: int, timeframe: str, market_type: str = 'spot'):
    """
    Агрегация 1m баров в любой старший TF.
    
    Это ЕДИНСТВЕННАЯ функция, которая создает старшие TF.
    Все TF строятся ОДИНАКОВО - как сумма нужного количества 1m баров.
    
    ОПТИМИЗАЦИЯ: использует кеш, обновляемый каждую минуту
    
    Args:
        symbol: торговая пара
        current_ts_ms: текущее время в миллисекундах
        timeframe: '2m', '3m', '5m', '15m', '30m', '1h', '8h', '1d'
        market_type: 'spot' или 'futures'
    
    Returns:
        dict с полями:
            - volume: суммарный объем
            - vdelta: суммарный vDelta (покупки - продажи)
            - vdelta_ratio: нормализованный vDelta = vdelta / volume (диапазон [-1, 1])
            - trades: количество сделок
            - price_open: цена открытия первого 1m бара
            - price_close: цена закрытия последнего 1m бара
            - change_pct: процентное изменение цены
            - bars_count: сколько 1m баров было использовано
        
        None если недостаточно данных
    
    Математика:
        volume_TF = Σ volume_1m
        vdelta_TF = Σ vdelta_1m = Σ(buy_vol_1m - sell_vol_1m)
    """
    # Выбираем хранилище и кеш
    bars_dict = _spot_1m_bars if market_type == 'spot' else _futures_1m_bars
    cache_dict = _spot_tf_cache if market_type == 'spot' else _futures_tf_cache
    
    if symbol not in bars_dict or not bars_dict[symbol]:
        return None
    
    # ОПТИМИЗАЦІЯ: Кеш на 5 секунд (замість 60с) для більш реального оновлення vDelta
    # Кешуємо по 5-секундних інтервалах для балансу CPU vs актуальність
    current_5sec = (current_ts_ms // 5000) * 5000
    
    # Проверяем кеш
    if symbol in cache_dict and timeframe in cache_dict[symbol]:
        cached = cache_dict[symbol][timeframe]
        if cached.get('cached_minute') == current_5sec:
            return cached.get('data')
    
    # Получаем количество минут для этого TF
    minutes_needed = TF_TO_MINUTES.get(timeframe, 1)
    minutes_ms = minutes_needed * 60000
    
    # Определяем окно времени
    cutoff_ms = current_ts_ms - minutes_ms
    
    # Собираем все 1m бары в этом окне - ОПТИМИЗИРОВАНО: single-pass без сортировки
    symbol_bars = bars_dict[symbol]
    
    # Single-pass агрегация
    volume_sum = 0.0
    vdelta_sum = 0.0
    trades_sum = 0
    price_open = None
    price_close = None
    min_ts = float('inf')
    max_ts = 0
    bars_count = 0
    
    for ts_min, bar in symbol_bars.items():
        if ts_min >= cutoff_ms:
            bars_count += 1
            volume_sum += bar['volume']
            vdelta_sum += bar['vdelta']
            trades_sum += bar['trades']
            
            # Отслеживаем первый и последний бар по времени
            if ts_min < min_ts:
                min_ts = ts_min
                price_open = bar['price_open']
            if ts_min > max_ts:
                max_ts = ts_min
                price_close = bar['price_close']
    
    if bars_count == 0:
        return None
    
    # Вычисляем процентное изменение
    change_pct = 0.0
    if price_open and price_open > 0:
        change_pct = ((price_close - price_open) / price_open) * 100
    
    # Нормализованный vDelta (независимый от масштаба объема)
    vdelta_ratio = (vdelta_sum / volume_sum) if volume_sum > 0 else 0.0
    
    result = {
        'volume': volume_sum,
        'vdelta': vdelta_sum,
        'vdelta_ratio': vdelta_ratio,
        'trades': trades_sum,
        'price_open': price_open,
        'price_close': price_close,
        'change_pct': change_pct,
        'bars_count': bars_count,
    }
    
    # Сохраняем в кеш (по 5-секундным интервалам)
    if symbol not in cache_dict:
        cache_dict[symbol] = {}
    cache_dict[symbol][timeframe] = {
        'cached_minute': current_5sec,
        'data': result,
    }
    
    return result


def get_bars_stats(market_type: str = 'spot'):
    """
    Получить статистику по загруженным 1m барам.
    Полезно для диагностики.
    """
    bars_dict = _spot_1m_bars if market_type == 'spot' else _futures_1m_bars
    
    stats = {}
    for symbol, bars in bars_dict.items():
        if bars:
            min_ts = min(bars.keys())
            max_ts = max(bars.keys())
            stats[symbol] = {
                'bars_count': len(bars),
                'oldest_bar_age_minutes': (datetime.now(timezone.utc).timestamp() * 1000 - min_ts) / 60000,
                'newest_bar_age_minutes': (datetime.now(timezone.utc).timestamp() * 1000 - max_ts) / 60000,
            }
    
    return stats


def clear_bars(market_type: str = 'spot'):
    """Очистка всех баров (для тестов или перезапуска)"""
    if market_type == 'spot':
        _spot_1m_bars.clear()
    else:
        _futures_1m_bars.clear()
    logger.info(f"Cleared all 1m bars for {market_type}")


async def load_historical_bars_from_rest(symbols: list, market_type: str = 'spot', hours_back: int = 24):
    """
    Загружает исторические 1m бары через aggTrades API Binance для точного vdelta.
    
    Используется при старте workers для заполнения истории.
    Обрабатывает aggTrades и создает 1m бары с правильным vdelta (buy - sell).
    
    Args:
        symbols: список символов для загрузки
        market_type: 'spot' или 'futures'
        hours_back: сколько часов истории загружать (по умолчанию 24)
    """
    import aiohttp
    import asyncio
    import time
    
    base_url = 'https://api.binance.com' if market_type == 'spot' else 'https://fapi.binance.com'
    endpoint = '/api/v3/aggTrades' if market_type == 'spot' else '/fapi/v1/aggTrades'
    
    # Временной диапазон
    end_time = int(time.time() * 1000)
    start_time = end_time - (hours_back * 60 * 60 * 1000)
    
    loaded_count = 0
    failed_count = 0
    
    logger.info(f"⬇️ Loading {hours_back}h history via aggTrades for {len(symbols)} {market_type} symbols...")
    
    # Ограничиваем параллелизм чтобы не словить rate limit
    semaphore = asyncio.Semaphore(10)
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for symbol in symbols:
            tasks.append(_load_symbol_aggtrades(session, base_url + endpoint, symbol, start_time, end_time, market_type, semaphore))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                failed_count += 1
                logger.debug(f"Failed to load: {result}")
            elif result:
                loaded_count += 1
    
    logger.info(f"✅ Loaded historical 1m bars for {loaded_count} symbols ({market_type}), failed: {failed_count}")


async def _load_symbol_aggtrades(session, url, symbol, start_time, end_time, market_type, semaphore):
    """Загружает aggTrades для символа и строит 1m бары с правильным vdelta"""
    import asyncio  # Import here for async operations
    
    async with semaphore:
        try:
            bars_dict = _spot_1m_bars if market_type == 'spot' else _futures_1m_bars
            
            if symbol not in bars_dict:
                bars_dict[symbol] = {}
            
            # Загружаем aggTrades порциями (limit=1000 за запрос)
            current_start = start_time
            total_trades = 0
            
            while current_start < end_time:
                params = {
                    'symbol': symbol,
                    'startTime': current_start,
                    'endTime': end_time,
                    'limit': 1000
                }
                
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to load aggTrades for {symbol}: HTTP {response.status}")
                        return False
                    
                    trades = await response.json()
                    
                    if not trades:
                        break
                    
                    # Обрабатываем каждую сделку и агрегируем в 1m бары
                    for trade in trades:
                        ts_ms = int(trade['T'])  # Transaction time
                        price = float(trade['p'])
                        qty = float(trade['q'])
                        quote_qty = float(trade.get('q', 0)) * price  # Volume in quote currency
                        is_buyer_maker = trade['m']  # true = sell (maker sold), false = buy (maker bought)
                        is_buy = not is_buyer_maker  # Инвертируем для правильного направления
                        
                        # Агрегируем в 1m бар
                        aggregate_trade_to_1m_bar(
                            symbol=symbol,
                            ts_ms=ts_ms,
                            quote_volume=quote_qty,
                            is_buy=is_buy,
                            price=price,
                            market_type=market_type
                        )
                        
                        total_trades += 1
                    
                    # Переходим к следующей порции
                    current_start = int(trades[-1]['T']) + 1
                    
                    # Защита от бесконечного цикла
                    if current_start <= int(trades[-1]['T']):
                        break
                
                # Rate limit protection
                await asyncio.sleep(0.1)
            
            bars_count = len(bars_dict.get(symbol, {}))
            if bars_count > 0:
                logger.info(f"✅ {symbol}: {total_trades} trades → {bars_count} 1m bars")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load aggTrades for {symbol}: {e}")
            return False


async def fill_missing_bars_from_klines(symbols: list, market_type: str = 'spot') -> int:
    """
    Заповнює пропущені 1m бари через Klines API якщо в Redis недостатньо даних.
    
    Klines API не дає точний vDelta (немає buy/sell інформації), але дозволяє:
    - Швидко отримати volume для 1500+ баров (25 годин)
    - Оцінити vDelta через формулу: (close - open) / (high - low) * volume
    
    Args:
        symbols: список символів
        market_type: 'spot' або 'futures'
    
    Returns:
        Кількість заповнених барів
    """
    import aiohttp
    import asyncio
    import time
    
    base_url = 'https://api.binance.com' if market_type == 'spot' else 'https://fapi.binance.com'
    endpoint = '/api/v3/klines' if market_type == 'spot' else '/fapi/v1/klines'
    
    bars_dict = _spot_1m_bars if market_type == 'spot' else _futures_1m_bars
    total_filled = 0
    
    logger.info(f"⬇️ Filling missing bars via Klines API for {len(symbols)} {market_type} symbols...")
    
    # Обмежуємо паралелізм
    semaphore = asyncio.Semaphore(20)
    
    async def fetch_klines(session, symbol):
        """Завантажує klines для одного символа"""
        nonlocal total_filled
        
        async with semaphore:
            try:
                # Перевіряємо скільки барів вже є
                existing_bars = len(bars_dict.get(symbol, {}))
                if existing_bars >= 1440:  # Вже є 24 години
                    return
                
                # Завантажуємо 1500 барів (25 годин)
                params = {
                    'symbol': symbol,
                    'interval': '1m',
                    'limit': 1500
                }
                
                async with session.get(f"{base_url}{endpoint}", params=params) as response:
                    if response.status != 200:
                        logger.debug(f"Klines API error for {symbol}: HTTP {response.status}")
                        return
                    
                    klines = await response.json()
                    
                    if not klines:
                        return
                    
                    if symbol not in bars_dict:
                        bars_dict[symbol] = {}
                    
                    filled = 0
                    for kline in klines:
                        # Kline format: [open_time, open, high, low, close, volume, close_time, quote_volume, trades, taker_buy_base, taker_buy_quote, ignore]
                        open_time_ms = int(kline[0])
                        ts_minute = (open_time_ms // 60000) * 60000  # Округлення до хвилини
                        
                        # Пропускаємо якщо бар вже існує (збираємо через WebSocket)
                        if ts_minute in bars_dict[symbol]:
                            continue
                        
                        open_price = float(kline[1])
                        high_price = float(kline[2])
                        low_price = float(kline[3])
                        close_price = float(kline[4])
                        quote_volume = float(kline[7])
                        taker_buy_quote = float(kline[10]) if len(kline) > 10 else quote_volume / 2
                        
                        # Розраховуємо vDelta: taker_buy_quote - (quote_volume - taker_buy_quote)
                        # = 2 * taker_buy_quote - quote_volume
                        vdelta = 2 * taker_buy_quote - quote_volume
                        
                        bar_data = {
                            'volume': quote_volume,
                            'vdelta': vdelta,
                            'trades': int(kline[8]) if len(kline) > 8 else 0,
                            'price_open': open_price,
                            'price_close': close_price,
                            'price_high': high_price,
                            'price_low': low_price,
                            'ts_minute': ts_minute,
                        }
                        
                        bars_dict[symbol][ts_minute] = bar_data
                        
                        # Зберігаємо в Redis
                        _save_bar_to_redis(symbol, ts_minute, bar_data, market_type)
                        filled += 1
                    
                    total_filled += filled
                    if filled > 0:
                        logger.debug(f"✅ {symbol}: filled {filled} bars via Klines API")
                
            except Exception as e:
                logger.debug(f"Error loading klines for {symbol}: {e}")
    
    # Запускаємо завантаження
    connector = aiohttp.TCPConnector(limit=50, limit_per_host=30, ttl_dns_cache=300)
    timeout = aiohttp.ClientTimeout(total=30, connect=10)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [fetch_klines(session, symbol) for symbol in symbols]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    logger.info(f"✅ Filled {total_filled} bars via Klines API for {market_type}")
    return total_filled