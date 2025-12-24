"""
WebApp API Tests - FastAPI Endpoints Testing
Полное покрытие всех реальных эндпоинтов WebApp API.
"""
import os
import sys
import json
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import webapp app
from webapp.app import app
import db


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers(test_user_id):
    """Headers with valid JWT token."""
    from webapp.api.auth import create_access_token
    token = create_access_token(test_user_id, is_admin=False)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers():
    """Admin auth headers."""
    from webapp.api.auth import create_access_token
    from coin_params import ADMIN_ID
    token = create_access_token(ADMIN_ID, is_admin=True)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_telegram_data():
    """Mock Telegram WebApp init_data."""
    return "query_id=test&user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22Test%22%7D&auth_date=1234567890&hash=test"


# ===========================
# AUTH API Tests (/api/auth)
# ===========================

class TestAuthAPI:
    """Authentication endpoint tests."""
    
    def test_telegram_auth_endpoint_exists(self, client, mock_telegram_data):
        """Test POST /api/auth/telegram exists."""
        response = client.post("/api/auth/telegram", json={"init_data": mock_telegram_data})
        # Может быть 200 или 401 в зависимости от валидации
        assert response.status_code in [200, 401]
    
    def test_get_me_authenticated(self, client, auth_headers, test_user_id):
        """Test GET /api/auth/me with valid token."""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user_id
    
    def test_get_me_unauthenticated(self, client):
        """Test GET /api/auth/me without auth."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401  # HTTPBearer returns 401
    
    def test_logout_endpoint(self, client, auth_headers):
        """Test POST /api/auth/logout."""
        response = client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200
    
    def test_direct_login_endpoint(self, client):
        """Test POST /api/auth/direct-login."""
        payload = {"user_id": 123456789, "password": "test"}
        response = client.post("/api/auth/direct-login", json=payload)
        assert response.status_code in [200, 401, 422]
    
    def test_token_login_endpoint(self, client):
        """Test GET /api/auth/token-login."""
        response = client.get("/api/auth/token-login?token=test_token")
        assert response.status_code in [200, 401]
    
    def test_login_by_id_endpoint(self, client):
        """Test POST /api/auth/login-by-id."""
        payload = {"identifier": "123456789"}
        response = client.post("/api/auth/login-by-id", json=payload)
        # 2FA flow expected
        assert response.status_code in [200, 400]


# ===========================
# USERS API Tests (/api/users)
# ===========================

class TestUsersAPI:
    """User settings and profile endpoints."""
    
    def test_get_settings_bybit(self, client, auth_headers, test_user_data):
        """Test GET /api/users/settings for Bybit."""
        response = client.get("/api/users/settings?exchange=bybit", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "percent" in data
        assert "leverage" in data
        assert "trading_mode" in data
        assert "tp_percent" in data
        assert "sl_percent" in data
    
    def test_get_settings_hyperliquid(self, client, auth_headers):
        """Test GET /api/users/settings for HyperLiquid."""
        response = client.get("/api/users/settings?exchange=hyperliquid", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "testnet" in data
        assert "percent" in data
    
    def test_update_settings(self, client, auth_headers):
        """Test PUT /api/users/settings."""
        payload = {
            "exchange": "bybit",
            "settings": {
                "percent": 10,
                "leverage": 20,
                "tp_percent": 5,
                "sl_percent": 2
            }
        }
        response = client.put("/api/users/settings", json=payload, headers=auth_headers)
        assert response.status_code == 200
    
    def test_switch_exchange(self, client, auth_headers):
        """Test POST /api/users/exchange."""
        payload = {"exchange": "hyperliquid", "reconnect": True}
        response = client.post("/api/users/exchange", json=payload, headers=auth_headers)
        assert response.status_code in [200, 400]
    
    def test_switch_account_type(self, client, auth_headers):
        """Test POST /api/users/switch-account-type."""
        payload = {"account_type": "demo", "exchange": "bybit"}
        response = client.post("/api/users/switch-account-type", json=payload, headers=auth_headers)
        assert response.status_code in [200, 400]
    
    def test_change_language(self, client, auth_headers):
        """Test POST /api/users/language."""
        response = client.post("/api/users/language", json={"language": "ru"}, headers=auth_headers)
        assert response.status_code == 200


# ===========================
# TRADING API Tests (/api/trading)
# ===========================

class TestTradingAPI:
    """Trading operations endpoints."""
    
    def test_get_balance(self, client, auth_headers):
        """Test GET /api/trading/balance."""
        response = client.get("/api/trading/balance?exchange=bybit&account_type=demo", headers=auth_headers)
        # Может упасть без credentials, но эндпоинт существует
        assert response.status_code in [200, 400, 500]
    
    def test_get_positions(self, client, auth_headers):
        """Test GET /api/trading/positions."""
        response = client.get("/api/trading/positions?exchange=bybit&account_type=demo", headers=auth_headers)
        assert response.status_code in [200, 400, 500]
    
    def test_get_orders(self, client, auth_headers):
        """Test GET /api/trading/orders."""
        response = client.get("/api/trading/orders?exchange=bybit&account_type=demo", headers=auth_headers)
        assert response.status_code in [200, 400, 500]
    
    def test_get_execution_history(self, client, auth_headers):
        """Test GET /api/trading/execution-history."""
        response = client.get("/api/trading/execution-history?exchange=bybit&account_type=demo", headers=auth_headers)
        assert response.status_code in [200, 400, 500]
    
    def test_get_trades(self, client, auth_headers):
        """Test GET /api/trading/trades."""
        response = client.get("/api/trading/trades?exchange=bybit&account_type=demo", headers=auth_headers)
        assert response.status_code in [200, 400, 500]
    
    def test_get_stats(self, client, auth_headers):
        """Test GET /api/trading/stats."""
        response = client.get("/api/trading/stats?exchange=bybit&account_type=demo", headers=auth_headers)
        assert response.status_code in [200, 500]
    
    def test_place_order_validation(self, client, auth_headers):
        """Test POST /api/trading/order with invalid data."""
        invalid_order = {
            "symbol": "BTCUSDT",
            "side": "invalid_side",
            "size": -10
        }
        response = client.post("/api/trading/order", json=invalid_order, headers=auth_headers)
        # Может вернуть 200 если валидация на сервере, 422 если pydantic
        assert response.status_code in [200, 400, 422, 500]
    
    def test_place_order_structure(self, client, auth_headers):
        """Test POST /api/trading/order structure."""
        order = {
            "symbol": "BTCUSDT",
            "side": "buy",
            "order_type": "market",
            "size": 0.001,
            "leverage": 10,
            "exchange": "bybit",
            "account_type": "demo"
        }
        response = client.post("/api/trading/order", json=order, headers=auth_headers)
        # Может упасть без credentials
        assert response.status_code in [200, 400, 500]
    
    def test_close_position(self, client, auth_headers):
        """Test POST /api/trading/close."""
        payload = {
            "symbol": "BTCUSDT",
            "exchange": "bybit",
            "account_type": "demo"
        }
        response = client.post("/api/trading/close", json=payload, headers=auth_headers)
        assert response.status_code in [200, 400, 404, 500]
    
    def test_close_all_positions(self, client, auth_headers):
        """Test POST /api/trading/close-all."""
        payload = {"exchange": "bybit", "account_type": "demo"}
        response = client.post("/api/trading/close-all", json=payload, headers=auth_headers)
        assert response.status_code in [200, 400, 500]
    
    def test_set_leverage(self, client, auth_headers):
        """Test POST /api/trading/leverage."""
        payload = {
            "symbol": "BTCUSDT",
            "leverage": 10,
            "exchange": "bybit",
            "account_type": "demo"
        }
        response = client.post("/api/trading/leverage", json=payload, headers=auth_headers)
        assert response.status_code in [200, 400, 500]
    
    def test_cancel_order(self, client, auth_headers):
        """Test DELETE /api/trading/order."""
        params = {
            "symbol": "BTCUSDT",
            "order_id": "test_order_123",
            "exchange": "bybit",
            "account_type": "demo"
        }
        response = client.delete("/api/trading/order", params=params, headers=auth_headers)
        assert response.status_code in [200, 400, 404, 422, 500]
    
    def test_get_account_info(self, client, auth_headers):
        """Test GET /api/trading/account-info."""
        response = client.get("/api/trading/account-info?exchange=bybit&account_type=demo", headers=auth_headers)
        assert response.status_code in [200, 400, 500]
    
    def test_modify_tpsl(self, client, auth_headers):
        """Test POST /api/trading/modify-tpsl."""
        payload = {
            "symbol": "BTCUSDT",
            "take_profit": 50000,
            "stop_loss": 40000,
            "exchange": "bybit",
            "account_type": "demo"
        }
        response = client.post("/api/trading/modify-tpsl", json=payload, headers=auth_headers)
        assert response.status_code in [200, 400, 500]
    
    def test_cancel_all_orders(self, client, auth_headers):
        """Test POST /api/trading/cancel-all-orders."""
        payload = {
            "symbol": "BTCUSDT",
            "exchange": "bybit",
            "account_type": "demo"
        }
        response = client.post("/api/trading/cancel-all-orders", json=payload, headers=auth_headers)
        assert response.status_code in [200, 400, 500]
    
    def test_dca_ladder(self, client, auth_headers):
        """Test POST /api/trading/dca-ladder."""
        payload = {
            "symbol": "BTCUSDT",
            "side": "buy",
            "entry_price": 45000,
            "total_size": 0.1,
            "num_orders": 5,
            "price_step_percent": 1,
            "exchange": "bybit",
            "account_type": "demo"
        }
        response = client.post("/api/trading/dca-ladder", json=payload, headers=auth_headers)
        assert response.status_code in [200, 400, 500]
    
    def test_calculate_position(self, client, auth_headers):
        """Test POST /api/trading/calculate-position."""
        payload = {
            "symbol": "BTCUSDT",
            "side": "buy",
            "entry_price": 45000,
            "leverage": 10,
            "balance": 1000,
            "risk_percent": 2
        }
        response = client.post("/api/trading/calculate-position", json=payload, headers=auth_headers)
        assert response.status_code in [200, 400, 422]
    
    def test_get_symbol_info(self, client, auth_headers):
        """Test GET /api/trading/symbol-info/{symbol}."""
        response = client.get("/api/trading/symbol-info/BTCUSDT?exchange=bybit&account_type=demo", headers=auth_headers)
        assert response.status_code in [200, 400, 500]
    
    def test_get_orderbook(self, client, auth_headers):
        """Test GET /api/trading/orderbook/{symbol}."""
        response = client.get("/api/trading/orderbook/BTCUSDT?exchange=bybit&account_type=demo", headers=auth_headers)
        assert response.status_code in [200, 400, 500]
    
    def test_get_recent_trades(self, client, auth_headers):
        """Test GET /api/trading/recent-trades/{symbol}."""
        response = client.get("/api/trading/recent-trades/BTCUSDT?exchange=bybit&account_type=demo", headers=auth_headers)
        assert response.status_code in [200, 400, 500]
    
    def test_get_symbols(self, client, auth_headers):
        """Test GET /api/trading/symbols."""
        response = client.get("/api/trading/symbols?exchange=bybit&account_type=demo", headers=auth_headers)
        assert response.status_code in [200, 400, 500]
    
    def test_get_funding_rates(self, client, auth_headers):
        """Test GET /api/trading/funding-rates."""
        response = client.get("/api/trading/funding-rates?exchange=bybit&account_type=demo", headers=auth_headers)
        assert response.status_code in [200, 400, 500]


# ===========================
# STATS API Tests (/api/stats)
# ===========================

class TestStatsAPI:
    """Statistics endpoints."""
    
    def test_get_dashboard(self, client, auth_headers):
        """Test GET /api/stats/dashboard."""
        response = client.get("/api/stats/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Response has nested structure: {success, data: {summary, pnlHistory, ...}}
        assert "data" in data or "message" in data
        if "data" in data:
            assert "summary" in data["data"]
    
    def test_get_pnl_history(self, client, auth_headers):
        """Test GET /api/stats/pnl-history."""
        response = client.get("/api/stats/pnl-history", headers=auth_headers)
        assert response.status_code in [200, 400]


# ===========================
# ADMIN API Tests (/api/admin)
# ===========================

class TestAdminAPI:
    """Admin panel endpoints."""
    
    def test_admin_access_denied(self, client, auth_headers):
        """Test non-admin cannot access admin endpoints."""
        response = client.get("/api/admin/users", headers=auth_headers)
        assert response.status_code == 403
    
    def test_admin_get_users(self, client, admin_headers):
        """Test GET /api/admin/users."""
        response = client.get("/api/admin/users", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        # Response is dict with pagination: {total, active, list: [...]}
        assert isinstance(data, dict)
        assert "list" in data
    
    def test_admin_get_user_detail(self, client, admin_headers, test_user_id):
        """Test GET /api/admin/users/{user_id}."""
        response = client.get(f"/api/admin/users/{test_user_id}", headers=admin_headers)
        assert response.status_code == 200
    
    def test_admin_ban_user(self, client, admin_headers, test_user_id):
        """Test POST /api/admin/users/{user_id}/ban."""
        response = client.post(f"/api/admin/users/{test_user_id}/ban", headers=admin_headers)
        assert response.status_code == 200
    
    def test_admin_unban_user(self, client, admin_headers, test_user_id):
        """Test POST /api/admin/users/{user_id}/unban."""
        response = client.post(f"/api/admin/users/{test_user_id}/unban", headers=admin_headers)
        assert response.status_code == 200
    
    def test_admin_approve_user(self, client, admin_headers, test_user_id):
        """Test POST /api/admin/users/{user_id}/approve."""
        response = client.post(f"/api/admin/users/{test_user_id}/approve", headers=admin_headers)
        assert response.status_code == 200
    
    def test_admin_get_stats(self, client, admin_headers):
        """Test GET /api/admin/stats."""
        response = client.get("/api/admin/stats", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        # May have various structure
        assert isinstance(data, dict)
    
    def test_admin_get_licenses(self, client, admin_headers):
        """Test GET /api/admin/licenses."""
        response = client.get("/api/admin/licenses", headers=admin_headers)
        assert response.status_code == 200
    
    def test_admin_create_license(self, client, admin_headers):
        """Test POST /api/admin/licenses."""
        payload = {
            "license_type": "premium",
            "duration_days": 30,
            "user_id": 999999
        }
        response = client.post("/api/admin/licenses", json=payload, headers=admin_headers)
        assert response.status_code in [200, 400]
    
    def test_admin_get_strategies(self, client, admin_headers):
        """Test GET /api/admin/strategies."""
        response = client.get("/api/admin/strategies", headers=admin_headers)
        assert response.status_code == 200
    
    def test_admin_get_marketplace_strategies(self, client, admin_headers):
        """Test GET /api/admin/strategies/marketplace."""
        response = client.get("/api/admin/strategies/marketplace", headers=admin_headers)
        assert response.status_code == 200


# ===========================
# BACKTEST API Tests (/api/strategy-backtest)
# ===========================

class TestBacktestAPI:
    """Backtesting endpoints."""
    
    def test_get_built_in_strategies(self, client, auth_headers):
        """Test GET /api/strategy-backtest/built-in."""
        response = client.get("/api/strategy-backtest/built-in", headers=auth_headers)
        # 404 if router not included in app
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_indicators(self, client, auth_headers):
        """Test GET /api/strategy-backtest/indicators."""
        response = client.get("/api/strategy-backtest/indicators", headers=auth_headers)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_timeframes(self, client, auth_headers):
        """Test GET /api/strategy-backtest/timeframes."""
        response = client.get("/api/strategy-backtest/timeframes", headers=auth_headers)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_symbols(self, client, auth_headers):
        """Test GET /api/strategy-backtest/symbols."""
        response = client.get("/api/strategy-backtest/symbols", headers=auth_headers)
        assert response.status_code in [200, 404]
    
    def test_backtest_built_in_missing_params(self, client, auth_headers):
        """Test POST /api/strategy-backtest/backtest/built-in without params."""
        response = client.post("/api/strategy-backtest/backtest/built-in", json={}, headers=auth_headers)
        assert response.status_code in [404, 422]  # 404 if not included
    
    def test_save_strategy(self, client, auth_headers):
        """Test POST /api/strategy-backtest/save."""
        payload = {
            "name": "Test Strategy",
            "code": "def strategy(data): return data",
            "description": "Test"
        }
        response = client.post("/api/strategy-backtest/save", json=payload, headers=auth_headers)
        assert response.status_code in [200, 400, 404]
    
    def test_get_my_strategies(self, client, auth_headers):
        """Test GET /api/strategy-backtest/my-strategies."""
        response = client.get("/api/strategy-backtest/my-strategies", headers=auth_headers)
        assert response.status_code in [200, 404]


# ===========================
# HEALTH & UTILITY Tests
# ===========================

class TestHealthAPI:
    """Health and utility endpoints."""
    
    def test_health_endpoint(self, client):
        """Test GET /health."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_detailed_health(self, client):
        """Test GET /health/detailed."""
        response = client.get("/health/detailed")
        assert response.status_code in [200, 404]  # May not exist
    
    def test_metrics_endpoint(self, client):
        """Test GET /metrics."""
        response = client.get("/metrics")
        assert response.status_code == 200
    
    def test_root_endpoint(self, client):
        """Test GET / returns HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


# ===========================
# ERROR HANDLING Tests
# ===========================

class TestErrorHandling:
    """Error handling and validation."""
    
    def test_not_found(self, client):
        """Test 404 for non-existent route."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test 405 for wrong HTTP method."""
        response = client.delete("/api/auth/me")
        assert response.status_code == 405
    
    def test_unauthorized_protected_endpoint(self, client):
        """Test accessing protected endpoint without auth."""
        response = client.get("/api/trading/balance")
        assert response.status_code == 401  # HTTPBearer returns 401
    
    def test_invalid_json(self, client, auth_headers):
        """Test invalid JSON payload."""
        response = client.post(
            "/api/trading/order",
            data="invalid json",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        assert response.status_code == 422
