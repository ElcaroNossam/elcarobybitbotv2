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
    """Create test database with schema"""
    conn = sqlite3.connect(temp_db_path)
    conn.row_factory = sqlite3.Row
    
    # Create minimal schema
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            lang TEXT DEFAULT 'en',
            api_key TEXT,
            api_secret TEXT,
            api_key_real TEXT,
            api_secret_real TEXT,
            trading_mode TEXT DEFAULT 'demo',
            balance REAL DEFAULT 0,
            percent REAL DEFAULT 1.0,
            tp_pct REAL DEFAULT 8.0,
            sl_pct REAL DEFAULT 3.0,
            leverage INTEGER DEFAULT 10,
            exchange_type TEXT DEFAULT 'bybit',
            hl_private_key TEXT,
            hl_vault_address TEXT,
            hl_testnet INTEGER DEFAULT 0,
            license_type TEXT DEFAULT 'free',
            license_expires INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS active_positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symbol TEXT,
            side TEXT,
            entry_price REAL,
            quantity REAL,
            leverage INTEGER,
            tp_price REAL,
            sl_price REAL,
            strategy TEXT,
            exchange TEXT DEFAULT 'bybit',
            account_type TEXT DEFAULT 'demo',
            opened_at INTEGER,
            UNIQUE(user_id, symbol, side, exchange, account_type)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trade_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symbol TEXT,
            side TEXT,
            entry_price REAL,
            exit_price REAL,
            quantity REAL,
            pnl REAL,
            strategy TEXT,
            exchange TEXT DEFAULT 'bybit',
            account_type TEXT DEFAULT 'demo',
            opened_at INTEGER,
            closed_at INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER,
            symbol TEXT,
            side TEXT,
            entry_price REAL,
            tp_price REAL,
            sl_price REAL,
            strategy TEXT,
            raw_text TEXT,
            created_at INTEGER
        )
    """)
    
    conn.commit()
    yield conn
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
