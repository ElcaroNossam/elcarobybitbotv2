"""
FastAPI Web Application for Trading Bot Management
Full Trading Terminal with AI Agent, Backtesting, and Statistics
"""
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os

APP_DIR = Path(__file__).parent

def create_app() -> FastAPI:
    app = FastAPI(
        title="ElCaro Trading Terminal",
        description="Professional Trading Terminal with AI Analysis, Backtesting & Statistics",
        version="2.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
        print(f"Warning: stats router: {e}")
    
    try:
        from webapp.api import backtest
        app.include_router(backtest.router, prefix="/api/backtest", tags=["backtest"])
    except ImportError as e:
        print(f"Warning: backtest router: {e}")
    
    try:
        from webapp.api import ai
        app.include_router(ai.router, prefix="/api/ai", tags=["ai-agent"])
    except ImportError as e:
        print(f"Warning: ai router: {e}")
    
    # WebSocket for live trades
    try:
        from webapp.api import websocket
        app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
    except ImportError as e:
        print(f"Warning: websocket router: {e}")
    
    # Marketplace for custom strategies
    try:
        from webapp.api import marketplace
        app.include_router(marketplace.router, prefix="/api/marketplace", tags=["marketplace"])
    except ImportError as e:
        print(f"Warning: marketplace router: {e}")
    
    # Strategy Marketplace (sharing, presets, import/export)
    try:
        from webapp.api import strategy_marketplace
        app.include_router(strategy_marketplace.router, prefix="/api/strategies", tags=["strategy-marketplace"])
    except ImportError as e:
        print(f"Warning: strategy_marketplace router: {e}")
    
    # Screener WebSocket API
    try:
        from webapp.api import screener_ws
        app.include_router(screener_ws.router, tags=["screener"])
    except ImportError as e:
        print(f"Warning: screener router: {e}")
    
    # Strategy Sync API (bidirectional webapp <-> bot)
    try:
        from webapp.api import strategy_sync
        app.include_router(strategy_sync.router, prefix="/api/sync", tags=["strategy-sync"])
    except ImportError as e:
        print(f"Warning: strategy_sync router: {e}")
    
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
    
    @app.get("/backtest", response_class=HTMLResponse)
    async def backtest_page(request: Request):
        return templates.TemplateResponse("backtest.html", {"request": request})
    
    @app.get("/settings", response_class=HTMLResponse)
    async def settings_page(request: Request):
        return templates.TemplateResponse("settings.html", {"request": request})
    
    @app.get("/portfolio", response_class=HTMLResponse)
    async def portfolio_page(request: Request):
        return templates.TemplateResponse("dashboard.html", {"request": request})
    
    @app.get("/health")
    async def health():
        """Basic health check"""
        return {"status": "healthy", "version": "2.0.0", "features": ["trading_terminal", "ai_agent", "backtesting", "statistics", "websocket", "multi_exchange", "marketplace", "screener"]}
    
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
