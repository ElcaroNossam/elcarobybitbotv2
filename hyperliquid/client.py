"""
HyperLiquid Async Client
"""
import asyncio
import logging
import time
import json
from typing import Dict, Any, Optional, List

import aiohttp

from .constants import (
    MAINNET_API_URL, TESTNET_API_URL,
    MAINNET_WS_URL, TESTNET_WS_URL,
    COIN_TO_ASSET, get_size_decimals, coin_to_asset_id,
)
from .signer import (
    sign_l1_action, sign_update_leverage_action,
    order_request_to_order_wire, order_wire_to_action,
    cancel_wire_to_action, float_to_wire, get_timestamp_ms,
    get_address_from_private_key,
)


logger = logging.getLogger(__name__)


def round_price(px: float, coin: str) -> float:
    """
    Round price according to HyperLiquid rules:
    - Prices can have up to 5 significant figures
    - But no more than (6 - szDecimals) decimal places for perps
    
    From official SDK (examples/rounding.py):
    round(float(f"{px:.5g}"), 6 - sz_decimals)
    """
    sz_decimals = get_size_decimals(coin)
    max_decimals = 6 - sz_decimals  # For perps, MAX_DECIMALS=6
    # First reduce to 5 significant figures, then limit decimal places
    return round(float(f"{px:.5g}"), max_decimals)


def _safe_float(val, default=0.0):
    """Safely convert value to float, handling empty strings and None"""
    if val is None or val == '':
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


