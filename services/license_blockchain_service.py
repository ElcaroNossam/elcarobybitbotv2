"""
License Blockchain Service
=========================
Full integration of licenses with blockchain (ELC/ELC tokens).

Features:
- Purchase license with ELC tokens
- Record license on blockchain (immutable proof)
- NFT-based license tokens (optional)
- License verification via blockchain
- Sync between database and blockchain records
- Admin minting and management

Architecture:
- All license purchases with ELC are recorded on-chain
- License NFTs can be minted for premium users
- Blockchain records serve as proof of purchase
- Database maintains fast access, blockchain = source of truth
"""

import hashlib
import json
import logging
import time
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================

# License prices in ELC (= USD, 1:1 peg)
LICENSE_PRICES_ELC = {
    "premium": {1: 100, 3: 270, 6: 480, 12: 840},
    "basic": {1: 50, 3: 135, 6: 240, 12: 420},
    "enterprise": {1: 500, 3: 1350, 6: 2400, 12: 4200},
    "trial": {1: 0}  # Free trial
}

# Discount for staked ELC holders
STAKING_DISCOUNTS = {
    100: 0.05,    # 100+ ELC staked = 5% off
    500: 0.10,    # 500+ ELC staked = 10% off
    1000: 0.15,   # 1000+ ELC staked = 15% off
    5000: 0.20,   # 5000+ ELC staked = 20% off
}

# NFT License Contract Address (virtual)
LICENSE_NFT_CONTRACT = "0xELCARO_LICENSE_NFT_V1"
ADMIN_ID = 511692487


class LicenseNFTTier(Enum):
    """NFT License tiers"""
    BRONZE = "bronze"       # Basic license
    SILVER = "silver"       # Premium 1-3 months
    GOLD = "gold"           # Premium 6-12 months
    PLATINUM = "platinum"   # Enterprise
    DIAMOND = "diamond"     # Lifetime / Special


@dataclass
class BlockchainLicenseRecord:
    """On-chain license record"""
    tx_hash: str
    user_id: int
    wallet_address: str
    license_type: str
    period_months: int
    amount_paid: float
    currency: str  # "ELC", "ELC", "USDT"
    start_timestamp: int
    end_timestamp: int
    nft_token_id: Optional[str]
    block_number: int
    created_at: int
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @property
    def is_active(self) -> bool:
        return time.time() < self.end_timestamp


@dataclass
class LicenseNFT:
    """NFT representing a license"""
    token_id: str
    owner_id: int
    owner_wallet: str
    tier: LicenseNFTTier
    license_type: str
    valid_until: int
    metadata_uri: str
    minted_at: int
    tx_hash: str
    
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["tier"] = self.tier.value
        return d


# ============================================
# PRICE CALCULATIONS
# ============================================

def get_license_price(license_type: str, months: int) -> float:
    """Get base license price in ELC"""
    prices = LICENSE_PRICES_ELC.get(license_type.lower(), LICENSE_PRICES_ELC["basic"])
    return float(prices.get(months, prices.get(1, 50)))


def get_staking_discount(staked_amount: float) -> float:
    """Get discount based on staked ELC amount"""
    discount = 0.0
    for threshold, disc in sorted(STAKING_DISCOUNTS.items()):
        if staked_amount >= threshold:
            discount = disc
    return discount


def calculate_final_price(license_type: str, months: int, staked_elc: float = 0) -> Dict[str, Any]:
    """Calculate final price with all discounts"""
    base_price = get_license_price(license_type, months)
    discount_rate = get_staking_discount(staked_elc)
    discount_amount = base_price * discount_rate
    final_price = base_price - discount_amount
    
    return {
        "license_type": license_type,
        "months": months,
        "base_price": base_price,
        "staked_elc": staked_elc,
        "discount_rate": discount_rate,
        "discount_amount": discount_amount,
        "final_price": final_price,
        "currency": "ELC"
    }


# ============================================
# BLOCKCHAIN OPERATIONS
# ============================================

def generate_tx_hash() -> str:
    """Generate unique transaction hash"""
    random_data = secrets.token_hex(32)
    timestamp = str(time.time_ns())
    return "0x" + hashlib.sha256(f"{random_data}{timestamp}".encode()).hexdigest()


def generate_nft_token_id(user_id: int, license_type: str) -> str:
    """Generate unique NFT token ID"""
    data = f"{user_id}:{license_type}:{time.time_ns()}"
    return hashlib.sha256(data.encode()).hexdigest()[:16].upper()


