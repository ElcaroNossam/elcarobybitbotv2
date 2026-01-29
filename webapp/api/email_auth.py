"""
Email Authentication API
========================
Registration and login via email with password.
Allows users to access the platform without Telegram.
"""
import os
import re
import hashlib
import secrets
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
from collections import defaultdict
import time

from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from pydantic import BaseModel, EmailStr, validator
import jwt

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import db
from coin_params import ADMIN_ID

# Load .env
_env_file = Path(__file__).parent.parent.parent / ".env"
if _env_file.exists():
    with open(_env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

logger = logging.getLogger(__name__)

router = APIRouter()

# =============================================================================
# RATE LIMITING for auth endpoints
# =============================================================================
_rate_limit_attempts: dict = defaultdict(list)  # ip -> [timestamp, ...]
RATE_LIMIT_WINDOW = 300  # 5 minutes
RATE_LIMIT_MAX_ATTEMPTS = 5  # max 5 attempts per window for sensitive ops
RATE_LIMIT_MAX_REGISTER = 3  # max 3 registration attempts per window


def check_rate_limit(ip: str, max_attempts: int = RATE_LIMIT_MAX_ATTEMPTS) -> None:
    """Check if IP has exceeded rate limit, raise HTTPException if so"""
    now = time.time()
    # Clean old entries
    _rate_limit_attempts[ip] = [t for t in _rate_limit_attempts[ip] if now - t < RATE_LIMIT_WINDOW]
    
    if len(_rate_limit_attempts[ip]) >= max_attempts:
        wait_time = int(RATE_LIMIT_WINDOW - (now - _rate_limit_attempts[ip][0]))
        raise HTTPException(
            status_code=429, 
            detail=f"Too many attempts. Please try again in {wait_time} seconds."
        )
    
    _rate_limit_attempts[ip].append(now)


def get_client_ip(request: Request) -> str:
    """Get client IP from request, considering X-Forwarded-For header"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# =============================================================================
# JWT CONFIG
# =============================================================================

# JWT Config
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is required")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 168  # 7 days

# Email Config
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@enliko.com")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

# Redis for verification codes (multi-worker support)
from core.redis_client import get_redis
_redis_available = False  # Set to True when Redis connected

# Fallback in-memory storage (single worker only)
_verification_codes: dict = {}  # email -> {code, expires, user_data}
_password_reset_codes: dict = {}  # email -> {code, expires}


async def _get_verification_code(email: str) -> Optional[dict]:
    """Get verification code from Redis or fallback to memory"""
    email = email.lower()
    try:
        redis = await get_redis()
        if redis._connected:
            data = await redis.get_verification_code(email)
            if data:
                return data
    except Exception:
        pass
    # Fallback to in-memory
    pending = _verification_codes.get(email)
    if pending:
        if datetime.utcnow() > pending.get('expires', datetime.min):
            del _verification_codes[email]
            return None
        return pending
    return None


async def _set_verification_code(email: str, data: dict):
    """Store verification code in Redis and fallback memory"""
    email = email.lower()
    try:
        redis = await get_redis()
        if redis._connected:
            await redis.set_verification_code(email, data, ttl=900)  # 15 min
    except Exception:
        pass
    # Also store in memory as fallback
    _verification_codes[email] = data


async def _delete_verification_code(email: str):
    """Delete verification code from Redis and memory"""
    email = email.lower()
    try:
        redis = await get_redis()
        if redis._connected:
            await redis.delete_verification_code(email)
    except Exception:
        pass
    _verification_codes.pop(email, None)


async def _get_password_reset_code(email: str) -> Optional[dict]:
    """Get password reset code from Redis or fallback to memory"""
    email = email.lower()
    try:
        redis = await get_redis()
        if redis._connected:
            data = await redis.get_password_reset_code(email)
            if data:
                return data
    except Exception:
        pass
    # Fallback to in-memory
    pending = _password_reset_codes.get(email)
    if pending:
        if datetime.utcnow() > pending.get('expires', datetime.min):
            del _password_reset_codes[email]
            return None
        return pending
    return None


async def _set_password_reset_code(email: str, data: dict):
    """Store password reset code in Redis and fallback memory"""
    email = email.lower()
    try:
        redis = await get_redis()
        if redis._connected:
            await redis.set_password_reset_code(email, data, ttl=3600)  # 1 hour
    except Exception:
        pass
    _password_reset_codes[email] = data


async def _delete_password_reset_code(email: str):
    """Delete password reset code from Redis and memory"""
    email = email.lower()
    try:
        redis = await get_redis()
        if redis._connected:
            await redis.delete_password_reset_code(email)
    except Exception:
        pass
    _password_reset_codes.pop(email, None)


# =============================================================================
# MODELS
# =============================================================================

class EmailRegisterRequest(BaseModel):
    """Email registration request"""
    email: EmailStr
    password: str
    name: Optional[str] = None
    first_name: Optional[str] = None  # iOS compatibility
    last_name: Optional[str] = None   # iOS compatibility
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
            raise ValueError('Password must contain letters and numbers')
        return v
    
    @property
    def display_name(self) -> Optional[str]:
        """Get display name from either name or first_name/last_name"""
        if self.name:
            return self.name
        if self.first_name:
            full_name = self.first_name
            if self.last_name:
                full_name = f"{self.first_name} {self.last_name}"
            return full_name
        return None


class EmailLoginRequest(BaseModel):
    """Email login request"""
    email: EmailStr
    password: str


class EmailVerifyRequest(BaseModel):
    """Email verification request"""
    email: EmailStr
    code: str


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    """Password reset confirm"""
    email: EmailStr
    code: str
    new_password: str


class GuestTokenRequest(BaseModel):
    """Guest access token request"""
    device_id: Optional[str] = None


# =============================================================================
# HELPERS
# =============================================================================

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash password with salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return hashed.hex(), salt


def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify password against hash"""
    computed, _ = hash_password(password, salt)
    return secrets.compare_digest(computed, hashed)


def create_access_token(user_id: int, is_admin: bool = False, is_guest: bool = False) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "sub": str(user_id),
        "is_admin": is_admin,
        "is_guest": is_guest,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_verification_code() -> str:
    """Generate 6-digit verification code"""
    return str(secrets.randbelow(900000) + 100000)


def generate_email_user_id() -> int:
    """Generate unique user_id for email users (negative to avoid Telegram ID conflicts)"""
    # Use negative IDs for email users to distinguish from Telegram users
    # Format: -1XXXXXXXXXX where X are random digits
    return -1 * (1000000000 + secrets.randbelow(9000000000))


async def send_email(to: str, subject: str, body_html: str) -> bool:
    """Send email via SMTP"""
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning(f"SMTP not configured, would send to {to}: {subject}")
        return True  # Pretend success in dev mode
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_FROM
        msg['To'] = to
        
        # Plain text fallback
        text_body = re.sub(r'<[^>]+>', '', body_html)
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(body_html, 'html'))
        
        if SMTP_USE_TLS:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM, [to], msg.as_string())
        server.quit()
        
        logger.info(f"Email sent to {to}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return False


# =============================================================================
# DATABASE HELPERS
# =============================================================================

def get_email_user(email: str) -> Optional[dict]:
    """Get user by email from database"""
    try:
        from core.db_postgres import execute_one
        row = execute_one(
            "SELECT * FROM email_users WHERE email = %s",
            (email.lower(),)
        )
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"get_email_user error: {e}")
        return None


