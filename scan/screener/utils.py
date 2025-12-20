"""
Utility functions for formatting values (same logic as template filters).
"""
from decimal import Decimal


def format_volume(value, market_type: str | None = None) -> str:
    """
    Format volume with commas as thousand separators and $ symbol:
    - Shows exact value without rounding (e.g., $1,234,567.89123456)
    - All decimal places preserved
    """
    if value is None:
        return "0$"

    try:
        if isinstance(value, Decimal):
            # Use Decimal directly to preserve precision
            d = value
        else:
            d = Decimal(str(value))
    except (ValueError, TypeError):
        return "$0"

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


def format_vdelta(value, market_type: str | None = None) -> str:
    """
    Format volume delta with commas as thousand separators and $ symbol.
    - Shows exact value without rounding (e.g., $1,234,567.89123456)
    - All decimal places preserved
    Works the same for spot and futures (vdelta is always in USDT).
    """
    if value is None:
        return "0$"

    try:
        if isinstance(value, Decimal):
            # Use Decimal directly to preserve precision
            d = value
        else:
            d = Decimal(str(value))
    except (ValueError, TypeError):
        return "$0"

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


def get_value_color(current_value, previous_value=None, is_positive_only=False):
    """
    Determine color class for a value based on comparison with previous value.
    Returns: "value-up" (green), "value-down" (red), or "" (white/no color)
    
    For ALL values (volume, vdelta, ticks, volatility, OI):
    - Green if current > previous
    - Red if current < previous
    - White if no previous value or equal
    
    Changed: Vdelta now works like Volume - only shows color when comparing with previous value.
    """
    if current_value is None:
        return ""
    
    try:
        current = float(current_value)
    except (ValueError, TypeError):
        return ""
    
    # If we have previous value, compare
    if previous_value is not None:
        try:
            previous = float(previous_value)
            diff = current - previous
            if diff > 0.0001:
                return "value-up"
            elif diff < -0.0001:
                return "value-down"
            # If values are equal or very close, no color
            return ""
        except (ValueError, TypeError):
            pass
    
    # No previous value - no color (white) for all values
    # This makes vdelta work like volume - only color when comparing
    return ""

