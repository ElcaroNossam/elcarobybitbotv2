"""
Exchange Registry - Extensible system for multiple exchanges
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class ExchangeType(str, Enum):
    """Supported exchange types"""
    BYBIT = "bybit"
    HYPERLIQUID = "hyperliquid"
    # Future exchanges:
    # BINANCE = "binance"
    # OKX = "okx"
    # DYDX = "dydx"


@dataclass
class ExchangeButton:
    """Button definition for exchange keyboard"""
    text: str
    callback: str  # Handler function name or callback_data
    row: int = 0
    requires_api: bool = False
    admin_only: bool = False


@dataclass
class ExchangeConfig:
    """Configuration for an exchange"""
    type: ExchangeType
    name: str
    icon: str
    color: str  # For UI theming
    
    # Keyboard configuration
    buttons: List[ExchangeButton] = field(default_factory=list)
    
    # Required credentials
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    
    # Features
    supports_testnet: bool = False
    supports_demo: bool = False
    supports_leverage: bool = True
    supports_tp_sl: bool = True
    supports_trailing_stop: bool = False
    is_dex: bool = False
    premium_only: bool = False
    
    # Settings keys specific to this exchange
    settings_keys: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════
# BYBIT CONFIGURATION
# ═══════════════════════════════════════════════════════════════
BYBIT_CONFIG = ExchangeConfig(
    type=ExchangeType.BYBIT,
    name="Bybit",
    icon="🟠",
    color="#F7931A",
    
    buttons=[
        # Row 0 - Exchange indicator
        ExchangeButton("🟠 Bybit", "cmd_exchange_status", row=0),
        ExchangeButton("🔄 Switch", "cmd_switch_exchange", row=0),
        
        # Row 1 - Info
        ExchangeButton("💰 Balance", "cmd_account", row=1),
        ExchangeButton("📊 Orders", "cmd_openorders", row=1),
        ExchangeButton("📈 Positions", "cmd_open_positions", row=1),
        
        # Row 2 - Stats & Market
        ExchangeButton("📊 Statistics", "cmd_trade_stats", row=2),
        ExchangeButton("📈 Market", "cmd_market", row=2),
        ExchangeButton("🌐 Language", "cmd_lang", row=2),
        
        # Row 3 - Trading Settings
        ExchangeButton("⚙️ Strategies", "cmd_strategy_settings", row=3),
        ExchangeButton("🎛️ Settings", "cmd_show_config", row=3),
        ExchangeButton("🪙 Coins", "cmd_select_coin_group", row=3),
        
        # Row 4 - API
        ExchangeButton("🔑 API Keys", "cmd_api_settings", row=4),
        
        # Row 5 - Subscribe & WebApp
        ExchangeButton("💎 Subscribe", "cmd_subscribe", row=5),
        ExchangeButton("🌐 WebApp", "cmd_webapp", row=5),
    ],
    
    required_fields=["api_key", "api_secret"],
    optional_fields=[],
    
    supports_testnet=True,
    supports_demo=True,
    supports_leverage=True,
    supports_tp_sl=True,
    supports_trailing_stop=True,
    is_dex=False,
    premium_only=False,
    
    settings_keys=[
        "percent", "leverage", "tp_percent", "sl_percent",
        "trading_mode", "use_demo", "use_real",
        "enable_scryptomera", "enable_elcaro", "enable_wyckoff", "enable_scalper",
        "limit_only", "use_oi", "use_rsi_bb", "use_atr",
        "demo_api_key", "demo_api_secret", "real_api_key", "real_api_secret"
    ]
)


# ═══════════════════════════════════════════════════════════════
# HYPERLIQUID CONFIGURATION
# ═══════════════════════════════════════════════════════════════
HYPERLIQUID_CONFIG = ExchangeConfig(
    type=ExchangeType.HYPERLIQUID,
    name="HyperLiquid",
    icon="🔷",
    color="#00D4FF",
    
    buttons=[
        # Row 0 - Exchange indicator
        ExchangeButton("🔷 HyperLiquid", "cmd_exchange_status", row=0),
        ExchangeButton("🔄 Switch", "cmd_switch_exchange", row=0),
        
        # Row 1 - Info
        ExchangeButton("💰 Balance", "cmd_hl_balance", row=1),
        ExchangeButton("📊 Positions", "cmd_hl_positions", row=1),
        ExchangeButton("📈 Orders", "cmd_hl_orders", row=1),
        
        # Row 2 - Trading
        ExchangeButton("🎯 Trade", "cmd_hl_trade", row=2),
        ExchangeButton("❌ Close All", "cmd_hl_close_all", row=2),
        ExchangeButton("📋 History", "cmd_hl_history", row=2),
        
        # Row 3 - Settings
        ExchangeButton("⚙️ Settings", "cmd_hl_config", row=3),
        ExchangeButton("🌐 Language", "cmd_lang", row=3),
        ExchangeButton("🔑 API", "cmd_hl_settings", row=3),
        
        # Row 4 - Subscribe & WebApp
        ExchangeButton("💎 Subscribe", "cmd_subscribe", row=4),
        ExchangeButton("🌐 WebApp", "cmd_webapp", row=4),
    ],
    
    required_fields=["private_key"],
    optional_fields=["wallet_address", "vault_address"],
    
    supports_testnet=True,
    supports_demo=False,
    supports_leverage=True,
    supports_tp_sl=True,
    supports_trailing_stop=False,
    is_dex=True,
    premium_only=True,
    
    settings_keys=[
        "hl_percent", "hl_leverage", "hl_tp_percent", "hl_sl_percent",
        "hl_private_key", "hl_wallet_address", "hl_vault_address", "hl_testnet",
        "hl_enable_signals", "hl_auto_trade"
    ]
)


# ═══════════════════════════════════════════════════════════════
# EXCHANGE REGISTRY
# ═══════════════════════════════════════════════════════════════
class ExchangeRegistry:
    """Registry of all supported exchanges"""
    
    _exchanges: Dict[ExchangeType, ExchangeConfig] = {
        ExchangeType.BYBIT: BYBIT_CONFIG,
        ExchangeType.HYPERLIQUID: HYPERLIQUID_CONFIG,
    }
    
    @classmethod
    def get(cls, exchange_type: str) -> Optional[ExchangeConfig]:
        """Get exchange config by type string"""
        try:
            et = ExchangeType(exchange_type)
            return cls._exchanges.get(et)
        except ValueError:
            return None
    
    @classmethod
    def get_all(cls) -> List[ExchangeConfig]:
        """Get all exchange configs"""
        return list(cls._exchanges.values())
    
    @classmethod
    def get_types(cls) -> List[str]:
        """Get all exchange type strings"""
        return [e.value for e in cls._exchanges.keys()]
    
    @classmethod
    def register(cls, config: ExchangeConfig):
        """Register a new exchange"""
        cls._exchanges[config.type] = config
    
    @classmethod
    def get_keyboard_rows(cls, exchange_type: str) -> Dict[int, List[ExchangeButton]]:
        """Get buttons organized by row"""
        config = cls.get(exchange_type)
        if not config:
            return {}
        
        rows: Dict[int, List[ExchangeButton]] = {}
        for btn in config.buttons:
            if btn.row not in rows:
                rows[btn.row] = []
            rows[btn.row].append(btn)
        
        return rows
    
    @classmethod
    def get_settings_keys(cls, exchange_type: str) -> List[str]:
        """Get settings keys for an exchange"""
        config = cls.get(exchange_type)
        return config.settings_keys if config else []
    
    @classmethod
    def is_premium_required(cls, exchange_type: str) -> bool:
        """Check if exchange requires premium"""
        config = cls.get(exchange_type)
        return config.premium_only if config else False


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════
def get_exchange_icon(exchange_type: str) -> str:
    """Get exchange icon emoji"""
    config = ExchangeRegistry.get(exchange_type)
    return config.icon if config else "❓"


def get_exchange_name(exchange_type: str) -> str:
    """Get exchange display name"""
    config = ExchangeRegistry.get(exchange_type)
    return config.name if config else exchange_type.upper()


def get_exchange_color(exchange_type: str) -> str:
    """Get exchange brand color"""
    config = ExchangeRegistry.get(exchange_type)
    return config.color if config else "#FFFFFF"


def get_switch_button_text(current_exchange: str) -> str:
    """Get text for switch button based on current exchange"""
    exchanges = ExchangeRegistry.get_types()
    current_idx = exchanges.index(current_exchange) if current_exchange in exchanges else 0
    next_idx = (current_idx + 1) % len(exchanges)
    next_exchange = exchanges[next_idx]
    next_config = ExchangeRegistry.get(next_exchange)
    
    if next_config:
        return f"🔄 → {next_config.icon} {next_config.name}"
    return "🔄 Switch"


def get_next_exchange(current_exchange: str) -> str:
    """Get next exchange in rotation"""
    exchanges = ExchangeRegistry.get_types()
    current_idx = exchanges.index(current_exchange) if current_exchange in exchanges else 0
    next_idx = (current_idx + 1) % len(exchanges)
    return exchanges[next_idx]
