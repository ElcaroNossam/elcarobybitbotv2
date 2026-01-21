# core/strategy_settings.py
"""
SIMPLIFIED Strategy Settings Module

Architecture:
- Each strategy has ONLY LONG and SHORT settings
- No complex fallback chains
- Defaults come from ENV variables
- Simple PRIMARY KEY: (user_id, strategy, side)

Settings per side:
- enabled: bool
- percent: Entry % (risk per trade)
- sl_percent: Stop-Loss %
- tp_percent: Take-Profit %
- leverage: Leverage
- use_atr: ATR Trailing enabled
- atr_trigger_pct: Trigger % (profit to activate)
- atr_step_pct: Step % (SL distance)
- order_type: market/limit
"""

import logging
from typing import Dict, Optional
from core.db_postgres import get_conn, execute, execute_one

_logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULTS FROM ENV (loaded from coin_params.py)
# ═══════════════════════════════════════════════════════════════════════════════

def get_default_settings() -> Dict:
    """Get default settings from ENV variables."""
    from coin_params import (
        DEFAULT_PERCENT, DEFAULT_SL_PCT, DEFAULT_TP_PCT, DEFAULT_LEVERAGE,
        DEFAULT_USE_ATR, DEFAULT_ATR_TRIGGER_PCT, DEFAULT_ATR_STEP_PCT, DEFAULT_ORDER_TYPE
    )
    return {
        "enabled": True,
        "percent": DEFAULT_PERCENT,
        "sl_percent": DEFAULT_SL_PCT,
        "tp_percent": DEFAULT_TP_PCT,
        "leverage": DEFAULT_LEVERAGE,
        "use_atr": DEFAULT_USE_ATR,
        "atr_trigger_pct": DEFAULT_ATR_TRIGGER_PCT,
        "atr_step_pct": DEFAULT_ATR_STEP_PCT,
        "order_type": DEFAULT_ORDER_TYPE,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_strategy_side_settings(user_id: int, strategy: str, side: str) -> Dict:
    """
    Get settings for a specific strategy + side (LONG or SHORT).
    
    Simple and direct - no fallback logic, just reads from DB or returns defaults.
    
    Args:
        user_id: Telegram user ID
        strategy: Strategy name (scryptomera, scalper, oi, etc.)
        side: 'long' or 'short'
    
    Returns:
        Dict with all trading parameters for this strategy+side
    """
    side = side.lower()
    if side not in ('long', 'short'):
        side = 'long'
    
    row = execute_one(
        """SELECT enabled, percent, sl_percent, tp_percent, leverage,
                  use_atr, atr_trigger_pct, atr_step_pct, order_type
           FROM user_strategy_settings
           WHERE user_id = %s AND strategy = %s AND side = %s""",
        (user_id, strategy, side)
    )
    
    defaults = get_default_settings()
    
    if not row:
        return defaults.copy()
    
    return {
        "enabled": row.get('enabled') if row.get('enabled') is not None else defaults["enabled"],
        "percent": row.get('percent') if row.get('percent') is not None else defaults["percent"],
        "sl_percent": row.get('sl_percent') if row.get('sl_percent') is not None else defaults["sl_percent"],
        "tp_percent": row.get('tp_percent') if row.get('tp_percent') is not None else defaults["tp_percent"],
        "leverage": row.get('leverage') if row.get('leverage') is not None else defaults["leverage"],
        "use_atr": row.get('use_atr') if row.get('use_atr') is not None else defaults["use_atr"],
        "atr_trigger_pct": row.get('atr_trigger_pct') if row.get('atr_trigger_pct') is not None else defaults["atr_trigger_pct"],
        "atr_step_pct": row.get('atr_step_pct') if row.get('atr_step_pct') is not None else defaults["atr_step_pct"],
        "order_type": row.get('order_type') if row.get('order_type') else defaults["order_type"],
    }


def set_strategy_side_setting(user_id: int, strategy: str, side: str, field: str, value) -> bool:
    """
    Set a single field for a strategy+side.
    
    If no record exists, creates one with all default values first.
    """
    side = side.lower()
    if side not in ('long', 'short'):
        return False
    
    ALLOWED_FIELDS = {
        'enabled', 'percent', 'sl_percent', 'tp_percent', 'leverage',
        'use_atr', 'atr_trigger_pct', 'atr_step_pct', 'order_type'
    }
    
    if field not in ALLOWED_FIELDS:
        _logger.warning(f"Field {field} not in ALLOWED_FIELDS")
        return False
    
    defaults = get_default_settings()
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # UPSERT with defaults
                cur.execute(f"""
                    INSERT INTO user_strategy_settings 
                        (user_id, strategy, side, enabled, percent, sl_percent, tp_percent, 
                         leverage, use_atr, atr_trigger_pct, atr_step_pct, order_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, strategy, side) 
                    DO UPDATE SET {field} = %s, updated_at = NOW()
                """, (user_id, strategy, side, 
                      defaults["enabled"], defaults["percent"], defaults["sl_percent"], defaults["tp_percent"],
                      defaults["leverage"], defaults["use_atr"], defaults["atr_trigger_pct"], 
                      defaults["atr_step_pct"], defaults["order_type"], value))
        return True
    except Exception as e:
        _logger.error(f"Error setting {field}={value} for {user_id}/{strategy}/{side}: {e}")
        return False


def reset_strategy_side_to_defaults(user_id: int, strategy: str, side: str) -> bool:
    """Reset a strategy+side settings to ENV defaults."""
    side = side.lower()
    if side not in ('long', 'short'):
        return False
    
    defaults = get_default_settings()
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO user_strategy_settings 
                        (user_id, strategy, side, enabled, percent, sl_percent, tp_percent, 
                         leverage, use_atr, atr_trigger_pct, atr_step_pct, order_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, strategy, side) 
                    DO UPDATE SET 
                        enabled = EXCLUDED.enabled,
                        percent = EXCLUDED.percent,
                        sl_percent = EXCLUDED.sl_percent,
                        tp_percent = EXCLUDED.tp_percent,
                        leverage = EXCLUDED.leverage,
                        use_atr = EXCLUDED.use_atr,
                        atr_trigger_pct = EXCLUDED.atr_trigger_pct,
                        atr_step_pct = EXCLUDED.atr_step_pct,
                        order_type = EXCLUDED.order_type,
                        updated_at = NOW()
                """, (user_id, strategy, side, 
                      defaults["enabled"], defaults["percent"], defaults["sl_percent"], defaults["tp_percent"],
                      defaults["leverage"], defaults["use_atr"], defaults["atr_trigger_pct"], 
                      defaults["atr_step_pct"], defaults["order_type"]))
        _logger.info(f"Reset {user_id}/{strategy}/{side} to defaults")
        return True
    except Exception as e:
        _logger.error(f"Error resetting {user_id}/{strategy}/{side}: {e}")
        return False


def get_strategy_enabled(user_id: int, strategy: str) -> bool:
    """Check if strategy is enabled (either LONG or SHORT is enabled)."""
    rows = execute(
        "SELECT enabled FROM user_strategy_settings WHERE user_id = %s AND strategy = %s",
        (user_id, strategy)
    )
    if not rows:
        return True  # Default enabled
    return any(row.get('enabled', True) for row in rows)


def set_strategy_enabled(user_id: int, strategy: str, side: str, enabled: bool) -> bool:
    """Enable or disable a strategy side."""
    return set_strategy_side_setting(user_id, strategy, side, 'enabled', enabled)


def get_effective_settings(user_id: int, strategy: str, side: str = None) -> Dict:
    """
    Get effective settings for trading.
    
    SIMPLIFIED: Just returns settings for the specific side.
    No complex fallback chains.
    
    Args:
        user_id: User ID
        strategy: Strategy name
        side: 'Buy'/'LONG' or 'Sell'/'SHORT'
    
    Returns:
        Dict with all trading parameters
    """
    # Normalize side
    if side:
        side_str = str(side).upper()
        if side_str in ("BUY", "LONG"):
            side = "long"
        elif side_str in ("SELL", "SHORT"):
            side = "short"
        else:
            side = "long"
    else:
        side = "long"
    
    return get_strategy_side_settings(user_id, strategy, side)


def get_all_strategy_settings(user_id: int, strategy: str) -> Dict:
    """
    Get both LONG and SHORT settings for a strategy.
    
    Returns:
        Dict with 'long' and 'short' keys, each containing full settings
    """
    return {
        "long": get_strategy_side_settings(user_id, strategy, "long"),
        "short": get_strategy_side_settings(user_id, strategy, "short"),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGY LIST
# ═══════════════════════════════════════════════════════════════════════════════

STRATEGY_NAMES = ["scryptomera", "scalper", "elcaro", "fibonacci", "oi", "rsi_bb"]

STRATEGY_DISPLAY_NAMES = {
    "scryptomera": "Scryptomera",
    "scalper": "Scalper", 
    "elcaro": "ElCaro",
    "fibonacci": "Fibonacci",
    "oi": "OI Delta",
    "rsi_bb": "RSI+BB",
}
