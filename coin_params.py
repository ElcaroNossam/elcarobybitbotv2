# coin_params.py
import os
from pathlib import Path
from typing import Callable

# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGY DEFAULTS - Used for all strategies when user hasn't customized
# Can be overridden via environment variables
# ═══════════════════════════════════════════════════════════════════════════════

# Trading parameters defaults
# Entry % max is 3% (1-3% range recommended for risk management)
DEFAULT_PERCENT = float(os.getenv("DEFAULT_PERCENT", "1.0"))        # Entry % (risk per trade, max 3%)
MAX_ENTRY_PERCENT = 3.0  # Maximum allowed entry percentage
DEFAULT_SL_PCT = float(os.getenv("DEFAULT_SL_PCT", "30.0"))         # Stop-Loss % (default 30%)
DEFAULT_TP_PCT = float(os.getenv("DEFAULT_TP_PCT", "25.0"))         # Take-Profit % (default 25%)
DEFAULT_LEVERAGE = int(os.getenv("DEFAULT_LEVERAGE", "10"))         # Leverage

# ATR Trailing defaults - ENABLED by default with 3% trigger
DEFAULT_USE_ATR = os.getenv("DEFAULT_USE_ATR", "1") == "1"          # ATR Trailing enabled by default
DEFAULT_ATR_TRIGGER_PCT = float(os.getenv("DEFAULT_ATR_TRIGGER_PCT", "3.0"))  # Trigger % (activate at 3% profit)
DEFAULT_ATR_STEP_PCT = float(os.getenv("DEFAULT_ATR_STEP_PCT", "0.5"))        # Step % (trail by 0.5%)

# Break-Even (BE) defaults - move SL to entry when profit reaches trigger
DEFAULT_BE_ENABLED = os.getenv("DEFAULT_BE_ENABLED", "0") == "1"       # BE disabled by default
DEFAULT_BE_TRIGGER_PCT = float(os.getenv("DEFAULT_BE_TRIGGER_PCT", "1.0"))  # Trigger % to move to BE

# Partial Take Profit (срез маржи) defaults - close X% of position at +Y% profit
DEFAULT_PARTIAL_TP_ENABLED = os.getenv("DEFAULT_PARTIAL_TP_ENABLED", "0") == "1"  # Disabled by default
DEFAULT_PARTIAL_TP_1_TRIGGER_PCT = float(os.getenv("DEFAULT_PARTIAL_TP_1_TRIGGER_PCT", "2.0"))  # Step 1 trigger
DEFAULT_PARTIAL_TP_1_CLOSE_PCT = float(os.getenv("DEFAULT_PARTIAL_TP_1_CLOSE_PCT", "30.0"))     # Step 1 close %
DEFAULT_PARTIAL_TP_2_TRIGGER_PCT = float(os.getenv("DEFAULT_PARTIAL_TP_2_TRIGGER_PCT", "5.0"))  # Step 2 trigger
DEFAULT_PARTIAL_TP_2_CLOSE_PCT = float(os.getenv("DEFAULT_PARTIAL_TP_2_CLOSE_PCT", "30.0"))     # Step 2 close %

# Order type default
DEFAULT_ORDER_TYPE = os.getenv("DEFAULT_ORDER_TYPE", "market")      # market/limit
DEFAULT_LIMIT_OFFSET_PCT = float(os.getenv("DEFAULT_LIMIT_OFFSET_PCT", "0.1"))  # Limit order offset %

# DCA defaults
DEFAULT_DCA_ENABLED = os.getenv("DEFAULT_DCA_ENABLED", "0") == "1"  # DCA disabled by default
DEFAULT_DCA_PCT_1 = float(os.getenv("DEFAULT_DCA_PCT_1", "10.0"))    # First DCA level %
DEFAULT_DCA_PCT_2 = float(os.getenv("DEFAULT_DCA_PCT_2", "25.0"))    # Second DCA level %

# Position limits
DEFAULT_MAX_POSITIONS = int(os.getenv("DEFAULT_MAX_POSITIONS", "0"))  # 0 = unlimited

# Coins filter
DEFAULT_COINS_GROUP = os.getenv("DEFAULT_COINS_GROUP", "ALL")  # ALL, TOP100, VOLATILE

# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGY DEFAULTS - Per-strategy defaults for LONG and SHORT
# All strategies use the same defaults, user can customize per strategy+side
# ═══════════════════════════════════════════════════════════════════════════════
STRATEGY_DEFAULTS = {
    "long": {
        "enabled": True,
        "percent": DEFAULT_PERCENT,
        "sl_percent": DEFAULT_SL_PCT,
        "tp_percent": DEFAULT_TP_PCT,
        "leverage": DEFAULT_LEVERAGE,
        "use_atr": 1,  # ATR ENABLED by default
        "atr_trigger_pct": DEFAULT_ATR_TRIGGER_PCT,
        "atr_step_pct": DEFAULT_ATR_STEP_PCT,
        "be_enabled": 1 if DEFAULT_BE_ENABLED else 0,  # Break-Even
        "be_trigger_pct": DEFAULT_BE_TRIGGER_PCT,       # BE trigger %
        # Partial Take Profit (срез маржи)
        "partial_tp_enabled": DEFAULT_PARTIAL_TP_ENABLED,
        "partial_tp_1_trigger_pct": DEFAULT_PARTIAL_TP_1_TRIGGER_PCT,
        "partial_tp_1_close_pct": DEFAULT_PARTIAL_TP_1_CLOSE_PCT,
        "partial_tp_2_trigger_pct": DEFAULT_PARTIAL_TP_2_TRIGGER_PCT,
        "partial_tp_2_close_pct": DEFAULT_PARTIAL_TP_2_CLOSE_PCT,
        "order_type": DEFAULT_ORDER_TYPE,
        "limit_offset_pct": DEFAULT_LIMIT_OFFSET_PCT,
        "dca_enabled": 1 if DEFAULT_DCA_ENABLED else 0,
        "dca_pct_1": DEFAULT_DCA_PCT_1,
        "dca_pct_2": DEFAULT_DCA_PCT_2,
        "max_positions": DEFAULT_MAX_POSITIONS,
        "coins_group": DEFAULT_COINS_GROUP,
    },
    "short": {
        "enabled": True,
        "percent": DEFAULT_PERCENT,
        "sl_percent": DEFAULT_SL_PCT,
        "tp_percent": DEFAULT_TP_PCT,
        "leverage": DEFAULT_LEVERAGE,
        "use_atr": 1,  # ATR ENABLED by default
        "atr_trigger_pct": DEFAULT_ATR_TRIGGER_PCT,
        "atr_step_pct": DEFAULT_ATR_STEP_PCT,
        "be_enabled": 1 if DEFAULT_BE_ENABLED else 0,  # Break-Even
        "be_trigger_pct": DEFAULT_BE_TRIGGER_PCT,       # BE trigger %
        # Partial Take Profit (срез маржи)
        "partial_tp_enabled": DEFAULT_PARTIAL_TP_ENABLED,
        "partial_tp_1_trigger_pct": DEFAULT_PARTIAL_TP_1_TRIGGER_PCT,
        "partial_tp_1_close_pct": DEFAULT_PARTIAL_TP_1_CLOSE_PCT,
        "partial_tp_2_trigger_pct": DEFAULT_PARTIAL_TP_2_TRIGGER_PCT,
        "partial_tp_2_close_pct": DEFAULT_PARTIAL_TP_2_CLOSE_PCT,
        "order_type": DEFAULT_ORDER_TYPE,
        "limit_offset_pct": DEFAULT_LIMIT_OFFSET_PCT,
        "dca_enabled": 1 if DEFAULT_DCA_ENABLED else 0,
        "dca_pct_1": DEFAULT_DCA_PCT_1,
        "dca_pct_2": DEFAULT_DCA_PCT_2,
        "max_positions": DEFAULT_MAX_POSITIONS,
        "coins_group": DEFAULT_COINS_GROUP,
    },
}

# Legacy compatibility
DEFAULT_TP_PCT_LEGACY = DEFAULT_TP_PCT
DEFAULT_SL_PCT_LEGACY = DEFAULT_SL_PCT

# ─── Dynamic symbols loading from symbols.txt ───────────────────────────────
def _load_top_symbols() -> set[str]:
    """Load TOP symbols from symbols.txt file.
    
    Reads from:
    1. symbols.txt in same directory as this module
    2. Falls back to empty set if file not found
    """
    symbols_path = Path(__file__).parent / "symbols.txt"
    if not symbols_path.exists():
        # Try alternate locations
        for alt_path in [Path("symbols.txt"), Path("/home/ubuntu/project/elcarobybitbotv2/symbols.txt")]:
            if alt_path.exists():
                symbols_path = alt_path
                break
    
    if symbols_path.exists():
        try:
            with open(symbols_path, "r") as f:
                return {line.strip().upper() for line in f if line.strip() and not line.startswith("#")}
        except Exception:
            pass
    return set()

# Load TOP symbols list dynamically from symbols.txt
TOP_LIST: set[str] = _load_top_symbols()

