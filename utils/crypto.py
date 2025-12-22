"""
Cryptography utilities for API keys and passwords
"""
import os
import base64
import hashlib
import secrets
from typing import Optional

# Try to import cryptography, fall back to simple encoding
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


def _get_encryption_key() -> bytes:
    """Get or generate encryption key"""
    key_env = os.environ.get("ENCRYPTION_KEY")
    
    if key_env:
        return base64.urlsafe_b64decode(key_env)
    
    # Derive key from a secret (in production, use proper key management)
    secret = os.environ.get("BOT_SECRET")
    if not secret:
        raise RuntimeError("BOT_SECRET or ENCRYPTION_KEY environment variable is required")
    salt = b"bybit-bot-salt-v1"
    
    if HAS_CRYPTO:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(secret.encode()))
    else:
        # Simple fallback
        return base64.urlsafe_b64encode(
            hashlib.pbkdf2_hmac("sha256", secret.encode(), salt, 100000)
        )


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    if not data:
        return ""
    
    if HAS_CRYPTO:
        key = _get_encryption_key()
        f = Fernet(key)
        encrypted = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    else:
        # Simple XOR encoding (not secure, use cryptography in production)
        key = _get_encryption_key()
        encoded = bytes(a ^ b for a, b in zip(data.encode(), key * (len(data) // len(key) + 1)))
        return base64.urlsafe_b64encode(encoded).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not encrypted_data:
        return ""
    
    try:
        if HAS_CRYPTO:
            key = _get_encryption_key()
            f = Fernet(key)
            decrypted = f.decrypt(base64.urlsafe_b64decode(encrypted_data))
            return decrypted.decode()
        else:
            # Simple XOR decoding
            key = _get_encryption_key()
            encrypted = base64.urlsafe_b64decode(encrypted_data)
            decoded = bytes(a ^ b for a, b in zip(encrypted, key * (len(encrypted) // len(key) + 1)))
            return decoded.decode()
    except Exception:
        return ""


def hash_password(password: str) -> str:
    """Hash password for storage"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        100000
    )
    return f"{salt}${base64.b64encode(pwd_hash).decode()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash"""
    try:
        salt, hash_b64 = stored_hash.split("$")
        stored_pwd_hash = base64.b64decode(hash_b64)
        
        new_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt.encode(),
            100000
        )
        
        return secrets.compare_digest(stored_pwd_hash, new_hash)
    except Exception:
        return False


def generate_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


def generate_api_key() -> str:
    """Generate a random API key"""
    return f"bbot_{secrets.token_hex(16)}"
