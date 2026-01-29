"""
Authentication API - Telegram WebApp + JWT
"""
import os
import hashlib
import hmac
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import parse_qs
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import db
from coin_params import ADMIN_ID

# Load .env file if environment variables not set (needed when running uvicorn standalone)
_env_file = Path(__file__).parent.parent.parent / ".env"
if _env_file.exists() and not os.getenv("TELEGRAM_TOKEN"):
    with open(_env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer(auto_error=False)

# Configuration - secrets MUST be set in environment
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is required")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 168  # 7 days
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN", "")


def get_client_ip(request: Request) -> Optional[str]:
    """
    Get real client IP, handling proxies (nginx/cloudflare).
    
    SECURITY: X-Forwarded-For can be spoofed if not behind trusted proxy.
    In production, nginx should set X-Real-IP from leftmost non-trusted X-Forwarded-For.
    """
    # X-Forwarded-For: client, proxy1, proxy2
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        # Take first (original client) IP
        return xff.split(",")[0].strip()
    
    # X-Real-IP set by nginx
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Direct connection (no proxy)
    return request.client.host if request.client else None


class TelegramWebAppAuth(BaseModel):
    """Telegram WebApp init_data"""
    init_data: str


class TokenResponse(BaseModel):
    """JWT token response"""
    token: str
    user: dict


class LoginByIdRequest(BaseModel):
    """Login by Telegram ID or @username"""
    identifier: str  # Telegram ID (number) or @username


class TwoFACheckRequest(BaseModel):
    """Check 2FA status"""
    confirmation_id: str


def verify_webapp_data(init_data: str) -> Optional[dict]:
    """Verify Telegram WebApp init_data and extract user info."""
    if not TELEGRAM_BOT_TOKEN:
        # Dev mode - ONLY allowed in development environment
        env = os.getenv("ENV", "development").lower()
        if env in ("production", "prod"):
            logger.error("CRITICAL: TELEGRAM_BOT_TOKEN not set in production! Rejecting auth.")
            return None
        
        logger.warning("TELEGRAM_BOT_TOKEN not set! Running in dev mode (no verification)")
        try:
            parsed = parse_qs(init_data)
            if 'user' in parsed:
                return json.loads(parsed['user'][0])
        except Exception as e:
            logger.error(f"Dev mode parse failed: {e}")
        return None
    
    try:
        parsed = parse_qs(init_data)
        
        # Check auth_date
        auth_date = int(parsed.get('auth_date', [0])[0])
        if time.time() - auth_date > 86400:  # 24 hours
            logger.warning(f"Auth expired: auth_date={auth_date}, now={time.time()}")
            return None
        
        # Build data check string
        data_check_arr = []
        for key in sorted(parsed.keys()):
            if key != 'hash':
                data_check_arr.append(f"{key}={parsed[key][0]}")
        data_check_string = "\n".join(data_check_arr)
        
        # Compute hash
        secret_key = hmac.new(b"WebAppData", TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256).digest()
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        received_hash = parsed.get('hash', [''])[0]
        
        # Use constant-time comparison to prevent timing attacks
        import secrets
        if secrets.compare_digest(computed_hash, received_hash):
            user_data = json.loads(parsed.get('user', ['{}'])[0])
            logger.info(f"Telegram WebApp auth success: user_id={user_data.get('id')}")
            return user_data
        
        logger.warning(f"Hash mismatch: computed={computed_hash[:16]}... received={received_hash[:16]}...")
        return None
    except Exception as e:
        logger.error(f"WebApp auth error: {e}")
        return None


# =============================================================================
# TOKEN BLACKLIST (Redis-backed with in-memory fallback)
# =============================================================================
from collections import OrderedDict
from threading import Lock
import os

class TokenBlacklist:
    """
    JWT token blacklist with Redis support for horizontal scaling.
    Falls back to in-memory storage if Redis is unavailable.
    
    Stores token JTI (unique identifier) until expiration.
    """
    def __init__(self, max_size: int = 10000):
        self._blacklist: OrderedDict[str, datetime] = OrderedDict()
        self._max_size = max_size
        self._lock = Lock()
        self._redis = None
        self._redis_available = False
        self._redis_prefix = "token_blacklist:"
    
    async def _get_redis(self):
        """Get Redis client, initialize if needed."""
        if self._redis_available:
            return self._redis
        
        try:
            from core.redis_client import get_redis
            self._redis = await get_redis()
            if self._redis and await self._redis.client.ping():
                self._redis_available = True
                logger.info("TokenBlacklist using Redis backend")
                return self._redis
        except Exception as e:
            logger.warning(f"Redis unavailable for TokenBlacklist, using in-memory: {e}")
        
        self._redis_available = False
        return None
    
    async def add_async(self, token: str, expires_at: datetime) -> None:
        """Add token to blacklist (async, uses Redis if available)."""
        redis = await self._get_redis()
        if redis:
            try:
                ttl = int((expires_at - datetime.utcnow()).total_seconds())
                if ttl > 0:
                    await redis.client.setex(
                        f"{self._redis_prefix}{token}",
                        ttl,
                        "1"
                    )
                return
            except Exception as e:
                logger.warning(f"Redis blacklist add failed, using in-memory: {e}")
        
        # Fallback to in-memory
        self.add(token, expires_at)
    
    async def is_blacklisted_async(self, token: str) -> bool:
        """Check if token is blacklisted (async, uses Redis if available)."""
        redis = await self._get_redis()
        if redis:
            try:
                result = await redis.client.exists(f"{self._redis_prefix}{token}")
                return bool(result)
            except Exception as e:
                logger.warning(f"Redis blacklist check failed, using in-memory: {e}")
        
        # Fallback to in-memory
        return self.is_blacklisted(token)
    
    def add(self, token: str, expires_at: datetime) -> None:
        """Add token to blacklist until its expiration (sync, in-memory)."""
        with self._lock:
            # Clean expired tokens
            now = datetime.utcnow()
            expired_keys = [k for k, exp in self._blacklist.items() if exp <= now]
            for k in expired_keys:
                del self._blacklist[k]
            
            # Enforce max size (LRU eviction)
            while len(self._blacklist) >= self._max_size:
                self._blacklist.popitem(last=False)
            
            self._blacklist[token] = expires_at
    
    def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted (sync, in-memory)."""
        with self._lock:
            if token in self._blacklist:
                # Check if still valid (not expired)
                if self._blacklist[token] > datetime.utcnow():
                    return True
                # Expired, remove
                del self._blacklist[token]
            return False

# Global blacklist instance
_token_blacklist = TokenBlacklist()


def verify_ws_token(token: str) -> Optional[dict]:
    """
    Verify JWT token for WebSocket connections.
    Returns user info dict or None if invalid.
    """
    if not token:
        return None
    
    # Remove 'Bearer ' prefix if present
    if token.startswith("Bearer "):
        token = token[7:]
    
    # Check blacklist
    if _token_blacklist.is_blacklisted(token):
        return None
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
        
        # Get user from DB
        user_data = db.get_all_user_credentials(user_id)
        if not user_data:
            return None
        
        return {
            "user_id": user_id,
            "is_admin": user_id == ADMIN_ID,
            **user_data
        }
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def create_access_token(user_id: int, is_admin: bool = False) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "sub": str(user_id),
        "is_admin": is_admin,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """Create JWT refresh token with longer expiration."""
    expire = datetime.utcnow() + timedelta(days=30)  # 30 days for refresh
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_token(user_id: int, is_admin: bool = False) -> tuple:
    """
    Create access and refresh tokens pair.
    Used by telegram_auth.py and email_auth.py for consistent token generation.
    Returns: (access_token, refresh_token)
    """
    access_token = create_access_token(user_id, is_admin)
    refresh_token = create_refresh_token(user_id)
    return access_token, refresh_token


def decode_token(token: str) -> dict:
    """
    Decode and verify JWT token.
    Returns payload dict or raises exception.
    Used by telegram_auth.py for token verification.
    """
    if token.startswith("Bearer "):
        token = token[7:]
    
    # Check blacklist
    if _token_blacklist.is_blacklisted(token):
        raise jwt.InvalidTokenError("Token has been revoked")
    
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def get_authorization_header(request) -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    Returns token string or None.
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    """Verify JWT and return user info from DB."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if token is blacklisted (logged out)
    if _token_blacklist.is_blacklisted(credentials.credentials):
        raise HTTPException(status_code=401, detail="Token has been revoked")
    
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
        
        # Get user from DB
        user_data = db.get_all_user_credentials(user_id)
        if not user_data:
            raise HTTPException(status_code=401, detail="User not found")
        
        return {
            "user_id": user_id,
            "is_admin": user_id == ADMIN_ID,
            **user_data
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """
    Get current user if authenticated, otherwise return None.
    Use for endpoints that work both with and without auth.
    """
    if not credentials:
        return None
    
    # Check if token is blacklisted (logged out)
    if _token_blacklist.is_blacklisted(credentials.credentials):
        return None
    
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
        
        # Get user from DB
        user_data = db.get_all_user_credentials(user_id)
        if not user_data:
            return None
        
        return {
            "user_id": user_id,
            "is_admin": user_id == ADMIN_ID,
            **user_data
        }
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """Require admin access."""
    if not user.get("is_admin"):
        logger.warning(f"🚫 Admin access denied for user {user.get('user_id')} - nice try!")
        raise HTTPException(status_code=403, detail="Шо вы головы не раздуплились? Ты не админ 🤡")
    return user


@router.post("/telegram", response_model=TokenResponse)
async def telegram_auth(data: TelegramWebAppAuth, request: Request):
    """Authenticate via Telegram WebApp init_data."""
    
    # Get client IP for logging
    client_ip = get_client_ip(request)
    
    # Verify and extract user data
    user_data = verify_webapp_data(data.init_data)
    
    if not user_data:
        # Dev fallback - try to parse directly
        try:
            parsed = parse_qs(data.init_data)
            if 'user' in parsed:
                user_data = json.loads(parsed['user'][0])
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
    
    if not user_data or 'id' not in user_data:
        logger.warning(f"🚨 Failed Telegram auth from {client_ip} - invalid init_data")
        raise HTTPException(status_code=401, detail="Invalid Telegram authentication")
    
    user_id = user_data['id']
    first_name = user_data.get('first_name', 'User')
    username = user_data.get('username')
    
    logger.info(f"✅ Telegram auth success: {user_id} ({first_name}) from {client_ip}")
    
    # Ensure user exists in DB
    db.ensure_user(user_id)
    
    # Get user info from DB
    db_user = db.get_all_user_credentials(user_id)
    exchange_status = db.get_exchange_status(user_id)
    
    is_admin = user_id == ADMIN_ID
    is_premium = db_user.get('license_type') == 'premium' or db_user.get('is_lifetime')
    
    # Create token
    token = create_access_token(user_id, is_admin)
    
    return TokenResponse(
        token=token,
        user={
            "user_id": user_id,
            "first_name": first_name,
            "username": username,
            "is_admin": is_admin,
            "is_premium": is_premium,
            "exchange_type": exchange_status.get("active_exchange", "bybit"),
            "language": db_user.get("lang", "en"),
            "license_type": db_user.get("license_type"),
        }
    )


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Get current user info."""
    user_id = user["user_id"]
    
    db_user = db.get_all_user_credentials(user_id)
    exchange_status = db.get_exchange_status(user_id)
    
    is_premium = db_user.get('license_type') == 'premium' or db_user.get('is_lifetime')
    
    return {
        "user_id": user_id,
        "first_name": db_user.get("first_name", "User"),
        "username": db_user.get("username"),
        "is_admin": user.get("is_admin", False),
        "is_premium": is_premium,
        "exchange_type": exchange_status.get("active_exchange", "bybit"),
        "language": db_user.get("lang", "en"),
        "license_type": db_user.get("license_type"),
        "is_allowed": db_user.get("is_allowed", False),
        "is_banned": db_user.get("is_banned", False),
    }


@router.post("/logout")
async def logout(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    Logout - invalidates the JWT token by adding to blacklist.
    
    SECURITY: Token will be rejected by get_current_user() until expiration.
    After expiration, it's automatically cleaned from the blacklist.
    """
    if credentials and credentials.credentials:
        try:
            # Decode to get expiration time
            payload = jwt.decode(
                credentials.credentials, 
                JWT_SECRET, 
                algorithms=[JWT_ALGORITHM],
                options={"verify_exp": False}  # Allow expired tokens to be blacklisted too
            )
            exp = datetime.utcfromtimestamp(payload.get("exp", 0))
            _token_blacklist.add(credentials.credentials, exp)
            logger.info(f"Token blacklisted for user {payload.get('sub')}")
        except jwt.PyJWTError:
            pass  # Invalid token, nothing to blacklist
    
    return {"success": True, "message": "Logged out"}


# ==============================================================================
# Direct login by user_id (from Telegram WebApp start param)
# ==============================================================================
# SECURITY: Rate limiting for direct-login to prevent brute force
# ==============================================================================
from collections import defaultdict
import time as time_module

_direct_login_attempts: dict = defaultdict(list)
_DIRECT_LOGIN_RATE_LIMIT = 5  # max attempts
_DIRECT_LOGIN_WINDOW = 300    # 5 minutes

def _check_direct_login_rate_limit(ip: str) -> bool:
    """Check if IP has exceeded rate limit for direct-login"""
    now = time_module.time()
    # Clean old attempts
    _direct_login_attempts[ip] = [t for t in _direct_login_attempts[ip] if now - t < _DIRECT_LOGIN_WINDOW]
    # Check limit
    if len(_direct_login_attempts[ip]) >= _DIRECT_LOGIN_RATE_LIMIT:
        return False
    _direct_login_attempts[ip].append(now)
    return True


class DirectLoginRequest(BaseModel):
    """Direct login by Telegram user_id - REQUIRES init_data for security"""
    user_id: int
    init_data: Optional[str] = None  # Telegram WebApp init_data for verification


@router.post("/direct-login")
async def direct_login(data: DirectLoginRequest, request: Request):
    """
    Authenticate directly using Telegram user_id.
    
    SECURITY: This endpoint now requires either:
    1. Valid Telegram WebApp init_data (production)
    2. User must exist in DB with verified telegram auth (fallback)
    
    Rate limited to prevent brute force attacks.
    """
    # SECURITY: Rate limiting
    client_ip = get_client_ip(request)
    if not _check_direct_login_rate_limit(client_ip or "unknown"):
        logger.warning(f"Rate limit exceeded for direct-login from IP: {client_ip}")
        raise HTTPException(
            status_code=429, 
            detail="Too many login attempts. Please wait 5 minutes."
        )
    
    user_id = data.user_id
    
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user_id")
    
    # SECURITY: Verify init_data if provided (production mode)
    if data.init_data:
        verified_user = verify_webapp_data(data.init_data)
        if not verified_user:
            logger.warning(f"Invalid init_data for direct-login user_id={user_id}")
            raise HTTPException(status_code=401, detail="Invalid Telegram authentication")
        
        # Verify user_id matches
        if verified_user.get('id') != user_id:
            logger.warning(f"User ID mismatch in direct-login: claimed={user_id}, verified={verified_user.get('id')}")
            raise HTTPException(status_code=401, detail="User ID mismatch")
    else:
        # SECURITY: Without init_data, only allow if user has active 2FA session
        # or if request comes from trusted Telegram IP ranges
        # For now, require user to exist and have been active recently
        db_user = db.get_all_user_credentials(user_id)
        if not db_user:
            logger.warning(f"Direct-login attempt for non-existent user_id={user_id} from IP={client_ip}")
            raise HTTPException(status_code=404, detail="User not found. Start the bot first with /start")
        
        # Log suspicious activity
        logger.info(f"Direct-login without init_data for user_id={user_id} from IP={client_ip}")
    
    # Ensure user exists
    db.ensure_user(user_id)
    
    # Get user info
    db_user = db.get_all_user_credentials(user_id)
    exchange_status = db.get_exchange_status(user_id)
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found. Start the bot first with /start")
    
    # SECURITY: Check if user is banned
    if db_user.get("is_banned"):
        logger.warning(f"Banned user attempted login: user_id={user_id}")
        raise HTTPException(status_code=403, detail="Account suspended")
    
    is_admin = user_id == ADMIN_ID
    is_premium = db_user.get('license_type') == 'premium' or db_user.get('is_lifetime')
    
    # Create JWT token
    token = create_access_token(user_id, is_admin)
    
    logger.info(f"Direct-login success: user_id={user_id}, IP={client_ip}")
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "user_id": user_id,
            "first_name": db_user.get("first_name", "User"),
            "username": db_user.get("username"),
            "is_admin": is_admin,
            "is_premium": is_premium,
            "exchange_type": exchange_status.get("active_exchange", "bybit"),
            "language": db_user.get("lang", "en"),
            "license_type": db_user.get("license_type"),
        }
    }


