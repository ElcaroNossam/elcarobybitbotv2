"""
Authentication API routes
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import jwt
import os

router = APIRouter()
security = HTTPBearer()

SECRET_KEY = os.environ.get("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


class LoginRequest(BaseModel):
    telegram_id: int
    auth_hash: str  # Telegram auth widget hash


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserInfo(BaseModel):
    user_id: int
    username: Optional[str]
    is_admin: bool
    license_type: str


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate user via Telegram widget"""
    # TODO: Verify Telegram auth hash
    # For now, accept any valid telegram_id
    
    # Check user in database
    # user = await get_user(request.telegram_id)
    
    token = create_access_token({
        "sub": str(request.telegram_id),
        "type": "access"
    })
    
    return TokenResponse(
        access_token=token,
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600
    )


@router.get("/me", response_model=UserInfo)
async def get_current_user(payload: dict = Depends(verify_token)):
    """Get current authenticated user info"""
    user_id = int(payload.get("sub", 0))
    
    # TODO: Get user from database
    return UserInfo(
        user_id=user_id,
        username=None,
        is_admin=False,
        license_type="free"
    )


@router.post("/logout")
async def logout(payload: dict = Depends(verify_token)):
    """Logout current user (invalidate token)"""
    # For JWT, we just tell client to discard token
    return {"message": "Logged out successfully"}
