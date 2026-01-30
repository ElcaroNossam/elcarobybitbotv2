"""
FastAPI Web Application for Trading Bot Management
Full Trading Terminal with AI Agent, Backtesting, and Statistics
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from pathlib import Path
import os
import logging
import time
import re
import random
from collections import defaultdict
from threading import Lock

# Load .env file for environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, rely on system env vars

logger = logging.getLogger(__name__)

APP_DIR = Path(__file__).parent


class HackerDetectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to detect and roast script kiddies trying common attacks.
    Doesn't block anyone, just logs and returns funny messages for obvious attacks.
    """
    
    # Паттерны атак которые ловим
    ATTACK_PATTERNS = [
        (r'\.\./', "Path traversal"),
        (r'\.\.\\', "Path traversal"),
        (r'%2e%2e', "Path traversal encoded"),
        (r"['\"].*(?:OR|AND|UNION|SELECT|INSERT|DELETE|DROP|UPDATE).*['\"]", "SQL injection"),
        (r'<script', "XSS attempt"),
        (r'javascript:', "XSS attempt"),
        (r'onerror\s*=', "XSS attempt"),
        (r'onload\s*=', "XSS attempt"),
        (r'/etc/passwd', "LFI attempt"),
        (r'/proc/self', "LFI attempt"),
        (r'\.env$', "Env file access"),
        (r'\.git/', "Git access"),
        (r'wp-admin', "WordPress scan"),
        (r'phpmyadmin', "phpMyAdmin scan"),
        (r'\.php$', "PHP scan"),
        (r'/admin\.', "Admin scan"),
    ]
    
    # Весёлые ответы для хакеров 😈
    ROAST_MESSAGES = [
        "Шо вы головы не раздуплились? Это не WordPress, дружок 🤡",
        "Хахаха, {} detected! Иди учи матчасть 📚",
        "Ты серьёзно? {} в 2026 году? Ну ты и динозавр 🦖",
        "Мамкин хакер засечён! {} не прокатит 😂",
        "Слышь, script kiddie, {} тут не работает 🎪",
        "О, смотрите кто пришёл! {} мастер 🏆",
        "Нашёл что искал? Спойлер: нет. {} blocked 🚫",
        "Бро, это не тот сайт. {} попытка #999 провалена 💀",
    ]
    
    def __init__(self, app):
        super().__init__(app)
        self.compiled_patterns = [(re.compile(p, re.IGNORECASE), name) for p, name in self.ATTACK_PATTERNS]
    
    async def dispatch(self, request: Request, call_next):
        # Проверяем URL и query string
        full_path = str(request.url)
        
        for pattern, attack_name in self.compiled_patterns:
            if pattern.search(full_path):
                # Логируем попытку атаки
                client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
                if not client_ip:
                    client_ip = request.client.host if request.client else "unknown"
                
                logger.warning(f"🚨 ATTACK DETECTED: {attack_name} from {client_ip} - {full_path}")
                
                # Возвращаем весёлый ответ
                roast = random.choice(self.ROAST_MESSAGES).format(attack_name)
                return JSONResponse(
                    status_code=418,  # I'm a teapot 🫖
                    content={
                        "error": "Nice try, script kiddie",
                        "message": roast,
                        "tip": "Попробуй нормально пользоваться сервисом 😊"
                    }
                )
        
        return await call_next(request)