def determine_nft_tier(license_type: str, months: int) -> LicenseNFTTier:
    """Determine NFT tier based on license"""
    if license_type == "enterprise":
        return LicenseNFTTier.PLATINUM
    elif license_type == "premium":
        if months >= 12:
            return LicenseNFTTier.GOLD
        elif months >= 3:
            return LicenseNFTTier.SILVER
        else:
            return LicenseNFTTier.BRONZE
    elif license_type == "basic":
        return LicenseNFTTier.BRONZE
    else:
        return LicenseNFTTier.BRONZE


# ============================================
# LICENSE PURCHASE WITH ELC
# ============================================

def purchase_license_with_elc(
    user_id: int,
    license_type: str,
    months: int,
    wallet_address: str = None,
    mint_nft: bool = True
) -> Dict[str, Any]:
    """
    Purchase license with ELC tokens.
    
    Flow:
    1. Calculate price with discounts
    2. Check ELC balance
    3. Deduct ELC from user
    4. Create blockchain record
    5. Mint NFT (optional)
    6. Activate license in database
    7. Return transaction details
    
    Args:
        user_id: User's Telegram ID
        license_type: "premium", "basic", "enterprise"
        months: License duration
        wallet_address: Optional wallet for NFT
        mint_nft: Whether to mint NFT license
    
    Returns:
        {"success": bool, "tx_hash": str, "nft_token_id": str, ...}
    """
    # Import here to avoid circular imports
    from db_elcaro import get_elc_balance, subtract_elc_balance, check_elc_balance
    from db import grant_license, invalidate_user_cache
    
    try:
        # 1. Get user's ELC balance
        balance = get_elc_balance(user_id)
        staked_elc = balance.get("staked", 0)
        available_elc = balance.get("available", 0)
        
        # 2. Calculate price
        price_info = calculate_final_price(license_type, months, staked_elc)
        final_price = price_info["final_price"]
        
        # 3. Check balance
        if available_elc < final_price:
            return {
                "success": False,
                "error": "insufficient_balance",
                "required": final_price,
                "available": available_elc,
                "message": f"Insufficient ELC balance. Need {final_price:.2f}, have {available_elc:.2f}"
            }
        
        # 4. Deduct ELC
        try:
            new_balance = subtract_elc_balance(
                user_id, 
                final_price, 
                f"License purchase: {license_type} {months}m"
            )
        except Exception as e:
            logger.error(f"Failed to deduct ELC for user {user_id}: {e}")
            return {
                "success": False,
                "error": "payment_failed",
                "message": str(e)
            }
        
        # 5. Generate blockchain record
        now = int(time.time())
        end_time = now + (months * 30 * 86400)  # Approximate month
        tx_hash = generate_tx_hash()
        block_number = int(now / 3)  # Simulated 3-second blocks
        
        # 6. Mint NFT if requested
        nft_token_id = None
        nft_record = None
        if mint_nft and license_type in ["premium", "enterprise"]:
            nft_token_id = generate_nft_token_id(user_id, license_type)
            nft_tier = determine_nft_tier(license_type, months)
            
            nft_record = LicenseNFT(
                token_id=nft_token_id,
                owner_id=user_id,
                owner_wallet=wallet_address or f"ELCARO_{user_id}",
                tier=nft_tier,
                license_type=license_type,
                valid_until=end_time,
                metadata_uri=f"ipfs://elcaro/license/{nft_token_id}",
                minted_at=now,
                tx_hash=tx_hash
            )
        
        # 7. Create blockchain license record
        blockchain_record = BlockchainLicenseRecord(
            tx_hash=tx_hash,
            user_id=user_id,
            wallet_address=wallet_address or f"ELCARO_{user_id}",
            license_type=license_type,
            period_months=months,
            amount_paid=final_price,
            currency="ELC",
            start_timestamp=now,
            end_timestamp=end_time,
            nft_token_id=nft_token_id,
            block_number=block_number,
            created_at=now
        )
        
        # 8. Save to database
        _save_blockchain_license_record(blockchain_record)
        if nft_record:
            _save_license_nft(nft_record)
        
        # 9. Activate license in main database
        grant_result = grant_license(
            user_id=user_id,
            license_type=license_type,
            period_months=months,
            payment_type="elc_blockchain",
            amount=final_price,
            currency="ELC",
            telegram_charge_id=tx_hash
        )
        
        if not grant_result.get("success"):
            logger.error(f"Failed to grant license after ELC payment: {grant_result}")
            # Note: ELC already deducted - this needs manual resolution
            return {
                "success": False,
                "error": "grant_failed",
                "message": "Payment processed but license activation failed. Contact support.",
                "tx_hash": tx_hash
            }
        
        invalidate_user_cache(user_id)
        
        logger.info(f"License purchased: user={user_id}, type={license_type}, months={months}, "
                   f"price={final_price} ELC, tx={tx_hash}")
        
        return {
            "success": True,
            "tx_hash": tx_hash,
            "nft_token_id": nft_token_id,
            "nft_tier": nft_record.tier.value if nft_record else None,
            "license_type": license_type,
            "months": months,
            "amount_paid": final_price,
            "discount_applied": price_info["discount_rate"] * 100,
            "valid_until": end_time,
            "valid_until_str": datetime.fromtimestamp(end_time).strftime("%Y-%m-%d"),
            "block_number": block_number,
            "new_elc_balance": new_balance.get("available", 0),
            "blockchain_record": blockchain_record.to_dict()
        }
        
    except Exception as e:
        logger.exception(f"License purchase failed for user {user_id}: {e}")
        return {
            "success": False,
            "error": "system_error",
            "message": str(e)
        }