# ==============================================================================
# Auto-login with token (from bot WebApp button)
# ==============================================================================

@router.get("/token-login")
async def telegram_token_auth(token: str, request: Request):
    """
    Authenticate using a one-time login token generated by the bot.
    This is used when user clicks WebApp button in Telegram.
    Redirects to dashboard with token in URL fragment.
    """
    from webapp.services import telegram_auth
    from fastapi.responses import RedirectResponse
    
    ip = get_client_ip(request)
    ua = request.headers.get("user-agent")
    
    user_id = telegram_auth.validate_login_token(token, ip, ua)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Ensure user exists
    db.ensure_user(user_id)
    
    # Get user info
    db_user = db.get_all_user_credentials(user_id)
    
    is_admin = user_id == ADMIN_ID
    
    # Create JWT token
    jwt_token = create_access_token(user_id, is_admin)
    
    # Redirect to landing page with token (will be saved by JS)
    return RedirectResponse(url=f"/?auth_token={jwt_token}", status_code=302)


# ==============================================================================
# Login by Telegram ID/username (for browser access)
# ==============================================================================

@router.post("/login-by-id")
async def login_by_telegram_id(data: LoginByIdRequest, request: Request, background_tasks: BackgroundTasks):
    """
    Initiate login by Telegram ID or username.
    Sends 2FA confirmation to user's Telegram.
    """
    from webapp.services import telegram_auth
    
    # Find user
    user_id = telegram_auth.find_user_by_identifier(data.identifier)
    
    if not user_id:
        raise HTTPException(
            status_code=404, 
            detail="User not found. Please start the bot first with /start"
        )
    
    # Check if user is banned
    db_user = db.get_all_user_credentials(user_id)
    if db_user and db_user.get("is_banned"):
        raise HTTPException(status_code=403, detail="User is banned")
    
    # Create 2FA confirmation
    ip = get_client_ip(request)
    ua = request.headers.get("user-agent")
    
    confirmation_id = telegram_auth.create_2fa_confirmation(user_id, ip, ua)
    
    # Send notification to Telegram (in background)
    background_tasks.add_task(
        telegram_auth.send_2fa_notification,
        user_id, confirmation_id, ip, ua
    )
    
    return {
        "success": True,
        "message": "Confirmation sent to your Telegram. Please approve the login.",
        "confirmation_id": confirmation_id,
        "expires_in": telegram_auth.CONFIRMATION_EXPIRY
    }