DEFAULT_LANG = 'en'

ADMIN_ID      = 511692487  # ваш Telegram-ID
GLOBAL_PAUSED = False      # если True — торговля и рассылка для всех отключены

# Position and order limits - 0 means unlimited
# Can be overridden via environment variables
MAX_OPEN_POSITIONS = int(os.getenv("MAX_OPEN_POSITIONS", "0"))  # 0 = unlimited
MAX_LIMIT_ORDERS = int(os.getenv("MAX_LIMIT_ORDERS", "0"))  # 0 = unlimited
BLACKLIST = {"FUSDT", "SKLUSDT", "BNBUSDT"}

# состояния конверса
ORDER_TYPE, ORDER_PARAMS = range(2)
CHECK_INTERVAL = 25  # секунда интервала проверки (was 15, optimized to reduce API/log load with 300+ positions)

# Проценты TP и SL для каждой монеты.
# Если монеты нет в этом словаре, будет подставлен default = 3%
COIN_PARAMS = {
    "DEFAULT": {
        "tp_pct": DEFAULT_TP_PCT,
        "sl_pct": DEFAULT_SL_PCT,
        "atr_multiplier_sl": 0.5,
        "atr_trigger_pct": DEFAULT_ATR_TRIGGER_PCT,  # 3% by default
        "atr_periods": 7,
    },
}

# TPSL и ATR для каждого таймфрейма
TIMEFRAME_PARAMS = {
    "5m": {
      "tp_pct":           DEFAULT_TP_PCT,
      "sl_pct":           DEFAULT_SL_PCT,
      "atr_periods":      7,
      "atr_multiplier_sl":0.8,
      "atr_trigger_pct":  1.0,
    },
    "15m": {
      "tp_pct":           DEFAULT_TP_PCT,
      "sl_pct":           DEFAULT_SL_PCT,
      "atr_periods":      7,
      "atr_multiplier_sl":1.0,
      "atr_trigger_pct":  1.5,
    },
    "1h": {
      "tp_pct":           DEFAULT_TP_PCT,
      "sl_pct":           DEFAULT_SL_PCT,
      "atr_periods":      3,
      "atr_multiplier_sl":0.5,
      "atr_trigger_pct":  2.5
    },
    "24h": {
      "tp_pct":           DEFAULT_TP_PCT,
      "sl_pct":           DEFAULT_SL_PCT,
      "atr_periods":      3,
      "atr_multiplier_sl":1.2,
      "atr_trigger_pct":  3.0,
    },
}
# Словарь режимов → функция проверки символа
# TOP100 is an alias for TOP for backward compatibility
SYMBOL_FILTER: dict[str, Callable[[str], bool]] = {
    "ALL":      lambda s: True,                   # всё пропускаем
    "TOP":      lambda s: s in TOP_LIST,          # только из symbols.txt
    "TOP100":   lambda s: s in TOP_LIST,          # alias для обратной совместимости
    "VOLATILE": lambda s: s not in TOP_LIST,      # всё, кроме TOP
}
# ——— дополнительные «хорошие» корни ————————————————————————
ADDITIONAL_POSITIVE = {
    'surge',      # surge | surges
    'celebrate',  # celebrate | celebrates | celebrating
    'bust',       # bust | busts
    'hit',        # hit | hits
    'record',     # record | records
    'revolution', # revolution | revolutionary
    'begin',      # begin | begins | beginning
    'production', # production | produces
    'rally',      # rally | rallies
    'growth',     # growth | grows
    'bull',       # bull | bullish
    'soar',       # soar | soars
    'gain',       # gain | gains | gained
    'jump',       # jump | jumps | jumped
    'rise',      # rise | rises | rising
    'climb',     # climb | climbs | climbing
    'rocket',    # rocket | rockets | skyrocketed
    'skyrocket', # skyrocket | skyrockets | skyrocketing
    'rebound',   # rebound | rebounds | rebounding
    'bounce',    # bounce | bounces | bouncing (bounce back)
    'success',   # success | successful
    'partner',   # partner | partners | partnership
    'adopt',     # adopt | adopts | adoption
}

