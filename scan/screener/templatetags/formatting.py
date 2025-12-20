"""
Template filters for formatting numeric values, especially prices and volumes.
"""
from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()


@register.filter
def format_price(value):
    """
    Adaptive price formatting with commas as thousand separators (no suffixes):
    - >= 1: 2 decimal places with commas (e.g., 51,234.56)
    - 0.01 <= price < 1: 4 decimal places (e.g., 0.1234)
    - price < 0.01: 8 decimal places (e.g., 0.00001234)
    """
    if value is None:
        return ""

    try:
        if isinstance(value, Decimal):
            v = float(value)
        else:
            v = float(value)
    except (ValueError, TypeError, InvalidOperation):
        return str(value)

    abs_v = abs(v)

    # Adaptive decimal places with commas for large values
    if abs_v >= 1:
        return f"{v:,.2f}"
    elif abs_v >= 0.01:
        return f"{v:.4f}"
    else:
        return f"{v:.8f}"


@register.filter
def format_volume(value, market_type=None):
    """
    Format volume with commas as thousand separators and $ symbol:
    - Shows exact value without rounding (e.g., $1,234,567.89123456)
    - All decimal places preserved
    """
    if value is None:
        return ""

    try:
        if isinstance(value, Decimal):
            # Use Decimal directly to preserve precision
            d = value
        else:
            d = Decimal(str(value))
    except (ValueError, TypeError, InvalidOperation):
        return "0$"

    if d == 0:
        return "0$"
    
    # Format with commas as thousand separators, preserving all decimal places
    # Handle negative numbers properly (put minus before number, $ at the end)
    is_negative = d < 0
    if is_negative:
        d = abs(d)
    
    # Remove trailing zeros but keep decimal point if needed
    s = f"{d:,}"
    # Remove trailing zeros after decimal point
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    
    return f"-{s}$" if is_negative else f"{s}$"


@register.filter
def format_vdelta(value, market_type=None):
    """
    Format volume delta with commas as thousand separators and $ symbol.
    - Shows exact value without rounding (e.g., $1,234,567.89123456)
    - All decimal places preserved
    Works the same for spot and futures (vdelta is always in USDT).
    """
    if value is None:
        return ""

    try:
        if isinstance(value, Decimal):
            # Use Decimal directly to preserve precision
            d = value
        else:
            d = Decimal(str(value))
    except (ValueError, TypeError, InvalidOperation):
        # Handle any invalid decimal conversion
        return "0$"

    if d == 0:
        return "0$"
    
    # Format with commas as thousand separators, preserving all decimal places
    # Handle negative numbers properly (put minus before number, $ at the end)
    is_negative = d < 0
    if is_negative:
        d = abs(d)
    
    # Remove trailing zeros but keep decimal point if needed
    s = f"{d:,}"
    # Remove trailing zeros after decimal point
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    
    return f"-{s}$" if is_negative else f"{s}$"


@register.filter
def format_percentage(value, decimals=2):
    """
    Format percentage with specified decimal places.
    """
    if value is None:
        return ""

    try:
        if isinstance(value, Decimal):
            v = float(value)
        else:
            v = float(value)
    except (ValueError, TypeError, InvalidOperation):
        return str(value)

    return f"{v:.{decimals}f}"


@register.filter
def format_volatility(value):
    """
    Format volatility with smart rounding:
    - >= 1: 2 decimals
    - < 1: 3 decimals
    """
    if value is None:
        return ""

    try:
        if isinstance(value, Decimal):
            v = float(value)
        else:
            v = float(value)
    except (ValueError, TypeError, InvalidOperation):
        return str(value)

    abs_v = abs(v)

    if abs_v >= 1:
        return f"{v:.2f}"
    else:
        return f"{v:.3f}"


@register.filter
def format_oi_change(value):
    """
    Format OI change percentage with smart rounding:
    - >= 1: 2 decimals
    - >= 0.1: 3 decimals
    - >= 0.001: 4 decimals
    - < 0.001: 6 decimals (to show very small negative values)
    """
    if value is None:
        return ""

    try:
        if isinstance(value, Decimal):
            v = float(value)
        else:
            v = float(value)
    except (ValueError, TypeError, InvalidOperation):
        return str(value)

    abs_v = abs(v)

    if abs_v >= 1:
        return f"{v:.2f}"
    elif abs_v >= 0.1:
        return f"{v:.3f}"
    elif abs_v >= 0.001:
        return f"{v:.4f}"
    else:
        # For very small values, show more decimals to distinguish from zero
        return f"{v:.6f}"


@register.filter
def format_ticks(value):
    """
    Format ticks with commas as thousand separators (no suffixes):
    - Always shows full number with commas (e.g., 1,234,567)
    - Integer format (no decimals)
    """
    if value is None:
        return ""

    try:
        if isinstance(value, Decimal):
            v = float(value)
        else:
            v = float(value)
    except (ValueError, TypeError, InvalidOperation):
        return str(value)

    # Format as integer with commas
    return f"{int(v):,}"

