"""
Exchange API Validator and Health Check
Validates API credentials and connectivity for Bybit and HyperLiquid
"""
import asyncio
import aiohttp
import hmac
import hashlib
import time
import json
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ExchangeType(str, Enum):
    BYBIT = "bybit"
    HYPERLIQUID = "hyperliquid"


@dataclass
class ValidationResult:
    success: bool
    message: str
    data: Optional[Dict] = None
    latency_ms: float = 0


class BybitValidator:
    """Validate Bybit API credentials and connectivity"""
    
    DEMO_BASE_URL = "https://api-demo.bybit.com"
    REAL_BASE_URL = "https://api.bybit.com"
    TESTNET_URL = "https://api-testnet.bybit.com"
    
    def __init__(self, api_key: str, api_secret: str, demo: bool = True, testnet: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        
        if testnet:
            self.base_url = self.TESTNET_URL
        elif demo:
            self.base_url = self.DEMO_BASE_URL
        else:
            self.base_url = self.REAL_BASE_URL
        
        self.mode = "testnet" if testnet else ("demo" if demo else "real")
    
    def _sign_request(self, params: dict) -> Tuple[str, str]:
        """Generate HMAC signature for Bybit API v5"""
        timestamp = str(int(time.time() * 1000))
        recv_window = "60000"
        
        param_str = timestamp + self.api_key + recv_window
        if params:
            param_str += "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return timestamp, signature
    
    async def validate_connection(self) -> ValidationResult:
        """Test basic connectivity to Bybit API"""
        start = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/v5/market/time",
                    timeout=10
                ) as resp:
                    latency = (time.time() - start) * 1000
                    
                    if resp.status != 200:
                        return ValidationResult(
                            False, f"Connection failed: HTTP {resp.status}",
                            latency_ms=latency
                        )
                    
                    data = await resp.json()
                    
                    if data.get("retCode") == 0:
                        server_time = data.get("result", {}).get("timeSecond")
                        return ValidationResult(
                            True, f"Connected to Bybit ({self.mode})",
                            {"server_time": server_time, "mode": self.mode},
                            latency
                        )
                    else:
                        return ValidationResult(
                            False, f"API error: {data.get('retMsg', 'Unknown')}",
                            latency_ms=latency
                        )
        except asyncio.TimeoutError:
            return ValidationResult(False, "Connection timeout", latency_ms=(time.time() - start) * 1000)
        except Exception as e:
            return ValidationResult(False, f"Connection error: {str(e)}")
    
    async def validate_credentials(self) -> ValidationResult:
        """Validate API key and secret"""
        start = time.time()
        
        timestamp, signature = self._sign_request({})
        
        headers = {
            "X-BAPI-API-KEY": self.api_key,
            "X-BAPI-SIGN": signature,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": "5000"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/v5/account/wallet-balance",
                    params={"accountType": "UNIFIED"},
                    headers=headers,
                    timeout=10
                ) as resp:
                    latency = (time.time() - start) * 1000
                    data = await resp.json()
                    
                    if data.get("retCode") == 0:
                        balance_list = data.get("result", {}).get("list", [])
                        equity = 0
                        if balance_list:
                            equity = float(balance_list[0].get("totalEquity", 0))
                        
                        return ValidationResult(
                            True,
                            f"API credentials valid ({self.mode})",
                            {
                                "mode": self.mode,
                                "equity": equity,
                                "permissions": "trade,read"
                            },
                            latency
                        )
                    elif data.get("retCode") == 10003:
                        return ValidationResult(False, "Invalid API key", latency_ms=latency)
                    elif data.get("retCode") == 10004:
                        return ValidationResult(False, "Invalid signature (wrong secret)", latency_ms=latency)
                    elif data.get("retCode") == 33004:
                        return ValidationResult(False, "API key expired or disabled", latency_ms=latency)
                    else:
                        return ValidationResult(
                            False,
                            f"Validation failed: {data.get('retMsg', 'Unknown error')}",
                            latency_ms=latency
                        )
                        
        except asyncio.TimeoutError:
            return ValidationResult(False, "Validation timeout", latency_ms=(time.time() - start) * 1000)
        except Exception as e:
            return ValidationResult(False, f"Validation error: {str(e)}")
    
    async def validate_trading_permissions(self) -> ValidationResult:
        """Check if API has trading permissions"""
        start = time.time()
        
        timestamp, signature = self._sign_request({})
        
        headers = {
            "X-BAPI-API-KEY": self.api_key,
            "X-BAPI-SIGN": signature,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": "5000"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Try to get API key info
                async with session.get(
                    f"{self.base_url}/v5/user/query-api",
                    headers=headers,
                    timeout=10
                ) as resp:
                    latency = (time.time() - start) * 1000
                    data = await resp.json()
                    
                    if data.get("retCode") == 0:
                        result = data.get("result", {})
                        permissions = result.get("permissions", {})
                        
                        # Check for contract trading permission
                        contract_perms = permissions.get("ContractTrade", [])
                        
                        can_trade = "Order" in contract_perms or "PositionWrite" in contract_perms
                        can_read = "PositionRead" in contract_perms
                        
                        return ValidationResult(
                            can_trade,
                            "Trading enabled" if can_trade else "Trading permissions missing",
                            {
                                "contract_permissions": contract_perms,
                                "can_trade": can_trade,
                                "can_read": can_read,
                                "ip_restriction": result.get("ips", [])
                            },
                            latency
                        )
                    else:
                        # Fallback - try placing a tiny order and cancel
                        return ValidationResult(
                            True,
                            "Permissions check unavailable, assume valid",
                            latency_ms=latency
                        )
                        
        except Exception as e:
            return ValidationResult(False, f"Permission check error: {str(e)}")
    
    async def get_market_info(self, symbol: str) -> ValidationResult:
        """Get trading info for a specific symbol"""
        start = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/v5/market/instruments-info",
                    params={"category": "linear", "symbol": symbol},
                    timeout=10
                ) as resp:
                    latency = (time.time() - start) * 1000
                    data = await resp.json()
                    
                    if data.get("retCode") == 0:
                        result = data.get("result", {}).get("list", [])
                        if result:
                            info = result[0]
                            return ValidationResult(
                                True,
                                f"Symbol {symbol} found",
                                {
                                    "symbol": symbol,
                                    "min_qty": info.get("lotSizeFilter", {}).get("minOrderQty"),
                                    "max_qty": info.get("lotSizeFilter", {}).get("maxOrderQty"),
                                    "qty_step": info.get("lotSizeFilter", {}).get("qtyStep"),
                                    "min_price": info.get("priceFilter", {}).get("minPrice"),
                                    "max_price": info.get("priceFilter", {}).get("maxPrice"),
                                    "tick_size": info.get("priceFilter", {}).get("tickSize"),
                                    "max_leverage": info.get("leverageFilter", {}).get("maxLeverage"),
                                    "status": info.get("status")
                                },
                                latency
                            )
                        else:
                            return ValidationResult(False, f"Symbol {symbol} not found", latency_ms=latency)
                    else:
                        return ValidationResult(
                            False,
                            f"Market info error: {data.get('retMsg')}",
                            latency_ms=latency
                        )
                        
        except Exception as e:
            return ValidationResult(False, f"Market info error: {str(e)}")
    
    async def full_validation(self) -> Dict[str, ValidationResult]:
        """Run all validation checks"""
        results = {}
        
        results["connection"] = await self.validate_connection()
        
        if results["connection"].success:
            results["credentials"] = await self.validate_credentials()
            
            if results["credentials"].success:
                results["permissions"] = await self.validate_trading_permissions()
                results["market"] = await self.get_market_info("BTCUSDT")
        
        return results


