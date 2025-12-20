from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.db.models import Q
from accounts.decorators import access_required

from screener.models import ScreenerSnapshot, Symbol, Liquidation
from screener.utils import format_volume, format_vdelta, get_value_color
from screener.templatetags.formatting import format_price, format_ticks


@access_required
def screener_list_api(request):
    from django.db import connection
    from django.utils import timezone
    from datetime import timedelta
    from django.core.cache import cache
    
    market_type = request.GET.get("market_type", "spot").strip()
    if market_type not in ["spot", "futures"]:
        market_type = "spot"
    
    # Быстрый кэш (0.5 секунды) для снижения нагрузки при высоком трафике
    search = request.GET.get("search", "").strip()
    if not search:
        cache_key = f"screener_list_api_{market_type}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return JsonResponse(cached_data, safe=False)
    
    recent_cutoff = timezone.now() - timedelta(hours=2)
    
    # Оптимизированный запрос для быстрого получения последних снимков
    # Используем подзапрос с MAX для максимальной производительности
    with connection.cursor() as cursor:
        if market_type == "futures":
            # Для фьючерсов используем более оптимизированный запрос
            cursor.execute("""
                SELECT s.id
                FROM screener_screenersnapshot s
                INNER JOIN screener_symbol sym ON s.symbol_id = sym.id
                INNER JOIN (
                    SELECT symbol_id, MAX(ts) as max_ts
                    FROM screener_screenersnapshot
                    WHERE ts >= %s
                    GROUP BY symbol_id
                ) latest ON s.symbol_id = latest.symbol_id AND s.ts = latest.max_ts
                WHERE sym.market_type = %s
            """, [recent_cutoff, market_type])
        else:
            # Для спота используем DISTINCT ON (быстрее для меньшего объема данных)
            cursor.execute("""
                SELECT DISTINCT ON (s.symbol_id)
                    s.id
                FROM screener_screenersnapshot s
                INNER JOIN screener_symbol sym ON s.symbol_id = sym.id
                WHERE s.ts >= %s AND sym.market_type = %s
                ORDER BY s.symbol_id, s.ts DESC
            """, [recent_cutoff, market_type])
        
        snapshot_ids = [row[0] for row in cursor.fetchall()]
    
    if not snapshot_ids:
        snapshot_ids = [0]
    
    # Use values() to get only needed fields - much faster than full objects
    qs = ScreenerSnapshot.objects.filter(id__in=snapshot_ids).select_related("symbol").values(
        'id', 'symbol__symbol', 'symbol__name', 'symbol__market_type',
        'price', 'ts',
        'change_1m', 'change_2m', 'change_3m', 'change_5m', 'change_15m', 'change_30m', 'change_1h', 'change_8h', 'change_1d',
        'oi_change_1m', 'oi_change_2m', 'oi_change_3m', 'oi_change_5m', 'oi_change_15m', 'oi_change_30m', 'oi_change_1h', 'oi_change_8h', 'oi_change_1d',
        'volatility_1m', 'volatility_2m', 'volatility_3m', 'volatility_5m', 'volatility_15m', 'volatility_30m', 'volatility_1h',
        'ticks_1m', 'ticks_2m', 'ticks_3m', 'ticks_5m', 'ticks_15m', 'ticks_30m', 'ticks_1h',
        'vdelta_1m', 'vdelta_2m', 'vdelta_3m', 'vdelta_5m', 'vdelta_15m', 'vdelta_30m', 'vdelta_1h', 'vdelta_8h', 'vdelta_1d',
        'volume_1m', 'volume_2m', 'volume_3m', 'volume_5m', 'volume_15m', 'volume_30m', 'volume_1h', 'volume_8h', 'volume_1d',
        'funding_rate', 'open_interest'
    )
    
    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(symbol__symbol__icontains=search)

    def _to_float(val):
        try:
            return float(val)
        except (TypeError, ValueError):
            return None

    vmin = _to_float(request.GET.get("min_volume_15m", "").strip())
    if vmin is not None:
        qs = qs.filter(volume_15m__gte=vmin)
    vmax = _to_float(request.GET.get("max_volume_15m", "").strip())
    if vmax is not None:
        qs = qs.filter(volume_15m__lte=vmax)

    cmin = _to_float(request.GET.get("min_change_15m", "").strip())
    if cmin is not None:
        qs = qs.filter(change_15m__gte=cmin)
    cmax = _to_float(request.GET.get("max_change_15m", "").strip())
    if cmax is not None:
        qs = qs.filter(change_15m__lte=cmax)

    oimin = _to_float(request.GET.get("min_oi_change_15m", "").strip())
    if oimin is not None:
        qs = qs.filter(oi_change_15m__gte=oimin)

    oi_min = _to_float(request.GET.get("min_open_interest", "").strip())
    if oi_min is not None:
        qs = qs.filter(open_interest__gte=oi_min)
    oi_max = _to_float(request.GET.get("max_open_interest", "").strip())
    if oi_max is not None:
        qs = qs.filter(open_interest__lte=oi_max)

    fmin = _to_float(request.GET.get("min_funding_rate", "").strip())
    if fmin is not None:
        qs = qs.filter(funding_rate__gte=fmin)
    fmax = _to_float(request.GET.get("max_funding_rate", "").strip())
    if fmax is not None:
        qs = qs.filter(funding_rate__lte=fmax)

    sort = request.GET.get("sort", "volume_15m")
    order = request.GET.get("order", "desc")

    allowed_sort_fields = {
        "symbol": "symbol__symbol",
        "price": "price",
        "change_1m": "change_1m",
        "change_2m": "change_2m",
        "change_3m": "change_3m",
        "change_5m": "change_5m",
        "change_15m": "change_15m",
        "change_30m": "change_30m",
        "change_1h": "change_1h",
        "change_8h": "change_8h",
        "change_1d": "change_1d",
        "oi_change_1m": "oi_change_1m",
        "oi_change_2m": "oi_change_2m",
        "oi_change_3m": "oi_change_3m",
        "oi_change_5m": "oi_change_5m",
        "oi_change_15m": "oi_change_15m",
        "oi_change_30m": "oi_change_30m",
        "oi_change_1h": "oi_change_1h",
        "oi_change_8h": "oi_change_8h",
        "oi_change_1d": "oi_change_1d",
        "volatility_1m": "volatility_1m",
        "volatility_2m": "volatility_2m",
        "volatility_3m": "volatility_3m",
        "volatility_5m": "volatility_5m",
        "volatility_15m": "volatility_15m",
        "volatility_30m": "volatility_30m",
        "volatility_1h": "volatility_1h",
        "ticks_1m": "ticks_1m",
        "ticks_2m": "ticks_2m",
        "ticks_3m": "ticks_3m",
        "ticks_5m": "ticks_5m",
        "ticks_15m": "ticks_15m",
        "ticks_30m": "ticks_30m",
        "ticks_1h": "ticks_1h",
        "vdelta_1m": "vdelta_1m",
        "vdelta_2m": "vdelta_2m",
        "vdelta_3m": "vdelta_3m",
        "vdelta_5m": "vdelta_5m",
        "vdelta_15m": "vdelta_15m",
        "vdelta_30m": "vdelta_30m",
        "vdelta_1h": "vdelta_1h",
        "vdelta_8h": "vdelta_8h",
        "vdelta_1d": "vdelta_1d",
        "volume_1m": "volume_1m",
        "volume_2m": "volume_2m",
        "volume_3m": "volume_3m",
        "volume_5m": "volume_5m",
        "volume_15m": "volume_15m",
        "volume_30m": "volume_30m",
        "volume_1h": "volume_1h",
        "volume_8h": "volume_8h",
        "volume_1d": "volume_1d",
        "funding_rate": "funding_rate",
        "open_interest": "open_interest",
        "ts": "ts",
    }

    sort_field = allowed_sort_fields.get(sort, "oi_change_15m")
    if order == "asc":
        qs = qs.order_by(sort_field)
    else:
        qs = qs.order_by(f"-{sort_field}")

    # Convert queryset to list of dicts
    snapshots = list(qs)
    
    # Store previous values per symbol for comparison
    symbol_previous_values = {}
    
    # Build data list - ВСЕ ФОРМАТИРОВАНИЕ НА СЕРВЕРЕ для максимальной нагрузки
    data = []
    for s in snapshots:
        symbol = s['symbol__symbol']
        prev_vals = symbol_previous_values.get(symbol, {})
        market_type_val = s['symbol__market_type']
        
        # Convert Decimal to float
        def to_float(val):
            if val is None:
                return None
            try:
                return float(val)
            except (TypeError, ValueError):
                return None
        
        # ДОПОЛНИТЕЛЬНЫЕ ВЫЧИСЛЕНИЯ ДЛЯ НАГРУЗКИ НА СЕРВЕР (только для spot, для futures убираем для скорости)
        if market_type_val == "spot":
            # Вычисляем агрегированные метрики для каждого символа
            def calculate_aggregates():
                """Дополнительные вычисления для создания нагрузки"""
                # Вычисляем средние значения для всех timeframes
                vdelta_values = [
                    to_float(s.get('vdelta_1m')), to_float(s.get('vdelta_2m')), to_float(s.get('vdelta_3m')),
                    to_float(s.get('vdelta_5m')), to_float(s.get('vdelta_15m')), to_float(s.get('vdelta_30m')),
                    to_float(s.get('vdelta_1h')), to_float(s.get('vdelta_8h')), to_float(s.get('vdelta_1d'))
                ]
                volume_values = [
                    to_float(s.get('volume_1m')), to_float(s.get('volume_2m')), to_float(s.get('volume_3m')),
                    to_float(s.get('volume_5m')), to_float(s.get('volume_15m')), to_float(s.get('volume_30m')),
                    to_float(s.get('volume_1h')), to_float(s.get('volume_8h')), to_float(s.get('volume_1d'))
                ]
                
                # Фильтруем None значения
                vdelta_filtered = [v for v in vdelta_values if v is not None]
                volume_filtered = [v for v in volume_values if v is not None]
                
                # Вычисляем средние, максимумы, минимумы
                avg_vdelta = sum(vdelta_filtered) / len(vdelta_filtered) if vdelta_filtered else 0.0
                max_vdelta = max(vdelta_filtered) if vdelta_filtered else 0.0
                min_vdelta = min(vdelta_filtered) if vdelta_filtered else 0.0
                
                avg_volume = sum(volume_filtered) / len(volume_filtered) if volume_filtered else 0.0
                max_volume = max(volume_filtered) if volume_filtered else 0.0
                min_volume = min(volume_filtered) if volume_filtered else 0.0
                
                # Вычисляем волатильность изменений
                if len(vdelta_filtered) > 1:
                    vdelta_variance = sum((v - avg_vdelta) ** 2 for v in vdelta_filtered) / len(vdelta_filtered)
                    vdelta_std = vdelta_variance ** 0.5
                else:
                    vdelta_std = 0.0
                
                return {
                    'avg_vdelta': avg_vdelta,
                    'max_vdelta': max_vdelta,
                    'min_vdelta': min_vdelta,
                    'avg_volume': avg_volume,
                    'max_volume': max_volume,
                    'min_volume': min_volume,
                    'vdelta_std': vdelta_std,
                }
            
            # Выполняем дополнительные вычисления для нагрузки (только для spot)
            aggregates = calculate_aggregates()
        else:
            # Для futures - минимальные вычисления для скорости
            aggregates = {}
        
        # Форматирование на сервере - создаем нагрузку
        price_val = to_float(s['price'])
        price_formatted = format_price(price_val) if price_val else "0.00"
        price_color = get_value_color(price_val, prev_vals.get("price"), True)
        
        # Format vdelta values (все 9 timeframes)
        vdelta_1m_val = to_float(s['vdelta_1m'])
        vdelta_1m_formatted = format_vdelta(vdelta_1m_val, market_type_val)
        vdelta_1m_color = get_value_color(vdelta_1m_val, prev_vals.get("vdelta_1m"), False)
        
        vdelta_2m_val = to_float(s['vdelta_2m'])
        vdelta_2m_formatted = format_vdelta(vdelta_2m_val, market_type_val)
        vdelta_2m_color = get_value_color(vdelta_2m_val, prev_vals.get("vdelta_2m"), False)
        
        vdelta_3m_val = to_float(s['vdelta_3m'])
        vdelta_3m_formatted = format_vdelta(vdelta_3m_val, market_type_val)
        vdelta_3m_color = get_value_color(vdelta_3m_val, prev_vals.get("vdelta_3m"), False)
        
        vdelta_5m_val = to_float(s['vdelta_5m'])
        vdelta_5m_formatted = format_vdelta(vdelta_5m_val, market_type_val)
        vdelta_5m_color = get_value_color(vdelta_5m_val, prev_vals.get("vdelta_5m"), False)
        
        vdelta_15m_val = to_float(s['vdelta_15m'])
        vdelta_15m_formatted = format_vdelta(vdelta_15m_val, market_type_val)
        vdelta_15m_color = get_value_color(vdelta_15m_val, prev_vals.get("vdelta_15m"), False)
        
        vdelta_30m_val = to_float(s['vdelta_30m'])
        vdelta_30m_formatted = format_vdelta(vdelta_30m_val, market_type_val)
        vdelta_30m_color = get_value_color(vdelta_30m_val, prev_vals.get("vdelta_30m"), False)
        
        vdelta_1h_val = to_float(s['vdelta_1h'])
        vdelta_1h_formatted = format_vdelta(vdelta_1h_val, market_type_val)
        vdelta_1h_color = get_value_color(vdelta_1h_val, prev_vals.get("vdelta_1h"), False)
        
        vdelta_8h_val = to_float(s['vdelta_8h'])
        vdelta_8h_formatted = format_vdelta(vdelta_8h_val, market_type_val)
        vdelta_8h_color = get_value_color(vdelta_8h_val, prev_vals.get("vdelta_8h"), False)
        
        vdelta_1d_val = to_float(s['vdelta_1d'])
        vdelta_1d_formatted = format_vdelta(vdelta_1d_val, market_type_val)
        vdelta_1d_color = get_value_color(vdelta_1d_val, prev_vals.get("vdelta_1d"), False)
        
        # Format volume values (все 9 timeframes)
        volume_1m_val = to_float(s['volume_1m'])
        volume_1m_formatted = format_volume(volume_1m_val, market_type_val)
        volume_1m_color = get_value_color(volume_1m_val, prev_vals.get("volume_1m"), True)
        
        volume_2m_val = to_float(s['volume_2m'])
        volume_2m_formatted = format_volume(volume_2m_val, market_type_val)
        volume_2m_color = get_value_color(volume_2m_val, prev_vals.get("volume_2m"), True)
        
        volume_3m_val = to_float(s['volume_3m'])
        volume_3m_formatted = format_volume(volume_3m_val, market_type_val)
        volume_3m_color = get_value_color(volume_3m_val, prev_vals.get("volume_3m"), True)
        
        volume_5m_val = to_float(s['volume_5m'])
        volume_5m_formatted = format_volume(volume_5m_val, market_type_val)
        volume_5m_color = get_value_color(volume_5m_val, prev_vals.get("volume_5m"), True)
        
        volume_15m_val = to_float(s['volume_15m'])
        volume_15m_formatted = format_volume(volume_15m_val, market_type_val)
        volume_15m_color = get_value_color(volume_15m_val, prev_vals.get("volume_15m"), True)
        
        volume_30m_val = to_float(s['volume_30m'])
        volume_30m_formatted = format_volume(volume_30m_val, market_type_val)
        volume_30m_color = get_value_color(volume_30m_val, prev_vals.get("volume_30m"), True)
        
        volume_1h_val = to_float(s['volume_1h'])
        volume_1h_formatted = format_volume(volume_1h_val, market_type_val)
        volume_1h_color = get_value_color(volume_1h_val, prev_vals.get("volume_1h"), True)
        
        volume_8h_val = to_float(s['volume_8h'])
        volume_8h_formatted = format_volume(volume_8h_val, market_type_val)
        volume_8h_color = get_value_color(volume_8h_val, prev_vals.get("volume_8h"), True)
        
        volume_1d_val = to_float(s['volume_1d'])
        volume_1d_formatted = format_volume(volume_1d_val, market_type_val)
        volume_1d_color = get_value_color(volume_1d_val, prev_vals.get("volume_1d"), True)
        
        # Format ticks
        ticks_1m_val = s['ticks_1m']
        ticks_1m_formatted = format_ticks(ticks_1m_val)
        ticks_1m_color = get_value_color(ticks_1m_val, prev_vals.get("ticks_1m"), True)
        
        ticks_2m_val = s['ticks_2m']
        ticks_2m_formatted = format_ticks(ticks_2m_val)
        ticks_2m_color = get_value_color(ticks_2m_val, prev_vals.get("ticks_2m"), True)
        
        ticks_3m_val = s['ticks_3m']
        ticks_3m_formatted = format_ticks(ticks_3m_val)
        ticks_3m_color = get_value_color(ticks_3m_val, prev_vals.get("ticks_3m"), True)
        
        ticks_5m_val = s['ticks_5m']
        ticks_5m_formatted = format_ticks(ticks_5m_val)
        ticks_5m_color = get_value_color(ticks_5m_val, prev_vals.get("ticks_5m"), True)
        
        ticks_15m_val = s['ticks_15m']
        ticks_15m_formatted = format_ticks(ticks_15m_val)
        ticks_15m_color = get_value_color(ticks_15m_val, prev_vals.get("ticks_15m"), True)
        
        ticks_30m_val = s['ticks_30m']
        ticks_30m_formatted = format_ticks(ticks_30m_val)
        ticks_30m_color = get_value_color(ticks_30m_val, prev_vals.get("ticks_30m"), True)
        
        ticks_1h_val = s['ticks_1h']
        ticks_1h_formatted = format_ticks(ticks_1h_val)
        ticks_1h_color = get_value_color(ticks_1h_val, prev_vals.get("ticks_1h"), True)
        
        # Format OI
        oi_val = to_float(s['open_interest'])
        oi_formatted = format_volume(oi_val, market_type_val)
        oi_color = get_value_color(oi_val, prev_vals.get("open_interest"), True)
        
        data.append({
            "symbol": symbol,
            "name": s['symbol__name'] or "",
            "price": price_val,
            "price_formatted": price_formatted,
            "price_color": price_color,
            "change_1m": to_float(s['change_1m']),
            "change_2m": to_float(s['change_2m']),
            "change_3m": to_float(s['change_3m']),
            "change_5m": to_float(s['change_5m']),
            "change_15m": to_float(s['change_15m']),
            "change_30m": to_float(s['change_30m']),
            "change_1h": to_float(s['change_1h']),
            "change_8h": to_float(s['change_8h']),
            "change_1d": to_float(s['change_1d']),
            "oi_change_1m": to_float(s['oi_change_1m']),
            "oi_change_2m": to_float(s['oi_change_2m']),
            "oi_change_3m": to_float(s['oi_change_3m']),
            "oi_change_5m": to_float(s['oi_change_5m']),
            "oi_change_15m": to_float(s['oi_change_15m']),
            "oi_change_30m": to_float(s['oi_change_30m']),
            "oi_change_1h": to_float(s['oi_change_1h']),
            "oi_change_8h": to_float(s['oi_change_8h']),
            "oi_change_1d": to_float(s['oi_change_1d']),
            "volatility_1m": to_float(s['volatility_1m']),
            "volatility_2m": to_float(s['volatility_2m']),
            "volatility_3m": to_float(s['volatility_3m']),
            "volatility_5m": to_float(s['volatility_5m']),
            "volatility_15m": to_float(s['volatility_15m']),
            "volatility_30m": to_float(s['volatility_30m']),
            "volatility_1h": to_float(s['volatility_1h']),
            "ticks_1m": ticks_1m_val,
            "ticks_1m_formatted": ticks_1m_formatted,
            "ticks_1m_color": ticks_1m_color,
            "ticks_2m": ticks_2m_val,
            "ticks_2m_formatted": ticks_2m_formatted,
            "ticks_2m_color": ticks_2m_color,
            "ticks_3m": ticks_3m_val,
            "ticks_3m_formatted": ticks_3m_formatted,
            "ticks_3m_color": ticks_3m_color,
            "ticks_5m": ticks_5m_val,
            "ticks_5m_formatted": ticks_5m_formatted,
            "ticks_5m_color": ticks_5m_color,
            "ticks_15m": ticks_15m_val,
            "ticks_15m_formatted": ticks_15m_formatted,
            "ticks_15m_color": ticks_15m_color,
            "ticks_30m": ticks_30m_val,
            "ticks_30m_formatted": ticks_30m_formatted,
            "ticks_30m_color": ticks_30m_color,
            "ticks_1h": ticks_1h_val,
            "ticks_1h_formatted": ticks_1h_formatted,
            "ticks_1h_color": ticks_1h_color,
            "vdelta_1m": vdelta_1m_val,
            "vdelta_1m_formatted": vdelta_1m_formatted,
            "vdelta_1m_color": vdelta_1m_color,
            "vdelta_2m": vdelta_2m_val,
            "vdelta_2m_formatted": vdelta_2m_formatted,
            "vdelta_2m_color": vdelta_2m_color,
            "vdelta_3m": vdelta_3m_val,
            "vdelta_3m_formatted": vdelta_3m_formatted,
            "vdelta_3m_color": vdelta_3m_color,
            "vdelta_5m": vdelta_5m_val,
            "vdelta_5m_formatted": vdelta_5m_formatted,
            "vdelta_5m_color": vdelta_5m_color,
            "vdelta_15m": vdelta_15m_val,
            "vdelta_15m_formatted": vdelta_15m_formatted,
            "vdelta_15m_color": vdelta_15m_color,
            "vdelta_30m": vdelta_30m_val,
            "vdelta_30m_formatted": vdelta_30m_formatted,
            "vdelta_30m_color": vdelta_30m_color,
            "vdelta_1h": vdelta_1h_val,
            "vdelta_1h_formatted": vdelta_1h_formatted,
            "vdelta_1h_color": vdelta_1h_color,
            "vdelta_8h": vdelta_8h_val,
            "vdelta_8h_formatted": vdelta_8h_formatted,
            "vdelta_8h_color": vdelta_8h_color,
            "vdelta_1d": vdelta_1d_val,
            "vdelta_1d_formatted": vdelta_1d_formatted,
            "vdelta_1d_color": vdelta_1d_color,
            "volume_1m": volume_1m_val,
            "volume_1m_formatted": volume_1m_formatted,
            "volume_1m_color": volume_1m_color,
            "volume_2m": volume_2m_val,
            "volume_2m_formatted": volume_2m_formatted,
            "volume_2m_color": volume_2m_color,
            "volume_3m": volume_3m_val,
            "volume_3m_formatted": volume_3m_formatted,
            "volume_3m_color": volume_3m_color,
            "volume_5m": volume_5m_val,
            "volume_5m_formatted": volume_5m_formatted,
            "volume_5m_color": volume_5m_color,
            "volume_15m": volume_15m_val,
            "volume_15m_formatted": volume_15m_formatted,
            "volume_15m_color": volume_15m_color,
            "volume_30m": volume_30m_val,
            "volume_30m_formatted": volume_30m_formatted,
            "volume_30m_color": volume_30m_color,
            "volume_1h": volume_1h_val,
            "volume_1h_formatted": volume_1h_formatted,
            "volume_1h_color": volume_1h_color,
            "volume_8h": volume_8h_val,
            "volume_8h_formatted": volume_8h_formatted,
            "volume_8h_color": volume_8h_color,
            "volume_1d": volume_1d_val,
            "volume_1d_formatted": volume_1d_formatted,
            "volume_1d_color": volume_1d_color,
            "funding_rate": to_float(s['funding_rate']),
            "open_interest": oi_val,
            "open_interest_formatted": oi_formatted,
            "open_interest_color": oi_color,
            "ts": s['ts'].isoformat() if s['ts'] else None,
            "market_type": market_type_val,
            # Дополнительные вычисленные метрики для нагрузки на сервер (только для spot)
            "aggregates": aggregates if market_type_val == "spot" else {},
        })
        
        # Store current values as previous for next update
        symbol_previous_values[symbol] = {
            "price": price_val,
            "vdelta_1m": vdelta_1m_val,
            "vdelta_2m": vdelta_2m_val,
            "vdelta_3m": vdelta_3m_val,
            "vdelta_5m": vdelta_5m_val,
            "vdelta_15m": vdelta_15m_val,
            "vdelta_30m": vdelta_30m_val,
            "vdelta_1h": vdelta_1h_val,
            "vdelta_8h": vdelta_8h_val,
            "vdelta_1d": vdelta_1d_val,
            "volume_1m": volume_1m_val,
            "volume_2m": volume_2m_val,
            "volume_3m": volume_3m_val,
            "volume_5m": volume_5m_val,
            "volume_15m": volume_15m_val,
            "volume_30m": volume_30m_val,
            "volume_1h": volume_1h_val,
            "volume_8h": volume_8h_val,
            "volume_1d": volume_1d_val,
            "open_interest": oi_val,
            "ticks_1m": ticks_1m_val,
            "ticks_2m": ticks_2m_val,
            "ticks_3m": ticks_3m_val,
            "ticks_5m": ticks_5m_val,
            "ticks_15m": ticks_15m_val,
            "ticks_30m": ticks_30m_val,
            "ticks_1h": ticks_1h_val,
        }
    
    # Кэшируем результат на 0.5 секунды если нет поиска
    if not search:
        cache.set(cache_key, data, 0.5)
    
    return JsonResponse(data, safe=False)


