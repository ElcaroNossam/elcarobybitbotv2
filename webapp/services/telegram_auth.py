# -*- coding: utf-8 -*-
"""
Telegram 2FA Authentication Service for Lyxen Trading Bot

Provides:
- Auto-login tokens for webapp access from bot
- 2FA confirmation via Telegram bot
- Login via Telegram ID/username from browser
- Session management
"""
import os
import secrets
import hashlib
import json
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Tuple
import aiohttp
from pathlib import Path

logger = logging.getLogger(__name__)

# Load .env file if not already loaded
_env_file = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / ".env"
if _env_file.exists() and not os.getenv("TELEGRAM_TOKEN"):
    with open(_env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

# Token expiry times
LOGIN_TOKEN_EXPIRY = 300  # 5 minutes for auto-login
SESSION_TOKEN_EXPIRY = 86400 * 7  # 7 days for sessions
CONFIRMATION_EXPIRY = 180  # 3 minutes for 2FA confirmation

# Webapp URL (configurable via env)
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:8765")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN", "")

# PostgreSQL database helper
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from webapp.api.db_helper import get_db


def init_auth_tables():
    """Initialize authentication tables using PostgreSQL"""
    try:
        with get_db() as con:
            cur = con.cursor()
            
            # Login tokens - for auto-login from bot
            cur.execute("""
                CREATE TABLE IF NOT EXISTS login_tokens (
                    token TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    ip_address TEXT,
                    user_agent TEXT
                )
            """)
            
            # 2FA confirmations - pending login confirmations
            cur.execute("""
                CREATE TABLE IF NOT EXISTS twofa_confirmations (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    session_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    confirmed_at TIMESTAMP
                )
            """)
            
            # Active sessions
            cur.execute("""
                CREATE TABLE IF NOT EXISTS webapp_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    token_hash TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    last_activity TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_login_tokens_user ON login_tokens(user_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_login_tokens_expires ON login_tokens(expires_at)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_twofa_user ON twofa_confirmations(user_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON webapp_sessions(user_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_hash ON webapp_sessions(token_hash)")
            
            con.commit()
    except Exception as e:
        logger.error(f"Failed to init auth tables: {e}")


# ==============================================================================
# Auto-Login Token Generation (from bot)
# ==============================================================================

def generate_login_token(user_id: int) -> Tuple[str, str]:
    """
    Generate a one-time login token for auto-login from bot.
    Returns (token, webapp_url_with_token)
    """
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(seconds=LOGIN_TOKEN_EXPIRY)
    
    with get_db() as con:
        cur = con.cursor()
        
        # Clean up old tokens for this user
        cur.execute("DELETE FROM login_tokens WHERE user_id = ?", (user_id,))
        
        # Insert new token
        cur.execute("""
            INSERT INTO login_tokens (token, user_id, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        """, (token, user_id, now, expires))
        
        con.commit()
    
    # Generate webapp URL with token
    login_url = f"{WEBAPP_URL}/api/auth/token-login?token={token}"
    
    return token, login_url


def validate_login_token(token: str, ip_address: str = None, user_agent: str = None) -> Optional[int]:
    """
    Validate a login token and return user_id if valid.
    Marks token as used after validation.
    """
    with get_db() as con:
        cur = con.cursor()
        
        now = datetime.now(timezone.utc)
        
        cur.execute("""
            SELECT user_id, expires_at, used
            FROM login_tokens
            WHERE token = ?
        """, (token,))
        
        row = cur.fetchone()
        
        if not row:
            return None
        
        # Check if already used
        if row['used']:
            return None
        
        # Check expiry
        expires = row['expires_at']
        if isinstance(expires, str):
            expires = datetime.fromisoformat(expires.replace('Z', '+00:00'))
        if now > expires:
            return None
        
        # Mark as used and update IP/UA
        cur.execute("""
            UPDATE login_tokens
            SET used = TRUE, ip_address = ?, user_agent = ?
            WHERE token = ?
        """, (ip_address, user_agent, token))
        
        con.commit()
        
        return row['user_id']


# ==============================================================================
# 2FA Confirmation (login from browser)
# ==============================================================================

def create_2fa_confirmation(user_id: int, ip_address: str = None, user_agent: str = None) -> str:
    """
    Create a 2FA confirmation request.
    Returns confirmation_id.
    """
    confirmation_id = secrets.token_urlsafe(16)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(seconds=CONFIRMATION_EXPIRY)
    
    with get_db() as con:
        cur = con.cursor()
        
        # Clean up old pending confirmations for this user
        cur.execute("""
            DELETE FROM twofa_confirmations 
            WHERE user_id = ? AND status = 'pending'
        """, (user_id,))
        
        # Create new confirmation
        cur.execute("""
            INSERT INTO twofa_confirmations (id, user_id, ip_address, user_agent, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (confirmation_id, user_id, ip_address, user_agent, now, expires))
        
        con.commit()
    
    return confirmation_id


def check_2fa_status(confirmation_id: str) -> Optional[dict]:
    """
    Check the status of a 2FA confirmation.
    Returns dict with status and user_id, or None if not found.
    """
    with get_db() as con:
        cur = con.cursor()
        
        cur.execute("""
            SELECT id, user_id, status, expires_at, confirmed_at
            FROM twofa_confirmations
            WHERE id = ?
        """, (confirmation_id,))
        
        row = cur.fetchone()
        
        if not row:
            return None
        
        # Check expiry
        now = datetime.now(timezone.utc)
        expires = row['expires_at']
        if isinstance(expires, str):
            expires = datetime.fromisoformat(expires.replace('Z', '+00:00'))
        
        if now > expires and row['status'] == 'pending':
            return {'status': 'expired', 'user_id': row['user_id']}
        
        return {
            'id': row['id'],
            'user_id': row['user_id'],
            'status': row['status'],
            'confirmed_at': str(row['confirmed_at']) if row['confirmed_at'] else None
        }


def confirm_2fa(confirmation_id: str, approved: bool) -> bool:
    """
    Confirm or deny a 2FA request.
    Called from bot callback.
    """
    with get_db() as con:
        cur = con.cursor()
        
        now = datetime.now(timezone.utc)
        
        # Check if exists and is pending
        cur.execute("""
            SELECT status, expires_at FROM twofa_confirmations WHERE id = ?
        """, (confirmation_id,))
        
        row = cur.fetchone()
        if not row or row['status'] != 'pending':
            return False
        
        # Check expiry
        expires = row['expires_at']
        if isinstance(expires, str):
            expires = datetime.fromisoformat(expires.replace('Z', '+00:00'))
        if now > expires:
            return False
        
        # Update status
        status = 'approved' if approved else 'denied'
        cur.execute("""
            UPDATE twofa_confirmations
            SET status = ?, confirmed_at = ?
            WHERE id = ?
        """, (status, now, confirmation_id))
        
        con.commit()
        
        return True


# ==============================================================================
# Find user by Telegram ID or username
# ==============================================================================

def find_user_by_identifier(identifier: str) -> Optional[int]:
    """
    Find user by Telegram ID or @username.
    Returns user_id if found, None otherwise.
    """
    with get_db() as con:
        cur = con.cursor()
        
        # Try as numeric ID first
        try:
            user_id = int(identifier.strip())
            cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            if row:
                return row['user_id']
        except ValueError:
            pass
        
        # Try as username (with or without @)
        username = identifier.strip().lstrip('@').lower()
        if username:
            cur.execute("SELECT user_id FROM users WHERE LOWER(username) = ?", (username,))
            row = cur.fetchone()
            if row:
                return row['user_id']
        
        return None


# ==============================================================================
# Bot Integration - Send 2FA Notifications
# ==============================================================================

async def send_2fa_notification(user_id: int, confirmation_id: str, ip_address: str = None, user_agent: str = None) -> bool:
    """
    Send 2FA confirmation request to user via Telegram bot.
    """
    if not TELEGRAM_BOT_TOKEN:
        return False
    
    # Get user language
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        import db
        cfg = db.get_user_config(user_id)
        lang = cfg.get("lang", "en") if cfg else "en"
    except Exception as e:
        logger.debug(f"Failed to get user language for {user_id}: {e}")
        lang = "en"
    
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    device = (user_agent[:50] + "...") if user_agent and len(user_agent) > 50 else (user_agent or "Unknown")
    
    # Translations
    translations = {
        "uk": {
            "title": "🔐 Підтвердження входу",
            "body": "Хтось намагається увійти у ваш акаунт:\n\n🌐 IP: {ip}\n📱 Пристрій: {device}\n⏰ Час: {time}\n\nЦе ви?",
            "approve": "✅ Підтвердити",
            "deny": "❌ Відхилити"
        },
        "ru": {
            "title": "🔐 Подтверждение входа",
            "body": "Кто-то пытается войти в ваш аккаунт:\n\n🌐 IP: {ip}\n📱 Устройство: {device}\n⏰ Время: {time}\n\nЭто вы?",
            "approve": "✅ Подтвердить",
            "deny": "❌ Отклонить"
        },
        "en": {
            "title": "🔐 Login Confirmation",
            "body": "Someone is trying to log into your account:\n\n🌐 IP: {ip}\n📱 Device: {device}\n⏰ Time: {time}\n\nIs this you?",
            "approve": "✅ Approve",
            "deny": "❌ Deny"
        },
        "de": {
            "title": "🔐 Anmeldebestätigung",
            "body": "Jemand versucht, sich in Ihr Konto einzuloggen:\n\n🌐 IP: {ip}\n📱 Gerät: {device}\n⏰ Zeit: {time}\n\nSind Sie das?",
            "approve": "✅ Bestätigen",
            "deny": "❌ Ablehnen"
        },
        "es": {
            "title": "🔐 Confirmación de inicio",
            "body": "Alguien está intentando acceder a su cuenta:\n\n🌐 IP: {ip}\n📱 Dispositivo: {device}\n⏰ Hora: {time}\n\n¿Es usted?",
            "approve": "✅ Aprobar",
            "deny": "❌ Rechazar"
        }
    }
    
    t = translations.get(lang, translations["en"])
    text = t["title"] + "\n\n" + t["body"].format(ip=ip_address or "Unknown", device=device, time=now)
    
    keyboard = {
        "inline_keyboard": [
            [
                {"text": t["approve"], "callback_data": f"twofa_approve:{confirmation_id}"},
                {"text": t["deny"], "callback_data": f"twofa_deny:{confirmation_id}"}
            ]
        ]
    }
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": user_id,
        "text": text,
        "reply_markup": keyboard
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                return resp.status == 200
    except Exception as e:
        print(f"Failed to send 2FA notification: {e}")
        return False


# ==============================================================================
# Cleanup
# ==============================================================================

def cleanup_expired():
    """Remove expired tokens and sessions"""
    with get_db() as con:
        cur = con.cursor()
        
        # Clean login tokens
        cur.execute("DELETE FROM login_tokens WHERE expires_at < NOW()")
        
        # Clean 2FA confirmations
        cur.execute("DELETE FROM twofa_confirmations WHERE expires_at < NOW() AND status = 'pending'")
        
        # Deactivate expired sessions
        cur.execute("UPDATE webapp_sessions SET is_active = FALSE WHERE expires_at < NOW()")
        
        # Delete very old sessions (30 days)
        cur.execute("DELETE FROM webapp_sessions WHERE expires_at < NOW() - INTERVAL '30 days'")
        
        con.commit()


# Initialize tables on import
try:
    init_auth_tables()
except Exception as e:
    print(f"Warning: Could not initialize auth tables: {e}")
