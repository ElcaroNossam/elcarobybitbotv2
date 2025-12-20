"""
WebApp API routers
"""
from webapp.api.auth import router as auth_router
from webapp.api.trading import router as trading_router
from webapp.api.admin import router as admin_router
from webapp.api.users import router as users_router

__all__ = ["auth_router", "trading_router", "admin_router", "users_router"]
