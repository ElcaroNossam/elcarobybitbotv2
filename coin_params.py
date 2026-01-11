# coin_params.py
import os
from pathlib import Path
from typing import Callable

DEFAULT_TP_PCT = 8.0
DEFAULT_SL_PCT = 3.0

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
CHECK_INTERVAL = 15  # секунда интервала проверки

THRESHOLD_MAP = {
    "5m":  float("inf"),
    "15m": float("inf"),
    "1h":  float("inf"),
    "4h":  float("inf"),
    "24h": float("inf"),
}
# Проценты TP и SL для каждой монеты.
# Если монеты нет в этом словаре, будет подставлен default = 3%
COIN_PARAMS = {
    "DEFAULT": {
        "tp_pct": DEFAULT_TP_PCT,
        "sl_pct": DEFAULT_SL_PCT,
        "atr_multiplier_sl": 0.3,
        "atr_trigger_pct": 3.0,
        "atr_periods": 5,
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