class ResponseCacheMiddleware(BaseHTTPMiddleware):
    """
    Lightweight response cache for GET requests.
    Caches frequent API responses to reduce DB/API load.
    TTL-based expiration with per-endpoint configuration.
    """
    
    # Endpoints to cache with TTL in seconds
    CACHEABLE_ENDPOINTS = {
        "/api/marketplace/overview": 30,      # Market data - 30s
        "/api/marketplace/trending": 60,      # Trending - 1min
        "/api/marketplace/top-performers": 60,
        "/api/stats/leaderboard": 120,        # Leaderboard - 2min
        "/health": 5,                          # Health check - 5s
    }
    
    def __init__(self, app):
        super().__init__(app)
        self._cache: dict = {}  # key -> (response_body, headers, timestamp)
        self._lock = Lock()
    
    async def dispatch(self, request: Request, call_next):
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)
        
        path = request.url.path
        ttl = self.CACHEABLE_ENDPOINTS.get(path)
        
        if ttl is None:
            return await call_next(request)
        
        cache_key = f"{path}?{request.url.query}"
        now = time.time()
        
        # Check cache
        with self._lock:
            if cache_key in self._cache:
                body, headers, cached_at = self._cache[cache_key]
                if now - cached_at < ttl:
                    # Cache hit
                    response = Response(
                        content=body,
                        media_type="application/json",
                        headers={"X-Cache": "HIT", "Cache-Control": f"max-age={ttl}"}
                    )
                    for k, v in headers.items():
                        if k.lower() not in ("content-length", "x-cache"):
                            response.headers[k] = v
                    return response
        
        # Cache miss - get response
        response = await call_next(request)
        
        # Only cache successful JSON responses
        if response.status_code == 200 and response.media_type == "application/json":
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            with self._lock:
                self._cache[cache_key] = (body, dict(response.headers), now)
                # Cleanup old entries (max 1000)
                if len(self._cache) > 1000:
                    oldest_keys = sorted(self._cache.keys(), 
                                        key=lambda k: self._cache[k][2])[:100]
                    for k in oldest_keys:
                        del self._cache[k]
            
            return Response(
                content=body,
                status_code=response.status_code,
                headers={"X-Cache": "MISS", **dict(response.headers)},
                media_type=response.media_type
            )
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Global rate limiting middleware.
    Protects against DDoS and brute-force attacks.
    Uses sliding window algorithm per IP address.
    """
    
    # Весёлые ответы для тех кто пытается брутфорсить 😈
    HACKER_RESPONSES = [
        "Шо вы головы не раздуплились? Иди погуляй, вернись через {} секунд 🤡",
        "Э, полегче там! Подожди {} секунд и не тупи 🧠",
        "Хакер, блин... Жди {} сек, потом попробуй нормально 😂",
        "Тебя мама не учила терпению? {} секунд подожди 🍼",
        "Too many requests, genius. Wait {} seconds 🎪",
        "Полегче на поворотах! Cooldown: {} сек 🚦",
        "Ты чё, DDoS-ить решил? {} секунд в бан 🔨",
    ]
    
    def __init__(self, app, requests_per_minute: int = 120, burst_size: int = 30):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.window_size = 60  # 1 minute window
        self.requests: dict = defaultdict(list)  # ip -> [timestamps]
        self._lock = Lock()
        
        # Stricter limits for sensitive endpoints
        self.sensitive_limits = {
            "/api/auth/login": (5, 60),      # 5 per minute
            "/api/auth/direct-login": (5, 300),  # 5 per 5 minutes
            "/api/auth/telegram": (10, 60),  # 10 per minute
            "/api/trading/order": (30, 60),  # 30 per minute
        }
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP (handle proxies)
        client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not client_ip:
            client_ip = request.client.host if request.client else "unknown"
        
        path = request.url.path
        now = time.time()
        
        # Determine rate limit for this endpoint
        if path in self.sensitive_limits:
            max_requests, window = self.sensitive_limits[path]
        else:
            max_requests = self.requests_per_minute
            window = self.window_size
        
        # Use endpoint-specific key for sensitive paths
        key = f"{client_ip}:{path}" if path in self.sensitive_limits else client_ip
        
        with self._lock:
            # Remove old timestamps outside the window
            self.requests[key] = [t for t in self.requests[key] if now - t < window]
            
            # Check rate limit
            if len(self.requests[key]) >= max_requests:
                retry_after = int(window - (now - self.requests[key][0]))
                # Выбираем весёлое сообщение для хакеров 😈
                import random
                fun_message = random.choice(self.HACKER_RESPONSES).format(retry_after)
                logger.warning(f"Rate limit hit: {client_ip} on {path} - {len(self.requests[key])} requests")
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too Many Requests",
                        "retry_after": retry_after,
                        "message": fun_message
                    },
                    headers={"Retry-After": str(retry_after)}
                )
            
            # Record this request
            self.requests[key].append(now)
        
        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    Prevents XSS, clickjacking, and other common attacks.
    """
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable XSS filter
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy (disable dangerous APIs)
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy - allow TradingView widgets, Telegram WebApp, Chart.js, FontAwesome
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://s3.tradingview.com https://*.tradingview.com https://telegram.org https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://*.tradingview.com https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https: blob:; "
            "font-src 'self' data: https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "connect-src 'self' https://*.tradingview.com https://*.binance.com https://*.bybit.com wss://*.binance.com wss://*.bybit.com https://cdn.jsdelivr.net; "
            "frame-src 'self' https://*.tradingview.com; "
            "object-src 'none'; "
            "base-uri 'self'"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response


