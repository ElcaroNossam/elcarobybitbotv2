"""
Formatting utilities for display
"""
from typing import Optional, Union
from decimal import Decimal, ROUND_DOWN


def format_price(price: Union[float, Decimal, str], decimals: int = 4) -> str:
    """Format price with appropriate decimal places"""
    if price is None:
        return "—"
    
    try:
        p = float(price)
        if p == 0:
            return "0"
        
        # Determine decimals based on price magnitude
        if p >= 1000:
            decimals = 2
        elif p >= 1:
            decimals = 4
        elif p >= 0.01:
            decimals = 6
        else:
            decimals = 8
        
        return f"{p:,.{decimals}f}".rstrip("0").rstrip(".")
    except (ValueError, TypeError):
        return str(price)


def format_percent(value: Union[float, Decimal, str], decimals: int = 2) -> str:
    """Format percentage value"""
    if value is None:
        return "—"
    
    try:
        v = float(value)
        sign = "+" if v > 0 else ""
        return f"{sign}{v:.{decimals}f}%"
    except (ValueError, TypeError):
        return str(value)


def format_pnl(
    pnl: Union[float, Decimal],
    currency: str = "USDT",
    include_percent: bool = True,
    entry_value: Optional[float] = None
) -> str:
    """Format PnL with color indicators"""
    if pnl is None:
        return "—"
    
    try:
        p = float(pnl)
        emoji = "🟢" if p >= 0 else "🔴"
        sign = "+" if p >= 0 else ""
        
        result = f"{emoji} {sign}{p:,.2f} {currency}"
        
        if include_percent and entry_value and entry_value > 0:
            percent = (p / entry_value) * 100
            result += f" ({sign}{percent:.2f}%)"
        
        return result
    except (ValueError, TypeError):
        return str(pnl)


def format_balance(
    balance: Union[float, Decimal],
    currency: str = "USDT",
    decimals: int = 2
) -> str:
    """Format balance value"""
    if balance is None:
        return "—"
    
    try:
        b = float(balance)
        return f"{b:,.{decimals}f} {currency}"
    except (ValueError, TypeError):
        return str(balance)


def format_quantity(qty: float, step_size: float = 0.001) -> str:
    """Format quantity according to step size"""
    if qty is None:
        return "—"
    
    try:
        # Calculate decimal places from step size
        step_str = str(step_size)
        if "." in step_str:
            decimals = len(step_str.split(".")[1].rstrip("0"))
        else:
            decimals = 0
        
        d = Decimal(str(qty))
        rounded = d.quantize(Decimal(str(step_size)), rounding=ROUND_DOWN)
        return str(rounded)
    except Exception:
        return str(qty)


def format_leverage(leverage: int) -> str:
    """Format leverage display"""
    return f"{leverage}x"


def format_timestamp(ts, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format timestamp for display"""
    from datetime import datetime
    
    if ts is None:
        return "—"
    
    if isinstance(ts, (int, float)):
        # Unix timestamp
        dt = datetime.fromtimestamp(ts)
    elif isinstance(ts, datetime):
        dt = ts
    else:
        return str(ts)
    
    return dt.strftime(fmt)