class HyperLiquidError(Exception):
    def __init__(self, message: str, status_code: int = None, response: Dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class HyperLiquidClient:
    def __init__(
        self,
        private_key: Optional[str] = None,
        wallet_address: Optional[str] = None,
        testnet: bool = False,
        vault_address: Optional[str] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        # Updated init - support read-only mode with wallet_address
        self._private_key = None
        self._address = None
        
        if private_key:
            self._private_key = private_key if private_key.startswith("0x") else f"0x{private_key}"
            self._address = get_address_from_private_key(self._private_key)
        elif wallet_address:
            self._address = wallet_address.lower() if wallet_address.startswith("0x") else f"0x{wallet_address}".lower()
        
        self._testnet = testnet
        self._vault_address = vault_address
        self._session = session
        self._own_session = session is None
        self._base_url = TESTNET_API_URL if testnet else MAINNET_API_URL
        self._ws_url = TESTNET_WS_URL if testnet else MAINNET_WS_URL
        self._meta_cache: Optional[Dict] = None
        self._meta_cache_time: float = 0
        self._meta_cache_ttl: float = 60
        # Cached main wallet address (discovered from agent role)
        self._main_wallet_address: Optional[str] = None
        self._role_checked: bool = False
    
    @property
    def address(self) -> str:
        return self._address
    
    @property
    def main_wallet_address(self) -> Optional[str]:
        """Return main wallet address if this is an agent wallet"""
        return self._main_wallet_address
    
    @property
    def is_testnet(self) -> bool:
        return self._testnet
    
    async def initialize(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            self._own_session = True
    
    async def discover_main_wallet(self) -> Optional[str]:
        """
        Check if this wallet is an API agent and discover the main wallet.
        Returns main wallet address if this is an agent, None otherwise.
        
        NOTE: We do NOT auto-set vault_address anymore!
        HyperLiquid distinguishes between:
        - Vault trading (requires registered vault_address)
        - Main wallet trading (no vault_address needed)
        
        For users trading with their main wallet (most common case),
        vault_address should remain None.
        """
        if self._role_checked:
            return self._main_wallet_address
        
        self._role_checked = True
        
        try:
            await self.initialize()
            role_info = await self.get_user_role(self._address)
            
            if role_info.get("role") == "agent":
                # This is an API wallet! Get the main wallet address
                main_wallet = role_info.get("data", {}).get("user")
                if main_wallet:
                    self._main_wallet_address = main_wallet.lower()
                    logger.info(f"[HL] Discovered main wallet: {self._main_wallet_address} for agent {self._address}")
                    
                    # NOTE: We intentionally do NOT set vault_address here anymore!
                    # Users trading with main wallet don't have a registered vault.
                    # Only set vault_address if user explicitly has a vault configured.
                    # This prevents "Vault not registered" errors for normal users.
                    
                    return self._main_wallet_address
            elif role_info.get("role") == "missing":
                logger.warning(f"[HL] Wallet {self._address} is not registered as agent")
            else:
                logger.info(f"[HL] Wallet role: {role_info.get('role')} (not an agent)")
                
        except Exception as e:
            logger.warning(f"[HL] Could not discover main wallet: {e}")
        
        return None
    
    async def close(self):
        if self._session and not self._session.closed:
            try:
                await self._session.close()
                # Wait a bit for the session to fully close
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.debug(f"Error closing session: {e}")
        self._session = None
        self._own_session = False
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None, retries: int = 5) -> Dict[str, Any]:
        if self._session is None or self._session.closed:
            await self.initialize()
        
        url = f"{self._base_url}{endpoint}"
        last_error = None
        
        for attempt in range(retries):
            try:
                async with self._session.request(method, url, json=data, params=params, headers={"Content-Type": "application/json"}) as response:
                    text = await response.text()
                    
                    # Handle rate limiting with exponential backoff
                    if response.status == 429:
                        wait_time = (2 ** attempt) + 1.0  # 2s, 5s, 9s, 17s, 33s
                        logger.warning(f"HyperLiquid rate limit (429), waiting {wait_time}s (attempt {attempt + 1}/{retries})")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    if response.status >= 400:
                        logger.error(f"HyperLiquid API error: {response.status} - {text}")
                        raise HyperLiquidError(f"API error: {text}", status_code=response.status, response={"error": text})
                    if not text:
                        return {}
                    return json.loads(text)
            except aiohttp.ClientError as e:
                logger.error(f"HyperLiquid request failed: {e}")
                last_error = e
                if attempt < retries - 1:
                    await asyncio.sleep(2)  # Increased from 1s
                    continue
                raise HyperLiquidError(f"Request failed: {e}")
        
        # If we exhausted retries due to rate limiting
        raise HyperLiquidError(f"Rate limited after {retries} attempts", status_code=429)
    
    async def _info_request(self, request_type: str, **kwargs) -> Dict[str, Any]:
        data = {"type": request_type, **kwargs}
        return await self._request("POST", "/info", data=data)
    
    async def _exchange_request(self, action: Dict[str, Any]) -> Dict[str, Any]:
        nonce = get_timestamp_ms()
        signed_payload = sign_l1_action(self._private_key, action, vault_address=self._vault_address, nonce=nonce, is_mainnet=not self._testnet)
        return await self._request("POST", "/exchange", data=signed_payload)
    
    async def meta(self) -> Dict[str, Any]:
        now = time.time()
        if self._meta_cache and (now - self._meta_cache_time) < self._meta_cache_ttl:
            return self._meta_cache
        result = await self._info_request("meta")
        self._meta_cache = result
        self._meta_cache_time = now
        return result
    
    async def get_all_mids(self) -> Dict[str, float]:
        result = await self._info_request("allMids")
        return {k: _safe_float(v) for k, v in result.items()}
    
    async def get_mid_price(self, coin: str) -> Optional[float]:
        mids = await self.get_all_mids()
        return mids.get(coin)
    
    async def user_state(self, address: Optional[str] = None) -> Dict[str, Any]:
        """Get perpetual clearinghouse state (Perp balance)"""
        addr = address or self._address
        return await self._info_request("clearinghouseState", user=addr)
    
    async def spot_state(self, address: Optional[str] = None) -> Dict[str, Any]:
        """Get spot clearinghouse state (Spot balance)"""
        addr = address or self._address
        return await self._info_request("spotClearinghouseState", user=addr)
    
    async def open_orders(self, address: Optional[str] = None) -> List[Dict[str, Any]]:
        addr = address or self._address
        return await self._info_request("openOrders", user=addr)
    
    async def user_fills(self, address: Optional[str] = None, start_time: Optional[int] = None) -> List[Dict[str, Any]]:
        addr = address or self._address
        data = {"user": addr}
        if start_time:
            data["startTime"] = start_time
        return await self._info_request("userFills", **data)
    
    async def l2_snapshot(self, coin: str) -> Dict[str, Any]:
        return await self._info_request("l2Book", coin=coin)
    
    async def order(self, coin: str, is_buy: bool, sz: float, limit_px: float, reduce_only: bool = False, order_type: Optional[Dict[str, Any]] = None, cloid: Optional[str] = None, grouping: str = "na") -> Dict[str, Any]:
        if order_type is None:
            order_type = {"limit": {"tif": "Gtc"}}
        
        asset = coin_to_asset_id(coin)
        if asset is None:
            raise HyperLiquidError(f"Unknown coin: {coin}")
        
        order_req = {"coin": coin, "is_buy": is_buy, "sz": sz, "limit_px": limit_px, "reduce_only": reduce_only, "order_type": order_type}
        if cloid:
            order_req["cloid"] = cloid
        
        order_wire = order_request_to_order_wire(order_req, asset)
        action = order_wire_to_action([order_wire], grouping=grouping)
        return await self._exchange_request(action)
    
    async def market_open(self, coin: str, is_buy: bool, sz: float, slippage: float = 0.01, cloid: Optional[str] = None) -> Dict[str, Any]:
        mid_price = await self.get_mid_price(coin)
        if mid_price is None:
            raise HyperLiquidError(f"Cannot get price for {coin}")
        
        limit_px = mid_price * (1 + slippage) if is_buy else mid_price * (1 - slippage)
        limit_px = round_price(limit_px, coin)  # Fixed: use proper rounding per HyperLiquid SDK
        
        return await self.order(coin=coin, is_buy=is_buy, sz=sz, limit_px=limit_px, reduce_only=False, order_type={"limit": {"tif": "Ioc"}}, cloid=cloid)
    
    async def market_close(self, coin: str, sz: Optional[float] = None, slippage: float = 0.01, cloid: Optional[str] = None, address: Optional[str] = None) -> Dict[str, Any]:
        """
        Close position with market order.
        
        Args:
            coin: Coin symbol (ETH, BTC, etc.)
            sz: Size to close (None = close all)
            slippage: Slippage tolerance (default 1%)
            cloid: Optional client order ID
            address: Address to check positions on (for Unified Account - main wallet holds positions)
        """
        # Use provided address or default to self._address
        query_address = address or self._address
        state = await self.user_state(address=query_address)
        position = None
        
        for pos in state.get("assetPositions", []):
            pos_info = pos.get("position", {})
            if pos_info.get("coin") == coin:
                position = pos_info
                break
        
        if position is None:
            raise HyperLiquidError(f"No position found for {coin}")
        
        position_size = _safe_float(position.get("szi"))
        if position_size == 0:
            raise HyperLiquidError(f"Position size is 0 for {coin}")
        
        close_size = sz if sz is not None else abs(position_size)
        is_buy = position_size < 0
        
        mid_price = await self.get_mid_price(coin)
        if mid_price is None:
            raise HyperLiquidError(f"Cannot get price for {coin}")
        
        limit_px = mid_price * (1 + slippage) if is_buy else mid_price * (1 - slippage)
        limit_px = round_price(limit_px, coin)  # Fixed: use proper rounding per HyperLiquid SDK
        
        return await self.order(coin=coin, is_buy=is_buy, sz=close_size, limit_px=limit_px, reduce_only=True, order_type={"limit": {"tif": "Ioc"}}, cloid=cloid)
    
    async def cancel(self, coin: str, oid: int) -> Dict[str, Any]:
        asset = coin_to_asset_id(coin)
        if asset is None:
            raise HyperLiquidError(f"Unknown coin: {coin}")
        action = cancel_wire_to_action([{"a": asset, "o": oid}])
        return await self._exchange_request(action)
    
    async def cancel_all(self) -> List[Dict[str, Any]]:
        orders = await self.open_orders()
        results = []
        for order in orders:
            coin = order.get("coin")
            oid = order.get("oid")
            if coin and oid:
                try:
                    result = await self.cancel(coin, oid)
                    results.append({"coin": coin, "oid": oid, "result": result})
                except Exception as e:
                    results.append({"coin": coin, "oid": oid, "error": str(e)})
        return results
    
    async def update_leverage(self, coin: str, leverage: int, is_cross: bool = True) -> Dict[str, Any]:
        asset = coin_to_asset_id(coin)
        if asset is None:
            raise HyperLiquidError(f"Unknown coin: {coin}")
        nonce = get_timestamp_ms()
        signed_payload = sign_update_leverage_action(self._private_key, asset, is_cross, leverage, nonce=nonce, is_mainnet=not self._testnet)
        return await self._request("POST", "/exchange", data=signed_payload)
    
    async def set_tp_sl(self, coin: str, tp_price: Optional[float] = None, sl_price: Optional[float] = None, sz: Optional[float] = None, address: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Set TP/SL orders for a position.
        
        Args:
            coin: Coin symbol
            tp_price: Take profit price
            sl_price: Stop loss price
            sz: Size (None = full position)
            address: Address to check positions on (for Unified Account)
        """
        query_address = address or self._address
        state = await self.user_state(address=query_address)
        position = None
        
        for pos in state.get("assetPositions", []):
            pos_info = pos.get("position", {})
            if pos_info.get("coin") == coin:
                position = pos_info
                break
        
        if position is None:
            raise HyperLiquidError(f"No position found for {coin}")
        
        position_size = _safe_float(position.get("szi"))
        if position_size == 0:
            raise HyperLiquidError(f"Position size is 0 for {coin}")
        
        order_size = sz if sz is not None else abs(position_size)
        is_long = position_size > 0
        results = []
        
        if tp_price is not None:
            tp_price_rounded = round_price(tp_price, coin)  # Fixed: proper price rounding
            tp_result = await self.order(coin=coin, is_buy=not is_long, sz=order_size, limit_px=tp_price_rounded, reduce_only=True, order_type={"trigger": {"isMarket": True, "triggerPx": tp_price_rounded, "tpsl": "tp"}})
            results.append({"type": "tp", "result": tp_result})
        
        if sl_price is not None:
            sl_price_rounded = round_price(sl_price, coin)  # Fixed: proper price rounding
            sl_result = await self.order(coin=coin, is_buy=not is_long, sz=order_size, limit_px=sl_price_rounded, reduce_only=True, order_type={"trigger": {"isMarket": True, "triggerPx": sl_price_rounded, "tpsl": "sl"}})
            results.append({"type": "sl", "result": sl_result})
        
        return results
    
    async def get_position(self, coin: str) -> Optional[Dict[str, Any]]:
        state = await self.user_state()
        for pos in state.get("assetPositions", []):
            pos_info = pos.get("position", {})
            if pos_info.get("coin") == coin:
                return pos_info
        return None
    
    async def get_all_positions(self) -> List[Dict[str, Any]]:
        state = await self.user_state()
        positions = []
        for pos in state.get("assetPositions", []):
            pos_info = pos.get("position", {})
            if _safe_float(pos_info.get("szi")) != 0:
                positions.append(pos_info)
        return positions
    
    async def get_balance(self) -> Dict[str, float]:
        state = await self.user_state()
        margin = state.get("marginSummary", {})
        return {
            "account_value": _safe_float(margin.get("accountValue")),
            "total_margin_used": _safe_float(margin.get("totalMarginUsed")),
            "total_ntl_pos": _safe_float(margin.get("totalNtlPos")),
            "withdrawable": _safe_float(state.get("withdrawable")),
        }
    
    async def get_unrealized_pnl(self) -> float:
        positions = await self.get_all_positions()
        total_pnl = 0.0
        for pos in positions:
            pnl = _safe_float(pos.get("unrealizedPnl"))
            total_pnl += pnl
        return total_pnl

    # ==================== NEW ADVANCED FEATURES ====================

    async def get_candles(
        self, 
        coin: str, 
        interval: str = "1h", 
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get OHLCV candle data for a coin.
        Intervals: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 8h, 12h, 1d, 3d, 1w, 1M
        Returns up to 5000 candles.
        """
        import time
        # candleSnapshot requires: req { coin, interval, startTime, endTime }
        now = int(time.time() * 1000)
        data = {
            "req": {
                "coin": coin, 
                "interval": interval,
                "startTime": start_time or (now - 24 * 60 * 60 * 1000),  # default 24h ago
                "endTime": end_time or now
            }
        }
        return await self._info_request("candleSnapshot", **data)
    
    async def get_historical_orders(
        self, 
        address: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get historical orders (up to 2000)"""
        addr = address or self._address
        return await self._info_request("historicalOrders", user=addr)
    
    async def get_order_status(
        self, 
        oid: Optional[int] = None,
        cloid: Optional[str] = None
    ) -> Dict[str, Any]:
        """Query order status by oid or cloid"""
        data = {"user": self._address}
        if oid:
            data["oid"] = oid
        elif cloid:
            data["cloid"] = cloid
        else:
            raise HyperLiquidError("Either oid or cloid must be provided")
        return await self._info_request("orderStatus", **data)
    
    async def get_rate_limits(self, address: Optional[str] = None) -> Dict[str, Any]:
        """Query user rate limits"""
        addr = address or self._address
        return await self._info_request("userRateLimit", user=addr)
    
    async def get_user_fees(self, address: Optional[str] = None) -> Dict[str, Any]:
        """Query user fee rates and schedule"""
        addr = address or self._address
        return await self._info_request("userFees", user=addr)
    
    async def get_portfolio(self, address: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user portfolio with PnL history"""
        addr = address or self._address
        return await self._info_request("portfolio", user=addr)
    
    async def get_referral_info(self, address: Optional[str] = None) -> Dict[str, Any]:
        """Get user referral information"""
        addr = address or self._address
        return await self._info_request("referral", user=addr)
    
    async def get_subaccounts(self, address: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user's subaccounts"""
        addr = address or self._address
        return await self._info_request("subAccounts", user=addr)
    
    async def get_user_role(self, address: Optional[str] = None) -> Dict[str, Any]:
        """Query user role (user, agent, vault, subAccount)"""
        addr = address or self._address
        return await self._info_request("userRole", user=addr)
    
    async def get_vault_details(self, vault_address: str) -> Dict[str, Any]:
        """Get vault details"""
        return await self._info_request("vaultDetails", vaultAddress=vault_address)
    
    async def get_funding_history(
        self, 
        coin: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get funding rate history for a coin"""
        import time as time_module
        now = int(time_module.time() * 1000)
        
        # fundingHistory format: { type, coin, startTime }
        data = {
            "coin": coin,
            "startTime": start_time or (now - 7 * 24 * 60 * 60 * 1000),  # default 7 days ago
        }
        if end_time:
            data["endTime"] = end_time
        return await self._info_request("fundingHistory", **data)
    
    async def get_predicted_funding(self, coin: str) -> Dict[str, Any]:
        """Get predicted funding rate for next period"""
        meta = await self.meta()
        universe = meta.get("universe", [])
        for asset in universe:
            if asset.get("name") == coin:
                funding = asset.get("funding")
                return {
                    "coin": coin,
                    "funding_rate": funding,
                    "next_funding": asset.get("nextFunding")
                }
        return {}
    
    async def modify_order(
        self,
        oid: int,
        coin: str,
        is_buy: bool,
        sz: float,
        limit_px: float,
        reduce_only: bool = False,
        order_type: Optional[Dict[str, Any]] = None,
        cloid: Optional[str] = None
    ) -> Dict[str, Any]:
        """Modify an existing order"""
        if order_type is None:
            order_type = {"limit": {"tif": "Gtc"}}
        
        asset = coin_to_asset_id(coin)
        if asset is None:
            raise HyperLiquidError(f"Unknown coin: {coin}")
        
        order_req = {
            "coin": coin, 
            "is_buy": is_buy, 
            "sz": sz, 
            "limit_px": limit_px, 
            "reduce_only": reduce_only, 
            "order_type": order_type
        }
        if cloid:
            order_req["cloid"] = cloid
        
        order_wire = order_request_to_order_wire(order_req, asset)
        order_wire["oid"] = oid
        
        action = {
            "type": "batchModify",
            "modifies": [order_wire]
        }
        return await self._exchange_request(action)
    
    async def schedule_cancel(self, time_ms: Optional[int] = None) -> Dict[str, Any]:
        """
        Schedule a cancel-all operation (dead man's switch).
        time_ms must be at least 5 seconds in future.
        Pass None to remove scheduled cancel.
        """
        action = {
            "type": "scheduleCancel",
            "time": time_ms
        }
        return await self._exchange_request(action)
    
    async def transfer_usdc(
        self,
        destination: str,
        amount: float
    ) -> Dict[str, Any]:
        """Transfer USDC to another address on L1"""
        nonce = get_timestamp_ms()
        
        # This requires a special signature format
        action = {
            "type": "usdSend",
            "hyperliquidChain": "Mainnet" if not self._testnet else "Testnet",
            "signatureChainId": "0xa4b1" if not self._testnet else "0x66eee",
            "destination": destination,
            "amount": str(amount),
            "time": nonce
        }
        return await self._exchange_request(action)
    
    async def spot_transfer(self, usd_to_perp: bool, usd_amount: float) -> Dict[str, Any]:
        """Transfer USDC between spot and perp accounts"""
        action = {
            "type": "spotUser",
            "classTransfer": {
                "usdc": float_to_wire(usd_amount),
                "toPerp": usd_to_perp
            }
        }
        return await self._exchange_request(action)
    
    async def update_isolated_margin(
        self,
        coin: str,
        is_buy: bool,
        margin_change: float
    ) -> Dict[str, Any]:
        """Add or remove margin from isolated position"""
        asset = coin_to_asset_id(coin)
        if asset is None:
            raise HyperLiquidError(f"Unknown coin: {coin}")
        
        action = {
            "type": "updateIsolatedMargin",
            "asset": asset,
            "isBuy": is_buy,
            "ntli": margin_change
        }
        return await self._exchange_request(action)
    
    async def place_twap_order(
        self,
        coin: str,
        is_buy: bool,
        sz: float,
        reduce_only: bool = False,
        duration_minutes: int = 60,
        randomize: bool = False
    ) -> Dict[str, Any]:
        """
        Place a TWAP (Time Weighted Average Price) order.
        Splits order into smaller pieces over duration.
        """
        asset = coin_to_asset_id(coin)
        if asset is None:
            raise HyperLiquidError(f"Unknown coin: {coin}")
        
        action = {
            "type": "twapOrder",
            "twap": {
                "a": asset,
                "b": is_buy,
                "s": float_to_wire(sz),
                "r": reduce_only,
                "m": duration_minutes,
                "t": randomize
            }
        }
        return await self._exchange_request(action)
    
    async def cancel_twap(self, twap_id: int) -> Dict[str, Any]:
        """Cancel a TWAP order"""
        action = {
            "type": "twapCancel",
            "a": twap_id
        }
        return await self._exchange_request(action)
    
    async def get_all_coins_info(self) -> List[Dict[str, Any]]:
        """Get detailed info for all coins including funding rates"""
        meta = await self.meta()
        mids = await self.get_all_mids()
        
        result = []
        for asset in meta.get("universe", []):
            coin = asset.get("name")
            result.append({
                "coin": coin,
                "price": mids.get(coin, 0),
                "maxLeverage": asset.get("maxLeverage"),
                "funding": asset.get("funding"),
                "openInterest": asset.get("openInterest"),
                "prevDayPx": asset.get("prevDayPx"),
                "dayNtlVlm": asset.get("dayNtlVlm"),
            })
        return result
    
    async def get_ticker(self, coin: str) -> Optional[Dict[str, Any]]:
        """Get ticker info for a coin (alias for compatibility)"""
        meta = await self.meta()
        mid = await self.get_mid_price(coin)
        
        for asset in meta.get("universe", []):
            if asset.get("name") == coin:
                prev_price = _safe_float(asset.get("prevDayPx")) or mid or 0
                change_24h = ((mid - prev_price) / prev_price * 100) if prev_price else 0
                
                return {
                    "symbol": f"{coin}USDC",
                    "price": mid,
                    "change_24h": round(change_24h, 2),
                    "volume_24h": _safe_float(asset.get("dayNtlVlm")),
                    "funding_rate": asset.get("funding"),
                    "open_interest": asset.get("openInterest"),
                    "max_leverage": asset.get("maxLeverage"),
                }
        return None
    
    async def get_orderbook(self, coin: str, depth: int = 20) -> Dict[str, Any]:
        """Get L2 orderbook snapshot"""
        result = await self.l2_snapshot(coin)
        levels = result.get("levels", [[], []])
        
        bids = []
        asks = []
        
        if len(levels) >= 2:
            for bid in levels[0][:depth]:
                bids.append([_safe_float(bid.get("px")), _safe_float(bid.get("sz"))])
            for ask in levels[1][:depth]:
                asks.append([_safe_float(ask.get("px")), _safe_float(ask.get("sz"))])
        
        return {
            "coin": coin,
            "bids": bids,
            "asks": asks,
            "timestamp": result.get("time", 0)
        }
    
    async def get_all_symbols(self) -> List[str]:
        """Get list of all tradable symbols"""
        meta = await self.meta()
        return [asset.get("name") for asset in meta.get("universe", [])]

    # ==================== SPOT TRADING ====================
    
    async def spot_meta(self) -> Dict[str, Any]:
        """
        Get spot metadata including all spot pairs and their indices.
        Spot asset IDs are calculated as: 10000 + index in universe array.
        
        Returns:
            Dict with:
            - universe: List of spot pairs with tokens info
            - tokens: List of all spot tokens
        """
        return await self._info_request("spotMeta")
    
    async def spot_meta_and_asset_contexts(self) -> List[Any]:
        """
        Get spot metadata with asset context in a single request.
        Returns [spotMeta, spotAssetCtxs] where spotAssetCtxs has price info.
        """
        return await self._info_request("spotMetaAndAssetCtxs")
    
    async def get_spot_pairs(self) -> List[Dict[str, Any]]:
        """
        Get list of all spot pairs with their asset IDs.
        
        Returns:
            List of dicts with: name, tokens (base/quote), asset_id (10000 + index)
        """
        spot_meta = await self.spot_meta()
        universe = spot_meta.get("universe", [])
        tokens = spot_meta.get("tokens", [])
        
        pairs = []
        for idx, pair in enumerate(universe):
            # Spot asset ID = 10000 + index
            asset_id = 10000 + idx
            
            # Get token indices
            token_indices = pair.get("tokens", [])
            base_idx = token_indices[0] if len(token_indices) > 0 else None
            quote_idx = token_indices[1] if len(token_indices) > 1 else None
            
            # Get token names
            base_token = tokens[base_idx].get("name") if base_idx is not None and base_idx < len(tokens) else "?"
            quote_token = tokens[quote_idx].get("name") if quote_idx is not None and quote_idx < len(tokens) else "USDC"
            
            pairs.append({
                "name": pair.get("name", f"{base_token}/{quote_token}"),
                "base_token": base_token,
                "quote_token": quote_token,
                "asset_id": asset_id,
                "index": idx,
            })
        
        return pairs
    
    async def get_spot_asset_id(self, base_token: str) -> Optional[int]:
        """
        Get spot asset ID for a token (e.g., "PURR" -> 10000).
        
        Args:
            base_token: Base token name (e.g., "PURR", "HYPE")
            
        Returns:
            Asset ID (10000 + index) or None if not found
        """
        pairs = await self.get_spot_pairs()
        for pair in pairs:
            if pair["base_token"].upper() == base_token.upper():
                return pair["asset_id"]
        return None
    
    async def spot_order(
        self,
        base_token: str,
        is_buy: bool,
        sz: float,
        limit_px: float,
        reduce_only: bool = False,
        order_type: Optional[Dict[str, Any]] = None,
        cloid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Place a spot order.
        
        Args:
            base_token: Base token name (e.g., "PURR", "HYPE")
            is_buy: True for buy, False for sell
            sz: Size in base token
            limit_px: Limit price in quote token (usually USDC)
            reduce_only: Whether this is a reduce-only order
            order_type: Order type dict (default: limit GTC)
            cloid: Optional client order ID
            
        Returns:
            Order result dict
        """
        if order_type is None:
            order_type = {"limit": {"tif": "Gtc"}}
        
        # Get spot asset ID
        asset_id = await self.get_spot_asset_id(base_token)
        if asset_id is None:
            raise HyperLiquidError(f"Unknown spot token: {base_token}")
        
        # Build order request - same format as perps but with spot asset ID
        order_req = {
            "coin": base_token,
            "is_buy": is_buy,
            "sz": sz,
            "limit_px": limit_px,
            "reduce_only": reduce_only,
            "order_type": order_type
        }
        if cloid:
            order_req["cloid"] = cloid
        
        order_wire = order_request_to_order_wire(order_req, asset_id)
        action = order_wire_to_action([order_wire], grouping="na")
        
        return await self._exchange_request(action)
    
    async def spot_market_buy(
        self,
        base_token: str,
        sz: float,
        slippage: float = 0.02,
        cloid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Place a spot market buy order.
        
        Args:
            base_token: Token to buy (e.g., "PURR", "HYPE")
            sz: Size in base token
            slippage: Slippage tolerance (default 2% for spot)
            cloid: Optional client order ID
            
        Returns:
            Order result dict
        """
        # Get spot prices
        spot_data = await self.spot_meta_and_asset_contexts()
        if len(spot_data) < 2:
            raise HyperLiquidError("Failed to get spot prices")
        
        spot_meta = spot_data[0]
        spot_ctxs = spot_data[1]
        universe = spot_meta.get("universe", [])
        
        # Find the pair and get mid price
        mid_price = None
        asset_id = None
        for idx, pair in enumerate(universe):
            tokens = spot_meta.get("tokens", [])
            token_indices = pair.get("tokens", [])
            base_idx = token_indices[0] if len(token_indices) > 0 else None
            base_name = tokens[base_idx].get("name") if base_idx is not None and base_idx < len(tokens) else None
            
            if base_name and base_name.upper() == base_token.upper():
                asset_id = 10000 + idx
                if idx < len(spot_ctxs):
                    mid_price = _safe_float(spot_ctxs[idx].get("midPx"))
                break
        
        if mid_price is None or mid_price == 0:
            raise HyperLiquidError(f"Cannot get price for spot token: {base_token}")
        
        # Apply slippage
        limit_px = mid_price * (1 + slippage)
        limit_px = round(limit_px, 5)  # Spot prices typically 5 decimals
        
        return await self.spot_order(
            base_token=base_token,
            is_buy=True,
            sz=sz,
            limit_px=limit_px,
            order_type={"limit": {"tif": "Ioc"}},  # IOC for market orders
            cloid=cloid
        )
    
    async def spot_market_sell(
        self,
        base_token: str,
        sz: float,
        slippage: float = 0.02,
        cloid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Place a spot market sell order.
        
        Args:
            base_token: Token to sell (e.g., "PURR", "HYPE")
            sz: Size in base token
            slippage: Slippage tolerance (default 2% for spot)
            cloid: Optional client order ID
            
        Returns:
            Order result dict
        """
        # Get spot prices
        spot_data = await self.spot_meta_and_asset_contexts()
        if len(spot_data) < 2:
            raise HyperLiquidError("Failed to get spot prices")
        
        spot_meta = spot_data[0]
        spot_ctxs = spot_data[1]
        universe = spot_meta.get("universe", [])
        
        # Find the pair and get mid price
        mid_price = None
        for idx, pair in enumerate(universe):
            tokens = spot_meta.get("tokens", [])
            token_indices = pair.get("tokens", [])
            base_idx = token_indices[0] if len(token_indices) > 0 else None
            base_name = tokens[base_idx].get("name") if base_idx is not None and base_idx < len(tokens) else None
            
            if base_name and base_name.upper() == base_token.upper():
                if idx < len(spot_ctxs):
                    mid_price = _safe_float(spot_ctxs[idx].get("midPx"))
                break
        
        if mid_price is None or mid_price == 0:
            raise HyperLiquidError(f"Cannot get price for spot token: {base_token}")
        
        # Apply slippage
        limit_px = mid_price * (1 - slippage)
        limit_px = round(limit_px, 5)  # Spot prices typically 5 decimals
        
        return await self.spot_order(
            base_token=base_token,
            is_buy=False,
            sz=sz,
            limit_px=limit_px,
            order_type={"limit": {"tif": "Ioc"}},  # IOC for market orders
            cloid=cloid
        )
    
    async def get_spot_ticker(self, base_token: str) -> Optional[Dict[str, Any]]:
        """
        Get spot ticker info for a token.
        
        Args:
            base_token: Token name (e.g., "PURR", "HYPE")
            
        Returns:
            Dict with price, volume, etc.
        """
        spot_data = await self.spot_meta_and_asset_contexts()
        if len(spot_data) < 2:
            return None
        
        spot_meta = spot_data[0]
        spot_ctxs = spot_data[1]
        universe = spot_meta.get("universe", [])
        tokens = spot_meta.get("tokens", [])
        
        for idx, pair in enumerate(universe):
            token_indices = pair.get("tokens", [])
            base_idx = token_indices[0] if len(token_indices) > 0 else None
            base_name = tokens[base_idx].get("name") if base_idx is not None and base_idx < len(tokens) else None
            
            if base_name and base_name.upper() == base_token.upper():
                ctx = spot_ctxs[idx] if idx < len(spot_ctxs) else {}
                
                mid_px = _safe_float(ctx.get("midPx"))
                prev_day_px = _safe_float(ctx.get("prevDayPx")) or mid_px or 0
                change_24h = ((mid_px - prev_day_px) / prev_day_px * 100) if prev_day_px else 0
                
                return {
                    "symbol": f"{base_name}/USDC",
                    "base_token": base_name,
                    "price": mid_px,
                    "prevDayPx": prev_day_px,
                    "change_24h": round(change_24h, 2),
                    "dayNtlVlm": _safe_float(ctx.get("dayNtlVlm")),
                    "markPx": _safe_float(ctx.get("markPx")),
                    "circSupply": _safe_float(ctx.get("circSupply")),
                }
        return None
    
    async def get_all_spot_tickers(self) -> List[Dict[str, Any]]:
        """
        Get ticker info for all spot pairs.
        
        Returns:
            List of ticker dicts
        """
        spot_data = await self.spot_meta_and_asset_contexts()
        if len(spot_data) < 2:
            return []
        
        spot_meta = spot_data[0]
        spot_ctxs = spot_data[1]
        universe = spot_meta.get("universe", [])
        tokens = spot_meta.get("tokens", [])
        
        tickers = []
        for idx, pair in enumerate(universe):
            token_indices = pair.get("tokens", [])
            base_idx = token_indices[0] if len(token_indices) > 0 else None
            base_name = tokens[base_idx].get("name") if base_idx is not None and base_idx < len(tokens) else "?"
            
            ctx = spot_ctxs[idx] if idx < len(spot_ctxs) else {}
            mid_px = _safe_float(ctx.get("midPx"))
            prev_day_px = _safe_float(ctx.get("prevDayPx")) or mid_px or 0
            change_24h = ((mid_px - prev_day_px) / prev_day_px * 100) if prev_day_px else 0
            
            tickers.append({
                "symbol": f"{base_name}/USDC",
                "base_token": base_name,
                "asset_id": 10000 + idx,
                "price": mid_px,
                "change_24h": round(change_24h, 2),
                "dayNtlVlm": _safe_float(ctx.get("dayNtlVlm")),
            })
        
        return tickers