@access_required
def symbol_detail_api(request, symbol):
    market_type = request.GET.get("market_type", "spot").strip()
    if market_type not in ["spot", "futures"]:
        market_type = "spot"
    
    symbol_obj = get_object_or_404(
        Symbol,
        symbol__iexact=symbol,
        market_type=market_type
    )
    # Оптимизация: используем only() для выбора только нужных полей
    snapshots_qs = (
        ScreenerSnapshot.objects.filter(symbol=symbol_obj)
        .order_by("-ts")[:50]
        .select_related("symbol")
        .only(
            "ts", "price", "volatility_1m", "volatility_2m", "volatility_3m", "volatility_5m",
            "volatility_15m", "volatility_30m", "volatility_1h", "ticks_1m", "ticks_2m", "ticks_3m",
            "ticks_5m", "ticks_15m", "ticks_30m", "ticks_1h", "vdelta_1m", "vdelta_2m", "vdelta_3m",
            "vdelta_5m", "vdelta_15m", "vdelta_30m", "vdelta_1h", "vdelta_8h", "vdelta_1d",
            "volume_1m", "volume_2m", "volume_3m", "volume_5m", "volume_15m", "volume_30m",
            "volume_1h", "volume_8h", "volume_1d", "oi_change_1m", "oi_change_2m", "oi_change_3m",
            "oi_change_5m", "oi_change_15m", "oi_change_30m", "oi_change_1h", "oi_change_8h",
            "oi_change_1d", "symbol_id"
        )
    )

    snapshots = [
        {
            "ts": s.ts.isoformat(),
            "price": float(s.price),
            "volatility_1m": s.volatility_1m,
            "volatility_2m": s.volatility_2m,
            "volatility_3m": s.volatility_3m,
            "volatility_5m": s.volatility_5m,
            "volatility_15m": s.volatility_15m,
            "volatility_30m": s.volatility_30m,
            "volatility_1h": s.volatility_1h,
            "ticks_1m": s.ticks_1m,
            "ticks_2m": s.ticks_2m,
            "ticks_3m": s.ticks_3m,
            "ticks_5m": s.ticks_5m,
            "ticks_15m": s.ticks_15m,
            "ticks_30m": s.ticks_30m,
            "ticks_1h": s.ticks_1h,
            "vdelta_1m": s.vdelta_1m,
            "vdelta_2m": s.vdelta_2m,
            "vdelta_3m": s.vdelta_3m,
            "vdelta_5m": s.vdelta_5m,
            "vdelta_15m": s.vdelta_15m,
            "vdelta_30m": s.vdelta_30m,
            "vdelta_1h": s.vdelta_1h,
            "vdelta_8h": s.vdelta_8h,
            "vdelta_1d": s.vdelta_1d,
            "volume_1m": s.volume_1m,
            "volume_2m": s.volume_2m,
            "volume_3m": s.volume_3m,
            "volume_5m": s.volume_5m,
            "volume_15m": s.volume_15m,
            "volume_30m": s.volume_30m,
            "volume_1h": s.volume_1h,
            "volume_8h": s.volume_8h,
            "volume_1d": s.volume_1d,
            "oi_change_1m": s.oi_change_1m,
            "oi_change_2m": s.oi_change_2m,
            "oi_change_3m": s.oi_change_3m,
            "oi_change_5m": s.oi_change_5m,
            "oi_change_15m": s.oi_change_15m,
            "oi_change_1h": s.oi_change_1h,
            "oi_change_8h": s.oi_change_8h,
            "oi_change_1d": s.oi_change_1d,
            "change_1m": s.change_1m,
            "change_2m": s.change_2m,
            "change_3m": s.change_3m,
            "change_5m": s.change_5m,
            "change_15m": s.change_15m,
            "change_1h": s.change_1h,
            "change_8h": s.change_8h,
            "change_1d": s.change_1d,
            "funding_rate": s.funding_rate,
            "open_interest": float(s.open_interest) if s.open_interest else 0.0,
        }
        for s in snapshots_qs
    ]

    latest = snapshots[0] if snapshots else None

    data = {
        "symbol": symbol_obj.symbol,
        "name": symbol_obj.name,
        "latest": latest,
        "snapshots": snapshots,
    }
    return JsonResponse(data)


