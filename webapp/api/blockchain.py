"""
Blockchain API Router for TRC Token Management

Provides endpoints for:
- Wallet management (balance, deposit, withdraw)
- Network information (supported networks, fees)
- Admin/Sovereign operations (emission, burn, treasury)
- Analytics and statistics

Author: ElCaro Team
Date: January 2026
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

# Import blockchain functions
from core.blockchain import (
    # Wallet operations
    get_trc_wallet,
    get_trc_balance,
    deposit_trc,
    pay_with_trc,
    reward_trc,
    pay_license,
    get_license_price_trc,
    
    # Conversion
    usdt_to_trc,
    trc_to_usdt,
    
    # Network operations
    get_supported_networks,
    get_network_config,
    get_deposit_address,
    request_withdrawal,
    get_withdrawal_fees,
    get_network_status,
    
    # Stats and info
    get_global_stats,
    get_owner_dashboard,
    get_treasury_stats,
    
    # Sovereign operations
    is_sovereign_owner,
    emit_tokens,
    burn_tokens,
    set_monetary_policy,
    freeze_wallet,
    unfreeze_wallet,
    distribute_staking_rewards,
    transfer_from_treasury,
    
    # Config
    SOVEREIGN_OWNER_ID,
    LICENSE_PRICES_TRC,
    CryptoNetwork,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================
# PYDANTIC MODELS
# ============================================

class WalletResponse(BaseModel):
    address: str
    balance: float
    staked_balance: float = 0.0
    pending_rewards: float = 0.0
    status: str = "active"


class DepositRequest(BaseModel):
    user_id: int
    amount: float = Field(gt=0, description="Amount to deposit")


class WithdrawalRequest(BaseModel):
    user_id: int
    amount: float = Field(gt=0)
    network: str = Field(description="Network ID (trc20, bep20, etc.)")
    external_address: str


class PaymentRequest(BaseModel):
    user_id: int
    amount: float = Field(gt=0)
    description: str


class LicensePaymentRequest(BaseModel):
    user_id: int
    license_type: str = Field(description="premium or basic")
    months: int = Field(ge=1, le=12)


class EmissionRequest(BaseModel):
    admin_id: int
    amount: float = Field(gt=0)
    reason: str


class BurnRequest(BaseModel):
    admin_id: int
    amount: float = Field(gt=0)
    reason: str


class PolicyRequest(BaseModel):
    admin_id: int
    staking_apy: Optional[float] = None
    reserve_ratio: Optional[float] = None
    is_paused: Optional[bool] = None


class FreezeRequest(BaseModel):
    admin_id: int
    target_user_id: int
    reason: str = ""


class TreasuryTransferRequest(BaseModel):
    admin_id: int
    to_user_id: int
    amount: float = Field(gt=0)
    reason: str


class RewardRequest(BaseModel):
    user_id: int
    amount: float = Field(gt=0)
    reason: str = "bonus"


# ============================================
# PUBLIC ENDPOINTS
# ============================================

@router.get("/stats", summary="Get global blockchain statistics")
async def get_blockchain_stats():
    """Public: Get global TRC blockchain statistics"""
    return await get_global_stats()


@router.get("/networks", summary="Get supported networks")
async def list_supported_networks():
    """Public: Get list of all supported deposit/withdrawal networks"""
    return {
        "networks": get_supported_networks(),
        "count": len(get_supported_networks())
    }


@router.get("/networks/fees", summary="Get network withdrawal fees")
async def get_network_fees():
    """Public: Get withdrawal fees for all networks"""
    return get_withdrawal_fees()


@router.get("/networks/status", summary="Get network status")
async def get_all_network_status():
    """Public: Get status of all networks"""
    return get_network_status()


@router.get("/networks/{network_id}", summary="Get network details")
async def get_network_details(network_id: str):
    """Public: Get configuration for specific network"""
    config = get_network_config(network_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Network {network_id} not found")
    return config


@router.get("/fees", summary="Get withdrawal fees")
async def list_withdrawal_fees():
    """Public: Get withdrawal fees for all networks"""
    return {
        "fees": get_withdrawal_fees(),
        "note": "Fees are in USDT"
    }


@router.get("/prices/license", summary="Get license prices")
async def get_license_prices():
    """Public: Get all license prices in TRC"""
    return {
        "prices": LICENSE_PRICES_TRC,
        "currency": "TRC",
        "note": "1 TRC = 1 USDT"
    }


@router.get("/price/license/{license_type}/{months}", summary="Get specific license price")
async def get_specific_license_price(license_type: str, months: int):
    """Public: Get price for specific license and duration"""
    price = get_license_price_trc(license_type, months)
    return {
        "license_type": license_type,
        "months": months,
        "price_trc": price,
        "price_usdt": trc_to_usdt(price)
    }


# ============================================
# USER WALLET ENDPOINTS
# ============================================

@router.get("/wallet/{user_id}", summary="Get user wallet")
async def get_user_wallet(user_id: int):
    """Get wallet information for user"""
    wallet = await get_trc_wallet(user_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    return WalletResponse(
        address=wallet.address,
        balance=wallet.balance,
        staked_balance=wallet.staked_balance,
        pending_rewards=wallet.pending_rewards,
        status=wallet.status.value if hasattr(wallet.status, 'value') else str(wallet.status)
    )


@router.get("/wallet/{user_id}/balance", summary="Get user balance")
async def get_user_balance(user_id: int):
    """Get TRC balance for user"""
    balance = await get_trc_balance(user_id)
    return {
        "user_id": user_id,
        "balance_trc": balance,
        "balance_usdt": trc_to_usdt(balance)
    }


@router.get("/wallet/{user_id}/deposit-address/{network}", summary="Get deposit address")
async def get_user_deposit_address(user_id: int, network: str):
    """Get deposit address for specific network"""
    address_info = get_deposit_address(user_id, network)
    if not address_info:
        raise HTTPException(status_code=404, detail=f"Network {network} not supported")
    return address_info


# ============================================
# TRANSACTION ENDPOINTS
# ============================================

@router.post("/deposit", summary="Process deposit")
async def process_deposit(request: DepositRequest):
    """Process TRC deposit (admin/system use)"""
    success, message = await deposit_trc(request.user_id, request.amount)
    return {
        "success": success,
        "message": message
    }


@router.post("/withdraw", summary="Request withdrawal")
async def process_withdrawal(request: WithdrawalRequest):
    """Request withdrawal to external address"""
    success, message, info = await request_withdrawal(
        request.user_id,
        request.amount,
        request.network,
        request.external_address
    )
    
    return {
        "success": success,
        "message": message,
        "withdrawal": info
    }


@router.post("/pay", summary="Process payment")
async def process_payment(request: PaymentRequest):
    """Process TRC payment"""
    success, message = await pay_with_trc(
        request.user_id,
        request.amount,
        request.description
    )
    return {
        "success": success,
        "message": message
    }


@router.post("/pay/license", summary="Pay for license")
async def process_license_payment(request: LicensePaymentRequest):
    """Pay for license subscription with TRC"""
    success, message = await pay_license(
        request.user_id,
        request.license_type,
        request.months
    )
    
    return {
        "success": success,
        "message": message,
        "license_type": request.license_type,
        "months": request.months
    }


@router.post("/reward", summary="Give TRC reward")
async def give_reward(request: RewardRequest):
    """Give TRC reward to user (admin)"""
    success, message = await reward_trc(
        request.user_id,
        request.amount,
        request.reason
    )
    return {
        "success": success,
        "message": message
    }


# ============================================
# ADMIN/SOVEREIGN ENDPOINTS
# ============================================

@router.get("/admin/dashboard/{admin_id}", summary="Get owner dashboard")
async def get_admin_dashboard(admin_id: int):
    """Sovereign: Get comprehensive owner dashboard"""
    if not is_sovereign_owner(admin_id):
        raise HTTPException(status_code=403, detail="Access denied. Sovereign owner only.")
    
    dashboard = await get_owner_dashboard(admin_id)
    return dashboard


@router.get("/admin/treasury/{admin_id}", summary="Get treasury stats")
async def get_admin_treasury(admin_id: int):
    """Sovereign: Get treasury statistics"""
    if not is_sovereign_owner(admin_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return await get_treasury_stats(admin_id)


@router.get("/admin/networks/status", summary="Get all networks status")
async def get_all_network_status():
    """Admin: Get status of all networks"""
    return get_network_status()


@router.post("/admin/emit", summary="Emit new tokens")
async def emit_new_tokens(request: EmissionRequest):
    """Sovereign: Emit new TRC tokens"""
    if not is_sovereign_owner(request.admin_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await emit_tokens(
        request.admin_id,
        request.amount,
        request.reason
    )
    return result


@router.post("/admin/burn", summary="Burn tokens")
async def burn_existing_tokens(request: BurnRequest):
    """Sovereign: Burn TRC tokens from treasury"""
    if not is_sovereign_owner(request.admin_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await burn_tokens(
        request.admin_id,
        request.amount,
        request.reason
    )
    return result


@router.post("/admin/policy", summary="Set monetary policy")
async def update_monetary_policy(request: PolicyRequest):
    """Sovereign: Update monetary policy parameters"""
    if not is_sovereign_owner(request.admin_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    params = {}
    if request.staking_apy is not None:
        params["staking_apy"] = request.staking_apy
    if request.reserve_ratio is not None:
        params["reserve_ratio"] = request.reserve_ratio
    if request.is_paused is not None:
        params["is_paused"] = request.is_paused
    
    result = await set_monetary_policy(request.admin_id, **params)
    return result


@router.post("/admin/freeze", summary="Freeze wallet")
async def freeze_user_wallet(request: FreezeRequest):
    """Sovereign: Freeze a user's wallet"""
    if not is_sovereign_owner(request.admin_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    target_wallet = await get_trc_wallet(request.target_user_id)
    if not target_wallet:
        raise HTTPException(status_code=404, detail="Target wallet not found")
    
    result = await freeze_wallet(
        request.admin_id,
        target_wallet.address,
        request.reason
    )
    return result


@router.post("/admin/unfreeze", summary="Unfreeze wallet")
async def unfreeze_user_wallet(request: FreezeRequest):
    """Sovereign: Unfreeze a user's wallet"""
    if not is_sovereign_owner(request.admin_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    target_wallet = await get_trc_wallet(request.target_user_id)
    if not target_wallet:
        raise HTTPException(status_code=404, detail="Target wallet not found")
    
    result = await unfreeze_wallet(
        request.admin_id,
        target_wallet.address
    )
    return result


@router.post("/admin/distribute-rewards", summary="Distribute staking rewards")
async def distribute_rewards(admin_id: int = Query(...)):
    """Sovereign: Distribute staking rewards to all stakers"""
    if not is_sovereign_owner(admin_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await distribute_staking_rewards(admin_id)
    return result


@router.post("/admin/treasury-transfer", summary="Transfer from treasury")
async def treasury_transfer(request: TreasuryTransferRequest):
    """Sovereign: Transfer TRC from treasury to user"""
    if not is_sovereign_owner(request.admin_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await transfer_from_treasury(
        request.admin_id,
        request.to_user_id,
        request.amount,
        request.reason
    )
    return result


# ============================================
# UTILITY ENDPOINTS
# ============================================

@router.get("/convert/usdt-to-trc", summary="Convert USDT to TRC")
async def convert_usdt_to_trc(amount: float = Query(gt=0)):
    """Convert USDT amount to TRC"""
    return {
        "usdt": amount,
        "trc": usdt_to_trc(amount),
        "rate": "1:1"
    }


@router.get("/convert/trc-to-usdt", summary="Convert TRC to USDT")
async def convert_trc_to_usdt(amount: float = Query(gt=0)):
    """Convert TRC amount to USDT"""
    return {
        "trc": amount,
        "usdt": trc_to_usdt(amount),
        "rate": "1:1"
    }


@router.get("/is-sovereign/{user_id}", summary="Check if sovereign owner")
async def check_sovereign(user_id: int):
    """Check if user is sovereign owner"""
    return {
        "user_id": user_id,
        "is_sovereign": is_sovereign_owner(user_id),
        "sovereign_id": SOVEREIGN_OWNER_ID
    }
