"""
License Blockchain API
======================
REST API endpoints for blockchain-integrated license management.

Endpoints:
- GET /api/license/blockchain/stats - Get blockchain license statistics
- GET /api/license/blockchain/user/{user_id} - Get user's blockchain licenses
- GET /api/license/blockchain/verify/{tx_hash} - Verify license on blockchain
- POST /api/license/blockchain/purchase - Purchase license with ELC
- GET /api/license/nft/user/{user_id} - Get user's license NFTs
- POST /api/license/nft/mint - Admin mint NFT (requires admin auth)
- GET /api/license/price - Calculate license price with discounts
"""

import time
import logging
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Header, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/license/blockchain", tags=["License Blockchain"])

# Admin ID for authorization
ADMIN_ID = 511692487


# ============================================
# MODELS
# ============================================

class PurchaseRequest(BaseModel):
    user_id: int
    license_type: str  # "premium", "basic", "enterprise"
    months: int = 1
    wallet_address: Optional[str] = None
    mint_nft: bool = True


class PriceCalculateRequest(BaseModel):
    license_type: str
    months: int
    staked_elc: float = 0


class MintNFTRequest(BaseModel):
    user_id: int
    tier: str  # "bronze", "silver", "gold", "platinum", "diamond"
    valid_months: int = 12
    wallet_address: Optional[str] = None


class BlockchainRecord(BaseModel):
    tx_hash: str
    user_id: int
    wallet_address: str
    license_type: str
    period_months: int
    amount_paid: float
    currency: str
    start_timestamp: int
    end_timestamp: int
    nft_token_id: Optional[str]
    block_number: int
    created_at: int
    is_active: bool


class LicenseNFT(BaseModel):
    token_id: str
    owner_id: int
    owner_wallet: str
    tier: str
    license_type: str
    valid_until: int
    metadata_uri: str
    minted_at: int
    tx_hash: str


class StatsResponse(BaseModel):
    total_licenses: int
    unique_users: int
    total_revenue_elc: float
    active_licenses: int
    total_nfts: int
    nft_breakdown: dict


# ============================================
# AUTH HELPERS
# ============================================

def verify_user_auth(authorization: str = Header(None)) -> int:
    """Extract and verify user ID from authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    
    # Simple token format: "Bearer user_id:signature"
    # In production, use proper JWT validation
    try:
        if authorization.startswith("Bearer "):
            token = authorization[7:]
            parts = token.split(":")
            user_id = int(parts[0])
            return user_id
    except:
        pass
    
    raise HTTPException(status_code=401, detail="Invalid authorization token")


def verify_admin_auth(authorization: str = Header(None)) -> int:
    """Verify admin authorization"""
    user_id = verify_user_auth(authorization)
    if user_id != ADMIN_ID:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user_id


# ============================================
# ENDPOINTS
# ============================================

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get blockchain license statistics (public)"""
    from services.license_blockchain_service import get_blockchain_license_stats
    
    stats = get_blockchain_license_stats()
    return StatsResponse(**stats)


@router.get("/user/{user_id}", response_model=List[BlockchainRecord])
async def get_user_licenses(
    user_id: int,
    active_only: bool = Query(False, description="Only return active licenses")
):
    """Get user's blockchain license records"""
    from services.license_blockchain_service import get_user_blockchain_licenses
    
    records = get_user_blockchain_licenses(user_id, active_only=active_only)
    
    result = []
    now = int(time.time())
    for r in records:
        record = BlockchainRecord(
            tx_hash=r.get("tx_hash", ""),
            user_id=r.get("user_id", 0),
            wallet_address=r.get("wallet_address", ""),
            license_type=r.get("license_type", ""),
            period_months=r.get("period_months", 0),
            amount_paid=r.get("amount_paid", 0),
            currency=r.get("currency", "ELC"),
            start_timestamp=r.get("start_timestamp", 0),
            end_timestamp=r.get("end_timestamp", 0),
            nft_token_id=r.get("nft_token_id"),
            block_number=r.get("block_number", 0),
            created_at=r.get("created_at", 0),
            is_active=r.get("end_timestamp", 0) > now
        )
        result.append(record)
    
    return result