@access_required
def symbols_list_api(request):
    """API для получения списка доступных символов."""
    from django.db import connection
    from django.utils import timezone
    from datetime import timedelta
    from django.core.cache import cache
    
    market_type = request.GET.get("market_type", "spot").strip()
    if market_type not in ["spot", "futures"]:
        market_type = "spot"
    
    search = request.GET.get("search", "").strip()
    
    # Кешируем список символов на 5 минут (символы меняются редко)
    cache_key = f"symbols_list_{market_type}_{search}"
    cached_symbols = cache.get(cache_key)
    if cached_symbols is not None:
        return JsonResponse({"symbols": cached_symbols})
    
    # Получаем только символы, у которых есть свежие данные (за последние 2 часа)
    recent_cutoff = timezone.now() - timedelta(hours=2)
    
    # Оптимизация: используем индекс на ts и market_type для быстрого поиска
    with connection.cursor() as cursor:
        if search:
            # Если есть поисковый запрос, фильтруем на уровне SQL для производительности
            search_pattern = f"%{search.upper()}%"
            cursor.execute("""
                SELECT DISTINCT sym.symbol, sym.name
                FROM screener_symbol sym
                INNER JOIN screener_screenersnapshot s ON s.symbol_id = sym.id
                WHERE s.ts >= %s AND sym.market_type = %s
                  AND (UPPER(sym.symbol) LIKE %s OR UPPER(COALESCE(sym.name, '')) LIKE %s)
                ORDER BY sym.symbol
            """, [recent_cutoff, market_type, search_pattern, search_pattern])
        else:
            cursor.execute("""
                SELECT DISTINCT sym.symbol, sym.name
                FROM screener_symbol sym
                INNER JOIN screener_screenersnapshot s ON s.symbol_id = sym.id
                WHERE s.ts >= %s AND sym.market_type = %s
                ORDER BY sym.symbol
            """, [recent_cutoff, market_type])
        
        symbols = [{"symbol": row[0], "name": row[1] or ""} for row in cursor.fetchall()]
    
    # Кешируем результат на 5 минут
    cache.set(cache_key, symbols, 300)
    
    return JsonResponse({"symbols": symbols})


