"""
Server-side formatters for screener data.
Moves formatting logic from browser to server for better performance.
"""
from decimal import Decimal


def format_price(value):
    """Format price with appropriate decimals."""
    if value is None:
        return "0.00"
    v = float(value)
    if v == 0:
        return "0.00"
    if abs(v) >= 1000:
        return f"{v:,.2f}"
    elif abs(v) >= 1:
        return f"{v:.4f}"
    elif abs(v) >= 0.0001:
        return f"{v:.6f}"
    else:
        return f"{v:.8f}"


def format_volume(value, market_type='spot'):
    """Format volume with K/M/B suffixes."""
    if value is None:
        return "0"
    v = abs(float(value))
    if v == 0:
        return "0"
    
    # Для фьючерсов используем полные цифры до 10K
    threshold = 10000 if market_type == 'futures' else 1000
    
    if v >= 1_000_000_000:
        return f"{v/1_000_000_000:.2f}B"
    elif v >= 1_000_000:
        return f"{v/1_000_000:.2f}M"
    elif v >= threshold:
        return f"{v/1000:.2f}K"
    else:
        return f"{v:.2f}"


def format_vdelta(value, market_type='spot'):
    """Format vdelta with sign and K/M/B suffixes."""
    if value is None:
        return "0"
    v = float(value)
    if v == 0:
        return "0"
    
    sign = "+" if v > 0 else ""
    abs_v = abs(v)
    
    # Для фьючерсов используем полные цифры до 10K
    threshold = 10000 if market_type == 'futures' else 1000
    
    if abs_v >= 1_000_000_000:
        return f"{sign}{v/1_000_000_000:.2f}B"
    elif abs_v >= 1_000_000:
        return f"{sign}{v/1_000_000:.2f}M"
    elif abs_v >= threshold:
        return f"{sign}{v/1000:.2f}K"
    else:
        return f"{sign}{v:.2f}"


def format_percentage(value):
    """Format percentage with + sign for positive values."""
    if value is None:
        return "0.00%"
    v = float(value)
    sign = "+" if v > 0 else ""
    return f"{sign}{v:.2f}%"


def format_integer(value):
    """Format integer with K/M/B suffixes."""
    if value is None:
        return "0"
    v = abs(float(value))
    if v == 0:
        return "0"
    
    if v >= 1_000_000_000:
        return f"{v/1_000_000_000:.1f}B"
    elif v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    elif v >= 1000:
        return f"{v/1000:.1f}K"
    else:
        return f"{int(v)}"


def format_snapshot_data(snapshot, market_type='spot'):
    """
    Format snapshot data on server side.
    Returns dictionary with formatted values ready for display.
    """
    if not snapshot:
        return {}
    
    # Базовые данные
    data = {
        'symbol': snapshot.symbol.symbol,
        'price': format_price(snapshot.price),
        'ts': snapshot.ts.isoformat() if snapshot.ts else None,
    }
    
    # Форматируем все таймфреймы
    timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
    
    for tf in timeframes:
        # Volume
        volume_field = f'volume_{tf}'
        if hasattr(snapshot, volume_field):
            data[volume_field] = format_volume(getattr(snapshot, volume_field), market_type)
        
        # Vdelta
        vdelta_field = f'vdelta_{tf}'
        if hasattr(snapshot, vdelta_field):
            data[vdelta_field] = format_vdelta(getattr(snapshot, vdelta_field), market_type)
        
        # Change (percentage)
        change_field = f'change_{tf}'
        if hasattr(snapshot, change_field):
            data[change_field] = format_percentage(getattr(snapshot, change_field))
        
        # OI Change (percentage) - только логичные TF
        if tf in ['5m', '15m', '1h', '4h']:
            oi_field = f'oi_change_{tf}'
            if hasattr(snapshot, oi_field):
                data[oi_field] = format_percentage(getattr(snapshot, oi_field))
    
    # Volatility - только логичные TF
    for tf in ['5m', '15m', '1h']:
        volatility_field = f'volatility_{tf}'
        if hasattr(snapshot, volatility_field):
            data[volatility_field] = format_percentage(getattr(snapshot, volatility_field))
    
    # Ticks - только логичные TF
    for tf in ['1m', '5m', '15m']:
        ticks_field = f'ticks_{tf}'
        if hasattr(snapshot, ticks_field):
            data[ticks_field] = format_integer(getattr(snapshot, ticks_field))
    
    # Funding rate и Open Interest (только для futures)
    if market_type == 'futures':
        if hasattr(snapshot, 'funding_rate') and snapshot.funding_rate is not None:
            data['funding_rate'] = format_percentage(snapshot.funding_rate)
        if hasattr(snapshot, 'open_interest') and snapshot.open_interest is not None:
            data['open_interest'] = format_volume(snapshot.open_interest, market_type)
    
    # Добавляем сырые значения для сортировки (с префиксом _raw)
    data['_raw_price'] = float(snapshot.price) if snapshot.price else 0
    
    for tf in timeframes:
        volume_field = f'volume_{tf}'
        if hasattr(snapshot, volume_field):
            val = getattr(snapshot, volume_field)
            data[f'_raw_{volume_field}'] = float(val) if val is not None else 0
        
        vdelta_field = f'vdelta_{tf}'
        if hasattr(snapshot, vdelta_field):
            val = getattr(snapshot, vdelta_field)
            data[f'_raw_{vdelta_field}'] = float(val) if val is not None else 0
        
        change_field = f'change_{tf}'
        if hasattr(snapshot, change_field):
            val = getattr(snapshot, change_field)
            data[f'_raw_{change_field}'] = float(val) if val is not None else 0
    
    return data