@router.get("/verify/{tx_hash}")
async def verify_license(tx_hash: str):
    """Verify license purchase on blockchain"""
    from services.license_blockchain_service import verify_license_on_blockchain
    
    result = verify_license_on_blockchain(tx_hash)
    
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return result


@router.post("/price")
async def calculate_price(request: PriceCalculateRequest):
    """Calculate license price with staking discounts"""
    from services.license_blockchain_service import calculate_final_price
    
    price_info = calculate_final_price(
        license_type=request.license_type,
        months=request.months,
        staked_elc=request.staked_elc
    )
    
    return price_info


@router.post("/purchase")
async def purchase_license(
    request: PurchaseRequest,
    user_id: int = Depends(verify_user_auth)
):
    """
    Purchase license with ELC tokens.
    
    Flow:
    1. Calculate price with discounts
    2. Deduct ELC from user
    3. Create blockchain record
    4. Mint NFT (optional)
    5. Activate license
    """
    from services.license_blockchain_service import purchase_license_with_elc
    
    # Security: only allow purchasing for self or admin for others
    if request.user_id != user_id and user_id != ADMIN_ID:
        raise HTTPException(status_code=403, detail="Can only purchase license for yourself")
    
    result = purchase_license_with_elc(
        user_id=request.user_id,
        license_type=request.license_type,
        months=request.months,
        wallet_address=request.wallet_address,
        mint_nft=request.mint_nft
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400, 
            detail=result.get("message", result.get("error", "Purchase failed"))
        )
    
    return result


# ============================================
# NFT ENDPOINTS
# ============================================

nft_router = APIRouter(prefix="/api/license/nft", tags=["License NFT"])


@nft_router.get("/user/{user_id}", response_model=List[LicenseNFT])
async def get_user_nfts(user_id: int):
    """Get user's license NFTs"""
    from services.license_blockchain_service import get_user_license_nfts
    
    nfts = get_user_license_nfts(user_id)
    
    result = []
    for n in nfts:
        nft = LicenseNFT(
            token_id=n.get("token_id", ""),
            owner_id=n.get("owner_id", 0),
            owner_wallet=n.get("owner_wallet", ""),
            tier=n.get("tier", ""),
            license_type=n.get("license_type", ""),
            valid_until=n.get("valid_until", 0),
            metadata_uri=n.get("metadata_uri", ""),
            minted_at=n.get("minted_at", 0),
            tx_hash=n.get("tx_hash", "")
        )
        result.append(nft)
    
    return result


@nft_router.get("/all")
async def get_all_nfts(
    limit: int = Query(50, le=100),
    admin_id: int = Depends(verify_admin_auth)
):
    """Get all license NFTs (admin only)"""
    from services.license_blockchain_service import get_all_license_nfts
    
    nfts = get_all_license_nfts(limit=limit)
    return nfts


@nft_router.post("/mint")
async def mint_nft(
    request: MintNFTRequest,
    admin_id: int = Depends(verify_admin_auth)
):
    """
    Admin mint a license NFT.
    
    Tiers:
    - diamond: Lifetime/Special
    - platinum: Enterprise tier
    - gold: Premium 6-12 months
    - silver: Premium 1-3 months
    - bronze: Basic tier
    """
    from services.license_blockchain_service import admin_mint_license_nft
    
    result = admin_mint_license_nft(
        admin_id=admin_id,
        user_id=request.user_id,
        tier=request.tier,
        valid_months=request.valid_months,
        wallet_address=request.wallet_address
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Minting failed")
        )
    
    return result


@nft_router.post("/revoke/{token_id}")
async def revoke_nft(
    token_id: str,
    reason: str = Query(None),
    admin_id: int = Depends(verify_admin_auth)
):
    """Revoke a license NFT (admin only)"""
    from services.license_blockchain_service import admin_revoke_nft
    
    result = admin_revoke_nft(admin_id, token_id, reason)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Revocation failed")
        )
    
    return result


# ============================================
# SYNC ENDPOINTS
# ============================================

@router.post("/sync/{user_id}")
async def sync_user_license(
    user_id: int,
    admin_id: int = Depends(verify_admin_auth)
):
    """
    Sync user's database license to blockchain (admin only).
    Used for legacy migration.
    """
    from services.license_blockchain_service import sync_database_to_blockchain
    
    result = sync_database_to_blockchain(user_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Sync failed")
        )
    
    return result