def get_email_user_by_id(user_id: int) -> Optional[dict]:
    """Get email user by user_id from database"""
    try:
        from core.db_postgres import execute_one
        row = execute_one(
            "SELECT * FROM email_users WHERE user_id = %s",
            (user_id,)
        )
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"get_email_user_by_id error: {e}")
        return None


def create_email_user(email: str, password_hash: str, password_salt: str, name: Optional[str] = None) -> Optional[int]:
    """Create email user in database"""
    try:
        from core.db_postgres import execute_one, get_conn
        
        user_id = generate_email_user_id()
        
        # Create in email_users table with RETURNING to verify insertion
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO email_users (user_id, email, password_hash, password_salt, name, is_verified, created_at)
                VALUES (%s, %s, %s, %s, %s, TRUE, NOW())
                ON CONFLICT (email) DO UPDATE SET 
                    user_id = EXCLUDED.user_id,
                    password_hash = EXCLUDED.password_hash,
                    password_salt = EXCLUDED.password_salt,
                    name = EXCLUDED.name,
                    is_verified = TRUE,
                    updated_at = NOW()
                RETURNING user_id
            """, (user_id, email.lower(), password_hash, password_salt, name))
            result = cur.fetchone()
            
            if not result:
                logger.error(f"create_email_user: INSERT returned no result for {email}")
                return None
            
            inserted_user_id = result[0]
            logger.info(f"email_users INSERT success: {email} -> user_id={inserted_user_id}")
        
        # Also ensure user exists in main users table with is_allowed = 1
        db.ensure_user(inserted_user_id)
        if name:
            db.set_user_field(inserted_user_id, "first_name", name)
        # Email users should be allowed by default
        db.set_user_field(inserted_user_id, "is_allowed", 1)
        
        logger.info(f"Created email user: {email} -> user_id={inserted_user_id}, is_allowed=1")
        return inserted_user_id
    except Exception as e:
        logger.error(f"create_email_user error: {e}", exc_info=True)
        return None


def update_email_user_password(email: str, password_hash: str, password_salt: str) -> bool:
    """Update email user password"""
    try:
        from core.db_postgres import execute
        execute(
            "UPDATE email_users SET password_hash = %s, password_salt = %s, updated_at = NOW() WHERE email = %s",
            (password_hash, password_salt, email.lower())
        )
        return True
    except Exception as e:
        logger.error(f"update_email_user_password error: {e}")
        return False


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/register")
async def email_register(request: Request, data: EmailRegisterRequest, background_tasks: BackgroundTasks):
    """
    Register new user with email.
    Sends verification code to email.
    """
    # SECURITY: Rate limit registration attempts
    ip = get_client_ip(request)
    check_rate_limit(ip, RATE_LIMIT_MAX_REGISTER)
    
    email = data.email.lower()
    
    # Check if email already registered
    existing = get_email_user(email)
    if existing and existing.get('is_verified'):
        raise HTTPException(400, "Email already registered")
    
    # Generate verification code
    code = generate_verification_code()
    expires = datetime.utcnow() + timedelta(minutes=15)
    
    # Hash password
    password_hash, password_salt = hash_password(data.password)
    
    # Store pending registration (Redis + fallback memory)
    await _set_verification_code(email, {
        'code': code,
        'expires': expires.isoformat(),
        'password_hash': password_hash,
        'password_salt': password_salt,
        'name': data.display_name  # Use display_name for iOS compatibility
    })
    
    # Send verification email
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #dc2626;">🚀 Welcome to Enliko!</h2>
        <p>Your verification code is:</p>
        <div style="background: #1a1a1a; color: #22c55e; font-size: 32px; font-weight: bold; 
                    padding: 20px; text-align: center; border-radius: 8px; letter-spacing: 8px;">
            {code}
        </div>
        <p style="color: #666; margin-top: 20px;">This code expires in 15 minutes.</p>
        <p style="color: #666;">If you didn't request this, please ignore this email.</p>
    </div>
    """
    
    background_tasks.add_task(send_email, email, "Enliko Verification Code", html)
    
    return {
        "success": True,
        "message": "Verification code sent to your email",
        "email": email
    }


