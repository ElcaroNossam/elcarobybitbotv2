import os
import re
import time
import datetime
import hmac
import json
import hashlib
import asyncio 
import logging
import db  
import math
import feedparser
from pathlib import Path
from urllib.parse import quote
import aiohttp
import html
import importlib
import functools
import contextlib
from dotenv import load_dotenv
load_dotenv()
from zoneinfo import ZoneInfo
from math import floor

# Unified models and functions (NEW ARCHITECTURE)
try:
    from models import Position, Order, Balance, OrderSide, OrderType, normalize_symbol
    from bot_unified import (
        get_balance_unified, get_positions_unified, 
        place_order_unified, close_position_unified, set_leverage_unified
    )
    from exchange_router import get_user_targets, Target, normalize_env
    UNIFIED_AVAILABLE = True
except ImportError as e:
    # logger not available yet at import time
    print(f"[WARNING] Unified models not available: {e}")
    UNIFIED_AVAILABLE = False
    # Fallback empty implementations
    def get_user_targets(uid): return []
    Target = None
    normalize_env = lambda x: x

from telegram.error import TimedOut as TgTimedOut, NetworkError, BadRequest
from telegram.request import HTTPXRequest
from urllib.parse import urlencode
from html import unescape
from functools import wraps

from aiohttp import ClientSession, ClientTimeout, TCPConnector
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, InputFile, WebAppInfo, MenuButtonWebApp, MenuButtonDefault, BotCommand
from user_guide import get_user_guide_pdf
from hl_adapter import HLAdapter
from services.notification_service import init_notification_service
from services.notification_service import init_notification_service
from db import (
    get_subscribed_users,
    get_user_config,
    # HyperLiquid functions
    get_hl_credentials,
    set_hl_credentials,
    clear_hl_credentials,
    set_hl_enabled,
    get_exchange_mode,
    set_exchange_mode,
    get_exchange_type,
    set_exchange_type,
    get_exchange_status,
    set_user_field,
    reset_pyramid,
    get_all_pyramided_symbols,
    add_active_position,
    remove_active_position,
    get_user_credentials,
    set_user_credentials,
    get_all_user_credentials,
    set_trading_mode,
    get_trading_mode,
    get_active_account_types,
    get_strategy_account_types,
    get_user_trading_context,
    normalize_account_type,
    delete_user_credentials,
    get_active_positions,
    get_execution_targets,
    get_live_enabled,
    set_live_enabled,
    get_routing_policy,
    set_routing_policy,
    RoutingPolicy,
    add_trade_log,
    inc_pyramid,
    get_pyramid,
    get_prev_btc_dom,
    store_prev_btc_dom,
    save_market_snapshot,
    store_news,
    get_all_users,
    get_active_trading_users,
    get_last_signal_id,
    get_last_signal_by_symbol_in_raw,
    fetch_signal_by_id,
    add_pending_limit_order,
    get_pending_limit_orders,
    remove_pending_limit_order,
    set_dca_flag,
    get_dca_flag,
    get_trade_stats,
    get_stats_by_strategy,
    # License functions
    get_user_license,
    set_user_license,
    extend_license,
    revoke_license,
    check_license_access,
    can_trade_strategy,
    get_allowed_strategies,
    create_promo_code,
    use_promo_code,
    get_promo_codes,
    deactivate_promo_code,
    get_user_payments,
    get_license_history,
    get_all_active_licenses,
    get_expiring_licenses,
    LICENSE_TYPES,
    LICENSE_PERIODS,
    # Admin functions
    get_user_full_info,
    get_users_paginated,
    search_user_by_id,
    ban_user,
    allow_user,
    delete_user,
    update_position_strategy,
    # Admin reports
    get_global_trade_stats,
    get_global_stats_by_strategy,
    get_all_payments,
    get_payment_stats,
    get_top_traders,
    get_user_usage_report,
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
    ContextTypes,
)

from coin_params import (
    COIN_PARAMS,
    DEFAULT_SL_PCT,
    DEFAULT_TP_PCT,
    POSITIVE_KEYWORDS,
    NEGATIVE_KEYWORDS,
    SYMBOL_FILTER,
    ADMIN_ID,
    GLOBAL_PAUSED,
    THRESHOLD_MAP,
    TIMEFRAME_PARAMS,
    DEFAULT_LANG,
    MAX_OPEN_POSITIONS,
    MAX_LIMIT_ORDERS,
    BLACKLIST,
    ORDER_TYPE, 
    ORDER_PARAMS,
    CHECK_INTERVAL
)

# Configure root logger to catch all module logs (exchanges, core, etc.)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[]  # We'll add handlers below
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Also configure exchanges module logger
exchanges_logger = logging.getLogger("exchanges")
exchanges_logger.setLevel(logging.INFO)

if not logger.handlers: 
    console_h = logging.StreamHandler()
    console_h.setLevel(logging.INFO)
    console_h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(console_h)
    # Add same handler to exchanges logger for proper formatting
    exchanges_logger.addHandler(console_h)

# ═══════════════════════════════════════════════════════════════
# UNIFIED ARCHITECTURE - Feature Flag
# ═══════════════════════════════════════════════════════════════
USE_UNIFIED_ARCHITECTURE = os.getenv("USE_UNIFIED", "true").lower() == "true"

if USE_UNIFIED_ARCHITECTURE and UNIFIED_AVAILABLE:
    logger.info("✅ Unified Architecture ENABLED - using new models and exchange client")
else:
    logger.info("⚠️  Unified Architecture DISABLED - using legacy functions")
# ═══════════════════════════════════════════════════════════════

    file_h = logging.FileHandler("bot_debug.log", mode="a", encoding="utf-8")
    file_h.setLevel(logging.INFO)
    file_h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(file_h)

BOT_TOKEN   = os.getenv("TELEGRAM_TOKEN")
WEBAPP_URL  = os.getenv("WEBAPP_URL", "http://localhost:8765")  # WebApp URL from env or fallback
BYBIT_DEMO_URL = "https://api-demo.bybit.com"
BYBIT_REAL_URL = "https://api.bybit.com"
BYBIT_BASE  = BYBIT_DEMO_URL  # Default for backward compatibility
PRICE_RANGE = float(os.getenv("PRICE_RANGE", "50.0"))
EPSILON = 1e-8
ATR_INTERVAL = "5" 
ATR_TRIGGER_PCT = 1

# Global notification service instance
notification_service = None

# Spot DCA Settings
SPOT_DCA_COINS = os.getenv("SPOT_DCA_COINS", "BTC,ETH").split(",")  # Coins for Spot DCA
SPOT_DCA_DEFAULT_AMOUNT = float(os.getenv("SPOT_DCA_DEFAULT_AMOUNT", "10.0"))  # Default USDT per buy

# Professional Spot Portfolio Presets
SPOT_PORTFOLIOS = {
    "blue_chip": {
        "name": "Blue Chips",
        "emoji": "💎",
        "coins": {"BTC": 50, "ETH": 30, "BNB": 10, "SOL": 10},  # % allocation
        "description": "Top market cap, lower risk",
    },
    "defi": {
        "name": "DeFi",
        "emoji": "🏦",
        "coins": {"UNI": 25, "AAVE": 25, "MKR": 20, "COMP": 15, "SNX": 15},
        "description": "Decentralized finance protocols",
    },
    "layer2": {
        "name": "Layer 2",
        "emoji": "⚡",
        "coins": {"MATIC": 30, "ARB": 25, "OP": 25, "IMX": 20},
        "description": "Ethereum scaling solutions",
    },
    "ai_narrative": {
        "name": "AI & Data",
        "emoji": "🤖",
        "coins": {"FET": 25, "RNDR": 25, "OCEAN": 20, "AGIX": 15, "TAO": 15},
        "description": "AI and data tokens",
    },
    "gaming": {
        "name": "Gaming",
        "emoji": "🎮",
        "coins": {"AXS": 25, "SAND": 20, "MANA": 20, "GALA": 20, "ENJ": 15},
        "description": "Gaming and Metaverse",
    },
    "custom": {
        "name": "Custom",
        "emoji": "⚙️",
        "coins": {},
        "description": "Your custom allocation",
    },
}

# Smart DCA Strategies
SMART_DCA_STRATEGIES = {
    "fixed": {
        "name": "Fixed DCA",
        "emoji": "📊",
        "description": "Same amount at regular intervals",
    },
    "value_avg": {
        "name": "Value Averaging",
        "emoji": "📈",
        "description": "Buy more when price drops, less when rises",
    },
    "fear_greed": {
        "name": "Fear & Greed",
        "emoji": "😱",
        "description": "Buy more during extreme fear",
    },
    "dip_buy": {
        "name": "Dip Buying",
        "emoji": "📉",
        "description": "Only buy on significant dips",
    },
}

# Spot Take Profit Levels (% gain -> % to sell)
DEFAULT_SPOT_TP_LEVELS = [
    {"gain_pct": 20, "sell_pct": 25},   # At 20% gain, sell 25%
    {"gain_pct": 50, "sell_pct": 25},   # At 50% gain, sell 25%
    {"gain_pct": 100, "sell_pct": 25},  # At 100% gain, sell 25%
    {"gain_pct": 200, "sell_pct": 25},  # At 200% gain, sell remaining 25%
]

# Trailing TP settings for Spot
SPOT_TRAILING_TP_DEFAULTS = {
    "enabled": False,
    "activation_pct": 15.0,    # Activate trailing at +15% profit
    "trail_pct": 5.0,          # Trail by 5% from peak
    "min_profit_pct": 10.0,    # Minimum profit to lock (activation - trail)
}

# Spot Grid Bot defaults
SPOT_GRID_DEFAULTS = {
    "enabled": False,
    "price_low": 0.0,          # Grid lower bound
    "price_high": 0.0,         # Grid upper bound
    "grid_count": 10,          # Number of grid levels
    "total_investment": 100.0, # Total USDT to invest
    "take_profit_pct": None,   # Optional overall TP
    "stop_loss_pct": None,     # Optional overall SL
}

# Spot DCA intervals in seconds
SPOT_DCA_INTERVALS = {
    "hourly": 3600,
    "daily": 86400,
    "weekly": 604800,
    "biweekly": 1209600,
    "monthly": 2592000,
}

# Multi-timeframe DCA plan structure
SPOT_DCA_PLAN_TEMPLATE = {
    "name": "Plan 1",
    "coins": [],
    "amount": 10.0,
    "frequency": "weekly",
    "strategy": "fixed",
    "enabled": True,
    "last_exec_ts": 0,
}

_session: ClientSession | None = None

TRANSLATIONS_DIR = os.path.join(os.path.dirname(__file__), "translations")
SUPPORTED_LANGS = [
    fname[:-3]
    for fname in os.listdir(TRANSLATIONS_DIR)
    if fname.endswith(".py") and fname != "__init__.py"
]

LANGS: dict[str, dict] = {
    lang: importlib.import_module(f"translations.{lang}").TEXTS
    for lang in SUPPORTED_LANGS
}

NOTICE_WINDOW = 360000   
MUTE_TTL      = 3600   
SPLIT_MARKET_PART = 0.5   
SPLIT_ADDON_PCT   = 1.0   
PAGE_SIZE = 10
DCA_LEGS = [0.25, 0.25, 0.50]               
DCA_ATR_MULTS = [0.3, 0.9]                   
DCA_LEG_TIMEOUT_SEC = int(os.getenv("DCA_LEG_TIMEOUT_SEC", "72000"))
DCA_POLL_SEC = float(os.getenv("DCA_POLL_SEC", "1.0"))          
DCA_LAST_LEG_EXTRA_PCT = float(os.getenv("DCA_LAST_LEG_EXTRA_PCT", "0.8")) 

PRIVACY_PATH = os.path.join(os.path.dirname(__file__), "privacy.txt")

_last_notice: dict[tuple[int, str, str], int] = {}  
_skip_until:  dict[tuple[int, str], int] = {} 

# Cache for leverage per user+symbol to avoid redundant API calls
# Key: (user_id, symbol), Value: current leverage
_leverage_cache: dict[tuple[int, str], int] = {}

# Cache for symbol filters (tick_size, min_qty, etc) - shared across all users
# Key: symbol, Value: (timestamp, filter_dict)
_symbol_filters_cache: dict[str, tuple[float, dict]] = {}
SYMBOL_FILTERS_CACHE_TTL = 3600  # 1 hour - filters rarely change

# Cache for "no API keys" message - only show once per day per user
# Key: user_id, Value: timestamp of last notification
_last_api_keys_notice: dict[int, float] = {}
API_KEYS_NOTICE_INTERVAL = 86400  # 24 hours in seconds

# Cache for expired/invalid API keys - skip monitoring for these users
# Key: (user_id, account_type), Value: timestamp when error occurred
_expired_api_keys_cache: dict[tuple[int, str], float] = {}
EXPIRED_API_KEYS_CACHE_TTL = 3600  # 1 hour - don't retry for 1 hour after auth error


def clear_expired_api_cache(user_id: int, account_type: str = None):
    """Clear expired API keys cache for a user when they update their credentials."""
    keys_to_remove = [k for k in _expired_api_keys_cache if k[0] == user_id and (account_type is None or k[1] == account_type)]
    for k in keys_to_remove:
        _expired_api_keys_cache.pop(k, None)
    
    # Also clear unified exchange client auth cache
    try:
        from core import clear_auth_error_cache
        clear_auth_error_cache(user_id, exchange_type="bybit", account_type=account_type)
    except Exception:
        pass


def _parse_chat_ids(*keys: str) -> list[int]:
    import re
    raw_parts = []
    for k in keys:
        v = os.getenv(k, "")
        if v:
            raw_parts.append(v)
    if not raw_parts:
        return []
    raw = ",".join(raw_parts)
    return [int(x) for x in re.split(r"[,\s]+", raw) if x]

SIGNAL_CHANNEL_IDS = _parse_chat_ids("SIGNAL_CHANNEL_IDS", "SIGNAL_CHANNEL_ID", "SIGNAL_CHANNEL_ID_2")
SIGNAL_CHANNEL_IDS = list(dict.fromkeys(SIGNAL_CHANNEL_IDS))

# =====================================================
# LICENSE PRICING - TRIACELO COIN (TRC)
# 1 TRC = 1 USDT (pegged stablecoin)
# Premium: $100/mo, $90/mo x3, $80/mo x6, $70/mo x12
# =====================================================

# Import blockchain module (Sovereign Monetary System)
from core.blockchain import (
    # Core
    blockchain, get_trc_balance, get_trc_wallet, pay_with_trc,
    deposit_trc, reward_trc, get_license_price_trc, pay_license,
    LICENSE_PRICES_TRC, TRC_SYMBOL, TRC_NAME,
    # Sovereign owner operations
    is_sovereign_owner, emit_tokens, burn_tokens, set_monetary_policy,
    freeze_wallet, unfreeze_wallet, distribute_staking_rewards,
    get_treasury_stats, transfer_from_treasury, get_global_stats,
    get_owner_dashboard,
    # Constants
    SOVEREIGN_OWNER_ID, SOVEREIGN_OWNER_NAME, CHAIN_ID, CHAIN_NAME
)

# TRC prices (1 TRC = 1 USDT)
PREMIUM_TRC_1M = 100.0    # $100
PREMIUM_TRC_3M = 270.0    # $270 ($90/mo)
PREMIUM_TRC_6M = 480.0    # $480 ($80/mo)
PREMIUM_TRC_12M = 840.0   # $840 ($70/mo)

# Basic plan (50% of premium)
BASIC_TRC_1M = 50.0       # $50
BASIC_TRC_3M = 135.0      # $135 ($45/mo)
BASIC_TRC_6M = 240.0      # $240 ($40/mo)
BASIC_TRC_12M = 420.0     # $420 ($35/mo)

TRIAL_PRICE = 0  # Free trial
TRIAL_DAYS = 7   # Trial duration

# TRC Payment wallet (platform master wallet)
TRC_MASTER_WALLET = "0xTRC000000000000000000000000000000001"

# License price mapping (TRC only - fully WEB3)
LICENSE_PRICES = {
    "premium": {
        "trc": {1: PREMIUM_TRC_1M, 3: PREMIUM_TRC_3M, 6: PREMIUM_TRC_6M, 12: PREMIUM_TRC_12M},
    },
    "basic": {
        "trc": {1: BASIC_TRC_1M, 3: BASIC_TRC_3M, 6: BASIC_TRC_6M, 12: BASIC_TRC_12M},
    },
    "trial": {
        "trc": {1: 0},
    },
}

# Discount labels
DISCOUNT_LABELS = {
    1: "",
    3: " (-10%)",
    6: " (-20%)",
    12: " (-30%)",
}

_session_lock = asyncio.Lock()

async def init_session():
    global _session
    if _session is not None:
        return
    async with _session_lock:
        if _session is not None:
            return
        db.init_db()
        timeout   = ClientTimeout(total=30, connect=10, sock_read=20)
        connector = TCPConnector(limit=20, limit_per_host=5)
        _session  = ClientSession(timeout=timeout, connector=connector)

def log_calls(func):
    """Minimal decorator - only logs exceptions, no entry/exit spam"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except MissingAPICredentials as e:
            # Don't spam logs with MissingAPICredentials - just log once as warning
            uid = None
            if args:
                if isinstance(args[0], int):
                    uid = args[0]
                elif hasattr(args[0], 'effective_user'):
                    try:
                        uid = args[0].effective_user.id
                    except:
                        pass
            # Log as debug to reduce spam
            logger.debug(f"⚠️ {func.__name__} [uid={uid}]: API keys not configured")
            raise
        except Exception as e:
            uid = None
            if args:
                if isinstance(args[0], int):
                    uid = args[0]
                elif hasattr(args[0], 'effective_user'):
                    try:
                        uid = args[0].effective_user.id
                    except:
                        pass
            # Skip logging for expected SL/TP validation errors
            err_str = str(e).lower()
            if "should lower than" in err_str or "should higher than" in err_str:
                # Expected error for positions in deep loss - don't spam logs
                pass
            else:
                logger.exception(
                    f"✖ {func.__name__}"
                    + (f" [uid={uid}]" if uid else "")
                    + f": {e}"
                )
            raise
    return wrapper

def once_per(key: tuple[int, str, str], seconds: int) -> bool:
    now = int(time.time())
    if len(_last_notice) > 5000:
        cutoff = now - max(NOTICE_WINDOW, 3600)
        for k, ts in list(_last_notice.items()):
            if ts < cutoff:
                _last_notice.pop(k, None)
    t = _last_notice.get(key, 0)
    if now - t < seconds:
        return False
    _last_notice[key] = now
    return True

def is_db_full_error(e: Exception) -> bool:
    return "database or disk is full" in str(e).lower()

async def set_fixed_sl_tp_percent(uid: int, symbol: str, side: str, *, sl_pct: float = 1.0, tp_pct: float = 3.0):
    positions = await fetch_open_positions(uid)
    pos_candidates = [p for p in positions if p.get("symbol") == symbol]
    if not pos_candidates:
        raise RuntimeError(f"No open position for {symbol} to set SL/TP")
    pos = max(pos_candidates, key=lambda p: abs(float(p.get("size") or 0.0)))
    entry_val = pos.get("avgPrice") or pos.get("entry_price") or 0
    entry = float(entry_val) if entry_val else 0.0
    if entry == 0:
        raise RuntimeError(f"Could not get entry price for {symbol}")
    sl_price = round(entry * (1 - sl_pct/100) if side == "Buy" else entry * (1 + sl_pct/100), 6)
    tp_price = round(entry * (1 + tp_pct/100) if side == "Buy" else entry * (1 - tp_pct/100), 6)
    await set_trading_stop(uid, symbol, sl_price=sl_price, tp_price=tp_price, side_hint=side)

def with_texts(func):
    @functools.wraps(func)
    async def wrapper(update, ctx, *args, **kwargs):
        # Guard against None user_data (e.g., channel posts without user context)
        user = update.effective_user
        if ctx.user_data is not None:
            if 'lang' not in ctx.user_data:
                if user:
                    cfg = get_user_config(user.id)
                    ctx.user_data['lang'] = cfg.get('lang', DEFAULT_LANG)
                else:
                    ctx.user_data['lang'] = DEFAULT_LANG
            ctx.t = get_texts(ctx)
        else:
            # No user_data available - get lang from DB or use default
            if user:
                cfg = get_user_config(user.id)
                lang = cfg.get('lang', DEFAULT_LANG)
            else:
                lang = DEFAULT_LANG
            ctx.t = LANGS.get(lang, LANGS[DEFAULT_LANG])
        return await func(update, ctx, *args, **kwargs)
    return wrapper

def _load_privacy_text(t: dict) -> str:
    try:
        with open(PRIVACY_PATH, "r", encoding="utf-8") as f:
            txt = f.read().strip()
        return txt
    except Exception:
        return t.get("terms_unavailable", "Terms of Service are unavailable. Please contact the admin.")

def terms_keyboard(t: dict) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t["terms_btn_accept"], callback_data="terms:accept"),
        InlineKeyboardButton(t["terms_btn_decline"], callback_data="terms:decline"),
    ]])

# ——— Access control ————————————————————————————————
def _is_banned(uid: int) -> bool:
    cfg = get_user_config(uid) or {}
    return bool(cfg.get("is_banned", 0))

def _is_allowed_user(uid: int) -> bool:
    if uid == ADMIN_ID:       
        return True
    if _is_banned(uid):
        return False
    cfg = get_user_config(uid) or {}
    return bool(cfg.get("is_allowed", 0))

def require_access(func):
    @wraps(func)
    @with_texts
    async def _wrap(update, ctx, *args, **kw):
        uid = getattr(getattr(update, "effective_user", None), "id", None)
        if uid is None:
            return await func(update, ctx, *args, **kw)

        t = ctx.t
        
        # Update user info (username, first_name) on every interaction
        try:
            user = update.effective_user
            if user:
                username = user.username
                first_name = user.first_name
                db.update_user_info(uid, username=username, first_name=first_name)
        except Exception as e:
            logger.warning(f"Failed to update user info for {uid}: {e}")

        if uid == ADMIN_ID:
            return await func(update, ctx, *args, **kw)

        if _is_banned(uid):
            try:
                await ctx.bot.send_message(uid, t.get("banned", "You are blocked."))
            except Exception:
                pass
            return

        if not _is_allowed_user(uid):
            msg = getattr(update, "message", None)
            if msg and getattr(msg, "text", "") and msg.text.startswith("/start"):
                return await func(update, ctx, *args, **kw)
            try:
                await ctx.bot.send_message(uid, t.get("invite_only", "Access by invitation. Wait for the admin's decision."))
            except Exception:
                pass
            return

        cfg = get_user_config(uid) or {}
        if not cfg.get("terms_accepted", 0):
            msg = getattr(update, "message", None)
            data = getattr(getattr(update, "callback_query", None), "data", "")
            text = (msg.text if msg and msg.text else "") if msg else ""
            allowed = (
                text.startswith("/start")
                or text.startswith("/terms")
                or (isinstance(data, str) and data.startswith("terms:"))
            )
            if not allowed:
                try:
                    await ctx.bot.send_message(
                        uid,
                        t.get("need_terms", "First, accept the rules: /terms"),
                        reply_markup=terms_keyboard(ctx.t),
                    )
                except:
                    pass
                return

        return await func(update, ctx, *args, **kw)
    return _wrap


def require_license(license_types: list[str] | None = None):
    """
    Decorator that requires user to have an active license.
    
    Args:
        license_types: List of allowed license types, e.g. ['premium', 'basic']
                      None = any active license is OK
    """
    def decorator(func):
        @wraps(func)
        @with_texts
        async def _wrap(update, ctx, *args, **kw):
            uid = getattr(getattr(update, "effective_user", None), "id", None)
            if uid is None:
                return await func(update, ctx, *args, **kw)

            t = ctx.t

            # Admin always has access
            if uid == ADMIN_ID:
                return await func(update, ctx, *args, **kw)

            license_info = get_user_license(uid)
            
            if not license_info["is_active"]:
                # No active license
                msg = t.get("no_license", "⚠️ You need an active subscription to use this feature.\n\nUse /subscribe to purchase a license.")
                try:
                    if update.callback_query:
                        await update.callback_query.answer(msg[:200], show_alert=True)
                    else:
                        await ctx.bot.send_message(uid, msg)
                except:
                    pass
                return
            
            # Check specific license type requirement
            if license_types and license_info["license_type"] not in license_types:
                required = ", ".join(license_types)
                msg = t.get("license_required", f"⚠️ This feature requires a {required} subscription.\n\nUse /subscribe to upgrade.")
                try:
                    if update.callback_query:
                        await update.callback_query.answer(msg[:200], show_alert=True)
                    else:
                        await ctx.bot.send_message(uid, msg)
                except:
                    pass
                return
            
            # Store license info in context for use in handler
            ctx.user_data["license_info"] = license_info
            return await func(update, ctx, *args, **kw)
        return _wrap
    return decorator



def get_texts(ctx: ContextTypes.DEFAULT_TYPE) -> dict:
    lang = ctx.user_data.get('lang', DEFAULT_LANG)
    return LANGS.get(lang, LANGS[DEFAULT_LANG])

def _stricter_sl(side_: str, new_sl: float, cur_sl):
    if cur_sl in (None, "", 0, "0", 0.0):
        return new_sl
    cur = float(cur_sl)
    if side_ == "Buy":   
        return new_sl if new_sl > cur else None
    else:    
        return new_sl if new_sl < cur else None

@with_texts
async def cmd_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    buttons = []
    for lang in SUPPORTED_LANGS:
        label = LANGS[lang].get(f"lang_{lang}", lang.upper())
        buttons.append(
            InlineKeyboardButton(label, callback_data=f"setlang:{lang}")
        )
    keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    await update.message.reply_text(
        ctx.t['select_language'],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@with_texts
async def on_setlang_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    try:
        asyncio.create_task(q.answer(cache_time=1))  
    except TgTimedOut:
        logger.warning("q.answer() timeout — ignore")

    _, lang = q.data.split(":", 1)
    ctx.user_data['lang'] = lang
    set_user_field(q.from_user.id, 'lang', lang)

    ctx.t = get_texts(ctx)

    lang_label = LANGS[lang].get(f"lang_{lang}", lang.upper())
    await q.edit_message_text(f"{ctx.t['language_set']} {lang_label}")

    await ctx.bot.send_message(
        chat_id=q.from_user.id,
        text=ctx.t['welcome'],
        reply_markup=main_menu_keyboard(ctx, update=update)
    )
    
@log_calls
async def cmd_terms(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    t = get_texts(ctx)
    text = _load_privacy_text(t)
    chat_id = update.effective_chat.id

    MAX_LEN = 3500
    for i in range(0, len(text), MAX_LEN):
        chunk = text[i:i+MAX_LEN]
        await ctx.bot.send_message(chat_id, chunk)
    await ctx.bot.send_message(chat_id, t.get("terms_confirm_prompt", "Please confirm:"), reply_markup=terms_keyboard(t))

@with_texts
@log_calls
async def on_terms_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = update.effective_user.id
    data = q.data or ""
    action = data.split(":", 1)[1] if ":" in data else ""

    if action == "accept":
        set_user_field(uid, "terms_accepted", 1)
        await q.edit_message_text(ctx.t["terms_ok"])
        
        # Send privacy policy document after accepting terms
        try:
            if os.path.exists(PRIVACY_PATH):
                with open(PRIVACY_PATH, "r", encoding="utf-8") as f:
                    privacy_text = f.read()
                # Send as document for better readability
                from io import BytesIO
                privacy_buffer = BytesIO(privacy_text.encode("utf-8"))
                privacy_buffer.name = "Privacy_Policy_Terms.txt"
                await ctx.bot.send_document(
                    chat_id=uid,
                    document=InputFile(privacy_buffer, filename="Privacy_Policy_Terms.txt"),
                    caption=ctx.t.get('privacy_caption', '📜 Privacy Policy & Terms of Use\n\nPlease read this document carefully.')
                )
        except Exception as e:
            logger.warning(f"Failed to send privacy document to {uid}: {e}")
        
        # Send user guide PDF after accepting terms
        cfg = get_user_config(uid) or {}
        if not cfg.get("guide_sent", 0):
            try:
                lang = cfg.get("lang", "en")
                pdf_buffer = get_user_guide_pdf(lang)
                guide_caption = ctx.t.get('guide_caption', '📚 Trading Bot User Guide\n\nPlease read this guide to learn how to configure strategies and use the bot effectively.')
                await ctx.bot.send_document(
                    chat_id=uid,
                    document=InputFile(pdf_buffer, filename="Bybit_Trading_Bot_Guide.pdf"),
                    caption=guide_caption
                )
                set_user_field(uid, "guide_sent", 1)
            except Exception as e:
                logger.warning(f"Failed to send user guide PDF to {uid}: {e}")
        
        await ctx.bot.send_message(
            chat_id=uid,
            text=ctx.t["welcome"],
            reply_markup=main_menu_keyboard(ctx, update=update),
        )
    elif action == "decline":
        set_user_field(uid, "terms_accepted", 0)
        await q.edit_message_text(ctx.t["terms_declined"])
    else:
        await q.answer(ctx.t.get("unknown_action", "Unknown action"), show_alert=True)


# ============================================================================
# 2FA Login Confirmation Handler
# ============================================================================
@log_calls
async def on_twofa_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle 2FA approval/denial from bot buttons."""
    q = update.callback_query
    await q.answer()
    uid = update.effective_user.id
    data = q.data or ""
    
    # Parse: twofa_approve:xxx or twofa_deny:xxx
    parts = data.split(":")
    if len(parts) != 2:
        return
    
    action = parts[0].replace("twofa_", "")  # approve or deny
    confirmation_id = parts[1]
    
    try:
        from webapp.services import telegram_auth
        
        # Get user language for messages
        cfg = get_user_config(uid) or {}
        lang = cfg.get("lang", "en")
        
        translations = {
            "uk": {
                "approved": "✅ Вхід підтверджено!\n\nТепер ви можете продовжити у браузері.",
                "denied": "❌ Вхід відхилено.\n\nЯкщо це була не ваша спроба, рекомендуємо змінити налаштування безпеки.",
                "expired": "⏰ Час підтвердження минув. Спробуйте ще раз.",
                "error": "⚠️ Помилка обробки. Спробуйте пізніше."
            },
            "ru": {
                "approved": "✅ Вход подтверждён!\n\nТеперь вы можете продолжить в браузере.",
                "denied": "❌ Вход отклонён.\n\nЕсли это была не ваша попытка, рекомендуем изменить настройки безопасности.",
                "expired": "⏰ Время подтверждения истекло. Попробуйте ещё раз.",
                "error": "⚠️ Ошибка обработки. Попробуйте позже."
            },
            "en": {
                "approved": "✅ Login approved!\n\nYou can now continue in your browser.",
                "denied": "❌ Login denied.\n\nIf this wasn't you, we recommend reviewing your security settings.",
                "expired": "⏰ Confirmation expired. Please try again.",
                "error": "⚠️ Processing error. Please try again later."
            }
        }
        t = translations.get(lang, translations["en"])
        
        if action == "approve":
            success = telegram_auth.confirm_2fa(confirmation_id, approved=True)
            if success:
                await q.edit_message_text(t["approved"])
            else:
                await q.edit_message_text(t["expired"])
        else:  # deny
            success = telegram_auth.confirm_2fa(confirmation_id, approved=False)
            if success:
                await q.edit_message_text(t["denied"])
            else:
                await q.edit_message_text(t["expired"])
                
    except Exception as e:
        logger.error(f"2FA callback error: {e}")
        await q.edit_message_text("⚠️ Error processing request")

# ------------------------------------------------------------------------------------
# API Settings Menu
# ------------------------------------------------------------------------------------
def _mask_key(key: str | None) -> str:
    """Mask API key for display, showing only last 4 chars."""
    if not key:
        return ""
    if len(key) <= 4:
        return "••••"
    return f"••••••••{key[-4:]}"

def get_api_settings_keyboard(t: dict, creds: dict) -> InlineKeyboardMarkup:
    """Build API settings keyboard with current state."""
    demo_key = creds.get("demo_api_key")
    demo_secret = creds.get("demo_api_secret")
    real_key = creds.get("real_api_key")
    real_secret = creds.get("real_api_secret")
    
    # Status indicators
    demo_key_status = "✅" if demo_key else "❌"
    demo_secret_status = "✅" if demo_secret else "❌"
    real_key_status = "✅" if real_key else "❌"
    real_secret_status = "✅" if real_secret else "❌"
    
    buttons = [
        # Demo section
        [InlineKeyboardButton(f"━━━ 🧪 DEMO ━━━", callback_data="api:noop")],
        [
            InlineKeyboardButton(f"{demo_key_status} API Key", callback_data="api:demo_key"),
            InlineKeyboardButton(f"{demo_secret_status} Secret", callback_data="api:demo_secret"),
        ],
        [InlineKeyboardButton(f"🔄 Test Demo", callback_data="api:test_demo")],
        
        # Real section  
        [InlineKeyboardButton(f"━━━ 💼 REAL ━━━", callback_data="api:noop")],
        [
            InlineKeyboardButton(f"{real_key_status} API Key", callback_data="api:real_key"),
            InlineKeyboardButton(f"{real_secret_status} Secret", callback_data="api:real_secret"),
        ],
        [InlineKeyboardButton(f"🔄 Test Real", callback_data="api:test_real")],
        
        # Delete buttons
        [
            InlineKeyboardButton(t.get("api_btn_delete_demo", "🗑 Delete Demo"), callback_data="api:delete_demo"),
            InlineKeyboardButton(t.get("api_btn_delete_real", "🗑 Delete Real"), callback_data="api:delete_real"),
        ],
    ]
    
    return InlineKeyboardMarkup(buttons)

def format_api_settings_message(t: dict, creds: dict) -> str:
    """Format API settings message with current state."""
    demo_key = creds.get("demo_api_key")
    demo_secret = creds.get("demo_api_secret")
    real_key = creds.get("real_api_key")
    real_secret = creds.get("real_api_secret")
    
    # Format status
    demo_key_display = _mask_key(demo_key) if demo_key else t.get("api_key_not_set", "❌ Not set")
    demo_secret_display = _mask_key(demo_secret) if demo_secret else t.get("api_key_not_set", "❌ Not set")
    real_key_display = _mask_key(real_key) if real_key else t.get("api_key_not_set", "❌ Not set")
    real_secret_display = _mask_key(real_secret) if real_secret else t.get("api_key_not_set", "❌ Not set")
    
    msg = f"""{t.get("api_settings_title", "🔑 <b>API Settings</b>")}

{t.get("api_demo_title", "🧪 Demo Account")}
├ API Key: <code>{demo_key_display}</code>
└ Secret: <code>{demo_secret_display}</code>

{t.get("api_real_title", "💼 Real Account")}
├ API Key: <code>{real_key_display}</code>
└ Secret: <code>{real_secret_display}</code>"""
    
    return msg

@with_texts
@log_calls
async def cmd_api_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show API settings menu."""
    uid = update.effective_user.id
    creds = get_all_user_credentials(uid)
    
    msg = format_api_settings_message(ctx.t, creds)
    keyboard = get_api_settings_keyboard(ctx.t, creds)
    
    await update.message.reply_text(
        msg,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@with_texts
@log_calls
async def on_api_settings_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle API settings callbacks."""
    q = update.callback_query
    uid = update.effective_user.id
    t = ctx.t
    
    action = q.data.split(":", 1)[1] if ":" in q.data else ""
    
    if action == "noop":
        await q.answer()
        return
    
    # Helper to safely edit message (ignores "not modified" error)
    async def safe_edit(text, reply_markup=None, parse_mode="HTML"):
        try:
            await q.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        except BadRequest as e:
            if "not modified" not in str(e).lower():
                raise
    
    # Enter API key/secret
    if action in ("demo_key", "demo_secret", "real_key", "real_secret"):
        await q.answer()
        prompts = {
            "demo_key": t.get("api_enter_demo_key", "Enter Demo API Key:"),
            "demo_secret": t.get("api_enter_demo_secret", "Enter Demo API Secret:"),
            "real_key": t.get("api_enter_real_key", "Enter Real API Key:"),
            "real_secret": t.get("api_enter_real_secret", "Enter Real API Secret:"),
        }
        ctx.user_data["mode"] = f"enter_api_{action}"
        await safe_edit(prompts[action])
        return
    
    # Delete credentials
    if action == "delete_demo":
        delete_user_credentials(uid, "demo")
        creds = get_all_user_credentials(uid)
        msg = format_api_settings_message(t, creds)
        keyboard = get_api_settings_keyboard(t, creds)
        await q.answer(t.get("api_deleted", "API deleted for {account}").format(account="Demo"), show_alert=True)
        await safe_edit(msg, reply_markup=keyboard)
        return
    
    if action == "delete_real":
        delete_user_credentials(uid, "real")
        creds = get_all_user_credentials(uid)
        msg = format_api_settings_message(t, creds)
        keyboard = get_api_settings_keyboard(t, creds)
        await q.answer(t.get("api_deleted", "API deleted for {account}").format(account="Real"), show_alert=True)
        await safe_edit(msg, reply_markup=keyboard)
        return
    
    # Test connection
    if action in ("test_demo", "test_real"):
        account_type = "demo" if action == "test_demo" else "real"
        account_emoji = "🧪" if account_type == "demo" else "💼"
        account_name = t.get("api_mode_demo", "Demo") if account_type == "demo" else t.get("api_mode_real", "Real")
        
        try:
            result = await _bybit_request(
                uid, "GET", "/v5/account/wallet-balance",
                params={"accountType": "UNIFIED", "coin": "USDT"},
                account_type=account_type
            )
            coins = result.get("list", [{}])[0].get("coin", [])
            usdt = next((c for c in coins if c.get("coin") == "USDT"), {})
            balance = float(usdt.get("walletBalance", 0))
            equity = float(usdt.get("equity", 0))
            available = float(usdt.get("availableToWithdraw", 0))
            
            test_msg = f"""✅ <b>{t.get('api_test_success', 'Connection Successful!')}</b>

{account_emoji} <b>{account_name}</b>

💰 {t.get('balance_wallet', 'Wallet Balance')}: <b>{balance:.2f}</b> USDT
💎 {t.get('balance_equity', 'Equity')}: <b>{equity:.2f}</b> USDT
✨ {t.get('balance_available', 'Available')}: <b>{available:.2f}</b> USDT

🔗 {t.get('api_test_status', 'Status')}: 🟢 {t.get('api_test_connected', 'Connected')}"""
            
            await q.answer("✅")
            creds = get_all_user_credentials(uid)
            keyboard = get_api_settings_keyboard(t, creds)
            try:
                await q.edit_message_text(test_msg, reply_markup=keyboard, parse_mode="HTML")
            except BadRequest:
                pass
        except MissingAPICredentials:
            test_msg = f"""{account_emoji} <b>{account_name}</b>

❌ <b>{t.get('api_test_no_keys', 'API Keys Not Set')}</b>

{t.get('api_test_set_keys', 'Please set API Key and Secret first.')}"""
            
            await q.answer("❌")
            creds = get_all_user_credentials(uid)
            keyboard = get_api_settings_keyboard(t, creds)
            try:
                await q.edit_message_text(test_msg, reply_markup=keyboard, parse_mode="HTML")
            except BadRequest:
                pass
        except Exception as e:
            test_msg = f"""{account_emoji} <b>{account_name}</b>

❌ <b>{t.get('api_test_failed', 'Connection Failed')}</b>

{t.get('api_test_error', 'Error')}: <code>{str(e)[:100]}</code>

{t.get('api_test_check_keys', 'Please check your API credentials.')}"""
            
            await q.answer("❌")
            creds = get_all_user_credentials(uid)
            keyboard = get_api_settings_keyboard(t, creds)
            try:
                await q.edit_message_text(test_msg, reply_markup=keyboard, parse_mode="HTML")
            except BadRequest:
                pass
        return
    
    # Unknown action - just answer to dismiss loading
    await q.answer()


# ==============================================================================
# SPOT SETTINGS HANDLERS
# ==============================================================================

def get_spot_settings_keyboard(t: dict, cfg: dict, spot_settings: dict) -> InlineKeyboardMarkup:
    """Build keyboard for Spot DCA settings - Professional version."""
    coins = spot_settings.get("coins", SPOT_DCA_COINS)
    amount = spot_settings.get("dca_amount", SPOT_DCA_DEFAULT_AMOUNT)
    freq = spot_settings.get("frequency", "manual")
    auto_dca = spot_settings.get("auto_dca", False)
    trading_mode = spot_settings.get("trading_mode", "demo")
    strategy = spot_settings.get("strategy", "fixed")
    portfolio = spot_settings.get("portfolio", "custom")
    tp_enabled = spot_settings.get("tp_enabled", False)
    rebalance_enabled = spot_settings.get("rebalance_enabled", False)
    
    freq_labels = {
        "manual": "⏸️ Manual",
        "hourly": t.get("spot_freq_hourly", "⏰ Hourly"),
        "daily": t.get("spot_freq_daily", "Daily"),
        "weekly": t.get("spot_freq_weekly", "Weekly"),
        "biweekly": t.get("spot_freq_biweekly", "Bi-Weekly"),
        "monthly": t.get("spot_freq_monthly", "Monthly"),
    }
    freq_label = freq_labels.get(freq, "Manual")
    
    auto_emoji = "✅" if auto_dca else "❌"
    tp_emoji = "✅" if tp_enabled else "❌"
    rebalance_emoji = "✅" if rebalance_enabled else "❌"
    mode_label = "Demo" if trading_mode == "demo" else "Real"
    
    # Get portfolio info
    portfolio_info = SPOT_PORTFOLIOS.get(portfolio, SPOT_PORTFOLIOS["custom"])
    portfolio_label = f"{portfolio_info['emoji']} {portfolio_info['name']}"
    
    # Get strategy info
    strategy_info = SMART_DCA_STRATEGIES.get(strategy, SMART_DCA_STRATEGIES["fixed"])
    strategy_label = f"{strategy_info['emoji']} {strategy_info['name']}"
    
    # Format coins display
    if portfolio != "custom" and portfolio_info.get("coins"):
        coins_display = portfolio_label
    else:
        coins_str = ", ".join(coins[:3]) if isinstance(coins, list) else str(coins)
        if isinstance(coins, list) and len(coins) > 3:
            coins_str += f" +{len(coins)-3}"
        coins_display = coins_str
    
    buttons = [
        # Trading mode (demo/real)
        [InlineKeyboardButton(
            f"📍 Mode: {mode_label}",
            callback_data="spot:mode"
        )],
        # Portfolio preset
        [InlineKeyboardButton(
            f"📁 Portfolio: {portfolio_label}",
            callback_data="spot:portfolio"
        )],
        # Custom coins (if custom portfolio)
        [InlineKeyboardButton(
            f"🪙 Coins: {coins_display}",
            callback_data="spot:coins"
        )],
        # DCA Strategy
        [InlineKeyboardButton(
            f"🎯 Strategy: {strategy_label}",
            callback_data="spot:strategy"
        )],
        # DCA Amount
        [InlineKeyboardButton(
            f"💵 Amount: {amount} USDT",
            callback_data="spot:amount"
        )],
        # Frequency
        [InlineKeyboardButton(
            f"⏰ Frequency: {freq_label}",
            callback_data="spot:frequency"
        )],
        # Auto DCA toggle
        [
            InlineKeyboardButton(f"🔄 Auto DCA: {auto_emoji}", callback_data="spot:auto_toggle"),
            InlineKeyboardButton(f"🎯 Auto TP: {tp_emoji}", callback_data="spot:tp_toggle"),
        ],
        # Trailing TP
        [InlineKeyboardButton(
            f"📈 Trailing TP: {'✅' if spot_settings.get('trailing_tp', {}).get('enabled') else '❌'}",
            callback_data="spot:trailing_toggle"
        )],
        # Rebalancing
        [InlineKeyboardButton(
            f"⚖️ Auto Rebalance: {rebalance_emoji}",
            callback_data="spot:rebalance_toggle"
        )],
        # Action buttons
        [
            InlineKeyboardButton("💰 Buy Now", callback_data="spot:buy_now"),
            InlineKeyboardButton("💸 Sell", callback_data="spot:sell_menu"),
        ],
        [
            InlineKeyboardButton("📋 Limit Order", callback_data="spot:limit_order"),
            InlineKeyboardButton("🔲 Grid Bot", callback_data="spot:grid_menu"),
        ],
        [
            InlineKeyboardButton("⚖️ Rebalance Now", callback_data="spot:rebalance_now"),
            InlineKeyboardButton("📊 Stats", callback_data="spot:portfolio_stats"),
        ],
        # Holdings / Stats
        [
            InlineKeyboardButton("💎 Holdings", callback_data="spot:holdings"),
            InlineKeyboardButton("📈 Performance", callback_data="spot:performance"),
        ],
        # TP Levels settings
        [InlineKeyboardButton(
            "⚙️ TP Settings",
            callback_data="spot:tp_settings"
        )],
        # Back to strategies
        [InlineKeyboardButton(
            t.get("spot_btn_back", "⬅️ Back"),
            callback_data="spot:back_to_strategies"
        )],
    ]
    return InlineKeyboardMarkup(buttons)


def format_spot_settings_message(t: dict, cfg: dict, spot_settings: dict) -> str:
    """Format Spot DCA settings message - Professional version."""
    coins = spot_settings.get("coins", SPOT_DCA_COINS)
    amount = spot_settings.get("dca_amount", SPOT_DCA_DEFAULT_AMOUNT)
    freq = spot_settings.get("frequency", "manual")
    auto_dca = spot_settings.get("auto_dca", False)
    total_invested = spot_settings.get("total_invested", 0.0)
    trading_mode = spot_settings.get("trading_mode", "demo")
    strategy = spot_settings.get("strategy", "fixed")
    portfolio = spot_settings.get("portfolio", "custom")
    tp_enabled = spot_settings.get("tp_enabled", False)
    rebalance_enabled = spot_settings.get("rebalance_enabled", False)
    dip_threshold = spot_settings.get("dip_threshold", 5.0)  # % drop to trigger extra buy
    fear_threshold = spot_settings.get("fear_threshold", 25)  # F&G index below this = buy more
    
    freq_labels = {
        "manual": "⏸️ Manual",
        "daily": t.get("spot_freq_daily", "Daily"),
        "weekly": t.get("spot_freq_weekly", "Weekly"),
        "biweekly": t.get("spot_freq_biweekly", "Bi-Weekly"),
        "monthly": t.get("spot_freq_monthly", "Monthly"),
    }
    freq_label = freq_labels.get(freq, "Manual")
    
    # Get portfolio info
    portfolio_info = SPOT_PORTFOLIOS.get(portfolio, SPOT_PORTFOLIOS["custom"])
    portfolio_label = f"{portfolio_info['emoji']} {portfolio_info['name']}"
    
    # Get strategy info
    strategy_info = SMART_DCA_STRATEGIES.get(strategy, SMART_DCA_STRATEGIES["fixed"])
    strategy_label = f"{strategy_info['emoji']} {strategy_info['name']}"
    
    # Coins allocation
    if portfolio != "custom" and portfolio_info.get("coins"):
        coins_lines = []
        for coin, pct in portfolio_info["coins"].items():
            coins_lines.append(f"  • {coin}: {pct}%")
        coins_display = "\n" + "\n".join(coins_lines)
    else:
        coins_str = ", ".join(coins) if isinstance(coins, list) else str(coins)
        coins_display = coins_str
    
    auto_status = "✅" if auto_dca else "❌"
    tp_status = "✅" if tp_enabled else "❌"
    rebalance_status = "✅" if rebalance_enabled else "❌"
    mode_label = "Demo" if trading_mode == "demo" else "Real"
    
    lines = [
        "💹 <b>Professional Spot DCA</b>",
        "",
        f"📍 <b>Mode:</b> {mode_label}",
        f"📁 <b>Portfolio:</b> {portfolio_label}",
        f"<i>{portfolio_info.get('description', '')}</i>",
        "",
        f"🪙 <b>Coins:</b> {coins_display}",
        "",
        f"🎯 <b>Strategy:</b> {strategy_label}",
        f"<i>{strategy_info.get('description', '')}</i>",
        "",
        f"💵 <b>Amount per DCA:</b> {amount} USDT",
        f"⏰ <b>Frequency:</b> {freq_label}",
        "",
        f"🔄 <b>Auto DCA:</b> {auto_status}",
        f"🎯 <b>Auto Take Profit:</b> {tp_status}",
        f"⚖️ <b>Auto Rebalance:</b> {rebalance_status}",
        "",
        f"📊 <b>Total Invested:</b> {total_invested:.2f} USDT",
    ]
    
    # Add strategy-specific info
    if strategy == "dip_buy":
        lines.append(f"📉 <b>Dip Threshold:</b> -{dip_threshold}%")
    elif strategy == "fear_greed":
        lines.append(f"😱 <b>Fear Threshold:</b> {fear_threshold}")
    
    return "\n".join(lines)


@with_texts
@log_calls
async def cmd_spot_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handler for Spot Settings button in main menu."""
    uid = update.effective_user.id
    t = ctx.t
    
    cfg = db.get_user_config(uid)
    
    # Check if spot is enabled
    if not cfg.get("spot_enabled", 0):
        await update.message.reply_text(
            t.get("spot_not_enabled", "❌ Spot trading is not enabled. Enable it in API Settings first."),
            parse_mode="HTML"
        )
        return
    
    spot_settings = cfg.get("spot_settings", {})
    if not spot_settings:
        # Initialize default spot settings
        spot_settings = {
            "coins": SPOT_DCA_COINS.copy() if isinstance(SPOT_DCA_COINS, list) else SPOT_DCA_COINS.split(","),
            "dca_amount": SPOT_DCA_DEFAULT_AMOUNT,
            "frequency": "manual",
            "auto_dca": False,
            "total_invested": 0.0,
        }
    
    msg = format_spot_settings_message(t, cfg, spot_settings)
    keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
    
    await update.message.reply_text(msg, reply_markup=keyboard, parse_mode="HTML")


@with_texts
@log_calls
async def on_spot_settings_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Callback handler for Spot settings inline buttons."""
    q = update.callback_query
    await q.answer()
    
    uid = q.from_user.id
    t = ctx.t
    data = q.data  # "spot:action"
    
    if not data.startswith("spot:"):
        return
    
    action = data.split(":", 1)[1]
    cfg = db.get_user_config(uid)
    spot_settings = cfg.get("spot_settings", {})
    
    if not spot_settings:
        spot_settings = {
            "coins": SPOT_DCA_COINS.copy() if isinstance(SPOT_DCA_COINS, list) else SPOT_DCA_COINS.split(","),
            "dca_amount": SPOT_DCA_DEFAULT_AMOUNT,
            "frequency": "manual",
            "auto_dca": False,
            "total_invested": 0.0,
            "trailing_tp": SPOT_TRAILING_TP_DEFAULTS.copy(),
            "trailing_state": {},
            "grids": {},
            "purchase_history": {},
        }
    
    # Handle actions
    if action == "coins":
        # Show coin selection
        available_coins = SPOT_DCA_COINS if isinstance(SPOT_DCA_COINS, list) else SPOT_DCA_COINS.split(",")
        current_coins = spot_settings.get("coins", available_coins)
        
        buttons = []
        for coin in available_coins:
            is_selected = coin in current_coins
            emoji = "✅" if is_selected else "⬜"
            buttons.append([InlineKeyboardButton(
                f"{emoji} {coin}",
                callback_data=f"spot:coin_toggle:{coin}"
            )])
        buttons.append([InlineKeyboardButton(
            t.get("spot_btn_back", "⬅️ Back"),
            callback_data="spot:back_to_main"
        )])
        
        try:
            await q.edit_message_text(
                t.get("spot_select_coins", "Select coins for Spot DCA:"),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="HTML"
            )
        except BadRequest:
            pass
        return
    
    if action.startswith("coin_toggle:"):
        coin = action.split(":")[1]
        current_coins = list(spot_settings.get("coins", []))
        
        if coin in current_coins:
            if len(current_coins) > 1:  # Don't allow empty selection
                current_coins.remove(coin)
        else:
            current_coins.append(coin)
        
        spot_settings["coins"] = current_coins
        db.set_user_field(uid, "spot_settings", json.dumps(spot_settings))
        
        # Refresh coin selection
        available_coins = SPOT_DCA_COINS if isinstance(SPOT_DCA_COINS, list) else SPOT_DCA_COINS.split(",")
        buttons = []
        for c in available_coins:
            is_selected = c in current_coins
            emoji = "✅" if is_selected else "⬜"
            buttons.append([InlineKeyboardButton(
                f"{emoji} {c}",
                callback_data=f"spot:coin_toggle:{c}"
            )])
        buttons.append([InlineKeyboardButton(
            t.get("spot_btn_back", "⬅️ Back"),
            callback_data="spot:back_to_main"
        )])
        
        try:
            await q.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
        except BadRequest:
            pass
        return
    
    if action == "amount":
        ctx.user_data["spot_awaiting"] = "amount"
        try:
            await q.edit_message_text(
                t.get("spot_enter_amount", "Enter DCA amount in USDT:"),
                parse_mode="HTML"
            )
        except BadRequest:
            pass
        return
    
    if action == "frequency":
        # Cycle through frequencies (includes hourly and biweekly)
        freqs = ["manual", "hourly", "daily", "weekly", "biweekly", "monthly"]
        current = spot_settings.get("frequency", "manual")
        idx = freqs.index(current) if current in freqs else 0
        new_freq = freqs[(idx + 1) % len(freqs)]
        
        spot_settings["frequency"] = new_freq
        db.set_user_field(uid, "spot_settings", json.dumps(spot_settings))
        
        freq_labels = {
            "manual": "⏸️ Manual",
            "hourly": t.get("spot_freq_hourly", "⏰ Hourly"),
            "daily": t.get("spot_freq_daily", "Daily"),
            "weekly": t.get("spot_freq_weekly", "Weekly"),
            "biweekly": t.get("spot_freq_biweekly", "Bi-Weekly"),
            "monthly": t.get("spot_freq_monthly", "Monthly"),
        }
        await q.answer(t.get("spot_frequency_saved", "✅ Frequency set to {freq}").format(freq=freq_labels[new_freq]))
        
        cfg = db.get_user_config(uid)
        spot_settings = cfg.get("spot_settings", {})
        msg = format_spot_settings_message(t, cfg, spot_settings)
        keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
        try:
            await q.edit_message_text(msg, reply_markup=keyboard, parse_mode="HTML")
        except BadRequest:
            pass
        return
    
    if action == "auto_toggle":
        current = spot_settings.get("auto_dca", False)
        spot_settings["auto_dca"] = not current
        db.set_user_field(uid, "spot_settings", json.dumps(spot_settings))
        
        status_msg = t.get("spot_auto_enabled", "✅ Auto DCA enabled") if not current else t.get("spot_auto_disabled", "❌ Auto DCA disabled")
        await q.answer(status_msg, show_alert=True)
        
        cfg = db.get_user_config(uid)
        spot_settings = cfg.get("spot_settings", {})
        msg = format_spot_settings_message(t, cfg, spot_settings)
        keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
        try:
            await q.edit_message_text(msg, reply_markup=keyboard, parse_mode="HTML")
        except BadRequest:
            pass
        return
    
    if action == "buy_now":
        # Execute Smart DCA buy for all selected coins
        coins = spot_settings.get("coins", SPOT_DCA_COINS)
        base_amount = spot_settings.get("dca_amount", SPOT_DCA_DEFAULT_AMOUNT)
        strategy = spot_settings.get("strategy", "fixed")
        portfolio = spot_settings.get("portfolio", "custom")
        allocation = spot_settings.get("allocation", {})
        
        # Use trading mode from spot settings
        account_type = spot_settings.get("trading_mode", "demo")
        
        results = []
        total_spent = 0.0
        skipped = []
        
        # Get portfolio allocation if using preset
        if portfolio != "custom" and portfolio in SPOT_PORTFOLIOS:
            portfolio_info = SPOT_PORTFOLIOS[portfolio]
            allocation = portfolio_info.get("coins", {})
        
        for coin in coins:
            # Calculate amount based on allocation
            if allocation and coin in allocation:
                coin_pct = allocation[coin] / 100.0
                coin_base_amount = base_amount * coin_pct
            else:
                coin_base_amount = base_amount / len(coins) if coins else base_amount
            
            # Apply smart DCA strategy multiplier
            adjusted_amount = await calculate_smart_dca_amount(
                base_amount=coin_base_amount,
                strategy=strategy,
                coin=coin,
                spot_settings=spot_settings,
                user_id=uid,
                account_type=account_type,
            )
            
            if adjusted_amount <= 0:
                skipped.append(coin)
                continue
            
            result = await execute_spot_dca_buy(uid, coin, adjusted_amount, account_type=account_type)
            if result.get("success"):
                spent = result.get("usdt_spent", adjusted_amount)
                results.append(f"✅ {result.get('qty', 0):.6f} {coin} (${spent:.2f})")
                total_spent += spent
            elif result.get("error") == "SKIP":
                # Silently skip - don't show error to user
                reason = result.get("reason", "unknown")
                if reason == "order_too_small":
                    skipped.append(f"{coin} (min)")
                elif reason == "insufficient_balance":
                    skipped.append(f"{coin} (bal)")
                else:
                    skipped.append(coin)
            else:
                # Only show real errors
                results.append(f"❌ {coin}: {result.get('error', 'Error')}")
        
        # Update total invested
        spot_settings["total_invested"] = spot_settings.get("total_invested", 0.0) + total_spent
        
        # Record last DCA timestamp
        spot_settings["last_dca_ts"] = int(time.time())
        
        db.set_user_field(uid, "spot_settings", json.dumps(spot_settings))
        
        # Build result message
        result_lines = results.copy()
        if skipped:
            result_lines.append(f"⏭️ Skipped (no dip): {', '.join(skipped)}")
        
        strategy_info = SMART_DCA_STRATEGIES.get(strategy, {})
        strategy_label = f"{strategy_info.get('emoji', '📊')} {strategy_info.get('name', 'Fixed')}"
        
        result_msg = "\n".join(result_lines)
        await q.answer(f"DCA executed! Spent: ${total_spent:.2f}", show_alert=True)
        
        cfg = db.get_user_config(uid)
        spot_settings = cfg.get("spot_settings", {})
        msg = format_spot_settings_message(t, cfg, spot_settings)
        keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
        try:
            extra_info = f"\n\n<b>🎯 Strategy:</b> {strategy_label}\n<b>Last Buy:</b>\n{result_msg}"
            await q.edit_message_text(msg + extra_info, reply_markup=keyboard, parse_mode="HTML")
        except BadRequest:
            pass
        return
    
    if action == "holdings":
        # Show current spot holdings - use trading mode from settings
        account_type = spot_settings.get("trading_mode", "demo")
        
        balances = await fetch_spot_balance(uid, account_type=account_type)
        
        if not balances:
            await q.answer(t.get("spot_no_balance", "❌ No spot balance found"), show_alert=True)
            return
        
        lines = ["💎 <b>Spot Holdings:</b>", ""]
        for coin, amount in sorted(balances.items()):
            if amount > 0.00001:
                lines.append(f"• {coin}: {amount:.8f}")
        
        holdings_msg = "\n".join(lines)
        await q.answer()
        
        cfg = db.get_user_config(uid)
        spot_settings = cfg.get("spot_settings", {})
        msg = format_spot_settings_message(t, cfg, spot_settings)
        keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
        try:
            await q.edit_message_text(msg + f"\n\n{holdings_msg}", reply_markup=keyboard, parse_mode="HTML")
        except BadRequest:
            pass
        return
    
    if action == "back_to_main":
        cfg = db.get_user_config(uid)
        spot_settings = cfg.get("spot_settings", {})
        msg = format_spot_settings_message(t, cfg, spot_settings)
        keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
        try:
            await q.edit_message_text(msg, reply_markup=keyboard, parse_mode="HTML")
        except BadRequest:
            pass
        return
    
    if action == "mode":
        # Toggle trading mode (demo/real)
        current_mode = spot_settings.get("trading_mode", "demo")
        new_mode = "real" if current_mode == "demo" else "demo"
        spot_settings["trading_mode"] = new_mode
        db.set_user_field(uid, "spot_settings", json.dumps(spot_settings))
        
        mode_labels = {"demo": "🧪 Demo", "real": "💰 Real"}
        await q.answer(f"Spot: {mode_labels.get(new_mode, new_mode)}")
        
        cfg = db.get_user_config(uid)
        spot_settings = cfg.get("spot_settings", {})
        msg = format_spot_settings_message(t, cfg, spot_settings)
        keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
        try:
            await q.edit_message_text(msg, reply_markup=keyboard, parse_mode="HTML")
        except BadRequest:
            pass
        return
    
    if action == "back_to_strategies":
        # Return to strategies menu
        cfg = get_user_config(uid)
        active_exchange = db.get_exchange_type(uid) or "bybit"
        global_use_atr = bool(cfg.get("use_atr", 1))
        lines = [t.get('strategy_settings_header', '⚙️ *Strategy Settings*')]
        lines.append("")
        for strat_key, strat_nm in STRATEGY_NAMES_MAP.items():
            strat_settings_data = db.get_strategy_settings(uid, strat_key)
            status_parts = _build_strategy_status_parts(strat_key, strat_settings_data, active_exchange, global_use_atr)
            if status_parts:
                lines.append(f"*{strat_nm}*: {', '.join(status_parts)}")
            else:
                lines.append(f"*{strat_nm}*: {t.get('using_global', 'Using global settings')}")
        lines.append("")
        dca_status = '✅' if cfg.get('dca_enabled', 0) else '❌'
        lines.append(f"*DCA*: {dca_status} Leg1={cfg.get('dca_pct_1', 10.0)}%, Leg2={cfg.get('dca_pct_2', 25.0)}%")
        
        try:
            await q.edit_message_text(
                "\n".join(lines),
                parse_mode="Markdown",
                reply_markup=get_strategy_settings_keyboard(t, cfg, uid=uid)
            )
        except BadRequest:
            pass
        return
    
    # === NEW PROFESSIONAL SPOT FEATURES ===
    
    if action == "portfolio":
        # Show portfolio selection menu
        buttons = []
        current_portfolio = spot_settings.get("portfolio", "custom")
        for key, info in SPOT_PORTFOLIOS.items():
            selected = "✅ " if key == current_portfolio else ""
            coins_preview = ", ".join(list(info["coins"].keys())[:3]) if info["coins"] else "Custom"
            buttons.append([InlineKeyboardButton(
                f"{selected}{info['emoji']} {info['name']} ({coins_preview})",
                callback_data=f"spot:set_portfolio:{key}"
            )])
        buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="spot:back_to_main")])
        
        try:
            await q.edit_message_text(
                "📁 <b>Select Portfolio Preset</b>\n\n"
                "Choose a predefined portfolio or create your own custom allocation:",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="HTML"
            )
        except BadRequest:
            pass
        return
    
    if action.startswith("set_portfolio:"):
        portfolio_key = action.split(":")[1]
        if portfolio_key in SPOT_PORTFOLIOS:
            portfolio_info = SPOT_PORTFOLIOS[portfolio_key]
            spot_settings["portfolio"] = portfolio_key
            
            # If not custom, set coins from portfolio
            if portfolio_key != "custom" and portfolio_info.get("coins"):
                spot_settings["coins"] = list(portfolio_info["coins"].keys())
                spot_settings["allocation"] = portfolio_info["coins"].copy()
            
            db.set_user_field(uid, "spot_settings", json.dumps(spot_settings))
            await q.answer(f"Portfolio: {portfolio_info['name']}")
        
        cfg = db.get_user_config(uid)
        spot_settings = cfg.get("spot_settings", {})
        msg = format_spot_settings_message(t, cfg, spot_settings)
        keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
        try:
            await q.edit_message_text(msg, reply_markup=keyboard, parse_mode="HTML")
        except BadRequest:
            pass
        return
    
    if action == "strategy":
        # Show DCA strategy selection
        buttons = []
        current_strategy = spot_settings.get("strategy", "fixed")
        for key, info in SMART_DCA_STRATEGIES.items():
            selected = "✅ " if key == current_strategy else ""
            buttons.append([InlineKeyboardButton(
                f"{selected}{info['emoji']} {info['name']}",
                callback_data=f"spot:set_strategy:{key}"
            )])
        buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="spot:back_to_main")])
        
        strategies_help = (
            "🎯 <b>Select DCA Strategy</b>\n\n"
            "<b>📊 Fixed DCA:</b> Buy same amount at regular intervals\n\n"
            "<b>📈 Value Averaging:</b> Buy MORE when price is down, LESS when up. "
            "Automatically adjusts to maintain target growth.\n\n"
            "<b>😱 Fear & Greed:</b> Increases buy amount during extreme market fear "
            "(F&G Index < 25). Great for buying blood in the streets.\n\n"
            "<b>📉 Dip Buying:</b> Only triggers when price drops by X% from recent high. "
            "Waits for dips instead of buying at any price."
        )
        
        try:
            await q.edit_message_text(
                strategies_help,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="HTML"
            )
        except BadRequest:
            pass
        return
    
    if action.startswith("set_strategy:"):
        strategy_key = action.split(":")[1]
        if strategy_key in SMART_DCA_STRATEGIES:
            strategy_info = SMART_DCA_STRATEGIES[strategy_key]
            spot_settings["strategy"] = strategy_key
            db.set_user_field(uid, "spot_settings", json.dumps(spot_settings))
            await q.answer(f"Strategy: {strategy_info['name']}")
        
        cfg = db.get_user_config(uid)
        spot_settings = cfg.get("spot_settings", {})
        msg = format_spot_settings_message(t, cfg, spot_settings)
        keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
        try:
            await q.edit_message_text(msg, reply_markup=keyboard, parse_mode="HTML")
        except BadRequest:
            pass
        return
    
    if action == "tp_toggle":
        current = spot_settings.get("tp_enabled", False)
        spot_settings["tp_enabled"] = not current
        db.set_user_field(uid, "spot_settings", json.dumps(spot_settings))
        
        status = "✅ Auto TP enabled" if not current else "❌ Auto TP disabled"
        await q.answer(status)
        
        cfg = db.get_user_config(uid)
        spot_settings = cfg.get("spot_settings", {})
        msg = format_spot_settings_message(t, cfg, spot_settings)
        keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
        try:
            await q.edit_message_text(msg, reply_markup=keyboard, parse_mode="HTML")
        except BadRequest:
            pass
        return
    
    if action == "rebalance_toggle":
        current = spot_settings.get("rebalance_enabled", False)
        spot_settings["rebalance_enabled"] = not current
        db.set_user_field(uid, "spot_settings", json.dumps(spot_settings))
        
        status = "✅ Auto Rebalance enabled" if not current else "❌ Auto Rebalance disabled"
        await q.answer(status)
        
        cfg = db.get_user_config(uid)
        spot_settings = cfg.get("spot_settings", {})
        msg = format_spot_settings_message(t, cfg, spot_settings)
        keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
        try:
            await q.edit_message_text(msg, reply_markup=keyboard, parse_mode="HTML")
        except BadRequest:
            pass
        return
    
    if action == "tp_settings":
        # Show TP levels configuration
        tp_levels = spot_settings.get("tp_levels", DEFAULT_SPOT_TP_LEVELS)
        
        lines = [
            "🎯 <b>Take Profit Levels</b>",
            "",
            "Configure automatic sell targets:",
            "",
        ]
        for i, level in enumerate(tp_levels):
            lines.append(f"📍 At +{level['gain_pct']}% gain → Sell {level['sell_pct']}%")
        
        lines.extend([
            "",
            "<i>When coin reaches target gain, bot will automatically "
            "sell the specified percentage of holdings.</i>",
        ])
        
        buttons = [
            [
                InlineKeyboardButton("📝 Edit Level 1", callback_data="spot:edit_tp:0"),
                InlineKeyboardButton("📝 Edit Level 2", callback_data="spot:edit_tp:1"),
            ],
            [
                InlineKeyboardButton("📝 Edit Level 3", callback_data="spot:edit_tp:2"),
                InlineKeyboardButton("📝 Edit Level 4", callback_data="spot:edit_tp:3"),
            ],
            [InlineKeyboardButton("🔄 Reset to Default", callback_data="spot:reset_tp")],
            [InlineKeyboardButton("⬅️ Back", callback_data="spot:back_to_main")],
        ]
        
        try:
            await q.edit_message_text(
                "\n".join(lines),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="HTML"
            )
        except BadRequest:
            pass
        return
    
    if action == "reset_tp":
        spot_settings["tp_levels"] = DEFAULT_SPOT_TP_LEVELS.copy()
        db.set_user_field(uid, "spot_settings", json.dumps(spot_settings))
        await q.answer("TP levels reset to default")
        
        cfg = db.get_user_config(uid)
        spot_settings = cfg.get("spot_settings", {})
        msg = format_spot_settings_message(t, cfg, spot_settings)
        keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
        try:
            await q.edit_message_text(msg, reply_markup=keyboard, parse_mode="HTML")
        except BadRequest:
            pass
        return
    
    if action.startswith("edit_tp:"):
        # Edit specific TP level (0-3)
        level_idx = int(action.split(":")[1])
        tp_levels = spot_settings.get("tp_levels", DEFAULT_SPOT_TP_LEVELS.copy())
        
        if 0 <= level_idx < len(tp_levels):
            level = tp_levels[level_idx]
            ctx.user_data["spot_edit_tp_level"] = level_idx
            ctx.user_data["spot_awaiting"] = "tp_gain"
            
            try:
                await q.edit_message_text(
                    f"📝 <b>Edit TP Level {level_idx + 1}</b>\n\n"
                    f"Current settings:\n"
                    f"• Gain trigger: +{level['gain_pct']}%\n"
                    f"• Sell amount: {level['sell_pct']}%\n\n"
                    f"Enter new <b>gain trigger %</b> (e.g. 50 for +50%):",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ Cancel", callback_data="spot:tp_settings")]
                    ])
                )
            except BadRequest:
                pass
        return
    
    if action.startswith("tp_sell_pct:"):
        # Set sell percentage for TP level
        level_idx = ctx.user_data.get("spot_edit_tp_level", 0)
        ctx.user_data["spot_awaiting"] = "tp_sell"
        
        tp_levels = spot_settings.get("tp_levels", DEFAULT_SPOT_TP_LEVELS.copy())
        if 0 <= level_idx < len(tp_levels):
            level = tp_levels[level_idx]
            try:
                await q.edit_message_text(
                    f"📝 <b>Edit TP Level {level_idx + 1}</b>\n\n"
                    f"Gain trigger: +{level['gain_pct']}%\n\n"
                    f"Enter <b>sell amount %</b> (e.g. 25 to sell 25% of holdings):",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ Cancel", callback_data="spot:tp_settings")]
                    ])
                )
            except BadRequest:
                pass
        return
    
    if action == "sell_menu":
        # Show menu to select coin to sell
        account_type = spot_settings.get("trading_mode", "demo")
        balances = await fetch_spot_balance(uid, account_type=account_type)
        
        # Filter coins with balance > 0 (excluding stables)
        sellable = {coin: qty for coin, qty in balances.items() 
                   if qty > 0.00001 and coin not in ("USDT", "USDC", "BUSD", "DAI")}
        
        if not sellable:
            await q.answer("❌ No coins to sell", show_alert=True)
            return
        
        buttons = []
        for coin, qty in sorted(sellable.items()):
            # Get current price
            symbol = f"{coin}USDT"
            try:
                ticker = await get_spot_ticker(uid, symbol, account_type)
                price = float(ticker.get("lastPrice", 0)) if ticker else 0
                value = qty * price
                buttons.append([InlineKeyboardButton(
                    f"💸 {coin}: {qty:.6f} (${value:.2f})",
                    callback_data=f"spot:sell_coin:{coin}"
                )])
            except:
                buttons.append([InlineKeyboardButton(
                    f"💸 {coin}: {qty:.6f}",
                    callback_data=f"spot:sell_coin:{coin}"
                )])
        
        buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="spot:back_to_main")])
        
        try:
            await q.edit_message_text(
                "💸 <b>Select Coin to Sell</b>\n\n"
                "Choose a coin from your holdings:",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="HTML"
            )
        except BadRequest:
            pass
        return
    
    if action.startswith("sell_coin:"):
        coin = action.split(":")[1]
        
        # Show sell percentage options
        buttons = [
            [
                InlineKeyboardButton("25%", callback_data=f"spot:exec_sell:{coin}:25"),
                InlineKeyboardButton("50%", callback_data=f"spot:exec_sell:{coin}:50"),
            ],
            [
                InlineKeyboardButton("75%", callback_data=f"spot:exec_sell:{coin}:75"),
                InlineKeyboardButton("100%", callback_data=f"spot:exec_sell:{coin}:100"),
            ],
            [InlineKeyboardButton("⬅️ Back", callback_data="spot:sell_menu")],
        ]
        
        try:
            await q.edit_message_text(
                f"💸 <b>Sell {coin}</b>\n\n"
                "Select percentage to sell:",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="HTML"
            )
        except BadRequest:
            pass
        return
    
    if action.startswith("exec_sell:"):
        parts = action.split(":")
        coin = parts[1]
        sell_pct = float(parts[2])
        account_type = spot_settings.get("trading_mode", "demo")
        
        await q.answer(f"Selling {sell_pct}% of {coin}...")
        
        result = await execute_spot_sell(uid, coin, sell_pct=sell_pct, account_type=account_type)
        
        if result.get("success"):
            msg_text = (
                f"✅ <b>Sold {coin}</b>\n\n"
                f"Qty: {result.get('qty_sold', 0):.6f} {coin}\n"
                f"Price: ${result.get('price', 0):.4f}\n"
                f"Received: ${result.get('usdt_received', 0):.2f} USDT"
            )
        else:
            msg_text = f"❌ <b>Sell Failed</b>\n\n{result.get('error', 'Unknown error')}"
        
        cfg = db.get_user_config(uid)
        spot_settings = cfg.get("spot_settings", {})
        keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
        
        try:
            await q.edit_message_text(msg_text, reply_markup=keyboard, parse_mode="HTML")
        except BadRequest:
            pass
        return
    
    if action == "rebalance_now":
        account_type = spot_settings.get("trading_mode", "demo")
        
        await q.answer("Rebalancing portfolio...")
        
        result = await rebalance_spot_portfolio(uid, account_type=account_type)
        
        if result.get("success"):
            sells = result.get("sells", [])
            buys = result.get("buys", [])
            total = result.get("total_rebalanced", 0)
            
            lines = ["⚖️ <b>Portfolio Rebalanced</b>", ""]
            
            if sells:
                lines.append("<b>Sold:</b>")
                lines.extend([f"  • {s}" for s in sells])
                lines.append("")
            
            if buys:
                lines.append("<b>Bought:</b>")
                lines.extend([f"  • {b}" for b in buys])
                lines.append("")
            
            if not sells and not buys:
                lines.append("✅ Portfolio already balanced!")
            else:
                lines.append(f"💰 Total rebalanced: ${total:.2f}")
            
            msg_text = "\n".join(lines)
        else:
            msg_text = f"❌ <b>Rebalance Failed</b>\n\n{result.get('error', 'Unknown error')}"
        
        cfg = db.get_user_config(uid)
        spot_settings = cfg.get("spot_settings", {})
        keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
        
        try:
            await q.edit_message_text(msg_text, reply_markup=keyboard, parse_mode="HTML")
        except BadRequest:
            pass
        return
    
    if action == "analysis":
        # Show market analysis for selected coins
        await q.answer("Analyzing market...")
        
        coins = spot_settings.get("coins", SPOT_DCA_COINS)
        account_type = spot_settings.get("trading_mode", "demo")
        
        lines = ["📊 <b>Market Analysis</b>", ""]
        
        # Fetch Fear & Greed Index (simulated for now, can integrate real API)
        fear_greed = await get_fear_greed_index()
        fg_emoji = "😱" if fear_greed < 25 else "😰" if fear_greed < 45 else "😐" if fear_greed < 55 else "😀" if fear_greed < 75 else "🤑"
        fg_label = "Extreme Fear" if fear_greed < 25 else "Fear" if fear_greed < 45 else "Neutral" if fear_greed < 55 else "Greed" if fear_greed < 75 else "Extreme Greed"
        
        lines.append(f"<b>Fear & Greed Index:</b> {fg_emoji} {fear_greed} ({fg_label})")
        lines.append("")
        
        # Get price data for coins
        for coin in coins[:5]:  # Limit to 5 coins
            symbol = f"{coin}USDT"
            try:
                ticker = await get_spot_ticker(uid, symbol, account_type)
                if ticker:
                    price = float(ticker.get("lastPrice", 0))
                    change_24h = float(ticker.get("price24hPcnt", 0)) * 100
                    change_emoji = "📈" if change_24h > 0 else "📉"
                    lines.append(f"{change_emoji} <b>{coin}:</b> ${price:.4f} ({change_24h:+.2f}%)")
            except Exception:
                lines.append(f"⚠️ <b>{coin}:</b> Data unavailable")
        
        lines.extend([
            "",
            "<i>💡 Tip: Buy more during Extreme Fear!</i>",
        ])
        
        cfg = db.get_user_config(uid)
        spot_settings = cfg.get("spot_settings", {})
        msg_base = format_spot_settings_message(t, cfg, spot_settings)
        keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
        
        try:
            await q.edit_message_text(
                msg_base + "\n\n" + "\n".join(lines),
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except BadRequest:
            pass
        return
    
    if action == "performance":
        # Show portfolio performance
        account_type = spot_settings.get("trading_mode", "demo")
        total_invested = spot_settings.get("total_invested", 0.0)
        
        balances = await fetch_spot_balance(uid, account_type=account_type)
        
        lines = ["📈 <b>Portfolio Performance</b>", ""]
        
        total_value = 0.0
        holdings_lines = []
        
        for coin, qty in sorted(balances.items()):
            if qty > 0.00001 and coin != "USDT":
                symbol = f"{coin}USDT"
                try:
                    ticker = await get_spot_ticker(uid, symbol, account_type)
                    if ticker:
                        price = float(ticker.get("lastPrice", 0))
                        value = qty * price
                        total_value += value
                        holdings_lines.append(f"• {coin}: {qty:.6f} (${value:.2f})")
                except Exception:
                    holdings_lines.append(f"• {coin}: {qty:.6f}")
        
        # Add USDT balance
        usdt_balance = balances.get("USDT", 0)
        if usdt_balance > 0.01:
            total_value += usdt_balance
            holdings_lines.append(f"• USDT: {usdt_balance:.2f}")
        
        for line in holdings_lines:
            lines.append(line)
        
        lines.append("")
        lines.append(f"💰 <b>Total Value:</b> ${total_value:.2f}")
        lines.append(f"💵 <b>Total Invested:</b> ${total_invested:.2f}")
        
        if total_invested > 0:
            pnl = total_value - total_invested
            pnl_pct = (pnl / total_invested) * 100
            pnl_emoji = "🟢" if pnl >= 0 else "🔴"
            lines.append(f"{pnl_emoji} <b>P&L:</b> ${pnl:.2f} ({pnl_pct:+.2f}%)")
        
        cfg = db.get_user_config(uid)
        spot_settings = cfg.get("spot_settings", {})
        msg_base = format_spot_settings_message(t, cfg, spot_settings)
        keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
        
        try:
            await q.edit_message_text(
                msg_base + "\n\n" + "\n".join(lines),
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except BadRequest:
            pass
        return
    
    # === END NEW PROFESSIONAL SPOT FEATURES ===
    
    # ==================== TRAILING TP ====================
    if action == "trailing_toggle":
        trailing_config = spot_settings.get("trailing_tp", SPOT_TRAILING_TP_DEFAULTS.copy())
        trailing_config["enabled"] = not trailing_config.get("enabled", False)
        spot_settings["trailing_tp"] = trailing_config
        db.set_user_field(uid, "spot_settings", json.dumps(spot_settings))
        
        status = "enabled" if trailing_config["enabled"] else "disabled"
        await q.answer(f"📈 Trailing TP {status}!", show_alert=True)
        
        cfg = db.get_user_config(uid)
        spot_settings = cfg.get("spot_settings", {})
        msg = format_spot_settings_message(t, cfg, spot_settings)
        keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
        try:
            await q.edit_message_text(msg, reply_markup=keyboard, parse_mode="HTML")
        except BadRequest:
            pass
        return
    
    # ==================== PORTFOLIO STATS ====================
    if action == "portfolio_stats":
        await q.answer("Loading portfolio stats...")
        account_type = spot_settings.get("trading_mode", "demo")
        
        stats = await get_spot_portfolio_stats(uid, account_type=account_type)
        
        lines = ["📊 <b>Portfolio Statistics</b>", ""]
        
        # Overall stats
        lines.append(f"💰 <b>Total Value:</b> ${stats['total_current_value']:.2f}")
        lines.append(f"💵 <b>Cost Basis:</b> ${stats['total_cost_basis']:.2f}")
        lines.append(f"🏦 <b>USDT Available:</b> ${stats['usdt_balance']:.2f}")
        lines.append("")
        
        pnl = stats['overall_pnl_value']
        pnl_pct = stats['overall_pnl_pct']
        pnl_emoji = "🟢" if pnl >= 0 else "🔴"
        lines.append(f"{pnl_emoji} <b>Overall P&L:</b> ${pnl:.2f} ({pnl_pct:+.2f}%)")
        lines.append("")
        
        # Per-coin breakdown
        if stats['coins']:
            lines.append("<b>📈 Coins Breakdown:</b>")
            for coin_stat in stats['coins'][:8]:  # Top 8 coins
                coin = coin_stat['coin']
                value = coin_stat['current_value']
                coin_pnl = coin_stat['pnl_pct']
                emoji = "🟢" if coin_pnl >= 0 else "🔴"
                lines.append(f"  {emoji} {coin}: ${value:.2f} ({coin_pnl:+.1f}%)")
        
        lines.append("")
        lines.append(f"📊 <b>Total Invested:</b> ${stats.get('total_invested', 0):.2f}")
        
        buttons = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="spot:portfolio_stats")],
            [InlineKeyboardButton("⬅️ Back", callback_data="spot:back_to_main")],
        ]
        
        try:
            await q.edit_message_text(
                "\n".join(lines),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="HTML"
            )
        except BadRequest:
            pass
        return
    
    # ==================== PERFORMANCE (DCA History) ====================
    if action == "performance":
        await q.answer("Loading performance...")
        account_type = spot_settings.get("trading_mode", "demo")
        purchase_history = spot_settings.get("purchase_history", {})
        total_invested = spot_settings.get("total_invested", 0)
        last_dca_ts = spot_settings.get("last_dca_ts", 0)
        
        lines = ["📈 <b>DCA Performance</b>", ""]
        
        # Summary
        lines.append(f"💵 <b>Total Invested:</b> ${total_invested:.2f}")
        if last_dca_ts:
            from datetime import datetime
            last_dca_date = datetime.fromtimestamp(last_dca_ts).strftime("%Y-%m-%d %H:%M")
            lines.append(f"⏰ <b>Last DCA:</b> {last_dca_date}")
        lines.append("")
        
        # Per-coin history
        if purchase_history:
            lines.append("<b>🪙 Purchase History:</b>")
            for coin, history in sorted(purchase_history.items()):
                total_qty = history.get("total_qty", 0)
                avg_price = history.get("avg_price", 0)
                total_cost = history.get("total_cost", 0)
                buy_count = len(history.get("purchases", []))
                
                if total_qty > 0:
                    lines.append(f"  • {coin}: {total_qty:.6f} @ avg ${avg_price:.4f}")
                    lines.append(f"    Cost: ${total_cost:.2f} ({buy_count} buys)")
        else:
            lines.append("<i>No DCA purchases yet. Use 'Buy Now' to start.</i>")
        
        # DCA frequency info
        lines.append("")
        freq = spot_settings.get("frequency", "manual")
        auto_dca = spot_settings.get("auto_dca", False)
        lines.append(f"⚙️ <b>Mode:</b> {freq.title()}" + (" (Auto)" if auto_dca else " (Manual)"))
        
        buttons = [
            [InlineKeyboardButton("📊 Portfolio Stats", callback_data="spot:portfolio_stats")],
            [InlineKeyboardButton("⬅️ Back", callback_data="spot:back_to_main")],
        ]
        
        try:
            await q.edit_message_text(
                "\n".join(lines),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="HTML"
            )
        except BadRequest:
            pass
        return
    
    # ==================== LIMIT ORDERS ====================
    if action == "limit_order":
        coins = spot_settings.get("coins", SPOT_DCA_COINS)
        
        buttons = []
        for coin in coins:
            buttons.append([InlineKeyboardButton(
                f"📋 {coin} Limit Order",
                callback_data=f"spot:limit_setup:{coin}"
            )])
        buttons.append([InlineKeyboardButton("📋 View Open Orders", callback_data="spot:limit_view")])
        buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="spot:back_to_main")])
        
        try:
            await q.edit_message_text(
                "📋 <b>Spot Limit Orders</b>\n\n"
                "Place limit buy orders at specific prices.\n"
                "Select a coin to set up a limit order:",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="HTML"
            )
        except BadRequest:
            pass
        return
    
    if action.startswith("limit_setup:"):
        coin = action.split(":")[1]
        ctx.user_data["spot_limit_coin"] = coin
        ctx.user_data["spot_awaiting"] = "limit_price"
        
        account_type = spot_settings.get("trading_mode", "demo")
        symbol = f"{coin}USDT"
        
        # Get current price
        current_price = 0
        try:
            ticker = await get_spot_ticker(uid, symbol, account_type)
            if ticker:
                current_price = float(ticker.get("lastPrice", 0))
        except:
            pass
        
        try:
            await q.edit_message_text(
                f"📋 <b>Limit Buy {coin}</b>\n\n"
                f"💰 Current price: ${current_price:.4f}\n\n"
                f"Enter the price at which you want to buy {coin}:",
                parse_mode="HTML"
            )
        except BadRequest:
            pass
        return
    
    if action == "limit_view":
        account_type = spot_settings.get("trading_mode", "demo")
        
        orders = await get_spot_open_orders(uid, account_type)
        
        if not orders:
            try:
                await q.edit_message_text(
                    "📋 <b>Open Limit Orders</b>\n\n"
                    "No open orders.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ Back", callback_data="spot:limit_order")]
                    ]),
                    parse_mode="HTML"
                )
            except BadRequest:
                pass
            return
        
        lines = ["📋 <b>Open Limit Orders</b>", ""]
        buttons = []
        
        for order in orders[:10]:  # Limit to 10
            symbol = order.get("symbol", "")
            side = order.get("side", "")
            price = float(order.get("price", 0))
            qty = float(order.get("qty", 0))
            order_id = order.get("orderId", "")
            
            side_emoji = "🟢" if side == "Buy" else "🔴"
            lines.append(f"{side_emoji} {symbol}: {qty:.6f} @ ${price:.4f}")
            
            buttons.append([InlineKeyboardButton(
                f"❌ Cancel {symbol[:6]}",
                callback_data=f"spot:limit_cancel:{symbol}:{order_id}"
            )])
        
        buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="spot:limit_order")])
        
        try:
            await q.edit_message_text(
                "\n".join(lines),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="HTML"
            )
        except BadRequest:
            pass
        return
    
    if action.startswith("limit_cancel:"):
        parts = action.split(":")
        symbol = parts[1]
        order_id = parts[2]
        account_type = spot_settings.get("trading_mode", "demo")
        
        result = await cancel_spot_order(uid, symbol, order_id, account_type)
        
        if result.get("success"):
            await q.answer("✅ Order cancelled!", show_alert=True)
        else:
            await q.answer(f"❌ Failed: {result.get('error', 'Unknown')}", show_alert=True)
        
        # Refresh order list
        orders = await get_spot_open_orders(uid, account_type)
        
        if not orders:
            try:
                await q.edit_message_text(
                    "📋 <b>Open Limit Orders</b>\n\n"
                    "No open orders.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ Back", callback_data="spot:limit_order")]
                    ]),
                    parse_mode="HTML"
                )
            except BadRequest:
                pass
            return
        
        lines = ["📋 <b>Open Limit Orders</b>", ""]
        buttons = []
        
        for order in orders[:10]:
            symbol = order.get("symbol", "")
            side = order.get("side", "")
            price = float(order.get("price", 0))
            qty = float(order.get("qty", 0))
            oid = order.get("orderId", "")
            
            side_emoji = "🟢" if side == "Buy" else "🔴"
            lines.append(f"{side_emoji} {symbol}: {qty:.6f} @ ${price:.4f}")
            buttons.append([InlineKeyboardButton(f"❌ Cancel {symbol[:6]}", callback_data=f"spot:limit_cancel:{symbol}:{oid}")])
        
        buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="spot:limit_order")])
        
        try:
            await q.edit_message_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
        except BadRequest:
            pass
        return
    
    # ==================== GRID BOT ====================
    if action == "grid_menu":
        coins = spot_settings.get("coins", SPOT_DCA_COINS)
        grids = spot_settings.get("grids", {})
        
        lines = ["🔲 <b>Spot Grid Bot</b>", ""]
        
        # Show active grids
        active_grids = [c for c, g in grids.items() if g.get("active")]
        if active_grids:
            lines.append("<b>Active Grids:</b>")
            for coin in active_grids:
                grid = grids[coin]
                profit = grid.get("realized_profit", 0)
                trades = grid.get("trades_count", 0)
                lines.append(f"  ✅ {coin}: ${profit:.2f} profit ({trades} trades)")
            lines.append("")
        
        lines.append("Select a coin to set up grid trading:")
        
        buttons = []
        for coin in coins:
            is_active = coin in active_grids
            emoji = "✅" if is_active else "➕"
            action_text = "Stop" if is_active else "Setup"
            buttons.append([InlineKeyboardButton(
                f"{emoji} {coin} Grid ({action_text})",
                callback_data=f"spot:grid_coin:{coin}"
            )])
        
        buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="spot:back_to_main")])
        
        try:
            await q.edit_message_text(
                "\n".join(lines),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="HTML"
            )
        except BadRequest:
            pass
        return
    
    if action.startswith("grid_coin:"):
        coin = action.split(":")[1]
        grids = spot_settings.get("grids", {})
        
        if coin in grids and grids[coin].get("active"):
            # Grid is active - show stop option
            grid = grids[coin]
            profit = grid.get("realized_profit", 0)
            trades = grid.get("trades_count", 0)
            
            buttons = [
                [InlineKeyboardButton("🛑 Stop Grid", callback_data=f"spot:grid_stop:{coin}")],
                [InlineKeyboardButton("⬅️ Back", callback_data="spot:grid_menu")],
            ]
            
            try:
                await q.edit_message_text(
                    f"🔲 <b>{coin} Grid Active</b>\n\n"
                    f"💰 Profit: ${profit:.2f}\n"
                    f"📊 Trades: {trades}\n"
                    f"📈 Range: ${grid.get('price_low', 0):.2f} - ${grid.get('price_high', 0):.2f}\n"
                    f"🔢 Levels: {grid.get('grid_count', 0)}",
                    reply_markup=InlineKeyboardMarkup(buttons),
                    parse_mode="HTML"
                )
            except BadRequest:
                pass
        else:
            # Setup new grid
            ctx.user_data["spot_grid_coin"] = coin
            ctx.user_data["spot_awaiting"] = "grid_range"
            
            account_type = spot_settings.get("trading_mode", "demo")
            symbol = f"{coin}USDT"
            
            current_price = 0
            try:
                ticker = await get_spot_ticker(uid, symbol, account_type)
                if ticker:
                    current_price = float(ticker.get("lastPrice", 0))
            except:
                pass
            
            try:
                await q.edit_message_text(
                    f"🔲 <b>Setup {coin} Grid</b>\n\n"
                    f"💰 Current price: ${current_price:.4f}\n\n"
                    f"Enter grid parameters:\n"
                    f"<code>low_price high_price grid_count total_usdt</code>\n\n"
                    f"Example: <code>{current_price*0.9:.2f} {current_price*1.1:.2f} 10 100</code>",
                    parse_mode="HTML"
                )
            except BadRequest:
                pass
        return
    
    if action.startswith("grid_stop:"):
        coin = action.split(":")[1]
        account_type = spot_settings.get("trading_mode", "demo")
        
        result = await stop_spot_grid(uid, coin, account_type)
        
        if result.get("success"):
            msg = (
                f"🛑 <b>{coin} Grid Stopped</b>\n\n"
                f"📊 Total Trades: {result.get('total_trades', 0)}\n"
                f"💰 Total Profit: ${result.get('total_profit', 0):.2f}\n"
                f"❌ Orders Cancelled: {result.get('orders_cancelled', 0)}"
            )
            await q.answer("Grid stopped!")
        else:
            msg = f"❌ Failed to stop grid: {result.get('error', 'Unknown')}"
        
        buttons = [[InlineKeyboardButton("⬅️ Back", callback_data="spot:grid_menu")]]
        
        try:
            await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
        except BadRequest:
            pass
        return
    
    if action == "back":
        await q.message.delete()
        await ctx.bot.send_message(
            chat_id=uid,
            text=t["welcome"],
            reply_markup=main_menu_keyboard(ctx, update=update)
        )
        return


@with_texts
@log_calls
async def handle_spot_text_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle text input for Spot settings (e.g., DCA amount).
    Returns True if handled, False otherwise.
    """
    if not ctx.user_data.get("spot_awaiting"):
        return False
    
    uid = update.effective_user.id
    t = ctx.t
    text = update.message.text.strip()
    awaiting = ctx.user_data.pop("spot_awaiting", None)
    
    if awaiting == "amount":
        try:
            amount = float(text)
            if amount < 1:
                await update.message.reply_text(t.get("min_amount_error", "❌ Minimum amount is 1 USDT"))
                return True
            if amount > 100000:
                await update.message.reply_text(t.get("max_amount_error", "❌ Maximum amount is 100,000 USDT"))
                return True
            
            cfg = db.get_user_config(uid)
            spot_settings = cfg.get("spot_settings", {})
            spot_settings["dca_amount"] = amount
            db.set_user_field(uid, "spot_settings", json.dumps(spot_settings))
            
            await update.message.reply_text(
                t.get("spot_amount_saved", "✅ DCA amount set to {amount} USDT").format(amount=amount)
            )
            
            # Show updated settings
            cfg = db.get_user_config(uid)
            spot_settings = cfg.get("spot_settings", {})
            msg = format_spot_settings_message(t, cfg, spot_settings)
            keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
            await update.message.reply_text(msg, reply_markup=keyboard, parse_mode="HTML")
            
            return True
        except ValueError:
            await update.message.reply_text(t.get("invalid_amount", "❌ Invalid number. Please enter a valid amount."))
            return True
    
    if awaiting == "tp_gain":
        # Handle TP gain percentage input
        try:
            gain_pct = float(text)
            if gain_pct < 1:
                await update.message.reply_text("❌ Minimum gain trigger is 1%")
                return True
            if gain_pct > 10000:
                await update.message.reply_text("❌ Maximum gain trigger is 10000%")
                return True
            
            level_idx = ctx.user_data.get("spot_edit_tp_level", 0)
            cfg = db.get_user_config(uid)
            spot_settings = cfg.get("spot_settings", {})
            tp_levels = spot_settings.get("tp_levels", DEFAULT_SPOT_TP_LEVELS.copy())
            
            if 0 <= level_idx < len(tp_levels):
                tp_levels[level_idx]["gain_pct"] = gain_pct
                spot_settings["tp_levels"] = tp_levels
                db.set_user_field(uid, "spot_settings", json.dumps(spot_settings))
            
            # Now ask for sell percentage
            ctx.user_data["spot_awaiting"] = "tp_sell"
            await update.message.reply_text(
                f"✅ Gain trigger set to +{gain_pct}%\n\n"
                f"Now enter <b>sell amount %</b> (how much to sell when triggered):",
                parse_mode="HTML"
            )
            return True
        except ValueError:
            await update.message.reply_text("❌ Invalid number. Please enter a valid percentage (e.g. 50)")
            return True
    
    if awaiting == "tp_sell":
        # Handle TP sell percentage input
        try:
            sell_pct = float(text)
            if sell_pct < 1:
                await update.message.reply_text("❌ Minimum sell amount is 1%")
                return True
            if sell_pct > 100:
                await update.message.reply_text("❌ Maximum sell amount is 100%")
                return True
            
            level_idx = ctx.user_data.pop("spot_edit_tp_level", 0)
            cfg = db.get_user_config(uid)
            spot_settings = cfg.get("spot_settings", {})
            tp_levels = spot_settings.get("tp_levels", DEFAULT_SPOT_TP_LEVELS.copy())
            
            if 0 <= level_idx < len(tp_levels):
                tp_levels[level_idx]["sell_pct"] = sell_pct
                spot_settings["tp_levels"] = tp_levels
                db.set_user_field(uid, "spot_settings", json.dumps(spot_settings))
            
            # Show updated TP levels
            lines = [
                "✅ <b>TP Level Updated!</b>",
                "",
                "🎯 <b>Current TP Levels:</b>",
                "",
            ]
            for i, level in enumerate(tp_levels):
                marker = "📍" if i == level_idx else "•"
                lines.append(f"{marker} At +{level['gain_pct']}% → Sell {level['sell_pct']}%")
            
            buttons = [
                [InlineKeyboardButton("⬅️ Back to TP Settings", callback_data="spot:tp_settings")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="spot:back_to_main")],
            ]
            
            await update.message.reply_text(
                "\n".join(lines),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="HTML"
            )
            return True
        except ValueError:
            await update.message.reply_text("❌ Invalid number. Please enter a valid percentage (e.g. 25)")
            return True
    
    # ==================== LIMIT ORDER INPUT ====================
    if awaiting == "limit_price":
        try:
            limit_price = float(text)
            if limit_price <= 0:
                await update.message.reply_text("❌ Price must be positive")
                return True
            
            ctx.user_data["spot_limit_price"] = limit_price
            ctx.user_data["spot_awaiting"] = "limit_amount"
            
            coin = ctx.user_data.get("spot_limit_coin", "BTC")
            await update.message.reply_text(
                f"📋 <b>Limit Buy {coin}</b>\n\n"
                f"💰 Price: ${limit_price:.4f}\n\n"
                f"Enter USDT amount to invest:",
                parse_mode="HTML"
            )
            return True
        except ValueError:
            await update.message.reply_text("❌ Invalid price. Please enter a number.")
            return True
    
    if awaiting == "limit_amount":
        try:
            amount = float(text)
            if amount < 5:
                await update.message.reply_text("❌ Minimum amount is 5 USDT")
                return True
            
            coin = ctx.user_data.pop("spot_limit_coin", "BTC")
            limit_price = ctx.user_data.pop("spot_limit_price", 0)
            
            cfg = db.get_user_config(uid)
            spot_settings = cfg.get("spot_settings", {})
            account_type = spot_settings.get("trading_mode", "demo")
            
            result = await place_spot_limit_order(
                user_id=uid,
                coin=coin,
                side="Buy",
                price=limit_price,
                usdt_amount=amount,
                account_type=account_type,
            )
            
            if result.get("success"):
                msg = (
                    f"✅ <b>Limit Order Placed!</b>\n\n"
                    f"🪙 {coin}\n"
                    f"💰 Price: ${limit_price:.4f}\n"
                    f"📦 Amount: {result.get('qty', 0):.6f}\n"
                    f"💵 Investment: ${amount:.2f}"
                )
            else:
                msg = f"❌ <b>Failed to place order</b>\n\n{result.get('error', 'Unknown error')}"
            
            buttons = [
                [InlineKeyboardButton("📋 View Orders", callback_data="spot:limit_view")],
                [InlineKeyboardButton("⬅️ Back", callback_data="spot:limit_order")],
            ]
            
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
            return True
        except ValueError:
            await update.message.reply_text("❌ Invalid amount. Please enter a number.")
            return True
    
    # ==================== GRID BOT INPUT ====================
    if awaiting == "grid_range":
        try:
            parts = text.split()
            if len(parts) != 4:
                await update.message.reply_text(
                    "❌ Invalid format. Please enter:\n"
                    "<code>low_price high_price grid_count total_usdt</code>",
                    parse_mode="HTML"
                )
                return True
            
            price_low = float(parts[0])
            price_high = float(parts[1])
            grid_count = int(parts[2])
            total_investment = float(parts[3])
            
            if price_low >= price_high:
                await update.message.reply_text("❌ Low price must be less than high price")
                return True
            if grid_count < 3 or grid_count > 50:
                await update.message.reply_text("❌ Grid count must be between 3 and 50")
                return True
            if total_investment < 10:
                await update.message.reply_text("❌ Minimum investment is 10 USDT")
                return True
            
            coin = ctx.user_data.pop("spot_grid_coin", "BTC")
            
            cfg = db.get_user_config(uid)
            spot_settings = cfg.get("spot_settings", {})
            account_type = spot_settings.get("trading_mode", "demo")
            
            await update.message.reply_text(f"⏳ Setting up {coin} grid...")
            
            result = await setup_spot_grid(
                user_id=uid,
                coin=coin,
                price_low=price_low,
                price_high=price_high,
                grid_count=grid_count,
                total_investment=total_investment,
                account_type=account_type,
            )
            
            if result.get("success"):
                msg = (
                    f"✅ <b>{coin} Grid Bot Started!</b>\n\n"
                    f"📈 Range: ${price_low:.2f} - ${price_high:.2f}\n"
                    f"🔢 Levels: {grid_count}\n"
                    f"💵 Investment: ${total_investment:.2f}\n"
                    f"📊 Orders placed: {result.get('orders_placed', 0)}\n"
                    f"📍 Grid step: ${result.get('grid_step', 0):.4f}"
                )
            else:
                msg = f"❌ <b>Failed to setup grid</b>\n\n{result.get('error', 'Unknown error')}"
            
            buttons = [
                [InlineKeyboardButton("🔲 Grid Menu", callback_data="spot:grid_menu")],
                [InlineKeyboardButton("⬅️ Back", callback_data="spot:back_to_main")],
            ]
            
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
            return True
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid input. Please enter numbers:\n"
                "<code>low_price high_price grid_count total_usdt</code>",
                parse_mode="HTML"
            )
            return True
    
    return False


def _clean(x: float) -> float:
    return float(f"{x:.12f}")

def quantize(value: float, step: float) -> float:
    return _clean(floor(value / step) * step)

def quantize_up(value: float, step: float) -> float:
    return _clean(math.ceil(value / step) * step)

def _decimals_from_step(step: float) -> int:
    s = f"{step:.16f}".rstrip("0")
    if "." in s:
        return len(s.split(".")[1])
    return 0

def resolve_sl_tp_pct(cfg: dict, symbol: str, strategy: str | None = None, user_id: int | None = None, side: str | None = None) -> tuple[float, float]:
    """
    Resolve SL/TP percentages for a trade.
    If strategy is provided and user has per-strategy settings, use those.
    For ALL strategies, side-specific settings (long_sl_percent, short_sl_percent) take priority if side is provided.
    Otherwise fallback to global user settings, then coin-specific defaults.
    
    Uses user's current exchange/account context for strategy settings lookup.
    """
    coin_cfg = COIN_PARAMS.get(symbol, COIN_PARAMS["DEFAULT"])

    # Try to get per-strategy settings if available
    strat_sl = None
    strat_tp = None
    if strategy and user_id:
        # Get user's current exchange/account context
        context = get_user_trading_context(user_id)
        strat_settings = db.get_strategy_settings(
            user_id, strategy, 
            context["exchange"], 
            context["account_type"]
        )
        
        # For ALL strategies, check side-specific settings first if side is provided
        if side:
            side_prefix = "long" if side in ("Buy", "LONG", "long") else "short"
            side_sl = strat_settings.get(f"{side_prefix}_sl_percent")
            side_tp = strat_settings.get(f"{side_prefix}_tp_percent")
            
            if side_sl is not None and side_sl > 0:
                strat_sl = side_sl
            if side_tp is not None and side_tp > 0:
                strat_tp = side_tp
        
        # Fallback to general strategy settings if side-specific not set
        if strat_sl is None:
            strat_sl = strat_settings.get("sl_percent")
        if strat_tp is None:
            strat_tp = strat_settings.get("tp_percent")

    # Priority: strategy settings > user global settings > coin defaults
    # SL
    user_sl = cfg.get("sl_percent") or 0
    if strat_sl is not None and 0 < strat_sl <= 50:
        sl_pct = float(strat_sl)
        logger.debug(f"[SL-RESOLVE] uid={user_id}, strategy={strategy}, strat_sl={strat_sl}, user_sl={user_sl}, sl_pct={sl_pct} (from strategy settings)")
    elif 0 < user_sl <= 50:
        sl_pct = float(user_sl)
        logger.debug(f"[SL-RESOLVE] uid={user_id}, strategy={strategy}, strat_sl={strat_sl}, user_sl={user_sl}, sl_pct={sl_pct} (from user global)")
    else:
        sl_pct = float(coin_cfg.get("sl_pct", DEFAULT_SL_PCT))
        logger.debug(f"[SL-RESOLVE] uid={user_id}, strategy={strategy}, strat_sl={strat_sl}, user_sl={user_sl}, sl_pct={sl_pct} (from coin defaults)")

    # TP
    if strat_tp is not None and float(strat_tp) > sl_pct:
        tp_pct = float(strat_tp)
    else:
        user_tp = cfg.get("tp_percent") or 0
        if float(user_tp) > sl_pct:
            tp_pct = float(user_tp)
        else:
            tp_pct = float(coin_cfg.get("tp_pct", DEFAULT_TP_PCT))

    return sl_pct, tp_pct


def get_strategy_trade_params(uid: int, cfg: dict, symbol: str, strategy: str, side: str = None,
                              exchange: str = None, account_type: str = None) -> dict:
    """
    Get trading parameters for a specific strategy.
    Returns dict with: percent (risk%), sl_pct, tp_pct, use_atr
    Falls back to global user settings if per-strategy not set.
    
    For ALL strategies, if side is provided, uses side-specific settings (long_percent, short_sl_percent, etc.)
    
    Args:
        uid: User ID
        cfg: User config dict
        symbol: Trading symbol
        strategy: Strategy name
        side: 'Buy' or 'Sell' for side-specific settings
        exchange: 'bybit' or 'hyperliquid' (auto-detected if None)
        account_type: 'demo', 'real', 'testnet', 'mainnet' (auto-detected if None)
    """
    # Auto-detect context if not provided
    if exchange is None or account_type is None:
        context = get_user_trading_context(uid)
        exchange = exchange or context["exchange"]
        account_type = account_type or context["account_type"]
    
    strat_settings = db.get_strategy_settings(uid, strategy, exchange, account_type)
    
    # Determine use_atr: strategy-specific takes priority over global
    strat_use_atr = strat_settings.get("use_atr")
    if strat_use_atr is not None:
        use_atr = bool(strat_use_atr)
    else:
        use_atr = bool(cfg.get("use_atr", 1))  # Default to ATR enabled
    
    # For ALL strategies, check for side-specific settings first if side is provided
    if side:
        side_prefix = "long" if side == "Buy" else "short"
        
        # Get side-specific percent
        side_percent = strat_settings.get(f"{side_prefix}_percent")
        if side_percent is not None and side_percent > 0:
            percent = float(side_percent)
        else:
            # Fallback to general strategy percent, then global
            strat_percent = strat_settings.get("percent")
            if strat_percent is not None and strat_percent > 0:
                percent = float(strat_percent)
            else:
                percent = float(cfg.get("percent", 1))
        
        # Get side-specific SL
        side_sl = strat_settings.get(f"{side_prefix}_sl_percent")
        if side_sl is not None and side_sl > 0:
            sl_pct = float(side_sl)
        else:
            sl_pct, _ = resolve_sl_tp_pct(cfg, symbol, strategy=strategy, user_id=uid, side=side)
        
        # Get side-specific TP
        side_tp = strat_settings.get(f"{side_prefix}_tp_percent")
        if side_tp is not None and side_tp > 0:
            tp_pct = float(side_tp)
        else:
            _, tp_pct = resolve_sl_tp_pct(cfg, symbol, strategy=strategy, user_id=uid, side=side)
        
        return {
            "percent": percent,
            "sl_pct": sl_pct,
            "tp_pct": tp_pct,
            "use_atr": use_atr,
        }
    
    # Default behavior when side is not provided
    # Get percent (risk)
    strat_percent = strat_settings.get("percent")
    if strat_percent is not None and strat_percent > 0:
        percent = float(strat_percent)
    else:
        percent = float(cfg.get("percent", 1))
    
    # Get SL/TP using resolve function with strategy awareness
    sl_pct, tp_pct = resolve_sl_tp_pct(cfg, symbol, strategy=strategy, user_id=uid)
    
    return {
        "percent": percent,
        "sl_pct": sl_pct,
        "tp_pct": tp_pct,
        "use_atr": use_atr,
    }


def _sign_payload(ts, api_key, secret, recv_window, body_json, query):
    base = ts + api_key + recv_window
    to_sign = base + (query or "") + (body_json or "")
    return hmac.new(secret.encode(), to_sign.encode(), hashlib.sha256).hexdigest()


def classify_headline(headline: str) -> str:
    text = headline.lower()
    words = set(re.findall(r'\w+', text))
    if words & NEGATIVE_KEYWORDS:
        return 'bad'
    if words & POSITIVE_KEYWORDS:
        return 'good'
    return 'neutral'

def _to_float_num(s: str) -> float:
    return float(s.replace(",", ".").strip())

def parse_manual(parts: list[str], typ: str):
    if typ == 'Limit':
        if len(parts) != 4:
            raise ValueError("Limit: 4 arguments required (SYMBOL SIDE PRICE QTY)")
        symbol, side_str, price_s, qty_s = parts
        price = _to_float_num(price_s)
        qty   = _to_float_num(qty_s)
    else:
        if len(parts) != 3:
            raise ValueError("Market: 3 arguments required (SYMBOL SIDE QTY)")
        symbol, side_str, qty_s = parts
        price = None
        qty   = _to_float_num(qty_s)

    side_str = side_str.strip().upper()
    if side_str not in ("LONG", "SHORT"):
        raise ValueError("SIDE must be LONG or SHORT")
    side = "Buy" if side_str == "LONG" else "Sell"
    return symbol.upper(), side, price, qty


def human_format(num: float) -> str:
    if abs(num) >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    if abs(num) >= 1_000:
        return f"{num/1_000:.1f}K"
    return f"{num:.2f}"

def _parse_sqlite_ts_to_utc(s: str) -> float:
    try:
        dt = datetime.datetime.fromisoformat(s.replace(" ", "T"))
    except Exception:
        try:
            return float(s)
        except Exception:
            return 0.0
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.timestamp()

def main_menu_keyboard(ctx: ContextTypes.DEFAULT_TYPE, user_id: int = None, update: Update = None):
    """Generate main menu keyboard. Clean and user-friendly for each exchange."""
    t = ctx.t
    
    # Try to get user_id from update if not provided
    if user_id is None and update is not None:
        try:
            user_id = update.effective_user.id
        except Exception:
            pass
    
    # Get active exchange and trading mode
    active_exchange = get_exchange_type(user_id) if user_id else "bybit"
    
    if active_exchange == "hyperliquid":
        # ═══════════════════════════════════════════════════════════════
        # ██  HYPERLIQUID - COMPACT MENU  ██
        # ═══════════════════════════════════════════════════════════════
        hl_creds = get_hl_credentials(user_id) if user_id else {}
        is_testnet = hl_creds.get("hl_testnet", False)
        net_emoji = "🧪" if is_testnet else "🌐"
        
        keyboard = [
            # ─── Row 1: Trading Info ───
            [ "💰 Balance", "📊 Positions", "📈 Orders" ],
            # ─── Row 2: Actions ───
            [ "📋 History", "📉 Market", "🤖 Strategies" ],
            # ─── Row 3: Coins & Premium ───
            [ t['button_coins'], t.get('button_subscribe', '💎 Premium'), t['button_lang'] ],
            # ─── Row 4: Exchange & API (bottom) ───
            [ f"🔷 HL {net_emoji}", "🔄 Bybit", "🔑 API Keys" ],
        ]
    else:
        # ═══════════════════════════════════════════════════════════════
        # ██  BYBIT - COMPACT MENU  ██
        # ═══════════════════════════════════════════════════════════════
        creds = get_all_user_credentials(user_id) if user_id else {}
        trading_mode = creds.get("trading_mode", "demo")
        mode_emoji = "🎮" if trading_mode == "demo" else ("💵" if trading_mode == "real" else "🔀")
        
        keyboard = [
            # ─── Row 1: Trading Info ───
            [ "💰 Balance", "📊 Positions", "📈 Orders" ],
            # ─── Row 2: Actions & Strategies ───
            [ "📋 History", "📉 Market", "🤖 Strategies" ],
            # ─── Row 3: Coins & Premium ───
            [ t['button_coins'], t.get('button_subscribe', '💎 Premium'), t['button_lang'] ],
            # ─── Row 4: Exchange & API (bottom) ───
            [ f"🟠 Bybit {mode_emoji}", "🔄 HyperLiquid", "🔑 API Keys" ],
        ]
    
    # Add admin row if user is admin
    if user_id == ADMIN_ID:
        keyboard.append([ t.get('button_licenses', '🔑 Licenses'), t.get('button_admin', '👑 Admin') ])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

def extract_image_from_summary(summary_html: str) -> str | None:
    m = re.search(r'<img[^>]+src="([^"]+)"', summary_html)
    return unescape(m.group(1)) if m else None

_position_mode_cache: dict[tuple[int, str], str] = {} 
_atr_triggered: dict[tuple[int, str], bool] = {}
_close_all_cooldown: dict[int, float] = {}  # uid -> timestamp when cooldown ends
_notification_retry_after: dict[int, float] = {}  # uid -> timestamp when Telegram rate limit expires


async def safe_send_notification(bot, uid: int, text: str, **kwargs) -> bool:
    """
    Send message with Telegram rate limit handling.
    Returns True if sent, False if rate limited.
    """
    from telegram.error import RetryAfter
    
    # Check if user is rate limited
    retry_until = _notification_retry_after.get(uid, 0)
    if time.time() < retry_until:
        logger.debug(f"[{uid}] Skipping notification - rate limited until {retry_until}")
        return False
    
    try:
        await bot.send_message(uid, text, **kwargs)
        return True
    except RetryAfter as e:
        # Store retry_after time and skip this notification
        _notification_retry_after[uid] = time.time() + e.retry_after
        logger.warning(f"[{uid}] Telegram rate limit hit, retry after {e.retry_after}s")
        return False
    except Exception as e:
        logger.error(f"[{uid}] Failed to send notification: {e}")
        return False


@log_calls
async def get_position_mode(user_id: int, symbol: str, account_type: str = None) -> str:
    key = (user_id, symbol, account_type or "auto")
    mode = _position_mode_cache.get(key)
    if mode:
        return mode

    res = await _bybit_request(
        user_id, "GET", "/v5/position/list",
        params={"category": "linear", "symbol": symbol},
        account_type=account_type
    )
    items = res.get("list", []) or []
    idxs = {int(it.get("positionIdx", 0)) for it in items if it is not None}

    mode = "hedge" if (1 in idxs or 2 in idxs) else "one_way"
    _position_mode_cache[key] = mode
    return mode

def position_idx_for(side: str, mode: str) -> int:
    if mode == "hedge":
        return 1 if side == "Buy" else 2
    return 0

@with_texts
@log_calls
async def cmd_approve(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        target_uid = int((ctx.args or [None])[0])
        if not target_uid:
            raise ValueError
    except Exception:
        await update.message.reply_text(ctx.t["usage_approve"])
        return

    set_user_field(target_uid, "is_allowed", 1)
    set_user_field(target_uid, "is_banned", 0)

    await update.message.reply_text(ctx.t["moderation_approved"].format(target=target_uid))
    try:
        await ctx.bot.send_message(target_uid, ctx.t["approved_user_dm"])
    except Exception:
        pass

@with_texts
@log_calls
async def whoami(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(ctx.t.get("your_id", "Your ID: {uid}").format(uid=update.effective_user.id))

@with_texts
@log_calls
async def cmd_ban(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        target_uid = int((ctx.args or [None])[0])
        if not target_uid:
            raise ValueError
    except Exception:
        await update.message.reply_text(ctx.t["usage_ban"])
        return

    set_user_field(target_uid, "is_banned", 1)
    set_user_field(target_uid, "is_allowed", 0)

    await update.message.reply_text(ctx.t["moderation_banned"].format(target=target_uid))
    try:
        await ctx.bot.send_message(target_uid, ctx.t["banned_user_dm"])
    except Exception:
        pass

@log_calls
async def set_leverage(
    user_id: int,
    symbol: str,
    leverage: int = 10,
    account_type: str = None
) -> bool:
    """
    Set leverage for a symbol. Uses cache to avoid redundant API calls.
    Returns True if leverage was changed, False if already set.
    """
    # Clamp leverage to reasonable bounds (Bybit max is typically 100-500 depending on symbol)
    leverage = max(1, min(leverage, 200))
    
    cache_key = (user_id, symbol, account_type or "auto")
    current_lev = _leverage_cache.get(cache_key)
    
    if current_lev == leverage:
        logger.debug(f"[{user_id}] Leverage for {symbol} already {leverage}x, skipping API call")
        return False
    
    body = {
        "category":    "linear",
        "symbol":      symbol,
        "buyLeverage":  str(leverage),
        "sellLeverage": str(leverage),
    }
    try:
        await _bybit_request(user_id, "POST", "/v5/position/set-leverage", body=body, account_type=account_type)
        _leverage_cache[cache_key] = leverage
        logger.info(f"[{user_id}] Leverage for {symbol} set to {leverage}x [{account_type or 'auto'}]")
        return True
    except Exception as e:
        err_str = str(e).lower()
        # If error contains "leverage not modified" - it's already set
        if "not modified" in err_str or "110043" in str(e):
            _leverage_cache[cache_key] = leverage
            logger.debug(f"[{user_id}] Leverage for {symbol} already {leverage}x (from API)")
            return False
        # If error is "leverage invalid" (10001) - fallback through decreasing values
        if "10001" in str(e) or "leverage invalid" in err_str:
            logger.warning(f"[{user_id}] Leverage {leverage}x not supported for {symbol}, trying fallbacks")
            # Try decreasing leverage values until one works
            for fallback_lev in [50, 25, 10, 5, 3, 2, 1]:
                if fallback_lev < leverage:
                    try:
                        body["buyLeverage"] = str(fallback_lev)
                        body["sellLeverage"] = str(fallback_lev)
                        await _bybit_request(user_id, "POST", "/v5/position/set-leverage", body=body, account_type=account_type)
                        _leverage_cache[cache_key] = fallback_lev
                        logger.info(f"[{user_id}] Leverage for {symbol} set to fallback {fallback_lev}x [{account_type or 'auto'}]")
                        return True
                    except Exception:
                        continue
            logger.warning(f"[{user_id}] Could not set any leverage for {symbol}")
            return False
        # 110013: leverage exceeds maxLeverage by risk limit - try to extract and use max
        if "110013" in str(e) or "cannot set leverage" in err_str or "maxleverage" in err_str:
            # Try to extract maxLeverage from error message: "gt maxLeverage [500]"
            import re
            match = re.search(r'maxLeverage\s*\[(\d+)\]', str(e))
            if match:
                max_lev = int(match.group(1))
                logger.warning(f"[{user_id}] Leverage {leverage}x exceeds max {max_lev}x for {symbol}, using max")
                if max_lev != leverage:
                    # Retry with max leverage
                    body["buyLeverage"] = str(max_lev)
                    body["sellLeverage"] = str(max_lev)
                    try:
                        await _bybit_request(user_id, "POST", "/v5/position/set-leverage", body=body, account_type=account_type)
                        _leverage_cache[cache_key] = max_lev
                        logger.info(f"[{user_id}] Leverage for {symbol} set to max {max_lev}x [{account_type or 'auto'}]")
                        return True
                    except Exception as e2:
                        logger.warning(f"[{user_id}] Failed to set max leverage for {symbol}: {e2}")
                        return False
            else:
                # Can't extract max, try common values: 100, 50, 25, 10
                for fallback_lev in [100, 50, 25, 10, 5, 3, 2, 1]:
                    if fallback_lev < leverage:
                        try:
                            body["buyLeverage"] = str(fallback_lev)
                            body["sellLeverage"] = str(fallback_lev)
                            await _bybit_request(user_id, "POST", "/v5/position/set-leverage", body=body, account_type=account_type)
                            _leverage_cache[cache_key] = fallback_lev
                            logger.info(f"[{user_id}] Leverage for {symbol} set to fallback {fallback_lev}x [{account_type or 'auto'}]")
                            return True
                        except Exception:
                            continue
                logger.warning(f"[{user_id}] Could not set any leverage for {symbol}")
                return False
        raise

def _calc_pnl(entry: float, exit_: float, side: str, size: float) -> tuple[float, float]:
    direction = 1.0 if side == "Buy" else -1.0
    pnl_abs = (exit_ - entry) * size * direction
    pct = (exit_ / entry - 1.0) * (100.0 if side == "Buy" else -100.0)
    return pnl_abs, pct


@log_calls
async def detect_exit_reason(
    user_id: int, 
    symbol: str, 
    entry_price: float = None, 
    exit_price: float = None, 
    side: str = None,
    sl_pct: float = None,
    tp_pct: float = None
) -> tuple[str, str]:
    """
    Detect exit reason by checking execution list and order history.
    If Bybit API doesn't provide clear reason, uses price comparison as fallback.
    Returns tuple of (reason, order_type) where reason is one of:
    - "TP" - Take Profit triggered
    - "SL" - Stop Loss triggered  
    - "TRAILING" - Trailing Stop triggered
    - "LIQ" - Liquidation
    - "ADL" - Auto-Deleveraging
    - "MANUAL" - Manual close by user
    - "UNKNOWN" - Could not determine
    """
    reason = "UNKNOWN"
    order_type = ""
    
    # Step 1: Check execution list for reduceOnly trades
    try:
        exec_data = await _bybit_request(
            user_id,
            "GET",
            "/v5/execution/list",
            params={
                "category": "linear",
                "symbol":   symbol,
                "limit":    20
            }
        )
        trades = exec_data.get("list", [])
        closes = [
            t for t in trades
            if t.get("execType") == "Trade"
            and str(t.get("reduceOnly", "")).lower() == "true"
        ]
        
        if closes:
            last = max(closes, key=lambda t: int(t.get("execTime", 0)))
            order_type = last.get("orderType", "")
            
            # Check stopOrderType first (most reliable)
            sop = (last.get("stopOrderType") or "").lower()
            if "takeprofit" in sop or "partialtakeprofit" in sop:
                return "TP", order_type
            elif "stoploss" in sop or "partialstoploss" in sop:
                return "SL", order_type
            elif "trailingstop" in sop:
                return "TRAILING", order_type
            
            # Check createType (from Bybit enum documentation)
            ctp = (last.get("createType") or "").lower()
            if "createbytakeprofit" in ctp or "createbypartialtakeprofit" in ctp:
                return "TP", order_type
            elif "createbystoploss" in ctp or "createbypartialstoploss" in ctp:
                return "SL", order_type
            elif "createbytrailingstop" in ctp or "createbytrailingprofit" in ctp:
                return "TRAILING", order_type
            elif "createbyliq" in ctp or "createbytakeover" in ctp:
                return "LIQ", order_type
            elif "createbyadl" in ctp:
                return "ADL", order_type
            elif "createbyclosing" in ctp:
                return "MANUAL", order_type
            elif "createbyuser" in ctp:
                return "MANUAL", order_type
                
            # Save orderId to check order history if still unknown
            order_id = last.get("orderId")
            if order_id:
                # Step 2: Check order history for more details
                try:
                    order_data = await _bybit_request(
                        user_id,
                        "GET",
                        "/v5/order/history",
                        params={
                            "category": "linear",
                            "symbol": symbol,
                            "orderId": order_id,
                            "limit": 1
                        }
                    )
                    orders = order_data.get("list", [])
                    if orders:
                        order = orders[0]
                        # Check stopOrderType in order
                        sop = (order.get("stopOrderType") or "").lower()
                        if "takeprofit" in sop:
                            return "TP", order_type
                        elif "stoploss" in sop:
                            return "SL", order_type
                        elif "trailingstop" in sop:
                            return "TRAILING", order_type
                        
                        # Check createType in order
                        ctp = (order.get("createType") or "").lower()
                        if "takeprofit" in ctp:
                            return "TP", order_type
                        elif "stoploss" in ctp:
                            return "SL", order_type
                        elif "trailing" in ctp:
                            return "TRAILING", order_type
                        elif "liq" in ctp or "takeover" in ctp:
                            return "LIQ", order_type
                        elif "adl" in ctp:
                            return "ADL", order_type
                        elif "closing" in ctp or "user" in ctp:
                            return "MANUAL", order_type
                except Exception as e:
                    logger.debug(f"Could not fetch order history for {symbol}: {e}")
            
            # Step 3: If still unknown but we have reduceOnly trades, assume MANUAL
            if reason == "UNKNOWN":
                return "MANUAL", order_type
                    
    except Exception as e:
        logger.warning(f"Error in detect_exit_reason for {symbol}: {e}")
    
    # Step 4: If no reduceOnly trades found, check closed-pnl API for execType
    if reason == "UNKNOWN":
        try:
            pnl_data = await _bybit_request(
                user_id,
                "GET",
                "/v5/position/closed-pnl",
                params={
                    "category": "linear",
                    "symbol": symbol,
                    "limit": 5
                }
            )
            pnl_list = pnl_data.get("list", [])
            if pnl_list:
                latest = pnl_list[0]
                exec_type = (latest.get("execType") or "").lower()
                if "trade" in exec_type:
                    # Check orderType for hints
                    ot = (latest.get("orderType") or "").lower()
                    if ot == "market":
                        # Market order could still be TP/SL - check by PnL
                        pass  # Will use price-based detection below
        except Exception as e:
            logger.debug(f"Could not fetch closed-pnl for detect_exit_reason: {e}")
    
    # Step 5: Fallback - determine by comparing exit_price with entry_price and expected TP/SL levels
    if reason == "UNKNOWN" and entry_price and exit_price and side:
        pnl_pct = ((exit_price / entry_price) - 1.0) * 100 if side == "Buy" else ((entry_price / exit_price) - 1.0) * 100
        
        # Use provided SL/TP or defaults
        sl_threshold = sl_pct or 3.0  # Default SL ~3%
        tp_threshold = tp_pct or 8.0  # Default TP ~8%
        
        if side == "Buy":
            # For LONG: profit if exit > entry
            if pnl_pct >= tp_threshold * 0.8:  # At least 80% of TP target
                return "TP", order_type or "Market"
            elif pnl_pct <= -sl_threshold * 0.8:  # At least 80% of SL target
                return "SL", order_type or "Market"
        else:
            # For SHORT: profit if exit < entry
            if pnl_pct >= tp_threshold * 0.8:
                return "TP", order_type or "Market"
            elif pnl_pct <= -sl_threshold * 0.8:
                return "SL", order_type or "Market"
        
        # If small profit/loss, likely manual
        return "MANUAL", order_type or "Market"
    
    return reason, order_type

@log_calls
async def fetch_candles(symbol: str, interval: str, limit: int) -> list[list]:
    url = f"{BYBIT_BASE}/v5/market/kline"
    params = {
        "category": "linear",
        "symbol":   symbol,
        "interval": interval.upper(),
        "limit":    limit
    }
    if _session is None:
        await init_session()
        
    async with _session.get(url, params=params) as resp:
        data = await resp.json()
    return data.get("result", {}).get("list", [])

@log_calls
async def calc_atr(symbol: str, interval: str = "D", periods: int = 14) -> float:
    candles = await fetch_candles(symbol, interval, periods + 50)
    if len(candles) < periods + 1:
        raise RuntimeError(f"Not enough data for ATR: need {periods+1}, need {len(candles)}")

    candles.sort(key=lambda c: int(c[0]))

    closes = [float(c[4]) for c in candles]
    highs  = [float(c[2]) for c in candles]
    lows   = [float(c[3]) for c in candles]

    trs = []
    for i in range(1, len(candles)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i]  - closes[i-1])
        )
        trs.append(tr)

    atr = sum(trs[:periods]) / periods
    for tr in trs[periods:]:
        atr = (atr * (periods - 1) + tr) / periods
    return atr

@with_texts
@log_calls
async def cmd_toggle_atr(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cfg = get_user_config(uid) or {}
    new_mode = not bool(cfg.get("use_atr", 0))
    set_user_field(uid, "use_atr", int(new_mode))
    mode_text = "Wilder‑ATR" if new_mode else "SL/TP %"
    await update.message.reply_text(
        ctx.t['atr_mode_changed'].format(mode_text=mode_text),
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(ctx, update=update)
    )

async def check_trading_limits_user(user_id: int, t: dict) -> tuple[bool, str]:
    """Check if user can open new positions/orders. 0 = unlimited."""
    # Check positions limit (0 = unlimited)
    if MAX_OPEN_POSITIONS > 0:
        positions = await fetch_open_positions(user_id)
        if len(positions) >= MAX_OPEN_POSITIONS:
            return False, t['limit_positions_exceeded'].format(max=MAX_OPEN_POSITIONS)

    # Check orders limit (0 = unlimited)
    if MAX_LIMIT_ORDERS > 0:
        orders = await fetch_open_orders(user_id)
        limit_orders = [o for o in orders if o.get("orderType") == "Limit"]
        if len(limit_orders) >= MAX_LIMIT_ORDERS:
            return False, t['limit_limit_orders_exceeded'].format(max=MAX_LIMIT_ORDERS)

    return True, ""

@with_texts
@log_calls
async def cmd_select_coin_group(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show coin filter selection with current filter highlighted."""
    uid = update.effective_user.id
    cfg = get_user_config(uid) or {}
    current_filter = (cfg.get("coins") or "ALL").upper()
    
    # Emojis for current selection
    filters = {
        "ALL": ("🌐", ctx.t.get('group_all', '🌐 All Coins')),
        "TOP100": ("🏆", ctx.t.get('group_top100', '🏆 Top Coins')),
        "VOLATILE": ("🔥", ctx.t.get('group_volatile', '🔥 Volatile Coins')),
    }
    
    # Build keyboard with check mark on current
    keyboard = []
    for key, (emoji, label) in filters.items():
        mark = " ✅" if key == current_filter else ""
        keyboard.append([InlineKeyboardButton(f"{emoji} {label}{mark}", callback_data=f"coins:{key}")])
    
    # Info text
    current_label = filters.get(current_filter, ("🌐", "All"))[1]
    text = f"🪙 *{ctx.t.get('select_coin_group', 'Select Coin Filter')}*\n\n"
    text += f"📍 Current: *{current_label}*\n\n"
    text += f"🌐 *All* — trade any coin\n"
    text += f"🏆 *Top* — only major coins (BTC, ETH, SOL, etc.)\n"
    text += f"🔥 *Volatile* — altcoins with high volatility"
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

def get_user_tz(user_id: int) -> str:
    cfg = get_user_config(user_id) or {}
    return cfg.get("tz", "UTC")  



@log_calls
async def fetch_today_realized_pnl(user_id: int, tz_str: str | None = None, account_type: str | None = None, exchange: str | None = None) -> float:
    """
    Fetch today's realized PnL for user.
    
    Args:
        user_id: Telegram user ID
        tz_str: Timezone string (defaults to user's timezone)
        account_type: 'demo' or 'real' (defaults to user's trading_mode)
        exchange: 'bybit' or 'hyperliquid' (defaults to user's active exchange)
    
    Returns:
        Total realized PnL for today in USDT
    """
    tz = ZoneInfo(tz_str or get_user_tz(user_id))
    now_local   = datetime.datetime.now(tz)
    start_local = datetime.datetime(year=now_local.year, month=now_local.month, day=now_local.day, tzinfo=tz)
    end_local   = start_local + datetime.timedelta(days=1)
    start_ts = int(start_local.timestamp() * 1000)
    end_ts   = int(end_local.timestamp() * 1000)
    
    # Determine exchange
    if exchange is None:
        exchange = db.get_exchange_type(user_id) or 'bybit'
    
    total = 0.0
    
    if exchange == 'hyperliquid':
        # Use HyperLiquid adapter for PnL
        try:
            creds = db.get_hl_credentials(user_id)
            if creds and creds.get("private_key"):
                from hl_adapter import HLAdapter
                adapter = HLAdapter(
                    private_key=creds["private_key"],
                    testnet=bool(creds.get("testnet", False)),
                    vault_address=creds.get("vault_address")
                )
                await adapter.initialize()
                
                # Get fills for today
                fills = await adapter.get_fills_by_time(start_ts, end_ts)
                for fill in fills:
                    try:
                        total += float(fill.get("closedPnl") or fill.get("pnl") or 0.0)
                    except Exception:
                        pass
                
                await adapter.close()
        except Exception as e:
            logger.warning(f"[{user_id}] HL realized PnL fetch error: {e}")
    else:
        # Bybit - use account_type for API request
        cursor = None
        while True:
            params = {
                "category":  "linear",
                "startTime": start_ts,
                "endTime":   end_ts,
                "limit":     100,
            }
            if cursor:
                params["cursor"] = cursor

            res = await _bybit_request(user_id, "GET", "/v5/position/closed-pnl", params=params, account_type=account_type)
            items = res.get("list", []) or []
            for it in items:
                try:
                    total += float(it.get("closedPnl") or 0.0)
                except Exception:
                    pass

            cursor = res.get("nextPageCursor")
            if not cursor:
                break

    return total


@log_calls
async def fetch_last_closed_pnl(user_id: int, symbol: str) -> dict | None:
    """Fetch last closed PnL record for a symbol. Returns None if no records found."""
    try:
        data = await _bybit_request(
            user_id,
            "GET",
            "/v5/position/closed-pnl",
            params={
                "category": "linear",
                "symbol":   symbol,
                "limit":    1
            }
        )
        recs = data.get("list", [])
        if not recs:
            logger.debug(f"[{user_id}] No closed PnL records for {symbol}")
            return None
        rec = recs[0]
        # Log all fields for debugging
        logger.debug(f"[{user_id}] Bybit closed-pnl raw: {rec}")
        return rec
    except Exception as e:
        logger.debug(f"[{user_id}] fetch_last_closed_pnl error: {e}")
        return None

@log_calls
async def fetch_last_execution_price(user_id: int, symbol: str) -> float:
    result = await _bybit_request(
        user_id,
        "GET",
        "/v5/position/closed-pnl",
        params={
            "category": "linear",
            "symbol":   symbol,
            "limit":    1
        }
    )
    closes = result.get("list", [])
    if not closes:
        raise RuntimeError(f"No closed PnL records for {symbol}")
    last = closes[0]
    exit_price = float(last["avgExitPrice"])
    return exit_price

class MissingAPICredentials(RuntimeError):
    pass


def _canon_query(params: dict | None) -> str:
    if not params:
        return ""
    items = sorted((str(k), str(v)) for k, v in params.items())
    return "&".join(f"{quote(k, safe='~')}={quote(v, safe='~')}" for k, v in items)


@log_calls
async def _bybit_request(user_id: int, method: str, path: str,
                         params: dict = None, body: dict = None,
                         retries: int = 3, account_type: str = None) -> dict:
    """Make a request to Bybit API.
    
    Args:
        user_id: Telegram user ID
        method: HTTP method (GET/POST)
        path: API endpoint path
        params: Query parameters for GET requests
        body: JSON body for POST requests
        retries: Number of retry attempts
        account_type: 'demo', 'real', or None (auto-detect from trading_mode)
    """
    # Check if API key is known to be expired/invalid - skip API call
    cache_key = (user_id, account_type or "auto")
    now = time.time()
    if cache_key in _expired_api_keys_cache:
        expired_ts = _expired_api_keys_cache[cache_key]
        if now - expired_ts < EXPIRED_API_KEYS_CACHE_TTL:
            raise MissingAPICredentials(f"API key expired/invalid (cached, retry after {int(EXPIRED_API_KEYS_CACHE_TTL - (now - expired_ts))}s)")
        else:
            # TTL expired, remove from cache and retry
            del _expired_api_keys_cache[cache_key]
    
    # Get credentials for specified account type
    api_key, api_secret = get_user_credentials(user_id, account_type)
    if not api_key or not api_secret:
        raise MissingAPICredentials("API Key/Secret not set")

    # Determine base URL based on account type
    if account_type == "real":
        base_url = BYBIT_REAL_URL
    elif account_type == "demo":
        base_url = BYBIT_DEMO_URL
    else:
        # Auto-detect from trading mode
        trading_mode = get_trading_mode(user_id)
        base_url = BYBIT_REAL_URL if trading_mode == "real" else BYBIT_DEMO_URL

    if _session is None:
        await init_session()

    ts   = str(int(time.time() * 1000))
    recv = "60000"
    params    = params or {}
    body_json = json.dumps(body, separators=(",", ":")) if body else ""
    query     = _canon_query(params)

    sign      = _sign_payload(ts, api_key, api_secret, recv, body_json, query)


    headers = {
        "X-BAPI-API-KEY":     api_key,
        "X-BAPI-TIMESTAMP":   ts,
        "X-BAPI-RECV-WINDOW": recv,
        "X-BAPI-SIGN":        sign,
        "X-BAPI-SIGN-TYPE":   "2",
        "Content-Type":       "application/json",
    }
    url = base_url + path + (f"?{query}" if method == "GET" and query else "")
    
    logger.debug(f"API Request: {method} {url} [account_type={account_type}]")


    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            if method == "GET":
                async with _session.get(url, headers=headers) as resp:
                    resp.raise_for_status()
                    data = await resp.json(content_type=None)
            else:
                async with _session.post(url, data=body_json, headers=headers) as resp:
                    resp.raise_for_status()
                    data = await resp.json(content_type=None)

            if path == "/v5/position/trading-stop" and data.get("retCode") == 34040:
                logger.debug(f"{path}: not modified (retCode=34040) — ok")
                return data.get("result", {})

            # Handle "leverage not modified" - not an error, just already set
            if path == "/v5/position/set-leverage" and data.get("retCode") == 110043:
                logger.debug(f"{path}: leverage not modified (retCode=110043) — ok")
                return data.get("result", {})
            
            # Handle "no closed PnL" - not critical, return empty
            if path == "/v5/position/closed-pnl" and data.get("retCode") == 10016:
                logger.debug(f"{path}: no closed PnL records (retCode=10016)")
                return {"list": []}

            if data.get("retCode") not in (0, None):
                ret_code = data.get("retCode")
                ret_msg = str(data.get("retMsg", "")).lower()
                
                # Handle expired/invalid API keys - cache to avoid spamming
                if ret_code in (33004, 10003, 10004, 10005):
                    # 33004 = API key expired, 10003/4/5 = invalid API key/signature
                    cache_key = (user_id, account_type or "auto")
                    _expired_api_keys_cache[cache_key] = time.time()
                    logger.warning(f"API key error for user {user_id} (cached for {EXPIRED_API_KEYS_CACHE_TTL}s): {data.get('retMsg')}")
                    raise MissingAPICredentials(f"API key error: {data.get('retMsg')}")
                
                # Leverage validation errors - log as debug only, not error (handled in set_leverage)
                elif path == "/v5/position/set-leverage" and ret_code in (10001, 110013):
                    logger.debug(f"Bybit leverage validation: {data.get('retMsg')}")
                    raise RuntimeError(f"Bybit error {path}: {data}")
                
                # SL/TP validation errors - log as warning, not error (expected for deep loss positions)
                elif ret_code == 10001 and ("should lower than" in ret_msg or "should higher than" in ret_msg):
                    logger.warning(f"Bybit SL/TP validation: {path} - {data.get('retMsg')}")
                    raise RuntimeError(f"Bybit error {path}: {data}")
                
                else:
                    logger.error(f"Bybit error for user {user_id} on {path}: {data}")
                    raise RuntimeError(f"Bybit error {path}: {data}")

            return data.get("result") or data

        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
            last_exc = e
            logger.warning(f"Request {path} failed ({attempt}/{retries}): {e}")
            if attempt < retries:
                await asyncio.sleep(2 ** attempt)
            else:
                logger.error(f"All {retries} retries failed for {path}")
                raise

    raise last_exc

@log_calls
async def fetch_market_status():
    """Fetch market data from CoinMarketCap (primary) and Yahoo Finance (Gold, S&P500)"""
    if _session is None:
        await init_session()

    btc_dom, eth_dom, usdt_dom = 0.0, 0.0, 0.0
    btc_price, btc_change = 0.0, 0.0
    sp500, sp500_change = 0.0, 0.0
    gold_price, gold_change = 0.0, 0.0
    total1, total2, total3 = 0.0, 0.0, 0.0
    fear_greed, fear_greed_label = 0, "N/A"
    altseason_index = 0
    top_coins = []  # List of (symbol, mcap_billions, dominance_pct)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    # ===== CoinMarketCap: listing API for top coins, dominance, BTC price =====
    try:
        cmc_url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?start=1&limit=15&sortBy=market_cap&sortType=desc"
        async with _session.get(cmc_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status == 200:
                data = await r.json()
                for crypto in data.get("data", {}).get("cryptoCurrencyList", []):
                    symbol = crypto.get("symbol")
                    # Get USD quote (second in list typically)
                    usd_quote = None
                    for q in crypto.get("quotes", []):
                        if q.get("name") == "USD":
                            usd_quote = q
                            break
                    if not usd_quote and crypto.get("quotes"):
                        usd_quote = crypto.get("quotes", [{}])[-1]  # Last is usually USD
                    
                    if not usd_quote:
                        continue
                        
                    dom = usd_quote.get("dominance", 0)
                    mcap = usd_quote.get("marketCap", 0)
                    mcap_b = mcap / 1e9 if mcap else 0
                    price = usd_quote.get("price", 0)
                    change_24h = usd_quote.get("percentChange24h", 0)
                    
                    if symbol == "BTC":
                        btc_dom = float(dom)
                        btc_price = float(price)
                        btc_change = float(change_24h)
                    elif symbol == "ETH":
                        eth_dom = float(dom)
                    elif symbol == "USDT":
                        usdt_dom = float(dom)
                    
                    # Collect top coins (skip stablecoins and index tokens for the list)
                    if symbol not in ("BTC", "USDT", "USDC", "DAI", "BUSD", "TUSD", "FDUSD", "USDD", "CMC20", "CMC100"):
                        top_coins.append((symbol, mcap_b, float(dom)))
    except Exception as e:
        logger.debug(f"CoinMarketCap listing fetch failed: {e}")

    # ===== CoinMarketCap: global metrics for Total Market Cap =====
    try:
        cmc_global_url = "https://api.coinmarketcap.com/data-api/v3/global-metrics/quotes/latest"
        async with _session.get(cmc_global_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status == 200:
                data = await r.json()
                gdata = data.get("data", {})
                
                # Fallback for dominance if listing failed
                if btc_dom == 0:
                    btc_dom = float(gdata.get("btcDominance", 0))
                if eth_dom == 0:
                    eth_dom = float(gdata.get("ethDominance", 0))
                
                # Get Total Market Cap from quotes
                quotes = gdata.get("quotes", [])
                if quotes:
                    q = quotes[0]
                    total_mcap = q.get("totalMarketCap", 0)
                    altcoin_mcap = q.get("altcoinMarketCap", 0)
                    
                    total1 = total_mcap / 1e12  # Total 1: All crypto in trillions
                    total2 = altcoin_mcap / 1e12  # Total 2: Without BTC
                    # Total 3: Without BTC and ETH
                    eth_mcap = total_mcap * (eth_dom / 100) if eth_dom else 0
                    total3 = (altcoin_mcap - eth_mcap) / 1e12
    except Exception as e:
        logger.debug(f"CoinMarketCap global metrics failed: {e}")

    # ===== CoinMarketCap: Fear & Greed and Altcoin Season from charts page =====
    try:
        fg_url = "https://coinmarketcap.com/charts/fear-and-greed-index/"
        async with _session.get(fg_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status == 200:
                html = await r.text()
                import re
                # Parse Fear & Greed Index
                fg_match = re.search(r'"score":(\d+).*?"name":"([^"]+)"', html)
                if fg_match:
                    fear_greed = int(fg_match.group(1))
                    fear_greed_label = fg_match.group(2)
                
                # Parse Altcoin Season Index
                alt_match = re.search(r'"altcoinIndex":(\d+)', html)
                if alt_match:
                    altseason_index = int(alt_match.group(1))
    except Exception as e:
        logger.debug(f"CoinMarketCap Fear & Greed fetch failed: {e}")

    # ===== Yahoo Finance: S&P 500 =====
    try:
        sp500_url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?interval=1d&range=2d"
        async with _session.get(sp500_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as r:
            data = await r.json()
            result = data.get("chart", {}).get("result", [])
            if result:
                meta = result[0].get("meta", {})
                sp500 = meta.get("regularMarketPrice", 0.0)
                prev_close = meta.get("chartPreviousClose", meta.get("previousClose", sp500))
                if prev_close and prev_close > 0:
                    sp500_change = ((sp500 - prev_close) / prev_close) * 100
    except Exception as e:
        logger.warning(f"Yahoo S&P500 fetch failed: {e}")

    # ===== Yahoo Finance: Gold (XAU/USD) =====
    try:
        gold_url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=1d&range=2d"
        async with _session.get(gold_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as r:
            data = await r.json()
            result = data.get("chart", {}).get("result", [])
            if result:
                meta = result[0].get("meta", {})
                gold_price = meta.get("regularMarketPrice", 0.0)
                prev_close = meta.get("chartPreviousClose", meta.get("previousClose", gold_price))
                if prev_close and prev_close > 0:
                    gold_change = ((gold_price - prev_close) / prev_close) * 100
    except Exception as e:
        logger.warning(f"Yahoo Gold fetch failed: {e}")

    # Get top 5 altcoins by dominance
    top_coins = sorted(top_coins, key=lambda x: x[2], reverse=True)[:5]

    return btc_dom, usdt_dom, btc_price, btc_change, sp500, sp500_change, top_coins, gold_price, gold_change, total1, total2, total3, fear_greed, fear_greed_label, altseason_index



@log_calls
async def set_trading_stop(
    uid: int,
    symbol: str,
    tp_price: float | None = None,
    sl_price: float | None = None,
    side_hint: str | None = None,
    is_trailing: bool = False,  # Skip entry price validation for trailing SL
) -> bool:
    """Set TP/SL for a position. Returns True if successful, False if position not found."""
    if tp_price is None and sl_price is None:
        raise ValueError("You must specify at least one of the levels: TP or SL")

    filt = await get_symbol_filters(uid, symbol)
    tick = float(filt["tickSize"])

    if side_hint:
        s = side_hint.strip().upper()
        if s in ("LONG", "BUY"):
            side_hint = "Buy"
        elif s in ("SHORT", "SELL"):
            side_hint = "Sell"
        else:
            side_hint = None  

    positions = await fetch_open_positions(uid)
    pos_candidates = [p for p in positions if p.get("symbol") == symbol]

    if not pos_candidates:
        # Position was closed - return False instead of raising
        logger.debug(f"[{uid}] No open positions for {symbol}, skipping SL/TP update")
        return False

    pos = None
    if side_hint:
        pos = next((p for p in pos_candidates if p.get("side") == side_hint), None)

    if not pos:
        pos = max(pos_candidates, key=lambda p: abs(float(p.get("size") or 0.0)))

    effective_side = pos.get("side")
    if effective_side not in ("Buy", "Sell"):
        try:
            mark = float(pos.get("markPrice"))
        except (TypeError, ValueError):
            mark = None
        if mark is not None:
            if sl_price is not None:
                effective_side = "Buy" if sl_price < mark else "Sell"
            elif tp_price is not None:
                effective_side = "Buy" if tp_price > mark else "Sell"
    if effective_side not in ("Buy", "Sell"):
        effective_side = "Buy" 

    def _to_float(x):
        try:
            return float(x) if x not in (None, "", 0, "0") else None
        except Exception:
            return None

    current_sl = _to_float(pos.get("stopLoss"))
    current_tp = _to_float(pos.get("takeProfit"))
    try:
        mark = float(pos.get("markPrice"))
    except (TypeError, ValueError):
        mark = None
    
    # Bybit validates SL/TP against entry price (avgPrice), not mark price
    try:
        entry_price = float(pos.get("avgPrice") or pos.get("entry_price") or 0)
    except (TypeError, ValueError):
        entry_price = None
    
    # Debug: log validation parameters
    logger.debug(f"{symbol}: set_trading_stop validation - entry_price={entry_price}, mark={mark}, sl_price={sl_price}, tp_price={tp_price}, side={effective_side}")

    def _q(x: float) -> float:
        return quantize(x, tick)

    def _qu(x: float) -> float:
        return quantize_up(x, tick)

    if sl_price is not None:
        if effective_side == "Buy":
            sl_price = _qu(sl_price)
        else:
            sl_price = _q(sl_price)

    if tp_price is not None:
        tp_price = _q(tp_price)

    # Bybit validates SL against BOTH entry price AND mark price
    # For LONG: SL must be < entry_price AND < mark_price
    # For SHORT: SL must be > entry_price AND > mark_price
    
    if tp_price is not None:
        # TP validation - check against entry_price first, then mark
        check_prices = [p for p in [entry_price, mark] if p and p > 0]
        for check_price in check_prices:
            if effective_side == "Buy" and tp_price <= check_price:
                logger.warning(f"{symbol}: TP ({tp_price}) <= price ({check_price}) for LONG - skipping TP")
                tp_price = None
                break
            if effective_side == "Sell" and tp_price >= check_price:
                logger.warning(f"{symbol}: TP ({tp_price}) >= price ({check_price}) for SHORT - skipping TP")
                tp_price = None
                break

    if sl_price is not None:
        # SL validation - for trailing SL only check against mark price, not entry
        # For regular SL, check against both entry and mark price
        if is_trailing:
            # Trailing SL: only validate against mark price (SL follows price movement)
            check_prices = [mark] if mark and mark > 0 else []
        else:
            # Regular SL: validate against both entry and mark price
            check_prices = [p for p in [entry_price, mark] if p and p > 0]
        for check_price in check_prices:
            if effective_side == "Buy" and sl_price >= check_price:
                logger.warning(f"{symbol}: SL ({sl_price}) >= price ({check_price}) for LONG - skipping SL")
                sl_price = None
                break
            if effective_side == "Sell" and sl_price <= check_price:
                logger.warning(f"{symbol}: SL ({sl_price}) <= price ({check_price}) for SHORT - skipping SL")
                sl_price = None
                break

    def _stricter(side_: str, new_sl: float, cur_sl):
        if cur_sl in (None, "", 0, "0", 0.0):
            return new_sl
        cur = float(cur_sl)
        if side_ == "Buy":
            return new_sl if new_sl > cur else None
        else:
            return new_sl if new_sl < cur else None

    if sl_price is not None:
        sl_candidate = _stricter(effective_side, sl_price, current_sl)
        if sl_candidate is None:
            sl_price = None
        else:
            sl_price = sl_candidate

    if (tp_price is None or tp_price == current_tp) and (sl_price is None or sl_price == current_sl):
        logger.debug(f"{symbol}: trading-stop unchanged (side={effective_side})")
        return {
            "symbol": symbol,
            "side": effective_side,
            "positionIdx": await _position_idx_for_cached(uid, symbol, effective_side),
            "takeProfit": current_tp,
            "stopLoss": current_sl,
            "changed": False,
        }

    mode = await get_position_mode(uid, symbol)
    position_idx = position_idx_for(effective_side, mode)

    body = {
        "category": "linear",
        "symbol": symbol,
        "positionIdx": position_idx,
    }
    if tp_price is not None:
        body["takeProfit"] = str(tp_price)
    if sl_price is not None:
        body["stopLoss"] = str(sl_price)

    logger.debug(
        f"{symbol}: set_trading_stop side={effective_side} mode={mode} idx={position_idx} "
        f"mark={mark} tp={tp_price} sl={sl_price}"
    )

    try:
        await _bybit_request(uid, "POST", "/v5/position/trading-stop", body=body)
        return True
    except RuntimeError as e:
        err_str = str(e).lower()
        if "no open positions" in err_str or "position not exists" in err_str:
            logger.debug(f"[{uid}] Position for {symbol} closed during set_trading_stop")
            return False
        # Handle invalid SL/TP price errors - position in deep loss
        if "should lower than" in err_str or "should higher than" in err_str:
            logger.warning(f"[{uid}] {symbol}: SL/TP price invalid (position in deep loss)")
            return "deep_loss"  # Special return value to indicate deep loss
        raise

async def _position_idx_for_cached(uid: int, symbol: str, side: str) -> int:
    mode = await get_position_mode(uid, symbol)
    return position_idx_for(side, mode)

@with_texts
@log_calls
async def cmd_manual_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                ctx.t['button_order_limit'],    
                callback_data="order_type:Limit"
            ),
            InlineKeyboardButton(
                ctx.t['button_order_market'],   
                callback_data="order_type:Market"
            ),
        ]
    ]
    await update.message.reply_text(
        ctx.t['order_type_prompt'],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ORDER_TYPE

async def on_error(update, context):
    err = context.error
    if err is None:
        # No actual error, probably just a cancelled callback
        return
    if isinstance(err, (TgTimedOut, NetworkError)):
        logger.warning(f"Telegram transient error: {err}")
        return
    # Log with traceback for debugging
    logger.error(f"Unhandled error: {type(err).__name__}: {err}", exc_info=err)  

@with_texts
@log_calls
async def on_order_type_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    try:
        asyncio.create_task(q.answer(cache_time=1))   
    except TgTimedOut:
        logger.warning("q.answer() timeout — we ignore")

    _, order_type = q.data.split(":", 1)
    ctx.user_data['manual_order_type'] = order_type

    if order_type == "Limit":
        prompt = (
            ctx.t['limit_order_format']
        )
    else:
        prompt = (
            ctx.t['market_order_format']
        )

    await q.edit_message_text(prompt, parse_mode='Markdown')
    return ORDER_PARAMS

@log_calls
async def split_market_plus_one_limit(
    uid: int,
    symbol: str,
    side: str,               
    spot_price: float,
    total_qty: float,
    signal_id: int | None,
    timeframe: str,
    ctx: ContextTypes.DEFAULT_TYPE,
    t: dict,
    *,
    market_msg: str,           
    limit_msg: str,
    strategy: str | None = None,
    account_type: str = "demo",
) -> None:
    filt = await get_symbol_filters(uid, symbol)
    step_qty  = float(filt["qtyStep"])
    min_qty   = float(filt["minQty"])

    def q_qty(v: float) -> float:
        return max(min_qty, quantize(v, step_qty))

    leg1_raw = total_qty * DCA_LEGS[0]
    leg2_raw = total_qty * DCA_LEGS[1]
    leg3_raw = total_qty * DCA_LEGS[2]

    leg1 = q_qty(leg1_raw)
    leg2 = q_qty(leg2_raw)
    leg3 = q_qty(total_qty - leg1 - leg2) 
    if leg3 < min_qty:
        leg2 = q_qty(leg2 + leg3)
        leg3 = 0.0

    if leg1 < min_qty:
        leg1 = q_qty(min_qty)
    if leg2 < min_qty and leg2 > 0:
        leg2 = q_qty(min_qty)

    async def get_mark() -> float | None:
        try:
            data = await _bybit_request(uid, "GET", "/v5/market/tickers",
                                        params={"category":"linear","symbol":symbol})
            last = (data.get("list") or [{}])[0].get("lastPrice")
            if last not in (None, "", "0"):
                return float(last)
        except Exception:
            pass
        try:
            positions = await fetch_open_positions(uid)
            p = next((p for p in positions if p.get("symbol")==symbol), None)
            if p:
                return float(p.get("markPrice"))
        except Exception:
            pass
        return None

    async def strict_set_sl_tp(_side: str, _entry: float, hint_tp_pct: float, hint_sl_pct: float):
        cfg = get_user_config(uid) or {}
        global_use_atr = bool(cfg.get("use_atr", 1))  # Default to ATR enabled
        
        # Get strategy-specific use_atr if strategy is set
        if strategy:
            strat_settings = db.get_strategy_settings(uid, strategy, exchange="bybit", account_type=account_type)
            strat_use_atr = strat_settings.get("use_atr")
            use_atr = bool(strat_use_atr) if strat_use_atr is not None else global_use_atr
        else:
            use_atr = global_use_atr
        
        # P0.5: If hint_tp_pct is None, it means ATR mode - skip TP
        if hint_tp_pct is None:
            use_atr = True
        
        # Use strategy-specific SL/TP if available
        sl_pct, tp_pct = resolve_sl_tp_pct(cfg, symbol, strategy=strategy, user_id=uid, side=_side)
        sl_pct = hint_sl_pct or sl_pct
        tp_pct = hint_tp_pct or tp_pct

        sl_price = round(_entry * (1 - sl_pct/100) if _side=="Buy" else _entry*(1+sl_pct/100), 6)
        if not use_atr:
            tp_price = round(_entry * (1 + tp_pct/100) if _side=="Buy" else _entry*(1-tp_pct/100), 6)
            mark = await get_mark()
            kwargs = {"sl_price": sl_price}
            if mark is None or (_side=="Buy" and tp_price>mark) or (_side=="Sell" and tp_price<mark):
                kwargs["tp_price"] = tp_price
            await set_trading_stop(uid, symbol, **kwargs, side_hint=_side)
        else:
            await set_trading_stop(uid, symbol, sl_price=sl_price, side_hint=_side)
            logger.info(f"[{uid}] ATR enabled for {symbol}: only SL={sl_price:.6f} set, TP managed by trailing")

    await place_order(uid, symbol, side, orderType="Market", qty=leg1)
    pos = None
    for _ in range(12):
        try:
            positions = await fetch_open_positions(uid)
            pos = next((p for p in positions if p.get("symbol")==symbol), None)
            if pos:
                break
        except Exception:
            pass
        await asyncio.sleep(0.25)

    cfg = get_user_config(uid) or {}
    # Use strategy-specific settings including use_atr
    trade_params = get_strategy_trade_params(uid, cfg, symbol, strategy, side=side, account_type=account_type)
    sl_pct = trade_params["sl_pct"]
    tp_pct = trade_params["tp_pct"]
    use_atr = trade_params["use_atr"]
    
    tf = timeframe or "24h"
    periods = TIMEFRAME_PARAMS.get(tf, TIMEFRAME_PARAMS["24h"])["atr_periods"]

    if not pos:
        try:
            await ctx.bot.send_message(
                uid,
                t.get('pos_fetch_fail', "Failed to confirm open position {symbol}.").format(symbol=symbol)
            )
        finally:
            return

    entry  = float(pos.get("avgPrice") or spot_price)
    size   = float(pos.get("size") or leg1)
    side_s = pos.get("side") or side
    # Get leverage from position data (Bybit returns it) or from user config
    pos_leverage = pos.get("leverage")
    if pos_leverage:
        pos_leverage = int(float(pos_leverage))
    else:
        pos_leverage = cfg.get('leverage', 10)

    add_active_position(
        user_id=uid, symbol=symbol, side=side_s,
        entry_price=entry, size=size,
        timeframe=tf, signal_id=(signal_id or get_last_signal_id(uid, symbol, tf)),
        strategy=strategy,
        account_type=account_type,
        use_atr=use_atr,  # P0.5: Pass ATR setting
        leverage=pos_leverage  # Save actual leverage used
    )

    # P0.5: If ATR enabled, only set SL (no TP - will be managed by ATR trailing)
    if use_atr:
        await strict_set_sl_tp(side_s, entry, None, sl_pct)  # tp_pct=None
        logger.info(f"[{uid}] ATR enabled for {symbol}: only SL set, TP will be managed by ATR trailing")
    else:
        await strict_set_sl_tp(side_s, entry, tp_pct, sl_pct)
    
    try:
        await ctx.bot.send_message(
            uid,
            t.get('dca_leg1_done', "DCA: Leg #1 MARKET {symbol} qty={q}, entry≈{p}")
             .format(symbol=symbol, q=leg1, p=entry)
        )
    except Exception:
        pass
    async def _dca_task():
        try:
            try:
                atr_val = await calc_atr(symbol, interval=ATR_INTERVAL, periods=periods)
            except Exception:
                atr_val = 0.0

            if leg2 >= min_qty:
                deadline2 = time.time() + DCA_LEG_TIMEOUT_SEC
                fired2 = False
                while time.time() < deadline2:
                    mark = await get_mark()
                    if mark is not None and atr_val > 0:
                        trigger = DCA_ATR_MULTS[0] * atr_val
                        if (side_s == "Buy" and (entry - mark) >= trigger) or \
                           (side_s == "Sell" and (mark - entry) >= trigger):
                            fired2 = True
                            break
                    await asyncio.sleep(DCA_POLL_SEC)

                if fired2:
                    await place_order(uid, symbol, side_s, orderType="Market", qty=leg2)
                    for _ in range(12):
                        positions = await fetch_open_positions(uid)
                        p2 = next((p for p in positions if p.get("symbol")==symbol), None)
                        if p2:
                            break
                        await asyncio.sleep(0.25)
                    if p2:
                        entry2 = float(p2.get("avgPrice") or entry)
                        size2  = float(p2.get("size") or (size + leg2))
                        await strict_set_sl_tp(side_s, entry2, tp_pct, sl_pct)
                        try:
                            await ctx.bot.send_message(
                                uid,
                                t.get('dca_leg2_done', "DCA: Leg #2 MARKET {symbol} qty={q}, new_avg≈{p}")
                                 .format(symbol=symbol, q=leg2, p=entry2)
                            )
                        except Exception:
                            pass
                        entry = entry2
                        size  = size2

            if leg3 >= min_qty:
                deadline3 = time.time() + DCA_LEG_TIMEOUT_SEC
                fired3 = False
                while time.time() < deadline3:
                    mark = await get_mark()
                    if mark is not None and atr_val > 0:
                        trigger = DCA_ATR_MULTS[1] * atr_val
                        if (side_s == "Buy" and (entry - mark) >= trigger) or \
                           (side_s == "Sell" and (mark - entry) >= trigger):
                            fired3 = True
                            break
                    await asyncio.sleep(DCA_POLL_SEC)

                cur = await get_mark()
                if cur is None:
                    cur = entry
                lim_price = cur * (1.0 - DCA_LAST_LEG_EXTRA_PCT/100.0) if side_s == "Buy" \
                            else cur * (1.0 + DCA_LAST_LEG_EXTRA_PCT/100.0)

                try:
                    res = await place_limit_order(uid, symbol, side_s, price=lim_price, qty=leg3)
                    order_id = _normalize_order_id(res)
                    tif = str(res.get("timeInForce") or "GTC")
                    add_pending_limit_order(
                        user_id=uid, order_id=order_id, symbol=symbol,
                        side=side_s, qty=leg3, price=lim_price,
                        signal_id=(signal_id or 0),
                        created_ts=int(time.time()*1000),
                        time_in_force=tif,
                    )
                    try:
                        await ctx.bot.send_message(
                            uid,
                            t.get('dca_leg3_limit', "DCA: Leg #3 LIMIT {symbol} @ {p} qty={q} (pending)")
                             .format(symbol=symbol, p=round(lim_price,6), q=leg3)
                        )
                    except Exception:
                        pass
                except Exception:
                    await place_order(uid, symbol, side_s, orderType="Market", qty=leg3)
                    for _ in range(12):
                        positions = await fetch_open_positions(uid)
                        p3 = next((p for p in positions if p.get("symbol")==symbol), None)
                        if p3:
                            break
                        await asyncio.sleep(0.25)
                    if p3:
                        entry3 = float(p3.get("avgPrice") or entry)
                        await strict_set_sl_tp(side_s, entry3, tp_pct, sl_pct)
                        try:
                            await ctx.bot.send_message(
                                uid,
                                t.get('dca_leg3_market', "DCA: Leg #3 MARKET {symbol} qty={q}, new_avg≈{p}")
                                 .format(symbol=symbol, q=leg3, p=entry3)
                            )
                        except Exception:
                            pass

        except Exception as e:
            logger.error(f"DCA task error for {uid}:{symbol}: {e}", exc_info=True)

    try:
        asyncio.create_task(_dca_task(), name=f"dca_{uid}_{symbol}")
    except Exception:
        pass

@with_texts
@log_calls
async def manual_order_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    try:
        typ = ctx.user_data.get('manual_order_type')
        if not typ:
            await update.message.reply_text(ctx.t['order_type_prompt'], reply_markup=main_menu_keyboard(ctx, update=update))
            return ConversationHandler.END

        parts = update.message.text.strip().split()
        symbol, side, price, qty = parse_manual(parts, typ)

        filt = await get_symbol_filters(uid, symbol) 
        tick     = float(filt["tickSize"])
        min_px   = float(filt["minPrice"])
        min_qty  = float(filt["minQty"])
        qty_step = float(filt["qtyStep"])

        q_raw = qty
        q = quantize(q_raw, qty_step)
        if q < min_qty:
            q = min_qty

        inst = await _bybit_request(
            uid, "GET", "/v5/market/instruments-info",
            params={"category": "linear", "symbol": symbol}
        )
        lot      = inst["list"][0]["lotSizeFilter"]
        raw_max  = lot.get("maxOrderQty") if typ == "Limit" else lot.get("maxMktOrderQty")
        max_qty  = float(raw_max) if raw_max not in (None, "", 0, "0") else float("inf")

        if q > max_qty:
            q = quantize(max_qty, qty_step)
            if q < min_qty:
                q = min_qty

        px_adj = None
        if typ == "Limit":
            if price is None:
                await update.message.reply_text(ctx.t['order_parse_error'], reply_markup=main_menu_keyboard(ctx, update=update))
                return ConversationHandler.END
            px_adj = quantize(price, tick)
            if px_adj < min_px:
                await update.message.reply_text(
                    ctx.t['price_error_min'].format(min=min_px),
                    reply_markup=main_menu_keyboard(ctx, update=update)
                )
                return ConversationHandler.END

        res = await place_order_all_accounts(
            user_id=uid,
            symbol=symbol,
            side=side,
            orderType=typ,
            qty=q,
            price=px_adj if typ == "Limit" else None,
            strategy="manual",
            add_position=(typ == "Market"),  # Only add position for Market orders
        )

        if typ == "Limit":
            await update.message.reply_text(
                ctx.t['order_success'] + f"\n{symbol} {('LONG' if side=='Buy' else 'SHORT')} @ {px_adj} qty={q}",
                reply_markup=main_menu_keyboard(ctx, update=update)
            )
        else:
            await update.message.reply_text(
                ctx.t['order_success'] + f"\n{symbol} {('LONG' if side=='Buy' else 'SHORT')} (Market) qty={q}",
                reply_markup=main_menu_keyboard(ctx, update=update)
            )

    except ValueError as ve:
        await update.message.reply_text(
            ctx.t.get("error_validation", "❌ {msg}").format(msg=str(ve)),
            reply_markup=main_menu_keyboard(ctx, update=update)
        )
    except Exception:
        logger.exception("Error placing order")
        await update.message.reply_text(
            ctx.t['order_create_error'].format(msg="internal error"),
            reply_markup=main_menu_keyboard(ctx, update=update)
        )
    finally:
        ctx.user_data.pop('manual_order_type', None)

    return ConversationHandler.END

@log_calls
async def fetch_coindesk_news(limit: int = 5) -> list[dict]:
    url = "https://www.coindesk.com/arc/outboundfeeds/rss/"
    if _session is None:
        await init_session()

    text = None
    for attempt in (1, 2):
        try:
            async with _session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    break
        except Exception:
            pass
        if attempt == 1:
            await asyncio.sleep(1.5)
    if not text:
        return []

    d = feedparser.parse(text)
    news = []
    for entry in d.entries[:limit]:
        title = entry.title
        link  = entry.link
        desc  = re.sub(r'<[^>]+>', '', entry.summary or '').strip()
        img = None
        mc = entry.get("media_content") or []
        if mc and isinstance(mc, list):
            img = (mc[0] or {}).get("url")
        if not img:
            m = re.search(r'<img[^>]+src="([^"]+)"', entry.summary or "")
            img = m.group(1) if m else None

        news.append({"title": title, "link": link, "description": desc, "image": img})
    return news


@require_access
@with_texts
@log_calls
async def cmd_market(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    loader = await ctx.bot.send_message(chat_id, ctx.t['loader'])
    try:
        await ctx.bot.delete_message(chat_id, loader.message_id)
    except Exception:
        pass
    btc_dom, usdt_dom, btc_price, btc_change, sp500, sp500_change, top_coins, gold_price, gold_change, total1, total2, total3, fear_greed, fear_greed_label, altseason_index = await fetch_market_status()
    prev_dom = get_prev_btc_dom()
    store_prev_btc_dom(btc_dom)
    if prev_dom is None:
        dom_trend = "unknown"
    elif btc_dom > prev_dom:
        dom_trend = "rising"      
    elif btc_dom < prev_dom:
        dom_trend = "falling"     
    else:
        dom_trend = "stable"      

    if dom_trend == "falling":
        alt_signal = "LONG" if btc_change > 0 else "NEUTRAL"
    else:
        alt_signal = "SHORT"

    save_market_snapshot(
        dom=btc_dom,
        price=btc_price,
        change=btc_change,
        alt_signal=alt_signal
    )
    emoji_map = {
        "LONG":    ctx.t["emoji_long"],
        "SHORT":   ctx.t["emoji_short"],
        "NEUTRAL": ctx.t["emoji_neutral"],
    }
    dom_emo = {
        "rising":  ctx.t['dominance_rising'],
        "falling": ctx.t['dominance_falling'],
        "stable":  ctx.t['dominance_stable'],
        "unknown": ctx.t['dominance_unknown']
    }[dom_trend]

    # S&P 500 emoji
    sp_emoji = "📈" if sp500_change > 0 else "📉" if sp500_change < 0 else "➖"
    btc_emoji = "📈" if btc_change > 0 else "📉" if btc_change < 0 else "➖"
    gold_emoji = "📈" if gold_change > 0 else "📉" if gold_change < 0 else "➖"

    # Fear & Greed emoji
    if fear_greed >= 75:
        fg_emoji = "🟢"  # Extreme Greed
    elif fear_greed >= 55:
        fg_emoji = "🟡"  # Greed
    elif fear_greed >= 45:
        fg_emoji = "⚪"  # Neutral
    elif fear_greed >= 25:
        fg_emoji = "🟠"  # Fear
    else:
        fg_emoji = "🔴"  # Extreme Fear

    # Altseason emoji
    if altseason_index >= 75:
        alt_emoji = "🚀"  # Altseason
    elif altseason_index >= 50:
        alt_emoji = "📈"
    elif altseason_index >= 25:
        alt_emoji = "📉"
    else:
        alt_emoji = "❄️"  # Bitcoin Season

    # Build top coins table
    top_coins_text = ""
    if top_coins:
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        top_coins_text = f"\n\n📊 *{ctx.t.get('market_dominance_header', 'Top Coins by Dominance')}:*\n"
        top_coins_text += "```\n"
        for i, (symbol, mcap_b, dom) in enumerate(top_coins[:5]):
            medal = medals[i] if i < len(medals) else f"{i+1}."
            top_coins_text += f"{medal} {symbol:<5} {dom:>5.2f}%\n"
        top_coins_text += "```"

    # Build Total Market Cap info
    total_text = ""
    if total1 > 0:
        total_text = (
            f"\n\n💰 *{ctx.t.get('market_total_header', 'Total Market Cap')}:*\n"
            f"• Total 1: ${total1:.2f}T\n"
            f"• Total 2: ${total2:.2f}T\n"
            f"• Total 3: ${total3:.2f}T"
        )

    # Build indices section
    indices_text = ""
    if fear_greed > 0 or altseason_index > 0:
        indices_text = f"\n\n🎭 *{ctx.t.get('market_indices_header', 'Market Indices')}:*\n"
        if fear_greed > 0:
            indices_text += f"• Fear & Greed: {fg_emoji} {fear_greed} ({fear_greed_label})\n"
        if altseason_index > 0:
            indices_text += f"• Altseason Index: {alt_emoji} {altseason_index}"

    header = (
        f"{ctx.t['market_status_heading']}\n\n"
        f"• BTC: ${btc_price:,.0f} {btc_emoji} {btc_change:+.2f}%\n"
        f"• {ctx.t['btc_dominance']}: {btc_dom:.2f}% ({dom_emo})\n"
        f"• {ctx.t['usdt_dominance']}: {usdt_dom:.2f}%\n"
        f"• S&P 500: {sp500:,.0f} {sp_emoji} {sp500_change:+.2f}%\n"
        f"• Gold: ${gold_price:,.0f} {gold_emoji} {gold_change:+.2f}%\n\n"
        f"• {ctx.t['alt_signal_label']}: {emoji_map[alt_signal]} *{ctx.t[f'alt_signal_{alt_signal.lower()}']}*"
        f"{indices_text}"
        f"{top_coins_text}"
        f"{total_text}"
    )
    await ctx.bot.send_message(chat_id, header, parse_mode="Markdown")

@log_calls
async def place_order(
    user_id: int,
    symbol: str,
    side: str,                 # "Buy" / "Sell"
    orderType: str,            # "Limit" / "Market"
    qty: float,
    price: float | None = None,
    timeInForce: str = "GTC",
    account_type: str = None,
):
    # Нормализация количества/цены под шаги инструмента
    qty_str, price_str, min_qty, max_qty, tick_size = await normalize_qty_price(
        user_id, symbol, orderType, qty, price, account_type=account_type
    )

    logger.debug(
        f"▶ place_order: {symbol} {side} {orderType} "
        f"raw_qty={qty}, min_qty={min_qty}, max_qty={max_qty} → send qty={qty_str}"
        + (f", price={price_str}" if price_str else "")
        + f" [{account_type or 'auto'}]"
    )

    import uuid
    order_link_id = f"tg_{uuid.uuid4().hex[:32]}"

    body = {
        "category":     "linear",
        "symbol":       symbol,
        "side":         side,
        "orderType":    orderType,          # "Limit" | "Market"
        "qty":          qty_str,            # для Market — это base qty
        "orderLinkId":  order_link_id,      # правильное имя ключа на Bybit v5
    }

    if orderType == "Limit":
        # Для лимиток — цена обязательна и TIF имеет смысл
        body["price"] = price_str
        body["timeInForce"] = timeInForce or "GTC"
    else:
        # Для Market — цену НЕ отправляем; TIF лучше явно как IOC
        body.pop("price", None)
        body["timeInForce"] = "IOC"

    # Проставляем корректный positionIdx (hedge/one_way)
    mode = await get_position_mode(user_id, symbol, account_type=account_type)
    body["positionIdx"] = position_idx_for(side, mode)

    try:
        res = await _bybit_request(user_id, "POST", "/v5/order/create", body=body, account_type=account_type)
    except RuntimeError as e:
        msg = str(e).lower()

        # Денег нет — сразу human-readable ошибка (110007: ab not enough, insufficient balance)
        if "insufficient" in msg or "balance" in msg or "110007" in msg or "ab not enough" in msg:
            # Log full error and order params for debugging
            logger.error(f"[{user_id}] INSUFFICIENT_BALANCE error. Order body: {body}. Full error: {e}")
            raise ValueError("INSUFFICIENT_BALANCE")

        # Неправильный position mode — меняем и ретраим
        if "position idx not match position mode" in msg:
            alt_mode = "one_way" if mode == "hedge" else "hedge"
            body["positionIdx"] = position_idx_for(side, alt_mode)
            _position_mode_cache[(user_id, symbol, account_type or "auto")] = alt_mode
            logger.info(f"{symbol}: retry with alt position mode {alt_mode}")
            res = await _bybit_request(user_id, "POST", "/v5/order/create", body=body, account_type=account_type)

        # Ошибка кредитного плеча — пытаемся извлечь maxLeverage из ошибки и установить
        elif "110013" in msg or "cannot set leverage" in msg:
            # Try to extract maxLeverage from error message: "gt maxLeverage [500]"
            import re
            match = re.search(r'maxLeverage\s*\[(\d+)\]', str(e))
            target_lev = int(match.group(1)) if match else 10
            
            logger.info(f"{symbol}: leverage error → trying to set {target_lev}x")
            lev_success = await set_leverage(user_id, symbol, leverage=target_lev, account_type=account_type)
            
            # If set_leverage failed, try progressively lower values
            if not lev_success:
                for fallback in [5, 3, 2, 1]:
                    logger.info(f"{symbol}: trying fallback leverage {fallback}x")
                    if await set_leverage(user_id, symbol, leverage=fallback, account_type=account_type):
                        break
            
            res = await _bybit_request(user_id, "POST", "/v5/order/create", body=body, account_type=account_type)

        # Ошибка 110090 - позиция превышает лимит, нужно снизить плечо до 45 или ниже
        elif "110090" in msg or "exceed the max" in msg:
            logger.info(f"{symbol}: max position limit error → reduce leverage to 45x and retry")
            await set_leverage(user_id, symbol, leverage=45, account_type=account_type)
            try:
                res = await _bybit_request(user_id, "POST", "/v5/order/create", body=body, account_type=account_type)
            except RuntimeError as e2:
                # Если всё ещё не работает - пробуем с 25x
                if "110090" in str(e2).lower() or "exceed the max" in str(e2).lower():
                    logger.info(f"{symbol}: still exceeds limit → reduce leverage to 25x and retry")
                    await set_leverage(user_id, symbol, leverage=25, account_type=account_type)
                    res = await _bybit_request(user_id, "POST", "/v5/order/create", body=body, account_type=account_type)
                else:
                    raise

        # Неверный TIF для рынка — поправим на IOC и ретраим
        elif "timeinforce" in msg and "market" in msg:
            if body.get("orderType") == "Market":
                body["timeInForce"] = "IOC"
                res = await _bybit_request(user_id, "POST", "/v5/order/create", body=body, account_type=account_type)
            else:
                raise

        else:
            raise

    logger.info(f"Order placed [{account_type or 'auto'}]: {res}")
    return res


@log_calls
async def place_order_all_accounts(
    user_id: int,
    symbol: str,
    side: str,
    orderType: str,
    qty: float,
    price: float | None = None,
    timeInForce: str = "GTC",
    strategy: str = None,
    leverage: int = None,
    signal_id: int | None = None,
    timeframe: str = "24h",
    add_position: bool = True,  # Whether to add position to DB
) -> dict:
    """
    DEPRECATED: Use place_order_for_targets() for multi-exchange support.
    
    Place order on all active accounts based on strategy's trading_mode or global trading_mode.
    If trading_mode is 'both', places order on both demo and real accounts.
    Also adds active positions to DB with correct account_type for each successful order.
    Returns dict with results per account type.
    """
    # Forward to new function using legacy mode
    return await place_order_for_targets(
        user_id=user_id,
        symbol=symbol,
        side=side,
        orderType=orderType,
        qty=qty,
        price=price,
        timeInForce=timeInForce,
        strategy=strategy,
        leverage=leverage,
        signal_id=signal_id,
        timeframe=timeframe,
        add_position=add_position,
        use_legacy_routing=True  # Use old account_types logic
    )


@log_calls
async def place_order_for_targets(
    user_id: int,
    symbol: str,
    side: str,
    orderType: str,
    qty: float,
    price: float | None = None,
    timeInForce: str = "GTC",
    strategy: str = None,
    leverage: int = None,
    signal_id: int | None = None,
    timeframe: str = "24h",
    add_position: bool = True,
    targets: list[dict] = None,  # Explicit targets list
    use_legacy_routing: bool = False,  # Use old account_types logic
) -> dict:
    """
    Place order on specified targets (supports Bybit + HyperLiquid).
    
    Target format: {"exchange": "bybit", "env": "paper", "account_type": "demo"}
    
    Features:
    - Multi-exchange support (Bybit + HyperLiquid)
    - Per-target qty calculation (future: can be different per target)
    - Per-target leverage/SL/TP
    - Unique client_order_id per target: {signal_id}-{exchange}-{env}
    
    Returns dict with results per target key (e.g., "bybit:paper": {...})
    """
    from db import get_execution_targets, get_live_enabled
    
    # Determine targets
    if targets is None:
        if use_legacy_routing:
            # Use old account_types logic for backward compatibility
            if strategy:
                account_types = get_strategy_account_types(user_id, strategy)
            else:
                account_types = get_active_account_types(user_id)
            
            if not account_types:
                raise ValueError("No API credentials configured")
            
            # Convert to targets format
            exchange = db.get_exchange_type(user_id)
            targets = []
            for acc_type in account_types:
                env = "paper" if acc_type in ("demo", "testnet") else "live"
                targets.append({
                    "exchange": exchange,
                    "env": env,
                    "account_type": acc_type
                })
        else:
            # Use new routing policy system
            targets = get_execution_targets(user_id, strategy)
    
    if not targets:
        raise ValueError("No execution targets configured")
    
    # Get default leverage from user config if not specified
    if leverage is None:
        cfg = get_user_config(user_id)
        leverage = cfg.get('leverage', 10)
    
    results = {}
    errors = []
    
    for target in targets:
        target_exchange = target.get("exchange", "bybit")
        target_env = target.get("env", "paper")
        target_account_type = target.get("account_type")
        target_key = f"{target_exchange}:{target_env}"
        
        # Generate unique client_order_id for this target
        client_order_id = f"{signal_id or 'manual'}-{target_exchange[:2]}-{target_env[:1]}-{int(time.time())}"
        
        try:
            if target_exchange == "hyperliquid":
                # ═══════════════════════════════════════════════════════════
                # HyperLiquid order
                # ═══════════════════════════════════════════════════════════
                is_testnet = (target_env == "paper" or target_account_type == "testnet")
                
                # Set leverage first
                try:
                    hl_creds = db.get_hl_credentials(user_id)
                    if hl_creds.get("hl_private_key"):
                        adapter = HLAdapter(
                            private_key=hl_creds["hl_private_key"],
                            testnet=is_testnet,
                            vault_address=hl_creds.get("hl_vault_address")
                        )
                        await adapter.set_leverage(hl_symbol_to_coin(symbol), leverage)
                        await adapter.close()
                except Exception as lev_err:
                    logger.warning(f"[{user_id}] Failed to set HL leverage for {symbol}: {lev_err}")
                
                # Place order
                res = await place_order_hyperliquid(
                    user_id=user_id,
                    symbol=symbol,
                    side=side,
                    orderType=orderType,
                    qty=qty,
                    price=price,
                    account_type=target_account_type or ("testnet" if is_testnet else "mainnet")
                )
                results[target_key] = {"success": True, "result": res, "exchange": target_exchange}
                logger.info(f"✅ [{target_key.upper()}] {orderType} order placed: {symbol} {side}")
                
            else:
                # ═══════════════════════════════════════════════════════════
                # Bybit order
                # ═══════════════════════════════════════════════════════════
                acc_type = target_account_type or ("demo" if target_env == "paper" else "real")
                
                # Set leverage first
                try:
                    await set_leverage(user_id, symbol, leverage=leverage, account_type=acc_type)
                except Exception as lev_err:
                    logger.warning(f"[{user_id}] Failed to set Bybit leverage for {symbol}: {lev_err}")
                
                # Place order
                res = await place_order(user_id, symbol, side, orderType, qty, price, timeInForce, account_type=acc_type)
                results[target_key] = {"success": True, "result": res, "exchange": target_exchange}
                logger.info(f"✅ [{target_key.upper()}] {orderType} order placed: {symbol} {side}")
            
            # Store position in DB with correct target info
            if add_position and orderType == "Market":
                # Get current price for entry_price
                entry_price = price if price else 0
                if not entry_price:
                    try:
                        if target_exchange == "hyperliquid":
                            # Get price from HL
                            hl_creds = db.get_hl_credentials(user_id)
                            if hl_creds.get("hl_private_key"):
                                adapter = HLAdapter(
                                    private_key=hl_creds["hl_private_key"],
                                    testnet=(target_env == "paper")
                                )
                                price_data = await adapter.get_price(hl_symbol_to_coin(symbol))
                                entry_price = float(price_data) if price_data else 0
                                await adapter.close()
                        else:
                            # Get price from Bybit
                            ticker_data = await _bybit_request(
                                user_id, "GET", "/v5/market/tickers",
                                params={"category": "linear", "symbol": symbol},
                                account_type=target_account_type or "demo"
                            )
                            ticker_list = ticker_data.get("list", [])
                            if ticker_list:
                                entry_price = float(ticker_list[0].get("lastPrice", 0))
                    except Exception:
                        pass  # Will be updated by monitoring
                
                # P0.5: Get use_atr from strategy settings
                cfg = get_user_config(user_id) or {}
                trade_params = get_strategy_trade_params(user_id, cfg, symbol, strategy or "manual", 
                                                         side=side, exchange=target_exchange, 
                                                         account_type=target_account_type)
                pos_use_atr = trade_params.get("use_atr", False)
                
                add_active_position(
                    user_id=user_id,
                    signal_id=signal_id,
                    symbol=symbol,
                    side=side,
                    size=qty,
                    entry_price=entry_price,
                    timeframe=timeframe,
                    strategy=strategy,
                    account_type=target_account_type or ("demo" if target_env == "paper" else "real"),
                    exchange=target_exchange,
                    env=target_env,
                    client_order_id=client_order_id,
                    use_atr=pos_use_atr,  # P0.5: Pass ATR setting
                    leverage=leverage  # Save leverage used for this order
                )
                logger.info(f"📊 [{target_key.upper()}] Position saved to DB: {symbol} {side} @ {entry_price} (use_atr={pos_use_atr}, leverage={leverage})")
                
        except Exception as e:
            results[target_key] = {"success": False, "error": str(e), "exchange": target_exchange}
            errors.append(f"[{target_key.upper()}] {str(e)}")
            logger.error(f"❌ [{target_key.upper()}] {orderType} order failed for {symbol}: {e}")
    
    if errors and not any(r["success"] for r in results.values()):
        raise RuntimeError(f"All orders failed: {'; '.join(errors)}")
    
    return results


# ═══════════════════════════════════════════════════════════════════════
# ██  HYPERLIQUID ORDER EXECUTION  ██
# ═══════════════════════════════════════════════════════════════════════

# Cache for HyperLiquid available coins
_hl_coins_cache = {"coins": set(), "timestamp": 0, "ttl": 300}  # 5 min cache

async def get_hl_available_coins() -> set:
    """Get set of available coin symbols on HyperLiquid."""
    import time
    now = time.time()
    
    if _hl_coins_cache["coins"] and (now - _hl_coins_cache["timestamp"]) < _hl_coins_cache["ttl"]:
        return _hl_coins_cache["coins"]
    
    try:
        from hyperliquid import HyperLiquidClient
        # Use read-only client just to get coin list
        client = HyperLiquidClient(testnet=False)
        await client.initialize()
        mids = await client.get_all_mids()
        await client.close()
        
        # Convert to USDT format for comparison (HL uses BTC, we compare BTCUSDT)
        coins = {f"{coin}USDT" for coin in mids.keys()}
        _hl_coins_cache["coins"] = coins
        _hl_coins_cache["timestamp"] = now
        return coins
    except Exception as e:
        logger.warning(f"Failed to get HL coins: {e}")
        return set()


def hl_symbol_to_coin(symbol: str) -> str:
    """Convert BTCUSDT to BTC for HyperLiquid."""
    if symbol.endswith("USDT"):
        return symbol[:-4]
    if symbol.endswith("USDC"):
        return symbol[:-4]
    return symbol


async def place_order_hyperliquid(
    user_id: int,
    symbol: str,
    side: str,
    qty: float,
    strategy: str,
    leverage: int = None,
    sl_percent: float = None,
    tp_percent: float = None,
) -> dict | None:
    """
    Place order on HyperLiquid if:
    1. User has HL credentials configured
    2. HL is enabled for this strategy
    3. The coin is available on HL
    
    Returns result dict or None if not executed.
    """
    try:
        # Check if HL is enabled for this strategy
        hl_settings = db.get_hl_effective_settings(user_id, strategy)
        if not hl_settings.get("enabled"):
            return None
        
        # Check if user has HL credentials
        hl_creds = get_hl_credentials(user_id)
        if not hl_creds.get("hl_private_key"):
            logger.debug(f"[{user_id}] No HL private key configured")
            return None
        
        # Check if coin is available on HL
        available_coins = await get_hl_available_coins()
        if symbol not in available_coins:
            logger.debug(f"[{user_id}] {symbol} not available on HyperLiquid")
            return None
        
        # Get HL-specific settings
        hl_percent = hl_settings.get("percent", 1.0)
        hl_sl = hl_settings.get("sl_percent", sl_percent or 2.0)
        hl_tp = hl_settings.get("tp_percent", tp_percent or 3.0)
        hl_leverage = hl_settings.get("leverage", leverage or 10)
        
        # Create adapter
        testnet = hl_creds.get("hl_testnet", False)
        adapter = HLAdapter(
            private_key=hl_creds["hl_private_key"],
            testnet=testnet,
            vault_address=hl_creds.get("hl_vault_address")
        )
        
        async with adapter:
            # Get current price
            coin = hl_symbol_to_coin(symbol)
            price = await adapter._client.get_mid_price(coin)
            if not price:
                logger.warning(f"[{user_id}] Could not get price for {coin} on HL")
                return None
            
            # Calculate qty based on HL percent
            user_state = await adapter._client.user_state()
            margin_summary = user_state.get("marginSummary", {})
            account_value = float(margin_summary.get("accountValue", 0))
            
            if account_value <= 0:
                logger.warning(f"[{user_id}] HL account value is 0")
                return None
            
            # Calculate position size
            position_value = account_value * (hl_percent / 100)
            hl_qty = position_value / price
            
            # Round qty to appropriate decimals
            hl_qty = round(hl_qty, 4)
            if hl_qty <= 0:
                return None
            
            # Set leverage first (required before placing order)
            is_buy = side.lower() in ("buy", "long")
            try:
                await adapter._client.update_leverage(coin=coin, leverage=hl_leverage, is_cross=True)
            except Exception as lev_err:
                logger.warning(f"[{user_id}] Could not set HL leverage: {lev_err}")
            
            # Place market order
            result = await adapter._client.market_open(
                coin=coin,
                is_buy=is_buy,
                sz=hl_qty,
                slippage=0.01  # 1% slippage
            )
            
            # Set TP/SL if provided
            if result.get("status") == "ok" and (hl_tp or hl_sl):
                try:
                    tp_price = None
                    sl_price = None
                    if hl_tp and hl_tp > 0:
                        tp_price = price * (1 + hl_tp / 100) if is_buy else price * (1 - hl_tp / 100)
                    if hl_sl and hl_sl > 0:
                        sl_price = price * (1 - hl_sl / 100) if is_buy else price * (1 + hl_sl / 100)
                    await adapter._client.set_tp_sl(coin=coin, tp_price=tp_price, sl_price=sl_price)
                except Exception as tpsl_err:
                    logger.warning(f"[{user_id}] Could not set HL TP/SL: {tpsl_err}")
            
            logger.info(f"✅ [{user_id}] HL order placed: {symbol} {side} qty={hl_qty} lev={hl_leverage}x")
            return {
                "success": True,
                "exchange": "hyperliquid",
                "testnet": testnet,
                "symbol": symbol,
                "side": side,
                "qty": hl_qty,
                "leverage": hl_leverage,
                "result": result
            }
            
    except Exception as e:
        logger.error(f"[{user_id}] HL order failed for {symbol}: {e}")
        return {"success": False, "error": str(e), "exchange": "hyperliquid"}


@require_access
@with_texts
@log_calls
async def cmd_toggle_oi(update, ctx):
    uid = update.effective_user.id
    cfg = get_user_config(uid) or {}
    new = not bool(cfg.get("trade_oi", 0))
    set_user_field(uid, "trade_oi", int(new))
    await update.message.reply_text(
        ctx.t['toggle_oi_status'].format(
            feature=ctx.t['feature_oi'],
            status=ctx.t['status_enabled'] if new else ctx.t['status_disabled']
        ),
        reply_markup=main_menu_keyboard(ctx, update=update)
    )

@require_access
@with_texts
@log_calls
async def cmd_toggle_scryptomera(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cfg = get_user_config(uid)
    new = 0 if cfg.get("trade_scryptomera", 0) else 1
    set_user_field(uid, "trade_scryptomera", new)

    emoji = ctx.t["emoji_long"] if new else ctx.t["emoji_short"]
    status = ctx.t['status_enabled'] if new else ctx.t['status_disabled']
    feature_name = ctx.t.get('feature_scryptomera', 'Scryptomera')

    await update.message.reply_text(
        f"{emoji} {feature_name}: {status}",
        reply_markup=main_menu_keyboard(ctx, update=update)
    )

@require_access
@with_texts
@log_calls
async def cmd_toggle_scalper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cfg = get_user_config(uid)
    new = 0 if cfg.get("trade_scalper", 0) else 1
    set_user_field(uid, "trade_scalper", new)

    emoji = ctx.t["emoji_long"] if new else ctx.t["emoji_short"]
    status = ctx.t['status_enabled'] if new else ctx.t['status_disabled']
    feature_name = ctx.t.get('feature_scalper', 'Scalper')

    await update.message.reply_text(
        f"{emoji} {feature_name}: {status}",
        reply_markup=main_menu_keyboard(ctx, update=update)
    )


@require_access
@with_texts
@log_calls
async def cmd_toggle_elcaro(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cfg = get_user_config(uid)
    new = 0 if cfg.get("trade_elcaro", 0) else 1
    set_user_field(uid, "trade_elcaro", new)

    emoji = ctx.t["emoji_long"] if new else ctx.t["emoji_short"]
    status = ctx.t['status_enabled'] if new else ctx.t['status_disabled']
    feature_name = ctx.t.get('feature_elcaro', 'Elcaro')

    await update.message.reply_text(
        f"{emoji} {feature_name}: {status}",
        reply_markup=main_menu_keyboard(ctx, update=update)
    )


@require_access
@with_texts
@log_calls
async def cmd_toggle_fibonacci(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cfg = get_user_config(uid)
    new = 0 if cfg.get("trade_fibonacci", 0) else 1
    set_user_field(uid, "trade_fibonacci", new)

    emoji = ctx.t["emoji_long"] if new else ctx.t["emoji_short"]
    status = ctx.t['status_enabled'] if new else ctx.t['status_disabled']
    feature_name = ctx.t.get('feature_fibonacci', 'Fibonacci')

    await update.message.reply_text(
        f"{emoji} {feature_name}: {status}",
        reply_markup=main_menu_keyboard(ctx, update=update)
    )


# ------------------------------------------------------------------------------------
# Strategy Settings with Inline Keyboard
# ------------------------------------------------------------------------------------

def _build_strategy_status_parts(strat_key: str, strat_settings: dict, active_exchange: str = "bybit", global_use_atr: bool = True) -> list:
    """
    Build status parts list for a strategy based on its settings.
    Used consistently across all menus to show strategy customizations.
    
    Args:
        strat_key: Strategy name
        strat_settings: Strategy-specific settings dict
        active_exchange: Current exchange (bybit/hyperliquid)
        global_use_atr: User's global ATR setting (fallback when strategy doesn't override)
    """
    status_parts = []
    
    pct = strat_settings.get("percent")
    sl = strat_settings.get("sl_percent")
    tp = strat_settings.get("tp_percent")
    atr_per = strat_settings.get("atr_periods")
    atr_mult = strat_settings.get("atr_multiplier_sl")
    atr_trig = strat_settings.get("atr_trigger_pct")
    use_atr_strat = strat_settings.get("use_atr")  # None = global, 0 = Fixed, 1 = ATR
    mode = strat_settings.get("trading_mode", "global")
    if mode == "all":
        mode = "global"  # Normalize legacy value
    
    # Determine effective use_atr: strategy-specific overrides global
    use_atr = use_atr_strat if use_atr_strat is not None else (1 if global_use_atr else 0)
    
    # Exchange-aware mode text
    if active_exchange == "hyperliquid":
        mode_text = {"testnet": "Testnet", "mainnet": "Mainnet", "both": "Both", "global": "Global", "demo": "Testnet", "real": "Mainnet"}.get(mode, "Global")
    else:
        mode_text = {"demo": "Demo", "real": "Real", "both": "Both", "global": "Global", "testnet": "Demo", "mainnet": "Real"}.get(mode, "Global")
    
    # For scryptomera and scalper, show side-specific or direction info
    if strat_key in ("scryptomera", "scalper"):
        direction = strat_settings.get("direction", "all")
        dir_emoji = {"all": "🔄", "long": "📈", "short": "📉"}.get(direction, "🔄")
        status_parts.append(f"{dir_emoji}")
        
        # Check for side-specific settings
        l_pct = strat_settings.get("long_percent")
        l_sl = strat_settings.get("long_sl_percent")
        s_pct = strat_settings.get("short_percent")
        s_sl = strat_settings.get("short_sl_percent")
        
        has_side_specific = (l_pct is not None or l_sl is not None or 
                            s_pct is not None or s_sl is not None)
        
        if has_side_specific:
            # Show side-specific settings
            if l_pct is not None or l_sl is not None:
                status_parts.append(f"L:{l_pct or '-'}%/{l_sl or '-'}%")
            if s_pct is not None or s_sl is not None:
                status_parts.append(f"S:{s_pct or '-'}%/{s_sl or '-'}%")
        else:
            # Show general settings if no side-specific overrides
            if pct is not None:
                status_parts.append(f"Entry: {pct}%")
            if sl is not None:
                status_parts.append(f"SL: {sl}%")
            if tp is not None:
                status_parts.append(f"TP: {tp}%")
    else:
        # General settings for other strategies
        if pct is not None:
            status_parts.append(f"Entry: {pct}%")
        if sl is not None:
            status_parts.append(f"SL: {sl}%")
        if tp is not None:
            status_parts.append(f"TP: {tp}%")
    
    # ATR status - ALWAYS show (with effective value: strategy or global fallback)
    atr_emoji = "⚡" if use_atr else "📉"
    status_parts.append(f"{atr_emoji}ATR:{'ON' if use_atr else 'OFF'}")
    
    if atr_per is not None:
        status_parts.append(f"ATR: {atr_per}p")
    if atr_mult is not None:
        status_parts.append(f"Mult: {atr_mult}")
    if atr_trig is not None:
        status_parts.append(f"Trig: {atr_trig}%")
    if mode != "global":
        status_parts.append(f"Mode: {mode_text}")
    
    return status_parts


STRATEGY_NAMES_MAP = {
    "oi": "OI",
    "rsi_bb": "RSI+BB",
    "scryptomera": "Scryptomera",
    "scalper": "Scalper",
    "elcaro": "Elcaro",
    "fibonacci": "Fibonacci",
}


def build_strategy_settings_text(strategy: str, strat_settings: dict, t: dict) -> str:
    """Build strategy settings display text based on STRATEGY_FEATURES.
    
    Returns formatted markdown text showing only relevant settings for the strategy.
    """
    features = STRATEGY_FEATURES.get(strategy, {})
    display_name = STRATEGY_NAMES_MAP.get(strategy, strategy.upper())
    global_lbl = t.get('global_default', 'Global')
    
    lines = [t.get('strategy_param_header', '⚙️ *{name} Settings*').format(name=display_name)]
    lines.append("")
    
    # Order type
    if features.get("order_type"):
        order_type = strat_settings.get("order_type", "market")
        order_emoji = "🎯" if order_type == "limit" else "⚡"
        order_label = "Limit" if order_type == "limit" else "Market"
        lines.append(f"*Order Type*: {order_emoji} {order_label}")
    
    # Direction
    if features.get("direction"):
        direction = strat_settings.get("direction", "all")
        dir_emoji = {"all": "🔄", "long": "📈", "short": "📉"}.get(direction, "🔄")
        dir_label = {"all": "ALL", "long": "LONG only", "short": "SHORT only"}.get(direction, "ALL")
        lines.append(f"*Direction*: {dir_emoji} {dir_label}")
    
    # Position size (for strategies that show it on main screen)
    if features.get("percent"):
        pct = strat_settings.get("percent")
        lines.append(f"📊 Position Size: {pct if pct is not None else global_lbl}%")
    
    # Leverage
    if features.get("leverage"):
        leverage = strat_settings.get("leverage")
        lines.append(f"⚡ Leverage: {leverage if leverage else 'Auto'}x")
    
    # ATR toggle
    if features.get("use_atr"):
        use_atr = strat_settings.get("use_atr") or 0
        atr_status = "✅ Enabled" if use_atr else "❌ Disabled"
        lines.append(f"📊 ATR Trailing: {atr_status}")
    
    # SL/TP on main screen (for simple strategies)
    if features.get("sl_tp"):
        sl = strat_settings.get("sl_percent")
        tp = strat_settings.get("tp_percent")
        lines.append(f"🔻 SL: {sl if sl is not None else global_lbl}%")
        lines.append(f"🔺 TP: {tp if tp is not None else global_lbl}%")
    
    # Coins group
    if features.get("coins_group"):
        coins_group = strat_settings.get("coins_group")
        coins_label = coins_group if coins_group else "All"
        lines.append(f"🪙 Coins Filter: {coins_label}")
    
    # Min quality (Fibonacci)
    if features.get("min_quality"):
        min_quality = strat_settings.get("min_quality", 50)
        lines.append(f"⭐ Min Quality: {min_quality}%")
    
    # Side-specific summary
    if features.get("side_settings"):
        lines.append("")
        l_pct = strat_settings.get("long_percent")
        l_sl = strat_settings.get("long_sl_percent")
        l_tp = strat_settings.get("long_tp_percent")
        s_pct = strat_settings.get("short_percent")
        s_sl = strat_settings.get("short_sl_percent")
        s_tp = strat_settings.get("short_tp_percent")
        
        if strategy in ("elcaro", "fibonacci"):
            # Only show percent for these strategies
            if l_pct is not None:
                lines.append(f"📈 LONG: Entry={l_pct}%")
            if s_pct is not None:
                lines.append(f"📉 SHORT: Entry={s_pct}%")
        else:
            if any(v is not None for v in [l_pct, l_sl, l_tp]):
                lines.append(f"📈 LONG: Entry={l_pct or global_lbl}, SL={l_sl or global_lbl}, TP={l_tp or global_lbl}")
            if any(v is not None for v in [s_pct, s_sl, s_tp]):
                lines.append(f"📉 SHORT: Entry={s_pct or global_lbl}, SL={s_sl or global_lbl}, TP={s_tp or global_lbl}")
    
    return "\n".join(lines)


# Define which features each strategy supports for cleaner UI
# This controls which settings are shown in the strategy settings menu
STRATEGY_FEATURES = {
    "scryptomera": {
        "order_type": True,      # Market/Limit toggle
        "coins_group": True,     # Coins filter (ALL/TOP100/VOLATILE)
        "leverage": True,        # Leverage setting
        "use_atr": True,         # ATR trailing toggle
        "direction": True,       # LONG/SHORT/ALL filter
        "side_settings": True,   # Separate LONG/SHORT settings
        "percent": True,         # Global percent
        "sl_tp": True,           # SL/TP on main screen
        "atr_params": True,      # ATR params on main screen  
        "hl_settings": True,     # HyperLiquid support
        "min_quality": False,    # Scryptomera doesn't have quality filter
    },
    "scalper": {
        "order_type": True,
        "coins_group": True,
        "leverage": True,
        "use_atr": True,
        "direction": True,
        "side_settings": True,
        "percent": True,
        "sl_tp": True,
        "atr_params": True,
        "hl_settings": True,
        "min_quality": False,
    },
    "elcaro": {
        "order_type": False,     # Elcaro signals have their own order logic
        "coins_group": True,
        "leverage": False,       # From signal
        "use_atr": False,        # ATR managed by signal
        "direction": True,
        "side_settings": True,   # Only percent per side
        "percent": True,         # Global percent for this strategy
        "sl_tp": False,          # From signal
        "atr_params": False,     # From signal
        "hl_settings": True,
        "min_quality": False,
    },
    "fibonacci": {
        "order_type": True,      # Market/Limit toggle
        "coins_group": True,
        "leverage": True,
        "use_atr": True,         # ATR trailing option
        "direction": True,
        "side_settings": True,
        "percent": True,
        "sl_tp": True,           # Manual SL/TP override
        "atr_params": True,      # ATR params
        "hl_settings": True,
        "min_quality": True,     # Fibonacci-specific quality filter
    },
    "oi": {
        "order_type": True,
        "coins_group": True,
        "leverage": True,
        "use_atr": True,
        "direction": True,
        "side_settings": True,   # LONG/SHORT separate settings
        "percent": True,
        "sl_tp": True,           # Manual SL/TP
        "atr_params": True,      # Full ATR control
        "hl_settings": True,
        "min_quality": False,
    },
    "rsi_bb": {
        "order_type": True,
        "coins_group": True,
        "leverage": True,
        "use_atr": True,
        "direction": True,
        "side_settings": True,   # LONG/SHORT separate settings
        "percent": True,
        "sl_tp": True,
        "atr_params": True,
        "hl_settings": True,
        "min_quality": False,
    },
}

def get_strategy_settings_keyboard(t: dict, cfg: dict = None, uid: int = None) -> InlineKeyboardMarkup:
    """Build inline keyboard for strategy selection with enable/disable status and trading mode."""
    cfg = cfg or {}
    
    # Get user's trading context (exchange + account_type)
    if uid:
        context = get_user_trading_context(uid)
        active_exchange = context["exchange"]
        account_type = context["account_type"]
    else:
        active_exchange = "bybit"
        account_type = "demo"
    
    # Helper to get status emoji
    def status(key):
        return "✅" if cfg.get(key, 0) else "❌"
    
    # Helper to get trading mode for strategy - now exchange-aware
    def get_mode_emoji(strategy: str) -> str:
        if uid:
            strat_settings = db.get_strategy_settings(uid, strategy, active_exchange, account_type)
            mode = strat_settings.get("trading_mode", "global")
            # Normalize "all" to "global" for backwards compatibility
            if mode == "all":
                mode = "global"
        else:
            mode = "global"
        
        # Different labels for different exchanges
        if active_exchange == "hyperliquid":
            # HyperLiquid: testnet/mainnet
            return {
                "testnet": "T",   # Testnet
                "mainnet": "M",   # Mainnet (real)
                "both": "B",      # Both
                "global": "G",    # Global
                # Handle bybit modes if user switches exchange
                "demo": "T",      # Treat demo as testnet
                "real": "M",      # Treat real as mainnet
            }.get(mode, "G")
        else:
            # Bybit: demo/real
            return {
                "demo": "D",      # Demo
                "real": "R",      # Real
                "both": "B",      # Both
                "global": "G",    # Global
                # Handle HL modes if user switches exchange
                "testnet": "D",   # Treat testnet as demo
                "mainnet": "R",   # Treat mainnet as real
            }.get(mode, "G")
    
    # Get spot status
    spot_enabled = cfg.get("spot_enabled", 0)
    spot_status = "✅" if spot_enabled else "❌"
    spot_settings = cfg.get("spot_settings", {}) or {}
    spot_mode = spot_settings.get("trading_mode", "demo")
    spot_mode_emoji = {"demo": "D", "real": "R"}.get(spot_mode, "D")
    
    buttons = [
        [InlineKeyboardButton(f"{status('trade_oi')} 📊 OI", callback_data="strat_toggle:oi"),
         InlineKeyboardButton(get_mode_emoji("oi"), callback_data="strat_mode:oi"),
         InlineKeyboardButton(t.get('btn_settings_icon', '⚙️'), callback_data="strat_set:oi")],
        [InlineKeyboardButton(f"{status('trade_rsi_bb')} 📉 RSI+BB", callback_data="strat_toggle:rsi_bb"),
         InlineKeyboardButton(get_mode_emoji("rsi_bb"), callback_data="strat_mode:rsi_bb"),
         InlineKeyboardButton(t.get('btn_settings_icon', '⚙️'), callback_data="strat_set:rsi_bb")],
        [InlineKeyboardButton(f"{status('trade_scryptomera')} 🔮 Scryptom...", callback_data="strat_toggle:scryptomera"),
         InlineKeyboardButton(get_mode_emoji("scryptomera"), callback_data="strat_mode:scryptomera"),
         InlineKeyboardButton(t.get('btn_settings_icon', '⚙️'), callback_data="strat_set:scryptomera")],
        [InlineKeyboardButton(f"{status('trade_scalper')} 🎯 Scalper", callback_data="strat_toggle:scalper"),
         InlineKeyboardButton(get_mode_emoji("scalper"), callback_data="strat_mode:scalper"),
         InlineKeyboardButton(t.get('btn_settings_icon', '⚙️'), callback_data="strat_set:scalper")],
        [InlineKeyboardButton(f"{status('trade_elcaro')} 🔥 Elcaro", callback_data="strat_toggle:elcaro"),
         InlineKeyboardButton(get_mode_emoji("elcaro"), callback_data="strat_mode:elcaro"),
         InlineKeyboardButton(t.get('btn_settings_icon', '⚙️'), callback_data="strat_set:elcaro")],
        [InlineKeyboardButton(f"{status('trade_fibonacci')} 📐 Fibonacci", callback_data="strat_toggle:fibonacci"),
         InlineKeyboardButton(get_mode_emoji("fibonacci"), callback_data="strat_mode:fibonacci"),
         InlineKeyboardButton(t.get('btn_settings_icon', '⚙️'), callback_data="strat_set:fibonacci")],
        # Spot as a strategy
        [InlineKeyboardButton(f"{spot_status} 💹 Spot", callback_data="strat_toggle:spot"),
         InlineKeyboardButton(spot_mode_emoji, callback_data="strat_mode:spot"),
         InlineKeyboardButton(t.get('btn_settings_icon', '⚙️'), callback_data="strat_set:spot")],
        [InlineKeyboardButton(t.get('dca_settings', '⚙️ DCA Settings'), callback_data="strat_set:dca")],
        [InlineKeyboardButton(t.get('global_settings', '🌐 Global Settings'), callback_data="strat_set:global")],
        [InlineKeyboardButton(t.get('btn_close', '❌ Close'), callback_data="strat_set:close")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_strategy_param_keyboard(strategy: str, t: dict, strat_settings: dict = None) -> InlineKeyboardMarkup:
    """Build inline keyboard for editing strategy parameters.
    
    Uses STRATEGY_FEATURES config to determine which settings to show.
    Settings are grouped logically:
    1. Order settings (order_type)
    2. Position settings (percent, leverage)
    3. Risk settings (SL, TP, ATR)
    4. Filters (coins, direction)
    5. Side-specific settings (LONG/SHORT)
    6. Advanced (HyperLiquid, Reset)
    """
    display_name = STRATEGY_NAMES_MAP.get(strategy, strategy.upper())
    strat_settings = strat_settings or {}
    features = STRATEGY_FEATURES.get(strategy, {})
    
    buttons = []
    
    # ─── 1. ORDER SETTINGS ───
    if features.get("order_type"):
        order_type = strat_settings.get("order_type", "market")
        order_emoji = "🎯" if order_type == "limit" else "⚡"
        order_label = "Limit" if order_type == "limit" else "Market"
        buttons.append([InlineKeyboardButton(
            f"📤 {t.get('order_type', 'Order Type')}: {order_emoji} {order_label}",
            callback_data=f"strat_order_type:{strategy}:{order_type}"
        )])
    
    # ─── 2. POSITION SETTINGS ───
    if features.get("percent"):
        pct = strat_settings.get("percent")
        pct_label = f"{pct}%" if pct else t.get('global_default', 'Global')
        buttons.append([InlineKeyboardButton(
            f"📊 {t.get('position_size', 'Position Size')}: {pct_label}",
            callback_data=f"strat_param:{strategy}:percent"
        )])
    
    if features.get("leverage"):
        leverage = strat_settings.get("leverage")
        lev_label = f"{leverage}x" if leverage else t.get('auto_default', 'Auto')
        buttons.append([InlineKeyboardButton(
            f"⚡ {t.get('leverage', 'Leverage')}: {lev_label}",
            callback_data=f"strat_param:{strategy}:leverage"
        )])
    
    # ─── 3. RISK SETTINGS (ATR) ───
    if features.get("use_atr"):
        use_atr = strat_settings.get("use_atr") or 0
        atr_status = "✅" if use_atr else "❌"
        buttons.append([InlineKeyboardButton(
            f"📊 {t.get('atr_trailing', 'ATR Trailing')}: {atr_status}",
            callback_data=f"strat_atr_toggle:{strategy}"
        )])
    
    if features.get("sl_tp"):
        # SL/TP buttons (only for simple strategies without side-specific)
        sl = strat_settings.get("sl_percent")
        tp = strat_settings.get("tp_percent")
        sl_label = f"{sl}%" if sl else t.get('global_default', 'Global')
        tp_label = f"{tp}%" if tp else t.get('global_default', 'Global')
        buttons.append([InlineKeyboardButton(
            f"🔻 {t.get('stop_loss', 'Stop-Loss')}: {sl_label}",
            callback_data=f"strat_param:{strategy}:sl_percent"
        )])
        buttons.append([InlineKeyboardButton(
            f"🔺 {t.get('take_profit', 'Take-Profit')}: {tp_label}",
            callback_data=f"strat_param:{strategy}:tp_percent"
        )])
    
    if features.get("atr_params"):
        # Full ATR control (only when ATR is enabled and for simple strategies)
        use_atr = strat_settings.get("use_atr") or 0
        if use_atr:
            atr_periods = strat_settings.get("atr_periods")
            atr_mult = strat_settings.get("atr_multiplier_sl")
            atr_trigger = strat_settings.get("atr_trigger_pct")
            buttons.append([InlineKeyboardButton(
                f"📈 ATR Periods: {atr_periods or 'Auto'}",
                callback_data=f"strat_param:{strategy}:atr_periods"
            )])
            buttons.append([InlineKeyboardButton(
                f"📉 ATR Multiplier: {atr_mult or 'Auto'}",
                callback_data=f"strat_param:{strategy}:atr_multiplier_sl"
            )])
            buttons.append([InlineKeyboardButton(
                f"🎯 ATR Trigger %: {atr_trigger or 'Auto'}",
                callback_data=f"strat_param:{strategy}:atr_trigger_pct"
            )])
    
    # ─── 4. FILTERS ───
    if features.get("coins_group"):
        coins_group = strat_settings.get("coins_group")
        coins_label = coins_group if coins_group else t.get('all_coins', 'All')
        coins_emoji = {"ALL": "🌐", "TOP100": "💎", "VOLATILE": "🔥"}.get(coins_group, "🌐")
        buttons.append([InlineKeyboardButton(
            f"🪙 {t.get('coins_filter', 'Coins')}: {coins_emoji} {coins_label}",
            callback_data=f"strat_coins:{strategy}"
        )])
    
    if features.get("direction"):
        current_dir = strat_settings.get("direction", "all")
        dir_emoji = {"all": "🔄", "long": "📈", "short": "📉"}.get(current_dir, "🔄")
        dir_label = {"all": "ALL", "long": "LONG", "short": "SHORT"}.get(current_dir, "ALL")
        buttons.append([InlineKeyboardButton(
            f"🎯 {t.get('direction', 'Direction')}: {dir_emoji} {dir_label}",
            callback_data=f"{strategy}_dir:{current_dir}"
        )])
    
    # ─── FIBONACCI SPECIFIC ───
    if features.get("min_quality"):
        min_quality = strat_settings.get("min_quality", 50)
        buttons.append([InlineKeyboardButton(
            f"⭐ {t.get('min_quality', 'Min Quality')}: {min_quality}%",
            callback_data=f"strat_param:{strategy}:min_quality"
        )])
    
    # ─── 5. SIDE-SPECIFIC SETTINGS ───
    if features.get("side_settings"):
        buttons.append([
            InlineKeyboardButton(f"📈 {t.get('long_settings', 'LONG')}", callback_data=f"{strategy}_side:long"),
            InlineKeyboardButton(f"📉 {t.get('short_settings', 'SHORT')}", callback_data=f"{strategy}_side:short"),
        ])
    
    # ─── 6. ADVANCED ───
    if features.get("hl_settings"):
        buttons.append([InlineKeyboardButton(
            f"🔷 {t.get('hl_settings', 'HyperLiquid')}",
            callback_data=f"strat_hl:{strategy}"
        )])
    
    buttons.append([InlineKeyboardButton(
        f"🔄 {t.get('reset_to_global', 'Reset to Global')}",
        callback_data=f"strat_reset:{strategy}"
    )])
    buttons.append([InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="strat_set:back")])
    
    return InlineKeyboardMarkup(buttons)


def get_strategy_side_keyboard(strategy: str, side: str, t: dict, settings: dict = None) -> InlineKeyboardMarkup:
    """Build inline keyboard for ANY strategy's LONG or SHORT settings.
    
    Uses STRATEGY_FEATURES to show only relevant parameters for each strategy.
    - Elcaro: Only percent (signals provide SL/TP)
    - Scryptomera/Scalper: Full settings with ATR params
    - OI/RSI_BB: SL/TP (ATR params on main screen)
    """
    emoji = "📈" if side == "long" else "📉"
    features = STRATEGY_FEATURES.get(strategy, {})
    settings = settings or {}
    use_atr = settings.get("use_atr", 0)
    
    buttons = []
    
    # Always show percent (every strategy has side-specific percent)
    buttons.append([InlineKeyboardButton(
        f"{emoji} {t.get('param_percent', 'Entry %')}", 
        callback_data=f"strat_param:{strategy}:{side}_percent"
    )])
    
    # SL/TP only if strategy supports manual SL/TP OR has side settings
    # But Elcaro uses signal data - skip SL/TP for Elcaro
    if strategy not in ("elcaro", "fibonacci"):
        buttons.append([InlineKeyboardButton(
            f"{emoji} {t.get('param_sl', 'Stop-Loss %')}", 
            callback_data=f"strat_param:{strategy}:{side}_sl_percent"
        )])
        buttons.append([InlineKeyboardButton(
            f"{emoji} {t.get('param_tp', 'Take-Profit %')}", 
            callback_data=f"strat_param:{strategy}:{side}_tp_percent"
        )])
    
    # ATR params only for strategies that support ATR AND have ATR enabled
    if features.get("use_atr") and use_atr:
        buttons.append([InlineKeyboardButton(
            f"{emoji} {t.get('param_atr_periods', 'ATR Periods')}", 
            callback_data=f"strat_param:{strategy}:{side}_atr_periods"
        )])
        buttons.append([InlineKeyboardButton(
            f"{emoji} {t.get('param_atr_mult', 'ATR Multiplier')}", 
            callback_data=f"strat_param:{strategy}:{side}_atr_multiplier_sl"
        )])
        buttons.append([InlineKeyboardButton(
            f"{emoji} {t.get('param_atr_trigger', 'ATR Trigger %')}", 
            callback_data=f"strat_param:{strategy}:{side}_atr_trigger_pct"
        )])
    
    # Back button
    buttons.append([InlineKeyboardButton(
        t.get('btn_back', '⬅️ Back'), 
        callback_data=f"strat_set:{strategy}"
    )])
    
    return InlineKeyboardMarkup(buttons)


def get_scryptomera_side_keyboard(side: str, t: dict, settings: dict = None) -> InlineKeyboardMarkup:
    """Build inline keyboard for Scryptomera LONG or SHORT settings (legacy wrapper)."""
    return get_strategy_side_keyboard("scryptomera", side, t, settings)


def get_scalper_side_keyboard(side: str, t: dict, settings: dict = None) -> InlineKeyboardMarkup:
    """Build inline keyboard for Scalper LONG or SHORT settings (legacy wrapper)."""
    return get_strategy_side_keyboard("scalper", side, t, settings)


def get_dca_settings_keyboard(t: dict, cfg: dict = None) -> InlineKeyboardMarkup:
    """Build inline keyboard for DCA settings."""
    cfg = cfg or {}
    dca_enabled = cfg.get("dca_enabled", 0)
    status_emoji = "✅" if dca_enabled else "❌"
    
    buttons = [
        [InlineKeyboardButton(
            f"{status_emoji} " + t.get('dca_toggle', 'DCA Enabled'),
            callback_data="dca_toggle"
        )],
        [InlineKeyboardButton(t.get('dca_leg1', '📉 DCA Leg 1 %'), callback_data="dca_param:dca_pct_1")],
        [InlineKeyboardButton(t.get('dca_leg2', '📉 DCA Leg 2 %'), callback_data="dca_param:dca_pct_2")],
        [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="strat_set:back")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_hl_strategy_keyboard(strategy: str, t: dict, uid: int = None) -> InlineKeyboardMarkup:
    """Build inline keyboard for HyperLiquid strategy settings."""
    hl_settings = db.get_hl_strategy_settings(uid, strategy) if uid else {}
    
    hl_enabled = hl_settings.get("hl_enabled", False)
    status_emoji = "✅" if hl_enabled else "❌"
    
    hl_percent = hl_settings.get("hl_percent")
    hl_sl = hl_settings.get("hl_sl_percent")
    hl_tp = hl_settings.get("hl_tp_percent")
    hl_lev = hl_settings.get("hl_leverage")
    
    percent_label = f"{hl_percent}%" if hl_percent else t.get('global_default', 'Global')
    sl_label = f"{hl_sl}%" if hl_sl else t.get('global_default', 'Global')
    tp_label = f"{hl_tp}%" if hl_tp else t.get('global_default', 'Global')
    lev_label = f"{hl_lev}x" if hl_lev else t.get('global_default', 'Global')
    
    display_name = STRATEGY_NAMES_MAP.get(strategy, strategy.upper())
    
    buttons = [
        [InlineKeyboardButton(
            f"{status_emoji} " + t.get('hl_trading_enabled', 'HyperLiquid Trading'),
            callback_data=f"hl_strat:toggle:{strategy}"
        )],
        [InlineKeyboardButton(
            t.get('param_percent', '📊 Entry %') + f": {percent_label}",
            callback_data=f"hl_strat:param:{strategy}:hl_percent"
        )],
        [InlineKeyboardButton(
            t.get('param_sl', '🔻 Stop-Loss %') + f": {sl_label}",
            callback_data=f"hl_strat:param:{strategy}:hl_sl_percent"
        )],
        [InlineKeyboardButton(
            t.get('param_tp', '🔺 Take-Profit %') + f": {tp_label}",
            callback_data=f"hl_strat:param:{strategy}:hl_tp_percent"
        )],
        [InlineKeyboardButton(
            t.get('param_leverage', '⚡ Leverage') + f": {lev_label}",
            callback_data=f"hl_strat:param:{strategy}:hl_leverage"
        )],
        [InlineKeyboardButton(
            t.get('hl_reset_settings', '🔄 Reset to Bybit Settings'),
            callback_data=f"hl_strat:reset:{strategy}"
        )],
        [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data=f"strat_set:{strategy}")],
    ]
    return InlineKeyboardMarkup(buttons)


@require_access
@with_texts
@log_calls
async def cmd_strategy_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show strategy settings menu."""
    uid = update.effective_user.id
    cfg = get_user_config(uid)
    active_exchange = db.get_exchange_type(uid) or "bybit"
    global_use_atr = bool(cfg.get("use_atr", 1))
    
    # Build status message
    lines = [ctx.t.get('strategy_settings_header', '⚙️ *Strategy Settings*')]
    lines.append("")
    
    for strat_key, strat_name in STRATEGY_NAMES_MAP.items():
        strat_settings = db.get_strategy_settings(uid, strat_key)
        status_parts = _build_strategy_status_parts(strat_key, strat_settings, active_exchange, global_use_atr)
        if status_parts:
            lines.append(f"*{strat_name}*: {', '.join(status_parts)}")
        else:
            lines.append(f"*{strat_name}*: {ctx.t.get('using_global', 'Using global settings')}")
    
    lines.append("")
    dca_status = '✅' if cfg.get('dca_enabled', 0) else '❌'
    lines.append(f"*DCA*: {dca_status} Leg1={cfg.get('dca_pct_1', 10.0)}%, Leg2={cfg.get('dca_pct_2', 25.0)}%")
    
    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=get_strategy_settings_keyboard(ctx.t, cfg, uid=uid)
    )


async def _show_global_settings_menu(query, uid: int, t: dict):
    """Helper to display Global Trading Settings menu."""
    cfg = get_user_config(uid)
    sl_val = cfg.get('sl_percent', cfg.get('sl_pct', 3))
    tp_val = cfg.get('tp_percent', cfg.get('tp_pct', 6))
    
    # ATR mode (trailing vs fixed)
    use_atr = cfg.get('use_atr', 1)
    atr_status = "✅" if use_atr else "❌"
    atr_label = "ATR Trailing" if use_atr else "Fixed SL/TP"
    
    # ATR parameters (global defaults)
    atr_trigger = cfg.get('atr_trigger_pct', ATR_TRIGGER_PCT)
    atr_step = cfg.get('atr_step_pct', 0.5)  # Default 0.5%
    atr_period = cfg.get('atr_period', 14)   # Default 14 candles
    atr_mult = cfg.get('atr_multiplier', 1.5)  # Default 1.5x ATR
    
    # Limit ladder info
    ladder_enabled = cfg.get('limit_ladder_enabled', 0)
    ladder_count = cfg.get('limit_ladder_count', 3)
    ladder_status = "✅" if ladder_enabled else "❌"
    
    # Order type (market/limit)
    order_type = cfg.get('global_order_type', 'market')
    order_emoji = "⚡" if order_type == "market" else "🎯"
    order_label = "Market" if order_type == "market" else "Limit"
    
    # Trading mode (demo/real/both)
    trading_mode = get_trading_mode(uid) or "demo"
    mode_emoji = {"demo": "🧪", "real": "💰", "both": "🔄"}.get(trading_mode, "🧪")
    mode_label = {"demo": "Demo", "real": "Real", "both": "Both"}.get(trading_mode, "Demo")
    
    lines = [t.get('global_settings_header', '🌐 *Global Trading Settings*')]
    lines.append("")
    lines.append(f"📊 Entry %: *{cfg.get('percent', 1)}%*")
    lines.append(f"🛑 SL %: *{sl_val}%*")
    lines.append(f"🎯 TP %: *{tp_val}%*")
    lines.append(f"🎚 Leverage: *{cfg.get('leverage', 10)}x*")
    lines.append(f"📉 Stop Mode: *{atr_label}* {atr_status}")
    lines.append(f"{order_emoji} Order type: *{order_label}*")
    lines.append(f"{mode_emoji} Account: *{mode_label}*")
    lines.append("")
    # ATR Settings section
    if use_atr:
        lines.append(f"📈 *ATR Settings:*")
        lines.append(f"  🎯 Trigger: *{atr_trigger}%* (activate trailing)")
        lines.append(f"  📏 Step: *{atr_step}%* (SL move step)")
        lines.append(f"  🕐 Period: *{atr_period}* candles")
        lines.append(f"  ✖️ Multiplier: *{atr_mult}x* ATR")
        lines.append("")
    lines.append(f"📈 {t.get('limit_ladder', 'Limit Ladder')}: {ladder_status} (*{ladder_count}* orders)")
    lines.append("")
    lines.append(t.get('global_settings_info', 'These settings are used as defaults when strategy-specific settings are not configured.'))
    
    buttons = [
        [InlineKeyboardButton(t.get('param_percent', '📊 Entry %'), callback_data="global_param:percent")],
        [InlineKeyboardButton(t.get('param_sl', '🛑 Stop-Loss %'), callback_data="global_param:sl_percent")],
        [InlineKeyboardButton(t.get('param_tp', '🎯 Take-Profit %'), callback_data="global_param:tp_percent")],
        [InlineKeyboardButton(t.get('param_leverage', '🎚 Leverage'), callback_data="global_param:leverage")],
        [InlineKeyboardButton(f"{atr_status} 📉 {atr_label}", callback_data="global_param:use_atr")],
        [InlineKeyboardButton(f"{order_emoji} Order: {order_label}", callback_data="global_param:order_type")],
        [InlineKeyboardButton(f"{mode_emoji} Account: {mode_label}", callback_data="global_param:trading_mode")],
        [InlineKeyboardButton("⚙️ ATR Settings", callback_data="global_atr:settings")],
        [InlineKeyboardButton(f"{ladder_status} {t.get('limit_ladder', '📈 Limit Ladder')}", callback_data="global_ladder:toggle")],
        [InlineKeyboardButton(t.get('limit_ladder_settings', '⚙️ Ladder Settings'), callback_data="global_ladder:settings")],
        [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="strat_set:back")],
    ]
    
    try:
        await query.message.edit_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        logger.error(f"Error editing global settings message: {e}")
        await query.message.edit_text(
            "\n".join(lines),
            reply_markup=InlineKeyboardMarkup(buttons)
        )


async def _show_global_atr_settings_menu(query, uid: int, t: dict):
    """Helper to display Global ATR Settings menu."""
    cfg = get_user_config(uid)
    
    atr_trigger = cfg.get('atr_trigger_pct', ATR_TRIGGER_PCT)
    atr_step = cfg.get('atr_step_pct', 0.5)
    atr_period = cfg.get('atr_period', 14)
    atr_mult = cfg.get('atr_multiplier', 1.5)
    use_atr = cfg.get('use_atr', 1)
    
    lines = [t.get('atr_settings_header', '📈 *Global ATR Settings*')]
    lines.append("")
    lines.append(f"📊 ATR Mode: {'✅ Enabled' if use_atr else '❌ Disabled'}")
    lines.append("")
    lines.append(t.get('atr_settings_desc', '_ATR (Average True Range) is used for dynamic trailing stop-loss._'))
    lines.append("")
    lines.append(f"🎯 *Trigger %*: {atr_trigger}%")
    lines.append(t.get('atr_trigger_desc', '   _Profit % to activate trailing_'))
    lines.append("")
    lines.append(f"📏 *Step %*: {atr_step}%")
    lines.append(t.get('atr_step_desc', '   _Min % move to update SL_'))
    lines.append("")
    lines.append(f"🕐 *Period*: {atr_period} candles")
    lines.append(t.get('atr_period_desc', '   _Candles for ATR calculation_'))
    lines.append("")
    lines.append(f"✖️ *Multiplier*: {atr_mult}x ATR")
    lines.append(t.get('atr_mult_desc', '   _Distance from price for SL_'))
    
    buttons = [
        [InlineKeyboardButton(f"🎯 Trigger: {atr_trigger}%", callback_data="global_atr:trigger")],
        [InlineKeyboardButton(f"📏 Step: {atr_step}%", callback_data="global_atr:step")],
        [InlineKeyboardButton(f"🕐 Period: {atr_period}", callback_data="global_atr:period")],
        [InlineKeyboardButton(f"✖️ Multiplier: {atr_mult}x", callback_data="global_atr:mult")],
        [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="strat_set:global")],
    ]
    
    try:
        await query.message.edit_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        logger.error(f"Error editing ATR settings message: {e}")
        await query.message.edit_text(
            "\n".join(lines),
            reply_markup=InlineKeyboardMarkup(buttons)
        )


async def _show_ladder_settings_menu(query, uid: int, t: dict):
    """Helper to display Ladder Settings menu."""
    cfg = get_user_config(uid)
    ladder_count = cfg.get('limit_ladder_count', 3)
    ladder_settings = cfg.get('limit_ladder_settings', [])
    
    # Default settings if empty
    if not ladder_settings:
        ladder_settings = [
            {"pct_from_entry": 1.0, "pct_of_deposit": 5.0},
            {"pct_from_entry": 2.0, "pct_of_deposit": 7.0},
            {"pct_from_entry": 3.0, "pct_of_deposit": 10.0},
        ]
    
    lines = [t.get('limit_ladder_header', '📈 *Limit Ladder Settings*')]
    lines.append("")
    lines.append(f"📊 {t.get('ladder_count', 'Number of orders')}: *{ladder_count}*")
    lines.append("")
    for i, leg in enumerate(ladder_settings[:ladder_count], 1):
        pct_entry = leg.get('pct_from_entry', 1.0)
        pct_deposit = leg.get('pct_of_deposit', 5.0)
        lines.append(f"📉 *Order {i}*: -{pct_entry}% @ {pct_deposit}% deposit")
    lines.append("")
    lines.append(t.get('ladder_info', 'Limit orders placed below entry price for DCA entries.'))
    
    buttons = [
        [InlineKeyboardButton(f"📊 {t.get('ladder_count', 'Count')}: {ladder_count}", callback_data="global_ladder:count")],
    ]
    for i in range(min(ladder_count, 5)):
        leg = ladder_settings[i] if i < len(ladder_settings) else {"pct_from_entry": 1.0, "pct_of_deposit": 5.0}
        pct_entry = leg.get('pct_from_entry', 1.0)
        pct_deposit = leg.get('pct_of_deposit', 5.0)
        buttons.append([
            InlineKeyboardButton(f"📉 #{i+1}: -{pct_entry}%", callback_data=f"global_ladder:pct_entry:{i}"),
            InlineKeyboardButton(f"💰 #{i+1}: {pct_deposit}%", callback_data=f"global_ladder:pct_deposit:{i}"),
        ])
    buttons.append([InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="strat_set:global")])
    
    try:
        await query.message.edit_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        logger.error(f"Error editing ladder settings message: {e}")
        await query.message.edit_text(
            "\n".join(lines),
            reply_markup=InlineKeyboardMarkup(buttons)
        )


@log_calls
async def callback_strategy_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle strategy settings inline button callbacks."""
    query = update.callback_query
    # Note: Don't call query.answer() here - each handler will answer with appropriate message
    
    uid = query.from_user.id
    data = query.data
    cfg = get_user_config(uid)
    lang = cfg.get("lang", DEFAULT_LANG)
    t = LANGS.get(lang, LANGS[DEFAULT_LANG])
    
    if data == "strat_set:close":
        await query.answer()
        await query.message.delete()
        return
    
    if data == "strat_set:back":
        # Rebuild main strategy menu
        active_exchange = db.get_exchange_type(uid) or "bybit"
        global_use_atr = bool(cfg.get("use_atr", 1))
        lines = [t.get('strategy_settings_header', '⚙️ *Strategy Settings*')]
        lines.append("")
        
        for strat_key, strat_name in STRATEGY_NAMES_MAP.items():
            strat_settings = db.get_strategy_settings(uid, strat_key)
            status_parts = _build_strategy_status_parts(strat_key, strat_settings, active_exchange, global_use_atr)
            if status_parts:
                lines.append(f"*{strat_name}*: {', '.join(status_parts)}")
            else:
                lines.append(f"*{strat_name}*: {t.get('using_global', 'Using global settings')}")
        
        lines.append("")
        dca_status = '✅' if cfg.get('dca_enabled', 0) else '❌'
        lines.append(f"*DCA*: {dca_status} Leg1={cfg.get('dca_pct_1', 10.0)}%, Leg2={cfg.get('dca_pct_2', 25.0)}%")
        
        await query.message.edit_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=get_strategy_settings_keyboard(t, cfg, uid=uid)
        )
        await query.answer()
        return
    
    if data == "strat_set:global":
        # Show global trading settings using helper
        return await _show_global_settings_menu(query, uid, t)
    
    # Global ATR mode toggle (ATR Trailing vs Fixed SL/TP)
    if data == "global_param:use_atr":
        current = cfg.get('use_atr', 1)
        new_val = 0 if current else 1
        set_user_field(uid, 'use_atr', new_val)
        status = "✅ ATR Trailing enabled" if new_val else "❌ Fixed SL/TP mode"
        await query.answer(status)
        # Return directly to global settings with updated value
        return await _show_global_settings_menu(query, uid, t)
    
    # Global order type toggle
    if data == "global_param:order_type":
        current = cfg.get('global_order_type', 'market')
        new_type = "limit" if current == "market" else "market"
        set_user_field(uid, 'global_order_type', new_type)
        emoji = "🎯" if new_type == "limit" else "⚡"
        # Return directly to global settings with updated value
        return await _show_global_settings_menu(query, uid, t)
    
    # Global trading mode toggle (demo -> real -> both -> demo)
    if data == "global_param:trading_mode":
        current = get_trading_mode(uid) or "demo"
        # Cycle: demo -> real -> both -> demo
        modes = ["demo", "real", "both"]
        next_idx = (modes.index(current) + 1) % 3 if current in modes else 0
        new_mode = modes[next_idx]
        set_trading_mode(uid, new_mode)
        # Return directly to global settings with updated value
        return await _show_global_settings_menu(query, uid, t)
    
    # ═══════════════════════════════════════════════════════════════════════
    # ██  GLOBAL ATR SETTINGS HANDLERS  ██
    # ═══════════════════════════════════════════════════════════════════════
    
    # Show ATR settings menu
    if data == "global_atr:settings":
        return await _show_global_atr_settings_menu(query, uid, t)
    
    # ATR Trigger %
    if data == "global_atr:trigger":
        ctx.user_data["global_setting_mode"] = "atr_trigger_pct"
        await query.message.edit_text(
            t.get('atr_trigger_prompt', '🎯 *ATR Trigger %*\n\nEnter the profit % at which ATR trailing stop activates.\n\nCurrent: {current}%\n\nExample: 1 = activate when +1% profit').format(
                current=cfg.get('atr_trigger_pct', ATR_TRIGGER_PCT)
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get('btn_cancel', '❌ Cancel'), callback_data="global_atr:settings")]
            ])
        )
        return
    
    # ATR Step %
    if data == "global_atr:step":
        ctx.user_data["global_setting_mode"] = "atr_step_pct"
        await query.message.edit_text(
            t.get('atr_step_prompt', '📏 *ATR Step %*\n\nEnter the minimum % move to trail SL.\n\nCurrent: {current}%\n\nExample: 0.5 = move SL when price moves +0.5%').format(
                current=cfg.get('atr_step_pct', 0.5)
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get('btn_cancel', '❌ Cancel'), callback_data="global_atr:settings")]
            ])
        )
        return
    
    # ATR Period
    if data == "global_atr:period":
        ctx.user_data["global_setting_mode"] = "atr_period"
        await query.message.edit_text(
            t.get('atr_period_prompt', '🕐 *ATR Period*\n\nEnter the number of candles for ATR calculation.\n\nCurrent: {current}\n\nExample: 14 = use 14 candles').format(
                current=cfg.get('atr_period', 14)
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get('btn_cancel', '❌ Cancel'), callback_data="global_atr:settings")]
            ])
        )
        return
    
    # ATR Multiplier
    if data == "global_atr:mult":
        ctx.user_data["global_setting_mode"] = "atr_multiplier"
        await query.message.edit_text(
            t.get('atr_mult_prompt', '✖️ *ATR Multiplier*\n\nEnter the ATR multiplier for SL distance.\n\nCurrent: {current}x\n\nExample: 1.5 = SL at 1.5 × ATR from price').format(
                current=cfg.get('atr_multiplier', 1.5)
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get('btn_cancel', '❌ Cancel'), callback_data="global_atr:settings")]
            ])
        )
        return
    
    # Limit ladder toggle
    if data == "global_ladder:toggle":
        current = cfg.get('limit_ladder_enabled', 0)
        new_val = 0 if current else 1
        set_user_field(uid, 'limit_ladder_enabled', new_val)
        # Refresh global settings directly
        return await _show_global_settings_menu(query, uid, t)
    
    # Limit ladder settings
    if data == "global_ladder:settings":
        # Show ladder settings using helper
        return await _show_ladder_settings_menu(query, uid, t)
    
    # Ladder count adjustment
    if data == "global_ladder:count":
        current = cfg.get('limit_ladder_count', 3)
        new_count = (current % 5) + 1  # Cycle 1-5
        set_user_field(uid, 'limit_ladder_count', new_count)
        # Refresh ladder settings directly
        return await _show_ladder_settings_menu(query, uid, t)
    
    # Ladder leg parameter input
    if data.startswith("global_ladder:pct_entry:") or data.startswith("global_ladder:pct_deposit:"):
        parts = data.split(":")
        param_type = parts[1]  # "pct_entry" or "pct_deposit"
        leg_idx = int(parts[2])
        
        ctx.user_data["ladder_setting_mode"] = {"type": param_type, "leg": leg_idx}
        
        if param_type == "pct_entry":
            prompt = t.get('prompt_ladder_pct_entry', 'Enter % below entry price for order {idx}:').format(idx=leg_idx+1)
        else:
            prompt = t.get('prompt_ladder_pct_deposit', 'Enter % of deposit for order {idx}:').format(idx=leg_idx+1)
        
        await query.message.edit_text(
            prompt,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get('btn_cancel', '❌ Cancel'), callback_data="global_ladder:settings")]
            ])
        )
        return
    
    # ═══════════════════════════════════════════════════════════════════════
    # ██  HYPERLIQUID STRATEGY SETTINGS HANDLERS  ██
    # ═══════════════════════════════════════════════════════════════════════
    
    # Handle opening HL settings for a strategy
    if data.startswith("strat_hl:"):
        strategy = data.split(":")[1]
        if strategy not in STRATEGY_NAMES_MAP:
            await query.answer("❌ Invalid strategy")
            return
        
        hl_settings = db.get_hl_strategy_settings(uid, strategy)
        bybit_settings = db.get_effective_settings(uid, strategy)
        
        hl_enabled = hl_settings.get("hl_enabled", False)
        hl_percent = hl_settings.get("hl_percent")
        hl_sl = hl_settings.get("hl_sl_percent")
        hl_tp = hl_settings.get("hl_tp_percent")
        hl_lev = hl_settings.get("hl_leverage")
        
        strat_name = STRATEGY_NAMES_MAP.get(strategy, strategy.upper())
        
        text = f"🔷 <b>HyperLiquid Settings: {strat_name}</b>\n\n"
        text += f"<b>Status:</b> {'✅ Enabled' if hl_enabled else '❌ Disabled'}\n\n"
        
        text += "<b>Current Settings:</b>\n"
        text += f"📊 Entry %: {hl_percent if hl_percent else 'Use Bybit (' + str(bybit_settings.get('percent', 1.0)) + '%)'}\n"
        text += f"🔻 Stop-Loss %: {hl_sl if hl_sl else 'Use Bybit (' + str(bybit_settings.get('sl_percent', 2.0)) + '%)'}\n"
        text += f"🔺 Take-Profit %: {hl_tp if hl_tp else 'Use Bybit (' + str(bybit_settings.get('tp_percent', 3.0)) + '%)'}\n"
        text += f"⚡ Leverage: {str(hl_lev) + 'x' if hl_lev else 'Use Bybit (' + str(bybit_settings.get('leverage', 10)) + 'x)'}\n\n"
        
        text += "<i>When enabled, signals will also open trades on HyperLiquid if the coin is available there.</i>"
        
        await query.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_hl_strategy_keyboard(strategy, t, uid=uid)
        )
        return
    
    # Handle HL strategy toggle
    if data.startswith("hl_strat:toggle:"):
        strategy = data.split(":")[2]
        hl_settings = db.get_hl_strategy_settings(uid, strategy)
        current = hl_settings.get("hl_enabled", False)
        new_val = not current
        
        db.set_hl_strategy_setting(uid, strategy, "hl_enabled", new_val)
        
        status = "✅ Enabled" if new_val else "❌ Disabled"
        await query.answer(f"🔷 HyperLiquid {STRATEGY_NAMES_MAP.get(strategy, strategy)}: {status}")
        
        # Refresh the HL settings menu
        hl_settings = db.get_hl_strategy_settings(uid, strategy)
        bybit_settings = db.get_effective_settings(uid, strategy)
        
        strat_name = STRATEGY_NAMES_MAP.get(strategy, strategy.upper())
        
        text = f"🔷 <b>HyperLiquid Settings: {strat_name}</b>\n\n"
        text += f"<b>Status:</b> {'✅ Enabled' if new_val else '❌ Disabled'}\n\n"
        
        hl_percent = hl_settings.get("hl_percent")
        hl_sl = hl_settings.get("hl_sl_percent")
        hl_tp = hl_settings.get("hl_tp_percent")
        hl_lev = hl_settings.get("hl_leverage")
        
        text += "<b>Current Settings:</b>\n"
        text += f"📊 Entry %: {hl_percent if hl_percent else 'Use Bybit (' + str(bybit_settings.get('percent', 1.0)) + '%)'}\n"
        text += f"🔻 Stop-Loss %: {hl_sl if hl_sl else 'Use Bybit (' + str(bybit_settings.get('sl_percent', 2.0)) + '%)'}\n"
        text += f"🔺 Take-Profit %: {hl_tp if hl_tp else 'Use Bybit (' + str(bybit_settings.get('tp_percent', 3.0)) + '%)'}\n"
        text += f"⚡ Leverage: {str(hl_lev) + 'x' if hl_lev else 'Use Bybit (' + str(bybit_settings.get('leverage', 10)) + 'x)'}\n"
        
        await query.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_hl_strategy_keyboard(strategy, t, uid=uid)
        )
        return
    
    # Handle HL strategy parameter input
    if data.startswith("hl_strat:param:"):
        parts = data.split(":")
        strategy = parts[2]
        param = parts[3]
        
        _awaiting_hl_param[uid] = {"strategy": strategy, "param": param}
        
        param_labels = {
            "hl_percent": "Entry %",
            "hl_sl_percent": "Stop-Loss %",
            "hl_tp_percent": "Take-Profit %",
            "hl_leverage": "Leverage"
        }
        
        strat_name = STRATEGY_NAMES_MAP.get(strategy, strategy.upper())
        param_label = param_labels.get(param, param)
        
        await query.message.edit_text(
            f"🔷 <b>{strat_name} - {param_label}</b>\n\n"
            f"Enter new value for {param_label}:\n\n"
            f"Send a number or /cancel to abort.",
            parse_mode="HTML"
        )
        return
    
    # Handle HL strategy reset
    if data.startswith("hl_strat:reset:"):
        strategy = data.split(":")[2]
        
        # Clear all HL settings for this strategy
        for field in ["hl_enabled", "hl_percent", "hl_sl_percent", "hl_tp_percent", "hl_leverage"]:
            db.set_hl_strategy_setting(uid, strategy, field, None)
        
        await query.answer(f"🔄 HyperLiquid settings reset for {STRATEGY_NAMES_MAP.get(strategy, strategy)}")
        
        # Refresh the strategy menu
        strat_settings = db.get_strategy_settings(uid, strategy)
        display_name = STRATEGY_NAMES_MAP.get(strategy, strategy.upper())
        
        await query.message.edit_text(
            f"⚙️ <b>{display_name} Strategy Settings</b>\n\n"
            f"Configure {display_name} signal parameters.\n"
            f"Use buttons below to adjust settings.",
            parse_mode="HTML",
            reply_markup=get_strategy_param_keyboard(strategy, t, strat_settings)
        )
        return
    
    if data == "strat_set:dca":
        # Show DCA settings
        dca_enabled = cfg.get('dca_enabled', 0)
        status = t.get('status_enabled', 'Enabled') if dca_enabled else t.get('status_disabled', 'Disabled')
        text = t.get('dca_settings_header', '⚙️ *DCA Settings (Futures)*\n\n')
        text += f"*{t.get('dca_status', 'Status')}*: {'✅' if dca_enabled else '❌'} {status}\n\n"
        text += f"📉 *Leg 1*: -{cfg.get('dca_pct_1', 10.0)}%\n"
        text += f"📉 *Leg 2*: -{cfg.get('dca_pct_2', 25.0)}%\n\n"
        text += t.get('dca_description', '_DCA will add to position when price moves against you._')
        
        await query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_dca_settings_keyboard(t, cfg)
        )
        return
    
    # Handle strategy enable/disable toggle
    if data.startswith("strat_toggle:"):
        strategy = data.split(":")[1]
        
        # Handle Spot toggle separately
        if strategy == "spot":
            current = cfg.get("spot_enabled", 0)
            new_val = 0 if current else 1
            set_user_field(uid, "spot_enabled", new_val)
            cfg = get_user_config(uid)
            
            status = "✅ ON" if new_val else "❌ OFF"
            await query.answer(f"💹 Spot: {status}")
            
            # Refresh the strategies menu
            active_exchange = db.get_exchange_type(uid) or "bybit"
            global_use_atr = bool(cfg.get("use_atr", 1))
            lines = [t.get('strategy_settings_header', '⚙️ *Strategy Settings*')]
            lines.append("")
            for strat_key, strat_nm in STRATEGY_NAMES_MAP.items():
                strat_settings = db.get_strategy_settings(uid, strat_key)
                status_parts = _build_strategy_status_parts(strat_key, strat_settings, active_exchange, global_use_atr)
                if status_parts:
                    lines.append(f"*{strat_nm}*: {', '.join(status_parts)}")
                else:
                    lines.append(f"*{strat_nm}*: {t.get('using_global', 'Using global settings')}")
            lines.append("")
            dca_status = '✅' if cfg.get('dca_enabled', 0) else '❌'
            lines.append(f"*DCA*: {dca_status} Leg1={cfg.get('dca_pct_1', 10.0)}%, Leg2={cfg.get('dca_pct_2', 25.0)}%")
            
            await query.message.edit_text(
                "\n".join(lines),
                parse_mode="Markdown",
                reply_markup=get_strategy_settings_keyboard(t, cfg, uid=uid)
            )
            return
        
        field_map = {
            "oi": "trade_oi",
            "rsi_bb": "trade_rsi_bb",
            "scryptomera": "trade_scryptomera",
            "scalper": "trade_scalper",
            "elcaro": "trade_elcaro",
            "fibonacci": "trade_fibonacci",
        }
        field = field_map.get(strategy)
        if field:
            current = cfg.get(field, 0)
            new_val = 0 if current else 1
            set_user_field(uid, field, new_val)
            cfg = get_user_config(uid)
            
            strat_name = STRATEGY_NAMES_MAP.get(strategy, strategy.upper())
            status = "✅ ON" if new_val else "❌ OFF"
            await query.answer(f"{strat_name}: {status}")
            
            # Refresh the strategies menu
            active_exchange = db.get_exchange_type(uid) or "bybit"
            global_use_atr = bool(cfg.get("use_atr", 1))
            lines = [t.get('strategy_settings_header', '⚙️ *Strategy Settings*')]
            lines.append("")
            for strat_key, strat_nm in STRATEGY_NAMES_MAP.items():
                strat_settings = db.get_strategy_settings(uid, strat_key)
                status_parts = _build_strategy_status_parts(strat_key, strat_settings, active_exchange, global_use_atr)
                if status_parts:
                    lines.append(f"*{strat_nm}*: {', '.join(status_parts)}")
                else:
                    lines.append(f"*{strat_nm}*: {t.get('using_global', 'Using global settings')}")
            lines.append("")
            dca_status = '✅' if cfg.get('dca_enabled', 0) else '❌'
            lines.append(f"*DCA*: {dca_status} Leg1={cfg.get('dca_pct_1', 10.0)}%, Leg2={cfg.get('dca_pct_2', 25.0)}%")
            
            await query.message.edit_text(
                "\n".join(lines),
                parse_mode="Markdown",
                reply_markup=get_strategy_settings_keyboard(t, cfg, uid=uid)
            )
        return
    
    # Handle strategy trading mode toggle - EXCHANGE AWARE
    # Bybit: global -> demo -> real -> both -> global
    # HyperLiquid: global -> testnet -> mainnet -> both -> global
    if data.startswith("strat_mode:"):
        strategy = data.split(":")[1]
        logger.info(f"[STRAT_MODE] User {uid} clicked mode button for strategy: {strategy}")
        
        # Get user's active exchange
        active_exchange = db.get_exchange_type(uid) or "bybit"
        
        # Handle Spot mode separately (only demo/real for Bybit, testnet/mainnet for HL)
        if strategy == "spot":
            spot_settings = cfg.get("spot_settings", {}) or {}
            current_mode = spot_settings.get("trading_mode", "demo")
            
            if active_exchange == "hyperliquid":
                # HL: testnet -> mainnet -> testnet
                if current_mode in ("demo", "testnet"):
                    new_mode = "mainnet"
                else:
                    new_mode = "testnet"
                mode_labels = {"testnet": "Testnet", "mainnet": "Mainnet"}
            else:
                # Bybit: demo -> real -> demo
                if current_mode in ("testnet", "demo"):
                    new_mode = "real"
                else:
                    new_mode = "demo"
                mode_labels = {"demo": "Demo", "real": "Real"}
            
            spot_settings["trading_mode"] = new_mode
            db.set_user_field(uid, "spot_settings", json.dumps(spot_settings))
            
            # Check credentials
            warning = ""
            if active_exchange == "hyperliquid":
                hl_creds = db.get_hl_credentials(uid)
                has_key = bool(hl_creds.get("hl_private_key"))
                if not has_key:
                    warning = " ⚠️ No HL private key!"
            else:
                creds = db.get_all_user_credentials(uid)
                has_demo = bool(creds.get("demo_api_key") and creds.get("demo_api_secret"))
                has_real = bool(creds.get("real_api_key") and creds.get("real_api_secret"))
                if new_mode == "real" and not has_real:
                    warning = " ⚠️ No Real API keys!"
                elif new_mode == "demo" and not has_demo:
                    warning = " ⚠️ No Demo API keys!"
            
            await query.answer(f"Spot: {mode_labels.get(new_mode, new_mode)}{warning}", show_alert=bool(warning))
            
            # Refresh the strategies menu
            cfg = get_user_config(uid)
            global_use_atr = bool(cfg.get("use_atr", 1))
            lines = [t.get('strategy_settings_header', '⚙️ *Strategy Settings*')]
            lines.append("")
            for strat_key, strat_nm in STRATEGY_NAMES_MAP.items():
                strat_set = db.get_strategy_settings(uid, strat_key)
                status_parts = _build_strategy_status_parts(strat_key, strat_set, active_exchange, global_use_atr)
                if status_parts:
                    lines.append(f"*{strat_nm}*: {', '.join(status_parts)}")
                else:
                    lines.append(f"*{strat_nm}*: {t.get('using_global', 'Using global settings')}")
            lines.append("")
            dca_status = '✅' if cfg.get('dca_enabled', 0) else '❌'
            lines.append(f"*DCA*: {dca_status} Leg1={cfg.get('dca_pct_1', 10.0)}%, Leg2={cfg.get('dca_pct_2', 25.0)}%")
            
            await query.message.edit_text(
                "\n".join(lines),
                parse_mode="Markdown",
                reply_markup=get_strategy_settings_keyboard(t, cfg, uid=uid)
            )
            return
        
        if strategy in STRATEGY_NAMES_MAP:
            strat_settings = db.get_strategy_settings(uid, strategy)
            current_mode = strat_settings.get("trading_mode", "global")
            # Normalize legacy "all" value to "global"
            if current_mode == "all":
                current_mode = "global"
            
            # Exchange-aware mode cycling
            if active_exchange == "hyperliquid":
                # HyperLiquid: global -> testnet -> mainnet -> both -> global
                mode_cycle = ["global", "testnet", "mainnet", "both"]
                # Normalize bybit modes to HL modes
                if current_mode == "demo":
                    current_mode = "testnet"
                elif current_mode == "real":
                    current_mode = "mainnet"
                mode_labels = {
                    "global": "Global",
                    "testnet": "Testnet",
                    "mainnet": "Mainnet",
                    "both": "Both"
                }
            else:
                # Bybit: global -> demo -> real -> both -> global
                mode_cycle = ["global", "demo", "real", "both"]
                # Normalize HL modes to Bybit modes
                if current_mode == "testnet":
                    current_mode = "demo"
                elif current_mode == "mainnet":
                    current_mode = "real"
                mode_labels = {
                    "global": "Global",
                    "demo": "Demo",
                    "real": "Real",
                    "both": "Both"
                }
            
            current_idx = mode_cycle.index(current_mode) if current_mode in mode_cycle else 0
            new_mode = mode_cycle[(current_idx + 1) % len(mode_cycle)]
            
            # Get current context for saving
            context = get_user_trading_context(uid)
            
            # Save new mode to current exchange/account context
            save_result = db.set_strategy_setting(uid, strategy, "trading_mode", new_mode,
                                   context["exchange"], context["account_type"])
            logger.info(f"[STRAT_MODE] {strategy}: {current_mode} -> {new_mode}, saved: {save_result}")
            
            # Check credentials
            warning = ""
            if active_exchange == "hyperliquid":
                hl_creds = db.get_hl_credentials(uid)
                has_key = bool(hl_creds.get("hl_private_key"))
                if not has_key and new_mode != "global":
                    warning = " ⚠️ No HL private key!"
            else:
                creds = db.get_all_user_credentials(uid)
                has_demo = bool(creds.get("demo_api_key") and creds.get("demo_api_secret"))
                has_real = bool(creds.get("real_api_key") and creds.get("real_api_secret"))
                
                if new_mode == "real" and not has_real:
                    warning = " ⚠️ No Real API keys!"
                elif new_mode == "demo" and not has_demo:
                    warning = " ⚠️ No Demo API keys!"
                elif new_mode == "both":
                    if not has_real and not has_demo:
                        warning = " ⚠️ No API keys!"
                    elif not has_real:
                        warning = " ⚠️ No Real API keys!"
                    elif not has_demo:
                        warning = " ⚠️ No Demo API keys!"
            
            await query.answer(f"{STRATEGY_NAMES_MAP[strategy]}: {mode_labels.get(new_mode, new_mode)}{warning}", show_alert=bool(warning))
            
            # Refresh the strategies menu
            cfg = get_user_config(uid)
            global_use_atr = bool(cfg.get("use_atr", 1))
            lines = [t.get('strategy_settings_header', '⚙️ *Strategy Settings*')]
            lines.append("")
            for strat_key, strat_nm in STRATEGY_NAMES_MAP.items():
                strat_set = db.get_strategy_settings(uid, strat_key)
                status_parts = _build_strategy_status_parts(strat_key, strat_set, active_exchange, global_use_atr)
                if status_parts:
                    lines.append(f"*{strat_nm}*: {', '.join(status_parts)}")
                else:
                    lines.append(f"*{strat_nm}*: {t.get('using_global', 'Using global settings')}")
            lines.append("")
            dca_status = '✅' if cfg.get('dca_enabled', 0) else '❌'
            lines.append(f"*DCA*: {dca_status} Leg1={cfg.get('dca_pct_1', 10.0)}%, Leg2={cfg.get('dca_pct_2', 25.0)}%")
            
            await query.message.edit_text(
                "\n".join(lines),
                parse_mode="Markdown",
                reply_markup=get_strategy_settings_keyboard(t, cfg, uid=uid)
            )
        return
    
    if data.startswith("strat_set:"):
        strategy = data.split(":")[1]
        
        # Handle Spot settings - open spot settings menu
        if strategy == "spot":
            spot_settings = cfg.get("spot_settings", {}) or {}
            if not spot_settings:
                spot_settings = {
                    "coins": SPOT_DCA_COINS.copy() if isinstance(SPOT_DCA_COINS, list) else SPOT_DCA_COINS.split(","),
                    "dca_amount": SPOT_DCA_DEFAULT_AMOUNT,
                    "frequency": "manual",
                    "auto_dca": False,
                    "total_invested": 0.0,
                    "trading_mode": "demo",
                }
            msg = format_spot_settings_message(t, cfg, spot_settings)
            keyboard = get_spot_settings_keyboard(t, cfg, spot_settings)
            await query.message.edit_text(msg, reply_markup=keyboard, parse_mode="HTML")
            return
        
        if strategy in STRATEGY_NAMES_MAP:
            # Get settings for current exchange/account_type context
            context = get_user_trading_context(uid)
            strat_settings = db.get_strategy_settings(uid, strategy, context["exchange"], context["account_type"])
            display_name = STRATEGY_NAMES_MAP[strategy]
            
            # Show which context we're viewing
            if context["exchange"] == "hyperliquid":
                ctx_label = "Testnet" if context["account_type"] == "testnet" else "Mainnet"
            else:
                ctx_label = "Demo" if context["account_type"] == "demo" else "Real"
            
            # Use unified build function for settings display
            lines = [t.get('strategy_param_header', '⚙️ *{name} Settings*').format(name=display_name)]
            lines.append(f"_{context['exchange'].title()} / {ctx_label}_")
            lines.append("")
            
            # Build settings text based on strategy features
            settings_text = build_strategy_settings_text(strategy, strat_settings, t)
            # Skip header from build function since we already have it
            settings_lines = settings_text.split("\n")
            if len(settings_lines) > 1:
                lines.extend(settings_lines[2:])  # Skip header and empty line
            
            # Special info for Elcaro/Fibonacci - AI signals
            if strategy in ("elcaro", "fibonacci"):
                lines.append("")
                lines.append("━━━━━━━━━━━━━━━━━━")
                if strategy == "elcaro":
                    lines.append(t.get('elcaro_ai_info', '🤖 *AI-Powered Trading*'))
                    lines.append("")
                    lines.append(t.get('elcaro_ai_desc', '_Entry, SL, TP, ATR, Leverage - all parsed from AI signals automatically._'))
                else:
                    lines.append(t.get('fibonacci_info', '📐 *Fibonacci Extension*'))
                    lines.append("")
                    lines.append(t.get('fibonacci_desc', '_Entry, SL, TP - from Fibonacci levels in signal._'))
            
            await query.message.edit_text(
                "\n".join(lines),
                parse_mode="Markdown",
                reply_markup=get_strategy_param_keyboard(strategy, t, strat_settings)
            )
        return
    
    # Global parameter setting
    if data.startswith("global_param:"):
        param = data.split(":")[1]
        ctx.user_data["global_setting_mode"] = param
        
        param_names = {
            "percent": t.get('prompt_entry_pct', 'Enter Entry % (risk per trade):'),
            "sl_percent": t.get('prompt_sl_pct', 'Enter Stop-Loss %:'),
            "tp_percent": t.get('prompt_tp_pct', 'Enter Take-Profit %:'),
            "leverage": t.get('prompt_leverage', 'Enter Leverage (1-100):'),
        }
        
        await query.message.edit_text(
            param_names.get(param, f"Enter value for {param}:"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get('btn_cancel', '❌ Cancel'), callback_data="strat_set:global")]
            ])
        )
        return
    
    if data.startswith("strat_param:"):
        parts = data.split(":")
        strategy = parts[1]
        param = parts[2]
        
        ctx.user_data["strat_setting_mode"] = {"strategy": strategy, "param": param}
        
        param_names = {
            "percent": t.get('prompt_entry_pct', 'Enter Entry % (risk per trade):'),
            "sl_percent": t.get('prompt_sl_pct', 'Enter Stop-Loss %:'),
            "tp_percent": t.get('prompt_tp_pct', 'Enter Take-Profit %:'),
            "atr_periods": t.get('prompt_atr_periods', 'Enter ATR Periods (e.g., 7):'),
            "atr_multiplier_sl": t.get('prompt_atr_mult', 'Enter ATR Multiplier for SL step (e.g., 1.0):'),
            "atr_trigger_pct": t.get('prompt_atr_trigger', 'Enter ATR Trigger % (e.g., 2.0):'),
            "leverage": t.get('prompt_leverage', 'Enter Leverage (1-100):'),
            "min_quality": t.get('prompt_min_quality', 'Enter Min Quality % (0-100):'),
            # LONG settings
            "long_percent": t.get('prompt_long_entry_pct', '📈 LONG Entry % (risk per trade):'),
            "long_sl_percent": t.get('prompt_long_sl_pct', '📈 LONG Stop-Loss %:'),
            "long_tp_percent": t.get('prompt_long_tp_pct', '📈 LONG Take-Profit %:'),
            "long_atr_periods": t.get('prompt_long_atr_periods', '📈 LONG ATR Periods (e.g., 7):'),
            "long_atr_multiplier_sl": t.get('prompt_long_atr_mult', '📈 LONG ATR Multiplier (e.g., 1.0):'),
            "long_atr_trigger_pct": t.get('prompt_long_atr_trigger', '📈 LONG ATR Trigger % (e.g., 2.0):'),
            # SHORT settings
            "short_percent": t.get('prompt_short_entry_pct', '📉 SHORT Entry % (risk per trade):'),
            "short_sl_percent": t.get('prompt_short_sl_pct', '📉 SHORT Stop-Loss %:'),
            "short_tp_percent": t.get('prompt_short_tp_pct', '📉 SHORT Take-Profit %:'),
            "short_atr_periods": t.get('prompt_short_atr_periods', '📉 SHORT ATR Periods (e.g., 7):'),
            "short_atr_multiplier_sl": t.get('prompt_short_atr_mult', '📉 SHORT ATR Multiplier (e.g., 1.0):'),
            "short_atr_trigger_pct": t.get('prompt_short_atr_trigger', '📉 SHORT ATR Trigger % (e.g., 2.0):'),
        }
        
        await query.message.edit_text(
            param_names.get(param, f"Enter value for {param}:"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get('btn_cancel', '❌ Cancel'), callback_data="strat_set:back")]
            ])
        )
        return
    
    if data.startswith("strat_reset:"):
        strategy = data.split(":")[1]
        # Reset all settings for this strategy
        all_settings = cfg.get("strategy_settings", {})
        if strategy in all_settings:
            del all_settings[strategy]
            set_user_field(uid, "strategy_settings", json.dumps(all_settings))
        
        await query.answer(t.get('settings_reset', 'Settings reset to global'))
        
        # Go back to strategy menu
        await callback_strategy_settings(update, ctx)
        return
    
    # DCA toggle
    if data == "dca_toggle":
        current = cfg.get("dca_enabled", 0)
        new_val = 0 if current else 1
        set_user_field(uid, "dca_enabled", new_val)
        cfg = get_user_config(uid)
        
        status = t.get('status_enabled', 'Enabled') if new_val else t.get('status_disabled', 'Disabled')
        await query.answer(f"DCA: {status}")
        
        # Refresh DCA settings
        text = t.get('dca_settings_header', '⚙️ *DCA Settings (Futures)*\n\n')
        text += f"*{t.get('dca_status', 'Status')}*: {'✅' if new_val else '❌'} {status}\n\n"
        text += f"📉 *Leg 1*: -{cfg.get('dca_pct_1', 10.0)}%\n"
        text += f"📉 *Leg 2*: -{cfg.get('dca_pct_2', 25.0)}%\n\n"
        text += t.get('dca_description', '_DCA will add to position when price moves against you._')
        
        await query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_dca_settings_keyboard(t, cfg)
        )
        return
    
    if data.startswith("dca_param:"):
        param = data.split(":")[1]
        ctx.user_data["dca_setting_mode"] = param
        
        param_names = {
            "dca_pct_1": t.get('prompt_dca_leg1', 'Enter DCA Leg 1 % (e.g., 10):'),
            "dca_pct_2": t.get('prompt_dca_leg2', 'Enter DCA Leg 2 % (e.g., 25):'),
        }
        
        await query.message.edit_text(
            param_names.get(param, f"Enter value for {param}:"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get('btn_cancel', '❌ Cancel'), callback_data="strat_set:dca")]
            ])
        )
        return
    
    # Order type toggle: market <-> limit
    if data.startswith("strat_order_type:"):
        parts = data.split(":")
        strategy = parts[1]
        current_type = parts[2]
        
        # Get context
        context = get_user_trading_context(uid)
        
        # Toggle order type
        new_type = "limit" if current_type == "market" else "market"
        db.set_strategy_setting(uid, strategy, "order_type", new_type,
                               context["exchange"], context["account_type"])
        
        type_labels = {
            "market": t.get('order_type_market', '⚡ Market orders'),
            "limit": t.get('order_type_limit', '🎯 Limit orders'),
        }
        await query.answer(type_labels.get(new_type, new_type))
        
        # Refresh the settings view
        strat_settings = db.get_strategy_settings(uid, strategy, context["exchange"], context["account_type"])
        display_name = STRATEGY_NAMES_MAP.get(strategy, strategy.upper())
        
        lines = [t.get('strategy_param_header', '⚙️ *{name} Settings*').format(name=display_name)]
        lines.append("")
        
        # Order type
        order_type = strat_settings.get("order_type", "market")
        order_emoji = "🎯" if order_type == "limit" else "⚡"
        order_label = "Limit" if order_type == "limit" else "Market"
        lines.append(f"*Order Type*: {order_emoji} {order_label}")
        lines.append("")
        
        global_lbl = t.get('global_default', 'Global')
        pct = strat_settings.get("percent")
        sl = strat_settings.get("sl_percent")
        tp = strat_settings.get("tp_percent")
        lines.append(f"Entry %: {pct if pct is not None else global_lbl}")
        lines.append(f"SL %: {sl if sl is not None else global_lbl}")
        lines.append(f"TP %: {tp if tp is not None else global_lbl}")
        lines.append("")
        atr_per = strat_settings.get("atr_periods")
        atr_mult = strat_settings.get("atr_multiplier_sl")
        atr_trig = strat_settings.get("atr_trigger_pct")
        lines.append(f"ATR Periods: {atr_per if atr_per is not None else global_lbl}")
        lines.append(f"ATR Mult (SL step): {atr_mult if atr_mult is not None else global_lbl}")
        lines.append(f"ATR Trigger %: {atr_trig if atr_trig is not None else global_lbl}")
        
        # Show Scryptomera-specific settings
        if strategy == "scryptomera":
            lines.append("")
            direction = strat_settings.get("direction", "all")
            dir_emoji = {"all": "🔄", "long": "📈", "short": "📉"}.get(direction, "🔄")
            dir_label = {"all": "ALL", "long": "LONG only", "short": "SHORT only"}.get(direction, "ALL")
            lines.append(f"*Direction*: {dir_emoji} {dir_label}")
            
            l_pct = strat_settings.get("long_percent")
            l_sl = strat_settings.get("long_sl_percent")
            l_tp = strat_settings.get("long_tp_percent")
            if any(v is not None for v in [l_pct, l_sl, l_tp]):
                lines.append(f"📈 LONG: Entry={l_pct or global_lbl}, SL={l_sl or global_lbl}, TP={l_tp or global_lbl}")
            
            s_pct = strat_settings.get("short_percent")
            s_sl = strat_settings.get("short_sl_percent")
            s_tp = strat_settings.get("short_tp_percent")
            if any(v is not None for v in [s_pct, s_sl, s_tp]):
                lines.append(f"📉 SHORT: Entry={s_pct or global_lbl}, SL={s_sl or global_lbl}, TP={s_tp or global_lbl}")
        
        await query.message.edit_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=get_strategy_param_keyboard(strategy, t, strat_settings)
        )
        return
    
    # Universal direction toggle handler for ALL strategies
    for strat_name in STRATEGY_NAMES_MAP.keys():
        if data.startswith(f"{strat_name}_dir:"):
            current = data.split(":")[1]
            next_dir = {"all": "long", "long": "short", "short": "all"}.get(current, "all")
            
            # Get context
            context = get_user_trading_context(uid)
            
            # Save new direction
            db.set_strategy_setting(uid, strat_name, "direction", next_dir,
                                   context["exchange"], context["account_type"])
            
            dir_labels = {
                "all": t.get('dir_all', '🔄 ALL (LONG + SHORT)'),
                "long": t.get('dir_long_only', '📈 LONG only'),
                "short": t.get('dir_short_only', '📉 SHORT only'),
            }
            await query.answer(dir_labels.get(next_dir, next_dir))
            
            # Refresh the settings view with updated settings
            strat_settings = db.get_strategy_settings(uid, strat_name, context["exchange"], context["account_type"])
            
            await query.message.edit_text(
                build_strategy_settings_text(strat_name, strat_settings, t),
                parse_mode="Markdown",
                reply_markup=get_strategy_param_keyboard(strat_name, t, strat_settings)
            )
            return
    
    # Universal LONG/SHORT side settings for ALL strategies with side_settings feature
    for strat_name in STRATEGY_NAMES_MAP.keys():
        features = STRATEGY_FEATURES.get(strat_name, {})
        if not features.get("side_settings"):
            continue
            
        if data.startswith(f"{strat_name}_side:"):
            side = data.split(":")[1]  # "long" or "short"
            
            # Get context for proper settings
            context = get_user_trading_context(uid)
            strat_settings = db.get_strategy_settings(uid, strat_name, context["exchange"], context["account_type"])
            
            side_upper = side.upper()
            emoji = "📈" if side == "long" else "📉"
            global_lbl = t.get('global_default', 'Global')
            display_name = STRATEGY_NAMES_MAP.get(strat_name, strat_name.upper())
            
            pct = strat_settings.get(f"{side}_percent")
            sl = strat_settings.get(f"{side}_sl_percent")
            tp = strat_settings.get(f"{side}_tp_percent")
            atr_trigger = strat_settings.get(f"{side}_atr_trigger_pct")
            use_atr = strat_settings.get("use_atr", 0)
            
            lines = [f"{emoji} *{display_name} {side_upper} Settings*"]
            lines.append("")
            lines.append(f"Entry %: {pct if pct is not None else global_lbl}")
            
            # SL/TP only for strategies that support it (not elcaro/fibonacci)
            if strat_name not in ("elcaro", "fibonacci"):
                lines.append(f"SL %: {sl if sl is not None else global_lbl}")
                lines.append(f"TP %: {tp if tp is not None else global_lbl}")
            
            # ATR params only if ATR is enabled for this strategy
            if features.get("use_atr") and use_atr:
                atr_periods = strat_settings.get(f"{side}_atr_periods")
                atr_mult = strat_settings.get(f"{side}_atr_multiplier_sl")
                lines.append(f"ATR Periods: {atr_periods if atr_periods is not None else global_lbl}")
                lines.append(f"ATR Multiplier: {atr_mult if atr_mult is not None else global_lbl}")
                lines.append(f"ATR Trigger %: {atr_trigger if atr_trigger is not None else global_lbl}")
            
            await query.message.edit_text(
                "\n".join(lines),
                parse_mode="Markdown",
                reply_markup=get_strategy_side_keyboard(strat_name, side, t, strat_settings)
            )
            return
    
    # ATR toggle for strategies
    if data.startswith("strat_atr_toggle:"):
        strategy = data.split(":")[1]
        # Get context
        context = get_user_trading_context(uid)
        strat_settings = db.get_strategy_settings(uid, strategy, context["exchange"], context["account_type"])
        # Use 'or 0' because get() returns None if key exists with None value
        current = strat_settings.get("use_atr") or 0
        new_value = 0 if current else 1
        
        logger.info(f"[{uid}] ATR toggle for {strategy}: {current} -> {new_value}")
        
        result = db.set_strategy_setting(uid, strategy, "use_atr", new_value,
                                        context["exchange"], context["account_type"])
        logger.info(f"[{uid}] ATR toggle result: {result}")
        
        status = t.get('atr_enabled', '✅ ATR Trailing enabled') if new_value else t.get('atr_disabled', '❌ ATR Trailing disabled')
        await query.answer(status)
        
        # Refresh settings using unified text builder
        strat_settings = db.get_strategy_settings(uid, strategy, context["exchange"], context["account_type"])
        
        await query.message.edit_text(
            build_strategy_settings_text(strategy, strat_settings, t),
            parse_mode="Markdown",
            reply_markup=get_strategy_param_keyboard(strategy, t, strat_settings)
        )
        return
    
    # Strategy coins group selection
    if data.startswith("strat_coins:"):
        strategy = data.split(":")[1]
        # Show coins group selection for this strategy
        strat_settings = db.get_strategy_settings(uid, strategy)
        current_group = strat_settings.get("coins_group")
        
        buttons = [
            [InlineKeyboardButton(
                ("✓ " if current_group is None else "") + t.get('group_global', '📊 Global (use common setting)'),
                callback_data=f"strat_coins_set:{strategy}:GLOBAL"
            )],
            [InlineKeyboardButton(
                ("✓ " if current_group == "ALL" else "") + "🌐 " + t.get('group_all', 'ALL'),
                callback_data=f"strat_coins_set:{strategy}:ALL"
            )],
            [InlineKeyboardButton(
                ("✓ " if current_group == "TOP100" else "") + "💎 " + t.get('group_top100', 'TOP 100'),
                callback_data=f"strat_coins_set:{strategy}:TOP100"
            )],
            [InlineKeyboardButton(
                ("✓ " if current_group == "VOLATILE" else "") + "🔥 " + t.get('group_volatile', 'VOLATILE'),
                callback_data=f"strat_coins_set:{strategy}:VOLATILE"
            )],
            [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data=f"strat_set:{strategy}")],
        ]
        
        display_name = STRATEGY_NAMES_MAP.get(strategy, strategy.upper())
        await query.message.edit_text(
            t.get('select_coins_for_strategy', '🪙 *Select coins group for {name}*').format(name=display_name),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    
    # Strategy coins group set
    if data.startswith("strat_coins_set:"):
        parts = data.split(":")
        strategy = parts[1]
        group = parts[2]  # "GLOBAL", "ALL", "TOP100", "VOLATILE"
        
        # Get context
        context = get_user_trading_context(uid)
        
        # Set coins_group (None for global)
        new_value = None if group == "GLOBAL" else group
        db.set_strategy_setting(uid, strategy, "coins_group", new_value,
                               context["exchange"], context["account_type"])
        
        group_labels = {
            "GLOBAL": t.get('group_global', '📊 Global'),
            "ALL": "🌐 " + t.get('group_all', 'ALL'),
            "TOP100": "💎 " + t.get('group_top100', 'TOP 100'),
            "VOLATILE": "🔥 " + t.get('group_volatile', 'VOLATILE'),
        }
        await query.answer(group_labels.get(group, group))
        
        # Go back to strategy settings
        strat_settings = db.get_strategy_settings(uid, strategy, context["exchange"], context["account_type"])
        display_name = STRATEGY_NAMES_MAP.get(strategy, strategy.upper())
        
        lines = [t.get('strategy_param_header', '⚙️ *{name} Settings*').format(name=display_name)]
        lines.append("")
        
        global_lbl = t.get('global_default', 'Global')
        
        # Coins group
        coins_group = strat_settings.get("coins_group")
        coins_label = coins_group if coins_group else global_lbl
        lines.append(f"*Coins*: {coins_label}")
        
        # Order type
        order_type = strat_settings.get("order_type", "market")
        order_emoji = "🎯" if order_type == "limit" else "⚡"
        order_label = "Limit" if order_type == "limit" else "Market"
        lines.append(f"*Order Type*: {order_emoji} {order_label}")
        lines.append("")
        
        pct = strat_settings.get("percent")
        sl = strat_settings.get("sl_percent")
        tp = strat_settings.get("tp_percent")
        lines.append(f"Entry %: {pct if pct is not None else global_lbl}")
        lines.append(f"SL %: {sl if sl is not None else global_lbl}")
        lines.append(f"TP %: {tp if tp is not None else global_lbl}")
        
        await query.message.edit_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=get_strategy_param_keyboard(strategy, t, strat_settings)
        )
        return


@require_access
@with_texts
@log_calls
async def cmd_toggle_rsi_bb(update, ctx):
    uid = update.effective_user.id
    cfg = get_user_config(uid) or {}
    new = not bool(cfg.get("trade_rsi_bb", 0))
    set_user_field(uid, "trade_rsi_bb", int(new))
    await update.message.reply_text(
        ctx.t['toggle_rsi_bb_status'].format(
            feature=ctx.t['feature_rsi_bb'],
            status=ctx.t['status_enabled'] if new else ctx.t['status_disabled']
        ),
        reply_markup=main_menu_keyboard(ctx, update=update)
    )

@with_texts
@log_calls
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if _is_banned(uid):
        await update.message.reply_text(ctx.t['banned'])
        return

    if not _is_allowed_user(uid):
        await _notify_admin_new_user(update, ctx)
        await update.message.reply_text(ctx.t['invite_only'])
        return

    cfg = get_user_config(uid) or {}
    if not cfg.get("terms_accepted", 0):
        await update.message.reply_text(ctx.t['need_terms'])
        await cmd_terms(update, ctx)
        return
    
    # Setup personalized Menu Button with user_id for auto-login
    try:
        # Get webapp URL from env, fallback to ngrok file, then default
        webapp_url = WEBAPP_URL
        if webapp_url == "http://localhost:8765":
            ngrok_file = Path(__file__).parent / "run" / "ngrok_url.txt"
            if ngrok_file.exists():
                webapp_url = ngrok_file.read_text().strip()
        
        # Add user_id as start param for auto-login
        # Landing page handles auth and redirects to dashboard
        # Add timestamp to prevent Telegram from caching old URL
        import time
        cache_bust = int(time.time())
        webapp_url_with_user = f"{webapp_url}?start={uid}&_t={cache_bust}"
        menu_button = MenuButtonWebApp(
            text="🖥️ Dashboard",
            web_app=WebAppInfo(url=webapp_url_with_user)
        )
        await ctx.bot.set_chat_menu_button(chat_id=uid, menu_button=menu_button)
        logger.info(f"[{uid}] Personalized menu button set: {webapp_url_with_user}")
    except Exception as e:
        logger.warning(f"Failed to set menu button for {uid}: {e}")

    # Send user guide PDF on first start (only once)
    if not cfg.get("guide_sent", 0):
        try:
            lang = cfg.get("lang", "en")
            pdf_buffer = get_user_guide_pdf(lang)
            guide_caption = ctx.t.get('guide_caption', '📚 Trading Bot User Guide\n\nPlease read this guide to learn how to configure strategies and use the bot effectively.')
            await update.message.reply_document(
                document=InputFile(pdf_buffer, filename="Bybit_Trading_Bot_Guide.pdf"),
                caption=guide_caption
            )
            set_user_field(uid, "guide_sent", 1)
        except Exception as e:
            logger.warning(f"Failed to send user guide PDF to {uid}: {e}")

    # Build active strategies list for welcome message
    strategy_map = {
        "trade_oi": "📊 OI",
        "trade_rsi_bb": "📉 RSI+BB", 
        "trade_scryptomera": "🔮 Scryptomera",
        "trade_scalper": "🎯 Scalper",
        "trade_elcaro": "🔥 Elcaro",
        "trade_fibonacci": "📐 Fibonacci",
    }
    active_strategies = [name for key, name in strategy_map.items() if cfg.get(key, 0)]
    strategies_text = ", ".join(active_strategies) if active_strategies else ctx.t.get('no_strategies', '❌ None')
    
    welcome_text = f"{ctx.t['welcome']}\n\n📡 <b>Active Strategies:</b> {strategies_text}"
    await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard(ctx, update=update), parse_mode="HTML")

@with_texts
async def _notify_admin_new_user(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    uid = u.id
    name_raw = f"{u.first_name or ''} {u.last_name or ''}".strip() or ctx.t['mark_no']
    name = html.escape(name_raw)
    uname = f"@{u.username}" if u.username else ctx.t['mark_no']
    lang = getattr(u, "language_code", ctx.t['mark_no'])
    cfg = get_user_config(uid) or {}
    allowed = ctx.t['mark_yes'] if cfg.get('is_allowed') else ctx.t['mark_no']
    banned = ctx.t['mark_ban'] if cfg.get('is_banned') else ctx.t['mark_no']

    def T(k, **kw): 
        s = ctx.t.get(k, k)
        return s.format(**kw) if kw else s

    wave = T("wave")
    title = T("title")
    text = T("admin_new_user_html", wave=wave, title=title, uid=uid, name=name, uname=uname, lang=lang, allowed=allowed, banned=banned)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(T("btn_approve"), callback_data=f"mod:approve:{uid}"),
        InlineKeyboardButton(T("btn_ban"), callback_data=f"mod:ban:{uid}")
    ]])
    try:
        await ctx.bot.send_message(ADMIN_ID, text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
    except Exception as e:
        logger.warning(T("admin_notify_fail", e=e))


@with_texts
@log_calls
async def on_moderate_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    admin_uid = update.effective_user.id
    if admin_uid != ADMIN_ID:
        await q.answer(ctx.t['not_allowed'], show_alert=True)
        return
    try:
        _, action, raw_uid = q.data.split(":", 2)
        target_uid = int(raw_uid)
    except Exception:
        await q.answer(ctx.t['bad_payload'], show_alert=True)
        return

    if action == "approve":
        set_user_field(target_uid, "is_allowed", 1)
        set_user_field(target_uid, "is_banned", 0)
        await q.edit_message_reply_markup(reply_markup=None)
        await q.message.reply_text(ctx.t['moderation_approved'].format(target=target_uid))
        try:
            await ctx.bot.send_message(target_uid, ctx.t['approved_user_dm'])
        except Exception:
            pass
    elif action == "ban":
        set_user_field(target_uid, "is_banned", 1)
        set_user_field(target_uid, "is_allowed", 0)
        await q.edit_message_reply_markup(reply_markup=None)
        await q.message.reply_text(ctx.t['moderation_banned'].format(target=target_uid))
        try:
            await ctx.bot.send_message(target_uid, ctx.t['banned_user_dm'])
        except Exception:
            pass
    else:
        await q.answer(ctx.t['unknown_action'], show_alert=True)

@log_calls
async def fetch_realized_pnl(uid: int, days: int = 1, account_type: str | None = None, exchange: str | None = None) -> float:
    """
    Fetch realized PnL for the last N days.
    
    Args:
        uid: User ID
        days: Number of days to look back (default: 1)
        account_type: 'demo' or 'real' (defaults to user's trading_mode)
        exchange: 'bybit' or 'hyperliquid' (defaults to user's active exchange)
    
    Returns:
        Total realized PnL in USDT
    """
    end_ts = int(time.time() * 1000)
    start_ts = end_ts - days * 24 * 60 * 60 * 1000
    total_pnl = 0.0
    
    # Determine exchange
    if exchange is None:
        exchange = db.get_exchange_type(uid) or 'bybit'
    
    if exchange == 'hyperliquid':
        # Use HyperLiquid adapter for PnL
        try:
            creds = db.get_hl_credentials(uid)
            if creds and creds.get("private_key"):
                from hl_adapter import HLAdapter
                adapter = HLAdapter(
                    private_key=creds["private_key"],
                    testnet=bool(creds.get("testnet", False)),
                    vault_address=creds.get("vault_address")
                )
                await adapter.initialize()
                
                # Get fills for the period
                fills = await adapter.get_fills_by_time(start_ts, end_ts)
                for fill in fills:
                    try:
                        total_pnl += float(fill.get("closedPnl") or fill.get("pnl") or 0.0)
                    except Exception:
                        pass
                
                await adapter.close()
        except Exception as e:
            logger.warning(f"[{uid}] HL realized PnL fetch error: {e}")
    else:
        # Bybit
        cursor = None
        while True:
            params = {
                "category": "linear",
                "startTime": start_ts,
                "endTime": end_ts,
                "limit": 100,      
            }
            if cursor:
                params["cursor"] = cursor

            res = await _bybit_request(uid, "GET", "/v5/position/closed-pnl", params=params, account_type=account_type)
            for item in res.get("list", []):
                total_pnl += float(item.get("closedPnl", 0))

            cursor = res.get("nextPageCursor")
            if not cursor:
                break

    return total_pnl

@require_access
@with_texts
@log_calls
async def cmd_account(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    try:
        bal = await fetch_usdt_balance(uid)
        pnl_today = await fetch_today_realized_pnl(uid, tz_str=get_user_tz(uid))
        pnl_week  = await fetch_realized_pnl(uid, days=7)
        positions     = await fetch_open_positions(uid)
        total_unreal  = sum(float(p.get("unrealisedPnl", 0)) for p in positions)
        total_im      = sum(float(p.get("positionIM",      0)) for p in positions)
        unreal_pct    = (total_unreal / total_im * 100) if total_im else 0.0

        text = "\n".join([
            ctx.t['account_balance'].format(balance=bal),
            "",
            ctx.t['account_realized_header'],
            ctx.t['account_realized_day'].format(pnl=pnl_today),
            ctx.t['account_realized_week'].format(pnl=pnl_week),
            "",
            ctx.t['account_unreal_header'],
            ctx.t['account_unreal_total'].format(unreal=total_unreal),
            ctx.t['account_unreal_pct'].format(pct=unreal_pct),
        ])
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        logger.exception("Error в cmd_account")
        await update.message.reply_text(ctx.t.get("error_generic", "Error: {msg}").format(msg=str(e)))

@require_access
@with_texts
@log_calls
async def cmd_show_config(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cfg = get_user_config(uid) or {}

    coins = cfg.get('coins')
    if isinstance(coins, str):
        coins_display = coins if coins else 'ALL'
    else:
        coins_display = ', '.join(coins) if coins else 'ALL'

    percent   = cfg.get('percent', 1)
    tp_pct    = cfg.get('tp_percent', 0)
    sl_pct    = cfg.get('sl_percent', 0)

    # Status emojis
    on = "✅"
    off = "❌"
    
    lines = [
        ctx.t['config_header'],
        f"• 💠 {ctx.t.get('config_coins_label', 'Coins')}: {coins_display}",
        f"• 📊 {ctx.t.get('config_percent_label', '% per Trade')}: {percent}%",
        f"• 🎯 TP%: {tp_pct}%  |  🛑 SL%: {sl_pct}%",
        f"• {ctx.t['config_stop_mode'].format(mode = ctx.t['mode_atr'] if cfg.get('use_atr',0) else ctx.t['mode_fixed'])}",
        f"• DCA: Leg1=-{cfg.get('dca_pct_1', 10.0)}%, Leg2=-{cfg.get('dca_pct_2', 25.0)}%",
        "",
        "*━━━ Strategies ━━━*",
    ]
    
    # Strategy details
    strategy_info = [
        ("oi", "📉 OI", "trade_oi"),
        ("rsi_bb", "📊 RSI+BB", "trade_rsi_bb"),
        ("scryptomera", "🐱 Scryptomera", "trade_scryptomera"),
        ("scalper", "⚡ Scalper", "trade_scalper"),
        ("elcaro", "🔥 Elcaro", "trade_elcaro"),
    ]
    
    global_lbl = ctx.t.get('global_default', 'Global')
    
    for strat_key, strat_name, trade_field in strategy_info:
        is_enabled = cfg.get(trade_field, 0)
        status = on if is_enabled else off
        
        strat_settings = db.get_strategy_settings(uid, strat_key)
        order_type = strat_settings.get("order_type", "market")
        order_lbl = "🎯L" if order_type == "limit" else "⚡M"
        coins_group = strat_settings.get("coins_group") or global_lbl
        
        pct = strat_settings.get("percent")
        sl = strat_settings.get("sl_percent")
        tp = strat_settings.get("tp_percent")
        
        details = []
        if pct is not None:
            details.append(f"E:{pct}%")
        if sl is not None:
            details.append(f"SL:{sl}%")
        if tp is not None:
            details.append(f"TP:{tp}%")
        
        detail_str = ", ".join(details) if details else global_lbl
        
        line = f"{status} {strat_name}: {order_lbl} | {coins_group}"
        if details:
            line += f" | {detail_str}"
        
        # Scryptomera special - show direction
        if strat_key == "scryptomera":
            direction = strat_settings.get("direction", "all")
            dir_icon = {"all": "🔄", "long": "📈", "short": "📉"}.get(direction, "🔄")
            line += f" | {dir_icon}"
        
        lines.append(line)

    text = "\n".join(lines)

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(ctx, update=update)
    )


@log_calls
async def fetch_account_balance(user_id: int, account_type: str = None) -> dict:
    """Fetch full account balance including totalEquity (all assets converted to USD).
    
    Returns dict with:
    - total_equity: Total account value in USD (all coins)
    - total_wallet: Total wallet balance in USD
    - available_balance: Available for trading (total, all collateral)
    - used_margin: Margin used by open positions
    - usdt_wallet: USDT wallet balance
    - usdt_available: USDT available for trading (key metric!)
    - usdt_position_margin: USDT margin in positions
    - usdt_order_margin: USDT margin in orders
    - coins: List of individual coin balances
    """
    def safe_float(val, default=0.0):
        """Convert value to float, handling empty strings and None"""
        if val is None or val == "" or val == "":
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default
    
    # First get all coins for total equity
    params = {"accountType": "UNIFIED"}
    try:
        res = await _bybit_request(user_id, "GET", "/v5/account/wallet-balance", params=params, account_type=account_type)
    except MissingAPICredentials:
        return {"total_equity": 0.0, "available_balance": 0.0, "used_margin": 0.0, "usdt_available": 0.0, "coins": []}
    
    # Also get USDT-specific data for trading margin (separate request with coin=USDT)
    usdt_wallet = 0.0
    usdt_available = 0.0
    usdt_position_im = 0.0
    usdt_order_im = 0.0
    usdt_equity = 0.0
    
    try:
        usdt_res = await _bybit_request(user_id, "GET", "/v5/account/wallet-balance", 
                                         params={"accountType": "UNIFIED", "coin": "USDT"}, 
                                         account_type=account_type)
        for acct in usdt_res.get("list", []) or []:
            for c in acct.get("coin", []) or []:
                if c.get("coin") == "USDT":
                    usdt_wallet = safe_float(c.get("walletBalance"))
                    usdt_equity = safe_float(c.get("equity"))
                    usdt_position_im = safe_float(c.get("totalPositionIM"))
                    usdt_order_im = safe_float(c.get("totalOrderIM"))
                    # Available = wallet - position margin - order margin
                    usdt_available = usdt_wallet - usdt_position_im - usdt_order_im
                    if usdt_available < 0:
                        usdt_available = 0.0
                    break
    except Exception as e:
        logger.warning(f"Failed to fetch USDT-specific balance: {e}")
    
    for acct in res.get("list", []) or []:
        # Account-level totals (all coins combined, in USD)
        total_equity = safe_float(acct.get("totalEquity"))
        total_wallet = safe_float(acct.get("totalWalletBalance"))
        total_available = safe_float(acct.get("totalAvailableBalance"))
        total_margin = safe_float(acct.get("totalInitialMargin"))
        
        # Individual coin balances and calculate margin from coins
        coins = []
        total_position_im = 0.0
        total_order_im = 0.0
        for c in acct.get("coin", []) or []:
            coin_name = c.get("coin", "")
            wallet_bal = safe_float(c.get("walletBalance"))
            usd_value = safe_float(c.get("usdValue"))
            position_im = safe_float(c.get("totalPositionIM"))
            order_im = safe_float(c.get("totalOrderIM"))
            
            total_position_im += position_im
            total_order_im += order_im
            
            if wallet_bal > 0 or usd_value > 0:
                coins.append({
                    "coin": coin_name,
                    "balance": wallet_bal,
                    "usd_value": usd_value
                })
        
        # For Demo accounts, calculate from coin data if account-level is empty
        if total_available == 0 and total_wallet > 0:
            total_available = total_wallet - total_position_im - total_order_im
            if total_available < 0:
                total_available = 0.0
        
        if total_margin == 0:
            total_margin = total_position_im + total_order_im
        
        # If USDT margin is still 0, fetch from positions API (Demo fallback)
        if usdt_position_im == 0 and account_type == "demo":
            try:
                pos_res = await _bybit_request(user_id, "GET", "/v5/position/list", 
                                               params={"category": "linear", "settleCoin": "USDT"}, 
                                               account_type=account_type)
                positions = pos_res.get("list", [])
                for p in positions:
                    usdt_position_im += safe_float(p.get("positionIM"))
                
                usdt_available = usdt_wallet - usdt_position_im - usdt_order_im
                if usdt_available < 0:
                    usdt_available = 0.0
                    
                if total_margin == 0:
                    total_margin = usdt_position_im + usdt_order_im
            except Exception as e:
                logger.warning(f"Failed to fetch positions for margin calc: {e}")
        
        return {
            "total_equity": total_equity,
            "total_wallet": total_wallet,
            "available_balance": total_available,
            "used_margin": total_margin,
            "usdt_wallet": usdt_wallet,
            "usdt_available": usdt_available,
            "usdt_position_margin": usdt_position_im,
            "usdt_order_margin": usdt_order_im,
            "usdt_equity": usdt_equity,
            "coins": coins
        }
    
    return {"total_equity": 0.0, "available_balance": 0.0, "used_margin": 0.0, "usdt_available": 0.0, "coins": []}


@log_calls
async def fetch_usdt_balance(user_id: int, account_type: str = None) -> float:
    """Fetch AVAILABLE USDT margin for trading.
    
    Returns the actual free USDT that can be used to open new positions:
    available = walletBalance - totalPositionIM - totalOrderIM
    
    This is the correct value for position sizing calculations.
    """
    params = {"accountType": "UNIFIED", "coin": "USDT"}
    try:
        res = await _bybit_request(user_id, "GET", "/v5/account/wallet-balance", params=params, account_type=account_type)
    except MissingAPICredentials:
        return 0.0

    for acct in res.get("list", []) or []:
        for c in acct.get("coin", []) or []:
            if c.get("coin") == "USDT":
                try:
                    wallet_balance = float(c.get("walletBalance") or 0)
                    position_im = float(c.get("totalPositionIM") or 0)
                    order_im = float(c.get("totalOrderIM") or 0)
                    
                    # Available for trading = wallet - margin in positions - margin in orders
                    available = wallet_balance - position_im - order_im
                    if available < 0:
                        available = 0.0
                    
                    logger.info(f"[{user_id}] USDT available for trading: {available:.2f} (wallet={wallet_balance:.2f} - posIM={position_im:.2f} - ordIM={order_im:.2f}) [{account_type or 'auto'}]")
                    return available
                except (TypeError, ValueError) as e:
                    logger.warning(f"[{user_id}] Error parsing USDT balance: {e}")
                    return 0.0
    return 0.0


# ==============================================================================
# SPOT TRADING MODULE
# ==============================================================================

@log_calls
async def fetch_spot_balance(user_id: int, account_type: str = None) -> dict:
    """Fetch Spot account balances from UNIFIED account.
    
    Returns dict like: {"USDT": 100.0, "BTC": 0.001, "ETH": 0.5}
    """
    params = {"accountType": "UNIFIED"}
    try:
        res = await _bybit_request(user_id, "GET", "/v5/account/wallet-balance", params=params, account_type=account_type)
    except MissingAPICredentials:
        return {}
    except Exception as e:
        logger.error(f"fetch_spot_balance error: {e}")
        return {}
    
    balances = {}
    for acct in res.get("list", []) or []:
        for c in acct.get("coin", []) or []:
            coin = c.get("coin", "")
            try:
                wallet_bal = float(c.get("walletBalance") or 0.0)
                if wallet_bal > 0:
                    balances[coin] = wallet_bal
            except (TypeError, ValueError):
                pass
    return balances


@log_calls
async def get_spot_ticker(user_id: int, symbol: str, account_type: str = None) -> dict:
    """Get current price info for a spot symbol (e.g., BTCUSDT)."""
    params = {"category": "spot", "symbol": symbol}
    try:
        res = await _bybit_request(user_id, "GET", "/v5/market/tickers", params=params, account_type=account_type)
        tickers = res.get("list", [])
        if tickers:
            return tickers[0]
    except Exception as e:
        logger.error(f"get_spot_ticker error for {symbol}: {e}")
    return {}


# Cache for Fear & Greed Index (updates every hour)
_fear_greed_cache = {"value": 50, "timestamp": 0}

# Cache for spot auto-DCA last execution timestamps per user
# Key: user_id, Value: last execution unix timestamp
_spot_dca_last_exec: dict[int, int] = {}

# Frequency intervals in seconds
SPOT_DCA_INTERVALS = {
    "daily": 24 * 60 * 60,      # 24 hours
    "weekly": 7 * 24 * 60 * 60,  # 7 days
    "monthly": 30 * 24 * 60 * 60,  # 30 days (approximate)
}

async def get_fear_greed_index() -> int:
    """
    Fetch the Fear & Greed Index from alternative.me API.
    Returns a value from 0 (Extreme Fear) to 100 (Extreme Greed).
    Caches the result for 1 hour.
    """
    global _fear_greed_cache
    
    now = time.time()
    # Return cached value if less than 1 hour old
    if now - _fear_greed_cache["timestamp"] < 3600:
        return _fear_greed_cache["value"]
    
    try:
        async with _session.get(
            "https://api.alternative.me/fng/",
            timeout=ClientTimeout(total=10)
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get("data") and len(data["data"]) > 0:
                    value = int(data["data"][0].get("value", 50))
                    _fear_greed_cache = {"value": value, "timestamp": now}
                    logger.info(f"Fear & Greed Index updated: {value}")
                    return value
    except Exception as e:
        logger.warning(f"Failed to fetch Fear & Greed Index: {e}")
    
    # Return cached or default value on error
    return _fear_greed_cache.get("value", 50)


async def calculate_smart_dca_amount(
    base_amount: float,
    strategy: str,
    coin: str,
    spot_settings: dict,
    user_id: int,
    account_type: str = None,
) -> float:
    """
    Calculate the adjusted DCA amount based on the selected strategy.
    
    Strategies:
    - fixed: Always return base_amount
    - value_avg: Increase amount when price is below avg, decrease when above
    - fear_greed: Increase amount during market fear
    - dip_buy: Only buy on significant dips
    
    Returns the adjusted amount (0 if should skip this buy).
    """
    if strategy == "fixed":
        return base_amount
    
    if strategy == "fear_greed":
        # Get Fear & Greed Index
        fg_index = await get_fear_greed_index()
        fear_threshold = spot_settings.get("fear_threshold", 25)
        
        if fg_index <= fear_threshold:
            # Extreme fear - buy 2x
            multiplier = 2.0
            logger.info(f"Fear & Greed = {fg_index} (extreme fear) → 2x multiplier")
        elif fg_index <= 40:
            # Fear - buy 1.5x
            multiplier = 1.5
        elif fg_index >= 75:
            # Extreme greed - skip or reduce
            multiplier = 0.5
            logger.info(f"Fear & Greed = {fg_index} (extreme greed) → 0.5x multiplier")
        else:
            # Neutral
            multiplier = 1.0
        
        return base_amount * multiplier
    
    if strategy == "dip_buy":
        # Only buy if price dropped by X% from 7-day high
        dip_threshold = spot_settings.get("dip_threshold", 5.0)
        symbol = f"{coin}USDT"
        
        try:
            # Get current price
            ticker = await get_spot_ticker(user_id, symbol, account_type)
            current_price = float(ticker.get("lastPrice", 0))
            
            # Get 7-day high (using klines)
            params = {
                "category": "spot",
                "symbol": symbol,
                "interval": "D",
                "limit": 7,
            }
            res = await _bybit_request(user_id, "GET", "/v5/market/kline", params=params, account_type=account_type)
            klines = res.get("list", [])
            
            if klines and current_price > 0:
                high_7d = max(float(k[2]) for k in klines)  # k[2] is high price
                drop_pct = ((high_7d - current_price) / high_7d) * 100
                
                if drop_pct >= dip_threshold:
                    # It's a dip! Buy more based on how much it dropped
                    multiplier = 1.0 + (drop_pct / 10)  # +10% for each 10% drop
                    logger.info(f"{coin} dip detected: -{drop_pct:.1f}% from 7d high → {multiplier:.1f}x")
                    return base_amount * multiplier
                else:
                    logger.info(f"{coin} not a dip ({drop_pct:.1f}% < {dip_threshold}%) → skip")
                    return 0.0  # Skip this buy
        except Exception as e:
            logger.error(f"dip_buy calculation error for {coin}: {e}")
            return base_amount  # Fallback to base amount
    
    if strategy == "value_avg":
        # Value averaging - try to maintain steady growth
        # Buy more when below target, less when above
        # This is a simplified version
        symbol = f"{coin}USDT"
        
        try:
            ticker = await get_spot_ticker(user_id, symbol, account_type)
            change_24h = float(ticker.get("price24hPcnt", 0)) * 100
            
            if change_24h < -5:
                # Price down significantly - buy more
                multiplier = 1.5
            elif change_24h < 0:
                # Price down slightly - buy normal
                multiplier = 1.2
            elif change_24h > 10:
                # Price up significantly - buy less
                multiplier = 0.5
            elif change_24h > 5:
                # Price up - buy slightly less
                multiplier = 0.8
            else:
                multiplier = 1.0
            
            logger.info(f"{coin} 24h change: {change_24h:.1f}% → {multiplier:.1f}x multiplier")
            return base_amount * multiplier
        except Exception as e:
            logger.error(f"value_avg calculation error for {coin}: {e}")
            return base_amount
    
    return base_amount


@log_calls
async def get_spot_instrument_info(user_id: int, symbol: str, account_type: str = None) -> dict:
    """Get instrument info for spot symbol (min order size, decimals, etc)."""
    params = {"category": "spot", "symbol": symbol}
    try:
        res = await _bybit_request(user_id, "GET", "/v5/market/instruments-info", params=params, account_type=account_type)
        instruments = res.get("list", [])
        if instruments:
            return instruments[0]
    except Exception as e:
        logger.error(f"get_spot_instrument_info error for {symbol}: {e}")
    return {}


@log_calls  
async def place_spot_order(
    user_id: int,
    symbol: str,
    side: str,  # "Buy" or "Sell"
    qty: float,
    order_type: str = "Market",
    price: float = None,
    account_type: str = None,
) -> dict:
    """Place a spot order.
    
    Args:
        user_id: Telegram user ID
        symbol: Spot symbol like "BTCUSDT"
        side: "Buy" or "Sell"
        qty: Quantity to buy/sell (in quote currency for market buy)
        order_type: "Market" or "Limit"
        price: Price for limit orders
        account_type: 'demo', 'real', or None
    """
    import uuid
    order_link_id = f"spot_{uuid.uuid4().hex[:20]}"
    
    # Get instrument info for proper qty rounding (fix "too many decimals" error)
    if side == "Sell" or order_type == "Limit":
        try:
            inst_info = await get_spot_instrument_info(user_id, symbol, account_type)
            if inst_info:
                # basePrecision is the decimal precision for base coin qty
                base_precision = inst_info.get("lotSizeFilter", {}).get("basePrecision", "0.00001")
                # Calculate decimal places from precision string
                if "." in base_precision:
                    decimals = len(base_precision.split(".")[1].rstrip("0")) or 1
                else:
                    decimals = 0
                # Round qty to proper precision
                import math
                qty = math.floor(qty * (10 ** decimals)) / (10 ** decimals)
                logger.debug(f"Spot order qty rounded to {decimals} decimals: {qty}")
        except Exception as e:
            logger.warning(f"Could not get spot instrument info for rounding: {e}")
    
    body = {
        "category": "spot",
        "symbol": symbol,
        "side": side,
        "orderType": order_type,
        "orderLinkId": order_link_id,
    }
    
    if order_type == "Market" and side == "Buy":
        # For market buy, use quote order qty (USDT amount)
        body["marketUnit"] = "quoteCoin"
        body["qty"] = str(qty)
    else:
        # For market sell or limit orders, qty is in base coin
        body["qty"] = str(qty)
        
    if order_type == "Limit" and price:
        body["price"] = str(price)
        body["timeInForce"] = "GTC"
    
    try:
        res = await _bybit_request(user_id, "POST", "/v5/order/create", body=body, account_type=account_type)
        logger.info(f"Spot order placed [{account_type or 'auto'}]: {res}")
        return res
    except RuntimeError as e:
        msg = str(e).lower()
        if "insufficient" in msg or "balance" in msg or "110007" in msg or "ab not enough" in msg:
            raise ValueError("INSUFFICIENT_BALANCE")
        # 170140 = Order value exceeded lower limit (order too small)
        if "170140" in str(e) or "lower limit" in msg:
            raise ValueError("ORDER_TOO_SMALL")
        # 170136 = Order qty too small
        if "170136" in str(e) or "qty" in msg and "small" in msg:
            raise ValueError("ORDER_TOO_SMALL")
        raise


async def execute_spot_dca_buy(
    user_id: int,
    coin: str,
    usdt_amount: float,
    account_type: str = None,
) -> dict:
    """Execute a DCA buy for a specific coin.
    
    Args:
        user_id: Telegram user ID
        coin: Coin to buy (e.g., "BTC", "ETH")
        usdt_amount: Amount in USDT to spend
        account_type: 'demo', 'real', or None
        
    Returns:
        dict with result info
    """
    symbol = f"{coin}USDT"
    
    # Get current price
    ticker = await get_spot_ticker(user_id, symbol, account_type)
    if not ticker:
        return {"success": False, "error": f"Could not get price for {symbol}"}
    
    current_price = float(ticker.get("lastPrice", 0))
    if current_price <= 0:
        return {"success": False, "error": f"Invalid price for {symbol}"}
    
    try:
        result = await place_spot_order(
            user_id=user_id,
            symbol=symbol,
            side="Buy",
            qty=usdt_amount,
            order_type="Market",
            account_type=account_type,
        )
        
        # Calculate approximate qty bought
        qty_bought = usdt_amount / current_price
        
        # Update purchase history for TP tracking
        try:
            cfg = db.get_user_config(user_id)
            spot_settings = cfg.get("spot_settings", {})
            purchase_history = spot_settings.get("purchase_history", {})
            
            if coin not in purchase_history:
                purchase_history[coin] = {
                    "total_qty": 0.0,
                    "total_cost": 0.0,
                    "avg_price": 0.0,
                    "purchases": [],
                }
            
            coin_history = purchase_history[coin]
            coin_history["total_qty"] += qty_bought
            coin_history["total_cost"] += usdt_amount
            coin_history["avg_price"] = coin_history["total_cost"] / coin_history["total_qty"] if coin_history["total_qty"] > 0 else 0
            coin_history["purchases"].append({
                "ts": int(time.time()),
                "qty": qty_bought,
                "price": current_price,
                "usdt": usdt_amount,
            })
            
            # Keep only last 50 purchases per coin
            if len(coin_history["purchases"]) > 50:
                coin_history["purchases"] = coin_history["purchases"][-50:]
            
            purchase_history[coin] = coin_history
            spot_settings["purchase_history"] = purchase_history
            db.set_user_field(user_id, "spot_settings", json.dumps(spot_settings))
            
        except Exception as e:
            logger.warning(f"Failed to update purchase history: {e}")
        
        return {
            "success": True,
            "coin": coin,
            "symbol": symbol,
            "qty": qty_bought,
            "usdt_spent": usdt_amount,
            "price": current_price,
            "order": result,
        }
    except ValueError as e:
        err_str = str(e)
        if err_str == "ORDER_TOO_SMALL":
            # Silently skip - amount too small for exchange minimum
            logger.debug(f"Spot DCA {coin}: order too small (${usdt_amount:.2f}), skipping")
            return {"success": False, "error": "SKIP", "reason": "order_too_small"}
        if err_str == "INSUFFICIENT_BALANCE":
            return {"success": False, "error": "SKIP", "reason": "insufficient_balance"}
        return {"success": False, "error": err_str}
    except Exception as e:
        # Don't show raw API errors to user
        logger.warning(f"execute_spot_dca_buy {coin}: {e}")
        return {"success": False, "error": "SKIP", "reason": "api_error"}


async def execute_spot_sell(
    user_id: int,
    coin: str,
    qty: float = None,
    sell_pct: float = None,
    account_type: str = None,
) -> dict:
    """Execute a spot sell for a specific coin.
    
    Args:
        user_id: Telegram user ID
        coin: Coin to sell (e.g., "BTC", "ETH")
        qty: Quantity to sell (in base coin). If None, use sell_pct.
        sell_pct: Percentage of holdings to sell (0-100). Used if qty is None.
        account_type: 'demo', 'real', or None
        
    Returns:
        dict with result info
    """
    symbol = f"{coin}USDT"
    
    # Get current balance if we need to calculate qty from percentage
    if qty is None:
        balances = await fetch_spot_balance(user_id, account_type=account_type)
        coin_balance = balances.get(coin, 0)
        
        if coin_balance <= 0:
            return {"success": False, "error": f"No {coin} balance to sell"}
        
        if sell_pct is None:
            sell_pct = 100.0  # Sell all by default
        
        qty = coin_balance * (sell_pct / 100.0)
        
        # For 100% sell, use slightly less to avoid "insufficient balance" due to rounding
        if sell_pct >= 99.9:
            qty = coin_balance * 0.9999  # Leave tiny dust to avoid rounding issues
    
    if qty <= 0:
        return {"success": False, "error": "Invalid quantity"}
    
    # Get current price
    ticker = await get_spot_ticker(user_id, symbol, account_type)
    if not ticker:
        return {"success": False, "error": f"Could not get price for {symbol}"}
    
    current_price = float(ticker.get("lastPrice", 0))
    if current_price <= 0:
        return {"success": False, "error": f"Invalid price for {symbol}"}
    
    try:
        result = await place_spot_order(
            user_id=user_id,
            symbol=symbol,
            side="Sell",
            qty=qty,
            order_type="Market",
            account_type=account_type,
        )
        
        usdt_received = qty * current_price
        
        # Update purchase history
        try:
            cfg = db.get_user_config(user_id)
            spot_settings = cfg.get("spot_settings", {})
            purchase_history = spot_settings.get("purchase_history", {})
            
            if coin in purchase_history:
                coin_history = purchase_history[coin]
                # Reduce tracked qty
                coin_history["total_qty"] = max(0, coin_history["total_qty"] - qty)
                # Reduce cost proportionally
                if coin_history["total_qty"] > 0:
                    sold_ratio = qty / (coin_history["total_qty"] + qty)
                    coin_history["total_cost"] = coin_history["total_cost"] * (1 - sold_ratio)
                else:
                    coin_history["total_cost"] = 0
                    coin_history["avg_price"] = 0
                
                purchase_history[coin] = coin_history
                spot_settings["purchase_history"] = purchase_history
                db.set_user_field(user_id, "spot_settings", json.dumps(spot_settings))
        except Exception as e:
            logger.warning(f"Failed to update purchase history on sell: {e}")
        
        return {
            "success": True,
            "coin": coin,
            "symbol": symbol,
            "qty_sold": qty,
            "usdt_received": usdt_received,
            "price": current_price,
            "order": result,
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"execute_spot_sell error: {e}")
        return {"success": False, "error": str(e)}


async def check_spot_tp_levels(
    user_id: int,
    account_type: str = None,
) -> list:
    """Check all spot holdings for TP level triggers and execute sells if needed.
    
    Returns list of executed sells.
    """
    cfg = db.get_user_config(user_id)
    spot_settings = cfg.get("spot_settings", {})
    
    if not spot_settings.get("tp_enabled"):
        return []
    
    purchase_history = spot_settings.get("purchase_history", {})
    tp_levels = spot_settings.get("tp_levels", DEFAULT_SPOT_TP_LEVELS)
    tp_executed = spot_settings.get("tp_executed", {})  # Track which levels were triggered
    
    executed_sells = []
    
    for coin, coin_history in purchase_history.items():
        avg_price = coin_history.get("avg_price", 0)
        total_qty = coin_history.get("total_qty", 0)
        
        if avg_price <= 0 or total_qty <= 0:
            continue
        
        symbol = f"{coin}USDT"
        
        try:
            ticker = await get_spot_ticker(user_id, symbol, account_type)
            if not ticker:
                continue
            
            current_price = float(ticker.get("lastPrice", 0))
            if current_price <= 0:
                continue
            
            # Calculate gain percentage
            gain_pct = ((current_price - avg_price) / avg_price) * 100
            
            # Check each TP level
            coin_tp_executed = tp_executed.get(coin, [])
            
            for i, level in enumerate(tp_levels):
                level_gain = level.get("gain_pct", 0)
                level_sell_pct = level.get("sell_pct", 0)
                
                # Skip if this level was already executed
                if i in coin_tp_executed:
                    continue
                
                # Check if gain reached this level
                if gain_pct >= level_gain:
                    logger.info(f"Spot TP triggered: {coin} +{gain_pct:.1f}% >= {level_gain}%, selling {level_sell_pct}%")
                    
                    result = await execute_spot_sell(
                        user_id=user_id,
                        coin=coin,
                        sell_pct=level_sell_pct,
                        account_type=account_type,
                    )
                    
                    if result.get("success"):
                        # Mark level as executed
                        coin_tp_executed.append(i)
                        tp_executed[coin] = coin_tp_executed
                        
                        executed_sells.append({
                            "coin": coin,
                            "level": i + 1,
                            "gain_pct": gain_pct,
                            "sell_pct": level_sell_pct,
                            "qty_sold": result.get("qty_sold", 0),
                            "usdt_received": result.get("usdt_received", 0),
                        })
                    else:
                        logger.error(f"Spot TP sell failed: {result.get('error')}")
        
        except Exception as e:
            logger.error(f"check_spot_tp_levels error for {coin}: {e}")
    
    # Save updated tp_executed state
    if executed_sells:
        spot_settings["tp_executed"] = tp_executed
        db.set_user_field(user_id, "spot_settings", json.dumps(spot_settings))
    
    return executed_sells


async def rebalance_spot_portfolio(
    user_id: int,
    account_type: str = None,
) -> dict:
    """Rebalance spot portfolio to match target allocation.
    
    Sells over-allocated coins and buys under-allocated coins.
    """
    cfg = db.get_user_config(user_id)
    spot_settings = cfg.get("spot_settings", {})
    
    portfolio = spot_settings.get("portfolio", "custom")
    if portfolio == "custom":
        allocation = spot_settings.get("allocation", {})
    else:
        portfolio_info = SPOT_PORTFOLIOS.get(portfolio, {})
        allocation = portfolio_info.get("coins", {})
    
    if not allocation:
        return {"success": False, "error": "No target allocation defined"}
    
    # Get current holdings
    balances = await fetch_spot_balance(user_id, account_type=account_type)
    
    # Calculate current portfolio value
    total_value = 0.0
    coin_values = {}
    
    for coin in allocation.keys():
        qty = balances.get(coin, 0)
        if qty > 0:
            symbol = f"{coin}USDT"
            ticker = await get_spot_ticker(user_id, symbol, account_type)
            if ticker:
                price = float(ticker.get("lastPrice", 0))
                value = qty * price
                coin_values[coin] = value
                total_value += value
    
    # Add USDT as available cash
    usdt_balance = balances.get("USDT", 0)
    total_portfolio = total_value + usdt_balance
    
    if total_portfolio < 10:  # Minimum $10 to rebalance
        return {"success": False, "error": "Portfolio too small to rebalance"}
    
    # Calculate target values and differences
    trades = {"buy": [], "sell": []}
    
    for coin, target_pct in allocation.items():
        target_value = total_portfolio * (target_pct / 100.0)
        current_value = coin_values.get(coin, 0)
        diff = target_value - current_value
        
        # Only rebalance if difference is more than 5% of target
        if abs(diff) < target_value * 0.05:
            continue
        
        if diff > 5:  # Need to buy at least $5
            trades["buy"].append({"coin": coin, "usdt": diff})
        elif diff < -5:  # Need to sell at least $5 worth
            trades["sell"].append({"coin": coin, "usdt": abs(diff)})
    
    results = {"sells": [], "buys": [], "total_rebalanced": 0.0}
    
    # Execute sells first to free up USDT
    for trade in trades["sell"]:
        coin = trade["coin"]
        usdt_to_sell = trade["usdt"]
        
        symbol = f"{coin}USDT"
        ticker = await get_spot_ticker(user_id, symbol, account_type)
        if not ticker:
            continue
        
        price = float(ticker.get("lastPrice", 0))
        qty_to_sell = usdt_to_sell / price if price > 0 else 0
        
        result = await execute_spot_sell(user_id, coin, qty=qty_to_sell, account_type=account_type)
        if result.get("success"):
            results["sells"].append(f"Sold {qty_to_sell:.6f} {coin}")
            results["total_rebalanced"] += result.get("usdt_received", 0)
    
    # Execute buys
    for trade in trades["buy"]:
        coin = trade["coin"]
        usdt_to_buy = trade["usdt"]
        
        result = await execute_spot_dca_buy(user_id, coin, usdt_to_buy, account_type=account_type)
        if result.get("success"):
            results["buys"].append(f"Bought {result.get('qty', 0):.6f} {coin}")
            results["total_rebalanced"] += result.get("usdt_spent", 0)
    
    results["success"] = True
    return results


# ==================== SPOT TRAILING TP ====================

async def check_spot_trailing_tp(
    user_id: int,
    account_type: str = None,
) -> list:
    """
    Check spot holdings for trailing TP triggers.
    
    Logic:
    1. If price reaches activation_pct above avg_price -> activate trailing
    2. Track peak price after activation
    3. If price drops trail_pct from peak -> sell
    
    Returns list of executed sells.
    """
    cfg = db.get_user_config(user_id)
    spot_settings = cfg.get("spot_settings", {})
    
    trailing_config = spot_settings.get("trailing_tp", SPOT_TRAILING_TP_DEFAULTS)
    if not trailing_config.get("enabled"):
        return []
    
    activation_pct = trailing_config.get("activation_pct", 15.0)
    trail_pct = trailing_config.get("trail_pct", 5.0)
    
    purchase_history = spot_settings.get("purchase_history", {})
    trailing_state = spot_settings.get("trailing_state", {})  # {coin: {active, peak_price}}
    
    executed_sells = []
    state_changed = False
    
    balances = await fetch_spot_balance(user_id, account_type=account_type)
    
    for coin, coin_history in purchase_history.items():
        avg_price = coin_history.get("avg_price", 0)
        total_qty = coin_history.get("total_qty", 0)
        
        if avg_price <= 0 or total_qty <= 0:
            continue
        
        # Check actual balance
        actual_qty = balances.get(coin, 0)
        if actual_qty < 0.00001:
            continue
        
        symbol = f"{coin}USDT"
        
        try:
            ticker = await get_spot_ticker(user_id, symbol, account_type)
            if not ticker:
                continue
            
            current_price = float(ticker.get("lastPrice", 0))
            if current_price <= 0:
                continue
            
            gain_pct = ((current_price - avg_price) / avg_price) * 100
            coin_state = trailing_state.get(coin, {"active": False, "peak_price": 0})
            
            if not coin_state.get("active"):
                # Check if we should activate trailing
                if gain_pct >= activation_pct:
                    coin_state["active"] = True
                    coin_state["peak_price"] = current_price
                    coin_state["activation_gain"] = gain_pct
                    trailing_state[coin] = coin_state
                    state_changed = True
                    logger.info(f"[SPOT-TRAIL] {coin} trailing activated at +{gain_pct:.1f}%, peak=${current_price:.4f}")
            else:
                # Trailing is active - update peak and check for trigger
                peak = coin_state.get("peak_price", current_price)
                
                if current_price > peak:
                    # New peak
                    coin_state["peak_price"] = current_price
                    trailing_state[coin] = coin_state
                    state_changed = True
                    logger.debug(f"[SPOT-TRAIL] {coin} new peak: ${current_price:.4f}")
                else:
                    # Check if dropped enough from peak to trigger
                    drop_from_peak = ((peak - current_price) / peak) * 100
                    
                    if drop_from_peak >= trail_pct:
                        # TRIGGER! Sell all
                        logger.info(f"[SPOT-TRAIL] {coin} TRIGGER! Peak=${peak:.4f}, now=${current_price:.4f}, drop={drop_from_peak:.1f}%")
                        
                        result = await execute_spot_sell(
                            user_id=user_id,
                            coin=coin,
                            qty=actual_qty,
                            account_type=account_type,
                        )
                        
                        if result.get("success"):
                            usdt_received = result.get("usdt_received", actual_qty * current_price)
                            final_gain = ((current_price - avg_price) / avg_price) * 100
                            
                            executed_sells.append({
                                "coin": coin,
                                "qty_sold": actual_qty,
                                "usdt_received": usdt_received,
                                "gain_pct": final_gain,
                                "peak_price": peak,
                                "sell_price": current_price,
                            })
                            
                            # Reset state for this coin
                            coin_state["active"] = False
                            coin_state["peak_price"] = 0
                            trailing_state[coin] = coin_state
                            state_changed = True
                        else:
                            logger.error(f"Trailing TP sell failed for {coin}: {result.get('error')}")
                            
        except Exception as e:
            logger.error(f"check_spot_trailing_tp error for {coin}: {e}")
    
    # Save state
    if state_changed:
        spot_settings["trailing_state"] = trailing_state
        db.set_user_field(user_id, "spot_settings", json.dumps(spot_settings))
    
    return executed_sells


# ==================== SPOT LIMIT ORDERS ====================

async def place_spot_limit_order(
    user_id: int,
    coin: str,
    side: str,  # "Buy" or "Sell"
    price: float,
    usdt_amount: float = None,  # For Buy
    qty: float = None,          # For Sell
    account_type: str = None,
) -> dict:
    """
    Place a limit order for spot.
    
    For Buy: specify usdt_amount, qty will be calculated
    For Sell: specify qty directly
    """
    symbol = f"{coin}USDT"
    
    if side == "Buy":
        if not usdt_amount or usdt_amount <= 0:
            return {"success": False, "error": "Invalid USDT amount"}
        order_qty = usdt_amount / price
    else:
        if not qty or qty <= 0:
            return {"success": False, "error": "Invalid quantity"}
        order_qty = qty
    
    try:
        result = await place_spot_order(
            user_id=user_id,
            symbol=symbol,
            side=side,
            qty=order_qty,
            order_type="Limit",
            price=price,
            account_type=account_type,
        )
        
        # Save pending limit order to track
        cfg = db.get_user_config(user_id)
        spot_settings = cfg.get("spot_settings", {})
        pending_orders = spot_settings.get("pending_limit_orders", [])
        
        order_id = result.get("orderId") or result.get("order_id")
        pending_orders.append({
            "order_id": order_id,
            "symbol": symbol,
            "coin": coin,
            "side": side,
            "price": price,
            "qty": order_qty,
            "usdt": usdt_amount if side == "Buy" else order_qty * price,
            "created_ts": int(time.time()),
        })
        
        # Keep last 50 orders
        if len(pending_orders) > 50:
            pending_orders = pending_orders[-50:]
        
        spot_settings["pending_limit_orders"] = pending_orders
        db.set_user_field(user_id, "spot_settings", json.dumps(spot_settings))
        
        return {
            "success": True,
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "price": price,
            "qty": order_qty,
        }
        
    except Exception as e:
        logger.error(f"place_spot_limit_order error: {e}")
        return {"success": False, "error": str(e)}


async def get_spot_open_orders(user_id: int, account_type: str = None) -> list:
    """Get all open spot orders."""
    try:
        params = {"category": "spot"}
        res = await _bybit_request(user_id, "GET", "/v5/order/realtime", params=params, account_type=account_type)
        orders = res.get("list", [])
        return orders
    except Exception as e:
        logger.error(f"get_spot_open_orders error: {e}")
        return []


async def cancel_spot_order(user_id: int, symbol: str, order_id: str, account_type: str = None) -> dict:
    """Cancel a spot order."""
    try:
        params = {
            "category": "spot",
            "symbol": symbol,
            "orderId": order_id,
        }
        res = await _bybit_request(user_id, "POST", "/v5/order/cancel", params=params, account_type=account_type)
        return {"success": True, "result": res}
    except Exception as e:
        logger.error(f"cancel_spot_order error: {e}")
        return {"success": False, "error": str(e)}


# ==================== SPOT GRID BOT ====================

async def setup_spot_grid(
    user_id: int,
    coin: str,
    price_low: float,
    price_high: float,
    grid_count: int,
    total_investment: float,
    account_type: str = None,
) -> dict:
    """
    Setup a grid bot for spot trading.
    
    Creates limit buy orders at regular intervals from price_low to current price,
    and prepares sell levels above current price.
    """
    symbol = f"{coin}USDT"
    
    try:
        # Get current price
        ticker = await get_spot_ticker(user_id, symbol, account_type)
        if not ticker:
            return {"success": False, "error": f"Could not get price for {symbol}"}
        
        current_price = float(ticker.get("lastPrice", 0))
        if current_price <= 0:
            return {"success": False, "error": "Invalid current price"}
        
        if price_low >= price_high:
            return {"success": False, "error": "Price low must be less than price high"}
        
        if current_price < price_low or current_price > price_high:
            return {"success": False, "error": f"Current price ${current_price:.2f} must be within grid range ${price_low:.2f} - ${price_high:.2f}"}
        
        # Calculate grid step
        grid_step = (price_high - price_low) / grid_count
        usdt_per_grid = total_investment / grid_count
        
        # Generate grid levels
        grid_levels = []
        for i in range(grid_count + 1):
            level_price = price_low + (i * grid_step)
            grid_levels.append({
                "price": level_price,
                "side": "Buy" if level_price < current_price else "Sell",
                "usdt": usdt_per_grid,
                "qty": usdt_per_grid / level_price,
                "filled": False,
                "order_id": None,
            })
        
        # Place buy orders below current price
        placed_orders = []
        for level in grid_levels:
            if level["side"] == "Buy" and level["price"] < current_price * 0.99:  # 1% buffer
                result = await place_spot_limit_order(
                    user_id=user_id,
                    coin=coin,
                    side="Buy",
                    price=level["price"],
                    usdt_amount=level["usdt"],
                    account_type=account_type,
                )
                
                if result.get("success"):
                    level["order_id"] = result.get("order_id")
                    placed_orders.append(level["price"])
        
        # Save grid config
        cfg = db.get_user_config(user_id)
        spot_settings = cfg.get("spot_settings", {})
        
        grids = spot_settings.get("grids", {})
        grids[coin] = {
            "price_low": price_low,
            "price_high": price_high,
            "grid_count": grid_count,
            "grid_step": grid_step,
            "total_investment": total_investment,
            "usdt_per_grid": usdt_per_grid,
            "levels": grid_levels,
            "created_ts": int(time.time()),
            "active": True,
            "realized_profit": 0.0,
            "trades_count": 0,
        }
        
        spot_settings["grids"] = grids
        db.set_user_field(user_id, "spot_settings", json.dumps(spot_settings))
        
        return {
            "success": True,
            "coin": coin,
            "price_low": price_low,
            "price_high": price_high,
            "grid_count": grid_count,
            "grid_step": grid_step,
            "orders_placed": len(placed_orders),
            "placed_at": placed_orders,
        }
        
    except Exception as e:
        logger.error(f"setup_spot_grid error: {e}")
        return {"success": False, "error": str(e)}


async def check_spot_grids(user_id: int, account_type: str = None) -> list:
    """
    Check and manage active spot grids.
    
    When a buy order fills -> place sell order at next level up
    When a sell order fills -> place buy order at the same level
    """
    cfg = db.get_user_config(user_id)
    spot_settings = cfg.get("spot_settings", {})
    grids = spot_settings.get("grids", {})
    
    if not grids:
        return []
    
    events = []
    state_changed = False
    
    # Get all open orders
    open_orders = await get_spot_open_orders(user_id, account_type)
    open_order_ids = {o.get("orderId") for o in open_orders}
    
    for coin, grid_config in grids.items():
        if not grid_config.get("active"):
            continue
        
        symbol = f"{coin}USDT"
        levels = grid_config.get("levels", [])
        grid_step = grid_config.get("grid_step", 0)
        usdt_per_grid = grid_config.get("usdt_per_grid", 0)
        
        for i, level in enumerate(levels):
            order_id = level.get("order_id")
            if not order_id:
                continue
            
            # Check if order was filled (not in open orders anymore)
            if order_id not in open_order_ids and not level.get("filled"):
                level["filled"] = True
                state_changed = True
                
                if level["side"] == "Buy":
                    # Buy filled -> place sell at next level
                    sell_price = level["price"] + grid_step
                    qty = level["qty"]
                    
                    result = await place_spot_limit_order(
                        user_id=user_id,
                        coin=coin,
                        side="Sell",
                        price=sell_price,
                        qty=qty,
                        account_type=account_type,
                    )
                    
                    if result.get("success"):
                        # Create new level entry for sell
                        new_sell_level = {
                            "price": sell_price,
                            "side": "Sell",
                            "qty": qty,
                            "order_id": result.get("order_id"),
                            "filled": False,
                            "linked_buy_price": level["price"],
                        }
                        levels.append(new_sell_level)
                        
                        events.append({
                            "type": "grid_buy_filled",
                            "coin": coin,
                            "buy_price": level["price"],
                            "sell_placed": sell_price,
                            "qty": qty,
                        })
                        
                        grid_config["trades_count"] = grid_config.get("trades_count", 0) + 1
                
                elif level["side"] == "Sell":
                    # Sell filled -> place buy back at linked level, record profit
                    buy_price = level.get("linked_buy_price", level["price"] - grid_step)
                    qty = level["qty"]
                    profit = (level["price"] - buy_price) * qty
                    
                    result = await place_spot_limit_order(
                        user_id=user_id,
                        coin=coin,
                        side="Buy",
                        price=buy_price,
                        usdt_amount=qty * buy_price,
                        account_type=account_type,
                    )
                    
                    if result.get("success"):
                        # Update buy level
                        for buy_level in levels:
                            if buy_level.get("price") == buy_price and buy_level.get("side") == "Buy":
                                buy_level["filled"] = False
                                buy_level["order_id"] = result.get("order_id")
                                break
                        else:
                            # Create new buy level
                            levels.append({
                                "price": buy_price,
                                "side": "Buy",
                                "usdt": qty * buy_price,
                                "qty": qty,
                                "order_id": result.get("order_id"),
                                "filled": False,
                            })
                        
                        grid_config["realized_profit"] = grid_config.get("realized_profit", 0) + profit
                        grid_config["trades_count"] = grid_config.get("trades_count", 0) + 1
                        
                        events.append({
                            "type": "grid_sell_filled",
                            "coin": coin,
                            "sell_price": level["price"],
                            "profit": profit,
                            "total_profit": grid_config["realized_profit"],
                        })
        
        grid_config["levels"] = levels
    
    # Save state
    if state_changed:
        spot_settings["grids"] = grids
        db.set_user_field(user_id, "spot_settings", json.dumps(spot_settings))
    
    return events


async def stop_spot_grid(user_id: int, coin: str, account_type: str = None) -> dict:
    """Stop a grid bot and cancel all its orders."""
    cfg = db.get_user_config(user_id)
    spot_settings = cfg.get("spot_settings", {})
    grids = spot_settings.get("grids", {})
    
    if coin not in grids:
        return {"success": False, "error": f"No grid found for {coin}"}
    
    grid_config = grids[coin]
    symbol = f"{coin}USDT"
    
    # Cancel all open orders
    cancelled = 0
    for level in grid_config.get("levels", []):
        order_id = level.get("order_id")
        if order_id and not level.get("filled"):
            result = await cancel_spot_order(user_id, symbol, order_id, account_type)
            if result.get("success"):
                cancelled += 1
    
    # Mark grid as inactive
    grid_config["active"] = False
    grid_config["stopped_ts"] = int(time.time())
    grids[coin] = grid_config
    
    spot_settings["grids"] = grids
    db.set_user_field(user_id, "spot_settings", json.dumps(spot_settings))
    
    return {
        "success": True,
        "coin": coin,
        "orders_cancelled": cancelled,
        "total_profit": grid_config.get("realized_profit", 0),
        "total_trades": grid_config.get("trades_count", 0),
    }


# ==================== SPOT PORTFOLIO STATS ====================

async def get_spot_portfolio_stats(user_id: int, account_type: str = None) -> dict:
    """
    Get comprehensive spot portfolio statistics.
    
    Returns:
    - Total value
    - Profit/loss per coin
    - Overall P&L
    - Comparison with HODL BTC
    """
    cfg = db.get_user_config(user_id)
    spot_settings = cfg.get("spot_settings", {})
    purchase_history = spot_settings.get("purchase_history", {})
    total_invested = spot_settings.get("total_invested", 0)
    
    # Get current balances and prices
    balances = await fetch_spot_balance(user_id, account_type=account_type)
    
    coins_stats = []
    total_current_value = 0
    total_cost_basis = 0
    
    for coin, history in purchase_history.items():
        avg_price = history.get("avg_price", 0)
        total_qty = history.get("total_qty", 0)
        total_cost = history.get("total_cost", 0)
        
        if avg_price <= 0:
            continue
        
        # Get actual balance (may differ if user traded outside bot)
        actual_qty = balances.get(coin, 0)
        
        symbol = f"{coin}USDT"
        try:
            ticker = await get_spot_ticker(user_id, symbol, account_type)
            if not ticker:
                continue
            
            current_price = float(ticker.get("lastPrice", 0))
            change_24h = float(ticker.get("price24hPcnt", 0)) * 100
            
            current_value = actual_qty * current_price
            
            # Calculate P&L based on tracked history
            pnl_value = current_value - total_cost if actual_qty > 0 else 0
            pnl_pct = ((current_price - avg_price) / avg_price) * 100 if avg_price > 0 else 0
            
            coins_stats.append({
                "coin": coin,
                "qty": actual_qty,
                "avg_price": avg_price,
                "current_price": current_price,
                "current_value": current_value,
                "cost_basis": total_cost,
                "pnl_value": pnl_value,
                "pnl_pct": pnl_pct,
                "change_24h": change_24h,
            })
            
            total_current_value += current_value
            total_cost_basis += total_cost
            
        except Exception as e:
            logger.error(f"get_spot_portfolio_stats error for {coin}: {e}")
    
    # Add USDT balance
    usdt_balance = balances.get("USDT", 0)
    total_current_value += usdt_balance
    
    # Calculate overall P&L
    overall_pnl_value = total_current_value - total_cost_basis
    overall_pnl_pct = ((total_current_value - total_cost_basis) / total_cost_basis * 100) if total_cost_basis > 0 else 0
    
    # Compare with HODL BTC
    btc_comparison = None
    if total_invested > 0:
        try:
            btc_ticker = await get_spot_ticker(user_id, "BTCUSDT", account_type)
            if btc_ticker:
                btc_price = float(btc_ticker.get("lastPrice", 0))
                # Get historical price when user started (approximation using first purchase)
                first_purchase_ts = None
                for history in purchase_history.values():
                    purchases = history.get("purchases", [])
                    if purchases:
                        ts = purchases[0].get("ts", 0)
                        if first_purchase_ts is None or ts < first_purchase_ts:
                            first_purchase_ts = ts
                
                # If we had just held BTC instead
                # Simplified: assume we could have bought at avg of all our buy times
                # For now, just show what total invested would be worth in BTC at current price
                btc_qty_if_hodl = total_invested / btc_price if btc_price > 0 else 0
                # This is simplified - real comparison would need historical prices
                btc_comparison = {
                    "total_invested": total_invested,
                    "btc_price_now": btc_price,
                    "btc_qty_if_hodl": btc_qty_if_hodl,
                }
        except Exception as e:
            logger.error(f"BTC comparison error: {e}")
    
    # Sort by value descending
    coins_stats.sort(key=lambda x: x["current_value"], reverse=True)
    
    return {
        "coins": coins_stats,
        "total_current_value": total_current_value,
        "total_cost_basis": total_cost_basis,
        "usdt_balance": usdt_balance,
        "overall_pnl_value": overall_pnl_value,
        "overall_pnl_pct": overall_pnl_pct,
        "total_invested": total_invested,
        "btc_comparison": btc_comparison,
    }


# ==================== MULTI-TIMEFRAME DCA ====================

async def execute_dca_plan(
    user_id: int,
    plan: dict,
    account_type: str = None,
) -> dict:
    """Execute a single DCA plan."""
    coins = plan.get("coins", [])
    amount = plan.get("amount", 10.0)
    strategy = plan.get("strategy", "fixed")
    plan_name = plan.get("name", "Plan")
    
    results = []
    total_spent = 0.0
    skipped = []
    
    cfg = db.get_user_config(user_id)
    spot_settings = cfg.get("spot_settings", {})
    
    for coin in coins:
        # Calculate amount per coin
        coin_amount = amount / len(coins) if coins else amount
        
        # Apply strategy
        adjusted_amount = await calculate_smart_dca_amount(
            base_amount=coin_amount,
            strategy=strategy,
            coin=coin,
            spot_settings=spot_settings,
            user_id=user_id,
            account_type=account_type,
        )
        
        if adjusted_amount <= 0:
            skipped.append(coin)
            continue
        
        result = await execute_spot_dca_buy(user_id, coin, adjusted_amount, account_type=account_type)
        if result.get("success"):
            spent = result.get("usdt_spent", adjusted_amount)
            results.append({
                "coin": coin,
                "qty": result.get("qty", 0),
                "spent": spent,
                "price": result.get("price", 0),
            })
            total_spent += spent
        elif result.get("error") == "SKIP":
            skipped.append(coin)
    
    return {
        "success": True,
        "plan_name": plan_name,
        "results": results,
        "total_spent": total_spent,
        "skipped": skipped,
    }


def _normalize_order_id(res: dict) -> str:
    return str(res.get("orderId") or res.get("id") or res.get("order_id") or "")


@log_calls
async def fetch_open_positions(user_id, *args, **kwargs) -> list:
    """
    Fetch open positions using unified architecture when available
    Falls back to direct Bybit API if unified is disabled
    """
    # Use unified architecture if available
    if USE_UNIFIED_ARCHITECTURE and UNIFIED_AVAILABLE:
        try:
            uid = None
            if isinstance(user_id, int):
                uid = user_id
            else:
                update = user_id
                uid = getattr(getattr(update, "effective_user", None), "id", None)
            
            if uid is None:
                uid = kwargs.get("user_id")
            
            if uid is None:
                raise RuntimeError("fetch_open_positions: не удалось определить user_id")
            
            # Get exchange and account type from user settings
            exchange_type = db.get_exchange_type(uid) or 'bybit'
            account_type = kwargs.get('account_type')
            if account_type is None:
                trading_mode = db.get_trading_mode(uid)
                account_type = 'real' if trading_mode == 'real' else 'demo'
            
            # Get unified Position objects
            positions = await get_positions_unified(
                uid, 
                exchange=exchange_type, 
                account_type=account_type
            )
            
            # Get active positions from DB to enrich with stored TP/SL
            db_positions = db.get_active_positions(uid, account_type=account_type)
            db_by_symbol = {p['symbol']: p for p in db_positions}
            
            # Convert to dicts for backward compatibility
            result = []
            for pos in positions:
                pos_dict = pos.to_dict()
                symbol = pos_dict.get('symbol', '')
                
                # Map unified fields to Bybit format for compatibility
                pos_dict['avgPrice'] = pos_dict['entry_price']
                pos_dict['markPrice'] = pos_dict['mark_price']
                pos_dict['unrealisedPnl'] = pos_dict['unrealized_pnl']
                pos_dict['positionIM'] = pos_dict['margin_used']
                pos_dict['liqPrice'] = pos_dict.get('liquidation_price')
                
                # Map TP/SL to Bybit format
                pos_dict['takeProfit'] = pos_dict.get('take_profit')
                pos_dict['stopLoss'] = pos_dict.get('stop_loss')
                
                # If exchange didn't return TP/SL, try to get from DB
                db_pos = db_by_symbol.get(symbol)
                if db_pos:
                    if not pos_dict.get('takeProfit') and db_pos.get('tp_price'):
                        pos_dict['takeProfit'] = db_pos['tp_price']
                    if not pos_dict.get('stopLoss') and db_pos.get('sl_price'):
                        pos_dict['stopLoss'] = db_pos['sl_price']
                    # Copy ALL DB metadata for detailed view
                    pos_dict['strategy'] = db_pos.get('strategy')
                    pos_dict['source'] = db_pos.get('source')
                    pos_dict['opened_by'] = db_pos.get('opened_by')
                    pos_dict['open_ts'] = db_pos.get('open_ts')
                    pos_dict['account_type'] = db_pos.get('account_type', account_type)
                    pos_dict['exchange'] = db_pos.get('exchange', exchange_type)
                    pos_dict['use_atr'] = db_pos.get('use_atr', False)
                    pos_dict['atr_activated'] = db_pos.get('atr_activated', False)
                    pos_dict['timeframe'] = db_pos.get('timeframe')
                else:
                    # Position not in DB - set defaults
                    pos_dict['account_type'] = account_type
                    pos_dict['exchange'] = exchange_type
                
                result.append(pos_dict)
            
            # Only log if positions changed or every 5 minutes
            if not hasattr(fetch_open_positions, '_last_count') or \
               fetch_open_positions._last_count != len(result) or \
               not hasattr(fetch_open_positions, '_last_log_time') or \
               (asyncio.get_event_loop().time() - fetch_open_positions._last_log_time) > 300:
                logger.info(f"✅ Fetched {len(result)} positions via unified architecture")
                fetch_open_positions._last_count = len(result)
                fetch_open_positions._last_log_time = asyncio.get_event_loop().time()
            
            return result
            
        except Exception as e:
            logger.error(f"Unified fetch_open_positions error: {e}", exc_info=True)
            # Fall through to old code
    
    # OLD CODE (fallback) - with pagination
    try:
        uid = None
        if isinstance(user_id, int):
            uid = user_id
        else:
            # предполагаем что это update
            update = user_id
            uid = getattr(getattr(update, "effective_user", None), "id", None)

        if uid is None:
            uid = kwargs.get("user_id")

        if uid is None:
            raise RuntimeError("fetch_open_positions: не удалось определить user_id")

        all_positions = []
        cursor = None
        
        while True:
            params = {"category": "linear", "settleCoin": "USDT", "limit": 200}
            if cursor:
                params["cursor"] = cursor
            
            res = await _bybit_request(
                uid, "GET", "/v5/position/list",
                params=params
            )
            
            positions = [p for p in (res.get("list") or []) if float(p.get("size") or 0) != 0.0]
            all_positions.extend(positions)
            
            cursor = res.get("nextPageCursor")
            if not cursor:
                break
        
        # Enrich with data from DB (TP/SL, strategy, etc.)
        account_type = kwargs.get('account_type')
        if not account_type:
            trading_mode = db.get_trading_mode(uid)
            account_type = 'real' if trading_mode == 'real' else 'demo'
        
        db_positions = db.get_active_positions(uid, account_type=account_type)
        db_by_symbol = {p['symbol']: p for p in db_positions}
        
        for pos in all_positions:
            symbol = pos.get('symbol', '')
            db_pos = db_by_symbol.get(symbol)
            if db_pos:
                # If exchange didn't return TP/SL, get from DB
                if not pos.get('takeProfit') and db_pos.get('tp_price'):
                    pos['takeProfit'] = str(db_pos['tp_price'])
                if not pos.get('stopLoss') and db_pos.get('sl_price'):
                    pos['stopLoss'] = str(db_pos['sl_price'])
                # Copy ALL DB metadata for detailed view
                pos['strategy'] = db_pos.get('strategy')
                pos['source'] = db_pos.get('source')
                pos['opened_by'] = db_pos.get('opened_by')
                pos['open_ts'] = db_pos.get('open_ts')
                pos['account_type'] = db_pos.get('account_type', account_type)
                pos['exchange'] = db_pos.get('exchange', 'bybit')
                pos['use_atr'] = db_pos.get('use_atr', False)
                pos['atr_activated'] = db_pos.get('atr_activated', False)
                pos['timeframe'] = db_pos.get('timeframe')
        
        return all_positions
    except MissingAPICredentials:
        return []

@log_calls
async def fetch_open_orders(user_id: int, symbol: str | None = None, account_type: str | None = None) -> list:
    """Fetch open orders with optional account_type override."""
    params = {"category": "linear", "settleCoin": "USDT"}
    if symbol:
        params["symbol"] = symbol
    try:
        res = await _bybit_request(user_id, "GET", "/v5/order/realtime", params=params, account_type=account_type)
    except MissingAPICredentials:
        return []
    ALIVE = {"Created", "New", "PendingNew", "PartiallyFilled"}
    return [o for o in (res.get("list") or []) if o.get("orderStatus") in ALIVE]

@require_access
@with_texts
@log_calls
async def cmd_openorders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show open orders with account type selection."""
    uid = update.effective_user.id
    t = ctx.t
    
    # Get user's trading mode to show available options
    trading_mode = get_trading_mode(uid)
    
    # If user has only one mode configured, show orders directly
    if trading_mode in ('demo', 'real'):
        await show_orders_for_account(update, ctx, trading_mode)
        return
    
    # If both modes, show selection
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎮 Demo Orders", callback_data="orders:demo"),
            InlineKeyboardButton("💎 Real Orders", callback_data="orders:real")
        ],
        [InlineKeyboardButton("🔙 " + t.get('back', 'Back'), callback_data="menu:main")]
    ])
    
    await update.message.reply_text(
        t.get('select_account_orders', '📝 *Select Account Type*\n\nChoose which account orders to view:'),
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


async def show_orders_for_account(update: Update, ctx: ContextTypes.DEFAULT_TYPE, account_type: str):
    """Show orders for specific account type."""
    uid = update.effective_user.id if hasattr(update, 'effective_user') else update.callback_query.from_user.id
    t = ctx.t
    trading_mode = get_trading_mode(uid)
    
    try:
        ords = await fetch_open_orders(uid, account_type=account_type)
        
        mode_emoji = "🎮" if account_type == "demo" else "💎"
        mode_label = "Demo" if account_type == "demo" else "Real"
        header = f"{mode_emoji} *{mode_label} Open Orders*\n\n"
        
        if not ords:
            text = header + t.get('no_open_orders', 'No open orders')
            
            # Only show mode switch buttons if user has both modes
            if trading_mode == 'both':
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("🎮 Demo", callback_data="orders:demo"),
                        InlineKeyboardButton("💎 Real", callback_data="orders:real")
                    ],
                    [InlineKeyboardButton("🔙 " + t.get('back', 'Back'), callback_data="menu:main")]
                ])
            else:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 " + t.get('back', 'Back'), callback_data="menu:main")]
                ])
            
            if hasattr(update, 'message'):
                await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
            else:
                await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
            return

        lines = [header + t.get('open_orders_header', '📝 Open Orders:'), ""]
        for i, o in enumerate(ords, start=1):
            price = o.get('price')
            price_str = str(price) if price not in (None, "", 0, "0") else "—"
            qty_str = str(o.get('qty', "—"))
            symbol = o.get('symbol', "—")
            side   = o.get('side', "—")
            oid    = o.get('orderId', "—")

            lines.append(
                t.get('open_orders_item', '#{idx} {symbol} {side}\n  Qty: {qty} @ {price}\n  ID: {id}').format(
                    idx=i,
                    symbol=symbol,
                    side=side,
                    qty=qty_str,
                    price=price_str,
                    id=oid
                )
            )
            lines.append("")

        text = "\n".join(lines)
        
        # Only show mode switch buttons if user has both modes
        if trading_mode == 'both':
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🎮 Demo", callback_data="orders:demo"),
                    InlineKeyboardButton("💎 Real", callback_data="orders:real")
                ],
                [InlineKeyboardButton("🔙 " + t.get('back', 'Back'), callback_data="menu:main")]
            ])
        else:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 " + t.get('back', 'Back'), callback_data="menu:main")]
            ])

        # Send message or edit existing
        if hasattr(update, 'message') and update.message:
            MAX_LEN = 3500
            for pos in range(0, len(text), MAX_LEN):
                chunk = text[pos:pos+MAX_LEN]
                await update.message.reply_text(
                    chunk, 
                    parse_mode="Markdown",
                    reply_markup=keyboard if pos + MAX_LEN >= len(text) else None
                )
        else:
            # Callback query - edit message
            if len(text) > 3500:
                text = text[:3450] + "\n...(truncated)"
            await update.callback_query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )

    except Exception as e:
        logger.error(f"Error in show_orders_for_account: {e}", exc_info=True)
        error_text = t.get('open_orders_error', 'Error fetching orders: {error}').format(error=e)
        
        if hasattr(update, 'message'):
            await update.message.reply_text(error_text)
        else:
            await update.callback_query.edit_message_text(error_text)


@log_calls
async def handle_orders_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle orders account selection callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if not data.startswith("orders:"):
        return
    
    account_type = data.split(":")[1]  # "demo" or "real"
    await show_orders_for_account(update, ctx, account_type)

@require_access
@with_texts
@log_calls
async def cmd_select_coins(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['mode'] = 'select_coins'
    await update.message.reply_text(
        ctx.t['enter_coins'],
        parse_mode='Markdown'
    )

@require_access
@with_texts
@log_calls
async def cmd_positions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show positions with account type selection."""
    uid = update.effective_user.id
    t = ctx.t
    
    # Get user's trading mode to show available options
    trading_mode = get_trading_mode(uid)
    
    # If user has only one mode configured, show positions directly
    if trading_mode in ('demo', 'real'):
        await show_positions_for_account(update, ctx, trading_mode)
        return
    
    # If both modes, show selection
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎮 Demo Positions", callback_data="positions:demo"),
            InlineKeyboardButton("💎 Real Positions", callback_data="positions:real")
        ],
        [InlineKeyboardButton("🔙 " + t.get('back', 'Back'), callback_data="menu:main")]
    ])
    
    await update.message.reply_text(
        t.get('select_account_type', '📊 *Select Account Type*\n\nChoose which account positions to view:'),
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


async def show_positions_for_account(update: Update, ctx: ContextTypes.DEFAULT_TYPE, account_type: str):
    """Show positions for specific account type."""
    uid = update.effective_user.id if hasattr(update, 'effective_user') else update.callback_query.from_user.id
    t = ctx.t
    trading_mode = get_trading_mode(uid)
    
    pos_list = await fetch_open_positions(uid, account_type=account_type)
    
    mode_emoji = "🎮" if account_type == "demo" else "💎"
    mode_label = "Demo" if account_type == "demo" else "Real"
    header = f"{mode_emoji} *{mode_label} Positions*\n\n"
    
    if not pos_list:
        text = header + t.get('no_positions', 'No open positions')
        
        # Only show mode switch buttons if user has both modes
        if trading_mode == 'both':
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🎮 Demo", callback_data="positions:demo"),
                    InlineKeyboardButton("💎 Real", callback_data="positions:real")
                ],
                [InlineKeyboardButton("🔙 " + t.get('back', 'Back'), callback_data="menu:main")]
            ])
        else:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 " + t.get('back', 'Back'), callback_data="menu:main")]
            ])
        
        if hasattr(update, 'message'):
            return await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
        else:
            return await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")

    total_pnl = 0.0
    total_im  = 0.0
    lines = [header + t.get('positions_header', '📊 Open Positions:')]

    for idx, p in enumerate(pos_list, start=1):
        sym   = p.get("symbol",    "-")
        side  = p.get("side",      "-")
        lev   = p.get("leverage",  "-")

        size   = human_format(float(p.get("size", 0)))
        avg    = float(p.get("avgPrice")    or 0)
        mark   = float(p.get("markPrice")   or 0)
        im     = float(p.get("positionIM")  or 0)
        mm     = float(p.get("positionMM")  or 0)
        pm     = float(p.get("positionBalance") or 0)
        pnl_i  = float(p.get("unrealisedPnl") or 0)

        def to_float(key):
            raw = p.get(key)
            return float(raw) if raw not in (None, "", "0") else None

        liq = to_float("liqPrice")
        tp  = to_float("takeProfit")
        sl  = to_float("stopLoss")

        pct = (pnl_i / im * 100) if im else 0.0
        total_pnl += pnl_i
        total_im  += im

        lines.append(
            t.get('position_item', '#{idx} {symbol} {side}x{leverage}\n  Size: {size}\n  Entry: {avg:.6f} → Mark: {mark:.6f}\n  Liq: {liq} | IM: {im:.2f} | MM: {mm:.2f}\n  TP: {tp} | SL: {sl}\n  PnL: {pnl:+.2f} ({pct:+.2f}%)').format(
                idx=idx,
                symbol=sym,
                side=side,
                leverage=lev,
                size=size,
                avg=avg,
                mark=mark,
                liq=(f"{liq:.8f}" if liq is not None else "–"),
                im=im,
                mm=mm,
                pm=pm,
                tp=(f"{tp:.8f}" if tp is not None else "–"),
                sl=(f"{sl:.8f}" if sl is not None else "–"),
                pnl=pnl_i,
                pct=pct
            )
        )

    if total_im:
        overall = total_pnl / total_im * 100
        lines.append(
            "\n" + t.get('positions_overall', '💰 *Total PnL:* {pnl:+.2f} USDT ({pct:+.2f}%)').format(
                pnl=total_pnl,
                pct=overall
            )
        )

    text = "\n".join(lines)
    
    # Only show mode switch buttons if user has both modes
    if trading_mode == 'both':
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎮 Demo", callback_data="positions:demo"),
                InlineKeyboardButton("💎 Real", callback_data="positions:real")
            ],
            [InlineKeyboardButton("🔙 " + t.get('back', 'Back'), callback_data="menu:main")]
        ])
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 " + t.get('back', 'Back'), callback_data="menu:main")]
        ])

    # Send message or edit existing
    if hasattr(update, 'message') and update.message:
        escaped = html.escape(text)
        max_len = 3000
        for i in range(0, len(escaped), max_len):
            chunk = escaped[i : i + max_len]
            await ctx.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"<pre>{chunk}</pre>",
                parse_mode="HTML",
                reply_markup=keyboard if i + max_len >= len(escaped) else None,
                disable_web_page_preview=True
            )
    else:
        # Callback query - edit message
        escaped = html.escape(text)
        if len(escaped) > 3000:
            escaped = escaped[:2950] + "\n...(truncated)"
        await update.callback_query.edit_message_text(
            f"<pre>{escaped}</pre>",
            parse_mode="HTML",
            reply_markup=keyboard,
            disable_web_page_preview=True
        )


@log_calls
async def handle_positions_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle positions account selection callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if not data.startswith("positions:"):
        return
    
    account_type = data.split(":")[1]  # "demo" or "real"
    await show_positions_for_account(update, ctx, account_type)


# ------------------------------------------------------------------------------------
# Open Positions Management (detailed view with pagination and close buttons)
# ------------------------------------------------------------------------------------

POSITIONS_PER_PAGE = 10  # Show 10 positions per page

def get_positions_list_keyboard(positions: list, page: int, t: dict) -> InlineKeyboardMarkup:
    """Build inline keyboard for paginated positions list (10 per page)."""
    buttons = []
    total = len(positions)
    total_pages = (total + POSITIONS_PER_PAGE - 1) // POSITIONS_PER_PAGE
    
    if total == 0:
        return InlineKeyboardMarkup([[
            InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data="pos:back")
        ]])
    
    # Get positions for current page
    start_idx = page * POSITIONS_PER_PAGE
    end_idx = min(start_idx + POSITIONS_PER_PAGE, total)
    page_positions = positions[start_idx:end_idx]
    
    # Create button for each position on this page
    for idx, pos in enumerate(page_positions):
        global_idx = start_idx + idx + 1  # 1-based index
        sym = pos.get("symbol", "-")
        side = pos.get("side", "-")
        pnl = float(pos.get("unrealisedPnl") or 0)
        
        emoji = "🟢" if side == "Buy" else "🔴"
        pnl_emoji = "📈" if pnl >= 0 else "📉"
        
        # Row: position button + close button
        buttons.append([
            InlineKeyboardButton(
                f"{emoji} {global_idx}. {sym} {pnl_emoji}{pnl:+.2f}",
                callback_data=f"pos:view:{sym}"
            ),
            InlineKeyboardButton("❌", callback_data=f"pos:close:{sym}")
        ])
    
    # Navigation row (if multiple pages)
    if total_pages > 1:
        nav_row = []
        # Previous page
        if page > 0:
            nav_row.append(InlineKeyboardButton("◀️ Prev", callback_data=f"pos:list:{page - 1}"))
        
        # Page counter
        nav_row.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="pos:noop"))
        
        # Next page
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton("Next ▶️", callback_data=f"pos:list:{page + 1}"))
        
        buttons.append(nav_row)
    
    # Action buttons
    action_row = [InlineKeyboardButton("🔄", callback_data=f"pos:list:{page}")]
    if total > 1:
        action_row.append(
            InlineKeyboardButton(
                f"⚠️ {t.get('btn_close_all', 'Close all')} ({total})",
                callback_data="pos:close_all"
            )
        )
    buttons.append(action_row)
    
    # Back button
    buttons.append([
        InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data="pos:back")
    ])
    
    return InlineKeyboardMarkup(buttons)


def format_positions_list_header(positions: list, page: int, t: dict) -> str:
    """Format header for paginated positions list."""
    total = len(positions)
    total_pages = (total + POSITIONS_PER_PAGE - 1) // POSITIONS_PER_PAGE
    
    total_pnl = sum(float(p.get("unrealisedPnl") or 0) for p in positions)
    pnl_emoji = "📈" if total_pnl >= 0 else "📉"
    
    return (
        f"📊 *{t.get('open_positions', 'Open Positions')}* ({total})\n"
        f"{pnl_emoji} Total P/L: `{total_pnl:+.2f}` USDT\n"
        f"📄 Page {page + 1}/{total_pages}\n"
        f"_Tap position to view details_"
    )


def get_positions_paginated_keyboard(positions: list, current_idx: int, t: dict, page: int = 0) -> InlineKeyboardMarkup:
    """Build inline keyboard for single position view with pagination."""
    buttons = []
    total = len(positions)
    
    if total == 0:
        return InlineKeyboardMarkup([[
            InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data="pos:back")
        ]])
    
    pos = positions[current_idx]
    sym = pos.get("symbol", "-")
    
    # Navigation row (if more than 1 position)
    if total > 1:
        nav_row = []
        # Previous button
        if current_idx > 0:
            nav_row.append(InlineKeyboardButton("◀️", callback_data=f"pos:page:{current_idx - 1}"))
        else:
            nav_row.append(InlineKeyboardButton("◀️", callback_data=f"pos:page:{total - 1}"))  # Wrap to end
        
        # Position counter
        nav_row.append(InlineKeyboardButton(f"{current_idx + 1}/{total}", callback_data="pos:noop"))
        
        # Next button
        if current_idx < total - 1:
            nav_row.append(InlineKeyboardButton("▶️", callback_data=f"pos:page:{current_idx + 1}"))
        else:
            nav_row.append(InlineKeyboardButton("▶️", callback_data=f"pos:page:0"))  # Wrap to start
        
        buttons.append(nav_row)
    
    # Close this position button
    buttons.append([
        InlineKeyboardButton(f"❌ {t.get('btn_close_position', 'Close position')}", callback_data=f"pos:close:{sym}")
    ])
    
    # Close all positions button (if more than 1)
    if total > 1:
        buttons.append([
            InlineKeyboardButton(
                f"⚠️ {t.get('btn_close_all', 'Close all')} ({total})",
                callback_data="pos:close_all"
            )
        ])
    
    # Refresh and Back - use pos:refresh:PAGE to preserve page
    buttons.append([
        InlineKeyboardButton("🔄", callback_data=f"pos:refresh:{page}"),
        InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data=f"pos:list:{page}")
    ])
    
    return InlineKeyboardMarkup(buttons)


def format_single_position(pos: dict, idx: int, total: int, t: dict) -> str:
    """Format detailed view of a single position for paginated display."""
    sym = pos.get("symbol", "-")
    side = pos.get("side", "-")
    lev = pos.get("leverage", "-")
    size = float(pos.get("size") or 0)
    entry = float(pos.get("avgPrice") or 0)
    mark = float(pos.get("markPrice") or 0)
    pnl = float(pos.get("unrealisedPnl") or 0)
    im = float(pos.get("positionIM") or 0)
    
    def to_float(key):
        raw = pos.get(key)
        return float(raw) if raw not in (None, "", "0") else None
    
    tp = to_float("takeProfit")
    sl = to_float("stopLoss")
    liq = to_float("liqPrice")
    
    # Calculate PnL percentage
    pnl_pct = (pnl / im * 100) if im else 0.0
    
    emoji = "🟢" if side == "Buy" else "🔴"
    side_text = "LONG" if side == "Buy" else "SHORT"
    pnl_emoji = "📈" if pnl >= 0 else "📉"
    
    lines = [
        f"{emoji} *{sym}* {side_text} {lev}x",
        "",
        f"📊 Size: `{size}`",
        f"💰 Entry: `{entry:.6g}`",
        f"📍 Mark: `{mark:.6g}`",
    ]
    
    # TP info
    if tp:
        tp_pct = abs((tp - entry) / entry * 100) if entry else 0
        tp_sign = "+" if (side == "Buy" and tp > entry) or (side == "Sell" and tp < entry) else "-"
        lines.append(f"🎯 TP: `{tp:.6g}` ({tp_sign}{tp_pct:.2f}%)")
    else:
        lines.append(f"🎯 TP: –")
    
    # SL info
    if sl:
        sl_pct = abs((sl - entry) / entry * 100) if entry else 0
        lines.append(f"🛑 SL: `{sl:.6g}` (-{sl_pct:.2f}%)")
    else:
        lines.append(f"🛑 SL: –")
    
    # Liquidation
    if liq:
        lines.append(f"💀 Liq: `{liq:.6g}`")
    
    lines.append("")
    lines.append(f"{pnl_emoji} *P/L:* `{pnl:+.4f}` USDT ({pnl_pct:+.2f}%)")
    
    return "\n".join(lines)


def get_positions_keyboard(positions: list, t: dict) -> InlineKeyboardMarkup:
    """Build inline keyboard for positions management."""
    buttons = []
    for idx, p in enumerate(positions, start=1):
        sym = p.get("symbol", "-")
        side = p.get("side", "-")
        emoji = "🟢" if side == "Buy" else "🔴"
        # View details button
        buttons.append([
            InlineKeyboardButton(
                f"{emoji} {idx}. {sym}",
                callback_data=f"pos:view:{sym}"
            ),
            InlineKeyboardButton(
                f"❌ {t.get('btn_close_short', 'Close')}",
                callback_data=f"pos:close:{sym}"
            )
        ])
    
    # Close all and Back buttons
    if len(positions) > 0:
        buttons.append([
            InlineKeyboardButton(
                f"⚠️ {t.get('btn_close_all', 'Close all positions')} ({len(positions)})",
                callback_data="pos:close_all"
            )
        ])
    buttons.append([
        InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data="pos:back")
    ])
    return InlineKeyboardMarkup(buttons)


def format_position_summary(positions: list, t: dict) -> str:
    """Format positions summary for the overview message."""
    if not positions:
        return t.get('no_positions', 'No open positions')
    
    total_pnl = 0.0
    lines = [t.get('open_positions_header', '📊 *Open positions*')]
    lines.append(f"{len(positions)} {t.get('positions_count', 'positions')}\n")
    
    for idx, p in enumerate(positions, start=1):
        sym = p.get("symbol", "-")
        side = p.get("side", "-")
        entry = float(p.get("avgPrice") or 0)
        mark = float(p.get("markPrice") or 0)
        pnl = float(p.get("unrealisedPnl") or 0)
        im = float(p.get("positionIM") or 0)
        
        # Calculate PnL percentage
        pct = (pnl / im * 100) if im else 0.0
        
        total_pnl += pnl
        
        # Format line - always show in USDT
        emoji = "🟢" if side == "Buy" else "🔴"
        pnl_emoji = "📈" if pnl >= 0 else "📉"
        
        lines.append(
            f"{idx}. {emoji} *{sym}* | Entry: `{entry:.6g}`\n"
            f"   {pnl_emoji} {pct:+.2f}% ({pnl:+.4f} USDT)"
        )
    
    # Total in USDT
    lines.append(f"\n*{t.get('total_unrealized_pnl', 'Total Unrealized P/L')}:* {total_pnl:+.2f} USDT")
    
    return "\n".join(lines)


def format_position_detail(p: dict, t: dict) -> str:
    """Format detailed view of a single position."""
    import datetime
    
    sym = p.get("symbol", "-")
    side = p.get("side", "-")
    lev = p.get("leverage", "-")
    size = float(p.get("size") or 0)
    entry = float(p.get("avgPrice") or 0)
    mark = float(p.get("markPrice") or 0)
    pnl = float(p.get("unrealisedPnl") or 0)
    im = float(p.get("positionIM") or 0)
    
    # Get extended info from DB
    strategy = p.get("strategy", "Unknown")
    account_type = p.get("account_type", "demo")
    exchange = p.get("exchange", "bybit")
    open_ts = p.get("open_ts")
    use_atr = p.get("use_atr", False)
    atr_activated = p.get("atr_activated", False)
    timeframe = p.get("timeframe")
    
    def to_float(key):
        raw = p.get(key)
        return float(raw) if raw not in (None, "", "0") else None
    
    tp = to_float("takeProfit")
    sl = to_float("stopLoss")
    liq = to_float("liqPrice")
    
    # Calculate percentages
    pnl_pct = (pnl / im * 100) if im else 0.0
    tp_pct = ((tp - entry) / entry * 100) if tp and entry else None
    sl_pct = ((entry - sl) / entry * 100) if sl and entry and side == "Buy" else None
    if sl and entry and side == "Sell":
        sl_pct = ((sl - entry) / entry * 100)
    
    emoji = "🟢" if side == "Buy" else "🔴"
    side_text = "LONG" if side == "Buy" else "SHORT"
    pnl_emoji = "📈" if pnl >= 0 else "📉"
    
    # Format strategy name nicely
    strategy_names = {
        "scryptomera": "📰 Scryptomera",
        "scalper": "⚡ Scalper", 
        "elcaro": "🎯 ElCaro",
        "wyckoff": "📊 Wyckoff",
        "oi": "📈 OI Delta",
        "fibonacci": "🔢 Fibonacci",
        "rsi_bb": "📉 RSI/BB",
        "manual": "✋ Manual",
    }
    strategy_display = strategy_names.get(strategy.lower() if strategy else "", f"🎲 {strategy}")
    
    # Format exchange and account
    exchange_emoji = "🟡" if exchange == "bybit" else "🟣"  # Yellow for Bybit, Purple for HL
    account_emoji = "🎮" if account_type == "demo" else "💎"
    account_label = "Demo" if account_type == "demo" else "Real"
    
    lines = [
        f"{emoji} *{sym}* {lev}x {side_text}",
        f"",
        f"📍 Entry: `{entry:.6g}` → Now: `{mark:.6g}`",
        f"📦 Size: `{size:.6g}`"
    ]
    
    # TP/SL info
    if tp:
        tp_sign = "+" if (side == "Buy" and tp > entry) or (side == "Sell" and tp < entry) else ""
        tp_pct_val = abs((tp - entry) / entry * 100) if entry else 0
        lines.append(f"🎯 TP: `{tp:.6g}` ({tp_sign}{tp_pct_val:.1f}%)")
    else:
        lines.append(f"🎯 TP: –")
    
    if sl:
        sl_pct_val = abs((sl - entry) / entry * 100) if entry else 0
        lines.append(f"🛑 SL: `{sl:.6g}` (-{sl_pct_val:.1f}%)")
    else:
        lines.append(f"🛑 SL: –")
    
    # Liquidation price if available
    if liq and liq > 0:
        liq_pct = abs((liq - entry) / entry * 100) if entry else 0
        lines.append(f"💀 Liq: `{liq:.6g}` (-{liq_pct:.1f}%)")
    
    # PnL
    lines.append(f"")
    lines.append(f"{pnl_emoji} *PnL:* {pnl_pct:+.2f}% ({pnl:+.4f} USDT)")
    
    # Separator
    lines.append(f"")
    lines.append(f"━━━━━━━━━━━━━━━")
    
    # Strategy info
    lines.append(f"📋 Strategy: {strategy_display}")
    
    # Exchange & Account
    lines.append(f"{exchange_emoji} {exchange.upper()} • {account_emoji} {account_label}")
    
    # ATR Trailing Stop status
    if use_atr:
        atr_status = "✅ Active" if atr_activated else "⏳ Waiting"
        lines.append(f"🔄 ATR Trailing: {atr_status}")
    
    # Time opened
    if open_ts:
        try:
            dt = datetime.datetime.fromtimestamp(open_ts)
            # Calculate duration
            now = datetime.datetime.now()
            duration = now - dt
            hours = int(duration.total_seconds() // 3600)
            mins = int((duration.total_seconds() % 3600) // 60)
            if hours > 24:
                days = hours // 24
                hours = hours % 24
                duration_str = f"{days}d {hours}h"
            elif hours > 0:
                duration_str = f"{hours}h {mins}m"
            else:
                duration_str = f"{mins}m"
            lines.append(f"⏱ Opened: {dt.strftime('%d.%m %H:%M')} ({duration_str} ago)")
        except:
            pass
    
    # Timeframe if available
    if timeframe:
        lines.append(f"📊 Timeframe: {timeframe}")
    
    return "\n".join(lines)


# ------------------------------------------------------------------------------------
# Direct Balance/Positions/Orders functions (skip mode selection for single-mode users)
# ------------------------------------------------------------------------------------

async def show_balance_for_account(update: Update, ctx: ContextTypes.DEFAULT_TYPE, account_type: str):
    """Show balance for specific account type directly (no mode selection menu)."""
    uid = update.effective_user.id
    t = ctx.t
    trading_mode = get_trading_mode(uid)
    
    try:
        # Fetch FULL account balance (totalEquity = all coins in USD)
        account_bal = await fetch_account_balance(uid, account_type=account_type)
        total_equity = account_bal.get("total_equity", 0.0)
        total_wallet = account_bal.get("total_wallet", 0.0)
        available = account_bal.get("available_balance", 0.0)
        used_margin = account_bal.get("used_margin", 0.0)
        coins = account_bal.get("coins", [])
        
        # USDT-specific trading margin (what we actually trade with)
        usdt_wallet = account_bal.get("usdt_wallet", 0.0)
        usdt_available = account_bal.get("usdt_available", 0.0)
        usdt_position_margin = account_bal.get("usdt_position_margin", 0.0)
        usdt_order_margin = account_bal.get("usdt_order_margin", 0.0)
        
        pnl_today = await fetch_today_realized_pnl(uid, tz_str=get_user_tz(uid), account_type=account_type)
        pnl_week = await fetch_realized_pnl(uid, days=7, account_type=account_type)
        positions = await fetch_open_positions(uid, account_type=account_type)
        total_unreal = sum(float(p.get("unrealisedPnl", 0)) for p in positions)
        total_im = sum(float(p.get("positionIM", 0)) for p in positions)
        unreal_pct = (total_unreal / total_im * 100) if total_im else 0.0
        
        mode_emoji = "🎮" if account_type == "demo" else "💎"
        mode_label = "Demo" if account_type == "demo" else "Real"
        
        # Format assets list (only coins with balance > 0)
        assets_text = ""
        # Sort by USD value descending
        sorted_coins = sorted(coins, key=lambda x: x.get("usd_value", 0), reverse=True)
        for coin_data in sorted_coins[:10]:  # Show top 10 assets
            coin = coin_data.get("coin", "")
            balance = coin_data.get("balance", 0)
            usd_val = coin_data.get("usd_value", 0)
            if balance > 0 or usd_val > 0:
                # Format balance nicely
                if balance >= 1:
                    bal_str = f"{balance:,.4f}"
                else:
                    bal_str = f"{balance:.8f}".rstrip('0').rstrip('.')
                assets_text += f"  • {coin}: {bal_str} (${usd_val:,.2f})\n"
        
        if not assets_text:
            assets_text = "  No assets\n"
        
        pnl_emoji_today = "🟢" if pnl_today >= 0 else "🔴"
        pnl_emoji_week = "🟢" if pnl_week >= 0 else "🔴"
        unreal_emoji = "🟢" if total_unreal >= 0 else "🔴"
        
        text = f"""
💰 *Bybit Balance* {mode_emoji} {mode_label}

💎 *Total Equity:* ${total_equity:,.2f}
💵 *Wallet Balance:* ${total_wallet:,.2f}

💵 *USDT Trading Margin:*
  • Wallet: {usdt_wallet:,.2f} USDT
  • In Positions: {usdt_position_margin:,.2f} USDT
  • In Orders: {usdt_order_margin:,.2f} USDT
  ✅ *Available:* {usdt_available:,.2f} USDT

📦 *Assets:*
{assets_text}
📈 *Realized PnL:*
{pnl_emoji_today} Today: {pnl_today:+,.2f} USDT
{pnl_emoji_week} 7 Days: {pnl_week:+,.2f} USDT

{unreal_emoji} *Unrealized PnL:* {total_unreal:+,.2f} USDT ({unreal_pct:+.2f}%)
"""
        
        # Only show mode switch buttons if user has both modes
        if trading_mode == 'both':
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎮 Demo", callback_data="balance:bybit:demo"),
                 InlineKeyboardButton("💎 Real", callback_data="balance:bybit:real")],
                [InlineKeyboardButton("🔙 Back", callback_data="menu:main")]
            ])
        else:
            # Single mode - just back button
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 " + t.get('back', 'Back'), callback_data="menu:main")]
            ])
        
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Balance fetch error (Bybit {account_type}): {e}")
        await update.message.reply_text(t.get('error_fetch_balance', '❌ Error fetching balance: {error}').format(error=str(e)))


async def show_positions_direct(update: Update, ctx: ContextTypes.DEFAULT_TYPE, account_type: str):
    """Show positions directly without mode selection (for single-mode users)."""
    uid = update.effective_user.id
    t = ctx.t
    trading_mode = get_trading_mode(uid)
    
    pos_list = await fetch_open_positions(uid, account_type=account_type)
    
    mode_emoji = "🎮" if account_type == "demo" else "💎"
    mode_label = "Demo" if account_type == "demo" else "Real"
    
    if not pos_list:
        text = f"{mode_emoji} *{mode_label} Positions*\n\n" + t.get('no_positions', '🚫 No open positions')
        
        # Only show mode switch buttons if user has both modes
        if trading_mode == 'both':
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎮 Demo", callback_data="positions:demo"),
                 InlineKeyboardButton("💎 Real", callback_data="positions:real")],
                [InlineKeyboardButton("🔙 " + t.get('back', 'Back'), callback_data="menu:main")]
            ])
        else:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 " + t.get('back', 'Back'), callback_data="menu:main")]
            ])
        
        return await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
    
    # Show paginated positions list
    text = format_positions_list_header(pos_list, 0, t)
    text = f"{mode_emoji} *{mode_label}* " + text
    
    # Store account_type in context for pagination
    ctx.user_data['positions_account_type'] = account_type
    keyboard = get_positions_list_keyboard(pos_list, 0, t)
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def show_orders_direct(update: Update, ctx: ContextTypes.DEFAULT_TYPE, account_type: str):
    """Show orders directly without mode selection (for single-mode users)."""
    uid = update.effective_user.id
    t = ctx.t
    trading_mode = get_trading_mode(uid)
    
    try:
        ords = await fetch_open_orders(uid, account_type=account_type)
        
        mode_emoji = "🎮" if account_type == "demo" else "💎"
        mode_label = "Demo" if account_type == "demo" else "Real"
        header = f"{mode_emoji} *{mode_label} Open Orders*\n\n"
        
        if not ords:
            text = header + t.get('no_open_orders', '🚫 No open orders')
            
            # Only show mode switch buttons if user has both modes
            if trading_mode == 'both':
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎮 Demo", callback_data="orders:demo"),
                     InlineKeyboardButton("💎 Real", callback_data="orders:real")],
                    [InlineKeyboardButton("🔙 " + t.get('back', 'Back'), callback_data="menu:main")]
                ])
            else:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 " + t.get('back', 'Back'), callback_data="menu:main")]
                ])
            
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
            return

        lines = [header + t.get('open_orders_header', '📝 Open Orders:'), ""]
        for i, o in enumerate(ords, start=1):
            price = o.get('price')
            price_str = str(price) if price not in (None, "", 0, "0") else "—"
            qty_str = str(o.get('qty', "—"))
            symbol = o.get('symbol', "—")
            side = o.get('side', "—")
            oid = o.get('orderId', "—")

            lines.append(
                t.get('open_orders_item', '#{idx} {symbol} {side}\n  Qty: {qty} @ {price}\n  ID: {id}').format(
                    idx=i,
                    symbol=symbol,
                    side=side,
                    qty=qty_str,
                    price=price_str,
                    id=oid
                )
            )
            lines.append("")

        text = "\n".join(lines)
        
        # Only show mode switch buttons if user has both modes
        if trading_mode == 'both':
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎮 Demo", callback_data="orders:demo"),
                 InlineKeyboardButton("💎 Real", callback_data="orders:real")],
                [InlineKeyboardButton("🔙 " + t.get('back', 'Back'), callback_data="menu:main")]
            ])
        else:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 " + t.get('back', 'Back'), callback_data="menu:main")]
            ])

        MAX_LEN = 3500
        for pos in range(0, len(text), MAX_LEN):
            chunk = text[pos:pos+MAX_LEN]
            await update.message.reply_text(
                chunk,
                parse_mode="Markdown",
                reply_markup=keyboard if pos + MAX_LEN >= len(text) else None
            )
    except Exception as e:
        logger.error(f"Orders fetch error ({account_type}): {e}")
        await update.message.reply_text(t.get('error_fetch_orders', '❌ Error fetching orders: {error}').format(error=str(e)))


@log_calls
@with_texts  
async def handle_balance_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle balance mode selection callbacks."""
    query = update.callback_query
    await query.answer()
    
    uid = update.effective_user.id
    data = query.data
    t = ctx.t
    
    if not data.startswith("balance:"):
        return
        
    logger.info(f"Balance callback received: {data}")
    parts = data.split(":")
    if len(parts) != 3:
        return
        
    _, exchange, mode = parts
    logger.info(f"Balance request: exchange={exchange}, mode={mode}")
    
    if exchange == "bybit":
        # Fetch Bybit balance for selected mode directly
        try:
            # Use full account balance (all coins, all fields)
            account_bal = await fetch_account_balance(uid, account_type=mode)
            total_equity = account_bal.get("total_equity", 0.0)
            total_wallet = account_bal.get("total_wallet", 0.0)
            available = account_bal.get("available_balance", 0.0)
            used_margin = account_bal.get("used_margin", 0.0)
            coins = account_bal.get("coins", [])
            
            # USDT-specific trading margin (what we actually trade with)
            usdt_wallet = account_bal.get("usdt_wallet", 0.0)
            usdt_available = account_bal.get("usdt_available", 0.0)
            usdt_position_margin = account_bal.get("usdt_position_margin", 0.0)
            usdt_order_margin = account_bal.get("usdt_order_margin", 0.0)
            
            pnl_today = await fetch_today_realized_pnl(uid, tz_str=get_user_tz(uid), account_type=mode)
            pnl_week = await fetch_realized_pnl(uid, days=7, account_type=mode)
            positions = await fetch_open_positions(uid, account_type=mode)
            total_unreal = sum(float(p.get("unrealisedPnl", 0)) for p in positions)
            total_im = sum(float(p.get("positionIM", 0)) for p in positions)
            unreal_pct = (total_unreal / total_im * 100) if total_im else 0.0
            
            trading_mode = get_trading_mode(uid)
            
            mode_emoji = "🎮" if mode == "demo" else "💎"
            mode_label = "Demo" if mode == "demo" else "Real"
            
            # Format assets list
            assets_text = ""
            sorted_coins = sorted(coins, key=lambda x: x.get("usd_value", 0), reverse=True)
            for coin_data in sorted_coins[:10]:
                coin = coin_data.get("coin", "")
                balance = coin_data.get("balance", 0)
                usd_val = coin_data.get("usd_value", 0)
                if balance > 0 or usd_val > 0:
                    if balance >= 1:
                        bal_str = f"{balance:,.4f}"
                    else:
                        bal_str = f"{balance:.8f}".rstrip('0').rstrip('.')
                    assets_text += f"  • {coin}: {bal_str} (${usd_val:,.2f})\n"
            
            if not assets_text:
                assets_text = "  No assets\n"
            
            pnl_emoji_today = "🟢" if pnl_today >= 0 else "🔴"
            pnl_emoji_week = "🟢" if pnl_week >= 0 else "🔴"
            unreal_emoji = "🟢" if total_unreal >= 0 else "🔴"
            
            text = f"""
💰 *Bybit Balance* {mode_emoji} {mode_label}

💎 *Total Equity:* ${total_equity:,.2f}
💵 *Wallet Balance:* ${total_wallet:,.2f}

💵 *USDT Trading Margin:*
  • Wallet: {usdt_wallet:,.2f} USDT
  • In Positions: {usdt_position_margin:,.2f} USDT
  • In Orders: {usdt_order_margin:,.2f} USDT
  ✅ *Available:* {usdt_available:,.2f} USDT

📦 *Assets:*
{assets_text}
📈 *Realized PnL:*
{pnl_emoji_today} Today: {pnl_today:+,.2f} USDT
{pnl_emoji_week} 7 Days: {pnl_week:+,.2f} USDT

{unreal_emoji} *Unrealized PnL:* {total_unreal:+,.2f} USDT ({unreal_pct:+.2f}%)
"""
            
            # Only show mode switch buttons if user has both modes
            if trading_mode == 'both':
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎮 Demo", callback_data="balance:bybit:demo"),
                     InlineKeyboardButton("💎 Real", callback_data="balance:bybit:real")],
                    [InlineKeyboardButton("🔙 Back", callback_data="menu:main")]
                ])
            else:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="menu:main")]
                ])
            
            await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Balance fetch error (Bybit {mode}): {e}")
            await query.edit_message_text(
                f"❌ Error fetching balance: {str(e)}",
                parse_mode="Markdown"
            )
            
    elif exchange == "hl":
        # Fetch HyperLiquid balance for selected mode
        try:
            testnet = (mode == "testnet")
            
            hl_creds = get_hl_credentials(uid)
            if not hl_creds.get("hl_private_key"):
                await query.edit_message_text(
                    "❌ HyperLiquid not configured. Use /hl to set up.",
                    parse_mode="Markdown"
                )
                return
            
            adapter = HLAdapter(
                private_key=hl_creds["hl_private_key"],
                testnet=testnet,
                vault_address=hl_creds.get("hl_vault_address")
            )
            
            result = await adapter.get_balance()
            
            if result.get("success"):
                data_bal = result.get("data", {})
                equity = float(data_bal.get("equity", 0))
                available = float(data_bal.get("available", 0))
                margin_used = float(data_bal.get("margin_used", 0))
                total_notional = float(data_bal.get("total_notional", 0))
                unrealized_pnl = float(data_bal.get("unrealized_pnl", 0))
                position_value = float(data_bal.get("position_value", 0))
                num_positions = int(data_bal.get("num_positions", 0))
                currency = data_bal.get("currency", "USDC")
                
                pnl_emoji = "🟢" if unrealized_pnl >= 0 else "🔴"
                network = "🧪 Testnet" if testnet else "🌐 Mainnet"
                
                # Calculate margin level if margin used > 0
                margin_level = ""
                if margin_used > 0:
                    level_pct = (equity / margin_used) * 100
                    margin_level = f"\n📐 *Margin Level:* {level_pct:.1f}%"
                
                text = f"""
💰 *HyperLiquid Balance* {network}

💎 *Account Equity:* ${equity:,.2f} {currency}
✅ *Available for Trading:* ${available:,.2f} {currency}
📊 *Margin Used:* ${margin_used:,.2f} {currency}{margin_level}

📦 *Positions:*
  • Active: {num_positions} positions
  • Notional Value: ${total_notional:,.2f}
  • Position Value: ${position_value:,.2f}

{pnl_emoji} *Unrealized PnL:* ${unrealized_pnl:,.2f} {currency}
"""
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🧪 Testnet", callback_data="balance:hl:testnet"),
                     InlineKeyboardButton("🌐 Mainnet", callback_data="balance:hl:mainnet")],
                    [InlineKeyboardButton("🔙 Back", callback_data="menu:main")]
                ])
                
                await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
            else:
                await query.edit_message_text(
                    f"❌ Failed to fetch balance: {result.get('error', 'Unknown error')}",
                    parse_mode="Markdown"
                )
                
        except Exception as e:
            logger.error(f"Balance fetch error (HL {mode}): {e}")
            await query.edit_message_text(
                f"❌ Error: {str(e)}",
                parse_mode="Markdown"
            )


@with_texts
async def on_positions_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle position management callbacks."""
    query = update.callback_query
    await query.answer()
    
    uid = update.effective_user.id
    data = query.data
    t = ctx.t
    
    if data == "pos:back":
        # Go back to main menu
        await query.message.delete()
        return
    
    if data == "pos:noop":
        # Do nothing - just for counter button
        return
    
    if data.startswith("pos:refresh"):
        # Refresh positions list - show list view
        # Support pos:refresh or pos:refresh:PAGE format
        parts = data.split(":")
        saved_page = int(parts[2]) if len(parts) > 2 else ctx.user_data.get('positions_page', 0)
        
        positions = await fetch_open_positions(uid)
        if not positions:
            await query.edit_message_text(
                t.get('no_positions', 'No open positions'),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data="pos:back")
                ]])
            )
            return
        
        # Validate page is still valid after position changes
        total_pages = (len(positions) + POSITIONS_PER_PAGE - 1) // POSITIONS_PER_PAGE
        page = max(0, min(saved_page, total_pages - 1))
        ctx.user_data['positions_page'] = page
        
        text = format_positions_list_header(positions, page, t)
        keyboard = get_positions_list_keyboard(positions, page, t)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
        return
    
    if data.startswith("pos:list:"):
        # Navigate to specific page of positions list
        page = int(data.split(":")[2])
        positions = await fetch_open_positions(uid)
        if not positions:
            await query.edit_message_text(
                t.get('no_positions', 'No open positions'),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data="pos:back")
                ]])
            )
            return
        
        # Ensure valid page
        total_pages = (len(positions) + POSITIONS_PER_PAGE - 1) // POSITIONS_PER_PAGE
        page = max(0, min(page, total_pages - 1))
        
        # Save current page for later restoration
        ctx.user_data['positions_page'] = page
        
        text = format_positions_list_header(positions, page, t)
        keyboard = get_positions_list_keyboard(positions, page, t)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
        return
    
    if data.startswith("pos:page:"):
        # Legacy: Navigate to specific single position (keeping for backward compatibility)
        page_idx = int(data.split(":")[2])
        positions = await fetch_open_positions(uid)
        if not positions:
            await query.edit_message_text(
                t.get('no_positions', 'No open positions'),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data="pos:back")
                ]])
            )
            return
        
        # Ensure valid index
        page_idx = max(0, min(page_idx, len(positions) - 1))
        
        # Get saved page from user_data
        saved_page = ctx.user_data.get('positions_page', 0)
        
        text = format_single_position(positions[page_idx], page_idx, len(positions), t)
        keyboard = get_positions_paginated_keyboard(positions, page_idx, t, page=saved_page)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
        return
    
    if data.startswith("pos:view:"):
        # View detailed position
        symbol = data.split(":")[2]
        positions = await fetch_open_positions(uid)
        pos = next((p for p in positions if p["symbol"] == symbol), None)
        
        # Get saved page from user_data
        saved_page = ctx.user_data.get('positions_page', 0)
        
        if not pos:
            await query.edit_message_text(
                t.get('position_not_found', 'Position not found'),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data=f"pos:refresh:{saved_page}")
                ]])
            )
            return
        
        text = format_position_detail(pos, t)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"❌ {t.get('btn_close_position', 'Close position')}", callback_data=f"pos:close:{symbol}")],
            [InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data=f"pos:refresh:{saved_page}")]
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
        return
    
    if data.startswith("pos:close:"):
        # Close single position
        symbol = data.split(":")[2]
        positions = await fetch_open_positions(uid)
        pos = next((p for p in positions if p["symbol"] == symbol), None)
        
        # Get saved page
        saved_page = ctx.user_data.get('positions_page', 0)
        
        if not pos:
            await query.edit_message_text(
                t.get('position_not_found', 'Position not found'),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data=f"pos:refresh:{saved_page}")
                ]])
            )
            return
        
        # Confirm close
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"✅ {t.get('btn_confirm_close', 'Confirm close')}", callback_data=f"pos:confirm_close:{symbol}")],
            [InlineKeyboardButton(t.get('btn_cancel', '❌ Cancel'), callback_data=f"pos:refresh:{saved_page}")]
        ])
        side_text = "LONG" if pos["side"] == "Buy" else "SHORT"
        size = float(pos.get("size") or 0)
        pnl = float(pos.get("unrealisedPnl") or 0)
        pnl_emoji = "📈" if pnl >= 0 else "📉"
        
        await query.edit_message_text(
            f"⚠️ {t.get('confirm_close_position', 'Close position')}?\n\n"
            f"*{symbol}* {side_text}\n"
            f"Size: {size}\n"
            f"{pnl_emoji} P/L: {pnl:+.4f} USDT",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return
    
    if data.startswith("pos:confirm_close:"):
        # Execute close
        symbol = data.split(":")[2]
        positions = await fetch_open_positions(uid)
        pos = next((p for p in positions if p["symbol"] == symbol), None)
        
        # Get saved page
        saved_page = ctx.user_data.get('positions_page', 0)
        
        if not pos:
            await query.edit_message_text(
                t.get('position_already_closed', 'Position already closed'),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data=f"pos:refresh:{saved_page}")
                ]])
            )
            return
        
        try:
            close_side = "Sell" if pos["side"] == "Buy" else "Buy"
            size = float(pos["size"])
            entry_price = float(pos.get("avgPrice") or 0)
            mark_price = float(pos.get("markPrice") or 0)
            unrealized_pnl = float(pos.get("unrealisedPnl") or 0)
            im = float(pos.get("positionIM") or 0)
            pnl_pct = (unrealized_pnl / im * 100) if im else 0.0
            side_text = "LONG" if pos["side"] == "Buy" else "SHORT"
            
            await place_order(
                user_id=uid,
                symbol=symbol,
                side=close_side,
                orderType="Market",
                qty=size
            )
            
            # Get active position info for strategy
            active_pos = get_active_positions(uid)
            ap = next((a for a in active_pos if a["symbol"] == symbol), None)
            strategy = ap.get("strategy") if ap else None
            strategy_display = {
                "scryptomera": "Scryptomera",
                "scalper": "Scalper", 
                "rsi_bb": "RSI+BB",
                "oi": "OI",
                "elcaro": "Elcaro",
                "fibonacci": "Fibonacci",
                "manual": "Manual",
            }.get(strategy, "Manual" if not strategy else strategy.title())
            
            # Log the trade
            try:
                account_type = get_trading_mode(uid) or "demo"
                log_exit_and_remove_position(
                    user_id=uid,
                    signal_id=ap.get("signal_id") if ap else None,
                    symbol=symbol,
                    side=pos["side"],
                    entry_price=entry_price,
                    exit_price=mark_price,
                    exit_reason="MANUAL",
                    size=size,
                    strategy=strategy,
                    account_type=account_type,
                )
            except Exception as log_err:
                logger.warning(f"Failed to log manual close for {symbol}: {log_err}")
            
            # Clean up internal tracking (log_exit_and_remove_position already removes position)
            reset_pyramid(uid, symbol)
            
            # Send notification about closed position
            if notification_service:
                try:
                    await notification_service.send_position_closed_notification(
                        user_id=uid,
                        position_data={
                            'symbol': symbol,
                            'side': side_text,
                            'entry_price': entry_price,
                            'exit_price': mark_price,
                            'quantity': size,
                            'pnl': unrealized_pnl,
                            'pnl_percent': pnl_pct,
                            'strategy': strategy_display,
                            'close_reason': 'Manual'
                        },
                        t=t
                    )
                except Exception as notif_err:
                    logger.error(f"Failed to send position closed notification: {notif_err}")
            
            # Format beautiful close message
            pnl_emoji = "📈" if unrealized_pnl >= 0 else "📉"
            emoji = "🟢" if pos["side"] == "Buy" else "🔴"
            
            close_msg = (
                f"✅ *{t.get('position_closed_success', 'Position closed')}*\n\n"
                f"{emoji} *{symbol}* {side_text}\n"
                f"• Strategy: `{strategy_display}`\n"
                f"• Entry: `{entry_price:.6g}`\n"
                f"• Exit: `{mark_price:.6g}`\n"
                f"{pnl_emoji} P/L: `{unrealized_pnl:+.4f}` USDT ({pnl_pct:+.2f}%)"
            )
            
            await query.edit_message_text(
                close_msg,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data=f"pos:refresh:{saved_page}")
                ]])
            )
        except Exception as e:
            logger.error(f"Close position {symbol} failed: {e}")
            await query.edit_message_text(
                f"❌ {t.get('position_close_error', 'Error closing position')}: {str(e)}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data=f"pos:refresh:{saved_page}")
                ]])
            )
        return
    
    if data == "pos:close_all":
        # Confirm close all
        positions = await fetch_open_positions(uid)
        if not positions:
            await query.edit_message_text(
                t.get('no_positions', 'No open positions'),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data="pos:back")
                ]])
            )
            return
        
        total_pnl = sum(float(p.get("unrealisedPnl") or 0) for p in positions)
        pnl_emoji = "📈" if total_pnl >= 0 else "📉"
        
        saved_page = ctx.user_data.get('positions_page', 0)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"✅ {t.get('btn_confirm_close_all', 'Yes, close all')}", callback_data="pos:confirm_close_all")],
            [InlineKeyboardButton(t.get('btn_cancel', '❌ Cancel'), callback_data=f"pos:refresh:{saved_page}")]
        ])
        
        await query.edit_message_text(
            f"⚠️ {t.get('confirm_close_all', 'Close ALL positions')}?\n\n"
            f"{t.get('positions_count_total', 'Total positions')}: {len(positions)}\n"
            f"{pnl_emoji} {t.get('total_pnl', 'Total P/L')}: {total_pnl:+.4f} USDT",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return
    
    if data == "pos:pause_after_close":
        # Disable all strategies after closing positions
        set_user_field(uid, "trade_scryptomera", 0)
        set_user_field(uid, "trade_scalper", 0)
        set_user_field(uid, "trade_elcaro", 0)
        set_user_field(uid, "trade_fibonacci", 0)
        
        saved_page = ctx.user_data.get('positions_page', 0)
        await query.edit_message_text(
            "✅ *All trading paused!*\n\n"
            "All strategies disabled. No new positions will open.\n\n"
            "To resume trading, enable strategies in Settings → Strategy.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⚙️ Strategy Settings", callback_data="settings:strategy"),
                InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data=f"pos:refresh:{saved_page}")
            ]])
        )
        return
    
    if data == "pos:confirm_close_all":
        # Execute close all
        positions = await fetch_open_positions(uid)
        if not positions:
            await query.edit_message_text(
                t.get('no_positions', 'No open positions'),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data="pos:back")
                ]])
            )
            return
        
        closed = 0
        errors = 0
        total_pnl = 0.0
        closed_positions = []
        active_list = get_active_positions(uid)
        
        for pos in positions:
            try:
                close_side = "Sell" if pos["side"] == "Buy" else "Buy"
                size = float(pos["size"])
                symbol = pos["symbol"]
                entry_price = float(pos.get("avgPrice") or 0)
                mark_price = float(pos.get("markPrice") or 0)
                unrealized_pnl = float(pos.get("unrealisedPnl") or 0)
                
                await place_order(
                    user_id=uid,
                    symbol=symbol,
                    side=close_side,
                    orderType="Market",
                    qty=size
                )
                
                # Log the trade
                ap = next((a for a in active_list if a["symbol"] == symbol), None)
                strategy = ap.get("strategy") if ap else None
                account_type = get_trading_mode(uid) or "demo"
                try:
                    log_exit_and_remove_position(
                        user_id=uid,
                        signal_id=ap.get("signal_id") if ap else None,
                        symbol=symbol,
                        side=pos["side"],
                        entry_price=entry_price,
                        exit_price=mark_price,
                        exit_reason="MANUAL",
                        size=size,
                        strategy=strategy,
                        account_type=account_type,
                    )
                except Exception as log_err:
                    logger.warning(f"Failed to log manual close for {symbol}: {log_err}")
                # Send position-closed notification (for Close All flow)
                try:
                    strategy_display = {
                        "scryptomera": "Scryptomera",
                        "scalper": "Scalper",
                        "rsi_bb": "RSI+BB",
                        "oi": "OI",
                        "elcaro": "Elcaro",
                        "fibonacci": "Fibonacci",
                        "manual": "Manual",
                    }.get(strategy, strategy.title() if strategy else "Manual")
                    if notification_service:
                        pnl_pct = 0.0
                        try:
                            if entry_price:
                                pnl_pct = (mark_price / entry_price - 1.0) * (100 if pos["side"] == "Buy" else -100)
                        except Exception:
                            pnl_pct = 0.0
                        await notification_service.send_position_closed_notification(
                            user_id=uid,
                            position_data={
                                'symbol': symbol,
                                'side': pos.get('side'),
                                'entry_price': entry_price,
                                'exit_price': mark_price,
                                'quantity': size,
                                'pnl': unrealized_pnl,
                                'pnl_percent': pnl_pct,
                                'strategy': strategy_display,
                                'close_reason': 'Manual'
                            },
                            t=t
                        )
                except Exception as notif_err:
                    logger.error(f"Failed to send position closed notification (close_all): {notif_err}")
                
                # log_exit_and_remove_position already removes position
                reset_pyramid(uid, symbol)
                closed += 1
                total_pnl += unrealized_pnl
                closed_positions.append({
                    "symbol": symbol,
                    "side": pos["side"],
                    "pnl": unrealized_pnl
                })
            except Exception as e:
                logger.error(f"Close position {pos['symbol']} failed: {e}")
                errors += 1
        
        # Set cooldown flag to prevent monitoring loop from re-adding positions
        import time
        _close_all_cooldown[uid] = time.time() + 30  # 30 seconds cooldown
        
        # Format result message
        pnl_emoji = "📈" if total_pnl >= 0 else "📉"
        result_lines = [f"✅ *{t.get('all_positions_closed', 'All positions closed')}*\n"]
        
        for cp in closed_positions:
            cp_emoji = "🟢" if cp["side"] == "Buy" else "🔴"
            cp_pnl_emoji = "+" if cp["pnl"] >= 0 else ""
            result_lines.append(f"{cp_emoji} {cp['symbol']}: `{cp_pnl_emoji}{cp['pnl']:.4f}` USDT")
        
        result_lines.append(f"\n{pnl_emoji} *{t.get('total_pnl', 'Total P/L')}:* `{total_pnl:+.4f}` USDT")
        
        if errors:
            result_lines.append(f"\n❌ {t.get('errors', 'Errors')}: {errors}")
        
        result_lines.append("\n⚠️ *Strategies still active!* New signals may open positions.")
        
        saved_page = ctx.user_data.get('positions_page', 0)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⏸ Pause All Trading", callback_data="pos:pause_after_close")],
            [InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data=f"pos:refresh:{saved_page}")]
        ])
        
        await query.edit_message_text(
            "\n".join(result_lines),
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return


@require_access
@with_texts
@log_calls
async def cmd_open_positions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show open positions with inline management buttons and pagination (10 per page)."""
    uid = update.effective_user.id
    positions = await fetch_open_positions(uid)
    
    if not positions:
        return await update.message.reply_text(ctx.t.get('no_positions', 'No open positions'))
    
    # Show positions list with pagination (10 per page)
    text = format_positions_list_header(positions, 0, ctx.t)
    keyboard = get_positions_list_keyboard(positions, 0, ctx.t)
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)


# ------------------------------------------------------------------------------------
# Trading Statistics
# ------------------------------------------------------------------------------------
STRATEGY_DISPLAY_NAMES = {
    "oi": "📉 OI",
    "rsi_bb": "📊 RSI+BB",
    "scryptomera": "🐱 Scryptomera",
    "scalper": "⚡ Scalper",
    "elcaro": "🔥 Elcaro",
    "fibonacci": "📐 Fibonacci",
    "manual": "✋ Manual",
    "all": "📈 All",
}

ACCOUNT_DISPLAY_NAMES = {
    "demo": "🔵 Demo",
    "real": "🟢 Real",
}

async def format_trade_stats(stats: dict, t: dict, strategy_name: str = "all", period_label: str = "", unrealized_pnl: float = 0.0, uid: int = None, account_type: str = "demo", period: str = "all", api_pnl: float = None) -> str:
    """Format trade statistics in beautiful style like the screenshot.
    
    Args:
        stats: Trade stats from database
        t: Translations dict
        strategy_name: Strategy filter
        period_label: Human-readable period label
        unrealized_pnl: Unrealized PnL from open positions
        uid: User ID
        account_type: 'demo' or 'real'
        period: Period key ('today', 'week', 'month', 'all')
        api_pnl: PnL from exchange API (for comparison/accuracy)
    """
    strat_display = STRATEGY_DISPLAY_NAMES.get(strategy_name, strategy_name.upper())
    account_display = ACCOUNT_DISPLAY_NAMES.get(account_type, account_type.capitalize())
    
    total = stats.get("total", 0)
    tp_count = stats.get("tp_count", 0)
    sl_count = stats.get("sl_count", 0)
    eod_count = stats.get("eod_count", 0)
    winrate = stats.get("winrate", 0.0)
    total_pnl = stats.get("total_pnl", 0.0)
    avg_pnl_pct = stats.get("avg_pnl_pct", 0.0)
    long_count = stats.get("long_count", 0)
    short_count = stats.get("short_count", 0)
    long_winrate = stats.get("long_winrate", 0.0)
    short_winrate = stats.get("short_winrate", 0.0)
    gross_profit = stats.get("gross_profit", 0.0)
    gross_loss = stats.get("gross_loss", 0.0)
    profit_factor = stats.get("profit_factor", 0.0)
    
    # R calculation (assuming 1R = 1% of account)
    total_r = total_pnl / 100 if total_pnl != 0 else 0
    avg_r = avg_pnl_pct / 100 if avg_pnl_pct != 0 else 0
    
    # Long/Short R
    long_pnl = gross_profit * (long_count / max(total, 1)) if long_count > 0 else 0
    short_pnl = gross_profit * (short_count / max(total, 1)) if short_count > 0 else 0
    
    closed = tp_count + sl_count + eod_count
    open_trades = stats.get("open_count", 0)  # From active_positions table
    total_with_open = closed + open_trades  # Include open positions in total
    
    # Combined PnL: realized + unrealized
    combined_pnl = total_pnl + unrealized_pnl
    
    pnl_sign = "+" if total_pnl >= 0 else ""
    pnl_emoji = "📈" if total_pnl >= 0 else "📉"
    unreal_sign = "+" if unrealized_pnl >= 0 else ""
    unreal_emoji = "📈" if unrealized_pnl >= 0 else "📉"
    combined_sign = "+" if combined_pnl >= 0 else ""
    combined_emoji = "📈" if combined_pnl >= 0 else "📉"
    
    lines = [
        f"📊 *{t.get('stats_title', 'Trading Statistics')}* {account_display}",
        f"├ {t.get('stats_strategy', 'Strategy')}: {strat_display}",
        f"└ {t.get('stats_period', 'Period')}: 📅 {period_label}",
        "",
        f"*{t.get('stats_overview', 'Overview')}*",
        f"├─ {t.get('stats_total_trades', 'Total trades')}: {total_with_open}",
        f"├─ {t.get('stats_closed', 'Closed')}: {closed}",
        f"└─ {t.get('stats_open', 'Open')}: {open_trades}",
        "",
        f"*{t.get('stats_results', 'Results')}*",
        f"├─ TP: {tp_count} │ SL: {sl_count} │ EOD: {eod_count}",
        f"├─ {t.get('stats_winrate', 'Winrate')}: {winrate:.1f}%",
        f"├─ {t.get('stats_total_r', 'Total R')}: {pnl_sign}{total_r:.2f}R",
        f"└─ {t.get('stats_avg_r', 'Avg R')}: {pnl_sign}{avg_r:.2f}R",
        "",
        f"*{t.get('stats_by_direction', 'By Direction')}*",
        f"├─ 🟢 {t.get('stats_long', 'Long')}: {long_count} │ {t.get('stats_winrate', 'WR')}: {long_winrate:.1f}%",
        f"└─ 🔴 {t.get('stats_short', 'Short')}: {short_count} │ {t.get('stats_winrate', 'WR')}: {short_winrate:.1f}%",
        "",
        f"*{t.get('stats_pnl', 'Profit/Loss')}*",
        f"├─ {t.get('stats_gross_profit', 'Profit')}: ${gross_profit:.2f}",
        f"├─ {t.get('stats_gross_loss', 'Loss')}: ${abs(gross_loss):.2f}",
    ]
    
    # Use API PnL as primary if available (more accurate), otherwise use DB
    if api_pnl is not None and strategy_name == "all":
        # API PnL is the real truth from exchange
        display_pnl = api_pnl
        display_sign = "+" if api_pnl >= 0 else ""
        display_emoji = "📈" if api_pnl >= 0 else "📉"
        lines.append(f"├─ {display_emoji} {t.get('stats_realized_pnl', 'Realized')}: ${display_sign}{display_pnl:.2f}")
        
        # Calculate combined with API PnL
        combined_pnl = api_pnl + unrealized_pnl
        combined_sign = "+" if combined_pnl >= 0 else ""
        combined_emoji = "📈" if combined_pnl >= 0 else "📉"
    else:
        # Fallback to DB tracked PnL
        lines.append(f"├─ {pnl_emoji} {t.get('stats_realized_pnl', 'Realized')}: ${pnl_sign}{total_pnl:.2f}")
    
    # Add unrealized PnL if there are open positions
    if open_trades > 0:
        lines.append(f"├─ {unreal_emoji} {t.get('stats_unrealized_pnl', 'Unrealized')}: ${unreal_sign}{unrealized_pnl:.2f}")
        lines.append(f"├─ {combined_emoji} {t.get('stats_combined_pnl', 'Combined')}: ${combined_sign}{combined_pnl:.2f}")
    
    lines.append(f"└─ {t.get('stats_profit_factor', 'PF')}: {profit_factor:.2f}" if profit_factor != float('inf') else f"└─ {t.get('stats_profit_factor', 'PF')}: ∞")
    
    # Add strategy settings if specific strategy is selected and uid is provided
    if uid and strategy_name != "all":
        strat_settings = db.get_strategy_settings(uid, strategy_name)
        if strat_settings:
            lines.append("")
            lines.append(f"*⚙️ {t.get('stats_strategy_settings', 'Strategy Settings')}*")
            
            # Entry percentage
            entry_pct = strat_settings.get("percent", 0)
            if entry_pct:
                lines.append(f"├─ {t.get('settings_entry_pct', 'Entry')}: {entry_pct}%")
            
            # SL/TP percentages
            sl_pct = strat_settings.get("sl_percent", 0)
            tp_pct = strat_settings.get("tp_percent", 0)
            if sl_pct or tp_pct:
                lines.append(f"├─ SL: {sl_pct}% │ TP: {tp_pct}%")
            
            # Leverage
            leverage = strat_settings.get("leverage", 0)
            if leverage:
                lines.append(f"├─ {t.get('settings_leverage', 'Leverage')}: {leverage}x")
            
            # Trading mode
            trading_mode = strat_settings.get("trading_mode", "")
            if trading_mode:
                mode_display = {"market": "🔵 Market", "limit": "🟡 Limit", "both": "🔄 Both"}.get(trading_mode, trading_mode)
                lines.append(f"├─ {t.get('settings_trading_mode', 'Mode')}: {mode_display}")
            
            # Direction
            direction = strat_settings.get("direction", "")
            if direction:
                dir_display = {"long": "🟢 Long", "short": "🔴 Short", "both": "🔄 Both"}.get(direction, direction)
                lines.append(f"└─ {t.get('settings_direction', 'Direction')}: {dir_display}")
    
    return "\n".join(lines)


def get_stats_keyboard(t: dict, current_strategy: str = "all", current_period: str = "all", current_account: str = "demo") -> InlineKeyboardMarkup:
    """Build inline keyboard for statistics navigation."""
    strategies = [
        ("all", t.get('stats_all', '📈 All')),
        ("oi", t.get('stats_oi', '📉 OI')),
        ("rsi_bb", t.get('stats_rsi_bb', '📊 RSI+BB')),
        ("scryptomera", t.get('stats_scryptomera', '🐱 Scryptomera')),
        ("scalper", t.get('stats_scalper', '⚡ Scalper')),
        ("elcaro", t.get('stats_elcaro', '🔥 Elcaro')),
        ("fibonacci", t.get('stats_fibonacci', '📐 Fibonacci')),
        ("manual", t.get('stats_manual', '✋ Manual')),
        ("spot", t.get('stats_spot', '💹 Spot')),
    ]
    
    periods = [
        ("all", t.get('stats_period_all', '📅 All')),
        ("today", t.get('stats_period_today', '📆 24h')),
        ("week", t.get('stats_period_week', '📅 Week')),
        ("month", t.get('stats_period_month', '🗓 Month')),
    ]
    
    accounts = [
        ("demo", t.get('stats_demo', '🔵 Demo')),
        ("real", t.get('stats_real', '🟢 Real')),
    ]
    
    # Account type buttons (first row)
    account_buttons = []
    for key, label in accounts:
        marker = "✓ " if key == current_account else ""
        account_buttons.append(InlineKeyboardButton(f"{marker}{label}", callback_data=f"stats:acc:{current_strategy}:{current_period}:{key}"))
    
    # Strategy buttons (2 per row)
    strat_buttons = []
    row = []
    for i, (key, label) in enumerate(strategies):
        marker = "✓ " if key == current_strategy else ""
        row.append(InlineKeyboardButton(f"{marker}{label}", callback_data=f"stats:strat:{key}:{current_period}:{current_account}"))
        if len(row) == 2:
            strat_buttons.append(row)
            row = []
    if row:
        strat_buttons.append(row)
    
    # Period buttons (1 row)
    period_buttons = []
    for key, label in periods:
        marker = "✓" if key == current_period else ""
        period_buttons.append(InlineKeyboardButton(f"{marker}{label}", callback_data=f"stats:period:{current_strategy}:{key}:{current_account}"))
    
    # Combine: Account selector first, then strategies, periods, and back
    keyboard = [account_buttons] + strat_buttons + [period_buttons]
    keyboard.append([InlineKeyboardButton(t.get('btn_back', '🔙 Back'), callback_data="stats:close")])
    
    return InlineKeyboardMarkup(keyboard)


async def get_unrealized_pnl(user_id: int, strategy: str | None = None) -> float:
    """Get total unrealized PnL from Bybit positions, optionally filtered by strategy."""
    try:
        # Get positions from all accounts
        account_types = get_active_account_types(user_id)
        if not account_types:
            return 0.0
        
        total_unrealized = 0.0
        db_positions = db.get_active_positions(user_id)
        
        # Build a mapping of symbol -> strategy from DB
        symbol_strategy_map = {p["symbol"]: p.get("strategy") for p in db_positions}
        
        for acc_type in account_types:
            try:
                cursor = None
                while True:
                    params = {"category": "linear", "settleCoin": "USDT", "limit": 200}
                    if cursor:
                        params["cursor"] = cursor
                    
                    data = await _bybit_request(
                        user_id, "GET", "/v5/position/list",
                        params=params,
                        account_type=acc_type
                    )
                    positions = data.get("list", [])
                    
                    for p in positions:
                        size = float(p.get("size") or 0)
                        if size <= 0:
                            continue
                        
                        symbol = p.get("symbol", "")
                        pos_strategy = symbol_strategy_map.get(symbol)
                        
                        # Filter by strategy if specified
                        if strategy and pos_strategy != strategy:
                            continue
                        
                        unrealized = float(p.get("unrealisedPnl") or 0)
                        total_unrealized += unrealized
                    
                    cursor = data.get("nextPageCursor")
                    if not cursor:
                        break
                    
            except Exception as e:
                logger.warning(f"Failed to get positions for {acc_type}: {e}")
                continue
        
        return total_unrealized
    except Exception as e:
        logger.warning(f"Failed to get unrealized PnL: {e}")
        return 0.0


@require_access
@with_texts
@log_calls
async def cmd_trade_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show trading statistics."""
    uid = update.effective_user.id
    t = ctx.t
    
    # Determine default account type based on user's active accounts
    creds = db.get_all_user_credentials(uid)
    default_account = "real" if creds.get("real_api_key") else "demo"
    
    # Default: all strategies, all time, detected account
    stats = get_trade_stats(uid, strategy=None, period="all", account_type=default_account)
    period_label = t.get('stats_period_all', 'All time')
    
    # Get unrealized PnL from open positions
    unrealized_pnl = await get_unrealized_pnl(uid, strategy=None)
    
    # For "all time" period, we don't fetch API PnL (would be too expensive)
    text = await format_trade_stats(stats, t, strategy_name="all", period_label=period_label, unrealized_pnl=unrealized_pnl, uid=uid, account_type=default_account, period="all", api_pnl=None)
    keyboard = get_stats_keyboard(t, current_strategy="all", current_period="all", current_account=default_account)
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)


@with_texts
@log_calls
async def on_stats_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle statistics navigation callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    t = ctx.t
    uid = update.effective_user.id
    
    if data == "stats:close":
        await query.delete_message()
        return
    
    parts = data.split(":")
    if len(parts) < 4:
        return
    
    # Parse callback data - now includes account_type
    # Format: stats:action:strategy:period:account_type
    _, action, *rest = parts
    
    # Handle different formats
    if action == "acc":
        # stats:acc:strategy:period:new_account_type -> switch account
        strategy = rest[0] if len(rest) > 0 else "all"
        period = rest[1] if len(rest) > 1 else "all"
        account_type = rest[2] if len(rest) > 2 else "demo"
    elif action == "strat":
        # stats:strat:new_strategy:period:account_type -> switch strategy
        strategy = rest[0] if len(rest) > 0 else "all"
        period = rest[1] if len(rest) > 1 else "all"
        account_type = rest[2] if len(rest) > 2 else "demo"
    elif action == "period":
        # stats:period:strategy:new_period:account_type -> switch period
        strategy = rest[0] if len(rest) > 0 else "all"
        period = rest[1] if len(rest) > 1 else "all"
        account_type = rest[2] if len(rest) > 2 else "demo"
    else:
        return
    
    period_labels = {
        "all": t.get('stats_period_all', 'All time'),
        "today": t.get('stats_period_today', '24h'),
        "week": t.get('stats_period_week', 'Week'),
        "month": t.get('stats_period_month', 'Month'),
    }
    period_label = period_labels.get(period, period)
    
    # Special handling for Spot statistics
    if strategy == "spot":
        text = await format_spot_stats(uid, t, period_label, account_type=account_type)
        keyboard = get_stats_keyboard(t, current_strategy=strategy, current_period=period, current_account=account_type)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
        return
    
    # Special handling for Manual trades (NULL strategy)
    if strategy == "manual":
        from db import get_trade_stats_unknown
        stats = get_trade_stats_unknown(uid, period=period, account_type=account_type)
        # Format manual stats with minimal info
        strat_display = "✋ Manual"
        account_display = ACCOUNT_DISPLAY_NAMES.get(account_type, account_type.capitalize())
        text = (
            f"📊 *{t.get('stats_title', 'Trading Statistics')}* {account_display}\n"
            f"├ {t.get('stats_strategy', 'Strategy')}: {strat_display}\n"
            f"└ {t.get('stats_period', 'Period')}: 📅 {period_label}\n\n"
            f"*{t.get('stats_overview', 'Overview')}*\n"
            f"├─ {t.get('stats_total_trades', 'Total trades')}: {stats['total']}\n"
            f"├─ {t.get('stats_winrate', 'Winrate')}: {stats['winrate']:.1f}%\n"
            f"└─ PnL: {stats['total_pnl']:+.2f} USDT\n\n"
            f"_These are trades closed manually without strategy attribution._"
        )
        keyboard = get_stats_keyboard(t, current_strategy=strategy, current_period=period, current_account=account_type)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
        return
    
    # Get stats based on selection
    strat_filter = None if strategy == "all" else strategy
    stats = get_trade_stats(uid, strategy=strat_filter, period=period, account_type=account_type)
    
    # Get unrealized PnL for selected strategy
    unrealized_pnl = await get_unrealized_pnl(uid, strategy=strat_filter)
    
    # Fetch API PnL for comparison (only for today/week periods and "all" strategy)
    api_pnl = None
    if strategy == "all":
        try:
            exchange = db.get_exchange_type(uid) or 'bybit'
            if exchange == 'bybit':
                if period == "today":
                    api_pnl = await fetch_today_realized_pnl(uid, account_type=account_type)
                elif period == "week":
                    api_pnl = await fetch_realized_pnl(uid, days=7, account_type=account_type)
                elif period == "month":
                    api_pnl = await fetch_realized_pnl(uid, days=30, account_type=account_type)
                elif period == "all":
                    # For all-time, fetch maximum Bybit allows (90 days)
                    api_pnl = await fetch_realized_pnl(uid, days=90, account_type=account_type)
        except Exception as e:
            logger.warning(f"Failed to fetch API PnL for stats: {e}")
    
    text = await format_trade_stats(stats, t, strategy_name=strategy, period_label=period_label, unrealized_pnl=unrealized_pnl, uid=uid, account_type=account_type, period=period, api_pnl=api_pnl)
    keyboard = get_stats_keyboard(t, current_strategy=strategy, current_period=period, current_account=account_type)
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def format_spot_stats(uid: int, t: dict, period_label: str, account_type: str = "demo") -> str:
    """Format Spot DCA statistics."""
    cfg = db.get_user_config(uid)
    spot_settings = cfg.get("spot_settings", {})
    
    total_invested = spot_settings.get("total_invested", 0.0)
    coins = spot_settings.get("coins", SPOT_DCA_COINS)
    dca_amount = spot_settings.get("dca_amount", SPOT_DCA_DEFAULT_AMOUNT)
    auto_dca = spot_settings.get("auto_dca", False)
    purchase_history = spot_settings.get("purchase_history", {})
    
    # Use provided account_type instead of auto-detecting
    account_display = ACCOUNT_DISPLAY_NAMES.get(account_type, account_type.capitalize())
    
    holdings_value = 0.0
    holdings_lines = []
    
    try:
        balances = await fetch_spot_balance(uid, account_type=account_type)
        
        for coin in coins:
            if coin in balances and balances[coin] > 0:
                symbol = f"{coin}USDT"
                ticker = await get_spot_ticker(uid, symbol, account_type=account_type)
                if ticker:
                    price = float(ticker.get("lastPrice", 0))
                    qty = balances[coin]
                    value = qty * price
                    holdings_value += value
                    
                    # Calculate PnL per coin using purchase history
                    coin_history = purchase_history.get(coin, {})
                    avg_price = coin_history.get("avg_price", 0)
                    total_cost = coin_history.get("total_cost", 0)
                    
                    if avg_price > 0:
                        # PnL = current value - cost basis (proportional to held qty)
                        pnl = value - (qty * avg_price)
                        pnl_sign = "+" if pnl >= 0 else ""
                        pnl_emoji = "🟢" if pnl >= 0 else "🔴"
                        holdings_lines.append(f"├─ {coin}: {qty:.8g} ≈ ${value:.2f} {pnl_emoji} {pnl_sign}${pnl:.2f}")
                    elif total_invested > 0 and holdings_value > 0:
                        # Fallback: estimate cost proportionally from total invested
                        coin_share = value / holdings_value if holdings_value > 0 else 0
                        estimated_cost = total_invested * coin_share
                        pnl = value - estimated_cost
                        pnl_sign = "+" if pnl >= 0 else ""
                        pnl_emoji = "🟢" if pnl >= 0 else "🔴"
                        holdings_lines.append(f"├─ {coin}: {qty:.8g} ≈ ${value:.2f} {pnl_emoji} ~{pnl_sign}${pnl:.2f}")
                    else:
                        holdings_lines.append(f"├─ {coin}: {qty:.8g} ≈ ${value:.2f}")
    except Exception as e:
        logger.error(f"Error getting spot holdings for stats: {e}")
        holdings_lines.append("├─ Unable to fetch holdings")
    
    # Calculate P/L
    pnl = holdings_value - total_invested if total_invested > 0 else 0
    pnl_pct = (pnl / total_invested * 100) if total_invested > 0 else 0
    pnl_sign = "+" if pnl >= 0 else ""
    pnl_emoji = "📈" if pnl >= 0 else "📉"
    
    coins_str = ", ".join(coins) if isinstance(coins, list) else str(coins)
    auto_status = "✅" if auto_dca else "❌"
    
    lines = [
        f"💹 *{t.get('stats_spot_title', 'Spot DCA Statistics')}* {account_display}",
        f"└ {t.get('stats_period', 'Period')}: 📅 {period_label}",
        "",
        f"*{t.get('stats_spot_config', 'Configuration')}*",
        f"├─ 🪙 {t.get('spot_coins_label', 'Coins')}: {coins_str}",
        f"├─ 💵 {t.get('spot_dca_amount_label', 'DCA Amount')}: ${dca_amount:.2f}",
        f"└─ 🔄 {t.get('spot_auto_dca_label', 'Auto DCA')}: {auto_status}",
        "",
        f"*{t.get('stats_spot_holdings', 'Holdings')}*",
    ]
    
    if holdings_lines:
        lines.extend(holdings_lines)
    else:
        lines.append("├─ No holdings")
    
    lines.extend([
        "",
        f"*{t.get('stats_spot_summary', 'Summary')}*",
        f"├─ {t.get('spot_total_invested', 'Total Invested')}: ${total_invested:.2f}",
        f"├─ {t.get('stats_spot_current_value', 'Current Value')}: ${holdings_value:.2f}",
        f"└─ {pnl_emoji} {t.get('stats_total_pnl', 'P/L')}: {pnl_sign}${pnl:.2f} ({pnl_sign}{pnl_pct:.1f}%)",
    ])
    
    return "\n".join(lines)


@require_access
@with_texts
@log_calls
async def cmd_set_percent(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['mode'] = 'set_percent'
    await update.message.reply_text(ctx.t['set_percent_prompt'])


@require_access
@with_texts
@log_calls
async def cmd_toggle_limit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cfg = get_user_config(uid)
    new = not bool(cfg.get("limit_enabled", 0))
    set_user_field(uid, "limit_enabled", int(new))
    await update.message.reply_text(ctx.t['limit_only_toggled'].format(state=ctx.t['status_enabled'] if new else ctx.t['status_disabled']),
        reply_markup=main_menu_keyboard(ctx, update=update)
)

@require_access
@with_texts
@log_calls
async def cmd_indicators(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1. RSI + BB",     url="https://ru.tradingview.com/script/SCDoLiri-elcaro-bollinger-rsi-win-strategy-v0-1/")],
        [InlineKeyboardButton("2. Trading Chaos",url="https://ru.tradingview.com/script/iRZwhDIu-trading-chaos-strategy-risk-management-strict/")],
        [InlineKeyboardButton("3. Adaptive Trend", url="https://ru.tradingview.com/script/TMWJzpka-adaptivnyj-kanal-regressiya-ehkstremumy/")],
        [InlineKeyboardButton("4. Dynamic Regression", url="https://ru.tradingview.com/script/CnqpAgCb-adaptivnyj-regressionnyj-kanal-v2/")],
    ]
    await ctx.bot.send_message(
        chat_id=update.effective_chat.id,
        text=ctx.t['indicators_header'],
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

@with_texts
@log_calls
async def cmd_support(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(ctx.t['support_button'], url="https://t.me/elcaronosam")]
    ]
    await ctx.bot.send_message(
        chat_id=update.effective_chat.id,
        text=ctx.t['support_prompt'],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@log_calls
async def normalize_qty_price(
    user_id: int,
    symbol: str,
    order_type: str,       
    qty: float,
    price: float | None = None,
    account_type: str = None
) -> tuple[str, str | None, float, float, float]:
    filt = await get_symbol_filters(user_id, symbol, account_type=account_type)
    min_qty   = float(filt["minQty"])
    step_qty  = float(filt["qtyStep"])
    tick_size = float(filt["tickSize"])
    min_price = float(filt["minPrice"])

    inst = await _bybit_request(
        user_id, "GET", "/v5/market/instruments-info",
        params={"category": "linear", "symbol": symbol},
        account_type=account_type
    )
    lot = inst["list"][0]["lotSizeFilter"]
    if order_type == "Market":
        raw_max = lot.get("maxMktOrderQty")
    else:
        raw_max = lot.get("maxOrderQty") or lot.get("maxMktOrderQty")
    max_qty = float(raw_max) if raw_max not in (None, "", 0, "0") else float("inf")

    q = quantize(qty, step_qty)
    if q < min_qty:
        q = min_qty

    q = min(q, max_qty)
    q = quantize(q, step_qty)
    if q < min_qty:
        q = min_qty

    qty_decimals   = _decimals_from_step(step_qty)
    price_decimals = _decimals_from_step(tick_size)
    qty_str = f"{q:.{qty_decimals}f}"

    price_str = None
    if order_type == "Limit":
        if price is None:
            raise ValueError("For Limit-order need price")
        px_q = quantize(float(price), tick_size)
        if px_q < min_price:
            raise ValueError(
                f"Price - min: {px_q:.{price_decimals}f} < {min_price:.{price_decimals}f}"
            )
        price_str = f"{px_q:.{price_decimals}f}"

    return qty_str, price_str, min_qty, max_qty, tick_size

@log_calls
async def get_symbol_filters(user_id: int, symbol: str, account_type: str = None) -> dict:
    """Get symbol trading filters with caching (1 hour TTL)."""
    now = time.time()
    
    # Check cache first - filters are same for all users
    if symbol in _symbol_filters_cache:
        ts, cached = _symbol_filters_cache[symbol]
        if now - ts < SYMBOL_FILTERS_CACHE_TTL:
            return cached
    
    res = await _bybit_request(user_id, "GET", "/v5/market/instruments-info", params={"category":"linear","symbol":symbol}, account_type=account_type)
    if not res.get("list"):
        raise ValueError(f"Symbol {symbol} not have")
    inst = res["list"][0]
    price_f = inst["priceFilter"]
    lot_f   = inst["lotSizeFilter"]
    filters = {
        "tickSize":      float(price_f["tickSize"]),
        "minPrice":      float(price_f["minPrice"]),
        "minQty":        float(lot_f["minOrderQty"]),
        "qtyStep":       float(lot_f["qtyStep"]),
    }
    # Store in cache
    _symbol_filters_cache[symbol] = (now, filters)
    return filters

@log_calls
async def place_limit_order(
    user_id: int,
    symbol: str,
    side: str,
    price: float,
    qty: float,
    account_type: str = None,
):
    filt = await get_symbol_filters(user_id, symbol, account_type=account_type)
    tick_size = filt["tickSize"]
    min_qty   = filt["minQty"]
    qty_step  = filt["qtyStep"]

    price_q = quantize(price, tick_size)
    price_decimals = _decimals_from_step(tick_size)
    if price_q < filt["minPrice"]:
        raise ValueError(
            f"Price - min: {price_q:.{price_decimals}f} < {filt['minPrice']:.{price_decimals}f}"
        )

    qty_q = quantize(qty, qty_step)
    if qty_q < min_qty:
        qty_q = min_qty

    inst = await _bybit_request(
        user_id, "GET", "/v5/market/instruments-info",
        params={"category": "linear", "symbol": symbol},
        account_type=account_type
    )
    lot = inst["list"][0]["lotSizeFilter"]
    max_qty_raw = lot.get("maxOrderQty") or lot.get("maxMktOrderQty")
    max_qty = float(max_qty_raw) if max_qty_raw not in (None, "", 0, "0") else float("inf")

    qty_q = min(qty_q, max_qty)
    qty_q = quantize(qty_q, qty_step)
    if qty_q < min_qty:
        qty_q = min_qty

    qty_decimals = _decimals_from_step(qty_step)
    qty_str   = f"{qty_q:.{qty_decimals}f}"
    price_str = f"{price_q:.{price_decimals}f}"

    order_body = {
        "category":    "linear",
        "symbol":      symbol,
        "side":        side,
        "orderType":   "Limit",
        "qty":         qty_str,
        "price":       price_str,
        "timeInForce": "GTC",
    }

    mode = await get_position_mode(user_id, symbol, account_type=account_type)
    order_body["positionIdx"] = position_idx_for(side, mode)

    try:
        res = await _bybit_request(user_id, "POST", "/v5/order/create", body=order_body, account_type=account_type)
    except RuntimeError as e:
        msg = str(e)

        if "insufficient" in msg.lower() or "balance" in msg.lower() or "110007" in msg or "ab not enough" in msg.lower():
            raise ValueError("INSUFFICIENT_BALANCE")

        if "position idx not match position mode" in msg.lower():
            alt_mode = "one_way" if mode == "hedge" else "hedge"
            order_body["positionIdx"] = position_idx_for(side, alt_mode)
            _position_mode_cache[(user_id, symbol)] = alt_mode
            logger.info(f"{symbol}: retry limit with alt position mode {alt_mode}")
            res = await _bybit_request(user_id, "POST", "/v5/order/create", body=order_body, account_type=account_type)
        elif "110013" in msg or "cannot set leverage" in msg.lower():
            logger.info(f"Leverage error on {symbol}, setting leverage=10 and retrying limit order")
            await set_leverage(user_id, symbol, leverage=10, account_type=account_type)
            res = await _bybit_request(user_id, "POST", "/v5/order/create", body=order_body, account_type=account_type)
        else:
            raise

    logger.info(f"✅ Limit order placed: {symbol} {side} {qty_q}@{price_q} [{account_type or 'auto'}]")
    return res


@log_calls
async def place_limit_order_all_accounts(
    user_id: int,
    symbol: str,
    side: str,
    price: float,
    qty: float,
    strategy: str = None,
) -> dict:
    """
    Place limit order on all active accounts based on strategy's trading_mode or global trading_mode.
    If trading_mode is 'both', places order on both demo and real accounts.
    Returns dict with results per account type.
    """
    if strategy:
        account_types = get_strategy_account_types(user_id, strategy)
    else:
        account_types = get_active_account_types(user_id)
    
    if not account_types:
        raise ValueError("No API credentials configured")
    
    results = {}
    errors = []
    
    for acc_type in account_types:
        try:
            res = await place_limit_order(user_id, symbol, side, price, qty, account_type=acc_type)
            results[acc_type] = {"success": True, "result": res}
            logger.info(f"✅ [{acc_type.upper()}] Limit order placed: {symbol} {side}")
        except Exception as e:
            results[acc_type] = {"success": False, "error": str(e)}
            errors.append(f"[{acc_type.upper()}] {str(e)}")
            logger.error(f"❌ [{acc_type.upper()}] Limit order failed for {symbol}: {e}")
    
    if errors and not any(r["success"] for r in results.values()):
        raise RuntimeError(f"All orders failed: {'; '.join(errors)}")
    
    return results


@log_calls
async def place_limit_order_with_strategy(
    user_id: int,
    symbol: str,
    side: str,
    price: float,
    qty: float,
    signal_id: int,
    strategy: str,
) -> dict:
    """
    Place limit order on all accounts for strategy and add to pending_limit_orders for each.
    Returns dict with results per account type.
    """
    account_types = get_strategy_account_types(user_id, strategy)
    
    if not account_types:
        raise ValueError("No API credentials configured")
    
    results = {}
    errors = []
    created_ts = int(time.time() * 1000)
    
    for acc_type in account_types:
        try:
            res = await place_limit_order(user_id, symbol, side, price, qty, account_type=acc_type)
            order_id = _normalize_order_id(res)
            tif = str(res.get("timeInForce") or "GTC")
            
            # Add to pending_limit_orders with account_type
            add_pending_limit_order(
                user_id=user_id,
                order_id=order_id,
                symbol=symbol,
                side=side,
                qty=qty,
                price=price,
                signal_id=signal_id,
                created_ts=created_ts,
                time_in_force=tif,
                strategy=strategy,
                account_type=acc_type,
            )
            
            results[acc_type] = {"success": True, "result": res, "order_id": order_id}
            logger.info(f"✅ [{acc_type.upper()}] Limit order placed: {symbol} {side} @ {price}")
        except Exception as e:
            results[acc_type] = {"success": False, "error": str(e)}
            errors.append(f"[{acc_type.upper()}] {str(e)}")
            logger.error(f"❌ [{acc_type.upper()}] Limit order failed for {symbol}: {e}")
    
    if errors and not any(r["success"] for r in results.values()):
        raise RuntimeError(f"All orders failed: {'; '.join(errors)}")
    
    return results


@log_calls
async def place_ladder_limit_orders(
    user_id: int,
    symbol: str,
    side: str,
    entry_price: float,
    strategy: str,
    ctx=None
) -> dict:
    """
    Place ladder limit orders below (for LONG) or above (for SHORT) entry price.
    Returns dict with results for each ladder order.
    
    Settings from user config:
    - limit_ladder_enabled: bool
    - limit_ladder_count: int (1-5)
    - limit_ladder_settings: list of {pct_from_entry, pct_of_deposit}
    """
    cfg = get_user_config(user_id)
    
    if not cfg.get('limit_ladder_enabled', 0):
        return {"skipped": True, "reason": "Ladder disabled"}
    
    ladder_count = cfg.get('limit_ladder_count', 3)
    ladder_settings = cfg.get('limit_ladder_settings', [])
    
    # Default settings if empty
    if not ladder_settings:
        ladder_settings = [
            {"pct_from_entry": 1.0, "pct_of_deposit": 5.0},
            {"pct_from_entry": 2.0, "pct_of_deposit": 7.0},
            {"pct_from_entry": 3.0, "pct_of_deposit": 10.0},
        ]
    
    # Get balance for calculating qty
    account_types = get_strategy_account_types(user_id, strategy)
    if not account_types:
        return {"skipped": True, "reason": "No accounts configured"}
    
    results = {}
    placed_count = 0
    
    for i in range(min(ladder_count, len(ladder_settings))):
        leg = ladder_settings[i]
        pct_from_entry = leg.get('pct_from_entry', 1.0 + i)
        pct_of_deposit = leg.get('pct_of_deposit', 5.0 + i * 2)
        
        # Calculate price: below entry for LONG, above entry for SHORT
        if side == "Buy":
            ladder_price = entry_price * (1 - pct_from_entry / 100)
        else:
            ladder_price = entry_price * (1 + pct_from_entry / 100)
        
        try:
            # Get balance and calculate qty for this ladder order
            for acc_type in account_types:
                balance = await fetch_usdt_balance(user_id, account_type=acc_type)
                qty_usdt = balance * (pct_of_deposit / 100)
                qty = qty_usdt / ladder_price
                
                if qty <= 0:
                    continue
                
                res = await place_limit_order(user_id, symbol, side, ladder_price, qty, account_type=acc_type)
                order_id = _normalize_order_id(res)
                
                # Add to pending_limit_orders
                created_ts = int(time.time() * 1000)
                add_pending_limit_order(
                    user_id=user_id,
                    order_id=order_id,
                    symbol=symbol,
                    side=side,
                    qty=qty,
                    price=ladder_price,
                    signal_id=0,
                    created_ts=created_ts,
                    time_in_force="GTC",
                    strategy=f"{strategy}_ladder_{i+1}",
                    account_type=acc_type,
                )
                
                results[f"ladder_{i+1}_{acc_type}"] = {
                    "success": True, 
                    "price": ladder_price, 
                    "qty": qty, 
                    "pct_from_entry": pct_from_entry,
                    "pct_of_deposit": pct_of_deposit,
                    "order_id": order_id
                }
                placed_count += 1
                logger.info(f"📉 Ladder {i+1} [{acc_type}]: {symbol} {side} @ {ladder_price:.6f} qty={qty:.4f}")
                
        except Exception as e:
            results[f"ladder_{i+1}"] = {"success": False, "error": str(e)}
            logger.error(f"❌ Ladder {i+1} failed: {e}")
    
    # Notify user if context available
    if ctx and placed_count > 0:
        t = ctx.t if hasattr(ctx, 't') else {}
        try:
            await ctx.bot.send_message(
                user_id,
                t.get('ladder_orders_placed', f"📉 Placed {placed_count} ladder limit orders for {symbol}")
                .format(count=placed_count, symbol=symbol),
                parse_mode="Markdown"
            )
        except Exception:
            pass
    
    results["placed_count"] = placed_count
    return results


@log_calls
async def calc_qty(
    user_id: int,
    symbol: str,
    price: float,
    risk_pct: float,
    sl_pct: float,
    account_type: str = None
) -> float:
    balance = await fetch_usdt_balance(user_id, account_type=account_type)
    logger.info(f"[calc_qty] uid={user_id} symbol={symbol} account_type={account_type} balance={balance:.2f}")
    if balance <= 0:
        raise ValueError(f"Don't have USDT (balance={balance}, account_type={account_type})")
    risk_usdt = balance * (risk_pct / 100)
    price_move = price * (sl_pct / 100)
    if price_move <= 0:
        raise ValueError("Wrong sl_pct for price_move")

    raw_qty = risk_usdt / price_move

    inst = await _bybit_request(
        user_id, "GET", "/v5/market/instruments-info",
        params={"category":"linear", "symbol": symbol},
        account_type=account_type
    )
    lot      = inst["list"][0]["lotSizeFilter"]
    min_qty  = float(lot["minOrderQty"])
    step_qty = float(lot["qtyStep"])
    raw_max  = lot.get("maxMktOrderQty")
    max_qty  = float(raw_max) if raw_max not in (None, "", 0, "0") else float("inf")

    qty = math.floor(raw_qty / step_qty) * step_qty
    qty = max(min_qty, qty)
    qty = min(max_qty, qty)

    if qty < min_qty:
        raise RuntimeError(f"qty < minOrderQty={min_qty}")
    if raw_qty > max_qty:
        logger.warning(
            f"raw_qty={raw_qty:.2f} > maxMktOrderQty={max_qty}, используем {qty:.2f}"
        )

    return qty

NUM = r'([0-9]+(?:[.,][0-9]+)?)'

def _tof(s: str) -> float:
    return float(s.replace(',', '.'))

def _to_mln(v: float, u: str) -> float:
    u = u.upper()
    if u == 'M':
        return round(v, 2)
    if u == 'K':
        return round(v / 1000.0, 2)
    return round(v, 2)

def _to_mln_ext(v: float, u: str, *, bare_is_units: bool = False) -> float:
    u = (u or '').strip().upper()
    if u == 'B':
        return round(v * 1000.0, 4)
    if u == 'M':
        return round(v, 4)
    if u == 'K':
        return round(v / 1000.0, 4)
    return round(v / 1_000_000.0, 6) if bare_is_units else round(v, 2)

BITK_RE_HDR     = re.compile(r'^\s*[^\w\s]?\s*DROP\s+CATCH\b', re.I | re.M)
BITK_RE_BTCLINE = re.compile(r'^\s*BTC\s*[:=]\s*[^ \t\r\n]+', re.I | re.M)
BITK_RE_TAG     = re.compile(r'\bTIGHTBTC\b', re.I)
BITK_RE_SYMBOL  = re.compile(r'\b([A-Z0-9]{2,}USDT)\b')
BITK_RE_SIDE    = re.compile(r'\b(LONG|SHORT)\b', re.I)
BITK_RE_PRICE   = re.compile(r'\b(?:Price|Px|Entry)\b\s*[:=]\s*' + NUM, re.I)

def is_bitk_signal(text: str) -> bool:
    return bool(BITK_RE_HDR.search(text) or BITK_RE_BTCLINE.search(text) or BITK_RE_TAG.search(text))

def parse_bitk_signal(text: str) -> dict | None:
    if not is_bitk_signal(text):
        return None
    m_sym = BITK_RE_SYMBOL.search(text)
    m_side = BITK_RE_SIDE.search(text)
    m_px = BITK_RE_PRICE.search(text)
    if not (m_sym and m_side and m_px):
        return None
    symbol = m_sym.group(1).upper()
    side = "Buy" if m_side.group(1).upper() == "LONG" else "Sell"
    price = _tof(m_px.group(1))
    return {"symbol": symbol, "side": side, "price": price}

# --- Scalper (DropsBot) parser ---
SCALPER_RE_HDR = re.compile(r'DropsBot\s*[—–-]\s*Bybit\s+linear', re.I)
SCALPER_RE_SYMBOL = re.compile(r'\[([A-Z0-9]+USDT)\]')
SCALPER_RE_SIDE = re.compile(r'\b(?:BOX\s+)?(LONG|SHORT)\b', re.I)
SCALPER_RE_PRICE = re.compile(r'\bPrice\s*[:=]\s*' + NUM, re.I)

def is_scalper_signal(text: str) -> bool:
    return bool(SCALPER_RE_HDR.search(text))

def parse_scalper_signal(text: str) -> dict | None:
    """
    Парсит сигнал от DropsBot Scalper.
    Пример: 📉 DropsBot — Bybit linear
            [AXLUSDT] BOX LONG • DD -2.47% inside the box (ΔVol ok)
            Price: 0.1384
    """
    if not is_scalper_signal(text):
        return None
    m_sym = SCALPER_RE_SYMBOL.search(text)
    m_side = SCALPER_RE_SIDE.search(text)
    m_px = SCALPER_RE_PRICE.search(text)
    if not (m_sym and m_side and m_px):
        return None
    symbol = m_sym.group(1).upper()
    side = "Buy" if m_side.group(1).upper() == "LONG" else "Sell"
    price = _tof(m_px.group(1))
    return {"symbol": symbol, "side": side, "price": price}

# --- Elcaro parser (new format) ---
# Header: "Elcaro" on first line (optional - can detect by structure)
ELCARO_RE_HDR = re.compile(r'^Elcaro\s*$', re.I | re.M)
# Symbol line: 🔔 FILUSDT 📉 SHORT or 🔔 BTCUSDT 📈 LONG or 🔔 XRPUSDT 📉 SHORT 🟢⚪️⚪️
# More flexible pattern - allows emojis and extra characters between symbol and side
ELCARO_RE_MAIN = re.compile(r'🔔\s*([A-Z0-9]+(?:USDT|USDC)?)\s*[📉📈🔻🔺]*\s*(LONG|SHORT)', re.I)
# Timeframe and leverage: ⏱️ 60 | 🎚 68  OR  ⏱️ 5 | 🎚 62
ELCARO_RE_TF_LEV = re.compile(r'⏱️\s*(\d+)\s*\|\s*🎚\s*(\d+)', re.I)
# Entry price: 💰 Entry: 1.253000 (also handle commas in prices)
ELCARO_RE_ENTRY = re.compile(r'💰\s*Entry\s*[:：]\s*' + NUM, re.I)
# SL: 🛑 SL: 1.281500 (2.27%) [ATR] - make the bracket part optional
ELCARO_RE_SL = re.compile(r'🛑\s*SL\s*[:：]\s*' + NUM + r'\s*\((' + NUM + r')%\)', re.I)
# TP: 🎯 TP: 1.215000 (3.03%) [AGG] - make the bracket part optional
ELCARO_RE_TP = re.compile(r'🎯\s*TP\s*[:：]\s*' + NUM + r'\s*\((' + NUM + r')%\)', re.I)
# ATR line: 📉 ATR: 14 | ×1.5 | Trigger: 30%
# Note: NUM already has capture group, so we use indices 1, 2, 4 for periods, mult, trigger
ELCARO_RE_ATR = re.compile(r'📉\s*ATR\s*[:：]\s*(\d+)\s*\|\s*[×x]' + NUM + r'\s*\|\s*Trigger\s*[:：]\s*' + NUM + r'%', re.I)
# RR line: 📊 RR: 5.0:1 | ATR Exit: ✅
ELCARO_RE_RR = re.compile(r'📊\s*RR\s*[:：]\s*' + NUM + r'\s*:\s*1', re.I)
# ATR Exit marker: ATR Exit: ✅
ELCARO_RE_ATR_EXIT = re.compile(r'ATR\s*Exit\s*[:：]\s*[✅✓]', re.I)

def is_elcaro_signal(text: str) -> bool:
    """Check if message is Elcaro signal - by header OR by structure."""
    # Has explicit header
    if ELCARO_RE_HDR.search(text):
        return True
    # Detect by structure: has 🔔 SYMBOL, Entry, SL with %, TP with %
    # ATR Exit marker is optional now (more flexible detection)
    has_main = bool(ELCARO_RE_MAIN.search(text))
    has_entry = bool(ELCARO_RE_ENTRY.search(text))
    has_sl = bool(ELCARO_RE_SL.search(text))
    has_tp = bool(ELCARO_RE_TP.search(text))
    has_atr = bool(ELCARO_RE_ATR.search(text))
    has_atr_exit = bool(ELCARO_RE_ATR_EXIT.search(text))
    has_tf_lev = bool(ELCARO_RE_TF_LEV.search(text))
    
    # Core detection: 🔔 SYMBOL + Entry + SL% + TP%
    core_match = has_main and has_entry and has_sl and has_tp
    
    # Additional indicators that strengthen the match
    has_additional = has_atr_exit or has_atr or has_tf_lev
    
    # If core match and at least one additional indicator, it's Elcaro
    return core_match and has_additional

def parse_elcaro_signal(text: str) -> dict | None:
    """
    Парсит сигнал от Elcaro (новый формат с ATR параметрами).
    
    Формат:
        🔔 XRPUSDT 📉 SHORT 🟢⚪️⚪️
        ⏱️ 5 | 🎚 62
        
        💰 Entry: 1.858300
        🛑 SL: 1.865350 (0.38%) [OB]
        🎯 TP: 1.848900 (0.51%) [AGG]
        
        📊 RR: 5.0:1 | ATR Exit: ✅
        📉 ATR: 14 | ×1.0 | Trigger: 30%
    
    Возвращает словарь со всеми параметрами для торговли.
    """
    if not is_elcaro_signal(text):
        return None
    
    m_main = ELCARO_RE_MAIN.search(text)
    m_entry = ELCARO_RE_ENTRY.search(text)
    
    if not (m_main and m_entry):
        return None
    
    symbol = m_main.group(1).upper()
    side = "Buy" if m_main.group(2).upper() == "LONG" else "Sell"
    entry_price = _tof(m_entry.group(1))
    
    result = {
        "symbol": symbol,
        "side": side,
        "price": entry_price,
        "entry": entry_price,  # Explicit entry price for limit orders
        "elcaro_mode": True,  # Flag for special Elcaro handling
    }
    
    # Timeframe and leverage
    m_tf_lev = ELCARO_RE_TF_LEV.search(text)
    if m_tf_lev:
        result["timeframe"] = m_tf_lev.group(1) + "m"  # e.g. "60m"
        result["leverage"] = int(m_tf_lev.group(2))
    
    # SL with percentage
    m_sl = ELCARO_RE_SL.search(text)
    if m_sl:
        result["sl"] = _tof(m_sl.group(1))
        result["sl_pct"] = _tof(m_sl.group(2))
    
    # TP with percentage  
    m_tp = ELCARO_RE_TP.search(text)
    if m_tp:
        result["tp"] = _tof(m_tp.group(1))
        result["tp_pct"] = _tof(m_tp.group(2))
    
    # ATR parameters: periods, multiplier, trigger
    m_atr = ELCARO_RE_ATR.search(text)
    if m_atr:
        result["atr_periods"] = int(m_atr.group(1))
        result["atr_multiplier"] = _tof(m_atr.group(2))
        result["atr_trigger_pct"] = _tof(m_atr.group(3))
    
    # RR
    m_rr = ELCARO_RE_RR.search(text)
    if m_rr:
        result["rr"] = _tof(m_rr.group(1))
    
    return result


# --- Fibonacci Extension Strategy Parser ---
# Header: 📊 FIBONACCI EXTENSION STRATEGY
FIBO_RE_HDR = re.compile(r'📊\s*FIBONACCI\s+EXTENSION\s+STRATEGY', re.I)
# Symbol: 🪙 BTCUSDT | ... (price is optional, can be '—' or empty)
FIBO_RE_SYMBOL = re.compile(r'🪙\s*([A-Z0-9]+USDT)', re.I)
# Optional price after symbol: | $97,500.00 or | 97500.00
FIBO_RE_SYMBOL_PRICE = re.compile(r'🪙\s*[A-Z0-9]+USDT\s*\|\s*[$]?([\d,]+(?:\.\d+)?)', re.I)
# Direction: 📈 LONG or 📉 SHORT
FIBO_RE_SIDE = re.compile(r'[📈📉]\s*(LONG|SHORT)', re.I)
# Entry Zone: 🎯 Entry Zone: 96,800.0000 – 97,200.0000
FIBO_RE_ENTRY = re.compile(r'🎯\s*Entry\s+Zone\s*[:：]\s*([\d,]+(?:\.\d+)?)\s*[–-]\s*([\d,]+(?:\.\d+)?)', re.I)
# Stop Loss: 🛑 Stop Loss: 95,500.0000
FIBO_RE_SL = re.compile(r'🛑\s*Stop\s+Loss\s*[:：]\s*([\d,]+(?:\.\d+)?)', re.I)
# Target: ✅ Target 1: 99,000.0000
FIBO_RE_TP = re.compile(r'✅\s*Target\s*\d*\s*[:：]\s*([\d,]+(?:\.\d+)?)', re.I)
# Trigger info: ⚡ Trigger: Spring detected + Price in 141.4%-161.8% zone
FIBO_RE_TRIGGER = re.compile(r'⚡\s*Trigger\s*[:：]\s*(.+)', re.I)
# Quality: 🟢 Quality: A (85/100) or 🟡 Quality: B (64/100)
FIBO_RE_QUALITY = re.compile(r'[🟢🟡🟠]\s*Quality\s*[:：]\s*([A-Z])\s*\((\d+)/\d+\)', re.I)


def is_fibonacci_signal(text: str) -> bool:
    """Check if message is Fibonacci Extension signal."""
    return bool(FIBO_RE_HDR.search(text))


def parse_fibonacci_signal(text: str) -> dict | None:
    """
    Parse Fibonacci Extension strategy signal.
    
    Format:
        📊 FIBONACCI EXTENSION STRATEGY

        🪙 BTCUSDT | $97,500.00 (price can be '—' or missing)
        📈 LONG

        🎯 Entry Zone: 96,800.0000 – 97,200.0000
        🛑 Stop Loss: 95,500.0000
        ✅ Target 1: 99,000.0000

        ⚡ Trigger: Price in 141.4%-161.8% zone
        🟢 Quality: A (85/100)
    
    Returns dict with all trading parameters.
    """
    if not is_fibonacci_signal(text):
        return None
    
    m_symbol = FIBO_RE_SYMBOL.search(text)
    m_side = FIBO_RE_SIDE.search(text)
    
    if not (m_symbol and m_side):
        return None
    
    symbol = m_symbol.group(1).upper()
    side = "Buy" if m_side.group(1).upper() == "LONG" else "Sell"
    
    # Try to get price from header (optional)
    m_price = FIBO_RE_SYMBOL_PRICE.search(text)
    current_price = None
    if m_price:
        current_price = _tof(m_price.group(1).replace(",", ""))
    
    result = {
        "symbol": symbol,
        "side": side,
        "fibonacci_mode": True,  # Flag for special Fibonacci handling
    }
    
    # Entry zone (for limit order range)
    m_entry = FIBO_RE_ENTRY.search(text)
    if m_entry:
        entry_low = _tof(m_entry.group(1).replace(",", ""))
        entry_high = _tof(m_entry.group(2).replace(",", ""))
        result["entry_low"] = entry_low
        result["entry_high"] = entry_high
        result["entry"] = (entry_low + entry_high) / 2  # Mid point for entry
        # If no price in header, use entry mid point
        if current_price is None:
            current_price = result["entry"]
    
    result["price"] = current_price
    
    # Stop Loss
    m_sl = FIBO_RE_SL.search(text)
    if m_sl:
        sl_price = _tof(m_sl.group(1).replace(",", ""))
        result["sl"] = sl_price
        # Calculate SL percentage
        if result.get("entry"):
            sl_pct = abs(result["entry"] - sl_price) / result["entry"] * 100
            result["sl_pct"] = round(sl_pct, 2)
    
    # Target (TP)
    m_tp = FIBO_RE_TP.search(text)
    if m_tp:
        tp_price = _tof(m_tp.group(1).replace(",", ""))
        result["tp"] = tp_price
        # Calculate TP percentage
        if result.get("entry"):
            tp_pct = abs(tp_price - result["entry"]) / result["entry"] * 100
            result["tp_pct"] = round(tp_pct, 2)
    
    # Trigger info
    m_trigger = FIBO_RE_TRIGGER.search(text)
    if m_trigger:
        result["trigger_info"] = m_trigger.group(1).strip()
    
    # Quality score
    m_quality = FIBO_RE_QUALITY.search(text)
    if m_quality:
        result["quality_grade"] = m_quality.group(1)
        result["quality_score"] = int(m_quality.group(2))
    
    return result


def parse_signal(txt: str) -> dict:
    tf_m    = re.search(r'(?:^|\n)\s*[^A-Za-z0-9_]*(?:TF|Timeframe)\s*[:=：]\s*([0-9]+[mhdD])', txt, re.I)
    side_m  = re.search(r'(?:^|\n).*?\b(LONG|SHORT|BUY|SELL|UP|DOWN)\b', txt, re.I)
    sym_m   = re.search(r'\b([A-Z0-9]{2,}USDT)\b', txt, re.I)
    price_m = re.search(r'(?:^|\n)\s*[^A-Za-z0-9_]*(?:Price|Px|Entry)\s*[:=]\s*' + NUM, txt, re.I)

    if not price_m and sym_m:
        start = max(0, sym_m.start() - 160)
        window = txt[start:sym_m.end() + 320]
        cand = re.findall(NUM, window)
        cand = [c for c in cand if ('.' in c or ',' in c)]
        if cand:
            class _Dummy:
                def group(self, i): return cand[0]
            price_m = _Dummy()

    oi_prev = oi_now = oi_chg = None
    
    # NEW FORMAT: PRE-ALERT signals with "OI Total: 74.88M (+794.75%, z=295.1)"
    # Format: OI Total: VALUE (+CHANGE%, z=SCORE)
    prealert_oi_match = re.search(
        r'OI\s+Total\s*:\s*([0-9]+(?:[.,][0-9]+)?)\s*([kKmMbB]?)\s*\(\s*([+\-]?[0-9]+(?:[.,][0-9]+)?)%',
        txt
    )
    if prealert_oi_match:
        # Parse OI value and change from PRE-ALERT format
        oi_val = _tof(prealert_oi_match.group(1))
        oi_unit = (prealert_oi_match.group(2) or '').upper()
        oi_chg = _tof(prealert_oi_match.group(3))
        
        oi_now = _to_mln_ext(oi_val, oi_unit, bare_is_units=True)
        # Calculate oi_prev from oi_now and oi_chg
        if oi_chg and abs(oi_chg) > 0.01:
            oi_prev = oi_now / (1 + oi_chg / 100)
        else:
            oi_prev = oi_now
        logger.debug(f"PRE-ALERT OI parsed: now={oi_now}M, prev={oi_prev:.4f}M, chg={oi_chg}%")
    else:
        # LEGACY FORMAT: Two separate OI lines
        oi_lines = [m.group(0) for m in re.finditer(
            r'(?im)^[^\n\r]*(?:\bOI\b|\bOpen\s+Interest\b)[^\n\r]*$', txt)]

        def _oi(line: str):
            norm = line.replace('\u00A0', ' ').replace('\u202F', ' ')
            m = re.search(r'([0-9]+(?:[.,][0-9]+)?)\s*([kKmMbB]?)', norm)
            if not m:
                return (None, None)
            v  = _tof(m.group(1))
            su = (m.group(2) or '').upper()  
            return (v, su or '')

        if oi_lines:
            v, u = _oi(oi_lines[0])
            if v is not None:
                oi_prev = _to_mln_ext(v, u, bare_is_units=True)
        if len(oi_lines) >= 2:
            v, u = _oi(oi_lines[1])
            if v is not None:
                oi_now = _to_mln_ext(v, u, bare_is_units=True)
        if oi_prev not in (None, 0) and oi_now is not None:
            oi_chg = round((oi_now - oi_prev) / oi_prev * 100, 2)

    vol_from = vol_to = None
    arrow_re = r'(?:→|->|=>)'
    vol_line = None
    for ln in txt.splitlines():
        if re.search(r'\b(Vol|Volume)\b', ln, re.I) or re.search(arrow_re, ln):
            if re.search(NUM + r'\s*([MK]).+?' + arrow_re + r'.+?' + NUM + r'\s*([MK])', ln):
                vol_line = ln
                break
    if vol_line:
        m = re.search(NUM + r'\s*([MK]).+?' + arrow_re + r'.+?' + NUM + r'\s*([MK])', vol_line)
        if m:
            v1, u1, v2, u2 = m.group(1), m.group(2), m.group(3), m.group(4)
            vol_from = _to_mln(_tof(v1), u1)
            vol_to   = _to_mln(_tof(v2), u2)

    price_chg_m = re.search(r'([+\-]?[0-9]+(?:[.,][0-9]+)?)\s*%', txt)
    vol_delta_m = re.search(r'\bV[^:\n\r]*[:=]\s*([+\-]?[0-9]+(?:[.,][0-9]+)?)', txt, re.I)
    rsi_m       = re.search(r'\bRSI(?:\s*\(p?\d+\))?\s*[:=]?\s*' + NUM, txt, re.I)

    bb_hi = bb_lo = None
    bb_vals = []
    for ln in txt.splitlines():
        if 'BB' in ln:
            for m in re.finditer(NUM, ln):
                bb_vals.append(_tof(m.group(1)))
    if bb_vals:
        bb_hi = max(bb_vals)
        bb_lo = min(bb_vals)

    return {
        "tf":         tf_m.group(1)            if tf_m    else None,
        "side":       side_m.group(1).upper()  if side_m  else None,
        "symbol":     sym_m.group(1).upper()   if sym_m   else None,
        "price":      _tof(price_m.group(1))   if price_m else None,
        "oi_prev":    oi_prev,
        "oi_now":     oi_now,
        "oi_chg":     oi_chg,
        "vol_from":   vol_from,
        "vol_to":     vol_to,
        "price_chg":  _tof(price_chg_m.group(1)) if price_chg_m else None,
        "vol_delta":  _tof(vol_delta_m.group(1)) if vol_delta_m else None,
        "rsi":        _tof(rsi_m.group(1))       if rsi_m else None,
        "bb_hi":      bb_hi,
        "bb_lo":      bb_lo,
    }

@log_calls
async def on_channel_post(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    logger.info(f"📨 Received channel post from chat_id={update.channel_post.chat_id if update.channel_post else 'None'}")
    try:
        ch_id = update.channel_post.chat_id
    except Exception:
        logger.warning("Channel post has no chat_id")
        return
    if SIGNAL_CHANNEL_IDS and ch_id not in SIGNAL_CHANNEL_IDS:
        logger.debug(f"Skip channel {ch_id} (not in allowlist)")
        return

    txt = (update.channel_post.text or update.channel_post.caption or "")
    logger.info(f"📝 Channel post text (first 200 chars): {txt[:200]!r}")
    if not txt.strip():
        logger.warning("Channel post has empty text/caption — skip")
        return

    parsed_bitk = parse_bitk_signal(txt)
    is_bitk = parsed_bitk is not None
    
    parsed_scalper = parse_scalper_signal(txt)
    is_scalper = parsed_scalper is not None
    
    parsed_elcaro = parse_elcaro_signal(txt)
    is_elcaro = parsed_elcaro is not None
    
    parsed_fibonacci = parse_fibonacci_signal(txt)
    is_fibonacci = parsed_fibonacci is not None
    
    logger.debug(f"Raw signal (bitk={is_bitk}, scalper={is_scalper}, elcaro={is_elcaro}, fibonacci={is_fibonacci}): {txt!r}")

    parsed = parse_signal(txt)
    
    # Override parsed with specific parser data to ensure symbol is saved correctly
    if is_bitk and parsed_bitk:
        parsed["symbol"] = parsed_bitk.get("symbol")
        parsed["side"] = parsed_bitk.get("side")
        parsed["price"] = parsed_bitk.get("price")
    elif is_scalper and parsed_scalper:
        parsed["symbol"] = parsed_scalper.get("symbol")
        parsed["side"] = parsed_scalper.get("side")
        parsed["price"] = parsed_scalper.get("price")
    elif is_elcaro and parsed_elcaro:
        parsed["symbol"] = parsed_elcaro.get("symbol")
        parsed["side"] = parsed_elcaro.get("side")
        parsed["price"] = parsed_elcaro.get("price")
    elif is_fibonacci and parsed_fibonacci:
        parsed["symbol"] = parsed_fibonacci.get("symbol")
        parsed["side"] = parsed_fibonacci.get("side")
        parsed["price"] = parsed_fibonacci.get("price")
    
    try:
        signal_id = db.add_signal(
            raw_message = txt,
            tf          = parsed.get("tf"),
            side        = parsed.get("side"),
            symbol      = parsed.get("symbol"),
            price       = parsed.get("price"),
            oi_prev     = parsed.get("oi_prev"),
            oi_now      = parsed.get("oi_now"),
            oi_chg      = parsed.get("oi_chg"),
            vol_from    = parsed.get("vol_from"),
            vol_to      = parsed.get("vol_to"),
            price_chg   = parsed.get("price_chg"),
            vol_delta   = parsed.get("vol_delta"),
            rsi         = parsed.get("rsi"),
            bb_hi       = parsed.get("bb_hi"),
            bb_lo       = parsed.get("bb_lo"),
        )
    except Exception as e:
        logger.error(f"add_signal failed: {e}", exc_info=True)
        signal_id = None

    timeframe = parsed.get("tf") or "24h"

    try:
        if is_bitk:
            symbol     = parsed_bitk["symbol"]
            side       = parsed_bitk["side"]
            spot_price = float(parsed_bitk["price"])
        elif is_scalper:
            symbol     = parsed_scalper["symbol"]
            side       = parsed_scalper["side"]
            spot_price = float(parsed_scalper["price"])
        elif is_elcaro:
            symbol     = parsed_elcaro["symbol"]
            side       = parsed_elcaro["side"]
            spot_price = float(parsed_elcaro["price"])
        elif is_fibonacci:
            symbol     = parsed_fibonacci["symbol"]
            side       = parsed_fibonacci["side"]
            spot_price = float(parsed_fibonacci["price"])
        else:
            side_txt = (parsed.get("side") or "").upper()
            if side_txt in ("LONG", "UP"):
                side = "Buy"
            elif side_txt in ("SHORT", "DOWN", "SELL"):
                side = "Sell"
            else:
                m_tr = re.search(r'\b(LONG|SHORT|UP|DOWN|BUY|SELL)\b', txt, re.I)
                if not m_tr:
                    logger.error(f"Side not found: {txt!r}")
                    return
                raw_side = m_tr.group(1).upper()
                side = "Buy" if raw_side in ("LONG", "UP", "BUY") else "Sell"

            symbol = (parsed.get("symbol") or "").upper()
            price  = parsed.get("price")
            if not symbol or price is None:
                m_sym = re.search(r'\b([A-Z0-9]+USDT)\b.*?(?:Price|Px|Entry)\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)', txt, re.I | re.S)
                if not m_sym:
                    logger.warning("Symbol/price not found — skip")
                    return
                symbol, price = m_sym.group(1).upper(), float(m_sym.group(2))
            spot_price = float(price)
    except Exception as e:
        logger.error(f"Parse symbol/side/price failed: {e}", exc_info=True)
        return

    if symbol in BLACKLIST:
        logger.info(f"Skipping blacklisted symbol: {symbol}")
        return

    rsi_val = parsed.get("rsi")
    bb_hi   = parsed.get("bb_hi")
    bb_lo   = parsed.get("bb_lo")
    oi_prev = parsed.get("oi_prev")
    oi_now  = parsed.get("oi_now")

    liq_price_buy  = round(spot_price * 0.98, 6)
    liq_price_sell = round(spot_price * 1.02, 6)

    for uid in get_all_users():
        try:
            if GLOBAL_PAUSED:
                continue

            cfg  = get_user_config(uid) or {}
            lang = cfg.get("lang", DEFAULT_LANG)
            t    = LANGS.get(lang, LANGS[DEFAULT_LANG])
            
            # Check if user has API keys configured - skip silently if not
            api_key, api_secret = get_user_credentials(uid)
            if not api_key or not api_secret:
                # User doesn't have API keys - skip without spamming logs
                continue

            # Check trading limits silently - no spam, just skip if at max
            can_trade, _ = await check_trading_limits_user(uid, t)
            if not can_trade:
                # Notify only once per hour
                if once_per((uid, "positions_limit", ""), 3600):
                    try:
                        await ctx.bot.send_message(
                            uid, 
                            t.get('max_positions_reached', "⚠️ Maximum positions reached. New signals will be skipped until a position closes.")
                        )
                    except:
                        pass
                continue

            existing_positions = await fetch_open_positions(uid)
            if any(p.get("symbol") == symbol for p in existing_positions):
                logger.debug(f"[{uid}] {symbol}: already has open position → skip")
                continue

            existing_orders = await fetch_open_orders(uid, symbol)
            if existing_orders:
                logger.debug(f"[{uid}] {symbol}: has active order(s) → skip")
                continue

            pending = get_pending_limit_orders(uid)
            if any(po.get("symbol") == symbol for po in pending):
                logger.debug(f"[{uid}] {symbol}: pending limit in DB → skip")
                continue

            # Global coins filter (used as fallback if strategy doesn't have own setting)
            global_coins_mode = cfg.get("coins", "ALL")
            global_coins_mode = global_coins_mode.upper() if isinstance(global_coins_mode, str) else "ALL"

            if not any(p.get("symbol") == symbol for p in existing_positions):
                reset_pyramid(uid, symbol)

            cnt = get_pyramid(uid, symbol)["count"]
            if cnt > 0:
                logger.debug(f"[{uid}] {symbol}: pyramid count={cnt} → skip")
                continue

            limit_enabled = bool(cfg.get("limit_enabled", 0))  # Legacy, kept for compatibility
            use_atr       = bool(cfg.get("use_atr", 0))

            rsi_bb_trigger  = (cfg.get("trade_rsi_bb", 0) and rsi_val is not None and bb_hi is not None and bb_lo is not None)
            bitk_trigger    = (cfg.get("trade_scryptomera", 0) and is_bitk)
            scalper_trigger = (cfg.get("trade_scalper", 0) and is_scalper)
            elcaro_trigger  = (cfg.get("trade_elcaro", 0) and is_elcaro)
            fibonacci_trigger = (cfg.get("trade_fibonacci", 0) and is_fibonacci)
            oi_trigger      = (cfg.get("trade_oi", 0) and oi_prev is not None and oi_now is not None)
            
            # Log strategy triggers for debugging
            if is_bitk:
                logger.info(f"[{uid}] Scryptomera signal detected: trade_scryptomera={cfg.get('trade_scryptomera', 0)}, bitk_trigger={bitk_trigger}, symbol={symbol}")
            if is_scalper:
                logger.info(f"[{uid}] Scalper signal detected: trade_scalper={cfg.get('trade_scalper', 0)}, scalper_trigger={scalper_trigger}, symbol={symbol}")
            if is_fibonacci:
                logger.info(f"[{uid}] Fibonacci signal detected: trade_fibonacci={cfg.get('trade_fibonacci', 0)}, fibonacci_trigger={fibonacci_trigger}")
            if oi_prev is not None and oi_now is not None:
                logger.info(f"[{uid}] OI signal detected: trade_oi={cfg.get('trade_oi', 0)}, oi_trigger={oi_trigger}, symbol={symbol}, oi_prev={oi_prev:.2f}M, oi_now={oi_now:.2f}M")

            # Get user's trading context for settings lookup
            user_context = get_user_trading_context(uid)
            ctx_exchange = user_context["exchange"]
            ctx_account_type = user_context["account_type"]

            # Helper to check coins filter for a strategy
            def check_coins_filter(strat_name: str) -> bool:
                strat_settings = db.get_strategy_settings(uid, strat_name, ctx_exchange, ctx_account_type)
                coins_group = strat_settings.get("coins_group") or global_coins_mode
                filter_fn = SYMBOL_FILTER.get(coins_group, SYMBOL_FILTER["ALL"])
                if not filter_fn(symbol):
                    logger.debug(f"[{uid}] {symbol}: filtered by {strat_name} coins group {coins_group}")
                    return False
                return True

            # Apply coins filter per strategy
            if rsi_bb_trigger and not check_coins_filter("rsi_bb"):
                rsi_bb_trigger = False
            if bitk_trigger and not check_coins_filter("scryptomera"):
                bitk_trigger = False
            if scalper_trigger and not check_coins_filter("scalper"):
                scalper_trigger = False
            if elcaro_trigger and not check_coins_filter("elcaro"):
                elcaro_trigger = False
            if fibonacci_trigger and not check_coins_filter("fibonacci"):
                fibonacci_trigger = False
            if oi_trigger and not check_coins_filter("oi"):
                oi_trigger = False

            # Check Scryptomera direction filter
            if bitk_trigger:
                scrypto_settings = db.get_strategy_settings(uid, "scryptomera", ctx_exchange, ctx_account_type)
                scrypto_direction = scrypto_settings.get("direction", "all")
                signal_direction = "long" if side == "Buy" else "short"
                logger.info(f"[{uid}] Scryptomera direction check: signal={signal_direction}, allowed={scrypto_direction}")
                
                if scrypto_direction != "all" and scrypto_direction != signal_direction:
                    logger.info(f"[{uid}] {symbol}: Scryptomera direction filter - signal={signal_direction}, allowed={scrypto_direction} → skip")
                    bitk_trigger = False
                else:
                    logger.info(f"[{uid}] Scryptomera direction OK, proceeding with {symbol}")

            # Check Scalper direction filter
            if scalper_trigger:
                scalper_settings = db.get_strategy_settings(uid, "scalper", ctx_exchange, ctx_account_type)
                scalper_direction = scalper_settings.get("direction", "all")
                signal_direction = "long" if side == "Buy" else "short"
                logger.info(f"[{uid}] Scalper direction check: signal={signal_direction}, allowed={scalper_direction}")
                
                if scalper_direction != "all" and scalper_direction != signal_direction:
                    logger.info(f"[{uid}] {symbol}: Scalper direction filter - signal={signal_direction}, allowed={scalper_direction} → skip")
                    scalper_trigger = False
                else:
                    logger.info(f"[{uid}] Scalper direction OK, proceeding with {symbol}")

            # Check Fibonacci direction filter
            if fibonacci_trigger:
                fibo_settings = db.get_strategy_settings(uid, "fibonacci", ctx_exchange, ctx_account_type)
                fibo_direction = fibo_settings.get("direction", "all")
                signal_direction = "long" if side == "Buy" else "short"
                logger.info(f"[{uid}] Fibonacci direction check: signal={signal_direction}, allowed={fibo_direction}")
                
                if fibo_direction != "all" and fibo_direction != signal_direction:
                    logger.info(f"[{uid}] {symbol}: Fibonacci direction filter - signal={signal_direction}, allowed={fibo_direction} → skip")
                    fibonacci_trigger = False
                else:
                    logger.info(f"[{uid}] Fibonacci direction OK, proceeding with {symbol}")

            # Check RSI_BB direction filter
            if rsi_bb_trigger:
                rsi_bb_settings = db.get_strategy_settings(uid, "rsi_bb", ctx_exchange, ctx_account_type)
                rsi_bb_direction = rsi_bb_settings.get("direction", "all")
                signal_direction = "long" if side == "Buy" else "short"
                
                if rsi_bb_direction != "all" and rsi_bb_direction != signal_direction:
                    logger.info(f"[{uid}] {symbol}: RSI_BB direction filter - signal={signal_direction}, allowed={rsi_bb_direction} → skip")
                    rsi_bb_trigger = False

            # Check Elcaro direction filter
            if elcaro_trigger:
                elcaro_settings = db.get_strategy_settings(uid, "elcaro", ctx_exchange, ctx_account_type)
                elcaro_direction = elcaro_settings.get("direction", "all")
                signal_direction = "long" if side == "Buy" else "short"
                
                if elcaro_direction != "all" and elcaro_direction != signal_direction:
                    logger.info(f"[{uid}] {symbol}: Elcaro direction filter - signal={signal_direction}, allowed={elcaro_direction} → skip")
                    elcaro_trigger = False

            # Check OI direction filter
            if oi_trigger:
                oi_settings = db.get_strategy_settings(uid, "oi", ctx_exchange, ctx_account_type)
                oi_direction = oi_settings.get("direction", "all")
                signal_direction = "long" if side == "Buy" else "short"
                
                if oi_direction != "all" and oi_direction != signal_direction:
                    logger.info(f"[{uid}] {symbol}: OI direction filter - signal={signal_direction}, allowed={oi_direction} → skip")
                    oi_trigger = False

            if not (rsi_bb_trigger or bitk_trigger or scalper_trigger or elcaro_trigger or fibonacci_trigger or oi_trigger):
                continue

            # =====================================================
            # LICENSE CHECK - Verify user can trade the strategy
            # =====================================================
            license_info = get_user_license(uid)
            if not license_info["is_active"]:
                # User has no active license - skip all trading
                if once_per((uid, "no_license_warn", ""), 3600):  # Warn once per hour
                    try:
                        await ctx.bot.send_message(
                            uid,
                            t.get("no_license_trading", "⚠️ You need an active subscription to trade.\n\nUse /subscribe to purchase a license.")
                        )
                    except:
                        pass
                continue
            
            # Get trading mode to check license restrictions
            trading_mode = cfg.get("trading_mode", "demo")
            is_real_trade = trading_mode in ("real", "both")
            
            # Determine which strategy is triggered (for license check)
            active_strategy = None
            if rsi_bb_trigger:
                active_strategy = "rsi_bb"
            elif bitk_trigger:
                active_strategy = "scryptomera"
            elif scalper_trigger:
                active_strategy = "scalper"
            elif elcaro_trigger:
                active_strategy = "elcaro"
            elif fibonacci_trigger:
                active_strategy = "fibonacci"
            elif oi_trigger:
                active_strategy = "oi"
            
            # Check if user can trade this strategy on this account type
            if active_strategy and is_real_trade:
                access = check_license_access(uid, f"strategy_{active_strategy}", "real")
                if not access["allowed"]:
                    if access["reason"] == "trial_demo_only":
                        if once_per((uid, "trial_demo_warn", ""), 3600):
                            try:
                                await ctx.bot.send_message(
                                    uid,
                                    t.get("trial_demo_only", "⚠️ Trial license allows only demo trading.\n\nUpgrade to Premium or Basic for real trading: /subscribe")
                                )
                            except:
                                pass
                        continue
                    elif access["reason"] == "basic_strategy_limit":
                        if once_per((uid, "basic_strategy_warn", active_strategy), 3600):
                            allowed = ", ".join(access.get("allowed_strategies", []))
                            try:
                                await ctx.bot.send_message(
                                    uid,
                                    t.get("basic_strategy_limit", "⚠️ Basic license on real account allows only: {strategies}\n\nUpgrade to Premium for all strategies: /subscribe").format(strategies=allowed)
                                )
                            except:
                                pass
                        continue

            if rsi_bb_trigger:
                strat_settings = db.get_strategy_settings(uid, "rsi_bb", ctx_exchange, ctx_account_type)
                use_limit = strat_settings.get("order_type", "market") == "limit"
                params = get_strategy_trade_params(uid, cfg, symbol, "rsi_bb", side=side,
                                                  exchange=ctx_exchange, account_type=ctx_account_type)
                user_sl_pct, user_tp_pct = params["sl_pct"], params["tp_pct"]
                risk_pct = params["percent"]
                try:
                    qty = await calc_qty(uid, symbol, spot_price, risk_pct, user_sl_pct, account_type=ctx_account_type)
                except Exception as e:
                    logger.warning(f"[{uid}] {symbol}: calc_qty failed for rsi_bb: {e}")
                    continue
                
                # Set leverage if configured
                user_leverage = strat_settings.get("leverage")
                if user_leverage:
                    try:
                        await set_leverage(uid, symbol, leverage=user_leverage)
                    except Exception as e:
                        logger.warning(f"[{uid}] rsi_bb: failed to set leverage: {e}")
                    
                if use_limit:
                    liq = liq_price_buy if side == "Buy" else liq_price_sell
                    try:
                        await place_limit_order_with_strategy(
                            uid, symbol, side, price=liq, qty=qty,
                            signal_id=(signal_id or 0), strategy="rsi_bb"
                        )
                        inc_pyramid(uid, symbol, side)
                        await ctx.bot.send_message(
                            uid,
                            t.get('rsi_bb_limit_entry', "📊 RSI+BB Limit: {symbol} {side} @ {price:.6f} qty={qty}")
                             .format(symbol=symbol, side=side, price=liq, qty=qty, sl_pct=user_sl_pct),
                            parse_mode="Markdown"
                        )
                    except Exception as e:
                        error_msg = str(e)
                        if "INSUFFICIENT_BALANCE" in error_msg or "110007" in error_msg or "ab not enough" in error_msg.lower():
                            await ctx.bot.send_message(
                                uid,
                                t.get('insufficient_balance_error_extended', "❌ <b>Insufficient balance!</b>\n\n📊 Strategy: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b> {side}\n\n💰 Not enough funds on your {account_type} account.\n\n<b>Solutions:</b>\n• Top up your balance\n• Reduce position size (% per trade)\n• Lower leverage\n• Close some open positions").format(strategy="RSI+BB", symbol=symbol, side=side, account_type=ctx_account_type.upper()),
                                parse_mode="HTML"
                            )
                        else:
                            await ctx.bot.send_message(uid, t.get('rsi_bb_market_error', "❌ RSI+BB error\n🪙 {symbol} {side}\n\n{msg}").format(symbol=symbol, side=side, msg=error_msg))
                else:
                    try:
                        rv = float(rsi_val)
                        hi = float(bb_hi)
                        lo = float(bb_lo)
                        rsi_zone = (
                            t.get('rsi_zone_oversold', 'oversold') if rv < 23 else
                            t.get('rsi_zone_overbought', 'overbought') if rv > 77 else
                            t.get('rsi_zone_neutral', 'neutral')
                        )
                        
                        await place_order_all_accounts(
                            uid, symbol, side, orderType="Market", qty=qty, 
                            strategy="rsi_bb", leverage=user_leverage,
                            signal_id=signal_id, timeframe=timeframe
                        )
                        
                        # Also place on HyperLiquid if enabled
                        hl_result = await place_order_hyperliquid(uid, symbol, side, qty=qty, strategy="rsi_bb", leverage=user_leverage, sl_percent=user_sl_pct, tp_percent=user_tp_pct)
                        if hl_result and hl_result.get("success"):
                            await ctx.bot.send_message(uid, f"🔷 *HyperLiquid*: {symbol} {side} opened!", parse_mode="Markdown")
                        
                        inc_pyramid(uid, symbol, side)
                        
                        # Note: Position is now saved inside place_order_all_accounts for each account_type
                        
                        # Send unified entry message
                        side_display = 'LONG' if side == 'Buy' else 'SHORT'
                        await ctx.bot.send_message(
                            uid,
                            t.get('rsi_bb_market_ok', '📊 *RSI+BB: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• RSI: {rsi} ({zone})\n• SL: {sl_pct}%')
                             .format(symbol=symbol, side=side_display, price=spot_price, qty=qty, 
                                     rsi=rv, zone=rsi_zone, sl_pct=user_sl_pct),
                            parse_mode="Markdown"
                        )
                        
                        # Place ladder limit orders if enabled
                        try:
                            await place_ladder_limit_orders(uid, symbol, side, spot_price, strategy="rsi_bb", ctx=ctx)
                        except Exception as ladder_err:
                            logger.warning(f"[{uid}] rsi_bb ladder error: {ladder_err}")
                    except Exception as e:
                        error_msg = str(e)
                        if "INSUFFICIENT_BALANCE" in error_msg or "110007" in error_msg or "ab not enough" in error_msg.lower():
                            await ctx.bot.send_message(
                                uid,
                                t.get('insufficient_balance_error_extended', "❌ <b>Insufficient balance!</b>\n\n📊 Strategy: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b> {side}\n\n💰 Not enough funds on your {account_type} account.\n\n<b>Solutions:</b>\n• Top up your balance\n• Reduce position size (% per trade)\n• Lower leverage\n• Close some open positions").format(strategy="RSI+BB", symbol=symbol, side=side, account_type=ctx_account_type.upper()),
                                parse_mode="HTML"
                            )
                        else:
                            await ctx.bot.send_message(uid, t.get('rsi_bb_market_error', "❌ RSI+BB error\n🪙 {symbol} {side}\n\n{msg}").format(symbol=symbol, side=side, msg=error_msg))
                continue

            if bitk_trigger:
                logger.info(f"[{uid}] 🔮 Processing Scryptomera trade for {symbol}")
                strat_settings = db.get_strategy_settings(uid, "scryptomera", ctx_exchange, ctx_account_type)
                use_limit = strat_settings.get("order_type", "market") == "limit"
                params = get_strategy_trade_params(uid, cfg, symbol, "scryptomera", side=side,
                                                  exchange=ctx_exchange, account_type=ctx_account_type)
                user_sl_pct = params["sl_pct"]
                user_tp_pct = params["tp_pct"]
                risk_pct = params["percent"]
                logger.info(f"[{uid}] Scryptomera params: sl_pct={user_sl_pct}, risk_pct={risk_pct}, order_type={'limit' if use_limit else 'market'}")
                try:
                    if not user_sl_pct or user_sl_pct <= 0:
                        raise ValueError(f"User SL% not configured for {symbol}")

                    qty = await calc_qty(uid, symbol, spot_price, risk_pct, sl_pct=user_sl_pct, account_type=ctx_account_type)

                    # Set leverage if configured
                    user_leverage = strat_settings.get("leverage")
                    if user_leverage:
                        try:
                            await set_leverage(uid, symbol, leverage=user_leverage, account_type=ctx_account_type)
                        except Exception as e:
                            logger.warning(f"[{uid}] scryptomera: failed to set leverage: {e}")

                    if use_limit:
                        liq = liq_price_buy if side == "Buy" else liq_price_sell
                        try:
                            await place_limit_order_with_strategy(
                                uid, symbol, side, price=liq, qty=qty,
                                signal_id=(signal_id or 0), strategy="scryptomera"
                            )
                            inc_pyramid(uid, symbol, side)
                            side_display = 'LONG' if side == 'Buy' else 'SHORT'
                            await ctx.bot.send_message(
                                uid,
                                t.get('bitk_limit_entry', "🔮 Scryptomera Limit: {symbol} {side} @ {price:.6f}")
                                .format(symbol=symbol, side=side_display, price=liq, qty=qty, sl_pct=user_sl_pct),
                                parse_mode="Markdown"
                            )
                        except Exception as e:
                            await ctx.bot.send_message(
                                uid,
                                t.get('bitk_limit_error', "Scryptomera limit error: {msg}").format(msg=str(e))
                            )
                    else:
                        await place_order_all_accounts(
                            uid, symbol, side, orderType="Market", qty=qty, 
                            strategy="scryptomera", leverage=user_leverage,
                            signal_id=signal_id, timeframe=timeframe
                        )
                        
                        # Also place on HyperLiquid if enabled
                        hl_result = await place_order_hyperliquid(uid, symbol, side, qty=qty, strategy="scryptomera", leverage=user_leverage, sl_percent=user_sl_pct, tp_percent=user_tp_pct)
                        if hl_result and hl_result.get("success"):
                            await ctx.bot.send_message(uid, f"🔷 *HyperLiquid*: {symbol} {side} opened!", parse_mode="Markdown")
                        
                        inc_pyramid(uid, symbol, side)
                        
                        # Note: Position is now saved inside place_order_all_accounts for each account_type
                        
                        side_display = 'LONG' if side == 'Buy' else 'SHORT'
                        await ctx.bot.send_message(
                            uid,
                            t.get('bitk_market_ok', "🔮 *Scryptomera: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%")
                            .format(symbol=symbol, side=side_display, price=spot_price, qty=qty, sl_pct=user_sl_pct),
                            parse_mode="Markdown"
                        )
                        
                        # Place ladder limit orders if enabled
                        try:
                            await place_ladder_limit_orders(uid, symbol, side, spot_price, strategy="scryptomera", ctx=ctx)
                        except Exception as ladder_err:
                            logger.warning(f"[{uid}] scryptomera ladder error: {ladder_err}")

                except Exception as e:
                    error_msg = str(e)
                    # Проверка на недостаток баланса - показываем понятное сообщение
                    if "INSUFFICIENT_BALANCE" in error_msg or "110007" in error_msg or "ab not enough" in error_msg.lower():
                        await ctx.bot.send_message(
                            uid,
                            t.get('insufficient_balance_error', "❌ <b>Insufficient balance!</b>\n\n💰 Not enough funds on your {account_type} account to open this position.\n\n<b>Solutions:</b>\n• Top up your balance\n• Reduce position size (% per trade)\n• Lower leverage\n• Close some open positions").format(account_type=ctx_account_type.upper()),
                            parse_mode="HTML"
                        )
                    elif "110013" in error_msg or "cannot set leverage" in error_msg.lower() or "maxleverage" in error_msg.lower():
                        # Extract max leverage from error if possible (re is imported globally)
                        match = re.search(r'maxLeverage\s*\[(\d+)\]', error_msg)
                        max_lev = match.group(1) if match else "50-100"
                        await ctx.bot.send_message(
                            uid,
                            t.get('leverage_too_high_error', "❌ <b>Leverage too high!</b>\n\n⚙️ Your configured leverage exceeds the maximum allowed for this symbol.\n\n<b>Maximum allowed:</b> {max_leverage}x\n\n<b>Solution:</b> Go to strategy settings and reduce leverage.").format(max_leverage=max_lev),
                            parse_mode="HTML"
                        )
                    elif "110090" in error_msg or "position limit exceeded" in error_msg.lower():
                        # Position limit exceeded error
                        await ctx.bot.send_message(
                            uid,
                            t.get('position_limit_error', "❌ <b>Position limit exceeded!</b>\n\n📊 Strategy: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b>\n\n⚠️ Your position would exceed the maximum allowed limit.\n\n<b>Solutions:</b>\n• Reduce leverage in strategy settings\n• Reduce position size (% per trade)\n• Close some existing positions").format(strategy="Scryptomera", symbol=symbol),
                            parse_mode="HTML"
                        )
                    else:
                        await ctx.bot.send_message(
                            uid,
                            t.get('bitk_market_error', "Market error: {msg}").format(msg=error_msg)
                        )
                continue

            if scalper_trigger:
                strat_settings = db.get_strategy_settings(uid, "scalper", ctx_exchange, ctx_account_type)
                use_limit = strat_settings.get("order_type", "market") == "limit"
                params = get_strategy_trade_params(uid, cfg, symbol, "scalper", side=side,
                                                  exchange=ctx_exchange, account_type=ctx_account_type)
                user_sl_pct = params["sl_pct"]
                user_tp_pct = params["tp_pct"]
                risk_pct = params["percent"]
                try:
                    if not user_sl_pct or user_sl_pct <= 0:
                        raise ValueError(f"User SL% not configured for {symbol}")

                    qty = await calc_qty(uid, symbol, spot_price, risk_pct, sl_pct=user_sl_pct, account_type=ctx_account_type)

                    # Set leverage if configured
                    user_leverage = strat_settings.get("leverage")
                    if user_leverage:
                        try:
                            await set_leverage(uid, symbol, leverage=user_leverage, account_type=ctx_account_type)
                        except Exception as e:
                            logger.warning(f"[{uid}] scalper: failed to set leverage: {e}")

                    if use_limit:
                        liq = liq_price_buy if side == "Buy" else liq_price_sell
                        try:
                            await place_limit_order_with_strategy(
                                uid, symbol, side, price=liq, qty=qty,
                                signal_id=(signal_id or 0), strategy="scalper"
                            )
                            inc_pyramid(uid, symbol, side)
                            side_display = 'LONG' if side == 'Buy' else 'SHORT'
                            await ctx.bot.send_message(
                                uid,
                                t.get('scalper_limit_entry', "⚡ Scalper Limit: {symbol} {side} @ {price:.6f}")
                                .format(symbol=symbol, side=side_display, price=liq, qty=qty, sl_pct=user_sl_pct),
                                parse_mode="Markdown"
                            )
                        except Exception as e:
                            await ctx.bot.send_message(
                                uid,
                                t.get('scalper_limit_error', "Scalper limit error: {msg}").format(msg=str(e))
                            )
                    else:
                        await place_order_all_accounts(
                            uid, symbol, side, orderType="Market", qty=qty, 
                            strategy="scalper", leverage=user_leverage,
                            signal_id=signal_id, timeframe=timeframe
                        )
                        
                        # Also place on HyperLiquid if enabled
                        hl_result = await place_order_hyperliquid(uid, symbol, side, qty=qty, strategy="scalper", leverage=user_leverage, sl_percent=user_sl_pct, tp_percent=user_tp_pct)
                        if hl_result and hl_result.get("success"):
                            await ctx.bot.send_message(uid, f"🔷 *HyperLiquid*: {symbol} {side} opened!", parse_mode="Markdown")
                        
                        inc_pyramid(uid, symbol, side)
                        
                        # Note: Position is now saved inside place_order_all_accounts for each account_type
                        
                        side_display = 'LONG' if side == 'Buy' else 'SHORT'
                        await ctx.bot.send_message(
                            uid,
                            t.get('scalper_market_ok', "⚡ *Scalper: {side}*\n• {symbol} @ {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%")
                            .format(symbol=symbol, side=side_display, price=spot_price, qty=qty, sl_pct=user_sl_pct),
                            parse_mode="Markdown"
                        )
                        
                        # Place ladder limit orders if enabled
                        try:
                            await place_ladder_limit_orders(uid, symbol, side, spot_price, strategy="scalper", ctx=ctx)
                        except Exception as ladder_err:
                            logger.warning(f"[{uid}] scalper ladder error: {ladder_err}")

                except Exception as e:
                    error_msg = str(e)
                    if "INSUFFICIENT_BALANCE" in error_msg or "110007" in error_msg or "ab not enough" in error_msg.lower():
                        await ctx.bot.send_message(
                            uid,
                            t.get('insufficient_balance_error', "❌ <b>Insufficient balance!</b>\n\n💰 Not enough funds on your {account_type} account to open this position.\n\n<b>Solutions:</b>\n• Top up your balance\n• Reduce position size (% per trade)\n• Lower leverage\n• Close some open positions").format(account_type=ctx_account_type.upper()),
                            parse_mode="HTML"
                        )
                    elif "110013" in error_msg or "cannot set leverage" in error_msg.lower() or "maxleverage" in error_msg.lower():
                        # Extract max leverage from error if possible (re is imported globally)
                        match = re.search(r'maxLeverage\s*\[(\d+)\]', error_msg)
                        max_lev = match.group(1) if match else "50-100"
                        await ctx.bot.send_message(
                            uid,
                            t.get('leverage_too_high_error', "❌ <b>Leverage too high!</b>\n\n⚙️ Your configured leverage exceeds the maximum allowed for this symbol.\n\n<b>Maximum allowed:</b> {max_leverage}x\n\n<b>Solution:</b> Go to strategy settings and reduce leverage.").format(max_leverage=max_lev),
                            parse_mode="HTML"
                        )
                    elif "110090" in error_msg or "position limit exceeded" in error_msg.lower():
                        await ctx.bot.send_message(
                            uid,
                            t.get('position_limit_error', "❌ <b>Position limit exceeded!</b>\n\n📊 Strategy: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b>\n\n⚠️ Your position would exceed the maximum allowed limit.\n\n<b>Solutions:</b>\n• Reduce leverage in strategy settings\n• Reduce position size (% per trade)\n• Close some existing positions").format(strategy="Scalper", symbol=symbol),
                            parse_mode="HTML"
                        )
                    else:
                        await ctx.bot.send_message(
                            uid,
                            t.get('scalper_market_error', "Scalper error: {msg}").format(msg=error_msg)
                        )
                continue

            if elcaro_trigger:
                # Elcaro mode: все параметры берём из сигнала, а не из настроек пользователя
                elcaro_mode = parsed_elcaro.get("elcaro_mode", False)
                
                if elcaro_mode:
                    # Новый формат - все параметры из сигнала
                    elcaro_sl_pct = parsed_elcaro.get("sl_pct", 3.0)
                    elcaro_tp_pct = parsed_elcaro.get("tp_pct", 6.0)
                    elcaro_atr_periods = parsed_elcaro.get("atr_periods", 14)
                    elcaro_atr_mult = parsed_elcaro.get("atr_multiplier", 1.5)
                    elcaro_atr_trigger = parsed_elcaro.get("atr_trigger_pct", 30.0)
                    elcaro_leverage = parsed_elcaro.get("leverage", 20)
                    elcaro_timeframe = parsed_elcaro.get("timeframe", "60m")
                    elcaro_entry = parsed_elcaro.get("price", spot_price)
                    elcaro_sl = parsed_elcaro.get("sl")
                    elcaro_tp = parsed_elcaro.get("tp")
                    
                    # Используем percent из настроек пользователя (риск на сделку)
                    params = get_strategy_trade_params(uid, cfg, symbol, "elcaro", side=side,
                                                      exchange=ctx_exchange, account_type=ctx_account_type)
                    risk_pct = params["percent"]
                    
                    # SL/TP из сигнала имеют приоритет
                    sl_pct = elcaro_sl_pct
                    tp_pct = elcaro_tp_pct
                    
                    logger.debug(f"[{uid}] Elcaro signal: SL={sl_pct}%, TP={tp_pct}%, "
                                f"ATR={elcaro_atr_periods}/x{elcaro_atr_mult}/trigger={elcaro_atr_trigger}%, "
                                f"leverage={elcaro_leverage}")
                else:
                    # Legacy формат - используем настройки пользователя
                    elcaro_strat_settings = db.get_strategy_settings(uid, "elcaro", ctx_exchange, ctx_account_type)
                    params = get_strategy_trade_params(uid, cfg, symbol, "elcaro", side=side,
                                                      exchange=ctx_exchange, account_type=ctx_account_type)
                    sl_pct = params["sl_pct"]
                    tp_pct = params["tp_pct"]
                    risk_pct = params["percent"]
                    elcaro_entry = parsed_elcaro.get("price", spot_price)
                    elcaro_sl = parsed_elcaro.get("sl")
                    elcaro_tp = parsed_elcaro.get("tp")
                    elcaro_leverage = elcaro_strat_settings.get("leverage")  # Use user's strategy settings
                    elcaro_timeframe = parsed_elcaro.get("interval", "60m")
                    elcaro_atr_periods = None
                    elcaro_atr_mult = None
                    elcaro_atr_trigger = None
                    
                    # Вычисляем SL% из сигнала, если пользователь не задал
                    if (not sl_pct or sl_pct <= 0) and elcaro_sl and elcaro_entry:
                        sl_pct = abs((elcaro_sl - elcaro_entry) / elcaro_entry * 100)
                    if not sl_pct or sl_pct <= 0:
                        sl_pct = 3.0  # fallback
                    if not tp_pct or tp_pct <= 0:
                        tp_pct = 6.0  # fallback

                try:
                    qty = await calc_qty(uid, symbol, spot_price, risk_pct, sl_pct=sl_pct, account_type=ctx_account_type)

                    # Set leverage from signal if available
                    if elcaro_mode and elcaro_leverage:
                        try:
                            await set_leverage(uid, symbol, leverage=elcaro_leverage, account_type=ctx_account_type)
                            logger.debug(f"[{uid}] Elcaro: set leverage={elcaro_leverage} for {symbol}")
                        except Exception as e:
                            logger.warning(f"[{uid}] Elcaro: failed to set leverage: {e}")

                    # Elcaro: automatically decide Market vs Limit based on Entry price
                    # If current price is close to Entry (within 0.3%) - use Market
                    # Otherwise use Limit at Entry price
                    entry_diff_pct = abs(spot_price - elcaro_entry) / spot_price * 100 if elcaro_entry else 0
                    use_limit_entry = elcaro_entry and entry_diff_pct > 0.3
                    
                    order_leverage = elcaro_leverage if elcaro_mode and elcaro_leverage else None
                    
                    if use_limit_entry:
                        # Limit order at Entry price from signal
                        try:
                            await place_limit_order_with_strategy(
                                uid, symbol, side, price=elcaro_entry, qty=qty,
                                signal_id=(signal_id or 0), strategy="elcaro"
                            )
                            inc_pyramid(uid, symbol, side)
                            side_display = 'LONG' if side == 'Buy' else 'SHORT'
                            await ctx.bot.send_message(
                                uid,
                                t.get('elcaro_limit_entry', "🔥 *Elcaro Limit Entry*\n• {symbol} {side}\n• Price: {price:.6f}\n• Qty: {qty}\n• SL: {sl_pct}%")
                                .format(symbol=symbol, side=side_display, price=elcaro_entry, qty=qty, sl_pct=sl_pct),
                                parse_mode="Markdown"
                            )
                        except Exception as e:
                            await ctx.bot.send_message(
                                uid,
                                t.get('elcaro_limit_error', "❌ Elcaro limit error: {msg}").format(msg=str(e))
                            )
                    else:
                        # Market order - price is close to Entry
                        try:
                            await place_order_all_accounts(
                                uid, symbol, side, orderType="Market", qty=qty, 
                                strategy="elcaro", leverage=order_leverage,
                                signal_id=signal_id, timeframe=elcaro_timeframe
                            )
                            
                            # Also place on HyperLiquid if enabled
                            hl_result = await place_order_hyperliquid(uid, symbol, side, qty=qty, strategy="elcaro", leverage=order_leverage, sl_percent=sl_pct, tp_percent=tp_pct)
                            if hl_result and hl_result.get("success"):
                                await ctx.bot.send_message(uid, f"🔷 *HyperLiquid*: {symbol} {side} opened!", parse_mode="Markdown")
                            
                            # Calculate exact SL/TP prices
                            if elcaro_mode and elcaro_sl and elcaro_tp:
                                # Use exact prices from signal
                                actual_sl = elcaro_sl
                                actual_tp = elcaro_tp
                            else:
                                # Calculate from percentages
                                if side == "Buy":
                                    actual_sl = spot_price * (1 - sl_pct / 100)
                                    actual_tp = spot_price * (1 + tp_pct / 100)
                                else:
                                    actual_sl = spot_price * (1 + sl_pct / 100)
                                    actual_tp = spot_price * (1 - tp_pct / 100)
                            
                            # Set TP/SL
                            await set_trading_stop(uid, symbol, tp_price=actual_tp, sl_price=actual_sl, side_hint=side)
                            
                            # Note: Position is now saved inside place_order_all_accounts for each account_type
                            inc_pyramid(uid, symbol, side)
                            
                            # Format signal message
                            signal_info = (
                                f"🔥 *Elcaro* {'📈 LONG' if side=='Buy' else '📉 SHORT'}\n"
                                f"📊 {symbol}\n"
                                f"💰 Entry: {spot_price:.6g}\n"
                                f"🛑 SL: {actual_sl:.6g} ({sl_pct:.2f}%)\n"
                                f"🎯 TP: {actual_tp:.6g} ({tp_pct:.2f}%)"
                            )
                            if elcaro_mode and elcaro_atr_periods:
                                signal_info += f"\n📉 ATR: {elcaro_atr_periods} | ×{elcaro_atr_mult} | Trigger: {elcaro_atr_trigger}%"
                            
                            await ctx.bot.send_message(uid, signal_info, parse_mode="Markdown")
                            
                            # Place ladder limit orders if enabled
                            try:
                                await place_ladder_limit_orders(uid, symbol, side, spot_price, strategy="elcaro", ctx=ctx)
                            except Exception as ladder_err:
                                logger.warning(f"[{uid}] elcaro ladder error: {ladder_err}")
                            
                        except Exception as e:
                            error_msg = str(e)
                            if "INSUFFICIENT_BALANCE" in error_msg or "110007" in error_msg or "ab not enough" in error_msg.lower():
                                await ctx.bot.send_message(
                                    uid,
                                    t.get('insufficient_balance_error', "❌ <b>Insufficient balance!</b>\n\n💰 Not enough funds on your {account_type} account to open this position.\n\n<b>Solutions:</b>\n• Top up your balance\n• Reduce position size (% per trade)\n• Lower leverage\n• Close some open positions").format(account_type=ctx_account_type.upper()),
                                    parse_mode="HTML"
                                )
                            elif "110013" in error_msg or "cannot set leverage" in error_msg.lower() or "maxleverage" in error_msg.lower():
                                match = re.search(r'maxLeverage\s*\[(\d+)\]', error_msg)
                                max_lev = match.group(1) if match else "50-100"
                                await ctx.bot.send_message(
                                    uid,
                                    t.get('leverage_too_high_error', "❌ <b>Leverage too high!</b>\n\n⚙️ Your configured leverage exceeds the maximum allowed for this symbol.\n\n<b>Maximum allowed:</b> {max_leverage}x\n\n<b>Solution:</b> Go to strategy settings and reduce leverage.").format(max_leverage=max_lev),
                                    parse_mode="HTML"
                                )
                            elif "110090" in error_msg or "position limit exceeded" in error_msg.lower():
                                await ctx.bot.send_message(
                                    uid,
                                    t.get('position_limit_error', "❌ <b>Position limit exceeded!</b>\n\n📊 Strategy: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b>\n\n⚠️ Your position would exceed the maximum allowed limit.\n\n<b>Solutions:</b>\n• Reduce leverage in strategy settings\n• Reduce position size (% per trade)\n• Close some existing positions").format(strategy="Elcaro", symbol=symbol),
                                    parse_mode="HTML"
                                )
                            else:
                                await ctx.bot.send_message(
                                    uid,
                                    t.get('elcaro_market_error', "Elcaro error: {msg}").format(msg=error_msg)
                                )
                except Exception as e:
                    error_msg = str(e)
                    if "INSUFFICIENT_BALANCE" in error_msg or "110007" in error_msg or "ab not enough" in error_msg.lower():
                        await ctx.bot.send_message(
                            uid,
                            t.get('insufficient_balance_error', "❌ <b>Insufficient balance!</b>\n\n💰 Not enough funds on your {account_type} account to open this position.\n\n<b>Solutions:</b>\n• Top up your balance\n• Reduce position size (% per trade)\n• Lower leverage\n• Close some open positions").format(account_type=ctx_account_type.upper()),
                            parse_mode="HTML"
                        )
                    elif "110013" in error_msg or "cannot set leverage" in error_msg.lower() or "maxleverage" in error_msg.lower():
                        match = re.search(r'maxLeverage\s*\[(\d+)\]', error_msg)
                        max_lev = match.group(1) if match else "50-100"
                        await ctx.bot.send_message(
                            uid,
                            t.get('leverage_too_high_error', "❌ <b>Leverage too high!</b>\n\n⚙️ Your configured leverage exceeds the maximum allowed for this symbol.\n\n<b>Maximum allowed:</b> {max_leverage}x\n\n<b>Solution:</b> Go to strategy settings and reduce leverage.").format(max_leverage=max_lev),
                            parse_mode="HTML"
                        )
                    elif "110090" in error_msg or "position limit exceeded" in error_msg.lower():
                        await ctx.bot.send_message(
                            uid,
                            t.get('position_limit_error', "❌ <b>Position limit exceeded!</b>\n\n📊 Strategy: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b>\n\n⚠️ Your position would exceed the maximum allowed limit.\n\n<b>Solutions:</b>\n• Reduce leverage in strategy settings\n• Reduce position size (% per trade)\n• Close some existing positions").format(strategy="Elcaro", symbol=symbol),
                            parse_mode="HTML"
                        )
                    else:
                        await ctx.bot.send_message(
                            uid,
                            t.get('elcaro_market_error', "Elcaro error: {msg}").format(msg=error_msg)
                        )
                continue

            if fibonacci_trigger:
                # Fibonacci Extension Strategy
                # All parameters come from the signal
                fibo_entry = parsed_fibonacci.get("entry", spot_price)
                fibo_entry_low = parsed_fibonacci.get("entry_low")
                fibo_entry_high = parsed_fibonacci.get("entry_high")
                fibo_sl = parsed_fibonacci.get("sl")
                fibo_tp = parsed_fibonacci.get("tp")
                fibo_sl_pct = parsed_fibonacci.get("sl_pct", 3.0)
                fibo_tp_pct = parsed_fibonacci.get("tp_pct", 6.0)
                quality_grade = parsed_fibonacci.get("quality_grade", "B")
                quality_score = parsed_fibonacci.get("quality_score", 50)
                trigger_info = parsed_fibonacci.get("trigger_info", "")
                
                # Get user settings (percent, leverage)
                strat_settings = db.get_strategy_settings(uid, "fibonacci", ctx_exchange, ctx_account_type)
                params = get_strategy_trade_params(uid, cfg, symbol, "fibonacci", side=side,
                                                  exchange=ctx_exchange, account_type=ctx_account_type)
                risk_pct = params["percent"]
                user_leverage = strat_settings.get("leverage", 10)
                
                # Quality filter - skip if quality score too low
                min_quality = strat_settings.get("min_quality", 50)
                if quality_score < min_quality:
                    logger.debug(f"[{uid}] Fibonacci {symbol}: quality {quality_score} < min {min_quality} → skip")
                    continue
                
                try:
                    qty = await calc_qty(uid, symbol, spot_price, risk_pct, sl_pct=fibo_sl_pct, account_type=ctx_account_type)
                    
                    # Set leverage
                    if user_leverage:
                        try:
                            await set_leverage(uid, symbol, leverage=user_leverage, account_type=ctx_account_type)
                        except Exception as e:
                            logger.warning(f"[{uid}] Fibonacci: failed to set leverage: {e}")
                    
                    # Decide Market vs Limit based on entry zone
                    # If current price is within entry zone → Market
                    # If current price is outside entry zone → Limit at best boundary
                    use_limit_entry = False
                    limit_entry_price = fibo_entry  # Default to mid-point
                    
                    if fibo_entry_low and fibo_entry_high:
                        # For LONG: use lower boundary (buy cheaper)
                        # For SHORT: use upper boundary (sell higher)
                        if side == "Buy":
                            limit_entry_price = fibo_entry_low
                        else:  # Sell
                            limit_entry_price = fibo_entry_high
                        
                        if not (fibo_entry_low <= spot_price <= fibo_entry_high):
                            use_limit_entry = True
                    
                    if use_limit_entry:
                        # Limit order at optimal entry zone boundary
                        try:
                            await place_limit_order_with_strategy(
                                uid, symbol, side, price=limit_entry_price, qty=qty,
                                signal_id=(signal_id or 0), strategy="fibonacci"
                            )
                            inc_pyramid(uid, symbol, side)
                            side_display = 'LONG' if side == 'Buy' else 'SHORT'
                            entry_zone_display = f"{fibo_entry_low:.6f} – {fibo_entry_high:.6f}"
                            await ctx.bot.send_message(
                                uid,
                                t.get('fibonacci_limit_entry', "📐 *Fibonacci Limit Entry*\n• {symbol} {side}\n• Limit: {price:.6f}\n• Entry Zone: {entry_zone}\n• Qty: {qty}\n• SL: {sl_pct}%")
                                .format(symbol=symbol, side=side_display, price=limit_entry_price, entry_zone=entry_zone_display, qty=qty, sl_pct=fibo_sl_pct),
                                parse_mode="Markdown"
                            )
                        except Exception as e:
                            error_msg = str(e)
                            if "INSUFFICIENT_BALANCE" in error_msg or "110007" in error_msg or "ab not enough" in error_msg.lower():
                                await ctx.bot.send_message(
                                    uid,
                                    t.get('insufficient_balance_error_extended', "❌ <b>Insufficient balance!</b>\n\n📊 Strategy: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b> {side}\n\n💰 Not enough funds on your {account_type} account.\n\n<b>Solutions:</b>\n• Top up your balance\n• Reduce position size (% per trade)\n• Lower leverage\n• Close some open positions").format(strategy="Fibonacci", symbol=symbol, side=side, account_type=ctx_account_type.upper()),
                                    parse_mode="HTML"
                                )
                            else:
                                await ctx.bot.send_message(
                                    uid,
                                    t.get('fibonacci_limit_error', "❌ Fibonacci limit error\n🪙 {symbol} {side}\n\n{msg}").format(symbol=symbol, side=side, msg=error_msg)
                                )
                    else:
                        # Market order - price is in entry zone
                        try:
                            await place_order_all_accounts(
                                uid, symbol, side, orderType="Market", qty=qty, 
                                strategy="fibonacci", leverage=user_leverage,
                                signal_id=signal_id, timeframe="1h"
                            )
                            
                            # Also place on HyperLiquid if enabled
                            hl_result = await place_order_hyperliquid(uid, symbol, side, qty=qty, strategy="fibonacci", leverage=user_leverage, sl_percent=fibo_sl_pct, tp_percent=fibo_tp_pct)
                            if hl_result and hl_result.get("success"):
                                await ctx.bot.send_message(uid, f"🔷 *HyperLiquid*: {symbol} {side} opened!", parse_mode="Markdown")
                            
                            # Use exact SL/TP from signal
                            actual_sl = fibo_sl if fibo_sl else (spot_price * (1 - fibo_sl_pct / 100) if side == "Buy" else spot_price * (1 + fibo_sl_pct / 100))
                            actual_tp = fibo_tp if fibo_tp else (spot_price * (1 + fibo_tp_pct / 100) if side == "Buy" else spot_price * (1 - fibo_tp_pct / 100))
                            
                            # Set TP/SL
                            await set_trading_stop(uid, symbol, tp_price=actual_tp, sl_price=actual_sl, side_hint=side)
                            
                            # Note: Position is now saved inside place_order_all_accounts for each account_type
                            inc_pyramid(uid, symbol, side)
                            
                            # Format signal message
                            signal_info = (
                                f"📐 *Fibonacci* {'📈 LONG' if side=='Buy' else '📉 SHORT'}\n"
                                f"🪙 {symbol}\n"
                                f"💰 Entry: {spot_price:.6g}\n"
                                f"🎯 Zone: {fibo_entry_low:.6g} – {fibo_entry_high:.6g}\n"
                                f"🛑 SL: {actual_sl:.6g} ({fibo_sl_pct:.2f}%)\n"
                                f"✅ TP: {actual_tp:.6g} ({fibo_tp_pct:.2f}%)\n"
                                f"🟢 Quality: {quality_grade} ({quality_score}/100)"
                            )
                            if trigger_info:
                                signal_info += f"\n⚡ {trigger_info}"
                            
                            await ctx.bot.send_message(uid, signal_info, parse_mode="Markdown")
                            
                        except Exception as e:
                            error_msg = str(e)
                            if "INSUFFICIENT_BALANCE" in error_msg or "110007" in error_msg or "ab not enough" in error_msg.lower():
                                await ctx.bot.send_message(
                                    uid,
                                    t.get('insufficient_balance_error_extended', "❌ <b>Insufficient balance!</b>\n\n📊 Strategy: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b> {side}\n\n💰 Not enough funds on your {account_type} account.\n\n<b>Solutions:</b>\n• Top up your balance\n• Reduce position size (% per trade)\n• Lower leverage\n• Close some open positions").format(strategy="Fibonacci", symbol=symbol, side=side, account_type=ctx_account_type.upper()),
                                    parse_mode="HTML"
                                )
                            else:
                                await ctx.bot.send_message(
                                    uid,
                                    t.get('fibonacci_market_error', "❌ Fibonacci error\n🪙 {symbol} {side}\n\n{msg}").format(symbol=symbol, side=side, msg=error_msg)
                                )
                except Exception as e:
                    error_msg = str(e)
                    if "INSUFFICIENT_BALANCE" in error_msg or "110007" in error_msg or "ab not enough" in error_msg.lower():
                        await ctx.bot.send_message(
                            uid,
                            t.get('insufficient_balance_error_extended', "❌ <b>Insufficient balance!</b>\n\n📊 Strategy: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b> {side}\n\n💰 Not enough funds on your {account_type} account.\n\n<b>Solutions:</b>\n• Top up your balance\n• Reduce position size (% per trade)\n• Lower leverage\n• Close some open positions").format(strategy="Fibonacci", symbol=symbol, side=side, account_type=ctx_account_type.upper()),
                            parse_mode="HTML"
                        )
                    else:
                        await ctx.bot.send_message(
                            uid,
                            t.get('fibonacci_market_error', "❌ Fibonacci error\n🪙 {symbol} {side}\n\n{msg}").format(symbol=symbol, side=side, msg=error_msg)
                        )
                continue

            if oi_trigger:
                strat_settings = db.get_strategy_settings(uid, "oi", ctx_exchange, ctx_account_type)
                use_limit = strat_settings.get("order_type", "market") == "limit"
                params = get_strategy_trade_params(uid, cfg, symbol, "oi", side=side,
                                                  exchange=ctx_exchange, account_type=ctx_account_type)
                user_sl_pct = params["sl_pct"]
                user_tp_pct = params["tp_pct"]
                risk_pct = params["percent"]
                try:
                    if user_sl_pct <= 0:
                        user_sl_pct = 1.0
                    qty_total = await calc_qty(uid, symbol, spot_price, risk_pct, sl_pct=user_sl_pct, account_type=ctx_account_type)

                    # Set leverage if configured
                    user_leverage = strat_settings.get("leverage")
                    if user_leverage:
                        try:
                            await set_leverage(uid, symbol, leverage=user_leverage, account_type=ctx_account_type)
                        except Exception as e:
                            logger.warning(f"[{uid}] oi: failed to set leverage: {e}")

                    filt     = await get_symbol_filters(uid, symbol)
                    step_qty = float(filt["qtyStep"])
                    min_qty  = float(filt["minQty"])
                    def q_qty(v: float) -> float:
                        return max(min_qty, quantize(v, step_qty))

                    if use_limit:
                        # Full limit order
                        qty_lim = q_qty(qty_total)
                        data = await _bybit_request(uid, "GET", "/v5/market/tickers", params={"category":"linear","symbol":symbol})
                        last = (data.get("list") or [{}])[0].get("lastPrice")
                        cur  = float(last) if last not in (None, "", "0") else float(spot_price)
                        lim_price = cur * (0.99 if side == "Buy" else 1.01)
                        await place_limit_order_with_strategy(
                            uid, symbol, side, price=lim_price, qty=qty_lim,
                            signal_id=(signal_id or 0), strategy="oi"
                        )
                        await ctx.bot.send_message(
                            uid,
                            t.get('oi_limit_entry', "📉 OI Limit: {symbol} {side} @ {price:.6f} qty={qty}")
                             .format(symbol=symbol, side=side, price=lim_price, qty=qty_lim, sl_pct=user_sl_pct),
                            parse_mode="Markdown"
                        )
                        inc_pyramid(uid, symbol, side)
                    else:
                        # Full market order
                        qty_mkt = q_qty(qty_total)
                        await place_order_all_accounts(
                            uid, symbol, side, orderType="Market", qty=qty_mkt, 
                            strategy="oi", leverage=user_leverage,
                            signal_id=signal_id, timeframe=timeframe
                        )
                        
                        # Also place on HyperLiquid if enabled
                        hl_result = await place_order_hyperliquid(uid, symbol, side, qty=qty_mkt, strategy="oi", leverage=user_leverage, sl_percent=user_sl_pct, tp_percent=user_tp_pct)
                        if hl_result and hl_result.get("success"):
                            await ctx.bot.send_message(uid, f"🔷 *HyperLiquid*: {symbol} {side} opened!", parse_mode="Markdown")
                        
                        # Note: Position is now saved inside place_order_all_accounts for each account_type
                        
                        await ctx.bot.send_message(
                            uid,
                            t.get('oi_market_ok', "📉 OI Market: {symbol} {side} qty={qty} (SL={sl_pct}%)")
                             .format(symbol=symbol, side=side, price=spot_price, qty=qty_mkt, sl_pct=user_sl_pct),
                            parse_mode="Markdown"
                        )
                        inc_pyramid(uid, symbol, side)
                        
                        # Place ladder limit orders if enabled
                        try:
                            await place_ladder_limit_orders(uid, symbol, side, spot_price, strategy="oi", ctx=ctx)
                        except Exception as ladder_err:
                            logger.warning(f"[{uid}] oi ladder error: {ladder_err}")

                except Exception as e:
                    error_msg = str(e)
                    if "INSUFFICIENT_BALANCE" in error_msg or "110007" in error_msg or "ab not enough" in error_msg.lower():
                        await ctx.bot.send_message(
                            uid,
                            t.get('insufficient_balance_error_extended', "❌ <b>Insufficient balance!</b>\n\n📊 Strategy: <b>{strategy}</b>\n🪙 Symbol: <b>{symbol}</b> {side}\n\n💰 Not enough funds on your {account_type} account.\n\n<b>Solutions:</b>\n• Top up your balance\n• Reduce position size (% per trade)\n• Lower leverage\n• Close some open positions").format(strategy="OI", symbol=symbol, side=side, account_type=ctx_account_type.upper()),
                            parse_mode="HTML"
                        )
                    else:
                        await ctx.bot.send_message(uid, t.get('oi_market_error', "❌ OI error\n🪙 {symbol} {side}\n\n{msg}").format(symbol=symbol, side=side, msg=error_msg))
                continue

        except Exception as e:
            # Handle Telegram rate limits gracefully
            from telegram.error import RetryAfter
            if isinstance(e, RetryAfter):
                _notification_retry_after[uid] = time.time() + e.retry_after
                logger.warning(f"[{uid}] Rate limited in channel handler, retry after {e.retry_after}s")
            else:
                logger.error(f"User loop error for uid={uid}: {e}", exc_info=True)
            continue

def log_exit_and_remove_position(
    user_id: int,
    *,
    signal_id: int | None,
    symbol: str,
    side: str,                 
    entry_price: float,
    exit_price: float,
    exit_reason: str,        
    size: float,
    signal_source: str | None = None,
    rsi: float | None = None, bb_hi: float | None = None, bb_lo: float | None = None,
    oi_prev: float | None = None, oi_now: float | None = None, oi_chg: float | None = None,
    vol_from: float | None = None, vol_to: float | None = None,
    price_chg: float | None = None, vol_delta: float | None = None,
    sl_price: float | None = None, tp_price: float | None = None,
    timeframe: str | None = None, entry_ts_ms: int | None = None,
    exit_order_type: str | None = None,
    strategy: str | None = None,
    account_type: str = "demo",
) -> None:
    cfg = get_user_config(user_id) or {}
    
    # Use strategy-specific SL/TP if available (pass side for side-specific settings)
    if strategy:
        sl_pct, tp_pct = resolve_sl_tp_pct(cfg, symbol, strategy=strategy, user_id=user_id, side=side)
    else:
        sl_pct = float(cfg.get("sl_percent") or DEFAULT_SL_PCT)
        tp_pct = float(cfg.get("tp_percent") or DEFAULT_TP_PCT)

    pnl_abs = (exit_price - entry_price) * float(size) * (1 if side == "Buy" else -1)
    pnl_pct = (exit_price / entry_price - 1.0) * (100 if side == "Buy" else -100)

    add_trade_log(
        user_id=user_id, signal_id=signal_id, symbol=symbol, side=side,
        entry_price=float(entry_price), exit_price=float(exit_price),
        exit_reason=str(exit_reason), pnl=float(pnl_abs), pnl_pct=float(pnl_pct),
        signal_source=signal_source, rsi=rsi, bb_hi=bb_hi, bb_lo=bb_lo,
        oi_prev=oi_prev, oi_now=oi_now, oi_chg=oi_chg,
        vol_from=vol_from, vol_to=vol_to, price_chg=price_chg, vol_delta=vol_delta,
        sl_pct=sl_pct, tp_pct=tp_pct, sl_price=sl_price, tp_price=tp_price,
        timeframe=timeframe, entry_ts=int(entry_ts_ms or 0),
        exit_ts=int(time.time()*1000), exit_order_type=exit_order_type,
        strategy=strategy, account_type=account_type,
    )
    # Pass entry_price to prevent race condition where a NEW position (opened by signal)
    # gets deleted when closing OLD position (detected by monitor)
    remove_active_position(user_id, symbol, account_type=account_type, entry_price=entry_price)

def cleanup_limit_order_on_status(user_id: int, order_id: str, status: str) -> None:
    status = (status or "").upper()
    if status in ("FILLED", "CANCELED", "EXPIRED"):
        try:
            remove_pending_limit_order(user_id, order_id)
        except Exception:
            pass

@log_calls
async def monitor_positions_loop(app: Application):
    """Main monitoring loop - optimized for multi-user."""
    global _close_all_cooldown
    bot = app.bot
    
    # Track previous open symbols per user to avoid spam notifications
    _open_syms_prev = {}
    
    # Track SL notifications already sent to avoid spam
    # Key: (uid, symbol), Value: timestamp when last notification was sent
    _sl_notified = {}
    
    # Track last stale cleanup time per user (run every 5 minutes)
    _last_stale_cleanup = {}
    
    # Track deep loss notifications (position without SL in deep loss)
    # Key: (uid, symbol), Value: timestamp when notification was sent
    _deep_loss_notified = {}
    
    # Track close position notifications already sent to avoid spam
    # Key: (uid, symbol, account_type), Value: timestamp when notification was sent
    # Prevents duplicate close notifications when remove_active_position() fails (e.g., entry_price mismatch)
    _close_notified = {}

    while True:
        try:
            # Use cached list of active trading users (with API keys)
            for uid in get_active_trading_users():
                try:
                    if GLOBAL_PAUSED:
                        continue
                    
                    cfg  = get_user_config(uid)  # Cached
                    
                    # Skip banned users
                    if cfg.get("is_banned"):
                        continue
                    
                    lang = cfg.get("lang", DEFAULT_LANG)
                    t    = LANGS.get(lang, LANGS[DEFAULT_LANG])
                    use_atr = bool(cfg.get("use_atr", 1))  # Default to ATR enabled
                    
                    # Get ALL user targets (for multi-account monitoring)
                    user_targets = get_user_targets(uid) if UNIFIED_AVAILABLE else []
                    
                    # Fallback to legacy if no targets from unified
                    if not user_targets:
                        user_trading_mode = get_trading_mode(uid) or "demo"
                        k, s = get_user_credentials(uid)
                        if not k or not s:
                            continue
                        # Create targets_to_check list for legacy mode (Bybit only)
                        if user_trading_mode == "both":
                            targets_to_check = [("bybit", "demo"), ("bybit", "real")]
                        else:
                            targets_to_check = [("bybit", user_trading_mode)]
                    else:
                        # Use targets from unified architecture
                        targets_to_check = [(tgt.exchange, tgt.account_type) for tgt in user_targets]
                        user_trading_mode = targets_to_check[0][1] if targets_to_check else "demo"
                    
                    # Process EACH target for this user (supports multi-exchange and multi-account)
                    for current_exchange, current_account_type in targets_to_check:
                        # Get previous symbols to avoid duplicate notifications
                        cache_key = f"{uid}:{current_exchange}:{current_account_type}"
                        open_syms_prev = _open_syms_prev.get(cache_key, set())
                        
                        open_positions = await fetch_open_positions(uid, account_type=current_account_type)
                        open_positions = [p for p in open_positions if p["symbol"] not in BLACKLIST]
                        active = get_active_positions(uid, account_type=current_account_type)
                        
                        existing_syms = {ap["symbol"] for ap in active}
                        tf_map = {ap['symbol']: ap.get('timeframe', '24h') for ap in active}
                        now = int(time.time())
                        open_syms = {p["symbol"] for p in open_positions}
                        
                        # Update previous symbols cache at end of processing
                        _open_syms_prev[cache_key] = open_syms.copy()
                        
                        pending = get_pending_limit_orders(uid)
                        if pending:
                            try:
                                open_orders = await fetch_open_orders(uid, account_type=current_account_type)
                                open_ids = {o["orderId"] for o in open_orders}
                            except Exception as e:
                                logger.warning(f"fetch_open_orders failed, skip pending check this tick: {e}")
                                open_ids = None  

                            if open_ids is not None:
                                for po in pending:
                                    order_id = po["order_id"]
                                    sym      = po["symbol"]
                                    sig = fetch_signal_by_id(po["signal_id"]) or {}
                                    tf_for_sym = sig.get("tf") or "24h"

                                    if order_id not in open_ids:
                                        pos = next((p for p in open_positions if p["symbol"] == sym), None)
                                        if pos:
                                            # P0.5: Get use_atr from strategy settings
                                            strat_name = po.get("strategy") or "manual"
                                            cfg_pending = get_user_config(uid) or {}
                                            trade_params_pending = get_strategy_trade_params(
                                                uid, cfg_pending, sym, strat_name,
                                                side=po["side"], account_type=current_account_type
                                            )
                                            pos_use_atr_pending = trade_params_pending.get("use_atr", False)
                                            # Get leverage from position (Bybit returns it)
                                            pos_leverage = pos.get("leverage")
                                            if pos_leverage:
                                                pos_leverage = int(float(pos_leverage))
                                            
                                            # Use current_account_type from the loop
                                            add_active_position(
                                                user_id     = uid,
                                                symbol      = sym,
                                                side        = po["side"],
                                                entry_price = float(pos["avgPrice"]),
                                                size        = float(pos["size"]),
                                                timeframe   = tf_for_sym,
                                                signal_id   = po["signal_id"],
                                                strategy    = strat_name,
                                                account_type = current_account_type,
                                                use_atr     = pos_use_atr_pending,  # P0.5
                                                leverage    = pos_leverage  # Save actual leverage
                                            )
                                            await bot.send_message(
                                                uid,
                                                t['limit_order_filled'].format(
                                                    symbol = sym,
                                                    price  = pos["avgPrice"]
                                                )
                                            )
                                        else:
                                            await bot.send_message(
                                                uid,
                                                t['limit_order_cancelled'].format(symbol=sym, order_id=order_id)
                                            )                                
                                        remove_pending_limit_order(uid, order_id)

                        # Refresh active positions for this account type
                        active = get_active_positions(uid, account_type=current_account_type)
                        existing_syms = {ap["symbol"] for ap in active}
                        tf_map = {ap["symbol"]: ap.get("timeframe", "24h") for ap in active}
                        
                        for ap in active:
                            entry_ts = _parse_sqlite_ts_to_utc(ap["open_ts"])
                            elapsed = now - entry_ts 
                            tf = ap.get("timeframe", "24h")
                            secs = THRESHOLD_MAP.get(tf, THRESHOLD_MAP['24h'])
                            pos = next((p for p in open_positions if p["symbol"] == ap["symbol"]), None)
                            raw_tp = pos.get("takeProfit") if pos else None
                            sym = ap["symbol"]
                            ap_account_type = ap.get("account_type", current_account_type)
                            if pos and elapsed >= secs and float(pos.get("unrealisedPnl", 0)) < 0:
                                close_side = "Sell" if pos["side"] == "Buy" else "Buy"
                                size       = float(pos["size"])
                                try:
                                    await place_order(
                                        user_id=uid,
                                        symbol=pos["symbol"],
                                        side=close_side,
                                        orderType="Market",
                                        qty=size,
                                        account_type=current_account_type
                                    )
                                    await bot.send_message(
                                        uid,
                                        t['auto_close_position'].format(symbol=pos["symbol"], tf=tf)
                                    )
                                    # Use ap entry_price to prevent race condition
                                    remove_active_position(uid, pos["symbol"], account_type=ap_account_type, entry_price=ap.get("entry_price"))
                                    reset_pyramid(uid, pos["symbol"])
                                    _atr_triggered.pop((uid, pos["symbol"]), None)
                                    _sl_notified.pop((uid, pos["symbol"]), None)  # Clear SL notification cache
                                    _deep_loss_notified.pop((uid, pos["symbol"]), None)  # Clear deep loss cache
                                except Exception as e:
                                    logger.error(f"Auto-close {pos['symbol']} failed: {e}")
                                    
                        for p in open_positions:
                            sym     = p["symbol"]
                            entry   = float(p["avgPrice"])
                            raw_sl  = p.get("stopLoss")
                            size    = float(p["size"])
                            side    = p["side"]
                            
                            # Reset detected_strategy for each position
                            detected_strategy = None

                            if sym not in existing_syms:
                                # Check if we're in cooldown period after close_all
                                cooldown_end = _close_all_cooldown.get(uid, 0)
                                if now < cooldown_end:
                                    # Skip adding new positions during cooldown
                                    logger.info(f"[{uid}] Skipping {sym} - in close_all cooldown ({int(cooldown_end - now)}s left)")
                                    continue
                                
                                tf_for_sym = tf_map.get(sym, "24h") 
                                signal_id = get_last_signal_id(uid, sym, tf_for_sym)
                                
                                # Try to determine strategy from signal if available
                                detected_strategy = None
                                sig = None
                                
                                if signal_id:
                                    sig = fetch_signal_by_id(signal_id)
                                
                                # Fallback: search by raw_message if signal not found
                                if not sig:
                                    sig = get_last_signal_by_symbol_in_raw(sym)
                                    if sig:
                                        signal_id = sig.get("id")
                                        logger.debug(f"[{uid}] Found signal for {sym} via raw_message search: id={signal_id}")
                                
                                if sig:
                                    # Check signal source/strategy
                                    raw_msg = sig.get("raw_message", "")
                                    raw_upper = raw_msg.upper()
                                    if "SCRYPTOMERA" in raw_upper or "DROP CATCH" in raw_msg or "DROPSBOT" in raw_upper or "TIGHTBTC" in raw_upper:
                                        detected_strategy = "scryptomera"
                                    elif "SCALPER" in raw_upper and "⚡" in raw_msg:
                                        detected_strategy = "scalper"
                                    elif "ELCARO" in raw_upper or "🔥 ELCARO" in raw_msg or "🚀 ELCARO" in raw_msg:
                                        detected_strategy = "elcaro"
                                    elif "FIBONACCI" in raw_upper or "FIBONACCI EXTENSION" in raw_upper:
                                        detected_strategy = "fibonacci"
                                
                                # Use current_account_type from the loop
                                # If strategy not detected, use "manual" (position opened externally)
                                final_strategy = detected_strategy or "manual"
                                
                                # P0.5: Get use_atr from strategy settings
                                cfg_detected = get_user_config(uid) or {}
                                trade_params_detected = get_strategy_trade_params(
                                    uid, cfg_detected, sym, final_strategy,
                                    side=side, account_type=current_account_type
                                )
                                pos_use_atr_detected = trade_params_detected.get("use_atr", False)
                                
                                # Get leverage from position data (Bybit returns it)
                                pos_leverage = p.get("leverage")
                                if pos_leverage:
                                    pos_leverage = int(float(pos_leverage))
                                
                                add_active_position(
                                    user_id    = uid,
                                    symbol     = sym,
                                    side       = side,
                                    entry_price= entry,
                                    size       = size,
                                    timeframe  = tf_for_sym,
                                    signal_id  = signal_id,
                                    strategy   = final_strategy,
                                    account_type = current_account_type,
                                    use_atr    = pos_use_atr_detected,  # P0.5
                                    leverage   = pos_leverage  # Save actual leverage
                                )
                            
                                if detected_strategy:
                                    logger.info(f"[{uid}] Position {sym} detected with strategy={detected_strategy} from signal")
                                else:
                                    logger.info(f"[{uid}] Position {sym} added with strategy=manual (external/webapp)")

                                # Only send notification if not in cooldown
                                cooldown_end = _close_all_cooldown.get(uid, 0)
                                if now >= cooldown_end:
                                    # Format exchange and market type for display
                                    exchange_display = current_exchange.upper() if current_exchange else "BYBIT"
                                    market_type_display = {
                                        "demo": "Demo",
                                        "real": "Real",
                                        "testnet": "Testnet",
                                        "mainnet": "Mainnet",
                                        "paper": "Paper",
                                        "live": "Live"
                                    }.get(current_account_type, current_account_type.title())
                                
                                    await safe_send_notification(
                                        bot, uid,
                                        t['new_position'].format(
                                            symbol=sym, 
                                            entry=entry, 
                                            size=size,
                                            exchange=exchange_display,
                                            market_type=market_type_display
                                        )
                                    )

                            if raw_sl in (None, "", "0", 0):
                                # Get strategy: for new positions use detected_strategy,
                                # for existing positions get from active_positions table
                                if detected_strategy:
                                    # New position - use what we just detected
                                    strategy = detected_strategy
                                else:
                                    # Existing or unknown position - get from DB
                                    ap_for_sym = next((ap for ap in active if ap["symbol"] == sym), None)
                                    strategy = ap_for_sym.get("strategy") if ap_for_sym else None
                            
                                logger.debug(f"[{uid}] {sym}: SL/TP resolution with strategy={strategy}, side={side}")
                            
                                # Determine use_atr: strategy-specific takes priority over global
                                if strategy:
                                    strat_settings = db.get_strategy_settings(uid, strategy, exchange=current_exchange, account_type=current_account_type)
                                    strat_use_atr = strat_settings.get("use_atr")
                                    pos_use_atr = bool(strat_use_atr) if strat_use_atr is not None else use_atr
                                else:
                                    pos_use_atr = use_atr
                            
                                # Use strategy-aware SL/TP resolution WITH side for Scryptomera/Scalper
                                sl_pct, tp_pct = resolve_sl_tp_pct(cfg, sym, strategy=strategy, user_id=uid, side=side)
                                sl_price = round(
                                    entry * (1 - sl_pct/100) if side == "Buy" else entry * (1 + sl_pct/100), 6
                                )
                                tp_price = round(
                                    entry * (1 + tp_pct/100) if side == "Buy" else entry * (1 - tp_pct/100), 6
                                )
                                mark = float(p["markPrice"])
                                raw_tp = p.get("takeProfit")
                                current_tp = float(raw_tp) if raw_tp not in (None, "", 0, "0", 0.0) else None

                                try:
                                    # Check if we should notify about SL/TP changes
                                    # 1. Skip if position existed in previous iteration (not new)
                                    # 2. Skip if we're in cooldown period (positions being closed)
                                    # 3. Skip if we already notified for this position
                                    # 4. Skip if position already exists in DB (to avoid spam after bot restart)
                                    cooldown_end = _close_all_cooldown.get(uid, 0)
                                    sl_notify_key = (uid, sym)
                                    already_notified = sl_notify_key in _sl_notified
                                    position_existed_in_db = sym in existing_syms
                                    should_notify = (sym not in open_syms_prev) and (now >= cooldown_end) and not already_notified and not position_existed_in_db
                                
                                    # Helper to handle deep loss notification
                                    async def notify_deep_loss(symbol, side, entry, mark, move_pct):
                                        deep_loss_key = (uid, symbol)
                                        logger.info(f"[{uid}] {symbol}: Sending deep loss notification (loss: {move_pct:.2f}%)")
                                        if deep_loss_key in _deep_loss_notified:
                                            logger.debug(f"[{uid}] {symbol}: Already notified about deep loss, skipping")
                                            return  # Already notified
                                        _deep_loss_notified[deep_loss_key] = now
                                    
                                        # Calculate loss percentage
                                        loss_pct = abs(move_pct)
                                    
                                        # Create inline keyboard with options
                                        keyboard = [
                                            [
                                                InlineKeyboardButton(
                                                    t.get('btn_close_position', '❌ Закрыть позицию'),
                                                    callback_data=f"deep_loss:close:{symbol}"
                                                )
                                            ],
                                            [
                                                InlineKeyboardButton(
                                                    t.get('btn_enable_dca', '📈 Включить DCA добор'),
                                                    callback_data=f"deep_loss:dca:{symbol}"
                                                )
                                            ],
                                            [
                                                InlineKeyboardButton(
                                                    t.get('btn_ignore', '🔇 Игнорировать'),
                                                    callback_data=f"deep_loss:ignore:{symbol}"
                                                )
                                            ]
                                        ]
                                    
                                        msg_text = t.get('deep_loss_alert', 
                                            "⚠️ <b>Позиция в глубоком минусе!</b>\n\n"
                                            "📊 <b>{symbol}</b> ({side})\n"
                                            "📉 Убыток: <code>{loss_pct:.2f}%</code>\n"
                                            "💰 Вход: <code>{entry}</code>\n"
                                            "📍 Текущая: <code>{mark}</code>\n\n"
                                            "❌ Стоп-лосс невозможно установить выше цены входа.\n\n"
                                            "<b>Что делать?</b>\n"
                                            "• <b>Закрыть</b> - зафиксировать убыток\n"
                                            "• <b>DCA добор</b> - усреднить позицию доборами\n"
                                            "• <b>Игнорировать</b> - оставить как есть"
                                        ).format(
                                            symbol=symbol,
                                            side="LONG" if side == "Buy" else "SHORT",
                                            loss_pct=loss_pct,
                                            entry=entry,
                                            mark=mark
                                        )
                                    
                                        try:
                                            await safe_send_notification(
                                                bot, uid,
                                                msg_text,
                                                parse_mode="HTML",
                                                reply_markup=InlineKeyboardMarkup(keyboard)
                                            )
                                        except Exception as e:
                                            logger.warning(f"Failed to send deep loss notification to {uid}: {e}")
                                
                                    if not pos_use_atr:
                                        kwargs = {"sl_price": sl_price}
                                        if current_tp is None:
                                            if (side == "Buy" and tp_price > mark) or (side == "Sell" and tp_price < mark):
                                                kwargs["tp_price"] = tp_price
                                        try:
                                            result = await set_trading_stop(uid, sym, **kwargs, side_hint=side)
                                        
                                            if result == "deep_loss":
                                                # Calculate move_pct for deep loss notification
                                                move_pct_local = (mark - entry) / entry * 100 if side == "Buy" else (entry - mark) / entry * 100
                                                logger.debug(f"[{uid}] {sym} deep_loss: entry={entry}, mark={mark}, side={side}, move_pct={move_pct_local:.2f}%")
                                                await notify_deep_loss(sym, side, entry, mark, move_pct_local)
                                                continue
                                        except RuntimeError as e:
                                            if "no open positions" in str(e).lower():
                                                logger.debug(f"{sym}: Position closed before SL/TP could be set")
                                                continue
                                            raise
                                        # Only notify if truly new position AND not in cooldown AND not already notified
                                        if should_notify:
                                            _sl_notified[sl_notify_key] = now
                                            if "tp_price" in kwargs:
                                                await safe_send_notification(
                                                    bot, uid,
                                                    t['fixed_sl_tp'].format(symbol=sym, sl=sl_price, tp=tp_price)
                                                )
                                            else:
                                                await safe_send_notification(
                                                    bot, uid,
                                                    t['sl_set_only'].format(symbol=sym, sl_price=sl_price)
                                                )
                                    else:
                                        try:
                                            result = await set_trading_stop(uid, sym, sl_price=sl_price, side_hint=side)
                                            if result == "deep_loss":
                                                # Calculate move_pct for deep loss notification
                                                move_pct_local = (mark - entry) / entry * 100 if side == "Buy" else (entry - mark) / entry * 100
                                                logger.debug(f"[{uid}] {sym} deep_loss ATR: entry={entry}, mark={mark}, side={side}, move_pct={move_pct_local:.2f}%")
                                                await notify_deep_loss(sym, side, entry, mark, move_pct_local)
                                                continue
                                        except RuntimeError as e:
                                            if "no open positions" in str(e).lower():
                                                logger.debug(f"{sym}: Position closed before SL could be set")
                                                continue
                                            raise
                                        # Only notify if truly new position AND not in cooldown AND not already notified
                                        if should_notify:
                                            _sl_notified[sl_notify_key] = now
                                            await safe_send_notification(bot, uid, t['sl_auto_set'].format(price=sl_price))
                                except Exception as e:
                                    if "no open positions" not in str(e).lower():
                                        logger.error(f"Errors with SL/TP for {sym}: {e}")

                        active = get_active_positions(uid, account_type=current_account_type)

                        for ap in active:
                            sym = ap["symbol"]
                            ap_account_type = ap.get("account_type", "demo")

                            if _skip_until.get((uid, sym), 0) > now:
                                continue

                            if sym not in open_syms:
                                logger.info(f"[{uid}] Position {sym} closed - detecting reason...")
                                rec = await fetch_last_closed_pnl(uid, sym)
                            
                                if rec is None:
                                    # No closed PnL record - clean up silently
                                    logger.debug(f"[{uid}] No closed PnL for {sym}, cleaning up")
                                    try:
                                        # Pass entry_price to avoid race condition
                                        remove_active_position(uid, sym, account_type=ap_account_type, entry_price=ap.get("entry_price"))
                                        reset_pyramid(uid, sym)
                                    finally:
                                        _atr_triggered.pop((uid, sym), None)
                                        _sl_notified.pop((uid, sym), None)
                                        _deep_loss_notified.pop((uid, sym), None)
                                    continue
                            
                                logger.info(f"[{uid}] Closed PnL for {sym}: entry={rec.get('avgEntryPrice')}, exit={rec.get('avgExitPrice')}, pnl={rec.get('closedPnl')}")

                                entry_price = float(rec["avgEntryPrice"])
                                exit_price  = float(rec["avgExitPrice"])
                                pos_side = ap.get("side", "Buy")
                                
                                # CRITICAL: Validate that closed PnL record matches our position
                                # Bybit API may return stale data from previous positions
                                db_entry_price = ap.get("entry_price")
                                if db_entry_price:
                                    price_diff_pct = abs(entry_price - db_entry_price) / db_entry_price * 100
                                    if price_diff_pct > 3.0:  # >3% difference means wrong record
                                        logger.warning(
                                            f"[{uid}] {sym}: Closed PnL entry price mismatch! "
                                            f"API={entry_price:.6f}, DB={db_entry_price:.6f}, diff={price_diff_pct:.1f}%. "
                                            f"Skipping - waiting for correct closed PnL record."
                                        )
                                        # Skip processing this iteration - wait for fresh data
                                        continue
                            
                                # Get strategy-specific SL/TP percentages for better detection
                                position_strategy = ap.get("strategy")
                                if position_strategy:
                                    strat_sl, strat_tp = resolve_sl_tp_pct(cfg, sym, strategy=position_strategy, user_id=uid, side=pos_side)
                                else:
                                    strat_sl = float(cfg.get("sl_percent") or DEFAULT_SL_PCT)
                                    strat_tp = float(cfg.get("tp_percent") or DEFAULT_TP_PCT)
                            
                                exit_reason, exit_order_type = await detect_exit_reason(
                                    uid, sym, 
                                    entry_price=entry_price, 
                                    exit_price=exit_price, 
                                    side=pos_side,
                                    sl_pct=strat_sl,
                                    tp_pct=strat_tp
                                )
                                logger.info(f"[{uid}] Exit reason for {sym}: {exit_reason} (order_type={exit_order_type})")
                                reason_text = exit_reason  

                                try:
                                    sig = fetch_signal_by_id(ap["signal_id"]) or {}
                                
                                    # Determine strategy: from position or fallback to signal detection
                                    if not position_strategy and sig:
                                        raw_msg = sig.get("raw_message") or ""
                                        if "DropsBot" in raw_msg or "DROP CATCH" in raw_msg or "TIGHTBTC" in raw_msg:
                                            position_strategy = "scryptomera"
                                        elif "⚡" in raw_msg and "Scalper" in raw_msg:
                                            position_strategy = "scalper"
                                        elif "🚀 Elcaro" in raw_msg or "ElCaro" in raw_msg:
                                            position_strategy = "elcaro"
                                        elif "Fibonacci" in raw_msg or "FIBONACCI EXTENSION" in raw_msg.upper():
                                            position_strategy = "fibonacci"
                                
                                    log_exit_and_remove_position(
                                        user_id=uid,
                                        signal_id=ap["signal_id"],
                                        symbol=sym,
                                        side=ap["side"],
                                        entry_price=entry_price,
                                        exit_price=exit_price,
                                        exit_reason=exit_reason,
                                        size=float(rec.get("closedSize") or ap.get("size") or 0.0),
                                        signal_source=("bitk" if (sig.get("raw_message") and ("DROP CATCH" in sig["raw_message"] or "TIGHTBTC" in sig["raw_message"])) else None),
                                        rsi=sig.get("rsi"), bb_hi=sig.get("bb_hi"), bb_lo=sig.get("bb_lo"),
                                        oi_prev=sig.get("oi_prev"), oi_now=sig.get("oi_now"), oi_chg=sig.get("oi_chg"),
                                        vol_from=sig.get("vol_from"), vol_to=sig.get("vol_to"),
                                        price_chg=sig.get("price_chg"), vol_delta=sig.get("vol_delta"),
                                        sl_price=exit_price if exit_reason=="SL" else None,
                                        tp_price=exit_price if exit_reason=="TP" else None,
                                        timeframe=ap.get("timeframe"),
                                        entry_ts_ms=int(_parse_sqlite_ts_to_utc(ap["open_ts"]) * 1000),
                                        exit_order_type=exit_order_type,
                                        strategy=position_strategy,
                                        account_type=ap_account_type,
                                    )

                                    pnl_from_exch = rec.get("closedPnl")
                                    rate_from_exch = rec.get("closedPnlRate")  # ROE as decimal (0.05 = 5%)
                                    leverage = float(rec.get("leverage") or ap.get("leverage") or 10)
                                
                                    size_for_calc = float(rec.get("closedSize") or ap.get("size") or 0.0)
                                    pnl_calc, pct_calc = _calc_pnl(entry_price, exit_price, ap["side"], size_for_calc)
                                
                                    # PnL value (prefer Bybit API)
                                    try:
                                        pnl_value = float(pnl_from_exch)
                                    except Exception:
                                        pnl_value = pnl_calc
                                
                                    # Percent value - show PRICE CHANGE %, not ROE
                                    # Our calc_qty formula doesn't use leverage, so showing ROE is misleading
                                    # We show the actual price change percentage instead
                                    pct_value = None
                                    if rate_from_exch is not None:
                                        try:
                                            # Bybit closedPnlRate is ROE - convert back to price change
                                            roe_pct = float(rate_from_exch) * 100.0
                                            # Price change = ROE / leverage
                                            pct_value = roe_pct / leverage if leverage > 0 else roe_pct
                                        except Exception:
                                            pass
                                
                                    # Fallback: use calculated price change directly (no leverage multiplication)
                                    if pct_value is None:
                                        pct_value = pct_calc  # Just price change %, NOT multiplied by leverage
                                    
                                    # CRITICAL: Ensure pct_value sign matches pnl_value sign
                                    # Sometimes Bybit API returns wrong sign for closedPnlRate
                                    if pnl_value > 0 and pct_value < 0:
                                        pct_value = abs(pct_value)
                                        logger.warning(f"[{uid}] {sym}: Fixed pct sign mismatch (pnl={pnl_value}, pct was negative)")
                                    elif pnl_value < 0 and pct_value > 0:
                                        pct_value = -abs(pct_value)
                                        logger.warning(f"[{uid}] {sym}: Fixed pct sign mismatch (pnl={pnl_value}, pct was positive)")
                                
                                    logger.info(f"[{uid}] PnL details for {sym}: pnl={pnl_value:.2f}, rate_from_api={rate_from_exch}, pct={pct_value:.2f}%, leverage={leverage}")
                                
                                    # Get strategy name for display (use already determined position_strategy)
                                    strategy_name = position_strategy or "unknown"
                                    
                                    strategy_display = {
                                        "scryptomera": "Scryptomera",
                                        "scalper": "Scalper", 
                                        "rsi_bb": "RSI+BB",
                                        "oi": "OI",
                                        "elcaro": "Elcaro",
                                        "fibonacci": "Fibonacci",
                                        "manual": "Manual",
                                    }.get(strategy_name, strategy_name.title() if strategy_name else "Unknown")
                                    
                                    # Format exchange and market type for display
                                    exchange_display = current_exchange.upper() if current_exchange else "BYBIT"
                                    market_type_display = {
                                        "demo": "Demo",
                                        "real": "Real",
                                        "testnet": "Testnet",
                                        "mainnet": "Mainnet",
                                        "paper": "Paper",
                                        "live": "Live"
                                    }.get(current_account_type, current_account_type.title())
                                
                                    # Deduplication: check if close notification already sent (prevents spam when remove_active_position fails)
                                    close_notify_key = (uid, sym, ap_account_type)
                                    now = int(time.time())
                                    CLOSE_NOTIFY_COOLDOWN = 3600  # 1 hour cooldown for same position close
                                    last_close_notify = _close_notified.get(close_notify_key, 0)
                                    
                                    if now - last_close_notify < CLOSE_NOTIFY_COOLDOWN:
                                        logger.debug(f"[{uid}] Skipping close notification for {sym} (already sent {now - last_close_notify}s ago)")
                                    else:
                                        _close_notified[close_notify_key] = now
                                        logger.info(f"[{uid}] Sending close notification for {sym}: reason={reason_text}, strategy={strategy_display}, pnl={pnl_value:.2f}")
                                        await safe_send_notification(
                                            bot, uid,
                                            t['position_closed'].format(
                                                symbol=sym,
                                                reason=reason_text,
                                                strategy=strategy_display,
                                                entry=float(entry_price),
                                                exit=float(exit_price),
                                                pnl=pnl_value,
                                                pct=pct_value,
                                                exchange=exchange_display,
                                                market_type=market_type_display,
                                            ),
                                            parse_mode="Markdown"
                                        )



                                except Exception as e:
                                    if is_db_full_error(e):
                                        if once_per((uid, "db_full", sym), NOTICE_WINDOW):
                                            await safe_send_notification(
                                                bot, uid,
                                                f"Logs are temporarily not written (there is not enough space). On {sym}, I switch to silent mode for 1 hour."
                                            )
                                        _skip_until[(uid, sym)] = int(time.time()) + MUTE_TTL
                                    else:
                                        if once_per((uid, "position_closed_error", sym), 300):
                                            await safe_send_notification(bot, uid, t['position_closed_error'].format(symbol=sym, error=str(e)))
                                finally:
                               
                                    try:
                                        reset_pyramid(uid, sym)
                                    finally:
                                        _atr_triggered.pop((uid, sym), None)
                                        _sl_notified.pop((uid, sym), None)  # Clear SL notification cache
                                        _deep_loss_notified.pop((uid, sym), None)  # Clear deep loss notification cache

                        active = get_active_positions(uid, account_type=current_account_type)
                        tf_map = { ap['symbol']: ap.get('timeframe','15m') for ap in active }  # Default 15m
                        strategy_map = { ap['symbol']: ap.get('strategy') for ap in active }
                        account_type_map = { ap['symbol']: ap.get('account_type', 'demo') for ap in active }
                        db_syms = set(tf_map.keys())

                        for pos in open_positions:
                            sym        = pos["symbol"]
                            side       = pos["side"]
                            entry      = float(pos["avgPrice"])
                            raw_sl     = pos.get("stopLoss")
                            raw_tp     = pos.get("takeProfit")
                            current_sl = float(raw_sl) if raw_sl not in (None, "", 0, "0", 0.0) else None
                            current_tp = float(raw_tp) if raw_tp not in (None, "", 0, "0", 0.0) else None
                            
                            # Log if position is not tracked in DB
                            if sym not in db_syms:
                                logger.debug(f"[{uid}] {sym}: Position not in active_positions DB, using default tf=15m")

                            coin_cfg    = COIN_PARAMS.get(sym, COIN_PARAMS["DEFAULT"])
                        
                            # Get strategy for this position
                            pos_strategy = strategy_map.get(sym)
                        
                            # Fallback: try to determine strategy from signal if not in DB
                            if not pos_strategy:
                                ap_for_sym = next((ap for ap in active if ap["symbol"] == sym), None)
                                if ap_for_sym and ap_for_sym.get("signal_id"):
                                    sig = fetch_signal_by_id(ap_for_sym["signal_id"])
                                    if sig:
                                        raw_msg = sig.get("raw_message", "")
                                        if "SCRYPTOMERA" in raw_msg.upper() or "DROP CATCH" in raw_msg:
                                            pos_strategy = "scryptomera"
                                        elif "SCALPER" in raw_msg.upper() or "⚡" in raw_msg:
                                            pos_strategy = "scalper"
                                        elif "ELCARO" in raw_msg.upper() or "🔥" in raw_msg:
                                            pos_strategy = "elcaro"
                                        elif sig.get("source"):
                                            source = sig.get("source", "").lower()
                                            if "scryptomera" in source or "bitk" in source:
                                                pos_strategy = "scryptomera"
                                            elif "scalper" in source:
                                                pos_strategy = "scalper"
                                            elif "elcaro" in source:
                                                pos_strategy = "elcaro"
                                    
                                        # Update DB with detected strategy for future iterations
                                        if pos_strategy:
                                            logger.info(f"[{uid}] {sym}: Detected strategy={pos_strategy} from signal, updating DB")
                                            try:
                                                pos_account_type = account_type_map.get(sym, "demo")
                                                update_position_strategy(uid, sym, pos_strategy, account_type=pos_account_type)
                                            except Exception as e:
                                                logger.warning(f"[{uid}] Failed to update position strategy: {e}")
                        
                            # Get SL/TP from strategy settings if available, otherwise use global
                            if pos_strategy:
                                # Get context for this position
                                pos_context = get_user_trading_context(uid)
                                pos_acct = account_type_map.get(sym, pos_context["account_type"])
                                strat_params = get_strategy_trade_params(uid, cfg, sym, pos_strategy, side=side,
                                                                         exchange=pos_context["exchange"], account_type=pos_acct)
                                sl_pct = strat_params["sl_pct"]
                                tp_pct = strat_params["tp_pct"]
                                risk_pct_for_dca = strat_params["percent"]
                            else:
                                raw_user_sl = cfg.get("sl_percent", 0)
                                if 0 < raw_user_sl <= 50:
                                    sl_pct = raw_user_sl
                                else:
                                    sl_pct = coin_cfg.get("sl_pct", DEFAULT_SL_PCT)
                                raw_user_tp = cfg.get("tp_percent", 0)
                                if raw_user_tp > sl_pct:
                                    tp_pct = raw_user_tp
                                else:
                                    tp_pct = coin_cfg.get("tp_pct", DEFAULT_TP_PCT)
                                risk_pct_for_dca = float(cfg.get("percent", 1) or 0)

                            tf          = tf_map.get(sym, "15m")  # Default to 15m if not in DB for more responsive ATR
                            tf_cfg      = TIMEFRAME_PARAMS.get(tf, TIMEFRAME_PARAMS["15m"])
                        
                            # Get account_type for this position from map (moved up for strategy settings)
                            pos_account_type = account_type_map.get(sym, "demo")
                        
                            # Get ATR params: priority is side-specific > strategy settings > timeframe defaults
                            if pos_strategy:
                                strat_settings = db.get_strategy_settings(uid, pos_strategy, exchange=current_exchange, account_type=pos_account_type)
                                side_prefix = "long" if side == "Buy" else "short"
                            
                                # Get side-specific ATR settings, fallback to general, then timeframe defaults
                                side_atr_periods = strat_settings.get(f"{side_prefix}_atr_periods")
                                side_atr_mult = strat_settings.get(f"{side_prefix}_atr_multiplier_sl")
                                side_atr_trigger = strat_settings.get(f"{side_prefix}_atr_trigger_pct")
                            
                                atr_periods = side_atr_periods if side_atr_periods is not None else (
                                    strat_settings.get("atr_periods") if strat_settings.get("atr_periods") is not None else tf_cfg["atr_periods"]
                                )
                                atr_mult_sl = side_atr_mult if side_atr_mult is not None else (
                                    strat_settings.get("atr_multiplier_sl") if strat_settings.get("atr_multiplier_sl") is not None else tf_cfg["atr_multiplier_sl"]
                                )
                                trigger_pct = side_atr_trigger if side_atr_trigger is not None else (
                                    strat_settings.get("atr_trigger_pct") if strat_settings.get("atr_trigger_pct") is not None else tf_cfg["atr_trigger_pct"]
                                )
                            
                                # Strategy-specific use_atr: if set in strategy (not None), use it; otherwise fall back to global
                                strat_use_atr = strat_settings.get("use_atr")
                                position_use_atr = bool(strat_use_atr) if strat_use_atr is not None else use_atr
                                
                                # Log side-specific settings resolution for debugging
                                logger.debug(f"[{uid}] {sym}: Side-specific ATR - side={side}, prefix={side_prefix}, "
                                            f"side_trigger={side_atr_trigger}, strat_trigger={strat_settings.get('atr_trigger_pct')}, tf_trigger={tf_cfg['atr_trigger_pct']}, final_trigger={trigger_pct}")
                            else:
                                atr_periods = tf_cfg["atr_periods"]
                                atr_mult_sl = tf_cfg["atr_multiplier_sl"]
                                trigger_pct = tf_cfg["atr_trigger_pct"]
                                position_use_atr = use_atr  # Use global setting

                            # Log ATR params being used for debugging
                            logger.debug(f"[{uid}] {sym}: ATR params - strategy={pos_strategy}, side={side}, "
                                        f"atr_periods={atr_periods}, atr_mult={atr_mult_sl}, trigger_pct={trigger_pct}, use_atr={position_use_atr}")

                            mark     = float(pos["markPrice"])
                            move_pct = (mark - entry) / entry * 100 if side == "Buy" else (entry - mark) / entry * 100
                            key = (uid, sym)

                            # User-configurable DCA settings
                            dca_enabled = bool(cfg.get("dca_enabled", 0))
                            dca_pct_1 = float(cfg.get("dca_pct_1", 10.0))
                            dca_pct_2 = float(cfg.get("dca_pct_2", 25.0))

                            # pos_account_type already defined above for strategy settings

                            # --- DCA при -dca_pct_1% против нас (только если DCA включён) ---
                            if dca_enabled and move_pct <= -dca_pct_1:
                                if not get_dca_flag(uid, sym, 10, account_type=pos_account_type):
                                    try:
                                        # Use strategy-specific percent if available
                                        if risk_pct_for_dca > 0:
                                            add_qty = await calc_qty(
                                                uid,
                                                sym,
                                                price=mark,
                                                risk_pct=risk_pct_for_dca,
                                                sl_pct=sl_pct,
                                                account_type=pos_account_type
                                            )
                                            if add_qty > 0:
                                                await place_order(
                                                    user_id=uid,
                                                    symbol=sym,
                                                    side=side,
                                                    orderType="Market",
                                                    qty=add_qty,
                                                    account_type=pos_account_type
                                                )
                                                set_dca_flag(uid, sym, 10, True, account_type=pos_account_type)
                                                try:
                                                    await safe_send_notification(
                                                        bot, uid,
                                                        t.get(
                                                            'dca_10pct',
                                                            "DCA −{pct}%: добор по {symbol} qty={qty} @ {price}"
                                                        ).format(
                                                            pct=dca_pct_1,
                                                            symbol=sym,
                                                            qty=add_qty,
                                                            price=mark
                                                        )
                                                    )
                                                except Exception:
                                                    pass
                                    except Exception as e:
                                        logger.error(f"{sym}: DCA −{dca_pct_1}% failed for {uid}: {e}", exc_info=True)

                            # --- DCA при -dca_pct_2% против нас (только если DCA включён) ---
                            if dca_enabled and move_pct <= -dca_pct_2:
                                if not get_dca_flag(uid, sym, 25, account_type=pos_account_type):
                                    try:
                                        # Use strategy-specific percent if available
                                        if risk_pct_for_dca > 0:
                                            add_qty = await calc_qty(
                                                uid,
                                                sym,
                                                price=mark,
                                                risk_pct=risk_pct_for_dca,
                                                sl_pct=sl_pct,
                                                account_type=pos_account_type
                                            )
                                            if add_qty > 0:
                                                await place_order(
                                                    user_id=uid,
                                                    symbol=sym,
                                                    side=side,
                                                    orderType="Market",
                                                    qty=add_qty,
                                                    account_type=pos_account_type
                                                )
                                                set_dca_flag(uid, sym, 25, True, account_type=pos_account_type)
                                                try:
                                                    await safe_send_notification(
                                                        bot, uid,
                                                        t.get(
                                                            'dca_25pct',
                                                            "DCA −{pct}%: добор по {symbol} qty={qty} @ {price}"
                                                        ).format(
                                                            pct=dca_pct_2,
                                                            symbol=sym,
                                                            qty=add_qty,
                                                            price=mark
                                                        )
                                                    )
                                                except Exception:
                                                    pass
                                    except Exception as e:
                                        logger.error(f"{sym}: DCA −{dca_pct_2}% failed for {uid}: {e}", exc_info=True)

                            if not position_use_atr:
                                # Use side-specific SL/TP for Scryptomera/Scalper strategies
                                sl_pct, tp_pct = resolve_sl_tp_pct(cfg, sym, strategy=pos_strategy, user_id=uid, side=side)
                                sl0 = round(
                                    entry * (1 - sl_pct/100) if side == "Buy"
                                    else entry * (1 + sl_pct/100),
                                    6
                                )
                                tp0 = round(
                                    entry * (1 + tp_pct/100) if side == "Buy"
                                    else entry * (1 - tp_pct/100),
                                    6
                                )

                                if current_sl is None or current_tp is None:
                                    kwargs = {}
                                    if current_sl is None:
                                        kwargs["sl_price"] = sl0
                                    if current_tp is None:
                                        if (side == "Buy" and tp0 > mark) or (side == "Sell" and tp0 < mark):
                                            kwargs["tp_price"] = tp0
                                    if kwargs:
                                        try:
                                            await set_trading_stop(uid, sym, **kwargs, side_hint=side)
                                            logger.info(f"[{uid}] {sym}: Fixed init → {kwargs}")
                                        except RuntimeError as e:
                                            if "no open positions" in str(e).lower():
                                                logger.debug(f"{sym}: Position already closed, skipping SL/TP update")
                                            else:
                                                raise
                                    continue
                           
                                # if move_pct >= trigger_pct:
                                #     be = entry
                                #     cand = _stricter_sl(side, be, current_sl)
                                #     if cand is not None:
                                #         await set_trading_stop(uid, sym, sl_price=cand, side_hint=side)
                                #         logger.info(f"{sym}: SL moved to breakeven {cand}")
                                #     continue
                           
                                cand = _stricter_sl(side, sl0, current_sl)
                                if cand is not None:
                                    try:
                                        await set_trading_stop(uid, sym, sl_price=cand, side_hint=side)
                                        logger.info(f"{sym}: Fixed SL tightened to {cand}")
                                    except RuntimeError as e:
                                        if "no open positions" in str(e).lower():
                                            logger.debug(f"{sym}: Position already closed, skipping SL update")
                                        else:
                                            raise
                                continue
                        
                            if position_use_atr:
                                # Log current ATR state for debugging
                                logger.info(f"[ATR-CHECK] {sym} uid={uid} entry={entry} mark={mark} move_pct={move_pct:.2f}% trigger_pct={trigger_pct}% triggered={_atr_triggered.get(key, False)} current_sl={current_sl}")
                                
                                if move_pct < trigger_pct and not _atr_triggered.get(key, False):
                                    # Log ATR status for debugging
                                    logger.info(f"[ATR-WAIT] {sym} move_pct={move_pct:.2f}% < trigger_pct={trigger_pct}% - waiting for trigger")
                                
                                    # Use strategy-specific SL% if available (already calculated above)
                                    base_sl = entry * (1 - sl_pct/100) if side == "Buy" else entry * (1 + sl_pct/100)

                                    tick = (await get_symbol_filters(uid, sym))["tickSize"]

                                    sl0 = quantize_up(base_sl, tick) if side == "Buy" else quantize(base_sl, tick)
                                    should_update = (
                                        current_sl is None
                                        or (side == "Buy"  and sl0 > current_sl)
                                        or (side == "Sell" and sl0 < current_sl)  
                                    )
                                    if should_update:
                                        try:
                                            await set_trading_stop(uid, sym, sl_price=sl0, side_hint=side)
                                            logger.info(f"[{uid}] {sym}: ATR-initial SL set/updated to {sl0}")
                                        except RuntimeError as e:
                                            if "no open positions" in str(e).lower():
                                                logger.debug(f"{sym}: Position already closed")
                                            else:
                                                raise
                                    continue

                                _atr_triggered[key] = True
                                logger.info(f"[ATR-ACTIVATED] {sym} uid={uid} - ATR trailing now active!")

                                filt = await get_symbol_filters(uid, sym)
                                tick = filt["tickSize"]
                                try:
                                    atr_val = await calc_atr(sym, interval=ATR_INTERVAL, periods=atr_periods)
                                except Exception as e:
                                    logger.warning(f"{sym}: failed to count ATR: {e}")
                                    continue

                                logger.info(f"[ATR-TRAIL] {sym} side={side} mark={mark:.6f} entry={entry:.6f} move_pct={move_pct:.2f}% atr_val={atr_val:.6f} atr_mult={atr_mult_sl} current_sl={current_sl}")

                                if side == "Buy":
                                    cand_raw   = mark - atr_val * atr_mult_sl
                                    cand_ceil  = quantize_up(cand_raw, tick)
                                    max_allowed = quantize(mark - tick, tick)    
                                    atr_cand    = min(cand_ceil, max_allowed)

                                    new_sl = max(current_sl or -float("inf"), atr_cand) 
                                    logger.info(f"[ATR-TRAIL] {sym} LONG: cand_raw={cand_raw:.6f} atr_cand={atr_cand:.6f} new_sl={new_sl:.6f} should_update={current_sl is None or new_sl > current_sl}")
                                    if current_sl is None or new_sl > current_sl:
                                        try:
                                            result = await set_trading_stop(uid, sym, sl_price=new_sl, side_hint=side, is_trailing=True)
                                            logger.info(f"[ATR-TRAIL] {sym} LONG: SL updated {current_sl} -> {new_sl}, result={result}")
                                        except RuntimeError as e:
                                            if "no open positions" in str(e).lower():
                                                logger.debug(f"{sym}: Position closed, skipping ATR SL")
                                            else:
                                                raise

                                else:  
                                    cand_raw    = mark + atr_val * atr_mult_sl
                                    cand_floor  = quantize(cand_raw, tick)
                                    min_allowed = quantize_up(mark + tick, tick)        
                                    atr_cand     = max(cand_floor, min_allowed)

                                    new_sl = min(current_sl or float("inf"), atr_cand)  
                                    logger.info(f"[ATR-TRAIL] {sym} SHORT: cand_raw={cand_raw:.6f} atr_cand={atr_cand:.6f} new_sl={new_sl:.6f} should_update={current_sl is None or new_sl < current_sl}")
                                    if current_sl is None or new_sl < current_sl:
                                        try:
                                            result = await set_trading_stop(uid, sym, sl_price=new_sl, side_hint=side, is_trailing=True)
                                            logger.info(f"[ATR-TRAIL] {sym} SHORT: SL updated {current_sl} -> {new_sl}, result={result}")
                                        except RuntimeError as e:
                                            if "no open positions" in str(e).lower():
                                                logger.debug(f"{sym}: Position closed, skipping ATR SL")
                                            else:
                                                raise
                    
                        # Save current symbols for next iteration to prevent duplicate notifications
                        _open_syms_prev[cache_key] = open_syms
                        
                        # === STALE POSITION CLEANUP (every 5 minutes per user/account) ===
                        cleanup_key = f"{uid}:{current_exchange}:{current_account_type}"
                        cleanup_interval = 300  # 5 minutes
                        if now - _last_stale_cleanup.get(cleanup_key, 0) >= cleanup_interval:
                            _last_stale_cleanup[cleanup_key] = now
                            # Get DB positions for this account
                            db_positions = get_active_positions(uid, account_type=current_account_type)
                            # Find stale: in DB but not on exchange
                            for db_pos in db_positions:
                                db_sym = db_pos.get("symbol")
                                if db_sym not in open_syms:
                                    # Stale position - not on exchange anymore
                                    logger.info(f"[STALE-CLEANUP] {uid} {db_sym} - removing from DB (not on exchange)")
                                    try:
                                        remove_active_position(uid, db_sym, account_type=current_account_type, entry_price=db_pos.get("entry_price"))
                                        reset_pyramid(uid, db_sym)
                                        _atr_triggered.pop((uid, db_sym), None)
                                        _sl_notified.pop((uid, db_sym), None)
                                        _deep_loss_notified.pop((uid, db_sym), None)
                                    except Exception as e:
                                        logger.warning(f"[STALE-CLEANUP] Failed to remove {db_sym} for {uid}: {e}")

                except Exception as e:
                    logger.error(f"Monitoring error for {uid}: {e}", exc_info=True)

            await asyncio.sleep(CHECK_INTERVAL)

        except Exception as e:
            logger.exception(f"Critical error in loop, restart after {CHECK_INTERVAL}s: {e}")
            await asyncio.sleep(CHECK_INTERVAL)


async def spot_tp_rebalance_loop(app: Application):
    """
    Background loop for spot trading monitoring:
    - Check Take Profit levels and auto-sell when targets reached
    - Check portfolio rebalancing needs
    
    Runs every 15 minutes.
    """
    bot = app.bot
    logger.info("Starting spot_tp_rebalance_loop")
    
    while True:
        try:
            await asyncio.sleep(900)  # Check every 15 minutes
            
            if GLOBAL_PAUSED:
                continue
            
            for uid in get_all_users():
                try:
                    cfg = get_user_config(uid)
                    spot_settings = cfg.get("spot_settings", {})
                    
                    # Check if user has API credentials
                    k, s = get_user_credentials(uid)
                    if not k or not s:
                        continue
                    
                    lang = cfg.get("lang", DEFAULT_LANG)
                    t = LANGS.get(lang, LANGS[DEFAULT_LANG])
                    account_type = spot_settings.get("trading_mode", "demo")
                    
                    # === Take Profit Monitoring ===
                    if spot_settings.get("tp_enabled"):
                        tp_levels = spot_settings.get("tp_levels", DEFAULT_SPOT_TP_LEVELS)
                        purchase_history = spot_settings.get("purchase_history", {})
                        sold_levels = spot_settings.get("sold_levels", {})  # Track which levels were hit
                        
                        balances = await fetch_spot_balance(uid, account_type=account_type)
                        
                        for coin, qty in balances.items():
                            if coin == "USDT" or qty < 0.00001:
                                continue
                            
                            symbol = f"{coin}USDT"
                            
                            # Get average purchase price from history
                            avg_price = purchase_history.get(coin, {}).get("avg_price", 0)
                            if avg_price <= 0:
                                continue
                            
                            try:
                                ticker = await get_spot_ticker(uid, symbol, account_type)
                                if not ticker:
                                    continue
                                    
                                current_price = float(ticker.get("lastPrice", 0))
                                if current_price <= 0:
                                    continue
                                
                                gain_pct = ((current_price - avg_price) / avg_price) * 100
                                
                                # Check each TP level
                                coin_sold_levels = sold_levels.get(coin, [])
                                
                                for i, level in enumerate(tp_levels):
                                    if i in coin_sold_levels:
                                        continue  # Already sold at this level
                                    
                                    if gain_pct >= level["gain_pct"]:
                                        # TP level reached! Sell partial
                                        sell_qty = qty * (level["sell_pct"] / 100.0)
                                        
                                        if sell_qty < 0.00001:
                                            continue
                                        
                                        try:
                                            result = await place_spot_order(
                                                user_id=uid,
                                                symbol=symbol,
                                                side="Sell",
                                                qty=sell_qty,
                                                order_type="Market",
                                                account_type=account_type,
                                            )
                                            
                                            # Mark level as sold
                                            if coin not in sold_levels:
                                                sold_levels[coin] = []
                                            sold_levels[coin].append(i)
                                            spot_settings["sold_levels"] = sold_levels
                                            db.set_user_field(uid, "spot_settings", json.dumps(spot_settings))
                                            
                                            usdt_received = sell_qty * current_price
                                            
                                            # Notify user
                                            msg = (
                                                f"🎯 <b>Take Profit Executed!</b>\n\n"
                                                f"📈 {coin} reached +{gain_pct:.1f}% gain\n"
                                                f"💰 Sold {sell_qty:.6f} {coin}\n"
                                                f"💵 Received ~${usdt_received:.2f} USDT\n"
                                                f"📊 TP Level {i+1}/{len(tp_levels)}"
                                            )
                                            
                                            await safe_send_notification(bot, uid, msg, parse_mode="HTML")
                                            logger.info(f"TP executed for {uid}: {coin} +{gain_pct:.1f}%, sold {sell_qty}")
                                            
                                        except Exception as e:
                                            logger.error(f"TP sell error for {uid}/{coin}: {e}")
                                        
                                        break  # Only one level per check
                                
                            except Exception as e:
                                logger.error(f"TP check error for {uid}/{coin}: {e}")
                    
                    # === Auto Rebalance ===
                    if spot_settings.get("rebalance_enabled"):
                        portfolio = spot_settings.get("portfolio", "custom")
                        
                        if portfolio != "custom" and portfolio in SPOT_PORTFOLIOS:
                            target_allocation = SPOT_PORTFOLIOS[portfolio].get("coins", {})
                            
                            if target_allocation:
                                balances = await fetch_spot_balance(uid, account_type=account_type)
                                
                                # Calculate current portfolio value
                                total_value = 0.0
                                coin_values = {}
                                
                                for coin, qty in balances.items():
                                    if coin == "USDT":
                                        total_value += qty
                                        coin_values[coin] = qty
                                    elif qty > 0.00001:
                                        symbol = f"{coin}USDT"
                                        try:
                                            ticker = await get_spot_ticker(uid, symbol, account_type)
                                            if ticker:
                                                price = float(ticker.get("lastPrice", 0))
                                                value = qty * price
                                                total_value += value
                                                coin_values[coin] = value
                                        except Exception:
                                            pass
                                
                                if total_value < 10:  # Skip if portfolio too small
                                    continue
                                
                                # Calculate deviation from target
                                rebalance_threshold = spot_settings.get("rebalance_threshold", 5.0)  # 5% default
                                needs_rebalance = False
                                
                                for coin, target_pct in target_allocation.items():
                                    current_value = coin_values.get(coin, 0)
                                    current_pct = (current_value / total_value) * 100 if total_value > 0 else 0
                                    deviation = abs(current_pct - target_pct)
                                    
                                    if deviation > rebalance_threshold:
                                        needs_rebalance = True
                                        break
                                
                                if needs_rebalance:
                                    rebalance_msg_lines = [
                                        "⚖️ <b>Portfolio Rebalance Suggestion</b>",
                                        "",
                                    ]
                                    
                                    for coin, target_pct in target_allocation.items():
                                        current_value = coin_values.get(coin, 0)
                                        current_pct = (current_value / total_value) * 100 if total_value > 0 else 0
                                        diff = target_pct - current_pct
                                        
                                        if abs(diff) > 1:
                                            arrow = "⬆️" if diff > 0 else "⬇️"
                                            rebalance_msg_lines.append(
                                                f"{arrow} {coin}: {current_pct:.1f}% → {target_pct}% ({diff:+.1f}%)"
                                            )
                                    
                                    rebalance_msg_lines.append("")
                                    rebalance_msg_lines.append("<i>Use Buy Now to rebalance manually.</i>")
                                    
                                    try:
                                        await safe_send_notification(
                                            bot, uid,
                                            "\n".join(rebalance_msg_lines),
                                            parse_mode="HTML"
                                        )
                                    except Exception as e:
                                        logger.warning(f"Failed to notify rebalance for {uid}: {e}")
                    
                    # === Trailing TP Monitoring ===
                    trailing_config = spot_settings.get("trailing_tp", {})
                    if trailing_config.get("enabled"):
                        try:
                            sells = await check_spot_trailing_tp(uid, account_type=account_type)
                            
                            for sell in sells:
                                coin = sell.get("coin", "")
                                qty_sold = sell.get("qty_sold", 0)
                                usdt_received = sell.get("usdt_received", 0)
                                gain_pct = sell.get("gain_pct", 0)
                                peak_price = sell.get("peak_price", 0)
                                sell_price = sell.get("sell_price", 0)
                                
                                msg = (
                                    f"📈 <b>Trailing TP Triggered!</b>\n\n"
                                    f"🪙 {coin}\n"
                                    f"📊 Final gain: +{gain_pct:.1f}%\n"
                                    f"🏔️ Peak: ${peak_price:.4f}\n"
                                    f"💰 Sold at: ${sell_price:.4f}\n"
                                    f"📦 Quantity: {qty_sold:.6f}\n"
                                    f"💵 Received: ${usdt_received:.2f}"
                                )
                                
                                try:
                                    await safe_send_notification(bot, uid, msg, parse_mode="HTML")
                                except Exception as e:
                                    logger.warning(f"Failed to notify trailing TP for {uid}: {e}")
                                    
                        except Exception as e:
                            logger.error(f"Trailing TP check error for {uid}: {e}")
                    
                    # === Grid Bot Monitoring ===
                    grids = spot_settings.get("grids", {})
                    active_grids = [c for c, g in grids.items() if g.get("active")]
                    
                    if active_grids:
                        try:
                            events = await check_spot_grids(uid, account_type=account_type)
                            
                            for event in events:
                                event_type = event.get("type", "")
                                coin = event.get("coin", "")
                                
                                if event_type == "grid_buy_filled":
                                    buy_price = event.get("buy_price", 0)
                                    sell_placed = event.get("sell_placed", 0)
                                    qty = event.get("qty", 0)
                                    
                                    msg = (
                                        f"🔲 <b>Grid Buy Filled</b>\n\n"
                                        f"🪙 {coin}\n"
                                        f"💰 Bought at: ${buy_price:.4f}\n"
                                        f"📦 Quantity: {qty:.6f}\n"
                                        f"📈 Sell placed at: ${sell_placed:.4f}"
                                    )
                                    
                                elif event_type == "grid_sell_filled":
                                    sell_price = event.get("sell_price", 0)
                                    profit = event.get("profit", 0)
                                    total_profit = event.get("total_profit", 0)
                                    
                                    msg = (
                                        f"🔲 <b>Grid Sell Filled</b>\n\n"
                                        f"🪙 {coin}\n"
                                        f"💰 Sold at: ${sell_price:.4f}\n"
                                        f"✅ Profit: +${profit:.2f}\n"
                                        f"📊 Total Grid Profit: +${total_profit:.2f}"
                                    )
                                else:
                                    continue
                                
                                try:
                                    await safe_send_notification(bot, uid, msg, parse_mode="HTML")
                                except Exception as e:
                                    logger.warning(f"Failed to notify grid event for {uid}: {e}")
                                    
                        except Exception as e:
                            logger.error(f"Grid check error for {uid}: {e}")
                    
                except Exception as e:
                    logger.error(f"TP/Rebalance error for user {uid}: {e}")
            
        except Exception as e:
            logger.exception(f"Critical error in spot_tp_rebalance_loop: {e}")
            await asyncio.sleep(60)


async def spot_auto_dca_loop(app: Application):
    """
    Background loop that executes automatic spot DCA for users who have:
    - auto_dca enabled
    - frequency set to daily/weekly/monthly
    - valid API credentials
    
    Runs every hour and checks if it's time for each user's DCA.
    """
    bot = app.bot
    logger.info("Starting spot_auto_dca_loop")
    
    while True:
        try:
            await asyncio.sleep(3600)  # Check every hour
            
            if GLOBAL_PAUSED:
                continue
            
            now = int(time.time())
            
            for uid in get_all_users():
                try:
                    cfg = get_user_config(uid)
                    spot_settings = cfg.get("spot_settings", {})
                    
                    # Skip if auto_dca is not enabled
                    if not spot_settings.get("auto_dca"):
                        continue
                    
                    frequency = spot_settings.get("frequency", "manual")
                    if frequency == "manual":
                        continue
                    
                    # Check if user has API credentials
                    k, s = get_user_credentials(uid)
                    if not k or not s:
                        continue
                    
                    # Check interval
                    interval = SPOT_DCA_INTERVALS.get(frequency)
                    if not interval:
                        continue
                    
                    # Get last execution time
                    last_exec = spot_settings.get("last_dca_ts", 0) or _spot_dca_last_exec.get(uid, 0)
                    
                    # Check if enough time has passed
                    if now - last_exec < interval:
                        continue
                    
                    # Time to execute DCA!
                    logger.info(f"Executing auto spot DCA for user {uid} (freq={frequency})")
                    
                    lang = cfg.get("lang", DEFAULT_LANG)
                    t = LANGS.get(lang, LANGS[DEFAULT_LANG])
                    
                    coins = spot_settings.get("coins", SPOT_DCA_COINS)
                    base_amount = spot_settings.get("dca_amount", SPOT_DCA_DEFAULT_AMOUNT)
                    strategy = spot_settings.get("strategy", "fixed")
                    portfolio = spot_settings.get("portfolio", "custom")
                    allocation = spot_settings.get("allocation", {})
                    account_type = spot_settings.get("trading_mode", "demo")
                    
                    # Get portfolio allocation if using preset
                    if portfolio != "custom" and portfolio in SPOT_PORTFOLIOS:
                        portfolio_info = SPOT_PORTFOLIOS[portfolio]
                        allocation = portfolio_info.get("coins", {})
                    
                    results = []
                    total_spent = 0.0
                    skipped = []
                    
                    for coin in coins:
                        try:
                            # Calculate amount based on allocation
                            if allocation and coin in allocation:
                                coin_pct = allocation[coin] / 100.0
                                coin_base_amount = base_amount * coin_pct
                            else:
                                coin_base_amount = base_amount / len(coins) if coins else base_amount
                            
                            # Apply smart DCA strategy multiplier
                            adjusted_amount = await calculate_smart_dca_amount(
                                base_amount=coin_base_amount,
                                strategy=strategy,
                                coin=coin,
                                spot_settings=spot_settings,
                                user_id=uid,
                                account_type=account_type,
                            )
                            
                            if adjusted_amount <= 0:
                                skipped.append(coin)
                                continue
                            
                            result = await execute_spot_dca_buy(uid, coin, adjusted_amount, account_type=account_type)
                            if result.get("success"):
                                spent = result.get("usdt_spent", adjusted_amount)
                                results.append(f"✅ {result.get('qty', 0):.6f} {coin} (${spent:.2f})")
                                total_spent += spent
                            elif result.get("error") == "SKIP":
                                # Silently skip - don't notify user
                                skipped.append(coin)
                            else:
                                # Only show real errors
                                results.append(f"❌ {coin}: {result.get('error', 'Error')}")
                        except Exception as e:
                            logger.error(f"Auto DCA buy error for {coin}: {e}")
                            results.append(f"❌ {coin}: {str(e)[:50]}")
                    
                    # Update last execution timestamp
                    spot_settings["last_dca_ts"] = now
                    spot_settings["total_invested"] = spot_settings.get("total_invested", 0.0) + total_spent
                    _spot_dca_last_exec[uid] = now
                    
                    db.set_user_field(uid, "spot_settings", json.dumps(spot_settings))
                    
                    # Notify user
                    if results:
                        strategy_info = SMART_DCA_STRATEGIES.get(strategy, {})
                        strategy_label = f"{strategy_info.get('emoji', '📊')} {strategy_info.get('name', 'Fixed')}"
                        
                        freq_labels = {
                            "daily": t.get("spot_freq_daily", "Daily"),
                            "weekly": t.get("spot_freq_weekly", "Weekly"),
                            "monthly": t.get("spot_freq_monthly", "Monthly"),
                        }
                        
                        msg_lines = [
                            f"🔄 <b>Auto DCA Executed</b>",
                            f"",
                            f"📅 Frequency: {freq_labels.get(frequency, frequency)}",
                            f"🎯 Strategy: {strategy_label}",
                            f"💰 Total spent: ${total_spent:.2f}",
                            f"",
                        ]
                        msg_lines.extend(results)
                        
                        if skipped:
                            msg_lines.append(f"")
                            msg_lines.append(f"⏭️ Skipped: {', '.join(skipped)}")
                        
                        try:
                            await safe_send_notification(bot, uid, "\n".join(msg_lines), parse_mode="HTML")
                        except Exception as e:
                            logger.warning(f"Failed to notify user {uid} about auto DCA: {e}")
                    
                except Exception as e:
                    logger.error(f"Auto DCA error for user {uid}: {e}")
            
        except Exception as e:
            logger.exception(f"Critical error in spot_auto_dca_loop: {e}")
            await asyncio.sleep(60)  # Wait a minute before retrying


@log_calls
async def start_monitoring(app: Application):
    try:
        db.init_db()
    except Exception:
        pass
    
    # Setup Menu Button (Dashboard) with WebApp
    try:
        # Get webapp URL from env, fallback to ngrok file, then default
        webapp_url = WEBAPP_URL
        if webapp_url == "http://localhost:8765":
            ngrok_file = Path(__file__).parent / "run" / "ngrok_url.txt"
            if ngrok_file.exists():
                webapp_url = ngrok_file.read_text().strip()
        
        # Check if menu button URL needs update
        last_url_file = Path(__file__).parent / "run" / "last_menu_url.txt"
        last_url = ""
        if last_url_file.exists():
            last_url = last_url_file.read_text().strip()
        
        # Add timestamp to prevent Telegram from caching old URL
        import time
        cache_bust = int(time.time())
        current_url = f"{webapp_url}/dashboard?_t={cache_bust}"
        base_url = f"{webapp_url}/dashboard"
        
        # Only update menu button if base URL changed
        if last_url != base_url:
            logger.info(f"Menu button URL changed: {last_url} -> {base_url}")
            
            # Reset to default first to clear Telegram's cache
            await app.bot.set_chat_menu_button(menu_button=MenuButtonDefault())
            logger.info("Menu button reset to default (clearing cache)")
            await asyncio.sleep(1)
            
            # Set the menu button for all users with cache-busting timestamp
            menu_button = MenuButtonWebApp(
                text="🖥️ Dashboard",
                web_app=WebAppInfo(url=current_url)
            )
            await app.bot.set_chat_menu_button(menu_button=menu_button)
            logger.info(f"Menu button set to Dashboard: {current_url}")
            
            # Save base URL (without timestamp) for comparison
            last_url_file.write_text(base_url)
        else:
            logger.info(f"Menu button URL unchanged: {base_url}")
    except Exception as e:
        logger.warning(f"Failed to set menu button: {e}")
    
    # Start futures positions monitoring loop
    logger.info("Starting monitor_positions_loop task")
    task = asyncio.create_task(monitor_positions_loop(app), name="monitor_positions_loop")
    app.bot_data["monitor_task"] = task

    def _on_done(t: asyncio.Task):
        try:
            exc = t.exception() 
        except asyncio.CancelledError:
            logger.info("monitor_positions_loop cancelled")
            return
        if exc:
            logger.error("monitor_positions_loop crashed", exc_info=(type(exc), exc, exc.__traceback__))
        else:
            logger.info("monitor_positions_loop finished normally")

    task.add_done_callback(_on_done)
    
    # Start spot auto-DCA loop
    logger.info("Starting spot_auto_dca_loop task")
    spot_task = asyncio.create_task(spot_auto_dca_loop(app), name="spot_auto_dca_loop")
    app.bot_data["spot_dca_task"] = spot_task

    def _on_spot_done(t: asyncio.Task):
        try:
            exc = t.exception() 
        except asyncio.CancelledError:
            logger.info("spot_auto_dca_loop cancelled")
            return
        if exc:
            logger.error("spot_auto_dca_loop crashed", exc_info=(type(exc), exc, exc.__traceback__))
        else:
            logger.info("spot_auto_dca_loop finished normally")

    spot_task.add_done_callback(_on_spot_done)
    
    # Start spot TP/Rebalance monitoring loop
    logger.info("Starting spot_tp_rebalance_loop task")
    tp_task = asyncio.create_task(spot_tp_rebalance_loop(app), name="spot_tp_rebalance_loop")
    app.bot_data["spot_tp_task"] = tp_task

    def _on_tp_done(t: asyncio.Task):
        try:
            exc = t.exception() 
        except asyncio.CancelledError:
            logger.info("spot_tp_rebalance_loop cancelled")
            return
        if exc:
            logger.error("spot_tp_rebalance_loop crashed", exc_info=(type(exc), exc, exc.__traceback__))
        else:
            logger.info("spot_tp_rebalance_loop finished normally")

    tp_task.add_done_callback(_on_tp_done)
    
    # Start notification service loop for market alerts
    if notification_service:
        logger.info("Starting notification_service_loop task")
        notif_task = asyncio.create_task(notification_service.start_notification_loop(), name="notification_loop")
        app.bot_data["notification_task"] = notif_task

        def _on_notif_done(t: asyncio.Task):
            try:
                exc = t.exception() 
            except asyncio.CancelledError:
                logger.info("notification_loop cancelled")
                return
            if exc:
                logger.error("notification_loop crashed", exc_info=(type(exc), exc, exc.__traceback__))
            else:
                logger.info("notification_loop finished normally")

        notif_task.add_done_callback(_on_notif_done)

@with_texts
@log_calls
async def on_users_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid_admin = update.effective_user.id

    def T(key: str, **kw):
        s = ctx.t.get(key, key)
        return s.format(**kw) if kw else s

    if uid_admin != ADMIN_ID:
        await q.answer(T("not_allowed"), show_alert=True)
        return

    await q.answer()
    data = q.data or ""
    if data.startswith("users:page:"):
        try:
            page = int(data.split(":", 2)[2])
        except Exception:
            await q.answer(T("bad_page"), show_alert=True)
            return
        await show_users_page(ctx, ctx.bot, q.message.chat_id, page=page)
        return

    try:
        _, action, payload = data.split(":", 2)
        target_uid = int(payload)
    except Exception:
        await q.answer(T("bad_payload"), show_alert=True)
        return

    if action == "approve":
        set_user_field(target_uid, "is_allowed", 1)
        set_user_field(target_uid, "is_banned", 0)
        new_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(T("btn_blacklist"), callback_data=f"users:ban:{target_uid}")],
            [InlineKeyboardButton(T("btn_delete_user"), callback_data=f"users:del:{target_uid}")]
        ])
        try:
            await q.edit_message_reply_markup(reply_markup=new_kb)
        except Exception:
            pass
        await q.message.reply_text(T("moderation_approved", target=target_uid))
        try:
            await ctx.bot.send_message(target_uid, T("user_access_approved"))
        except Exception:
            pass

    elif action == "ban":
        set_user_field(target_uid, "is_banned", 1)
        set_user_field(target_uid, "is_allowed", 0)
        new_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(T("btn_delete_user"), callback_data=f"users:del:{target_uid}")]
        ])
        try:
            await q.edit_message_reply_markup(reply_markup=new_kb)
        except Exception:
            pass
        await q.message.reply_text(T("moderation_banned", target=target_uid))
        try:
            await ctx.bot.send_message(target_uid, T("banned"))
        except Exception:
            pass

    elif action == "del":
        try:
            db.delete_user(target_uid)
        except Exception as e:
            await q.message.reply_text(T("admin_user_delete_fail", target=target_uid, error=e))
            return
        try:
            await q.edit_message_text(T("admin_user_deleted", target=target_uid))
        except Exception:
            await q.message.reply_text(T("admin_user_deleted", target=target_uid))

    else:
        await q.answer(T("unknown_action"), show_alert=True)

@require_access
@with_texts
@log_calls
async def cancel_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        ctx.t['order_cancelled'],
        reply_markup=main_menu_keyboard(ctx, update=update)
    )
    return ConversationHandler.END

@require_access
@with_texts
@log_calls
async def cmd_update_tpsl(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    positions = await fetch_open_positions(uid)
    if not positions:
        await update.message.reply_text(ctx.t['update_tpsl_no_positions'], reply_markup=main_menu_keyboard(ctx, update=update))
        return
    await update.message.reply_text(ctx.t['update_tpsl_prompt'], parse_mode='Markdown')
    ctx.user_data['mode'] = 'update_tpsl'

@require_access
@with_texts
@log_calls
async def on_coin_group_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    try:
        await q.answer()
    except Exception:
        pass

    data = (q.data or "").strip()
    try:
        prefix, raw = data.split(":", 1)
        if prefix != "coins":
            await q.answer("Bad payload", show_alert=True)
            return
    except Exception:
        await q.answer("Bad payload", show_alert=True)
        return

    group = raw.strip().upper()
    valid = {"ALL", "TOP100", "VOLATILE"}
    if group not in valid:
        await q.answer("Unknown group", show_alert=True)
        return

    set_user_field(q.from_user.id, "coins", group)
    ctx.user_data["coins"] = group

    labels = {
        "ALL":      ctx.t.get('group_all', 'ALL'),
        "TOP100":   ctx.t.get('group_top100', 'TOP100'),
        "VOLATILE": ctx.t.get('group_volatile', 'VOLATILE'),
    }
    label = labels[group]

    try:
        await q.edit_message_text(ctx.t['group_set'].format(group=label))
    except Exception:
        await ctx.bot.send_message(q.from_user.id, ctx.t['group_set'].format(group=label))

    # показываем меню
    await ctx.bot.send_message(
        chat_id=q.from_user.id,
        text=ctx.t['welcome'],
        reply_markup=main_menu_keyboard(ctx, update=update)
    )


def _fmt_bool_mark(t: dict, v: int | bool | None) -> str:
    return t.get('mark_yes', '✅') if v else t.get('mark_no', '❌')

def _fmt_username(u, dash: str = "—") -> str:
    try:
        return f"@{u.username}" if u and getattr(u, "username", None) else dash
    except Exception:
        return dash

async def _fetch_user_public(bot, uid: int):
    try:
        return await bot.get_chat(uid)
    except Exception:
        return None


async def show_users_page(ctx: ContextTypes.DEFAULT_TYPE, bot, chat_id: int, page: int = 0):
    # Get translations manually since this is not a direct handler
    if hasattr(ctx, 't') and ctx.t:
        t = ctx.t
    else:
        lang = DEFAULT_LANG
        if hasattr(ctx, 'user_data') and ctx.user_data:
            lang = ctx.user_data.get('lang', DEFAULT_LANG)
        t = LANGS.get(lang, LANGS[DEFAULT_LANG])
    
    all_ids = sorted(set(get_all_users() or []))
    total = len(all_ids)
    if total == 0:
        await bot.send_message(chat_id, t['users_not_found'])
        return

    start = page * PAGE_SIZE
    end   = min(start + PAGE_SIZE, total)
    slice_ids = all_ids[start:end]
    pages_total = (total - 1) // PAGE_SIZE + 1

    await bot.send_message(chat_id, t['users_page_info'].format(page=page+1, pages=pages_total, total=total))

    for uid in slice_ids:
        cfg = get_user_config(uid) or {}
        allowed = _fmt_bool_mark(t, cfg.get("is_allowed", 0))
        banned  = _fmt_bool_mark(t, cfg.get("is_banned", 0))
        terms   = _fmt_bool_mark(t, cfg.get("terms_accepted", 0))
        lang    = cfg.get("lang", DEFAULT_LANG)
        percent = cfg.get("percent", 0)

        u = await _fetch_user_public(bot, uid)
        full_name = (f"{getattr(u,'first_name', '') or ''} {getattr(u,'last_name','') or ''}").strip() or t['dash']
        uname = _fmt_username(u, dash=t['dash'])

        text = t['user_card_html'].format(
            uid=uid,
            full_name=html.escape(full_name),
            uname=uname,
            lang=lang,
            allowed=allowed,
            banned=banned,
            terms=terms,
            percent=percent
        )

        if cfg.get("is_banned", 0):
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(t['btn_delete_user'], callback_data=f"users:del:{uid}")]])
        else:
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(t['btn_blacklist'], callback_data=f"users:ban:{uid}")]])

        await bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(t['btn_prev'], callback_data=f"users:page:{page-1}"))
    if end < total:
        nav_row.append(InlineKeyboardButton(t['btn_next'], callback_data=f"users:page:{page+1}"))
    if nav_row:
        await bot.send_message(chat_id, t['nav_caption'], reply_markup=InlineKeyboardMarkup([nav_row]))

@with_texts
@log_calls
async def cmd_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    t = ctx.t
    keyboard = [
        [InlineKeyboardButton(t.get('admin_users_management', '👥 Users'), callback_data="admin:users_menu"),
         InlineKeyboardButton(t.get('admin_licenses', '🔑 Licenses'), callback_data="adm_lic:menu")],
        [InlineKeyboardButton(t.get('admin_payments', '💳 Payments'), callback_data="admin:payments_menu"),
         InlineKeyboardButton(t.get('admin_reports', '📊 Reports'), callback_data="admin:reports_menu")],
        [InlineKeyboardButton(t['admin_pause_all'],  callback_data="admin:pause"),
         InlineKeyboardButton(t['admin_resume_all'], callback_data="admin:resume")],
        [InlineKeyboardButton(t['admin_close_longs'],  callback_data="admin:close_longs"),
         InlineKeyboardButton(t['admin_close_shorts'], callback_data="admin:close_shorts")],
        [InlineKeyboardButton(t['admin_cancel_limits'], callback_data="admin:cancel_limits")],
        [InlineKeyboardButton(t.get('admin_search_user', '🔍 Find User'), callback_data="admin:search_user")],
    ]
    await update.message.reply_text(t['admin_panel'], reply_markup=InlineKeyboardMarkup(keyboard))

@with_texts
@log_calls
async def on_admin_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    t   = ctx.t
    q   = update.callback_query
    uid = update.effective_user.id
    await q.answer()
    if uid != ADMIN_ID:
        return
    try:
        _, cmd = q.data.split(":", 1)
    except Exception:
        return

    if cmd == "menu":
        # Back to main admin menu
        keyboard = [
            [InlineKeyboardButton(t.get('admin_users_management', '👥 Users'), callback_data="admin:users_menu"),
             InlineKeyboardButton(t.get('admin_licenses', '🔑 Licenses'), callback_data="adm_lic:menu")],
            [InlineKeyboardButton(t.get('admin_payments', '💳 Payments'), callback_data="admin:payments_menu"),
             InlineKeyboardButton(t.get('admin_reports', '📊 Reports'), callback_data="admin:reports_menu")],
            [InlineKeyboardButton(t['admin_pause_all'],  callback_data="admin:pause"),
             InlineKeyboardButton(t['admin_resume_all'], callback_data="admin:resume")],
            [InlineKeyboardButton(t['admin_close_longs'],  callback_data="admin:close_longs"),
             InlineKeyboardButton(t['admin_close_shorts'], callback_data="admin:close_shorts")],
            [InlineKeyboardButton(t['admin_cancel_limits'], callback_data="admin:cancel_limits")],
            [InlineKeyboardButton(t.get('admin_search_user', '🔍 Find User'), callback_data="admin:search_user")],
        ]
        await q.edit_message_text(t['admin_panel'], reply_markup=InlineKeyboardMarkup(keyboard))

    elif cmd == "pause":
        global GLOBAL_PAUSED
        GLOBAL_PAUSED = True
        await q.edit_message_text(t['admin_pause_notice'])

    elif cmd == "resume":
        GLOBAL_PAUSED = False
        await q.edit_message_text(t['admin_resume_notice'])

    elif cmd == "users":
        await show_users_page(ctx, ctx.bot, q.message.chat_id, page=0)

    elif cmd == "users_menu":
        # Users management menu with filters
        keyboard = [
            [InlineKeyboardButton(t.get('admin_all_users', '👥 All Users'), callback_data="admin:users_list:all:0")],
            [InlineKeyboardButton(t.get('admin_active_users', '✅ Active'), callback_data="admin:users_list:active:0"),
             InlineKeyboardButton(t.get('admin_banned_users', '🚫 Banned'), callback_data="admin:users_list:banned:0")],
            [InlineKeyboardButton("💎 Premium", callback_data="admin:users_list:premium:0"),
             InlineKeyboardButton("🥈 Basic", callback_data="admin:users_list:basic:0"),
             InlineKeyboardButton("🎁 Trial", callback_data="admin:users_list:trial:0")],
            [InlineKeyboardButton(t.get('admin_no_license', '❌ No License'), callback_data="admin:users_list:no_license:0")],
            [InlineKeyboardButton(t.get('admin_search_user', '🔍 Find User'), callback_data="admin:search_user")],
            [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:menu")],
        ]
        await q.edit_message_text(
            t.get('admin_users_menu', '👥 *User Management*\n\nSelect filter or search:'),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif cmd.startswith("users_list:"):
        # Show paginated users list
        parts = cmd.split(":")
        filter_type = parts[1] if len(parts) > 1 else "all"
        page = int(parts[2]) if len(parts) > 2 else 0
        
        users, total = get_users_paginated(page=page, per_page=8, filter_type=filter_type)
        total_pages = (total + 7) // 8
        
        if not users:
            await q.edit_message_text(
                t.get('admin_no_users_found', 'No users found.'),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:users_menu")]
                ])
            )
            return
        
        # Build user list
        lines = [f"👥 *Users ({filter_type})* — Page {page + 1}/{total_pages}\n"]
        keyboard = []
        
        for u in users:
            status = "🚫" if u["is_banned"] else "✅" if u["is_allowed"] else "⏳"
            license_icon = {"premium": "💎", "basic": "🥈", "trial": "🎁"}.get(u["license_type"], "❌")
            days = f"({u['license_days_left']}d)" if u["license_days_left"] else ""
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{status} {u['user_id']} {license_icon}{days}",
                    callback_data=f"admin:user:{u['user_id']}"
                )
            ])
        
        # Pagination
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️", callback_data=f"admin:users_list:{filter_type}:{page-1}"))
        nav_row.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="noop"))
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton("➡️", callback_data=f"admin:users_list:{filter_type}:{page+1}"))
        
        if nav_row:
            keyboard.append(nav_row)
        
        keyboard.append([InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:users_menu")])
        
        await q.edit_message_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif cmd.startswith("user:"):
        # Show user card
        target_uid = int(cmd.split(":")[1])
        await show_user_card(q, ctx, target_uid)

    elif cmd == "search_user":
        # Ask for user ID
        ctx.user_data["mode"] = "admin_search_user"
        await q.edit_message_text(
            t.get('admin_enter_user_id', '🔍 Enter user ID to search:'),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get('btn_cancel', '❌ Cancel'), callback_data="admin:users_menu")]
            ])
        )

    elif cmd.startswith("ban:"):
        target_uid = int(cmd.split(":")[1])
        ban_user(target_uid)
        await q.answer(t.get('admin_user_banned', 'User banned!'), show_alert=True)
        await show_user_card(q, ctx, target_uid)

    elif cmd.startswith("unban:"):
        target_uid = int(cmd.split(":")[1])
        allow_user(target_uid)
        await q.answer(t.get('admin_user_unbanned', 'User unbanned!'), show_alert=True)
        await show_user_card(q, ctx, target_uid)

    elif cmd.startswith("approve:"):
        target_uid = int(cmd.split(":")[1])
        set_user_field(target_uid, "is_allowed", 1)
        await q.answer(t.get('admin_user_approved', 'User approved!'), show_alert=True)
        await show_user_card(q, ctx, target_uid)

    elif cmd.startswith("delete:"):
        target_uid = int(cmd.split(":")[1])
        # Confirm deletion
        await q.edit_message_text(
            t.get('admin_confirm_delete', '⚠️ *Confirm deletion*\n\nUser {uid} will be permanently deleted!').format(uid=target_uid),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get('admin_confirm_yes', '✅ Yes, Delete'), callback_data=f"admin:confirm_delete:{target_uid}")],
                [InlineKeyboardButton(t.get('admin_confirm_no', '❌ Cancel'), callback_data=f"admin:user:{target_uid}")],
            ])
        )

    elif cmd.startswith("confirm_delete:"):
        target_uid = int(cmd.split(":")[1])
        delete_user(target_uid)
        await q.edit_message_text(
            t.get('admin_user_deleted', '✅ User {uid} deleted.').format(uid=target_uid),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:users_menu")]
            ])
        )

    elif cmd.startswith("grant_lic:"):
        # Grant license to user: admin:grant_lic:uid:type:months
        parts = cmd.split(":")
        target_uid = int(parts[1])
        license_type = parts[2] if len(parts) > 2 else None
        months = int(parts[3]) if len(parts) > 3 else None
        
        if not license_type:
            # Select license type
            await q.edit_message_text(
                t.get('admin_select_license_type', 'Select license type for user {uid}:').format(uid=target_uid),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💎 Premium", callback_data=f"admin:grant_lic:{target_uid}:premium")],
                    [InlineKeyboardButton("🥈 Basic", callback_data=f"admin:grant_lic:{target_uid}:basic")],
                    [InlineKeyboardButton("🎁 Trial (7d)", callback_data=f"admin:grant_lic:{target_uid}:trial:1")],
                    [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data=f"admin:user:{target_uid}")],
                ])
            )
        elif not months and license_type != "trial":
            # Select period
            if license_type == "premium":
                keyboard = [
                    [InlineKeyboardButton("1 Month", callback_data=f"admin:grant_lic:{target_uid}:premium:1")],
                    [InlineKeyboardButton("3 Months", callback_data=f"admin:grant_lic:{target_uid}:premium:3")],
                    [InlineKeyboardButton("6 Months", callback_data=f"admin:grant_lic:{target_uid}:premium:6")],
                    [InlineKeyboardButton("12 Months", callback_data=f"admin:grant_lic:{target_uid}:premium:12")],
                ]
            else:
                keyboard = [
                    [InlineKeyboardButton("1 Month", callback_data=f"admin:grant_lic:{target_uid}:basic:1")],
                ]
            keyboard.append([InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data=f"admin:grant_lic:{target_uid}")])
            await q.edit_message_text(
                t.get('admin_select_period', 'Select period:'),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            # Grant license
            result = set_user_license(
                user_id=target_uid,
                license_type=license_type,
                period_months=months or 1,
                admin_id=uid,
                payment_type="admin_grant",
            )
            if result.get("success"):
                await q.answer(t.get('admin_license_granted_short', 'License granted!'), show_alert=True)
            else:
                await q.answer(f"Error: {result.get('error')}", show_alert=True)
            await show_user_card(q, ctx, target_uid)

    elif cmd.startswith("extend_lic:"):
        # Extend license: admin:extend_lic:uid or admin:extend_lic:uid:days
        parts = cmd.split(":")
        target_uid = int(parts[1])
        days = int(parts[2]) if len(parts) > 2 else None
        
        if not days:
            # Select days to extend
            await q.edit_message_text(
                t.get('admin_select_extend_days', 'Select days to extend for user {uid}:').format(uid=target_uid),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("7 days", callback_data=f"admin:extend_lic:{target_uid}:7"),
                     InlineKeyboardButton("14 days", callback_data=f"admin:extend_lic:{target_uid}:14")],
                    [InlineKeyboardButton("30 days", callback_data=f"admin:extend_lic:{target_uid}:30"),
                     InlineKeyboardButton("90 days", callback_data=f"admin:extend_lic:{target_uid}:90")],
                    [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data=f"admin:user:{target_uid}")],
                ])
            )
        else:
            result = extend_license(target_uid, days, admin_id=uid)
            if result.get("success"):
                await q.answer(t.get('admin_license_extended_short', 'Extended by {days} days!').format(days=days), show_alert=True)
            else:
                await q.answer(f"Error: {result.get('error')}", show_alert=True)
            await show_user_card(q, ctx, target_uid)

    elif cmd.startswith("revoke_lic:"):
        target_uid = int(cmd.split(":")[1])
        result = revoke_license(target_uid, admin_id=uid)
        if result.get("success"):
            await q.answer(t.get('admin_license_revoked_short', 'License revoked!'), show_alert=True)
        else:
            await q.answer(f"Error: {result.get('error')}", show_alert=True)
        await show_user_card(q, ctx, target_uid)

    elif cmd.startswith("msg_user:"):
        # Send message to user
        target_uid = int(cmd.split(":")[1])
        ctx.user_data["admin_msg_target"] = target_uid
        ctx.user_data["mode"] = "admin_send_message"
        await q.edit_message_text(
            t.get('admin_enter_message', '✉️ Enter message to send to user {uid}:').format(uid=target_uid),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get('btn_cancel', '❌ Cancel'), callback_data=f"admin:user:{target_uid}")]
            ])
        )

    elif cmd in ("close_longs", "close_shorts"):
        side_to_close = "Buy" if cmd == "close_longs" else "Sell"
        type_label = t['type_longs'] if cmd == "close_longs" else t['type_shorts']
        count = 0
        for user in get_all_users():
            if GLOBAL_PAUSED:
                break
            positions = await fetch_open_positions(user)
            targets = [p for p in positions if p.get("side") == side_to_close]
            for p in targets:
                sym = p.get("symbol")
                qty = float(p.get("size", 0) or 0)
                if not sym or qty <= 0:
                    continue
                try:
                    await place_order(
                        user_id=user,
                        symbol=sym,
                        side=("Sell" if side_to_close == "Buy" else "Buy"),
                        orderType="Market",
                        qty=qty
                    )
                    count += 1
                except Exception:
                    pass
        await q.edit_message_text(t['admin_closed_total'].format(count=count, type=type_label))

    elif cmd == "cancel_limits":
        canceled = 0
        for user in get_all_users():
            if GLOBAL_PAUSED:
                break
            orders = await fetch_open_orders(user)
            for o in orders:
                if o.get("orderType") == "Limit":
                    try:
                        await _bybit_request(
                            user, "POST", "/v5/order/cancel",
                            body={"category": "linear", "orderId": o["orderId"], "symbol": o["symbol"]}
                        )
                        remove_pending_limit_order(user, o["orderId"])
                        canceled += 1
                    except Exception:
                        pass
        await q.edit_message_text(t['admin_canceled_limits_total'].format(count=canceled))

    # =====================================================
    # PAYMENTS MENU
    # =====================================================
    elif cmd == "payments_menu":
        stats = get_payment_stats()
        text = t.get('admin_payments_menu', '💳 *Payments Management*') + "\n\n"
        text += f"📊 *Stats:*\n"
        text += f"• Total payments: {stats['total_payments']}\n"
        text += f"• Completed: {stats['completed']}\n"
        text += f"• Pending: {stats['pending']}\n"
        text += f"• Failed: {stats['failed']}\n"
        text += f"• Total Stars: {stats['total_stars']}⭐\n"
        text += f"• Total TON: {stats['total_ton']:.2f} 💎\n"
        text += f"• Unique payers: {stats['unique_payers']}\n"
        
        keyboard = [
            [InlineKeyboardButton(t.get('admin_all_payments', '📜 All Payments'), callback_data="admin:payments_list:all:0")],
            [InlineKeyboardButton("✅ Completed", callback_data="admin:payments_list:completed:0"),
             InlineKeyboardButton("⏳ Pending", callback_data="admin:payments_list:pending:0")],
            [InlineKeyboardButton("❌ Failed", callback_data="admin:payments_list:failed:0")],
            [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:menu")],
        ]
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif cmd.startswith("payments_list:"):
        parts = cmd.split(":")
        status = parts[1] if len(parts) > 1 and parts[1] != "all" else None
        page = int(parts[2]) if len(parts) > 2 else 0
        
        payments, total = get_all_payments(status=status, limit=10, offset=page * 10)
        total_pages = (total + 9) // 10
        
        if not payments:
            await q.edit_message_text(
                t.get('admin_no_payments_found', 'No payments found.'),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:payments_menu")]
                ])
            )
            return
        
        lines = [f"💳 *Payments ({status or 'all'})* — Page {page + 1}/{total_pages}\n"]
        for p in payments:
            status_emoji = "✅" if p["status"] == "completed" else "⏳" if p["status"] == "pending" else "❌"
            curr_emoji = "⭐" if p["currency"] == "XTR" else "💎"
            lines.append(f"{status_emoji} `{p['user_id']}` | {p['amount']}{curr_emoji} | {p['license_type']} | {p['created_at'][:10]}")
        
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️", callback_data=f"admin:payments_list:{status or 'all'}:{page - 1}"))
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton("➡️", callback_data=f"admin:payments_list:{status or 'all'}:{page + 1}"))
        
        keyboard = []
        if nav_row:
            keyboard.append(nav_row)
        keyboard.append([InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:payments_menu")])
        
        await q.edit_message_text("\n".join(lines), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    # =====================================================
    # REPORTS MENU
    # =====================================================
    elif cmd == "reports_menu":
        keyboard = [
            [InlineKeyboardButton(t.get('admin_global_stats', '📊 Global Stats'), callback_data="admin:global_stats:all:all")],
            [InlineKeyboardButton(t.get('admin_demo_stats', '🎮 Demo Stats'), callback_data="admin:global_stats:demo:all"),
             InlineKeyboardButton(t.get('admin_real_stats', '💰 Real Stats'), callback_data="admin:global_stats:real:all")],
            [InlineKeyboardButton(t.get('admin_strategy_breakdown', '🎯 By Strategy'), callback_data="admin:strategy_breakdown:all")],
            [InlineKeyboardButton(t.get('admin_top_traders', '🏆 Top Traders'), callback_data="admin:top_traders:all:all")],
            [InlineKeyboardButton(t.get('admin_user_report', '👤 User Report'), callback_data="admin:user_report_select")],
            [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:menu")],
        ]
        await q.edit_message_text(
            t.get('admin_reports_menu', '📊 *Reports & Analytics*\n\nSelect report type:'),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif cmd.startswith("global_stats:"):
        parts = cmd.split(":")
        account_type = parts[1] if len(parts) > 1 and parts[1] != "all" else None
        period = parts[2] if len(parts) > 2 else "all"
        
        stats = get_global_trade_stats(account_type=account_type, period=period)
        account_label = account_type.upper() if account_type else "ALL"
        period_label = period.title()
        
        text = f"📊 *Global Stats — {account_label} — {period_label}*\n\n"
        text += f"👥 Users: {stats['unique_users']}\n"
        text += f"📈 Total trades: {stats['total_trades']}\n"
        text += f"📂 Open positions: {stats['open_positions']} ({stats['users_with_open']} users)\n"
        text += f"✅ Wins: {stats['wins']} ({stats['winrate']:.1f}%)\n"
        text += f"💰 Total PnL: ${stats['total_pnl']:.2f}\n"
        text += f"📊 Avg PnL%: {stats['avg_pnl_pct']:.2f}%\n"
        text += f"📈 Longs: {stats['long_count']} | 📉 Shorts: {stats['short_count']}\n"
        text += f"💹 Profit Factor: {stats['profit_factor']:.2f}\n"
        
        # Period selector
        period_row = []
        for p, label in [("today", "Today"), ("week", "Week"), ("month", "Month"), ("all", "All")]:
            if p == period:
                label = f"[{label}]"
            period_row.append(InlineKeyboardButton(label, callback_data=f"admin:global_stats:{account_type or 'all'}:{p}"))
        
        keyboard = [
            period_row,
            [InlineKeyboardButton("🎮 Demo", callback_data=f"admin:global_stats:demo:{period}"),
             InlineKeyboardButton("💰 Real", callback_data=f"admin:global_stats:real:{period}"),
             InlineKeyboardButton("📊 All", callback_data=f"admin:global_stats:all:{period}")],
            [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:reports_menu")],
        ]
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif cmd.startswith("strategy_breakdown:"):
        parts = cmd.split(":")
        account_type = parts[1] if len(parts) > 1 and parts[1] != "all" else None
        
        stats_by_strat = get_global_stats_by_strategy(period="all", account_type=account_type)
        account_label = account_type.upper() if account_type else "ALL"
        
        text = f"🎯 *Strategy Breakdown — {account_label}*\n\n"
        
        for strat, stats in stats_by_strat.items():
            if strat == "all":
                continue
            if stats["total_trades"] > 0:
                text += f"*{strat.upper()}*\n"
                text += f"  Trades: {stats['total_trades']} | WR: {stats['winrate']:.1f}%\n"
                text += f"  PnL: ${stats['total_pnl']:.2f} | PF: {stats['profit_factor']:.2f}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🎮 Demo", callback_data="admin:strategy_breakdown:demo"),
             InlineKeyboardButton("💰 Real", callback_data="admin:strategy_breakdown:real"),
             InlineKeyboardButton("📊 All", callback_data="admin:strategy_breakdown:all")],
            [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:reports_menu")],
        ]
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif cmd.startswith("top_traders:"):
        parts = cmd.split(":")
        account_type = parts[1] if len(parts) > 1 and parts[1] != "all" else "demo"
        period = parts[2] if len(parts) > 2 else "all"
        
        traders = get_top_traders(period=period, account_type=account_type, limit=10)
        account_label = account_type.upper()
        period_label = period.title()
        
        text = f"🏆 *Top 10 Traders — {account_label} — {period_label}*\n\n"
        
        for i, tr in enumerate(traders, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} `{tr['user_id']}` — ${tr['total_pnl']:.2f} ({tr['trades']} trades, {tr['winrate']:.0f}% WR)\n"
        
        if not traders:
            text += "_No data_\n"
        
        period_row = []
        for p, label in [("today", "Today"), ("week", "Week"), ("month", "Month"), ("all", "All")]:
            if p == period:
                label = f"[{label}]"
            period_row.append(InlineKeyboardButton(label, callback_data=f"admin:top_traders:{account_type}:{p}"))
        
        keyboard = [
            period_row,
            [InlineKeyboardButton("🎮 Demo", callback_data=f"admin:top_traders:demo:{period}"),
             InlineKeyboardButton("💰 Real", callback_data=f"admin:top_traders:real:{period}")],
            [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:reports_menu")],
        ]
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif cmd == "user_report_select":
        ctx.user_data["mode"] = "admin_user_report"
        await q.edit_message_text(
            t.get('admin_enter_user_for_report', '👤 Enter user ID for detailed report:'),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get('btn_cancel', '❌ Cancel'), callback_data="admin:reports_menu")]
            ])
        )

    elif cmd.startswith("user_report:"):
        target_uid = int(cmd.split(":")[1])
        report = get_user_usage_report(target_uid)
        
        if not report["user_info"]:
            await q.edit_message_text(
                t.get('admin_user_not_found', '❌ User {uid} not found.').format(uid=target_uid),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:reports_menu")]
                ])
            )
            return
        
        user = report["user_info"]
        demo = report["demo_stats"]
        real = report["real_stats"]
        
        text = f"👤 *User Report — {target_uid}*\n\n"
        text += f"📊 *Demo Trading:*\n"
        text += f"  Trades: {demo['total']} | WR: {demo['winrate']:.1f}%\n"
        text += f"  PnL: ${demo['total_pnl']:.2f} | PF: {demo['profit_factor']:.2f}\n"
        text += f"  Open: {demo['open_count']}\n\n"
        
        text += f"💰 *Real Trading:*\n"
        text += f"  Trades: {real['total']} | WR: {real['winrate']:.1f}%\n"
        text += f"  PnL: ${real['total_pnl']:.2f} | PF: {real['profit_factor']:.2f}\n"
        text += f"  Open: {real['open_count']}\n\n"
        
        text += f"🎯 *By Strategy (Demo):*\n"
        for strat, stats in report["demo_by_strategy"].items():
            text += f"  {strat}: {stats['total']} trades, {stats['winrate']:.1f}% WR\n"
        
        if report["real_by_strategy"]:
            text += f"\n🎯 *By Strategy (Real):*\n"
            for strat, stats in report["real_by_strategy"].items():
                text += f"  {strat}: {stats['total']} trades, {stats['winrate']:.1f}% WR\n"
        
        keyboard = [
            [InlineKeyboardButton(t.get('admin_view_user', '👤 User Card'), callback_data=f"admin:user:{target_uid}")],
            [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:reports_menu")],
        ]
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def show_user_card(q, ctx, target_uid: int):
    """Display user card with all information and actions."""
    t = ctx.t
    user = get_user_full_info(target_uid)
    
    if not user:
        await q.edit_message_text(
            t.get('admin_user_not_found', '❌ User {uid} not found.').format(uid=target_uid),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:users_menu")]
            ])
        )
        return
    
    # Build user card text
    import datetime
    
    status_emoji = "🚫" if user["is_banned"] else "✅" if user["is_allowed"] else "⏳"
    license_emoji = {"premium": "💎", "basic": "🥈", "trial": "🎁"}.get(user["current_license"], "❌")
    
    # Format dates
    first_seen = datetime.datetime.fromtimestamp(user["first_seen_ts"]).strftime("%Y-%m-%d") if user["first_seen_ts"] else "—"
    last_seen = datetime.datetime.fromtimestamp(user["last_seen_ts"]).strftime("%Y-%m-%d %H:%M") if user["last_seen_ts"] else "—"
    license_expires = ""
    if user["license_expires"]:
        expires_dt = datetime.datetime.fromtimestamp(user["license_expires"])
        license_expires = expires_dt.strftime("%Y-%m-%d")
    
    # Strategies
    strategies = []
    if user["trade_oi"]: strategies.append("OI")
    if user["trade_rsi_bb"]: strategies.append("RSI")
    if user["trade_scryptomera"]: strategies.append("Scrypto")
    if user["trade_scalper"]: strategies.append("Scalp")
    if user["trade_elcaro"]: strategies.append("Elcaro")
    strategies_str = ", ".join(strategies) if strategies else "—"
    
    card_text = t.get('admin_user_card', '''👤 *User Card*

📋 *ID:* `{uid}`
{status_emoji} *Status:* {status}
📝 *Terms:* {terms}

{license_emoji} *License:* {license_type}
📅 *Expires:* {license_expires}
⏳ *Days Left:* {days_left}

🌐 *Language:* {lang}
📊 *Trading Mode:* {trading_mode}
💰 *% per Trade:* {percent}%
🪙 *Coins:* {coins}

🔌 *API Keys:*
  Demo: {demo_api}
  Real: {real_api}

📈 *Strategies:* {strategies}

📊 *Statistics:*
  Positions: {positions}
  Trades: {trades}
  PnL: {pnl}
  Winrate: {winrate}%

💳 *Payments:*
  Total: {payments_count}
  Stars: {total_stars}⭐

📅 *First Seen:* {first_seen}
🕐 *Last Seen:* {last_seen}
''').format(
        uid=user["user_id"],
        status_emoji=status_emoji,
        status="Banned" if user["is_banned"] else "Active" if user["is_allowed"] else "Pending",
        terms="✅" if user["terms_accepted"] else "❌",
        license_emoji=license_emoji,
        license_type=user["current_license"].title(),
        license_expires=license_expires or "—",
        days_left=user["license_days_left"] or "—",
        lang=user["lang"].upper(),
        trading_mode=user["trading_mode"],
        percent=user["percent"],
        coins=user["coins"],
        demo_api="✅" if user["has_demo_api"] else "❌",
        real_api="✅" if user["has_real_api"] else "❌",
        strategies=strategies_str,
        positions=user["positions_count"],
        trades=user["trades_count"],
        pnl=f"{user['total_pnl']:.2f}",
        winrate=f"{user['winrate']:.1f}",
        payments_count=user["payments_count"],
        total_stars=user["total_paid_stars"],
        first_seen=first_seen,
        last_seen=last_seen,
    )
    
    # Build action keyboard
    keyboard = []
    
    # License actions
    license_row = [
        InlineKeyboardButton(t.get('admin_btn_grant_lic', '🎁 Grant'), callback_data=f"admin:grant_lic:{target_uid}"),
    ]
    if user["current_license"] != "none" and user["license_days_left"]:
        license_row.append(InlineKeyboardButton(t.get('admin_btn_extend', '⏳ Extend'), callback_data=f"admin:extend_lic:{target_uid}"))
        license_row.append(InlineKeyboardButton(t.get('admin_btn_revoke', '🚫 Revoke'), callback_data=f"admin:revoke_lic:{target_uid}"))
    keyboard.append(license_row)
    
    # User status actions
    status_row = []
    if user["is_banned"]:
        status_row.append(InlineKeyboardButton(t.get('admin_btn_unban', '✅ Unban'), callback_data=f"admin:unban:{target_uid}"))
    else:
        status_row.append(InlineKeyboardButton(t.get('admin_btn_ban', '🚫 Ban'), callback_data=f"admin:ban:{target_uid}"))
    if not user["is_allowed"]:
        status_row.append(InlineKeyboardButton(t.get('admin_btn_approve', '✅ Approve'), callback_data=f"admin:approve:{target_uid}"))
    keyboard.append(status_row)
    
    # Other actions
    keyboard.append([
        InlineKeyboardButton(t.get('admin_btn_message', '✉️ Message'), callback_data=f"admin:msg_user:{target_uid}"),
        InlineKeyboardButton(t.get('admin_btn_delete', '🗑 Delete'), callback_data=f"admin:delete:{target_uid}"),
    ])
    
    # Back button
    keyboard.append([InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:users_menu")])
    
    await q.edit_message_text(
        card_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@require_access
@with_texts
@log_calls
async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # Skip if no user context (e.g., channel posts)
    if not update.effective_user:
        return
    uid   = update.effective_user.id
    text  = (update.message.text or "").strip()
    mode  = ctx.user_data.get("mode") if ctx.user_data else None

    # Handle Sovereign Owner input (emission, burn, policy)
    if await handle_sovereign_input(update, ctx):
        return

    # Handle HyperLiquid private key input FIRST
    if await handle_hl_private_key(update, ctx):
        return
    
    # Handle HyperLiquid strategy parameter input
    if await handle_hl_strategy_param(update, ctx):
        return

    # Handle promo code entry
    if mode == "enter_promo":
        ctx.user_data.pop("mode", None)
        t = LANGS.get(ctx.user_data.get("lang", DEFAULT_LANG), LANGS[DEFAULT_LANG])
        
        result = use_promo_code(uid, text.strip().upper())
        
        if result.get("success"):
            await update.message.reply_text(
                t.get("promo_success", "🎉 Promo code applied!\n\n{plan} activated for {days} days.").format(
                    plan=result["license_type"].title(),
                    days=result["days"]
                ),
                reply_markup=get_subscribe_menu_keyboard(t)
            )
        else:
            error_key = {
                "invalid_code": "promo_invalid",
                "code_inactive": "promo_invalid",
                "code_expired": "promo_expired",
                "code_used_up": "promo_used",
                "already_used": "promo_already_used",
            }.get(result.get("error"), "promo_invalid")
            
            await update.message.reply_text(
                t.get(error_key, "❌ Invalid promo code."),
                reply_markup=get_subscribe_menu_keyboard(t)
            )
        return

    # Handle admin license grant (user ID input)
    if mode == "admin_grant_user" and uid == ADMIN_ID:
        ctx.user_data.pop("mode", None)
        t = LANGS.get(ctx.user_data.get("lang", DEFAULT_LANG), LANGS[DEFAULT_LANG])
        
        try:
            target_uid = int(text.strip())
            plan = ctx.user_data.pop("admin_grant_type", "premium")
            period = ctx.user_data.pop("admin_grant_period", 1)
            
            result = set_user_license(
                user_id=target_uid,
                license_type=plan,
                period_months=period,
                admin_id=uid,
                payment_type="admin_grant",
            )
            
            if result.get("success"):
                await update.message.reply_text(
                    t.get("admin_license_granted", "✅ {plan} granted to user {uid} for {days} days.").format(
                        plan=plan.title(),
                        uid=target_uid,
                        days=result["days"]
                    ),
                    reply_markup=get_admin_license_keyboard(t)
                )
            else:
                await update.message.reply_text(
                    f"❌ Error: {result.get('error', 'Unknown')}",
                    reply_markup=get_admin_license_keyboard(t)
                )
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid user ID. Enter a number.",
                reply_markup=get_admin_license_keyboard(t)
            )
        return

    # Handle admin promo code creation
    if mode == "admin_promo_create" and uid == ADMIN_ID:
        ctx.user_data.pop("mode", None)
        t = LANGS.get(ctx.user_data.get("lang", DEFAULT_LANG), LANGS[DEFAULT_LANG])
        
        try:
            # Format: CODE:TYPE:DAYS:MAX_USES
            parts = text.strip().split(":")
            if len(parts) < 3:
                raise ValueError("Format: CODE:TYPE:DAYS:MAX_USES")
            
            code = parts[0].upper()
            license_type = parts[1].lower()
            days = int(parts[2])
            max_uses = int(parts[3]) if len(parts) > 3 else 1
            
            if license_type not in ["premium", "basic", "trial"]:
                raise ValueError("Type must be premium, basic, or trial")
            
            result = create_promo_code(
                code=code,
                license_type=license_type,
                period_days=days,
                max_uses=max_uses,
                admin_id=uid,
            )
            
            if result.get("success"):
                await update.message.reply_text(
                    t.get("admin_promo_created", "✅ Promo code created: {code}\nType: {type}\nDays: {days}\nMax uses: {max}").format(
                        code=code,
                        type=license_type,
                        days=days,
                        max=max_uses
                    ),
                    reply_markup=get_admin_license_keyboard(t)
                )
            else:
                await update.message.reply_text(
                    f"❌ Error: {result.get('error', 'Unknown')}",
                    reply_markup=get_admin_license_keyboard(t)
                )
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error: {e}\n\nFormat: `CODE:TYPE:DAYS:MAX_USES`",
                parse_mode="Markdown",
                reply_markup=get_admin_license_keyboard(t)
            )
        return

    # Handle admin user search
    if mode == "admin_search_user" and uid == ADMIN_ID:
        ctx.user_data.pop("mode", None)
        t = LANGS.get(ctx.user_data.get("lang", DEFAULT_LANG), LANGS[DEFAULT_LANG])
        
        try:
            target_uid = int(text.strip())
            user_info = get_user_full_info(target_uid)
            
            if user_info:
                # Found - show user card via callback simulation
                # Create a fake callback to reuse show_user_card
                keyboard = [
                    [InlineKeyboardButton(t.get('admin_view_card', '👤 View Card'), callback_data=f"admin:user:{target_uid}")],
                    [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:users_menu")],
                ]
                await update.message.reply_text(
                    t.get('admin_user_found', '✅ User {uid} found!').format(uid=target_uid),
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                await update.message.reply_text(
                    t.get('admin_user_not_found', '❌ User {uid} not found.').format(uid=target_uid),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:users_menu")]
                    ])
                )
        except ValueError:
            await update.message.reply_text(
                t.get('admin_invalid_user_id', '❌ Invalid user ID. Enter a number.'),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:users_menu")]
                ])
            )
        return

    # Handle admin user report by ID
    if mode == "admin_user_report" and uid == ADMIN_ID:
        ctx.user_data.pop("mode", None)
        t = LANGS.get(ctx.user_data.get("lang", DEFAULT_LANG), LANGS[DEFAULT_LANG])
        
        try:
            target_uid = int(text.strip())
            keyboard = [[InlineKeyboardButton(t.get('admin_view_report', '📊 View Report'), callback_data=f"admin:user_report:{target_uid}")]]
            await update.message.reply_text(
                t.get('admin_generating_report', '📊 Generating report for user {uid}...').format(uid=target_uid),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except ValueError:
            await update.message.reply_text(
                t.get('admin_invalid_user_id', '❌ Invalid user ID. Enter a number.'),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data="admin:reports_menu")]
                ])
            )
        return

    # Handle admin send message to user
    if mode == "admin_send_message" and uid == ADMIN_ID:
        ctx.user_data.pop("mode", None)
        target_uid = ctx.user_data.pop("admin_msg_target", None)
        t = LANGS.get(ctx.user_data.get("lang", DEFAULT_LANG), LANGS[DEFAULT_LANG])
        
        if target_uid:
            try:
                await ctx.bot.send_message(
                    target_uid,
                    f"📢 *Message from Admin:*\n\n{text}",
                    parse_mode="Markdown"
                )
                keyboard = [[InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data=f"admin:user:{target_uid}")]]
                await update.message.reply_text(
                    t.get('admin_message_sent', '✅ Message sent to user {uid}!').format(uid=target_uid),
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception as e:
                await update.message.reply_text(
                    t.get('admin_message_failed', '❌ Failed to send message: {error}').format(error=str(e)),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(t.get('btn_back', '⬅️ Back'), callback_data=f"admin:user:{target_uid}")]
                    ])
                )
        return

    if mode == "update_tpsl":
        try:
            parts = text.split()
            if len(parts) != 3:
                raise ValueError
            symbol, tp_str, sl_str = parts
            tp_price = float(tp_str.replace(",", "."))
            sl_price = float(sl_str.replace(",", "."))
        except ValueError:
            ctx.user_data.pop("mode", None)
            return await update.message.reply_text(
                ctx.t["invalid_tpsl_format"],
                reply_markup=main_menu_keyboard(ctx, update=update)
            )

        positions = await fetch_open_positions(uid)
        pos = next((p for p in positions if p.get("symbol") == symbol), None)
        if not pos:
            return await update.message.reply_text(
                ctx.t["no_position_symbol"].format(symbol=symbol),
                reply_markup=main_menu_keyboard(ctx, update=update)
            )

        current_price = float(pos["markPrice"])
        side = pos["side"]  

        if side == "Buy":
            if not (sl_price < current_price < tp_price):
                return await update.message.reply_text(
                    ctx.t["invalid_tpsl_long"].format(current=current_price),
                    reply_markup=main_menu_keyboard(ctx, update=update)
                )
        else: 
            if not (tp_price < current_price < sl_price):
                return await update.message.reply_text(
                    ctx.t["invalid_tpsl_short"].format(current=current_price),
                    reply_markup=main_menu_keyboard(ctx, update=update)
                )
        await set_trading_stop(uid, symbol, tp_price=tp_price, sl_price=sl_price, side_hint=side)
        ctx.user_data.pop("mode", None)
        return await update.message.reply_text(
            ctx.t["tpsl_set_success"].format(tp=tp_price, sl=sl_price, symbol=symbol),
            reply_markup=main_menu_keyboard(ctx, uid)
        )
    
    # Admin-only buttons
    if uid == ADMIN_ID:
        if text == ctx.t.get("button_licenses", "🔑 Licenses"):
            # Show license management menu
            await update.message.reply_text(
                ctx.t.get("admin_license_menu", "🔑 *License Management*"),
                parse_mode="Markdown",
                reply_markup=get_admin_license_keyboard(ctx.t)
            )
            return
        
        if text == ctx.t.get("button_admin", "👑 Admin"):
            return await cmd_admin(update, ctx)
    
    # New API Settings button
    if text == ctx.t.get("button_api_settings", "🔑 API"):
        return await cmd_api_settings(update, ctx)
    
    # Subscribe button
    if text in [ctx.t.get('button_subscribe', '💎 Subscribe'), "💎 Premium", ctx.t.get('button_subscribe', '💎 Premium')]:
        return await cmd_subscribe(update, ctx)
    
    # Exchange header button - shows exchange status/info (supports short 🔷 HL and full 🔷 HyperLiquid)
    if text.startswith("🔷 HL") or text.startswith("🔷 HyperLiquid") or text.startswith("🟠 Bybit"):
        return await cmd_exchange_status(update, ctx)
    
    # ═══════════════════════════════════════════════════════════════
    # ██  SWITCH EXCHANGE BUTTONS  ██
    # ═══════════════════════════════════════════════════════════════
    if text in ["🔄 Bybit", "🔄 Switch to Bybit"]:
        set_exchange_type(uid, "bybit")
        await update.message.reply_text(
            "🟠 *Switched to Bybit!*\n\n"
            "All trading commands now work with your Bybit account.\n"
            "Use ⚙️ Settings to configure trading mode (Demo/Real).",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(ctx, uid)
        )
        return
    
    if text in ["🔄 HyperLiquid", "🔄 Switch to HL"]:
        # Check if HL is configured
        hl_creds = get_hl_credentials(uid)
        if not hl_creds.get("hl_private_key"):
            await update.message.reply_text(
                "❌ *HyperLiquid not configured!*\n\n"
                "To trade on HyperLiquid:\n"
                "1️⃣ Press 🔑 API Keys\n"
                "2️⃣ Set up your wallet and private key\n\n"
                "_You can use testnet for practice!_",
                parse_mode="Markdown"
            )
            return
        set_exchange_type(uid, "hyperliquid")
        await update.message.reply_text(
            "🔷 *Switched to HyperLiquid!*\n\n"
            "All trading commands now work with HyperLiquid.\n"
            "Use ⚙️ Settings to switch between Testnet/Mainnet.",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(ctx, uid)
        )
        return
    
    # ═══════════════════════════════════════════════════════════════
    # ██  UNIFIED BUTTONS (work for both exchanges)  ██
    # ═══════════════════════════════════════════════════════════════
    active_exchange = get_exchange_type(uid)
    
    # Balance - works for current exchange with smart mode selection
    if text in ["💰 Balance", "💰 HL Balance", ctx.t.get('button_balance', '💰 Balance')]:
        trading_mode = get_trading_mode(uid)
        
        if active_exchange == "hyperliquid":
            # HyperLiquid: check testnet mode
            hl_creds = get_hl_credentials(uid)
            is_testnet = hl_creds.get("hl_testnet", False)
            # For now, show selection - can be optimized later
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🧪 Testnet", callback_data="balance:hl:testnet"),
                 InlineKeyboardButton("🌐 Mainnet", callback_data="balance:hl:mainnet")],
                [InlineKeyboardButton("🔙 Back", callback_data="menu:main")]
            ])
            await update.message.reply_text(
                "💰 *HyperLiquid Balance*\n\nSelect network:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            # Bybit: if only one mode, show directly
            if trading_mode in ('demo', 'real'):
                # Directly show balance for this mode
                return await show_balance_for_account(update, ctx, trading_mode)
            else:
                # Both modes - show selection
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎮 Demo", callback_data="balance:bybit:demo"),
                     InlineKeyboardButton("💎 Real", callback_data="balance:bybit:real")],
                    [InlineKeyboardButton("🔙 Back", callback_data="menu:main")]
                ])
                await update.message.reply_text(
                    "💰 *Bybit Balance*\n\nSelect account type:",
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
        return
    
    # Positions - works for current exchange with smart mode
    if text in ["📊 Positions", "📊 HL Positions", ctx.t.get('button_positions', '📊 Positions')]:
        if active_exchange == "hyperliquid":
            return await cmd_hl_positions(update, ctx)
        else:
            trading_mode = get_trading_mode(uid)
            if trading_mode in ('demo', 'real'):
                # Single mode - show directly
                return await show_positions_direct(update, ctx, trading_mode)
            else:
                # Both modes - use standard flow with selection
                return await cmd_positions(update, ctx)
    
    # Orders - works for current exchange with smart mode
    if text in ["📈 Orders", "📈 HL Orders", ctx.t.get('button_orders', '📈 Orders')]:
        if active_exchange == "hyperliquid":
            return await cmd_hl_orders(update, ctx)
        else:
            trading_mode = get_trading_mode(uid)
            if trading_mode in ('demo', 'real'):
                # Single mode - show directly
                return await show_orders_direct(update, ctx, trading_mode)
            else:
                # Both modes - use standard flow with selection
                return await cmd_openorders(update, ctx)
    
    # History - works for current exchange
    if text in ["📋 History", "📋 HL History"]:
        if active_exchange == "hyperliquid":
            return await cmd_hl_history(update, ctx)
        else:
            return await cmd_trade_stats(update, ctx)
    
    # Trade - works for current exchange
    if text in ["🎯 Trade", "🎯 HL Trade"]:
        if active_exchange == "hyperliquid":
            return await cmd_hl_trade(update, ctx)
        else:
            # Bybit quick trade - show order prompt
            await update.message.reply_text(
                "🎯 *Quick Trade*\n\n"
                "Send your order in format:\n"
                "`BTCUSDT long 10 10x`\n"
                "`ETHUSDT short 5% 20x`\n\n"
                "Or use /terminal for advanced trading.",
                parse_mode="Markdown"
            )
            return
    
    # Close All - works for current exchange  
    if text in ["❌ Close All", "❌ HL Close All"]:
        if active_exchange == "hyperliquid":
            return await cmd_hl_close_all(update, ctx)
        else:
            # Show positions with close buttons (user can close all from there)
            return await cmd_open_positions(update, ctx)
    
    # Market - Bybit only
    if text in ["📉 Market", ctx.t.get('button_market', '📉 Market')]:
        return await cmd_market(update, ctx)
    
    # Settings - works for current exchange
    if text in ["⚙️ Settings", "⚙️ HL Settings", ctx.t.get('button_settings', '⚙️ Settings')]:
        if active_exchange == "hyperliquid":
            return await cmd_hl_settings(update, ctx)
        else:
            return await cmd_show_config(update, ctx)
    
    # API Keys - unified API management
    if text in ["🔑 API Keys", "🔑 HL API", "🟠 Bybit API", "🔷 HL API"]:
        return await cmd_api_settings(update, ctx)
    
    # Strategies button
    if text in ["🤖 Strategies", ctx.t.get('button_strategy_settings', '⚙️ Strategies')]:
        return await cmd_strategy_settings(update, ctx)
    
    # ═══════════════════════════════════════════════════════════════
    # ██  LEGACY BUTTONS (for backward compatibility)  ██
    # ═══════════════════════════════════════════════════════════════
    
    # WebApp button
    if text == ctx.t.get("button_webapp", "🌐 WebApp"):
        return await cmd_webapp(update, ctx)
    
    # Spot Settings button
    if text == ctx.t.get("button_spot_settings", "💹 Spot Settings"):
        return await cmd_spot_settings(update, ctx)
    
    # Handle spot text input (e.g., DCA amount)
    if ctx.user_data.get("spot_awaiting"):
        handled = await handle_spot_text_input(update, ctx)
        if handled:
            return
    
    # Legacy API buttons (for backward compatibility, redirect to new menu)
    if text == ctx.t.get("button_api", "🔑 API") or text == ctx.t.get("button_secret", "🔒 Secret"):
        return await cmd_api_settings(update, ctx)

    if text == ctx.t["button_lang"]:
        return await cmd_lang(update, ctx)

    if text == ctx.t["button_balance"]:
        return await cmd_account(update, ctx)

    if text == ctx.t["button_orders"]:
        return await cmd_openorders(update, ctx)

    if text == ctx.t["button_positions"]:
        return await cmd_open_positions(update, ctx)

    if text == ctx.t.get("button_stats", "📊 Statistics"):
        return await cmd_trade_stats(update, ctx)

    if text == ctx.t["button_market"]:
        return await cmd_market(update, ctx)

    if text == ctx.t["button_settings"]:
        return await cmd_show_config(update, ctx)

    if text == ctx.t["button_indicators"]:
        return await cmd_indicators(update, ctx)

    if text == ctx.t["button_limit_only"]:
        return await cmd_toggle_limit(update, ctx)

    if text == ctx.t["button_toggle_oi"]:
        return await cmd_toggle_oi(update, ctx)

    if text == ctx.t["button_scryptomera"]:
        return await cmd_toggle_scryptomera(update, ctx)

    if text == ctx.t.get("button_scalper"):
        return await cmd_toggle_scalper(update, ctx)

    if text == ctx.t.get("button_elcaro"):
        return await cmd_toggle_elcaro(update, ctx)

    if text == ctx.t.get("button_fibonacci"):
        return await cmd_toggle_fibonacci(update, ctx)

    if text == ctx.t.get("button_strategy_settings", "⚙️ Strategy Settings"):
        return await cmd_strategy_settings(update, ctx)

    if text == ctx.t["button_toggle_rsi_bb"]:
        return await cmd_toggle_rsi_bb(update, ctx)

    if text == ctx.t["button_support"]:
        return await cmd_support(update, ctx)

    if text == ctx.t["button_coins"]:
        return await cmd_select_coin_group(update, ctx)

    if text == ctx.t["button_toggle_atr"]:
        return await cmd_toggle_atr(update, ctx)

    if text == ctx.t["button_update_tpsl"]:
        return await cmd_update_tpsl(update, ctx)

    # Handle new API key entry modes
    if mode and mode.startswith("enter_api_"):
        api_type = mode.replace("enter_api_", "")
        creds = get_all_user_credentials(uid)
        
        if api_type == "demo_key":
            set_user_credentials(uid, text, creds.get("demo_api_secret") or "", "demo")
            clear_expired_api_cache(uid, "demo")
        elif api_type == "demo_secret":
            set_user_credentials(uid, creds.get("demo_api_key") or "", text, "demo")
            clear_expired_api_cache(uid, "demo")
        elif api_type == "real_key":
            set_user_credentials(uid, text, creds.get("real_api_secret") or "", "real")
            clear_expired_api_cache(uid, "real")
        elif api_type == "real_secret":
            set_user_credentials(uid, creds.get("real_api_key") or "", text, "real")
            clear_expired_api_cache(uid, "real")
        
        ctx.user_data.pop("mode", None)
        
        # Show updated API settings
        creds = get_all_user_credentials(uid)
        msg = format_api_settings_message(ctx.t, creds)
        keyboard = get_api_settings_keyboard(ctx.t, creds)
        await update.message.reply_text(
            ctx.t.get("api_key_saved", "✅ Saved!") + "\n\n" + msg,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return

    # Legacy API modes (backward compatibility)
    if mode == "enter_api":
        set_user_credentials(uid, text, "", "demo")
        clear_expired_api_cache(uid, "demo")
        ctx.user_data.pop("mode", None)
        return await update.message.reply_text(ctx.t.get("api_saved", "API saved"), reply_markup=main_menu_keyboard(ctx, update=update))

    if mode == "enter_secret":
        creds = get_all_user_credentials(uid)
        set_user_credentials(uid, creds.get("demo_api_key") or "", text, "demo")
        clear_expired_api_cache(uid, "demo")
        ctx.user_data.pop("mode", None)
        return await update.message.reply_text(ctx.t.get("secret_saved", "Secret saved"), reply_markup=main_menu_keyboard(ctx, update=update))

    # Handle global setting input
    global_setting = ctx.user_data.get("global_setting_mode")
    if global_setting:
        try:
            value = float(text.replace(",", ".").strip())
            
            if global_setting in ("percent", "sl_percent", "tp_percent"):
                if value <= 0 or value > 100:
                    raise ValueError("Value must be between 0 and 100")
            elif global_setting == "leverage":
                if value < 1 or value > 100 or int(value) != value:
                    raise ValueError("Leverage must be integer between 1 and 100")
                value = int(value)
            # ATR settings validation
            elif global_setting == "atr_trigger_pct":
                if value < 0.1 or value > 50:
                    raise ValueError("ATR Trigger must be between 0.1 and 50")
            elif global_setting == "atr_step_pct":
                if value < 0.1 or value > 20:
                    raise ValueError("ATR Step must be between 0.1 and 20")
            elif global_setting == "atr_period":
                if value < 1 or value > 100 or int(value) != value:
                    raise ValueError("ATR Period must be integer between 1 and 100")
                value = int(value)
            elif global_setting == "atr_multiplier":
                if value < 0.1 or value > 10:
                    raise ValueError("ATR Multiplier must be between 0.1 and 10")
            
            logger.info(f"[GLOBAL-SETTING] uid={uid} saving {global_setting}={value}")
            set_user_field(uid, global_setting, value)
            ctx.user_data.pop("global_setting_mode", None)
            
            param_names = {
                "percent": "Entry %",
                "sl_percent": "SL %",
                "tp_percent": "TP %",
                "leverage": "Leverage",
                "atr_trigger_pct": "ATR Trigger %",
                "atr_step_pct": "ATR Step %",
                "atr_period": "ATR Period",
                "atr_multiplier": "ATR Multiplier",
            }
            
            # Check if ATR setting - go back to ATR menu
            if global_setting.startswith("atr_"):
                await update.message.reply_text(
                    f"✅ {param_names.get(global_setting, global_setting)} → *{value}*\n\nUpdated successfully!",
                    parse_mode="Markdown"
                )
                return
            
            # Get updated config for settings display
            cfg = get_user_config(uid)
            sl_val = cfg.get('sl_percent', cfg.get('sl_pct', 3))
            tp_val = cfg.get('tp_percent', cfg.get('tp_pct', 6))
            ladder_enabled = cfg.get('limit_ladder_enabled', 0)
            ladder_count = cfg.get('limit_ladder_count', 3)
            ladder_status = "✅" if ladder_enabled else "❌"
            order_type = cfg.get('global_order_type', 'market')
            order_emoji = "⚡" if order_type == "market" else "🎯"
            order_label = "Market" if order_type == "market" else "Limit"
            trading_mode = get_trading_mode(uid) or "demo"
            mode_emoji = {"demo": "🧪", "real": "💰", "both": "🔄"}.get(trading_mode, "🧪")
            mode_label = {"demo": "Demo", "real": "Real", "both": "Both"}.get(trading_mode, "Demo")
            
            lines = [ctx.t.get('global_settings_header', '🌐 *Global Trading Settings*')]
            lines.append(f"\n✅ {param_names.get(global_setting, global_setting)} → *{value}*\n")
            lines.append(f"📊 Entry %: *{cfg.get('percent', 1)}%*")
            lines.append(f"🛑 SL %: *{sl_val}%*")
            lines.append(f"🎯 TP %: *{tp_val}%*")
            lines.append(f"🎚 Leverage: *{cfg.get('leverage', 10)}x*")
            lines.append(f"{order_emoji} Order type: *{order_label}*")
            lines.append(f"{mode_emoji} Account: *{mode_label}*")
            lines.append("")
            lines.append(f"📈 {ctx.t.get('limit_ladder', 'Limit Ladder')}: {ladder_status} (*{ladder_count}* orders)")
            
            buttons = [
                [InlineKeyboardButton(ctx.t.get('param_percent', '📊 Entry %'), callback_data="global_param:percent")],
                [InlineKeyboardButton(ctx.t.get('param_sl', '🛑 Stop-Loss %'), callback_data="global_param:sl_percent")],
                [InlineKeyboardButton(ctx.t.get('param_tp', '🎯 Take-Profit %'), callback_data="global_param:tp_percent")],
                [InlineKeyboardButton(ctx.t.get('param_leverage', '🎚 Leverage'), callback_data="global_param:leverage")],
                [InlineKeyboardButton(f"{order_emoji} Order: {order_label}", callback_data="global_param:order_type")],
                [InlineKeyboardButton(f"{mode_emoji} Account: {mode_label}", callback_data="global_param:trading_mode")],
                [InlineKeyboardButton(f"{ladder_status} {ctx.t.get('limit_ladder', '📈 Limit Ladder')}", callback_data="global_ladder:toggle")],
                [InlineKeyboardButton(ctx.t.get('limit_ladder_settings', '⚙️ Ladder Settings'), callback_data="global_ladder:settings")],
                [InlineKeyboardButton(ctx.t.get('btn_back', '⬅️ Back'), callback_data="strat_set:back")],
            ]
            
            await update.message.reply_text(
                "\n".join(lines),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return
        except ValueError as e:
            await update.message.reply_text(
                ctx.t.get('invalid_value', '❌ Invalid value: {error}').format(error=str(e))
            )
            return

    # Handle ladder setting input
    ladder_setting = ctx.user_data.get("ladder_setting_mode")
    if ladder_setting:
        try:
            value = float(text.replace(",", ".").strip())
            if value <= 0 or value > 100:
                raise ValueError("Value must be between 0 and 100")
            
            param_type = ladder_setting["type"]  # "pct_entry" or "pct_deposit"
            leg_idx = ladder_setting["leg"]
            
            cfg = get_user_config(uid)
            ladder_settings = cfg.get("limit_ladder_settings", [])
            
            # Ensure list has enough elements
            while len(ladder_settings) <= leg_idx:
                ladder_settings.append({"pct_from_entry": 1.0, "pct_of_deposit": 5.0})
            
            if param_type == "pct_entry":
                ladder_settings[leg_idx]["pct_from_entry"] = value
            else:
                ladder_settings[leg_idx]["pct_of_deposit"] = value
            
            set_user_field(uid, "limit_ladder_settings", json.dumps(ladder_settings))
            ctx.user_data.pop("ladder_setting_mode", None)
            
            # Return to ladder settings menu
            cfg = get_user_config(uid)
            ladder_count = cfg.get('limit_ladder_count', 3)
            ladder_settings = cfg.get('limit_ladder_settings', [])
            
            if not ladder_settings:
                ladder_settings = [
                    {"pct_from_entry": 1.0, "pct_of_deposit": 5.0},
                    {"pct_from_entry": 2.0, "pct_of_deposit": 7.0},
                    {"pct_from_entry": 3.0, "pct_of_deposit": 10.0},
                ]
            
            lines = [ctx.t.get('limit_ladder_header', '📈 *Limit Ladder Settings*')]
            lines.append(f"\n✅ Order {leg_idx+1} updated!\n")
            lines.append(f"📊 {ctx.t.get('ladder_count', 'Number of orders')}: *{ladder_count}*")
            lines.append("")
            for i, leg in enumerate(ladder_settings[:ladder_count], 1):
                pct_entry = leg.get('pct_from_entry', 1.0)
                pct_deposit = leg.get('pct_of_deposit', 5.0)
                lines.append(f"📉 *Order {i}*: -{pct_entry}% @ {pct_deposit}% deposit")
            
            buttons = [
                [InlineKeyboardButton(f"📊 {ctx.t.get('ladder_count', 'Count')}: {ladder_count}", callback_data="global_ladder:count")],
            ]
            for i in range(min(ladder_count, 5)):
                leg = ladder_settings[i] if i < len(ladder_settings) else {"pct_from_entry": 1.0, "pct_of_deposit": 5.0}
                pct_entry = leg.get('pct_from_entry', 1.0)
                pct_deposit = leg.get('pct_of_deposit', 5.0)
                buttons.append([
                    InlineKeyboardButton(f"📉 #{i+1}: -{pct_entry}%", callback_data=f"global_ladder:pct_entry:{i}"),
                    InlineKeyboardButton(f"💰 #{i+1}: {pct_deposit}%", callback_data=f"global_ladder:pct_deposit:{i}"),
                ])
            buttons.append([InlineKeyboardButton(ctx.t.get('btn_back', '⬅️ Back'), callback_data="strat_set:global")])
            
            await update.message.reply_text(
                "\n".join(lines),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return
        except ValueError as e:
            await update.message.reply_text(
                ctx.t.get('invalid_value', '❌ Invalid value: {error}').format(error=str(e))
            )
            return

    # Handle strategy setting input
    strat_mode = ctx.user_data.get("strat_setting_mode")
    if strat_mode:
        strategy = strat_mode.get("strategy")
        param = strat_mode.get("param")
        try:
            value = float(text.replace(",", ".").strip())
            
            # Different validation for different params
            if param in ("percent", "sl_percent", "tp_percent", "atr_trigger_pct",
                         "long_percent", "long_sl_percent", "long_tp_percent", "long_atr_trigger_pct",
                         "short_percent", "short_sl_percent", "short_tp_percent", "short_atr_trigger_pct"):
                if value <= 0 or value > 100:
                    raise ValueError("Value must be between 0 and 100")
            elif param == "min_quality":
                if value < 0 or value > 100:
                    raise ValueError("Min quality must be between 0 and 100")
                value = int(value)
            elif param in ("atr_periods", "long_atr_periods", "short_atr_periods"):
                if value < 1 or value > 50 or int(value) != value:
                    raise ValueError("ATR periods must be integer between 1 and 50")
                value = int(value)
            elif param in ("atr_multiplier_sl", "long_atr_multiplier_sl", "short_atr_multiplier_sl"):
                if value <= 0 or value > 10:
                    raise ValueError("ATR multiplier must be between 0 and 10")
            elif param == "leverage":
                if value < 1 or value > 100 or int(value) != value:
                    raise ValueError("Leverage must be integer between 1 and 100")
                value = int(value)
            else:
                if value <= 0 or value > 100:
                    raise ValueError("Value must be between 0 and 100")
            
            # Get context for saving
            context = get_user_trading_context(uid)
            db.set_strategy_setting(uid, strategy, param, value,
                                   context["exchange"], context["account_type"])
            ctx.user_data.pop("strat_setting_mode", None)
            
            display_name = STRATEGY_NAMES_MAP.get(strategy, strategy.upper())
            param_name = {
                "percent": "Entry %",
                "sl_percent": "SL %",
                "tp_percent": "TP %",
                "atr_periods": "ATR Periods",
                "atr_multiplier_sl": "ATR Multiplier",
                "atr_trigger_pct": "ATR Trigger %",
                "leverage": "Leverage",
                "min_quality": "Min Quality %",
                # LONG
                "long_percent": "LONG Entry %",
                "long_sl_percent": "LONG SL %",
                "long_tp_percent": "LONG TP %",
                "long_atr_periods": "LONG ATR Periods",
                "long_atr_multiplier_sl": "LONG ATR Multiplier",
                "long_atr_trigger_pct": "LONG ATR Trigger %",
                # SHORT
                "short_percent": "SHORT Entry %",
                "short_sl_percent": "SHORT SL %",
                "short_tp_percent": "SHORT TP %",
                "short_atr_periods": "SHORT ATR Periods",
                "short_atr_multiplier_sl": "SHORT ATR Multiplier",
                "short_atr_trigger_pct": "SHORT ATR Trigger %",
            }.get(param, param)
            
            # Determine which keyboard to return to based on param
            if param.startswith("long_"):
                strat_settings = db.get_strategy_settings(uid, strategy, context["exchange"], context["account_type"])
                reply_kb = get_strategy_side_keyboard(strategy, "long", ctx.t, strat_settings)
            elif param.startswith("short_"):
                strat_settings = db.get_strategy_settings(uid, strategy, context["exchange"], context["account_type"])
                reply_kb = get_strategy_side_keyboard(strategy, "short", ctx.t, strat_settings)
            else:
                strat_settings = db.get_strategy_settings(uid, strategy, context["exchange"], context["account_type"])
                reply_kb = get_strategy_param_keyboard(strategy, ctx.t, strat_settings)
            
            # Show confirmation and return to appropriate settings menu
            await update.message.reply_text(
                ctx.t.get('strat_setting_saved', '✅ {name} {param} set to {value}').format(
                    name=display_name, param=param_name, value=value
                ),
                reply_markup=reply_kb
            )
            return
        except (ValueError, TypeError) as e:
            # Show error but stay in input mode
            return await update.message.reply_text(
                ctx.t.get('invalid_number', '❌ Invalid number. Enter a value between 0 and 100.'),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(ctx.t.get('btn_cancel', '❌ Cancel'), callback_data=f"strat_set:{strategy}")]
                ])
            )

    # Handle DCA setting input
    dca_mode = ctx.user_data.get("dca_setting_mode")
    if dca_mode:
        try:
            value = float(text.replace(",", ".").strip())
            if value <= 0 or value > 100:
                raise ValueError("Value must be between 0 and 100")
            
            set_user_field(uid, dca_mode, value)
            ctx.user_data.pop("dca_setting_mode", None)
            
            leg_name = "Leg 1" if dca_mode == "dca_pct_1" else "Leg 2"
            
            # Return to DCA settings menu
            return await update.message.reply_text(
                ctx.t.get('dca_setting_saved', '✅ DCA {leg} set to {value}%').format(
                    leg=leg_name, value=value
                ),
                reply_markup=get_dca_settings_keyboard(ctx.t)
            )
        except (ValueError, TypeError):
            return await update.message.reply_text(
                ctx.t.get('invalid_number', '❌ Invalid number. Enter a value between 0 and 100.'),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(ctx.t.get('btn_cancel', '❌ Cancel'), callback_data="strat_set:dca")]
                ])
            )

    if mode == "select_coins":
        coins = [c.strip().upper() for c in text.split(",") if c.strip()]
        set_user_field(uid, "coins", ",".join(coins))
        ctx.user_data.pop("mode", None)
        return await update.message.reply_text(
            ctx.t["coins_set_success"].format(coins=", ".join(coins) if coins else "ALL"),
            reply_markup=main_menu_keyboard(ctx, update=update)
        )
    return await update.message.reply_text(ctx.t.get("fallback", "Command not recognized."),
                                           reply_markup=main_menu_keyboard(ctx, update=update))


# =====================================================
# SUBSCRIPTION & PAYMENT HANDLERS
# =====================================================

def get_subscribe_menu_keyboard(t: dict) -> InlineKeyboardMarkup:
    """Main subscription menu keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t.get("btn_premium", "💎 Premium"), callback_data="sub:plan:premium")],
        [InlineKeyboardButton(t.get("btn_basic", "🥈 Basic"), callback_data="sub:plan:basic")],
        [InlineKeyboardButton(t.get("btn_trial", "🎁 Trial (Free)"), callback_data="sub:plan:trial")],
        [InlineKeyboardButton(t.get("btn_enter_promo", "🎟 Promo Code"), callback_data="sub:promo")],
        [InlineKeyboardButton(t.get("btn_my_subscription", "📋 My Subscription"), callback_data="sub:my")],
        [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="back:main")],
    ])


def get_premium_period_keyboard(t: dict) -> InlineKeyboardMarkup:
    """Premium period selection keyboard with TRC prices."""
    prices = LICENSE_PRICES["premium"]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"💎 1 Month — {prices['trc'][1]:.0f} TRC",
            callback_data="sub:period:premium:1"
        )],
        [InlineKeyboardButton(
            f"💎 3 Months — {prices['trc'][3]:.0f} TRC (-10%)",
            callback_data="sub:period:premium:3"
        )],
        [InlineKeyboardButton(
            f"💎 6 Months — {prices['trc'][6]:.0f} TRC (-20%)",
            callback_data="sub:period:premium:6"
        )],
        [InlineKeyboardButton(
            f"💎 12 Months — {prices['trc'][12]:.0f} TRC (-30%)",
            callback_data="sub:period:premium:12"
        )],
        [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="sub:menu")],
    ])


def get_basic_period_keyboard(t: dict) -> InlineKeyboardMarkup:
    """Basic period selection keyboard with TRC prices."""
    prices = LICENSE_PRICES["basic"]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"🥈 1 Month — {prices['trc'][1]:.0f} TRC",
            callback_data="sub:period:basic:1"
        )],
        [InlineKeyboardButton(
            f"🥈 3 Months — {prices['trc'][3]:.0f} TRC (-10%)",
            callback_data="sub:period:basic:3"
        )],
        [InlineKeyboardButton(
            f"🥈 6 Months — {prices['trc'][6]:.0f} TRC (-20%)",
            callback_data="sub:period:basic:6"
        )],
        [InlineKeyboardButton(
            f"🥈 12 Months — {prices['trc'][12]:.0f} TRC (-30%)",
            callback_data="sub:period:basic:12"
        )],
        [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="sub:menu")],
    ])


def get_payment_method_keyboard(t: dict, plan: str, period: int) -> InlineKeyboardMarkup:
    """Payment method selection keyboard - TRC only (WEB3 native)."""
    prices = LICENSE_PRICES.get(plan, {})
    trc_price = prices.get("trc", {}).get(period, 0)
    
    buttons = [
        [InlineKeyboardButton(
            f"🪙 Pay {trc_price:.0f} TRC (~${trc_price:.0f})",
            callback_data=f"sub:trc:{plan}:{period}"
        )],
        [InlineKeyboardButton(
            f"💳 Buy TRC (Deposit)",
            callback_data=f"wallet:deposit"
        )],
        [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data=f"sub:plan:{plan}")],
    ]
    return InlineKeyboardMarkup(buttons)


# =====================================================
# SOVEREIGN OWNER CONTROLS (Monetary Authority)
# =====================================================

@log_calls
async def cmd_sovereign(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    SOVEREIGN OWNER COMMAND: Full monetary control panel.
    Only available to the sovereign owner (SOVEREIGN_OWNER_ID).
    """
    uid = update.effective_user.id
    
    if not is_sovereign_owner(uid):
        await update.message.reply_text("❌ Unauthorized. This command is only for the Sovereign Owner.")
        return
    
    # Get comprehensive dashboard
    dashboard = await get_owner_dashboard(uid)
    
    if not dashboard:
        await update.message.reply_text("❌ Error loading dashboard.")
        return
    
    treasury = dashboard["treasury"]
    global_stats = dashboard["global"]
    
    text = f"""🏛️ *SOVEREIGN MONETARY CONTROL PANEL*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

👑 *{SOVEREIGN_OWNER_NAME}*
🎖️ {dashboard['owner_title']}

📊 *SUPPLY METRICS*
├ Current Supply: *{treasury['current_supply']:,.0f} TRC*
├ Max Supply: *{treasury['max_supply']:,.0f} TRC*
├ Utilization: *{treasury['supply_utilization']*100:.2f}%*
└ Circulating: *{treasury['current_supply'] - treasury['treasury_balance']:,.0f} TRC*

🏦 *TREASURY*
├ Treasury Balance: *{treasury['treasury_balance']:,.0f} TRC*
├ Liquidity Pool: *{treasury['liquidity_pool']:,.0f} TRC*
└ Fees Collected: *{treasury['total_fees_collected']:,.2f} TRC*

📈 *RESERVES*
├ Total Value: *${treasury['total_reserve_value']:,.0f}*
├ Reserve Ratio: *{treasury['reserve_ratio']*100:.1f}%*
└ Status: {'✅ Healthy' if treasury['reserve_ratio'] >= 1.0 else '⚠️ Under-collateralized'}

💎 *STAKING*
├ Total Staked: *{treasury['total_staked']:,.0f} TRC*
├ Current APY: *{treasury['staking_apy']*100:.1f}%*
└ Rewards Distributed: *{treasury['total_rewards_distributed']:,.2f} TRC*

🔗 *BLOCKCHAIN*
├ Chain: *{CHAIN_NAME}*
├ Chain ID: *{CHAIN_ID}*
├ Wallets: *{global_stats['total_wallets']:,}*
├ Transactions: *{global_stats['total_transactions']:,}*
└ Block Height: *{global_stats['block_height']:,}*

⚡ *STATUS:* {'🔴 PAUSED' if treasury['is_paused'] else '🟢 ACTIVE'}
📊 *Emission Events:* {dashboard['emission_count']}
"""

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💵 Emit Tokens", callback_data="sovereign:emit"),
            InlineKeyboardButton("🔥 Burn Tokens", callback_data="sovereign:burn")
        ],
        [
            InlineKeyboardButton("📊 Set APY", callback_data="sovereign:set_apy"),
            InlineKeyboardButton("💰 Set Fees", callback_data="sovereign:set_fees")
        ],
        [
            InlineKeyboardButton("🎁 Distribute Rewards", callback_data="sovereign:distribute"),
            InlineKeyboardButton("💸 Treasury Transfer", callback_data="sovereign:transfer")
        ],
        [
            InlineKeyboardButton("❄️ Freeze Wallet", callback_data="sovereign:freeze"),
            InlineKeyboardButton("🔓 Unfreeze Wallet", callback_data="sovereign:unfreeze")
        ],
        [
            InlineKeyboardButton("⏸️ Pause Protocol" if not treasury['is_paused'] else "▶️ Resume Protocol", 
                               callback_data="sovereign:pause" if not treasury['is_paused'] else "sovereign:resume"),
        ],
        [InlineKeyboardButton("🔄 Refresh", callback_data="sovereign:refresh")]
    ])
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def on_sovereign_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle sovereign owner callbacks."""
    q = update.callback_query
    await q.answer()
    
    uid = update.effective_user.id
    
    if not is_sovereign_owner(uid):
        await q.edit_message_text("❌ Unauthorized.")
        return
    
    data = q.data  # sovereign:xxx
    parts = data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    
    if action == "refresh":
        dashboard = await get_owner_dashboard(uid)
        treasury = dashboard["treasury"]
        global_stats = dashboard["global"]
        
        text = f"""🏛️ *SOVEREIGN MONETARY CONTROL PANEL*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

👑 *{SOVEREIGN_OWNER_NAME}*

📊 Supply: *{treasury['current_supply']:,.0f}* / {treasury['max_supply']:,.0f} TRC
🏦 Treasury: *{treasury['treasury_balance']:,.0f} TRC*
📈 Reserves: *${treasury['total_reserve_value']:,.0f}* ({treasury['reserve_ratio']*100:.1f}%)
💎 Staked: *{treasury['total_staked']:,.0f} TRC* @ {treasury['staking_apy']*100:.1f}% APY
🔗 Wallets: *{global_stats['total_wallets']:,}* | TXs: *{global_stats['total_transactions']:,}*

⚡ *STATUS:* {'🔴 PAUSED' if treasury['is_paused'] else '🟢 ACTIVE'}
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💵 Emit", callback_data="sovereign:emit"),
                InlineKeyboardButton("🔥 Burn", callback_data="sovereign:burn"),
                InlineKeyboardButton("📊 APY", callback_data="sovereign:set_apy")
            ],
            [
                InlineKeyboardButton("🎁 Rewards", callback_data="sovereign:distribute"),
                InlineKeyboardButton("💸 Transfer", callback_data="sovereign:transfer"),
                InlineKeyboardButton("❄️ Freeze", callback_data="sovereign:freeze")
            ],
            [
                InlineKeyboardButton("⏸️ Pause" if not treasury['is_paused'] else "▶️ Resume", 
                                   callback_data="sovereign:pause" if not treasury['is_paused'] else "sovereign:resume"),
                InlineKeyboardButton("🔄 Refresh", callback_data="sovereign:refresh")
            ]
        ])
        
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
    
    elif action == "emit":
        ctx.user_data["sovereign_mode"] = "emit"
        await q.edit_message_text(
            "💵 *TOKEN EMISSION*\n\n"
            "Enter the amount of TRC to emit and reason:\n"
            "Format: `amount reason`\n\n"
            "Example: `1000000 Liquidity expansion Q1 2026`\n\n"
            "⚠️ This will increase total supply!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="sovereign:refresh")]
            ])
        )
    
    elif action == "burn":
        ctx.user_data["sovereign_mode"] = "burn"
        dashboard = await get_owner_dashboard(uid)
        treasury_balance = dashboard["treasury"]["treasury_balance"]
        
        await q.edit_message_text(
            f"🔥 *TOKEN BURN*\n\n"
            f"Treasury Balance: *{treasury_balance:,.0f} TRC*\n\n"
            "Enter amount and reason:\n"
            "Format: `amount reason`\n\n"
            "Example: `500000 Supply reduction for stability`\n\n"
            "⚠️ This will decrease total supply!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="sovereign:refresh")]
            ])
        )
    
    elif action == "set_apy":
        ctx.user_data["sovereign_mode"] = "set_apy"
        await q.edit_message_text(
            "📊 *SET STAKING APY*\n\n"
            "Current APY: 12%\n"
            "Range: 5% - 25%\n\n"
            "Enter new APY (number only):\n"
            "Example: `15` for 15% APY",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="sovereign:refresh")]
            ])
        )
    
    elif action == "distribute":
        result = await distribute_staking_rewards(uid)
        
        if result["success"]:
            await q.edit_message_text(
                f"✅ *REWARDS DISTRIBUTED*\n\n"
                f"💰 Total: *{result['distributed']:,.2f} TRC*\n"
                f"👥 Recipients: *{result['recipients']}*\n"
                f"📊 Daily Rate: *{result['daily_rate']*100:.4f}%*\n"
                f"📈 APY: *{result['apy']*100:.1f}%*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("« Back", callback_data="sovereign:refresh")]
                ])
            )
        else:
            await q.edit_message_text(f"❌ Error: {result.get('message', 'Unknown')}")
    
    elif action == "transfer":
        ctx.user_data["sovereign_mode"] = "transfer"
        await q.edit_message_text(
            "💸 *TREASURY TRANSFER*\n\n"
            "Transfer TRC from treasury to a user.\n\n"
            "Format: `user_id amount reason`\n"
            "Example: `123456789 10000 Partner bonus`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="sovereign:refresh")]
            ])
        )
    
    elif action == "freeze":
        ctx.user_data["sovereign_mode"] = "freeze"
        await q.edit_message_text(
            "❄️ *FREEZE WALLET*\n\n"
            "Enter user ID to freeze:\n"
            "Format: `user_id reason`\n\n"
            "Example: `123456789 Suspicious activity`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="sovereign:refresh")]
            ])
        )
    
    elif action == "unfreeze":
        ctx.user_data["sovereign_mode"] = "unfreeze"
        await q.edit_message_text(
            "🔓 *UNFREEZE WALLET*\n\n"
            "Enter user ID to unfreeze:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="sovereign:refresh")]
            ])
        )
    
    elif action in ("pause", "resume"):
        is_pause = action == "pause"
        result = await set_monetary_policy(uid, is_paused=is_pause)
        
        if result["success"]:
            status = "⏸️ PAUSED" if is_pause else "▶️ RESUMED"
            await q.edit_message_text(
                f"✅ Protocol {status}\n\n"
                f"{'⚠️ All transactions are now blocked!' if is_pause else '✅ Normal operations restored.'}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("« Back", callback_data="sovereign:refresh")]
                ])
            )


async def handle_sovereign_input(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle sovereign mode text inputs. Returns True if handled."""
    uid = update.effective_user.id
    
    if not is_sovereign_owner(uid):
        return False
    
    mode = ctx.user_data.get("sovereign_mode")
    if not mode:
        return False
    
    text = update.message.text.strip()
    
    if mode == "emit":
        try:
            parts = text.split(maxsplit=1)
            amount = float(parts[0])
            reason = parts[1] if len(parts) > 1 else "Manual emission"
            
            result = await emit_tokens(uid, amount, reason)
            
            if result["success"]:
                await update.message.reply_text(
                    f"✅ *TOKEN EMISSION SUCCESSFUL*\n\n"
                    f"💵 Amount: *{amount:,.0f} TRC*\n"
                    f"📝 Reason: {reason}\n"
                    f"📊 New Supply: *{result['new_supply']:,.0f} TRC*\n"
                    f"🔗 TX: `{result['tx_hash'][:20]}...`",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(f"❌ Error: {result['error']}")
        except Exception as e:
            await update.message.reply_text(f"❌ Invalid format: {e}")
        
        ctx.user_data.pop("sovereign_mode", None)
        return True
    
    elif mode == "burn":
        try:
            parts = text.split(maxsplit=1)
            amount = float(parts[0])
            reason = parts[1] if len(parts) > 1 else "Manual burn"
            
            result = await burn_tokens(uid, amount, reason)
            
            if result["success"]:
                await update.message.reply_text(
                    f"✅ *TOKEN BURN SUCCESSFUL*\n\n"
                    f"🔥 Amount: *{amount:,.0f} TRC*\n"
                    f"📝 Reason: {reason}\n"
                    f"📊 New Supply: *{result['new_supply']:,.0f} TRC*\n"
                    f"🔗 TX: `{result['tx_hash'][:20]}...`",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(f"❌ Error: {result['error']}")
        except Exception as e:
            await update.message.reply_text(f"❌ Invalid format: {e}")
        
        ctx.user_data.pop("sovereign_mode", None)
        return True
    
    elif mode == "set_apy":
        try:
            apy = float(text) / 100  # Convert from percent
            
            result = await set_monetary_policy(uid, staking_apy=apy)
            
            if result["success"]:
                changes = result.get("changes", {})
                apy_change = changes.get("staking_apy", {})
                await update.message.reply_text(
                    f"✅ *STAKING APY UPDATED*\n\n"
                    f"📉 Old: {apy_change.get('old', 0)*100:.1f}%\n"
                    f"📈 New: {apy_change.get('new', apy)*100:.1f}%",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(f"❌ Error: {result.get('error', 'Unknown')}")
        except Exception as e:
            await update.message.reply_text(f"❌ Invalid format: {e}")
        
        ctx.user_data.pop("sovereign_mode", None)
        return True
    
    elif mode == "transfer":
        try:
            parts = text.split(maxsplit=2)
            target_uid = int(parts[0])
            amount = float(parts[1])
            reason = parts[2] if len(parts) > 2 else "Treasury transfer"
            
            result = await transfer_from_treasury(uid, target_uid, amount, reason)
            
            if result["success"]:
                await update.message.reply_text(
                    f"✅ *TREASURY TRANSFER SUCCESSFUL*\n\n"
                    f"👤 To: User `{target_uid}`\n"
                    f"💰 Amount: *{amount:,.0f} TRC*\n"
                    f"📝 Reason: {reason}\n"
                    f"🏦 Remaining: *{result['remaining_treasury']:,.0f} TRC*",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(f"❌ Error: {result['error']}")
        except Exception as e:
            await update.message.reply_text(f"❌ Invalid format: {e}")
        
        ctx.user_data.pop("sovereign_mode", None)
        return True
    
    elif mode == "freeze":
        try:
            parts = text.split(maxsplit=1)
            target_uid = int(parts[0])
            reason = parts[1] if len(parts) > 1 else "Frozen by owner"
            
            target_wallet = await get_trc_wallet(target_uid)
            result = await freeze_wallet(uid, target_wallet.address, reason)
            
            if result["success"]:
                await update.message.reply_text(
                    f"✅ *WALLET FROZEN*\n\n"
                    f"👤 User: `{target_uid}`\n"
                    f"📍 Address: `{result['address'][:20]}...`\n"
                    f"📝 Reason: {reason}",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(f"❌ Error: {result['error']}")
        except Exception as e:
            await update.message.reply_text(f"❌ Invalid format: {e}")
        
        ctx.user_data.pop("sovereign_mode", None)
        return True
    
    elif mode == "unfreeze":
        try:
            target_uid = int(text.strip())
            target_wallet = await get_trc_wallet(target_uid)
            result = await unfreeze_wallet(uid, target_wallet.address)
            
            if result["success"]:
                await update.message.reply_text(
                    f"✅ *WALLET UNFROZEN*\n\n"
                    f"👤 User: `{target_uid}`\n"
                    f"📍 Address: `{result['address'][:20]}...`",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(f"❌ Error: {result['error']}")
        except Exception as e:
            await update.message.reply_text(f"❌ Invalid format: {e}")
        
        ctx.user_data.pop("sovereign_mode", None)
        return True
    
    return False


# =====================================================
# TRC WALLET MANAGEMENT
# =====================================================

@log_calls
@require_access
async def cmd_wallet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show user's TRC wallet."""
    uid = update.effective_user.id
    t = ctx.t
    
    # Get or create wallet
    wallet = await get_trc_wallet(uid)
    balance_info = await blockchain.get_total_balance(uid)
    
    # Get recent transactions
    transactions = await blockchain.get_transaction_history(uid, limit=5)
    
    text = t.get("wallet_header", "🪙 *Triacelo Coin (TRC) Wallet*")
    text += f"\n\n📍 *Address:*\n`{wallet.address}`"
    text += f"\n\n💰 *Available:* {balance_info['available']:.2f} TRC"
    text += f"\n🔒 *Staked:* {balance_info['staked']:.2f} TRC"
    text += f"\n🎁 *Rewards:* {balance_info['pending_rewards']:.2f} TRC"
    text += f"\n━━━━━━━━━━━━━━━"
    text += f"\n💎 *Total:* {balance_info['total']:.2f} TRC (~${balance_info['total']:.2f})"
    
    # Recent transactions
    if transactions:
        text += f"\n\n📜 *Recent Transactions:*"
        for tx in transactions[:5]:
            icon = "📥" if tx.to_address == wallet.address else "📤"
            text += f"\n{icon} {tx.tx_type.value}: {tx.amount:.2f} TRC"
    
    text += "\n\n💡 *1 TRC = 1 USDT*"
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💳 Deposit", callback_data="wallet:deposit"),
            InlineKeyboardButton("💸 Withdraw", callback_data="wallet:withdraw")
        ],
        [
            InlineKeyboardButton("📊 Stake TRC (12% APY)", callback_data="wallet:stake"),
            InlineKeyboardButton("📜 History", callback_data="wallet:history")
        ],
        [InlineKeyboardButton("🔄 Refresh", callback_data="wallet:refresh")],
    ])
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)


@with_texts
async def on_wallet_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle wallet callbacks."""
    q = update.callback_query
    await q.answer()
    
    uid = update.effective_user.id
    t = ctx.t
    data = q.data  # wallet:xxx
    
    parts = data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    
    if action == "refresh":
        # Refresh wallet display
        wallet = await get_trc_wallet(uid)
        balance_info = await blockchain.get_total_balance(uid)
        transactions = await blockchain.get_transaction_history(uid, limit=5)
        
        text = t.get("wallet_header", "🪙 *Triacelo Coin (TRC) Wallet*")
        text += f"\n\n📍 *Address:*\n`{wallet.address}`"
        text += f"\n\n💰 *Available:* {balance_info['available']:.2f} TRC"
        text += f"\n🔒 *Staked:* {balance_info['staked']:.2f} TRC"
        text += f"\n🎁 *Rewards:* {balance_info['pending_rewards']:.2f} TRC"
        text += f"\n━━━━━━━━━━━━━━━"
        text += f"\n💎 *Total:* {balance_info['total']:.2f} TRC (~${balance_info['total']:.2f})"
        
        if transactions:
            text += f"\n\n📜 *Recent Transactions:*"
            for tx in transactions[:5]:
                icon = "📥" if tx.to_address == wallet.address else "📤"
                text += f"\n{icon} {tx.tx_type.value}: {tx.amount:.2f} TRC"
        
        text += "\n\n💡 *1 TRC = 1 USDT*"
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💳 Deposit", callback_data="wallet:deposit"),
                InlineKeyboardButton("💸 Withdraw", callback_data="wallet:withdraw")
            ],
            [
                InlineKeyboardButton("📊 Stake TRC (12% APY)", callback_data="wallet:stake"),
                InlineKeyboardButton("📜 History", callback_data="wallet:history")
            ],
            [InlineKeyboardButton("🔄 Refresh", callback_data="wallet:refresh")],
        ])
        
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
    
    elif action == "deposit":
        # Show deposit options
        wallet = await get_trc_wallet(uid)
        
        text = t.get("wallet_deposit_header", "💳 *Deposit TRC*")
        text += "\n\n🪙 *Ways to get TRC:*"
        text += "\n\n1️⃣ *Buy with Crypto:*"
        text += f"\nSend USDT/USDC to our exchange and receive TRC 1:1"
        text += "\n\n2️⃣ *Earn Rewards:*"
        text += "\n• Referral bonuses"
        text += "\n• Trading achievements"
        text += "\n• Staking rewards (12% APY)"
        text += "\n\n3️⃣ *Demo Deposit (Test):*"
        text += "\nGet 100 TRC for testing (demo only)"
        text += f"\n\n📍 *Your Wallet:*\n`{wallet.address}`"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 Get 100 TRC (Demo)", callback_data="wallet:demo_deposit")],
            [InlineKeyboardButton("📊 Buy TRC (Coming Soon)", callback_data="wallet:buy_soon")],
            [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="wallet:refresh")],
        ])
        
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
    
    elif action == "demo_deposit":
        # Demo deposit - give 100 TRC for testing
        success, message = await deposit_trc(uid, 100.0, "Demo deposit")
        
        if success:
            new_balance = await get_trc_balance(uid)
            await q.edit_message_text(
                f"✅ *Demo Deposit Successful!*\n\n🪙 +100 TRC credited\n💰 New Balance: {new_balance:.2f} TRC\n\n{message}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="wallet:refresh")]
                ])
            )
        else:
            await q.edit_message_text(
                f"❌ Deposit failed: {message}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="wallet:deposit")]
                ])
            )
    
    elif action == "buy_soon":
        await q.answer("🚧 Coming soon! External TRC purchases will be available in the next update.", show_alert=True)
    
    elif action == "withdraw":
        balance = await get_trc_balance(uid)
        
        text = t.get("wallet_withdraw_header", "💸 *Withdraw TRC*")
        text += f"\n\n💰 Available: {balance:.2f} TRC"
        text += "\n\n📝 Withdrawal converts TRC to USDT 1:1"
        text += "\n• Minimum: 10 TRC"
        text += "\n• Fee: 0%"
        text += "\n• Processing: Instant"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💸 Withdraw to USDT", callback_data="wallet:withdraw_usdt")],
            [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="wallet:refresh")],
        ])
        
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
    
    elif action == "withdraw_usdt":
        await q.answer("🚧 External withdrawals coming soon! Contact support for manual processing.", show_alert=True)
    
    elif action == "stake":
        wallet = await get_trc_wallet(uid)
        balance_info = await blockchain.get_total_balance(uid)
        
        text = t.get("wallet_stake_header", "📊 *TRC Staking*")
        text += "\n\n🔥 *Earn 12% APY on your TRC!*"
        text += f"\n\n💰 Available to stake: {balance_info['available']:.2f} TRC"
        text += f"\n🔒 Currently staked: {balance_info['staked']:.2f} TRC"
        text += f"\n🎁 Pending rewards: {balance_info['pending_rewards']:.2f} TRC"
        text += "\n\n• No lock period"
        text += "\n• Instant unstaking"
        text += "\n• Daily reward distribution"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔒 Stake All", callback_data="wallet:stake_all")],
            [InlineKeyboardButton("🔓 Unstake All", callback_data="wallet:unstake_all")],
            [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="wallet:refresh")],
        ])
        
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
    
    elif action == "stake_all":
        balance = await get_trc_balance(uid)
        if balance < 1:
            await q.answer("❌ Minimum 1 TRC required for staking", show_alert=True)
            return
        
        success, tx, message = await blockchain.stake(uid, balance)
        if success:
            await q.answer(f"✅ Staked {balance:.2f} TRC successfully!", show_alert=True)
            # Refresh stake view
            await on_wallet_cb(update, ctx)
        else:
            await q.answer(f"❌ Staking failed: {message}", show_alert=True)
    
    elif action == "unstake_all":
        wallet = await get_trc_wallet(uid)
        if wallet.staked_balance < 1:
            await q.answer("❌ No staked TRC to unstake", show_alert=True)
            return
        
        success, tx, message = await blockchain.unstake(uid, wallet.staked_balance)
        if success:
            await q.answer(f"✅ Unstaked {wallet.staked_balance:.2f} TRC successfully!", show_alert=True)
            # Refresh stake view
            await on_wallet_cb(update, ctx)
        else:
            await q.answer(f"❌ Unstaking failed: {message}", show_alert=True)
    
    elif action == "history":
        transactions = await blockchain.get_transaction_history(uid, limit=20)
        wallet = await get_trc_wallet(uid)
        
        text = t.get("wallet_history_header", "📜 *Transaction History*")
        text += f"\n\n📍 Wallet: `{wallet.address[:20]}...`"
        
        if not transactions:
            text += "\n\nNo transactions yet."
        else:
            for tx in transactions:
                icon = "📥" if tx.to_address == wallet.address else "📤"
                status_icon = "✅" if tx.status.value == "confirmed" else "⏳"
                date_str = tx.timestamp.strftime("%m/%d %H:%M")
                text += f"\n\n{icon} *{tx.tx_type.value.upper()}*"
                text += f"\n   Amount: {tx.amount:.2f} TRC"
                text += f"\n   {date_str} {status_icon}"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="wallet:refresh")]
        ])
        
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)


@require_access
@with_texts
async def cmd_subscribe(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show subscription menu."""
    uid = update.effective_user.id
    t = ctx.t
    
    license_info = get_user_license(uid)
    
    header = t.get("subscribe_menu_header", "💎 *Subscription Plans*")
    info = t.get("subscribe_menu_info", "Choose your plan to unlock trading features:")
    
    # Show current license status if any
    if license_info["is_active"]:
        import datetime
        expires_dt = datetime.datetime.fromtimestamp(license_info["expires"])
        status = f"\n\n✅ Current: {license_info['license_type'].title()} (expires {expires_dt.strftime('%Y-%m-%d')})"
    else:
        status = ""
    
    await update.message.reply_text(
        f"{header}\n\n{info}{status}",
        parse_mode="Markdown",
        reply_markup=get_subscribe_menu_keyboard(t)
    )


@with_texts
async def on_subscribe_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle subscription menu callbacks."""
    q = update.callback_query
    await q.answer()
    
    uid = update.effective_user.id
    t = ctx.t
    data = q.data  # sub:xxx:yyy
    
    parts = data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    
    if action == "menu":
        # Back to main subscription menu
        await q.edit_message_text(
            f"{t.get('subscribe_menu_header', '💎 *Subscription Plans*')}\n\n{t.get('subscribe_menu_info', 'Choose your plan:')}",
            parse_mode="Markdown",
            reply_markup=get_subscribe_menu_keyboard(t)
        )
    
    elif action == "plan":
        plan = parts[2] if len(parts) > 2 else ""
        
        if plan == "premium":
            await q.edit_message_text(
                f"{t.get('premium_title', '💎 *PREMIUM PLAN*')}\n\n{t.get('premium_desc', 'Full access to all features')}",
                parse_mode="Markdown",
                reply_markup=get_premium_period_keyboard(t)
            )
        
        elif plan == "basic":
            await q.edit_message_text(
                f"{t.get('basic_title', '🥈 *BASIC PLAN*')}\n\n{t.get('basic_desc', 'Demo + limited real trading')}",
                parse_mode="Markdown",
                reply_markup=get_basic_period_keyboard(t)
            )
        
        elif plan == "trial":
            # Check if user already used trial
            license_history = get_license_history(uid)
            used_trial = any(l["license_type"] == "trial" for l in license_history)
            
            if used_trial:
                await q.edit_message_text(
                    t.get("trial_already_used", "⚠️ You have already used your free trial."),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="sub:menu")]
                    ])
                )
            else:
                await q.edit_message_text(
                    f"{t.get('trial_title', '🎁 *TRIAL PLAN*')}\n\n{t.get('trial_desc', 'Free demo access for 7 days')}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(t.get("trial_activate", "🎁 Activate Free Trial"), callback_data="sub:activate:trial")],
                        [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="sub:menu")]
                    ])
                )
    
    elif action == "activate":
        plan = parts[2] if len(parts) > 2 else ""
        if plan == "trial":
            # Check again for trial usage
            license_history = get_license_history(uid)
            used_trial = any(l["license_type"] == "trial" for l in license_history)
            
            if used_trial:
                await q.edit_message_text(
                    t.get("trial_already_used", "⚠️ You have already used your free trial."),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="sub:menu")]
                    ])
                )
            else:
                # Activate trial
                result = set_user_license(
                    user_id=uid,
                    license_type="trial",
                    period_months=1,  # Will be 7 days
                    payment_type="trial",
                    amount=0,
                    currency="FREE",
                    notes="Free trial activation"
                )
                
                if result.get("success"):
                    await q.edit_message_text(
                        t.get("trial_activated", "🎉 Trial activated! You have 7 days of full demo access."),
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="sub:menu")]
                        ])
                    )
                else:
                    await q.edit_message_text(
                        t.get("payment_failed", "❌ Payment failed: {error}").format(error=result.get("error", "Unknown")),
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="sub:menu")]
                        ])
                    )
    
    elif action == "period":
        # User selected period, show payment with TRC
        plan = parts[2] if len(parts) > 2 else ""
        period = int(parts[3]) if len(parts) > 3 else 1
        
        prices = LICENSE_PRICES.get(plan, {})
        trc_price = prices.get("trc", {}).get(period, 0)
        period_text = f"{period} month{'s' if period > 1 else ''}"
        
        # Get user's TRC balance
        user_balance = await get_trc_balance(uid)
        
        text = t.get("payment_select_method", "💳 *Payment with Triacelo Coin (TRC)*")
        text += f"\n\n📦 *Plan:* {plan.title()}\n⏰ *Period:* {period_text}"
        text += f"\n\n🪙 *Price:* {trc_price:.0f} TRC (~${trc_price:.0f})"
        text += f"\n💰 *Your Balance:* {user_balance:.2f} TRC"
        
        if user_balance >= trc_price:
            text += "\n\n✅ You have enough TRC to pay!"
        else:
            needed = trc_price - user_balance
            text += f"\n\n⚠️ You need {needed:.2f} more TRC. Deposit to continue."
        
        await q.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_payment_method_keyboard(t, plan, period)
        )
    
    elif action == "trc":
        # TRC payment flow
        plan = parts[2] if len(parts) > 2 else ""
        period = int(parts[3]) if len(parts) > 3 else 1
        prices = LICENSE_PRICES.get(plan, {})
        trc_price = prices.get("trc", {}).get(period, 0)
        period_text = f"{period} month{'s' if period > 1 else ''}"
        
        # Check TRC balance
        user_balance = await get_trc_balance(uid)
        
        if user_balance < trc_price:
            needed = trc_price - user_balance
            await q.edit_message_text(
                t.get("payment_insufficient_trc", "❌ *Insufficient TRC Balance*\n\nYou need {needed:.2f} more TRC.\n\nYour balance: {balance:.2f} TRC\nRequired: {price:.0f} TRC\n\nDeposit TRC to continue.").format(
                    needed=needed, balance=user_balance, price=trc_price
                ),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 Deposit TRC", callback_data="wallet:deposit")],
                    [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data=f"sub:period:{plan}:{period}")]
                ])
            )
            return
        
        # Process TRC payment
        description = f"{plan.title()} License ({period_text})"
        success, message = await pay_with_trc(uid, trc_price, description)
        
        if success:
            # Activate license
            result = set_user_license(
                user_id=uid,
                license_type=plan,
                period_months=period,
                payment_type="TRC",
                amount=trc_price,
                currency="TRC",
                notes=f"Paid with Triacelo Coin. {message}"
            )
            
            if result.get("success"):
                new_balance = await get_trc_balance(uid)
                await q.edit_message_text(
                    t.get("payment_success_trc", "✅ *Payment Successful!*\n\n🪙 Paid: {amount:.0f} TRC\n📦 Plan: {plan}\n⏰ Period: {period}\n\n💰 New Balance: {balance:.2f} TRC\n\nThank you for using Triacelo!").format(
                        amount=trc_price, plan=plan.title(), period=period_text, balance=new_balance
                    ),
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="sub:menu")]
                    ])
                )
            else:
                # Payment went through but license activation failed - refund
                await reward_trc(uid, trc_price, "License activation failed - refund")
                await q.edit_message_text(
                    t.get("payment_failed", "❌ Payment failed: {error}").format(error=result.get("error", "Unknown")),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="sub:menu")]
                    ])
                )
        else:
            await q.edit_message_text(
                t.get("payment_failed", "❌ Payment failed: {error}").format(error=message),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data=f"sub:period:{plan}:{period}")]
                ])
            )
    
    elif action == "verify_ton":
        # TON payments deprecated - redirect to TRC
        await q.edit_message_text(
            t.get("payment_ton_not_configured", "❌ TON payments are deprecated. Use TRC tokens."),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get("wallet_btn_deposit", "📥 Deposit"), callback_data="wallet:deposit")],
                [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="sub:menu")]
            ])
        )
    
    elif action == "my":
        # Show user's subscription status
        license_info = get_user_license(uid)
        
        if license_info["is_active"]:
            import datetime
            expires_dt = datetime.datetime.fromtimestamp(license_info["expires"])
            text = t.get("my_subscription_active", "📋 *Current Plan:* {plan}\n⏰ *Expires:* {expires}\n📅 *Days Left:* {days}").format(
                plan=license_info["license_type"].title(),
                expires=expires_dt.strftime("%Y-%m-%d"),
                days=license_info["days_left"]
            )
        else:
            text = t.get("my_subscription_none", "❌ No active subscription.\n\nUse /subscribe to purchase a plan.")
        
        # Get payment history
        payments = get_user_payments(uid, limit=5)
        if payments:
            history_lines = []
            for p in payments:
                import datetime
                dt = datetime.datetime.fromtimestamp(p["created_at"])
                history_lines.append(f"• {dt.strftime('%Y-%m-%d')}: {p['license_type'].title()} ({p['payment_type']})")
            text += f"\n\n{t.get('my_subscription_history', '📜 *Payment History:*')}\n" + "\n".join(history_lines)
        
        await q.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="sub:menu")]
            ])
        )
    
    elif action == "promo":
        # Ask user to enter promo code
        ctx.user_data["mode"] = "enter_promo"
        await q.edit_message_text(
            t.get("promo_enter", "🎟 Enter your promo code:"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="sub:menu")]
            ])
        )


async def verify_ton_payment(wallet_address: str, memo: str, expected_amount: float) -> bool:
    """
    DEPRECATED: TON payments no longer supported.
    All payments now use TRC tokens via the blockchain module.
    """
    logger.warning("verify_ton_payment is deprecated. Use TRC payments instead.")
    return False


async def notify_admin_payment(bot, uid: int, username: str, plan: str, period: int, 
                                amount: float, currency: str, status: str, charge_id: str = None):
    """Send payment notification to admin with action buttons."""
    import datetime
    
    user_info = f"👤 User: {uid}"
    if username:
        user_info += f" (@{username})"
    
    period_text = f"{period} month{'s' if period > 1 else ''}"
    
    text = f"💳 *Payment {status}*\n\n"
    text += f"{user_info}\n"
    text += f"📦 Plan: *{plan.title()}*\n"
    text += f"⏰ Period: *{period_text}*\n"
    text += f"💰 Amount: *{amount} {currency}*\n"
    text += f"🕐 Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    if charge_id:
        text += f"\n🧾 Charge ID: `{charge_id}`"
    
    # Admin action buttons
    buttons = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"adm_pay:confirm:{uid}:{plan}:{period}"),
            InlineKeyboardButton("🔄 Change Plan", callback_data=f"adm_pay:change:{uid}")
        ],
        [
            InlineKeyboardButton("⏳ Extend", callback_data=f"adm_pay:extend:{uid}"),
            InlineKeyboardButton("🚫 Revoke", callback_data=f"adm_pay:revoke:{uid}")
        ],
        [
            InlineKeyboardButton("🚫 Ban User", callback_data=f"adm_pay:ban:{uid}"),
            InlineKeyboardButton("🗑 Delete User", callback_data=f"adm_pay:delete:{uid}")
        ],
        [InlineKeyboardButton("👤 User Card", callback_data=f"admin:user_card:{uid}")]
    ]
    
    try:
        await bot.send_message(
            ADMIN_ID,
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        logger.error(f"Failed to notify admin about payment: {e}")


@with_texts
async def on_admin_payment_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle admin payment action callbacks."""
    q = update.callback_query
    await q.answer()
    
    admin_uid = update.effective_user.id
    if admin_uid != ADMIN_ID:
        return
    
    t = ctx.t
    data = q.data  # adm_pay:action:uid:...
    parts = data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    target_uid = int(parts[2]) if len(parts) > 2 else 0
    
    if action == "confirm":
        # Already confirmed via automatic processing
        plan = parts[3] if len(parts) > 3 else "premium"
        period = int(parts[4]) if len(parts) > 4 else 1
        await q.edit_message_text(
            f"✅ Payment for user {target_uid} already processed.\n\nPlan: {plan.title()}\nPeriod: {period} months"
        )
    
    elif action == "change":
        # Show plan selection for this user
        buttons = [
            [InlineKeyboardButton("💎 Premium 1m", callback_data=f"adm_pay:grant:{target_uid}:premium:1")],
            [InlineKeyboardButton("💎 Premium 3m", callback_data=f"adm_pay:grant:{target_uid}:premium:3")],
            [InlineKeyboardButton("💎 Premium 6m", callback_data=f"adm_pay:grant:{target_uid}:premium:6")],
            [InlineKeyboardButton("💎 Premium 12m", callback_data=f"adm_pay:grant:{target_uid}:premium:12")],
            [InlineKeyboardButton("🥈 Basic 1m", callback_data=f"adm_pay:grant:{target_uid}:basic:1")],
            [InlineKeyboardButton("🎁 Trial", callback_data=f"adm_pay:grant:{target_uid}:trial:1")],
            [InlineKeyboardButton("⬅️ Cancel", callback_data=f"admin:user_card:{target_uid}")]
        ]
        await q.edit_message_text(
            f"🔄 *Change Plan for User {target_uid}*\n\nSelect new plan:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    elif action == "grant":
        plan = parts[3] if len(parts) > 3 else "premium"
        period = int(parts[4]) if len(parts) > 4 else 1
        result = set_user_license(
            user_id=target_uid,
            license_type=plan,
            period_months=period,
            payment_type="admin_grant",
            amount=0,
            currency="FREE",
            admin_id=admin_uid,
            notes=f"Admin granted after payment review"
        )
        if result.get("success"):
            import datetime
            expires_dt = datetime.datetime.fromtimestamp(result["expires"])
            await q.edit_message_text(
                f"✅ License granted to user {target_uid}!\n\nPlan: {plan.title()}\nExpires: {expires_dt.strftime('%Y-%m-%d')}"
            )
            # Notify user
            try:
                await ctx.bot.send_message(
                    target_uid,
                    f"🎉 Your {plan.title()} license has been activated!\n\nExpires: {expires_dt.strftime('%Y-%m-%d')}"
                )
            except:
                pass
        else:
            await q.edit_message_text(f"❌ Failed to grant license: {result.get('error')}")
    
    elif action == "extend":
        buttons = [
            [InlineKeyboardButton("7 days", callback_data=f"adm_pay:do_extend:{target_uid}:7")],
            [InlineKeyboardButton("14 days", callback_data=f"adm_pay:do_extend:{target_uid}:14")],
            [InlineKeyboardButton("30 days", callback_data=f"adm_pay:do_extend:{target_uid}:30")],
            [InlineKeyboardButton("90 days", callback_data=f"adm_pay:do_extend:{target_uid}:90")],
            [InlineKeyboardButton("⬅️ Cancel", callback_data=f"admin:user_card:{target_uid}")]
        ]
        await q.edit_message_text(
            f"⏳ *Extend License for User {target_uid}*\n\nSelect days to add:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    elif action == "do_extend":
        days = int(parts[3]) if len(parts) > 3 else 30
        result = extend_license(target_uid, days, admin_id=admin_uid)
        if result.get("success"):
            await q.edit_message_text(f"✅ License extended by {days} days for user {target_uid}!")
        else:
            await q.edit_message_text(f"❌ Failed to extend: {result.get('error')}")
    
    elif action == "revoke":
        result = revoke_license(target_uid, admin_id=admin_uid)
        if result.get("success"):
            await q.edit_message_text(f"✅ License revoked for user {target_uid}!")
        else:
            await q.edit_message_text(f"❌ Failed to revoke: {result.get('error')}")
    
    elif action == "ban":
        set_user_field(target_uid, "is_banned", 1)
        await q.edit_message_text(f"🚫 User {target_uid} has been banned!")
    
    elif action == "delete":
        buttons = [
            [InlineKeyboardButton("✅ Yes, Delete", callback_data=f"adm_pay:do_delete:{target_uid}")],
            [InlineKeyboardButton("❌ Cancel", callback_data=f"admin:user_card:{target_uid}")]
        ]
        await q.edit_message_text(
            f"⚠️ *Confirm deletion of user {target_uid}*\n\nThis action cannot be undone!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    elif action == "do_delete":
        try:
            delete_user(target_uid)
            await q.edit_message_text(f"🗑 User {target_uid} has been deleted!")
        except Exception as e:
            await q.edit_message_text(f"❌ Failed to delete user: {e}")


@with_texts
async def on_pre_checkout_query(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle pre-checkout query for Telegram Stars payments."""
    query = update.pre_checkout_query
    # Always approve - Telegram handles the actual payment
    await query.answer(ok=True)


@with_texts
async def on_successful_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle successful Telegram Stars payment."""
    uid = update.effective_user.id
    t = ctx.t
    username = update.effective_user.username or ""
    
    payment = update.message.successful_payment
    payload = payment.invoice_payload  # "license:premium:1"
    charge_id = payment.telegram_payment_charge_id
    
    parts = payload.split(":")
    if parts[0] == "license" and len(parts) >= 3:
        plan = parts[1]
        period = int(parts[2])
        
        # Grant license
        result = set_user_license(
            user_id=uid,
            license_type=plan,
            period_months=period,
            payment_type="stars",
            amount=payment.total_amount,
            currency="XTR",
            telegram_charge_id=charge_id,
        )
        
        if result.get("success"):
            import datetime
            expires_dt = datetime.datetime.fromtimestamp(result["expires"])
            await update.message.reply_text(
                t.get("payment_success", "🎉 Payment successful!\n\n{plan} activated until {expires}.").format(
                    plan=plan.title(),
                    expires=expires_dt.strftime("%Y-%m-%d")
                )
            )
            # Notify admin about successful payment
            await notify_admin_payment(
                ctx.bot, uid, username, plan, period,
                payment.total_amount, "⭐ Stars", "✅ SUCCESSFUL", charge_id
            )
        else:
            await update.message.reply_text(
                t.get("payment_failed", "❌ Payment failed: {error}").format(error=result.get("error", "Unknown"))
            )
            # Notify admin about failed payment
            await notify_admin_payment(
                ctx.bot, uid, username, plan, period,
                payment.total_amount, "⭐ Stars", "❌ FAILED", charge_id
            )


# =====================================================
# ADMIN LICENSE MANAGEMENT
# =====================================================

def get_admin_license_keyboard(t: dict) -> InlineKeyboardMarkup:
    """Admin license management keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t.get("admin_users_management", "👥 Users"), callback_data="admin:users_menu")],
        [InlineKeyboardButton(t.get("admin_btn_grant_license", "🎁 Grant License"), callback_data="adm_lic:grant")],
        [InlineKeyboardButton(t.get("admin_btn_view_licenses", "📋 View Licenses"), callback_data="adm_lic:list")],
        [InlineKeyboardButton(t.get("admin_btn_create_promo", "🎟 Create Promo"), callback_data="adm_lic:promo_create")],
        [InlineKeyboardButton(t.get("admin_btn_view_promos", "📋 View Promos"), callback_data="adm_lic:promo_list")],
        [InlineKeyboardButton(t.get("admin_btn_expiring_soon", "⚠️ Expiring Soon"), callback_data="adm_lic:expiring")],
        [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="admin:menu")],
    ])


@with_texts
async def on_admin_license_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle admin license management callbacks."""
    q = update.callback_query
    await q.answer()
    
    uid = update.effective_user.id
    if uid != ADMIN_ID:
        return
    
    t = ctx.t
    data = q.data  # adm_lic:xxx
    parts = data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    
    if action == "menu":
        await q.edit_message_text(
            t.get("admin_license_menu", "🔑 *License Management*"),
            parse_mode="Markdown",
            reply_markup=get_admin_license_keyboard(t)
        )
    
    elif action == "grant":
        # Show license type selection
        await q.edit_message_text(
            t.get("admin_grant_select_type", "Select license type:"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Premium", callback_data="adm_lic:grant_type:premium")],
                [InlineKeyboardButton("🥈 Basic", callback_data="adm_lic:grant_type:basic")],
                [InlineKeyboardButton("🎁 Trial", callback_data="adm_lic:grant_type:trial")],
                [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="adm_lic:menu")],
            ])
        )
    
    elif action == "grant_type":
        plan = parts[2] if len(parts) > 2 else "premium"
        ctx.user_data["admin_grant_type"] = plan
        
        # Show period selection
        if plan == "premium":
            keyboard = [
                [InlineKeyboardButton("1 Month", callback_data="adm_lic:grant_period:1")],
                [InlineKeyboardButton("3 Months", callback_data="adm_lic:grant_period:3")],
                [InlineKeyboardButton("6 Months", callback_data="adm_lic:grant_period:6")],
                [InlineKeyboardButton("12 Months", callback_data="adm_lic:grant_period:12")],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("1 Month", callback_data="adm_lic:grant_period:1")],
            ]
        keyboard.append([InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="adm_lic:grant")])
        
        await q.edit_message_text(
            t.get("admin_grant_select_period", "Select period:"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif action == "grant_period":
        period = int(parts[2]) if len(parts) > 2 else 1
        ctx.user_data["admin_grant_period"] = period
        ctx.user_data["mode"] = "admin_grant_user"
        
        await q.edit_message_text(
            t.get("admin_grant_enter_user", "Enter user ID:"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="adm_lic:menu")]
            ])
        )
    
    elif action == "list":
        # Show all active licenses
        licenses = get_all_active_licenses()
        
        if not licenses:
            text = "No active licenses found."
        else:
            lines = []
            for lic in licenses[:20]:  # Limit to 20
                lines.append(f"• User {lic['user_id']}: {lic['license_type'].title()} ({lic['days_left']}d left)")
            text = "📋 *Active Licenses:*\n\n" + "\n".join(lines)
        
        await q.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="adm_lic:menu")]
            ])
        )
    
    elif action == "expiring":
        # Show licenses expiring in 3 days
        expiring = get_expiring_licenses(days=3)
        
        if not expiring:
            text = "No licenses expiring soon."
        else:
            lines = []
            for lic in expiring:
                lines.append(f"• User {lic['user_id']}: {lic['license_type'].title()} ({lic['days_left']}d left)")
            text = "⚠️ *Expiring Soon:*\n\n" + "\n".join(lines)
        
        await q.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="adm_lic:menu")]
            ])
        )
    
    elif action == "promo_create":
        ctx.user_data["mode"] = "admin_promo_create"
        await q.edit_message_text(
            "Enter promo code details:\n`CODE:TYPE:DAYS:MAX_USES`\n\nExample: `LAUNCH50:premium:30:100`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="adm_lic:menu")]
            ])
        )
    
    elif action == "promo_list":
        promos = get_promo_codes(active_only=False)
        
        if not promos:
            text = "No promo codes found."
        else:
            lines = []
            for p in promos[:15]:
                status = "✅" if p["is_active"] else "❌"
                lines.append(f"{status} `{p['code']}`: {p['license_type']} {p['period_days']}d ({p['current_uses']}/{p['max_uses'] or '∞'})")
            text = "🎟 *Promo Codes:*\n\n" + "\n".join(lines)
        
        await q.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t.get("btn_back", "⬅️ Back"), callback_data="adm_lic:menu")]
            ])
        )


# ========================
# HyperLiquid DEX Commands
# ========================

# Global dict to track users waiting for private key input
_hl_awaiting_key = {}
_awaiting_hl_param = {}  # {uid: {strategy, param}}

# HyperLiquid requires premium license
HYPERLIQUID_LICENSE_TYPES = ["premium", "vip", "enterprise"]


def require_premium_for_hl(func):
    """Decorator that requires premium license for HyperLiquid features"""
    @wraps(func)
    @with_texts
    async def _wrap(update, ctx, *args, **kw):
        uid = getattr(getattr(update, "effective_user", None), "id", None)
        if uid is None:
            return await func(update, ctx, *args, **kw)

        t = ctx.t

        # Admin always has access
        if uid == ADMIN_ID:
            return await func(update, ctx, *args, **kw)

        license_info = get_user_license(uid)
        
        if not license_info["is_active"] or license_info["license_type"] not in HYPERLIQUID_LICENSE_TYPES:
            msg = t.get(
                "hl_premium_required", 
                "🔐 <b>Premium Required</b>\n\n"
                "HyperLiquid DEX trading is available only for Premium users.\n\n"
                "✨ <b>Benefits of Premium:</b>\n"
                "• Trade on HyperLiquid DEX\n"
                "• Trade on both exchanges simultaneously\n"
                "• Advanced DCA & Pyramid strategies\n"
                "• Priority support\n\n"
                "Use /subscribe to upgrade your account."
            )
            try:
                if update.callback_query:
                    await update.callback_query.answer("🔐 Premium required for HyperLiquid", show_alert=True)
                    await update.callback_query.edit_message_text(msg, parse_mode="HTML")
                else:
                    await ctx.bot.send_message(uid, msg, parse_mode="HTML")
            except:
                pass
            return
        
        return await func(update, ctx, *args, **kw)
    return _wrap


@require_premium_for_hl
@with_texts
@log_calls
async def cmd_hyperliquid(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Main HyperLiquid menu"""
    uid = update.effective_user.id
    t = ctx.t
    
    hl_creds = get_hl_credentials(uid)
    is_configured = bool(hl_creds.get("hl_private_key"))
    is_enabled = hl_creds.get("hl_enabled", False)
    exchange = get_exchange_type(uid)
    network = "Testnet" if hl_creds.get("hl_testnet") else "Mainnet"
    
    if is_configured:
        addr = hl_creds.get("hl_address", "")[:10] + "..." if hl_creds.get("hl_address") else "N/A"
        status_text = f"""
🔗 *HyperLiquid DEX*

📊 *Status:* {'✅ Connected' if is_enabled else '⚠️ Disabled'}
🌐 *Network:* {network}
👛 *Wallet:* `{addr}`
🔄 *Active Exchange:* {exchange.upper()}

Select an action:
"""
        buttons = [
            [InlineKeyboardButton("💰 Balance", callback_data="hl:balance"),
             InlineKeyboardButton("📈 Positions", callback_data="hl:positions")],
            [InlineKeyboardButton("🔄 Switch to HL" if exchange == "bybit" else "🔄 Switch to Bybit", 
                                callback_data="hl:switch")],
            [InlineKeyboardButton("🌐 Testnet" if not hl_creds.get("hl_testnet") else "🌐 Mainnet",
                                callback_data="hl:network")],
            [InlineKeyboardButton("🔑 Update Key", callback_data="hl:setkey"),
             InlineKeyboardButton("❌ Disconnect", callback_data="hl:disconnect")],
        ]
    else:
        status_text = """
🔗 *HyperLiquid DEX*

Connect your HyperLiquid account to trade on DEX!

⚡ *Benefits:*
• True decentralized trading
• No KYC required
• Lower fees
• Self-custody

To connect, you need your ETH private key.
⚠️ *IMPORTANT:* Use a dedicated trading wallet, NOT your main wallet!

Select network to start:
"""
        buttons = [
            [InlineKeyboardButton("🌐 Mainnet", callback_data="hl:mainnet"),
             InlineKeyboardButton("🧪 Testnet", callback_data="hl:testnet")],
        ]
    
    await update.message.reply_text(
        status_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@require_premium_for_hl
@with_texts
@log_calls
async def cmd_hl_setkey(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Command to set HyperLiquid private key"""
    uid = update.effective_user.id
    _hl_awaiting_key[uid] = {"waiting": True, "testnet": False}
    
    await update.message.reply_text(
        "🔑 *Set HyperLiquid Private Key*\n\n"
        "Please send your ETH private key (with or without 0x prefix).\n\n"
        "⚠️ *Security Tips:*\n"
        "• Use a dedicated trading wallet\n"
        "• Never share your key with anyone\n"
        "• The key will be stored encrypted\n\n"
        "Send /cancel to abort.",
        parse_mode="Markdown"
    )


@require_premium_for_hl
@with_texts
@log_calls
async def cmd_hl_balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show HyperLiquid balance"""
    uid = update.effective_user.id
    t = ctx.t
    
    hl_creds = get_hl_credentials(uid)
    if not hl_creds.get("hl_private_key"):
        await update.message.reply_text(
            "❌ HyperLiquid not configured. Use /hl to set up.",
            parse_mode="Markdown"
        )
        return
    
    try:
        adapter = HLAdapter(
            private_key=hl_creds["hl_private_key"],
            testnet=hl_creds.get("hl_testnet", False),
            vault_address=hl_creds.get("hl_vault_address")
        )
        
        result = await adapter.get_balance()
        
        if result.get("success"):
            data = result.get("data", {})
            equity = float(data.get("equity", 0))
            available = float(data.get("available", 0))
            margin_used = float(data.get("margin_used", 0))
            total_notional = float(data.get("total_notional", 0))
            unrealized_pnl = float(data.get("unrealized_pnl", 0))
            position_value = float(data.get("position_value", 0))
            num_positions = int(data.get("num_positions", 0))
            currency = data.get("currency", "USDC")
            
            pnl_emoji = "🟢" if unrealized_pnl >= 0 else "🔴"
            network = "🧪 Testnet" if hl_creds.get("hl_testnet") else "🌐 Mainnet"
            
            # Calculate margin level if margin used > 0
            margin_level = ""
            if margin_used > 0:
                level_pct = (equity / margin_used) * 100
                margin_level = f"\n📐 *Margin Level:* {level_pct:.1f}%"
            
            text = f"""
💰 *HyperLiquid Balance* {network}

💎 *Account Equity:* ${equity:,.2f} {currency}
✅ *Available for Trading:* ${available:,.2f} {currency}
📊 *Margin Used:* ${margin_used:,.2f} {currency}{margin_level}

📦 *Positions:*
  • Active: {num_positions} positions
  • Notional Value: ${total_notional:,.2f}
  • Position Value: ${position_value:,.2f}

{pnl_emoji} *Unrealized PnL:* ${unrealized_pnl:,.2f} {currency}
"""
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            await update.message.reply_text(
                t.get('error_fetch_balance', '❌ Error fetching balance: {error}').format(error=result.get('error', 'Unknown error')),
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"HL balance error: {e}")
        await update.message.reply_text(t.get('error_occurred', '❌ Error: {error}').format(error=str(e)), parse_mode="Markdown")


@require_premium_for_hl
@with_texts
@log_calls
async def cmd_hl_positions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show HyperLiquid positions"""
    uid = update.effective_user.id
    t = ctx.t
    
    hl_creds = get_hl_credentials(uid)
    if not hl_creds.get("hl_private_key"):
        await update.message.reply_text(
            "❌ HyperLiquid not configured. Use /hl to set up.",
            parse_mode="Markdown"
        )
        return
    
    try:
        adapter = HLAdapter(
            private_key=hl_creds["hl_private_key"],
            testnet=hl_creds.get("hl_testnet", False),
            vault_address=hl_creds.get("hl_vault_address")
        )
        
        result = await adapter.fetch_positions()
        
        if result.get("success"):
            positions = result.get("data", [])
            if not positions:
                await update.message.reply_text(t.get("hl_no_positions", "📭 No open positions on HyperLiquid."))
                return
            
            network = "🧪 Testnet" if hl_creds.get("hl_testnet") else "🌐 Mainnet"
            lines = [f"📈 *HyperLiquid Positions* {network}\n"]
            
            for pos in positions[:10]:
                symbol = pos.get("symbol", "?")
                side = pos.get("side", "?")
                size = float(pos.get("size", 0))
                entry = float(pos.get("entry_price", 0))
                pnl = float(pos.get("unrealized_pnl", 0))
                leverage = pos.get("leverage", "?")
                
                side_emoji = "�� LONG" if side == "Buy" else "🔴 SHORT"
                pnl_emoji = "+" if pnl >= 0 else ""
                
                lines.append(
                    f"{side_emoji} *{symbol}* {leverage}x\n"
                    f"   Size: {size} | Entry: ${entry:,.4f}\n"
                    f"   PnL: {pnl_emoji}${pnl:,.2f}\n"
                )
            
            await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
        else:
            await update.message.reply_text(
                t.get('error_generic', 'Error: {msg}').format(msg=f"Failed to fetch positions: {result.get('error', 'Unknown error')}"),
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"HL positions error: {e}")
        await update.message.reply_text(t.get('error_occurred', '❌ Error: {error}').format(error=str(e)), parse_mode="Markdown")


@require_premium_for_hl
@with_texts  
@log_calls
async def cmd_hl_switch(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Switch active exchange"""
    uid = update.effective_user.id
    
    current = get_exchange_type(uid)
    new_exchange = "hyperliquid" if current == "bybit" else "bybit"
    
    # Check if HL is configured before switching to it
    if new_exchange == "hyperliquid":
        hl_creds = get_hl_credentials(uid)
        if not hl_creds.get("hl_private_key"):
            await update.message.reply_text(
                "❌ Cannot switch to HyperLiquid - not configured.\n"
                "Use /hl to set up first.",
                parse_mode="Markdown"
            )
            return
    
    set_exchange_type(uid, new_exchange)
    
    await update.message.reply_text(
        f"✅ Switched to *{new_exchange.upper()}*\n\n"
        f"All new trades will execute on {new_exchange.upper()}.",
        parse_mode="Markdown"
    )


@require_premium_for_hl
@with_texts
@log_calls
async def cmd_hl_orders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show HyperLiquid open orders"""
    uid = update.effective_user.id
    t = ctx.t
    
    hl_creds = get_hl_credentials(uid)
    if not hl_creds.get("hl_private_key"):
        await update.message.reply_text(
            "❌ HyperLiquid not configured. Use 🔑 HL API to set up.",
            parse_mode="Markdown"
        )
        return
    
    try:
        adapter = HLAdapter(
            private_key=hl_creds["hl_private_key"],
            testnet=hl_creds.get("hl_testnet", False),
            vault_address=hl_creds.get("hl_vault_address")
        )
        
        result = await adapter.fetch_open_orders()
        
        if result.get("success"):
            orders = result.get("data", [])
            if not orders:
                await update.message.reply_text(t.get("hl_no_orders", "📭 No open orders on HyperLiquid."))
                return
            
            network = "🧪 Testnet" if hl_creds.get("hl_testnet") else "🌐 Mainnet"
            lines = [f"📈 *HyperLiquid Open Orders* {network}\n"]
            
            for order in orders[:10]:
                symbol = order.get("symbol", "?")
                side = order.get("side", "?")
                size = float(order.get("size", 0))
                price = float(order.get("price", 0))
                order_type = order.get("order_type", "?")
                
                side_emoji = "🟢 BUY" if side == "Buy" else "🔴 SELL"
                
                lines.append(
                    f"{side_emoji} *{symbol}*\n"
                    f"   {order_type} | Size: {size} @ ${price:,.4f}\n"
                )
            
            await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
        else:
            await update.message.reply_text(
                t.get('error_fetch_orders', '❌ Error fetching orders: {error}').format(error=result.get('error', 'Unknown error')),
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"HL orders error: {e}")
        await update.message.reply_text(t.get('error_occurred', '❌ Error: {error}').format(error=str(e)), parse_mode="Markdown")


@require_premium_for_hl
@with_texts
@log_calls
async def cmd_hl_trade(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show HyperLiquid trade menu"""
    uid = update.effective_user.id
    
    hl_creds = get_hl_credentials(uid)
    if not hl_creds.get("hl_private_key"):
        await update.message.reply_text(
            "❌ HyperLiquid not configured. Use 🔑 HL API to set up.",
            parse_mode="Markdown"
        )
        return
    
    network = "🧪 Testnet" if hl_creds.get("hl_testnet") else "🌐 Mainnet"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 Buy BTC", callback_data="hl_trade:buy_BTC"),
         InlineKeyboardButton("🔴 Sell BTC", callback_data="hl_trade:sell_BTC")],
        [InlineKeyboardButton("🟢 Buy ETH", callback_data="hl_trade:buy_ETH"),
         InlineKeyboardButton("🔴 Sell ETH", callback_data="hl_trade:sell_ETH")],
        [InlineKeyboardButton("📝 Custom Trade", callback_data="hl_trade:custom")],
        [InlineKeyboardButton("❌ Close", callback_data="hl_trade:close")],
    ])
    
    await update.message.reply_text(
        f"🎯 *HyperLiquid Trade* {network}\n\n"
        "Select a quick trade or custom trade:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


@require_premium_for_hl
@with_texts
@log_calls
async def cmd_hl_close_all(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Close all HyperLiquid positions"""
    uid = update.effective_user.id
    
    hl_creds = get_hl_credentials(uid)
    if not hl_creds.get("hl_private_key"):
        await update.message.reply_text(
            "❌ HyperLiquid not configured. Use 🔑 HL API to set up.",
            parse_mode="Markdown"
        )
        return
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Yes, Close All", callback_data="hl_close:confirm")],
        [InlineKeyboardButton("❌ Cancel", callback_data="hl_close:cancel")],
    ])
    
    await update.message.reply_text(
        "⚠️ *Close All Positions?*\n\n"
        "This will market close ALL your open positions on HyperLiquid.\n\n"
        "Are you sure?",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


@require_premium_for_hl
@with_texts
@log_calls
async def cmd_hl_history(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show HyperLiquid trade history"""
    uid = update.effective_user.id
    t = ctx.t
    
    hl_creds = get_hl_credentials(uid)
    if not hl_creds.get("hl_private_key"):
        await update.message.reply_text(
            "❌ HyperLiquid not configured. Use 🔑 HL API to set up.",
            parse_mode="Markdown"
        )
        return
    
    try:
        adapter = HLAdapter(
            private_key=hl_creds["hl_private_key"],
            testnet=hl_creds.get("hl_testnet", False),
            vault_address=hl_creds.get("hl_vault_address")
        )
        
        result = await adapter.fetch_trade_history(limit=10)
        
        if result.get("success"):
            trades = result.get("data", [])
            if not trades:
                await update.message.reply_text(t.get("hl_no_history", "📭 No trade history on HyperLiquid."))
                return
            
            network = "🧪 Testnet" if hl_creds.get("hl_testnet") else "🌐 Mainnet"
            lines = [f"📋 *HyperLiquid Trade History* {network}\n"]
            
            for trade in trades[:10]:
                symbol = trade.get("symbol", "?")
                side = trade.get("side", "?")
                size = float(trade.get("size", 0))
                price = float(trade.get("price", 0))
                pnl = float(trade.get("pnl", 0))
                
                side_emoji = "🟢" if side == "Buy" else "🔴"
                pnl_emoji = "+" if pnl >= 0 else ""
                
                lines.append(
                    f"{side_emoji} *{symbol}* | {size} @ ${price:,.4f}\n"
                    f"   PnL: {pnl_emoji}${pnl:,.2f}\n"
                )
            
            await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
        else:
            await update.message.reply_text(
                t.get('error_generic', 'Error: {msg}').format(msg=f"Failed to fetch history: {result.get('error', 'Unknown error')}"),
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"HL history error: {e}")
        await update.message.reply_text(t.get('error_occurred', '❌ Error: {error}').format(error=str(e)), parse_mode="Markdown")


@require_premium_for_hl
@with_texts
@log_calls  
async def cmd_hl_clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Clear HyperLiquid credentials"""
    uid = update.effective_user.id
    
    clear_hl_credentials(uid)
    set_exchange_type(uid, "bybit")
    
    await update.message.reply_text(
        "✅ HyperLiquid credentials cleared.\n"
        "Switched back to Bybit.",
        parse_mode="Markdown"
    )


@with_texts
@log_calls
async def cmd_hl_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show HyperLiquid API settings menu."""
    uid = update.effective_user.id
    t = ctx.t
    
    hl_creds = get_hl_credentials(uid)
    
    # Check separate testnet and mainnet keys
    has_testnet_key = bool(hl_creds.get("hl_testnet_private_key"))
    has_mainnet_key = bool(hl_creds.get("hl_mainnet_private_key"))
    testnet_wallet = hl_creds.get("hl_testnet_wallet_address", "")
    mainnet_wallet = hl_creds.get("hl_mainnet_wallet_address", "")
    
    # Fallback to legacy key
    if not has_testnet_key and not has_mainnet_key:
        legacy_key = hl_creds.get("hl_private_key")
        legacy_wallet = hl_creds.get("hl_wallet_address", "")
        if legacy_key:
            if hl_creds.get("hl_testnet"):
                has_testnet_key = True
                testnet_wallet = legacy_wallet
            else:
                has_mainnet_key = True
                mainnet_wallet = legacy_wallet
    
    # Build status message
    msg = "🔷 <b>HyperLiquid API Settings</b>\n\n"
    
    # Show testnet status
    if has_testnet_key:
        wallet_short = f"{testnet_wallet[:8]}...{testnet_wallet[-6:]}" if len(testnet_wallet) > 14 else testnet_wallet
        msg += f"🧪 <b>Testnet:</b> ✅ Configured\n"
        msg += f"   Wallet: <code>{wallet_short}</code>\n\n"
    else:
        msg += f"🧪 <b>Testnet:</b> ❌ Not configured\n\n"
    
    # Show mainnet status
    if has_mainnet_key:
        wallet_short = f"{mainnet_wallet[:8]}...{mainnet_wallet[-6:]}" if len(mainnet_wallet) > 14 else mainnet_wallet
        msg += f"🌐 <b>Mainnet:</b> ✅ Configured\n"
        msg += f"   Wallet: <code>{wallet_short}</code>\n\n"
    else:
        msg += f"🌐 <b>Mainnet:</b> ❌ Not configured\n\n"
    
    if has_testnet_key or has_mainnet_key:
        msg += "✅ <b>Status:</b> Ready to trade"
    else:
        msg += "❌ <b>Status:</b> Setup required\n\n"
        msg += "Choose network to configure:"
    
    # Build keyboard
    keyboard = []
    
    # Always show setup buttons for unconfigured networks
    setup_row = []
    if not has_mainnet_key:
        setup_row.append(InlineKeyboardButton("🌐 Setup Mainnet", callback_data="hl_api:setup_mainnet"))
    if not has_testnet_key:
        setup_row.append(InlineKeyboardButton("🧪 Setup Testnet", callback_data="hl_api:setup_testnet"))
    if setup_row:
        keyboard.append(setup_row)
    
    # Show management buttons if any key is configured
    if has_testnet_key or has_mainnet_key:
        keyboard.append([
            InlineKeyboardButton("🧪 Test Connection", callback_data="hl_api:test")
        ])
        
        # Clear buttons for each configured network
        clear_row = []
        if has_testnet_key:
            clear_row.append(InlineKeyboardButton("🗑 Clear Testnet", callback_data="hl_api:clear_testnet"))
        if has_mainnet_key:
            clear_row.append(InlineKeyboardButton("🗑 Clear Mainnet", callback_data="hl_api:clear_mainnet"))
        if clear_row:
            keyboard.append(clear_row)
    
    keyboard.append([
        InlineKeyboardButton(t.get("button_back", "🔙 Back"), callback_data="hl_api:back")
    ])
    
    await update.message.reply_text(
        msg,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@with_texts
@log_calls
async def cmd_exchange_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show current exchange status with quick mode switch"""
    uid = update.effective_user.id
    t = ctx.t
    
    status = get_exchange_status(uid)
    active = status.get("active_exchange", "bybit")
    
    bybit_info = status.get("bybit", {})
    hl_info = status.get("hyperliquid", {})
    
    keyboard = []
    
    if active == "hyperliquid":
        # ═══════════════════════════════════════════════════════════════
        # ██  HYPERLIQUID STATUS  ██
        # ═══════════════════════════════════════════════════════════════
        is_testnet = hl_info.get("testnet", False)
        wallet = hl_info.get("wallet", "")
        wallet_short = f"{wallet[:8]}...{wallet[-6:]}" if len(wallet) > 20 else wallet
        
        text = "🔷 *HyperLiquid*\n\n"
        
        if hl_info.get("configured"):
            text += f"🌐 Network: {'🧪 Testnet' if is_testnet else '💰 Mainnet'}\n"
            text += f"📍 Wallet: `{wallet_short}`\n"
            if hl_info.get("vault"):
                text += f"🏦 Vault: Configured\n"
            
            # Quick network switch buttons
            keyboard.append([
                InlineKeyboardButton("🧪 Testnet" + (" ✓" if is_testnet else ""), callback_data="hl:testnet"),
                InlineKeyboardButton("💰 Mainnet" + ("" if is_testnet else " ✓"), callback_data="hl:mainnet")
            ])
        else:
            text += "❌ Not configured\n\n_Press 🔑 API Keys to set up_"
        
        # Switch to Bybit
        if bybit_info.get("configured"):
            keyboard.append([InlineKeyboardButton("🔄 Switch to 🟠 Bybit", callback_data="exchange:set_bybit")])
        
    else:
        # ═══════════════════════════════════════════════════════════════
        # ██  BYBIT STATUS  ██
        # ═══════════════════════════════════════════════════════════════
        creds = get_all_user_credentials(uid) or {}
        trading_mode = creds.get("trading_mode", "demo")
        
        text = "🟠 *Bybit*\n\n"
        
        if bybit_info.get("configured"):
            has_demo = bybit_info.get("demo", False)
            has_real = bybit_info.get("real", False)
            
            # Show current mode
            mode_text = "🎮 Demo" if trading_mode == "demo" else ("💵 Real" if trading_mode == "real" else "🔀 Both")
            text += f"📍 Mode: {mode_text}\n"
            text += f"🧪 Demo: {'✅' if has_demo else '❌'}\n"
            text += f"💼 Real: {'✅' if has_real else '❌'}\n"
            
            # Quick mode switch buttons
            mode_buttons = []
            if has_demo:
                mode_buttons.append(InlineKeyboardButton(
                    "🎮 Demo" + (" ✓" if trading_mode == "demo" else ""), 
                    callback_data="bybit:mode_demo"
                ))
            if has_real:
                mode_buttons.append(InlineKeyboardButton(
                    "💵 Real" + (" ✓" if trading_mode == "real" else ""), 
                    callback_data="bybit:mode_real"
                ))
            if has_demo and has_real:
                mode_buttons.append(InlineKeyboardButton(
                    "🔀 Both" + (" ✓" if trading_mode == "both" else ""), 
                    callback_data="bybit:mode_both"
                ))
            if mode_buttons:
                keyboard.append(mode_buttons)
        else:
            text += "❌ Not configured\n\n_Press 🔑 API Keys to set up_"
        
        # Switch to HyperLiquid
        if hl_info.get("configured"):
            keyboard.append([InlineKeyboardButton("🔄 Switch to 🔷 HyperLiquid", callback_data="exchange:set_hl")])
        else:
            keyboard.append([InlineKeyboardButton("🔷 Setup HyperLiquid", callback_data="exchange:setup_hl")])
    
    keyboard.append([InlineKeyboardButton(t.get("button_back", "🔙 Back"), callback_data="main_menu")])
    
    await update.message.reply_text(
        text, 
        parse_mode="Markdown", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@with_texts
@log_calls
async def cmd_switch_exchange(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Switch between Bybit and HyperLiquid"""
    uid = update.effective_user.id
    t = ctx.t
    
    status = get_exchange_status(uid)
    current = status.get("active_exchange", "bybit")
    hl_configured = status.get("hyperliquid", {}).get("configured", False)
    bybit_configured = status.get("bybit", {}).get("configured", False)
    
    keyboard = []
    
    # Bybit option
    if current == "bybit":
        keyboard.append([InlineKeyboardButton("🟠 Bybit ✓ (current)", callback_data="exchange:noop")])
    else:
        keyboard.append([InlineKeyboardButton("🟠 Switch to Bybit", callback_data="exchange:set_bybit")])
    
    # HyperLiquid option
    if hl_configured:
        if current == "hyperliquid":
            keyboard.append([InlineKeyboardButton("🔷 HyperLiquid ✓ (current)", callback_data="exchange:noop")])
        else:
            keyboard.append([InlineKeyboardButton("🔷 Switch to HyperLiquid", callback_data="exchange:set_hl")])
    else:
        keyboard.append([InlineKeyboardButton("🔷 Setup HyperLiquid", callback_data="exchange:setup_hl")])
    
    keyboard.append([InlineKeyboardButton(t.get("button_back", "🔙 Back"), callback_data="main_menu")])
    
    text = (
        "🔄 *Switch Exchange*\n\n"
        f"Current: {'🔷 HyperLiquid' if current == 'hyperliquid' else '🟠 Bybit'}\n\n"
        "Select the exchange you want to trade on:"
    )
    
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@with_texts
@log_calls
async def cmd_webapp(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Open WebApp in browser with auto-login"""
    t = ctx.t
    uid = update.effective_user.id
    
    # Get webapp URL from env, fallback to ngrok file, then localhost
    webapp_url = WEBAPP_URL
    try:
        if webapp_url == "http://localhost:8765":
            ngrok_file = Path(__file__).parent / "run" / "ngrok_url.txt"
            if ngrok_file.exists():
                webapp_url = ngrok_file.read_text().strip()
    except:
        pass
    
    # Generate auto-login token
    try:
        from webapp.services import telegram_auth
        token, login_url = telegram_auth.generate_login_token(uid)
        # Update login_url with current webapp URL (in case ngrok changed)
        # Add timestamp to prevent Telegram from caching old URL
        import time
        cache_bust = int(time.time())
        login_url = f"{webapp_url}/api/auth/token-login?token={token}&_t={cache_bust}"
    except Exception as e:
        logging.warning(f"Failed to generate login token: {e}")
        login_url = f"{webapp_url}?_t={int(time.time())}"
    
    # Check if ngrok (free tier has warning page that breaks WebApp)
    is_ngrok = "ngrok" in webapp_url
    
    if is_ngrok:
        # For ngrok, use regular URL buttons (WebAppInfo shows blank due to ngrok warning)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Open WebApp", url=login_url)],
            [InlineKeyboardButton(t.get("button_back", "🔙 Back"), callback_data="main_menu")]
        ])
    else:
        # For production HTTPS, use WebAppInfo for native experience
        # Add start param with user_id for auto-login and timestamp to prevent Telegram caching
        webapp_url_with_start = f"{webapp_url}?start={uid}&_t={cache_bust}"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Open WebApp", web_app=WebAppInfo(url=webapp_url_with_start))],
            [InlineKeyboardButton("🔗 Open in Browser", url=login_url)],
            [InlineKeyboardButton(t.get("button_back", "🔙 Back"), callback_data="main_menu")]
        ])
    
    text = (
        "🌐 *Trading WebApp*\n\n"
        "Access your trading dashboard:\n\n"
        "• 📊 View positions and orders\n"
        "• 💰 Check balances\n"
        "• ⚙️ Manage settings\n"
        "• 📈 Trading statistics\n\n"
        "_Tap the button below to open_"
    )
    
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True
    )


@log_calls
async def on_hl_api_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle HyperLiquid API settings callbacks"""
    q = update.callback_query
    await q.answer()
    
    uid = q.from_user.id
    data = q.data
    
    if data == "hl_api:setup_mainnet":
        _hl_awaiting_key[uid] = {"waiting": True, "testnet": False}
        await q.edit_message_text(
            "🌐 <b>HyperLiquid Mainnet Setup</b>\n\n"
            "Send your ETH private key (with or without 0x prefix).\n\n"
            "⚠️ <b>Security Tips:</b>\n"
            "• Use a dedicated trading wallet\n"
            "• Never share your key with anyone\n\n"
            "Send /cancel to abort.",
            parse_mode="HTML"
        )
    
    elif data == "hl_api:setup_testnet":
        _hl_awaiting_key[uid] = {"waiting": True, "testnet": True}
        await q.edit_message_text(
            "🧪 <b>HyperLiquid Testnet Setup</b>\n\n"
            "Send your ETH private key (with or without 0x prefix).\n\n"
            "⚠️ <b>Security Tips:</b>\n"
            "• Use a dedicated trading wallet\n"
            "• Never share your key with anyone\n\n"
            "Send /cancel to abort.",
            parse_mode="HTML"
        )
    
    elif data == "hl_api:test":
        # Test HyperLiquid connection
        hl_creds = get_hl_credentials(uid)
        wallet = hl_creds.get("hl_wallet_address")
        testnet = hl_creds.get("hl_testnet", False)
        
        if not wallet:
            await q.edit_message_text("❌ No wallet configured.")
            return
        
        try:
            from hyperliquid import HyperLiquidClient
            client = HyperLiquidClient(
                wallet_address=wallet,
                private_key=hl_creds.get("hl_private_key"),
                testnet=testnet
            )
            state = await client.user_state(wallet)
            balance = float(state.get("marginSummary", {}).get("accountValue", 0))
            
            network = "🧪 Testnet" if testnet else "🌐 Mainnet"
            await q.edit_message_text(
                f"✅ <b>Connection Successful!</b>\n\n"
                f"<b>Network:</b> {network}\n"
                f"<b>Wallet:</b> <code>{wallet[:10]}...{wallet[-6:]}</code>\n"
                f"<b>Balance:</b> ${balance:.2f}\n\n"
                f"🟢 HyperLiquid is ready!",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="hl_api:back")]
                ])
            )
        except Exception as e:
            await q.edit_message_text(
                f"❌ <b>Connection Failed</b>\n\n"
                f"Error: {str(e)[:100]}",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="hl_api:back")]
                ])
            )
    
    elif data == "hl_api:clear":
        clear_hl_credentials(uid)
        await q.edit_message_text(
            "✅ All HyperLiquid credentials cleared.\n\n"
            "Use 🔷 HL API to setup again.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="hl_api:back")]
            ])
        )
    
    elif data == "hl_api:clear_testnet":
        clear_hl_credentials(uid, account_type="testnet")
        await q.edit_message_text(
            "✅ HyperLiquid Testnet credentials cleared.\n\n"
            "Use 🔷 HL API to setup again.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="hl_api:back")]
            ])
        )
    
    elif data == "hl_api:clear_mainnet":
        clear_hl_credentials(uid, account_type="mainnet")
        await q.edit_message_text(
            "✅ HyperLiquid Mainnet credentials cleared.\n\n"
            "Use 🔷 HL API to setup again.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="hl_api:back")]
            ])
        )
    
    elif data == "hl_api:back":
        await q.edit_message_text("Use /start to return to main menu.")


@log_calls
@require_access
async def on_deep_loss_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle deep loss position actions: close, enable DCA, or ignore"""
    q = update.callback_query
    await q.answer()
    
    uid = q.from_user.id
    t = ctx.t
    data = q.data  # Format: deep_loss:action:symbol
    
    parts = data.split(":")
    if len(parts) != 3:
        return
    
    _, action, symbol = parts
    
    if action == "close":
        # Close the position
        try:
            # Get position info
            positions = await fetch_open_positions(uid)
            pos = next((p for p in positions if p.get("symbol") == symbol), None)
            
            if not pos:
                await q.edit_message_text(
                    t.get('position_already_closed', "❌ Позиция {symbol} уже закрыта.").format(symbol=symbol),
                    parse_mode="HTML"
                )
                return
            
            side = pos.get("side")
            size = float(pos.get("size", 0))
            close_side = "Sell" if side == "Buy" else "Buy"
            
            # Place close order
            await place_order(
                user_id=uid,
                symbol=symbol,
                side=close_side,
                orderType="Market",
                qty=size,
                reduceOnly=True
            )
            
            await q.edit_message_text(
                t.get('deep_loss_closed', 
                    "✅ Позиция {symbol} закрыта.\n\n"
                    "Убыток зафиксирован. Иногда лучше принять небольшой убыток, чем надеяться на разворот."
                ).format(symbol=symbol),
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Error closing deep loss position {symbol} for {uid}: {e}")
            await q.edit_message_text(
                t.get('deep_loss_close_error', "❌ Ошибка при закрытии позиции: {error}").format(error=str(e)[:100]),
                parse_mode="HTML"
            )
    
    elif action == "dca":
        # Enable DCA for this symbol
        try:
            cfg = get_user_config(uid)
            
            # Check if DCA is already enabled globally
            dca_enabled = cfg.get("dca_enabled", 0)
            
            if dca_enabled:
                await q.edit_message_text(
                    t.get('dca_already_enabled',
                        "✅ DCA добор уже включен!\n\n"
                        "📊 <b>{symbol}</b>\n"
                        "Бот будет автоматически добавлять к позиции при просадке:\n"
                        "• -10% → добор\n"
                        "• -25% → добор\n\n"
                        "Это поможет усреднить цену входа."
                    ).format(symbol=symbol),
                    parse_mode="HTML"
                )
            else:
                # Enable DCA globally
                set_user_field(uid, "dca_enabled", 1)
                
                await q.edit_message_text(
                    t.get('dca_enabled_for_symbol',
                        "✅ DCA добор включен!\n\n"
                        "📊 <b>{symbol}</b>\n"
                        "Бот будет автоматически добавлять к позиции при просадке:\n"
                        "• -10% → добор (усреднение)\n"
                        "• -25% → добор (усреднение)\n\n"
                        "⚠️ DCA требует достаточный баланс для доборов.\n"
                        "Настроить параметры: /strategy_settings"
                    ).format(symbol=symbol),
                    parse_mode="HTML"
                )
                
        except Exception as e:
            logger.error(f"Error enabling DCA for {symbol} for {uid}: {e}")
            await q.edit_message_text(
                t.get('dca_enable_error', "❌ Ошибка: {error}").format(error=str(e)[:100]),
                parse_mode="HTML"
            )
    
    elif action == "ignore":
        await q.edit_message_text(
            t.get('deep_loss_ignored',
                "🔇 Понял, позиция {symbol} оставлена без изменений.\n\n"
                "⚠️ Помните: без стоп-лосса риск потерь неограничен.\n"
                "Вы можете закрыть позицию вручную через /positions"
            ).format(symbol=symbol),
            parse_mode="HTML"
        )


@log_calls
async def on_exchange_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle exchange switching callbacks"""
    q = update.callback_query
    await q.answer()
    
    uid = q.from_user.id
    data = q.data
    
    if data == "exchange:set_bybit":
        set_exchange_type(uid, "bybit")
        await q.edit_message_text(
            "✅ *Switched to Bybit*\n\n"
            "All trading operations will now use Bybit.",
            parse_mode="Markdown"
        )
        # Send new keyboard to update ReplyKeyboard
        await ctx.bot.send_message(
            chat_id=uid,
            text="🟠 *Bybit mode activated*",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(ctx, user_id=uid)
        )
    
    elif data == "exchange:set_hl":
        # Check if HL is configured
        hl_creds = get_hl_credentials(uid)
        if not hl_creds.get("hl_wallet_address") and not hl_creds.get("hl_private_key"):
            await q.edit_message_text(
                "❌ *HyperLiquid not configured*\n\n"
                "Please setup HyperLiquid first.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔷 Setup HyperLiquid", callback_data="exchange:setup_hl")]
                ])
            )
            return
        
        set_exchange_type(uid, "hyperliquid")
        await q.edit_message_text(
            "✅ *Switched to HyperLiquid*\n\n"
            "All trading operations will now use HyperLiquid DEX.",
            parse_mode="Markdown"
        )
        # Send new keyboard to update ReplyKeyboard
        await ctx.bot.send_message(
            chat_id=uid,
            text="🔷 *HyperLiquid mode activated*",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(ctx, user_id=uid)
        )
    
    elif data == "exchange:setup_hl":
        # Redirect to HyperLiquid setup
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Mainnet", callback_data="hl:mainnet"),
             InlineKeyboardButton("🧪 Testnet", callback_data="hl:testnet")],
        ])
        await q.edit_message_text(
            "🔷 *HyperLiquid Setup*\n\n"
            "Select network:\n\n"
            "• *Mainnet* - Real trading with real funds\n"
            "• *Testnet* - Practice with test funds\n\n"
            "After selecting, send your private key.",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    elif data == "exchange:switch":
        # Quick switch between configured exchanges
        current = get_exchange_type(uid)
        if current == "bybit":
            hl_creds = get_hl_credentials(uid)
            if hl_creds.get("hl_wallet_address") or hl_creds.get("hl_private_key"):
                set_exchange_type(uid, "hyperliquid")
                await q.edit_message_text(
                    "✅ *Switched to HyperLiquid*\n\n"
                    "All trading operations will now use HyperLiquid DEX.",
                    parse_mode="Markdown"
                )
                await ctx.bot.send_message(
                    chat_id=uid,
                    text="🔷 *HyperLiquid mode activated*",
                    parse_mode="Markdown",
                    reply_markup=main_menu_keyboard(ctx, user_id=uid)
                )
            else:
                await q.edit_message_text(
                    "❌ HyperLiquid not configured. Setup first.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔷 Setup HyperLiquid", callback_data="exchange:setup_hl")]
                    ])
                )
        else:
            set_exchange_type(uid, "bybit")
            await q.edit_message_text(
                "✅ *Switched to Bybit*\n\n"
                "All trading operations will now use Bybit.",
                parse_mode="Markdown"
            )
            await ctx.bot.send_message(
                chat_id=uid,
                text="🟠 *Bybit mode activated*",
                parse_mode="Markdown",
                reply_markup=main_menu_keyboard(ctx, user_id=uid)
            )
    
    elif data == "exchange:noop":
        pass  # Do nothing, already on this exchange
    
    elif data == "main_menu":
        await q.edit_message_text("Use /start to return to main menu.")


@log_calls
async def on_bybit_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle Bybit mode switching callbacks"""
    q = update.callback_query
    await q.answer()
    
    uid = q.from_user.id
    data = q.data
    
    if data == "bybit:mode_demo":
        set_trading_mode(uid, "demo")
        await q.edit_message_text(
            "🎮 *Demo mode activated*\n\n"
            "All trades will execute on your Demo account.\n"
            "Perfect for testing strategies!",
            parse_mode="Markdown"
        )
        await ctx.bot.send_message(
            chat_id=uid,
            text="🟠 Bybit 🎮 Demo",
            reply_markup=main_menu_keyboard(ctx, user_id=uid)
        )
    
    elif data == "bybit:mode_real":
        set_trading_mode(uid, "real")
        await q.edit_message_text(
            "💵 *Real mode activated*\n\n"
            "⚠️ All trades will execute with real funds!\n"
            "Trade responsibly.",
            parse_mode="Markdown"
        )
        await ctx.bot.send_message(
            chat_id=uid,
            text="🟠 Bybit 💵 Real",
            reply_markup=main_menu_keyboard(ctx, user_id=uid)
        )
    
    elif data == "bybit:mode_both":
        set_trading_mode(uid, "both")
        await q.edit_message_text(
            "🔀 *Both mode activated*\n\n"
            "⚠️ All signals will be executed on BOTH Demo and Real accounts!\n"
            "Use with caution.",
            parse_mode="Markdown"
        )
        await ctx.bot.send_message(
            chat_id=uid,
            text="🟠 Bybit 🔀 Both",
            reply_markup=main_menu_keyboard(ctx, user_id=uid)
        )


@log_calls
async def on_hl_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle HyperLiquid callbacks"""
    q = update.callback_query
    await q.answer()
    
    uid = q.from_user.id
    data = q.data
    
    if data == "hl:mainnet":
        # Check if user already has HL configured - just switch network
        hl_creds = get_hl_credentials(uid)
        if hl_creds.get("hl_private_key"):
            # Already configured, just switch to mainnet
            set_hl_credentials(uid, 
                private_key=hl_creds.get("hl_private_key"),
                wallet_address=hl_creds.get("hl_wallet_address"),
                vault_address=hl_creds.get("hl_vault_address"),
                testnet=False
            )
            await q.edit_message_text(
                "🌐 *Switched to Mainnet*\n\n"
                "⚠️ Now trading with real funds!",
                parse_mode="Markdown"
            )
            await ctx.bot.send_message(
                chat_id=uid,
                text="🔷 HL 🌐",
                reply_markup=main_menu_keyboard(ctx, user_id=uid)
            )
            return
        
        # New setup
        _hl_awaiting_key[uid] = {"waiting": True, "testnet": False}
        await q.edit_message_text(
            "🔑 *Connect to HyperLiquid Mainnet*\n\n"
            "Please send your ETH private key (with or without 0x prefix).\n\n"
            "⚠️ *Security Tips:*\n"
            "• Use a dedicated trading wallet\n"
            "• Never share your key with anyone\n\n"
            "Send /cancel to abort.",
            parse_mode="Markdown"
        )
    
    elif data == "hl:testnet":
        # Check if user already has HL configured - just switch network
        hl_creds = get_hl_credentials(uid)
        if hl_creds.get("hl_private_key"):
            # Already configured, just switch to testnet
            set_hl_credentials(uid, 
                private_key=hl_creds.get("hl_private_key"),
                wallet_address=hl_creds.get("hl_wallet_address"),
                vault_address=hl_creds.get("hl_vault_address"),
                testnet=True
            )
            await q.edit_message_text(
                "🧪 *Switched to Testnet*\n\n"
                "Safe for practice trading!",
                parse_mode="Markdown"
            )
            await ctx.bot.send_message(
                chat_id=uid,
                text="🔷 HL 🧪",
                reply_markup=main_menu_keyboard(ctx, user_id=uid)
            )
            return
        
        # New setup
        _hl_awaiting_key[uid] = {"waiting": True, "testnet": True}
        await q.edit_message_text(
            "🔑 *Connect to HyperLiquid Testnet*\n\n"
            "Please send your ETH private key (with or without 0x prefix).\n\n"
            "⚠️ *Security Tips:*\n"
            "• Use a dedicated trading wallet\n"
            "• Never share your key with anyone\n\n"
            "Send /cancel to abort.",
            parse_mode="Markdown"
        )
    
    elif data == "hl:balance":
        hl_creds = get_hl_credentials(uid)
        try:
            adapter = HLAdapter(
                private_key=hl_creds["hl_private_key"],
                testnet=hl_creds.get("hl_testnet", False),
                vault_address=hl_creds.get("hl_vault_address")
            )
            result = await adapter.get_balance()
            
            if result.get("success"):
                data_balance = result.get("data", {})
                equity = float(data_balance.get("equity", 0))
                available = float(data_balance.get("available", 0))
                unrealized_pnl = float(data_balance.get("unrealized_pnl", 0))
                
                pnl_emoji = "🟢" if unrealized_pnl >= 0 else "🔴"
                network = "🧪 Testnet" if hl_creds.get("hl_testnet") else "🌐 Mainnet"
                
                await q.edit_message_text(
                    f"💰 *HyperLiquid Balance* {network}\n\n"
                    f"💎 *Equity:* ${equity:,.2f}\n"
                    f"💵 *Available:* ${available:,.2f}\n"
                    f"{pnl_emoji} *Unrealized PnL:* ${unrealized_pnl:,.2f}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ Back", callback_data="hl:menu")]
                    ])
                )
            else:
                await q.edit_message_text(f"❌ Error: {result.get('error')}")
        except Exception as e:
            await q.edit_message_text(f"❌ Error: {str(e)}")
    
    elif data == "hl:positions":
        hl_creds = get_hl_credentials(uid)
        try:
            adapter = HLAdapter(
                private_key=hl_creds["hl_private_key"],
                testnet=hl_creds.get("hl_testnet", False),
                vault_address=hl_creds.get("hl_vault_address")
            )
            result = await adapter.fetch_positions()
            
            if result.get("success"):
                positions = result.get("data", [])
                if not positions:
                    text = "📭 No open positions."
                else:
                    lines = ["📈 *Positions*\n"]
                    for pos in positions[:5]:
                        symbol = pos.get("symbol", "?")
                        side = "🟢" if pos.get("side") == "Buy" else "🔴"
                        pnl = float(pos.get("unrealized_pnl", 0))
                        lines.append(f"{side} {symbol}: ${pnl:+,.2f}")
                    text = "\n".join(lines)
                
                await q.edit_message_text(
                    text,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ Back", callback_data="hl:menu")]
                    ])
                )
            else:
                await q.edit_message_text(f"❌ Error: {result.get('error')}")
        except Exception as e:
            await q.edit_message_text(f"❌ Error: {str(e)}")
    
    elif data == "hl:switch":
        current = get_exchange_type(uid)
        new_exchange = "hyperliquid" if current == "bybit" else "bybit"
        set_exchange_type(uid, new_exchange)
        
        await q.edit_message_text(
            f"✅ Switched to *{new_exchange.upper()}*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data="hl:menu")]
            ])
        )
    
    elif data == "hl:network":
        hl_creds = get_hl_credentials(uid)
        current_testnet = hl_creds.get("hl_testnet", False)
        new_testnet = not current_testnet
        
        set_hl_credentials(
            uid,
            hl_creds["hl_private_key"],
            hl_creds.get("hl_vault_address"),
            new_testnet
        )
        
        network = "Testnet" if new_testnet else "Mainnet"
        await q.edit_message_text(
            f"✅ Switched to *{network}*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data="hl:menu")]
            ])
        )
    
    elif data == "hl:disconnect":
        await q.edit_message_text(
            "⚠️ *Disconnect HyperLiquid?*\n\n"
            "This will remove your private key and switch back to Bybit.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Yes, Disconnect", callback_data="hl:confirm_disconnect")],
                [InlineKeyboardButton("❌ Cancel", callback_data="hl:menu")]
            ])
        )
    
    elif data == "hl:confirm_disconnect":
        clear_hl_credentials(uid)
        set_exchange_type(uid, "bybit")
        await q.edit_message_text(
            "✅ HyperLiquid disconnected.\nSwitched to Bybit.",
            parse_mode="Markdown"
        )
    
    elif data == "hl:menu":
        # Re-show main menu
        hl_creds = get_hl_credentials(uid)
        is_configured = bool(hl_creds.get("hl_private_key"))
        exchange = get_exchange_type(uid)
        network = "Testnet" if hl_creds.get("hl_testnet") else "Mainnet"
        
        if is_configured:
            addr = hl_creds.get("hl_address", "")[:10] + "..." if hl_creds.get("hl_address") else "N/A"
            buttons = [
                [InlineKeyboardButton("💰 Balance", callback_data="hl:balance"),
                 InlineKeyboardButton("📈 Positions", callback_data="hl:positions")],
                [InlineKeyboardButton("🔄 Switch to HL" if exchange == "bybit" else "🔄 Switch to Bybit", 
                                    callback_data="hl:switch")],
                [InlineKeyboardButton("🌐 Testnet" if not hl_creds.get("hl_testnet") else "🌐 Mainnet",
                                    callback_data="hl:network")],
                [InlineKeyboardButton("❌ Disconnect", callback_data="hl:disconnect")],
            ]
            await q.edit_message_text(
                f"🔗 *HyperLiquid DEX*\n\n"
                f"📊 *Status:* ✅ Connected\n"
                f"🌐 *Network:* {network}\n"
                f"👛 *Wallet:* `{addr}`\n"
                f"🔄 *Active:* {exchange.upper()}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await q.edit_message_text(
                "🔗 *HyperLiquid DEX*\n\nNot connected.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🌐 Mainnet", callback_data="hl:mainnet"),
                     InlineKeyboardButton("🧪 Testnet", callback_data="hl:testnet")],
                ])
            )
    
    elif data == "hl:setkey":
        _hl_awaiting_key[uid] = {"waiting": True, "testnet": False}
        await q.edit_message_text(
            "🔑 *Update Private Key*\n\n"
            "Send your new ETH private key.\n"
            "Send /cancel to abort.",
            parse_mode="Markdown"
        )


async def handle_hl_strategy_param(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle HL strategy parameter input. Returns True if handled."""
    uid = update.effective_user.id
    
    if uid not in _awaiting_hl_param:
        return False
    
    # Get translations
    cfg = get_user_config(uid)
    lang = cfg.get("lang", DEFAULT_LANG)
    t = LANGS.get(lang, LANGS[DEFAULT_LANG])
    
    text = update.message.text.strip()
    
    # Cancel
    if text.lower() == "/cancel":
        del _awaiting_hl_param[uid]
        await update.message.reply_text(t.get("cancelled", "❌ Cancelled."))
        return True
    
    try:
        value = float(text)
    except ValueError:
        await update.message.reply_text(t.get("invalid_number", "❌ Please enter a valid number."))
        return True
    
    info = _awaiting_hl_param[uid]
    strategy = info["strategy"]
    param = info["param"]
    
    # Validate ranges
    if param == "hl_percent" and (value <= 0 or value > 100):
        await update.message.reply_text(t.get("entry_pct_range_error", "❌ Entry % must be between 0.1 and 100."))
        return True
    if param in ["hl_sl_percent", "hl_tp_percent"] and (value <= 0 or value > 500):
        await update.message.reply_text(t.get("sl_tp_range_error", "❌ SL/TP % must be between 0.1 and 500."))
        return True
    if param == "hl_leverage" and (value < 1 or value > 100):
        await update.message.reply_text(t.get("leverage_range_error", "❌ Leverage must be between 1 and 100."))
        return True
    
    # Save the value
    if param == "hl_leverage":
        value = int(value)
    db.set_hl_strategy_setting(uid, strategy, param, value)
    
    del _awaiting_hl_param[uid]
    
    strat_name = STRATEGY_NAMES_MAP.get(strategy, strategy.upper())
    param_labels = {
        "hl_percent": "Entry %",
        "hl_sl_percent": "Stop-Loss %", 
        "hl_tp_percent": "Take-Profit %",
        "hl_leverage": "Leverage"
    }
    param_label = param_labels.get(param, param)
    
    cfg = get_user_config(uid)
    lang = cfg.get("lang", DEFAULT_LANG)
    t = LANGS.get(lang, LANGS[DEFAULT_LANG])
    
    await update.message.reply_text(
        f"✅ {strat_name} HyperLiquid {param_label} set to {value}",
        reply_markup=get_hl_strategy_keyboard(strategy, t, uid=uid)
    )
    return True


async def handle_hl_private_key(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle private key input for HyperLiquid setup. Returns True if handled."""
    uid = update.effective_user.id
    
    if uid not in _hl_awaiting_key or not _hl_awaiting_key[uid].get("waiting"):
        return False
    
    # Get translations
    cfg = get_user_config(uid)
    lang = cfg.get("lang", DEFAULT_LANG)
    t = LANGS.get(lang, LANGS[DEFAULT_LANG])
    
    text = update.message.text.strip()
    
    # Cancel
    if text.lower() == "/cancel":
        del _hl_awaiting_key[uid]
        await update.message.reply_text(t.get("hl_setup_cancelled", "❌ HyperLiquid setup cancelled."))
        return True
    
    # Validate private key format
    key = text.replace("0x", "").strip()
    
    # Check if user sent wallet address instead of private key
    if len(key) == 40:
        await update.message.reply_text(
            "❌ *This looks like a wallet address, not a private key!*\n\n"
            "• Wallet address: 40 characters (what you sent)\n"
            "• Private key: 64 characters (what we need)\n\n"
            "Your private key is in your wallet app under 'Export Private Key'.\n\n"
            "Try again or send /cancel to abort.",
            parse_mode="Markdown"
        )
        return True
    
    if len(key) != 64 or not all(c in "0123456789abcdefABCDEF" for c in key):
        await update.message.reply_text(
            f"❌ *Invalid private key format*\n\n"
            f"You sent: {len(key)} characters\n"
            f"Expected: 64 hex characters\n\n"
            "Private key should look like:\n"
            "`47b6e4448f97b26f...40e5981a`\n\n"
            "Try again or send /cancel to abort.",
            parse_mode="Markdown"
        )
        return True
    
    testnet = _hl_awaiting_key[uid].get("testnet", False)
    del _hl_awaiting_key[uid]
    
    # Try to derive address and validate
    try:
        from eth_account import Account
        account = Account.from_key("0x" + key)
        address = account.address
        
        # Save credentials - use account_type for proper column placement
        account_type = "testnet" if testnet else "mainnet"
        set_hl_credentials(uid, creds={
            "hl_private_key": "0x" + key,
            "hl_wallet_address": address,
            "hl_testnet": testnet,
            "account_type": account_type
        })
        
        # Enable HL for user
        set_hl_enabled(uid, True)
        
        # Delete the message containing the private key for security
        try:
            await update.message.delete()
        except:
            pass
        
        network = "🧪 Testnet" if testnet else "🌐 Mainnet"
        await update.message.reply_text(
            f"✅ *HyperLiquid Connected!*\n\n"
            f"*Network:* {network}\n"
            f"*Wallet:* `{address[:10]}...{address[-6:]}`\n\n"
            f"Now you can switch to HyperLiquid using 🔄 Switch button.",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"HL key setup error: {e}")
        await update.message.reply_text(
            f"❌ Error setting up HyperLiquid: {str(e)}\n\n"
            "Make sure you have eth-account installed: pip install eth-account"
        )
    
    return True

async def _shutdown(app: Application):
    task = app.bot_data.get("monitor_task")
    if isinstance(task, asyncio.Task) and not task.done():
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

    global _session
    if _session is not None:
        await _session.close()
        _session = None

def main():
    db.init_db()
    try:
        set_user_field(ADMIN_ID, "is_allowed", 1)
        set_user_field(ADMIN_ID, "is_banned", 0)
    except Exception as e:
        logger.warning(f"Failed to ensure admin allowed: {e}")

    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN not set in the environment")
    request = HTTPXRequest(connect_timeout=10.0, read_timeout=30.0)

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .request(request)
        .post_init(start_monitoring)   
        .build()
    )
    
    # Initialize notification service
    try:
        global notification_service
        notification_service = init_notification_service(app.bot, db)
        logger.info("Notification service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize notification service: {e}")
    
    app.add_handler(CallbackQueryHandler(on_coin_group_cb, pattern=r"^coins:"))
    app.add_handler(CallbackQueryHandler(on_positions_cb, pattern=r"^pos:"))
    app.add_handler(CallbackQueryHandler(on_stats_callback, pattern=r"^stats:"))
    app.add_handler(CallbackQueryHandler(handle_balance_callback, pattern=r"^balance:"))
    app.add_handler(CallbackQueryHandler(handle_positions_callback, pattern=r"^positions:"))
    app.add_handler(CallbackQueryHandler(handle_orders_callback, pattern=r"^orders:"))
    app.add_handler(CommandHandler("start",        cmd_start))
    app.add_handler(CommandHandler("account",      cmd_account))
    app.add_handler(CommandHandler("openorders",   cmd_openorders))
    app.add_handler(CommandHandler("positions",    cmd_positions))
    app.add_handler(CommandHandler("openpositions", cmd_open_positions))
    app.add_handler(CommandHandler("stats",        cmd_trade_stats))
    app.add_handler(CommandHandler("select_coins", cmd_select_coins))
    app.add_handler(CommandHandler("set_percent",  cmd_set_percent))
    app.add_handler(CommandHandler("toggle_limit", cmd_toggle_limit))
    app.add_handler(CommandHandler("toggle_oi",    cmd_toggle_oi))
    app.add_handler(CommandHandler("toggle_rsi_bb",cmd_toggle_rsi_bb))
    app.add_handler(CommandHandler("market",       cmd_market))
    app.add_handler(CommandHandler("show_config",  cmd_show_config))
    app.add_handler(CommandHandler("indicators",   cmd_indicators))
    app.add_handler(CommandHandler("support",      cmd_support))
    app.add_handler(CommandHandler("admin",        cmd_admin))
    
    # Subscription handlers
    app.add_handler(CommandHandler("subscribe",    cmd_subscribe))
    app.add_handler(CallbackQueryHandler(on_subscribe_cb, pattern=r"^sub:"))
    app.add_handler(CallbackQueryHandler(on_admin_license_cb, pattern=r"^adm_lic:"))
    app.add_handler(CallbackQueryHandler(on_admin_payment_cb, pattern=r"^adm_pay:"))
    app.add_handler(PreCheckoutQueryHandler(on_pre_checkout_query))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, on_successful_payment))
    
    # TRC Wallet handlers
    app.add_handler(CommandHandler("wallet",       cmd_wallet))
    app.add_handler(CallbackQueryHandler(on_wallet_cb, pattern=r"^wallet:"))
    
    # Sovereign Owner (Monetary Authority) handlers
    app.add_handler(CommandHandler("sovereign",    cmd_sovereign))
    app.add_handler(CallbackQueryHandler(on_sovereign_cb, pattern=r"^sovereign:"))

    app.add_handler(CallbackQueryHandler(on_moderate_cb, pattern=r"^mod:(approve|ban):\d+$"))
    app.add_handler(CallbackQueryHandler(on_admin_cb,    pattern=r"^admin:"))
    app.add_handler(CommandHandler("lang",               cmd_lang))
    app.add_handler(CallbackQueryHandler(on_setlang_cb,  pattern=r"^setlang:"))
    app.add_handler(CallbackQueryHandler(on_api_settings_cb, pattern=r"^api:"))
    app.add_handler(CallbackQueryHandler(on_spot_settings_cb, pattern=r"^spot:"))
    app.add_handler(CommandHandler("approve",            cmd_approve))
    app.add_handler(CommandHandler("ban",                cmd_ban))
    app.add_handler(CommandHandler("whoami",             whoami))

    # HyperLiquid DEX commands
    app.add_handler(CommandHandler("hl",                 cmd_hyperliquid))
    app.add_handler(CommandHandler("hyperliquid",        cmd_hyperliquid))
    app.add_handler(CommandHandler("hl_balance",         cmd_hl_balance))
    app.add_handler(CommandHandler("hl_positions",       cmd_hl_positions))
    app.add_handler(CommandHandler("hl_switch",          cmd_hl_switch))
    app.add_handler(CommandHandler("hl_clear",           cmd_hl_clear))
    app.add_handler(CallbackQueryHandler(on_hl_callback, pattern=r"^hl:"))
    app.add_handler(CallbackQueryHandler(on_deep_loss_callback, pattern=r"^deep_loss:"))
    app.add_handler(CallbackQueryHandler(on_exchange_callback, pattern=r"^exchange:"))
    app.add_handler(CallbackQueryHandler(on_bybit_callback, pattern=r"^bybit:"))
    app.add_handler(CallbackQueryHandler(on_hl_api_callback, pattern=r"^hl_api:"))

    app.add_handler(CommandHandler("terms",              cmd_terms))
    app.add_handler(CommandHandler("strategy_settings",  cmd_strategy_settings))
    app.add_handler(CallbackQueryHandler(on_terms_cb,    pattern=r"^terms:(accept|decline)$"))
    app.add_handler(CallbackQueryHandler(on_twofa_cb,    pattern=r"^twofa_(approve|deny):"))
    app.add_handler(CallbackQueryHandler(on_users_cb,    pattern=r"^users:"))
    app.add_handler(CallbackQueryHandler(callback_strategy_settings, pattern=r"^(strat_set:|strat_toggle:|strat_param:|strat_reset:|dca_param:|dca_toggle|strat_order_type:|strat_coins:|strat_coins_set:|scryptomera_dir:|scryptomera_side:|scalper_dir:|scalper_side:|fibonacci_dir:|elcaro_dir:|oi_dir:|rsi_bb_dir:|strat_atr_toggle:|strat_mode:|global_param:|global_ladder:|strat_hl:|hl_strat:|rsi_bb_side:|elcaro_side:|fibonacci_side:|oi_side:)"))

    try:
        manual_labels = {texts["button_manual_order"] for texts in LANGS.values() if "button_manual_order" in texts}
        manual_pattern = r"^(" + "|".join(re.escape(lbl) for lbl in sorted(manual_labels, key=len, reverse=True)) + r")$" \
            if manual_labels else r"^\b$"  
    except Exception as e:
        logger.error(f"Failed to build manual order regex: {e}")
        manual_pattern = r"^\b$"

    try:
        cancel_labels = {texts["button_cancel_order"] for texts in LANGS.values() if "button_cancel_order" in texts}
        cancel_pattern = r"^(" + "|".join(re.escape(lbl) for lbl in sorted(cancel_labels, key=len, reverse=True)) + r")$" \
            if cancel_labels else r"^\b$"
    except Exception as e:
        logger.error(f"Failed to build cancel order regex: {e}")
        cancel_pattern = r"^\b$"
 
    conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex(manual_pattern), cmd_manual_order),
        ],
        states={
            ORDER_TYPE:   [CallbackQueryHandler(on_order_type_cb, pattern=r"^order_type:")],
            ORDER_PARAMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, manual_order_text)],
        },
        fallbacks=[
            MessageHandler(filters.Regex(cancel_pattern), cancel_order),
        ],
        allow_reentry=False,
        per_message=False,
        per_chat=True,   
        per_user=True  
    )
    app.add_handler(conv)

    if SIGNAL_CHANNEL_IDS:
        app.add_handler(
            MessageHandler(
                filters.Chat(chat_id=SIGNAL_CHANNEL_IDS)
                & (filters.TEXT | filters.CAPTION)
                & filters.ChatType.CHANNEL,
                on_channel_post,
            )
        )
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    logger.info("🚀 Bot starting, SIGNAL_CHANNEL_IDS=%s", SIGNAL_CHANNEL_IDS)
    app.add_error_handler(on_error)

    try:
        app.run_polling(allowed_updates=["message", "channel_post", "callback_query"])
    finally:
        logger.info("Shutting down application and HTTP session")
        loop = asyncio.get_event_loop()
        mon_task = app.bot_data.get("monitor_task")
        if mon_task:
            mon_task.cancel()
            try:
                loop.run_until_complete(mon_task)
            except asyncio.CancelledError:
                pass
        try:
            loop.run_until_complete(app.shutdown())
            loop.run_until_complete(app.stop())
        except Exception as e:
            logger.warning(f"App shutdown warning: {e}")
        if _session:
            try:
                loop.run_until_complete(_session.close())
            except Exception as e:
                logger.warning(f"AIOHTTP close warning: {e}")

        logger.info("Shutdown complete")

if __name__ == '__main__':
    main()
