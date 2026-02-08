"""
HyperLiquid Constants and Configuration
"""

# API URLs
MAINNET_API_URL = "https://api.hyperliquid.xyz"
TESTNET_API_URL = "https://api.hyperliquid-testnet.xyz"

# WebSocket URLs
MAINNET_WS_URL = "wss://api.hyperliquid.xyz/ws"
TESTNET_WS_URL = "wss://api.hyperliquid-testnet.xyz/ws"

# Coin to Asset Index Mapping
COIN_TO_ASSET = {
    "BTC": 0, "ETH": 1, "SOL": 2, "AVAX": 3, "ARB": 4,
    "DOGE": 5, "LTC": 6, "MATIC": 7, "LINK": 8, "BNB": 9,
    "OP": 10, "ATOM": 11, "APE": 12, "NEAR": 13, "FTM": 14,
    "AAVE": 15, "DOT": 16, "UNI": 17, "BCH": 18, "TRX": 19,
    "APT": 20, "XRP": 21, "LDO": 22, "CRV": 23, "SUI": 24,
    "RNDR": 25, "INJ": 26, "GMX": 27, "SNX": 28, "STX": 29,
    "MKR": 30, "COMP": 31, "FXS": 32, "DYDX": 33, "WLD": 34,
    "BLUR": 35, "CFX": 36, "ORDI": 37, "PEPE": 38, "SHIB": 39,
    "SEI": 40, "FLOKI": 41, "TIA": 42, "PYTH": 43, "JTO": 44,
    "BONK": 45, "WIF": 46, "JUP": 47, "STRK": 48, "MANTA": 49,
    "DYM": 50, "PIXEL": 51, "ALT": 52, "PORTAL": 53, "ENA": 54,
    "W": 55, "REZ": 56, "LISTA": 57, "ZRO": 58, "BLAST": 59,
    "IO": 60, "ZK": 61, "MERL": 62, "TRUMP": 63, "MELANIA": 64,
    "XLM": 65, "ETC": 66, "HBAR": 67, "FIL": 68, "RUNE": 69,
    "ICP": 70, "SAND": 71, "MANA": 72, "AXS": 73, "KAS": 74,
    "TAO": 75, "PENDLE": 76, "TON": 77, "POPCAT": 78, "WEN": 79,
    "MYRO": 80, "ONDO": 81, "ETHFI": 82, "KMNO": 83, "PEOPLE": 84,
    "NEIRO": 85, "SYN": 86, "MOTHER": 87, "BRETT": 88, "MOG": 89,
    "GOAT": 90, "MOODENG": 91, "PNUT": 92, "ACT": 93, "HIPPO": 94,
    "VIRTUAL": 95, "AI16Z": 96, "GRASS": 97, "ME": 98, "MOVE": 99,
    "HYPE": 100, "ZEREBRO": 101, "AIXBT": 102, "FARTCOIN": 103,
    "SPX": 104, "ADA": 105, "OMNI": 106, "BB": 107, "NOT": 108,
    "TURBO": 109, "DOGS": 110, "HMSTR": 111, "EIGEN": 112, "POL": 113,
    "DRIFT": 114, "DEEP": 115, "VVAIFU": 116, "ELIZA": 117, "GRIFFAIN": 118,
    "BIO": 119, "SWARMS": 120, "SONIC": 121, "PENGU": 122, "XAI": 123,
}

# Reverse mapping
ASSET_TO_COIN = {v: k for k, v in COIN_TO_ASSET.items()}

# Size decimals per coin
SIZE_DECIMALS = {
    "BTC": 5, "ETH": 4, "SOL": 2, "DOGE": 0, "SHIB": 0,
    "PEPE": 0, "BONK": 0, "FLOKI": 0, "WIF": 1, "POPCAT": 1,
}

DEFAULT_SIZE_DECIMALS = 2

def get_size_decimals(coin: str) -> int:
    return SIZE_DECIMALS.get(coin.upper(), DEFAULT_SIZE_DECIMALS)

def coin_to_asset_id(coin: str) -> int:
    """Convert coin name to asset ID.
    
    Supports:
    - Perp coins: BTC, ETH, BTCUSDT, etc. -> 0, 1, ...
    - Spot tokens: @0, @1, etc. -> 10000, 10001, ... (spot asset = 10000 + pair_index)
    """
    # Spot token format: @INDEX (e.g. @0 for PURR/USDC)
    if coin.startswith("@"):
        try:
            pair_index = int(coin[1:])
            return 10000 + pair_index  # Spot asset IDs start at 10000
        except ValueError:
            return None
    
    clean_coin = coin.upper().replace("USDT", "").replace("USDC", "").replace("PERP", "")
    return COIN_TO_ASSET.get(clean_coin)

def asset_id_to_coin(asset_id: int) -> str:
    return ASSET_TO_COIN.get(asset_id)
