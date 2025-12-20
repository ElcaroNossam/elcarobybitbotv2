"""
Оптимизированный модуль для построения snapshot данных.

Централизует логику сборки snapshot для SPOT и FUTURES,
устраняя дублирование кода.
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Таймфреймы для показателей
TIMEFRAMES = ['1m', '3m', '5m', '15m', '30m', '1h', '4h', '8h', '1d']


def build_symbol_row(
    symbol: str,
    symbol_data: Dict[str, Any],
    market_type: str,
    get_tf_data_func,
    open_interest: float = 0.0,
) -> Optional[Dict[str, Any]]:
    """
    Построение данных одного символа для snapshot.
    
    Args:
        symbol: торговая пара
        symbol_data: данные из _spot_data или _futures_data
        market_type: 'spot' или 'futures'
        get_tf_data_func: функция для получения данных TF из aggregation_model
        open_interest: OI для futures (0 для spot)
    
    Returns:
        dict с данными символа или None если нет ticker
    """
    ticker = symbol_data.get('ticker', {})
    
    # Пропускаем без цены
    if not ticker or ticker.get('price', 0) == 0:
        return None
    
    price = ticker.get('price', 0)
    
    row = {
        'symbol': symbol,
        'price': price,
        'change_24h': ticker.get('change_24h', ticker.get('change', 0)),
        'volume_24h': ticker.get('quote_volume', 0),
    }
    
    # Данные специфичные для market type
    if market_type == 'futures':
        mark_price = symbol_data.get('markPrice', {})
        row['mark_price'] = mark_price.get('mark_price', price)
        row['funding_rate'] = mark_price.get('funding_rate', 0)
        row['open_interest'] = open_interest
    else:
        # Для spot используем volume как псевдо-OI
        row['open_interest'] = ticker.get('quote_volume', 0)
        row['funding_rate'] = 0.0
    
    # Получаем kline данные
    klines = symbol_data.get('kline', {})
    
    # Заполняем данные по таймфреймам
    for tf in TIMEFRAMES:
        # Сначала пробуем из aggregation model (vDelta)
        tf_data = get_tf_data_func(symbol, tf, market_type)
        
        if tf_data and tf_data.get('bars_count', 0) > 0:
            # Данные из aggregation model (приоритет)
            row[f'vdelta_{tf}'] = tf_data['vdelta']
            row[f'volume_{tf}'] = tf_data['volume']
            row[f'change_{tf}'] = tf_data['change_pct']
        else:
            # Fallback на kline
            kline = klines.get(tf, {})
            if kline:
                open_price = kline.get('open', 0)
                close_price = kline.get('close', 0)
                
                row[f'volume_{tf}'] = kline.get('quote_volume', 0)
                
                if open_price > 0:
                    row[f'change_{tf}'] = ((close_price - open_price) / open_price) * 100
                else:
                    row[f'change_{tf}'] = 0.0
            else:
                row[f'volume_{tf}'] = 0.0
                row[f'change_{tf}'] = 0.0
            
            # vDelta = 0 если нет данных из aggregation
            row[f'vdelta_{tf}'] = 0.0
        
        # Volatility из kline
        kline = klines.get(tf, {})
        if kline:
            open_price = kline.get('open', 0)
            high = kline.get('high', 0)
            low = kline.get('low', 0)
            
            if open_price > 0:
                row[f'volatility_{tf}'] = ((high - low) / open_price) * 100
            else:
                row[f'volatility_{tf}'] = 0.0
            
            row[f'ticks_{tf}'] = kline.get('trades', 0)
        else:
            row[f'volatility_{tf}'] = 0.0
            row[f'ticks_{tf}'] = 0
        
        # OI change (упрощенно - одинаковый для всех TF)
        row[f'oi_change_{tf}'] = 0.0
    
    # Timestamp
    row['timestamp'] = datetime.now(timezone.utc).isoformat()
    row['ts'] = row['timestamp']
    
    return row


def project_row_for_client(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Убирает лишние поля для отправки клиенту.
    Уменьшает размер payload.
    """
    # Оставляем только нужные поля
    keep_fields = {
        'symbol', 'price', 'mark_price', 'funding_rate', 'open_interest',
        'change_24h', 'volume_24h', 'timestamp', 'ts'
    }
    
    # Добавляем все TF поля
    for tf in TIMEFRAMES:
        keep_fields.add(f'vdelta_{tf}')
        keep_fields.add(f'volume_{tf}')
        keep_fields.add(f'change_{tf}')
        keep_fields.add(f'volatility_{tf}')
        keep_fields.add(f'ticks_{tf}')
        keep_fields.add(f'oi_change_{tf}')
    
    return {k: v for k, v in row.items() if k in keep_fields}