# ============================================
# DATABASE OPERATIONS
# ============================================

def _save_blockchain_license_record(record: BlockchainLicenseRecord) -> bool:
    """Save blockchain license record to database"""
    from core.db_postgres import execute_write
    
    try:
        execute_write("""
            INSERT INTO license_blockchain_records 
            (tx_hash, user_id, wallet_address, license_type, period_months,
             amount_paid, currency, start_timestamp, end_timestamp, 
             nft_token_id, block_number, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (tx_hash) DO NOTHING
        """, (
            record.tx_hash, record.user_id, record.wallet_address,
            record.license_type, record.period_months, record.amount_paid,
            record.currency, record.start_timestamp, record.end_timestamp,
            record.nft_token_id, record.block_number, record.created_at
        ))
        return True
    except Exception as e:
        logger.error(f"Failed to save blockchain record: {e}")
        return False


def _save_license_nft(nft: LicenseNFT) -> bool:
    """Save license NFT to database"""
    from core.db_postgres import execute_write
    
    try:
        execute_write("""
            INSERT INTO license_nft_tokens
            (token_id, owner_id, owner_wallet, tier, license_type,
             valid_until, metadata_uri, minted_at, tx_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (token_id) DO UPDATE SET
                owner_id = EXCLUDED.owner_id,
                owner_wallet = EXCLUDED.owner_wallet
        """, (
            nft.token_id, nft.owner_id, nft.owner_wallet, nft.tier.value,
            nft.license_type, nft.valid_until, nft.metadata_uri,
            nft.minted_at, nft.tx_hash
        ))
        return True
    except Exception as e:
        logger.error(f"Failed to save NFT record: {e}")
        return False