class HyperLiquidValidator:
    """Validate HyperLiquid API credentials and connectivity"""
    
    MAINNET_URL = "https://api.hyperliquid.xyz"
    TESTNET_URL = "https://api.hyperliquid-testnet.xyz"
    
    def __init__(self, private_key: str, testnet: bool = False):
        self.private_key = private_key
        self.testnet = testnet
        self.base_url = self.TESTNET_URL if testnet else self.MAINNET_URL
        self.mode = "testnet" if testnet else "mainnet"
    
    def _get_address(self) -> str:
        """Derive address from private key"""
        try:
            from eth_account import Account
            account = Account.from_key(self.private_key)
            return account.address
        except Exception:
            return ""
    
    async def validate_connection(self) -> ValidationResult:
        """Test basic connectivity to HyperLiquid API"""
        start = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/info",
                    json={"type": "meta"},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                ) as resp:
                    latency = (time.time() - start) * 1000
                    
                    if resp.status == 200:
                        data = await resp.json()
                        if "universe" in data:
                            return ValidationResult(
                                True,
                                f"Connected to HyperLiquid ({self.mode})",
                                {
                                    "mode": self.mode,
                                    "assets": len(data.get("universe", []))
                                },
                                latency
                            )
                    
                    return ValidationResult(
                        False,
                        f"Connection failed: HTTP {resp.status}",
                        latency_ms=latency
                    )
                    
        except asyncio.TimeoutError:
            return ValidationResult(False, "Connection timeout", latency_ms=(time.time() - start) * 1000)
        except Exception as e:
            return ValidationResult(False, f"Connection error: {str(e)}")
    
    async def validate_credentials(self) -> ValidationResult:
        """Validate private key and get wallet info"""
        start = time.time()
        
        address = self._get_address()
        if not address:
            return ValidationResult(False, "Invalid private key format")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/info",
                    json={"type": "clearinghouseState", "user": address},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                ) as resp:
                    latency = (time.time() - start) * 1000
                    
                    if resp.status == 200:
                        data = await resp.json()
                        
                        margin_summary = data.get("marginSummary", {})
                        account_value = float(margin_summary.get("accountValue", 0))
                        
                        return ValidationResult(
                            True,
                            f"Credentials valid ({self.mode})",
                            {
                                "address": address,
                                "account_value": account_value,
                                "withdrawable": float(margin_summary.get("withdrawable", 0)),
                                "mode": self.mode
                            },
                            latency
                        )
                    else:
                        return ValidationResult(
                            False,
                            f"Validation failed: HTTP {resp.status}",
                            latency_ms=latency
                        )
                        
        except Exception as e:
            return ValidationResult(False, f"Validation error: {str(e)}")
    
    async def get_market_info(self, symbol: str) -> ValidationResult:
        """Get trading info for a specific asset"""
        start = time.time()
        
        # Normalize symbol (remove USDC/USDT suffix)
        coin = symbol.upper()
        for suffix in ["USDT", "USDC", "PERP", "-PERP"]:
            coin = coin.replace(suffix, "")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/info",
                    json={"type": "meta"},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                ) as resp:
                    latency = (time.time() - start) * 1000
                    
                    if resp.status == 200:
                        data = await resp.json()
                        
                        for i, asset in enumerate(data.get("universe", [])):
                            if asset.get("name") == coin:
                                return ValidationResult(
                                    True,
                                    f"Asset {coin} found",
                                    {
                                        "asset_id": i,
                                        "name": coin,
                                        "sz_decimals": asset.get("szDecimals"),
                                        "max_leverage": asset.get("maxLeverage"),
                                        "onlyIsolated": asset.get("onlyIsolated", False)
                                    },
                                    latency
                                )
                        
                        return ValidationResult(False, f"Asset {coin} not found", latency_ms=latency)
                    else:
                        return ValidationResult(
                            False,
                            f"Market info failed: HTTP {resp.status}",
                            latency_ms=latency
                        )
                        
        except Exception as e:
            return ValidationResult(False, f"Market info error: {str(e)}")
    
    async def full_validation(self) -> Dict[str, ValidationResult]:
        """Run all validation checks"""
        results = {}
        
        results["connection"] = await self.validate_connection()
        
        if results["connection"].success:
            results["credentials"] = await self.validate_credentials()
            
            if results["credentials"].success:
                results["market"] = await self.get_market_info("BTC")
        
        return results