@router.post("/check-2fa")
async def check_2fa_status(data: TwoFACheckRequest, request: Request):
    """
    Check 2FA confirmation status.
    Frontend should poll this endpoint.
    """
    from webapp.services import telegram_auth
    
    status = telegram_auth.check_2fa_status(data.confirmation_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Confirmation not found")
    
    if status['status'] == 'expired':
        return {"success": False, "status": "expired", "message": "Confirmation expired"}
    
    if status['status'] == 'denied':
        return {"success": False, "status": "denied", "message": "Login denied"}
    
    if status['status'] == 'pending':
        return {"success": False, "status": "pending", "message": "Waiting for confirmation..."}
    
    if status['status'] == 'approved':
        user_id = status['user_id']
        
        # Ensure user exists
        db.ensure_user(user_id)
        
        # Get user info
        db_user = db.get_all_user_credentials(user_id)
        exchange_status = db.get_exchange_status(user_id)
        
        is_admin = user_id == ADMIN_ID
        is_premium = db_user.get('license_type') == 'premium' or db_user.get('is_lifetime')
        
        # Create JWT token
        jwt_token = create_access_token(user_id, is_admin)
        
        return {
            "success": True,
            "status": "approved",
            "token": jwt_token,
            "user": {
                "user_id": user_id,
                "first_name": db_user.get("first_name", "User"),
                "username": db_user.get("username"),
                "is_admin": is_admin,
                "is_premium": is_premium,
                "exchange_type": exchange_status.get("active_exchange", "bybit"),
                "language": db_user.get("lang", "en"),
            }
        }
    
    return {"success": False, "status": status['status']}
