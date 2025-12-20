"""
General helper utilities
"""
import uuid
import re
from typing import Optional, Any, Union
from datetime import datetime, timedelta


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float"""
    if value is None:
        return default
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int"""
    if value is None:
        return default
    
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def truncate_string(s: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate string to max length"""
    if not s:
        return ""
    
    if len(s) <= max_length:
        return s
    
    return s[:max_length - len(suffix)] + suffix


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID"""
    uid = uuid.uuid4().hex[:12]
    return f"{prefix}{uid}" if prefix else uid


def parse_timeframe(tf: str) -> Optional[timedelta]:
    """Parse timeframe string to timedelta"""
    patterns = {
        r"(\d+)m": lambda m: timedelta(minutes=int(m)),
        r"(\d+)h": lambda m: timedelta(hours=int(m)),
        r"(\d+)d": lambda m: timedelta(days=int(m)),
        r"(\d+)w": lambda m: timedelta(weeks=int(m)),
    }
    
    tf = tf.lower().strip()
    
    for pattern, converter in patterns.items():
        match = re.match(pattern, tf)
        if match:
            return converter(int(match.group(1)))
    
    return None


def normalize_symbol(symbol: str) -> str:
    """Normalize trading symbol"""
    if not symbol:
        return ""
    
    symbol = symbol.upper().strip()
    symbol = symbol.replace("/", "").replace("-", "")
    
    if not symbol.endswith("USDT"):
        symbol += "USDT"
    
    return symbol


def calculate_pnl(
    entry_price: float,
    current_price: float,
    quantity: float,
    is_long: bool
) -> float:
    """Calculate PnL for a position"""
    if is_long:
        return (current_price - entry_price) * quantity
    else:
        return (entry_price - current_price) * quantity


def calculate_pnl_percent(
    entry_price: float,
    current_price: float,
    leverage: int,
    is_long: bool
) -> float:
    """Calculate PnL percentage"""
    if entry_price == 0:
        return 0.0
    
    if is_long:
        return ((current_price - entry_price) / entry_price) * 100 * leverage
    else:
        return ((entry_price - current_price) / entry_price) * 100 * leverage


def mask_api_key(key: str, visible_chars: int = 4) -> str:
    """Mask API key for display"""
    if not key or len(key) <= visible_chars * 2:
        return "••••••••"
    
    return f"{key[:visible_chars]}••••••••{key[-visible_chars:]}"


def parse_bool(value: Any) -> bool:
    """Parse value to boolean"""
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on", "enabled")
    
    return bool(value)


def chunk_list(lst: list, chunk_size: int) -> list:
    """Split list into chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def format_duration(seconds: Union[int, float]) -> str:
    """Format duration in human readable format"""
    seconds = int(seconds)
    
    if seconds < 60:
        return f"{seconds}s"
    
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m {seconds % 60}s"
    
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h {minutes % 60}m"
    
    days = hours // 24
    return f"{days}d {hours % 24}h"