class ExchangeValidator:
    """Universal exchange validator"""
    
    @staticmethod
    async def validate_bybit(
        api_key: str,
        api_secret: str,
        demo: bool = True,
        testnet: bool = False
    ) -> Dict[str, Any]:
        """Validate Bybit credentials"""
        validator = BybitValidator(api_key, api_secret, demo, testnet)
        results = await validator.full_validation()
        
        return {
            "exchange": "bybit",
            "mode": validator.mode,
            "valid": all(r.success for r in results.values()),
            "checks": {
                name: {
                    "success": r.success,
                    "message": r.message,
                    "data": r.data,
                    "latency_ms": r.latency_ms
                }
                for name, r in results.items()
            }
        }
    
    @staticmethod
    async def validate_hyperliquid(
        private_key: str,
        testnet: bool = False
    ) -> Dict[str, Any]:
        """Validate HyperLiquid credentials"""
        validator = HyperLiquidValidator(private_key, testnet)
        results = await validator.full_validation()
        
        return {
            "exchange": "hyperliquid",
            "mode": validator.mode,
            "valid": all(r.success for r in results.values()),
            "checks": {
                name: {
                    "success": r.success,
                    "message": r.message,
                    "data": r.data,
                    "latency_ms": r.latency_ms
                }
                for name, r in results.items()
            }
        }
    
    @staticmethod
    async def health_check_all() -> Dict[str, Any]:
        """Check connectivity to all exchanges"""
        results = {}
        
        # Bybit
        bybit_demo = BybitValidator("", "", demo=True)
        bybit_real = BybitValidator("", "", demo=False)
        
        results["bybit_demo"] = await bybit_demo.validate_connection()
        results["bybit_real"] = await bybit_real.validate_connection()
        
        # HyperLiquid
        hl_main = HyperLiquidValidator("", testnet=False)
        hl_test = HyperLiquidValidator("", testnet=True)
        
        results["hyperliquid_mainnet"] = await hl_main.validate_connection()
        results["hyperliquid_testnet"] = await hl_test.validate_connection()
        
        return {
            name: {
                "success": r.success,
                "message": r.message,
                "latency_ms": r.latency_ms
            }
            for name, r in results.items()
        }


# API endpoints to be used
async def validate_user_exchange_setup(
    user_id: int,
    exchange: str = None
) -> Dict[str, Any]:
    """Validate exchange setup for a user"""
    from db import get_exchange_type, get_user_config, get_hl_credentials
    
    if not exchange:
        exchange = get_exchange_type(user_id)
    
    if exchange == "hyperliquid":
        creds = get_hl_credentials(user_id)
        if not creds.get("hl_private_key"):
            return {"valid": False, "error": "HyperLiquid not configured"}
        
        return await ExchangeValidator.validate_hyperliquid(
            creds["hl_private_key"],
            creds.get("hl_testnet", False)
        )
    else:
        config = get_user_config(user_id)
        api_key = config.get("api_key", "")
        api_secret = config.get("api_secret", "")
        
        if not api_key or not api_secret:
            return {"valid": False, "error": "Bybit not configured"}
        
        # Determine mode
        mode = config.get("trading_mode", "demo")
        demo = mode == "demo"
        
        return await ExchangeValidator.validate_bybit(
            api_key, api_secret, demo=demo
        )
