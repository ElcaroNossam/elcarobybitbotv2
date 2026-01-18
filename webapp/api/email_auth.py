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

# JWT Config
JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 168  # 7 days

# Email Config
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@triacelo.com")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

# Verification codes storage (in production use Redis)
_verification_codes: dict = {}  # email -> {code, expires, user_data}
_password_reset_codes: dict = {}  # email -> {code, expires}


# =============================================================================
# MODELS
# =============================================================================

class EmailRegisterRequest(BaseModel):
    """Email registration request"""
    email: EmailStr
    password: str
    name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
            raise ValueError('Password must contain letters and numbers')
        return v


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


def create_email_user(email: str, password_hash: str, password_salt: str, name: Optional[str] = None) -> Optional[int]:
    """Create email user in database"""
    try:
        from core.db_postgres import execute, execute_one
        
        user_id = generate_email_user_id()
        
        # Create in email_users table
        execute("""
            INSERT INTO email_users (user_id, email, password_hash, password_salt, name, is_verified, created_at)
            VALUES (%s, %s, %s, %s, %s, TRUE, NOW())
            ON CONFLICT (email) DO NOTHING
        """, (user_id, email.lower(), password_hash, password_salt, name))
        
        # Also ensure user exists in main users table
        db.ensure_user(user_id)
        if name:
            db.set_user_field(user_id, "first_name", name)
        
        logger.info(f"Created email user: {email} -> user_id={user_id}")
        return user_id
    except Exception as e:
        logger.error(f"create_email_user error: {e}")
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
async def email_register(data: EmailRegisterRequest, background_tasks: BackgroundTasks):
    """
    Register new user with email.
    Sends verification code to email.
    """
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
    
    # Store pending registration
    _verification_codes[email] = {
        'code': code,
        'expires': expires,
        'password_hash': password_hash,
        'password_salt': password_salt,
        'name': data.name
    }
    
    # Send verification email
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #dc2626;">🚀 Welcome to Triacelo!</h2>
        <p>Your verification code is:</p>
        <div style="background: #1a1a1a; color: #22c55e; font-size: 32px; font-weight: bold; 
                    padding: 20px; text-align: center; border-radius: 8px; letter-spacing: 8px;">
            {code}
        </div>
        <p style="color: #666; margin-top: 20px;">This code expires in 15 minutes.</p>
        <p style="color: #666;">If you didn't request this, please ignore this email.</p>
    </div>
    """
    
    background_tasks.add_task(send_email, email, "Triacelo Verification Code", html)
    
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
    
    pending = _verification_codes.get(email)
    if not pending:
        raise HTTPException(400, "No pending verification for this email")
    
    if datetime.utcnow() > pending['expires']:
        del _verification_codes[email]
        raise HTTPException(400, "Verification code expired")
    
    if pending['code'] != data.code:
        raise HTTPException(400, "Invalid verification code")
    
    # Create user
    user_id = create_email_user(
        email=email,
        password_hash=pending['password_hash'],
        password_salt=pending['password_salt'],
        name=pending['name']
    )
    
    if not user_id:
        raise HTTPException(500, "Failed to create user")
    
    # Clean up
    del _verification_codes[email]
    
    # Create token
    token = create_access_token(user_id, is_admin=False)
    
    return {
        "success": True,
        "token": token,
        "user": {
            "user_id": user_id,
            "email": email,
            "name": pending.get('name'),
            "is_admin": False,
            "license_type": "free"
        }
    }


@router.post("/login")
async def email_login(data: EmailLoginRequest, request: Request):
    """
    Login with email and password.
    """
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
    
    token = create_access_token(user_id, is_admin)
    
    return {
        "success": True,
        "token": token,
        "user": {
            "user_id": user_id,
            "email": email,
            "name": user.get('name') or db_user.get('first_name'),
            "is_admin": is_admin,
            "license_type": db_user.get('license_type', 'free')
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
    
    _password_reset_codes[email] = {
        'code': code,
        'expires': expires
    }
    
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
    
    background_tasks.add_task(send_email, email, "Triacelo Password Reset", html)
    
    return {"success": True, "message": "If email exists, reset code was sent"}


@router.post("/reset-password")
async def reset_password(data: PasswordResetConfirmRequest):
    """
    Reset password with code.
    """
    email = data.email.lower()
    
    pending = _password_reset_codes.get(email)
    if not pending:
        raise HTTPException(400, "No pending reset for this email")
    
    if datetime.utcnow() > pending['expires']:
        del _password_reset_codes[email]
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
    
    del _password_reset_codes[email]
    
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
    except:
        raise HTTPException(400, "Invalid email format")
    
    user = get_email_user(email.lower())
    
    return {
        "available": user is None or not user.get('is_verified'),
        "email": email.lower()
    }
