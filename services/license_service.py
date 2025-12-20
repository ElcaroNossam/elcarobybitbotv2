"""
License service for premium feature management
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import logging
import secrets
import string

logger = logging.getLogger(__name__)


class LicenseType(Enum):
    FREE = "free"
    PREMIUM = "premium"
    VIP = "vip"
    ENTERPRISE = "enterprise"


FEATURE_REQUIREMENTS: Dict[str, str] = {
    "hyperliquid": "premium",
    "advanced_signals": "premium",
    "multi_exchange": "vip",
    "priority_support": "premium",
    "custom_strategies": "vip",
    "unlimited_positions": "enterprise",
    "dca_advanced": "premium",
    "pyramid_advanced": "premium",
    "analytics": "vip",
    "webhooks": "enterprise",
}


LICENSE_LEVELS = {"free": 0, "premium": 1, "vip": 2, "enterprise": 3}


class LicenseService:
    """Service for license and premium feature management"""
    
    def __init__(self, db_module):
        self.db = db_module
        self._promo_codes: Dict[str, Dict[str, Any]] = {}
    
    async def get_license(self, user_id: int) -> Dict[str, Any]:
        """Get user's current license"""
        config = self.db.get_user_config(user_id)
        license_type = config.get("license_type", "free")
        
        expires_at = None
        if config.get("license_expires"):
            try:
                expires_at = datetime.fromisoformat(config["license_expires"])
            except (ValueError, TypeError):
                pass
        
        is_active = True
        if license_type != "free" and expires_at:
            is_active = datetime.utcnow() < expires_at
        
        features = self._get_features_for_license(license_type)
        
        return {
            "type": license_type,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "is_active": is_active,
            "promo_code": config.get("promo_code"),
            "features": features
        }
    
    async def set_license(
        self,
        user_id: int,
        license_type: str,
        duration_days: Optional[int] = None,
        promo_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Set user license"""
        self.db.ensure_user(user_id)
        self.db.set_user_field(user_id, "license_type", license_type)
        
        if duration_days:
            expires_at = datetime.utcnow() + timedelta(days=duration_days)
            self.db.set_user_field(user_id, "license_expires", expires_at.isoformat())
        else:
            self.db.set_user_field(user_id, "license_expires", None)
        
        if promo_code:
            self.db.set_user_field(user_id, "promo_code", promo_code)
        
        logger.info(f"License set for user {user_id}: {license_type}, duration: {duration_days} days")
        return await self.get_license(user_id)
    
    async def check_feature_access(self, user_id: int, feature: str) -> Tuple[bool, Optional[str]]:
        """Check if user has access to a feature"""
        license = await self.get_license(user_id)
        
        if not license["is_active"]:
            return False, "License has expired"
        
        required_type = FEATURE_REQUIREMENTS.get(feature.lower())
        if not required_type:
            return True, None
        
        user_level = LICENSE_LEVELS.get(license["type"], 0)
        required_level = LICENSE_LEVELS.get(required_type, 0)
        
        if user_level >= required_level:
            return True, None
        
        return False, f"Feature '{feature}' requires {required_type} license"
    
    async def check_license_access(self, user_id: int, feature: str) -> bool:
        """Simple check if user has access to a feature"""
        has_access, _ = await self.check_feature_access(user_id, feature)
        return has_access
    
    async def can_use_hyperliquid(self, user_id: int) -> bool:
        """Check if user can use HyperLiquid"""
        return await self.check_license_access(user_id, "hyperliquid")
    
    async def can_use_advanced_signals(self, user_id: int) -> bool:
        """Check if user can use advanced signals"""
        return await self.check_license_access(user_id, "advanced_signals")
    
    async def can_use_multi_exchange(self, user_id: int) -> bool:
        """Check if user can use multiple exchanges"""
        return await self.check_license_access(user_id, "multi_exchange")
    
    async def get_position_limit(self, user_id: int) -> int:
        """Get max positions limit for user"""
        if await self.check_license_access(user_id, "unlimited_positions"):
            return 999
        
        license = await self.get_license(user_id)
        limits = {"free": 3, "premium": 10, "vip": 25, "enterprise": 999}
        return limits.get(license["type"], 3)
    
    async def create_promo_code(
        self,
        license_type: str,
        duration_days: int = 30,
        max_uses: int = 1,
        code: Optional[str] = None
    ) -> str:
        """Create a promo code"""
        if not code:
            code = self._generate_promo_code()
        
        promo_data = {
            "code": code,
            "license_type": license_type,
            "duration_days": duration_days,
            "max_uses": max_uses,
            "used_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "used_by": []
        }
        
        self._promo_codes[code] = promo_data
        logger.info(f"Promo code created: {code}")
        return code
    
    async def apply_promo_code(self, user_id: int, code: str) -> Dict[str, Any]:
        """Apply promo code for user"""
        promo = self._promo_codes.get(code)
        
        if not promo:
            raise ValueError("Invalid promo code")
        
        if promo.get("used_count", 0) >= promo.get("max_uses", 1):
            raise ValueError("Promo code has been fully used")
        
        if user_id in promo.get("used_by", []):
            raise ValueError("You have already used this promo code")
        
        license_type = promo["license_type"]
        duration = promo.get("duration_days", 30)
        
        result = await self.set_license(user_id, license_type, duration, code)
        
        promo["used_count"] += 1
        promo["used_by"].append(user_id)
        
        logger.info(f"Promo code {code} applied for user {user_id}")
        return result
    
    def _get_features_for_license(self, license_type: str) -> List[str]:
        """Get list of features available for license type"""
        user_level = LICENSE_LEVELS.get(license_type, 0)
        features = []
        for feature, required in FEATURE_REQUIREMENTS.items():
            required_level = LICENSE_LEVELS.get(required, 0)
            if user_level >= required_level:
                features.append(feature)
        return features
    
    def _generate_promo_code(self, length: int = 10) -> str:
        """Generate random promo code"""
        chars = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(chars) for _ in range(length))