def create_app() -> FastAPI:
    # SECURITY: Disable docs in production
    is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    app = FastAPI(
        title="Enliko Trading Terminal",
        description="Professional Trading Terminal with AI Analysis, Backtesting & Statistics",
        version="2.0.0",
        docs_url=None if is_production else "/api/docs",
        redoc_url=None if is_production else "/api/redoc"
    )
    
    # SECURITY: Add hacker detection middleware (first - catches script kiddies)
    app.add_middleware(HackerDetectionMiddleware)
    
    # PERFORMANCE: Add response cache middleware (before rate limiting)
    app.add_middleware(ResponseCacheMiddleware)
    
    # SECURITY: Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware, requests_per_minute=120, burst_size=30)
    
    # SECURITY: Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # SECURITY: CORS configuration
    # If CORS_ORIGINS=* allow all origins (for mobile/Telegram WebApp)
    # Otherwise use specific origins list
    cors_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8765")
    env_name = os.getenv("ENV", "development").lower()
    
    if cors_env.strip() == "*":
        # SECURITY: Warn about wildcard CORS in production
        if env_name in ("production", "prod"):
            logger.warning("⚠️ SECURITY: CORS_ORIGINS=* in production! Consider using specific origins.")
        # Allow all origins - needed for Telegram WebApp and mobile
        allowed_origins = ["*"]
        allow_credentials = False  # Can't use credentials with wildcard
    else:
        allowed_origins = [o.strip() for o in cors_env.split(",") if o.strip()]
        allow_credentials = True
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With", "X-Telegram-Init-Data"],
    )
    
    static_path = APP_DIR / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    
    templates = Jinja2Templates(directory=str(APP_DIR / "templates"))
    
    # API routers
    from webapp.api import auth, users, trading, admin
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    app.include_router(trading.router, prefix="/api/trading", tags=["trading"])
    app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
    
    # iOS Logs API for monitoring
    try:
        from webapp.api import ios_logs
        app.include_router(ios_logs.router, prefix="/api", tags=["ios-logs"])
        logger.info("✅ iOS Logs API mounted")
    except Exception as e:
        logger.warning(f"⚠️ iOS Logs API not available: {e}")
    
    # Telegram auth for iOS/Android
    try:
        from webapp.api import telegram_auth
        app.include_router(telegram_auth.router, prefix="/api", tags=["telegram-auth"])
        logger.info("✅ Telegram Auth API mounted")
    except Exception as e:
        logger.warning(f"⚠️ Telegram Auth API not available: {e}")
    
    try:
        from webapp.api import stats
        app.include_router(stats.router, prefix="/api/stats", tags=["statistics"])
    except ImportError as e:
        logger.warning(f"stats router not available: {e}")
    
    try:
        from webapp.api import backtest
        app.include_router(backtest.router, prefix="/api/backtest", tags=["backtest"])
    except ImportError as e:
        logger.warning(f"backtest router not available: {e}")
    
    try:
        from webapp.api import backtest_enhanced
        app.include_router(backtest_enhanced.router, prefix="/api/backtest-v2", tags=["backtest-enhanced"])
    except ImportError as e:
        logger.warning(f"backtest_enhanced router not available: {e}")
    
    # Note: backtest_v2 was merged into backtest.py
    
    try:
        from webapp.api import ai
        app.include_router(ai.router, prefix="/api/ai", tags=["ai-agent"])
    except ImportError as e:
        logger.warning(f"ai router not available: {e}")
    
    # WebSocket for live trades
    try:
        from webapp.api import websocket
        app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
    except ImportError as e:
        logger.warning(f"websocket router not available: {e}")
    
    # Real-time market data WebSocket
    try:
        from webapp.api import realtime
        app.include_router(realtime.router, prefix="/ws", tags=["realtime"])
        logger.info("✅ Real-time market data WebSocket enabled")
    except ImportError as e:
        logger.warning(f"realtime router not available: {e}")
    
    # Marketplace for custom strategies
    try:
        from webapp.api import marketplace
        app.include_router(marketplace.router, prefix="/api/marketplace", tags=["marketplace"])
    except ImportError as e:
        logger.warning(f"marketplace router not available: {e}")
    
    # Protected Strategy Backtest & Custom Strategy Builder
    try:
        from webapp.api import strategy_backtest
        app.include_router(strategy_backtest.router, prefix="/api", tags=["strategy"])
    except ImportError as e:
        logger.warning(f"strategy_backtest router not available: {e}")
    
    # Strategy Marketplace (sharing, presets, import/export)
    try:
        from webapp.api import strategy_marketplace
        app.include_router(strategy_marketplace.router, prefix="/api/strategies", tags=["strategy-marketplace"])
    except ImportError as e:
        logger.warning(f"strategy_marketplace router not available: {e}")
    
    # Strategy Builder API (CRUD, Backtest, Live Trading)
    try:
        from webapp.api import strategy_builder_api
        app.include_router(strategy_builder_api.router, prefix="/api/builder", tags=["strategy-builder"])
        logger.info("✅ Strategy Builder API loaded at /api/builder/strategies")
    except ImportError as e:
        logger.warning(f"strategy_builder_api router not available: {e}")
    
    # ENLIKO Token Payment System (USDT → ELC, Cold Wallet Trading)
    try:
        from webapp.api import elcaro_payments
        app.include_router(elcaro_payments.router, prefix="/api/elcaro", tags=["elcaro-payments"])
        logger.info("✅ ENLIKO payment system loaded")
    except ImportError as e:
        logger.warning(f"elcaro_payments router not available: {e}")
    
    # Web3 Blockchain Integration
    try:
        from webapp.api import web3
        app.include_router(web3.router, prefix="/api/web3", tags=["web3", "blockchain"])
        logger.info("Web3 router registered at /api/web3")
    except ImportError as e:
        logger.warning(f"Web3 router not available: {e}")
    
    # Screener WebSocket API
    try:
        from webapp.api import screener_ws
        app.include_router(screener_ws.router, tags=["screener"])
    except ImportError as e:
        logger.warning(f"screener router not available: {e}")
    
    # Backtest WebSocket API
    try:
        from webapp.api import backtest_ws
        app.include_router(backtest_ws.router, tags=["backtest-ws"])
        logger.info("✅ Backtest WebSocket enabled")
    except ImportError as e:
        logger.warning(f"backtest_ws router not available: {e}")
    
    # Strategy Sync API (bidirectional webapp <-> bot)
    try:
        from webapp.api import strategy_sync
        app.include_router(strategy_sync.router, prefix="/api/sync", tags=["strategy-sync"])
    except ImportError as e:
        logger.warning(f"strategy_sync router not available: {e}")
    
    # Payments & Subscriptions API
    try:
        from webapp.api import payments
        app.include_router(payments.router, prefix="/api/payments", tags=["payments", "subscriptions"])
        logger.info("✅ Payments API loaded")
    except ImportError as e:
        logger.warning(f"payments router not available: {e}")
    
    # TON Payments API (subscription purchases via TON blockchain)
    try:
        from webapp.api import ton_payments
        app.include_router(ton_payments.router, prefix="/api/payments", tags=["ton", "payments"])
        logger.info("✅ TON Payments API loaded at /api/payments/ton/*")
    except ImportError as e:
        logger.warning(f"ton_payments router not available: {e}")
    
    # Signals REST API (for iOS/mobile)
    try:
        from webapp.api import signals
        app.include_router(signals.router, prefix="/api", tags=["signals"])
        logger.info("✅ Signals API loaded at /api/signals")
    except ImportError as e:
        logger.warning(f"signals router not available: {e}")
    
    # Activity Log & Cross-Platform Sync API
    try:
        from webapp.api import activity
        app.include_router(activity.router, prefix="/api", tags=["activity", "sync"])
        logger.info("✅ Activity Log API loaded at /api/activity")
    except ImportError as e:
        logger.warning(f"activity router not available: {e}")
    
    # Push Notifications API (device tokens, preferences, WebSocket)
    try:
        from webapp.api import push_notifications
        app.include_router(push_notifications.router, prefix="/api", tags=["notifications"])
        logger.info("✅ Push Notifications API loaded at /api/notifications")
    except ImportError as e:
        logger.warning(f"push_notifications router not available: {e}")
    
    # ELC Blockchain API (wallets, deposits, withdrawals, sovereign operations)
    try:
        from webapp.api import blockchain
        app.include_router(blockchain.router, prefix="/api/blockchain", tags=["blockchain", "elc"])
        logger.info("✅ ELC Blockchain API loaded at /api/blockchain")
    except ImportError as e:
        logger.warning(f"blockchain router not available: {e}")
    
    # License Blockchain API (ELC license purchases, NFTs)
    try:
        from webapp.api import license_blockchain
        app.include_router(license_blockchain.router, tags=["license", "blockchain"])
        app.include_router(license_blockchain.nft_router, tags=["license", "nft"])
        logger.info("✅ License Blockchain API loaded at /api/license/blockchain")
    except ImportError as e:
        logger.warning(f"license_blockchain router not available: {e}")
    
    # Finance & Accounting API (admin dashboard, reports, exports)
    try:
        from webapp.api import finance
        app.include_router(finance.router, prefix="/api/finance", tags=["finance", "accounting"])
        logger.info("✅ Finance & Accounting API loaded at /api/finance")
    except ImportError as e:
        logger.warning(f"finance router not available: {e}")
    
    # Mobile API (Android/iOS specific endpoints with multitenancy)
    try:
        from webapp.api import mobile
        app.include_router(mobile.router, prefix="/api/mobile", tags=["mobile", "multitenancy"])
        logger.info("✅ Mobile API loaded at /api/mobile")
    except ImportError as e:
        logger.warning(f"mobile router not available: {e}")
    
    # Email Authentication API (registration, login, password reset)
    try:
        from webapp.api import email_auth
        app.include_router(email_auth.router, prefix="/api/auth/email", tags=["auth", "email"])
        logger.info("✅ Email Auth API loaded at /api/auth/email")
    except ImportError as e:
        logger.warning(f"email_auth router not available: {e}")
    
    # Home Page Data API (BTC/Gold charts, platform stats)
    try:
        from webapp.api import home_data
        app.include_router(home_data.router, tags=["home"])
        logger.info("✅ Home Data API loaded at /api/home")
    except ImportError as e:
        logger.warning(f"home_data router not available: {e}")
    
    # Landing page (modern design with charts)
    @app.get("/", response_class=HTMLResponse)
    async def landing(request: Request):
        return templates.TemplateResponse("home.html", {"request": request})
    
    @app.get("/landing", response_class=HTMLResponse)
    async def landing_old(request: Request):
        return templates.TemplateResponse("landing.html", {"request": request})
    
    @app.get("/old", response_class=HTMLResponse)
    async def old_index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})
    
    @app.get("/login", response_class=HTMLResponse)
    async def login_page(request: Request):
        return templates.TemplateResponse("auth/login.html", {"request": request})
    
    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard(request: Request):
        return templates.TemplateResponse("user/dashboard.html", {"request": request})
    
    @app.get("/admin", response_class=HTMLResponse)
    async def admin_panel(request: Request):
        return templates.TemplateResponse("admin/dashboard.html", {"request": request})
    
    @app.get("/admin/legacy", response_class=HTMLResponse)
    async def admin_panel_legacy(request: Request):
        return templates.TemplateResponse("admin/index.html", {"request": request})
    
    # Terminal routes
    @app.get("/terminal", response_class=HTMLResponse)
    async def terminal(request: Request):
        return templates.TemplateResponse("terminal.html", {"request": request, "active_section": "terminal"})
    
    @app.get("/terminal/{section}", response_class=HTMLResponse)
    async def terminal_section(request: Request, section: str):
        return templates.TemplateResponse("terminal.html", {"request": request, "active_section": section})
    
    # Marketplace pages
    @app.get("/marketplace", response_class=HTMLResponse)
    async def marketplace_page(request: Request):
        return templates.TemplateResponse("marketplace.html", {"request": request})
    
    @app.get("/strategies", response_class=HTMLResponse)
    async def strategies_page(request: Request):
        return templates.TemplateResponse("strategies.html", {"request": request})
    
    @app.get("/leaderboard", response_class=HTMLResponse)
    async def leaderboard_page(request: Request):
        return templates.TemplateResponse("leaderboard.html", {"request": request})
    
    @app.get("/screener", response_class=HTMLResponse)
    async def screener_page(request: Request):
        return templates.TemplateResponse("screener.html", {"request": request})
    
    @app.get("/enhanced-screener", response_class=HTMLResponse)
    async def enhanced_screener_page(request: Request):
        """Enhanced screener with top 200 Bybit + all HyperLiquid symbols."""
        return templates.TemplateResponse("enhanced_screener.html", {"request": request})
    
    # Blockchain/ELC pages
    @app.get("/wallet", response_class=HTMLResponse)
    async def wallet_page(request: Request):
        """ELC wallet - deposit, withdraw, stake, subscribe"""
        return templates.TemplateResponse("wallet.html", {"request": request})
    
    @app.get("/blockchain-admin", response_class=HTMLResponse)
    async def blockchain_admin_page(request: Request):
        """ELC blockchain admin panel - sovereign owner only"""
        return templates.TemplateResponse("blockchain_admin.html", {"request": request})
    
    @app.get("/backtest", response_class=HTMLResponse)
    async def backtest_page(request: Request):
        return templates.TemplateResponse("backtest.html", {"request": request})
    
    @app.get("/settings", response_class=HTMLResponse)
    async def settings_page(request: Request):
        return templates.TemplateResponse("settings.html", {"request": request})
    
    @app.get("/strategy-settings", response_class=HTMLResponse)
    async def strategy_settings_page(request: Request):
        """Strategy settings with Long/Short tabs"""
        return templates.TemplateResponse("strategy_settings.html", {"request": request})
    
    @app.get("/portfolio", response_class=HTMLResponse)
    async def portfolio_page(request: Request):
        """Portfolio page redirects to statistics"""
        return RedirectResponse(url="/statistics", status_code=302)
    
    @app.get("/pricing", response_class=HTMLResponse)
    async def pricing_page(request: Request):
        return templates.TemplateResponse("pricing.html", {"request": request})
    
    @app.get("/realtime-test", response_class=HTMLResponse)
    async def realtime_test_page(request: Request):
        """Real-time market data test page"""
        return templates.TemplateResponse("realtime_test.html", {"request": request})
    
    @app.get("/statistics", response_class=HTMLResponse)
    async def statistics_page(request: Request):
        """Trading statistics dashboard"""
        return templates.TemplateResponse("statistics.html", {"request": request})
    
    @app.get("/stats", response_class=HTMLResponse)
    async def stats_page(request: Request):
        """Trading statistics dashboard (alias)"""
        return templates.TemplateResponse("statistics.html", {"request": request})
    
    # ===== LEGAL PAGES =====
    
    @app.get("/privacy", response_class=HTMLResponse)
    async def privacy_page(request: Request):
        """Privacy Policy"""
        return templates.TemplateResponse("privacy.html", {"request": request})
    
    @app.get("/terms", response_class=HTMLResponse)
    async def terms_page(request: Request):
        """Terms of Service"""
        return templates.TemplateResponse("terms.html", {"request": request})
    
    @app.get("/cookies", response_class=HTMLResponse)
    async def cookies_page(request: Request):
        """Cookie Policy"""
        return templates.TemplateResponse("cookies.html", {"request": request})
    
    @app.get("/disclaimer", response_class=HTMLResponse)
    async def disclaimer_page(request: Request):
        """Redirect to terms page which has disclaimer"""
        return RedirectResponse(url="/terms", status_code=302)
    
    @app.get("/health")
    async def health():
        """Basic health check"""
        return {"status": "healthy", "version": "2.0.0", "features": ["trading_terminal", "ai_agent", "backtesting", "statistics", "websocket", "multi_exchange", "marketplace", "screener", "realtime"]}
    
    @app.on_event("startup")
    async def startup_event():
        """Start real-time workers on application startup."""
        try:
            from webapp.realtime import start_workers
            # Start with default symbols
            await start_workers(
                bybit_symbols=['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 
                              'ADAUSDT', 'DOGEUSDT', 'MATICUSDT', 'DOTUSDT', 'LTCUSDT'],
                hl_symbols=['BTC', 'ETH', 'SOL', 'ARB', 'OP']
            )
            logger.info("✅ Real-time workers started on application startup")
        except Exception as e:
            logger.error(f"Failed to start real-time workers: {e}", exc_info=True)
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Stop real-time workers on application shutdown."""
        try:
            from webapp.realtime import stop_workers
            await stop_workers()
            logger.info("✅ Real-time workers stopped")
        except Exception as e:
            logger.error(f"Error stopping workers: {e}")
    
    @app.get("/health/detailed")
    async def health_detailed():
        """Detailed health check with metrics"""
        try:
            from core.metrics import get_health_status
            return await get_health_status()
        except Exception as e:
            return {"status": "degraded", "error": str(e)}
    
    @app.get("/metrics")
    async def get_metrics():
        """Prometheus-style metrics endpoint"""
        try:
            from core.metrics import metrics
            from core.cache import get_all_cache_stats
            from core.connection_pool import connection_pool
            
            return {
                "metrics": metrics.get_all_metrics(),
                "cache": get_all_cache_stats(),
                "connection_pool": connection_pool.stats
            }
        except Exception as e:
            return {"error": str(e)}
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
