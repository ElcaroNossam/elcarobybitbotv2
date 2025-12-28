# coin_params.py
import os
from typing import Callable

DEFAULT_TP_PCT = 8.0
DEFAULT_SL_PCT = 3.0

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
SYMBOL_FILTER: dict[str, Callable[[str], bool]] = {
    "ALL":      lambda s: True,                   # всё пропускаем
    "TOP100":   lambda s: s in TOP100_LIST,       # только топ-100
    "VOLATILE": lambda s: s not in TOP100_LIST,   # всё, кроме топ-100
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

# Ваш заранее заполненный список топ-100 по капитализации:
TOP100_LIST = [
    "1000BONKUSDT",
    "1000FLOKIUSDT",
    "1000PEPEUSDT",
    "1000RATSUSDT",
    "1INCHUSDT",
    "AAVEUSDT",
    "ABUSDT",
    "ADAUSDT",
    "AEROUSDT",
    "ALGOUSDT",
    "ANKRUSDT",
    "APTUSDT",
    "ARBUSDT",
    "ARKMUSDT",
    "ARKUSDT",
    "ATOMUSDT",
    "AUCTIONUSDT",
    "AVAXUSDT",
    "BCHUSDT",
    "BLURUSDT",
    "BNBUSDT",
    "BONKUSDT",
    "BSVUSDT",
    "CAKEUSDT",
    "C98USDT",
    "COMPUSDT",
    "COSUSDT",
    "CRVUSDT",
    "DAIUSDT",
    "DEXEUSDT",
    "DOTUSDT",
    "DUCKUSDT",
    "DYDXUSDT",
    "ELXUSDT",
    "ENAUSDT",
    "ENJUSDT",
    "ENSUSDT",
    "ETHUSDT",
    "FARTCOINUSDT",  # проверьте точное написание
    "FETUSDT",
    "FILUSDT",
    "FLOKIUSDT",  # проверьте FLOKIUSDT
    "FORMUSDT",
    "FTDUSDUSDT",  # проверьте FDUSDUSDT
    "GALAUSDT",
    "GIGAUSDT",
    "GNTUSDT",  # если нужен GNT
    "GRTUSDT",
    "GRASSUSDT",
    "GTUSDT",
    "HBARUSDT",  # проверьте HBARUSDT
    "HIPPOUSDT",
    "HYPEUSDT",  # проверьте HYPEUSDT
    "ICPUSDT",
    "IOTAUSDT",
    "IPUSDT",
    "INJUSDT",
    "IPTUSDT",  # проверьте IMXUSDT
    "JASMYUSDT",
    "JTOUSDT",
    "JUPUSDT",
    "KAVAUSDT",
    "KAIAUSDT",
    "KCSUSDT",
    "LINKUSDT",
    "LDOUSDT",
    "LEOUSDT",
    "LTCUSDT",
    "LPTUSDT",
    "MANAUSDT",
    "MATICUSDT",  # если нужен MATIC
    "MNTUSDT",
    "MYRIAUSDT",
    "NEARUSDT",
    "NEXOUSDT",
    "NOTUSDT",
    "OKBUSDT",
    "OPUSDT",
    "ORDIUSDT",
    "OSMOUSDT",
    "PAXGUSDT",
    "PEPEUSDT",
    "PENGUUSDT",
    "PIUSDT",
    "PIUSDT",  # проверьте PIUSDT
    "POPCATUSDT",
    "PORTALUSDT",
    "PYUSDUSDT",
    "QNTUSDT",
    "RENDERUSDT",
    "RNDRUSDT",  # если нужен RNDRUSDT
    "SEIUSDT",
    "SHIBUSDT",
    "SKYUSDT",
    "SANDUSDT",
    "SOLUSDT",
    "SPXUSDT",
    "SOPHUSDT",
    "SUIUSDT",
    "SUSHIUSDT",
    "SYRUPUSDT",
    "TAIKOUSDT",
    "TAOUSDT",
    "TIAUSDT",
    "TONUSDT",
    "TRXUSDT",
    "USDCUSDT",
    "USDEUSDT",
    "USDTUSDT",
    "USD1USDT",
    "VETUSDT",
    "VIRTUALUSDT",
    "WIFUSDT",
    "WLDUSDT",
    "XAUTUSDT",
    "XLMUSDT",
    "XMRUSDT",
    "XRPUSDT",
    "XDCUSDT",
    "ZECUSDT",
    "ZROUSDT"
]