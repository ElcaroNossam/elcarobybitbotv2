"""
FastAPI Web Application for Trading Bot Management
Full Trading Terminal with AI Agent, Backtesting, and Statistics
"""
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)

APP_DIR = Path(__file__).parent


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
    app = FastAPI(
        title="Triacelo Trading Terminal",
        description="Professional Trading Terminal with AI Analysis, Backtesting & Statistics",
        version="2.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    # SECURITY: Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # SECURITY: Restrict CORS origins in production
    # allow_credentials=True requires specific origins, not "*"
    allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8765").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
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
    
    # ELCARO Token Payment System (USDT → ELC, Cold Wallet Trading)
    try:
        from webapp.api import elcaro_payments
        app.include_router(elcaro_payments.router, prefix="/api/elcaro", tags=["elcaro-payments"])
        logger.info("✅ ELCARO payment system loaded")
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
    
    # TRC Blockchain API (wallets, deposits, withdrawals, sovereign operations)
    try:
        from webapp.api import blockchain
        app.include_router(blockchain.router, prefix="/api/blockchain", tags=["blockchain", "trc"])
        logger.info("✅ TRC Blockchain API loaded at /api/blockchain")
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
    
    # Landing page (epic dynamic)
    @app.get("/", response_class=HTMLResponse)
    async def landing(request: Request):
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
    
    # Blockchain/TRC pages
    @app.get("/wallet", response_class=HTMLResponse)
    async def wallet_page(request: Request):
        """TRC wallet - deposit, withdraw, stake, subscribe"""
        return templates.TemplateResponse("wallet.html", {"request": request})
    
    @app.get("/blockchain-admin", response_class=HTMLResponse)
    async def blockchain_admin_page(request: Request):
        """TRC blockchain admin panel - sovereign owner only"""
        return templates.TemplateResponse("blockchain_admin.html", {"request": request})
    
    @app.get("/backtest", response_class=HTMLResponse)
    async def backtest_page(request: Request):
        return templates.TemplateResponse("backtest.html", {"request": request})
    
    @app.get("/settings", response_class=HTMLResponse)
    async def settings_page(request: Request):
        return templates.TemplateResponse("settings.html", {"request": request})
    
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