def get_user_blockchain_licenses(user_id: int, active_only: bool = False) -> List[Dict[str, Any]]:
    """Get user's blockchain license records"""
    from core.db_postgres import execute
    
    if active_only:
        now = int(time.time())
        rows = execute("""
            SELECT * FROM license_blockchain_records
            WHERE user_id = %s AND end_timestamp > %s
            ORDER BY created_at DESC
        """, (user_id, now))
    else:
        rows = execute("""
            SELECT * FROM license_blockchain_records
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
    
    return [dict(r) for r in rows] if rows else []


def get_user_license_nfts(user_id: int) -> List[Dict[str, Any]]:
    """Get user's license NFTs"""
    from core.db_postgres import execute
    
    rows = execute("""
        SELECT * FROM license_nft_tokens
        WHERE owner_id = %s
        ORDER BY minted_at DESC
    """, (user_id,))
    
    return [dict(r) for r in rows] if rows else []


def verify_license_on_blockchain(tx_hash: str) -> Optional[Dict[str, Any]]:
    """Verify license purchase on blockchain"""
    from core.db_postgres import execute_one
    
    record = execute_one("""
        SELECT * FROM license_blockchain_records
        WHERE tx_hash = %s
    """, (tx_hash,))
    
    if not record:
        return None
    
    now = int(time.time())
    return {
        "verified": True,
        "tx_hash": tx_hash,
        "user_id": record["user_id"],
        "license_type": record["license_type"],
        "period_months": record["period_months"],
        "amount_paid": record["amount_paid"],
        "is_active": record["end_timestamp"] > now,
        "valid_until": record["end_timestamp"],
        "block_number": record["block_number"]
    }


def get_blockchain_license_stats() -> Dict[str, Any]:
    """Get overall blockchain license statistics"""
    from core.db_postgres import execute_one
    
    now = int(time.time())
    
    stats = execute_one("""
        SELECT 
            COUNT(*) as total_licenses,
            COUNT(DISTINCT user_id) as unique_users,
            SUM(amount_paid) as total_revenue_elc,
            COUNT(CASE WHEN end_timestamp > %s THEN 1 END) as active_licenses,
            COUNT(nft_token_id) as total_nfts
        FROM license_blockchain_records
    """, (now,))
    
    nft_stats = execute_one("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN tier = 'bronze' THEN 1 END) as bronze,
            COUNT(CASE WHEN tier = 'silver' THEN 1 END) as silver,
            COUNT(CASE WHEN tier = 'gold' THEN 1 END) as gold,
            COUNT(CASE WHEN tier = 'platinum' THEN 1 END) as platinum,
            COUNT(CASE WHEN tier = 'diamond' THEN 1 END) as diamond
        FROM license_nft_tokens
    """)
    
    return {
        "total_licenses": stats.get("total_licenses", 0) if stats else 0,
        "unique_users": stats.get("unique_users", 0) if stats else 0,
        "total_revenue_elc": stats.get("total_revenue_elc", 0) if stats else 0,
        "active_licenses": stats.get("active_licenses", 0) if stats else 0,
        "total_nfts": stats.get("total_nfts", 0) if stats else 0,
        "nft_breakdown": {
            "bronze": nft_stats.get("bronze", 0) if nft_stats else 0,
            "silver": nft_stats.get("silver", 0) if nft_stats else 0,
            "gold": nft_stats.get("gold", 0) if nft_stats else 0,
            "platinum": nft_stats.get("platinum", 0) if nft_stats else 0,
            "diamond": nft_stats.get("diamond", 0) if nft_stats else 0
        }
    }


# ============================================
# ADMIN FUNCTIONS
# ============================================

def admin_mint_license_nft(
    admin_id: int,
    user_id: int,
    tier: str,
    valid_months: int = 12,
    wallet_address: str = None
) -> Dict[str, Any]:
    """Admin mints a special license NFT for user"""
    if admin_id != ADMIN_ID:
        return {"success": False, "error": "Unauthorized"}
    
    now = int(time.time())
    end_time = now + (valid_months * 30 * 86400)
    tx_hash = generate_tx_hash()
    token_id = generate_nft_token_id(user_id, f"admin_{tier}")
    
    try:
        nft_tier = LicenseNFTTier(tier.lower())
    except ValueError:
        return {"success": False, "error": f"Invalid tier: {tier}"}
    
    nft = LicenseNFT(
        token_id=token_id,
        owner_id=user_id,
        owner_wallet=wallet_address or f"ELCARO_{user_id}",
        tier=nft_tier,
        license_type="admin_grant",
        valid_until=end_time,
        metadata_uri=f"ipfs://elcaro/admin-nft/{token_id}",
        minted_at=now,
        tx_hash=tx_hash
    )
    
    _save_license_nft(nft)
    
    # Create blockchain record
    record = BlockchainLicenseRecord(
        tx_hash=tx_hash,
        user_id=user_id,
        wallet_address=wallet_address or f"ELCARO_{user_id}",
        license_type="admin_grant",
        period_months=valid_months,
        amount_paid=0,
        currency="ADMIN",
        start_timestamp=now,
        end_timestamp=end_time,
        nft_token_id=token_id,
        block_number=int(now / 3),
        created_at=now
    )
    _save_blockchain_license_record(record)
    
    logger.info(f"Admin {admin_id} minted {tier} NFT for user {user_id}")
    
    return {
        "success": True,
        "nft": nft.to_dict(),
        "tx_hash": tx_hash,
        "message": f"Minted {tier} NFT license for user {user_id}"
    }


def admin_revoke_nft(admin_id: int, token_id: str, reason: str = None) -> Dict[str, Any]:
    """Admin revokes an NFT"""
    if admin_id != ADMIN_ID:
        return {"success": False, "error": "Unauthorized"}
    
    from core.db_postgres import execute_write, execute_one
    
    nft = execute_one("SELECT * FROM license_nft_tokens WHERE token_id = %s", (token_id,))
    if not nft:
        return {"success": False, "error": "NFT not found"}
    
    execute_write("""
        UPDATE license_nft_tokens 
        SET valid_until = %s, owner_wallet = 'REVOKED'
        WHERE token_id = %s
    """, (int(time.time()), token_id))
    
    logger.info(f"Admin {admin_id} revoked NFT {token_id}. Reason: {reason}")
    
    return {
        "success": True,
        "token_id": token_id,
        "previous_owner": nft["owner_id"],
        "message": f"NFT {token_id} revoked"
    }


def get_all_license_nfts(limit: int = 100) -> List[Dict[str, Any]]:
    """Get all license NFTs (admin function)"""
    from core.db_postgres import execute
    
    rows = execute("""
        SELECT n.*, r.amount_paid, r.currency
        FROM license_nft_tokens n
        LEFT JOIN license_blockchain_records r ON n.tx_hash = r.tx_hash
        ORDER BY n.minted_at DESC
        LIMIT %s
    """, (limit,))
    
    return [dict(r) for r in rows] if rows else []


# ============================================
# SYNC FUNCTIONS
# ============================================

def sync_database_to_blockchain(user_id: int) -> Dict[str, Any]:
    """
    Sync user's database license to blockchain records.
    Used when user has a license but no blockchain record (legacy migration).
    """
    from db import get_user_license
    
    license_info = get_user_license(user_id)
    
    if not license_info.get("is_active"):
        return {"success": False, "error": "No active license to sync"}
    
    # Check if already has blockchain record
    existing = get_user_blockchain_licenses(user_id, active_only=True)
    if existing:
        return {"success": True, "message": "Already synced", "records": existing}
    
    # Create blockchain record from existing license
    now = int(time.time())
    tx_hash = generate_tx_hash()
    
    record = BlockchainLicenseRecord(
        tx_hash=tx_hash,
        user_id=user_id,
        wallet_address=f"ELCARO_{user_id}",
        license_type=license_info["license_type"],
        period_months=license_info.get("days_left", 30) // 30 or 1,
        amount_paid=0,
        currency="MIGRATION",
        start_timestamp=now,
        end_timestamp=license_info["expires"],
        nft_token_id=None,
        block_number=int(now / 3),
        created_at=now
    )
    
    _save_blockchain_license_record(record)
    
    return {
        "success": True,
        "message": "License synced to blockchain",
        "tx_hash": tx_hash,
        "record": record.to_dict()
    }


# ============================================
# TABLE INITIALIZATION
# ============================================

def ensure_license_blockchain_tables():
    """Create blockchain license tables if not exist"""
    from core.db_postgres import get_conn
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Blockchain license records
            cur.execute("""
                CREATE TABLE IF NOT EXISTS license_blockchain_records (
                    id SERIAL PRIMARY KEY,
                    tx_hash TEXT UNIQUE NOT NULL,
                    user_id BIGINT NOT NULL,
                    wallet_address TEXT,
                    license_type TEXT NOT NULL,
                    period_months INTEGER NOT NULL,
                    amount_paid REAL DEFAULT 0,
                    currency TEXT DEFAULT 'ELC',
                    start_timestamp BIGINT NOT NULL,
                    end_timestamp BIGINT NOT NULL,
                    nft_token_id TEXT,
                    block_number BIGINT,
                    created_at BIGINT NOT NULL
                )
            """)
            
            # License NFT tokens
            cur.execute("""
                CREATE TABLE IF NOT EXISTS license_nft_tokens (
                    id SERIAL PRIMARY KEY,
                    token_id TEXT UNIQUE NOT NULL,
                    owner_id BIGINT NOT NULL,
                    owner_wallet TEXT,
                    tier TEXT NOT NULL,
                    license_type TEXT NOT NULL,
                    valid_until BIGINT NOT NULL,
                    metadata_uri TEXT,
                    minted_at BIGINT NOT NULL,
                    tx_hash TEXT
                )
            """)
            
            # Indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_blockchain_lic_user ON license_blockchain_records(user_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_blockchain_lic_active ON license_blockchain_records(end_timestamp)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_nft_owner ON license_nft_tokens(owner_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_nft_tier ON license_nft_tokens(tier)")
    
    logger.info("License blockchain tables initialized")


# Initialize tables on module load
try:
    ensure_license_blockchain_tables()
except Exception as e:
    logger.warning(f"Could not initialize blockchain license tables: {e}")