@router.post("/verify")
async def email_verify(data: EmailVerifyRequest):
    """
    Verify email with code and complete registration.
    """
    email = data.email.lower()
    
    pending = await _get_verification_code(email)
    if not pending:
        raise HTTPException(400, "No pending verification for this email")
    
    # Parse expires from ISO format (Redis stores as string)
    expires = pending.get('expires')
    if isinstance(expires, str):
        expires = datetime.fromisoformat(expires)
    
    if datetime.utcnow() > expires:
        await _delete_verification_code(email)
        raise HTTPException(400, "Verification code expired")
    
    if pending['code'] != data.code:
        raise HTTPException(400, "Invalid verification code")
    
    # Create user
    user_id = create_email_user(
        email=email,
        password_hash=pending['password_hash'],
        password_salt=pending['password_salt'],
        name=pending.get('name')
    )
    
    if not user_id:
        raise HTTPException(500, "Failed to create user")
    
    # Clean up
    await _delete_verification_code(email)
    
    # Create tokens
    token = create_access_token(user_id, is_admin=False)
    # Generate refresh token (hash of user_id + email + secret)
    refresh_secret = os.getenv("JWT_SECRET", "enliko_default_secret")
    refresh_token = hashlib.sha256(f"{user_id}:{email}:{refresh_secret}".encode()).hexdigest()
    
    # Build full user object for iOS compatibility
    name = pending.get('name')
    return {
        "success": True,
        "token": token,
        "refresh_token": refresh_token,
        "user_id": user_id,
        "user": {
            "id": user_id,  # Required for iOS Identifiable
            "user_id": user_id,
            "email": email,
            "name": name,
            "first_name": name.split()[0] if name and ' ' in name else name,
            "last_name": name.split()[-1] if name and ' ' in name else None,
            "is_admin": False,
            "is_allowed": True,
            "is_premium": False,
            "license_type": "free",
            "exchange_type": "bybit",
            "trading_mode": "demo",
            "lang": "en"
        }
    }