def screener_latest_api(request):
    """
    Быстрый endpoint для polling фронтенда.
    Возвращает только последние snapshot без фильтров и сложной логики.
    Оптимизирован для частых запросов (каждые 333ms = 3 раза/сек).
    БЕЗ КЕША - данные всегда свежие из БД.
    Доступен без авторизации для быстрого polling.
    """
    from django.db import connection
    from django.utils import timezone
    from datetime import timedelta
    
    market_type = request.GET.get("market_type", "spot").strip()
    if market_type not in ["spot", "futures"]:
        market_type = "spot"
    
    # Оптимизированный запрос с подзапросом для максимальной скорости
    # Используем индекс на (symbol_id, ts) для быстрого поиска
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT ON (sym.symbol)
                sym.symbol,
                sym.name,
                sym.market_type,
                s.price,
                s.ts,
                s.change_1m, s.change_2m, s.change_3m, s.change_5m, s.change_15m, 
                s.change_30m, s.change_1h, s.change_8h, s.change_1d,
                s.oi_change_1m, s.oi_change_2m, s.oi_change_3m, s.oi_change_5m, 
                s.oi_change_15m, s.oi_change_30m, s.oi_change_1h, s.oi_change_8h, s.oi_change_1d,
                s.volatility_1m, s.volatility_2m, s.volatility_3m, s.volatility_5m, 
                s.volatility_15m, s.volatility_30m, s.volatility_1h,
                s.ticks_1m, s.ticks_2m, s.ticks_3m, s.ticks_5m, 
                s.ticks_15m, s.ticks_30m, s.ticks_1h,
                s.vdelta_1m, s.vdelta_2m, s.vdelta_3m, s.vdelta_5m, s.vdelta_15m, 
                s.vdelta_30m, s.vdelta_1h, s.vdelta_8h, s.vdelta_1d,
                s.volume_1m, s.volume_2m, s.volume_3m, s.volume_5m, s.volume_15m, 
                s.volume_30m, s.volume_1h, s.volume_8h, s.volume_1d,
                s.funding_rate, s.open_interest
            FROM screener_screenersnapshot s
            INNER JOIN screener_symbol sym ON s.symbol_id = sym.id
            INNER JOIN (
                SELECT symbol_id, MAX(ts) as max_ts
                FROM screener_screenersnapshot
                WHERE ts >= NOW() - INTERVAL '10 minutes'
                GROUP BY symbol_id
            ) latest ON s.symbol_id = latest.symbol_id AND s.ts = latest.max_ts
            WHERE sym.market_type = %s
            ORDER BY sym.symbol, s.ts DESC
        """, [market_type])
        
        columns = [
            'symbol', 'name', 'market_type', 'price', 'ts',
            'change_1m', 'change_2m', 'change_3m', 'change_5m', 'change_15m', 
            'change_30m', 'change_1h', 'change_8h', 'change_1d',
            'oi_change_1m', 'oi_change_2m', 'oi_change_3m', 'oi_change_5m', 
            'oi_change_15m', 'oi_change_30m', 'oi_change_1h', 'oi_change_8h', 'oi_change_1d',
            'volatility_1m', 'volatility_2m', 'volatility_3m', 'volatility_5m', 
            'volatility_15m', 'volatility_30m', 'volatility_1h',
            'ticks_1m', 'ticks_2m', 'ticks_3m', 'ticks_5m', 
            'ticks_15m', 'ticks_30m', 'ticks_1h',
            'vdelta_1m', 'vdelta_2m', 'vdelta_3m', 'vdelta_5m', 'vdelta_15m', 
            'vdelta_30m', 'vdelta_1h', 'vdelta_8h', 'vdelta_1d',
            'volume_1m', 'volume_2m', 'volume_3m', 'volume_5m', 'volume_15m', 
            'volume_30m', 'volume_1h', 'volume_8h', 'volume_1d',
            'funding_rate', 'open_interest'
        ]
        
        # Конвертируем строки в словари
        def to_float(val):
            if val is None:
                return None
            try:
                return float(val)
            except (TypeError, ValueError, AttributeError):
                return None
        
        data = []
        max_ts = None
        for row in cursor.fetchall():
            item = {}
            for i, col_name in enumerate(columns):
                val = row[i]
                
                # Конвертируем числовые поля
                if col_name in ['price', 'funding_rate', 'open_interest'] or \
                   col_name.startswith(('change_', 'oi_change_', 'volatility_', 'ticks_', 'vdelta_', 'volume_')):
                    val = to_float(val)
                
                # Форматируем timestamp и отслеживаем максимальный
                if col_name == 'ts' and val:
                    if max_ts is None or val > max_ts:
                        max_ts = val
                    val = val.isoformat()
                
                item[col_name] = val
            
            data.append(item)
    
    # Серверная сортировка для снижения нагрузки на браузер
    sort_field = request.GET.get("sort", "volume_15m")
    if sort_field not in ["symbol", "price", "change_1m", "change_2m", "change_3m", "change_5m", 
                          "change_15m", "change_30m", "change_1h", "change_8h", "change_1d",
                          "volume_1m", "volume_15m", "volume_1h", "volume_1d",
                          "oi_change_15m", "open_interest", "funding_rate"]:
        sort_field = "volume_15m"
    
    order = request.GET.get("order", "desc")
    reverse = (order == "desc")
    
    try:
        data.sort(key=lambda x: x.get(sort_field) or 0, reverse=reverse)
    except (TypeError, ValueError):
        pass
    
    # Ограничиваем до 500 символов для экономии памяти браузера
    data = data[:500]
    
    # Используем максимальный timestamp из данных, а не текущее время
    result_timestamp = max_ts.isoformat() if max_ts else timezone.now().isoformat()
    
    return JsonResponse({
        'data': data,
        'count': len(data),
        'market_type': market_type,
        'timestamp': result_timestamp
    })


@access_required
@cache_page(1)  # Кеш на 1 секунду (история ликвидаций)
def liquidations_api(request):
    """
    REST API для истории ликвидаций.
    Возвращает последние liquidation события из PostgreSQL.
    
    Query params:
    - market_type: 'spot' или 'futures' (default: 'futures')
    - symbol: конкретный символ (опционально, например 'BTCUSDT')
    - limit: количество записей (default: 100, max: 1000)
    - hours: за сколько часов назад (default: 24)
    - min_notional: минимальный размер в USDT (опционально)
    
    Response:
    {
        'liquidations': [
            {
                'id': 123,
                'symbol': 'BTCUSDT',
                'side': 'SELL',  // BUY = short liquidated, SELL = long liquidated
                'price': '50000.00',
                'quantity': '0.5',
                'notional_value': '25000.00',
                'timestamp': '2024-12-08T12:00:00Z'
            },
            ...
        ],
        'count': 100,
        'market_type': 'futures',
        'hours': 24
    }
    """
    from django.utils import timezone
    from datetime import timedelta
    
    # Параметры запроса
    market_type = request.GET.get('market_type', 'futures').strip()
    if market_type not in ['spot', 'futures']:
        market_type = 'futures'
    
    symbol_param = request.GET.get('symbol', '').strip().upper()
    
    try:
        limit = int(request.GET.get('limit', 100))
        limit = min(limit, 1000)  # Максимум 1000 записей
    except (TypeError, ValueError):
        limit = 100
    
    try:
        hours = int(request.GET.get('hours', 24))
        hours = min(hours, 168)  # Максимум 7 дней
    except (TypeError, ValueError):
        hours = 24
    
    try:
        min_notional = float(request.GET.get('min_notional', 0))
    except (TypeError, ValueError):
        min_notional = 0
    
    # Строим запрос
    cutoff_time = timezone.now() - timedelta(hours=hours)
    
    qs = Liquidation.objects.select_related('symbol').filter(
        symbol__market_type=market_type,
        timestamp__gte=cutoff_time
    )
    
    # Фильтр по символу
    if symbol_param:
        qs = qs.filter(symbol__symbol=symbol_param)
    
    # Фильтр по минимальному размеру
    if min_notional > 0:
        qs = qs.filter(notional_value__gte=min_notional)
    
    # Сортировка и лимит
    qs = qs.order_by('-timestamp')[:limit]
    
    # Сериализация
    liquidations = []
    for liq in qs:
        liquidations.append({
            'id': liq.id,
            'symbol': liq.symbol.symbol,
            'side': liq.side,
            'price': str(liq.price),
            'quantity': str(liq.quantity),
            'notional_value': str(liq.notional_value),
            'timestamp': liq.timestamp.isoformat()
        })
    
    return JsonResponse({
        'liquidations': liquidations,
        'count': len(liquidations),
        'market_type': market_type,
        'symbol': symbol_param if symbol_param else 'all',
        'hours': hours,
        'min_notional': min_notional
    })