# ——— дополнительные «плохие» корни ————————————————————————
ADDITIONAL_NEGATIVE = {
    'collapse',   # collapse | collapses
    'crash',      # crash | crashes
    'leak',       # leak | leaks
    'hack',       # hack | hacks
    'scam',       # scam | scams
    'fraud',      # fraud | frauds
    'backlash',   # backlash
    'outage',     # outage | outages
    'ban',        # ban | bans
    'spam',       # spam | spams
    'bear',       # bear | bearish
    'plunge',     # plunge | plunges | plunged
    'slump',      # slump | slumps | slumped
    'tumble',     # tumble | tumbles | tumbled
    'nosedive',   # nosedive | nosedives | nosedived
    'dip',        # dip | dips | dipped
    'dump',       # dump | dumps | dumping
    'crackdown',  # crackdown (crack down)
    'restrict',   # restrict | restricts | restriction
    'sanction',   # sanction | sanctions | sanctioned
    'sue',        # sue | sues | sued (lawsuit)
    'arrest',     # arrest | arrests | arrested (jail, prison)
    'sentence',   # sentence | sentenced
    'exploit',    # exploit | exploits | exploited
    'manipulate', # manipulate | manipulation
    'theft',      # theft | stolen
    'fear',       # fear | fears | fearful
    'selloff',    # sell-off | selloff
    # … добавьте другие корни по аналогии
}

# ——— базовые списки ключевых слов —————————————————————————
# Преобразуем в множества и объединяем с дополнительными корнями
POSITIVE_KEYWORDS = {
    "able", "achieve", "advantage", "advance", "aggressive", "anchor",
    "amazing", "assure", "boom", "breakthrough", "best", "better", "bold",
    "brilliant", "buoyant", "bullish", "celebrate", "certainty", "clean",
    "collaborate", "confidence", "consistent", "constructive", "credible",
    "deliver", "demand", "dynamic", "effective", "efficient", "elite",
    "empower", "enable", "enhance", "entrepreneur", "excel", "exceed",
    "expansion", "expert", "fast", "favour", "favourable", "focus",
    "forward", "fresh", "gain", "glow", "gold", "great", "growth", "healthy",
    "ideal", "improve", "improvement", "innovation", "insight", "leadership",
    "leading", "liquidity", "master", "mastery", "momentum", "opportunity",
    "optimism", "outperform", "pioneer", "premium", "prime", "proficient",
    "prosper", "quality", "rapid", "recover", "recovery", "robust", "secure",
    "spark", "spectacular", "stability", "strong", "surge", "sustain",
    "trusted", "up", "upbeat", "upgrade", "value", "vibrant", "vital",
    "win", "yield", "zeal", "zealous"
} | ADDITIONAL_POSITIVE

NEGATIVE_KEYWORDS = {
    "abandon", "bankrupt", "belie", "blockade", "boycott", "breach", "bribe",
    "burden", "collapse", "conflict", "crash", "crisis", "damage", "defect",
    "deficit", "decline", "default", "delay", "deny", "despair", "deteriorate",
    "disaster", "disclose", "disconnect", "down", "drop", "error", "evade",
    "fail", "failure", "fraud", "freeze", "friction", "harm", "hazard",
    "hesitate", "illegal", "imbalance", "impair", "impede", "impose",
    "inadequate", "incapable", "incline", "incompetent", "inflate", "injury",
    "insolvent", "instability", "interfere", "jeopardy", "lag", "lawsuit",
    "liability", "liquidation", "loss", "miss", "negative", "negligence",
    "obstacle", "outage", "overcapacity", "panic", "penalty", "plummet",
    "pollute", "poor", "problem", "prohibit", "recession", "reduce", "refuse",
    "rejection", "risk", "ruin", "scandal", "shaky", "shortfall", "stall",
    "steal", "strain", "stress", "stumble", "tarnish", "tax", "threat",
    "uncertain", "undermine", "unsafe", "unstable", "upheaval", "violate",
    "vulnerability", "weak", "withdraw", "worry", "worse", "wreck", 
    'war', 'terror', 'terrorism', 'terrorist', 'attack', 'assault',
    'explosion', 'bomb', 'bombing', 'missile', 'rocket', 'drone',
    'airstrike', 'invasion', 'conflict', 'combat', 'gunfire', 'gunshot',
    'gunman', 'shooter', 'shooting', 'sniper', 'firefight', 'massacre',
    'killing', 'kill', 'murder', 'militant', 'extremist', 'radical',
    'hostage', 'insurgent', 'ambush', 'grenade', 'IED', 'carbomb',
    'detonate', 'execute', 'execution', 'behead', 'beheading',
    'kidnap', 'abduct', 'martyr', 'casualty', 'civilian death',
    'genocide', 'atrocity', 'slaughter', 'raid', 'raid', 'air raid',
    'torture', 'siege', 'militia'
} | ADDITIONAL_NEGATIVE

# ─── Backward compatibility alias ───────────────────────────────────────────
# TOP100_LIST is deprecated, use TOP_LIST instead
# Kept for backward compatibility with old code
TOP100_LIST = TOP_LIST