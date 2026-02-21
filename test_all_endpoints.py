#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all endpoints of the Enliko Trading Platform
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://enliko.com/api"
VERBOSE = True

# Test results
results = {
    "passed": [],
    "failed": [],
    "skipped": []
}

def log(msg, level="INFO"):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")

def test_endpoint(method, endpoint, expected_codes=[200], data=None, headers=None, auth_token=None, name=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    test_name = name or f"{method.upper()} {endpoint}"
    
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        if method.lower() == "get":
            resp = requests.get(url, headers=headers, timeout=30)
        elif method.lower() == "post":
            resp = requests.post(url, json=data, headers=headers, timeout=30)
        elif method.lower() == "put":
            resp = requests.put(url, json=data, headers=headers, timeout=30)
        elif method.lower() == "delete":
            resp = requests.delete(url, headers=headers, timeout=30)
        else:
            log(f"Unknown method: {method}", "ERROR")
            results["skipped"].append(test_name)
            return None
        
        if resp.status_code in expected_codes:
            log(f"✅ {test_name} → {resp.status_code}", "PASS")
            results["passed"].append(test_name)
            return resp
        else:
            log(f"❌ {test_name} → {resp.status_code} (expected {expected_codes})", "FAIL")
            if VERBOSE:
                try:
                    log(f"   Response: {resp.text[:200]}", "DEBUG")
                except:
                    pass
            results["failed"].append((test_name, resp.status_code, resp.text[:200] if resp.text else ""))
            return resp
            
    except requests.exceptions.Timeout:
        log(f"⏱️ {test_name} → TIMEOUT", "FAIL")
        results["failed"].append((test_name, "TIMEOUT", ""))
        return None
    except Exception as e:
        log(f"💥 {test_name} → {str(e)}", "FAIL")
        results["failed"].append((test_name, "EXCEPTION", str(e)))
        return None

def test_public_endpoints():
    """Test endpoints that don't require authentication"""
    log("=" * 60)
    log("TESTING PUBLIC ENDPOINTS")
    log("=" * 60)
    
    # Health check (NOT under /api)
    url = "https://enliko.com/health"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            log(f"✅ GET /health → 200", "PASS")
            results["passed"].append("GET /health")
        else:
            log(f"❌ GET /health → {resp.status_code}", "FAIL")
            results["failed"].append(("GET /health", resp.status_code, ""))
    except Exception as e:
        log(f"💥 GET /health → {e}", "FAIL")
        results["failed"].append(("GET /health", "EXCEPTION", str(e)))
    
    # Screener (correct paths)
    test_endpoint("get", "/screener/symbols", [200])
    test_endpoint("get", "/screener/overview", [200])
    test_endpoint("get", "/screener/symbol/BTCUSDT", [200])
    
    # Marketplace (correct path with doubled prefix)
    test_endpoint("get", "/marketplace/marketplace", [200])
    test_endpoint("get", "/marketplace/market/overview", [200])
    test_endpoint("get", "/marketplace/indicators", [200])
    test_endpoint("get", "/marketplace/rankings/top", [200])
    
    # Stats
    test_endpoint("get", "/stats/leaderboard", [200])
    
    # TON payments plans (public)
    test_endpoint("get", "/payments/plans", [200])
    
    # Crypto payments (public)
    test_endpoint("get", "/crypto/plans", [200])
    test_endpoint("get", "/crypto/currencies", [200])
    
    # Backtest public
    test_endpoint("get", "/backtest/strategies", [200])
    test_endpoint("get", "/backtest/indicators", [200])
    test_endpoint("get", "/backtest/timeframes", [200])
    test_endpoint("get", "/backtest/exchange-health", [200])
    
    # Trading public endpoints (symbols, orderbook - no auth)
    test_endpoint("get", "/trading/symbols", [200])
    test_endpoint("get", "/trading/market-overview", [200])
    test_endpoint("get", "/trading/orderbook/BTCUSDT", [200])
    test_endpoint("get", "/trading/recent-trades/BTCUSDT", [200])
    test_endpoint("get", "/trading/funding-rates", [200])
    
    # Trading endpoints requiring auth
    test_endpoint("get", "/trading/price/BTCUSDT", [401, 403])  # Requires auth
    test_endpoint("get", "/trading/symbol-info/BTCUSDT", [401, 403])  # Requires auth

def test_auth_endpoints():
    """Test authentication endpoints"""
    log("=" * 60)
    log("TESTING AUTH ENDPOINTS")
    log("=" * 60)
    
    # These should return 401/422 without proper data
    test_endpoint("post", "/auth/telegram", [401, 422, 400], data={})
    test_endpoint("get", "/auth/me", [401, 403])
    test_endpoint("post", "/auth/logout", [200, 401, 403])  # 200 is OK for logout
    
    # Email auth
    test_endpoint("post", "/auth/email/register", [422, 400], data={})
    test_endpoint("post", "/auth/email/login", [401, 422, 400], data={})
    test_endpoint("post", "/auth/email/verify", [422, 400], data={})
    
    # Telegram auth
    test_endpoint("get", "/auth/telegram/widget-params", [200])
    test_endpoint("post", "/auth/telegram/login", [401, 422, 400], data={})
    test_endpoint("post", "/auth/telegram/deep-link", [401, 422, 400], data={})
    
    # 2FA
    test_endpoint("post", "/auth/telegram/request-2fa", [422, 401, 400], data={})
    test_endpoint("post", "/auth/check-2fa", [422, 401, 400], data={})
    
    # Direct login
    test_endpoint("post", "/auth/direct-login", [422, 401, 400], data={})
    test_endpoint("get", "/auth/token-login", [422, 401, 400])


def test_trading_endpoints_no_auth():
    """Test trading endpoints without auth - should return 401/403"""
    log("=" * 60)
    log("TESTING TRADING ENDPOINTS (NO AUTH - expect 401/403)")
    log("=" * 60)
    
    test_endpoint("get", "/trading/balance", [401, 403])
    test_endpoint("get", "/trading/positions", [401, 403])
    test_endpoint("get", "/trading/orders", [401, 403])
    test_endpoint("get", "/trading/trades", [401, 403])
    test_endpoint("get", "/trading/stats", [401, 403])
    test_endpoint("post", "/trading/order", [401, 403, 422], data={})
    test_endpoint("post", "/trading/close", [401, 403, 422], data={})
    test_endpoint("get", "/trading/strategy-settings", [401, 403])
    test_endpoint("get", "/trading/symbols", [200, 401, 403])  # May be public
    test_endpoint("get", "/trading/market-overview", [200, 401, 403])


def test_user_endpoints_no_auth():
    """Test user endpoints without auth - should return 401/403"""
    log("=" * 60)
    log("TESTING USER ENDPOINTS (NO AUTH - expect 401/403)")
    log("=" * 60)
    
    test_endpoint("get", "/users/settings", [401, 403])
    test_endpoint("get", "/users/me", [401, 403])
    test_endpoint("get", "/users/profile", [401, 403])
    test_endpoint("get", "/users/api-keys", [401, 403])
    test_endpoint("get", "/users/api-keys/status", [401, 403])
    test_endpoint("get", "/users/global-settings", [401, 403])
    test_endpoint("get", "/users/strategy-settings", [401, 403])
    test_endpoint("get", "/users/exchange-settings", [401, 403])


def test_admin_endpoints_no_auth():
    """Test admin endpoints without auth - should return 401/403"""
    log("=" * 60)
    log("TESTING ADMIN ENDPOINTS (NO AUTH - expect 401/403)")
    log("=" * 60)
    
    test_endpoint("get", "/admin/users", [401, 403])
    test_endpoint("get", "/admin/dashboard", [401, 403])
    test_endpoint("get", "/admin/stats", [401, 403])
    test_endpoint("get", "/admin/licenses", [401, 403])
    test_endpoint("get", "/admin/positions", [401, 403])
    test_endpoint("get", "/admin/trades", [401, 403])
    test_endpoint("get", "/admin/system/health", [401, 403])


def test_backtest_endpoints():
    """Test backtest endpoints"""
    log("=" * 60)
    log("TESTING BACKTEST ENDPOINTS")
    log("=" * 60)
    
    # Public (no auth required)
    test_endpoint("get", "/backtest/strategies", [200])
    test_endpoint("get", "/backtest/indicators", [200])
    test_endpoint("get", "/backtest/timeframes", [200])
    test_endpoint("get", "/backtest/exchange-health", [200])
    
    # Auth required (rate_limit_backtest depends on get_current_user)
    test_endpoint("get", "/backtest/chart-data", [401, 403])
    test_endpoint("get", "/backtest/available-parsers", [401, 403])
    test_endpoint("post", "/backtest/quick", [401, 422], data={
        "symbol": "BTCUSDT",
        "strategy": "oi",
        "timeframe": "1h",
        "days": 7
    })
    test_endpoint("post", "/backtest/run", [401, 422], data={})
    test_endpoint("get", "/backtest/deployments", [401, 403])
    test_endpoint("get", "/backtest/my-deployments", [401, 403])


def test_ai_endpoints():
    """Test AI endpoints"""
    log("=" * 60)
    log("TESTING AI ENDPOINTS")
    log("=" * 60)
    
    test_endpoint("get", "/ai/market-sentiment", [200, 401, 403])
    test_endpoint("post", "/ai/analyze", [200, 401, 422], data={"symbol": "BTCUSDT"})
    test_endpoint("post", "/ai/chat", [200, 401, 422], data={"message": "What is Bitcoin?"})


def test_activity_endpoints():
    """Test activity endpoints"""
    log("=" * 60)
    log("TESTING ACTIVITY ENDPOINTS")
    log("=" * 60)
    
    test_endpoint("get", "/activity/history", [401, 403])
    test_endpoint("get", "/activity/recent", [401, 403])
    test_endpoint("get", "/activity/stats", [401, 403])


def test_payments_endpoints():
    """Test payment endpoints"""
    log("=" * 60)
    log("TESTING PAYMENT ENDPOINTS")
    log("=" * 60)
    
    # Payments API (/api/payments/*)
    test_endpoint("get", "/payments/plans", [200])
    test_endpoint("get", "/payments/subscription", [401, 403])
    test_endpoint("post", "/payments/create", [401, 422], data={})
    test_endpoint("get", "/payments/history/me", [401, 403])
    
    # Crypto Payments (OxaPay) (/api/crypto/*)
    test_endpoint("get", "/crypto/plans", [200])
    test_endpoint("get", "/crypto/currencies", [200])
    test_endpoint("post", "/crypto/create", [401, 422], data={})
    test_endpoint("get", "/crypto/history", [401, 403])


def test_web3_endpoints():
    """Test Web3 endpoints"""
    log("=" * 60)
    log("TESTING WEB3 ENDPOINTS (may be 503 if not configured)")
    log("=" * 60)
    
    # Web3 may not be configured in production
    test_endpoint("get", "/web3/token/info", [200, 503])
    test_endpoint("get", "/web3/marketplace/listings", [200, 503])
    
    # Auth required
    test_endpoint("get", "/web3/wallet/info", [401, 403])


def test_marketplace_endpoints():
    """Test marketplace endpoints"""
    log("=" * 60)
    log("TESTING MARKETPLACE ENDPOINTS")
    log("=" * 60)
    
    # Public endpoints
    test_endpoint("get", "/marketplace/marketplace", [200])
    test_endpoint("get", "/marketplace/indicators", [200])
    test_endpoint("get", "/marketplace/market/overview", [200])
    test_endpoint("get", "/marketplace/rankings/top", [200])
    
    # Auth required
    test_endpoint("get", "/marketplace/strategies/my", [401, 403])
    test_endpoint("get", "/marketplace/purchases", [401, 403])
    test_endpoint("get", "/marketplace/seller/stats", [401, 403])


def test_support_endpoints():
    """Test support chat endpoints"""
    log("=" * 60)
    log("TESTING SUPPORT ENDPOINTS")
    log("=" * 60)
    
    # Public
    test_endpoint("get", "/support/faq", [200])
    
    # Auth required
    test_endpoint("get", "/support/chat", [401, 403])
    test_endpoint("post", "/support/chat", [401, 422], data={})
    test_endpoint("get", "/support/chat/history", [401, 403])
    
    # Admin required
    test_endpoint("get", "/support/admin/chats", [401, 403])
    test_endpoint("get", "/support/admin/stats", [401, 403])


def test_static_files():
    """Test static files are accessible"""
    log("=" * 60)
    log("TESTING STATIC FILES")
    log("=" * 60)
    
    static_files = [
        "/static/css/base.css",
        "/static/css/components.css",
        "/static/css/animations.css",
        "/static/js/core.js",
        "/static/js/dynamic.js",
    ]
    
    for file_path in static_files:
        url = f"https://enliko.com{file_path}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                log(f"✅ {file_path} → 200", "PASS")
                results["passed"].append(f"STATIC {file_path}")
            else:
                log(f"❌ {file_path} → {resp.status_code}", "FAIL")
                results["failed"].append((f"STATIC {file_path}", resp.status_code, ""))
        except Exception as e:
            log(f"💥 {file_path} → {e}", "FAIL")
            results["failed"].append((f"STATIC {file_path}", "EXCEPTION", str(e)))


def test_html_pages():
    """Test HTML pages are accessible"""
    log("=" * 60)
    log("TESTING HTML PAGES")
    log("=" * 60)
    
    pages = [
        "/",
        "/terminal",
        "/screener",
        "/marketplace",
        "/statistics",
        "/backtest",
        "/pricing",
        "/terms",
        "/privacy",
        "/download",
    ]
    
    for page in pages:
        url = f"https://enliko.com{page}"
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                log(f"✅ PAGE {page} → 200", "PASS")
                results["passed"].append(f"PAGE {page}")
            else:
                log(f"❌ PAGE {page} → {resp.status_code}", "FAIL")
                results["failed"].append((f"PAGE {page}", resp.status_code, ""))
        except Exception as e:
            log(f"💥 PAGE {page} → {e}", "FAIL")
            results["failed"].append((f"PAGE {page}", "EXCEPTION", str(e)))


def print_summary():
    """Print test results summary"""
    log("=" * 60)
    log("TEST SUMMARY")
    log("=" * 60)
    
    total = len(results["passed"]) + len(results["failed"]) + len(results["skipped"])
    
    log(f"✅ PASSED: {len(results['passed'])}")
    log(f"❌ FAILED: {len(results['failed'])}")
    log(f"⏭️ SKIPPED: {len(results['skipped'])}")
    log(f"📊 TOTAL: {total}")
    log(f"📈 SUCCESS RATE: {len(results['passed'])/total*100:.1f}%" if total > 0 else "N/A")
    
    if results["failed"]:
        log("")
        log("FAILED TESTS:")
        for item in results["failed"]:
            if isinstance(item, tuple):
                name, code, msg = item
                log(f"   ❌ {name}: {code}")
            else:
                log(f"   ❌ {item}")
    
    return len(results["failed"]) == 0


if __name__ == "__main__":
    log("🚀 Starting Comprehensive API Testing")
    log(f"🌐 Base URL: {BASE_URL}")
    log("")
    
    start_time = time.time()
    
    # Run all tests
    test_static_files()
    test_html_pages()
    test_public_endpoints()
    test_auth_endpoints()
    test_trading_endpoints_no_auth()
    test_user_endpoints_no_auth()
    test_admin_endpoints_no_auth()
    test_backtest_endpoints()
    test_ai_endpoints()
    test_activity_endpoints()
    test_payments_endpoints()
    test_web3_endpoints()
    test_marketplace_endpoints()
    test_support_endpoints()
    
    elapsed = time.time() - start_time
    log(f"\n⏱️ Total time: {elapsed:.1f}s")
    
    success = print_summary()
    
    exit(0 if success else 1)