@router.post("/login")
async def email_login(data: EmailLoginRequest, request: Request):
    """
    Login with email and password.
    """
    # SECURITY: Rate limit login attempts to prevent brute force
    ip = get_client_ip(request)
    check_rate_limit(ip, RATE_LIMIT_MAX_ATTEMPTS)
    
    email = data.email.lower()
    
    user = get_email_user(email)
    if not user:
        raise HTTPException(401, "Invalid email or password")
    
    if not user.get('is_verified'):
        raise HTTPException(401, "Email not verified")
    
    if not verify_password(data.password, user['password_hash'], user['password_salt']):
        raise HTTPException(401, "Invalid email or password")
    
    user_id = user['user_id']
    is_admin = user_id == ADMIN_ID
    
    # Get additional user data
    db_user = db.get_all_user_credentials(user_id) or {}
    
    # Create tokens
    token = create_access_token(user_id, is_admin)
    # Generate refresh token (hash of user_id + email + secret)
    refresh_secret = os.getenv("JWT_SECRET", "enliko_default_secret")
    refresh_token = hashlib.sha256(f"{user_id}:{email}:{refresh_secret}".encode()).hexdigest()
    
    # Build full user object for iOS compatibility
    name = user.get('name') or db_user.get('first_name')
    return {
        "success": True,
        "token": token,
        "refresh_token": refresh_token,
        "user_id": user_id,
        "user": {
            "id": user_id,  # Required for iOS Identifiable
            "user_id": user_id,
            "email": email,
            "name": name,
            "first_name": name.split()[0] if name and ' ' in name else name,
            "last_name": name.split()[-1] if name and ' ' in name else None,
            "is_admin": is_admin,
            "is_allowed": db_user.get('is_allowed', True),
            "is_premium": db_user.get('license_type') not in (None, 'free'),
            "license_type": db_user.get('license_type', 'free'),
            "exchange_type": db_user.get('exchange_type', 'bybit'),
            "trading_mode": db_user.get('trading_mode', 'demo'),
            "lang": db_user.get('lang', 'en')
        }
    }


@router.post("/forgot-password")
async def forgot_password(data: PasswordResetRequest, background_tasks: BackgroundTasks):
    """
    Request password reset - sends code to email.
    """
    email = data.email.lower()
    
    user = get_email_user(email)
    if not user:
        # Don't reveal if email exists
        return {"success": True, "message": "If email exists, reset code was sent"}
    
    code = generate_verification_code()
    expires = datetime.utcnow() + timedelta(minutes=15)
    
    # Store in Redis + fallback memory
    await _set_password_reset_code(email, {
        'code': code,
        'expires': expires.isoformat()
    })
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #dc2626;">🔐 Password Reset</h2>
        <p>Your password reset code is:</p>
        <div style="background: #1a1a1a; color: #f59e0b; font-size: 32px; font-weight: bold; 
                    padding: 20px; text-align: center; border-radius: 8px; letter-spacing: 8px;">
            {code}
        </div>
        <p style="color: #666; margin-top: 20px;">This code expires in 15 minutes.</p>
        <p style="color: #666;">If you didn't request this, please ignore this email.</p>
    </div>
    """
    
    background_tasks.add_task(send_email, email, "Enliko Password Reset", html)
    
    return {"success": True, "message": "If email exists, reset code was sent"}


@router.post("/reset-password")
async def reset_password(request: Request, data: PasswordResetConfirmRequest):
    """
    Reset password with code.
    """
    # SECURITY: Rate limit password reset attempts
    ip = get_client_ip(request)
    check_rate_limit(ip, RATE_LIMIT_MAX_ATTEMPTS)
    
    email = data.email.lower()
    
    pending = await _get_password_reset_code(email)
    if not pending:
        raise HTTPException(400, "No pending reset for this email")
    
    # Parse expires from ISO format (Redis stores as string)
    expires = pending.get('expires')
    if isinstance(expires, str):
        expires = datetime.fromisoformat(expires)
    
    if datetime.utcnow() > expires:
        await _delete_password_reset_code(email)
        raise HTTPException(400, "Reset code expired")
    
    if pending['code'] != data.code:
        raise HTTPException(400, "Invalid reset code")
    
    # Validate new password
    if len(data.new_password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    
    # Update password
    password_hash, password_salt = hash_password(data.new_password)
    if not update_email_user_password(email, password_hash, password_salt):
        raise HTTPException(500, "Failed to update password")
    
    await _delete_password_reset_code(email)
    
    return {"success": True, "message": "Password updated successfully"}


@router.post("/guest")
async def guest_access(data: GuestTokenRequest):
    """
    Get guest access token for browsing without registration.
    Limited functionality - can view pricing, features, but not trade.
    """
    # Generate temporary guest ID
    guest_id = -secrets.randbelow(1000000)  # Negative ID for guests
    
    token = create_access_token(guest_id, is_admin=False, is_guest=True)
    
    return {
        "success": True,
        "token": token,
        "user": {
            "user_id": guest_id,
            "is_guest": True,
            "is_admin": False,
            "license_type": "guest",
            "features": {
                "view_pricing": True,
                "view_features": True,
                "view_terminal": True,  # Demo mode
                "trading": False,
                "backtesting": False,
                "ai_signals": False
            }
        }
    }


@router.get("/check-email/{email}")
async def check_email_available(email: str):
    """
    Check if email is available for registration.
    """
    try:
        EmailStr.validate(email)
    except (ValueError, TypeError):
        raise HTTPException(400, "Invalid email format")
    
    user = get_email_user(email.lower())
    
    return {
        "available": user is None or not user.get('is_verified'),
        "email": email.lower()
    }
