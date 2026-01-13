"""
PyTest Configuration and Fixtures
Shared fixtures for all tests
"""

import asyncio
import os
import pytest
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Generator, AsyncGenerator

# Test environment setup
os.environ['TESTING'] = 'true'
os.environ['JWT_SECRET'] = 'test_jwt_secret_key'
os.environ['TELEGRAM_TOKEN'] = 'test:token'


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_db_path() -> Generator[str, None, None]:
    """Create temporary database file"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture
def test_db(temp_db_path) -> Generator[sqlite3.Connection, None, None]:
    """Create test database with schema matching production"""
    conn = sqlite3.connect(temp_db_path)
    conn.row_factory = sqlite3.Row
    
    # Create full schema matching production db.py
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            lang TEXT DEFAULT 'en',
            -- Bybit API keys
            api_key TEXT,
            api_secret TEXT,
            api_key_real TEXT,
            api_secret_real TEXT,
            demo_api_key TEXT,
            demo_api_secret TEXT,
            real_api_key TEXT,
            real_api_secret TEXT,
            -- Trading settings
            trading_mode TEXT DEFAULT 'demo',
            balance REAL DEFAULT 0,
            percent REAL DEFAULT 1.0,
            coins TEXT DEFAULT 'ALL',
            tp_percent REAL DEFAULT 8.0,
            sl_percent REAL DEFAULT 3.0,
            leverage INTEGER DEFAULT 10,
            limit_enabled INTEGER DEFAULT 0,
            limit_only_default INTEGER DEFAULT 0,
            global_order_type TEXT DEFAULT 'market',
            -- Strategy toggles
            trade_oi INTEGER DEFAULT 1,
            trade_rsi_bb INTEGER DEFAULT 1,
            trade_scryptomera INTEGER DEFAULT 0,
            trade_scalper INTEGER DEFAULT 0,
            trade_elcaro INTEGER DEFAULT 0,
            trade_wyckoff INTEGER DEFAULT 0,
            strategies_enabled TEXT,
            strategies_order TEXT,
            strategy_settings TEXT,
            -- RSI/BB thresholds
            rsi_lo REAL DEFAULT 30,
            rsi_hi REAL DEFAULT 70,
            bb_touch_k REAL DEFAULT 0.8,
            oi_min_pct REAL DEFAULT 1.0,
            price_min_pct REAL DEFAULT 0.5,
            -- ATR settings
            use_atr INTEGER DEFAULT 0,
            atr_period INTEGER DEFAULT 14,
            atr_mult REAL DEFAULT 1.5,
            -- DCA settings
            dca_enabled INTEGER DEFAULT 0,
            dca_pct_1 REAL DEFAULT 5.0,
            dca_pct_2 REAL DEFAULT 10.0,
            -- Limit ladder
            limit_ladder_enabled INTEGER DEFAULT 0,
            limit_ladder_count INTEGER DEFAULT 3,
            limit_ladder_settings TEXT,
            -- Spot trading
            spot_enabled INTEGER DEFAULT 0,
            spot_settings TEXT,
            -- HyperLiquid
            exchange_type TEXT DEFAULT 'bybit',
            hl_private_key TEXT,
            hl_vault_address TEXT,
            hl_wallet_address TEXT,
            hl_testnet INTEGER DEFAULT 0,
            hl_enabled INTEGER DEFAULT 0,
            -- Exchange mode
            exchange_mode TEXT DEFAULT 'bybit',
            -- License
            license_type TEXT DEFAULT 'free',
            license_expires INTEGER,
            is_lifetime INTEGER DEFAULT 0,
            -- Access control
            is_banned INTEGER DEFAULT 0,
            is_allowed INTEGER DEFAULT 0,
            terms_accepted INTEGER DEFAULT 0,
            guide_sent INTEGER DEFAULT 0,
            -- Timestamps
            first_seen_ts INTEGER,
            last_seen_ts INTEGER,
            created_at DATETIME DEFAULT (CURRENT_TIMESTAMP)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS active_positions (
            user_id      INTEGER NOT NULL,
            symbol       TEXT    NOT NULL,
            account_type TEXT    NOT NULL DEFAULT 'demo',
            side         TEXT,
            entry_price  REAL,
            size         REAL,
            open_ts      DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
            timeframe    TEXT,
            signal_id    INTEGER,
            dca_10_done  INTEGER NOT NULL DEFAULT 0,
            dca_25_done  INTEGER NOT NULL DEFAULT 0,
            strategy     TEXT,
            source       TEXT DEFAULT 'bot',
            opened_by    TEXT,
            exchange     TEXT DEFAULT 'bybit',
            sl_price     REAL,
            tp_price     REAL,
            leverage     INTEGER,
            client_order_id TEXT,
            exchange_order_id TEXT,
            env          TEXT DEFAULT 'paper',
            manual_sltp_override INTEGER DEFAULT 0,
            manual_sltp_ts DATETIME,
            atr_activated INTEGER DEFAULT 0,
            atr_activation_price REAL,
            atr_last_stop_price REAL,
            atr_last_update_ts DATETIME,
            use_atr INTEGER DEFAULT 0,
            applied_sl_pct REAL,
            applied_tp_pct REAL,
            PRIMARY KEY(user_id, symbol, account_type),
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trade_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            signal_id INTEGER,
            symbol TEXT,
            side TEXT,
            entry_price REAL,
            exit_price REAL,
            exit_reason TEXT,
            pnl REAL,
            pnl_pct REAL,
            ts DATETIME DEFAULT (CURRENT_TIMESTAMP),
            signal_source TEXT,
            rsi REAL,
            bb_hi REAL,
            bb_lo REAL,
            oi_prev REAL,
            oi_now REAL,
            oi_chg REAL,
            vol_from REAL,
            vol_to REAL,
            price_chg REAL,
            vol_delta REAL,
            sl_pct REAL,
            tp_pct REAL,
            sl_price REAL,
            tp_price REAL,
            timeframe TEXT,
            entry_ts INTEGER,
            exit_ts INTEGER,
            exit_order_type TEXT,
            strategy TEXT,
            account_type TEXT DEFAULT 'demo'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_message TEXT,
            ts DATETIME DEFAULT (CURRENT_TIMESTAMP),
            tf TEXT,
            side TEXT,
            symbol TEXT,
            price REAL,
            oi_prev REAL,
            oi_now REAL,
            oi_chg REAL,
            vol_from REAL,
            vol_to REAL,
            price_chg REAL,
            vol_delta REAL,
            rsi REAL,
            bb_hi REAL,
            bb_lo REAL
        )
    """)
    
    # Create user_strategy_settings table for strategy-specific settings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_strategy_settings (
            user_id INTEGER NOT NULL,
            strategy TEXT NOT NULL,
            exchange TEXT NOT NULL DEFAULT 'bybit',
            account_type TEXT NOT NULL DEFAULT 'demo',
            
            -- General settings
            enabled INTEGER DEFAULT 1,
            percent REAL,
            sl_percent REAL,
            tp_percent REAL,
            leverage INTEGER,
            
            -- ATR settings
            use_atr INTEGER,
            atr_periods INTEGER,
            atr_multiplier_sl REAL,
            atr_trigger_pct REAL,
            
            -- Other settings
            order_type TEXT DEFAULT 'market',
            coins_group TEXT,
            direction TEXT DEFAULT 'all',
            trading_mode TEXT DEFAULT 'all',
            
            -- Side-specific settings for LONG
            long_percent REAL,
            long_sl_percent REAL,
            long_tp_percent REAL,
            long_atr_periods INTEGER,
            long_atr_multiplier_sl REAL,
            long_atr_trigger_pct REAL,
            
            -- Side-specific settings for SHORT
            short_percent REAL,
            short_sl_percent REAL,
            short_tp_percent REAL,
            short_atr_periods INTEGER,
            short_atr_multiplier_sl REAL,
            short_atr_trigger_pct REAL,
            
            -- Fibonacci-specific
            min_quality INTEGER DEFAULT 50,
            
            PRIMARY KEY (user_id, strategy, exchange, account_type),
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    # Custom strategies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_strategies (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            name            TEXT NOT NULL,
            description     TEXT,
            strategy_type   TEXT DEFAULT 'custom',
            config          TEXT,
            is_active       INTEGER DEFAULT 1,
            is_public       INTEGER DEFAULT 0,
            marketplace_id  INTEGER,
            performance_stats TEXT,
            win_rate        REAL DEFAULT 0,
            total_pnl       REAL DEFAULT 0,
            total_trades    INTEGER DEFAULT 0,
            backtest_score  REAL DEFAULT 0,
            created_at      INTEGER,
            updated_at      INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    # Strategy marketplace
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategy_marketplace (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy_id     INTEGER NOT NULL,
            seller_id       INTEGER NOT NULL,
            name            TEXT NOT NULL,
            description     TEXT,
            price_stars     INTEGER NOT NULL DEFAULT 100,
            price_ton       REAL NOT NULL DEFAULT 1.0,
            preview_config  TEXT,
            category        TEXT DEFAULT 'general',
            tags            TEXT,
            rating          REAL DEFAULT 0,
            rating_count    INTEGER DEFAULT 0,
            total_sales     INTEGER DEFAULT 0,
            total_revenue   REAL DEFAULT 0,
            is_active       INTEGER DEFAULT 1,
            featured        INTEGER DEFAULT 0,
            created_at      INTEGER NOT NULL,
            FOREIGN KEY(strategy_id) REFERENCES custom_strategies(id) ON DELETE CASCADE,
            FOREIGN KEY(seller_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    # Strategy purchases
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategy_purchases (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            buyer_id        INTEGER NOT NULL,
            marketplace_id  INTEGER NOT NULL,
            strategy_id     INTEGER NOT NULL,
            seller_id       INTEGER NOT NULL,
            amount_paid     REAL NOT NULL,
            currency        TEXT NOT NULL,
            seller_share    REAL NOT NULL,
            platform_share  REAL NOT NULL,
            is_active       INTEGER DEFAULT 1,
            purchased_at    INTEGER NOT NULL,
            FOREIGN KEY(buyer_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY(marketplace_id) REFERENCES strategy_marketplace(id) ON DELETE CASCADE,
            FOREIGN KEY(strategy_id) REFERENCES custom_strategies(id) ON DELETE CASCADE,
            FOREIGN KEY(seller_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    # Strategy ratings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategy_ratings (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            marketplace_id  INTEGER NOT NULL,
            user_id         INTEGER NOT NULL,
            rating          INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            review          TEXT,
            created_at      INTEGER NOT NULL,
            FOREIGN KEY(marketplace_id) REFERENCES strategy_marketplace(id) ON DELETE CASCADE,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE(marketplace_id, user_id)
        )
    """)
    
    # Seller payouts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seller_payouts (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id       INTEGER NOT NULL,
            amount          REAL NOT NULL,
            currency        TEXT NOT NULL,
            status          TEXT DEFAULT 'pending',
            tx_hash         TEXT,
            requested_at    INTEGER NOT NULL,
            processed_at    INTEGER,
            FOREIGN KEY(seller_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    # Top strategies
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS top_strategies (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy_type   TEXT NOT NULL,
            strategy_id     INTEGER,
            strategy_name   TEXT NOT NULL,
            win_rate        REAL DEFAULT 0,
            total_pnl       REAL DEFAULT 0,
            total_trades    INTEGER DEFAULT 0,
            sharpe_ratio    REAL DEFAULT 0,
            max_drawdown    REAL DEFAULT 0,
            rank            INTEGER,
            config_json     TEXT,
            updated_at      INTEGER NOT NULL
        )
    """)
    
    # Create indexes like production
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_active_user ON active_positions(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_active_account ON active_positions(user_id, account_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_flags ON users(is_banned, is_allowed)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_custom_strategies_user ON custom_strategies(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_marketplace_seller ON strategy_marketplace(seller_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payouts_seller ON seller_payouts(seller_id)")
    
    conn.commit()
    
    # IMPORTANT: Patch db module to use this temporary database
    import db as db_module
    original_db_file = db_module.DB_FILE
    db_module.DB_FILE = Path(temp_db_path)
    
    # Clear the connection pool to force new connections to temp db
    while not db_module._pool.empty():
        try:
            old_conn = db_module._pool.get_nowait()
            old_conn.close()
        except:
            pass
    
    # Run init_db() to apply all migrations and get production-like schema
    # This ensures test schema matches production exactly
    db_module.init_db()
    
    yield conn
    
    # Restore original DB_FILE
    db_module.DB_FILE = original_db_file
    conn.close()


@pytest.fixture
def test_user_id() -> int:
    """Standard test user ID"""
    return 123456789


@pytest.fixture
def test_user_data(test_db, test_user_id) -> dict:
    """Create test user in database"""
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO users (
            user_id, username, api_key, api_secret,
            balance, percent, leverage, exchange_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        test_user_id, "testuser", "test_api_key", "test_api_secret",
        10000.0, 2.0, 10, "bybit"
    ))
    test_db.commit()
    
    return {
        "user_id": test_user_id,
        "username": "testuser",
        "api_key": "test_api_key",
        "api_secret": "test_api_secret",
        "balance": 10000.0,
        "percent": 2.0,
        "leverage": 10,
        "exchange_type": "bybit"
    }


@pytest.fixture
def mock_bybit_client():
    """Mock Bybit exchange client"""
    client = AsyncMock()
    
    # Mock balance
    client.get_balance.return_value = {
        "totalWalletBalance": "10000.00",
        "totalAvailableBalance": "10000.00"
    }
    
    # Mock positions
    client.get_positions.return_value = []
    
    # Mock order placement
    client.place_order.return_value = {
        "retCode": 0,
        "result": {
            "orderId": "test-order-123",
            "orderLinkId": "test-link-123"
        }
    }
    
    # Mock price
    client.get_price.return_value = 50000.0
    
    # Mock ticker
    client.get_ticker.return_value = {
        "symbol": "BTCUSDT",
        "lastPrice": "50000.00",
        "bid1Price": "49999.00",
        "ask1Price": "50001.00"
    }
    
    return client


@pytest.fixture
def mock_hyperliquid_client():
    """Mock HyperLiquid exchange client"""
    client = AsyncMock()
    
    # Mock balance
    client.get_balance.return_value = {
        "balance": 10000.0,
        "available": 10000.0
    }
    
    # Mock positions
    client.fetch_positions.return_value = []
    
    # Mock order placement
    client.place_order.return_value = {
        "status": "ok",
        "response": {
            "type": "order",
            "data": {
                "statuses": [{
                    "filled": {"totalSz": "1.0"}
                }]
            }
        }
    }
    
    # Mock price
    client.get_price.return_value = 50000.0
    
    return client


@pytest.fixture
def mock_telegram_update():
    """Mock Telegram Update object"""
    update = MagicMock()
    update.effective_user.id = 123456789
    update.effective_user.username = "testuser"
    update.message.text = "/start"
    update.message.reply_text = AsyncMock()
    update.message.edit_text = AsyncMock()
    update.callback_query = None
    return update


@pytest.fixture
def mock_telegram_context():
    """Mock Telegram Context object"""
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    context.user_data = {}
    context.t = {}  # Translation dict
    return context


@pytest.fixture
async def mock_exchange_service():
    """Mock ExchangeService"""
    from unittest.mock import AsyncMock
    
    service = AsyncMock()
    service.get_balance.return_value = 10000.0
    service.place_order.return_value = {
        "orderId": "test-order",
        "status": "success"
    }
    service.get_positions.return_value = []
    service.close_position.return_value = True
    
    return service


@pytest.fixture
def sample_signal_data() -> dict:
    """Sample trading signal data"""
    return {
        "symbol": "BTCUSDT",
        "side": "LONG",
        "entry_price": 50000.0,
        "tp_price": 54000.0,
        "sl_price": 48500.0,
        "strategy": "elcaro",
        "leverage": 10
    }


@pytest.fixture
def sample_position_data() -> dict:
    """Sample position data"""
    return {
        "symbol": "BTCUSDT",
        "side": "LONG",
        "entry_price": 50000.0,
        "quantity": 0.1,
        "leverage": 10,
        "tp_price": 54000.0,
        "sl_price": 48500.0,
        "unrealized_pnl": 50.0,
        "pnl_percent": 1.0
    }


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis_mock = MagicMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=True)
    redis_mock.expire = AsyncMock(return_value=True)
    return redis_mock


# Cleanup fixture for cache invalidation
@pytest.fixture(autouse=True)
def clear_caches():
    """Clear all caches before each test"""
    yield
    # Clear caches after test
    try:
        from core.cache import user_config_cache, price_cache, balance_cache
        user_config_cache.cache.clear()
        price_cache.cache.clear()
        balance_cache.cache.clear()
    except:
        pass
